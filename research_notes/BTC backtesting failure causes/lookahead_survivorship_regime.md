# Look-ahead bias, survivorship bias, non-stationarity / regime change, and backtest-period selection as causes of backtest failure (asset-agnostic)

Scope note: general, not crypto-specific. Source type and date are given in brackets. Many hits were secondary summaries (search snippets, vendor blogs, study aids). Where a figure comes only from a secondary source, it is flagged as such. I could not open several primary PDFs (the fetch tool returned undecoded binary), so a few headline numbers are second-hand. They are marked.

## 1. Look-ahead bias: what it is, and documented examples of it inflating backtests

### Takeaway
Look-ahead bias means the backtest uses information that did not exist, or was not public, at decision time. The documented mechanisms are:
- database backfilling (Compustat);
- restated or re-standardised fundamentals overwriting the as-reported values;
- revised macro data (GDP vintages);
- filing/reporting lags ignored;
- using today's index membership as the historical universe.

The best-documented academic case is Banz & Breen (1986): portfolio returns differ significantly depending on whether a look-ahead-free database is used. Peer-reviewed estimates of the return inflation from restatements alone are scarce.

### Cited Findings
- **Banz & Breen (1986), *Journal of Finance* 41(4):779-793** [peer-reviewed, 1986]:
  - Studies combining accounting and price data via Compustat or the related PDE database "may introduce a look-ahead bias and an ex-post-selection bias".
  - Rates of return from portfolios chosen on accounting data differ *significantly* between Compustat and a database free of both biases.
  - The authors propose remedies for use with standard Compustat.
  - Source: [AFA JoF vol 41 issue 4 listing / search summary](https://afajof.org/issue/volume-41-issue-4/). I saw only the abstract-level summary, not the full text.
- **Compustat backfill mechanism** [arXiv preprint, 2020]: firms are added to Compustat after operating viably for some years and arrive *with multiple years of historical accounting data*. Firms that fail early never enter the database. So a backtest "sees" a firm's history only because the firm later survived. This is look-ahead and survivorship combined. — [arXiv 2001.08240](https://arxiv.org/pdf/2001.08240)
- **Kothari, Shanken & Sloan selection-bias critique of book-to-market tests** [peer-reviewed, 1995; Kellogg page]: Compustat selection bias was argued to inflate the measured book-to-market effect. — [Kellogg: "On Selection Biases in Book-to-Market Based Tests"](https://www.kellogg.northwestern.edu/academics-research/research/detail/1995/on-selection-biases-in-book-to-market-based-tests/). Title and topic only; I did not retrieve the magnitudes.
- **Lyle, Siano & Yohn (2024)** [academic working paper, 2024]:
  - Compustat's *re-standardisation* of its products introduces a form of look-ahead bias, because historical data are altered after the fact.
  - Using Compustat Snapshot (point-in-time) data, standardisations "significantly alter key financial figures such as sales and earnings", which complicates replication. — [Columbia ADP PDF](https://business.columbia.edu/sites/default/files-efs/imce-uploads/ADP/Fall%202024/Lyle%20Siano%20Yohn%202024.pdf); [Yale SOM version](https://som.yale.edu/sites/default/files/2024-07/Re-Standardized%20Financial%20Statement%20Data.pdf)
  - Related: UNC note on the Compustat Snapshot product — [UNC Kenan-Flagler](https://kenanflaglerresearchtools.web.unc.edu/research-resource/compustat-snapshot/)
- **Macro data revisions (real-time data)** [Philadelphia Fed working papers / Journal of Econometrics 2001 / Journal of Macroeconomics 2002 / handbook chapters 2005, 2010]:
  - Croushore & Stark built quarterly "vintage" snapshots of US macro data so that a modeller can see what was known at each past date.
  - Forecasting experiments using latest-revised data instead of real-time data "may be misleading" about forecast accuracy, and revisions affect model selection. — [Philadelphia Fed WP 99-15](https://www.philadelphiafed.org/-/media/frbp/assets/working-papers/1999/wp99-15.pdf); [Croushore, "Forecasting with Real-Time Macroeconomic Data" (Richmond)](https://scholarship.richmond.edu/economics-faculty-publications/24/); [Croushore handbook chapter PDF](https://facultystaff.richmond.edu/~dcrousho/docs/hef_croushore.pdf)
- **Restatement overwriting** [vendor blog, c. 2025, illustrative only]:
  - Most databases overwrite history when a restatement occurs. The restated value then carries the original filing date, information that did not exist on that date.
  - One vendor reports that re-running its own backtest with current (restated) scores inflated CAGR by **7.29 percentage points** for one strategy and **5.09 pp** for another. This is a single self-run test, not a general finding.
  - The same vendor measured an average **~43-day lag** between fiscal period end and public filing in its sample. A backtest that keys fundamentals to period-end dates looks ahead by about that much. — [DEV Community / tradevodata: lookahead bias in fundamental data](https://dev.to/tradevodata/your-backtest-saw-the-future-lookahead-bias-in-fundamental-data-measured-across-313562-rows-4cba); [as-reported vs restated](https://dev.to/tradevodata/as-reported-vs-restated-financial-data-why-the-difference-matters-for-backtesting-1big)
- **Point-in-time data rationale** [industry research blog]: Glassnode notes that the restatement effect is distinct from timing lag and is concentrated in entities whose numbers were later corrected. — [Glassnode: "Your Backtest Is Lying: Why You Must Use Point-in-Time Data"](https://research.glassnode.com/why-use-point-in-time-data/)
- **"Preinclusion bias"** [arXiv, 2025]:
  - Using *today's* S&P 500 members as the historical universe is a form of look-ahead bias: future index membership shapes past decisions.
  - The paper cites an academic estimate of **0.1%-0.9% per year** return distortion. — [arXiv 2505.07078](https://arxiv.org/pdf/2505.07078)
  - Unsourced practitioner claims of 1-2% per year exist ([QuantConnect forum](https://www.quantconnect.com/forum/discussion/21226/would-you-pay-for-cheap-point-in-time-s-amp-p-500-data-survivorship-bias-free/); [fffinstill](https://fffinstill.com/learning/concepts/backtesting-methodology)). Prefer the cited 0.1-0.9%.
- **CFA curriculum-style guidance** [study notes]: use a point-in-time approach when vendor data allows it. — [AnalystPrep: Problems in Backtesting](https://analystprep.com/study-notes/?p=22822)

### Inferences
- Look-ahead bias rarely appears as an obvious "peek". It usually enters through the *data source*: backfilled histories, overwritten restatements, revised macro series, unlagged fundamentals, and current-constituent universes. A clean-looking backtest on a standard vendor dataset can still be contaminated.
- Intrabar/end-of-bar look-ahead is mechanically the same error at high frequency. Examples:
  - deciding on a bar's close, high or low and filling at a price inside that same bar;
  - using a daily close to trigger a trade "at the open" of the same day.
  It is widely described in practitioner material but I found no peer-reviewed quantification (see Gaps).
- The effects compound with survivorship bias. Backfilling only survivors (Compustat) is both biases at once.

### Gaps
- No peer-reviewed study found that quantifies the average return inflation from fundamental *restatements* alone. The evidence is mechanism plus vendor examples.
- No academic quantification found for intrabar/end-of-bar look-ahead (for example, same-bar close-to-fill). Only practitioner explainers.
- The magnitudes in Banz & Breen (1986) and Kothari-Shanken-Sloan (1995) were not retrieved, so only the qualitative "significant difference" is confirmed.
- I could not retrieve the size of forecast changes in the Stark-Croushore experiments.

## 2. Survivorship bias: what it is, and how large the documented effect on returns is

### Takeaway
Testing only on assets or funds that still exist removes the failures, whose exit is usually performance-driven. Documented magnitudes:

| Setting | Bias | Status |
|---|---|---|
| US mutual funds | ~0.9%/yr (Elton-Gruber-Blake 1996) | secondary source |
| Hedge-fund databases | ~2-3%/yr survivorship (Fung-Hsieh 2000; Liang 2000) | secondary sources |
| Hedge-fund backfill | ~1%/yr, up to 7.3%/yr (Malkiel-Saha 2005) | secondary sources |
| Equity databases (CRSP delisting returns) | missing delisting returns are large and negative; corrections of -30% (NYSE/Amex) and -55% (Nasdaq); the correction erased the Nasdaq size effect | see Cited Findings |

### Cited Findings
- **Elton, Gruber & Blake (1996), "Survivorship Bias and Mutual Fund Performance", *Review of Financial Studies* 9(4):1097-1120** [peer-reviewed, 1996]:
  - Tracks all funds in Wiesenberger's 1977 directory from 1976 to 1993.
  - Funds that disappear tend to do so because of poor performance. — [IDEAS/RePEc](https://ideas.repec.org/a/oup/rfinst/v9y1996i4p1097-1120.html); [NYU archive](https://archive.nyu.edu/handle/2451/27234)
  - Headline estimate of **0.9% per annum** (surviving-fund alpha minus all-fund alpha). Taken from a Wikipedia mirror, not the original. — [Survivorship bias (Wikipedia mirror)](https://wikipedia.classicistranieri.com/en/articles/s/u/r/Survivorship_bias.html). **Unverified against the paper.**
- **Carhart (1997 working paper) and Carhart, Carpenter, Lynch & Musto (2002)** [peer-reviewed, RFS 2002]: these are the standard follow-ups on mutual fund survivorship, and they discuss how the bias grows with sample length. — [Carhart 1997 "Mutual Fund Survivorship" PDF](https://www.evidenceinvestor.com/wp-content/uploads/2016/08/Mutual-Fund-Survivorship-Mark-M.-Carhart-May-1997.pdf); [Carhart-Carpenter-Lynch-Musto PDF](https://pages.stern.nyu.edu/~jcarpen0/pdfs/CarhartCarpenterLynchMusto.pdf). I could not extract their numeric estimates (see Gaps).
- **Hedge fund databases** [peer-reviewed originals, cited via secondary sources]:
  - Fung & Hsieh (2000): survivorship bias **~3% per year** (TASS, 1994-1998), consistent with Brown, Goetzmann & Ibbotson's ~3%.
  - Liang (2000): **~2.24% per year**.
  - Another sample (1994-2010): **1.91%**. — [Scribd copy of SSRN 1581559 (survey)](https://www.scribd.com/document/511144361/SSRN-id1581559); [EFMA 2006 paper](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2006-Madrid/papers/816799_full.pdf); [ZHAW thesis](https://srv-clst-301-data66.zhaw.ch/bitstream/11475/97/1/1841884028.pdf)
- **Backfill (instant-history) bias in hedge fund databases** [secondary summaries]:
  - Average about **1% per year** (one study of 1994-2006: 1.04%/yr).
  - Malkiel & Saha (2005): backfilled minus non-backfilled returns averaged **7.3% per year**.
  - Posthuma & van der Sluis (2003): higher, and consistent across styles. — [EFMA 2006 paper](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2006-Madrid/papers/816799_full.pdf); [Brown (NYU) online appendix](https://pages.stern.nyu.edu/~sbrown/online_appendix.pdf); [Unicatt PhD thesis](https://publicatt.unicatt.it/retrieve/da7bd7d8-481f-4e6c-a18c-368d85e99f18/01frontespizio_tesiphd_Dongmo.Guefack.pdf)
  - Estimates vary widely by database and method.
- **Shumway (1997), "The Delisting Bias in CRSP Data", *Journal of Finance* 52(1):327-340** [peer-reviewed, 1997]:
  - CRSP omits many delisting returns. Delistings for bankruptcy and other negative reasons are mostly surprises.
  - Correct delisting returns are unavailable for most negative delistings since 1962, and the omitted returns are large. — [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:52:y:1997:i:1:p:327-40)
  - Standard practice imputes **-30%** for missing performance-related NYSE/Amex delisting returns. — [SAFE Frankfurt CRSP data description (2025)](https://datacenter.safe-frankfurt.de/documents/Data_Description_CRSP_Shumway_20250317.pdf)
- **Shumway & Warther (1999)** [peer-reviewed, JF 1999]:
  - Delisted Nasdaq stocks' missing returns are large and negative. A corrected return of **-55%** fixes the bias.
  - After the correction, **there is no evidence of a Nasdaq size effect**. This is a concrete case of an "anomaly" created by survivorship/delisting bias.
  - Performance-related delistings (bankruptcy, failing capital requirements) are missed far more often than neutral or good ones (mergers). — [SUFE newsletter summary](https://academicnewsletter.sufe.edu.cn/info/361673); [SAFE data description](https://datacenter.safe-frankfurt.de/documents/Data_Description_CRSP_Shumway_20250317.pdf)
- **Index constituent survivorship** [practitioner sources]:
  - Backtesting "all S&P 500 stocks" with today's list never trades removed or failed members.
  - Roughly a third to half of the index turns over per decade (practitioner claim). — [DEV Community: survivorship vs lookahead](https://dev.to/tradevodata/survivorship-bias-vs-lookahead-bias-the-two-silent-backtest-killers-pmm); [ABC Trading Group](https://www.abctradinggroup.com/backtesting-pitfalls/)

### Inferences
- Survivorship bias is not a constant haircut:
  - it grows with sample length, because more failures are excluded;
  - it is largest where attrition is high and performance-driven (hedge funds, small caps, Nasdaq);
  - it can *create* apparent anomalies outright (the Nasdaq size effect).
- Strategies that buy losers, distressed names, small caps or "cheap" assets are the most exposed. The excluded failures are exactly the names such strategies would have bought.
- For any universe with venue or listing churn (exchanges, delisted instruments, merged funds), the same logic applies at the venue level: testing only on venues that still exist is survivorship bias. This is an inference by analogy; I found no venue-level study in scope.

### Gaps
- I could not confirm the 0.9% EGB figure, or extract Carhart et al.'s estimates, from the primary PDFs: the fetch returned compressed binary.
- The often-quoted Malkiel (1995) mutual-fund survivorship estimate was not found in the searches, so it is omitted.
- No primary peer-reviewed figure was retrieved for current-constituent (index) survivorship beyond the arXiv-cited 0.1-0.9%/yr.

## 3. Non-stationarity and regime change: why relationships that held in one period break down later

### Takeaway
Return-generating processes are not stationary. Volatility, correlations, factor premia and strategy payoffs shift with:
- macro regimes (inflation, rates);
- crises and "panic" states;
- arbitrage after publication.

Documented examples:
- McLean & Pontiff (2016): anomaly returns are 26% lower out-of-sample and 58% lower post-publication.
- Momentum crashes in 1932 and 2009.
- The stock-bond correlation flipped sign (+0.18 over 1926-1999, -0.2 over 2000-2022, positive again in 2022).
- The value factor's ~55% drawdown from 2007 to mid-2020.
- Technical trading rules lost power after the mid-1980s.
- Hamilton-style Markov switching models formalise the regime idea.

### Cited Findings
- **McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", *Journal of Finance*** [peer-reviewed, 2016]. Studies 97 published predictors:
  - Portfolio returns are **26% lower out-of-sample** (pre-publication, outside the original sample). The authors treat this as an *upper bound on data-mining effects*.
  - Returns are **58% lower post-publication**. That implies roughly **32% (58-26) from publication-informed trading**, i.e. arbitrage.
  - Declines are larger for predictors with higher in-sample returns. — [Counterpoint Funds PDF of paper](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf); [gwern mirror](https://Www.Gwern.net/doc/economics/2016-mclean.pdf); [ThinkAdvisor coverage (2016)](https://www.thinkadvisor.com/2016/02/09/markets-dont-work-as-well-as-we-thought/); [CXO Advisory](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation)
- **Daniel & Moskowitz, "Momentum Crashes"** [working paper 2011 (NBER w20439); *Journal of Financial Economics* 2016]:
  - In 1927-2013 US data, the two worst months for winner-minus-loser decile momentum were **July-August 1932**: losers +232% vs winners +32%.
  - In **March-May 2009**, losers rose +163% vs winners +8%.
  - Crashes occur in "panic" states: after market declines, with high volatility, coinciding with sharp rebounds. Losers carry option-like payoffs and large negative-beta exposure after declines. — [NBER w20439](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf); [Columbia PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf); [Alpha Architect: avoiding momentum crashes](https://alphaarchitect.com/avoiding-momentum-crashes/)
  - Alpha Architect cites a ~91% momentum-portfolio loss from June to August 1932. This is a different measure from the decile returns above.
- **Stock-bond correlation regime** [peer-reviewed FAJ 2024 + practitioner commentary]:
  - Monthly US stock-bond correlation was **+0.18 over 1926-1999** and **-0.2 over Jan 2000-Nov 2022**.
  - 2022 was the first year in which both the S&P 500 (-18.1%) and long-term Treasuries (-26.1%) had double-digit declines.
  - Molenaar, Sénéchal, Swinkels & Wang, "Empirical Evidence on the Stock-Bond Correlation", *FAJ* 80(3), 2024 (US data back to 1875): inflation, real rates and government creditworthiness explain the correlation. — [EUR Pure](https://pure.eur.nl/en/publications/empirical-evidence-on-the-stock-bond-correlation/); [RePEc](https://econpapers.repec.org/RePEc:taf:ufajxx:v:80:y:2024:i:3:p:17-36); [Alpha Architect](https://alphaarchitect.com/stock-bond-correlation/); [WealthManagement](https://www.wealthmanagement.com/equities/implications-of-regime-shifting-stock-and-bond-correlations)
  - A backtest of a 60/40 or risk-parity design calibrated on 2000-2021 assumed a hedge that did not exist in other regimes.
- **Value factor drawdown: Arnott, Harvey, Kalesnik & Linnainmaa (2021), "Reports of Value's Death May Be Greatly Exaggerated", *FAJ* 77(1):44-67** [peer-reviewed, 2021]:
  - HML (Fama-French value) had a **55% drawdown from 2007 through mid-2020**.
  - The whole drawdown is explained by the valuation spread moving from the top quartile (2007) to the bottom percentile (June 2020), plus book-to-price missing intangibles.
  - A real regime of a decade-plus can make a long-documented premium look dead. — [RePEc](https://econpapers.repec.org/RePEc:taf:ufajxx:v:77:y:2021:i:1:p:44-67); [Duke Scholars](https://scholars.duke.edu/publication/1472748)
- **Sullivan, Timmermann & White (1999), "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap", *Journal of Finance* 54(5):1647-1691** [peer-reviewed, 1999]:
  - Applies White's Reality Check to a universe of **7,846** technical rules on ~100 years of daily DJIA data.
  - A later review summarises that the rules lost predictive power for major US indices after the mid-1980s. Another summary says no simple rule was profitable for DJIA, S&P 500 or S&P futures. The two summaries differ in emphasis. — [Paper PDF (kevinsheppard.com)](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf); [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:54:y:1999:i:5:p:1647-1691); [core.ac.uk follow-up](https://core.ac.uk/download/37964017.pdf); [HKU review](https://hub.hku.hk/bitstream/10722/141768/1/content.pdf?accept=1)
- **Hamilton (1989), "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle", *Econometrica* 57(2):357-384** [peer-reviewed, 1989]:
  - Autoregression parameters follow a discrete-state Markov chain, so the series' growth rate switches occasionally between regimes.
  - Applied to postwar US real GNP, the switch from expansion to recession serves as an objective recession dating. A typical recession implies a ~3% permanent drop in GNP level. — [RePEc](https://econpapers.repec.org/RePEc:ecm:emetrp:v:57:y:1989:i:2:p:357-84); [statsmodels replication](https://www.statsmodels.org/dev/examples/notebooks/generated/markov_autoregression.html)
  - Caveat from later work: maximum-likelihood regime estimates depend on the **sample period and starting values**, and a three-regime model was more robust for GNP. The regime models themselves are fragile. — [Fed IFDP 681 (2000)](https://webarchive.library.unt.edu/eot2008/20090119105617/http:/www.federalreserve.gov/pubs/ifdp/2000/681/ifdp681.pdf); [SNDE article](https://scholar.lib.vt.edu/ejournals/SNDE/001/articles/v1n1005.pdf)

### Inferences
- Three distinct mechanisms produce "it worked, then stopped":
  1. **Statistical (overfitting)**: the in-sample edge was partly noise. McLean-Pontiff's 26% is an upper bound on this.
  2. **Adaptive markets / crowding**: the edge is arbitraged away once known. This is McLean-Pontiff's ~32% publication effect.
  3. **True regime change**: the economic drivers shift (inflation regime, stock-bond correlation, valuation-spread cycles, panic states for momentum).
- A backtest cannot tell these apart from returns alone.
- Regime dependence also means a backtest period dominated by one regime yields parameter estimates (volatility, correlation, hedge ratios) that are wrong for the next one. Long, multi-regime samples matter more than many trades within a single regime.

### Gaps
- No primary study retrieved on regime shifts in **volume/liquidity patterns** specifically (for example, intraday volume-profile changes after market-structure shifts).
- I did not retrieve specific numbers on alpha decay over calendar time for a broad strategy set beyond McLean-Pontiff. Quantpedia and AQR pieces on factor decay were not fetched.

## 4. Data snooping and selection of the backtest period itself (cherry-picking start/end dates)

### Takeaway
Choosing among many strategy variants, including variants that differ only in the backtest window, inflates the best in-sample Sharpe ratio even when the true Sharpe is zero. Examples:
- After only ~7 configurations, a 2-year backtest with Sharpe >1 is *expected* when the true out-of-sample Sharpe is 0 (Bailey et al. 2014).
- Harvey-Liu-Zhu (2016) argue a new factor needs t > ~3.0, not 2.0, given hundreds of factors tested.
- White's Reality Check (Sullivan-Timmermann-White 1999) is the classic correction for searching a universe of rules.

Start and end dates are an unreported degree of freedom in this search.

### Cited Findings
- **Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance", *Notices of the AMS* 61(5):458-471** [peer-reviewed, 2014; preprint Sept 2013]:
  - High backtest performance is easily achievable after trying a relatively small number of configurations. The more configurations tried, the higher the probability of overfit.
  - They define a **Minimum Backtest Length (MinBTL)** required for a given number of trials.
  - Example: after only **7 configurations**, a researcher is *expected* to find at least one **2-year backtest with annualised Sharpe > 1** when the expected out-of-sample Sharpe is **0**.
  - Standard hold-out is inadequate because it does not control for the number of trials. — [WMU ScholarWorks](https://scholarworks.wmich.edu/math_pubs/40/); [author PDF](https://carmamaths.org/jon/backtest.pdf); [lecture notes](https://cs.runi.ac.il/~kipnis/notes/STATS_207_L18.pdf); [EurekAlert release](https://www.eurekalert.org/news-releases/817304)
- **Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns", *Review of Financial Studies* 29(1):5-68** (NBER w20592, 2014) [peer-reviewed]:
  - Given multiple testing across hundreds of proposed factors, a new factor should clear **t ≈ 3.0**, not 2.0. — [NBER w20592](https://www.nber.org/papers/w20592); [RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.)
  - "At least 316 factors tested" comes from a study-aid summary, not verified against the paper. — [Brainscape flashcards](https://www.brainscape.com/flashcards/12886732/packs/21266483)
- **Sullivan, Timmermann & White (1999)** (see §3): evaluating the best of **7,846** rules without adjusting for the search overstates significance. The White Reality Check bootstrap adjusts for the full rule universe. — [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:54:y:1999:i:5:p:1647-1691)
- **McLean & Pontiff (2016)**: the 26% out-of-sample decline is an upper bound on data mining, including choice of sample period, across 97 published anomalies. — [paper PDF](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf)
- **Regime-model sample dependence**: Markov-switching estimates depend on the sample period. Fitting a "regime" model is itself subject to period selection. — [Fed IFDP 681](https://webarchive.library.unt.edu/eot2008/20090119105617/http:/www.federalreserve.gov/pubs/ifdp/2000/681/ifdp681.pdf)
- **Practitioner taxonomy (Robert Carver)** [CMT webcast 2021; workshop 2026]: three types of overfitting, "the one everyone has heard of, another you do but don't admit to, and one you may not even realize you are doing". A summary of his book *Systematic Trading* (2015) gives the example of testing 200 parameter combinations, keeping the 10 profitable ones, and building a strategy on them. — [CMT Association (2021)](https://cmtassociation.org/?p=76417); [WBS Training workshop](https://www.wbstraining.com/?p=15809); [wikidocs reading notes on Systematic Trading](https://wikidocs.net/blog/@systrader79/18757/) (secondary notes)

### Inferences
- Start and end dates are hidden trials. A window that starts at a market trough or ends before a crash (for momentum, before 1932 or 2009; for bond-hedged portfolios, before 2022) can turn a mediocre rule into a strong one. Every window tried should count toward the trial count in MinBTL, Deflated-Sharpe and Reality Check corrections.
- Short backtests are especially vulnerable. MinBTL implies the required length grows with the number of variants tried. A 2-year window is near-worthless after even a handful of trials.
- Regime concentration interacts with period selection. A window inside one regime (2000-2021 negative stock-bond correlation; 2009-2020 growth-over-value) both cherry-picks and hides non-stationarity.

### Gaps
- No peer-reviewed study retrieved that isolates start/end-date choice as a separate source of bias with a numeric effect. The point is implied by the multiple-testing literature above.
- The MinBTL formula itself was not retrieved (paper PDF not parsed).
- Carver's own blog (qoppac.blogspot.com) posts on minimum data length and regimes were not retrieved. Only secondary notes on his views were found.

## 5. Practitioner and academic mitigations for each bias

### Takeaway
- **Look-ahead**: point-in-time ("as-reported", vintage) data with as-of timestamps, plus explicit reporting lags.
- **Survivorship**: survivorship-free universes, including dead and delisted assets with correct delisting returns (Shumway imputations), and point-in-time index membership.
- **Snooping / period selection**: count all trials and apply multiple-testing corrections (t > 3, Reality Check, MinBTL/deflated Sharpe).
- **Regime change**: long multi-regime samples, sub-period and crisis-state analysis, explicit regime or state models (used cautiously), and expect post-discovery decay.

### Cited Findings
- **Look-ahead**:
  - Use point-in-time/as-reported data with "as-of" timestamps that preserve the original value alongside restatements. — [Glassnode](https://research.glassnode.com/why-use-point-in-time-data/); [AnalystPrep](https://analystprep.com/study-notes/?p=22822); [DEV Community](https://dev.to/tradevodata/as-reported-vs-restated-financial-data-why-the-difference-matters-for-backtesting-1big)
  - Use Compustat Snapshot rather than restated Compustat. — [Lyle, Siano & Yohn 2024](https://business.columbia.edu/sites/default/files-efs/imce-uploads/ADP/Fall%202024/Lyle%20Siano%20Yohn%202024.pdf); [UNC](https://kenanflaglerresearchtools.web.unc.edu/research-resource/compustat-snapshot/)
  - Use real-time macro vintages (Philadelphia Fed Real-Time Data Set). — [Philadelphia Fed WP 99-15](https://www.philadelphiafed.org/-/media/frbp/assets/working-papers/1999/wp99-15.pdf)
  - Banz & Breen (1986) propose remedies when only standard Compustat is available. — [AFA listing](https://afajof.org/issue/volume-41-issue-4/)
  - Respect filing lags (vendor sample average ~43 days). — [DEV Community](https://dev.to/tradevodata/your-backtest-saw-the-future-lookahead-bias-in-fundamental-data-measured-across-313562-rows-4cba)
- **Survivorship**:
  - Include delisted securities and impute missing performance-related delisting returns (-30% NYSE/Amex, -55% Nasdaq per Shumway 1997 and Shumway & Warther 1999). — [SAFE Frankfurt](https://datacenter.safe-frankfurt.de/documents/Data_Description_CRSP_Shumway_20250317.pdf)
  - Use historical (point-in-time) index constituents, for example via CRSP or Norgate. — [QuantConnect forum](https://www.quantconnect.com/forum/discussion/21226/would-you-pay-for-cheap-point-in-time-s-amp-p-500-data-survivorship-bias-free/); [DEV Community](https://dev.to/tradevodata/survivorship-bias-vs-lookahead-bias-the-two-silent-backtest-killers-pmm)
  - For fund data, track the full cohort from a start date, as Elton-Gruber-Blake did with all funds in the 1977 Wiesenberger directory. — [IDEAS/RePEc](https://ideas.repec.org/a/oup/rfinst/v9y1996i4p1097-1120.html)
- **Data snooping / period selection**:
  - Raise significance hurdles (t ≈ 3). — [NBER w20592](https://www.nber.org/papers/w20592)
  - Bootstrap Reality Check over the full rule universe. — [Sullivan-Timmermann-White PDF](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
  - Require a MinBTL consistent with the number of trials; note that simple hold-out does not control for trials. — [Bailey et al. 2014](https://scholarworks.wmich.edu/math_pubs/40/)
- **Regime change / non-stationarity**:
  - Expect decay: haircut published anomaly returns by roughly 26-58%. — [McLean & Pontiff](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf)
  - Test in crisis/"panic" states. Daniel & Moskowitz show momentum crash risk is forecastable from bear-market and high-volatility states and propose dynamic scaling. — [NBER w20439](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf); [Alpha Architect](https://alphaarchitect.com/avoiding-momentum-crashes/)
  - Use long histories spanning different macro regimes, as Molenaar et al. use data back to 1875 for stock-bond correlation. — [EUR Pure](https://pure.eur.nl/en/publications/empirical-evidence-on-the-stock-bond-correlation/)
  - Markov-switching models (Hamilton 1989; statsmodels implementation) are a formal tool, but estimates depend on the sample and starting values. — [statsmodels](https://www.statsmodels.org/dev/examples/notebooks/generated/markov_autoregression.html); [Fed IFDP 681](https://webarchive.library.unt.edu/eot2008/20090119105617/http:/www.federalreserve.gov/pubs/ifdp/2000/681/ifdp681.pdf)

### Inferences
- Mitigations map one-to-one onto the data pipeline:
  - **data layer**: point-in-time, dead assets, delisting returns, real-time vintages;
  - **research-process layer**: trial counting, multiple-testing corrections, minimum backtest length, a pre-committed window;
  - **evaluation layer**: sub-period, regime and crisis splits, and an expected post-deployment decay haircut.
- A practical rule implied by the evidence: report results across several start/end windows and regimes, not one headline number.

### Gaps
- Not retrieved: specific practitioner white papers from AQR, Research Affiliates or Quantpedia on walk-forward or combinatorially purged cross-validation (López de Prado's CPCV and Deflated Sharpe Ratio are known techniques, but I did not fetch sources for them this session).
- Not retrieved: Carver's own published recommendations (qoppac blog), only second-hand descriptions.
