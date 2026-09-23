#!/usr/bin/env python3
"""R1 · Coherent residue scan: do dismissed radiocarbon dates line up?

Implements the pre-registered method R1 in findings/log.md exactly as worded there and in
its "R1 clarification (before running)" (commit d1013c1; moved under the R1 entry in
625227f). Standard library only, fixed random seed. The Long/Lat columns are dropped as
each row is read, so no coordinate can reach any output.

Run from the repository root:
    python3 scripts/residue/scan.py
Writes:
    analysis/residue/r1_summary.json   counts after each stage, every tested region, survivors
    analysis/residue/r1_report.md      one-page plain-language report
"""
import csv
import hashlib
import json
import math
import random
import re
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/raw/p3k14c_scrubbed_fuzzed_2022.06.csv"
INTCAL = ROOT / "data/raw/intcal20.14c"
OUT = ROOT / "analysis/residue"

DATA_INFO = {
    "name": "p3k14c (Bird et al. 2022, Scientific Data, doi:10.1038/s41597-022-01118-7)",
    "release": "v2022.06 public scrubbed-and-fuzzed CSV (identical file in package release 2025.07)",
    "source_url": "https://raw.githubusercontent.com/people3k/p3k14c/"
                  "ce16085396b54fc5bd8360f7efb60cf3cf81e1af/inst/p3k14c_scrubbed_fuzzed.csv",
    "repository": "https://github.com/people3k/p3k14c at commit ce16085396b54fc5bd8360f7efb60cf3cf81e1af",
    "canonical_archive": "https://core.tdar.org/collection/70213/p3k14c-data "
                         "(refused automated download, HTTP 403)",
    "expected_sha256": "5c92b7ae96959bc2924409cf66a8919aac955a4abac5545fad26f3fb209eca0c",
}
INTCAL_INFO = {
    "name": "IntCal20 (Reimer et al. 2020, Radiocarbon 62(4), doi:10.1017/RDC.2020.41)",
    "source_url": "https://intcal.org/curves/intcal20.14c",
    "expected_sha256": "974a66649f2ac8a53e6c99e256b019ac6982f999b12dcf7193162d4c1c09168e",
}

# ---- Registered parameters (findings/log.md, R1) -- never tuned -----------------------
MIN_DATES = 5          # sites with >= 5 dates
OUTLIER_SE = 3.0       # older than every other date by > 3 combined standard errors
ISOLATION_SIGMA = 2.0  # no other date within 2 sigma
WINDOW_SIGMA = 2.0     # clusters: outliers whose 2-sigma ranges share one point
MAX_AGE = 40000        # filter: dates beyond 40,000 radiocarbon years
BONE_YEAR = 1990       # filter: bone dated before 1990 without stated collagen QC
N_PERM = 10000
SEED = 20260923
ALPHA = 0.01           # after Bonferroni across regions tested

KEEP = ("LabID", "Age", "Error", "Material", "Taxa", "SiteName", "Country", "Province",
        "Continent", "Source", "Reference")  # Long, Lat, LocAccuracy are never kept
MISSING = {"", "NA", "N/A", "na", "NaN", "nan", "NULL", "null", "None", "-"}
PLACEHOLDER_NAMES = {"", "unknown", "unknown site", "unnamed", "unnamed site", "not specified",
                     "unspecified", "na", "n a", "nd", "n d", "none", "no name", "noname", "site",
                     "sin nombre", "various", "misc", "miscellaneous", "not given", "unk"}

# Conventional and AMS lab codes of one institution (clarification, "Independence").
LAB_ALIASES = {
    "GRN": "GRONINGEN", "GRA": "GRONINGEN", "GRM": "GRONINGEN", "GRO": "GRONINGEN",
    "GIF": "GIF", "GIFA": "GIF", "LY": "LYON", "LYON": "LYON", "UB": "BELFAST", "UBA": "BELFAST",
    "UGA": "GEORGIA", "UGAMS": "GEORGIA", "A": "ARIZONA", "AA": "ARIZONA",
    "T": "TRONDHEIM", "TUA": "TRONDHEIM", "HEL": "HELSINKI", "HELA": "HELSINKI",
    "NZ": "RAFTER", "NZA": "RAFTER", "GU": "GLASGOW", "SUERC": "GLASGOW",
    "LU": "LUND", "LUA": "LUND", "LUS": "LUND", "U": "UPPSALA", "UA": "UPPSALA",
    "KN": "KOELN", "COL": "KOELN", "ISGS": "ISGS", "ISGSA": "ISGS",
}

