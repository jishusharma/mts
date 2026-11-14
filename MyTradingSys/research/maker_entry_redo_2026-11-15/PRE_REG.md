# PRE_REG maker_entry_redo_2026-11-15: maker (limit) entry vs taker entry, fee-net, 10 symbols, 2024+ out of sample (frozen before any return was read)

Card `maker-entry-redo-1115` (queue row 4, PLAN_24H_2026-11-15 section 8). NEW work: the maker-entry-1114 study (six NK/edge near-misses, 20 coins, own cost constants) was reverted
from trunk by 5cef7cf20 because its checker files broke Step 4e `test_no_own_costs`; its code is NOT reused. Its result (0 of 6 pass, maker net -0.04 to -0.35 R) stays in git history
and is context, not evidence for this study. This study asks one question: on two rules already re-derived on 10 symbols, does replacing the taker entry by a resting limit order
improve the fee-net result, and does any cell become a fee-net EDGE. Signals, levels, brackets and horizons are the parents' (imported by path, no line edited); only the entry
mechanics and the cost row change. Claim tested as encoded, not the trader's discretionary read.
Code `study.py`, tests `test_study.py`. Only signal/fill COUNTS were produced before this freeze (counts.csv, regime_mix.txt); the count pass computes no cost-adjusted figure it writes.

## Context
Regime: the parents' gates, unchanged. Arm BB: BTC Malkan weekly/monthly RSI band says RANGE (research_kit.regime_tag) and the signal bar is session-range tagged (current session range above the median of the 20 prior same-name sessions). Arm WT: the symbol's own daily SMA200 side agrees with the trade (buy above, sell below). Descriptive controls are not run here.
Phase: BB = range-to-range retest of the Bollinger band after an excursion and a re-entry close; WT = WaveTrend dot in the +-53 band with RSI 40/60 or close-divergence confluence, entry on the retest of the dot-bar midpoint (OURS phase device, as the parent).
Session: BB confirmatory sessions asia, london, ny (late excluded, as the parent); WT pooled over the day.
Entry: BB limit at level +- k ATR(14) (k 0.25 / 0.5 / 1.0), placed at the close of the re-entry bar, live N_TOUCH = 10 15m bars. WT limit at the dot-bar midpoint, placed at the dot-bar close, live 6 timeframe bars.
Regime mix: 150 weeks (BTC, 2024-01-01..2026-11-14, research_kit.regime_tag, parents' window; this study's events end 2026-11-12): bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%). The tag never returns bear in this window; the exact weeks of this study's window are written to regime_mix.txt by the run and quoted first in RESULT.md.

## Data
Signals: the parents' Binance SPOT cache (15m for BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, 30m/1h built from 15m, daily/weekly/monthly BTC), copied to the shared data cache (F:\MTS\data_cache\maker-redo-1115\, outside the tree). Fills and exits: the shared Binance spot 1m archive (F:\MTS\data_cache\binance_1m, ends 2026-11-13 23:59; a few missing minutes per symbol only make fills rarer, never invent one). Window: signal closes 2024-01-01 .. 2026-11-12 exclusive for every symbol. Ten symbols are the parents' (the 10 most established majors by listing age and liquidity, chosen before any return; survivorship-biased, stated).

## Cost (shared model, imported, never redefined)
| Leg | Value | Label |
|---|---|---|
| Taker baseline T0 = the parent entry (touch fill on the signal timeframe), round trip | research_kit.TAKER_RT_PCT (0.14 %) | SOURCED research_kit |
| Maker model M: limit entry + taker exit, round trip | research_kit.MAKER_IN_RT_PCT (0.09 %) | SOURCED research_kit |
| Target exit | market on touch, taker (so the 0.09 % holds: maker entry, taker exit) | OURS, conservative |
| Stop exit | market stop at the stop price, a gap fills at the 1m open | as parent |
No funding, no slippage beyond the stop gap, no rebate, no partial fills.

