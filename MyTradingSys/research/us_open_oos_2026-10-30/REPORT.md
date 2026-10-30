# US-open findings: out-of-sample replication on 2020-01..2021-12 (ask P0-34, T054 N1)

Method: `session_sweeps/session_open_study.py` re-run unchanged via `run_oos.py` (text-substitutes only data dir, date range, holiday list, output path). Data: Binance USD-M BTCUSDT 1m, `F:/MTS/Dumps/backtest/raw_1m_2019/klines` (24 monthly files, 1,052,640 bars, no gaps). Descriptive study, no costs, no trade rule (same status as the original). 505 valid days (original: 1,178 days, 2022-01..2026-09). Results: `results_oos_2020_2021.json`.
Limits: (1) perp 1m klines are public only from 2019-12-31, so 2019-09..12 does not exist for this series; window is 2020-01..2021-12 (the DEV_EXT segment, D3). (2) 2020-21 NYSE closures were typed from memory (OURS, verify); early closes not removed. (3) DEV_EXT is a development segment, so "out-of-sample" here means earlier-regime, not a sealed holdout.

## 1. Direction: first 10/15/30 min do not predict the rest of the US session - REPLICATES
P(sign(c[E]-c[O+k]) == sign(c[O+k]-o[O])), Wilson 95% CI:

| k | 2022-26 (orig) | 2020-21 (OOS) |
|---|---|---|
| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |
| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |
| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |

All CIs contain 0.5. OOS value sits inside the placebo spread of the 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501), i.e. no US-open-specific persistence. By year: 2020 0.502, 2021 0.468 (both include 0.5). Same null in both samples.

## 2. US-open volume / |ret| peak - PARTLY replicates (weaker, not the top bucket)
Top 15-min UTC buckets by |return| (x = multiple of mean), vol_x in brackets:

| regime | 2022-26 (orig) | 2020-21 (OOS) |
|---|---|---|
| US DST | 13:30 1.92x [2.55], 14:00 1.77x, 13:45 1.72x | 00:00 1.55x [1.52], **13:30 1.36x [1.63]**, 12:00 1.35x |
| US std | 14:30 2.03x [2.81], 14:45 1.81x, 15:15 1.76x | 00:00 1.51x [1.44], **14:30 1.39x [1.49]**, 16:00 1.35x [1.89] |

- Replicates: the US-open bucket is the top-2 |ret| bucket in both regimes and shifts 13:30 -> 14:30 with US DST (so it tracks the cash open, not a UTC clock time).
- Does not replicate: magnitude (1.36-1.39x vs 1.92-2.03x; volume 1.5-1.6x vs 2.5-2.8x) and rank: 00:00 UTC is the top |ret| bucket in 2020-21 (it is not in the top 6 in the original). In std-time days the highest volume bucket is 16:00 UTC (1.89x), not the open.
- Reading: the US-open peak existed in 2020-21 but was a fraction of its 2022-26 size and not dominant; the original "US open is the peak" claim holds only as 'one of the top buckets' for 2020-21.

## Other tests (T3/T4/T5) - reported for completeness, not part of this card's question
T3 base P(US up)=0.549 [0.505,0.591]; no class separates from base with n>=50 (H_sweep_back 0.493 n=75, none 0.600 n=75). T4 classes n<=34 so uninformative (H_sweep_back 0.647 n=34, CI [0.48,0.79]). T5 small IB trend 0.205, mid 0.265, large 0.253 (no monotone link). See JSON; no parameter was selected.
