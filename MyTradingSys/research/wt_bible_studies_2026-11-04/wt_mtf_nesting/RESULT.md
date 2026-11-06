# RESULT: WT multi-timeframe cycle nesting (Card 2), DEV only, BTCUSDT, fee-net 0.14 %

Regime mix: 130 weeks: bull 16 (12%) | bear 0 (0%) | range 49 (38%) | n/a 65 (50%)  (n/a: weekly/monthly RSI history before 2022-01 is not on disk)

**VERDICT: FAIL** (frozen rule in PRE_REG.md: no TF has Holm p < 0.05 with nested minus rejected > 0; both TFs passed the power gate). VALIDATION not read, HOLDOUT never loaded. No result is a trading claim.

Primary read (nested trades vs the baseline dots the gate rejects), mean net bp-% is in percent per trade, day-block bootstrap 95 % CI, B=4000, Holm m=232:
| TF | n_nested | n_rejected | nested net % [CI] | rejected net % | diff % [CI] | raw p | Holm p |
|---|---|---|---|---|---|---|---|
| 5m | 544 | 2796 | -0.152 [-0.199, -0.104] | -0.132 | -0.020 [-0.072, +0.034] | 0.469 | 1.0 |
| 15m | 173 | 912 | -0.131 [-0.298, +0.025] | -0.152 | +0.021 [-0.150, +0.190] | 0.817 | 1.0 |

Baseline (all deduped dots): 5m n=3468 net -0.133 [-0.155,-0.112]; 15m n=1128 net -0.128 [-0.188,-0.069]. Every arm's net mean is negative except 15m age 0-0.5 (n=47, +0.072 [-0.309,+0.430]); no arm has Holm p < 1.

Controls (per-cell n, net [CI], diff vs complement, Holm p; all Holm p = 1.0; full table `dev_cells.csv`):
- 5m phase_only n=1735 -0.138 [-0.167,-0.108] diff -0.007; slope_only n=1622 -0.134 diff +0.003; age 0-0.5 n=182 -0.204 [-0.287,-0.130] diff -0.073 (raw p 0.066); age 0.5-1 n=245 -0.131; age >1 n=117 -0.115.
- 15m phase_only n=552 -0.119 diff +0.021; slope_only n=466 -0.155 diff -0.012; age 0-0.5 n=47 +0.072; age 0.5-1 n=84 -0.253 diff -0.113; age >1 n=42 -0.116.

Reading: the dot itself loses the 0.14 % cost at 12 bars (baseline net about -0.13 %), and the 30m phase and 4h slope gates do not separate winners from losers on DEV (5m diff within +-0.07, 15m CI +-0.17 around zero). Nesting is not shown to help; at 5m the nested trades are slightly worse. Median 30m cycle 43.5 h (161 cycles), counts in `counts.csv`, 4h slope unknown for the first ~33 days of 2022 (5m 128, 15m 43 dots excluded).
Limits: BTCUSDT only, DEV bars from 2022-01 only (no PRE_DEV warm-up), half the weeks have no regime tag, sd for the gate is OURS. Unseen confirmation target if anyone retries: a different instrument or a forward window, not VALIDATION BTCUSDT unless pre-registered fresh.
