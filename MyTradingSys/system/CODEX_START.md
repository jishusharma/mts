# CODEX START - first-message prompt for a Codex (GPT) builder session

Rules are not copied here: AGENTS.md -> CLAUDE.md is the single source; protocol is PARALLEL.md.
Codex is one more work-tree session. It meets Claude only through `origin/fast-track` (commits, claims, task cards, desk board).

## Zero-conflict rules (all already in PARALLEL.md; Codex adds none)
1. Own checkout: a work tree, never the live tree (`BinanceDataFeed` on JIS-NB, marked `.mts_live`). Never add that folder as a Codex project.
2. Own branch prefix `<host>/codex-<slug>`; shares work only by `sync.py ship` (merge, never rebase or force-push).
3. The claim is the lock: `sync.py claim "<task>"` before work, `sync.py release` after. Take no card another session holds.
4. Codex does not touch `NEXT_SESSION.md`, the relay scripts or the Claude scheduled tasks (`mts-relay-*`, dispatcher). It works cards one at a time.
5. Codex never restarts processes, touches HALT files, opens trades, or reads `.secrets/` / `.env`. Testnet only.

## Routing (who takes which card; no code change needed)
- Since 2026-10-12 Codex's own queue is lane `CODEX` (layer lab: audits, backtest runs, builds for the Tom/Fabio layers), fired
  unattended by `scripts/dev/codex_run.py`: see `LAYER_LAB.md`. The lines below still hold for a hand-started app session.
- Card lanes: `python scripts/dev/tasks.py next --lane SONNET` (and HAIKU). Codex takes these. That is the cheap tier.
- `OPUS` cards (need `approved_by`) and anything the operator names Opus stay with Claude. Codex skips them.
- Opus (Claude) is the guide: it writes and refines cards, owns the OPUS lane, and spot-checks one claim per Codex report
  (CLAUDE.md work routing). CI runs the full gate on every push, so Codex code is gated exactly like Claude code.
- Data-bound cards (1m klines, DAX archive, videos live on JIS-NB disks): from another machine post a desk task
  (`desk.py post ... --target JIS-NB`) instead of guessing. `F:\MTS` on JIS-NB and JIS-NUC are different disks.

## Who does what (three lanes; Cloud credits are the free budget, so Cloud takes what only needs the repo)
| Lane | Takes | Why |
|---|---|---|
| CLD (claude.ai/code, session credits, SURFACE_POLICY section 1) | offline research and extraction, specs and card writing, adversarial reviews of Codex/Claude commits, docs, backtests on committed data, OPUS-lane thinking when the operator names Opus | needs only pushed git refs; credits ($100 pool, expires 2026-11-05) are use-it-or-lose-it |
| COD on JIS-NUC (Codex trial, 1 month) | Sonnet/Haiku-lane code cards with fail-first tests, NUC-side runs (raw_1h/1d/funding data), refactors, test writing | cheap tier; no live tree; trial runs out, so start now |
| JIS-NB (App session, relay) | live path, deploy, 1m-kline and video-bound cards, desk tasks, supervisor decisions | only machine with that data and the live tree |
Rules of thumb: a card that needs no gitignored file and no live reach goes to CLD first; Codex gets code that must be built and run against NUC data; nothing crosses lanes without a card and a claim. Cloud sessions ship by PR into fast-track (CI auto-merges on green).

## Where to install (operator choice; recommendation: JIS-NUC)
- JIS-NUC: no live tree, no operator screen, repo copy at `F:\MTS\repo`. Zero chance of touching the live system. Lacks the 1m klines.
- JIS-NB: has the data, but also the live loop and the operator's screen; use only with the work tree on F: and no background windows.
- Either way install on F: or D: and point Codex's data folder there (CODEX_HOME for the CLI; check the app's settings for its storage path) so C: stays clean.
- Setup: `git fetch origin`, then `git worktree add F:\MTS\mts-codex -b <host>/codex-<slug> origin/fast-track`
  (or a plain `git clone` on the NUC, then `git switch -c nuc/codex-<slug> origin/fast-track`).
  In Codex: Add project -> that folder, approval mode "Ask for approval", then paste the block below.

## Paste into Codex
```
You are an MTS builder session (surface COD, Codex). Read AGENTS.md (-> CLAUDE.md), then
MyTradingSys/research/STATUS.md, MyTradingSys/system/PARALLEL.md, MyTradingSys/system/CODEX_START.md.
0. `python scripts/dev/sync.py start`, `sync.py where`. Push fails: say so in one line, stop.
1. `python scripts/dev/tasks.py next --lane SONNET`: take the first ready card nobody has claimed.
   `tasks.py brief <card>` is the whole task. `sync.py claim "<card>"`, work, tests (new test red before the fix), `tasks.py done <card> --result "<number/file>"`.
2. `sync.py ship`, `sync.py release <slug>`, `sync.py where` clean.
Commit trailer `MTS-Session: MTS-<UTC date>-<HHMMZ>-COD-BLD-<slug>`, body line `Result: <what works now / the number>`.
Provenance rule applies: every parameter needs the trader's own words (quote + file:line) or it is NO-SOURCE.
Skip OPUS cards; do not touch NEXT_SESSION.md or the relay. One card per session, then stop with a one-line summary.
```

## When Claude hands Codex work (or back)
Put the task on a card (`tasks.py new`, lane SONNET) and ship it to `origin/fast-track`; a question for the operator = `Operator: <question>` in the commit body.
Read the other side's work with `python scripts/dev/sync.py news 24`.
