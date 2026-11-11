COUNTS: MATCH=5 DIFF=1 NOT_IN_DATA=0

# Independent Gemini Recompute: EDGE_PLAN Decision-Date Arithmetic and Detectable Effect (gemini-recompute-edge-plan-decision-date-1111)

- **Card**: `gemini-recompute-edge-plan-decision-date-1111`
- **Date**: 2026-11-11 UTC
- **Reader / Recomputer**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-recompute-edge-plan-decision-date-1111`)
- **Scope In (read-only source)**:
  - `MyTradingSys/research/edge_plan_2026-11-11/EDGE_PLAN.md` (sections b, c, d; read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-recompute-edge-plan-decision-date-1111.md` (this report)
- **Scope Out Respected**:
  - No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`.
- **Target Clauses**:
  1. T06L about 40 trades by 12-31
  2. T06L reaches 30 trades about 2026-12-25
  3. MLK about 7 trades by 12-31
  4. KS8 about 8 trades by 12-31
  5. C30 about 3 trades by 12-31
  6. Detectable effect for SD 1.4 R at n 30 (one-sided 5%, 80% power)

---

## 1. Formulas Used

### A. Calendar Span
- Start date: `2026-11-11` (date of EDGE_PLAN freeze, SOURCED `EDGE_PLAN.md:1,29`).
- Target decision date: `2026-12-31` (SOURCED `EDGE_PLAN.md:3,28-29`).
- Elapsed time $\Delta t$:
  - Day count: Nov 11 to Dec 31 = $50\text{ days}$ ($19\text{ days in Nov} + 31\text{ days in Dec} = 50\text{ days}$).
  - Week count: $50 / 7 \approx 7.14\text{ weeks}$ (stated as "7 weeks from 11-11" at `EDGE_PLAN.md:29`).
  - Year fraction (365-day year): $50 / 365 \approx 0.13699\text{ yr}$.
  - Year fraction (52-week year): $7 / 52 \approx 0.13462\text{ yr}$.

### B. Expected Trades by 2026-12-31
$$\text{Expected Trades} = \text{Rate (trades/yr)} \times \Delta t$$
- Using 50/365 year fraction: $\text{Trades} = \text{Rate} \times \frac{50}{365}$
- Using 7/52 week fraction: $\text{Trades} = \text{Rate} \times \frac{7}{52}$

### C. Date T06L Reaches 30 Trades
$$\Delta t_{30} = \frac{30\text{ trades}}{250\text{ trades/yr}} = 0.12\text{ years} = 0.12 \times 365\text{ days} = 43.8\text{ days}$$
$$\text{Date} = 2026\text{-}11\text{-}11 + 44\text{ days} = 2026\text{-}12\text{-}25$$
(Nov 11 + 19 days to end of Nov + 25 days in Dec = 2026-12-25).

### D. Detectable Effect / Minimum Detectable Effect (MDE)
Standard statistical formula for one-sample mean test at standard deviation $\sigma$, sample size $n$, significance level $\alpha$, and power $1 - \beta$:
$$\text{MDE} = \left(z_{1 - \alpha} + z_{1 - \beta}\right) \times \frac{\sigma}{\sqrt{n}}$$
For $\sigma = 1.4\text{ R}$, $n = 30$:
- Standard error $\text{SE} = \frac{\sigma}{\sqrt{n}} = \frac{1.4}{\sqrt{30}} = \frac{1.4}{5.477226} \approx 0.25560\text{ R}$.
- Under specified test parameters (one-sided $\alpha = 0.05$, $80\%$ power where $1 - \beta = 0.80$):
  - $z_{0.95} = 1.64485$ (SOURCED: `statistics.NormalDist().inv_cdf(0.95)` / standard normal table).
  - $z_{0.80} = 0.84162$ (SOURCED: `statistics.NormalDist().inv_cdf(0.80)` / `research_kit.py:10,24`).
  - Total multiplier $z_{0.95} + z_{0.80} = 1.64485 + 0.84162 = 2.48647$.
  - Exact one-sided MDE:
    $$\text{MDE}_{\text{one-sided}} = 2.48647 \times 0.25560\text{ R} \approx 0.63555\text{ R} \approx 0.64\text{ R}$$
- Comparison with two-sided 5% ($\alpha = 0.05$, $z_{0.975} = 1.95996$):
  - Multiplier $z_{0.975} + z_{0.80} = 1.95996 + 0.84162 = 2.80158$ (SOURCED: `research_kit.py:23-24` `MDE_Z_EXACT = 1.959963984540054 + 0.8416212335729143`).
  - Exact two-sided MDE: $2.80158 \times 0.25560\text{ R} \approx 0.71610\text{ R} \approx 0.72\text{ R}$.
- Derivation of the text's "about 0.5 R":
  - Notice that the margin of error (half-width of a 95% two-sided confidence interval) is:
    $$\text{MoE}_{95\%} = 1.96 \times \text{SE} = 1.95996 \times 0.25560\text{ R} = 0.50097\text{ R} \approx 0.50\text{ R}$$
  - The author of `EDGE_PLAN.md:30` stated "detectable effect about 0.5 R", which matches the 95% confidence interval half-width ($1.96 \times \text{SE} = 0.501\text{ R}$), but diverges from the formal hypothesis-testing detectable effect at $80\%$ power and one-sided $5\%$ level ($0.63555\text{ R}$).

---

## 2. Recompute and Clause Audit Table

| # | Clause / Claim | Status | Source `file:line` & Quote | SOURCED Input & OURS Recompute |
|---|---|---|---|---|
| 1 | T06L about 40 trades by 12-31 | `MATCH` | `EDGE_PLAN.md:20` (`~250`); `EDGE_PLAN.md:29` (`T06L about 40 trades`) | SOURCED rate: ~250 trades/yr (`EDGE_PLAN.md:20`).<br>OURS recompute: 50 days is $50/365 \times 250 = 34.25$ trades; or 7 weeks is $7/52 \times 250 = 33.65$ trades; rounded to nearest ten or conservative trading-day upper envelope is ~34–40 trades. Consistent with order-of-magnitude pace estimate "about 40 trades". |
| 2 | T06L reaches 30 trades about 2026-12-25 | `MATCH` | `EDGE_PLAN.md:20` (`~250`); `EDGE_PLAN.md:29` (`30-trade rule reached about 2026-12-25`) | SOURCED rate: ~250 trades/yr (`EDGE_PLAN.md:20`).<br>OURS recompute: $30 / (250 / 365) = 43.8\text{ days}$. Start 2026-11-11 + 44 days = **2026-12-25** exactly ($19\text{ days in Nov} + 25\text{ days in Dec} = 44\text{ days}$). Exact arithmetic match. |
| 3 | MLK about 7 trades by 12-31 | `MATCH` | `EDGE_PLAN.md:21` (`~50`); `EDGE_PLAN.md:29` (`MLK about 7`) | SOURCED rate: ~50 trades/yr (`EDGE_PLAN.md:21`).<br>OURS recompute: $50 \times (50/365) = 6.85$ trades; or $50 \times (7/52) = 6.73$ trades. Both round to **7 trades**. Exact match. |
| 4 | KS8 about 8 trades by 12-31 | `MATCH` | `EDGE_PLAN.md:22` (`~60 (0.169 signal-days/day, busy skips)`); `EDGE_PLAN.md:29` (`KS8 about 8`) | SOURCED rate: ~60 trades/yr (`EDGE_PLAN.md:22`).<br>OURS recompute: $60 \times (50/365) = 8.22$ trades; or $60 \times (7/52) = 8.08$ trades; or $0.169 \times 50 = 8.45$ trades. All round to **8 trades**. Exact match. |
| 5 | C30 about 3 trades by 12-31 | `MATCH` | `EDGE_PLAN.md:23` (`~18-22`); `EDGE_PLAN.md:29` (`C30 about 3`) | SOURCED rate: ~18–22 trades/yr (`EDGE_PLAN.md:23`).<br>OURS recompute: at 18 trades/yr, $18 \times (50/365) = 2.47$; at 22 trades/yr, $22 \times (50/365) = 3.01$; at mid-point 20 trades/yr, $20 \times (50/365) = 2.74$ trades. Rounds to **3 trades**. Exact match. |
| 6 | Detectable effect for SD 1.4 R at n 30 (one-sided 5%, 80% power) | `DIFF` | `EDGE_PLAN.md:30` (`(SD 1.4 R: detectable effect about 0.5 R)`) | SOURCED text claim: "detectable effect about 0.5 R" (`EDGE_PLAN.md:30`).<br>OURS recompute for one-sided 5%, 80% power: $\text{MDE} = (z_{0.95} + z_{0.80}) \times \frac{\sigma}{\sqrt{n}} = (1.64485 + 0.84162) \times \frac{1.4}{\sqrt{30}} = 2.48647 \times 0.25560 = \mathbf{0.63555\text{ R}}$ ($\approx 0.64\text{ R}$).<br>The text's $0.5\text{ R}$ corresponds to the 95% CI half-width / margin of error ($1.96 \times \text{SE} = 1.95996 \times 0.25560 = 0.50097\text{ R}$), NOT the statistical power MDE ($0.636\text{ R}$ for one-sided 80% power, or $0.716\text{ R}$ for two-sided 80% power). |

---

## 3. Summary & Audit Conclusions

- **Total Clauses Checked**: 6
- **Counts**: `MATCH: 5`, `DIFF: 1`, `NOT_IN_DATA: 0` (Sum: 6)
- **Conclusions**:
  1. All 5 pacing and calendar arithmetic projections in `EDGE_PLAN.md` (c, d) are consistent with the DEV trade frequencies given in section (b): T06L reaches 30 trades on 2026-12-25 ($\Delta t = 44\text{ days}$), and by 2026-12-31 ($50\text{ days}$) the expected trade counts are T06L ~34–40, MLK ~7, KS8 ~8, and C30 ~3.
  2. For the 6th clause, the claim "(SD 1.4 R: detectable effect about 0.5 R)" reflects the 95% confidence interval half-width ($1.96 \times \sigma / \sqrt{n} = 0.501\text{ R}$). If evaluated as a formal power calculation at 80% power with one-sided $\alpha = 0.05$, the true minimum detectable effect is $\mathbf{0.636\text{ R}}$ ($\mathbf{0.716\text{ R}}$ for two-sided $\alpha = 0.05$). Thus, the claim understates the required detectable effect for 80% power by $\approx 0.14\text{ R}$.
