# Blind Review: edge3-rsi-deep-extreme-grid-1113

## Verdict: SOUND (internally consistent within documented scope, fail-closed on low power)

The author's verdict of **FAIL / UNDERPOWERED** is **SOUND**:
1. All 60 pre-registered pooled cells failed to pass the edge criteria (48 UNDERPOWERED due to validation $n < 30$, 12 FAIL where $n \ge 30$ but Benjamini-Hochberg FDR at 10% was not significant).
2. The author appropriately refuses to claim an edge despite positive validation means on select sub-cells (such as 4h T=20 or 4h T=15), recognizing that the study lacks statistical power ($n < 30$) or fails multiple-testing corrections across the 60 pre-registered cells.
3. What would change this verdict:
   - A larger sample size (accumulating out-of-sample data or expanding the universe beyond 10 coins while properly controlling for coin cross-correlation) that achieves $n \ge 30$ in validation for deep RSI thresholds ($T \le 15$).
   - A realistic execution model incorporating taker slippage and funding costs, especially given that deep capitulation episodes suffer from wide bid-ask spreads and severe illiquidity.
   - Accounting for cross-coin clustering, since the 10 coins frequently trigger simultaneous RSI dips during market-wide crashes, reducing effective degrees of freedom.

---

## 1. Table: Claims, Text Locations, and Internal Consistency Checks

| Claim / Subject | File Location | Stated Value | Recomputed / Verified Value | Consistent? | Notes / Calculations |
|---|---|---|---|---|---|
| Study Verdict | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:3` | `Verdict: FAIL / UNDERPOWERED. 0 of 60 pre-registered pooled cells PASS` | 48 + 12 = 60 total cells. Of 14 BH-significant cells, 0 have $n \ge 30$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:3`. Directly consistent with the rule requiring both $n \ge 30$ and significance to claim a PASS. |
| Table A: Sums across 10 coins for all 16 cells | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:12-24` | Stated row ALL: 43/33, 78/45, 218/138, 852/545, 9/7, 26/21, 74/51, 239/130, 4/3, 11/7, 33/23, 114/67, 0/0, 5/3, 25/20, 75/55 | Exactly recomputed by summing BTC..LTC for each (TF, T): all 16 column totals match stated values identically. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:14-24`. Recomputed arithmetic sum over all 10 assets. |
| BTC Episode Table: T <= 12 row counts | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:28-57` | Stated in Table A: 1h<=10: 5/4; 1h<=12: 8/5; 4h<=10: 3/2; 4h<=12: 6/4; 8h<=10: 1/0; 8h<=12: 2/1; 12h<=12: 2/1 | Table has exactly 27 rows. By cell: (1h,10): 5 rows (4 cf=yes); (1h,12): 8 rows (5 cf=yes); (4h,10): 3 rows (2 cf=yes); (4h,12): 6 rows (4 cf=yes); (8h,10): 1 row (0 cf=yes); (8h,12): 2 rows (1 cf=yes); (12h,12): 2 rows (1 cf=yes). Total = 27 rows. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:31-57`. Row-by-row count matches Table A BTC numbers exactly. |
| BTC Episode Table: 4h RSI <= 12 rows | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:47-52` | 6 episodes, 4 confirm-yes | Lines 47-52: 6 rows (2022-05-09: yes, 2022-11-09: yes, 2023-03-10: no, 2023-08-17: no, 2026-02-05: yes, 2026-06-03: yes). Count: 6 total, 4 confirm-yes. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:47-52`. Exactly 6 episodes and 4 confirm-yes. |
| BTC Episode Table: T = 15 row counts | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:59-108` | Stated in Table A: 1h<=15: 27/20; 4h<=15: 10/5; 8h<=15: 6/5; 12h<=15: 4/3 | Table has exactly 47 rows. (1h,15): 27 rows (20 cf=yes); (4h,15): 10 rows (5 cf=yes); (8h,15): 6 rows (5 cf=yes); (12h,15): 4 rows (3 cf=yes). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:62-108`. Row-by-row count matches Table A BTC numbers exactly. |
| BTC Stop Distance % Table counts (n) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:128-141` | BTC stop% counts for confirm-yes: 1h,10: 4; 1h,12: 5; 1h,15: 20; 4h,10: 2; 4h,12: 4; 4h,15: 5; 8h,12: 1; 8h,15: 5; 12h,12: 1; 12h,15: 3 | Confirm-yes events with valid stop% from the BTC episode tables match n for all T <= 15 cells. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:128-141`. Recomputed counts match Table A and Stop Distance table n. |
| Stop Distance % Percentiles & Ranges | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:128-141` | e.g., BTC 4h T=12: n=4, p25=2.51, med=2.80, p75=3.57, worst=5.46. 4h T=10: n=2, p25=3.09, med=3.88, p75=4.67, worst=5.46. | BTC 4h T=12 stop% values are {2.1, 2.7, 2.9, 5.5}. Worst is 5.46 (rounds to 5.5). Median of 2.7 and 2.9 is 2.80. Percentiles match standard quantile interpolation. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:132-133`. Recomputed from BTC episode stop% values. |
| Today trade Operator Example | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:8-9` | Entry 69034.8, Stop 67468.4, stop distance 2.27%. Peak 70187.0 = +0.74R. Last close 68666.3 = -0.24R. | Stop dist: (69034.8 - 67468.4) / 69034.8 = 2.269% (2.27%). Peak R: (70187.0 - 69034.8) / 1566.4 = +0.7356R (+0.74R). Last close R: (68666.3 - 69034.8) / 1566.4 = -0.2352R (-0.24R). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:8-9`. Recomputed arithmetic from stated price points. |
| Number of Pooled Cells with VALIDATION n >= 30 | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:144` | "Cells with VALIDATION n >= 30: 12 of 60." | The 12 cells comprise 2 combos of (TF, T) with 6 exits each: (1h, 20) with VAL n=92, and (4h, 20) with VAL n=32. All remaining 48 cells have VAL n < 30. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:144-168`. Verified against Table B listings. |
| Table C: Pooled confirm-yes counts on T=20 | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:248-300` | 1h T=20 confirm-yes total = 545. Weekend split: 96 + 443 = 539. Trend split: 152 + 336 = 488. | Category sub-counts sum to total events within missing data tolerances noted at line 302. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:248-302`. Arithmetic consistent with reported missing values. |

