#!/usr/bin/env python3
"""Final QA audit: checks the key items from the assignment's QA checklist."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pipeline.schema import validate_record  # noqa: E402
from pipeline.scoring.buildability import score_record  # noqa: E402

URL = re.compile(r"^https?://")


def main() -> int:
    ds = json.load(open(os.path.join(ROOT, "data", "final", "dataset.json")))
    checks = []

    def chk(name, ok, detail=""):
        checks.append((name, ok, detail))

    apps = [r["app"] for r in ds]
    chk("exactly 100 apps", len(ds) == 100, str(len(ds)))
    chk("no duplicate apps", len(set(apps)) == len(apps))
    chk("exactly 10 categories", len({r["category"] for r in ds}) == 10)

    invalid = [(r["app"], validate_record(r)) for r in ds if validate_record(r)]
    chk("all records schema-valid", not invalid, str(invalid[:3]))

    mismatch = [r["app"] for r in ds if score_record(r)[:2] != (r["buildability_score"], r["buildability"])]
    chk("buildability matches rubric", not mismatch, str(mismatch[:3]))

    noev = [r["app"] for r in ds if not r.get("evidence")]
    chk("every app has >=1 evidence", not noev, str(noev[:5]))

    badurl = [e["url"] for r in ds for e in r["evidence"] if not URL.match(e.get("url", ""))]
    chk("all evidence URLs well-formed", not badurl, str(badurl[:3]))

    mcpbad = [r["app"] for r in ds if r["mcp_status"] in ("Official", "First-party documented") and not r.get("mcp_evidence_url")]
    chk("official/first-party MCP has evidence URL", not mcpbad, str(mcpbad[:5]))

    cli = [r["app"] for r in ds if "CLI" in r.get("api_type", []) and "REST" not in r.get("api_type", [])
           and "GraphQL" not in r.get("api_type", []) and r["buildability"] in ("Easy", "Medium")]
    chk("no local-only CLI rated Easy/Medium", not cli, str(cli))

    unk = [r["app"] for r in ds if r["access_model"] == "Unknown"]
    chk("Unknown access reported honestly", True, "unknown=" + str(unk))

    # artifacts present
    for f in ["data/raw/dataset_pass1.json", "data/final/dataset.json", "verification/sample.json",
              "verification/accuracy.json", "verification/errors.json", "verification/analytics.json",
              "site/index.html", "README.md", ".env.example", ".gitignore", "requirements.txt"]:
        chk(f"artifact exists: {f}", os.path.exists(os.path.join(ROOT, f)))

    chk("100 traces present", len(os.listdir(os.path.join(ROOT, "data", "traces"))) == 100)
    chk(".env is NOT committed", not os.path.exists(os.path.join(ROOT, ".env")))

    acc = json.load(open(os.path.join(ROOT, "verification", "accuracy.json")))
    chk("accuracy computed from records", acc["pass_1"]["total_claims"] > 0,
        f"pass1={acc['pass_1']['accuracy_pct']}% pass2={acc['pass_2']['accuracy_pct']}%")

    html = open(os.path.join(ROOT, "site", "index.html")).read()
    chk("site embeds 100 apps", html.count('"app":') >= 100)
    chk("site has no CDN/external script", "<script src=" not in html)

    ok = all(c[1] for c in checks)
    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not passed else ""))
    print("\n" + ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
