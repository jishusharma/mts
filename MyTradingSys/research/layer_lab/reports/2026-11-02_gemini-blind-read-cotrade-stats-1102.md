# Layer Lab Report: Blind Re-read of testnet_cotrade DESIGN.md and P5_BRIEF.md Numbers vs stats_run.json

- **Task**: `gemini-blind-read-cotrade-stats-1102`
- **Lane**: `CODEX`
- **Audited Documents**:
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/DESIGN.md`
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/P5_BRIEF.md`
- **Underlying Sources**:
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/stats_run.json`
  - `MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py`
  - Execution modules: `risk_guard.py`, `trade_plan_validator.py`, `daily_loss_guard.py`, `cotrade.py`, `deribit_orders.py`, `executor.py`, `journal.py`
  - Research findings: `eur_low_us_sweep_2026-10-14/RESULT.md`, `us_open_oos_2026-10-30/REPORT.md`, `pre_us_squeeze_2026-10-29/RESULT.md`, `us_open_levels_2026-10-30/RESULT.md`, commit `4a36c8a38` (`results.txt`)
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report completes the blind re-read and verification of every quantitative metric, clock fact, ladder step, risk cap, and testnet specification contained in `testnet_cotrade_2026-10-31/DESIGN.md` and `P5_BRIEF.md`.

- **Total Claims / Numbers Audited**: 107
- **FOUND**: 106 (99.1%)
- **NOT_IN_DATA**: 1 (0.9%) — explicitly acknowledged in `DESIGN.md:65` as an empirical null finding ("Something happens just before as a tradable signal | NOT_IN_DATA").
- **DIFF**: 0 (0.0%)
- **Overall Verdict**: `SOUND` (Exact numerical alignment between text claims, `stats_run.json`, `ladder_math.py`, and repo code).

---

## 2. Key Findings by Category

### 1. Ladder Math & Worst-Case Loss (`ladder_math.py`)
- Independent re-execution of `ladder_math.py` validates all four reported steps in `DESIGN.md:28-31`:
  - Rung 1: Size $100 (1X), stop move 0.40%, loss at stop $0.40, margin at 10x/20x $10/$5.
  - Rung 3: Size $600 (6X), stop move 1.20%, loss at stop $4.00, margin at 10x/20x $60/$30.
  - Rung 5: Size $2,400 (24X), stop move 2.01%, loss at stop $18.38, margin at 10x/20x $240/$120.
  - Rung 7: Size $9,600 (96X), stop move 2.81%, loss at stop $75.67 (reported as $76 in Section 6), margin at 10x/20x $960/$480.
- Progression adds sequence: `[100, 200, 300, 600, 1200, 2400, 4800]`. Rung 8 would add $9,600 to reach $19,200, which exceeds `MAX_ACCOUNT_NOTIONAL_USD = 10000` (`risk_guard.py:22`), justifying the hard cap of 7 rungs.
- Average entry at rung 7 is 102,006 vs stop 102,810; break-even requires a price rebound of 0.78% (`back_to_avg_needs = -0.78%`).

### 2. US Open Distributions (`stats_run.json`)
- Dataset window: 2022-01-01 to 2026-09-26, 1235 weekdays (`stats_run.json:all.n`).
- US 4h range p25/p50/p75/p90: `1.45 / 2.06 / 2.98 / 4.25 %` matches `[1.446, 2.055, 2.975, 4.254]`.
- Winter rows median: `2.37 %` matches `stats_run.json:std.us4h_range_pct_p25_p50_p75_p90[1]` (`2.374`).
- Max move from open in 4h: `0.79 %` up (`0.792`), `0.89 %` down (`0.893`); both $\ge 0.5\%$ on `40 %` of days (`0.402`).
- First 30 min range median: `0.87 %` (`0.872`); share of 4h range: `44 %` (`0.441`).
- Pre-60 min range median: `0.74 %` (`0.741`); pre-open drift matches US 4h direction: `49.8 %` (`0.498`).
- Days moving $\ge 2\%$ one way: `35 %` (`0.353`).

### 3. Clock & Calendar Facts
- US cash open: 09:30 New York (`SOURCED`).
- Transition dates: EDT open 13:30Z until Fri 2026-10-30; DST ends Sun 2026-11-01; EST open 14:30Z from Mon 2026-11-02; spring DST return 13:30Z on 2027-03-15 (`SOURCED`).
- Data release slot: 08:30 ET = 13:30Z (`SOURCED`).
- India cash open: 20:00 IST from Monday (was 19:00 IST) (`SOURCED`).

### 4. P5 Hedge Leg Specifications (`P5_BRIEF.md` and `cotrade.py`)
- P1 baseline: commit `0711c65f5`, 33 tests.
- Step size: `AMOUNT_STEP_USD = 10` (`cotrade.py:27`).
- Loss cap: `MAX_LOSS_AT_STOP_USD = 500.0` (`cotrade.py:28`).
- Floor rounding rule test case: parent 70 at 50% gives 35 -> floored to 30 USD (`cotrade.py:round_down_to_step`).
- Net view arithmetic: +30 and -10 USD yields net +20 USD.

---

## 3. Primary Audit File

Detailed itemized table available at:
`MyTradingSys/research/gemini_audits_2026-11-02/cotrade_blind_read.md`
