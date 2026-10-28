# Lab Report: Re-check of GPT Habib Audit Findings (2026-10-28)

**Task**: `gem-habib-planscore-ledger`  
**Card Title**: `[GEMINI] Check GPT's two HIGH Habib findings: same-candle scoring and HOLDOUT overlap`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx-habib-imbalance/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/gpt_burn_2026-10-24/gx-habib-imbalance/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py` (lines 40–65)
- `MyTradingSys/research/imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv` (lines 1–5)
- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md` (lines 14–26)
- `MyTradingSys/research/gpt_burn_2026-10-24/gx-habib-imbalance/report.md`

*Constraint adherence*: Reproduction lines in `gx-habib-imbalance/report.md` were NOT inspected prior to independent count and verification.

---

## 1. Executive Summary

Both of GPT's HIGH audit findings regarding Habib plan scoring and the Qriptal exposure ledger have been independently verified and **CONFIRMED**:
1. **Same-Candle Plan Scoring (HIGH)**: [`score_plan`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py#L39-L65) evaluates the target scan starting from `t >= filled_at`, meaning the very candle that fills entry is also evaluated for target reach. On a candle with `high=110, low=100`, a long order with `entry=100` and `target=110` scores `"full"`. Because OHLC provides no sub-candle sequence, it cannot determine whether the high preceded the low, creating lookahead/intraday-ordering bias.
2. **Sealed Main HOLDOUT Overlap (HIGH)**: [`EXPOSURE_LEDGER.csv:2-3`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv#L2-L3) documents two backtest runs (`--k 2.0` and `--k 3.0`) whose check window spans `2025-09-01..2026-06-25`. Per canonical specification [`AUDIT_BRIEF.md:16`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md#L16), the sealed HOLDOUT period starts on `2025-07-01`. Both runs deeply penetrated the sealed HOLDOUT period (by nearly a full year), which invalidates them as clean out-of-sample evidence.

---

## 2. Independent Verification and Derivations

### Finding 1: Same-Candle Scoring Ambiguity in `plan_score.py`
- **Code Inspection**:
  In [`plan_score.py:48-64`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py#L48-L64):
  ```python
  filled_at = None
  for t, hi, lo in win:
      if t >= posted + FILL:
          break
      if lo <= entry <= hi:
          filled_at = t
          break
  if filled_at is None:
      return "miss"
  best = 0.0
  for t, hi, lo in win:
      if t < filled_at:
          continue
      reach = hi if sign == 1 else lo
      if (reach - target) * sign >= 0:
          return "full"
      best = max(best, (reach - entry) * sign)
  ```
- **Execution Test**:
  - Constructed synthetic candle: `(posted + 1h, high=110.0, low=100.0)`.
  - Direction: `'long'`, `entry=100.0`, `target=110.0`.
  - Result of `score_plan(candles, 'long', 100.0, 110.0, posted)`:
    - Output: **`"full"`**.
- **Mechanics**:
  In the target loop, `if t < filled_at: continue` permits `t == filled_at`. On that candle, `reach = hi = 110.0`. `(110.0 - 110.0) * 1 == 0 >= 0` evaluates to True and exits immediately with `"full"`. If in reality the market traded 110 first and then 100, the target occurred prior to fill. The scorer credits full profit without intraday sequence evidence.

### Finding 2: Sealed HOLDOUT Overlap in `EXPOSURE_LEDGER.csv`
- **Canonical Boundary**:
  [`AUDIT_BRIEF.md:16`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md#L16) defines:
  - DEV: before `2024-07-01`
  - VALIDATION: `2024-07-01..2025-06-30` (read once per pre-registered hypothesis)
  - HOLDOUT: `2025-07-01..2026-09-30` (sealed; rule A7: only operator opens it)
- **Ledger Records**:
  In [`EXPOSURE_LEDGER.csv`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv#L2-L3):
  - Row 2: `imbalance_qriptal_2026-10-16/imb.py backtest --k 2.0`
    Window read: `"design 2022-01-01..2025-08-31, check 2025-09-01..2026-06-25"`
    Split column: `DEV+VALIDATION+HOLDOUT (main split; declared as Qriptal/Tom-protocol DEV at run time)`
  - Row 3: `imbalance_qriptal_2026-10-16/imb.py backtest --k 3.0`
    Window read: `"design 2022-01-01..2025-08-31, check 2025-09-01..2026-06-25"`
    Split column: `DEV+VALIDATION+HOLDOUT (main split; declared as Qriptal/Tom-protocol DEV at run time)`
- **Count & Overlap**:
  - The check window (`2025-09-01..2026-06-25`) extends **360 days** beyond the start of the sealed HOLDOUT (`2025-07-01`).
  - Exactly **2 backtest runs** published returns over this period.
  - While lines 4–5 (label-check and candle-parity) also read HOLDOUT timestamps, their returns were not evaluated. Rows 2 and 3 explicitly evaluated returns, thus exposing the sealed HOLDOUT twice.

---

## 3. Findings

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| HIGH | [`plan_score.py:48-64`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py#L48-L64) | `score_plan` scores target hits on the entry candle (`t == filled_at`), crediting `"full"` without evidence of intraday sequencing. | Long entry 100 / target 110 on candle high 110 low 100 returns `"full"`. | Require target candle `t > filled_at`, or resolve same-candle simultaneous touch as ambiguous/unscored unless 1-minute tick/sequence data confirms fill preceded target. |
| HIGH | [`EXPOSURE_LEDGER.csv:2-3`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-habib-planscore-ledger/MyTradingSys/research/imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv#L2-L3) | Backtest runs k=2.0 and k=3.0 published returns evaluated through `2026-06-25`, penetrating the sealed `2025-07-01..2026-09-30` HOLDOUT window. | `EXPOSURE_LEDGER.csv` rows 2–3 record check window `2025-09-01..2026-06-25` vs `AUDIT_BRIEF.md:16` HOLDOUT start `2025-07-01`. | Treat the `2025-09-01..2026-06-25` interval as burned/exposed; enforce date guards in backtest scripts rejecting dates past `2025-07-01` unless explicitly running authorized holdout. |

---

## 4. Verdict

**Verdict: SOUND.**  
Both HIGH findings reported by GPT in `gx-habib-imbalance/report.md` are completely confirmed by independent derivation and repository record verification:
1. `plan_score.py:48-64` produces `"full"` on same-candle entry/target touch.
2. `EXPOSURE_LEDGER.csv:2-3` documents two return-generating runs penetrating the repository's sealed HOLDOUT window.
