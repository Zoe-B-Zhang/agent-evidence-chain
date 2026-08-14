"""收集并输出 latency / token / cost 指标到 evidence（D2）。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MetricsCollector:
    """单次 run 的指标收集器。"""

    run_id: str
    task: str = ""
    model: str = "mock-small"
    route_tier: str = "simple"
    latencies_ms: list[int] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    rate_limited: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def add_latency(self, ms: int) -> None:
        """追加一次延迟样本。"""
        self.latencies_ms.append(ms)

    def set_cost(
        self,
        *,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> None:
        """设置累计 token/cost。"""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cost_usd = cost_usd

    def to_dict(self) -> dict[str, Any]:
        """序列化为可写入 JSON 的字典。"""
        p95 = 0
        if self.latencies_ms:
            ordered = sorted(self.latencies_ms)
            p95 = ordered[max(0, int(0.95 * len(ordered)) - 1)]
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "task": self.task,
            "model": self.model,
            "route_tier": self.route_tier,
            "latency_ms": {
                "samples": self.latencies_ms,
                "p95": p95,
                "total": sum(self.latencies_ms),
            },
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
            },
            "cost_usd": self.cost_usd,
            "rate_limited": self.rate_limited,
            **self.extra,
        }

    def write(self, out_dir: Path) -> Path:
        """写入 metrics-{run_id}.json。"""
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"metrics-{self.run_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path
