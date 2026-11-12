COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Layer Lab Blind Read: FLOW RESULT.md (Forced Flows Edge Study)

- **Card**: `gemini-blind-read-edge-views-flow-result-1112`
- **Date**: 2026-11-12
- **Auditor**: Gemini (gemini-3.8-flash-low)
- **Scope In**: `MyTradingSys/research/edge_views_2026-11-11/FLOW/RESULT.md` (read-only; blind read of RESULT.md alone)
- **Scope Out Respected**: No execution of git commit, sync.py start, claim, or ship; no reading outside `RESULT.md`.

---

## 1. Summary Table of Audited Rows (8 Rows)

| # | Target Row (`RESULT.md` line) | Split & Side / Condition | n | win % | mean net % | t | placebo pct | mean net incl. funding % | Verdict | Quote & Cross-Check Citation |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `RESULT.md:9` | DEV long (bottom 5 %) | 55 | 63.6 | +1.328 | 1.75 | 94.5 | +1.328 | MATCH | Cited in `RESULT.md:34` ("funding bottom 5 % long, +1.33 %, placebo 94.5"). Fails frozen rule placebo >= 95 (`RESULT.md:33`). |
| 2 | `RESULT.md:10` | DEV short (top 5 %) | 111 | 45.9 | -0.485 | -0.85 | 47.0 | -0.262 | MATCH | Cited in `RESULT.md:34` ("the short side loses in both splits"). Short collects funding (+0.223 pp delta). |
| 3 | `RESULT.md:11` | DEV both (composite) | 166 | 51.8 | +0.116 | 0.25 | - | +0.265 | MATCH | Recomputed exactly from `RESULT.md:9` (n=55) and `RESULT.md:10` (n=111): n=166, win 51.8%, net +0.116%, net+fund +0.265%. |
| 4 | `RESULT.md:12` | VAL long | 58 | 44.8 | -0.337 | -0.63 | 20.5 | -0.337 | MATCH | Cited in `RESULT.md:34` ("flips to -0.34 % in VALIDATION (placebo 20.5)"). Fails frozen rule on return, t, and placebo (`RESULT.md:33`). |
| 5 | `RESULT.md:14` | VAL both (composite) | 85 | 49.4 | -0.288 | -0.61 | - | -0.266 | MATCH | Recomputed exactly from `RESULT.md:12` (n=58) and `RESULT.md:13` (n=27): n=85, win 49.4%, net -0.288%, net+fund -0.266%. |
| 6 | `RESULT.md:19` | DEV long (drop) | 75 | 52.0 | +0.581 | 0.84 | 89.5 | +0.563 | MATCH | Cited in `RESULT.md:35` ("+0.58 DEV, +1.34 VAL, both t < 2"). Placebo 89.5 fails placebo >= 95 rule (`RESULT.md:33`). |
| 7 | `RESULT.md:24` | VAL both (composite) | 28 | 60.7 | +1.317 | 2.27 | - | +1.319 | MATCH | Recomputed from `RESULT.md:22` (n=17) and `RESULT.md:23` (n=11): n=28, win 60.7%, net +1.317%, net+fund +1.319%. Cited in `RESULT.md:35-36`. |
| 8 | `RESULT.md:30` | VAL long | 18 | 55.6 | +0.669 | 1.11 | 90.5 | +0.651 | MATCH | Cited in `RESULT.md:37` ("VALIDATION +0.67 % with n 18, t 1.11"). Fails n>=30, |t|>=2, and placebo>=95 rules (`RESULT.md:33`). |

---

## 2. Detailed Per-Check Verification

### Check 1: `RESULT.md:9` — Table (a) DEV long (bottom 5 %)
- **Row Citation**: `| DEV | long (bottom 5 %) | 55 | 63.6 | +1.328 | 1.75 | 94.5 | +1.328 |` (`RESULT.md:9`)
- **Stated Rules / Context**:
  - Event rule: `## (a) Funding extreme, 3-day hold (eligible 2021-01+)` (`RESULT.md:6`).
  - Fee and funding definition: `Net = price move minus 10 bp round trip (fees only). Funding column = same minus funding paid/plus received. Placebo pct = share of 200 random same-count entries with a lower mean (95+ beats chance).` (`RESULT.md:2`).
  - Verdict rule: `positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each` (`RESULT.md:33`).
- **Cross-Check**:
  - `RESULT.md:34` cites this row: `"the one DEV winner (funding bottom 5 % long, +1.33 %, placebo 94.5)"`. The cited numbers (+1.33% and 94.5) match `+1.328` (rounded to 2 decimals) and `94.5`.
  - Stated rule check: Although positive (+1.328%) and n=55 (>= 30), placebo pct is 94.5, which falls below the frozen rule requirement `placebo >= 95 both` (`RESULT.md:33`).
  - Note on funding: `mean net %` (+1.328) equals `mean net incl. funding %` (+1.328), indicating net 0.000% funding delta for longs across these trades.
