**Verdict: UNDERPOWERED. NKN-01 convergence breakout produced 0 DEV and 0 VAL episodes in all three PRIMARY cells (P1, P2, P3) on 20 coins; the kill rule "fewer than 50 total P1 episodes" applies: the rule is NOT TESTABLE on this universe as pre-registered. No edge claim, no failure claim.**

Rule: NKN-01 (video 5GZIshXnxW8), design frozen in PRE_REG.md (commit b1b4fa273, before any run). Run: `study.py run`, results.json (code commit b1b4fa273, head 22557eef7; study.py unchanged since b1b4fa273). Tests 34 passed in 14 s, prereg lint 0 offenders.

Regime mix: DEV (signal bar before 2024-01-01, 20720 coin-days) UP 27.5% / DOWN 35.1% / RANGE 37.4% (mixed). VAL (20940 coin-days) UP 24.8% / DOWN 35.1% / RANGE 40.1% (mixed). BTC cycle DEV: CAPITULATION 3.3, MARKDOWN 30.0, RELIEF 8.1, ACCUM-RANGE 17.0, MARKUP 26.1, DISTRIBUTION 15.5. VAL: 0.6 / 18.8 / 3.3 / 14.9 / 30.7 / 31.7. BTC above SMA200: DEV 47.6%, VAL 61.7%.

Today's state (PRE_REG): CBP lean bearish and BTC cycle MARKDOWN, so the primary cell is out of phase; no live or forward trading from this study.

## PRIMARY table (daily, long, coin phase RANGE x BTC cycle ACCUM-RANGE, level type = lowest low of 12 closed weeks, at-level within 1.0 ATR_D; context conditions: 3% stack width, fall shape 10 bars, fall depth 50 bars / 1.5 ATR, two closes above stack: all OURS, idea SOURCED 5GZIshXnxW8 00:06:03 / 00:13:58; crypto translation: BTC cycle label as label, gap and expiry dropped, funding in V2 only)
| cell | layer agreement | tf | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | V0 rule alone | 1d | long | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1.0 | UNDERPOWERED |
| P2 | V1 (+WaveTrend) | 1d | long | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1.0 | UNDERPOWERED |
| P3 | V2 (+funding) | 1d | long | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1.0 | UNDERPOWERED |

There is no best primary cell: no primary trade exists. V1/V2 removal counts are 0 because V0 is empty. At-level share of all RANGE x ACCUM-RANGE signals: DEV 0 of 5 (all 5 are away-from-level), VAL 0 of 0.

## CONTROL table (descriptive, never pooled with primary, cannot make anything PASS; net R at 12 bp)
| cell | what it varies | n DEV | n VAL | DEV gross / net12 / net6 | VAL net12 | note |
|---|---|---|---|---|---|---|
| C1 | RANGE x ACCUM-RANGE, AWAY from level (level comparison) | 5 | 0 | +0.209 / +0.188 / +0.199, win 60% | n/a | at-level 0 vs away 5: level comparison cannot be made |
| C2 | RANGE x MARKUP, at level | 1 | 1 | +3.112 / +3.102 | -1.039 | one trade each, no inference |
| C3 | DOWN x MARKDOWN, at level (falling knife) | 0 | 0 | n/a | n/a | |
| C4 | UP x any label, at level | 1 | 0 | +0.602 / +0.581 | n/a | one trade, label MARKUP |
| C5 | RANGE x CAPITULATION/RELIEF | 0 | 0 | n/a | n/a | |
| C6 | RANGE x ACCUM-RANGE, 4h (stack 1.5%, R floor 1.2%) | 0 | 0 | n/a | n/a | fresh-holdout coins: 1 VAL trade, net12 +1.133 (descriptive, n=1) |
| C7 | mirrored short, DOWN x MARKDOWN | 0 | 0 | n/a | n/a | |
| C8 | + BTC close > SMA20 and SMA50 | 0 | 0 | n/a | n/a | |
| C9 | limit at SMA20 within 5 bars | 0 | 0 | n/a | n/a | |
| C10 | stack width 5% power check | 0 | 0 | n/a | n/a | even a 5% stack gives 0 episodes in this cell |

Every control has n < 100 (largest 5): no control supports any statement. Placebo rows are in results.json; they are only meaningful for n >= 1 and none is interpretable here.

**Total cells tried: 13. Primary cells: 3.** (15m, 1h, native weekly and monthly rows were not implemented, see PRE_REG "Design items not implemented".)

## What this says, and does not say
- The conjunction (tight EMA20/50/100/200 stack after a fall, two closes above it, coin in RANGE, BTC in ACCUM-RANGE) essentially does not occur on daily bars of 20 spot coins from 2021-03: 5 DEV and 0 VAL episodes even before the at-level condition. The context-conditioned version of the rule cannot be evaluated on this data; this is a power finding about the rule and cell definition, not evidence for or against the rule.
- Nothing was loosened after seeing counts (that would be tuning). Possible forward steps, each a new pre-registration and not done here: lower timeframes with their own source (15m/1h stacks), more coins, or a looser stack pre-declared in advance.
- Gross R about zero across earlier NK rows is the standing prior; this study adds no information against it.

## Provenance
Read-only `F:/MTS/data_cache/binance_spot/<SYM>USDT_15m.npz` (20 gated coins, key `t` for BTC ETH BNB XRP ADA SOL and `ts` for the rest, exactly one asserted, strictly increasing, step a multiple of 15 min), all coins 2019-2021 start to 2026-11-13. Fresh holdout (8 coins, 5m files `binance_fresh/nk5_nyasia`): AAVE ENJ GRT HBAR MANA SAND THETA XTZ, VAL period only, descriptive. Daily and 4h bars bucketed from the ONE 15m (or 5m) source per coin. Per-file n, first/last timestamp (ms, UTC), step, gap events are in results.json `provenance` (28 files, 454 intraday exchange gap events in total, counted, not filled). BTC cycle: `F:/MTS/data_cache/mts_brains/phase_daily.csv` (shared file; final provisional row dropped). Funding: `binance_futures/nkp1/<SYM>_funding.csv` (17 coins; ALGO, FIL, NEAR NO-DATA for V2). Nothing fetched, nothing written into existing cache folders.

## Deviations
- None to cells, parameters or gates. A previous builder was stopped mid-way: its committed PRE_REG, study.py, test_study.py (b1b4fa273) and counts.json (22557eef7) were verified against the frozen design and kept. A stray untracked results.json from that builder was inspected, found to come from the committed code (prereg_code_commit b1b4fa273) with zero primary episodes, and is kept as the run output.
- Frozen-design deviations already stated in PRE_REG: 4h R floor 1.2%, 15m/1h/weekly rows not run, coin-phase slope definition OURS, 8 not 10 fresh coins.

## Parameter labels
See PRE_REG.md "Parameters (SOURCED / OURS)": stack lengths, widths, fall shape/depth, coin phase, BTC cycle, level (12 weeks, 1.0 ATR_D), R floors, 2R half-exit, WT1 > WT2, funding 0.03% are OURS; stop under lowest EMA, trail, two-close exit/trigger idea SOURCED (5GZIshXnxW8, a8RP5ftOfGo 00:08:50, IjU9PpqvrI8 00:14:58); +53 SOURCED in the WaveTrend module. No grid, no OURS parameter called NK's.
