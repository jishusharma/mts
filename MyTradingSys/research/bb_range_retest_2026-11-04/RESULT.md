Regime mix: 130 weeks DEV: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
Verdict: INCONCLUSIVE (underpowered), not FAIL: prereg_gate BLOCKs all 9 family cells (BLOCKED.md: 146-186 days per cell against 478-1783 needed), so no FAIL is available. 0 of 9 cells survive (dev_survivors.json is []); every cell has net below zero (-0.07 to -0.20 % per trade) and none has a Holm p below 0.17. VALIDATION not read (no DEV survivor); HOLDOUT never loaded. This says nothing about other exits, other band settings, maker cost, other symbols, a bear regime (none in this DEV window) or the trader's discretionary read.

# bb_range_retest_2026-11-04 result (DEV 2022-01-01..2024-06-30, fee-net 0.14 %, PRE_REG.md frozen first, commit 53bdf1f2a)

The earlier FAIL (bb_range_to_range_2026-11-04) was partly an encoding failure: its "retest" filled 99.9 % of signals, i.e. the next open. This arm is a real return-to-the-band entry and is valid: 59-74 % of tagged signals fill (the rest never close back inside the band, or never pull back to level +- k ATR). It does not change the answer: gross is about +0.03 % (zero within noise), the move to the opposite band completes in 14-29 % of trades, and the 0.14 % round trip leaves net negative.

Fill rate (fills / signals; the earlier study: 4256 of 4260 = 99.9 %):

| 15m, range, session-range tagged | k = 0.25 | k = 0.5 | k = 1.0 |
|---|---|---|---|
| all sessions | 752 / 1187 = 63 % | 785 / 1187 = 66 % | 813 / 1187 = 68 % |
| asia | 62 % | 65 % | 68 % |
| london | 67 % | 69 % | 72 % |
| ny | 59 % | 61 % | 64 % |
| late (descriptive) | 68 % | 72 % | 74 % |

Of the signals, 824 of 1187 (69 %) close back inside the band within 10 bars; 91-99 % of those then touch the k-ATR limit. Untagged range signals fill 75 % at k = 0.5.

Confirmatory family (15m, range gate, tagged, sides pooled; Holm m = 9; net = gross - 0.14 %, day-clustered 95 % CI):

| session | k (ATR) | n | days | gross % | net % [95 % CI] | target hit | Holm p | tagged range minus all-regime tagged (t) |
|---|---|---|---|---|---|---|---|---|
| asia | 0.25 | 225 | 176 | +0.046 | -0.094 [-0.240, +0.052] | 16 % | 0.89 | -0.1 |
| asia | 0.5 | 235 | 182 | +0.035 | -0.105 [-0.248, +0.037] | 16 % | 0.89 | -0.3 |
| asia | 1.0 | 244 | 186 | +0.008 | -0.132 [-0.270, +0.007] | 14 % | 0.44 | -0.6 |
| london | 0.25 | 175 | 146 | +0.007 | -0.133 [-0.321, +0.054] | 29 % | 0.89 | 0.7 |
| london | 0.5 | 180 | 149 | -0.035 | -0.175 [-0.350, 0.000] | 28 % | 0.40 | 0.7 |
| london | 1.0 | 186 | 155 | -0.061 | -0.201 [-0.369, -0.033] | 28 % | 0.17 | 0.8 |
| ny | 0.25 | 215 | 162 | +0.022 | -0.118 [-0.305, +0.068] | 16 % | 0.89 | 0.4 |
| ny | 0.5 | 224 | 169 | +0.057 | -0.083 [-0.268, +0.101] | 17 % | 0.89 | 0.3 |
| ny | 1.0 | 233 | 174 | +0.067 | -0.073 [-0.253, +0.108] | 17 % | 0.89 | 0.4 |

- The session-range tag (OURS; no transcript line for Tom or the trader was found, so it is not attributed to them) does nothing measurable: tagged range net -0.108 % [-0.195, -0.022] vs untagged range -0.115 % [-0.140, -0.091] (k = 0.5, all sessions); the tagged-minus-untagged t values are -0.7 to 0.5 in every cell.
- The range gate does nothing, as before (81 % of DEV weeks are range): tagged range net -0.108 vs tagged all-regime -0.118; every vs-ungated t is 0.8 or less in absolute value.
- Sides (tagged range, k = 0.5, all sessions): long net -0.128 % [-0.258, +0.002] (n 427), short -0.085 % [-0.189, +0.019] (n 358).
- The CIs are wide (about +-0.15 %); a gross edge of 0.12-0.15 % per trade is NOT excluded, so this is INCONCLUSIVE and not a disproof. Compare the earlier concept-only rows, which were powered and negative.

Concept-only comparison row (bb_range_to_range_2026-11-04, 15m range, all sessions, not re-run; copied from its dev_cells.csv): signal entry n 4256, net -0.130 % [-0.161, -0.099], target hit 22 %; its "retest" entry n 4256 (fill 99.9 %), net -0.123 % [-0.155, -0.092], hit 23 %. The level arm (tagged, k = 0.5) is -0.108 % [-0.195, -0.022]: the same sign and size, with a wider CI.

Not a PASS; no replay needed (no survivor). Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, tagged-range minus tagged-all-regime t >= 2): 0 survivors.

Parameter labels: BB(20,2), M = 10, N = 10, k grid {0.25, 0.5, 1.0}, ATR(14), stop 0.5 x distance, 24-bar time-out, session-range tag (20 prior same-name sessions, >= 10, strict above median) all OURS; range regime band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo; session cutoffs OURS (research_kit); cost 0.14 % SOURCED research_kit.

Files: PRE_REG.md, BLOCKED.md, counts.csv (pre-return counts and fill rates), dev_cells.csv (gate x tag x side x session x k), dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, study.py, test_level_arm.py (5 tests; all 5 failed on the pre-change stub with NotImplementedError at study.py:17, then 5 passed). Data: BTCUSDT 1m from F:/MTS/Dumps/backtest, loaded only to 2024-07-01.