# ---- Material classification (clarification, "Mundane filters" and "Material classes") --
SHELL_GENERA = ("anadara|mytilus|haliotis|crassostrea|ostrea|mercenaria|rangia|tridacna|strombus|"
                "donax|tegula|saxidomus|protothaca|leukoma|chione|cerastoderma|patella|littorina|"
                "busycon|spondylus|glycymeris|macoma|cardium|pecten|nerita|polymesoda|geloina|"
                "batissa|corbicula|unio|anodonta|lampsilis|helix|cepaea|achatina|margaritifera|"
                "mesodesma|concholepas|choromytilus|fissurella|perna|modiolus|trochus|cypraea|"
                "terebralia|telescopium|melanoides|venus|pinctada|placuna|tapes|ruditapes|arca|"
                "scutellastra|turbo|conus|nassarius|dentalium|neritina|pila|viviparus|bellamya")
AQUATIC_GENERA = ("phoca|pusa|halichoerus|odobenus|eumetopias|zalophus|callorhinus|arctocephalus|"
                  "otaria|mirounga|delphinus|tursiops|phocoena|balaena|balaenoptera|eubalaena|"
                  "megaptera|physeter|orcinus|monodon|delphinapterus|trichechus|dugong|enhydra|"
                  "oncorhynchus|salmo|gadus|clupea|thunnus|acipenser|esox|perca|silurus|sparus|"
                  "pagrus|chelonia|cyprinus|lates|clarias")
RE_FIRED_CLAY = re.compile(r"\b(fired|burnt|burned|baked)\s+clay\b")
RE_NUTSHELL = re.compile(r"\bnut\s*-?\s*shells?\b|\bnutshells?\b")
RE_EGGSHELL = re.compile(r"\begg\s*-?\s*shells?\b|\beggshells?\b")
RESERVOIR_RULES = [  # checked on Material + Taxa, in this order
    ("carbonate", RE_EGGSHELL),
    ("shell", re.compile(r"shell|coquill|mollus|mussel|oyster|\bclams?\b|snail|gastropod|bivalv|"
                         r"limpet|whelk|cockle|conch|periwinkle|scallop|operculum|\b(" +
                         SHELL_GENERA + r")\b")),
    ("carbonate", re.compile(r"carbonate|caliche|calcrete|\btufa|travertine|speleothem|stalagm|"
                             r"stalact|flowstone|\bmarl|calcite|aragonite|mortar|plaster|\blime\b|"
                             r"limestone|coral|concretion")),
    ("aquatic animal", re.compile(r"marine|freshwater|fresh water|\bfish|salmon|\bcod\b|herring|"
                                  r"\bwhales?\b|baleine|\bseals?\b|phoque|walrus|\bmorse\b|sea lion|"
                                  r"sea otter|dolphin|porpoise|narwhal|beluga|\bsea\b|aquatic|"
                                  r"seaweed|kelp|\bcrabs?\b|lobster|urchin|turtle|pinniped|"
                                  r"cetacean|sturgeon|\beels?\b|\b(" + AQUATIC_GENERA + r")\b")),
    ("food residue", re.compile(r"residu|\bcrusts?\b|foodcrust|encrust")),
    ("sediment", re.compile(r"sediment|gyttja|\bmud\b|\bsilts?\b|\bclay\b|lacustr|\blake\b|\booze\b|"
                            r"detritus|sapropel|limnic|diatom")),
    ("fossil carbon", re.compile(r"bitumen|asphalt|\bcoal\b|lignite|graphite|petroleum")),
]
BONE = "bone/tooth/antler"
UNKNOWN = "unknown"
CLASS_RULES = [  # checked on Material (then Taxa if Material gives nothing), in this order
    (BONE, re.compile(r"\bbone|\bos\b|osseu|\bossa?\b|collag|antler|\btooth|\bteeth|dentin|enamel|"
                      r"ivory|ivoire|\btusks?\b|\bhorns?\b|cremat|calcin|apatite|skull|skeleton|"
                      r"mandible|femur|bois de (renne|cerf|caribou)")),
    ("charcoal/wood", re.compile(r"charcoal|charbon|\bwoods?\b|\bbois\b|timber|\blogs?\b|twig|\bbark\b|"
                                 r"branch|roundwood|sapwood|heartwood|tree ?rings?|\bstumps?\b|"
                                 r"\btrunks?\b|\bplanks?\b|\bposts?\b|\bbeams?\b")),
    ("short-lived plant", re.compile(r"seed|grain|cereal|maize|\bzea\b|\bcorn\b|\bcobs?\b|kernel|"
                                     r"cupule|nuthull|\bnuts?\b|acorn|hazel|fruit|\brice\b|barley|"
                                     r"wheat|millet|\boats?\b|\brye\b|sorghum|pennisetum|straw|grass|"
                                     r"\breeds?\b|\bleaf|leaves|\bplants?\b|plantes?\b|macrofossil|"
                                     r"macro-fossil|cultig|\bbeans?\b|squash|cucurbit|chaff|tuber|"
                                     r"pollen|\bstems?\b")),
    ("other organic", re.compile(r"textile|fib(er|re)|cloth|leather|\bhides?\b|\bskins?\b|\bhair|"
                                 r"\bwool|\bfur\b|feather|basket|cordage|\bropes?\b|\bstrings?\b|"
                                 r"\bmats?\b|lacquer|resin|\bwax|feces|faeces|dung|coprolit|excrement|"
                                 r"tissue|mumm|\bblood|food remains|sinew|parchment|\bpaper|papyrus")),
    ("pottery/temper", re.compile(r"potter|ceramic|sherd|\btemper|\bvessel|\bbricks?\b|\bdaub")),
    ("soil/peat/humate", re.compile(r"\bsoils?\b|paleosol|palaeosol|humic|humate|humin|\bpeat|tourbe|"
                                    r"organic|humus|\bsod\b|\bturf\b")),
]
RE_YEAR = re.compile(r"(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)")


