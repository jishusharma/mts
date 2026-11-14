# PRE_REG: Test 5, large-trade flow lead test with a proper lag, BTC (frozen before any outcome is computed)

Source brief: `buy_zone_1114/NEXT5_TESTS.md` Test 5 and its Shared rules. Task from login C ask q-d8cd77. Nothing here is an edge until a fee-net out-of-sample result passes; this is a LEAD-signal test and claims no trade result. Only data availability and file sizes were looked at when this file was written (the flow reduction job was started; flow aggregates were not joined to any return). Every parameter is OURS unless marked SOURCED.

## Context
Regime: none as a separate gate; the daily phase below (closed bars only) is the regime split. The test is run on ALL days and reported per phase.
Phase: UP, BASE, RANGE, DOWN, POSTPEAK_BEAR, the Test 1 daily labels (definitions in `buyzone_test1_ladder_2026-11-14/PRE_REG.md`, code reused unchanged from `ladder.phases`), read at the closed daily bar D that carries the flow, so the phase uses bars <= D only (no lookahead for an entry at the D+1 open).
Session: not applicable, 24/7 UTC calendar days (flow window = one UTC day).
Entry: hypothetical entry at the D+1 open (= Close[D]); the lead return is measured from there. No trade is claimed (SOURCED, NEXT5 Test 5 fee note).
Regime mix: reported in REPORT.md as the share of flow days per phase per split (DEV, VAL, RECENT) and the day count per phase. Regime mix in UP: reported; BASE: reported; RANGE: reported; DOWN: reported; POSTPEAK_BEAR: reported. A split whose days are more than 85% from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone.

## Data (OURS)
| Item | Choice |
|---|---|
| Flow | Binance public daily aggTrades dumps `data.binance.vision`, BTCUSDT, spot AND USD-M futures, UTC days 2022-01-01 to the last published day. No key. Each day is reduced on the fly by `fetch_flow.py` to large-trade sums; raw trades are never kept |
| Large trade | one aggTrade row (same-side, same-price aggregate of one taker order) with price x qty >= $1M ("1M") or >= $5M ("5M"). Both cutoffs are reported. Aggressor buy = `is_buyer_maker` False |
| Window | window t = one UTC day D. Flow is complete at D 24:00, return starts at the D+1 open |
| Price | Binance spot BTCUSDT 1d klines from the host cache (same source as Test 1), last (possibly partial) bar dropped. Returns: `ret24 = Close[D+1]/Close[D]-1` (t+1..t+24 h), `ret72 = Close[D+3]/Close[D]-1` (t+1..t+72 h) |
| Cache | outside the repo (`F:/MTS/data_cache` absent here): flow in `$MTS_FLOW_CACHE` or `C:/Users/e-ngineers/mts_cache/buyzone_test5`, price in `$MTS_DATA_CACHE` or `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d`. Never committed; repo is public. Tests use synthetic fixtures only and read no cache |
| Gap 2026-11-13 | the brief says the 11-13 files were not yet published. At registration time `BTCUSDT-aggTrades-2026-11-13.zip` returns 404 for spot. The last flow day used is the last day that has BOTH spot and futures flow AND the closed daily bars needed (D+1 for ret24, D+3 for ret72). Days with a missing spot or futures file are dropped and listed (gaps.json count in the REPORT) |
| Why 2022 start | download size limits the window (a full 2017+ aggTrades history is over 50 GB). 2022-01-01 gives DEV = 2022-2023 (two calendar years, about 730 days) and VAL = 2024 onwards (about 1050 days). Shorter DEV than other tests is a stated weakness |
| Coinbase premium | extra feature, DESCRIPTIVE only (cannot change the verdict): `prem[D] = 1e4 x (CB_close[D] / BN_close[D] - 1)` bp, Coinbase `BTC-USD` public daily candles (api.exchange.coinbase.com, UTC) vs Binance BTCUSDT daily close. It mixes the USD-USDT basis with the premium; stated in the report |

