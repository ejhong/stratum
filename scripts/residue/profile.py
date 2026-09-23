"""Profile the p3k14c CSV: field names, non-missing counts, distinct values,
vocabularies of categorical fields. Never prints coordinates (Long/Lat are only
counted for missingness). Standard library only.

Usage: python3 scripts/residue/profile.py data/raw/<file>.csv
"""
import csv, re, sys
from collections import Counter

MISSING = {"", "NA", "N/A", "na", "NaN", "nan", "NULL", "null", "None", "-"}
COORD_FIELDS = {"Long", "Lat"}

def missing(v):
    return v is None or v.strip() in MISSING

def main(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())
    print(f"rows: {len(rows)}  fields: {len(fields)}")
    print(f"{'field':<12} {'non-missing':>11} {'missing':>8} {'distinct':>9}")
    for k in fields:
        vals = [r[k] for r in rows if not missing(r[k])]
        print(f"{k:<12} {len(vals):>11} {len(rows)-len(vals):>8} {len(set(vals)):>9}")
    def top(field, n):
        c = Counter(r[field].strip() for r in rows if not missing(r[field]))
        print(f"\n-- {field}: top {n} of {len(c)} values")
        for v, k in c.most_common(n):
            print(f"  {k:>7}  {v[:70]}")
    for field, n in [("Continent", 10), ("Method", 15), ("Source", 45),
                     ("LocAccuracy", 10), ("Material", 150), ("Taxa", 40),
                     ("Country", 25), ("Period", 15)]:
        if field not in COORD_FIELDS:
            top(field, n)
    # numeric fields
    for field in ("Age", "Error", "d13C"):
        bad, nums = 0, []
        for r in rows:
            if missing(r[field]):
                continue
            try:
                nums.append(float(r[field]))
            except ValueError:
                bad += 1
        nums.sort()
        q = lambda p: nums[min(len(nums) - 1, int(p * len(nums)))]
        print(f"\n-- {field}: numeric {len(nums)}, unparseable {bad}, min {nums[0]}, "
              f"p50 {q(.5)}, p99 {q(.99)}, max {nums[-1]}, <=0: {sum(x <= 0 for x in nums)}")
    ages = [float(r["Age"]) for r in rows if not missing(r["Age"])]
    print(f"   Age > 40000: {sum(a > 40000 for a in ages)}")
    # coordinates: missingness only
    for field in COORD_FIELDS:
        print(f"-- {field}: missing {sum(missing(r[field]) for r in rows)} (values never printed)")
    # Province coverage
    print(f"\n-- rows with Province: {sum(not missing(r['Province']) for r in rows)}; "
          f"Countries without any Province: "
          f"{sorted({r['Country'] for r in rows} - {r['Country'] for r in rows if not missing(r['Province'])})[:40]}")
    # lab codes
    labs = Counter()
    nolab = 0
    for r in rows:
        m = re.match(r"\s*([A-Za-z][A-Za-z\-]*?[A-Za-z]*)[\s\-_]*\d", r["LabID"] or "")
        if m:
            labs[m.group(1).upper().rstrip("-")] += 1
        else:
            nolab += 1
    print(f"\n-- LabID prefixes: {len(labs)} distinct; LabIDs without a parseable prefix: {nolab}")
    print("  ", ", ".join(f"{k}:{v}" for k, v in labs.most_common(60)))
    ids = Counter(re.sub(r"[\s\-_]", "", (r["LabID"] or "").upper()) for r in rows)
    print(f"-- normalized LabIDs occurring >1 times: {sum(1 for v in ids.values() if v > 1)} "
          f"(rows involved {sum(v for v in ids.values() if v > 1)})")
    # site identity
    sid = Counter(r["SiteID"] for r in rows)
    name_to_ids = {}
    for r in rows:
        key = (r["Country"], r["Province"], re.sub(r"\W+", " ", r["SiteName"].lower()).strip())
        name_to_ids.setdefault(key, set()).add(r["SiteID"])
    id_to_names = {}
    for r in rows:
        id_to_names.setdefault(r["SiteID"], set()).add(r["SiteName"].strip().lower())
    print(f"\n-- distinct SiteID {len(sid)}; distinct (country, province, normalized name) "
          f"{len(name_to_ids)}; names spread over >1 SiteID: "
          f"{sum(1 for v in name_to_ids.values() if len(v) > 1)}; SiteIDs with >1 name: "
          f"{sum(1 for v in id_to_names.values() if len(v) > 1)}")
    print(f"   SiteIDs with >=5 rows: {sum(1 for v in sid.values() if v >= 5)}")
    yrs = sum(1 for r in rows if re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", r["Reference"] or ""))
    print(f"-- rows whose Reference contains a 4-digit year: {yrs}")

if __name__ == "__main__":
    main(sys.argv[1])
