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


## Q4 (2026-11-01 09:54Z): the operator's six hand-drawn lines vs the repo's level rules

Operator lines (TradingView, Bitstamp BTCUSD 15m, top to bottom): 81,888 / 80,842 / 79,688 / 79,131 / 78,644 / 77,937. Binance spot 15m
(this cache) runs +0.10..0.22 % above Bitstamp, so the match is by swing, not by cent. Script: scratch levels_check.py (Krown walk, FORMULAS 18.2 fractals).

| Line | Binance 15m swing | Krown KR-S12 dominant (new low made after it) | C26 pivot +-16 (OURS) | fractal +-3 |
|---|---|---|---|---|
| 81,888 | 10-29 16:00 81,971 | yes (top) | yes | yes |
| 80,842 | 10-29 18:15 80,946 | yes | no (within 16 bars of the top) | yes |
| 79,688 | 10-29 21:15 79,811 | yes | no | no (+-2 yes) |
| 79,131 | 10-29 22:15 79,272 | no: a 1-bar retest high before the crash | no | no |
| 78,644 | 10-30 06:30 78,804 | no: the next new low (10-30 18:45) came after 77,937, not from this high | yes | yes |
| 77,937 | 10-30 15:15 78,110 | yes: the dominant lower high now | yes | yes |

Reading. (1) The lines are the lower highs of the descent: every one is a swing high on 15m, five of six at +-2 or wider. (2) Krown's rule
(KROWN_SETUP_CATALOG.md line 820, KR-L09) has no width: a lower high counts when a new low follows it; that keeps 4 of the 6 and names 77,937 the
dominant one. (3) C26's +-16 (OURS) keeps 3 of 6 and adds three range highs (77.5-77.8k Bitstamp) he does not draw: the two H1 definitions
disagree on the fast part of the descent. Card c26-h1-structural-lower-high: define H1 structurally (SOURCED), run both sets in Phase 3.
(4) The 09:45Z 15m close (78,107 Binance / 77,990 Bitstamp) is the first close above the dominant lower high: Krown calls that the reclaim that
confirms a reversal (higher timeframes outrank it; 4h/1D are still inside the leg down from 81.9k); C26 calls it the H1 take-out in a DOWN regime,
which went back to L1 in 18 of 30 cases in Phase 1 (seen period). Two SOURCED readings of one event point opposite ways; only DEV settles it.
(5) Tom's levels are a different family (FORMULAS 18.4: POC/VAH/VAL anchored at the last meaningful pivots), not swing highs; the Coinglass
panel adds OI rising into the test (97.6K) with CVD flat (-18.8K), which Phase 1 counted as P1_oi_up (no edge found).

<!-- Q5 appended 2026-11-01 12:10Z by phase1_touch_look.py (shots e40e870ab33b, b98031bacd10 CoinGlass 15m; TradingView WT_CROSS_LB shot 11:33Z) -->
## Q5. The touch after the bottom: what the 15m chart showed at the 30 DOWN-high take-outs (design look, n=30)

