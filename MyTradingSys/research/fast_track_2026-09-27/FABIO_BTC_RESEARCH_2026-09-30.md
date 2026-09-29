# Fabio on BTC + BTC indicator evidence + audit of our Fabio backtests (supervisor, 2026-09-30)

Done under playbook Part I (methodology/playbook.md). Web research done personally; every cited source below was opened and
matched (title / authors / venue / year) on 2026-09-30 unless marked otherwise. Tags: `Tier | Method quality | Confidence`.
Nothing here is a backtest result. External evidence only ranks what to test first (Part I 3e).

## 0. Method note (Step 1)
- Q1 "What does Fabio say about BTC / do BTC professionals use his lens?" - settled only by his own words (T3) and by our own OOS
  test. No academic method can settle "does Fabio's model port"; so Q1 = ideas + our backtest.
- Q2 "Which BTC indicators have evidence?" - settled by peer-reviewed / working-paper studies with disclosed data, out-of-sample or
  data-snooping control, and costs. Horizon matters more than indicator (see 3).
- Adoption for anything: our own OOS backtest, Deribit costs, PBO, n large enough (section 4).

## 1. What Fabio says about BTC
**No validated evidence found.** The eight Fabio transcripts we hold locally (0jM5Y31YJak, 8CWKfoSJu3c, 0KyIEdvVKMQ, fZlNGWvd2Ko, LQvv5xgy_ik,
FawPrRUGNpk, jasv3L-d8ZE, o-w5Gxss6T0 was not on disk; StaphlRH8NQ is another trader and also has none) contain zero occurrences of bitcoin / btc / crypto / binance
(grep, whole files, 2026-09-30). Public pages agree, all say Nasdaq futures, New York session:
- Chart Academy instructor page: "futures, mostly the Nasdaq, during the New York session"; top-3 Robbins World Cup futures
  scalping, audited >500% in a year. T3 (vendor bio) | no method | M.
- TradeZella "Auction Market Theory + LVN Playbook by Fabio": futures only (NQ, ES), no crypto. Targets 1:2.5-1:5, stops just
  beyond aggressive prints, no win rate, no audited results on the page. T3 | no OOS | L.
- Podcast transcript (pickscribe, "I Traded with the World #1 Scalper"): NASDAQ only; A/B/C-setup risk tiers; avoids European
  afternoon ("wait for the 3:30 shake out"); stop at "the level holding the aggression of the sellers". T3 | M.
Consequence: nobody has shown his model on BTC, and he never claims it. The user's instinct is right in one way: absence of a
BTC claim is not evidence against, it is just untested. Our tests (below) also do not prove it fails.

**The lens we missed.** His public playbook has two models, not the one we simulated:
1. Trend model: market out of balance, wait for a PULLBACK into a low-volume node (LVN) of the impulse leg, enter on
   aggression confirmation (big prints / CVD), stop beyond the aggressive prints.
2. Mean-reversion model: failed breakout that reclaims back into balance (London / compressed conditions).
We tested "break of prior-session VAH/VAL/POC/LVN then retest" and "absorption fade at those levels". That is not the LVN
pullback, and the levels came from an 8h UTC block profile, not a session with a closing auction.

## 2. Audit of how we tested Fabio (findings, most important first)
Files: `backtest/layers/fabio/fabio_of_model.py`, `run_of_model.py`, `run_of_model_v2.py`, `FABIO_OF_REPORT.md`.
1. **Underpowered, so "no edge" is really "untested".** OOS = 28 days, n = 9-90 per cell; the 95% CI on expectancy at n = 30 with
   R-SD ~1.5 is about +/-0.55R. To resolve a +0.2R edge you need roughly 650 trades, +0.1R roughly 2,600. The report itself
   says one regime, 90 days. Do not quote its verdicts as evidence against Fabio-on-BTC.
2. **The committed report's fees are not the fees the code now uses.** Report text: taker 0.05%/side, maker 0.02% (0.10% RT).
   `fabio_of_model.py` header and constants: Deribit taker 3.5 bps, maker -1.5 bps. results.json/tables.md were written
   02:42 IST (old fees); the Deribit code landed 03:18 in WIP commit 5831ead and run_of_model_v2 has no results yet. So the
   headline "fees eat 0.66R" is Binance-taker fees, NOT our live venue. Re-run before any conclusion.
