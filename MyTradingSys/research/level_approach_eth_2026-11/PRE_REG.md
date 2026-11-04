# PRE_REG: level approach replication on ETHUSDT and BTC+ETH pooled (card ms-level-approach-eth-replicate, C15)

Written and frozen BEFORE any ETH or pooled outcome was read. `study.py` refuses to run unless the last line is `FROZEN_UTC: ...` and prints this file's sha256. Descriptive, fee-free; no trade rule, no edge claim. Source study: `../level_approach_2026-10-30/` (PRE_REG.md, RESULT.md); its code (`level_approach.py`) is reused by path, unchanged.

`verdicts.py check "level approach"` before freezing: no prior row matches (need 2 of ['appro', 'level']). Safe to pre-register; exit 0.

## Definitions (all as C15, nothing retuned)
| Item | Value | Label |
|---|---|---|
| Data | BTCUSDT and ETHUSDT USD-M futures 1m klines (F:/MTS/data/tom_raw/klines), complete UTC bars; 5m/15m/1h resampled from 1m | OURS |
| DEV window | 2022-01-01 .. 2024-06-30; the loader refuses any end after 2024-07-01 and never opens a later file. Half A < 2023-07-01 <= half B. VALIDATION/HOLDOUT unread | SOURCED (project windows) |
| Levels | prior-day high (pdh) and last lower high (lh, 10-day lower-low lookback) per symbol from its own daily bars | pdh/lh SOURCED (operator); 10 OURS |
| Classes | near_miss / wick_back / close_then_fail / accepted with the C15 arm line 0.1 %, 3 confirm closes, 12-bar forward | OURS (C15) |
| Features | RSI14 >= 50; CVD12 > 0; close >= daily BB mid (SMA20 of prior daily closes) | OURS (C15) |
| Sequence cell | class x TF x the 8 feature combos, both level kinds pooled (as C15 sequences.csv); only near_miss and wick_back are judged (class known at the event bar) | OURS (C15) |
| Outcome | p_above_level = share whose close 12 bars after the anchor is above the level; Wilson 95 % CI | OURS (C15) |
| Class base rate | p_above_level of all events of that class x TF (features known), per symbol, and pooled | OURS |

## Agreement rule (frozen)
A near_miss / wick_back sequence row AGREES when all hold:
1. n >= 30 in each of the four cells BTC-A, BTC-B, ETH-A, ETH-B (OURS, C15's MIN_N).
2. In each of those four cells p_half - (that symbol's class x TF base rate) has the same sign, and none is exactly 0.
3. The pooled Wilson 95 % CI of the row excludes the pooled class x TF base rate (differs from the base rate).
Rows failing 1 are UNDERPOWERED rows; rows passing 1 but failing 2 or 3 DISAGREE.

## Reproduction check
BTC futures here = the same folder and code as C15, so the BTC run must reproduce C15 exactly: 10,822 events, the shipped tables.csv n per kind x class x TF, and the invalidation row (near_miss 1m, 0/0/0, n=466, p 0.210). Any mismatch stops the study and is reported.

## Context
Regime: none, because this is a descriptive replication with no regime gate (as C15); the weekly regime mix of the DEV window (research_kit.regime_tag on each symbol's spot 1d history, as bb_range_retest_eth_pool) is reported per symbol and pooled.
Phase: none, because the level approach event itself is the phase (armed under the level, first touch of the arm line).
Session: none, because C15 has no session gate; events from all UTC hours count.
Entry: none, because no trade is simulated; the event bar (near_miss / wick_back) or event bar + 3 (through classes) is the anchor.

## Verdicts declared now
- REPLICATES: at least one near_miss / wick_back row AGREES.
- DOES-NOT-REPLICATE: no row agrees and at least one row passes rule 1.
- UNDERPOWERED: no row passes rule 1.
The C15 invalidation row (near_miss, 1m, RSI<50, CVD12<=0, below daily BB mid) is named in advance and reported whatever the verdict. 2 classes x 4 TFs x 8 combos = 64 rows judged, no multiplicity correction: an agreeing row is a hypothesis for a fresh-window test, never a core, never "edge". Wilson CIs treat overlapping events as independent and are too narrow.

## Not allowed
No threshold changes after the run; no extra levels, symbols or windows; no fee or slip constant (fee-free study).

FROZEN_UTC: 2026-11-05T01:30:00Z
