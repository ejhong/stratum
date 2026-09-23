# R2 · Frontier scan: dates older than the accepted first arrival

*Run 2026-09-23 with `scripts/frontier/scan.py`. Pre-registered in `findings/log.md` (R2); regions, limits and the conversion rule were fixed in `limits.json` and pushed before the scan (commit be225f4). Detail: `r2_summary.json`. No coordinates were read; sites are named only.*

**Result: 2 region(s) meet the lead rule: Americas and Iceland.** A lead is a list for the researcher and skeptic, not a finding; read the note under each.

**Method.** Each limit (calendar years BP) became a radiocarbon threshold: the oldest age the IntCal20 mean curve reaches at or after the limit, with the curve's own error (IntCal20 everywhere, slightly permissive in the south). A date counts if it is older than that by more than 2 combined standard errors and survives R1's filters. Lead = at least 3 sites, 2 labs and 2 known material classes between them.

## Funnel

| Stage | Dates | Sites |
|---|---:|---:|
| dates in a defined region | 77,098 | 13,456 |
| with a usable site name | 59,331 | 13,456 |
| older than the limit by > 2 SE | 487 | 157 |
| after (a) reservoir-prone materials | 468 | 152 |
| after (b) bone before 1990 / year unknown | 305 | 97 |
| after (c) ages over 40,000 14C BP | 275 | 90 |
| after (d) split or duplicate samples = candidates | 273 | 89 |

Pre-limit dates with no usable site name: 20. Removed: reservoir-prone 19 (aquatic animal 11, sediment 5, shell 3); bone 151 pre-1990 + 12 no year; over 40,000: 30; split/duplicate or no lab number: 2.

## Regions

