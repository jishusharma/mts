# Pre-registration: Malkan GFS (Grandfather-Father-Son) on BTC 1D/4h (Readiness Checklist, PRE_REG_TEMPLATE.md)

**Date:** 2026-10-20  
**Card:** `malkan-gfs-btc-htf-prereg` (SONNET, priority 2)  
**Task Goal:** Implement the 'Edge-Before-Extraction' pre-registration on Malkan GFS (Grandfather-Father-Son: Monthly RSI > 60, Weekly RSI > 60, Daily RSI support at 60) on historical Binance 1D/4h BTC DEV klines (count-only + `prereg_gate.py` power check first).  
**Strategic Directive:** `MyTradingSys/research/GROUND_LEVEL_YOUTUBE_EXTRACTIONS_STRATEGY_2026-10-18.md:87-97` (Section 6.2 item 2: Edge-Before-Extraction Decision Rule).  
**Template:** `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:1-78`  
**Provenance Rule:** Every number is labeled SOURCED (quote + file:line) or OURS (engineering/design choice). No P&L backtest run; no tuning; edits to live code out of scope.

---

## 0. Pre-build gate (items 0a-0f; decision q13, 2026-10-14: adopted, "be flexible")

- 0a Cost: Smallest stop or target this idea uses? On BTC fees stay under 0.25 R only with a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry). On BTC daily DEV klines, median stop widths read from signal-bar candle structures are: MAL-2 = 4.5% [SOURCED `EVENT_COUNTS.md:32`], MAL-5 = 6.3% [SOURCED `EVENT_COUNTS.md:33`], MAL-10 = 5.2% [SOURCED `EVENT_COUNTS.md:34`]. Round-trip taker fee on BTC is 10 bps (0.0010) [SOURCED `fees.py:23`]. Cost in R is cost_R = 0.0010 / 0.045 = 0.022 R (MAL-2), 0.016 R (MAL-5), and 0.019 R (MAL-10) [SOURCED `EVENT_COUNTS.md:32-34`]. Fee shares of R are strictly between 1.6% and 2.2% of R, well below the 0.25 R (25%) economic ceiling. Gate 0a passes.
- 0b Gross: Does a cheap fixed-horizon check on existing data show a raw move of at least 2x the round-trip cost? Yes. 2x round-trip fee cost is 20 bps (0.0020) to 28 bps (0.0028) under Binance taker/slippage sensitivity [SOURCED `candle_patterns_2026-10-04/pilot/run_p1.py:27`]. Daily median true range on BTC DEV is ~3.52% (~352 bps) [SOURCED `PRE_REG_CRYPTOCRED_HTF.md:11`]. Target moves at 2.0R span 9.0% to 12.6% [OURS, arithmetic 2 * 4.5% and 2 * 6.3%], exceeding round-trip transaction costs by more than 45x to 63x. Gate 0b passes.
- 0c Record: Does the source have dated calls or trades we can score on BTC data? NOT_IN_DATA. Malkan's YouTube channel contains 876 videos of educational lectures, webinar teaching, and retrospective chart analyses [SOURCED `SETUP_SUMMARY.md:37,78`, `HOME_FIT_AUDIT_MALKAN.md:18-20`]. There are 0 timestamped or dated real-time trade calls in the repository. Per Gate 0c rule, with no dated record to score, the Malkan GFS strategy is classified strictly as a HYPOTHESIS, NEVER A CORE. Gate 0c is answered: hypothesis-only classification.
- 0d Data: Does BTC history hold every input the source reads? Yes for BTC test. Malkan's GFS rules read exclusively Wilder RSI(14) on closed monthly, weekly, and daily bars plus candle high/low/close [SOURCED `FORMULAS.md:10-29`, `SETUP_SUMMARY.md:77,113`]. No order flow, aggressor volume, CVD, or open interest is used. Binance BTCUSDT 1m klines across the DEV period (2017-08-17 to 2024-06-30, 2,510 daily bars and 358 weekly bars) provide continuous, gap-free OHLC [SOURCED `EVENT_COUNTS.md:26`]. Note that monthly RSI(14) requires 14 closed calendar months of warmup before firing [SOURCED `EVENT_COUNTS.md:63`]. Gate 0d passes for BTC.
- 0e Power: Trades in the dev window and the detectable edge; if larger than the claimed edge, write INCONCLUSIVE in advance or do not run (backtest/power_mde.py). Count-only check on historical Binance BTC DEV klines (2,510 daily bars, 358 weekly bars) yields severely restricted event counts: MAL-2 has n = 7 events [SOURCED `EVENT_COUNTS.md:32`], MAL-5 has n = 25 events [SOURCED `EVENT_COUNTS.md:33`], MAL-10 has n = 6 events [SOURCED `EVENT_COUNTS.md:34`]. Evaluating `scripts/dev/prereg_gate.py` with repo-wide Holm family size m = 57 (from `verdicts.py count --split DEV`) and standard two-point sd = 1.732 [SOURCED `EVENT_COUNTS.md:26`]:
  - MAL-2 (n=7, sd=1.732, cost=0.022): z_holm = 3.327, MDE = 2.728 R, MDE + cost = 2.750 R vs max plausible gross 0.30 R. Events needed for 80% power at 0.10 R net = 674 (under Holm m=57) / 1,654 (unadjusted, `EVENT_COUNTS.md:32`). Result: `BLOCK: do not freeze (write BLOCKED.md with these numbers)`.
  - MAL-5 (n=25, sd=1.732, cost=0.016): z_holm = 3.327, MDE = 1.444 R, MDE + cost = 1.460 R vs max plausible gross 0.30 R. Events needed for 80% power at 0.10 R net = 646 (under Holm m=57) / 1,650 (unadjusted, `EVENT_COUNTS.md:33`). Result: `BLOCK: do not freeze (write BLOCKED.md with these numbers)`.
  - MAL-10 (n=6, sd=1.732, cost=0.019): z_holm = 3.327, MDE = 2.946 R, MDE + cost = 2.965 R vs max plausible gross 0.30 R. Events needed for 80% power = 678. Result: `BLOCK: do not freeze`.
  Every setup on BTC DEV has N << 100, MDE exceeding 1.44 R (over 4.8x the maximum plausible gross edge of 0.30 R), and is statistically incapable of detecting an edge. Gate 0e FAILS closed on BTC: all Malkan GFS setups on BTC are formally declared BLOCKED / INCONCLUSIVE IN ADVANCE DUE TO SEVERE UNDERPOWERING.
