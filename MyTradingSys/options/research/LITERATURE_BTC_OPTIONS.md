# LITERATURE: BTC options profitability, hedging, Deribit mechanics
Session 2026-10-09 | external literature worker | Playbook Part I applied (tiers, citation check, "verified 2026-10-09").
Role of this file: ranks WHAT TO TEST FIRST. Nothing below is a validated edge; adoption needs our own backtest
(OPTIONS_PLAN Question A / B). Tag format: `Tier | method (OOS? costs? sample) | confidence H/M/L`.

## 0. Method note (fixed before searching)
Q1/Q3 settled by: peer-reviewed or disclosed-method study on Deribit options, out-of-sample (OOS), net of fees + spread,
>= 1 vol cycle incl. 2020-03 / 2021-05 / 2022-11 shocks. Q2: study of premium carry vs tail saved on a BTC long.
Q4: exchange documentation (T2). Outcome: NO source meets the full bar for Q1-Q3. Every "profit" below is gross-of-something
or in-sample; verdicts are "hypothesis to test", not "edge". "abstract only" = claim taken from the abstract.

## 1. Verified source register (all opened 2026-10-09; URL = what was opened)
S1  Almeida, Grith, Miftachov, Wang, "Risk Premia in the Bitcoin Market", arXiv:2410.15195 v2 (1 Aug 2025). T2.
    https://arxiv.org/abs/2410.15195  (full text https://arxiv.org/html/2410.15195v2). Preprint, not journal.
S2  Lucic & Sepp, "Valuation and hedging of cryptocurrency inverse options", Quantitative Finance 24(7):851-869, 2024,
    DOI 10.1080/14697688.2024.2364804. T1, abstract only (publisher + SSRN pages blocked by bot challenge; not bypassed).
    https://ideas.repec.org/a/taf/quantf/v24y2024i7p851-869.html
S3  Alexander & Imeraj, "Delta hedging bitcoin options with a smile", Quant. Finance 23(5):799-817, 2023,
    DOI 10.1080/14697688.2023.2181205. T1, abstract only. https://ideas.repec.org/a/taf/quantf/v23y2023i5p799-817.html
S4  Hoang & Baur, "Forecasting bitcoin volatility: Evidence from the options market", J. Futures Markets 40(10):1584-1602,
    2020, DOI 10.1002/fut.22144. T1, abstract only. https://ideas.repec.org/a/wly/jfutmk/v40y2020i10p1584-1602.html
S5  Chi & Hao, "A Horserace of Volatility Models for Cryptocurrency: Evidence from Bitcoin Spot and Option Markets",
    arXiv:2010.07402 (Sep/Oct 2020), FULL TEXT read (T2). https://arxiv.org/abs/2010.07402 ; published as "Volatility models
    for cryptocurrencies and applications in the options market", J. Int. Fin. Markets, Inst. & Money 75, 2021,
    DOI 10.1016/j.intfin.2021.101421 (T1, abstract only) https://ideas.repec.org/a/eee/intfin/v75y2021ics1042443121001359.html
S6  Kumar, "Deep Hedging Under Realistic Market Frictions: ... Dynamic Option Hedging on Bitcoin Options", arXiv:2608.29025
    (29 Aug 2026). T2, abstract only, single author, ~6 weeks old, unreplicated. https://arxiv.org/abs/2608.29025
S7  Matic, Packham, Haerdle, "Hedging cryptocurrency options", Rev. Derivatives Research 26(1):91-133, 2023,
    DOI 10.1007/s11147-023-09194-6. T1. https://pmc.ncbi.nlm.nih.gov/articles/PMC9911343/ (first 100k chars read)
S8  Atanasova, Miao, Segarra, Willeboordse, "Aggregate illiquidity and crypto option returns", Finance Research Letters
    85(PC), 2025, DOI 10.1016/j.frl.2025.108003. T1, abstract only.
    https://ideas.repec.org/a/eee/finlet/v85y2025ipcs1544612325012619.html
