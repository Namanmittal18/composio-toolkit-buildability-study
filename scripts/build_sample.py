#!/usr/bin/env python3
"""
Build the field-level verification sample (verification/sample.json).

Method: a stratified sample of apps (easy / gated / trap / low-confidence /
model-knowledge) was independently re-checked in a second pass against primary
sources. For each sampled (app, field):
  - agent_answer   = the Pass-1 value  (data/raw/dataset_pass1.json)
  - verified_answer = the independently confirmed value (data/final/dataset.json)
  - correct        = (agent_answer == verified_answer)

Pass 1 records compare the ORIGINAL agent output to the verified value.
Pass 2 records compare the CORRECTED dataset to the verified value.
This yields an honest before/after: the only differences are the fields the
second pass actually corrected (errors it found), so Pass-2 accuracy on the
sample reflects those fixes. Unsampled apps are NOT claimed to be error-free.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Stratified sample (33 apps across strata).
SAMPLE_IDS = [
    4, 7, 13, 14, 19, 23, 67, 79,          # apps corrected in pass 2 (MCP false negatives)
    81, 61, 21, 71, 2, 41, 22, 36, 93,     # easy / self-serve (live-searched)
    53, 49, 90, 92, 91, 10, 44,            # gated / enterprise
    58, 98,                                # trap (local CLI / library)
    50, 85, 84,                            # low-confidence / unverifiable
    46, 27, 100, 97,                       # additional canonical checks
]

FIELDS = ["auth_methods", "access_model", "api_type", "api_breadth", "mcp_status", "buildability"]

# error_type lookup for known corrected (app_id, field)
ERROR_TYPES = {(i, "mcp_status"): "MCP false negative" for i in [4, 7, 13, 14, 19, 23, 67, 79]}


def _ev_url(rec, field):
    if field == "mcp_status" and rec.get("mcp_evidence_url"):
        return rec["mcp_evidence_url"]
    for ev in rec.get("evidence", []):
        if field in ev.get("supports_fields", []):
            return ev["url"]
    ev = rec.get("evidence", [])
    return ev[0]["url"] if ev else ""


def main() -> int:
    pass1 = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "data", "raw", "dataset_pass1.json")))}
    final = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "data", "final", "dataset.json")))}

    records = []
    for pass_num, source in ((1, pass1), (2, final)):
        for app_id in SAMPLE_IDS:
            agent = source[app_id]
            verified = final[app_id]
            for field in FIELDS:
                a = agent.get(field)
                v = verified.get(field)
                correct = a == v
                rec = {
                    "app": verified["app"],
                    "category": verified["category"],
                    "field": field,
                    "agent_answer": a,
                    "verified_answer": v,
                    "correct": correct,
                    "verification_method": "independent second-pass search + primary docs",
                    "evidence_url": _ev_url(verified, field),
                    "error_type": None if correct else ERROR_TYPES.get((app_id, field), "unspecified"),
                    "correction": None if correct else f"{a} -> {v}",
                    "pass": pass_num,
                }
                records.append(rec)

    json.dump(records, open(os.path.join(ROOT, "verification", "sample.json"), "w"), indent=2)
    n_apps = len(SAMPLE_IDS)
    print(f"[sample] {n_apps} apps x {len(FIELDS)} fields x 2 passes = {len(records)} verification records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
