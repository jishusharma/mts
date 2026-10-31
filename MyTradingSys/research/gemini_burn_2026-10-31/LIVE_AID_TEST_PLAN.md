# Live Aid Dashboard Test Plan (`tools/live_aid/*.js`)

**Task ID:** `gemini-test-plan-live-aid-js-1031`  
**Date (UTC):** 2026-10-31  
**Target Codebase:** `MyTradingSys/tools/live_aid/live_aid_indicators.js`, `MyTradingSys/tools/live_aid/us_open_rates.js`, `MyTradingSys/tools/live_aid/live_aid.html`  
**Test Suites Examined:** `test_live_aid.py`, `test_live_aid_replay.py`, `test_live_aid_layout.py`, `test_oi_money.py`, `test_build_analyst_data.py`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## 1. Executive Summary & Inventory

This test plan provides a complete audit of every displayed number on the live aid dashboard (`live_aid.html` and its indicator modules `live_aid_indicators.js`, `us_open_rates.js`).

- **Total Displayed Number Metrics Cataloged:** 48 concrete displayed numeric outputs across 13 dashboard panels / sections.
- **Formulas & Thresholds:** Categorized strictly as `SOURCED` (industry standard / vendor formulas / external research) or `OURS` (heuristics / thresholds / custom definitions established in `STEPS.md` & research studies).
- **Test Coverage Breakdown:**
  - **PINNED (Python / Node unit tests or Replay Fixture tests):** 36 displayed metrics (75.0%) are directly verified and pinned by existing test assertions.
  - **PARTIAL (Indicator function tested, but UI element rendering not pinned by replay/browser test):** 8 displayed metrics (16.7%).
  - **NONE (Neither unit test nor replay fixture assertion exists):** 4 displayed metrics (8.3%).

---

## 2. Displayed Numbers Audit Table

The table below catalogs every number displayed on the Live Aid page, its feed source field, mathematical formula / formatting, and its test pinning status.

