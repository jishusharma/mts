# Overfitting, Data Snooping and Curve-Fitting as Causes of Backtest Failure (asset-agnostic)

Scope note: general statistical and methodological causes only; crypto-specific causes are covered by another researcher. Primary papers were read in full text where marked "[full text read]"; other claims rest on abstracts or secondary summaries and are labelled as such. Arithmetic checks were recomputed independently by this researcher where stated.

## Q1. What is the probabilistic / deflated Sharpe ratio problem, and how does repeated strategy testing (multiple testing / p-hacking) inflate apparent performance?

### Takeaway
A backtest Sharpe ratio is a noisy estimate. When many configurations are tried and only the best is kept, the expected best Sharpe is well above zero even if every configuration has zero true skill. Non-normal returns (negative skew, fat tails) and short samples add more inflation. The Probabilistic Sharpe Ratio (PSR) corrects for sample length and higher moments. The Deflated Sharpe Ratio (DSR) is a PSR whose rejection threshold rises with the number of independent trials N and the variance of the trial Sharpe ratios.

### Cited Findings
- **Expected-maximum effect (core mechanism).** Under IID Normal returns with true SR = 0 and 1 year of data, the estimated annualized SR is approximately N(0,1). The expected maximum over N independent trials is approximately E[max_N] = (1-gamma) Z^-1[1-1/N] + gamma Z^-1[1-1/(N e)], where gamma is about 0.5772 (Euler-Mascheroni), with upper bound sqrt(2 ln N). The paper's example: "if the researcher tries only N = 10 alternative configurations ... he or she is expected to find a strategy with a Sharpe ratio IS of 1.57, despite the fact that all strategies are expected to deliver a Sharpe ratio of zero OOS." (I recomputed 1.57 independently and it checks.) — [Bailey, Borwein, Lopez de Prado, Zhu, "Pseudo-Mathematics and Financial Charlatanism", Notices of the AMS 61(5), 2014, pp. 458-471; author PDF, full text read](https://carmamaths.org/jon/backtest.pdf)
- **Sampling distribution of SR.** Following Lo (2002), the estimated annualized SR is asymptotically Normal with mean SR and variance (1 + SR^2/(2q))/y, where q is returns per year and y is years. The paper notes that when SR = 0, increasing sampling frequency q does not reduce the variance. Only more years do. — [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **DSR definition.** "The Deflated Sharpe Ratio (DSR) corrects for two leading sources of performance inflation: Selection bias under multiple testing and non-Normally distributed returns." "Essentially, DSR is a PSR where the rejection threshold is adjusted to reflect the multiplicity of trials."
  - DSR deflates SR using five additional variables: skewness, kurtosis, sample length T, the variance of the trial SRs V[{SR_n}], and the number of independent trials N.
  - The threshold is SR0 = sqrt(V[{SR_n}]) * ((1-gamma) Z^-1[1-1/N] + gamma Z^-1[1-1/(N e)]).
  - Then DSR = Z[ (SR_hat - SR0) sqrt(T-1) / sqrt(1 - skew*SR_hat + ((kurt-1)/4) SR_hat^2) ].
  - Source: [Bailey & Lopez de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", Journal of Portfolio Management 40(5), 2014, pp. 94-107; author PDF, full text read (the PDF's math symbols did not extract cleanly, so the formula above is reconstructed from the paper's text and structure)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf); [SSRN abstract 2460551](https://papers.ssrn.com/abstract=2460551)
- **DSR worked example (Treasury auction-cycle seasonality).**
  - Setup: a strategist backtests many configurations, and "many combinations yield an annualized SR of 2, with a particular one yielding a SR of 2.5 over a daily sample of 5 years" (T = 1250).
  - Result: after deflation the investor "has recognized that there is only a 90% chance that the true SR associated with this strategy is greater than zero", so the strategy is rejected at 95%.
  - With only N = 46 trials, DSR "would have been 0.9505". With Normal returns, the 95% threshold would have been reached at N = 88 trials.
  - The specific inputs (N, V, skew, kurtosis) are garbled in the text extraction. They are commonly reported as N = 100, V = 0.5, skew = -3, kurtosis = 10, but that is unverified here.
  - Source: [Bailey & Lopez de Prado 2014, JPM (full text)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- **Winner's curse framing.** "When an investor selects the best performing strategy over a large number of alternatives, she exposes herself to 'the winner's curse' ... Performance out of sample is likely to disappoint, a phenomenon called 'regression to the mean'." The same logic covers capital allocators who apply a fixed SR cut-off to many managers: "As more candidates are considered, the false positive rate keeps growing." — [Bailey & Lopez de Prado 2014, JPM](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- **Stopping rule.** The DSR paper recommends planning trials in advance: "Investment theory, not computational power, should motivate what experiments are worth conducting." It proposes the optimal-stopping "secretary problem" (1/e law) as a rule of thumb. Sample about 37% of theoretically justified configurations, then stop at the first one that beats all previous ones, "because every additional trial irremediably increases the probability of a false positive." — [Bailey & Lopez de Prado 2014, JPM](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- **Multiple-testing p-value (Harvey & Liu).**
  - For N independent tests, p_M = 1 - (1 - p_S)^N.
  - "If N = 10 and we observe a strategy with p_S = 0.05, p_M = 0.401."
  - Haircut example: 20 years of monthly returns (T = 240) and an annual SR of 0.75 give a single-test p of 0.0008. With N = 200 tests, p_M = 0.15, the adjusted SR is 0.32, a haircut of about 60%.
  - SR and t-stat are linked by t = SR * sqrt(T).
  - Source: [Harvey & Liu, "Backtesting", Journal of Portfolio Management 41(1), Fall 2015, pp. 13-28; Duke PDF, full text read](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- **PSR on a random-walk overfit.** In the AMS paper's seasonal example, an 8,800-node grid (entry day x holding period x stop loss x side) was fitted on 1,000 days of a pure random walk. The best rule had an annualized SR of 1.27 and "the PSR-Stat is 2.83, which implies a less than 1% probability that the true Sharpe ratio is below 0". This shows that PSR alone, without a trial count, does not protect against selection bias. — [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **p-hacking (Harvey's presidential address).** Harvey argues that the incentive to publish significant results, together with unreported tests, failure to adjust for multiple testing and direct and indirect p-hacking, means many published findings will not hold up. Raising t cutoffs helps, but may be insufficient when true effects are rare. He proposes reporting a minimum Bayes factor or "Bayesianized p-value" that depends on prior plausibility. — [Harvey, "Presidential Address: The Scientific Outlook in Financial Economics", Journal of Finance 72(4), 2017, pp. 1399-1440 (summarised from search snippets of the abstract; full text not read)](https://people.duke.edu/~charvey/Research/Published_Papers/P131_The_scientific_outlook.pdf)
- **Practitioner thresholds are not from the papers.** Rules of thumb such as "DSR > 0.95 = strong evidence" appear on practitioner sites. They are not part of the original paper, which uses a standard 95% confidence framing. — [CXO Advisory summary](https://cxoadvisory.com/big-ideas/sharper-sharpe-ratio); [quantstrat deflatedSharpe docs](https://www.rdocumentation.org/packages/quantstrat/versions/0.16.7/topics/deflatedSharpe)

### Inferences
- The inflation scales roughly with sqrt(2 ln N) / sqrt(years). This is why short-history markets with many parameter sweeps are especially exposed: 10 trials on 1 year already produce an expected best SR of about 1.6 from pure noise.
- Negative skew and fat tails (typical of carry, short-vol, mean-reversion and stop-loss-heavy strategies) inflate the SR's standard error. This compounds selection bias, as the DSR example shows: the strategy passes with Normal returns at N = 88 but fails at N = 46 with its actual skew and kurtosis.
- Every swept parameter, every discarded idea and every re-run after peeking at results counts toward N. Effective N is rarely recorded, so most backtest SRs cannot be deflated after the fact.

### Gaps
- The exact numeric inputs of the DSR worked example could not be verified from the extracted text because the math glyphs were lost.
- The original PSR paper (Bailey & Lopez de Prado 2012, "The Sharpe Ratio Efficient Frontier", Journal of Risk) was not fetched. The PSR formula above comes from the DSR paper's description.

## Q2. What do Lopez de Prado, Harvey, Liu and peers say about the number of backtests run before "discovering" a strategy, and how it inflates false-positive risk?

### Takeaway
All of them argue that the number of trials is the single most important missing disclosure. Without it, the risk of overfitting cannot be assessed. Harvey, Liu and Zhu (factor research) say a new factor needs t > 3.0 rather than 2.0 given the hundreds of factors already tested. Harvey & Liu show the haircut is nonlinear: marginal Sharpe ratios are cut by far more than 50%. Lopez de Prado's group says hiding trials is equivalent to the "stock-market newsletter" fraud.

### Cited Findings
- **Not reporting N is the key defect.** "A researcher that does not report the number of trials N used to identify the selected backtest configuration makes it impossible to assess the risk of overfitting." "Because N is almost never reported, the magnitude of overfitting in published backtests is unknown. It is not hard to overfit a backtest (indeed, the previous theorem shows that it is hard not to), so we suspect that a large proportion of backtests published in academic journals may be misleading. The situation is not likely to be better among practitioners." — [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **Industry tooling.** "In our experience, overfitting is pathological within the financial industry, where proprietary and commercial software is developed to estimate the combination of parameters that best fits (or more precisely, overfits) the data. These tools allow the user to add filters without ever reporting how such additions increase the probability of backtest overfitting." The authors note that fund families closing poor funds have the same effect as hiding experiments, through survivorship and selection bias. — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Fraud analogy.** A manager emails up/down forecasts to 2^n * x prospects and keeps only the correct half each month. After n months, x people have seen n perfect calls. "Not reporting the number of trials (N) involved in identifying a successful backtest is a similar kind of fraud." Also: "When investment advisers do not control for backtest overfitting, good backtest performance is an indicator of negative future results." — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Regression-style overfit tests miss the trial count.** A researcher needs an SR > 2.0 with a specification that passes AIC at 95% confidence. "After only 20 trials, the researcher is expected to find one specification that passes the AIC criterion ... AIC's assessment did not take into account the hundreds of other trials that the researcher neglected to mention." — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Factor zoo hurdle (Harvey, Liu & Zhu).** "A newly discovered factor needs to clear a much higher hurdle, with a t-ratio greater than 3.0." They argue it "does not make any economic or statistical sense to use the usual significance criteria (t > 2.0)". The paper builds a time series of significance cutoffs from 1967 onward and allows for correlated tests. The authors concede they count only top-journal factors and "cannot" count unpublished failed tests, so the true hurdle is likely higher. — [Harvey, Liu & Zhu, "...and the Cross-Section of Expected Returns", Review of Financial Studies 29(1), 2016, pp. 5-68; NBER w20592 abstract](https://www.nber.org/papers/w20592); [SSRN 2513152](https://papers.ssrn.com/abstract=2513152)
- **At least 316 factors.** "Harvey, Liu, and Zhu [2015] (HLZ) document that at least 316 factors have been tested in the quest to explain the cross-sectional patterns in equity returns." — [Harvey & Liu 2015, JPM "Backtesting" (full text)](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- **The 50% rule and the nonlinear haircut.** "A common practice in evaluating backtests of trading strategies is to discount the reported Sharpe ratios by 50% ... The 50% haircut is only a rule of thumb." "We argue that it is a serious mistake to use the usual 50% haircut. Our results show that the multiple testing haircut is nonlinear. The highest Sharpe ratios are only moderately penalized, while the marginal Sharpe ratios are heavily penalized ... The strategies with very high Sharpe ratios are probably true discoveries. In these cases, a 50% haircut is too punitive."
  - Methods covered: Bonferroni and Holm, which control the family-wise error rate (Bonferroni is strictest), and Benjamini-Hochberg-Yekutieli, which controls the false discovery rate and is more lenient.
  - Source: [Harvey & Liu 2015, JPM (full text)](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
  - A secondary summary adds specific thresholds: for gross SR < 0.4 the haircut is "almost always above and sometimes far above 50%", and for SR > 1.0 it is at most about 25%. These were not verified in the paper. — [CXO Advisory (secondary)](https://www.cxoadvisory.com/big-ideas/navigating-the-data-snooping-icebergs/)
- **Trial and error kills OOS.** "A researcher tries a strategy. After running an OOS test, she finds that the strategy fails. She then revises the strategy and tries again ... This trial and error approach is not truly OOS, but the difference is hard for outsiders to see." Also: "given that the researcher has experienced the data, there is no true OOS that uses historical data." — [Harvey & Liu 2015, JPM (full text)](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- **Holdout under public data.** "If the data is publicly available, it is quite likely that the researcher has used the 'hold-out' as part of the IS dataset", and researchers know how markets behaved in the OOS window, "consciously or not". — [Bailey, Borwein, Lopez de Prado, Zhu, "The Probability of Backtest Overfitting", Journal of Computational Finance (DOI 10.21314/JCF.2016.322; online 2016, print c. 2017); eScholarship PDF, full text read](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Older data-snooping evidence (technical rules).**
  - Scope: Sullivan, Timmermann & White apply White's Reality Check bootstrap to "nearly 8,000 parameterizations of trading rules" on 100 years of DJIA data.
  - In-sample: in BLL's 1897-1986 sample, some rules beat the benchmark even after the data-snooping adjustment.
  - Out of sample: in the next 10 years (1987-1996) "the probability that the best-performing trading rule did not outperform the benchmark during this period is nearly 12 percent ... scant evidence that technical trading rules were of any economic value".
  - S&P 500 futures (1984-1996): "no evidence that the trading rules outperform the benchmark".
  - With the Sharpe criterion, the best rule's Reality Check p-value is 0.26, "no longer significant".
  - Source: [Sullivan, Timmermann & White, "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap", Journal of Finance 54(5), 1999, pp. 1647-1691 (full text read)](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- **Data snooping defined (STW 1999).** "Data-snooping occurs when a given set of data is used more than once for purposes of inference or model selection. When such data reuse occurs, there is always the possibility that any satisfactory results obtained may simply be due to chance." It also arises across many researchers over time on shared data (cites Lo & MacKinlay 1990). — [Sullivan, Timmermann & White 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- **Post-publication decay of anomalies.** Across 97 published return predictors, returns are about 26% lower out of sample and about 58% lower after publication. The authors treat the 26% out-of-sample decline as an upper bound on data-mining effects and attribute the 32% gap to publication-informed trading. — [McLean & Pontiff, "Does Academic Research Destroy Stock Return Predictability?", Journal of Finance 71(1), 2016 (from abstract/search summary)](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf)
- **Live vs backtest, retail algorithms (Quantopian).**
  - Sample: 888 algorithms with at least 6 months of OOS performance.
  - Backtest Sharpe barely predicted live Sharpe (R^2 < 0.025).
  - "More backtesting on a given strategy correlated with a bigger gap between backtest and OOS results", which is direct empirical evidence of the trial-count effect.
  - Volatility, max drawdown and hedging features had some predictive value. A nonlinear classifier on backtest features reached R^2 of about 0.17 on hold-out.
  - Source: [Wiecki, Campbell, Lent, Stauth, "All that Glitters Is Not Gold", Quantopian/SSRN, March 2016 (via Quantpedia summary and Quantopian forum archive)](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/); [Quantopian archive](https://quantopian-archive.netlify.app/forum/threads/q-paper-all-that-glitters-is-not-gold-comparing-backtest-and-out-of-sample-performance-on-a-large-cohort-of-trading-algorithms)
- **Live vs backtest, bank alternative-beta indices.**
  - Sample: about 215 bank "alternative beta" indices.
  - Median Sharpe deterioration from backtest to live: 72-73% (sources differ), about 80% for equity strategies.
  - Only 18 of 215 (8.4%) had a live SR at or above the backtest SR.
  - The most complex strategies had more than 30 percentage points larger haircuts.
  - The 50% derating rule is "not conservative enough".
  - Source: [Suhonen, Lennkh & Perez, "Quantifying Backtest Overfitting in Alternative Beta Strategies", JPM 2017 / SSRN 2016 (secondary summaries only; the original was not read)](https://mathinvestor.org/2017/08/backtest-overfitting-in-smart-beta-investments/); [CXO Advisory](https://www.cxoadvisory.com/big-ideas/live-performance-of-alternative-beta-products/)
- **Research through backtesting.** Lopez de Prado (Advances in Financial Machine Learning, Wiley 2018, ch. 11) describes treating backtesting as a research tool as a common misunderstanding: "researching and backtesting is like drinking and driving. Do not research under the influence of a backtest." This is from search-snippet paraphrase. A related paper, "The 10 Reasons Most Machine Learning Funds Fail" (JPM 2018), lists research-through-backtesting as a pitfall. — [O'Reilly ch. 11 listing](https://www.oreilly.com/library/view/advances-in-financial/9781119482086/c11.xhtml); [GARP copy of the 10 Reasons paper](https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf)

### Inferences
- The consensus is that live Sharpe typically keeps well under half of backtest Sharpe:
  - 72-73% median decay for bank indices.
  - About 58% post-publication decay for academic anomalies.
  - Near-zero predictive power of backtest SR for retail algorithms.
- So a flat 50% haircut is optimistic for marginal strategies.
- The trial count includes the whole research team's history on the same dataset, including earlier rejected ideas and published papers using the same data. It is not just the current grid search.

### Gaps
- Lopez de Prado's "False Strategy Theorem" (Lopez de Prado & Lewis, "Detection of false investment strategies using unsupervised learning methods", Quantitative Finance 2019) and his ONC clustering method for estimating effective N were not fetched.
- Harvey & Liu, "False (and Missed) Discoveries in Financial Economics" (Journal of Finance 2020) was not fetched.
- The exact Suhonen et al. median (72% vs 73%) is unresolved because only secondary sources were read.

## Q3. What is "backtest overfitting" formally (Bailey / Borwein / Lopez de Prado / Zhu)?

### Takeaway
Formally, a strategy-selection process overfits when the configuration that ranks best in-sample has an expected out-of-sample rank below the median of all configurations tried. PBO is the probability of that event, estimated non-parametrically by Combinatorially Symmetric Cross-Validation (CSCV). The companion AMS paper derives the Minimum Backtest Length for a given N. It also shows that when returns have "memory" (compensation effects), overfitting does not just fail to help: it actively produces negative OOS performance.

### Cited Findings
- **Informal definition.** Overfitting "denotes the situation when a model targets particular observations rather than a general structure". Example: removing trades known to lose IS ("data snooping"), so that the "optimal parameters ... profit from features that are present in that particular sample but may well be rare in the population." "A backtest is realistic when the IS performance is consistent with the OOS performance." — [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **Definition 2.1 (Backtest Overfitting).** "We say that the backtest strategy selection process overfits if a strategy with optimal performance IS has an expected ranking below the median OOS."
- **Definition 2.2 (PBO).** The probability that the IS-optimal strategy ranks below the median OOS: PBO = sum_n Prob[rbar_n < N/2 | r in Omega*_n] Prob[r in Omega*_n].
- **Selection, not calibration.** Overfitting here is defined "in relation to the strategy selection process, not a strategy's model calibration", which makes it model-free.
- Source for the two definitions and the note above: [Bailey, Borwein, Lopez de Prado, Zhu, "The Probability of Backtest Overfitting", Journal of Computational Finance (full text)](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf); [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- **CSCV algorithm.**
  1. Build a T x N matrix M of per-period P&L for all N trials.
  2. Split M by rows into an even number S of equal blocks.
  3. Form all C(S, S/2) combinations. Each combination is a training set J (half the blocks, kept in order), and its complement is the test set.
  4. For each combination, find the IS-best configuration n*, compute its OOS relative rank omega = rank/(N+1), and compute the logit lambda = ln(omega / (1 - omega)).
  5. PBO = the fraction of logits <= 0.
  - The paper recommends S = 16 (quarterly blocks for 4 years of daily data, preserving serial correlation).
  - The text says this gives "12,780 combinations". C(16,8) is actually 12,870, so the paper's figure appears to be a typo (recomputed independently).
  - The paper suggests rejecting models with PBO > 0.05 under a Neyman-Pearson convention.
  - Source: [Bailey et al., JCF (full text)](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Four overfit statistics from the same framework:**
  1. PBO.
  2. Performance degradation: the slope of OOS SR on IS SR, "negative in most practical cases, due to compensation effects".
  3. Probability of loss OOS.
  4. Stochastic dominance of the selection procedure over random choice.
  - "The model is so fit to past noise, that it is often rendered unfit for future signal. And the more overfit a backtest is, the more memory is accumulated against its future performance." — [Bailey et al., JCF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Illustrations.**
  - Overfit example: 100% of IS SRs are positive but about 78% of OOS SRs are negative, IS SRs range from 1 to 3, and PBO = 74%. "We cannot hope escaping the risk of overfitting by exceeding some SR IS threshold. On the contrary, it appears that the higher the SR IS, the lower the SR OOS."
  - Real strategy: PBO of about 0.04% and an OOS loss probability of about 3%. The method can pass genuine strategies.
  - Source: [Bailey et al., JCF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Minimum Backtest Length (MinBTL), Theorem 3.1.** The minimum backtest length in years needed to avoid selecting a strategy with IS SR of E[max_N] among N independent zero-skill strategies is MinBTL ~ ( ((1-gamma) Z^-1[1-1/N] + gamma Z^-1[1-1/(N e)]) / E[max_N] )^2 < 2 ln(N) / E[max_N]^2. Numerical examples:
  - "If only 5 years of data are available, no more than 45 independent model configurations should be tried, or we are almost guaranteed to produce strategies with an annualized Sharpe ratio IS of 1, but an expected Sharpe ratio OOS of zero."
  - "After trying only 7 independent strategy configurations, the expected maximum SR IS is 1 for a 2-year long backtest."
  - I recomputed both independently: N = 45, y = 5 gives about 1.00; N = 7, y = 2 gives about 0.98.
  - MinBTL is "a necessary, non-sufficient condition".
  - Correlated trials should be reduced to an effective independent N, for example by PCA.
  - Source: [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf); [Harvey & Liu 2015 restating the 7-trial result](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- **Compensation effects make overfitting harmful, not just useless.**
  - Memoryless random walks: selecting the IS-best path out of 1,000 (T = 1000 split 500/500) gives an IS SR of 1.2-2.6 (centred about 1.7), while the OOS SR stays around 0.
  - Global constraint: re-centring each path to a fixed mean (one global constraint) makes OOS performance negative, with a significant negative IS-to-OOS slope (p-value of slope = 0).
  - Serial dependence: the same happens with AR(1) performance series (phi = 0.995, half-life of about 138 observations). Proposition 6.3: SR_IS(A) > SR_IS(B) if and only if SR_OOS(A) < SR_OOS(B).
  - The authors list real-world compensation sources: "overcrowded investment opportunities, major corrections, economic cycles, reversal of financial flows, structural breaks, bubble bursts". They note serial correlation is "present in the performance of most hedge fund strategies".
  - Source: [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **Seasonality and "the effect was never there".** The authors warn that OOS disappointment is often wrongly blamed on the market "arbitraging away" an effect: "Rather, the effect was never there; instead it was just a random pattern that gave rise to an overfitted trading rule." — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)

### Inferences
- PBO answers a different question from DSR or Harvey-Liu.
  - PBO asks whether the selection process is reliable, based on rank persistence.
  - DSR and Harvey-Liu ask whether the chosen strategy is statistically significant given N.
  - Harvey & Liu (2015) themselves describe the approaches as complementary.
- Under mean-reverting regimes, the more aggressively parameters are tuned to recent history, the worse the expected live result. This is a mechanism for live P&L below zero, not just below the backtest.

### Gaps
- The PBO paper's limitations section was not reviewed in detail. One noted requirement is N much larger than 10 so that logits are not too discrete.
- The Monte Carlo / extreme-value-theory accuracy study (SSRN 2568435) was not fetched.

## Q4. How do degrees of freedom / number of free parameters relative to data length drive overfitting in trading-rule backtests?

### Takeaway
Each free parameter multiplies the number of distinguishable configurations, which is the effective N. Expected best-of-N performance grows as about sqrt(2 ln N), while the standard error of the SR shrinks only as 1/sqrt(years). So the data needed grows with ln N. A handful of binary filters on a few years of data is enough to manufacture Sharpe ratios above 2 from noise. Empirically, more complex products show larger backtest-to-live decay.

### Cited Findings
- **Complexity multiplies N.** "Consider a one-parameter model that may adopt two possible values ... Overfitting will be difficult, because N = 2. Let's say that we make the model more complex, by adding 4 more parameters so that the total number of parameters becomes 5, i.e. N = 2^5 = 32." "A relatively simple strategy with just 7 binomial independent parameters offers N = 2^7 = 128 trials, with an expected maximum Sharpe ratio above 2.6." The paper also says you do not need to fit perfectly: "Without perfectly fitting a strategy, or making it over-complex, a researcher can achieve high Sharpe ratios." — [Bailey et al. 2014, Notices AMS (full text)](https://carmamaths.org/jon/backtest.pdf)
- **Where the free parameters hide.** Overfitting is not limited to the forecasting equation: "other components of the investment strategy may have been overfitted, including entry thresholds, risk sizing, profit-taking, stop-loss, cost of capital". In design, researchers tune "optimal sample sizes, signal update frequency, entry and profit taking thresholds, risk sizing, stop losses, maximum holding periods". The authors single out technical-analysis filters and non-parametric tools (neural nets, kernel estimators) as needing "extra caution". — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Grid example.** A 4-parameter monthly rule (entry day 1-22, holding 1-20, stop 0-10, side +/-1) gives 8,800 nodes. On 1,000 days of a pure random walk it yields a best annualized SR of 1.27. — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Data-length requirement.** MinBTL < 2 ln(N) / E[max_N]^2, so the required years grow with the log of the configuration count. For a target of IS SR = 1: 7 trials need about 2 years, and 45 trials need about 5 years. — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Holdout sample size.** Citing Weiss & Kulikowski, the PBO paper says "hold-out should not be applied to an analysis with less than 1,000 observations. For example, if a strategy trades on a weekly basis, hold-out should not be used on backtests of less than 20 years." It also notes the high variance of holdout estimates (Van Belle & Kerr): "Different hold-outs are thus likely to lead to different conclusions." — [Bailey et al., JCF (full text)](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Complexity and live decay.** In the bank alternative-beta sample, the most complex strategies had more than 30 percentage points larger Sharpe haircuts than simpler ones after fixed-effect controls. — [Suhonen et al. via mathinvestor.org (secondary)](https://mathinvestor.org/2017/08/backtest-overfitting-in-smart-beta-investments/)
- **Complexity in the Arnott-Harvey-Markowitz protocol.** Category 6 asks:
  - "Does the model avoid the curse of dimensionality?"
  - "Have the researchers taken steps to produce the simplest practicable model specification?"
  - Is an attempt made to interpret ML predictions rather than use a black box?
  - The paper flags data scarcity: ML usually needs far more data than finance offers, especially at longer horizons.
  - Source: [Arnott, Harvey & Markowitz, "A Backtesting Protocol in the Era of Machine Learning", Journal of Financial Data Science 1(1), 2019, pp. 64-74; SSRN 3275654 PDF, full text read](https://www.smallake.kr/wp-content/uploads/2023/04/SSRN-id3275654.pdf); [SSRN abstract](https://papers.ssrn.com/abstract=3275654)
- **Practitioner degrees-of-freedom literature.** Pardo's *The Evaluation and Optimization of Trading Strategies* (Wiley, 2nd ed. 2008) has sections on "Degrees of Freedom, Sample Size and Startup Overhead" and "Overparameterization". Walk-forward-efficiency rules of thumb attributed to Pardo (WFE > 0.5 robust, < 0.3 red flag) are secondhand and unverified. — [Pardo TOC excerpt](https://typeset.io/pdf/the-evaluation-and-optimization-of-trading-strategies-1v4948xmy2.pdf); [backtrex WFE page (secondary)](https://backtrex.com/en/blog/walk-forward-efficiency-ratio-thresholds)

### Inferences
- Counting: a strategy with k parameters each tried at m levels has up to m^k configurations. Correlated neighbouring settings reduce the effective N, but not to 1.
- Adding a filter that removes losing IS trades is exactly the "data snooping" example the AMS paper gives.
- Signs that free parameters outnumber what the data can support:
  - Few trades per parameter.
  - Performance sensitive to small parameter changes, with isolated peaks rather than plateaus.
  - Rules tied to specific calendar days or events.
- A practical consequence of the sqrt(2 ln N) / sqrt(y) scaling: doubling the history roughly offsets squaring the number of independent trials at a fixed IS SR target. Shorter histories, such as young markets, tolerate far fewer parameter sweeps.

### Gaps
- No primary source gave a validated numeric rule such as "at least X trades per free parameter". Such rules circulate in practitioner books, Pardo among them, but could not be verified.
- Formal effective-N estimation for correlated parameter grids (PCA in Bailey et al.; ONC clustering in Lopez de Prado's later work) was not researched in depth.

## Q5. What practical warning signs and diagnostics are recommended (walk-forward, holdout, time-series CV, CPCV)?

### Takeaway
Holdout and single-path walk-forward are necessary but weak. They ignore N, can be contaminated by the researcher's knowledge, give one high-variance estimate, and trade test power against training power. The recommended stack is:
- An ex-ante economic hypothesis and a complete log of all trials.
- Multiple-testing adjustment (DSR or Harvey-Liu haircut, t > 3).
- PBO/CSCV on the full trial matrix.
- Purged and embargoed time-series CV, or Combinatorial Purged CV (CPCV), to get a distribution of OOS paths.
- Realistic costs.
- Live paper trading as the only true OOS.

### Cited Findings
- **Five weaknesses of the holdout method (PBO paper).**
  1. Public data means the holdout was likely seen.
  2. Researchers know what happened in the OOS period.
  3. It is inadequate for small samples (fewer than about 1,000 observations).
  4. It wastes data: taking the OOS from the end discards "the most recent observations, which often are the most representative going forward".
  5. "The hold-out method does not take into account the number of trials attempted before selecting a particular strategy configuration."
  - Conclusion: "The answer to the question 'is this backtest overfit?' is not a true-or-false, but a non-null probability that depends on the number of trials involved."
  - Source: [Bailey et al., JCF (full text)](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Synthetic-data approach.** Monte Carlo or synthetic-scenario backtests give a distribution rather than a single OOS figure. The risk is that "the model that generates random series of the underlying variable may also be overfit, or may not contain all relevant statistical features." — [Bailey et al., JCF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)
- **Type I vs type II trade-off in splitting.** With 1,000 observations, a 50/50 split loses true discoveries in the short IS period. A 90/10 split leaves only 100 OOS observations, too few "to truly discriminate". Harvey & Liu suggest a lenient IS screen (for example p = 0.2), then requiring survival both in OOS and in a full-sample multiple-testing adjustment. — [Harvey & Liu 2015, JPM (full text)](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF)
- **Seven-point protocol (Arnott, Harvey & Markowitz 2019), selected questions:**
  - (1) Was the economic hypothesis set before the research?
  - (2) "Did the researcher keep track of all models and variables that were tried (both successful and unsuccessful)?" "Did the researchers investigate all variables set out in the research agenda or did they cut the research as soon as they found a good model?"
  - (3) Were data transformations, outlier and winsorization rules chosen in advance, with only one tried?
  - (4) "Are the researchers aware that true out-of-sample tests are only possible in live trading?" Are steps in place to stop OOS "iterations" (an IS model later modified to fit OOS data)? Are trading costs and data revisions in the OOS?
  - (5) Resilience to structural change, overcrowding, and "tweaking of a live model".
  - (6) Simplicity and the curse of dimensionality.
  - (7) A research culture that rewards quality over "finding the winning strategy" and accepts that "most tests will fail".
  - Source: [Arnott, Harvey & Markowitz 2019, JFDS (full text, Exhibit 2)](https://www.smallake.kr/wp-content/uploads/2023/04/SSRN-id3275654.pdf)
- **Model sequestration.** The AMS paper cites Leinweber & Sisk, who announced a strategy and published its results 6 months later on unseen data, as "an extreme variation of 'hold-out'". — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)
- **Purged CV, embargo and CPCV (Advances in Financial Machine Learning, Lopez de Prado, Wiley 2018, ch. 7 and 12).**
  - Standard k-fold leaks information when labels span future windows and data are serially correlated.
  - Purging removes training observations whose label windows overlap the test set.
  - An embargo drops a buffer after each test block. A cited rule of thumb is about 1% of bars.
  - CPCV splits data into N groups and tests on every combination of k groups, C(N, k) splits. These are reassembled into multiple full OOS backtest paths, turning one backtest into a distribution of OOS Sharpe ratios that can feed PBO.
  - The main criticism of walk-forward is that it tests a single historical path, so its estimate has high variance and depends on that particular sequence.
  - Source: secondary and tutorial sources; the book itself was not read. [Purged cross-validation (Wikipedia; carries a conflict-of-interest note)](https://en.wikipedia.org/wiki/Purged_cross-validation); [fynance CPCV docs](https://fynance.readthedocs.io/en/latest/generated/fynance.data.combinatorial_purged_cv.html); [LuxAlgo explainer](https://www.luxalgo.com/library/concept/purged-cross-validation/)
- **CPCV vs walk-forward, empirical comparison.** In a synthetic controlled environment, CPCV gave lower PBO and higher DSR than traditional methods. Walk-forward "shows notable shortcomings in false discovery prevention, characterized by increased temporal variability and weaker stationarity." A later paper notes walk-forward remains the industry standard for realistic simulation. — [Arian, Norouzi Mobarekeh & Seco, "Backtest overfitting in the machine learning era", Knowledge-Based Systems 2024, DOI 10.1016/j.knosys.2024.112477 (abstract/secondary only)](https://www.scribd.com/document/725401650/SSRN-id4778909); [arXiv 2512.12924 citing it](https://arxiv.org/pdf/2512.12924)
- **Multiple-testing corrections to apply.** Bonferroni, Holm (FWER) or BHY (FDR) adjusted p-values, converted to a haircut Sharpe. Harvey & Liu provide code to compute haircuts and the minimum profitability hurdle. White's Reality Check (and Hansen's SPA) bootstrap the best rule against the whole rule universe. — [Harvey & Liu 2015](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF); [Sullivan, Timmermann & White 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- **Which backtest stats predict live results.** In the Quantopian cohort, backtest Sharpe barely predicted live Sharpe (R^2 < 0.025). Volatility, max drawdown and hedging carried more information. More backtest iterations meant larger IS-to-OOS gaps. — [Quantpedia summary of Wiecki et al. 2016](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)
- **Seasonal and calendar rules.** Questions like "Is there a time interval every ___ when I would have made money on a regular basis?" always have an "arbitrarily optimal" answer. Doyle & Chen find the weekday effect "wanders". — [Bailey et al. 2014](https://carmamaths.org/jon/backtest.pdf)

### Inferences
Warning-sign checklist synthesised from the sources above:
1. The number of configurations tried is unknown or unlogged.
2. IS Sharpe is high (> 2) on short history. Under compensation effects, higher IS SR predicts worse OOS.
3. Performance hinges on a few parameters with sharp optima, or on calendar or event-specific rules.
4. The OOS window was looked at more than once, or the strategy was revised after an OOS failure.
5. The OOS window is short (fewer than about 1,000 observations).
6. A single walk-forward path with no dispersion estimate.
7. Negative skew or fat tails left unaccounted for in the SR.
8. PBO well above 0.05, DSR below 0.95, or t-stat below 3 after correction.
9. Costs and slippage missing from the OOS.
10. Live results trailing backtest by more than the 50-75% decay seen empirically.

Recommended order: pre-register the hypothesis and log every trial; compute DSR and the Harvey-Liu haircut with honest N; run CSCV/PBO on the full trial P&L matrix; validate with purged/embargoed CPCV; then paper or small-size live trading as the only true OOS.

### Gaps
- *Advances in Financial Machine Learning* (2018) chapters 7, 11, 12 and 14 were not read directly. CPCV mechanics, the number-of-paths formula, embargo sizing and the "backtesting while researching" quote come from secondary sources and snippets.
- Quantitative evidence on how much CPCV improves live results in real (not synthetic) portfolios was not found.
- Industry blogs requested in the brief were not fetched directly: an attempted Alpha Architect page returned 403; Two Sigma and AQR were not tried.
