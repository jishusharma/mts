# Blind Review: cross-sectional momentum / reversal, Bybit USDT perps, weekly (edge-xsec-momentum-1113)

Verdict: **SOUND** (The reported conclusion `Verdict: UNDERPOWERED, no pass.` is completely supported by the empirical evidence and tables presented in the text; what would change it is an expanded sample with adequate statistical power where the validation confidence interval lower bound excludes zero and survives multiple testing).

Reviewed input file: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md`

---

## 1. Overview and Core Verdict

The study tests weekly cross-sectional momentum and reversal strategies on Bybit USDT perpetuals across three chronological splits (DEV: 159 weeks, VALIDATION: 53 weeks, RECENT: 70 weeks; total 282 weeks).

The headline verdict states:
- "Verdict: UNDERPOWERED, no pass." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3`)

And:
> "0 of 7 cells pass; no cell has VALIDATION CI lower bound > 0 (all CIs span roughly +-2 to +-3 percent a week against means under 0.4 percent), none is BH-10% significant (smallest VALIDATION p 0.42). No factor earns a testnet-forward run on this evidence." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3`)

This verdict is **SOUND**. In the out-of-sample VALIDATION split, point estimates are small (+0.05% to +0.39% for positive cells, -0.71% and -0.09% for negative cells), whereas the 4-week block bootstrap 95% confidence intervals are massive (widths between 2.33% and 5.63% a week). Not a single cell achieves statistical significance (minimum p-value is 0.420 on MOM-7), and the best cell (+0.39%) falls far below the 95th percentile of the placebo distribution (+1.24%).

---

## 2. Table Analysis and Arithmetic Verification

### 2.1 Cell Inventory and Structure
The results table (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:13-35`) contains 21 rows across 7 factor cells evaluated on 3 sample splits:
- 3 Long-Short Momentum cells: `MOM-7`, `MOM-14`, `MOM-28`
- 1 Long-Short Reversal cell: `REV-7`
- 3 Long-Only minus Equal-Weight cells: `LO-7`, `LO-14`, `LO-28`

The splits comprise:
- `DEV`: 159 weeks (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:15`)
- `VALIDATION`: 53 weeks (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:16`)
- `RECENT`: 70 weeks (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:17`)

Sum of split lengths: `159 + 53 + 70 = 282` weeks (OURS; recomputed).
This matches the universe description:
> "282 weeks 2021-06-14 .. 2026-11-02, 67 distinct names; 18 early weeks have 10-19 names" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:9`).