| take-out (UTC) | H1 | RSI div vs H1 | close > BB up | StochRSI K | wt1 | WT cross dn (h) | OI -1..+4 bars % | CVD impulse at touch | up / down impulses after | first up-impulse (h) | RSI then | single short net, exit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09-23 01:00 | 86718 | no | yes | 99 | 27 | 0.8 | -0.36 | up | 3 / 8 | 1.2 | 57 | +0.63 L1 |
| 09-24 14:15 | 84670 | no | yes | 98 | 50 | 0.5 | -0.28 | - | 1 / 5 | 20.8 | 69 | +0.69 L1 |
| 09-25 11:00 | 84942 | yes 84b | yes | 86 | 43 | 0.8 | -0.66 | up | 0 / 3 | - | - | +0.82 L1 |
| 09-25 11:00 | 84888 | no | yes | 86 | 43 | 0.8 | -0.66 | up | 0 / 3 | - | - | +1.04 L1 |
| 09-30 12:45 | 85159 | no | yes | 95 | 63 | 0.8 | -2.53 | up | 2 / 3 | 19.2 | 36 | -0.02 L1 |
| 09-29 11:45 | 84381 | no | yes | 58 | 49 | 1.8 | -0.07 | - | 2 / 4 | 3.8 | 31 | +0.42 24h |
| 10-01 15:00 | 84420 | yes 122b | exc | 89 | 31 | 0.5 | +0.92 | up | 6 / 7 | 0.0 | 57 | -1.49 stop |
| 10-02 03:00 | 85274 | yes 72b | yes | 91 | 47 | 2.2 | +1.43 | up | 0 / 1 | - | - | +0.71 L1 |
| 10-02 04:15 | 85650 | yes 190b | yes | 97 | 70 | 1.0 | +1.30 | up | 0 / 2 | - | - | +1.20 24h |
| 10-06 09:45 | 86130 | yes 56b | exc | 75 | 30 | 2.5 | +0.31 | - | 5 / 3 | 3.8 | 61 | +0.89 L1 |
| 10-09 11:45 | 83521 | no | yes | 78 | 47 | 1.0 | +0.52 | - | 6 / 2 | 11.0 | 53 | +0.79 L1 |
| 10-09 11:30 | 82776 | no | yes | 49 | 32 | 1.2 | -0.36 | - | 6 / 2 | 11.2 | 53 | -0.50 24h |
| 10-11 15:45 | 83529 | yes 268b | yes | 81 | 62 | 1.2 | -0.22 | up | 4 / 5 | 9.2 | 69 | +0.76 24h |
| 10-12 05:00 | 84199 | yes 53b | yes | 100 | 21 | 1.0 | +0.89 | - | 4 / 5 | 1.8 | 62 | +0.60 L1 |
| 10-13 03:30 | 83148 | no | exc | 99 | 22 | 2.5 | +0.77 | - | 2 / 5 | 22.0 | 48 | -0.97 24h |
| 10-14 03:30 | 83850 | no | yes | 100 | 43 | 1.5 | -0.17 | - | 3 / 6 | 4.5 | 65 | +0.89 L1 |
| 10-16 11:00 | 82634 | no | yes | 86 | 8 | 1.2 | +0.10 | up | 2 / 3 | 6.5 | 45 | +0.57 L1 |
| 10-18 01:30 | 81821 | no | yes | 100 | 40 | 2.8 | -0.63 | up | 9 / 8 | 0.5 | 58 | +0.55 L1 |
| 10-18 01:30 | 81770 | no | yes | 100 | 40 | 2.8 | -0.63 | up | 9 / 8 | 0.5 | 58 | +0.92 L1 |
| 10-19 00:30 | 82295 | yes 88b | no | 96 | 51 | 1.2 | +0.61 | up | 0 / 2 | - | - | +0.52 24h |
| 10-19 07:30 | 82941 | yes 273b | no | 72 | 59 | 0.2 | +0.69 | - | 3 / 5 | 17.2 | 39 | +1.48 24h |
| 10-20 04:15 | 82270 | no | no | 97 | 22 | 1.0 | +0.08 | - | 8 / 3 | 3.2 | 38 | +0.53 L1 |
| 10-21 08:45 | 83439 | yes 103b | exc | 92 | 46 | 1.2 | +0.86 | up | 5 / 15 | 0.0 | 65 | -1.33 stop |
| 10-24 23:30 | 80846 | no | yes | 100 | 43 | 1.5 | -0.55 | - | 1 / 2 | 21.5 | 44 | +0.72 L1 |
| 10-27 21:30 | 81034 | no | yes | 47 | 56 | 1.0 | -0.13 | up | 15 / 1 | 0.0 | 66 | -0.46 24h |
| 10-27 21:30 | 80952 | no | yes | 47 | 56 | 1.0 | -0.13 | up | 14 / 1 | 4.2 | 60 | -1.15 stop |
| 10-27 12:45 | 80388 | no | yes | 100 | 42 | 0.8 | +0.16 | up | 16 / 1 | 0.0 | 69 | -1.13 stop |
| 10-27 21:30 | 80845 | no | yes | 47 | 56 | 1.0 | -0.13 | up | 14 / 1 | 4.2 | 60 | -1.16 stop |
| 10-29 15:45 | 81823 | yes 126b | no | 92 | 69 | 0.5 | -1.51 | - | 0 / 9 | - | - | +1.59 L1 |
| 10-29 15:45 | 81789 | no | no | 92 | 69 | 0.5 | -1.51 | - | 0 / 9 | - | - | +2.43 L1 |

RSI div = excursion-high bar above H1 with lower RSI(14) than the H1 bar, 'Nb' = bars between the two highs; BB = close of the take-out bar above the upper band ('exc' = some bar of the excursion was); impulses counted from the single short's entry (else the take-out) to its exit; OI = Binance USDT-M sum_open_interest, close of the bar before the touch to 1h after.

| factor at the touch | yes: n, reached L1, mean net unit-% | no: n, reached L1, mean net unit-% |
|---|---|---|
| RSI div vs H1 | 11: 5 L1, +0.52 | 19: 12 L1, +0.25 |
| close > BB up at touch | 21: 13 L1, +0.33 | 9: 4 L1, +0.41 |
| close > BB up in excursion | 25: 14 L1, +0.16 | 5: 3 L1, +1.31 |
| StochRSI K >= 80 | 22: 15 L1, +0.46 | 8: 2 L1, +0.04 |
| WT OB (wt1 >= 53) | 9: 3 L1, +0.52 | 21: 14 L1, +0.28 |
| WT cross down <= 2h | 25: 13 L1, +0.34 | 5: 4 L1, +0.42 |
| OI up -1..+4 bars | 13: 6 L1, +0.18 | 17: 11 L1, +0.48 |
| CVD up-impulse at touch | 17: 8 L1, +0.06 | 13: 9 L1, +0.73 |
| CVD up-impulse within 2h after entry | 8: 4 L1, -0.21 | 22: 13 L1, +0.56 |

