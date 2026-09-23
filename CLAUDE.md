# Stratum

*Strange finds, fair tests.*

Live site: https://ejhong.github.io/stratum/ · Repository: https://github.com/ejhong/stratum

**Read first:** `docs/RUNBOOK.md` (how to run a batch) · `docs/DECISIONS.md` (why things are
as they are; newer entries win) · `docs/DESIGN.md` (the site's design system).

## Mission

Stratum is an AI-operated research lab for archaeology, history and human origins. It looks
for genuine discoveries hiding in existing data: anomalies the field may have dismissed too
quickly, and patterns no single researcher could see across thousands of sources.

The model is Anthropic's 2026 biology work, where hundreds of Claude agents combed a huge
DNA database, flagged something unusual, and human scientists tested it in a lab. Here the
"database" is the published archaeological record, and the "wet lab" is a partner
archaeologist who can check leads with new dates, specimen re-examination or fieldwork.

Two outputs matter, and the site shows both:

1. **Lessons**: how past anomalies actually fared, and what separated the real ones from the
   ones that fell apart.
2. **Leads**: open anomalies ranked by how closely they resemble past vindications, each
   with the specific, affordable test that would settle it. A paradigm change, if one is
   hiding in the record, should surface here first.

## Core principles (non-negotiable)

1. **Evenhanded testing.** Anomalies get checked as hard as orthodoxy does. We are not trying
   to prove the mainstream wrong, or to defend it. We want to find out what is true.
2. **Mundane explanations first.** Before treating anything as a real anomaly, rule out
   contamination, dating error, stratigraphic mixing, misidentification, hoax and recording
   error.
3. **Falsifiability.** Every hypothesis, record and finding states in advance what evidence
   would disprove it. Hypotheses are pre-registered in `findings/log.md` before the data
   that tests them exists, and are tested exactly as worded.
4. **No fabrication, ever.** Every factual claim needs a real source (DOI, URL, or full
   bibliographic reference) that was actually checked. Never invent citations, dates,
   authors, figures or quotes. Unconfirmed sources are labelled `unverified` and never
   carry a key field.
5. **Honest uncertainty.** Many cases are still disputed. Say so rather than force a
   verdict. Small samples get small claims.
6. **Heritage ethics.** Locations stay at country/region level. Never publish coordinates,
   directions or restricted site information. Never encourage unpermitted digging. Fieldwork
   is done only by credentialed archaeologists with permits.

## How the lab works

Agent roles are defined in `.claude/agents/` (each file sets the model, effort and tools):

| Agent | Job | Model · effort | Can use |
|---|---|---|---|
| `researcher` | Drafts or revises ONE case record from published sources | Opus · high | web, files, scripts |
| `skeptic` | Attacks ONE draft: citations, mundane explanations, hindsight, overconfidence. Writes a review; never edits cases | Opus · high | web, read, reviews |
| `analyst` | Tests pre-registered hypotheses on the verified catalog | Opus · high | files, scripts; **no web** |
| `scout` | Finds candidate cases for expansion, with two real sources each | Sonnet · medium | web, candidates file |

The pipeline for every case:

1. **Scout** proposes candidates in `catalog/candidates.json`.
2. **Researcher** drafts `catalog/cases/<id>.json`; it must pass `scripts/validate.py` and
   `scripts/check_sources.py`.
3. **Skeptic** reviews it into `catalog/reviews/<id>.json` (pass / revise / fail).
4. On `revise`, the same researcher fixes it (continue that agent with SendMessage so it
   keeps its context). Disagreements are recorded in `review.open_issues`, not hidden.
5. The main session spot-checks, sets `review.stage` to `published`, rebuilds the site,
   logs usage and pushes.
6. The **analyst** runs after each batch of about 10 records and updates the findings.

**Source verification labels**: `checked` (opened and confirmed it says what it is cited
for) · `exists` (metadata confirmed, content not read, e.g. paywalled) · `unverified`.

**Cost policy: scripts sift the haystack, models judge the needles.**
- Anything mechanical is a script and costs no tokens: validation, citation matching, image
  import, database, analysis, site, and (Phase 2) scanning whole databases for outliers.
- Model reasoning is spent where judgment matters: drafting records, the skeptic gate, and
  weighing the small residue that survives the scripts.
- Agents use `scripts/lookup.py` for every lookup (citation, abstract, open-access status,
  `page --grep` for passages) and never read raw API output or whole PDFs: everything an
  agent reads is re-read on every later step. Budgets: researcher ≈ 40 tool calls, skeptic
  ≈ 35. One case per agent.
- Researchers and skeptics run on Opus: a trial with Sonnet researchers produced about 2.4×
  the major issues, including misread sources (D17). Sonnet does mechanical revisions, scouting
  and structured audits, always checked by an Opus skeptic. Never downgrade the skeptic. Log
  tokens per batch in `logs/usage.md`.

## Phase 1: The Anomaly Fates Catalog (current)

A structured catalog of archaeological and paleoanthropological anomalies whose fate is
known, plus those still open, and an analysis of what distinguished the real from the false.

### Research questions

- What features did vindicated anomalies share (independent dating methods, clean
  stratigraphy, replication, open material)?
- What features did refuted ones share (single date, poor provenance, one investigator, no
  replication, an outside stake)?
- Which objections raised against vindicated anomalies turned out to be bias rather than
  evidence?
- How long did resolution take, and what finally settled each case?
- Applying these lessons: which open anomalies most resemble past vindications?

Pre-registered hypotheses H1–H6 in `findings/log.md` turn these questions into tests.

### Records

`catalog/schema.json` is the authoritative contract; its field descriptions are
instructions. Key design choices:

- **Hard length budgets** on every text field, enforced by the build. This keeps the site
  short and readable. Shorten; never raise a budget to fit a wordy draft.
- **Structured ages** (calendar years before 1950) for the claimed age, the accepted age,
  and the then-accepted limit, so the site can plot deep time and compute leap size.
- **`features_at_claim`**: nine diagnostic features coded as they stood within about five
  years of the claim, not with hindsight, each with a source. This drives the analysis.
- **Objections** carry a `kind` (prior, context, dating, identification, integrity) and an
  `outcome` (held, wrong, unresolved). "Objections that were wrong" are those with
  `outcome = wrong`.
- **`decisive_tests`** (required for open and partial cases) are the field partner's queue.
- **`location`** holds country, region and continent only.
- **`plates`** name Wikimedia Commons files; license and credit are fetched from Commons by
  `scripts/fetch_plates.py`, never typed by hand. Real photographs only; never AI images.

### Inclusion rules (to limit selection bias)

A case enters when (1) a specific claim was made publicly by a named person or team,
(2) it contradicted the accepted view of its time, and (3) at least two independent
published sources discuss it. Famous vindications are over-remembered and quiet failures
are under-remembered, so the scout actively seeks obscure refutations and claims that were
simply abandoned. Record how each candidate was found (`found_via`).

### Starter cases

Written from general knowledge; every detail must be verified, and corrections recorded in
each record's `corrections` field.

- *Largely vindicated:* Monte Verde (Chile), White Sands footprints (New Mexico), Jebel
  Irhoud (Morocco), Denisovans, *Homo floresiensis* (Indonesia), Paisley Caves (Oregon),
  Bluefish Caves (Yukon), Göbekli Tepe (Turkey), L'Anse aux Meadows (Canada), Troy/Hisarlik
  (Turkey).
- *Refuted:* Piltdown Man, Calico Hills (California), the Japanese Paleolithic fraud
  (Fujimura, 2000), Cardiff Giant, Glozel (France), Kensington Runestone, Bosnian
  "pyramids".
- *Open or disputed:* Cerutti Mastodon (California), Pedra Furada (Brazil), Hueyatlaco
  (Mexico), Topper (South Carolina), Meadowcroft Rockshelter (Pennsylvania), Madjedbebe
  (Australia), the Tecaxic-Calixtlahuaca head (Mexico).

Expansion ideas (verify first): Sunnyvale and Del Mar skeletons, Old Crow flesher, Jinmium,
Valsequillo footprints, Calaveras skull, Galley Hill, Moulin-Quignon, Kennewick Man ancestry,
Gunung Padang (retracted 2024), Vinland Map, Bat Creek Stone, Great Zimbabwe origin claims,
the Mound Builder myth, Chiquihuite Cave, Polynesian–American contact, Neanderthal cave art,
*Homo naledi* burial. *Forbidden Archaeology* (Cremo & Thompson, 1993) can be mined for
candidates, but only with independent literature on each.

Target: about 60 balanced, reviewed records — enough to test H1–H6 at their thresholds —
before Phase 2 starts; 100+ over time.

## The site

The site is how the lab reports: every record, finding and lead appears there
automatically. The owner's standard is **beautiful, dense and concise**: tables and bullets
rather than narrative, smaller type, lots of information per screen, nothing flourishy. Full
system in `docs/DESIGN.md`.

- **Generated, never hand-edited.** `python3 scripts/build.py` validates the catalog, builds
  the SQLite database, runs the analysis, and writes the static site to `_site/`. Pushing to
  `main` runs `.github/workflows/pages.yml`, which builds and deploys to GitHub Pages. The
  build fails on any invalid record.
- **Keep the top current.** The home page opens with "What we’ve found so far"
  (`findings/summary.json`), updated after every batch or result; big results also get a
  dated lab bulletin (`findings/bulletins/`). Never overstate: leads are leads.
- **Pages** (each answers one question): Home (the record at a glance), Cases (the catalog),
  a page per case, Findings (hypotheses and patterns), Leads (open cases and the tests that
  would settle them), Method (how the lab works, and its costs).
- **Design rules** (`site/assets/style.css` holds the tokens):
  - Show, don't tell: charts are generated from the data (deep-time section, lifelines,
    evidence matrix, strips, per-case ruler). Tables and bullets, not paragraphs.
  - One accent color. Fate colors are never red-versus-green and always paired with a shape:
    vindicated ● · partial ◐ · open ◎ · refuted ✕.
  - Newsreader for titles, IBM Plex Sans for reading (15px), IBM Plex Mono for numbers and
    labels. WCAG AA contrast; works on a phone (wide tables and charts scroll sideways).
  - Drafts appear labelled "Draft"; only skeptic-reviewed records count in the analysis.
  - Real, credited photographs only. No precise locations anywhere.
