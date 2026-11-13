# Rule book: Cumulative Volume Delta (CVD) / Taker Delta

Sources: FORM = `backtest/layers/FORMULAS.md` s14; BT = `backtest/bt/bt_data.py`:182-185; OFV = `research/orderflow_views_2026-10-14/RESULT.md`; FAB = `research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`; TOM_Y67 = `extracts/fresh/extract_y67l86cSqb8_fresh.md`; TOM_5LJ = `extracts/v2/tom/5Ljfwvtktek_v2.md`; LA_HTML = `tools/live_aid/live_aid.html`:137-142, 290-294; LA_REQ = `tools/live_aid/REQUIREMENTS.md`:27; LA_STEPS = `tools/live_aid/STEPS.md`:110; SC = https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375 (Sierra Chart "Cumulative Delta Bars - Volume", fetched 2026-11-13; SOURCED); CG = https://www.coinglass.com/learn/cvd-cumulative-volume-delta-explained (CoinGlass "CVD (Cumulative Volume Delta) Explained Guide", fetched 2026-11-13; SOURCED); TV = https://www.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/ (TradingView Support "Cumulative Volume Delta", fetched 2026-11-13; SOURCED); HARN = https://emojitrading.com/order-flow/ (Trevor Harnett / MarketDelta 2003 history, fetched 2026-11-13; SOURCED). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: CVD measures accumulated net aggressive market order pressure (taker buy minus taker sell volume). Our backtest data on BTC shows price-vs-CVD divergence on 1m and 5m has 0 of 12 arms passing (no fee-net predictive edge). It serves as an order flow pressure gauge and context filter, never a standalone entry signal.**

## 1. What it measures
CVD measures the running cumulative sum of net aggressive market order volume (taker buy volume minus taker sell volume) over an anchor window or session. Aggressive buyers lift the ask (positive delta), while aggressive sellers hit the bid (negative delta).
- Formula: `delta = 2 * taker_buy_volume - volume` (`backtest/bt/bt_data.py`:184; `backtest/layers/FORMULAS.md` s14).
- Divergence formula: `backtest/layers/FORMULAS.md` s14 (bearish if price makes higher high while CVD makes lower high; bullish if price makes lower low while CVD makes higher low).
- Parity / Verification: `NOT VERIFIED-TV` (calculated directly from exchange tick/kline trade feeds; TV estimates intrabar delta from price action rather than exchange tick logs; Sierra Chart / Binance / Deribit use raw trade taker flags).
- Code modules: `backtest/bt/bt_data.py` (`cvd_delta`), `backtest/layers/positioning/funding_cvd_fade.py`, `backtest/layers/fabio/fabio_cvd_absorption.py`, `tools/live_aid/tf_strip.js`, `tools/live_aid/flow_collector.py`.

## 2. Developer's own rules (SOURCED)
CVD / Cumulative Delta is an order-flow market microstructure concept that originated with the transition to electronic order books:
- **Developer / Originator:** Trevor Harnett, founder of MarketDelta (founded in 2003), pioneered the Footprint® chart and popularized "Cumulative Delta" running totals of net aggressive volume (Ask Volume minus Bid Volume) across trading sessions (HARN, SC).
- **Sierra Chart Documentation (SC):**
  - **Inputs / Settings:** Study "Cumulative Delta Bars - Volume" (SC). Inputs include "Reset at Start of Trading Day" (Yes/No) and "Perform Rolling Calculation / Length" (SC).
  - **Mechanics:** Calculates `AskVolume - BidVolume` per bar and accumulates across the day or session (SC). Plots Open, High, Low, Close delta candlestick bars (SC).
  - **Rules stated:** The technical reference documentation describes the exact data structure and accumulation reset math; "the page states no rule" for standalone entry, stop, or exit signals (SC).
