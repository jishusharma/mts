# Probability table common layer: first frozen run

- Card: `prob-layer-common-table` (CODEX, M, p1).
- Command: `python MyTradingSys/research/layer_lab/prob_table_1103/prob_table_run.py`.
- Code and tests: `MyTradingSys/research/layer_lab/prob_table_1103/prob_table_run.py:1`, `test_prob_table_run.py:1`.
- Outputs: `MyTradingSys/research/layer_lab/prob_table_1103/RESULT.md`, `table.csv`, `cell_quantiles.csv`.

## Design and independent checks

Implemented the frozen design: closed BTCUSDT bars at 1h/4h, horizons 4/24, SMA200 above/below regime, BB(20,2) four zones and Wilder RSI14 zones. Regime-only baseline is compared with regime+BB+RSI. Fit uses 2022-01-01 through 2024-06-30 and evaluation uses 2020-01-01 through 2021-12-31, as explicitly frozen by the card. Training cells under n=30 fall back to the regime parent. Evaluation includes paired weekly block-bootstrap 95% intervals, fee-net expected-direction returns and MFE/MAE quantiles by cell.

All choices not determined in `MyTradingSys/backtest/layers/FORMULAS.md` are marked OURS in `RESULT.md` and the code: binary Laplace smoothing, fallback semantics, arithmetic EV and zero-trade convention, fee-net direction rule, 1,000 weekly resamples, and seed 1103. Fees use canonical Deribit all-taker: two `DERIBIT_TAKER=0.0005` legs (10 bp round trip before slippage), from `MyTradingSys/backtest/fees.py:32` and `:43`. Formula references: Wilder RSI seed and smoothing, `FORMULAS.md` section 1; Bollinger population SD, section 22. RSI hand values were checked against the canonical formula result in `MyTradingSys/backtest/layers/rsi/TEST_PLAN.md` case C1.

Fail-first tests cover appended-future-bar invariance, hand-derived two-observation log-loss, the n=29/n=30 shrink boundary, cutoff refusal, excluded-month sentinels, missing-minute refusal, and incomplete-candle refusal. EXPECT for log-loss is `(-ln(.75)-ln(.25))/2 = 0.836988...`; the p-up inputs are [.75,.75] for labels [up,down]. The test suite passes 7/7.

Data availability was checked before the run: 30 monthly fit files (2022-01 through 2024-06) in `F:/MTS/data/tom_raw/klines`, and 24 evaluation files (2020-01 through 2021-12) in `F:/MTS/data/dev_ext_2019_2021/klines`. Loader applies half-open UTC windows; bars at or after 2024-07-01 are excluded. It did not load VALIDATION or HOLDOUT.

Loader review correction: the first version selected the exclusive end month by `month > end_month`, which could open the next month's CSV and discard its rows afterward. `tom_raw` contains `BTCUSDT-1m-2024-07.csv`; the corrected overlap test skips it before `read_csv`. Sentinel tests prove both July 2024 (fit end) and January 2022 (evaluation end) files are not opened. The full study was rerun after this correction and the counts and verdicts above are unchanged. Source timestamp inventory has zero missing one-minute intervals in either window. Aggregation rejects missing or duplicate source minutes and refuses a candle unless all 60 (1h) or 240 (4h) one-minute rows are present; observed aggregates were 21,888 / 5,472 fit bars and 17,544 / 4,386 evaluation bars respectively.

## Evidence verdict

All four TF/horizon combinations are **KILL** under the frozen kill line. 1h/4h and 4/24 bar details, test counts, log-loss, EV, and CIs are in `RESULT.md` and `table.csv`. No cell combination has both a wholly better log-loss CI and positive fee-net test EV whose improvement CI clears zero. The 4h/4-bar model is significantly worse on log-loss (difference +0.003789, 95% CI [+0.000243,+0.007570]). The other three log-loss intervals overlap zero; all four EV-difference intervals overlap zero. No KEEP evidence.

## Limits

This is one BTCUSDT data source and a reverse-time evaluation split specifically required by the card. Returns are close-to-close with canonical fees and no slippage, funding, spread, or execution model. The chosen EV convention and binary UP label are OURS. The result is research evidence only, not trade authorization. VALIDATION/HOLDOUT were not read.

## Closure gate

`python scripts/dev/tasks.py done prob-layer-common-table --result "4/4 KILL; RESULT.md and table.csv"` was refused: `trial-ledger count 1 != runs.jsonl count 0 for prob-layer-common-table`. `LAYER_LAB.md` documents the interactive Codex app as following the same rules; it does not define an interactive receipt. The only producer found for the required model/effort/session/token row is `codex_run.py`. No fabricated run row or quota-consuming duplicate was created. The card remains READY for operator/lab-runner reconciliation.

CI was refreshed with `python scripts/dev/health_audit.py`: the newest finished fast-track run is SUCCESS. Earlier failures at 09:42–09:45Z were Step 3xt. No ship was attempted after this refresh because official task closure still fails the run-receipt guard.