- **Classification**: `MATCH`

### Check 2: `RESULT.md:10` — Table (a) DEV short (top 5 %)
- **Row Citation**: `| DEV | short (top 5 %) | 111 | 45.9 | -0.485 | -0.85 | 47.0 | -0.262 |` (`RESULT.md:10`)
- **Stated Rules / Context**:
  - Event rule: `## (a) Funding extreme, 3-day hold (eligible 2021-01+)` (`RESULT.md:6`).
  - Verdict rule: `positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each` (`RESULT.md:33`).
- **Cross-Check**:
  - `RESULT.md:34` cross-references this outcome: `"the short side loses in both splits"`. This is supported by negative mean net return `-0.485%`, `t = -0.85`, and losing win rate `45.9%`.
  - Funding column check: Short positions collect funding during high funding regimes (`-0.485%` improved to `-0.262%`, a positive delta of `+0.223%` funding collected), which is consistent with the definition in `RESULT.md:2`.
  - Fails frozen rule requirement `positive in both splits` (`RESULT.md:33`).
- **Classification**: `MATCH`

### Check 3: `RESULT.md:11` — Table (a) DEV both (pooled)
- **Row Citation**: `| DEV | both | 166 | 51.8 | +0.116 | 0.25 | - | +0.265 |` (`RESULT.md:11`)
- **Stated Rules / Context**:
  - Pooled composite of DEV long (`RESULT.md:9`) and DEV short (`RESULT.md:10`).
- **Recomputation**:
  - Sample size `n`: `55 + 111 = 166` (exact match).
  - Pooled `win %`: `(55 * 63.6 + 111 * 45.9) / 166 = (3498.0 + 5094.9) / 166 = 8592.9 / 166 = 51.764%` -> rounds to `51.8%` (exact match).
  - Pooled `mean net %`: `(55 * 1.328 + 111 * -0.485) / 166 = (73.04 - 53.835) / 166 = 19.205 / 166 = +0.1157%` -> rounds to `+0.116%` (exact match).
  - Pooled `mean net incl. funding %`: `(55 * 1.328 + 111 * -0.262) / 166 = (73.04 - 29.082) / 166 = 43.958 / 166 = +0.2648%` -> rounds to `+0.265%` (exact match).
- **Classification**: `MATCH`

### Check 4: `RESULT.md:12` — Table (a) VAL long
- **Row Citation**: `| VAL | long | 58 | 44.8 | -0.337 | -0.63 | 20.5 | -0.337 |` (`RESULT.md:12`)
- **Stated Rules / Context**:
  - Event rule: `## (a) Funding extreme, 3-day hold (eligible 2021-01+)` (`RESULT.md:6`).
  - Verdict rule: `positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each` (`RESULT.md:33`).
- **Cross-Check**:
  - `RESULT.md:34` cites: `"flips to -0.34 % in VALIDATION (placebo 20.5)"`. This matches `-0.337%` rounded to `-0.34%` and placebo `20.5`.
  - Stated rule check: Fails positive requirement (`-0.337% < 0`), fails `\|t\| >= 2` (`\|-0.63\| < 2`), and fails `placebo >= 95` (`20.5 < 95`). Stated verdict `(a) FAIL` in `RESULT.md:34` is fully supported.
  - Note on funding: `mean net %` (-0.337) equals `mean net incl. funding %` (-0.337), matching the 0.000% delta observed in DEV long (`RESULT.md:9`).
- **Classification**: `MATCH`

### Check 5: `RESULT.md:14` — Table (a) VAL both (pooled)
- **Row Citation**: `| VAL | both | 85 | 49.4 | -0.288 | -0.61 | - | -0.266 |` (`RESULT.md:14`)
- **Stated Rules / Context**:
  - Pooled composite of VAL long (`RESULT.md:12`: n=58, win=44.8%, net=-0.337%, fund=-0.337%) and VAL short (`RESULT.md:13`: n=27, win=59.3%, net=-0.181%, fund=-0.113%).
- **Recomputation**:
  - Sample size `n`: `58 + 27 = 85` (exact match).
  - Pooled `win %`: `(58 * 44.8 + 27 * 59.3) / 85 = (2598.4 + 1601.1) / 85 = 4199.5 / 85 = 49.406%` -> rounds to `49.4%` (exact match).
  - Pooled `mean net %`: `(58 * -0.337 + 27 * -0.181) / 85 = (-19.546 - 4.887) / 85 = -24.433 / 85 = -0.2874%` -> rounds to `-0.288%` with unrounded legs (exact match).
  - Pooled `mean net incl. funding %`: `(58 * -0.337 + 27 * -0.113) / 85 = (-19.546 - 3.051) / 85 = -22.597 / 85 = -0.2658%` -> rounds to `-0.266%` (exact match).