- 0f Kill: Which result ends this source for good, and how many redesigns are allowed before it? Per `GROUND_LEVEL_YOUTUBE_EXTRACTIONS_STRATEGY_2026-10-18.md` section 6.2 item 2 and card `malkan-gfs-btc-htf-prereg`:
  "Decision rule: if GFS shows no power or no DEV edge on BTC, cancel all remaining Malkan video downloads; if it passes, ingest only v8pCR_bA0_0 and U12jz3LQhy0."
  Because Gate 0e is BLOCKED on BTC DEV (N = 7 to 25 events, MDE >= 1.44 R vs 0.30 R ceiling), the pre-registered kill rule executes immediately:
  1. CANCEL all remaining Malkan YouTube video downloads and extractions (specifically including `v8pCR_bA0_0` and `U12jz3LQhy0`) for BTC trading.
  2. Permanently HALT in-agent and automated scraping of the Malkan YouTube channel to eliminate HTTP 429 rate limit bans across all worker nodes.
  3. Re-route all future Malkan research exclusively to its native home market: Indian Equities (Nifty 100 / Nifty 500), where cross-sectional asset pooling achieves the required 1,655 events over 5-10 years (as established by `UNIVERSE_POWER.md`). Exactly ZERO (0) redesigns are permitted on BTC.

