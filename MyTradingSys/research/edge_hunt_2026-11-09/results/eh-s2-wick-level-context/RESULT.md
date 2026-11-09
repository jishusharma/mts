Verdict: T09=FAIL (DEV n=41, mean net R -0.581, SE 0.235, CI -1.042..-0.120, below the MDE 0.658; VALIDATION not read), T10=FAIL (DEV n=47, mean net R -0.804, SE 0.215, CI -1.226..-0.382, below the MDE 0.602; VALIDATION not read)

# eh-s2-wick-level-context: wick at an HTF level with the whole context (T09 long, T10 short)

## Answer in plain words
The context gate as frozen does not make wicks buy-able. On BTCUSDT USD-M 15m, DEV 2019-12-31 .. 2024-06-30, a first-touch sweep of a prior-week low, prior-month low or unbroken daily pivot low (and the mirror at highs), with a reclaim inside 3 bars, a 3x volume bar and no knife, entered by a maker limit at the level, loses about 0.6 R (long) and 0.8 R (short) per filled trade after fees. It loses before fees too (gross -0.29 R long, -0.46 R short). The sweep extreme is almost always retaken after the limit fills: 27 of 41 long fills and 32 of 47 short fills hit the stop, 10 and 12 went to break-even, and only 2 and 2 reached the next-level target (about 11 R away on median; the target hit rate was 5 % and 4 %). Both DEV 95 % intervals lie wholly below zero and their upper bounds are under the 80 %-power MDE, so this is a power-adequate FAIL for this exact rule, not "too few trades". n is small (41 and 47), so a smaller edge than the MDE (about 0.6 R) is not excluded by this test, but none is suggested.

Two things worth knowing for the next design:
- The effort gate does nothing here. Sweeping a weekly or monthly extreme is itself a high-volume bar: the median sweep volume is 9.5x the prior-96-bar median, and the 3x gate removed only 3 of 97 long events and 4 of 111 short events. The Friday case (12x) is typical of these sweeps, not special.
- The maker limit fills only about 55 % of the placed orders (long 41 of 74, short 47 of 82), and the fills are the adverse ones: price had to trade back through the level, and then the stop at the sweep extreme was 44 bps away on median (2.6 to 209 bps). Fees in regime B still cost 0.28 R (long) and 0.34 R (short) on average because many stops are tight; regime A (taker both legs) costs 0.57 and 0.70 R.

Not tested here (outside the frozen rules): a stop beyond the sweep extreme with a buffer, a limit placed below the level, a target nearer than 2.5 R, or entering on the reclaim close. No parameter was changed after the count pass.

Next: END. Both trials FAIL on DEV; no VALIDATION read was made (the screen was not passed), no testnet-forward card is filed. HOLDOUT (2025-07+) was never loaded.

## Context
- Regime: none as a gate (the rule fires in every regime); report-only research_kit.regime_tag per trade (table below).
- Phase: first-touch wick sweep and reclaim (tf_break class W1, range-type); not a break-and-hold.
- Session: none as a gate; exploratory by UTC 4h block of the sweep bar (table below).
- Entry: retest of the swept level, maker limit at the level, placed at the reclaim close, live 4 bars, strict fill.

Regime mix: 234 weeks (DEV, 2020-01-06 .. 2024-06-30): bull 64 (27%) | bear 0 (0%) | range 170 (73%) | n/a 0 (0%) (research_kit.regime_tag; it has no bear weeks in this window, so a bear split is NOT_IN_DATA)

## Data and run
- 15m futures klines 2019-12-31 00:00 .. 2024-06-30 23:45 UTC (157,824 bars, cached outside the repo). The monthly futures archive starts 2020-01 (the 2019-09..2019-12 monthly files 404; only 2019-12-31 has a daily file). Funding from the archive from 2020-01 (none before; there is no earlier data anyway). Regime tag warm-up from spot 1d (2017-08 on, before 2024-07 only).
- HOLDOUT never loaded; VALIDATION never loaded (no trial passed the DEV screen). The loader refuses HOLDOUT and any bar at/after the split end (test_loader_refuses_bars_past_the_split_end_and_the_holdout).
- The count pass (run before DEV) printed, besides the counts, the exit-kind tally of the filled trades: that is outcome information seen before the DEV table. Nothing was changed in response (PRE_REG and code are frozen at commit 7c381503d; the one later code change was the sys.path line for research_kit, and removing an empty write).
- Failing test run (before wick_context.py existed): `1 error in 1.89s` (collection error, module missing). After the code: `32 passed in 3.83s`.

## T09 and T10 primary (DEV, regime B, volume gate, funding included)
| Trial | n | hit (net R > 0) | mean gross R | mean fee_r | mean funding R | mean net R | SE (UTC day) | 95 % CI | MDE 80 % | screen |
|---|---|---|---|---|---|---|---|---|---|---|
| T09 long | 41 | 9.8 % | -0.292 | 0.281 | 0.008 | -0.581 | 0.235 | -1.042 .. -0.120 | 0.658 | fail |
| T10 short | 47 | 6.4 % | -0.463 | 0.344 | -0.003 | -0.804 | 0.215 | -1.226 .. -0.382 | 0.602 | fail |

