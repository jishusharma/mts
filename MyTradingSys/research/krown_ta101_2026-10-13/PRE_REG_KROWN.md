# Pre-registration: Krown layer v0 - readiness (12 items, backtest/PRE_REG_TEMPLATE.md)

Filled 2026-10-14 from the 15 extracts (14 TA videos), updated after batch 2. An item with no answer or no evidence line is NOT_ANSWERED and the P&L run does not start.
Status line: items 1, 4 (partly), 6, 8, 9, 11, 12 answered; **2 and 5 NOT_ANSWERED; 3 and 10 planned (cards k2, k3)**. Detectors and the recall
check (items 3) are allowed before this is complete; no P&L backtest is. Extract paths are under `MyTradingSys/research/krown_ta101_2026-10-13/extracts/`.

## 1. Source home: market, timeframe, session, holding period
Answer: BTC/crypto, daily and weekly decisions, 6h/4h timing only after weekly and daily agree; daily close 00:00 UTC; 24/7 so no session. Holding
period NOT stated (days to weeks inferred from the timeframes; "scalp" lengths are not given).
Evidence: `extract__t_XIBrcjRk.md:115-122` (daily is the gold standard for most cryptos), `:85-94` (live on the daily, 4h/6h the lowest), `:53-61`
(close 00:00 UTC), `extract_8MvxK_nxO-0.md:56-63`.

