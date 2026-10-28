# Lab Report: Re-check of GPT T05 LC1 Control Audit (2026-10-28)

**Task**: `gem-lc1-csv-recheck`  
**Card Title**: `[GEMINI] Recheck GPT's LC1 control: 12 families DROP, own-distance pool share 50.78%`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/independent_results.csv`
- `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/report.md`
- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py` (lines 90–135)

*Constraint adherence*: In strict adherence to the task brief, `MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/recheck.py` was NOT read, inspected, or imported. Audit was conducted exclusively by source code inspection of `t05_lc1.py` and numerical re-derivation of `independent_results.csv`.

---

## 1. Executive Summary

1. **Published KEEP Survivals Recomputed (100% Confirmed)**:
   - Analysis of [`independent_results.csv`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/independent_results.csv) confirms that for all 8 level families originally published as KEEP in study T05 (`4h_fractal_high`, `4h_fractal_low`, `naked_poc`, `prior_day_high`, `prior_day_low`, `prior_day_poc`, `prior_week_high`, `round_1000`), **0 of 8 families satisfy $ci\_lo > 0$**.
   - In fact, across all 12 level families evaluated, **every single family results in a DROP verdict** (all $ci\_lo \le -0.0098$). The three families with positive mean hold rate differences (`daily_open` +0.34 pp, `naked_poc` +2.10 pp, `prior_day_poc` +1.38 pp, `prior_day_val` +1.62 pp) have 95% bootstrap confidence intervals spanning zero.

2. **Control Pool Contamination Confirmed (`t05_lc1.py:97-126`)**:
   - Source inspection of [`t05_lc1.py:97-102`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L97-L102) reveals that `pool[(fam, month_of(day))]` aggregates distance offsets $|price - mid|$ across ALL candidates in the calendar month without excluding the candidate level itself.
   - At sampling time ([`t05_lc1.py:124-126`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L124-L126)), offsets are drawn with replacement from that uncleaned pool.
   - For `daily_open`, exactly **50.78%** (`0.5078467153284671`) of the control distance draws replicate the candidate's own distance, allowing the placebo level to equal the candidate level itself when the random sign matches.

---

## 2. Independent Recount and Verification Details

### A. Level Family Hold Rate Differences & Confidence Intervals

| Family | Published Verdict | Real Touches | Real HOLD Rate | Control Touches | Control HOLD Rate | Diff (pp) | 95% Bootstrap CI (pp) | Verified Verdict | Same Distance Share |
|---|---|---|---|---|---|---|---|---|---|
| `4h_fractal_high` | **KEEP** | 1,984 | 46.27% | 42,126 | 49.75% | -3.48 pp | [-5.96, -0.99] | **DROP** | 0.37% |
| `4h_fractal_low` | **KEEP** | 1,963 | 44.88% | 41,878 | 50.27% | -5.39 pp | [-7.69, -3.07] | **DROP** | 0.42% |
| `daily_open` | DROP | 822 | 49.27% | 16,435 | 48.93% | +0.34 pp | [-2.46, +3.32] | **DROP** | **50.78%** |
| `naked_poc` | **KEEP** | 732 | 53.14% | 14,896 | 51.04% | +2.10 pp | [-1.20, +5.50] | **DROP** | 1.28% |
| `prior_day_high` | **KEEP** | 380 | 37.63% | 7,937 | 49.45% | -11.82 pp | [-16.41, -7.02] | **DROP** | 3.32% |
| `prior_day_low` | **KEEP** | 345 | 40.87% | 7,611 | 48.61% | -7.74 pp | [-13.13, -2.55] | **DROP** | 3.14% |
| `prior_day_poc` | **KEEP** | 583 | 52.66% | 11,070 | 51.27% | +1.38 pp | [-2.42, +5.47] | **DROP** | 3.31% |
| `prior_day_vah` | DROP | 537 | 48.23% | 10,508 | 51.21% | -2.98 pp | [-7.30, +1.33] | **DROP** | 3.50% |
| `prior_day_val` | DROP | 539 | 52.32% | 10,400 | 50.70% | +1.62 pp | [-2.51, +5.80] | **DROP** | 3.35% |
| `prior_week_high` | **KEEP** | 150 | 44.67% | 2,775 | 49.84% | -5.17 pp | [-13.11, +2.23] | **DROP** | 3.52% |
| `prior_week_low` | DROP | 124 | 43.55% | 2,809 | 50.84% | -7.29 pp | [-16.08, +1.36] | **DROP** | 3.10% |
| `round_1000` | **KEEP** | 831 | 45.01% | 16,454 | 49.45% | -4.45 pp | [-7.97, -1.05] | **DROP** | 1.34% |

**Summary**:
- Published KEEPs evaluated: 8 families.
- Published KEEPs with $ci\_lo > 0$: **0 of 8 (0.0%)**.
- All 12 families produce $ci\_lo \le 0$, confirming full DROP agreement with T05 fair-control findings.

### B. Code Inspection of Control Distance Pool (`t05_lc1.py`)

1. **Pool Construction Without Exclusion** ([`t05_lc1.py:97-102`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L97-L102)):
   ```python
   pool = defaultdict(list)
   for day, rows in by_day.items():
       mid = float(rows[0]["o"])
       for lv in levels.get(day, []):
           pool[(lv["family"], month_of(day))].append(abs(float(lv["price"]) - mid))
   ```
   The pool for a given calendar month pools all candidate levels across the entire month. It does not exclude the candidate's own level.

2. **Control Sampling With Replacement** ([`t05_lc1.py:124-126`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L124-L126)):
   ```python
   for _ in range(K_LINES):
       dist = ps[rng.randrange(len(ps))]
       p = mid + (-1 if rng.random() < .5 else 1) * dist
   ```
   For `daily_open`, candidate prices frequently equal or cluster near `mid = rows[0]["o"]` ($dist = 0.0$). As a result, $50.78\%$ of draws replicate the candidate's exact distance. With probability $0.5$ (or $1.0$ when $dist=0$), $p = mid \pm dist$ creates a control identical to the real candidate.

---

## 3. Findings Table

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| LOW | [`t05_lc1.py:97-102, 124-126`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L97-L102) | Control distance pool does not exclude the candidate level itself, causing `daily_open` to draw its own distance in 50.78% of samples. | `pool_draw_same_distance_share = 0.5078` in `independent_results.csv`; code pools all candidate levels in month without leave-one-out filter. | Construct leave-one-candidate-out distance pools so $ps$ explicitly excludes the current level's offset from the empirical distribution. |
| LOW | [`t05_lc1.py:97-102`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-lc1-csv-recheck/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py#L97-L102) | Monthly distance pool uses future candidates within the same month for early-month decisions. | `month_of(day)` groups entire calendar month before decision loop runs. | Use an expanding historical lookback window (e.g. prior 30 days) to enforce causal, point-in-time covariate matching. |

---

## 4. Verdict

**Verdict: SOUND.**  
GPT's audit report `gx4-t05-recheck/report.md` is accurate and technically sound:
1. Recomputed $real\_hold - control\_hold$ confirms that **0 of 8 published KEEP families have $ci\_lo > 0$**, resulting in **12 of 12 families classified as DROP**.
2. Code inspection of `t05_lc1.py:97-126` confirms the control pool fails to exclude candidate levels, yielding exactly **50.78% same-distance draws for `daily_open`**.
