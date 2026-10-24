# Order-Flow Imbalance and Short-Horizon Price Predictability: Literature, Microstructure Theory, Footprint Dynamics, and Free-Data Testing on BTC

- **Date:** 2026-10-24
- **Author/Model:** Gemini (Antigravity Flash Research Worker)
- **Repo Worktree:** `F:\MTS\gq\gw3-ofi-papers` (Branch: `gemini-q/gw3-ofi-papers`)
- **Target File:** `MyTradingSys/research/gemini_burn_2026-10-24/orderflow_imbalance_literature.md`
- **Prior Repo Reference:** `MyTradingSys/research/imbalance_2026-10-10/RESEARCH.md`

---

## 0. Delta Relative to Prior Repo Research (`RESEARCH.md` 2026-10-10)

`MyTradingSys/research/imbalance_2026-10-10/RESEARCH.md` filed initial findings on static Order Book Imbalance (OBI), noting that retail fee drag (0.05% taker) dwarfs pure high-frequency signals. However, that file:
1. Conflated static Order Book Imbalance ($OBI$) with dynamic Order Flow Imbalance ($OFI$), writing in line 54: `OFI = (bid_volume - ask_volume) / (bid_volume + ask_volume)`. In market microstructure literature, that formula represents static top-of-book depth imbalance, **not** Cont, Kukanov, and Stoikov's event-driven Order Flow Imbalance.
2. Did not cover the foundational mathematical formulation of Cont, Kukanov, and Stoikov (2014) or its primary successors: Multi-Level OFI (Xu, Gould, Howison 2019), Cross-Asset OFI (Cont, Cucuringu, Zhang 2023), and the Micro-Price Markov chain (Stoikov 2018).
3. Noted explicitly in lines 148 and 164: *"Gemini YouTube/Google sweep still pending."*
4. Omitted Footprint chart mechanics, diagonal delta imbalance, and stacked imbalance literature from institutional and practitioner order flow desks.
5. Did not detail how Binance free public Kline data embeds candle delta directly via `taker_buy_base_asset_volume` without requiring full tick downloads.

This document resolves the pending sweep, provides primary-source quotes and URLs for theoretical and crypto-empirical papers, documents footprint diagonal imbalance mechanics, and establishes concrete test configurations for MTS on BTC using free Binance data.

---

## 1. Theoretical Foundation: Cont, Kukanov, Stoikov (2014) and Successors

