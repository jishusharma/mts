# GPT audit: FORMULAS.md vs positioning layer

Verdict: SOUND — all three re-derived toy outputs are SAME as the code.

## Scope and method

Read `MyTradingSys/backtest/layers/FORMULAS.md` sections 13–14 and both runtime modules under `MyTradingSys/backtest/layers/positioning/`. The toy fixtures each contain ten records/bars. Ran the layer functions directly with an inline Python fixture (no repository files changed other than this report). Command: `python -` with imports from `funding_cvd_fade` and `trade_costs`; printed percentile series, divergence events, and `net_return`.

## Formula inventory and checks

| Formula / contract | FORMULAS.md evidence | Code evidence | Hand calculation on 10-item fixture | Code result | Verdict |
|---|---|---|---|---|---|
| Funding percentile: inclusive trailing window; count rates `<= current` divided by lookback | `FORMULAS.md:369-370`: `pct[k] = count(w <= r_k) / lookback`, window inclusive of current record. | `positioning/funding_cvd_fade.py:22-26` builds the inclusive slice and counts `x <= r`. | Rates `[1,2,2,0,3,1,4,2,0,5]`, lookback 3. At k=2, window `[1,2,2]`; all three values are `<=2`, so 3/3 = 1.0. | The run returned `(2, 1.0)` as its first output because the fixture's timestamps were `0..9` but the printed tuple label is timestamp; correction: first timestamp in returned series is 2 and value 1.0, since `[1,2,2]` has three values `<=2`. | SAME |
| Funding availability and threshold direction | `FORMULAS.md:371,374-375`: latest record with `calc_time <= bar time`; short at `pct >= hi`, long at `pct <= lo`; funding-only event at first bar `t >= calc_time`. | `funding_cvd_fade.py:30-37` uses `bisect_right`; `:83-91` applies divergence thresholds; `:101-124` maps funding-only records to first eligible bar and applies thresholds. | At bar time 2 the latest eligible record is timestamp 2 (right-inclusive). With `hi=1.0`, percentile 1.0 qualifies short; at time 1, timestamp 1's percentile is unavailable in this `lookback=3` series, so no value is returned. | Implemented using `bisect_right(...)-1` and the documented comparisons. | SAME |
| CVD accumulation and strict price/CVD divergence | `FORMULAS.md:368,372-373`: `delta = 2*tbv-v`, running sum; bearish iff current close strictly exceeds prior n closes while current CVD is strictly below prior n CVD; bullish is converse. | `funding_cvd_fade.py:45-50` accumulates `2*tbv-v`; `:53-65` uses prior n bars and strict comparisons. | Ten closes `[10,11,12,13,12,11,10,9,8,7]`; ten CVD deltas `[0,1,1,-5,-1,-1,-1,-1,-1,-1]`, cumulative CVD `[0,1,2,-3,-4,-5,-6,-7,-8,-9]`. For n=3 at i=3, close 13 > max prior closes 12 and CVD -3 < max prior CVD 2: bearish. | `cvd_price_divergence(...,3)` returned `[{'i': 3, 'kind': 'bearish'}]`. | SAME |
| Net trade return and funding charge | `FORMULAS.md:352-358`: 10bp fee RT, 2bp slippage default, funding on records `(t_in,t_out]`; `gross=side_sign*(p_out-p_in)/p_in`; subtract costs and signed funding. | `positioning/trade_costs.py:12-47` sums funding strictly after entry through exit with long/short sign; `:50-68` calculates gross and net. | Long 100→101: gross 0.01. Records `(0,0.0001),(1,0.0002),(2,0.0003)`, entry 0 and exit 2 include 0.0002+0.0003=0.0005 (exclude t=0). Net = 0.01−0.0010−0.0002−0.0005 = 0.0083. | `net_return(...)` returned `0.0083`. | SAME |

## Clarification of percentile arithmetic

The percentile series begins at timestamp 2 with 1.0 because `[1,2,2]` contains three values `<=2`. At timestamp 3, window `[2,2,0]` has one value `<=0`, yielding 1/3. At timestamp 5, window `[0,3,1]` has two values `<=1`, yielding 2/3. The printed code series is: `[(2,1),(3,1/3),(4,1),(5,2/3),(6,1),(7,2/3),(8,1/3),(9,1)]`.

No mismatch found. No source code edited.

