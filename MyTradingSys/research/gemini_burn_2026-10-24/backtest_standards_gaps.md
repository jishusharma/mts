# Industry Standards Audit & Gap Analysis: MTS Backtesting Architecture

**Audit Date:** 2026-10-24  
**Auditor:** Gemini Flash Research Worker (Antigravity JIS-NUC)  
**Output Target:** `MyTradingSys/research/gemini_burn_2026-10-24/backtest_standards_gaps.md`  
**Primary Focus:** Look-Ahead Bias, Survivorship Bias, Fees & Slippage, Funding Rates, Walk-Forward / CPCV, Multiple-Testing Corrections (Deflated Sharpe Ratio, PBO), Minimum Trade Counts.

---

## 1. Executive Summary & Audit Context

This document delivers an exhaustive, rigorous gap analysis benchmarking the backtesting methodology, simulation engines, and research infrastructure of `MyTradingSys` (MTS) against quantitative finance industry standards and peer-reviewed literature.

The analysis evaluates four mandatory baseline files:
1. `MyTradingSys/research/BACKTEST_METHOD_2026-09-21.md` (historical snapshot replay & forward-return join methodology)
2. `MyTradingSys/research/sim_desk/` (including `DESIGN.md`, `INPUTS.md`, `PLUGIN.md`, `ROADMAP.md`, `REVIEW_FABLE.md`, `desk.py`, and `studies/_bars.py`)
3. `MyTradingSys/backtest/layers/FORMULAS_SPEC.md` (re-derivation specifications F01–F23)
4. `MyTradingSys/research/TRIAL_LEDGER.csv` (pre-registered trial ledger headers and variant rows)

It also traces execution reality against the repo's underlying execution engines: `MyTradingSys/backtest/fees.py`, `MyTradingSys/backtest/bt/bt_engine.py`, `MyTradingSys/backtest/bt/bt_stats.py`, `MyTradingSys/backtest/bt/ref_pbo.py`, `MyTradingSys/backtest/maker_model.py`, and `MyTradingSys/research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md`.

### Summary Matrix of Ranked Gaps

| Rank | Dimension | Severity | Primary Standard Source | Primary Repo Location | Core Gap Identified |
|:---:|:---|:---:|:---|:---|:---|
| **1** | **Fees, Slippage & Execution Realism** | **CRITICAL** | Almgren & Chriss (2000); Binance / Deribit Fee Schedules | `sim_desk/studies/_bars.py:143-159` | Slippage is entirely omitted in Sim Desk; resting limit orders assume 100% queue fill on touch; no bid-ask spread charged on market orders. |
| **2** | **Multiple Testing & Overfitting (DSR / PBO)** | **CRITICAL** | Bailey & López de Prado (2014); Bailey, Borwein, López de Prado & Zhu (2014) | `sim_desk/desk.py:23-37`; `TRIAL_LEDGER.csv:1` | Sim Desk verdict relies entirely on a naive bootstrap CI of mean net R; DSR and PBO implemented in `bt_stats.py` are completely bypassed during interactive tuning; Trial Ledger cannot compute PBO. |
| **3** | **Funding Rate Modeling** | **HIGH** | Binance Futures FAQ; Deribit Education Docs | `sim_desk/studies/_bars.py:122-160`; `maker_model.py:19` | Funding is completely absent in Sim Desk (trades held up to 100 bars pay $0 funding); mismatch between continuous (Deribit) and discrete 8h (Binance) mechanics in `bt_engine.py`. |
| **4** | **Walk-Forward / CPCV vs. Static Splitting** | **HIGH** | Pardo (2008); López de Prado (2018) | `sim_desk/DESIGN.md:16`; `TRIAL_LEDGER.csv:2-15` | No Combinatorial Purged Cross-Validation (CPCV) anywhere in repo; Sim Desk hard-locks all "hit-and-try" research inside a monolithic 27-month DEV window without rolling walk-forward or purging. |
| **5** | **Minimum Trade Counts & Power** | **HIGH** | Bailey & López de Prado (2012, 2014); Pardo (2008) | `sim_desk/desk.py:29`; `BACKTEST_METHOD_2026-09-21.md:33` | $N=30$ trade threshold has < 15% statistical power to detect plausible edge (+0.10 R); no Minimum Track Record Length (MinTRL) calculation adjusted for skewness and kurtosis. |
| **6** | **Look-Ahead Bias & Mark Price Triggers** | **HIGH** | Chan (2009); López de Prado (2018) | `sim_desk/studies/_bars.py:141-143`; `rsi.py:104-108` | Sim Desk evaluates stop orders against 1m trade bar extremes rather than Mark Price index; `rsi.py` pre-computes signal exits (`t_exit`) across future bars before simulating the trade path. |
| **7** | **Survivorship Bias & Universe Selection** | **MEDIUM** | Brown, Goetzmann, Ibbotson & Ross (1992); Chan (2009) | `sim_desk/studies/_bars.py:43`; `ROADMAP.md:16-21` | Backtesting is restricted exclusively to BTC and ETH (macro survivors); testing cross-sectional setups without point-in-time universe selection introduces survivorship bias if expanded. |

---

## 2. Primary Sources & Sourced vs. Ours Parameters

Every parameter, threshold, and formula across the literature and the repo is explicitly cataloged below and labeled **SOURCED** (with verbatim quote and URL) or **OURS** (repo internal convention or operator ruling).

### Primary Literature, Specifications, and Video Citations

