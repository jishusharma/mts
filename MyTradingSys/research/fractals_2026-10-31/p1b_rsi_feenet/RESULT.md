# P1b RESULT: RSI-DIV-MTF with the frozen 1R/2R/24-bar bracket and taker fees is NEGATIVE; no phase cell decides anything

**Verdict: honest negative. Pooled fee-net mean R = -0.229 (gross -0.100) on 640 DEV events; no cell has a positive CI; no PASS. Edge claimed: none. Taker fee only, no slippage or funding.**

Frozen in `PRE_REG.md` (commit db5a52697, before any outcome). 643 table rows, 3 NOT_IN_DATA dropped, 640 kept (502 1h, 138 4h). Exits: stop 67.0%, target 26.7%, time 6.2%. Bracket multiples 1R/2R are OURS; fee = fees.py BINANCE_TAKER per side.

| Slice | n | gross mean R | net mean R |
|---|---|---|---|
| pooled | 640 | -0.100 | -0.229 |
| 1h | 502 | -0.157 | -0.303 |
| 4h | 138 | +0.109 | +0.042 (n < 200, no verdict) |

Phase split (`split_cells.csv`; net R, block-bootstrap 95% CI, `p1_split.analyse`, shift test over each tag):

| Tag | Cell | n | net mean R | CI | Verdict |
|---|---|---|---|---|---|
| cowen_side | above | 340 | -0.294 | -0.431..-0.160 | FAIL (not flagged) |
| cowen_side | below | 283 | -0.150 | -0.296..-0.002 | FAIL |
| cowen_side | inside | 17 | -0.229 | -0.925..+0.608 | N_TOO_SMALL |
| sma200_side | above | 335 | -0.282 | -0.434..-0.137 | FAIL |
| sma200_side | below | 305 | -0.170 | -0.300..-0.029 | FAIL |
| wsma10_phase | above_down | 67 | -0.523 | -0.769..-0.289 | REPORT_ONLY |
| wsma10_phase | above_up | 260 | -0.293 | -0.428..-0.139 | FAIL |
| wsma10_phase | below_down | 241 | -0.059 | -0.248..+0.143 | FAIL |
| wsma10_phase | below_up | 72 | -0.291 | -0.617..+0.012 | REPORT_ONLY |
| placebo (week parity) | 0 / 1 | 319 / 321 | -0.222 / -0.235 | | not flagged (as required) |

No cell is flagged by the shift test: the phase tags do not separate the cells beyond chance. The loss is the whole list, not one phase. Cells with n >= 200 are decided (all FAIL); 30..199 reported only; < 30 too small.

Limits: the 1h and 4h events overlap in time (stated in the PRE_REG; calendar-day block bootstrap). Stop and target multiples were fixed, not tuned; any other bracket is a new PRE_REG and a new TRIALS row. The 4h gross is positive but n = 138 and it falls below the decide bar.
Files: `events_feenet.csv`, `build_feenet.py`, `test_build_feenet.py` (9 tests; mutating the fee count or the stop branch fails them), `run_split.py`, `split_cells.csv`.
