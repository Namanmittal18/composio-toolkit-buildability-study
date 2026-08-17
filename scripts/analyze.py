#!/usr/bin/env python3
"""Compute analytics from the final dataset -> verification/analytics.json."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.analysis.analytics import analyze  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    dataset = json.load(open(os.path.join(ROOT, "data", "final", "dataset.json")))
    result = analyze(dataset)
    out = os.path.join(ROOT, "verification", "analytics.json")
    json.dump(result, open(out, "w"), indent=2)
    print(f"[analyze] {result['n']} apps analyzed -> {out}")
    print(f"  buildability: {result['buildability_distribution']}")
    print(f"  access:       {result['access_distribution']}")
    print(f"  mcp:          {result['mcp_distribution']}")


if __name__ == "__main__":
    main()