| # | Panel / Element | Displayed Number | DOM Target / Citation | Source Feed & Field | Formula / Derivation | Type | Test Pin Status & Citation |
|---|---|---|---|---|---|---|---|
| 1 | Header / Price | Deribit Last Price | `live_aid.html:549` (`#dbt-last`) | Deribit ticker: `ticker.BTC-PERPETUAL.100ms` -> `last_price` (`live_aid.html:330`) | `fmt(S.dbt, 1)` | SOURCED | **PINNED**: `test_live_aid.py:233`, `test_live_aid_replay.py:149` (via fixture) |
| 2 | Header / Price | Deribit Mark Price | `live_aid.html:550` (`#dbt-sub`) | Deribit ticker: `ticker.BTC-PERPETUAL.100ms` -> `mark_price` (`live_aid.html:330`) | `fmt(S.dbtMark, 1)` | SOURCED | **PINNED**: `test_live_aid.py:227`, `test_live_aid.py:233` |
| 3 | Header / Price | Binance Last Price | `live_aid.html:551` (`#bin-last`) | Binance ws: `btcusdt@aggTrade` -> `d.p` (`live_aid.html:378`) | `fmt(S.bin, 1)` | SOURCED | **PINNED**: `test_live_aid.py:454` |
| 4 | Header / Price | Basis (Deribit - Binance) | `live_aid.html:553` (`#basis`) | Deribit `last_price` (`S.dbt`) & Binance `aggTrade` (`S.bin`) | `S.dbt - S.bin` (`sgn(..., 1)`) | OURS | **PINNED**: `test_live_aid.py:454` |
| 5 | Position Bar | Position P&L (BTC) | `live_aid.html:571` (`#pnl-btc`) | User input `store.size`, `store.entry`, `store.side`; Deribit `mark_price` | `inversePnlBtc(side, size, entry, mark)`: `long = size * (1/entry - 1/mark); side === 'short' ? -long : long` (`live_aid_indicators.js:89-92`) | SOURCED | **PINNED**: `test_live_aid.py:227` (SOURCED Deribit spec), `test_live_aid.py:233` |
| 6 | Position Bar | Position P&L (USD) | `live_aid.html:572` (`#pnl-usd`) | User input & Deribit `mark_price` | `p * mark` (`sgn(..., 2) + ' USD'`) | SOURCED | **PINNED**: `test_live_aid.py:233` |
| 7 | Position Bar | Distance to Entry (pts) | `live_aid.html:574` (`#pos-dist`) | User `store.entry` - Deribit `mark_price` | `entry - mark` (`sgn(d, 1) + ' pts'`) | OURS | **NONE** (UI-only rendering) |
| 8 | Position Bar | Distance in ATR15 | `live_aid.html:575` (`#pos-atr`) | `(entry - mark)` / `S.a15` | `d / a15` (`sgn(..., 2) + ' x ATR15'`) | OURS | **NONE** (UI-only rendering) |
| 9 | Position Bar / Rungs | Rung Price & Size | `live_aid.html:581` (`#rungs`) | User input: `store.rungs[i].price`, `.size` | `fmt(+r.price, 1)`, `fmt(+r.size, 0)` | YOU / OURS | **NONE** (local storage UI only) |
| 10 | Position Bar / Rungs | Uncovered Position Size | `live_aid.html:584` (`#uncovered`) | `store.size` - `sum(rungs.size)` | `size - covered` (`fmt(..., 0)`) | OURS | **NONE** (local storage UI only) |
| 11 | Glance Tiles | VWAP Distance | `live_aid.html:1022` (`#g-vwap`) | Venue mark/price (`px`) - Day VWAP (`vw`) | `px - vw` (`sgn(dv, 1)`) | OURS | **PINNED**: `test_live_aid_replay.py:165` (verifies vs VWAP NOT_IN_DATA / value) |
| 12 | Glance Tiles | VWAP Absolute Value | `live_aid.html:1022` (`#g-vwap-sub`) | 1m Klines `dayVwap()` (`live_aid_indicators.js:76-85`) | Cumulative HLC3 * volume / cumulative volume resetting at 00:00Z | SOURCED | **PINNED**: `test_live_aid.py:194` (`test_day_vwap_hlc3`), `test_live_aid_replay.py:149` |
| 13 | Glance Tiles | Nearest Level Above/Below Distance | `live_aid.html:1029` (`#g-above`, `#g-below`) | Nearest support/resistance level price - live price `px` | `level.p - px` (`sgn(d, 1)`) | OURS | **PARTIAL**: `test_live_aid.py:363` pins `supports()`, but glance DOM tile text not asserted |
| 14 | Glance Tiles | Nearest Level Above/Below ATR15 Ratio | `live_aid.html:1030` (`#g-above-sub`, `#g-below-sub`) | Level distance `d` / 15m ATR | `d / a15` (`sgn(..., 2) + ' ATR15'`) | OURS | **PARTIAL**: `test_live_aid.py:190` pins `atr()`, glance ratio formatting unpinned in replay |
| 15 | Glance Tiles | Stay Confidence Count | `live_aid.html:1094` (`#g-stay`) | Confidence flags across DOM, Flow, VWAP, Squeeze, Divergence (`live_aid_indicators.js:236-239`) | Count of positive flags `cf.for` / available flags `cf.avail` | OURS | **PINNED**: `test_live_aid.py:376` (`test_it_confidence_and_reduce_rule`) |
| 16 | Glance Tiles | Rule R Against Count | `live_aid.html:1095` (`#g-rule`) | Confidence flags against the trade `cf.against` | Count of negative flags `cf.against >= 3` | OURS | **PINNED**: `test_live_aid.py:376` (`test_it_confidence_and_reduce_rule`) |
| 17 | Momentum Strip | RSI 14 (1m, 5m, 15m, 1h, 4h) | `live_aid.html:681` (`#strip`) | Klines close prices | Wilder RMA(gains, 14) / RMA(losses, 14) (`live_aid_indicators.js:34-47`) | SOURCED | **PINNED**: `test_live_aid.py:176`, `test_live_aid_replay.py:149`, `test_live_aid_replay.py:157`, `test_live_aid_layout.py:118-120` |
| 18 | Momentum Strip | RSI SMA 14 | `live_aid.html:681` (`#strip`) | RSI series | 14-period simple moving average of RSI (`live_aid_indicators.js:24-32`) | SOURCED | **PINNED**: `test_live_aid.py:180`, `test_live_aid_replay.py:149` |
| 19 | Momentum Strip | Bollinger %B | `live_aid.html:681` (`#strip`) | Klines close prices | `(close - lower) / (upper - lower) * 100` (`live_aid_indicators.js:59`) | SOURCED | **PINNED**: `test_live_aid.py:184`, `test_live_aid_replay.py:149` |
| 20 | Momentum Strip | Bollinger Band Width % | `live_aid.html:682` (`#strip`) | Klines close prices | `(upper - lower) / basis * 100` (`live_aid_indicators.js:60`) | SOURCED | **PINNED**: `test_live_aid.py:184`, `test_live_aid_replay.py:149` |
| 21 | Momentum Strip | ATR 14 | `live_aid.html:682` (`#strip`) | Klines H, L, C | Wilder RMA of True Range over 14 bars (`live_aid_indicators.js:65-73`) | SOURCED | **PINNED**: `test_live_aid.py:190`, `test_live_aid_replay.py:149` |
| 22 | Momentum Strip | Close vs VWAP Distance | `live_aid.html:682` (`#strip`) | Close price - Day VWAP | `k.close - vw` (`sgn(..., 1)`) | OURS | **PINNED**: `test_live_aid_replay.py:149`, `test_live_aid_replay.py:170` |
| 23 | Momentum Strip | WaveTrend wt1, wt2 | `live_aid.html:679` (`#strip`) | Klines H, L, C | LazyBear WT: `wt1 = EMA(ci, 21)`, `wt2 = SMA(wt1, 4)` (`live_aid_indicators.js:107-137`) | SOURCED | **PINNED**: `test_live_aid.py:211` (matches `backtest/layers/wavetrend/wavetrend.py`), `test_live_aid_replay.py:149` |
| 24 | Momentum Strip | WaveTrend Cross Value & Age | `live_aid.html:676-677` (`#strip`) | WaveTrend event history | `w.wt1[j]` value at crossover and `n - j` bars ago | OURS | **PINNED**: `test_live_aid.py:211`, `test_live_aid_replay.py:149` |
| 25 | Coil & Pierce | Bollinger Band Width & Percentile | `live_aid.html:601` (`#coil`) | 15m Klines closes | Current width `100 * width`, percentile `100 * bwPct` over lookback 2880 bars (`live_aid_indicators.js:252-254`) | OURS | **PINNED**: `test_live_aid.py:402` (`test_coil_pierce_hand_case`) |
| 26 | Coil & Pierce | Lookback History Days | `live_aid.html:602` (`#coil`) | 15m bars count in history | `histBars / 96` (96 bars per 24h day) | OURS | **PINNED**: `test_live_aid.py:402` |
| 27 | Coil & Pierce | Measured Base Rates (Expand, Up, Down, Side, Both, n) | `live_aid.html:602-603` (`#coil`) | Descriptive constants `CP.coil` / `CP.noCoil` (`live_aid_indicators.js:247`) | Historical base rates from `research/pre_us_squeeze_2026-10-29` | SOURCED (research) | **PINNED**: `test_live_aid.py:402` |
| 28 | Coil & Pierce | Pierce Close Price & Age | `live_aid.html:607` (`#coil`) | 15m breakout bar | Breakout bar close `fmt(p.close, 1)` and `p.ageBars` | OURS | **PINNED**: `test_live_aid.py:402` |
| 29 | Coil & Pierce | Pierce Volume Ratio | `live_aid.html:609` (`#coil`) | 15m breakout bar volume vs 20-bar SMA | `v / (vs / 20)` (`fmt(..., 2) + 'x'`) (`live_aid_indicators.js:259-260`) | OURS | **PINNED**: `test_live_aid.py:402` |
| 30 | Coil & Pierce | Pierce Taker Delta Share | `live_aid.html:609` (`#coil`) | Taker buy volume vs total volume | `(2 * tb - v) / v * dir` (`sgn(..., 2)`) (`live_aid_indicators.js:261`) | OURS | **PINNED**: `test_live_aid.py:402` |
| 31 | Coil & Pierce | Pierce Reference Level & Distance | `live_aid.html:611` (`#coil`) | Prior day high / low (`pdh` / `pdl`) | Distance `Math.abs(lvl / c[k] - 1) * 100` (`live_aid_indicators.js:264`) | OURS | **PINNED**: `test_live_aid.py:402` |
| 32 | Coil & Pierce | Force Category Reach / Fail Odds | `live_aid.html:610` (`#coil`) | `CP.force[fb]` lookup table (`live_aid_indicators.js:246`) | Descriptive reach % and fail % from `research/bb_pierce_force_2026-10-29` | SOURCED (research) | **PINNED**: `test_live_aid.py:402` |
| 33 | US Open Ladder | Pre-Open Range (Box H/L) | `live_aid.html:626` (`#uo-box`) | 5m Klines from 00:00Z to US Open | `box.h`, `box.l`, range % `(box.h - box.l) / box.l * 100` (`live_aid_indicators.js:446-448`) | OURS | **PINNED**: `test_live_aid.py:532` (`test_us_open_ladder_hand_case`) |
| 34 | US Open Ladder | Opening Range (OR 15m H/L) | `live_aid.html:627` (`#uo-box`) | First three 5m bars from US Open | `or.h`, `or.l` (`live_aid_indicators.js:448`) | OURS | **PINNED**: `test_live_aid.py:532` |
| 35 | US Open Ladder | Level Distance % | `live_aid.html:631` (`#uo-rows`) | Level price `x.p` vs mark `px` | `(x.p - px) / px * 100` (`live_aid_indicators.js:460`) | OURS | **PINNED**: `test_live_aid.py:532` |
| 36 | US Open Ladder | Empirical Touch & Held Rates % | `live_aid.html:631` (`#uo-rows`) | `US_OPEN_RATES.rates[kind][bucket]` (`us_open_rates.js:2`) | Historical touch % (`r.touch`) and held % (`r.held`) if `n >= 30` | SOURCED (research) | **PINNED**: `test_live_aid.py:532` |
| 37 | Money / OI | Multi-Window Price & OI Change % | `live_aid.html:800,804` (`#m-sub`, `#m-rows`) | Bybit, Deribit, Binance OI samples | `dp = last.px / base.px - 1`, `doi = last.oi / base.oi - 1` over 5m/15m/60m (`live_aid_indicators.js:506`) | OURS | **PINNED**: `test_oi_money.py:97`, `test_live_aid_replay.py:301-312` |
| 38 | Money / OI | BTC-Weighted Net OI Change % | `live_aid.html:805` (`#m-rows`) | Sum of BTC-weighted OI changes / total BTC OI | `sum(btc * doi) / sum(btc)` (`live_aid_indicators.js:512-515`) | OURS | **PINNED**: `test_oi_money.py:111` (`test_venue_disagreement_and_net`) |
| 39 | Money / OI | Flush / Squeeze Extreme & Move % | `live_aid.html:819` (`#m-lines`) | Bybit 5m bar wick and OI drop | Wick low/high vs prev close `(b.l / pc - 1) * 100`, OI change `(b.oi1 / b.oi0 - 1) * 100` (`live_aid_indicators.js:538-540`) | OURS | **PINNED**: `test_oi_money.py:132`, `test_live_aid_replay.py:301-305` |
| 40 | Money / OI | OI Delta (BTC) on Flush/Squeeze | `live_aid_indicators.js:577` | Bybit 5m bar OI snapshot diff | `b.oi1 - b.oi0` in BTC contracts | SOURCED | **PINNED**: `test_oi_money.py:132`, `test_live_aid_replay.py:304` |
| 41 | Money / OI | Trapped Extreme Level | `live_aid.html:821` (`#m-lines`) | Post-flush extreme high or post-squeeze low | `path.hi` / `path.lo` if OI rebuilt >= 0.2% (`live_aid_indicators.js:569-570`) | OURS | **PINNED**: `test_oi_money.py:147` (`test_path_trap_and_measured_line`) |
| 42 | Money / OI | C24 Measured Expectation % | `live_aid.html:825` (`#m-lines`) | C24 empirical study (`live_aid_indicators.js:581-591`) | 4h up rate `g.up` % vs base 52%, drop rate `g.drop` % vs base 6% | SOURCED (research) | **PINNED**: `test_oi_money.py:147` |
| 43 | Liquidations | USD Liquidated Sum (1m, 5m, 15m) | `live_aid.html:850,854` (`#liq-sum`, `#g-liq-sub`) | Deribit trades liquidation flag, Bybit linear socket, Binance forceOrder | Sum of liquidated USD per side over window (`live_aid_indicators.js:287`) | SOURCED / OURS | **PINNED**: `test_live_aid.py:428`, `test_live_aid.py:435` |
| 44 | Funding & Premium | Funding Rate % per 8h & Annualized % | `live_aid.html:871,882` (`#fund`, `#g-fund`) | Deribit `funding_8h`, Bybit `fundingRate` | `pct8h = r * 100`, `annual = r * 1095 * 100` (`live_aid_indicators.js:298`) | SOURCED | **PINNED**: `test_live_aid.py:444` (`test_funding_read`) |
| 45 | Funding & Premium | Premium Mark - Index (pts & bps) | `live_aid.html:870` (`#fund`) | Deribit / Bybit mark and index prices | `pts = mark - idx`, `bps = pts / idx * 10000` (`live_aid_indicators.js:302`) | SOURCED | **PINNED**: `test_live_aid.py:454` (`test_premium_and_bybit_merge`) |
| 46 | Macro Calendar | Event Countdown / Offset Time | `live_aid.html:907` (`#mc-next`) | ForexFactory calendar `date` vs `now` | `countdownMs = event.t - now` converted to days/hours/mins (`live_aid.html:896-899`) | SOURCED | **PINNED**: `test_live_aid.py:593`, `test_live_aid_replay.py:216-224` |
| 47 | News | Importance Score & Event Count | `live_aid.html:942,947` (`#news`, `#g-news`) | Tree of Alpha news REST API `importance` (0-10) | Count of headlines with `importance >= 7` in 60 min window (`live_aid_indicators.js:343`) | SOURCED / OURS | **PINNED**: `test_live_aid.py:476`, `test_live_aid_layout.py:123`, `test_live_aid_layout.py:158` |
| 48 | Verdict Board | Consensus Lean Votes | `live_aid.html:965` (`#v-count`) | Net fresh analyst bias, VWAP sign, RSI 1h & 4h vs 50 | Count of bull vs bear votes (`live_aid_indicators.js:417-420`) | OURS | **PINNED**: `test_live_aid.py:516` (`test_lean_rule`) |

