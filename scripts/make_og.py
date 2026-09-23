#!/usr/bin/env python3
"""Render link-preview images (1200×630) and the iOS icon from the current catalog.

  python3 scripts/make_og.py

Writes site/assets/og.png (the site card), site/assets/og-bulletin-<n>.png (one per
bulletin) and site/assets/apple-touch-icon.png. Local step (needs Google Chrome); re-run
after a batch or a new bulletin so previews show current numbers. Case pages use their
own photograph as the preview when they have one (see build_site.py).
"""
import json
import math
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402
from stratum_data import ROOT, STATUS_LABEL, STATUSES, TAGLINE, load_cases  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ASSETS = ROOT / "site" / "assets"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap")
BASE = """
:root{--paper:#f8f5ef;--ink:#1c1915;--ink-2:#474036;--ink-3:#6c6356;--accent:#9a3e1c;--rule:#ddd5c7;--dark:#1c1a17;--dark-text:#ebe5da;--dark-faint:#a39a8b;--dark-accent:#e0956b;
--serif:"Newsreader",Georgia,serif;--mono:"IBM Plex Mono",Menlo,monospace;--sans:"IBM Plex Sans",system-ui,sans-serif}
*{box-sizing:border-box}html,body{margin:0}body{width:1200px;height:630px;overflow:hidden;-webkit-font-smoothing:antialiased}
.eyebrow{font:500 15px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase}
"""


def shoot(html, out, size=(1200, 630)):
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "card.html"
        page.write_text(html)
        png = Path(d) / "card.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=8000",
                        f"--window-size={size[0]},{size[1]}", f"--screenshot={png}", page.as_uri()], capture_output=True)
        shutil.copy(png, out)


def column_svg(cases, W=560, H=552):
    """Strata filling the panel (log age, deeper = older), each case placed at its claimed age."""
    lo, hi = math.log10(300), math.log10(2_000_000)

    def Y(bp):
        return (math.log10(min(max(bp, 300), 2_000_000)) - lo) / (hi - lo) * H

    out = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">', charts.patterns()]
    for i, (top, bot, _, fill, pat) in enumerate(charts.EPOCHS):
        y0, y1 = Y(max(top, 300)), Y(min(bot, 2_000_000))
        if y1 - y0 < 1:
            continue
        up = charts.wavy(0, W, y0, amp=3, wl=140, phase=i * 1.3) if i else f"M0,{y0:.1f} L{W},{y0:.1f}"
        down = charts.wavy(0, W, y1, amp=3, wl=140, phase=(i + 1) * 1.3)
        back = " L".join(reversed(down[1:].split(" L")))
        path = f"{up} L{back} Z"
        out.append(f'<path d="{path}" fill="{fill}"/><path d="{path}" fill="url(#p-{pat})"/>')
        if i:
            out.append(f'<path d="{up}" fill="none" stroke="#6c6356" stroke-width="1" opacity=".5"/>')
    pts = sorted([r for r in cases if r["_age"]], key=lambda r: (r["year_claimed"], r["id"]))
    for k, r in enumerate(pts):
        x = 40 + (W - 80) * (k + 0.5) / len(pts)
        out.append(charts.glyph(r["status"], x, Y(r["_age"]), 9))
    out.append("</svg>")
    return "".join(out)


