"""M3-K04 L3: rollout state machine + auto-rollback on guardrail fail streak.

Generic design (business-agnostic)
--------------------------------
Inputs:
  - candidate artifact version (e.g. prompt v2, model route B, feature flag payload)
  - gray_percent (canary traffic share)
  - guardrail_check(version, gray) -> {ok, metrics, action, reason}
  - optional eval_gate() -> {gate_pass} for promote
  - persisted rollout_state (phase, fail_streak, locks, audit)

State machine phases:
  stable   -> active version at 100% (or gray=0 on candidate)
  gray     -> candidate on partial traffic; stable remains fallback
  locked   -> candidate blocked after N consecutive guardrail failures
  promoted -> candidate passed gray + eval; active switches to candidate

On each watch tick:
  1. Reject if candidate is locked.
  2. Run guardrail_check.
  3. If fail: increment fail_streak; rollback traffic to stable;
     if fail_streak >= limit: lock candidate + alert.
  4. If pass: reset fail_streak; if promote requested and eval_gate_pass:
     promote; else stay in gray (ready for next tick).

Outputs:
  - updated rollout_state.json
  - harness-report.json (single tick evidence)
  - alerts[] append-only audit
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

GuardrailFn = Callable[[str, int], dict[str, Any]]
EvalGateFn = Callable[[], dict[str, Any]]
AlertFn = Callable[[dict[str, Any], str, dict[str, Any]], None]

DEFAULT_STATE: dict[str, Any] = {
    "phase": "stable",
    "active_version": "v1",
    "candidate_version": None,
    "gray_percent": 0,
    "fail_streak": 0,
    "fail_streak_limit": 3,
    "version_locked": False,
    "locked_versions": [],
    "alerts": [],
    "traffic_log": [],
    "history": [],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_rollout_state(path: Path, *, fail_streak_limit: int = 3) -> dict[str, Any]:
    """Load rollout state or return defaults."""
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
    else:
        state = deepcopy(DEFAULT_STATE)
    state.setdefault("fail_streak_limit", fail_streak_limit)
    state["fail_streak_limit"] = fail_streak_limit
    for key, value in DEFAULT_STATE.items():
        state.setdefault(key, deepcopy(value) if isinstance(value, list) else value)
    return state


def save_rollout_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def default_alert(state: dict[str, Any], message: str, payload: dict[str, Any]) -> None:
    state["alerts"].append({"at": _now(), "message": message, "payload": payload})


def apply_traffic(
    state: dict[str, Any],
    *,
    active_version: str,
    gray_percent: int,
    reason: str,
) -> None:
    """Mock traffic switch — updates state only (no real load balancer)."""
    state["active_version"] = active_version
    state["gray_percent"] = gray_percent
    state["traffic_log"].append(
        {
            "at": _now(),
            "active_version": active_version,
            "gray_percent": gray_percent,
            "reason": reason,
        }
    )


def run_watch_cycle(
    state: dict[str, Any],
    *,
    candidate_version: str,
    gray_percent: int,
    guardrail_check: GuardrailFn,
    eval_gate: EvalGateFn | None = None,
    promote_if_ready: bool = False,
    alert: AlertFn = default_alert,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Execute one rollout watch tick; return (state, harness_report, cycle_summary)."""
    stable = state.get("active_version", "v1")
    if state.get("version_locked") and candidate_version in state.get("locked_versions", []):
        msg = f"candidate {candidate_version} is locked; rollback controller blocked"
        alert(state, msg, {"candidate": candidate_version})
        summary = {
            "tick": "rejected",
            "reason": "candidate_locked",
            "candidate_version": candidate_version,
        }
        state["history"].append({"at": _now(), **summary})
        return state, {}, summary

    report = guardrail_check(candidate_version, gray_percent)
    state["candidate_version"] = candidate_version
    tick: dict[str, Any] = {
        "at": _now(),
        "candidate_version": candidate_version,
        "gray_percent": gray_percent,
        "guardrail_ok": report.get("guardrail_ok"),
        "harness_action": report.get("action"),
    }

    if not report.get("guardrail_ok"):
        state["fail_streak"] = int(state.get("fail_streak", 0)) + 1
        tick["fail_streak"] = state["fail_streak"]
        apply_traffic(
            state,
            active_version=stable,
            gray_percent=0,
            reason="guardrail_fail_auto_rollback",
        )
        state["phase"] = "stable"
        alert(
            state,
            "guardrail failed during gray",
            {
                "candidate": candidate_version,
                "fail_streak": state["fail_streak"],
                "rollback_reason": report.get("rollback_reason"),
            },
        )
        if state["fail_streak"] >= state["fail_streak_limit"]:
            state["version_locked"] = True
            state["phase"] = "locked"
            locked = set(state.get("locked_versions", []))
            locked.add(candidate_version)
            state["locked_versions"] = sorted(locked)
            alert(
                state,
                "candidate locked after fail streak",
                {
                    "candidate": candidate_version,
                    "fail_streak_limit": state["fail_streak_limit"],
                },
            )
            tick["locked"] = True
        summary = {"tick": "rollback", **tick}
        state["history"].append(summary)
        return state, report, summary

    state["fail_streak"] = 0
    state["phase"] = "gray"
    apply_traffic(
        state,
        active_version=stable,
        gray_percent=gray_percent,
        reason="gray_guardrail_pass",
    )
    tick["fail_streak"] = 0

    if promote_if_ready:
        if eval_gate is None:
            tick["promote"] = "skipped_no_eval_gate"
        else:
            eval_report = eval_gate()
            tick["eval_gate_pass"] = eval_report.get("gate_pass")
            if eval_report.get("gate_pass"):
                state["phase"] = "promoted"
                apply_traffic(
                    state,
                    active_version=candidate_version,
                    gray_percent=100,
                    reason="promote_after_eval_gate",
                )
                alert(
                    state,
                    "promoted candidate",
                    {
                        "candidate": candidate_version,
                        "eval_success_rate": eval_report.get("success_rate"),
                    },
                )
                tick["promote"] = "done"
            else:
                alert(state, "promote blocked: eval gate failed", eval_report)
                tick["promote"] = "blocked_eval_gate"

    summary = {"tick": "gray_ok", **tick}
    state["history"].append(summary)
    return state, report, summary


def reset_rollout_state(state: dict[str, Any]) -> dict[str, Any]:
    """Clear locks and streak for demo replay."""
    fresh = deepcopy(DEFAULT_STATE)
    fresh["fail_streak_limit"] = state.get("fail_streak_limit", 3)
    return fresh
