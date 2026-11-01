# C26 Candidate C, measure first: the range above a taken high and the divergence legs inside it (Lab_Guy, 2026-11-01)

Operator 2026-11-01: a martingale of shorts inside a range above the taken high, legs on RSI divergence on 1m / 2m / 3m / 5m, no per-leg stop inside
the range. Before any rule is frozen: how wide is that range, how often does price leave it, and how many divergence legs would it have carried?
Design window (SEEN, never a test): Binance spot 15m events from `phase1_recent.py`, 1m bars 2026-06-21 .. 11-01 07:44Z. Script `phase1_range.py`,
simulator card `c26-range-ladder`. All numbers OURS.

## Reading
1. The range exists only against the trend. DOWN highs (n=30): 60 % came back to L1 within 24h; those went 0.37 % (median) / 0.64 % (80th pct)
   beyond H1 first, the widest 2.28 %. The 40 % that did not come back ran 1.06 % (median) in the 24h. UP highs: 38 % came back and the rest ran
   1.76 % median, 3.85 % at the 80th pct: no range to lean on there. Lows mirror it (DOWN lows came back 32 %, UP lows 41 %).
2. Range top X for DOWN highs is a trade-off, not a free lunch: X = 1.0 % keeps 21/30 inside and 16 of those reach L1 (76 %), 9 stop out (2 of them
   would have come back). X = 0.65 %: 17 inside (15 reach L1), 13 stopped (3 false). Below 0.5 % the ladder is stopped more often than not.
   A break of the range is therefore the 30-45 % case at any X a ladder can afford, and it hits the biggest stack.
