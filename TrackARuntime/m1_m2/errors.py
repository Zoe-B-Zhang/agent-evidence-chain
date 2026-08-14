"""Failure classification for agent runtime (M1-K05)."""

from __future__ import annotations

from enum import Enum


class ErrorClass(str, Enum):
    RECOVERABLE = "recoverable"
    RETRYABLE = "retryable"
    FATAL = "fatal"
    STALLED = "stalled"
    UNKNOWN = "unknown"


class FatalAgentError(Exception):
    """Unrecoverable state — stop loop and persist trajectory (maps to mini-swe-agent #803)."""

    def __init__(self, message: str, error_class: ErrorClass = ErrorClass.FATAL) -> None:
        super().__init__(message)
        self.error_class = error_class
