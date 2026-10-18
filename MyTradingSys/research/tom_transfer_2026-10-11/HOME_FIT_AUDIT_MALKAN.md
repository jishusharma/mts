# Home-fit audit: Malkan RSI layer vs the 12-item readiness checklist

Date: 2026-10-18. Card: malkan-home-fit-audit. Checklist: BACKTEST_FAILURES_RESEARCH.md section 6 (template: backtest/PRE_REG_TEMPLATE.md). Model: HOME_FIT_AUDIT_CRYPTOCRED.md. No backtest was run and no data was loaded; every number below is quoted from an existing report, or is arithmetic on those numbers and labelled OURS.
Layer: `rsi`, Malkan sub-layer (backtest/layers/rsi/: malkan_40_60.py, malkan_mtf.py, run_rsi_backtest.py, run_divergence_mtf.py). Verdicts on record: malkan_40_60 on BTC 1h OOS n 43, -0.092 % net, PBO 0.760; 4h n 17; 1d n 5, "NO-EDGE / insufficient n" (research/MARKET_GUIDE_RESULTS_2026-10-07.md:21). RSI divergence on every timeframe: no edge where n >= 300, 31 of 32 cells net negative, leads at n 6-54 (research/rsi_divergence_mtf_2026-10-09/RESULT.md:3-10). The 5-star driver `malkan_mtf` (weekly AND monthly gate, daily entry) exists (run_rsi_backtest.py:225-236) but no result for it appears in LAYERS.md, MARKET_GUIDE_RESULTS or research/; I found none. NOT_IN_DATA.
Labels: FAIR = the test measures the trader's idea on this item; UNFAIR = the "no edge" cannot yet be read as a statement about the trader.

