"""
F13 (ETAP 29) — SeniorAudioPreprocessor (DSP) + adaptive VAD.

Kontekst: seniorzy często mówią cicho, drżącym głosem, z długimi pauzami i
w otoczeniu z szumem (TV, radio). Standardowy VAD ucina zdania w połowie i
kończy nagranie zanim senior dokończy myśl. Ten moduł:

  1. SeniorAudioPreprocessor — lekki, deterministyczny łańcuch DSP na ramkach
     audio (RMS/energia): bramka szumu (noise gate), automatyczna regulacja
     wzmocnienia (AGC do docelowego poziomu), miękki limiter. Operuje na
     wartościach ramek (float PCM znormalizowany [-1,1]) — bez zależności od
     bibliotek natywnych, żeby działać przenośnie (edge/portable).

  2. AdaptiveVAD — detekcja mowy z progiem adaptującym się do tła oraz
     WYDŁUŻONYM oknem ciszy końcowej dla seniorów (hangover), tak by nie ucinać
     wolnej wypowiedzi. Kalibruje próg z pierwszych ramek (szum tła).

Wszystko deterministyczne i audytowalne (AI Act): brak losowości, jawne progi.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Pomocnicze: energia/RMS ramki
# ---------------------------------------------------------------------------
def frame_rms(frame: list[float]) -> float:
    """Pierwiastek średniej kwadratów (RMS) ramki PCM float [-1, 1]."""
    if not frame:
        return 0.0
    return math.sqrt(sum(x * x for x in frame) / len(frame))


def rms_to_dbfs(rms: float) -> float:
    """RMS → dBFS (0 dBFS = pełna skala). Cisza ≈ -100 dBFS."""
    if rms <= 1e-9:
        return -100.0
    return 20.0 * math.log10(rms)


# ---------------------------------------------------------------------------
# DSP — łańcuch przetwarzania na ramce
# ---------------------------------------------------------------------------
@dataclass
class PreprocessorConfig:
    noise_gate_dbfs: float = -55.0     # poniżej — traktuj jako szum → wycisz
    target_dbfs: float = -20.0         # docelowy poziom po AGC
    max_gain_db: float = 18.0          # limit wzmocnienia (nie podbijaj szumu w nieskończoność)
    limiter_ceiling: float = 0.98      # miękki sufit amplitudy
    agc_attack: float = 0.4            # jak szybko AGC podąża w górę (0..1)
    agc_release: float = 0.1           # jak szybko schodzi w dół


@dataclass
class FrameStats:
    in_dbfs: float
    out_dbfs: float
    applied_gain_db: float
    gated: bool
    clipped: bool


class SeniorAudioPreprocessor:
    """Deterministyczny łańcuch DSP: noise gate → AGC → limiter.

    Utrzymuje stan wygładzonego wzmocnienia między ramkami (płynne AGC).
    """

    def __init__(self, config: PreprocessorConfig | None = None):
        self.cfg = config or PreprocessorConfig()
        self._smoothed_gain_db = 0.0
        self.frames_processed = 0
        self.frames_gated = 0

    def _agc_gain_db(self, in_dbfs: float) -> float:
        if in_dbfs <= -99.0:
            desired = 0.0
        else:
            desired = self.cfg.target_dbfs - in_dbfs
        desired = max(0.0, min(self.cfg.max_gain_db, desired))
        # wygładzenie: attack gdy rośnie, release gdy maleje
        if desired > self._smoothed_gain_db:
            coeff = self.cfg.agc_attack
        else:
            coeff = self.cfg.agc_release
        self._smoothed_gain_db += (desired - self._smoothed_gain_db) * coeff
        return self._smoothed_gain_db

    def process_frame(self, frame: list[float]) -> tuple[list[float], FrameStats]:
        self.frames_processed += 1
        in_rms = frame_rms(frame)
        in_dbfs = rms_to_dbfs(in_rms)

        # 1) noise gate
        if in_dbfs < self.cfg.noise_gate_dbfs:
            self.frames_gated += 1
            out = [0.0] * len(frame)
            return out, FrameStats(in_dbfs, -100.0, 0.0, gated=True, clipped=False)

        # 2) AGC
        gain_db = self._agc_gain_db(in_dbfs)
        gain_lin = 10.0 ** (gain_db / 20.0)
        amplified = [x * gain_lin for x in frame]

        # 3) miękki limiter (tanh soft-clip powyżej sufitu)
        ceiling = self.cfg.limiter_ceiling
        clipped = False
        out = []
        for x in amplified:
            if abs(x) > ceiling:
                clipped = True
                x = math.copysign(ceiling + (1 - ceiling) * math.tanh((abs(x) - ceiling) / (1 - ceiling)), x)
            out.append(x)

        out_dbfs = rms_to_dbfs(frame_rms(out))
        return out, FrameStats(in_dbfs, out_dbfs, gain_db, gated=False, clipped=clipped)

    def process(self, frames: list[list[float]]) -> tuple[list[list[float]], list[FrameStats]]:
        outs, stats = [], []
        for fr in frames:
            o, st = self.process_frame(fr)
            outs.append(o)
            stats.append(st)
        return outs, stats


# ---------------------------------------------------------------------------
# Adaptive VAD
# ---------------------------------------------------------------------------
class VADState(str, Enum):
    silence = "silence"
    speech = "speech"


@dataclass
class VADConfig:
    calibration_frames: int = 5        # ile pierwszych ramek to pomiar tła
    margin_db: float = 8.0             # próg = tło + margines
    min_threshold_dbfs: float = -50.0  # dolna granica progu (nie schodź poniżej)
    start_frames: int = 2              # ramki powyżej progu → START mowy
    # HANGOVER senioralny: długie okno ciszy końcowej, by nie ucinać wolnej mowy
    hangover_frames: int = 12          # ~ przy 100ms/ramce = 1.2 s ciszy końcowej


@dataclass
class VADResult:
    state: VADState
    speech_frames: int
    threshold_dbfs: float
    segments: list[tuple[int, int]] = field(default_factory=list)  # (start, end) w indeksach ramek


class AdaptiveVAD:
    """VAD z progiem adaptacyjnym do tła i wydłużonym hangoverem dla seniorów."""

    def __init__(self, config: VADConfig | None = None):
        self.cfg = config or VADConfig()
        self._bg_samples: list[float] = []
        self.threshold_dbfs: float | None = None

    def _calibrate(self, dbfs: float):
        self._bg_samples.append(dbfs)
        if len(self._bg_samples) >= self.cfg.calibration_frames:
            bg = sum(self._bg_samples) / len(self._bg_samples)
            self.threshold_dbfs = max(
                self.cfg.min_threshold_dbfs, bg + self.cfg.margin_db
            )

    def run(self, frames: list[list[float]]) -> VADResult:
        """Zwraca segmenty mowy z adaptacyjnym progiem i senioralnym hangoverem."""
        segments: list[tuple[int, int]] = []
        state = VADState.silence
        speech_count = 0
        above_run = 0       # ile ramek z rzędu powyżej progu
        silence_run = 0     # ile ramek ciszy w trakcie mowy (do hangover)
        seg_start = 0

        for i, fr in enumerate(frames):
            dbfs = rms_to_dbfs(frame_rms(fr))

            if self.threshold_dbfs is None:
                self._calibrate(dbfs)
                # w trakcie kalibracji nie wykrywamy mowy
                thr = self.cfg.min_threshold_dbfs
            else:
                thr = self.threshold_dbfs

            is_loud = dbfs >= thr

            if state == VADState.silence:
                if is_loud:
                    above_run += 1
                    if above_run >= self.cfg.start_frames:
                        state = VADState.speech
                        seg_start = i - above_run + 1
                        speech_count += above_run
                        silence_run = 0
                else:
                    above_run = 0
            else:  # speech
                if is_loud:
                    speech_count += 1
                    silence_run = 0
                else:
                    silence_run += 1
                    # hangover: dopiero po długim oknie ciszy kończymy segment
                    if silence_run >= self.cfg.hangover_frames:
                        seg_end = i - silence_run
                        segments.append((seg_start, max(seg_start, seg_end)))
                        state = VADState.silence
                        above_run = 0

        # domknij segment na końcu strumienia
        if state == VADState.speech:
            segments.append((seg_start, len(frames) - 1))

        return VADResult(
            state=state,
            speech_frames=speech_count,
            threshold_dbfs=self.threshold_dbfs if self.threshold_dbfs is not None
            else self.cfg.min_threshold_dbfs,
            segments=segments,
        )
