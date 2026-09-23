"""Inline SVG charts, generated from the catalog at build time. No chart libraries."""
import math
from html import escape

from stratum_data import FEATURES, STATUS_LABEL, THIS_YEAR, fmt_age, fmt_leap

COLOR = {"vindicated": "#2b6858", "partial": "#86661a", "open": "#a4461f", "refuted": "#6f6a62"}
INK, INK2, INK3, RULE, PAPER = "#1c1915", "#474036", "#6c6356", "#ddd5c7", "#f8f5ef"
EPOCHS = [  # years before 1950, top to bottom
    (0, 4200, "Late Holocene", "#f3ede3", "silt"),
    (4200, 11700, "Early Holocene", "#ece3d5", "silt"),
    (11700, 129000, "Late Pleistocene", "#e5d9c6", "sand"),
    (129000, 774000, "Middle Pleistocene", "#dccdb5", "gravel"),
    (774000, 2580000, "Early Pleistocene", "#d2c1a5", "hatch"),
    (2580000, 5333000, "Pliocene", "#c8b594", "hatch"),
]


def a(s):
    return escape(str(s), quote=True)


def glyph(status, cx, cy, r=6.5, stroke=PAPER):
    c = COLOR[status]
    if status == "vindicated":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{c}" stroke="{stroke}" stroke-width="1.5"/>'
    if status == "partial":
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{PAPER}" stroke="{c}" stroke-width="1.8"/>'
                f'<path d="M{cx:.1f},{cy - r:.1f} A{r},{r} 0 0 0 {cx:.1f},{cy + r:.1f} Z" fill="{c}"/>')
    if status == "open":
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{PAPER}" stroke="{c}" stroke-width="2"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.36:.1f}" fill="{c}"/>')
    d = r * 0.72
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 1}" fill="{PAPER}" opacity=".85"/>'
            f'<path d="M{cx - d:.1f},{cy - d:.1f} L{cx + d:.1f},{cy + d:.1f} M{cx + d:.1f},{cy - d:.1f} L{cx - d:.1f},{cy + d:.1f}" '
            f'stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>')


def glyph_svg(status, size=14):
    h = size / 2
    return (f'<svg class="g" width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true">'
            f'{glyph(status, h, h, h - 1.6)}</svg>')


def mark_open(r, href):
    info = f"{STATUS_LABEL[r['status']]} · claimed {r['year_claimed']} · {r['claimed_age']['label']}"
    return (f'<a href="{a(href)}" class="case-mark" data-name="{a(r["name"])}" data-info="{a(info)}" '
            f'aria-label="{a(r["name"] + ": " + info)}">')


def patterns():
    return f"""<defs>
<pattern id="p-silt" width="22" height="9" patternUnits="userSpaceOnUse"><path d="M2 4.5h8M13 1h6M14 8h5" stroke="{INK3}" stroke-width=".7" opacity=".32"/></pattern>
<pattern id="p-sand" width="11" height="11" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r=".85" fill="{INK3}" opacity=".35"/><circle cx="7.5" cy="8" r=".7" fill="{INK3}" opacity=".3"/></pattern>
<pattern id="p-gravel" width="26" height="20" patternUnits="userSpaceOnUse"><ellipse cx="6" cy="6" rx="3.2" ry="2.2" fill="none" stroke="{INK3}" stroke-width=".7" opacity=".35"/><ellipse cx="18" cy="15" rx="2.4" ry="1.7" fill="none" stroke="{INK3}" stroke-width=".7" opacity=".3"/><circle cx="20" cy="4" r=".8" fill="{INK3}" opacity=".3"/></pattern>
<pattern id="p-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0v9" stroke="{INK3}" stroke-width=".7" opacity=".28"/></pattern>
</defs>"""


