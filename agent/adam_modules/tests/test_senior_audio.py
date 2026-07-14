"""Testy F13 (ETAP 29) — DSP preprocessor, adaptive VAD, słownik wielkopolski."""
from __future__ import annotations

import math

from adam_modules.speech import (
    SeniorAudioPreprocessor, PreprocessorConfig,
    AdaptiveVAD, VADConfig, VADState,
    normalize_regional, dictionary_size,
    frame_rms, rms_to_dbfs,
)
from adam_modules.semaphore.detector import CrisisDetector


# ---- helpers ----
def _sine(amp: float, n: int = 160, freq: float = 0.05) -> list[float]:
    return [amp * math.sin(2 * math.pi * freq * i) for i in range(n)]


def _silence(n: int = 160) -> list[float]:
    return [0.0] * n


# ---- słownik wielkopolski ----
def test_dictionary_has_enough_terms():
    # cel ~380 terminów
    assert dictionary_size() >= 380


def test_normalize_regional_maps_dialect():
    r = normalize_regional("Ino ździebko pyr ugotowałam, tej.")
    assert "tylko" in r.normalized
    assert "trochę" in r.normalized
    assert r.changed
    assert r.hit_count >= 3


def test_normalize_preserves_original():
    r = normalize_regional("laczki mi zginęły")
    assert r.original == "laczki mi zginęły"
    assert "kapcie" in r.normalized


def test_regional_crisis_phrase_normalized():
    r = normalize_regional("nie mogę dychać i serce mi wali jak młot")
    assert "nie mogę oddychać" in r.normalized
    assert "kołatanie serca" in r.normalized


def test_detector_regional_catches_dialect_crisis():
    plain = CrisisDetector(regional=False)
    reg = CrisisDetector(regional=True)
    text = "nie mogę dychać"
    # bez normalizacji regionalnej gwara może nie trafić w regułę;
    # z normalizacją "nie mogę oddychać" musi zostać wykryte
    reg_hits = reg.detect_text(text)
    assert any(d.level.value in ("red", "purple") for d in reg_hits)


# ---- DSP preprocessor ----
def test_preprocessor_gates_silence():
    pre = SeniorAudioPreprocessor()
    out, stats = pre.process_frame(_silence())
    assert stats.gated is True
    assert all(x == 0.0 for x in out)


def test_preprocessor_boosts_quiet_speech():
    # cichy sygnał → AGC powinno podbić poziom
    pre = SeniorAudioPreprocessor(PreprocessorConfig(target_dbfs=-20.0))
    quiet = _sine(0.02)
    in_db = rms_to_dbfs(frame_rms(quiet))
    # wiele ramek, by AGC się rozpędziło
    last = None
    for _ in range(10):
        out, last = pre.process_frame(_sine(0.02))
    assert last.applied_gain_db > 0
    assert last.out_dbfs > in_db


def test_preprocessor_limiter_prevents_clipping():
    pre = SeniorAudioPreprocessor(PreprocessorConfig(limiter_ceiling=0.9, max_gain_db=30))
    loud = _sine(0.9)
    for _ in range(5):
        out, st = pre.process_frame(_sine(0.9))
    assert max(abs(x) for x in out) <= 1.0


# ---- adaptive VAD ----
def test_vad_calibrates_and_detects_speech():
    vad = AdaptiveVAD(VADConfig(calibration_frames=3, hangover_frames=3))
    # 3 ramki tła (cisza) + mowa + cisza
    frames = [_silence() for _ in range(3)]
    frames += [_sine(0.3) for _ in range(6)]
    frames += [_silence() for _ in range(6)]
    res = vad.run(frames)
    assert res.speech_frames > 0
    assert len(res.segments) >= 1


def test_vad_hangover_keeps_slow_speech_together():
    # senior robi krótką pauzę w środku wypowiedzi — hangover NIE powinien ciąć
    vad = AdaptiveVAD(VADConfig(calibration_frames=2, hangover_frames=5))
    frames = [_silence() for _ in range(2)]
    frames += [_sine(0.3) for _ in range(4)]
    frames += [_silence() for _ in range(3)]   # krótka pauza < hangover
    frames += [_sine(0.3) for _ in range(4)]
    frames += [_silence() for _ in range(6)]   # dłuższa cisza > hangover
    res = vad.run(frames)
    # jedna spójna wypowiedź mimo pauzy
    assert len(res.segments) == 1


def test_vad_threshold_adapts_to_noise_floor():
    quiet = AdaptiveVAD(VADConfig(calibration_frames=3, margin_db=8))
    quiet.run([_silence() for _ in range(3)])
    assert quiet.threshold_dbfs is not None
    assert quiet.threshold_dbfs <= -40  # przy ciszy próg blisko dolnej granicy
