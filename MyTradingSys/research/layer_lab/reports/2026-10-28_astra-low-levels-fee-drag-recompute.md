# Astra-low levels fee-drag recomputation — 2026-10-28

## Result

**MATCH at the Fable review's displayed precision for all five requested quantities.** Independent raw-row means are gross +0.2174473159477666989 R, fees +0.3368860406537607552 R/trade, net -0.1194387247059940563 R, and 104/255 = 40.7843137254901961% net-positive; there are 255 explicit fills and 517 explicit no-fills.

## Method and inputs

Read `MyTradingSys/backtest/layers/FORMULAS.md:468-470,479-483` and `MyTradingSys/research/design_cards_2026-10-26/levels_raw_ledger/provenance.md:3-8`. Recomputed filled rows only, with `gross_R = side * (exit - entry) / R_dist`, `fee_R = (fee_in + fee_out) / R_dist` (ledger fee legs are USD per unit and qty is 1), and `net_R = gross_R - fee_R`. Win rate is strictly `net_R > 0`. This is the frozen E1/S2/K5/X0_2R DEV run, source revision `da096725e880974683bdd6cca6b086d64c61e7fd`, zero slippage, timestamp range [2022-04-01, 2024-07-01). No VALIDATION/HOLDOUT data.

Before loading the real ledger, the independent Decimal calculator passed three handwritten exact cases: long win (gross 1, fee 0.0202, net 0.9798), short loss (gross -1, fee 0.0705, net -1.0705), and long timeout (gross 0.25, fee 0.050125, net 0.199875). It rejected invalid side/nonpositive risk in its calculation function. It used Python CSV, Decimal, and subprocess only to read the tracked Git blob hash; it did not import or execute the exporter, study, or `reconcile.py`.

Input Git blob SHA-256 for `levels_raw_ledger/ledger.csv`: `2f72374b31b7f78bb6a31f96fa8fa0e30643a4e0d147fa32f34a38a3e6503915`.

## Checks and comparison

- Ledger invariants: 772 rows = 255 `filled=Y` + 517 `filled=N`; every no-fill has `NO_FILL` and blank entry/exit; all rows identify source revision above. Filled rows have unit quantity, valid side, and positive risk.
- Each raw-row recomputation agrees with ledger `gross_R`, `fee_R`, and `net_R` within 1.21e-13 R (float serialization tolerance). Independently recomputed mean values: gross `0.2174473159477666988727880220706821552577`; fee `0.3368860406537607551948768035060470501438`; net `-0.1194387247059940563220887814353648948864`; positive net count `104`.
- Review values at `MyTradingSys/research/sim_desk/REVIEW_FABLE_2026-10-25.md`: 255 / 517 and -0.1194 R / 40.8% in section 1 line 19; +0.22 R in lines 9 and 19; +0.337 R fee in line 21. All five values round to those displayed values.
- Differences from displayed numbers before display rounding: gross -0.0025526840522333011272 R; fee -0.0001139593462392448051 R; net -0.0000387247059940563221 R; win rate -0.0156862745098039215686 percentage points. These are rounding differences, not gaps.
- Exit reasons: 102 X0, 150 STOP, 3 TIME. No target-hit rate was inferred.

## Limits

This independently recomputes arithmetic from the exported trade rows; it does not independently regenerate fills from raw candles. The ledger exporter used the frozen idea geometry and historical one-minute klines, as recorded in provenance. The prior audit had already read the Fable review during input discovery, so this is an independent calculation but not a blind review. No layer keep/drop/demote/park disposition or production change follows from this result.

Reproduction command: `python F:/MTS/astra_levels_recompute_independent.py` (scratch script outside the repository).
