# H7 megalith-dating audit — batch B (monuments 21–40)

**Auditor:** Sonnet auditor · **Date:** 2026-09-23 · **Scope:** `sample.json` entries 21–40, in fixed order, no additions/drops. Full records in `audit_B.json`.

## Counts by dating basis (n=20)

| dating_basis | n | monuments |
|---|---|---|
| associated-organic | 10 | nabta-playa, senegambia, gochang-dolmens, plain-of-jars, tiwanaku, chavin, olmec-heads, chankillo, rapa-nui, latte-stones |
| stylistic | 3 | aksum, san-agustin, diquis-spheres |
| historical-contextual | 3 | sacsayhuaman, ollantaytambo, haamonga |
| none | 3 | gunung-padang, bada-valley, yonaguni |
| **direct** | **1** | nan-madol |

Only **1 of 20 (5%)** rests on a direct date of the construction material itself. Combined with "none," **16 of 20 (80%)** have no direct dating at all — consistent with H7's claim, though this is one 20-monument half of the pre-registered 40; the full test needs batch A too.

## Association strength (19 non-direct records)

| strength | n |
|---|---|
| strong | 7 |
| moderate | 3 |
| weak | 9 |

Strong cases share a pattern: a dedicated multi-sample dating paper exists (Chankillo, Chavín, Olmec heads, Rapa Nui, Plain of Jars, Senegambia, Tiwanaku). Weak cases mostly reflect *my* inability to locate a site-specific chronometric study within budget (bada-valley, gochang-dolmens, haamonga, yonaguni, san-agustin, diquis-spheres) rather than a confirmed absence in the literature — flagged `confidence: low` and worth a second pass, ideally in the original language (Korean, Indonesian, Spanish) literature.

## Notable finds

- **Nan Madol** is the one clean **direct** case: 230Th/U on coral building blocks dates the first tomb to AD 1180–1200 (McCoy et al. 2016) — a useful positive control showing the direct methods this audit asks about are feasible and have been done elsewhere.
- **Gunung Padang**: the 2023 claim of a 9,000+ BCE "buried pyramid" was retracted in 2024 specifically because the dated soil could not be tied to any anthropogenic feature — H7's concern realized almost verbatim.
- **Aksum**: charcoal directly tied to a stela's construction was collected but failed to radiocarbon-date; the field fell back on ceramic style. Close to being directly dateable.
- **Yonaguni**: per the task brief, checked first — it is **not widely accepted as human-made**; mainstream view treats it as a natural rock formation. Sourcing on this specific question was thin within budget (flagged low-confidence, needs recheck).

## Where a direct date would be most informative

1. **Gunung Padang** — would settle whether any deep layer is anthropogenic at all.
2. **Yonaguni** — would settle the man-made question itself, prior to any construction date.
3. **Sacsayhuamán** — major, iconic Inca monument with no located sealed/direct date; rests on chronicles.
4. **Nabta Playa** — decades of excavation, but no direct method ever applied to the stones themselves.
5. **Aksum** — one failed radiocarbon attempt on construction-context charcoal; a technically modest re-attempt (or OSL) could resolve it.
6. **Bada Valley / Ha'amonga ʻa Maui** — essentially no chronometric evidence located; currently undated in the accessible literature.

## Budget

~70 lookup.py calls used (search/doi/page-grep), within budget. No rate-limiting encountered.
