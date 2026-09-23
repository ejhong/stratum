# Findings log

Every notable observation goes here: date, what was noticed, the evidence, what would
disprove it, and its current status. Entries are append-only; a changed status gets a
dated note, never a silent edit. The site renders this file.

Hypotheses marked **pre-registered** were written and pushed to GitHub before any
catalog record existed, so the data could not shape them. They are tested exactly as
worded here.

<!-- Entry format:
## <ID> · <short title>
- **Date:** YYYY-MM-DD
- **Type:** pre-registered hypothesis | observation | lead
- **Claim:** one or two sentences.
- **Test:** how it is measured from the catalog.
- **Would disprove it:** the result that kills it.
- **Status:** awaiting data | consistent (n=…) | not supported (n=…) | refuted (n=…)
- **Evidence:** record ids, counts, notes.
-->

## H1 · The size of the leap predicts the fate
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** Chronology anomalies that were later vindicated extended the then-accepted limit modestly; those later refuted claimed much larger leaps. The field accepts deep time in steps.
- **Test:** leap = claimed age (midpoint) ÷ the accepted limit at the time of the claim (`orthodoxy_at_claim.limit_bp`). Compare medians for vindicated vs refuted chronology cases.
- **Would disprove it:** once at least 12 resolved chronology cases are catalogued, the vindicated median leap is not lower than the refuted median.
- **Status:** awaiting data

## H2 · Independent dating methods predict vindication
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** Anomalies later vindicated more often had two or more independent dating methods, and dates from more than one laboratory, when first claimed.
- **Test:** share of `multiple_dating_methods = yes` (and separately `multiple_labs = yes`) among vindicated vs refuted cases.
- **Would disprove it:** at 20 or more resolved cases, the share is not higher among vindicated cases.
- **Status:** awaiting data

## H3 · One team and closed material predict refutation
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** Refuted anomalies more often rested on a single team and on material critics could not examine.
- **Test:** share of `independent_teams = no` and of `material_accessible = no` among refuted vs vindicated cases.
- **Would disprove it:** at 20 or more resolved cases, these features are not more common among refuted cases.
- **Status:** awaiting data

## H4 · The objections that proved wrong were mostly priors
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** Objections later shown to be wrong were disproportionately arguments from the accepted model ("it can't be that old") rather than specific evidential problems such as contamination or disturbance.
- **Test:** share of objections with `kind = prior` among those with `outcome = wrong`, vs among those with `outcome = held`.
- **Would disprove it:** at 30 or more objections with known outcomes, the prior-based share among wrong objections is not higher than among objections that held.
- **Status:** awaiting data

## H5 · Vindication is slower than refutation
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** The burden of proof is asymmetric: anomalies that turn out real take longer to be accepted than false ones take to be rejected.
- **Test:** median years from `year_claimed` to `year_resolved`, vindicated vs refuted.
- **Would disprove it:** at 20 or more resolved cases, the vindicated median is not longer than the refuted median.
- **Status:** awaiting data

## H6 · A proponent's outside stake is a warning sign
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis
- **Claim:** A documented commercial, religious, nationalist or fame-seeking motive (`proponent_stake = yes`) is concentrated among refuted cases.
- **Test:** count of `proponent_stake = yes` by status.
- **Would disprove it:** two or more vindicated cases with a documented proponent stake, or a rate among vindicated cases at least half the refuted rate.
- **Status:** awaiting data

## M1 · Known weakness of this first test
- **Date:** 2026-09-23
- **Type:** observation
- **Claim:** In the first catalog round, features are coded by researcher agents who know each case's outcome. Even with the rule to code "as things stood at the time", hindsight can leak into the coding and inflate H1–H6.
- **Test:** re-code a random subset blind: a separate agent sees only sources published before resolution, never the outcome. Compare agreement.
- **Would disprove it:** (that this bias matters) blind and unblinded codings agree on at least 90% of feature values.
- **Status:** planned for after the first 24 records

## R1 · Coherent residue: do dismissed dates line up?
- **Date:** 2026-09-23
- **Type:** pre-registered method (discovery track pilot), written before any radiocarbon data was examined
- **Claim:** Dates set aside as "too old" are usually noise (contamination, old wood, reservoir effects, lab error), and noise should scatter. If, within a region, isolated too-old dates from independent sites (different sites, labs and materials) cluster at a common age more than chance allows, that coherent residue is a candidate signal of an unrecognized earlier occupation.
- **Test:** (1) Data: open radiocarbon databases, p3k14c first. (2) Outliers: at sites with ≥ 5 dates, a date older than every other date at the site by > 3 combined standard errors, with no other date at that site within 2σ of it (an isolated old date, the kind excavators dismiss). (3) Mundane filters, applied before any clustering: marine shell and other reservoir-prone materials; bone dated before 1990 without stated collagen quality control; dates beyond 40,000 radiocarbon years; duplicate or split samples. (4) Coherence: per region, the largest number of independent sites whose outliers overlap in one 2σ age window, compared with a permutation null that shuffles outlier ages across regions within the same continent (10,000 permutations). (5) Threshold: p < 0.01 after Bonferroni correction across regions. (6) Every surviving cluster goes to a researcher and a skeptic: is it already known, and is there a mundane cause?
- **Would disprove it:** (the method's value) no cluster survives, or every survivor is already known or mundanely explained — a publishable null for this approach on this database.
- **Status:** pre-registered; pilot pending

## H7 · Many megaliths are dated by association, not directly
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis (megalith dating audit), written before the audit gathered any dating information
- **Claim:** For most major megalithic monuments, the construction age rests on material found with the monument (charcoal, bone, pottery, inscriptions, style, historical texts) rather than a direct date of the stonework (e.g. rock-surface luminescence, cosmogenic exposure, U-series on carbonate formed after construction). That leaves room for large errors in either direction.
- **Test:** an audit of 40 monuments whose list is fixed and committed before any dating research: widely cited megalithic sites across all inhabited continents. For each: stated construction date, dating basis (direct / associated organic / historical-contextual / stylistic / none), number of independent dates and their spread, and whether a direct method is feasible.
- **Would disprove it:** fewer than half of the 40 depend on association alone.
- **Status:** pre-registered; audit pending. Output also includes a ranked list of monuments where a direct date would be decisive — the leads.