S9  Alexander, Deng, Feng, Wan, "Net Buying Pressure and the Information in Bitcoin Option Trades", arXiv:2109.02776 v2
    (25 Mar 2022). T2, abstract only. https://arxiv.org/abs/2109.02776
S10 Schmeling, Schrimpf, Todorov, "Crypto carry", BIS Working Paper 1087, 4 Apr 2023. T1. https://www.bis.org/publ/work1087.htm
S11 He, Manela, Ross, von Wachter, "Fundamentals of Perpetual Futures", arXiv:2212.06888 (v7, 17 Sep 2026). T2, abstract only.
    https://arxiv.org/abs/2212.06888
S12 Israelov & Klein, "Risk and Return of Equity Index Collar Strategies", J. Alternative Investments 19(1), Summer 2016.
    T1 (EQUITY analogue). Full text read: https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/Risk-and-Return.pdf
S13 Israelov & Nielsen, "Covered Calls Uncovered", Financial Analysts J. 71(6):44-57, 2015, DOI 10.2469/faj.v71.n6.1.
    T1 (EQUITY analogue), abstract only. https://ideas.repec.org/a/taf/ufajxx/v71y2015i6p44-57.html
S14 Bakshi & Kapadia, "Delta-Hedged Gains and the Negative Market Volatility Risk Premium", Rev. Fin. Studies 16(2):527-566,
    2003, DOI 10.1093/rfs/hhg002. T1 (EQUITY method base), abstract only. https://ideas.repec.org/a/oup/rfinst/v16y2003i2p527-566.html
S15 Golez & Jackwerth, "Pinning in the S&P 500 futures", J. Financial Economics 106(3):566-585, 2012,
    DOI 10.1016/j.jfineco.2012.06.010. T1 (EQUITY), abstract only. https://ideas.repec.org/a/eee/jfinec/v106y2012i3p566-585.html
S16 Houlihan & Creamer, "Leveraging a call-put ratio as a trading signal", Quant. Finance 19(5):763-777, 2019,
    DOI 10.1080/14697688.2018.1538563. T1 (EQUITY, 2005-2012), abstract only. https://ideas.repec.org/a/taf/quantf/v19y2019i5p763-777.html
S17 Deribit Insights (Cryptarbitrage), "Option Backtest - Selling Weekend Vol", 19 Sep 2024. T3 (exchange-published,
    not peer reviewed). https://insights.deribit.com/education/option-backtest-selling-weekend-vol/ (opened as ?p=88953)
S18 Same series, "... Revisited", 21 May 2025. T3. https://insights.deribit.com/education/option-backtest-selling-weekend-vol-revisited/
    (opened as ?p=99807)
S19 Anchorage Digital Research (D. Lawant), "Synthetic Yield on Bitcoin: ... Systematic Covered Call Writing", 28 May 2026
    (page modified 29 Sep 2026). T2 (regulated-bank research, method disclosed, commercial interest, not peer reviewed).
    https://www.anchorage.com/research/synthetic-yield-on-bitcoin-implementation-discipline-and-performance-boundaries-of-systematic-covered-call-writing