---

## 2. Detailed Recount: BTC Episodes and 4h RSI <= 12 Rows

### A. 4h RSI <= 12 Episodes
From `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:47-52`, there are 6 distinct episodes:
1. `2022-05-09 20`: rsi=11.4, dRSI=24.6, cf=yes, stop%=2.1%, +1R=target, +2R=target, +3R=target, brk_h=33.0, r24%=1.8%, r72%=-0.3%, r7d%=-1.0%, rsi@pk=30.4
2. `2022-11-09 20`: rsi=9.8, dRSI=24.4, cf=yes, stop%=5.5%, +1R=target, +2R=target, +3R=neither, brk_h=blank, r24%=4.2%, r72%=3.3%, r7d%=1.0%, rsi@pk=41.0
3. `2023-03-10 00`: rsi=11.0, dRSI=29.4, cf=no, stop%=0.9%
4. `2023-08-17 12`: rsi=11.3, dRSI=37.7, cf=no, stop%=0.1%
5. `2026-02-05 20`: rsi=11.8, dRSI=15.8, cf=yes, stop%=2.9%, +1R=target, +2R=target, +3R=target, brk_h=blank, r24%=10.5%, r72%=11.1%, r7d%=3.7%, rsi@pk=48.1
6. `2026-06-03 00`: rsi=10.9, dRSI=21.8, cf=yes, stop%=2.7%, +1R=stop, +2R=stop, +3R=stop, brk_h=12.0, r24%=-5.4%, r72%=-9.2%, r7d%=-8.2%, rsi@pk=25.3

