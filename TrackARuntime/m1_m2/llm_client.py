"""Pluggable LLM client for the Agent loop (D1)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanContext:
    """Inputs an LLM client needs to produce a plan."""

    task: str
    observation: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)
    round: int = 0
    pseudo_replan: bool = False
    model: str = "mock-small"
    context_prompt: str = ""


class LLMClient(ABC):
    """Abstract LLM client.

    Implementations can call OpenAI / Anthropic / local models.
    The default `MockLLMClient` preserves the original deterministic demo behavior.
    """

    @abstractmethod
    def generate_plan(self, ctx: PlanContext) -> str:
        """Return the next plan string given the current context."""
        ...

    @property
    def description(self) -> str:
        return self.__class__.__name__


_PSEUDO_REPLAN_PLAN = (
    "Let me fix the parameter name — use indexPattern not index_pattern"
)


class MockLLMClient(LLMClient):
    """Deterministic mock planner used for offline teaching demos."""

    def __init__(self) -> None:
        self.last_model: str | None = None
        self.last_context_chars: int = 0

    def generate_plan(self, ctx: PlanContext) -> str:
        # Record routed model for metrics / teaching demos (Phase C).
        self.last_model = ctx.model
        self.last_context_chars = len(ctx.context_prompt)
        if ctx.pseudo_replan and ctx.round > 1:
            return _PSEUDO_REPLAN_PLAN
        if ctx.round <= 1:
            return "Apply minimal patch without reading test output"
        return (
            f"Replan using observation: {ctx.observation}; "
            "read test file and fix assertion"
        )

    @property
    def description(self) -> str:
        return "MockLLMClient(deterministic)"
