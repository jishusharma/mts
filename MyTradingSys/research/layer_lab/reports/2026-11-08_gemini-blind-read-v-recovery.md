FOUND=7 DIFF=0 NOT_IN_DATA=0 (MATCH=7)

# Gemini Blind Read Report: `v_recovery_low_sweep_2026-11-04/RESULT.md`

- **Card**: `gemini-blind-read-v-recovery-low-sweep-1108`
- **Date**: 2026-11-08 UTC
- **Reader**: Gemini (independent blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/RESULT.md`
- **Source Files**:
  - `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md`
  - `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/counts.json`

## Item-by-Item Reconciliation Table

| Item | Target Quote (`RESULT.md`) | Benchmark Source (`counts.json` / `PRE_REG.md`) | Label | Status | Notes |
|---|---|---|---|---|---|
| Headline: 5-day-low sweep window | `BTC 5-day-low sweep + 50% win-back` (`RESULT.md:1`) | `120 complete 1h bars` = 5 days (`120 / 24 = 5`) (`PRE_REG.md:9,22`) | OURS | MATCH | 120 1h bars corresponds exactly to 5 days. |
| Headline: Gate result | `(no DEV run, power-gate BLOCK)` (`RESULT.md:1`) | `All BLOCK (exit 1). Consequence: no --pass dev` (`PRE_REG.md:23-24`) | SOURCED | MATCH | Matches preregistration outcome and resolution rule. |
| Regime mix status | `Regime mix: NOT_IN_DATA (descriptive study, no regime spec frozen)` (`RESULT.md:2`) | `Regime mix: NOT_IN_DATA (unchanged)` (`PRE_REG.md:10,24`) | SOURCED | MATCH | Direct verbatim alignment with PRE_REG. |
| Verdict wording | `VERDICT: INCONCLUSIVE (underpowered).` (`RESULT.md:3`) | `Verdict INCONCLUSIVE (underpowered).` (`PRE_REG.md:24`) | SOURCED | MATCH | Verdict wording matches frozen resolution in PRE_REG line 24. |
| Event count | `DEV counts only: 435 events` (`RESULT.md:3`) | `"events": 435` (`counts.json:2`) & `435 events` (`PRE_REG.md:22`) | SOURCED | MATCH | Exact integer match. |
| Event days (cluster count) | `195 event-days` (`RESULT.md:3`) | `"event_days": 195` (`counts.json:3`) & `195 distinct UTC days` (`PRE_REG.md:22`) | SOURCED | MATCH | Exact integer match. |
| Horizon gate exit status | `prereg_gate exit 1 at 4h/24h/72h.` (`RESULT.md:3`) | `All BLOCK (exit 1)` for 4h, 24h, 72h (`PRE_REG.md:23`) | SOURCED | MATCH | Recomputed via `prereg_gate.py`: all 3 return exit code 1. |

## Verdict and Observations

- **Reconciliation Verdict**: `MATCH` (7 checked items: 7 MATCH, 0 DIFF, 0 NOT_IN_DATA).
- All numbers cited in `RESULT.md` reconcile against `counts.json` and `PRE_REG.md`.
- Forward return and power gating logic strictly matches the preregistration rules: DEV forward returns were never inspected or computed, VAL was never opened, and HOLDOUT was never accessed.