**Recomputed metrics on these 4 confirm-yes trades:**
- **Win rate (+1R within 72h):** [OURS] 3 out of 4 reached +1R (75.0%).
- **Win rate (+2R within 72h):** [OURS] 3 out of 4 reached +2R (75.0%).
- **Win rate (+3R within 72h):** [OURS] 2 out of 4 reached +3R (50.0%), 1 was stopped, 1 reached neither.
- **Stop rate:** [OURS] 1 out of 4 was stopped before reaching +1R (25.0%).
- **Returns:**
  - 24h return: [1.8%, 4.2%, 10.5%, -5.4%] -> [OURS] Mean = +2.78%, Median = +3.00%.
  - 72h return: [-0.3%, 3.3%, 11.1%, -9.2%] -> [OURS] Mean = +1.22%, Median = +1.50%.
  - 7d return: [-1.0%, 1.0%, 3.7%, -8.2%] -> [OURS] Mean = -1.13%, Median = 0.00%.

### B. Internal Consistency vs Verdict
While 4h RSI <= 12 shows high nominal win rates (75% to +2R) on BTC, the sample size is only $n = 4$ confirm-yes trades across the entire history of BTC. Pooled across all 10 coins (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:24`), 4h RSI <= 12 yields only 26 episodes and 21 confirm-yes trades total across all years. Even pooled, $n = 21 < 30$, meaning it cannot be statistically evaluated without extreme overfitting and sampling noise. The text verdict of UNDERPOWERED directly and correctly reflects this sample constraint.

---

## 3. Concrete Methodological and Execution Risks Exposed by the Text

The study text itself candidly documents multiple significant risks:

1. **Look-Ahead and Incomplete Windows:**
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:5`:
     "Trades need 168 h of forward data, so the last 7 days are excluded from tested trades."
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:9`:
     "(Not in any statistics: its 168 h window is not complete.)"
   - Analysis: The author properly excludes incomplete trades from backtest statistics to avoid right-censorship / look-ahead truncation bias.

2. **Fee and Slippage Risks:**
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:5`:
     "fees 2 x BINANCE_TAKER (fees.py), no slippage, no funding"
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:323`:
     "No slippage or funding; R-multiples explode when the signal-bar range is tiny (fees / stop distance)"
   - Analysis: In deep RSI extreme crashes ($RSI \le 10$ or $12$), market order books are severely depleted, bid-ask spreads widen dramatically, and volatility is extreme. Taker fills will experience substantial adverse slippage not captured by the fee-only model. Furthermore, when stop distance is tight (e.g., 0.3% to 0.5%), a realistic slippage of 0.10%-0.20% consumes 20%-60% of the entire risk budget ($1R$).

3. **Placebo Validity and Statistical Power:**
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:3`:
     "0 of 60 pre-registered pooled cells PASS (verdicts: {'UNDERPOWERED': 48, 'FAIL': 12}). BH 10% significant on VALIDATION: 14 (of which 0 have VALIDATION n >= 30; the rest are UNDERPOWERED)."
   - Analysis: 48 out of 60 cells have fewer than 30 trades in the validation period. When $n$ is very small (e.g. $n = 3$ in line 163), bootstrap confidence intervals collapse and placebo p-values become uninterpretable or degenerate.

4. **Clustering and Asset Cross-Correlation:**
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:323`:
     "10 coins are highly correlated (week-block bootstrap partly handles that)"
   - Analysis: Deep market selloffs (e.g., May 2022, November 2022, August 2023) trigger RSI extreme conditions on all 10 crypto assets simultaneously. Treating these as 10 independent samples severely overstates effective sample size.

5. **Multiple Testing / Grid Mining:**
   - Text quote: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge3-rsi-deep-extreme-grid_RESULTS.md:323`:
     "T=20 is the superset of deeper first touches only approximately because first touch is defined per threshold"
   - Analysis: Running a grid of 4 timeframes (1h, 4h, 8h, 12h) x 4 thresholds (10, 12, 15, 20) x 6 exits produces 96 theoretical combinations (60 evaluated in pooled). Applying Benjamini-Hochberg FDR control at 10% is necessary, and under this correction, 0 sufficiently powered cells were significant.

---

## Conclusion
The study is rigorous and candid about its data limits. Its headline conclusion—that deep extreme RSI buy setups cannot be validated as a robust standalone edge across the pooled crypto universe due to low sample power and lack of FDR significance—is fully confirmed by internal arithmetic and table consistency.
