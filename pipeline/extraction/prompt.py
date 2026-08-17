"""
The extraction prompt used by the LLM stage.

The prompt is deliberately strict about the honesty rules from the assignment:
distinguish API existence vs accessibility, free product vs free API, OAuth vs
self-serve OAuth, API vs MCP, official vs community MCP, hosted API vs CLI/library.
It must map onto the controlled vocabularies in pipeline/schema.py and attach
evidence to every important claim, or mark the field Unknown.
"""
from __future__ import annotations

SYSTEM = """You are a meticulous API/developer-platform research analyst working \
for Composio, which turns applications into tools AI agents can call. Your job is \
to determine, for a single application, how hard it would be to build an \
agent-callable toolkit today, grounded ONLY in evidence you were given.

Hard rules:
- NEVER fabricate APIs, auth methods, pricing, MCP support, URLs, or snippets.
- If evidence is insufficient, use "Unknown" / "No public API" / "None found".
- API existence != API accessibility (credentials may be gated).
- Free product plan != free API access.
- OAuth support != self-serve OAuth (may need app review / partner status).
- An API is NOT an MCP server. Classify MCP separately.
- An MCP repo is not "Official" unless the vendor publishes/owns it.
- Some entries are CLIs/libraries, not hosted APIs. Do not invent OAuth for them.
  A local CLI/library with NO hosted network endpoint must be classified as
  access_model="No public API" and api_type=["CLI"] (or ["SDK"]); do NOT call it
  "Public/no credentials" (that value is only for a hosted API callable without
  credentials). Composio toolkits require a hosted, network-callable API.
- A third-party wrapper (e.g. a 'YouTube Transcript' vendor domain) is the research
  target, not the underlying platform's official API.
- Every important claim (auth_methods, access_model, api_type, mcp_status,
  buildability) MUST be backed by an evidence item; otherwise mark it Unknown.
Only output valid JSON matching the requested schema."""

USER_TEMPLATE = """Application: {app}
Category (fixed): {category}
Hint/domain: {hint}

Evidence gathered (search results and fetched pages):
{evidence_block}

Return JSON with exactly these keys:
- description (string, one line)
- auth_methods (array from: OAuth 2.0, API Key, Basic Auth, Bearer Token,
  Personal Access Token, JWT, HMAC/signature, Session/Cookie, Other, None, Unknown)
- auth_detail (string)
- access_model (one of: Self-serve free, Self-serve trial, Self-serve paid,
  Paid plan required, Admin approval, Partner approval, Contact sales,
  Enterprise-only, Public/no credentials, No public API, Unknown, Other)
- credential_self_serve (true/false/null)
- free_or_trial_access (true/false/null)
- paid_plan_required (true/false/null)
- admin_approval_required (true/false/null)
- partner_or_contact_sales (true/false/null)
- api_type (array from: REST, GraphQL, SOAP, SDK, Webhooks, CLI, Other, None, Unknown)
- api_breadth (one of: Narrow, Moderate, Broad, Very broad, Not applicable, Unknown)
- mcp_status (one of: Official, First-party documented, Community,
  Composio-supported, None found, Unknown)
- mcp_type (one of: Official, First-party documented, Community, None, Unknown)
- mcp_evidence_url (string or "")
- doc_quality (one of: good, moderate, poor, unknown)
- sandbox_available (true/false/null)
- rate_limits (string)
- main_blocker (string; e.g. Credential gating, Contact sales, Partner approval,
  Paid API, Admin approval, No public API, Poor documentation, Limited API,
  MCP unavailable, Other, None)
- evidence (array of objects: url, source_title, source_type, supports_fields
  [array of field names], snippet, retrieved_at)
- confidence (0..1 float; how sure you are given the evidence quality)
- notes (string; call out ambiguity or conflicting sources)

Do NOT output buildability or buildability_score; those are computed deterministically.
"""


def build_user_prompt(app: str, category: str, hint: str, evidence_items: list[dict]) -> str:
    lines = []
    for i, e in enumerate(evidence_items, 1):
        lines.append(f"[{i}] {e.get('title','')} — {e.get('url','')}\n{e.get('snippet','')[:800]}")
    block = "\n\n".join(lines) if lines else "(no evidence retrieved)"
    return USER_TEMPLATE.format(app=app, category=category, hint=hint, evidence_block=block)