3. **Limit-entry fills are adversely selected.** Fade limit is placed AFTER the trigger bar has closed back away from the level and
   fills only if price returns through it (`simulate_trade`, entry_mode == "limit"). Fills therefore happen mostly when the
   absorption failed. Real Fabio rests the order before the touch. The limit variants are biased pessimistic; a causal fix is a
   resting order armed on approach (pre-trigger) with fill-through, plus reporting missed winners.
4. **Management is not his management.** Target = min(3R, nearest HVN/POC) caps winners; no pyramiding; trail is 1R after 2R,
   not behind order-flow levels; no S8 exit; no day selection (volatile/directional only) and no daily stop. FABIO_TRADE_MODEL.md
   already says the edge is in exactly these; the simulator cuts them.
5. **Signal stack is a chain of ANDs.** delta >= k x mean AND >= 2 big prints AND extreme within 0.1% AND close back on side. Each AND
   shrinks n (that is why n = 16-90); 64 grid variants on top raises multiple-testing cost with too little data.
6. **Levels are a poor proxy.** 10 USD bins on a ~100k asset (~0.01%) make LVN minima noise; profile comes from the prior 8h UTC block
   (Asia/London/NY). BTC has no closing auction, so "prior session value" has no institutional meaning. Fabio's LVNs come from the
   impulse-leg / multi-day composite profile.
7. **Venue mismatch.** Flow is Binance USD-M aggTrades only; his order flow is CME (Nasdaq). BTC volume is split across Binance, Bybit,
   OKX, Coinbase, CME (ETF-linked). aggTrades also merges same-price fills, so "big print" != one order. Kim-Hansen (below)
   shows periodic algorithmic round-size trading at quarter-hours, another contaminant of the "big trade" idea.
8. **Sound parts (keep):** causal state (first 15m), prior-30d percentile thresholds, worst-case stop-before-target in a bar,
   PBO on IS daily R, IS-frozen choice. The cross-check of kline delta vs aggTrades (94% identical) is good.
9. **More data now exists.** `F:\MTS\data\orderflow_1m` has 676 day files (from 2024-12-02). The 90-day limit no longer binds.

## 3. Evidence for BTC (opened + matched)
All external evidence below is DAILY-to-multi-hour, not tight-stop scalping. Micro-signals exist but are below fees.

| # | Source (verified) | Finding | Tag |
|---|---|---|---|
| E1 | Gerritsen, Bouri, Ramezanifar, Roubaud (2020), "The profitability of technical trading rules in the Bitcoin market", Finance Research Letters 34 (ideas.repec.org/a/eee/finlet/v34y2020ics1544612319303770.html; abstract only) | 7 trend indicators, daily BTC Jul-2010..Jan-2019; trading-range breakout beats buy-and-hold on bootstrapped Sharpe, best in strongly trending markets | T1 \| bootstrap, daily, costs not stated in abstract \| M |
| E2 | Detzel, Liu, Strauss, Zhou, Zhu (2021), "Learning and predictability via technical analysis: Evidence from bitcoin and stocks with hard-to-value fundamentals", Financial Management 50(1):107-137 (ideas.repec.org, abstract only) | price / moving-average ratios forecast daily BTC returns in and out of sample; alpha and Sharpe gain vs buy-and-hold | T1 \| OOS yes, costs not in abstract \| M |
| E3 | Zarattini, Pagani, Barbon (2025), "Catching Crypto Trends", Swiss Finance Institute Research Paper 25-80 (ideas.repec.org/p/chf/rpseri/rp2580.html, abstract only) | ensemble of Donchian-channel trend models + vol sizing; top-20 rotational portfolio net of fees Sharpe > 1.5, alpha 10.8% vs BTC | T2 \| net of fees, survivorship-free universe, mostly a portfolio not BTC alone \| M |
| E4 | Shen, Urquhart, Wang (2022), "Bitcoin intraday time series momentum", Financial Review (research.birmingham.ac.uk, abstract only; sample and costs not on page) | first half-hour (volume-time) return predicts last half-hour; strongest in high-volume / high-vol sessions | T1 \| costs unknown \| L-M |
| E5 | Cao, Zhai, Luo (2024), "Anatomy of cryptocurrency perpetual futures returns", Journal of Futures Markets (research.ed.ac.uk, abstract only) | 134 predictors, 48 significant; basis + price-volume two-factor model explains all | T1 \| breadth test, data-snooping unclear \| M |
| E6 | Kim, Hansen (2026), "The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency Futures", arXiv 2607.09426 v2 | Binance perps 2021-2024: opening 10s returns OOS R2 1.2-5.8%; quarter-hour opening order imbalance predicts 4-12h returns. But predictable part ~0.5 bp per boundary, ~1/10 of taker fee | T2 \| LASSO rolling OOS, costs discussed \| M |
| E7 | Kitron, Wengrowicz (2026), "Short-horizon mean reversion in cryptocurrency markets", arXiv 2608.21888 | 15m directional reversal significant in 90% of 183 Binance pairs, but gross edge ~1.3 bp vs 5 bp round trip | T2 \| permutation + 6-month holdout \| M |
| E8 | Concretum, "Seasonality in Bitcoin Intraday Trend Trading" (concretumgroup.com) | ensemble intraday trend gross Sharpe ~1.6 (2018-2025), best from Sunday ~19:00 NY (Asia open), stronger after mid-2020; no net-of-fee / OOS statement on page | T3 \| gross, no OOS shown \| L |

