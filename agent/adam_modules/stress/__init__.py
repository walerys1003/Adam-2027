"""
F17 (ETAP 31) — testy stresowe / red-team dla Adama.

SeniorSimulator „gra" seniora (persony: spokojny/samotny/kryzys/zdezorientowany/
manipulator/hipochondryk) w rozmowie z DialogEngine, umożliwiając powtarzalne,
bezaudiowe testy odporności: eskalacja kryzysu, blokada prompt-injection (F4),
blokada halucynacji medycznych (dawki/diagnozy/obietnice).
"""
from .simulator import (
    SeniorSimulator, Persona, ScenarioReport, SimTurn, HallucinatingLLM,
)

__all__ = ["SeniorSimulator", "Persona", "ScenarioReport", "SimTurn", "HallucinatingLLM"]
