8 CONFIRMED / 1 CONTRADICTED / 3 NOT FETCHED

# Primary-Source Check: VFI Rule Book (`VFI.md`)

Target: `MyTradingSys/research/indicator_rulebooks/VFI.md` (81 lines).
Primary sources fetched:
1. Markos Katsanos official VFI page: `https://mkatsanos.com/volume-flow-vfi-indicator/` (HTTP 200, fetched 2026-11-14).
2. LazyBear TradingView script `VFI_LB`: `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` (HTTP 200, fetched 2026-11-14) and its public comments API `https://www.tradingview.com/api/v1/ideas/MhlDpfdS/comments/?limit=50` (72 top-level comments fetched 2026-11-14).
3. QuantifiedStrategies VFI page: `https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/` (returned HTTP 200 `Bot Verification` / `lsrecaptcha-form` anti-bot gate; not bypassed -> `NOT FETCHED`).

---

## 1. Inventory of Rule Lines in `VFI.md`

| `VFI.md` line | Section / Item | Label in `VFI.md` | Cited Source(s) |
|---|---|---|---|
| `MyTradingSys/research/indicator_rulebooks/VFI.md:8` | What it measures (OBV defects, `cutoff`, `2.5 * SMA(volume, 50)`, `vcoef * SMA(volume, length)[1]`, 130 bars) | unlabeled (prose) | `FORMULAS.md` s32, `USAGE_vfi.md`, `KAT`, `LB` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:16` | Who (Katsanos June 2004 TASC; LazyBear `VFI_LB`, `MhlDpfdS`) | `SOURCED` (section header) | `USG:7-8`, `KAT`, `LB` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:17` | Defaults (`130`, `coef = 0.2`, `vcoef = 2.5`, stdev `30`, signal `5` EMA, smooth false / 3-bar SMA) | `SOURCED` | `USG:58-64`, `LB`, `KAT`, `FORM` s32.1 |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:18` | Intraday `coef = 0.1` | `SOURCED` | `USG:30, 60, 66`, `KAT` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:19` | Stated use: Zero line (`VFI > 0` bull, `VFI < 0` bear, zero cross = intermediate trend shift) | `SOURCED` | `USG:14, 22-23`, `KAT` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:20` | Stated use: Signal line (5-period EMA `vfima` and histogram `vfi - vfima` for entry/exit triggers) | `SOURCED` | `USG:27`, `LB` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:21` | Stated use: Divergence & Sharp `"V"` patterns | `SOURCED` | `USG:15, 23, 41`, `KAT` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:22` | Timeframe (130 trading days ~ 6 calendar months; intraday `coef = 0.1`) | `SOURCED` | `USG:20`, `KAT` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:23` | Warnings (no mechanical stop-loss, position sizing, or profit targets) | `SOURCED` | `USG:22`, `KAT`, `LB` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:28` | Zero-line crossover yields 40-45% win rate, high payoff, high drawdown without stops | `measured` (`[fetched]`, no quote) | `https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:29` | Macro trend filter: long only when `VFI > 0` above 200 SMA improves win rate | `measured` (`[fetched]`, no quote) | `https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:30` | Crypto 24/7 distortion (130d ~ 4.3 months; daily `coef = 0.2` over-filters 15m/1h) | `anecdote` (`OURS` / MTS note) | `USAGE_vfi.md` (`USG:48-50`) |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:31` | Divergence at liquidity sweeps confirms absorption / distribution | `anecdote` | `USAGE_vfi.md` (`USG:53-54`); TradingView community |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:32` | Filtering low-volume churn superior to OBV at S/R | `anecdote` | `USAGE_vfi.md` (`USG:36`); TradingView practitioner consensus |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:33` | Signal line crossover (`VFI` cross 5 EMA) generates early swing entry triggers | `UNVERIFIED` | TradingView script comments (`MhlDpfdS`) |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:50-57` | OUR measurements (`VFI_STATE.md`, `USAGE_vfi.md`, `FORMULAS.md` s32) | `OURS` / `UNTESTED` | `VFI_STATE.md`, `USAGE_vfi.md`, `FORMULAS.md` s32 |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:60-68` | Live Aid integration (`indread.js`, `home.js`, `live_aid.html`) | `OURS` (local code) | `MyTradingSys/tools/live_aid/indread.js:13,79-80,100-107`, `MyTradingSys/tools/live_aid/home.js:113-121,282-297` |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:70-73` | Confluence role: `FLOW` (context only, never an entry trigger) | `OURS` | Internal design rule |
| `MyTradingSys/research/indicator_rulebooks/VFI.md:75-81` | Open tests (4 unfiled studies) | `OURS` (`not filed`) | None |

---

## 2. Local Source File & Quote Verification

1. **Row `vfi` ("Volume flow")**: FOUND.
   - `MyTradingSys/tools/live_aid/indread.js:13` contains `['vfi', 'Volume flow']`.
2. **263-bar warmup & `"needs 263 bars"`**: FOUND.
   - `MyTradingSys/tools/live_aid/indread.js:80` contains `'needs 263 bars'` and `c.length >= 263 ? 'no volume data' : 'needs 263 bars'`.
3. **Live Aid rise confirmation `"15m rise is backed by volume"`**: FOUND.
   - `MyTradingSys/tools/live_aid/indread.js:104` contains `nm + ' rise is backed by volume: flow rising, buyers lead'` (with `nm = a ? '15m' : '1h'` at line 99).
4. **Live Aid warning `"pullback risk"`**: **NOT FOUND** in `indread.js`.
   - `MyTradingSys/research/indicator_rulebooks/VFI.md:65` claims Live Aid warns of `"pullback risk"`.
   - `MyTradingSys/tools/live_aid/indread.js:104-105` actually warns of `fade risk` on an unbacked rise and `bounce risk` on an unbacked fall.
5. **Home Volume card (`"Money flow (VFI):"`)**: FOUND.
   - `MyTradingSys/tools/live_aid/home.js:115,120` contains `'in'`, `'out'`, `'flat'`, `' ▲'`, `' ▼'`, and `Money flow (VFI):`.
6. **Home `"Who is winning"` card (`indCard()`)**: FOUND.
   - `MyTradingSys/tools/live_aid/home.js:285,294` contains `Who is winning` and `6 readings vote per timeframe: money flow, squeeze, trend strength, WaveTrend, RSI, buy vs sell volume. A lead of 2 wins.`.
7. **`SMA(volume, 50)` vs `SMA(volume, 130)[1]`**: FOUND in `USAGE_vfi.md`, superseded in `FORMULAS.md`.
   - `MyTradingSys/research/tv_favorites_2026-11/USAGE_vfi.md:12` contains `"2.5 * SMA(volume, 50)"` and line 13 `"50-bar average volume"`.
   - `MyTradingSys/backtest/layers/FORMULAS.md:716` states `"the SPEC_ENGINES.md B text (50/130 split, EMA 3) was Lead C's recall and is superseded."` Both Katsanos (`mkatsanos.com`) and LazyBear (`VFI_LB`) use `length` (`130`), not `50`.
8. **Sharp `"V"` patterns**: FOUND in `USAGE_vfi.md` (paraphrase), NOT found on `mkatsanos.com`.
   - `MyTradingSys/research/tv_favorites_2026-11/USAGE_vfi.md:15` contains `sharp V-formations in VFI frequently preceding price turning points`.
9. **Other cited local files**: All exist (`MyTradingSys/backtest/layers/vfi/vfi.py`, `MyTradingSys/backtest/layers/vfi/test_vfi.py`, `MyTradingSys/tools/live_aid/live_aid.html`, `MyTradingSys/research/tv_favorites_2026-11/VFI_STATE.md`).

---

## 3. Primary Source Verification Table (`UNVERIFIED` and Quote-Lacking Rule Lines)

| Claim (`VFI.md` line) | Primary Source | Verbatim Quote or `NOT FETCHED` | Verdict |
|---|---|---|---|
| Who: Katsanos June 2004 TASC; LazyBear `VFI_LB` (line 16) | `https://mkatsanos.com/volume-flow-vfi-indicator/` & `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` | "This indicator was first introduced in my June 2004 article in Technical Analysis of STOCKS & COMMODITIES." / `study(title = "Volume Flow Indicator [LazyBear]", shorttitle="VFI_LB")` | CONFIRMED |
| Defaults: 130, 0.2, 2.5, stdev 30, signal 5 EMA, smooth false / 3-bar SMA (line 17) | `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` | `length = input(130, title="VFI length")` `coef = input(0.2)` `vcoef = input(2.5, title="Max. vol. cutoff")` `signalLength=input(5)` `smoothVFI=input(false, type=bool)` `vinter = stdev(inter, 30 )` `vfi = ma(sum( vcp , length )/vave, 3)` | CONFIRMED |
| Intraday `coef = 0.1` (line 18) | `https://mkatsanos.com/volume-flow-vfi-indicator/` & `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` | "Coef=coefficient for minimal price cut-of (use 0.2 for daily and 0.1 for intraday 5-15 min data)" / "Markos suggests using 0.2 coeff for day trading and 0.1 for intra-day." | CONFIRMED |
| Zero line: `> 0` bullish, `< 0` bearish, cross = trend shift (line 19) | `https://mkatsanos.com/volume-flow-vfi-indicator/` | "Positive readings are bullish and negative bearish." / "A simplified interpretation of the VFI is that values above zero indicate a bullish state and the crossing of the zero line is the trigger or buy signal." | CONFIRMED |
| Signal line: 5-period EMA `vfima` and histogram `vfi - vfima` (line 20; note description does not state "for entry/exit triggers") | `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` | `vfima=ema( vfi, signalLength )` `d=vfi-vfima` / "I have exposed options to plot a signal EMA. All parameters are configurable." | CONFIRMED |
| Divergences between VFI and price are the primary signal (line 21) | `https://mkatsanos.com/volume-flow-vfi-indicator/` | "The strongest signal with all money flow indicators is of course divergence. The classic form of divergence is when the indicator refuses to follow the price action and makes lower highs while price makes higher highs (negative divergence)." | CONFIRMED |
| Sharp `"V"` patterns in VFI frequently precede price turns (line 21) | June 2004 *Technical Analysis of STOCKS & COMMODITIES* (paywalled; absent from `mkatsanos.com/volume-flow-vfi-indicator/`) | NOT FETCHED (not present on `mkatsanos.com/volume-flow-vfi-indicator/`; TASC June 2004 full article requires paid access) | NOT FETCHED |
| Timeframe: 130 daily bars = 6 months (line 22) | `https://mkatsanos.com/volume-flow-vfi-indicator/` | "The indicator takes into account only the latest 6 month volume action and not the entire data loaded in the chart." / "Period=days for VFI calculation. Default values are 130 for daily and 26 for weekly charts." | CONFIRMED |
| Warnings: no mechanical stop-loss, position sizing, or profit targets (line 23) | `https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/` | "A simplified interpretation of the VFI is: * Values above zero indicate a bullish state and the crossing of the zero line is the trigger or buy signal. * The strongest signal with all money flow indicators is of course divergence." (no stop-loss, sizing, or profit target rules appear on the page) | CONFIRMED |
| Zero-line crossover strategy: 40-45% win rate, high payoff, high drawdown without stops (line 28) | `https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/` | NOT FETCHED (returned HTTP 200 `Bot Verification` / `lsrecaptcha-form` anti-bot gate) | NOT FETCHED |
| Macro trend filter: long only when `VFI > 0` above 200 SMA improves win rate (line 29) | `https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/` | NOT FETCHED (returned HTTP 200 `Bot Verification` / `lsrecaptcha-form` anti-bot gate) | NOT FETCHED |
| Signal line crossover (`VFI` cross 5 EMA) generates early swing entry triggers (line 33, `UNVERIFIED`) | `https://www.tradingview.com/api/v1/ideas/MhlDpfdS/comments/?limit=50` (72 comments fetched) | "I am just curious, why I am not able to see the grey histogram. I can only see the green and orange lines crossing each other." (comment 3690628) / "Is it effective if I change the setting to '50' for swing and '30' for scalping?" (comment 13698886) — zero of 72 fetched comments claim VFI crossing 5 EMA generates early swing entry triggers | CONTRADICTED |