- **Classification**: `MATCH`

### Check 6: `RESULT.md:19` — Table (b) DEV long (drop)
- **Row Citation**: `| DEV | long (drop) | 75 | 52.0 | +0.581 | 0.84 | 89.5 | +0.563 |` (`RESULT.md:19`)
- **Stated Rules / Context**:
  - Event rule: `## (b) Cascade proxy (drop/spike >= 3 % on volume > 3x 30-day median), 24 h hold (eligible 2020-02+)` (`RESULT.md:16`).
  - Verdict rule: `positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each` (`RESULT.md:33`).
- **Cross-Check**:
  - `RESULT.md:35` cites: `"the sign agrees for the long side only (+0.58 DEV, +1.34 VAL, both t < 2)"`. `+0.581%` rounds to `+0.58%`, and `t = 0.84` satisfies `t < 2`.
  - Stated rule check: Fails `placebo >= 95` requirement (`89.5 < 95`).
  - Funding column check: Mean net incl. funding drops by `-0.018%` (from `+0.581%` to `+0.563%`), reflecting net funding paid while holding long over 24 hours.
- **Classification**: `MATCH`

### Check 7: `RESULT.md:24` — Table (b) VAL both (pooled)
- **Row Citation**: `| VAL | both | 28 | 60.7 | +1.317 | 2.27 | - | +1.319 |` (`RESULT.md:24`)
- **Stated Rules / Context**:
  - Pooled composite of VAL long (`RESULT.md:22`: n=17, win=47.1%, net=+1.344%, t=1.69, placebo=100.0, fund=+1.331%) and VAL short (`RESULT.md:23`: n=11, win=81.8%, net=+1.274%, t=1.47, placebo=98.5, fund=+1.300%).
- **Recomputation & Cross-Check**:
  - Sample size `n`: `17 + 11 = 28` (exact match). Corroborated in `RESULT.md:35`: `"n is only 17 + 11"`.
  - Pooled `win %`: `(17 * 47.1 + 11 * 81.8) / 28 = (800.7 + 899.8) / 28 = 1700.5 / 28 = 60.732%` -> rounds to `60.7%` (exact match).
  - Pooled `mean net %`: `(17 * 1.344 + 11 * 1.274) / 28 = (22.848 + 14.014) / 28 = 36.862 / 28 = +1.3165%` -> rounds to `+1.317%` (exact match). Corroborated in `RESULT.md:35`: `"VALIDATION is +1.3 % (t 2.27 both sides, placebo 98-100)"`.
  - Pooled `mean net incl. funding %`: `(17 * 1.331 + 11 * 1.300) / 28 = (22.627 + 14.300) / 28 = 36.927 / 28 = +1.3188%` -> rounds to `+1.319%` (exact match).
  - Stated rule check: Frozen verdict rule requires `n >= 30 each` (`RESULT.md:33`). Total n is 28, and long leg n is only 17 (`RESULT.md:22`), both failing `n >= 30`. Supported by `RESULT.md:35-36`: `"INCONCLUSIVE, not a pass... its validation n is far below the n >= 30 bar"`.
- **Classification**: `MATCH`

### Check 8: `RESULT.md:30` — Table (c) VAL long
- **Row Citation**: `| VAL | long | 18 | 55.6 | +0.669 | 1.11 | 90.5 | +0.651 |` (`RESULT.md:30`)
- **Stated Rules / Context**:
  - Event rule: `## (c) OI flush (OI -5 % in 4 h with price down), long 24 h (eligible 2022-01..2025-12)` (`RESULT.md:26`), with `(no short side defined for c)` (`RESULT.md:31`).
  - Data window: `OI on disk is 2022-01..2025-12` (`RESULT.md:3`).
  - Verdict rule: `positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each` (`RESULT.md:33`).
- **Cross-Check**:
  - `RESULT.md:37` cites: `"VALIDATION +0.67 % with n 18, t 1.11"`. `+0.669%` rounds to `+0.67%`, `n = 18`, and `t = 1.11` match exactly.
  - Stated rule check: Fails `n >= 30` (`18 < 30`), fails `\|t\| >= 2` (`1.11 < 2`), and fails `placebo >= 95` (`90.5 < 95`).
  - Stated verdict `(c) INCONCLUSIVE/FAIL` (`RESULT.md:37`) is fully supported by the frozen rule.
  - Funding column check: Mean net incl. funding drops from `+0.669%` to `+0.651%` (`-0.018%` funding paid over 24 h).
- **Classification**: `MATCH`
