# Blind Read: pre-US failed break short DEV run on 10 USD-M symbols

- **Card**: `gemini-blind-read-pre-us-failed-break-10sym-1106` (`OURS`)
- **Date**: 2026-11-06 UTC (`OURS`)
- **Reader**: Gemini (independent blind read worker) (`OURS`)
- **Target study**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md` [SOURCED `RESULT.md:1-56`]
- **Pre-registration**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/PRE_REG.md` [SOURCED `PRE_REG.md:1-47`]
- **Source code & data**:
  - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analyze.py` [SOURCED `analyze.py:1-81`]
  - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/ledger.csv` (1393 rows) [SOURCED `ledger.csv:1-1394`]
  - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/per_symbol.csv` (10 symbols) [SOURCED `per_symbol.csv:1-11`]
  - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json` [SOURCED `analysis.json:1-36`]
  - `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/COUNT.json` [SOURCED `COUNT.json:1-55`]

---

## 1. Per-Claim Verification Table

| Item / Claim | SOURCED Claim (Quote & file:line) | Recomputed Value / Verification (OURS) | Status | Defect & Notes |
|---|---|---|---|---|
| **Phase / Split** | `DEV only, 2022-01-01..2024-06-30` [SOURCED `PRE_REG.md:9`, `RESULT.md:3`] | Verified min date `2022-01-11`, max date `2024-06-30` [SOURCED `ledger.csv:2,1394`]; no validation or holdout opened [OURS] | MATCH | None |
| **Window** | `pre-US 07:00-13:00 UTC` [SOURCED `PRE_REG.md:10`] | Min entry time `t_min = 422` (07:02 UTC), max `t_min = 778` (12:58 UTC) [OURS `ledger.csv`] | MATCH | None |
| **Costs** | `FEES_ALL_TAKER 0.0005 per leg ... + 2 bps slippage per leg ... 14 bps round trip` [SOURCED `PRE_REG.md:21`, `RESULT.md:5`] | 14 bps round trip per tranche (2 * 7 bps), funding 1 bp across 08:00 UTC [OURS `run_10sym.py:27`] | MATCH | None |
| **BTC count** | `BTC 177` [SOURCED `PRE_REG.md:31`, `RESULT.md:28`] | `177` [SOURCED `COUNT.json:4`, OURS `ledger.csv`] | MATCH | None |
| **ETH count** | `ETH 186` [SOURCED `PRE_REG.md:31`, `RESULT.md:29`] | `186` [SOURCED `COUNT.json:9`, OURS `ledger.csv`] | MATCH | None |
| **SOL count** | `SOL 141` [SOURCED `PRE_REG.md:31`, `RESULT.md:30`] | `141` [SOURCED `COUNT.json:14`, OURS `ledger.csv`] | MATCH | None |
| **BNB count** | `BNB 128` [SOURCED `PRE_REG.md:31`, `RESULT.md:31`] | `128` [SOURCED `COUNT.json:19`, OURS `ledger.csv`] | MATCH | None |
| **XRP count** | `XRP 124` [SOURCED `PRE_REG.md:31`, `RESULT.md:32`] | `124` [SOURCED `COUNT.json:24`, OURS `ledger.csv`] | MATCH | None |
| **DOGE count** | `DOGE 131` [SOURCED `PRE_REG.md:31`, `RESULT.md:33`] | `131` [SOURCED `COUNT.json:29`, OURS `ledger.csv`] | MATCH | None |
| **ADA count** | `ADA 106` [SOURCED `PRE_REG.md:31`, `RESULT.md:34`] | `106` [SOURCED `COUNT.json:34`, OURS `ledger.csv`] | MATCH | None |
| **AVAX count** | `AVAX 115` [SOURCED `PRE_REG.md:31`, `RESULT.md:35`] | `115` [SOURCED `COUNT.json:39`, OURS `ledger.csv`] | MATCH | None |
| **LINK count** | `LINK 137` [SOURCED `PRE_REG.md:31`, `RESULT.md:36`] | `137` [SOURCED `COUNT.json:44`, OURS `ledger.csv`] | MATCH | None |
| **LTC count** | `LTC 148` [SOURCED `PRE_REG.md:31`, `RESULT.md:37`] | `148` [SOURCED `COUNT.json:49`, OURS `ledger.csv`] | MATCH | None |
| **Missing bars** | `SOL, XRP, LTC each miss 7200 bars` [SOURCED `PRE_REG.md:26`] | `SOL 7200, XRP 7200, LTC 7200, others 0` [SOURCED `COUNT.json:16,26,51`] | MATCH | None |
| **Pooled n** | `1393` [SOURCED `PRE_REG.md:31`, `RESULT.md:12,16`] | `1393` episodes [OURS `ledger.csv`] | MATCH | None |
| **Mean net bps** | `-2.47` [SOURCED `RESULT.md:12,17`] | `-2.467156` bps of K [OURS `ledger.csv`] | MATCH | None |
| **SE (clustered)** | `4.39` [SOURCED `RESULT.md:12`] | `4.391812` bps [OURS `research_kit.cluster_mean_se`] | MATCH | None |
| **t (clustered)** | `-0.56` [SOURCED `RESULT.md:12,18`] | `-0.561763` [OURS m / se_c] | MATCH | None |
| **95% CI** | `-11.08 .. +6.14` [SOURCED `RESULT.md:12`] | `[-11.0751, 6.1408]` [OURS m +/- 1.96 * se_c] | MATCH | None |
| **SE plain / t plain** | `3.21 / -0.77` [SOURCED `RESULT.md:12`] | `3.214786 / -0.767440` [OURS sd / sqrt(n), m / se_p] | MATCH | None |
| **Measured sd** | `119.99` [SOURCED `RESULT.md:12,42`] | `119.985186` bps [OURS `ledger.csv`] | MATCH | None |
| **Check n >= 250** | `1393` ok [SOURCED `RESULT.md:16`] | `1393 >= 250` ok [OURS] | MATCH | None |
| **Check mean net > 0** | `-2.47` fails [SOURCED `RESULT.md:17`] | `-2.467 < 0` fails [OURS] | MATCH | None |
| **Check t >= 2.0** | `-0.56` fails [SOURCED `RESULT.md:18`] | `-0.562 < 2.0` fails [OURS] | MATCH | None |
| **Time-cap days** | `1270 days, sum -16,400 bps` [SOURCED `RESULT.md:19`] | `1270 days, sum -16399.80 bps` [OURS `ledger.csv`] | MATCH | None |
| **Target days** | `target 123 days, sum +12,963 bps` [SOURCED `RESULT.md:19`] | `123 days, sum +12963.05 bps` [OURS `ledger.csv`] | MATCH | None |
| **Time vs Target sum** | `loss < target gain: fails` [SOURCED `RESULT.md:19`] | Loss |-16400| > Gain |12963|: fails [OURS] | MATCH | None |
| **Pooled MDD** | `97.9 %` [SOURCED `RESULT.md:20`] | `97.9307 %` of K chronologically pooled [OURS] | MATCH | None |
| **BTC B&H MDD** | `66.9 %` [SOURCED `RESULT.md:20`] | `66.9359 %` [OURS daily close DEV peak-to-trough] | MATCH | None |
| **MDD check** | `97.9 <= BTC buy-and-hold 66.9: fails` [SOURCED `RESULT.md:20`] | `97.93 > 66.94`: fails [OURS] | MATCH | None |
| **Win rate** | `60.7 %` [SOURCED `RESULT.md:21`] | `846 / 1393 = 60.7322 %` [OURS `ledger.csv`] | MATCH | None |
| **Mean winner** | `+45.96 bps` [SOURCED `RESULT.md:21`] | `+45.9584 bps` [OURS `ledger.csv`] | MATCH | None |
| **Mean loser** | `-77.36 bps` [SOURCED `RESULT.md:21`] | `-77.3631 bps` [OURS `ledger.csv`] | MATCH | None |
| **MAE percentiles** | `0.21 / 1.87 / 6.22 / 22.25` [SOURCED `RESULT.md:22`] | `p50=0.206, p90=1.868, p99=6.219, max=22.249` [OURS] | MATCH | None |
| **Tranches 1/2/3/4** | `553 / 310 / 190 / 340` [SOURCED `RESULT.md:23`] | `553 / 310 / 190 / 340` (sum: 1393) [OURS `ledger.csv`] | MATCH | None |
| **Per-sym BTCUSDT** | `177 \| -3.24 \| 68.96 \| 0.60 \| 155 \| -573` [SOURCED `RESULT.md:28`] | `n=177, mean=-3.24, sd=68.96, win=0.60, time=155, sum=-573.12` [OURS] | MATCH | None |
| **Per-sym ETHUSDT** | `186 \| -2.51 \| 87.23 \| 0.58 \| 171 \| -466` [SOURCED `RESULT.md:29`] | `n=186, mean=-2.51, sd=87.23, win=0.58, time=171, sum=-466.10` [OURS] | MATCH | None |
| **Per-sym SOLUSDT** | `141 \| -24.04 \| 152.02 \| 0.61 \| 136 \| -3390` [SOURCED `RESULT.md:30`] | `n=141, mean=-24.04, sd=152.02, win=0.61, time=136, sum=-3389.73` [OURS] | MATCH | None |
| **Per-sym BNBUSDT** | `128 \| +3.47 \| 61.81 \| 0.61 \| 120 \| +445` [SOURCED `RESULT.md:31`] | `n=128, mean=+3.47, sd=61.81, win=0.61, time=120, sum=+444.51` [OURS] | MATCH | None |
| **Per-sym XRPUSDT** | `124 \| -0.07 \| 81.52 \| 0.57 \| 109 \| -9` [SOURCED `RESULT.md:32`] | `n=124, mean=-0.07, sd=81.52, win=0.57, time=109, sum=-9.24` [OURS] | MATCH | None |
| **Per-sym DOGEUSDT** | `131 \| +1.65 \| 232.59 \| 0.66 \| 122 \| +216` [SOURCED `RESULT.md:33`] | `n=131, mean=+1.65, sd=232.59, win=0.66, time=122, sum=+215.93` [OURS] | MATCH | None |
| **Per-sym ADAUSDT** | `106 \| +11.86 \| 118.06 \| 0.58 \| 95 \| +1258` [SOURCED `RESULT.md:34`] | `n=106, mean=+11.86, sd=118.06, win=0.58, time=95, sum=+1257.58` [OURS] | MATCH | None |
| **Per-sym AVAXUSDT** | `115 \| +3.05 \| 121.71 \| 0.62 \| 101 \| +351` [SOURCED `RESULT.md:35`] | `n=115, mean=+3.05, sd=121.71, win=0.62, time=101, sum=+351.03` [OURS] | MATCH | None |
| **Per-sym LINKUSDT** | `137 \| +9.68 \| 92.63 \| 0.64 \| 125 \| +1327` [SOURCED `RESULT.md:36`] | `n=137, mean=+9.68, sd=92.63, win=0.64, time=125, sum=+1326.63` [OURS] | MATCH | None |
| **Per-sym LTCUSDT** | `148 \| -17.53 \| 109.19 \| 0.61 \| 136 \| -2594` [SOURCED `RESULT.md:37`] | `n=148, mean=-17.53, sd=109.19, win=0.61, time=136, sum=-2594.22` [OURS] | MATCH | None |
| **Regime weeks** | `130 weeks: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%)` [SOURCED `RESULT.md:7`] | `130 weeks: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%)` [SOURCED `analysis.json:28`] | MATCH | None |
| **Regime episodes** | `bull n=255 mean -2.43; range n=1138 mean -2.48` [SOURCED `RESULT.md:7,39`] | Bull n=255 mean=-2.43 bps; Range n=1138 mean=-2.48 bps [OURS `analysis.json`, `ledger.csv`] | MATCH | None |
| **Year 2022** | `2022 n=552 +3.64` [SOURCED `RESULT.md:39`] | `n=552, mean=+3.64 bps` [OURS `ledger.csv`] | MATCH | None |
| **Year 2023** | `2023 n=573 -8.29` [SOURCED `RESULT.md:39`] | `n=573, mean=-8.29 bps` [OURS `ledger.csv`] | MATCH | None |
| **Year 2024** | `2024 n=268 -2.59` [SOURCED `RESULT.md:39`] | `n=268, mean=-2.59 bps` [OURS `ledger.csv`] | MATCH | None |
| **Positive symbols count** | `(four of ten symbols positive, none individually tested)` [SOURCED `RESULT.md:39`] | Exactly 5 symbols are positive: ADA (+11.86), AVAX (+3.05), BNB (+3.47), DOGE (+1.65), LINK (+9.68). Exactly 5 are negative: BTC (-3.24), ETH (-2.51), LTC (-17.53), SOL (-24.04), XRP (-0.07). [OURS `per_symbol.csv:2-11`] | **MISMATCH** | **Defect at `RESULT.md:39`**: Prose claims 4 of 10 symbols positive, but data shows 5 of 10 are positive. |
| **Gate re-run (sd 120)** | `n 1393 sd 120 m 221 z_holm 3.688 MDE 14.558 R + cost 14 = 28.558 vs max plausible gross 30; n needed 1153; PASS` [SOURCED `RESULT.md:44-46`] | Recomputed formula with m=221: z=3.6883, MDE=14.558, R+cost=28.558, n needed 1153 <= 1393 -> PASS [OURS `prereg_gate.py`] | MATCH | None |
| **Powered status** | `Powered at the measured sd (n 1393 >= 1153 needed), so the FAIL is not UNDERPOWERED` [SOURCED `RESULT.md:48`] | `1393 >= 1153` -> powered, not underpowered [OURS] | MATCH | None |
| **Outcome Verdict** | `FAIL` [SOURCED `RESULT.md:1,52,56`, `sim_desk_card_held.json:22`] | Conforms to `PRE_REG.md:46` criteria (4 of 5 checks fail, n >= 250, powered) -> FAIL [OURS] | MATCH | None |

