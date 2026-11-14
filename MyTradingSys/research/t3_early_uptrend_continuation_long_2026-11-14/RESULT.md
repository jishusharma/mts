# RESULT: T3 early-uptrend continuation long, fresh coins (VAL opened once: `t3_study.py --window all --unlock-val`, exit 0)

**Verdict: FAIL (both cells). Cell A FAIL (bars 2,3,4,5,8 breached; n=225 so powered). Cell B FAIL (bars 2,3,4,5,6,8 breached; n=744). No cell passes; nothing here is an edge. DEV looked strong (A +1.90 R, B +1.63 R net) but VAL is zero for A (-0.01 R) and negative for B (-0.20 R): the DEV/VAL sign flip of failure mode 3, on fresh coins.**

Frozen spec: `PRE_REG.md` (unedited). The code ran unchanged after VAL was opened; no crash, no code change. Bar 8 reading (audit m5): code and PRE_REG agree it cannot count as PASS; both cells also breach bars 2-5, so FAIL is unambiguous.

## Bars 1-8 per cell on VAL at 12 bp (RIDE row unless stated)

| Bar | Threshold | Cell A value | A | Cell B value | B |
|---|---|---|---|---|---|
| 1 | n >= 30 and >= 20 distinct entry weeks | 225, 52 | ok | 744, 50 | ok |
| 2 | mean net R > 0 | -0.014 | FAIL | -0.200 | FAIL |
| 3 | EXCESS week-cluster CI low > 0 | -0.323 | FAIL | -0.200 | FAIL |
| 4 | BH q < 0.05 (m=2) | 0.316 | FAIL | 0.316 | FAIL |
| 5 | ex-best-5 mean net R > 0 (CAP3R) | -0.063 | FAIL | -0.181 | FAIL |
| 6 | signal net daily return in position >= basket daily mean | 0.0000, -0.0013 | ok | -0.0030, -0.0013 | FAIL |
| 7 | DEV mean net R > 0 (sign check) | 1.900 | ok | 1.633 | ok |
| 8 | 2024 and 2025 both mean net R > 0 | 0.4592, -0.4578 | FAIL | 0.2225, -0.4583 | FAIL |

Bar 1 values are (n, distinct entry weeks). Bar 6 values are (signal mean net daily return in position, basket mean daily return over VAL UP_E days). Bar 8 values are (2024, 2025) mean net R. Bar 3 value is the EXCESS week-cluster CI low. Bar 4 is the BH q over m = 2 (the same for both cells because the BH step-up takes the cumulative min).

## Core table: n, gross R, fee-net R at 12 bp (6 bp informational), DEV vs VAL

| Window | Cell | Exit | n | weeks | gross R | net R 12bp | 95% CI (week clusters) | p one-sided | net R 6bp | win rate | ex-best-5 net R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV | A | RIDE | 248 | 59 | 2.049 | 1.900 | [0.588, 3.500] | 0.000 | 1.903 | 0.427 | 0.944 |
| DEV | A | CAP3R | 339 | 61 | 0.677 | 0.586 | [0.313, 0.856] | 0.000 | 0.588 | 0.510 | 0.548 |
| DEV | B | RIDE | 416 | 53 | 1.763 | 1.633 | [0.601, 3.043] | 0.000 | 1.635 | 0.387 | 0.937 |
| DEV | B | CAP3R | 506 | 60 | 0.697 | 0.610 | [0.294, 0.954] | 0.000 | 0.612 | 0.522 | 0.585 |
| VAL | A | RIDE | 225 | 52 | 0.010 | -0.014 | [-0.643, 0.648] | 0.563 | -0.010 | 0.267 | -0.259 |
| VAL | A | CAP3R | 261 | 54 | 0.019 | -0.003 | [-0.612, 0.609] | 0.576 | 0.001 | 0.280 | -0.063 |
| VAL | B | RIDE | 744 | 50 | -0.177 | -0.200 | [-0.621, 0.556] | 0.750 | -0.197 | 0.141 | -0.327 |
| VAL | B | CAP3R | 689 | 57 | -0.134 | -0.157 | [-0.607, 0.365] | 0.759 | -0.154 | 0.267 | -0.181 |