Regime mix check:
- DEV: 35 bull + 30 bear + 94 range = 159 weeks (OURS; matches DEV n=159). SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`.
- VALIDATION: 14 bull + 5 bear + 34 range = 53 weeks (OURS; matches VALIDATION n=53). SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`.
- RECENT: 8 bull + 12 bear + 50 range = 70 weeks (OURS; matches RECENT n=70). SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`.

All sample counts are internally consistent: **YES**.

### 2.2 Net Return Arithmetic Verification
The relationship between weekly mean returns is defined as: `net mean = gross - fee + funding`.
Recomputing `gross - fee + funding` across all 21 rows (OURS):

| Cell | Split | Gross | Fee | Funding | Reported Net | Calculated Net | Difference | Consistent? |
|---|---|---|---|---|---|---|---|---|
| MOM-7 | DEV | -0.08% | 0.16% | +0.05% | -0.20% | -0.19% | -0.01% | YES (rounding) |
| MOM-7 | VALIDATION | 0.55% | 0.16% | -0.00% | +0.39% | +0.39% | 0.00% | YES |
| MOM-7 | RECENT | 1.57% | 0.15% | -0.02% | +1.40% | +1.40% | 0.00% | YES |
| MOM-14 | DEV | -0.08% | 0.12% | +0.07% | -0.13% | -0.13% | 0.00% | YES |
| MOM-14 | VALIDATION | 0.41% | 0.12% | +0.02% | +0.31% | +0.31% | 0.00% | YES |
| MOM-14 | RECENT | 0.86% | 0.12% | +0.00% | +0.75% | +0.74% | +0.01% | YES (rounding) |
| MOM-28 | DEV | 0.01% | 0.10% | +0.08% | -0.00% | -0.01% | +0.01% | YES (rounding) |
| MOM-28 | VALIDATION | 0.10% | 0.10% | +0.07% | +0.07% | +0.07% | 0.00% | YES |
| MOM-28 | RECENT | -1.40% | 0.10% | +0.62% | -0.87% | -0.88% | +0.01% | YES (rounding) |
| REV-7 | DEV | 0.08% | 0.16% | -0.05% | -0.12% | -0.13% | +0.01% | YES (rounding) |
| REV-7 | VALIDATION | -0.55% | 0.16% | +0.00% | -0.71% | -0.71% | 0.00% | YES |
| REV-7 | RECENT | -1.57% | 0.16% | +0.02% | -1.71% | -1.71% | 0.00% | YES |
| LO-7 | DEV | -0.52% | 0.09% | +0.03% | -0.58% | -0.58% | 0.00% | YES |
| LO-7 | VALIDATION | 0.18% | 0.08% | +0.04% | +0.14% | +0.14% | 0.00% | YES |
| LO-7 | RECENT | 0.86% | 0.08% | +0.23% | +1.01% | +1.01% | 0.00% | YES |
| LO-14 | DEV | -0.53% | 0.06% | +0.06% | -0.54% | -0.53% | -0.01% | YES (rounding) |
| LO-14 | VALIDATION | 0.08% | 0.06% | +0.03% | +0.05% | +0.05% | 0.00% | YES |
| LO-14 | RECENT | 0.20% | 0.06% | +0.25% | +0.39% | +0.39% | 0.00% | YES |
| LO-28 | DEV | -0.25% | 0.05% | +0.06% | -0.25% | -0.24% | -0.01% | YES (rounding) |
| LO-28 | VALIDATION | -0.11% | 0.05% | +0.07% | -0.09% | -0.09% | 0.00% | YES |
| LO-28 | RECENT | -1.04% | 0.05% | +0.54% | -0.54% | -0.55% | +0.01% | YES (rounding) |

Every row is exactly equal to the reported net return within 0.01% (attributable to 2 decimal place rounding of the components): **YES**.

### 2.3 Confidence Intervals and Statistical Precision
All 7 cells on VALIDATION have confidence intervals spanning zero:
- `MOM-7`: `[-2.13%, +3.43%]` (width = 5.56%, p = 0.420)
- `MOM-14`: `[-1.77%, +2.85%]` (width = 4.62%, p = 0.423)
- `MOM-28`: `[-2.11%, +2.63%]` (width = 4.74%, p = 0.494)
- `REV-7`: `[-3.77%, +1.86%]` (width = 5.63%, p = 0.674)
- `LO-7`: `[-1.31%, +1.96%]` (width = 3.27%, p = 0.474)
- `LO-14`: `[-1.28%, +1.58%]` (width = 2.86%, p = 0.497)
- `LO-28`: `[-1.19%, +1.14%]` (width = 2.33%, p = 0.568)

Recomputed CI widths span roughly 2.3% to 5.6% a week (half-widths ~1.1% to ~2.8%), compared to validation net means under 0.4% (+0.05% to +0.39%). This confirms the verbatim claim:
> "all CIs span roughly +-2 to +-3 percent a week against means under 0.4 percent" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3`).

None of the p-values in VALIDATION approach significance (smallest is 0.420 on MOM-7). Even without multiple testing correction, zero factors pass. Under Benjamini-Hochberg at 10% FDR, critical values for ranks 1..7 would require `p <= (rank / 7) * 0.10` (i.e. p <= 0.014 for rank 1), whereas the empirical minimum p is 0.420:
> "none is BH-10% significant (smallest VALIDATION p 0.42)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3`).

---

## 3. Methodological Risks Exposed in the Text

The report is commendably candid about its structural limitations. The text itself explicitly exposes five concrete categories of risk:

### 3.1 Look-Ahead and Execution Feasibility Risks
1. **Unrealistic Execution at Weekly Open**:
   The text discloses that fills are assumed at weekly bar opens rather than realistic traded fills:
   > "Limits: universe is a survivor list; weekly open prices from daily bars (not tradable fills); ~50-70 weeks per out-of-sample split." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:55`)
   Simulating 20 coin rebalances simultaneously at the exact weekly open price ignores execution lag and order book depth.

2. **Universe Selection Mechanism**:
   The universe is filtered using historical data:
   > "Universe: top 20 by trailing 30-day mean turnover among 79 candidates (launchTime <= 2021-12-31), chosen per Monday from data before that date" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:9`)
   While rolling turnover from data prior to Monday avoids direct look-ahead in volume ranking, requiring `launchTime <= 2021-12-31` imposes a backward filter over the full universe of candidates.

