# Lab formula spec recount — 2026-10-22

Verdict: PASS — `test_formula_spec.py` independently recomputes every sub-id F11.1–8, F18.1–7, F19.1–8, F20.1–4, and F21.1–9 from the canonical `FORMULAS.md` paragraph of each sub-id without echo fallback. Sub-ids lacking computable numbers (F18.4, F20.2, F20.4) are classified and handled as `NOT_APPLICABLE` with cited paragraph text.

## 1. Sub-IDs Inventory

Grepped via: `git grep -n -E "^\*\*(11|18|19|20|21)\.[0-9]+ " MyTradingSys/backtest/layers/FORMULAS.md`

### Section 11 (Execution math)
- **11.1** [FORMULAS.md:213](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L213): `Tick-size price snapping — directional, by order purpose and side` — SOURCED (`FORMULAS.md:213-241`). Rule: Entry BUY floor / SELL ceil; Stop LONG ceil / SHORT floor; Target LONG floor / SHORT ceil. Tick 0.5.
- **11.2** [FORMULAS.md:242](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L242): `Contract size (amount) rounding — floor only, reject below minimum` — SOURCED (`FORMULAS.md:242-252`). Minimum 10 USD, floor in 10 USD increments.
- **11.3** [FORMULAS.md:253](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L253): `Ladder entry rung prices` — SOURCED (`FORMULAS.md:253-260`). `step = (high - low)/(N - 1)`.
- **11.4** [FORMULAS.md:261](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L261): `Ladder / multi-fill average price for an inverse contract — harmonic mean weighted by USD size` — SOURCED (`FORMULAS.md:261-279`). `avg_price = sum(size_i) / sum(size_i / p_i)`.
- **11.5** [FORMULAS.md:280](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L280): `Inverse-contract average fill price (live fills)` — SOURCED (`FORMULAS.md:280-285`). Same harmonic mean on actual fills.
- **11.6** [FORMULAS.md:286](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L286): `Worst-case loss at a fixed-percent stop (inverse contract)` — SOURCED (`FORMULAS.md:286-303`). `worst_case_loss_usd = -size * abs(E - S) / E`.
- **11.7** [FORMULAS.md:304](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L304): `Target price from PnL%` — SOURCED (`FORMULAS.md:304-312`). `T = E * (1 + pct/100)`, tick-snapped toward entry.
- **11.8** [FORMULAS.md:313](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L313): `Notional cap` — SOURCED (`FORMULAS.md:313-323`). `notional = abs(size)` (USD) or `abs(size) * mark_price`.

### Section 18 (Volume profile)
- **18.1** [FORMULAS.md:415](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L415): `Profile of a bar set (bin grid w = 10.0 USD, NO-SOURCE, engine uses about 5 USD)` — SOURCED (`FORMULAS.md:415-431`). Bar uniform overlap into bins; POC lowest bin holding max volume (`poc_price = k_poc*w + w/2`). Worked A: bars `(0,2,6)`, `(1,3,4)`, `(1,2,10)` at w=1.0 gives POC bin 1, poc_price 1.5.
- **18.2** [FORMULAS.md:432](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L432): `Fractal pivots (NO-SOURCE width n; FORMULAS section 9 fixed-width fractal, strict comparisons)` — SOURCED (`FORMULAS.md:432-439`). Strict pivot high test `h[i] > h[j] for j in [i-n, i+n], j != i`. Worked: n=1, h=[1,3,2,5,4,1,2] gives pivot high at index 1 (True).
- **18.3** [FORMULAS.md:440](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L440): `Size filter (NO-SOURCE k)` — SOURCED (`FORMULAS.md:440-444`). Meaningful iff `|price_p - price_q| >= k * ATR14`.
- **18.4** [FORMULAS.md:445](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L445): `Anchored families` — SOURCED (`FORMULAS.md:445-457`). Defines profile interval windows and 15m grid refreshes; no inline formula computation. Status: NOT_APPLICABLE.
- **18.5** [FORMULAS.md:458](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L458): `Touch event and R-multiple outcome` — SOURCED (`FORMULAS.md:458-474`). `net_R = (side * (exit - L) - fee_in * L - fee_out * exit) / R`. Worked: Long L=100, R=2, exit=102, fees=0.0005 gives net_R 0.9495.
- **18.6** [FORMULAS.md:475](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L475): `Placebo` — SOURCED (`FORMULAS.md:475-478`). `placebo = L + d * R_ref` with d cycling deterministically through `(-3, -2, -1, -0.5, +0.5, +1, +2, +3)` mod 8.
- **18.7** [FORMULAS.md:479](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L479): `Statistics` — SOURCED (`FORMULAS.md:479-487`). Day-block bootstrap mean. Worked: Day A [1, 3], Day B [-2], resample (A, B) mean = 2 / 3 = 0.666666666667 (0.6667).

