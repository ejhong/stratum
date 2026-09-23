#!/usr/bin/env python3
"""R2 · Frontier scan: radiocarbon dates older than a region's accepted first arrival.

Implements the pre-registered method R2 in findings/log.md, with the regions, membership
rules, limits and conversion rule fixed in analysis/frontier/limits.json (committed and
pushed alone, commit be225f4, before this script existed). Standard library only.

Reuses R1 (scripts/residue/scan.py) for everything R2 says to reuse: the p3k14c file and
its checksum, row loading (the Long/Lat columns are never kept), site definition by
normalised name, laboratory codes, material classes, and R1's four mundane filters in
R1's order: (a) reservoir-prone materials, (b) bone before 1990 or with no reference
year, (c) ages over 40,000 14C BP, (d) split or duplicate samples.

Conversion (documented approximation): each calendar limit L becomes a radiocarbon
threshold T = the oldest age the IntCal20 mean curve reaches at any calendar age <= L
(so a wiggle younger than L cannot make a false exceedance), with sigma_T = the curve's
1-sigma there. A date is "older than the limit by > 2 standard errors" when
(Age - T) > 2 * sqrt(Error^2 + sigma_T^2). IntCal20 is used everywhere, including the
Southern Hemisphere, where it makes the test slightly permissive (see limits.json).

Run from the repository root:
    python3 scripts/frontier/scan.py
Writes:
    analysis/frontier/r2_summary.json   thresholds, funnel, every region's result, lead details
    analysis/frontier/r2_report.md      one-page plain-language report
"""
import csv
import importlib.util
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("r1_scan", ROOT / "scripts/residue/scan.py")
r1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r1)

LIMITS = ROOT / "analysis/frontier/limits.json"
LIMITS_COMMIT = "be225f4 (pushed to origin/main before the scan)"
OUT = ROOT / "analysis/frontier"

# ---- Registered parameters (findings/log.md, R2) -- never tuned -----------------------
SE_MULT = 2.0                          # older than the limit by more than 2 standard errors
MIN_SITES, MIN_LABS, MIN_CLASSES = 3, 2, 2   # lead rule
BONE, UNKNOWN, MAX_AGE, BONE_YEAR = r1.BONE, r1.UNKNOWN, r1.MAX_AGE, r1.BONE_YEAR

# Annotations added AFTER the scan, from general knowledge and the database's own fields only
# (no literature was searched). They label sites in the report and change no count or status.
# Keys are R1-normalised site names.
FAMOUS, KNOWN = "famous early-arrival controversy", "known site, but not known to me for a claim this old"
RECOGNIZED = {
    "bluefish cave 3": FAMOUS + " (Bluefish Caves, Yukon)",
    "cactus hill": FAMOUS + " (pre-Clovis claim, Virginia)",
    "meadowcroft rockshelter": FAMOUS + " (pre-Clovis claim, Pennsylvania)",
    **{f"old crow loc {s}": FAMOUS + " (Old Crow Basin bone-tool debate, Yukon)"
       for s in ("crh 4", "crh 12", "crh 13", "crh 22", "crh 47", "crh 70", "crh 71", "crh 87", "rem78 1")},
    "manis mastodon": KNOWN + " (pre-Clovis mastodon site, about 13,800 years)",
    "on your knees cave": KNOWN + " (Alaska; early Holocene human remains)",
    "cape krusenstern": KNOWN + " (Alaska; beach-ridge archaeological sequence)",
    "smiling dan": KNOWN + " (Illinois)",
    "gerstle river": KNOWN + " (Alaska; late-glacial site)",
    "mead": KNOWN + " (Alaska; late-glacial site)",
    "jim pitts": KNOWN + " (South Dakota; Paleoindian site)",
    "paw paw cove": KNOWN + " (Maryland; Paleoindian site)",
    "bechan cave": KNOWN + " (Utah; a palaeontological dung cave)",
    "the forks": KNOWN + " (Manitoba)",
    "ugashik narrows": KNOWN + " (Alaska Peninsula)",
    "trail creek cave 9": KNOWN + " (Alaska; I recall debated early bone dates, unverified)",
}
SHORT = {"americas": "Americas", "sahul": "Sahul", "japan": "Japan", "remote_oceania_west": "Remote Oceania (west)",
         "remote_oceania_east_polynesia": "Remote Oceania (East Polynesia)", "new_zealand": "New Zealand",
         "iceland": "Iceland", "madagascar": "Madagascar", "caribbean": "Caribbean"}
