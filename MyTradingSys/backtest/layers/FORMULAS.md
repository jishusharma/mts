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

---

## Verification note (this audit, 2026-09-28)

Every case number in `layers/timeframe/TEST_PLAN.md`, `layers/rsi/TEST_PLAN.md`,
`layers/TEST_PLAN_runner.md` and `layers/cryptocred/TEST_PLAN.md` was independently re-derived using a
throwaway Python scratch implementation written directly from this file's definitions (never by
importing or reading the layer modules under test), and matched the existing plan values exactly. No
plan numbers required correction. The one correction made was to `layers/rsi/TEST_PLAN.md`'s header
(Case C1 provenance claim, which described deriving from `bt/bt_rsi.py.new` — against the "never derive
from code" rule even though the module's own math turned out to match textbook Wilder); see that file's
diff and the audit report for detail.