Ex-best-5 on CAP3R (bar 5): VAL A -0.063, B -0.181 (both below zero); on RIDE: A -0.259, B -0.327. DEV CAP3R: A 0.548, B 0.585.

## Random same-phase entry baseline (1000 draws, same exit, same costs) and EXCESS

| Window | Cell | Exit | random mean net R | excess | excess 95% CI | excess p | BH q (RIDE) |
|---|---|---|---|---|---|---|---|
| DEV | A | RIDE | 0.890 | 1.010 | [-0.302, 2.610] | 0.085 | 0.085 |
| DEV | A | CAP3R | 0.445 | 0.141 | [-0.132, 0.412] | 0.140 |  |
| DEV | B | RIDE | 0.554 | 1.079 | [0.047, 2.489] | 0.017 | 0.035 |
| DEV | B | CAP3R | 0.395 | 0.214 | [-0.102, 0.559] | 0.097 |  |
| VAL | A | RIDE | -0.321 | 0.307 | [-0.323, 0.969] | 0.291 | 0.316 |
| VAL | A | CAP3R | -0.318 | 0.315 | [-0.294, 0.927] | 0.225 |  |
| VAL | B | RIDE | -0.421 | 0.221 | [-0.200, 0.978] | 0.316 | 0.316 |
| VAL | B | CAP3R | -0.342 | 0.185 | [-0.266, 0.707] | 0.245 |  |

Random longs entered in VAL UP_E lose on this stop and exit (random mean about -0.32 R for A-sized, -0.42 R for B-sized RIDE). Both cells beat random by a positive point estimate (+0.31 R, +0.22 R) but the CIs include zero: 'loses less', not 'wins'.

## Buy-and-hold basket (equal-weight fresh coins, open-to-open, UP_E days) and bar 6

| Window | basket mean daily | UP_E days | A signal net daily in position | B signal net daily in position |
|---|---|---|---|---|
| DEV | 0.00909 | 415 | 0.01783 | 0.01561 |
| VAL | -0.00125 | 410 | 0.00001 | -0.00296 |

VAL: A edges the basket by a hair (+0.00001 vs -0.00125 per day; bar 6 is met only because the basket fell); B is below it (-0.00296).

## By year (RIDE, 12 bp net R)

| Window | Cell | Year | n | mean net R | win rate |
|---|---|---|---|---|---|
| DEV | A | 2020 | 99 | 0.960 | 0.434 |
| DEV | A | 2021 | 149 | 2.524 | 0.423 |
| DEV | B | 2020 | 202 | 0.894 | 0.351 |
| DEV | B | 2021 | 214 | 2.330 | 0.421 |
| VAL | A | 2024 | 109 | 0.459 | 0.376 |
| VAL | A | 2025 | 116 | -0.458 | 0.164 |
| VAL | B | 2024 | 282 | 0.223 | 0.188 |
| VAL | B | 2025 | 462 | -0.458 | 0.113 |

DEV is 2020-2021 only (no 2017 UP_E days: audit m3, BTC SMA200 exists from 2018-03): one bull run. ONE-YEAR flag: VAL max year share A 0.516, B 0.621 (not flagged; limit 85%).

## By symbol (VAL, RIDE, 12 bp net R; n per coin is small, descriptive only)

**Cell A**

