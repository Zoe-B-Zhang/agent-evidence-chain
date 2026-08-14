"""Eval runner with regression gate (M4 + D4)."""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from m4.baseline import resolve_baseline
from m4.golden_dataset import load_golden_dataset
from m4.judge import get_judge

_TAXONOMY_PATH = Path(__file__).parent / "failure_taxonomy.md"
_FALLBACK_ADVICE = "查阅 failure_taxonomy.md 并补充检测信号。"


@lru_cache(maxsize=1)
def _load_taxonomy_advice() -> dict[str, str]:
    """Parse failure_taxonomy.md table into code → remediation advice."""
    if not _TAXONOMY_PATH.exists():
        return {}
    advice: dict[str, str] = {}
    for line in _TAXONOMY_PATH.read_text(encoding="utf-8").splitlines():
        m = re.match(
            r"\|\s*([A-Z_]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
            line.strip(),
        )
        if not m or m.group(1) == "Code":
            continue
        code, category, signal = (g.strip() for g in m.groups())
        advice[code] = f"[{category}] 检测信号：{signal} → 按该轴排查并加回归场景。"
    return advice


def _simulate(scenario: dict[str, Any]) -> dict[str, Any]:
    """模拟场景执行（deterministic teaching stub）。"""
    start = time.perf_counter()
    time.sleep(0.005)
    latency_ms = int((time.perf_counter() - start) * 1000)
    category = scenario.get("category", "mixed")
    if scenario["expect"] == "pass":
        return {
            "id": scenario["id"],
            "success": True,
            "latencyMs": latency_ms,
            "category": category,
        }
    return {
        "id": scenario["id"],
        "success": False,
        "failure_code": scenario.get("failure_code", "REQ_MISREAD"),
        "latencyMs": latency_ms,
        "category": category,
    }


def _category_split(results: list[dict[str, Any]]) -> dict[str, Any]:
    """按 retrieval / generation / mixed 统计成功率。"""
    buckets: dict[str, list[bool]] = {"retrieval": [], "generation": [], "mixed": []}
    for r in results:
        cat = r.get("category", "mixed")
        if cat not in buckets:
            buckets[cat] = []
        buckets[cat].append(bool(r["success"]))
    out: dict[str, Any] = {}
    for cat, flags in buckets.items():
        if not flags:
            out[cat] = {"total": 0, "successes": 0, "success_rate": 0.0}
            continue
        ok = sum(1 for f in flags if f)
        out[cat] = {
            "total": len(flags),
            "successes": ok,
            "success_rate": round(ok / len(flags), 3),
        }
    return out


def _remediation_layer(failure_distribution: dict[str, int]) -> dict[str, str]:
    """为每个失败码给出 taxonomy 驱动的修复建议（读 failure_taxonomy.md）。"""
    taxonomy = _load_taxonomy_advice()
    return {code: taxonomy.get(code, _FALLBACK_ADVICE) for code in failure_distribution}


def run_eval(
    baseline: float | str = 0.5,
    seed: int = 42,
    *,
    evidence_dir: Path | None = None,
    enable_judge: bool = False,
) -> dict[str, Any]:
    """运行 golden scenarios 并计算 gate。"""
    _ = seed  # reserved for future stochastic sims
    data = load_golden_dataset()
    results = [_simulate(s) for s in data["scenarios"]]
    successes = sum(1 for r in results if r["success"])
    total = len(results)
    rate = successes / total if total else 0.0

    evidence_dir = evidence_dir or Path(__file__).parent / "evidence"
    baseline_info = resolve_baseline(baseline, evidence_dir=evidence_dir)
    baseline_value = float(baseline_info["baseline"])

    failures = Counter(r.get("failure_code", "UNKNOWN") for r in results if not r["success"])
    latencies = sorted(r["latencyMs"] for r in results)
    p95 = latencies[max(0, int(0.95 * len(latencies)) - 1)] if latencies else 0

    judge = get_judge(enabled=enable_judge)
    judge_verdicts = [
        judge.judge(task=r["id"], trajectory=[], outcome=r).rationale for r in results[:3]
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": data.get("version"),
        "total": total,
        "successes": successes,
        "success_rate": round(rate, 3),
        "baseline": baseline_value,
        "baseline_meta": baseline_info,
        "gate_pass": rate >= baseline_value,
        "failure_distribution": dict(failures),
        "remediation_advice": _remediation_layer(dict(failures)),
        "category_split": _category_split(results),
        "p95_latency_ms": p95,
        "judge_sample": judge_verdicts,
        "results": results,
    }


def write_eval_report(report: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    """写入 evaluation-report.json 与 .md。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "evaluation-report.json"
    md_path = out_dir / "evaluation-report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Evaluation Report",
        "",
        f"- Dataset version: {report.get('dataset_version')}",
        f"- Success: {report['successes']}/{report['total']} ({report['success_rate']:.1%})",
        f"- Gate ({report['baseline']:.0%}): **{'PASS' if report['gate_pass'] else 'FAIL'}**",
        f"- Baseline source: {report.get('baseline_meta', {}).get('source', 'n/a')}",
        f"- P95 latency: {report['p95_latency_ms']} ms",
        "",
        "## Category split (retrieval vs generation)",
        "",
    ]
    for cat, stats in sorted(report.get("category_split", {}).items()):
        lines.append(
            f"- {cat}: {stats['successes']}/{stats['total']} ({stats['success_rate']:.1%})"
        )
    lines.extend(["", "## Failure distribution + remediation", ""])
    advice = report.get("remediation_advice", {})
    for code, count in sorted(report["failure_distribution"].items()):
        tip = advice.get(code, "")
        lines.append(f"- {code}: {count} — {tip}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
