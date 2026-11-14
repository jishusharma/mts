5 CONFIRMED / 3 CONTRADICTED / 6 NOT FETCHED

# Primary-Source Verification: SQUEEZE Rule Book (`MyTradingSys/research/indicator_rulebooks/SQUEEZE.md`)

Checked against `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:1-85` (read in full, no edits made to the rule book).

---

## 1. Inventory of Every Rule Line in `SQUEEZE.md`

| Rule Book Line | Section | Rule / Claim Summary | Label in `SQUEEZE.md` | Cited Source(s) |
|---|---|---|---|---|
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:5` | Header Result | Volatility compression/expansion gauge; BTC pure breakout releases 29% UP vs 29% DOWN, 23% dual-side whipsaw; use strictly as TIMING/filter | OURS (derived from `PRE_US`) | `PRE_US` (`MyTradingSys/research/pre_us_squeeze_2026-10-29/RESULT.md`) |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:9` | Sec 1 | BB (20, 2.0 or 1.5 sd) inside KC (20, 1.5 ATR/TR) = squeeze ON; outside = release | SOURCED | `FORM s31`, `LB_TV`, `CARTER` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:10` | Sec 1 | 20-period linear regression of price minus average of Donchian midpoint and SMA | SOURCED | `FORM s31`, `LB_TV` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:11` | Sec 1 | Formula pointer: `31.1 Definitions`, `31.2 Worked toy` | OURS / SOURCED | `MyTradingSys/backtest/layers/FORMULAS.md` s31 |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:12` | Sec 1 | TradingView parity `VERIFIED-TV 2026-11-07`: momentum 3/3 bars, dots 4/4 bars, quirk `1.5*sd` | OURS (verification) / SOURCED (quirk) | `FORM s31` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:13` | Sec 1 | Code module: `squeeze.py`, `indread.js` | OURS | `MyTradingSys/backtest/layers/squeeze/squeeze.py`, `MyTradingSys/tools/live_aid/indread.js` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:18` | Sec 2 | Original Developer: John F. Carter, *Mastering the Trade* (2005/2012, Ch. 11) | SOURCED | `CARTER:245-248` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:19` | Sec 2 | Pine Script Author: LazyBear, `SQZMOM_LB` (2014) | SOURCED | `LB_TV`, `FORM s31` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:20` | Sec 2 | Core Premise: periods of low volatility followed by high volatility and vice versa | SOURCED | `CARTER:246`, `USAGE:25`, `LB_TV` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:21` | Sec 2 | Inputs & Defaults: BB 20/2.0 (quirk uses `multKC` 1.5), KC 20/1.5 TR, linreg 20 | SOURCED | `LB_TV`, `FORM s31:11-18`, `USAGE:58-66` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:22` | Sec 2 | Setup Requirement: >= 6 consecutive squeeze dots | SOURCED | `CARTER:250-252`, `USAGE:11` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:23` | Sec 2 | Trigger ("Squeeze Fires"): first bar BB expands outside KC (black/red to gray/green) | SOURCED | `CARTER:248`, `LB_TV`, `USAGE:12` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:24` | Sec 2 | Directional Rule: breakout trade in momentum histogram direction (>0 long, <0 short) | SOURCED | `CARTER:249`, `USAGE:13`, `LB_TV` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:25` | Sec 2 | Timeframe: intraday (5m, 15m, 60m), daily swing, weekly; MTF alignment | SOURCED | `CARTER:255-258`, `USAGE:28` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:26` | Sec 2 | Exit Rule: two consecutive bars of declining momentum / color shift | SOURCED | `CARTER:253`, `USAGE:15` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:27` | Sec 2 | Warning / Caveats: never anticipate before fire; false breakouts into major S/R | SOURCED | `CARTER:261`, `USAGE:36` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:32` | Sec 3 | Firing into major S/R fails; filter with HTF trend (e.g. 200 EMA) | SOURCED | `https://enlightenedstocktrading.com/squeeze-momentum-indicator/` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:33` | Sec 3 | Mechanical breakout entries without HTF filter yield 35% to 50% win rate | SOURCED | `https://trendspider.com/learning-center/ttm-squeeze-explained/` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:34` | Sec 3 | Multi-timeframe squeeze nesting produces highest probability explosive breakouts | SOURCED | `https://trendspider.com/learning-center/ttm-squeeze-explained/` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:35` | Sec 3 | Squeeze ON identifies low-volatility balance where OI builds before liquidation cascade | SOURCED | `MyTradingSys/research/tv_favorites_2026-11/USAGE_squeeze.md:38-42` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:36` | Sec 3 | Standalone fee-net profitable edge for crypto scalping on 1m/5m | UNVERIFIED | Crypto YouTube / trading forum claims |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:41` | Sec 4 | Krown: compression = low vol regime; low vol precedes high vol; prefers BBWP; OI + funding | SOURCED (analyst extract) | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md:144-159`, `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:25-45` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:42` | Sec 4 | Tom: does not use Squeeze Momentum; analyzes compression via volume profile value areas | SOURCED (analyst extract) | `MyTradingSys/research/orderflow_extracts_1112/extract_AtR_c-B0jw8.md:60-65` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:43` | Sec 4 | Fabio: order-flow squeeze (aggressive buyers at top, forced closing of absorbed side) | SOURCED (analyst extract) | `MyTradingSys/research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md:53-65`, `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md:62-74` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:44-48` | Sec 4 | Malkan, NK StockTalk, CCU, Habib/CBP, CryptoCred: do not use Squeeze Momentum | SOURCED (negative grep) | `MyTradingSys/research/malkan_level_shorts_2026-11-09/READING.md:5`, `nk_stocktalk_1113/`, `CCU_RULES_2026-10-31.md`, `extracts/processed/`, `cryptocred/TEST_PLAN.md` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:54-56` | Sec 5 | Fable Run 6 Krown S8 4h: C0 n=420, mean net R +0.1312, t=+1.73, INCONCLUSIVE; comparator n=51,831 -0.0249 | OURS | `MyTradingSys/research/fable_run6_powered_prereg/RESULT.md` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:57` | Sec 5 | Pre-US Bollinger squeeze 15m BTCUSDT: n=192, UP 29%, DOWN 29%, SIDEWAYS 43%, broke both 23%, range 1.54x | OURS | `MyTradingSys/research/pre_us_squeeze_2026-10-29/RESULT.md` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:58` | Sec 5 | Volume-confirmed BB squeeze breakout 4h 6 pairs: DEV +88 bp p=0.008, VAL -13 bp p=0.60, DO NOT USE | OURS | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:59` | Sec 5 | Squeeze state census 90d (15m/1h/1d): in squeeze 59.1%/59.8%/60.0%, median run 13/13.0/12.5 | OURS | `MyTradingSys/research/tv_favorites_2026-11/SQUEEZE_STATE.md` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:64-71` | Sec 6 | Live Aid displays (`COILED`, directional momentum, release banner, `sqz_release`) | OURS | `tools/live_aid/indread.js:32-35, 127-142`, `live_aid.html`, `home.js:48, 121` |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:74-77` | Sec 7 | Confluence role: TIMING; CONTEXT ONLY; veto against coiled or fading momentum | OURS | Repo synthesis |
| `MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:82-85` | Sec 8 | Open tests (HTF trend gate, nesting, breakout vs midline retest, Fable Run 6 val) | OURS | Proposed tests (not filed) |

