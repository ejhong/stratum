#!/usr/bin/env python3
"""Render the link-preview card (site/assets/og.png, 1200×630) from the current catalog.

  python3 scripts/make_og.py

Local step (needs Google Chrome). Re-run after a batch so previews show current counts.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402
from stratum_data import ROOT, STATUS_LABEL, STATUSES, load_cases  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main():
    cases = load_cases()
    counts = " · ".join(f"{sum(r['status'] == s for r in cases)} {STATUS_LABEL[s].split()[0].lower()}" for s in STATUSES)
    css = (ROOT / "site" / "assets" / "style.css").read_text()
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&family=Newsreader:opsz,wght@6..72,500&display=swap">
<style>{css}
body{{width:1200px;height:630px;overflow:hidden;margin:0;padding:44px 52px;box-sizing:border-box;display:grid;grid-template-columns:360px 1fr;gap:36px;align-items:center}}
.og-t{{font:500 64px/1 var(--serif);letter-spacing:-.02em}} .og-s{{font:15px/1.5 var(--mono);color:var(--ink-3);margin-top:16px}}
.og-h{{font:500 27px/1.25 var(--serif);margin-top:34px}} .og-c{{font:14px var(--mono);color:var(--ink-2);margin-top:22px;line-height:1.7}}
svg{{width:100%;height:auto}}</style></head><body>
<div><div class="og-t">Stratum</div><div class="og-s">what’s left after the<br>boring explanations</div>
<div class="og-h">Some anomalies rewrite history. Most don’t.</div>
<div class="og-c">{len(cases)} cases · {counts}<br>ejhong.github.io/stratum</div></div>
<div>{charts.section(cases, "")}</div></body></html>"""
    if not Path(CHROME).exists():
        sys.exit("Google Chrome not found; skipping the preview card.")
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "og.html"
        page.write_text(html)
        out = Path(d) / "og.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=6000",
                        "--window-size=1200,630", f"--screenshot={out}", page.as_uri()], capture_output=True)
        shutil.copy(out, ROOT / "site" / "assets" / "og.png")
    print("preview card -> site/assets/og.png")


if __name__ == "__main__":
    main()
