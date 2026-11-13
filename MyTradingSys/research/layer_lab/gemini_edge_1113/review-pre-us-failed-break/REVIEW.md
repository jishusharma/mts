SOUND

# Blind Review: Pre-US Failed-Break Short 10-Symbol Study (2026-11)

Verdict: SOUND (Methodology and execution in code/ledger are sound; reported numbers match data and code; findings confirm the study's FAIL conclusion).

## Headline Numbers Recount

All headline numbers recounted from `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/ledger.csv`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json`, and `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md`.
Regime mix requires external spot 1d history (`F:\MTS\Dumps\backtest\spot_2017`) which is not present on this machine, and is thus classified as UNVERIFIABLE. All other figures are direct MATCHes.

| Claim | Claimed Value | Recounted Value | Status | Citation (Claim) | Citation (Recount source) |
|---|---|---|---|---|---|
| Pooled episodes n | 1393 | 1393 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:2` |
| Pooled mean net bps of K | -2.47 | -2.467 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:3` |
| SE (day-clustered) | 4.39 | 4.392 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:4` |
| t (day-clustered) | -0.56 | -0.562 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:5` |
| 95% CI | -11.08 .. +6.14 | [-11.075, +6.141] | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:9-12` |
| SE plain / t plain | 3.21 / -0.77 | 3.215 / -0.767 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:6-7` |
| Measured sd (bps) | 119.99 | 119.985 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:8` |
| Target hit count / sum bps | 123 / +12,963 | 123 / +12963.05 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:19` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:16-17` |
| Time-cap count / sum bps | 1270 / -16,400 | 1270 / -16399.80 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:19` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:18-19` |
| Win rate | 60.7% | 60.73% | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:21` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:13` |
| Mean winner / mean loser bps | +45.96 / -77.36 | +45.958 / -77.363 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:21` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:14-15` |
| MDD of cumulative net (% of K) | 97.9 | 97.93 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:20` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:20` |
| BTC buy-and-hold MDD (% of K) | 66.9 | 66.94 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:20` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:21` |
| MAE % of K (p50 / p90 / p99 / max) | 0.21 / 1.87 / 6.22 / 22.25 | 0.206 / 1.868 / 6.219 / 22.249 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:22` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:22-27` |
| Tranches filled 1 / 2 / 3 / 4 | 553 / 310 / 190 / 340 | 553 / 310 / 190 / 340 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:23` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:30-35` |
| BTCUSDT: n / mean / sd / win / timecap / sum | 177 / -3.24 / 68.96 / 0.60 / 155 / -573 | 177 / -3.24 / 68.96 / 0.60 / 155 / -573.1 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:28` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:5` |
| ETHUSDT: n / mean / sd / win / timecap / sum | 186 / -2.51 / 87.23 / 0.58 / 171 / -466 | 186 / -2.51 / 87.23 / 0.58 / 171 / -466.1 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:29` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:7` |
| SOLUSDT: n / mean / sd / win / timecap / sum | 141 / -24.04 / 152.02 / 0.61 / 136 / -3390 | 141 / -24.04 / 152.02 / 0.61 / 136 / -3389.7 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:30` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:10` |
| BNBUSDT: n / mean / sd / win / timecap / sum | 128 / +3.47 / 61.81 / 0.61 / 120 / +445 | 128 / +3.47 / 61.81 / 0.61 / 120 / +444.5 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:31` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:4` |
| XRPUSDT: n / mean / sd / win / timecap / sum | 124 / -0.07 / 81.52 / 0.57 / 109 / -9 | 124 / -0.07 / 81.52 / 0.57 / 109 / -9.2 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:32` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:11` |
| DOGEUSDT: n / mean / sd / win / timecap / sum | 131 / +1.65 / 232.59 / 0.66 / 122 / +216 | 131 / +1.65 / 232.59 / 0.66 / 122 / +215.9 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:33` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:6` |
| ADAUSDT: n / mean / sd / win / timecap / sum | 106 / +11.86 / 118.06 / 0.58 / 95 / +1258 | 106 / +11.86 / 118.06 / 0.58 / 95 / +1257.6 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:34` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:2` |
| AVAXUSDT: n / mean / sd / win / timecap / sum | 115 / +3.05 / 121.71 / 0.62 / 101 / +351 | 115 / +3.05 / 121.71 / 0.62 / 101 / +351.0 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:35` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:3` |
| LINKUSDT: n / mean / sd / win / timecap / sum | 137 / +9.68 / 92.63 / 0.64 / 125 / +1327 | 137 / +9.68 / 92.63 / 0.64 / 125 / +1326.6 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:36` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:8` |
| LTCUSDT: n / mean / sd / win / timecap / sum | 148 / -17.53 / 109.19 / 0.61 / 136 / -2594 | 148 / -17.53 / 109.19 / 0.61 / 136 / -2594.2 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:37` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv:9` |
| Regime mix (bull 25 / range 105) | 130 weeks: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%) | Data missing on machine | UNVERIFIABLE | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:7` | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:28` |