S20 Deribit Support pages (T2, exchange docs; opened in browser pane, each shows "Updated" 10-24 days before 2026-10-09):
    Fees .../hc/en-us/articles/25944746248989-Fees | Settlement .../29734325712413-Settlement |
    Inverse Options .../31424939096093-Inverse-Options | Standard Margin .../25944811528477-Standard-Margin |
    Portfolio Margin .../25944756247837-Portfolio-Margin | Contract Introduction Policy .../25944688876957-Contract-Introduction-Policy
    (host https://support.deribit.com). Plus Deribit Insights "Change To Option Delivery Process", 12 Mar 2026,
    https://insights.deribit.com/?p=113365 and "Deribit lowers Option trading fees" https://insights.deribit.com/?p=2277
    (0.04% -> 0.03% effective "Monday, August 24", year not stated on page; page dates conflict: 12 Aug 2020 vs 11 Jun 2021).
S21 Deribit Insights, F. Fernando, "DVOL - Deribit Implied Volatility Index", 31 Mar 2021 (upd 20 Mar 2023). T2.
    https://insights.deribit.com/?p=1813
S22 C. Alexander, "Bitcoin Variance Swaps", Social Science Encyclopedia reprint (28 May 2021 / 6 Sep 2022). T3 (qualitative).
    https://www.socialscience.international/bitcoin-variance-swaps

## 2. Q1 - Is there a BTC variance risk premium, and do short-vol strategies earn it net of costs?
Verdict: premium SIGN is supported (implied > realized, T1/T2). NET-OF-COST capturability is NOT validated by any T1/T2 source.

F1.1 Premium exists (implied variance above realized), larger in calm regimes. S1: Deribit transaction-level options
  2017-07..2022-12, 27-day options, BVRP = sigma_Q^2 - sigma_P^2 (BVIX variance-swap method vs 27-day realized variance).
  Annualized variance units: all 0.72 vs 0.58 = 0.14; HV regime 0.86 vs 0.74 = 0.12; LV regime 0.46 vs 0.29 = 0.17.
  In vol points (my arithmetic, sqrt): ~84.9 vs ~76.2 (gap 8.7); LV 67.8 vs 53.9 (13.9); HV 92.7 vs 86.0 (6.7).
  S&P 500 VRP quoted at ~0.02. Return-premium (first moment) decomposition: states with +20..+60% returns carry 38.7% of the
  BTC return premium overall, 52.3% in the LV regime (equities: mostly mildly negative returns). Whether OTM calls are better
  paid than OTM puts for SELLERS is not established by S1 (it decomposes the return premium, not seller P&L).
  Tag: T2 | transaction prices not quotes, no costs, no OOS, one venue; paper's day counts inconsistent (1,992 / 1,301 / 1,017
  days in different sections) | M for sign, L for size.
F1.2 S2 (abstract only): 5 years of Deribit data, delta-hedged roll strategies (selling and buying options), USD vs coin P&L
  accounting shown equivalent; "risk premia in Deribit options are negative and significant, so strategies that sell
  volatility should earn positive risk-adjusted returns over the long term." Inverse-option delta needs a premium adjustment.
  Tag: T1 | abstract only; Sharpe, tenor, delta, roll rule, cost model NOT retrievable | M direction, L magnitude.
  (A search-tool excerpt of the SSRN version claimed "realistic transaction costs" and short calls out-earning short puts;
  I could not open that page, so neither claim is used. See REJECT.)
F1.3 Method base (equity): delta-hedged option gains are the standard VRP test; S&P 500 delta-hedged long options lose (S14).
  So a delta-hedged SHORT option P&L series is the right object to measure in our backtest, not raw payoff tables.
