# FORMULAS.md — canonical formula definitions for the indicator layers

Purpose: every formula used by `layers/rsi`, `layers/timeframe`, `layers/cryptocred` and
`layers/runner.py` (plus the `bt/bt_stats.py` / `bt/ref_pbo.py` metrics used to score them) gets ONE
chosen definition here, its canonical source, the known variants and why we picked ours, and a tiny
worked example. Every TEST_PLAN.md in these layers must derive its expected numbers from this file,
never from an implementation module (see LESSONS_LEARNED.md 2026-09-28 D1: `layers/rsi/TEST_PLAN.md`
Case C1 was originally derived from `bt/bt_rsi.py.new`'s `rsi_wilder`, which is off vs textbook Wilder).

## 1. RSI (Wilder, `rsi_core.rsi_core`)

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

Source: `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md` cluster C08 (MSB Definition &
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

**Degenerate-input policy (DECISION OURS, 2026-10-28):** `pbo_cscv` / `ref_pbo_cscv` raise `ValueError` for
T < S, S < 2 or odd S, ragged rows, an empty or single-row matrix, or zero columns (no partition is
silently truncated to zero rows; nondivisible T keeps the first (T//S)*S rows). `bt_stats.sharpe`
returns NaN for zero variance or a single observation, and `psr` / `dsr` propagate NaN; inside CSCV a
constant variant ranks as Sharpe 0 so valid-input PBO arithmetic is unchanged (section 10 oracle, 1e-12).
`ref_pbo.sharpe` keeps its own 0.0 convention for constant series (internal to the reference CSCV).

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

Sources: funding-extreme reversion T2, Memon 2026 (7y Binance) via `research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md`
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

## 25. Halving clock (`research/fractals_2026-10-31/phase_tag/phase_tag.py`) - added 2026-10-31

**Chosen definition.** Halving instants (UTC, SOURCED: Bitcoin block timestamps): 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20 00:09 (block 840,000; pinned per VALIDATION.md 2a, R1 used 04-20 and R2 04-19). `days_since_halving` at tag row t = calendar days from the date of the latest halving that is dated on or before the LAST CLOSED bar (t-1) to the date of bar t-1. The epoch switches on the bar dated the halving day (day 0). Cycle year (OURS) = 1 + floor(days/365), capped at 4. Pure calendar function; with the one-bar shift it uses nothing from bar t. A tag is descriptive context, never a trigger (n = 2-3 cycles).

**Worked example (by hand).** Peak close of the 2024 cycle = bar dated 2025-10-06 (Binance spot 124,658.54). 2024-04-20 -> 2025-04-20 = 365 days; then Apr 20 -> May 20 30, -> Jun 20 31, -> Jul 20 30, -> Aug 20 31, -> Sep 20 31, -> Oct 6 16; 30+31+30+31+31+16 = 169; 365 + 169 = 534. The tag row dated 2025-10-07 reads 534. Row dated 2026-09-30 uses the 2026-09-29 bar: 2024-04-20 -> 2026-04-20 = 730, -> 2026-09-29 = 30+31+30+31+31+9 = 162; 892. Boundary: row for 2024-04-20 uses bar 04-19 -> 1439 days from 2020-05-11 (2020-05-11 -> 2024-05-11 = 1461, minus 22 days); row 2024-04-21 uses bar 04-20 -> 0. Variant not used: counting from 2024-04-19 gives 535 at the peak.

## 26. Cowen band (`research/fractals_2026-10-31/phase_tag/phase_tag.py`) - added 2026-10-31

**Chosen definition.** Weekly closes = close of the Sunday bar (ISO week Mon..Sun, UTC); only completed weeks whose Monday bar exists in the data count. SMA20w = mean of the last 20 weekly closes (SOURCED: Cowen band, R2_BTC_PHASES.md s2, video bWdXPK3Hlok 00:06:02; sim-desk `cowen_bmsb.py:35`). EMA21w: seed = SMA of the first 21 weekly closes (OURS, TradingView `ta.ema` convention), then e = e + (2/22)*(W - e). Both values are carried forward from the last completed Sunday. Side of the last closed bar's DAILY close: above if close > max(SMA20w, EMA21w); below if close < min; else inside (OURS). Only data up to the last closed bar is used; the tag at row t is shifted one bar.

**Worked example (by hand).** Synthetic dates from Monday 2023-01-02, close[i] = 100 + i (i <= 449). Sunday bars i = 6, 13, ..., so weekly close W_k = 106 + 7k. Row i = 250 uses bar 249; completed weeks k = 0..34 (Sunday bar 244). SMA20w = mean(W_15..W_34) = 106 + 7*24.5 = 277.5. EMA21w: seed = mean(W_0..W_20) = 106 + 7*10 = 176 = W_20 - 70, and on a ramp of slope 7 the EMA lag is (1-a)/a * 7 = 10 * 7 = 70, so every step stays on W_k - 70 (check: e + (1/11)(7 + 70) = e + 7); EMA21w at k = 34 is 344 - 70 = 274. Close of bar 249 = 349 > max(277.5, 274): side = above. Weekly SMA10 = 106 + 7*mean(25..34) = 312.5 (one week earlier 305.5: rising), close above: phase above_up. Real data: row 2026-09-30 reads SMA20w 70,366.92, EMA21w 73,695.10, bar 2026-09-29 close 83,663.66: above (independent plain-python recompute matches).

## 27. Rolling DFA Hurst (`research/fractals_2026-10-31/f2/dfa.py`) - added 2026-10-31

**Chosen definition (OURS parameters, SOURCED estimator).** Detrended fluctuation analysis, order 1 (Peng et al. 1994), the estimator Bariviera 2017 uses rolling on BTC (R1 s1b). For a window of n returns x: profile y_j = sum_{i<=j}(x_i - mean(x)). Cut y from the front into nb = floor(n/s) boxes of s points. In each box fit the least-squares line a + b t and take the mean squared residual; F^2(s) = average of the box values over boxes; F(s) = sqrt(F^2(s)). H = OLS slope of log F(s) on log s over s in {8,16,32,60,96,160}. H ~ 0.5 for uncorrelated returns, > 0.5 persistent (trending), < 0.5 anti-persistent (mean-reverting). Window W = 480 consecutive 1h log returns (20 days); H of the window ending at bar i is known at the close of bar i.

**Worked example (by hand).** x = +1,-1,+1,-1,... (mean 0), s = 4: profile per box 1,0,1,0; t - mean(t) = -1.5,-0.5,0.5,1.5, sum of squares 5; slope = (1*(-1.5) + 0 + 1*0.5 + 0)/5 = -0.2; fitted line = 0.5 - 0.2(t - 1.5) = 0.8,0.6,0.4,0.2; residuals 0.2,-0.6,0.6,-0.2; mean square = (0.04+0.36+0.36+0.04)/4 = 0.2. So F^2(4) = 0.2 (test_dfa.py). Random-walk increments give H = 0.5 and fGn with Hurst 0.8 gives about 0.8 (tests with tolerances).

**Known limit.** DFA understates H on short windows (R1 s1b, arXiv 1201.4786); the thresholds 0.45 / 0.55 are not corrected for that bias, and the 480-return window has a wide error band (sd of H over DEV hours is 0.056).

## 28. Fabio v3: signals S1-S9 and Models A-D (`research/fast_track_2026-09-27/FABIO_V3_SPEC.md` s2-s6, v3.1) - added 2026-11-01

Written from the spec text only; the worked numbers below were computed by hand and then cross-checked with a throwaway script
written from these definitions (never from `layers/fabio/v3/`). Labels: SOURCED = a Fabio quote (spec table 7.1, id Pnn); OURS =
our choice (NS-fixed fixed value, NS-grid registered grid value); SIM = venue/data/cost convention; SAFETY = exempt limit. Nothing
here is a result. Look-ahead rule: every f(bars, i, ...) reads bars[0..i] only; a decision at the close of bar i acts from bar i+1.

**28.1 Inputs and helpers.** 1m order-flow bars: `o,h,l,c`, `buy_vol,sell_vol` (`v = buy+sell`, `d = delta = buy-sell`), big-trade
columns `b99_*` / `b999_*`, footprint `fp` (10 USD bins, re-binned to B_prof = 50 USD, SIM). A window [a, i] is valid only if
`t[i]-t[a] = (i-a)*60000` ms, else the signal is None/0/False. TICK = 0.1 USD (SIM). `s` = +1 long/buyers, -1 short/sellers.
`TR`, `ATR_N(i) = mean(TR[i-N+1..i])`: section 12 (plain SMA, needs i >= N). Contiguity (amended 2026-11-01, SAFETY): `ATR_N(i)` reads `TR[i-N+1]`, which reads `c[i-N]`, so the bars [i-N, i] (N+1 bars) must be contiguous; a timestamp gap anywhere in them -> None. z-score `z(x_i;L) = (x_i - mean(x[i-L..i-1])) / pstdev(x[i-L..i-1])`
(population sd; pstdev = 0 -> None). Profile `P(window)` = bin -> sum(buy+sell) of the fp entries, re-binned `k = floor(binlow/B)*B`.
POC = max-volume bin, ties to the lower bin, `poc_center = bin + B/2`. Value area 70% (SOURCED P11 quote, NS-fixed value): dense
volumes v[0..n-1]; a = z = POC index, acc = v[POC]; while acc < 0.70*total and bins remain: up = v[z+1]+v[z+2], dn = v[a-1]+v[a-2]
(missing = 0); if no bins above, or (bins below and dn > up) take up to 2 bins below, else up to 2 above (tie -> above).
`VAL = lowbin(a)`, `VAH = lowbin(z) + B`. Not the section 18.1 builder (that one walks one bin at a time). LVN: interior i with
`v[i] < v[i-1]`, `v[i] <= v[i+1]`, `v[i] <= 0.5 * med`, med = upper median of the nonzero v; LVN price = bin + B/2 (OURS P35).
*Worked (value area, B = 10):* {100:10, 110:20, 120:40, 130:15, 140:5, 150:10}, total 100, target 70. POC = 120, acc 40. up = 15+5 = 20,
dn = 20+10 = 30 > 20 -> take 110 and 100, acc = 70 >= 70 stop. VAL = 100, VAH = 120+10 = 130, poc_center = 125. Close 135 = premium,
99 = discount, 115 or 130 = fair. Tie: {100:10, 110:30, 120:10}: POC 110, acc 30 < 35, up = 10 = dn -> above: 120, acc 40 -> VAL 110, VAH 130.
*Worked (LVN, B = 10):* v = [30,25,5,20,4,30,10] at bins 100..160, nonzero sorted [4,5,10,20,25,30,30], upper median index 3 -> 20,
limit 10. Interior 120 (5 < 25, 5 <= 20, 5 <= 10) and 140 (4 < 20, 4 <= 30, 4 <= 10) qualify: LVNs 125 and 145.

**28.2 Signals (pure functions; parameters passed explicitly).**
- **S1 balance(i, N, k_bal)** (N in {60,120,240} OURS NS-grid, k_bal 0.8 OURS NS-fixed, POC band 0.25 OURS NS-fixed; concept 0j:4 "the market is balanced"): W = [i-N+1, i] (needs [i-N, i] contiguous because of `ATR_N(i)`, section 28.1; fail closed on a gap), `H = max h`, `L = min l`, `R = H-L`, `poc = poc_center(P(W))`. Balance iff `R <= k_bal*sqrt(N)*ATR_N(i)` AND `|c[i]-poc| <= 0.25*R`; result {H, L, R, poc}, else None.
- **S2 pressure(i, N, p, q = 0.25)** (p in {0.05, 0.10} OURS NS-grid, q OURS NS-fixed): only where S1(i) exists. `P = sum d[W] / sum v[W]`, `drift = |c[i]-o[i-N+1]| / R`. S2 = sign(P) if `|P| >= p` and `drift <= q`, else 0 (+1 accumulation, -1 distribution).
- **S3 effort_result(i, L = 60, z_hi, r_abs = 0.25, r_ctl = 1.0)** (z_hi in {2.0, 2.5, 3.0} OURS NS-grid, rest OURS NS-fixed): `e = z(d_i;L)`, `res = z(r_i;L)`, `r = c-o`. For s: CONTROL = s if `s*e >= z_hi` and `s*res >= r_ctl`; ABSORBED = s if `s*e >= z_hi` and `s*res <= r_abs` (side s aggressed with no result or against it). Either z None -> {0, 0}. In a trade (v3.1): `E_opp(i)` = absorbed[i] == -s, `E_own(i)` = absorbed[i] == s.
- **S4 big_push(i, m, s)** (m in {5, 15} OURS; big trade = causal prior-30-day 99th / 99.9th row-size percentile, OURS NS-fixed; concept 0j:4 "big trades in the direction"): tier `"999"` iff `VR(i) >= 1.5` else `"99"` (OURS NS-fixed, concept ja:25-26), `VR` = session volume so far / median of the prior 20 valid weekdays over the same elapsed minutes; fewer than 10 prior days -> "99". `net(i;m) = sum_{j=i-m+1..i}(bT_buy_vol - bT_sell_vol)`. S4 = `s*net(i;m) > 0`.
- **S5 breakout(i)** (trigger on the close, SOURCED P08): = s iff `S2(i-1) == s`, `s*(c[i]-E_s) > 0` with `E_{+1} = H(i-1)`, `E_{-1} = L(i-1)` (from S1(i-1)), and S4(i, m, s); else 0.
- **S5D failed_auction(i)** (v3.1, SOURCED P09): balance S1(i-1) exists, `S2(i-1) == -s` (side -s pressed), some j in [i-N, i-1] with `absorbed[j] == -s`, `s*(c[i]-E_s) > 0`, S4(i, m, s). Result `edge = E_s`, `lvl` = `l[j]` (s = +1) or `h[j]` (s = -1) of the LAST such j. Else None.
- **S6 control_level(a, i, s)** (SOURCED P10): last j in (a, i] with `ctrl[j] == s`; `l[j]` if s = +1, `h[j]` if s = -1; else None.
- **S7 curve(i, sess_open)** (add gate on = SOURCED P11 "raise the exposure low in the curve"; off = variant): value area of the session profile [sess_open, i]; premium if `c > VAH`, discount if `c < VAL`, else fair. Add gate: no long add in premium, no short add in discount.
- **S8 exhaustion(i, trade = {s, e_i, lvl})** (exit taker at o[i+1]): true if any of
  (a) `i-e_i >= 15` and `s*net(i;15) <= 0` (OURS NS-fixed, concept 0j:4 "not pushing anymore");
  (b) S1(i, 60, k_bal) exists, `i-59 > e_i` and (`S2(i,60,p) == -s` OR `n(s) > n(-s)`), `n(x)` = count of j in [i-59, i] with S3(j).absorbed == x (SOURCED P14; a new balance where the other side was absorbed, or neutral, is a HOLD);
  (c) `S3(i).control == -s` and `s*(c[i]-lvl) < 0` (SOURCED P15);
  (d) only with climax on (event mode): bar x = i-1 made a new trade extreme (`s*(ext(x)-ext_prev) > 0`, ext = h long / l short, ext_prev = best ext over [e_i, x-1], needs x-1 >= e_i), `s*net(x;1) > 0`, and `S3(i).absorbed == s` (SOURCED P16, 1-bar look-back OURS).
  Too few bars for a clause -> that clause is False.
- **S9 defended_level(a, i, s)** (v3.1, SOURCED P20): last j in (a, i] with `absorbed[j] == s`; `h[j]` if s = +1, `l[j]` if s = -1; else None.

*Worked (S1/S2/S4/S5, 6 bars, bin 1.0):* o/h/l/c, buy/sell, fp bin: 0: 100/101/99/100, 5/5, 100; 1: 100/102/99/101, 6/4, 100; 2: 101/102/100/100, 3/7, 100; 3: 100/101/99/100, 4/6, 99; 4: 100/101/99/100.5, 3/7, 100; 5: 100/100.5/98/98.5, 2/8, 98 with `b99_sell_vol` 3, `b99_buy_vol` 0. i = 4, N = 4, W = [1..4]. TR1 = max(3, |102-100|, |99-100|) = 3, TR2 = 2, TR3 = 2, TR4 = 2, ATR = 9/4 = 2.25. H = 102, L = 99, R = 3; limit = 0.8*2*2.25 = 3.6 >= 3. Profile {99: 10, 100: 30}, POC bin 100, poc = 100.5, |100.5-100.5| = 0 <= 0.75: balance {102, 99, 3, 100.5}. With k_bal = 0.6 the limit is 2.7 < 3: None. S2: sum d = 2-4-2-4 = -8, sum v = 40, P = -0.2; drift = |100.5-100|/3 = 0.1667 <= 0.25; p = 0.10 -> S2 = -1; p = 0.25 -> 0. S5 at i = 5, s = -1, m = 1, tier 99: S2(4) = -1 = s, `E_{-1} = L(4) = 99`, `-1*(98.5-99) = 0.5 > 0`, net = 0-3 = -3, `s*net = 3 > 0` -> S5 = -1. S4 tier: ten prior days of volume 200, today 300 -> VR 1.5 -> "999"; today 299 -> "99".
*Worked (S3, L = 4, z_hi 2.5):* prev d = [1,-1,1,-1] (mean 0, pstdev 1), prev r = [0.5,-0.5,0.5,-0.5] (mean 0, pstdev 0.5). d_i = 3 gives e = 3 >= 2.5. r_i = 0: res = 0 <= 0.25 -> {control 0, absorbed +1}. r_i = 1.0: res = 2 >= 1 -> {control +1, absorbed 0}. r_i = 0.25: res = 0.5, neither -> {0, 0}. Prev d all 1: pstdev 0 -> {0, 0}.
*Worked (S6/S9/S8):* s = -1, a = 10, ctrl[11] = -1 (h 105), ctrl[12] = +1, ctrl[13] = -1 (h 103): S6(i = 14) = 103, S6(i = 12) = 105, S6(i = 10) = None. S9 long with absorbed[j] = +1 at the last such j, h[j] = 100,120 -> level 100,120. S8(c): long, lvl 101, control -1: close 100.9 -> true, close 101.0 -> false (strict). S8(a): long, net(i;15) = -1 or 0 and i-e_i = 15 -> true; net +1 -> false; i-e_i = 14 -> false.

**28.3 Models (one state machine per model, one open trade per model, run independently per window).** Stop distance `D = max(f*entry, structural)` with f in {0.3%, 0.5%} (OURS NS-grid); no arm if `D > Dmax*entry`, Dmax = 1.0% (OURS NS-fixed, SAFETY). Stop = `entry - s*D`. Entry mode (OURS NS-grid): `rest` = maker limit armed before the touch; `confirm` = taker at the next open.
- **Model A, LVN pullback trend** (WITH the pressure; retrace 25% OURS P35): IDLE -> IMPULSE at bar i_b with S5(i_b) = s and the day gate open; O = E_s of that balance. Each bar: X = leg extreme since i_b, leg profile `P([i_b, i])`; candidates are LVNs with `s*(X-lvn) >= 0.25*s*(X-O)` and `s*(c[i]-lvn) > 0`; LVN* = candidate nearest X; ARMED (limit at LVN*, re-priced each close) else IMPULSE. confirm: taker at o[j+1] after the first armed bar j touching the limit with `S3(j).control == s`. Cancel: `s*(c[i]-O) < 0`, S8(c), or bar >= open+330. Structural = `s*(entry-O) + TICK`.
- **Model B, failed-breakout reclaim** (AGAINST, reclaim within 5 bars, rest valid 3 bars: OURS NS-fixed P36): balance B = S1(i-1); PROBE at bar i with `s_b*(c[i]-E_{s_b}) > 0`, Xp = probe extreme, absorbed = any `absorbed[j] == s_b` in the probe; RECLAIM at the first j <= i+5 with `s_b*(c[j]-E_{s_b}) < 0` and absorbed, else IDLE; side `s = -s_b`. rest: limit at c[j]; confirm: taker at o[j+1]. Structural = `|Xp-entry| + TICK`. target_mode `edge` (default): target = opposite balance edge E_s, maker, fill-through; `trail` (variant, SOURCED P37): no target, managed like A. No day gate.
- **Model C, IVB** (IB 30 min, SOURCED P38): `IBH`, `IBL` over [open, open+30), `mid = (IBH+IBL)/2`. First bar i >= open+30 with `s*(c[i]-IB_s) > 0` (IB_{+1} = IBH), S4(i, m, s) and the day gate open: rest = limit at IB_s armed at the close of i; confirm = taker at o[i+1]. Structural = `s*(entry-mid) + TICK`. One IVB trade per day.
- **Model D, failed-auction breakout** (v3.1, SOURCED P09, rest validity 3 bars OURS P39): at bar k with S5D(k) = {s, lvl, edge} (day gate off in the grid): rest = limit at `edge` armed at the close of k, valid bars k+1..k+3, cancelled if a close before the fill has `s*(c-lvl) < 0`; confirm = taker at o[k+1]. Structural = `s*(entry-lvl) + TICK`. No target.
*Worked (BTC prices):* A: O = 100,000, X = 100,650, threshold 0.25*650 = 162.5, so lvn <= 100,487.5; LVNs {100,225, 100,475, 100,575}; close 100,550: candidates 100,225 and 100,475 (100,575 fails both tests); nearest X = 100,475 = entry; structural = 475 + 0.1 = 475.1; f = 0.3% gives 301.425, D = 475.1, stop = 99,999.9, `Dmax*entry = 1,004.75` ok. B: E_{+1} = 100,000, probe extreme Xp = 100,150, reclaim close 99,950 -> short entry 99,950; structural = 200 + 0.1 = 200.1; f = 0.3% gives 299.85, D = 299.85, stop 100,249.85; target E_{-1} = 99,400. C: IBH 100,300, IBL 99,900, mid 100,100, long entry 100,300: structural = 200.1, f = 0.3% gives 300.9, D = 300.9, stop 99,999.1. D: edge = entry = 100,000, lvl = 99,800: structural 200.1, f = 0.3% gives 300, D = 300, stop 99,700.

**28.4 Fills, management, costs.**
- **Fills** (SIM, BP:50-51): a limit at P placed at the close of bar i is live from bar i+1. Buy fills in bar j iff `l[j] <= P - TICK`; sell iff `h[j] >= P + TICK` (1e-9 tolerance); fill price = P; the arming bar never fills. Fill bar j: only the stop is checked; management and S8 start at j+1. A taker fill is at o[j] and makes j the fill bar. Missed winner: an order that never fills while price later reaches `P + s*2D`.
- **Stop exit**: long `l[i] <= stop` -> exit at the stop, or at o[i] if the bar opened beyond it. Stop-first when a target is also touched (SIM); target-first reported too.
- **Order each close i > fill bar**: stop moves, S8, add.
- **mgmt `event`** (v3.1 default, SOURCED P17-P20): (i) `E_opp(i)`: `a` = last j in [fill+1, i-1] with ctrl[j] == s else the fill bar; `pb` = adverse extreme of (a, i] (min l long, max h short); candidates {e1, pb - s*TICK}; keep those with `s*(c[i]-x) > 0`; best = max_s; stop -> best iff `s*(best-stop) > 0` (kind "opp"). (ii) `E_own(i)`: stop -> `trail_update` (kind "own"), arm DL = S9 at i; never an exit. (iii) DL armed at a bar < i and `s*(c[i]-DL) > 0`: stop -> `trail_update`, DL cleared (kind "trail"). (iv) S8 with clause (d) on. `trail_update(stop, lvl, c)`: cand = `lvl - s*TICK`; stop -> cand iff `s*(cand-stop) > 0` and `s*(c-cand) > 0`.
- **mgmt `dist`** (registered variant, be_k in {1.0, 2.0} OURS NS-grid): BE when `s*(ext-e1) >= be_k*D` (ext = best price from fill bar+1): stop -> e1 if tighter (kind "be"); trail only after BE.
- **Adds** (SOURCED P22 max 2 adds / 3 entries; P23 mode `be`; P24 mode `day`, operator variant; min add 0.25*q1 and cap q1 OURS P25): allowed iff fewer than 2 adds, bar i < open+330, `S3(i).control == s`, S4(i, 15, s), S7 gate (unless s7 off), and in mode `be` the stop is at or beyond e1. Taker at `pa = o[i+1]`. `locked = sum_k q_k*s*(stop-e_k)`, `dist = s*(pa-stop)`, `q_add = min(q1, (budget+locked)/dist)`, skipped if `q_add < 0.25*q1`. Mode `be`: budget 0; mode `day`: `budget = max(0, closed day R)*U`, `U = q1*D1/r1`. Executed by `simulate_trade_legs` (name OURS, not wired into the engine): stop, S8 and target are shared by all legs, so every leg exits at the one exit price; decision at the close of bar i after the stop moves (not on an S8 bar), fill taker at `o[i+1]`; fee R per leg on its ENTRY notional, also on a stop exit.
- **Costs** (SIM, sim.py wins): FEE_MAKER = 0, FEE_TAKER = 0.0005. R unit = `q1*D1`. Leg gross R = `q_k*s*(x_k-e_k)/(q1*D1)`; fee R = `(fee_in+fee_out)*e_k*q_k/(q1*D1)` (fee on the entry notional); slippage stress 0/2/5 bps per taker leg = `slip*e_k*q_k/(q1*D1)`. Funding: section 13, own line, stress 2x.
*Worked (stops, adds, costs):* Add leg arithmetic (long, q1 = 1, e1 = 100,000, D1 = 300, stop 100,100, add at pa = 100,200, stopped at 100,100): gross R = (100 - 100)/300 = 0; fee R = (0 + 0.0005)*100,000/300 + 0.001*100,200/300 = 0.166667 + 0.334 = 0.500667; net R = -0.500667 (pinned by `test_s28_add_net_r_matches_hand_number`). E_opp: long, e1 = 100,000, stop = 99,700, pb = 99,900, c = 100,150: candidates {100,000, 99,899.9}, both below c; best = 100,000 > 99,700 -> stop 100,000 (kind "opp"). trail_update: S6 = 100,050 -> cand = 100,049.9 > stop and < c 100,150 -> stop 100,049.9. Add (mode `be`): q1 = 1, e1 = 100,000, stop = 100,100 (past e1), pa = 100,200: locked = 100, dist = 100, q_add = min(1, 100/100) = 1; P&L at the stop after the add = 1*100 + 1*(100,100-100,200) = 0. Same with stop = e1: locked 0 -> q_add 0 < 0.25 -> skip. Mode `day` with closed day R = 0.5, D1 = 300, r1 = 1: U = 300, budget = 150, stop = 99,900 (below e1 by 100): locked = -100, dist = 300, q_add = 50/300 = 0.1667 < 0.25 -> skip. Costs, model B short above: q = 1, D1 = 299.85, target 99,400 exit maker: gross R = 550/299.85 = 1.8343; rest entry (maker) fee R = 0; confirm entry (taker): fee R = 0.0005*99,950/299.85 = 49.975/299.85 = 0.16667, net 1.6676; a stop exit with taker in and taker out: fee R = 0.0010*99,950/299.85 = 0.3333.

**28.5 Day rules and windows.** Unit = the UTC date. Day R = sum of `risk_u * net_r` of its trades (risk_u default 1; no trade -> 0). NY window (SIM, DST-aware, SOURCED P33 cash open): for a Mon-Fri UTC date D not in US_CLOSED, `open(D) = 13:30 UTC` if US DST holds (second Sunday of March <= D < first Sunday of November) else `14:30 UTC`; window = 390 one-minute bars, no new entries (first legs or adds) at or after open+330 (OURS NS-fixed), exit at the last window bar close. London: open 07:00 UTC in UK BST (last Sunday March <= D < last Sunday October) else 08:00, 390 bars; Asia 00:00 UTC, 390 bars. Closed prefix sums `P = [0, carry, carry+n1, carry+n1+n2, ...]`, C = last, peak = max(P). `first_leg_allowed` is False iff any of: n_first_legs >= 10 (SAFETY P30); `C <= -3` (SAFETY P29, value unsourced); some `P_k <= -1` and a later `P_m >= 0` (stop after recovery, SOURCED P28, -1 OURS); `peak > 0` and `C <= 0` (floor at day R 0, SOURCED P26). Risk of the next first leg `r1 = 0` if not allowed, else `min(1, C)` if peak > 0, else 1 (SOURCED P27). Day gate (models A and C, OURS NS-grid g in {off, 0.8}): at bar i >= open+60, `G = (max h - min l over [open, i]) / median over the prior 20 valid weekdays of the same elapsed range`, open iff `G >= g`; closed before open+60 when g is not off. Empty history or a median <= 0 -> G undefined -> closed (SAFETY, amended 2026-11-01; hand numbers: prior [1000]*20, elapsed 60: day range 800 -> open (G = 0.8), 790 -> closed, empty or [0]*20 -> closed). Ex-post day type (reporting only): trend iff `|c_last - o_first| / (Hwin - Lwin) >= 0.6`, else balance. Sample size `n = ceil(((1.96+0.8416)*SD/delta)^2)`; CI half-width `1.96*SD/sqrt(n)`.
*Worked:* Monday 2026-10-26 (before Sunday 2026-11-01): DST in force, open 13:30, last entry bar before 19:00, window ends 20:00. Monday 2026-11-02: DST over, open 14:30. Monday 2026-03-09 (second Sunday of March 2026 is 03-08): open 13:30. Day rules: closed nets [-1, +1.2]: P = [0, 0, -1, 0.2]; P_2 = -1 <= -1 and P_3 = 0.2 >= 0 -> not allowed (r1 = 0). Nets [+2, -2]: P = [0, 0, 2, 0], peak 2 > 0 and C = 0 <= 0 -> not allowed. carry 1.5, no trades: C = 1.5, peak 1.5, allowed, r1 = min(1, 1.5) = 1; carry 0.4: r1 = 0.4. Nets [-1, -1, -1.5]: C = -3.5 <= -3 -> not allowed. Gate: today range 800 against prior median 1,000 -> G = 0.8 >= 0.8 open; 790 -> 0.79 closed. Sample size SD 1.5, delta 0.2: (2.8016*7.5)^2 = 21.012^2 = 441.5 -> 442; SD 1.82 -> 650. CI half-width n 30, SD 1.5: 1.96*1.5/5.4772 = 0.5368.

**28.6 Code vs spec: RESOLVED 2026-11-01 (card fabio-v3-code-vs-formulas-s28-diffs; the commit that introduced this line, first commit containing this heading).** (1) contiguity of [i-N, i] is the spec (28.1/28.2 amended, code fails closed on a gap; test_signals `test_s28_contiguity_gap_fails_closed`); (2) multi-leg adds are built as `simulate_trade_legs` in `manage.py` (28.4; `simulate_trade`/`walk_trade` unchanged and still first-leg only; not wired into the engine, so no golden number moved); (3) `day_gate_open` closed on empty history or median <= 0 is the spec (28.5 amended, SAFETY; test_day_gates `test_s28_day_gate_boundaries_and_empty_history`). Values matched on every worked number before this change.

## 29. Tom VP return-to-value count (`backtest/vp_return_to_value.py`; pre-registration `research/tom_transfer_2026-10-11/vp_return/PRE_REG.md`) - added 2026-11-01

A COUNT of Tom's claim "about 30% of the time ... the other 70% he will try and strive to run back" (`extracts/processed/tom/extract_BB3c8visnkI.md:38`, SOURCED claim, never a gate). No entry, stop, target or cost. Derived from PRE_REG.md and the module docstring; the worked numbers below were computed by hand, then compared with the code.

**29.1 Definitions (5m bars, one UTC day D at a time, complete days only: 288 bars in D and D-1).**
- Prior-day value: profile of the 5m bars of D-1 by section 18.1 (bin w = 10 USD NO-SOURCE, value area 70%): `poc_price`, `vah`, `val`.
- Event (OURS): the first 5m bar of D whose CLOSE is above VAH or below VAL; `side = +1` above, `-1` below; one event per day at most; uses bars up to that close only. No such bar -> NO-EVENT (counted, not in the share).
- RETURN (OURS): a bar strictly after the event bar, still in D, whose range contains the prior POC (`l <= poc <= h`). Else RUN-AWAY. An event on the last bar of the day has no later bar: censored, counted as no return.
- Back inside value (OURS, side column): a later bar of D closes in `[VAL, VAH]`.
- Part B accepted away (N in {3, 6, 12} NO-SOURCE from the card, all reported, never chosen by outcome): applicable iff the event bar plus N-1 later bars exist in D (`e+N-1 <= 287`); accepted_N iff the event bar and the next N-1 bars all CLOSE beyond the same edge (all above VAH, or all below VAL); outcome = a bar strictly after the N-th close touches the POC (no bar left: censored, counted no return). Reads "beyond the LVN side of value" as the value-area edge (OURS; no LVN is built).
- Naked-POC columns (SOURCED threshold `NakedPocTracker.java:26`, 0.3%; use OURS): over ALL days, share on which any bar of D touches the D-1 POC exactly, and share on which any bar has `l <= poc*(1+0.003)` and `h >= poc*(1-0.003)`.
- Placebo (NO-SOURCE, section 18.6 adapted to one refresh per day): POC, VAH, VAL all shifted by `d * R_ref`, `R_ref` = ATR14 of 1h bars (section 12) of the last 1h bar closed at or before 00:00 UTC of D; d cycles (-3, -2, -1, -0.5, 0.5, 1, 2, 3) by `(day index in the study) mod 8`; same event and outcome rules. The pooled placebo is the primary comparison.
- Statistics (section 18.7): return share = returns / events; 95% CI = day-block bootstrap, 2000 resamples, `default_rng(20261009)`, share = sum over resampled days / events in them; difference real minus placebo uses the SAME resampled days. A row with n < 100 events is UNDERPOWERED, never "no effect". DEV window only (2022-01-01 .. 2024-06-30), OURS. Result classes written before any run: difference CI contains 0 -> a property of any band, not of value; share CI excludes 70% -> his number does not reproduce.

**29.2 Worked example (by hand).** Prior-day levels from the section 18.1 Worked A (w = 1): POC 1.5, VAH 2.0, VAL 1.0. Day D bars (h, l, c): 0: (1.8, 1.2, 1.6); 1: (2.4, 1.7, 2.2); 2: (2.6, 2.1, 2.5); 3: (2.7, 2.3, 2.6); 4: (2.5, 1.4, 1.9); 5: (2.0, 1.8, 1.9). First close outside [1.0, 2.0]: bar 1 (2.2 > 2.0), e = 1, side +1, bars left = 4. Bars 2-5 contain 1.5? bar 2 (l 2.1) no, bar 3 no, bar 4 (1.4 <= 1.5 <= 2.5) yes -> RETURN. Closes after the event 2.5, 2.6, 1.9, 1.9: 1.9 is inside -> back inside value = yes. Part B N = 3: closes of bars 1-3 = 2.2, 2.5, 2.6 all > 2.0 -> accepted; bars after the 3rd close are 4 and 5, bar 4 touches -> returned. N = 6: needs e+5 = 6 <= 5, no -> not applicable (so N = 12 too). Naked: bar 4 contains 1.5 -> exact yes; near yes. Placebo with day index 3, R_ref = 2: d = PLACEBO_D[3 mod 8] = -0.5, shift = -1.0 -> POC 0.5, VAH 1.0, VAL 0.0; bar 0 closes 1.6 > 1.0 -> event at e = 0, side +1; no later bar has `l <= 0.5` (lowest later low is 1.4) -> RUN-AWAY. Shares over three such days: real events [1,1,1] with returns [1,1,0] -> 2/3 = 0.6667; placebo returns [0,1,0] -> 1/3; difference 0.3333.

**29.3 Code comparison (2026-11-01).** `analyse_day`, `shift_levels`, `build_days` (D and D-1 both 288 bars, R_ref from the last 1h bar closed at or before 00:00, day index = D minus the start day), `_naked`, `share`, `diff` match 29.1 and the numbers above. Recorded, not changed: censored events (event on the last bar, or no bar after the N-th close) enter the share as no-return, which is what PRE_REG.md's "else RUN-AWAY" gives and is also reported in the `censoring` audit (post-hoc, OURS, 12-bar restriction).

## 30. ADX/DI (Wilder) (`backtest/layers/adx/adx.py`; census `research/adx_di_2026-11/census.py`) - added 2026-11-07
VERIFIED-TV 2026-11-07: TradingView built-in DMI 14/14, BINANCE:BTCUSDT 1D, bars 2026-01-15 and 2026-05-15 match to 0.01 on DI+, DI-, ADX (research/adx_di_2026-11/TV_CROSSCHECK.md); the last csv bar was partial, refresh after 00:00Z.

Context indicator only (card adx-di-2d-cross-census-1107); Wilder's definitions, n = 14 by default, every threshold in the census is OURS.

**30.1 Definitions.** For bar i >= 1: `TR_i = max(H_i - L_i, |H_i - C_{i-1}|, |L_i - C_{i-1}|)`; `up = H_i - H_{i-1}`, `dn = L_{i-1} - L_i`; `+DM_i = up if up > dn and up > 0 else 0`; `-DM_i = dn if dn > up and dn > 0 else 0`. Wilder smoothing: first value `S` = sum of the first n values (bars 1..n), then `S_i = S_{i-1} - S_{i-1}/n + x_i`. `DI+ = 100 * S(+DM) / S(TR)`, `DI- = 100 * S(-DM) / S(TR)` (both 0 if S(TR) = 0), first defined at bar n. `DX = 100 * |DI+ - DI-| / (DI+ + DI-)` (0 if the sum is 0). `ADX` = mean of the first n DX (first defined at bar 2n-1), then `ADX_i = (ADX_{i-1} * (n-1) + DX_i) / n`. Cross: the sign of `DI+ - DI-` flips (strict, zeros ignored); red = DI- over DI+, green = DI+ over DI-.

**30.2 Worked toy (n = 3, 20 bars, by hand).** H = 10,11,12,11,13,14,13,12,11,12,13,15,14,13,12,11,12,14,15,14; L = 8,9,10,9,10,12,11,10,9,10,11,12,12,11,10,9,10,11,13,12; C = 9,10,11,10,12,13,12,11,10,11,12,14,13,12,11,10,11,13,14,13. Bars 1-3: TR = 2, 2, 2; +DM = 1, 1, 0; -DM = 0, 0, 1. Bar 3: S(TR) = 6, S(+DM) = 2, S(-DM) = 1 -> DI+ = 33.333, DI- = 16.667, DX = 100 * 16.667 / 50 = 33.333. Bar 4: TR = 3 (H 13 - C 10), +DM = 2, -DM = 0; S(TR) = 6 - 2 + 3 = 7, S(+DM) = 2 - 2/3 + 2 = 10/3, S(-DM) = 1 - 1/3 + 0 = 2/3 -> DI+ = 47.619, DI- = 9.524, DX = 66.667. Bar 5: TR = 2, +DM = 1, -DM = 0 (dn = L4 - L5 = -2); S(TR) = 7 - 7/3 + 2 = 6.667, S(+DM) = 10/3 - 10/9 + 1 = 3.222, S(-DM) = 2/3 - 2/9 = 0.4444 -> DI+ = 48.333, DI- = 6.667, DX = 100 * 41.667 / 55 = 75.758; ADX_5 = (33.333 + 66.667 + 75.758) / 3 = 58.586 (= 5800/99). Bar 6: TR = 2, +DM = 0, -DM = 1 -> S(TR) = 6.444, S(+DM) = 2.148, S(-DM) = 1.296, DI+ = 33.333, DI- = 20.115, DX = 24.731, ADX_6 = (58.586 * 2 + 24.731) / 3 = 47.301 (= 435500/9207). Bar 19: ADX = 34.938 (exact fraction in test_adx.py).
## 31. Squeeze Momentum (LazyBear) (`backtest/layers/squeeze/squeeze.py`; state `research/tv_favorites_2026-11/SQUEEZE_STATE.md`) - added 2026-11-07
VERIFIED-TV (momentum only), 2026-11-07, login C: BYBIT:BTCUSDT.P 1D momentum matches TradingView exactly on 3/3 bars (2026-08-19 858.4, 2026-09-20 -1642.2, 2026-10-31 -2441.8). Squeeze on/off dots: NOT VERIFIED (unreadable in Chrome; operator asked).
Context columns only (card squeeze-momentum-engine-1107, SPEC_ENGINES.md A); defaults SOURCED from LazyBear's public "Squeeze Momentum Indicator" Pine script (length 20, BB mult 2.0, KC mult 1.5, true range); everything else OURS.

**31.1 Definitions.** BB: basis = SMA(close, n), dev = mult * POPULATION stdev (section 22); half-width BBhw = 2.0 * sd. KC: ma = SMA(close, n), rangema = SMA(TR, n), half-width KChw = 1.5 * rangema; `TR_0 = H_0 - L_0`, `TR_i = max(H_i - L_i, |H_i - C_{i-1}|, |L_i - C_{i-1}|)`. Both bands centre on the same SMA, so BB lower > KC lower and BB upper < KC upper is exactly `BBhw < KChw`: squeeze ON; `BBhw > KChw`: squeeze OFF; equal: neither (OURS: ties within 1e-9 relative count as equal, so float noise cannot flip a flag). `src_i = C_i - ( (HH_i + LL_i)/2 + SMA(C, n)_i ) / 2` with HH/LL the highest high / lowest low of the last n bars. `momentum_i` = value at the newest bar of the least-squares line through the last n values of src (x = 0..n-1, newest x = n-1): `mean(y) + slope * (n-1 - (n-1)/2)`, `slope = sum((x - (n-1)/2) * y_x) / sum((x - (n-1)/2)^2)`. First defined: flags at bar n-1, momentum at bar 2n-2.

**31.2 Worked toy (all lengths n = 5, 25 bars; reduced from 20 because a 20-length momentum needs 38 bars; OURS).** C = 10..19 (step 1, bars 0-9), 19.5 (bars 10-17), then 21, 23, 25, 26, 28, 30, 31; H = C + 0.5 and L = C - 0.5 on bars 0-9; H = 19.75, L = 19.25 on bars 10-17; H = 21.5, 23.5, 25.5, 26.5, 28.5, 30.5, 31.5 and L = 19.5, 21.5, 23.5, 25.5, 26.5, 28.5, 29.5 on bars 18-24. Bar 4: C = 10..14, sd^2 = 2, BBhw = 2 * sqrt(2) = 2.828; bars 1-4 have |H - Cprev| = 1.5 so TR = 1, 1.5, 1.5, 1.5, 1.5, SMA = 1.4, KChw = 2.1 < 2.828 -> OFF. (Square form used in the test: BBhw^2 = 8 vs KChw^2 = 4.41.) Bars 12-17 ON (bar 14: closes all 19.5, sd = 0, BBhw = 0 < KChw^2 = 0.6806). Bar 18: closes 19.5 x4 and 21, mean 19.8, sd^2 = 0.36, BBhw = 1.2; TR_18 = max(H 21.5 - L 19.5 = 2, 21.5 - 19.5 = 2, 19.5 - 19.5 = 0) = 2 and bars 14-17 TR 0.5 -> SMA = 0.8, KChw = 1.2: equal -> neither. Momentum, bar 8: src is exactly 2 on bars 4-8 (e.g. bar 4: HH 14.5, LL 9.5, mid 12, SMA 12, src = 14 - 12 = 2) so the line is flat at 2.0. Bar 10: HH = 19.75, LL = 15.5, mid 17.625, SMA(16,17,18,19,19.5) = 17.9, src = 19.5 - 17.7625 = 1.7375; y = 2, 2, 2, 2, 1.7375, mean 1.9475, slope = (-4 - 2 + 0 + 2 + 3.475)/10 = -0.0525, momentum = 1.9475 + 2 * (-0.0525) = 1.8425. Hand values in test_squeeze.py: momentum bars 8..24 = 2, 2, 1.8425, 1.3775, 0.785, 0.225, -0.125, -0.18, -0.1275, -0.0475, 0.5475, 1.6025, 2.815, 3.485, 3.885, 3.97, 3.6075; flags OFF bars 4-11, ON 12-17, neither 18, OFF 19-24.
## 32. Volume Flow Indicator (LazyBear / Katsanos) (`backtest/layers/vfi/vfi.py`; state `research/tv_favorites_2026-11/VFI_STATE.md`) - added 2026-11-07
Context columns only (card vfi-engine-1107, SPEC_ENGINES.md B); defaults SOURCED from LazyBear's public "Volume Flow Indicator" Pine script after Katsanos (2004): length 130, coef 0.2, vcoef 2.5, stdev length 30, smoothing length 3; everything else OURS. No signal, no order.

**32.1 Definitions.** `typ = (H+L+C)/3`; `inter_i = ln(typ_i) - ln(typ_{i-1})` (i >= 1); `vinter_i` = POPULATION stdev (section 22) of inter over the last stdev_len values (first at i = stdev_len); `cutoff_i = coef * vinter_i * C_i`; `vave_i` = SMA(volume, length) over bars i-length..i-1 (the PREVIOUS bar's average, current volume excluded; first at i = length); `vmax_i = vcoef * vave_i`; `vc_i = min(V_i, vmax_i)`; `mf_i = typ_i - typ_{i-1}`; `vcp_i = +vc_i if mf_i > cutoff_i; -vc_i if mf_i < -cutoff_i; else 0` (strict; a tie is 0); `vfi_i = SUM(vcp, length)_i / vave_i`. Smoothed output = SMA(vfi, smooth) (LazyBear `smoothVFI`, `ma = sma`; `smooth` <= 1 returns vfi itself); `smooth_kind="ema"` gives EMA(vfi, smooth), alpha = 2/(smooth+1), SMA-seeded (section 4).
- **Conventions OURS:** vfi is None until the sum window is fully real data, i.e. from bar `max(stdev_len, length) + length - 1` (Pine treats the earlier na comparisons as false, so TradingView shows a partial-warmup value built from zeros there; we show None). Smoothed is None until `smooth` vfi values exist.
- **Where this differs from the SPEC_ENGINES.md B text (DECISION OURS, flagged for the TradingView check by Lead C):** the spec line says `vfi = SMA(vcp, 130) / vave`, `vave = SMA(volume, 50)[1]` and smoothing EMA(3). LazyBear's script (and Katsanos) uses `sum(vcp, length) / vave`, `vave = sma(volume, length)[1]` and `sma(vfi, 3)` when smoothVFI is on. We follow the script as recalled (no network source was read in this session; the recall is unverified until C looks). SMA-instead-of-sum would only divide vfi by `length` (the sign, and so every zero cross, is identical), and the EMA smoothing is one argument away (`smooth_kind="ema"`). Lead C settles both on the operator's TradingView, where the script source is visible.

**32.2 Worked toy (stdev_len = 2, length = 3, smooth = 2, coef 0.2, vcoef 2.5; reduced from 30/130/3 so it is hand-sized; OURS).** H = C + 1, L = C - 1 so `typ = C`. C = 100, 102, 101, 105, 105, 104, 110, 108, 108.25 (bars 0-8); V = 10, 20, 30, 20, 40, 10, 100, 30, 50. The population stdev of two numbers is `|a - b| / 2`. For bars 3-8, `vave` = 20, 70/3, 30, 70/3, 50, 140/3, so `vmax` = 50, 175/3, 75, 175/3, 125, 350/3 and `vc` = 20, 40, 10, 175/3 (volume 100 is capped), 30, 50.
- Bar 3: mf = +4; inter_2 = ln(101/102) = -0.009852, inter_3 = ln(105/101) = 0.038839, vinter = 0.024345, cutoff = 0.2 * 0.024345 * 105 = 0.5113; 4 > cutoff -> vcp = +20.
- Bar 4: mf = 0 (a tie against a positive cutoff) -> vcp = 0.
- Bar 5: mf = -1; inter_5 = ln(104/105) = -0.009569, inter_4 = 0, vinter = 0.004785, cutoff = 0.0995; -1 < -0.0995 -> vcp = -10.
- Bar 6: mf = +6; inter_6 = ln(110/104) = 0.056090, vinter = 0.032830, cutoff = 0.7222; 6 > cutoff -> vcp = +vc = 175/3 = 58.3333 (uncapped it would be +100).
- Bar 7: mf = -2; inter_7 = ln(108/110) = -0.018349, vinter = 0.037220, cutoff = 0.8040; -2 < -0.804 -> vcp = -30.
- Bar 8: mf = +0.25; inter_8 = ln(108.25/108) = 0.002312, vinter = (0.002312 + 0.018349)/2 = 0.010331, cutoff = 0.2 * 0.010331 * 108.25 = 0.2237; 0.25 > 0.2237 -> vcp = +50. (A SAMPLE stdev, divisor n-1, would give cutoff 0.3163 and vcp = 0: the variant, not used.)
- vfi (first at bar 5 = max(2, 3) + 3 - 1): bar 5 sum(vcp, bars 3-5) = 20 + 0 - 10 = 10, vave 30 -> 1/3 = 0.333333. Bar 6 sum = 0 - 10 + 175/3 = 145/3, vave 70/3 -> 145/70 = 29/14 = 2.071429. Bar 7 sum = -10 + 175/3 - 30 = 55/3, vave 50 -> 11/30 = 0.366667. Bar 8 sum = 175/3 - 30 + 50 = 235/3, vave 140/3 -> 47/28 = 1.678571. Bars 0-4 None.
- Smoothed SMA(2), first at bar 6: (1/3 + 29/14)/2 = 101/84 = 1.202381; bar 7 (29/14 + 11/30)/2 = 128/105 = 1.219048; bar 8 (11/30 + 47/28)/2 = 859/840 = 1.022619. EMA(2) variant (alpha 2/3, seed at bar 6 = 101/84): bar 7 = (2/3)(11/30) + (1/3)(101/84) = 271/420 = 0.645238; bar 8 = (2/3)(47/28) + (1/3)(271/420) = 1681/1260 = 1.334127.
VERIFIED-TV 2026-11-07, login C: TradingView "Volume Flow Indicator [LazyBear]" (VFI_LB 130 0.2 2.5 5), BYBIT:BTCUSDT.P 1D, raw vfi matches on 4/4 bars within the one-decimal display (2026-10-04 0.6 vs +0.641, 2026-10-08 -0.7 vs -0.736, 2026-10-09 1.4 vs +1.436, 2026-11-06 8.5 vs +8.518). The engine's reading of the script (sum(vcp, 130) / SMA(volume, 130)[1], SMA smoothing) is the verified one; the SPEC_ENGINES.md B text (50/130 split, EMA 3) was Lead C's recall and is superseded.

## Verification note (this audit, 2026-09-28)

Every case number in `layers/timeframe/TEST_PLAN.md`, `layers/rsi/TEST_PLAN.md`,
`layers/TEST_PLAN_runner.md` and `layers/cryptocred/TEST_PLAN.md` was independently re-derived using a
throwaway Python scratch implementation written directly from this file's definitions (never by
importing or reading the layer modules under test), and matched the existing plan values exactly. No
plan numbers required correction. The one correction made was to `layers/rsi/TEST_PLAN.md`'s header
(Case C1 provenance claim, which described deriving from `bt/bt_rsi.py.new` — against the "never derive
from code" rule even though the module's own math turned out to match textbook Wilder); see that file's
diff and the audit report for detail.

**19.9 Contract v1.1 notes (2026-10-26).** Close arm penetration over ia..ib uses closes only: anchors (15,100), (27,106), L(20) = 100 + 6*5/12 = 102.5; close 101 fails (1.5 below, tolerance 1.0), a wick at 95 with close 100 on the anchor bar passes. Availability window: pivot b at ib = 27, k = 3, available at 30; bars 28..30 grant no contact/reset/eligibility; a close below L(28) = 106.5 on bar 28 (close 106.4) rejects the line as `broken_before_available`. E11: inner line (15,27) breaks; pivot at 40 pairs with 15 (outer line) but not with 27.