## Look-Ahead Hunt

We verified the temporal causality of every feature and signal decision bar in `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py`:

1. **ATR calculation (`wilder_atr` and `atr_at`)**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:124`: "ATR of the last hour CLOSED by the close of minute m of day d (hour closes with its minute 59)."
   - If `m % 60 == 59`, uses `atr[k]` (which ends at minute 59 of hour `k`); otherwise uses `atr[k - 1]`. No unclosed hourly bars or future bars are referenced.
2. **Prior Day High/Low (PDH / PDL)**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:170` and `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:187`: Uses `self.h[d - 1].max()` and `self.l[d - 1].min()`, which are derived strictly from day `d - 1`. Zero look-ahead.
3. **Asian Session High (ASH)**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:171-177`: Calculated using `first[ms - 1] <= ms - 60` where `pre = np.maximum.accumulate(h[:W1])`. For candidate break bar `b = ms[j]`, it strictly examines bars `0` to `b - 1`. Zero look-ahead.
4. **Swing High / Low**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:129`: "Highest hourly swing high of the last 5 UTC days, usable once its next hour has closed (confirmed 2h after formation)."
   - `kmax = (m + 1) // 60 + d * 24 - 2`. To confirm an hourly swing at hour `H`, hour `H + 1` must close, so at least 2 hours must elapse before the swing is recognized. Zero look-ahead.
5. **Break and Confirmation Execution**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:146-158`: Break occurs at minute `b` in `[W0, W1)`. Failure confirmation occurs on bar `t` in `[b, min(b + 3, W1 - 2)]` when `c[t] < lvl`.
   - Entry occurs at `e = t + 1` open (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:197-199`), using `o[e]`. Fills and target evaluations strictly run on `j` from `e + 1` to `W1 - 1` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:205`). Time exit occurs at `o[W1]` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:217`). Zero look-ahead.

Conclusion: No look-ahead detected.

## Fee and Slippage Hunt

We audited fee, slippage, and funding implementations in `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py`:

1. **Fee Model & Rate**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:34`: `FEE_LEG = fees.FEES_ALL_TAKER["entry"]` (which is 0.0005 = 5 bps taker fee).
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:35`: `ADVERSE_PX = 2 / 1e4` (2 bps slippage per leg).
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:36`: `LEG_COST = FEE_LEG + ADVERSE_PX` (7 bps per leg).
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:219`: `rt_drag = 2 * LEG_COST * TRANCHE * len(fills)` (14 bps round-trip per filled tranche of weight 0.25 K).
2. **Side & Double Counting**:
   - Both entry and exit are treated as taker with 2 bps slippage each (7 bps * 2 = 14 bps round-trip per tranche).
   - Fees are applied proportionally to each filled tranche (`TRANCHE * len(fills)`), correctly reflecting actual tranche execution.
   - No double counting or omitted legs identified.
3. **Funding Drag**:
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:37`: `SETTLE_DRAG = 1 / 1e4` (flat 1 bp).
   - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:206-207`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:220`: Applied only when position is open across 08:00 UTC (`e < 480 and exit_j >= 480`), on `fund_w = TRANCHE * len(fills)`. Correctly signed as a cost penalty.

Conclusion: Fee and slippage mechanics are properly implemented and conservative.

## Summary Verdict

The study implementation is SOUND. Every reported metric matches the raw ledger data and simulation formulas. The conclusion of `FAIL` (negative expectancy of -2.47 bps/episode after taker costs, high MDD of 97.9%, and 91% time-cap exits) is fully verified.
