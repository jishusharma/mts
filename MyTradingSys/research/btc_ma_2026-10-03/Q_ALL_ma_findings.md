# Q_ALL: BTC moving-average evidence, consolidated pass (2026-10-07)

Worker: Sonnet research pass covering briefs sonnet-01 (Q1), sonnet-02 (Q2 definitions + cycle MAs), sonnet-03 (Q3/Q4, partial).
Method: playbook Part I tiers (T1/T2/T3/REJECT). Budget ~25 fetches; ~24 used. Every source below was opened this session
(date 2026-10-07). "verified" = body text read or definition page matched; "abstract only" = only the abstract/metadata page opened,
so method details (costs, OOS split, snooping control) are NOT claimed beyond the abstract.
Lesson: one web-fetch summary of Grobys 2020 invented "costs + OOS"; the PDF text was then read and shows neither. Summaries from
the fetch tool are not evidence; the primary text is. Findings below use the primary text where marked verified.
Not reached (budget, no claim made): Huang et al 2019 JFDS, Shynkevich ~2021, Zarattini et al 2025 SSRN, Q2 adaptive MAs
(KAMA/FRAMA/Hull/ALMA etc.), Q3 detector papers, Q4 factor papers. Those briefs remain open for a follow-up worker.

## 3. Findings

### 3a. Peer-reviewed BTC MA / technical-rule studies

F1. Wei, Kyriakou, Sermpinis, Stasinakis (2024), "Cryptocurrencies and Lucky Factors: The value of technical and fundamental
analysis", Int. J. Finance & Economics 29(4):4073-4104. DOI 10.1002/ijfe.2863. Full text read; verified 2026-10-07.
URL: https://eprints.gla.ac.uk/302711/1/302711.pdf
- Tier T1 | Method quality: high (7,851 technical rules incl. MA rules, 59 fundamental factors, 12 coins; Lucky Factors + Hansen SPA
  snooping control; trading performance computed with average Binance transaction costs; three IS/OOS splits 50/25/10 percent OOS;
  BTC from Bitstamp, in-sample start Aug 2015, OOS ends 5 Mar 2022) | Confidence M (sample ends Mar 2022; no post-ETF data).
- Finding: of the top 15 in-sample technical rules only ONE, the short-horizon log price-to-moving-average ratio (PMA1, 1-week
  average, the Detzel et al. 2021 construct), keeps genuine in-sample profitability after snooping control and positive OOS R2
  across splits and coins; traditional momentum/crossover rules were not robust OOS. Conclusion in the paper: "question the value
  of both technical and fundamental analysis". Caveat for us: costs are an average Binance fee, no funding, spot-style long/flat.

F2. Hudson & Urquhart (2021), "Technical trading and cryptocurrencies", Annals of Operations Research 297(1):191-220.
DOI 10.1007/s10479-019-03357-1. Abstract only (RePEc page); verified 2026-10-07 (abstract only).
URL: https://ideas.repec.org/a/spr/annopr/v297y2021i1d10.1007_s10479-019-03357-1.html
- Tier T1 | Method quality: high on paper (~15,000 rules, five rule classes, multiple-testing data-snooping procedures, breakeven
  costs reported) but internals unread | Confidence M.
- Finding: in-sample significance for every rule class and breakeven costs above typical crypto costs; the abstract states
  there is no predictability for Bitcoin in the out-of-sample period (other coins keep it). This is a direct negative OOS result
  for BTC rule-based trading and conflicts with a naive reading of F4/F5.

F3. Detzel, Liu, Strauss, Zhou, Zhu (2021), "Learning and predictability via technical analysis: Evidence from bitcoin and stocks
with hard-to-value fundamentals", Financial Management 50(1):107-137. DOI 10.1111/fima.12310. Abstract only; verified 2026-10-07
(abstract only). URL: https://profiles.wustl.edu/en/publications/learning-and-predictability-via-technical-analysis-evidence-from-/
- Tier T1 | Method quality: unknown beyond abstract (equilibrium model + predictive regressions + trading strategies) |
  Confidence M-L.
- Finding: ratios of price to moving averages forecast daily BTC returns in and out of sample, and MA-ratio strategies show alpha
  and Sharpe gains over buy-and-hold. Cost treatment, sample end and OOS design NOT confirmed from the abstract. F1 uses this
  paper's ratio and independently finds it to be the one surviving rule, which raises confidence in the ratio (not in crossovers).
