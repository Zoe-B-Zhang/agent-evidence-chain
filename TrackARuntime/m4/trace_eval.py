"""从 trace.json 计算轨迹级质量指标（D4）。"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def evaluate_trace(trace_path: Path | list[dict[str, Any]]) -> dict[str, Any]:
    """计算 fingerprint 重复、retry、fallback 率、stalled 检测。"""
    if isinstance(trace_path, Path):
        events = json.loads(trace_path.read_text(encoding="utf-8"))
    else:
        events = trace_path

    total = len(events)
    if total == 0:
        return {
            "total_events": 0,
            "fingerprint_duplicates": 0,
            "max_fingerprint_repeats": 0,
            "retry_count": 0,
            "fallback_rate": 0.0,
            "stalled_count": 0,
            "error_class_distribution": {},
        }

    # Fingerprint ≈ tool + sorted input JSON.
    fps: list[str] = []
    for e in events:
        raw = json.dumps({"tool": e.get("tool"), "input": e.get("input")}, sort_keys=True)
        fps.append(raw)
    fp_counts = Counter(fps)
    duplicates = sum(1 for c in fp_counts.values() if c > 1)
    max_repeats = max(fp_counts.values()) if fp_counts else 0

    retry_count = sum(
        1
        for e in events
        if e.get("error_class") == "retryable"
        or (isinstance(e.get("output"), dict) and e["output"].get("error_class") == "retryable")
    )
    fallback_used = sum(1 for e in events if e.get("fallback_used"))
    stalled_count = sum(1 for e in events if e.get("error_class") == "stalled")
    err_dist = Counter(e.get("error_class") or "none" for e in events)

    return {
        "total_events": total,
        "fingerprint_duplicates": duplicates,
        "max_fingerprint_repeats": max_repeats,
        "retry_count": retry_count,
        "fallback_rate": round(fallback_used / total, 3),
        "stalled_count": stalled_count,
        "error_class_distribution": dict(err_dist),
    }
