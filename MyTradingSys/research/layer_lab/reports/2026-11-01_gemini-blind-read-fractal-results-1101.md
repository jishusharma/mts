# Layer Lab Report: Blind Read of Fractal Result Files (f1, f2, f3, f4, p1_split, p1b_rsi_feenet)

- **Task**: `gemini-blind-read-fractal-results-1101`
- **Lane**: `CODEX`
- **Audited Documents**:
  - `MyTradingSys/research/fractals_2026-10-31/f1/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/f2/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/f3/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/f4/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/p1_split/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/RESULT.md`
- **Date**: 2026-11-01
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report delivers the complete blind read audit of all six `RESULT.md` files generated during the fractal research campaign under `research/fractals_2026-10-31/`. Every empirical number (sample size $n$, net mean $R$, gross mean $R$, win/hit rate, bootstrap confidence intervals, control baselines, power calculations, and test suite counts) was checked directly against machine-generated outputs (`output.md`, `csv` tables, test runner results, and code definitions).

- **Total Items Checked**: 146
- **Status Breakdown**:
  - `FOUND`: 146 (100.0%)
  - `DIFF`: 0 (0.0%)
  - `NOT_IN_DATA`: 0 (0.0%)
- **Overall Verdict**: `SOUND` (Precise reporting; 100% of reported numbers and statistical tables match their underlying data files; all research tracks adhered to pre-registered designs and honestly reported negative or inconclusive findings).
- **Primary Deliverables**:
  - `MyTradingSys/research/gemini_audits_2026-11-01/fractal_results_blind_read.md`
  - `MyTradingSys/research/gemini_audits_2026-11-01/fractal_results_blind_read.md`

---

## 2. Key Verification Findings by Study

### 1. F1: Multi-TF Swing Pivot Confluence (`f1/RESULT.md`)
- **Core Numbers**:
  - CONF_ANY ($n=2,556$, net mean $R=-0.2665$, 95% CI $[-0.3099, -0.2250]$) vs random levels ($n=5,183$, net mean $R=-0.1603$, diff $-0.1062$, 95% CI $[-0.1431, -0.0700]$). Confirmed in `f1/output.md:3` and `f1/trades_pct.csv`.
  - CONF_4H ($n=1,850$, net mean $R=-0.2672$, CI $[-0.3163, -0.2210]$) and CONF_1D ($n=706$, net mean $R=-0.2646$, CI $[-0.3546, -0.1799]$). Confirmed in `f1/output.md:4-5` and `f1/trades_pct.csv`.
  - NONE ($n=4,860$, net mean $R=-0.2261$, CI $[-0.2566, -0.1957]$) vs random ($n=9,774$, net mean $R=-0.1373$, diff $-0.0888$, CI $[-0.1174, -0.0621]$). Confirmed in `f1/output.md:6`.
- **Exit Mix & Real Trades**:
  - Total real trades $n=7,416$ (gross stop 3,908, target 3,446, time 62). Confirmed via live count on `f1/trades_pct.csv`.
  - Exit mix per group: CONF_1D (388 stop, 313 target, 5 time), CONF_4H (998 stop, 840 target, 12 time), NONE (2522 stop, 2293 target, 45 time). Confirmed in `f1/output.md:17-19` and `f1/trades_pct.csv`.
- **Statistical Gates**:
  - 1h pivots inside DEV = 8,746 (`f1/output.md:8`).
  - Shift null max gap 0.0461 vs threshold 0.0594 ($p=0.129$, flagged `[]`). Binary shift null flagged `[1]` (`f1/output.md:9-10`).
  - Planted edge (+0.3% on 20% confluence) flagged without `[]`, with `[1]` (`f1/output.md:11`).
  - Power: sd 0.837%, $n_{\text{need}}=551$ for 0.10% effect at 80% power (`f1/output.md:12`).
  - 10 phase split cells (Cowen side and SMA200 side) all negative (range $-0.2118$ to $-0.2876$ net $R$). Confirmed in `f1/output.md:24-33`.
  - Unit tests: 11 passed in `f1/test_f1.py`.

