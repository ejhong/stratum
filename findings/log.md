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