- New page types must fit this system. Prefer removing words to adding sections.

## Later phases

Phase 1 is the teacher (what distinguishes real anomalies from false ones); Phase 2 is the
search engine (anomalies nobody has flagged yet), filtered by Phase 1's lessons. Phase 2
starts once Phase 1 reaches about 60 reviewed records, and runs alongside it.

- **Phase 2 · Radiocarbon residue.** The closest analog to the biology work. Scan open
  radiocarbon databases (p3k14c, XRONOS, CARD, regional sets) for dates that contradict their
  site's or region's accepted chronology. Classify the mundane causes automatically (old
  wood, marine reservoir, pre-AMS bone dates, lab flags, context notes). What remains is the
  residue. The wet-lab test is cheap: re-date the archived sample.
- **Phase 3 · Grey literature.** Read unpublished excavation reports at scale (e.g. the
  Archaeology Data Service library) for anomalous finds and dates that never reached a
  journal. This is where reading everything, AI's real advantage, matters most.
- **Phase 4 · Landscape survey.** Open LiDAR and satellite data for unrecorded features.
  Results go privately to the relevant heritage authority; the site shows region-level
  summaries only.
- **Special study · The signature test.** Pre-register what an advanced Ice Age civilization
  would have left that is hard to erase (metal pollution in ice cores, domesticate genetics,
  quarry scars, refuse), then check the open data. A positive result would be enormous; a
  null result is also an answer.