### Section 19 (Trend-lines)
- **19.1** [FORMULAS.md:489](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L489): `Pivot with k bars each side, strict` — SOURCED (`FORMULAS.md:489-491`). Swing low `low[i] < low[j]`. Worked: k=3, lows [9,8,7,5,6,7,8] index 3 is pivot (True).
- **19.2** [FORMULAS.md:492](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L492): `Line through anchors (ia,pa), (ib,pb)` — SOURCED (`FORMULAS.md:492-494`). Linear `L(t) = pa + (pb - pa)*(t - ia)/(ib - ia)`. Worked: ia=10, pa=100, ib=20, pb=110, t=25 gives L(25) = 115.0.
- **19.3** [FORMULAS.md:495](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L495): `ATR for the contract` — SOURCED (`FORMULAS.md:495-496`). Plain SMA of True Range (OURS). Worked: ranges [2.0, 2.5, 2.0], length 3 gives 2.166666666667.
- **19.4** [FORMULAS.md:497](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L497): `Slope` — SOURCED (`FORMULAS.md:497-499`). `slope_atr = (L(ib)-L(ia))/(ib-ia)/ATR_b`. Worked: pa=100, pb=110, dt=10, ATR_b=4 gives 0.25.
- **19.5** [FORMULAS.md:500](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L500): `Touch, penetration, break (support; resistance mirrors)` — SOURCED (`FORMULAS.md:500-502`). Touch tolerance 0.25*4 = 1; contact iff `low <= L + 1`. Worked: L=115, low 115.8 contacts (True).
- **19.6** [FORMULAS.md:503](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L503): `Contact episode and reset` — SOURCED (`FORMULAS.md:503-504`). Reset distance 1.0*ATR_b = 4; reset when `low > L + 4`. Worked: L=115, low 120.0 > 119.0 (True).
- **19.7** [FORMULAS.md:505](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L505): `Volume anchor test` — SOURCED (`FORMULAS.md:505-506`). Pass iff `V >= 2*M`. Worked: M=140, V=300 gives ratio 2.142857142857 (2.143).
- **19.8** [FORMULAS.md:507](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L507): `Arm B third anchor` — SOURCED (`FORMULAS.md:507-511`). Anchor within tolerance iff `|price - L| <= 0.25*ATR_b`. Worked: L=120, price=119.5, ATR_b=4, diff 0.5 <= 1.0 (True).

### Section 20 (WaveTrend)
- **20.1** [FORMULAS.md:513](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L513): `Formula` — SOURCED (`FORMULAS.md:513-514`). `ap = (h + l + c)/3`.
- **20.2** [FORMULAS.md:515](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L515): `Conventions the source does not state` — SOURCED (`FORMULAS.md:515-516`). Warmup 200 bars, NaN conditions, event rules; no isolated formula. Status: NOT_APPLICABLE.
- **20.3** [FORMULAS.md:517](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L517): `Worked, by hand` — SOURCED (`FORMULAS.md:517-522`). Two bars ap=[10, 12]: Bar 1 `esa=114/11`, `d=36/121`, `ci=(18/11)/(0.015*36/121) = 366.666666667` (366.6667).
- **20.4** [FORMULAS.md:523](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L523): `Golden series` — SOURCED (`FORMULAS.md:523-527`). Parity against external CSV `golden_wt_btcusdt_1h_dev_2022-01.csv`; no inline formula computation. Status: NOT_APPLICABLE.

