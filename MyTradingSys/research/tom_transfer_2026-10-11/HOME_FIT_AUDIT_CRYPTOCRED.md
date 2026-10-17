# Home-fit audit: CryptoCred layer vs the 12-item readiness checklist

Date: 2026-10-17. Card: cryptocred-home-fit-audit. Checklist: BACKTEST_FAILURES_RESEARCH.md section 6 (template: backtest/PRE_REG_TEMPLATE.md). No backtest was run; every number below is quoted from an existing report.
Layer: `cryptocred` (backtest/layers/cryptocred/: cc_setups.py, run_cc_setups.py). Verdict on record: setups 1-3 FAIL on 1h, both fee variants (research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:163, rerun 2026-10-10 at :315-330). Stop sweep: every rule net-negative (research/cryptocred_stop_2026-10-10/STOP_SOURCES.md, section "NET R SWEEP RESULT").
Labels: FAIR = the test measures the trader's idea on this item; UNFAIR = the "no edge" cannot yet be read as a statement about the trader.

Bottom line: the 1h FAIL is a fair measurement of fills (item 7) and data (item 4) only. It is not a fair test of the trader on 8 of 12 items (timeframe, ground truth, recall, parity, cost/stop, exits, null, holdout/strata). "No edge" must be read as "this encoding at 1h with unsourced 0.1% stops and a fixed 1.5R/2.0R bracket loses after fees", not "CryptoCred has no edge".

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Verdict: UNFAIR
Answer: Home market is crypto (BTC/ETH), so no transfer is needed. Timeframe is daily/weekly structure with hourly entries and management; structure breaks need a close on the same timeframe as the anchor. The layer only ever ran 1h structure with 1h closes (run_cc_setups.py:59 allows 1h/15m/4h, every reported run is 1h). No session applies (24h market). Holding period is swing (days), never stated numerically; the runner caps at max_bars=1440 1m bars = 1 day (run_cc_setups.py:170).
Evidence (file:line): extracts/processed/cryptocred/extract__ndAoizXy64.md:48 "I'll be trading high timeframe from the daily and weekly but a lot of my entries and management will be on the hourly timeframe"; extract_inqHN8q57X4.md:34 "if you've got a daily structure it's only broken if you get a daily candle close through it"; extract_BHwoN7VPrBE.md:106 "I want to see a daily close through that high or low to constitute a market structure break"; extract__ndAoizXy64.md:42 daily trades manage on daily + 4h/6h/12h.
Cheapest fix: structure on 4h and 1d with same-timeframe closes, entries/management on 1h (needs a multi-timeframe adapter; a count-only check first, see card C2).

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Verdict: UNFAIR
Answer: NOT_IN_DATA. There is no CryptoCred trade ledger. The five extracts hold rules and teaching examples, not a dated list of his trades; no TOM_TRADE_LEDGER-style file exists for him (rg of research/ for a CryptoCred ledger finds none).
Evidence (file:line): extracts/processed/cryptocred/ holds 5 files (extract__ndAoizXy64.md, extract_BHwoN7VPrBE.md, extract_inqHN8q57X4.md, extract_XeQV2ECtZVQ.md, extract_Yp0k8HD5xro.md), all rule extractions; pre-build gate 0c in backtest/PRE_REG_TEMPLATE.md ("does the source have dated calls or trades we can score on BTC data?").
Cheapest fix: card C1 - find out whether any dated CryptoCred calls exist (his public chart posts are not in the repo); if not, the layer stays a hypothesis per gate 0c.

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Verdict: UNFAIR
Answer: Recall NOT_IN_DATA (needs item 2). Fire rate was never reported as a rate: setup 1 gives 1,536 signals and setup 2 about 1,400 over 41,520 hourly bars (2022-01..2026-09), roughly one signal per 27-30 bars; he says setups are selective ("most obvious or outstanding high or low"). The P&L backtest was run without passing recall.
Evidence (file:line): research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:175 (1536 signals, 1486 trades) and :321 (41,520 1h bars); extract_BHwoN7VPrBE.md:12 swing "smell test".
Cheapest fix: after C1, a recall + fire-rate check on the check set; with no ledger, a fire-rate-only check on 4h/1d (count signals, no P&L).

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Verdict: FAIR
Answer: The three setups read only OHLC (cc_structure swings/MSB, cc_retest). Binance BTCUSDT 1m klines 2022-01-01..2026-09-26 (2,491,200 bars, zero gaps) and 7,395 funding records are in the data and funding is included in net. No aggressor/OI input is used by this layer. His teaching also names volume-free structure only.
Evidence (file:line): research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:321 (data line); cc_setups.py:1-19 (module header, inputs are bars).

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Verdict: UNFAIR
Answer: NOT_IN_DATA for his drawn levels (no chart frames). Raw-bar check: unit tests pin find_swings/classify_msb on hand-computed bars (TEST_PLAN.md cases S1-S6), so the code does what the spec says, but the spec's swing rule is ours: he says there is "no single formula". Whether the encoded swings equal the ones he would draw is untested.
Evidence (file:line): extract_BHwoN7VPrBE.md:12 "there's no single formula... recency... significance... smell test"; backtest/layers/cryptocred/TEST_PLAN.md:1-30 (hand-computed cases); items/B143_cryptocred_stop_buffer_and_target_unsourced.md (C14-C23 NO-SOURCE).
Cheapest fix: card C1 includes any chart-frame levels it finds; otherwise state "unverifiable" in the pre-registration.

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Verdict: UNFAIR
Answer: Costs are modelled (Deribit taker/maker fees from fees.py plus funding), so the cost model is right. The stop is the problem: a 0.1% buffer around the level makes fee per R about 0.65 R (all_taker mean net -1.07 R vs -0.107 %, i.e. 1 R is about 0.1 %), far over the 0.25 R limit, and the 0.1% is NO-SOURCE. He says the stop is the trade invalidation, not a percent, and that stop width scales with the move (HTF swings get room). In the sweep the NO-SOURCE 0.1% stop is worst everywhere (-1.069 / -1.307 / -1.050 R) and the widest ATR stop least bad (-0.095 / -0.073 / -0.040 R, still negative). Gate 0a: BTC fees stay under 0.25 R only with a stop of at least 0.40% (taker) or 0.20% (maker entry); the 0.1% stop fails 0a by construction.
Evidence (file:line): cc_setups.py:53 setup1_sr_flip(stop_buffer_pct=0.001, target_r=1.5); items/B143_cryptocred_stop_buffer_and_target_unsourced.md:14-18; extract_XeQV2ECtZVQ.md:33 "your stop reflects your invalidation", :54 mixing low-TF stops with HTF ideas; research/cryptocred_stop_2026-10-10/STOP_SOURCES.md sweep table; PRE_REG_TEMPLATE.md gate 0a.
Cheapest fix: stop = structural invalidation level plus a noise-unit buffer set before the run (ATR multiple, labelled OURS); report fee share of R per setup. Do not grid.

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Verdict: FAIR
Answer: Resting limit at the broken level / fib zone, placed at the close of the confirm bar, filled only on a bar that trades one tick (0.1) through it; targets also need a tick through; blow-through bars fill; unfilled limits are counted (50 of setup 1's signals). The trade-through rule moved the result by under 0.01 percentage points. Caveat to keep: entry-after-retest means passive-side entry, which matches his "retest" teaching; touch-fill numbers were reported in the 10-07 run and trade-through in the 10-09 and 10-10 reruns.
Evidence (file:line): backtest/layers/cryptocred/run_cc_setups.py:105 find_limit_fill; test_run_cc_setups.py:208 (touch does not fill, trade-through does); CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:175 and :315-318.

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Verdict: UNFAIR
Answer: The layer uses a fixed target of 1.5R (setups 1-2) or 2.0R (setup 3) and a fixed stop, no trailing, no scaling. He manages with trailing stops under swing lows in trends, fixed targets at range boundaries/ATR in ranges, FTA (first trouble area) targets for beginners, and warns against automatic break-even. His only numbers are "two reward for one risk instead of 1.5" for counter-trend trades (a minimum, not a target). The fixed bracket is a lower bound only and the 1.5R is NO-SOURCE as a fixed value.
Evidence (file:line): extract__ndAoizXy64.md:124-138 (trailing vs fixed); extract_XeQV2ECtZVQ.md:121-123 (FTA); extract_BHwoN7VPrBE.md:82 "two reward for one risk instead of 1.5"; items/B143_...md:C15; cc_setups.py:53,178.
Cheapest fix: pre-register the exit set before running (structure-trail under swing lows; FTA = next opposing swing; both, with the fixed bracket kept as the stated lower bound).

## 9. Null like-for-like: same session window, same order type, same fill rules.

Verdict: UNFAIR
Answer: NOT_IN_DATA. No null/shuffle test exists for the CryptoCred layer: the runner states "Defaults only, no grid: PBO N/A". Session matching is moot (24h market), but a random-entry null with the same limit-fill, same stop/target and fees is missing, so "FAIL" is relative to zero, not to a matched random baseline.
Evidence (file:line): CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:11 ("PBO N/A, not part of the verdict"); run_cc_setups.py:285 (same text in the report writer); N7 in BACKTEST_FAILURES_RESEARCH.md.
Cheapest fix: random-entry null on the same bars with the identical fill and exit code (card C2 spec).

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Verdict: UNFAIR (setup 3 and any 4h/1d rerun); FAIR for setups 1-2 at 1h
Answer: 1h OOS n: setup 1 = 421, setup 2 = 398 (>100, powered for large effects); setup 3 = 167 trades total, OOS n = 48 (< 100): its FAIL must read "underpowered". Moving to the trader's real structure timeframes cuts N sharply (4h and 1d bars are 4x and 24x fewer, signals fewer still), so power must be computed with backtest/power_mde.py before any 4h/1d run. No power calculation is recorded for any CryptoCred run.
Evidence (file:line): CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:322-330 (OOS n 421 / 398 / 48; trades 167); STOP_SOURCES.md sweep table (n 1487 / 1392 / 167); backtest/power_mde.py:1-12.

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Verdict: UNFAIR
Answer: The split is a chronological 70/30 IS/OOS of the same 2022-2026 series (run_cc_setups.py:77), not a sealed holdout; the OOS part has been read in at least six reruns (b3dbe74, 10-06, 10-07 touch, 10-09 trade-through, 10-10 fixes, stop sweep) and the layer code was changed between them (bear fib zone, blow-through fills, target tick). Trial count: sweep alone = 12 setup/stop cells; reruns add more; none is recorded in a ledger. No ledger days exist to contaminate (item 2), which is the one good point. Any new 4h/1d run needs a fresh sealed holdout, which this series can no longer provide for the 1h design.
Evidence (file:line): run_cc_setups.py:77 chronological_split(is_frac=0.70); CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:1,157,315 (reruns); STOP_SOURCES.md sweep (12 cells).
Cheapest fix: seal the most recent period (or fresh data forward from the audit date) before the 4h/1d design and log every trial.

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Verdict: UNFAIR
Answer: Only pooled IS/OOS and per-year OOS are reported. B154 (regime and session stratified verdict) is OPEN. He says trend regime changes the right exits and risk-reward (counter-trend needs defensive parameters, ranging vs trending profit taking), so a pooled number mixes regimes he treats differently. Session is not relevant to him.
Evidence (file:line): items/INDEX.md:125 (B154 OPEN); extract__ndAoizXy64.md:132 (range vs trend profit taking); extract_BHwoN7VPrBE.md:82 (counter-trend defensive); CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md per-year OOS only.

## Tally and order of cards

FAIR: items 4, 7 (and 10 for setups 1-2 at 1h). UNFAIR: 1, 2, 3, 5, 6, 8, 9, 11, 12 (and 10 for setup 3 / 4h / 1d).

Cheapest path to a fair read, in order (follow-up Sonnet cards, none a backtest P&L run):
1. C1 `cryptocred-ledger-feasibility` (items 2, 3, 5; gate 0c): does any dated CryptoCred call/trade exist to score? Decides whether the layer is a hypothesis or testable.
2. C2 `cryptocred-htf-count-power` (items 1, 9, 10; gate 0e): count-only signals for 4h/1d structure with same-timeframe closes, fire rate, random-entry null spec and power_mde.py; no P&L.
3. C3 `cryptocred-prereg-4h-1d` (items 6, 8, 11, 12; gates 0a, 0f): the filled PRE_REG with invalidation-based stop (labelled OURS), trailing/FTA exits, sealed holdout, stratification plan and the kill rule. The backtest card itself waits on this and on the operator's choice.
