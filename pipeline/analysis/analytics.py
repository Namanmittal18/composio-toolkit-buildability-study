"""
Analytics over the final dataset.

Fully deterministic. Produces the distributions and cross-tabs the case study
needs. Only computes what the data supports; no interpretation is baked in here.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def _count(items: list[str]) -> dict[str, int]:
    return dict(Counter(items).most_common())


def analyze(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(dataset)

    auth_counter: Counter[str] = Counter()
    for r in dataset:
        for a in r.get("auth_methods", []) or ["Unknown"]:
            auth_counter[a] += 1

    api_type_counter: Counter[str] = Counter()
    for r in dataset:
        for t in r.get("api_type", []) or ["Unknown"]:
            api_type_counter[t] += 1

    access = _count([r.get("access_model", "Unknown") for r in dataset])
    breadth = _count([r.get("api_breadth", "Unknown") for r in dataset])
    mcp = _count([r.get("mcp_status", "Unknown") for r in dataset])
    build = _count([r.get("buildability", "Unknown") for r in dataset])
    blockers = _count([r.get("main_blocker", "Unknown") or "None" for r in dataset])

    # cross-tabs by category
    build_by_cat: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    access_by_cat: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    score_by_cat: dict[str, list[int]] = defaultdict(list)
    for r in dataset:
        c = r["category"]
        build_by_cat[c][r.get("buildability", "Unknown")] += 1
        access_by_cat[c][r.get("access_model", "Unknown")] += 1
        score_by_cat[c].append(r.get("buildability_score", 0))

    gated_models = {"Admin approval", "Partner approval", "Contact sales",
                    "Enterprise-only", "No public API", "Paid plan required"}
    selfserve_models = {"Self-serve free", "Self-serve trial", "Public/no credentials"}

    def is_gated(r): return r.get("access_model") in gated_models
    def is_selfserve(r): return r.get("access_model") in selfserve_models

    # relationships
    def bucket_build(rs):
        return _count([r.get("buildability", "Unknown") for r in rs])

    selfserve_build = bucket_build([r for r in dataset if is_selfserve(r)])
    gated_build = bucket_build([r for r in dataset if is_gated(r)])
    has_mcp_build = bucket_build([r for r in dataset if r.get("mcp_status") in
                                  {"Official", "First-party documented", "Community", "Composio-supported"}])
    no_mcp_build = bucket_build([r for r in dataset if r.get("mcp_status") in {"None found", "Unknown"}])

    easy_wins = sorted(
        [r for r in dataset if r.get("buildability") in {"Easy", "Medium"}],
        key=lambda r: -r.get("buildability_score", 0),
    )
    outreach = sorted(
        [r for r in dataset if r.get("buildability") in {"Hard", "Not currently feasible"}],
        key=lambda r: r.get("buildability_score", 0),
    )

    mcp_apps = [r["app"] for r in dataset if r.get("mcp_status") in
                {"Official", "First-party documented"}]

    return {
        "n": n,
        "auth_distribution": dict(auth_counter.most_common()),
        "api_type_distribution": dict(api_type_counter.most_common()),
        "access_distribution": access,
        "breadth_distribution": breadth,
        "mcp_distribution": mcp,
        "buildability_distribution": build,
        "blocker_distribution": blockers,
        "buildability_by_category": {k: dict(v) for k, v in build_by_cat.items()},
        "access_by_category": {k: dict(v) for k, v in access_by_cat.items()},
        "avg_score_by_category": {k: round(sum(v) / len(v), 1) for k, v in score_by_cat.items()},
        "counts": {
            "gated": sum(1 for r in dataset if is_gated(r)),
            "self_serve": sum(1 for r in dataset if is_selfserve(r)),
            "has_official_or_firstparty_mcp": len(mcp_apps),
            "has_any_mcp": sum(1 for r in dataset if r.get("mcp_status") in
                               {"Official", "First-party documented", "Community", "Composio-supported"}),
            "easy": build.get("Easy", 0),
            "medium": build.get("Medium", 0),
            "hard": build.get("Hard", 0),
            "not_feasible": build.get("Not currently feasible", 0),
            "no_public_api": sum(1 for r in dataset if r.get("access_model") == "No public API"),
        },
        "relationship_selfserve_vs_buildability": selfserve_build,
        "relationship_gated_vs_buildability": gated_build,
        "relationship_mcp_vs_buildability": {"has_mcp": has_mcp_build, "no_mcp": no_mcp_build},
        "mcp_apps": mcp_apps,
        "easy_wins_ranked": [
            {"app": r["app"], "category": r["category"], "score": r["buildability_score"],
             "access_model": r.get("access_model"), "auth": r.get("auth_methods"),
             "api_type": r.get("api_type"), "breadth": r.get("api_breadth"),
             "mcp": r.get("mcp_status"), "blocker": r.get("main_blocker")}
            for r in easy_wins
        ],
        "outreach_ranked": [
            {"app": r["app"], "category": r["category"], "score": r["buildability_score"],
             "access_model": r.get("access_model"), "blocker": r.get("main_blocker")}
            for r in outreach
        ],
    }
