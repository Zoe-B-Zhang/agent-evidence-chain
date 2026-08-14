"""四层上下文管理：system / long-term / short-term / current（D2）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextLayers:
    """分层上下文，供 plan / LLM 使用。"""

    system: str = "You are a coding agent. Prefer minimal, verified changes."
    long_term: str = ""
    short_term: str = ""
    current: str = ""

    def render(self, *, max_chars: int = 4000) -> str:
        """拼接四层上下文并按字符上限截断。"""
        short = self.short_term
        long_term = self.long_term
        parts = [
            ("system", self.system),
            ("long_term", long_term),
            ("short_term", short),
            ("current", self.current),
        ]
        joined = "\n\n".join(f"[{n}]\n{t}" for n, t in parts if t)
        if len(joined) <= max_chars:
            return joined
        # Prefer truncating short_term, then long_term.
        overhead = len(joined) - max_chars
        if short:
            cut = min(len(short), overhead)
            short = short[: max(0, len(short) - cut)] + ("…" if cut else "")
            overhead -= cut
        if overhead > 0 and long_term:
            cut = min(len(long_term), overhead)
            long_term = long_term[: max(0, len(long_term) - cut)] + ("…" if cut else "")
        parts = [
            ("system", self.system),
            ("long_term", long_term),
            ("short_term", short),
            ("current", self.current),
        ]
        return "\n\n".join(f"[{n}]\n{t}" for n, t in parts if t)[:max_chars]


@dataclass
class ContextManager:
    """从 loop 状态构建四层上下文。"""

    max_chars: int = 4000
    system_prompt: str = "You are a coding agent. Prefer minimal, verified changes."
    layers: ContextLayers = field(default_factory=ContextLayers)

    def build(
        self,
        *,
        task: str,
        observation: str = "",
        history: list[dict[str, Any]] | None = None,
        plan: str = "",
    ) -> ContextLayers:
        """根据当前任务与历史填充四层上下文。"""
        history = history or []
        recent = history[-6:]
        short_lines = [
            f"r{h.get('round')}:{h.get('phase')} — {str(h.get('detail', ''))[:120]}"
            for h in recent
        ]
        long_summary = f"Task: {task}"
        if len(history) > 6:
            long_summary += f" | earlier_steps={len(history) - 6}"
        self.layers = ContextLayers(
            system=self.system_prompt,
            long_term=long_summary,
            short_term="\n".join(short_lines),
            current=f"observation={observation}; plan={plan}",
        )
        return self.layers

    def as_prompt(self) -> str:
        """返回截断后的拼接 prompt。"""
        return self.layers.render(max_chars=self.max_chars)
