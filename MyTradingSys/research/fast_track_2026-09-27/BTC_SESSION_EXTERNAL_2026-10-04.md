# BTC session / open - external literature check (playbook Part I) - 2026-10-04

Session MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps/sonnet-01. Web research only. Tiers fixed per playbook Part I.
Every source below was opened 2026-10-04 ("verified 2026-10-04") unless listed under DISCARDED. 14 distinct sources opened
(brief said ~12; 2 extra were needed to close Q4). Most pages gave ABSTRACT ONLY; where a number is not on the page it says so.
Already verified in repo (cited, NOT re-researched): Osler 2000/2003/2005, Kavajecz & Odders-White 2004, Brock-Lakonishok-LeBaron
1992, Chung & Bellotti 2021, George & Hwang 2004 (PARTIAL) in T058_BROKEN_EXTREMES.md; Shen-Urquhart-Wang 2022 (E4), Kim-Hansen
arXiv 2607.09426 (E6), Concretum seasonality (E8, T3) in FABIO_BTC_RESEARCH_2026-09-30.md section 3.
Rule reminder: external evidence only ranks what to test; our own OOS backtest (fees + funding + slippage, PBO) decides.

## 1. Step-1 method notes (what evidence would settle each question)
Q1 (session seasonality): an hour-of-day (UTC) study of realised volatility, volume and SIGNED return on several exchanges, >= 2 years,
with the US-open DST shift (13:30 UTC summer / 14:30 UTC winter) handled and a pre/post Jan-2024 (spot ETF) split. Volatility/volume
seasonality is descriptive (costs not needed); any direction claim needs out-of-sample testing net of fees, funding and slippage.
Q2 (first 10-30 min decide the day): a predictive test of first-N-minute return on later return, with multi-instrument or OOS
replication, then a tradable test net of commissions and slippage; for BTC the anchor must be the US cash open, not 00:00 UTC.
Q3 (pre-open sweep then reversal): an event study conditioning on a pre-defined prior range (overnight/Asia/London) being taken out
within minutes of an open, comparing subsequent returns with breaks that hold, on tick or order data, with costs and multiple-testing
control. If no T1/T2 study exists the answer is "No validated evidence found" and only our own backtest can decide.
Q4 (equity spillover): a predictive regression of BTC US-session return on ES/NQ open-period or overnight return, clock-aligned and
DST-aware, OOS and net of costs, plus a time-of-day BTC-equity correlation profile split at Jan-2024.
Deviation logged: these notes were written into this file after the first citation-check searches, not before them.