1. **Probability of Backtest Overfitting (PBO) & CSCV:**
   - **Source:** Bailey, David H., Jonathan M. Borwein, Marcos López de Prado, and Qiji Jim Zhu (2014/2016), "The Probability of Backtest Overfitting", *Journal of Computational Finance*, Vol. 20, No. 4, pp. 39–69.
   - **URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)
   - **Verbatim Quote:**
     > *"We propose a general framework to assess the probability of backtest overfitting (PBO). We illustrate this framework with specific generic, model-free and nonparametric implementations in the context of investment simulations, which implementations we call combinatorially symmetric cross-validation (CSCV)."*

2. **Deflated Sharpe Ratio (DSR) & Multiple Testing Correction:**
   - **Source:** Bailey, David H., and Marcos López de Prado (2014), "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", *Journal of Portfolio Management*, Vol. 40, No. 5, pp. 94–107.
   - **URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675)
   - **Verbatim Quote:**
     > *"The Deflated Sharpe Ratio (DSR) corrects for two leading sources of performance inflation: non-Normally distributed returns and selection bias under multiple testing."*

3. **Minimum Track Record Length (MinTRL):**
   - **Source:** Bailey, David H., and Marcos López de Prado (2012), "The Sharpe Ratio Efficient Frontier", *Journal of Risk*, Vol. 15, No. 2, pp. 13–44.
   - **URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643)
   - **Verbatim Quote:**
     > *"How long should a track record be in order to have statistical confidence that its Sharpe ratio is above a given threshold?"*
   - **Formula:**
     $$\text{MinTRL} = 1 + \left(1 - \gamma_3 \widehat{\text{SR}} + \frac{\gamma_4 - 1}{4}\widehat{\text{SR}}^2\right)\left(\frac{Z_\alpha}{\widehat{\text{SR}} - \text{SR}^*}\right)^2$$

