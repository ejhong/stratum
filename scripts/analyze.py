#!/usr/bin/env python3
"""Test the pre-registered hypotheses (findings/log.md) on reviewed records.

Writes analysis/outputs/summary.json, which the site renders. Thresholds and
disproof rules are copied from the pre-registration and must not be changed after
seeing data; add a new dated hypothesis instead. Standard library only.
"""
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stratum_data import FEATURES, ROOT, load_cases  # noqa: E402

OUT = ROOT / "analysis" / "outputs" / "summary.json"


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def fisher_two_sided(a, b, c, d):
    """Fisher's exact test for [[a, b], [c, d]]."""
    n1, n2, m1, n = a + b, c + d, a + c, a + b + c + d

    def p(x):
        return math.comb(n1, x) * math.comb(n2, m1 - x) / math.comb(n, m1)

    obs = p(a)
    lo, hi = max(0, m1 - n2), min(n1, m1)
    return round(min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs * (1 + 1e-9))), 4)


def share(recs, feature, value="yes"):
    known = [r for r in recs if r["features_at_claim"][feature]["value"] != "unknown"]
    k = sum(r["features_at_claim"][feature]["value"] == value for r in known)
    return {"k": k, "n": len(known), "rate": round(k / len(known), 3) if known else None, "ci": wilson(k, len(known))}


def verdict(ready, holds):
    if not ready:
        return "awaiting data"
    return "consistent" if holds else "not supported"


def run(cases):
    reviewed = [r for r in cases if r["_reviewed"]]
    vind = [r for r in reviewed if r["status"] == "vindicated"]
    refu = [r for r in reviewed if r["status"] == "refuted"]
    resolved = vind + refu
    res = {"n_total": len(cases), "n_reviewed": len(reviewed), "n_resolved": len(resolved), "hypotheses": {}}

    # H1 leap size, chronology cases
    lv = [r["_leap"] for r in vind if r["_leap"]]
    lr = [r["_leap"] for r in refu if r["_leap"]]
    n1 = len(lv) + len(lr)
    mv = statistics.median(lv) if lv else None
    mr = statistics.median(lr) if lr else None
    res["hypotheses"]["H1"] = {
        "n": n1, "threshold": 12,
        "vindicated_median": round(mv, 2) if mv else None, "refuted_median": round(mr, 2) if mr else None,
        "vindicated": sorted(round(x, 2) for x in lv), "refuted": sorted(round(x, 2) for x in lr),
        "status": verdict(n1 >= 12 and lv and lr, bool(mv and mr and mv < mr)),
        "reading": (f"Vindicated median {mv:.1f}×, refuted median {mr:.1f}×" if (mv and mr) else "Not enough chronology cases with a sourced accepted limit yet"),
    }

    # H2 dating methods and labs
    h2 = {}
    for f in ("multiple_dating_methods", "multiple_labs"):
        sv, sr = share(vind, f), share(refu, f)
        p = fisher_two_sided(sv["k"], sv["n"] - sv["k"], sr["k"], sr["n"] - sr["k"]) if sv["n"] and sr["n"] else None
        h2[f] = {"vindicated": sv, "refuted": sr, "fisher_p": p}
    a = h2["multiple_dating_methods"]
    holds = a["vindicated"]["rate"] is not None and a["refuted"]["rate"] is not None and a["vindicated"]["rate"] > a["refuted"]["rate"]
    res["hypotheses"]["H2"] = {**h2, "n": len(resolved), "threshold": 20, "status": verdict(len(resolved) >= 20, holds)}

    # H3 one team, closed material
    h3 = {}
    for f in ("independent_teams", "material_accessible"):
        sv, sr = share(vind, f, "no"), share(refu, f, "no")
        p = fisher_two_sided(sr["k"], sr["n"] - sr["k"], sv["k"], sv["n"] - sv["k"]) if sv["n"] and sr["n"] else None
        h3[f] = {"vindicated": sv, "refuted": sr, "fisher_p": p}
    holds = all(
        h3[f]["refuted"]["rate"] is not None and h3[f]["vindicated"]["rate"] is not None
        and h3[f]["refuted"]["rate"] > h3[f]["vindicated"]["rate"] for f in h3
    )
    res["hypotheses"]["H3"] = {**h3, "n": len(resolved), "threshold": 20, "status": verdict(len(resolved) >= 20, holds)}

    # H4 objections that proved wrong were priors
    objs = [o for r in reviewed for o in r.get("objections", [])]
    wrong = [o for o in objs if o["outcome"] == "wrong"]
    held = [o for o in objs if o["outcome"] == "held"]
    pw = sum(o["kind"] == "prior" for o in wrong) / len(wrong) if wrong else None
    ph = sum(o["kind"] == "prior" for o in held) / len(held) if held else None
    kinds = sorted({o["kind"] for o in objs})
    table = {k: {oc: sum(o["kind"] == k and o["outcome"] == oc for o in objs) for oc in ("held", "wrong", "unresolved")} for k in kinds}
    n4 = len(wrong) + len(held)
    res["hypotheses"]["H4"] = {
        "n": n4, "threshold": 30, "prior_share_wrong": round(pw, 3) if pw is not None else None,
        "prior_share_held": round(ph, 3) if ph is not None else None, "table": table,
        "status": verdict(n4 >= 30 and pw is not None and ph is not None, (pw or 0) > (ph or 0)),
    }

    # H5 time to resolution
    yv = [r["_years"] for r in vind]
    yr = [r["_years"] for r in refu]
    mv5 = statistics.median(yv) if yv else None
    mr5 = statistics.median(yr) if yr else None
    res["hypotheses"]["H5"] = {
        "n": len(resolved), "threshold": 20, "vindicated_median": mv5, "refuted_median": mr5,
        "vindicated": sorted(yv), "refuted": sorted(yr),
        "status": verdict(len(resolved) >= 20 and yv and yr, bool(mv5 is not None and mr5 is not None and mv5 > mr5)),
    }

    # H6 outside stake
    sv, sr = share(vind, "proponent_stake"), share(refu, "proponent_stake")
    disproved = sv["k"] >= 2 or (sr["rate"] and sv["rate"] is not None and sv["rate"] >= sr["rate"] / 2 and len(resolved) >= 20)
    res["hypotheses"]["H6"] = {
        "n": len(resolved), "threshold": 20, "vindicated": sv, "refuted": sr,
        "status": "not supported" if sv["k"] >= 2 else verdict(len(resolved) >= 20, not disproved),
    }

    # Feature rates by status, for the matrix
    res["feature_rates"] = {
        f: {s: share([r for r in reviewed if r["status"] == s], f) for s in ("vindicated", "partial", "open", "refuted")}
        for f, _, _ in FEATURES
    }
    return res


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    res = run(load_cases())
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(f"analysis: {res['n_reviewed']} reviewed of {res['n_total']} records; "
          + ", ".join(f"{k} {v['status']}" for k, v in res["hypotheses"].items()))


if __name__ == "__main__":
    main()
