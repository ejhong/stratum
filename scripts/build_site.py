#!/usr/bin/env python3
"""Generate the static site into _site/ from the catalog, the analysis and the findings log.

Never edit _site/ by hand: change the records, the templates here, or site/assets/.
Design rule: dense, quiet and exact — tables and bullets, not narrative.
"""
import csv
import json
import math
import re
import shutil
import statistics
import sys
from datetime import date
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402
from stratum_data import (  # noqa: E402
    COST_LABEL, FEATURES, OBJECTION_KIND, OUTCOME_LABEL, POSITIVE_FEATURES, ROOT, STATUS_LABEL, STATUSES,
    THIS_YEAR, TYPE_LABEL, fmt_age, fmt_leap, load_cases,
)

OUT = ROOT / "_site"
SITE = ROOT / "site"
URL = "https://ejhong.github.io/stratum/"
REPO = "https://github.com/ejhong/stratum"
TARGET_FIRST, TARGET_NEXT = 24, 100
NAV = [("cases/", "Cases"), ("findings/", "Findings"), ("leads/", "Leads"), ("method/", "Method")]
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap")
BUILD_DATE = date.today().isoformat()
STATUS_ORDER = {s: i for i, s in enumerate(STATUSES)}
TYPE_SHORT = {"chronology": "Too early", "hominin": "New lineage", "capability": "Capability",
              "contact": "Contact", "legend": "Legend", "artifact": "Object"}
SETTLED_LABEL = {
    "independent-redating": "Independent redating", "new-excavation": "New excavation", "site-visit": "Site visit",
    "replication": "Replication", "dna": "DNA", "morphology": "Morphology", "forensic-analysis": "Forensic analysis",
    "confession": "Confession", "provenance-research": "Provenance research", "geology": "Geology",
    "expert-review": "Expert review", "not-settled": "Not settled",
}


def e(s):
    return escape("" if s is None else str(s))


def fate(status):
    return f'<span class="fate {status}">{charts.glyph_svg(status, 12)}{e(STATUS_LABEL[status])}</span>'


def page(rel, title, body, active=None, desc=None, full_title=False, root=None):
    root = "../" * rel.count("/") if root is None else root
    desc = desc or "An AI-operated lab that learns from how past archaeological anomalies fared, and ranks the open ones worth testing."
    nav = "".join(f'<a href="{root}{h}"{" aria-current=page" if h == active else ""}>{lbl}</a>' for h, lbl in NAV)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title if full_title else f"{title} · Stratum")}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:site_name" content="Stratum">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL}{rel.replace("index.html", "")}">
<meta property="og:image" content="{URL}assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f8f5ef">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="{root or "./"}"><b>Stratum</b><span>what’s left after the boring explanations</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body.replace("{root}", root)}
</main>
<footer class="site-footer"><div class="wrap">
<div><div class="mark">Stratum</div><p>An AI-operated lab for archaeology and human origins: how past anomalies fared, and which open ones deserve a test.</p></div>
<div><h4>Explore</h4><ul><li><a href="{root}cases/">Cases</a></li><li><a href="{root}findings/">Findings</a></li><li><a href="{root}leads/">Leads</a></li><li><a href="{root}method/">Method</a></li></ul></div>
<div><h4>Open lab</h4><ul><li><a href="{REPO}">Code &amp; records</a></li><li><a href="{root}method/#data">Download the catalog</a></li><li><a href="{REPO}/issues/new">Send a correction</a></li></ul></div>
<div class="base"><span>Drafted and checked by AI agents under published rules · every claim cites a source · locations at country level only</span><span>Built {BUILD_DATE}</span></div>
</div></footer>
<script src="{root}assets/app.js" defer></script>
</body>
</html>
"""
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)


# ---------------------------------------------------------------- small parts

def stage_tag(r):
    if r["_reviewed"]:
        return '<span class="tag consistent">Reviewed</span>'
    return '<span class="tag draft">Draft</span>'


def profile_dots(r, with_stake=False):
    keys = POSITIVE_FEATURES + (["proponent_stake"] if with_stake else [])
    out = []
    for k in keys:
        v = r["features_at_claim"][k]["value"]
        cls = ("warn" if v == "yes" else "") if k == "proponent_stake" else (v if v in ("yes", "partial") else "")
        out.append(f'<i class="{cls}" title="{e(dict((f[0], f[1]) for f in FEATURES)[k])}: {e(v)}"></i>')
    return f'<span class="profile" aria-label="Evidence profile {r["_profile"]:g} of 8">{"".join(out)}</span>'


def verdict_cell(r):
    if r["status"] == "open":
        return "open"
    return str(r.get("year_resolved") or "—")


def years_cell(r):
    return f'{r["_years"]}' + ("+" if r["status"] == "open" else "")


def mini_section(r):
    """Card placeholder when no photograph exists: the case's claimed depth as a tiny section."""
    W, H = 320, 180
    lo, hi = math.log10(150), math.log10(3e6)

    def Y(bp):
        return (math.log10(min(max(bp, 150), 3e6)) - lo) / (hi - lo) * H

    parts = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">', charts.patterns()]
    for i, (top, bot, _, fill, pat) in enumerate(charts.EPOCHS):
        y0, y1 = Y(max(top, 150)), Y(min(bot, 3e6))
        if y1 - y0 < 1:
            continue
        parts.append(f'<rect x="0" y="{y0:.1f}" width="{W}" height="{y1 - y0 + 1:.1f}" fill="{fill}"/><rect x="0" y="{y0:.1f}" width="{W}" height="{y1 - y0 + 1:.1f}" fill="url(#p-{pat})"/>')
        if i:
            parts.append(f'<path d="{charts.wavy(0, W, y0, amp=2, wl=90, phase=i)}" stroke="#6c6356" stroke-width=".7" fill="none" opacity=".5"/>')
    if r["_age"]:
        parts.append(charts.glyph(r["status"], W * 0.62, Y(r["_age"]), 9))
    parts.append("</svg>")
    return "".join(parts)


