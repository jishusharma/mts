# Crowding as a contrarian signal, 4h and 1d, 10 Bybit USDT perps (2026-11-13)

**Verdict: FAIL.** 0 of 24 cells pass. VALIDATION (2024-07-01..2025-06-30) fee-net mean is negative in 21 of 24 cells; the best, OIFLAT 4h/7d, is +8.7 bp on n=57 with CI [-315, +334] bp, one-sided p 0.48. Smallest VALIDATION p across all cells is 0.48, so BH at 10% selects nothing. Rule, parameters and pass line are in `PRE_REG.md` (committed first, sha 4a540b4da); nothing was changed after the run. Raw table: `results.csv`, log: `output.txt`.

Data: Bybit v5 public, 10 coins (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX), kline from 2020-03 (BTC) to 2021-10 (SOL); account ratio 4h from 2020-07. Fees: `fees.BINANCE_TAKER x 2` plus funding paid while held; entry next bar open; one position per coin; weekly-cluster bootstrap 4000; placebo = same coin, same month, same side (200 draws).

## VALIDATION, per signal (fee-net bp per trade; range over the 6 TF x hold cells)
| Signal | n range | mean range (bp) | Cells beating placebo p95 | Best CI lower (bp) |
|---|---|---|---|---|
| a FUND extreme, fade | 339-1676 | -230 to -45 | 3 of 6 | -166 |
| b RATIO extreme, fade | 197-852 | -90 to -6 | 3 of 6 | -363 |
| c FUND + 3d push | 94-338 | -281 to -83 | 2 of 6 | -392 |
| d OI surge, price flat, vs funding | 23-75 | -92 to +9 | 0 of 6 | -250 |

## Other splits (context, not a pass)
- Ratio fade (b) is the only family that looks alive outside VALIDATION: DEV +25 to +196 bp (1d/7d: +196, CI [+74, +316], n=629, beats placebo) and RECENT +11 to +131 bp (1d/7d: +131, CI [+6, +264], n=291), but it does not beat the RECENT placebo p95 (+175 bp; the placebo is itself positive in RECENT, so side drift explains part of it) and VALIDATION is -86 bp, CI [-311, +143], n=197. The sign flip means no pass.
- Funding extreme fade (a) is flat-to-negative in every split; the fee-net DEV means (-26 to +14 bp) are inside noise.
- Funding+push (c) is negative in all 18 split cells: fading a crowded move that already ran lost money, the move continued.
- n: signal d has 23-75 trades per VALIDATION cell (UNDERPOWERED for the 1d cells, n < 30 in 2 of them).
- Regime mix from prices (share of 3-day windows up): DEV 0.499, VALIDATION 0.510, RECENT 0.467.

## Reading
Funding and account-ratio extremes did not reverse over the next 1-7 days after costs in the year-long out-of-sample window. Hold-7 cells lose the most because funding is paid for the whole hold while the crowded side keeps trending. The one thing worth another look is the account ratio on 1d/7d, which is positive in two of three splits.

## 2026-11-13 context (not a signal)
Latest BTC 4h account buy-ratio row is 0.733, above its trailing 90-day 95th percentile (0.704): signal (b) would say short. Latest funding is -0.0033%, at the 1st percentile of its trailing 270 prints: signal (a) would say long. The two disagree, and neither passed VALIDATION.

## Tests and wiring
`test_crowd.py` (6 tests: PIT percentile excludes the current value, fade side, fee and funding sign, funding window and hold, next-bar entry plus one-position rule, bootstrap CI); registered in `scripts/dev/extra_tests.tsv`. The tests were written before the first run; there is no pre-change code to fail against (new module).

## Best next test
Account-ratio fade, 1d, 7d hold, with the PRE_REG changed to pool VALIDATION+RECENT against a drift-matched placebo and more coins (top-30 perps), registered first; the DEV and RECENT sign agrees but VALIDATION does not.