F1.4 Net-of-cost short-vol evidence on Deribit (all weak):
  a) Weekend short strangle (S17, S18): sell put+call at ~0.35 delta Fri 16:00 UTC, expire Sun 08:00 UTC, held to expiry;
     fee 0.0003 BTC/option + 5% haircut on premium; flat size 1/1 from 1 BTC; hourly data. 2020-01-01..2024-08-31: 212 trades,
     169 wins, +1.2485 BTC, APR 27.4%, max DD 23.8% (0.27 BTC). 2024-09-01..2025-04-30 (post-publication): 34 trades, 32 wins,
     +0.2912 BTC, APR 45.8%, DD 3.9%. Sunday-open variant: 251 trades, -0.9224 BTC, DD 102.1%. All-days 2 DTE at size 0.5:
     1780 trades, +126.5%, APR 23.8%, DD 26.5% (0.45 BTC). ETH Friday: APR 20.3%, DD 27.2%.
     Authors' own caveats: look-ahead (idea from same-sample average daily moves), DD understated by hourly data, left tail not
     in sample, no bid/ask (haircut only). Tag: T3 | in-sample idea, costs approximated, 212 trades | L-M.
  b) Covered call overlay (S19): Deribit hourly constant-delta IV surfaces (via CoinMetrics), Black-76, r=0; 2021-10-01..2026-04-30.
     Unfiltered 20-delta / 30-day calls: FULL-PERIOD overlay net yield -0.5% (-0.1%/yr), profit factor 1.00, 70 trades, 13 losers;
     last 12 months +5.5% vs spot -19.4% (16 trades, 3 overran). Filtered (regime + IV filters, 108-combo grid, 37,000 rolling
     windows): +23.7% (+5.2%/yr), market exposure ~44%. 7- and 14-day expiries worst; 15-25 delta best; 30-35 delta high
     negative-outcome risk; 3-year rolling positive-yield rate >= 91% for 11/12 corridor configs, median 4-6%/yr.
     Costs: slippage 1 vol point per leg; trading FEES NOT DESCRIBED. Tag: T2 | no OOS split, grid-searched filters (overfit
     risk, no PBO), one BTC cycle, fees missing | L for filtered result, M for "unfiltered ~ zero".
  c) GARCH-minus-IV spread, delta-hedged (S5): single contract BTC-8000-C-27MAR20, 2019-09-10..2020-03-26; best spec
     (24h GARCH, entry 0.05, exit 0.00): 25 trades, 88.5% win, gross PnL $2,251 on $5,000 capital. Appendix A2: option fees $85
     + hedge fees $361 (taker 0.04% options, 0.075% perp) = $446 (19.8% of PnL); spread cost at 3% of ATM premium +
     $0.50 perp = $1,182 (52.5% of PnL). If additive, ~27.7% of gross (~$623) survives. Strategy failed in 2020-03.
     Tag: T2 (journal version T1 abstract) | no OOS, 1 contract, 6.5 months, thresholds swept | L.
F1.5 Tail risk (qualitative, consistent): S22 says BTC variance premium can spike unpredictably and is hard to hedge with
  options (T3); S5 lost on 2020-03; S19 stop-loss exits rose 13 -> 19 under filters; S18 Sunday variant exceeded 100% DD
  (backtest does not stop at ruin). Short BTC options on Deribit are coin-margined: a short put's USD loss is compounded by
  collateral (BTC) falling (my inference from S20 mechanics; quantify in backtest).
F1.6 What a covered call actually earns (S13, equity, abstract only): equity premium + VRP + an unrewarded reversal exposure;
  short-vol leg Sharpe near 1.0 on <10% of risk. Implication: score a BTC covered call versus BTC-hold AND isolate the short-call
  sleeve; do not credit the BTC beta as strategy alpha.
F1.7 Hedging a short-option book (what the hedge costs):
  S3 (abstract only): hourly BTC options, synthetic 10/20/30-day maturities, two 1-year periods; smile-implied deltas beat
  Black-Scholes delta by >30% (hedging-error variance ratio) for OTM puts and ~15% for short-term OTM calls; perpetual swap
  is the better hedge than calendar futures (smaller basis risk). T1 | no costs | M.
  S6 (abstract only): Deribit 2020-2024, test episodes 2023-09..2024-12 (11,546), 5 bp cost: Whalley-Wilmott no-trade band
  saved $1.79/episode vs hourly BS-delta (95% CI -2.21..-1.39), ~8x fewer trades; P&L/tail gains not significant; advantage
  shrank in the calm validation period; deep-hedging nets no better than classical. T2 | OOS yes, cost 5 bp flat | M-L.
  S7: SVCJ / GARCH-KDE / historical paths; Delta, Delta-Gamma, Delta-Vega, min-variance; multi-instrument hedges cut ES5%
  for longer maturities (e.g. 1M bullish 1.75 -> 1.21; table alignment ambiguous in source), short maturities barely respond;
  frictionless, bid/ask ignored.
  T1 | no costs | M.
