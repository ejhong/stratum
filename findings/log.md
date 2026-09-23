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
- **Result (2026-09-23):** null. p3k14c v2022.06 (173,946 dates) → 2,122 isolated old outliers after the mundane filters, in 89 testable regions; none passed the Bonferroni threshold (closest: Russian Federation, corrected p = 0.68 — what chance predicts across 89 tests). Blind spots: compilations may omit dates excavators rejected; a continent-wide pattern would not stand out; Australia was untestable as a single region. Report: analysis/residue/r1_report.md.
- **Status:** tested — null
- **R1 clarification (before running), 2026-09-23.** Written after downloading p3k14c and profiling its fields (names, counts, missingness, vocabularies), before any outlier detection, clustering or permutation. It pins down what the registration left undefined; no registered threshold changes. Ages are uncalibrated radiocarbon years BP, as given.
  - *Data.* p3k14c public release v2022.06 (unchanged in package release 2025.07): `inst/p3k14c_scrubbed_fuzzed.csv` from github.com/people3k/p3k14c at commit ce16085, SHA-256 `5c92b7ae96959bc2924409cf66a8919aac955a4abac5545fad26f3fb209eca0c`, 173,946 dates, 18 fields. The canonical tDAR copy refused automated download (HTTP 403). The file contains site coordinates, so it stays in the git-ignored `data/raw/`; no coordinate enters any output.
  - *Site.* SiteID is blank for about 70% of dates, so a site is its name, normalised (lower case, accents and apostrophes dropped, punctuation to spaces) within continent and country; a name that carries two or more different provinces is split by province. Dates with no usable name (blank, "unknown" and similar placeholders) are left out.
  - *Region.* Continent as given, then the first-level unit (state/province) in countries where most dates carry one (USA, Canada, China); elsewhere the country. Sites in those three countries with no province form a "province not given" region of their country.
  - *Outliers.* All dates at a site count toward the ≥ 5, whatever the material. The candidate is the site's single oldest date; it qualifies if it is older than every other date there by more than 3 × √(σ₁² + σ₂²). That already implies no other date lies within 2σ of it (checked anyway), so a site yields at most one outlier.
  - *Mundane filters (in this order, on outliers only, before any clustering).* (a) Reservoir-prone materials, matched by keywords in the Material and Taxa fields: mollusc shell of any kind (marine, freshwater, land snail, named shell genera; nutshell is not shell); carbonates (including eggshell, mortar, plaster, tufa, marl, speleothem); aquatic animals (fish, whale, seal, walrus, anything labelled marine or freshwater); pottery food residue or crust; bulk sediment, gyttja, lake mud; fossil carbon (bitumen, asphalt, coal). (b) Bone before 1990 without collagen quality control: p3k14c has no measurement-year field and no collagen-quality field, so no bone date has stated QC. Substitute: a bone-class outlier (bone, collagen, antler, tooth, dentine, ivory, horn, cremated or burnt bone) is removed unless the earliest four-digit year (1950–2026) in its Reference field is 1990 or later; one with no such year is removed. (c) Age above 40,000 radiocarbon years. (d) Duplicate or split samples: LabIDs are already unique in this release, so an outlier is removed if another date shares its laboratory and lab number under a different suffix or format (split fractions); outliers at different sites with identical age, error and laboratory count once (the first site name alphabetically is kept).
  - *Material classes.* charcoal/wood; short-lived plant (seed, grain, maize, nutshell, other plant parts); bone/tooth/antler; other organic (textile, leather, hair, dung, coprolite, soft tissue, resin); soil/peat/humate; pottery/temper; unknown (includes unspecified "charred material"). Unknown never counts as a distinct class.
  - *Independence.* Distinct sites, and a cluster qualifies only if its members include ≥ 2 laboratories and ≥ 2 known material classes. Laboratory = the LabID's letter prefix, with conventional and AMS codes of one institution merged (GrN/GrA/GrM/GrO, Gif/GifA, Ly/Lyon, UB/UBA, UGA/UGAMS, A/AA, T/TUa, Hel/Hela, NZ/NZA, GU/SUERC, Lu/LuA/LuS, U/Ua, KN/COL, ISGS/ISGSA).
  - *Statistic.* Per region, S = the largest number of distinct sites whose outliers' 2σ ranges (age ± 2 errors) all share a common point. The cluster is those outliers; its window is their common overlap.
  - *Null.* Within each continent, the (age, error) pairs of all filtered outliers are shuffled among all outlier slots of that continent; each slot keeps its site, region, laboratory and material. 10,000 permutations, random seed 20260923. p = (1 + permutations with S ≥ observed S) / 10,001.
  - *Regions tested and Bonferroni.* A region is tested if its filtered outliers span ≥ 2 sites, ≥ 2 laboratories and ≥ 2 known material classes (otherwise no qualifying cluster is possible). A cluster survives if p × (number of regions tested) < 0.01 and a maximal window meets the independence rule.
  - *Known limit, stated before running.* With 10,000 permutations the smallest possible p is 1/10,001, so if more than 100 regions are tested nothing can pass. Permutations and regions will not be changed afterwards: that outcome is reported as a design-limited null, and regions at the p floor are listed as exploratory only, never as survivors.
  - *Calendar ages (report only).* An approximate calendar range is read off the IntCal20 mean curve (Reimer et al. 2020, doi:10.1017/RDC.2020.41; intcal.org/curves/intcal20.14c, SHA-256 `974a66649f2ac8a53e6c99e256b019ac6982f999b12dcf7193162d4c1c09168e`) wherever it falls inside the radiocarbon window. This is not a formal calibration.

