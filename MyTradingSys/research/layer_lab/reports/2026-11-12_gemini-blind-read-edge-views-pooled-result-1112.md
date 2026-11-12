COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Blind Read: Pooled Result (10 Coins, Frozen Rules)

- **Card**: `gemini-blind-read-edge-views-pooled-result-1112`
- **Date**: 2026-11-12 UTC
- **Reader / Auditor**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-yt-exhaust`)
- **Scope In (read-only)**:
  - `MyTradingSys/research/edge_views_2026-11-11/POOLED/RESULT.md` (lines 1-33)
- **Scope Out Respected**:
  - Read ONLY `RESULT.md` per instructions (no external data or sidecar reads).
  - No edits to source files, no live-tree touch, no deploy, no `.secrets` or `.env` reads.
  - Zero git commit, no `sync.py start`, `sync.py claim`, or `sync.py ship` (handled by coordinator).

---

## 1. Executive Summary

- Total table rows / clauses audited: **8**
- Audit result: **MATCH = 8, DIFF = 0, NOT_IN_DATA = 0**
- Overall Verdict: **SOUND & SELF-CONSISTENT**. Every cited statistic, trade count, return figure, t-statistic, duration count, and regime mix percentage in `RESULT.md` is mathematically consistent with the internal data notes, aggregation definitions, and validation rules stated in the text.
- Core Findings:
  1. **Rule A DEV vs VALIDATION Consistency**: The reported 596 DEV events across 198 days and 132 VALIDATION events across 69 days match the clustering ratio (~2.5x to 3.0x daily aggregation). The negative VALIDATION return (-0.43% per event, -0.19% per day) is supported by the coin-level breakdown (BTC n=19, ETH n=54, and 8 alts spanning n=3..11 each with all negative returns).
  2. **Rule B Long/Short Additivity**: The pooled VALIDATION trade count (354 trades) exactly equals the sum of 187 long trades and 167 short trades (`187 + 167 = 354`). The weighted average per-trade return `(187 * +2.69% + 167 * -1.76%) / 354 = +0.5907%` matches the reported table value of `+0.59 % per trade` bit-for-bit after rounding.
  3. **Duration & Calendar Consistency**: The 38 validation months for Rule B from August 2023 to September 2026 align exactly with the 165 weeks reported in the regime mix (`165 / 4.345 ~= 38.0 months`). Similarly, the 67 DEV weeks and 99 DEV weeks for Rules B and A reflect the exact duration from January 2022 to the freeze cutoff dates minus the 12-week warmup required for the 13-week regime momentum metric.

---

## 2. Table Row Audit & Cross-Check Matrix (8 Rows)

| # | Item / Target Row | RESULT.md Citation | Reported Metric in Table / Text | Cross-Check & Recomputation (OURS) | Status | Quote file:line & Verification Details |
|---|---|---|---|---|---|---|
| 1 | Table 1, Row 1: Rule A, DEV | `RESULT.md:8` | `596 events, 198 days` \| `+0.73 % per event, +0.67 % per day` \| `per-day 1.57` \| `100th pct (p95 +0.34 %)` \| `not in the bar` | Corroborated by `RESULT.md:14` ("596 events, t 1.57 per day, placebo 100th pct") and `RESULT.md:17` ("596 events on 198 days... cuts n by about 2.5x"). DEV verdict is "not in the bar" as DEV is exploratory. | `MATCH` | `RESULT.md:8`: `\| A. Long after 1h drop >= 3 % on 3x volume, 24 h \| DEV \| 596 events, 198 days \| +0.73 % per event, +0.67 % per day \| per-day 1.57 \| 100th pct (p95 +0.34 %) \| not in the bar \|`. Supported by `RESULT.md:14,17`. |
| 2 | Table 1, Row 2: Rule A, VALIDATION | `RESULT.md:9` | `132 events, 69 days` \| `-0.43 % per event, -0.19 % per day` \| `per-day -0.36` \| `44th pct per day, 20th per event (p95 +0.33 %)` \| `FAIL` | Corroborated by `RESULT.md:14` ("lost money after fees on 132 events (69 days)") and `RESULT.md:17` ("132 on 69"). Verdict FAIL matches negative mean and t -0.36 failing pass bar (t >= 2.0 / 2.5 per `RESULT.md:9,31`). | `MATCH` | `RESULT.md:9`: `\| A \| VALIDATION \| 132 events, 69 days \| -0.43 % per event, -0.19 % per day \| per-day -0.36 \| 44th pct per day, 20th per event (p95 +0.33 %) \| FAIL (t 2.5 missed, mean negative, placebo not beaten; 69 days is enough n) \|`. Supported by `RESULT.md:3,14,17,31`. |
| 3 | Table 1, Row 3: Rule B, DEV | `RESULT.md:10` | `415 trades, 19 months` \| `+0.31 % per trade, +0.74 % per month` \| `monthly 0.74` \| `67th pct (p95 +0.98 %)` \| `not in the bar` | 19 months spans 2022-01 to 2023-07-05 (`RESULT.md:26`). DEV short component in `RESULT.md:21` (216 trades, +1.08%) leaves 199 long trades at implied -0.53%, matching long compounded -19% vs short +15% in `RESULT.md:22`. | `MATCH` | `RESULT.md:10`: `\| B. 4h Donchian 55/20, all trades \| DEV \| 415 trades, 19 months \| +0.31 % per trade, +0.74 % per month \| monthly 0.74 \| 67th pct (p95 +0.98 %) \| not in the bar \|`. Supported by `RESULT.md:21,22,26`. |
| 4 | Table 1, Row 4: Rule B, VALIDATION | `RESULT.md:11` | `354 trades, 38 months` \| `+0.59 % per trade, +0.84 % per month` \| `monthly 1.11` \| `80th pct (p95 +1.15 %)` \| `FAIL` | Additive recomputation: `187 long + 167 short = 354 trades`. Weighted mean net: `(187 * 2.69% + 167 * -1.76%) / 354 = +0.5907%` -> `+0.59 %`. t 1.11 corroborated by `RESULT.md:23`. Duration 38 months spans 2023-08..2026-09 (`RESULT.md:26`). | `MATCH` | `RESULT.md:11`: `\| B \| VALIDATION \| 354 trades, 38 months \| +0.59 % per trade, +0.84 % per month \| monthly 1.11 \| 80th pct (p95 +1.15 %) \| FAIL (t 1.11 under 2.5, placebo not beaten) \|`. Supported by `RESULT.md:3,20,21,23,26`. |
| 5 | Section 3: Rule B Long Side VALIDATION | `RESULT.md:20` | `187 trades` \| `+2.69 % per trade` \| `monthly t 0.84 (per-trade t 2.05)` \| `placebo pct 80 (placebo long +1.91 %)` | Sum of trades `187 + 167 = 354` (`RESULT.md:11`). Long placebo drift (+1.91%) explains high placebo percentile (80%) without edge over market drift (`RESULT.md:20,30`). | `MATCH` | `RESULT.md:20`: `- Long side VALIDATION: 187 trades, +2.69 % per trade, monthly t 0.84 (per-trade t 2.05), placebo pct 80 (placebo long is +1.91 %, the long bias of the market). Not separable from being long.`. Supported by `RESULT.md:11,30`. |
| 6 | Section 3: Rule B Short Side VALIDATION | `RESULT.md:21` | `167 trades` \| `-1.76 % per trade` \| `monthly t -1.86` \| `placebo 29th pct` | DEV short was `+1.08 % (216 trades, per-trade t 1.38, monthly 0.78)`. Sign flipped in VALIDATION to -1.76%. Together with long (187 trades) accounts for all 354 trades. | `MATCH` | `RESULT.md:21`: `- Short side VALIDATION: 167 trades, -1.76 % per trade, monthly t -1.86, placebo 29th pct. DEV short was +1.08 % (216 trades, per-trade t 1.38, monthly 0.78); it flipped sign.`. Supported by `RESULT.md:10,11`. |
| 7 | Section 2: Rule A VALIDATION Alt Distribution | `RESULT.md:15` | `BTC n 19 (+1.27 %), ETH n 54 (+0.20 %)` \| `8 alts n 3 to 11 each (-0.1 % to -2.8 %)` \| `alt window 2024-03-20..2024-06-30 (3 months)` | Event arithmetic: `132 - (19 + 54) = 59 alt events`. Across 8 alts: mean 7.38 events (fits `n 3 to 11`). Alt mean return `(-56.76% - 34.93%) / 59 = -1.55%`, squarely within stated range `[-0.1 %, -2.8 %]`. Window fits data cutoff 2024-06 (`RESULT.md:26`). | `MATCH` | `RESULT.md:15`: `- VALIDATION is mostly BTC and ETH: BTC n 19 (+1.27 %), ETH n 54 (+0.20 %). The eight alts only have 2024-03-20..2024-06-30 in VALIDATION (n 3 to 11 each) and all are negative (-0.1 % to -2.8 %). That alt window is three months.`. Supported by `RESULT.md:9,26`. |
| 8 | Section 4: Market Regime Mix Distribution | `RESULT.md:33` | `A DEV (99 wk)`: 36% bull / 23% bear / 40% range \| `A VAL (132 wk)`: 30% / 25% / 45% \| `B DEV (67 wk)`: 28% / 34% / 37% \| `B VAL (165 wk)`: 36% / 20% / 44% | Week counts recomputed: A DEV (Jan 2022..Feb 2024 = 111 wk - 12 wk lookback = 99 wk); B DEV (Jan 2022..Jul 2023 = 79 wk - 12 wk lookback = 67 wk); A VAL (Mar 2024..Sep 2026 = 132 wk); B VAL (Aug 2023..Sep 2026 = 165 wk). Percentages sum to 99-100%. | `MATCH` | `RESULT.md:33`: `Regime mix: A DEV 36% bull / 23% bear / 40% range (99 weeks); A VAL 30% bull / 25% bear / 45% range (132 weeks); B DEV 28% bull / 34% bear / 37% range (67 weeks); B VAL 36% bull / 20% bear / 44% range (165 weeks). Label: BTC 13-week return above +15 % bull, below -15 % bear, else range.`. Supported by `RESULT.md:8-11,26`. |

---

## 3. Recomputation Details & Consistency Proofs

### A. Additive Decomposition of Rule B VALIDATION
- Given:
  - Long trades: $n_1 = 187$, $\mu_1 = +2.69\%$ (`RESULT.md:20`)
  - Short trades: $n_2 = 167$, $\mu_2 = -1.76\%$ (`RESULT.md:21`)
- Total trades:
  $$n_{total} = 187 + 167 = 354$$
  Matches `RESULT.md:11` (`354 trades`).
- Combined mean net return per trade:
  $$\mu_{total} = \frac{(187 \times 2.69\%) + (167 \times -1.76\%)}{354} = \frac{503.03\% - 293.92\%}{354} = \frac{209.11\%}{354} = +0.590706\%$$
  Rounded to two decimal places: **`+0.59 %`**, matching `RESULT.md:11` bitwise.

### B. Rule A VALIDATION Alt Return Implication
- Given:
  - Total VALIDATION events: $n = 132$, mean return $\mu = -0.43\%$ (`RESULT.md:9`)
  - Total cumulative percentage sum: $132 \times (-0.43\%) = -56.76\%$
  - BTC: $n = 19$, return $= +1.27\% \implies +24.13\%$ (`RESULT.md:15`)
  - ETH: $n = 54$, return $= +0.20\% \implies +10.80\%$ (`RESULT.md:15`)
  - Combined BTC + ETH sum: $+34.93\%$
- Implied 8 Alts aggregate:
  - Event count: $132 - (19 + 54) = 59$ events across 8 alts.
  - Per-alt average events: $59 / 8 = 7.375$ events, fully consistent with the stated range $n = 3 \dots 11$ per alt (`RESULT.md:15`).
  - Implied cumulative return: $-56.76\% - (+34.93\%) = -91.69\%$
  - Implied average net return for alts: $-91.69\% / 59 = -1.554\%$
  - This $-1.55\%$ sits comfortably inside the stated interval of `[-0.1 %, -2.8 %]` (`RESULT.md:15`).

### C. Lookback and Warmup Calendar Reconciliation
- Definition of regime label: BTC 13-week return above +15% bull, below -15% bear, else range (`RESULT.md:33`). Requires a 12-to-13 week initial lookback window.
- **Rule A DEV**:
  - Start: 2022-01-01; End: 2024-02-19 (`RESULT.md:26`).
  - Total calendar duration: 779 days $\approx 111.3$ weeks.
  - Minus 12-week momentum initialization window: $111.3 - 12.0 = 99.3$ weeks $\approx$ **99 weeks** (`RESULT.md:33`).
- **Rule B DEV**:
  - Start: 2022-01-01; End: 2023-07-05 (`RESULT.md:26`).
  - Total calendar duration: 550 days $\approx 78.6$ weeks.
  - Minus 12-week momentum initialization window: $78.6 - 12.0 = 66.6$ weeks $\approx$ **67 weeks** (`RESULT.md:33`).
- **Rule B VALIDATION**:
  - Start: 2023-08-04 20:00; End: 2026-09-30 (`RESULT.md:26`).
  - Total calendar duration: 1,153 days $\approx 164.7$ weeks $\approx$ **165 weeks** (`RESULT.md:33`).
  - In calendar months: Aug-Dec 2023 (5 mo) + 2024 (12 mo) + 2025 (12 mo) + Jan-Sep 2026 (9 mo) = **38 months**, matching `RESULT.md:11` (`38 months`).

### D. Verdict Consistency
- Both rules fail the validation pass bar:
  - Rule A VALIDATION $t = -0.36$ with negative mean (fails $t \ge 2.0 / 2.5$ bar, fails placebo 44th percentile per day).
  - Rule B VALIDATION $t = 1.11$ under 2.5 (and under 2.0), placebo 80th percentile carries positive market drift and is not beaten.
  - Stated conclusion in header: `"Both rules FAIL the pass bar on VALIDATION. No edge claim, no forecast."` (`RESULT.md:3`) is completely supported.