CVD impulses per session over the whole window (bars, up, down, up per 24h of that session):

| session | bars | up | down | up per session-day |
|---|---|---|---|---|
| ASIA | 3724 | 176 | 195 | 1.32 |
| LONDON | 3436 | 166 | 202 | 1.26 |
| US | 3432 | 236 | 181 | 1.79 |
| LATE | 2112 | 61 | 81 | 0.46 |

RSI(14) 15m at the bar of every up-impulse (operator: the next push comes near the 40 line):

| RSI at up-impulse | count |
|---|---|
| <40 | 66 |
| 40-50 | 97 |
| 50-60 | 160 |
| >=60 | 316 |

Reading (OURS, n=30 take-outs = ~22 distinct touches, 3 same-bar duplicates on 10-27 21:30 and 2 on 09-25 / 10-18 / 10-29):
1. StochRSI K >= 80 at the touch is the one split that moved both counts and money (22 yes: 15 reached L1, +0.46; 8 no: 2, +0.04).
2. RSI(14) bearish divergence vs H1 helped the mean (+0.52 vs +0.25) but 2 of the 4 stops carried one (10-01, 10-21); the bars apart
   (53..273) show no pattern at this n. A 15m close outside the upper band did not discriminate (21 of 30 had it; +0.33 vs +0.41).
3. WaveTrend: the cross down came within 2h in 25 of 30 touches, so it confirms almost every touch and selects nothing; OB (wt1 >= 53)
   at the touch 9 of 30, +0.52 vs +0.28. Compare it in Phase 3 as context (OB yes/no), never as the trigger (C27/C28 said the same).
4. CVD forces: an up-impulse AT the touch (17 of 30) = the short did worse (+0.06 vs +0.73); an up-impulse in the first 2h after entry
   (8 of 30) = -0.21 vs +0.56. The operator's "is CVD still firing" question has a measurable form: no up-impulse in the first 2h.
   Over the window up-impulses come 1.3-1.8 per session-day (US most, LATE 0.46) and 74 % of them at RSI >= 50; only 10 % at RSI < 40,
   so "the next push comes near the 40 line" is not the common case here (first up-impulse after entry: RSI 31..69, median ~57).
5. OI rising into the touch (-1..+4 bars) went with the weaker shorts (+0.18 vs +0.48): OI that keeps climbing through the level is
   the continuation case he described.
Not evidence: SEEN window, the single short's own stop/target, factors read after the fact. They become pre-registered H2 filters
of Phase 3 (DEV 2022-04..2024-06, fee-net, one-bar shift, Holm): StochRSI >= 80, no CVD up-impulse at the touch, OI not rising.


## Q6. Phase 3 DEV: the DOWN-regime fade on two H1 sets, fee-net, with the Q5 filters (card c26-h1-structural-lower-high, 2026-11-01)

Run once, `phase3_dev.py`, DEV only (2022-04-01 .. 2024-06-30; VALIDATION and HOLDOUT bars never loaded, the loader refuses any bar from 2024-07-01).
Data: Binance spot BTCUSDT 1m -> 15m (public klines, `F:/MTS/data/bigtrade/spot_raw`, not committed), OI = USDT-M 5m metrics.
Rule (all OURS unless marked): H1 taken out in a DOWN regime (close before the take-out below the 200-bar mean of 15m closes), short at the first 15m
close back under H1 (next-bar open = shifted, primary), one stop H1 + 1.0 %, target L1, 24h; fee 0.10 % round trip (fees.py, SOURCED), no slippage or funding.
H1 set 1 = C26 pivot +-16 (OURS). H1 set 2 = Krown KR-S12 dominant lower high (principle SOURCED, KROWN_SETUP_CATALOG.md line 820; finder OURS: fractal +-2
FORMULAS 18.2, new low = below the low H rallied from AND a 12-bar record low, fixed once so the operator's six 10-30/31 lines come out as Q4 says: 4 kept, 2 dropped;
`test_phase3_dev.py`). Arms F0..F4c as pre-registered in Q5 (F3 is an exit rule, F4 reads bars after the entry in most trades so F4c is its causal twin).
Stats per distinct take-out bar (highest H1). Base = same exits on 20 random DOWN-regime entries per event, paired, Holm over the 12 arms, power at alpha 0.05/12;
the power gate is MDE (80 %) <= the +0.20 % design effect (OURS); power at the observed effect is printed but is a function of p. Shifted and unshifted entries
give the same numbers because a 15m spot open equals the previous close.