- **TradingView Documentation (TV):**
  - **Mechanics:** Analyzes intrabar volume and categorizes volume into buying and selling pressure, accumulating results across bars until a reset period (TV).
  - **Rules stated:** Used to assess whether aggressive buyers or aggressive sellers are driving the market and spot divergence; "the page states no rule" for specific mechanical entry/exit levels or win rates (TV).

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| CVD divergence indicates reversal: price higher high with CVD lower high signals buyer exhaustion / absorption (bearish); price lower low with CVD higher low signals seller absorption (bullish) | https://www.coinglass.com/learn/cvd-cumulative-volume-delta-explained (SOURCED) | anecdote (conceptual explanation, no costed sample or statistical significance stated) |
| Spot vs Futures CVD divergence: when futures CVD rises while spot CVD is flat or falling, the move is leverage-driven and prone to long squeezes; spot CVD leading confirms organic accumulation | https://www.coinglass.com/learn/cvd-cumulative-volume-delta-explained (SOURCED) | anecdote (market commentary, no backtest ledger or fee-net sample) |
| CVD candles (Open, High, Low, Close of accumulated delta) show intra-bar aggressive pressure shifts and delta rejection wicks | https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375 (SOURCED) | anecdote (platform visualization feature, no mechanical edge demonstrated) |
| Intrabar lower-timeframe estimation of CVD can approximate order flow where exchange trade aggressor flags are missing | https://www.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/ (SOURCED) | anecdote (vendor approximation, unverified accuracy against tick-level data) |
| CVD divergence alone has edge on crypto scalping (1m/5m) | Crypto Twitter / YouTube orderflow claims (UNVERIFIED) | none (refuted by our data; zero measured fee-net edge) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Tom | Cumulative delta measures buying surplus minus selling surplus across the day; must know market-specific key figures (e.g. 500 contracts in oil vs Euro stocks); delta must never be used alone, only at strong technical levels to identify exhaustion or absorption; rising cumulative delta confirms footprint long setup | `extracts/fresh/extract_y67l86cSqb8_fresh.md`:32-39, 74-85, 103-120, 140-145; `extracts/v2/tom/5Ljfwvtktek_v2.md`:53 (`5Ljfwvtktek_raw.txt` [26905]) |
| Fabio | CVD is a pressure gauge ("volume is leading the price"); in a range, CVD breaking out first shows loading (accumulation/distribution); absorption occurs when CVD makes a lower low while price holds level (passive buyers absorb aggressors); CVD sell candle printing green shows absorption; falling CVD flipping lower acts as a veto against counter-trend longs; never enter on CVD alone | `MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`:14-36; `extracts/processed/fabio_valentini/0jM5Y31YJak/extract_0jM5Y31YJak.md`:1-6; `extracts/v2/fabio/FawPrRUGNpk_v2.md`:74-90; `extracts/v2/fabio/Is1HvdfQm5c_v2.md`:72-77, L675-L681; `extracts/v2/fabio/o-w5Gxss6T0_v2.md`:R3 |
| Andrea Cimi | CVD divergence on 5m/1m charts (negative delta with positive price action) marks divergence in market pressure; enter on the 5-minute candle close confirming it | `MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`:37-41 (`9IliXww64uM`) |
| Krown | Market orders lift/hit resting orders and are the only orders that move price; supports measuring taker flow (CVD / aggTrades); order book resting orders are advertisement; volume on intraday is order flow (CVD, big trades) | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md`:KR-OBK03 (`ftK2BqggabQ` t=00:17:52-00:18:49); `KROWN_SETUP_CATALOG.md`:KR-S4/FAB-1 |
| FlowHorse | Market profile identifies zones; order flow (delta, absorption, CVD) determines whether to act at those zones | `extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md`:Context |
| Malkan | Does not use CVD or taker delta on any timeframe (focuses on price action, moving averages, trendlines, session timing) | `extracts/processed/malkan/extract_Wvq1TZh8aF0.md`:none |
| CCU | Does not use CVD or taker delta (uses 50/200 MA, Stoch RSI, WaveTrend on high timeframes like 2d/12d) | `research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md`:41-42 |
| NK StockTalk | No extract mentions CVD or taker delta (uses Hilega Milega / RSI EMA system on cash equities) | `MyTradingSys/research/nk_stocktalk_1113/` (none found) |
| Habib / CBP | No extract mentions CVD or taker delta (uses structural imbalance, session levels, FVG) | `extracts/processed/` (none found) |
| CryptoCred | No extract mentions CVD or taker delta (uses support/resistance, market structure, trigger candles) | `extracts/processed/cryptocred/` (none found) |

## 5. OUR measurements
All rows OURS, copied from the named file. BTCUSDT. CVD here is Binance kline taker-buy delta, not aggregated all-exchange CVD (that is NOT_MEASURED).
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/orderflow_views_2026-10-14/RESULT.md` (DEV-only rerun note 2026-10-17) | Price lower low with CVD not lower low (and mirror), 60 min after entry, DIV minus CONTROL, DEV before 2024-07-01 | 1m long 4933, 1m short 5434, 5m long 1411, 5m short 1858 (full-period n, original run) | DIV minus CONTROL, DEV rerun (Welch t): 1m long -0.023 (-1.4), 1m short +0.016 (1.1), 5m long +0.017 (0.5), 5m short -0.022 (-0.9). Pass mark (>= 0.05, t >= 2) met by 0 of 4; 0 of 12 arms incl. OI split | 1m, 5m: DO NOT USE (file verdict NEGATIVE). Original table is flagged CONTAMINATED (DEV read 2024-07..12); use the rerun row |
| `backtest/layers/fabio/FABIO_L1_REPORT.md` | CVD absorption, frozen IS-best params applied to OOS (last 30%), fee 0.10% round trip, h=5 | OOS 5m 1639, 15m 982, 1h 109 | OOS h5 net: 5m -0.100%, 15m -0.099%, 1h -0.142%; PBO 0.683 / 0.330 / 0.333 | 5m, 15m, 1h: DO NOT USE (file verdict "no edge") |
| `research/setup_alpha_beta_v2_2026-10/RESULT.md` | Beta S1: 15m PDH/PDL sweep + session + kline-CVD absorption, 1.5R / 90 min bracket, taker fees | DEV 50; VAL 23 | mean R net DEV -0.583 (SE 0.230, t -2.54); VAL -0.697 (SE 0.217, t -3.21); plain-sweep S0 DEV -0.47 R | 15m: DO NOT USE for the primary arm (file verdict INCONCLUSIVE at pre-reg power; CVD adds nothing over plain sweep) |
| `research/wlow_bounce_bbrsi60_2026-10-16/RESULT.md` | Weekly-low bounce, CVD change break to trigger, split by sign and median, 1h long h=4 | up 7 / down 1; high 4 / low 4 | net long: up -0.437%, down -0.405%, high -0.542%, low -0.325% (sign/median tests marked NOT_EVALUATED in the file) | 1h: UNDERPOWERED |
| `research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md` | CVD / OBV 20-bar price divergence, 4h and 1d, taker-delta z >= 2 spike | NOT_MEASURED here (file gives "no pass" without n in the row quoted) | no pass on either timeframe | 4h, 1d: DO NOT USE |
Regime mix and DEV / VALIDATION / RECENT split: only setup_alpha_beta_v2 has DEV and VAL; Fabio L1 uses a 70/30 chronological IS/OOS and states "no regime split". Aggregated CVD, divergence at a level (VAL, band): NOT_MEASURED (listed untested in orderflow_views RESULT.md).