| Symbol | n | mean net R | win rate |
|---|---|---|---|
| 1INCH | 6 | 0.27 | 0.33 |
| AAVE | 4 | 1.52 | 0.50 |
| ALGO | 3 | 3.31 | 0.67 |
| ANKR | 6 | -0.52 | 0.33 |
| AXS | 5 | -0.60 | 0.20 |
| BAND | 7 | -0.74 | 0.14 |
| BAT | 8 | -0.33 | 0.12 |
| CELR | 2 | -0.38 | 0.50 |
| CHZ | 3 | 0.03 | 0.33 |
| COMP | 8 | -0.25 | 0.12 |
| CRV | 4 | 2.14 | 0.50 |
| DASH | 7 | 1.25 | 0.29 |
| EGLD | 6 | -0.25 | 0.17 |
| ENJ | 4 | -0.29 | 0.25 |
| EOS | 2 | 3.26 | 1.00 |
| FIL | 3 | -0.28 | 0.33 |
| FTM | 4 | -0.77 | 0.25 |
| FTT#2 | 8 | 0.05 | 0.38 |
| GRT | 6 | -0.77 | 0.00 |
| HBAR | 7 | 2.41 | 0.43 |
| ICX | 6 | -0.40 | 0.33 |
| IOST | 5 | -0.20 | 0.20 |
| IOTA | 6 | 0.88 | 0.33 |
| KAVA | 3 | -0.15 | 0.33 |
| KNC | 5 | -0.02 | 0.20 |
| LUNA#2 | 6 | -0.80 | 0.00 |
| MANA | 5 | -0.04 | 0.40 |
| MATIC | 2 | -1.04 | 0.00 |
| MKR | 6 | -0.01 | 0.67 |
| NEAR | 5 | -0.81 | 0.20 |
| ONE | 6 | -0.18 | 0.17 |
| ONT | 8 | -0.64 | 0.12 |
| QTUM | 6 | -0.63 | 0.17 |
| RUNE | 3 | -0.41 | 0.33 |
| RVN | 5 | -0.20 | 0.40 |
| SAND | 6 | -0.37 | 0.17 |
| SNX | 5 | -0.62 | 0.20 |
| STORJ | 7 | -0.58 | 0.00 |
| SUSHI | 4 | -0.15 | 0.25 |
| THETA | 5 | -0.56 | 0.20 |
| XTZ | 3 | 2.20 | 0.67 |
| YFI | 6 | -0.60 | 0.17 |
| ZIL | 3 | -0.02 | 0.33 |
| ZRX | 6 | -0.35 | 0.33 |

**Cell B**

| Symbol | n | mean net R | win rate |
|---|---|---|---|
| 1INCH | 18 | -0.19 | 0.22 |
| AAVE | 16 | 0.06 | 0.25 |
| ALGO | 17 | 0.30 | 0.12 |
| ANKR | 15 | -0.39 | 0.13 |
| AXS | 17 | -0.43 | 0.06 |
| BAND | 21 | -0.43 | 0.19 |
| BAT | 18 | -0.31 | 0.11 |
| CELR | 18 | -0.36 | 0.06 |
| CHZ | 18 | -0.37 | 0.11 |
| COMP | 21 | -0.23 | 0.10 |
| CRV | 23 | 0.17 | 0.13 |
| DASH | 17 | 0.81 | 0.18 |
| EGLD | 17 | -0.30 | 0.18 |
| ENJ | 19 | -0.44 | 0.16 |
| EOS | 9 | 0.85 | 0.22 |
| FIL | 18 | -0.42 | 0.06 |
| FTM | 7 | -0.14 | 0.14 |
| FTT#2 | 13 | 0.07 | 0.31 |
| GRT | 17 | -0.32 | 0.24 |
| HBAR | 15 | 2.11 | 0.20 |
| ICX | 14 | -0.39 | 0.14 |
| IOST | 19 | -0.51 | 0.11 |
| IOTA | 19 | 0.22 | 0.16 |
| KAVA | 19 | -0.54 | 0.05 |
| KNC | 15 | -0.32 | 0.13 |
| LUNA#2 | 18 | -0.54 | 0.11 |
| MANA | 18 | -0.32 | 0.17 |
| MATIC | 4 | -0.65 | 0.00 |
| MKR | 14 | -0.29 | 0.36 |
| NEAR | 18 | -0.40 | 0.17 |
| OCEAN | 4 | -0.51 | 0.00 |
| OMG | 2 | -0.72 | 0.00 |
| ONE | 18 | -0.30 | 0.11 |
| ONT | 17 | -0.44 | 0.12 |
| QTUM | 17 | -0.44 | 0.12 |
| RUNE | 16 | -0.30 | 0.19 |
| RVN | 20 | -0.59 | 0.05 |
| SAND | 19 | -0.08 | 0.11 |
| SNX | 18 | -0.40 | 0.11 |
| STORJ | 16 | -0.51 | 0.12 |
| SUSHI | 19 | -0.17 | 0.11 |
| THETA | 18 | -0.26 | 0.17 |
| WAVES | 1 | -1.01 | 0.00 |
| XTZ | 18 | 0.03 | 0.17 |
| YFI | 17 | -0.27 | 0.12 |
| ZIL | 18 | -0.37 | 0.06 |
| ZRX | 14 | -0.29 | 0.29 |