## H7 · Many megaliths are dated by association, not directly
- **Date:** 2026-09-23
- **Type:** pre-registered hypothesis (megalith dating audit), written before the audit gathered any dating information
- **Claim:** For most major megalithic monuments, the construction age rests on material found with the monument (charcoal, bone, pottery, inscriptions, style, historical texts) rather than a direct date of the stonework (e.g. rock-surface luminescence, cosmogenic exposure, U-series on carbonate formed after construction). That leaves room for large errors in either direction.
- **Test:** an audit of 40 monuments whose list is fixed and committed before any dating research: widely cited megalithic sites across all inhabited continents. For each: stated construction date, dating basis (direct / associated organic / historical-contextual / stylistic / none), number of independent dates and their spread, and whether a direct method is feasible.
- **Would disprove it:** fewer than half of the 40 depend on association alone.
- **Status:** pre-registered; audit pending. Output also includes a ranked list of monuments where a direct date would be decisive — the leads.
- **Result (2026-09-23):** consistent. After an independent Opus review of the Sonnet audit (19 corrections), dating bases for the 40: direct 1 (Nan Madol, U-Th on coral), associated organic 25, historical-contextual 5, stylistic 6, none 3 — about 35 of 40 rest on association alone (at least 29 even under the most generous definition of direct), far beyond the disproof line of 20. Unverifiable: Almendres, Karahan Tepe, Ġgantija, Ħaġar Qim, and a paywalled 2015 luminescence study of Egyptian monuments. Top leads for a first direct date: Gunung Padang, Almendres, the Great Sphinx, Carnac, Sacsayhuamán. Files: analysis/megaliths/audit_review.json, leads.json.
- **Status:** consistent (n = 40)

## R2 · The frontier scan: dates older than the accepted first arrival
- **Date:** 2026-09-23
- **Type:** pre-registered method (discovery track), written before the scan
- **Claim:** If people reached a region earlier than accepted, dates older than the accepted first arrival should recur across independent sites, laboratories and materials — the pattern that preceded the acceptance of pre-Clovis sites.
- **Test:** (1) Regions and their accepted first-arrival limits, each with a source, are fixed in analysis/frontier/limits.json and committed before any scan — at least the Americas, Sahul, Japan, Remote Oceania, New Zealand, Iceland, Madagascar and the Caribbean. (2) From p3k14c, select dates older than the limit by more than 2 standard errors (after converting between radiocarbon and calendar years consistently), applying R1's mundane filters. (3) A region is a lead if at least 3 independent sites, with at least 2 laboratories and 2 material classes between them, have pre-limit dates. (4) Every lead goes to a researcher and a skeptic: is the site already debated, and is there a mundane cause?
- **Would disprove it:** (the method's value) no region qualifies, or every qualifying site is already known and debated — the scan adds nothing new.
- **Status:** pre-registered; scan pending
- **Result (2026-09-23):** limits fixed and pushed before the scan (be225f4). 77,098 dates in the tested regions → 487 older than their region's limit → 273 dates at 89 sites after R1's filters. Two regions met the rule: Iceland (3 sites; one is a mis-coded record — without it, no lead) and the Americas (85 sites: 56 fossil-fauna localities with bone or unspecified dates; known controversies such as Bluefish Caves, Cactus Hill, Meadowcroft and Old Crow; and 10 unfamiliar sites with old charcoal or wood dates, sent to literature triage). Sahul untestable (limit beyond the 40,000-year filter); no p3k14c rows for New Zealand, Madagascar, the Caribbean or western Remote Oceania. Report: analysis/frontier/r2_report.md.
- **Status:** tested — leads in triage

## O1 · Refutations stay clean; vindications mostly do not
- **Date:** 2026-09-23
- **Type:** observation (not pre-registered; from the first 24 reviewed or revised records)
- **Claim:** All 7 refuted cases in the starter list were confirmed as refuted, but of the 10 starter cases described as "largely vindicated", only 3 held cleanly (Monte Verde, Denisovans, L'Anse aux Meadows); 5 are partial (Jebel Irhoud, Paisley Caves, Göbekli Tepe, *Homo floresiensis*, Troy) and 2 remain open (White Sands, Bluefish Caves). Anomalies that turn out real tend to be right about their core and wrong about details, and popular accounts round this up into clean vindications.
- **Test:** register as a hypothesis and test it on vindicated cases sampled from review literature rather than from the starter list: share fully vindicated vs partial.
- **Would disprove it:** in a sample not drawn from popular accounts, more than half of vindications are clean.
- **Status:** observation (n = 17; starter-list sample, selection-biased)
