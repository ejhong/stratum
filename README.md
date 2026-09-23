# Stratum

*What's left after the boring explanations.*

An AI-operated research lab for archaeology and human origins. It catalogs anomalies —
claims that challenged the accepted story — records how each one fared, learns what
separated the real ones from the ones that fell apart, and uses those lessons to rank the
anomalies that are still open.

**Site:** https://ejhong.github.io/stratum/

- `catalog/cases/` — one verified record per case ([schema](catalog/schema.json))
- `catalog/reviews/` — the skeptic review of each record
- `findings/log.md` — pre-registered hypotheses and findings
- `.claude/agents/` — the lab's agent roles (researcher, skeptic, analyst, scout)
- `CLAUDE.md` — mission, principles and how the lab works

```bash
python3 scripts/build.py                 # validate, analyze, build the site into _site/
python3 -m http.server -d _site 8000     # preview at http://localhost:8000
```

No dependencies beyond Python 3.11+. Every claim cites a checked source; locations stay at
country/region level. Corrections and better sources are welcome as
[issues](https://github.com/ejhong/stratum/issues).
