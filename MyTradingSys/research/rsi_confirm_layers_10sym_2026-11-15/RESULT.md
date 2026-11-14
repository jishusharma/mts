# RESULT: RSI-extreme + confirm-candle long with ONE layer, re-derived on 10 symbols, 2024+ out of sample, fee-net 0.14 % round trip (card rederive-rsi-confirm-layers)

**Verdict: NO EDGE.** 0 of 56 pre-registered layer tests PASS on VALIDATION (38 FAIL, 18 UNDERPOWERED with n < 30); smallest Holm-adjusted p over the 56 is 1.000 (best raw one-sided p 0.050, 4h SmallR +2R, n = 22). Power-qualified: the count-only gate BLOCKed (MDE 0.76 to 1.6 R vs a plausible 0.30 R, POWER_GATE.md), so this reads "no edge found at this power, base rule net-negative on 1h", not a proof for every variant.
Regime mix: BTC weeks by research_kit.regime_tag: DEV 2020-03..2023-12 200 weeks bull 20 % / bear 0 % / range 80 %; VALIDATION 2024-01-01..2026-11-14 150 weeks bull 58 (39 %) | bear 0 (0 %) | range 92 (61 %); first half 79 weeks bull 63 %, second half 71 weeks bull 11 % / range 89 % (regime_mix.txt). Bear never fires with this tag, so no bear-phase statement is possible.

Rule and layers unchanged from `rsi_confirm_layers_2026-11-13` (code reused by path). Changed: 10 symbols (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, Bybit USDT perps), cost research_kit.TAKER_RT_PCT 0.14 % round trip (parent 0.10 %), Holm over m = 56 on day-clustered one-sided p (parent: BH on bootstrap p). Trades: 1h 539 (DEV 284 / VAL 255), 4h 129 (DEV 60 / VAL 69); VALIDATION = entry from 2024-01-01; last trade 2026-11-05 (7 h-day forward window rule). Correction to PRE_REG: the "~10 extra days" of data did not materialise, the last tested entry is the same date as the parent's, so the 2024+ window is NOT fresh versus the parent (its layers saw it on 20 coins); this is a cost / universe / multiplicity re-test only.
Parameters: all as PRE_REG table (signal threshold 20, exits +1R/+2R, 72 h cap, layer cutoffs OURS; entry and stop SOURCED operator; cost SOURCED research_kit; regime band SOURCED Malkan).

## Unfiltered base (the bar every layer has to beat), VALIDATION, mean fee-net R

| base | n DEV / VAL | win% VAL | mean R DEV | mean R VAL | SE (day-clustered) | boot 95 % CI VAL | MDE (2.8 SE) |
|---|---|---|---|---|---|---|---|
| 1h +1R | 284 / 255 | 47 % | -0.237 | -0.198 | 0.097 | [-0.39, +0.00] | 0.27 |
| 1h +2R | 284 / 255 | 38 % | -0.256 | -0.124 | 0.130 | [-0.38, +0.15] | 0.36 |
| 4h +1R | 60 / 69 | 65 % | -0.036 | +0.139 | 0.164 | [-0.18, +0.45] | 0.46 |
| 4h +2R | 60 / 69 | 59 % | -0.295 | +0.375 | 0.276 | [-0.17, +0.90] | 0.77 |

1h bare rule is net-negative in DEV and VALIDATION (the 1h +1R CI touches zero from below). 4h VALIDATION is positive but its CI contains 0 and DEV is negative.

## The cells that look best (all 56 are in cells.csv)

| cell (TF, exit) | n DEV / VAL | mean R DEV | mean R VAL | win% VAL | raw p | Holm p | placebo p | verdict |
|---|---|---|---|---|---|---|---|---|
| OI-unwind, 1h +1R | 141 / 93 | -0.221 | +0.112 | 61 % | 0.198 | 1.000 | 0.001 | FAIL |
| OI-unwind, 1h +2R | 141 / 93 | -0.348 | +0.168 | 52 % | 0.129 | 1.000 | 0.004 | FAIL |
| US 16-24 UTC, 1h +1R | 105 / 108 | -0.300 | +0.027 | 56 % | 0.432 | 1.000 | 0.001 | FAIL |
| US 16-24 UTC, 1h +2R | 105 / 108 | -0.205 | +0.168 | 48 % | 0.199 | 1.000 | 0.002 | FAIL |
| SmallR, 4h +2R | 20 / 22 | -0.215 | +0.744 | 64 % | 0.050 | 1.000 | 0.041 | UNDERPOWERED |
| dADX>25, 4h +2R | 35 / 40 | -0.236 | +0.397 | 55 % | 0.117 | 1.000 | 0.411 | FAIL |

OI-unwind and US beat the 1h base (placebo p <= 0.004, +0.29 to +0.31 R over base) but sit at mean +0.03 to +0.17 R with a clustered SE of 0.12 to 0.16 R, and they were NEGATIVE in DEV (-0.20 to -0.35 R): the sign flips between periods, which is what noise on 10 coins looks like. Same two layers were the parent's best 1h cells (also FAIL there). Every other 1h layer has a negative VALIDATION mean; BTC/ETH, SmallR and dADX 20-25 are significantly worse than base.

## Phase split (VALIDATION, fee-net mean R, descriptive; phase.csv has the layers with Holm p <= 0.20, which is none above 1.0)

| base | regime bull (n) | regime range (n) | BTC > SMA200 (n) | BTC < SMA200 (n) |
|---|---|---|---|---|
| 1h +1R | -0.054 (80) | -0.264 (175) | -0.224 (124) | -0.173 (131) |
| 1h +2R | +0.033 (80) | -0.196 (175) | -0.215 (124) | -0.039 (131) |
| 4h +1R | -0.105 (31) | +0.338 (38) | +0.006 (37) | +0.292 (32) |
| 4h +2R | -0.280 (31) | +0.909 (38) | -0.027 (37) | +0.839 (32) |

1h is least bad in bull weeks, 4h is better in range weeks and when BTC is below its SMA200 (a flush into a down-trend rebounds), but the 4h cells have n of 31 to 38 and SE 0.2 to 0.4 R. This is a lead for a larger-n 4h study, not a result. Regime bear: 0 trades.

## What this does and does not say
- Net of 0.14 % round trip the 1h rule with any single layer has no tested edge; the only sub-sets with positive means are within one SE of zero and unstable across DEV / VALIDATION.
- Not tested: pairs of layers (not run, PRE_REG), funding cost, maker entries, other exits, the trader's discretionary read, a bear phase (none in the window), symbols outside these 10 (survivorship-biased towards survivors).
- Sibling card rederive-rsi-htf-extreme owns the 4h <= 12 / daily-gate variant; not repeated.
