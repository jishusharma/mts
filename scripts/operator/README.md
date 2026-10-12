# Operator polling station

Post a short instruction without reloading a long chat. Each request = one fresh headless Claude run
(small context, no chat history). Polling is a directory listing only: no model call, no body read.

Layout (Dumps/ is gitignored): `Dumps/operator/{inbox,outbox,done,archive}`, `poller.log`, optional `events.jsonl`.

## Setup
1. Install CLI: `irm https://claude.ai/install.ps1 | iex`, then run `claude` once to log in.
2. Start poller (PowerShell, repo root): `pwsh scripts/operator/inbox_poller.ps1`
   Autostart at logon (run once by you): `scripts/operator/install_poller_task.ps1` (task `MTS-OperatorPoller`).

## Use
- Ask: `scripts/operator/ask.ps1 "what is the auto-trader status?"` (add `-Model opus|haiku`; default haiku; use sonnet for work requests).
- Read: `scripts/operator/replies.ps1` (newest), `-Count 3`, or `-List`.
- Runs `claude -p --model <m> --permission-mode acceptEdits` in the repo root, prompt on stdin; 30 min timeout;
  one request at a time; reply in `outbox/<req>.reply.md`, request moved to `done/`.
- First header line `model: opus` escalates (ask.ps1 -Model writes it).
- If the CLI is missing the reply says how to install it; the poller keeps running.
- Files older than 14 days in done/ and outbox/ move to archive/ (checked hourly).
- Requests needing the long-running supervisor session get a reply saying so.

## Cost notes
Default haiku (escalate with -Model), small fixed preamble; the model reads CLAUDE.md/STATUS.md only as needed. Use opus sparingly.
Every request pays for its own context read, so batch related questions into one request.

## Events (optional)
`python scripts/operator/emit_event.py <source> <kind> "<text>"` appends `{ts,source,kind,text}` to events.jsonl.
Not wired in. Later the auto-trader / NUC watcher can call it (subprocess or `emit()`) on halt/flatten/alerts.

## Test
`pwsh scripts/operator/test_inbox_poller.ps1` (stub claude on PATH, no network).