- Secondary pointer (T3, working-paper summary by CXO Advisory of SSRN 3115846, Jan 2018, sample 2010-07 to 2017-12, SMA 5/10/20/
  50/100-day, price above SMA = long else cash): gross results only, breakeven frictions 1.1 percent (5d) to 4.5 percent (100d); the
  author-reported caveat is data-snooping. URL: https://www.cxoadvisory.com/currency-trading/timing-bitcoin-with-smas/ verified 2026-10-07
  (secondhand summary; the SSRN page itself returned 403, so numbers are not independently matched).

F4. Gerritsen, Bouri, Ramezanifar, Roubaud (2020), "The profitability of technical trading rules in the Bitcoin market", Finance
Research Letters 34. DOI 10.1016/j.frl.2019.08.011. Abstract only; verified 2026-10-07 (abstract only).
URL: https://ideas.repec.org/a/eee/finlet/v34y2020ics1544612319303770.html
- Tier T1 | Method quality: medium (7 trend-following indicators, daily 2010-07 to 2019-01, bootstrap Sharpe comparison vs buy-and-hold)
  | Confidence L-M (costs/OOS not in abstract).
- Finding: mainly the trading-range BREAKOUT rule (not MA crossovers) has significant forecasting power; sub-periods (normal vs boom)
  broadly agree and breakout is said to outperform in strongly trending markets. This is the only regime-flavoured claim found, and
  it is by sub-period (boom label), not an ex-ante regime filter, and it concerns breakouts, not MAs.

F5. Grobys, Ahmed, Sapkota (2020), "Technical trading rules in the cryptocurrency market", Finance Research Letters 32:101396.
DOI 10.1016/j.frl.2019.101396. Full text read; verified 2026-10-07.
URL: https://osuva.uwasa.fi/bitstream/10024/11192/2/Osuva_%20Grobys_Ahmed_Sapkota_2020.pdf
- Tier T1 | Method quality: low-medium (daily 2016-2018 only, 3 years, 11 coins, long/flat price-vs-MA rule (1, n) with n in 20, 50, 100,
  150, 200 using log prices, SUR joint test; NO transaction costs, NO out-of-sample, NO data-snooping correction) | Confidence L.
- Finding: BTC single-coin payoffs positive for all n, strongest for n=20 and fading as n grows; jointly the (1,20), (1,50), (1,100)
  rules are significant. Joint-test excess return 8.76 percent p.a. is for the ten non-BTC coins ((1,20), vs 36.87 percent buy-and-hold).
  In-sample evidence only; the 2016-2018 window is one bull run.

F6. Corbet, Eraslan, Lucey, Sensoy (2019), "The effectiveness of technical trading rules in cryptocurrency markets", Finance Research
Letters 31:32-37. DOI 10.1016/j.frl.2019.04.027. Abstract only; verified 2026-10-07 (abstract only).
URL: https://ideas.repec.org/a/eee/finlet/v31y2019icp32-37.html
- Tier T1 | Method quality: unknown (high-frequency BTC returns; MA-oscillator and range-breakout rules) | Confidence L.
- Finding: the variable-length MA rule performs best, buy signals earn more than sell signals. Sample, costs and OOS not stated in the
  abstract page. No validated net-of-cost claim can be made from it.

F7. Resta, Pagnottoni, De Giuli (2020), "Technical Analysis on the Bitcoin Market: Trading Opportunities or Investors' Pitfall?",
Risks 8(2):44. DOI 10.3390/risks8020044. Abstract only; verified 2026-10-07 (abstract only).
URL: https://ideas.repec.org/a/gam/jrisks/v8y2020i2p44-d354452.html
- Tier T1 (MDPI, peer-reviewed; lower prestige) | Method quality: unknown beyond abstract (5-min vs daily, 2012-01 to 2019-08) |
  Confidence L.
- Finding: daily trading is more profitable than intraday, simple MAs do best on daily data, and buy-and-hold beats the tested
  strategies intraday. Supports the prior that intraday MA rules are fee-limited; no cost/OOS detail confirmed.

F8. Zakamulin & Giner (2020), "Trend following with momentum versus moving averages: a tale of differences", Quantitative Finance
20(6):985-1007. DOI 10.1080/14697688.2020.1716057. Abstract only; verified 2026-10-07 (abstract only).
URL: https://ideas.repec.org/a/taf/quantf/v20y2020i6p985-1007.html
- Tier T1 | Method quality: theoretical + stock-price data, NOT Bitcoin | Confidence H for what it says, N/A for BTC.
- Finding: MA rules give more robust trend-direction forecasts than momentum rules in their framework. Not BTC evidence; kept only
  as method background for MA-vs-momentum. Zakamulin & Giner BTC-specific or regime-switching results were not found in a
  Bitcoin-specific paper in this pass ("No validated evidence found" for their BTC regime claims).

