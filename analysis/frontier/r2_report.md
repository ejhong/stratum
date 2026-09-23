# R2 · Frontier scan: dates older than the accepted first arrival

*Run 2026-09-23 with `scripts/frontier/scan.py`. Method pre-registered in `findings/log.md` (R2); regions, limits and the conversion rule were fixed in `limits.json` and pushed first (commit be225f4). Full detail: `r2_summary.json`. No coordinates were read; sites are named only.*

**Result: 2 lead region(s): The Americas, Iceland.** A lead means pre-limit dates recur at ≥ 3 sites with ≥ 2 labs and ≥ 2 material classes after R1's mundane filters. It is a list for the researcher and skeptic, not a finding.

## Method in brief
Each region's limit (calendar years BP) was turned into a radiocarbon threshold: the oldest age the IntCal20 mean curve reaches at or after the limit, with the curve's own error. A date counts if it is older than that threshold by more than 2 combined standard errors. Then R1's filters removed reservoir-prone materials, bone without a post-1990 reference, ages over 40,000 14C BP, and split or duplicate samples. IntCal20 is used everywhere, which is slightly permissive in the Southern Hemisphere.

## Funnel (all regions)

| Stage | Dates | Sites |
|---|---:|---:|
| dates in a defined region | 77,098 | 13,456 |
| with a usable site name | 59,331 | 13,456 |
| older than the limit by > 2 SE | 487 | 157 |
| after (a) reservoir-prone materials | 468 | 152 |
| after (b) bone before 1990 / year unknown | 305 | 97 |
| after (c) ages over 40,000 14C BP | 275 | 90 |
| after (d) split or duplicate samples = candidates | 273 | 89 |

Pre-limit dates with no usable site name (not countable as sites): 20. Removed as reservoir-prone: aquatic animal 11, sediment 5, shell 3. Bone: 151 pre-1990, 12 no year. Over 40,000: 30. Split/duplicate or no lab number: 2.

## Regions

| Region | Limit (cal BP) | 14C threshold | Dates in region | Pre-limit (> 2 SE) | Candidates | Sites | Labs | Classes | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| The Americas | 17,500 | 14,442 ± 40 | 71,961 | 479 | 265 | 85 | 29 | 5 | LEAD |
| Sahul | 50,000 | 47,531 ± 354 | 3,624 | 0 | 0 | 0 | 0 | 0 | untestable by design: limit is beyond R1's 40,000 14C BP filter |
| Japanese Archipelago | 40,000 | 34,918 ± 125 | 1,433 | 0 | 0 | 0 | 0 | 0 | not a lead |
| Remote Oceania, western part: Micronesia, Island Melanesia beyond the main Solomons chain, Fiji and West Polynesia | 3,450 | 3,227 ± 12 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no p3k14c rows |
| Remote Oceania, East Polynesia except New Zealand | 925 | 1,009 ± 10 | 73 | 1 | 1 | 1 | 1 | 1 | not a lead |
| New Zealand | 670 | 718 ± 11 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no p3k14c rows |
| Iceland | 1,080 | 1,201 ± 13 | 7 | 7 | 7 | 3 | 3 | 2 | LEAD |
| Madagascar | 1,450 | 1,603 ± 13 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no p3k14c rows |
| The Caribbean islands | 5,800 | 5,084 ± 17 | 0 | 0 | 0 | 0 | 0 | 0 | untestable: no p3k14c rows |

## Lead: The Americas (mainland North, Central and South America, including Beringia and continental islands)

85 sites; labs: AECV, ARIZONA, AU, B, BETA, BGS, CAMS, DIC, GEORGIA, GSC, GX, I, ISGS, L, LUND, NSRL, OXA, QC, RIDDL, S, SI, SMU, ST, TO, TX, UCIAMS, USGS, W, WSU; material classes: bone/tooth/antler, charcoal/wood, other organic, short-lived plant, soil/peat/humate. Oldest kept date per site shown; every kept date is in the JSON. 'Known?' is from general knowledge only, not checked against the literature.

