# Usage log

Approximate token use per batch of work, so costs stay visible. Figures come from the agent
run summaries; they are estimates, not invoices.

| Date | Batch | Agents (model · effort) | Approx. tokens | Notes |
|---|---|---|---|---|
| 2026-09-23 | Wave 1 · 10 researcher drafts | 10 × researcher (Opus, session effort) | ≈ 2.96M (270–340k each; 69–105 tool calls; ~21–26 min) | Before the lookup tool: raw API JSON and whole PDFs read into context. Budget stop sent mid-run. Monte Verde got a targeted exception for its 2026 re-contest. |
| 2026-09-23 | Wave 1 · 10 skeptic reviews | 10 × skeptic (Opus) | ≈ 1.50M (139–175k each; 27–37 tool calls; ~11–16 min) | With lookup.py and a 35-call budget. Verdicts: 1 pass, 9 revise, 0 fail; no fabricated sources. Majors were hindsight codings, misattributions, status calibration. |
