# T081 - Backtest D: walk-forward tuning of stop_buffer_atr

Status: OPEN (filed 2026-10-09). Severity HIGH.
Source: BUGS.md row T081; Road to profitability (control room); session MTS-2026-10-09-APP-SUP-control-room (X-BTD).

## Verbatim ask

Backtest D: walk-forward tuning of stop_buffer_atr (stop = structure +/- k x ATR) for Tom and every tight-stop layer, fee_R per cell, label BT-TUNED (fix path for B146, F-BT-01, F-BT-22).

## State

2026-10-09 PART 1 (Tom only): NO. Walk-forward over stop = structure +/- k x ATR(14), k grid 0..2, 6 folds, dev only: out-of-fold net R negative in all 8 runs (best -0.200 [-0.277, -0.120], zone-tf ATR, Deribit fees; k=0 same blocks -6.595); picked k=2 in 23 of 24 folds (grid edge, not widened). Report research/fast_track_2026-09-27/T081_STOP_BUFFER_WF_2026-10-09.md. Open: the other tight-stop layers (CryptoCred stop_buffer_pct etc.) - B143 forbids gridding NO-SOURCE values without a ruling.

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN row has a matching items/ file. State copied from the BUGS.md row.
