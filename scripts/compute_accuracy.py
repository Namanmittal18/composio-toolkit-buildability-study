#!/usr/bin/env python3
"""Compute pass-1, pass-2, and overall accuracy from verification/sample.json."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.verification.accuracy import compute_accuracy  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    records = json.load(open(os.path.join(ROOT, "verification", "sample.json")))
    out = {
        "overall": compute_accuracy(records),
        "pass_1": compute_accuracy(records, 1),
        "pass_2": compute_accuracy(records, 2),
    }
    dest = os.path.join(ROOT, "verification", "accuracy.json")
    json.dump(out, open(dest, "w"), indent=2)
    print(f"[accuracy] pass1={out['pass_1']['accuracy_pct']}%  "
          f"pass2={out['pass_2']['accuracy_pct']}%  overall={out['overall']['accuracy_pct']}%")
    print(f"  fields: {list(out['overall']['accuracy_by_field'].keys())}")


if __name__ == "__main__":
    main()