### 3.2 Fee and Slippage Handling Risks
1. **Zero Slippage Modeling**:
   The fee model accounts only for taker fees and funding:
   > "Costs: fees.BINANCE_TAKER (5 bp) per side on drifted-weight turnover; Bybit funding history, long pays positive rate, short receives. Columns are weekly means." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:11`)
   Slippage is completely omitted (0 bp). In altcoin perpetuals rebalancing weekly (turnover of top/bottom quantiles), market impact and bid-ask spread crossing would further reduce gross margins.
2. **Noise vs. Fee Magnitude**:
   The author notes:
   > "Fees are 0.05-0.16% a week of a 2-5% weekly standard deviation: the weekly horizon makes costs small and noise large, so the limit is statistical power (53 validation weeks), not cost." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:52`)
   Because fees are 5-16 bp per week while weekly return volatility is 200-500 bp, backtested fees do not alter the conclusion, but real execution costs would degrade any marginal edge.

### 3.3 Placebo Validity Risks
1. **Placebo Baseline Comparison**:
   The report evaluates a 200-draw random portfolio placebo:
   > "Placebo (random q-set per week, 200 draws, same fees and funding), weekly net mean, 5th / mean / 95th percentile:" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:37`)
   For long-short strategies in VALIDATION, the placebo 95th percentile is +1.24% a week (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:42`), whereas the best momentum factor achieves only +0.39%:
   > "VALIDATION: best net cell MOM-7 +0.39% a week, CI [-2.13%, +3.43%], p 0.42, below the long-short placebo 95th percentile (+1.24%). Not a result." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:49`)
   A factor that fails to beat a random quantile selection has zero empirical validity.

### 3.4 Clustering and Sample Independence Risks
1. **Cross-Sectional and Temporal Clustering**:
   Crypto assets exhibit massive cross-sectional correlation (high beta to BTC). Furthermore, overlapping lookback windows (MOM-14, MOM-28) create autocorrelated portfolio positions.
   The study attempts to mitigate temporal clustering via a 4-week block bootstrap (`95% CI (4-wk block)`, SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:13`), which appropriately widens the confidence intervals.
2. **Severe Regime Imbalance in Validation**:
   The text highlights:
   > "VALIDATION had only 5 bear weeks; RECENT has the most bear weeks." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`)
   With only 5 bear weeks out of 53 in VALIDATION (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`), the validation set cannot reliably assess regime invariance.

### 3.5 Survivorship and Multiple Testing Risks
1. **Survivorship Bias**:
   The text admits:
   > "Candidate list excludes delisted perps (Bybit does not serve them): residual survivorship, which flatters long legs." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:9`)
   Excluding tokens that were delisted over the 2021-2026 period introduces positive bias into long legs. Despite this upward bias, long-only and long-short strategies still failed.
2. **Sign Flips Across Regimes and Multiple Testing**:
   The report notes:
   > "RECENT (reported, never used to select): MOM-7 +1.40% (p 0.07) and LO-7 +1.01% (p 0.06) lean positive, MOM-28 and REV-7 negative; the 7-day momentum sign flips from DEV (-0.20%) to RECENT. A one-regime lean at 70 weeks, not BH-corrected, not a pass." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:50`)
   The sign flip between DEV (-0.20%) and RECENT (+1.40%) illustrates factor instability across regimes. Pre-registration (`PRE_REG.md`, committed `9f86723f1` before outcome, SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:5`) properly prevented ex-post selection of RECENT.

---

## 4. Conclusion and Verdict

The verdict of the report is **SOUND**.
The study author correctly evaluated the results:
- 0 of 7 cells passed pre-registered criteria.
- Out-of-sample statistical power is severely lacking with 53 weeks.
- The factors do not beat placebo random draws.
- The conclusion that "No factor earns a testnet-forward run on this evidence" is fully warranted.