def wavy(x0, x1, y, amp=2.4, wl=150.0, phase=0.0):
    xs = [x0 + i * 10 for i in range(int((x1 - x0) // 10) + 1)]
    if xs[-1] < x1:
        xs.append(x1)
    return "M" + " L".join(f"{x:.1f},{y + amp * math.sin(2 * math.pi * x / wl + phase):.1f}" for x in xs)


def section(cases, root):
    """Every claim placed by when it was made (x) and how old it claimed to be (y, deeper = older)."""
    rows = [r for r in cases if r["_age"]]
    W, H = 1100, 560
    L, R, T, B = 64, 162, 40, 16
    if not rows:
        return ""
    years = [r["year_claimed"] for r in rows]
    x0 = min(1850, (min(years) // 10) * 10 - 10)
    x1 = THIS_YEAR + 4
    ends = [v for r in rows for v in (r["claimed_age"].get("bp_min"), r["claimed_age"].get("bp_max"), r["_age"]) if isinstance(v, (int, float)) and v > 0]
    lo = max(150.0, min(ends) / 1.6)
    hi = min(6e6, max(ends) * 1.6)
    lo, hi = math.log10(lo), math.log10(hi)

    def X(y):
        return L + (y - x0) / (x1 - x0) * (W - L - R)

    def Y(bp):
        return T + (math.log10(max(bp, 1)) - lo) / (hi - lo) * (H - T - B)

    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="sec-t"><title id="sec-t">Each anomaly placed by the year it was claimed and the age it claimed</title>', patterns()]
    # strata
    for i, (top, bot, name, fill, pat) in enumerate(EPOCHS):
        ytop, ybot = Y(max(top, 10 ** lo)), Y(min(bot, 10 ** hi))
        if bot <= 10 ** lo or top >= 10 ** hi:
            continue
        up = wavy(L, W - R, ytop, phase=i * 1.7) if top > 10 ** lo else f"M{L},{ytop:.1f} L{W - R},{ytop:.1f}"
        down = wavy(L, W - R, ybot, phase=(i + 1) * 1.7) if bot < 10 ** hi else f"M{L},{ybot:.1f} L{W - R},{ybot:.1f}"
        # closed band: along the top boundary, then back along the bottom one
        back = " L".join(reversed(down[1:].split(" L")))
        path = f"{up} L{back} Z"
        out.append(f'<path d="{path}" fill="{fill}"/><path d="{path}" fill="url(#p-{pat})"/>')
        if top > 10 ** lo:
            out.append(f'<path d="{up}" fill="none" stroke="{INK3}" stroke-width=".8" opacity=".55"/>')
        mid = (max(ytop, T) + min(ybot, H - B)) / 2
        if min(ybot, H - B) - max(ytop, T) > 22:
            out.append(f'<text x="{W - R + 14}" y="{mid + 4:.1f}" font-size="11.5" fill="{INK3}" letter-spacing=".06em">{a(name.upper())}</text>')
    out.append(f'<rect x="{L}" y="{T}" width="{W - L - R}" height="{H - T - B}" fill="none" stroke="{INK3}" stroke-width=".8" opacity=".6"/>')
    # axes
    for bp, lab in [(1000, "1k yrs"), (10000, "10k"), (100000, "100k"), (1000000, "1M")]:
        if 10 ** lo < bp < 10 ** hi:
            y = Y(bp)
            out.append(f'<line x1="{L - 5}" x2="{L}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK3}"/>'
                       f'<text x="{L - 9}" y="{y + 4:.1f}" font-size="11.5" fill="{INK3}" text-anchor="end">{lab}</text>')
    step = 25 if (x1 - x0) > 120 else 10
    for yr in range(((x0 // step) + 1) * step, x1, step):
        x = X(yr)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H - B}" stroke="{INK}" stroke-width=".5" opacity=".12"/>'
                   f'<text x="{x:.1f}" y="{T - 12}" font-size="11.5" fill="{INK3}" text-anchor="middle">{yr}</text>')
    out.append(f'<text x="{L}" y="{T - 28}" font-size="11" fill="{INK3}" letter-spacing=".08em">YEAR CLAIMED →</text>')
    out.append(f'<text x="{L - 9}" y="{T - 28}" font-size="11" fill="{INK3}" letter-spacing=".08em" text-anchor="end">AGE ↓</text>')
    # marks: ranges first, then glyphs + labels with simple collision avoidance
    placed = []

    def free(x, y, w, h):
        return all(x + w < px or px + pw < x or y + h < py or py + ph < y for px, py, pw, ph in placed) and L < x and x + w < W - R + 6

    marks = []
    for r in sorted(rows, key=lambda r: -r["_age"]):
        x, y = X(r["year_claimed"]), Y(r["_age"])
        ca = r["claimed_age"]
        g = [mark_open(r, f"{root}cases/{r['id']}/")]
        if isinstance(ca.get("bp_min"), int) and isinstance(ca.get("bp_max"), int) and ca["bp_max"] > ca["bp_min"] * 1.15:
            y0, y1 = max(T, Y(max(ca["bp_min"], 1))), min(H - B, Y(ca["bp_max"]))
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y0:.1f}" y2="{y1:.1f}" stroke="{COLOR[r["status"]]}" stroke-width="2.4" stroke-linecap="round" opacity=".45"/>')
        acc = r["_accepted"]
        if acc and acc > 0 and abs(math.log10(acc) - math.log10(r["_age"])) > 0.15 and 10 ** lo <= acc <= 10 ** hi:
            ya = Y(acc)
            g.append(f'<g class="conn"><line x1="{x:.1f}" x2="{x:.1f}" y1="{y:.1f}" y2="{ya:.1f}" stroke="{INK2}" stroke-width="1.2" stroke-dasharray="2 3"/>'
                     f'<circle cx="{x:.1f}" cy="{ya:.1f}" r="3.2" fill="{PAPER}" stroke="{INK2}" stroke-width="1.2"/></g>')
        g.append(f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="11" fill="transparent"/>')
        g.append(glyph(r["status"], x, y, 7))
        w = len(r["name"]) * 7.1 + 4
        for lx, ly, anchor in ((x + 12, y - 7, "start"), (x - 12 - w, y - 7, "end"), (x - w / 2, y - 26, "middle"), (x - w / 2, y + 12, "middle")):
            if free(lx, ly, w, 14):
                placed.append((lx, ly, w, 14))
                tx = lx if anchor == "start" else (lx + w if anchor == "end" else lx + w / 2)
                g.append(f'<text x="{tx:.1f}" y="{ly + 11:.1f}" font-size="12" fill="{INK2}" text-anchor="{anchor}">{a(r["name"])}</text>')
                break
        g.append("</a>")
        marks.append("".join(g))
    out.extend(marks)
    out.append("</svg>")
    return "".join(out)


def lifelines(cases, root, W=660):
    rows = sorted(cases, key=lambda r: (r["year_claimed"], r["name"]))
    if not rows:
        return ""
    LBL, R, T, RH = 168, 64, 30, 24
    H = T + RH * len(rows) + 10
    x0 = min(r["year_claimed"] for r in rows)
    x0 = (x0 // 10) * 10 - 5
    x1 = THIS_YEAR + 2

    def X(y):
        return LBL + (y - x0) / (x1 - x0) * (W - LBL - R)

    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="life-t"><title id="life-t">How long each anomaly waited for a verdict</title>']
    step = 25 if (x1 - x0) > 110 else 10
    for yr in range(((x0 // step) + 1) * step, x1 + 1, step):
        x = X(yr)
        label = "" if abs(THIS_YEAR - yr) < 8 else f'<text x="{x:.1f}" y="{T - 14}" font-size="11" fill="{INK3}" text-anchor="middle">{yr}</text>'
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T - 6}" y2="{H - 6}" stroke="{INK}" stroke-width=".5" opacity=".12"/>{label}')
    xt = X(THIS_YEAR)
    out.append(f'<line x1="{xt:.1f}" x2="{xt:.1f}" y1="{T - 6}" y2="{H - 6}" stroke="{COLOR["open"]}" stroke-width="1" stroke-dasharray="3 3" opacity=".6"/>'
               f'<text x="{xt:.1f}" y="{T - 14}" font-size="11" fill="{COLOR["open"]}" text-anchor="middle">now</text>')
    for i, r in enumerate(rows):
        y = T + RH * i + RH / 2
        c = COLOR[r["status"]]
        xs = X(r["year_claimed"])
        end_year = r["year_resolved"] if (r["status"] != "open" and isinstance(r.get("year_resolved"), int)) else THIS_YEAR
        xe = X(end_year)
        dur = end_year - r["year_claimed"]
        g = [mark_open(r, f"{root}cases/{r['id']}/")]
        g.append(f'<rect class="hit" x="0" y="{y - RH / 2:.1f}" width="{W}" height="{RH}" fill="transparent"/>')
        g.append(f'<rect class="row-bg" x="0" y="{y - RH / 2 + 1:.1f}" width="{W}" height="{RH - 2}" rx="3" fill="transparent"/>')
        nm = r["name"] if len(r["name"]) <= 24 else r["name"][:23].rstrip() + "…"
        g.append(f'<text x="{LBL - 12}" y="{y + 4:.1f}" font-size="12.5" fill="{INK}" text-anchor="end" style="font-family:var(--sans)">{a(nm)}</text>')
        if r["status"] == "open":
            g.append(f'<line x1="{xs:.1f}" x2="{xe:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 6" />'
                     f'<line x1="{xs:.1f}" x2="{xe:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="1.2" opacity=".5"/>')
        else:
            g.append(f'<line x1="{xs:.1f}" x2="{xe:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="3" stroke-linecap="round" opacity=".85"/>')
        g.append(f'<circle cx="{xs:.1f}" cy="{y:.1f}" r="3.2" fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
        g.append(glyph(r["status"], xe, y, 6))
        word = "+" if r["status"] == "open" else ""
        g.append(f'<text x="{xe + 11:.1f}" y="{y + 4:.1f}" font-size="11" fill="{INK3}">{dur}{word} yr</text>')
        g.append("</a>")
        out.append("".join(g))
    out.append("</svg>")
    return "".join(out)


def feature_matrix(cases, root):
    order = ["vindicated", "partial", "open", "refuted"]
    rows = sorted(cases, key=lambda r: (order.index(r["status"]), r["name"]))
    if not rows:
        return ""
    LBL, CW, T, RH = 230, 62, 130, 28
    W = LBL + CW * len(FEATURES) + 20
    groups = [s for s in order if any(r["status"] == s for r in rows)]
    H = T + RH * len(rows) + 22 * len(groups) + 10
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="fm-t"><title id="fm-t">Evidence at the time of each claim, grouped by how the case ended</title>']
    for j, (_, label, _) in enumerate(FEATURES):
        x = LBL + CW * j + CW / 2
        col = COLOR["open"] if j == len(FEATURES) - 1 else INK2
        out.append(f'<text x="{x:.1f}" y="{T - 12}" font-size="12" fill="{col}" transform="rotate(-38 {x:.1f} {T - 12})">{a(label)}</text>')
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T - 4}" y2="{H - 6}" stroke="{INK}" stroke-width=".5" opacity=".08"/>')
    y = T
    for s in groups:
        y += 22
        out.append(f'<text x="0" y="{y - 6}" font-size="11" fill="{COLOR[s]}" letter-spacing=".1em">{a(STATUS_LABEL[s].upper())}</text>'
                   f'<line x1="0" x2="{W}" y1="{y - 1}" y2="{y - 1}" stroke="{RULE}"/>')
        for r in [r for r in rows if r["status"] == s]:
            cy = y + RH / 2
            g = [mark_open(r, f"{root}cases/{r['id']}/"), f'<rect class="hit" x="0" y="{y}" width="{W}" height="{RH}" fill="transparent"/>']
            g.append(glyph(r["status"], 8, cy, 5.5))
            g.append(f'<text x="22" y="{cy + 4.5:.1f}" font-size="13.5" fill="{INK}" style="font-family:var(--sans)">{a(r["name"])}</text>')
            for j, (k, _, _) in enumerate(FEATURES):
                x = LBL + CW * j + CW / 2
                v = r["features_at_claim"][k]["value"]
                col = COLOR["open"] if k == "proponent_stake" else INK2
                if v == "yes":
                    g.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="6.5" fill="{col}"/>')
                elif v == "partial":
                    g.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="6" fill="{PAPER}" stroke="{col}" stroke-width="1.4"/>'
                             f'<path d="M{x:.1f},{cy - 6:.1f} A6,6 0 0 0 {x:.1f},{cy + 6:.1f} Z" fill="{col}"/>')
                elif v == "no":
                    g.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="6" fill="none" stroke="{INK3}" stroke-width="1.3"/>')
                else:
                    g.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="1.6" fill="{INK3}"/>')
            g.append("</a>")
            out.append("".join(g))
            y += RH
    out.append("</svg>")
    return "".join(out)


def strip(rows, root, domain, log=False, ticks=(), fmt=str, unit_label=""):
    """rows: [(label, status_or_None, [(value, record, hollow)])] -> a dot-strip chart."""
    W, LBL, R, T, RH = 1100, 170, 40, 30, 46
    H = T + RH * len(rows) + 8
    d0, d1 = domain

    def X(v):
        if log:
            v = min(max(v, d0), d1)
            return LBL + (math.log10(v) - math.log10(d0)) / (math.log10(d1) - math.log10(d0)) * (W - LBL - R)
        v = min(max(v, d0), d1)
        return LBL + (v - d0) / (d1 - d0) * (W - LBL - R)

    out = [f'<svg viewBox="0 0 {W} {H}" role="img">']
    for t in ticks:
        x = X(t)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T - 6}" y2="{H - 4}" stroke="{INK}" stroke-width=".5" opacity=".13"/>'
                   f'<text x="{x:.1f}" y="{T - 12}" font-size="11.5" fill="{INK3}" text-anchor="middle">{a(fmt(t))}</text>')
    if unit_label:
        out.append(f'<text x="{W - R}" y="{T - 12}" font-size="11" fill="{INK3}" text-anchor="end" letter-spacing=".08em">{a(unit_label)}</text>')
    for i, (label, status, pts) in enumerate(rows):
        y = T + RH * i + RH / 2
        out.append(f'<line x1="{LBL}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RULE}"/>')
        out.append(f'<text x="{LBL - 16}" y="{y + 4.5:.1f}" font-size="13.5" fill="{COLOR.get(status, INK)}" text-anchor="end" style="font-family:var(--sans)">{a(label)}</text>')
        vals = [v for v, _, _ in pts]
        if len(vals) >= 2 and not any(h for _, _, h in pts):
            vals_sorted = sorted(vals)
            n = len(vals_sorted)
            med = vals_sorted[n // 2] if n % 2 else (vals_sorted[n // 2 - 1] * vals_sorted[n // 2]) ** 0.5 if log else (vals_sorted[n // 2 - 1] + vals_sorted[n // 2]) / 2
            xm = X(med)
            out.append(f'<line x1="{xm:.1f}" x2="{xm:.1f}" y1="{y - 15:.1f}" y2="{y + 15:.1f}" stroke="{COLOR.get(status, INK)}" stroke-width="2" opacity=".6"/>')
        seen = {}
        for v, r, hollow in sorted(pts, key=lambda p: p[0]):
            x = X(v)
            k = round(x / 9)
            off = seen.get(k, 0)
            seen[k] = off + 1
            cy = y + (0 if off == 0 else (8 if off % 2 else -8) * ((off + 1) // 2))
            g = [mark_open(r, f"{root}cases/{r['id']}/"), f'<circle class="hit" cx="{x:.1f}" cy="{cy:.1f}" r="10" fill="transparent"/>']
            g.append(glyph(r["status"], x, cy, 6.5))
            g.append("</a>")
            out.append("".join(g))
    out.append("</svg>")
    return "".join(out)


def ruler(r):
    """A small deep-time ruler for a case page: claimed age, the then-accepted limit, the accepted age now."""
    W, H, L, R = 1140, 84, 8, 8
    lo, hi = math.log10(100), math.log10(5e6)

    def X(bp):
        return L + (math.log10(min(max(bp, 100), 5e6)) - lo) / (hi - lo) * (W - L - R)

    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Deep-time ruler for {a(r["name"])}">', patterns()]
    for top, bot, name, fill, pat in EPOCHS:
        if bot <= 100:
            continue
        x0, x1 = X(max(top, 100)), X(min(bot, 5e6))
        out.append(f'<rect x="{x0:.1f}" y="30" width="{x1 - x0:.1f}" height="20" fill="{fill}"/><rect x="{x0:.1f}" y="30" width="{x1 - x0:.1f}" height="20" fill="url(#p-{pat})"/>')
    for bp, lab in [(1000, "1k"), (10000, "10k"), (100000, "100k"), (1000000, "1M yrs")]:
        x = X(bp)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="50" y2="56" stroke="{INK3}"/><text x="{x:.1f}" y="68" font-size="11" fill="{INK3}" text-anchor="middle">{lab}</text>')
    lim = (r.get("orthodoxy_at_claim") or {}).get("limit_bp")
    if lim:
        x = X(lim)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="24" y2="72" stroke="{INK}" stroke-width="1.2"/>'
                   f'<text x="{x + 6:.1f}" y="82" font-size="11" fill="{INK}">accepted limit then · {a(fmt_age(lim))}</text>')
    if r["_accepted"] and r["_accepted"] > 0 and (not r["_age"] or abs(math.log10(r["_accepted"]) - math.log10(r["_age"])) > 0.05):
        x = X(r["_accepted"])
        out.append(f'<circle cx="{x:.1f}" cy="40" r="5" fill="{PAPER}" stroke="{INK2}" stroke-width="1.5"/>'
                   f'<text x="{x:.1f}" y="16" font-size="11" fill="{INK2}" text-anchor="middle">now understood</text>')
    if r["_age"]:
        ca = r["claimed_age"]
        if isinstance(ca.get("bp_min"), int) and isinstance(ca.get("bp_max"), int) and ca["bp_max"] > ca["bp_min"]:
            out.append(f'<line x1="{X(ca["bp_min"]):.1f}" x2="{X(ca["bp_max"]):.1f}" y1="40" y2="40" stroke="{COLOR[r["status"]]}" stroke-width="4" stroke-linecap="round" opacity=".5"/>')
        x = X(r["_age"])
        out.append(glyph(r["status"], x, 40, 7))
        out.append(f'<text x="{x:.1f}" y="16" font-size="11" fill="{COLOR[r["status"]]}" text-anchor="middle">claimed · {a(fmt_age(r["_age"]))}</text>')
    out.append("</svg>")
    return "".join(out)


def leap_strip(cases, root):
    rows = []
    for s, label in (("vindicated", "Vindicated"), ("partial", "Partly vindicated"), ("refuted", "Refuted"), ("open", "Still open")):
        pts = [(r["_leap"], r, s == "open") for r in cases if r["status"] == s and r["_leap"]]
        if pts:
            rows.append((label, s, pts))
    if not rows:
        return ""
    mx = max(v for _, _, pts in rows for v, _, _ in pts)
    d1 = max(30, mx * 1.4)
    ticks = [t for t in (1, 2, 5, 10, 20, 50, 100, 200) if t <= d1]
    return strip(rows, root, (0.8, d1), log=True, ticks=ticks, fmt=lambda t: f"{t}×", unit_label="× THE ACCEPTED LIMIT")


def years_strip(cases, root):
    rows = []
    for s, label in (("vindicated", "Vindicated"), ("partial", "Partly vindicated"), ("refuted", "Refuted"), ("open", "Still open")):
        pts = [(r["_years"], r, s == "open") for r in cases if r["status"] == s]
        if pts:
            rows.append((label, s, pts))
    if not rows:
        return ""
    mx = max(v for _, _, pts in rows for v, _, _ in pts)
    d1 = max(50, int(math.ceil(mx / 10.0) * 10) + 5)
    ticks = list(range(0, d1 + 1, 10 if d1 <= 80 else 20))
    return strip(rows, root, (0, d1), ticks=ticks, fmt=str, unit_label="YEARS FROM CLAIM TO VERDICT")