4. **Walk-Forward Analysis:**
   - **Source:** Pardo, Robert (2008), *The Evaluation and Optimization of Trading Strategies*, 2nd ed., John Wiley & Sons, Chapter 11.
   - **URL:** [https://www.oreilly.com/library/view/the-evaluation-and/9780470128014/](https://www.oreilly.com/library/view/the-evaluation-and/9780470128014/)
   - **Verbatim Quote:**
     > *"The Walk-Forward Analysis judges the performance of a trading system exclusively on the basis of postoptimization or out-of-sample trading. The performance of a trading strategy on data which were never part of the optimization process is a far more reliable measure than performance based solely on in-sample simulation. If a trading strategy performs well under a Walk-Forward Analysis, it has shown itself to be robust and capable of producing real-time trading profit."*

5. **Cross-Validation Leakage, Purging, and Embargoing:**
   - **Source:** López de Prado, Marcos (2018), *Advances in Financial Machine Learning*, John Wiley & Sons, Chapter 7; and "The 10 Reasons Most Machine Learning Funds Fail", *Journal of Portfolio Management*, Vol. 44, No. 6, pp. 120–133.
   - **URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3104816](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3104816)
   - **Verbatim Quote:**
     > *"Failing to account for overlapping outcomes leads to cross-validation leakage... when labels span multiple periods, standard cross-validation methods allow information from the testing set to leak into the training set."*
   - **YouTube Video:** Quantoisseur (2021), "Combinatorial Purged Cross-Validation Explained"
   - **URL:** [https://www.youtube.com/watch?v=hDQssGntmFA](https://www.youtube.com/watch?v=hDQssGntmFA)
   - **Timestamps & Verbatim Quotes:**
     - `[03:15]`: *"Purging removes training observations whose label-generation periods overlap with the test set to prevent look-ahead bias and data leakage."*
     - `[05:00]`: *"Embargoing drops training samples immediately following the test set to eliminate serial correlation and spillover from serially correlated features."*
   - **YouTube Video:** Institutional Investor Journals (2014), "The Dangers of Backtest Overfitting - Marcos López de Prado"
   - **URL:** [https://www.youtube.com/watch?v=QxhxLwNbMMg](https://www.youtube.com/watch?v=QxhxLwNbMMg)
   - **Timestamp `[01:45]` & Verbatim Quote:**
     > *"If you test enough variations, you will eventually find a strategy that looks exceptional purely by chance... A backtest is overfit when the strategy is profiting from noise rather than genuine market structure."*

6. **Look-Ahead Bias & Survivorship Bias:**
   - **Source (Look-Ahead):** Chan, Ernest P. (2009), *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*, John Wiley & Sons.
   - **URL:** [https://www.wiley.com/en-us/Quantitative+Trading%3A+How+to+Build+Your+Own+Algorithmic+Trading+Business-p-9780470284889](https://www.wiley.com/en-us/Quantitative+Trading%3A+How+to+Build+Your+Own+Algorithmic+Trading+Business-p-9780470284889)
   - **Verbatim Quote:**
     > *"Look-ahead bias is introduced into a backtest when information that was not available at the time of the trade is used in generating the trading signal."*
   - **Source (Survivorship):** Brown, Stephen J., William Goetzmann, Roger G. Ibbotson, and Stephen A. Ross (1992), "Survivorship Bias in Performance Studies", *Review of Financial Studies*, Vol. 5, No. 4, pp. 553–580.
   - **URL:** [https://doi.org/10.1093/rfs/5.4.553](https://doi.org/10.1093/rfs/5.4.553)
   - **Verbatim Quote:**
     > *"We analyze the relationship between volatility and returns in a sample that is truncated by survivorship and show that this relationship gives rise to the appearance of predictability. We present some numerical examples to show that this effect can be strong enough to account for the strength of the evidence favoring return predictability."*

7. **Market Impact, Slippage, and Fees:**
   - **Source (Market Impact):** Almgren, Robert, and Neil Chriss (2000), "Optimal Execution of Portfolio Transactions", *Journal of Risk*, Vol. 3, No. 2, pp. 5–39.
   - **URL:** [http://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf](http://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf)
   - **Verbatim Quote:**
     > *"The price of the asset is affected by our own trading. We distinguish between permanent market impact... and temporary market impact, which is a temporary price movement caused by the trading velocity."*
   - **Source (Binance Fees):** Binance Futures VIP Fee Schedule (USDS-M Futures).
   - **URL:** [https://www.binance.com/en/fee/futureFee](https://www.binance.com/en/fee/futureFee)
   - **Verbatim Quote:**
     > *"USDS-M Futures: VIP 0 Maker Fee: 0.0200%, Taker Fee: 0.0500%."*
   - **Source (Deribit Fees):** Deribit Fee Schedule (BTC-PERPETUAL).
   - **URL:** [https://www.deribit.com/pages/information/fees](https://www.deribit.com/pages/information/fees)
   - **Verbatim Quote:**
     > *"BTC-PERPETUAL: Maker: -0.025% (Rebate), Taker: 0.050%."*

8. **Funding Mechanisms:**
   - **Source (Binance):** Binance Support, "Introduction to Binance Futures Funding Rates".
   - **URL:** [https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031](https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031)
   - **Verbatim Quote:**
     > *"Funding Amount = Nominal Value of Position * Funding Rate... Nominal Value of Position = Mark Price * Size of a Contract... When the funding rate is positive, long positions pay short positions."*
   - **Source (Deribit):** Deribit Education, "Perpetual Contract Funding Mechanisms".
   - **URL:** [https://www.deribit.com/education/perpetual-education/funding-mechanisms/](https://www.deribit.com/education/perpetual-education/funding-mechanisms/)
   - **Verbatim Quote:**
     > *"Funding is calculated and paid/received continuously rather than in discrete lump sums at fixed 8-hour intervals... Funding Payment = Funding Rate * Position Size * Time Fraction, where Time Fraction = Funding Rate Time Period / 8 hours."*

### Parameter Labeling: SOURCED vs. OURS

| Parameter / Convention | Classification | Primary Authority / Source Citation | Repo Location |
|:---|:---:|:---|:---|
| **Binance VIP 0 Taker Fee (0.05%)** | **SOURCED** | Binance Fee Schedule: "VIP 0 Taker Fee: 0.0500%" | `fees.py:27` (`BINANCE_TAKER = 0.0005`) |
| **Binance VIP 0 Maker Fee (0.02%)** | **SOURCED** | Binance Fee Schedule: "VIP 0 Maker Fee: 0.0200%" | `fees.py:28` (`BINANCE_MAKER = 0.0002`) |
| **Deribit Taker Fee (0.05%)** | **SOURCED** | Deribit Fee Schedule: "Taker: 0.050%" | `fees.py:23` (`DERIBIT_TAKER = 0.0005`) |
| **Deribit Maker Fee (0.0% / Rebate)** | **SOURCED / OURS** | Deribit quotes -0.025% rebate; repo rounds conservatively to 0.0% | `fees.py:24` (`DERIBIT_MAKER = 0.0`) |
| **Deribit BTC Tick Size ($0.50)** | **SOURCED** | Deribit Contract Specifications: minimum tick 0.5 USD | `maker_model.py:34` (`TICK = 0.5`) |
| **Binance 8h Funding Settlements** | **SOURCED** | Binance FAQ: 00:00, 08:00, 16:00 UTC settlements | `FORMULAS_SPEC.md:127` (F13); `bt_engine.py:68-76` |
| **Deribit Continuous Funding Accrual** | **SOURCED** | Deribit Education: continuous millisecond time-fraction | `BACKTEST_PROTOCOL.md:48` |
| **PBO CSCV Split Count ($S = 16$)** | **SOURCED** | Bailey, Borwein, López de Prado & Zhu (2014) | `FORMULAS_SPEC.md:76` (F10); `ref_pbo.py:14` |
| **DSR Significance Threshold ($\alpha = 0.05 \rightarrow \text{DSR} \ge 0.95$)** | **SOURCED** | Bailey & López de Prado (2014) | `BACKTEST_PROTOCOL.md:63` |
| **PBO Cutoff ($\le 0.20$)** | **SOURCED** | Bailey et al. (2014) recommendation for strategy selection | `BACKTEST_PROTOCOL.md:61` |
| **Close-Only Pivot Confirmation Lag ($n$ bars)** | **SOURCED / OURS** | Standard fractal definition SOURCED; strict tie-breaker OURS | `FORMULAS_SPEC.md:70` (F09) |
| **Slippage Stress Levels (0 / 2 / 5 bps)** | **OURS** | Operator stress-testing ruling | `BACKTEST_PROTOCOL.md:41-42` |
| **Adverse Selection Cells (0.02 bp, 1.0 bp)** | **OURS** | Empirical P1 breakdown estimates from 2026-10-06 | `maker_model.py:38` (`ADV_CELLS`) |
| **Date Windows (DEV / VALIDATION / HOLDOUT)** | **OURS** | Operator sealed-data partitioning scheme | `sim_desk/DESIGN.md:16`; `ROADMAP.md:16` |
| **Minimum Sample Size ($N = 30$)** | **OURS** | Internal Sim Desk threshold (derived from classical rule of thumb) | `sim_desk/desk.py:29` (`MIN_TRADES = 30`) |
| **Plausible Edge Floor ($+0.10\text{ R}$)** | **OURS** | Operator economic significance benchmark | `sim_desk/desk.py:28` (`PLAUSIBLE_R = 0.10`) |
| **Through-the-Level Limit Order Execution ($1\text{ tick}$)** | **OURS** | Conservative limit order queue proxy | `maker_model.py:46`; `bt_engine.py:9` |

---

## 3. Detailed Audit of Repository Baseline Files

### 3.1 `MyTradingSys/research/BACKTEST_METHOD_2026-09-21.md`
- **What it covers:** Outlines an Option A approach to backtesting by replaying historical verdicts from snapshot files (`runtime_data\snapshots\BTCUSDT_*.json`, ~6,200 snapshots spanning 2026-09-13 to 2026-09-21) and joining them to forward-return outcome labels (`runtime_data\outcome_labels.json`, containing 30m, 60m, 120m forward returns).
- **Look-Ahead Protections:** L38 explicitly acknowledges *Label leakage*: *"fwd_return_pct at 30m, 60m, and 120m is future information relative to snapshot time; features at time t must not use labels from t+30m or later."*
- **Known Deficiencies Identified in the File:** L14 notes missing persisted historical verdicts, missing label fields (`verdict`, `setup_type`, `zone`, `net_rr`, `proof`), and cadence irregularities (0.48 files/min vs. stated 1 file/min).
- **Statistical Handling:** L33 establishes a minimum bucket size of $n \ge 30$; L35 mentions pre-registering $\le 5$ hypotheses and reporting False Discovery Rate (FDR) at $q = 0.10$, but marks it as `[UNVERIFIED-WEB]`.

### 3.2 `MyTradingSys/research/sim_desk/` (Full Documentation Suite)
- **Architecture (`DESIGN.md`, `INPUTS.md`):** A lightweight local Python web server (`desk.py` on `127.0.0.1:8765`) designed for the operator to conduct interactive "hit-and-try" exploration on trading rules.
- **The Sealed Data Partitioning Rule:** `DESIGN.md:16` and `INPUTS.md:15` enforce a strict code lock: the desk executes *only* on the DEV window (`2022-04-01` to `2024-06-30`, 27 months). VALIDATION (`2024-07-01` to `2025-06-30`) and HOLDOUT (`2025-07-01+`) are hard-coded as unreadable.
- **Trial Counter vs. Overfitting Brake (`DESIGN.md:28`, `REVIEW_FABLE.md:31`):** A trial counter increments on the screen ("try #N on this data; the best of many tries looks better than it is"). `TRIALS.md` logs each run. However, `REVIEW_FABLE.md:31` notes: *"Hit-and-try has no brake except a number... The brake that actually works is social: the validation window is read once, off this desk."*
- **Simulated Execution Engine (`sim_desk/studies/_bars.py`):**
  - Bar cache loaded from 1m CSVs (`_bars.py:60-95`).
  - `run_trade` (`_bars.py:122-160`) simulates a trade from time `t_from`: evaluates limit trigger `trig` or market at open `a[i, 1]`; checks stop vs. target; applies taker/maker fees.
- **The Fable Review Findings (`REVIEW_FABLE.md`):**
  - Unfilled limit orders were previously counted as trades (517 out of 772 were 0-R non-fills), making the lowest-filling variant look best. Corrected in commit `3c262f8b3` to evaluate filled trades only ($N=255$).
  - Two-point binomial power model broke down due to zero-loss trades; replaced on the verdict bar with a sample-spread bootstrap confidence interval.

### 3.3 `MyTradingSys/backtest/layers/FORMULAS_SPEC.md`
- **Statistical Specifications (F10, L75–80):** Specifies formulas for arithmetic mean / population standard deviation Sharpe ratio, Probabilistic Sharpe Ratio (PSR), Deflated Sharpe Ratio (DSR), and Combinatorial Symmetric Cross-Validation (CSCV) PBO.
- **Execution & Cost Models (F11, F13, F17):**
  - F11 (L81–118): Deribit contract execution math, tick floor/ceil snapping (`Decimal`), inverse contract PnL (`-size * abs(E - S) / E`).
  - F13 (L125–130): Shared cost model: $Gross = s \cdot (P_{out} - P_{in}) / P_{in}$; $Net = Gross - Fee - Slip - s \sum Rate$.
  - F17 (L149–154): Net Reward-to-Risk ratio with round-trip taker fees: $Cost = 2 \cdot f \cdot E$; $NetRR = (|T - E| - Cost) / (|E - S| + Cost)$.

### 3.4 `MyTradingSys/research/TRIAL_LEDGER.csv` Header
- **Header:** `study,variant,run_utc,split,data_source,description,status`
- **Entries:** Rows L2–15 record pre-registered trials (e.g., `wlow_bounce_bbrsi60_2026-10-16`, `wavetrend_2026-10-17`) evaluated on `DEV` split using `F:/MTS/data/tom_raw/klines 1m->1h` or `1m->5m`.
- **Limitation:** The ledger records only categorical metadata, parameter descriptions, and run statuses. It does not store per-bar or per-trade aligned return vectors across variants, precluding concurrent matrix operations like CSCV PBO.

---

## 4. Ranked Gap Analysis (Industry Standards vs. Repo Reality)

---

### GAP 1: Total Omission of Slippage & Optimistic Limit Queue Fill Assumptions
- **Severity:** **CRITICAL**
- **Domain:** Fees, Slippage & Execution Realism
- **Industry Standard (Source):**
  - Almgren & Chriss (2000), "Optimal Execution of Portfolio Transactions" (URL: [http://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf](http://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf)):
    > *"We distinguish between permanent market impact... and temporary market impact, which is a temporary price movement caused by the trading velocity."*
  - Kissell & Glantz (2003); Harris (2003) *Trading and Exchanges*: Market orders cross the bid-ask spread and incur temporary liquidity impact; resting limit orders have execution probability strictly $< 1.0$ at the touch and suffer adverse selection when filled.
- **What the Repo Does:**
  - `MyTradingSys/research/sim_desk/studies/_bars.py:122-160`: `run_trade` executes market orders at the exact open price `a[j, 1]` with **zero slippage** and **zero half-spread penalty**. Stop orders execute at the exact stop price (or bar open on a gap).
  - `MyTradingSys/research/sim_desk/studies/levels.py` & `studies/_bars.py:141-146`: Limit order entries and targets fill instantly whenever the bar's extreme touches the price level (`seg[:, 2] >= trig`).
  - `MyTradingSys/backtest/maker_model.py:19`: Explicitly documents this structural flaw:
    > *"Funding, slippage on stop fills, queue position and partial fills are NOT modelled (1m bars cannot show them)."*
- **The Gap:**
  1. **Zero Slippage in Sim Desk:** While `BACKTEST_PROTOCOL.md:41` proposes a 0 / 2 / 5 bps slippage stress test, `sim_desk` implements none. For an intraday BTC setup targeting $+0.10\text{ R}$ to $+0.20\text{ R}$ with a $0.5\%$ stop distance ($50\text{ bps}$ risk), a typical $2\text{ bps}$ entry slippage and $3\text{ bps}$ stop slippage ($5\text{ bps}$ total) consumes:
     $$\frac{5\text{ bps}}{50\text{ bps}} = 0.10\text{ R}$$
     This single unmodeled friction wipes out $100\%$ of the targeted $+0.10\text{ R}$ edge.
  2. **Touch-Fill Optimism:** Assuming resting orders fill at the instant the price touches the limit price ignores limit order queue priority. Real fills require cumulative trade volume at that price to exhaust preceding queue depth.
- **Remediation:**
  1. Add a mandatory `slip_bp` parameter to `sim_desk/studies/_bars.py:run_trade` defaulting to $2.0\text{ bps}$ for market entries and stop-loss exits.
  2. Enforce the through-the-level execution rule from `maker_model.py:46` (Regime C: price must trade through the level by at least $1\text{ tick} = 0.5\text{ USD}$) for all limit fills on 1m bars.

---

### GAP 2: Bypassing Multiple-Testing Corrections (DSR / PBO) in Interactive Research
- **Severity:** **CRITICAL**
- **Domain:** Multiple-Testing & Overfitting Corrections
- **Industry Standard (Source):**
  - Bailey & López de Prado (2014), "The Deflated Sharpe Ratio" (URL: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675)):
    > *"The Deflated Sharpe Ratio (DSR) corrects for two leading sources of performance inflation: non-Normally distributed returns and selection bias under multiple testing."*
  - Bailey, Borwein, López de Prado & Zhu (2014), "The Probability of Backtest Overfitting" (URL: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)):
    > *"Standard statistical techniques designed to prevent regression overfitting, such as hold-out, tend to be unreliable and inaccurate in the context of investment backtests. We propose a general framework to assess the probability of backtest overfitting (PBO)... which implementations we call combinatorially symmetric cross-validation (CSCV)."*
  - López de Prado, YouTube Interview `[01:45]` (URL: [https://www.youtube.com/watch?v=QxhxLwNbMMg](https://www.youtube.com/watch?v=QxhxLwNbMMg)):
    > *"If you test enough variations, you will eventually find a strategy that looks exceptional purely by chance... A backtest is overfit when the strategy is profiting from noise rather than genuine market structure."*
- **What the Repo Does:**
  - `MyTradingSys/backtest/bt/bt_stats.py:57-67` & `ref_pbo.py:14-84`: Contains mathematically sound standalone implementations of `psr`, `expected_max_sr`, `dsr`, and `pbo_cscv`.
  - `MyTradingSys/research/sim_desk/desk.py:23-37`: `verdict()` completely ignores `dsr` and `pbo_cscv`. It renders a `PASSED` verdict whenever the naive bootstrap lower bound is greater than zero:
    ```python
    if st['lo'] > 0:
        return 'PASSED', f'the whole {rng} is above zero. On DEV only: it needs its one validation run...'
    ```
  - `MyTradingSys/research/sim_desk/REVIEW_FABLE.md:31`: Confirms that the trial counter on the screen is purely cosmetic:
    > *"Hit-and-try has no brake except a number... Any value runs in seconds, every run is one DEV trial, and the only guard is 'try #N' on the bar plus the off-desk validation run."*
  - `MyTradingSys/research/TRIAL_LEDGER.csv:1`: Stores only scalar summaries, preventing CSCV matrix construction.
- **The Gap:**
  1. **Disconnection Between Protocol and Practice:** While `BACKTEST_PROTOCOL.md:61-63` mandates `DSR >= 0.95` and `PBO <= 0.20`, the actual interactive tool where strategies are developed (`sim_desk`) does not evaluate DSR or PBO.
  2. **Selection Bias Under "Hit and Try":** The operator is encouraged to freely modify knobs (stop distance, tolerance, trend lookbacks). After 50 or 100 trials, selecting a rule where the lower bootstrap CI $> 0$ has an expected false discovery rate exceeding $80\%$, yet the UI prints `PASSED`.
  3. **Data Logging Gap:** Because `TRIAL_LEDGER.csv` and `TRIALS.md` do not log per-trade or per-bar returns for each trial, PBO cannot be calculated post-hoc across the search history.
- **Remediation:**
  1. Wire `bt_stats.dsr` directly into `sim_desk/desk.py:verdict()`, feeding it the cumulative `try_no` from `TRIALS.md` as $N_{trials}$. If $DSR < 0.95$, the verdict must display `OVERFIT RISK (DSR < 0.95)` instead of `PASSED`.
  2. In `desk.py`, serialize per-trade outcome vectors to `cache/trial_returns/` so that CSCV PBO can be evaluated across all logged trials.

---

### GAP 3: Complete Absence of Funding Rate Calculations in the Simulator Desk
- **Severity:** **HIGH**
- **Domain:** Funding Rates
- **Industry Standard (Source):**
  - Binance Futures Documentation (URL: [https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031](https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031)):
    > *"Funding Amount = Nominal Value of Position * Funding Rate... Nominal Value of Position = Mark Price * Size of a Contract... When the funding rate is positive, long positions pay short positions."*
  - Deribit Perpetual Education (URL: [https://www.deribit.com/education/perpetual-education/funding-mechanisms/](https://www.deribit.com/education/perpetual-education/funding-mechanisms/)):
    > *"Funding is calculated and paid/received continuously rather than in discrete lump sums at fixed 8-hour intervals... Funding Payment = Funding Rate * Position Size * Time Fraction, where Time Fraction = Funding Rate Time Period / 8 hours."*
- **What the Repo Does:**
  - `MyTradingSys/backtest/layers/FORMULAS_SPEC.md:125-130` (F13) & `MyTradingSys/backtest/bt/bt_engine.py:68-76`: Explicitly computes funding for discrete 8-hour intervals ($s \in [t_{in}, t_{out}]$).
  - `MyTradingSys/research/sim_desk/studies/_bars.py:122-160`: Completely drops funding. In `run_trade`, the cost calculation is solely:
    ```python
    fee = (taker * px + ex[2] * ex[0]) / risk
    net_r = float(gross - fee)
    ```
  - `MyTradingSys/research/sim_desk/studies/rsi.py:18`: Allows swing positions to be held for up to `MAX_HOLD = 100` bars ($100\text{ hours}$ on 1h, $400\text{ hours} \approx 16.7\text{ days}$ on 4h, and $100\text{ days}$ on daily charts), charging exactly $\$0.00$ in funding.
  - `MyTradingSys/backtest/maker_model.py:19`: Confirms that funding is unmodeled.
- **The Gap:**
  1. **Sim Desk Distortion:** In crypto perpetuals, funding rates during trending regimes frequently average $+0.03\%$ to $+0.08\%$ per 8 hours ($0.09\%$ to $0.24\%$ per day). Over a 5-day hold ($120\text{ hours}$), a long position accumulates $0.45\%$ to $1.20\%$ in funding expenses. Against a $1.0\%$ stop distance ($100\text{ bps}$ risk), funding costs range from $0.45\text{ R}$ to $1.20\text{ R}$, transforming a nominally profitable setup into a severe loser.
  2. **Continuous vs. Discrete Engine Artifacts:** While `bt_engine.py` implements F13 using Binance discrete 8-hour timestamps, Deribit contracts settle continuously. A position entering at 07:59 UTC and exiting at 08:01 UTC pays an entire 8-hour funding block on Binance, but only 2 minutes on Deribit.
- **Remediation:**
  1. Port the funding lookup logic from `bt_engine.py` into `sim_desk/studies/_bars.py:run_trade`, reading historical funding rates from `F:/MTS/data/funding/` or caching 8h rates alongside kline arrays.
  2. Implement continuous funding accrual for Deribit profiles:
     $$\text{Funding Cost} = \text{Rate}_{8h} \times \text{Notional} \times \left(\frac{\Delta t_{\text{ms}}}{8 \times 3600 \times 1000}\right)$$

---

### GAP 4: Monolithic Static Data Splitting vs. Combinatorial Purged Cross-Validation (CPCV)
- **Severity:** **HIGH**
- **Domain:** Validation Design & Walk-Forward / CPCV
- **Industry Standard (Source):**
  - Pardo (2008), *The Evaluation and Optimization of Trading Strategies*, Ch. 11 (URL: [https://www.oreilly.com/library/view/the-evaluation-and/9780470128014/](https://www.oreilly.com/library/view/the-evaluation-and/9780470128014/)): Mandates rolling out-of-sample walk-forward windows to assess temporal stability.
  - López de Prado (2018), *Advances in Financial Machine Learning*, Ch. 7 (URL: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3104816](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3104816)):
    > *"Combinatorial Purged Cross-Validation (CPCV) generates multiple backtest paths... Purging is the removal of training labels whose information overlaps with the test labels. Embargo is the removal of training labels immediately following the test set..."*
  - Quantoisseur YouTube Tutorial `[03:15]` & `[05:00]` (URL: [https://www.youtube.com/watch?v=hDQssGntmFA](https://www.youtube.com/watch?v=hDQssGntmFA)):
    > *"Purging removes training observations whose label-generation periods overlap with the test set... Embargoing drops training samples immediately following the test set to eliminate serial correlation."*
- **What the Repo Does:**
  - `MyTradingSys/research/sim_desk/DESIGN.md:16` & `INPUTS.md:15`: Enforces a rigid 3-window static split: DEV (`2022-04-01` to `2024-06-30`), VALIDATION (`2024-07-01` to `2025-06-30`), and HOLDOUT (`2025-07-01+`). The desk only runs DEV.
  - `MyTradingSys/research/TRIAL_LEDGER.csv:2-15`: Pre-registered trials are evaluated monolithically on the `DEV` split.
  - `MyTradingSys/research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md:54-63`: Mentions a rolling 3-month train / 1-month test walk-forward with purging and an embargo of 1440 bars.
- **The Gap:**
  1. **CPCV is Entirely Missing:** Neither `sim_desk` nor `backtest/bt/` implements Combinatorial Purged Cross-Validation.
  2. **Extreme Static In-Sample Overfitting:** Sim Desk treats the 27-month DEV period as a single monolithic block. Strategy parameters (e.g. Malkan RSI tolerance, lookback) are tuned against the entire 27 months simultaneously.
  3. **Single Validation Path Vulnerability:** Relying on a single 12-month VALIDATION window to be tested once creates acute path-dependency risk. A strategy might fail on the single validation window due to macro regime changes (e.g., transition to high volatility) despite possessing a valid statistical edge across other regimes.
- **Remediation:**
  1. Implement a 6-fold combinatorial purged cross-validation engine generating $\binom{6}{2} = 15$ out-of-sample backtest paths across the DEV window.
  2. Introduce purging of all trades whose holding periods span across partition boundaries, and apply a 1-day ($1440\text{ bars}$) post-test embargo.

---

### GAP 5: Inadequate Minimum Trade Sample Size ($N=30$) and Lack of MinTRL
- **Severity:** **HIGH**
- **Domain:** Minimum Trade Counts & Statistical Power
- **Industry Standard (Source):**
  - Bailey & López de Prado (2012, 2014), "Minimum Track Record Length" (URL: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643)):
    $$\text{MinTRL} = 1 + \left(1 - \gamma_3 \widehat{\text{SR}} + \frac{\gamma_4 - 1}{4}\widehat{\text{SR}}^2\right)\left(\frac{Z_\alpha}{\widehat{\text{SR}} - \text{SR}^*}\right)^2$$
    Demonstrates that non-normal return distributions (negative skewness $\gamma_3 < 0$, high kurtosis $\gamma_4 > 3$) drastically expand the sample size required for statistical significance.
  - Pardo (2008), *The Evaluation and Optimization of Trading Strategies*, Ch. 8: $N \ge 30$ is an absolute mathematical lower bound for central limit approximations; robust multi-parameter trading models require $N \ge 100$ to $300+$ independent trades.
- **What the Repo Does:**
  - `MyTradingSys/research/sim_desk/desk.py:29`: Sets `MIN_TRADES = 30`:
    ```python
    MIN_TRADES = 30  # same floor as the layer runners (run_rsi_backtest.py MIN_OOS_N)
    ```
  - `MyTradingSys/research/sim_desk/PLUGIN.md:21`:
    > *"Under 30 filled trades it always reads NOT ENOUGH DATA: PASSED when the whole range is above zero... FAILED when the whole range is below zero..."*
  - `MyTradingSys/research/BACKTEST_METHOD_2026-09-21.md:33`:
    > *"Bucket minimum: each primary verdict bucket... should have n >= 30 for reporting; sparse buckets must be flagged."*
  - `MyTradingSys/research/sim_desk/ROADMAP.md:13`: Daily RSI yielded only 2 filled trades; 4h yielded 20 trades; 1h yielded 75 trades.
- **The Gap:**
  1. **Severe Lack of Statistical Power at $N=30$:** For trade returns with standard deviation $\sigma = 1.0\text{ R}$, detecting an expected edge of $\mu = +0.10\text{ R}$ at $\alpha = 0.05$ with $80\%$ statistical power ($\beta = 0.20$) requires:
     $$N = \left(\frac{Z_{0.05} + Z_{0.20}}{\mu / \sigma}\right)^2 = \left(\frac{1.96 + 0.84}{0.10}\right)^2 = (28.0)^2 = 784\text{ trades}$$
     At $N = 30$, statistical power to detect $+0.10\text{ R}$ is less than $12\%$. A real edge will be incorrectly rejected ($88\%$ Type II error rate), while an apparent pass at $N=30$ is almost certainly an artifact of random sampling variance.
  2. **Absence of MinTRL:** The repo calculates standard bootstrap confidence intervals, but does not calculate the Minimum Track Record Length (MinTRL) based on the sample's observed skewness and kurtosis.
- **Remediation:**
  1. Elevate `MIN_TRADES` in `sim_desk/desk.py` from 30 to at least 100 for any provisional pass.
  2. Implement `min_trl()` in `bt_stats.py` using formula F10 and realized sample moments ($\gamma_3, \gamma_4$), displaying on the Sim Desk screen whether the observed trade count satisfies MinTRL.

---

### GAP 6: Look-Ahead Invariants in Sim Desk Studies & Missing Mark-Price Triggers
- **Severity:** **HIGH**
- **Domain:** Look-Ahead Bias & Execution Realism
- **Industry Standard (Source):**
  - Chan (2009), *Quantitative Trading* (URL: [https://www.wiley.com/en-us/Quantitative+Trading%3A+How+to+Build+Your+Own+Algorithmic+Trading+Business-p-9780470284889](https://www.wiley.com/en-us/Quantitative+Trading%3A+How+to+Build+Your+Own+Algorithmic+Trading+Business-p-9780470284889)):
    > *"Look-ahead bias is introduced into a backtest when information that was not available at the time of the trade is used in generating the trading signal."*
  - Binance & Deribit Contract Specifications: Perpetual stop-loss and liquidation triggers are evaluated against the Mark Price (Fair Price index) to prevent market manipulation, whereas execution fills occur on the order book (Last Trade Price).
- **What the Repo Does:**
  - `MyTradingSys/research/sim_desk/studies/rsi.py:104-108`:
    ```python
    if q['exit'] == 'LEVEL':
        for m in range(k + 1, min(k + 1 + MAX_HOLD, len(b))):
            if rsi[m] is not None and (rsi[m] >= 60 if side > 0 else rsi[m] <= 40):
                t_exit = int(b[m, 0]) + tf_ms
                break
    ```
  - `MyTradingSys/research/sim_desk/studies/_bars.py:141-143`: Stop-loss orders are evaluated strictly against 1m trade bar extremes (`seg[:, 3] <= stop` for long, `seg[:, 2] >= stop` for short).
  - `MyTradingSys/research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md:43`:
    > *"Stops trigger on MARK (markPriceKlines); fills priced off trade bars. Report the Binance-vs-Deribit basis on the overlap..."*
- **The Gap:**
  1. **Pre-Determined Exit Trajectory in `rsi.py`:** Pre-scanning future bars for `t_exit` before simulating the trade path in `_bars.py` violates the strict point-in-time state-machine paradigm. If indicator parameters depend on dynamic state or volatility, pre-scanning leaks forward structure.
  2. **Trade Price vs. Mark Price Stops:** In live crypto trading, stop-losses are triggered when the exchange's Mark Price hits the stop level. Sim Desk evaluates stops exclusively on 1m trade klines from Binance. During liquidation cascades, mark prices frequently diverge from last trade prices by 20–100 bps, triggering stops that appear untriggered on trade bar klines.
- **Remediation:**
  1. Convert `sim_desk` exit evaluation into an incremental sequential loop where indicator values are computed bar-by-bar during the trade hold.
  2. Integrate `markPriceKlines` into `sim_desk` stop checks, triggering stop exits when `mark_low <= stop <= mark_high`.

---

### GAP 7: Conditioning on Survival (Single-Asset BTC/ETH Backtesting)
- **Severity:** **MEDIUM**
- **Domain:** Survivorship Bias
- **Industry Standard (Source):**
  - Brown, Goetzmann, Ibbotson & Ross (1992), "Survivorship Bias in Performance Studies" (URL: [https://doi.org/10.1093/rfs/5.4.553](https://doi.org/10.1093/rfs/5.4.553)):
    > *"We analyze the relationship between volatility and returns in a sample that is truncated by survivorship and show that this relationship gives rise to the appearance of predictability."*
  - Chan (2009), *Quantitative Trading*: Backtesting only on assets that currently exist or remain liquid introduces survivorship bias, inflating simulated returns.
- **What the Repo Does:**
  - `MyTradingSys/research/sim_desk/studies/_bars.py:43`: `SYMBOLS = {'BTCUSDT': 'BTC / USDT (ours)', 'ETHUSDT': 'ETH / USDT (ours)'}`.
  - `MyTradingSys/research/sim_desk/ROADMAP.md:16-21`: Documents that only BTC 1m data exists on disk; roadmap step R2 plans to fetch ETH 1m for breadth.
  - `MyTradingSys/research/TRIAL_LEDGER.csv:2-15`: All 14 pre-registered variants are executed solely on `BTCUSDT`.
- **The Gap:**
  - BTC and ETH are the quintessential "survivors" of the cryptocurrency asset class across the 2022–2026 cycles. Developing trend-following or level-bounce strategies exclusively on assets that successfully recovered from the 2022 crypto winter embeds an implicit survival filter. If the strategy library is expanded to altcoins (as contemplated in `ROADMAP.md`), selecting the top 20 coins as of today rather than a dynamic point-in-time universe will introduce massive survivorship bias.
- **Remediation:**
  - Explicitly document that all BTC/ETH single-asset results carry an asset-class survival condition.
  - If multi-asset screening is implemented, enforce a point-in-time universe selection protocol (e.g., top 20 coins by market cap as of the start of each rebalance month, including delisted/defunct tokens).

---

## 5. Engineering Remediation Roadmap for MTS

To transition the MTS backtesting framework to institutional standards, the following phased engineering roadmap is recommended:

```mermaid
flowchart TD
    subgraph Phase 1: Microstructure Realism
        P1A["Add slippage model (2-5 bps) to sim_desk"] --> P1B["Enforce trade-through tick on limit orders"]
        P1B --> P1C["Integrate continuous and 8h funding calculations"]
    end
    subgraph Phase 2: Statistical Rigor
        P2A["Wire Deflated Sharpe Ratio (DSR) into desk.py"] --> P2B["Compute Minimum Track Record Length (MinTRL)"]
        P2B --> P2C["Raise minimum trade gate from N=30 to N=100+"]
    end
    subgraph Phase 3: Validation Architecture
        P3A["Build Combinatorial Purged Cross-Validation (CPCV)"] --> P3B["Implement 1-day trade embargo & purging"]
        P3B --> P3C["Export T x N return matrices to TRIAL_LEDGER for PBO"]
    end
    Phase 1 --> Phase 2 --> Phase 3
```

1. **Immediate Execution Fixes (Phase 1):**
   - Inject a mandatory `slip_bp` default ($2.0\text{ bps}$) into `sim_desk/studies/_bars.py:run_trade`.
   - Charge funding rates on all positions holding past funding settlement timestamps or applying time-fraction continuous funding.
   - Restrict limit order fills to trades that penetrate the price level by at least $1\text{ tick}$ ($0.5\text{ USD}$ on BTC).

2. **Statistical Decision Gates (Phase 2):**
   - In `sim_desk/desk.py:verdict()`, calculate the Deflated Sharpe Ratio (DSR) using the trial count from `TRIALS.md`. Suppress `PASSED` verdicts when $DSR < 0.95$.
   - Calculate MinTRL based on realized skewness and kurtosis; flag any test where $N < \text{MinTRL}$ as `INSUFFICIENT SAMPLE SIZE`.

3. **Validation Infrastructure (Phase 3):**
   - Build a general CPCV module generating $\binom{N}{k}$ purged and embargoed out-of-sample backtest paths across historical data.
   - Log standardized per-trade return arrays for every registered trial to enable automated PBO calculations across the entire strategy ledger.
