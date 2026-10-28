# B154 STRATIFIED VERDICTS - by UTC session and by regime

Task: 20261009-181323-b154-stratify-existing-verdicts-by-sessi
Run: MTS-2026-10-10 (DSA), worktree mts-dsa
Reads only. No existing result edited.

## Finding

No result on disk carries per-event data (a timestamp column plus a net R column).
Every result is aggregate: it stores n, mean net R and t per cell, never the rows.
A session x regime stratification cannot be computed from these files; it needs the
event rows, which the producing scripts do not write.

Scan: 23 CSV/JSONL files under MyTradingSys/research and MyTradingSys/backtest were
opened and their header checked for a timestamp column and a net-R column. Zero passed.
The single file whose header contains both words (fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv,
columns run_id,date,variant,n_trades,mean_r_net,sharpe_per_trade) is a trial registry: one row
per run, not per trade.

## Table per source result

| Source | Per-event file | What it holds | Stratifiable |
|---|---|---|---|
| rsi_divergence_mtf_2026-10-09 | none | n, net mean, t per cell per timeframe | no |
| t087_session_levels_2026-10-09 | none | n, target/stop percent, net mean, t per cell | no |
| t090_7h_2026-10-09 | none | n, net mean, t per anchor shift | no |
| screenshot_context_2026-10-10 | none | narrative | no |
| fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv | none | one row per run | no |
| candle_patterns_2026-10-04/TRIAL_REGISTRY.csv | none | one row per run | no |
| volume_2026-10-09/TRIAL_REGISTRY.csv | none | one row per run | no |
| monitor_20260915/*.csv (9 files) | none | runtime counters, not trades | no |
| core_readiness_2026-09-27/harness/verdict_golden_baseline.csv | none | verdict rows, no PnL | no |
| W3_KAPPA_*.csv (2 files) | none | id, verdict | no |
| htf_context/*.jsonl (5 files) | none | context fields, no PnL | no |

## Count

Results examined: 11 directories/groups (23 CSV/JSONL files).
Results with a per-event file: 0.
Results with no per-event file: 11.

## Consequence and next step

B154 cannot be answered from existing files. To stratify, the producing scripts need an
events dump: one row per event with at least (timestamp_utc, net_r, side) plus the
session (Asia 00-08, EU 08-13, US 13-21, late 21-24 UTC) and a 1d EMA50 slope regime.
Recommended shape: add an --events <path.csv> flag to backtest/layers/rsi/run_divergence_mtf.py
and the T087 probe, run once, then this task is re-posted against those CSVs.