F1.8 No validated evidence found for: cash-secured puts, short straddles (ATM), iron condors/defined-risk wings, or
  any rolling short-vol program on BTC that reports Sharpe/drawdown net of fees AND real bid/ask. Vendor/blog results exist
  (REJECT list) but fail the cost/method bar.

## 3. Q2 - Do long-vol / protective put / collar overlays pay for themselves on a BTC long?
Verdict: No validated evidence found for BTC (no peer-reviewed or disclosed-method overlay study on Deribit, CME or IBIT
options measuring carry vs tail saved). Only analogues:
F2.1 Equity analogue S12 (full text): CBOE S&P 500 95-110 Collar Index 1986-07..2014-12: excess return 3.2%/yr vs S&P 7.3%,
  vol 10.7% vs 15.7%, equity beta 0.62, Sharpe ~35% below S&P, alpha -1.3%/yr; puts pay the VRP and a "zero-cost" collar is
  not zero cost because the put is the more overpriced leg (skew). Constructive example: 3-month put at 95% of index, call strike
  chosen so premium offsets the put. T1 | equity, 28 years, index-level, no BTC | M that logic transfers, L for numbers.
F2.2 BTC-specific indirect evidence: (i) S1: VRP higher in LV regimes (0.17 vs 0.12) -> long-variance hedges are dearest
  when vol is low (inference). (ii) S10 (BIS): futures basis averages >10%/yr, high carry predicts crashes, rising carry coincides
  with rising prices of crash-risk insurance -> hedge cost is state-dependent. (iii) S19: call overlays do not hedge drawdown
  (blended max DD 44.5-49.7% in the 12m to 2026-04-30 despite +5.5% overlay yield).
F2.3 Cheaper hedge instrument to benchmark against: short perp / futures hedge pays/receives funding; S11 (abstract only) and
  S10 show crypto perp/futures basis deviates widely and arbitrage is not risk-free (margin spikes, no convergence date).
  Options-vs-perp hedge comparison for our book = OPTIONS_PLAN Question B; no external number to import.
F2.4 Test design from sources: rolling long put grid (strike % of spot, tenor) and collar with call premium matched to put
  premium (S12); report premium carry %/yr, MaxDD, ES5% of hedged vs unhedged perp PnL; both USD and coin accounting (S2).

## 4. Q3 - Other claimed edges
Verdict by item (none validated for BTC options profit):
F3.1 DVOL mean reversion: No validated evidence found. Index spec (S21, T2): 2 expiries bracketing 30 days (each >= 1 h old);
  mid price = average of depth bid/ask, VWAP over 2 BTC size, up to 5 levels; wide-spread fallback to 1-min trade VWAP/mark;
  delta cutoff 5%; variance-swap formula; raw value every second, EMA over last 240 points; Deribit may change parameters
  with 48 h notice. Implication: DVOL is a smoothed, ~4-minute-lagged series; do not backtest entries at DVOL ticks.
F3.2 IV vs realized-vol spread as a timing signal: mixed. S4 (T1, abstract only): Deribit IV is LESS accurate than ARMA/HAR at
  1-day horizon but MORE accurate at 7/10/15 days; combining IV with model forecasts is best at every horizon. S5 (journal
  abstract): GARCH forecasts beat IV for realized vol, and a delta-hedged GARCH-IV spread trade was profitable gross
  (net-of-cost see F1.4c). Contradiction is horizon/period dependent -> test spread-timing as a swept filter, not as a rule.
  S19's IV filter (30-day IV at target delta above its own 90-day average) lifted full-period overlay yield from -0.5% to +23.7%
  but within a 108-combo grid -> L.
F3.3 Term structure / skew signals: No validated evidence found. (A 2026 SMU dissertation on 25-delta risk-reversal predicting BTC
  returns could not be opened -> REJECT.) Adjacent verified: S8 (T1, abstract only, Deribit 2021-2024): when market-maker
  aggregate gamma inventory is negative, effective spreads widen (+0.12% OTM calls, +0.19% OTM puts per 1 s.d.) and the
  illiquidity factor is priced in BTC option returns -> spread cost is state-dependent. S9 (T2, abstract only): ATM prices are driven
  mainly by volatility traders, OTM prices also by informed directional traders.
