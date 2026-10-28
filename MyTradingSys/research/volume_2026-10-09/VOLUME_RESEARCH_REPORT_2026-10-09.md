# BTC volume research: buy volume, sell volume, exhaustion, patterns, time (2026-10-09)

Session MTS-2026-10-09-APP-ANA-btc-volume (App, JIS-NUC work tree, Sonnet 5.5). Operator ask: research what "volume cannot be hidden" gives MTS for mid/long-term directional BTC trades, combined with
candles, consolidation patterns, Bollinger Bands, RSI 40/60 and exhaustion volume; then, mid-session: "also combine time analysis". Method: MTS protocol (pre-register, DEV / VALIDATION / sealed HOLDOUT, 14 bp costs + funding,
White Reality-Check, placebo calibration). Everything is reproducible from this folder; the registry holds every trial.

## 0. Bottom line

1. **No volume rule we tested is a validated directional edge on BTC.** 553 pre-registered trials (event studies, state variables, contrasts, time hypotheses; DEV first, VALIDATION for survivors) produced 1 marginal pass
   and 0 usable survivors: that one failed VALIDATION (net -2 bp on 50 events vs +70 bp on DEV). Two further DEV-supported ideas (a time-of-day contrast and a pooled "volume confirms breakouts" premium, which looked very strong on DEV, p = 0.008)
   both failed VALIDATION. HOLDOUT (2025-07 .. 2026-09) was never opened and is still sealed.
2. **Volume is not hidden, but what it reveals is intensity, not direction.** Robust, high-n facts: volume is persistent (lag-1 autocorrelation 0.67), strongly tied to the size of the move (corr 0.42-0.49), forecasts the NEXT bar's range
   (a 2-3x day is followed by a bar with 1.25-1.40x its normal range) but not its direction (corr with next-bar return 0.01-0.04). Buy/sell (taker) delta explains the bar that just printed (corr 0.53) and says nothing about the next one (0.01-0.03).
3. **Time matters a great deal, and plain relative volume is biased by it.** BTC volume has a 2x intraday rhythm (peak 13-16 UTC, trough 03-05 UTC) and weekends run at 0.62-0.72x. With a plain 20-bar baseline, 36% of 12-16 UTC 4h bars look like "2x volume spikes"
   vs 6% of 04-08 UTC bars; a same-slot baseline makes both about 11%. Any MTS volume flag without a time baseline is partly a clock.
4. **MTS actionable, in order:** (a) use volume for risk and volatility timing (feeds T070), not for entries; (b) fix the time bias of the existing volume-spike proof P06 and keep it labelled NO-SOURCE; (c) add a read-only, time-adjusted
   volume context to the market guide; (d) do not build volume/CVD/OBV divergence, climax, or volume-confirmation entry rules; (e) the next honest test of exhaustion/absorption needs 1m/aggTrades data (T071), because at 4h and 1d those events occur only 20-80 times in 4.5 years.

"No edge found" has limits (section 6): with 50-300 events, only effects larger than roughly 60-170 bp (4h, n about 200, 1 to 7 day holds) or 100-550 bp (daily, n 50-200) are detectable. Small effects are not excluded; they are also too small to trade after 14 bp costs and funding with any confidence.

## 1. How the goal was refined during the session

| step | what happened | change |
|---|---|---|
| start | Read STATUS, LESSONS, prior research. Repo priors: 0/108 candle patterns, RSI 40/60, Fabio volume/CVD layers, funding+CVD divergence all NO-EDGE | Goal reframed from "find profitable volume strategies" to "test them with pre-registration and report honestly, null included" |
| data | This machine had no price archive | Asked, then downloaded BTCUSDT USD-M 1d + 1h klines (with taker-buy volume) and funding, 2020-01..2026-09, SHA256-verified, 8 MB, gitignored |
| literature | Searched volume-return, Wyckoff/VSA, BB squeeze, taker flow, intraday seasonality | Fixed the family list (36 events) and the time-adjusted volume measure |
| operator add | "Combine time analysis" | Made time-adjusted relative volume (RVadj) the core definition; added T0 time map, TH1-TH3, session split, weekend contrast |
| after V1 | Daily bars underpowered (120 of 216 trials had too few events) | Pre-registered a state family (V2) that exists on every bar, incl. US-hours vs Asia-hours buying |
| after V3 | Both survivors failed VALIDATION | One last registered pooled test of the operator's own question (does volume confirm breakouts?), V4; failed too |
| stop | More searching would be forking paths | Wrote the report; remaining ideas are listed as NEW registrations (section 5) |