## Regime mix

Regime mix: DEV calendar days UP_E 19.7% / other UP 22.2% / MIX 23.7% / DOWN 34.4%; share of signal trades (pooled over cells and all phases, incl. control) UP_E 22.7% / other UP 23.5% / MIX 23.0% / DOWN 30.8%.

Regime mix: VAL calendar days UP_E 39.1% / other UP 19.0% / MIX 15.3% / DOWN 26.7%; share of signal trades (pooled over cells and all phases, incl. control) UP_E 41.8% / other UP 15.0% / MIX 16.5% / DOWN 26.7%.

## Brain-label join (UP_E signals per MTS brain label, informational; RIDE)

| Window | Cell | brain labels (n, share) | cycle state (n) | UP_E and MARKUP subset |
|---|---|---|---|---|
| DEV | A | MARKUP 174 (70%), ACCUM-RANGE 31 (12%), DISTRIBUTION 22 (9%), RELIEF 21 (8%) | BULL 141, BASE 100, BEAR 7 | n 174, mean net R 2.342 |
| DEV | B | MARKUP 229 (55%), ACCUM-RANGE 72 (17%), DISTRIBUTION 70 (17%), RELIEF 43 (10%), CAPITULATION 2 (0%) | BASE 204, BULL 187, BEAR 25 | n 229, mean net R 2.503 |
| VAL | A | MARKUP 120 (53%), DISTRIBUTION 104 (46%), MARKDOWN 1 (0%) | BULL 224, BEAR 1 | n 120, mean net R 0.418 |
| VAL | B | DISTRIBUTION 480 (65%), MARKUP 239 (32%), MARKDOWN 25 (3%) | BULL 692, BASE 27, BEAR 25 | n 239, mean net R 0.480 |

## Control rows (same cells outside UP_E, RIDE, 12 bp)

| Window | Cell | all non-UP_E n | mean net R | CI | UP_L | MIX | DOWN |
|---|---|---|---|---|---|---|---|
| DEV | A | 665 | 0.418 | [-0.002, 0.863] | n 239, 0.17 | n 176, 0.48 | n 250, 0.61 |
| DEV | B | 1602 | 0.230 | [-0.114, 0.619] | n 451, -0.01 | n 499, 0.22 | n 652, 0.40 |
| VAL | A | 376 | 0.078 | [-0.250, 0.462] | n 95, 0.68 | n 93, 0.26 | n 188, -0.32 |
| VAL | B | 975 | 0.017 | [-0.245, 0.316] | n 254, 0.10 | n 290, -0.02 | n 431, -0.01 |

VAL control A is +0.08 R (CI includes zero) against UP_E A -0.01 R: Cell A does not separate UP_E from other phases in VAL. (Controls are expected to show no edge; the DEV controls are positive too, so the DEV result was mostly the bull run, not the UP_E gate.)

## Coins, funding, survivorship handling