## 2. Citation-check table (source | claimed for | result)
| # | Source | Claimed for | Result |
|---|---|---|---|
| 1 | Hansen, Kim, Kimbrough (2024), "Periodicity in Cryptocurrency Volatility and Liquidity", J. Financial Econometrics 22(1):224-251, doi 10.1093/jjfinec/nbac034; https://research.cbs.dk/en/publications/periodicity-in-cryptocurrency-volatility-and-liquidity/ and https://arxiv.org/abs/2109.12142 | Q1 | VERIFIED (title/authors/venue/year match; abstract only; PDF not parseable here; abstract gives no UTC hours) |
| 2 | Baur, Cahill, Godfrey, Liu (2019), "Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume", Finance Research Letters 31:78-92, doi 10.1016/j.frl.2019.04.023; https://ideas.repec.org/a/eee/finlet/v31y2019icp78-92.html | Q1 | VERIFIED (abstract only) |
| 3 | Eross, McGroarty, Urquhart, WOLFE (2019), "The intraday dynamics of bitcoin", Res. Int. Business & Finance 49:71-81, doi 10.1016/j.ribaf.2019.01.008; https://econpapers.repec.org/article/eeeriibaf/v_3a49_3ay_3a2019_3ai_3ac_3ap_3a71-81.htm | Q1 | VERIFIED (abstract only). AUTHOR CORRECTION: fourth author is Simon Wolfe, not "Wald" as in the brief |
| 4 | Wang, Liu, Hsu (2020), "Time-of-day periodicities of trading volume and volatility in Bitcoin exchange: Does the stock market matter?", Finance Research Letters 34; https://ideas.repec.org/a/eee/finlet/v34y2020ics1544612319301904.html | Q1 (found by search, not in brief) | VERIFIED (abstract only) |
| 5 | Brauneis, Mestel, Theissen (2024 online), "The crypto world trades at tea time: intraday evidence from centralized exchanges across the globe", Rev. Quantitative Finance & Accounting, doi 10.1007/s11156-024-01304-1; https://irep.ntu.ac.uk/id/eprint/51576/ | Q1 (found by search) | VERIFIED (abstract only; publisher page redirected to login, NTU repository page opened instead) |
| 6 | Wen, Bouri, Xu, Zhao (2022), "Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both", N. Am. J. Economics & Finance 62, doi 10.1016/j.najef.2022.101733; https://ideas.repec.org/a/eee/ecofin/v62y2022ics1062940822000833.html | Q1, Q2 | VERIFIED (abstract only; SSRN copy returned 403) |
| 7 | Gao, Han, Li, Zhou (2018), "Market intraday momentum", J. Financial Economics 129(2):394-414; https://ideas.repec.org/a/eee/jfinec/v129y2018i2p394-414.html | Q2 | VERIFIED (abstract only) |
| 8 | Barbon, Aziz, Zarattini (2024), "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)", Swiss Finance Institute Research Paper N. 24-97, 27 Nov 2024; https://www.sfi.ch/en/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy | Q2 | VERIFIED (abstract only; SSRN 4824172 returned 403) |
| 9 | Zarattini, Barbon, Aziz (Feb 2024), "A Profitable Day Trading Strategy For The U.S. Equity Market", SSRN 4729284; opened only the authors' firm page https://concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/ | Q2 | PARTIAL: title/authors matched on the authors' own page; SSRN page 403, so the paper itself is not opened -> capped at T3 |
| 10 | Brusco, independent replication of Zarattini & Aziz 2023 (SSRN 4416622), https://github.com/giovannibrusco/zarattini-2023-orb-qqq | Q2 costs | OPENED (README); T3, not peer reviewed |
| 11 | Holmberg, Lonnbark, Lundstrom (2013), "Assessing the profitability of intraday opening range breakout strategies", Finance Research Letters 10(1):27-33; https://econpapers.repec.org/RePEc:eee:finlet:v:10:y:2013:i:1:p:27-33 | Q2 | VERIFIED (abstract only) |
| 12 | Evans (2018), "Forex trading and the WMR Fix", J. Banking & Finance 87:233-247, doi 10.1016/j.jbankfin.2017.09.017; https://ideas.repec.org/a/eee/jbfina/v87y2018icp233-247.html | Q3 | VERIFIED (abstract only) |
| 13 | Tang, Lee, Huang, Liu (2024), "The impact of index futures crash risk on bitcoin futures returns and volatility", Heliyon; https://pmc.ncbi.nlm.nih.gov/articles/PMC10825442/ | Q4 | VERIFIED (full text on PMC) |
| 14 | De Nicola (2021), "On the Intraday Behavior of Bitcoin", Ledger 6; https://ledger.pitt.edu/ojs/ledger/article/view/213 | Q2, Q3 | VERIFIED (abstract only) |

## 3. Findings
Tag format: Tier | Method quality (OOS? costs? sample/period) | Confidence H/M/L

### Q1 - BTC intraday seasonality by session
- BTC volume and volatility are higher in hours that coincide with European and US stock-exchange daytime, with an inverted-V shape
  over the day; Asian stock opens barely move volatility and do not move volume; weekdays above weekends (Wang et al. 2020, Bitstamp,
  hourly shares of volume and realised variance). `T1 | descriptive; no OOS; no costs (not a trading test); sample dates not on the abstract page | M`