def clean(v):
    v = (v or "").strip()
    return "" if v in MISSING else v


def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def norm_name(s):
    s = re.sub(r"['’`´]", "", fold(s))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def classify(material, taxa):
    """Return (material class, reservoir reason or None)."""
    def prep(s):
        s = RE_FIRED_CLAY.sub(" firedceramic ", fold(s))
        return RE_NUTSHELL.sub(" nuthull ", s)
    both = prep(material) + " | " + prep(taxa)
    reason = next((name for name, rx in RESERVOIR_RULES if rx.search(both)), None)
    cls = UNKNOWN
    for text in (prep(material), prep(taxa)):
        cls = next((name for name, rx in CLASS_RULES if rx.search(text)), UNKNOWN)
        if cls != UNKNOWN:
            break
    return cls, reason


def lab_of(labid):
    m = re.match(r"\s*([A-Za-z]+)", labid)
    prefix = m.group(1).upper() if m else "?"
    n = re.search(r"\d+", labid)
    number = (n.group(0).lstrip("0") or "0") if n else None
    return LAB_ALIASES.get(prefix, prefix), number


def earliest_ref_year(ref):
    years = [int(y) for y in RE_YEAR.findall(ref or "") if 1950 <= int(y) <= 2026]
    return min(years) if years else None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def max_overlap(intervals):
    """Largest number of closed intervals sharing one point (sweep line)."""
    events = []
    for lo, hi in intervals:
        events.append((lo, 0))  # starts sort before ends at the same point: touching overlaps
        events.append((hi, 1))
    events.sort()
    cur = best = 0
    for _, kind in events:
        if kind == 0:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur -= 1
    return best


def load_intcal(path):
    pts = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(",")
        pts.append((float(parts[0]), float(parts[1])))
    return sorted(pts)


