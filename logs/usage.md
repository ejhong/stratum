# Usage log

Approximate token use per batch of work, so costs stay visible. Figures come from the agent
run summaries; they are estimates, not invoices.

| Date | Batch | Agents (model · effort) | Approx. tokens | Notes |
|---|---|---|---|---|
| 2026-09-23 | Wave 1 · 10 researcher drafts | 10 × researcher (Opus, session effort) | ≈ 2.96M (270–340k each; 69–105 tool calls; ~21–26 min) | Before the lookup tool: raw API JSON and whole PDFs read into context. Budget stop sent mid-run. Monte Verde got a targeted exception for its 2026 re-contest. |
| 2026-09-23 | Wave 1 · 10 skeptic reviews | 10 × skeptic (Opus) | ≈ 1.50M (139–175k each; 27–37 tool calls; ~11–16 min) | With lookup.py and a 35-call budget. Verdicts: 1 pass, 9 revise, 0 fail; no fabricated sources. Majors were hindsight codings, misattributions, status calibration. |
| 2026-09-23 | Wave 2 · 14 researcher drafts (trial) | 14 × researcher (Sonnet), with lookup.py | ≈ 2.4M (148–203k each; 46–94 tool calls) | Skeptic major issues averaged ≈ 6.6 per record vs ≈ 2.7 for Opus drafts, incl. misreadings and false corrections → researchers return to Opus (D17). |
| 2026-09-23 | Wave 2 · 14 skeptic reviews | 14 × skeptic (Opus) | ≈ 2.1M (135–159k each; 26–38 tool calls) | 0 pass, 14 revise, 0 fail; no fabricated sources; one invented detail (Hueyatlaco). |
| 2026-09-23 | Revisions, waves 1–2 | 14 × Sonnet + 9 × Opus revisers | ≈ 3.4M (105–176k each; 11–35 tool calls) | Opus used where drafts had misread sources. All 24 starter records now reviewed. |
| 2026-09-23 | Discovery track R1 + megalith audit | 1 × Opus scan, 2 × Sonnet auditors | ≈ 0.50M | R1 null; audit under Opus review. |