- Realised volatility is "fairly consistent" through the day but highest at the opening times of the three major global stock markets;
  volume rises through the day and falls from about 16:00 until midnight; liquidity is highest at the opens and thin in the early
  morning (Eross et al. 2019, 5-minute GMT tick data, 4 years, the leading exchange). `T1 | descriptive; no OOS/costs; period not on page | M`
  Reading: the US open is one of three volatility bumps, not a unique one.
- Activity, volatility and illiquidity all peak at 16:00-17:00 UTC across 38 exchanges and 1,940 pairs (Brauneis et al. 2024).
  `T1 | descriptive; sample period not on abstract page | M (that a peak exists), L (its cause)`
  Reading: this is 1.5-2.5 hours AFTER the US cash open (13:30 / 14:30 UTC), so the largest hour in that study is not the open hour.
- Systematic patterns across day-of-week, hour-of-day and within the hour; intensified over time; linked to algorithmic trading and
  futures funding schedules; centralised exchanges lead price discovery (Hansen-Kim-Kimbrough 2024; Coinbase Pro, Binance,
  Uniswap V2 per abstract). `T1 | abstract only; hour list and dates not on the page | M`
  Within-hour structure (quarter-hour): Kim-Hansen already verified in repo (E6, ~0.5 bp predictable part, below fees).
- Direction by session: time-specific return anomalies exist but are NOT persistent across time; persistent differences are in
  volume (Baur et al. 2019, >15M observations, 7 exchanges). `T1 | long multi-exchange sample; descriptive | M-H for "no stable session-direction edge"`
  BTC intraday return predictability exists, both momentum and reversal, and changes with large jumps, FOMC releases, liquidity and
  COVID; timing strategies beat buy-and-hold (Wen et al. 2022, BTC Mar-2013..May-2020, pre-ETF). `T1 | OOS and costs not stated on the abstract page | L-M`
- Post-2024 spot-ETF era, session returns or session volatility: No validated evidence found (nothing T1/T2 could be opened; see the
  hand-check candidate in DISCARDED).
- Parameters the literature used (Q1): 5-minute bars with GMT timestamps (Eross); hourly bins of volume share and realised variance on
  one exchange (Wang); hourly UTC bin 16:00-17:00 across 38 exchanges (Brauneis); day-of-week + hour-of-day + within-hour bins
  (Hansen); 7 exchanges, hour/weekday/month dummies (Baur). NO opened abstract defines Asia / London / US session boundaries and none
  states whether the US-open DST shift was handled. Session windows in our backtest are therefore OUR choice and must be
  pre-registered: 00:00 UTC (Asia), 07:00 or 08:00 UTC (London), 13:30 UTC summer / 14:30 UTC winter (US cash open), with DST flagged.

### Q2 - "First 10-30 minutes decide the day"
- US equities: the first half-hour return, measured from the PREVIOUS day's close (so it includes the overnight gap), predicts the
  LAST half-hour return of the day; stronger on high-volatility, high-volume, recession and macro-announcement days; also holds for 10
  other ETFs (Gao-Han-Li-Zhou 2018, S&P 500 ETF 1993-2013). `T1 | predictive regression; costs and OOS not in the abstract; 20 years | M-H for equities`
  It predicts the last 30 minutes, not the rest of the day.
- Tradable version: trend-following entries as soon as intraday supply/demand imbalance appears (not only the last 30 minutes) with
  dynamic trailing stops on SPY, 2007-early 2024: 19.6% annualised, Sharpe 1.33, 1,985% total, net of commissions and slippage per
  the abstract (Barbon-Aziz-Zarattini, SFI 24-97). `T2 | net of costs (stated); OOS not mentioned; authors run a commercial research firm | M`
