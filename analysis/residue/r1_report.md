# R1 · Coherent residue: first scan

*Run 2026-09-23 with `scripts/residue/scan.py` (seed 20260923). Method pre-registered in `findings/log.md` (R1); its clarification was committed before the scan ran. Full numbers: `r1_summary.json`. No coordinates were read into the analysis or appear here.*

**Result: null.** No region's isolated old dates line up more than the shuffled null allows after Bonferroni correction. For this database and method, coherent residue was not found.

## Data
p3k14c, v2022.06 public scrubbed-and-fuzzed CSV (identical file in package release 2025.07); 173,946 radiocarbon dates. Source: https://github.com/people3k/p3k14c at commit ce16085396b54fc5bd8360f7efb60cf3cf81e1af. SHA-256 `5c92b7ae96959bc2924409cf66a8919aac955a4abac5545fad26f3fb209eca0c`. Ages are uncalibrated 14C years BP.

## What the scan did
At each site with at least 5 dates it looked for a date older than every other date there by more than 3 combined standard errors (the kind usually set aside). It removed the usual mundane suspects (reservoir-prone materials, bone that is pre-1990 or undatable, ages over 40,000, duplicate or split samples). Then, per state/province (else country), it counted the most sites whose leftover old dates overlap at 2σ, and compared that with 10,000 shuffles of the same dates across regions of the same continent.

## Funnel

| Stage | Dates | Sites |
|---|---:|---:|
| all dates in the release | 173,946 | – |
| dates with a usable site name | 154,492 | 36,528 |
| dates at sites with ≥ 5 dates | 105,428 | 8,160 |
| isolated old outliers (one per site at most) | 2,696 | 2,696 |
| after (a) reservoir-prone materials | 2,450 | 2,450 |
| after (b) bone before 1990 / year unknown | 2,245 | 2,245 |
| after (c) ages over 40,000 14C BP | 2,215 | 2,215 |
| after (d) duplicate or split samples = candidates | 2,122 | 2,122 |

Removed as reservoir-prone: shell 140, sediment 50, food residue 37, carbonate 12, aquatic animal 7. Bone removed: 38 with a pre-1990 reference, 167 with no reference year. Over 40,000: 30. Duplicates/splits: 93.

## Region tests
165 regions hold at least one candidate; 89 qualified for testing (candidates from ≥ 2 sites, ≥ 2 labs, ≥ 2 known material classes), holding 1,841 candidates. With 89 tests, Bonferroni requires raw p < 1.1e-04; the smallest possible p is 1/10,001, so a region had to beat every one of the 10,000 shuffles. Significant after Bonferroni: 0. Surviving (also meeting the independence rule): 0.

Lowest raw p-values (none significant): Asia / Russian Federation (S = 6 of 24 sites, p = 0.0076, Bonferroni 0.68); Europe / United Kingdom (S = 28 of 315 sites, p = 0.0102, Bonferroni 0.91); Europe / Ireland (S = 13 of 99 sites, p = 0.0160, Bonferroni 1.00); South America / Peru (S = 6 of 22 sites, p = 0.1222, Bonferroni 1.00); Africa / Niger (S = 3 of 8 sites, p = 0.1330, Bonferroni 1.00).

## Surviving clusters

None. Nothing passed the registered threshold.

## Caveats
- p3k14c is a compilation: site names, materials and references are as compiled, and the same place can appear under two spellings, or two places under one name. Sites were matched by normalised name.
- p3k14c has no measurement year and no collagen-quality field; the bone filter uses the earliest year in the reference as a proxy. Materials were classed by keywords, which can misfire.
- An isolated old date is often a real but already known earlier phase, not an error; a coherent cluster may simply be a recognised early horizon. The null keeps each region's number of outlier sites fixed.
- Scope of the test: the shuffle compares regions within one continent, so an early horizon shared by a whole continent would not stand out, and a continent whose candidates sit in a single region (Australia) cannot be tested at all (p = 1 by construction). Only each site's single oldest date, at sites with ≥ 5 dates, was examined.

## Next step
Record the null in `findings/log.md` under R1. Per R1, a null is publishable for this approach on this database.
