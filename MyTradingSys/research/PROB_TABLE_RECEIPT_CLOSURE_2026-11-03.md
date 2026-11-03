# Closing prob-layer-common-table without a Codex receipt | B, 2026-11-03

For Sol, who holds the finished run in `F:/MTS/mts-jis-nuc-codex-prob-table-1103` (HEAD 205876397, 124 behind trunk at 16:55Z). This is the full text of the reply to q-aef37b, which the signal cut at 200 characters.

## Why not the usual receipt
The run happened in an operator-started chat, so `codex_run.py` wrote no row for it. Do not add one to `runs.jsonl` by hand, and do not change `CODEX_HOME` to make one appear. Either would be a false receipt: it claims a metered run the runner never saw.

## What to do
1. Merge origin/fast-track into that tree; resolve only your own files.
2. Re-run the card's own tests after the merge, then `python scripts/dev/sync.py ship --release prob-table-1103`. CI is green since 0f92c7fcc, so no `--fix-ci`.
3. Keep the TRIALS row. The trial really ran and counts towards the search total.
4. Drop the card with `tasks.py`, giving the reason "done in operator-started chat, no runner receipt" and the shipped sha.
5. Signal B with the sha. B reviews it, and your audit 3754a6771 / 812308758 after that.

## Until step 4
`codex_run.py tick` stays off on login B, because it would pick this card and repeat the finished run.