def thumb(r):
    if r["_plates"]:
        p = r["_plates"][0]
        return f'<div class="thumb"><img src="{{root}}{e(p["file"])}" alt="{e(p["caption"])}" loading="lazy"></div>'
    return f'<div class="thumb">{mini_section(r)}</div>'


def case_rows(cases, compact=False):
    rows = []
    for r in cases:
        loc = r["location"]["country"]
        cells = [
            f'<td data-v="{STATUS_ORDER[r["status"]]}">{fate(r["status"])}</td>',
            f'<td class="name" data-v="{e(r["name"])}"><a href="{{root}}cases/{r["id"]}/">{e(r["name"])}</a><span class="sub">{e(r["hook"])}</span></td>',
            f'<td class="m" data-v="{e(loc)}">{e(loc)}</td>',
        ]
        if not compact:
            cells.append(f'<td data-v="{e(r["anomaly_type"])}" class="kind" title="{e(TYPE_LABEL[r["anomaly_type"]])}">{e(TYPE_SHORT[r["anomaly_type"]])}</td>')
        cells += [
            f'<td class="n" data-v="{int(r["_age"] or 0)}">{e(r["claimed_age"]["label"])}</td>',
            f'<td class="n" data-v="{r["year_claimed"]}">{r["year_claimed"]}</td>',
            f'<td class="n" data-v="{r.get("year_resolved") or 9999}">{verdict_cell(r)}</td>',
            f'<td class="n" data-v="{r["_years"]}">{years_cell(r)}</td>',
        ]
        if not compact:
            cells += [
                f'<td class="n" data-v="{r["_leap"] or 0}">{fmt_leap(r["_leap"])}</td>',
                f'<td data-v="{r["_profile"]}">{profile_dots(r)}</td>',
                f'<td data-v="{1 if r["_reviewed"] else 0}">{stage_tag(r)}</td>',
            ]
        rows.append(f'<tr data-status="{r["status"]}" data-type="{r["anomaly_type"]}">{"".join(cells)}</tr>')
    return "".join(rows)


def case_table(cases, compact=False):
    heads = [("Fate", ""), ("Case", ""), ("Where", "")]
    if not compact:
        heads.append(("Kind", ""))
    heads += [("Claimed age", "n"), ("Claimed", "n"), ("Verdict", "n"), ("Years", "n")]
    if not compact:
        heads += [("Leap", "n"), ("Evidence then", ""), ("Record", "")]
    th = "".join(f'<th data-sort class="{c}">{e(h)}</th>' for h, c in heads)
    return f'<div class="table-scroll"><table class="data" data-table><thead><tr>{th}</tr></thead><tbody>{case_rows(cases, compact)}</tbody></table></div>'


def legend():
    return '<div class="legend">' + "".join(fate(s) for s in STATUSES) + "</div>"


def stat_block(items):
    return '<div class="stats">' + "".join(
        f'<div class="stat"><span class="num">{n}</span><span class="label">{g}{e(lbl)}</span></div>' for n, g, lbl in items) + "</div>"


def hyp_reading(hid, h):
    def frac(s):
        return f"{s['k']}/{s['n']}" if s and s["n"] else "—"
    if not h:
        return ""
    if hid == "H1":
        return h["reading"]
    if hid == "H2":
        m = h["multiple_dating_methods"]
        return f"2+ dating methods: vindicated {frac(m['vindicated'])} · refuted {frac(m['refuted'])}"
    if hid == "H3":
        t, m = h["independent_teams"], h["material_accessible"]
        return f"One team: refuted {frac(t['refuted'])} · vindicated {frac(t['vindicated'])}; closed material: refuted {frac(m['refuted'])} · vindicated {frac(m['vindicated'])}"
    if hid == "H4":
        if h["prior_share_wrong"] is None:
            return "No objections with known outcomes yet"
        ph = f"{h['prior_share_held']:.0%}" if h["prior_share_held"] is not None else "—"
        return f"Model-based objections: {h['prior_share_wrong']:.0%} of those proved wrong vs {ph} of those that held"
    if hid == "H5":
        if h["vindicated_median"] is None or h["refuted_median"] is None:
            return "Needs resolved cases of both kinds"
        return f"Median years to verdict: vindicated {h['vindicated_median']:g} · refuted {h['refuted_median']:g}"
    if hid == "H6":
        return f"Outside stake: refuted {frac(h['refuted'])} · vindicated {frac(h['vindicated'])}"
    return ""


def parse_log():
    text = re.sub(r"<!--.*?-->", "", (ROOT / "findings" / "log.md").read_text(), flags=re.S)
    entries = []
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, rest = chunk.partition("\n")
        eid, _, title = head.partition(" · ")
        fields = dict(re.findall(r"^- \*\*(.+?):\*\* (.+)$", rest, flags=re.M))
        entries.append({"id": eid.strip(), "title": title.strip(), **fields})
    return entries