Bars: 81883 15m bars 2022-03-01 .. 2024-06-30 23:45 UTC (spot BTCUSDT, built from 1m; 1 gaps in the 15m series, 1 bars with < 15 minutes); DEV window events: H1 pivot on or after 2022-04-01; OI days missing: none; random-entry pool 39125 DOWN-regime bars.

**C26 pivot +-16 (OURS)**: 595 take-outs (495 distinct bars), DOWN 123 (108 distinct), UP 472 (387 distinct)

| arm | events | distinct bars | traded | mean net % | median | win % | sum % | worst % | mean net % unshifted | base mean % | mean minus base % | p | Holm p | power (observed) | MDE 80 % | power at +0.20 % | read |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F0 | 123 | 108 | 97 | -0.216 | -0.115 | 46 | -21.0 | -1.72 | -0.216 | -0.082 | -0.134 | 0.214 | 1.000 | 0.05 | 0.30 | 0.16 | underpowered, no verdict (MDE 0.30 %) |
| F1 | 77 | 71 | 65 | -0.230 | -0.166 | 45 | -15.0 | -1.52 | -0.230 | -0.096 | -0.135 | 0.299 | 1.000 | 0.03 | 0.36 | 0.09 | underpowered, no verdict (MDE 0.36 %) |
| F2 | 50 | 49 | 45 | -0.327 | -1.119 | 38 | -14.7 | -1.52 | -0.327 | -0.069 | -0.259 | 0.117 | 1.000 | 0.10 | 0.46 | 0.05 | underpowered, no verdict (MDE 0.46 %) |
| F3 | 123 | 108 | 97 | -0.191 | -0.339 | 40 | -18.5 | -1.72 | -0.191 | -0.119 | -0.072 | 0.466 | 1.000 | 0.02 | 0.27 | 0.20 | underpowered, no verdict (MDE 0.27 %) |
| F4 | 78 | 67 | 60 | -0.207 | -0.073 | 48 | -12.4 | -1.72 | -0.207 | -0.074 | -0.134 | 0.352 | 1.000 | 0.03 | 0.40 | 0.07 | underpowered, no verdict (MDE 0.40 %) |
| F4c | 74 | 65 | 65 | -0.131 | -0.066 | 49 | -8.5 | -1.72 | -0.131 | -0.093 | -0.038 | 0.778 | 1.000 | 0.00 | 0.38 | 0.08 | underpowered, no verdict (MDE 0.38 %) |

exits (shifted, distinct): F0: L1 39 / stop 44 / 24h 14; F1: L1 25 / stop 31 / 24h 9; F2: L1 16 / stop 24 / 24h 5; F3: L1 33 / stop 28 / 24h 10 / F3 26; F4: L1 25 / stop 26 / 24h 9; F4c: L1 29 / stop 26 / 24h 10; F4 pre-registered window read bars after the entry in 47 of 60 trades

context (not in the family): F0 in the UP regime, n=342 mean net +0.010 %; WaveTrend at the take-out, DOWN F0 trades: wt1 >= 53 at take-out: n=20, +0.172 %; wt1 < 53 at take-out: n=76, -0.336 %; WT cross down within 2h of the take-out: n=74, -0.091 %; no WT cross down within 2h: n=22, -0.699 %

**Krown dominant lower high (KR-S12)**: 2248 take-outs (1683 distinct bars), DOWN 923 (695 distinct), UP 1325 (988 distinct)

| arm | events | distinct bars | traded | mean net % | median | win % | sum % | worst % | mean net % unshifted | base mean % | mean minus base % | p | Holm p | power (observed) | MDE 80 % | power at +0.20 % | read |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F0 | 923 | 695 | 661 | -0.117 | +0.117 | 57 | -77.1 | -2.11 | -0.117 | -0.094 | -0.023 | 0.516 | 1.000 | 0.01 | 0.10 | 1.00 | powered, no edge vs base (MDE 0.10 %) |
| F1 | 619 | 479 | 456 | -0.146 | +0.104 | 55 | -66.7 | -2.11 | -0.146 | -0.095 | -0.051 | 0.251 | 1.000 | 0.04 | 0.13 | 0.95 | powered, no edge vs base (MDE 0.13 %) |
| F2 | 545 | 461 | 450 | -0.112 | +0.121 | 58 | -50.6 | -1.76 | -0.112 | -0.092 | -0.020 | 0.629 | 1.000 | 0.01 | 0.12 | 0.98 | powered, no edge vs base (MDE 0.12 %) |
| F3 | 923 | 695 | 661 | -0.129 | -0.020 | 49 | -85.3 | -2.11 | -0.129 | -0.093 | -0.036 | 0.270 | 1.000 | 0.04 | 0.09 | 1.00 | powered, no edge vs base (MDE 0.09 %) |
| F4 | 568 | 406 | 389 | -0.117 | +0.084 | 55 | -45.4 | -2.11 | -0.117 | -0.097 | -0.019 | 0.686 | 1.000 | 0.01 | 0.13 | 0.91 | powered, no edge vs base (MDE 0.13 %) |
| F4c | 584 | 429 | 428 | -0.106 | +0.095 | 56 | -45.5 | -2.11 | -0.106 | -0.081 | -0.026 | 0.568 | 1.000 | 0.01 | 0.13 | 0.94 | powered, no edge vs base (MDE 0.13 %) |

