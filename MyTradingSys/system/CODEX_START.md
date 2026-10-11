# CODEX START - first-message prompt for a Codex (GPT) builder session

Rules are not copied here: AGENTS.md -> CLAUDE.md is the single source; protocol is PARALLEL.md.
Codex is one more work-tree session. It meets Claude only through `origin/fast-track` (commits, claims, desk board, task cards).

## Before the first run (operator, once)
1. Do NOT open Codex in the live tree (`BinanceDataFeed`, marked by the gitignored `.mts_live`). `sync.py` refuses to run there.
2. In a terminal on the machine Codex runs on: `git fetch origin` then
   `git worktree add ../mts-codex -b <host>/codex-<slug> origin/fast-track` (host = jisnb, jisnuc or laptop; slug = the card).
3. In Codex: Add project -> that `../mts-codex` folder. New chat there, model GPT, approval mode "Ask for approval".
4. Paste the block below as the first message.

## Paste into Codex
```
You are an MTS builder session (surface COD, Codex). Read AGENTS.md (-> CLAUDE.md), then
MyTradingSys/research/STATUS.md, MyTradingSys/system/PARALLEL.md, MyTradingSys/system/NEXT_SESSION.md.
Follow the block in NEXT_SESSION.md steps 0-3 exactly, with these differences:
- Work only in this work tree. Never touch the live tree, live processes, HALT files, .secrets/ or .env. Testnet only.
- Take only Sonnet-tier cards (skip every OPUS card: Q4/Q5). Take the first Sonnet card that is not DONE and not claimed.
- Claim before working (`sync.py claim <slug>`); another session or the JIS-NB dispatcher cron may hold it.
- Commit trailer `MTS-Session: MTS-<UTC date>-<HHMMZ>-COD-BLD-<slug>` and a `Result:` line in the body.
- Provenance rule applies: every parameter needs the trader's own words (quote + file:line) or it is NO-SOURCE.
- Do not overwrite NEXT_SESSION.md unless its "End" step says so and no dispatcher run is active; report in the card
  (`tasks.py done <card> --result ...`) and the commit Result line instead.
One task per session. Stop after the task and give a one-line summary.
```

## When Claude hands Codex work (or back)
Commit to `origin/fast-track` (or a PR from a `claude/...` branch). Put the task on a card or NEXT_SESSION.md; a question for the operator = `Operator: <question>` in the commit body.
Read the other side's work with `python scripts/dev/sync.py news 24`.
