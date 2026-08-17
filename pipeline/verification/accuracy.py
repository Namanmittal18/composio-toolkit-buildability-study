"""
Field-level accuracy computation from verification records.

A verification record compares the agent's answer for one (app, field) against
an independently verified answer. This module aggregates them into overall,
per-field, and per-category accuracy. It is fully deterministic and runs on the
real verification/sample.json produced during the human + second-pass review.

Verification record shape:
  {
    "app": "...", "category": "...", "field": "...",
    "agent_answer": ..., "verified_answer": ...,
    "correct": true/false, "verification_method": "...",
    "evidence_url": "...", "error_type": "...", "correction": "...",
    "pass": 1 | 2
  }
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def compute_accuracy(records: list[dict[str, Any]], pass_num: int | None = None) -> dict[str, Any]:
    recs = [r for r in records if pass_num is None or r.get("pass") == pass_num]
    total = len(recs)
    correct = sum(1 for r in recs if r.get("correct"))

    by_field: dict[str, list[int]] = defaultdict(list)
    by_cat: dict[str, list[int]] = defaultdict(list)
    by_error: dict[str, int] = defaultdict(int)

    for r in recs:
        by_field[r["field"]].append(1 if r.get("correct") else 0)
        by_cat[r.get("category", "?")].append(1 if r.get("correct") else 0)
        if not r.get("correct"):
            by_error[r.get("error_type", "unspecified")] += 1

    def pct(xs: list[int]) -> float:
        return round(100 * sum(xs) / len(xs), 1) if xs else 0.0

    return {
        "pass": pass_num,
        "total_claims": total,
        "correct_claims": correct,
        "incorrect_claims": total - correct,
        "accuracy_pct": pct([1 if r.get("correct") else 0 for r in recs]),
        "accuracy_by_field": {k: {"n": len(v), "pct": pct(v)} for k, v in sorted(by_field.items())},
        "accuracy_by_category": {k: {"n": len(v), "pct": pct(v)} for k, v in sorted(by_cat.items())},
        "error_type_counts": dict(sorted(by_error.items(), key=lambda x: -x[1])),
        "apps_sampled": sorted({r["app"] for r in recs}),
        "num_apps_sampled": len({r["app"] for r in recs}),
    }
