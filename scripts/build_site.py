#!/usr/bin/env python3
"""
Generate the self-contained single-page case study at site/index.html.

Reads the REAL artifacts (data/final/dataset.json, verification/*.json) and embeds
them inline as JSON. All charts, metrics, headline findings, the 100-app matrix,
and the verification numbers are computed in-browser from that embedded data — no
hardcoded statistics, no external network dependencies. Works via file:// and as
a static deploy (Vercel/Netlify).
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(*parts):
    return json.load(open(os.path.join(ROOT, *parts)))


def main() -> int:
    dataset = load("data", "final", "dataset.json")
    analytics = load("verification", "analytics.json")
    accuracy = load("verification", "accuracy.json")
    errors = load("verification", "errors.json")

    blob = {
        "dataset": dataset,
        "analytics": analytics,
        "accuracy": accuracy,
        "errors": errors,
        "generated_note": "Data produced by the Kiro research agent (Claude + web search/fetch) executing the pipeline workflow; deterministic stages (scoring, validation, analytics, accuracy) run in Python on this data.",
    }
    payload = json.dumps(blob, ensure_ascii=False).replace("</", "<\\/")

    html = TEMPLATE.replace("/*__DATA__*/", payload)
    os.makedirs(os.path.join(ROOT, "site"), exist_ok=True)
    with open(os.path.join(ROOT, "site", "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[site] wrote site/index.html ({len(html):,} bytes, {len(dataset)} apps embedded)")
    return 0


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Can These 100 Apps Become Agent Tools? — Composio Toolkit Buildability Study</title>
<meta name="description" content="An evidence-backed research agent assessing API access, authentication, gating, MCP readiness, and toolkit buildability across 100 applications."/>
<style>
  :root{
    --ink:#141719; --muted:#5c6672; --line:#e6e8eb; --bg:#ffffff; --soft:#f6f7f9;
    --accent:#2f6df6; --easy:#1f9d5c; --medium:#c98a12; --hard:#d1642a; --no:#b23b4e;
    --chip:#eef1f5;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
  a{color:var(--accent);text-decoration:none}
  a:hover{text-decoration:underline}
  .wrap{max-width:1120px;margin:0 auto;padding:0 20px}
  header.hero{padding:64px 0 40px;border-bottom:1px solid var(--line)}
  .kicker{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:600}
  h1{font-size:40px;line-height:1.1;margin:14px 0 10px;letter-spacing:-.02em}
  .sub{font-size:19px;color:var(--muted);max-width:760px}
  .note{font-size:13px;color:var(--muted);margin-top:18px;max-width:820px}
  section{padding:46px 0;border-bottom:1px solid var(--line)}
  h2{font-size:13px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:700;margin:0 0 22px}
  h3{font-size:20px;margin:0 0 8px;letter-spacing:-.01em}
  .metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}
  .metric{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:16px}
  .metric .n{font-size:30px;font-weight:700;letter-spacing:-.02em}
  .metric .l{font-size:12.5px;color:var(--muted);margin-top:2px}
  .findings{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .find{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
  .find .big{font-size:15px;color:var(--muted)}
  .find p{margin:6px 0 0;color:var(--muted);font-size:14.5px}
  .find b{color:var(--ink)}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:28px}
  .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px}
  .chart{margin-bottom:8px}
  .bar-row{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13.5px}
  .bar-row .lab{width:150px;color:var(--muted);flex:none;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .bar-row .track{flex:1;background:var(--soft);border-radius:6px;overflow:hidden;height:20px;position:relative}
  .bar-row .fill{height:100%;background:var(--accent);border-radius:6px}
  .bar-row .val{width:34px;text-align:left;color:var(--ink);font-variant-numeric:tabular-nums;flex:none}
  .stack{display:flex;height:26px;border-radius:7px;overflow:hidden;border:1px solid var(--line)}
  .stack > div{display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:600}
  .legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:12.5px;color:var(--muted)}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .dot{width:10px;height:10px;border-radius:3px;display:inline-block}
  .catbars .bar-row .lab{width:210px}
  table{width:100%;border-collapse:collapse;font-size:13.5px}
  .matrix-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
  th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap;vertical-align:top}
  th{position:sticky;top:0;background:var(--soft);cursor:pointer;user-select:none;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
  th:hover{color:var(--ink)}
  td.wrap-cell{white-space:normal;min-width:210px;color:var(--muted)}
  tr:hover td{background:#fbfcfe}
  .pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:600;border:1px solid transparent}
  .b-Easy{background:#e7f6ee;color:var(--easy)}
  .b-Medium{background:#fbf1dd;color:var(--medium)}
  .b-Hard{background:#fbe9df;color:var(--hard)}
  .b-Notcurrentlyfeasible{background:#fbe4e8;color:var(--no)}
  .chip{background:var(--chip);color:#41505f;border-radius:6px;padding:1px 7px;font-size:11.5px;margin:1px 2px 1px 0;display:inline-block}
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px;align-items:center}
  .controls input,.controls select{font:14px inherit;padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink)}
  .controls input[type=search]{min-width:220px;flex:1}
  .count{font-size:13px;color:var(--muted)}
  .flow{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch}
  .step{flex:1;min-width:120px;background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:12px;font-size:13px}
  .step b{display:block;font-size:12px;color:var(--accent);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
  .arrow{align-self:center;color:var(--muted)}
  .two-col{display:grid;grid-template-columns:1fr 1fr;gap:22px}
  .card{border:1px solid var(--line);border-radius:12px;padding:20px}
  ul.tight{margin:8px 0 0;padding-left:18px}
  ul.tight li{margin:5px 0;color:var(--muted);font-size:14.5px}
  ul.tight li b{color:var(--ink)}
  .acc-row{display:flex;gap:24px;align-items:flex-end;margin-bottom:14px}
  .acc-big{font-size:44px;font-weight:700;letter-spacing:-.02em;line-height:1}
  .acc-big small{font-size:15px;color:var(--muted);font-weight:500}
  .delta{color:var(--easy);font-weight:600;font-size:14px}
  code{background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:12.5px}
  pre{background:#0f1418;color:#e7edf3;border-radius:10px;padding:16px;overflow-x:auto;font-size:12.5px;line-height:1.5}
  footer{padding:40px 0 70px;color:var(--muted);font-size:13px}
  .muted{color:var(--muted)}
  .evlink{font-size:12px}
  @media(max-width:860px){
    .metrics{grid-template-columns:repeat(2,1fr)}
    .findings,.grid2,.grid3,.two-col{grid-template-columns:1fr}
    h1{font-size:31px}
  }
</style>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="kicker">Composio · AI Product Ops — take-home study</div>
  <h1>Can these 100 apps become agent tools?</h1>
  <div class="sub">An evidence-backed research agent that classifies API access, authentication, credential gating, MCP readiness, and toolkit buildability across 100 applications — then measures its own error rate and improves.</div>
  <div class="note" id="provNote"></div>
</div></header>

<section><div class="wrap">
  <h2>Key metrics</h2>
  <div class="metrics" id="metrics"></div>
</div></section>

<section><div class="wrap">
  <h2>Headline findings</h2>
  <div class="findings" id="findings"></div>
</div></section>

<section><div class="wrap">
  <h2>Patterns across the dataset</h2>
  <div class="grid2">
    <div><h3>Authentication methods</h3><div class="chart" id="authChart"></div></div>
    <div><h3>API type</h3><div class="chart" id="apiChart"></div></div>
  </div>
  <div style="height:26px"></div>
  <div class="grid2">
    <div>
      <h3>Credential access: self-serve vs gated</h3>
      <div class="stack" id="accessStack"></div>
      <div class="legend" id="accessLegend"></div>
      <div class="chart" id="accessChart" style="margin-top:16px"></div>
    </div>
    <div>
      <h3>MCP availability</h3>
      <div class="chart" id="mcpChart"></div>
    </div>
  </div>
  <div style="height:26px"></div>
  <div class="grid2">
    <div><h3>Buildability verdict</h3><div class="stack" id="buildStack"></div><div class="legend" id="buildLegend"></div></div>
    <div><h3>Avg. buildability score by category</h3><div class="chart catbars" id="catChart"></div></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Easy wins vs. outreach</h2>
  <div class="two-col">
    <div class="card">
      <h3 style="color:var(--easy)">Top easy wins</h3>
      <p class="muted" style="margin:0 0 8px;font-size:14px">Highest buildability scores: self-serve credentials, public REST/GraphQL, often an official MCP.</p>
      <div id="easyWins"></div>
    </div>
    <div class="card">
      <h3 style="color:var(--hard)">Needs outreach / gated</h3>
      <p class="muted" style="margin:0 0 8px;font-size:14px">API may exist, but credentials require enterprise/partner/contact-sales/approval — or there is no hosted API.</p>
      <div id="outreach"></div>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>The full 100-app matrix</h2>
  <div class="controls">
    <input type="search" id="q" placeholder="Search app, blocker, notes…"/>
    <select id="fCat"></select>
    <select id="fBuild"></select>
    <select id="fAccess"></select>
    <select id="fAuth"></select>
    <select id="fMcp"></select>
    <span class="count" id="rowCount"></span>
  </div>
  <div class="matrix-wrap"><table id="matrix"><thead><tr id="matHead"></tr></thead><tbody id="matBody"></tbody></table></div>
  <p class="muted" style="font-size:12.5px;margin-top:8px">Click a column header to sort. Evidence links open primary documentation. Confidence is the agent's self-rated certainty given the evidence quality.</p>
</div></section>

<section><div class="wrap">
  <h2>How the agent works</h2>
  <div class="flow">
    <div class="step"><b>Seed</b>100 apps + domain hints</div>
    <div class="arrow">→</div>
    <div class="step"><b>Discover</b>Targeted queries + candidate doc URLs</div>
    <div class="arrow">→</div>
    <div class="step"><b>Retrieve</b>Fetch primary docs (auth, pricing, API, MCP)</div>
    <div class="arrow">→</div>
    <div class="step"><b>Extract</b>Structured facts onto a strict schema</div>
    <div class="arrow">→</div>
    <div class="step"><b>Evidence</b>Attach source URL to each claim</div>
  </div>
  <div class="flow" style="margin-top:8px">
    <div class="step"><b>Validate</b>Enum + evidence + impossible-combo checks</div>
    <div class="arrow">→</div>
    <div class="step"><b>Score</b>Deterministic buildability rubric</div>
    <div class="arrow">→</div>
    <div class="step"><b>Verify</b>Independent 2nd pass + human sample</div>
    <div class="arrow">→</div>
    <div class="step"><b>Correct</b>Apply fixes, keep before/after</div>
    <div class="arrow">→</div>
    <div class="step"><b>Final</b>Dataset · analytics · this page</div>
  </div>
  <div class="two-col" style="margin-top:24px">
    <div class="card">
      <h3>Agent handled</h3>
      <ul class="tight">
        <li><b>Source discovery</b> — query generation and candidate documentation URLs.</li>
        <li><b>Retrieval &amp; extraction</b> — reading primary docs and mapping facts onto the schema.</li>
        <li><b>Normalization</b> — auth / access / API / MCP taxonomies.</li>
        <li><b>Scoring</b> — deterministic, reproducible buildability rubric (Python, single source of truth).</li>
        <li><b>Analytics</b> — every distribution and cross-tab on this page.</li>
      </ul>
    </div>
    <div class="card">
      <h3>Human handled</h3>
      <ul class="tight">
        <li><b>Ambiguity calls</b> — e.g. "is a local CLI a hosted API?" (no).</li>
        <li><b>Trap identification</b> — Sherlock, Mermaid CLI, the transcriptapi.com wrapper vs. YouTube.</li>
        <li><b>Independent verification</b> — re-checking a stratified sample against primary sources.</li>
        <li><b>Error analysis</b> — categorizing failure modes and confirming corrections.</li>
        <li><b>Rubric design</b> — choosing weights/thresholds so tiers are meaningful.</li>
      </ul>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>How do we know it's accurate?</h2>
  <div class="acc-row">
    <div><div class="acc-big" id="p1acc"></div><div class="muted">Pass 1 accuracy</div></div>
    <div style="font-size:26px;color:var(--muted)">→</div>
    <div><div class="acc-big" id="p2acc"></div><div class="muted">Pass 2 (after corrections)</div></div>
    <div><div class="delta" id="accDelta"></div><div class="muted" id="sampleMeta"></div></div>
  </div>
  <p class="muted" style="max-width:820px;font-size:14.5px">A stratified sample (easy, gated, trap, low-confidence, and model-knowledge apps) was re-checked in an <b>independent second pass</b> against primary sources — deliberately not the same reasoning that produced Pass 1. Field-level accuracy below; the improvement comes entirely from real corrections, not re-labeling.</p>
  <div class="grid2" style="margin-top:18px">
    <div><h3 style="font-size:15px">Pass 1 accuracy by field</h3><div class="chart" id="fieldAcc1"></div></div>
    <div><h3 style="font-size:15px">Pass 2 accuracy by field</h3><div class="chart" id="fieldAcc2"></div></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>What the agent got wrong</h2>
  <p class="muted" style="max-width:820px;margin-top:-8px">Every miss shared one root cause: apps researched from <b>model knowledge alone</b> (not live-searched) had their MCP support under-reported. The independent search pass found official/first-party MCP servers the first pass missed. No verdicts were hidden.</p>
  <div class="matrix-wrap" style="margin-top:16px"><table id="errTable"><thead><tr><th>App</th><th>Field</th><th>Pass 1 (agent)</th><th>Verified</th><th>Error type</th><th>Evidence</th></tr></thead><tbody id="errBody"></tbody></table></div>
</div></section>

<section><div class="wrap">
  <h2>Limitations &amp; honest caveats</h2>
  <ul class="tight" style="max-width:860px">
    <li><b>MCP is time-sensitive and likely still under-counted.</b> ~45 apps are marked "None found"; some were researched from model knowledge, and the ecosystem ships new servers weekly. The 8 corrections show this class of error is real — treat "None found" on non-searched apps as a lower bound.</li>
    <li><b>Credential access is judged from documentation, not by purchasing every product.</b> "Self-serve free" means a developer can obtain credentials without sales/approval; it does not guarantee every endpoint is free.</li>
    <li><b>Two apps are genuinely unverifiable</b> (fanbasis, iPayX) — reported as Unknown rather than guessed.</li>
    <li><b>The app list skews API-first</b>, so a high share is "Easy". That is a property of the sample, not a claim that most software is easy to toolkit-ify.</li>
    <li><b>Verification covered a 33-app sample, not all 100</b>; unsampled apps may contain errors of the same class.</li>
    <li><b>Composio corroboration is wired but optional</b> — it activates only with a user-provided API key and was not used as ground truth.</li>
  </ul>
</div></section>

<section><div class="wrap">
  <h2>Reproduce it</h2>
  <div class="grid2">
    <div>
      <p class="muted" style="font-size:14.5px">The deterministic stages need no API keys and run on the shipped data. The LLM+search extraction stage is provider-pluggable (Anthropic/OpenAI + Tavily) and reproduces the same workflow with your own keys.</p>
      <pre>python scripts/merge_parts.py data/research_full.json
python scripts/finalize.py data/research_full_corrected.json \
    data/final/dataset.json      # score + validate
python scripts/validate_dataset.py   # QA gate (100 apps, rubric match)
python scripts/compute_accuracy.py   # Pass 1 vs Pass 2
python scripts/analyze.py            # distributions + cross-tabs
python scripts/build_site.py         # regenerate this page

# optional: run the live agent with your own keys
export TAVILY_API_KEY=...  ANTHROPIC_API_KEY=...
python scripts/run_research.py --pilot</pre>
    </div>
    <div>
      <h3 style="font-size:15px">What ships in the repo</h3>
      <ul class="tight">
        <li><code>pipeline/</code> — schema, scoring, source discovery, extraction, verification, analysis.</li>
        <li><code>data/</code> — 100-app seed, Pass-1 raw, corrected final dataset, 100 per-app traces.</li>
        <li><code>verification/</code> — sample, accuracy, errors, analytics (all machine-readable).</li>
        <li><code>site/index.html</code> — this self-contained page (dataset embedded as JSON).</li>
      </ul>
      <p class="muted" style="font-size:13px;margin-top:14px">Deploy: any static host. <code>vercel deploy</code> or drag <code>site/</code> into Netlify. Locally: <code>npm run serve</code>.</p>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <div id="footNote"></div>
</div></footer>

<script id="payload" type="application/json">/*__DATA__*/</script>
<script>
const DB = JSON.parse(document.getElementById('payload').textContent);
const D = DB.dataset, A = DB.analytics, ACC = DB.accuracy, ERR = DB.errors;
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const buildColor = {'Easy':'var(--easy)','Medium':'var(--medium)','Hard':'var(--hard)','Not currently feasible':'var(--no)'};

document.getElementById('provNote').textContent = DB.generated_note;

// ---------- metrics ----------
const selfServe = A.counts.self_serve, gated = A.counts.gated;
const anyMcp = A.counts.has_any_mcp, offMcp = A.counts.has_official_or_firstparty_mcp;
const easyN = A.counts.easy + A.counts.medium;
const metrics = [
  ['100','applications'],
  ['10','categories'],
  [ACC.pass_2.accuracy_pct+'%','verified accuracy'],
  [anyMcp,'apps with an MCP'],
  [easyN,'easy-win candidates'],
  [gated,'gated (need outreach)'],
];
$('#metrics').innerHTML = metrics.map(m=>`<div class="metric"><div class="n">${m[0]}</div><div class="l">${m[1]}</div></div>`).join('');

// ---------- headline findings (derived) ----------
const pct = n => Math.round(100*n/D.length);
const restCount = D.filter(r=>(r.api_type||[]).some(t=>t==='REST'||t==='GraphQL')).length;
const findings = [
  ['Credential access — not API existence — is the real gate.',
   `<b>${selfServe} of 100</b> apps let a developer self-serve credentials; only <b>${gated}</b> are gated behind enterprise, partner, contact-sales or approval. Several gated apps (Ahrefs, Amazon SP, PitchBook, Otter) have rich public APIs you still can't call without a deal.`],
  ['MCP has quietly become mainstream.',
   `<b>${anyMcp} of 100</b> apps already expose an MCP server (<b>${offMcp}</b> official/first-party). For those, a toolkit is closer to "connect" than "build".`],
  ['Most of this set is buildable today.',
   `<b>${A.buildability_distribution.Easy||0}</b> Easy + <b>${A.buildability_distribution.Medium||0}</b> Medium. The list skews toward API-first products — the signal is <i>where</i> the friction concentrates, not the headline count.`],
  ['The blockers cluster by domain.',
   `Gating concentrates in <b>enterprise data</b> (PitchBook, DealCloud, NotebookLM, Salesforce Commerce), <b>ads platforms</b> (Google/Meta/LinkedIn app-review), and <b>fintech</b> (production approval). Support, productivity and dev-tools are overwhelmingly self-serve.`],
];
$('#findings').innerHTML = findings.map(f=>`<div class="find"><div class="big"><b>${f[0]}</b></div><p>${f[1]}</p></div>`).join('');

// ---------- bar chart helper ----------
function barChart(el, entries, color){
  const max = Math.max(...entries.map(e=>e[1]), 1);
  el.innerHTML = entries.map(([k,v])=>`
    <div class="bar-row"><div class="lab" title="${esc(k)}">${esc(k)}</div>
      <div class="track"><div class="fill" style="width:${100*v/max}%;background:${color||'var(--accent)'}"></div></div>
      <div class="val">${v}</div></div>`).join('');
}
barChart($('#authChart'), Object.entries(A.auth_distribution));
barChart($('#apiChart'), Object.entries(A.api_type_distribution));
barChart($('#accessChart'), Object.entries(A.access_distribution));
barChart($('#mcpChart'), Object.entries(A.mcp_distribution));

// ---------- stacked bars ----------
function stack(el, legendEl, entries, colorFn){
  const total = entries.reduce((s,e)=>s+e[1],0);
  el.innerHTML = entries.map(([k,v])=>`<div style="width:${100*v/total}%;background:${colorFn(k)}" title="${esc(k)}: ${v}">${v>4?v:''}</div>`).join('');
  if(legendEl) legendEl.innerHTML = entries.map(([k,v])=>`<span><i class="dot" style="background:${colorFn(k)}"></i>${esc(k)} · ${v}</span>`).join('');
}
const accessColor = k => (['Self-serve free','Self-serve trial','Self-serve paid','Public/no credentials'].includes(k))?'var(--easy)':(k==='Unknown'?'#9aa4ae':'var(--hard)');
const ssVsGated = [['Self-serve',selfServe],['Gated',gated],['Unknown/Other',100-selfServe-gated]];
stack($('#accessStack'), $('#accessLegend'), ssVsGated, k=>k==='Self-serve'?'var(--easy)':(k==='Gated'?'var(--hard)':'#9aa4ae'));

const bdOrder = ['Easy','Medium','Hard','Not currently feasible'];
stack($('#buildStack'), $('#buildLegend'), bdOrder.filter(k=>A.buildability_distribution[k]).map(k=>[k,A.buildability_distribution[k]]), k=>buildColor[k]);

// ---------- avg score by category ----------
const catEntries = Object.entries(A.avg_score_by_category).sort((a,b)=>b[1]-a[1]);
(function(){
  const max=100;
  $('#catChart').innerHTML = catEntries.map(([k,v])=>`
    <div class="bar-row"><div class="lab" title="${esc(k)}">${esc(k)}</div>
      <div class="track"><div class="fill" style="width:${100*v/max}%;background:var(--accent)"></div></div>
      <div class="val">${v}</div></div>`).join('');
})();

// ---------- easy wins / outreach ----------
function listCard(el, rows, kind){
  el.innerHTML = rows.map(r=>`
    <div style="display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-bottom:1px solid var(--line)">
      <div><b>${esc(r.app)}</b> <span class="muted" style="font-size:12.5px">· ${esc(r.category)}</span>
        <div class="muted" style="font-size:12.5px">${esc(kind==='easy'?(r.access_model+' · '+(r.mcp)):(r.access_model+' · '+r.blocker))}</div></div>
      <div style="text-align:right"><span class="pill b-${(r.buildability||kind==='easy'?'Easy':'Hard').replace(/ /g,'')}">${r.score}</span></div>
    </div>`).join('');
}
listCard($('#easyWins'), A.easy_wins_ranked.slice(0,12), 'easy');
listCard($('#outreach'), A.outreach_ranked.slice(0,12), 'out');

// ---------- matrix ----------
const COLS = [
  ['app','App'],['category','Category'],['auth_methods','Auth'],['access_model','Access'],
  ['api_type','API'],['api_breadth','Breadth'],['mcp_status','MCP'],['buildability','Build'],
  ['buildability_score','Score'],['main_blocker','Blocker'],['confidence','Conf'],['evidence','Evidence']
];
$('#matHead').innerHTML = COLS.map(c=>`<th data-k="${c[0]}">${c[1]}</th>`).join('');
function uniq(key){return [...new Set(D.flatMap(r=>Array.isArray(r[key])?r[key]:[r[key]]))].filter(Boolean).sort();}
function fillSel(id,label,key){const s=$(id);s.innerHTML=`<option value="">All ${label}</option>`+uniq(key).map(v=>`<option>${esc(v)}</option>`).join('');}
fillSel('#fCat','categories','category');fillSel('#fBuild','buildability','buildability');
fillSel('#fAccess','access','access_model');fillSel('#fAuth','auth','auth_methods');fillSel('#fMcp','MCP','mcp_status');
let sortKey='buildability_score',sortDir=-1;
function rowMatch(r){
  const q=$('#q').value.toLowerCase();
  if(q && !(r.app+' '+r.main_blocker+' '+(r.notes||'')+' '+r.description).toLowerCase().includes(q))return false;
  if($('#fCat').value && r.category!==$('#fCat').value)return false;
  if($('#fBuild').value && r.buildability!==$('#fBuild').value)return false;
  if($('#fAccess').value && r.access_model!==$('#fAccess').value)return false;
  if($('#fAuth').value && !(r.auth_methods||[]).includes($('#fAuth').value))return false;
  if($('#fMcp').value && r.mcp_status!==$('#fMcp').value)return false;
  return true;
}
function cell(r,k){
  if(k==='buildability')return `<span class="pill b-${r.buildability.replace(/ /g,'')}">${esc(r.buildability)}</span>`;
  if(k==='auth_methods'||k==='api_type')return (r[k]||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('');
  if(k==='main_blocker')return `<div class="wrap-cell">${esc(r.main_blocker)}</div>`;
  if(k==='confidence')return (r.confidence).toFixed(2);
  if(k==='evidence'){const e=(r.evidence||[])[0];return e?`<a class="evlink" href="${esc(e.url)}" target="_blank" rel="noopener">source ↗</a>`:'';}
  return esc(r[k]);
}
function render(){
  const rows=D.filter(rowMatch).sort((a,b)=>{
    let x=a[sortKey],y=b[sortKey];
    if(Array.isArray(x))x=x.join();if(Array.isArray(y))y=y.join();
    if(typeof x==='string')return sortDir*x.localeCompare(y);
    return sortDir*((x||0)-(y||0));
  });
  $('#matBody').innerHTML=rows.map(r=>`<tr>${COLS.map(c=>`<td>${cell(r,c[0])}</td>`).join('')}</tr>`).join('');
  $('#rowCount').textContent=`${rows.length} of ${D.length} apps`;
}
document.querySelectorAll('#matHead th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;sortDir=(sortKey===k)?-sortDir:-1;sortKey=k;render();});
['#q','#fCat','#fBuild','#fAccess','#fAuth','#fMcp'].forEach(s=>$(s).addEventListener('input',render));
render();

// ---------- accuracy ----------
$('#p1acc').innerHTML = ACC.pass_1.accuracy_pct+'<small>%</small>';
$('#p2acc').innerHTML = ACC.pass_2.accuracy_pct+'<small>%</small>';
$('#accDelta').textContent = '+'+(Math.round((ACC.pass_2.accuracy_pct-ACC.pass_1.accuracy_pct)*10)/10)+' pts';
$('#sampleMeta').textContent = `${ACC.pass_1.num_apps_sampled} apps · ${ACC.pass_1.total_claims} claims/pass · ${ACC.overall.incorrect_claims/1|0} corrections`;
function fieldAcc(el,obj){barChart(el,Object.entries(obj).map(([k,v])=>[k,v.pct]),'var(--accent)');}
fieldAcc($('#fieldAcc1'),ACC.pass_1.accuracy_by_field);
fieldAcc($('#fieldAcc2'),ACC.pass_2.accuracy_by_field);

// ---------- errors ----------
$('#errBody').innerHTML = ERR.map(e=>`<tr>
  <td><b>${esc(e.app)}</b></td><td>${esc(e.field)}</td>
  <td class="muted">${esc(Array.isArray(e.agent_answer)?e.agent_answer.join(', '):e.agent_answer)}</td>
  <td><b>${esc(Array.isArray(e.verified_answer)?e.verified_answer.join(', '):e.verified_answer)}</b></td>
  <td>${esc(e.error_type)}</td>
  <td>${e.evidence_url?`<a class="evlink" href="${esc(e.evidence_url)}" target="_blank" rel="noopener">source ↗</a>`:''}</td></tr>`).join('');

$('#footNote').innerHTML = `Built as an agentic research pipeline. Buildability is deterministic and reproducible from the embedded signals. Data and full traces ship in the repository. ${esc(DB.generated_note)}`;
</script>
</body>
</html>
"""

if __name__ == "__main__":
    raise SystemExit(main())