## Fill model (stated as OURS; same code for every cell; 1m bars)
| Item | Rule | Label |
|---|---|---|
| Signal | exactly the parent's signal and level; evaluated at bar close; the order is placed at the close of the trigger bar (BB: re-entry bar r; WT: dot bar) | SOURCED parent |
| Fill | first 1m bar after placement whose range trades THROUGH the limit by one tick (long: low <= L - tick; short: high >= L + tick). Touching L exactly is not a fill. Fill price = L (never better, even when the bar opens through it) | OURS |
| Tick | smallest nonzero price step seen in the last 300k 1m closes of that symbol | OURS |
| Queue position | a through-by-one-tick rule stands in for queue position: an order at the front of the queue would fill on a touch, one at the back needs the level to be traded through; we assume the back. A real passive order sits between this and the touch control TK below | OURS, conservative |
| Adverse selection | not an input: it is MEASURED as the parent's gross over the maker-filled signals minus over all parent-filled signals (negative = limits fill on the worse signals) | OURS |
| Order life | BB 10 x 15m after the re-entry bar (the parent's N_TOUCH); WT 6 timeframe bars after the dot bar (the parent's RETEST_N); then cancelled, a missed fill | SOURCED parent |
| Missed fills | counted: fill rate reported; "net per signal" counts a miss as 0 | OURS |
| After fill (BB) | parent bracket on 1m: target static at the event target, stop = px -+ 0.5 x |target - px|, time exit at the close of the 15m bar K_BARS after the 15m bar holding the fill; stop first when one bar touches both; the fill minute can stop out but not reach the target | OURS resolution, parent rule |
| After fill (WT) | exit at the close 12 timeframe bars after the timeframe bar holding the fill (the parent's H); no stop | SOURCED parent |
| Control TK (BB only) | same 1m exit engine, touch fill at L, taker cost 0.14: isolates the fill rule from the 15m to 1m resolution change | OURS |

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| BB: BB(20,2) excursion, re-entry close within 10 bars, retest at level +- k ATR within 10 bars, k grid, ATR 14, stop 0.5 x target distance, session-range tag (20 sessions, min 10), range gate | as bb_range_retest_2026-11-04 / bb_range_retest_10sym_2026-11-15 | OURS (parent), range gate SOURCED Malkan 60/40 |
| WT: WaveTrend hlc3 EMA10/EMA10/EMA21/SMA4, band 53, RSI(14) 40/60, close divergence 3..12 bars (near 3), dot-bar midpoint level, retest 6 bars, hold 12 bars, SMA200 trend gate | as wavetrend_c30_retest_2026-11-04 / wt_c30_retest_10sym_2026-11-15 | band 53, RSI 14, divergence window SOURCED; rest OURS |
| Maker fill: through-by-1-tick, fill at L, order life as above, taker target, 1m exit walk | see Fill model | OURS |
| Cost | research_kit.TAKER_RT_PCT / MAKER_IN_RT_PCT | SOURCED research_kit |
| Statistics | net = gross - cost; SE clustered by UTC day of the FILL ACROSS ALL SYMBOLS (research_kit.cluster_mean_se); t = mean/SE; two-sided normal p | SOURCED research_kit |
| Family | BB 3 sessions x 3 k = 9 cells + WT 3 TF x 2 sides x 2 conf = 12 cells = 21 cells; Holm m = 21 (research_kit.holm) on the maker-model p | OURS |
| EDGE (per cell) | maker n >= 30, >= 20 distinct fill days, maker net mean > 0, Holm p < 0.05, AND maker net > 0 in both sub-windows (2024-01..2025-06, 2025-07..2026-11) | thresholds OURS (as the parents' sub-window rule; the drift-excess gate of the parents is dropped here because the question is entry mechanics, stated) |
| Maker-vs-taker comparison | per cell: net per filled trade M vs T0, fill rate, net per signal with misses = 0, adverse selection; improvement counted only when M net per signal > T0 net per signal | OURS |
| Verdict | EDGE = at least one EDGE cell. Otherwise NO EDGE. Power wording follows the power gate (POWER_GATE.md): where it BLOCKs, the strongest wording is "NO EDGE, underpowered, INCONCLUSIVE ceiling" | OURS |
| Window / holdout | 2024-01-01..2026-11-12 reads the project VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) windows for these rule families: logged in research/holdout_reads.csv; both rule families were already burned by the parents' 10-symbol runs (this study adds no new tuning, nothing in the rules is changed) | operator card |

## Power gate (scripts/dev/prereg_gate.py; POWER_GATE.md)
Gross about +0.30 % per trade is the plausible effect (EDGE_POSTMORTEM_1114). Parents' day-clustered SEs make most cells BLOCK (MDE + cost > 0.30); the maker model lowers cost by 0.05 % only. The study is run anyway as an honest descriptive comparison with the ceiling wording above.

## What RESULT will say
1. `Regime mix:` first, then the verdict. 2. The 21-cell table: signals, maker fills (rate), n, days, gross, net, CI, p, Holm p, sub-window nets, T0 net, net per signal M vs T0, adverse selection. 3. One line per question: did maker improve fee-net (per signal), did any cell pass.

## Independent checks
Tests (`test_study.py`): fill cannot happen on a touch; fill at the limit not better; reads only bars after placement; cost imports are the research_kit values; the BB T0 baseline reproduces the parent's n and mean net on the parent window (replication line in RESULT).

## Not done
No forecast, no live-tree touch, no orders of any kind (research only, public market data).