Bottom line: 2 FAIR (items 4, 6), 10 UNFAIR. The Malkan "no edge" is a statement about the encoding: single-timeframe RSI 40/60 bounces on BTC 1h/4h/1d (the weekly and monthly gate that defines his 5-star is not applied in the run on record), a 1 % / 2 % / 100-bar bracket nobody sourced, entry at the signal close, 5 to 43 trades. It is not a statement about Malkan. His home is Indian equities on daily, weekly and monthly charts, and the home test cannot run today because no Indian equity series is in the repo (item 1, 4, 10).

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Verdict: UNFAIR
Answer: Home market is Indian equities: Nifty and large caps such as Tata Motors, with shorts taken through futures. Timeframes are three RSI(14) charts: monthly = grandfather, weekly = father, daily = son (entry); divergence is read on weekly and traded on the daily chart. No session issue (one daily close). Holding period: swing 2-4 days for short divergences (his examples reach target in 4-6 days); 3-7 days swing and 5+ days positional for the 5-star, held while weekly and monthly RSI stay above 60 (the 3-7 / 5+ figures are a web-research secondary, not his words). Crypto: no source text, he never addresses it. The run on record used BTCUSDT 1m history resampled to 1h/4h/1d (run_rsi_backtest.py:8,272), so the market, the entry timeframe (1h, 4h) and the higher-timeframe gate are all away from home.
Evidence (file:line): research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:167-172 (swing, "two-four days"); :284-287 (Nifty weekly example); :312 (shorting only through futures); extract_2HcJ3NeZmEQ.md:60-65 (Tata Motors on the sell list); extract_-CBvFi40sIQ.md:22 "On all 3 timeframes you have to apply 14 period RSI"; extract_A-CQiV_UFB4.md:372-374 "mostly daily and at the most weekly"; research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:276-279 (holding period), :302 (no crypto text); backtest/layers/rsi/run_rsi_backtest.py:8,272.
Cheapest fix: stop reading BTC 1h/4h as his market. The home test is Indian equities, entry on daily closes with closed weekly and monthly gates (card C2 sources the series).

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Verdict: UNFAIR
Answer: NOT_IN_DATA. There is no dated Malkan trade list. Six videos are extracted (19 setups plus one grade) and every row records "0 trades in a ledger": they are lectures, and on-screen examples are not counted. The channel holds 876 videos; 61 are ranked, captions for 12-13 ids are still pending the no-auth fetch card (SETUP_SUMMARY.md:41), and only 6 are extracted. His recap-style videos (for example the Tuesday talks) may hold dated calls, which is unchecked. Chart frames are not in the transcripts, so a candle or level he points at cannot be read ("made here" stops).
Evidence (file:line): research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:37 (totals), :78 (0 trades in a ledger, repeated per row); research/video_priority_2026-10-15/METHOD.md:13 (876 videos); RANKED_MALKAN.csv (61 rows); research/layer_lab/reports/2026-10-17_malkan-hindi-rows-gpt-read.md:82 (chart frames NOT_IN_DATA); card malkan-captions-fetch-noauth (ready, HAIKU); PRE_REG_TEMPLATE.md gate 0c.
Cheapest fix: card C1 counts dated calls in the extracts and saved captions. Fewer than 20 scorable calls means the layer stays a hypothesis under gate 0c, not a core.

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Verdict: UNFAIR
Answer: Recall NOT_IN_DATA (needs item 2). Fire rate was counted but never compared to anything: 132 events in 21,888 BTC 1h DEV bars (about one per 7 days); on BTC daily the pre-filtered counts are 7 (MAL-2), 25 (MAL-5), 6 (MAL-10), 35 and 42 (MAL-17, MAL-16) over 2510 bars. He states no frequency, and says sell setups are "very limited" in his scan. The 2026-10-07 P&L run happened before any recall or fire-rate check.
Evidence (file:line): research/layer_lab/malkan_rsi_event_table/REPORT.md:13; research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:32-36; research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:168 (sell side limited); research/MARKET_GUIDE_RESULTS_2026-10-07.md:21.
Cheapest fix: after C1, recall on the check set and fire rate per stock-year on the equity universe (count only, no P&L).

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Verdict: FAIR (BTC test); the home-market series is NOT_IN_DATA and is scored under items 1 and 10
Answer: Every Malkan setup reads only RSI(14) on closes plus candle colour, high and low: OHLC. No volume, aggressor side, OI or funding input is used, and his volume rules are not published (WEB_RESEARCH.md:273-274). BTC history is complete: 2,507,040 1m bars 2022-01-01..2026-10-07 with no gaps, and daily bars from 2017-08-17. Caveat that bites the 5-star: monthly RSI(14) needs 14 closed months, so the monthly gate is blank for the first 14 of the 57 months in a 2022 start (EVENT_COUNTS.md:63). Indian equity OHLC (split and bonus adjusted, delisted names included) is not in the repo: the committed coverage table lists Binance spot and Coinbase BTC only.
Evidence (file:line): research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:14 (2,507,040 bars, no gaps); research/krown_ta101_2026-10-13/DATA_COVERAGE.md:11-16 (series list); research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:63; WEB_RESEARCH.md:273-274.
Cheapest fix: none for BTC. For the home test, card C2 lists free public Indian EOD sources and their coverage before anything is fetched.

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Verdict: UNFAIR
Answer: Raw-bar check: RSI is Wilder, defined in FORMULAS.md section 1 with hand-computed cases, so the arithmetic is pinned. Parity with HIS reading is not: the regime rule is ours (BULL = min >= 40 and max >= 60 over 20 bars; the provenance audit rates it CONCEPT-ONLY) where he says weekly and monthly RSI above 60; the module docstring still describes the single-timeframe version; and the independent RSI-value audit card is not done. He quotes chart values that could serve as parity points (Nifty weekly A 74.29 and B 71; RSI 37.72 and 38.89 on a weekly example, "small decimal differences are acceptable"), but the matching Nifty weekly series is NOT_IN_DATA, so they cannot be checked.
Evidence (file:line): backtest/layers/FORMULAS.md:10-29 (Wilder); research/LAYER_PROVENANCE_AUDIT.md:59,66 (R10, R17 CONCEPT-ONLY); research/malkan_extract_2026-10-15/COMPARE.md:19-21,41; extract_Wvq1TZh8aF0.md:287,334; system/LAYERS.md:104 (indicator-values-multi-model-audit, ready, not done).
Cheapest fix: card C1 lists every quoted RSI value as a parity point; once C2 names a Nifty weekly source, compare rsi_core to those values at his tolerance.

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Verdict: FAIR (BTC test); Indian costs are NOT_IN_DATA
Answer: Fees come from fees.py (Deribit taker 0.0005 per side, maker 0), read by the driver and not hard-coded. Fee share of R is under the 0.25 R limit at both stops in play: with the run's 1 % stop a stop-out costs 5 bp + 5 bp = 0.10 R and a target exit 0.05 R; at his own candle-based stops on BTC daily (median stop 3.6-6.3 %) the round trip is 0.016-0.028 R. So fees are not why the Malkan result is negative. Open point: the stop width itself (1 %, NO-SOURCE) is judged under item 8. For the home market, fees.py holds no Indian schedule (STT, brokerage, GST, stamp duty, slippage; shorts only through futures): NOT_IN_DATA.
Evidence (file:line): backtest/fees.py:23-24; backtest/layers/rsi/run_rsi_backtest.py:14-17,63-69; research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:18,32-36 (cost in R at his stops); extract_Wvq1TZh8aF0.md:312 (futures).
Cheapest fix: for the home test, an India cost model labelled OURS and set before the run (card C3).

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Verdict: UNFAIR
Answer: The driver enters at the close of the signal bar as a taker (stop-first on shared bars, gap through the stop fills at the open). His entry is an order above the high of the signal candle (short: below the low), a breakout trigger that fills only if the next bar trades through it and can gap. The test therefore enters every signal, while his rule drops the signals that never break the high. The provenance audit already records it: entry named, trigger differs. He also waits for confirmation on the weekly (no direct weekly trade, wait for Monday). Touch vs trade-through is not reported because the order type was never modelled.
Evidence (file:line): backtest/layers/rsi/run_rsi_backtest.py:14-18,107; research/LAYER_PROVENANCE_AUDIT.md:73 (R24); WEB_RESEARCH.md:117; extract_-CBvFi40sIQ.md:68; extract_Wvq1TZh8aF0.md:277-279; research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:33 (MAL-5 geometry already coded as order over the high).
Cheapest fix: buy-stop one tick above the signal-candle high, valid for the next N bars, filled on trade-through or gap-open, unfilled signals counted; report both touch and trade-through (card C3).

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Verdict: UNFAIR
Answer: Run: stop 1 %, target 2 %, time exit 100 bars (all three NO-SOURCE), one position at a time. His exits: stop below the signal candle low (long) or above its high (short), stated in plain words for the 5-star and the divergence; divergence target is point C between A and B; the 7-star doubles the target with the stop unchanged; the 5-star numeric target is not recoverable from his words (the "daily RSI 60" target is a web secondary); management is to hold while weekly and monthly RSI stay above 60 (secondary). A 1 % stop is 3-6 times tighter than his typical daily candle stop on BTC (3.6-6.3 %), and exit shape flips the sign: on 1h bull signals the wide-stop 96-bar policy is +76 bp in TRAIN and -104 bp in VALIDATE (n 72 and 12), the 1 %/2 % policy is negative in both. The fixed bracket is a lower bound only.
Evidence (file:line): backtest/layers/rsi/run_rsi_backtest.py:56-58,109; research/LAYER_PROVENANCE_AUDIT.md:70-72 (R21-R23); research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:333-336 (MAL-10 stop), :472-477 (MAL-16 stop, target C), :550-555 (MAL-19); COMPARE.md:87,160; WEB_RESEARCH.md:122-133; research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:99-104,146; EVENT_COUNTS.md:32-36 (median stops).
Cheapest fix: pre-register the exit set before the run: signal-candle-low stop, point-C / RSI-level target, hold-while-gate-holds, fixed bracket kept as the stated lower bound (card C3).