def hyp_table(summary, compact=False):
    hyps = summary.get("hypotheses", {})
    rows = []
    for en in parse_log():
        if not en["id"].startswith("H"):
            continue
        h = hyps.get(en["id"], {})
        status = h.get("status", "awaiting data")
        n, thr = h.get("n", 0), h.get("threshold", 1)
        pct = min(100, round(100 * n / thr)) if thr else 0
        tag = f'<span class="tag {status.replace(" ", "-")}">{e(status)}</span>'
        meter = f'<div class="mono muted">{n} / {thr}</div><div class="meter"><i style="width:{pct}%"></i></div>'
        if compact:
            rows.append(f'<tr><td class="id">{e(en["id"])}</td><td><div class="t">{e(en["title"])}</div></td><td>{meter}</td><td>{tag}</td></tr>')
        else:
            rows.append(f"""<tr><td class="id">{e(en['id'])}</td><td><div class="t">{e(en['title'])}</div><div class="c">{e(en.get('Claim', ''))}</div>
<details><summary>Test · disproof</summary><p><b>Test.</b> {e(en.get('Test', ''))}</p><p><b>Would disprove it.</b> {e(en.get('Would disprove it', ''))}</p><p>Registered {e(en.get('Date', ''))}, before any data.</p></details></td>
<td class="rd">{e(hyp_reading(en['id'], h))}</td><td>{meter}</td><td>{tag}</td></tr>""")
    head = "<tr><th></th><th>Hypothesis</th><th>n / needed</th><th>Status</th></tr>" if compact else "<tr><th></th><th>Hypothesis</th><th>Current reading</th><th>n / needed</th><th>Status</th></tr>"
    return f'<div class="table-scroll"><table class="data hyps"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'


def ranked_leads(cases):
    open_cases = [r for r in cases if r["status"] in ("open", "partial")]
    return sorted(open_cases, key=lambda r: (-r["_profile"], r["_leap"] or 99, r["name"]))