## 6. How to read it now on Live Aid
CVD is displayed across two primary panels in Live Aid (`tools/live_aid/live_aid.html`):
1. **Timeframe strip (`tools/live_aid/live_aid.html`:137-142):**
   - Column `CVD`: Shows the taker buy minus sell volume of the forming bar (kline field 9 from `data-api.binance.vision`: `2 * taker_buy - volume`) across 12 rows (1m through 1w).
   - Displayed as a directional indicator / colored arrow (green buy / red sell), refreshing every 15 s (1m-15m) or 60 s (higher frames).
2. **Forced moves & Taker flow (`tools/live_aid/live_aid.html`:290-294, 1275-1277, 1629-1633):**
   - Panel displays spot CVD vs perp CVD (via `flow_collector.py`).
   - Bullet `Taker flow (CVD vs 60 s delta)`: Compares 15-minute CVD against 60 s delta on Deribit trades to identify agreement or disagreement between taker pressure and price drift.
   - Tagged explicitly as: *"Context, never a signal; no size, no orders."*

## 7. Confluence role: FLOW
CVD serves strictly as **FLOW** context:
- What it may add confidence to: It may add confidence to a breakout setup when CVD leads price into an auction boundary, confirm an absorption setup at an established key support/resistance level, or act as a **veto** (e.g. Fabio's rule: do not take a counter-trend long while CVD is flipping lower and sellers dominate).
- Rule in one line: Read effort (CVD) against result (price) only at existing structural levels; never trade CVD divergence or delta crosses as an entry by itself.
- Current status: CONTEXT ONLY (no fee-net out-of-sample edge exists for raw CVD divergence).

## 8. Open tests
| Test | Status | Fixed rule before run |
|---|---|---|
| CVD divergence at key structural levels (POC / VAH / VAL / prior day high/low) rather than anywhere on chart | not filed | Price sweeps level, CVD fails to confirm with lower low / higher high; 15m/1h horizon, fee-net 10 bps |
| Aggregated multi-exchange CVD (CoinGlass model: Binance + Bybit + OKX) vs single-exchange CVD | not filed | Compare signal reliability of aggregated taker delta vs Binance spot/perp taker delta |
| Spot CVD vs Perp CVD divergence leading indicator test | not filed | Perp CVD rising + Spot CVD flat/falling at resistance -> fade long breakout |
| Fabio CVD absorption detector (`fabio_cvd_absorption.py`) on 1h/4h with volume FVG confluence | not filed | CVD new extreme with price holding level inside higher timeframe trend gate |
