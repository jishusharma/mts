# RERUN_FUNDING - RSI and CryptoCred DEV rows with real funding (card bt-engine-wire-real-funding-rsi-cc-rerun)

Scope: DEV (IS 70%) only. VALIDATION and HOLDOUT (OOS) were not scored (`--dev-only` for RSI, `dev_only=True` for CC). No stop, target or threshold changed. Funding = bt_data.load_funding(F:/MTS/Dumps/backtest/raw), 7395 records to 2026-09-30. Funding deltas below are SOURCED (funding files through bt_engine, window t_in < s <= t_out, FORMULAS 13).

## What was wired
- RSI: `run_rsi_backtest.py` had `funding=[]` hard-coded. `trades_from_events`, `grid_search_and_oos` and `run_family` now take `funding`; `main` loads it (`--no-funding` = old model, `--dev-only` = no OOS scoring). 3 new tests fail on the old code (3 errors) and pass after.
- CC: funding was already wired (load_data -> run_setup -> build_trades), so no pass-through change was needed. Found instead: a full run now crashes (B103 span check) on trades after the funding end (2026-09-30). Added `run_setup(dev_only=True)`: DEV signals only, 1m bars cut at split + max_bars. Its test fails on the old code and passes after.

## RSI DEV rows (IS, bracket 1% / 2%, maker 0 / taker 5 bps)
Published rows: F:/MTS/Dumps/backtest/runs/rsi_*/summary.json (older data, fewer bars). "Rerun no-funding" = same code and data as the funded run with `--no-funding`, which isolates the funding effect. No published row exists for rsi_ma_events 15m or malkan_mtf.

| family / tf | published IS (chosen, n, mean net) | rerun no-funding (chosen, n, mean net) | rerun with funding (chosen, n, mean net) | funding delta on same params (pp) | same chosen params? |
|---|---|---|---|---|---|
| malkan_40_60 1h | {"period": 21, "tolerance": 2.0, "lookback": 40}, 109, 0.1129% | {"period": 21, "tolerance": 2.0, "lookback": 40}, 110, 0.1019% | {"period": 21, "tolerance": 2.0, "lookback": 40}, 110, 0.1007% | -0.0011 | True |
| malkan_40_60 4h | {"period": 10, "tolerance": 1.0, "lookback": 10}, 26, 0.4251% | {"period": 10, "tolerance": 1.0, "lookback": 10}, 26, 0.4251% | {"period": 10, "tolerance": 1.0, "lookback": 10}, 26, 0.4333% | +0.0082 | True |
| malkan_40_60 1d | {"period": 10, "tolerance": 3.0, "lookback": 20}, 13, 0.0732% | {"period": 10, "tolerance": 3.0, "lookback": 20}, 13, 0.0732% | {"period": 10, "tolerance": 3.0, "lookback": 20}, 13, 0.0866% | +0.0135 | True |
| rsi_ma_events 15m | "n/a", None, - | {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}, 2095, -0.0715% | {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}, 2095, -0.0716% | -0.0001 | True |
| rsi_ma_events 1h | {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}, 897, -0.0118% | {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}, 907, -0.0103% | {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}, 907, -0.0084% | +0.0019 | True |
| rsi_ma_events 4h | {"period": 14, "ma_length": 9, "tolerance": 0.5, "mode": "touch"}, 185, 0.0871% | {"period": 14, "ma_length": 9, "tolerance": 0.5, "mode": "touch"}, 187, 0.0744% | {"period": 14, "ma_length": 9, "tolerance": 0.5, "mode": "touch"}, 187, 0.0721% | -0.0023 | True |
| malkan_mtf 1d | "n/a", None, - | {"period": 14, "tolerance": 3.0, "lookback": 20, "htf_lookback": 3}, 7, -0.6639% | {"period": 14, "tolerance": 3.0, "lookback": 20, "htf_lookback": 3}, 7, -0.6786% | -0.0147 | True |

Read: funding moves every RSI DEV net mean by at most 0.0147 pp (7 rows: 4 negative, 3 positive; shorts receive positive funding). Chosen params unchanged in all 7 rows. Published-vs-rerun differences (e.g. malkan 1h 0.1129% -> 0.1019%) are NOT funding: they come from the longer data span (1 to 10 more IS trades). Every RSI DEV net row moves by funding, but by under 0.015 pp, and none changes sign.

## CryptoCred DEV rows (1h, defaults, IS)
Published file: F:/MTS/data/cc_setups_2026-10-06/cc_setups_result.json (funding included, old window). "Rerun same span" uses the first 41520 1h bars (the published span) with current code; net minus no-funding on the same trades is the funding effect. Units: mean net % per trade.

| setup / fees | published IS n, mean net % (old code, funding old window) | rerun same span: n, mean net %, no-funding % | delta vs published (pp) | rerun full current data: n, net %, no-fund % |
|---|---|---|---|---|
| setup1_sr_flip / all_taker | 1093, 0.00940 | 1056, -0.10720, -0.10720 | -0.11660 | 1070, -0.10701, -0.10701 |
| setup1_sr_flip / maker_entry | 1093, 0.10126 | 1056, -0.03864, -0.03864 | -0.13990 | 1070, -0.03841, -0.03841 |
| setup2_fib_pullback / all_taker | 372, 0.08151 | 984, -0.08543, -0.08535 | -0.16694 | 998, -0.08556, -0.08547 |
| setup2_fib_pullback / maker_entry | 372, 0.16628 | 984, -0.01821, -0.01812 | -0.18449 | 998, -0.01832, -0.01824 |
| setup3_failed_msb_reversal / all_taker | 119, 0.15952 | 119, 0.15967, 0.16572 | +0.00015 | 119, 0.15967, 0.16572 |
| setup3_failed_msb_reversal / maker_entry | 119, 0.22007 | 119, 0.22022, 0.22627 | +0.00015 | 119, 0.22022, 0.22627 |

Read:
- Funding effect (net minus no-funding, same trades, SOURCED, IS mean): setup1 0.00000 pp, setup2 -0.00008 pp, setup3 -0.00605 pp. Negligible (short holds).
- Published vs rerun differ far more for setup1 (all_taker 0.0094% -> -0.1072%; maker_entry 0.1013% -> -0.0386%) and setup2 (n 372 -> 984; 0.0815% -> -0.0854%). This is NOT funding (net equals no-funding): other code changes in the CC signal/limit-fill path since 2026-10-06 changed the trade counts. Flagged, not investigated (outside this card). All four published setup1 and setup2 DEV net rows move (sign flips); the two setup3 rows are unchanged (+0.00015 pp).
- Do not quote the 2026-10-06 CC net rows for setup1 or setup2.

## Limitations and DECISIONs
- DECISION (OURS): RSI runs bt_engine on tf bars, and the engine's exit instant is the exit bar's open + 60000 ms (a 1m bar). For 1h/4h/1d bars, settlements in the last tf-1m of the exit bar are not charged, so RSI funding is slightly understated. bt_engine.py is outside this card; flagged as a follow-up (pass the bar width to simulate_trade).
- DECISION (OURS): CC dev_only keeps 1m bars to split + max_bars so DEV trades near the split can close; no OOS trade is simulated or read.
- DECISION (OURS): VALIDATION/HOLDOUT rows were not recomputed, so their published values stay unreviewed for funding.
- The CC test `test_run_setup_passes_funding_through` passes on the old code by design (wiring pre-existed).