## Flow feature (OURS)
For venue v in {spot, fut}, cutoff k in {1M, 5M}: `net_{v,k}[D] = buy_{v,k}[D] - sell_{v,k}[D]` (USD). Normalised `F_{v,k}[D] = 1e4 x net_{v,k}[D] / total_v[D]` in bp of that venue's whole-day notional. Combined feature `F_{ALL,k}[D] = 1e4 x (net_spot,k + net_fut,k) / (total_spot + total_fut)`. PRIMARY feature: `F_ALL,1M` and (second primary, required by the verdict) `F_ALL,5M`. Descriptive rows: spot only, futures only, and Coinbase premium.

## Design (SOURCED, NEXT5 Test 5; details OURS)
- 24 h: pairs (F[D], ret24[D]) for every day D. Flow windows do not overlap and return windows do not overlap (each return day is the next flow day, never the same window).
- 72 h: non-overlapping 72 h returns need stride 3: three offsets o in {0,1,2}, day index D with `(day number) mod 3 == o`. Offset 0 is the reported 72 h row; offsets 1 and 2 are replicates (stated, not pooled).
- Quintiles: cutoffs are the 20/40/60/80th percentiles of the DEV flow values (DEV days with a return), frozen and applied unchanged to DEV, VAL and RECENT (causal for VAL; in-sample for DEV, stated). Q5 = highest flow, Q1 = lowest.
- Statistics per cell (split x phase, plus ALL phases): n, Spearman rank correlation of F with ret (24 h and 72 h), mean ret per quintile, spread = mean ret(Q5) - mean ret(Q1) in bp. A quintile with n < 10 marks the cell UNDERPOWERED (spread shown, not used).
- Fee-net rows (descriptive, cannot change the verdict, no trade claimed): long Q5 mean ret minus fee; short Q1 (= minus mean ret) minus fee; two-leg spread minus 2 x fee. Fee 12 bp (main) and 6 bp (sensitivity) per round trip.
- Splits: DEV <= 2023-12-31 (by flow day D); VAL >= 2024-01-01; RECENT >= 2025-07-01 (subset of VAL, reported separately, never used to pick anything).

## Placebo (>= 1000 draws)
2000 draws, seed 1114. Within each split, flow values are permuted among days of the SAME phase (shuffle within phase), returns and phases unchanged, DEV quintile cutoffs unchanged. Per draw the spread is recomputed; the band is the 2.5th to 97.5th percentile of the 2000 draw spreads; the percentile of the actual spread is reported. "Beats the shuffle band" = actual spread above the 97.5th percentile. Run per cell where all five quintiles have n >= 10, for both horizons.

## Bootstrap
Block bootstrap of the day pairs by 7-calendar-day blocks of D (longer than the 1-day / 3-day return hold, so it also covers serial dependence; DECISION OURS, conservative), 10000 resamples, seed 1114, percentile 95% CI of the spread (block sums per quintile resampled together, quintile means recomputed).

## Verdict (SOURCED NEXT5 Test 5; conservative details DECISION OURS)
PRIMARY = ALL phases, VAL, ret24, spread of top vs bottom flow quintile, for BOTH F_ALL,1M and F_ALL,5M.
- UNDERPOWERED (do not claim) if VAL days with a ret24 < 200.
- PASS only if, for BOTH cutoffs: VAL spread > 0 AND bootstrap CI low > 0 AND actual spread > shuffle 97.5th percentile AND DEV spread > 0 (sign agrees). A PASS is a LEAD PASS only: it licenses pre-registering a separate fee-net trade test, nothing else.
- Otherwise KILL, stated with the VAL spread in bp, CI, shuffle percentile and n for both cutoffs. If the cutoffs disagree in sign it is stated as MIXED and counted as KILL.
- The shared rule "VAL fee-net 12 bp mean R > 0" is not a PASS condition here (brief: lead-signal test, fee note); the fee-net rows are reported anyway.
- Descriptive only: 72 h rows and replicates, per phase, RECENT, spot-only, futures-only, Coinbase premium, correlation (Spearman; also the concurrent same-window correlation Spearman(F[D], return over day D) as the +0.45 check).
- One primary test; nothing re-run with changed rules. A bug fix is stated with both numbers.

## Output
`REPORT.md` and `summary.json` in this folder. Code: `flow.py`, `run_test5.py`, `fetch_flow.py`, `fetch_cb.py`, tests `test_flow.py`.