exits (shifted, distinct): F0: L1 380 / stop 215 / 24h 56; F1: L1 252 / stop 164 / 24h 36; F2: L1 266 / stop 140 / 24h 38; F3: L1 316 / stop 152 / 24h 45 / F3 138; F4: L1 218 / stop 125 / 24h 40; F4c: L1 243 / stop 136 / 24h 40; F4 pre-registered window read bars after the entry in 320 of 389 trades

context (not in the family): F0 in the UP regime, n=919 mean net -0.098 %; WaveTrend at the take-out, DOWN F0 trades: wt1 >= 53 at take-out: n=45, -0.187 %; wt1 < 53 at take-out: n=613, -0.110 %; WT cross down within 2h of the take-out: n=469, -0.004 %; no WT cross down within 2h: n=189, -0.390 %

Reading (OURS; every number above is a DEV count, nothing else was read):
1. Fee-net the fade earns nothing: 0 of 12 arms have a positive mean net. Krown F0 -0.117 % (n 661 traded, win 57 %, median +0.117 but 215 stops), C26 F0 -0.216 % (n 97, win 46 %).
2. Neither H1 definition beats random DOWN-regime entries with the same exits: mean minus base -0.023 % (Krown F0, p 0.516) and -0.134 % (C26 F0, p 0.214); every Holm p is 1.000
   (smallest raw p 0.117, C26 F2, and that arm is worse than its base).
3. Power: the Krown set is powered (MDE 0.09-0.13 % per trade against +0.20 %; verdict NO for this fade: no edge of about 0.1 % or more over random entries). The C26 set is
   underpowered in all 6 arms (MDE 0.27-0.46 %): no verdict. Only 108 of 495 distinct C26 take-outs fall in the DOWN regime (97 traded), against 695 of 1683 for Krown.
4. No filter rescued it. F1 (StochRSI K >= 80, the Q5 favourite) is worse than F0 in both sets (-0.230 / -0.146); F2 -0.327 / -0.112; F3 (exit at the first CVD up-impulse) lowers the win rate
   (40 % / 49 %) and does not lift the mean (-0.191 / -0.129); F4 read bars after the entry in 47 of 60 (C26) and 320 of 389 (Krown) trades, its causal twin F4c is -0.131 / -0.106.
   The Q5 splits on the 30 SEEN take-outs (K >= 80: +0.46 vs +0.04) did not carry to DEV, as a design look at n=30 should be expected not to.
5. Regime and WaveTrend (context, not in the family): the same fade in the UP regime nets +0.010 % (C26, n 342) and -0.098 % (Krown, n 919), so the DOWN split does not separate for Krown
   and C26 is the reverse of Phase 1's story. WaveTrend: a cross down within 2h of the take-out went with -0.09 % vs -0.70 % (C26) and -0.004 % vs -0.39 % (Krown); that is read
   after the fact (look-ahead) and OB at the take-out is mixed (+0.17 % n 20 vs -0.34 % C26; -0.19 % vs -0.11 % Krown): it is a lead for a new pre-registration, not a finding.
