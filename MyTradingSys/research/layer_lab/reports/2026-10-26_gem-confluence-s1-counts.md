# Lab Report: Re-check of Confluence S1 Context and Event Row Counts (2026-10-28)

**Task**: `gem-confluence-s1-counts`  
**Card Title**: `[GEMINI] Recount Confluence S1 rows: 7,115 context, 23,213 events, 22,862 usable`  
**Producer**: GPT `gpt-6-luna` over Claude data ([`MyTradingSys/research/gpt_burn_2026-10-24/gx2-confluence-s1/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-confluence-s1-counts/MyTradingSys/research/gpt_burn_2026-10-24/gx2-confluence-s1/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/research/krown_audit_2026-10-22/run/context_dev.csv`
- `MyTradingSys/research/krown_audit_2026-10-22/run/joined_events.csv`
- `MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_S1_COUNTS.md` (line 11)
- `MyTradingSys/research/krown_audit_2026-10-22/run/COUNTS.md` (lines 64–85)
- `MyTradingSys/research/gpt_burn_2026-10-24/gx2-confluence-s1/report.md`

*Constraint adherence*: In strict adherence to the card rules and `PRE_REG_S1_COUNTS.md:F3,4`, NO outcome columns (forward returns, gross move, etc.) were read or analyzed. Audit was conducted exclusively on timestamp, timeframe, set, indicator, usable status, and confluence dimension score columns on DEV data.

---

## 1. Executive Summary

1. **Row Counts Confirmed (100% Match)**:
   - **`context_dev.csv`**: Contains exactly **7,115 data rows** (excluding comments and headers):
     - **1,643 daily (`1d`) rows** (731 in `DEV_EXT` 2020-01-01..2021-12-31, 912 in `DEV` 2022-01-01..2024-06-30).
     - **5,472 four-hour (`4h`) rows** (exactly $21{,}888 / 4 = 5{,}472$, all in `DEV`).
   - **`joined_events.csv`**: Contains exactly **23,213 total event rows**:
     - **22,862 usable rows** (`usable == 1`, with all context dimensions D1, D2, D3 available at decision time).
     - **351 unusable rows** (`usable == 0`, dropped due to availability latency or missing context).
     - **18,247 unique pooled events** across `(decision_ts, side)`.

2. **Pre-Reg Expected vs Actual Confluence Shares (`PRE_REG_S1_COUNTS.md:11`)**:
   - `PRE_REG_S1_COUNTS.md:11` established prior approximations for cell shares: $S=+3 \approx 1.6\%$, $S \ge +2 \approx 12\%$, $S \le -2 \approx 13\%$.
   - Actual recount across the $N=18{,}247$ pooled unique usable events reveals extreme sparsity and asymmetry:
     - **$S = +3$**: Actual **12 events (0.07%)** vs expected ~1.6% (approx. **23x fewer** events than anticipated).
     - **$S \ge +2$**: Actual **351 events (1.9%)** vs expected ~12% (approx. **6.3x fewer** events than anticipated).
     - **$S \le -2$**: Actual **1,849 events (10.1%)** vs expected ~13% (approx. 1.3x fewer events than anticipated).

---

## 2. Independent Row and Cell Recount Details

### A. Context Table Breakdown (`context_dev.csv`)

| Timeframe | Data Set | Date Range | Row Count | Formula / Verification Check |
|---|---|---|---|---|
| `1d` | `DEV_EXT` | 2020-01-01 .. 2021-12-31 | 731 | 366 (leap 2020) + 365 (2021) = 731 days |
| `1d` | `DEV` | 2022-01-01 .. 2024-06-30 | 912 | 365 (2022) + 365 (2023) + 182 (2024 H1) = 912 days |
| **`1d` Total** | | | **1,643** | Sum of daily rows |
| `4h` | `DEV` | 2022-01-01 .. 2024-06-30 | **5,472** | $21{,}888\text{ 1h bars} / 4 = 5{,}472\text{ 4h bars}$ |
| **Total Context Rows** | | | **7,115** | $1{,}643 + 5{,}472 = 7{,}115$ (Header + comment lines excluded) |

### B. Joined Event Table Breakdown (`joined_events.csv`)

| Category | Count | Share of Total | Notes |
|---|---|---|---|
| Total event rows | 23,213 | 100.0% | Layer events across all 13 detectors |
| Usable event rows (`usable == 1`) | 22,862 | 98.49% | All D1, D2, D3 context available at `decision_ts` |
| Dropped unusable rows (`usable == 0`) | 351 | 1.51% | Insufficient lookback or `available_at >= decision_ts` |
| Unique pooled events `(decision_ts, side)` | 18,247 | — | Deduplicated pool for confluence evaluation |

### C. Confluence Score ($S$) Distribution & Comparison with Pre-Reg Spec

Distribution of $S = D_1 + D_2 + D_3 \in \{-3, -2, -1, 0, +1, +2, +3\}$ across the $N=18{,}247$ unique pooled usable events:

| Confluence Score ($S$) | Event Count | Share (%) | Pre-Reg Spec / COUNTS.md Cell | Expected Share (`PRE_REG:11`) | Actual Share | Ratio (Actual / Expected) |
|---|---|---|---|---|---|---|
| **$S = -3$** | 256 | 1.40% | | | | |
| **$S = -2$** | 1,593 | 8.73% | | | | |
| **$S \le -2$** | **1,849** | **10.13%** | Cell $S \le -2$ | ~13.0% | **10.1%** | 0.78x |
| **$S = -1$** | 5,600 | 30.69% | | | | |
| **$S = 0$** | 7,242 | 39.69% | | | | |
| **$S = +1$** | 3,205 | 17.56% | | | | |
| **$S = +2$** | 339 | 1.86% | | | | |
| **$S = +3$** | 12 | 0.07% | Cell $S = +3$ | ~1.6% | **0.07%** | **0.04x (23x deficit)** |
| **$S \ge +2$** | **351** | **1.92%** | Cell $S \ge +2$ | ~12.0% | **1.9%** | **0.16x (6.3x deficit)** |

*Note on F6 Direction Alignment*: Under the original 6-bar price direction implementation (`krown_context.py`), $S \ge +2$ was 353 (341 + 12). Under the F6 direction amendment adopted on trunk (`612fc633878c`), which resets direction since BBWP was last $\le 50$, $S=+2$ is 339 and $S \ge +2$ is 351 (1.92%).

---

## 3. Findings Table

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| MED | [`PRE_REG_S1_COUNTS.md:11`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-confluence-s1-counts/MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_S1_COUNTS.md#L11) | Severe statistical power collapse on positive confluence cells ($S=+3$ has only 12 events; $S \ge +2$ has 351 events, vs 12% expected). | Actual pooled share for $S=+3$ is 0.07% (expected 1.6%); $S \ge +2$ is 1.9% (expected 12%). | Acknowledge that the $S=+3$ cell is severely underpowered for independent regression/classification and must remain purely descriptive; widen positive score bands or pool $S \ge +1$ if statistical inference is required. |
| LOW | [`COUNTS.md:80,82`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-confluence-s1-counts/MyTradingSys/research/krown_audit_2026-10-22/run/COUNTS.md#L80-L82) | Direction definition nuance (F6 vs 6-bar) causes a minor 2-event shift in $S \ge +2$ (351 vs 353). | Re-derived count is 351 with F6 direction and 353 with 6-bar direction; both round to 1.9%. | Retain F6 direction definition as committed on trunk (`612fc633878c`) and update documentation references accordingly. |

---

## 4. Verdict

**Verdict: SOUND.**  
All row counts cited in the card and audited by GPT are independently verified to the exact integer:
1. `context_dev.csv`: exactly **7,115 rows** (1,643 daily + 5,472 4-hour).
2. `joined_events.csv`: exactly **23,213 total rows** with **22,862 usable rows** and **18,247 unique pooled events**.
3. Confluence cell shares: **$S=+3$ at 0.07% (12)**, **$S \ge +2$ at 1.9% (351)**, and **$S \le -2$ at 10.1% (1,849)** confirm the severe power drop against the pre-reg expected shares.