### 3b. Recent OOS test including the post-ETF period

F9. Islas Anguiano & Garcia-Medina (2025), "Technical Analysis Meets Machine Learning: Bitcoin Evidence", arXiv:2511.00665
(preprint, not peer reviewed; submitted to Computational Economics). Full text read; verified 2026-10-07.
URL: https://arxiv.org/pdf/2511.00665
- Tier T2 | Method quality: low-medium (Binance daily BTC; train 2021-01 to 2024-01-09, test 2024-01-10 to 2024-12-31; EMA cross
  6/95 and MACD+ADX chosen by grid on training cumulative return; 0.1 percent fee per trade; no snooping control; one test year) |
  Confidence L.
- Finding (test year, net of 0.1 percent fee): buy-and-hold 42.31 percent, EMA 6/95 25.27 percent (8 trades), MACD+ADX 34.45
  percent (14 trades), LSTM 53.23 percent (120 trades), LightGBM 39.78 percent. Plain trend rules lagged buy-and-hold in a strong
  post-ETF up year; no risk-adjusted metric given. n=1 year, so "anecdote".

### 3c. Definitions table (T3, definitions only, no performance claim accepted)

| MA state | Formula as stated | Originator as stated | Tier | Source (verified 2026-10-07) |
|---|---|---|---|---|
| Mayer Multiple | price / 200-day SMA; folklore levels 2.4 (overbought) and 0.8 (oversold) | Trace Mayer (as credited by TradingView scripts) | T3 | https://br.tradingview.com/scripts/mayermultiple |
| Pi Cycle Top | 111-day MA crossing above 2 x 350-day MA = top signal (350/111 = 3.153, near pi) | Philip Swift (script posted 2021-02-28) | T3 | https://it.tradingview.com/script/elqHbZ9a-Pi-Cycle-Top-Indicator |
| 200-week MA | simple average of last 200 weekly closes (about 3.8 years, 1400 days) | no originator named on page | T3 (vendor education, dated 2026-06-02) | https://www.bit.com/knowledge-hub/200-wma |
| PMA(L) | log price minus equal-weight average of log price over L weeks, L in 1, 2, 4, 10, 20 | Detzel et al 2021, simplified in Wei et al 2024 | T1 (via F1) | see F1 |

Cycle-signal evidence status: the Mayer 2.4 / 0.8 levels, the Pi Cycle crossing and 200W-as-bottom are descriptions of past peaks and
troughs. The pages give no costs, no OOS split and no rule test; BTC has had about four cycles, so these are "anecdote, n<=4". Our own
data (section 4b) shows the Pi Cycle crossing twice in 2021-04 (n=1 cycle) and the 200W SMA has only 152 valid weeks. Vendor page
also admits price did go below the 200W MA in 2022. Confidence L for any use as a signal.

## 5. Answer

Q-A. Which MA setups have OOS, net-of-cost evidence on BTC?
- Only one is supported by an independent peer-reviewed test with snooping control AND OOS AND costs: the short-horizon (about 1-week)
  log price-to-MA ratio, F1 (T1, Confidence M), with F3 (abstract only) as the originating study. Sample ends Mar 2022; no funding;
  long/flat; costs are an average Binance fee. Not tested post-ETF.
- Counter-evidence: Hudson & Urquhart report no BTC predictability OOS (F2, abstract only); the 2024 single-year test (F9, T2) shows
  EMA 6/95 trailing buy-and-hold net of 0.1 percent fees. Classic crossovers (50/200, EMA 9/21) and VMA lengths: "No validated
  evidence found" (F5 is in-sample, costless, 3 years; F6/F7/F4 are abstract only).
- Regime (trending vs ranging): "No validated evidence found" of an ex-ante regime filter that improves an MA rule net of costs. The
  only regime-flavoured item is F4 (breakout rule better in strongly trending sub-periods, defined by a boom label, abstract only).
  Statement that MA rules work when trending and fail when ranging is folklore at our bar.
- Folklore (no testable evidence): 50/200 golden/death cross (12 events in our data, 4 OOS), Pi Cycle (n=1 cycle in our data), Mayer
  2.4/0.8 thresholds, 200W MA as bottom, "secret" adaptive MAs (not researched this pass, still unvalidated).