def cal_range(curve, a, b):
    """Calendar range (cal BP) where the IntCal20 mean curve lies inside [a, b] 14C BP."""
    lo = hi = None
    for (t1, c1), (t2, c2) in zip(curve, curve[1:]):
        if max(c1, c2) < a or min(c1, c2) > b:
            continue
        if c1 == c2:
            s0, s1 = t1, t2
        else:
            ta = t1 + (a - c1) * (t2 - t1) / (c2 - c1)
            tb = t1 + (b - c1) * (t2 - t1) / (c2 - c1)
            s0, s1 = max(t1, min(ta, tb)), min(t2, max(ta, tb))
        if s0 > s1:
            continue
        lo = s0 if lo is None else min(lo, s0)
        hi = s1 if hi is None else max(hi, s1)
    return lo, hi


def self_test():
    assert max_overlap([(0, 1), (1, 2), (3, 4)]) == 2
    assert max_overlap([(0, 10), (2, 3), (4, 5), (2.5, 4.5)]) == 3
    assert classify("Marine shell", "")[1] == "shell"
    assert classify("Hazel nutshell", "") == ("short-lived plant", None)
    assert classify("whale bone collagen; collagène osseux de baleine", "")[1] == "aquatic animal"
    assert classify("bison bone collagen", "") == (BONE, None)
    assert classify("POTTERYRESIDUE", "")[1] == "food residue"
    assert classify("charcoal; charbon de bois", "") == ("charcoal/wood", None)
    assert classify("Charred Remain", "") == (UNKNOWN, None)
    assert classify("", "Zea mays") == ("short-lived plant", None)
    assert lab_of("GrA-12345") == ("GRONINGEN", "12345") and lab_of("Beta-012") == ("BETA", "12")
    assert earliest_ref_year("Smith 1985; Jones 2003, p. 1234") == 1985


def region_label(region):
    cont, country, prov = region
    return " / ".join(x for x in (cont, country or "country not given", prov) if x)


