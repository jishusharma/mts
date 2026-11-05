# Habib plan scoring — layer lab report

**BLOCKED — 0 eligible DEV plans; cannot compute the requested hit rate or Wilson CI.** All nine priced ledger calls are HOLDOUT and the preregistration remains an unapproved draft. No HOLDOUT or post-2024-07-01 market bars were read; no call was scored. The nine calls are listed below for operator unsealing.

## Checked and run

- Read `PRE_REG_HABIB_PLANS.md:3,15,64,103`, `plan_score.py`, `PLAN_LEDGER.csv:2-10`, `README.md:56`, and `test_plan_score.py`.
- Ledger: 9 priced calls; 0 DEV; 9 `NOT_SCORED_HOLDOUT_WINDOW` (`PLAN_LEDGER.csv:2-10`).
- Preregistration: draft and awaiting approval (`PRE_REG_HABIB_PLANS.md:3`); approval is the release for these nine calls (`:64`); if unapproved, no holdout candle is read (`:103`).
- No candle access or scoring command was appropriate with zero eligible DEV rows and the holdout gate still closed. Tests not run; no tests or scoring code changed.
- Wrote `RESULT_PLAN_HIT_RATE.md` and `sim_desk/results/habib-plan-hit-rate-1104.json`. Export accurately records `n=0`, null rates/CI, and 9 sealed IDs.

## Findings

| Severity | File:line | Finding | Evidence / disposition |
|---|---|---|---|
| HIGH | `PLAN_LEDGER.csv:2-10` | NOT_IN_DATA for DEV hit rate | All nine rows are tagged HOLDOUT; ledger has no DEV call. Rate and Wilson CI are undefined at n=0. |
| HIGH | `PRE_REG_HABIB_PLANS.md:3,64,103` | Holdout scoring is not authorized by the preregistration state | File says draft/awaiting approval and makes operator approval the release. Calls remain sealed. |
| LOW | `README.md:56` | Existing study status agrees | Prior result also states 0 scoreable DEV plans and no outcomes read. |

## Operator request: unseal these nine calls

`QRP-yKm-lCrA_zw-03`, `QRP-dYlk1gtY2Lk-01`, `QRP-tJnls-_oGXc-02`, `QRP-xnuGOjqzcqY-01`, `QRP-xnuGOjqzcqY-02`, `QRP-t5xiPuo3yuc-03`, `QRP-ZPFK3ZsLwoo-05`, `QRP-ZPFK3ZsLwoo-06`, `QRP-lRB4wMGa9tw-02`.

Operator action: approve/finalize the preregistration and explicitly unseal these calls for a one-time score, or provide at least 12 typed DEV plans dated before 2026-06-26. This unattended run does not mark the task done because its required score cannot be produced under the current data split and preregistration.

Follow-up cards created: none.