Q-B. MA states worth SHOWING in an observation guide (display only, no signal weight):
1. 1d close vs SMA200 (and SMA50, SMA20): the 20/50/100 lengths are the Grobys grid; 200 is the standard long reference.
2. Mayer Multiple = close / SMA200d as a distance gauge, labelled folklore; show 2.4/0.8 as "popular levels" with source T3 only.
3. PMA(L): ln(close) minus mean(ln close) over L weeks for L = 1 (and 2, 4), the only construct with T1 OOS support (F1/F3), plotted
   as a signed state (above/below zero), tagged "T1, sample to 2022".
4. 200W SMA as slow context line only, marked data-limited (152 valid weeks in our series). Pi Cycle: optional, labelled anecdote n=1.
Do not present any as a trading signal.

Q-C. Worth BACKTESTING next (design against section 4 data coverage; separate layer, never a Tom filter):
- Evaluator: position-series test (section 4d item 2), signal at close t holds t->t+1, long/flat, fee + slippage on every change,
  funding per 8h only after B103 fetch (funding history 2020-01.. needed; present data only 2025-09..), Sharpe/DSR/PBO vs
  buy-and-hold, run_t055 template (70/30 split, IS-only grid, PBO < 0.5, >= 2 OOS years). The last 30 percent of 2020-01..2026-09 is
  about 2024-09 onward, so OOS is post-ETF only; pre-ETF robustness comes from walk-forward folds, with subperiods 2020-2023 and 2024+.
- T1. PMA(L), L in {1, 2, 4, 10, 20} weeks, sign rule, 1d bars: replicates F1's single survivor on a newer sample (2022-2026). The
  hypothesis is fixed before running: PMA1 outperforms the other L values net of costs. Smallest grid, lowest snooping risk.
- T2. close vs SMA(n), n in {20, 50, 100, 200} (Grobys grid), same evaluator; 100/200 fail the event gate (24/18 OOS events), so
  judge by position-series Sharpe and the buy-and-hold comparison, not event count.
- T3. EMA 9/21 on 4h/1h only if the fee floor is cleared by T1/T2 results; skip golden cross and Pi Cycle (event counts 12/2).
- Regime test (Q3) only after PMA/SMA baselines exist: split their daily returns by ex-ante labels (efficiency ratio, realised-vol
  tercile, Fabio balance on 1d) and test the difference by bootstrap; label must use data up to bar t only.
- Out of scope until data exists: 200W, Mayer thresholds and Pi Cycle as signals (spot 1d from 2017-08 and pre-2017 source needed;
  n<10 even then).

## 6. REJECT list

| Item | Reason |
|---|---|
| Corbet 2019 / Gerritsen 2020 / Resta 2020 / Detzel 2021 / Hudson 2021 internals (costs, OOS dates, snooping details) | Only abstract pages opened; the unread details are not cited. The papers themselves stay T1 pointers, abstract-only. |
| Grobys 2020 as net-of-cost or OOS evidence | Full text: no costs, no OOS, no snooping control, 2016-2018 only. REJECT as validation, kept as in-sample pointer (F5). |
| Fetch-tool summary of Grobys saying costs/OOS were applied | Contradicted by the PDF text. REJECT; do not reuse. |
| SSRN 3115846 numbers (breakevens 1.1-4.5 pct) | SSRN 403; known only via CXO Advisory summary (T3 secondhand). Not used for conclusions. |
| Quantpedia "Revisiting Trend-following and Mean-reversion Strategies in Bitcoin" | Opened, but it tests MAX/MIN lookbacks (10-50 days), not MAs; pointer only, no original paper cited. Out of scope. |
| Zakamulin & Giner 2020 as BTC evidence | Equity data; no BTC test. Kept as method note only (F8). |
| woobull Mayer chart (526), newhedge Pi Cycle (403), BitMEX Pi Cycle blog (fetch failed), Hull repository PDF of Hudson (403), uia.brage Zakamulin (host not found), Springer Hudson full text (login redirect) | Unopenable. Per rule: cannot open = REJECT as citations; definitions used the TradingView / BIT pages instead. |
| "Pi Cycle accurate to within 3 days", "200W marks every bottom", "Mayer 2.4 = bubble" claims in search snippets | Marketing/vendor prose, no costs, no test, n<=4 cycles. REJECT as evidence; kept only as definitions. |
| Unattempted leads: Huang 2019, Shynkevich 2021, Zarattini 2025, Ellis & Parbery 2005, Kaufman/Ehlers/Hull/ALMA/KAMA adaptive MA comparisons, Q3/Q4 detector and factor papers | Not opened this pass. "No validated evidence found" for adaptive-vs-simple MA superiority on BTC; follow-up worker needed. |
