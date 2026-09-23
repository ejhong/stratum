#!/usr/bin/env python3
"""Download the Wikimedia Commons photographs named in records' `plates`, license-checked.

  python3 scripts/fetch_plates.py            # all records; skips files already downloaded
  python3 scripts/fetch_plates.py piltdown   # one record

License, author and source link come from the Commons API — never typed by hand. Files
whose license does not clearly permit reuse are refused. Output: site/plates/<id>/<file>
plus site/plates/manifest.json, which the site build reads.
"""
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from net import fetch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "catalog" / "cases"
PLATES = ROOT / "site" / "plates"
MANIFEST = PLATES / "manifest.json"
OK = re.compile(r"^(public domain|pd|cc0|cc[ -]?by(?:[ -]?sa)?[ -]?\d)", re.I)
WIDTH = 1400


def optimize(path):
    """Cap at WIDTH px and store as a web-weight JPEG (macOS sips; skipped where unavailable)."""
    if not shutil.which("sips"):
        return path
    out = path.with_suffix(".jpg")
    subprocess.run(["sips", "-Z", str(WIDTH), "-s", "format", "jpeg", "-s", "formatOptions", "72", str(path), "--out", str(out)],
                   capture_output=True)
    if out != path and out.exists():
        path.unlink()
    return out


def strip(v):
    return re.sub(r"<[^>]+>", "", v or "").strip()


def info(title):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
                                "iiprop": "url|extmetadata|size", "iiurlwidth": str(WIDTH), "titles": title})
    pages = json.loads(fetch("https://commons.wikimedia.org/w/api.php?" + q)[1])["query"]["pages"]
    return (pages[0].get("imageinfo") or [None])[0]


def main(argv):
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for f in sorted(CASES.glob("*.json")):
        if argv and f.stem not in argv:
            continue
        rec = json.loads(f.read_text())
        entries = []
        for pl in rec.get("plates", []):
            title = pl["commons_file"]
            try:
                ii = info(title)
            except Exception as e:
                print(f"✗ {f.stem}: {title}: lookup failed ({e})")
                continue
            if not ii:
                print(f"✗ {f.stem}: {title}: not found on Commons")
                continue
            meta = ii.get("extmetadata", {})
            lic = strip((meta.get("LicenseShortName") or {}).get("value"))
            if not OK.match(lic):
                print(f"✗ {f.stem}: {title}: license '{lic}' does not clearly permit reuse — skipped")
                continue
            url = ii.get("thumburl") or ii["url"]
            ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
            slug = re.sub(r"[^a-z0-9]+", "-", title[5:].rsplit(".", 1)[0].lower()).strip("-")[:60]
            rel = f"plates/{f.stem}/{slug}.jpg"
            out = ROOT / "site" / rel
            if not out.exists():
                raw = out.with_name(slug + ext + ".download")
                raw.parent.mkdir(parents=True, exist_ok=True)
                raw.write_bytes(fetch(url, accept="image/*", timeout=60)[1])
                optimize(raw.rename(raw.with_suffix("")) if ext != ".jpg" else raw.rename(out))
                print(f"↓ {f.stem}: {title} ({lic})")
            w = ii.get("thumbwidth") or ii.get("width")
            h = ii.get("thumbheight") or ii.get("height")
            entries.append({
                "file": rel, "caption": pl["caption"], "commons_file": title, "license": lic,
                "license_url": (meta.get("LicenseUrl") or {}).get("value"),
                "credit": strip((meta.get("Artist") or {}).get("value"))[:120] or "Unknown author",
                "source_url": ii.get("descriptionurl"), "width": w, "height": h,
            })
        if entries:
            manifest[f.stem] = entries
        elif f.stem in manifest and not rec.get("plates"):
            del manifest[f.stem]
    PLATES.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    print(f"manifest: {sum(len(v) for v in manifest.values())} plates for {len(manifest)} cases")


if __name__ == "__main__":
    main(sys.argv[1:])
