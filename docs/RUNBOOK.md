# Runbook

How to run the lab. Written for the owner and for any Claude session picking up the work.

## Start a session

```bash
cd ~/prj/stratum && claude
```

Start from the repository root so the agent roles in `.claude/agents/` load (researcher,
skeptic, analyst, scout). A good opening message: *"Read docs/RUNBOOK.md and
docs/DECISIONS.md, check the state of the catalog, and run the next batch."*

## Run a batch of about ten cases

1. **Choose cases.** From `catalog/candidates.json` (or the expansion list in CLAUDE.md),
   pick about ten, balanced across vindicated, refuted and open. If candidates run low, spawn
   one `scout` first.
2. **Draft.** Spawn one `researcher` per case, in parallel, in the background:
   *"Research the Stratum case `<id>` — <name>. Starter notes (may be wrong): <notes>.
   Write only catalog/cases/<id>.json."*
3. **Check.** When each finishes: `python3 scripts/validate.py` and
   `python3 scripts/check_sources.py <id>`.
4. **Review.** Spawn one `skeptic` per record: *"Review catalog/cases/<id>.json. The
   researcher flagged: <their 'check first' list>."*
5. **Revise.** Triage each `revise` verdict: apply mechanical fixes (a label, a year, a
   wording) directly; for substantive ones spawn a *fresh* researcher: *"Revise
   catalog/cases/<id>.json per catalog/reviews/<id>.json."* A fresh agent reads only the
   record and review; resuming the original reloads its whole large context (D13). For
   `fail`, redraft from scratch.
6. **Publish.** Set `review.stage` to `published` once issues are resolved (or recorded in
   `review.open_issues`), then:
   ```bash
   python3 scripts/fetch_plates.py      # licensed photographs
   python3 scripts/make_og.py           # link-preview cards with current numbers (needs Chrome)
   python3 scripts/build.py             # validate → database → analysis → site
   python3 -m http.server -d _site 8000 # look at it: http://localhost:8000
   ```
7. **Update the summary.** Edit `findings/summary.json` — the "What we’ve found so far"
   panel at the top of the home page: at most 7 items, most important first, plain numbers,
   each with a link and a tag (Lead, News, Pattern, Tentative, Null). Change `updated`. A big
   result also gets a dated bulletin in `findings/bulletins/` (then run `make_og.py`).
8. **Log and push.** Add a row to `logs/usage.md` (tokens and tool calls from the agents'
   completion notes), commit, `git push`. GitHub Actions rebuilds and deploys within a
   minute; check with `gh run list --limit 3`.
9. **Analyse.** After every ~10 reviewed records, spawn the `analyst` to update
   `findings/log.md`.

## Keep costs down

- Agents must use `scripts/lookup.py` (`doi`, `search`, `page --grep`, `commons`), never raw
  API dumps or whole PDFs. Everything an agent reads is re-read on every later step.
- Budgets: researcher ≈ 40 tool calls, skeptic ≈ 35. If an agent passes ~200k tokens without
  writing its file, message it to write up what it has.
- One case per agent. Small separate contexts cost less than one big one.
- Mechanical work belongs in scripts, which cost nothing to run.

## When the literature changes

A new paper can reopen a case (Monte Verde, 2026). Add it to the record's sources and
timeline, add the challenge as an objection (`unresolved`), update `status` and
`status_note` honestly, and let a skeptic review the change. Never delete history.

## Add a hypothesis

Append a new dated entry to `findings/log.md` in the same format, **before** looking at the
data that will test it, and push it. Never reword an existing hypothesis; if it was badly
posed, retire it with a dated note and register a better one.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Build fails | Run `python3 scripts/validate.py`; it names the record, field and problem. |
| "budget is N — shorten it" | The text exceeds its length budget. Shorten it; never raise the budget. |
| Site not updating | `gh run list --limit 3`; open the failed run with `gh run view <id> --log-failed`. |
| Certificate errors from Python | `scripts/net.py` falls back to curl automatically. |
| A Commons photo is refused | Its license does not clearly permit reuse; pick another. |