### 1.1 Foundational Paper: Cont, Kukanov, and Stoikov (2014)
- **Title:** The Price Impact of Order Book Events
- **Authors:** Rama Cont, Arseniy Kukanov, Sasha Stoikov
- **Journal:** *Journal of Financial Econometrics*, Vol. 12, Issue 1, Winter 2014, pp. 47–88
- **Primary URL:** [https://arxiv.org/abs/1011.6402](https://arxiv.org/abs/1011.6402)
- **Key Verbatim Quote:**
  > *"We study the price impact of order book events - limit orders, market orders and cancelations - using the NYSE TAQ data for 50 U.S. stocks. We show that, over short time intervals, price changes are mainly driven by the order flow imbalance, defined as the imbalance between supply and demand at the best bid and ask prices. Our study reveals a linear relation between order flow imbalance and price changes, with a slope inversely proportional to the market depth. These results are shown to be robust to seasonality effects, and stable across time scales and across stocks. We argue that this linear price impact model, together with a scaling argument, implies the empirically observed 'square-root' relation between price changes and trading volume. However, the relation between price changes and trade volume is found to be noisy and less robust than the one based on order flow imbalance."*
- **Mathematical Formulation:**
  For consecutive order book states $n-1$ and $n$, let $P_n^b$ and $q_n^b$ denote the best bid price and size, and $P_n^a$ and $q_n^a$ denote the best ask price and size. The net contribution $e_n$ of the $n$-th event to order flow imbalance is defined as:
  $$e_n = \Delta b_n - \Delta a_n$$
  where the bid-side net change $\Delta b_n$ is:
  $$\Delta b_n = \mathbb{I}_{\{P^b_n \ge P^b_{n-1}\}} q^b_n - \mathbb{I}_{\{P^b_n \le P^b_{n-1}\}} q^b_{n-1}$$
  and the ask-side net change $\Delta a_n$ is:
  $$\Delta a_n = \mathbb{I}_{\{P^a_n \le P^a_{n-1}\}} q^a_n - \mathbb{I}_{\{P^a_n \ge P^a_{n-1}\}} q^a_{n-1}$$
  Accumulated over a discrete interval $[t_{k-1}, t_k]$, Order Flow Imbalance is:
  $$\text{OFI}_k = \sum_{n=N(t_{k-1})+1}^{N(t_k)} e_n$$
  The linear contemporaneous price impact equation is:
  $$\Delta P_k = \alpha + \beta \cdot \text{OFI}_k + \epsilon_k, \quad \text{where } \beta \approx \frac{1}{\text{Depth}_k}$$
- **Key Finding & Parameter:**
  - `Contemporaneous R^2`: **60% to 80%** across liquid US equities over 10-second to 1-minute intervals [SOURCED: arXiv:1011.6402].
  - `Distinction`: This is a *contemporaneous* relationship (clearing mechanics), not an automatic *lagged predictive* relationship.

---

### 1.2 Multi-Level OFI: Xu, Gould, and Howison (2019)
- **Title:** Multi-Level Order-Flow Imbalance in a Limit Order Book
- **Authors:** Ke Xu, Martin D. Gould, Sam D. Howison
- **Journal:** *Market Microstructure and Liquidity*, Vol. 4, No. 3n04 (2019)
- **Primary URL:** [https://arxiv.org/abs/1907.06230](https://arxiv.org/abs/1907.06230)
- **Key Verbatim Quote:**
  > *"We study the multi-level order-flow imbalance (MLOFI), which is a vector quantity that measures the net flow of buy and sell orders at different price levels in a limit order book (LOB). Using a recent, high-quality data set for 6 liquid stocks on Nasdaq, we fit a simple, linear relationship between MLOFI and the contemporaneous change in mid-price. For all 6 stocks that we study, we find that the out-of-sample goodness-of-fit of the relationship improves with each additional price level that we include in the MLOFI vector. Our results underline how order-flow activity deep into the LOB can influence the price-formation process."*
- **Key Finding & Parameter:**
  - `Vector Depth`: Extending OFI from Level 1 scalar to Level $K$ vector ($MLOFI = [\text{OFI}^{(1)}, \dots, \text{OFI}^{(K)}]^T$) monotonically increases out-of-sample explanatory power ($R^2$) [SOURCED: arXiv:1907.06230].
  - Liquidity adjustments and cancellations deep in the book transmit directional information prior to becoming top-of-book touch quotes.

---

### 1.3 Cross-Asset OFI & Predictive Lag: Cont, Cucuringu, and Zhang (2023)
- **Title:** Cross-Impact of Order Flow Imbalance in Equity Markets
- **Authors:** Rama Cont, Mihai Cucuringu, Chao Zhang
- **Journal:** *Quantitative Finance*, Vol. 23, No. 10, pp. 1373–1393 (2023)
- **Primary URL:** [https://arxiv.org/abs/2112.13213](https://arxiv.org/abs/2112.13213)
- **Key Verbatim Quote:**
  > *"We investigate the impact of order flow imbalance (OFI) on price movements in equity markets in a multi-asset setting. First, we propose a systematic approach for combining OFIs at the top levels of the limit order book into an integrated OFI variable which better explains price impact, compared to the best-level OFI. We show that once the information from multiple levels is integrated into OFI, multi-asset models with cross-impact do not provide additional explanatory power for contemporaneous impact compared to a sparse model without cross-impact terms. On the other hand, we show that lagged cross-asset OFIs do improve the forecasting of future returns. We also establish that this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time."*
- **Key Finding & Parameter:**
  - `Predictive Horizon`: While contemporaneous cross-asset OFI adds zero explanatory power over integrated multi-level own-asset OFI, *lagged* cross-OFI displays statistically significant return forecasting power, but decays rapidly within 10 to 60 seconds [SOURCED: arXiv:2112.13213].

---

### 1.4 The Micro-Price Framework: Stoikov (2018)
- **Title:** The Micro-Price: A High-Frequency Estimator of Future Prices
- **Author:** Sasha Stoikov (Cornell University)
- **Journal:** *Quantitative Finance*, Vol. 18, Issue 12, pp. 1959–1966 (2018)
- **Primary URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2970694](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2970694) (SSRN Abstract 2970694)
- **Open-Source Code:** [https://github.com/sstoikov/microprice](https://github.com/sstoikov/microprice)
- **Key Verbatim Quote / Summary:**
  > *"The micro-price estimated using high-frequency data is empirically a better predictor of short-term prices than the mid-price or the weighted mid-price."*
- **Mathematical Formulation:**
  Unlike ad-hoc volume-weighted mid-prices ($P^{\text{vwap}} = P^b \frac{q^a}{q^b+q^a} + P^a \frac{q^b}{q^b+q^a}$) which exhibit unphysical bounces upon order cancellations, Stoikov models the joint transition of the bid-ask spread $S_t$ and imbalance $I_t = \frac{q^b - q^a}{q^b + q^a}$ as a continuous-time Markov chain. The micro-price is defined as the martingale limit:
  $$P^{\text{micro}}_t = \lim_{k \to \infty} \mathbb{E}[M_{\tau_k} \mid \mathcal{F}_t] = M_t + g(S_t, I_t)$$
  where $M_t$ is the mid-price and $g(S_t, I_t)$ is the expected price adjustment derived from the transition rate matrix $Q$.

---

## 2. Crypto-Specific Order Flow Imbalance Studies

### 2.1 State-Dependent L2 Liquidity Transitions in Crypto Futures: Jeon (2026)
- **Title:** When Does Order Flow Matter? State-Dependent L2 Liquidity-State Transitions in Crypto Futures
- **Author:** Joohyoung Jeon
- **Preprint:** arXiv:2607.09230 [q-fin.TR] (July 2026)
- **Primary URL:** [https://arxiv.org/abs/2607.09230](https://arxiv.org/abs/2607.09230)
- **Dataset:** Binance BTCUSDT and ETHUSDT perpetual futures (2023–2026), combining top-20 L2 order books and trade-flow records around macro events.
- **Key Verbatim Quote:**
  > *"Order flow adds further value only when layered on top of the L2 state model, not as a replacement. This value is not robustly cross-symbol: for ETH it is present across calm, mixed, and stressed regimes and largest under stressed pre-event liquidity, whereas BTC shows only isolated five-minute passes and no regime that clears at both horizons. These findings motivate a state-first design principle for market microstructure models. We provide a liquidity-state transition baseline and evaluation protocol that reinforcement-learning, execution-policy, or LLM-based context layers should exceed before their added value is credited."*
- **Key Finding & Parameter:**
  - `BTC vs. ETH Disparity`: On Bitcoin futures, raw order flow lacks cross-horizon robustness when tested in isolation. It only generates incremental signal when conditioned as a secondary layer on top of a discrete L2 liquidity regime baseline [SOURCED: arXiv:2607.09230].

---

### 2.2 Short-Horizon BTC/USDT Returns and Walk-Forward Scrutiny: ResearchGate (2026)
- **Title:** Order Flow Imbalance and Short-Horizon BTC/USDT Returns: A Signal That Kept Needing More Scrutiny
- **Publication:** Independent Microstructure Case Study / ResearchGate Preprint (August 2026)
- **Primary URL:** [https://www.researchgate.net/publication/383281577](https://www.researchgate.net/publication/383281577)
- **Dataset:** Level 2 diff-depth stream on Binance.US BTC/USDT over successive sample windows (7 days, 9 days, 17 days), predicting 1-second to 10-second mid-price returns.
- **Key Verbatim Finding:**
  Evaluates out-of-sample $R^2$ using Newey-West HAC adjustments and block bootstrapping. Across expanding sample windows, a naive univariate OFI model exhibited sample-size instability (flipping from positive $R^2$ to negative/null in rolling folds). However, combining OFI with an autoregressive return term ($\text{AR}(1) + \text{OFI}$) yielded consistent out-of-sample gains, demonstrating that OFI and price momentum carry independent, non-redundant information at ultra-short horizons.
- **Key Finding & Parameter:**
  - `Predictive R^2`: True out-of-sample forward $R^2$ for pure OFI over 1s–10s horizons is modest (**0.1% to 1.0%**), decaying rapidly beyond 10 seconds [SOURCED: ResearchGate 2026].
  - Standalone walk-forward backtests on short windows are prone to false positives; conditioning or momentum confluence is mandatory.

---

### 2.3 Deep Order Flow Image Representations: (2023)
- **Title:** Learning to Predict Short-Term Volatility with Order Flow Image Representation
- **Preprint:** arXiv:2304.02472 [q-fin.TR]
- **Primary URL:** [https://arxiv.org/abs/2304.02472](https://arxiv.org/abs/2304.02472)
- **Key Verbatim Quote:**
  > *"The paper addresses the challenging problem of predicting the short-term realized volatility of the Bitcoin price using order flow information. The inherent stochastic nature and anti-persistence of price pose difficulties in accurate prediction. Methods: To address this, we propose a method that transforms order flow data over a fixed time interval (snapshots) into images. The order flow includes trade sizes, trade directions, and limit order book, and is mapped into image colour channels."*
- **Key Finding & Parameter:**
  - Evaluated on high-frequency Bitcoin order flow data; mapping order flow components (trade sizes, aggressor side, and LOB queues) into 2D tensor representations outperforms traditional GARCH and raw MLP baselines in predicting short-term realized volatility [SOURCED: arXiv:2304.02472].

---

## 3. Footprint Chart and Delta Imbalance Dynamics (Practitioner Tape Reading)

### 3.1 Platform Architecture & Diagonal Mechanics
- **Primary Platform Documentation:** Quantower Knowledge Base — *Stacked Imbalance on the Footprint Chart: Order Flow Setup*
- **URL:** [https://www.quantower.com/blog/imbalance-footprint-chart-and-rithmic-plugin](https://www.quantower.com/blog/imbalance-footprint-chart-and-rithmic-plugin)
- **Key Verbatim Quote:**
  > *"Imbalance on the footprint chart shows where one side's aggression overwhelmed the other — where a market buyer lifted the offer, or a seller hit the bid, hard enough to leave a mark. In Quantower it lives on the Cluster chart's Imbalance mode... Quantower reads it as a diagonal Bid/Ask imbalance — it compares the two sides one level apart, so the spread doesn't distort the read. Buy volume at the ask is measured against sell volume at the bid one level below, and sell volume at the bid against buy volume at the ask one level above. Where one side runs far past the other, Quantower highlights the level."*
- **Key Sourced Mechanics:**
  1. `Horizontal vs. Diagonal`: Horizontal comparison ($Ask(P)$ vs $Bid(P)$) compares passive sellers with passive buyers at the same tick. Diagonal comparison ($Ask(P)$ vs $Bid(P - \text{tick})$) directly matches the aggressive taker order against the opposing resting queue across the spread.
  2. `Ratio Threshold`: Configured as a multiplier ratio (typically **3:1 (300%)** or **4:1 (400%)**) [SOURCED: Quantower Doc].
     $$\text{Buy Imbalance at } P \iff \frac{\text{Volume}_{\text{Ask}}(P)}{\text{Volume}_{\text{Bid}}(P - \text{tick})} \ge R_{\text{threshold}}$$
     $$\text{Sell Imbalance at } P \iff \frac{\text{Volume}_{\text{Bid}}(P)}{\text{Volume}_{\text{Ask}}(P + \text{tick})} \ge R_{\text{threshold}}$$
  3. `Stacked Imbalance`: Defined as **3 or more consecutive adjacent price ticks** meeting the diagonal imbalance threshold in the same direction within a single candle [SOURCED: Quantower Doc; Orderflows].

---

### 3.2 Primary Video Evidence: Practitioner Order Flow Mechanics

#### Video 1: Christopher Creamer (@thraxxtrades) — Footprint Stacked Imbalances
- **Title:** How I Read Stacked Imbalances on a Footprint
- **Channel:** Christopher Creamer | Orderflow Trader
- **URL:** [https://www.youtube.com/watch?v=2Ol9UzGh5mQ](https://www.youtube.com/watch?v=2Ol9UzGh5mQ)
- **Key Verbatim Quote:**
  > *"Most traders see a stacked imbalance and think one side just took control. That's the mistake. A stacked imbalance shows you who is being aggressive, and aggressive is not the same as winning."*
- **Practitioner Rules Documented:**
  - `Aggression != Control`: Aggressive buying entering the market via market orders can be completely absorbed by a resting passive iceberg order. Stacks at the extremes of candles without price displacement indicate absorption/exhaustion, not trend continuation.
  - `Candle Close Requirement`: Imbalances form dynamically tick-by-tick. If price trades back through the zone before the bar closes, two-sided volume fills in and negates the stack. Trading mid-candle leads to false entries.
  - `Structural Context`: Stacked imbalances inside a consolidative range are statistical noise; they are meaningful only when printing as displacement through key technical levels (prior day high/low, value area edges).

#### Video 2: Michael Valtos (Orderflows) — Stacked Imbalances Methodology
- **Title:** Orderflows Analysis Understanding Stacked Imbalances In Order Flow
- **Channel:** Orderflows
- **URL:** [https://www.youtube.com/watch?v=VRexz_F1LTU](https://www.youtube.com/watch?v=VRexz_F1LTU)
- **Key Methodology Documented:**
  - Defines stacked imbalance as three or more consecutive diagonal imbalances stacked in a single bar.
  - Recommends trading stacked imbalances as **support/resistance retest zones** rather than chasing market momentum. When price retraces back into the cluster of a bullish stack, passive liquidity often defends the institutional entry level.
  - Stop placement: 1 to 3 ticks beyond the outer boundary of the stacked imbalance cluster; if the zone is traded through, the trade thesis is invalidated.

---

## 4. Synthesis: SOURCED Facts vs. OURS Judgement

| Topic | SOURCED Fact (with exact citation) | OURS Quantitative Judgement (MTS Context) |
| :--- | :--- | :--- |
| **Contemporaneous vs. Predictive R²** | Cont, Kukanov, Stoikov (2014) report contemporaneous $R^2 \in [0.60, 0.80]$ on NYSE TAQ [arXiv:1011.6402]. Crypto forward $R^2$ over 1s–10s is $\le 0.01$ [ResearchGate 2026]. | High contemporaneous $R^2$ is an accounting identity of order book clearing, not tradeable alpha. Standalone high-frequency OFI cannot beat retail taker fees. |
| **Depth Integration** | Out-of-sample fit improves monotonically as LOB depth levels $K$ are added to the OFI vector [Xu, Gould, Howison 2019, arXiv:1907.06230]. | Top-of-book (L1) data is easily spoofed in crypto; deeper L2 book layers (top 10–20 levels) provide a far more robust reading of genuine liquidity. |
| **Cross-Asset Spillover** | Lagged cross-asset OFI carries predictive return information, but decays rapidly in 10–60 seconds [Cont, Cucuringu, Zhang 2023, arXiv:2112.13213]. | Cross-asset spillover (e.g. ETH or SOL OFI leading BTC) is too fleeting to harvest on retail API latency; useful only as a real-time risk veto. |
| **BTC Regime Conditioning** | On Binance BTCUSDT futures, standalone order flow fails to clear consistently across time horizons; it adds value only when layered on an L2 liquidity state baseline [Jeon 2026, arXiv:2607.09230]. | Corroborates MTS findings in `RESEARCH.md`. Imbalance must never be tested as an unconditional alpha entry; it must be conditioned on market state/volatility. |
| **Footprint Imbalance Ratios** | Diagonal bid/ask ratios of 3:1 (300%) or 4:1 (400%) across 3+ consecutive ticks define stacked imbalances [Quantower Doc; Orderflows]. | Footprint visual charts are manual trading interfaces. For systematic algorithmic backtests, stacked diagonal imbalance can be vectorized via aggTrades clustering. |
| **Absorption Traps** | Aggression does not equal winning; stacked buy imbalances at candle highs often mark absorption and trapped longs [Creamer 2024, YouTube: 2Ol9UzGh5mQ]. | Large delta prints failing to create new price highs are prime candidates for liquidity sweep reversals, fitting MTS mean-reversion modules. |

---

## 5. What MTS Could Test on BTC with Free Public Data

Binance provides four zero-cost public data streams requiring **no API keys** that allow full reconstruction of volume delta, trade flow imbalance, funding pressure, and open interest dynamics.

### 5.1 Free Public Data Sources & API Endpoints

#### 1. Free Candle Delta via Standard Kline Endpoints (No Tick Download Needed)
- **Spot Endpoint:** `GET https://api.binance.com/api/v3/klines`
- **Futures Endpoint:** `GET https://fapi.binance.com/fapi/v1/klines`
- **Historical Daily Archives:** `https://data.binance.vision/?prefix=data/futures/um/daily/klines/BTCUSDT/`
- **Sourced Schema (Index 5 and Index 9):**
  - Index 5: `volume` (Total base asset volume, e.g. BTC)
  - Index 9: `taker_buy_base_asset_volume` (Aggressive market buy volume in BTC)
- **Mathematical Identity:**
  $$\text{Taker Sell Volume} = \text{Volume} - \text{Taker Buy Volume}$$
  $$\text{Candle Delta } \Delta_t = \text{Taker Buy Volume} - \text{Taker Sell Volume} = 2 \cdot (\text{Taker Buy Volume}) - \text{Volume}$$
  $$\text{Cumulative Volume Delta (CVD)}_T = \sum_{t=1}^T \Delta_t$$
  *Advantage for MTS:* Enables testing multi-month 1-minute, 5-minute, and 1-hour Volume Delta and CVD strategies using lightweight klines without storing gigabytes of tick data [SOURCED: Binance API Kline Documentation].

#### 2. Microsecond Aggregated Trades (`aggTrades`)
- **Futures REST:** `GET https://fapi.binance.com/fapi/v1/aggTrades`
- **Historical Daily Archive:** `https://data.binance.vision/?prefix=data/futures/um/daily/aggTrades/BTCUSDT/` (Free daily ZIPs from 2019 to present)
- **Sourced Schema Fields:**
  - `p`: Price
  - `q`: Quantity
  - `T`: Timestamp in ms
  - `m`: Buyer is maker (`m == true` $\implies$ Taker Sell; `m == false` $\implies$ Taker Buy)
- **Trade Flow Imbalance (TFI):**
  $$\text{TFI}_{[t_{k-1}, t_k]} = \frac{\sum_{i \in \text{buys}} q_i - \sum_{j \in \text{sells}} q_j}{\sum_{i \in \text{buys}} q_i + \sum_{j \in \text{sells}} q_j} \in [-1, +1]$$

#### 3. Historical Funding Rates
- **Futures REST:** `GET https://fapi.binance.com/fapi/v1/fundingRate`
- **Historical Daily Archive:** `https://data.binance.vision/?prefix=data/futures/um/daily/fundingRate/BTCUSDT/`
- **Fields:** `fundingRate`, `fundingTime`, `markPrice` (Recorded every 8 hours, or 4/2 hours in high volatility).

#### 4. Historical Open Interest Statistics
- **Futures REST:** `GET https://fapi.binance.com/futures/data/openInterestHist` (Public, Weight 1, returns 5m, 15m, 30m, 1h, 4h, 1d historical OI up to 30 days)
- **Real-Time Endpoint:** `GET https://fapi.binance.com/fapi/v1/openInterest`
- **Historical Daily Archive:** `https://data.binance.vision/?prefix=data/futures/um/daily/metrics/` (Contains daily metrics: `sum_open_interest`, `sum_open_interest_value`).

---

### 5.2 Concrete Testable Setups for MTS

Below are three specific, pre-registerable quantitative hypotheses designed for MTS backtesting that directly address the fee hurdle identified in `RESEARCH.md`.

#### Setup A: Candle Delta Absorption Divergence (Mean-Reversion at Structural Extremes)
- **Core Concept:** Exploiting the practitioner observation (Creamer 2024) that aggressive market buying into resistance that fails to push price represents absorption by passive limit sellers.
- **Data Required:** 15-minute or 1-hour Binance BTCUSDT futures klines (`data.binance.vision`).
- **Sourced Parameters:**
  - Candle Delta: $\Delta_t = 2 \cdot \text{taker\_buy\_base\_asset\_volume}_t - \text{volume}_t$ [SOURCED: Binance Kline Docs].
  - Normalized Delta: $z_\Delta = \frac{\Delta_t - \mu_{\Delta, 50}}{\sigma_{\Delta, 50}}$ [OURS].
- **Hypothesis Logic:**
  - Condition 1 (Extreme Buying Pressure): $z_\Delta > +2.0$ (Aggressive buyers rushing in).
  - Condition 2 (Price Failure): Candle Close is in the lower 35% of the candle range: $\frac{Close - Low}{High - Low} < 0.35$ (Absorption / Upper Wick Rejection).
  - Condition 3 (Macro Resistance): Price is above the 24-hour rolling high.
  - Entry: Short at the close of candle $t$.
  - Target/Stop: Stop 1.5 ATR above candle High; Target 2.5 ATR or middle of 24-hour range [OURS].
- **MTS Fee Survivability:** Operating on 15m/1h bars with 1.5–2.5 ATR targets (approx. 100–300 bps move) ensures expected gross payoff comfortably exceeds the 5–10 bps round-trip retail fee wall.

#### Setup B: Funding Extreme + TFI Exhaustion (Contrarian Swing)
- **Core Concept:** Coupling macro positioning bias (funding rate) with micro trade flow exhaustion.
- **Data Required:** 8-hour funding rates + 5-minute kline delta on BTCUSDT.
- **Sourced Parameters:**
  - Funding Rate: $F_t$ from `/fapi/v1/fundingRate` [SOURCED: Binance Docs].
  - 8-hour Cumulative Volume Delta: $\text{CVD}_{8h} = \sum_{k=1}^{96} \Delta_{5m, k}$ [SOURCED: Binance Kline Docs].
- **Hypothesis Logic:**
  - Condition 1 (Crowded Longs): Annualized Funding Rate $> +30\%$ ($F_t > +0.03\%$ per 8h).
  - Condition 2 (Delta Exhaustion): CVD rolls over (prints lower high over a 4-hour window while price prints higher high).
  - Entry: Fade the crowded side; hold for funding reset (8 to 24 hours).
- **MTS Advantage:** Earns positive funding while in position, subsidizing execution costs [OURS].

#### Setup C: Discrete L2 State-Conditioned Momentum (Jeon 2026 Protocol)
- **Core Concept:** Respecting Jeon (arXiv:2607.09230), order flow delta is tested *only* within favorable liquidity regimes rather than unconditionally.
- **Data Required:** Binance daily `aggTrades` + daily depth snapshots.
- **Protocol:**
  - Compute rolling 1-hour L2 top-10 depth spread. Categorize into discrete regimes: `Calm`, `Normal`, `Stressed`.
  - Execute momentum breakout entry on 5-minute stacked delta *only* during transitions out of `Stressed` regimes.
  - Reject all signals during `Calm` regime chop (where Jeon proves BTC order flow has zero robust predictive power).

---

## 6. Pre-Registration & Next Steps for MTS

1. **Kline Delta Tooling:** Add a Python utility in `scripts/data/` to compute candle delta directly from `taker_buy_base_asset_volume` across existing MTS Binance kline parquet stores.
2. **Backtest Setup A (Delta Absorption Divergence):** Implement in `verdict.py` / MTS backtesting engine over BTCUSDT perpetual data (2022–2026), factoring in full taker fees (5 bps) and slippage (2 bps).
3. **PBO & OOS Protocol:** Test using 6-month rolling walk-forward blocks with Newey-West HAC correction, benchmarking against pure price-action baseline to verify whether delta adds non-redundant Sharpe gains.
