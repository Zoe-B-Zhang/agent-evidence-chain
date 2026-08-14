"""Output guardrails (M3)."""

from __future__ import annotations

import re


def formal_tone_score(text: str) -> float:
    if not text:
        return 0.0
    penalties = len(re.findall(r"!+", text)) * 0.15
    hype = len(re.findall(r"\b(amazing|exciting|awesome)\b", text, re.I)) * 0.2
    return max(0.0, min(1.0, 0.9 - penalties - hype))


def check_formality(text: str, min_score: float) -> tuple[bool, float, str]:
    score = formal_tone_score(text)
    if score >= min_score:
        return True, score, "ok"
    return False, score, f"formality {score:.2f} < {min_score}"
