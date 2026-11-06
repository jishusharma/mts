# Blind recount (Haiku slot, 2026-11-06): WT 30m divergence short and cycle frequency
Built from SPEC.md Cards 1 and 3 text only (no scratch script opened). BTCUSDT spot, closed bars, DEV only 2022-01-01..2024-06-30 (`backtest/splits.py` DEV_START/DEV_END), WT via `layers/wavetrend/wavetrend.py` (30-day lead-in for warm-up, events counted inside DEV). 5m built from spot 1m (only full 5-bar buckets). MATCH = within 15 % of the candidate; else DIFF.
Command: `python MyTradingSys/research/wt_bible_studies_2026-11-04/recount_haiku_1104.py` (script beside this file; 15m-4h from `F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/<tf>/klines`, 5m from `raw_1m_2022/klines`).

## Card 1: 30m lower-high divergence short, DEV only
Rule as written (events deduplicated, 48 bars skipped after an event). Interpretations (DECISION, OURS): "earlier down-cross" = the latest one in the 96 bars before that meets wt1>=45 and >=10 above the confirming wt1; "wt1 went below 0" = min wt1 over earlier cross..confirming bar < 0; dedup counts from the last accepted event.
| n (DEV, deduplicated) | candidate | verdict |
|---|---|---|
| 132 | 1219 (2020-01..2026-11, overlapping, not deduplicated) | DIFF |
Why DIFF is expected, not a fault of either side: DEV is 2.5 y of the 6.8 y window (x0.37 => about 450 at equal density) and the candidate had no 48-bar dedup. Even so 132 is well under 450; the gap is not explained, so the candidate n is not confirmed by the written rule. Not a trading claim.

## Card 3: cycles per week and valid-dot share, DEV only
| TF | crosses | valid dots | % crosses valid | cycles | cycles/week | candidate | verdict |
|---|---|---|---|---|---|---|---|
| 5m | 40472 | 6376 | 15.8 | 1046 | 8.03 | 6.1 | DIFF |
| 15m | 13400 | 2048 | 15.3 | 335 | 2.57 | 2.1 | DIFF |
| 30m | 6723 | 1042 | 15.5 | 161 | 1.24 | 1.1 | MATCH |
| 1h | 3430 | 536 | 15.6 | 81 | 0.62 | 0.6 | MATCH |
| 4h | 827 | 132 | 16.0 | 21 | 0.16 | 0.1 | DIFF |
Valid-dot share 15.3-16.0 % on every TF vs candidate 13-15 %: DIFF (about 1 point above the range, same order). Cycle = valid bottom up-cross (prior-bar wt1 <= -53) to the last valid top down-cross (prior-bar wt1 >= 53) before the next valid bottom; cycles without a top are not counted. Weeks = DEV length / 7 d (130.4).
Median cycle length (bars): 5m 95, 15m 99, 30m 88, 1h 98, 4h 114.
Reading: 30m and 1h frequencies match (1.1 and 0.6 per week); 5m, 15m and 4h differ by 22-60 %. Differences may come from window (DEV vs 2020-26) and 5m source; not resolved.