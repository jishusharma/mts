# FORMULAS.md — canonical formula definitions for the indicator layers

Purpose: every formula used by `layers/rsi`, `layers/timeframe`, `layers/cryptocred` and
`layers/runner.py` (plus the `bt/bt_stats.py` / `bt/ref_pbo.py` metrics used to score them) gets ONE
chosen definition here, its canonical source, the known variants and why we picked ours, and a tiny
worked example. Every TEST_PLAN.md in these layers must derive its expected numbers from this file,
never from an implementation module (see LESSONS_LEARNED.md 2026-09-28 D1: `layers/rsi/TEST_PLAN.md`
Case C1 was originally derived from `bt/bt_rsi.py.new`'s `rsi_wilder`, which is off vs textbook Wilder).

## 1. RSI (Wilder, `rsi_core.rsi_wilder`)

**Chosen definition (textbook Wilder = TradingView `ta.rsi`):**
1. `delta[i] = close[i] - close[i-1]` for `i = 1..len-1`.
2. Seed at index `period`: `avg_gain = mean(max(delta,0) for delta in delta[0:period])`,
   `avg_loss = mean(max(-delta,0) for delta in delta[0:period])` (a plain SMA seed over the first
   `period` deltas — NOT the first `period` closes).
3. Wilder-smooth every index after the seed: `avg_gain = (avg_gain*(period-1) + gain[i]) / period`,
   `avg_loss = (avg_loss*(period-1) + loss[i]) / period`, where `gain[i]=max(delta[i],0)`,
   `loss[i]=max(-delta[i],0)`.
4. `rs = avg_gain / avg_loss`; `rsi = 100 - 100/(1+rs)`. If `avg_loss == 0`: `rsi = 100` when
   `avg_gain > 0`, else `rsi = 50` (flat series, no gains or losses at all).
   DELIBERATE DEVIATION (supervisor 2026-09-28): TradingView's ta.rsi returns 100 whenever down == 0,
   including a flat series. We return 50 for flat (neutral, no momentum). Only reachable on a perfectly
   flat window; any cross-check vs TradingView must skip that case.
5. Indices `0..period-1` are `None` (not enough data for a seed).

**Canonical source:** J. Welles Wilder, *New Concepts in Technical Trading Systems* (Trend Research,
1978) — RSI = 100 - 100/(1+RS), RS = avg gain / avg loss over the period, subsequently smoothed with
Wilder's own recursive average (equivalent to an EMA with `alpha = 1/period`, i.e. `N = 2*period-1` in
plain-EMA terms). Cross-checked against TradingView's Pine v5/v6 reference: `ta.rsi(source, length)` is
documented as `up = ta.rma(math.max(change(close),0), length)`, `down = ta.rma(-math.min(change(close),0),
length)`, `rsi = 100 - 100/(1 + up/down)`, and `ta.rma` is Wilder's recursive smoothing seeded by a plain
average of the first `length` values (TradingView Pine Script Reference Manual, `ta.rsi`/`ta.rma`
entries, pine-script-docs/v5+v6, https://www.tradingview.com/pine-script-reference/v5/).

**Known variants and why we picked ours:**
- *Cutler's RSI* uses a plain SMA of gains/losses throughout (no recursive smoothing) — rejected, not
  what "RSI" means on TradingView/most platforms, and not what MalkanView's 40/60 rule assumes.
- *EMA-seeded-from-first-value* Wilder variants (seed = first delta, not an SMA of `period` deltas) —
  rejected; diverges from Wilder's own worked example and from `ta.rma`'s documented seeding.
- `bt/bt_rsi.py.new`'s `rsi_wilder` IS off, confirmed by this audit: its seed divides
  `sum(gains)/len(gains)` and `sum(losses)/len(losses)` — i.e. by the COUNT OF NONZERO up-moves /
  down-moves among the first `period` deltas — instead of dividing by `period` as steps 2-3 above
  require (down-moves silently drop out of the gain average's denominator, and vice versa). Worked
  example, period=5, closes=[100,102,101,103,106,105,107,110,108,...]: deltas[0:5]=[2,-1,2,3,-1];
  textbook seed = avg_gain=(2+0+2+3+0)/5=1.4, avg_loss=(0+1+0+0+1)/5=0.4; `bt_rsi.py.new`'s buggy seed =
  avg_gain=(2+2+3)/3=2.3333, avg_loss=(1+1)/2=1.0 — a materially different RSI from index `period`
  onward (the recursive smoothing after the seed is correct Wilder, so the error is confined to, and
  persists from, the seed). This is why `rsi/TEST_PLAN.md` Case C1 explicitly says "NOT bt_rsi.py.new,
  which is off" and why spec 073 was corrected (see the audit report) to stop telling a worker to
  "reuse `rsi_regime`'s EXACT algorithm" from that file — `rsi_regime` itself (the 40/60 window
  classifier) does not depend on `rsi_wilder`'s seeding and is unaffected, but the instruction's
  phrasing risked normalizing "copy from bt_rsi.py.new" as a pattern for future specs touching RSI math.

**Worked example (period=3):** closes = [10, 12, 11, 14]. deltas = [2, -1, 3]. Seed: gains=[2,0,3] over
3 deltas -> avg_gain=(2+0+3)/3=1.6667, losses=[0,1,0] -> avg_loss=(0+1+0)/3=0.3333. rs=5.0,
rsi[3] = 100 - 100/6 = 83.3333.

## 2. RMA / SMMA (`rsi_ma` type="RMA")

**Chosen definition:** `alpha = 1/length`. Seed = SMA of the first `length` available (consecutive,
non-None) input values. Subsequent: `rma[i] = (x[i] - rma[i-1]) * alpha + rma[i-1]`.

**Canonical source:** Wilder 1978 (this is literally Wilder's smoothing method, generalized to any
input series, not just gain/loss); TradingView `ta.rma(source, length)` reference confirms the same
SMA-seed-then-recursive-average behavior (pine-script-docs, `ta.rma`).

**Variant note:** some libraries seed RMA with the first raw value instead of an SMA of `length` values
— rejected for the same reason as the RSI seeding variant above (diverges from Wilder's and Pine's
documented seed).

**Worked example (length=3):** x = [50,55,45]. Seed = (50+55+45)/3 = 50.0. Next x=60:
rma = (60-50)/3+50 = 53.3333.

## 3. SMA (`rsi_ma` type="SMA")

**Chosen definition:** plain arithmetic mean of the last `length` consecutive non-None values ending at
`i`; `None` if fewer than `length` consecutive values are available.

**Canonical source:** universal definition; cross-checked against TradingView `ta.sma(source, length)`
(pine-script-docs, `ta.sma`), which is the same rolling arithmetic mean, no variants to choose between.

**Worked example (length=3):** [50,55,45] -> 50.0.

## 4. EMA (`rsi_ma` type="EMA"), including seeding

**Chosen definition:** `alpha = 2/(length+1)`. Seed = SMA of the first `length` available values (same
seeding convention as RMA above, for consistency within this codebase's `rsi_ma` module — see variant
note). Subsequent: `ema[i] = (x[i] - ema[i-1]) * alpha + ema[i-1]`.

**Canonical source:** standard EMA formula (`alpha = 2/(N+1)`); TradingView `ta.ema(source, length)`
reference (pine-script-docs, `ta.ema`) documents the same alpha and an SMA-style seed for the first
value.

**Known variants and why we picked ours:** two seeding conventions are common — (a) SMA-seeded (first
`length` values averaged, then EMA recursion starts at index `length-1`), used here; (b) "EMA from the
first raw value" (`ema[0] = x[0]`, recursion starts immediately) — common in some charting libraries
(older TA-Lib EMA) but produces a materially different early-series value and complicates cross-checking
against SMA/RMA in the same module (`rsi_ma` supports SMA/WMA/EMA/RMA switched by a single `type` param;
using the same "SMA seed, first `length` values needed" contract for all four keeps their None-prefix
identical, which the rsi_ma implementation and its tests rely on). We picked (a) for internal consistency
and because it matches the TradingView-anchored convention used for RSI/RMA above.

**Worked example (length=3):** x=[50,55,45,60]. Seed(idx of 45)=SMA([50,55,45])=50.0. Next x=60:
ema=(60-50)*0.5+50=55.0 (alpha=2/4=0.5).

## 5. WMA (`rsi_ma` type="WMA")

**Chosen definition:** linearly increasing weights `1..length` applied oldest-to-newest over the last
`length` consecutive values: `wma[i] = sum(w_k * x[i-length+1+k-1] for k in 1..length) / sum(1..length)`.

**Canonical source:** standard WMA; TradingView `ta.wma(source, length)` reference (pine-script-docs,
`ta.wma`) documents the identical oldest-gets-least-weight linear weighting.

**Variant note:** no material variants for linear WMA weighting (some libraries reverse the weight
order, i.e. newest = weight 1 — rejected, contradicts Pine's `ta.wma` and every mainstream charting
platform's convention of "recent bars matter more").

**Worked example (length=3):** [50,55,45], weights [1,2,3]: (50*1+55*2+45*3)/6 = 295/6 = 49.1667.

## 6. Tolerance-band level/line events (`rsi_events.rsi_events`)

**Chosen definition:** generic level-touch state machine over any numeric series vs a `level` +/-
`tolerance` band. See `layers/rsi/TEST_PLAN.md` "rsi_events.py" section for the full mechanical
specification (side classification, run tracking, `support`/`rejection`/`failure`/`cross` semantics,
`None`-skipping for warm-up/gap bars, penetration and `t` conventions). This is a repo-original
mechanical definition (not from an external technical-analysis text) built to formalize "price touches
a level and either holds or breaks" for RSI 40/60/70/30 zones and cc_retest-style level interactions; no
external canonical source applies. Re-derived independently for this audit (see Case E1 below) by
implementing the state machine directly from the TEST_PLAN's prose, without reading `rsi_events.py`'s
source, and the result matches the plan's expected event list exactly.

## 7. Forward return / MAE (`layers/runner.py`)

**Chosen definition:** for an event at index `i` with side sign `sgn` (+1 long, -1 short) and horizon
`h`: `ret = sgn * (closes[i+h] - closes[i]) / closes[i]` (only when `i+h < len(closes)`, else the event
contributes nothing at that horizon — insufficient data, not a zero). `mae` (max adverse excursion) at
horizon `h` = the minimum of `sgn * (closes[j]-closes[i])/closes[i]` over `j in [i+1, min(i+h,len-1)]`
(the worst point reached on the way to the horizon, close-only in this hand-derivable form; production
code should prefer intrabar high/low when available — documented as a scope note in
`layers/TEST_PLAN_runner.md`, not tested there). `hit_rate` = fraction of contributing events with
`ret > 0`. Aggregates (`mean_return`, `mae`) average only over events with data at that horizon.

**Canonical source:** standard "forward return" / "event study" methodology used throughout quant
research (see e.g. Lopez de Prado, *Advances in Financial Machine Learning*, triple-barrier /
event-based labeling chapters, for the general pattern of measuring returns and adverse excursion from
a fixed event index over a fixed horizon); the specific close-only MAE simplification here is a
documented scope reduction of that general idea, not a claim that it matches any one textbook formula
verbatim.

## 8. Resample / OHLCV aggregation + bucket anchoring (`layers/timeframe/tf_resample.py`)

**Chosen definition:** see `layers/timeframe/TEST_PLAN.md` for the full boundary-math and aggregation
spec (seconds/days/week/month bucket anchoring, closed-bars-only rule, gap counting). Bucket math is
plain UTC calendar/epoch arithmetic (`floor` division for seconds/day-multiples, Monday-anchored ISO
week via `epoch_day % 7`, first-of-calendar-month for `1M`) — this is a mechanical/engineering choice
(Binance-compatible UTC bucketing), not drawn from a named external formula; cross-checked against
Python's own `datetime`/`timezone.utc` arithmetic (stdlib is the "canonical source" here). OHLCV
aggregation is the universal convention: `o` = first bar's open in the closed window, `c` = last bar's
close, `h` = max high, `l` = min low, `v` = sum of volumes; a bucket is only emitted once
`bucket_end <= last_bar_close_ms` (never a partial trailing bucket).

## 9. CryptoCred swing / MSB / retest / R-target math (`layers/cryptocred/*`)

Source: `MyTradingSys/research/cross_trader_consolidated.md` cluster C08 (MSB Definition &
Significance), C07 (Retests) and C10 (Setup Types) — these are verbatim-quote-verified transcript
extracts (per repo convention, higher confidence than the Malkan web research), and the module
docstrings already cite the specific rule IDs (C08-Rule1, C08-E01/E03/E05, C07-E01/E04/E05, C10-E01/
E02/E03/E04/E05). No external canonical formula exists for these (they are one trader's discretionary
rules mechanized); this repo's own interpretation choices are documented at the top of
`cc_structure.py`, `cc_retest.py` and `cc_setups.py` and restated in `layers/cryptocred/TEST_PLAN.md`.
Independently re-derived for this audit directly from those docstrings' prose (fixed-width fractal swing
detection with strict `>`/`<` comparisons against both side-windows; MSB = a close beyond the most
recent opposing swing, gated by "lower-high"/"higher-low" prior sequence when `require_prior_sequence`;
retest = price re-touches the broken level within `tolerance_pct` before invalidating past
`invalidate_pct`, scanned bar-by-bar from `confirm_i`; R-target = `entry +/- target_r * |entry - stop|`
in the trade's profit direction) — see Cases S1-S7/R1-R5/U1-U6 below, all reproduced exactly.

## 10. bt_stats / ref_pbo metrics (Sharpe, PSR/DSR, PBO)

**Sharpe (`bt/bt_stats.py:sharpe`, `bt/ref_pbo.py:sharpe`):** `mean(x) / population_stdev(x)` (divides
by `n`, not `n-1` — population, not sample, standard deviation; both modules agree on this choice).
Canonical source: standard Sharpe ratio (reward per unit of volatility); the population-vs-sample choice
here follows Bailey/Lopez de Prado's PBO paper's own convention of dividing by the realized in-sample
`N`, not `N-1`, when comparing strategy variants over a fixed block of returns.

**PSR / DSR (`bt/bt_stats.py:psr,dsr,expected_max_sr`):** Probabilistic Sharpe Ratio / Deflated Sharpe
Ratio per Bailey & Lopez de Prado, "The Sharpe Ratio Efficient Frontier" (2012) and the DSR literature —
`psr = Phi((SR - SR*) * sqrt(T-1) / sqrt(1 - skew*SR + (kurtosis-1)/4 * SR^2))`; `dsr` substitutes
`SR* = expected_max_sr(var_sr, n_trials)` (the expected maximum Sharpe ratio achievable by chance over
`n_trials` independent strategy variants, via the Euler-Mascheroni-constant expression for the expected
max of `n_trials` standard normals). Matches the implementation in both files exactly.

**PBO / CSCV (`bt/bt_stats.py:pbo_cscv`, `bt/ref_pbo.py:ref_pbo_cscv`):** Combinatorially Symmetric
Cross-Validation per David H. Bailey, Jonathan Borwein, Marcos López de Prado, Qiji Jim Zhu, "The
Probability of Backtest Overfitting," Journal of Computational Finance (2015; SSRN 2326253,
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253) — split the return matrix into `S` equal
contiguous blocks, form every equal-size in-sample/out-of-sample split (`C(S, S/2)` combinations), pick
the in-sample-best variant `n*` per split, compute its out-of-sample relative rank `w = (count(oos[n] <
oos[n*]) + 1)/(N+1)`, `logit = ln(w/(1-w))`; `PBO` = fraction of splits where `logit <= 0` (the
in-sample winner underperforms the OOS median). `ref_pbo.py` is the deliberately independent
re-implementation of `bt_stats.py:pbo_cscv` used by `test_ref_pbo.py` as a cross-check — both were
inspected for this audit and agree on the CSCV algorithm and the Sharpe convention (population stdev).

## 11. Execution math (`execution/plan_compiler.py`, `execution/executor.py`,
`execution/risk_guard.py`) — canonical Deribit BTC-PERPETUAL inverse-contract math

All definitions derived from Deribit's published BTC-PERPETUAL contract spec (Deribit Exchange
documentation, "BTC-PERPETUAL" instrument page: tick size 0.5 USD, contract size / minimum trade
amount 10 USD, inverse contract settled/margined in BTC) and from first-principles inverse-contract
PnL algebra — NOT from reading `plan_compiler.py`/`executor.py`.