- **Partnership (continuous).** Once the Leads page has 25+ records behind it, approach an
  academic archaeologist or radiocarbon lab with the ranked leads.

## Directory structure

```
stratum/
├── CLAUDE.md               this file
├── README.md
├── .claude/agents/         agent roles: researcher, skeptic, analyst, scout
├── catalog/
│   ├── schema.json         the record contract (authoritative)
│   ├── cases/              one JSON record per case
│   ├── reviews/            one skeptic review per case
│   ├── checks/             machine citation checks per case (generated)
│   ├── candidates.json     scout proposals awaiting research
│   └── stratum.db          SQLite database (generated, not committed)
├── docs/                   RUNBOOK, DECISIONS (append-only), DESIGN
├── findings/log.md         pre-registered hypotheses, observations, leads
├── analysis/outputs/       analysis results (generated)
├── scripts/                validate, check_sources, lookup, fetch_plates, build (+ db, analysis, site, charts)
├── site/                   site source: styles, scripts, photographs
├── sources/                research notes (PDFs stay local and are not committed)
├── logs/usage.md           approximate token cost per batch
├── inputs/                 the founding conversation
└── .github/workflows/      build and deploy to GitHub Pages
```

## Commands

```bash
python3 scripts/validate.py              # check every record against the schema
python3 scripts/check_sources.py [id]    # verify DOIs and URLs (needs network)
python3 scripts/lookup.py doi <doi>      # compact citation + abstract (also: search, page --grep, commons)
python3 scripts/fetch_plates.py          # download licensed Commons photographs
python3 scripts/build.py                 # validate → database → analysis → site in _site/
python3 -m http.server -d _site 8000     # preview at http://localhost:8000
```

Python 3.11+ standard library only; nothing to install. Start Claude Code from the repository
root (`stratum/`) so the agent roles in `.claude/agents/` load.

## Working style

- The owner is not a professional programmer: explain technical steps plainly and keep
  commands copy-pasteable.
- Quality before scale: grow in batches of about 10, and review each batch before the next.
- Prefer open-access sources; note paywalls.
- Keep costs visible in `logs/usage.md`.
- Commit with clear messages; push when a batch is published so the site updates.