### Section 21 (Krown trading rules)
- **21.1** [FORMULAS.md:529](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L529): `Zone` — SOURCED (`FORMULAS.md:529-530`). Zone `[min(c, E), max(c, E)]`. Worked: c=104, extreme=90 gives zone high 104.0, low 90.0.
- **21.2** [FORMULAS.md:531](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L531): `Volume` — SOURCED (`FORMULAS.md:531-532`). `ratio = V / mean(prior 20 volumes)`. Worked: M=100, V=250 gives 2.5.
- **21.3** [FORMULAS.md:533](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L533): `Strict engulfing` — SOURCED (`FORMULAS.md:533-534`). Bullish: `low < prior_low AND close > prior_high`. Worked: prior h=105, l=100, bar l=99, c=106 is bullish (True).
- **21.4** [FORMULAS.md:535](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L535): `Dominant low / dominant lower high` — SOURCED (`FORMULAS.md:535-536`). Dominant low = `min(lows)` between latest swing highs. Worked: k=1, at t=7 dominant low = min(l3..l6) = 8.0.
- **21.5** [FORMULAS.md:537](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L537): `BBWP` — SOURCED (`FORMULAS.md:537-538`). `bbw = 4*std/SMA`. `BBWP = 100 * count(prev < curr) / lookback`. Worked: basis=2, lookback=3, closes [10,10,12,11,15,15,14], BBWP[4] = 100.0%.
- **21.6** [FORMULAS.md:539](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L539): `Moving averages and leash` — SOURCED (`FORMULAS.md:539-540`). EMA(n) seeded with SMA, alpha=2/(n+1). Worked: EMA(5) of [1,2,3,4,5,6] gives index 5 = 3 + (6-3)/3 = 4.0.
- **21.7** [FORMULAS.md:541](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L541): `RSI and zones` — SOURCED (`FORMULAS.md:541-542`). Wilder RSI smoothing. Worked: period 2, closes [10,11,10,12] gives RSI[3] = 100 - 100/6 = 83.3333333333%.
- **21.8** [FORMULAS.md:543](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L543): `Range and coil` — SOURCED (`FORMULAS.md:543-544`). Position = `(close - bottom) / height`. Worked: highs [10,11,10.5,11], lows [9,9.5,9,9.5], close 9.4 gives position (9.4 - 9)/2 = 0.2.
- **21.9** [FORMULAS.md:545](file:///F:/MTS/gq/lab-formula-spec-recount/MyTradingSys/backtest/layers/FORMULAS.md#L545): `Tops` — SOURCED (`FORMULAS.md:545-555`). Signals in rolling window w=3. Worked: Candle at 5, volume at 6, BBWP at 7, window 5..7 has count 3 (fires at t=7).

## 2. Fail-First Execution

Running `python MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py` before updating `gen_examples.py` resulted in the expected fail-closed assertion because the existing `examples.json` sub-id rows did not match the sub-id recount formulas:
```
======================================================================
FAIL: test_every_catalog_id_has_spec_example_and_independent_tape_recount (__main__.FormulaSpec.test_every_catalog_id_has_spec_example_and_independent_tape_recount)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "F:\MTS\gq\lab-formula-spec-recount\MyTradingSys\research\layer_lab\formula_spec_text\test_formula_spec.py", line 173, in test_every_catalog_id_has_spec_example_and_independent_tape_recount
    else: raise AssertionError(f"unknown formula name: {name!r} ({ident})")
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: unknown formula name: 'bin index' (F18.1)

----------------------------------------------------------------------
Ran 2 tests in 0.033s

FAILED (failures=1)
```

## 3. Findings

| Severity | File:line / command | Finding | Evidence | Disposition |
|---|---|---|---|---|
| INFO | `FORMULAS.md:445` | F18.4 defines anchored families and grid intervals rather than a standalone formula. | "levels refreshed on a 15-minute grid... Developing; need >= 12 bars... Each profile contributes three levels: POC, VAH, VAL" | Labelled NOT_APPLICABLE in `examples.json` and `FORMULAS_SPEC.md`. |
| INFO | `FORMULAS.md:515` | F20.2 specifies operational conventions (warmup periods, NaN conditions, event rules) rather than an isolated formula. | "EMA seeded with the first valid source value; output used only after WARMUP=200 bars... Zones from wt1: ob2 >= 60, ob1 >= 53... available_at = bar_open + timeframe" | Labelled NOT_APPLICABLE in `examples.json` and `FORMULAS_SPEC.md`. |
| INFO | `FORMULAS.md:523` | F20.4 specifies external golden series dataset verification rather than an inline formula. | "wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv: 400 BTCUSDT 1h bars... Compared at 1e-9 (OURS) after bar 200" | Labelled NOT_APPLICABLE in `examples.json` and `FORMULAS_SPEC.md`. |

## 4. Verification

- `python MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py`:
  ```
  ..
  ----------------------------------------------------------------------
  Ran 2 tests in 0.043s

  OK
  ```
- `python -m pytest MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py -q -p no:cacheprovider`:
  ```
  2 passed in 0.19s
  ```
- `python scripts/dev/run_extra_tests.py`:
  ```
  ok   MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py: 2 passed in 0.23s
  ```
- `examples.json` contains 59 entries (23 parent IDs F01–F23 and 36 sub-IDs F11.1–8, F18.1–7, F19.1–8, F20.1–4, F21.1–9).
- `FORMULAS_SPEC.md` worked examples updated from `examples.json`.
- `FORMULAS.md` was preserved read-only with no modifications.
- No `REVIEWED` stamp was added.
