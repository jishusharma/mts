# T093 - turn-of-candle 4-12 h order-imbalance test on klines, BTCUSDT 2022-2026

Status: CLOSED 2026-10-10 (result: NO REPLICATION). Severity: MED. Opened 2026-10-10.
Session: MTS-2026-10-10 unblock-trunk (APP-BLD). Origin: Control Room D08 answer (replace the live 1-minute turn_of_candle test with the
4-12 h imbalance test), NEXT_SESSION task 3a. The handoff called it "T085"; T085 in BUGS.md is the time-exit task, so this is T093.

## Spec
- Data: BTCUSDT 1m klines 2022-01-01..2026-09-26 (F:/MTS/data/tom_raw/klines). No aggTrades on disk: buy = taker_buy_volume, sell = volume - taker_buy_volume.
- Signal: at each quarter-hour open (1m bar at :00/:15/:30/:45 UTC) imbalance = (buy - sell) / (buy + sell) of that bar; zero = no trade.
- Trade: entry at that bar's close, exit at the close W minutes later, W = 240 / 480 / 720 (4h / 8h / 12h); direction = sign(imbalance).
- Costs: net = gross - 10 bp (taker 0.0005 x 2 legs, backtest/fees.py). Source of the idea: research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md (Kim and Hansen).
- Decision (as P4 corrected): PASS = gross sign stable across all years AND net CI95 (day-block bootstrap, seed 12345) lower bound > 0.
- Runs split by year, each under 300 s (3-4 s measured).

## Tests (derived from the spec, failing before the module existed)
MyTradingSys/research/loose_code/test_t093_toc_imbalance_klines.py: buy/sell derivation, hand-worked +100 bp long and short, zero imbalance skipped, missing exit dropped,
year boundary (opens in the year only, exit may be in the next January), loader layout/dedup, parts equal one run, fee 10 bp, no-edge is not a PASS. Gate step 3t.

## Receipt
2026-10-10: ran here (data on this host). NO REPLICATION at 4h/8h/12h, n about 166,000 per window, gross +0.5 bp vs 10 bp fee, net CI95 below zero, sign unstable by year.
Report: research/_archive/loose_2026-10/T093_TOC_IMBALANCE_KLINES_2026-10-10.md. P4 corrected reproduces unchanged after the shared-code refactor (summarize()).
# END
