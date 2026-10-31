# P1 RESULT: BLOCKED (no frozen per-event fee-net list for either layer)

**Verdict: no cell was run. Neither RSI-DIV-MTF nor Krown has a frozen DEV per-event fee-net R list on disk, so there is nothing to split without inventing an exit rule (= a new study). No edge claimed, none refuted.**

| Layer | Tag | n | fee-net mean R | CI | Verdict |
|---|---|---|---|---|---|
| RSI-DIV-MTF | cowen_side / sma200_side / wsma10_phase | - | - | - | BLOCKED |
| Krown | cowen_side / sma200_side / wsma10_phase | - | - | - | BLOCKED |

What exists (see PRE_REG.md section 0): RSI event table = 643 gross MFE/MAE events, no exit, no fees; RSI MTF study = aggregate 10-bar % returns, no list, window runs into holdout dates; Krown = "no DEV event study has run", only 6 Silver Cross events.

Shipped instead: `p1_split.py` (join of event day t to tag row t, block-bootstrap CI, `harness.shift_null_test`, placebo, year and episode rules) and `test_p1_split.py` (5 tests: tag of day t unchanged when bar t is altered but changed for t+1; DEV-only filter; planted +3 on 20% of one cell flagged alone; no-injection flags nothing; small cells not decided). Erratum to PRE_REG pass rule: "years" means years in which the cell has n >= 10.

To unblock: a frozen exit rule + fee model for RSI-DIV-MTF (e.g. the 24-bar ATR14 bracket already in event_table.py, pre-registered) or Krown S5/S8/S4 on 2022-01..2024-06; then run `p1_split.analyse` per tag. Even then expect n well under 200 per cell (643 RSI events over 3 tags x 2-4 states).
