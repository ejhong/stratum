"""Load the catalog and derive the values the analysis and the site share."""
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "catalog" / "cases"
REVIEWS = ROOT / "catalog" / "reviews"
CHECKS = ROOT / "catalog" / "checks"
PLATES = ROOT / "site" / "plates" / "manifest.json"
THIS_YEAR = date.today().year

TAGLINE = "Strange finds, fair tests"  # the byline everywhere (header, titles, preview cards)
STATUSES = ["vindicated", "partial", "open", "refuted"]
STATUS_LABEL = {"vindicated": "Vindicated", "partial": "Partly vindicated", "open": "Open", "refuted": "Refuted"}
TYPE_LABEL = {
    "chronology": "Earlier than accepted", "hominin": "New human lineage", "capability": "Unexpected capability",
    "contact": "Long-distance contact", "legend": "Legend made real", "artifact": "Out-of-place object",
}
FEATURES = [
    ("unambiguous_signal", "Unambiguous evidence", "Clearly human-made, human remains, or a distinct genome — not something nature could make."),
    ("documented_context", "Documented context", "Found in place, in documented undisturbed layers."),
    ("multiple_dating_methods", "Independent dating methods", "Two or more independent dating methods agreed."),
    ("multiple_labs", "More than one lab", "Key dates or analyses came from more than one laboratory."),
    ("professional_recovery", "Professional recovery", "Recovered and recorded by trained scientists."),
    ("peer_reviewed_report", "Peer-reviewed report", "A full technical report in a peer-reviewed venue within about five years."),
    ("material_accessible", "Open to critics", "Specimens, site or data open to independent re-examination."),
    ("independent_teams", "Independent teams", "More than one independent group contributed evidence early on."),
    ("proponent_stake", "Outside stake", "A documented commercial, religious, nationalist or fame motive. A warning sign."),
]
POSITIVE_FEATURES = [f[0] for f in FEATURES if f[0] != "proponent_stake"]
POINTS = {"yes": 1.0, "partial": 0.5, "no": 0.0, "unknown": 0.0}
OBJECTION_KIND = {
    "prior": "Contradicts the accepted model", "context": "Layers or association", "dating": "Dating or samples",
    "identification": "Natural, not human", "integrity": "Fraud or provenance", "other": "Other",
}
OUTCOME_LABEL = {"held": "Held up", "wrong": "Proved wrong", "unresolved": "Unresolved"}
COST_LABEL = {"low": "Low cost", "medium": "Medium cost", "high": "High cost"}
REVIEWED_STAGES = ("skeptic-passed", "revised", "published")


def _read(path):
    return json.loads(path.read_text()) if path.exists() else None


def age_mid(age):
    """Representative age in years BP: geometric mean of the range, or whichever end exists."""
    if not isinstance(age, dict):
        return None
    lo, hi = age.get("bp_min"), age.get("bp_max")
    vals = [v for v in (lo, hi) if isinstance(v, int)]
    if not vals:
        return None
    if len(vals) == 2 and lo > 0 and hi > 0:
        return math.sqrt(lo * hi)
    return float(sum(vals) / len(vals))


def load_cases(cases_dir=CASES):
    plates = _read(PLATES) or {}
    out = []
    for f in sorted(Path(cases_dir).glob("*.json")):
        r = json.loads(f.read_text())
        r["_review"] = _read(REVIEWS / f.name)
        r["_checks"] = _read(CHECKS / f.name) or {}
        r["_plates"] = plates.get(r["id"], [])
        r["_age"] = age_mid(r.get("claimed_age"))
        r["_accepted"] = age_mid(r.get("accepted_age"))
        orth = r.get("orthodoxy_at_claim") or {}
        lim = orth.get("limit_bp")
        r["_leap"] = (r["_age"] / lim) if (r.get("anomaly_type") == "chronology" and r["_age"] and lim) else None
        yc, yr = r.get("year_claimed"), r.get("year_resolved")
        r["_years"] = (yr - yc) if isinstance(yr, int) else (THIS_YEAR - yc)
        r["_resolved"] = isinstance(yr, int) and r.get("status") != "open"
        feats = r.get("features_at_claim", {})
        r["_profile"] = sum(POINTS[feats.get(k, {}).get("value", "unknown")] for k in POSITIVE_FEATURES)
        r["_reviewed"] = r.get("review", {}).get("stage") in REVIEWED_STAGES
        out.append(r)
    return out


def fmt_age(bp):
    """Human scale for years before present."""
    if bp is None:
        return "—"
    if bp >= 1_000_000:
        return f"{bp / 1_000_000:.1f} million yrs".replace(".0 ", " ")
    if bp >= 10_000:
        return f"{round(bp / 1000):,}k yrs"
    if bp >= 1000:
        return f"{bp / 1000:.1f}k yrs".replace(".0k", "k")
    return f"{int(round(bp, -1)):,} yrs"


def fmt_leap(x):
    if x is None:
        return "—"
    return f"{x:.1f}×" if x < 10 else f"{round(x):,}×"
