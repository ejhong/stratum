# R2 triage: ten unfamiliar Americas sites with old charcoal dates

*2026-09-23. R2 step 4 for the ten sites in `r2_report.md` whose pre-17,500 cal BP dates are on charcoal or wood and that were not recognized. Method: I read every p3k14c row for each site and the neighbouring lab numbers (no coordinates), then searched the literature with `scripts/lookup.py` and web search to locate documents (no Wikipedia). Detail and sources: `r2_triage.json`.*

**Result: none of the ten dates has a documented cultural association.** The published record explains two of them, two are data errors, and two sit in sites their excavators date far later. The other four are unexplained only because nothing about their context is published. They are records to check, not evidence of early people.

| Site (region) | Date, 14C BP | What it dated / context | Class | Conf. |
|---|---|---|---|---|
| Millard Creek (BC) | 16,910 ± 270 | Charcoal at the base of a test pit in a shell midden. The lab list says it is "too early, probably coal contaminated" (worked cannel coal at the site). The row's lab number S-142 is wrong: S-142 is 8300 ± 200, and this age is S-944. | old material in a younger site | high |
| Petroglyph Canyon (MT) | 15,695 ± 135 | Part of the Francis, Loendorf & Dorn 1993 rock-varnish AMS series. It is almost certainly weathering-rind organic matter, mis-coded as charcoal. The authors accepted no Pleistocene age. Beck et al. 1998 showed such samples mix carbon of different ages. The excavated deposits date 850–1820 BP. | non-cultural | medium |
| Dry Creek ("Wyoming") | 19,050 ± 1,500 | An artefact of the scan: "Dry Creek" merges at least five unrelated sites, and this row inherited "Wyoming" from 48NA3805 (3930 BP). The date's real site is unknown (refs: Byers 1979; Shaw 1988). | data error | high |
| Chugachik Island (AK) | 18,910 ± 250 | Not in the site's published series: five dates, 1475–2740 BP, with the midden base above sterile peat. Its references are the site's generic list, and the next lab number cites a source unrelated to Alaska (Breschini & Haversat 1992). | data error | low |
| Clam Gulch (AK) | 16,280 ± 110 | A Dena'ina site that the excavator dates to about AD 1500 (Reger 1987 via Reger 2008). The sample's context is in reports not online. | old material in a younger site (provisional) | medium |
| Rock Levee (MS) | 16,479 ± 571 (and 13,870 ± 158) | The excavators' report (Weinstein et al. 1995) calls the site "Late Marksville through Late Mississippi Period". The other five dates are 830–4425 BP. The report is not online. | old material in a younger site (provisional) | medium |
| Iceberg (NL) | 18,730 ± 850 | A lone outlier with a large error, among seven dates of 2115–3470 BP from the same investigators. The sources are not online. | unexplained | low |
| Drift Fence site (OR) | 24,700 ± 80 (and 13,200 ± 60) | Source is the Oregon SHPO database only. The site's other five dates are 370–2530 BP. No report found. | unexplained | low |
| Phillis (PA) | 16,280 ± 100 | Source is SHPO files only. Probably Phillis Island in the Ohio River (name and county match). No report found. | unexplained | low |
| The Burn Site (KS) | 20,425 ± 396 | A single date from the laboratory's own database, with no site number. It is not even established that this is an archaeological site. | unexplained | low |

## What would settle the four unexplained dates

Nothing found justifies dismissing any of these four, and none should be promoted without a cultural association. For each, the first test is a records check; re-dating comes second.
- **Drift Fence (35UM169):** get the report behind the Oregon SHPO entry and read the provenience of BETA-146262 and -146263: feature or natural soil, depth, sediment unit, artifacts. If they came from a hearth or pit with artifacts, AMS-date identified single charcoal fragments from the same feature and OSL-date the enclosing sediment. Otherwise reclassify them as non-cultural.
- **Phillis (36BV344):** get the Pennsylvania SHPO file and CRM report for BETA-108382 and check whether the sample came from a cultural feature or from older terrace or outwash sediments. Then apply the same AMS and OSL pair.
- **The Burn Site:** get TX-8484's submission record (submitter, project, sample) and check the Kansas site files. If it is not an archaeological sample, drop it.
- **Iceberg:** read SI-2431's provenience in McGhee & Tuck 1975 and Tuck 1978, and check the local deglaciation age (Dalton et al. 2020). If the location was under the Laurentide ice 20.5–24.6 ka cal BP, as is generally understood (UNVERIFIED here), the sample holds older carbon and the question is closed.

The two provisional calls (Clam Gulch, Rock Levee) are settled the same way: read Reger 1983/1987 and Weinstein et al. 1995 for the sample proveniences.

## Corrections to feed back
- **Scan:** `scan.py` gives a province to every same-name row when only one row has one. Split sites by SiteID or reference, and do not spread one row's province to other rows. "Dry Creek (Wyoming)" should be dropped.
- **Records:** Millard Creek S-142 → S-944. Petroglyph Canyon AA-6537 (and probably AA-6544 and Bear Shield AA-6539 and AA-6543, not checked) is varnish organics, not charcoal. Chugachik Island WSU-4302 and WSU-4303 are probably attached to the wrong site.

## For R2's pre-registered test
Of the 10 unfamiliar sites, 6 are explained or erroneous. The 4 still open are unresolved records, and none has any evidence of an occupation. So far the Americas lead has brought up noise in the records rather than new candidate sites. That points toward R2's disproof condition, but the four checks above must come back first.

*Not read (paywalled or offline): Reger 1983/1987, Moss & Erlandson 1995, McGhee & Tuck 1975, Tuck 1978, Weinstein et al. 1995, Mills 1994, and the body of Francis et al. 1993. Cost: about 48 tool calls, about 175k tokens.*
