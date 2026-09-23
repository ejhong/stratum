#!/usr/bin/env python3
"""Mechanical citation check: does every DOI exist, and does its metadata match the citation?

  python3 scripts/check_sources.py                  # all records
  python3 scripts/check_sources.py monte-verde      # one record

For each DOI, asks Crossref (falling back to doi.org) for title, year and authors and
compares them with the citation text. Plain URLs get a reachability check. Results go to
catalog/checks/<id>.json (one file per case, so parallel agents never collide) and are
shown on the site. This proves a source EXISTS and is
the one described; whether it SAYS what it is cited for is the skeptic agent's job.
Standard library only; needs network.
"""
import json
import re
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from net import HTTPError, fetch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "catalog" / "cases"
OUT = ROOT / "catalog" / "checks"


def get(url, accept="application/json"):
    _, body = fetch(url, accept=accept, timeout=25)
    return 200, body


def words(s):
    return set(re.findall(r"[a-z0-9]{4,}", (s or "").lower()))


def crossref(doi):
    try:
        _, body = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
        m = json.loads(body)["message"]
        year = None
        for k in ("published-print", "published-online", "issued", "created"):
            parts = (m.get(k) or {}).get("date-parts") or [[None]]
            if parts[0] and parts[0][0]:
                year = parts[0][0]
                break
        return {
            "title": " ".join(m.get("title") or [""]),
            "year": year,
            "authors": [a.get("family", "") for a in m.get("author", [])][:8],
            "venue": " ".join(m.get("container-title") or [""]),
        }
    except HTTPError as e:
        if e.code == 404:
            return None
        raise


def doi_resolves(doi):
    try:
        fetch("https://doi.org/" + doi, accept="text/html", timeout=25, method="HEAD")
        return True
    except HTTPError as e:
        return e.code in (401, 403, 405, 429)  # publisher blocks bots but the DOI resolved
    except Exception:
        return False


def check_source(src):
    cit = src.get("citation", "")
    doi = src.get("doi")
    if doi:
        meta = crossref(doi)
        if meta is None:
            ok = doi_resolves(doi)
            return {"result": "doi-resolves" if ok else "doi-not-found", "detail": "not in Crossref" + ("; resolves at doi.org" if ok else "")}
        tw, cw = words(meta["title"]), words(cit)
        overlap = len(tw & cw) / max(1, len(tw))
        year_ok = meta["year"] is None or str(meta["year"]) in cit or str(meta["year"] - 1) in cit or str(meta["year"] + 1) in cit
        author_ok = not meta["authors"] or any(a and a.lower() in cit.lower() for a in meta["authors"][:3])
        good = overlap >= 0.6 and year_ok and author_ok
        return {
            "result": "match" if good else "mismatch",
            "detail": f"title overlap {overlap:.0%}, year {'ok' if year_ok else 'differs'}, author {'ok' if author_ok else 'differs'}",
            "crossref_title": meta["title"][:200],
            "crossref_year": meta["year"],
            "crossref_venue": meta["venue"][:120],
        }
    url = src.get("url")
    if url:
        try:
            status, _ = get(url, accept="text/html,*/*")
            return {"result": "url-ok", "detail": f"HTTP {status}"}
        except HTTPError as e:
            if e.code in (401, 403, 405, 429):
                return {"result": "url-blocked", "detail": f"HTTP {e.code} (site blocks bots; check by hand)"}
            return {"result": "url-broken", "detail": f"HTTP {e.code}"}
        except Exception as e:
            return {"result": "url-broken", "detail": str(e)[:120]}
    return {"result": "no-identifier", "detail": "book or report without DOI/URL; check by hand"}


def main(argv):
    wanted = set(argv)
    OUT.mkdir(exist_ok=True)
    bad = 0
    for f in sorted(CASES.glob("*.json")):
        if wanted and f.stem not in wanted:
            continue
        rec = json.loads(f.read_text())
        results = {}
        for s in rec.get("sources", []):
            try:
                r = check_source(s)
            except Exception as e:
                r = {"result": "error", "detail": str(e)[:160]}
            r["checked_on"] = date.today().isoformat()
            results[s["id"]] = r
            flag = r["result"] in ("mismatch", "doi-not-found", "url-broken")
            bad += flag
            print(f"{'✗' if flag else '·'} {f.stem} {s['id']}: {r['result']} — {r['detail']}")
            time.sleep(0.3)
        (OUT / f"{f.stem}.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    print(f"\n{bad} problem(s). Results in {OUT.relative_to(ROOT)}/")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