- 5-minute opening-range breakout on 7,000+ US stocks 2016-2023, "stocks in play" top-20 portfolio: 1,600% net, Sharpe 2.81, with 15,
  30 and 60-minute ranges compared (Zarattini-Barbon-Aziz, SSRN 4729284, via authors' page only). `T3 | costs claimed net; no OOS disclosed; selected subset | L`
- Independent replication of the 5-minute QQQ ORB (SSRN 4416622), Jan-2016..Feb-2023, 1,775 trades vs 1,795 in the paper: net PnL
  crosses zero at about 2.2 cents/share entry slippage (about one spread); 76% of the NQ-filtered profit comes from 2022 alone; the
  strategy loses in 2017, 2020 and early 2023; the filter was chosen in-sample. `T3 | costs stress-tested; no OOS; not peer reviewed | M that the equity ORB edge is cost- and regime-fragile`
- Crude-oil futures ORB with a distributional (low/high/open/close) test finds returns above zero (Holmberg et al. 2013).
  `T1 | abstract only; sample and costs not on page | L (different instrument)`
- BTC at the US cash open (not 00:00 UTC): No validated evidence found. Adjacent only: BTC returns over 1, 2 and 4 hours show
  significant NEGATIVE first-order autocorrelation, larger moves reverse more, a simple strategy is back-tested, authors blame
  overreaction and liquidation cascades (De Nicola 2021, 1-minute data Jan-2012..Mar-2021). `T1 | in-sample style; costs not on page | M (reversal exists at hour scale), L (tradable)`
  This points AGAINST naive continuation at 1-4h horizons in BTC. Shen-Urquhart-Wang 2022 (first half-hour in VOLUME time predicts last
  half-hour) is already in repo as E4: volume time, not a US-open clock anchor. Wen et al. 2022: both momentum and reversal.
- Parameters the literature used (Q2): Gao: window = first 30 min from prior close -> last 30 min (equity regular session). SFI 24-97:
  SPY, dynamic trailing stop, long/short intraday. Zarattini et al.: 5-minute opening range, compared with 15/30/60. Replication: range
  = 09:30-09:35 ET bar, entry 09:35 ET, risk cap 1% per trade, leverage cap 4x. US cash open = 09:30 ET = 13:30 UTC (EDT) or 14:30 UTC
  (EST). For BTC a backtest would copy: range windows 5/15/30/60 min from the US open, entry after the window, breakeven slippage sweep.

### Q3 - Pre-open sweep of prior range then reversal
- Studies of price taking out a prior overnight/Asia/London range high or low shortly before or at an open and then reversing, in FX,
  equity-index futures or crypto: No validated evidence found (no T1/T2 study located; vendor and blog statistics were REJECTED).
- Adjacent mechanism only: FX prices show "extraordinary volatility and negative serial correlation" around the 4:00 pm WMR Fix,
  21 currencies, 10 years (Evans 2018). `T1 | microstructure model + data; abstract only; not a range-sweep test; no costs | M (benchmark-time pressure then reversal exists in FX), L (transfer to BTC opens)`
  Stop-order clusters and hourly stop cascades (Osler 2003/2005), levels as depth peaks (Kavajecz-Odders-White 2004) and bounce
  odds (Chung-Bellotti 2021): already verified in repo (T058); they support the MECHANISM, not a sweep-reversal rule.
  De Nicola 2021 (above): hour-scale reversals after large BTC moves, authors cite liquidation cascades. `T1 | see Q2 | L-M`
- Parameters the literature used (Q3): Evans: 16:00 London-time fix, 21 currency pairs, 10 years (window length around the fix is not
  on the abstract page). No source defines a "prior range" for sweeps; our T058 definitions (C1-C3) remain our own, tested by our own data.

### Q4 - Equity (ES/NQ) to BTC spillover in the US session
- ES/NQ open-period return or overnight futures move predicting BTC direction in the US session, and a time-of-day BTC-equity
  correlation profile: No validated evidence found (no T1/T2 study opened).
- Adjacent: E-mini S&P 500 crash-risk measures (NCSKEW, DUVOL from 5-minute data, aggregated daily) have NO significant
  relationship with BTC futures RETURNS but a positive one with BTC futures VOLATILITY, 2017-12-17..2021-06-30, 884 days, GARCH(1,1)
  (Tang et al. 2024). `T1 | daily aggregation; no OOS; no costs; no time-of-day; pre-ETF | M (volatility link), L (no return link means no direction signal)`
  BTC activity and volatility follow European/US stock-exchange hours (Wang 2020; Eross 2019): this is activity alignment, not a
  direction lead. `T1 | see Q1 | M`
- Parameters the literature used (Q4): none for direction. Tang: 5-minute E-mini data collapsed to daily skewness/volatility-ratio
  measures; GARCH(1,1). A backtest must define its own lead-lag windows (e.g. ES/NQ return from 13:30 UTC open over 5/15/30 min
  vs BTC return after it) with DST handled; this is our design, not copied from literature.

## 4. What this means for test ordering (external ranking only; our backtest decides)
1. Supported (T1, M): BTC volume and volatility are higher in European/US stock hours. Use as a conditioning / stop-width variable,
   not as a direction signal. The single biggest hour found is 16:00-17:00 UTC, after the US open.
2. Not supported: any stable session-of-day DIRECTION edge for BTC (Baur: not persistent). Post-ETF era is an evidence gap.
3. BTC opening-range test at the US cash open is new ground: equity ORB evidence is cost-fragile (replication break-even about one
   spread) and regime-concentrated; BTC evidence at hour scale leans toward reversal (De Nicola). Run it as an event study first.
4. Sweep-then-reversal and ES/NQ-to-BTC lead-lag have no external support; only our own data can rank them.

## 5. DISCARDED (do not research again; source + reason)
- Schmidt & Kraft, "Keeping New York's hours: Bitcoin's intraday clock after the spot ETFs", SSRN 7384239: SSRN returned 403 on three
  routes (papers.ssrn.com, dx.doi.org redirect, ssrn.com); only a search snippet seen, so UNVERIFIED and not relied on. It is the
  best post-ETF candidate: HAND-OPEN it before any Q1 post-2024 work.
- Aalto University thesis "Crypto never sleeps, but humans do. Do regional hours matter for Bitcoin returns?": 403, unreviewed
  thesis, snippet only.
- CME Group Economic Research, "Why is Bitcoin moving in tandem with equities?" (2025): fetch timed out twice; not opened.
- Quantpedia pages on BTC periodicity and BTC overnight sessions: 403 / not opened; T3 summaries of papers.
- Melvin & Prins (2015), London 4pm fix, J. Financial Markets 22:50-72: seen in a search snippet only; not opened.
- arXiv 2512.12815 and 2501.09911 (BTC-equity correlation after ETF/institutional adoption): snippets only; daily data; not opened.
- "Bitcoin's overnight returns forecast the VIX" (aligrithm.com, ccn.com): not opened; wrong direction (BTC to VIX) for Q4.
- tradingstats.net (ORB / overnight-range stats on ES and NQ), chartswatcher, fortraders, trademomentum, warriortrading, a vercel.app
  "NQ ORB study", TradingView scripts: vendor/blog statistics with no method, costs or review. REJECT.
- spendnode.io "9-hour US window", Yahoo Finance and Coin Bureau / TMGM / Mudrex trading-hours pages: marketing, no method. REJECT.
- SSRN pages 4080253 (Wen), 4824172 and 4729284 (Zarattini et al.): 403; replaced by verified alternate pages above (not a rejection of
  the papers, only of those URLs). Springer direct link (Brauneis) redirected to login; econbiz (Wen) blocked by bot wall.
- Hansen-Kim-Kimbrough full PDF: downloaded but no PDF text tool in this environment; hour-by-hour numbers NOT extracted, so none
  are used. Hand-read it if exact hours are needed.