3. The 15m close back under H1 (Candidate A's entry) comes after a 0.33 % median / 0.58 % 80th-pct excursion in DOWN highs: a single short at that
   close sells about 0.3 % below the extreme. The ladder's only advantage over it is a better average entry, bought with size into the breaks.
4. Divergence legs are not scarce: 83-96 % of DOWN-high take-outs had a 1m-5m bearish divergence inside the window, median 8-16 signals, the first
   12-63 min after the break and 0.14-0.24 % above H1. "One leg per divergence" is fully loaded within the first hour on any of the four timeframes,
   so the leg count and spacing must be fixed by rule, not by the indicator. The divergence does not pick the events that come back (17/29 with a
   signal vs 18/30 overall). This matches the repo: 1m-5m divergence shorts net about minus the fee (T089/T091, n 29k on 1m); C30 bearish shorts lose
   62 of 65 cells; RSI divergence at H1 did not make the level hold (PHASE1_RECENT.md).
5. What this leaves as the edge candidate: the STATE (a held high taken in a DOWN regime reverses; median -0.94 % 24h later, back to L1 60 %), not the
   trigger (divergence) and not the structure (martingale). Three ladders in the repo tested negative (eur_low_us_sweep 1-1-2-3, levels_ladder,
   ladder_dev). A ladder can only pay if the single short in the same state has gross edge; it reshapes that edge (higher win rate, fatter tail).
6. Limits: n=30 DOWN highs over 4 months; spot bars; the regime split is by eye (one top). Nothing here is a verdict; Phase 2 freezes, DEV scores.

## Q1a. How far beyond H1 before it came back (take-outs, 24h window, bars to 2026-11-01 07:45)

| group | take-outs | back to L1 <=24h | excursion of those that came back: median / 80th / max | excursion of those that did not (24h): median / 80th | excursion before the 15m close back under H1: median / 80th | time to the extreme (median, came back) |
|---|---|---|---|---|---|---|
| UP highs | 63 | 24 (38 %) | 0.51 / 0.85 / 1.59 | 1.76 / 3.85 | 0.28 / 0.74 | 0.8 h |
| UP lows | 60 | 25 (41 %) | 0.52 / 1.23 / 2.05 | 1.41 / 2.41 | 0.21 / 0.55 | 0.8 h |
| DOWN highs | 30 | 18 (60 %) | 0.37 / 0.64 / 2.28 | 1.06 / 1.23 | 0.33 / 0.58 | 1.0 h |
| DOWN lows | 34 | 11 (32 %) | 0.75 / 1.11 / 2.69 | 1.52 / 2.63 | 0.24 / 0.57 | 0.5 h |

## Q1b. Range top X: what a ladder with its one stop at H1 + X would meet

| group | range top X | stopped out (excursion > X) | ...of which came back to L1 anyway (false stops) | not stopped: back to L1 / n |
|---|---|---|---|---|
| UP highs | 0.30 % | 53/63 (84 %) | 14 | 10/10 |
| UP highs | 0.50 % | 49/63 (77 %) | 12 | 12/14 |
| UP highs | 0.65 % | 41/63 (65 %) | 7 | 17/22 |
| UP highs | 0.80 % | 37/63 (58 %) | 6 | 18/26 |
| UP highs | 1.00 % | 33/63 (52 %) | 4 | 20/30 |
| UP highs | 1.50 % | 24/63 (38 %) | 1 | 23/39 |
| UP highs | 2.00 % | 17/63 (26 %) | 0 | 24/46 |
| UP lows | 0.30 % | 51/60 (85 %) | 17 | 8/9 |
| UP lows | 0.50 % | 47/60 (78 %) | 14 | 11/13 |
| UP lows | 0.65 % | 43/60 (71 %) | 10 | 15/17 |
| UP lows | 0.80 % | 42/60 (70 %) | 10 | 15/18 |
| UP lows | 1.00 % | 36/60 (60 %) | 8 | 17/24 |
| UP lows | 1.50 % | 20/60 (33 %) | 4 | 21/40 |
| UP lows | 2.00 % | 11/60 (18 %) | 1 | 24/49 |
| DOWN highs | 0.30 % | 22/30 (73 %) | 12 | 6/8 |
| DOWN highs | 0.50 % | 17/30 (56 %) | 7 | 11/13 |
| DOWN highs | 0.65 % | 13/30 (43 %) | 3 | 15/17 |
| DOWN highs | 0.80 % | 12/30 (40 %) | 2 | 16/18 |
| DOWN highs | 1.00 % | 9/30 (30 %) | 2 | 16/21 |
| DOWN highs | 1.50 % | 5/30 (16 %) | 2 | 16/25 |
| DOWN highs | 2.00 % | 2/30 (6 %) | 1 | 17/28 |
| DOWN lows | 0.30 % | 27/34 (79 %) | 7 | 4/7 |
| DOWN lows | 0.50 % | 23/34 (67 %) | 6 | 5/11 |
| DOWN lows | 0.65 % | 23/34 (67 %) | 6 | 5/11 |
| DOWN lows | 0.80 % | 19/34 (55 %) | 4 | 7/15 |
| DOWN lows | 1.00 % | 17/34 (50 %) | 3 | 8/17 |
| DOWN lows | 1.50 % | 14/34 (41 %) | 2 | 9/20 |
| DOWN lows | 2.00 % | 12/34 (35 %) | 2 | 9/22 |

## Q2. RSI(14) bearish-divergence legs above H1 between the take-out and the exit (1m bars 2026-06-21 .. 2026-11-01 07:44)

| group | TF | take-outs with >= 1 signal | signals per take-out: median / max | first signal after the break (median) | first signal above H1: median / 80th | with a signal: back to L1 / n |
|---|---|---|---|---|---|---|
| UP highs | 1m | 60/63 (95 %) | 41.00 / 111 | 16 min | 0.20 % / 0.41 % | 21/60 |
| UP highs | 2m | 60/63 (95 %) | 21.00 / 50 | 30 min | 0.30 % / 0.56 % | 21/60 |
| UP highs | 3m | 60/63 (95 %) | 15.00 / 36 | 50 min | 0.38 % / 0.69 % | 21/60 |
| UP highs | 5m | 60/63 (95 %) | 10.50 / 25 | 44 min | 0.30 % / 0.73 % | 21/60 |
| UP lows | 1m | 52/60 (86 %) | 47.50 / 105 | 14 min | 0.19 % / 0.40 % | 17/52 |
| UP lows | 2m | 56/60 (93 %) | 22.00 / 45 | 28 min | 0.23 % / 0.41 % | 21/56 |
| UP lows | 3m | 57/60 (95 %) | 15.00 / 27 | 44 min | 0.27 % / 0.63 % | 22/57 |
| UP lows | 5m | 52/60 (86 %) | 9.50 / 20 | 42 min | 0.28 % / 0.64 % | 17/52 |
| DOWN highs | 1m | 29/30 (96 %) | 16.00 / 76 | 12 min | 0.14 % / 0.37 % | 17/29 |
| DOWN highs | 2m | 29/30 (96 %) | 12.00 / 38 | 25 min | 0.14 % / 0.38 % | 17/29 |
| DOWN highs | 3m | 27/30 (90 %) | 11.00 / 27 | 31 min | 0.21 % / 0.39 % | 15/27 |
| DOWN highs | 5m | 25/30 (83 %) | 8.00 / 18 | 63 min | 0.24 % / 0.43 % | 13/25 |
| DOWN lows | 1m | 30/34 (88 %) | 42.50 / 100 | 16 min | 0.16 % / 0.53 % | 7/30 |
| DOWN lows | 2m | 30/34 (88 %) | 22.50 / 49 | 28 min | 0.23 % / 0.64 % | 7/30 |
| DOWN lows | 3m | 30/34 (88 %) | 13.00 / 33 | 39 min | 0.24 % / 0.64 % | 7/30 |
| DOWN lows | 5m | 29/34 (85 %) | 9.00 / 18 | 68 min | 0.30 % / 0.85 % | 8/29 |

K=3, LB=60 bars, divergence = pivot high above a prior pivot high (<= LB bars back) with a lower RSI; known 3 bars after the pivot.
Window = from the 1m bar that broke H1 to the 15m bar that reached L1, else 24h. cut = exit beyond the data end, excluded (none here).

## Q3. Ladder shapes on the DOWN-high take-outs (design look, gross arithmetic, n=30; `phase1_ladder_look.py`)

Operator 2026-11-01 (chat): "do a martingale in the first range, then continue in the 1 % range and 1.5 %: a martingale inside a martingale".
Shapes below sell at fixed prices above H1 (filled when a 15m high reaches the price), one stop for all legs at H1 + X, target = L1 touch,
time = 24h. unit-% = units x move in % of H1, fee 0.10 % per unit per leg (fees.py). The single short enters at the first 15m close back under H1.

| shape | events filled | exits L1 / 24h / stop | mean net unit-% | sum | worst event | mean net per max unit | max units |
|---|---|---|---|---|---|---|---|
| A single short, stop 1.0 | 30/30 | 17 / 8 / 5 | +0.35 | +10.54 | -1.49 | +0.35 | 1 |
| A single short, stop 1.5 | 30/30 | 17 / 10 / 3 | +0.34 | +10.17 | -1.99 | +0.34 | 1 |
| flat 3 legs 1-1-1, stop 1.0 | 30/30 | 16 / 5 / 9 | +0.59 | +17.79 | -2.40 | +0.20 | 3 |
| martingale 1-2-4, stop 1.0 | 30/30 | 16 / 5 / 9 | +1.02 | +30.67 | -4.70 | +0.15 | 7 |
| nested tiers 0.65/1.0/1.5, sizes 1/2/4, stop 1.5 | 30/30 | 16 / 9 / 5 | +0.38 | +11.34 | -10.10 | +0.03 | 14 |
| nested tiers, flat sizes 1/1/1, stop 1.5 | 30/30 | 16 / 9 / 5 | +0.54 | +16.12 | -5.55 | +0.09 | 6 |

Reading (design look, SEEN, n=30; a verdict needs the DEV book run):
1. Every ladder shows more unit-% than the single short only because it carries more units. Per unit of margin the shape must hold, the order
   reverses: single short +0.35, flat 3 legs +0.20, martingale 1-2-4 +0.15, nested flat +0.09, nested martingale +0.03.
2. The nested martingale (operator's shape) puts 14 units behind one stop: it won 16 of 30 but its 5 stops cost -10.1 unit-% each at worst,
   27 times the single short's worst event (-1.49). Its mean per max unit (+0.03) is below the 0.10 % fee of a single leg.
3. Nesting does not change the stop: all legs still leave together at the outer top (1.5 %), and 5 of 30 take-outs went there.
4. Where the edge sits (if anywhere) is the same in every row: 16-17 of 30 reach L1. A ladder changes how much is bet on that count, not the count.
5. Ranking the shapes on n=30 is itself a selection: all six are logged; the DEV book run tests A first, then the ladders against it.

Re-run: `python phase1_range.py <repo> <cache> --until 2026-11-01T07:45 --sim-json sim_desk/results/c26-range-ladder.json` (1m cache from
`fetch_1m.py`, public Binance klines, not committed); `python phase1_ladder_look.py <repo> <cache> --until 2026-11-01T07:45 --card <that card>`.
Looks logged in `TRIAL_REGISTRY_c26_roadmap.csv` (15 rows, count_only / design_gross).
