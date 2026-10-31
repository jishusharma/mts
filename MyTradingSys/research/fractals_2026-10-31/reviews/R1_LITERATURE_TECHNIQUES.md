# R1: Fractals for BTC: literature and techniques review (Lab_Guy, 2026-10-31)

Review only: no code built, no backtest run. Sources are public. Every external claim has a link; where I read only an abstract or summary page, the row says so. Evidence classes used throughout:

| Class | Meaning |
|---|---|
| **OOS-NET** | out-of-sample and after fees |
| **OOS-GROSS** | out-of-sample, fees ignored or unrealistically low |
| **IS** | in-sample statistics or a backtest on the same data the rule was built on |
| **DESC** | a description of the market (efficiency, scaling), not a trading claim |
| **ANECDOTE** | chart posts, vendor pages, forum claims, single predictions |

**Bottom line:** across the four meanings of "fractal" I found **no published OOS-NET evidence on BTC**. The best evidence is DESC (BTC's Hurst exponent and efficiency change over time) plus one 2026 preprint that pre-registers halving-clock windows that have not resolved yet. In this repo, Williams-style fractal swings at 15m already FAIL fee-net, 1h and 4h are INCONCLUSIVE, and a 1m shape-analog search gave coin-flip outcomes. A fractals layer is most likely to add value as a **context or regime tag on layers we already have**, not as a stand-alone trigger.

---

## 1. Four meanings: keep them separate

| # | Meaning | What it measures | Typical use | Best evidence class found |
|---|---|---|---|---|
| a | Bill Williams 5-bar fractal | A swing point: the middle bar's high above two highs on each side (lows mirror), confirmed only after the 2 later bars close ([MT5 help](https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals); origin *Trading Chaos*, 1995, per [LuxAlgo](https://www.luxalgo.com/library/concept/williams-fractal/)) | Stops, breakout levels, swing structure | ANECDOTE outside this repo; repo: FAIL at 15m, INCONCLUSIVE at 1h/4h |
| b | Fractal market hypothesis (FMH), Hurst exponent, DFA, MF-DFA, fractal dimension | Persistence (H>0.5 trending, H<0.5 mean-reverting) and multiscaling of returns | Regime and efficiency labels | DESC (many papers); trading use is IS or OOS-GROSS at best |
| c | "Cycle fractal" overlays | Shift a past cycle's price path (2013/2017/2021) onto now, aligned on the halving or on a peak/bottom; also a smaller structure "repeating" at a lower timeframe | Top/bottom timing calls | ANECDOTE, plus one pre-registered preprint (unresolved) |
| d | Multi-timeframe self-similarity | Whether structure (swings, legs, ranges) looks the same across timeframes | Nested-level confluence, top-down analysis | No direct trading evidence; the stylised fact (scaling) is DESC under (b) |

"Fractal" in (a) is a name only: LuxAlgo notes the Williams fractal is "a five-bar swing marker, not a measured fractal" ([LuxAlgo](https://www.luxalgo.com/library/concept/williams-fractal/)). Mixing (a) with (b) is the most common confusion in retail material.

### 1a. Williams fractals: what exists

| Source | Claim | Class |
|---|---|---|
| [TradingView EMA + Williams Fractal strategy](https://www.tradingview.com/script/9x6HqchH-EMA-Williams-Fractal-Pullback-Trading-Nerd) (author's notes, per search summary) | Not profitable after fees on low timeframes; "seems to work" on higher timeframes | ANECDOTE (author backtest, tuned) |
| [QuantConnect fractal backtest](https://www.quantconnect.com/terminal/cache/embedded_backtest_f59b5f6b8777bd10e8b8303e521c5c67.html) | 11 trades on TQQQ (not crypto) | ANECDOTE (n=11) |
| Implementation detail ([LuxAlgo](https://www.luxalgo.com/library/concept/williams-fractal/)) | Tie handling differs between platforms (strict vs equal on older side) | definitional |

No peer-reviewed study of Williams fractals on crypto turned up. Closest academic relative: automated chart-pattern detection by kernel regression on US stocks 1962-1996, which found that patterns carry "incremental information" in conditional return distributions, with no trading-cost test ([Lo, Mamaysky, Wang 2000, NBER w7613](https://www.nber.org/system/files/working_papers/w7613/w7613.pdf); [summary page](https://web.mit.edu/Alo/www/Papers/techanal.html)). Class: IS/DESC.

### 1b. FMH / Hurst / DFA / MF-DFA on BTC

| Paper | Finding | Class |
|---|---|---|
| [Bariviera 2017, Economics Letters (arXiv 1709.08090)](https://arxiv.org/abs/1709.08090) | Rolling Hurst 2011-2017: returns persistent early, more efficient from about 2014; volatility long-memory throughout; DFA tracks changes better than R/S (abstract) | DESC |
| [Kristoufek 2018, Physica A 503](https://ideas.repec.org/a/eee/phsmap/v503y2018icp257-262.html) | BTC mostly inefficient 2010-2017; efficient spells come in cool-downs after bubbles (abstract) | DESC |
| [Takaishi & Adachi, arXiv 1902.09253](https://arxiv.org/abs/1902.09253) | H below 0.5 before 2013 (low liquidity), about 0.5 after as liquidity grew (per search summary) | DESC |
| [Shrestha 2021, Int. Rev. Finance](https://zendy.io/title/10.1111/irfi.12256) | MF-DFA: BTC returns multifractal, so not efficient (abstract) | DESC |
| [arXiv 2510.13785 (2025)](https://arxiv.org/html/2510.13785v1) | Multifractality comes mainly from temporal correlations, not only fat tails (shuffle test) | DESC |
| [Kristoufek 2012/2013, arXiv 1203.4979](https://arxiv.org/abs/1203.4979) | FMH test on equities: rolling local Hurst shifts before and during the 2008 crisis | DESC (equities) |
| [Mathematics 2024, 12(18):2911](https://mdpi.com/2227-7390/12/18/2911) | Local Hurst as a crypto pairs-trading entry; commissions over long holds can wipe out excess returns (per summary) | IS/OOS-GROSS, fee-fragile |
| [Generalised Hurst stat-arb (Marmara listing)](https://avesis.marmara.edu.tr/yayin/09a0fe35-34ad-4a3f-83b5-cd6779ad7376/statistical-arbitrage-in-cryptocurrencies-using-the-generalised-hurst-exponent) | Pairs with H<0.5; costs 0.01% (far below our 0.10% round trip) | OOS-GROSS in effect |
| [Halving-split efficiency, Eurasian Econ Rev 2022](https://link.springer.com/article/10.1007/s40822-022-00214-8) | Sample split at halving dates; efficiency changes across halving epochs (per summary) | DESC |
| [Preprints.org FMH preprint 2025](https://www.preprints.org/manuscript/202507.1974) | H about 0.32 for BTC/ETH; in-sample backtests | IS, not peer reviewed |

Estimator pitfalls that bite us directly:
- **Bias in short windows:** R/S tends to overstate H and DFA to understate it; the direction depends on the estimator and the window length ([arXiv 1201.4786](https://arxiv.org/abs/1201.4786); [UMN, short or irregular series](https://experts.umn.edu/en/publications/are-hurst-exponents-estimated-from-short-or-irregular-time-series/)). A rolling 250-day H has a wide error band, so a 0.55 threshold may sit inside the noise.
- **Spurious multifractality:** finite samples and fat tails create apparent multifractality ([search summary of arXiv 1307.3653](https://arxiv.org/abs/1307.3653)). Every MF-DFA reading needs a shuffled-series and a phase-randomised surrogate comparison.
- **Vendor filters:** "Hurst adaptive" indicators use H>0.55 trending / H<0.45 mean-reverting cut-offs with no evidence attached ([TradingView HEAF listing](https://www.tradingview.com/scripts/volatilityfilter/)). ANECDOTE.

### 1c. Cycle-fractal overlays

What analysts do:
- **Halving-aligned rebasing:** [Glassnode price performance since halving](https://studio.glassnode.com/charts/btc-price-performance-since-halving?a=BTC), [Decentrader bull market comparison](https://www.decentrader.com/?p=2808293), [The Right Trader reward-era comparison](https://therighttrader.com/bitcoin-charts/reward-era-comparison), [BGeometrics halving radar](https://bgeometrics.com/blog/2021-01-bitcoin-price-halving-radar-chart).
- **User overlays:** e.g. [TradingView "Bitcoin cycle vs last cycle"](https://www.tradingview.com/chart/BTCUSD/bXBwOkbl-Bitcoin-cycle-vs-last-cycle).
- **Lengthening-cycle and diminishing-returns variants:** [TradingView lengthening cycles](https://pl.tradingview.com/chart/BTCUSD/vftNbHiR-Lengthening-Cycles-Diminishing-Returns-from-halvings), [Cryptonary](https://cryptonary.com/bitcoin-cycles-expanding-beyond-four-years-a-deeper-dive-into-lengthening-cycles), [Into The Cryptoverse summary](https://rosetta.to/u/intothecryptoverse/bitcoin-lengthening-cycles-and-diminishing-returns).

What happened in this cycle:
- **The 2025 top:** BTC made an ATH near 126k on 2025-10-06, about 534 days after the 2024-04-20 halving ([CryptoPotato](https://cryptopotato.com/was-bitcoins-126k-peak-on-october-6-the-final-top-of-this-cycle-poll/), [Blocmates](https://www.blocmates.com/news-posts/bull-run-back-on-bitcoin-hits-new-ath-of-126-080-over-365m-in-liquidations-recorded)).
- **The 4chan date call:** an anonymous Dec-2023 post had named that exact date and a bottom 364 days later, about 2026-10-05 ([Decrypt](https://decrypt.co/380113/4chan-bitcoin-prophecy-end-crypto-winter)). This is ANECDOTE: one hit, with no record of how many such predictions were posted.

The one serious paper:
- **Paper:** Molnar, "Bitcoin Runs on a Clock", arXiv 2607.26188, July 2026, single author, not peer reviewed ([abstract](https://arxiv.org/abs/2607.26188); I read the abstract page only).
- **Top timing:** mature tops came 525 / 546 / 534 days after the halving, and bottoms 406 / 364 / 366 days after the top.
- **The nulls:** the top cluster survives a block-bootstrap path null (0 of 10,000 paths reproduce it). The bottom cluster appears in 31-43% of random paths, so **bottom timing is mostly a property of drawdowns, not of the clock**.
- **HAC inference:** it over-rejects (size 0.33 at a nominal 0.05).
- **Indicator decay:** top-calling indicators decayed cycle by cycle ("precise, then early, then silent").
- **Shape overlays:** they did not add value.
- **Pre-registered windows:** a 2026 bottom between Oct 5 and Nov 16, and the next top 525-546 days after the next halving.
- **Class:** DESC with a pre-registration. No fee-net trading test.

Critiques:
- **Tiny sample:** [Hackernoon on microcycles](https://hackernoon.com/will-microcycles-replace-4-year-cycles-in-crypto) and [Medium / Quantum Economics](https://medium.com/quantum-economics/is-the-current-bitcoin-halving-cycle-already-over-6d35a25fbf9c) point out how few cycles there are.
- **Lengthening is itself only 2 data points:** the lengthening-cycle claim rests on comparing 2017 with 2021.
- **The 2024 cycle broke the lengthening story:** halving-to-top was 534 days, shorter than 546, not longer.

### 1d. Multi-timeframe self-similarity
- **DESC:** the academic content is the scaling work in (b); MF-DFA and the generalised Hurst exponent are the formal versions of "structure looks the same across scales".
- **Swing nesting:** no paper tests swing nesting (a 4h swing inside a daily swing) as a trading signal on BTC.
- **The closest trading relative is matrix-profile motif work:**
  - Variable-length motifs across horizons (e.g. head-and-shoulders at different scales) on FX and indexes, by Cartwright, Crane and Ruskin at DCU ([DORAS 26068](https://doras.dcu.ie/26068); [Forecasting 2022](https://doaj.org/article/353c4e870d0d44869c90071ce7d9183f)).
  - That work finds "similar behaviour" periods. It reports no trading returns. Class: DESC.

---

## 2. Techniques for (c) and (d)

| Technique | Detects | Main pitfalls | Published OOS evidence |
|---|---|---|---|
| **Pearson / z-normalised correlation of log paths** (what `fractal.py` does) | Same shape at the same speed | (1) Two independent random walks show widely scattered correlations ("nonsense correlation"; [Ernst, Shepp, Wyner 2017, Ann. Stat.](https://arxiv.org/abs/1608.04120)), so r>=0.85 on trending windows is common by chance. (2) Overlapping windows inflate n. (3) Template picked after the fact | None for BTC; repo DESC run: coin flip (Section 4) |
| **DTW** (Sakoe-Chiba band) | Same shape at different speeds | Window length, band width and normalisation are 3+ free parameters ([LuxAlgo DTW](https://www.luxalgo.com/library/concept/dynamic-time-warping-similarity.md)); warping makes almost anything match | S&P 500 thesis with a strictly causal pipeline and a single OOS test: DTW features gave **no consistent OOS gain**, a small positive net result in trading ([PoliTo thesis](https://webthesis.biblio.polito.it/39690/1/tesi.pdf)): OOS-NET, negative-to-flat, equities. BTC: Liston, Gretton, Lensky 2024 DTW pattern clusters with continual learning on BTCUSDT 2017-2024 ([ANU](https://openresearch-repository.anu.edu.au/entities/publication/52f2798c-dec4-4fe2-9b3c-fb5be1e43e1c)); headline returns and fee handling not visible in the abstract: unverified |
| **Matrix profile** ([STUMPY](https://stumpy.readthedocs.io/en/stable/tutorials.html)) | Every window's nearest neighbour (motifs) and its most unusual window (discords), exact and fast | Finds repeats, not edge ([LuxAlgo](https://www.luxalgo.com/library/concept/matrix-profile.md)); trivial self-matches need an exclusion zone; picking the motif length is a free parameter | DESC only ([DCU](https://doras.dcu.ie/26068)) |
| **Shape-based nearest-neighbour (analog) forecasting** | Average outcome after the k most similar past windows | Look-ahead if the library contains future data or the template is chosen at a known turn; k and the distance metric are tuned | FX 1978-1994: net of costs and interest, the NN rule beat buy-and-hold in all but one currency ([Fernández-Rodríguez, Sosvilla-Rivero, Andrada-Félix, AFE 2003](https://econpapers.repec.org/RePEc:taf:apfiec:v:13:y:2003:i:2:p:113-122)), OOS-NET but old FX; the same authors call NN results in general "rather inconclusive" ([FEDEA 2002-05](https://econpapers.repec.org/RePEc:fda:fdaddt:2002-05)) |
| **Wavelets / wavelet coherence** | Power and co-movement by scale and time; candidate cycle periods | Edge effects (cone of influence) make the latest values the least reliable, exactly where we need them; a 4-year period has fewer than 4 full repeats in the whole history | DESC: [Kristoufek 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4398561/) (price drivers), [PSL Quarterly Review: halvings and institutions](https://rosa.uniroma1.it/rosa04/psl_quarterly_review/article/view/18744); no trading test |
| **Change-point / regime models** (Bayesian CPD, HMM, Markov switching, GSADF) | When the price process changes regime | Offline CPD uses the whole sample (look-ahead): only online/filtered probabilities are point-in-time; the number of states is tuned | DESC/risk: MS-GARCH beats single-regime GARCH for 1-day VaR ([UniNE](https://libra.unine.ch/bitstreams/68f79eef-f5b3-4954-987e-2ec953b2bf02/download)); 4-state HMM bull/bear/calm ([arXiv 2011.03741](https://arxiv.org/abs/2011.03741)); GSADF bubble dating ([JRFM 18(8):450](https://mdpi.com/1911-8074/18/8/450)). No fee-net trading |
| **CNN on chart images** | Learned price-chart patterns | Needs a cross-section (thousands of stocks); one asset has too few independent samples | US stocks, image CNN beats price-trend baselines OOS ([Jiang, Kelly, Xiu 2023, JF](https://papers.ssrn.com/abstract=3756587)); cross-sectional, not a single-asset timing result; the 2026 replication on 20 stocks ([BSIC](https://bsic.it/?p=19661)) not read in full |
| **Vision-LLM chart reading** | Narrative reading of a chart | Shortcut learning: tracks the visible trend; bias toward up or down | Benchmark: VLMs do well only in persistent up/down trends and are weak in ordinary markets ([arXiv 2604.12659](https://arxiv.org/abs/2604.12659)); "Martingale Doppelgänger" audit: models ignore injected candlestick meaning or go against it ([arXiv 2606.17423](https://arxiv.org/abs/2606.17423)). Evidence against using a VLM as the detector |
| **Deep RL / transformers on crypto** | Learned policies | Backtest overfitting: walk-forward hyper-selection is itself tuning ([Gort et al., arXiv 2209.05559](https://arxiv.org/abs/2209.05559)) | Short window (May-June 2022, 10 coins), 0.3% cost; not a fractal method |

Pitfalls that apply to every row:
1. **Look-ahead from alignment.** Aligning cycles on the *peak* or *bottom* uses a date nobody knew at the time. Only the **halving date** (known years ahead from block height) and running quantities (days since the running ATH, drawdown from the running ATH) are point-in-time. A bottom is only "known" after a rule confirms it, e.g. +X% off the low with no new low for N days, and the confirmation lag must be charged.
2. **Tiny n of cycles.** Binance BTCUSDT daily starts 2017-08-17: it holds the 2017 top, one full cycle (2018 bottom to 2021 top to 2022 bottom), and the 2024-2026 cycle. That gives **2-3 tops and 2 bottoms**, about 1 independent observation per cycle per statistic. Pre-2017 needs another public source (Bitstamp or CoinMetrics), and that still gives only 4 halvings in total.
3. **Multiple testing.** Template choice, window length, alignment anchor, metric and threshold are each a fork. Overlay posts show the best of many unseen tries (the 4chan date is the extreme case).
4. **Overlapping windows.** Consecutive sliding windows share most bars, so n of events overstates independent n. `fractal.py`'s 240-bar spacing helps, but outcomes still cluster in volatile weeks. Use week-block bootstrap, as tf_break_event_study does.
5. **Nonsense correlation.** Trending log paths correlate by chance ([Ernst et al.](https://arxiv.org/abs/1608.04120)). Compare against surrogate paths (random walks with BTC's volatility, or block-shuffled returns), never against zero.
6. **Regime and decay.** Molnar's own result is that cycle indicators decay cycle by cycle, so a fit on 2017+2021 is the wrong prior for 2025+.

---

## 3. What is fee-net out-of-sample, and what is anecdote

| Claim | Fee-net? | OOS? | Verdict |
|---|---|---|---|
| ~15k technical rules on BTC/LTC/ETH/XRP: profitable after data-snooping controls, **except BTC out-of-sample, where there is no predictability** ([Hudson & Urquhart, Ann. Oper. Res.](https://link.springer.com/article/10.1007/s10479-019-03357-1)) | break-even cost reported | yes | **The strongest negative prior for BTC rule-trading in general** |
| NN analog trading rule on EMS FX ([AFE 2003](https://econpapers.repec.org/RePEc:taf:apfiec:v:13:y:2003:i:2:p:113-122)) | yes | yes (FX, 1978-94) | OOS-NET, wrong asset and era |
| DTW features on S&P 500 ([PoliTo](https://webthesis.biblio.polito.it/39690/1/tesi.pdf)) | yes | yes, single test | OOS-NET, no consistent gain |
| Image CNN on US stocks ([JKX 2023](https://papers.ssrn.com/abstract=3756587)) | partly (turnover discussed in the paper) | yes | cross-sectional; not transferable to one asset |
| Halving-clock top timing ([Molnar 2026](https://arxiv.org/abs/2607.26188)) | no | pre-registered, unresolved | DESC; the bottom window (2026-10-05 to 2026-11-16) is open **today** |
| Local-Hurst crypto pairs ([Mathematics 2024](https://mdpi.com/2227-7390/12/18/2911)) | fragile to costs | partly | OOS-GROSS |
| Rolling Hurst / DFA / MF-DFA papers on BTC | no | no | DESC |
| Williams fractal strategies (TradingView, QuantConnect) | author-reported | no | ANECDOTE |
| Cycle overlays, "fractal repeats", lengthening cycles, the 4chan date | no | no | ANECDOTE |
| VLM chart reading | no | benchmarks only | negative evidence |

---

## 4. Prior art in this repo (read first)

| Item | What it says | Implication for a fractals layer |
|---|---|---|
| `MyTradingSys/research/drop_bounce_2026-10-29/fractal.py`, `RESULT.md` | 1m shape-analog search: z-normalised Pearson r>=0.85, 96-bar template, 240-bar spacing, range and low-position filters. n=511: low broke within 4h in 48%, up after 4h 55%, median max up +0.88% / max down -0.81%; r>=0.90 (n=314) gave the same answer. Fee-free, DESC | Meaning (c/d) at intraday scale already gave a coin flip. Also: no surrogate null, no phase context, a single template picked at a known moment (the operator's box) |
| `MyTradingSys/research/tf_break_event_study_2026-10-30/RESULT.md` + 6 VERDICTS rows | Fractal-swing break/reclaim/wick-sweep trades: **15m FAIL** in DEV and VAL (taker 0.10% round trip, 4-bar hold); 1h/4h INCONCLUSIVE; 1D/W too few events (1D 31 H / 20 R / 71 W1 over 3.5 years). Hold share of real swings is close to random pseudo-levels at 15m and 4h; at 1h it is 3-7 points higher | Meaning (a) as a trigger is mostly spent at 15m. 1h is the only frame where real swings differ from random ones |
| `FORMULAS.md` section 9 (CryptoCred fixed-width fractal swings, strict comparisons), **18.2** (fractal pivots, width n NO-SOURCE, confirmed at i+n), 18.3 (ATR size filter k), **21.4** (KR-L10 dominant low / lower high on k-bar swings, k and tol OURS) | Canonical point-in-time pivot definitions already exist | Reuse 18.2 + 18.3 for any (a)/(d) work; never redefine |
| `backtest/layers/alerts/live_levels_confluence.py` | Confirmed 5-bar 4h fractal highs/lows from the last 10 days are one of the level families | A multi-TF (d) score can plug into this family list |
| `backtest/layers/cryptocred/cc_structure.py`, `trendlines/trendline_core.py`, `krown/krown_core.py` | k-bar fractal swings feed MSB, trendline anchors and KR-L10 | (a) is plumbing, not a new layer |
| `PRE_REG_TEMPLATE.md` 0g | Coded KR-L10 "cannot see his daily last lower high" | Before any run, check that an encoded swing matches the operator's marks on 3 dated charts |
| `dsa_backtest_audit_2026-10-16/T10_missing_aspects.md` R02 | Structural breaks (listing, halving, ETF, fee changes) not tested anywhere ("NONE") | A phase tag fills a known audit gap |
| `FORMULAS.md` | No Hurst, DFA, halving-clock or DTW entry | Any (b)/(c) formula needs a new FORMULAS entry first, SOURCED from the papers above |

---

## 5. Operational definitions to test (ranked by expected value x testability)

Data: Binance BTCUSDT daily from 2017-08, 1m from 2022-01 (tf_break used 2022-01..2025-06 with HOLDOUT 2025-07+). All parameters below are **OURS** unless a source is named. Minimum n is set so that the standard error is below about half the 0.10% taker round trip for 1h-4h holds (per-trade sd of about 0.7-1.0% gives n >= 200 per split), and >= 30 per phase cell for any conditioned split.

| Rank | Definition | Point-in-time construction | Phase context | Null / shuffle test | Min n | Testable? |
|---|---|---|---|---|---|---|
| **1** | **Phase tag as a conditioning variable on existing layers** (not a trigger). Tag = (days since last halving, binned 0-180 / 180-540 / 540-900 / 900+) x (drawdown from running ATH: <10% / 10-35% / >35%) | Halving dates are known in advance; the running ATH uses only past closes. No peak or bottom date used | It *is* the context | Circular-shift the phase labels by whole months (keeps autocorrelation), 1,000 shifts; the real between-phase gap in fee-net R must sit beyond the 95th percentile. The same sign is required in each cycle instance available | >= 30 trades per cell per split; the layer itself >= 200 | **Partly.** Plenty of trades, but each phase cell comes from 1-2 cycle instances, so a phase effect cannot be told apart from "that year". Read it as "this layer is safe or unsafe in phase X so far", never as a cycle law |
| **2** | **Rolling-Hurst / DFA regime gate.** H from DFA-1 on 1h log returns over a trailing 30-day window (720 bars), refreshed daily; gate trend layers on H > q80 of a surrogate band, mean-reversion layers on H < q20 | Trailing window only; thresholds set from surrogates (shuffled returns, same window), never from outcome data | Report by phase tag (rank 1) | (i) Surrogate band: shuffle the 1h returns inside each window and recompute H; (ii) random gating with the same on-share as the real gate, 1,000 draws; the gate must beat the 95th percentile of random gates in fee-net R | >= 200 gated trades per split; >= 10 regime switches per split | **Yes** at 1h (many switches since 2022). Daily H (250-day window) gives only about 10-15 regimes since 2017: descriptive only |
| **3** | **Multi-TF nested fractal confluence (meaning d on a base).** A level counts as nested if a confirmed FORMULAS 18.2 pivot (n=2) on 1D or 4h lies within 0.25 x ATR14(1h) of a confirmed 1h pivot; test first-touch fades/holds at nested vs single-TF levels | 18.2 confirmation at i+n on each TF; higher-TF bar used only after it closes | Split by phase tag | Pseudo-level control as in tf_break (random levels with the same distance distribution) + week-block bootstrap; nested must beat single-TF *and* pseudo | >= 200 nested touches per split | **Yes.** It builds on the one positive hint (1h real swings beat random by 3-7 points) |
| **4** | **Phase-matched intraday shape analog** (extend `fractal.py`): kNN (k=50) on z-normalised 1h log-return paths of 48 bars, library = past data only, outcome = sign and size of the next 24 bars; compare to the vol-matched unconditional base | Expanding library (only windows ending before t); no template picked at a known turn: run on *every* window on a fixed grid | Only neighbours from the same phase tag and volatility tercile | Surrogate library of random walks with BTC's volatility (nonsense-correlation control) + block-shuffled outcomes; Holm correction over horizons | >= 500 non-overlapping forecasts per split | **Yes**, but the prior is weak: the 1m version gave a coin flip and the FX NN evidence is old |
| **5** | **Halving-aligned cycle-path correlation** (meaning c): r between the current cycle's log path since its halving and each prior cycle's, plus the halving-clock window for tops and bottoms | Halving alignment only (point-in-time). **Peak or bottom alignment is banned** (look-ahead) | It defines the phase | Block-bootstrap path null as in Molnar; there is nothing to shuffle across cycles | n = 3 prior cycles (2 on Binance data) | **Not testable as a trading claim.** With 3-4 cycles, no p-value is meaningful and any fit has as many parameters as observations. Use it only as a described context line, and log Molnar's pre-registered bottom window (2026-10-05 to 2026-11-16) as one live, n=1 check |

Where n kills the claim (plain words):
- "This cycle is repeating the 2017 (or 2021) cycle": **untestable**, n=3.
- "The top or bottom comes X days after the halving": **untestable as a trade**. It can only be logged forward, one event every ~4 years.
- "A 2019 structure is repeating at a lower timeframe": testable only as rank 4 (many intraday windows, surrogate null). The single hand-picked repeat analysts show is an anecdote.
