# Provenance: levels E1 S2 K5 X0_2R raw DEV fill ledger

Status: REPRODUCED. 772 ideas = 255 filled + 517 unfilled (explicit `filled=N`, `exit_reason=NO_FILL`), matching REVIEW_FABLE_2026-10-25.md:19.

- Source sha: `da096725e880974683bdd6cca6b086d64c61e7fd` (2026-10-21 "lc-ladder-dev"; last commit touching ladder.py, ladder_run.py, ladder_ideas_dev.csv; current defaults unused). Note: the 2026-10-25 sim_desk change (slippage box, 0.02 %) is NOT applied: zero slippage.
- Command: `python MyTradingSys/research/design_cards_2026-10-26/levels_raw_ledger/export_ledger.py` (klines F:/MTS/data/tom_raw/klines, 1m BTCUSDT).
- Settings (frozen_rule.json): E1, S2 (limit at L2), K5, X0_2R; fees MAIN (maker entry/target 0.0002, taker stop/time 0.0005); zero slippage; DEV only, touch_t in [2022-04-01, 2024-07-01); idea geometry (L1, L2, T1, atr1h) read from ladder_ideas_dev.csv, each idea replayed with `ladder.simulate`.
- Ledger columns: id, side, entry_t, entry, exit_t, exit (ms UTC, prices), qty (planned size = 1), fee_in/fee_out (USD per qty), R_dist (planned entry-to-stop price distance), filled, src_sha; extras: exit_reason, gross_R, fee_R, net_R, day, touch_t, L1, L2, stop, target.
- ledger.csv sha256: `2f72374b31b7f78bb6a31f96fa8fa0e30643a4e0d147fa32f34a38a3e6503915`.

## Reconcile (`python reconcile.py`)
net = gross - fees recomputed from prices; mean gross_R +0.217447, fee_R +0.336886, net_R -0.119439, win 40.78 % over 255 filled (conditional on filled; matches the review's +0.22 / +0.337 / -0.1194 / 40.8 %, so the earlier rescaled values are now confirmed from raw rows). Three hand rows (OURS fixtures) pass; a stub ledger fails.
Unexplained differences: none. Three rows (L0194, L0446, L0749) differ from the stored 3-decimal net by exactly the rounding boundary (0.0005) only.
Caveat: touch ideas come from the committed ideas CSV, not re-derived from raw levels; the replay reproduced all 255/517 fill statuses.
