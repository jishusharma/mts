# T058 per-timeframe break event study (ledger P0-45) - REDUCED run

**Result: across W/1D/4h/1h/15m, a close-break of a confirmed swing level holds (no close back inside) about 35% of the time at 15m, 43-46% at 1h, 42-50% at 4h; no class (hold or reclaim) earned a positive fee-net trade at any TF with n >= 100. Daily and weekly are too few events to say anything.**

Numbers: all tables are in `output.md`, produced by `study.py` then `analyze.py` (`python study.py events.csv; python analyze.py events.csv > output.md`). `events.csv` is the full event list (22k rows: 10.5k real, rest pseudo-level control).

## What was run (and what was not)

| Item | Status |
|---|---|
| Data | Binance USD-M BTCUSDT 1m archive (`F:/MTS/data/tom_raw/klines`), 2022-01-01 to 2025-08-31, 1.93M rows; TF bars built by UTC epoch bucketing, complete buckets only (W = epoch weeks, start Thursday) |
| Splits | DEV 2022-01..2024-06, VAL 2024-07..2025-08. Holdout 2025-09+ NOT read |
| Indicators before/at/after | RSI(14) Wilder, taker-flow ratio (2*taker_buy - volume)/volume (a per-bar CVD delta), volume vs 20-bar median. Pre = bars i-5..i-1, At = break bar, Post = bars i+1..i+N |
| NOT done (data not local for 2022-2025) | OI delta, funding, tick tiers, liquidations (T058 data gaps 1-4). Hence no OI/funding conditioning |
| NOT done | DSR/PBO, time-shuffle control C2, rolling-channel baseline C3, parameter sensitivity grid (L, N, buffer). Only primary parameters ran |

Parameters (all OURS, frozen before the run; from T058_BROKEN_EXTREMES.md 3.2-3.3): fractal swing L = W2, D3, 4h3, 1h5, 15m5, known at bar k+L close; reclaim window N = W2, D3, 4h6, 1h6, 15m8; close-break buffer 0.1 x ATR14 (SMA); first bar to pierce a live level consumes it (close beyond by buffer = break, else W1 wick sweep). Cost for net columns: 12 bp round trip (10 bp taker + 2 bp slippage, OURS slippage). Forward measures start at the open after the class is known. Control C1: same pipeline with a random non-fractal bar's low/high (last M bars, near side of price) as the level.

## Findings (all from `output.md`)

| # | Finding | Evidence |
|---|---|---|
| 1 | Hold share among close-breaks falls with shorter TF: 1D 63% DEV / 50% VAL (n 35 / 20), 4h 50% / 42%, 1h 46% / 43%, 15m 36% / 35% (T2) | Direction "higher TF holds more" appears in DEV, but 1D flips down in VAL and its CI is [27, 70]; only 15m vs 4h/1h is statistically separated (15m CI [34, 38] DEV, [32, 38] VAL) |
| 2 | Being a real swing mostly changes how often price closes through, not whether it holds after: close-break share (R+H) for real levels is ~40-46% at 4h/1h/15m vs ~31-38% for pseudo-levels, in both DEV and VAL; H share among breaks differs from control by 1-6 pp with overlapping CIs | T1, T2 |
| 3 | Wick sweeps (W1, pierce but close back inside) are the most common outcome at every TF: 55-60% of events at 4h/1h/15m, 54-75% at 1D | T1 |
| 4 | Indicator state AT the break is similar for H and R: RSI falls ~8-10 points from pre to at in both (e.g. 1h pre 44 to at 36 R / 33 H), taker flow against the break is ~equally negative (1h at -0.10 R, -0.11 H), volume spike is larger for H (4h 2.8x vs 2.2x median; 1h 3.9x vs 3.0x). AFTER: RSI recovers to pre level for R (1h 46) and stays low for H (1h 34); taker flow turns positive for R (+0.012) and stays negative for H (-0.013). After is a consequence of the class, not a predictor | T3 |
| 5 | Only AT-bar variables that separated H from R in DEV AND kept the same direction in VAL: larger break distance (close beyond level in ATR) and larger volume spike -> more holds (15m dist 24% below / 49% above DEV cut; 24% / 51% VAL; 1h 32 / 61 DEV, 32 / 56 VAL; 4h dist 37 / 63 DEV, 26 / 58 VAL); higher AT RSI -> fewer holds at 1h and 15m. These are partly mechanical (a deeper close is further from reclaiming) and were not corrected for multiple testing | T4 |
| 6 | Fee-net trades: follow H and fade R both negative or indistinguishable from zero at 15m, 1h, 4h in DEV and VAL (15m follow H -0.12 / -0.10 %, fade R -0.15 / -0.13 % per trade at h4, CI excludes 0 on the negative side). 1D fade R VAL +2.30 % [0.18, 4.89] has DEV +0.85 % [-1.77, 3.02] with n 13 / 10 and is not a result | T5 |
| 7 | W: 12 W1 events, 7 real breaks in 3.7 years, nothing to conclude | T1 |

## Reading for the question asked

- "Is a weekly low broken different from a daily?" Not answerable here: 19 weekly and 129 daily real events (both sides) over 3.7 years. More history (Binance futures from 2019-09, or spot BTCUSDT) is the first fix.
- At 15m-4h the data say: most pierces are wick sweeps, and among close-breaks the chance the break holds is below 50% and rises modestly with TF and with how far the close is beyond the level. Neither "hold" nor "reclaim" gave a fee-net edge by itself, so the hedge hook in T058 Q4 has nothing from this run to be built on.
- Hypothesis H2 (OI-conditioned hold) was not testable (no OI before 2025-09); the 2025-09+ holdout is the only place it can be, and it was left unread on purpose.

## Caveats

- Bar-level evaluation (no 1m intrabar ordering for touch), so a pierce and close-back inside the same bar is W1 by construction.
- Events overlap in time (week-block bootstrap used for CIs where shown); cells with n < 30 are descriptive only (all W, most 1D).
- Taker-flow ratio uses `taker_buy_volume` from the archive; swing-count cross-check against `cc_structure.find_swings` not done.
- No parameter was tuned; sensitivities in T058 3.2/3.3 (L, N, buffer 0 and 0.25) were not run, so the findings are for the primary set only.