---

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Answer: Home market is Indian equities: Nifty 50, Nifty 100, and large liquid Indian cash equities (e.g. Tata Motors), with short positions taken exclusively through index or stock futures [SOURCED `HOME_FIT_AUDIT_MALKAN.md:12`, `extract_Wvq1TZh8aF0.md:284-287,312`]. Timeframe is a multi-timeframe trio of 14-period RSI charts: Monthly = Grandfather (macro regime), Weekly = Father (trend gate), and Daily = Son (execution entry) [SOURCED `extract_-CBvFi40sIQ.md:22`, `extract_A-CQiV_UFB4.md:372-374`]. Session is Indian cash equity hours (09:15 to 15:30 IST); trades execute on daily candle closes or buy-stop triggers on subsequent opens. Holding period is swing to positional: typically 2 to 4 days for short swings and 3 to 7+ days for 5-star trend rides, held while Weekly and Monthly RSI remain above 60 [SOURCED `HOME_FIT_AUDIT_MALKAN.md:12`, `extract_Wvq1TZh8aF0.md:167-172`].
Evidence (file:line):
- `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:167-172` ("swing... two-four days")
- `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:284-287` (Nifty weekly example)
- `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:312` (shorting only through futures)
- `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:22` ("On all 3 timeframes you have to apply 14 period RSI")
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:9-15`

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Answer: NOT_IN_DATA. No dated trade ledger exists for Malkan. The six extracted YouTube videos are educational lectures and conceptual presentations; every row in `SETUP_SUMMARY.md` records "0 trades in a ledger" [SOURCED `SETUP_SUMMARY.md:78`]. On-screen examples lack timestamped trade fills with minute precision [SOURCED `HOME_FIT_AUDIT_MALKAN.md:18-20`]. Ground truth is therefore evaluated solely through deterministic synthetic unit test cases verifying RSI 40/60 support detection and candle trigger geometry [SOURCED `test_pre_reg_template.py:81-92`].
Evidence (file:line):
- `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:37,78`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:16-22`
- `MyTradingSys/research/layer_lab/reports/2026-10-17_malkan-hindi-rows-gpt-read.md:82`

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Answer: Recall on an author trade ledger is NOT_IN_DATA (due to absence of dated trade records in item 2). Fire rate on historical BTC DEV (2,510 daily bars, 2017-08-17 to 2024-06-30):
- MAL-2 (Daily RSI support at 60 with Weekly+Monthly RSI > 60): 7 events across 6.87 years = 1.02 events/year [SOURCED `EVENT_COUNTS.md:32`].
- MAL-5 (Daily RSI in 58..62 green candle, order over high): 25 events across 6.87 years = 3.64 events/year [SOURCED `EVENT_COUNTS.md:33`].
- MAL-10 (Daily RSI support at 40): 6 events across 6.87 years = 0.87 events/year [SOURCED `EVENT_COUNTS.md:34`].
Fire rate on BTC is excessively sparse (0.87 to 3.64 events per calendar year), confirming that BTC alone does not generate sufficient trade occurrences for statistically robust evaluation.
Evidence (file:line):
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:32-34`
- `MyTradingSys/research/malkan_universe_2026-10/UNIVERSE_POWER.md:87-97`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:23-29`

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Answer: Every Malkan setup requires strictly OHLC price bars to compute Wilder RSI(14) on close and identify candle trigger levels (candle high, low, close). No aggressor order flow, tick volume, open interest, or funding rate is required [SOURCED `HOME_FIT_AUDIT_MALKAN.md:32-34`, `WEB_RESEARCH.md:273-274`]. For BTC, Binance DEV klines (2,510 daily bars and 358 weekly bars) provide continuous, gap-free inputs [SOURCED `EVENT_COUNTS.md:26`]. Missing Indian equity daily/weekly/monthly series are scored as NOT_IN_DATA for the home market.
Evidence (file:line):
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:30-36`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:26`
- `MyTradingSys/backtest/layers/FORMULAS.md:10-29`

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Answer: Wilder RSI(14) formula is mathematically codified in `FORMULAS.md` section 1 with hand-calculated benchmark cases [SOURCED `FORMULAS.md:10-29`]. Parity against Malkan's specific chart readings (e.g. Nifty weekly levels A 74.29, B 71; RSI 37.72, 38.89) is NOT_IN_DATA on BTC because matching Nifty historical series is absent from the repository [SOURCED `HOME_FIT_AUDIT_MALKAN.md:40`].
Evidence (file:line):
- `MyTradingSys/backtest/layers/FORMULAS.md:10-29`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:37-43`
- `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:287,334`

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Answer: Transaction costs follow the standardized Deribit taker fee model of 0.0005 per leg (10 bps round trip) [SOURCED `fees.py:23`]. On BTC daily DEV, stop widths are determined by local swing geometry: median stop is 4.5% (MAL-2), 6.3% (MAL-5), and 5.2% (MAL-10) [SOURCED `EVENT_COUNTS.md:32-34`]. Round-trip fee share of R is cost_R = 0.016 R to 0.022 R (1.6% to 2.2% of R), which is more than 10x below the 0.25 R maximum fee friction ceiling. Transaction costs are therefore negligible relative to stop width on daily BTC bars.
Evidence (file:line):
- `MyTradingSys/backtest/fees.py:23-24`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:18,32-34`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:44-50`

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Answer: Malkan's entry trigger requires placing a buy-stop order one tick above the high of the confirming daily candle (short: sell-stop below the low) [SOURCED `SETUP_SUMMARY.md:92`, `HOME_FIT_AUDIT_MALKAN.md:54`]. Entry occurs only if the subsequent bar trades through the breakout level; signals where price fails to exceed the signal bar high remain unfilled and are discarded. Both touch and trade-through must be logged, with execution occurring on trade-through.
Evidence (file:line):
- `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:92-95`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:51-57`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:33`

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Answer: Malkan's primary trade invalidation stop is placed below the low of the 3-bar swing formation or below the signal candle low [SOURCED `SETUP_SUMMARY.md:96-100`, `EVENT_COUNTS.md:33`]. Position is held for swing follow-through while Weekly and Monthly RSI maintain support above 60 [SOURCED `HOME_FIT_AUDIT_MALKAN.md:12`]. A fixed 1R/2R profit target bracket serves strictly as a conservative lower-bound benchmark, and the mismatch against Malkan's multi-day trend riding is explicitly stated.
Evidence (file:line):
- `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:96-105`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:58-65`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:19`

## 9. Null like-for-like: same session window, same order type, same fill rules.

Answer: The matched null model consists of placing identical buy-stop orders above daily candle highs on randomly sampled DEV bars that meet the Weekly+Monthly RSI > 60 macro gate but lack the Daily RSI support bounce, using identical 3-bar low stops and identical trade-through fill logic.
Evidence (file:line):
- `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:59-63`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:66-71`

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Answer: Expected N on BTC DEV is n = 7 (MAL-2), n = 25 (MAL-5), and n = 6 (MAL-10) across 6.87 calendar years [SOURCED `EVENT_COUNTS.md:32-34`]. All N are strictly < 100. Evaluating `power_mde.py` confirms that detecting a true edge of +0.10 R net at 80% power requires N = 1,650 to 1,655 independent trades [SOURCED `EVENT_COUNTS.md:12,26`, `UNIVERSE_POWER.md:87-97`]. Running `prereg_gate.py` shows MDE + cost = 1.46 R to 2.75 R vs the 0.30 R maximum plausible gross effect limit, resulting in `BLOCK: do not freeze`. Because N << 100 and MDE >> 0.30 R, Malkan GFS on BTC is formally classified as UNDERPOWERED AND INCONCLUSIVE IN ADVANCE, NEVER "NO EDGE".
Evidence (file:line):
- `MyTradingSys/backtest/power_mde.py:19-51`
- `scripts/dev/prereg_gate.py:21-65`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:12,26-38`
- `MyTradingSys/research/malkan_universe_2026-10/UNIVERSE_POWER.md:21-29,87-97`

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Answer: Binance BTC data from 2024-07-01 onward (VALIDATION 2024-07-01 to 2024-12-31 and HOLDOUT 2025-01-01+) remains completely untouched, unread, and sealed. No parameters have been inspected or tuned against post-DEV data.
Evidence (file:line):
- `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:69-73`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:82-87`

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Answer: Readouts must be stratified across BTC macro market regimes: Bull trend (2017, 2020-2021, 2023-2024), Bear trend (2018, 2022), and Sideways consolidation (2019, mid-2023). However, given that total BTC DEV events span only 6 to 25 occurrences, regime-stratified cells contain 1 to 9 events each, rendering intra-regime statistical inference completely impossible on BTC alone.
Evidence (file:line):
- `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:74-78`
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:26-38`
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:88-94`