def leads_table(cases, limit=None):
    ranked = ranked_leads(cases)[:limit]
    rows = []
    for i, r in enumerate(ranked, 1):
        t = (r.get("decisive_tests") or [None])[0]
        test = f'<b>{e(COST_LABEL[t["cost"]])}</b>{e(t["test"])}' if t else "—"
        stake = r["features_at_claim"]["proponent_stake"]["value"]
        rows.append(f'<tr><td class="rank">{i}</td><td class="name"><a href="{{root}}cases/{r["id"]}/">{e(r["name"])}</a><span class="sub">{e(r["hook"])}</span></td>'
                    f'<td class="test">{test}</td><td>{profile_dots(r)} <span class="mono muted">{r["_profile"]:g}/8</span></td>'
                    f'<td class="n">{fmt_leap(r["_leap"])}</td><td class="n">{THIS_YEAR - r["year_claimed"]}</td><td class="m">{e(stake)}</td></tr>')
    if not rows:
        return '<p class="empty">Open cases appear here as their records land.</p>'
    return ('<div class="table-scroll"><table class="data leads"><thead><tr><th></th><th>Case</th><th>Decisive test</th><th>Evidence then</th>'
            f'<th class="n">Leap</th><th class="n">Years open</th><th>Stake</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


# ---------------------------------------------------------------- pages

def home(cases, summary):
    c = {s: sum(r["status"] == s for r in cases) for s in STATUSES}
    reviewed = sum(r["_reviewed"] for r in cases)
    stats = stat_block([(len(cases), "", "Cases")] + [
        (c[s], charts.glyph_svg(s, 11), STATUS_LABEL[s].split()[0]) for s in STATUSES])
    if cases:
        vy = [r["_years"] for r in cases if r["status"] == "vindicated"]
        ry = [r["_years"] for r in cases if r["status"] == "refuted"]
        def yrs(v):
            return f"{v:g} yr" + ("" if v == 1 else "s")
        med = f"median {yrs(statistics.median(vy))} to vindicate · {yrs(statistics.median(ry))} to refute" if vy and ry else "claim → verdict"
        main = f"""
<section class="section">
<div class="sh"><h2>Every claim, at the depth it claimed</h2>{legend()}</div>
<figure class="chart chart-scroll">{charts.section(cases, "{root}")}
<figcaption>Across: year the claim was made. Down: age claimed (log scale), over the geological epochs. Bars show claimed ranges; hover a refuted case for where it really belongs. Claims with no figure in years (e.g. Piltdown’s “Early Pleistocene”) are listed in the cases table only.</figcaption></figure>
</section>
<section class="section grid-6-4">
<div class="panel"><h2>Time to verdict <small>{e(med)}</small></h2><figure class="chart chart-scroll">{charts.lifelines(cases, "{root}")}</figure></div>
<div class="panel"><h2>Pre-registered hypotheses <small>published before any data</small></h2>{hyp_table(summary, compact=True)}<p class="small" style="margin-top:8px"><a href="{{root}}findings/">All findings →</a></p></div>
</section>
<section class="section">
<div class="sh"><h2>Top open leads</h2><a class="small" href="{{root}}leads/">All leads →</a></div>
{leads_table(cases, 3)}
</section>"""
    else:
        main = '<section class="section"><p class="empty">The first ten records are being researched now: drafted by researcher agents, checked against Crossref, then attacked by skeptic agents. This page fills in as they land.</p></section>'
    body = f"""<div class="wrap">
<section class="head"><div>
<div class="eyebrow">An AI lab for archaeology’s anomalies</div>
<h1>Some anomalies rewrite history. Most don’t.</h1>
<p class="lede">Claims that challenged the accepted story · how each fared · what separated the real from the false · which open cases deserve a test.</p>
</div>{stats}</section>
{main}
<section class="section links3">
<a href="{{root}}findings/"><b>Findings</b>Six hypotheses, registered before the data, tested as the catalog grows.</a>
<a href="{{root}}leads/"><b>Leads</b>Open anomalies ranked by resemblance to past vindications, each with its decisive test.</a>
<a href="{{root}}method/"><b>Method</b>Agents, checks, pre-registration, progress and costs. {reviewed} of {len(cases)} records reviewed.</a>
</section>
</div>"""
    page("index.html", "Stratum — what’s left after the boring explanations", body, full_title=True)


def cases_index(cases):
    counts = {s: sum(r["status"] == s for r in cases) for s in STATUSES}
    chips = [f'<button class="chip" data-filter="all" aria-pressed="true">All <span class="n">{len(cases)}</span></button>']
    chips += [f'<button class="chip" data-filter="{s}" aria-pressed="false">{charts.glyph_svg(s, 11)}{e(STATUS_LABEL[s])} <span class="n">{counts[s]}</span></button>'
              for s in STATUSES if counts[s]]
    ordered = sorted(cases, key=lambda r: -(r["_age"] or 0))
    cards = "".join(
        f'<a class="card" href="{{root}}cases/{r["id"]}/" data-status="{r["status"]}" data-type="{r["anomaly_type"]}">{thumb(r)}'
        f'<div class="body">{fate(r["status"])}<h3>{e(r["name"])}</h3><p class="hook">{e(r["hook"])}</p>'
        f'<div class="meta"><span>{e(r["location"]["country"])}</span><span>{e(r["claimed_age"]["label"])}</span></div></div></a>'
        for r in ordered)
    stats = stat_block([(counts[s], charts.glyph_svg(s, 11), STATUS_LABEL[s].split()[0]) for s in STATUSES])
    body = f"""<div class="wrap" data-view="table">
<section class="head"><div><div class="eyebrow">The catalog</div><h1>Cases</h1>
<p class="lede">Every anomaly in the catalog. Sort any column; filter by fate. “Evidence then” shows the eight features as they stood when the claim was made.</p></div>{stats}</section>
<div class="filters">{"".join(chips)}<span class="spacer"></span><div class="seg" role="group" aria-label="View"><button data-view-btn="table" aria-pressed="true">Table</button><button data-view-btn="cards" aria-pressed="false">Cards</button></div></div>
{case_table(ordered) if cases else '<p class="empty">No records yet.</p>'}
<div class="cards" data-cards>{cards}</div>
</div>"""
    page("cases/index.html", "Cases", body, active="cases/")


def case_page(r):
    root = "../../"
    st = r["status"]
    loc = r["location"]
    where = ", ".join(x for x in (loc.get("region"), loc["country"]) if x)
    plate = ""
    if r["_plates"]:
        p = r["_plates"][0]
        plate = (f'<figure class="plate"><img src="{root}{e(p["file"])}" alt="{e(p["caption"])}">'
                 f'<figcaption>{e(p["caption"])}<span class="credit">{e(p["credit"])} · <a href="{e(p["source_url"])}">{e(p["license"])}</a></span></figcaption></figure>')
    orth = r.get("orthodoxy_at_claim") or {}
    nsrc = len(r["sources"])
    nchk = sum(s["verification"] == "checked" for s in r["sources"])
    if st == "open":
        verdict = f'Open<small>{THIS_YEAR - r["year_claimed"]} years and counting</small>'
    else:
        verdict = f'{e(STATUS_LABEL[st])} · {r.get("year_resolved") or "—"}<small>{r["_years"]} years after the claim</small>'
    facts = [
        ("Claimed age", f'{e(r["claimed_age"]["label"])}<small>{e(fmt_age(r["_age"]))}</small>'),
        ("Claimed", f'{r["year_claimed"]}<small>{e(", ".join(r.get("key_proponents", [])[:2]))}</small>'),
        ("Verdict", f'<span style="color:var(--{st})">{verdict}</span>'),
        ("Leap", f'{fmt_leap(r["_leap"])}<small>{"× the accepted limit then" if r["_leap"] else "not a dating claim" if r["anomaly_type"] != "chronology" else "limit not sourced"}</small>'),
        ("Evidence then", f'{r["_profile"]:g} / 8<small>{profile_dots(r, with_stake=True)}</small>'),
        ("Sources", f'{nsrc}<small>{nchk} opened and checked</small>'),
        ("Record", f'{e(r["confidence"].capitalize())} confidence<small>{"Reviewed" if r["_reviewed"] else "Draft · skeptic review pending"}</small>'),
    ]
    facts_html = '<div class="facts">' + "".join(f'<div><div class="label">{e(k)}</div><div class="v">{v}</div></div>' for k, v in facts) + "</div>"

    tl = sorted(r.get("timeline", []), key=lambda t: t["year"])
    key_years = {r["year_claimed"], r.get("year_resolved")}
    timeline = "".join(f'<li class="{"key" if t["year"] in key_years else ""}"><span class="y">{t["year"]}</span><span class="e">{e(t["event"])}</span></li>' for t in tl)

    objs = r.get("objections", [])
    marks = {"held": "✓", "wrong": "✕", "unresolved": "?"}
    obj_items = []
    for o in objs:
        who = " · ".join(str(x) for x in (o.get("raised_by"), o.get("year")) if x)
        out = f' — {e(o["outcome_note"])}' if o.get("outcome_note") else ""
        obj_items.append(f'<li><span class="o-mark {o["outcome"]}" aria-hidden="true">{marks[o["outcome"]]}</span><div>{e(o["text"])}'
                         f'<div class="o-meta">{e(OBJECTION_KIND[o["kind"]])}{" · " + e(who) if who else ""}</div>'
                         f'<div class="o-out"><span class="o-tag {o["outcome"]}">{e(OUTCOME_LABEL[o["outcome"]])}</span>{out}</div></div></li>')
    n_wrong = sum(o["outcome"] == "wrong" for o in objs)
    obj_sub = f"{n_wrong} of {len(objs)} proved wrong" if objs else ""

    feat_items = []
    for k, label, _ in FEATURES:
        f = r["features_at_claim"][k]
        col = "var(--open)" if k == "proponent_stake" else "var(--ink-2)"
        dot = {"yes": f'<svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="5" fill="{col}"/></svg>',
               "partial": f'<svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4.6" fill="none" stroke="{col}" stroke-width="1.2"/><path d="M6,1.4 A4.6,4.6 0 0 0 6,10.6 Z" fill="{col}"/></svg>',
               "no": '<svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4.6" fill="none" stroke="var(--ink-3)" stroke-width="1.2"/></svg>',
               "unknown": '<svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="1.5" fill="var(--ink-3)"/></svg>'}[f["value"]]
        word = {"yes": "Yes", "partial": "Partly", "no": "No", "unknown": "Unknown"}[f["value"]]
        note = f' — {e(f["note"])}' if f.get("note") else ""
        feat_items.append(f'<li>{dot}<b>{e(label)}</b><span><b>{word}</b>{note}</span></li>')

    right = []
    if r.get("decisive_tests"):
        tests = "".join(f'<li>{e(t["test"])}<span class="c">{e(COST_LABEL[t["cost"]])}</span><div class="w">Would show: {e(t["would_show"])}</div></li>' for t in r["decisive_tests"])
        right.append(f'<h3>What would settle it <small>for a field partner</small></h3><ol class="tests">{tests}</ol>')
    if r.get("what_settled_it"):
        how = ", ".join(SETTLED_LABEL.get(m, m) for m in r.get("settled_by", []) if m != "not-settled")
        right.append(f'<h3 style="margin-top:16px">What settled it{f" <small>{e(how)}</small>" if how else ""}</h3><div class="settled">{e(r["what_settled_it"])}</div>')
    right.append(f'<h3 style="margin-top:16px">What would change this record</h3><p class="falsifier">{e(r["falsifier"])}</p>')

    notes = [f'<li><b>Status.</b> {e(r["status_note"])}</li>']
    if orth.get("label"):
        notes.append(f'<li><b>Accepted view then.</b> {e(orth["label"])}</li>')
    if (r.get("accepted_age") or {}).get("label"):
        notes.append(f'<li><b>Now understood.</b> {e(r["accepted_age"]["label"])}</li>')
    if r["claimed_age"].get("basis"):
        notes.append(f'<li><b>Dating basis.</b> {e(r["claimed_age"]["basis"])}</li>')
    for cor in r.get("corrections", []):
        notes.append(f"<li><b>Correction.</b> {e(cor)}</li>")
    if r.get("notes"):
        notes.append(f"<li>{e(r['notes'])}</li>")
    people = []
    if r.get("key_proponents"):
        people.append(f'<li><b>Proponents.</b> {e(", ".join(r["key_proponents"]))}</li>')
    if r.get("key_critics"):
        people.append(f'<li><b>Critics.</b> {e(", ".join(r["key_critics"]))}</li>')
    people.append(f'<li><b>Evidence types.</b> {e(", ".join(t.replace("-", " ") for t in r["evidence_types"]))} · {r["independent_methods_count"]} independent lines</li>')
    if r.get("confidence_note"):
        people.append(f'<li><b>Record confidence.</b> {e(r["confidence"])} — {e(r["confidence_note"])}</li>')

    vlabel = {"checked": "● checked", "exists": "◐ exists, not read", "unverified": "○ unverified"}
    mcheck = {"match": "Crossref match", "doi-resolves": "DOI resolves", "url-ok": "link works", "url-blocked": "link blocks bots",
              "mismatch": "Crossref mismatch", "doi-not-found": "DOI not found", "url-broken": "link broken", "no-identifier": "no identifier", "error": "check failed"}
    src = []
    for s in r["sources"]:
        chk = (r["_checks"].get(s["id"]) or {}).get("result")
        bits = [f'<span class="ver {s["verification"]}">{vlabel[s["verification"]]}</span>', e(s["kind"])]
        if s.get("access") == "paywalled":
            bits.append("paywalled")
        if chk:
            bits.append(e(mcheck.get(chk, chk)))
        if s.get("doi"):
            bits.append(f'<a href="https://doi.org/{e(s["doi"])}">doi:{e(s["doi"])}</a>')
        if s.get("url"):
            bits.append(f'<a href="{e(s["url"])}">link</a>')
        snote = f'<div class="muted">{e(s["note"])}</div>' if s.get("note") else ""
        src.append(f'<li><span class="sid">{e(s["id"])}</span><div>{e(s["citation"])}{snote}<div class="smeta">{" · ".join(bits)}</div></div></li>')

    rv = r.get("review", {})
    rev = r["_review"] or {}
    rec = [f'<span><b>Drafted</b> {e(rv.get("drafted_by", ""))} · {e(rv.get("drafted_on", ""))}</span>']
    if rev:
        rec.append(f'<span><b>Skeptic</b> {e(rev.get("verdict", ""))} · {e(rev.get("date", ""))}</span>')
    rec.append(f'<span><b>Stage</b> {e(rv.get("stage", ""))}</span>')
    if rv.get("open_issues"):
        rec.append(f'<span><b>Open issues</b> {e("; ".join(rv["open_issues"]))}</span>')
    rec.append(f'<span><a href="{REPO}/blob/main/catalog/cases/{r["id"]}.json">Raw record</a> · <a href="{REPO}/issues/new?title={e("Correction: " + r["name"])}">Suggest a correction</a></span>')

    body = f"""<div class="wrap">
<div class="crumbs"><a href="{root}cases/">Cases</a> / {e(r['name'])}</div>
<section class="case-head{'' if plate else ' no-plate'}"><div>
{fate(st)}<h1>{e(r['name'])}</h1>
<div class="meta"><span>{e(where)}</span><span>{e(TYPE_LABEL[r['anomaly_type']])}</span><span>claimed {r['year_claimed']}</span>{"" if r["_reviewed"] else "<span>draft · awaiting skeptic review</span>"}</div>
<p class="claim">{e(r['claim'])}</p>
</div>{plate}</section>
{facts_html}
{f'<figure class="chart chart-scroll ruler">{charts.ruler(r)}</figure>' if (r["_age"] or (r.get("orthodoxy_at_claim") or {}).get("limit_bp")) else ""}
<section class="section grid2">
<div class="panel"><h3>What happened</h3><ol class="timeline">{timeline}</ol></div>
<div class="panel"><h3>Objections{f" <small>{e(obj_sub)}</small>" if obj_sub else ""}</h3><ul class="objections">{"".join(obj_items) or '<li class="muted">None recorded.</li>'}</ul></div>
</section>
<section class="section grid2">
<div class="panel"><h3>Evidence at the time <small>within ~5 years of the claim</small></h3><ul class="features">{"".join(feat_items)}</ul></div>
<div class="panel">{"".join(right)}</div>
</section>
<section class="section grid2">
<div class="panel"><h3>Notes</h3><ul class="dots">{"".join(notes)}</ul></div>
<div class="panel"><h3>People and evidence</h3><ul class="dots">{"".join(people)}</ul></div>
</section>
<section class="section">
<details class="sources"><summary>Sources · {nsrc} · {nchk} opened and checked · DOIs matched against Crossref</summary><ol class="srclist">{"".join(src)}</ol></details>
<div class="record" style="margin-top:14px">{"".join(rec)}</div>
</section>
</div>"""
    page(f"cases/{r['id']}/index.html", r["name"], body, active="cases/", desc=r["hook"])


def findings(cases, summary):
    reviewed = [r for r in cases if r["_reviewed"]]
    resolved = [r for r in reviewed if r["status"] in ("vindicated", "refuted")]
    entries = parse_log()
    obs = [en for en in entries if not en["id"].startswith("H")]
    obs_rows = "".join(
        f'<tr><td class="id">{e(o["id"])}</td><td><div class="t">{e(o["title"])}</div><div class="c">{e(o.get("Claim", ""))}</div>'
        f'<details><summary>Test · disproof</summary><p><b>Test.</b> {e(o.get("Test", ""))}</p><p><b>Would disprove it.</b> {e(o.get("Would disprove it", ""))}</p></details></td>'
        f'<td><span class="tag">{e(o.get("Status", ""))}</span></td></tr>' for o in obs)
    h4 = summary.get("hypotheses", {}).get("H4", {}).get("table", {})
    obj_rows = "".join(
        f'<tr><td>{e(OBJECTION_KIND.get(k, k))}</td>' + "".join(f'<td class="n">{v[oc] or "·"}</td>' for oc in ("held", "wrong", "unresolved")) + "</tr>"
        for k, v in h4.items())
    viz = ""
    if reviewed:
        viz = f"""
<section class="section"><div class="sh"><h2>H1 · How far each claim reached</h2><p>Claimed age ÷ the accepted limit when the claim was made. Chronology cases with a sourced limit.</p></div>
<figure class="chart chart-scroll">{charts.leap_strip(reviewed, "{root}") or '<p class="empty">No chronology cases with a sourced limit yet.</p>'}</figure></section>
<section class="section"><div class="sh"><h2>H5 · Years from claim to verdict</h2><p>Open cases show the years so far.</p></div>
<figure class="chart chart-scroll">{charts.years_strip(reviewed, "{root}")}</figure></section>
<section class="section grid-6-4">
<div class="panel"><h2>H2 · H3 · H6 · Evidence at the claim <small>filled yes · half partly · ring no · dot unknown</small></h2><figure class="chart chart-scroll">{charts.feature_matrix(reviewed, "{root}")}</figure></div>
<div class="panel"><h2>H4 · Objections by kind and fate</h2><div class="table-scroll"><table class="data"><thead><tr><th>Kind</th><th class="n">Held</th><th class="n">Wrong</th><th class="n">Open</th></tr></thead><tbody>{obj_rows or '<tr><td colspan=4 class="muted">None yet</td></tr>'}</tbody></table></div></div>
</section>"""
    stats = stat_block([(len(reviewed), "", "Reviewed"), (len(resolved), "", "Resolved"), (len(cases) - len(reviewed), "", "In review")])
    body = f"""<div class="wrap">
<section class="head"><div><div class="eyebrow">Findings</div><h1>What separates the real from the false?</h1>
<p class="lede">Six hypotheses, published before any record existed and tested exactly as worded. Only skeptic-reviewed records count; nothing is a result until its threshold is met.</p></div>{stats}</section>
<section class="section">{hyp_table(summary)}</section>
{viz}
<section class="section"><div class="sh"><h2>Notes on our own method</h2></div>
<div class="table-scroll"><table class="data hyps"><tbody>{obs_rows}</tbody></table></div></section>
</div>"""
    page("findings/index.html", "Findings", body, active="findings/")


def leads(cases):
    ranked = ranked_leads(cases)
    stats = stat_block([(sum(r["status"] == "open" for r in ranked), charts.glyph_svg("open", 11), "Open"),
                        (sum(r["status"] == "partial" for r in ranked), charts.glyph_svg("partial", 11), "Partial")])
    body = f"""<div class="wrap">
<section class="head"><div><div class="eyebrow">Leads</div><h1>The open cases, ranked</h1>
<p class="lede">Unresolved anomalies ordered by how closely their evidence at the time resembles past vindications, each with the test that would settle it. A prioritization, not a probability.</p></div>{stats}</section>
<section class="section">{leads_table(cases)}
<ul class="dots small muted" style="margin-top:12px">
<li>Rank = evidence profile (eight positive features; yes = 1, partly = ½), ties broken by the smaller leap. A validated model replaces it once the catalog is large enough.</li>
<li>Leap = claimed age ÷ the accepted limit when the claim was made. Past vindications mostly stepped modestly (hypothesis H1).</li>
<li>Stake = a documented commercial, religious, nationalist or fame motive (hypothesis H6).</li></ul>
</section></div>"""
    page("leads/index.html", "Leads", body, active="leads/")


def parse_agents():
    out = []
    for f in sorted((ROOT / ".claude" / "agents").glob("*.md")):
        m = re.match(r"^---\n(.*?)\n---", f.read_text(), flags=re.S)
        if m:
            out.append(dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), flags=re.M)))
    order = ["scout", "researcher", "skeptic", "analyst"]
    return sorted(out, key=lambda m: order.index(m["name"]) if m.get("name") in order else 9)