F3.4 0DTE / weekly / weekend: only S17/S18 (T3, F1.4a). Sunday-open loses, Friday-open wins in-sample; all-days dilutes.
  No peer-reviewed BTC test. Structural fact (S20 Contract Policy): up to 4 daily, 3 weekly, 3 monthly, 4 quarterly BTC
  inverse expiries; dailies are exempt from delivery fees (S20 Fees).
F3.5 GEX / max pain / pinning: No validated evidence found for BTC. Equity only: S15 (abstract only) S&P 500 futures drift
  toward the ATM strike on option-expiry days (delta-hedge decay), est. >= $115m notional/expiry day. Dealer sign for crypto OI is
  unobservable from public data; vendor GEX (REJECT list) is untested.
F3.6 Funding/basis + options: options-specific edge: No validated evidence found. Verified context: S10 average carry >10%/yr,
  up to ~60%/yr, driven by retail leverage demand and scarce arbitrage capital; S11 perp deviations from no-arbitrage are
  larger than FX, shrink over time, yet an implied arbitrage still shows high Sharpe after highest Binance fees (abstract).
F3.7 Put-call ratio: No validated evidence found for BTC. S16 (equity, 2005-2012, special volume data): ratio-sorted portfolios
  earn abnormal returns after Carhart and costs -> not transferable to Deribit total volume ratios.

## 5. Q4 - Deribit mechanics that drive cost (S20, T2, verified 2026-10-09)
- Trading fee (Standard tier): options 3 bps of underlying per contract, maker = taker (0.0003 BTC), capped at 12.5% of option
  price per leg (cap binds when premium < 0.0024 BTC; my arithmetic). Fee currency = BTC. VIP1 2.5/2.5 bps (cap 10.42%); higher VIPs lower.
  Pre-2020-08 era was 0.04% (S20 Insights ?p=2277; year on page unclear) - S5 used 0.04% taker. Perp/futures standard 1.5 maker / 3.5 taker bps.
- Combos: buy+sell option combos zero the cheaper side's fees; same-direction combos (straddle, strangle) get NO discount. Block option fee 3 bps.
- Delivery fee: BTC/ETH options 0.015% of underlying (never above 12.5% of option value), charged on ITM expiry; DAILY options 0%;
  futures 0.025%; weekly futures 0%; DVOL futures 0.05%. Settlement (daily 08:00 UTC mark-to-market) has no fee. Liquidation fee extra,
  options capped at 25% of option value, no tier discounts.
- Expiry/delivery: 08:00 UTC; delivery price = 30-min TWAP of Deribit index 07:30-08:00 UTC (snapshot every 4 s); delta of expiring
  options decays linearly to 0 over the last 30 min. Since 2026-08-01 ITM inverse options first settle into an inverse future at the
  strike, which then cash-settles in BTC; P&L unchanged, delivery fee charged once, offsetting futures net before fee.
- Inverse (coin) payoff: contract multiplier 1; premium and margin in BTC; call pays (S_T - K)/S_T BTC, put pays (K - S_T)/S_T BTC
  (S20 worked examples: K=100k, S_T=125k -> 0.2 BTC; K=100k, S_T=80k -> 0.25 BTC). Displayed IV uses the FORWARD, not the index.
  S2: inverse options are vanilla options under forward numeraire; delta needs the premium adjustment; USD and coin accounting both valid.
- Margin: default account mode S:SM (segregated standard). Standard margin per 1 BTC contract (BTC units):
  short call IM = MAX(0.15 - MAX((K - Index)/Index, 0), 0.1) + mark; short put IM = MAX(MAX(0.15 - MAX(Index - K, 0)/Index, 0.1)
  + mark, MM); MM short call 0.075 + mark; short put MAX(0.075, 0.075*mark) + mark. Long options: premium only. Portfolio margin (S:PM, X:PM):
  worst case of price-move x vol-shock risk matrix (example +/-16%, 9 buckets, vol up/same/down) + extended table (-66%..+500%, vol up
  only) + delta shock + roll shock; MM factor 0.80 by default. Hedged/spread books should need less margin under PM than SM
  (inference, not a doc statement); model both.
