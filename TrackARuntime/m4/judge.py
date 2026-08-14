"""LLM-as-Judge 接口（默认关闭，保持 deterministic 教学行为）（D4）。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class JudgeVerdict:
    """评判结果。"""

    score: float
    passed: bool
    rationale: str
    enabled: bool = False


class Judge(ABC):
    """Judge 抽象接口。"""

    @abstractmethod
    def judge(self, *, task: str, trajectory: list[dict[str, Any]], outcome: dict[str, Any]) -> JudgeVerdict:
        """对一条轨迹给出分数与理由。"""
        ...


class DisabledJudge(Judge):
    """默认关闭：不调用 LLM，返回中性 verdict。"""

    def judge(self, *, task: str, trajectory: list[dict[str, Any]], outcome: dict[str, Any]) -> JudgeVerdict:
        """返回 disabled 占位结果。"""
        return JudgeVerdict(
            score=0.0,
            passed=bool(outcome.get("success")),
            rationale="judge disabled (deterministic teaching mode)",
            enabled=False,
        )


class HeuristicJudge(Judge):
    """轻量启发式 Judge（仍无网络）：成功且无 fallback 得高分。"""

    def judge(self, *, task: str, trajectory: list[dict[str, Any]], outcome: dict[str, Any]) -> JudgeVerdict:
        """基于 success / fallback 计数打分。"""
        success = bool(outcome.get("success"))
        fallbacks = sum(1 for e in trajectory if e.get("fallback_used"))
        score = 1.0 if success and fallbacks == 0 else (0.6 if success else 0.0)
        return JudgeVerdict(
            score=score,
            passed=success,
            rationale=f"heuristic: success={success}, fallbacks={fallbacks}",
            enabled=True,
        )


def get_judge(*, enabled: bool = False) -> Judge:
    """工厂：默认 DisabledJudge。"""
    if enabled:
        return HeuristicJudge()
    return DisabledJudge()
