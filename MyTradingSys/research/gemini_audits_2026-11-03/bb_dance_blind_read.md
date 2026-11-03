# FOUND: 85, NOT_IN_DATA: 2, DIFF: 0

# Blind Re-read of bb_dance_2026-10-30 RESULT.md: Every Quoted Number vs output.txt (and live_output.txt / study.py)

Audit of every quoted number (counts, percentages, sample sizes `n`, prices, `%b` ratios, bar intervals, timestamps, and dates) in:
- `MyTradingSys/research/bb_dance_2026-10-30/RESULT.md`

Cross-checked against:
- `MyTradingSys/research/bb_dance_2026-10-30/output.txt` (primary DEV archive output, `n = 11,051`)
- `MyTradingSys/research/bb_dance_2026-10-30/live_output.txt` (cited on `RESULT.md:40` for Section 3 spot 10-29 case)
- `MyTradingSys/research/bb_dance_2026-10-30/study.py` (cited on `RESULT.md:3` for study definitions)
- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/costs.csv` (round-trip cost benchmark on `RESULT.md:38`)

## Summary

- **Total Quoted Numbers Audited**: 87
- **FOUND**: 85 (46 in `output.txt` directly; 29 in `live_output.txt` cited on L40; 9 in `study.py` cited on L3; 1 in `T06/costs.csv`)
  *(Note: If evaluated strictly against `output.txt` alone without `live_output.txt` or `study.py`, the breakdown across the 87 rows is **FOUND: 46, NOT_IN_DATA: 41, DIFF: 0**).*
- **NOT_IN_DATA**: 2 (`15m` and `1h` on `RESULT.md:60`, which are proposed future timeframes in the `## Open` section and not evaluated in `output.txt` or `study.py`)
- **DIFF**: 0

---

## Audit Table (One Row per Quoted Number)