- Liquidity by tenor: NO validated tenor-by-tenor spread study found. Listing structure (S20): strike step for BTC <=4 days
  $500 ATM/$500 outer/$1,000 wings; 1 week and 1 month $1,000/$2,000/$5,000; 3 months $2,000/$5,000/$10,000 (Contract Policy
  secondary snapshot; I opened the expiry table in-browser and the strike table via search excerpt only - re-check before use).
  Spread evidence: S5 ~3% of premium at ATM in 2019-20 (stale); S8 shows state dependence. Own snapshots (OPTIONS_PLAN P2) are the only
  valid source: measure (ask-bid)/mid by DTE and delta.

## 6. Ranked backtest list (what to test first) with source parameters
Ranking rule: parameter completeness x evidence tier x testability on Deribit public history. All need real bid/ask or a
swept spread (S5: 3% of premium ATM; S19: 1 vol point; S17: 5% of premium) AND the fee schedule in section 5.
R1 Weekend short strangle (S17/S18, T3). Sell put + call nearest 0.35 delta (max 0.1 delta deviation), Fri 16:00 UTC, expiry Sun
   08:00 UTC, hold to expiry, flat 1+1, 1 BTC start, fee 0.0003/option, 5% premium haircut, hourly data. Reported: 2020-01..2024-08
   +124.85%, DD 23.8%. Our job: re-run on 2025-05 onward (true OOS), swap haircut for measured spread, add 2020-03/2021-05/2022-11
   stress, size as % of equity, coin vs USD accounting, then PBO over delta {0.25..0.45}, entry hour, Sat/Sun variants.
R2 Covered-call overlay (S19, T2). Grid: delta 5-45 (headline 10/15/20/25), tenor 7/14/21/30/60/90 d; base 20-delta 30-day;
   strike from target delta (Black-76, r=0); exits: take profit at 75% decay, delta stop at live delta 0.45 (example value),
   close within 48 h of expiry; immediate re-entry; filters: no bullish 10/30/50-day SMA stack, 30-day IV (target delta) above its
   90-day average; hourly checks; slippage 1 vol pt each leg. Report unfiltered vs filtered, with fees added and PBO on the 108 grid.
   Expected prior: unfiltered ~0 net yield (S19 full period -0.5%).
R3 Delta-hedged rolling short straddle/strangle (mechanism T1: S2, S14; tenor/delta NO-SOURCE -> swept grid, report whole grid).
   Hedge rules with sources: re-hedge on |delta change| > 0.02 (S5) vs Whalley-Wilmott no-trade band (S6, 5 bp cost, saved
   $1.79/episode) vs smile-implied delta (S3: synthetic 10/20/30-day maturities, hourly option prices); hedge instrument =
   BTC-PERPETUAL (S3), include funding; inverse-option delta premium adjustment (S2). Measure P&L = gamma/theta/vega + funding + fees.
R4 Cash-secured put (short put, BTC collateral): NO-SOURCE parameters. Mirror R2 grid on puts; report calls vs puts separately
   (no verified source says which side pays sellers more). Coin-margin double hit: model USD equity path.
R5 Defined-risk variants (iron condor / long wings on R1): NO-SOURCE wings; swept grid; purpose is to cap the left tail S17 admits.
R6 GARCH-IV spread filter on R3 (S5: GARCH, 24h update; spread = GARCH multi-period vol forecast minus option IV; entry
   threshold {0.05, 0.075, 0.10} x exit {0.00, 0.05}, 5 combos reported, win rates 87.5-92.3%; 1 call + delta in perp, re-hedge
   at |delta change| > 0.02). Low rank: one contract, 8-25 trades, spread cost 52.5% of gross. Use only as a filter inside R3
   with full-grid reporting.
