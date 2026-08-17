#!/usr/bin/env python3
"""
Finalize a research file (raw LLM/agent extraction, WITHOUT buildability) into a
scored + validated dataset.

  python scripts/finalize.py <input_research.json> <output_dataset.json>

Steps per record:
  1. merge seed fields (id, app, category, hint) from data/apps.json
  2. apply deterministic buildability scoring (single source of truth)
  3. validate against schema
  4. report validation errors (non-zero exit if any)

This is the boundary between the non-deterministic extraction stage and the fully
deterministic, auditable downstream. Buildability is NEVER hand-authored.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.schema import validate_record  # noqa: E402
from pipeline.scoring.buildability import apply_scoring  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    inp, outp = sys.argv[1], sys.argv[2]
    seeds = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "data", "apps.json")))}
    research = json.load(open(inp))

    finalized = []
    total_errors = 0
    for r in research:
        seed = seeds[r["id"]]
        r["app"] = seed["app"]
        r["category"] = seed["category"]
        r["hint"] = seed["hint"]
        r.setdefault("verification_status", "unverified")
        apply_scoring(r)
        errs = validate_record(r)
        if errs:
            total_errors += 1
            print(f"INVALID {r['id']:>3} {r['app']}: {errs}")
        finalized.append(r)

    finalized.sort(key=lambda x: x["id"])
    json.dump(finalized, open(outp, "w"), indent=2)
    print(f"[finalize] {len(finalized)} records -> {outp} ({total_errors} invalid)")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
