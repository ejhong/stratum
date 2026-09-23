# Design system

The owner's standard: **beautiful, dense, concise.** Tables and bullets instead of
narrative; smaller type; lots of information per screen; nothing flourishy. Every page answers
one question. If a section needs a paragraph to explain itself, redesign the section.

Tokens live in `site/assets/style.css`; charts in `scripts/charts.py`; templates in
`scripts/build_site.py`. Never edit `_site/`.

## Palette

| Token | Hex | Use |
|---|---|---|
| `--paper` / `--paper-2` / `--card` | #f8f5ef / #f1ece3 / #fffdf9 | ground, wells, cards |
| `--ink` / `--ink-2` / `--ink-3` | #1c1915 / #474036 / #6c6356 | text, secondary, tertiary (all AA on paper) |
| `--accent` | #9a3e1c | red ochre — the one accent: links, eyebrows, key years |
| `--vindicated` | #2b6858 | ● filled circle |
| `--partial` | #86661a | ◐ half circle |
| `--open` | #a4461f | ◎ ring with dot — the "live" color |
| `--refuted` | #6f6a62 | ✕ cross, ash grey |
| `--dark` | #1c1a17 | footer, decisive-test cards |

Rules: fate colors are never red-versus-green and **always travel with their shape**. No other
colors. Soil tints (`EPOCHS` in `charts.py`) belong to charts only.

## Type

- **Newsreader** (serif): page titles 1.65–2.2rem, section titles 1.05–1.28rem, big numbers.
- **IBM Plex Sans**: reading text 15px; secondary 13–13.5px.
- **IBM Plex Mono**: numbers, labels, eyebrows (11px uppercase, tracked), chart text 11–12px.
- Minimums: 12.5px for sentence text, 10.5px only for uppercase mono labels.

## Layout

- Width 1200px; gutter 16–28px. Sections separated by hairlines, 26px padding.
- Page head: eyebrow · title · one-line lede, with a stat block on the right.
- Two-column panels (`grid2`, `grid-6-4`) collapse to one column under 900px.
- Wide tables and charts scroll sideways on phones; nothing else may.

## Components

Stat block · fate chip · tag (status, draft) · sortable data table · facts strip · timeline ·
objection list (✓ held · ✕ wrong · ? unresolved) · evidence list · decisive tests (dark cards) ·
falsifier rule · collapsible sources with verification labels (● checked · ◐ exists ·
○ unverified) · record line (drafted, skeptic, stage) · profile dots (eight positive
features; the stake dot is ochre).

## Charts

All are SVG generated at build time from the catalog — no libraries.

| Chart | Where | Encodes |
|---|---|---|
| Deep-time section | home | x = year claimed, y = claimed age (log) over geological epochs with soil textures; bars = claimed ranges; hover a refuted case for its accepted age |
| Lifelines | home | claim → verdict per case; open cases dotted to "now" |
| Evidence matrix | findings | cases × nine features, grouped by fate |
| Strips | findings | leap factor (H1), years to verdict (H5), by fate |
| Ruler | case page | claimed age vs the accepted limit then vs accepted age now |
| Mini-section | card thumbnail | the case's claimed depth, when no photograph exists |

Rules: make the SVG `viewBox` width close to its rendered width so text renders near 1:1;
every mark is a link to its case with `data-name`/`data-info` for the tooltip; label
collisions are avoided in code, and a label that cannot fit is left to the tooltip.

## Images

Real photographs only, from Wikimedia Commons via `scripts/fetch_plates.py`, which checks
the license and takes credit and license text from Commons. Resized to at most 1400px and
stored as JPEG (quality 72). Shown slightly desaturated on cards, full color on case pages.
Never AI-generated images of evidence.

## Adding something new

Use `page()` in `build_site.py`; keep the nav at four items (Cases, Findings, Leads, Method).
Prefer a table row or a bullet over a new section, and a chart over a paragraph. Check desktop
(1440px) and phone (390px) screenshots before publishing.

## Link previews

What people see when a link is shared (iMessage, Slack, X, LinkedIn, WhatsApp):

- **Site card** (`site/assets/og.png`, 1200×630): wordmark, headline, fate counts, a
  stratigraphic column of the cases, and the latest bulletin in a dark strip.
- **Bulletin cards** (`og-bulletin-<n>.png`): dark, the headline large, one line of context,
  one small data graphic.
- **Case pages** preview with their own licensed photograph; the title carries the fate
  ("Piltdown Man — Refuted · Stratum"). Cases without a photograph use the site card.
- Every page carries complete Open Graph and Twitter tags (image size, alt text) and an
  `apple-touch-icon`. `scripts/make_og.py` regenerates the cards from the catalog; run it
  after each batch or bulletin. Platforms cache previews, so a changed card shows on new
  shares, not old ones.