def site_card(cases, latest):
    n = {s: sum(r["status"] == s for r in cases) for s in STATUSES}
    stats = "".join(
        f'<div class="st"><b>{n[s]}</b><span>{charts.glyph_svg(s, 14)} {escape(STATUS_LABEL[s].split()[0])}</span></div>' for s in STATUSES)
    strip = ""
    if latest:
        strip = (f'<div class="strip"><span class="eyebrow" style="color:var(--dark-accent)">Lab bulletin {latest["number"]}</span>'
                 f'<b>{escape(latest["title"])}</b></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}"><style>{BASE}
body{{background:var(--paper);color:var(--ink);position:relative}}
.left{{position:absolute;left:64px;top:58px;width:500px}}
.mark{{font:500 104px/0.9 var(--serif);letter-spacing:-.03em;margin:18px 0 12px}}
.tag{{font:400 19px/1.3 var(--mono);color:var(--ink-3)}}
.h{{font:500 36px/1.18 var(--serif);margin-top:30px;letter-spacing:-.01em}}
.stats{{display:flex;gap:26px;margin-top:30px}} .st b{{display:block;font:500 40px/1 var(--serif)}}
.st span{{display:flex;align-items:center;gap:6px;margin-top:8px;font:500 12px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}}
.right{{position:absolute;right:0;top:0;width:560px;height:552px;overflow:hidden;background:#d2c1a5}}
.strip{{position:absolute;left:0;right:0;bottom:0;height:78px;background:var(--dark);color:var(--dark-text);display:flex;align-items:center;gap:20px;padding:0 64px}}
.strip b{{font:500 25px/1.2 var(--serif)}}
.url{{position:absolute;right:28px;top:26px;font:500 14px var(--mono);color:var(--ink-3);background:var(--paper);padding:4px 8px;border-radius:4px}}
</style></head><body>
<div class="left"><div class="eyebrow" style="color:var(--accent)">An AI lab for archaeology’s anomalies</div>
<div class="mark">Stratum</div><div class="tag">{escape(TAGLINE.lower())}</div>
<div class="h">Some anomalies rewrite history. Most don’t.</div><div class="stats">{stats}</div></div>
<div class="right">{column_svg(cases)}</div><div class="url">ejhong.github.io/stratum</div>{strip}
</body></html>"""


def bulletin_card(bl, counts):
    segs = [("direct", "Direct date", "#7fc0ad"), ("associated_organic", "Nearby material", "#b9a584"),
            ("historical_contextual", "Texts", "#8a7658"), ("stylistic", "Style", "#6f6250"), ("none", "No date", "transparent")]
    total = sum(counts.get(k, 0) for k, _, _ in segs) or 1
    dash = "border:1.5px dashed #a39a8b;"
    bar = "".join(f'<div class="seg" style="flex:{counts.get(k, 0)};background:{c};{dash if c == "transparent" else ""}"></div>'
                  for k, lbl, c in segs if counts.get(k, 0))
    legend = "".join(f'<span><i style="background:{c};{dash if c == "transparent" else ""}"></i><b>{counts.get(k, 0)}</b> {escape(lbl)}</span>'
                     for k, lbl, c in segs if counts.get(k, 0))
    return f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}"><style>{BASE}
body{{background:var(--dark);color:var(--dark-text);padding:60px 68px;position:relative}}
.top{{display:flex;justify-content:space-between;align-items:baseline}} .mark{{font:500 40px/1 var(--serif);letter-spacing:-.02em}}
.h{{font:500 64px/1.06 var(--serif);letter-spacing:-.02em;margin-top:40px;max-width:1040px}}
.sub{{font:400 italic 25px/1.35 var(--serif);color:var(--dark-faint);margin-top:18px;max-width:1000px}}
.bar{{display:flex;gap:4px;height:40px;margin-top:34px}} .seg{{border-radius:5px;min-width:8px}}
.legend{{display:flex;gap:26px;margin-top:16px;font:500 15px var(--mono);color:var(--dark-faint)}}
.legend i{{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px}} .legend b{{color:var(--dark-text);font-weight:500;margin-right:4px}}
.foot{{position:absolute;left:68px;right:68px;bottom:46px;display:flex;justify-content:space-between;font:500 15px var(--mono);color:var(--dark-faint)}}
</style></head><body>
<div class="top"><div class="mark">Stratum</div><div class="eyebrow" style="color:var(--dark-accent)">Lab bulletin {bl['number']} · {escape(bl['date'])}</div></div>
<div class="h">{escape(bl['title'])}</div>
<div class="sub">Only one of 40 famous monuments has a direct date on its stones. The ages of the Great Sphinx, Carnac, Sacsayhuamán and Tiwanaku rest on nearby material, texts or style.</div>
<div class="bar">{bar}</div><div class="legend">{legend}</div>
<div class="foot"><span>How 40 famous megalithic monuments are dated</span><span>ejhong.github.io/stratum</span></div>
</body></html>"""


def touch_icon():
    svg = (ASSETS / "favicon.svg").read_text()
    html = f'<!doctype html><html><body style="margin:0;width:180px;height:180px;overflow:hidden;background:#1c1a17">{svg.replace("<svg ", "<svg width=\"180\" height=\"180\" ", 1)}</body></html>'
    shoot(html, ASSETS / "apple-touch-icon.png", size=(180, 180))


def main():
    if not Path(CHROME).exists():
        sys.exit("Google Chrome not found; skipping preview images.")
    cases = load_cases()
    bls = [json.loads(f.read_text()) for f in sorted((ROOT / "findings" / "bulletins").glob("*.json"))]
    shoot(site_card(cases, bls[-1] if bls else None), ASSETS / "og.png")
    review = ROOT / "analysis" / "megaliths" / "audit_review.json"
    counts = json.loads(review.read_text()).get("counts_after_review", {}) if review.exists() else {}
    for bl in bls:
        shoot(bulletin_card(bl, counts), ASSETS / f"og-bulletin-{bl['number']}.png")
    touch_icon()
    print(f"preview images -> site/assets/og.png, {len(bls)} bulletin card(s), apple-touch-icon.png")


if __name__ == "__main__":
    main()
