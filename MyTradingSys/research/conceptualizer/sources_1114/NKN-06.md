# NKN-06 context design (frozen before results)
Pivot R2/R3 (and S2/S3) breakouts. Frozen 2026-11-14 from five angle designs. No backtest run, no outcome data seen.

## Verified inputs (checked on disk this turn)
| Item | Where | Status |
|---|---|---|
| Classic floor pivots P, R1-R3, S1-S3 | `MyTradingSys/research/nkp2-levels-phase-1114_2026-11-14/nkcore.py:70` `pivots(h,l,c)` (R3 = H+2(P-L), S3 = L-2(H-P)) | exists |
| ATR14 | `nkcore.py:48` `atr14_simple`, `:57` `wilder_atr` | exists; Wilder, fixed |
| Cycle phase labels (MARKUP, MARKDOWN, ...) | same folder `mts_phase.py`; `<local-path>`; PHASE_LAG=1 default | exists; one BTC-based label per UTC day |
| Coin-day trend phase UP/DOWN/RANGE (20-day MA slope lag 5 + ADX14>=20) | common block; `ctxlib.py`, `nkcore.prep` | exists; must be computed per coin-DAY (NK2 used 1h-bar labels: the flagged bug) |
| Malkan regime | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` `malkan_regime(rsi,40,60,20)` returns BULL / BEAR / RANGE (BULL = min>=40 and max>=60) | exists |
| RSI | `backtest/layers/rsi/rsi_core.py:7` | exists |
| Bollinger %B | NO layer module. Only `bb_len=20, bb_mult=2` inside `backtest/layers/squeeze/squeeze.py:15` `squeeze_momentum` | NEW CODE needed (trivial formula, own test, committed WITH the PRE_REG) |
| OHLCV | `<local-path>` (23 files); 1h/4h/1d resampled from 15m, bars used only after close | exists |
| Funding 8h, OI daily | `<local-path>`, `_oi_daily.csv` | exists; descriptive columns only |
| HM(9,3,21) layer | not verified | DROPPED |

## Phase tested
- **PRIMARY P1 (long):** coin-day trend phase UP x BTC cycle state MARKUP (both from the prior UTC day close). Trigger: 1h close above R2.
- **PRIMARY P2 (short mirror):** coin-day DOWN x cycle MARKDOWN. Trigger: 1h close below S2, target S3. Own gate line, own n.
- **PRIMARY P3 (long, NK's second claim):** UP x MARKUP, daily "three days near R3" row (see Timeframes).
- Phase fixed before the day starts; not widened to gain n.
- Controls (reported separately, never pooled with any primary): RANGE x MARKUP; UP x cycle not MARKUP; DOWN x MARKDOWN long (mismatch, descriptive); 15m/4h trigger timeframes; away-from-level; BTC-filter row; V1/V2 layer rows; Malkan-opposite; close-based exit; placebo.
- All phases per coin-day from data through the prior close (PHASE_LAG=1). Look-ahead test must cover the phase labels (day-N label must not change if day-N bars are altered), not only the pivot levels.

## Context conditions
| # | Condition | Label |
|---|---|---|
| 1 | "R2 break leads to R3": price over R2 goes toward R3 (FzNDQm7wC_s 00:09:44) | SOURCED idea |
| 2 | "Three days sitting at R3 leads to a large up move" (a8RP5ftOfGo 00:13:56) | SOURCED idea (count of 3) |
| 3 | Zones, not lines (FzNDQm7wC_s 00:04:44) | SOURCED principle; implemented only as the at-level cap in #8, no extra band parameter |
| 4 | Pivots from prior UTC day H/L/C, classic floor formula, known at 00:00 UTC | OURS |
| 5 | Trigger timeframe 1h close (primary); 15m and 4h as controls | OURS |
| 6 | Fresh cross: signal close > R2 and prior 1h close <= R2; first such bar per coin-day; the 00:00 UTC 1h bar is skipped | OURS |
| 7 | No trigger if the day's high so far (closed bars) already >= R3 | OURS |
| 8 | At-level: signal close <= R2 + 1.0 x ATR14(1h); away: above that | OURS, 1.0 |
| 9 | Entry at next bar open | OURS |
| 10 | R = max(0.5% of price, 0.6 x ATR14(1h), entry minus R2); stop = entry - R | common block (0.5%, 0.6 OURS) |
| 11 | Target R3. If a bar opens beyond stop or target, fill at the OPEN (not the level). Same-bar stop and target: stop first | OURS (fixes NK2 flag) |
| 12 | Time exit at last 1h close of the trigger UTC day | OURS |
| 13 | Skip rule: R3 - entry < 1.5 x R. Skipped signals counted and reported. Report hit rate beside mean R | OURS, 1.5 |
| 14 | Day trend phase UP/DOWN/RANGE per coin-day | common block |
| 15 | Cycle state MARKUP/MARKDOWN per day, BTC-based, thresholds exactly as MTS_BRAINS_SPEC_1114, no retuning | OURS (spec ledger) |
| 16 | Close-based exit: 1h close back below R2 (control C11 only) | SOURCED in spirit (NK close-stop), 1h OURS |
| 17 | BTC filter (control C10): BTC daily close > SMA20 and SMA50 at the prior close (BTC uses its own) | rule SOURCED (NK index filter, NKN-03), BTC proxy OURS |
| 18 | Descriptive columns only, no filter: funding at last closed 8h stamp vs 90-day percentile; prior-day OI change; entry-hour share; stacked overhead (weekly R1 or prior-week high between entry and R3) vs clear; halving age | OURS |

Dropped on purpose: the 2-of-3-closes-above-P condition (UP phase covers it); the 1.0% room gate (one room rule only: 1.5R); the 0.15 ATR zone band (second OURS parameter); HM(9,3,21) row (layer not verified); funding percentile filter (postmortem: crowding-reversal 21/24 cells negative); OI filter; overhead clutter as a gate; any hour-of-day anchor (NK gives none).

## Crypto translation
- **Session open:** UTC 00:00 day boundary is the pivot anchor (also the funding stamp and the phase day). London/NY anchors not used. Weak port; only this one registered (no rolling-24h variant).
- **Gap replacement:** no overnight gap, so gap-above-R2 ideas are dropped. Triggers use closed 1h bars only, never an open price. The only gap handling is fill-at-open on gap-through of stop or target.
- **Funding / OI:** descriptive columns only (funding 8h; OI daily from 2020-09, known only after the UTC day closes). No filter, no cell.
- **BTC market filter:** control row C10 only; the BTC-based cycle state is already in the primary.
- **Does NOT translate:** weekly expiry pin and max-pain, overnight gap, equity session close, R3 as a magnet (liquidation levels are the real magnets in 20x perps; no data held, unmeasured). The daily "three days near R3" count is a weak port of a daily-bar equity idea.

## Layer agreement
| Variant | Exact read | Code path |
|---|---|---|
| V0 | Rule alone (pivot trigger + phase cell) | `nkcore.py` pivots + `mts_phase.py` |
| V1 | V0 + daily Malkan regime == BULL at the last CLOSED day (day d-1 for a signal on day d); RSI14 on daily closes. Short mirror reads BEAR. 40/60/20 SOURCED to Malkan, daily TF OURS | `rsi_core.py:7`, `malkan_40_60.py:24` |
| V2 | V1 + 4h Bollinger %B (SMA20, 2 population sd) on the last CLOSED 4h bar >= 0.50 (short mirror <= 0.50); 20 and 2 standard, 0.50 OURS | NEW `bb_percent_b`, own test with a future-bar poke, committed with PRE_REG; if not committed before the run, V2 is NOT RUN |
- If `malkan_regime` cannot be used, V1 is reported NOT RUN, no substitute layer (no second choice after sight of data).
- Opposite-state control C5 (Malkan BEAR) shows whether the layer adds anything.
- Rejected: 4h RSI (duplicate of V1), ADX (inside phase label), funding/OI (data from 2020-09), taker-delta, WaveTrend, session.

## Level type
- One primary level type: daily classic floor pivots; R2 trigger, R3 target; mirror S2 and S3. Weekly pivot and prior-day/week H/L only as the descriptive stacked-overhead column.
- **At-level test:** first fresh 1h close above R2 with close <= R2 + 1.0 x ATR14(1h) (#6, #8).
- **Away-from-level complement:** first 1h close of the day above R2 + 1.0 x ATR14 (fresh-cross condition waived), same UP x MARKUP days. Descriptive; compared with at-level on the same days to separate level effect from phase effect.
- **Placebo:** random 1h-close long entries in the same phase cell matched on UTC hour and on distance to R2 (+-0.3 ATR), same exit rules, 1000 draws.

## Timeframes
- Trigger: 1h primary; 15m and 4h trigger bars as control rows (levels stay daily; R uses that timeframe's ATR14 with the same floor).
- Native daily row P3: each of the last 3 closed daily closes within 0.5% below the R3 in force on day 3 and none above; R3 frozen at day 3; entry next day open; target R3, stop R (daily ATR14 with 0.5% floor), time exit 5 days. 0.5% and 5 days OURS, single values.
- Weekly: none (pivot levels are daily).

## Cells (every cell that will be run)
| ID | Role | Side | Phase cell | Variant | At/away | TF | Notes |
|---|---|---|---|---|---|---|---|
| P1 | PRIMARY | long | UP x MARKUP | V0 | at | 1h | R2 to R3 |
| P2 | PRIMARY | short | DOWN x MARKDOWN | V0 | at | 1h | S2 to S3, own gate line |
| P3 | PRIMARY | long | UP x MARKUP | V0 | at R3 | 1d | three-days row |
| C1 | CONTROL | long | RANGE x MARKUP | V0 | at | 1h | does trend label add |
| C2 | CONTROL | long | UP x not MARKUP | V0 | at | 1h | does cycle label add |
| C3 | CONTROL | long | DOWN x MARKDOWN | V0 | at | 1h | mismatch, descriptive |
| C4 | CONTROL | long | UP x MARKUP | V1 | at | 1h | Malkan BULL |
| C5 | CONTROL | long | UP x MARKUP | V1-opposite (BEAR) | at | 1h | layer adds? |
| C6 | CONTROL | long | UP x MARKUP | V2 | at | 1h | plus %B |
| C7 | CONTROL | long | UP x MARKUP | V0 | away | 1h | level effect |
| C8 | CONTROL | long | UP x MARKUP | V0 | at | 15m | |
| C9 | CONTROL | long | UP x MARKUP | V0 | at | 4h | |
| C10 | CONTROL | long | UP x MARKUP | V0 + BTC filter | at | 1h | #17 |
| C11 | CONTROL | long | UP x MARKUP | V0, close-based exit | at | 1h | #16 |
| C12 | PLACEBO | long | UP x MARKUP | random, hour + R2-distance matched | - | 1h | gate, not an edge cell |

**Total cells tried: 15** (3 primary, 11 controls, 1 placebo). **Primary cells: 3** (P1, P2, P3). Benjamini-Hochberg q <= 0.10 across the 3 primaries; any positive control is reported with the count 15 beside it. Other gates exactly as the common block (DEV <= 2023-12-31, VAL >= 2024-01-01; 12 bp taker, 6 bp maker non-gating; trade and day-cluster CI; ex-best-5; placebo beaten). Universe: the 20 NK1-NK6 coins plus 10 fresh holdout coins, run forward once from 2026-11-13. Code committed with the PRE_REG. Regime-mix block per split.

## Underpowered rule
A cell with n VAL < 100 is UNDERPOWERED, not FAIL, and is not read for or against the rule. 100 <= n < 200: numbers reported, cannot PASS (common block needs n >= 200). Pooling the 20 plus 10 holdout coins is already in the universe. No widening of phase and no loosening of the 1.5R skip or 1.0 ATR cap to gain n. Skipped signals are listed per cell.

## Open doubts
- NK never ties R2/R3 to trend days; the phase mapping is a hypothesis (quotes carry no phase, hour or timeframe; videos uncaptioned). Whether "R2 break" was on the daily or 1h chart is unknown (1h is OURS).
- A BTC-wide cycle label for altcoins; whether a UTC day suits the pivot anchor.
- Whether UP x MARKUP reaches n >= 200 on VAL after the fresh cross and 1.5R skip: likely UNDERPOWERED; P3 almost certainly.
- Three-day R3: R3 moves daily, so freezing at day 3 is OURS and may not be NK's meaning.
- MARKDOWN = SHORT mirror is OURS; NK's "no shorts near support" (ysq6x0eCFvI 00:03:00) is not applied to breakouts.
- V2 needs new code; NOT RUN if not committed with a test.
- 15 cells inflate false-positive risk on controls; only primaries gate.
- The NK2 FAIL (P/S1/R1, n 6102, net -0.009 R) does not transfer to R2/R3, but 12 bp is large against a 0.5%-floor R.
