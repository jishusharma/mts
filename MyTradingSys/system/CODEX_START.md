# CODEX START - first-message prompt for a Codex (GPT) builder session

Rules are not copied here: AGENTS.md -> CLAUDE.md is the single source (Claude-only parts do not apply to Codex: screenshots, Control Room pages, DSA posting); protocol is PARALLEL.md.
Codex is one more work-tree session. It meets Claude only through `origin/fast-track` (commits, claims, task cards, desk board).
**Codex takes lane `CODEX` cards only** (layer lab: audits, backtest runs, builds; unattended runner and plan/allowance: `LAYER_LAB.md`). Machines and logins: `HOW_MTS_RUNS.md`.

## Zero-conflict rules (all already in PARALLEL.md; Codex adds none)
1. Own checkout: a work tree, never the live tree (`BinanceDataFeed` on JIS-NB, marked `.mts_live`). Never add that folder as a Codex project.
2. Own branch prefix `<host>/codex-<slug>`; shares work only by `sync.py ship` (merge, never rebase or force-push).
3. The claim is the lock: `sync.py claim "<task>"` before work, `sync.py ship --release <slug>` after. Take no card another session holds.
4. Codex does not touch `NEXT_SESSION.md`, the relay scripts or the relay scripts (no scheduled tasks or dispatcher run: RETIRED 2026-10-17, see SCHEDULING_POLICY.md). It works cards one at a time.
5. Codex never restarts processes, touches HALT files, opens trades, or reads `.secrets/` / `.env`. Testnet only.
Cards that need `OPUS` (they need `approved_by`) stay with Claude; Claude refines cards and spot-checks one claim per Codex report. CI gates Codex code exactly like Claude code.
Data-bound cards (1m klines, DAX archive, videos live on JIS-NB disks; the NUC copy is listed in LAYER_LAB.md): from another machine post a desk task
(`desk.py post ... --target JIS-NB`) instead of guessing. `F:\MTS` on JIS-NB and JIS-NUC are different disks.

## Where to install (operator choice; recommendation: JIS-NUC)
- JIS-NUC: no live tree, no operator screen. Codex app project folder `F:\MTS\mts-codex` (a work tree); the unattended lab runs in `F:\MTS\mts-codex-lab` (LAYER_LAB.md). `F:\MTS\repo` there is not a git repo. Lacks the 1m klines.
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
1. `python scripts/dev/tasks.py next --lane CODEX`: take the first ready card nobody has claimed.
   `tasks.py brief <card>` is the whole task. `sync.py claim "<card>"`, work, tests (new test red before the fix), `tasks.py done <card> --result "<number/file>"`.
2. `sync.py ship --release <slug>`, `sync.py where` clean.
Commit trailer `MTS-Session: MTS-<UTC date>-<HHMMZ>-COD-BLD-<slug>`, body line `Result: <what works now / the number>`.
Provenance rule applies: label every parameter SOURCED (trader's quote + file:line) or OURS (CLAUDE.md Hard rules).
Skip OPUS cards; do not touch NEXT_SESSION.md or the relay. One card per session, then stop with a one-line summary.
```

## Pack file bridge (operator 2026-10-11; merged here from CODEX_BRIDGE.md)
Codex and Claude share ONE repo and never share a folder.
- Codex cannot see claude.ai chats, artifacts (Control Room), App session history or `~/.claude`; do not import them wholesale.
- It can see git (`origin/fast-track`), task cards, `sync.py news`, and a **pack file** outside the repo.
- `python scripts/dev/codex_pack.py <card-id> [--chat exported.md]` writes `%CODEX_HOME%\packs\<card>.md` (brief, STATUS head, lessons digest, scope_in files).
  It refuses any path inside the project, so nothing clutters the repo. Chats worth keeping: export the transcript (App: session menu, or `export_transcript`),
  pass `--chat`; it lands in `%CODEX_HOME%\packs\chats\` as reference, never as instructions. Artifact content (Control Room decisions) goes the same way: paste or export to a file, `--chat`.
- Results return only through the card flow: `tasks.py done`, `sync.py ship` (Codex trailer `MTS-Session: ...-COD-BLD-<slug>`).

## When Claude hands Codex work (or back)
Put the task on a card (`tasks.py new`, lane CODEX, `kind`) and ship it to `origin/fast-track`; a question for the operator = `Operator: <question>` in the commit body.
Read the other side's work with `python scripts/dev/sync.py news 24`.
