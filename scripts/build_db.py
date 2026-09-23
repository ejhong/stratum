#!/usr/bin/env python3
"""Rebuild catalog/stratum.db from the JSON records (the JSON files stay authoritative).

Open it with any SQLite browser, e.g. `sqlite3 catalog/stratum.db "select name, status from cases"`.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stratum_data import ROOT, load_cases  # noqa: E402

DB = ROOT / "catalog" / "stratum.db"

SCHEMA = """
create table cases (
  id text primary key, name text, hook text, country text, region text, continent text,
  anomaly_type text, claim text, claimed_label text, claimed_bp_min integer, claimed_bp_max integer,
  claimed_mid real, accepted_label text, accepted_bp_min integer, accepted_bp_max integer,
  orthodoxy_label text, orthodoxy_limit_bp integer, leap real, year_claimed integer,
  year_resolved integer, years_to_resolution integer, status text, status_note text,
  what_settled_it text, failure_mode text, independent_methods_count integer,
  profile_score real, confidence text, review_stage text, skeptic_verdict text
);
create table features (case_id text, feature text, value text, note text, source_id text);
create table objections (case_id text, idx integer, text text, kind text, raised_by text, year integer,
  outcome text, outcome_note text, source_id text);
create table timeline (case_id text, year integer, event text, source_id text);
create table sources (case_id text, source_id text, citation text, doi text, url text, kind text,
  access text, verification text, machine_check text);
create table tests (case_id text, idx integer, test text, would_show text, cost text);
create table evidence_types (case_id text, type text);
create table settled_by (case_id text, method text);
create table people (case_id text, name text, role text);
"""


def build(path=DB):
    cases = load_cases()
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    for r in cases:
        ca, aa, oa = r["claimed_age"], r.get("accepted_age") or {}, r.get("orthodoxy_at_claim") or {}
        rev = r.get("review", {})
        con.execute(
            "insert into cases values (" + ",".join("?" * 30) + ")",
            (
                r["id"], r["name"], r["hook"], r["location"]["country"], r["location"].get("region"),
                r["location"]["continent"], r["anomaly_type"], r["claim"], ca.get("label"),
                ca.get("bp_min"), ca.get("bp_max"), r["_age"], aa.get("label"), aa.get("bp_min"),
                aa.get("bp_max"), oa.get("label"), oa.get("limit_bp"), r["_leap"], r["year_claimed"],
                r.get("year_resolved"), r["_years"] if r["_resolved"] else None, r["status"],
                r["status_note"], r.get("what_settled_it"), r.get("failure_mode"),
                r["independent_methods_count"], r["_profile"], r["confidence"], rev.get("stage"),
                (r["_review"] or {}).get("verdict"),
            ),
        )
        for k, f in r["features_at_claim"].items():
            con.execute("insert into features values (?,?,?,?,?)", (r["id"], k, f["value"], f.get("note"), f.get("source")))
        for i, o in enumerate(r.get("objections", [])):
            con.execute(
                "insert into objections values (?,?,?,?,?,?,?,?,?)",
                (r["id"], i, o["text"], o["kind"], o.get("raised_by"), o.get("year"), o["outcome"], o.get("outcome_note"), o.get("source")),
            )
        for t in r.get("timeline", []):
            con.execute("insert into timeline values (?,?,?,?)", (r["id"], t["year"], t["event"], t.get("source")))
        for s in r.get("sources", []):
            chk = (r["_checks"].get(s["id"]) or {}).get("result")
            con.execute(
                "insert into sources values (?,?,?,?,?,?,?,?,?)",
                (r["id"], s["id"], s["citation"], s.get("doi"), s.get("url"), s["kind"], s.get("access"), s["verification"], chk),
            )
        for i, t in enumerate(r.get("decisive_tests", [])):
            con.execute("insert into tests values (?,?,?,?,?)", (r["id"], i, t["test"], t["would_show"], t["cost"]))
        for e in r.get("evidence_types", []):
            con.execute("insert into evidence_types values (?,?)", (r["id"], e))
        for m in r.get("settled_by", []):
            con.execute("insert into settled_by values (?,?)", (r["id"], m))
        for p in r.get("key_proponents", []):
            con.execute("insert into people values (?,?,?)", (r["id"], p, "proponent"))
        for p in r.get("key_critics", []):
            con.execute("insert into people values (?,?,?)", (r["id"], p, "critic"))
    con.commit()
    con.close()
    print(f"database: {len(cases)} cases -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