Reading across E1-E8: BTC trend / breakout / momentum on multi-hour to daily horizons has repeated support; order-flow imbalance
carries information for 4-12h direction; anything faster (10s-15m) is real but smaller than fees. That tells us the lens
problem is horizon, not the signal: Fabio's tight-stop 5-15m execution may not be feasible on BTC at Deribit costs unless the
stop is wide enough (0.3-0.5%) and the entry is maker. The order flow signal (S2 pressure in balance) is better tested as a
4-12h directional predictor (E6 style) than as a scalp trigger.

## 4. What to test next (all need our OOS backtest; ranked by evidence, then cost to build)
Objective is expectancy after Deribit fees + funding + slippage with PBO, not hit rate. Trend/breakout systems
win ~35-45% and that is normal; a "max hit rate" objective would select small-win/large-loss rules.
A. **Donchian / trading-range-breakout ensemble + vol sizing** (E1, E3), daily and 4h, BTC-PERPETUAL, Deribit costs + funding.
   Cheapest (klines only), best evidence. Baseline for everything else.
B. **Price / MA ratio and momentum** at daily/4h (E2, E4). Also intraday TSMOM by volume-time (E4), 30-60 min blocks.
C. **Order-flow pressure as a 4-12h direction predictor**: normalized CVD slope inside a balance (S2) and quarter-hour opening
   imbalance (E6) on the 676-day F: bars. Event study first: does it predict signed 4-12h return net of costs? If not, stop.
D. **Basis / funding + price-volume factor** (E5) as a directional filter on A (positioning layer, separate from Tom).
E. **Fabio v3 (only after C):** LVN-pullback trend model + failed-breakout-reclaim mean reversion, impulse-leg / RTH-composite
   profile (CME RTH 13:30-20:00 UTC as the "session"), maker resting entries armed pre-touch, runners with pyramiding and
   order-flow-level trail, min stop 0.3-0.5%, all 676 days, report trend vs balance days and NY separately.
F. Time-of-week seasonality (E8) as a conditioning variable, tested with our own data, not adopted from the blog.
Sample-size rule for every item: fix the number of trials first (TRIAL_REGISTRY.csv), require enough OOS trades to
resolve the effect size (n ~650+ for 0.2R), IS/OOS split by regime not only by month (2024-12..2026-09 contains several regimes).

## 5. Discarded (Part I 3c; do not research again)
- TradingView scripts, PickMyTrade blog, Scribd "Fabio Playbook", TikTok clips, LinkedIn bio, coconote landing page,
  fabervaale.com landing page: marketing / no method / no costs. REJECT.
- ScienceDirect "Order flow and cryptocurrency returns" (pii S1386418126000029) and its EFMA 2025 working-paper PDF: could not open
  (403; PDF unparsable here), so unverifiable. REJECT until opened. It is the best candidate to verify by hand for item C.
- Hudson & Urquhart (2021), "Technical trading and cryptocurrencies", Annals of Operations Research 297:191-220: bibliographic data
  matched in search listings, but I could not open the abstract page (host unreachable / 403). Not relied on. Verify before use;
  it would support E1 (breakeven costs vs crypto costs) if the abstract says what the secondary summaries say.
- arXiv/Preprints.org ML papers claiming 86-92% signal "accuracy" or LSTM returns with no costs; TradingView/investing.com/
  Kraken/altindex indicator pages; Bitget/CryptoRank/CoinDesk CVD news pieces; Glassnode/Amberdata blogs. No method or
  cost-adjusted OOS; REJECT.
- Practitioner order-flow BTC pages (markettrace.ai, traderprofesional.com, pearloftrades, tholvitrader): T3 definitions of
  absorption / LVN only; contain no test. Used for vocabulary only.
