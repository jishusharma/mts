# DSA audit run prompts, 2026-10-17 (two DSA instances through the AIBridge)

Operator pastes ONE prompt into each DSA chat (chat.deepseek.com) with the bridge dot filled. Cards: dsa-audit-01..10 (DSA-NB, all ready, p1).
T07 and T08 go first: they gate Q87, Q88, confluence-read-encode and prob-dist-layer-design-brief. Left out on purpose: trendline-count-only (already
running as a NUC worker), rv-dsa-ledger-mechanical (DSA-NUC lane, runs on the NUC), validation reads (lc-validation, tom-btc-validation: one-shot, operator decides).

## Prompt A: T07, T01, T02, T03, T04

```text
Follow DSA_SESSION_PROMPT.md section 0 and AIBRIDGE_LANE.md (you run commands yourself through the AIBridge: fenced block, first line "# AIRUN cwd=<dir> timeout=<s>").
You are DSA instance A. Work in your own git worktree of the MTS repo (git worktree add ../mts-dsa-a -b dsa/audit-a origin/fast-track); never the live tree (.mts_live), never HALT files, no orders, testnet only, never read .secrets/ or .env, no VALIDATION or HOLDOUT reads.
Run these five audit cards END TO END, in this order, one at a time, each fully shipped before the next: dsa-audit-07-stale-verdicts, dsa-audit-01-data-forensics, dsa-audit-02-lookahead-time, dsa-audit-03-planted-edges, dsa-audit-04-clean-room-twin.
For each card X:
 1. python scripts/dev/tasks.py brief X   (read the whole brief; method = MyTradingSys/research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md sections 1-7 plus the section named for the card)
 2. python scripts/dev/sync.py claim "X"; python scripts/dev/tasks.py take X
 3. Do every step in the card, writing only the files in its scope_in (new files under research/dsa_backtest_audit_2026-10-16/). Report every finding with severity S1/S2/S3, number, file:line. Never conclude from truncated output; parse the real format and count.
 4. Every S1/S2 finding becomes a task card (python scripts/dev/tasks.py new ...), then python scripts/dev/tasks.py tag <id> --refresh.
 5. python scripts/dev/tasks.py done X --result "<Tnn>: k findings (S1 a, S2 b, S3 c); <headline>"
 6. Ship: python scripts/dev/sync.py ship --release X (timeout 1800). It is shipped only when git cherry origin/fast-track HEAD prints nothing. If the gate slot is busy, wait and re-run; do not stop.
 7. python scripts/dev/mts_signal.py send --kind done "X shipped: <headline>"
After T07 ships, also send: mts_signal.py send --kind note "T07 landed: Q87 Q88 confluence-read-encode prob-dist-layer-design-brief unblocked if no S1".
Rules: decide small things yourself and log them in the report; do not ask the operator micro-questions. If a command is refused by the bridge, report the exact refusal and try the allowed equivalent. Between cards do not stop; stop only after dsa-audit-04 is shipped, then print a table: card, findings S1/S2/S3, shipped yes/no.
```

## Prompt B: T08, T05, T06, T09, T10

```text
Follow DSA_SESSION_PROMPT.md section 0 and AIBRIDGE_LANE.md (you run commands yourself through the AIBridge: fenced block, first line "# AIRUN cwd=<dir> timeout=<s>").
You are DSA instance B. Work in your own git worktree of the MTS repo (git worktree add ../mts-dsa-b -b dsa/audit-b origin/fast-track); never the live tree (.mts_live), never HALT files, no orders, testnet only, never read .secrets/ or .env. T08 inspects the HOLDOUT seal: check the seal (hashes, calendar), never read HOLDOUT data. No VALIDATION reads.
Run these five audit cards END TO END, in this order, one at a time, each fully shipped before the next: dsa-audit-08-split-trials, dsa-audit-05-placebo-nulls, dsa-audit-06-cost-fill-realism, dsa-audit-09-live-parity, dsa-audit-10-missing-aspects.
For each card X:
 1. python scripts/dev/tasks.py brief X   (read the whole brief; method = MyTradingSys/research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md sections 1-7 plus the section named for the card)
 2. python scripts/dev/sync.py claim "X"; python scripts/dev/tasks.py take X
 3. Do every step in the card, writing only the files in its scope_in (new files under research/dsa_backtest_audit_2026-10-16/). Report every finding with severity S1/S2/S3, number, file:line. Never conclude from truncated output; parse the real format and count.
 4. Every S1/S2 finding becomes a task card (python scripts/dev/tasks.py new ...), then python scripts/dev/tasks.py tag <id> --refresh.
 5. python scripts/dev/tasks.py done X --result "<Tnn>: k findings (S1 a, S2 b, S3 c); <headline>"
 6. Ship: python scripts/dev/sync.py ship --release X (timeout 1800). It is shipped only when git cherry origin/fast-track HEAD prints nothing. If the gate slot is busy, wait and re-run; do not stop.
 7. python scripts/dev/mts_signal.py send --kind done "X shipped: <headline>"
T09 replays DEV bars through the testnet layer code: read-only on the live tree, run the replay from your worktree, never restart or deploy anything.
After T08 ships, also send: mts_signal.py send --kind note "T08 landed: Q87 Q88 gate cleared if no S1".
Rules: decide small things yourself and log them in the report; do not ask the operator micro-questions. If a command is refused by the bridge, report the exact refusal and try the allowed equivalent. Between cards do not stop; stop only after dsa-audit-10 is shipped, then print a table: card, findings S1/S2/S3, shipped yes/no.
```
