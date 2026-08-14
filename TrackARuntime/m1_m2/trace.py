"""Trace system — replayable execution graph (M2-K02)."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class TraceEvent:
    trace_id: str
    step: str
    tool: str
    input: dict[str, Any]
    output: dict[str, Any]
    latency_ms: int
    fallback_used: bool = False
    error_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceCollector:
    """Collects spans for one agent run."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    events: list[TraceEvent] = field(default_factory=list)

    def record(
        self,
        step: str,
        tool: str,
        payload: dict[str, Any],
        output: dict[str, Any],
        latency_ms: int,
        *,
        fallback_used: bool = False,
        error_class: str | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            trace_id=self.trace_id,
            step=step,
            tool=tool,
            input=payload,
            output=output,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
            error_class=error_class,
        )
        self.events.append(event)
        return event

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps([e.to_dict() for e in self.events], indent=2),
            encoding="utf-8",
        )

    def write_state(self, path: Path, state: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "trace_id": self.trace_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **state,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