| Site | Country / province | Kept pre-limit dates (of all at site) | Oldest kept: lab no., 14C BP, ~cal BP (2σ), material | Labs | Known? |
|---|---|---:|---|---|---|
| Banks Island mammoth | Canada / Northwest Territories | 1 (1) | TO-2355, 20,700 ± 270, 24,200–25,660, mammoth bone collagen; collagène osseux de mammouth | TO | not recognized |
| Beaverhouse Hill | USA | 1 (1) | GX-13092C, 16,950 ± 260, 19,860–21,010, bone collagen; collagène osseux | GX | not recognized |
| Beaverlodge | Canada / Alberta | 1 (1) | AECV-1185C, 24,640 ± 940, 27,170–30,880, mammoth bone collagen; collagène osseux de mammouth | AECV | not recognized |
| Bechan Cave | USA / Utah | 1 (32) | A-3514, 16,700 ± 250, 19,540–20,810, plant remains; restes de plantes | ARIZONA | not recognized |
| Bluefish Cave 3 | Canada / Yukon Territories | 2 (9) | TO-1196, 33,550 ± 350, 37,160–39,400, ferret bone collagen; collagène osseux de furet | TO | not recognized |
| Bushe River | Canada / Alberta | 1 (2) | AECV-719C, 22,020 ± 450, 25,390–27,250, mammoth bone collagen; collagène osseux de mammouth | AECV | not recognized |
| Cactus Hill | USA / Virginia | 1 (25) | BETA-81590, 15,070 ± 70, 18,230–18,630, charcoal; charbon de bois | BETA | not recognized |
| Canyon Creek | USA | 1 (1) | SMU-640, 39,390 ± 1,740, 41,050–45,340, horse bone collagen; collagène osseux de cheval | SMU | not recognized |
| Cape Krusenstern | USA | 1 (31) | B-265, 26,100 ± 400, 29,650–31,090, peat; tourbe | B | not recognized |
| Chatanika River | USA | 35 (51) | AA-3897, 33,000 ± 750, 35,970–39,620, animal remains; restes d'animaux | ARIZONA, CAMS, DIC, L, QC, SI, ST | not recognized |
| Chuchi Lake | Canada | 3 (3) | BETA-78574, 35,480 ± 1,080, 37,730–42,160, bison bone collagen; collagène osseux de bison | BETA, TO | not recognized |
| Chugachik Island | USA | 1 (7) | WSU-4302, 18,910 ± 250, 22,360–23,660, charcoal; charbon de bois | WSU | not recognized |
| Clam Gulch | USA | 1 (8) | BETA-6689, 16,280 ± 110, 19,430–19,910, charcoal; charbon de bois | BETA | not recognized |
| Clover Bar Pit | Canada / Alberta | 4 (6) | AECV-1202C, 31,220 ± 1,260, 33,120–39,070, horse bone collagen; collagène osseux de cheval | AECV | not recognized |
| Colorado Creek | USA | 2 (4) | AA-683, 16,150 ± 230, 18,930–20,080, animal remains; restes d'animaux | ARIZONA, BETA | not recognized |
| Consolidated Pit 45 | Canada / Alberta | 2 (5) | AECV-1582C, 35,760 ± 2,130, 35,970–43,060, wood; bois | AECV | not recognized |
| Consolidated Pit 46 | Canada / Alberta | 3 (3) | AECV-718C, 39,960 ± 3,950, 36,330–50,280, mammoth bone collagen; collagène osseux de mammouth | AECV, TO | not recognized |
| Consolidated Pit 48 | Canada / Alberta | 7 (8) | AECV-935C, 38,980 ± 3,520, 36,250–48,300, mammoth bone collagen; collagène osseux de mammouth | AECV | not recognized |
| Crawford Knoll | Canada / Ontario | 1 (2) | TO-921, 15,120 ± 100, 18,230–18,680, bone collagen; collagène osseux | TO | not recognized |
| Dawson Loc. 10 | Canada / Yukon Territories | 1 (4) | BETA-83413, 37,990 ± 750, 41,410–42,830, badger bone collagen; collagène osseux de blaireau | BETA | not recognized |
| Dawson Loc. 12 | Canada / Yukon Territories | 2 (4) | BETA-23347, 30,370 ± 560, 33,860–35,960, ferret bone collagen; collagène osseux de furet | BETA | not recognized |
| Dawson Loc. 29 | Canada / Yukon Territories | 2 (2) | TO-3712, 35,610 ± 340, 40,010–41,280, moose bone collagen; collagène osseux d' orignal | BETA, TO | not recognized |
| Dawson Loc. 31 | Canada / Yukon Territories | 1 (1) | TO-2696, 26,040 ± 270, 29,920–30,930, bear bone collagen; collagène osseux d' ours | TO | not recognized |
| Dawson Loc. 37 | Canada / Yukon Territories | 1 (2) | TO-3707, 24,850 ± 150, 28,780–29,250, bear bone collagen; collagène osseux d' ours | TO | not recognized |
| Dawson Loc. 57 | Canada / Yukon Territories | 1 (1) | OXA-9259, 26,720 ± 290, 30,310–31,220, bear bone collagen; collagène osseux d'ours | OXA | not recognized |
| Dawson Loc. 60 | Canada / Yukon Territories | 1 (1) | LU-3010, 37,220 ± 830, 40,740–42,560, mammoth bone collagen; collagène osseux de mammouth | LUND | not recognized |
| Dawson Loc. 63 | Canada / Yukon Territories | 2 (2) | BETA-33192, 30,810 ± 975, 33,270–37,070, bison bone collagen; collagène osseux de bison | BETA | not recognized |
| Dawson Loc. 77 | Canada / Yukon Territories | 1 (1) | BETA-79852, 20,250 ± 110, 24,030–24,620, bear bone collagen; collagène osseux d' ours | BETA | not recognized |
| Drift Fence site | USA / Oregon | 1 (7) | BETA-146263, 24,700 ± 80, 28,770–29,130, CHARCOAL | BETA | not recognized |
| Dry Creek | USA / Wyoming | 1 (24) | SI-1544, 19,050 ± 1,500, 19,420–26,340, charcoal; charbon de bois | SI | not recognized |
| Duhme Cave | USA | 1 (1) | BETA-56040, 21,780 ± 240, 25,700–26,430, unknown; inconnu | BETA | not recognized |
| Eagle Cave | Canada / Alberta | 2 (4) | TO-6350, 34,860 ± 470, 39,190–40,970, marmot bone collagen; collagène osseux de marmotte | TO | not recognized |
| Epiguruk | USA | 9 (12) | USGS-1514, 36,850 ± 750, 40,560–42,380, horse bone collagen; collagène osseux de cheval | USGS | not recognized |
| Esther | USA | 2 (3) | AA-17515, 34,974 ± 652, 39,000–41,270, bear bone collagen; collagène osseux d'ours | ARIZONA | not recognized |
| Galt Island Bluff | Canada / Alberta | 2 (4) | GSC-14422, 38,700 ± 1,100, 41,410–44,110, wood; bois | GSC | not recognized |
| Gerstle River | USA | 1 (7) | BETA-109267, 15,090 ± 70, 18,240–18,640, horse bone collagen; collagène osseux de cheval | BETA | not recognized |
| Goldstream | USA | 85 (152) | AA-17514, 39,565 ± 1,126, 42,030–44,590, bear bone collagen; collagène osseux d'ours | ARIZONA, CAMS, I, OXA, QC, SI | not recognized |
| Harvard bison | USA | 1 (1) | W-544, 21,280 ± 1,000, 23,140–27,460, bison bone; os de bison | W | not recognized |
| HH75-1 | Canada / Yukon Territories | 1 (1) | TO-124, 34,220 ± 178, 39,160–39,680, rodent feces; féces de rongeur | TO | not recognized |
| Hillsborough Mastodon | Canada / New Brunswick | 1 (3) | GSC-2469, 37,200 ± 1,310, 39,680–42,960, wood; bois | GSC | not recognized |
| Hungry Creek | Canada / Yukon Territories | 1 (1) | GSC-2422, 36,900 ± 300, 41,290–42,100, beaver-chewed wood; bois rongé par des castors | GSC | not recognized |
| Iceberg | Canada / Newfoundland | 1 (8) | SI-2431, 18,730 ± 850, 20,540–24,580, charcoal; charbon de bois | SI | not recognized |
| Ikpikpuk River | USA | 6 (11) | TO-2539, 27,190 ± 280, 30,980–31,680, bear bone collagen; collagène osseux d'ours | DIC, GX, I, TO | not recognized |
| Jim Pitts | USA / South Dakota | 1 (22) | AA-35949, 38,000 ± 1,300, 40,600–43,850, CHARCOAL | ARIZONA | not recognized |
| Kangiguksuk | USA | 1 (2) | CAMS-107317, 34,820 ± 460, 39,180–40,920, Bone collagen | CAMS | not recognized |
| Ketza River | Canada / Yukon Territories | 1 (1) | TO-393, 26,350 ± 280, 30,050–31,100, bison bone collagen; collagène osseux de bison | TO | not recognized |
| Likely mammoth | Canada | 1 (1) | S-1036, 20,190 ± 190, 23,820–24,770, charcoal; charbon de bois | S | not recognized |
| Lime Hills 1 | USA | 1 (7) | BETA-67670, 27,950 ± 560, 31,070–33,670, bison bone collagen; collagène osseux de bison | BETA | not recognized |
| Lost Chicken Creek | USA | 2 (18) | AA-3076, 31,390 ± 780, 34,350–37,340, saiga bone collagen; collagène osseux de saéga | ARIZONA, I | not recognized |
| Manis Mastodon | USA / Washington | 1 (13) | UCIAMS-29116, 29,070 ± 230, 33,040–34,170, BONE | UCIAMS | not recognized |
| Mead | USA | 1 (9) | NSRL-2000, 17,370 ± 90, 20,800–21,160, mammoth bone collagen; collagène osseux de mammouth | NSRL | not recognized |
| Meadowcroft Rockshelter | USA / Pennsylvania | 6 (6) | OXA-363, 31,400 ± 1,200, 33,580–39,120, CHARCOAL | DIC, OXA, SI | not recognized |
| Melville Island mammoth | Canada / Northwest Territories | 1 (2) | GSC-1760, 21,000 ± 320, 24,500–25,910, mammoth bone collagen; collagène osseux de mammouth | GSC | not recognized |
| Millard Creek | Canada | 1 (5) | S-142, 16,910 ± 270, 19,640–20,990, charcoal; charbon de bois | S | not recognized |
| North Saskatchewan River | Canada / Alberta | 3 (9) | AECV-720C, 29,380 ± 4,970, 23,360–42,760, horse bone collagen; collagène osseux de cheval | AECV | not recognized |
| Old Crow Loc. CRH-12 | Canada / Yukon Territories | 2 (4) | RIDDL-307, 38,200 ± 1,200, 40,970–43,850, mammoth bone collagen; collagène osseux de mammouth | RIDDL, TO | not recognized |
| Old Crow Loc. CRH-13 | Canada / Yukon Territories | 1 (1) | RIDDL-123, 35,800 ± 1,000, 39,120–42,210, mammoth bone collagen; collagène osseux de mammouth | RIDDL | not recognized |
| Old Crow Loc. CRH-22 | Canada / Yukon Territories | 1 (4) | I-4229, 33,880 ± 2,000, 34,380–42,240, moose bone collagen; collagène osseux d' orignal | I | not recognized |
| Old Crow Loc. CRH-4 | Canada / Yukon Territories | 1 (3) | RIDDL-122, 31,120 ± 450, 34,580–36,300, mammoth? bone collagen; collagène osseux de mammouth | RIDDL | not recognized |
| Old Crow Loc. CRH-47 | Canada / Yukon Territories | 1 (1) | RIDDL-733, 37,800 ± 800, 41,230–42,800, mammoth bone collagen; collagène osseux de mammouth | RIDDL | not recognized |
| Old Crow Loc. CRH-70 | Canada / Yukon Territories | 1 (1) | RIDDL-136, 37,300 ± 750, 40,970–42,530, bison bone collagen; collagène osseux de bison | RIDDL | not recognized |
| Old Crow Loc. CRH-71 | Canada / Yukon Territories | 1 (3) | RIDDL-127, 39,500 ± 1,600, 41,290–45,180, mammoth bone collagen; collagène osseux de mammouth | RIDDL | not recognized |
| Old Crow Loc. CRH-87 | Canada / Yukon Territories | 1 (5) | RIDDL-727, 31,200 ± 500, 34,570–36,440, mammoth? bone collagen; collagène osseux de mammouth | RIDDL | not recognized |
| Old Crow Loc. REM78-1 | Canada / Yukon Territories | 3 (6) | RIDDL-137, 35,700 ± 900, 39,180–42,100, mammal bone collagen; collagène osseux de mammiféres | RIDDL | not recognized |
| Old Wound | USA | 1 (3) | AU-90, 26,900 ± 3,400, 24,150–39,040, peat; tourbe | AU | not recognized |
| On Your Knees Cave | USA | 6 (21) | AA-15227, 35,365 ± 800, 39,090–41,870, bear bone collagen; collagène osseux d'ours | ARIZONA | not recognized |
| Paw Paw Cove | USA / Maryland | 1 (2) | AA-3870, 17,820 ± 170, 21,020–22,110, wood; bois | ARIZONA | not recognized |
| Petroglyph Canyon | USA / Montana | 1 (2) | AA-6537, 15,695 ± 135, 18,760–19,230, CHARCOAL | ARIZONA | not recognized |
| Phillis | USA / Pennsylvania | 1 (1) | BETA-108382, 16,280 ± 100, 19,450–19,890, CHARCOAL | BETA | not recognized |
| Porcupine River Cave 1 | USA | 2 (6) | BETA-37057, 38,260 ± 830, 41,500–43,010, sheep bone collagen; collagène osseux de mouflon | BETA, DIC | not recognized |
| Riverview Pit | Canada / Alberta | 1 (1) | AECV-941C, 31,290 ± 1,960, 31,250–40,450, mammal bone collagen; collagène osseux de mammiféres | AECV | not recognized |
| Rock Levee | USA / Mississippi | 1 (7) | UGA-6060, 16,479 ± 571, 18,690–21,360, CHARCOAL | GEORGIA | not recognized |
| Schowalter | Canada / Alberta | 2 (2) | TO-872, 28,000 ± 250, 31,380–32,920, prairie dog bone collagen; collagène osseux de chien de prairie | TO | not recognized |
| Seward | Canada / Alberta | 2 (3) | TO-1307, 25,980 ± 180, 29,980–30,740, prairie dog bone collagen; collagène osseux de chien de prairie | TO | not recognized |
| Simpson Point | Canada / Yukon Territories | 2 (6) | BETA-70841, 36,160 ± 530, 40,340–41,990, horse bone collagen; collagène osseux de cheval | BETA, RIDDL | not recognized |
| Sixtymile Loc. 3 | Canada / Yukon Territories | 6 (14) | TO-214, 39,560 ± 490, 42,450–43,390, ferret bone collagen; collagène osseux de furet | BETA, CAMS, TO | not recognized |
| Sixtymile Loc. 5 | Canada / Yukon Territories | 2 (3) | BETA-16163, 24,980 ± 1,300, 26,480–31,560, mastodon bone collagen; collagène osseux de mastodonte | BETA | not recognized |
| Smiling Dan | USA / Illinois | 1 (15) | ISGS-851, 23,380 ± 500, 26,480–28,670, plant remains; restes de plantes | ISGS | not recognized |
| Sullivan Creek | USA | 2 (4) | AA-26858, 18,060 ± 130, 21,480–22,290, horse bone collagen; collagène osseux de cheval | ARIZONA, SI | not recognized |
| The Burn Site | USA / Kansas | 1 (1) | TX-8484, 20,425 ± 396, 23,760–25,650, CHARCOAL | TX | not recognized |
| The Forks | Canada / Manitoba | 1 (34) | BGS-1315, 16,330 ± 200, 19,180–20,240, charcoal; charbon de bois | BGS | not recognized |
| Trail Creek Cave 9 | USA | 1 (16) | BETA-35839, 16,300 ± 140, 19,380–20,030, caribou bone collagen; collagène osseux de caribou | BETA | not recognized |
| Ugashik Narrows | USA | 1 (16) | SI-2079, 35,700 ± 3,000, 34,280–44,540, charcoalé; charbon de boisé | SI | not recognized |
| Whitestone mammoth CRH-43 | Canada / Yukon Territories | 1 (1) | I-3576, 30,380 ± 2,000, 30,780–39,510, mammoth bone collagen; collagène osseux de mammouth | I | not recognized |
| Winter | Canada / Alberta | 1 (5) | TO-1142, 33,650 ± 340, 37,390–39,460, prairie dog bone collagen; collagène osseux de chien de prairie | TO | not recognized |

