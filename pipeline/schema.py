"""
Strongly-typed schema + deterministic validation for the Composio toolkit
research pipeline.

Every record produced by the research agent is validated against this schema
BEFORE it is allowed into the dataset. Validation is deterministic and runs
independently of the LLM, so it catches hallucinated enums, missing evidence
for important claims, malformed URLs, and impossible field combinations.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Controlled vocabularies (enums). The LLM extraction stage MUST map free text
# onto these values; anything else is flagged by the validator.
# ---------------------------------------------------------------------------

CATEGORIES = {
    "CRM and Sales",
    "Support and Helpdesk",
    "Communications and Messaging",
    "Marketing, Ads, Email and Social",
    "Ecommerce",
    "Data, SEO and Scraping",
    "Developer, Infra and Data Platforms",
    "Productivity and Project Management",
    "Finance and Fintech",
    "AI, Research and Media-native",
}

AUTH_METHODS = {
    "OAuth 2.0",
    "API Key",
    "Basic Auth",
    "Bearer Token",
    "Personal Access Token",
    "JWT",
    "HMAC/signature",
    "Session/Cookie",
    "Other",
    "None",
    "Unknown",
}

ACCESS_MODELS = {
    "Self-serve free",
    "Self-serve trial",
    "Self-serve paid",
    "Paid plan required",
    "Admin approval",
    "Partner approval",
    "Contact sales",
    "Enterprise-only",
    "Public/no credentials",
    "No public API",
    "Unknown",
    "Other",
}

API_TYPES = {
    "REST",
    "GraphQL",
    "SOAP",
    "SDK",
    "Webhooks",
    "CLI",
    "Other",
    "None",
    "Unknown",
}

API_BREADTH = {
    "Narrow",
    "Moderate",
    "Broad",
    "Very broad",
    "Not applicable",
    "Unknown",
}

MCP_STATUS = {
    "Official",
    "First-party documented",
    "Community",
    "Composio-supported",
    "None found",
    "Unknown",
}

MCP_TYPE = {"Official", "First-party documented", "Community", "None", "Unknown"}

BUILDABILITY = {"Easy", "Medium", "Hard", "Not currently feasible"}

VERIFICATION_STATUS = {
    "unverified",
    "auto-validated",
    "second-pass",
    "composio-corroborated",
    "human-verified",
    "conflict",
}

SOURCE_TYPES = {
    "official_api_docs",
    "official_dev_docs",
    "official_auth_docs",
    "official_pricing",
    "official_mcp",
    "official_repo",
    "official_support",
    "secondary_docs",
    "composio_catalog",
    "search_result",
    "other",
}

BOOL_OR_NULL = (True, False, None)

_URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)


@dataclass
class Evidence:
    url: str
    source_title: str = ""
    source_type: str = "other"
    supports_fields: list[str] = field(default_factory=list)
    snippet: str = ""
    retrieved_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "source_title": self.source_title,
            "source_type": self.source_type,
            "supports_fields": self.supports_fields,
            "snippet": self.snippet,
            "retrieved_at": self.retrieved_at,
        }


# Fields whose conclusions are considered "important" and therefore REQUIRE
# at least one piece of attached evidence (unless the value is an explicit
# unknown/none marker).
# NOTE: 'buildability' is intentionally NOT here. It is derived deterministically
# by the scorer from the evidenced signals below, so it inherits its support
# transitively rather than needing its own citation.
IMPORTANT_FIELDS = {
    "auth_methods",
    "access_model",
    "api_type",
    "mcp_status",
}

REQUIRED_FIELDS = [
    "id",
    "app",
    "category",
    "hint",
    "description",
    "auth_methods",
    "auth_detail",
    "access_model",
    "api_type",
    "api_breadth",
    "mcp_status",
    "buildability",
    "buildability_score",
    "main_blocker",
    "evidence",
    "confidence",
    "verification_status",
]


def _is_unknown_value(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower() in {"unknown", "none", "none found", "no public api", "not applicable"}
    if isinstance(v, list):
        return len(v) == 0 or all(_is_unknown_value(x) for x in v)
    return False


def validate_record(rec: dict[str, Any]) -> list[str]:
    """Return a list of validation error strings. Empty list == valid."""
    errors: list[str] = []

    for f in REQUIRED_FIELDS:
        if f not in rec:
            errors.append(f"missing required field: {f}")

    if rec.get("category") not in CATEGORIES:
        errors.append(f"invalid category: {rec.get('category')!r}")

    for a in rec.get("auth_methods", []) or []:
        if a not in AUTH_METHODS:
            errors.append(f"invalid auth_method: {a!r}")

    if rec.get("access_model") not in ACCESS_MODELS:
        errors.append(f"invalid access_model: {rec.get('access_model')!r}")

    for t in rec.get("api_type", []) or []:
        if t not in API_TYPES:
            errors.append(f"invalid api_type: {t!r}")

    if rec.get("api_breadth") not in API_BREADTH:
        errors.append(f"invalid api_breadth: {rec.get('api_breadth')!r}")

    if rec.get("mcp_status") not in MCP_STATUS:
        errors.append(f"invalid mcp_status: {rec.get('mcp_status')!r}")

    if rec.get("mcp_type") and rec.get("mcp_type") not in MCP_TYPE:
        errors.append(f"invalid mcp_type: {rec.get('mcp_type')!r}")

    if rec.get("buildability") not in BUILDABILITY:
        errors.append(f"invalid buildability: {rec.get('buildability')!r}")

    if rec.get("verification_status") not in VERIFICATION_STATUS:
        errors.append(f"invalid verification_status: {rec.get('verification_status')!r}")

    for b in ("credential_self_serve", "free_or_trial_access", "paid_plan_required",
              "admin_approval_required", "partner_or_contact_sales", "sandbox_available"):
        if b in rec and rec[b] not in BOOL_OR_NULL:
            errors.append(f"{b} must be true/false/null, got {rec[b]!r}")

    conf = rec.get("confidence")
    if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
        errors.append(f"confidence must be 0..1, got {conf!r}")

    score = rec.get("buildability_score")
    if not isinstance(score, (int, float)) or not (0 <= score <= 100):
        errors.append(f"buildability_score must be 0..100, got {score!r}")

    # Evidence must exist and be well formed for important claims.
    evidence = rec.get("evidence", []) or []
    for ev in evidence:
        url = ev.get("url", "")
        if not _URL_RE.match(url or ""):
            errors.append(f"invalid evidence url: {url!r}")
        if ev.get("source_type") and ev["source_type"] not in SOURCE_TYPES:
            errors.append(f"invalid source_type: {ev['source_type']!r}")

    supported = set()
    for ev in evidence:
        supported.update(ev.get("supports_fields", []) or [])

    for f in IMPORTANT_FIELDS:
        if _is_unknown_value(rec.get(f)):
            continue  # explicit unknowns don't need evidence
        if f not in supported:
            errors.append(f"important field '{f}' has no supporting evidence")

    # Impossible / suspicious combinations.
    if rec.get("access_model") == "No public API" and (rec.get("api_type") or []) not in ([], ["None"], ["Unknown"]):
        if any(t not in ("None", "Unknown", "CLI", "SDK") for t in rec.get("api_type", [])):
            errors.append("access_model=No public API but api_type lists a hosted API type")

    if rec.get("mcp_status") in ("Official", "First-party documented") and not rec.get("mcp_evidence_url"):
        errors.append("official/first-party MCP claimed without mcp_evidence_url")

    if rec.get("buildability") == "Not currently feasible" and rec.get("buildability_score", 0) >= 50:
        errors.append("buildability 'Not currently feasible' but score >= 50 (rubric mismatch)")

    return errors