## 2. What the literature says (ranks what to test; our own data decides)

Tiers: T1 peer-reviewed, T2 working paper or preprint, T3 practitioner. Most pages were opened as abstracts or summaries only; none of the numbers below was re-derived by us except where stated.

| source | tier | claim | what we found |
|---|---|---|---|
| [Balcilar, Bouri, Gupta, Roubaud 2017](https://repository.up.ac.za/handle/2263/60028) | T1 | BTC volume predicts returns except in strong bull/bear regimes (2011-2016); not volatility | We find the opposite split: no return predictability, but a next-bar range link (descriptive, 2020-2024) |
| [Karpoff 1987](https://ideas.repec.org/a/cup/jfinqa/v22y1987i01p109-126_01.html) | T1 | Volume rises with the size of price moves | Confirmed: corr(ln v, abs ret) 0.42 (1d), 0.49 (4h) |
| [Gervais, Kaniel, Mingelgrin](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2014/04/9901.pdf) | T1 | Stocks with a volume shock out/under-perform over the next month (visibility) | Not shown on BTC: 20-day volume trend and delta states, V2, no pass |
| [Llorente, Michaely, Saar, Wang 2002](https://img.nber.org/papers/w8312) | T1 | Volume with speculative trading means continuation, hedging means reversal | Untested directly; our spike continuation vs reversal trials: neither passes |
| [Baur et al. 2019 (time-of-day, day-of-week)](https://research-repository.uwa.edu.au/en/publications/bitcoin-time-of-day-day-of-week-and-month-of-year-effects-in-retu/) | T1 | Volume/volatility have clear intraday and weekday shapes; returns show no persistent calendar pattern | Confirmed for volume (our time map); our time-conditioned return hypothesis TH1 did not replicate |
| [Quantpedia on BTC calendar effects](https://quantpedia.com/are-there-any-simple-calendar-effects-in-bitcoin-market/) | T3 | Weak returns around 03-04 UTC; a 21-23 UTC rule at about 33% a year | Blog backtest, no costs or OOS; not tested, volume is lowest at 03-05 UTC |
| [Zarattini, Pagani, Barbon 2025 (Donchian trend, BTC and alts)](https://abarbon.com/papers/catching-crypto-trends) | T2 | Multi-lookback Donchian trend with vol sizing; volume enters only as a liquidity screen for altcoins | Supports using volume for universe/size, not as a signal |
| [Taker-imbalance mean-reversion preprint (arXiv 2608.21888)](https://arxiv.org/pdf/2608.21888) | T2 | After flow-driven bars price tends to revert; walk-forward AUC 0.540 vs 0.519 | Tiny effect, unreviewed; our DBUY/DSELL trials show no pass |
| [Climactic action / stopping volume (LuxAlgo)](https://www.luxalgo.com/library/concept/climactic-action.md), TradingView scripts | T3 | Wyckoff/VSA: effort without result at an extreme marks buying/selling climax | No out-of-sample test found anywhere; ours cannot reach the sample size (section 4.3) |
| Repo: T5_CVD_DEFINITION_2026-10-01.md, 102 trader transcripts | internal | Traders name absorption, exhaustion, cumulative delta, volume profile; give no numeric rule. "Volume cannot be hidden" is not in the corpus | Every threshold here is engineering/literature, tagged NO-SOURCE-TRADER |

## 3. What was tested (full definitions: PRE_REG_VOLUME_2026-10-09.md and addenda A, B)

Data: BTCUSDT USD-M perpetual, Binance archive. DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30 (touched only by 4 frozen tests); HOLDOUT 2025-07-01..2026-09-30 sealed by a code guard (the loader refuses it without an explicit unseal flag).
Costs: 14 bp round trip plus realised funding. Entry next bar open. Timeframes: 1d and 4h (weekly bars: about 230 in DEV, no power, not tested).

| family | content | trials |
|---|---|---|
| V1 events | 36 events x 3 horizons x 2 orientations x 2 timeframes. Volume spike (2x/3x), buying/selling climax and breakaway, absorption (high volume, small range), no-demand/no-supply (new high on low volume), taker-delta spike, CVD divergence, OBV divergence, Bollinger squeeze breakout with/without volume, Donchian-20 breakout with/without volume, squeeze with dry-up volume, RSI(14) 40/60 crosses with/without volume | 432 |
| V1 contrasts | does volume confirmation add anything (6 pairs), plain vs time-adjusted volume, weekend vs weekday, session A/B/C | 18 |
| V2 states | 20-day taker-delta share, volume trend, momentum (control), US-hours and Asia-hours delta, each x top/bottom third of its own trailing-year rank, plus RSI 40/60 regime x delta | 96 + 3 contrasts |
| V3 validation | the one V1 pass and the one supported time hypothesis | 2 |
| V4 pooled | volume-confirmation premium pooled over the 6 pairs, 4h and 1d | 2 |
| total | | **553 edge trials** (60 placebo runs counted separately) |

Key measure: **RVadj** = volume / median of the same 4h slot over the previous 20 days (daily: same weekday, 8 weeks). Taker delta share DP = (2 x taker-buy - volume) / volume.
Statistics: White Reality-Check across each family (both continuation and reversal), circular block bootstrap, net of costs, minimum-detectable-effect printed beside every result.
Quality: 40 unit tests (hand-derived expectations, RSI from FORMULAS.md, no-look-ahead tests, sealed-holdout test), 24 mutants of the code all caught, 20 placebo runs per family with volume circularly shifted (8 of 60 hit at the nominal 10% level, 13%: calibrated).

## 4. Results

### 4.1 What volume does tell you (DEV, high n, descriptive; V0_RESULTS.md)

| fact | numbers |
|---|---|
| Volume level drifts, so use relative volume | median daily volume: 2020 239k BTC, 2021 336k, 2022 427k, 2023 351k, 2024H1 249k |
| Volume is persistent | autocorrelation of ln volume: lag 1 = 0.67, lag 5 = 0.41 (1d) / 0.51 (4h) |
| Volume rises with move size | corr(ln v, abs ret) 0.42 (1d), 0.49 (4h); corr(RVadj, range / ATR) 0.54 / 0.66 |
| Volume forecasts the NEXT bar's range, not direction | next-bar range as a multiple of normal after RVadj < 0.7 / 0.7-1.3 / 1.3-2 / 2-3 / >= 3: 1d 1.00 / 1.01 / 1.10 / 1.40 / 1.22; 4h 0.94 / 1.01 / 1.13 / 1.25 / 1.34. corr(RVadj, next return) 0.04 (1d), 0.01 (4h) |
| Buy/sell delta describes the bar, not the future | corr(taker delta share, same-bar return) 0.53 on both timeframes; with next-bar return 0.027 (1d), 0.009 (4h) |
| Spikes are not rare enough to be "events" on 4h | RVadj >= 2 in 12.5% of 4h bars, >= 3 in 4.7%; daily 7.2% and 2.1% |
| Taker buy share hardly moves | mean 0.496-0.501 per year, daily range 0.447-0.566: there is no persistent buy or sell side in perp taker flow |

### 4.2 Directional tests (DEV, then VALIDATION)

Verdict legend: NO-EDGE = tested with enough events and failed; INSUFFICIENT = too few events for the registered test, descriptive numbers only; NOT SUPPORTED = failed VALIDATION.

| concept (operator list) | what was tested | result |
|---|---|---|
| Volume spike, up or down bar | SP2/SP3 x 3 horizons x follow/fade | 1d and 4h: no pass. Best: 4h SP3 up, 7-day hold, +247 bp excess, adjusted p = 0.37 |
| Exhaustion: buying/selling climax | spike at a 20-bar extreme closing off the extreme (BCLX/SCLX) | **INSUFFICIENT**: 82 and 68 events in 4.5 years at 4h, 5 and 6 daily. Descriptive: BCLX followed by +141 bp after 3 days [+12, +259] vs all bars +36; SCLX no signal. Not evidence |
| Breakaway (spike, closes at the extreme) | BAWAY up/down | 4h no pass (best +192 bp at 7 days, p = 0.58); daily INSUFFICIENT |
| Absorption / effort-vs-result | high volume, small range, in a trend | **INSUFFICIENT** (36-41 events at 4h). Descriptive only; belongs in T071 at 1m |
| No-demand / no-supply | new 20-bar high on low volume (and mirror) | **INSUFFICIENT** (55, 23 events at 4h) |
| Buy/sell volume | taker-delta z >= 2 on an up bar, <= -2 on a down bar | no pass on either timeframe |
| CVD / OBV price-divergence | 20-bar divergence, FORMULAS.md section 14 definition | no pass. Matches the earlier NO-EDGE of funding_cvd_fade |
| Consolidation + breakout + volume | Bollinger squeeze (width in lowest 20% of 120 bars) then close outside the band, confirmed vs unconfirmed; Donchian-20 the same; squeeze with volume dry-up | no pass. Volume-confirmed minus unconfirmed (6 pairs): DEV positive in 6/6 daily and 5/6 at 4h, none individually supported (smallest q = 0.19) |
| RSI 40/60 + volume | RSI(14) crosses 60 up / 40 down, confirmed or not, 40-reclaim, 60-rejection | one 4h trial passed DEV (RSI crosses below 40 on UNconfirmed volume, buy for 1 day, +70 bp net [+24, +121], RC p = 0.081); **failed VALIDATION: n = 50, net -2 bp [-68, +64]** |
| Volume as a state (mid/long term) | 20-day taker delta, 20-day volume trend, US-hours / Asia-hours delta, each top/bottom third, 5-20 day holds, plus RSI-regime interaction | no pass among 84 testable trials. Closest: RSI >= 60 and high delta, 10-day follow, +381 bp net [+29, +629] but adjusted p = 0.28 |
| Does buy-volume confirm momentum? | K1/K2 contrasts | not supported (K1 +141 bp, CI [-371, +614]) |
| Pooled "volume confirms breakouts" | six pairs pooled (V4) | DEV 4h +88 bp [+15, +155] p = 0.008; **VALIDATION -13 bp [-109, +81], p = 0.60, 3/6 pairs positive; 1d +123 bp, p = 0.34. NOT SUPPORTED**, HOLDOUT stays sealed |

Why the pooled result is a lesson, not a near miss: it was found by looking at DEV (hence its apparent p = 0.008), and it halved to nothing the first time it met unseen data. This is the textbook selection effect and the reason MTS pre-registers.

### 4.3 Time analysis (operator addition)

| question | answer |
|---|---|
| When is BTC volume? | Share of the day's volume per UTC hour (flat = 4.2%): 03-05 UTC 2.4-2.5%; 12-16 UTC 4.4-5.5% (peak 14 UTC 5.5%); a US-open step is visible, 13 UTC = 5.3% in Apr-Oct vs 4.5% in Nov-Mar (DST) |
| Weekends | Saturday volume 0.62x and Sunday 0.72x the all-day median; Saturday median abs daily return 0.76% vs 1.5-1.9% Mon-Fri. Weekend 4h RVadj >= 3 happens in 1.8% of bars vs 5.9% on weekdays (the 4h baseline mixes weekdays, so weekend spikes look rarer than they are: a limit) |
| Does the clock bias a volume flag? | Yes. Plain 20-bar RV >= 2: 36.1% of 12-16 UTC 4h bars, 21.3% of 16-20, 6.2% of 04-08. Same-slot RVadj >= 2: 10.9%, 15.1%, 11.2%. A 1-hour analog of the existing P06 proxy (volume >= 2x mean of the previous 4 hours): 21% of 13-14 UTC hours, 4% of 04 UTC hours and 6-7% of 17-21 UTC hours |
| Does it change returns? | Registered contrasts: plain vs time-adjusted spikes (C7): no difference at 4h (-24 bp, CI [-68, +18]); spike continuation by session (TH1) was supported on DEV (session C minus A -178 bp) and **reversed on VALIDATION (+126 bp)**; weekend vs weekday spikes (TH2) not supported; BB-squeeze volume breakout by session (TH3) +2 bp. Taker delta in US hours vs Asia hours (K3): +186 bp, CI [-85, +471], not supported |
| Summary | Time structure is real for volume and volatility. No time-conditioned directional rule survived |

### 4.4 Why not more

Power (naive i.i.d. figures, 80% power, one-sided 5%): at 4h with n = 200 the minimum detectable excess is 61 bp for a 1-day hold, 104 bp for 3 days, 164 bp for 7 days (n = 50: 122 / 208 / 327 bp); on daily bars with n = 50 it is 195 / 373 / 550 bp for 3 / 10 / 20 day holds (n = 200: 98 / 187 / 275 bp). Effects below that are invisible in 4.5 years of one asset
and venue. The pooled V4 test had a validation minimum detectable effect of about 130 bp (from its bootstrap standard error of about 48 bp), against a DEV estimate of 88 bp: it had roughly a 45% chance of confirming an effect that size, so "not supported" means "not shown", not "proved zero". HOLDOUT (about 15 months, standard error near 68 bp) would give roughly a 1-in-4 chance even if the DEV estimate were true, and that estimate is probably inflated, so we did not spend it.

## 5. How MTS should use this

Provenance rule applies: nothing here comes from a trader's words, so everything below is a separate observation layer or a research item, never a Tom/Fabio filter or proof.

| # | actionable | evidence | tier / owner | acceptance | status |
|---|---|---|---|---|---|
| A1 | **Add `volume_context` to the market guide (observation only):** latest 4h and 1d RVadj with the same-slot baseline, spike/dry label (>= 2, <= 0.8), taker delta share and its z-score, weekend/Asia/US flag, and the empirical next-bar range multiplier for that RVadj bucket. Print "descriptive, not a signal" and the verdict tag NO-EDGE (direction) | 4.1, 4.3 | T2 Sonnet, S (spec: items/T072) | Hand-derived tests for RVadj, DP, slot keys (reuse test_volume.py cases); guide prints it; no execution import | specified, not built |
| A2 | **Volatility timing from volume (T070):** use RVadj, hour-of-day volume share and weekday as forecast features for the next-bar range; test whether volatility-scaled stops lift Tom/Fabio net R. Pre-register the estimator first | next-bar range 1.25-1.40x after a 2-3x bar; volume persistence 0.67 | T2 Sonnet, M (existing item T070, evidence appended) | Pre-registered, read-only, improve/degrade/no change reported | queued |
| A3 | **P06 volume-spike proof:** it uses "last 1m volume > 2.0x mean of 240 bars, close within 0.1%" (SetupCandidatesBuilder.java:804-816, T5_CVD_DEFINITION). The 4-hour baseline makes it fire about 3-5x more often at 13-14 UTC than at 04 UTC or 17-21 UTC (1h analog above). Keep it NO-SOURCE; if it stays in the proof count, give it a same-slot baseline. Live Java: supervisor deploy window only | 4.3 | T3 Opus supervisor (items/T073) | Proof frequency by hour reported before and after (target: flat across the day); B063 note updated: no CVD divergence rule has edge | specified |
| A4 | **Do not build** volume/CVD/OBV divergence entries, climax or breakaway entries, volume-confirmed breakout filters, RSI 40/60 + volume entries, delta-state or US/Asia-delta entries. Recorded as NO-EDGE in market_guide_verdicts.json | 4.2 | done | verdict row present, guide test green | done |
| A5 | **Exhaustion and absorption need intraday data:** at 4h they occur 20-80 times in 4.5 years. Test them where order flow lives (1m klines, aggTrades) under T071 with a registered threshold set; the descriptive appendix in V4_RESULTS.md gives the first hypotheses (BCLX 3-day +141 bp [+12, +259], ABS_HIGH 7-day +462 bp [+139, +812]) which are NOT evidence | 4.2 appendix | T3 Opus plan, then Sonnet; needs operator OK for 1m/aggTrades download (about 0.25-0.4 GB for 1m 2022+, aggTrades 0.1-0.3 GB per day) | New pre-registration with its own trial rows | open |
| A6 | **Multi-asset replication of the one open question** ("does volume confirm breakouts?"): same 6 pairs on ETH and SOL perps, 2020-2025 (about 3x the events). Register first, run once on VALIDATION. Needs a small download (about 10 MB per asset); operator approval | V4 | T2 Sonnet, M | VCP > 0 with p < 0.025 on VALIDATION in the pooled-assets test | proposed |
| A7 | **Keep HOLDOUT sealed** for a properly powered hypothesis (A5/A6). Spending it on V4 would give roughly a 1-in-4 chance of detecting even the DEV-sized effect (section 4.4) | 4.4 | operator decision | HOLDOUT opened once, by a registered rule | open |

## 6. Limits and corrections to read before trusting anything above

- One venue, one product: Binance USD-M BTC perpetual taker volume. "Volume cannot be hidden" is true of the whole market only if one venue represents it; wash trading and cross-venue flow are not controlled. Multi-venue CVD is agenda item P8.
- One regime history: 2020-mid 2025 (one full cycle). Spot-ETF era (Jan 2024 onward) is in DEV's last six months and VALIDATION; no pre/post split was registered.
- The daily test is underpowered (120 of 216 trials had too few events). Absence of a pass there says little. The 4h test is better but still limited to effects of roughly 60+ bp.
- RVadj at 4h uses the previous 20 days of the same slot, which mixes weekdays and weekends; weekend spikes are therefore under-flagged and TH2 is confounded. A weekday-and-slot baseline would be a new registration.
- The US cash-open DST shift (13:30 vs 14:30 UTC) is not modelled inside the 4h slots; the hour table shows it (13 UTC share 5.3% summer vs 4.5% winter).
- Taker delta here is per bar from kline taker-buy volume, not tick-level order flow; footprint and absorption in the traders' sense need aggTrades.
- Implementation choices not in the original pre-registration text (logged in addendum A and in code docstrings): funding charged on settlements in (entry, exit]; warm-up of 150 bars; V1 DEV ran 3 times and V2 twice (crashes before any outcome, one group-mean column added, one placebo lag draw fixed, all outcomes unchanged); the V2 placebo hit rate was 4/20 (the boundary of the miscalibration rule).
- One data anomaly: 2023-08-16, 1h volume sums differ from the 1d archive by 3.1% (all other 1,642 DEV days agree exactly). The daily test uses the 1d file; effect negligible.
- Literature rows come from abstract-level reads through web search; none was verified against full text.

## 7. Reproduce

```
python MyTradingSys/research/volume_2026-10-09/test_volume.py     # 31 tests
python MyTradingSys/research/volume_2026-10-09/test_state.py      # 9 tests
python MyTradingSys/research/volume_2026-10-09/mutation_check.py  # 24 mutants, 0 survivors
python MyTradingSys/research/volume_2026-10-09/run_v0.py          # V0_RESULTS.md
python MyTradingSys/research/volume_2026-10-09/run_v1.py          # V1_DEV_RESULTS.md
python MyTradingSys/research/volume_2026-10-09/run_v2.py          # V2_DEV_RESULTS.md
python MyTradingSys/research/volume_2026-10-09/run_v3.py          # V3_VALIDATION_RESULTS.md (one-shot; rerunning is not a new validation)
python MyTradingSys/research/volume_2026-10-09/run_v4.py          # V4_RESULTS.md
```
Needs the archive under Dumps/backtest (raw_1d, raw_1h, raw_fund): `python MyTradingSys/backtest/fetch_binance_archive.py --start 2020-01-01 --end 2026-09-30 --datasets klines --interval 1d --out Dumps/backtest/raw_1d` (and `--interval 1h --out Dumps/backtest/raw_1h`, `--datasets fundingRate --out Dumps/backtest/raw_fund`).
Commit order is the proof: ec18096 (pre-registration) < 81c0b10 (V1) < 6e6227b (addendum A) < e0e3a2e (V2) < f69f01c (V3 + addendum B) < d7ff23f (V4).
