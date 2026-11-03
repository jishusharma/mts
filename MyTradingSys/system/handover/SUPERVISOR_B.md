# Supervisor B handover | written 2026-11-03T16:58Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify

## Goal
Login B on JIS-NUC, super session on Opus (operator named it 2026-11-03). Operator cap for this run: stop new work at week 57%, hard stop 60% (read 55% at 16:54Z). Keep rolling, never end idle; work until 20:24Z or the cap.

## Truth
- CI green at 0f92c7fcc after 17 red runs (causes: bridge bump, tom-probe card path, test_fetch_captions whole-file skip, then ci_deps_lint on an unguarded yt_dlp import).
- Bridge 0.7.24 installed and running on JIS-NUC at 16:53Z; JIS-NB also 0.7.24.
- Released at 16:54Z to ship: Builder dsa-prompt-flow-1103 (aa7a5ec9a7270c3ab; prompt, paste, ci_fail.py, bridge 0.7.25), PASS guard (a983e04d58c59d1b9), Haiku (ae602911954025ea5).
- Codex: do NOT `codex_run.py tick` until prob-layer-common-table is dropped by Sol: see research/PROB_TABLE_RECEIPT_CLOSURE_2026-11-03.md.
- mts-audit-1103-independent-recheck: a Luna chat holds it; do not split or rerun.

## Ruled out
- runs.jsonl row or CODEX_HOME change to close the prob card: false receipt.
- `sync.py ci <sha>` as a CI verdict: it wrongly says no run exists (card sync-py-ci-falsely-says-no-ci-run-path-f).

## Next 3 steps
1. On each worker note: verify per roles/supervisor.md (ancestor of origin/fast-track, Result: line, one spot check).
2. DSA ship done: check the paste has the HOW YOU WORK section and a Prompt source line, install 0.7.25 when the bridge is idle, tell the operator to start a new DSA chat.
3. Ship Gemini sim-results-cards and krown branches from F:/MTS/gq; requeue STALE indian-fees and roadmap-review; then Fabio fix cards (fabio-v3-is-only-loads-oos-bars, fabio-l1-driver-reads-holdout).

## Traps
- A two-dot compare of a gq branch shows hundreds of files once trunk moves; use three dots.
- The Bash tool can fail on its cwd file after a tree is removed; use PowerShell.
- `tasks.py stale --refresh` touches all 13 stale cards: read first.
- A bridge agent restart kills the command DSA is running: wait for /ping running 0.

## Open
- Operator: arm DeepSeek hands-free on DSA-NB (oldest row 57 h).

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
