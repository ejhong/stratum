#!/usr/bin/env python3
"""Validate catalog records against catalog/schema.json plus cross-field rules.

  python3 scripts/validate.py                 # every record in catalog/cases/
  python3 scripts/validate.py catalog/cases/monte-verde.json

Exits 1 on any error, so the build and CI fail closed. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "catalog" / "schema.json").read_text())
CASES = ROOT / "catalog" / "cases"

TYPES = {
    "object": dict, "array": list, "string": str, "integer": int,
    "number": (int, float), "boolean": bool, "null": type(None),
}
# Decimal-degree pairs, degree signs with decimals, or explicit lat/long words.
COORD_RE = re.compile(
    r"(-?\d{1,3}\.\d{3,}\s*[,;/]\s*-?\d{1,3}\.\d{3,})|(\d+\.\d+\s*°)|(\d+°\s*\d+['′])|\b(latitude|longitude|lat/long|GPS)\b",
    re.I,
)


def type_ok(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[t])


def resolve(ref):
    node = SCHEMA
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def check(value, schema, path, errs):
    if "$ref" in schema:
        schema = {**resolve(schema["$ref"]), **{k: v for k, v in schema.items() if k != "$ref"}}
    if "oneOf" in schema:
        hits = 0
        for sub in schema["oneOf"]:
            e = []
            check(value, sub, path, e)
            hits += not e
        if hits != 1:
            errs.append(f"{path}: does not match exactly one allowed shape")
        return
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not one of {schema['enum']}")
        return
    t = schema.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        if not any(type_ok(value, x) for x in ts):
            errs.append(f"{path}: expected {t}, got {type(value).__name__}")
            return
    if isinstance(value, str):
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: {len(value)} chars, budget is {schema['maxLength']} — shorten it")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}: needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errs.append(f"{path}: at most {schema['maxItems']} items allowed")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errs.append(f"{path}: items must be unique")
        if "items" in schema:
            for i, item in enumerate(value):
                check(item, schema["items"], f"{path}[{i}]", errs)
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errs.append(f"{path}.{key}: required")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errs.append(f"{path}.{key}: unknown field")
        for key, sub in props.items():
            if key in value:
                check(value[key], sub, f"{path}.{key}", errs)


def strings(node):
    """Every text value, except identifiers (DOIs, URLs), which can look like coordinates."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in ("doi", "url", "commons_file"):
                yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def rules(rec, stem, errs):
    if rec.get("id") != stem:
        errs.append(f"id {rec.get('id')!r} must equal file name {stem!r}")
    sources = rec.get("sources", [])
    ids = [s.get("id") for s in sources]
    if len(set(ids)) != len(ids):
        errs.append("sources: duplicate source ids")
    known = set(ids)
    refs = []
    for key in ("claimed_age", "accepted_age", "orthodoxy_at_claim"):
        if isinstance(rec.get(key), dict):
            refs.append((key, rec[key].get("source")))
    for k, f in (rec.get("features_at_claim") or {}).items():
        refs.append((f"features_at_claim.{k}", f.get("source")))
    for i, o in enumerate(rec.get("objections", [])):
        refs.append((f"objections[{i}]", o.get("source")))
    for i, t in enumerate(rec.get("timeline", [])):
        refs.append((f"timeline[{i}]", t.get("source")))
    for where, sid in refs:
        if sid and sid not in known:
            errs.append(f"{where}: cites {sid}, which is not in sources")
    if not any(s.get("verification") == "checked" for s in sources):
        errs.append("sources: at least one source must be 'checked' (opened and confirmed)")
    for s in sources:
        if not s.get("doi") and not s.get("url") and s.get("kind") not in ("book",):
            errs.append(f"sources {s.get('id')}: needs a DOI or URL (books may use a full reference only)")

    status = rec.get("status")
    if status in ("vindicated", "refuted"):
        if not isinstance(rec.get("year_resolved"), int):
            errs.append(f"year_resolved: required when status is {status}")
        if not rec.get("what_settled_it"):
            errs.append(f"what_settled_it: required when status is {status}")
    if status in ("open", "unsupported") and rec.get("year_resolved") is not None:
        errs.append(f"year_resolved: must be null for an {status} case")
    if status in ("open", "partial", "unsupported") and not rec.get("decisive_tests"):
        errs.append("decisive_tests: required for open, partial and unsupported cases")
    if status == "refuted" and rec.get("failure_mode") in (None, "none"):
        errs.append("failure_mode: required for refuted cases")
    yc, yr = rec.get("year_claimed"), rec.get("year_resolved")
    if isinstance(yc, int) and isinstance(yr, int) and yr < yc:
        errs.append("year_resolved is earlier than year_claimed")
    for key in ("claimed_age", "accepted_age"):
        a = rec.get(key)
        if isinstance(a, dict) and isinstance(a.get("bp_min"), int) and isinstance(a.get("bp_max"), int):
            if a["bp_min"] > a["bp_max"]:
                errs.append(f"{key}: bp_min is greater than bp_max")
    for text in strings(rec):
        text = re.sub(r"10\.\d{4,9}/\S+", " ", text)  # DOIs quoted in prose are not coordinates
        if COORD_RE.search(text):
            errs.append(f"possible coordinates or location detail: {text[:80]!r} — location must stay at country/region level")
            break


def validate(path):
    errs = []
    try:
        rec = json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        return [f"not valid JSON: {e}"]
    check(rec, SCHEMA, "$", errs)
    rules(rec, Path(path).stem, errs)
    return errs


def main(argv):
    files = [Path(a) for a in argv] or sorted(CASES.glob("*.json"))
    bad = 0
    for f in files:
        errs = validate(f)
        if errs:
            bad += 1
            print(f"✗ {f.name}")
            for e in errs:
                print(f"    {e}")
        else:
            print(f"✓ {f.name}")
    print(f"\n{len(files) - bad}/{len(files)} records valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