| Region | Limit, cal BP (source) | 14C threshold | Dates | Pre-limit | Kept | Sites | Labs | Classes | Result |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Americas | 17,500 (Waters 2019) | 14,442 ± 40 | 71,961 | 479 | 265 | 85 | 29 | 5 | **lead** |
| Sahul | 50,000 (O'Connell et al. 2018) | 47,531 ± 354 | 3,624 | 0 | 0 | 0 | 0 | 0 | untestable: beyond 40k filter |
| Japan | 40,000 (Nakazawa 2017) | 34,918 ± 125 | 1,433 | 0 | 0 | 0 | 0 | 0 | no |
| Remote Oceania (west) | 3,450 (Rieth & Athens 2019) | 3,227 ± 12 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no rows |
| Remote Oceania (East Polynesia) | 925 (Wilmshurst et al. 2011) | 1,009 ± 10 | 73 | 1 | 1 | 1 | 1 | 1 | no |
| New Zealand | 670 (Wilmshurst et al. 2008) | 718 ± 11 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no rows |
| Iceland | 1,080 (Vésteinsson & McGovern 2012) | 1,201 ± 13 | 7 | 7 | 7 | 3 | 3 | 2 | **lead** |
| Madagascar | 1,450 (Mitchell 2020) | 1,603 ± 13 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no rows |
| Caribbean | 5,800 (Napolitano et al. 2019) | 5,084 ± 17 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no rows |

## Lead: Americas

85 sites, 265 kept dates, 29 labs. Classes: bone/tooth/antler 198, charcoal/wood 31, unknown 25, short-lived plant 6, soil/peat/humate 4, other organic 1. Compilations: CARD 256, UWyo2021 9. Continents (kept / before filters): North America 265/479. Sites with only animal-bone or unspecified dates: 56 of 85. 'Recognized' means from general knowledge; nothing about the leads was looked up.

*Note written after the scan, from the database fields only:* Most sites are Alaskan, Yukon and Alberta localities whose kept dates are on bones of named Pleistocene animals (mammoth, horse, bison, bear and others), compiled in CARD and often citing fauna compilations (FAUNMAP, Harington 2003, Guthrie). A date on a fossil bone gives the animal's age, not evidence of people, unless the bone is shown to be modified by humans. p3k14c does not record that, and R1's filters were not built to remove it, so the registered rule flags the region on the strength of fossil localities. The useful parts of this lead are the famous cases and the smaller set of unrecognized sites dated on charcoal, wood or plants. No Central or South American date passed the threshold, even before the filters.

**Recognized as famous early-arrival controversies** (12 sites):
- Bluefish Caves, Yukon: Bluefish Cave 3 (Yukon Territories; 2 of 9 dates kept; TO): TO-1196 33,550 ± 350 (~37.2–39.4 ka cal, ferret bone collagen); TO-1266 18,970 ± 1,490 (~19.3–26.1 ka cal, cougar bone collagen)
- pre-Clovis claim, Virginia: Cactus Hill (Virginia; 1 of 25 dates kept; BETA): BETA-81590 15,070 ± 70 (~18.2–18.6 ka cal, charcoal)
- pre-Clovis claim, Pennsylvania: Meadowcroft Rockshelter (Pennsylvania; 6 of 6 dates kept; DIC, OXA, SI): OXA-363 31,400 ± 1,200 (~33.6–39.1 ka cal, charcoal); OXA-364 30,900 ± 1,100 (~33.1–37.5 ka cal, charcoal); SI-1687 30,710 ± 1,140 (~32.3–37.4 ka cal, charcoal); +3 more
- Old Crow Basin bone-tool debate, Yukon: 9 localities (Old Crow Loc. CRH-12, Old Crow Loc. CRH-13, Old Crow Loc. CRH-22, Old Crow Loc. CRH-4, Old Crow Loc. CRH-47, Old Crow Loc. CRH-70, Old Crow Loc. CRH-71, Old Crow Loc. CRH-87, Old Crow Loc. REM78-1); 12 dates, 22,330–39,500 14C BP; mammoth bone collagen 4, mammoth? bone collagen 3, mammal bone collagen 3, moose bone collagen 1, bison bone collagen 1; labs I, RIDDL, TO

**Recognized sites, but not (to my knowledge) for a claim this old** (12):
- Bechan Cave (Utah; 1 of 32 dates kept; ARIZONA): A-3514 16,700 ± 250 (~19.5–20.8 ka cal, plant remains) — Utah; a palaeontological dung cave
- Cape Krusenstern (USA; 1 of 31 dates kept; B): B-265 26,100 ± 400 (~29.6–31.1 ka cal, peat) — Alaska; beach-ridge archaeological sequence
- Gerstle River (USA; 1 of 7 dates kept; BETA): BETA-109267 15,090 ± 70 (~18.2–18.6 ka cal, horse bone collagen) — Alaska; late-glacial site
- Jim Pitts (South Dakota; 1 of 22 dates kept; ARIZONA): AA-35949 38,000 ± 1,300 (~40.6–43.9 ka cal, charcoal) — South Dakota; Paleoindian site
- Manis Mastodon (Washington; 1 of 13 dates kept; UCIAMS): UCIAMS-29116 29,070 ± 230 (~33.0–34.2 ka cal, bone) — pre-Clovis mastodon site, about 13,800 years
- Mead (USA; 1 of 9 dates kept; NSRL): NSRL-2000 17,370 ± 90 (~20.8–21.2 ka cal, mammoth bone collagen) — Alaska; late-glacial site
- On Your Knees Cave (USA; 6 of 21 dates kept; ARIZONA): AA-15227 35,365 ± 800 (~39.1–41.9 ka cal, bear bone collagen); +5 more — Alaska; early Holocene human remains
- Paw Paw Cove (Maryland; 1 of 2 dates kept; ARIZONA): AA-3870 17,820 ± 170 (~21.0–22.1 ka cal, wood) — Maryland; Paleoindian site
- Smiling Dan (Illinois; 1 of 15 dates kept; ISGS): ISGS-851 23,380 ± 500 (~26.5–28.7 ka cal, plant remains) — Illinois
- The Forks (Manitoba; 1 of 34 dates kept; BGS): BGS-1315 16,330 ± 200 (~19.2–20.2 ka cal, charcoal) — Manitoba
- Trail Creek Cave 9 (USA; 1 of 16 dates kept; BETA): BETA-35839 16,300 ± 140 (~19.4–20.0 ka cal, caribou bone collagen) — Alaska; I recall debated early bone dates, unverified
- Ugashik Narrows (USA; 1 of 16 dates kept; SI): SI-2079 35,700 ± 3,000 (~34.3–44.5 ka cal, charcoalé) — Alaska Peninsula

**Not recognized, with dates on charcoal, wood, plants, soil or other organics** (20; only those dates shown, the count includes any bone dates):
- Chatanika River (USA; 35 of 51 dates kept; ARIZONA, CAMS, DIC, L, QC, SI, ST): QC-673 19,660 ± 30 (~23.8 ka cal, plant remains)
- Chugachik Island (USA; 1 of 7 dates kept; WSU): WSU-4302 18,910 ± 250 (~22.4–23.7 ka cal, charcoal)
- Clam Gulch (USA; 1 of 8 dates kept; BETA): BETA-6689 16,280 ± 110 (~19.4–19.9 ka cal, charcoal)
- Consolidated Pit 45 (Alberta; 2 of 5 dates kept; AECV): AECV-1582C 35,760 ± 2,130 (~36.0–43.1 ka cal, wood); AECV-1581C 35,500 ± 2,530 (~34.7–43.8 ka cal, wood)
- Drift Fence site (Oregon; 1 of 7 dates kept; BETA): BETA-146263 24,700 ± 80 (~28.8–29.1 ka cal, charcoal)
- Dry Creek (Wyoming; 1 of 24 dates kept; SI): SI-1544 19,050 ± 1,500 (~19.4–26.3 ka cal, charcoal)
- Epiguruk (USA; 9 of 12 dates kept; USGS): USGS-1443 33,670 ± 280 (~37.5–39.4 ka cal, willow wood); USGS-1442 23,560 ± 160 (~27.4–27.9 ka cal, willow wood); +3 more
- Galt Island Bluff (Alberta; 2 of 4 dates kept; GSC): GSC-14422 38,700 ± 1,100 (~41.4–44.1 ka cal, wood); GSC-1442 37,900 ± 1,100 (~40.9–43.1 ka cal, wood)
- Goldstream (USA; 85 of 152 dates kept; ARIZONA, CAMS, I, OXA, QC, SI): I-2116 24,000 ± 650 (~27.1–29.6 ka cal, plant remains); QC-668 18,230 ± 410 (~20.9–23.0 ka cal, plant remains); +1 more
- HH75-1 (Yukon Territories; 1 of 1 dates kept; TO): TO-124 34,220 ± 178 (~39.2–39.7 ka cal, rodent feces)
- Hillsborough Mastodon (New Brunswick; 1 of 3 dates kept; GSC): GSC-2469 37,200 ± 1,310 (~39.7–43.0 ka cal, wood)
- Hungry Creek (Yukon Territories; 1 of 1 dates kept; GSC): GSC-2422 36,900 ± 300 (~41.3–42.1 ka cal, beaver-chewed wood)
- Iceberg (Newfoundland; 1 of 8 dates kept; SI): SI-2431 18,730 ± 850 (~20.5–24.6 ka cal, charcoal)
- Likely mammoth (Canada; 1 of 1 dates kept; S): S-1036 20,190 ± 190 (~23.8–24.8 ka cal, charcoal)
- Millard Creek (Canada; 1 of 5 dates kept; S): S-142 16,910 ± 270 (~19.6–21.0 ka cal, charcoal)
- Old Wound (USA; 1 of 3 dates kept; AU): AU-90 26,900 ± 3,400 (~24.1–39.0 ka cal, peat)
- Petroglyph Canyon (Montana; 1 of 2 dates kept; ARIZONA): AA-6537 15,695 ± 135 (~18.8–19.2 ka cal, charcoal)
- Phillis (Pennsylvania; 1 of 1 dates kept; BETA): BETA-108382 16,280 ± 100 (~19.4–19.9 ka cal, charcoal)
- Rock Levee (Mississippi; 1 of 7 dates kept; GEORGIA): UGA-6060 16,479 ± 571 (~18.7–21.4 ka cal, charcoal)
- The Burn Site (Kansas; 1 of 1 dates kept; TX): TX-8484 20,425 ± 396 (~23.8–25.6 ka cal, charcoal)

**Not recognized, dated only on animal bone or unspecified material** (41; kept dates, oldest 14C BP): Banks Island mammoth (1; 20,700); Beaverhouse Hill (1; 16,950); Beaverlodge (1; 24,640); Bushe River (1; 22,020); Canyon Creek (1; 39,390); Chuchi Lake (3; 35,480); Clover Bar Pit (4; 31,220); Colorado Creek (2; 16,150); Consolidated Pit 46 (3; 39,960); Consolidated Pit 48 (7; 38,980); Crawford Knoll (1; 15,120); Dawson Loc. 10 (1; 37,990); Dawson Loc. 12 (2; 30,370); Dawson Loc. 29 (2; 35,610); Dawson Loc. 31 (1; 26,040); Dawson Loc. 37 (1; 24,850); Dawson Loc. 57 (1; 26,720); Dawson Loc. 60 (1; 37,220); Dawson Loc. 63 (2; 30,810); Dawson Loc. 77 (1; 20,250); Duhme Cave (1; 21,780); Eagle Cave (2; 34,860); Esther (2; 34,974); Harvard bison (1; 21,280); Ikpikpuk River (6; 27,190); Kangiguksuk (1; 34,820); Ketza River (1; 26,350); Lime Hills 1 (1; 27,950); Lost Chicken Creek (2; 31,390); Melville Island mammoth (1; 21,000); North Saskatchewan River (3; 29,380); Porcupine River Cave 1 (2; 38,260); Riverview Pit (1; 31,290); Schowalter (2; 28,000); Seward (2; 25,980); Simpson Point (2; 36,160); Sixtymile Loc. 3 (6; 39,560); Sixtymile Loc. 5 (2; 24,980); Sullivan Creek (2; 18,060); Whitestone mammoth CRH-43 (1; 30,380); Winter (1; 33,650).

## Lead: Iceland

3 sites, 7 kept dates, 3 labs. Classes: short-lived plant 3, charcoal/wood 3, unknown 1. Compilations: RADON-B 7. Continents (kept / before filters): Europe 7/7. Sites with only animal-bone or unspecified dates: 1 of 3. 'Recognized' means from general knowledge; nothing about the leads was looked up.

*Note written after the scan, from the database fields only:* All 7 Icelandic rows in p3k14c come from RADON-B (a Bronze Age compilation) and fall between 2,650 and 2,820 14C BP, about 2,400–3,150 cal BP. One site name, Castro de Nossa Senhora da Guia, is Portuguese, which suggests a country-coding error in the compilation. Without that site, Iceland has 2 sites and no short-lived plant date, so it would not meet the lead rule. p3k14c does not record whether the other samples come from human activity at all. These observations come from the database fields only.

**Not recognized, with dates on charcoal, wood, plants, soil or other organics** (2; only those dates shown, the count includes any bone dates):
- Castro de Nossa Senhora da Guia (Iceland; 4 of 4 dates kept; GRONINGEN): GRA-29095 2,745 ± 45 (~2.8–3.0 ka cal, grain); GRA-29097 2,680 ± 40 (~2.7–2.9 ka cal, grain); +2 more
- Rangárbotnar (Iceland; 2 of 2 dates kept; ST): ST-813 2,820 ± 70 (~2.8–3.1 ka cal, wood); ST-814 2,660 ± 80 (~2.5–2.9 ka cal, wood)

**Not recognized, dated only on animal bone or unspecified material** (1; kept dates, oldest 14C BP): Svinavath (1; 2,740).

**Non-lead regions with candidates:** Remote Oceania (East Polynesia): Site 18-473G (Rapa Nui; 1 of 3 dates kept; BETA): BETA-199324 1,110 ± 40 (~0.9–1.2 ka cal, wood charcoal).

## Caveats
- p3k14c has no rows for the Caribbean islands, western Remote Oceania, New Zealand or Madagascar, and only Rapa Nui for East Polynesia. Sahul cannot be tested by radiocarbon under R1's 40,000 14C BP filter. None of these are nulls.
- p3k14c does not record whether a date is cultural. A date on fossil bone or natural wood below a site passes every R1 filter, and dates excavators rejected may be missing altogether.
- One limit covers each whole region, so areas settled later (Hokkaido, the Ryukyus, the later Polynesian pulse) are tested conservatively. Materials were classed by keywords; the bone filter uses the reference year as a proxy.

## Next step
Per R2 step 4, each lead goes to a researcher and a skeptic: is each site already debated, and is there a mundane cause (non-cultural sample, miscoded country, contamination)? No literature on the leads was consulted for this run.