## 2. Ground truth: a ledger of the source's own trades read from frames (minute timestamps), split into design and check sets
Answer: NOT_ANSWERED. TA 101 is a lecture series: charts are illustrations, not a trade ledger, and no entry/stop/target pair is ever stated
(every extract's Gaps section). Candidate ledger: Krown's daily BTC event-study videos and prospectively timestamped calls (options/research/
KROWN_FREE_VS_PAID.md s1b; CBP queue item krown_2026-09-25_OggsnATGbOg, status rejected) - not read, not extracted. Retrospectively narrated
charts cannot estimate a hit rate (research/layer_lab/candle_close_2026-10-14/RESEARCH.md:40).
Substitute for RECALL ONLY (never for hit rate): the dated examples in item 3.
Evidence: extracts' Gaps sections (e.g. `extract_qEfES84jwwo.md:265-274`, `extract_6aA-P4Gvhrc.md:277-284`, `extract_-NXzJs5JRks.md:285-293`).

## 3. Recall (encoding fires on the check set) AND fire rate (not everywhere)
Answer: planned (card k2). Check set = his dated chart examples, each first verified against klines (dates and prices from captions are unreliable):
(1) BTC weekly low March 2020 on about 3-3.5x volume (VOL-13); (2) February 2026 low on about 2x volume, rally from about 60k to 83k (VOL-08);
(3) December 2018 anchor respected March 2020 (TRL-20); (4) 2018 range, about February to November (RNG-05); (5) first test of 100,000 reached about
108,000 (SNR-17); (6) weekly 200 SMA lows 2015, 2018, 2020, 2022 (MAV-16); (7) death cross January 2022 with the 200 sloping down (MAV-21);
(8) 21/55 + 200 reversal and 2021 55 EMA/zone confluence (MAV-11, MAV-15); (9) Bitcoin 2017 weekly top: BBWP high for months (about May to December 2017), the top in December with bearish divergence, extreme volume and a later weekly MACD cross (TOP-12); (10) Bitcoin 2021 top: RSI lower highs, a shooting star and the MACD cross, volume and volatility weak (TOP-32); (11) a weekly 55 EMA reclaim given up within two closes (VJZ-13), the reversal off the 2018 lows about 4,000 to 14,000 and a move about 40,000 to 52,000 (VJZ-50, VJZ-49); (12) the BBWP-high dump examples (KCM-15). Pass bars declared now (OURS): detector fires within 2 bars of at
least 6 of the examples that verify against klines; fire rate per setup <= 1 event per 10 daily bars pooled (the "most days no trade" rule, KR-T05).
Evidence: examples at `extract_UqAvU1loT_k.md:73-80,120-130`, `extract_14bxwxC8gBQ.md:183-192`, `extract_6aA-P4Gvhrc.md:50-57`,
`extract_qEfES84jwwo.md:172-180`, `extract_-NXzJs5JRks.md:157-165,197-213`, `extract_7IxfsuD2wCM.md:126-136,343-350`, `extract_vjzy_KxJ_y8.md:121-132,458-476`, `extract_kcMnnQr1VFg.md:128-134`.

## 4. Data carries every proof input; missing inputs are NOT_IN_DATA, never 0
Answer: the layer needs OHLCV only (no aggressor side, OI, funding). Open point: volume venue (conflict C6): he reads Coinbase, the TradingView index
or CME because crypto volume can be faked; we have Binance klines. Coinbase/index daily volume is NOT_IN_DATA until fetched. Bars before 2017-08
(his 14-year and 26-year claims) are NOT_IN_DATA.
Evidence: `extract_UqAvU1loT_k.md:41-48` (venues), `:50-56` (coins vs dollars).

## 5. Profile/snapshot parity against the trader's own drawn levels or a raw-bar check
Answer: NOT_ANSWERED. His drawn zones are on video frames, which were not captured; captions carry only what he says. Planned substitute: blind
eye read of N charts by two readers (Claude and Jis) against detector zones, as in the Tom eye-read card, before any P&L.
Evidence: `extract_qEfES84jwwo.md:90-97` ("if it ain't obvious it ain't there": the obviousness filter is an eye call).

## 6. Cost per instrument; stop width in noise units; fee share of R < 0.25 R
Answer: EXPECT (not RESULT): daily stops of several percent against a round-trip cost of about 14 bp (taker 5 bp per side, repo schedule) give a fee
share of R near 0.05, far under 0.25. Computed from the data when k1 lands (ATR14 distribution on 1d/6h/4h, per arm). Maker entries tested in a
separate arm with trade-through reported.
Evidence: `research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:19,75` (fee schedule); `extract_HhV4HI9p5Uw.md` is retail DCA fees only and is not used.

## 7. Fills: touch AND trade-through reported; the entry is on the passive side of price
Answer: signals fire on a CLOSED bar (KR-T04), entries are (a) next bar open, taker, and (b) a resting limit at the zone edge, maker, filled only on
trade-through (touch also reported). Reuse the repo fill model (card gap-g4-through-ticks-flag). Planned in k1/k3.

## 8. Exits match the trader's management, or the mismatch is stated
Answer: MISMATCH STATED. He gives no stop distance and no general size. Sourced exits: a close beyond the zone (KR-X01), the far side of the compression zone as the
stop and a volatility peak as the exit (KR-Q05, KR-Q06), the range height (KR-R07), and a 20-85 % scale-out at tops (KR-P02). Everything else is OURS; a fixed
bracket is a LOWER BOUND on his discretionary management.
Evidence: `extract_qEfES84jwwo.md:212-221`, `extract_6aA-P4Gvhrc.md:209-217`, `extract_kcMnnQr1VFg.md:543-573`, `extract_7IxfsuD2wCM.md:27-35`.

## 9. Null like-for-like
Answer: same-window random entries with the same side, same timeframe, same order type, same fill rules and same hold; placebo lags drawn without
replacement with the lags printed (LESSONS_DIGEST s2); event studies use nearby-price controls (as METHOD.md in the candle-close lab).

## 10. Power: expected N per period computed before the run; if < 100 say "underpowered", never "no edge"
Answer: planned (k3, before any run). Rough bound: BTC DEV 2017-08..2024-06 is about 2,500 daily bars and about 360 weekly bars; a setup firing on
<= 10 % of bars yields at most a few hundred events and most setups far fewer; weekly and 200W events are tens. Most setups are expected to be
UNDERPOWERED on BTC alone (the tops framework S9 has only a handful of weekly events: descriptive, no P&L; S8 needs a count of distinct BBWP-compression episodes, not bars); pooling ETH and other majors (his own claim of "across all markets") needs a data card. Compute N from the real fire counts
and the minimum detectable effect (backtest/power_mde.py) first.

## 11. Holdout untouched; trial count includes extensions and recall iterations
Answer: splits reused from the volume and candle studies: DEV BTC spot 2017-08 .. 2024-06 (the volume study used perps from 2020-01), VALIDATION
2024-07-01 .. 2025-06-30, HOLDOUT 2025-07-01 .. 2026-09-30 sealed. DISCLOSURE: VALIDATION was touched by 4 frozen volume tests and the candle
pilot reserved it; it is not pristine for volume- or candle-related Krown hypotheses (candle-close REPORT:72 rule). Holdout stays sealed until a
rule is pre-registered and survives VALIDATION once. Every variant, recall iteration and H-id goes to the trial ledger.
Evidence: `research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:52`, `research/layer_lab/candle_close_2026-10-14/METHOD.md:9,44`.

## 12. Stratified readout by regime and session next to the pooled number
Answer: strata = mode (trend/range, KR-T06), top-down agree/disagree (KR-T03), volume flag, year; no session split (24/7 daily bars). Pooled first.
