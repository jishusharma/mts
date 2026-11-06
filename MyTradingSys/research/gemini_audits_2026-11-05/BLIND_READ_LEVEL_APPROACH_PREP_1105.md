# BLIND READ: level_approach_prep_2026-11-05 (U1 absorption, U2 OI tell, U3 wick count)

Reader: Claude Sonnet 5.5 worker on the `gemini-blind-read-of-level-approach-prep` card (producer of this audit; no REVIEWED stamp). Blind order: read PRE_REG.md definitions only, wrote [blind_read_lap.py](blind_read_lap.py) from them, ran it, and only then opened RESULT.md. study.py was never read.
Command: `python MyTradingSys/research/gemini_audits_2026-11-05/blind_read_lap.py` (raw output: [blind_read_lap_output.txt](blind_read_lap_output.txt)).

## Data (SOURCED: PRE_REG.md:12-13)
- 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01..2024-06.csv` -> 1,313,280 rows, 2022-01-01 00:00 .. 2024-06-30 23:59 (OURS: command output). 912 UTC days, bars at or after 2024-07-01 dropped.
- 5m OI `F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-*.csv` (the `data/binance_metrics` path named in PRE_REG does not exist; the files are in `data/metrics/BTCUSDT`) -> 262,528 stamps before 2024-07-01.

## Reading choices where PRE_REG.md is silent (OURS)
- "Within 0.3 %" approach: high >= PDH x 0.997 (low <= PDL x 1.003); the day opens inside the zone if the first bar's open is already past that line.
- Reversal and break both checked bar by bar from t+4..t+63; the reversal uses the bar low/high (0.5 % back from close of t+3); if both occur in the same bar the reversal counts first (primary). Break-first variant also run: absorption 18 %, non-absorption 26 %.
- OI start stamp = floor-5m of (t - 7 min); end stamp = floor-5m of (t + 4 min).
- Matching weights = absorption distance-bucket mix; all four buckets had non-absorption support (weight used 1.0).
- Wick TF bars aligned to the UTC epoch, TF bar must be complete and inside [u-15, u).

## Per-number table (RESULT.md line = RESULT.md:N)

| Number | RESULT.md | Recompute | Match |
|---|---|---|---|
| Prior-day H/L approaches | 887 (:3) | 887 | EXACT |
| First touches (U3 total) | 733 = 280+129+137+187 (:34-37) | 733 | EXACT |
| U1 absorption n | 228 (:18) | 224 | NO (-4, 1.8 %) |
| U1 absorption reversal | 18 % (:18) | 17.9 % | yes |
| U1 absorption break-first | 22 % (:18) | 21.9 % | yes |
| U1 non-absorption n | 659 (:19) | 663 | NO (+4) |
| U1 non-absorption reversal | 27 % (:19) | 27.0 % | yes |
| U1 non-absorption break-first | 45 % (:19) | 44.0 % | off 1 pt |
| U1 matched non-absorption reversal | 27 % (:20) | 26.9 % | yes |
| U2 UP n / reversal | 67 / 18 % (:26) | 67 / 17.9 % | yes |
| U2 FLAT n / reversal | 88 / 15 % (:27) | 87 / 14.9 % | n off 1 |
| U2 DOWN n / reversal | 73 / 23 % (:28) | 70 / 21.4 % | NO (n -3, rate -2 pt) |
| U2 group count | 3 | 3 | yes |
| U3 0 TF n / hold | 280 / 18 % (:34) | 285 / 17.5 % | n off 5, rate yes |
| U3 1 TF n / hold | 129 / 25 % (:35) | 130 / 24.6 % | yes |
| U3 2 TF n / hold | 137 / 23 % (:36) | 134 / 23.9 % | n off 3, rate off 1 pt |
| U3 3+ TF n / hold | 187 / 23 % (:37) | 184 / 23.9 % | n off 3, rate off 1 pt |
| U3 bucket count | 4 | 4 (0,1,2,3+; 3 and 4 TF split 131/53) | yes |

## Findings
- Event counts (887, 733) reproduce exactly, so level, zone-skip, approach and touch definitions agree.
- Absorption n differs by 4 of 228 (the absorption flag and the OI/wick fine counts move a few events). Likely a boundary difference (>= vs >, extension sign clamp, wick range rule, or bar-alignment); not isolated without reading study.py, which the blind rule excludes.
- Every qualitative conclusion in RESULT.md:5-8 replicates: absorption reverses less than matched non-absorption (18 % vs 27 %) and breaks half as often (22 % vs 44-45 %); OI split inside 15-21 % without a monotone ordering (n 67-87); wick TF count 0 holds 17.5 % vs 24-25 % for 1+, no gain beyond 1 TF.
- Practical drift: all differing rates are within about 2 points; sample sizes small (n 53-285), so the 2-point gaps are within noise.
- PRE_REG.md:12 names `F:/MTS/data/binance_metrics`, which does not exist on disk (actual: `F:/MTS/data/metrics/BTCUSDT`). Doc-path error only.

VERDICT: MISMATCH (minor: counts 887/733 and rates 18 %/22 %, 3 OI groups, 4 wick buckets match; absorption n 224 vs 228 and a few fine counts/rates differ by 1-2 points; conclusions unchanged)