**11.1 Tick-size price snapping — directional, by order purpose and side (Opus review R2: the earlier
round-half-to-even version was REJECTED for being a definition borrowed from Python's `round()` rather
than from risk direction, and for ignoring which way rounding a given order should go).** Deribit
BTC-PERPETUAL quotes in 0.5 USD increments; every order price must be an exact multiple of the tick.
There is no single tick-snap rule — the direction depends on what the price IS, from first principles
(never accept a worse fill than planned; never let a stop realize a bigger loss than budgeted; make a
target more likely to fill, not less):
- **Entry (limit or ladder rung):** BUY -> `floor` (never pay MORE than the planned price), SELL ->
  `ceil` (never sell for LESS than the planned price).
- **Stop:** LONG stop (below entry) -> `ceil`, i.e. rounds UP, toward entry (a stop that rounded further
  DOWN would be further from entry, i.e. a BIGGER loss than budgeted). SHORT stop (above entry) ->
  `floor`, toward entry, for the same reason (mirrored). In both cases: **the loss can never exceed the
  budget the plan computed.**
- **Target:** LONG target (above entry) -> `floor`, toward entry (a target further from entry, i.e.
  rounded UP, is less likely to be reached/filled than one closer to entry). SHORT target (below entry)
  -> `ceil`, toward entry (mirrored). In both cases: **rounding toward entry makes the target more
  likely to fill at the stated price or better, never less likely.**

