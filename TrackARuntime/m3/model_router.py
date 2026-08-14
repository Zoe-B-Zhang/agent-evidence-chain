"""简单任务 vs 复杂任务模型路由 + fallback（D2）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    """路由结果。"""

    model: str
    tier: str  # "simple" | "complex"
    fallback: str
    reason: str


# Keyword heuristics for complexity (teaching stub — deterministic).
_COMPLEX_KEYWORDS = (
    "refactor",
    "migrate",
    "architecture",
    "multi",
    "entire",
    "redesign",
    "debug",
    "investigate",
    "container",
    "stuck",
)


class ModelRouter:
    """按任务复杂度选择模型，并提供 fallback。"""

    def __init__(
        self,
        *,
        simple_model: str = "mock-small",
        complex_model: str = "mock-large",
        fallback_model: str = "mock-small",
    ) -> None:
        self.simple_model = simple_model
        self.complex_model = complex_model
        self.fallback_model = fallback_model

    def route(self, task: str) -> RouteDecision:
        """根据任务文本启发式选择模型。"""
        lower = task.lower()
        is_complex = any(k in lower for k in _COMPLEX_KEYWORDS) or len(task) > 80
        if is_complex:
            return RouteDecision(
                model=self.complex_model,
                tier="complex",
                fallback=self.fallback_model,
                reason="complex keywords or long task",
            )
        return RouteDecision(
            model=self.simple_model,
            tier="simple",
            fallback=self.fallback_model,
            reason="default simple path",
        )

    def fallback(self, decision: RouteDecision) -> str:
        """返回降级模型名。"""
        return decision.fallback
