# Layer Lab Report: `gemini-blind-read-bb-range-retest-1104`

- **Card**: `gemini-blind-read-bb-range-retest-1104` (`OURS`)
- **Date**: 2026-11-04 UTC (`OURS`)
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/bb_range_retest_blind_read.md` (`OURS`)
- **Headline Counts**: `FOUND: 52 | DIFF: 0 | NOT_IN_DATA: 0` (`OURS`)

## Findings

1. **Exact Reproduction of All 52 Quoted Numbers (`FOUND: 52, DIFF: 0, NOT_IN_DATA: 0`)**:
   - Audited every quantitative claim in `MyTradingSys/research/bb_range_retest_2026-11-04/RESULT.md:1-45` line by line against committed research outputs: `counts.csv`, `dev_cells.csv`, `BLOCKED.md`, `regime_mix_count.txt`, `dev_survivors.json`, `test_level_arm.py`, and the comparison files in `bb_range_to_range_2026-11-04/`.
   - Table 1 fill rates (15m, range, session-range tagged): all 15 cells across all sessions (63%, 66%, 68%), asia (62%, 65%, 68%), london (67%, 69%, 72%), ny (59%, 61%, 64%), and late (68%, 72%, 74%) match `counts.csv:2-254`.
   - Confirmatory family table (Holm $m=9$, sides pooled): all 9 rows for asia, london, and ny at $k \in \{0.25, 0.5, 1.0\}$ match $n$, active days, gross %, net % with 95% CI, target hit %, Holm $p$, and $t$-statistic versus ungated tagged in `dev_cells.csv:20-236`.
   - Pre-return counts: re-entered count 824 of 1187 (69.4%), touch rate of k-ATR limit (91.3% to 98.7%), and untagged range fill rate at $k=0.5$ (74.55% $\approx$ 75%) match `counts.csv:2,92,95,182`.
   - Comparison and power numbers: 146-186 days per cell vs 478-1783 needed match `BLOCKED.md:3-11`; 0 of 9 survivors match `dev_survivors.json`; previous arm numbers ($n=4256$, 99.9% fill, net -0.130% and -0.123%) match `bb_range_to_range_2026-11-04/dev_cells.csv` and `counts.csv`.
   - Wiring tests: verified `test_level_arm.py` executes and passes all 5 tests cleanly (`pytest MyTradingSys/research/bb_range_retest_2026-11-04/test_level_arm.py` -> 5 passed).