LEAD_NOTES = {
    "americas": "Most sites are Alaskan, Yukon and Alberta localities whose kept dates are on bones of named Pleistocene "
                "animals (mammoth, horse, bison, bear and others), compiled in CARD and often citing fauna compilations "
                "(FAUNMAP, Harington 2003, Guthrie). A date on a fossil bone gives the animal's age, not evidence of people, "
                "unless the bone is shown to be modified by humans. p3k14c does not record that, and R1's filters were not "
                "built to remove it, so the registered rule flags the region on the strength of fossil localities. The "
                "useful parts of this lead are the famous cases and the smaller set of unrecognized sites dated on charcoal, "
                "wood or plants. No Central or South American date passed the threshold, even before the filters.",
    "iceland": "All 7 Icelandic rows in p3k14c come from RADON-B (a Bronze Age compilation) and fall between 2,650 and "
               "2,820 14C BP, about 2,400–3,150 cal BP. One site name, Castro de Nossa Senhora da Guia, is Portuguese, "
               "which suggests a country-coding error in the compilation. Without that site, Iceland has 2 sites and no "
               "short-lived plant date, so it would not meet the lead rule. p3k14c does not record whether the other "
               "samples come from human activity at all. These observations come from the database fields only.",
}


def key(s):
    return re.sub(r"[^a-z0-9]", "", r1.fold(s or ""))


def load_curve(path):
    """IntCal20 points (cal BP, 14C BP, 1-sigma), oldest last."""
    pts = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        p = line.split(",")
        pts.append((float(p[0]), float(p[1]), float(p[2])))
    return sorted(pts)


def threshold(curve, limit):
    """(T, sigma_T, cal BP where T is reached): the oldest mean 14C age at calendar ages <= limit."""
    best = None
    for (t1, c1, s1), (t2, c2, s2) in zip(curve, curve[1:]):
        if t1 > limit:
            break
        cands = [(c1, s1, t1)]
        if t2 <= limit:
            cands.append((c2, s2, t2))
        else:
            f = (limit - t1) / (t2 - t1)
            cands.append((c1 + f * (c2 - c1), s1 + f * (s2 - s1), limit))
        for c in cands:
            if best is None or c[0] > best[0]:
                best = c
    return best


def rule_matches(rule, r):
    return all(key(rule[f]) == key(r[col]) for f, col in
               (("continent", "Continent"), ("country", "Country"), ("province", "Province")) if f in rule)


def region_of(r, regions):
    hits = [g["id"] for g in regions
            if any(rule_matches(x, r) for x in g["include"]) and not any(rule_matches(x, r) for x in g["exclude"])]
    assert len(hits) <= 1, f"row matches two regions: {hits}"
    return hits[0] if hits else None


def self_test():
    curve = [(0, 0, 10), (100, 150, 10), (200, 120, 20), (300, 260, 20)]
    assert threshold(curve, 200)[:2] == (150, 10)          # wiggle: the max younger than the limit wins
    assert threshold(curve, 250)[0] == 190                 # interpolated at the limit
    assert key("BurkinaFaso") == key("Burkina Faso") and key("Hawai'i") == key("Hawaii")
    regs = [{"id": "x", "include": [{"continent": "South America"}], "exclude": [{"country": "Chile", "province": "Rapa Nui"}]},
            {"id": "y", "include": [{"country": "Chile", "province": "Rapa Nui"}], "exclude": []}]
    assert region_of({"Continent": "South America", "Country": "Chile", "Province": "Rapa Nui"}, regs) == "y"
    assert region_of({"Continent": "South America", "Country": "Chile", "Province": ""}, regs) == "x"


