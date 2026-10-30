# B208 - Eagle_Eyes does not get smarter with use: lessons, habits and call results live in one chat and an append-only

Filed: 2026-10-27
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B208 | 2026-10-27 | OPEN | HIGH | Eagle_Eyes does not get smarter with use: lessons, habits and call results live in one chat and an append-only log that nothing reads back. MUST CHANGE (1) a calls ledger, one row per call (time, call, level, cancel rule, outcome HIT/MISS/OPEN) written when the call is made and scored from klines or watch_rows.csv by a script at day end; (2) a RULES block in roles/eagle_eyes.md (or rules.md next to it) with at most 15 one-line rules, each with source and date, e.g. cancel a break only on a 5m close above the line, RSI means Malkan 40-60, report only flips; a session adds a rule the first time the operator or a miss corrects it, and ships it the same turn; (3) a pre-assert check: before stating a level or a no-close claim, the session reads the last klines (a one-line helper), because two false statements came from memory; (4) the role hook injects RULES and the last 10 ledger rows at start and after each compaction, so a new or compacted session starts with them; (5) a weekly hit-rate line per call type so the operator sees whether it is improving. Not a new gate: the ledger is written by the same script that logs the call. Proofs: B208_proofs.md. | MyTradingSys/research/live_reads/2026-10-26_cross_market_tools/B208_proofs.md: role file has no lesson text (69 lines), same cancel mistake 3x (03:30Z, 05:00Z, 06:10Z), lesson only in READ.md line 154, 893 scoreable rows unused, 2 false claims found by the operator | |