Implementation: exact Decimal tick arithmetic (not float + epsilon), so the boundary is exact regardless
of binary floating-point representation error: convert `price` and `tick` to `Decimal` via `Decimal(str(x))`
(never `Decimal(x)` directly on a float, which would import the float's own binary imprecision), divide,
then `.to_integral_value(rounding=ROUND_FLOOR)` or `ROUND_CEILING` per the direction above, then multiply
back by `tick`. (A `math.floor(price/tick + 1e-9)*tick` epsilon-nudge is an acceptable float-only
alternative but was not the one chosen here — Decimal was, since it has no epsilon to get wrong.)

Worked examples, `tick=0.5`: `price=50000.1` (just above the 50000.0 tick) -> `floor=50000.0`,
`ceil=50000.5`. `price=50000.49` (just below the 50000.5 tick) -> `floor=50000.0`, `ceil=50000.5`.
`price=50000.0` (exact tick) -> `floor=ceil=50000.0` (no-op either direction).

**11.2 Contract size (amount) rounding — floor only, reject below minimum (Opus review R2: the earlier
`max(10, round(amount/10)*10)` was REJECTED — forcing a too-small size UP to the 10 USD minimum can
trade MORE size, and take MORE risk, than the plan's own risk budget calls for).** Minimum trade amount
is 10 USD, in 10 USD increments. Canonical definition: floor `amount` to the nearest 10 USD multiple
(same Decimal `ROUND_FLOOR` approach as 11.1, never rounds up); if the floored size is below 10 USD, the
plan is REJECTED (raise, do not silently substitute 10). Source: Deribit BTC-PERPETUAL "Minimum Trade
Amount" = 10 USD. Worked examples: `amount=25` -> `25/10=2.5` -> floor -> `2` -> `20` (not `30`, and not
banker's-rounded to `20` either — floor always rounds down regardless of the fractional part).
`amount=29.9` -> floor -> `20`. `amount=9` -> floors to `0` USD, below the 10 USD minimum -> REJECTED
(the plan cannot be traded at this risk budget; forcing it up to 10 would silently exceed that budget).

**11.3 Ladder entry rung prices.** For an N-rung ladder over `[low, high]` with even spacing
`step=(high-low)/(N-1)` (N=1 uses a single rung), first-principles convention (best price is the one
first touched moving away from the current market toward the range): for a LONG ladder (buying on a
pullback) rung 1 = `high` (nearest/best), each subsequent rung steps down by `step` to rung N = `low`
(worst, deepest fill); for a SHORT ladder this is mirrored, rung 1 = `low`, stepping up to rung N =
`high`. This is a design convention (not an exchange rule) documented here so ladder tests derive from
it rather than from the module.

**11.4 Ladder / multi-fill average price for an inverse contract — harmonic mean weighted by USD
size.** For an INVERSE contract (Deribit BTC-PERPETUAL: each contract is a fixed 1 USD of notional;
the quantity of BTC bought/sold at price `p` for a `size`-USD fill is `size/p` BTC, NOT `size*p` USD of
BTC), the correct volume-weighted average price across fills `(p_i, size_i)` is the harmonic mean
weighted by USD size, not the arithmetic mean:
`avg_price = sum(size_i) / sum(size_i / p_i)`
Derivation: total BTC acquired = `sum(size_i/p_i)`; total USD notional = `sum(size_i)`; the single
price that would have produced the same BTC quantity for the same total USD notional is
`total_USD / total_BTC = sum(size_i) / sum(size_i/p_i)`, i.e. the weighted harmonic mean. The
plain notional-weighted arithmetic mean `sum(p_i*size_i)/sum(size_i)` is the correct formula for a
LINEAR contract (fixed BTC quantity per contract) but is WRONG for Deribit's inverse contract, per
Deribit's own inverse-contract PnL documentation ("Perpetual and Futures Contract Specifications" /
"Trading Guide — Inverse Futures": PnL and average entry for inverse contracts are computed via
`1/price` quantities, not `price` quantities directly). Worked example (4-rung ladder, sizes
`[10,10,20,30]` USD, snapped prices `[50200, 50050, 49900, 49750]`): harmonic mean =
`70 / (10/50200 + 10/50050 + 20/49900 + 30/49750) = 70 / 0.0014028201.. = 49899.49` (rounded to 2dp),
versus the arithmetic mean `sum(p*s)/sum(s) = 3493000/70 = 49900.00` — a real, if small, discrepancy
that grows with wider price ranges or larger size skew across rungs.

**11.5 Inverse-contract average fill price (live fills).** Same formula as 11.4, applied to actual
exchange fills as they arrive: `avg_fill = filled_total_usd / sum(fill_amount_i / fill_price_i)`. This
is the correct live-fill analogue of 11.4 and must use the same harmonic-mean-weighted-by-USD-size
definition — a plan-compile-time estimate (11.4) and a live-fill computation of the same quantity must
not silently use two different formulas.

**11.6 Worst-case loss at a fixed-percent stop (inverse contract).** For a LONG position of `size` USD
opened at average entry `E`, with a stop at `S = E*(1-pct)` (LONG) or `S = E*(1+pct)` (SHORT), the
inverse-contract PnL in BTC is `size*(1/E - 1/S)` for a LONG close (and the mirror for SHORT); converting
to USD at the exit price `S` gives `PnL_usd = size*(1/E - 1/S)*S = size*(S/E - 1) = size*(S-E)/E`. Taking
the stop side this is always a loss, so:
`worst_case_loss_usd = -size * abs(E - S) / E`
(equivalently `-size*pct` when `S` is not tick-snapped; snapping `S` introduces a small residual). This
is the standard inverse-contract linear PnL approximation (exact for a single close at the stop price,
using the stop price itself as the BTC-to-USD conversion rate) per Deribit's inverse-contract PnL
formula. Worked example: `size=70`, `E=49899.49` (11.4's harmonic mean), `pct=2%`, LONG (stop snaps `ceil`, 11.1)
-> `S_raw = 49899.49*0.98 = 48901.50002..` -> snapped `S=48901.5` -> `loss = -round(70*abs(49899.49-48901.5)/49899.49, 2)
= -round(70*997.99/49899.49, 2) = -round(1.4004.., 2) = -1.40` USD.

NOTE: `worst_case_loss_usd` is the loss realized AT the stop price only — it excludes stop-market
trigger slippage (the actual fill can be worse than the trigger once the market order the stop becomes
is filled) and exchange fees. It is a floor on planning risk, not a guarantee of the maximum possible
real-world loss.

**11.7 Target price from PnL%.** Inverting 11.6's relation for a target instead of a stop: a desired
USD PnL of `+pct%` of the position's USD size at exit price `T` satisfies `size*(T-E)/E = size*pct/100`
(LONG) -> `T = E*(1+pct/100)`, mirrored to `T = E*(1-pct/100)` for SHORT. Same formula shape as the stop
in 11.6, opposite sign convention, then tick-snapped TOWARD entry per 11.1 (LONG target -> `floor`,
SHORT target -> `ceil` — the opposite direction from the stop, which also snaps toward entry but for the
opposite reason: capping loss rather than raising fill probability). This is the same computation done in two
places (`plan_compiler.py` at compile time from the ladder estimate, `executor.py` at fill time from
the real average fill) and per 11.5 both must use the same `E` definition (11.4/11.5's harmonic mean).

**11.8 Notional cap.** Account-wide notional exposure check: for a size already expressed in USD
notional (Deribit BTC-PERPETUAL "size"/"amount" fields are USD-denominated), `notional = abs(size)`
directly, with no price multiply, when the caller has already confirmed `size` is USD (the
`mark_price=None` branch); when `size` is in BTC/contracts needing conversion, `notional =
abs(size) * mark_price`. Source: Deribit position/ticker API — BTC-PERPETUAL position `size` is
reported in USD; the `mark_price`-multiply branch exists only for instruments/fields that are NOT
already USD-denominated. A projected notional `current + new` that exceeds the account cap
(`MAX_ACCOUNT_NOTIONAL_USD`) is a breach; no formula ambiguity here, just a units contract that the
caller must get right (this is a documentation gap, not a math bug, per FORMULA_INVENTORY.md's "mark
None -> assumes USD units" flag).

## 12. Core ATR — operator decision: plain SMA, not Wilder (2026-09-28)

**Canonical True Range definition** (J. Welles Wilder, *New Concepts in Technical Trading Systems*,
1978): `TR[i] = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))` for `i>=1`
(undefined at `i=0`, no prior close).

**Operator decision (2026-09-28):** MTS's core ATR (`SetupCandidatesBuilder.java`,
`averageTrueRange`) is a PLAIN (simple, unweighted) arithmetic average of `TR` over the lookback
window, `ATR[n] = mean(TR[i] for i in window of size n)` — explicitly NOT Wilder's recursive/RMA
smoothing (contrast with section 1's RSI, which IS full Wilder `ta.rma` smoothing). This is a
deliberate choice for MTS's core (Tom's method), confirmed by the operator on 2026-09-28; it must not
be silently changed to Wilder smoothing by a future worker who assumes "ATR" implies Wilder by default.

**Worked example (plain SMA, period=3):** highs=[10,11,12,11], lows=[9,9,10,9], closes=[9.5,10.5,11.5,10].
`TR[1]=max(11-9, |11-9.5|, |9-9.5|)=max(2,1.5,0.5)=2`. `TR[2]=max(12-10,|12-10.5|,|10-10.5|)=max(2,1.5,0.5)=2`.
`TR[3]=max(11-9,|11-11.5|,|9-11.5|)=max(2,0.5,2.5)=2.5`. `ATR = mean(TR[1..3]) = (2+2+2.5)/3 = 2.1667`
(plain average — Wilder recursive smoothing over the same window, for comparison, would instead need a
seed plus `(prev*(n-1)+TR)/n` recursion and is NOT what MTS core computes).

## 13. T055 shared cost model (`layers/positioning/trade_costs.py`) - added 2026-09-29

Applies to C1, C2, C3 below. Binance USDT-M perp: taker fee 10 bps round trip (0.0010), realistic slippage
added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b "SCALPING FEE FLOOR",
internal arithmetic). Funding: a position pays `side_sign * rate` (as a fraction of notional, entry notional
used) for every funding record with `t_in < calc_time <= t_out`; `side_sign` = +1 long, -1 short, so longs
pay positive rates and shorts receive them (Binance perpetual funding convention).
`gross = side_sign * (p_out - p_in) / p_in`;
`net = gross - fee_rt - slip_rt - side_sign * sum(rate over records in (t_in, t_out])`.
Worked: long 100 -> 101, funding records at t=8h rate 0.0001 and t=16h rate 0.0003, t_in=0, t_out=16h:
`net = 0.01 - 0.0010 - 0.0002 - 0.0004 = 0.0084`. Short 100 -> 99, same records: gross = 0.01,
funding term = -1 * 0.0004 = -0.0004, `net = 0.01 - 0.0012 + 0.0004 = 0.0092`.

## 14. T055 C1 - funding-extreme reversion + CVD/price divergence fade (`layers/positioning/funding_cvd_fade.py`)

Sources: funding-extreme reversion T2, Memon 2026 (7y Binance) via `research/whale_positioning_evidence_2026-09-12.md`
(the percentile threshold is NOT given there: UNDEFINED in source, so it is a grid parameter); mechanism
He/Manela/Ross/von Wachter arXiv 2212.06888 (T2); CVD/price divergence = same CVD as `bt_data.cvd_delta`
(section above, `delta = 2*tbv - v`, running sum). Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme).
- Funding percentile: for the k-th funding record (k >= lookback-1), `pct[k] = count(w <= r_k) / lookback`
  where `w = rates[k-lookback+1 .. k]` (inclusive of the current record, `r_k = rates[k]`).
- Funding known at bar time: latest record with `calc_time <= bar["t"]` (no look-ahead).
- Divergence at bar i >= n on closes `c` and `cvd`: bearish if `c[i] > max(c[i-n..i-1])` and
  `cvd[i] < max(cvd[i-n..i-1])`; bullish if `c[i] < min(c[i-n..i-1])` and `cvd[i] > min(cvd[i-n..i-1])` (strict).
- Signal: short if bearish AND `pct >= hi`; long if bullish AND `pct <= lo`. Funding-only variant: one event per
  funding record at the first bar with `t >= calc_time`; short if `pct >= hi`, long if `pct <= lo`.
- Defaults (all UNDEFINED in source, grid-searched IS only): lookback 90 records, n 20, hi 0.95, lo 0.05.
- Costs: section 13. Kill (T055a H2 / T055b): OOS Sharpe < 0.3 or too few events. Data: funding exists 2025-09 on only.

## 15. T055 C2 - intraday session momentum (`layers/session/session_momentum.py`)

Source: Shen, Urquhart, Wang, *Financial Review* 57(2), 319-344, 2022, DOI 10.1111/fire.12290 (T1): the first
half-hour return predicts the last half-hour return (liquidity-provision mechanism). The T055b report words it as
"first-half-session return biases rest-of-session"; both entries are supported via `entry_min`.
- Session start `S` = UTC midnight of the bar's day + `session_start_min` minutes. Window end `E = S + first_min` min.
- `r_first = close(last bar with t + bar_ms <= E) / open(first bar with t >= S) - 1`; needs both bars to exist.
- Side = long if `r_first > min_abs`, short if `r_first < -min_abs` (else no event). Entry at the close of the
  bar with `t + bar_ms == S + entry_min` min (event index i = that bar; runner enters at `closes[i]`).
  `entry_min = first_min` gives "rest of session"; `entry_min = session_len - 30` gives the paper's "last half-hour".
- Defaults (adaptation to 24/7 BTC, UNDEFINED in source): session_start_min 0 (UTC day), first_min 30, min_abs 0.
- Costs: section 13. Kill (T055b): effect sign-flips or vanishes post-2023.

## 16. T055 C3 - turn-of-candle (`layers/turn_of_candle/turn_of_candle.py`)

Source: Shanaev, Vasenin, Stepanov, *Heliyon*, PMC10015199 (T1): returns concentrate at the opening of 15-minute
candles (minutes 0, 15, 30, 45 of the hour). The paper has no cost model.
- On 1-minute bars: `mq = (t_ms // 60000) % 15` (minute-of-quarter; epoch-aligned, 15 divides 60). Per-bar
  return `(c - o) / o`. `turn_mean` = mean return of bars with `mq == 0`; `other_mean` = mean of the rest;
  `by_minute[m]` = mean return of bars with `mq == m`.
- Event: at bars with `mq == 15 - lead_minutes` (enter at that bar's close, i.e. just before the candle opens),
  side fixed by parameter (`long`, `short`); direction of the effect is NOT stated in the report, so both are
  grid-searched IS only, and the sign of `turn_mean` is reported.
- Costs: section 13. Fee floor 10 bps RT vs a per-minute effect: expected to fail unless gross edge is large.
  Kill (T055b): net-of-cost edge does not survive on >= 2 OOS years.

---

## 17. B070 net R:R fee model (`runtime/mts_math.py` calculate_net_rr, `ExecutionMathConstants.netRR`) - added 2026-10-03

Operator ruling (a), 2026-10-03: replaces the flat `net = gross * 0.75` (no trader source). Source of the fee: `backtest/fees.py`
DERIBIT_TAKER = BINANCE_TAKER = 0.0005 per side, both legs taker (stop and entry are market). `cost = 2 * taker * entry`
(price units). `net_rr = (|target - entry| - cost) / (|entry - stop| + cost)`; stop == entry -> 0.0.
Worked: entry 100, target 104, stop 98: cost 0.1, net = 3.9 / 2.1 = 1.8571. Tight stop: entry 100, target 100.3, stop 99.9:
cost 0.1, net = 0.2 / 0.2 = 1.0 (gross 3.0). The Java constant must equal fees.py (`tests/test_b070_fee_parity.py`).

## 18. Anchored volume profile touch study (`backtest/vp_pivot_probe.py`) - added 2026-10-09

Context: `research/vp_pivots_2026-10-09/SOURCES.md` and `PLAN.md`. Tom draws a composite profile "from the last major
high to the last major low" (sQ_biBKhPVU:19); the engine anchors every profile to a UTC calendar boundary. This section
defines the mechanical pieces of the offline probe. Everything marked NO-SOURCE is a measurement choice or the pivot
definition, flagged and not tuned.

**18.1 Profile of a bar set (bin grid w = 10.0 USD, NO-SOURCE, engine uses about 5 USD).** Bin k covers `[k*w, (k+1)*w)`.
A bar `(l, h, v)` with `h > l` adds `v * overlap([l,h],[k*w,(k+1)*w)) / (h - l)` to bin k (uniform spread over its
high-low; the engine instead uses triangular weights around the typical price, an accepted difference because every
family in the probe goes through the same builder). A bar with `h == l` adds all of `v` to bin `floor(l/w)`.
POC = lowest bin holding the maximum volume (ties go to the lower bin, as the engine's `Stream.max` keeps the first
key). `poc_price = k_poc*w + w/2`. Value area = 70% (engine `VALUE_AREA_PCT`; Tom: "70% of the trades",
1utSjHs_Mq8:19): start `lo = hi = k_poc`, `acc = vol[k_poc]`; while `acc < 0.70 * total` and bins remain: `vl = vol[lo-1]`
(or -1 if `lo` is the first bin), `vh = vol[hi+1]` (or -1 at the last bin); if `vl >= vh` and `lo` is not the first
bin take `lo-1`, else take `hi+1` (else `lo-1`). The scan covers every bin from the lowest to the highest bin touched
by any bar of the set (zero-volume interior bins included). `val = lo*w`, `vah = (hi+1)*w`. Empty or zero-volume set -> none.
*Worked A (w = 1):* bars (l,h,v) = (0,2,6), (1,3,4), (1,2,10): bin0 = 3, bin1 = 3+2+10 = 15, bin2 = 2, total 20, target
14; POC = bin1 (poc_price 1.5), `acc = 15 >= 14` at once -> val 1.0, vah 2.0.
*Worked B (w = 1, point-mass bars at bin centres):* bin volumes [1,2,10,4,3], total 20, target 14: POC bin2, `acc = 10`;
`vl = 2 < vh = 4` -> hi = 3, `acc = 14` stop -> val 2.0, vah 4.0, poc_price 2.5.
*Worked C (tie):* bin volumes [3,10,3], total 16, target 11.2: `acc = 10`, `vl = vh = 3` -> lower: lo = 0, `acc = 13` stop
-> val 0.0, vah 2.0.

**18.2 Fractal pivots (NO-SOURCE width n; FORMULAS section 9 fixed-width fractal, strict comparisons).** On a bar series
with wicks `h`, `l`: bar i is a pivot high iff `h[i] > h[j]` for every `j in [i-n, i+n], j != i`; pivot low iff
`l[i] < l[j]` for the same j. Highs and lows are tested independently (an outside bar can be both; `find_swings` would
label it a high only). Needs `n <= i <= len-1-n`. A pivot at i is confirmed at the close of bar `i+n`, so it may be used
from the open of bar `i+n+1` (no look-ahead).
*Worked:* n = 1, h = [1,3,2,5,4,1,2] -> pivot highs at i = 1 and 3 (h = 3 > 1,2; 5 > 2,4); i = 6 is the last bar, not
testable; a plateau h = [1,3,3,2] gives none (equality fails). n = 2 with h = [1,2,5,2,1] -> pivot high at i = 2 only.

**18.3 Size filter (NO-SOURCE k).** A pivot p is *meaningful* for k > 0 iff there is an earlier pivot q of the opposite
kind (largest `q.i < p.i`) with `|price_p - price_q| >= k * ATR14(p.i)`, where ATR14(i) is the plain-SMA ATR of section 12
over the 14 true ranges ending at bar i (needs i >= 14). `k = 0`: every fractal pivot is meaningful. Pivot price = the
bar's `h` (high) or `l` (low).

**18.4 Anchored families (all built on 5-minute bars, levels refreshed on a 15-minute grid, i.e. at 5m bars whose open
time is a multiple of 900 s, using only bars that closed before the refresh).**
- `session`: bars from 00:00 UTC of the current day. `weekly`: from Monday 00:00 UTC. Developing; need >= 12 bars.
- `prior_day`: the previous UTC day; `prior_week`: the previous Monday-Sunday. Static, active from the first bar after.
- `A1(n,k)` (Tom-shaped): let H = the last meaningful pivot high and Lo = the last meaningful pivot low, both confirmed;
  the set is every 5m bar from the open of the earlier pivot's 1h bar to the close of the later pivot's 1h bar. Active
  from the open of the 5m bar after the later pivot is confirmed (`i_later + n` closed). Static until a newer
  meaningful pivot is confirmed.
- `A2(n,k)` (operator's idea, not Tom's words): the set is every 5m bar from the open of the last confirmed meaningful
  pivot's 1h bar (either kind) up to the refresh. Developing; need >= 12 bars.
Each profile contributes three levels: POC (`poc_price`), VAH, VAL (Tom, aursfDVYzUk:7: "reaction levels, value high,
value low, ... point of control").

**18.5 Touch event and R-multiple outcome (NO-SOURCE measurement choices: R = 1 x ATR14 of 1h bars, H bars, barriers
+-1R).** Let `L` be the level in force at 5m bar j (the value from the latest refresh at or before bar j's open),
`c[j-1]` the previous close, `R = ATR14` of the 1h bars closed before bar j's open. Event: `l[j] <= L <= h[j]` and
`c[j-1] != L`. Side: `c[j-1] > L` -> long (price came down to the level, expected support); `c[j-1] < L` -> short.
Entry price is `L` (limit at the level). Long: stop `L-R`, target `L+R`; short mirrored. Resolution, conservative:
(1) in the touch bar only the stop is tested (`l[j] <= stop` for a long -> stopped at the stop price); (2) bars
j+1..j+H: if `l <= stop` (long) the exit is the stop, filled at the bar open if the bar opened beyond the stop; else if
`h >= target` the exit is the target; the stop is tested first when a bar holds both; (3) otherwise exit at the close of
bar j+H (timeout). One open event per (family, level type) at a time: a touch is skipped while the previous event of that
stream is still open (its exit bar >= this bar).
`gross_R = side * (exit - L) / R`; `net_R = (side * (exit - L) - fee_in * L - fee_out * exit) / R`, fees as fractions of
price from `backtest/fees.py`: primary all-taker `BINANCE_TAKER = 0.0005` on entry and exit; stated variant entry and
target maker `BINANCE_MAKER = 0.0002`, stop and timeout taker.
H = 48 five-minute bars (4h): NO-SOURCE, set as the phase 2 default 2026-10-09, not tuned.
*Worked:* long, L = 100, R = 2, target 102 reached, taker: `net_R = (2 - 0.0005*100 - 0.0005*102) / 2 = 0.9495`. Stop
(98): `(-2 - 0.05 - 0.049) / 2 = -1.0495`. Timeout at 100.5: `(0.5 - 0.05 - 0.05025) / 2 = 0.19987`.

**18.6 Placebo.** For every real level value the placebo level is `L + d * R_ref`, `R_ref` = the ATR14(1h) in force at the
refresh, and `d` cycles deterministically through (-3, -2, -1, -0.5, +0.5, +1, +2, +3) by `(refresh_index) mod 8`. The
same event rule (18.5) is then applied. It measures what any price level earns under the same barriers and fees.

**18.7 Statistics.** n = events; hit = share of exits at target; stop%; timeout%; `mean gross_R`, `mean net_R`. 95%
interval of a mean (or of a difference of two streams) = day-block bootstrap: events are grouped by UTC date, days are
resampled with replacement (2000 resamples, numpy `default_rng(20261009)`), statistic = sum of R over resampled days
divided by the number of events in them (difference: both streams use the same resampled days). Percentiles 2.5 / 97.5.
*Worked:* two days, day A events R = [1, 3], day B events R = [-2]; resample (A, A): mean 2.0; (B, B): -2.0; (A, B): 0.6667.

## 19. Trend-line contract formulas (`research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md`) - added 2026-10-17

All numbers below are computed by hand from the definitions, not from code. Parameters (k=3, tolerances, ATR length 14) are OURS; see the contract.

**19.1 Pivot with k bars each side, strict.** Swing low at bar i iff `low[i] < low[j]` for every j in `i-k..i-1` and `i+1..i+k`. Available at close of bar `i+k`.
Worked (k=3): lows by bar 0..6 = [9,8,7,5,6,7,8]: bar 3 is 5 < 9,8,7 and < 6,7,8, so pivot, available_at = close(bar 6). Ties, lows [9,8,7,5,5,7,8,9] (k=3): bar 3 fails (bar 4 equals 5), bar 4 fails (bar 3 equals 5), no pivot. Bars with fewer than 3 bars on a side (bars 0-2 and 5-7) are never pivots.

**19.2 Line through anchors (ia,pa), (ib,pb).** Linear: `L(t) = pa + (pb-pa)*(t-ia)/(ib-ia)`. Log: `L(t) = exp(ln pa + (ln pb - ln pa)*(t-ia)/(ib-ia))`.
Worked linear: ia=10, pa=100, ib=20, pb=110: `L(25) = 100 + 10*15/10 = 115`. Worked log: pa=100, pb=121, ib-ia=2, t-ia=3: `L = 100*(121/100)^(3/2) = 100*1.21^1.5 = 100*1.1^3 = 133.1` (linear on the same anchors: `100 + 21*3/2 = 131.5`, so the geometries differ).

**19.3 ATR for the contract.** Plain SMA of True Range, section 12, length 14 (OURS). Numeric example of the SMA form is in section 12 (period 3, ATR 2.1667); the line uses ATR_b fixed at the close of bar ib.

**19.4 Slope.** `slope_atr = (L(ib)-L(ia))/(ib-ia)/ATR_b`; `slope_log = (ln pb - ln pa)/(ib-ia)`.
Worked: pa=100, pb=110, ib-ia=10, ATR_b=4: `slope_atr = 10/10/4 = 0.25`; `slope_log = ln(1.1)/10 = 0.0953102/10 = 0.00953102`.

**19.5 Touch, penetration, break (support; resistance mirrors).** With L(25)=115 and ATR_b=4: touch tolerance 0.25*4 = 1, so contact iff `low <= 116`: low 115.8 contacts, low 116.5 does not. Poke tolerance 0.10*4 = 0.4: low 114.5 (< 114.6) with close 115.2 is a poke, still a contact, not a break. Break iff `close < 115`: close 114.9 breaks, close 115.0 does not.
Strict penetration test (L6): anchor-segment bar with L(j)=105 and low 104.7 passes (104.7 >= 105 - 0.4 = 104.6); low 104.5 fails.

**19.6 Contact episode and reset.** Reset distance 1.0*ATR_b = 4: after a contact, the episode ends on the first bar with `low > L + 4` (here `low > 119`). Lows [115.5, 116.0, 120.0, 115.9] against L=115 on four consecutive bars: bars 1,2 are one episode (episode 1), bar 3 (120.0 > 119) ends it, bar 4 contacts again = episode 2. Eligibility (arm A) is at bar 3.

**19.7 Volume anchor test.** Anchor bar volume V, mean of the 20 prior bars M: pass iff `V >= 2*M`. Worked: M=140: V=300 gives ratio 2.143, pass; V=270 gives 1.929, fail; V=280 gives exactly 2.0, pass.

**19.8 Arm B third anchor.** Third pivot c at ic=30 with price 119.5; L(30) = 100 + 10*20/10 = 120; |119.5-120| = 0.5 <= 0.25*4 = 1, so c is an anchor within tolerance; eligible at close(ic+3 = 33). A third pivot at 118.5 (|diff| 1.5) is not.

## 20. WaveTrend observation (`layers/wavetrend/wavetrend.py`) - added 2026-10-17

Source (SOURCED): LazyBear "WaveTrend with Crosses", `research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:14-21` (identical math in `LB_WaveTrend_marketcalls_gist.pine.txt:14-21`); bands `:9-12`, centre `:23`. Re-implemented from the formula, no Pine text copied. Contract: `PARITY_CONTRACT.md` s2-s3.

**20.1 Formula (SOURCED, :14-21).** `ap=(h+l+c)/3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4)`. EMA alpha = 2/(n+1).

**20.2 Conventions the source does not state (OURS, PARITY_CONTRACT s3).** EMA seeded with the first valid source value; output used only after WARMUP=200 bars from series start, from any gap or from any NaN `ci`. `ci` is NaN when `d <= 1e-9*|ap|` (never 0, never inf) and propagates to no event. wt2 is NaN until 4 valid wt1. Cross "le": an event fires at the first bar strictly on the opposite side of the last strict side of `wt1-wt2`; a tie bar is skipped; above-tie-above is no cross; sides reset at NaN. Zones from wt1: `ob2 >= 60`, `ob1 >= 53`, `os2 <= -60`, `os1 <= -53`, else `mid` (boundary inclusive; OURS tag names). `available_at = bar_open + timeframe`. HTF value at time t = last HTF bar with `open + htf_tf <= t`.

**20.3 Worked, by hand.** Two bars, h=l=c: ap = [10, 12].
- Bar 0: `esa=10`, `|ap-esa|=0`, `d=0` -> `ci` NaN (flat window).
- Bar 1: `alpha=2/11`; `esa = 10 + (2/11)*2 = 114/11 = 10.363636`; `|ap-esa| = 18/11 = 1.636364`; `d = 0 + (2/11)*(18/11) = 36/121 = 0.297521`; `ci = (18/11)/(0.015*36/121) = (18/11)*(121/36)/0.015 = 5.5/0.015 = 366.6667`. `wt1[1]` = first valid `ci` = 366.6667 (seed); `wt2` NaN (needs 4 wt1).
- wt2 with wt1 = [10, 20, 30, 40]: `wt2[3] = (10+20+30+40)/4 = 25`; with wt1 = [10,20,30,40,50]: `wt2[4] = 35`.
- Cross, wt1-wt2 signs [+, 0, +] -> no event; [+, 0, -] -> one down-cross at the last bar; [-, +] -> up-cross at the second.

**20.4 Golden series.** `wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv`: 400 BTCUSDT 1h bars (2022-01-01 00:00 UTC onward, DEV period), wt1/wt2 and "le" events from `wavetrend/make_golden.py` (pandas ewm/rolling recursion of 20.1, not the module). Compared at 1e-9 (OURS) after bar 200. Spreadsheet-style parity only; no TradingView export, so NOT Pine-runtime parity.

## 21. Krown layer v0 detectors (`layers/krown/krown_core.py`, `krown_events.py`) - added 2026-10-17

Sources: ledger `research/krown_ta101_2026-10-13/KROWN_RULES.csv` (ids KR-xxx), spec `KROWN_LAYER_SPEC.md` s2-s3. Each number is SOURCED (ledger id) or OURS in `layers/krown/params/krown_params.json`. All detectors are pure functions of closed bars; a value at bar t uses bars <= t only. Descriptive only: no P&L, no live wiring, default OFF. Hand values below are computed from the definitions, not from the code.

**21.1 Zone (KR-Z01, SOURCED).** Pivot bar with wick extreme E and close c: zone = [min(c,E), max(c,E)]. Swing-low pivot o=100 h=110 l=90 c=104: zone [90, 104]. Swing-high pivot h=120 l=108 c=112: zone [112, 120]. A swing at bar i with k bars each side (OURS k=3) is known at bar i+k (KR-Z05, confirm after a later close); a zone is never used before i+k. Turns (KR-Z02) = confirmed same-kind pivots whose wick extreme lies inside the zone, the origin included; a zone qualifies at turns >= 2, or at 1 when the pivot volume ratio >= 2 (KR-Z04). Ranked by (heavy, turns, recency), at most 5 (KR-Z03).

**21.2 Volume (KR-V01, KR-V02, KR-V10; baseline OURS).** ratio = V / mean of the n=20 PRIOR volumes (the current bar is excluded: OURS, so a spike does not inflate its own baseline). Prior mean M=100: V=250 gives 2.5 (flag 2x); V=200 gives exactly 2.0 (flag 2x, boundary inclusive); V=50 gives 0.5 (half flag, KR-V10 observation, boundary inclusive). Same-slot arm (OURS, KROWN spec C5/C10): mean of the same slot (index mod 7 for 1d) over the previous m weeks (production default m=8 in params/krown_params.json; the example below uses m=2); v[0]=100, v[7]=300, v[14]=400: baseline 200, ratio 2.0.

**21.3 Strict engulfing (KR-C06, SOURCED).** Bullish: low < prior low AND close > prior HIGH. Bearish: high > prior high AND close < prior LOW. Prior h=105 l=100: bar l=99 c=106 is bullish; l=99 c=104 is not (loose textbook form); bar h=106 c=99 is bearish. Hammer / shooting star / doji ratios are OURS: hammer = lower wick >= 0.6 of range and (c-l)/range >= 0.7 (bar o=100 h=101 l=90 c=100.5: wick 10/11 = 0.909, close position 0.955: hammer); shooting star mirrors (bar o=100 h=110 l=99 c=100.5: upper wick 9.5/11 = 0.864, (h-c)/range 0.864: shooting star); doji = |c-o| <= 0.1 range. Confirmation (KR-C08): first close within H=3 bars (KR-C03 says 3-5) beyond the pattern's wick high (bullish) or low (bearish).

**21.4 Dominant low / dominant lower high (KR-L10, SOURCED structure; k, tolerance OURS).** Swing high at i: h[i] > h of k bars each side (strict); swing low mirror; known at i+k. State per bar t, after the swings confirming at t: structural s = up if the last two swing highs AND the last two swing lows both rise by more than tol (OURS 0.01), down if both fall, else range. Rules: from range/None, s in (up, down) is taken; from up or down, s differing from the state gives range (a short counter-swing that takes no level is just a range). In up, dominant low = min low between the two latest swing-high indices; in down, dominant high = max high between the two latest swing-low indices. A reversal needs a bar that trades through AND closes beyond the level: in up, low < dominant low and close < dominant low gives down, with dominant lower high = price of the latest swing high; mirror gives up with dominant low = latest swing-low price. Worked, k=1, tol=0, bars (h, l, c): 0:(10,8,9) 1:(12,9,11) 2:(11,7,8) 3:(14,9,13) 4:(13,10,12) 5:(12,8,9) 6:(17,11,16) 7:(15,12,13) 8:(13,6,7.5). Swing highs at 1 (12), 3 (14), 6 (17); swing lows at 2 (7), 5 (8). Known at: high1 t=2, low2 t=3, high3 t=4, low5 t=6, high6 t=7. States t=0..5: range (fewer than two swing lows until t=6). t=6: highs 12,14 rise, lows 7,8 rise: up, dominant low = min(l1..l3) = 7. t=7: highs 14,17: up, dominant low = min(l3..l6) = min(9,10,8,11) = 8. t=8: low 6 < 8 and close 7.5 < 8: down, dominant lower high = 17.

**21.5 BBWP (KR-Q01 basis 7 and lookback 100, close: SOURCED; the rest OURS).** bbw[t] = (upper - lower) / basis = 2*mult*std/SMA with basis SMA over the last `basis` closes, population std, mult = 2 (OURS), so bbw = 4*std/SMA. BBWP[t] = 100 * (number of the previous `lookback` bbw values strictly below bbw[t]) / lookback (OURS percentile formula, current value excluded). First value at t = basis-1+lookback. Regime (KR-Q02): expansion >= 85; compression <= 30 (OURS pick inside the sourced 25-35); confirm > 50. Worked with basis=2, lookback=3, closes [10,10,12,11,15,15,14]: bbw[t] = 4|a-b|/(a+b) with a,b the last two closes: t1 0; t2 8/22 = 0.363636; t3 4/23 = 0.173913; t4 16/26 = 0.615385; t5 0; t6 4/29 = 0.137931. BBWP[4]: previous (t1..t3) = 0, 0.3636, 0.1739 all below 0.6154: 100. BBWP[5]: previous (t2..t4) none below 0: 0. BBWP[6]: previous (t3..t5) = 0.1739, 0.6154, 0; only 0 is below 0.1379: 33.3333.

**21.6 Moving averages and leash (KR-M01, KR-M06; seeding OURS).** EMA(n) seeded with the SMA of the first n values, alpha = 2/(n+1); EMA(5) of [1,2,3,4,5,6] = seed 3 at index 4, alpha 1/3, index 5 = 3 + (6-3)/3 = 4. Leash (KR-M06): a close with candle low above the 5 EMA counts as disconnected; a run of >= 3 (SOURCED "late at about 3 closes") ends at the first bar whose low touches the EMA: event "leash long" at that bar (mirror with the high below the EMA: short). low = [-,11,12,13,12.5,11], ema = [-,9,9.5,10,11,12]: run of 4 closes (idx 1-4), idx 5 low 11 <= 12 touches: one leash at idx 5 (run 4).

**21.7 RSI and zones (KR-S02, KR-S03; period OURS 14).** Wilder RSI: first average gain/loss = simple mean of the first `period` changes, then avg = (avg*(period-1) + x)/period. Period 2, closes [10,11,10,12]: changes +1,-1,+2; seed gain (1+0)/2 = 0.5, loss (0+1)/2 = 0.5: RSI[2] = 50; next avg gain (0.5+2)/2 = 1.25, avg loss (0.5+0)/2 = 0.25: RS 5, RSI[3] = 100 - 100/6 = 83.3333. Zone state (SOURCED 40/60): rsi > 60 bull, < 40 bear, 40-60 inclusive range.

**21.8 Range and coil (KR-R01, KR-R07; windows OURS).** Over the n=20 PRIOR bars: top = max high, bottom = min low, height = top - bottom (the KR-R07 projection), exists when height / midpoint <= 0.25 (OURS). Position = (close - bottom)/height; edge when <= 0.2 or >= 0.8 (KR-R01: edges only, never the middle). Breakout close: close above top or below bottom. Highs [10,11,10.5,11], lows [9,9.5,9,9.5] (n=4): top 11, bottom 9, height 2, midpoint 10, width 0.2: range. Close 9.4: position 0.2, low edge. Close 11.5: breakout up. Coil score = mean(h-l over the last 5 bars) / mean(h-l over the n bars before them); compression when < 0.7 (OURS).

**21.9 Tops (KR-P01, KR-V02, KR-Q02).** Signals per bar: reversal candle (shooting star, strict bearish engulfing or three black crows), volume ratio >= 2 vs the 30-bar mean (SOURCED TOP-05), BBWP > 85, momentum (bearish RSI divergence between the two latest swing highs, or MACD(12,26,9) bearish cross; periods OURS). Fires at t when at least 3 of the 4 have a signal inside bars t-w+1..t (w = 3, OURS "a few bars") and the count was < 3 at t-1. Candle at 5, volume at 6, BBWP at 7, no momentum: count at t=7 is 3: one fire at 7; at t=8 the window 6..8 holds 2: none.

## 22. Bollinger Bands (`scripts/dev/chart_verify.py`; same maths as `layers/alerts/live_bb_top_reversal.bollinger`) - added 2026-10-17

**Chosen definition (TradingView `ta.bb`):** mid[t] = SMA of the last n closes; sd[t] = POPULATION standard deviation of those n closes (divide by n, not n-1); upper = mid + mult*sd; lower = mid - mult*sd. Defaults n=20, mult=2 (SOURCED: standard Bollinger setting, TradingView default). `None` until n closes exist. Checked 2026-10-17 against `live_bb_top_reversal.py` lines 33-43: it divides by n (population), so the two agree. Sample sd (n-1) is the known variant: it widens the band by sqrt(n/(n-1)) (2.6% at n=20) and is NOT used.

**Worked example (n=4, mult=2, 6 bars):** closes = [8, 10, 10, 12, 14, 12]. Last window (idx 2..5) = [10, 12, 14, 12]: mean 12; deviations -2, 0, 2, 0; squares sum 8; population variance 8/4 = 2, sd = 1.414214; upper = 12 + 2.828427 = 14.828427, lower = 9.171573. (Sample sd would give sqrt(8/3) = 1.632993, upper 15.265986: the variant, not used.) First window (idx 0..3) = [8,10,10,12]: mean 10, squares 4+0+0+4 = 8, sd 1.414214, upper 12.828427, lower 7.171573.

## 23. Stochastic RSI (`scripts/dev/chart_verify.py`) - added 2026-10-17

**Chosen definition (TradingView "Stoch RSI" defaults 3, 3, 14, 14):** r = Wilder RSI(rsi_len) from section 1; raw[t] = 100*(r[t] - min(r over the last stoch_len values)) / (max - min) over the same window (all values must exist; if max == min raw = 0 - OURS, avoids 0/0); K = SMA(raw, k_len); D = SMA(K, d_len). Defaults rsi_len 14, stoch_len 14, k_len 3, d_len 3 (SOURCED: TradingView defaults; CoinGlass shows the same pair, verified chart by chart with `chart_verify.py --seen`). First K at index rsi_len + stoch_len - 1 + k_len - 1.

**Worked example (rsi_len 2, stoch_len 3, 6 bars):** closes = [10, 11, 10, 12, 11, 13]. Section 1 / 21.7 gives RSI[2] = 50, RSI[3] = 100 - 100/6 = 83.3333 (avg gain 1.25, avg loss 0.25). RSI[4]: change -1, avg gain 1.25/2 = 0.625, avg loss (0.25+1)/2 = 0.625, RS 1: 50. RSI[5]: change +2, avg gain (0.625+2)/2 = 1.3125, avg loss 0.625/2 = 0.3125, RS 4.2: 100 - 100/5.2 = 80.76923. raw[4]: window [50, 83.3333, 50]: (50-50)/33.3333 = 0. raw[5]: window [83.3333, 50, 80.76923]: (80.76923-50)/33.3333 = 12/13: 92.30769. With k_len 2: K[5] = (0 + 92.30769)/2 = 46.15385. With k_len 1, d_len 1, K = raw.

## 24. Kurisko Quad Rotation (`layers/kurisko/stoch_core.py`, `quad_rotation.py`) - added 2026-10-18

Sources: `research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md` s3 and s5, extract `extracts/processed/kurisko/QUAD_ROTATION.md` (R1 periods, R2 level 20, R3 turn trigger, R8 "here I'm using the D line"), non-Claude review `research/lab_guy/spec_review_kurisko_2026-10-18.md` (FIX applied: plotted line is D = SMA_d(raw %K), not raw %K). Labels per number are in `layers/kurisko/params/kurisko_default.json`. Pure functions of closed bars: a value at bar t uses bars <= t only. Alert-only, default OFF.

**24.1 Stochastic line (period SOURCED R1/S4; formula OURS where the sources are silent).** raw %K_k[t] = 100*(C[t] - LL_k)/(HH_k - LL_k), HH/LL over bars t-k+1..t of high/low. HH == LL gives NaN (never 0 or 100). Plotted line = D = SMA_d(raw %K_k); bands (k, d) = (9,3), (14,3), (40,4), (60,10). Variant (60,10,10) = SMA_10 of SMA_10 (slowing 10, then d 10), a ledger trial. A NaN in any SMA window gives NaN. A missing bar or NaN bar splits the series; windows never span it.

**24.2 Worked example (independent: `layers/kurisko/make_golden.py`, does not import the module; golden `golden_stoch_k5d3.csv`).** k = 5, d = 3, 20 bars (high, low, close): (102,98,100) (104,99,103) (105,101,102) (106,102,105) (107,103,104) (108,104,107) (110,106,109) (111,111,111) (111,111,111) (110,106,107) (109,105,106) (108,104,105) (107,103,104) (106,102,103) (105,101,102) (104,100,101) (103,99,102) (105,100,104) (107,102,106) (108,104,107). Bar 4: window bars 0..4, HH 107, LL 98, C 104: raw = 100*6/9 = 66.666667; first line value needs three raw values, so bar 6: raws 66.6667, 88.8889, 88.8889 give 81.481481. Raw %K by bar 4..19: 66.6667, 88.8889, 88.8889, 100, 100, 42.8571, 16.6667, 14.2857, 12.5, 12.5, 12.5, 12.5, 37.5, 71.4286, 87.5, 88.8889. Line by bar 6..19: 81.4815, 92.5926, 96.2963, 80.9524, 53.1746, 24.6032, 14.4841, 13.0952, 12.5, 12.5, 20.8333, 40.4762, 65.4762, 82.6058. Flat series (HH == LL for every window): all NaN.

**24.3 RSI arm (OPERATOR-HYPOTHESIS, not Kurisko; "RSI" occurs 0 times in the transcript).** Wilder RSI from section 1 / `rsi_core` on the same four lookbacks 9, 14, 40, 60, levels 20/80 reused. Hand example, closes 10,9,8,7,6,7, periods (2,3,3,3): falling closes give RSI 0 once seeded; idx 5, period 2: avg gain (0*1+1)/2 = 0.5, avg loss (1*1+0)/2 = 0.5, RS 1, RSI 50; idx 5, period 3: avg gain 1/3, avg loss 2/3, RS 0.5, RSI 33.3333.

**24.4 Event rule (OURS: no source defines the number for "turn up", KURISKO_SPEC s5 gap 3).** Episode = from the first bar s with all four lines < 20 (strict; exactly 20 is not under 20) until any line is >= 20 or NaN. Long event at the close of the first t > s with all four < 20 on bars s..t-1 and fast[t] > fast[t-1] (strict; fast = the first band, (9,3)); the event bar itself may leave the zone. One event per episode; a later episode can fire again. Mirror (all four > 80 strictly, fast[t] < fast[t-1]) = short, NO-SOURCE, reported apart. Row: t_close (= open_time + tf), side, kind (`quad_rotation_stoch` or `quad_rotation_rsi`), the four values at t, episode_start_t (close time of bar s). Other turn rules (D9 crosses up through 20) are ledger trials, not built.

**24.5 Worked event fixtures (hand-derived, in `test_quad_rotation.py`).** Bands (2,1), (3,1), (4,1), (5,1) (line = raw %K). Bars 0..5 fall one point each with close = low, high = low + 1 (low 100-i): every full-window raw %K is 0, so all four lines are 0 from bar 4 (s = 4). Bar 6 (h 97, l 94.5, c 96.5): lines 80, 80, 57.142857, 44.444444; fast 80 > 0: long event at t = 6, episode_start bar 4. Alternative bar 6 (h 96, l 94, c 94.2) gives 10, 6.666667, 5, 4 (event at 6) and bar 7 (h 95, l 93, c 93.5) gives 16.666667, 16.666667, 12.5, 10: the fast line ticks up again inside the same episode, no second event. Mirror (h' = 200-l, l' = 200-h, c' = 200-c, raw' = 100 - raw): short event at 6 with 90, 93.333333, 95, 96.

## Verification note (this audit, 2026-09-28)

Every case number in `layers/timeframe/TEST_PLAN.md`, `layers/rsi/TEST_PLAN.md`,
`layers/TEST_PLAN_runner.md` and `layers/cryptocred/TEST_PLAN.md` was independently re-derived using a
throwaway Python scratch implementation written directly from this file's definitions (never by
importing or reading the layer modules under test), and matched the existing plan values exactly. No
plan numbers required correction. The one correction made was to `layers/rsi/TEST_PLAN.md`'s header
(Case C1 provenance claim, which described deriving from `bt/bt_rsi.py.new` — against the "never derive
from code" rule even though the module's own math turned out to match textbook Wilder); see that file's
diff and the audit report for detail.