## 9. Null like-for-like: same session window, same order type, same fill rules.

Verdict: UNFAIR
Answer: The only comparator is a drift baseline: every bar treated as a long-only event, forward return at 1/5/20 bars. It is not a random-entry null with the same entry, exit, one-position rule and fees. The Malkan gate selects bull stretches, so a null drawn from all bars would measure bull drift, not skill; the null must draw from bars where the same weekly and monthly gate is true. Session matching is moot on daily bars.
Evidence (file:line): backtest/layers/runner.py:75-95 (baseline_return_stats); backtest/layers/rsi/run_rsi_backtest.py:294; BACKTEST_FAILURES_RESEARCH.md:106-108 (N7).
Cheapest fix: random-entry null on the gate-true bars with identical fills, exits and fees, at least 1,000 draws (card C3 writes the spec).

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Verdict: UNFAIR
Answer: The 2026-10-07 run reports 1h OOS n 43 as "NO-EDGE": the driver's own rule says "insufficient n" only below 30, but this checklist says below 100. Counts on BTC daily are 6-42 per rule over DEV and weekly 3-8; MDE is 0.62-1.63 R on daily and 1.40-2.29 R on weekly, all rated THIN. Pooling BTC, ETH, BNB and SOL reaches 66-127 events on the best rows with MDE 0.35-0.49 R, still far from confirming +0.10 R, which needs about 1,655 independent events. BTC-only monthly bars are underpowered: 57 months in a 2022 start, at most 43 with a monthly RSI, and the weekly-and-monthly gate plus the sixty-line support leaves 7 daily events (MAL-2). A BTC result for the 5-star is descriptive, never "no edge". The divergence verdict is the exception: 32 cells reached 300 events, so that negative is powered. Universe arithmetic, OURS and from BTC's rate (MAL-5: 25 events in 2510 days, about 3.6 per asset-year): 1,655 events is about 455 asset-years, so 100 to 500 stocks over 10 years before any allowance for clustering in bull markets. An equity rate is NOT_IN_DATA until C2.
Evidence (file:line): research/MARKET_GUIDE_RESULTS_2026-10-07.md:21; backtest/layers/rsi/run_rsi_backtest.py:27,59,85-90; research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:12,32-38,46-58,63; research/rsi_divergence_mtf_2026-10-09/RESULT.md:7-8; backtest/power_mde.py:1-12.
Cheapest fix: card C2 computes N per period and MDE for universes of 50, 100 and 500 stocks with power_mde.py; any run under 100 trades is labelled INCONCLUSIVE in advance.

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Verdict: UNFAIR
Answer: The driver splits the same 2022-01..2026-10 series 70/30 chronologically (OOS starts about 2025-05 by arithmetic: 0.70 of 1,741 days), which overlaps the VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) windows named later. So the line "VALIDATION/HOLDOUT untouched" in MARKET_GUIDE_RESULTS_2026-10-07.md:36 cannot hold for this driver on those dates (checked by arithmetic, not rerun). Trials: 27 malkan_40_60 variants x 3 timeframes and an 18-variant malkan_mtf grid, plus the tolerance sweep and the divergence anchor probe; no Malkan row exists in any TRIAL_REGISTRY.csv. The one good point: no ledger exists (item 2), so no ledger day can contaminate a holdout. The newer DEV-only work (event table, event counts) stops at 2024-06-30 and is clean.
Evidence (file:line): backtest/layers/rsi/run_rsi_backtest.py:76-78,265-272; research/MARKET_GUIDE_RESULTS_2026-10-07.md:36; research/bigtrade_2026-10-09/EXIT_POLICIES_RERUN_DEV_2026-10-17.md:1; research/bigtrade_2026-10-09/PLAN.md:53-57; research/layer_lab/malkan_rsi_event_table/REPORT.md:3; EVENT_COUNTS.md:4; BACKTEST_FAILURES_RESEARCH.md:42 (C7).
Cheapest fix: seal a fresh equity holdout (last 2 years of each stock, or forward from this audit date) before C3, and log every variant in a TRIAL_REGISTRY.csv before any run.

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Verdict: UNFAIR
Answer: Only the pooled IS/OOS line per timeframe is reported. A bull/bear side split exists in the exit-policy tables but not by market regime, and the divergence runner states the regime split is not available in code. B154 is OPEN. His rule is itself regime-conditioned (a 40-60 RSI range is consolidation and low probability; weekly and monthly RSI gate the daily entry), yet malkan_40_60 gates only on its own timeframe's regime, so gate-true and gate-false events are pooled. Session does not apply on daily bars; regime does: index bull/bear, and long vs short, which he treats differently.
Evidence (file:line): research/MARKET_GUIDE_RESULTS_2026-10-07.md:21; research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:93-104; research/rsi_divergence_mtf_2026-10-09/RESULT.md:16-21; items/INDEX.md:125 (B154); WEB_RESEARCH.md:62; research/LAYER_PROVENANCE_AUDIT.md:65 (R16).
Cheapest fix: pre-register strata (long/short, index regime, gate-true vs gate-false) and report each next to the pooled number (card C3).