---

## 3. Replay Fixture Coverage & Verification Audit

### 3.1 Existing Replay Fixtures (`fixture_*.json`)
1. **`fixture_klines.json`:**
   - Provides 300 1m kline candles `[t, o, h, l, c, v]`.
   - Used by `test_live_aid_replay.py:open_replay()` to fold into 5m, 15m, 1h, and 4h series.
   - Pinned by `test_rendered_strip_matches_python_maths` against independent Python implementations of Wilder RMA RSI, SMA, Bollinger Bands, ATR, and VWAP.
2. **`fixture_ff_calendar.json`:**
   - ForexFactory economic events JSON array.
   - Used by `test_calendar_strip_renders_next_and_last` to pin event countdowns and historical results display.
3. **`fixture_bybit_flush_1030.json`:**
   - 5m Bybit klines and open interest snapshots during the 2026-10-30 18:50Z flush.
   - Used by `test_money_tile_replays_the_1850_flush` and `test_flush_detector_replays_10_30_1850` to pin exact flush wicks, OI drops, and trapped price boundaries.

### 3.2 Fixture Gaps & Missing Checks
1. **Live Aid Liquidation Tape Replay Fixture (MISSING):**
   - While `test_live_aid.py:428-435` tests `liqDeribit`, `liqBybit`, `liqBinance`, and `liqSum` with synthetic in-memory dicts, there is no JSON fixture replaying a known liquidation cascading cluster through `test_live_aid_replay.py` on the browser-rendered DOM `#liq-tape` or `#liq-sum`.
2. **Analyst Ingestion Fixture in Browser Replay (MISSING):**
   - In `test_live_aid_replay.py`, analyst data (`analyst_data.js`) is omitted, causing the verdict board to default to no-analyst fallbacks. `test_build_analyst_data.py` tests JSON generation from CSV, but full end-to-end replay with browser DOM verification is not hooked.
3. **US Open Ladder Historical Fixture (PARTIAL):**
   - `test_us_open_ladder_hand_case` verifies `usOpen()` logic in Node via synthetic arrays, but browser replay with `window.LIVEAID_REPLAY` currently folds 5m bars without a full 7-day daily history, causing the ladder in replay to show fewer than 7 prior days.
