# B141 - htf_context_live balance fields always null

Opened 2026-10-07. Status OPEN. Severity MED. Session MTS-2026-10-07-1000Z-APP-ANA-whea-htf.

## Problem
research/htf_context rows: bal_4h and bal_1d null in all 13 stored rows; failed_breakout null since R4-T2 (4 legacy false rows 2026-10-02).

## Cause
Not a runtime error (err/out logs empty). balance() (backtest/layers/fabio/v3/signals.py:183-205) needs R <= 0.8*sqrt(N)*ATR_N and
|c - poc| <= 0.25*R; both constants NS-fixed (FABIO_PROVENANCE_AUDIT_2026-10-01.md:59). On 6 days of live 1m klines: N=240 1 of 281 windows
balanced, N=1440 0 of 241 (median R/(sqrt(N)*ATR) 1.38 and 1.54 against the 0.8 threshold).

## Path
Operator 2026-10-07: replace-via-backtest. Pre-registration BOUND 2026-10-07 (28 declared cells, holdout read once;
operator delegated the sweep ranges in session): MyTradingSys/research/PRE_REG_HTF_REPLACE_2026-10-07.md. Next: run it. Unblocks
BUILD_PIPELINE 2.4 (R4-D) and 3.1 (R5) once run.

## Validation
validated 2026-10-07 on JIS-NUC (session MTS-2026-10-07-1000Z-APP-ANA-whea-htf, follow-up): balance() re-run on live klines ending 2026-10-07T11:15Z: N=240 6 of 280 (2.1%), N=1440 0 of 240. Cause confirmed.
