# Independent recompute of 3 DEV trades (t1, 2026-11-14)

Method: own script (not committed, scratchpad) from raw 15m cache bars (EOSUSDT_15m.npz) and FORMULAS.md s1/s4/s5/s12 only. study.py and test_study.py were not read until the numbers below were final (afterwards only a grep confirmed ATR is read at the signal bar, inclusive). Study values come from `dev_trades.csv` (sample primary, coin EOS). `t_utc` in the log = 1h signal-bar OPEN; entry = next 1h open. Phase table label read from `phase_daily.csv`.

## Verdict: all 3 trades match the study on every field the log carries (entry, level, D, target, exit type, gross R, fee R, net R, hold24 R); 0 diffs. Day labels MARKDOWN/BEAR on all three dates.

## Trade A: stop exit, EOS 2019-01-04T08:00 (level P)
| Field | Independent | Study | Diff |
|---|---|---|---|
| Prior day (01-03) H/L/C | 2.822 / 2.5709 / 2.6379 | not logged | n/a |
| P / R1 / S1 | 2.676933 / 2.782967 / 2.531867 | target 2.53186667 = S1 | 0 |
| Signal bar O/H/L/C | 2.7022 / 2.7238 / 2.638 / 2.6457 | not logged | n/a |
| Trigger | high > P, close < P; R1 not touched, so level P | P | 0 |
| 30m RSI9 / EMA3 / WMA21 (bar 08:30-09:00) | 40.745 / 49.787 / 58.691, sell True | filter passed (trade exists) | 0 |
| VWAP (00:00 anchor) | 2.67483, close 2.6457 below | filter passed | 0 |
| Entry (09:00 open) | 2.6457 | 2.6457 | 0 |
| ATR14 | 0.040757 | not logged | n/a |
| D candidates: high-entry / ATR / 1.2% | 0.0781 / 0.040757 / 0.031748, D = 0.0781 (signal-high binds) | 0.0781 | 0 |
| Stop / target | 2.7238 / 2.531867 (target 1.46 R away, no skip) | target 2.53186667 | 0 |
| Exit | stop touched in bar 2019-01-05T00:00 (price 2.7238) | stop | 0 |
| Gross R / fee R / net R | -1.00000 / 0.040651 / -1.040651 | -1.0 / 0.04065 / -1.04065 | 0 (rounding 5 dp) |
| Hold24 gross R | -0.153649 | -0.15365 | 0 |

## Trade B: target exit, EOS 2019-01-03T08:00 (level P)
| Field | Independent | Study | Diff |
|---|---|---|---|
| Prior day (01-02) H/L/C | 2.8617 / 2.5877 / 2.8197 | not logged | n/a |
| P / R1 / S1 | 2.756367 / 2.925033 / 2.651033 | target 2.65103333 | 0 |
| Signal bar O/H/L/C | 2.7711 / 2.7711 / 2.7188 / 2.7294 | not logged | n/a |
| Trigger | high > P, close < P, level P | P | 0 |
| 30m RSI9 / EMA3 / WMA21 | 29.967 / 36.651 / 45.426, sell True | passed | 0 |
| VWAP | 2.77241, close 2.7294 below | passed | 0 |
| Entry | 2.7271 | 2.7271 | 0 |
| ATR14 | 0.0429 | not logged | n/a |
| D candidates | 0.044 / 0.0429 / 0.032725, D = 0.044 | 0.044 | 0 |
| Stop / target | 2.7711 / 2.651033 (1.73 R) | 2.65103333 | 0 |
| Exit | target hit in bar 2019-01-03T15:00, fill at 2.651033 | target | 0 |
| Gross / fee / net R | 1.728788 / 0.074375 / 1.654412 | 1.72879 / 0.07438 / 1.65441 | 0 |
| Hold24 gross R | 1.85 | 1.85 | 0 |

## Trade C: time exit, EOS 2019-10-12T09:00 (level P)
| Field | Independent | Study | Diff |
|---|---|---|---|
| Prior day (10-11) H/L/C | 3.2 / 3.027 / 3.0594 | not logged | n/a |
| P / R1 / S1 | 3.095467 / 3.163933 / 2.990933 | target 2.99093333 | 0 |
| Signal bar O/H/L/C | 3.1069 / 3.1212 / 3.0836 / 3.0905 | not logged | n/a |
| Trigger | high > P, close < P, level P | P | 0 |
| 30m RSI9 / EMA3 / WMA21 | 40.837 / 48.727 / 58.206, sell True | passed | 0 |
| VWAP | 3.10501, close 3.0905 below | passed | 0 |
| Entry | 3.0887 | 3.0887 | 0 |
| ATR14 | 0.025686 | not logged | n/a |
| D candidates | 0.0325 / 0.025686 / 0.037064, D = 0.0370644 (1.2% floor binds) | 0.0370644 | 0 |
| Stop / target | 3.125764 / 2.990933 (2.64 R) | 2.99093333 | 0 |
| Exit | neither touched in 24 bars; close of bar 2019-10-13T09:00 = 3.0926 | time | 0 |
| Gross / fee / net R | -0.105222 / 0.1 / -0.205222 | -0.10522 / 0.1 / -0.20522 | 0 |
| Hold24 gross R | -0.105222 (equals time exit, as it must) | -0.10522 | 0 |

## Day labels (phase_daily.csv, signal-bar UTC day)
| Date | Label | Cycle | close_used (BTC, prior day close) |
|---|---|---|---|
| 2019-01-03 | MARKDOWN | BEAR | 3858.56 |
| 2019-01-04 | MARKDOWN | BEAR | 3766.78 |
| 2019-10-12 | MARKDOWN | BEAR | 8258.5 |

Study log shows phase MARKDOWN, cycle BEAR for all three: 0 diffs.

## Notes and limits
- Covers three EOS trades, all level P; no R1 trade, no gap-fill stop, no same-bar tie recomputed here (those are in the hand-case unit tests).
- Intermediate fields (pivots, signal OHLC, RSI/EMA/WMA, VWAP, ATR) are not in `dev_trades.csv`; they are compared indirectly: the trade existing (filters passed), the target equal to S1, and D equal to the binding candidate. Trade A's D rests on signal-high minus entry, Trade B's too, Trade C's on the 1.2% floor, so ATR itself was never the binding term and is not directly tested by these three.
- ATR window: 14 true ranges ending at the signal bar inclusive; the excl-signal-bar variant (0.0359, 0.0410, 0.0240) would not change D on any of the three.
- RSI run over the full 30m history from 2018-10-01 (no gap fill), EMA/WMA seeded per FORMULAS s4/s5.
- Script: C:\Users\E-NGIN~1\AppData\Local\Temp\claude\daf915e1cb198d32\ce6e4118-da43-4178-8e19-703e14a3747c\scratchpad\recompute.py (not committed; reads F:\ cache, so cannot be a committed test).
