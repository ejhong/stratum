#!/usr/bin/env python3
"""Compact lookups for agents: print only what a record needs, never raw API dumps.

  python3 scripts/lookup.py doi 10.1126/science.abg7586          # citation + abstract + open-access link
  python3 scripts/lookup.py search "Monte Verde Dillehay 1997"    # top matches: year · authors · title · DOI
  python3 scripts/lookup.py page <url> --grep "radiocarbon|OSL"   # only the matching passages of a page or PDF
  python3 scripts/lookup.py commons "File:Name.jpg"               # license, author and size of a Commons file

Why: raw Crossref records include whole reference lists and web pages arrive as full
HTML, and every character an agent reads is re-read on each later step. Read abstracts
first; open full text only for the passages you need, with --grep.
"""
import html
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from net import HTTPError, fetch  # noqa: E402


def jget(url):
    return json.loads(fetch(url)[1])


def authors(lst, n=4):
    names = [f'{a.get("family", "")}, {"".join(p[0] + "." for p in a.get("given", "").split() if p)}'.strip(", ") for a in lst]
    return "; ".join(names[:n]) + (" et al." if len(names) > n else "")


def year_of(m):
    for k in ("published-print", "published-online", "issued"):
        p = (m.get(k) or {}).get("date-parts") or [[None]]
        if p[0] and p[0][0]:
            return p[0][0]
    return "n.d."


def cmd_doi(doi):
    doi = doi.replace("https://doi.org/", "").strip()
    try:
        m = jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
        vol = m.get("volume", "")
        iss = f'({m["issue"]})' if m.get("issue") else ""
        pages = f': {m["page"]}' if m.get("page") else ""
        print(f'CITATION  {authors(m.get("author", []))} ({year_of(m)}). {" ".join(m.get("title") or [""])}. '
              f'{" ".join(m.get("container-title") or [""])} {vol}{iss}{pages}. https://doi.org/{doi}')
    except HTTPError as e:
        print(f"CROSSREF  not found (HTTP {e.code}) — do not cite this DOI unless doi.org resolves it")
    try:
        d = jget(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?select=open_access,abstract_inverted_index,type,cited_by_count")
        inv = d.get("abstract_inverted_index") or {}
        words = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
        oa = d.get("open_access") or {}
        print(f'ACCESS    {"open · " + (oa.get("oa_url") or "") if oa.get("is_oa") else "paywalled / closed"} · cited by {d.get("cited_by_count", "?")}')
        print(f'ABSTRACT  {words[:1500] + ("…" if len(words) > 1500 else "") if words else "(none in OpenAlex — open the publisher page with page --grep)"}')
    except Exception:
        print("ABSTRACT  (OpenAlex lookup failed)")


def cmd_search(q, rows=6):
    url = ("https://api.crossref.org/works?rows=%d&select=DOI,title,author,issued,container-title&query.bibliographic=%s"
           % (rows, urllib.parse.quote(q)))
    for it in jget(url)["message"]["items"]:
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        title = re.sub(r"<[^>]+>", "", " ".join(it.get("title") or [""]))
        print(f'{y} · {authors(it.get("author", []), 2)} · {title[:140]} · '
              f'{" ".join(it.get("container-title") or [""])[:60]} · {it.get("DOI")}')


def page_text(url):
    ctype, body = fetch(url, accept="text/html,application/pdf,*/*", timeout=45)
    if "pdf" in ctype.lower() or url.lower().endswith(".pdf") or body[:5] == b"%PDF-":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(body)
            f.flush()
            out = subprocess.run(["pdftotext", "-q", f.name, "-"], capture_output=True, text=True)
            return out.stdout
    text = body.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<(script|style|nav|footer|header|noscript)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h\d|/tr)[^>]*>", "\n\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"[ \t]+", " ", text)


def cmd_page(url, grep=None, maxc=3000):
    try:
        text = page_text(url)
    except Exception as e:
        print(f"FAILED    {e}")
        return
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    paras = [p for p in paras if len(p) > 40]
    print(f"PAGE      {len(text):,} chars, {len(paras)} passages")
    if grep:
        rx = re.compile(grep, re.I)
        hits = [p for p in paras if rx.search(p)]
        print(f"MATCHES   {len(hits)} passages match /{grep}/")
        used = 0
        for p in hits:
            if used > maxc:
                print(f"…         more matches omitted; narrow --grep")
                break
            print("·", p[:900])
            used += min(len(p), 900)
    else:
        print("\n".join(paras)[:maxc])


def cmd_commons(title):
    params = urllib.parse.urlencode({"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
                                     "iiprop": "url|extmetadata|size", "titles": title})
    pages = jget("https://commons.wikimedia.org/w/api.php?" + params)["query"]["pages"]
    info = (pages[0].get("imageinfo") or [None])[0]
    if not info:
        print("NOT FOUND — check the exact File: title")
        return
    meta = info.get("extmetadata", {})

    def strip(k):
        return re.sub(r"<[^>]+>", "", (meta.get(k) or {}).get("value", "")).strip()
    print(f'LICENSE   {strip("LicenseShortName")} · AUTHOR {strip("Artist")[:80]} · {info.get("width")}×{info.get("height")}')
    print(f'SHOWS     {strip("ImageDescription")[:240]}')
    print(f'URL       {info.get("descriptionurl")}')


def main(argv):
    try:
        return run(argv)
    except HTTPError as e:
        print(f"FAILED    HTTP {e.code} — the service refused or rate-limited; wait a minute and retry, or use another source")
        return 1


def run(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, arg = argv[0], argv[1]
    if cmd == "doi":
        cmd_doi(arg)
    elif cmd == "search":
        cmd_search(" ".join(argv[1:]))
    elif cmd == "page":
        grep = argv[argv.index("--grep") + 1] if "--grep" in argv else None
        maxc = int(argv[argv.index("--max") + 1]) if "--max" in argv else 3000
        cmd_page(arg, grep, maxc)
    elif cmd == "commons":
        cmd_commons(arg)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
