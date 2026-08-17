"""
Source discovery.

Given an app seed (name + hint), produce (a) a set of candidate authoritative
documentation URLs derived deterministically from the hint, and (b) a set of
targeted search queries. This is intentionally cheap and deterministic so the
expensive LLM/fetch stages get pointed at the right places.
"""
from __future__ import annotations

from urllib.parse import urlparse


def _norm_hint_to_url(hint: str) -> str | None:
    if not hint:
        return None
    token = hint.split()[0].strip().strip("/")
    if not token or "." not in token:
        return None
    if not token.startswith("http"):
        token = "https://" + token
    return token


def candidate_urls(app: str, hint: str) -> list[str]:
    urls: list[str] = []
    base = _norm_hint_to_url(hint)
    if base:
        urls.append(base)
        host = urlparse(base).netloc
        # common developer sub-paths / hosts
        root = ".".join(host.split(".")[-2:])
        urls.extend([
            f"https://{host}",
            f"https://developers.{root}",
            f"https://developer.{root}",
            f"https://docs.{root}",
            f"https://{root}/developers",
            f"https://{root}/docs",
            f"https://{root}/api",
        ])
    # dedupe, keep order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def search_queries(app: str, hint: str) -> list[str]:
    return [
        f"{app} API documentation authentication",
        f"{app} developer API OAuth API key",
        f"{app} API pricing free trial developer access",
        f"{app} official MCP server model context protocol",
        f"{app} REST API GraphQL webhooks docs",
        f"{app} composio toolkit",
    ]