## What a fair test needs

- Market and series: Indian equities, adjusted daily OHLC from the instruments' listing, built into weekly and monthly bars from the daily file (the way the Binance weekly was built), delisted names kept, at least 10 years so the monthly RSI(14) is defined and a full bull and bear cycle is covered. NOT_IN_DATA today.
- His timeframes and horizon: monthly and weekly RSI gates read on closed bars, daily entry and divergence on the daily chart (weekly divergence traded on the daily), swing holds of days to a few weeks, hold while the gate holds.
- Universe for N: a basket, not one asset. About 1,655 independent events are needed to confirm +0.10 R net at 80 % power; at BTC's MAL-5 rate that is about 455 asset-years (OURS arithmetic), so 100 to 500 stocks over 10 years, and clustered bull-market events count less than independent ones. Nifty 50 alone is too small.
- BTC-only is underpowered for the 5-star: 57 monthly bars in a 2022 start (at most 43 with an RSI) and 7 daily events behind the weekly-and-monthly gate with the sixty-line support (MAL-2). State this wherever a BTC Malkan number is quoted. Crypto transfer is a second, separately pre-registered question after the home test, pooled over BTC, ETH, BNB and SOL daily.
- Ground truth: dated Malkan calls from the videos if any exist (C1); otherwise the layer is a hypothesis under gate 0c.
- Encoding: his reading ("above 60", signal-candle stop, break of the high, point C), not our 20-bar min/max regime; every choice we add is labelled OURS.

## Tally and order of cards

FAIR: items 4, 6 (both for the BTC test only). UNFAIR: items 1, 2, 3, 5, 7, 8, 9, 10, 11, 12.

Cheapest path to a fair read, in order (follow-up Sonnet cards, none a backtest P&L run):
1. C1 `malkan-ledger-parity-feasibility` (items 2, 3, 5; gate 0c): count dated Malkan calls in the extracts and saved captions, list the quoted RSI values as parity points, verdict SCORABLE or HYPOTHESIS.
2. C2 `malkan-universe-data-power` (items 1, 4, 10; gates 0d, 0e): free public Indian EOD sources and their coverage, candidate universes of 50, 100 and 500 stocks, N and MDE with power_mde.py. Metadata only; no price series fetched.
3. C3 `malkan-prereg-dwm-equities` (items 6, 7, 8, 9, 11, 12; gates 0a, 0f): the filled PRE_REG with India costs (OURS), buy-stop fills with trade-through, his exits, the gate-matched random-entry null, a sealed holdout with a trial ledger, strata, and the kill rule. Waits on C1 and C2. The backtest card itself waits on this and on the operator's choice.
