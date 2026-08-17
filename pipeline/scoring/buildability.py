"""
Deterministic buildability scoring.

This is the single source of truth for the buildability_score and the mapped
buildability label. The research agent never hand-writes a buildability label;
it fills the structured signals (auth, access, api, breadth, mcp, docs) and this
scorer derives score + label. That makes buildability reproducible and auditable:
given the same signals you always get the same verdict.

Score range: 0..100. Higher = easier to turn into an agent-callable toolkit today.

CALIBRATION NOTE (v2): the first weighting compressed 83/100 apps into "Easy"
because any self-serve product with a REST API cleared the threshold. That washed
out the free/paid/gated distinction that matters most for Composio prioritization.
v2 lowers the base, widens the gap between free/trial/paid/gated access, and
raises the Easy/Medium thresholds so tiers are discriminating:
  - Easy      = genuinely low-friction self-serve (free/trial) + real API
  - Medium    = self-serve but paid, or minor friction (app review/admin)
  - Hard      = significant gating (enterprise/partner/contact-sales/approval) but API exists
  - Not feasible = no public/hosted API (or unverifiable)

Rubric (additive, then clamped to 0..100):
  Base: 40

  Access model (credential accessibility — the dominant real-world factor):
    Self-serve free ................ +30
    Public/no credentials .......... +25
    Self-serve trial ............... +22
    Self-serve paid ................ +10
    Paid plan required .............  0
    Admin approval ................. -10
    Partner approval ............... -20
    Contact sales .................. -20
    Enterprise-only ................ -22
    No public API .................. -40
    Unknown / Other ................ -12

  API type (is there a machine-callable hosted surface):
    has REST or GraphQL ............ +8
    only SDK/CLI (no hosted API) ... -6
    None ........................... -30
    Unknown ........................ -8
    Webhooks present (bonus) ....... +2

  API breadth:
    Very broad ..................... +6
    Broad .......................... +4
    Moderate ....................... +2
    Narrow ......................... 0
    Not applicable ................. -5
    Unknown ........................ -3

  Auth method (self-serve-friendliness of the auth):
    API Key / Bearer / PAT present . +5
    OAuth 2.0 present .............. +3
    None / Unknown ................. -6

  MCP availability (accelerates toolkit creation):
    Official MCP ................... +10
    First-party documented MCP ..... +8
    Composio-supported ............. +6
    Community MCP .................. +3
    None found / Unknown ........... 0

  Documentation quality (doc_quality: good/moderate/poor/unknown):
    good ........................... +3
    moderate ....................... 0
    poor ........................... -6
    unknown ........................ -3

Label mapping:
    score >= 78 ......... Easy
    58 <= score < 78 .... Medium
    35 <= score < 58 .... Hard
    score < 35 .......... Not currently feasible
"""
from __future__ import annotations

from typing import Any

BASE = 40

ACCESS_POINTS = {
    "Self-serve free": 30,
    "Public/no credentials": 25,
    "Self-serve trial": 22,
    "Self-serve paid": 10,
    "Paid plan required": 0,
    "Admin approval": -10,
    "Partner approval": -20,
    "Contact sales": -20,
    "Enterprise-only": -22,
    "No public API": -40,
    "Unknown": -12,
    "Other": -12,
}

BREADTH_POINTS = {
    "Very broad": 6,
    "Broad": 4,
    "Moderate": 2,
    "Narrow": 0,
    "Not applicable": -5,
    "Unknown": -3,
}

MCP_POINTS = {
    "Official": 10,
    "First-party documented": 8,
    "Composio-supported": 6,
    "Community": 3,
    "None found": 0,
    "Unknown": 0,
}

DOC_POINTS = {"good": 3, "moderate": 0, "poor": -6, "unknown": -3}


def score_record(rec: dict[str, Any]) -> tuple[int, str, dict[str, int]]:
    """Return (score, label, breakdown)."""
    breakdown: dict[str, int] = {"base": BASE}
    score = BASE

    acc = rec.get("access_model", "Unknown")
    pts = ACCESS_POINTS.get(acc, -12)
    breakdown["access_model"] = pts
    score += pts

    api_types = set(rec.get("api_type", []) or [])
    if api_types & {"REST", "GraphQL"}:
        pts = 8
    elif api_types & {"SDK", "CLI"} and not (api_types & {"REST", "GraphQL"}):
        pts = -6
    elif "None" in api_types or not api_types:
        pts = -30
    elif "Unknown" in api_types:
        pts = -8
    else:
        pts = 0
    if "Webhooks" in api_types:
        pts += 2
    breakdown["api_type"] = pts
    score += pts

    pts = BREADTH_POINTS.get(rec.get("api_breadth", "Unknown"), -3)
    breakdown["api_breadth"] = pts
    score += pts

    auth = set(rec.get("auth_methods", []) or [])
    if auth & {"API Key", "Bearer Token", "Personal Access Token"}:
        pts = 5
    elif auth & {"OAuth 2.0"}:
        pts = 3
    elif not auth or auth <= {"None", "Unknown"}:
        pts = -6
    else:
        pts = 0
    breakdown["auth_methods"] = pts
    score += pts

    pts = MCP_POINTS.get(rec.get("mcp_status", "None found"), 0)
    breakdown["mcp_status"] = pts
    score += pts

    pts = DOC_POINTS.get((rec.get("doc_quality") or "unknown").lower(), -3)
    breakdown["doc_quality"] = pts
    score += pts

    score = max(0, min(100, score))

    if score >= 78:
        label = "Easy"
    elif score >= 58:
        label = "Medium"
    elif score >= 35:
        label = "Hard"
    else:
        label = "Not currently feasible"

    return score, label, breakdown


def apply_scoring(rec: dict[str, Any]) -> dict[str, Any]:
    """Overwrite buildability_score + buildability from signals. Mutates & returns."""
    score, label, breakdown = score_record(rec)
    rec["buildability_score"] = score
    rec["buildability"] = label
    rec["buildability_breakdown"] = breakdown
    return rec