## Lead: Iceland

3 sites; labs: GRONINGEN, OXA, ST; material classes: charcoal/wood, short-lived plant. Oldest kept date per site shown; every kept date is in the JSON. 'Known?' is from general knowledge only, not checked against the literature.

| Site | Country / province | Kept pre-limit dates (of all at site) | Oldest kept: lab no., 14C BP, ~cal BP (2σ), material | Labs | Known? |
|---|---|---:|---|---|---|
| Castro de Nossa Senhora da Guia | Iceland | 4 (4) | GRA-29095, 2,745 ± 45, 2,760–2,950, grain | GRONINGEN | not recognized |
| Rangárbotnar | Iceland | 2 (2) | ST-813, 2,820 ± 70, 2,760–3,150, wood | ST | not recognized |
| Svinavath | Iceland | 1 (1) | OXA-441, 2,740 ± 100, 2,720–3,140, not given | OXA | not recognized |

Non-lead regions with some candidates: Remote Oceania, East Polynesia except New Zealand: Site 18-473G (BETA-199324, 1,110 ± 40).

## Caveats
- Coverage: p3k14c has no rows for the Caribbean islands, western Remote Oceania, New Zealand or Madagascar, and only Rapa Nui for East Polynesia; those results say nothing about the regions themselves.
- Sahul cannot be tested with radiocarbon under R1's filters: 50,000 cal BP lies beyond the 40,000 14C BP cut-off.
- One limit per region is applied everywhere in it; regions settled in stages (Beringia vs. the south, Hokkaido and the Ryukyus, the second Polynesian pulse) are tested conservatively.
- p3k14c is a compilation: dates that excavators rejected may be missing, names and materials are as compiled, and a date's context (is it cultural at all?) is not recorded. A pre-limit date may be from a natural layer below the occupation.
- Material classes come from keyword matching and the bone filter uses the earliest reference year as a proxy.

## Next step
Per R2 step 4, every lead goes to a researcher and a skeptic: is each site already debated, and is there a mundane cause? No literature on the leads was consulted for this run.
