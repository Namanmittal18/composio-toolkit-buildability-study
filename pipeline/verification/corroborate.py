"""
Composio corroboration (OPTIONAL, KEY-GATED, best-effort — not part of the
shipped results).

If a COMPOSIO_API_KEY is present, this module independently corroborates the
agent's auth/access findings against Composio's own toolkit catalog metadata
(whether a toolkit exists for the app and which auth schemes it exposes). It is
treated strictly as CORROBORATION, never ground truth: Composio listing a
toolkit is strong evidence a self-serve integration exists, but the primary
question remains what the vendor's own docs say.

Honest status (see README):
  - This path was NOT executed for the shipped dataset. No COMPOSIO_API_KEY was
    configured in the build environment, so `corroborate()` returned None for
    every app and the pipeline never depended on it.
  - The calls below target the documented Composio v3 Python SDK
    (`Composio().toolkits.get(slug=...)` / `.list(...)`, see
    https://docs.composio.dev/reference/sdk-reference/python/toolkits). Response
    fields are read defensively because the exact response object differs across
    SDK versions. It is a genuine best-effort integration, but it is UNTESTED
    without a key and a pinned SDK version.

Without a key this module is a no-op, so the rest of the pipeline is fully
reproducible with no Composio access.
"""
from __future__ import annotations

import os
from typing import Any


def composio_available() -> bool:
    return bool(os.environ.get("COMPOSIO_API_KEY"))


def _slug_candidates(app: str) -> list[str]:
    """Deterministic slug guesses for an app name (Composio slugs are lowercase)."""
    base = app.lower().strip()
    compact = base.replace(".", "").replace(" ", "")
    underscored = base.replace(".", "").replace(" ", "_")
    first = base.split()[0].replace(".", "") if base.split() else compact
    # keep order, dedupe
    out: list[str] = []
    for s in (compact, underscored, first):
        if s and s not in out:
            out.append(s)
    return out


def _extract(tk: Any) -> dict[str, Any]:
    """Read slug / auth schemes / tool count defensively from a toolkit object or dict."""
    def field(obj: Any, *names: str) -> Any:
        for n in names:
            if isinstance(obj, dict) and n in obj:
                return obj[n]
            if hasattr(obj, n):
                return getattr(obj, n)
        return None

    meta = field(tk, "meta") or {}
    return {
        "in_catalog": True,
        "slug": field(tk, "slug", "name") or "",
        "auth_schemes": list(
            field(tk, "auth_schemes", "authSchemes")
            or field(meta, "auth_schemes", "authSchemes")
            or []
        ),
        "tool_count": field(tk, "tools_count", "toolsCount", "no_of_tools")
        or field(meta, "tools_count", "toolsCount"),
    }


def corroborate(app: str) -> dict[str, Any] | None:
    """Return a corroboration dict, or None if Composio is not configured.

    Shape when available:
      {"in_catalog": bool, "auth_schemes": [...], "tool_count": int|None, "slug": str}
    On SDK/network error returns {"error": "..."} so callers can log without crashing.
    """
    if not composio_available():
        return None
    try:
        from composio import Composio  # type: ignore

        client = Composio()  # reads COMPOSIO_API_KEY from env

        # 1) Direct lookup by slug (documented: toolkits.get(slug=...)).
        for slug in _slug_candidates(app):
            try:
                tk = client.toolkits.get(slug=slug)  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001 — slug miss / not found; try next
                continue
            if tk:
                return _extract(tk)

        # 2) Fallback: page the catalog (documented: toolkits.list(...)) and match
        #    on slug/name. Note: .list() has NO `search=` param in the v3 SDK.
        resp = client.toolkits.list()  # type: ignore[attr-defined]
        items = getattr(resp, "items", None) or getattr(resp, "data", None) or resp
        needle = app.lower().split()[0] if app.split() else app.lower()
        for tk in items or []:
            name = ""
            if isinstance(tk, dict):
                name = str(tk.get("slug") or tk.get("name") or "")
            else:
                name = str(getattr(tk, "slug", "") or getattr(tk, "name", ""))
            if needle and needle in name.lower():
                return _extract(tk)

        return {"in_catalog": False}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