---

## 2. Cited Local Source File Verification

| Cited File & Claim | Status | Exact Location & Evidence |
|---|---|---|
| `FORMULAS.md` s31: quirk `dev = multKC * stdev(source, length)` | FOUND | `MyTradingSys/backtest/layers/FORMULAS.md:694` (`dev = multKC * stdev(source, length)`, `textbook_bb=True` at `:694,697,699`) |
| `FORMULAS.md` s31: `VERIFIED-TV 2026-11-07` 3/3 momentum, 4/4 dots | FOUND | `MyTradingSys/backtest/layers/FORMULAS.md:693` (matches TradingView on 3/3 bars, dots 4/4 bars) |
| `MyTradingSys/research/tv_favorites_2026-11/USAGE_squeeze.md:11-15,25,30,36,41,58-66` | FOUND | `MyTradingSys/research/tv_favorites_2026-11/USAGE_squeeze.md:25,30` ("The idea behind the indicator is that periods of low volatility are followed by periods of high volatility, and vice versa.", "The premise is simple: periods of low volatility are followed by periods of high volatility, and vice versa.") |
| `SQUEEZE_STATE.md` (15m/1h/1d share & median run) | FOUND | `MyTradingSys/research/tv_favorites_2026-11/SQUEEZE_STATE.md:5-6` (1d 90 bars, 60.0%, median 12.5), `:13-14` (1h 2160 bars, 59.8%, median 13.0), `:22-23` (15m 8640 bars, 59.1%, median 13) |
| `fable_run6_powered_prereg/RESULT.md` (C0 & strata & comparator) | FOUND | `MyTradingSys/research/fable_run6_powered_prereg/RESULT.md:3` (C0 n 420, mean net R +0.1312, SE 0.0760, t +1.73), `:14-21,32-39` (strata), `:53` (n 51831, mean net R -0.0249) |
| `pre_us_squeeze_2026-10-29/RESULT.md` (n=192, UP 29%, DOWN 29%, etc.) | FOUND | `MyTradingSys/research/pre_us_squeeze_2026-10-29/RESULT.md:13-15` (Squeeze 192, 29%/29%/43%, broke both 23%, held 52%, 1.54x; Wide 223, 0.80x, 4%) |
| `VOLUME_RESEARCH_REPORT_2026-10-09.md` (V4 4h DEV +88 bp, VAL -13 bp) | FOUND | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:99` ("DEV 4h +88 bp [+15, +155] p = 0.008; **VALIDATION -13 bp [-109, +81], p = 0.60") |
| Krown extracts (`extract_kcMnnQr1VFg.md`, `extract_P3rDSh187TE.md`) | FOUND | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md:144-159` and `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:25-45` |
| Tom extract (`MyTradingSys/research/orderflow_extracts_1112/extract_AtR_c-B0jw8.md:60-65`) | FOUND | `MyTradingSys/research/orderflow_extracts_1112/extract_AtR_c-B0jw8.md:60-65` (fair vs unfair price; stock squeeze mentioned at `:55`) |
| Fabio extract & ledger (`MyTradingSys/research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md:53-65`, `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md:62-74`) | FOUND | `MyTradingSys/research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md:57,64` and `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md:62,67,74` |
| Malkan, NK, CCU, CryptoCred (no Squeeze Momentum) | FOUND | Zero matches for `squeeze` in `MyTradingSys/research/malkan_level_shorts_2026-11-09/READING.md:5`, `MyTradingSys/research/nk_stocktalk_1113/`, `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`, `MyTradingSys/backtest/layers/cryptocred/TEST_PLAN.md` |
| `indread.js:32-35, 127-142` & 12 rows (`MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:64-65`) | **NOT FOUND / MIS-CITED** | `MyTradingSys/tools/live_aid/indread.js:12-13,38-55,81-83,115` has only 3 timeframes (`15m`, `1h`, `4h`), not "12 rows (1m through 1w)" (`MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:65`); file ends at line 139 (`:142` out of range); `squeeze()` is at `:38-55`, `cells.sqz` at `:81-83`, `"Squeeze just released: "` at `:115` |
| `home.js:48, 121` for `sqz_release` (`MyTradingSys/research/indicator_rulebooks/SQUEEZE.md:69-71`) | **NOT FOUND / MIS-CITED** | `sqz_release: 'Squeeze released'` is at `MyTradingSys/tools/live_aid/home.js:533`, not at `:48` or `:121` |