def main():
    t0 = time.time()
    r1.self_test()
    self_test()
    data_sha, intcal_sha, limits_sha = r1.sha256(r1.DATA), r1.sha256(r1.INTCAL), r1.sha256(LIMITS)
    assert data_sha == r1.DATA_INFO["expected_sha256"], "p3k14c file differs from the registered one"
    assert intcal_sha == r1.INTCAL_INFO["expected_sha256"], "IntCal20 file differs"
    limits = json.loads(LIMITS.read_text(encoding="utf-8"))
    regions = limits["regions"]
    curve = load_curve(r1.INTCAL)
    mean_curve = [(t, c) for t, c, _ in curve]

    # ---- load exactly as R1 (coordinates never kept) -----------------------------------
    rows = []
    with open(r1.DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({k: r1.clean(r.get(k)) for k in r1.KEEP})
    for r in rows:
        r["age"], r["err"] = float(r["Age"]), float(r["Error"])
        r["lab"], r["labnum"] = r1.lab_of(r["LabID"])
        r["cls"], r["reservoir"] = r1.classify(r["Material"], r["Taxa"])
        r["ref_year"] = r1.earliest_ref_year(r["Reference"])
        r["region"] = region_of(r, regions)

    # ---- sites exactly as R1: normalised name within continent and country, split by province
    base = defaultdict(list)
    for i, r in enumerate(rows):
        n = r1.norm_name(r["SiteName"])
        if n not in r1.PLACEHOLDER_NAMES:
            base[(r["Continent"], r["Country"], n)].append(i)
    sites, site_of = defaultdict(list), {}
    for k, idxs in base.items():
        provs = {rows[i]["Province"] for i in idxs if rows[i]["Province"]}
        for i in idxs:
            prov = (rows[i]["Province"] or None) if len(provs) >= 2 else (next(iter(provs)) if provs else None)
            sites[k + (prov,)].append(i)
            site_of[i] = k + (prov,)

    def site_display(skey):
        c = Counter(rows[i]["SiteName"] for i in sites[skey])
        return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    labnum_index = defaultdict(set)
    for r in rows:
        if r["labnum"] is not None:
            labnum_index[(r["lab"], r["labnum"])].add(r["LabID"])

    # ---- thresholds ----------------------------------------------------------------------
    thr = {}
    for g in regions:
        T, sT, tcal = threshold(curve, g["limit_cal_bp"])
        thr[g["id"]] = {"limit_cal_bp": g["limit_cal_bp"], "threshold_14C_BP": round(T, 1),
                        "curve_sigma": round(sT, 1), "reached_at_cal_BP": round(tcal, 1),
                        "untestable_by_design": T >= MAX_AGE}

    def z(i):
        r, t = rows[i], thr[rows[i]["region"]]
        return (r["age"] - t["threshold_14C_BP"]) / math.hypot(r["err"], t["curve_sigma"])

    # ---- selection and R1's mundane filters, in R1's order --------------------------------
    in_reg = [i for i, r in enumerate(rows) if r["region"]]
    named = [i for i in in_reg if i in site_of]
    pre_any = [i for i in in_reg if z(i) > SE_MULT]
    pre = [i for i in named if z(i) > SE_MULT]
    a = [i for i in pre if not rows[i]["reservoir"]]
    is_old_bone = lambda i: rows[i]["cls"] == BONE and (rows[i]["ref_year"] is None or rows[i]["ref_year"] < BONE_YEAR)
    b = [i for i in a if not is_old_bone(i)]
    c = [i for i in b if rows[i]["age"] <= MAX_AGE]
    d1 = [i for i in c if len(labnum_index[(rows[i]["lab"], rows[i]["labnum"])]) == 1]  # R1's rule, as coded
    seen, cands = set(), []
    for i in sorted(d1, key=lambda i: (site_display(site_of[i]).lower(), rows[i]["LabID"])):
        k = (rows[i]["lab"], rows[i]["age"], rows[i]["err"])
        if k not in seen:
            seen.add(k)
            cands.append(i)
    stages = [("dates in a defined region", in_reg), ("with a usable site name", named),
              (f"older than the limit by > {SE_MULT:g} SE", pre),
              ("after (a) reservoir-prone materials", a), ("after (b) bone before 1990 / year unknown", b),
              ("after (c) ages over 40,000 14C BP", c), ("after (d) split or duplicate samples = candidates", cands)]
    removed = {
        "pre_limit_dates_without_usable_site_name": len(pre_any) - len(pre),
        "a_reservoir_prone": dict(Counter(rows[i]["reservoir"] for i in pre if rows[i]["reservoir"])),
        "b_bone": {"reference_year_before_1990": sum(rows[i]["ref_year"] is not None for i in a if is_old_bone(i)),
                   "no_reference_year": sum(rows[i]["ref_year"] is None for i in a if is_old_bone(i))},
        "c_over_40000": len(b) - len(c),
        "d_split_or_duplicate": {"lab_number_shared_or_missing": len(c) - len(d1),
                                 "same_lab_age_error_elsewhere": len(d1) - len(cands)},
    }

    # ---- per region -------------------------------------------------------------------------
    by_reg = {g["id"]: [] for g in regions}
    for i in cands:
        by_reg[rows[i]["region"]].append(i)
    region_rows, leads = [], []
    for g in regions:
        gid, js = g["id"], by_reg[g["id"]]
        funnel = {name: sum(rows[i]["region"] == gid for i in lst) for name, lst in stages}
        skeys = sorted({site_of[i] for i in js}, key=lambda s: site_display(s).lower())
        labs = sorted({rows[i]["lab"] for i in js} - {"?"})
        classes = sorted({rows[i]["cls"] for i in js} - {UNKNOWN})
        is_lead = len(skeys) >= MIN_SITES and len(labs) >= MIN_LABS and len(classes) >= MIN_CLASSES
        if funnel["dates in a defined region"] == 0:
            status = "untestable: no p3k14c rows"
        elif thr[gid]["untestable_by_design"]:
            status = "untestable by design: limit is beyond R1's 40,000 14C BP filter"
        elif is_lead:
            status = "LEAD"
        else:
            status = "not a lead"
        site_list = []
        for s in skeys:
            mine = sorted((i for i in js if site_of[i] == s), key=lambda i: -rows[i]["age"])
            name = site_display(s)
            dates = []
            for i in mine:
                r = rows[i]
                lo, hi = r1.cal_range(mean_curve, r["age"] - 2 * r["err"], r["age"] + 2 * r["err"])
                dates.append({"LabID": r["LabID"], "age_14C_BP": r["age"], "error": r["err"],
                              "z_over_limit": round(z(i), 1),
                              "approx_cal_BP_2sigma": [round(lo, -1), round(hi, -1)] if lo is not None else None,
                              "lab": r["lab"], "material": r["Material"], "taxa": r["Taxa"],
                              "material_class": r["cls"], "reference_year": r["ref_year"],
                              "p3k14c_source": r["Source"], "reference": r["Reference"][:200]})
            site_list.append({"site": name, "country": s[1], "province": s[3],
                              "dates_at_site": len(sites[s]),
                              "pre_limit_dates_before_filters": sum(1 for i in pre if site_of[i] == s),
                              "candidate_dates": len(mine), "labs": sorted({d["lab"] for d in dates}),
                              "material_classes": sorted({d["material_class"] for d in dates}),
                              "recognized": RECOGNIZED.get(r1.norm_name(name)), "dates": dates})
        row = {"id": gid, "name": g["name"], **thr[gid], "funnel": funnel, "n_sites": len(skeys),
               "labs": labs, "known_material_classes": classes, "status": status,
               "pre_limit_dates_by_continent_before_filters": dict(Counter(rows[i]["Continent"] for i in pre if rows[i]["region"] == gid)),
               "kept_dates_by_continent": dict(Counter(rows[i]["Continent"] for i in js)),
               "kept_dates_by_class": dict(Counter(rows[i]["cls"] for i in js)),
               "kept_dates_by_p3k14c_source": dict(Counter(rows[i]["Source"] for i in js)),
               "annotation_after_scan": LEAD_NOTES.get(gid), "source_short": short_source(g["source"]["citation"]),
               "source_doi": g["source"]["doi"], "sites": site_list}
        region_rows.append(row)
        if is_lead:
            leads.append(gid)

    summary = {
        "method": "R2 frontier scan (pre-registered 2026-09-23, findings/log.md); limits fixed in "
                  "analysis/frontier/limits.json, commit " + LIMITS_COMMIT,
        "script": "scripts/frontier/scan.py (reuses scripts/residue/scan.py for loading, sites, labs, materials, filters)",
        "limits_file": {"path": "analysis/frontier/limits.json", "sha256": limits_sha, "commit": LIMITS_COMMIT},
        "data": {**r1.DATA_INFO, "sha256": data_sha, "rows": len(rows)},
        "calibration_curve": {**r1.INTCAL_INFO, "sha256": intcal_sha,
                              "use": "limit -> 14C threshold (oldest mean age at or younger than the limit, "
                                     "with the curve's 1-sigma); approximate calendar ranges for display"},
        "parameters": {"se_multiple": SE_MULT, "lead_min_sites": MIN_SITES, "lead_min_labs": MIN_LABS,
                       "lead_min_known_material_classes": MIN_CLASSES, "max_age_14C_BP": MAX_AGE,
                       "bone_year": BONE_YEAR,
                       "notes": ["An unknown laboratory ('?', LabID without letters) and the 'unknown' material class "
                                 "never count toward the lead rule's distinct labs or classes.",
                                 "Filter (d) is R1's code as run: a date is removed if its lab number is shared with "
                                 "another LabID or missing, then identical lab+age+error at another site counts once."]},
        "funnel": [{"stage": s, "dates": len(lst), "sites": len({site_of[i] for i in lst if i in site_of})}
                   for s, lst in stages],
        "removed_by_filter": removed,
        "regions": region_rows,
        "leads": leads,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "r2_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "r2_report.md").write_text(report(summary), encoding="utf-8")
    print(json.dumps({"funnel": summary["funnel"], "removed": removed,
                      "regions": [{k: r[k] for k in ("id", "threshold_14C_BP", "curve_sigma", "status", "n_sites", "labs",
                                                     "known_material_classes")} | {"funnel": list(r["funnel"].values())}
                                  for r in region_rows], "runtime": summary["runtime_seconds"]}, indent=1, ensure_ascii=False))


def fmt(n):
    return f"{int(round(n)):,}"


def short_source(citation):
    authors = citation.split(" (")[0]
    parts = [p for p in re.split(r"\.,\s*", authors) if p.strip()]
    names = [p.split(",")[0].strip() for p in parts]
    year = re.search(r"\((\d{4})", citation).group(1)
    who = names[0] if len(names) == 1 else f"{names[0]} & {names[1]}" if len(names) == 2 else f"{names[0]} et al."
    return f"{who} {year}"


def report(s):
    f, regs, rm = s["funnel"], s["regions"], s["removed_by_filter"]
    lead_regs = [r for r in regs if r["status"] == "LEAD"]
    L = ["# R2 · Frontier scan: dates older than the accepted first arrival", "",
         "*Run 2026-09-23 with `scripts/frontier/scan.py`. Pre-registered in `findings/log.md` (R2); regions, limits and the "
         f"conversion rule were fixed in `limits.json` and pushed before the scan (commit {s['limits_file']['commit'].split()[0]}). "
         "Detail: `r2_summary.json`. No coordinates were read; sites are named only.*", ""]
    if lead_regs:
        L.append(f"**Result: {len(lead_regs)} region(s) meet the lead rule: {' and '.join(SHORT[r['id']] for r in lead_regs)}.** "
                 "A lead is a list for the researcher and skeptic, not a finding; read the note under each.")
    else:
        L.append("**Result: null.** No region has pre-limit dates at ≥ 3 sites with ≥ 2 labs and ≥ 2 material classes.")
    L += ["", "**Method.** Each limit (calendar years BP) became a radiocarbon threshold: the oldest age the IntCal20 mean "
          "curve reaches at or after the limit, with the curve's own error (IntCal20 everywhere, slightly permissive in the "
          "south). A date counts if it is older than that by more than 2 combined standard errors and survives R1's filters. "
          "Lead = at least 3 sites, 2 labs and 2 known material classes between them.",
          "", "## Funnel", "", "| Stage | Dates | Sites |", "|---|---:|---:|"]
    L += [f"| {x['stage']} | {x['dates']:,} | {x['sites']:,} |" for x in f]
    rsv = rm["a_reservoir_prone"]
    L += ["", f"Pre-limit dates with no usable site name: {rm['pre_limit_dates_without_usable_site_name']}. Removed: "
          f"reservoir-prone {sum(rsv.values())} (" + ", ".join(f"{k} {v}" for k, v in sorted(rsv.items(), key=lambda kv: -kv[1])) +
          f"); bone {rm['b_bone']['reference_year_before_1990']} pre-1990 + {rm['b_bone']['no_reference_year']} no year; "
          f"over 40,000: {rm['c_over_40000']}; split/duplicate or no lab number: "
          f"{sum(rm['d_split_or_duplicate'].values())}.",
          "", "## Regions", "",
          "| Region | Limit, cal BP (source) | 14C threshold | Dates | Pre-limit | Kept | Sites | Labs | Classes | Result |",
          "|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    status_short = {"LEAD": "**lead**", "not a lead": "no",
                    "untestable: no p3k14c rows": "untestable: no rows",
                    "untestable by design: limit is beyond R1's 40,000 14C BP filter": "untestable: beyond 40k filter"}
    for r in regs:
        fu = list(r["funnel"].values())
        L.append(f"| {SHORT[r['id']]} | {r['limit_cal_bp']:,} ({r['source_short']}) | {fmt(r['threshold_14C_BP'])} ± "
                 f"{fmt(r['curve_sigma'])} | {fu[0]:,} | {fu[2]:,} | {fu[-1]:,} | {r['n_sites']} | {len(r['labs'])} | "
                 f"{len(r['known_material_classes'])} | {status_short.get(r['status'], r['status'])} |")

    def ka(d):
        c = d["approx_cal_BP_2sigma"]
        if not c:
            return "beyond curve"
        lo, hi = f"{c[0] / 1000:.1f}", f"{c[1] / 1000:.1f}"
        return f"~{lo} ka cal" if lo == hi else f"~{lo}–{hi} ka cal"

    def one(d):
        mat = (d["material"] or "material not given").split(";")[0].strip().lower()
        return f"{d['LabID']} {fmt(d['age_14C_BP'])} ± {fmt(d['error'])} ({ka(d)}, {mat})"

    def line(x, ds, cap):
        more = f"; +{len(ds) - cap} more" if len(ds) > cap else ""
        return (f"{x['site']} ({x['province'] or x['country']}; {x['candidate_dates']} of {x['dates_at_site']} dates kept; "
                f"{', '.join(x['labs'])}): " + "; ".join(one(d) for d in ds[:cap]) + more)

    tag = lambda x: x["recognized"].split(" (", 1)[1].rstrip(")") if "(" in x["recognized"] else x["recognized"]
    nonbone = lambda x: [d for d in x["dates"] if d["material_class"] not in (BONE, UNKNOWN)]
    for r in lead_regs:
        xs_all = r["sites"]
        famous = [x for x in xs_all if (x["recognized"] or "").startswith(FAMOUS)]
        known = [x for x in xs_all if (x["recognized"] or "").startswith(KNOWN)]
        unk_other = [x for x in xs_all if not x["recognized"] and nonbone(x)]
        unk_bone = [x for x in xs_all if not x["recognized"] and not nonbone(x)]
        L += ["", f"## Lead: {SHORT[r['id']]}", "",
              f"{r['n_sites']} sites, {sum(x['candidate_dates'] for x in xs_all)} kept dates, {len(r['labs'])} labs. Classes: " +
              ", ".join(f"{k} {v}" for k, v in sorted(r["kept_dates_by_class"].items(), key=lambda kv: -kv[1])) +
              ". Compilations: " + ", ".join(f"{k} {v}" for k, v in sorted(r["kept_dates_by_p3k14c_source"].items(), key=lambda kv: -kv[1])) +
              ". Continents (kept / before filters): " + ", ".join(
                  f"{k} {r['kept_dates_by_continent'].get(k, 0)}/{v}" for k, v in sorted(r["pre_limit_dates_by_continent_before_filters"].items(), key=lambda kv: -kv[1])) +
              f". Sites with only animal-bone or unspecified dates: {len([x for x in xs_all if not nonbone(x)])} of {r['n_sites']}. "
              "'Recognized' means from general knowledge; nothing about the leads was looked up."]
        if r.get("annotation_after_scan"):
            L += ["", "*Note written after the scan, from the database fields only:* " + r["annotation_after_scan"]]
        if famous:
            L += ["", f"**Recognized as famous early-arrival controversies** ({len(famous)} sites):"]
            by_tag = defaultdict(list)
            for x in famous:
                by_tag[tag(x)].append(x)
            for t, xs in by_tag.items():
                if len(xs) == 1:
                    L.append(f"- {t}: " + line(xs[0], xs[0]["dates"], 3))
                else:
                    ds = [d for x in xs for d in x["dates"]]
                    mats = Counter((d["material"] or "not given").split(";")[0].strip().lower() for d in ds)
                    L.append(f"- {t}: {len(xs)} localities ({', '.join(x['site'] for x in xs)}); {len(ds)} dates, "
                             f"{fmt(min(d['age_14C_BP'] for d in ds))}–{fmt(max(d['age_14C_BP'] for d in ds))} 14C BP; "
                             + ", ".join(f"{m} {n}" for m, n in mats.most_common()) + f"; labs {', '.join(sorted({d['lab'] for d in ds}))}")
        if known:
            L += ["", f"**Recognized sites, but not (to my knowledge) for a claim this old** ({len(known)}):"]
            L += [f"- {line(x, x['dates'], 1)} — {tag(x)}" for x in known]
        if unk_other:
            L += ["", f"**Not recognized, with dates on charcoal, wood, plants, soil or other organics** ({len(unk_other)}; "
                  "only those dates shown, the count includes any bone dates):"]
            L += [f"- {line(x, nonbone(x), 2)}" for x in unk_other]
        if unk_bone:
            L += ["", f"**Not recognized, dated only on animal bone or unspecified material** ({len(unk_bone)}; kept dates, oldest 14C BP): "
                  + "; ".join(f"{x['site']} ({x['candidate_dates']}; {fmt(x['dates'][0]['age_14C_BP'])})" for x in unk_bone) + "."]
    others = [r for r in regs if r["status"] == "not a lead" and r["n_sites"]]
    if others:
        L += ["", "**Non-lead regions with candidates:** " + "; ".join(
            f"{SHORT[r['id']]}: " + ", ".join(line(x, x["dates"], 1) for x in r["sites"]) for r in others) + "."]
    L += ["", "## Caveats",
          "- p3k14c has no rows for the Caribbean islands, western Remote Oceania, New Zealand or Madagascar, and only Rapa Nui "
          "for East Polynesia. Sahul cannot be tested by radiocarbon under R1's 40,000 14C BP filter. None of these are nulls.",
          "- p3k14c does not record whether a date is cultural. A date on fossil bone or natural wood below a site passes every "
          "R1 filter, and dates excavators rejected may be missing altogether.",
          "- One limit covers each whole region, so areas settled later (Hokkaido, the Ryukyus, the later Polynesian pulse) are "
          "tested conservatively. Materials were classed by keywords; the bone filter uses the reference year as a proxy.",
          "", "## Next step",
          "Per R2 step 4, each lead goes to a researcher and a skeptic: is each site already debated, and is there a mundane "
          "cause (non-cultural sample, miscoded country, contamination)? No literature on the leads was consulted for this run."
          if lead_regs else "Record the null in `findings/log.md` under R2."]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    main()