- Coins used: 48 symbols (50 segments; re-used tickers LUNA and FTT split into #1 and #2); dropped for under 250 bars: 0 (none). Fetch details in `fetch_report.json`.
- Segments whose archive ended before 2026-11-13: MATIC, EOS, ICX, WAVES, OMG, FTM, MKR, STORJ, LUNA#1, FTT#1, XMR, OCEAN.
- Audit M1 is handled in the code that ran: positions still open at a segment's last bar are force-exited at that close (reason DELIST) instead of dropped. VAL signal trades force-exited: A 1, B 3; random-pool entries force-exited: 90 (RIDE) and 112 (CAP3R); dropped at the global end: 0. DEV: 0.
- Funding fallback (flat 1 bp per 8 h paid by longs; trades with at least one flat day): VAL A RIDE 12 of 225, B RIDE 23 of 744; DEV A RIDE 58 of 248, B RIDE 88 of 416. Real perp prints cover the rest.
- Costs: 12 bp = 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13, imported from `fees.py` (0.0012); the 6 bp row is informational only and never enters a verdict.

## prereg_gate output (run before the freeze; BLOCK reported, run was ordered anyway)

```
cmd: python scripts/dev/prereg_gate.py --n 118 --sd 5.79 --cost 0.01 --m 2 --sd-source F:/MTS/data_cache/binance/combo-edge-miner-1114/dev_cells.csv:206
inputs: miner Cell A (ADX_DI+VOLX, 1d, long, UP_E, RIDE): DEV n=118, days=87 (day clusters), se12=0.6207 R (day-cluster SE of the mean, miner.py cluster_stats L508-518); sd = se12*sqrt(days) = 5.79 R (approximation of per-trade sd; the csv holds no per-trade sd); cost 0.01 R = feeR 0.0070 rounded up
n 118 sd 5.79 m 2 z_holm 2.241 MDE 1.642 R + cost 0.01 = 1.652 vs max plausible gross 0.3; n needed 3785
BLOCK: do not freeze (write BLOCKED.md with these numbers)
exit code: 1
```

The gate said Cell A at n=118 needed a minimum detectable effect of about 1.65 R against a plausible gross of 0.3 R. At VAL n=225 and 52 weeks the realised CI half-width is about 0.65 R, still wider than any plausible edge. The FAIL rests on the point estimates (mean near zero or negative), not on power; a pass would not have been believable either.

## Recompute and audit outcome

- RECOMPUTE.md (second agent, raw klines and FORMULAS only): MATCH on 3 dated trades plus 2 extras; largest difference 1.6e-15 R.
- AUDIT.md (third agent, VAL unopened): no look-ahead, no fee error, no blocker; two MAJOR items (M1 delisted-open trades dropped; M2 weak tests) and minors m1-m7. M1 is reflected in the run (DELIST forced exits, counted above). Whether the M2 test additions and minors m2, m4, m6, m7 landed in the committed files was not re-verified by the runner; the verdict does not depend on them.
- Audit m3 (no 2017 UP_E days) and m4 (weekly clusters are anti-conservative for 60-day holds, so the CIs here are if anything too narrow, which strengthens the FAIL on bars 3-4) are stated here.

## Honest limits

- Survivorship: hand-picked 2026 candidate list; coins never on it are absent; delisted coins are included only where the archive has them.
- Spot is a proxy for perp prices; funding from perp prints with a flat 1 bp / 8 h fallback.
- One VAL regime sequence (UP_E 2024-04-20..2025-10-12, one cycle): 2024 positive and 2025 negative in both cells, a single episode.
- 20-week power: VAL has 50-52 distinct entry weeks and a per-trade spread of about 5 R; a CI half-width near 0.65 R cannot resolve effects under about 0.5 R. Adjacent weekly clusters overlap on 60-day holds (m4).
- DEV is a single 2020-2021 bull run; its +1.6 to +1.9 R is carried by a handful of 10-15 R winners (DEV A RIDE ex-best-5 is +0.94 R) and should not have been read as a target.
- Two cells, no tuning; Cell A was picked from the miner's DEV table on 20 other coins (DEV-only selection).

## Next variant (one line, not run)

Cell A with the entry gated on the MTS brain label MARKUP (VAL subset n 120, 0.42 R net, but chosen after seeing VAL, so it needs a fresh forward test), because DISTRIBUTION-labelled UP_E days look like what turned 2025 negative.
