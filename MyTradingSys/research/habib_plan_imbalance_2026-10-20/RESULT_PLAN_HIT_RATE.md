# Habib plan hit rate — 2026-11-04

**BLOCKED — DEV hit rate not measurable: 0 eligible DEV plans (n=0); all 9 priced calls remain sealed HOLDOUT.** No Wilson confidence interval is defined for n=0. No holdout rows or candles were read.

## What was checked

- `MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:3,15,64,103`: preregistration remains a draft; it states all nine priced BTC plans fall in HOLDOUT, DEV is empty for these calls, and operator approval releases the holdout read.
- `MyTradingSys/research/habib_plan_imbalance_2026-10-20/PLAN_LEDGER.csv:2-10`: nine rows, each `NOT_SCORED_HOLDOUT_WINDOW`; no DEV row exists.
- `MyTradingSys/research/habib_plan_imbalance_2026-10-20/README.md:56`: prior study result independently records 0 scoreable DEV plans and no outcomes read.
- Scorer reused/read: `plan_score.py`; no code or ledger changes. No market candles were accessed because no ledger call is in DEV.

## Findings

| Severity | Evidence | Finding | Proposed next step |
|---|---|---|---|
| HIGH | `PLAN_LEDGER.csv:2-10`; prereg `:3,64` | **NOT_IN_DATA (DEV):** none of the nine scored candidates is eligible for DEV. A plan hit rate and Wilson CI cannot be calculated from this ledger on DEV. | Operator: approve/finalize the preregistration and explicitly unseal the nine HOLDOUT calls below for a one-time score, or provide at least 12 typed plans dated before 2026-06-26. |
| MED | `PRE_REG_HABIB_PLANS.md:3,103` | **MATCH:** the preregistration's holdout gate is still active and approval is blank; scoring these rows now would violate it. | Keep all nine sealed pending operator action. |

## Calls awaiting operator unseal

`QRP-yKm-lCrA_zw-03`, `QRP-dYlk1gtY2Lk-01`, `QRP-tJnls-_oGXc-02`, `QRP-xnuGOjqzcqY-01`, `QRP-xnuGOjqzcqY-02`, `QRP-t5xiPuo3yuc-03`, `QRP-ZPFK3ZsLwoo-05`, `QRP-ZPFK3ZsLwoo-06`, `QRP-lRB4wMGa9tw-02`.

## Outputs

- `RESULT_PLAN_HIT_RATE.md`: this blocked result and operator request.
- `sim_desk/results/habib-plan-hit-rate-1104.json`: machine-readable blocked export (`n=0`, rate/CI null, nine holdout IDs sealed).
- Tests were not run; no scoring implementation was changed.
- No follow-up card was created. The task is **not marked done** because the requested outcome measurement is blocked by the preregistration gate and absence of DEV rows.