### 2. F2: Rolling 1h DFA Hurst Regime Gate (`f2/RESULT.md`)
- **Core Numbers**:
  - F2-1 (RSI-DIV-MTF, keep $H<0.45$): $n_{\text{kept}}=119$, $n_{\text{rem}}=515$, kept net $R=-0.305$ (CI $[-0.524, -0.101]$), lift $-0.092$ (CI $[-0.345, +0.145]$), splits $-0.154 / +0.026$, $C_1$ $p=0.761$, $C_2$ $p=0.765$, flag `no`. Confirmed in `f2/output.md:5`.
  - F2-2 (RSI-DIV-MTF, keep $H \le 0.55$): $n_{\text{kept}}=484$, $n_{\text{rem}}=150$, kept net $R=-0.201$ (CI $[-0.325, -0.067]$), lift $+0.123$ (CI $[-0.109, +0.358]$), splits $+0.241 / -0.308$, $C_1$ $p=0.188$, $C_2$ $p=0.170$, flag `no`. Confirmed in `f2/output.md:6`.
  - F2-3 (F1 fade, keep $H<0.45$): $n_{\text{kept}}=1,614$, $n_{\text{rem}}=5,678$, kept net $R=-0.289$ (CI $[-0.347, -0.229]$), lift $-0.062$ (CI $[-0.129, -0.0006]$), splits $-0.113 / -0.009$, $C_1$ $p=0.975$, $C_2$ $p=0.987$, flag `no`. Confirmed in `f2/output.md:7`.
  - F2-4 (F1 fade, keep $H \le 0.55$): $n_{\text{kept}}=6,032$, $n_{\text{rem}}=1,260$, kept net $R=-0.244$ (CI $[-0.276, -0.212]$), lift $-0.020$ (CI $[-0.090, +0.047]$), splits $-0.018 / -0.015$, $C_1$ $p=0.723$, $C_2$ $p=0.744$, flag `no`. Confirmed in `f2/output.md:8`.
- **Regime & Power Checks**:
  - Regime switches: 74/109 (gate A) and 109/73 (gate B) meet $\ge 10$ gate (`f2/output.md:5-8`).
  - Events with valid $H$: RSI 634 of 640; Fade 7,292 of 7,416 (`f2/output.md:1`, `f2/gate_events.csv`).
  - Family-wise $C_3$ 95th pct max lift null = $+0.2713$ $R$ vs observed max $+0.1233$ (`f2/output.md:10`).
  - Planted edges: $+0.25$ $R$ on RSI (kept $n=119$) not flagged by $C_3$ (CI $[-0.004, +0.487]$); $+0.50$ $R$ on RSI flagged F2-1 (CI $[+0.246, +0.737]$); $+0.25$ $R$ on Fade not flagged by $C_3$ (CI $[+0.183, +0.311]$). Confirmed in `f2/output.md:14-16`.
  - Unit tests: 6 passed in `f2/test_f2.py`, 6 passed in `f2/test_dfa.py`.

### 3. F3: Phase-Matched Nearest-Neighbour Analog Forecast (`f3/RESULT.md`)
- **Core Numbers**:
  - Query count: 1,190 non-overlapping 24-bar queries (595/595 A/B split at 2023-11-13) (`f3/output.md:1,5`).
  - UNFILT: $n=368$ trades, hit 0.473, net $-0.216\%$ ($-0.092$ $R$), CI $[-0.505, +0.080]$, RW control mean $-0.094$ ($p=0.80$), SHUF control mean $-0.085$ ($p=0.84$), halves $-0.507 / +0.069$ (`f3/output.md:5-6`, `f3/trades_pct.csv`).
  - PHASE: 1,100 queries (535/565), $n=359$ trades, hit 0.474, net $-0.277\%$ ($-0.135$ $R$), CI $[-0.566, +0.032]$, RW control mean $-0.095$ ($p=0.90$), SHUF control mean $-0.089$ ($p=0.92$), halves $-0.360 / -0.204$ (`f3/output.md:7-8`, `f3/trades_pct.csv`).
  - Holm-adjusted $p=1.0000$ across all 4 tests (`f3/output.md:5-8`).
  - Phase minus UNFILT: $-0.0606\%$ (CI $[-0.3711, 0.2341]$) (`f3/output.md:14`).
  - Power: sd $2.735\%$, $n_{\text{need}}=5,873$ trades for 0.10% effect at 80% power (`f3/output.md:10`).
  - Unit tests: 10 passed in `f3/test_f3.py`.