Funnel (DEV): reclaim events 97 / 111; volume fail 3 / 4; knife veto 17 / 21; no target 0 / 0; nearest target under 2.5 R skipped 3 / 3; one-at-a-time skip 0 / 1; orders placed 74 / 82; filled 41 / 47 (fill rate of resolved orders 55.4 % / 57.3 %); exits: target 2 / 2, stop 27 / 32, break-even 10 / 12, time stop 2 / 1. By level type, events: month 11 / 18, week 57 / 73, pivot 29 / 20.

## Per-year table (DEV, by fill year; net R)
| Year | T09 n | T09 mean net | T10 n | T10 mean net |
|---|---|---|---|---|
| 2020 | 7 | -0.511 | 12 | -0.959 |
| 2021 | 6 | -1.153 | 10 | -0.449 |
| 2022 | 11 | -0.141 | 5 | +0.580 |
| 2023 | 10 | -0.235 | 16 | -1.239 |
| 2024 (to 06-30) | 7 | -1.347 | 4 | -1.218 |

Per-year SEs are 0.15 to 1.2 R: no year is a signal; 9 of 10 cells are negative.

## Exploratory cells (cannot promote; full table with SE/CI in cells.csv)
| Cell | T09 n / net R | T10 n / net R |
|---|---|---|
| Regime A (taker both legs) | 41 / -0.868 | 47 / -1.157 |
| No volume gate | 41 / -0.581 (same trades) | 48 / -0.854 |
| By level type: week | 30 / -0.560 | 34 / -0.900 |
| month | 2 / -1.498 | 7 / -1.140 |
| pivot | 9 / -0.448 | 6 / +0.129 |
| Sweep UTC 00-04 (Asia early) | 12 / -1.096 | 11 / -0.966 |
| 04-08 | 3 / +0.977 | 7 / -0.004 |
| 08-12 | 4 / -0.804 | 7 / -1.105 |
| 12-16 | 7 / -0.810 | 8 / -1.305 |
| 16-20 | 9 / -1.117 | 12 / -0.535 |
| 20-24 | 6 / +0.890 | 2 / -1.278 |
| Regime tag bull | 10 / -1.382 | 11 / -1.133 |
| Regime tag range | 31 / -0.323 | 36 / -0.704 |
| Exit target | 2 / +3.58 | 2 / +4.50 |
| Exit stop | 27 / -1.381 | 32 / -1.426 |
| Exit break-even | 10 / -0.141 | 12 / -0.200 |

The Asia 68 % census (n = 19, V-sweep without costs) does not show up as an edge here: the 00-04 block is the worst cell in both trials. Cells with n < 10 carry intervals wider than 2 R and are not evidence in either direction. All of these cells are exploratory and none is claimed.

## DECISION (OURS) list (all in PRE_REG.md; chosen once, not tuned)
1. "Within 3 bars": the sweep bar is bar 1; reclaim = first close above the level among bars s, s+1, s+2; sweep extreme over s..r; order placed at r's close.
2. First touch: all levels above bar s's low die at s, reclaimed or not; week/month levels live only in the following week/month; pivots live until touched.
3. Several levels touched at once: one trade, the level reclaimed earliest (causal at the order time), ties by month > week > pivot, then the higher level. (Amended before any return was computed; first draft was priority only.)
4. Pivot strict (ties are no pivot), confirmed at the start of day d+6.
5. Effort volume = bar s over the median of bars s-96..s-1; fewer than 96 prior bars: no event.
6. Knife measured over the 12 approach bars (H to the lowest low after H), not to the sweep extreme, since the wick's own range would veto every wick deeper than 2 %. (Amended before any return was computed; first draft measured to the sweep extreme.)
7. Target read at the reclaim close, nearest level strictly above the entry, literal; target limit fills only when a bar's high trades strictly above it.
8. Fill price = the level; on the fill bar only the stop counts (stop wins ties); +1R arms break-even from the next bar; per bar stop (or entry once armed) first, then target, then the +1R trigger.
9. Time stop = close of fill bar + 96; trades open at the end of the data are dropped (none in DEV).
10. One position or pending order at a time per side (1 event skipped).
11. Costs: regime B = fees.FEES_DERIBIT + 1 bp on taker legs (6 bps on stop / BE / timeout, 0 on target); regime A (exploratory) 12 bps on every exit; funding via bt_data.funding_cost_pct.
12. DEV start = data start (2019-12-31) per the brief, not splits.py DEV_START 2022-01-01.
13. The brief's "the sweep bar's volume" is read as bar s (the first bar below the level).

## Noticed
- A first-touch sweep of a weekly/monthly extreme is a high-volume bar by construction (median 9.5x), so the volume gate adds nothing here; any "effort" test needs a stricter or relative measure (for example against sweep bars of other levels).
- research_kit.regime_tag has 0 bear weeks in the whole DEV window again (monthly RSI14 never at or below 40 in the window); regime splits are bull vs range only.
- DNS: data.binance.vision reachable from this station; the futures UM monthly archive has no 2019-09..2019-12 files, so the brief's "2019-09" start is really 2019-12-31.
- eh_h3_first_touch (another worker) has its own copy of the same 15m cache from 2020-01; this worker fetched its own copy to cover 2019-12-31 and to avoid reading a cache a sibling may still be writing.