def parse_usage():
    rows = []
    for line in (ROOT / "logs" / "usage.md").read_text().splitlines():
        if line.startswith("|") and not line.startswith("|---") and "| Date" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(cells):
                rows.append(cells)
    return rows


def method(cases):
    drafted = len(cases)
    reviewed = sum(r["_reviewed"] for r in cases)
    agents = "".join(
        f'<tr><td><b>{e(m.get("name", "").capitalize())}</b></td><td>{e(m.get("description", "").split(". ")[0])}.</td>'
        f'<td class="m">{e(m.get("model", "inherit"))} · {e(m.get("effort", "default"))}</td><td class="m" style="white-space:normal">{e(m.get("tools", ""))}</td></tr>'
        for m in parse_agents())
    usage = parse_usage()
    usage_html = ('<div class="table-scroll"><table class="data"><thead><tr><th>Date</th><th>Batch</th><th>Agents</th><th>Tokens</th><th>Notes</th></tr></thead><tbody>'
                  + "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in usage) + "</tbody></table></div>") if usage else '<p class="empty">The first batch is running; its cost is logged when it finishes.</p>'

    def bar(label, n, target):
        pct = min(100, round(100 * n / target)) if target else 0
        return f'<div class="row"><span>{e(label)}</span><span class="bar"><i style="width:{pct}%"></i></span><span>{n} / {target}</span></div>'

    body = f"""<div class="wrap">
<section class="head"><div><div class="eyebrow">Method</div><h1>How the lab works</h1>
<p class="lede">AI agents read and argue under rules published in advance. Humans do the digging.</p></div>
{stat_block([(drafted, "", "Drafted"), (reviewed, "", "Reviewed"), (TARGET_NEXT, "", "Target")])}</section>
<section class="section"><ol class="flow">
<li><span class="eyebrow">01</span><b>Scout</b>Finds candidate anomalies — famous and forgotten — with two real sources each.</li>
<li><span class="eyebrow">02</span><b>Researcher</b>Drafts one record from the literature; every source checked.</li>
<li><span class="eyebrow">03</span><b>Skeptic</b>Attacks the draft: citations, mundane explanations, hindsight, overconfidence.</li>
<li><span class="eyebrow">04</span><b>Analyst</b>Tests the pre-registered hypotheses on reviewed records only.</li>
<li><span class="eyebrow">05</span><b>Field partner</b>A credentialed archaeologist tests the best leads: new dates, re-examination, fieldwork.</li>
</ol></section>
<section class="section grid2">
<div class="panel"><h2>Principles</h2><ul class="dots">
<li><b>Evenhanded.</b> Anomalies are checked as hard as orthodoxy.</li>
<li><b>Mundane first.</b> Contamination, dating error, mixing, misidentification, hoax and recording error are ruled out first.</li>
<li><b>Falsifiable.</b> Every record and finding says what would disprove it; hypotheses are registered before the data.</li>
<li><b>No fabrication.</b> Every claim cites a real source that was actually checked.</li>
<li><b>Honest uncertainty.</b> Disputed cases stay disputed; small samples get small claims.</li>
<li><b>Heritage ethics.</b> Country-level locations only; no coordinates; fieldwork only by permitted professionals.</li></ul></div>
<div class="panel"><h2>Checks on every record</h2><ul class="dots">
<li><b>Schema.</b> Required fields, allowed values and hard length limits; the build fails on any violation.</li>
<li><b>Crossref.</b> Every DOI is matched by script against its title, year and authors.</li>
<li><b>Source labels.</b> <span class="ver checked">● checked</span> opened and confirmed · <span class="ver exists">◐ exists</span> metadata only · <span class="ver unverified">○ unverified</span>.</li>
<li><b>Skeptic review.</b> An independent agent tries to break each draft; issues go back to the researcher.</li>
<li><b>Hindsight guard.</b> Evidence is coded as it stood at the time of the claim; a blind re-coding test is planned (M1).</li></ul></div>
</section>
<section class="section"><div class="sh"><h2>Agents</h2><p>Each role has its own model, effort and tools. The analyst has no web access, so it can only use the checked catalog.</p></div>
<div class="table-scroll"><table class="data"><thead><tr><th>Role</th><th>Job</th><th>Model · effort</th><th>Tools</th></tr></thead><tbody>{agents}</tbody></table></div></section>
<section class="section grid2">
<div class="panel"><h2>Progress</h2><div class="progress">{bar("Records drafted", drafted, TARGET_FIRST)}{bar("Skeptic-reviewed", reviewed, TARGET_FIRST)}{bar("Toward 100 cases", reviewed, TARGET_NEXT)}</div>
<ul class="dots" style="margin-top:16px">
<li><b>Phase 1 · now.</b> Anomaly fates: the catalog, the lessons, the leads.</li>
<li><b>Phase 2.</b> Radiocarbon residue: dates that contradict their site once mundane causes are removed.</li>
<li><b>Phase 3.</b> Grey literature: unpublished excavation reports, read at scale.</li>
<li><b>Phase 4.</b> Landscape: open LiDAR and imagery; findings go privately to heritage authorities.</li>
<li><b>Continuous.</b> Partnership: ranked leads to a field archaeologist or dating lab.</li></ul></div>
<div class="panel"><h2>Costs <small>approximate tokens per batch</small></h2>{usage_html}</div>
</section>
<section class="section" id="data"><div class="sh"><h2>Open data</h2><p>Everything on this site is generated from these files.</p></div>
<div class="downloads"><a class="btn primary" href="{{root}}data/catalog.json">catalog.json</a><a class="btn" href="{{root}}data/catalog.csv">catalog.csv</a><a class="btn" href="{{root}}data/stratum.db">stratum.db · SQLite</a><a class="btn" href="{REPO}">GitHub</a></div></section>
</div>"""
    page("method/index.html", "Method", body, active="method/")


def not_found():
    page("404.html", "Not found", '<div class="wrap"><section class="head"><div><div class="eyebrow">404</div><h1>Nothing at this depth.</h1><p class="lede"><a href="/stratum/">Back to the surface →</a></p></div></section></div>', root="/stratum/")


def exports(cases):
    d = OUT / "data"
    d.mkdir(parents=True, exist_ok=True)
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in cases]
    (d / "catalog.json").write_text(json.dumps(clean, indent=1, ensure_ascii=False))
    cols = ["id", "name", "country", "continent", "anomaly_type", "status", "year_claimed", "year_resolved",
            "claimed_age", "claimed_bp_mid", "leap", "evidence_profile", "confidence", "review_stage"]
    with open(d / "catalog.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in cases:
            w.writerow([r["id"], r["name"], r["location"]["country"], r["location"]["continent"], r["anomaly_type"], r["status"],
                        r["year_claimed"], r.get("year_resolved") or "", r["claimed_age"]["label"],
                        round(r["_age"]) if r["_age"] else "", round(r["_leap"], 2) if r["_leap"] else "", r["_profile"],
                        r["confidence"], r.get("review", {}).get("stage")])
    db = ROOT / "catalog" / "stratum.db"
    if db.exists():
        shutil.copy(db, d / "stratum.db")


def main(argv):
    cases = load_cases(Path(argv[0])) if argv else load_cases()
    summary_path = ROOT / "analysis" / "outputs" / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE / "assets", OUT / "assets")
    if (SITE / "plates").exists():
        shutil.copytree(SITE / "plates", OUT / "plates")
    (OUT / ".nojekyll").write_text("")
    home(cases, summary)
    cases_index(cases)
    for r in cases:
        case_page(r)
    findings(cases, summary)
    leads(cases)
    method(cases)
    not_found()
    exports(cases)
    print(f"site: {len(cases)} case pages -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main(sys.argv[1:])