def main():
    t0 = time.time()
    self_test()
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    data_sha, intcal_sha = sha256(DATA), sha256(INTCAL)
    assert data_sha == DATA_INFO["expected_sha256"], "p3k14c file differs from the registered one"
    assert intcal_sha == INTCAL_INFO["expected_sha256"], "IntCal20 file differs"

    # ---- load (coordinates dropped immediately) ---------------------------------------
    rows = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({k: clean(r.get(k)) for k in KEEP})
    for r in rows:
        r["age"], r["err"] = float(r["Age"]), float(r["Error"])
        r["lab"], r["labnum"] = lab_of(r["LabID"])
        r["cls"], r["reservoir"] = classify(r["Material"], r["Taxa"])

    # ---- sites and regions --------------------------------------------------------------
    by_country = defaultdict(lambda: [0, 0])
    for r in rows:
        by_country[r["Country"]][1 if r["Province"] else 0] += 1
    province_countries = sorted(c for c, (no, yes) in by_country.items() if yes > no)
    base = defaultdict(list)
    for i, r in enumerate(rows):
        n = norm_name(r["SiteName"])
        if n not in PLACEHOLDER_NAMES:
            base[(r["Continent"], r["Country"], n)].append(i)
    sites = defaultdict(list)
    for key, idxs in base.items():
        provs = {rows[i]["Province"] for i in idxs if rows[i]["Province"]}
        for i in idxs:
            prov = (rows[i]["Province"] or None) if len(provs) >= 2 else (next(iter(provs)) if provs else None)
            sites[key + (prov,)].append(i)
    n_usable = sum(len(v) for v in sites.values())

    def site_region(skey):
        cont, country, _, prov = skey
        if country in province_countries:
            return (cont, country, prov or "province not given")
        return (cont, country, None)

    def site_display(idxs):
        c = Counter(rows[i]["SiteName"] for i in idxs)
        return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    # ---- outliers -----------------------------------------------------------------------
    labnum_index = defaultdict(set)
    for r in rows:
        if r["labnum"] is not None:
            labnum_index[(r["lab"], r["labnum"])].add(r["LabID"])
    eligible = {k: v for k, v in sites.items() if len(v) >= MIN_DATES}
    outliers, isolation_violations = [], 0
    for skey, idxs in eligible.items():
        ds = sorted((rows[i] for i in idxs), key=lambda r: -r["age"])
        d, others = ds[0], ds[1:]
        if all(d["age"] - o["age"] > OUTLIER_SE * math.hypot(d["err"], o["err"]) for o in others):
            if not all(abs(d["age"] - o["age"]) > ISOLATION_SIGMA * (d["err"] + o["err"]) for o in others):
                isolation_violations += 1  # cannot happen (3*sqrt(a2+b2) > 2*(a+b)); checked anyway
                continue
            outliers.append({
                "site_key": skey, "site": site_display(idxs), "region": site_region(skey),
                "continent": skey[0], "n_site_dates": len(idxs),
                "second_oldest": others[0]["age"], "LabID": d["LabID"], "lab": d["lab"],
                "labnum": d["labnum"], "age": d["age"], "err": d["err"], "Material": d["Material"],
                "Taxa": d["Taxa"], "cls": d["cls"], "reservoir": d["reservoir"],
                "ref_year": earliest_ref_year(d["Reference"]), "Source": d["Source"],
                "Reference": d["Reference"][:200],
            })
    outliers.sort(key=lambda o: (o["site"].lower(), o["LabID"]))

    # ---- mundane filters, in registered order ------------------------------------------
    funnel = [("all dates in the release", len(rows), None),
              ("dates with a usable site name", n_usable, len(sites)),
              (f"dates at sites with ≥ {MIN_DATES} dates", sum(len(v) for v in eligible.values()), len(eligible)),
              ("isolated old outliers (one per site at most)", len(outliers), len(outliers))]
    removed = {}
    stage = outliers
    a_kept = [o for o in stage if not o["reservoir"]]
    removed["a_reservoir_prone"] = dict(Counter(o["reservoir"] for o in stage if o["reservoir"]))
    funnel.append(("after (a) reservoir-prone materials", len(a_kept), len(a_kept)))
    b_kept = [o for o in a_kept if not (o["cls"] == BONE and (o["ref_year"] is None or o["ref_year"] < BONE_YEAR))]
    b_gone = [o for o in a_kept if o["cls"] == BONE and (o["ref_year"] is None or o["ref_year"] < BONE_YEAR)]
    removed["b_bone_pre1990_or_undated"] = {"reference_year_before_1990": sum(o["ref_year"] is not None for o in b_gone),
                                            "no_reference_year": sum(o["ref_year"] is None for o in b_gone)}
    funnel.append(("after (b) bone before 1990 / year unknown", len(b_kept), len(b_kept)))
    c_kept = [o for o in b_kept if o["age"] <= MAX_AGE]
    removed["c_over_40000"] = len(b_kept) - len(c_kept)
    funnel.append(("after (c) ages over 40,000 14C BP", len(c_kept), len(c_kept)))
    d1 = [o for o in c_kept if len(labnum_index[(o["lab"], o["labnum"])]) == 1]
    seen, d_kept = set(), []
    for o in d1:  # already sorted by site name, so the first site alphabetically is kept
        k = (o["lab"], o["age"], o["err"])
        if k not in seen:
            seen.add(k)
            d_kept.append(o)
    removed["d_duplicates_splits"] = {"split_or_duplicate_lab_number": len(c_kept) - len(d1),
                                      "same_age_error_lab_at_another_site": len(d1) - len(d_kept)}
    funnel.append(("after (d) duplicate or split samples = candidates", len(d_kept), len(d_kept)))
    cands = d_kept

    # ---- regions and the coherence statistic -------------------------------------------
    for o in cands:
        o["lo"], o["hi"] = o["age"] - WINDOW_SIGMA * o["err"], o["age"] + WINDOW_SIGMA * o["err"]
    by_region = defaultdict(list)
    for j, o in enumerate(cands):
        by_region[o["region"]].append(j)
    known = lambda js: {cands[j]["cls"] for j in js} - {UNKNOWN}
    tested = sorted(reg for reg, js in by_region.items()
                    if len({cands[j]["site_key"] for j in js}) >= 2
                    and len({cands[j]["lab"] for j in js}) >= 2 and len(known(js)) >= 2)
    m = len(tested)
    s_obs = {reg: max_overlap([(cands[j]["lo"], cands[j]["hi"]) for j in by_region[reg]]) for reg in tested}

    # ---- permutation null: shuffle (age, error) among outlier slots within continent ----
    ge = Counter()
    by_cont = defaultdict(list)
    for j, o in enumerate(cands):
        by_cont[o["continent"]].append(j)
    for cont in sorted(by_cont):
        slots = by_cont[cont]
        pos = {j: p for p, j in enumerate(slots)}
        pairs = [(cands[j]["lo"], cands[j]["hi"]) for j in slots]
        regs = [(reg, [pos[j] for j in by_region[reg]], s_obs[reg]) for reg in tested if reg[0] == cont]
        if not regs:
            continue
        perm = list(range(len(slots)))
        for _ in range(N_PERM):
            rng.shuffle(perm)
            for reg, members, s in regs:
                if max_overlap([pairs[perm[p]] for p in members]) >= s:
                    ge[reg] += 1

    curve = load_intcal(INTCAL)

    def windows(reg):
        js = by_region[reg]
        s = s_obs[reg]
        sets = []
        for j in js:
            t = cands[j]["lo"]
            cover = frozenset(k for k in js if cands[k]["lo"] <= t <= cands[k]["hi"])
            if len(cover) == s and cover not in sets:
                sets.append(cover)
        out = []
        for cover in sets:
            mem = sorted((cands[k] for k in cover), key=lambda o: -o["age"])
            wlo, whi = max(o["lo"] for o in mem), min(o["hi"] for o in mem)
            labs, classes = sorted({o["lab"] for o in mem}), sorted({o["cls"] for o in mem})
            cl, ch = cal_range(curve, wlo, whi)
            out.append({
                "window_14C_BP": [round(wlo), round(whi)],
                "approx_cal_BP": [round(cl, -1), round(ch, -1)] if cl is not None else None,
                "n_sites": len(mem), "labs": labs, "material_classes": classes,
                "meets_independence": len(labs) >= 2 and len(set(classes) - {UNKNOWN}) >= 2,
                "members": [{"site": o["site"], "LabID": o["LabID"], "age_14C_BP": o["age"],
                             "error": o["err"], "material": o["Material"], "taxa": o["Taxa"],
                             "material_class": o["cls"], "lab": o["lab"],
                             "next_oldest_date_at_site": o["second_oldest"],
                             "dates_at_site": o["n_site_dates"], "p3k14c_source": o["Source"],
                             "reference": o["Reference"]} for o in mem],
            })
        return out

    p_floor = 1 / (N_PERM + 1)
    region_rows, survivors, floor_regions = [], [], []
    for reg in tested:
        js = by_region[reg]
        p = (1 + ge[reg]) / (N_PERM + 1)
        row = {"region": region_label(reg), "continent": reg[0], "country": reg[1],
               "province": reg[2], "n_outlier_sites": len(js),
               "n_labs": len({cands[j]["lab"] for j in js}), "n_known_classes": len(known(js)),
               "S": s_obs[reg], "perms_ge_S": ge[reg], "p": p, "p_bonferroni": min(1.0, p * m),
               "significant": p * m < ALPHA}
        region_rows.append(row)
        if row["significant"]:
            ws = [w for w in windows(reg) if w["meets_independence"]]
            if ws:
                survivors.append({**row, "clusters": ws})
        if ge[reg] == 0:
            floor_regions.append((reg, row))
    region_rows.sort(key=lambda r: (r["p"], -r["S"], r["region"]))
    design_limited = m * p_floor >= ALPHA
    exploratory = []
    if design_limited:
        for reg, row in floor_regions:
            exploratory.append({**row, "note": "p at the permutation floor; NOT a survivor",
                                "clusters": windows(reg)})

    summary = {
        "method": "R1 coherent residue (pre-registered 2026-09-23, findings/log.md); "
                  "clarification committed before running: d1013c1, placed under R1 in 625227f",
        "script": "scripts/residue/scan.py",
        "data": {**DATA_INFO, "sha256": data_sha, "rows": len(rows)},
        "calibration_curve": {**INTCAL_INFO, "sha256": intcal_sha, "use": "approximate calendar ranges in the report only"},
        "parameters": {"min_dates_per_site": MIN_DATES, "outlier_combined_se": OUTLIER_SE,
                       "isolation_sigma": ISOLATION_SIGMA, "window_sigma": WINDOW_SIGMA,
                       "max_age_14C_BP": MAX_AGE, "bone_year": BONE_YEAR, "permutations": N_PERM,
                       "seed": SEED, "alpha_after_bonferroni": ALPHA,
                       "province_level_countries": province_countries},
        "funnel": [{"stage": s, "dates": n, "sites": k} for s, n, k in funnel],
        "removed_by_filter": removed,
        "isolation_check_violations": isolation_violations,
        "candidate_material_classes": dict(Counter(o["cls"] for o in cands)),
        "regions": {"with_candidates": len(by_region), "tested": m,
                    "single_region_continents": sorted(c for c in by_cont
                                                       if len({cands[j]["region"] for j in by_cont[c]}) == 1),
                    "candidates_in_tested_regions": sum(len(by_region[r]) for r in tested),
                    "bonferroni_raw_p_threshold": ALPHA / m if m else None,
                    "smallest_attainable_p": p_floor, "design_limited": design_limited,
                    "significant": sum(r["significant"] for r in region_rows),
                    "surviving_regions": len(survivors)},
        "tested_regions": region_rows,
        "surviving_clusters": survivors,
        "exploratory_at_p_floor": exploratory,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (OUT / "r1_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "r1_report.md").write_text(report(summary), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("funnel", "removed_by_filter", "regions", "runtime_seconds")}, indent=1))


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def cluster_lines(c):
    w, cal = c["window_14C_BP"], c["approx_cal_BP"]
    cal_txt = f"about {fmt(int(cal[0]))}–{fmt(int(cal[1]))} cal BP" if cal else "outside IntCal20"
    sites = "; ".join(f"{x['site']} ({x['LabID']}, {fmt(int(x['age_14C_BP']))} ± {fmt(int(x['error']))}, "
                      f"{x['material'] or 'material not given'})" for x in c["members"])
    return (f"window {fmt(w[0])}–{fmt(w[1])} 14C BP ({cal_txt}); {c['n_sites']} sites, "
            f"{len(c['labs'])} labs ({', '.join(c['labs'])}), materials: {', '.join(c['material_classes'])}. "
            f"Sites: {sites}.")


def report(s):
    f, reg = s["funnel"], s["regions"]
    L = ["# R1 · Coherent residue: first scan", "",
         f"*Run 2026-09-23 with `scripts/residue/scan.py` (seed {s['parameters']['seed']}). Method pre-registered "
         "in `findings/log.md` (R1); its clarification was committed before the scan ran. Full numbers: "
         "`r1_summary.json`. No coordinates were read into the analysis or appear here.*", ""]
    if s["surviving_clusters"]:
        head = (f"**Result:** {len(s['surviving_clusters'])} region(s) show a cluster of isolated old dates "
                "that survives the registered test. These are leads for review, not findings.")
    elif reg["design_limited"]:
        head = (f"**Result: null, and design-limited.** {reg['tested']} regions qualified for testing, so the "
                f"Bonferroni threshold (raw p < {reg['bonferroni_raw_p_threshold']:.1e}) is below the smallest "
                f"p that 10,000 permutations can give ({reg['smallest_attainable_p']:.1e}). No cluster could "
                "survive, whatever the data. As pre-declared, this is not rescued by adding permutations.")
    else:
        head = ("**Result: null.** No region's isolated old dates line up more than the shuffled null allows "
                "after Bonferroni correction. For this database and method, coherent residue was not found.")
    L += [head, "", "## Data",
          f"p3k14c, {s['data']['release']}; {fmt(s['data']['rows'])} radiocarbon dates. Source: "
          f"{s['data']['repository']}. SHA-256 `{s['data']['sha256']}`. Ages are uncalibrated 14C years BP.", "",
          "## What the scan did",
          "At each site with at least 5 dates it looked for a date older than every other date there by more "
          "than 3 combined standard errors (the kind usually set aside). It removed the usual mundane suspects "
          "(reservoir-prone materials, bone that is pre-1990 or undatable, ages over 40,000, duplicate or split "
          "samples). Then, per state/province (else country), it counted the most sites whose leftover old "
          "dates overlap at 2σ, and compared that with 10,000 shuffles of the same dates across regions of the "
          "same continent.", "", "## Funnel", "", "| Stage | Dates | Sites |", "|---|---:|---:|"]
    L += [f"| {x['stage']} | {fmt(x['dates'])} | {fmt(x['sites']) if x['sites'] is not None else '–'} |" for x in f]
    rm = s["removed_by_filter"]
    L += ["", "Removed as reservoir-prone: " + ", ".join(f"{k} {v}" for k, v in sorted(rm['a_reservoir_prone'].items(), key=lambda kv: -kv[1])) +
          f". Bone removed: {rm['b_bone_pre1990_or_undated']['reference_year_before_1990']} with a pre-1990 reference, "
          f"{rm['b_bone_pre1990_or_undated']['no_reference_year']} with no reference year. "
          f"Over 40,000: {rm['c_over_40000']}. Duplicates/splits: "
          f"{rm['d_duplicates_splits']['split_or_duplicate_lab_number'] + rm['d_duplicates_splits']['same_age_error_lab_at_another_site']}.",
          "", "## Region tests",
          f"{reg['with_candidates']} regions hold at least one candidate; {reg['tested']} qualified for testing "
          f"(candidates from ≥ 2 sites, ≥ 2 labs, ≥ 2 known material classes), holding "
          f"{fmt(reg['candidates_in_tested_regions'])} candidates. "
          + (f"With {reg['tested']} tests, Bonferroni requires raw p < {reg['bonferroni_raw_p_threshold']:.1e}; the "
             "smallest possible p is 1/10,001, so a region had to beat every one of the 10,000 shuffles. "
             if reg["tested"] else "") +
          f"Significant after Bonferroni: {reg['significant']}. "
          f"Surviving (also meeting the independence rule): {reg['surviving_regions']}."]
    top = s["tested_regions"][:5]
    if top:
        L += ["", "Lowest raw p-values (none significant): " + "; ".join(
            f"{r['region']} (S = {r['S']} of {r['n_outlier_sites']} sites, p = {r['p']:.4f}, "
            f"Bonferroni {r['p_bonferroni']:.2f})" for r in top) + "."]
    L += ["", "## Surviving clusters", ""]
    if s["surviving_clusters"]:
        for r in s["surviving_clusters"]:
            for c in r["clusters"]:
                L.append(f"- **{r['region']}** (S = {r['S']}, p = {r['p']:.1e}, Bonferroni p = {r['p_bonferroni']:.3f}): " + cluster_lines(c))
    else:
        L.append("None. " + ("The registered design cannot pass Bonferroni with this many regions (see above)."
                             if reg["design_limited"] else "Nothing passed the registered threshold."))
    if s["exploratory_at_p_floor"]:
        L += ["", "**Exploratory only (pre-declared; not survivors):** regions whose observed S was never matched in "
              "10,000 shuffles: " + "; ".join(f"{r['region']} (S = {r['S']})" for r in s["exploratory_at_p_floor"]) + "."]
    L += ["", "## Caveats",
          "- p3k14c is a compilation: site names, materials and references are as compiled, and the same place can "
          "appear under two spellings, or two places under one name. Sites were matched by normalised name.",
          "- p3k14c has no measurement year and no collagen-quality field; the bone filter uses the earliest year in "
          "the reference as a proxy. Materials were classed by keywords, which can misfire.",
          "- An isolated old date is often a real but already known earlier phase, not an error; a coherent cluster "
          "may simply be a recognised early horizon. The null keeps each region's number of outlier sites fixed.",
          "- Scope of the test: the shuffle compares regions within one continent, so an early horizon shared by a "
          "whole continent would not stand out, and a continent whose candidates sit in a single region "
          f"({', '.join(reg['single_region_continents']) or 'none here'}) cannot be tested at all (p = 1 by "
          "construction). Only each site's single oldest date, at sites with ≥ 5 dates, was examined.",
          ] + (["- Calendar ranges are read off the IntCal20 mean curve (Northern Hemisphere), not formally calibrated."]
               if s["surviving_clusters"] or s["exploratory_at_p_floor"] else []) + [
          "", "## Next step",
          "Per R1 step 6, each surviving cluster goes to a researcher and a skeptic: is it already known, and is "
          "there a mundane cause? No literature was consulted for this run." if s["surviving_clusters"] else
          "Record the null in `findings/log.md` under R1. Per R1, a null is publishable for this approach on this database."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