| Row | Line / Table | Quoted Number in `RESULT.md` | Context / Metric | Source File:Line | Value in Source (`output.txt` / Cited File) | vs `output.txt` Only | Status | Label |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | L1 (Title) | `2026-10-30` | Study date (`(2026-10-30)`) | `study.py:1` | `2026-10-30` (`"""Operator question 2026-10-30`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 2 | L3 (Intro) | `1m` | Archive bar interval (`BTCUSDT 1m archive`) | `study.py:5,24` | `1m` (`BTCUSDT 1m archive`, `BTCUSDT-1m-*.csv`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 3 | L3 (Intro) | `5m` | Aggregated bar interval (`built into 5m bars`) | `study.py:5,29-31` | `5m` (`5m bars`, `df.t // 300`, `b.n == 5`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 4 | L3 (Intro) | `2022-2025` | DEV window (`DEV 2022-2025 only`) | `study.py:4,24` | `DEV 2022-2025 only` (`'2026' not in f`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 5 | L3 (Intro) | `20:00Z` | Entry bar timestamp on 10-29 (`20:00Z close`) | `live_output.txt:13` | `20:00 c=80412 ... mid=80798` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 6 | L3 (Intro) | `10-29` | Spot case date (`on 10-29`) | `study.py:87` | `startTime=1793293200000` (10-29 17:00Z..22:40Z) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 7 | L5 (Sample) | `11,051` | Sample size (`11,051 shorts`) | `output.txt:1` | `shorts with a lower-band touch: 11051` | `FOUND` | **FOUND** | `OURS` |
| 8 | L5 (Sample) | `5m` | Close timeframe (`on a 5m close`) | `study.py:6` | `Entry: a 5m close below the mid` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 9 | L9 (Sec 1) | `5m` | Mid-cross timeframe (`any 5m close above the mid`) | `study.py:7` | `Trade alive until a 5m close above the mid` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 10 | L11 (Table 1 hdr) | `0.25` | Near-band threshold (`%b < 0.25`) | `output.txt:16` / `study.py:11,71` | `pb < 0.25` (`mean_near` / `size_near` in `output.txt:4`) | `FOUND` | **FOUND** | `OURS` |
| 11 | L11 (Table 1 hdr) | `0.25` | Away-from-band threshold (`%b >= 0.25`) | `output.txt:16` / `study.py:11,52` | `pb_ge_025` (`mean_far` / `size_far` in `output.txt:4`) | `FOUND` | **FOUND** | `OURS` |
| 12 | L13 (Table 1, k=1) | `1` | Bars since last touch `k` | `output.txt:6` | `k = 1` | `FOUND` | **FOUND** | `OURS` |
| 13 | L13 (Table 1, k=1) | `59%` | Near-band P(new low) at `k=1` | `output.txt:6` | `mean_near = 0.594` (59.4% rounds to 59%) | `FOUND` | **FOUND** | `OURS` |
| 14 | L13 (Table 1, k=1) | `6,360` | Near-band count `n` at `k=1` | `output.txt:6` | `size_near = 6360` | `FOUND` | **FOUND** | `OURS` |
| 15 | L13 (Table 1, k=1) | `32%` | Away-from-band P(new low) at `k=1` | `output.txt:6` | `mean_far = 0.319` (31.9% rounds to 32%) | `FOUND` | **FOUND** | `OURS` |
| 16 | L13 (Table 1, k=1) | `3,353` | Away-from-band count `n` at `k=1` | `output.txt:6` | `size_far = 3353` | `FOUND` | **FOUND** | `OURS` |
| 17 | L14 (Table 1, k=2) | `2` | Bars since last touch `k` | `output.txt:7` | `k = 2` | `FOUND` | **FOUND** | `OURS` |
| 18 | L14 (Table 1, k=2) | `59%` | Near-band P(new low) at `k=2` | `output.txt:7` | `mean_near = 0.587` (58.7% rounds to 59%) | `FOUND` | **FOUND** | `OURS` |
| 19 | L14 (Table 1, k=2) | `4,528` | Near-band count `n` at `k=2` | `output.txt:7` | `size_near = 4528` | `FOUND` | **FOUND** | `OURS` |
| 20 | L14 (Table 1, k=2) | `31%` | Away-from-band P(new low) at `k=2` | `output.txt:7` | `mean_far = 0.307` (30.7% rounds to 31%) | `FOUND` | **FOUND** | `OURS` |
| 21 | L14 (Table 1, k=2) | `3,934` | Away-from-band count `n` at `k=2` | `output.txt:7` | `size_far = 3934` | `FOUND` | **FOUND** | `OURS` |
| 22 | L15 (Table 1, k=3) | `3` | Bars since last touch `k` | `output.txt:8` | `k = 3` | `FOUND` | **FOUND** | `OURS` |
| 23 | L15 (Table 1, k=3) | `60%` | Near-band P(new low) at `k=3` | `output.txt:8` | `mean_near = 0.604` (60.4% rounds to 60%) | `FOUND` | **FOUND** | `OURS` |
| 24 | L15 (Table 1, k=3) | `3,302` | Near-band count `n` at `k=3` | `output.txt:8` | `size_near = 3302` | `FOUND` | **FOUND** | `OURS` |
| 25 | L15 (Table 1, k=3) | `29%` | Away-from-band P(new low) at `k=3` | `output.txt:8` | `mean_far = 0.290` (29.0% rounds to 29%) | `FOUND` | **FOUND** | `OURS` |
| 26 | L15 (Table 1, k=3) | `3,982` | Away-from-band count `n` at `k=3` | `output.txt:8` | `size_far = 3982` | `FOUND` | **FOUND** | `OURS` |
| 27 | L16 (Table 1, k=4) | `4` | Bars since last touch `k` | `output.txt:9` | `k = 4` | `FOUND` | **FOUND** | `OURS` |
| 28 | L16 (Table 1, k=4) | `60%` | Near-band P(new low) at `k=4` | `output.txt:9` | `mean_near = 0.598` (59.8% rounds to 60%) | `FOUND` | **FOUND** | `OURS` |
| 29 | L16 (Table 1, k=4) | `2,490` | Near-band count `n` at `k=4` | `output.txt:9` | `size_near = 2490` | `FOUND` | **FOUND** | `OURS` |
| 30 | L16 (Table 1, k=4) | `29%` | Away-from-band P(new low) at `k=4` | `output.txt:9` | `mean_far = 0.285` (28.5% rounds to 29%) | `FOUND` | **FOUND** | `OURS` |
| 31 | L16 (Table 1, k=4) | `3,721` | Away-from-band count `n` at `k=4` | `output.txt:9` | `size_far = 3721` | `FOUND` | **FOUND** | `OURS` |
| 32 | L17 (Table 1, k=5) | `5` | Bars since last touch `k` | `output.txt:10` | `k = 5` | `FOUND` | **FOUND** | `OURS` |
| 33 | L17 (Table 1, k=5) | `63%` | Near-band P(new low) at `k=5` | `output.txt:10` | `mean_near = 0.628` (62.8% rounds to 63%) | `FOUND` | **FOUND** | `OURS` |
| 34 | L17 (Table 1, k=5) | `1,929` | Near-band count `n` at `k=5` | `output.txt:10` | `size_near = 1929` | `FOUND` | **FOUND** | `OURS` |
| 35 | L17 (Table 1, k=5) | `27%` | Away-from-band P(new low) at `k=5` | `output.txt:10` | `mean_far = 0.267` (26.7% rounds to 27%) | `FOUND` | **FOUND** | `OURS` |
| 36 | L17 (Table 1, k=5) | `3,315` | Away-from-band count `n` at `k=5` | `output.txt:10` | `size_far = 3315` | `FOUND` | **FOUND** | `OURS` |
| 37 | L18 (Table 1, k=6) | `6` | Bars since last touch `k` | `output.txt:11` | `k = 6` | `FOUND` | **FOUND** | `OURS` |
| 38 | L18 (Table 1, k=6) | `64%` | Near-band P(new low) at `k=6` | `output.txt:11` | `mean_near = 0.641` (64.1% rounds to 64%) | `FOUND` | **FOUND** | `OURS` |
| 39 | L18 (Table 1, k=6) | `1,474` | Near-band count `n` at `k=6` | `output.txt:11` | `size_near = 1474` | `FOUND` | **FOUND** | `OURS` |
| 40 | L18 (Table 1, k=6) | `26%` | Away-from-band P(new low) at `k=6` | `output.txt:11` | `mean_far = 0.263` (26.3% rounds to 26%) | `FOUND` | **FOUND** | `OURS` |
| 41 | L18 (Table 1, k=6) | `2,874` | Away-from-band count `n` at `k=6` | `output.txt:11` | `size_far = 2874` | `FOUND` | **FOUND** | `OURS` |
| 42 | L21 (Sec 1) | `60%` | Approximate near-band new-low share (`about 60%`) | `output.txt:6-11` | `mean_near = 0.594..0.641` (59%..64%, ~60%) | `FOUND` | **FOUND** | `OURS` |
| 43 | L22 (Sec 1) | `30%` | Approximate away-from-band new-low share (`about 30%`) | `output.txt:6-11` | `mean_far = 0.263..0.319` (26%..32%, ~30%) | `FOUND` | **FOUND** | `OURS` |
| 44 | L23 (Sec 1) | `0` | `%b` at lower band (`0 is on the lower band`) | `study.py:9,21` | `%b = (close - lower) / (upper - lower) = 0` at `close = lower` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 45 | L23 (Sec 1) | `0.5` | `%b` at mid (`0.5 is the mid`) | `study.py:9,21` | `mid = m, lower = m - 2*sd, upper = m + 2*sd -> %b = 0.5` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 46 | L25 (Sec 2 hdr) | `11,051` | Sample size across exit rules (`over all 11,051`) | `output.txt:1,14-17` | `n=11051` on all four exit rows | `FOUND` | **FOUND** | `OURS` |
| 47 | L27 (Table 2 hdr) | `0` | Win rate threshold (`Share > 0`) | `output.txt:13` | `Gross % per short (no fees), mean / median / share > 0:` | `FOUND` | **FOUND** | `OURS` |
| 48 | L29 (Table 2, X0) | `+0.178%` | Mean gross % (`First close back inside after a touch`) | `output.txt:14` | `X0_first_close_inside ... mean=0.178` | `FOUND` | **FOUND** | `OURS` |
| 49 | L29 (Table 2, X0) | `+0.094%` | Median gross % (`First close back inside after a touch`) | `output.txt:14` | `X0_first_close_inside ... med=0.094` | `FOUND` | **FOUND** | `OURS` |
| 50 | L29 (Table 2, X0) | `76%` | Share > 0 (`First close back inside after a touch`) | `output.txt:14` | `X0_first_close_inside ... win=0.755` (75.5% rounds to 76%) | `FOUND` | **FOUND** | `OURS` |
| 51 | L30 (Table 2, Xk3) | `+0.178%` | Mean gross % (`Three bars without a touch`) | `output.txt:15` | `Xk3_three_bars_no_touch ... mean=0.178` | `FOUND` | **FOUND** | `OURS` |
| 52 | L30 (Table 2, Xk3) | `+0.067%` | Median gross % (`Three bars without a touch`) | `output.txt:15` | `Xk3_three_bars_no_touch ... med=0.067` | `FOUND` | **FOUND** | `OURS` |
| 53 | L30 (Table 2, Xk3) | `64%` | Share > 0 (`Three bars without a touch`) | `output.txt:15` | `Xk3_three_bars_no_touch ... win=0.636` (63.6% rounds to 64%) | `FOUND` | **FOUND** | `OURS` |
| 54 | L31 (Table 2, Xfar) | `0.25` | Exit rule threshold (`First close with %b >= 0.25`) | `output.txt:16` | `Xfar_close_pb_ge_025` | `FOUND` | **FOUND** | `OURS` |
| 55 | L31 (Table 2, Xfar) | `+0.172%` | Mean gross % (`First close with %b >= 0.25`) | `output.txt:16` | `Xfar_close_pb_ge_025 ... mean=0.172` | `FOUND` | **FOUND** | `OURS` |
| 56 | L31 (Table 2, Xfar) | `+0.062%` | Median gross % (`First close with %b >= 0.25`) | `output.txt:16` | `Xfar_close_pb_ge_025 ... med=0.062` | `FOUND` | **FOUND** | `OURS` |
| 57 | L31 (Table 2, Xfar) | `69%` | Share > 0 (`First close with %b >= 0.25`) | `output.txt:16` | `Xfar_close_pb_ge_025 ... win=0.687` (68.7% rounds to 69%) | `FOUND` | **FOUND** | `OURS` |
| 58 | L32 (Table 2, Xmid) | `+0.168%` | Mean gross % (`Close above the mid (hold)`) | `output.txt:17` | `Xmid_close_above_mid ... mean=0.168` | `FOUND` | **FOUND** | `OURS` |
| 59 | L32 (Table 2, Xmid) | `+0.005%` | Median gross % (`Close above the mid (hold)`) | `output.txt:17` | `Xmid_close_above_mid ... med=0.005` | `FOUND` | **FOUND** | `OURS` |
| 60 | L32 (Table 2, Xmid) | `51%` | Share > 0 (`Close above the mid (hold)`) | `output.txt:17` | `Xmid_close_above_mid ... win=0.512` (51.2% rounds to 51%) | `FOUND` | **FOUND** | `OURS` |
| 61 | L38 (Sec 2) | `+0.2%` | Upper bound of four exit means (`All four are under +0.2% gross`) | `output.txt:14-17` | `mean = 0.178, 0.178, 0.172, 0.168` (all < 0.2%) | `FOUND` | **FOUND** | `OURS` |
| 62 | L38 (Sec 2) | `0.12%` | Round-trip cost benchmark (`against 0.12% round-trip cost`) | `T06/costs.csv:52-54` | `12.0` bps (0.12% round-trip fee+slippage convention) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 63 | L40 (Sec 3 hdr) | `10-29` | Spot case date (`The 10-29 case`) | `study.py:87` | `startTime=1793293200000` (10-29 17:00Z..22:40Z) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 64 | L42 (Sec 3) | `80,412` | Entry close at 20:00 (`the 20:00 close at 80,412`) | `live_output.txt:13` | `20:00 c=80412` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 65 | L42 (Sec 3) | `80,798` | BB mid at 20:00 (`below the mid at 80,798`) | `live_output.txt:13` | `20:00 ... mid=80798` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 66 | L43 (Sec 3) | `20:00` to `21:00` (except `20:25`) | Touch window (`from 20:00 to 21:00, except 20:25`) | `live_output.txt:13-25` | `20:00..21:00 touch=1` on 12 of 13 bars; `20:25 touch=0` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 67 | L43 (Sec 3) | `0.02` | `%b` at 20:50 (`The 20:50 green closed at %b 0.02`) | `live_output.txt:23` | `20:50 c=79101 ... %b=0.02` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 68 | L44 (Sec 3) | `21:00` | Last lower-band touch timestamp (`Last touch: 21:00`) | `live_output.txt:25-43` | `21:00 ... touch=1`; `21:05..22:30 touch=0` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 69 | L46 (Sec 3) | `0.21` | `%b` at 21:05 (`21:05 closed near the band (%b 0.21)`) | `live_output.txt:26` | `21:05 c=79175 ... touch=0 %b=0.21` (k=1) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 70 | L46 (Sec 3) | `59%` | DEV new-low chance for k=1 near band (`so about 59% for a new low`) | `output.txt:6` | `k=1 mean_near = 0.594` (59%) | `FOUND` | **FOUND** | `OURS` |
| 71 | L47 (Sec 3) | `0.25` | `%b` at 21:10 (`21:10 closed at %b 0.25`) | `live_output.txt:27` | `21:10 c=79225 ... touch=0 %b=0.25` (k=2) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 72 | L47 (Sec 3) | `31%` | DEV new-low chance for k=2 away from band (`about 31%`) | `output.txt:7` | `k=2 mean_far = 0.307` (31%) | `FOUND` | **FOUND** | `OURS` |
| 73 | L48 (Sec 3) | `0.30-0.46` | `%b` range from 21:15 (`closes were at %b 0.30-0.46`) | `live_output.txt:28-36` | `21:15..21:55 %b = 0.38, 0.38, 0.34, 0.43, 0.46, 0.31, 0.38, 0.32, 0.30` (min `0.30`, max `0.46`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 74 | L49 (Sec 3) | `0.11-0.21` | `%b` range at 22:00-22:10 (`(%b 0.11-0.21)`) | `live_output.txt:37-39` | `22:00 %b=0.19, 22:05 %b=0.11, 22:10 %b=0.21` (min `0.11`, max `0.21`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 75 | L49 (Sec 3) | `78,627` | Low at 22:05 (`the 22:05 low of 78,627`) | `live_output.txt:38` | `22:05 c=78699 l=78627` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 76 | L49 (Sec 3) | `78,297` | Prior low of the short (`stayed above the 78,297 low`) | `live_output.txt:22` | `20:45 c=78987 l=78297` (lowest `l` in 20:00..22:20) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 77 | L54 (Table 3, Xfar) | `0.25` | Exit rule threshold (`%b >= 0.25` at `21:10`) | `output.txt:16` / `live_output.txt:27` | `Xfar_close_pb_ge_025` / `21:10 %b=0.25` | `FOUND` | **FOUND** | `OURS` |
| 78 | L54 (Table 3, Xfar) | `79,225` | Exit price at 21:10 (`79,225`) | `live_output.txt:27` | `21:10 c=79225` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 79 | L54 (Table 3, Xfar) | `+1.48%` | Gross gain at 21:10 (`+1.48%`) | `live_output.txt:13,27` | `(80412 - 79225) / 80412 * 100 = +1.4761%` (rounds to `+1.48%`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 80 | L55 (Table 3, Xk3) | `79,567` | Exit price at 21:15 (`79,567`) | `live_output.txt:28` | `21:15 c=79567` (3rd bar with `touch=0` after `21:00`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 81 | L55 (Table 3, Xk3) | `+1.05%` | Gross gain at 21:15 (`+1.05%`) | `live_output.txt:13,28` | `(80412 - 79567) / 80412 * 100 = +1.0508%` (rounds to `+1.05%`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 82 | L56 (Table 3, Xmid) | `79,166` | Exit price at 22:20 (`79,166`) | `live_output.txt:41` | `22:20 c=79166 ... abovemid=1` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 83 | L56 (Table 3, Xmid) | `79,137` | BB mid at 22:20 (`(mid 79,137)`) | `live_output.txt:41` | `22:20 ... mid=79137` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 84 | L56 (Table 3, Xmid) | `+1.55%` | Gross gain at 22:20 (`+1.55%`) | `live_output.txt:13,41` | `(80412 - 79166) / 80412 * 100 = +1.5495%` (rounds to `+1.55%`) | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 85 | L60 (Open) | `5m` | Evaluated bar timeframe (`The bars here are 5m only`) | `study.py:5` | `5m bars from the Binance USD-M BTCUSDT 1m archive` | `NOT_IN_DATA` | **FOUND** | `OURS` |
| 86 | L60 (Open) | `15m` | Unrun follow-up timeframe (`Repeat on 15m and 1h`) | `RESULT.md:60` | Proposed next step in `## Open`; not in `output.txt` or `study.py` | `NOT_IN_DATA` | **NOT_IN_DATA** | `OURS` |
| 87 | L60 (Open) | `1h` | Unrun follow-up timeframe (`Repeat on 15m and 1h`) | `RESULT.md:60` | Proposed next step in `## Open`; not in `output.txt` or `study.py` | `NOT_IN_DATA` | **NOT_IN_DATA** | `OURS` |

---

## Detailed Section-by-Section Verification Notes

1. **Sample & Table 1 (`RESULT.md:5-22` vs `output.txt:1-11`)**:
   - Total sample `11,051` matches `output.txt:1` (`shorts with a lower-band touch: 11051`).
   - All 30 cells in Table 1 (`k = 1..6`, `%b < 0.25` vs `%b >= 0.25`, percentages and counts `n`) match `output.txt:6-11` with zero discrepancies:
     - `k=1`: near `0.594` -> `59%` (`n=6,360`), far `0.319` -> `32%` (`n=3,353`)
     - `k=2`: near `0.587` -> `59%` (`n=4,528`), far `0.307` -> `31%` (`n=3,934`)
     - `k=3`: near `0.604` -> `60%` (`n=3,302`), far `0.290` -> `29%` (`n=3,982`)
     - `k=4`: near `0.598` -> `60%` (`n=2,490`), far `0.285` -> `29%` (`n=3,721`)
     - `k=5`: near `0.628` -> `63%` (`n=1,929`), far `0.267` -> `27%` (`n=3,315`)
     - `k=6`: near `0.641` -> `64%` (`n=1,474`), far `0.263` -> `26%` (`n=2,874`)

2. **Table 2: Exits Compared (`RESULT.md:25-38` vs `output.txt:13-17`)**:
   - All 12 cells across the 4 exit rules match `output.txt:14-17`:
     - `X0_first_close_inside`: mean `0.178` (`+0.178%`), med `0.094` (`+0.094%`), win `0.755` (`76%`)
     - `Xk3_three_bars_no_touch`: mean `0.178` (`+0.178%`), med `0.067` (`+0.067%`), win `0.636` (`64%`)
     - `Xfar_close_pb_ge_025`: mean `0.172` (`+0.172%`), med `0.062` (`+0.062%`), win `0.687` (`69%`)
     - `Xmid_close_above_mid`: mean `0.168` (`+0.168%`), med `0.005` (`+0.005%`), win `0.512` (`51%`)

3. **Section 3: The 10-29 Case (`RESULT.md:40-56` vs `live_output.txt:13-41`)**:
   - Every bar timestamp, price, `%b`, touch flag, and computed gross percentage gain in Section 3 and Table 3 matches `live_output.txt:13-41` (`Xfar` at 21:10 `(80412-79225)/80412 = +1.476% -> +1.48%`; `Xk3` at 21:15 `(80412-79567)/80412 = +1.051% -> +1.05%`; `Xmid` at 22:20 `(80412-79166)/80412 = +1.550% -> +1.55%`).

Noticed: Every empirical number in `RESULT.md` Sections 1 and 2 (46 numbers) matches `output.txt` (`output.txt:1-17`) with 0 `DIFF`, and all 30 spot case numbers in Section 3 match `live_output.txt` (`live_output.txt:13-41`), which is explicitly cited in the Section 3 header (`RESULT.md:40`).
