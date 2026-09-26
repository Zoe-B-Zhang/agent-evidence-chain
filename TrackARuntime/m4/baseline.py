"""动态校准 eval baseline（D4）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_BASELINE = 0.45
HISTORY_FILENAME = "evaluation-report.json"


def load_historical_success_rate(evidence_dir: Path) -> float | None:
    """从历史 evaluation-report.json 读取 success_rate；不存在则返回 None。"""
    path = evidence_dir / HISTORY_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    rate = data.get("success_rate")
    if isinstance(rate, (int, float)):
        return float(rate)
    return None


def resolve_baseline(
    requested: float | str | None,
    *,
    evidence_dir: Path | None = None,
    floor: float = 0.4,
    ceiling: float = 0.9,
) -> dict[str, Any]:
    """解析 baseline：数值直接用；'auto' 用历史成功率（夹在 floor/ceiling）。

    无历史时回退 DEFAULT_BASELINE 并注明来源。
    """
    evidence_dir = evidence_dir or Path(__file__).parent / "evidence"

    if requested is None or requested == "auto":
        historical = load_historical_success_rate(evidence_dir)
        if historical is None:
            return {
                "baseline": DEFAULT_BASELINE,
                "source": "default_fallback",
                "note": f"no historical evaluation-report; using {DEFAULT_BASELINE}",
            }
        calibrated = min(ceiling, max(floor, historical))
        return {
            "baseline": round(calibrated, 3),
            "source": "historical_success_rate",
            "historical_success_rate": historical,
            "note": f"clamped to [{floor}, {ceiling}]",
        }

    value = float(requested)
    return {
        "baseline": value,
        "source": "explicit",
        "note": "user-provided baseline",
    }