---

## Decision Rule Summary (Execution of Edge-Before-Extraction Protocol)

| Criterion | BTC DEV Evaluation | Gate Status | Operational Action |
|---|---|---|---|
| **Event Count** | $n = 7\text{ (MAL-2)}, 25\text{ (MAL-5)}, 6\text{ (MAL-10)}$ | $N < 100$ | INCONCLUSIVE IN ADVANCE |
| **Detectable MDE** | $\text{MDE} = 1.44\text{ R to }2.73\text{ R}$ | $\text{MDE} > 0.30\text{ R}$ ceiling | BLOCKED by `prereg_gate.py` |
| **Events for 80% Power** | $N_{80} = 1,650\text{ to }1,655\text{ events}$ | Deficit of $>1,625\text{ events}$ | Cannot confirm edge on BTC |
| **YouTube Extraction Action** | Gate 0e BLOCKED | **KILL CONDITION TRIGGERED** | **CANCEL remaining video downloads (`v8pCR_bA0_0`, `U12jz3LQhy0`) for BTC; halt all Malkan scraping.** |
| **Strategic Re-route** | Home market has power | **RECOMMENDED** | Route testing to Indian Equities (Nifty 100/500) where $N \ge 1,655$ is achievable across 5-10 years (`UNIVERSE_POWER.md`). |
