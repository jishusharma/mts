# Home-fit audit: FlowHorse / whale positioning layer vs the 12-item readiness checklist

Date: 2026-10-18. Card: positioning-home-fit-audit. Checklist: BACKTEST_FAILURES_RESEARCH.md section 6 (template: backtest/PRE_REG_TEMPLATE.md). No backtest was run and no number was recomputed from market data; every number is quoted from an existing report, except the three power figures in item 10, which are arithmetic on quoted numbers (shown there).
Layer: `positioning` (system/LAYERS.md:122-135), code backtest/layers/positioning/funding_cvd_fade.py, driver backtest/layers/run_t055.py (candidate C1). Verdict on record: FAIL, closed (research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:14, OOS n 76, net mean -0.0453%, net Sharpe -0.0346 per trade).
Labels: FAIR = the test measures the idea it claims to on this item; UNFAIR = the "no edge" cannot yet be read as a statement about the trader (or the idea).

## Finding that frames everything: the tested layer is not a FlowHorse layer

BACKTEST_FAILURES_RESEARCH.md:69 lists the layer as "FlowHorse extracts (crypto positioning); thresholds UNDEFINED in source (grid)". The code and specs say otherwise:
- `funding_cvd_fade` is built from Memon 2026 (funding-extreme reversion, tier T2, relayed by four AI replies) plus a CVD/price divergence (T055a H2), not from any trader: backtest/layers/FORMULAS.md:356-370 and funding_cvd_fade.py:1-9.
- The three processed FlowHorse extracts contain zero mentions of funding, open interest or liquidation (grep of extracts/processed/flowhorse/*.md: 0/0/0). The rulebook counts FlowHorse rows built as layers: 0 of 32 (research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121).
- FlowHorse's real positioning content is in the two raw transcripts: the liquidation-cascade video (OI pickup, blown-out low, first green candle) and the NFP news video; neither has a funding rule, and in the NFP video he says he is not focused on funding (extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:230).
- The "whale" half was rejected before any test: research/whale_positioning_evidence_2026-09-12.md:19,46 ("Whale signals are coincident or lagged, not leading"; "DO NOT add whale-tracking DSA field"). There is no wallet-cohort data in the repo, so no whale layer was ever tested.

So the FAIL measures our grid encoding of a literature idea (36 parameter cells x 3 holds = 108 variants, run_t055.py:65-68 and T055 rerun :27), on 365 days of 15m BTC. It says nothing about FlowHorse and nothing about whales.

## Decision asked by the card: sourced threshold, or NO-SOURCE research test

Decision (OURS, judgement, 2026-10-18): label `funding_cvd_fade` a NO-SOURCE research test under VISION exception 2 (PROJECT_VISION.md:238-242: "NO-SOURCE research tests: specs with no trader behind them ... may run as labelled backtests only, never as live layers"). Reasons:
- No sourced threshold exists. hi/lo/lookback/n are "UNDEFINED in source" (FORMULAS.md:359,369). FlowHorse supplies no funding number; his only positioning quantities are a stop "1.5 ATR 2x ATR outside" the swing (extract_UrnES-HzQ6w_the_flow_horse.txt:283) and an OI "sharp pickup in a short amount of time" with no number (same file :295-296, :317-319).
- Consequence: every C1 parameter is OURS (grid-chosen on DEV); the layer is not called FlowHorse or whale in any report; its FAIL is closed as "this encoding, this window". A FlowHorse-sourced positioning layer (FHR-19 to FHR-26, CROSS_TRADER_RULEBOOK.md:84-91) is a separate, unbuilt hypothesis; it would again hit NO-SOURCE numbers for "sharp" and "first pause".

## 1. Source home: market, timeframe, session, holding period (with quote + file:line).

Verdict: UNFAIR
Answer: Two different homes, neither matched by the test. FlowHorse trades crypto and index-futures style profile (RTH/ETH sessions, DVOL), intraday to session, with news-event windows of 30-60 minutes (FHR-26) and cascade trades of hours; he says positioning relevance is "5, 15 minutes ago, a session ago". C1 has no trader home: its source (Memon 2026, 7 years of Binance) is known only through a one-line summary, so the paper's horizon and the percentile it used are NOT_IN_DATA. C1 holds 4, 16 or 48 bars of 15m (1h, 4h, 12h) chosen by grid, which is neither FlowHorse's horizon nor a sourced one.
Evidence (file:line): extracts/processed/flowhorse/extract_Oy2Z-FQ77NM.md:23 "If it took place 5, 15 minutes ago, a session ago even, it's probably still more relevant"; extracts/fresh/extract_izZyd-HrTSE_the_flow_horse.txt:1 (title "How I Trade News Catalysts in Crypto - Non Farm Payroll", ACTUAL LIVE VIDEO); CROSS_TRADER_RULEBOOK.md:91 (FHR-26, 30-60 min window); research/whale_positioning_evidence_2026-09-12.md:30 ("Extreme funding | T2 (Memon 2026, 7y Binance) vs T3 (n=2)"); backtest/layers/run_t055.py:87 (horizons 4, 16, 48).
Cheapest fix: C1 pre-registration states "NO-SOURCE research test, horizons OURS"; FlowHorse home goes into card P1.

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps). The ledger is split into design and check sets.

Verdict: UNFAIR
Answer: NOT_IN_DATA. There is no FlowHorse trade ledger and no dated call list. The five FlowHorse sources are three processed rule extracts (19 rules, 0 dated trades) and two raw transcripts (one live news day, one cascade trade described in words) that have no Part J extraction and no minute timestamps. Gate 0c therefore says "hypothesis, never a core" for any FlowHorse-derived layer. For C1 no trader exists, so a ledger cannot exist; this is item 2 of the NO-SOURCE label, not a defect of the run.
Evidence (file:line): CROSS_TRADER_RULEBOOK.md:6 (the two raw transcripts "have no rule ids and no Part J extraction"), :115 ("the two richest trade descriptions are raw transcripts"); extract_UrnES-HzQ6w_the_flow_horse.txt:579-583 (one cascade trade, no date or fill); research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md:50 (FlowHorse parked); PRE_REG_TEMPLATE.md:14 (gate 0c).
Cheapest fix: card P1 - list every dated FlowHorse trade or call visible in the 5 sources; if none can be scored on BTC 1m data, FlowHorse stays a hypothesis.

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere). Pass both before any P&L backtest.

Verdict: UNFAIR
Answer: Recall NOT_IN_DATA (needs item 2). Fire rate was not reported as a rate but the counts give one: IS 129 events in 24,505 bars (1 per 190 bars) and OOS 76 in 10,503 bars (1 per 138), so the encoding does not fire everywhere. That half is acceptable; the P&L backtest still ran with no recall check.
Evidence (file:line): T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27 (bars 35008, IS 24505 / OOS 10503), :33-34 (n 129 / 76); run_t055.py:238-246 (the OOS run goes straight to P&L).
Cheapest fix: card P2 reports fire rate per month and per year on the long window; recall waits on card P1.

## 4. Data carries every proof input (aggressor side, real volume, OI, funding); missing inputs are NOT_IN_DATA, never 0 (B084/B136).

Verdict: FAIR (for the inputs C1 reads); the FlowHorse inputs are NOT_IN_DATA
Answer: C1 reads 15m bars with taker-buy volume (aggressor proxy, CVD = 2*tbv - v) and funding. Funding is present for 2020-01..2026-08 (7,305 records) and B103 (silent zero funding) is fixed: every C1 trade is funded. FlowHorse's cascade inputs are not in the data: liquidation history (the repo has only a live forceOrder socket that keeps $100 price buckets, no history), tick/L2, cross-exchange basis are NOT_IN_DATA. OI exists only from 2025-09-01 to 2026-09-26 at 5 minutes. Whale cohorts (Glassnode-style entities of 1,000 BTC or more) are NOT_IN_DATA.
Evidence (file:line): funding_cvd_fade.py:48 (cvd uses tbv); T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7 (80 funding files, 7305 records), :36 (all trades funded); items/B103_funding_coverage.md:1; src/main/java/datafeed/BinanceLiquidationAccumulator.java:14-15, :31 (live forceOrder socket, $100 buckets, no history); research/PRE_REG_OI_DIVERGENCE_2026-10-10.md:10-11 (OI window); CROSS_TRADER_RULEBOOK.md:115 (LIQ/OI/TICK/L2 may not exist for backtest); whale_positioning_evidence_2026-09-12.md:16 (no universal whale definition).

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check (N3).

Verdict: FAIR (raw-bar check); trader-level parity NOT_IN_DATA
Answer: C1 is fully mechanical (percentile and strict-extreme CVD divergence), with no drawn level. Unit tests pin hand-computed funding percentiles (1.0 and 0.25), both divergence directions, the merged short/long events and the funding-only variant, so code equals spec. The spec's own choices are OURS: the percentile window includes the current record, and lookback is counted in 8-hour funding records (90 records = 30 days). Parity to what FlowHorse would call "extreme" cannot be tested: no chart frames, and he does not use funding.
Evidence (file:line): backtest/layers/positioning/test_funding_cvd_fade.py:27-32, :50-56, :66-90; FORMULAS.md:362-368 (definitions); extract_izZyd-HrTSE_the_flow_horse.txt:230.

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R (VISION economics).

Verdict: FAIR
Answer: The cost model is right and conservative for a fade at the close: Binance USDT-M taker 10 bps round trip plus 2 bps slippage plus funding, all charged (funding itself helped this fade: OOS -0.0453% with funding vs -0.0550% without). C1 has no stop, so an R-based fee share does not exist; the hold is time-based. In noise units the OOS per-trade sd is about 1.31% (item 10), so 12 bps of cost is about 0.09 sd. What kills the test is gate 0b, not the cost model: OOS gross mean 0.0650% is below one round-trip cost (0.12%) and well below the 2x (0.24%) gate; IS gross 0.5244% (4.4x cost) did not survive to OOS. The 2 bps slippage is OURS and flat.
Evidence (file:line): T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27 (fee 10 + slip 2 bps RT, funding included), :33-34 (gross vs net), :36 (funding effect); run_t055.py:111-113; PRE_REG_TEMPLATE.md:13 (gate 0b).

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price.

Verdict: FAIR
Answer: No resting order exists, so the CryptoCred-type touch-fill optimism (B151) cannot occur. Entry is at the close of the event bar and exit at the close of bar i+h, both as taker with the full fee and slippage; the funding record used is the last one at or before the bar open (no look-ahead). Caveat: spread and slippage at an extreme-signal bar were not measured (NOT_IN_DATA), so 2 bps is an assumption.
Evidence (file:line): run_t055.py:10-12 (entry at event-bar close), :111-113 (score_trades); FORMULAS.md:364 (funding known at bar time); funding_cvd_fade.py:83; items/B151_backtest_fill_optimism_and_selection.md:1 (the touch-fill defect class this layer does not have).

## 8. Exits match the trader's management, or the mismatch is stated (fixed bracket = a lower bound only).

Verdict: UNFAIR
Answer: C1 exits on a fixed hold of 1h, 4h or 12h, no stop, no target, no management; the hold is picked by IS grid. FlowHorse's stated management for positioning trades differs: cascade target is the origin of the breakdown with most size off there, stop 1.5-2 ATR beyond the obvious swing, news-trade bracket of 200-300 bp and "scratch if not immediately in profit". A time exit is a lower bound for a mean-reversion idea at best, and for FlowHorse it is a mismatch.
Evidence (file:line): run_t055.py:87 (horizons), :111-113 (exit at bar i+h close); extract_UrnES-HzQ6w_the_flow_horse.txt:283 (1.5 ATR / 2x ATR), :579-583 (target = point of origin); CROSS_TRADER_RULEBOOK.md:85, :88, :90, :92 (FHR-20, FHR-23, FHR-25, FHR-27).
Cheapest fix: only for a FlowHorse-sourced layer (after card P1); for the NO-SOURCE C1 test the pre-reg states "time exit, lower bound only".

## 9. Null like-for-like: same session window, same order type, same fill rules.

Verdict: UNFAIR
Answer: NOT_IN_DATA. The driver has no random-entry or shuffle null; the only multiple-testing control is PBO (CSCV) at 0.1385, which ranks IS variants against each other and says nothing about a matched random baseline. The FAIL is relative to zero, not to random entries with the same taker fills, the same 4/16/48-bar holds and the same fees. A fair null must also match the funding regime, because C1 events cluster in extreme-funding weeks.
Evidence (file:line): run_t055.py (no null/random/shuffle anywhere; grep count 0); T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27 (PBO 0.1385), :40-48 (criteria list has no null).
Cheapest fix: card P2 writes the null spec (random entries, same side mix, same holds, same cost, matched by funding regime and calendar); P3 pre-registers it.

## 10. Power: expected N per period computed before the run. If < 100, say "underpowered", never "no edge".

Verdict: UNFAIR
Answer: No power calculation is recorded. OOS n is 76 (< 100) over about 109 days (10,503 bars x 15 min), so the FAIL must read UNDERPOWERED / INCONCLUSIVE. Arithmetic on quoted numbers: the per-trade sd implied by mean -0.0453% and Sharpe -0.0346 (per-trade, run_t055.py:16) is 1.31%; the standard error at n=76 is 0.150%; the 80%-power detectable mean is about 0.42% per trade; the 95% interval on OOS net mean is about -0.34% to +0.25%. It therefore cannot exclude a real net edge of +0.25% per trade, which is twice the round-trip cost. The runner's own n >= 30 gate is below the template's 100.
Evidence (file:line): T055_BT_RERUN_FULLFUNDING_2026-10-07.md:14, :27, :33-34; run_t055.py:16, :43 (MIN_OOS_EVENTS = 30); backtest/power_mde.py:1-12; PRE_REG_TEMPLATE.md:16 (gate 0e).
Cheapest fix: card P2 computes expected N and the MDE on the DEV window 2022-01..2024-06 (C1 is wired to the 12-month raw folder only: run_t055.py:89 "roots": "raw"; klines exist from 2022-01 and funding from 2020-01), so the next test has about 2.5 years of design data instead of 365 days.

## 11. Holdout: untouched by the ledger days and by every design look (N1); trial count includes extensions and recall iterations.

Verdict: UNFAIR
Answer: There is no sealed holdout. The split is a chronological 70/30 of one 364.7-day window (35,008 bars, the 2025-09..2026-08 raw folder) that lies entirely inside the repo HOLDOUT period (2025-07-01..2026-09), while the TRAIN/DEV period 2022-01-01..2024-07-01 was never read by C1; the 30% OOS part (calendar 2026 only) was read at least three times (2026-09-29, the invalid 2026-10-06 rerun, the 2026-10-07 rerun) and the loader was changed in between (bars clipped to funding coverage). Trials: 108 variants in the grid, plus the OI studies and the funding/CVD merge decision made before the run; no trial ledger row for T055 exists. No ledger days exist to contaminate (item 2), the one good point. The 2022-01..2024-06 klines (raw_1m_2022) were never used by C1 and are clean DEV; the 2025-07..2026-08 stretch is burned for C1.
Evidence (file:line): backtest/bigtrade/fires_kline.py:90 and backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md:13 (repo split TRAIN 2022-01..2024-07, VALIDATE 2024-07..2025-07, HOLDOUT unchanged = 2025-07..2026-09 per :5); research/PRE_REG_OI_DIVERGENCE_2026-10-10.md:10-11 (raw folder starts 2025-09-01); run_t055.py:101-103 (chronological_split), :65-68 (36 cells), :87 (3 holds); T055_BT_RERUN_FULLFUNDING_2026-10-07.md:5-8 (why the 10-06 run was invalid and what changed), :27, :38 (OOS year 2026 only); BACKTEST_FAILURES_RESEARCH.md:19, :125 (N1 holdout rule).
Cheapest fix: P3 designs on DEV 2022-01..2024-06 only, reads VALIDATE 2024-07..2025-06 once, treats 2025-07..2026-08 as burned for C1 (a new holdout can only be data after this audit date), and starts a trial ledger that counts the 108 prior variants.

## 12. Stratified readout by regime and session (B154) next to the pooled number.

Verdict: UNFAIR
Answer: Only pooled IS and OOS are reported. B154 (no regime- or session-stratified verdict anywhere) is OPEN and names this report. The OOS is about 109 days in one calendar year, so a stratified read of it is impossible; the sibling OI divergence v2 study shows why a pooled read hides structure (pooled long and short both lose about 0.14% net at t of -4 to -9, roughly the cost level, while its per-regime cells differ, e.g. trend_up long -0.0887%). Funding extremes are themselves regime-dependent (they cluster in strong trends), which a pooled mean hides.
Evidence (file:line): items/B154_regime_and_session_stratified_backtest.md:1-14; T055_BT_RERUN_FULLFUNDING_2026-10-07.md:38 (OOS by year: 2026 n=76 only); research/OI_DIVERGENCE_V2_2026-10-10.md:10-18 (pooled rows).
Cheapest fix: the long window of card P2 gives several regimes; P3 fixes the regime definition before the run and reports strata beside the pooled number.

## Tally and order of cards

FAIR: items 4, 5, 6, 7 (4 of 12). UNFAIR: items 1, 2, 3, 8, 9, 10, 11, 12 (8 of 12).

Bottom line: the closed FAIL is a fair measurement of costs, fills and C1's own data (items 4-7) and an unfair one on everything that would tie it to a trader or to a detectable effect (source home, ledger, recall, exits, null, power, holdout, strata). Read it as "this NO-SOURCE funding x CVD grid, 15m, 1-12 h holds, taker costs, 109-day OOS of 76 trades: no net edge detectable at 0.42% per trade". Do not read it as "FlowHorse has no edge" or "whale positioning has no edge".

Cheapest path to a fair read, in order (follow-up Sonnet cards, none a P&L backtest):
1. P1 `positioning-flowhorse-ledger-feasibility` (items 1, 2, 3, 5; gates 0c, 0d): are there dated FlowHorse trades or calls (cascade, news days) that can be scored on BTC data? Decides whether FlowHorse positioning is testable or stays a hypothesis.
2. P2 `positioning-c1-longwindow-count-power` (items 3, 9, 10, 12; gates 0b, 0e): count-only C1 events on the DEV window 2022-01..2024-06 with the 2020+ funding, fire rate per month, power_mde, raw move versus 2x cost on DEV only, and the random-entry null spec. No net P&L, no VALIDATE or HOLDOUT read.
3. P3 `positioning-c1-prereg-no-source` (items 1, 6, 8, 9, 11, 12; gates 0a, 0f): the filled PRE_REG labelled NO-SOURCE (exception 2), parameters OURS, sealed holdout and trial ledger (108 prior variants), null, strata, kill rule. The backtest card waits on this and on the operator's choice. P1 and P2 are independent and can run in parallel.
