#!/usr/bin/env python3
"""
Run the research agent over the app seed set.

Usage:
  python scripts/run_research.py --pilot           # ~8 hand-picked hard apps
  python scripts/run_research.py --all             # all 100
  python scripts/run_research.py --ids 1 21 81     # specific ids

Requires an LLM key (ANTHROPIC_API_KEY or OPENAI_API_KEY) and TAVILY_API_KEY.
Writes one record per app to data/raw/<id>.json and a trace to data/traces/<id>.json.

NOTE: The dataset shipped in data/final/dataset.json was produced by the Kiro
research agent (Claude + web search/fetch) executing this exact workflow. This
script reproduces the workflow programmatically for any reviewer with their own
keys. Downstream stages (validation, scoring, analytics, site) run on the JSON
regardless of how it was produced.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.research_agent.agent import research_app  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_IDS = [1, 21, 61, 81, 53, 49, 58, 98, 99]  # incl. Salesforce, Slack, GitHub, Stripe, Ahrefs, Amazon SP, Sherlock, Mermaid CLI, YT Transcript


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ids", nargs="*", type=int)
    args = ap.parse_args()

    seeds = json.load(open(os.path.join(ROOT, "data", "apps.json")))
    if args.pilot:
        seeds = [s for s in seeds if s["id"] in PILOT_IDS]
    elif args.ids:
        seeds = [s for s in seeds if s["id"] in set(args.ids)]
    elif not args.all:
        ap.error("choose --pilot, --all, or --ids")

    os.makedirs(os.path.join(ROOT, "data", "raw"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "data", "traces"), exist_ok=True)

    for seed in seeds:
        print(f"[research] {seed['id']:>3} {seed['app']}")
        out = research_app(seed)
        json.dump(out["record"], open(os.path.join(ROOT, "data", "raw", f"{seed['id']}.json"), "w"), indent=2)
        json.dump(out["trace"], open(os.path.join(ROOT, "data", "traces", f"{seed['id']}.json"), "w"), indent=2)
        errs = out["record"].get("_validation_errors", [])
        print(f"          score={out['record']['buildability_score']} "
              f"build={out['record']['buildability']} valid={'OK' if not errs else errs}")


if __name__ == "__main__":
    main()