Limits: spot bars, one 15m gap in 27 months, fees only (no slippage, funding, or maker fills), overlapping holds not modelled, one regime definition (a 50h mean is short next to
Phase 1's multi-week DOWN phase), Krown finder parameters set on six hand lines, F0 take-outs not traded (no close back under H1 inside the 24h window, or the window runs past the DEV end): 11 of 108 C26, 34 of 695 Krown.
Re-run: `python phase3_dev.py <repo> <cache> --dev 2022-04-01:2024-06-30 --md out.md --sim-json <card> --registry <csv>`; 12 rows in `TRIAL_REGISTRY_c26_roadmap.csv`
(P3_<set>_<arm>, split DEV); card `sim_desk/results/c26-h1-structural-lower-high.json`.

<!-- Q7 appended 2026-11-01 by phase1_liq_look.py (shot fd1787b08c1b, CoinGlass Legend 15m with Liquidation Heatmap) -->
## Q7. Liquidation bands at the touch: a proxy heatmap, three windows (design look on the SEEN window, not a test)

The operator's ask (11-01): do liquidation levels say where to short if we add this layer, and how are the heatmaps read when
they "develop in different timeframes". No CoinGlass history exists in the repo (liquidation_layer_2026-10-28/README.md:
BANDS_LEDGER has 7 hand-read rows), so `phase1_liq_look.py` builds the same KIND of picture the vendor describes for its
Model 1 (OURS, no claim it matches the vendor's numbers): every 15m rise in Binance USDT-M open interest adds positions at
that bar's close, half long and half short, liquidating at close x (1 -/+ 1/L) for L = 10, 25, 50, 100; 100 USD buckets; a
bucket is cleared the moment a later bar trades through it; a bucket older than the window is dropped. The window IS the
heatmap timeframe: the 24h view holds only yesterday's positions, the 7d view holds the week's. Bars before the take-out only.

| window | strong short band within 0.5 % above H1 (n, mean net) | not (n, mean net) | excursion reached the band (n, L1, mean net, overshoot) | stopped short (n, L1, mean net, overshoot) |
|---|---|---|---|---|
| 24h | 16: +0.22 | 9: +0.62 | 13: 4 L1, -0.10, 1.35 % | 12: 10 L1, +0.88, 0.33 % |
| 72h | 16: +0.46 | 9: +0.21 | 14: 7 L1, +0.24, 1.16 % | 11: 7 L1, +0.52, 0.48 % |
| 7d | 8: +0.72 | 17: +0.20 | 12: 5 L1, +0.15, 1.29 % | 13: 9 L1, +0.57, 0.47 % |

25 distinct take-out bars (the 30 events collapse same-bar duplicates). Base rate: a strong short band within 0.5 % above the
close stood at 10 % of hourly samples over the window; at take-outs it is 64 % (72h), by construction: shorts built under H1
liquidate just above it, so a take-out through H1 is where the band sits. Proxy long bands sit 1.2-4 % under H1 and are never
nearer than L1 (0 of 25 at 72h and 7d, 3 of 25 at 24h); "the trade reached the long band" = it reached L1 first.

Reading:
1. The band above H1 does not say WHERE to short; it says how far the overshoot goes. Touches whose excursion ran into the band
   carry every one of the 4 stops; touches that stopped short of it carried the winners (24h: +0.88 vs -0.10). A 1 % stop above
   H1 sits inside the band's reach.
2. So the testable version of the layer is a sequence, not a level: band above H1 traded through (consumed) -> first close back
   under H1 -> short. On this proxy that is the "reached the band" group, and it is the poorer one with the fixed 1 % stop; the
   question for Phase 3b is whether the stop above the consumed band's top (not H1 + 1 %) turns it around. Not pre-registered in
   Phase 3; a candidate for the next card, with the short-window (24h) proxy, since that view separated the two groups most.
3. Timeframes: the 24h view answers "what is above the next hour", the 7d view "what is the week's magnet". The 24h split is the
   sharpest here; the 7d view thins the "band within 0.5 %" group to 8. For a backtest the window is a parameter (24h first).
4. The vendor's bands end where price traded through them; so do these. A band that "held" is one the excursion did not reach,
   which is only known after the excursion. Any live read of the heatmap is therefore a read of the overshoot risk, not a trigger.
5. Gap that makes this a proxy, not the layer: the vendor's leverage mix and exchange coverage are NOT_IN_DATA (A_liquidation.md);
   recorded Binance forceOrder prints (BinanceLiquidationAccumulator in the Java feed) are a lower bound of real liquidations and
   are not yet in the research cache. Pasted heatmap bands go on in BANDS_LEDGER.csv per the 10-28 pre-registered forward test.

Not evidence: SEEN window, one proxy, factors read after the fact, n = 25.

<!-- Q8 appended 2026-11-01 by phase1_cvd_div.py (CoinGlass CVD page shots f0c96ab4648f 8a0a7c7df46c 66e5bd1cba25 e6ffb95a80ef 2075e46d6f75 01954b8d332f) -->
## Q8. CVD divergence as the CoinGlass CVD page draws it, with Malkan's 12-18 candle rule (design look, OURS)

The operator's ask (11-01): the CoinGlass CVD page marks "Bear div / Bull div" on every bar size and prints a hit rate at
+12 bars (its panel today: 1D 58 % of 31, 1H 58 % of 19, 30m 21 % of 14, 15m 35 % of 20, 5m 71 % of 21, 1m 53 % of 17);
do we have a match, given Malkan's rule that the two legs of a divergence are at most 12-18 candles apart. CVD = the running
sum of taker buy minus taker sell volume; the page's "Futures vs spot" keeps two sums. `phase1_cvd_div.py` rebuilds the shape
on our data (Binance SPOT 1m taker delta, not the vendor's 8-market combined CVD): pivot = high above the 3 bars either side,
bear div = two consecutive pivot highs, the later higher in price and lower in CVD, confirmed 3 bars after the second pivot;
bull mirrored; hit = the close 12 bars after confirmation moved the divergence's way. Four months, 2026-06-21 to 11-01.

| bars | legs apart | bear div: n, hit rate at +12, mean move | bull div: n, hit rate, mean move | base rate down / up |
|---|---|---|---|---|
| 1m | 2-18 | 1699: 49 %, -0.00 % | 1655: 50 %, +0.00 % | 50 / 50 |
| 5m | 2-18 | 585: 50 %, -0.01 % | 473: 56 %, +0.03 % | 50 / 50 |
| 15m | 2-18 | 205: 50 %, +0.00 % | 177: 51 %, +0.08 % | 49 / 51 |
| 60m | 2-18 | 43: 40 %, -0.20 % | 50: 64 %, +0.07 % | 47 / 53 |
| 15m | 19-60 | 11: 27 %, -0.24 % | 8: 62 %, -0.02 % | 49 / 51 |

At the 30 DOWN-high take-outs: a 15m CVD bear divergence with legs <= 18 bars was confirmed within 4 bars of the touch on 2
(single short +1.04 mean, 1 L1); the other 28: +0.30 mean, 16 L1. The RSI divergence of Q5 at the touch has legs 53-273 bars
apart, so under Malkan's bar none of the Q5 divergences count.

Reading:
1. The shape alone has no follow-through: every bar size within Malkan's 18 bars sits on the base rate, with n in the hundreds
   to thousands. The vendor's 21-71 % are n = 14-31 readings of the same coin flip.
2. "Match" with the vendor: not testable one-to-one (its CVD is 8 markets combined, its pivot rule is NOT_IN_DATA); the shape is
   the same, and ours finds the vendor's 15m count order of magnitude (20 in 2 days there, 205 in 4 months here at K = 3).
3. CVD divergence is not a C26 trigger candidate. If it enters anywhere it is as a context column beside the touch (Q5 already
   has the CVD impulse columns, which did split the shorts: no up-impulse at/after the touch).
4. The 60m bear row (40 % on 43) and the 15m 19-60 row (27 % on 11) are the only ones away from 50 %, both on the wrong side
   of the base rate and both small n: noise until a VALIDATION read says otherwise.

SOURCED from the page's own article (coinglass.com/cvd, read 2026-11-01 via Chrome, operator's ask "read the latest about the
CoinGlass pages"): CVD = running sum of per-bar taker buy minus taker sell; "Combined" = the markets ticked in the picker, today
8 of 21 (Binance, OKX, Bybit perp + spot, Coinbase spot, Hyperliquid perp), each weighted by its share of volume; divergence =
"price higher high, CVD lower high ... no taker buying behind the rally"; the "Spot vs futures" card says whether a move is
perp-driven (futures CVD up, spot CVD down: "leveraged move that can unwind as fast") or spot-driven. Pivot rule and the +12-bar
scoring: NOT_IN_DATA. How to use it, per the vendor: as a who-pushed read on a move already seen, not as a trigger; our Q5
impulse columns (15m taker delta beyond 1.5 sigma) are the same quantity read per bar instead of cumulated.

Not evidence: SEEN window, OURS pivot rule, spot-only CVD, one +12-bar horizon.

<!-- Q9 appended 2026-11-01 by phase1_fp_look.py (CoinGlass Footprint 4H shots c0a8fc721e58 aggregated 4/4, 82d84b32fe1a Binance perp) -->
## Q9. Footprint at the touch: a taker-delta-per-row proxy over the excursion above H1 (design look, OURS, n=30)

The operator sent the CoinGlass Footprint page (4H, bid x ask cells, imbalance ratio 300 %, volume profile with POC and value
area, signals: imbalance / absorption / unfinished auction) and asked what its "Latest signal: Absorption, Bullish, selling
absorbed at the low, 19d ago (Binance perp) / 23d ago (aggregated)" means. We have no bid x ask per price row; `phase1_fp_look.py`
puts each Binance SPOT 1m bar's taker delta on the 100 USD row of its close over the excursion (take-out bar to the excursion
high) and reads the top quarter of that range the way the page reads a bar's top: who won the auction there, how much volume
stacked there, where the POC sits, whether any top row has taker sells >= 3 x taker buys.

| footprint fact over the excursion | yes: n, reached L1, mean net unit-% | no: n, reached L1, mean net unit-% |
|---|---|---|
| top-quarter delta negative (sellers won the high) | 1: 0 L1, -1.33 | 29: 17 L1, +0.41 |
| top-quarter volume share >= 35 % (stacked top) | 6: 5 L1, +0.45 | 24: 12 L1, +0.33 |
| POC in the lower half (top rejected) | 18: 9 L1, +0.41 | 12: 8 L1, +0.26 |
| a sell-imbalance row at the top (sells >= 3 x buys) | 0 | 30: 17 L1, +0.35 |

Reading:
1. The take-out through H1 is taker buying by definition: 29 of 30 excursions have buyers winning the top quarter, and no top
   row ever shows the page's 300 % sell imbalance. The footprint cannot tell the 17 winners from the 4 stops at the touch.
2. "Absorption, bullish, selling absorbed at the low" is the page's BOTTOM signal: a 4H bar where heavy taker selling at the
   bar's low did not push price lower. Its last firing was 19 days ago on Binance perp (about 10-13) and 23 days ago on the
   aggregated set (about 10-09), both before the 82k top and the 10-30 drop: a stale read, and the detector printed nothing
   through the whole fall (no absorption = sellers were not met). The two dates differ because the detector runs per data set.
3. A stacked top (6 touches, 5 reached L1) is the only footprint fact leaning the short's way; n = 6, noise until Phase 3b.
4. Aggregated (4 markets) vs Binance perp: same shape, twice the volume, POC 77,600 vs 77,800. For a backtest the per-exchange
   taker data is what exists (Binance spot/perp 1m); the aggregated footprint is a vendor view with no history in the repo.

Not evidence: SEEN window, spot-only taker delta at 1m resolution instead of bid x ask per row, n = 30.

<!-- Q10 appended 2026-11-01 by phase1_dist_look.py (operator: "keep in mind the probability distribution layer to find entries and exits") -->
## Q10. The probability-distribution layer on the C26 event: quantiles of the path around the take-out (design look, OURS, n=30)

The operator's standing layer (research/prob_dist_layer_brief_2026-10-16/BRIEF.md, design D2 "outcome-after-event table";
backtest/prob_table.py exists but never produced an evidence run) applied to the one event this folder studies: the DOWN-high
take-out. Instead of the fixed stop 1 % / target L1 of Q3, read what price did off its own quantiles, all in % of H1:

| quantity | p25 | p50 | p75 | p90 |
|---|---|---|---|---|
| overshoot above H1 before the reclaim | 0.13 | 0.33 | 0.53 | 1.07 |
| 15m bars to the first close back under H1 | 0 | 1 | 4 | 42 |
| MAE after entry: highest high above the entry close within 96 bars | 0.25 | 0.71 | 1.08 | 1.67 |
| MFE after entry: deepest low under the entry close within 96 bars | 0.91 | 1.50 | 2.04 | 3.68 |
| L1 below the entry close | 0.80 | 1.01 | 1.55 | 2.48 |

All 30 take-outs closed back under H1 inside the hold. Stop x target grid read off those quantiles, fee-net (0.10 % per round trip):

| stop (MAE quantile) | target (MFE quantile) | exits tgt / 24h / stop | mean net % | sum | worst |
|---|---|---|---|---|---|
| 0.71 (p50) | 0.91 (p25) | 16 / 1 / 13 | +0.10 | +2.95 | -0.81 |
| 0.71 | 1.50 (p50) | 12 / 3 / 15 | +0.21 | +6.29 | -0.81 |
| 1.00 (Q3 stop) | 0.91 | 20 / 2 / 8 | +0.25 | +7.42 | -1.10 |
| 1.00 | 1.50 | 14 / 5 / 11 | +0.31 | +9.44 | -1.10 |
| 1.08 (p75) | 2.04 (p75) | 8 / 13 / 9 | +0.33 | +9.99 | -1.18 |
| 1.67 (p90) | 1.50 | 14 / 13 / 3 | +0.37 | +11.06 | -1.77 |
| 1.67 | 2.04 | 8 / 19 / 3 | +0.39 | +11.56 | -1.77 |

Reading:
1. The grid is flat: every stop x target pair lands between +0.10 and +0.39 mean net. The shape of the exit does not make the
   trade; the small drift after the reclaim does. A distribution layer's first job here is to say exactly that, and it does.
2. Entry: half the reclaims come on the take-out bar or the next (p50 wait 1 bar) with a 0.33 % overshoot; the slow tenth
   (p90 42 bars, 1.07 % overshoot) is the Q7 band-overshoot case. Legs above H1 beyond 0.5 % fill on one touch in four.
3. Exit: MFE p50 1.50 % against MAE p50 0.71 % is a 2:1 shape before fees, but the median L1 sits at 1.01 %, so L1 as target
   takes the first half of the available move. Wider stops win by holding to 24h (13-19 of 30 exits), i.e. by drift, not by
   a better exit.
4. These quantiles are fitted on the same 30 events they are scored on. The right use: freeze stop/target quantiles from SEEN
   (Phase 2 card) and score them once on the VALIDATION window; a grid searched on VALIDATION is the overfit the roadmap forbids.

Not evidence: SEEN window, n = 30, quantiles and scoring on the same events.
