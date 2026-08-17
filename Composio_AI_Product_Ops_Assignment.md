# Composio — AI Product Ops Intern Take-Home Assignment

## Context

Composio turns apps into tools that AI agents can call. Before Composio builds a toolkit for an app, it researches:

- What authentication the app uses
- Whether credentials are self-serve or gated
- Whether credentials can be obtained for free or on a trial
- Whether a paid plan, admin approval, partnership, or contact-sales process is required
- What API surface exists
- Whether the API is REST, GraphQL, or another type
- Approximately how broad the API surface is
- Whether the app can be an MCP server or has an existing MCP
- Whether it could be an agent-callable toolkit today
- What the main blocker is

Doing this manually across hundreds of apps does not scale. This assignment is a small, real version of that problem.

---

# The Task

You are given a list of **100 apps**.

For each app, research and capture:

1. **Category**
2. **What it does in one line**
3. **Auth method(s)** — OAuth2, API key, Basic, token, or other
4. **Self-serve vs gated** — can a developer get credentials themselves for free or on a trial, or does it require a paid plan, admin approval, partnership, or contact-sales process?
5. **API surface** — documented public REST / GraphQL, roughly how broad, and any existing MCP
6. **Buildability verdict** — could this be an agent toolkit today, and what is the main blocker if not?
7. **Evidence** — the documentation URL / article supporting each answer

## The Actual Point

Do not just produce 100 rows.

**Find the patterns.**

Cluster the results and explain:

- Which auth methods dominate
- Which categories are self-serve vs gated
- The most common blockers
- Where the easy wins are
- What needs outreach

**Insight over raw table.**

---

# Agent Requirement

**Do it with an agent, not by hand.**

Build an agent, script, or pipeline that performs the research across all 100 apps.

Using Composio's own SDK and MCP to build it is in the spirit of the role.

The project should explain:

- What the agent does
- How the research pipeline works
- Where a human was needed
- What automation was used
- What verification loops were implemented

---

# Accuracy and Verification

**Verify your accuracy.**

Sample the 100 apps and cross-check the agent's answers against real documentation by hand.

Report:

- Where the agent was right
- Where the agent was wrong
- How the errors were detected
- How the results were corrected
- How accuracy changed after verification

Build real verification loops using:

- Agent research
- Browser/documentation research
- Other appropriate automated means
- Human checks

Show at the end how the verification process improved confidence/accuracy.

**Accuracy is what matters most.**

If an app is difficult to research, gated, unavailable, or the agent gets something wrong, report it honestly.

---

# Deliverable

The complete assignment must be presented as a **single self-explanatory HTML page or slideshow**.

A reviewer should understand the work in approximately two minutes without narration.

The final artifact must clearly show:

## 1. Findings

A clean, skimmable table/matrix containing the 100 apps and the important research fields.

## 2. Patterns

Headline findings and clusters across the dataset.

## 3. Agent

What was built, how the workflow works, and where a human was needed.

## 4. Proof

The app/project itself, with a live link or runnable trigger where appropriate.

## 5. Verification

Accuracy checks, sample results, hits, misses, corrections, and methodology.

Show both:

- The final output
- The process/workflow behind it

Make the result easy for both an agent and a human to consume.

---

# Constraints and Honesty

Use AI tooling freely — that is the job.

However:

- Understand and be able to explain everything submitted.
- The interview will probe the implementation and methodology.
- Do not fabricate research results.
- Do not fabricate evidence.
- Do not fabricate verification.
- Do not fabricate accuracy numbers.
- Do not claim an app is self-serve if credentials are actually gated.
- Do not confuse a free product plan with free API access.
- Do not confuse an API with an MCP server.
- If an app is gated behind payment or partnership, saying so with evidence is the correct finding.
- You do not need paid accounts for apps.

---

# What to Submit

Submit:

1. **A live link** to the deployed HTML page / case study
2. **A link to the source repository**
3. A short **README** explaining how to run the research agent
4. The complete research set of 100 apps
5. Evidence and verification information

---

# Research Set — 100 Apps

## 1. CRM and Sales

| # | App | Website / Hint |
|---|---|---|
| 1 | Salesforce | salesforce.com |
| 2 | HubSpot | hubspot.com |
| 3 | Pipedrive | pipedrive.com |
| 4 | Attio | attio.com |
| 5 | Twenty | twenty.com (open-source CRM) |
| 6 | Podio | podio.com |
| 7 | Zoho CRM | zoho.com/crm |
| 8 | Close | close.com |
| 9 | Copper | copper.com |
| 10 | DealCloud | api.docs.dealcloud.com |

## 2. Support and Helpdesk

