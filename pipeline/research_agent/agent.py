"""
Per-app research agent orchestration.

Stages (each recorded in the trace):
  seed -> source discovery -> fetch -> LLM extraction -> schema validation
       -> deterministic scoring -> conflict/ambiguity flags -> record + trace

Failure handling is graceful: search/fetch errors are logged into the trace and
the app is still emitted with Unknowns rather than a fabricated answer.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from pipeline.extraction.prompt import SYSTEM, build_user_prompt
from pipeline.extraction.providers import ProviderError, fetch_url, get_llm, get_search
from pipeline.schema import validate_record
from pipeline.scoring.buildability import apply_scoring
from pipeline.source_discovery.discover import candidate_urls, search_queries


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def research_app(seed: dict[str, Any], max_search: int = 3, max_fetch: int = 3) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "app": seed["app"],
        "started_at": _now(),
        "stages": [],
        "queries": [],
        "sources_found": [],
        "fetched": [],
        "errors": [],
    }

    llm = get_llm()  # raises clearly if no key
    search = get_search()

    evidence_items: list[dict[str, str]] = []

    # --- source discovery ---
    queries = search_queries(seed["app"], seed["hint"])[:max_search]
    trace["queries"] = queries
    trace["stages"].append({"stage": "source_discovery", "at": _now(), "candidates": candidate_urls(seed["app"], seed["hint"])})

    for q in queries:
        try:
            results = search.search(q, k=5)
            for r in results:
                trace["sources_found"].append({"query": q, "url": r["url"], "title": r["title"]})
                evidence_items.append(r)
        except Exception as e:  # noqa: BLE001
            trace["errors"].append({"stage": "search", "query": q, "error": str(e)})

    # --- fetch top official-looking pages ---
    fetched = 0
    for r in evidence_items:
        if fetched >= max_fetch:
            break
        try:
            html = fetch_url(r["url"])
            r["snippet"] = (r.get("snippet", "") + "\n" + html)[:1500]
            trace["fetched"].append(r["url"])
            fetched += 1
        except Exception as e:  # noqa: BLE001
            trace["errors"].append({"stage": "fetch", "url": r["url"], "error": str(e)})

    # --- LLM extraction ---
    user = build_user_prompt(seed["app"], seed["category"], seed["hint"], evidence_items)
    trace["stages"].append({"stage": "extraction", "at": _now()})
    try:
        extracted = llm.complete_json(SYSTEM, user)
    except Exception as e:  # noqa: BLE001
        trace["errors"].append({"stage": "extraction", "error": str(e)})
        extracted = {}

    rec: dict[str, Any] = {
        "id": seed["id"],
        "app": seed["app"],
        "category": seed["category"],
        "hint": seed["hint"],
        "verification_status": "unverified",
    }
    rec.update(extracted)
    rec.setdefault("evidence", [])
    for ev in rec["evidence"]:
        ev.setdefault("retrieved_at", _now())

    # --- deterministic scoring ---
    apply_scoring(rec)
    trace["stages"].append({"stage": "scoring", "at": _now(), "score": rec["buildability_score"], "label": rec["buildability"]})

    # --- validation ---
    errors = validate_record(rec)
    rec["_validation_errors"] = errors
    if not errors:
        rec["verification_status"] = "auto-validated"
    trace["stages"].append({"stage": "validation", "at": _now(), "errors": errors})

    trace["finished_at"] = _now()
    return {"record": rec, "trace": trace}