---

## 3. Primary Source Verification Table (UNVERIFIED & Unquoted Rule Lines)

| Rule Line & Claim (`SQUEEZE.md`) | Primary Source URL / Reference | Verbatim Quote or `NOT FETCHED` | Verdict |
|---|---|---|---|
| Sec 2 (`:18-19`): Original Developer John F. Carter (*Mastering the Trade*, Ch. 11) & LazyBear `SQZMOM_LB` | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `study(shorttitle = "SQZMOM_LB", title="Squeeze Momentum Indicator [LazyBear]", overlay=false)` / `This is a derivative of John Carter's "TTM Squeeze" volatility indicator, as discussed in his book "Mastering the Trade" (chapter 11).` | CONFIRMED |
| Sec 2 (`:20`): Core Premise quote `"The premise is simple: periods of low volatility are followed by periods of high volatility, and vice versa."` (cites `CARTER:246, USAGE:25, LB_TV`) | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `Black crosses on the midline show that the market just entered a squeeze (Bollinger Bands are with in Keltner Channel). This signifies low volatility, market preparing itself for an explosive move (up or down).` (The exact quote in `:20` does not appear on `LB_TV`, despite `USAGE:25` attributing it to LazyBear; `CARTER:246` is a paid book.) | CONTRADICTED |
| Sec 2 (`:21`): Inputs & Defaults (BB 20, mult 2.0; KC 20, mult 1.5, TR; quirk `dev = multKC * stdev`) | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `length = input(20, title="BB Length")` / `mult = input(2.0,title="BB MultFactor")` / `lengthKC=input(20, title="KC Length")` / `multKC = input(1.5, title="KC MultFactor")` / `useTrueRange = input(true, title="Use TrueRange (KC)", type=bool)` / `dev = multKC * stdev(source, length)` | CONFIRMED |
| Sec 2 (`:22`): Setup Requirement >= 6 consecutive squeeze dots | John F. Carter, *Mastering the Trade* (McGraw-Hill, 2005/2012, pp. 250-252) | `NOT FETCHED` (paid book; no public primary source text; not present on `LB_TV`) | NOT FETCHED |
| Sec 2 (`:23`): Trigger ("Squeeze Fires"): first bar BB expands outside KC (black/red to gray/green) | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `Black crosses on the midline show that the market just entered a squeeze (Bollinger Bands are with in Keltner Channel). This signifies low volatility, market preparing itself for an explosive move (up or down). Gray crosses signify "Squeeze release".` | CONFIRMED |
| Sec 2 (`:24`): Directional Rule: trade in momentum histogram direction at release bar | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `Mr.Carter suggests waiting till the first gray after a black cross, and taking a position in the direction of the momentum (for ex., if momentum value is above zero, go long).` | CONFIRMED |
| Sec 2 (`:25`): Timeframe (5m, 15m, 60m, daily, weekly; MTF alignment) | John F. Carter, *Mastering the Trade* (pp. 255-258) | `NOT FETCHED` (paid book; not specified on `LB_TV`) | NOT FETCHED |
| Sec 2 (`:26`): Exit Rule when momentum fades / color shift | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) | `Exit the position when the momentum changes (increase or decrease --- signified by a color change).` (Note: `LB_TV` specifies a color change; the "two consecutive bars" detail from `CARTER:253` is unverified.) | CONFIRMED |
| Sec 2 (`:27`): Warning / Caveats (never anticipate before fire; false breakouts into S/R) | John F. Carter, *Mastering the Trade* (p. 261) | `NOT FETCHED` (paid book; not present on `LB_TV`) | NOT FETCHED |
| Sec 3 (`:32`): Firing into major S/R fails; filter with HTF trend (e.g. 200 EMA) | `https://enlightenedstocktrading.com/squeeze-momentum-indicator/` | `Traders can overcome these issues by combining the Squeeze Momentum Indicator with trend filters (like moving averages), momentum confirmation (like RSI or MACD), and proper risk management rules.` / `: Only enter if the 20-day EMA is above the 50-day EMA.` (Neither support/resistance nor 200 EMA appears in the article.) | CONTRADICTED |
| Sec 3 (`:33`): Mechanical breakout entries without HTF filter yield 35% to 50% win rate | `https://trendspider.com/learning-center/ttm-squeeze-explained/` | `NOT FETCHED` (HTTP Error 404: Not Found) | NOT FETCHED |
| Sec 3 (`:34`): Multi-timeframe squeeze nesting produces highest probability explosive breakouts | `https://trendspider.com/learning-center/ttm-squeeze-explained/` | `NOT FETCHED` (HTTP Error 404: Not Found) | NOT FETCHED |
| Sec 3 (`:35`): Squeeze ON identifies low-volatility balance where OI builds before liquidation cascade | QuantConnect & PickMyTrade (no URL in `MyTradingSys/research/tv_favorites_2026-11/USAGE_squeeze.md:38-42`) | `NOT FETCHED` (no primary URL cited; verbatim quote not found in public search) | NOT FETCHED |
| Sec 3 (`:36`): Standalone fee-net profitable edge for crypto scalping on 1m/5m (`UNVERIFIED`) | `https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/` (`LB_TV`) & `https://enlightenedstocktrading.com/squeeze-momentum-indicator/` | `My (limited) experience with this shows, an additional indicator like ADX / WaveTrend, is needed to not miss good entry points.` (`LB_TV`) / `Many traders see a squeeze and jump in blindly, which often leads to trading that contains substantial risk.` (`enlightenedstocktrading.com`) | CONTRADICTED |