| # | App | Website / Hint |
|---|---|---|
| 11 | Zendesk | zendesk.com |
| 12 | Intercom | intercom.com |
| 13 | Freshdesk | freshdesk.com |
| 14 | Front | front.com |
| 15 | Pylon | usepylon.com |
| 16 | LiveAgent | liveagent.com |
| 17 | Plain | plain.com |
| 18 | Help Scout | helpscout.com |
| 19 | Gorgias | gorgias.com |
| 20 | Gladly | gladly.com |

## 3. Communications and Messaging

| # | App | Website / Hint |
|---|---|---|
| 21 | Slack | slack.com |
| 22 | Twilio | twilio.com |
| 23 | Zoho Cliq | zoho.com/cliq |
| 24 | Lark (Larksuite) | open.larksuite.com |
| 25 | Pumble | pumble.com |
| 26 | Discord | discord.com |
| 27 | Telegram | core.telegram.org |
| 28 | WhatsApp Business | developers.facebook.com/docs/whatsapp |
| 29 | Aircall | aircall.io |
| 30 | Vonage | developer.vonage.com |

## 4. Marketing, Ads, Email and Social

| # | App | Website / Hint |
|---|---|---|
| 31 | Google Ads | developers.google.com/google-ads |
| 32 | Meta Ads | developers.facebook.com/docs/marketing-apis |
| 33 | LinkedIn Ads | learn.microsoft.com/linkedin/marketing |
| 34 | GoHighLevel | highlevel.stoplight.io |
| 35 | Mailchimp | mailchimp.com/developer |
| 36 | Klaviyo | developers.klaviyo.com |
| 37 | systeme.io | systeme.io (funnel builder) |
| 38 | Pinterest | developers.pinterest.com |
| 39 | Threads (Meta) | developers.facebook.com/docs/threads |
| 40 | SendGrid | sendgrid.com |

## 5. Ecommerce

| # | App | Website / Hint |
|---|---|---|
| 41 | Shopify | shopify.dev |
| 42 | WooCommerce | woocommerce.com/document/woocommerce-rest-api |
| 43 | BigCommerce | developer.bigcommerce.com |
| 44 | Salesforce Commerce Cloud | developer.salesforce.com/docs/commerce |
| 45 | Magento (Adobe Commerce) | developer.adobe.com/commerce |
| 46 | Squarespace | developers.squarespace.com |
| 47 | Ecwid | api-docs.ecwid.com |
| 48 | Gumroad | gumroad.com/api |
| 49 | Amazon Selling Partner | developer-docs.amazon.com/sp-api |
| 50 | fanbasis | fanbasis.com |

## 6. Data, SEO and Scraping

| # | App | Website / Hint |
|---|---|---|
| 51 | DataForSEO | docs.dataforseo.com |
| 52 | SE Ranking | seranking.com/api |
| 53 | Ahrefs | ahrefs.com/api |
| 54 | MrScraper | docs.mrscraper.com |
| 55 | Apify | docs.apify.com |
| 56 | Firecrawl | firecrawl.dev |
| 57 | Bright Data | brightdata.com |
| 58 | Sherlock | github.com/sherlock-project/sherlock |
| 59 | Waterfall.io | waterfall.io (contact/company intel) |
| 60 | Clay | clay.com |

## 7. Developer, Infra and Data Platforms

| # | App | Website / Hint |
|---|---|---|
| 61 | GitHub | docs.github.com/rest |
| 62 | Vercel | vercel.com/docs/rest-api |
| 63 | Netlify | docs.netlify.com/api |
| 64 | Cloudflare | developers.cloudflare.com/api |
| 65 | Supabase | supabase.com/docs |
| 66 | Neo4j | neo4j.com/docs/api |
| 67 | Snowflake | docs.snowflake.com |
| 68 | MongoDB Atlas | mongodb.com/docs/atlas/api |
| 69 | Datadog | docs.datadoghq.com/api |
| 70 | Sentry | docs.sentry.io/api |

## 8. Productivity and Project Management

| # | App | Website / Hint |
|---|---|---|
| 71 | Notion | developers.notion.com |
| 72 | Airtable | airtable.com/developers |
| 73 | Linear | developers.linear.app |
| 74 | Jira | developer.atlassian.com |
| 75 | Asana | developers.asana.com |
| 76 | Monday.com | developer.monday.com |
| 77 | ClickUp | clickup.com/api |
| 78 | Coda | coda.io/developers |
| 79 | Smartsheet | smartsheet.com/developers |
| 80 | Harvest | harvestapp.com (help.getharvest.com/api-v2) |

## 9. Finance and Fintech

