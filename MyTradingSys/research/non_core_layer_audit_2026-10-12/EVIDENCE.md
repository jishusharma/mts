# Evidence attachment - independent layer audit

Captured source files with exact line numbers and SHA-256 hashes of original bytes. Trailing whitespace is omitted from displayed lines. Historical documents are evidence of what was reported, not fresh market-data reproductions. Full source snapshots below allow cloud review without local file access.

## E01

### MyTradingSys/backtest/layers/rsi/rsi_core.py

SHA-256: `05d5cd42a9f7f179011c2ebb1f4a57499b677710edbd8759db21de68e7e8b762`

```text
1: """
2: The ONLY Wilder RSI implementation any other MTS layer or consumer may import.
3: D2 isolation rule: the 40/60 numbers are private to malkan_40_60. No other module imports them.
4: """
5: from typing import List, Optional
6:
7: def rsi_core(closes: List[float], period: int = 14) -> List[Optional[float]]:
8:     """
9:     Wilder RSI: returns a list the same length as `closes`; entries before index `period` are `None`.
10:     Seed `avg_gain`/`avg_loss` from the mean of the positive/negative deltas among the first `period` bar-to-bar changes (0.0 if there are none of one sign).
11:     RSI at index `period`: if `avg_loss == 0`, `50.0` if `avg_gain == 0` else `100.0`; otherwise `100 - 100/(1 + avg_gain/avg_loss)`.
12:     For `i > period`: Wilder-smooth `avg_gain = (avg_gain*(period-1) + gain)/period`, `avg_loss = (avg_loss*(period-1) + loss)/period` where `gain = max(0, closes[i]-closes[i-1])`, `loss = max(0, closes[i-1]-closes[i])`, then the same RSI formula.
13:     Raise `ValueError` if `period < 1` or `len(closes) <= period`.
14:     """
15:     if period < 1:
16:         raise ValueError("Period must be >= 1")
17:     if len(closes) <= period:
18:         raise ValueError("Not enough data points for the given period")
19:
20:     result = [None] * len(closes)
21:
22:     # Compute deltas
23:     deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
24:
25:     # Seed values from first period
26:     gains = [max(0.0, delta) for delta in deltas[:period]]
27:     losses = [max(0.0, -delta) for delta in deltas[:period]]
28:
29:     avg_gain = sum(gains) / period
30:     avg_loss = sum(losses) / period
31:
32:     # Handle case where avg_loss is 0
33:     if avg_loss == 0:
34:         rsi_val = 100.0 if avg_gain > 0 else 50.0
35:     else:
36:         rs = avg_gain / avg_loss
37:         rsi_val = 100 - 100 / (1 + rs)
38:
39:     result[period] = rsi_val
40:
41:     # Recursive smoothing for subsequent values
42:     for i in range(period + 1, len(closes)):
43:         gain = max(0.0, closes[i] - closes[i-1])
44:         loss = max(0.0, closes[i-1] - closes[i])
45:
46:         avg_gain = (avg_gain * (period - 1) + gain) / period
47:         avg_loss = (avg_loss * (period - 1) + loss) / period
48:
49:         if avg_loss == 0:
50:             rsi_val = 100.0 if avg_gain > 0 else 50.0
51:         else:
52:             rs = avg_gain / avg_loss
53:             rsi_val = 100 - 100 / (1 + rs)
54:
55:         result[i] = rsi_val
56:
57:     return result
```

### MyTradingSys/backtest/layers/FORMULAS.md

SHA-256: `8aa03d2d19fb0722bfbde9c116a84ed21d5f248fae59e2d5f103363fa524ecd2`

```text
1: # FORMULAS.md — canonical formula definitions for the indicator layers
2:
3: Purpose: every formula used by `layers/rsi`, `layers/timeframe`, `layers/cryptocred` and
4: `layers/runner.py` (plus the `bt/bt_stats.py` / `bt/ref_pbo.py` metrics used to score them) gets ONE
5: chosen definition here, its canonical source, the known variants and why we picked ours, and a tiny
6: worked example. Every TEST_PLAN.md in these layers must derive its expected numbers from this file,
7: never from an implementation module (see LESSONS_LEARNED.md 2026-09-28 D1: `layers/rsi/TEST_PLAN.md`
8: Case C1 was originally derived from `bt/bt_rsi.py.new`'s `rsi_wilder`, which is off vs textbook Wilder).
9:
10: ## 1. RSI (Wilder, `rsi_core.rsi_wilder`)
11:
12: **Chosen definition (textbook Wilder = TradingView `ta.rsi`):**
13: 1. `delta[i] = close[i] - close[i-1]` for `i = 1..len-1`.
14: 2. Seed at index `period`: `avg_gain = mean(max(delta,0) for delta in delta[0:period])`,
15:    `avg_loss = mean(max(-delta,0) for delta in delta[0:period])` (a plain SMA seed over the first
16:    `period` deltas — NOT the first `period` closes).
17: 3. Wilder-smooth every index after the seed: `avg_gain = (avg_gain*(period-1) + gain[i]) / period`,
18:    `avg_loss = (avg_loss*(period-1) + loss[i]) / period`, where `gain[i]=max(delta[i],0)`,
19:    `loss[i]=max(-delta[i],0)`.
20: 4. `rs = avg_gain / avg_loss`; `rsi = 100 - 100/(1+rs)`. If `avg_loss == 0`: `rsi = 100` when
21:    `avg_gain > 0`, else `rsi = 50` (flat series, no gains or losses at all).
22:    DELIBERATE DEVIATION (supervisor 2026-09-28): TradingView's ta.rsi returns 100 whenever down == 0,
23:    including a flat series. We return 50 for flat (neutral, no momentum). Only reachable on a perfectly
24:    flat window; any cross-check vs TradingView must skip that case.
25: 5. Indices `0..period-1` are `None` (not enough data for a seed).
26:
27: **Canonical source:** J. Welles Wilder, *New Concepts in Technical Trading Systems* (Trend Research,
28: 1978) — RSI = 100 - 100/(1+RS), RS = avg gain / avg loss over the period, subsequently smoothed with
29: Wilder's own recursive average (equivalent to an EMA with `alpha = 1/period`, i.e. `N = 2*period-1` in
30: plain-EMA terms). Cross-checked against TradingView's Pine v5/v6 reference: `ta.rsi(source, length)` is
31: documented as `up = ta.rma(math.max(change(close),0), length)`, `down = ta.rma(-math.min(change(close),0),
32: length)`, `rsi = 100 - 100/(1 + up/down)`, and `ta.rma` is Wilder's recursive smoothing seeded by a plain
33: average of the first `length` values (TradingView Pine Script Reference Manual, `ta.rsi`/`ta.rma`
34: entries, pine-script-docs/v5+v6, https://www.tradingview.com/pine-script-reference/v5/).
35:
36: **Known variants and why we picked ours:**
37: - *Cutler's RSI* uses a plain SMA of gains/losses throughout (no recursive smoothing) — rejected, not
38:   what "RSI" means on TradingView/most platforms, and not what MalkanView's 40/60 rule assumes.
39: - *EMA-seeded-from-first-value* Wilder variants (seed = first delta, not an SMA of `period` deltas) —
40:   rejected; diverges from Wilder's own worked example and from `ta.rma`'s documented seeding.
41: - `bt/bt_rsi.py.new`'s `rsi_wilder` IS off, confirmed by this audit: its seed divides
42:   `sum(gains)/len(gains)` and `sum(losses)/len(losses)` — i.e. by the COUNT OF NONZERO up-moves /
43:   down-moves among the first `period` deltas — instead of dividing by `period` as steps 2-3 above
44:   require (down-moves silently drop out of the gain average's denominator, and vice versa). Worked
45:   example, period=5, closes=[100,102,101,103,106,105,107,110,108,...]: deltas[0:5]=[2,-1,2,3,-1];
46:   textbook seed = avg_gain=(2+0+2+3+0)/5=1.4, avg_loss=(0+1+0+0+1)/5=0.4; `bt_rsi.py.new`'s buggy seed =
47:   avg_gain=(2+2+3)/3=2.3333, avg_loss=(1+1)/2=1.0 — a materially different RSI from index `period`
48:   onward (the recursive smoothing after the seed is correct Wilder, so the error is confined to, and
49:   persists from, the seed). This is why `rsi/TEST_PLAN.md` Case C1 explicitly says "NOT bt_rsi.py.new,
50:   which is off" and why spec 073 was corrected (see the audit report) to stop telling a worker to
51:   "reuse `rsi_regime`'s EXACT algorithm" from that file — `rsi_regime` itself (the 40/60 window
52:   classifier) does not depend on `rsi_wilder`'s seeding and is unaffected, but the instruction's
53:   phrasing risked normalizing "copy from bt_rsi.py.new" as a pattern for future specs touching RSI math.
54:
55: **Worked example (period=3):** closes = [10, 12, 11, 14]. deltas = [2, -1, 3]. Seed: gains=[2,0,3] over
56: 3 deltas -> avg_gain=(2+0+3)/3=1.6667, losses=[0,1,0] -> avg_loss=(0+1+0)/3=0.3333. rs=5.0,
57: rsi[3] = 100 - 100/6 = 83.3333.
58:
59: ## 2. RMA / SMMA (`rsi_ma` type="RMA")
60:
61: **Chosen definition:** `alpha = 1/length`. Seed = SMA of the first `length` available (consecutive,
62: non-None) input values. Subsequent: `rma[i] = (x[i] - rma[i-1]) * alpha + rma[i-1]`.
63:
64: **Canonical source:** Wilder 1978 (this is literally Wilder's smoothing method, generalized to any
65: input series, not just gain/loss); TradingView `ta.rma(source, length)` reference confirms the same
66: SMA-seed-then-recursive-average behavior (pine-script-docs, `ta.rma`).
67:
68: **Variant note:** some libraries seed RMA with the first raw value instead of an SMA of `length` values
69: — rejected for the same reason as the RSI seeding variant above (diverges from Wilder's and Pine's
70: documented seed).
71:
72: **Worked example (length=3):** x = [50,55,45]. Seed = (50+55+45)/3 = 50.0. Next x=60:
73: rma = (60-50)/3+50 = 53.3333.
74:
75: ## 3. SMA (`rsi_ma` type="SMA")
76:
77: **Chosen definition:** plain arithmetic mean of the last `length` consecutive non-None values ending at
78: `i`; `None` if fewer than `length` consecutive values are available.
79:
80: **Canonical source:** universal definition; cross-checked against TradingView `ta.sma(source, length)`
81: (pine-script-docs, `ta.sma`), which is the same rolling arithmetic mean, no variants to choose between.
82:
83: **Worked example (length=3):** [50,55,45] -> 50.0.
84:
85: ## 4. EMA (`rsi_ma` type="EMA"), including seeding
86:
87: **Chosen definition:** `alpha = 2/(length+1)`. Seed = SMA of the first `length` available values (same
88: seeding convention as RMA above, for consistency within this codebase's `rsi_ma` module — see variant
89: note). Subsequent: `ema[i] = (x[i] - ema[i-1]) * alpha + ema[i-1]`.
90:
91: **Canonical source:** standard EMA formula (`alpha = 2/(N+1)`); TradingView `ta.ema(source, length)`
92: reference (pine-script-docs, `ta.ema`) documents the same alpha and an SMA-style seed for the first
93: value.
94:
95: **Known variants and why we picked ours:** two seeding conventions are common — (a) SMA-seeded (first
96: `length` values averaged, then EMA recursion starts at index `length-1`), used here; (b) "EMA from the
97: first raw value" (`ema[0] = x[0]`, recursion starts immediately) — common in some charting libraries
98: (older TA-Lib EMA) but produces a materially different early-series value and complicates cross-checking
99: against SMA/RMA in the same module (`rsi_ma` supports SMA/WMA/EMA/RMA switched by a single `type` param;
100: using the same "SMA seed, first `length` values needed" contract for all four keeps their None-prefix
101: identical, which the rsi_ma implementation and its tests rely on). We picked (a) for internal consistency
102: and because it matches the TradingView-anchored convention used for RSI/RMA above.
103:
104: **Worked example (length=3):** x=[50,55,45,60]. Seed(idx of 45)=SMA([50,55,45])=50.0. Next x=60:
105: ema=(60-50)*0.5+50=55.0 (alpha=2/4=0.5).
106:
107: ## 5. WMA (`rsi_ma` type="WMA")
108:
109: **Chosen definition:** linearly increasing weights `1..length` applied oldest-to-newest over the last
110: `length` consecutive values: `wma[i] = sum(w_k * x[i-length+1+k-1] for k in 1..length) / sum(1..length)`.
111:
112: **Canonical source:** standard WMA; TradingView `ta.wma(source, length)` reference (pine-script-docs,
113: `ta.wma`) documents the identical oldest-gets-least-weight linear weighting.
114:
115: **Variant note:** no material variants for linear WMA weighting (some libraries reverse the weight
116: order, i.e. newest = weight 1 — rejected, contradicts Pine's `ta.wma` and every mainstream charting
117: platform's convention of "recent bars matter more").
118:
119: **Worked example (length=3):** [50,55,45], weights [1,2,3]: (50*1+55*2+45*3)/6 = 295/6 = 49.1667.
120:
121: ## 6. Tolerance-band level/line events (`rsi_events.rsi_events`)
122:
123: **Chosen definition:** generic level-touch state machine over any numeric series vs a `level` +/-
124: `tolerance` band. See `layers/rsi/TEST_PLAN.md` "rsi_events.py" section for the full mechanical
125: specification (side classification, run tracking, `support`/`rejection`/`failure`/`cross` semantics,
126: `None`-skipping for warm-up/gap bars, penetration and `t` conventions). This is a repo-original
127: mechanical definition (not from an external technical-analysis text) built to formalize "price touches
128: a level and either holds or breaks" for RSI 40/60/70/30 zones and cc_retest-style level interactions; no
129: external canonical source applies. Re-derived independently for this audit (see Case E1 below) by
130: implementing the state machine directly from the TEST_PLAN's prose, without reading `rsi_events.py`'s
131: source, and the result matches the plan's expected event list exactly.
132:
133: ## 7. Forward return / MAE (`layers/runner.py`)
134:
135: **Chosen definition:** for an event at index `i` with side sign `sgn` (+1 long, -1 short) and horizon
136: `h`: `ret = sgn * (closes[i+h] - closes[i]) / closes[i]` (only when `i+h < len(closes)`, else the event
137: contributes nothing at that horizon — insufficient data, not a zero). `mae` (max adverse excursion) at
138: horizon `h` = the minimum of `sgn * (closes[j]-closes[i])/closes[i]` over `j in [i+1, min(i+h,len-1)]`
139: (the worst point reached on the way to the horizon, close-only in this hand-derivable form; production
140: code should prefer intrabar high/low when available — documented as a scope note in
141: `layers/TEST_PLAN_runner.md`, not tested there). `hit_rate` = fraction of contributing events with
142: `ret > 0`. Aggregates (`mean_return`, `mae`) average only over events with data at that horizon.
143:
144: **Canonical source:** standard "forward return" / "event study" methodology used throughout quant
145: research (see e.g. Lopez de Prado, *Advances in Financial Machine Learning*, triple-barrier /
146: event-based labeling chapters, for the general pattern of measuring returns and adverse excursion from
147: a fixed event index over a fixed horizon); the specific close-only MAE simplification here is a
148: documented scope reduction of that general idea, not a claim that it matches any one textbook formula
149: verbatim.
150:
151: ## 8. Resample / OHLCV aggregation + bucket anchoring (`layers/timeframe/tf_resample.py`)
152:
153: **Chosen definition:** see `layers/timeframe/TEST_PLAN.md` for the full boundary-math and aggregation
154: spec (seconds/days/week/month bucket anchoring, closed-bars-only rule, gap counting). Bucket math is
155: plain UTC calendar/epoch arithmetic (`floor` division for seconds/day-multiples, Monday-anchored ISO
156: week via `epoch_day % 7`, first-of-calendar-month for `1M`) — this is a mechanical/engineering choice
157: (Binance-compatible UTC bucketing), not drawn from a named external formula; cross-checked against
158: Python's own `datetime`/`timezone.utc` arithmetic (stdlib is the "canonical source" here). OHLCV
159: aggregation is the universal convention: `o` = first bar's open in the closed window, `c` = last bar's
160: close, `h` = max high, `l` = min low, `v` = sum of volumes; a bucket is only emitted once
161: `bucket_end <= last_bar_close_ms` (never a partial trailing bucket).
162:
163: ## 9. CryptoCred swing / MSB / retest / R-target math (`layers/cryptocred/*`)
164:
165: Source: `MyTradingSys/research/cross_trader_consolidated.md` cluster C08 (MSB Definition &
166: Significance), C07 (Retests) and C10 (Setup Types) — these are verbatim-quote-verified transcript
167: extracts (per repo convention, higher confidence than the Malkan web research), and the module
168: docstrings already cite the specific rule IDs (C08-Rule1, C08-E01/E03/E05, C07-E01/E04/E05, C10-E01/
169: E02/E03/E04/E05). No external canonical formula exists for these (they are one trader's discretionary
170: rules mechanized); this repo's own interpretation choices are documented at the top of
171: `cc_structure.py`, `cc_retest.py` and `cc_setups.py` and restated in `layers/cryptocred/TEST_PLAN.md`.
172: Independently re-derived for this audit directly from those docstrings' prose (fixed-width fractal swing
173: detection with strict `>`/`<` comparisons against both side-windows; MSB = a close beyond the most
174: recent opposing swing, gated by "lower-high"/"higher-low" prior sequence when `require_prior_sequence`;
175: retest = price re-touches the broken level within `tolerance_pct` before invalidating past
176: `invalidate_pct`, scanned bar-by-bar from `confirm_i`; R-target = `entry +/- target_r * |entry - stop|`
177: in the trade's profit direction) — see Cases S1-S7/R1-R5/U1-U6 below, all reproduced exactly.
178:
179: ## 10. bt_stats / ref_pbo metrics (Sharpe, PSR/DSR, PBO)
180:
181: **Sharpe (`bt/bt_stats.py:sharpe`, `bt/ref_pbo.py:sharpe`):** `mean(x) / population_stdev(x)` (divides
182: by `n`, not `n-1` — population, not sample, standard deviation; both modules agree on this choice).
183: Canonical source: standard Sharpe ratio (reward per unit of volatility); the population-vs-sample choice
184: here follows Bailey/Lopez de Prado's PBO paper's own convention of dividing by the realized in-sample
185: `N`, not `N-1`, when comparing strategy variants over a fixed block of returns.
186:
187: **PSR / DSR (`bt/bt_stats.py:psr,dsr,expected_max_sr`):** Probabilistic Sharpe Ratio / Deflated Sharpe
188: Ratio per Bailey & Lopez de Prado, "The Sharpe Ratio Efficient Frontier" (2012) and the DSR literature —
189: `psr = Phi((SR - SR*) * sqrt(T-1) / sqrt(1 - skew*SR + (kurtosis-1)/4 * SR^2))`; `dsr` substitutes
190: `SR* = expected_max_sr(var_sr, n_trials)` (the expected maximum Sharpe ratio achievable by chance over
191: `n_trials` independent strategy variants, via the Euler-Mascheroni-constant expression for the expected
192: max of `n_trials` standard normals). Matches the implementation in both files exactly.
193:
194: **PBO / CSCV (`bt/bt_stats.py:pbo_cscv`, `bt/ref_pbo.py:ref_pbo_cscv`):** Combinatorially Symmetric
195: Cross-Validation per David H. Bailey, Jonathan Borwein, Marcos López de Prado, Qiji Jim Zhu, "The
196: Probability of Backtest Overfitting," Journal of Computational Finance (2015; SSRN 2326253,
197: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253) — split the return matrix into `S` equal
198: contiguous blocks, form every equal-size in-sample/out-of-sample split (`C(S, S/2)` combinations), pick
199: the in-sample-best variant `n*` per split, compute its out-of-sample relative rank `w = (count(oos[n] <
200: oos[n*]) + 1)/(N+1)`, `logit = ln(w/(1-w))`; `PBO` = fraction of splits where `logit <= 0` (the
201: in-sample winner underperforms the OOS median). `ref_pbo.py` is the deliberately independent
202: re-implementation of `bt_stats.py:pbo_cscv` used by `test_ref_pbo.py` as a cross-check — both were
203: inspected for this audit and agree on the CSCV algorithm and the Sharpe convention (population stdev).
204:
205: ## 11. Execution math (`execution/plan_compiler.py`, `execution/executor.py`,
206: `execution/risk_guard.py`) — canonical Deribit BTC-PERPETUAL inverse-contract math
207:
208: All definitions derived from Deribit's published BTC-PERPETUAL contract spec (Deribit Exchange
209: documentation, "BTC-PERPETUAL" instrument page: tick size 0.5 USD, contract size / minimum trade
210: amount 10 USD, inverse contract settled/margined in BTC) and from first-principles inverse-contract
211: PnL algebra — NOT from reading `plan_compiler.py`/`executor.py`.
212:
213: **11.1 Tick-size price snapping — directional, by order purpose and side (Opus review R2: the earlier
214: round-half-to-even version was REJECTED for being a definition borrowed from Python's `round()` rather
215: than from risk direction, and for ignoring which way rounding a given order should go).** Deribit
216: BTC-PERPETUAL quotes in 0.5 USD increments; every order price must be an exact multiple of the tick.
217: There is no single tick-snap rule — the direction depends on what the price IS, from first principles
218: (never accept a worse fill than planned; never let a stop realize a bigger loss than budgeted; make a
219: target more likely to fill, not less):
220: - **Entry (limit or ladder rung):** BUY -> `floor` (never pay MORE than the planned price), SELL ->
221:   `ceil` (never sell for LESS than the planned price).
222: - **Stop:** LONG stop (below entry) -> `ceil`, i.e. rounds UP, toward entry (a stop that rounded further
223:   DOWN would be further from entry, i.e. a BIGGER loss than budgeted). SHORT stop (above entry) ->
224:   `floor`, toward entry, for the same reason (mirrored). In both cases: **the loss can never exceed the
225:   budget the plan computed.**
226: - **Target:** LONG target (above entry) -> `floor`, toward entry (a target further from entry, i.e.
227:   rounded UP, is less likely to be reached/filled than one closer to entry). SHORT target (below entry)
228:   -> `ceil`, toward entry (mirrored). In both cases: **rounding toward entry makes the target more
229:   likely to fill at the stated price or better, never less likely.**
230:
231: Implementation: exact Decimal tick arithmetic (not float + epsilon), so the boundary is exact regardless
232: of binary floating-point representation error: convert `price` and `tick` to `Decimal` via `Decimal(str(x))`
233: (never `Decimal(x)` directly on a float, which would import the float's own binary imprecision), divide,
234: then `.to_integral_value(rounding=ROUND_FLOOR)` or `ROUND_CEILING` per the direction above, then multiply
235: back by `tick`. (A `math.floor(price/tick + 1e-9)*tick` epsilon-nudge is an acceptable float-only
236: alternative but was not the one chosen here — Decimal was, since it has no epsilon to get wrong.)
237:
238: Worked examples, `tick=0.5`: `price=50000.1` (just above the 50000.0 tick) -> `floor=50000.0`,
239: `ceil=50000.5`. `price=50000.49` (just below the 50000.5 tick) -> `floor=50000.0`, `ceil=50000.5`.
240: `price=50000.0` (exact tick) -> `floor=ceil=50000.0` (no-op either direction).
241:
242: **11.2 Contract size (amount) rounding — floor only, reject below minimum (Opus review R2: the earlier
243: `max(10, round(amount/10)*10)` was REJECTED — forcing a too-small size UP to the 10 USD minimum can
244: trade MORE size, and take MORE risk, than the plan's own risk budget calls for).** Minimum trade amount
245: is 10 USD, in 10 USD increments. Canonical definition: floor `amount` to the nearest 10 USD multiple
246: (same Decimal `ROUND_FLOOR` approach as 11.1, never rounds up); if the floored size is below 10 USD, the
247: plan is REJECTED (raise, do not silently substitute 10). Source: Deribit BTC-PERPETUAL "Minimum Trade
248: Amount" = 10 USD. Worked examples: `amount=25` -> `25/10=2.5` -> floor -> `2` -> `20` (not `30`, and not
249: banker's-rounded to `20` either — floor always rounds down regardless of the fractional part).
250: `amount=29.9` -> floor -> `20`. `amount=9` -> floors to `0` USD, below the 10 USD minimum -> REJECTED
251: (the plan cannot be traded at this risk budget; forcing it up to 10 would silently exceed that budget).
252:
253: **11.3 Ladder entry rung prices.** For an N-rung ladder over `[low, high]` with even spacing
254: `step=(high-low)/(N-1)` (N=1 uses a single rung), first-principles convention (best price is the one
255: first touched moving away from the current market toward the range): for a LONG ladder (buying on a
256: pullback) rung 1 = `high` (nearest/best), each subsequent rung steps down by `step` to rung N = `low`
257: (worst, deepest fill); for a SHORT ladder this is mirrored, rung 1 = `low`, stepping up to rung N =
258: `high`. This is a design convention (not an exchange rule) documented here so ladder tests derive from
259: it rather than from the module.
260:
261: **11.4 Ladder / multi-fill average price for an inverse contract — harmonic mean weighted by USD
262: size.** For an INVERSE contract (Deribit BTC-PERPETUAL: each contract is a fixed 1 USD of notional;
263: the quantity of BTC bought/sold at price `p` for a `size`-USD fill is `size/p` BTC, NOT `size*p` USD of
264: BTC), the correct volume-weighted average price across fills `(p_i, size_i)` is the harmonic mean
265: weighted by USD size, not the arithmetic mean:
266: `avg_price = sum(size_i) / sum(size_i / p_i)`
267: Derivation: total BTC acquired = `sum(size_i/p_i)`; total USD notional = `sum(size_i)`; the single
268: price that would have produced the same BTC quantity for the same total USD notional is
269: `total_USD / total_BTC = sum(size_i) / sum(size_i/p_i)`, i.e. the weighted harmonic mean. The
270: plain notional-weighted arithmetic mean `sum(p_i*size_i)/sum(size_i)` is the correct formula for a
271: LINEAR contract (fixed BTC quantity per contract) but is WRONG for Deribit's inverse contract, per
272: Deribit's own inverse-contract PnL documentation ("Perpetual and Futures Contract Specifications" /
273: "Trading Guide — Inverse Futures": PnL and average entry for inverse contracts are computed via
274: `1/price` quantities, not `price` quantities directly). Worked example (4-rung ladder, sizes
275: `[10,10,20,30]` USD, snapped prices `[50200, 50050, 49900, 49750]`): harmonic mean =
276: `70 / (10/50200 + 10/50050 + 20/49900 + 30/49750) = 70 / 0.0014028201.. = 49899.49` (rounded to 2dp),
277: versus the arithmetic mean `sum(p*s)/sum(s) = 3493000/70 = 49900.00` — a real, if small, discrepancy
278: that grows with wider price ranges or larger size skew across rungs.
279:
280: **11.5 Inverse-contract average fill price (live fills).** Same formula as 11.4, applied to actual
281: exchange fills as they arrive: `avg_fill = filled_total_usd / sum(fill_amount_i / fill_price_i)`. This
282: is the correct live-fill analogue of 11.4 and must use the same harmonic-mean-weighted-by-USD-size
283: definition — a plan-compile-time estimate (11.4) and a live-fill computation of the same quantity must
284: not silently use two different formulas.
285:
286: **11.6 Worst-case loss at a fixed-percent stop (inverse contract).** For a LONG position of `size` USD
287: opened at average entry `E`, with a stop at `S = E*(1-pct)` (LONG) or `S = E*(1+pct)` (SHORT), the
288: inverse-contract PnL in BTC is `size*(1/E - 1/S)` for a LONG close (and the mirror for SHORT); converting
289: to USD at the exit price `S` gives `PnL_usd = size*(1/E - 1/S)*S = size*(S/E - 1) = size*(S-E)/E`. Taking
290: the stop side this is always a loss, so:
291: `worst_case_loss_usd = -size * abs(E - S) / E`
292: (equivalently `-size*pct` when `S` is not tick-snapped; snapping `S` introduces a small residual). This
293: is the standard inverse-contract linear PnL approximation (exact for a single close at the stop price,
294: using the stop price itself as the BTC-to-USD conversion rate) per Deribit's inverse-contract PnL
295: formula. Worked example: `size=70`, `E=49899.49` (11.4's harmonic mean), `pct=2%`, LONG (stop snaps `ceil`, 11.1)
296: -> `S_raw = 49899.49*0.98 = 48901.50002..` -> snapped `S=48901.5` -> `loss = -round(70*abs(49899.49-48901.5)/49899.49, 2)
297: = -round(70*997.99/49899.49, 2) = -round(1.4004.., 2) = -1.40` USD.
298:
299: NOTE: `worst_case_loss_usd` is the loss realized AT the stop price only — it excludes stop-market
300: trigger slippage (the actual fill can be worse than the trigger once the market order the stop becomes
301: is filled) and exchange fees. It is a floor on planning risk, not a guarantee of the maximum possible
302: real-world loss.
303:
304: **11.7 Target price from PnL%.** Inverting 11.6's relation for a target instead of a stop: a desired
305: USD PnL of `+pct%` of the position's USD size at exit price `T` satisfies `size*(T-E)/E = size*pct/100`
306: (LONG) -> `T = E*(1+pct/100)`, mirrored to `T = E*(1-pct/100)` for SHORT. Same formula shape as the stop
307: in 11.6, opposite sign convention, then tick-snapped TOWARD entry per 11.1 (LONG target -> `floor`,
308: SHORT target -> `ceil` — the opposite direction from the stop, which also snaps toward entry but for the
309: opposite reason: capping loss rather than raising fill probability). This is the same computation done in two
310: places (`plan_compiler.py` at compile time from the ladder estimate, `executor.py` at fill time from
311: the real average fill) and per 11.5 both must use the same `E` definition (11.4/11.5's harmonic mean).
312:
313: **11.8 Notional cap.** Account-wide notional exposure check: for a size already expressed in USD
314: notional (Deribit BTC-PERPETUAL "size"/"amount" fields are USD-denominated), `notional = abs(size)`
315: directly, with no price multiply, when the caller has already confirmed `size` is USD (the
316: `mark_price=None` branch); when `size` is in BTC/contracts needing conversion, `notional =
317: abs(size) * mark_price`. Source: Deribit position/ticker API — BTC-PERPETUAL position `size` is
318: reported in USD; the `mark_price`-multiply branch exists only for instruments/fields that are NOT
319: already USD-denominated. A projected notional `current + new` that exceeds the account cap
320: (`MAX_ACCOUNT_NOTIONAL_USD`) is a breach; no formula ambiguity here, just a units contract that the
321: caller must get right (this is a documentation gap, not a math bug, per FORMULA_INVENTORY.md's "mark
322: None -> assumes USD units" flag).
323:
324: ## 12. Core ATR — operator decision: plain SMA, not Wilder (2026-09-28)
325:
326: **Canonical True Range definition** (J. Welles Wilder, *New Concepts in Technical Trading Systems*,
327: 1978): `TR[i] = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))` for `i>=1`
328: (undefined at `i=0`, no prior close).
329:
330: **Operator decision (2026-09-28):** MTS's core ATR (`SetupCandidatesBuilder.java`,
331: `averageTrueRange`) is a PLAIN (simple, unweighted) arithmetic average of `TR` over the lookback
332: window, `ATR[n] = mean(TR[i] for i in window of size n)` — explicitly NOT Wilder's recursive/RMA
333: smoothing (contrast with section 1's RSI, which IS full Wilder `ta.rma` smoothing). This is a
334: deliberate choice for MTS's core (Tom's method), confirmed by the operator on 2026-09-28; it must not
335: be silently changed to Wilder smoothing by a future worker who assumes "ATR" implies Wilder by default.
336:
337: **Worked example (plain SMA, period=3):** highs=[10,11,12,11], lows=[9,9,10,9], closes=[9.5,10.5,11.5,10].
338: `TR[1]=max(11-9, |11-9.5|, |9-9.5|)=max(2,1.5,0.5)=2`. `TR[2]=max(12-10,|12-10.5|,|10-10.5|)=max(2,1.5,0.5)=2`.
339: `TR[3]=max(11-9,|11-11.5|,|9-11.5|)=max(2,0.5,2.5)=2.5`. `ATR = mean(TR[1..3]) = (2+2+2.5)/3 = 2.1667`
340: (plain average — Wilder recursive smoothing over the same window, for comparison, would instead need a
341: seed plus `(prev*(n-1)+TR)/n` recursion and is NOT what MTS core computes).
342:
343: ## 13. T055 shared cost model (`layers/positioning/trade_costs.py`) - added 2026-09-29
344:
345: Applies to C1, C2, C3 below. Binance USDT-M perp: taker fee 10 bps round trip (0.0010), realistic slippage
346: added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b "SCALPING FEE FLOOR",
347: internal arithmetic). Funding: a position pays `side_sign * rate` (as a fraction of notional, entry notional
348: used) for every funding record with `t_in < calc_time <= t_out`; `side_sign` = +1 long, -1 short, so longs
349: pay positive rates and shorts receive them (Binance perpetual funding convention).
350: `gross = side_sign * (p_out - p_in) / p_in`;
351: `net = gross - fee_rt - slip_rt - side_sign * sum(rate over records in (t_in, t_out])`.
352: Worked: long 100 -> 101, funding records at t=8h rate 0.0001 and t=16h rate 0.0003, t_in=0, t_out=16h:
353: `net = 0.01 - 0.0010 - 0.0002 - 0.0004 = 0.0084`. Short 100 -> 99, same records: gross = 0.01,
354: funding term = -1 * 0.0004 = -0.0004, `net = 0.01 - 0.0012 + 0.0004 = 0.0092`.
355:
356: ## 14. T055 C1 - funding-extreme reversion + CVD/price divergence fade (`layers/positioning/funding_cvd_fade.py`)
357:
358: Sources: funding-extreme reversion T2, Memon 2026 (7y Binance) via `research/whale_positioning_evidence_2026-09-12.md`
359: (the percentile threshold is NOT given there: UNDEFINED in source, so it is a grid parameter); mechanism
360: He/Manela/Ross/von Wachter arXiv 2212.06888 (T2); CVD/price divergence = same CVD as `bt_data.cvd_delta`
361: (section above, `delta = 2*tbv - v`, running sum). Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme).
362: - Funding percentile: for the k-th funding record (k >= lookback-1), `pct[k] = count(w <= r_k) / lookback`
363:   where `w = rates[k-lookback+1 .. k]` (inclusive of the current record, `r_k = rates[k]`).
364: - Funding known at bar time: latest record with `calc_time <= bar["t"]` (no look-ahead).
365: - Divergence at bar i >= n on closes `c` and `cvd`: bearish if `c[i] > max(c[i-n..i-1])` and
366:   `cvd[i] < max(cvd[i-n..i-1])`; bullish if `c[i] < min(c[i-n..i-1])` and `cvd[i] > min(cvd[i-n..i-1])` (strict).
367: - Signal: short if bearish AND `pct >= hi`; long if bullish AND `pct <= lo`. Funding-only variant: one event per
368:   funding record at the first bar with `t >= calc_time`; short if `pct >= hi`, long if `pct <= lo`.
369: - Defaults (all UNDEFINED in source, grid-searched IS only): lookback 90 records, n 20, hi 0.95, lo 0.05.
370: - Costs: section 13. Kill (T055a H2 / T055b): OOS Sharpe < 0.3 or too few events. Data: funding exists 2025-09 on only.
371:
372: ## 15. T055 C2 - intraday session momentum (`layers/session/session_momentum.py`)
373:
374: Source: Shen, Urquhart, Wang, *Financial Review* 57(2), 319-344, 2022, DOI 10.1111/fire.12290 (T1): the first
375: half-hour return predicts the last half-hour return (liquidity-provision mechanism). The T055b report words it as
376: "first-half-session return biases rest-of-session"; both entries are supported via `entry_min`.
377: - Session start `S` = UTC midnight of the bar's day + `session_start_min` minutes. Window end `E = S + first_min` min.
378: - `r_first = close(last bar with t + bar_ms <= E) / open(first bar with t >= S) - 1`; needs both bars to exist.
379: - Side = long if `r_first > min_abs`, short if `r_first < -min_abs` (else no event). Entry at the close of the
380:   bar with `t + bar_ms == S + entry_min` min (event index i = that bar; runner enters at `closes[i]`).
381:   `entry_min = first_min` gives "rest of session"; `entry_min = session_len - 30` gives the paper's "last half-hour".
382: - Defaults (adaptation to 24/7 BTC, UNDEFINED in source): session_start_min 0 (UTC day), first_min 30, min_abs 0.
383: - Costs: section 13. Kill (T055b): effect sign-flips or vanishes post-2023.
384:
385: ## 16. T055 C3 - turn-of-candle (`layers/turn_of_candle/turn_of_candle.py`)
386:
387: Source: Shanaev, Vasenin, Stepanov, *Heliyon*, PMC10015199 (T1): returns concentrate at the opening of 15-minute
388: candles (minutes 0, 15, 30, 45 of the hour). The paper has no cost model.
389: - On 1-minute bars: `mq = (t_ms // 60000) % 15` (minute-of-quarter; epoch-aligned, 15 divides 60). Per-bar
390:   return `(c - o) / o`. `turn_mean` = mean return of bars with `mq == 0`; `other_mean` = mean of the rest;
391:   `by_minute[m]` = mean return of bars with `mq == m`.
392: - Event: at bars with `mq == 15 - lead_minutes` (enter at that bar's close, i.e. just before the candle opens),
393:   side fixed by parameter (`long`, `short`); direction of the effect is NOT stated in the report, so both are
394:   grid-searched IS only, and the sign of `turn_mean` is reported.
395: - Costs: section 13. Fee floor 10 bps RT vs a per-minute effect: expected to fail unless gross edge is large.
396:   Kill (T055b): net-of-cost edge does not survive on >= 2 OOS years.
397:
398: ---
399:
400: ## 17. B070 net R:R fee model (`runtime/mts_math.py` calculate_net_rr, `ExecutionMathConstants.netRR`) - added 2026-10-03
401:
402: Operator ruling (a), 2026-10-03: replaces the flat `net = gross * 0.75` (no trader source). Source of the fee: `backtest/fees.py`
403: DERIBIT_TAKER = BINANCE_TAKER = 0.0005 per side, both legs taker (stop and entry are market). `cost = 2 * taker * entry`
404: (price units). `net_rr = (|target - entry| - cost) / (|entry - stop| + cost)`; stop == entry -> 0.0.
405: Worked: entry 100, target 104, stop 98: cost 0.1, net = 3.9 / 2.1 = 1.8571. Tight stop: entry 100, target 100.3, stop 99.9:
406: cost 0.1, net = 0.2 / 0.2 = 1.0 (gross 3.0). The Java constant must equal fees.py (`tests/test_b070_fee_parity.py`).
407:
408: ## 18. Anchored volume profile touch study (`backtest/vp_pivot_probe.py`) - added 2026-10-09
409:
410: Context: `research/vp_pivots_2026-10-09/SOURCES.md` and `PLAN.md`. Tom draws a composite profile "from the last major
411: high to the last major low" (sQ_biBKhPVU:19); the engine anchors every profile to a UTC calendar boundary. This section
412: defines the mechanical pieces of the offline probe. Everything marked NO-SOURCE is a measurement choice or the pivot
413: definition, flagged and not tuned.
414:
415: **18.1 Profile of a bar set (bin grid w = 10.0 USD, NO-SOURCE, engine uses about 5 USD).** Bin k covers `[k*w, (k+1)*w)`.
416: A bar `(l, h, v)` with `h > l` adds `v * overlap([l,h],[k*w,(k+1)*w)) / (h - l)` to bin k (uniform spread over its
417: high-low; the engine instead uses triangular weights around the typical price, an accepted difference because every
418: family in the probe goes through the same builder). A bar with `h == l` adds all of `v` to bin `floor(l/w)`.
419: POC = lowest bin holding the maximum volume (ties go to the lower bin, as the engine's `Stream.max` keeps the first
420: key). `poc_price = k_poc*w + w/2`. Value area = 70% (engine `VALUE_AREA_PCT`; Tom: "70% of the trades",
421: 1utSjHs_Mq8:19): start `lo = hi = k_poc`, `acc = vol[k_poc]`; while `acc < 0.70 * total` and bins remain: `vl = vol[lo-1]`
422: (or -1 if `lo` is the first bin), `vh = vol[hi+1]` (or -1 at the last bin); if `vl >= vh` and `lo` is not the first
423: bin take `lo-1`, else take `hi+1` (else `lo-1`). The scan covers every bin from the lowest to the highest bin touched
424: by any bar of the set (zero-volume interior bins included). `val = lo*w`, `vah = (hi+1)*w`. Empty or zero-volume set -> none.
425: *Worked A (w = 1):* bars (l,h,v) = (0,2,6), (1,3,4), (1,2,10): bin0 = 3, bin1 = 3+2+10 = 15, bin2 = 2, total 20, target
426: 14; POC = bin1 (poc_price 1.5), `acc = 15 >= 14` at once -> val 1.0, vah 2.0.
427: *Worked B (w = 1, point-mass bars at bin centres):* bin volumes [1,2,10,4,3], total 20, target 14: POC bin2, `acc = 10`;
428: `vl = 2 < vh = 4` -> hi = 3, `acc = 14` stop -> val 2.0, vah 4.0, poc_price 2.5.
429: *Worked C (tie):* bin volumes [3,10,3], total 16, target 11.2: `acc = 10`, `vl = vh = 3` -> lower: lo = 0, `acc = 13` stop
430: -> val 0.0, vah 2.0.
431:
432: **18.2 Fractal pivots (NO-SOURCE width n; FORMULAS section 9 fixed-width fractal, strict comparisons).** On a bar series
433: with wicks `h`, `l`: bar i is a pivot high iff `h[i] > h[j]` for every `j in [i-n, i+n], j != i`; pivot low iff
434: `l[i] < l[j]` for the same j. Highs and lows are tested independently (an outside bar can be both; `find_swings` would
435: label it a high only). Needs `n <= i <= len-1-n`. A pivot at i is confirmed at the close of bar `i+n`, so it may be used
436: from the open of bar `i+n+1` (no look-ahead).
437: *Worked:* n = 1, h = [1,3,2,5,4,1,2] -> pivot highs at i = 1 and 3 (h = 3 > 1,2; 5 > 2,4); i = 6 is the last bar, not
438: testable; a plateau h = [1,3,3,2] gives none (equality fails). n = 2 with h = [1,2,5,2,1] -> pivot high at i = 2 only.
439:
440: **18.3 Size filter (NO-SOURCE k).** A pivot p is *meaningful* for k > 0 iff there is an earlier pivot q of the opposite
441: kind (largest `q.i < p.i`) with `|price_p - price_q| >= k * ATR14(p.i)`, where ATR14(i) is the plain-SMA ATR of section 12
442: over the 14 true ranges ending at bar i (needs i >= 14). `k = 0`: every fractal pivot is meaningful. Pivot price = the
443: bar's `h` (high) or `l` (low).
444:
445: **18.4 Anchored families (all built on 5-minute bars, levels refreshed on a 15-minute grid, i.e. at 5m bars whose open
446: time is a multiple of 900 s, using only bars that closed before the refresh).**
447: - `session`: bars from 00:00 UTC of the current day. `weekly`: from Monday 00:00 UTC. Developing; need >= 12 bars.
448: - `prior_day`: the previous UTC day; `prior_week`: the previous Monday-Sunday. Static, active from the first bar after.
449: - `A1(n,k)` (Tom-shaped): let H = the last meaningful pivot high and Lo = the last meaningful pivot low, both confirmed;
450:   the set is every 5m bar from the open of the earlier pivot's 1h bar to the close of the later pivot's 1h bar. Active
451:   from the open of the 5m bar after the later pivot is confirmed (`i_later + n` closed). Static until a newer
452:   meaningful pivot is confirmed.
453: - `A2(n,k)` (operator's idea, not Tom's words): the set is every 5m bar from the open of the last confirmed meaningful
454:   pivot's 1h bar (either kind) up to the refresh. Developing; need >= 12 bars.
455: Each profile contributes three levels: POC (`poc_price`), VAH, VAL (Tom, aursfDVYzUk:7: "reaction levels, value high,
456: value low, ... point of control").
457:
458: **18.5 Touch event and R-multiple outcome (NO-SOURCE measurement choices: R = 1 x ATR14 of 1h bars, H bars, barriers
459: +-1R).** Let `L` be the level in force at 5m bar j (the value from the latest refresh at or before bar j's open),
460: `c[j-1]` the previous close, `R = ATR14` of the 1h bars closed before bar j's open. Event: `l[j] <= L <= h[j]` and
461: `c[j-1] != L`. Side: `c[j-1] > L` -> long (price came down to the level, expected support); `c[j-1] < L` -> short.
462: Entry price is `L` (limit at the level). Long: stop `L-R`, target `L+R`; short mirrored. Resolution, conservative:
463: (1) in the touch bar only the stop is tested (`l[j] <= stop` for a long -> stopped at the stop price); (2) bars
464: j+1..j+H: if `l <= stop` (long) the exit is the stop, filled at the bar open if the bar opened beyond the stop; else if
465: `h >= target` the exit is the target; the stop is tested first when a bar holds both; (3) otherwise exit at the close of
466: bar j+H (timeout). One open event per (family, level type) at a time: a touch is skipped while the previous event of that
467: stream is still open (its exit bar >= this bar).
468: `gross_R = side * (exit - L) / R`; `net_R = (side * (exit - L) - fee_in * L - fee_out * exit) / R`, fees as fractions of
469: price from `backtest/fees.py`: primary all-taker `BINANCE_TAKER = 0.0005` on entry and exit; stated variant entry and
470: target maker `BINANCE_MAKER = 0.0002`, stop and timeout taker.
471: H = 48 five-minute bars (4h): NO-SOURCE, set as the phase 2 default 2026-10-09, not tuned.
472: *Worked:* long, L = 100, R = 2, target 102 reached, taker: `net_R = (2 - 0.0005*100 - 0.0005*102) / 2 = 0.9495`. Stop
473: (98): `(-2 - 0.05 - 0.049) / 2 = -1.0495`. Timeout at 100.5: `(0.5 - 0.05 - 0.05025) / 2 = 0.19987`.
474:
475: **18.6 Placebo.** For every real level value the placebo level is `L + d * R_ref`, `R_ref` = the ATR14(1h) in force at the
476: refresh, and `d` cycles deterministically through (-3, -2, -1, -0.5, +0.5, +1, +2, +3) by `(refresh_index) mod 8`. The
477: same event rule (18.5) is then applied. It measures what any price level earns under the same barriers and fees.
478:
479: **18.7 Statistics.** n = events; hit = share of exits at target; stop%; timeout%; `mean gross_R`, `mean net_R`. 95%
480: interval of a mean (or of a difference of two streams) = day-block bootstrap: events are grouped by UTC date, days are
481: resampled with replacement (2000 resamples, numpy `default_rng(20261009)`), statistic = sum of R over resampled days
482: divided by the number of events in them (difference: both streams use the same resampled days). Percentiles 2.5 / 97.5.
483: *Worked:* two days, day A events R = [1, 3], day B events R = [-2]; resample (A, A): mean 2.0; (B, B): -2.0; (A, B): 0.6667.
484:
485: ## Verification note (this audit, 2026-09-28)
486:
487: Every case number in `layers/timeframe/TEST_PLAN.md`, `layers/rsi/TEST_PLAN.md`,
488: `layers/TEST_PLAN_runner.md` and `layers/cryptocred/TEST_PLAN.md` was independently re-derived using a
489: throwaway Python scratch implementation written directly from this file's definitions (never by
490: importing or reading the layer modules under test), and matched the existing plan values exactly. No
491: plan numbers required correction. The one correction made was to `layers/rsi/TEST_PLAN.md`'s header
492: (Case C1 provenance claim, which described deriving from `bt/bt_rsi.py.new` — against the "never derive
493: from code" rule even though the module's own math turned out to match textbook Wilder); see that file's
494: diff and the audit report for detail.
```

## E02

### MyTradingSys/backtest/layers/rsi/params/default.json

SHA-256: `685fe1eb8a8dac6fa3c3ad65800721e5ee40f7ab7b50baf311ca1545776906a4`

```text
1: {
2:   "params_id": "rsi_default_2026-09-28",
3:   "source": "operator",
4:   "date": "2026-09-28",
5:   "note": "Defaults per RSI_TF_LAYER_DESIGN.md D2/D4. Standard RSI reading levels only (70/50/30). No 40/60 level anywhere in this file -- those numbers are private to malkan_40_60_default.json per the D2 isolation rule.",
6:   "rsi_core": {
7:     "period": 14
8:   },
9:   "rsi_ma": {
10:     "type": "SMA",
11:     "length": 14
12:   },
13:   "rsi_events": {
14:     "levels": [70, 50, 30],
15:     "tolerance": 0,
16:     "ma_support_enabled": false
17:   }
18: }
```

### MyTradingSys/backtest/layers/rsi/rsi_events.py

SHA-256: `79a1e736d5ea330e400a87057eb3626db07caa44fba729fda013d3301eae79a4`

```text
1: """
2: Generic level and line interactions with a tolerance band: support, rejection, cross.
3: Works on any level (70/50/30, 40/60) or on the rsi_ma line.
4:
5: Edge cases handled:
6: - Exact touch, touch-and-close-back both directions
7: - Close-through-band failure
8: - Single-bar band-skip cross
9: - Multiple resolving band runs at the same level
10: - An unresolved trailing run
11: - RSI flat on the level
12: - Warm-up bars (no RSI yet)
13: - Data gap mid-series (carry prev_side/run_entry_side across None entries unchanged)
14:
15: Note: this module is close-based only (it receives a single rsi series with no separate high/low RSI),
16: so intrabar RSI is explicitly out of scope here.
17: """
18:
19: def rsi_events(rsi: list, ts: list, level: float, tolerance: float, direction_names: tuple = ("above", "below")) -> list:
20:     if tolerance <= 0:
21:         raise ValueError("tolerance must be > 0")
22:     if len(rsi) != len(ts):
23:         raise ValueError("rsi and ts must have the same length")
24:
25:     # Validate direction_names
26:     if not isinstance(direction_names, tuple) or len(direction_names) != 2:
27:         raise ValueError("direction_names must be a tuple of length 2")
28:
29:     above_name, below_name = direction_names
30:
31:     events = []
32:     prev_side = None
33:     in_run = False
34:     run_entry_side = None
35:     run_start = None  # index where the current run started (for penetration calculation)
36:
37:     for i, rsi_val in enumerate(rsi):
38:         if rsi_val is None:
39:             continue
40:
41:         # Classify the current bar
42:         lower_bound = level - tolerance
43:         upper_bound = level + tolerance
44:
45:         if rsi_val > upper_bound:
46:             side = above_name
47:         elif rsi_val < lower_bound:
48:             side = below_name
49:         else:
50:             side = "band"
51:
52:         if side == "band":
53:             # If we're not already in a run, start one
54:             if not in_run:
55:                 in_run = True
56:                 run_entry_side = prev_side
57:                 run_start = i
58:             continue  # Do not update prev_side while in the band
59:
60:         else:  # side is either above_name or below_name
61:             # If we were in a run, this bar closes it. A run resolution is never also a
62:             # cross: the band run is what a same-bar band-skip ("cross") explicitly excludes
63:             # ("no band run in between"), so the two are mutually exclusive per bar.
64:             if in_run:
65:                 in_run = False
66:
67:                 # Emit event based on entry side and exit side
68:                 if run_entry_side is not None:
69:                     if side == run_entry_side:
70:                         event_type = "support" if side == above_name else "rejection"
71:                         # support/rejection: deepest dip into the band over the run's band bars.
72:                         penetration = 0.0
73:                         for j in range(run_start, i):
74:                             if rsi[j] is not None:
75:                                 dist = abs(rsi[j] - level)
76:                                 penetration = max(penetration, dist)
77:                     else:
78:                         event_type = "failure"
79:                         # failure: how far past the level the resolving bar closed.
80:                         penetration = abs(rsi_val - level)
81:
82:                     events.append({
83:                         "t": ts[i],
84:                         "event": event_type,
85:                         "level_value": level,
86:                         "tolerance_used": tolerance,
87:                         "penetration": penetration
88:                     })
89:             elif prev_side is not None and prev_side != side:
90:                 # Direct side-to-side flip with no band run in between: a cross.
91:                 events.append({
92:                     "t": ts[i],
93:                     "event": "cross",
94:                     "level_value": level,
95:                     "tolerance_used": tolerance,
96:                     "penetration": abs(rsi_val - level),
97:                     "direction": "up" if side == above_name else "down"
98:                 })
99:
100:             # Update prev_side for next iteration
101:             prev_side = side
102:
103:     return events
```

## E03

### MyTradingSys/research/non_core_layer_audit_2026-10-12/reproductions.json

SHA-256: `adc55ec5d1d9a206d97b565ee7df4f497931fa7968ecf4118d458de3407fab00`

```text
1: {
2:   "head": "99b43fd6d7344d86b158c2ddf4e443b14d6ea690",
3:   "rsi_hand_example": {
4:     "closes": [
5:       10,
6:       12,
7:       11,
8:       14,
9:       13
10:     ],
11:     "period": 3,
12:     "expected_seed": 83.33333333333333,
13:     "expected_next": 66.66666666666666,
14:     "actual": [
15:       null,
16:       null,
17:       null,
18:       83.33333333333334,
19:       66.66666666666667
20:     ]
21:   },
22:   "regime_value_mismatch": {
23:     "input": [
24:       65.0,
25:       65.0,
26:       65.0,
27:       65.0,
28:       65.0,
29:       65.0,
30:       65.0,
31:       65.0,
32:       65.0,
33:       65.0,
34:       65.0,
35:       65.0,
36:       65.0,
37:       65.0,
38:       65.0,
39:       65.0,
40:       65.0,
41:       65.0,
42:       65.0,
43:       45.0
44:     ],
45:     "latest_rsi": 45,
46:     "computed_regime": "BULL",
47:     "meaning": "BULL is possible with current RSI 45; not equivalent to current RSI >60."
48:   },
49:   "state_asof_contract": {
50:     "open_times": [
51:       0
52:     ],
53:     "value": [
54:       "BULL"
55:     ],
56:     "query": 1,
57:     "actual": "BULL",
58:     "meaning": "No close-time enforcement inside helper; caller must pass availability times."
59:   },
60:   "gapped_resample": [
61:     {
62:       "t": 0,
63:       "o": 100,
64:       "h": 101,
65:       "l": 99,
66:       "c": 100,
67:       "v": 4,
68:       "gap_count": 1,
69:       "n_bars": 4
70:     }
71:   ],
72:   "summary_recount": {
73:     "summary.json": {
74:       "timeframes": 19,
75:       "cells": 76,
76:       "verdicts": {
77:         "no edge": 32,
78:         "insufficient n": 44
79:       },
80:       "eligible": 32,
81:       "eligible_negative_net": 31,
82:       "report_reproduced_exactly": true,
83:       "eligible_positive_net": [
84:         [
85:           "1h",
86:           "operator",
87:           "bearish",
88:           {
89:             "n": 332,
90:             "gross_mean": 0.0013839767483132374,
91:             "net_mean": 0.00038397674831323723,
92:             "net_t": 0.38819799331819654,
93:             "hit_net": 0.5271084337349398,
94:             "baseline_side": -0.00027762759599041784
95:           }
96:         ]
97:       ]
98:     },
99:     "summary_T088.json": {
100:       "timeframes": 4,
101:       "cells": 16,
102:       "verdicts": {
103:         "no edge": 4,
104:         "insufficient n": 12
105:       },
106:       "eligible": 4,
107:       "eligible_negative_net": 4,
108:       "report_reproduced_exactly": true,
109:       "eligible_positive_net": []
110:     }
111:   },
112:   "indicator_named_implementation_paths": {
113:     "refs_checked": [
114:       "refs/heads/fast-track",
115:       "refs/heads/fast-track-old",
116:       "refs/heads/fast-track-work",
117:       "refs/heads/jis-nuc/b172-tokens",
118:       "refs/heads/jis-nuc/codex-lab",
119:       "refs/heads/jis-nuc/codex-layer-lab",
120:       "refs/heads/jis-nuc/owner-card",
121:       "refs/heads/jis-nuc/relay",
122:       "refs/heads/jisnb/cloud-backtest-findings",
123:       "refs/heads/jisnb/dsa",
124:       "refs/heads/jisnb/refiner-lab",
125:       "refs/heads/jisnb/tom-fabio-guidance",
126:       "refs/heads/jisnuc/t092",
127:       "refs/heads/nuc/codex-first",
128:       "refs/heads/nuc/codex-holdout",
129:       "refs/heads/wf-pending",
130:       "refs/remotes/origin/HEAD",
131:       "refs/remotes/origin/backup/JIS-NB/BinanceDataFeed",
132:       "refs/remotes/origin/backup/JIS-NB/BinanceDataFeed.registry",
133:       "refs/remotes/origin/backup/JIS-NB/mts-cc",
134:       "refs/remotes/origin/backup/JIS-NB/mts-cicd",
135:       "refs/remotes/origin/backup/JIS-NB/mts-control-room",
136:       "refs/remotes/origin/backup/JIS-NB/mts-dsa",
137:       "refs/remotes/origin/backup/JIS-NB/mts-extract",
138:       "refs/remotes/origin/backup/JIS-NB/mts-inbox",
139:       "refs/remotes/origin/backup/JIS-NB/mts-live-reads",
140:       "refs/remotes/origin/backup/JIS-NB/mts-malkan",
141:       "refs/remotes/origin/backup/JIS-NB/mts-missed-trades",
142:       "refs/remotes/origin/backup/JIS-NB/mts-ops",
143:       "refs/remotes/origin/backup/JIS-NB/mts-push",
144:       "refs/remotes/origin/backup/JIS-NB/mts-registry",
145:       "refs/remotes/origin/backup/JIS-NB/mts-relay",
146:       "refs/remotes/origin/backup/JIS-NB/mts-relay-20261010T0027",
147:       "refs/remotes/origin/backup/JIS-NB/mts-relay-20261010T0627Z",
148:       "refs/remotes/origin/backup/JIS-NB/mts-research",
149:       "refs/remotes/origin/backup/JIS-NB/mts-rsi",
150:       "refs/remotes/origin/backup/JIS-NB/mts-shots",
151:       "refs/remotes/origin/backup/JIS-NB/mts-sup",
152:       "refs/remotes/origin/backup/JIS-NB/mts-t080",
153:       "refs/remotes/origin/backup/JIS-NB/mts-t081",
154:       "refs/remotes/origin/backup/JIS-NB/mts-task",
155:       "refs/remotes/origin/backup/JIS-NB/mts-tom",
156:       "refs/remotes/origin/backup/JIS-NB/mts-vpa",
157:       "refs/remotes/origin/backup/live-tree-2026-10-09",
158:       "refs/remotes/origin/claude/auto-merge-fast-track",
159:       "refs/remotes/origin/claude/cbp-trade-inputs-eosfz8",
160:       "refs/remotes/origin/claude/ci-offline-gate",
161:       "refs/remotes/origin/claude/consensus-tf-maps-eomuv3",
162:       "refs/remotes/origin/claude/dazzling-volta-ry933w",
163:       "refs/remotes/origin/claude/engine-tests-8y0yqm",
164:       "refs/remotes/origin/claude/fabio-v3-core-dtn9bf",
165:       "refs/remotes/origin/claude/fast-track-consolidation-phshp6",
166:       "refs/remotes/origin/claude/fix-book-imbalance-no-data-eo55st",
167:       "refs/remotes/origin/claude/formula-audit-xmj7t4",
168:       "refs/remotes/origin/claude/lucid-rubin-6q47un",
169:       "refs/remotes/origin/claude/mts-launcher-verbs-37cows",
170:       "refs/remotes/origin/claude/nifty-euler-6i4g40",
171:       "refs/remotes/origin/claude/project-thread-5v1jht",
172:       "refs/remotes/origin/claude/project-thread-7gvyfy",
173:       "refs/remotes/origin/claude/project-thread-a5n5nk",
174:       "refs/remotes/origin/claude/project-thread-mvbseb",
175:       "refs/remotes/origin/claude/project-thread-vi37ux",
176:       "refs/remotes/origin/claude/quirky-knuth-y2u3ij",
177:       "refs/remotes/origin/claude/sharp-allen-k7m4ap",
178:       "refs/remotes/origin/claude/sleepy-pasteur-mbcxe5",
179:       "refs/remotes/origin/claude/trusting-meitner-nsjwsm",
180:       "refs/remotes/origin/claude/wave1-review-gate-myacv5",
181:       "refs/remotes/origin/claude/wizardly-babbage-3098i5",
182:       "refs/remotes/origin/claude/zealous-cannon-ehyvh3",
183:       "refs/remotes/origin/cloud/work",
184:       "refs/remotes/origin/fast-track",
185:       "refs/remotes/origin/fix/dsa-prompt-cbp-path",
186:       "refs/remotes/origin/green/fast-track",
187:       "refs/remotes/origin/jisnb/rsi-kurisko-2026-10-09",
188:       "refs/remotes/origin/jisnb/vp-anchored-2026-10-09",
189:       "refs/remotes/origin/main",
190:       "refs/remotes/origin/research/agenda-2026-10-06",
191:       "refs/remotes/origin/research/agenda-registry-2026-10-06"
192:     ],
193:     "hits": {},
194:     "limit": "Named paths only; current code text searched separately."
195:   },
196:   "mirror": {
197:     "utc": "2026-10-11T20:09:30.734919+00:00",
198:     "git_head": "927665a",
199:     "rows": 3961,
200:     "events": {
201:       "trade_attempt": 698,
202:       "start": 72,
203:       "signal_rejected": 499,
204:       "skipped_busy": 111,
205:       "trade_closed": 682,
206:       "ledger_row": 680,
207:       "skipped_auto_pause": 3,
208:       "adopted": 35,
209:       "manager_lost": 25,
210:       "manager_exit_unverified": 20,
211:       "skipped_halt": 987,
212:       "layer_trade_blocked": 148,
213:       "fabio_account_missing": 1
214:     },
215:     "closed_by_source": {
216:       "layer:rsi:rsi_events:15m": 13,
217:       "smoke": 1,
218:       "layer:turn_of_candle:turn_of_candle:1m": 548,
219:       "layer:rsi:rsi_events:5m": 48,
220:       "layer:session:session_momentum:15m": 5,
221:       "layer:rsi:rsi_events:1h": 4,
222:       "tom": 7,
223:       "layer:fabio:escalation:15m": 6,
224:       "layer:fabio:cvd_absorption:15m": 17,
225:       "layer:cryptocred:sr_flip:15m": 19,
226:       "layer:fabio:cvd_absorption:1h": 2,
227:       "layer:cryptocred:fib_pullback:15m": 7,
228:       "layer:fabio:volume_fvg:15m": 2,
229:       "layer:cryptocred:sr_flip:1h": 2,
230:       "layer:cryptocred:failed_msb:15m": 1
231:     },
232:     "closed_exit_reasons": {
233:       "UNKNOWN": 682
234:     },
235:     "limitation": "Mirrored auto_trades log, not canonical trade ledger; not live and not deduplicated P/L evidence."
236:   }
237: }
```

### MyTradingSys/research/non_core_layer_audit_2026-10-12/test_results.json

SHA-256: `8d37dfc30e47ba2e77b104e559b9c1d9448b3a45d1fb6bfe653c3913d5db1745`

```text
1: {
2:   "rsi": {
3:     "modules": [
4:       "MyTradingSys.backtest.layers.rsi.test_malkan_40_60",
5:       "MyTradingSys.backtest.layers.rsi.test_malkan_mtf",
6:       "MyTradingSys.backtest.layers.rsi.test_observation",
7:       "MyTradingSys.backtest.layers.rsi.test_rsi_core_ma",
8:       "MyTradingSys.backtest.layers.rsi.test_rsi_divergence",
9:       "MyTradingSys.backtest.layers.rsi.test_rsi_events",
10:       "MyTradingSys.backtest.layers.rsi.test_rsi_ma_events",
11:       "MyTradingSys.backtest.layers.rsi.test_rsi_reclaim",
12:       "MyTradingSys.backtest.layers.rsi.test_run_divergence_mtf",
13:       "MyTradingSys.backtest.layers.rsi.test_run_rsi_backtest"
14:     ],
15:     "run": 134,
16:     "failures": 0,
17:     "errors": 0,
18:     "skipped": 0,
19:     "passed": true
20:   },
21:   "timeframe": {
22:     "modules": [
23:       "MyTradingSys.backtest.layers.timeframe.test_tf_resample"
24:     ],
25:     "run": 18,
26:     "failures": 0,
27:     "errors": 0,
28:     "skipped": 0,
29:     "passed": true
30:   },
31:   "cryptocred": {
32:     "modules": [
33:       "MyTradingSys.backtest.layers.cryptocred.test_cc_bt_adapter",
34:       "MyTradingSys.backtest.layers.cryptocred.test_cc_range_noise_live_neutrality",
35:       "MyTradingSys.backtest.layers.cryptocred.test_cc_retest",
36:       "MyTradingSys.backtest.layers.cryptocred.test_cc_setups",
37:       "MyTradingSys.backtest.layers.cryptocred.test_cc_structure",
38:       "MyTradingSys.backtest.layers.cryptocred.test_run_cc_setups"
39:     ],
40:     "run": 69,
41:     "failures": 0,
42:     "errors": 0,
43:     "skipped": 1,
44:     "passed": true
45:   },
46:   "positioning": {
47:     "modules": [
48:       "MyTradingSys.backtest.layers.positioning.test_funding_cvd_fade",
49:       "MyTradingSys.backtest.layers.positioning.test_trade_costs"
50:     ],
51:     "run": 21,
52:     "failures": 0,
53:     "errors": 0,
54:     "skipped": 0,
55:     "passed": true
56:   },
57:   "session": {
58:     "modules": [
59:       "MyTradingSys.backtest.layers.session.test_session_momentum"
60:     ],
61:     "run": 9,
62:     "failures": 0,
63:     "errors": 0,
64:     "skipped": 0,
65:     "passed": true
66:   },
67:   "turn_of_candle": {
68:     "modules": [
69:       "MyTradingSys.backtest.layers.turn_of_candle.test_turn_of_candle",
70:       "MyTradingSys.backtest.layers.turn_of_candle.test_turn_of_candle_edge"
71:     ],
72:     "run": 36,
73:     "failures": 0,
74:     "errors": 0,
75:     "skipped": 0,
76:     "passed": true
77:   },
78:   "session_levels": {
79:     "modules": [
80:       "MyTradingSys.backtest.layers.session_levels.test_session_levels"
81:     ],
82:     "run": 13,
83:     "failures": 0,
84:     "errors": 0,
85:     "skipped": 0,
86:     "passed": true
87:   },
88:   "tick": {
89:     "modules": [
90:       "MyTradingSys.backtest.layers.tick.test_tick_extremes",
91:       "MyTradingSys.backtest.layers.tick.test_tick_flagger",
92:       "MyTradingSys.backtest.layers.tick.test_tick_oi_extremes"
93:     ],
94:     "run": 49,
95:     "failures": 0,
96:     "errors": 0,
97:     "skipped": 0,
98:     "passed": true
99:   },
100:   "consensus": {
101:     "modules": [
102:       "MyTradingSys.backtest.layers.consensus.test_hook",
103:       "MyTradingSys.backtest.layers.consensus.test_writer"
104:     ],
105:     "run": 52,
106:     "failures": 0,
107:     "errors": 0,
108:     "skipped": 0,
109:     "passed": true
110:   },
111:   "alerts": {
112:     "modules": [
113:       "MyTradingSys.backtest.layers.alerts.test_alert_emitter",
114:       "MyTradingSys.backtest.layers.alerts.test_live_runner_cli",
115:       "MyTradingSys.backtest.layers.alerts.test_live_runner_core",
116:       "MyTradingSys.backtest.layers.alerts.test_live_runner_fresh",
117:       "MyTradingSys.backtest.layers.alerts.test_live_runner_lag",
118:       "MyTradingSys.backtest.layers.alerts.test_live_runner_layers",
119:       "MyTradingSys.backtest.layers.alerts.test_live_runner_of_feed",
120:       "MyTradingSys.backtest.layers.alerts.test_live_runner_v3_shadow",
121:       "MyTradingSys.backtest.layers.alerts.test_live_runner_wiring",
122:       "MyTradingSys.backtest.layers.alerts.test_live_toc_tfs"
123:     ],
124:     "run": 104,
125:     "failures": 0,
126:     "errors": 0,
127:     "skipped": 0,
128:     "passed": true
129:   }
130: }
```

## E04

### MyTradingSys/backtest/layers/alerts/live_layers.py

SHA-256: `2354186bfa795deebd57017e166e3adb956ef681c1e0b95fb612935d05681562`

```text
1: """
2: Adapters that turn already-built layer modules into live-runner layer functions `fn(bars) -> [event]`.
3:
4: Every event returned here has:
5:   "t"     bar OPEN time (ms) of the signal bar (live_runner_core/alert_emitter turn it into "t_close")
6:   "event" a name that is unique per (t, distinct signal) - alert_emitter dedups on (t, event)
7:   "side"  "long" | "short", derived from the layer's own event semantics (mapping documented per adapter)
8: The auto-trader trades any alert with a "side" field. Alert-only: no orders, no keys, stdlib only.
9: Bars are closed Binance klines {t,o,h,l,c,v,tbv}. Parameters are the module defaults or the values
10: the backtests used (cited per adapter).
11: """
12:
13: import json
14: import urllib.parse
15: import urllib.request
16:
17: from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
18: from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
19: from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import turn_of_candle_events
20: from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull, malkan_setup_bear
21: from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events
22: from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (
23:     swing_legs, build_profile, value_area, lowest_volume_level,
24: )
25: from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events
26: from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import funding_cvd_fade_events
27: from MyTradingSys.backtest.layers.cryptocred.cc_setups import (
28:     setup1_sr_flip, setup2_fib_pullback, setup3_failed_msb_reversal,
29: )
30:
31:
32: def escalation_layer(bars):
33:     """Side = the module's own: breakout in the aggressor's direction (up -> long, down -> short).
34:     Params: module defaults (left/right 2, tol 0.001, k 2.0, lookback 20; run_backtest ESCALATION_GRID includes them)."""
35:     out = []
36:     for e in escalation_events(bars):
37:         out.append({**e, "t": bars[e["i"]]["t"], "event": "%s_%s_%s" % (e["kind"], e["side"], e["level_price"])})
38:     return out
39:
40:
41: def volume_fvg_layer(bars, n_bins=20):
42:     """Mirrors fabio/run_backtest.py run_fvg (real lowest-volume level in the 70% value area of each swing leg;
43:     first touch of that level within 200 bars of leg confirmation). Side as in the backtest: price at leg
44:     confirmation above the level -> "short", else "long". n_bins=20, VA 70% = backtest values."""
45:     legs = swing_legs(bars, left=2, right=2, use_body=True)
46:     closes = [b["c"] for b in bars]
47:     out = []
48:     for leg in legs:
49:         a_i, b_i = min(leg["a_i"], leg["b_i"]), max(leg["a_i"], leg["b_i"])
50:         if b_i - a_i < n_bins:
51:             continue
52:         try:
53:             profile = build_profile(bars, a_i, b_i, n_bins=n_bins)
54:             lvl = lowest_volume_level(profile, value_area(profile, pct=0.70))
55:         except ValueError:
56:             continue
57:         start = leg["confirmed_i"]
58:         mid = (lvl["price_lo"] + lvl["price_hi"]) / 2.0
59:         for i in range(start, min(start + 200, len(bars) - 1)):
60:             if bars[i]["l"] <= mid <= bars[i]["h"]:
61:                 side = "short" if closes[start] > mid else "long"
62:                 out.append({"t": bars[i]["t"], "side": side, "level": round(mid, 2),
63:                             "event": "fvg_touch_%s_%s" % (side, round(mid, 2))})
64:                 break
65:     return sorted(out, key=lambda e: e["t"])
66:
67:
68: def session_momentum_layer(bars):
69:     """15m bars. Side = sign of the first-30-min return of the UTC day (>0 long, <0 short), entered on the
70:     bar closing at +30 min. Params: module defaults (session_start 0, first_min 30, entry_min 30, min_abs 0),
71:     bar_min=15 to match the tf. Source: Shen/Urquhart/Wang 2022 (module docstring)."""
72:     out = []
73:     for e in session_momentum_events(bars, bar_min=15):
74:         out.append({"t": bars[e["i"]]["t"], "side": e["side"], "r_first": e["r_first"],
75:                     "event": "session_momentum"})
76:     return out
77:
78:
79: def default_fetch_funding(symbol, limit):
80:     """Public GET fapi/v1/fundingRate -> [(fundingTime_ms, rate_float)] ascending. Real network; not unit-tested."""
81:     url = "https://fapi.binance.com/fapi/v1/fundingRate?" + urllib.parse.urlencode(
82:         {"symbol": symbol, "limit": limit})
83:     with urllib.request.urlopen(url, timeout=10) as resp:
84:         raw = json.loads(resp.read())
85:     return sorted((int(r["fundingTime"]), float(r["fundingRate"])) for r in raw)
86:
87:
88: def make_funding_layer(fetch_funding=None, symbol="BTCUSDT", limit=200):
89:     """1h bars. Side fades the crowded side: bearish CVD/price divergence + funding percentile >= 0.95 -> short;
90:     bullish divergence + percentile <= 0.05 -> long. Params: module defaults (lookback 90, n 20, hi .95, lo .05)."""
91:     fetch = fetch_funding or default_fetch_funding
92:
93:     def fn(bars):
94:         funding = fetch(symbol, limit)
95:         out = []
96:         for e in funding_cvd_fade_events(bars, funding):
97:             out.append({"t": bars[e["i"]]["t"], "side": e["side"], "funding_pct": e["funding_pct"],
98:                         "event": "funding_fade_%s" % e["div"]})
99:         return out
100:     return fn
101:
102:
103: def _malkan_signals(bars, fn, event_name):
104:     if len(bars) <= 14:  # rsi_core needs period+1 closes; too few bars = no events, not an error
105:         return []
106:     rsi = rsi_core([b["c"] for b in bars], period=14)
107:     regime = malkan_regime(rsi)
108:     return [{**s, "event": event_name} for s in fn(bars, rsi, regime)]
109:
110:
111: def malkan_bull_layer(bars):
112:     """1h. MLK-S1: RSI support bounce at 40 in a BULL regime with a bullish candle -> long. Module defaults
113:     (tolerance 2.0, regime lookback 20, RSI period 14)."""
114:     return _malkan_signals(bars, malkan_setup_bull, "malkan_support")
115:
116:
117: def malkan_bear_layer(bars):
118:     """1h. MLK-S2: RSI rejection at 60 in a BEAR regime with a bearish candle -> short. Module defaults."""
119:     return _malkan_signals(bars, malkan_setup_bear, "malkan_resistance")
120:
121:
122: def _cc_layer(setup_fn, name):
123:     """1h. Side = the setup's own signal side (long/short); entry_t is the entry trigger bar's open time.
124:     Params: module defaults (the BACKTEST_L1_REPORT runs used defaults on 1h bars)."""
125:     def fn(bars):
126:         try:
127:             signals = setup_fn(bars)
128:         except ValueError as exc:
129:             if "must not be empty" in str(exc):  # no swings yet (too few bars) = no events, not an error
130:                 return []
131:             raise
132:         return [{"t": s["entry_t"], "side": s["side"], "event": "%s_%s" % (name, s["side"]),
133:                  "entry_price": s["entry_price"], "stop": s["stop"]} for s in signals]
134:     return fn
135:
136:
137: cc_sr_flip_layer = _cc_layer(setup1_sr_flip, "sr_flip")
138: cc_fib_pullback_layer = _cc_layer(setup2_fib_pullback, "fib_pullback")
139: cc_failed_msb_layer = _cc_layer(setup3_failed_msb_reversal, "failed_msb")
140:
141:
142: RSI_LEVEL = 40.0
143: RSI_TOL = 0.5
144:
145:
146: def rsi_level_layer(bars):
147:     """1h/15m RSI(14) level events at 40 +/- 0.5 (unchanged detector: rsi_events). Side only on "failure":
148:     a failure is a band run whose resolving bar closed on the OPPOSITE side of the run's entry side
149:     (rsi_events.py; rsi/TEST_PLAN.md), so the entry side is the opposite of the resolving bar's side, and that side
150:     is readable from the RSI value at the event bar (t = resolving bar; rsi > level+tol / < level-tol always holds
151:     there). Resolved below -> the run came from above (support from above failed) -> "short"; resolved above -> came
152:     from below (resistance from below failed) -> "long". support / rejection / cross keep NO side (alert-only)."""
153:     closes = [b["c"] for b in bars]
154:     ts = [b["t"] for b in bars]
155:     rsi = rsi_core(closes, period=14)
156:     idx = {t: i for i, t in enumerate(ts)}
157:     out = []
158:     for e in rsi_events(rsi, ts, level=RSI_LEVEL, tolerance=RSI_TOL):
159:         if e["event"] == "failure":
160:             v = rsi[idx[e["t"]]]
161:             if v is not None and v < RSI_LEVEL - RSI_TOL:
162:                 e = {**e, "side": "short"}
163:             elif v is not None and v > RSI_LEVEL + RSI_TOL:
164:                 e = {**e, "side": "long"}
165:         out.append(e)
166:     return out
167:
168:
169: def turn_of_candle_layer(bars):
170:     """1m bars. Candidate C3 (T055, FORMULAS.md sec 16): one event per quarter hour at minute-of-quarter 14
171:     (lead_minutes=1, entry at that bar's close, just before the 15m candle opens). Side (operator 2026-09-30,
172:     data collection): sign of the opening taker-buy imbalance (2*tbv - v)/v of the SAME quarter's minute-0 bar,
173:     as in run_t055_c3_imbalance.py imbalance_events(window=1, direction="mom"): > 0 long, < 0 short, 0 / no volume /
174:     missing minute-0 bar -> NO side. "sampling": True marks a no-edge layer traded only to collect fills
175:     (T055_BT_c3.md: no gross edge); never a Tom filter."""
176:     out = []
177:     for e in turn_of_candle_events(bars, lead_minutes=1):
178:         i = e["i"]
179:         ev = {"t": bars[i]["t"], "event": "toc_m14", "sampling": True}
180:         o = i - 14
181:         if o >= 0 and bars[i]["t"] - bars[o]["t"] == 14 * 60000 and bars[o]["v"] > 0:
182:             imb = (2 * bars[o]["tbv"] - bars[o]["v"]) / bars[o]["v"]
183:             ev["imbalance"] = round(imb, 6)
184:             if imb > 0:
185:                 ev["side"] = "long"
186:             elif imb < 0:
187:                 ev["side"] = "short"
188:         out.append(ev)
189:     return out
```

## E05

### MyTradingSys/execution/auto_trader.py

SHA-256: `9f7a5201affa81d281f7db906d3c40822c0559a78608a6156dfe302453a679f9`

```text
1: """Auto-trader for Deribit TESTNET: turns live signals into plans and trades them with the existing tools.
2:
3: Operator order 2026-09-29: "start trading now on test-net based on what we have functional, and on every build
4: launch fresh trades for newly built layers." This is an ORCHESTRATOR only. Every order goes through the same gated
5: path the operator uses by hand:
6:     new_plan.py --yes  ->  executor.py <plan> --go  ->  position_manager.py <plan_id>
7: so the HALT files, the R8 one-position preflight, the account cap and the fail-closed paths all still apply.
8: It never talks to the exchange itself and has no mainnet path (the executor is testnet-only).
9:
10: Signal sources (read-only):
11:   - Tom core: runtime_data/last_alert.json (verdict SETUP_FORMING / SETUP_CONFIRMED, with ENTRY/STOP/TARGET).
12:   - Indicator layers: MyTradingSys/runtime/alerts/<tf>.jsonl written by the live alert runner. Any NEW layer that
13:     the runner emits is picked up automatically if its event maps to a side (config "layer_rules", or a "side"
14:     field on the alert). Unknown layer/event pairs are logged as "unmapped" so the supervisor can add a rule.
15: Priority when several signals are new: Tom first, then layers in arrival order. One trade at a time (the account
16: has one BTC-PERPETUAL position); signals that arrive while a trade is open are logged as skipped_busy, so every
17: layer still gets a signal count for later scoring.
18:
19: Every decision is appended to MyTradingSys/execution/auto_trades.jsonl (source, signal, plan_id, outcome).
20: Usage (repo root):  python -m MyTradingSys.execution.auto_trader [--once] [--dry-run] [--poll-seconds 20]
21: Stop it with Ctrl+C or by creating execution/HALT (mts pause); it then trades nothing until the brake is removed.
22: To pause ONLY the auto-trader (e.g. while a testnet suite needs a flat account), create execution/AUTO_PAUSE.
23: """
24: import argparse
25: import json
26: import math
27: import os
28: import re
29: import subprocess
30: import sys
31: import time
32: from datetime import datetime, timezone
33: from pathlib import Path
34:
35: HERE = Path(__file__).resolve().parent
36: REPO = HERE.parents[1]
37: # Single source of the net_rr floor: MyTradingSys/system/net_rr_floor.json (MTS_REPO_ROOT is set by run_staged_tests.py).
38: sys.path.append(str(Path(os.environ.get("MTS_REPO_ROOT") or REPO) / "MyTradingSys" / "runtime"))
39: from net_rr_floor import NetRrFloorError, load_floor  # noqa: E402
40: HALT = HERE / "HALT"
41: HALT_DAILY_LOSS = HERE / "HALT_DAILY_LOSS"
42: # Auto-trader-only pause: no new auto-trades, but no HALT (so manual trades and the testnet suites still run).
43: AUTO_PAUSE = HERE / "AUTO_PAUSE"
44: STATE_PATH = HERE / "auto_trader_state.json"
45: LOG_PATH = HERE / "auto_trades.jsonl"
46: MANAGER_LOG_DIR = HERE / "journal" / "auto_manager_logs"
47: OPERATOR_ALERTS = HERE / "OPERATOR_ALERTS.log"
48: MAX_RESPAWNS = 3   # position_manager respawns per plan when it exits while the exchange still shows a position
49: TOM_ALERT = REPO / "runtime_data" / "last_alert.json"
50: LAYER_ALERT_DIR = REPO / "MyTradingSys" / "runtime" / "alerts"
51:
52: TF_SECONDS = {"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "1d": 86400}
53:
54: DEFAULT_CONFIG = {
55:     # Tom core: limit at the zone, stop/target from the alert. Whole size off at the target, or (R2) the
56:     # runner_leg_pct share on RUNNER_TARGET when the card carries one.
57:     # TF5 (EXEC_PROVENANCE_AUDIT H5 E1b, E2): max_hold_minutes is one flat time exit (no zone-TF scaling; None = no
58:     # time exit) and max_entry_seconds is the limit wait passed to executor --max-entry-seconds. Both NO-SOURCE testnet
59:     # defaults kept at the values the live path already used (120 = the old 15m fallback, 600 = executor default);
60:     # MEASURE (operator Ruling 3, pending).
61:     "tom": {"enabled": True, "size_usd": 200, "max_loss_usd": 25, "hours": 1.0, "max_hold_minutes": 120,
62:             "max_entry_seconds": 600, "max_age_seconds": 300,
63:             "verdicts": ["SETUP_FORMING", "SETUP_CONFIRMED"],   # net_rr floor is net_rr_floor.json, not a config key
64:             # R2: share of size on the runner leg (RUNNER_TARGET); the rest exits at TARGET and the stop moves to
65:             # breakeven when that first leg fills. NO-SOURCE testnet default (operator Ruling 2, 2026-10-03; BE
66:             # concept: Fabio P21 "I put my stop loss to break even"). 0 = off = single target, as before.
67:             "runner_leg_pct": 50},
68:     # Layers have no stop/target of their own: fixed bracket, market entry, small size. B118: stop_pct, targets, size,
69:     # hours, max_age_bars and max_hold_bars are NO-SOURCE (no trader quote); bracket_source labels every layer log row
70:     # SAMPLING (trades exist to sample layer behaviour, the values are not tuned or claimed).
71:     "layers": {"enabled": True, "size_usd": 100, "max_loss_usd": 10, "stop_pct": 1.0, "targets": "2",
72:                "bracket_source": "SAMPLING",
73:                "hours": 2.0, "max_age_bars": 1.2,
74:                "max_hold_bars": 8},   # time exit = 8 bars of the signal timeframe (minutes derived per alert tf)
75:     # (layer, event) -> side. "direction" means: up -> long, down -> short; "level" means the side comes from the level
76:     # crossed (CROSS_SIDE_BY_LEVEL), everything else unmapped. A "side" field on the alert wins.
77:     "layer_rules": {
78:         "rsi:support": "long",
79:         "rsi:rejection": "short",
80:         "rsi:cross": "level",
81:     },
82:     "disabled_layers": [],
83:     # source prefix -> named testnet account (credentials .secrets/testnet_<label>.secret.json).
84:     # Missing file -> shared default slot, exactly as before.
85:     "accounts": {"layer:fabio:": "fabio"},
86:     # Layer source prefixes that keep emitting alerts (data collection) but never place a trade, with the reason per
87:     # prefix. Tom ("tom") is never matched. Missing key = nothing blocked; a PRESENT but malformed key, or an unreadable /
88:     # missing config file, blocks ALL layer trades (fail closed) - see trade_block_reason / load_config.
89:     "trade_blocklist": [],
90:     "trade_blocklist_reasons": {},
91:     # Layer source prefix -> {"size_usd", "max_loss_usd"}; the longest matching prefix replaces the layers size and max
92:     # loss. Testnet calibration spread (operator 2026-10-07: "Use amounts ranging from 20 to 1000 $"). A malformed
93:     # entry rejects the signal (no order at a guessed size).
94:     "size_overrides": {},
95: }
96: SECRETS_DIR = HERE / ".secrets"
97: _warned_missing = set()
98:
99:
100: def now_utc() -> datetime:
101:     return datetime.now(timezone.utc)
102:
103:
104: def log(event: dict, path: Path = None) -> None:
105:     event = {"ts": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), **event}
106:     with open(path or LOG_PATH, "a", encoding="utf-8", newline="\n") as f:
107:         f.write(json.dumps(event) + "\n")
108:     print(json.dumps(event), flush=True)
109:
110:
111: def load_json(path: Path, default):
112:     try:
113:         return json.loads(path.read_text(encoding="utf-8"))
114:     except (OSError, ValueError):
115:         return default
116:
117:
118: def save_json(path: Path, data) -> None:
119:     tmp = path.with_suffix(path.suffix + ".tmp")
120:     tmp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
121:     tmp.replace(path)
122:
123:
124: # ---------------------------------------------------------------- Tom core signal
125:
126: CARD_FIELD = re.compile(r"^(VERDICT|TIME|PRICE|SETUP|ZONE|ENTRY|STOP|TARGET|RUNNER_TARGET|R:R):\s*(.*)$", re.M)
127: ALERT_NO = re.compile(r"#(\d+)")
128:
129:
130: def _positive_float(raw):
131:     """Card field (RUNNER_TARGET, PRICE) -> positive finite float, or None (absent, 0 = none, or unparsable)."""
132:     try:
133:         v = float(raw)
134:     except (TypeError, ValueError):
135:         return None
136:     return v if math.isfinite(v) and v > 0 else None
137:
138:
139: def parse_tom_alert(alert: dict) -> dict:
140:     """Return {'alert_no','verdict','time','price','setup','side','entry','stop','target','runner_target','net_rr'}
141:     or {} if unusable. runner_target is None when the card carries no (valid) RUNNER_TARGET line; price (the
142:     engine's market read, card PRICE line, PS1 Build-Card) is None when absent or unparsable."""
143:     card = alert.get("card_text") or ""
144:     fields = {k: v.strip() for k, v in CARD_FIELD.findall(card)}
145:     m = ALERT_NO.search(alert.get("title") or "")
146:     try:
147:         entry, stop, target = float(fields["ENTRY"]), float(fields["STOP"]), float(fields["TARGET"])
148:     except (KeyError, ValueError):
149:         return {}
150:     setup = fields.get("SETUP", "")
151:     side = "long" if setup.endswith("_long") else "short" if setup.endswith("_short") else None
152:     rr = re.search(r"net\s+([0-9.]+)", fields.get("R:R", ""))
153:     return {"alert_no": int(m.group(1)) if m else None, "verdict": fields.get("VERDICT", ""),
154:             "time": fields.get("TIME", ""), "price": _positive_float(fields.get("PRICE")),
155:             "setup": setup, "side": side, "entry": entry, "stop": stop,
156:             "target": target, "runner_target": _positive_float(fields.get("RUNNER_TARGET")),
157:             "net_rr": float(rr.group(1)) if rr else None}
158:
159:
160: def runner_split(p: dict, c: dict):
161:     """R2 leg split for a Tom alert -> (targets_arg, None) for 'near@pct,runner@pct', or (None, reason).
162:     Share of size sent to the runner leg = c['runner_leg_pct'] (NO-SOURCE testnet default 50, operator Ruling 2;
163:     0 disables). Fails closed to the single-target plan: no runner, runner not beyond TARGET, a leg that
164:     would floor below the 10 USD contract minimum, or legs that do not sum to the size (TF5 E3: the compiler floors
165:     each leg to 10 USD on its own, PC:266, so size 30 at 50/50 would leave 10 USD with no target)."""
166:     pct = c.get("runner_leg_pct") or 0
167:     if pct <= 0:
168:         return None, "runner_leg_pct off"
169:     runner = p.get("runner_target")
170:     if runner is None:
171:         return None, "no RUNNER_TARGET"
172:     beyond = runner > p["target"] if p["side"] == "long" else runner < p["target"]
173:     if not beyond:
174:         return None, f"runner {runner} not beyond target {p['target']}"
175:     size = c["size_usd"]
176:     near = int(size * (100 - pct) / 100 // 10) * 10       # each leg floored to 10 USD exactly as PC round_size does
177:     far = int(size * pct / 100 // 10) * 10
178:     if near < 10 or far < 10:
179:         return None, f"size {size} too small for a {100 - pct:g}/{pct:g} split"
180:     if near + far != size:
181:         return None, f"legs {near}+{far} do not sum to size {size}"
182:     tgt_pct = round(abs(p["target"] - p["entry"]) / p["entry"] * 100, 3)
183:     run_pct = round(abs(runner - p["entry"]) / p["entry"] * 100, 3)
184:     return f"{100 - pct:g}@{tgt_pct},{pct:g}@{run_pct}", None
185:
186:
187: def net_rr_floor_reject(net_rr: float):
188:     """None if net_rr clears the floor, else the reject reason. The file is re-read on every alert, so an edit
189:     applies without restarting the trader; unreadable -> reject (fail closed)."""
190:     try:
191:         floor = load_floor()
192:     except NetRrFloorError as e:
193:         return f"net_rr floor unreadable: {e}"
194:     return None if net_rr >= floor else f"net_rr {net_rr} < {floor}"
195:
196:
197: RT_TAKER_FEE_FRAC = 0.0010   # 2 x Deribit BTC-PERPETUAL taker 5 bp (backtest/fees.py, API-verified 2026-09-26): worst-case round trip
198:
199:
200: def fee_to_stop_reject(entry: float, stop: float, cut):
201:     """B146: None if the worst-case round-trip fee is at most `cut` of the stop distance (in R), else the reject reason.
202:     Off unless tom.max_fee_to_stop is set. Evidence: research/fast_track_2026-09-27/TOM_STOP_WIDTH_2026-10-09.md
203:     (stops under 0.10 % of price cost 3.8 to 7.6 R of fees per trade; cut 0.3 leaves under 0.3 R). Bad input -> reject."""
204:     try:
205:         cut = float(cut)
206:         dist = abs(float(entry) - float(stop))
207:         if not (cut > 0 and dist > 0 and float(entry) > 0):
208:             raise ValueError
209:     except (TypeError, ValueError):
210:         return f"fee_to_stop gate misconfigured or zero stop distance (cut {cut!r})"
211:     ratio = RT_TAKER_FEE_FRAC * float(entry) / dist
212:     return None if ratio <= cut else f"fee/stop {ratio:.2f} R > {cut:g} R (stop {dist / float(entry) * 100:.3f} % of price)"
213:
214:
215: def tom_signal(alert: dict, state: dict, cfg: dict, now: datetime):
216:     """New, fresh, actionable Tom alert -> order signal; else None. Marks the alert as seen in state."""
217:     c = cfg["tom"]
218:     if not c["enabled"] or not alert:
219:         return None
220:     p = parse_tom_alert(alert)
221:     if not p or p["alert_no"] is None or p["alert_no"] <= state.get("tom_last_alert_no", -1):
222:         return None
223:     state["tom_last_alert_no"] = p["alert_no"]
224:     reject = None
225:     if p["verdict"] not in c["verdicts"]:
226:         reject = f"verdict {p['verdict']}"
227:     elif p["side"] is None:
228:         reject = f"unknown setup side {p['setup']!r}"
229:     elif p["net_rr"] is not None and (rr_reject := net_rr_floor_reject(p["net_rr"])):
230:         reject = rr_reject
231:     else:
232:         try:
233:             t = datetime.strptime(p["time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
234:             if (now - t).total_seconds() > c["max_age_seconds"]:
235:                 reject = f"stale alert ({int((now - t).total_seconds())} s old)"
236:         except ValueError:
237:             reject = f"bad TIME {p['time']!r}"
238:     if not reject:
239:         wrong_side = (p["side"] == "long" and not (p["stop"] < p["entry"] < p["target"])) or \
240:                      (p["side"] == "short" and not (p["target"] < p["entry"] < p["stop"]))
241:         if wrong_side:
242:             reject = "entry/stop/target not ordered for the side"
243:     cut = c.get("max_fee_to_stop")
244:     if not reject and cut is not None:
245:         reject = fee_to_stop_reject(p["entry"], p["stop"], cut)
246:     wait = c.get("max_entry_seconds")
247:     if not reject and not (isinstance(wait, int) and not isinstance(wait, bool) and wait > 0):
248:         reject = f"bad tom.max_entry_seconds {wait!r}"     # config error: no order rather than a guessed wait
249:     sig = {"source": "tom", "key": f"tom#{p['alert_no']}", "side": p["side"], "detail": p}
250:     if reject:
251:         sig["reject"] = reject
252:         return sig
253:     stop_pct = round(abs(p["entry"] - p["stop"]) / p["entry"] * 100, 3)
254:     tgt_pct = round(abs(p["target"] - p["entry"]) / p["entry"] * 100, 3)
255:     legs, why_single = runner_split(p, c)
256:     sig["log"] = {"runner_target": p["runner_target"]} if legs else {"runner_skipped": why_single}
257:     sig["plan_args"] = ["--side", p["side"], "--entry", "limit", "--price", f"{p['entry']}",
258:                         "--size", str(c["size_usd"]), "--stop", f"{stop_pct}", "--targets", legs or f"{tgt_pct}",
259:                         "--max-loss", str(c["max_loss_usd"]), "--hours", str(c["hours"])]
260:     if legs:                                   # R2: stop to breakeven when the first leg fills (position_manager)
261:         sig["plan_args"].append("--breakeven-after-first-target")
262:     if c.get("max_hold_minutes"):              # TF5 E2: one flat time exit; the zone name no longer scales it
263:         sig["plan_args"] += ["--max-hold-minutes", str(c["max_hold_minutes"])]
264:     sig["executor_args"] = ["--max-entry-seconds", str(c["max_entry_seconds"])]   # TF5 E1b
265:     sig["venue_price"] = True                  # TF5 E1a: cycle() moves --price onto Deribit before place()
266:     return sig
267:
268:
269: def deribit_mark(instrument: str = "BTC-PERPETUAL") -> float:
270:     """Deribit mark price (public/ticker, no credentials, testnet base by default). Raises on any failure."""
271:     if str(HERE) not in sys.path:
272:         sys.path.insert(0, str(HERE))
273:     import deribit_orders as do
274:     return do.get_ticker(instrument)["mark_price"]
275:
276:
277: def apply_venue_price(sig: dict, mark_fn=None):
278:     """TF5 E1a: the card's zone ENTRY is a Binance-derived price; Deribit trades at a basis to it. Move the limit to
279:     zone + (Deribit mark - card PRICE). Stop and target stay percentages of the entry, so they move with it.
280:     Returns None when --price was rewritten (and sig['log'] carries the numbers), else the reject reason.
281:     Fails closed: no usable card PRICE or an unreadable/invalid mark -> no order."""
282:     p = sig["detail"]
283:     if p.get("price") is None:
284:         return "no card PRICE: venue basis unknown"
285:     try:
286:         mark = float((mark_fn or deribit_mark)())
287:     except Exception as e:  # noqa: BLE001 - any ticker failure refuses the entry
288:         return f"deribit mark unreadable: {type(e).__name__}: {str(e)[:120]}"
289:     if not math.isfinite(mark) or mark <= 0:
290:         return f"deribit mark invalid: {mark!r}"
291:     basis = mark - p["price"]
292:     venue_entry = round(p["entry"] + basis, 1)
293:     a = sig["plan_args"]
294:     a[a.index("--price") + 1] = f"{venue_entry}"
295:     sig.setdefault("log", {}).update({"card_entry": p["entry"], "card_price": p["price"], "deribit_mark": mark,
296:                                       "basis": round(basis, 2), "venue_entry": venue_entry})
297:     return None
298:
299:
300: # ---------------------------------------------------------------- layer signals
301:
302: # (RSI level, cross direction) -> side. MLK-R1 (backtest/layers/rsi/malkan_40_60.py): a bull regime cannot cross 40 downward,
303: # a bear regime cannot cross 60 upward, so those two crosses are the regime failing. Any other cross has no source: no side.
304: CROSS_SIDE_BY_LEVEL = {(40.0, "down"): "short", (60.0, "up"): "long"}
305:
306:
307: def layer_side(alert: dict, cfg: dict):
308:     """Side for a layer alert, or None if no rule maps it."""
309:     if alert.get("side") in ("long", "short"):
310:         return alert["side"]
311:     rule = cfg["layer_rules"].get(f"{alert.get('layer')}:{alert.get('event')}")
312:     if rule == "direction":
313:         return {"up": "long", "down": "short"}.get(alert.get("direction"))
314:     if rule == "level":
315:         lv = alert.get("level_value")
316:         return CROSS_SIDE_BY_LEVEL.get((float(lv), alert.get("direction"))) if isinstance(lv, (int, float)) else None
317:     return rule if rule in ("long", "short") else None
318:
319:
320: def read_new_layer_alerts(state: dict, alert_dir: Path = None) -> list:
321:     """New JSONL lines since the stored byte offset of each file. First sight of a file = start at its end."""
322:     alert_dir = alert_dir or LAYER_ALERT_DIR
323:     offsets = state.setdefault("layer_offsets", {})
324:     out = []
325:     for f in sorted(alert_dir.glob("*.jsonl")):
326:         size = f.stat().st_size
327:         off = offsets.get(f.name)
328:         if off is None or off > size:        # new file or truncated/rotated: don't replay history
329:             offsets[f.name] = size
330:             continue
331:         with open(f, "rb") as fh:
332:             fh.seek(off)
333:             chunk = fh.read(size - off)
334:         complete = chunk.rsplit(b"\n", 1)[0] if b"\n" in chunk else b""
335:         offsets[f.name] = off + (len(complete) + 1 if complete else 0)
336:         for line in complete.decode("utf-8", errors="replace").splitlines():
337:             try:
338:                 out.append(json.loads(line))
339:             except ValueError:
340:                 continue
341:     return out
342:
343:
344: SIZE_CEILING_USD = 10000   # trade_plan_validator.MAX_NOTIONAL_CEILING
345:
346:
347: def size_override(source: str, cfg: dict):
348:     """(size_usd, max_loss_usd) from the longest size_overrides prefix matching source, or None. Raises ValueError on
349:     a malformed table or entry: size a positive 10 USD multiple (Deribit contract) up to the validator ceiling,
350:     max loss a positive number."""
351:     table = cfg.get("size_overrides") or {}
352:     if not isinstance(table, dict):
353:         raise ValueError("size_overrides is not an object")
354:     hits = [p for p in table if isinstance(p, str) and p and source.startswith(p)]
355:     if not hits:
356:         return None
357:     v = table[max(hits, key=len)]
358:     size = v.get("size_usd") if isinstance(v, dict) else None
359:     loss = v.get("max_loss_usd") if isinstance(v, dict) else None
360:     if not (isinstance(size, int) and not isinstance(size, bool) and 0 < size <= SIZE_CEILING_USD and size % 10 == 0):
361:         raise ValueError(f"size_usd {size!r} for {max(hits, key=len)}")
362:     if not (isinstance(loss, (int, float)) and not isinstance(loss, bool) and loss > 0):
363:         raise ValueError(f"max_loss_usd {loss!r} for {max(hits, key=len)}")
364:     return size, loss
365:
366:
367: def layer_signal(alert: dict, cfg: dict, now: datetime) -> dict:
368:     c = cfg["layers"]
369:     layer, tf = alert.get("layer"), alert.get("tf")
370:     event = alert.get("event") or alert.get("kind") or alert.get("sub")
371:     # t_close is the bar's OPEN time in ms (Binance kline convention), not its close; the name is kept (operator 2026-10-08).
372:     key = f"{layer}:{alert.get('sub')}:{event}:{tf}:{alert.get('t_close')}"
373:     sig = {"source": f"layer:{layer}:{alert.get('sub')}:{tf}", "key": key, "detail": alert}
374:     sig["log"] = {"bracket_source": c.get("bracket_source", "SAMPLING")}
375:     side = layer_side(alert, cfg)
376:     sig["side"] = side
377:     if not c["enabled"] or layer in cfg["disabled_layers"]:
378:         sig["reject"] = "layer disabled"
379:     elif side is None:
380:         sig["reject"] = f"unmapped {layer}:{event} (add a layer_rules entry)"
381:     else:
382:         t_close = alert.get("t_close")
383:         bar = TF_SECONDS.get(tf)
384:         if not isinstance(t_close, (int, float)) or bar is None:
385:             sig["reject"] = "no t_close/tf"
386:         else:
387:             # t_close is the bar's open time in ms (Binance kline convention); the bar closes one tf later.
388:             # A lagged layer's event is first seen `t_confirm` (latest closed bar) after its own bar: age from that.
389:             t_seen = alert.get("t_confirm")
390:             if isinstance(t_seen, (int, float)) and t_seen > t_close:
391:                 t_close = t_seen
392:             age = now.timestamp() - (t_close / 1000 + bar)
393:             if age > c["max_age_bars"] * bar:
394:                 sig["reject"] = f"stale ({int(age)} s after bar close)"
395:     size, max_loss = c["size_usd"], c["max_loss_usd"]
396:     if "reject" not in sig:
397:         try:
398:             size, max_loss = size_override(sig["source"], cfg) or (size, max_loss)
399:         except ValueError as e:
400:             sig["reject"] = f"bad size_overrides: {e}"
401:     if "reject" not in sig:
402:         sig["plan_args"] = ["--side", side, "--entry", "market", "--size", str(size),
403:                             "--stop", str(c["stop_pct"]), "--targets", c["targets"],
404:                             "--max-loss", str(max_loss), "--hours", str(c["hours"])]
405:         if c.get("max_hold_bars"):
406:             sig["plan_args"] += ["--max-hold-minutes", f"{c['max_hold_bars'] * bar / 60:g}"]
407:     return sig
408:
409:
410: # ---------------------------------------------------------------- trading
411:
412: def brakes() -> list:
413:     return [p.name for p in (HALT, HALT_DAILY_LOSS) if p.exists()]
414:
415:
416: def account_secret_path(label: str) -> Path:
417:     return SECRETS_DIR / f"testnet_{label}.secret.json"
418:
419:
420: BLOCKLIST_INVALID = "trade_blocklist invalid or config unreadable: all layer trades blocked (fail closed)"
421:
422:
423: def trade_block_reason(source: str, cfg: dict):
424:     """Reason string when a LAYER source may not trade, else None. Tom (any source not starting 'layer:') is never
425:     blocked. Fail closed: a trade_blocklist that is present but not a list of non-empty strings, or reasons that are
426:     not a dict, blocks every layer source (never silently re-enables a layer that failed its backtest)."""
427:     if not str(source).startswith("layer:"):
428:         return None
429:     bl = cfg.get("trade_blocklist", [])
430:     reasons = cfg.get("trade_blocklist_reasons", {})
431:     if (not isinstance(bl, list) or not isinstance(reasons, dict)
432:             or not all(isinstance(p, str) and p for p in bl)):
433:         return BLOCKLIST_INVALID
434:     for prefix in bl:
435:         if source.startswith(prefix):
436:             r = reasons.get(prefix)
437:             return r if isinstance(r, str) and r else "blocklisted (no reason recorded)"
438:     return None
439:
440:
441: def load_config(path: Path) -> dict:
442:     """DEFAULT_CONFIG overlaid with the JSON file. A missing/unparseable/non-object file cannot be trusted to still
443:     carry the blocklist, so it sets trade_blocklist to None (-> trade_block_reason blocks all layer trades) and logs."""
444:     cfg = json.loads(json.dumps(DEFAULT_CONFIG))
445:     try:
446:         raw = json.loads(Path(path).read_text(encoding="utf-8"))
447:         if not isinstance(raw, dict):
448:             raise ValueError("config top level is not an object")
449:     except (OSError, ValueError) as e:
450:         log({"event": "config_unreadable", "path": str(path), "error": repr(e)[:200],
451:              "action": "all layer trades blocked (fail closed); Tom unaffected"})
452:         cfg["trade_blocklist"] = None
453:         return cfg
454:     for k, v in raw.items():
455:         # accounts is an ordered prefix table (first match wins): the file replaces it, never overlays it, or a default
456:         # key keeps its early position and shadows the file's more specific prefixes (fabio fell to the main slot).
457:         cfg[k] = ({**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) and k != "accounts" else v)
458:     return cfg
459:
460:
461: def account_for(source: str, cfg: dict):
462:     """Named account for a signal source, or None (default shared slot). Existence check only, never reads the file."""
463:     for prefix, label in (cfg.get("accounts") or {}).items():
464:         if source.startswith(prefix):
465:             if account_secret_path(label).exists():
466:                 return label
467:             if label not in _warned_missing:
468:                 _warned_missing.add(label)
469:                 log({"event": f"{label}_account_missing", "path": str(account_secret_path(label))})
470:             return None
471:     return None
472:
473:
474: def account_secret_missing(source: str, cfg: dict):
475:     """Label of the named account this source is routed to when its secret file is missing, else None.
476:     A routed source must never fall back to the main slot (B148): that sent layer trades to MAIN at the override size."""
477:     for prefix, label in (cfg.get("accounts") or {}).items():
478:         if source.startswith(prefix):
479:             return None if account_secret_path(label).exists() else label
480:     return None
481:
482:
483: def run(cmd: list, timeout: int = 900, account: str = None) -> tuple:
484:     env = {**os.environ, "MTS_ACCOUNT": account} if account else {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
485:     r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
486:                        timeout=timeout, env=env)
487:     return r.returncode, (r.stdout or "") + (r.stderr or "")
488:
489:
490: def place(sig: dict, dry_run: bool, account: str = None) -> dict:
491:     """new_plan -> executor --go -> start position_manager. Returns an outcome dict (never raises)."""
492:     py = sys.executable
493:     rc, out = run([py, str(HERE / "new_plan.py"), *sig["plan_args"], "--yes"], timeout=60, account=account)
494:     m = re.search(r"SAVED (\S+)", out)
495:     if rc != 0 or not m:
496:         return {"outcome": "plan_refused", "output": out.strip()[-400:]}
497:     plan_id = m.group(1)
498:     plan_file = HERE / "plans" / f"{plan_id}.json"
499:     if dry_run:
500:         rc, out = run([py, str(HERE / "executor.py"), str(plan_file)], timeout=60, account=account)
501:         return {"outcome": "dry_run", "plan_id": plan_id, "rc": rc, "output": out.strip()[-300:]}
502:     rc, out = run([py, str(HERE / "executor.py"), str(plan_file), "--go", *sig.get("executor_args", [])],
503:                   account=account)
504:     if rc != 0:
505:         return {"outcome": "entry_failed", "plan_id": plan_id, "output": out.strip()[-400:]}
506:     if "no_fill" in out:                     # limit entry that never filled: nothing to manage
507:         return {"outcome": "no_fill", "plan_id": plan_id, "output": out.strip()[-300:]}
508:     proc = spawn_manager(plan_id, account)
509:     return {"outcome": "entered", "plan_id": plan_id, "manager_pid": proc.pid, "proc": proc,
510:             "output": out.strip()[-300:]}
511:
512:
513: def spawn_manager(plan_id: str, account: str = None):
514:     """Start position_manager for plan_id with the account's MTS_ACCOUNT. Returns the Popen."""
515:     MANAGER_LOG_DIR.mkdir(parents=True, exist_ok=True)
516:     mlog = open(MANAGER_LOG_DIR / f"{plan_id}.log", "a", encoding="utf-8")
517:     penv = {**os.environ, "MTS_ACCOUNT": account} if account else {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
518:     return subprocess.Popen([sys.executable, str(HERE / "position_manager.py"), plan_id], cwd=REPO, stdout=mlog,
519:                             stderr=subprocess.STDOUT, env=penv)
520:
521:
522: def exchange_flat(account: str = None, instrument: str = "BTC-PERPETUAL"):
523:     """Read-only exchange check for one account: True flat, False position open, None could not be read."""
524:     prev = os.environ.get("MTS_ACCOUNT")
525:     try:
526:         if str(HERE) not in sys.path:
527:             sys.path.insert(0, str(HERE))
528:         import deribit_orders as do
529:         if account:
530:             os.environ["MTS_ACCOUNT"] = account
531:         else:
532:             os.environ.pop("MTS_ACCOUNT", None)
533:         token = do.authenticate()
534:         return int(do.get_position(token, instrument).get("size") or 0) == 0
535:     except Exception:  # noqa: BLE001
536:         return None
537:     finally:
538:         if prev is None:
539:             os.environ.pop("MTS_ACCOUNT", None)
540:         else:
541:             os.environ["MTS_ACCOUNT"] = prev
542:
543:
544: def operator_alert(msg: str) -> None:
545:     with open(OPERATOR_ALERTS, "a", encoding="utf-8", newline="\n") as f:
546:         f.write(f"{now_utc().strftime('%Y-%m-%dT%H:%M:%SZ')} auto_trader {msg}\n")
547:
548:
549: def settle_slot(slot: dict, acct: str = None) -> bool:
550:     """True when the slot's trade is closed and the slot may be freed. A manager that exited non-zero frees the slot
551:     only if the exchange shows the account flat; otherwise it is respawned (max MAX_RESPAWNS) and the slot stays busy."""
552:     rc = slot["proc"].poll()
553:     if rc is None:
554:         return False
555:     if rc != 0:
556:         flat = exchange_flat(acct)
557:         if flat is None:
558:             slot["flat_check_fails"] = slot.get("flat_check_fails", 0) + 1
559:             if slot["flat_check_fails"] % 10 == 1:
560:                 log({"event": "manager_exit_unverified", "plan_id": slot["plan_id"], "manager_rc": rc,
561:                      "account": acct, "note": "exchange position unreadable; slot kept busy"})
562:             return False
563:         if flat is False:
564:             n = slot.get("respawns", 0)
565:             if n >= MAX_RESPAWNS:
566:                 if not slot.get("alerted"):
567:                     slot["alerted"] = True
568:                     log({"event": "manager_lost", "plan_id": slot["plan_id"], "manager_rc": rc, "account": acct,
569:                          "respawns": n, "action": "operator_alert_slot_busy"})
570:                     operator_alert(f"OPERATOR: position_manager for {slot['plan_id']} (account {acct or 'default'}) "
571:                                    f"keeps dying (rc={rc}) and the position is still OPEN; {MAX_RESPAWNS} respawns "
572:                                    f"used - manage/close it by hand")
573:                 return False
574:             slot["respawns"] = n + 1
575:             log({"event": "manager_lost", "plan_id": slot["plan_id"], "manager_rc": rc, "account": acct,
576:                  "respawn": slot["respawns"], "action": "respawn"})
577:             try:
578:                 slot["proc"] = spawn_manager(slot["plan_id"], acct)
579:             except Exception as e:  # noqa: BLE001 - the dead proc stays in the slot, next cycle retries
580:                 log({"event": "respawn_error", "plan_id": slot["plan_id"], "error": repr(e)[:200]})
581:             return False
582:     log({"event": "trade_closed", "plan_id": slot["plan_id"], "source": slot["source"], "manager_rc": rc,
583:          **({"account": acct} if acct else {})})
584:     record_ledger(slot["plan_id"], slot["source"], acct, rc)
585:     return True
586:
587:
588: def record_ledger(plan_id: str, source: str, account, manager_rc) -> None:
589:     """Outcome ledger row for a closed trade (trade_ledger.py). Never raises: the ledger must not stop the trader."""
590:     try:
591:         if str(HERE) not in sys.path:
592:             sys.path.insert(0, str(HERE))
593:         import trade_ledger
594:         row = trade_ledger.record_closed(plan_id, source, account, manager_rc)
595:         log({"event": "ledger_row", "plan_id": plan_id, "net_pnl_usd": row and row.get("net_pnl_usd"),
596:              "exit_reason": row and row.get("exit_reason"),
597:              "account": account, "unresolved": row and row.get("unresolved")})
598:     except Exception as e:  # noqa: BLE001
599:         log({"event": "ledger_error", "plan_id": plan_id, "error": repr(e)[:200]})
600:
601:
602: # ---------------------------------------------------------------- restart recovery (adopt running managers)
603:
604: ADOPTED_RC = -1   # exit code reported for an adopted manager once it is gone (real rc unknown -> exchange flat check)
605:
606:
607: class PidProc:
608:     """Popen-like handle for a manager we did not start: poll() is None while the pid lives, then ADOPTED_RC."""
609:
610:     def __init__(self, pid: int, alive_fn=None):
611:         self.pid = pid
612:         self._alive = alive_fn or pid_alive
613:
614:     def poll(self):
615:         return None if self._alive(self.pid) else ADOPTED_RC
616:
617:
618: class DeadProc:
619:     """Manager that was not running at restart; settle_slot then applies the exchange flat check / respawn rules."""
620:     pid = None
621:
622:     def poll(self):
623:         return ADOPTED_RC
624:
625:
626: def pid_alive(pid: int) -> bool:
627:     if os.name == "nt":
628:         import ctypes
629:         k32 = ctypes.windll.kernel32
630:         h = k32.OpenProcess(0x1000, False, int(pid))    # PROCESS_QUERY_LIMITED_INFORMATION
631:         if not h:
632:             return False
633:         try:
634:             code = ctypes.c_ulong()
635:             return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259   # STILL_ACTIVE
636:         finally:
637:             k32.CloseHandle(h)
638:     try:
639:         os.kill(int(pid), 0)
640:         return True
641:     except OSError:
642:         return False
643:
644:
645: def list_process_cmdlines() -> list:
646:     """[(pid, commandline)] of all processes (Win32_Process). [] when unavailable."""
647:     try:
648:         r = subprocess.run(["powershell", "-NoProfile", "-Command",
649:                             "Get-CimInstance Win32_Process | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
650:                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
651:         rows = json.loads(r.stdout or "[]")
652:         rows = [rows] if isinstance(rows, dict) else rows
653:         return [(int(x["ProcessId"]), x.get("CommandLine") or "") for x in rows]
654:     except Exception:  # noqa: BLE001
655:         return []
656:
657:
658: def manager_pids(plan_id: str, procs: list) -> list:
659:     """Pids of python processes running `position_manager.py <plan_id>` (exact plan id token)."""
660:     pat = re.compile(r'position_manager\.py"?\s+"?' + re.escape(plan_id) + r'"?(\s|$)')
661:     return sorted(pid for pid, cl in procs
662:                   if pat.search(cl) and "python" in cl.split("position_manager.py")[0].lower())
663:
664:
665: def open_plans_from_log(path: Path = None) -> list:
666:     """trade_attempt outcome=entered without a later trade_closed for the same plan_id. Oldest first."""
667:     entered, closed = {}, set()
668:     try:
669:         lines = (path or LOG_PATH).read_text(encoding="utf-8").splitlines()
670:     except OSError:
671:         return []
672:     for line in lines:
673:         try:
674:             e = json.loads(line)
675:         except ValueError:
676:             continue
677:         pid = e.get("plan_id")
678:         if e.get("event") == "trade_attempt" and e.get("outcome") == "entered" and pid:
679:             entered[pid] = e
680:             closed.discard(pid)
681:         elif e.get("event") == "trade_closed" and pid:
682:             closed.add(pid)
683:     return [e for pid, e in entered.items() if pid not in closed]
684:
685:
686: def recover_slots(log_path: Path = None, procs=None, alive_fn=None) -> tuple:
687:     """Rebuild (active, extra) slots at start from the log + live processes. Account comes from the logged attempt.
688:     Manager alive -> adopt. Manager dead -> slot with DeadProc: the first cycle's settle_slot does the exchange check
689:     (open -> respawn per MAX_RESPAWNS, flat -> trade_closed + ledger row). An older open plan of an account that has a
690:     newer one is closed as superseded (one position per account)."""
691:     plans = open_plans_from_log(log_path)
692:     procs = list_process_cmdlines() if procs is None else procs
693:     active, extra = {}, {}
694:     for e in reversed(plans):                                  # newest first
695:         pid, acct = e["plan_id"], e.get("account") or None
696:         taken = (active if not acct else extra.get(acct))
697:         pids = manager_pids(pid, procs)
698:         if taken:
699:             if pids:
700:                 log({"event": "adopt_skipped", "plan_id": pid, "account": acct, "manager_pids": pids,
701:                      "note": f"slot already held by {taken['plan_id']}; alert operator"})
702:                 operator_alert(f"OPERATOR: two live managers for account {acct or 'default'}: {pid} and "
703:                                f"{taken['plan_id']} - check by hand")
704:             else:
705:                 log({"event": "trade_closed", "plan_id": pid, "source": e.get("source"), "manager_rc": ADOPTED_RC,
706:                      "note": "superseded_at_restart", **({"account": acct} if acct else {})})
707:                 record_ledger(pid, e.get("source"), acct, ADOPTED_RC)
708:             continue
709:         slot = {"proc": PidProc(pids[0], alive_fn) if pids else DeadProc(), "plan_id": pid, "source": e.get("source")}
710:         log({"event": "adopted", "plan_id": pid, "source": e.get("source"), "account": acct,
711:              "manager_pid": pids[0] if pids else None, "manager": "alive" if pids else "dead_checking_exchange"})
712:         if acct:
713:             extra[acct] = slot
714:         else:
715:             active = slot
716:     return active, extra
717:
718:
719: def cycle(state: dict, cfg: dict, dry_run: bool, active: dict, now: datetime = None, extra: dict = None) -> dict:
720:     """One poll. Returns the (possibly new) default-slot trade dict. `active` = {'proc','plan_id','source'} or {}.
721:     `extra` = {account_label: trade dict}, mutated in place (named-account slots)."""
722:     now = now or now_utc()
723:     extra = extra if extra is not None else {}
724:     for lab in list(extra):
725:         if settle_slot(extra[lab], lab):
726:             del extra[lab]
727:     if active and settle_slot(active, None):
728:         active = {}
729:     signals = []
730:     s = tom_signal(load_json(TOM_ALERT, {}), state, cfg, now)
731:     if s:
732:         signals.append(s)
733:     signals += [layer_signal(a, cfg, now) for a in read_new_layer_alerts(state)]
734:     halted = brakes()
735:     for sig in signals:
736:         base = {"source": sig["source"], "key": sig["key"], "side": sig.get("side"), **sig.get("log", {})}
737:         blocked = trade_block_reason(sig["source"], cfg)
738:         if blocked:
739:             # Alert already consumed (layer_offsets advance in read_new_layer_alerts, persisted each cycle): no retry.
740:             log({"event": "layer_trade_blocked", "source": sig["source"], "reason": blocked, "key": sig["key"],
741:                  "side": sig.get("side")})
742:         elif "reject" in sig:
743:             log({"event": "signal_rejected", **base, "reason": sig["reject"]})
744:         elif halted:
745:             log({"event": "skipped_halt", **base, "brakes": halted})
746:         elif AUTO_PAUSE.exists():
747:             log({"event": "skipped_auto_pause", **base})
748:         elif account_secret_missing(sig["source"], cfg):
749:             account_for(sig["source"], cfg)        # logs <label>_account_missing once
750:             log({"event": "signal_rejected", **base, "reason": "account_secret_missing",
751:                  "account": account_secret_missing(sig["source"], cfg)})
752:         else:
753:             acct = account_for(sig["source"], cfg)
754:             slot = extra.get(acct) if acct else active
755:             if slot:
756:                 log({"event": "skipped_busy", **base, "busy_with": slot["plan_id"], "account": acct})
757:                 continue
758:             if sig.get("venue_price"):           # read the mark only when the order is about to go out
759:                 why = apply_venue_price(sig)
760:                 if why:
761:                     log({"event": "signal_rejected", **base, "reason": why})
762:                     continue
763:                 base.update(sig["log"])
764:             res = place(sig, dry_run, acct) if acct else place(sig, dry_run)
765:             proc = res.pop("proc", None)
766:             log({"event": "trade_attempt", **base, **res, "account": acct})
767:             if proc is not None:
768:                 new = {"proc": proc, "plan_id": res["plan_id"], "source": sig["source"]}
769:                 if acct:
770:                     extra[acct] = new
771:                 else:
772:                     active = new
773:     return active
774:
775:
776: def main(argv=None) -> int:
777:     ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
778:     ap.add_argument("--once", action="store_true")
779:     ap.add_argument("--dry-run", action="store_true", help="build plans and dry-run the executor; place nothing")
780:     ap.add_argument("--poll-seconds", type=int, default=20)
781:     ap.add_argument("--config", default=str(HERE / "auto_trader_config.json"))
782:     a = ap.parse_args(argv)
783:     cfg = load_config(Path(a.config))
784:     state = load_json(STATE_PATH, {})
785:     if "tom_last_alert_no" not in state:     # first start: never trade an alert that predates the trader
786:         p = parse_tom_alert(load_json(TOM_ALERT, {}))
787:         state["tom_last_alert_no"] = p.get("alert_no") or -1
788:     log({"event": "start", "dry_run": a.dry_run, "brakes": brakes(), "tom_last_alert_no": state["tom_last_alert_no"]})
789:     active, extra = recover_slots()
790:     try:
791:         while True:
792:             active = cycle(state, cfg, a.dry_run, active, extra=extra)
793:             save_json(STATE_PATH, state)
794:             if a.once:
795:                 return 0
796:             time.sleep(a.poll_seconds)
797:     except KeyboardInterrupt:
798:         log({"event": "stop", "active": active.get("plan_id")})
799:         return 0
800:
801:
802: if __name__ == "__main__":
803:     raise SystemExit(main())
```

### MyTradingSys/execution/auto_trader_config.json

SHA-256: `1d4fc9553b5399bae1da07bfed6d99a206b9959392d652d7f943b85a2d6d5d19`

```text
1: {
2:  "_calibration": "Testnet calibration from 2026-10-08 (operator 2026-10-07: all layers fire, sizes 20 to 1000 USD, base 20). Blocklist parked, not deleted; restore it from trade_blocklist_parked before any mainnet use.",
3:  "accounts": {
4:   "layer:turn_of_candle:": "jishu_1",
5:   "layer:rsi:rsi_events:5m": "jishu_2",
6:   "layer:rsi:rsi_events:15m": "jishu_3",
7:   "layer:rsi:rsi_events:1h": "jishu_4",
8:   "layer:rsi:malkan_bull:": "jishu_7",
9:   "layer:rsi:malkan_bear:": "jishu_8",
10:   "layer:session:": "jishu_9",
11:   "layer:positioning:": "jishu_10",
12:   "layer:fabio:cvd_absorption:15m": "jishu_11",
13:   "layer:fabio:cvd_absorption:1h": "jishu_12",
14:   "layer:fabio:escalation:": "jishu_13",
15:   "layer:fabio:volume_fvg:": "jishu_14",
16:   "layer:fabio:": "jishu_15",
17:   "layer:cryptocred:sr_flip:15m": "jishu_16",
18:   "layer:cryptocred:sr_flip:1h": "jishu_17",
19:   "layer:cryptocred:fib_pullback:15m": "jishu_18",
20:   "layer:cryptocred:fib_pullback:1h": "jishu_19",
21:   "layer:cryptocred:": "jishu_20",
22:   "layer:": "jishu_21"
23:  },
24:  "tom": {
25:   "size_usd": 20,
26:   "max_loss_usd": 5,
27:   "verdicts": [
28:    "SETUP_FORMING",
29:    "SETUP_CONFIRMED",
30:    "WAIT_RR"
31:   ],
32:   "hours": 1.0,
33:   "max_hold_minutes": 120,
34:   "max_entry_seconds": 600,
35:   "max_fee_to_stop": 0.3
36:  },
37:  "layers": {
38:   "size_usd": 20,
39:   "max_loss_usd": 2,
40:   "max_age_bars": 2.0,
41:   "hours": 1.0
42:  },
43:  "size_overrides": {
44:   "layer:turn_of_candle:": {
45:    "size_usd": 20,
46:    "max_loss_usd": 2
47:   },
48:   "layer:rsi:rsi_events:5m": {
49:    "size_usd": 50,
50:    "max_loss_usd": 2
51:   },
52:   "layer:rsi:rsi_events:15m": {
53:    "size_usd": 100,
54:    "max_loss_usd": 3
55:   },
56:   "layer:rsi:rsi_events:1h": {
57:    "size_usd": 250,
58:    "max_loss_usd": 5
59:   },
60:   "layer:rsi:malkan_": {
61:    "size_usd": 500,
62:    "max_loss_usd": 10
63:   },
64:   "layer:session:": {
65:    "size_usd": 150,
66:    "max_loss_usd": 3
67:   },
68:   "layer:positioning:": {
69:    "size_usd": 750,
70:    "max_loss_usd": 15
71:   },
72:   "layer:fabio:cvd_absorption:15m": {
73:    "size_usd": 100,
74:    "max_loss_usd": 3
75:   },
76:   "layer:fabio:cvd_absorption:1h": {
77:    "size_usd": 300,
78:    "max_loss_usd": 6
79:   },
80:   "layer:fabio:escalation:": {
81:    "size_usd": 400,
82:    "max_loss_usd": 8
83:   },
84:   "layer:fabio:volume_fvg:": {
85:    "size_usd": 1000,
86:    "max_loss_usd": 20
87:   },
88:   "layer:cryptocred:sr_flip:15m": {
89:    "size_usd": 200,
90:    "max_loss_usd": 4
91:   },
92:   "layer:cryptocred:sr_flip:1h": {
93:    "size_usd": 600,
94:    "max_loss_usd": 12
95:   },
96:   "layer:cryptocred:fib_pullback:15m": {
97:    "size_usd": 350,
98:    "max_loss_usd": 7
99:   },
100:   "layer:cryptocred:fib_pullback:1h": {
101:    "size_usd": 800,
102:    "max_loss_usd": 16
103:   }
104:  },
105:  "trade_blocklist": [],
106:  "trade_blocklist_reasons": {},
107:  "trade_blocklist_parked": {
108:   "layer:session:session_momentum:": "T055 C2 FAIL (research/fast_track_2026-09-27/T055_BT_c2.md): backtest failed; alerts kept for data collection",
109:   "layer:positioning:funding_cvd_fade:": "T055 C1 FAIL (research/fast_track_2026-09-27/T055_BT_c1.md): backtest failed; alerts kept for data collection",
110:   "layer:turn_of_candle:": "T055 C3 NO EDGE (research/fast_track_2026-09-27/T055_BT_c3.md): no gross edge; alerts kept for data collection",
111:   "layer:fabio:escalation:": "FABIO_L1_REPORT (backtest/layers/fabio/FABIO_L1_REPORT.md): no edge; alerts kept for data collection",
112:   "layer:rsi:rsi_events:15m": "BACKTEST_L1_REPORT (backtest/layers/BACKTEST_L1_REPORT.md): PBO 0.79-0.91, overfit; alerts kept for data collection"
113:  },
114:  "_accounts_note": "2026-10-08: one account per layer group so one-position-per-account never blocks another layer; Tom stays on the main (default) slot; jishu_22 spare. A missing secret file falls back to the main slot (logged as <label>_account_missing)."
115: }
```

## E06

### MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md

SHA-256: `6a8a1ab2ef7495384dbe1ed3c2a0cf6db1421342608f6da3e679f93f75d14034`

```text
1: # Backtest L1 report - D3 RSI tolerance study + 075 CryptoCred adapter
2:
3: Run id `l1_2ee35b1e79` (manifest: `Dumps/backtest/runs/l1_2ee35b1e79/manifest.json`, gitignored data
4: files: `d3_tolerance_study.json`, `cc_adapter_results.json` in the same dir).
5: Revision `da488de` (commit `da488deb447d88ae2188e017ce5d3988bb42385f`). Data: BTCUSDT 1m,
6: 2022-01-01..2026-09-26 (2,491,200 bars, `Dumps/backtest/raw_1m_2022` + `Dumps/backtest/raw`).
7: Split: chronological 70% in-sample (IS) / 30% out-of-sample (OOS) per timeframe, no shuffling.
8: Tolerance grid: 0.5..5.0 RSI points (0.5 steps, symmetric — `rsi_events` takes one tolerance for
9: both sides of the band). Levels: 40 `support` (long) and 60 `rejection` (short), the D3 worked
10: example. Chosen tolerance = best IS mean forward return at h=5 among tolerances with >=5 IS events.
11: PBO via `bt/ref_pbo.ref_pbo_cscv` on IS daily-bucketed h=5 returns (no-signal days = 0 return),
12: S=16 blocks where the day count allowed it.
13:
14: ## D3 tolerance study (RSI level events, no Malkan regime gate — see caveats)
15:
16: | TF | Level | Chosen tol | IS n (h5 mean/hit) | OOS n (h5 mean/hit) | OOS baseline (h5 mean/hit) | PBO |
17: |---|---|---|---|---|---|---|
18: | 15m | 40 support (long) | 1.0 | 1552 / +0.017% / 54.5% | 698 / -0.028% / 50.0% | 49820 / 0.00003% / 50.2% | 0.785 |
19: | 15m | 60 rejection (short) | 1.0 | 1617 / +0.016% / 53.4% | 767 / -0.002% / 49.3% | 49820 / 0.00003% / 50.2% | 0.907 |
20: | 1h | 40 support (long) | 0.5 | 193 / +0.108% / 54.9% | 89 / +0.043% / 56.2% | 12452 / -0.0001% / 50.7% | **0.030** |
21: | 1h | 60 rejection (short) | 1.5 | 564 / -0.035% / 52.3% | 219 / -0.010% / 46.6% | 12452 / -0.0001% / 50.7% | 0.681 |
22: | 4h | 40 support (long) | 1.0 | 93 / +0.544% / 53.8% | 32 / +0.140% / 62.5% | 3110 / 0.00005% / 51.3% | 0.886 |
23: | 4h | 60 rejection (short) | 0.5 | 39 / +0.095% / 48.7% | 19 / -0.605% / 21.1% | 3110 / 0.00005% / 51.3% | 0.643 |
24: | 1d | 40 support (long) | 4.0 | 55 / -0.821% / 47.3% | 23 / +0.891% / 56.5% | 514 / +0.011% / 49.4% | 0.390 |
25: | 1d | 60 rejection (short) | 1.5 | 23 / +1.084% / 60.9% | 8 / -1.526% / 37.5% | 514 / +0.011% / 49.4% | 0.477 |
26:
27: (Percentages are mean forward return at horizon h=5 bars; `hit` = fraction of events with a positive
28: h=5 return. Full per-tolerance grid and horizons 1/3/5/10/20 are in `d3_tolerance_study.json`.)
29:
30: **Headline: only one cell clears the PBO bar.** 1h / level-40 support, tolerance 0.5, PBO=0.030
31: (well under the conventional <0.5 "probably not overfit" line), and its OOS edge (+0.043% mean,
32: 56.2% hit over 89 events) sits in the same direction as IS. Every other cell has PBO >= 0.39 — the
33: "best" tolerance on IS is statistically indistinguishable from the other nine tolerances in the grid
34: on OOS data, i.e. likely overfit to the IS split, not a real edge. 15m is the clearest case: huge
35: PBO (0.79-0.91) and the OOS mean return is near zero or negative despite a positive IS mean.
36:
37: ## 075 CryptoCred adapter (setups -> `signals_to_events` -> `forward_return_stats`, 1h bars)
38:
39: | Setup | Signals | h5 mean return | h5 hit rate | Sim trades (bt_engine) | Sim win rate |
40: |---|---|---|---|---|---|
41: | setup1_sr_flip | 2517 | +0.021% | 46.3% | 500 (capped) | 51.2% |
42: | setup3_failed_msb_reversal | 290 | +0.036% | 47.6% | 290 | 33.4% |
43: | setup2_fib_pullback | 839 | +0.006% | 52.1% | 500 (capped) | 61.4% |
44:
45: No PBO computed for CC setups (task asked for PBO on the D3 grid; CC setups aren't a parameter sweep
46: here, just fixed rule sets).
47:
48: ## Blocker found and fixed
49:
50: `cc_setups.setup2_fib_pullback` (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:75-76,102-103`)
51: indexed `swings[broken_swing_i]`, treating `broken_swing_i` as a position in the local `swings` list.
52: But `cc_structure.classify_msb` sets `broken_swing_i = H_last["i"]` / `L_last["i"]`
53: (`cc_structure.py:106,128`), which is a **bars index** (`find_swings` stores each swing's own bar
54: position as `"i"`, and swings are sparse — far fewer than bars). On real data this raised
55: `IndexError: list index out of range` as soon as `broken_swing_i >= len(swings)`. `setup3` uses the
56: same field correctly (`bars[swing_i:c+1]`, a bars-index slice) and was unaffected; `setup1` never reads
57: the field. The existing `test_cc_setups.py` unit tests passed because their hand-built fixtures were
58: crafted so a swing's bars-index happened to equal its swings-list position (see the test file's own
59: comment at line 85: "list-index 3, matching broken_swing_i"), which masked the mismatch.
60:
61: Fixed (commit `54ad393`, fast-track): `setup2_fib_pullback` now first locates the swings-list position
62: whose `s["i"] == broken_swing_i`, then walks backward from that position in both the bull and bear
63: branches. `cc_structure`'s field semantics (a bars index) were left unchanged. A regression test
64: (`test_u4b_bull_swing_list_index_ne_bar_index` in `test_cc_setups.py`) uses swings at bar indices
65: 10-13 (list positions 0-3) to catch the list/bar-index mismatch; it raises `IndexError` on the
66: pre-fix code. The setup2 row above is from a real-data re-run with the fix applied
67: (`setup2_fib_pullback` over the same 1h-resampled BTCUSDT bars as setup1/setup3).
68:
69: ## Caveats
70:
71: - **Sample size**: 4h and 1d event counts are small (8-93 per cell); their PBO and OOS figures are
72:   low-confidence. 15m has by far the largest sample and the cleanest (negative) result.
73: - **No look-ahead**: `forward_return_stats` only uses `closes[i+h]` for `i+h < len(closes)`;
74:   events with insufficient trailing data are excluded from `n`, not zero-filled. The IS/OOS split is
75:   chronological (IS strictly precedes OOS) so the tolerance choice never sees OOS bars.
76: - **Not Malkan-regime-gated**: this D3 study runs `rsi_events` directly (generic level
77:   support/rejection), not `malkan_setup_bull`/`bear` (which additionally gate on `malkan_regime` and
78:   candle color, per 073). The design's own MLK-GAP1 note says the full 5-star setup also needs
79:   Monthly+Weekly regime, which is out of scope here.
80: - **PBO methodology**: IS returns were bucketed by calendar day (mean h=5 return of that day's
81:   events, 0 for a no-signal day) to build the CSCV return matrix across the 10-tolerance grid; this
82:   is a reasonable but not unique way to turn sparse per-event returns into equal-length series for
83:   `ref_pbo_cscv`. Different bucketing could shift these numbers somewhat, though not the qualitative
84:   conclusion (only 1h/40-support survives).
85: - **CC adapter fees/costs**: `signals_to_trades` bt_engine sim used default taker/maker fees; win
86:   rates above are before comparing to a funding-cost or slippage-adjusted baseline.
```

## E07

### MyTradingSys/backtest/layers/rsi/malkan_40_60.py

SHA-256: `d21747c74636250614ecba5c3ad1b13e5afc169b96ee6741136dedf6642eda7a`

```text
1: """
2: MalkanView 40/60 regime classifier plus single-timeframe bull/bear bounce setups.
3:
4: Cites:
5: - MLK-R1 (regime/range-shift, WEB_RESEARCH.md lines 39-62 and 84-89: "Whenever the market is bearish,
6:   it won't be able to cross 60 ... whenever in a bullish trend, it won't be able to cross 40")
7: - MLK-S1 (Bullish candlestick forms at 40 RSI level on daily chart = buy signal)
8: - MLK-S2 (Bearish candlestick forms at 60 RSI level on daily chart = short signal)
9:
10: D2 rule: the 40/60 numbers are private to malkan_40_60. No other module imports them.
11: This file is the one place those numbers may live as defaults.
12:
13: MLK-GAP1: The real Malkan 5-star setup gates a Daily entry on Monthly AND Weekly RSI regime
14: (a 3-timeframe composition). This module implements the single-timeframe mechanics only:
15: regime + 40/60 bounce/reject + entry-candle color. A caller must run it once per timeframe
16: (via the timeframe layer, D1) and combine results itself to reconstruct the full multi-timeframe setup.
17:
18: Source: MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md (medium-high confidence)
19: """
20:
21: from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
22:
23:
24: def malkan_regime(rsi: list, lo: float = 40.0, hi: float = 60.0, lookback: int = 20) -> list:
25:     """
26:     Identical algorithm to the scoped `rsi_regime`: returns a list the same length as `rsi`.
27:     A value at index `i` requires exactly `lookback` consecutive non-`None` `rsi` values ending at `i`
28:     (walking backward from `i`, collecting non-`None` values until `lookback` are found or the start
29:     of the series is reached without enough — if not enough, output `None` at `i`).
30:     Given the window: `min_rsi = min(window)`, `max_rsi = max(window)`.
31:     `"BULL"` if `min_rsi >= lo and max_rsi >= hi`.
32:     Else `"BEAR"` if `max_rsi <= hi and min_rsi <= lo`.
33:     Else `"RANGE"`.
34:     Raise `ValueError` if not `0 < lo < hi < 100`, or if `lookback < 1`.
35:     """
36:     if not (0 < lo < hi < 100):
37:         raise ValueError("lo and hi must satisfy 0 < lo < hi < 100")
38:     if lookback < 1:
39:         raise ValueError("lookback must be at least 1")
40:
41:     result = [None] * len(rsi)
42:     for i in range(len(rsi)):
43:         window = []
44:         j = i
45:         while len(window) < lookback and j >= 0:
46:             if rsi[j] is not None:
47:                 window.append(rsi[j])
48:             j -= 1
49:
50:         if len(window) == lookback:
51:             min_rsi = min(window)
52:             max_rsi = max(window)
53:             if min_rsi >= lo and max_rsi >= hi:
54:                 result[i] = "BULL"
55:             elif max_rsi <= hi and min_rsi <= lo:
56:                 result[i] = "BEAR"
57:             else:
58:                 result[i] = "RANGE"
59:         # else: leave as None
60:
61:     return result
62:
63:
64: def malkan_setup_bull(bars: list, rsi: list, regime: list, level: float = 40.0, tolerance: float = 2.0, require_bullish_candle: bool = True) -> list:
65:     """
66:     [MLK-S1, MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md lines 108-134:
67:     "Bullish candlestick forms at 40 RSI level on daily chart = buy signal"]
68:     `bars` is a list of dicts with at least `o`,`c`,`t` (same shape as elsewhere in this codebase),
69:     same length and index-alignment as `rsi`/`regime`.
70:     `ts = [b["t"] for b in bars]`.
71:     Call `events = rsi_events(rsi, ts, level=level, tolerance=tolerance)`.
72:     For each event in `events` with `event["event"] == "support"` (RSI approached `level` from above
73:     and bounced back up — a level=40 support in an uptrend is exactly the Malkan bull bounce):
74:     find the bar `b` in `bars` whose `"t" == event["t"]`; look up that bar's index `i` (via the `ts`
75:     list) to read `regime[i]`. Skip this event if `regime[i] != "BULL"` [MLK-GAP1: the full 5-star
76:     setup gates on Monthly+Weekly RSI regime; this single-timeframe module uses this timeframe's own
77:     `malkan_regime` as the simplified regime gate — document this simplification in the module docstring].
78:     If `require_bullish_candle` is True, also skip if `b["c"] <= b["o"]` (not a bullish/green candle).
79:     Otherwise emit `{"t": event["t"], "side": "long", "rule_id": "MLK-S1", "event": "support",
80:     "level_value": level, "regime": regime[i]}`.
81:     Return one signal per qualifying event, sorted ascending by `"t"`. Return `[]` if there are no
82:     qualifying events (this is the normal case, not an error — do not raise).
83:     """
84:     ts = [b["t"] for b in bars]
85:     events = rsi_events(rsi, ts, level=level, tolerance=tolerance)
86:     signals = []
87:     for event in events:
88:         if event["event"] == "support":
89:             t = event["t"]
90:             i = ts.index(t)  # Find index of bar with timestamp t
91:             if regime[i] != "BULL":
92:                 continue
93:             b = bars[i]
94:             if require_bullish_candle and b["c"] <= b["o"]:
95:                 continue
96:             signals.append({
97:                 "t": t,
98:                 "side": "long",
99:                 "rule_id": "MLK-S1",
100:                 "event": "support",
101:                 "level_value": level,
102:                 "regime": regime[i]
103:             })
104:     return sorted(signals, key=lambda x: x["t"])
105:
106:
107: def malkan_setup_bear(bars: list, rsi: list, regime: list, level: float = 60.0, tolerance: float = 2.0, require_bearish_candle: bool = True) -> list:
108:     """
109:     [MLK-S2, WEB_RESEARCH.md lines 135-159: "Bearish candlestick forms at 60 RSI level on daily chart = short signal"]
110:     Mirror of `malkan_setup_bull`: `events = rsi_events(rsi, ts, level=level, tolerance=tolerance)`;
111:     use `event["event"] == "rejection"` (RSI approached `level` from below and got rejected back down
112:     — the Malkan bear bounce/reject at 60). Skip unless `regime[i] == "BEAR"`.
113:     If `require_bearish_candle`, skip unless `b["c"] < b["o"]` (a bearish/red candle).
114:     Emit `{"t": event["t"], "side": "short", "rule_id": "MLK-S2", "event": "rejection",
115:     "level_value": level, "regime": regime[i]}`.
116:     Return one signal per qualifying event, sorted ascending by `"t"`.
117:     """
118:     ts = [b["t"] for b in bars]
119:     events = rsi_events(rsi, ts, level=level, tolerance=tolerance)
120:     signals = []
121:     for event in events:
122:         if event["event"] == "rejection":
123:             t = event["t"]
124:             i = ts.index(t)  # Find index of bar with timestamp t
125:             if regime[i] != "BEAR":
126:                 continue
127:             b = bars[i]
128:             if require_bearish_candle and b["c"] >= b["o"]:
129:                 continue
130:             signals.append({
131:                 "t": t,
132:                 "side": "short",
133:                 "rule_id": "MLK-S2",
134:                 "event": "rejection",
135:                 "level_value": level,
136:                 "regime": regime[i]
137:             })
138:     return sorted(signals, key=lambda x: x["t"])
```

### MyTradingSys/backtest/layers/rsi/malkan_mtf.py

SHA-256: `f7c852dfb860b861adb75359a104c11b27e2140e1e0df160268c12eabfc47051`

```text
1: """
2: MLK-GAP1: the full 5-star setup is multi-timeframe (Monthly/Weekly gate + Daily entry)
3: ... the multi-timeframe grandfather-father-son gate is out of scope [of malkan_40_60.py] and must be
4: composed later by a caller that runs this module once per timeframe and combines the results.
5:
6: This file implements the MLK-GAP1 multi-timeframe composer: Monthly and Weekly `malkan_regime` states
7: gate a Daily `malkan_setup_bull`/`malkan_setup_bear` signal, reconstructing the full Malkan 5-star setup
8: from the single-timeframe pieces `malkan_40_60.py` already implements per timeframe.
9:
10: This module performs NO new RSI/regime computation itself: monthly and weekly `rsi`/`malkan_regime`
11: values must already have been computed by running `rsi_core`/`malkan_regime` once per timeframe (via the
12: D1 timeframe layer) before calling here; this file only aligns and gates.
13:
14: The "most recently CLOSED higher-timeframe bar as of the daily timestamp" lookback semantics of `state_asof`
15: are critical: a daily bar is gated by the most recently CLOSED higher-timeframe bar, never a future one.
16: This prevents information leakage into backtests.
17: """
18:
19: from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_setup_bull, malkan_setup_bear
20:
21:
22: def state_asof(times: list, values: list, t: int):
23:     """
24:     Return the value from the LATEST entry in `times` whose value is `<= t`.
25:
26:     `times` is a list of bar-open timestamps for one (higher) timeframe, ascending, same length as
27:     `values` (its regime string at each of those times, e.g. "BULL"/"BEAR"/"RANGE"/None).
28:
29:     Return the value from the LATEST entry in `times` whose value is `<= t` (the higher-timeframe bar
30:     that was already open/closed at or before the daily timestamp `t` — a daily bar is gated by the most
31:     recently CLOSED higher-timeframe bar, never a future one). Return `None` if `times` is empty or every
32:     entry in `times` is `> t` (no higher-timeframe state exists yet at time `t`).
33:
34:     Raise `ValueError` if `len(times) != len(values)`.
35:     """
36:     if len(times) != len(values):
37:         raise ValueError("times and values must have the same length")
38:
39:     if not times:
40:         return None
41:
42:     # Find the rightmost index where times[i] <= t
43:     i = len(times) - 1
44:     while i >= 0 and times[i] > t:
45:         i -= 1
46:
47:     if i < 0:
48:         return None
49:
50:     return values[i]
51:
52:
53: def malkan_mtf_bull(bars: list, rsi: list, daily_regime: list, weekly_times: list, weekly_regime: list, monthly_times: list, monthly_regime: list, level: float = 40.0, tolerance: float = 2.0, require_bullish_candle: bool = True) -> list:
54:     """
55:     Multi-timeframe bull setup (MLK-S1-MTF): Daily regime BULL + rsi_events "support" @ 40 + bullish entry candle,
56:     gated by Weekly and Monthly RSI regimes both being BULL.
57:
58:     Call malkan_setup_bull to get base signals, then gate them with weekly and monthly regime states.
59:     """
60:     ts = [b["t"] for b in bars]
61:     base = malkan_setup_bull(bars, rsi, daily_regime, level=level, tolerance=tolerance, require_bullish_candle=require_bullish_candle)
62:
63:     signals = []
64:     for signal in base:
65:         w = state_asof(weekly_times, weekly_regime, signal["t"])
66:         m = state_asof(monthly_times, monthly_regime, signal["t"])
67:
68:         # Keep only if both higher timeframes are BULL
69:         if w == "BULL" and m == "BULL":
70:             new_signal = signal.copy()
71:             new_signal["weekly_regime"] = w
72:             new_signal["monthly_regime"] = m
73:             new_signal["rule_id"] = "MLK-S1-MTF"
74:             signals.append(new_signal)
75:
76:     return signals
77:
78:
79: def malkan_mtf_bear(bars: list, rsi: list, daily_regime: list, weekly_times: list, weekly_regime: list, monthly_times: list, monthly_regime: list, level: float = 60.0, tolerance: float = 2.0, require_bearish_candle: bool = True) -> list:
80:     """
81:     Multi-timeframe bear setup (MLK-S2-MTF): Daily regime BEAR + rsi_events "resistance" @ 60 + bearish entry candle,
82:     gated by Weekly and Monthly RSI regimes both being BEAR.
83:
84:     Call malkan_setup_bear to get base signals, then gate them with weekly and monthly regime states.
85:     """
86:     ts = [b["t"] for b in bars]
87:     base = malkan_setup_bear(bars, rsi, daily_regime, level=level, tolerance=tolerance, require_bearish_candle=require_bearish_candle)
88:
89:     signals = []
90:     for signal in base:
91:         w = state_asof(weekly_times, weekly_regime, signal["t"])
92:         m = state_asof(monthly_times, monthly_regime, signal["t"])
93:
94:         # Keep only if both higher timeframes are BEAR
95:         if w == "BEAR" and m == "BEAR":
96:             new_signal = signal.copy()
97:             new_signal["weekly_regime"] = w
98:             new_signal["monthly_regime"] = m
99:             new_signal["rule_id"] = "MLK-S2-MTF"
100:             signals.append(new_signal)
101:
102:     return signals
103:
```

## E08

### MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py

SHA-256: `70c29a5ddb3bdfb4f6ec18ea613680c3a0ef274ee12f543f43f5fdb3ac160b82`

```text
1: """
2: MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py
3:
4: Backtest driver for the RSI-layer setups that were never tested on history:
5:   --family malkan_40_60   single-timeframe regime-gated 40/60 bounce/reject setups (MLK-S1/S2)
6:   --family malkan_mtf     5-star Grandfather(1M)/Father(1w)/Son(1d) composition (MLK-S1-MTF/S2-MTF)
7:   --family rsi_ma_events  RSI x RSI-MA touch (ma_support/ma_rejection) or cross events
8: Same method and verdict rule as fabio/run_backtest.py: BTCUSDT 1m history -> tf_resample, 70/30
9: chronological IS/OOS split, grid searched on IS only, chosen params frozen and applied to OOS, PBO
10: (bt.ref_pbo.ref_pbo_cscv) on IS daily-bucketed net returns over the whole grid.
11:
12: Differences from the Fabio L1 driver (deliberate):
13: - Trades are scored NET with a bracket (default stop 1% / target 2%, the live indicator-layer bracket,
14:   MTS_USER_GUIDE.md s4) through bt.bt_engine.simulate_trade on the signal-timeframe bars (stop first if
15:   both are hit in one bar, gap through the stop fills at the open). Fees are sim.py's canonical schedule
16:   (B080, operator 2026-09-30): maker 0 / taker 5 bps; entry and stop/timeout pay taker, target pays maker.
17:   Fee constants are read from sim.py, never hardcoded here.
18: - Entry = close of the signal bar (the signal is only known at that close). One position at a time.
19: - Indicators/signals are computed ONCE over the full series (all causal) and the events split by bar index,
20:   so OOS has no RSI/regime cold start. IS trades are simulated on IS bars only (a trade still open at the
21:   IS boundary is dropped); OOS trades on the full series (open at series end: dropped).
22: - malkan_mtf: malkan_mtf.state_asof compares HTF bar OPEN times to the daily timestamp, which lets a daily
23:   bar see a weekly/monthly bar that has not closed yet. This driver passes each HTF bar's CLOSE time
24:   (tf_resample.bucket_end) instead, so the gate only ever uses closed higher-timeframe bars.
25: - The 40/60 levels live only in malkan_40_60; this driver calls it with its defaults and never names them.
26:
27: Verdict: "insufficient n" if OOS n < 30; "edge" needs OOS mean net > 0 and PBO < 0.5; else "no edge".
28: Research code only; never touches execution/ or Tom core.
29: """
30:
31: import argparse
32: import inspect
33: import json
34: import re
35: import sys
36: from collections import Counter
37: from datetime import datetime, timezone
38: from pathlib import Path
39:
40: REPO = Path(__file__).resolve().parents[4]
41: sys.path.insert(0, str(REPO))
42:
43: from MyTradingSys.backtest.bt.bt_data import load_klines
44: from MyTradingSys.backtest.bt.bt_engine import simulate_trade
45: from MyTradingSys.backtest.bt.ref_pbo import ref_pbo_cscv
46: from MyTradingSys.backtest.layers.timeframe.tf_resample import resample, bucket_end
47: from MyTradingSys.backtest.layers.runner import forward_return_stats, baseline_return_stats
48: from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
49: from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma
50: from MyTradingSys.backtest.layers.rsi.rsi_ma_events import rsi_ma_events
51: from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull, malkan_setup_bear
52: from MyTradingSys.backtest.layers.rsi.malkan_mtf import malkan_mtf_bull, malkan_mtf_bear
53:
54: REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
55: HORIZONS = (1, 5, 20)
56: STOP_PCT = 0.01
57: TARGET_PCT = 0.02
58: MAX_BARS = 100
59: MIN_OOS_N = 30
60: MAX_PBO = 0.5
61:
62:
63: def load_fees():
64:     """(taker, maker) from MyTradingSys/backtest/fees.py (single source of truth, B081)."""
65:     from MyTradingSys.backtest.fees import DERIBIT_TAKER, DERIBIT_MAKER
66:     return DERIBIT_TAKER, DERIBIT_MAKER
67:
68:
69: TAKER_FEE, MAKER_FEE = load_fees()
70:
71:
72: def load_registry():
73:     return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
74:
75:
76: def chronological_split(bars, is_frac=0.70):
77:     n_is = int(len(bars) * is_frac)
78:     return bars[:n_is], bars[n_is:], n_is
79:
80:
81: def _day(t_ms):
82:     return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).date()
83:
84:
85: def verdict(n_oos, mean_net_oos, pbo):
86:     if not n_oos or n_oos < MIN_OOS_N:
87:         return "insufficient n"
88:     if mean_net_oos is not None and mean_net_oos > 0 and pbo is not None and pbo < MAX_PBO:
89:         return "edge"
90:     return "no edge"
91:
92:
93: # ---------------------------------------------------------------- scoring
94:
95: def trades_from_events(events, bars, stop_pct=STOP_PCT, target_pct=TARGET_PCT, max_bars=MAX_BARS,
96:                        taker=None, maker=None):
97:     """Bracket-simulate events {"i","side"} (entry = close of bar i). One position at a time: an event
98:     at or before the previous trade's exit bar is skipped. Trades still open at the end of `bars` are
99:     dropped. Returns [{"i","t","side","net","exit_reason","bars_held"}], net = fraction of entry price."""
100:     taker = TAKER_FEE if taker is None else taker
101:     maker = MAKER_FEE if maker is None else maker
102:     trades, free_from = [], 0
103:     for e in sorted(events, key=lambda x: x["i"]):
104:         i, side = e["i"], e["side"]
105:         if i < free_from or i >= len(bars) - 1:
106:             continue
107:         px = bars[i]["c"]
108:         sgn = 1.0 if side == "long" else -1.0
109:         r = simulate_trade(side, px, bars[i]["t"], px * (1.0 - sgn * stop_pct), [(px * (1.0 + sgn * target_pct), 1.0)],
110:                            bars[i + 1:i + 1 + max_bars], taker_fee=taker, maker_fee=maker, max_bars=max_bars)
111:         if r["net_r"] is None:
112:             continue
113:         trades.append({"i": i, "t": bars[i]["t"], "side": side, "net": r["pnl_pct_net"] / 100.0,
114:                        "exit_reason": r["exit_reason"], "bars_held": r["bars_held"]})
115:         free_from = i + r["bars_held"]
116:     return trades
117:
118:
119: def trade_stats(trades):
120:     n = len(trades)
121:     if n == 0:
122:         return {"n": 0, "mean_net": None, "sum_net": None, "hit_rate": None, "exits": {}}
123:     nets = [t["net"] for t in trades]
124:     return {"n": n, "mean_net": sum(nets) / n, "sum_net": sum(nets),
125:             "hit_rate": sum(1 for x in nets if x > 0) / n,
126:             "exits": dict(Counter(t["exit_reason"] for t in trades))}
127:
128:
129: def daily_net_returns(trades, days):
130:     """Sum of trade net returns per UTC day (entry bar) on a COMMON day axis; 0.0 for no-trade days."""
131:     per = {}
132:     for t in trades:
133:         d = _day(t["t"])
134:         per[d] = per.get(d, 0.0) + t["net"]
135:     return [per.get(d, 0.0) for d in days]
136:
137:
138: def pbo_from_columns(cols, S=12):
139:     if len(cols) < 2:
140:         return None
141:     T = len(cols[0])
142:     S = min(S, (T // 2) * 2)
143:     if S < 4:
144:         return None
145:     M = [list(r) for r in zip(*cols)]
146:     try:
147:         return ref_pbo_cscv(M, S=S)[0]
148:     except Exception:
149:         return None
150:
151:
152: def _fwd(events, closes):
153:     if not events or not closes:
154:         return {h: {"n": 0, "mean_return": None, "hit_rate": None, "mae": None} for h in HORIZONS}
155:     return forward_return_stats([{"i": e["i"], "side": e["side"]} for e in events], closes, horizons=HORIZONS)
156:
157:
158: def grid_search_and_oos(events_fn, grid, bars, n_is, stop_pct=STOP_PCT, target_pct=TARGET_PCT,
159:                         max_bars=MAX_BARS, taker=None, maker=None, min_events=5, S=12):
160:     """events_fn(params) -> events over the FULL `bars` series. Chooses the IS-best variant by mean net
161:     per trade (>= min_events IS trades), reports IS and OOS stats and PBO over the IS grid."""
162:     kw = dict(stop_pct=stop_pct, target_pct=target_pct, max_bars=max_bars, taker=taker, maker=maker)
163:     if n_is < 50 or len(bars) - n_is < 10:
164:         return {"chosen": None, "reason": "too_few_bars", "pbo": None, "n_variants": len(grid),
165:                 "verdict": "insufficient n"}
166:     bars_is = bars[:n_is]
167:     days = sorted({_day(b["t"]) for b in bars_is})
168:     results, cols = [], []
169:     for params in grid:
170:         try:
171:             ev = events_fn(params)
172:         except Exception as exc:
173:             results.append({"params": params, "error": str(exc), "n_is": 0, "mean_is": None})
174:             cols.append([0.0] * len(days))
175:             continue
176:         tr = trades_from_events([e for e in ev if e["i"] < n_is], bars_is, **kw)
177:         st = trade_stats(tr)
178:         results.append({"params": params, "n_is": st["n"], "mean_is": st["mean_net"], "is_stats": st,
179:                         "events_is": [e for e in ev if e["i"] < n_is]})
180:         cols.append(daily_net_returns(tr, days))
181:     pbo_val = pbo_from_columns(cols, S=S)
182:     summary = [{"params": r["params"], "n_is": r["n_is"], "mean_is": r["mean_is"]} for r in results]
183:     ok = [r for r in results if r["n_is"] >= min_events and r["mean_is"] is not None]
184:     if not ok:
185:         return {"chosen": None, "reason": "no_variant_with_min_events", "pbo": pbo_val,
186:                 "n_variants": len(grid), "all_grid": summary, "verdict": "insufficient n"}
187:     best = max(ok, key=lambda r: r["mean_is"])
188:     ev_oos = [e for e in events_fn(best["params"]) if e["i"] >= n_is]
189:     tr_oos = trades_from_events(ev_oos, bars, **kw)
190:     oos = trade_stats(tr_oos)
191:     return {"chosen": best["params"], "n_variants": len(grid), "is_stats": best["is_stats"], "oos_stats": oos,
192:             "is_fwd_gross": _fwd(best["events_is"], [b["c"] for b in bars_is]),
193:             "oos_fwd_gross": _fwd(ev_oos, [b["c"] for b in bars]),
194:             "pbo": pbo_val, "all_grid": summary, "verdict": verdict(oos["n"], oos["mean_net"], pbo_val)}
195:
196:
197: # ---------------------------------------------------------------- signal families
198:
199: def safe_rsi(closes, period):
200:     """rsi_core, but an all-None series (instead of ValueError) when the series is too short."""
201:     if len(closes) <= period:
202:         return [None] * len(closes)
203:     return rsi_core(closes, period)
204:
205:
206: def signals_to_events(signals, bars):
207:     idx = {b["t"]: i for i, b in enumerate(bars)}
208:     return [{"i": idx[s["t"]], "side": s["side"]} for s in sorted(signals, key=lambda s: s["t"])]
209:
210:
211: def malkan_events(bars, p):
212:     """malkan_40_60: bull (MLK-S1) + bear (MLK-S2) single-timeframe setups. p: period, tolerance, lookback."""
213:     rsi = safe_rsi([b["c"] for b in bars], p["period"])
214:     regime = malkan_regime(rsi, lookback=p["lookback"])
215:     sigs = malkan_setup_bull(bars, rsi, regime, tolerance=p["tolerance"]) + \
216:         malkan_setup_bear(bars, rsi, regime, tolerance=p["tolerance"])
217:     return signals_to_events(sigs, bars)
218:
219:
220: def htf_close_times(htf_bars, tf, registry):
221:     """Bar CLOSE times for higher-timeframe bars labelled by open time (no-look-ahead gate)."""
222:     return [bucket_end(b["t"], tf, registry) for b in htf_bars]
223:
224:
225: def malkan_mtf_events(bars, htf, registry, p):
226:     """5-star: entry-tf (1d) setup gated by closed 1w and 1M regimes. htf = {"1w": bars, "1M": bars}.
227:     p: period, tolerance, lookback (entry tf), htf_lookback."""
228:     rsi = safe_rsi([b["c"] for b in bars], p["period"])
229:     regime = malkan_regime(rsi, lookback=p["lookback"])
230:     gates = []
231:     for tf in ("1w", "1M"):
232:         hb = htf[tf]
233:         hr = malkan_regime(safe_rsi([b["c"] for b in hb], p["period"]), lookback=p["htf_lookback"])
234:         gates += [htf_close_times(hb, tf, registry), hr]
235:     sigs = malkan_mtf_bull(bars, rsi, regime, *gates, tolerance=p["tolerance"]) + \
236:         malkan_mtf_bear(bars, rsi, regime, *gates, tolerance=p["tolerance"])
237:     return signals_to_events(sigs, bars)
238:
239:
240: def rsi_ma_to_events(events, bars, mode):
241:     if mode not in ("touch", "cross"):
242:         raise ValueError("mode must be touch or cross")
243:     idx = {b["t"]: i for i, b in enumerate(bars)}
244:     out = []
245:     for e in events:
246:         side = None
247:         if mode == "touch":
248:             side = {"ma_support": "long", "ma_rejection": "short"}.get(e["event"])
249:         elif e["event"] == "cross":
250:             side = "long" if e.get("direction") == "up" else "short"
251:         if side:
252:             out.append({"i": idx[e["t"]], "side": side})
253:     return sorted(out, key=lambda e: e["i"])
254:
255:
256: def rsi_ma_family_events(bars, p):
257:     """rsi_ma_events: p: period, ma_length, tolerance (RSI points), mode touch|cross."""
258:     rsi = safe_rsi([b["c"] for b in bars], p["period"])
259:     ma = rsi_ma(rsi, "SMA", p["ma_length"])
260:     ev = rsi_ma_events(rsi, ma, [b["t"] for b in bars], p["tolerance"])
261:     return rsi_ma_to_events(ev, bars, p["mode"])
262:
263:
264: GRIDS = {
265:     "malkan_40_60": [{"period": pe, "tolerance": tol, "lookback": lb}
266:                      for pe in (10, 14, 21) for tol in (1.0, 2.0, 3.0) for lb in (10, 20, 40)],
267:     "malkan_mtf": [{"period": pe, "tolerance": tol, "lookback": 20, "htf_lookback": hl}
268:                    for pe in (9, 14) for tol in (1.0, 2.0, 3.0) for hl in (3, 6, 12)],
269:     "rsi_ma_events": [{"period": pe, "ma_length": ml, "tolerance": tol, "mode": m}
270:                       for pe in (9, 14) for ml in (9, 14) for tol in (0.5, 1.0, 2.0) for m in ("touch", "cross")],
271: }
272: DEFAULT_TFS = {"malkan_40_60": ["1h", "4h", "1d"], "malkan_mtf": ["1d"], "rsi_ma_events": ["15m", "1h", "4h"]}
273:
274:
275: def run_family(family, bars_1m, registry, tfs=None, grid=None, out_dir=None, **kw):
276:     """Returns {tf: {"n_bars","n_bars_is","n_bars_oos","baseline_oos","result": grid_search_and_oos(...)}}.
277:     kw: stop_pct, target_pct, max_bars, taker, maker, min_events."""
278:     if family not in GRIDS:
279:         raise ValueError("unknown family %r (expected one of %s)" % (family, ", ".join(GRIDS)))
280:     grid = grid or GRIDS[family]
281:     out = {}
282:     for tf in tfs or DEFAULT_TFS[family]:
283:         bars = resample(bars_1m, tf, registry)
284:         n_is = int(len(bars) * 0.70)
285:         if family == "malkan_40_60":
286:             fn = lambda p, b=bars: malkan_events(b, p)
287:         elif family == "rsi_ma_events":
288:             fn = lambda p, b=bars: rsi_ma_family_events(b, p)
289:         else:
290:             htf = {t: resample(bars_1m, t, registry) for t in ("1w", "1M")}
291:             fn = lambda p, b=bars, h=htf: malkan_mtf_events(b, h, registry, p)
292:         res = {"n_bars": len(bars), "n_bars_is": n_is, "n_bars_oos": len(bars) - n_is}
293:         if len(bars) - n_is > 0:
294:             res["baseline_oos"] = baseline_return_stats([b["c"] for b in bars[n_is:]], horizons=HORIZONS)
295:         res["result"] = grid_search_and_oos(fn, grid, bars, n_is, **kw)
296:         out[tf] = res
297:         if out_dir is not None:
298:             with open(Path(out_dir) / ("%s_%s_result.json" % (family, tf)), "w", newline="\n", encoding="utf-8") as f:
299:                 json.dump(res, f, indent=1, default=str)
300:     return out
301:
302:
303: def _fmt(x, pct=False, nd=3):
304:     if x is None:
305:         return "-"
306:     return ("%.*f%%" % (nd, x * 100)) if pct else ("%.*f" % (nd, x))
307:
308:
309: def render_report(summary):
310:     fam = summary["family"]
311:     lines = ["# %s backtest (IS/OOS 70/30)" % fam, "",
312:              "Fees: taker %.4f / maker %.4f (sim.py canonical); bracket stop %.2f%% / target %.2f%%. "
313:              "Verdict: OOS n >= %d, OOS mean net > 0, PBO < %.1f -> edge." % (
314:                  TAKER_FEE, MAKER_FEE, STOP_PCT * 100, TARGET_PCT * 100, MIN_OOS_N, MAX_PBO), "",
315:              "| TF | Variants | Chosen params | IS n / mean net | OOS n / mean net / hit | PBO | Verdict |",
316:              "|---|---|---|---|---|---|---|"]
317:     for tf, r in summary["tfs"].items():
318:         res = r["result"]
319:         i, o = res.get("is_stats") or {}, res.get("oos_stats") or {}
320:         lines.append("| %s | %s | %s | %s / %s | %s / %s / %s | %s | %s |" % (
321:             tf, res.get("n_variants"), json.dumps(res.get("chosen")) if res.get("chosen") else res.get("reason", "-"),
322:             i.get("n", "-"), _fmt(i.get("mean_net"), True), o.get("n", "-"), _fmt(o.get("mean_net"), True),
323:             _fmt(o.get("hit_rate"), True, 1), _fmt(res.get("pbo")), res.get("verdict")))
324:     return "\n".join(lines) + "\n"
325:
326:
327: def main():
328:     ap = argparse.ArgumentParser()
329:     ap.add_argument("--family", required=True, choices=sorted(GRIDS))
330:     ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
331:     ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
332:     ap.add_argument("--out", default=None, help="default Dumps/backtest/runs/rsi_<family>")
333:     ap.add_argument("--tfs", default=None, help="comma list; default per family (malkan_mtf: entry tf, gates fixed 1w+1M)")
334:     ap.add_argument("--stop-pct", type=float, default=STOP_PCT)
335:     ap.add_argument("--target-pct", type=float, default=TARGET_PCT)
336:     ap.add_argument("--max-bars", type=int, default=MAX_BARS)
337:     ap.add_argument("--min-events", type=int, default=5)
338:     args = ap.parse_args()
339:
340:     out_dir = Path(args.out or REPO / "Dumps" / "backtest" / "runs" / ("rsi_" + args.family))
341:     out_dir.mkdir(parents=True, exist_ok=True)
342:     registry = load_registry()
343:     bars_1m = load_klines(args.data_root)
344:     last_t = bars_1m[-1]["t"] if bars_1m else 0
345:     bars_1m += [b for b in load_klines(args.data_root2) if b["t"] > last_t]
346:     bars_1m.sort(key=lambda b: b["t"])
347:     print("Loaded %d 1m bars" % len(bars_1m), file=sys.stderr, flush=True)
348:     if not bars_1m:
349:         print("No data found under --data-root/--data-root2", file=sys.stderr)
350:         return 2
351:
352:     tfs = args.tfs.split(",") if args.tfs else None
353:     res = run_family(args.family, bars_1m, registry, tfs=tfs, out_dir=out_dir, stop_pct=args.stop_pct,
354:                      target_pct=args.target_pct, max_bars=args.max_bars, min_events=args.min_events)
355:     summary = {"family": args.family, "fees": {"taker": TAKER_FEE, "maker": MAKER_FEE},
356:                "stop_pct": args.stop_pct, "target_pct": args.target_pct, "max_bars": args.max_bars, "tfs": res}
357:     with open(out_dir / "summary.json", "w", newline="\n", encoding="utf-8") as f:
358:         json.dump(summary, f, indent=1, default=str)
359:     with open(out_dir / "REPORT.md", "w", newline="\n", encoding="utf-8") as f:
360:         f.write(render_report(summary))
361:     print("Done. Results in %s" % out_dir, file=sys.stderr)
362:     return 0
363:
364:
365: if __name__ == "__main__":
366:     sys.exit(main())
```

## E09

### MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_HISTORY.md

SHA-256: `2ab4fc5db5370dda7ecf4754f84a6b4fc92aee23f776b6fbe8bbcbdf338a8f88`

```text
1: # RSI line of work: what was planned, built, tested, and why it stopped (2026-10-09)
2:
3: Operator ask: "What happened to RSI setups and research - it was stalled."
4: Method: every claim below cites a file I read in worktree `mts-rsi` (origin/fast-track 46ef159) or, for run
5: outputs and the trade ledger, the live tree read-only (`Dumps/backtest/runs/*`, `MyTradingSys/execution/trade_ledger.jsonl`;
6: both are gitignored runtime data). MATCH = stated by a file I read. NOT_IN_DATA = I looked and the file set has no answer.
7: Paths are relative to `MyTradingSys/` unless prefixed. `WR` = `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md`.
8:
9: ## 1. Short answer
10:
11: 1. The RSI system is Vishal B Malkan's ("MalkanView") RSI 40/60 method. It was designed on 2026-09-28, fully built as an offline layer the same
12:    day, and wired to the live testnet runner on 2026-09-29. [MATCH: research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md; git log 4f74c20..0817968..4d1bc36]
13: 2. What was backtested is NOT Malkan's actual 5-star setup. Every backtest used the project's generic 1% stop / 2% target / 100-bar bracket and a
14:    single-timeframe regime. The multi-timeframe "Grandfather-Father-Son" composer (`malkan_mtf`) has a backtest driver but no run exists on disk.
15:    [MATCH: LAYER_PROVENANCE_AUDIT.md:70-73; run_rsi_backtest.py:9-12; NOT_IN_DATA: no `rsi_malkan_mtf` folder in `Dumps/backtest/runs/`, listing: fabio_l1, fabio_l1_smoke, l1_2ee35b1e79, rsi_malkan_40_60, rsi_rsi_ma_events, t055_c1, t055_c1_1h, t055_c2, t055_c3_imb]
16: 3. The tests that were run all came back "no edge" (numbers in section 4), so on 2026-10-06/07 the RSI work was closed as a verdict row, not as a
17:    finished investigation. Nobody holds an open item to finish it. [MATCH: MARKET_GUIDE_RESULTS_2026-10-07.md:20-22; scripts/dev/market_guide_verdicts.json:6; NOT_IN_DATA: no RSI/Malkan row in items/INDEX.md other than B128:93, which is only the rsi:cross side mapping]
18: 4. Malkan's own words were never extracted. Three Malkan transcripts have sat in `raw_transcripts_canonical/` since 2026-09-28
19:    (`-CBvFi40sIQ`, `cQ-y1oULkBw`, `Wvq1TZh8aF0`, 7,954 + 16,777 + 39,058 bytes) but there is no `extracts/processed/malkan*` folder, and the
20:    provenance audit still lists "fetch a Malkan transcript" as an open question. [MATCH: `ls extracts/processed` = cryptocred, fabio_valentini; LAYER_PROVENANCE_AUDIT.md:206; research/fast_track_2026-09-27/NEXT_SESSION_PLAN.md:129 "No video extraction yet"]
21: 5. Live, the RSI alerts keep firing and trade on the testnet, and 1h RSI is the only layer that reached targets. That is 4 trades, not evidence.
22:    [MATCH: trade_ledger.jsonl parse below; CONSOLIDATED_ROADMAP_2026-10-09.md:32]
23:
24: ## 2. Timeline
25:
26: | Date | Event | Source |
27: |---|---|---|
28: | 2026-08-29 | "Malkans RSI 40/60 integrated" into the Tom chart layout (E4) | system/COMPILED_DECISIONS.md:40 |
29: | 2026-09-01 | VVP-001 demotes RSI: removed from default layout, "NEVER let RSI or BB override a Tom-validated setup" | research/visual_validation_protocol_vvp001.md:116,119; BUGS.md T019 (line 105) |
30: | 2026-09-28 | Operator directive (verbatim): Malkan 40-60 is private to its own sub-layer; RSI MA support; "slippage" tolerance around 40/60 to be measured; alerts per timeframe incl. 1,2,3,10 min and 2d,3d,5d; fine-tune later on testnet | PROJECT_VISION.md:189-203 |
31: | 2026-09-28 | Opus design D1-D7 (timeframe layer + rsi_core / rsi_ma / rsi_events / malkan_40_60) | research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md |
32: | 2026-09-28 | Web research on Malkan (secondary sources: eLearnMarkets blog, Chartink screeners, YouTube titles). 10 gaps listed | WR (400 lines) |
33: | 2026-09-28 | Built and committed: rsi_core + rsi_ma (d9eba41), rsi_events (77be7ef), malkan_40_60 (6bce07f), rsi_ma_events (13558c0), malkan_mtf (ae30eda), tolerance_sweep (8ea2f68), runner (d9f0d2a) | git log -- backtest/layers/rsi |
34: | 2026-09-28 | L1 backtest report (D3 tolerance study) | backtest/layers/BACKTEST_L1_REPORT.md |
35: | 2026-09-29 | Live runner: RSI-40 tol 0.5 on 1h/15m (0817968); malkan_bull / malkan_bear added (4d1bc36); failure-event side (adc75b3). 5m added 2026-09-30 (7058bc2) | NEXT_SESSION_PLAN.md:145; SUPERVISOR_LOG.md:185,221 |
36: | 2026-09-30 | Cloud Sonnet writes `run_rsi_backtest.py` (35 tests) with families malkan_40_60, malkan_mtf, rsi_ma_events | research/fast_track_2026-09-27/DSA_BACKLOG.md:23-24 |
37: | 2026-10-04 | Layer provenance audit: rsi = 4 SOURCED, 10 CONCEPT-ONLY, 12 NO-SOURCE | research/LAYER_PROVENANCE_AUDIT.md:46 |
38: | 2026-10-07 | Desktop runs malkan_40_60 and rsi_ma_events; both NO-EDGE. malkan_mtf not run. Verdict table written | research/MARKET_GUIDE_RESULTS_2026-10-07.md:20-22,36 |
39: | 2026-10-08 | Closeout: rsi:cross now side-by-level (40 down = short, 60 up = long, else no side); the trade blocklist is emptied for testnet data collection and parked | items/B128 row M29-11; research/AUDIT_CLOSEOUT_2026-10-07.md:53; execution/auto_trader_config.json:2,104-111 |
40: | 2026-10-09 | Volume study re-tests RSI 40/60 cross events with volume: one 4h DEV pass, failed VALIDATION (n=50, net -2 bp) | research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:96 |
41:
42: ## 3. What exists (built)
43:
44: All under `backtest/layers/rsi/`: `rsi_core` (Wilder RSI, period 14), `rsi_ma` (SMA/EMA/RMA/WMA of RSI, default SMA 14), `rsi_events` (tolerance band
45: support / rejection / failure / cross), `malkan_40_60` (20-bar regime + bounce/reject setups, lo 40 / hi 60 / tolerance 2),
46: `malkan_mtf` (weekly+monthly regime gate on a daily entry), `rsi_ma_events`, `tolerance_sweep`, `run_rsi_backtest.py`, `observation.py`
47: (RSI block for the consensus writer, wired 2026-10-08, commit 2fccf66). Params with provenance: `params/default.json`,
48: `params/malkan_40_60_default.json`. Live detectors: `alerts/live_layers.py` (`rsi_level_layer` fixed at level 40, tol 0.5, lines 142-143;
49: `malkan_bull_layer` / `malkan_bear_layer`, lines 103-119).
50:
51: ## 4. What was tested, with numbers
52:
53: | Test | Result | Source |
54: |---|---|---|
55: | D3 level-event tolerance study, BTCUSDT 1m 2022-01..2026-09-26 (2,491,200 bars), IS 70 / OOS 30, tolerance 0.5-5.0 | 8 cells (15m, 1h, 4h, 1d x level 40 long, 60 short). Only 1h / level-40 support / tol 0.5 has PBO 0.030 (OOS n 89, +0.043% mean h5, 56.2% hit). All other cells PBO 0.39-0.91. 15m: OOS mean near zero or negative | BACKTEST_L1_REPORT.md:16-25 (table), 28-32 |
56: | That one good cell vs cost | +0.043% gross OOS is below the 14 bp round-trip cost used elsewhere | MARKET_GUIDE_RESULTS_2026-10-07.md:20; SUPERVISOR_LOG.md:114 |
57: | malkan_40_60, 27 variants x 3 tf, bracket 1%/2%, taker 5 bp | 1h: OOS n 43, mean net -0.092%, hit 32.6%, PBO 0.760, no edge. 4h: OOS n 17, -0.203%, insufficient n. 1d: OOS n 5, insufficient n | `Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md` (read) |
58: | rsi_ma_events, 24 variants x 2 tf | 1h: OOS n 357, -0.199% net, PBO 0.352. 4h: OOS n 69, -0.216%, PBO 0.455. Both no edge. 15m dropped after a 30-minute timeout | `Dumps/backtest/runs/rsi_rsi_ma_events/REPORT.md` (read) |
59: | malkan_mtf (5-star, 1M + 1w gate, 1d entry) | NOT_IN_DATA: driver exists (run_rsi_backtest.py:6,225-236,267), default tf 1d (line 272); no run output | see section 1 item 2 |
60: | Volume x RSI(14) cross 60 up / 40 down (V1 DEV, 4h) | RSI down-cross 40 with unconfirmed volume: pass on DEV (+70 bp net), then failed VALIDATION n=50, -2 bp [-68,+64] | VOLUME_RESEARCH_REPORT_2026-10-09.md:96 |
61: | Live testnet ledger (389 rows to 2026-10-09T08:08Z; I parsed the JSONL) | rsi_events 1h: 4 trades, 4 wins, +11.46 USD net. 15m: 11 rows, 6 wins, +2.44 (1 row has no P/L). 5m: 29 trades, 11 wins, +0.25. malkan_bull / malkan_bear: 0 ledger rows although accounts jishu_7 / jishu_8 are mapped (auto_trader_config.json:8-9). For scale, turn_of_candle 1m = 311 of 389 rows | `execution/trade_ledger.jsonl` (live tree, read-only) |
62:
63: Note on the 1h live result: 4 trades are inside the noise. The backtest of the same cell (L1 report) shows +0.043% gross OOS, which does not
64: cover fees. These two facts do not contradict; neither is proof.
65:
66: ## 5. Where and why it stalled (quotes)
67:
68: 1. **The tests did not test Malkan.** The driver's bracket is its own: `LAYER_PROVENANCE_AUDIT.md:70-72` R21-R23: stop 1%, target 2%, time exit
69:    100 bars, all "NO-SOURCE", with "Malkan's target is an RSI level, not a price %." (line 71) Malkan's exit (WR:123 stop below signal-candle low, WR:128
70:    "Target is 60 RSI level on daily chart", WR:132-133 hold while monthly+weekly stay above 60) was never coded as an exit.
71: 2. **The regime gate is a guess.** Audit R10-R11 (lines 59-60, CONCEPT-ONLY): "the second clause (max >= 60, min <= 40) has no quote", lookback 20 bars "no window in WR".
72:    R16 (line 65): the single-timeframe module gates on the entry timeframe's own regime, "WR:77 gates on Monthly + Weekly, not the entry TF"
73:    (self-documented as MLK-GAP1 in malkan_40_60.py:13-16).
74: 3. **Grids were tuning, which the provenance rule forbids.** Audit R19-R20 (lines 68-69), R25 (line 74): period 10/14/21, tolerance, lookback, HTF lookback were swept; "Sweeping a sourced value (period) is tuning."
75:    Notes item 4 (lines 197-199): "these grids should not choose live values."
76: 4. **Sample too small on the timeframes Malkan actually uses.** malkan_40_60 4h OOS n 17 and 1d OOS n 5 (REPORT.md above). Malkan's 5-star is a
77:    daily/weekly/monthly swing setup: WR:100-134 and the Samco transcript line 26-35 below. The live system, by contrast, fires on 5m/15m/1h
78:    (auto_trader_config.json:5-7), where Malkan gives no rule (WR gap 5: "No specific text found on crypto vs. equity differences").
79: 5. **Malkan's own words were never read.** SUPERVISOR_LOG.md:47 "Malkan rules have no verbatim extract yet (only research/malkan_rsi_2026-09-28/WEB_RESEARCH.md; NUC 040 reply PARTIAL)";
80:    NEXT_SESSION_PLAN.md:129 "No video extraction yet"; audit Q1 (line 206) "fetch a Malkan transcript or page capture for period 14 (R01), the regime window (R11) and the band (R12)".
81:    The transcripts are in the repo already (see section 6). LAYER_PROVENANCE_AUDIT.md:191-193 (notes item 1) states: "no Malkan transcript or saved page is in the repo" - that is wrong as of
82:    commit 80b2edd (2026-09-28, "first Malkan transcript") and ba4a396.
83: 6. **Priority moved.** From 2026-10-01 the roadmap centres on Tom core and Fabio ("two cores"); RSI is a sub-line there (ARCHITECTURE_TWO_CORES_2026-10-01.md:23,39,58). The 10-07 market-guide
84:    pass classified RSI as context: "None of them is a proven entry signal on our data" (MARKET_GUIDE_RESULTS_2026-10-07.md:32). The trade blocklist that stopped RSI-15m
85:    testnet trades was parked on 2026-10-08 for data collection (auto_trader_config.json:2,111). No owner or next step was recorded for RSI.
86: 7. **Bookkeeping ambiguity** (does not change the verdict): the backlog line "never tested historically" (DSA_BACKLOG.md:23) was written 09-30, before the 10-07 runs; it is still unchecked for malkan_mtf.
87:
88: ## 6. What the repo's Malkan transcripts say (read 2026-10-09; not yet an extract, no quote-gate run)
89:
90: Labels: T3 practitioner content. The Samco file is a third-party host (Apurva Sheth, Samco) explaining Malkan's strategy (header line 5: "third-party (Samco), secondary source").
91: The other two are Malkan's own channel, auto-captions (garbled in places). The files are single long lines, so line numbers apply only to the Samco file.
92:
93: - Period and levels, Samco host: "you have 14 period RSI ... on monthly weekly and daily" (`-CBvFi40sIQ_raw.txt:26-27`); long = monthly RSI above 60, weekly above 60, "daily RSI i.e. 14 day RSI must be near 40" (lines 28-30); short = monthly below 40, weekly below 40, "daily RSI must be at around 60" (lines 42-44). This is the first transcript support for period 14 (audit R01 was CONCEPT-ONLY, WR:35 is a researcher bullet).
94: - Entry/stop, Samco host: entry "above the high of the signal candle", stop "below the low of the signal candle" (lines 34-35). No RSI-60 target is stated in this transcript; that target exists only in the eLearnMarkets blog quoted in WR:128 (secondary).
95: - Waiting: "So you have to wait patiently" (line 74) - said of the rarity of all three criteria lining up in the same stock.
96: - Malkan, `Wvq1TZh8aF0_raw.txt:8` (published 2026-04-15): "bearish below 40, bullish above 60, sideways between 40 and 60, so this is our fixed cut"; the most powerful divergence comes "near 60 bearish ... and near 40" bullish; seven-star = "RSI monthly is above 60 and then there is divergence in the daily".
97: - **Conflict with the repo:** WR "Setup 2: 7-Star" says 7-star = 5-star plus "Previous 3 consecutive days' RSI > 60" (Chartink screener text, secondary). Malkan's own video defines seven-star as monthly above 60 plus a daily divergence. The repo's WR version is wrong or screener-specific; it is unused in code (no 7-star module).
98: - Malkan, `cQ-y1oULkBw_raw.txt:8`: "shorter duration of number of divergences, the stronger the divergence" (3, 5, 7 bars; 15-40 bars "diluted completely").
99: - NOT_IN_DATA in all three files: any crypto or intraday rule, RSI-60 profit target, regime lookback window, tolerance around 40/60.
100:
101: ## 7. What is open now
102:
103: | Open item | State |
104: |---|---|
105: | Extract Malkan transcripts through the quote gate (`verify_extract_quotes.py`) | not started; 3 files ready |
106: | Backtest malkan_mtf (1M + 1w gates, 1d entry) | driver written, no run |
107: | Code Malkan's own exit (signal-candle stop, RSI-60/40 target, HTF-hold) instead of 1%/2%/100 bars | audit Q2 is an "operator call", no answer recorded |
108: | Replace NO-SOURCE items R02-R05, R07, R19-R23, R25-R26 (remove or source) | no ticket found |
109: | Divergence (Malkan's core RSI edge per Wvq1TZh8aF0 and cQ-y1oULkBw) | not in code as an RSI-divergence layer; DIVERGENCE_AUDIT_AND_RESEARCH.md only lists it as "UNVERIFIED-WEB" |
110: | Daily/weekly/monthly RSI on BTC | data present (LAYER_READINESS.md:200-204 says monthly+weekly computable) |
111: | Live malkan_bull / malkan_bear produce 0 ledger trades | cause not investigated here |
112: | audit Q3 / Q4 (tolerance 0 invalid; HTF open-vs-close leak in `state_asof` doc) | driver passes close times (run_rsi_backtest.py:22-24); doc fix open |
113:
114: Suggested order (cheapest tier first, not started): T0 extract the 3 transcripts; T2 one pre-registered backtest of the sourced rule only (5-star long/short on 1d with
115: the 1w+1M RSI gates, Malkan's stop/target/hold); T3 operator decision on audit Q2. Anything on 5m/15m stays "context, no rule".
```

### MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md

SHA-256: `eca6ff01506f101723ef9f20f40120236a5f493fb8963292cd3fd82a112471e9`

```text
1: # MARKET GUIDE: results (2026-10-07)
2:
3: Executes MARKET_GUIDE_EXECUTION_PLAN_2026-10-07.md after revalidation. Session MTS-2026-10-07-1330Z-APP-BLD-market-guide.
4:
5: ## Revalidation: what was really needed
6: - Built: one read-only digest, `scripts/dev/market_guide.py` (+14 tests, `mts market` verb, MTS_USER_GUIDE row). It computes MA / RSI /
7:   candle state itself from `market_data/klines/BTCUSDT_{5m,15m,1h}.json` (4h resampled from 1h) and summarises
8:   `runtime/alerts/*.jsonl` (turn_of_candle excluded). Writes `runtime/market_guide.md` atomically. Observation only: no side, not
9:   imported by execution code, never a Tom filter.
10: - Dropped from the plan (not needed for the ask): new live layers in the registry (ma / candles / rsi_setup) and the
11:   layers/alerts/ claim. The guide reads state directly, so no live-imported file was edited and nothing needs a restart.
12: - B103 does not block this work: funding archive covers 2020-01-01..2026-08-31 (7305 settlements); P0/P1 DEV runs use full funding.
13: - Kept open: 7-day shadow (nothing new runs in the live loop, so nothing to shadow); MA backtest (next step below).
14:
15: ## Verdict table (which signals carry value)
16: Gate: OOS n >= 30, OOS mean net > 0, PBO < 0.5 (layer drivers); candle pilot triage per PRE_REG_CANDLE_PILOT.md s5.
17:
18: | Layer / signal | Verdict | Evidence |
19: |---|---|---|
20: | rsi_events 40/60 level (live) | NO-EDGE | backtest/layers/BACKTEST_L1_REPORT.md:16-25: best cell 1h/40 OOS +0.043% gross (n 89) < 14 bps cost; other cells PBO >= 0.39 |
21: | rsi malkan_40_60 (live malkan_*) | NO-EDGE / insufficient n | run 2026-10-07 Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md: 1h OOS n 43, -0.092% net, PBO 0.760; 4h n 17, 1d n 5 |
22: | rsi_ma_events (offline only) | NO-EDGE | run 2026-10-07 Dumps/backtest/runs/rsi_rsi_ma_events/REPORT.md (1h+4h only; 15m dropped after a 30-min timeout): 1h OOS n 357, -0.199% net, PBO 0.352; 4h n 69, -0.216%, PBO 0.455 |
23: | fabio cvd_absorption / escalation / volume_fvg | NO-EDGE | backtest/layers/fabio/FABIO_L1_REPORT.md:33-58 |
24: | cryptocred sr_flip / fib_pullback | NO-EDGE | research/AUDIT_CLOSEOUT_2026-10-07.md:25 |
25: | positioning funding_cvd_fade | NO-EDGE | AUDIT_CLOSEOUT_2026-10-07.md:23 (OOS -0.0453%) |
26: | session momentum | NO-EDGE | AUDIT_CLOSEOUT_2026-10-07.md:24 (Sharpe 0.0084) |
27: | turn_of_candle toc_m14 | timer, excluded | no gross edge (closeout) |
28: | Candles: operator daily-open rule P0a/c/s/e | FAIL triage | candle_patterns_2026-10-04/P0_RESULTS.md: P0a -0.7 bps/trade [-43, 43], p vs random 0.789 |
29: | Candles: 18 classical patterns x h1/3/5, 1d + 1h | 0 of 108 pass triage | P1_RESULTS.md; closest: three_white_soldiers 1d h5 +222 bps [19, 452] but RC p 0.464; 24 trials INSUFFICIENT-N |
30: | MA setups (literature) | UNTESTED here | btc_ma_2026-10-03/Q_ALL_ma_findings.md: only the ~1-week log price/MA ratio has OOS net evidence (Wei et al. 2024, ends 2022-03); crossovers incl. 50/200: no validated evidence |
31:
32: Answer to the operator question: the layers fire, and as context they say what the market is doing (RSI regime, MA position,
33: candle shape, S/R flips, absorption). None of them is a proven entry signal on our data. The guide prints each row with its tag.
34:
35: ## Trials
36: Candle pilot: 130 rows in TRIAL_REGISTRY.csv (P0 10, P1 120). RSI malkan_40_60: 27 variants x 3 tf; rsi_ma_events: 24 variants x 2 tf. VALIDATION/HOLDOUT untouched.
37:
38: ## Next (only if wanted)
39: 1. MA layer backtest, pre-registered: log price/MA ratio 1/2/4/10/20w (hypothesis: 1w best), then close vs SMA 20/50/100/200d;
40:    position-series evaluator, daily, OOS post-2024-09. Skip golden cross / Pi Cycle (12 and 2 events).
41: 2. Open MA briefs sonnet-02 (adaptive MAs) and sonnet-03 (regime/factors): not reached in the consolidated pass.
42: 3. Optional: schedule `mts market` (or a launch-*.vbs like make_status) so runtime/market_guide.md refreshes without asking.
43:
44: ## Notes for review
45: - run_p1.py: worker relaxed two of its own RC sanity tests after they failed on finished code (null test now allows <= 3 false
46:   rejections in 12 noise sets). Pre-reg definitions unchanged. Open choices it made are listed in P1_RESULTS.md.
47: - Spot-checks: guide RSI(14) 5m recomputed independently (25.9 = 25.9); P1 three_white_soldiers row read from P1_RESULTS.md:40-42;
48:   Wei et al. 2024 PDF title/DOI matched.
```

## E10

### extracts/processed/malkan/extract_Wvq1TZh8aF0.md

SHA-256: `fecd0d088bb73fd1d742e128e2a02d4b5e2435601f46f4991123e8ea9e048b7d`

```text
1: # Extract Wvq1TZh8aF0 - Malkan "RSI Divergence Explained Simply" (2026-04-15, auto-captions, uploader Malkansview)
2: Phase 1, one transcript, quotes verbatim (auto-caption noise kept). Tags: T3 = practitioner, own words. Nothing here is an MTS rule until the operator approves it and our own OOS backtest passes.
3: Instrument: Indian equities / Nifty on daily, weekly, monthly bars. Not crypto, not intraday. Translation_warning: yes (auto-captions, Hindi->English noise).
4:
5: ## D1 What is compared
6: > "What do we have to compare? Close to close. Because RSI is based on closing price."
7: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
8:
9: ## D2 Minimum and maximum bars between the two points
10: > "How many candles are needed? Three."
11: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
12:
13: > "at the most 10 times divergence. If you have 30 times divergence, 50 times divergence, that is diluted."
14: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
15:
16: > "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10."
17: **Source GPS: Wvq1TZh8aF0 | MIDDLE** T3
18:
19: ## D3 Where in RSI the divergence is strongest
20: > "the most powerful divergence come near 60 bearish divergence and the most powerful bullish divergence comes near 40."
21: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
22:
23: > "because there will also be reverse divergences which will negate that divergence or its effect will be very short term."
24: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
25:
26: ## D4 Decimals count
27: > "Sometimes there is divergence in decimals and that will also be acceptable."
28: **Source GPS: Wvq1TZh8aF0 | END** T3
29:
30: ## D5 Confirmation, entry, stop
31: > "Not confirmed. Need confirmation."
32: **Source GPS: Wvq1TZh8aF0 | BEGIN** T3
33:
34: > "It will be confirmed when he shows the red candle."
35: **Source GPS: Wvq1TZh8aF0 | MIDDLE** T3
36:
37: > "What would be my stop loss above the high"
38: **Source GPS: Wvq1TZh8aF0 | MIDDLE** T3
39:
40: > "If it trades above closing, I will take the trade."
41: **Source GPS: Wvq1TZh8aF0 | END** T3
42:
43: ## D6 Target
44: > "The target is this point between A and B which we let's call it C."
45: **Source GPS: Wvq1TZh8aF0 | MIDDLE** T3
46:
47: > "Divergence target arrived. If you have taken the trade for divergence, then it is very important to exit as soon as the divergence target is reached."
48: **Source GPS: Wvq1TZh8aF0 | END** T3
49:
50: > "And at least you should exit 50% to 35% of the quantity."
51: **Source GPS: Wvq1TZh8aF0 | END** T3
52:
53: ## D7 Risk reward
54: > "What is the most important thing? Risk reward ratio."
55: **Source GPS: Wvq1TZh8aF0 | MIDDLE** T3
56:
57: ## D8 Higher-timeframe stacking ("seven star") and double target
58: > "if the monthly is at 60 and there is divergence on the daily, then it becomes a seven star signal"
59: **Source GPS: Wvq1TZh8aF0 | END** T3
60:
61: > "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades"
62: **Source GPS: Wvq1TZh8aF0 | END** T3
63:
64: > "when this ABC setup happens, then double the target. The stop loss will remain the same."
65: **Source GPS: Wvq1TZh8aF0 | END** T3
66:
67: ## D9 Failed attempts, multiple divergences
68: > "Sometimes you take a trade after a divergence and it will make a new low."
69: **Source GPS: Wvq1TZh8aF0 | END** T3
70:
71: > "As long as there is divergence the trade is on."
72: **Source GPS: Wvq1TZh8aF0 | END** T3
73:
74: > "And as long as the RSI is above 60, a second attempt will have to be made."
75: **Source GPS: Wvq1TZh8aF0 | END** T3
76:
77: ## Not stated in this video (do NOT fill from memory)
78: - What exactly "C" is in price terms (the transcript says only "this point between A and B"; it was drawn on a chart). OPEN: needs the video frame.
79: - Wick/intrabar RSI: not mentioned; he says close to close.
80: - Any intraday or crypto timeframe, Bollinger Bands, RSI MA, CVD/OI, speed-based early entry: none.
81: - The "ABC" trade stop distance in numbers: only "above the high" / "Up Rs 12 above the high" (an Indian-stock tick figure, not transferable).
```

### extracts/processed/malkan/extract_cQ-y1oULkBw.md

SHA-256: `856d4b8b39cedbd04fa59b3ea117062911653381a08f7ca2dac12c166ecb8320`

```text
1: # Extract cQ-y1oULkBw - Malkan "Divergence Trading Strategy | RSI Series" (2023-08-26, auto-captions, uploader Malkansview)
2: Phase 1, one transcript, quotes verbatim. T3 = practitioner, own words. Indian equities, daily/weekly/monthly.
3:
4: ## D1 Closing basis
5: > "Always remember that the construction of RSI or it is made on the RSI is at the closing price, so the closing has to match the closing."
6: **Source GPS: cQ-y1oULkBw | BEGIN** T3
7:
8: ## D2 Bar count and strength
9: > "Now, any divergence will take a minimum of three bars, meaning three candles."
10: **Source GPS: cQ-y1oULkBw | MIDDLE** T3
11:
12: > "so this lesson is that shorter duration of number of divergences, the stronger the divergence."
13: **Source GPS: cQ-y1oULkBw | MIDDLE** T3
14:
15: > "As the number of bars increases, you see 15, 20, 25, 30, 40 bars. The divergence gets diluted completely and it has not worked."
16: **Source GPS: cQ-y1oULkBw | MIDDLE** T3
17:
18: ## D3 Confirmation
19: > "It should get confirmation. That will be train line confirmation."
20: **Source GPS: cQ-y1oULkBw | END** T3
21:
22: ## D4 Multiple divergences
23: > "Now when multiple divergences come, the big effect is a big U-turn."
24: **Source GPS: cQ-y1oULkBw | END** T3
25:
26: > "sometimes confirmation does not come after one divergence. There is a second or a third."
27: **Source GPS: cQ-y1oULkBw | END** T3
28:
29: ## D5 Multi-timeframe
30: > "Always remember, if you trade by looking at just a single timeframe chart, you're making the biggest mistake."
31: **Source GPS: cQ-y1oULkBw | END** T3
32:
33: ## D6 Not stated
34: - Classes A, B, C of divergence: named, deferred to another video ("Class 8, Class B, Class C" in captions). OPEN.
35: - Which trendline / how the break is measured: drawn on chart, not in words.
```

### extracts/processed/malkan/extract_-CBvFi40sIQ.md

SHA-256: `6cc663af18c1e41818777ee9bc749fb7572ae95f71b1795f9e65729977168d01`

```text
1: # Extract -CBvFi40sIQ - "5 Star RSI Strategy Screener" (2022-02-09)
2: SECONDARY SOURCE: presenter is Apurva Sheth (Samco), restating Malkan's strategy, not Malkan in his own words. Tier T3 secondary; use only to cross-check. Indian stocks, scanner on Nifty 500.
3:
4: ## D1 Long gate
5: > "To trade on the long side you have to find such trades whose 14 month RSI is above 60"
6: **Source GPS: -CBvFi40sIQ | BEGIN** T3-secondary
7:
8: > "The daily RSI i.e. 14 day RSI must be near 40"
9: **Source GPS: -CBvFi40sIQ | BEGIN** T3-secondary
10:
11: ## D2 Trigger: daily re-cross of 40 after being below
12: > "whenever it is their daily RSI comes below 40 and later when it cross 40 it goes up, you will see an alert in this scanner"
13: **Source GPS: -CBvFi40sIQ | MIDDLE** T3-secondary
14:
15: ## D3 Entry and stop
16: > "your entry point will be above the high of the signal candle and the stoploss you will have to be below the low of the signal candle"
17: **Source GPS: -CBvFi40sIQ | BEGIN** T3-secondary
18:
19: ## D4 Short gate
20: > "In a bearish strategy you have to see 14 month RSI must be below 40 and also 14 week RSI below 40"
21: **Source GPS: -CBvFi40sIQ | BEGIN** T3-secondary
22:
23: > "daily RSI must be at around 60"
24: **Source GPS: -CBvFi40sIQ | MIDDLE** T3-secondary
```

### extracts/processed/malkan/extract_2HcJ3NeZmEQ.md

SHA-256: `15b3528a34bb24ba2fee6748bc18f02c78238294959e6528c1045c380bb9cbf8`

```text
1: # Extract 2HcJ3NeZmEQ - Malkan "RSI 5 Star Set Up #1 (Sell Setup)" (2019-01-20, auto-captions, uploader Malkansview)
2: Phase 1, one transcript. T3 own words. Indian equities. Note: transcript_inventory counted Malkan as 3 raw files; this is a 4th, mis-attributed by the inventory script.
3:
4: ## D1 Long setup as recalled
5: > "five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend"
6: **Source GPS: 2HcJ3NeZmEQ | BEGIN** T3
7:
8: ## D2 Short setup gates
9: > "what would be the short side kind of a trade winds its monthly below 40"
10: **Source GPS: 2HcJ3NeZmEQ | BEGIN** T3
11:
12: > "then we go to weekly setup where the RSI is only below 40"
13: **Source GPS: 2HcJ3NeZmEQ | BEGIN** T3
14:
15: > "we can go to daily and look for 60 rise just to sell"
16: **Source GPS: 2HcJ3NeZmEQ | MIDDLE** T3
17:
18: ## D3 Candles at the trigger
19: > "there's all this candlestick patterns which we see the shooting stars and the doji Zen and hammers and inverted hammers and all"
20: **Source GPS: 2HcJ3NeZmEQ | MIDDLE** T3
21:
22: ## D4 Son does not fight father and grandfather
23: > "son will definitely not try to go against the father or the grandfather"
24: **Source GPS: 2HcJ3NeZmEQ | MIDDLE** T3
```

## E11

### MyTradingSys/backtest/layers/rsi/rsi_divergence.py

SHA-256: `c45ef9e14031d05efdc32ff934996db69554b6023ffac41a4233a2ef8dc80fdc`

```text
1: """
2: Regular RSI/price divergence, Malkan rules (extracts/processed/malkan/, quotes verified):
3: - close to close ("What do we have to compare? Close to close. Because RSI is based on closing price.")
4: - two swing points A then B with B - A + 1 bars between min_bars and max_bars inclusive
5:   (Malkan: minimum three candles; "between three and 10"; 15-50 diluted). min_bars/max_bars are arguments,
6:   the sourced values live in params/malkan_divergence_default.json.
7: - decimals count: any strictly lower price close with a strictly higher RSI is a divergence (min_rsi_diff=0).
8: Bullish: price close lower low, RSI higher low. Bearish: price higher high, RSI lower high (mirror via sign).
9:
10: Swing point = strict local extreme of the CLOSE: close[i] < both neighbours (low) or > both (high). It is only
11: known one bar later, so the event time is ts[i+1] (causal: never uses a bar after the one it is stamped on).
12: A and B are CONSECUTIVE swing points of the same kind (v1 limit: a divergence against an older, non-adjacent
13: swing is not detected). A swing point with RSI None is skipped as if absent.
14: `chain` counts how many consecutive A->B pairs ending at this B were divergences (1 = single, 2 = double...):
15: Malkan's "multiple divergences".
16: Not here: candle confirmation, entry, stop, target (backtest step), intrabar/wick RSI (he says close to close).
17: """
18:
19:
20: def _pivots(vals, rsi, kind):
21:     sign = 1 if kind == "low" else -1
22:     out = []
23:     for i in range(1, len(vals) - 1):
24:         if rsi[i] is None:
25:             continue
26:         a, b, c = sign * vals[i - 1], sign * vals[i], sign * vals[i + 1]
27:         if b < a and b < c:
28:             out.append(i)
29:     return out
30:
31:
32: def rsi_divergence(close: list, rsi: list, ts: list, min_bars: int, max_bars: int,
33:                    kind: str = "bullish", min_rsi_diff: float = 0.0) -> list:
34:     if kind not in ("bullish", "bearish"):
35:         raise ValueError("kind must be 'bullish' or 'bearish'")
36:     if not (len(close) == len(rsi) == len(ts)):
37:         raise ValueError("close, rsi and ts must have the same length")
38:     if min_bars < 3 or max_bars < min_bars:
39:         raise ValueError("need 3 <= min_bars <= max_bars")
40:     if min_rsi_diff < 0:
41:         raise ValueError("min_rsi_diff must be >= 0")
42:     sign = 1 if kind == "bullish" else -1
43:     piv = _pivots(close, rsi, "low" if kind == "bullish" else "high")
44:     events = []
45:     chain = 0
46:     for k in range(1, len(piv)):
47:         a, b = piv[k - 1], piv[k]
48:         bars = b - a + 1
49:         price_ok = sign * close[b] < sign * close[a]
50:         rsi_ok = sign * rsi[b] - sign * rsi[a] > min_rsi_diff
51:         if price_ok and rsi_ok and min_bars <= bars <= max_bars:
52:             chain += 1
53:             events.append({
54:                 "t": ts[b + 1], "i": b + 1, "event": kind + "_divergence",
55:                 "a_i": a, "b_i": b, "a_t": ts[a], "b_t": ts[b], "bars": bars,
56:                 "close_a": close[a], "close_b": close[b],
57:                 "rsi_a": rsi[a], "rsi_b": rsi[b], "chain": chain,
58:             })
59:         else:
60:             chain = 0
61:     return events
```

## E12

### MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py

SHA-256: `acaa7e3285d941d477c5256e1fc805a1ea33c84cb8f92997026179a728e788b3`

```text
1: """
2: MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py  (T089 + T091, items/T088_all_timeframe_module.md)
3:
4: Regular RSI/price divergence measured on EVERY timeframe in layers/timeframe/registry.json over the
5: BTCUSDT 1m history (2022-01 .. latest on disk), resampled with tf_resample. Backtest only, no live gate.
6:
7: Two event columns per timeframe:
8: - "malkan"   rsi_divergence.py with the sourced window (params/malkan_divergence_default.json: 3-10 bars,
9:              consecutive swing points, close to close, decimals count).
10: - "operator" T091, operator idea, NO-SOURCE: long-range divergence 11-60 bars between a swing point A and a
11:              later same-kind swing point B, NON-adjacent (at least one same-kind swing point between them),
12:              every swing point between them smaller than A ("highs 14 bars apart with smaller swings
13:              between", live read R2 2026-10-09). Malkan rejects this range in his own words
14:              (extract_Wvq1TZh8aF0.md:13, extract_cQ-y1oULkBw.md:15). 11 and 60 come from the T091 item text,
15:              not from a trader. Measured only; never wired live without a source.
16:
17: Outcome: FORMULAS.md s7 forward return from the event bar's close (event = bar after B closes, causal),
18: side long for bullish / short for bearish, at horizons HORIZONS (bars of that timeframe). Net = gross minus
19: one round trip of taker fee (fees.py DERIBIT_TAKER, entry and exit both taker: the conservative case).
20: Baseline = the same-side forward return averaged over every bar of that timeframe (drift control).
21:
22: Verdict per (timeframe, column, kind) at PRIMARY_H:
23:   "insufficient n"  fewer than MIN_EVENTS (300, operator rule in the T089 item) events with data at PRIMARY_H
24:   "edge candidate"  net mean > 0, t-stat of net >= T_MIN, gross mean > same-side baseline, and net mean > 0
25:                     in at least half of the calendar years that hold >= 30 events
26:   "no edge"         otherwise
27: PRIMARY_H = 10 bars and T_MIN = 2.0 are engineering choices (NO-SOURCE), fixed before the run, not tuned.
28: Overlapping horizons on dense timeframes make the t-stat optimistic; a candidate is a lead, not a result.
29:
30: Splits: by calendar year (UTC), and by two 12-hour UTC halves (00-12, 12-24) for timeframes shorter than
31: 12h (B154 names two 12-hour sessions but no boundary; 00/12 UTC is a placeholder, NO-SOURCE). B154's regime
32: split does not exist yet in code, so it is not here.
33: """
34:
35: import argparse
36: import json
37: import math
38: import sys
39: from datetime import datetime, timezone
40: from pathlib import Path
41:
42: REPO = Path(__file__).resolve().parents[4]
43: sys.path.insert(0, str(REPO))
44:
45: from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence, _pivots
46:
47: HORIZONS = (1, 5, 10, 20)
48: PRIMARY_H = 10
49: MIN_EVENTS = 300
50: T_MIN = 2.0
51: MIN_YEAR_EVENTS = 30
52: OPERATOR_MIN_BARS = 11
53: OPERATOR_MAX_BARS = 60
54: RSI_PERIOD = 14
55:
56: PARAMS_PATH = Path(__file__).resolve().parent / "params" / "malkan_divergence_default.json"
57: REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"
58:
59:
60: def load_taker():
61:     from MyTradingSys.backtest.fees import DERIBIT_TAKER
62:     return DERIBIT_TAKER
63:
64:
65: # ---------------------------------------------------------------- detector (T091)
66:
67: def long_range_divergence(close, rsi, ts, min_bars, max_bars, kind="bullish"):
68:     """Non-adjacent long-range divergence. For each swing point B take the MOST RECENT earlier same-kind
69:     swing point A with min_bars <= B - A + 1 <= max_bars such that: B is more extreme than A (bullish:
70:     close lower; bearish: close higher), RSI disagrees (bullish: rsi[B] > rsi[A]; bearish: rsi[B] < rsi[A]),
71:     at least one same-kind swing point lies strictly between them, and every such in-between swing point is
72:     less extreme than A. One event per B at most, stamped ts[B+1] (swing known one bar later)."""
73:     if kind not in ("bullish", "bearish"):
74:         raise ValueError("kind must be 'bullish' or 'bearish'")
75:     if not (len(close) == len(rsi) == len(ts)):
76:         raise ValueError("close, rsi and ts must have the same length")
77:     if min_bars < 3 or max_bars < min_bars:
78:         raise ValueError("need 3 <= min_bars <= max_bars")
79:     ext = (lambda x: -x) if kind == "bullish" else (lambda x: x)   # larger = more extreme
80:     rsi_ok = (lambda ra, rb: rb > ra) if kind == "bullish" else (lambda ra, rb: rb < ra)
81:     piv = _pivots(close, rsi, "low" if kind == "bullish" else "high")
82:     events = []
83:     for k in range(1, len(piv)):
84:         b = piv[k]
85:         eb = ext(close[b])
86:         max_between = None
87:         for j in range(k - 1, -1, -1):
88:             a = piv[j]
89:             bars = b - a + 1
90:             if bars > max_bars:
91:                 break
92:             ea = ext(close[a])
93:             n_between = k - j - 1
94:             if (bars >= min_bars and n_between >= 1 and eb > ea and max_between < ea
95:                     and rsi_ok(rsi[a], rsi[b])):
96:                 events.append({
97:                     "t": ts[b + 1], "i": b + 1, "event": kind + "_divergence_long",
98:                     "a_i": a, "b_i": b, "a_t": ts[a], "b_t": ts[b], "bars": bars, "n_between": n_between,
99:                     "close_a": close[a], "close_b": close[b], "rsi_a": rsi[a], "rsi_b": rsi[b],
100:                 })
101:                 break
102:             max_between = ea if max_between is None else max(max_between, ea)
103:     return events
104:
105:
106: # ---------------------------------------------------------------- scoring
107:
108: def forward_returns(i, sgn, closes, horizons=HORIZONS):
109:     """FORMULAS s7: {h: sgn*(c[i+h]-c[i])/c[i]} for horizons with data (missing h = no entry)."""
110:     out = {}
111:     for h in horizons:
112:         if i + h < len(closes):
113:             out[h] = sgn * (closes[i + h] - closes[i]) / closes[i]
114:     return out
115:
116:
117: def baseline(closes, horizons=HORIZONS):
118:     """Mean long forward return over every bar with data at h. Short baseline = minus this."""
119:     out = {}
120:     for h in horizons:
121:         n = len(closes) - h
122:         out[h] = (sum((closes[i + h] - closes[i]) / closes[i] for i in range(n)) / n) if n > 0 else None
123:     return out
124:
125:
126: def _mean_t(xs):
127:     n = len(xs)
128:     if n == 0:
129:         return None, None
130:     m = sum(xs) / n
131:     if n < 2:
132:         return m, None
133:     var = sum((x - m) ** 2 for x in xs) / (n - 1)
134:     return m, (m / math.sqrt(var / n) if var > 0 else None)
135:
136:
137: def _year(t_ms):
138:     return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).year
139:
140:
141: def _half(t_ms):
142:     return "00-12" if datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).hour < 12 else "12-24"
143:
144:
145: def score(events, closes, sgn, base, taker, with_half=False):
146:     """events: [{"i","t"}]. Returns stats per horizon, by year and by 12h half at PRIMARY_H, and verdict."""
147:     rt = 2 * taker
148:     rows = [(e, forward_returns(e["i"], sgn, closes)) for e in events]
149:     per_h = {}
150:     for h in HORIZONS:
151:         g = [f[h] for _, f in rows if h in f]
152:         gm, _ = _mean_t(g)
153:         nm, nt = _mean_t([x - rt for x in g])
154:         b = base.get(h)
155:         per_h[h] = {"n": len(g), "gross_mean": gm, "net_mean": nm, "net_t": nt,
156:                     "hit_net": (sum(1 for x in g if x - rt > 0) / len(g)) if g else None,
157:                     "baseline_side": (sgn * b) if b is not None else None}
158:
159:     def split(keyf):
160:         groups = {}
161:         for e, f in rows:
162:             if PRIMARY_H in f:
163:                 groups.setdefault(keyf(e["t"]), []).append(f[PRIMARY_H] - rt)
164:         return {k: {"n": len(v), "net_mean": sum(v) / len(v)} for k, v in sorted(groups.items())}
165:
166:     by_year = split(_year)
167:     by_half = split(_half) if with_half else None
168:     return {"horizons": per_h, "by_year": by_year, "by_half": by_half,
169:             "verdict": verdict(per_h[PRIMARY_H], by_year)}
170:
171:
172: def verdict(p, by_year):
173:     if p["n"] < MIN_EVENTS:
174:         return "insufficient n"
175:     years = [v for v in by_year.values() if v["n"] >= MIN_YEAR_EVENTS]
176:     years_ok = years and sum(1 for v in years if v["net_mean"] > 0) * 2 >= len(years)
177:     if (p["net_mean"] is not None and p["net_mean"] > 0 and p["net_t"] is not None and p["net_t"] >= T_MIN
178:             and p["baseline_side"] is not None and p["gross_mean"] > p["baseline_side"] and years_ok):
179:         return "edge candidate"
180:     return "no edge"
181:
182:
183: # ---------------------------------------------------------------- per timeframe
184:
185: def run_tf(bars, malkan_params, taker, with_half):
186:     from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
187:     closes = [b["c"] for b in bars]
188:     ts = [b["t"] for b in bars]
189:     if len(closes) <= RSI_PERIOD + 2:
190:         return {"n_bars": len(bars), "columns": {}}
191:     rsi = rsi_core(closes, RSI_PERIOD)
192:     base = baseline(closes)
193:     cols = {}
194:     for kind, sgn in (("bullish", 1.0), ("bearish", -1.0)):
195:         mk = rsi_divergence(closes, rsi, ts, malkan_params["min_bars"], malkan_params["max_bars"], kind,
196:                             malkan_params.get("min_rsi_diff", 0.0))
197:         op = long_range_divergence(closes, rsi, ts, OPERATOR_MIN_BARS, OPERATOR_MAX_BARS, kind)
198:         cols.setdefault("malkan", {})[kind] = score(mk, closes, sgn, base, taker, with_half)
199:         cols.setdefault("operator", {})[kind] = score(op, closes, sgn, base, taker, with_half)
200:         cols["malkan"][kind]["n_events"] = len(mk)
201:         cols["operator"][kind]["n_events"] = len(op)
202:     return {"n_bars": len(bars), "first_t": ts[0], "last_t": ts[-1], "columns": cols}
203:
204:
205: def _pct(x):
206:     return "-" if x is None else "%+.3f%%" % (x * 100)
207:
208:
209: def render_report(summary):
210:     L = ["# T089 RSI divergence on every timeframe (+ T091 operator long-range column)", "",
211:          "Data: BTCUSDT 1m %s .. %s, resampled per registry. RSI %d. Fees: one taker round trip %.2f%% "
212:          "deducted from every event (fees.py). Primary horizon %d bars; verdict needs >= %d events, net > 0, "
213:          "t >= %.1f, gross above same-side drift, net > 0 in half the years. Malkan column = sourced 3-10 bar "
214:          "rule; operator column = T091 11-60 bar non-adjacent idea (NO-SOURCE)." % (
215:              summary["data_from"], summary["data_to"], RSI_PERIOD, 2 * summary["taker"] * 100, PRIMARY_H,
216:              MIN_EVENTS, T_MIN), "",
217:          "| TF | Column | Kind | Events | n@h | Gross | Drift (side) | Net | t | Hit net | Verdict |",
218:          "|---|---|---|---|---|---|---|---|---|---|---|"]
219:     for tf, r in summary["tfs"].items():
220:         for col, kinds in r["columns"].items():
221:             for kind, s in kinds.items():
222:                 p = s["horizons"][PRIMARY_H] if PRIMARY_H in s["horizons"] else s["horizons"][str(PRIMARY_H)]
223:                 L.append("| %s | %s | %s | %d | %d | %s | %s | %s | %s | %s | %s |" % (
224:                     tf, col, kind, s["n_events"], p["n"], _pct(p["gross_mean"]), _pct(p["baseline_side"]),
225:                     _pct(p["net_mean"]), "-" if p["net_t"] is None else "%.2f" % p["net_t"],
226:                     "-" if p["hit_net"] is None else "%.1f%%" % (p["hit_net"] * 100), s["verdict"]))
227:     L += ["", "## Net mean at the primary horizon by year (events with >= %d per cell shown as n/net)" %
228:           MIN_YEAR_EVENTS, ""]
229:     years = sorted({y for r in summary["tfs"].values() for k in r["columns"].values() for s in k.values()
230:                     for y in s["by_year"]})
231:     L.append("| TF | Column | Kind | " + " | ".join(str(y) for y in years) + " |")
232:     L.append("|---|---|---|" + "---|" * len(years))
233:     for tf, r in summary["tfs"].items():
234:         for col, kinds in r["columns"].items():
235:             for kind, s in kinds.items():
236:                 cells = []
237:                 for y in years:
238:                     v = s["by_year"].get(y) or s["by_year"].get(str(y))
239:                     cells.append("-" if not v else "%d/%s" % (v["n"], _pct(v["net_mean"])))
240:                 L.append("| %s | %s | %s | %s |" % (tf, col, kind, " | ".join(cells)))
241:     return "\n".join(L) + "\n"
242:
243:
244: def main():
245:     from MyTradingSys.backtest.bt.bt_data import load_klines
246:     from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
247:     ap = argparse.ArgumentParser()
248:     ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
249:     ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
250:     ap.add_argument("--out", required=True)
251:     ap.add_argument("--tfs", default=None, help="comma list; default every registry timeframe")
252:     args = ap.parse_args()
253:
254:     out_dir = Path(args.out)
255:     out_dir.mkdir(parents=True, exist_ok=True)
256:     registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
257:     mp = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
258:     taker = load_taker()
259:     bars_1m = load_klines(args.data_root)
260:     last_t = bars_1m[-1]["t"] if bars_1m else 0
261:     bars_1m += [b for b in load_klines(args.data_root2) if b["t"] > last_t]
262:     bars_1m.sort(key=lambda b: b["t"])
263:     if not bars_1m:
264:         print("No data found", file=sys.stderr)
265:         return 2
266:     print("Loaded %d 1m bars" % len(bars_1m), file=sys.stderr, flush=True)
267:     fmt = lambda t: datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
268:     tfs = args.tfs.split(",") if args.tfs else list(registry["timeframes"])
269:     res = {}
270:     for tf in tfs:
271:         bars = bars_1m if tf == "1m" else resample(bars_1m, tf, registry)
272:         spec = registry["timeframes"][tf]
273:         with_half = spec.get("unit") == "seconds" and spec["seconds"] < 43200
274:         res[tf] = run_tf(bars, mp, taker, with_half)
275:         print("%s: %d bars done" % (tf, len(bars)), file=sys.stderr, flush=True)
276:     summary = {"task": "T089+T091", "data_from": fmt(bars_1m[0]["t"]), "data_to": fmt(bars_1m[-1]["t"]),
277:                "taker": taker, "rsi_period": RSI_PERIOD, "primary_h": PRIMARY_H, "min_events": MIN_EVENTS,
278:                "malkan_params": {k: mp[k] for k in ("min_bars", "max_bars", "min_rsi_diff")},
279:                "operator_window": [OPERATOR_MIN_BARS, OPERATOR_MAX_BARS], "tfs": res}
280:     with open(out_dir / "summary.json", "w", newline="\n", encoding="utf-8") as f:
281:         json.dump(summary, f, indent=1)
282:     with open(out_dir / "REPORT.md", "w", newline="\n", encoding="utf-8") as f:
283:         f.write(render_report(summary))
284:     print("Done. %s" % out_dir, file=sys.stderr)
285:     return 0
286:
287:
288: if __name__ == "__main__":
289:     sys.exit(main())
```

### MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md

SHA-256: `c87cb3260e0c9ddbf875e8bc75d6d143391204d0acba4270e750de93b359d157`

```text
1: # T089 + T091 result: RSI divergence on every timeframe, 2022-01-01 .. 2026-10-07 (2026-10-09)
2:
3: Verdict: no edge on any timeframe that reached 300 events, for either Malkan's sourced 3-10 bar rule or the
4: operator's 11-60 bar long-range idea. From 2h up only one cell (2h Malkan bearish, 301) reaches 300 events on one
5: symbol in 4.75 years; the rest stay "insufficient n" (not "edge", not "no edge").
6:
7: - 32 cells have >= 300 events (1m-1h except 1h operator bullish at 277, plus 2h Malkan bearish). Gross forward return at 10 bars sits within a few
8:   hundredths of a percent of plain drift; after one taker round trip (0.10%) 31 of 32 are net negative (t -0.4 to
9:   -73). On 1m-30m net is negative in every year 2022-2026 except three 2024 operator cells (15m/30m, +0.001% to
10:   +0.072%).
11: - Best cell with enough n: 1h operator bearish, 332 events, net +0.038%, t 0.39: noise.
12: - 6h operator bullish (54 events, net +1.57%, t 2.99) and 2d operator cells look large, but n is 6-54; they are
13:   leads for a multi-symbol rerun at most, not results.
14: - Operator column (T091) is no better than Malkan's: Malkan's own words ("diluted") are not contradicted.
15:
16: Method: `backtest/layers/rsi/run_divergence_mtf.py` (9 tests). RSI 14, close to close, events stamped the bar
17: after swing B (causal). FORMULAS s7 forward return at 1/5/10/20 bars, net of fees.py taker x2. Verdict at 10
18: bars needs >= 300 events, net > 0, t >= 2, gross above same-side drift, net > 0 in half the years. 10 bars, t 2
19: and the 00/12 UTC halves are engineering choices fixed before the run (NO-SOURCE). No stop/target bracket and no
20: candle confirmation: this measures the raw signal only. B154 regime split not available in code yet.
21:
22: Files: REPORT.md (all cells + by-year table), summary.json (all horizons, by year, by 12h half).
23: Data: 2,507,040 1m bars (1741 full days, no gaps), live-tree Dumps/backtest raw_1m_2022 + raw.
24:
25: ## T088 addendum: 4m, 3h, 7h, 7h_epoch (2026-10-09)
26:
27: Same script, data and rules, `--tfs 4m,3h,7h,7h_epoch` after T088 added them to the registry. Files: REPORT_T088.md,
28: summary_T088.json.
29: - 4m: no edge. 14,490 Malkan + 8,815 operator events, gross equals drift, net -0.10% at 10 bars (t -14 to -20),
30:   negative in every year 2022-2026.
31: - 3h (168-208 Malkan, 94-106 operator) and 7h (46-113): insufficient n, no verdict.
32: - 7h operator bullish, 46 events, net +1.09%, t 2.11, positive in all 5 years (8-11 a year): the same shape as the
33:   6h operator bullish lead. A lead for a multi-symbol rerun only. The epoch-aligned 7h variant gives 41 events,
34:   net +0.47%, t 0.72, so the lead depends on the 00:00 UTC day-reset anchor (NO-SOURCE, T090 open).
```

## E13

### MyTradingSys/backtest/layers/rsi/rsi_reclaim.py

SHA-256: `cb8519ed34607e6cc2b3629d37e24da211528b87c4dd522198e3e20d531e2f20`

```text
1: """
2: Operator RSI "2a" context events (research/rsi_2a_2026-10-09/RSI_2A_SPEC.md), close-based, no tuned numbers.
3:
4: rsi_reclaim_events: RSI sits below a level (below = rsi < level - clearance) and later closes back above it
5: (above = rsi > level + clearance). Bars between the two thresholds are the "band". Each reclaim reports what the
6: operator wants to bucket afterwards instead of a pre-picked cut-off:
7:   dwell_below  bars in the last contiguous below-run (Case A = 1, Case B = 4..24 are analysis buckets, not rules here)
8:   band_bars    band bars between the end of that run and the reclaim bar (0 = direct cross)
9:   depth        level - lowest RSI in the run
10: direction="down" is the mirror for shorts (RSI above level + clearance, then closes back below it): the series is
11: mirrored with 100 - x, so "level" stays the real level (60 for the short side) and depth = highest RSI - level.
12: A band pop between two below-runs starts a NEW run (dwell restarts). None bars (warm-up/gap) carry state unchanged.
13:
14: rsi_retest: Case C. After a reclaim, within `within` bars RSI comes back into the band (touch) and then closes above
15: again = "support"; closes below the lower threshold first = "fail"; otherwise "none". `within` and `clearance` are
16: caller arguments on purpose: no default, so no unsourced number can hide here.
17: """
18:
19:
20: def _mirror(v):
21:     return None if v is None else 100.0 - v
22:
23:
24: def _check(rsi, ts, clearance, direction):
25:     if clearance < 0:
26:         raise ValueError("clearance must be >= 0")
27:     if len(rsi) != len(ts):
28:         raise ValueError("rsi and ts must have the same length")
29:     if direction not in ("up", "down"):
30:         raise ValueError("direction must be 'up' or 'down'")
31:
32:
33: def rsi_reclaim_events(rsi: list, ts: list, level: float, clearance: float, direction: str = "up") -> list:
34:     _check(rsi, ts, clearance, direction)
35:     if direction == "down":
36:         series, lvl = [_mirror(v) for v in rsi], 100.0 - level
37:     else:
38:         series, lvl = rsi, level
39:     lo, hi = lvl - clearance, lvl + clearance
40:     events = []
41:     prev = None            # side of the last non-None bar: "below" | "band" | "above"
42:     armed = False          # a below-run exists and has not been reclaimed yet
43:     run_len = 0
44:     run_start = None
45:     run_min = None
46:     band_bars = 0
47:     for i, v in enumerate(series):
48:         if v is None:
49:             continue
50:         if v < lo:
51:             if prev != "below":
52:                 run_len, run_start, run_min, band_bars = 0, i, v, 0
53:             run_len += 1
54:             run_min = min(run_min, v)
55:             armed = True
56:             prev = "below"
57:         elif v > hi:
58:             if armed:
59:                 events.append({
60:                     "t": ts[i], "i": i, "event": "reclaim", "direction": direction,
61:                     "level_value": level, "clearance": clearance,
62:                     "dwell_below": run_len, "band_bars": band_bars,
63:                     "depth": lvl - run_min, "direct": band_bars == 0,
64:                     "run_start_t": ts[run_start],
65:                 })
66:                 armed = False
67:             prev = "above"
68:         else:
69:             if armed:
70:                 band_bars += 1
71:             prev = "band"
72:     return events
73:
74:
75: def rsi_retest(rsi: list, reclaim_events: list, level: float, clearance: float, within: int,
76:                direction: str = "up") -> list:
77:     if clearance < 0:
78:         raise ValueError("clearance must be >= 0")
79:     if within < 1:
80:         raise ValueError("within must be >= 1")
81:     if direction not in ("up", "down"):
82:         raise ValueError("direction must be 'up' or 'down'")
83:     series = [_mirror(v) for v in rsi] if direction == "down" else rsi
84:     lvl = 100.0 - level if direction == "down" else level
85:     lo, hi = lvl - clearance, lvl + clearance
86:     out = []
87:     n = len(series)
88:     for ev in reclaim_events:
89:         i = ev["i"]
90:         touched_at = None
91:         status, at = "none", None
92:         for j in range(i + 1, min(i + within, n - 1) + 1):
93:             v = series[j]
94:             if v is None:
95:                 continue
96:             if v < lo:
97:                 status, at = "fail", j
98:                 break
99:             if v <= hi:
100:                 if touched_at is None:
101:                     touched_at = j
102:             elif touched_at is not None:
103:                 status, at = "support", j
104:                 break
105:         out.append({"reclaim_t": ev["t"], "reclaim_i": i, "status": status,
106:                     "resolve_i": at, "touch_i": touched_at,
107:                     "bars_after": None if at is None else at - i})
108:     return out
```

### MyTradingSys/research/rsi_2a_2026-10-09/RSI_2A_SPEC.md

SHA-256: `f03a644da1d23ebcc9f1c6877fb5bdfe00a08ecf826dd112d4740c2026198977`

```text
1: # RSI 2a / 2a' - operator ideas vs Malkan sources (2026-10-09)
2:
3: Status: layer candidate only (separate layer, never a Tom filter). Nothing here is an MTS rule until the operator approves it and our own OOS backtest passes.
4: Provenance split: every parameter is tagged OPERATOR (his words, this session) or MALKAN (quote in extracts/processed/malkan/) or NO-SOURCE (do not tune).
5: Operator answer to the open questions: "these questions will be answered by Malkanviews extractions". Extractions done: 3 transcripts, quotes gate PASS.
6:
7: ## Operator input, verbatim (source tag OPERATOR)
8: 2a: RSI cross above 40 (clearance 37-38 to 41-42) or RSI support at 40 after it crosses up and lands on the 40 line.
9:   Case A: RSI crosses below 40, closes exactly 1 candle below, pops back into neutral; price then returns to the same level or higher.
10:   Case B: RSI below 40 for more than 4-24 candles, then enters from under and crosses 40.
11:   HINT 1: divergence while RSI is below 40 (price lower lows, RSI higher lows); multiple divergences seen on 1m.
12:   HINT 2: RSI support on the RSI MA near 2a = better signal.
13: 2a': mirror for shorts from above 60, with Bollinger Bands: price outside the BB plus resistance confluence (bearish divergence, CVD, OI).
14:   Bearish divergence = higher highs in price, lower highs in RSI. Trigger when RSI's low breaks its last low on candle close, unless price falls faster than
15:   the average speed at the tops (then do not wait for the close). Backtest to find which confluence combinations work.
16:
17: ## Answers from the Malkan extractions (T3, Indian equities D/W/M, not crypto, not intraday)
18: | Question | Answer | Quote file |
19: |---|---|---|
20: | Close or wick RSI for divergence? | Close to close | extract_Wvq1TZh8aF0 D1, extract_cQ-y1oULkBw D1 |
21: | Min bars between the two points | 3 | Wvq1 D2, cQ-y D2 |
22: | Max useful bars | up to ~10 ("between three and 10"); 15-50 diluted | Wvq1 D2, cQ-y D2 |
23: | Where is divergence strongest | bullish near 40, bearish near 60; at 20/80 reverse divergences negate it | Wvq1 D3 |
24: | Decimals | count (37.7 vs 38.89 accepted) | Wvq1 D4 |
25: | Confirmation | bullish candle after bullish div (bearish candle after bearish); entry on break of that candle; stop beyond its extreme | Wvq1 D5 |
26: | Target | point "C between A and B" (price level; exact definition NOT in the words, needs the video frame) | Wvq1 D6 |
27: | Exit | take 50% (caption says "50% to 35%") at target, trail the rest | Wvq1 D6 |
28: | Multiple divergences | second/third divergence = retry while monthly RSI > 60; "big U-turn" | Wvq1 D9, cQ-y D4 |
29: | Higher-TF stack | monthly > 60 + daily < 40 + divergence = best, double the target | Wvq1 D8 |
30: | Daily 40 re-cross | 5-star: monthly and weekly > 60, daily comes below 40 then crosses back up; entry above signal candle high, stop below its low (secondary source) | extract_-CBvFi40sIQ |
31: | Timeframe | daily/weekly/monthly only; he says to read one higher and one lower | cQ-y D5 |
32:
33: ## Not covered by Malkan (stay OPERATOR hypotheses; log, do not tune)
34: - Case A (exactly 1 candle below 40) and Case B dwell 4-24 candles. Bucket dwell in the analysis, pick no number.
35: - RSI MA support as confluence (existing `rsi_ma_events.ma_support`).
36: - Bollinger Bands, CVD, OI confluence; the speed-based early trigger; 1m/intraday use.
37: - Malkan's BB/"3x3 volatility" videos are not in the repo yet (WEB_RESEARCH.md gap list).
38:
39: ## Conflicts to flag
40: - Malkan's 2a gate is HTF-first (monthly/weekly > 60). The operator's 2a has no HTF gate. Test both; `malkan_mtf.py` already has the composition.
41: - Malkan exits at target C with a candle-based stop. The earlier RSI backtests used a generic 1%/2% bracket (RSI_HISTORY.md in the mts-rsi worktree), so their "no edge" verdict does not test Malkan's own exit.
42: - Operator 1m use vs Malkan daily-and-up: the 10-bar max rule may scale with timeframe or may not; test per timeframe.
43:
44: ## Build order (steps 1-3 DONE 2026-10-09; 27 tests; both mutation-checked)
45: 1. `rsi_events` annotation: dwell bars below the level before the cross, depth of dip. Parameter-free; bucket later.
46: 2. cross-then-support sequencer (Case C).
47: 3. `rsi_divergence.py`: close-to-close swing points, 3..10 bars apart (MALKAN), decimals allowed, bullish only if RSI at the low is near 40 as a logged flag (not a filter). Tests derived from FORMULAS.md style hand-computed series.
48: 4. Confluence flags logged per event (MA support, divergence count, HTF RSI state, BB position, CVD, OI).
49: 5. Malkan-exit backtest (candle-break entry, stop beyond candle, target C) vs generic bracket, both reported.
50: 6. Speed-based early trigger last (needs intrabar RSI; out of scope in rsi_events today).
51:
52: ## Built (backtest/layers/rsi/)
53: - `rsi_reclaim.py`: `rsi_reclaim_events` (dwell_below, band_bars, depth, direct; up for the 40 side, down for the 60 side) and `rsi_retest` (Case C: support / fail / none within N bars). Clearance and window are arguments with no default.
54: - `rsi_divergence.py`: close-to-close bullish/bearish divergence between consecutive swing closes, 3..10 bars inclusive (params/malkan_divergence_default.json, quotes cited), `chain` = multiple-divergence count. Event is stamped one bar after the second swing (causal).
55: - v1 limits: only consecutive swings are compared; no candle confirmation or target C yet (step 5).
56:
57: ## Corpus findings
58: - A 4th Malkan transcript existed, `2HcJ3NeZmEQ` (5-star sell setup: monthly < 40, weekly < 40, daily rises to 60). The inventory counted 3. Extracted (gate PASS) and the raw file added to git (it was untracked).
59: - WEB_RESEARCH.md lists ~8 more Malkan videos with no transcript in the repo (W1HrDl70Lhk, A-CQiV_UFB4, fgN6QBFY3Ss Bollinger father-son, kVIvcn7T44o, N7r3v7plqZM, FHEoMmD6xKM, dXxQOnK2jhQ, TYB7GJODt-k volatility divergence, WBByyLBp8-c). The Bollinger and volatility-divergence ones are the ones the 2a' short side needs. Downloading them needs operator approval.
```

## E14

### MyTradingSys/research/t090_7h_2026-10-09/RESULT.md

SHA-256: `35a226c5c50c15bf4a48a5eae12a74fa09ee134f866bfbbeb8c1a103852dfb46`

```text
1: # T090 7h research + T088 lead robustness (2026-10-09)
2:
3: ## Sources (standard web search + page fetch 2026-10-09; no YouTube video found that discusses 7h)
4: - TradingView "MCS HTF Po3 (printed from 1800)" https://www.tradingview.com/script/PizcXAAP-MCS-HTF-Po3-printed-from-1800/ : closed-source; text: "Designed to view AM trades 7H candles as they print on the lower time frame." / "Customisable HTF candles that reset and print at your chosen time". 18:00 is only in the title; no time zone, market or test.
5: - TradingView "7Hour Levels" https://www.tradingview.com/script/KXQfNGf1-7Hour-Levels/ : "Asia 18:00 -> London 01:00 -> NYAM 08:00 -> NYPM 15:00 (New York time)", "The trading day begins at 18:00 New York time". 7 h = spacing of session opens (ICT day), not a candle study.
6: - Playbook tier: T3 at best (indicator descriptions). No backtest, no crypto-specific 7h evidence found. 7h is an ICT session-spacing idea for FX/futures, not a crypto convention.
7:
8: ## Anchor decision
9: - Only sourced anchor: 18:00 New York = 22:00 UTC (EDT) / 23:00 UTC (EST). 00:00 UTC day-reset (T088 default) and epoch have no source: flags updated in registry.json, both stay NO-SOURCE; the 18:00-NY variant is `7h` shifted +22h/+23h (probe script, not yet a registry key because it needs DST handling).
10: - Pick for any later 7h test: 18:00 NY (22/23 UTC), not 00:00 UTC.
11:
12: ## Robustness of the T088 lead (operator bullish long-range RSI divergence, net of taker x2, horizon 10 bars, BTCUSDT 2022-01..2026-10)
13: Only BTCUSDT is on disk (no ETH). Anchor shift = 1m bars shifted by h hours then the registry resample rule.
14:
15: | cell | n | net mean h10 | t | hit |
16: |---|---|---|---|---|
17: | 7h@00 | 46 | +1.09% | 2.11 | 70% |
18: | 7h@18 | 47 | +0.15% | 0.25 | 55% |
19: | 7h@22 | 45 | +0.65% | 1.18 | 58% |
20: | 7h@23 | 43 | +0.46% | 1.23 | 58% |
21: | 7h@03 | 55 | +1.89% | 3.45 | 73% |
22: | 7h@05 | 48 | +0.57% | 0.87 | 56% |
23: | 7h@12 | 47 | +0.43% | 0.64 | 53% |
24: | 6h@00 | 54 | +1.57% | 2.99 | 69% |
25: | 6h@01 | 46 | +0.43% | 0.79 | 61% |
26: | 6h@02 | 47 | +1.03% | 1.87 | 57% |
27: | 6h@03 | 45 | +0.55% | 1.15 | 51% |
28: | 6h@04 | 39 | +0.38% | 0.69 | 56% |
29: | 6h@05 | 48 | +0.29% | 0.44 | 56% |
30: | 8h@00 | 35 | +1.02% | 1.42 | 60% |
31: | 8h@01 | 37 | +0.69% | 0.94 | 51% |
32: | 8h@02 | 38 | +1.23% | 1.74 | 61% |
33: | 8h@04 | 38 | +0.61% | 0.98 | 53% |
34: | 8h@06 | 37 | -0.17% | -0.23 | 46% |
35:
36: Verdict: NOT robust. Of 18 anchor cells, 3 reach t>2 (7h@03 t3.45, 6h@00 t2.99, 7h@00 t2.11); 17 of 18 are positive (mean ~+0.7%), so the bullish operator signal on 6-8h carries a common positive drift, and the "best" cell moves with the anchor. Picking the best of 18 explains the 7h@00 result. At the sourced anchor (22/23 UTC) the 7h lead is t 1.2: no edge. It is the same 6h/8h-type effect shifted, not a 7h-specific one. All cells n 35-55 (< 300): no verdict either way. Not wired, not queued; closing the 7h lead.
37: Script: backtest/layers/rsi/run_t090_anchor_probe.py; data anchor_probe.json.
```

## E15

### MyTradingSys/items/T061_wavetrend_lazybear.md

SHA-256: `f72d3772e541fae6fcdde3dbbe95d252856e2a04e016d80623a5fa38c67b4bf7`

```text
1: # T061 WaveTrend with Crosses [LazyBear]
2:
3: Opened 2026-10-01. Status OPEN. Severity MED.
4:
5: ## Operator ask (verbatim)
6:
7: I need wave trend indicator integration into MTS as a separate layer.
8:
9: Source: https://in.tradingview.com/v/jFQn4jYZ/  (LazyBear, Pine v2, public domain code with author attribution)
10:
11: ## Parameters (from source)
12:
13: - Channel Length n1 = 10
14: - Average Length n2 = 21
15: - Overbought Level 1 = 60
16: - Overbought Level 2 = 53
17: - Oversold Level 1 = -60
18: - Oversold Level 2 = -53
19:
20: ## Math
21:
22: ap    = hlc3 = (high + low + close) / 3
23: esa   = EMA(ap, n1)
24: d     = EMA(abs(ap - esa), n1)
25: ci    = (ap - esa) / (0.015 * d)
26: tci   = EMA(ci, n2)
27: wt1   = tci
28: wt2   = SMA(wt1, 4)
29: plot  wt1, wt2, wt1-wt2 area, cross(wt1, wt2) markers, barcolor on cross
30:
31: ## Classification
32:
33: - Layer type: indicator / read-only module.
34: - Doctrine: PROJECT_VISION.md lock 2026-09-23. Modules never gate core. Switchable on/off. Display alongside or compute as separate read.
35: - Source tag: [SCREENER] until the admission gate. Not Tom, not CT, not a Tom filter.
36: - Admission: per playbook Part I, T3 practitioner content. No engine rule on this item alone.
37:
38: ## Planned shape (design only, not built)
39:
40: - One offline module under MyTradingSys/backtest/layers/wavetrend/ with a driver that reads the archived klines.
41: - Compute wt1, wt2 on each timeframe already present in the snapshot (5m, 15m, 1h, 4h, 1d).
42: - Emit cross events (wt1 x wt2) with the four threshold levels as tags.
43: - Backtest with the same method as FABIO_L1: IS/OOS 70/30, fees 0.10% RT, PBO.
44: - If verdict passes, a live alert layer may be added. Never a filter on core verdict.
45:
46: ## Next step
47:
48: Write the FORMULAS.md entry for this layer, then spec the driver. No code yet.
```

## E16

### MyTradingSys/research/T065_LAZYBEAR_SURVEY.md

SHA-256: `3d97b2addb017eeacae617a83035a18083fd032ce44dd211a7e1d0f1a8ee7ac4`

```text
1: # T065 - LazyBear survey and shortlist
2:
3: Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, static). Item: items/T065_lazybear_survey.md.
4:
5: ## 0. Evidence status (updated 2026-10-05, Desktop, session MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish)
6:
7: - TradingView reachable from Desktop (built-in browser). The four shortlisted Pine sources were **opened and read** (Source code tab). Every parameter below tagged **[PINE]** is from that source;
8:   the earlier [SEARCH]/[MEMORY] tags are replaced. Corrections to the Cloud draft are in section 2 under "Correction".
9: - Not verified: the Squeeze Momentum author's *updated* source (pastebin.com/UCpcX8d7, see S1) was not opened; boost/like counts are as displayed on the page, label meaning (views vs boosts) not confirmed.
10: - Evidence tier for all items: T3 practitioner indicator (no MTS backtest). Ranking is a port-cost/fit judgement, not a result. Nothing here is a tuned number.
11:
12: ## 1. Scripts found (search-confirmed to exist and be open source)
13:
14: | Script | URL | Likes seen | Maps to MTS gap |
15: |---|---|---|---|
16: | Squeeze Momentum Indicator | https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/ | page shows 116.8K / 680 [PINE page] | volatility compression: GAP (no BB/Keltner code in repo; grep of py/md/java finds none) |
17: | WaveTrend Oscillator / WT with Crosses | https://in.tradingview.com/v/jFQn4jYZ/ (from T061) | not shown | momentum/divergence: already T061 |
18: | Volume Flow Indicator (VFI, Katsanos) | https://tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear | not shown | volume/flow: PARTIAL duplicate of CVD (MTS has aggTrade CVD live; VFI is OBV-style on candle volume) |
19: | Better Volume Indicator (BVI) | https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/ | not shown | effort-vs-result volume bars (climax / churn / low): GAP vs absorption flag |
20: | Impulse MACD | https://in.tradingview.com/script/qt6xLfLi-Impulse-MACD-LazyBear | not shown | trend state: overlaps the 6-state MOMENTUM map in MTS_PLAYBOOK.md:32 and RSI layers. Not shortlisted |
21: | Others named in the ask (Klinger, Relative Volatility, Chandelier) | - | - | Search returned no LazyBear page for them; not assessed |
22:
23: ## 2. Shortlist (4; each a separate switchable layer, tag [SCREENER], never a Tom filter, read-only contract per PROJECT_VISION)
24:
25: ### S1. Squeeze Momentum (priority 1)
26: - **Computes:** volatility-compression flag when Bollinger Bands sit inside Keltner Channels (sqzOn = lowerBB > lowerKC and upperBB < upperKC; sqzOff the opposite), plus a linear-regression momentum
27:   histogram: `linreg(close - avg(avg(highest(high,20), lowest(low,20)), sma(close,20)), 20, 0)`. Derived from Carter's TTM Squeeze. Source: close.
28: - **Verified parameters [PINE]:** BB length 20, BB mult 2.0, KC length 20, KC mult 1.5, useTrueRange true (KC range = TR, SMA 20), momentum linreg length 20 (= KC length), offset 0.
29: - **Correction (vs Cloud draft):** the draft's momentum linreg length "20 [MEMORY]" is confirmed. **Bug in the displayed source:** `dev = multKC * stdev(...)` uses the KC multiplier (1.5) for the BB deviation; the author's note (2014-09-29) says the BB multiplier
30:   was stuck at 1.5 and points to an updated pastebin (not opened). Build with BB dev = 2.0 * stdev(close,20) (the `mult` input), not the as-displayed code.
31: - **One-line reason:** MTS has no volatility-compression read; BTC "needs to break out" is the operator's ask 1 and a squeeze state is
32:   the only LazyBear item that says *when a range is loaded*.
33: - **Port cost:** ~4 h (SMA, stdev, ATR/TR, linreg on klines already in data/klines/).
34: - **Draft file:** `MyTradingSys/backtest/layers/volatility/squeeze_momentum.py` (+ `test_squeeze_momentum.py`)
35: - **Source:** https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/
36:
37: ### S2. Better Volume Indicator (priority 2)
38: - **Computes:** per bar, splits volume into an up/down share by range (`range = true range`; `v1` = buy-share formula chosen by close>=open, `v2 = v - v1`), builds 22 derived series (v1..v22: volume x range, volume / range, differences,
39:   and 2-bar sums over `highest(high,2)-lowest(low,2)`), and flags a bar when a series equals its `length`-bar extreme (c1..c20). Classes: climax-up (red), climax-down (white), churn (green), climax-churn (purple #8B008B), low volume (yellow), default cyan. Plots volume columns coloured by class plus `sma(volume, length)`.
40: - **Verified parameters [PINE]:** length (Lookback) = 8; use2Bars = true; lowVol / climaxUp / climaxDown / churn / climaxChurn = true; enableBarColors = false. 2-bar window = `highest(high,2)`/`lowest(low,2)`. No other numeric constants except `(2+(range*range)/10)` inside the v1 formula.
41: - **Correction (vs Cloud draft):** the draft's "lookback and thresholds [MEMORY, unverified]" is wrong on two points: lookback is 8 and there are **no thresholds**; classification is "series equals its 8-bar extreme". The v1 expression is long and has an operator-precedence quirk in the down-bar branch
42:   (`... / (2+(range*range)/10) * range + (close - open)`); port it literally, then test, or the layer will not match TradingView.
43: - **One-line reason:** "high-volume churn" is effort-without-result at bar level, the klines-only cousin of the absorption flag, so
44:   it can be backtested on 5m/15m/1h history where aggTrade CVD does not exist.
45: - **Port cost:** ~4 h (revised up from 3: 22 series and 20 conditions).
46: - **Draft file:** `MyTradingSys/backtest/layers/volume/better_volume.py`
47: - **Source:** https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/
48:
49: ### S3. WaveTrend with Crosses (already open as T061; priority 3)
50: - **Computes:** `ap = hlc3; esa = ema(ap, n1); d = ema(abs(ap - esa), n1); ci = (ap - esa) / (0.015 * d); wt1 = ema(ci, n2); wt2 = sma(wt1, 4)`; cross markers where wt1 crosses wt2, bar colour on cross.
51: - **Verified parameters [PINE]:** n1 (Channel Length) 10, n2 (Average Length) 21, obLevel1 60, obLevel2 53, osLevel1 -60, osLevel2 -53, signal SMA length 4 (hard-coded), 0.015 constant. Matches the T061 numbers; no correction.
52: - **Provenance flag:** the page at in.tradingview.com/v/jFQn4jYZ/ is listed as an indicator **by lonestar108** (a republish dated 2016-02-21); the code header says `@author LazyBear`. LazyBear's own WaveTrend Oscillator [WT] page was not opened here; the math and defaults are the standard LazyBear WT.
53: - **One-line reason:** only oscillator on the list that carries divergence, which the operator named as a gap; do not open a second item.
54: - **Port cost:** ~3 h (math already written in T061).
55: - **Draft file:** `MyTradingSys/backtest/layers/momentum/wavetrend.py`
56: - **Source:** https://in.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/
57:
58: ### S4. Volume Flow Indicator (priority 4)
59: - **Computes:** Katsanos VFI: `typical = hlc3; inter = log(typical) - log(typical[1]); vinter = stdev(inter, 30); cutoff = coef * vinter * close; vave = sma(volume, length)[1]; vmax = vave * vcoef; vc = min(volume, vmax);
60:   mf = typical - typical[1]; vcp = vc if mf > cutoff, -vc if mf < -cutoff, else 0; vfi = sum(vcp, length) / vave` (optional 3-bar SMA); signal `vfima = ema(vfi, signalLength)`; optional histogram vfi - vfima.
61: - **Verified parameters [PINE]:** length 130, coef 0.2, vcoef (max volume cutoff) 2.5, signalLength 5, smoothVFI false (3-bar SMA when true), stdev window 30 (hard-coded), showHisto false.
62: - **Correction (vs Cloud draft):** the draft's "coefficient 0.2 for daily and 0.1 for intraday [SEARCH]" describes Katsanos' guidance; the script default is 0.2 for all timeframes. length 130 and vcoef 2.5 replace the [MEMORY] values; signal 5 is new. Page shows 27K / 106.
63: - **One-line reason:** only worth it as a klines-history stand-in for CVD; on live data aggTrade CVD is the better source, so it is the weakest fit.
64: - **Port cost:** ~3 h.
65: - **Draft file:** `MyTradingSys/backtest/layers/volume/volume_flow.py`
66: - **Source:** https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/
67:
68: ## 3. ROI note and next step
69:
70: Build order S1, S2, S3; S4 only if a klines-only backtest of CVD-like flow is wanted. Total ~10-13 h for S1-S3. The four source pages were opened on Desktop 2026-10-05 and the [MEMORY]/[SEARCH] tags replaced (section 0); still open: the Squeeze updated pastebin and the BB-mult fix. No layer touches execution/ or layers/alerts/. Each layer needs a fail-first test (CLAUDE.md gate) and outputs a
71: flag only; promotion past SCREENER needs a backtest per PROJECT_VISION point 4.
```

### MyTradingSys/items/T065_lazybear_survey.md

SHA-256: `dbc44eed3cb1f12dee7d4876cf5e9e38b3c8150785176f308211e685a2ce49ef`

```text
1: # T065 - LazyBear indicators that complement MTS: survey + shortlist
2:
3: Opened 2026-10-05 by MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Status OPEN. Verbatim ask: research/OPERATOR_ASKS_2026-10-05.md section 0, ask 3. Related: T061 (WaveTrend, already open).
4: Source page: https://in.tradingview.com/u/LazyBear/
5:
6: ## Task (Cloud, web research, playbook Part I tiers; LazyBear = T3 practitioner)
7: 1. List the most-used LazyBear scripts (boosts/likes as shown) with open-source Pine links.
8: 2. Map each to an MTS gap (volume/flow, absorption, squeeze/volatility, divergence, trend state) or "duplicate of X".
9: 3. Shortlist 5 or fewer: math, parameters from the source, port cost (hours), evidence tier, ROI note.
10: 4. Each survivor = a separate switchable layer, [SCREENER] tag, never a Tom filter.
11: Output: research/T065_LAZYBEAR_SURVEY.md.
```

## E17

### MyTradingSys/backtest/layers/cryptocred/cc_setups.py

SHA-256: `74f7c393375d98efe8bc75363e540db42a874c93aa2a3892914c4c41781d3989`

```text
1: """
2: MyTradingSys/backtest/layers/cryptocred/cc_setups.py - CryptoCred entry-pattern setups (cluster C10).
3: Module implements three setup functions as pure functions producing bt_engine-ready trade signals:
4: - setup1_sr_flip: [C10-E01 "continuation at break level (SR flip)"]
5: - setup2_fib_pullback: [C10-E04 "continuation at pullback level (0.618-0.786)"]
6: - setup3_failed_msb_reversal: [C10-E05 "reversal on failed MSB", C10-E02 "counter-trend = defensive parameters"]
7:
8: Signal output contract:
9: Each signal is a dict with top-level keys required by bt_engine.simulate_trade:
10: "side" ("long"/"short"), "entry_price" (float), "entry_t" (int, the bar t of the entry trigger bar),
11: "stop" (float), "targets" (list with exactly one tuple: [(target_price, 1.0)]) — plus a nested "meta" dict
12: holding everything else ("setup", "rule_id", "msb_i", "target_r").
13:
14: Module source: MyTradingSys/research/cross_trader_consolidated.md, cluster C10 (Setup Types).
15: Design constraint: [C10-E03 "cut and reverse trap"] - this module never auto-chains a setup-1/2 stop-out into a setup-3 entry;
16: each function only looks at MSB structure independently.
17: """
18: from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings, classify_msb
19: from MyTradingSys.backtest.layers.cryptocred.cc_retest import find_retest, classify_retest_timing
20:
21:
22: def _r_target(entry_price, stop, side, target_r):
23:     """Compute target price from entry/stop/target_r for a given side.
24:
25:     risk is always the positive entry-to-stop distance; the target sits
26:     target_r risk-multiples away from entry in the trade's profit direction
27:     (above entry for long, below entry for short).
28:     """
29:     risk = (entry_price - stop) if side == "long" else (stop - entry_price)
30:     sgn = 1.0 if side == "long" else -1.0
31:     return entry_price + sgn * target_r * risk
32:
33:
34: def _limit_window_end_t(bars, msb_event, retest_kwargs=None):
35:     """Open time of the last bar a resting limit at the broken level stays valid: the existing
36:     find_retest expiry (default 200 bars) or the first bar whose close invalidates the level
37:     (default 0.5% beyond it), whichever comes first. Mirrors cc_retest.find_retest defaults;
38:     only used to expose meta['valid_until_t'] (no signal key is changed)."""
39:     kw = retest_kwargs or {}
40:     expiry = kw.get("expiry_bars", 200)
41:     inval = kw.get("invalidate_pct", 0.005)
42:     c = msb_event["confirm_i"]
43:     lvl = msb_event["broken_level"]
44:     end_k = min(c + expiry, len(bars) - 1)
45:     for k in range(c, end_k + 1):
46:         cl = bars[k]["c"]
47:         if (msb_event["direction"] == "bull" and cl < lvl * (1 - inval)) or \
48:            (msb_event["direction"] != "bull" and cl > lvl * (1 + inval)):
49:             return bars[k]["t"]
50:     return bars[end_k]["t"]
51:
52:
53: def setup1_sr_flip(bars: list, stop_buffer_pct: float = 0.001, target_r: float = 1.5, msb_kwargs: dict | None = None, retest_kwargs: dict | None = None) -> list:
54:     swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
55:     msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
56:     signals = []
57:     for msb_event in msb_events:
58:         retest = find_retest(bars, msb_event, **(retest_kwargs or {}))
59:         if retest is None:
60:             continue
61:         side = "long" if msb_event["direction"] == "bull" else "short"
62:         entry_price = msb_event["broken_level"]
63:         entry_t = retest["t"]
64:         stop = entry_price * (1 - stop_buffer_pct) if side == "long" else entry_price * (1 + stop_buffer_pct)
65:         target_price = _r_target(entry_price, stop, side, target_r)
66:         signal = {
67:             "side": side,
68:             "entry_price": entry_price,
69:             "entry_t": entry_t,
70:             "stop": stop,
71:             "targets": [(target_price, 1.0)],
72:             "meta": {
73:                 "setup": "sr_flip",
74:                 "rule_id": "C10-E01",
75:                 "msb_i": msb_event["i"],
76:                 "target_r": target_r
77:             }
78:         }
79:         if msb_event["confirm_i"] < len(bars):
80:             # limit-order placement info (open times of HTF bars): the setup is known at the
81:             # close of the MSB confirm bar; a resting limit at entry_price is valid through
82:             # the close of the bar opened at valid_until_t.
83:             signal["meta"]["placed_t"] = bars[msb_event["confirm_i"]]["t"]
84:             signal["meta"]["valid_until_t"] = _limit_window_end_t(bars, msb_event, retest_kwargs)
85:         signals.append(signal)
86:     return sorted(signals, key=lambda s: s["entry_t"])
87:
88:
89: def setup2_fib_pullback(bars: list, fib_lo: float = 0.618, fib_hi: float = 0.786, stop_buffer_pct: float = 0.001, target_r: float = 1.5, msb_kwargs: dict | None = None) -> list:
90:     expiry_bars = 200
91:     swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
92:     msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
93:     signals = []
94:     for msb_event in msb_events:
95:         # Find the preceding swing of the opposite kind. broken_swing_i is a BAR index
96:         # (cc_structure.classify_msb sets it from H_last["i"]/L_last["i"]), not a
97:         # position in the `swings` list -- non-swing bars between swings mean the two
98:         # can diverge, so first locate the swing whose "i" matches, then walk backward
99:         # from its list position.
100:         broken_swing_i = msb_event["broken_swing_i"]
101:         broken_pos = next((idx for idx, s in enumerate(swings) if s["i"] == broken_swing_i), None)
102:         if broken_pos is None:
103:             continue
104:         if msb_event["direction"] == "bull":
105:             # Find the most recent swing low before the high that was broken
106:             prev_low = None
107:             for i in range(broken_pos - 1, -1, -1):
108:                 if swings[i]["kind"] == "low":
109:                     prev_low = swings[i]
110:                     break
111:             if prev_low is None:
112:                 continue
113:             # The impulse leg is from the low to the high that was broken
114:             H_price = msb_event["broken_level"]
115:             P_low = prev_low["price"]
116:             fib_zone = [H_price - fib_hi * (H_price - P_low), H_price - fib_lo * (H_price - P_low)]
117:             # Scan bars after confirm_i for the first bar that reaches the resting limit at the zone's upper
118:             # edge. A bar that blows through the whole zone (low below the zone) filled it too (B151).
119:             start_idx = msb_event["confirm_i"] + 1
120:             end_idx = min(start_idx + expiry_bars, len(bars))
121:             found_bar = None
122:             for k in range(start_idx, end_idx):
123:                 if bars[k]["l"] <= fib_zone[1]:
124:                     found_bar = k
125:                     break
126:             if found_bar is None:
127:                 continue
128:             entry_price = fib_zone[1]
129:             entry_t = bars[found_bar]["t"]
130:             stop = fib_zone[0] * (1 - stop_buffer_pct)
131:             side = "long"
132:         else:  # bear msb_event
133:             # Find the most recent swing high before the low that was broken
134:             prev_high = None
135:             for i in range(broken_pos - 1, -1, -1):
136:                 if swings[i]["kind"] == "high":
137:                     prev_high = swings[i]
138:                     break
139:             if prev_high is None:
140:                 continue
141:             # The impulse leg is from the high to the low that was broken
142:             L_price = msb_event["broken_level"]
143:             P_high = prev_high["price"]
144:             # ascending like the bull zone: nearest edge (fib_lo) first, so zone[0] is the short's resting limit
145:             fib_zone = [L_price + fib_lo * (P_high - L_price), L_price + fib_hi * (P_high - L_price)]
146:             # Scan bars after confirm_i for the first bar that reaches the resting limit at the zone's lower
147:             # edge. A bar that blows through the whole zone (high above the zone) filled it too (B151).
148:             start_idx = msb_event["confirm_i"] + 1
149:             end_idx = min(start_idx + expiry_bars, len(bars))
150:             found_bar = None
151:             for k in range(start_idx, end_idx):
152:                 if bars[k]["h"] >= fib_zone[0]:
153:                     found_bar = k
154:                     break
155:             if found_bar is None:
156:                 continue
157:             entry_price = fib_zone[0]
158:             entry_t = bars[found_bar]["t"]
159:             stop = fib_zone[1] * (1 + stop_buffer_pct)
160:             side = "short"
161:         target_price = _r_target(entry_price, stop, side, target_r)
162:         signal = {
163:             "side": side,
164:             "entry_price": entry_price,
165:             "entry_t": entry_t,
166:             "stop": stop,
167:             "targets": [(target_price, 1.0)],
168:             "meta": {
169:                 "setup": "fib_pullback",
170:                 "rule_id": "C10-E04",
171:                 "msb_i": msb_event["i"],
172:                 "target_r": target_r,
173:                 "placed_t": bars[msb_event["confirm_i"]]["t"],
174:                 "valid_until_t": bars[end_idx - 1]["t"]
175:             }
176:         }
177:         signals.append(signal)
178:     return sorted(signals, key=lambda s: s["entry_t"])
179:
180:
181: def setup3_failed_msb_reversal(bars: list, failure_lookback: int = 20, stop_buffer_pct: float = 0.001, target_r: float = 2.0, msb_kwargs: dict | None = None) -> list:
182:     swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
183:     msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
184:     signals = []
185:     for msb_event in msb_events:
186:         c = msb_event["confirm_i"]
187:         if len(bars) - 1 < c + failure_lookback:
188:             continue
189:         # Determine the post-break high/low
190:         swing_i = msb_event["broken_swing_i"]
191:         if msb_event["direction"] == "bull":
192:             broken_level = msb_event["broken_level"]
193:             # The "no new high" check must use the actual extreme reached while the
194:             # break was forming (from the swing to the confirm bar, inclusive), not
195:             # just the broken level itself -- price may have already wicked above it.
196:             structure_high = max(b["h"] for b in bars[swing_i:c+1])
197:             # Look at the next failure_lookback bars after c
198:             window_bars = bars[c+1 : c+1+failure_lookback]
199:             if len(window_bars) < failure_lookback:
200:                 window_bars = bars[c+1:]
201:             # Check if any new high exceeds the structure extreme
202:             max_new_high = max(b["h"] for b in window_bars)
203:             if max_new_high > structure_high:
204:                 continue  # The move continued, not failed
205:             # Check if the close at the end of the window is below the broken level
206:             last_close = window_bars[-1]["c"]
207:             if last_close >= broken_level:
208:                 continue  # Not reversed yet
209:             # Emit reversal signal
210:             side = "short"
211:             entry_price = last_close
212:             entry_t = window_bars[-1]["t"]
213:             stop = broken_level * (1 + stop_buffer_pct)
214:         else:  # bear msb_event
215:             broken_level = msb_event["broken_level"]
216:             # The "no new low" check must use the actual extreme reached while the
217:             # break was forming (from the swing to the confirm bar, inclusive), not
218:             # just the broken level itself -- price may have already wicked below it.
219:             structure_low = min(b["l"] for b in bars[swing_i:c+1])
220:             # Look at the next failure_lookback bars after c
221:             window_bars = bars[c+1 : c+1+failure_lookback]
222:             if len(window_bars) < failure_lookback:
223:                 window_bars = bars[c+1:]
224:             # Check if any new low is below the structure extreme
225:             min_new_low = min(b["l"] for b in window_bars)
226:             if min_new_low < structure_low:
227:                 continue  # The move continued, not failed
228:             # Check if the close at the end of the window is above the broken level
229:             last_close = window_bars[-1]["c"]
230:             if last_close <= broken_level:
231:                 continue  # Not reversed yet
232:             # Emit reversal signal
233:             side = "long"
234:             entry_price = last_close
235:             entry_t = window_bars[-1]["t"]
236:             stop = broken_level * (1 - stop_buffer_pct)
237:         target_price = _r_target(entry_price, stop, side, target_r)
238:         signal = {
239:             "side": side,
240:             "entry_price": entry_price,
241:             "entry_t": entry_t,
242:             "stop": stop,
243:             "targets": [(target_price, 1.0)],
244:             "meta": {
245:                 "setup": "failed_msb_reversal",
246:                 "rule_id": "C10-E05",
247:                 "msb_i": msb_event["i"],
248:                 "target_r": target_r
249:             }
250:         }
251:         signals.append(signal)
252:     return sorted(signals, key=lambda s: s["entry_t"])
```

### MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py

SHA-256: `8a5e87a8b0c387b077e238183a3fc11d779359d4e1891b2cade2eb7f7d84942b`

```text
1: """
2: MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py - D7 row 075 adapter (T051 L3).
3: Cryptocred adapter: cc_setups trades -> bt_engine + layers/runner.py.
4: Stdlib only. This module is a thin, mechanical wiring layer with no trading logic of its own:
5: - all the logic lives in cc_setups.py, bt_engine.py and layers/runner.py
6: - this file only translates between their different shapes:
7:   * cc_setups' {side,entry_price,entry_t,stop,targets,meta} signal dict
8:   * bt_engine's simulate_trade(**kwargs) call
9:   * runner's {"i": index, "side"} event dict
10:
11: The module works for any of the three cc_setups functions (setup1_sr_flip, setup2_fib_pullback,
12: setup3_failed_msb_reversal) since they all share the same signal contract.
13: """
14: from MyTradingSys.backtest.bt.bt_engine import simulate_trade
15:
16:
17: def signals_to_trades(signals: list, bars: list, mark_bars: list = None, funding: list = None, taker_fee: float = 0.0005, maker_fee: float = 0.0, max_bars: int = 1440, stop_first: bool = True, target_through: float = 0.0) -> list:
18:     """
19:     Convert cc_setups signals into bt_engine trade simulations.
20:
21:     Args:
22:         signals: List of signal dicts from cc_setups (with meta)
23:         bars: List of bar dicts {t,o,h,l,c} for time lookup
24:         mark_bars: Optional list of mark bars for stop/target timing
25:         funding: Optional list of funding events {t, rate}
26:         taker_fee: Taker fee rate
27:         maker_fee: Maker fee rate
28:         max_bars: Maximum bars to simulate
29:         stop_first: Whether stop takes whole size if hit same bar as entry
30:
31:     Returns:
32:         List of {"signal_meta": signal.get("meta", {}), "trade_result": result} dicts
33:     """
34:     if not signals:
35:         return []
36:
37:     results = []
38:     for signal in signals:
39:         # Build call kwargs by dropping meta (bt_engine doesn't want it)
40:         call_kwargs = {k: v for k, v in signal.items() if k != "meta"}
41:         result = simulate_trade(
42:             bars=bars,
43:             mark_bars=mark_bars,
44:             funding=funding,
45:             taker_fee=taker_fee,
46:             maker_fee=maker_fee,
47:             max_bars=max_bars,
48:             stop_first=stop_first,
49:             target_through=target_through,
50:             **call_kwargs
51:         )
52:         results.append({"signal_meta": signal.get("meta", {}), "trade_result": result})
53:
54:     return results
55:
56:
57: def signals_to_events(signals: list, bars: list) -> list:
58:     """
59:     Convert cc_setups signals into runner.py events (index-based).
60:
61:     Args:
62:         signals: List of signal dicts from cc_setups (with meta)
63:         bars: List of bar dicts {t,o,h,l,c} for time lookup
64:
65:     Returns:
66:         List of {"i": index, "side": side} dicts matching runner's expected format
67:         Signals with no matching bar in bars are silently skipped.
68:     """
69:     if not signals:
70:         return []
71:
72:     # Build timestamp -> index lookup once for efficiency
73:     ts_to_idx = {bar["t"]: i for i, bar in enumerate(bars)}
74:
75:     events = []
76:     for signal in signals:
77:         entry_t = signal["entry_t"]
78:         idx = ts_to_idx.get(entry_t)
79:         if idx is not None:
80:             events.append({"i": idx, "side": signal["side"]})
81:
82:     return events
```

## E18

### extracts/processed/cryptocred/extract_BHwoN7VPrBE.md

SHA-256: `192462fe916f2bec74558fc7a4192859d84769d362fdedf2e43f8e67a31bce65`

```text
1: # EXTRACT: CryptoCred — Technical Analysis Series — Market Structure
2: # Video ID: BHwoN7VPrBE
3: # Analyst: CryptoCred
4: # Duration: 95:53
5: # Extracted: 2026-08-29
6: # Reprocessed: 2026-08-30
7: # Method: Manual read + verbatim quote extraction per MTS Part J
8: # Status: PURE EXTRACTION — no tagging, no engine assessment
9: # ---
10:
11: ## RULE 1: SWING HIGH/LOW QUALITY FILTERS
12: > "a swing low is a low with a higher low on both sides and a swing high is a high with a lower high on both sides... there's no single formula... recency is important, significance and size of the move following that high or low is important... the basic smell test... what's the most obvious or outstanding high or low you probably can't go wrong with that"
13: > — BHwoN7VPrBE, ~08:00
14:
15: > "if you have a bigger more significant swing away from the level it's probably going to be better and more significant and meaningful generally for your trading"
16: > — BHwoN7VPrBE, ~08:30
17:
18: **Context:** Swing point selection criteria: recency, significance, size of subsequent move. "Smell test" = most obvious/obvious highs and lows.
19:
20: ---
21:
22: ## RULE 2: MSB DEFINITION — HIGHER HIGH / LOWER LOW
23: > "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low"
24: > — BHwoN7VPrBE, ~22:00
25:
26: **Context:** Formal definition of market structure break: sequence violation in the opposite direction.
27:
28: ---
29:
30: ## RULE 3: MSB AS CONTEXT TOOL, NOT MECHANICAL SYSTEM
31: > "market structure generally i think is a tool to provide context more so than just a mechanical trading system"
32: > — BHwoN7VPrBE, ~05:30
33:
34: **Context:** Market structure provides context for trade decisions, not a standalone mechanical entry system.
35:
36: ---
37:
38: ## RULE 4: DO NOT CHASE EVERY MSB
39: > "if you end up ascribing significance to every single shift in market structure you are turning yourself into nothing more than a breakout and breakdown chaser... it's got very little to do with how we want to use market structure as a tool to provide context"
40: > — BHwoN7VPrBE, ~19:30
41:
42: **Context:** Selective significance: not every minor pivot break is actionable. Chasing every MSB = breakout-chasing behavior.
43:
44: ---
45:
46: ## RULE 5: CONFLUENCE FOR SWING SELECTION
47: > "is the swing high or low you're assessing confluent with another key level... is there a candle open there like the monthly open weekly open daily open etc is there just a good reason to have eyes there"
48: > — BHwoN7VPrBE, ~10:00
49:
50: > "if in doubt sr it out works quite well so by definition horizontal support resistance is derived from old highs and lows"
51: > — BHwoN7VPrBE, ~12:00
52:
53: **Context:** Swing points at confluent levels (SR, opens, old highs/lows) are more significant than isolated swings.
54:
55: ---
56:
57: ## RULE 6: SETUP 1 — CONTINUATION AT BREAK LEVEL (SR FLIP)
58: > "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low... broken support turning to resistance on re-test broken resistance turning to support on a re-test"
59: > — BHwoN7VPrBE, ~45:00
60:
61: **Context:** SR flip setup: enter on pullback to broken level after MSB. Broken support becomes resistance, broken resistance becomes support.
62:
63: ---
64:
65: ## RULE 7: MSB IN RANGE = NOISE
66: > "market structure breaks which are just less obvious or shorter term... in the middle of nowhere... can just be pure noise... i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade"
67: > — BHwoN7VPrBE, ~85:00
68:
69: **Context:** MSBs within a range (not at range extremes) are noise. Only MSBs at actionable range boundaries matter.
70:
71: ---
72:
73: ## RULE 8: TIME FRAME OF MSB = EXPECTED MOVE SIZE
74: > "the time frame of the market structure break to have a significant bearing on the size of the move that follows... don't expect the world to end over an intraday market structure break but at the same time don't expect a weekly market structure break to fizzle out after a couple days"
75: > — BHwoN7VPrBE, ~82:00
76:
77: **Context:** Higher timeframe MSBs produce larger moves. Intraday MSBs = smaller moves. Weekly MSBs = larger, more sustained moves.
78:
79: ---
80:
81: ## RULE 9: COUNTER-TREND = DEFENSIVE PARAMETERS
82: > "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... shorter holding periods... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5... different sizing is also another consideration... smaller or more conservative"
83: > — BHwoN7VPrBE, ~33:00
84:
85: **Context:** Counter-trend trades require: shorter holds, higher R:R minimums (2:1 vs 1.5:1), smaller position size.
86:
87: ---
88:
89: ## RULE 10: CUT AND REVERSE TRAP
90: > "don't take the cut and reverse for granted... sometimes you just end up in a shitty position the market just doesn't want to mesh with you or there's something else going on so don't assume that you've always identified absolute turning points and that the market's going to be kind enough to let you get in on the other side"
91: > — BHwoN7VPrBE, ~42:00
92:
93: **Context:** Automatic cut-and-reverse on invalidation is dangerous. Each setup must be evaluated independently.
94:
95: ---
96:
97: ## RULE 11: PROBABILITY ENHANCERS
98: > "always look for probability enhancers... if the market's kind enough to be in a place where you have some sort of confluence be it the underlying trend high time frames technical confluence funding oi whatever it is you use or proven it's worth make sure to use it"
99: > — BHwoN7VPrBE, ~38:00
100:
101: **Context:** Stack confluence factors (trend, HTF, technical levels, funding, OI) to improve setup probability.
102:
103: ---
104:
105: ## RULE 12: CANDLE BODIES FOR STRUCTURE, CLOSES FOR BREAKS
106: > "my preferred variant is using candle bodies for market structure and then closes so again bodies above or below for market structure break... i at least like to see a close above or below on the same time frame as the market structure anchor so if i'm looking at daily market structure... i want to see a daily close through that high or low to constitute a market structure break"
107: > — BHwoN7VPrBE, ~28:30
108:
109: **Context:** MSB definition using candle bodies (not wicks) for structure, and closes (not just penetrations) for valid breaks. Wick-through without close = retest, not break.
110:
111: ---
112:
113: ## RULE 13: SETUP 2 — CONTINUATION AT PULLBACK LEVEL (0.618-0.786)
114: > "the continuation trade is taken below the breakout point but above the most recent low... i'll map out the low and then the higher high and then as the market starts pulling back it's between these levels that i'll look for structure... personally i look for support resistance structures anywhere between the 618 and 786 retracement"
115: > — BHwoN7VPrBE, ~50:00
116:
117: > "there's no fixed answer really"
118: > — BHwoN7VPrBE, ~55:00
119:
120: **Context:** Fibonacci pullback zone (0.618-0.786) as continuation entry area after breakout. Explicitly noted as personal preference with "no fixed answer."
121:
122: ---
123:
124: ## RULE 14: SETUP 3 — REVERSAL ON FAILED MSB
125: > "the reversal setup... focuses on trading in the opposite direction of a market structure break... a high that forced the lower low is significant... price closing above it means that strong resistance has failed and strong resistance failing is bullish"
126: > — BHwoN7VPrBE, ~65:00
127:
128: > "failed continuation is suggestive of reversal... if we get a higher high bullish into a lower low invalidated then you have bulls offside... bulls offside makes for a good sell setup"
129: > — BHwoN7VPrBE, ~66:00
130:
131: **Context:** Failed continuation after MSB = reversal signal. Sequence: MSB occurs -> fails to continue (no follow-through swing) -> reversal setup at prior breakout level.
132:
133: ---
134:
135: ## RULE 15: EARLY WARNING — FAILURE TO CONTINUE
136: > "failure to continue making lower lows... it's not bullish per se but it's less bearish... the twisting of the dial more gradually is still useful... a sign of bullishness slowly emerging is when you've got clear lower highs and lower lows except those lower lows then start to form equal or higher lows... it's not bullish per se but it's less bearish right and that information itself... the twisting of the dial more gradually is still useful"
137: > — BHwoN7VPrBE, ~88:00
138:
139: **Context:** Gradual shift in swing behavior (lower lows -> equal/higher lows) as early warning of trend slowdown. Not a trade signal — context information only.
140:
141: ---
142:
143: # END
```

### MyTradingSys/research/no_source_sweep_2026-10-09/RESULT.md

SHA-256: `cc25f5966c5c3236f407c52a937b35a53ad15ab1cd0aa341c3dcfc8de3d4c6cb`

```text
1: # NO-SOURCE SWEEP - B142, B143, B144, B145
2:
3: Task: 20261009-181323-no-source-sweep-b142-b143-b144-b145
4: Run: MTS-2026-10-10 (DSA), worktree mts-dsa
5: Method: grep over extracts/processed (45 .md) and raw_transcripts_canonical (109 .txt) = 154 files
6: No code changed.
7:
8: ## B142 - ExtraSetupBuilder stop = previous 1m bar high/low
9: NOT FOUND in 154 files. No extract or raw transcript states a stop at the previous 1-minute bar high or low.
10: Nearest language: Tom CONSOLIDATED_RULES.md discusses exhaustion and volume spikes after a move, not a previous-bar stop.
11: Verdict: NO-SOURCE confirmed.
12:
13: ## B143 - CryptoCred 0.1 percent stop buffer and 1.5R target
14: PARTIAL. Source: extracts/processed/cryptocred/extract_BHwoN7VPrBE.md, RULE 9 (~33:00):
15:   "...greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5..."
16: This sources 1.5R as the trend-aligned baseline and 2.0R for counter-trend. The 0.1 percent stop buffer is NOT FOUND in any file.
17: Verdict: 1.5R SOURCED (CC Rule 9). 0.1 percent buffer NO-SOURCE.
18:
19: ## B144 - SCB exhaustion volume 2.0x over 240 one-minute bars
20: NOT FOUND in 154 files. No extract gives 2.0x volume over 240 bars.
21: Nearest language: extracts/processed/tom/new_selected_10/extract_HySZZSjMxF8.md line 24 and 69 describe exhaustion after increased volume; extracts/processed/tom/CONSOLIDATED_RULES.md describes exhaustion after volume spikes, without the 2.0x / 240-bar numbers.
22: Verdict: NO-SOURCE confirmed.
23:
24: ## B145 - classify_msb filter_range_noise
25: SOURCED. Source: extracts/processed/cryptocred/extract_BHwoN7VPrBE.md, RULE 7 (~85:00):
26:   "market structure breaks which are just less obvious or shorter term... in the middle of nowhere... can just be pure noise... i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade"
27: Corroborating: RULE 3 (context, not mechanical) and RULE 4 (do not chase every MSB).
28: Verdict: SOURCED (CC Rule 7, Rule 4, Rule 3).
29:
30: ## Summary
31: | Row | Parameter | Verdict |
32: |---|---|---|
33: | B142 | previous 1m bar stop | NOT FOUND in 154 files |
34: | B143 | 0.1 percent buffer / 1.5R target | 1.5R sourced (CC Rule 9); 0.1 percent NOT FOUND |
35: | B144 | 2.0x / 240-bar exhaustion | NOT FOUND in 154 files |
36: | B145 | filter_range_noise | SOURCED (CC Rule 7) |
```

## E19

### MyTradingSys/research/AUDIT_CLOSEOUT_2026-10-07.md

SHA-256: `b9dd755a3b5cb35e2739c8365c1df763abd5f539b37786e21d3ccdd62e6fa995`

```text
1: # AUDIT CLOSEOUT 2026-10-07
2:
3: Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Verdicts are from disk on 2026-10-07 after the live tree was fast-forwarded to 5053e2d.
4:
5: ## Part 0: Build-Check scope
6: - BUILD_REPORT.md never lost the Java lines. The tracked file read 2026-10-03 20:34Z (Java compile, 237 math), written before commit 7563de7 (2026-10-04) added "Java tests:" to scripts/Build-Check.ps1. A fresh full run 2026-10-07 10:05Z: Java compile PASS, Java tests 147/147, Math 345/345, Doc 5/5, STATUS PASS.
7: - The 237 to 345 delta is stale file vs current collection (pytest MyTradingSys/tests --ignore=docs collects 348 with this session's tests). No file removed, no path dropped. The copies in mts-research, mts-registry and BinanceDataFeed.registry still hold the 2026-10-03 report.
8:
9: ## Part 1: inventory
10: All 13 source paths exist. Rows were reached through AUDIT_RECONCILE_2026-10-04.md (which carries the other nine documents' findings) and the three item docs; the nine other audit documents were not re-read line by line this session.
11:
12: | source | reached | verdict summary |
13: |---|---|---|
14: | AUDIT_RERUNS_2026-10-06.md | full | 4 reruns resolved this session, see Part 2 |
15: | AUDIT_RECONCILE_2026-10-04.md | PARTIAL rows (B127/B128 31 rows) | 21 closed on disk (12 + 9), 10 residual named in the item receipts |
16: | B120 / B127 / B128 | full | receipts written |
17: | EXEC_PROVENANCE_AUDIT, LAYER_PROVENANCE_AUDIT, PROVENANCE_AUDIT_TOM | cited rows only (C14, C15, C19, C23, P06, A03) | CONFIRMED NO-SOURCE, feed B142-B144 |
18: | FORMULA_AUDIT, WIRING_MAINTENANCE_AUDIT, W3_KAPPA_REPORT, REVALIDATION_ACTIONS, TWO_CORES_READINESS | via reconcile rows only | UNVERIFIED beyond those rows |
19:
20: ## Part 2: why stuck (not CLOSED)
21: | item | blocker | last session left | smallest next action |
22: |---|---|---|---|
23: | T055 C1 funding_cvd_fade FAIL | was: run used 12 months of funding. Now FAIL on full funding (OOS -0.0453%) | 10-06 reruns not valid | none; closes under the T055 rule. File: T055_BT_RERUN_FULLFUNDING_2026-10-07.md |
24: | T055 C2 session_momentum FAIL | same | same | none; FAIL (Sharpe 0.0084, 1 positive OOS year) |
25: | CryptoCred fill bias | was code + rerun | fix committed, rerun pending | done: all FAIL. UNVERIFIED removed |
26: | Tom core BT | was disk path + merge | PC run unfinished | done: TOM_CORE_BT_RERUN_2026-10-06.md; open: why live rule 19 signals -> 0 |
27: | 5 NO-SOURCE items | operator decision (keep flagged) | review never scheduled | separate remove-or-replace session; rows B117, B118, B142, B143, B144 (B116 closed 10-06) |
28: | B120 | operator (W3-5) + doc work | filing only | W3-5 ruling; Sonnet doc pass for the rest |
29: | B127 | Java test + doc reclass (RA-W4-A11) | filing only | write SetupCandidatesBuilder test: grossRR < 1.5 candidate kept |
30: | B128 | Java tests, DSR spec, scheduler, operator decisions | filing only | see receipt table |
31: | CLOUD_INBOX note 1 | none | OPEN | DONE on disk; Cloud removes at next boot |
32: | CLOUD_INBOX note 2 | doc task 1 | OPEN | operator: supersede or reconstruct TWO_CORES_FIX_PASS_2026-10-02.md |
33:
34: ## Operator decisions
35: - B120 W3-5 | W3_BLIND_PACKET_2026-10-01.md:14 | Does DATA-PLUMBING mean "no trading meaning" or "no Tom idea"? (parked)
36: - CLOUD_INBOX note 2 task 1 | system/CLOUD_INBOX.md | Mark TWO_CORES_FIX_PASS_2026-10-02.md SUPERSEDED by the merged PRs, or reconstruct it from git history?
37: - B127 RA-W4-A11 | PROVENANCE_AUDIT_TOM.md row A11 | Reclassify the gross 1.5 R:R advisory flag to CONCEPT-ONLY?
38: - B128 TC-W1-6 | live_layers.py:122 | Enable classify_msb(filter_range_noise=True) in the live _cc_layer? (default stays False)
39: - B128 M29-11 | execution/auto_trader.py:75-78 | Should rsi:cross map side by level, not by direction?
40: - B128 M29-14/15 | auto_trader.py:311,320 | Rename the t_close key, or accept the documented meaning?
41: - F:\MTS\data\tom_snapshots_smoke | F: | Archive the 2026-09-01 smoke output?
42: - Research branch | mts-research 7aa01cd | Push the research commits (4c74cd7, 2aa75cc, b3dbe74, merge 5334975, 7aa01cd) to origin?
43:
44: ## Fixes made (all with tests)
45: - run_t055.load_data clips bars to funding coverage (failed before the fix, 26 pass).
46: - tom_bt_report.adapter_line prefers the promoted adapter files (crash fix; test added).
47: - Coverage tests: test_b127_fetch_archive_funding (6), test_b127_declutter_backups (3), test_b127_fabio_v3_isolation (2), test_b128_cc_range_noise_filter (3). Fail-first intent not satisfiable on already-correct code; kept as coverage tests, mutation coverage incomplete.
48:
49: ## Operator rulings 2026-10-08 and what was done
50: 1. CLOUD_INBOX note 2 CLOSED and removed: TWO_CORES_FIX_PASS_2026-10-02.md is SUPERSEDED by the merged PRs jishusharma/BinanceDataFeed #2 (book_imbalance no-data fix), #4 (Fabio v3 core), #5 (mts launcher runner/orphans verbs), #6 (consensus writer + TF maps), #7 (engine tests), #8 (formula audit), #10 (fast-track consolidation); no doc written.
51: 2. B127 RA-W4-A11 reclassified TOM-CONCEPT-ONLY (PROVENANCE_AUDIT_TOM.md:33, summary 34/35). B127 CLOSED.
52: 3. B128 TC-W1-6: filter_range_noise stays off; B145 filed with file and exact test.
53: 4. B128 M29-11: rsi:cross now side-by-level, fail-first test, backup auto_trader.py.pre_rsicross. The running auto_trader (PID 5364) keeps the old mapping until the supervisor restarts it. Source for the table: MLK-R1; 40-down -> short, 60-up -> long, every other cross has no side. Live alerts today are all level 40, so only 40-down trades and 40-up is now rejected.
54: 5. B128 M29-15: t_close meaning accepted; comment added.
55: 6. Smoke dir moved (receipt in B128).
56: 7. B120 W3-5 stays parked.
57:
58: ## Next session first action
59: Month-by-month diff of the live-rule drop (17 filled trades / 19 SETUP_FORMING signals -> 0).
60: Row directories compared: OLD F:\MTS\data\tom_bt (previous run) vs NEW F:\MTS\data\tom_bt_2026-10-07 (this rerun, current Java).
61: Command (from the repo root, read-only, script added this session):
62:
63:     python scripts/dev/diff_tom_rows.py F:/MTS/data/tom_bt F:/MTS/data/tom_bt_2026-10-07
64:
65: First result (run once 2026-10-08): SETUP_FORMING rows total old 19, new 0, differing in 15 months (2022-02 ... 2026-05, one or two rows each).
66: Rows per month fall about 25 percent (e.g. 2022-02: 1856 -> 1264), WAIT_RR falls sharply (1147 -> 355) and WAIT_PROOF roughly doubles (264 -> 446). So the current Java emits fewer candidates, fewer fail on R:R, and more fail on proof: consistent with PR #12 (stop floor removed, book_imbalance null, net R:R gate from net_rr_floor.json) but not yet attributed.
67: Next step: for 2022-02, join old and new rows on t and print proof, stop, gross_rr, net_rr for the one old SETUP_FORMING row; the field that moved is the cause.
```

### MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md

SHA-256: `cfe66285fe425f5cd6508b4651e3f88e5b836f902d3c0b86cf4fa855c3aa9e72`

```text
1: # LAYER_PROVENANCE_AUDIT - non-core layer parameters (BUILD_PIPELINE 8.1, LY1)
2:
3: Session: MTS-2026-10-04-1230Z-APP-BLD-ly1-layer-provenance. Mode: static (code and source files read, nothing run).
4: Scope: rsi, cryptocred, positioning, session, turn_of_candle, tick, consensus under MyTradingSys/backtest/layers/.
5: Verdicts use the definitions in research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md:5, with "Tom" read as "the
6: layer's own source":
7: - SOURCED = a quote from the layer's source supports the value and the role.
8: - CONCEPT-ONLY = the source names the idea; the code measures it by proxy or the number is ours.
9: - NO-SOURCE = no source idea behind it, or it plays a role (gate, stop, target, time exit) the source never gives it.
10: - DATA-PLUMBING = no trading meaning (fees, file paths, study gates). Listed, not counted.
11:
12: Source per layer (the "trader" whose words count):
13: | Layer | Source | Where the words are |
14: |---|---|---|
15: | rsi (malkan) | Vishal B Malkan (MalkanView), blog/chartink text | research/malkan_rsi_2026-09-28/WEB_RESEARCH.md (WR) |
16: | rsi (generic) | none named; params say "source": "operator" | backtest/layers/rsi/params/default.json:3 |
17: | cryptocred | CryptoCred, videos BHwoN7VPrBE, inqHN8q57X4 | extracts/processed/cryptocred/extract_BHwoN7VPrBE.md (BH), extract_inqHN8q57X4.md (INQ) |
18: | positioning | Memon 2026 (T2), He/Manela/Ross/von Wachter (T2); CVD leg = internal T055a H2 | research/whale_positioning_evidence_2026-09-12.md:30; backtest/layers/FORMULAS.md:356-370 |
19: | session | Shen, Urquhart, Wang 2022 (T1) | research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:30; FORMULAS.md:372-383 |
20: | turn_of_candle | Shanaev, Vasenin, Stepanov, Heliyon (T1) | T055b_PROVEN_SETUPS.md:38,51; FORMULAS.md:385-398 |
21: | tick | operator spec (T040), verbatim operator text | MyTradingSys/items/T040_tick_delta_layer.md (T040) |
22: | consensus | operator architecture doc | research/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43 |
23:
24: Quote rule used: a SOURCED row cites a line that carries the source's own words (in quotes in that file). A summary
25: bullet written by our researcher is not a quote; rows resting only on one are CONCEPT-ONLY.
26:
27: ## Totals
28:
29: | Layer | SOURCED | CONCEPT-ONLY | NO-SOURCE | Rows | Plumbing (not counted) |
30: |---|---|---|---|---|---|
31: | rsi | 4 | 10 | 12 | 26 | 6 |
32: | cryptocred | 6 | 11 | 8 | 25 | 2 |
33: | positioning | 0 | 4 | 3 | 7 | 3 |
34: | session | 1 | 2 | 3 | 6 | 1 |
35: | turn_of_candle | 2 | 1 | 2 | 5 | 0 |
36: | tick | 4 | 6 | 2 | 12 | 3 |
37: | consensus | 0 | 0 | 0 | 0 | 4 |
38: | **All** | **17** | **34** | **30** | **81** | **19** |
39:
40: Headline: no non-core layer has a sourced exit. Every stop, target and time exit in these layers (RSI 1%/2%/100 bars,
41: CryptoCred 0.1% buffers, fixed 1.5R/2R targets, 200/1440-bar expiries) is NO-SOURCE, and two of them reuse a number the
42: trader gives in a different role (CryptoCred's 1.5:1 and 2:1 are MINIMUM R:R filters, BH:82, used as fixed targets).
43:
44: ## 1. rsi
45:
46: rsi: 4 SOURCED, 10 CONCEPT-ONLY, 12 NO-SOURCE.
47:
48: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
49: |---|---|---|---|---|---|---|
50: | R01 | rsi/rsi_core.py:7; params/default.json:7; params/malkan_40_60_default.json:7 | RSI period | 14 | WR:35 "Period: 14 (RSI 14)" is a researcher bullet, no Malkan quote | CONCEPT-ONLY | Also the live alert RSI (observation.py.new:24). |
51: | R02 | rsi/rsi_ma.py:8; params/default.json:9-12 | RSI smoothing line | SMA 14 | - (no Malkan text mentions an RSI MA) | NO-SOURCE | default.json:3 "source": "operator"; operator is not a trader source. |
52: | R03 | params/default.json:14 | Generic RSI levels | 70 / 50 / 30 | - WR:39-40: Malkan uses 40-60 "Instead of traditional overbought (70) / oversold (30)"; WR:93: 50 "not explicitly defined" | NO-SOURCE | Live rsi_events alerts feed the testnet trader. |
53: | R04 | params/default.json:15 | Generic event tolerance | 0 | - | NO-SOURCE | Invalid: rsi_events.py:20-21 raises on tolerance <= 0 (open question Q3). |
54: | R05 | params/default.json:16 | ma_support_enabled | false | - | NO-SOURCE | Switch for R07, itself unsourced. |
55: | R06 | rsi/rsi_events.py:19-103 | Band events support / rejection / failure / cross | rule | WR:60-61 "when it bounces from 40, trend is strong upward" (bullet) | CONCEPT-ONLY | Taxonomy is ours; Malkan names only bounce at 40 / fall from 60. |
56: | R07 | rsi/rsi_ma_events.py:15; run_rsi_backtest.py:269-270 | RSI-vs-MA events: period 9/14, ma_length 9/14, tolerance 0.5/1/2, mode touch/cross | grid | - | NO-SOURCE | Grid-searched: tuning, forbidden by the provenance rule. |
57: | R08 | rsi/malkan_40_60.py:24,64; malkan_40_60_default.json:10 | Bull support level lo | 40 | WR:45 "When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40." | SOURCED | |
58: | R09 | rsi/malkan_40_60.py:24,107; malkan_40_60_default.json:11 | Bear resistance level hi | 60 | WR:45 (same quote) | SOURCED | |
59: | R10 | rsi/malkan_40_60.py:53-58 | Regime: BULL if min >= 40 AND max >= 60; BEAR if max <= 60 AND min <= 40; else RANGE | rule | WR:45, WR:85 support "won't cross 40/60"; the second clause (max >= 60, min <= 40) has no quote | CONCEPT-ONLY | |
60: | R11 | rsi/malkan_40_60.py:24; malkan_40_60_default.json:12 | Regime lookback | 20 bars | - (no window in WR) | CONCEPT-ONLY | |
61: | R12 | rsi/malkan_40_60.py:64,107; malkan_40_60_default.json:13 | Band tolerance around 40/60 | 2.0 RSI pts | WR:116 "at or near Daily RSI 40" (bullet); quote WR:120 "Bullish candlestick forms at 40 RSI level" | CONCEPT-ONLY | |
62: | R13 | rsi/malkan_40_60.py:88,122 | Bull trigger = "support" event (enters band from above, closes back above 40+tol); bear = "rejection" at 60 | rule | WR:77 "Daily RSI supporting near 40"; WR:113 "Daily RSI <= 40" | CONCEPT-ONLY | A dip below 38 is a "failure" in code and is dropped; WR:113 accepts RSI below 40. |
63: | R14 | rsi/malkan_40_60.py:64,94; malkan_40_60_default.json:14 | Green entry candle required (long) | true | WR:77 "...Daily RSI supporting near 40 with entry on Green Candle." | SOURCED | |
64: | R15 | rsi/malkan_40_60.py:107,128; malkan_40_60_default.json:15 | Red entry candle required (short) | true | WR:144 "Bearish candlestick forms at 60 RSI level on daily chart = short signal." | SOURCED | |
65: | R16 | rsi/malkan_40_60.py:91,125 | Gate signal on the SAME timeframe's regime | rule | WR:85 regime quote; WR:77 gates on Monthly + Weekly, not the entry TF | CONCEPT-ONLY | Self-documented MLK-GAP1 (malkan_40_60.py:13-16). |
66: | R17 | rsi/malkan_mtf.py:69 | MTF bull gate: weekly AND monthly regime == BULL | rule | WR:77 "Monthly RSI >= 60 AND Weekly RSI >= 60" | CONCEPT-ONLY | Malkan reads the HTF RSI value; code uses the 20-bar regime (R10). |
67: | R18 | rsi/malkan_mtf.py:95 | MTF bear gate: weekly AND monthly regime == BEAR | rule | WR:80-81, WR:138-139 bullets "Monthly RSI < 40 / <= 40"; no quote | CONCEPT-ONLY | |
68: | R19 | run_rsi_backtest.py:233,268 | HTF regime lookback | grid 3 / 6 / 12 | - | NO-SOURCE | Tuned. |
69: | R20 | run_rsi_backtest.py:265-266 | malkan_40_60 grid: period 10/14/21, tolerance 1/2/3, lookback 10/20/40 | grid | - | NO-SOURCE | Sweeping a sourced value (period) is tuning. |
70: | R21 | run_rsi_backtest.py:56,109 | Stop | 1% from entry | - WR:123 "Place below the low of the bullish entry candle" (bullet) | NO-SOURCE | |
71: | R22 | run_rsi_backtest.py:57,109 | Target | 2% from entry | - WR:128 "Target is 60 RSI level on daily chart" | NO-SOURCE | Malkan's target is an RSI level, not a price %. |
72: | R23 | run_rsi_backtest.py:58,110 | Time exit | 100 bars | - WR:132-133: hold while Monthly and Weekly RSI stay > 60 | NO-SOURCE | |
73: | R24 | run_rsi_backtest.py:107 | Entry at the signal bar close | rule | WR:117 "Entry point is determined by placing an order above the high of the signal candle" | CONCEPT-ONLY | Entry named; trigger differs (close vs break of high). |
74: | R25 | rsi/tolerance_sweep.py:45 | Tolerance sweep 0.5..5.0, horizons 1/3/5/10/20 | grid | - | NO-SOURCE | Tuning machinery. |
75: | R26 | rsi/tolerance_sweep.py:22-42 | event -> side map (support long, rejection short, cross by direction) | rule | - (docstring :27 "this driver's own heuristic") | NO-SOURCE | |
76:
77: Plumbing (rsi): run_rsi_backtest.py:55 HORIZONS (1,5,20); :59 MIN_OOS_N 30; :60 MAX_PBO 0.5; :76 is_frac 0.70;
78: tolerance_sweep.py:83 min_events 5; observation.py.new:50,59-60 TFS, _CHUNK, DEFAULT_MAX_SCAN_BYTES.
79:
80: ## 2. cryptocred
81:
82: cryptocred: 6 SOURCED, 11 CONCEPT-ONLY, 8 NO-SOURCE.
83:
84: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
85: |---|---|---|---|---|---|---|
86: | C01 | cryptocred/cc_structure.py:11 | Swing fractal left | 2 bars | BH:12 "a swing low is a low with a higher low on both sides... there's no single formula" | CONCEPT-ONLY | |
87: | C02 | cryptocred/cc_structure.py:11 | Swing fractal right | 2 bars | BH:12 (same) | CONCEPT-ONLY | Also the confirmation delay (cc_structure.py:49,57). |
88: | C03 | cryptocred/cc_structure.py:11,17-21 | Bodies, not wicks, for swings | use_body=True | BH:106 "my preferred variant is using candle bodies for market structure and then closes" | SOURCED | |
89: | C04 | cryptocred/cc_structure.py:100,122 | Break requires a close through the level | close | BH:106 "i at least like to see a close above or below on the same time frame as the market structure anchor" | SOURCED | |
90: | C05 | cryptocred/cc_structure.py:81,95,117 | Break must violate a sequence (lower high broken by higher high) | require_prior_sequence=True | BH:23 "for a bullish market structure break it is when a sequence of lower highs is violated by a higher high" | SOURCED | Code checks one prior swing only (H_last < H_prev). |
91: | C06 | cryptocred/cc_structure.py:81,134-135 | Mid-range MSB filter default | off | BH:66 "i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade" | CONCEPT-ONLY | Default OFF keeps the MSBs the trader calls noise. |
92: | C07 | cryptocred/cc_structure.py:63,81 | Range lookback | 50 bars | BH:66 (same) | CONCEPT-ONLY | |
93: | C08 | cryptocred/cc_structure.py:63,81 | Range-extreme band | 25% of span | BH:66 (same) | CONCEPT-ONLY | |
94: | C09 | cryptocred/cc_retest.py:17,37,46 | Retest touch tolerance | 0.15% | INQ:45 "the immediate retest is when you trade at or near structure when it breaks" | CONCEPT-ONLY | |
95: | C10 | cryptocred/cc_retest.py:17,38,47 | Retest void if close beyond level | 0.5% | INQ:51 "you essentially eradicate the risk of falling for a failed breakout" | CONCEPT-ONLY | Docstring cites C07-E04 for this (cc_retest.py:6); C07-E04 is timeframe alignment. MISCITED. |
96: | C11 | cryptocred/cc_retest.py:17,31 | Retest expiry | 200 bars | - INQ:139 "a lot can happen between a break and the subsequent retest" (no limit) | NO-SOURCE | |
97: | C12 | cryptocred/cc_retest.py:57,63 | Immediate vs rounded split | 5 bars | INQ:45 "the main distinguishing factor is time and space" (CT-038) | CONCEPT-ONLY | Imported by cc_setups.py:19, never called. |
98: | C13 | cryptocred/cc_setups.py:43 | Setup 1 entry at the broken level | level | BH:58 "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low" | SOURCED | |
99: | C14 | cryptocred/cc_setups.py:34,45 | Setup 1 stop = level x (1 -/+ 0.1%) | 0.1% | - (no stop rule in BH or INQ) | NO-SOURCE | |
100: | C15 | cryptocred/cc_setups.py:34,64,46,133 | Setups 1-2 fixed target | 1.5R | - BH:82 "greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5" | NO-SOURCE | 1.5 is his trend MINIMUM R:R (a filter); code uses it as the take-profit. |
101: | C16 | cryptocred/cc_setups.py:64,91,118 | Fib zone shallow edge | 0.618 | BH:114 "personally i look for support resistance structures anywhere between the 618 and 786 retracement" | SOURCED | BH:117 "there's no fixed answer really". |
102: | C17 | cryptocred/cc_setups.py:64,91,118 | Fib zone deep edge | 0.786 | BH:114 (same) | SOURCED | |
103: | C18 | cryptocred/cc_setups.py:96-102,123-129 | Setup 2 entry = first touch, filled at the 0.618 edge | rule | BH:114 looks for "structures" inside the zone | CONCEPT-ONLY | He waits for structure in the zone; code fills on touch. |
104: | C19 | cryptocred/cc_setups.py:104,131 | Setup 2 stop beyond 0.786 x 0.1% | rule | - BH:114 "above the most recent low" is entry location, no stop | NO-SOURCE | |
105: | C20 | cryptocred/cc_setups.py:65,94,121 | Setup 2 zone expiry | 200 bars | - | NO-SOURCE | Hard-coded. |
106: | C21 | cryptocred/cc_setups.py:151,168 | Setup 3 failure window | 20 bars | BH:128 "failed continuation is suggestive of reversal" | CONCEPT-ONLY | |
107: | C22 | cryptocred/cc_setups.py:173-182,196-205 | Setup 3 trigger: no new extreme in window AND window-end close back through the broken level | rule | BH:128 "if we get a higher high bullish into a lower low invalidated then you have bulls offside" | CONCEPT-ONLY | His trigger is the invalidating swing, not a close after N bars. |
108: | C23 | cryptocred/cc_setups.py:183,206 | Setup 3 stop = broken level x 0.1% | 0.1% | - | NO-SOURCE | |
109: | C24 | cryptocred/cc_setups.py:151,207 | Setup 3 fixed target | 2.0R | - BH:82 (counter-trend MINIMUM 2:1) | NO-SOURCE | Same role swap as C15. |
110: | C25 | cryptocred/cc_bt_adapter.py:17,47 | Time exit | 1440 bars | - BH:82 "shorter holding periods" (counter-trend only, no number) | NO-SOURCE | |
111:
112: Plumbing (cryptocred): cc_bt_adapter.py:17 taker_fee 0.0005 / maker_fee 0.0; stop_first=True.
113:
114: ## 3. positioning
115:
116: positioning: 0 SOURCED, 4 CONCEPT-ONLY, 3 NO-SOURCE.
117:
118: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
119: |---|---|---|---|---|---|---|
120: | P01 | positioning/funding_cvd_fade.py:70 | Funding percentile window | 90 records | whale_positioning_evidence:30 "Extreme funding" T2 (Memon 2026) - a table row, no quote | CONCEPT-ONLY | FORMULAS.md:369 "all UNDEFINED in source". |
121: | P02 | positioning/funding_cvd_fade.py:70-71 | High-funding extreme | pct >= 0.95 | same | CONCEPT-ONLY | |
122: | P03 | positioning/funding_cvd_fade.py:71 | Low-funding extreme | pct <= 0.05 | same | CONCEPT-ONLY | |
123: | P04 | positioning/funding_cvd_fade.py:88-91,114-117 | Side: high funding -> short, low -> long | rule | FORMULAS.md:356 "funding-extreme reversion"; no source sentence on direction in repo | CONCEPT-ONLY | |
124: | P05 | positioning/funding_cvd_fade.py:70 | Divergence lookback n | 20 bars | - T055a_POSITIONING_FLOW.md:113 "20-50 bar lookback" (our own hypothesis) | NO-SOURCE | |
125: | P06 | positioning/funding_cvd_fade.py:71,79-91 | Divergence AND funding both required (use_divergence=True) | gate | - FORMULAS.md:361 "Merge decision: supervisor 2026-09-29" | NO-SOURCE | A gate no source gives. |
126: | P07 | positioning/funding_cvd_fade.py:62-65 | Divergence: new n-bar close extreme with CVD inside its n-bar range | rule | - (T055a H2, internal) | NO-SOURCE | |
127:
128: Plumbing (positioning): funding_cvd_fade.py:48 CVD = running sum of 2*tbv - v; trade_costs.py:47 fee_rt 0.0010
129: (Binance taker; live venue is Deribit, backtest/fees.py); trade_costs.py:47 slip_rt 0.0002 (FORMULAS.md:347 "internal arithmetic").
130:
131: ## 4. session
132:
133: session: 1 SOURCED, 2 CONCEPT-ONLY, 3 NO-SOURCE.
134:
135: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
136: |---|---|---|---|---|---|---|
137: | S01 | session/session_momentum.py:12,40 | First window | 30 min | T055b:30 "intraday momentum, first-half-hour predicts last-half-hour" | CONCEPT-ONLY | Paper is in VOLUME time (FABIO_BTC_RESEARCH_2026-09-30.md:70, BTC_SESSION_EXTERNAL_2026-10-04.md:90); code uses clock minutes. |
138: | S02 | session/session_momentum.py:12,80 | Entry time | 30 min after start | T055b:30 predicts the LAST half-hour | CONCEPT-ONLY | Default enters for the rest of the day, not the last half-hour (FORMULAS.md:381). |
139: | S03 | session/session_momentum.py:11,29 | Session start | 00:00 UTC | - FORMULAS.md:382 "UNDEFINED in source" | NO-SOURCE | Fixed UTC, no DST (B102). |
140: | S04 | session/session_momentum.py:23,29 | Session length | 24 h (UTC day) | - | NO-SOURCE | 24/7 adaptation is ours (session_momentum.py:5-6). |
141: | S05 | session/session_momentum.py:12,71-74 | Minimum first-window move | 0.0 | - | NO-SOURCE | Inert at default. |
142: | S06 | session/session_momentum.py:71-74 | Side = sign of first-window return (continuation) | rule | T055b:30 "first-half-hour predicts last-half-hour" | SOURCED | BTC_SESSION_EXTERNAL:88-90 reports reversal at hour scale (counter-evidence). |
143:
144: Plumbing (session): session_momentum.py:11 bar_min 1.
145:
146: ## 5. turn_of_candle
147:
148: turn_of_candle: 2 SOURCED, 1 CONCEPT-ONLY, 2 NO-SOURCE.
149:
150: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
151: |---|---|---|---|---|---|---|
152: | T01 | turn_of_candle/turn_of_candle.py:3 | Candle length | 15 min | T055b:51 "Turn-of-candle effect (returns concentrated at 15-min candle opens)" | SOURCED | |
153: | T02 | turn_of_candle/turn_of_candle.py:36 | Turn minute | minute 0 of the quarter | T055b:51 (same) | SOURCED | |
154: | T03 | turn_of_candle/turn_of_candle.py:59,68; alerts/live_layers.py:177 | Lead | 1 min (enter at minute 14 close) | - | CONCEPT-ONLY | |
155: | T04 | turn_of_candle/turn_of_candle.py:59 | Side (backtest) | long | - FORMULAS.md:393 "direction of the effect is NOT stated" | NO-SOURCE | |
156: | T05 | alerts/live_layers.py:170-182 | Side (live testnet) = sign of the quarter's minute-0 taker imbalance | rule | - (operator 2026-09-30 data-collection ruling, live_layers.py:171-175) | NO-SOURCE | Trades on testnet as "sampling"; T055_BT_c3.md: no gross edge. |
157:
158: ## 6. tick
159:
160: tick: 4 SOURCED, 6 CONCEPT-ONLY, 2 NO-SOURCE. Source is the operator's own spec (T040), the only trader-equivalent
161: for this layer.
162:
163: | ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
164: |---|---|---|---|---|---|---|
165: | K01 | tick/tick_extremes.py:214; tick/build_tiers.py:66,72 | Timeframes | 1, 2, 3, 5, 10, 15 min | T040:40-41 "Compute for each time frame 1m, 2m, 3m, 5m, 10m and 15 minutes" | SOURCED | |
166: | K02 | tick/tick_extremes.py:162,214; tick/build_tiers.py:29,68-70 | Indicators: net_delta, cvd_change, volume, price_change_pct, oi_delta | list | T040:35-36 "flag unusual increase or decrease(the change) in price or cvd or volume or oi or net delta etc." | SOURCED | cvd_change == net_delta per bucket (tick_extremes.py:56): one reading, two flags (Q9). |
167: | K03 | tick/build_tiers.py:33-38,67 | History | klines 2022-01..; OI 2025-09.. | T040:39-40 "duration/range of ALL TIME using our Binance exchange API" | CONCEPT-ONLY | Neither series is all-time. |
168: | K04 | tick/tick_extremes.py:108-147; tick/tick_oi_extremes.py:90-112 | Tiering by gaps between consecutive ranks | rule | T040:46-48 "check the diff from 1st -> check third highest and check the diff from 2nd -> In this way detect a range to group these" | SOURCED | |
169: | K05 | tick/tick_extremes.py:108,143; tick/tick_oi_extremes.py:90,103; tiers_meta.json:30 | New tier when gap > factor x median gap | 1.5 | T040:47-48 (same; no number) | CONCEPT-ONLY | |
170: | K06 | tick/tick_extremes.py:149,214; tick/tick_oi_extremes.py:115,156; tick/build_tiers.py:66-67 | Ranks kept per side | top 20 | T040:43-47 highest, second, third... (no cut-off) | CONCEPT-ONLY | Only the 20 all-time extremes can ever flag: 0.11 flags/day (tiers_meta.json:17). |
171: | K07 | tick/tick_extremes.py:80-96; tick/tick_oi_extremes.py:65-77 | Session windows asian 00-08, european 08-13, overlap 13-16:30, american 16:30-21, off 21-24 UTC | rule | T040:50 "Also note the time period (when it happened - session info etc.)" | CONCEPT-ONLY | Context tag only. |
172: | K08 | tick/tick_extremes.py:98-106; tick/tick_oi_extremes.py:80-87 | Funding window | +-30 min of 00/08/16 UTC | - (the operator text has no funding window; added in our design, T040:70) | NO-SOURCE | Context tag only. |
173: | K09 | tick/tick_extremes.py:58 | Price % change over the same bucket | rule | T040:51 "Calculate the % change in price during the corresponding time period." | SOURCED | |
174: | K10 | tick/tick_flagger.py:142,100 | Cooldown | 30 min | T040:18 "Needs its own cooldown, same as the existing candle-alert cooldown" | CONCEPT-ONLY | No candle-alert cooldown exists to copy (alerts dedup on (t, event), alerts/live_layers.py:6). |
175: | K11 | tick/tick_flagger.py:95-97 | Escalation to a more extreme tier bypasses cooldown | rule | - | NO-SOURCE | |
176: | K12 | tick/tick_flagger.py:14-46,62-69 | Boundary = least extreme value of a tier; reading >= boundary flags | rule | T040:48 "group these as per categories of severity/intensity/strength" | CONCEPT-ONLY | |
177:
178: Plumbing (tick): tick_oi_extremes.py:16-17 OI tf must be a multiple of 5 (5m metrics); build_tiers.py:67 OI tfs 5/10/15;
179: tick_extremes.py:101 funding resets 0/480/960 (exchange schedule).
180:
181: ## 7. consensus
182:
183: consensus: 0 SOURCED, 0 CONCEPT-ONLY, 0 NO-SOURCE. No trading parameter: the writer never gates, votes or weights
184: (writer.py.new:4-6; ARCHITECTURE_TWO_CORES_2026-10-01.md:43 "Consensus is an observation. It does not gate, veto, or
185: delay any core trade.").
186: Plumbing: writer.py.new:44 TOM_KEYS, :45 FABIO_KEYS, :46 RSI_TFS (all from ARCHITECTURE:37-39), :42 DEFAULT_DIR.
187:
188: ## 8. REJECT list
189:
190: Playbook Part I (methodology/playbook.md:28,36): a citation that cannot be opened and matched is REJECT.
191: 1. Malkan quotes (WR:45, :77, :117, :120, :128, :144) are copied from blog.elearnmarkets.com and chartink.com; no
192:    Malkan transcript or saved page is in the repo. Until a page capture or transcript is matched, R08/R09/R14/R15 rest
193:    on a secondary copy. Not downgraded here (the text is quoted and URL-cited) but REJECT if the URLs fail to match.
194: 2. Memon 2026 (positioning): the repo holds a tier label only (whale_positioning_evidence:30); no title, URL, quote or
195:    threshold. P01-P04 cannot rise above CONCEPT-ONLY, and the citation is REJECT until opened and matched.
196: 3. cc_retest.py:6 cites C07-E04 for the 0.5% invalidation; C07-E04 (INQ RULE 3) is timeframe alignment. Miscited.
197: 4. Tuning grids: run_rsi_backtest.py:265-271 and tolerance_sweep.py:45 search over parameters (including the period
198:    that has a source). The provenance rule says unsourced values are removed or replaced, never tuned: these grids
199:    should not choose live values.
200: 5. Role swaps (NO-SOURCE although the number is the trader's): C15 1.5R and C24 2.0R targets (BH:82 minimums).
201:
202: Remove-or-replace candidates (NO-SOURCE that decide a trade): R21-R23, C14, C15, C19, C23, C24, C25, P06, T04, T05.
203:
204: ## 9. Open questions
205:
206: - Q1 (rsi): fetch a Malkan transcript or page capture for period 14 (R01), the regime window (R11) and the band (R12).
207: - Q2 (rsi): replace the 1%/2%/100-bar bracket (R21-R23) with Malkan's own exit (candle-low stop WR:123, RSI-60 target
208:   WR:128, HTF-RSI hold WR:132-133)? Operator call.
209: - Q3 (rsi): params/default.json:15 tolerance 0 is rejected by rsi_events.py:20-21. What does the live runner pass?
210: - Q4 (rsi): malkan_mtf.state_asof doc (malkan_mtf.py:26-31) takes bar-OPEN times; run_rsi_backtest.py:220,234 passes
211:   close times (htf_close_times). A caller that follows the docstring leaks the unclosed HTF bar. Confirm and fix doc.
212: - Q5 (cryptocred): no stop rule in BH or INQ. Is there a CryptoCred source (other videos: XeQV2ECtZVQ, Yp0k8HD5xro,
213:   _ndAoizXy64) that gives stop placement or a target method?
214: - Q6 (cryptocred): classify_retest_timing is never called; INQ:51 says rounded retests are clearer. Should setup 1
215:   use it?
216: - Q7 (positioning): open Memon 2026 and record title, URL and the extreme definition, or drop P01-P04.
217: - Q8 (session): volume-time vs clock-time (S01). Keep the clock proxy or build volume time?
218: - Q9 (tick): cvd_change equals net_delta for a single bucket, so each reading flags twice. Was CVD meant as a
219:   multi-bucket running change?
220: - Q10 (tick): K10 copies a candle-alert cooldown that does not exist. Operator to state the cooldown.
221: - Q11 (turn_of_candle): T05 trades on testnet with a NO-SOURCE side under a sampling ruling; confirm it stays
222:   sampling-only and is excluded from any edge claim.
```

## E20

### MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md

SHA-256: `b261b96a1be8dee4009aecc5db21861b62194fbe5c31d57acf30bef57f4c36aa`

```text
1: # T055 C1/C2 RERUN, full funding, 2026-10-07
2:
3: Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Replaces T055_BT_c1_RERUN_2026-10-06.md and T055_BT_c2_RERUN_2026-10-06.md (commit 4c74cd7, research branch) for the verdict.
4:
5: ## Why the 10-06 rerun is not valid
6: - The 10-06 C1 report states funding history from 1756684800000 ms (2025-09-01), i.e. about 12 months, and an OOS net identical to the 09-29 run (-0.3992%): it did not use the 80 funding files (2020-01..2026-08, 7305 records).
7: - With all 7305 records loaded, run_t055 c1 crashes: ValueError in trade_costs.funding_paid, funding covers to 1788192000001 (2026-08-31) but bars run to 2026-09-26. Reproduced 2026-10-07.
8: - Fix (research code, not live): run_t055.load_data keeps only bars that close inside funding coverage. Test: backtest/layers/test_run_t055.py::TestFundingForC2::test_load_data_clips_bars_to_funding_coverage (failed before the fix, 26 pass after). C1 now 35008 15m bars (was 37536), C2 490656 5m bars.
9: - Command (research worktree mts-research at 5334975 plus the fix, absolute data roots): python -m MyTradingSys.backtest.layers.run_t055 --candidate c1|c2 --data-root <repo>/Dumps/backtest/raw_1m_2022 --data-root2 <repo>/Dumps/backtest/raw. Raw output: BinanceDataFeed_backups/t055_rerun_2026-10-07/.
10:
11: ## Result
12: | candidate | verdict | OOS n | OOS net mean | OOS net Sharpe | funding coverage | note |
13: |---|---|---|---|---|---|---|
14: | C1 funding_cvd_fade | FAIL | 76 | -0.0453% | -0.0346 | from 2020-01, all trades funded | OOS net moved from -0.3992% (09-29 and 10-06) to -0.0453%; verdict unchanged; criteria oos_mean_net, oos_net_sharpe, same_sign fail; still 'provisional' (single year of OOS) |
15: | C2 session_momentum | FAIL | 299 | +0.0177% | 0.0084 | from 2020-01 | oos_mean_net PASS, Sharpe FAIL, only 1 of 2 OOS years positive; the 10-06 run (n=519, -0.2988%) used the wrong funding window |
16:
17: Both candidates close under the T055 rule (FAIL closes). Nothing was tuned.
18:
19: ## Raw reports
20:
21: ### C1
22:
23: #### T055 backtest - C1 (funding_cvd_fade)
24:
25: Verdict: **FAIL** (provisional: ~12 months of funding, single 70/30 split)
26:
27: Bars 35008 (IS 24505 / OOS 10503); variants 108; cost: fee 10 bps RT + slip 2 bps RT + funding (included). PBO (CSCV, IS daily net): 0.1385
28:
29: IS-chosen: `{"params": {"lookback": 90, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}, "horizon": 48}`
30:
31: | split | n events | gross mean | net mean | hit (gross) | hit (net) | net Sharpe |
32: |---|---|---|---|---|---|---|
33: | IS | 129 | 0.5244% | 0.4113% | 0.6047 | 0.5271 | 0.2736 |
34: | OOS | 76 | 0.0650% | -0.0453% | 0.4868 | 0.4737 | -0.0346 |
35:
36: Funding coverage (funding history from 1577836800000 ms; trades before it are net of fees+slippage only, no funding): IS: 129 funded / 0 fee-only trades, funded-trade net 0.4113% vs same trades without funding 0.4044%, fee-only-trade net n/a; OOS: 76 funded / 0 fee-only trades, funded-trade net -0.0453% vs same trades without funding -0.0550%, fee-only-trade net n/a
37:
38: OOS by calendar year: 2026: n=76 net=-0.0453%
39:
40: ## Criteria (runbook step 4)
41:
42: | criterion | result |
43: |---|---|
44: | oos_n>=30 | PASS |
45: | oos_mean_net>0 | FAIL |
46: | oos_net_sharpe>=0.3 | FAIL |
47: | pbo<0.5 | PASS |
48: | same_sign_is_oos | FAIL |
49:
50: No parameter was tuned on OOS. On FAIL the candidate closes; on PASS register alert-only.
51:
52: ## Top IS grid points (by net mean)
53:
54: | params | horizon | n | net mean |
55: |---|---|---|---|
56: | `{"lookback": 90, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 129 | 0.4113% |
57: | `{"lookback": 90, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 43 | 0.4109% |
58: | `{"lookback": 60, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 119 | 0.4081% |
59: | `{"lookback": 60, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 44 | 0.3931% |
60: | `{"lookback": 180, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 54 | 0.3816% |
61: | `{"lookback": 180, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 134 | 0.3105% |
62: | `{"lookback": 90, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 191 | 0.2642% |
63: | `{"lookback": 60, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 202 | 0.2322% |
64: | `{"lookback": 180, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 204 | 0.1177% |
65: | `{"lookback": 60, "n": 20, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 202 | 0.0943% |
66:
67:
68: ### C2
69:
70: #### T055 backtest - C2 (session_momentum)
71:
72: Verdict: **FAIL**
73:
74: Bars 490656 (IS 343459 / OOS 147197); variants 16; cost: fee 10 bps RT + slip 2 bps RT + funding (included). PBO (CSCV, IS daily net): 0.0000
75:
76: IS-chosen: `{"params": {"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.001}, "horizon": "session"}`
77:
78: | split | n events | gross mean | net mean | hit (gross) | hit (net) | net Sharpe |
79: |---|---|---|---|---|---|---|
80: | IS | 731 | 0.2193% | 0.0999% | 0.5075 | 0.4788 | 0.0356 |
81: | OOS | 299 | 0.1358% | 0.0177% | 0.5084 | 0.4749 | 0.0084 |
82:
83: Funding coverage (funding history from 1577836800000 ms; trades before it are net of fees+slippage only, no funding): IS: 731 funded / 0 fee-only trades, funded-trade net 0.0999% vs same trades without funding 0.0993%, fee-only-trade net n/a; OOS: 299 funded / 0 fee-only trades, funded-trade net 0.0177% vs same trades without funding 0.0158%, fee-only-trade net n/a
84:
85: OOS by calendar year: 2025: n=157 net=0.0636%, 2026: n=142 net=-0.0332%
86:
87: ## Criteria (runbook step 4)
88:
89: | criterion | result |
90: |---|---|
91: | oos_n>=30 | PASS |
92: | oos_mean_net>0 | PASS |
93: | oos_net_sharpe>=0.3 | FAIL |
94: | pbo<0.5 | PASS |
95: | same_sign_is_oos | PASS |
96: | >=2_positive_oos_years | FAIL |
97:
98: No parameter was tuned on OOS. On FAIL the candidate closes; on PASS register alert-only.
99:
100: ## Top IS grid points (by net mean)
101:
102: | params | horizon | n | net mean |
103: |---|---|---|---|
104: | `{"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.001}` | session | 731 | 0.0999% |
105: | `{"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.0}` | session | 843 | 0.0506% |
106: | `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 30, "min_abs": 0.001}` | session | 686 | 0.0463% |
107: | `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 30, "min_abs": 0.0}` | session | 844 | 0.0438% |
108: | `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 30, "min_abs": 0.0}` | session | 1192 | -0.0800% |
109: | `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 1410, "min_abs": 0.001}` | session | 818 | -0.1103% |
110: | `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 1410, "min_abs": 0.0}` | session | 1192 | -0.1155% |
111: | `{"bar_min": 5, "session_start_min": 0, "first_min": 60, "entry_min": 1410, "min_abs": 0.0}` | session | 1192 | -0.1270% |
112: | `{"bar_min": 5, "session_start_min": 0, "first_min": 60, "entry_min": 1410, "min_abs": 0.001}` | session | 946 | -0.1299% |
113: | `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 1410, "min_abs": 0.001}` | session | 539 | -0.1338% |
114:
```

## E21

### MyTradingSys/backtest/layers/session/session_momentum.py

SHA-256: `b82db9757eea1a88d3b828fd6201167563d2e6199d9d39300a964d4400011751`

```text
1: """
2: candidate C2, intraday session momentum.
3: Source: Shen, Urquhart, Wang, Financial Review 57(2), 319-344, 2022 (T1):
4: the return over the first half-hour predicts the return of the last half-hour.
5: The 24/7 BTC adaptation (session = UTC day from `session_start_min`; "ny"/"london" = DST-aware day_gates open, B102) is UNDEFINED in the source
6: and is a parameter, not a claim. Independent layer, never a Tom filter.
7: """
8:
9: import datetime as dt
10: from typing import List, Dict
11:
12: from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc, london_open_utc
13:
14: _ANCHORS = {"ny": ny_open_utc, "london": london_open_utc}  # B102: DST-aware, None on weekends/holidays
15:
16: def session_momentum_events(bars: List[Dict], bar_min: int = 1, session_start_min=0,
17:                             first_min: int = 30, entry_min: int = 30, min_abs: float = 0.0) -> List[Dict]:
18:     if not bars:
19:         raise ValueError("bars cannot be empty")
20:     if bar_min <= 0:
21:         raise ValueError("bar_min must be positive")
22:     if first_min <= 0:
23:         raise ValueError("first_min must be positive")
24:     if entry_min < first_min:
25:         raise ValueError("entry_min must be >= first_min")
26:
27:     bar_ms = bar_min * 60000
28:     DAY = 86400000
29:
30:     # Group bars by session
31:     sessions = {}
32:     for i, bar in enumerate(bars):
33:         t = bar["t"]
34:         if isinstance(session_start_min, str):
35:             # DST-aware named anchor: session starts at that day's open; days with no open are skipped
36:             day = dt.datetime.fromtimestamp(t // DAY * DAY / 1000, tz=dt.timezone.utc).date()
37:             o = _ANCHORS[session_start_min](day)
38:             if o is None:
39:                 continue
40:             S = int(o.timestamp() * 1000)
41:             if S > t:
42:                 prev = _ANCHORS[session_start_min](day - dt.timedelta(days=1))
43:                 if prev is None:
44:                     continue
45:                 S = int(prev.timestamp() * 1000)
46:         else:
47:             S = (t // DAY) * DAY + session_start_min * 60000
48:             if S > t:
49:                 S -= DAY
50:         if S not in sessions:
51:             sessions[S] = []
52:         sessions[S].append((i, bar))
53:
54:     events = []
55:
56:     for S in sorted(sessions.keys()):
57:         session_bars = sessions[S]
58:         E = S + first_min * 60000
59:
60:         # Find first_bar
61:         first_bar = None
62:         for i, bar in session_bars:
63:             if bar["t"] >= S and bar["t"] < E:
64:                 first_bar = bar
65:                 break
66:
67:         if first_bar is None:
68:             continue
69:
70:         # Find last_bar
71:         last_bar = None
72:         for i, bar in reversed(session_bars):
73:             if bar["t"] >= S and bar["t"] + bar_ms <= E:
74:                 last_bar = bar
75:                 break
76:
77:         if last_bar is None:
78:             continue
79:
80:         # Compute return
81:         open_price = first_bar["o"]
82:         if open_price <= 0:
83:             continue
84:         close_price = last_bar["c"]
85:         r_first = close_price / open_price - 1.0
86:
87:         # Determine side
88:         side = None
89:         if r_first > min_abs:
90:             side = "long"
91:         elif r_first < -min_abs:
92:             side = "short"
93:
94:         if side is None:
95:             continue
96:
97:         # Find entry bar
98:         entry_time = S + entry_min * 60000
99:         entry_bar = None
100:         for i, bar in session_bars:
101:             if bar["t"] >= S and bar["t"] + bar_ms == entry_time:
102:                 entry_bar = (i, bar)
103:                 break
104:
105:         if entry_bar is None:
106:             continue
107:
108:         entry_idx, _ = entry_bar
109:         events.append({
110:             "i": entry_idx,
111:             "side": side,
112:             "r_first": r_first,
113:             "session_start": S
114:         })
115:
116:     # Sort by entry index
117:     events.sort(key=lambda x: x["i"])
118:     return events
```

### MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py

SHA-256: `06f76b4c1db378662b1108ad40132126d9398f6699c598c36eea68d1e48f34af`

```text
1: """
2: candidate C1. Funding-extreme mean reversion (T2, Memon 2026, 7y Binance, via
3: research/whale_positioning_evidence_2026-09-12.md; that source does NOT give the percentile threshold, so
4: `hi`/`lo`/`lookback` are UNDEFINED in source and are grid parameters) merged with a CVD/price divergence
5: fade (T055a H2). It is an independent layer, never a filter on the Tom core. Signals fade the crowded side:
6: extreme high funding -> short, extreme low funding -> long. Events use the shape
7: `{"i": int, "side": "long"|"short", ...}` consumed by `layers/runner.forward_return_stats`; the caller enters
8: at `closes[i]`.
9: """
10:
11: from bisect import bisect_right
12:
13:
14: def funding_percentiles(funding: list, lookback: int) -> list:
15:     """Calculate funding percentiles for each time point."""
16:     if lookback < 1:
17:         raise ValueError("lookback must be >= 1")
18:     if len(funding) < lookback:
19:         return []
20:
21:     result = []
22:     for k in range(lookback - 1, len(funding)):
23:         window = [rate for (_, rate) in funding[k - lookback + 1 : k + 1]]
24:         r = funding[k][1]
25:         pct = sum(1 for x in window if x <= r) / lookback
26:         result.append((funding[k][0], pct))
27:     return result
28:
29:
30: def funding_pct_at(series: list, t_ms: int):
31:     """Get the latest funding percentile before or at time t_ms."""
32:     if not series:
33:         return None
34:     idx = bisect_right([x[0] for x in series], t_ms) - 1
35:     if idx < 0:
36:         return None
37:     return series[idx][1]
38:
39:
40: def cvd_price_divergence(bars: list, n: int) -> list:
41:     """Calculate CVD price divergence events."""
42:     if n < 1 or not bars:
43:         raise ValueError("n must be >= 1 and bars must not be empty")
44:
45:     # Calculate cumulative CVD
46:     cvd = [0] * len(bars)
47:     for i in range(len(bars)):
48:         cvd[i] = 2 * bars[i]["tbv"] - bars[i]["v"]
49:         if i > 0:
50:             cvd[i] += cvd[i - 1]
51:
52:     events = []
53:     for i in range(n, len(bars)):
54:         pc = [bars[j]["c"] for j in range(i - n, i)]
55:         pv = [cvd[j] for j in range(i - n, i)]
56:
57:         price_max = max(pc)
58:         price_min = min(pc)
59:         cvd_max = max(pv)
60:         cvd_min = min(pv)
61:
62:         if bars[i]["c"] > price_max and cvd[i] < cvd_max:
63:             events.append({"i": i, "kind": "bearish"})
64:         elif bars[i]["c"] < price_min and cvd[i] > cvd_min:
65:             events.append({"i": i, "kind": "bullish"})
66:
67:     return events
68:
69:
70: def funding_cvd_fade_events(bars: list, funding: list, lookback: int = 90, n: int = 20, hi: float = 0.95,
71:                             lo: float = 0.05, use_divergence: bool = True) -> list:
72:     """Generate events for funding-extreme reversion merged with CVD/price divergence fade."""
73:     series = funding_percentiles(funding, lookback)
74:     if not series:
75:         return []
76:
77:     events = []
78:
79:     if use_divergence:
80:         # Use divergence-based approach
81:         divergences = cvd_price_divergence(bars, n)
82:         for d in divergences:
83:             pct = funding_pct_at(series, bars[d["i"]]["t"])
84:             if pct is None:
85:                 continue
86:
87:             side = None
88:             if d["kind"] == "bearish" and pct >= hi:
89:                 side = "short"
90:             elif d["kind"] == "bullish" and pct <= lo:
91:                 side = "long"
92:
93:             if side:
94:                 events.append({
95:                     "i": d["i"],
96:                     "side": side,
97:                     "funding_pct": pct,
98:                     "div": d["kind"]
99:                 })
100:     else:
101:         # Use funding-only approach
102:         for t, pct in series:
103:             # Find the first bar with time >= t
104:             i = None
105:             for j in range(len(bars)):
106:                 if bars[j]["t"] >= t:
107:                     i = j
108:                     break
109:
110:             if i is None:
111:                 continue
112:
113:             side = None
114:             if pct >= hi:
115:                 side = "short"
116:             elif pct <= lo:
117:                 side = "long"
118:
119:             if side:
120:                 events.append({
121:                     "i": i,
122:                     "side": side,
123:                     "funding_pct": pct,
124:                     "div": None
125:                 })
126:
127:     # Sort by index to ensure stable order
128:     events.sort(key=lambda x: x["i"])
129:     return events
130:
```

### MyTradingSys/backtest/layers/alerts/live_runner_cli.py

SHA-256: `820a8d394ebae544bb27899a8a73d8fa9bd113aa1c41455d3ce5e392aee10748`

```text
1: """
2: Thin IO/CLI shell around sibling module `live_runner_core.py` (not yet on disk when this task was packed).
3:
4: This module fetches closed Binance klines over public REST, wires two registered layers (RSI and FABIO CVD),
5: and calls sibling module 085's pure core every poll. Alert-only: no orders, no execution imports, no keys,
6: no mainnet (public market-data endpoint only).
7: """
8:
9: import json
10: import pathlib
11: import argparse
12: import time
13: import urllib.request
14: import urllib.parse
15: import sys
16:
17: from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl
18: from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
19: from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
20: from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import cvd_absorption_events
21:
22:
23: def klines_to_bars(raw: list) -> list:
24:     """
25:     Pure mapper, no network. `raw` is Binance `/api/v3/klines` response format:
26:     a list of rows, each row a list/tuple of at least 10 elements
27:     `[open_time_ms, open, high, low, close, volume, close_time_ms, quote_asset_volume, num_trades,
28:     taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore]` (strings or numbers -- cast with
29:     `int`/`float`). Raise `ValueError` if any row has fewer than 10 elements. Map each row `r` to
30:     `{"t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]),
31:     "v": float(r[5]), "tbv": float(r[9])}` (same bar shape as `bt_data.load_klines`: `t/o/h/l/c/v/tbv`).
32:     Return the mapped list in the same order as `raw` (do not sort or filter here). Return `[]` if `raw`
33:     is empty.
34:     """
35:     if not raw:
36:         return []
37:
38:     bars = []
39:     for r in raw:
40:         if len(r) < 10:
41:             raise ValueError("Each row must have at least 10 elements")
42:         bar = {
43:             "t": int(r[0]),
44:             "o": float(r[1]),
45:             "h": float(r[2]),
46:             "l": float(r[3]),
47:             "c": float(r[4]),
48:             "v": float(r[5]),
49:             "tbv": float(r[9])
50:         }
51:         bars.append(bar)
52:
53:     return bars
54:
55:
56: def fetch_closed_bars(fetch_fn, symbol: str, interval: str, limit: int = 100) -> list:
57:     """
58:     Fetches closed bars using `fetch_fn` and processes them.
59:     Drops the last possibly-open row to ensure only closed bars are returned.
60:     Raises `ValueError` if fewer than 2 bars are returned or if bars are not strictly ascending by time.
61:     """
62:     raw = fetch_fn(symbol, interval, limit)
63:     bars = klines_to_bars(raw)
64:
65:     if len(bars) < 2:
66:         raise ValueError("Not enough closed bars returned")
67:
68:     # Drop the last possibly-open bar
69:     closed = bars[:-1]
70:
71:     # Check strictly ascending by time
72:     for i in range(1, len(closed)):
73:         if closed[i]["t"] <= closed[i-1]["t"]:
74:             raise ValueError("Bars are not strictly ascending by time")
75:
76:     return closed
77:
78:
79: def default_fetch_klines(symbol: str, interval: str, limit: int) -> list:
80:     """
81:     Real network call (not unit-tested; tests only use the injectable `fetch_fn` above).
82:     Builds URL and fetches from Binance's public market-data endpoint.
83:     """
84:     url = "https://api.binance.com/api/v3/klines?" + urllib.parse.urlencode({
85:         "symbol": symbol,
86:         "interval": interval,
87:         "limit": limit
88:     })
89:
90:     with urllib.request.urlopen(url, timeout=10) as resp:
91:         body = resp.read()
92:
93:     return json.loads(body)
94:
95:
96: def load_state(path) -> dict:
97:     """
98:     Loads the state from a JSON file.
99:     If the file does not exist, returns an empty state.
100:     """
101:     try:
102:         with open(path, 'r', encoding='utf-8') as f:
103:             return json.load(f)
104:     except FileNotFoundError:
105:         return {"last_t": {}, "prev_events": {}}
106:
107:
108: def save_state(state: dict, path) -> None:
109:     """
110:     Saves the state to a JSON file.
111:     Creates parent directories if needed.
112:     """
113:     pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
114:
115:     with open(path, 'w', encoding='utf-8', newline='\n') as f:
116:         json.dump(state, f, sort_keys=True, indent=2)
117:
118:
119: # Bars between an event's "t" and the first closed bar on which the detector can report it (measured by
120: # replaying 7 days of BTCUSDT 15m/1h through a sliding 99-bar window, 2026-09-29). Every layer's t is its
121: # confirmation bar except volume_fvg (its scan stops one bar short of the newest bar, so a touch shows up 1 bar
122: # later). live_runner_core allows this lag + 1 bar of slack (0 slack on a fresh state).
123: CONFIRM_LAG_BARS = {"volume_fvg": 1}
124:
125:
126: # ---- Fabio v3 live emitter (staged MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow) -----------------------------------
127: # Decision per grid parameter, from research/FABIO_V3_SOURCING_2026-10-02.md: SOURCE = a Fabio quote gives the numeric
128: # value; SHADOW = it does not (NS-grid). A cell is SOURCE only if every parameter it uses is SOURCE. A SOURCE signal is
129: # an ordinary fabio.* alert (has "side", the auto-trader maps it). A SHADOW signal is collection-only: tagged
130: # `collection_only`, carries `shadow_side` and NO "side" and no layer_rules entry, so the auto-trader's layer_side()
131: # returns None and it rejects the alert as unmapped (same pattern as turn_of_candle). No order path exists here.
132: FABIO_V3_DECISIONS = {"N": "SHADOW", "p": "SHADOW", "z_hi": "SHADOW", "m_c": "SHADOW", "f": "SHADOW"}
133: FABIO_V3_GRID = {"N": (60, 120, 240), "p": (0.05, 0.10), "z_hi": (2.0, 2.5, 3.0), "m_c": (5, 15), "f": (0.003, 0.005)}
134: # Not grid-expanded here (spec 7.2 main grid values): day gate off, confirm entry (a discrete SIGNAL on one bar; the
135: # resting-limit ARMED state persists across bars and is not an event), event management.
136: FABIO_V3_FIXED = {"g": "off", "entry_mode": "confirm", "mgmt": "event"}
137: FABIO_V3_FLOW_COLS = ("buy_vol", "sell_vol", "b99_buy_vol", "b99_sell_vol", "thr_days", "fp")
138: FABIO_V3_PARAMS_ID = "fabio_v3_grid_2026-10-02"
139:
140:
141: def fabio_v3_cells(grid=None):
142:     """Cartesian product of the grid as a list of dicts (stable order)."""
143:     import itertools
144:     grid = FABIO_V3_GRID if grid is None else grid
145:     keys = list(grid)
146:     return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]
147:
148:
149: def fabio_v3_cell_decision(cell, decisions=None):
150:     """"SOURCE" only if every parameter of the cell is SOURCE; a missing or unknown decision is SHADOW (fail closed)."""
151:     decisions = FABIO_V3_DECISIONS if decisions is None else decisions
152:     return "SOURCE" if cell and all(decisions.get(k) == "SOURCE" for k in cell) else "SHADOW"
153:
154:
155: def fabio_v3_flow_window(bars):
156:     """The partial NY window (open .. last closed bar) of 1m ORDER-FLOW bars, or None. Order-flow bars carry
157:     aggTrades columns (FABIO_V3_FLOW_COLS); plain Binance klines ({t,o,h,l,c,v,tbv}) do not, so on a klines feed this
158:     returns None and the layer is silent (poll line shows 0). Also None if the window has a gap, is empty, or any bar
159:     has thr_days == 0 (own-day big-trade thresholds = look-ahead, spec section 1)."""
160:     import datetime as dt
161:     from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc
162:     if not bars or any(c not in bars[-1] for c in FABIO_V3_FLOW_COLS):
163:         return None
164:     last = bars[-1]["t"]
165:     opener = ny_open_utc(dt.datetime.fromtimestamp(last / 1000.0, dt.timezone.utc).date())
166:     if opener is None:
167:         return None
168:     t0 = int(opener.timestamp() * 1000)
169:     win = [b for b in bars if t0 <= b["t"] <= last]
170:     if not win or win[0]["t"] != t0 or len(win) != (last - t0) // 60000 + 1:
171:         return None
172:     if any(b.get("thr_days", 0) == 0 for b in win):
173:         return None
174:     return win
175:
176:
177: FABIO_V3_OF_DIR = pathlib.Path(__file__).resolve().parents[4] / "MyTradingSys" / "runtime" / "orderflow_live"
178:
179:
180: def fabio_v3_live_flow(bars, of_dir=None):
181:     """Default flow source of the v3 layer. Bars that already carry the order-flow columns are used as given. On the
182:     klines feed (no such columns) the live order-flow writer's files (orderflow_live.py, R3) are read and cut at the last
183:     closed kline's open time, so the layer and the registry agree on "now". Any read problem, a gap, thr_days == 0 or a
184:     missing file -> None (silent, fail closed)."""
185:     win = fabio_v3_flow_window(bars)
186:     if win or not bars:
187:         return win
188:     try:
189:         from MyTradingSys.backtest.layers.fabio.orderflow_live import load_live_bars
190:         last = bars[-1]["t"]
191:         # a NY window is at most 390 bars: read only the last ~7 h
192:         of = [b for b in load_live_bars(of_dir or FABIO_V3_OF_DIR, since_ms=last - 7 * 3600 * 1000) if b["t"] <= last]
193:     except Exception:  # noqa: BLE001
194:         return None
195:     if not of or of[-1]["t"] != last:      # the writer is behind the klines: stale window, stay silent
196:         return None
197:     return fabio_v3_flow_window(of)
198:
199:
200: def make_fabio_v3_layer(grid=None, decisions=None, fixed=None, run_fn=None, flow_fn=None):
201:     """Layer function fn(bars) -> events for the live registry: one engine run per grid cell, an event per SIGNAL.
202:     `run_fn(win, config)` defaults to fabio v3 engine.run (imported lazily), `flow_fn(bars)` to fabio_v3_live_flow;
203:     both injectable for tests. Event "t" = the signal bar's open time, "event" is unique per (cell, model, side)."""
204:     cells = fabio_v3_cells(grid)
205:     fixed = dict(FABIO_V3_FIXED if fixed is None else fixed)
206:
207:     def _layer(bars):
208:         win = (flow_fn or fabio_v3_live_flow)(bars)
209:         if not win:
210:             return []
211:         run = run_fn
212:         if run is None:
213:             from MyTradingSys.backtest.layers.fabio.v3.engine import run
214:         events = []
215:         for cell in cells:
216:             res = run(win, {**cell, **fixed})
217:             if res.get("verdict") != "SIGNAL":
218:                 continue
219:             side = {1: "long", -1: "short"}.get(res.get("side"))
220:             if side is None:
221:                 continue
222:             decision = fabio_v3_cell_decision(cell, decisions)
223:             tag = "_".join("%s%s" % (k, cell[k]) for k in cell)
224:             ev = {"t": win[-1]["t"], "event": "v3_%s_%s_%s" % (tag, res["model"], side), "model": res["model"],
225:                   "cell": dict(cell), "decision": decision, "entry_ref": res.get("entry"), "stop": res.get("stop"),
226:                   "target": res.get("target")}
227:             if decision == "SOURCE":
228:                 ev["side"] = side
229:             else:
230:                 ev["collection_only"] = True
231:                 ev["shadow_side"] = side
232:             events.append(ev)
233:         return events
234:
235:     return _layer
236:
237:
238: def build_default_registry(fetch_funding=None) -> dict:
239:     """
240:     Builds and returns a registry for two registered layers: RSI and FABIO CVD.
241:     More layers can be added in the same way in future work.
242:     """
243:     def _fabio_cvd_layer_fn(bars):
244:         return cvd_absorption_events(bars)
245:
246:     from MyTradingSys.backtest.layers.alerts import live_layers as ll
247:     _rsi_layer_fn = ll.rsi_level_layer
248:
249:     entries = [
250:         {
251:             "layer": "rsi",
252:             "sub": "rsi_events",
253:             "tf": "1h",
254:             "fn": _rsi_layer_fn,
255:             "params_id": "rsi_40_tol0.5_L1_2026-09-29"
256:         },
257:         {
258:             "layer": "rsi",
259:             "sub": "rsi_events",
260:             "tf": "15m",
261:             "fn": _rsi_layer_fn,
262:             "params_id": "rsi_40_tol0.5_L1_2026-09-29"
263:         },
264:         {
265:             "layer": "rsi",
266:             "sub": "rsi_events",
267:             "tf": "5m",
268:             "fn": _rsi_layer_fn,
269:             "params_id": "rsi_40_tol0.5_L1_2026-09-29"
270:         },
271:         {
272:             "layer": "fabio",
273:             "sub": "cvd_absorption",
274:             "tf": "1h",
275:             "fn": _fabio_cvd_layer_fn,
276:             "params_id": "fabio_cvd_default_2026-09-29"
277:         },
278:         {
279:             "layer": "fabio",
280:             "sub": "cvd_absorption",
281:             "tf": "15m",
282:             "fn": _fabio_cvd_layer_fn,
283:             "params_id": "fabio_cvd_default_2026-09-29"
284:         }
285:     ]
286:     suffix = "_defaults_2026-09-29"
287:     for layer, sub, tf, fn in [
288:         ("fabio", "escalation", "1h", ll.escalation_layer),
289:         ("fabio", "volume_fvg", "1h", ll.volume_fvg_layer),
290:         ("session", "session_momentum", "15m", ll.session_momentum_layer),
291:         ("positioning", "funding_cvd_fade", "1h", ll.make_funding_layer(fetch_funding)),
292:         ("rsi", "malkan_bull", "1h", ll.malkan_bull_layer),
293:         ("rsi", "malkan_bear", "1h", ll.malkan_bear_layer),
294:         ("cryptocred", "sr_flip", "1h", ll.cc_sr_flip_layer),
295:         ("cryptocred", "fib_pullback", "1h", ll.cc_fib_pullback_layer),
296:         ("cryptocred", "failed_msb", "1h", ll.cc_failed_msb_layer),
297:         ("turn_of_candle", "turn_of_candle", "1m", ll.turn_of_candle_layer),
298:         # 2026-09-30 extra timeframes for fill collection (detectors are bar-index based, tf-agnostic)
299:         ("fabio", "escalation", "15m", ll.escalation_layer),
300:         ("fabio", "volume_fvg", "15m", ll.volume_fvg_layer),
301:         ("cryptocred", "sr_flip", "15m", ll.cc_sr_flip_layer),
302:         ("cryptocred", "fib_pullback", "15m", ll.cc_fib_pullback_layer),
303:         ("cryptocred", "failed_msb", "15m", ll.cc_failed_msb_layer),
304:     ]:
305:         entries.append({"layer": layer, "sub": sub, "tf": tf, "fn": fn, "params_id": sub + suffix,
306:                         "confirm_lag_bars": CONFIRM_LAG_BARS.get(sub, 0)})
307:     # Fabio v3: one key, all grid cells inside (a SHADOW cell is collection-only, see FABIO_V3_DECISIONS)
308:     entries.append({"layer": "fabio", "sub": "v3_grid", "tf": "1m", "fn": make_fabio_v3_layer(),
309:                     "params_id": FABIO_V3_PARAMS_ID, "confirm_lag_bars": 0})
310:
311:     # Import here to avoid circular dependency
312:     from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry
313:
314:     return build_registry(entries)
315:
316:
317: def poll_once(registry: dict, symbol: str, tfs: list, fetch_fn, state: dict, limit: int = 100) -> dict:
318:     """
319:     Polls for closed bars from multiple timeframes and runs the registry.
320:     """
321:     bars_by_tf = {}
322:     fetch_errors = []
323:
324:     for tf in sorted(set(tfs)):
325:         try:
326:             bars_by_tf[tf] = fetch_closed_bars(fetch_fn, symbol, tf, limit)
327:         except Exception as exc:
328:             fetch_errors.append({"key": f"fetch:{tf}", "error": str(exc)})
329:
330:     # Import here to avoid circular dependency
331:     from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry
332:
333:     result = run_registry(registry, bars_by_tf, state)
334:
335:     return {
336:         "alerts": result["alerts"],
337:         "state": result["state"],
338:         "errors": fetch_errors + result["errors"]
339:     }
340:
341:
342: def format_poll_line(registry: dict, result: dict, now_ms: int = None) -> str:
343:     """One line per poll: UTC time, totals, then alerts per registered layer key (0 included, so a dead layer
344:     is visible), then the error count. Pure."""
345:     import datetime
346:     now = datetime.datetime.fromtimestamp((now_ms if now_ms is not None else time.time() * 1000) / 1000.0,
347:                                           datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
348:     counts = {k: 0 for k in registry}
349:     for a in result["alerts"]:
350:         k = f'{a["layer"]}|{a["sub"]}|{a["tf"]}'
351:         counts[k] = counts.get(k, 0) + 1
352:     per = " ".join(f"{k}={n}" for k, n in sorted(counts.items()))
353:     return f"poll {now} alerts={len(result['alerts'])} errors={len(result['errors'])} {per}"
354:
355:
356: def main(argv=None) -> int:
357:     """
358:     Main entry point for the CLI.
359:     """
360:     parser = argparse.ArgumentParser()
361:     parser.add_argument("--symbol", default="BTCUSDT")
362:     parser.add_argument("--tfs", default="1h,15m,5m,1m")
363:     parser.add_argument("--state-path", default="MyTradingSys/runtime/live_alert_state.json")
364:     parser.add_argument("--alerts-dir", default="MyTradingSys/runtime/alerts")
365:     parser.add_argument("--limit", type=int, default=100)
366:     parser.add_argument("--poll-seconds", type=int, default=60)
367:     parser.add_argument("--consensus-dir", default=None,
368:                         help="directory for consensus_<date>.jsonl rows (default Dumps/consensus)")
369:     parser.add_argument("--once", action="store_true")
370:
371:     args = parser.parse_args(argv)
372:
373:     registry = build_default_registry()
374:     state = load_state(args.state_path)
375:
376:     def loop_body():
377:         nonlocal state
378:         result = poll_once(registry, args.symbol, args.tfs.split(","), default_fetch_klines, state, args.limit)
379:
380:         # Group alerts by timeframe
381:         alerts_by_tf = {}
382:         for alert in result["alerts"]:
383:             tf = alert["tf"]
384:             if tf not in alerts_by_tf:
385:                 alerts_by_tf[tf] = []
386:             alerts_by_tf[tf].append(alert)
387:
388:         # Write alerts to JSONL files
389:         for tf, group in alerts_by_tf.items():
390:             append_alerts_jsonl(group, pathlib.Path(args.alerts_dir) / f"{tf}.jsonl")
391:
392:         # Consensus row (observation only: never gates a core, never raises). One row per poll in which the Fabio
393:         # core emitted an alert or the Tom card advanced (research/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43).
394:         # Runs after the alert files are written because the rsi block is read back from them.
395:         try:
396:             from MyTradingSys.backtest.layers.consensus.hook import consensus_after_poll
397:             consensus_after_poll(
398:                 result["alerts"], alerts_dir=pathlib.Path(args.alerts_dir),
399:                 state_path=pathlib.Path(args.state_path).with_name("consensus_hook_state.json"),
400:                 base_dir=args.consensus_dir)
401:         except Exception as exc:  # noqa: BLE001 - observation must never stop the alert runner
402:             print(json.dumps({"key": "consensus_hook", "error": str(exc)}), file=sys.stderr, flush=True)
403:
404:         save_state(result["state"], args.state_path)
405:         state = result["state"]
406:
407:         print(format_poll_line(registry, result), flush=True)
408:
409:         # Print errors to stderr
410:         for error in result["errors"]:
411:             print(json.dumps(error), file=sys.stderr, flush=True)
412:
413:     if args.once:
414:         loop_body()
415:         return 0
416:
417:     try:
418:         while True:
419:             loop_body()
420:             time.sleep(args.poll_seconds)
421:     except KeyboardInterrupt:
422:         print("stopped", flush=True)
423:         return 0
424:
425:
426: if __name__ == "__main__":
427:     raise SystemExit(main())
```

## E22

### MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md

SHA-256: `44e9e04465d28b886f7ae5276e4a65664a04e6f5da44d6b8dc886442f24dd3d5`

```text
1: # T055 backtest - C3 (turn_of_candle + quarter-hour opening order imbalance)
2:
3: Verdict: **NO EDGE (FAIL)** - same rule as C1/C2 (OOS n>=30, net mean>0, net Sharpe>=0.3, PBO<0.5, same IS/OOS sign, >=2 positive OOS years). No horizon passes any of the net-mean, Sharpe or year criteria.
4:
5: ## Source (verified 2026-09-29)
6: Kim & Hansen, "The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency Futures", arXiv 2607.09426 (10 Jul 2026, v2 16 Jul). Abstract: "opening order imbalance predicts returns over four to twelve hours". Six Binance perps, trade-level data. Tier T2 (preprint, no replication, cost model not in abstract). The abstract does not give the sign of the relation, so momentum and contrarian are both IS-grid variants.
7:
8: ## Part 1 - driver default (calendar entry, fixed side, no imbalance signal)
9: `run_t055.py --candidate c3` (2,491,200 1m BTCUSDT bars, IS 1,743,840 / OOS 747,360; fee 10 bps RT + slip 2 bps RT + funding). Chosen on IS: lead 2 min, long, 2-bar hold. IS n=116,255 net -0.1183%; OOS n=49,823 gross -0.0000%, net -0.1201%, net Sharpe -1.49; OOS years 2025 -0.1198%, 2026 -0.1203%. PBO 0.0000 (all variants negative; ranking stable only). FAIL: pure cost drag, zero gross drift at the turn.
10:
11: ## Part 2 - order-imbalance signal (script `layers/run_t055_c3_imbalance.py`)
12: Proxy: taker-buy-volume imbalance (2*tbv - v)/v from 1m kline column 9, summed over the opening window (1 or 5 one-minute bars from minute-of-quarter 0). Entry at close of the last window bar; long if imbalance>0 (momentum) or short (contrarian). Grid: window {1,5} x min |imb| {0,0.1} x direction {mom,contra} x horizon {1,2,5 bars (driver defaults), 240, 480, 720 min}. Non-overlapping trades (flat before next entry). Same costs/funding/split (70/30 chronological, params chosen on IS only). PBO: pooled CSCV over all 48 IS variants = 0.0000 (per-horizon PBO not computed; all IS variants negative so it is uninformative).
13:
14: | horizon | IS-chosen | IS n / net | OOS n | OOS gross | OOS net | net Sharpe | OOS yrs +ve |
15: |---|---|---|---|---|---|---|---|
16: | 1 bar | 1m, |imb|>=0.1, contra | 93014 / -0.1168% | 40857 | +0.0005% | -0.1195% | -1.93 | 0/2 |
17: | 2 bar | same | 93014 / -0.1135% | 40857 | +0.0008% | -0.1192% | -1.39 | 0/2 |
18: | 5 bar | same | 93014 / -0.1110% | 40857 | +0.0021% | -0.1179% | -0.91 | 0/2 |
19: | 4h | 5m, all, contra | 7265 / -0.0887% | 3113 | +0.0143% | -0.1058% | -0.12 | 0/2 |
20: | 8h | 5m, all, contra | 3632 / -0.0866% | 1556 | -0.0154% | -0.1353% | -0.11 | 0/2 |
21: | 12h | 5m, |imb|>=0.1, mom | 2397 / -0.0253% | 1029 | -0.0109% | -0.1310% | -0.09 | 0/2 |
22:
23: OOS by year at 4h/8h/12h: 2025 -0.108/-0.132/-0.053%, 2026 -0.104/-0.138/-0.204%. Gross OOS is about zero at every horizon, so there is no gross predictability to lose to costs; 12h IS-chosen direction flips (mom) vs 4h/8h (contra), i.e. unstable sign.
24:
25: ## Limits of the proxy and test
26: - Paper uses trade-level data on six perps; we have BTCUSDT only and 1m-kline taker-buy volume (no aggTrades on disk, no trade-size roundness, no exact quarter-hour-open sub-minute window). The paper's imbalance may be finer than one minute and cross-sectional over six assets; a null here on BTC-only 1m proxy does not refute the paper, it only says the tradable BTC version on our data has no net edge.
27: - Data: 2022-01..2026 months on disk; funding only from 2025-09 (earlier trades fee+slippage only, as in C1/C2). At 4-12h holds funding is at most 1-2 records, negligible versus 12 bps cost.
28: - Multiple horizons/variants were tried; none passed, so no multiplicity adjustment needed for the null.
29:
30: ## Recommendation
31: No alert-only live sampling warranted for C3 (no gross edge at 4/8/12h on BTC proxy). If the operator wants forward confirmation anyway: alert-only log of opening-minute taker imbalance with 4h/8h/12h forward returns, and only after real aggTrades data is available for a faithful replication. Never a Tom filter (layer stays separate).
```

## E23

### MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md

SHA-256: `9341d45abeb2ad9a6beb8bcb6ff17ea1abeff76b24b9210bb238b6829e6725b8`

```text
1: # T087 failed first break: base rates, BTCUSDT 1m 2022-01-01 .. 2026-10-07
2:
3: Event: first touch of the previous UTC day high (side high) / low (side low) before 14:00 UTC, close back through the level within 60 min. Entry at that close, stop = spike extreme, target = Asia or EU session extreme on the other side, time exit 14:00 UTC (US-open placeholder). Net = minus 2 x taker 0.05%. Same-bar target+stop counts as stop. All clocks/thresholds NO-SOURCE. Verdict: n >= 300 and t >= 2.0.
4:
5: Events found: high side 466, low side 447 (days with a failed first break).
6:
7: - asia_target|touch_asia|high: n=345 target 27% / stop 67% / neither 6%, net -0.044% t -1.36 win 30% -> no edge
8: - asia_target|touch_asia|low: n=301 target 34% / stop 60% / neither 6%, net -0.025% t -0.66 win 36% -> no edge
9: - asia_target|touch_asia|both: n=646 target 30% / stop 64% / neither 6%, net -0.035% t -1.43 win 33% -> no edge
10: - asia_target|touch_eu|high: n=121 target 13% / stop 57% / neither 30%, net 0.037% t 0.61 win 33% -> insufficient n
11: - asia_target|touch_eu|low: n=144 target 5% / stop 63% / neither 32%, net -0.101% t -1.95 win 25% -> insufficient n
12: - asia_target|touch_eu|both: n=265 target 9% / stop 60% / neither 31%, net -0.038% t -0.96 win 29% -> insufficient n
13: - asia_target|touch_all|high: n=466 target 23% / stop 65% / neither 12%, net -0.023% t -0.80 win 30% -> no edge
14: - asia_target|touch_all|low: n=445 target 25% / stop 61% / neither 14%, net -0.049% t -1.64 win 32% -> no edge
15: - asia_target|touch_all|both: n=911 target 24% / stop 63% / neither 13%, net -0.036% t -1.72 win 31% -> no edge
16: - eu_target|touch_asia|high: n=2 target 100% / stop 0% / neither 0%, net -0.093% t -71.80 win 0% -> insufficient n
17: - eu_target|touch_asia|low: n=2 target 100% / stop 0% / neither 0%, net -0.080% t -6.28 win 0% -> insufficient n
18: - eu_target|touch_asia|both: n=4 target 100% / stop 0% / neither 0%, net -0.087% t -13.49 win 0% -> insufficient n
19: - eu_target|touch_eu|high: n=121 target 24% / stop 54% / neither 22%, net 0.028% t 0.56 win 36% -> insufficient n
20: - eu_target|touch_eu|low: n=144 target 14% / stop 62% / neither 24%, net -0.112% t -2.28 win 26% -> insufficient n
21: - eu_target|touch_eu|both: n=265 target 18% / stop 58% / neither 23%, net -0.048% t -1.35 win 31% -> insufficient n
22: - eu_target|touch_all|high: n=123 target 25% / stop 53% / neither 22%, net 0.026% t 0.53 win 36% -> insufficient n
23: - eu_target|touch_all|low: n=146 target 15% / stop 61% / neither 24%, net -0.112% t -2.31 win 25% -> insufficient n
24: - eu_target|touch_all|both: n=269 target 20% / stop 57% / neither 23%, net -0.049% t -1.39 win 30% -> insufficient n
25:
26: ## By year (both sides, touch session all)
27:
28: - asia_target 2022: n=188 target 26% / stop 59% / neither 15%, net 0.001% t 0.02 win 35% -> insufficient n
29: - asia_target 2023: n=164 target 27% / stop 52% / neither 21%, net 0.014% t 0.32 win 41% -> insufficient n
30: - asia_target 2024: n=193 target 22% / stop 68% / neither 10%, net -0.027% t -0.61 win 28% -> insufficient n
31: - asia_target 2025: n=212 target 26% / stop 65% / neither 9%, net -0.077% t -2.45 win 28% -> insufficient n
32: - asia_target 2026: n=154 target 18% / stop 71% / neither 12%, net -0.087% t -1.93 win 25% -> insufficient n
33: - eu_target 2022: n=58 target 19% / stop 53% / neither 28%, net -0.002% t -0.02 win 38% -> insufficient n
34: - eu_target 2023: n=48 target 23% / stop 46% / neither 31%, net 0.015% t 0.20 win 44% -> insufficient n
35: - eu_target 2024: n=54 target 15% / stop 63% / neither 22%, net -0.061% t -0.86 win 24% -> insufficient n
36: - eu_target 2025: n=63 target 19% / stop 63% / neither 17%, net -0.123% t -2.77 win 22% -> insufficient n
37: - eu_target 2026: n=46 target 24% / stop 59% / neither 17%, net -0.058% t -0.80 win 24% -> insufficient n
38:
39: ## Reading (T087 session, 2026-10-09)
40: - The 1m-only data answers Jis's question as a base rate: after a failed first break of the prior-day high, price retakes the local (spike) high before the Asia low in 57-67% of events and reaches the Asia low first in 24% (EU low first in 20%); the rest do neither before 14:00 UTC. Mirror (prior-day low) is similar.
41: - The "retake" share is geometric: the stop sits a few ticks above the entry, the targets are far below it. It is a base rate, not an edge. The short entered at the fail close and held to the Asia/EU low, net of taker x2, is negative in every cell with n >= 300 (no edge); EU-target cells have n < 300 (insufficient n).
42: - 2025 and 2026 are the weakest years (net -0.08% to -0.12%); 2022-2023 are flat. No session-stratified edge to carry forward.
43: - All session clocks, the 60 min fail window and the 14:00 UTC US open are NO-SOURCE placeholders; the 2026-10-09 day in the item is one event, not evidence.
```

## E24

### MyTradingSys/backtest/layers/tick/build_tiers.py

SHA-256: `85b704c8f8242f5f93b1dde551626b070ceb5b48fe1a7def8908484bedbc3544`

```text
1: """
2: MyTradingSys/backtest/layers/tick/build_tiers.py - T040 Q6: compute the tier table (tiers.json) per the tick layer spec.
3:
4: Offline tool; does not touch execution/ or the live runner. Sources:
5:   * price/net_delta/cvd_change/volume tiers, 1/2/3/5/10/15m: ALL-TIME 1m klines (2022-01..now). net_delta = 2*tbv - v is
6:     EXACT aggressor delta (taker-buy volume is the aggressor sum), so it is identical to the aggTrades 1m delta; this is
7:     cross-checked bar by bar against the aggTrades order-flow bars (F:\\MTS\\data\\orderflow_1m) in tiers_meta.json.
8:   * oi_delta tiers 5/10/15m from the 5m OI metrics (Dumps/backtest/raw/metrics, 2025-09..now).
9:   * tiers_aggtrades_window.json: same table built only from the aggTrades window (shows the window is not all-time).
10: Output shape = tick_flagger.replay tiers_table: {tf: {indicator: {"high": [...], "low": [...]}}} (no metadata keys;
11: metadata goes in tiers_meta.json). Flags are CONTEXT ONLY (never gate Tom).
12: """
13: import json
14: import sys
15: from datetime import datetime, timezone
16: from pathlib import Path
17:
18: REPO = Path(__file__).resolve().parents[4]
19: sys.path.insert(0, str(REPO))
20:
21: from MyTradingSys.backtest.bt.bt_data import load_klines, load_metrics
22: from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days
23: from MyTradingSys.backtest.layers.tick import tick_extremes as TE
24: from MyTradingSys.backtest.layers.tick import tick_flagger as TF
25: from MyTradingSys.backtest.layers.tick import tick_oi_extremes as TO
26:
27: HERE = Path(__file__).resolve().parent
28: OF_DIR = r"F:\MTS\data\orderflow_1m"
29: INDICATORS = ("net_delta", "cvd_change", "volume", "price_change_pct")
30:
31:
32: def klines_all():
33:     a = load_klines(REPO / "Dumps" / "backtest" / "raw_1m_2022")
34:     b = load_klines(REPO / "Dumps" / "backtest" / "raw")
35:     last = a[-1]["t"] if a else 0
36:     a += [x for x in b if x["t"] > last]
37:     a.sort(key=lambda x: x["t"])
38:     return a
39:
40:
41: def of_as_klines(days):
42:     return [{"t": d["t"], "o": d["o"], "h": d["h"], "l": d["l"], "c": d["c"], "v": d["buy_vol"] + d["sell_vol"],
43:              "tbv": d["buy_vol"]} for d in days]
44:
45:
46: def flag_rate(bars_1m, table, tfs=(1, 2, 3, 5, 10, 15)):
47:     """Replay the flagger over bars_1m (1m klines-shaped) -> flags per day by (tf, indicator, side, tier)."""
48:     hist = []
49:     for tf in tfs:
50:         for b in TE.resample(bars_1m, tf):
51:             for ind in INDICATORS:
52:                 hist.append({"t": b["t"], "tf": str(tf), "indicator": ind, "value": b[ind]})
53:     hist.sort(key=lambda x: x["t"])
54:     flags = TF.replay(hist, table)
55:     n_days = (bars_1m[-1]["t"] - bars_1m[0]["t"]) / 86400000
56:     by = {}
57:     for f in flags:
58:         k = f"{f['tf']}m {f['indicator']} {f['side']} T{f['tier']}"
59:         by[k] = by.get(k, 0) + 1
60:     return {"days": round(n_days, 1), "flags": len(flags), "per_day": round(len(flags) / n_days, 2), "by": by}
61:
62:
63: def main():
64:     kl = klines_all()
65:     print("klines", len(kl), kl[0]["t"], kl[-1]["t"], flush=True)
66:     table = TE.build_tier_table(kl, timeframes=[1, 2, 3, 5, 10, 15], indicators=list(INDICATORS), top_n=20)
67:     oi = TO.build_oi_tier_table(load_metrics(REPO / "Dumps" / "backtest" / "raw"), timeframes=[5, 10, 15], top_n=20)
68:     for tf, t in oi.items():
69:         table.setdefault(tf, {})["oi_delta"] = t
70:
71:     days = load_days(OF_DIR)
72:     of_bars = of_as_klines([d for d in days if d["thr_days"] >= 30])
73:     kl_by_t = {b["t"]: b for b in kl}
74:     n_cmp = n_missing = 0
75:     max_diff = 0.0
76:     for b in of_bars:
77:         k = kl_by_t.get(b["t"])
78:         if k is None:
79:             n_missing += 1
80:             continue
81:         n_cmp += 1
82:         max_diff = max(max_diff, abs((2 * b["tbv"] - b["v"]) - (2 * k["tbv"] - k["v"])))
83:     window_table = TE.build_tier_table(of_bars, timeframes=[1, 2, 3, 5, 10, 15], indicators=list(INDICATORS), top_n=20)
84:
85:     (HERE / "tiers.json").write_text(json.dumps(table, indent=1), encoding="utf-8", newline="\n")
86:     (HERE / "tiers_aggtrades_window.json").write_text(json.dumps(window_table, indent=1), encoding="utf-8", newline="\n")
87:     meta = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
88:             "kline_bars": len(kl), "kline_first": kl[0]["t"], "kline_last": kl[-1]["t"],
89:             "aggtrades_bars": len(of_bars), "aggtrades_first": of_bars[0]["t"], "aggtrades_last": of_bars[-1]["t"],
90:             "delta_crosscheck": {"bars_compared": n_cmp, "missing_in_klines": n_missing,
91:                                  "max_abs_delta_diff_btc": max_diff},
92:             "flag_rate_alltime_tiers_on_aggtrades_window": flag_rate(of_bars, table),
93:             "top_n": 20, "gap_factor": 1.5}
94:     (HERE / "tiers_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8", newline="\n")
95:     print(json.dumps(meta, indent=1)[:3000])
96:
97:
98: if __name__ == "__main__":
99:     main()
```

### MyTradingSys/backtest/layers/tick/tiers_meta.json

SHA-256: `65e1427c0c07e6477142ceb22e50f41f485c2056fa77df4b3468b6ccf826dc55`

```text
1: {
2:  "built_utc": "2026-09-29T21:09:49+00:00",
3:  "kline_bars": 2491200,
4:  "kline_first": 1640995200000,
5:  "kline_last": 1790467140000,
6:  "aggtrades_bars": 129600,
7:  "aggtrades_first": 1782864000000,
8:  "aggtrades_last": 1790639940000,
9:  "delta_crosscheck": {
10:   "bars_compared": 126720,
11:   "missing_in_klines": 2880,
12:   "max_abs_delta_diff_btc": 68.25000000000006
13:  },
14:  "flag_rate_alltime_tiers_on_aggtrades_window": {
15:   "days": 90.0,
16:   "flags": 10,
17:   "per_day": 0.11,
18:   "by": {
19:    "15m volume low T1": 3,
20:    "10m net_delta high T6": 1,
21:    "10m cvd_change high T6": 1,
22:    "2m net_delta high T7": 1,
23:    "2m cvd_change high T7": 1,
24:    "2m price_change_pct high T2": 1,
25:    "1m price_change_pct high T5": 1,
26:    "2m price_change_pct low T7": 1
27:   }
28:  },
29:  "top_n": 20,
30:  "gap_factor": 1.5
31: }
```

### MyTradingSys/backtest/layers/tick/tick_flagger.py

SHA-256: `0422b7259a506a807413b6f4564924309c219bca66de2fa5f79557a3314761d1`

```text
1: """
2: T040 tick-based delta layer, part 3 of 3.
3:
4: This module is the FLAG DECISION LOGIC ONLY for tick-sourced events.
5: It classifies live indicator readings against tier tables, decides whether
6: to flag them based on cooldown rules, and formats the flags as JSONL events.
7: """
8:
9: import json
10: import pathlib
11: from datetime import datetime
12:
13:
14: def tier_boundaries(occurrences: list) -> list:
15:     """
16:     Compute tier boundaries from a list of occurrences ordered most-to-least extreme.
17:
18:     Args:
19:         occurrences: List of dicts with "value" and "tier" keys, ordered most-to-least extreme.
20:
21:     Returns:
22:         List of (tier, boundary_value) tuples in tier-ascending order.
23:
24:     Raises:
25:         ValueError: If occurrences is empty.
26:     """
27:     if not occurrences:
28:         raise ValueError("Occurrences list cannot be empty.")
29:
30:     # Group by tier and find the least extreme value for each tier
31:     tier_groups = {}
32:     for item in occurrences:
33:         tier = item["tier"]
34:         value = item["value"]
35:         if tier not in tier_groups:
36:             tier_groups[tier] = []
37:         tier_groups[tier].append(value)
38:
39:     # Return (tier, boundary) pairs in ascending tier order
40:     result = []
41:     for tier in sorted(tier_groups.keys()):
42:         # The least extreme value is the last one in the ordered list for that tier
43:         boundary_value = tier_groups[tier][-1]
44:         result.append((tier, boundary_value))
45:
46:     return result
47:
48:
49: def classify_reading(value: float, high_bounds: list, low_bounds: list) -> dict:
50:     """
51:     Classify a reading against high and low boundaries.
52:
53:     Args:
54:         value: The indicator reading to classify.
55:         high_bounds: List of (tier, boundary) tuples for high side, ascending by tier.
56:         low_bounds: List of (tier, boundary) tuples for low side, ascending by tier.
57:
58:     Returns:
59:         Dict with "side" and "tier" keys indicating the classification.
60:     """
61:     # Check high side first
62:     for tier, boundary in high_bounds:
63:         if value >= boundary:
64:             return {"side": "high", "tier": tier}
65:
66:     # Check low side
67:     for tier, boundary in low_bounds:
68:         if value <= boundary:
69:             return {"side": "low", "tier": tier}
70:
71:     # No match on either side
72:     return {"side": None, "tier": None}
73:
74:
75: def should_emit(state: dict, key: tuple, tier: int, now_ms: int, cooldown_ms: int) -> bool:
76:     """
77:     Determine whether to emit a flag for the given reading.
78:
79:     Args:
80:         state: Dictionary mapping keys to last emission info.
81:         key: Tuple of (indicator, tf, side).
82:         tier: Tier number of the current reading.
83:         now_ms: Current timestamp in milliseconds.
84:         cooldown_ms: Cooldown period in milliseconds.
85:
86:     Returns:
87:         True if the flag should be emitted, False otherwise.
88:     """
89:     # If never emitted before
90:     if key not in state:
91:         return True
92:
93:     last_emit_info = state[key]
94:
95:     # Escalation always emits immediately
96:     if tier < last_emit_info["last_tier"]:
97:         return True
98:
99:     # Same or less extreme tier, but cooldown has passed
100:     if now_ms - last_emit_info["last_emit_ms"] >= cooldown_ms:
101:         return True
102:
103:     # Otherwise suppress emission
104:     return False
105:
106:
107: def make_flag(indicator: str, tf: str, side: str, tier: int, value: float, t_ms: int, extra: dict = None) -> dict:
108:     """
109:     Create a flag event dictionary.
110:
111:     Args:
112:         indicator: The indicator name.
113:         tf: Timeframe string.
114:         side: "high" or "low".
115:         tier: Tier number.
116:         value: Indicator reading.
117:         t_ms: Timestamp in milliseconds.
118:         extra: Optional additional fields to merge into the result.
119:
120:     Returns:
121:         Formatted flag event dictionary.
122:     """
123:     base = {
124:         "t": t_ms,
125:         "event": "tick_extreme",
126:         "source": "tick",
127:         "indicator": indicator,
128:         "tf": tf,
129:         "side": side,
130:         "tier": tier,
131:         "value": value
132:     }
133:
134:     if extra is None:
135:         return base
136:
137:     # Merge extra fields, with base keys taking precedence
138:     result = {**extra, **base}
139:     return result
140:
141:
142: def replay(historical: list, tiers_table: dict, cooldown_ms: int = 1800000) -> list:
143:     """
144:     Replay historical tick data through the flagger logic.
145:
146:     Args:
147:         historical: List of tick readings with keys "t", "tf", "indicator", "value".
148:         tiers_table: Tier table mapping tf -> indicator -> {"high": [...], "low": [...]}.
149:         cooldown_ms: Cooldown period in milliseconds.
150:
151:     Returns:
152:         List of flag events to emit.
153:     """
154:     # Precompute bounds cache
155:     bounds_cache = {}
156:     for tf, indicators in tiers_table.items():
157:         for indicator, sides in indicators.items():
158:             high = sides.get("high", [])
159:             low = sides.get("low", [])
160:             bounds_cache[(tf, indicator)] = (
161:                 tier_boundaries(high) if high else [],
162:                 tier_boundaries(low) if low else []
163:             )
164:
165:     # Initialize state and flags
166:     state = {}
167:     flags = []
168:
169:     for item in historical:
170:         tf = item["tf"]
171:         indicator = item["indicator"]
172:         value = item["value"]
173:         t_ms = item["t"]
174:
175:         if (tf, indicator) not in bounds_cache:
176:             continue  # Skip if no tier table for this (tf, indicator) pair
177:
178:         high_bounds, low_bounds = bounds_cache[(tf, indicator)]
179:         result = classify_reading(value, high_bounds, low_bounds)
180:
181:         # No flag needed if neutral reading
182:         if result["side"] is None:
183:             continue
184:
185:         # Compute key for state tracking
186:         key = (indicator, tf, result["side"])
187:
188:         # Check if we should emit
189:         if should_emit(state, key, result["tier"], t_ms, cooldown_ms):
190:             flag = make_flag(
191:                 indicator=indicator,
192:                 tf=tf,
193:                 side=result["side"],
194:                 tier=result["tier"],
195:                 value=value,
196:                 t_ms=t_ms
197:             )
198:             flags.append(flag)
199:
200:             # Update state
201:             state[key] = {
202:                 "last_tier": result["tier"],
203:                 "last_emit_ms": t_ms
204:             }
205:
206:     return flags
207:
```

## E25

### MyTradingSys/backtest/layers/timeframe/tf_resample.py

SHA-256: `cba6fd0c70e8a9d833c036d4985bb6a71826ff5ddc18b85df80f2d18d5cfe6db`

```text
1: """
2: MyTradingSys/backtest/layers/timeframe/tf_resample.py - D1 (RSI_TF_LAYER_DESIGN.md) timeframe resampling.
3: Closed bars only, gaps reported not filled, registry-driven.
4: """
5: import datetime
6: import math
7:
8:
9: def bucket_start(t_ms: int, tf: str, registry: dict) -> int:
10:     """
11:     Compute the start time (epoch ms) of the bucket containing t_ms for timeframe tf.
12:     Boundary regimes:
13:     - seconds: epoch-aligned (floor(t_sec / seconds) * seconds)
14:     - day_reset_seconds: counted from 00:00 UTC each day; the last bucket of the day is cut at midnight (T088 7h)
15:     - days: epoch-day-mod-N with configurable anchor date
16:     - week: Monday-anchored ISO week (epoch_day % 7 == 4 is Monday)
17:     - month: first day of calendar UTC month
18:     """
19:     entry = registry["timeframes"][tf]
20:     unit = entry["unit"]
21:
22:     if unit == "seconds":
23:         sec = t_ms // 1000
24:         seconds = entry["seconds"]
25:         return (sec // seconds) * seconds * 1000
26:
27:     elif unit == "day_reset_seconds":
28:         day_ms = (t_ms // 86400000) * 86400000
29:         step = entry["seconds"] * 1000
30:         return day_ms + ((t_ms - day_ms) // step) * step
31:
32:     elif unit == "days":
33:         anchor_date = entry["anchor_date"]
34:         y, m, d = map(int, anchor_date.split("-"))
35:         anchor_ms = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc).timestamp() * 1000
36:         anchor_day = anchor_ms // 86400000
37:
38:         epoch_day = t_ms // 86400000
39:         offset = epoch_day - anchor_day
40:         days = entry["days"]
41:         bucket_day = anchor_day + days * (offset // days)
42:
43:         return bucket_day * 86400000
44:
45:     elif unit == "week":
46:         epoch_day = t_ms // 86400000
47:         # Monday is where epoch_day % 7 == 4 (1970-01-01 is Thursday)
48:         bucket_day = epoch_day - ((epoch_day - 4) % 7)
49:         return bucket_day * 86400000
50:
51:     elif unit == "month":
52:         # Convert t_ms to UTC datetime, get first day of that month
53:         dt = datetime.datetime.fromtimestamp(t_ms/1000, tz=datetime.timezone.utc)
54:         y, m = dt.year, dt.month
55:         first_of_month = datetime.datetime(y, m, 1, tzinfo=datetime.timezone.utc)
56:         return int(first_of_month.timestamp() * 1000)
57:
58:     else:
59:         raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")
60:
61:
62: def bucket_end(t_ms: int, tf: str, registry: dict) -> int:
63:     """
64:     Compute the end time (epoch ms) of the bucket containing t_ms for timeframe tf.
65:     """
66:     entry = registry["timeframes"][tf]
67:     start = bucket_start(t_ms, tf, registry)
68:     unit = entry["unit"]
69:
70:     if unit == "seconds":
71:         return start + entry["seconds"] * 1000
72:     elif unit == "day_reset_seconds":
73:         return min(start + entry["seconds"] * 1000, (start // 86400000 + 1) * 86400000)
74:     elif unit == "days":
75:         return start + entry["days"] * 86400000
76:     elif unit == "week":
77:         return start + 7 * 86400000
78:     elif unit == "month":
79:         # Get first day of next month
80:         start_dt = datetime.datetime.fromtimestamp(start/1000, tz=datetime.timezone.utc)
81:         if start_dt.month == 12:
82:             next_month = datetime.datetime(start_dt.year + 1, 1, 1, tzinfo=datetime.timezone.utc)
83:         else:
84:             next_month = datetime.datetime(start_dt.year, start_dt.month + 1, 1, tzinfo=datetime.timezone.utc)
85:         return int(next_month.timestamp() * 1000)
86:     else:
87:         raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")
88:
89:
90: def resample(bars_1m: list, tf: str, registry: dict) -> list:
91:     """
92:     Resample 1m bars to the given timeframe tf.
93:     Returns closed bars only (no partial trailing buckets).
94:     Gap count is computed and reported but not filled.
95:     """
96:     if not bars_1m:
97:         return []
98:
99:     if tf not in registry["timeframes"]:
100:         raise ValueError(f"Timeframe '{tf}' not found in registry")
101:
102:     # Group bars by bucket
103:     buckets = {}
104:     for bar in bars_1m:
105:         start = bucket_start(bar["t"], tf, registry)
106:         if start not in buckets:
107:             buckets[start] = []
108:         buckets[start].append(bar)
109:
110:     # Compute results for each bucket
111:     result = []
112:     last_bar_close_ms = bars_1m[-1]["t"] + 60000
113:
114:     for bucket_start_ms, bars_in_bucket in sorted(buckets.items()):
115:         # Skip buckets that haven't closed yet
116:         if bucket_end(bucket_start_ms, tf, registry) > last_bar_close_ms:
117:             continue
118:
119:         # Compute OHLCV stats
120:         o = bars_in_bucket[0]["o"]
121:         c = bars_in_bucket[-1]["c"]
122:         h = max(bar["h"] for bar in bars_in_bucket)
123:         l = min(bar["l"] for bar in bars_in_bucket)
124:
125:         v = 0
126:         for bar in bars_in_bucket:
127:             v += bar.get("v", 0)
128:
129:         n_bars = len(bars_in_bucket)
130:
131:         # Compute expected minutes per bucket
132:         entry = registry["timeframes"][tf]
133:         unit = entry["unit"]
134:         if unit == "seconds":
135:             n_expected = entry["seconds"] // 60
136:         elif unit == "days":
137:             n_expected = entry["days"] * 1440
138:         elif unit == "week":
139:             n_expected = 10080
140:         elif unit in ("month", "day_reset_seconds"):
141:             n_expected = (bucket_end(bucket_start_ms, tf, registry) - bucket_start_ms) // 60000
142:         else:
143:             raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")
144:
145:         gap_count = max(0, n_expected - n_bars)
146:
147:         result.append({
148:             "t": bucket_start_ms,
149:             "o": o,
150:             "h": h,
151:             "l": l,
152:             "c": c,
153:             "v": v,
154:             "gap_count": gap_count,
155:             "n_bars": n_bars
156:         })
157:
158:     return result
```

### MyTradingSys/backtest/layers/timeframe/registry.json

SHA-256: `fe10d3c037f98b5f680d9478ccafe67fbccdd4f5baa15effc0c939ae270b05d7`

```text
1: {
2:   "registry_id": "tf_registry_default_2026-09-28",
3:   "source": "operator",
4:   "date": "2026-09-28",
5:   "note": "D1 timeframe registry: minute/hour frames align to Unix epoch; 2d/3d/5d use epoch-day index mod N from anchor_date; 1w opens Monday 00:00 UTC (epoch_day % 7 == 4); 1M is calendar month in UTC. day_reset_seconds frames restart at 00:00 UTC and end the day with a short bar. All times UTC. Adding a timeframe is a one-line addition below.",
6:   "timeframes": {
7:     "1m":  {"unit": "seconds", "seconds": 60},
8:     "2m":  {"unit": "seconds", "seconds": 120},
9:     "3m":  {"unit": "seconds", "seconds": 180},
10:     "4m":  {"unit": "seconds", "seconds": 240},
11:     "5m":  {"unit": "seconds", "seconds": 300},
12:     "10m": {"unit": "seconds", "seconds": 600},
13:     "15m": {"unit": "seconds", "seconds": 900},
14:     "30m": {"unit": "seconds", "seconds": 1800},
15:     "1h":  {"unit": "seconds", "seconds": 3600},
16:     "2h":  {"unit": "seconds", "seconds": 7200},
17:     "3h":  {"unit": "seconds", "seconds": 10800},
18:     "4h":  {"unit": "seconds", "seconds": 14400},
19:     "6h":  {"unit": "seconds", "seconds": 21600},
20:     "7h":  {"unit": "day_reset_seconds", "seconds": 25200, "flag": "NO-SOURCE anchor (T090 2026-10-09: no source for 00:00 UTC on crypto; the only sourced 7h anchor is 18:00 New York = 22:00/23:00 UTC, TradingView script 7Hour_Levels, a tool description not a test; use offsets in run_t090_anchor_probe.py): restarts at 00:00 UTC each day like TradingView intraday bars; 00/07/14/21 then a 3h stub"},
21:     "7h_epoch": {"unit": "seconds", "seconds": 25200, "flag": "NO-SOURCE anchor (T090: nobody cites epoch alignment for 7h): epoch-aligned, drifts 3h against the UTC day each day"},
22:     "8h":  {"unit": "seconds", "seconds": 28800},
23:     "12h": {"unit": "seconds", "seconds": 43200},
24:     "1d":  {"unit": "days", "days": 1, "anchor_date": "1970-01-01"},
25:     "2d":  {"unit": "days", "days": 2, "anchor_date": "1970-01-01"},
26:     "3d":  {"unit": "days", "days": 3, "anchor_date": "1970-01-01"},
27:     "5d":  {"unit": "days", "days": 5, "anchor_date": "1970-01-01"},
28:     "1w":  {"unit": "week"},
29:     "1M":  {"unit": "month"}
30:   }
31: }
```

## E26

### MyTradingSys/backtest/layers/consensus/hook.py

SHA-256: `1c1ff6faa67885b378d3afde966bd1fec0ea0b5acff0be5d235a03240e9bd7dc`

```text
1: """
2: Consensus hook: the one call the live alert runner makes after each poll (ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43).
3:
4: When EITHER core fires, write one consensus row (writer.append_row) built from what is already on disk:
5:   - Fabio core fired  = this poll emitted at least one alert with layer "fabio".
6:   - Tom core fired    = runtime_data/last_alert.json carries an alert number greater than the one stored in the hook's
7:                         own state file (the Tom card is written by the market loop, a different process).
8:   - rsi block         = rsi/observation.read_latest() (the newest rsi_events record per timeframe the runner persisted).
9:   - snapshot          = the newest runtime_data/snapshots/BTCUSDT_*.json; its file stem is the snapshot_id (nothing else
10:                         mints one, see consensus/README.md open item 1), current_price comes from the file.
11:
12: OBSERVATION ONLY: nothing here gates, vetoes or delays a core. Imports nothing from execution/ (the Tom card is
13: parsed with the same field names as execution/auto_trader.py CARD_FIELD / parse_tom_alert, copied, not imported:
14: test_layer_boundaries.py forbids the import). consensus_after_poll never raises: any error is swallowed and the
15: poll goes on. The only files written are the consensus daily jsonl and the hook's own tiny state file.
16: """
17: import json
18: import logging
19: import math
20: import re
21: from pathlib import Path
22:
23: from MyTradingSys.backtest.layers.consensus import writer
24: from MyTradingSys.backtest.layers.rsi import observation
25:
26: _LOG = logging.getLogger(__name__)
27:
28: REPO_ROOT = Path(__file__).resolve().parents[4]
29: TOM_ALERT = REPO_ROOT / "runtime_data" / "last_alert.json"
30: SNAP_DIR = REPO_ROOT / "runtime_data" / "snapshots"
31: ALERTS_DIR = REPO_ROOT / "MyTradingSys" / "runtime" / "alerts"
32: STATE_PATH = REPO_ROOT / "MyTradingSys" / "runtime" / "consensus_hook_state.json"
33:
34: CARD_FIELD = re.compile(r"^(VERDICT|TIME|PRICE|SETUP|ZONE|ENTRY|STOP|TARGET|RUNNER_TARGET|R:R):\s*(.*)$", re.M)
35: ALERT_NO = re.compile(r"#(\d+)")
36:
37:
38: def _num(v):
39:     try:
40:         f = float(v)
41:     except (TypeError, ValueError):
42:         return None
43:     return f if math.isfinite(f) else None
44:
45:
46: def _load_json(path):
47:     try:
48:         with open(path, encoding="utf-8") as fh:
49:             return json.load(fh)
50:     except (OSError, ValueError):
51:         return None
52:
53:
54: def read_tom(path=None):
55:     """The Tom card as {alert_no, verdict, setup, side, entry, stop, target, net_rr}, or None (no file, no ENTRY/STOP/
56:     TARGET, unreadable). Same field rules as auto_trader.parse_tom_alert."""
57:     alert = _load_json(path or TOM_ALERT)
58:     if not isinstance(alert, dict):
59:         return None
60:     fields = {k: v.strip() for k, v in CARD_FIELD.findall(alert.get("card_text") or "")}
61:     entry, stop, target = _num(fields.get("ENTRY")), _num(fields.get("STOP")), _num(fields.get("TARGET"))
62:     if entry is None or stop is None or target is None:
63:         return None
64:     m = ALERT_NO.search(alert.get("title") or "")
65:     setup = fields.get("SETUP", "")
66:     side = "long" if setup.endswith("_long") else "short" if setup.endswith("_short") else None
67:     rr = re.search(r"net\s+([0-9.]+)", fields.get("R:R", ""))
68:     return {"alert_no": int(m.group(1)) if m else None, "verdict": fields.get("VERDICT", ""), "setup": setup,
69:             "side": side, "entry": entry, "stop": stop, "target": target,
70:             "net_rr": float(rr.group(1)) if rr else None}
71:
72:
73: def fabio_from_alerts(alerts):
74:     """The newest layer-"fabio" alert of this poll as the consensus fabio block, or None. A collection-only (shadow)
75:     alert carries shadow_side instead of side; it is reported (this is an observation) with the same side key."""
76:     mine = [a for a in alerts or [] if isinstance(a, dict) and a.get("layer") == "fabio"]
77:     if not mine:
78:         return None
79:     a = max(mine, key=lambda x: x.get("t_close") or 0)
80:     return {"verdict": "%s:%s" % (a.get("sub"), a.get("event")), "model": a.get("model"),
81:             "side": a.get("side") or a.get("shadow_side"),
82:             "entry": a.get("entry_ref") if a.get("entry_ref") is not None else a.get("entry"),
83:             "stop": a.get("stop"), "target": a.get("target")}
84:
85:
86: def latest_snapshot(snap_dir=None):
87:     """{"snapshot_id": <file stem>, "current_price": float|None} for the newest BTCUSDT_*.json, or None."""
88:     try:
89:         files = sorted(Path(snap_dir or SNAP_DIR).glob("BTCUSDT_*.json"))
90:     except OSError:
91:         return None
92:     if not files:
93:         return None
94:     snap = _load_json(files[-1])
95:     price = _num(snap.get("current_price")) if isinstance(snap, dict) else None
96:     return {"snapshot_id": files[-1].stem, "current_price": price}
97:
98:
99: def _read_state(path):
100:     st = _load_json(path)
101:     return st if isinstance(st, dict) else {}
102:
103:
104: def _write_state(path, st):
105:     path = Path(path)
106:     path.parent.mkdir(parents=True, exist_ok=True)
107:     tmp = path.with_suffix(path.suffix + ".tmp")
108:     tmp.write_text(json.dumps(st) + "\n", encoding="utf-8", newline="\n")
109:     tmp.replace(path)
110:
111:
112: def consensus_after_poll(alerts, *, tom_path=None, snap_dir=None, alerts_dir=None, state_path=None,
113:                          base_dir=None, now=None):
114:     """Write one consensus row if a core fired this poll. Returns True when a row was written. Never raises."""
115:     try:
116:         state_path = Path(state_path or STATE_PATH)
117:         state = _read_state(state_path)
118:         tom = read_tom(tom_path)
119:         seen = state.get("tom_alert_no")
120:         tom_new = bool(tom) and tom["alert_no"] is not None and (seen is None or tom["alert_no"] > seen)
121:         fabio = fabio_from_alerts(alerts)
122:         if tom_new:
123:             state["tom_alert_no"] = tom["alert_no"]
124:             _write_state(state_path, state)
125:             if seen is None:
126:                 # First start: remember the current Tom alert, do not log a row for a card that predates the hook.
127:                 tom_new = False
128:         if not fabio and not tom_new:
129:             return False
130:         notes = "trigger=" + "+".join(t for t, on in (("tom", tom_new), ("fabio", bool(fabio))) if on)
131:         return writer.append_row(latest_snapshot(snap_dir), tom, fabio,
132:                                  observation.read_latest(alerts_dir=alerts_dir or ALERTS_DIR),
133:                                  notes=notes, base_dir=base_dir, now=now)
134:     except Exception as exc:  # noqa: BLE001 - the runner must never notice this hook
135:         try:
136:             _LOG.warning("consensus hook: %s: %s", type(exc).__name__, exc)
137:         except Exception:  # noqa: BLE001
138:             pass
139:         return False
```

### MyTradingSys/backtest/layers/consensus/README.md

SHA-256: `0a229f696fbb23bc06a463a238dc9b98669d0c76341b4ca41e829eb78825acd1`

```text
1: # consensus: one observation row per core alert
2:
3: Doctrine: `MyTradingSys/research/ARCHITECTURE_TWO_CORES_2026-10-01.md` :29-43 (consensus row), :76-83 (acceptance).
4: Consensus is an observation. It never gates, vetoes or delays a core, and nothing in this directory edits core state.
5: Every claim below cites file:line; "unknown" means the clone shows nothing.
6:
7: Files (staged as `*.new` until the parent promotes them): `writer.py`, `test_writer.py` (this directory),
8: `../rsi/observation.py`, `../rsi/test_observation.py`.
9:
10: ## Status: nothing calls it yet
11:
12: `append_row` is not wired into anything (no import of it exists in `live_runner_cli.py`, `live_runner_core.py`,
13: `auto_trader.py`). Hook points, owner and the snapshot id are open items (below).
14:
15: ## Invocation
16:
17: ```python
18: from MyTradingSys.backtest.layers.consensus.writer import append_row
19: from MyTradingSys.backtest.layers.rsi.observation import read_latest
20:
21: ok = append_row(snapshot, tom, fabio, read_latest())       # True / False; never raises, never blocks
22: # optional keyword-only: notes="free text", base_dir=<dir holding the daily files>, now=<UTC datetime>
23: ```
24:
25: | argument | what the caller passes | what is written |
26: |---|---|---|
27: | `snapshot` | the snapshot / math-object dict (read only) | `snapshot_id`, `price` (see OPEN 1 and the price rule) |
28: | `tom` | dict like `auto_trader.parse_tom_alert(alert)` (`execution/auto_trader.py:103-119`), or `None` | block with exactly `verdict, setup, side, entry, stop, target, net_rr`; `None` -> `"tom": null` |
29: | `fabio` | dict with `verdict, model, side, entry, stop, target`, or `None` | block with exactly those six keys; `None` -> `"fabio": null` |
30: | `rsi` | `observation.read_latest()` result, or `None` | the six keys `1m,3m,15m,1h,4h,1d` always (null if absent), then any extra key (`5m`) unchanged |
31:
32: Notes on the blocks:
33:
34: - `parse_tom_alert` actually returns `{alert_no, verdict, zone_tf, time, setup, side, entry, stop, target, net_rr}`
35:   (`auto_trader.py:116-119`; `zone_tf` is also there) or `{}` when the alert is unusable (`:110-111`). The row keeps only the
36:   seven documented keys (ARCHITECTURE:37); `alert_no`, `zone_tf`, `time` are dropped (put anything worth keeping in `notes`).
37:   Pass `None`, not `{}`, when there is no Tom alert: `{}` is written as a block of seven nulls, `None` as `null`.
38: - The fabio block comes from the Fabio v3 core being built in parallel under `MyTradingSys/backtest/layers/fabio/v3`, whose
39:   output fields are `verdict, model, side, entry, stop, target`: this is per the wave-2 contract, not yet verified (that
40:   directory does not exist in this clone when this was written).
41: - A non-mapping `tom`/`fabio`/`rsi`/`snapshot` is logged and treated as absent; it is not an error.
42:
43: ## File and row
44:
45: `<repo>/Dumps/consensus/consensus_<YYYYMMDD of the UTC date>.jsonl` (`Dumps/*` is gitignored, `.gitignore` "Dumps/*"; the directory
46: is created on first write). `base_dir` replaces `<repo>/Dumps/consensus`. UTC date and `utc_timestamp` come from one `now`
47: (default real UTC now; a naive datetime is taken as UTC, an aware one is converted). One row = one line, LF only, keys in
48: this order, `utc_timestamp` ISO-8601 UTC with milliseconds:
49:
50: ```json
51: {"snapshot_id": null, "utc_timestamp": "2026-10-01T19:30:15.123Z", "price": 67123.5,
52:  "tom": {"verdict": "SETUP_CONFIRMED", "setup": "pullback_long", "side": "long", "entry": 67000.0, "stop": 66800.0, "target": 67500.0, "net_rr": 2.4},
53:  "fabio": null,
54:  "rsi": {"1m": null, "3m": null, "15m": {"rsi": 51.0, "ma_sma": 49.0, "ma_ema": null, "support_or_reject": "support", "level": 40.0, "t_close": 1790000000000, "t_confirm": 1790000000000},
55:          "1h": null, "4h": null, "1d": null,
56:          "5m": {"rsi": 44.0, "ma_sma": 47.5, "ma_ema": null, "support_or_reject": "cross", "level": 40.0, "t_close": 1790000900000, "t_confirm": 1790000900000}},
57:  "notes": "snapshot_id absent in input"}
58: ```
59:
60: (The values are illustrative, hand-written for this document, not a real row.)
61:
62: ## The six-vs-seven timeframe note
63:
64: ARCHITECTURE:39 lists six rsi keys (`1m,3m,15m,1h,4h,1d`); `observation.read_latest()` returns seven (it also has `5m`, because
65: the live runner registers `rsi_events` at 5m, `live_runner_cli.py:152-158`). The writer always writes the six architecture keys
66: (null if absent) and carries `5m` (any key not among the six) through unchanged after them. Acceptance ARCHITECTURE:82-83
67: ("all six TF keys") is therefore met by every row regardless of what `read_latest` found.
68:
69: ## RSI block: which timeframes have a source today
70:
71: Investigation (2026-10-01): `rsi_ma_events` has NO live producer (it is imported only by `rsi/run_rsi_backtest.py:50`, offline,
72: and not registered in `alerts/live_runner_cli.py:137-194`); no persisted output of it exists. The only persisted RSI output is
73: the alert files `MyTradingSys/runtime/alerts/<tf>.jsonl` (`live_runner_cli.py:263-273`, `alert_emitter.append_alerts_jsonl`
74: `alert_emitter.py:69-92`). One file per timeframe holds every layer's alerts for that tf; `observation.read_latest()` scans a
75: file backward for the newest line with `layer == "rsi"`, `sub == "rsi_events"` and `tf ==` the file's tf.
76:
77: | tf | source today | file:line |
78: |---|---|---|
79: | 1m | none. The runner fetches 1m (default `--tfs "1h,15m,5m,1m"`, `live_runner_cli.py:247`) but registers no rsi layer at 1m; `1m.jsonl` carries `turn_of_candle` alerts only | registry `live_runner_cli.py:137-158` (rsi at 1h/15m/5m only), `:185` (turn_of_candle 1m) |
80: | 3m | none: not in default `--tfs`, no layer registered (`TF_SECONDS` in `auto_trader.py:48` has no 3m either) | `live_runner_cli.py:247` |
81: | 5m | `rsi_events` alert in `5m.jsonl` | registered `live_runner_cli.py:152-158` (tf at :155) |
82: | 15m | `rsi_events` alert in `15m.jsonl` | registered `live_runner_cli.py:145-151` (tf at :148) |
83: | 1h | `rsi_events` alert in `1h.jsonl` (the `malkan_bull`/`malkan_bear` 1h alerts, `:180-181`, are NOT used: different `sub` and event names) | registered `live_runner_cli.py:138-144` (tf at :141) |
84: | 4h | none: not in default `--tfs`, no layer registered | `live_runner_cli.py:247` |
85: | 1d | none: not in default `--tfs`, no layer registered | `live_runner_cli.py:247` |
86:
87: "Source today" means a source exists in the code; the file only exists once the runner has emitted an `rsi_events` alert at that
88: tf. This clone has no `MyTradingSys/runtime/alerts/` directory (gitignored, `.gitignore` "MyTradingSys/runtime/alerts/*.jsonl"), so
89: here every tf reads all-None; whether the live machine has the files is unknown. Nothing here computes an RSI or fetches klines
90: to fill a gap.
91:
92: Per-tf fields (all copied from the newest valid record, else None):
93:
94: | field | from | cite |
95: |---|---|---|
96: | `rsi` | `record["rsi"]`: RSI(14) on the latest closed bar when the alert was first seen | `alert_emitter.py:41`, `live_runner_core.py:137-138,149-150` |
97: | `ma_sma` | `record["rsi_ma"]`: SMA(14) of that RSI | `live_runner_core.py:139` `_rsi_ma(rs, "SMA", 14)`; the record does not name the MA type, the producer code does (if the producer changes, this mapping is silently wrong) |
98: | `ma_ema` | always None: no live code produces an EMA of the RSI | grep of `"EMA"` outside `rsi_ma.py`/tests: none; `run_rsi_backtest.py:259` uses `"SMA"` |
99: | `support_or_reject` | `record["event"]` verbatim: `support`, `rejection`, `failure` or `cross` (so not only support/reject) | `rsi_events.py:70,78,93` |
100: | `level` | `record["level_value"]` | `rsi_events.py:85,94`; the live adapter uses `RSI_LEVEL` `live_layers.py:142` |
101: | `t_close` (extra) | `record["t_close"]`: OPEN time (ms) of the event bar, despite the name | `alert_emitter.py:46-47`, `auto_trader.py:221` |
102: | `t_confirm` (extra, not requested) | `record["t_confirm"]`: open time of the latest closed bar when first seen = the bar `rsi`/`ma_sma` belong to | `live_runner_core.py:151` |
103:
104: Rules (tested): "latest" is the last valid matching line of the file; empty, non-UTF-8, non-JSON, non-object, other-layer,
105: other-sub and wrong-tf lines are skipped, so a half-written last line falls back to the previous valid rsi record and a file with
106: none gives all None; non-finite or wrongly typed numbers become None; only the tail is read (64 KiB chunks backward, at most
107: 16 MiB, then stop: a match older than that is not found); a missing, unreadable or non-file path gives all None and nothing is
108: created. The default directory is `<repo>/MyTradingSys/runtime/alerts` (`auto_trader.py:46`); the runner's own default is
109: cwd-relative (`live_runner_cli.py:249`), so a runner started from another cwd writes elsewhere (pass `alerts_dir=`).
110:
111: IMPORTANT staleness: the values are as of the last `rsi_events` alert on that tf (a rare event at one level), NOT the RSI at the
112: time of the consensus row. On 1h that can be many hours old. Compare `t_confirm` with the row's `utc_timestamp` before using a
113: block. A truly per-snapshot RSI per tf needs a producer that persists the RSI on every poll (not built; it would touch
114: `layers/alerts/`, which needs a SUPERVISOR_LOG ownership claim, CLAUDE.md). Related, not implemented: every alert of any layer
115: also carries `rsi`/`rsi_ma` for its own tf (`live_runner_core.py:149-150`), so the newest alert of any layer on a tf has a
116: fresher RSI, but it would mix fields from two different records; that is a decision for the parent/supervisor.
117:
118: ## OPEN items (nothing here is invented)
119:
120: 1. `snapshot_id`: there is no `snapshot_id` in `MyTradingSys/runtime/math_object_builder.py` (grep count 0) or anywhere else in the
121:    repo apart from the two 2026-10-01 design docs. Who mints it is unknown. The writer takes `snapshot.get("snapshot_id")` if
122:    present, else writes `null` and adds `"snapshot_id absent in input"` to `notes`. Rows can therefore not yet be keyed by
123:    snapshot_id (ARCHITECTURE:42); no id scheme is invented.
124: 2. `price`: `snapshot["current_price"]` (key of the raw snapshot, `math_object_builder.py:6,43,64,91`, and of the math object
125:    it returns, `:376`), else `snapshot.get("price")`, else null. A key present with value `None` counts as absent.
126:    `math_object_builder` itself substitutes `0.0` for a missing `current_price` (`:64,:91`); the writer does not.
127: 3. Hook points and owner: SCAFFOLD section 3 proposes Tom side at `auto_trader.py:507` and Fabio/RSI side at
128:    `live_runner_core.py:149` (`TWO_CORES_SCAFFOLD_2026-10-01.md:32`); which side owns the write is unknown. Both files are in
129:    areas that need a SUPERVISOR_LOG claim and staged `.new` edits. Boundary conflict found: `test_layer_boundaries.py:81-101`
130:    fails any `.py` under `execution/` that imports `MyTradingSys.backtest.layers...`, so `auto_trader.py` cannot import this
131:    writer from `layers/consensus/` without changing that rule or moving the writer (supervisor decision), and layers cannot
132:    import execution (`:43-79`).
133: 4. Row timing: ARCHITECTURE:31 says "at the moment an alert fires from either core". Two different processes would write the same
134:    daily file; the writer takes no lock (by design), relies on one `write` of one short line in append mode, and was not tested
135:    with concurrent writers.
136:
137: ## Guarantees (each has a test in `test_writer.py` / `test_observation.py`)
138:
139: - Append-only: mode `"a"`, `newline="\n"`, one write per row; never read back, rewritten or truncated; old bytes stay identical.
140: - Never raises, never blocks on IO or serialization errors: logs (`logging`, stderr by default, nothing on stdout) and returns
141:   `False`. Serialization happens before the file is opened (no partial line), `allow_nan=False` (every line is valid JSON).
142: - Arguments are not mutated; no network; no locks; stdlib only; no import from `execution/` (boundary test green).
143: - Writes only `<base_dir>/consensus_<date>.jsonl`; `observation.read_latest` writes nothing at all.
144: - Observation only: neither module is imported by, nor feeds, any core or gate.
145:
146: ## Acceptance (ARCHITECTURE:76-83)
147:
148: | acceptance | status |
149: |---|---|
150: | :78-79 two cores emit verdicts independently | not covered here (core behaviour, not this module) |
151: | :80 every alert writes one consensus row ("fire N alerts, count N rows") | the writer half is tested (N `append_row` calls -> N lines, each valid JSON); the "every alert" half cannot be satisfied until the hook points above exist (owner unknown) |
152: | :81 every trade row carries source tom or fabio | not covered here (ledger) |
153: | :82-83 consensus row carries all six TF keys | satisfied by the writer for every row (tested with `rsi=None`, `{}`, partial, full); the VALUES are mostly null until 3m/4h/1d (and 1m) have a source (table above) and are stale between rsi events |
154:
155: ## Run the tests
156:
157: `python -m unittest MyTradingSys.backtest.layers.consensus.test_writer MyTradingSys.backtest.layers.rsi.test_observation`
158: from the repo root (namespace packages, no `__init__.py`; `run_all_tests.py` Step 5b collects `MyTradingSys/backtest/layers/**/test_*.py`
159: as dotted modules). All tests write only under temp directories.
```

### MyTradingSys/backtest/layers/rsi/observation.py

SHA-256: `c716f4090e460ed9b17924f42c33a58fa1652942d92ff676a2e4ce2abb090ab3`

```text
1: """
2: RSI observation block: the latest RSI reading per timeframe, READ from what the live alert runner already persisted.
3:
4: READ-ONLY, NO NEW COMPUTATION: nothing here computes an RSI or an MA, fetches klines, writes a file, or imports any
5: execution code. It tails MyTradingSys/runtime/alerts/<tf>.jsonl (written by alerts/live_runner_cli.py:263-273 via
6: alert_emitter.append_alerts_jsonl) and copies fields that already exist in an alert record. A field or timeframe with
7: no source stays None. Consensus is an observation (research/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43): this block
8: never gates, vetoes or delays a core.
9:
10: WHERE THE DATA LIVES (investigated 2026-10-01):
11: - rsi_ma_events has NO live producer: it is imported only by rsi/run_rsi_backtest.py (offline). Nothing registers it in
12:   alerts/live_runner_cli.py:137-194 and no persisted output of it exists. So no rsi-vs-MA "ma_support"/"ma_rejection"
13:   event can be reported; support_or_reject below comes from rsi_events (the level-event detector) only.
14: - The live source is the alert record of layer "rsi", sub "rsi_events" (registered for 1h, 15m, 5m only:
15:   live_runner_cli.py:137-158; adapter alerts/live_layers.py:146-166). Every alert is built by alert_emitter.format_alert
16:   (alert_emitter.py:36-49): "rsi" and "rsi_ma" are the RSI(14) and its SMA(14) on the latest closed bar when the alert was
17:   first seen (live_runner_core.py:133-142,149-151), "event" and "level_value" are the rsi_events event (rsi_events.py:82-98),
18:   "t_close" is the event bar's OPEN time in ms (alert_emitter.py:46-47; auto_trader.py:221), "t_confirm" is the open time
19:   of the latest closed bar when first seen (live_runner_core.py:151).
20: - The <tf>.jsonl files hold every layer's alerts for that tf (live_runner_cli.py:263-273), so the newest line is often
21:   another layer's; this module scans backward for the newest rsi/rsi_events line.
22:
23: MAPPING (per tf, fields copied from the newest valid record; anything else is None):
24:     rsi                <- record["rsi"]            (RSI(14) at t_confirm's bar, not at "now")
25:     ma_sma             <- record["rsi_ma"]         (SMA(14): live_runner_core.py:139 `_rsi_ma(rs, "SMA", 14)`; the record
26:                                                     itself does not name the MA type, the producer code does)
27:     ma_ema             <- always None              (no EMA is produced by any live code)
28:     support_or_reject  <- record["event"]          (verbatim: support | rejection | failure | cross, rsi_events.py:70,78,93)
29:     level              <- record["level_value"]    (rsi_events.py:85,94)
30:     t_close            <- record["t_close"]        (extra key, for staleness checks)
31:     t_confirm          <- record["t_confirm"]      (extra key: the bar the rsi/ma_sma values belong to)
32:
33: RULES (tested in test_observation.py):
34: - "Latest" = the LAST valid matching line of the file (the runner appends in time order).
35: - A line is skipped (never raises) when it is empty, not valid UTF-8/JSON, not a JSON object, not layer "rsi" /
36:   sub "rsi_events", or when its "tf" differs from the file's tf. So a garbled or half-written last line falls back
37:   to the previous valid rsi_events record; if there is none, that tf is all None.
38: - Numeric fields must be finite numbers (bool, strings, NaN, inf -> None); "event" must be a string.
39: - Only the tail is read: the file is scanned backward in _CHUNK-byte chunks, at most max_scan_bytes bytes, stopping at
40:   the first match. A match older than max_scan_bytes is not found (that tf is all None).
41: - Missing file / unreadable / directory / bad alerts_dir -> that tf all None; nothing is created or written.
42: """
43:
44: import json
45: import math
46: import os
47: from contextlib import closing
48: from pathlib import Path
49:
50: TFS = ("1m", "3m", "5m", "15m", "1h", "4h", "1d")
51: SOURCE_LAYER = "rsi"
52: SOURCE_SUB = "rsi_events"
53:
54: # <repo>/MyTradingSys/backtest/layers/rsi/observation.py -> parents[3] is <repo>/MyTradingSys.
55: # Same directory as auto_trader.LAYER_ALERT_DIR (execution/auto_trader.py:46) and the runner's default
56: # (live_runner_cli.py:249, which is cwd-relative: a runner started from another cwd writes elsewhere).
57: DEFAULT_ALERTS_DIR = Path(__file__).resolve().parents[3] / "runtime" / "alerts"
58:
59: _CHUNK = 64 * 1024
60: DEFAULT_MAX_SCAN_BYTES = 16 * 1024 * 1024
61:
62:
63: def _empty():
64:     return {"rsi": None, "ma_sma": None, "ma_ema": None, "support_or_reject": None, "level": None,
65:             "t_close": None, "t_confirm": None}
66:
67:
68: def _num(v):
69:     """A finite real number (not bool) or None."""
70:     if isinstance(v, bool) or not isinstance(v, (int, float)):
71:         return None
72:     if isinstance(v, float) and not math.isfinite(v):
73:         return None
74:     return v
75:
76:
77: def _ms(v):
78:     """An epoch-ms integer (not bool; an integral float is accepted) or None."""
79:     v = _num(v)
80:     if v is None:
81:         return None
82:     if isinstance(v, float):
83:         return int(v) if v.is_integer() else None
84:     return v
85:
86:
87: def _map(rec):
88:     ev = rec.get("event")
89:     return {
90:         "rsi": _num(rec.get("rsi")),
91:         "ma_sma": _num(rec.get("rsi_ma")),
92:         "ma_ema": None,
93:         "support_or_reject": ev if isinstance(ev, str) else None,
94:         "level": _num(rec.get("level_value")),
95:         "t_close": _ms(rec.get("t_close")),
96:         "t_confirm": _ms(rec.get("t_confirm")),
97:     }
98:
99:
100: def _lines_backward(path, max_scan_bytes):
101:     """Yield the file's lines (bytes, no newline) newest first, reading _CHUNK bytes at a time, at most
102:     max_scan_bytes bytes in total. A line cut by the scan limit is dropped, never yielded half."""
103:     with open(path, "rb") as fh:
104:         fh.seek(0, os.SEEK_END)
105:         pos = fh.tell()
106:         scanned = 0
107:         carry = b""
108:         while pos > 0 and scanned < max_scan_bytes:
109:             step = min(_CHUNK, pos, max_scan_bytes - scanned)
110:             pos -= step
111:             scanned += step
112:             fh.seek(pos)
113:             parts = (fh.read(step) + carry).split(b"\n")
114:             carry = parts[0]   # may be the tail of a line that starts in an earlier chunk
115:             for line in reversed(parts[1:]):
116:                 yield line
117:         if pos == 0:
118:             yield carry        # the very first line of the file, complete
119:
120:
121: def _latest_for_tf(path, tf, max_scan_bytes):
122:     with closing(_lines_backward(path, max_scan_bytes)) as lines:
123:         for raw in lines:
124:             raw = raw.strip()
125:             if not raw:
126:                 continue
127:             try:
128:                 rec = json.loads(raw.decode("utf-8"))
129:             except Exception:   # bad UTF-8, bad JSON, absurd nesting / huge ints: a garbled line is skipped
130:                 continue
131:             if (isinstance(rec, dict) and rec.get("layer") == SOURCE_LAYER and rec.get("sub") == SOURCE_SUB
132:                     and rec.get("tf") == tf):
133:                 return _map(rec)
134:     return None
135:
136:
137: def read_latest(*, alerts_dir=None, max_scan_bytes=DEFAULT_MAX_SCAN_BYTES):
138:     """{tf: {"rsi","ma_sma","ma_ema","support_or_reject","level","t_close","t_confirm"}} for the seven TFs in TFS.
139:
140:     Read-only; never raises; every field/tf without a source is None (see the module docstring for the mapping and
141:     which tfs have a source today: only 1h, 15m, 5m can, and only once the runner has emitted an rsi_events alert there).
142:     alerts_dir: directory holding <tf>.jsonl (default MyTradingSys/runtime/alerts).
143:     """
144:     out = {tf: _empty() for tf in TFS}
145:     try:
146:         base = Path(alerts_dir) if alerts_dir is not None else DEFAULT_ALERTS_DIR
147:     except Exception:
148:         return out
149:     for tf in TFS:
150:         try:
151:             rec = _latest_for_tf(base / (tf + ".jsonl"), tf, max_scan_bytes)
152:         except Exception:   # missing file, a directory, permissions, anything else: that tf stays all None
153:             rec = None
154:         if rec is not None:
155:             out[tf] = rec
156:     return out
```

## E27

### MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md

SHA-256: `5ab15134ee26e7834acfb495d6a6fa30acd11aabe5df4680d5b8ec8c94316d8c`

```text
1: # V3 VALIDATION RESULTS (2024-07-01 .. 2025-06-30, run once; HOLDOUT never loaded)
2:
3: Frozen in PRE_REG_ADDENDUM_A_2026-10-09.md (commit 6e6227b). Features computed on DEV+VALIDATION concatenated for warm-up; events and baselines restricted to bars opening on/after 2024-07-01; forward windows end by 2025-06-30.
4:
5: ## Candidate 1: R40D_N, 4h, h=6, reversal (long after RSI(14) crosses down through 40 on RVadj < 1.5)
6:
7: | n events | gross bp | net bp [95% CI] | win | excess bp vs all bars | one-sided p | min n (registered) |
8: |---|---|---|---|---|---|---|
9: | 50 | +14 | -2 [-68, +64] | 52% | -1 | 0.523 | 100 |
10:
11: Verdict: **INSUFFICIENT-N (n < 100: registered rule cannot be met; numbers shown for information, candidate stays an unvalidated hypothesis)**
12:
13: DEV had 189 such events in 4.5 years (about 42 per year); VALIDATION has 50 in 1 year.
14:
15: ## Candidate 2: TH1 replication - SP3 spike continuation return (h=18), session C (16-24 UTC) minus session A (00-08 UTC)
16:
17: | nC | nA | mean C bp | mean A bp | diff bp | 95% CI bp | p |
18: |---|---|---|---|---|---|---|
19: | 31 | 36 | -26 | -152 | +126 | [-90, +377] | 0.310 |
20:
21: DEV: diff -178 bp, CI [-344, -20] (C mean -40, A mean +138). Replicated only if the CI excludes 0 with diff < 0: **NOT REPLICATED**
22:
```

### MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md

SHA-256: `9beb7731761ea4149c5e2c1227d3e582453713484c167a98b8e38f1e04afc1be`

```text
1: # P1 RESULTS - classical candle patterns on DEV data (generated by run_p1.py, run P1-2026-10-07)
2:
3: Definitions frozen in PRE_REG_CANDLE_PILOT.md section 4. Net = sign*fwd - 14 bps - sign*realised funding. Entry open(i+1), exit open(i+1+h).
4: Reality-Check p = single-step max-T over the 54 (18 patterns x 3 h) family per timeframe, one-sided in the textbook direction; q = two-sided BH over the 54 trials (INSUFFICIENT-N enters with p=1). CI = circular block bootstrap of mean net per trade.
5: Bars: 1d n=1643 (gaps 0); 1h n=21888 (gaps 0, dropped partial hours 0). Common range i<=n-7 for all h. Triage = section 5 (N, net>0 with CI lo>0, RC p<0.10, textbook direction).
6:
7: ## 1d directional patterns (54 trials; 18 INSUFFICIENT-N)
8: | pattern | h | n | win | gross bps | net bps [CI] | excess bps | t | RC p | q(BH) | triage |
9: |---|---|---|---|---|---|---|---|---|---|---|
10: | bull_engulf | 1 | 164 | 40% | -7.4 | -26.2 [-70, 21] | -20.5 | -0.91 | 1.000 | 1.000 | FAIL |
11: | bull_engulf | 3 | 164 | 43% | -17.9 | -47.1 [-134, 43] | -57.2 | -1.39 | 1.000 | 1.000 | FAIL |
12: | bull_engulf | 5 | 164 | 45% | 61.0 | 22.4 [-88, 133] | -4.2 | -0.09 | 1.000 | 1.000 | FAIL |
13: | bear_engulf | 1 | 140 | 40% | -59.0 | -70.5 [-125, -22] | -45.9 | -1.69 | 1.000 | 0.993 | FAIL |
14: | bear_engulf | 3 | 140 | 39% | -90.8 | -95.8 [-177, -19] | -51.4 | -1.29 | 1.000 | 1.000 | FAIL |
15: | bear_engulf | 5 | 140 | 42% | -78.8 | -77.0 [-197, 78] | -13.7 | -0.24 | 1.000 | 1.000 | FAIL |
16: | bull_harami | 1 | 70 | 47% | 10.4 | -5.9 [-84, 80] | -2.7 | -0.07 | 1.000 | 1.000 | FAIL |
17: | bull_harami | 3 | 70 | 49% | 87.8 | 65.9 [-47, 184] | 48.4 | 0.83 | 0.998 | 1.000 | FAIL |
18: | bull_harami | 5 | 70 | 54% | 130.6 | 102.6 [-41, 254] | 65.5 | 0.90 | 0.994 | 1.000 | FAIL |
19: | bear_harami | 1 | 65 | 43% | -42.6 | -51.9 [-145, 40] | -29.5 | -0.63 | 1.000 | 1.000 | FAIL |
20: | bear_harami | 3 | 65 | 54% | -3.8 | -3.2 [-142, 126] | 35.6 | 0.52 | 1.000 | 1.000 | FAIL |
21: | bear_harami | 5 | 65 | 43% | -148.8 | -139.1 [-333, 38] | -83.7 | -0.88 | 1.000 | 1.000 | FAIL |
22: | hammer | 1 | 17 | 47% | 4.7 | -10.6 - | - | - | - | - | INSUFFICIENT-N |
23: | hammer | 3 | 17 | 65% | 174.3 | 156.1 - | - | - | - | - | INSUFFICIENT-N |
24: | hammer | 5 | 17 | 71% | 333.3 | 311.3 - | - | - | - | - | INSUFFICIENT-N |
25: | hanging_man | 1 | 15 | 53% | 9.0 | 2.7 - | - | - | - | - | INSUFFICIENT-N |
26: | hanging_man | 3 | 15 | 47% | -6.6 | -0.2 - | - | - | - | - | INSUFFICIENT-N |
27: | hanging_man | 5 | 15 | 53% | 35.6 | 54.1 - | - | - | - | - | INSUFFICIENT-N |
28: | inv_hammer | 1 | 5 | 60% | -29.4 | -41.3 - | - | - | - | - | INSUFFICIENT-N |
29: | inv_hammer | 3 | 5 | 60% | 88.1 | 75.6 - | - | - | - | - | INSUFFICIENT-N |
30: | inv_hammer | 5 | 5 | 80% | 480.0 | 463.9 - | - | - | - | - | INSUFFICIENT-N |
31: | shooting_star | 1 | 11 | 36% | -37.9 | -46.1 - | - | - | - | - | INSUFFICIENT-N |
32: | shooting_star | 3 | 11 | 9% | -483.6 | -479.0 - | - | - | - | - | INSUFFICIENT-N |
33: | shooting_star | 5 | 11 | 27% | -669.0 | -651.3 - | - | - | - | - | INSUFFICIENT-N |
34: | morning_star | 1 | 44 | 48% | 10.0 | -7.9 [-90, 82] | -3.2 | -0.07 | 1.000 | 1.000 | FAIL |
35: | morning_star | 3 | 44 | 55% | 10.2 | -14.6 [-178, 142] | -29.2 | -0.38 | 1.000 | 1.000 | FAIL |
36: | morning_star | 5 | 44 | 50% | -4.1 | -35.4 [-280, 167] | -69.3 | -0.62 | 1.000 | 1.000 | FAIL |
37: | evening_star | 1 | 44 | 50% | -49.4 | -60.4 [-182, 63] | -36.2 | -0.62 | 1.000 | 1.000 | FAIL |
38: | evening_star | 3 | 44 | 43% | -27.0 | -31.9 [-194, 156] | 12.3 | 0.15 | 1.000 | 1.000 | FAIL |
39: | evening_star | 5 | 44 | 55% | 112.7 | 114.9 [-176, 555] | 177.9 | 1.06 | 0.976 | 1.000 | FAIL |
40: | three_white_soldiers | 1 | 105 | 51% | 43.0 | 22.9 [-35, 80] | 29.9 | 1.08 | 0.974 | 1.000 | FAIL |
41: | three_white_soldiers | 3 | 105 | 61% | 202.2 | 168.8 [34, 311] | 162.8 | 2.35 | 0.264 | 0.993 | FAIL |
42: | three_white_soldiers | 5 | 105 | 54% | 269.7 | 222.4 [19, 452] | 204.5 | 2.02 | 0.464 | 0.993 | FAIL |
43: | three_black_crows | 1 | 81 | 43% | -11.0 | -23.1 [-92, 41] | 2.2 | 0.07 | 1.000 | 1.000 | FAIL |
44: | three_black_crows | 3 | 81 | 43% | 84.3 | 74.3 [-122, 279] | 123.6 | 1.27 | 0.933 | 1.000 | FAIL |
45: | three_black_crows | 5 | 81 | 44% | 48.1 | 41.7 [-167, 275] | 113.2 | 1.08 | 0.975 | 1.000 | FAIL |
46: | piercing | 1 | 48 | 35% | -43.3 | -60.5 [-126, 1] | -56.4 | -1.73 | 1.000 | 0.993 | FAIL |
47: | piercing | 3 | 48 | 56% | -2.6 | -26.9 [-183, 136] | -42.0 | -0.54 | 1.000 | 1.000 | FAIL |
48: | piercing | 5 | 48 | 42% | 1.2 | -29.3 [-195, 140] | -63.9 | -0.77 | 1.000 | 1.000 | FAIL |
49: | dark_cloud | 1 | 65 | 45% | 9.2 | -0.5 [-73, 75] | 22.4 | 0.59 | 1.000 | 1.000 | FAIL |
50: | dark_cloud | 3 | 65 | 58% | -13.3 | -15.8 [-133, 92] | 26.0 | 0.45 | 1.000 | 1.000 | FAIL |
51: | dark_cloud | 5 | 65 | 45% | -62.6 | -56.9 [-196, 76] | 2.6 | 0.04 | 1.000 | 1.000 | FAIL |
52: | hikkake_bull | 1 | 29 | 48% | 66.1 | 47.9 [-49, 153] | 52.9 | 1.03 | 0.983 | 1.000 | FAIL |
53: | hikkake_bull | 3 | 29 | 45% | 66.6 | 39.2 [-157, 233] | 27.2 | 0.28 | 1.000 | 1.000 | FAIL |
54: | hikkake_bull | 5 | 29 | 41% | 46.6 | 7.9 [-256, 293] | -18.6 | -0.14 | 1.000 | 1.000 | FAIL |
55: | hikkake_bear | 1 | 31 | 32% | -90.1 | -101.7 [-234, 27] | -77.0 | -1.14 | 1.000 | 1.000 | FAIL |
56: | hikkake_bear | 3 | 31 | 26% | -244.8 | -251.3 [-478, -39] | -205.4 | -1.81 | 1.000 | 0.993 | FAIL |
57: | hikkake_bear | 5 | 31 | 29% | -167.8 | -169.6 [-445, 155] | -102.6 | -0.71 | 1.000 | 1.000 | FAIL |
58: | marubozu_up | 1 | 6 | 0% | -149.3 | -172.9 - | - | - | - | - | INSUFFICIENT-N |
59: | marubozu_up | 3 | 6 | 50% | -84.4 | -124.1 - | - | - | - | - | INSUFFICIENT-N |
60: | marubozu_up | 5 | 6 | 50% | -68.1 | -119.5 - | - | - | - | - | INSUFFICIENT-N |
61: | marubozu_dn | 1 | 5 | 40% | -54.2 | -66.2 - | - | - | - | - | INSUFFICIENT-N |
62: | marubozu_dn | 3 | 5 | 60% | -48.1 | -57.6 - | - | - | - | - | INSUFFICIENT-N |
63: | marubozu_dn | 5 | 5 | 40% | 567.7 | 552.7 - | - | - | - | - | INSUFFICIENT-N |
64:
65: ## 1d volatility-state family (6 trials; one-sided: event mean > all-bar mean)
66: | state | metric | n | event mean | all-bar mean | diff | t | RC p | q(BH) |
67: |---|---|---|---|---|---|---|---|---|
68: | doji | range_ratio | 194 | 0.947 | 1.047 | -0.101 | -2.59 | 1.000 | 0.028 |
69: | doji | abs_return | 194 | 0.0228 | 0.0232 | -0.0004 | -0.25 | 0.946 | 0.797 |
70: | inside_bar | range_ratio | 365 | 0.963 | 1.047 | -0.084 | -2.61 | 1.000 | 0.028 |
71: | inside_bar | abs_return | 365 | 0.0209 | 0.0232 | -0.0023 | -1.87 | 0.999 | 0.097 |
72: | nr7 | range_ratio | 239 | 0.875 | 1.047 | -0.173 | -5.13 | 1.000 | 0.006 |
73: | nr7 | abs_return | 239 | 0.0211 | 0.0232 | -0.0021 | -1.52 | 0.999 | 0.135 |
74:
75: ## 1h directional patterns (54 trials; 6 INSUFFICIENT-N)
76: | pattern | h | n | win | gross bps | net bps [CI] | excess bps | t | RC p | q(BH) | triage |
77: |---|---|---|---|---|---|---|---|---|---|---|
78: | bull_engulf | 1 | 2053 | 29% | 1.3 | -12.8 [-15, -10] | 1.1 | 1.01 | 0.998 | 1.000 | FAIL |
79: | bull_engulf | 3 | 2053 | 35% | 1.0 | -13.3 [-18, -9] | 0.6 | 0.31 | 1.000 | 1.000 | FAIL |
80: | bull_engulf | 5 | 2053 | 38% | 0.3 | -14.1 [-20, -9] | -0.3 | -0.14 | 1.000 | 1.000 | FAIL |
81: | bear_engulf | 1 | 2083 | 27% | 0.6 | -13.3 [-16, -11] | 0.7 | 0.58 | 1.000 | 1.000 | FAIL |
82: | bear_engulf | 3 | 2083 | 34% | -1.3 | -15.1 [-19, -11] | -1.0 | -0.49 | 1.000 | 1.000 | FAIL |
83: | bear_engulf | 5 | 2083 | 38% | 3.2 | -10.3 [-16, -4] | 3.9 | 1.57 | 0.871 | 0.826 | FAIL |
84: | bull_harami | 1 | 783 | 36% | 1.3 | -12.8 [-17, -8] | 1.2 | 0.52 | 1.000 | 1.000 | FAIL |
85: | bull_harami | 3 | 783 | 44% | 0.7 | -13.5 [-21, -7] | 0.3 | 0.09 | 1.000 | 1.000 | FAIL |
86: | bull_harami | 5 | 783 | 44% | 6.0 | -8.4 [-19, 1] | 5.3 | 1.17 | 0.990 | 0.838 | FAIL |
87: | bear_harami | 1 | 739 | 34% | 4.9 | -9.0 [-13, -5] | 5.0 | 2.36 | 0.324 | 0.270 | FAIL |
88: | bear_harami | 3 | 739 | 41% | 8.8 | -4.9 [-12, 3] | 9.2 | 2.49 | 0.250 | 0.270 | FAIL |
89: | bear_harami | 5 | 739 | 42% | 7.0 | -6.5 [-16, 4] | 7.7 | 1.68 | 0.804 | 0.826 | FAIL |
90: | hammer | 1 | 425 | 26% | -6.1 | -20.2 [-25, -15] | -6.3 | -2.50 | 1.000 | 0.270 | FAIL |
91: | hammer | 3 | 425 | 37% | -2.0 | -16.3 [-24, -8] | -2.3 | -0.55 | 1.000 | 1.000 | FAIL |
92: | hammer | 5 | 425 | 41% | 5.2 | -9.3 [-21, 2] | 4.6 | 0.81 | 1.000 | 1.000 | FAIL |
93: | hanging_man | 1 | 278 | 37% | 3.9 | -10.1 [-15, -5] | 4.0 | 1.57 | 0.871 | 0.826 | FAIL |
94: | hanging_man | 3 | 278 | 38% | 6.0 | -7.7 [-18, 3] | 6.4 | 1.23 | 0.981 | 0.838 | FAIL |
95: | hanging_man | 5 | 278 | 43% | 7.8 | -5.6 [-18, 7] | 8.5 | 1.33 | 0.957 | 0.826 | FAIL |
96: | inv_hammer | 1 | 240 | 45% | 9.5 | -4.6 [-11, 2] | 9.4 | 3.04 | 0.057 | 0.216 | FAIL |
97: | inv_hammer | 3 | 240 | 40% | -1.4 | -15.6 [-31, -1] | -1.8 | -0.25 | 1.000 | 1.000 | FAIL |
98: | inv_hammer | 5 | 240 | 45% | 0.5 | -13.9 [-35, 5] | -0.1 | -0.01 | 1.000 | 1.000 | FAIL |
99: | shooting_star | 1 | 365 | 30% | -0.4 | -14.3 [-19, -10] | -0.3 | -0.12 | 1.000 | 1.000 | FAIL |
100: | shooting_star | 3 | 365 | 38% | 1.4 | -12.4 [-21, -4] | 1.7 | 0.40 | 1.000 | 1.000 | FAIL |
101: | shooting_star | 5 | 365 | 45% | 6.7 | -6.8 [-19, 5] | 7.4 | 1.29 | 0.973 | 0.826 | FAIL |
102: | morning_star | 1 | 538 | 28% | 0.9 | -13.3 [-18, -9] | 0.8 | 0.34 | 1.000 | 1.000 | FAIL |
103: | morning_star | 3 | 538 | 34% | -2.1 | -16.5 [-23, -10] | -2.5 | -0.74 | 1.000 | 1.000 | FAIL |
104: | morning_star | 5 | 538 | 39% | 0.8 | -13.8 [-24, -5] | 0.1 | 0.02 | 1.000 | 1.000 | FAIL |
105: | evening_star | 1 | 584 | 28% | -0.8 | -14.8 [-19, -10] | -0.7 | -0.31 | 1.000 | 1.000 | FAIL |
106: | evening_star | 3 | 584 | 33% | -2.5 | -16.2 [-24, -9] | -2.1 | -0.54 | 1.000 | 1.000 | FAIL |
107: | evening_star | 5 | 584 | 39% | 4.2 | -9.3 [-20, 2] | 4.9 | 0.94 | 0.998 | 1.000 | FAIL |
108: | three_white_soldiers | 1 | 1215 | 27% | -1.3 | -15.4 [-19, -12] | -1.4 | -0.81 | 1.000 | 1.000 | FAIL |
109: | three_white_soldiers | 3 | 1215 | 35% | 1.3 | -13.0 [-20, -6] | 0.9 | 0.28 | 1.000 | 1.000 | FAIL |
110: | three_white_soldiers | 5 | 1215 | 36% | -1.4 | -15.9 [-26, -6] | -2.0 | -0.46 | 1.000 | 1.000 | FAIL |
111: | three_black_crows | 1 | 1165 | 27% | -2.6 | -16.5 [-20, -13] | -2.5 | -1.44 | 1.000 | 0.826 | FAIL |
112: | three_black_crows | 3 | 1165 | 33% | -2.0 | -15.7 [-22, -9] | -1.6 | -0.50 | 1.000 | 1.000 | FAIL |
113: | three_black_crows | 5 | 1165 | 34% | -1.9 | -15.5 [-25, -7] | -1.3 | -0.29 | 1.000 | 1.000 | FAIL |
114: | piercing | 1 | 922 | 30% | 0.3 | -13.8 [-17, -11] | 0.2 | 0.09 | 1.000 | 1.000 | FAIL |
115: | piercing | 3 | 922 | 39% | -3.3 | -17.6 [-23, -12] | -3.7 | -1.31 | 1.000 | 0.826 | FAIL |
116: | piercing | 5 | 922 | 41% | -1.8 | -16.3 [-25, -9] | -2.5 | -0.67 | 1.000 | 1.000 | FAIL |
117: | dark_cloud | 1 | 926 | 30% | 0.0 | -13.9 [-17, -11] | 0.2 | 0.11 | 1.000 | 1.000 | FAIL |
118: | dark_cloud | 3 | 926 | 37% | -0.2 | -13.9 [-19, -9] | 0.2 | 0.07 | 1.000 | 1.000 | FAIL |
119: | dark_cloud | 5 | 926 | 39% | -0.3 | -13.8 [-21, -5] | 0.4 | 0.11 | 1.000 | 1.000 | FAIL |
120: | hikkake_bull | 1 | 383 | 28% | 0.3 | -13.8 [-19, -8] | 0.2 | 0.07 | 1.000 | 1.000 | FAIL |
121: | hikkake_bull | 3 | 383 | 32% | 1.1 | -13.2 [-23, -3] | 0.7 | 0.14 | 1.000 | 1.000 | FAIL |
122: | hikkake_bull | 5 | 383 | 36% | -1.9 | -16.4 [-29, -1] | -2.5 | -0.39 | 1.000 | 1.000 | FAIL |
123: | hikkake_bear | 1 | 373 | 25% | -4.5 | -18.4 [-24, -12] | -4.3 | -1.46 | 1.000 | 0.826 | FAIL |
124: | hikkake_bear | 3 | 373 | 34% | -2.5 | -16.2 [-26, -5] | -2.1 | -0.39 | 1.000 | 1.000 | FAIL |
125: | hikkake_bear | 5 | 373 | 33% | -11.4 | -25.1 [-41, -10] | -10.8 | -1.52 | 1.000 | 0.826 | FAIL |
126: | marubozu_up | 1 | 61 | 38% | 14.9 | 0.7 - | - | - | - | - | INSUFFICIENT-N |
127: | marubozu_up | 3 | 61 | 48% | 30.1 | 15.7 - | - | - | - | - | INSUFFICIENT-N |
128: | marubozu_up | 5 | 61 | 49% | 16.4 | 1.9 - | - | - | - | - | INSUFFICIENT-N |
129: | marubozu_dn | 1 | 59 | 34% | 2.3 | -11.6 - | - | - | - | - | INSUFFICIENT-N |
130: | marubozu_dn | 3 | 59 | 46% | 22.9 | 9.1 - | - | - | - | - | INSUFFICIENT-N |
131: | marubozu_dn | 5 | 59 | 51% | 25.1 | 11.4 - | - | - | - | - | INSUFFICIENT-N |
132:
133: ## 1h volatility-state family (6 trials; one-sided: event mean > all-bar mean)
134: | state | metric | n | event mean | all-bar mean | diff | t | RC p | q(BH) |
135: |---|---|---|---|---|---|---|---|---|
136: | doji | range_ratio | 2405 | 1.041 | 1.062 | -0.022 | -1.23 | 1.000 | 0.255 |
137: | doji | abs_return | 2405 | 0.0034 | 0.0035 | -0.0001 | -0.60 | 0.997 | 0.514 |
138: | inside_bar | range_ratio | 4363 | 0.993 | 1.062 | -0.070 | -6.70 | 1.000 | 0.001 |
139: | inside_bar | abs_return | 4363 | 0.0033 | 0.0035 | -0.0002 | -3.68 | 1.000 | 0.001 |
140: | nr7 | range_ratio | 3701 | 0.826 | 1.062 | -0.237 | -22.82 | 1.000 | 0.001 |
141: | nr7 | abs_return | 3701 | 0.0030 | 0.0035 | -0.0005 | -8.25 | 1.000 | 0.001 |
142:
143: ## Triage summary
144: Pass triage: NONE
145: Trials: 1d 54 + 6 vol; 1h 54 + 6 vol (registry rows run_id P1-2026-10-07).
```

## E28

### MyTradingSys/research/b154_stratified_2026-10-09/RESULT.md

SHA-256: `ff10d640b782543d992f8287f8048eeb155dc5acc41f642531087539adeedfc4`

```text
1: # B154 STRATIFIED VERDICTS - by UTC session and by regime
2:
3: Task: 20261009-181323-b154-stratify-existing-verdicts-by-sessi
4: Run: MTS-2026-10-10 (DSA), worktree mts-dsa
5: Reads only. No existing result edited.
6:
7: ## Finding
8:
9: No result on disk carries per-event data (a timestamp column plus a net R column).
10: Every result is aggregate: it stores n, mean net R and t per cell, never the rows.
11: A session x regime stratification cannot be computed from these files; it needs the
12: event rows, which the producing scripts do not write.
13:
14: Scan: 23 CSV/JSONL files under MyTradingSys/research and MyTradingSys/backtest were
15: opened and their header checked for a timestamp column and a net-R column. Zero passed.
16: The single file whose header contains both words (fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv,
17: columns run_id,date,variant,n_trades,mean_r_net,sharpe_per_trade) is a trial registry: one row
18: per run, not per trade.
19:
20: ## Table per source result
21:
22: | Source | Per-event file | What it holds | Stratifiable |
23: |---|---|---|---|
24: | rsi_divergence_mtf_2026-10-09 | none | n, net mean, t per cell per timeframe | no |
25: | t087_session_levels_2026-10-09 | none | n, target/stop percent, net mean, t per cell | no |
26: | t090_7h_2026-10-09 | none | n, net mean, t per anchor shift | no |
27: | screenshot_context_2026-10-10 | none | narrative | no |
28: | fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv | none | one row per run | no |
29: | candle_patterns_2026-10-04/TRIAL_REGISTRY.csv | none | one row per run | no |
30: | volume_2026-10-09/TRIAL_REGISTRY.csv | none | one row per run | no |
31: | monitor_20260915/*.csv (9 files) | none | runtime counters, not trades | no |
32: | core_readiness_2026-09-27/harness/verdict_golden_baseline.csv | none | verdict rows, no PnL | no |
33: | W3_KAPPA_*.csv (2 files) | none | id, verdict | no |
34: | htf_context/*.jsonl (5 files) | none | context fields, no PnL | no |
35:
36: ## Count
37:
38: Results examined: 11 directories/groups (23 CSV/JSONL files).
39: Results with a per-event file: 0.
40: Results with no per-event file: 11.
41:
42: ## Consequence and next step
43:
44: B154 cannot be answered from existing files. To stratify, the producing scripts need an
45: events dump: one row per event with at least (timestamp_utc, net_r, side) plus the
46: session (Asia 00-08, EU 08-13, US 13-21, late 21-24 UTC) and a 1d EMA50 slope regime.
47: Recommended shape: add an --events <path.csv> flag to backtest/layers/rsi/run_divergence_mtf.py
48: and the T087 probe, run once, then this task is re-posted against those CSVs.
```

## E29

### MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md

SHA-256: `d930f51c05a08066a58f3b7731ca01c9cd80bd48e6d9e31feafd098794c8f634`

```text
1: # John Kurisko "Quad Rotation" scalp - sourced spec (playbook Part I) - 2026-10-09
2:
3: Operator ask (verbatim): "What abt John Kurisko strategies? he said there is one that you need to sit and wait patiently. It is a quick get in
4: and get out scalp - i remember it was 4 rsi indicators with certain params."
5: Status: layer candidate only. Separate layer, never a Tom filter (Tom is core, PROJECT_VISION). Nothing here is an MTS rule until the operator approves it
6: (playbook Part I "Consequences": a change backed only by T3 needs explicit operator approval) and our own backtest passes.
7:
8: ## 0. Answer in five lines
9:
10: 1. John Kurisko (DayTradingRadio) has exactly one multi-indicator scalp that fits your memory: the **Quad Rotation** (with the **Super Signal** = quad rotation + divergence).
11:    It is **four STOCHASTIC oscillators, not four RSIs.** No source I opened ties Kurisko to RSI. [MATCH: sources S1-S5 below; the transcript, the slide deck, the show notes and the AI summary were each checked for "RSI": none mentions it]
12: 2. Settings stated by Kurisko-attributed sources: stochastic (9,3), (14,3), (40,4) or (44,?) [conflict], and (60,10,10). Levels 20 / 80. One position idea: wait for all four under 20, then the fast one turns up.
13: 3. Timeframe 1-minute and 5-minute charts, micro E-mini S&P futures (MES). Patience is part of it: "less is more ... wait for the opportunities".
14: 4. The spec is **not fully sourced** (section 5), so no backtest plan is written. Two fixes are needed first: the missing exact stochastic definition and the (40,4)-vs-(44) conflict.
15: 5. "4 RSI with params" stays **NO-SOURCE**. If you want the RSI version tested anyway, it has to be labelled "operator hypothesis", not Kurisko.
16:
17: ## 1. Method note (Part I step 1)
18:
19: What would settle "does a quad-rotation scalp have an edge on BTC": our own pre-registered out-of-sample backtest on BTCUSDT 1m/5m klines with fees (taker 5 bp per side,
20: repo schedule; 14 bp round trip used in MARKET_GUIDE_RESULTS_2026-10-07.md:20) and funding, IS 70 / OOS 30 plus PBO, per CLAUDE.md gates. External sources here only say WHAT the rule is, never THAT it works.
21: Searches covered Kurisko-attributed content only. I did not search T1/T2 literature on stochastic-oscillator profitability: **no validated evidence searched or found**, so nothing below may be used as a universal claim.
22:
23: ## 2. Sources, tiers and verification (Part I step 3a: each opened 2026-10-09)
24:
25: | ID | Source | What it is | Tier | Opened / matched |
26: |---|---|---|---|---|
27: | S1 | Desire To Trade podcast ep 472 "The 3 Scalping Setups That Make Me A Living - John Kurisko" (Etienne Crete interviews Kurisko; released 2024-09-16, 43 min), https://podcasts.apple.com/us/podcast/472-the-3-scalping-setups-that-make-me-a-living-john-kurisko/id1037685976?i=1000669724169 ; same recording on YouTube https://www.youtube.com/watch?v=PjigwAmhiT0 | Kurisko in his own words (primary speaker); chapters "quad rotation strategy" 13:22, "concept of divergence trading" 16:20, "Quad Super Signal: the perfect exit" 33:24 | T3 (practitioner, own words) | Apple page opened and title/date/chapters matched. YouTube page opened: title matched, description not retrievable |
28: | S2 | Auto-captions of S1: https://pickscribe.com/v/PjigwAmhiT0 (ytscribe redirects here) | Full transcript, auto-generated ("93 14344 and 6010", "mees" for MES) | T3, garbled numbers | Opened; title and channel matched to S1; the numbers in it are NOT clean, so they are only used to cross-check S3/S4 |
29: | S3 | Desire To Trade ep 538 "This Scalping Strategy Makes Me A Living (John Kurisko)", https://www.desiretotrade.com/538-this-scalping-strategy-makes-me-a-living-john-kurisko/ | Show notes of a second Kurisko interview (date not on page): "Deep dive on stochastics (9-3, 14-3, 44, 60-10)", "Quad rotation explained (all stochastics aligned)", "The super signal: quad rotation + divergence", "why the 9-3 at 80 is your cash-out signal", "Timeframes, expectations (1-5 min)" | T3 | Opened and matched. Topic list only; mechanics are not on the page |
30: | S4 | Slide deck, "John Kurisko's interview on Desire To Trade.pdf", re-host https://www.slideshare.net/slideshow/john-kurisko-s-interview-on-desire-to-trade-pdf/272299238 (uploader famosabazaar, i.e. not Kurisko) | Kurisko's chart blueprint: "Fast Stoch (9-,3)", "Fast Stoch (14,3)", "Fast Stoch (40,4)", "Full Stoch (60,10,10)"; divergence stage rules; stops; partial exits | T3 (re-host of a practitioner deck) | Opened and matched. The DTT original https://www.desiretotrade.com/wp-content/uploads/2020/07/Podcast-Interview-slide-show.pdf (46 pages, 89 images) opened but has no extractable text, so I could not match it page by page |
31: | S5 | Lilys AI note https://lilys.ai/en/notes/211149 | AI summary of S1 (states itself "garbled" numbers) | T3 secondary; cross-check only | Opened; it matches S2 where both are readable |
32: | S6 | https://home.daytradingradio.com/ | Kurisko's commercial site | Vendor page; no rule content | Opened: mentions "Quad Rotation" only as a scanner/alert feature for members |
33: | S7 | TradingView "JK Scalp" by nishith85441 (2025-12-16), https://kr.tradingview.com/script/1TTBunq7-JK-Scalp-Nishith-Rajwar | Third-party implementation: Fast (9,3), Medium (14,3), Slow (44,3), Trend (60,10,10) | T3 community, NOT Kurisko | Opened. Source code not shown; it does not name Kurisko or RSI in the text I read |
34:
35: Findings are tagged `Tier | method | confidence` below. None of S1-S7 shows any backtest, so method quality is "none: stated rules only".
36:
37: ## 3. The rule as stated (what each source says)
38:
39: | Element | Statement | Sources | Tag |
40: |---|---|---|---|
41: | Concept | Four stochastic "bands" on one chart. A **quad rotation** is when all four are oversold, under 20, at the same time: "when all each one of these bands get oversold under 20 at the same time that is what we call a quad rotation" | S2 (quote), S3, S4 | T3 / none / M |
42: | Super Signal | Quad rotation merged with a (price vs stochastic) divergence. Kurisko calls the combination his "Holy Grail" (win-rate claims such as "95%" are his own and have no data: REJECT as evidence) | S2, S3, S4 ("The Super Signal is a merger of a quad rotation and an" - truncated) | T3 / none / M |
43: | Stochastic 1 (fast) | (9,3); slide label "Fast Stoch (9-,3)" (OCR artefact for 9,3) | S4, S3 "9-3", S2 "nine candles", S7 | T3 / none / H for the pair 9,3 |
44: | Stochastic 2 | (14,3) | S4, S3, S2 "14 candles", S7 | T3 / none / H |
45: | Stochastic 3 | **CONFLICT**: (40,4) in S4 and S2 "40 candles"; "44" in S3 and in S2's digits ("14344"); (44,3) in S7 | S2-S4, S7 | T3 / none / L |
46: | Stochastic 4 (trend) | (60,10) in S3 / S2; (60,10,10), "Full Stoch", in S4 and S7. Role: it represents the 5-minute timeframe inside a 1-minute chart ("the 6010 is the five minute time frame") | S2, S3, S4, S7 | T3 / none / H for 60,10 |
47: | Levels | Oversold < 20, overbought > 80. In bull setups the 60/10 should be above 80, "preferably 90" ("above 85 preferably 90") | S2 | T3 / none / M |
48: | Entry (divergence / quad) | Enter right when the fast (9,3) turns back up: "you take that trade right when you see that turn back up". Divergence stage 1: stochastics under 20; the low bounces them back above 20; price then makes a lower low / double bottom while the stochastic makes a higher low | S2, S4 ("Stage 1 on the divergence should have the stochastics under the 20") | T3 / none / M |
49: | Entry (bull flag, a separate third setup) | After a strong push off the 20 EMA, 60/10 stays above 80, buy when the fast stochastic hits 20 | S2 ("you buy when the 93 hits the 20"), S4, S5 | T3 / none / M |
50: | Higher-timeframe confirmation | "5 Min and/or 60 Min stochastics should be moving up (preferred) off oversold"; chart legend lists 1 Min, 5 Min, 60 Min, D | S4 | T3 / none / L |
51: | Stop | S2: "one to two ticks under the pattern low candle"; S4: "1 tick under the divergence candle". Tick-based on MES (0.25 index point); no percent or ATR form is given | S2, S4 | T3 / none / M (1 vs 1-2 ticks conflict) |
52: | Exit | Sell each fast (9,3) rotation above 80 ("you need to sell every rotation of the 93 above 80"); partial profit when the fast stochastic crosses back above 80, stop moved up. Chapter "Quad Super Signal: the perfect exit" (S1 33:24) | S2, S3, S4 | T3 / none / M |
53: | Timeframe / market | 1-minute and 5-minute charts for scalps; micro E-mini S&P (MES) mainly; daily charts for longer trades. Context tools named in S5: 20/50/200 EMA, VWAP, hand-drawn support/resistance | S2, S3, S5 | T3 / none / M |
54: | Waiting | "less is more you know wait for the opportunities"; "you got to only take the Divergence setups"; slide: "You have to be ready when the trade appears" and "Most of the great setups appear in channels" | S2, S4 | T3 / none / M |
55: | Shorts | The mirror (all four above 80) is described only by community text (S7: "below 20 or above 80"). Kurisko's own words I read give long examples plus "sell every rotation above 80" as an exit | S7 | community only: treat the short side as NO-SOURCE until his words are matched |
56:
57: ## 4. About the "4 RSI" memory
58:
59: - NOT_IN_DATA: no opened source says Kurisko uses RSI. The full transcript text (S2), the slide deck text (S4), the show notes (S3) and the AI note (S5) do not contain "RSI".
60: - Closest RSI link on the open web: the TradingView script "Multi Stochastic Alert" by IMStockwala (2025-01-30), https://cn.tradingview.com/script/SSUHdyuV-Multi-Stochastic-Alert/ . It uses the same four stochastics (9,3), (14,3), (40,4), (60,10), says "Trade entry become active when all of these goes below 20 or above 80", and adds "we wait for RSI Divergence and we enter". Its author is IMStockwala, not Kurisko; the name Kurisko appears only as a page tag. This is a plausible origin of "four indicators + RSI" in memory (hypothesis, not established).
61: - Therefore: "4 RSI indicators with certain params" = NO-SOURCE. Do not create RSI parameters and attribute them to Kurisko.
62:
63: ## 5. Is the spec fully sourced? No. Blocking gaps
64:
65: 1. Third oscillator: (40,4) vs (44,x). Two Kurisko-attributed readings disagree. Needs the slide image or the video itself.
66: 2. The exact stochastic formula: the labels "Fast Stoch" and "Full Stoch" with (k,d) or (k,d,d) are given, but %K period vs smoothing roles and the platform (formula variant) are not stated in any source I read. FORMULAS.md has no stochastic section (checked: sections 1-17 cover RSI, MAs, tolerance events, forward return, resample, CryptoCred, stats, execution, ATR, T055, B070).
67: 3. "Turns back up": no numeric turn definition (1 bar? crosses 20 upward? crosses own %D?). S2 says "turn back up", S4 says "close of touch oversold 20 line".
68: 4. Divergence: no swing-detection rule (minimum bars, which of the four stochastics defines it; S2 only says price lower low + stochastic higher low). A Kurisko-style rule must be defined by his words or listed as operator choice.
69: 5. Stop and exit are in ticks on MES and "every rotation" of the 93 above 80; there is no BTC translation, no position-size rule, no time exit, no max trades per day. Each would be NO-SOURCE if invented.
70: 6. Short side not sourced (section 3 last row).
71: 7. Primary text quality: S2 is auto-captions (digits garbled); I read it through a web summariser, so quotes above are as returned and need a clean match. Next step (needs a go-ahead because it is a download): `python scripts/dev/fetch_captions.py PjigwAmhiT0` into `raw_transcripts_canonical/` (same tool that fetched the Malkan transcripts), then the extract gate `verify_extract_quotes.py`.
72:
73: ## 6. Fit to MTS (analysis, not a plan)
74:
75: - Market mismatch: Kurisko's stops are 1-2 ticks on MES during US cash hours; the repo's cost model is taker 5 bp per side. A few-bp stop on BTC 1m is under the 14 bp round-trip cost, the situation the roadmap already calls fee-dominated ("49-100 % fee-dominated (stop under round-trip fee, F-BT-22)", research/CONSOLIDATED_ROADMAP_2026-10-09.md:27-28). Expect the same problem unless the trade targets more than a few bp.
76: - Closest sibling already tested: generic RSI/volume events NO-EDGE (RSI_HISTORY.md section 4). A stochastic quad rotation is untested in the repo (grep "stochastic" over .md/.py found only DIVERGENCE_AUDIT, VVP-001 "Stochastic: Not a Tom concept", BT_SPEC and a Krown note).
77: - Isolation: if built, it is a new layer under `backtest/layers/` with its own params file (`source` = "Kurisko S1-S4"), no import of Tom constants, no use as a Tom filter, alert-only first.
78: - Backtest plan: **not written** (condition "only if the spec is fully sourced" is not met). Preconditions to write one in under a page: close gaps 1-4 above, add a stochastic section to FORMULAS.md with a hand-computed example, and have the operator decide gap 5 items (stop, exit, BTC translation) as explicit operator parameters.
79:
80: ## 7. Rejected / not used (listed once so they are not researched again)
81:
82: - forex.in.rs "John Kurisko's Trader Strategy" and companion article: seen only in search results, not opened (cannot be matched), and the snippet's "four stochastics on four timeframes" contradicts S2/S4. REJECT.
83: - cTrader "Stoch PRO Quad Rotation Signal" and the unattributed TradingView "Quad Rotation Stochastic": vendor listings, not opened, no Kurisko words. REJECT.
84: - Generic RSI scalping blogs (RSI 5/7/9 with 80/20, 75/25, etc.): no author tie to Kurisko. REJECT as Kurisko evidence.
85: - Kurisko's own performance claims ("95 percenter", "Holy Grail", "works 95% of the time"): win-rate claims without costs or method. REJECT.
86: - Spotify / Podbean / iHeart / Everand listings of the same episodes: duplicates of S1/S3, not needed.
```

## E30

### MyTradingSys/backtest/PRE_REG_TEMPLATE.md

SHA-256: `2e790bab7de5ae67bd18092b0fe042049e489396127d107371cafb69ed5f880a`

```text
1: # Pre-registration template: backtest readiness (12 items)
2:
3: Source: research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md section 6 (adopted 2026-10-12, card backtest-readiness-template).
4: Copy this file next to a layer's pre-registration (or HOME_FIT_AUDIT_<layer>.md) and fill every slot BEFORE any backtest run.
5: An item with no answer or no evidence line is `NOT_ANSWERED`; the run does not start. Missing data is `NOT_IN_DATA`, never 0.
6:
7: ## 1. Source home: market, timeframe, session, holding period (with quote + file:line).
8:
9: Answer: TODO
10: Evidence (file:line): TODO
11:
12: ## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.
13:
14: Answer: TODO
15: Evidence (file:line): TODO
16:
17: ## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.
18:
19: Answer: TODO
20: Evidence (file:line): TODO
21:
22: ## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).
23:
24: Answer: TODO
25: Evidence (file:line): TODO
26:
27: ## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).
28:
29: Answer: TODO
30: Evidence (file:line): TODO
31:
32: ## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).
33:
34: Answer: TODO
35: Evidence (file:line): TODO
36:
37: ## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.
38:
39: Answer: TODO
40: Evidence (file:line): TODO
41:
42: ## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).
43:
44: Answer: TODO
45: Evidence (file:line): TODO
46:
47: ## 9. Null like-for-like: same session window, same order type, same fill rules.
48:
49: Answer: TODO
50: Evidence (file:line): TODO
51:
52: ## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".
53:
54: Answer: TODO
55: Evidence (file:line): TODO
56:
57: ## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.
58:
59: Answer: TODO
60: Evidence (file:line): TODO
61:
62: ## 12. Stratified readout by regime and session (B154) next to the pooled number.
63:
64: Answer: TODO
65: Evidence (file:line): TODO
```

### MyTradingSys/PROJECT_VISION.md

SHA-256: `21eec21783b6959aa6f0c7cda3a0b0c9ea92a6fa5c3be104a54997c6a7e01e30`

```text
1: # PROJECT VISION / DIRECTION
2: # Saved: 2026-09-15  |  Rewritten: 2026-09-23 (architecture doctrine locked)
3: # Purpose: direction ledger + locked architecture doctrine. Read before any new build.
4: # Rule 52: this is a pointer for direction, not a spec.
5: # Change rule: verbatim sections change only by operator edit. No agent rewrite.
6:
7:
8: ## ARCHITECTURE DOCTRINE (locked 2026-09-23)
9:
10: ### OPERATOR STATEMENT (verbatim, 2026-09-23)
11:
12: "We use Tom's core ideas - It is the core layer. Everything else sits on top of it and must be an independent module that could be switched on and off for computation/integration purposes and or displayed along side as complimentary readings. Understand that we will keep adding Tom's rules as we extract more transcripts. And not just from him - also from different analysts. We will then decide what gets into the core engine later as the project evolves and we back test!"
13:
14: ### INTERPRETATION (not verbatim)
15:
16: 1. TOM IS CORE. Tom's rules are the core layer. Non-negotiable. Sourced from transcripts, cited per [TOM-NNN].
17: 2. EVERYTHING ELSE IS A MODULE. Modules are switchable: on for computation and/or integration, off for baseline operation. Or displayed alongside as complementary reading. Modules never gate core behavior.
18: 3. CORE GROWS. New Tom transcripts extend the core. Other analysts' rules may enter the core later, by the same admission gate.
19: 4. ADMISSION IS DEFERRED. New rules wait at the module layer until project maturity and backtesting justify promotion. No rule enters the core engine without that gate.
20:
21: ### RELATION TO DSA SECTION 9
22:
23: DSA_SESSION_PROMPT.md section 9 lists the authority order for behavior in a
24: session: compiled_engine first, condition files second, Tom transcripts third.
25: That order governs how a live session resolves conflicts. This doctrine governs
26: what should be in the engine over time: Tom's rules, extended by extraction,
27: with non-Tom layers kept modular. The two are compatible. Where they appear to
28: conflict, DSA governs the session; this file governs direction.
29:
30: ### CURRENT TAG FAMILIES IN compiled_engine.md
31:
32: Inline rule tags as of 2026-09-23 (grep of compiled_engine.md):
33:
34: | Tag | Count | Role |
35: |-----|-------|------|
36: | [PRINCIPLE] | 21 | reading aids, display-only |
37: | [SYSTEM] | 11 | mechanism, math, plumbing |
38: | [VISUAL FLAG] | 2 | screenshot-only, no runtime consumer |
39: | [SSOT] | 1 | single-source marker |
40:
41: [TOM-NNN] and [CT-NNN] are source ids in traceability matrices, not inline
42: rule tags. Under this doctrine, inline tags will be extended to [CORE] or
43: [MODULE] over time. That extension is deferred; the doctrine locks the intent,
44: not a code change.
45:
46: ## THE FOUR GAP CLASSES (locked 2026-09-23)
47:
48: ### OPERATOR STATEMENT (verbatim, 2026-09-23)
49:
50: "1. It can be that we did not extract all rules so far!
51: 2. We extracted rules incorrectly or partially
52: 3. Extracted rules are implemented incorrectly or partially or missed compleletly
53: 4. Rules could be wired incorrectly or not wored at all."
54:
55: (Spelling preserved verbatim: "compleletly", "wored".)
56:
57: ### PLAIN FORM
58:
59: | # | Gap | Where it lives | Guard |
60: |---|-----|----------------|-------|
61: | 1 | Rule not yet extracted | Transcript to extract | Extraction coverage audit |
62: | 2 | Rule extracted incorrectly or partially | Extract file | DSA section 10 discipline (three snapshots) |
63: | 3 | Rule implemented incorrectly, partially, or missed | Code | Source-to-code traceability (T043) |
64: | 4 | Rule wired incorrectly or not wired | Runtime | Runtime verification, not just compile/test |
65:
66: Gaps 1 and 2 sit upstream of the engine. Gaps 3 and 4 sit inside it.
67: T043 currently covers 3 and 4 only. Gaps 1 and 2 have no mechanism yet.
68: ## USER DIRECTIVE (verbatim, 2026-09-15)
69:
70: "Instead of thinking like this - think -> that we will create this capability that is session-aware and use it an as in add on to our existing system. We do not need to change any existing trade logic right now. let this evolve. First let us see how the outer frame will look like.
71:
72: Note that we will integrate RSI - so it is momentum and it comes from a different trading system which is using RSI as 40-60 as per MalkanViews. So it will provide us trade setups. Similarly - we were working on probability distribution and it will do it's job and now I am not sure how we need to combine things. we need to keep things isolated at first and get independent read of these trading systems that we will integrate with MTS and then we can look for confluences and use some metric from these new trading system integrations that will be like a add on stuff. Take for example analysts verdicts on trades - so we will download video transcripts - extract and keep tabs on what they say and the confluences we get from our trading systems. Slowly we can even integrate it but it is distant! I think you should save this note verbatium for the needs of the project and it's direction that should be kept in mind before developing anything new! We can also build and maintain it to see where we are headed."
73:
74: ## INTERPRETATION (not verbatim)
75:
76: 1. ADD-ON, NOT REWRITE. Session-aware frame layers on MTS. Existing trade logic unchanged. Let it evolve.
77: 2. OUTER FRAME FIRST. Define how the session frame looks before wiring anything in.
78: 3. ISOLATE, THEN COMBINE. Each external system produces its own independent read first. Confluence is a later step, only after independent reads are proven.
79: 4. INTEGRATIONS ARE PEERS. RSI/MalkanView, probability distribution, analyst verdicts each enter as a separate read layer. None replaces MTS core.
80: 5. ANALYST LAYER IS A PIPELINE. Download transcripts -> extract -> track verdicts -> compare against MTS output. Distant. Not wired.
81: 6. THIS FILE IS THE DIRECTION LEDGER. Read before any new build. Update when direction changes.
82:
83: ## INTEGRATIONS TRACKED
84:
85: | System | Source | Status | Read produced |
86: |---|---|---|---|
87: | RSI 40-60 (MalkanView) | external system | design 2026-09-28 (RSI_TF_LAYER_DESIGN.md); sub-layer of the RSI layer | momentum, setup timing |
88: | Probability distribution | event_probability_layer_DESIGN.md | stage 3 unblocked 2026-09-28 (10,289 labels; 5,000 gate met); frequency-table MVP queued (NUC 033) | forward return probability |
89: | Analyst verdicts | extracts/processed/tom/ + future | distant | discretionary opinion |
90: | Session-aware frame | new (this project) | design | session bias, day type, initial balance |
91:
92: ## PRINCIPLES
93:
94: - Tom is core. Everything else is a module. Modules never gate core behavior.
95: - Modules are switchable: on for computation/integration, off for baseline. Or displayed alongside.
96: - Add, do not modify. Core MTS logic not rewritten.
97: - Isolate first. Combine only after each read is independently validated.
98: - Independent reads before confluences.
99: - Rule 32 still binds: no new engine rule without 3-snapshot proof.
100: - Direction documented here before build.
101: - RSI arrives first. Design its isolation path with the session frame.
102:
103: ## OPEN QUESTIONS
104:
105: - Session anchor: RESOLVED 2026-09-16. Two anchors, two jobs. UTC 00:00 anchors raw data calculation (existing CVD block and session aggregates). US cash open (13:30 UTC summer / 14:30 UTC winter, DST-aware) anchors the session-aware frame: session high/low/open, range position, day type, initial balance, session bias. The sixteen new session fields use the US cash open anchor. No existing UTC-anchored field is renamed or moved.
106: - How does each integration surface its read? Snapshot field, separate file, sidecar process? (Undefined.)
107: - Interface between MTS core and read layers? (Undefined.)
108: - When a read conflicts with MTS, which wins? (Undefined. Must be decided before integration.)
109:   RESOLVED 2026-09-25 (worker W6, receipt per extract PROJECT_VISION.md L23-L28; L134-L138; L16-L18).
110:   Q1 (how each integration surfaces its read): separate read-layer file or sidecar process; read-only; switchable module; never gates core.
111:   Q2 (interface between MTS core and read layers): one-way read-only contract over engine-computed state; no writes back; no commands run by the reader.
112:   Q3 (conflict priority): MTS core wins for core behavior; read layers may annotate conflict as complementary reading only.
113:   Reply: Dumps/workers/CLOSE-2026-09-25/W6-project-vision/REPLY.md
114:
115: ## USER DIRECTIVE (verbatim, 2026-09-22) - LOCAL AI ASSISTANT + TICK-DELTA LAYER
116:
117: Quoted from operator note. Preserved verbatim. Full text with the three-machine breakdown is in the companion note supplied to the session; the sections below carry the parts that change project direction.
118:
119: On the assistant: "the real-time trading assistant must run LOCALLY ON THE DESKTOP, co-located with the MTS engine - not on the NUC. Reason: during an active trade I need instant answers with zero network hop (no LAN round-trip to NUC, no browser/API round-trip to hosted models). The NUC stays purely for offline code work where latency doesn't matter."
120:
121: On the assistant's job: "it must NOT just repeat what the compiled engine already alerts on (that's already solved, deterministic, and doesn't need an LLM). Its value is answering ad-hoc questions I didn't pre-program a fixed display for - comparing current state to recent history, explaining why a verdict changed, contextualizing strength/weakness of a setup - grounded STRICTLY in what the engine has actually computed. Read-only: it never writes back to the engine, never runs commands, matching the existing MTS safety model."
122:
123: On the tick-delta layer: "A standalone Python process subscribing to the raw tick feed (independent of the candle-close snapshot writer). Computes fast deltas on selected indicators (price, CVD, whatever else proves useful) over a short rolling tick window. Checks against a threshold - only when crossed does it emit an event (avoids flooding the assistant with tick noise). Writes to a separate event stream/file, tagged clearly as source: tick vs source: candle, so the assistant's context always knows the granularity and recency of what it is looking at. Needs its own cooldown, same as your existing candle-alert cooldown, or tick noise will spam it constantly."
124:
125: On rule surface: "any tick-based thresholds you pick (what counts as a significant CVD delta, say) will need the same Tom-citation-or-documented-exception treatment your other indicators go through - this is new rule surface, not just plumbing, so it likely needs to go through the same research-tier process before it's trusted in a live decision."
126:
127: ## THE THREE MACHINES (added 2026-09-22)
128:
129: | Machine | Role | Compute |
130: |---|---|---|
131: | Intel NUC 10 (NUC10i7FNHN, i7-10710U, 32GB) | Offline code builder, always-on. Runs Ollama on CPU (no GPU). Background work only. Not live trading. | CPU-only inference, 7B-14B quantized |
132: | Old desktop (i7-4770K, 32GB DDR3, locked MB/CPU/RAM trio) | Runs the MTS core engine (Java ingest + Python rule eval). Also candidate host for the real-time assistant. | CPU/RAM bound; GPU relevance only for assistant latency |
133: | Lenovo ThinkPad laptop | Lightweight monitoring. Not a compute node. | N/A |
134:
135: Decision: GPU purchase for the desktop is not speculative. Test a small quantized model (3B-8B) on CPU first; only measured latency above tolerable threshold justifies a GPU (RTX 3060 class). Evidence-based, not speculative.
136:
137: ## ASSISTANT PRINCIPLES (added 2026-09-22)
138:
139: - Read-only. Never writes to the engine. Never runs commands. Matches the existing MTS safety model.
140: - Grounded strictly in engine-computed state. The assistant's answers derive from snapshot fields, verdict strings, alerts, and history; it does not free-reason beyond them.
141: - Value is ad-hoc Q&A, not alert repetition. Alerts stay in the deterministic engine; the assistant handles questions the engine was not pre-programmed to answer.
142: - Co-located on desktop. No network hop during an active trade.
143: - One input granularity tag per consumed record: source:candle or source:tick. Mixing without the tag is not allowed.
144:
145: ## INTEGRATIONS TRACKED (rows added 2026-09-22)
146:
147: | System | Source | Status | Read produced |
148: |---|---|---|---|
149: | Local AI trading assistant (desktop) | operator note 2026-09-22 | direction | ad-hoc Q&A over engine state. Read-only. |
150: | Tick-based delta layer | operator note 2026-09-22; item doc T040 | design | fast deltas over rolling tick window, threshold-cross events tagged source:tick |
151: | Ollama code builder (NUC) | operator note 2026-09-22 | direction | offline code change execution. Not live. |
152:
153: ## OPEN QUESTIONS (added 2026-09-22)
154:
155: - Assistant model choice: which small local model for CPU-first, with GPU fallback. Undecided.
156: - Assistant context window shape: rolling N-minute window of recent snapshots, or single latest snapshot only. Undecided.
157: - Tick-delta thresholds: which indicators, what numeric thresholds, what cooldown value. All new rule surface; require research-tier process before trust. Tracked in items/T040_tick_delta_layer.md.
158: - Assistant input merge: shared file vs separate files for candle and tick streams, ordering and dedup rules. Design item under T040.
159:   RESOLVED 2026-09-25 (worker W6, receipt per extract PROJECT_VISION.md L114; L116; L118-L120; L126-L130; L135; L138; L152-L153; per extract MTS_DICTIONARY.md L162-L175).
160:   Q4 (assistant model choice): test a 3B-8B quantized model CPU-first on the desktop; buy an RTX 3060-class GPU only if measured latency exceeds tolerance.
161:   Q5 (context window shape): rolling N-minute window of recent snapshots, plus alerts and history as needed.
162:   Q6 (tick-delta thresholds and input merge): start with price and CVD; documented numeric thresholds; explicit cooldown; separate files for candle and tick streams; one granularity tag per consumed record (source:candle or source:tick). Thresholds are new rule surface and require research-tier before trust. Tick-delta stays module-only: it never vetoes or triggers a core setup.
163:   Reply: Dumps/workers/CLOSE-2026-09-25/W6-project-vision/REPLY.md
164:
165: ## DIRECTION DECISION (2026-09-26) - LAYER FREEZE LIFTED FOR T048
166:
167: Not verbatim. Recorded per this file's own "direction documented here before
168: build" principle.
169:
170: MyTradingSys/PROJECT_VISION.md.new (drafted 2026-09-25 13:21Z, never merged)
171: proposed a layer freeze pausing T048 (satellite framework + exchange API
172: layer), T040, the local AI assistant, and further NUC-builder build-out,
173: until (1) compiled_engine.md's inline tags extend to CORE/MODULE and (2)
174: T043 closes. Neither condition was actually met when this was found
175: 2026-09-26: (1) is undone - zero CORE/MODULE tags exist, the doctrine above
176: still calls that extension deferred; (2) T043 closed WONTFIX 2026-09-23 (the
177: mechanism was rejected, not built - see items/T043_traceability_gap.md,
178: synced 2026-09-26 to match BUGS.md, having drifted since the closure).
179:
180: Operator directive 2026-09-26: lift the freeze for T048 specifically. The
181: NUC-worker rule-tagging/traceability work continues on its own track under
182: T049; it is not a precondition for T048 anymore. T040 and the local AI
183: assistant are not addressed by this decision and remain as the unmerged
184: .new left them unless raised separately.
185:
186: The unmerged MyTradingSys/PROJECT_VISION.md.new is superseded by this entry
187: for T048's purposes and left in place as a dated record, not applied.
188:
189: ## USER DIRECTIVE (verbatim, 2026-09-28) - RSI LAYER, TIMEFRAME LAYER, BACKTESTING
190:
191: Preserved verbatim from the operator's message in the Opus supervisor session (code mode). Spelling kept.
192:
193: 1. Back test all and prepare Qwen for all back testing related stuff.
194: 2. [...] where downloaded - on desktop or NUC? Build must do as much of back-testing as possible under surveillance. This RSI 40-60 must not be used for any other RSI signal that MTS may demand/need/require instead use the usual RSI default readings. Some Things I want to quote here (log as a Verbatim ) -
195:
196: 1. We need smoothed RSI moving average that come with the usual indicator and look for support on these moving avgs on any given time frame. Add this is a separate feature in the RSI module/indicator-layer.
197: 2. The threshold of slipped from actual numbers like RSI taking support on the 60 line or RSI rejected from the 40 line. So it can reject from 41 0r 42 or 39/38  etc - so we need to see during back-testing that how much slippage we can allow based on actual results. This to be done for all edge cases/scenarios.
198: 3. RSI modules must be also layered within. A full Malkanview RSo 40-60 system can spit out trades for any timeframe. But we may require things like RSI support or rejecton in 3 mins or 2 mins or 15 mins or 12 ours - whenever it changes - we get an alert for each time frame. We need usual time frames but we also need 1,2,3,10 mins and 2 day, 3 day and 5 day as well! I think we might require a separate timeframe layer that serves each module/later including core? Opus needs to decide.
199: 4. So once we start testing indicators on test-net - we will fine tune them as per my inputs and expertise and as per professional that are WORTH listening to in the Crypto Space! Remeber about the fine tuning part and make sure our design is flexible and accurate and well aritectured for this trading software we are building.
200:
201: So you get the idea.. I need evrything rolling efficiently
202:
203: ### INTERPRETATION (not verbatim)
204: Design decisions for this directive: MyTradingSys/research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md.
205:
206: ## DIRECTION UPDATE (2026-10-10, operator approved D23 'Apply the addendum as drafted'; not verbatim; supersedes stale rows above where they conflict)
207:
208: Backtest gate (2026-10-12): every layer backtest answers the 12 items in `backtest/PRE_REG_TEMPLATE.md` before it runs.
209:
210: ### Goal and stages
211: MTS exists to trade BTC with a proven net edge after fees, first on testnet, then real money only after the
212: GO-LIVE BAR (system/GO_LIVE_BAR.md, D06-gate 2026-10-09) holds for 30 days. Work follows five stages:
213: S1 trustworthy measurements, S2 survive the fees, S3 find a real edge (walk-forward OOS net R > 0, CI above 0),
214: S4 prove it on testnet, S5 go-live gate. Status today: S1-S2 in progress; no source has passed S3.
215:
216: ### Cores and layers
217: Two cores since 2026-10-01: Tom and Fabio, each compiled independently with its own verdicts, plans and ledger
218: source flag (research/ARCHITECTURE_TWO_CORES_2026-10-01.md). Every other system (RSI/Malkan, CryptoCred,
219: session, positioning, probability, tick, timeframe, options, analyst/caller feeds) is a switchable layer that
220: never gates a core. A core or layer that fails S3 on fixed data is parked (alerts kept for data), not tuned
221: into passing. Promotion to core uses the S3 bar, never opinion.
222:
223: ### Provenance and its two exceptions
224: Every parameter comes from the source trader's own words (file:line) or is NO-SOURCE. Exceptions:
225: (1) BT-TUNED: backtests may tune toward catching big, profitable moves; tuned values are labelled and never
226: written to live files without an operator decision. (2) NO-SOURCE research tests: specs with no trader
227: behind them (chatbot handoffs, B163) may run as labelled backtests only, never as live layers.
228:
229: ### Sources we listen to
230: A trader/analyst enters only with transcripts or a verifiable call history, scored before any trade
231: (Qriptal scorecard B162 is the template). Each stays an isolated layer until S3.
232:
233: ### Economics and risk
234: Every result is net of real fees and funding. Stops are wide enough that fees cost under 0.25 R.
235: Safety checks fail closed; missing data is reported as missing, never as 0. Per-source testnet accounts,
236: daily-loss monitor and kill switch guard every trade. Testnet calibration (all layers fire) counts as data,
237: not as S4 evidence; only S3-passed configs count toward the bar. Mainnet needs a separate signed decision.
238:
239: ### How the project runs
240: Operator speaks through the Control Room (inbox verbatim, decisions). Work is cost-routed: scripts, then DSA,
241: then Sonnet, Opus only when named. Sessions are short and relay automatically. Code reaches the live tree only
242: through CI-gated auto-deploy. Off-desktop sessions read live state through the read-only mirror.
243: Devices: JIS-NB live loop; JIS-NUC backtests (candidate live host); laptop for travel. Qwen/Ollama lane retired.
244:
245: ### Parked or open
246: Local AI assistant: parked (no build since 2026-09-25). Symbol scope beyond BTCUSDT perp: undecided.
247: Confluence may gate a trade only after each input passed S3 on its own.
248:
249: # END
```

### MyTradingSys/system/control_room.json

SHA-256: `ccd3b737d04e913dbdcb4da670928f30f592ba14be6e7f18ee5f3a89e65e34c8`

```text
1: {
2:   "_doc": "Hand-kept content of the MTS Control Room page (scripts/dev/make_control_room.py). Edit HERE, never the page. Process: MyTradingSys/system/CONTROL_ROOM.md. Item ids: registry rows (B/T), bigtrade findings (F-BT-NN), or X- road tasks defined below. When an X- task gets a registry row, replace the X- id with the row id.",
3:   "artifact_url": "https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su",
4:   "asof": "2026-10-09",
5:   "verdict": "The system runs and trades on testnet, but no source has shown a real edge after fees. Stage 1 data fixes are now live (volume profile, naked POC); Stage 2 results are in and negative for Tom: a wider stop or maker orders only shrink fees, because gross R is already negative. Next: re-run the backtests on the fixed data (T082) and look for gross edge elsewhere.",
6:   "road": [
7:     {
8:       "id": "S1",
9:       "name": "Trustworthy measurements",
10:       "goal": "Every number a backtest or the live engine reads is correct. Until this holds, every 'no edge' verdict is suspect.",
11:       "exit": "B146-B148 closed; volume profile, naked POC and OI fixes live; backtests re-run on fixed data.",
12:       "items": [
13:         "B146",
14:         "B147",
15:         "B148",
16:         "F-BT-09",
17:         "F-BT-14",
18:         "F-BT-10",
19:         "F-BT-11",
20:         "F-BT-12",
21:         "F-BT-20",
22:         "F-BT-21",
23:         "B136",
24:         "B141",
25:         "B059",
26:         "B066",
27:         "F-BT-13"
28:       ]
29:     },
30:     {
31:       "id": "S2",
32:       "name": "Survive the fees",
33:       "goal": "Stops wide enough that a 1m wick does not hit them and fees cost a small fraction of R.",
34:       "exit": "fee_R under 0.25 R on Tom and every traded layer; maker entries modelled and tested.",
35:       "items": [
36:         "F-BT-01",
37:         "F-BT-22",
38:         "T080",
39:         "B118",
40:         "B142",
41:         "B143",
42:         "B144",
43:         "B151",
44:         "B153"
45:       ]
46:     },
47:     {
48:       "id": "S3",
49:       "name": "Find a real edge",
50:       "goal": "At least one source shows net-positive expectancy out of sample, after fees, on fixed data.",
51:       "exit": "Walk-forward (backtest D) net R > 0 with CI above 0 for at least one Tom or layer config.",
52:       "items": [
53:         "T081",
54:         "T082",
55:         "F-BT-08",
56:         "F-BT-02",
57:         "T083",
58:         "T084",
59:         "B117",
60:         "T052",
61:         "B063",
62:         "T055",
63:         "T058"
64:       ]
65:     },
66:     {
67:       "id": "S4",
68:       "name": "Prove it on testnet",
69:       "goal": "The winning configs trade on testnet with real exits, enough trades, the stack up around the clock.",
70:       "exit": "200+ trades from S3 configs, net positive, under 5 % of exits by time-out, uptime over 95 %.",
71:       "items": [
72:         "F-BT-19",
73:         "T085",
74:         "B123",
75:         "B124",
76:         "B121",
77:         "B149",
78:         "B125"
79:       ]
80:     },
81:     {
82:       "id": "S5",
83:       "name": "Go-live gate",
84:       "goal": "A written bar for real money, agreed by the operator, met by S4 numbers.",
85:       "exit": "Operator signs the bar; S4 meets it for 30 days.",
86:       "items": [
87:         "T086",
88:         "T048"
89:       ]
90:     }
91:   ],
92:   "x_tasks": {},
93:   "evidence": [
94:     {
95:       "test": "Tom core backtest",
96:       "result": "Gross -0.15 R before fees (CI -0.29 to +0.04); live rule now finds 0 signals where an older run found 19",
97:       "verdict": "fail",
98:       "src": "B147, TOM_CORE_BT_RERUN"
99:     },
100:     {
101:       "test": "Capture matrix, 34 layer/side rows, 2022-2026",
102:       "result": "0 of 34 reach lift 1.15 at 96 bars; most sit at 1.00 (no better than chance)",
103:       "verdict": "fail",
104:       "src": "bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md"
105:     },
106:     {
107:       "test": "Fabio order-flow model, 64 variants",
108:       "result": "0 net-positive out of sample; gross +0.13 R, fees cost 0.66 R",
109:       "verdict": "fail",
110:       "src": "SUPERVISOR_LOG 2026-09-30 FABIO_OF"
111:     },
112:     {
113:       "test": "Passive (maker) execution, P1",
114:       "result": "Adverse selection +0.02 bp against a ~10 bp fee: maker fills are realistic",
115:       "verdict": "pass",
116:       "src": "SUPERVISOR_LOG 2026-10-06 research agenda"
117:     },
118:     {
119:       "test": "Kim & Hansen imbalance replication, P4",
120:       "result": "8 h window passes; 4 h and 12 h fail sign stability",
121:       "verdict": "partial",
122:       "src": "SUPERVISOR_LOG 2026-10-06 research agenda"
123:     },
124:     {
125:       "test": "Live layers vs backtest parity",
126:       "result": "92-100 % after switching backtests to spot data (was 0-70 % on perp)",
127:       "verdict": "pass",
128:       "src": "FINDINGS F-BT-18"
129:     },
130:     {
131:       "test": "Stop-buffer walk-forward (T081, Tom)",
132:       "result": "Out-of-fold net R negative in all 8 runs; best -0.20 R [-0.28, -0.12] vs -6.6 R with no buffer. Wider stops cut fees, gross R stays negative",
133:       "verdict": "fail",
134:       "src": "T081_STOP_BUFFER_WF_2026-10-09.md"
135:     },
136:     {
137:       "test": "Maker execution model (T080, Tom)",
138:       "result": "Maker entry removes 50 % of fee drag (9.3 -> 4.7 R per trade); net still -4.9 R because gross R is -0.29",
139:       "verdict": "fail",
140:       "src": "T080_MAKER_MODEL_2026-10-09.md"
141:     },
142:     {
143:       "test": "Volume profile fix (F-BT-09)",
144:       "result": "POC now within 50 points of trade-level on 10-06 and 10-07 (was 300-690 off); deployed 2026-10-09 12:46",
145:       "verdict": "pass",
146:       "src": "39520d4, BuildVpWeightTest"
147:     },
148:     {
149:       "test": "turn_of_candle (D01 research)",
150:       "result": "Already one slot; research found no gross edge; pays its fees and nothing else (-11 bp vs 12 bp cost)",
151:       "verdict": "fail",
152:       "src": "TURN_OF_CANDLE_ORIGIN_2026-10-09.md"
153:     }
154:   ],
155:   "health_notes": [
156:     {
157:       "k": "Uptime",
158:       "v": "Gaps",
159:       "s": "warn",
160:       "d": "dark ~23 of the last 120 h; 2-day gap 09-30..10-02 (F-BT-19). Windows sleep is already off; remaining causes are restarts and power. Java engine restarted 2026-10-09 12:46 (2m20s gap)."
161:     },
162:     {
163:       "k": "Hardware",
164:       "v": "WHEA errors",
165:       "s": "bad",
166:       "d": "fatal hardware error every 1-3 days since July, SMART unread (B140)"
167:     }
168:   ],
169:   "changelog": [
170:     {
171:       "date": "2026-10-09",
172:       "what": "Page made: road to profitability, decisions, evidence, ledger, board."
173:     },
174:     {
175:       "date": "2026-10-09",
176:       "what": "Generator moved into the repo; refreshed daily from the real files."
177:     },
178:     {
179:       "date": "2026-10-09",
180:       "what": "Inbox added: paste questions, tasks and requirements word for word; Claude replies under each."
181:     },
182:     {
183:       "date": "2026-10-09",
184:       "what": "Road tasks filed as registry rows T080-T086; the board now shows their real status."
185:     },
186:     {
187:       "date": "2026-10-09",
188:       "what": "Pickup: D01-D07 applied, D08-D10 asked; T080/T081 results added to Evidence; F-BT-09 and F-BT-14 shown as closed; go-live bar written (T086)."
189:     },
190:     {
191:       "date": "2026-10-10",
192:       "what": "Decluttered: only decisions waiting on you show as cards (applied ones fold to one line each); Evidence, Testnet ledger, Board and How-it-works start collapsed; long inbox items fold to 200 characters (full text one tap away); the changelog shows the 3 newest."
193:     },
194:     {
195:       "date": "2026-10-10",
196:       "what": "New Backlog section: the tasks waiting to run, with their lane and size and what each still needs before it is ready. Move to top, Hold, Drop and Approve Opus are buttons here; Claude applies them at the next pickup."
197:     },
198:     {
199:       "date": "2026-10-12",
200:       "what": "Every Inbox item now shows its status, Claude's reply and where it was filed. An item with no registry row yet says 'received, no registry row yet' instead of showing nothing (B181)."
201:     },
202:     {
203:       "date": "2026-10-12",
204:       "what": "New Layer Board section under the road: one line per layer being worked on (stage, indicators, setups, open rows, next step, source file). 'not recorded' means no committed file states it. Layout waits for your approval (B177)."
205:     }
206:   ],
207:   "finding_closed": {
208:     "F-BT-09": "fixed 39520d4, deployed 2026-10-09 12:46 (POC within 50 of trade level)",
209:     "F-BT-14": "writer added 39520d4, deployed 2026-10-09 12:46; Sep-Oct backfilled"
210:   },
211:   "layers": [
212:     {
213:       "id": "tom-v2",
214:       "name": "Tom (v2 redefinition)",
215:       "stage": "spec",
216:       "indicators": "profile shape P/b, inside bar, ledge of old highs, liquidity above (his reasons, not yet in the code)",
217:       "setups": "7 chart-verified DAX trades; coded Tom fired on 0 of 7; families not recorded",
218:       "rows": [
219:         "B146",
220:         "B147",
221:         "T052"
222:       ],
223:       "next": "tom-holdout-clean-split, then tom-layer-v2-spec (Opus)",
224:       "src": "MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md:9"
225:     },
226:     {
227:       "id": "fabio-v2",
228:       "name": "Fabio (v2 redefinition)",
229:       "stage": "spec",
230:       "indicators": "not recorded",
231:       "setups": "not recorded",
232:       "rows": [
233:         "T084",
234:         "B123"
235:       ],
236:       "next": "fabio-ledger-minute-timestamps, then fabio-layer-v2-spec (Opus)",
237:       "src": "MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md:44"
238:     },
239:     {
240:       "id": "turn-of-candle",
241:       "name": "turn_of_candle",
242:       "stage": "live-testnet",
243:       "indicators": "not recorded",
244:       "setups": "not recorded",
245:       "rows": [],
246:       "next": "your yes/no on F-BT-02 (it failed its backtest)",
247:       "src": "MyTradingSys/system/PROJECT_MAP.md:97"
248:     },
249:     {
250:       "id": "wavetrend",
251:       "name": "WaveTrend",
252:       "stage": "parked",
253:       "indicators": "WaveTrend with Crosses [LazyBear]",
254:       "setups": "not recorded",
255:       "rows": [
256:         "T061"
257:       ],
258:       "next": "no new layers while Tom/Fabio are redefined",
259:       "src": "MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md:27"
260:     }
261:   ]
262: }
```