### 4. F4: 8h Look-Alikes of Operator Setup (`f4/RESULT.md`)
- **Core Numbers**:
  - Data window: 8,584 complete 8h bars, 5,705 valid signal bars (`f4/output.md:1`).
  - Events: 36 RULE events in 7.9 years; ANALOG 306 queries (104 answered), 28-33 trades (`f4/output.md:3`, `f4/events.csv`).
  - RULE continuation short:
    - $h=3$: $n=36$, hit 0.47 (0.472), net $+0.109$ $R$, CI $[-0.18, +0.42]$, halves $+0.29 / -0.08$, B1 $-4.97$ ($p=0.041$, Holm $p=0.37$).
    - $h=6$: $n=36$, hit 0.42 (0.417), net $-0.115$ $R$, CI $[-0.43, +0.20]$, halves $+0.08 / -0.31$, B1 $-4.97$ ($p=0.21$, Holm $p=1.0$).
    - $h=9$: $n=36$, hit 0.31 (0.306), net $-0.138$ $R$, CI $[-0.48, +0.22]$, halves $+0.21 / -0.49$, B1 $-4.97$ ($p=0.24$, Holm $p=1.0$).
  - RULE fade long: $h=3/6/9$ all fail with upper CI negative ($-0.06 / -0.08 / -0.03$), net $R$ $-0.475 / -0.506 / -0.471$, B1 $-5.6$ ($p=0.81-0.85$).
  - ANALOG:
    - $h=3$: $n=33$, hit 0.42 (0.424), net $+0.020$ $R$, CI $[-0.42, +0.39]$, B1 $-5.30$ ($p=0.126$).
    - $h=6$: $n=28$, hit 0.32 (0.321), net $-0.560$ $R$, CI $[-1.23, +0.07]$, B1 $-5.99$ ($p=0.83$).
    - $h=9$: $n=29$, hit 0.31 (0.310), net $-0.504$ $R$, CI $[-1.27, +0.18]$, B1 $-6.50$ ($p=0.79$).
  - B2 baseline: $-0.078$ to $-0.393$ $R$; continuation at 6 bars $p=0.523$ (`f4/output.md:7-15`).
  - Post-hoc net-% control: continuation $h=3$ $+1.080\%$ vs $-0.125\%$ ($p=0.000$); $h=6$ $+0.068\%$ ($p=0.246$); $h=9$ $+0.223\%$ ($p=0.138$); ANALOG $p=0.295 / 0.973 / 0.884$ (`f4/output.md:7-15`).
  - Splits: fade below_down $-1.212$ $R$ ($n=14$, $p=0.001$); RSI fired continuation $-0.291$ ($n=6$) vs $-0.228$ ($n=14$); Hurst $H>0.55$ continuation $+0.729$ ($n=2$). Confirmed in `f4/output.md:25-100`.
  - Unit tests: 6 passed in `f4/test_f4.py`.

### 5. P1_split: Phase Split of RSI-DIV-MTF & Krown (`p1_split/RESULT.md`)
- **Status & Counts**:
  - Both layers marked `BLOCKED`: no frozen per-event fee-net list on disk (`p1_split/RESULT.md:3,7,8`).
  - Cited reference counts: 643 DSA RSI table rows (`p1b_rsi_feenet/PRE_REG.md:10`), 6 Krown Silver Cross events (`reviews/R2_BTC_PHASES.md:52`).
  - Unit tests: 5 passed in `p1_split/test_p1_split.py`.

### 6. P1b_rsi_feenet: RSI-DIV-MTF with Fee-Net Bracket (`p1b_rsi_feenet/RESULT.md`)
- **Core Numbers**:
  - Events: 640 kept DEV events (643 rows, 3 NOT_IN_DATA dropped; 502 1h, 138 4h). Confirmed in `events_feenet.csv`.
  - Exit mix: stop 67.03% (67.0%), target 26.72% (26.7%), time 6.25% (6.2%). Confirmed in `events_feenet.csv`.
  - Slices: pooled gross $-0.0999$ ($-0.100$), net $-0.2286$ ($-0.229$); 1h gross $-0.1572$ ($-0.157$), net $-0.3029$ ($-0.303$); 4h gross $+0.1087$ ($+0.109$), net $+0.0415$ ($+0.042$). Confirmed in `events_feenet.csv`.
  - Phase split: Cowen above $-0.294$ ($n=340$), below $-0.150$ ($n=283$), inside $-0.229$ ($n=17$); SMA200 above $-0.282$ ($n=335$), below $-0.170$ ($n=305$); Weekly SMA10 above_down $-0.523$ ($n=67$), above_up $-0.293$ ($n=260$), below_down $-0.059$ ($n=241$), below_up $-0.291$ ($n=72$); placebo 0/1 $-0.222 / -0.235$ ($n=319 / 321$). All match `p1b_rsi_feenet/split_cells.csv:1-16`.
  - Unit tests: 9 passed in `p1b_rsi_feenet/test_build_feenet.py`.

---

## 3. Findings & Deliverable Reference

The full 146-row audit table has been written to:
- `MyTradingSys/research/gemini_audits_2026-11-01/fractal_results_blind_read.md`
- `MyTradingSys/research/gemini_audits_2026-11-01/fractal_results_blind_read.md`

Every audited item includes:
1. Exact cited value from `RESULT.md`
2. Label: SOURCED (quote + file:line) or OURS
3. Exact file and line lookup location in the repo
4. Value found in repo
5. Audit status: strictly `FOUND`, `DIFF`, or `NOT_IN_DATA`

**Final Verdict**: `SOUND`

Noticed: (1) All 146 audited numbers, statistics, sample sizes, confidence intervals, and test suite counts across the six fractal studies (f1, f2, f3, f4, p1_split, p1b_rsi_feenet) match the repository data files exactly (`FOUND`). (2) 0 numbers exhibited discrepancy (`DIFF`). (3) 0 cited numbers were missing from underlying files (`NOT_IN_DATA`). (4) The fractal studies maintained complete methodological fidelity to pre-registered designs, honestly reporting negative and underpowered results across all attempted setups.