| # | App | Website / Hint |
|---|---|---|
| 81 | Stripe | stripe.com/docs/api |
| 82 | Plaid | plaid.com/docs |
| 83 | Binance | binance-docs.github.io |
| 84 | Paygent Connect | paygent (NMI-powered) |
| 85 | iPayX | ipayx.ai/docs |
| 86 | QuickBooks | developer.intuit.com |
| 87 | Xero | developer.xero.com |
| 88 | Brex | developer.brex.com |
| 89 | Ramp | docs.ramp.com |
| 90 | PitchBook | pitchbook.com (research API) |

## 10. AI, Research and Media-native

| # | App | Website / Hint |
|---|---|---|
| 91 | NotebookLM | cloud.google.com/gemini (Enterprise API) |
| 92 | Otter AI | help.otter.ai (MCP server) |
| 93 | Fathom | fathom.video |
| 94 | Consensus | consensus.app (OAuth requested) |
| 95 | Reducto | reducto.ai (document parsing) |
| 96 | Devin | docs.devin.ai (MCP) |
| 97 | higgsfield | higgsfield.ai/cli (content suite) |
| 98 | Mermaid CLI | github.com/mermaid-js/mermaid-cli |
| 99 | YouTube Transcript | transcriptapi.com |
| 100 | Grain | grain.com (meeting notes) |

---

# Expected Research Questions Per App

For each of the 100 applications, answer as accurately as possible:

### A. Category
Which of the ten provided categories does it belong to?

### B. One-line description
What does the application do?

### C. Authentication
What authentication methods are supported?

Examples:

- OAuth2
- API key
- Basic authentication
- Bearer token
- Personal access token
- JWT
- Other

### D. Credential/access model
Can a developer get credentials themselves?

Classify as appropriate:

- Self-serve free
- Self-serve trial
- Self-serve paid
- Paid plan required
- Admin approval
- Partner approval
- Contact sales
- Enterprise-only
- Public/no credentials
- No public API
- Unknown

### E. API
What public API exists?

Identify:

- REST
- GraphQL
- SOAP
- SDK
- Webhooks
- CLI
- Other
- None
- Unknown

### F. API breadth
Estimate using evidence:

- Narrow
- Moderate
- Broad
- Very broad
- Not applicable
- Unknown

### G. MCP
Determine whether there is:

- Official MCP
- First-party documented MCP
- Community MCP
- Composio-supported MCP/toolkit
- None found
- Unknown

### H. Buildability
Could this realistically be an agent toolkit today?

Classify:

- Easy
- Medium
- Hard
- Not currently feasible

### I. Main blocker
What is the main obstacle?

Examples:

- Credential gating
- Contact sales
- Partner approval
- Paid API
- Admin approval
- No public API
- Poor documentation
- Limited API
- MCP unavailable
- Other
- None

### J. Evidence
Provide the strongest available documentation URL(s).

---

# Important Research Principles

## API existence ≠ API accessibility

An app can have a public API while developer credentials are gated.

## Free product ≠ free API

Do not assume a free SaaS plan includes API access.

## OAuth support ≠ self-serve OAuth

OAuth may require application approval or partner access.

## API ≠ MCP

Treat API and MCP as separate properties.

## Official MCP ≠ community MCP

Clearly distinguish first-party and third-party implementations.

## Product website ≠ developer documentation

Prefer official developer/API documentation whenever possible.

## Do not guess

If evidence is unavailable, report uncertainty honestly.

---

# Expected Pattern Analysis

After researching the 100 apps, analyze:

1. Authentication distribution
2. Access/gating distribution
3. API type distribution
4. API breadth
5. MCP availability
6. Buildability distribution
7. Buildability by category
8. Access model by category
9. Common blockers
10. Easy-win opportunities
11. Outreach opportunities

The final conclusions must be derived from the actual dataset.

---

# Verification Expectations

The verification section should show:

- Sample size
- Apps sampled
- Fields checked
- Agent result
- Verified result
- Correct/incorrect status
- Evidence
- Error type
- Correction

Where possible, compare:

**Pass 1 → Verification → Corrected Pass → Final Accuracy**

Do not invent an accuracy improvement.

Show real misses honestly.

---

# Final Case Study Requirements

The single HTML page/slideshow should contain:

1. Title / problem
2. Key metrics
3. Headline findings
4. Pattern visualizations
5. Easy wins
6. Outreach/gated cases
7. 100-app matrix
8. Agent workflow
9. Agent vs human responsibilities
10. Verification methodology
11. Accuracy
12. Real failures/misses
13. Limitations
14. Repository link
15. Live deployment link
16. Instructions / reproducibility information

The page should be understandable in approximately two minutes without narration.

---

# Submission Standard

The final project should be:

- Accurate
- Evidence-backed
- Reproducible
- Honest
- Clearly presented
- Agent-driven
- Properly verified
- Professionally designed

The goal is not to make the agent appear perfect.

The goal is to demonstrate that the research workflow is scalable and trustworthy.