---

## 2. Findings and Contradiction Audit

1. **Exact Reproduction of All Quantitative Data (74 of 75 claims MATCH)**:
   - Every single entry across the Pooled Table (7 metrics), the Gate Check Table (8 metrics), the Per-Symbol Table (10 symbols x 6 columns = 60 metrics), the Breakdown by Year (3 years), and the Breakdown by Regime Week reproduces from `ledger.csv` and `analysis.json` with 100% precision.
   - The pass/fail rules frozen in `PRE_REG.md:46` are applied with complete fidelity:
     - $n = 1393 \ge 250$ (OK)
     - Mean net return $-2.47 < 0$ (FAILS)
     - Clustered $t = -0.56 < 2.0$ (FAILS)
     - Time-cap loss (1270 days, sum $-16,400$ bps) exceeds target gain (123 days, sum $+12,963$ bps) (FAILS)
     - Pooled MDD ($97.9\%$ of $K$) exceeds BTC DEV buy-and-hold MDD ($66.9\%$) (FAILS)
   - Gate re-run confirms power: $n_{\text{needed}} = 1153 \le 1393$, ruling out UNDERPOWERED.

2. **Identified Defect**:
   - `RESULT.md:39`: `(four of ten symbols positive, none individually tested)`
   - Verified data in `per_symbol.csv:2-11` and `RESULT.md:28-37`:
     - Positive mean net bps (5 symbols): ADAUSDT (+11.86), AVAXUSDT (+3.05), BNBUSDT (+3.47), DOGEUSDT (+1.65), LINKUSDT (+9.68).
     - Negative mean net bps (5 symbols): BTCUSDT (-3.24), ETHUSDT (-2.51), LTCUSDT (-17.53), SOLUSDT (-24.04), XRPUSDT (-0.07).
     - The prose claim states "four of ten symbols positive", whereas the table directly above it contains five positive symbols. This is an isolated prose counting error; it does not alter the study conclusion (the rule was pre-registered as a single pooled cell, not per-symbol, and none of the individual symbols were tested or cleared).

---

## 3. Verdict

Defect identified: `RESULT.md:39` claims "four of ten symbols positive", whereas exact per-symbol data in `RESULT.md:28-37` and `per_symbol.csv:2-11` shows 5 of 10 symbols are positive (ADAUSDT +11.86, AVAXUSDT +3.05, BNBUSDT +3.47, DOGEUSDT +1.65, LINKUSDT +9.68). All 74 quantitative metrics and the study outcome (FAIL powered) reproduce with 100% precision.

VERDICT: MISMATCH