R7 Protective put / collar overlay on BTC long (Question B; no BTC source): 3-month put at 95% of spot and call matched to put
   premium (S12 construction) plus rolling OTM put grid; metrics = carry %/yr vs ES5%/MaxDD saved; vs perp-short hedge with funding.
Not recommended to build until R1-R3 produce own data: DVOL mean reversion, skew/term-structure timing, GEX/max pain, put-call ratio.

## 7. Backtest design notes drawn from sources
- Account in both coin and USD (S2). Use delivery TWAP, not the 08:00 index print (S20). Forward-based IV (S20) for delta.
- Fees by era: 0.04% before the 2020 cut, 0.03% after; delivery 0.015% on ITM non-daily expiries; cap 12.5% of premium.
- Do not let equity go below zero silently (S18 notes DD above 100% means liquidation in practice); apply S20 margin rules.
- Data fidelity per OPTIONS_PLAN: public trades + DVOL + index = lower fidelity than order-book snapshots; label results.

## 8. REJECT list (not used; do not re-research)
- Winnower/Authorea "Bitcoin Portfolio Hedging Using Protective Put Options" (doi 10.15200/winn.145088.84878): pages 403 / TLS mismatch, unopenable.
- SMU dissertation on BTC risk-reversal predicting returns (ink.library.smu.edu.sg/etd_coll/887): page returned no content; unverifiable.
- Lucic & Sepp claims "realistic transaction costs" and "short calls beat short puts" (SSRN version): only seen in search excerpts; unverified.
- Atanasova et al. 2024 working paper (AUT-hosted PDF, 0.07%/0.06% delta-hedged return headline): 403, not opened; FRL 2025 used instead.
- Alexander & Imeraj J. Alt. Investments 23(4):84-109 "The Bitcoin VIX and Its Variance Risk Premium" (DOI 10.3905/jai.2020.1.112): metadata
  confirmed via Crossref, abstract paywalled; no finding taken from it.
- Alexander & Imeraj QF "bid-ask 200-300 bp ATM" figure: search excerpt only, not verified.
- Grayscale July 2026 covered-call yield (22%): scenario arithmetic, not a backtest, not opened.
- Cointelegraph/Cryptowisser/BYDFi/Bybit/exchange Q&A "hedging guides": marketing or generic; no method (Bybit fee numbers are another exchange).
- Delta Exchange blog "ETH straddle 70.21% win rate": entry time chosen in-sample, win-rate claim without costs (not opened).
- Panoptic "BTC straddle +10.32% annualized": DeFi venue (Uniswap v3/Aave), not Deribit (not opened).
- Glassnode taker-flow GEX (Dec 2025) and vendor GEX dashboards: original not opened, dealer-sign assumption untested, no OOS.
- Glassnode IBIT metrics note (18 May 2026): descriptive, own disclaimer "limited case study"; no test (opened, not used).
- Filippou, Garcia-Ares, Zapatero "No Max Pain, No Max Gain" (2022): paper not opened, equity only; blog summaries (Coinglass, OptionCharts, LuxAlgo) REJECT.
- Put/call ratio commentary (The Block, CoinDesk, Deribit executives): opposite readings of same ratio, no tested OOS.
- Chepal tweet "IV falls 80% of the time after Friday expiry" (via blockchain.news): anecdotal, no method.
- Guo, Li, Luo, Wang "Illiquid Bitcoin Options": US-regulated market, not Deribit, not opened.
- Harbourfront Substack summary of S1: secondary; replaced by the arXiv text.
- Deribit Insights "Trading Volatility - What Are My Options?" (2023) and SignalPlus "Demystifying DVOL Futures": education, no backtest or statistics (opened).
- Chi & Hao abstract headline "robust profits": abstract-level, costs only in Appendix A2 (cost-adjusted figures used instead).
