# Blind Read: `tom_v2_gross_first_2026-11`

- **Card**: `gemini-blind-read-tom-v2-gross-first-1107`
- **Reader**: Gemini (independent blind read worker), 2026-11-07
- **Target Study**: `MyTradingSys/research/tom_v2_gross_first_2026-11/RESULT.md`
- **Data Source in Folder**: `MyTradingSys/research/tom_v2_gross_first_2026-11/results.json`
- **Scripts in Folder**: `run_near_placebo.py`, `fetch_dev_ext.py`
- **Scope**: Recompute every table number and stated metric of `RESULT.md` from `results.json`, diff against prose, and report findings.

---

## 1. Per-Claim and Table Recomputation

Every number below is labeled SOURCED (quote + file:line) or OURS (independent extraction / recomputation from `results.json`).

### Table: Verdict arms (`RESULT.md:10-12`)

| Field | SOURCED (`RESULT.md:12`) | OURS (`results.json`) | Diff | Match? |
|---|---|---|---|---|
| Arm | `real minus near-band placebo (|d|<=1)` | `primary_near` (`max_abs_d: 1.0`) | 0 | MATCH |
| n | `352` | OURS: `352` (`primary_near.real.n = 352`) | 0 | MATCH |
| mean (pp) | `4.4` | OURS: `4.428759979397379` pp -> `4.4` pp (`primary_near.diff.diff * 100`) | 0.0 pp | MATCH |
| SE (pp) | `2.35` | OURS: `2.347364509141591` pp -> `2.35` pp (from 95% CI [-0.27, 8.93]: $(8.933 - (-0.268)) / (2 \times 1.96) \approx 2.347$) | 0.00 pp | MATCH |
| Verdict | `FAIL` | OURS: `FAIL` (`primary_verdict = "FAIL"`, CI lower bound -0.27 pp <= 0) | 0 | MATCH |

---

### Narrative and Stated Findings (`RESULT.md:1-24`)

| # | Item / Claim | SOURCED (`RESULT.md`) | OURS (`results.json`) | Diff | Match? |
|---|---|---|---|---|---|
| 1 | Days used | `730 complete UTC days` (`RESULT.md:4`) | OURS: `730` (`days_used: 730`) | 0 | MATCH |
| 2 | Dropped days | `dropped {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0}` (`RESULT.md:4`) | OURS: `{'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0}` (`dropped`) | 0 | MATCH |
| 3 | Verdict | `Verdict: FAIL (CI lower bound -0.3 pp is not above 0)` (`RESULT.md:7`) | OURS: `FAIL` (`primary_verdict: "FAIL"`, CI lo = -0.268 pp -> -0.3 pp) | 0 | MATCH |
| 4 | Primary real return share | `real return share 63.4 % (n 352, CI 58.2..68.2)` (`RESULT.md:14`) | OURS: share `63.352%` -> `63.4%`, n=`352`, CI `[58.239%, 68.169%]` -> `58.2..68.2` (`primary_near.real`) | 0.0 pp | MATCH |
| 5 | Primary near placebo share | `near placebo 58.9 % (n 353, CI 53.8..64.0)` (`RESULT.md:14`) | OURS: share `58.924%` -> `58.9%`, n=`353`, CI `[53.846%, 64.023%]` -> `53.8..64.0` (`primary_near.placebo`) | 0.0 pp | MATCH |
| 6 | Primary difference & CI | `difference 4.4 pp, 95 % day-block CI -0.3..8.9` (`RESULT.md:14`) | OURS: diff `+4.429 pp` -> `+4.4 pp`, CI `[-0.268 pp, +8.933 pp]` -> `-0.3..8.9` (`primary_near.diff`) | 0.0 pp | MATCH |
| 7 | Primary days | `Days in the primary: 365.` (`RESULT.md:14`) | OURS: `365` (`primary_near.n_days: 365`) | 0 | MATCH |
| 8 | Event counts breakdown | `352 real / 353 placebo events` (`RESULT.md:15`) | OURS: `352` real, `353` placebo (`primary_near.real.n`, `primary_near.placebo.n`) | 0 | MATCH |
| 9 | Far bands real share | `real 58.5 %` (`RESULT.md:16`) | OURS: `58.453%` -> `58.5%` (`far_descriptive.real.share`) | 0.0 pp | MATCH |
| 10 | Far bands placebo share | `placebo 37.3 %` (`RESULT.md:16`) | OURS: `37.326%` -> `37.3%` (`far_descriptive.placebo.share`) | 0.0 pp | MATCH |
| 11 | Far bands difference & CI | `diff 21.1 pp, CI 13.7..28.6` (`RESULT.md:16`) | OURS: diff `+21.127 pp` -> `+21.1 pp`, CI `[13.678 pp, 28.648 pp]` -> `13.7..28.6` (`far_descriptive.diff`) | 0.0 pp | MATCH |
| 12 | All-d real return share | `all-d real share 60.9 % (CI 57.2..64.4)` (`RESULT.md:17`) | OURS: share `60.913%` -> `60.9%`, CI `[57.163%, 64.358%]` -> `57.2..64.4` (`A.real`) | 0.0 pp | MATCH |
| 13 | Fee-net trade test | `A count of a claim, no fee/stop/target.` (`RESULT.md:24`) | OURS: NOT_IN_DATA / pure claim count; no fee model or net return in study data | 0 | MATCH |

---

## 2. Notes on Scope and Data
- The study evaluates the gross return share of Tom's 70/30 POC return claim against a near-band placebo ($|d| \le 1$).
- No fee or slippage deductions are modeled in `run_near_placebo.py` or `results.json` as this was an event count study rather than a trade simulation.
- All numbers cited in `RESULT.md` (the table and prose) reproduce exactly from `results.json` with zero discrepancy.

---

VERDICT: MATCH
