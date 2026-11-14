# PRE_REG NKN-06: daily pivot R2/R3 (and S2/S3) breakouts, context-conditioned (written and committed with the code, before any trade outcome is computed)

Operator order 2026-11-14 06:12Z: NK rules are not to be tested blindly; phases, context, crypto context, layers and levels must all be applied. A mechanical all-bars test is not acceptable. This PRE_REG implements the frozen design `nkn_design/NKN-06.md` (frozen 2026-11-14 from five angle designs; no backtest run, no outcome data seen). Label convention: SOURCED = a named video quote (id + time), OURS = our choice, one value, no grid. No parameter here is NK's own.

## Hypothesis
Pivot R2 break leads to R3 (FzNDQm7wC_s 00:09:44) and three days sitting at R3 lead to a large up move (a8RP5ftOfGo 00:13:56) work only when the coin is in an uptrend day AND the BTC cycle state is MARKUP (short mirror: DOWN x MARKDOWN), and only when price is at the level (within 1 ATR of R2), not far above it. Null: after 12 bp fee-net the same entries do no better than random entries in the same phase cell, hour and distance to the level.

## Context
- Regime: coin-day trend phase UP / DOWN / RANGE from data through the prior UTC daily close (20-day MA slope with 5-day lag, ADX14 >= 20 with DI direction, else RANGE; UNK for the first 60 rows) crossed with the BTC cycle state MARKUP / MARKDOWN per UTC day (BTC daily data through the prior close, lag 1, thresholds exactly MTS_BRAINS_SPEC_1114 s1, copied from nkp2 `mts_phase.py`, not retuned). Primary cells are only UP x MARKUP long (P1, P3) and DOWN x MARKDOWN short (P2); every other phase cell is a CONTROL.
- Phase: tested = UP x MARKUP (long), DOWN x MARKDOWN (short mirror). Fixed before the day starts, never widened to gain n. Controls: RANGE x MARKUP, UP x cycle-not-MARKUP, DOWN x MARKDOWN long (mismatched side).
- Session: UTC 00:00 day boundary is the pivot anchor (also the funding stamp and the phase day). London/NY anchors are not used and no rolling-24h variant is registered; no hour-of-day gate (NK gives none). The 00:00 UTC trigger bar is skipped.
- Entry: first FRESH 1h close through R2 (long) / S2 (short) per coin-day (signal close beyond the level, previous 1h close not beyond it), signal close at most 1.0 x ATR14(1h) beyond the level ("at level"), no trigger if the day's extreme so far (closed bars) already reached R3/S3; entry at the NEXT bar open in the same UTC day; stop = entry - R; target R3/S3; time exit at the last 1h close of the trigger UTC day.
- Regime mix (plan): RESULT.md reports UP / DOWN / RANGE share of coin-days for DEV and VAL and the share of coin-days in each primary cell. Nothing about the mix is chosen after sight of outcomes.

## Verified inputs (checked on disk 2026-11-14)
| Item | Where |
|---|---|
| Classic floor pivots P, R1-R3, S1-S3 (R3 = H + 2(P-L), S3 = L - 2(H-P)) | `nkn06_core.pivots` (same formula as nkp2 `nkcore.py:70`) |
| ATR14 simple mean of TR | `nkn06_core.atr14_simple` |
| Cycle state labels | `nkn06_core.cycle_labels_from_daily`, a line-for-line copy of nkp2 `mts_phase.py` features and `labels_from_features`; recomputed from `btc_cycles_2026-11/btc_daily.csv` (to 2026-11-06) plus complete UTC days of the cached Binance 15m; compared informationally with the shared `phase_daily.csv` in RESULT |
| Coin-day trend UP/DOWN/RANGE | `nkn06_core.daily_trend`, computed per coin-DAY on daily bars (not per 1h bar: the NK2 flagged bug) |
| Malkan regime BULL/BEAR/RANGE | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py` `malkan_regime(rsi, 40, 60, 20)` on `rsi_core` RSI14 of daily closes |
| Bollinger %B | NEW `nkn06_core.bb_percent_b` (SMA20, 2 population sd), own test with a future-bar poke, committed with this PRE_REG |
| OHLCV | `F:/MTS/data_cache/binance_spot/<COIN>USDT_15m.npz` (read-only); 1h, 4h, 1d are resampled from the 15m of the SAME coin; bars used only after close; a group with a missing 15m bar is dropped |

## Context conditions (cells read these)
| # | Condition | Label |
|---|---|---|
| 1 | "R2 break leads to R3": price over R2 goes toward R3 (FzNDQm7wC_s 00:09:44) | SOURCED idea |
| 2 | "Three days sitting at R3 leads to a large up move" (a8RP5ftOfGo 00:13:56) | SOURCED idea (count of 3) |
| 3 | Zones, not lines (FzNDQm7wC_s 00:04:44) | SOURCED principle; implemented only as the at-level cap in #8, no extra band parameter |
| 4 | Pivots from the prior UTC day H/L/C, classic floor formula, known at 00:00 UTC | OURS |
| 5 | Trigger timeframe 1h close (primary); 15m and 4h as controls | OURS |
| 6 | Fresh cross: signal close > R2 and previous 1h close <= R2; first such bar per coin-day; the 00:00 UTC bar is skipped | OURS |
| 7 | No trigger if the day's high so far (closed bars) already >= R3 | OURS |
| 8 | At-level: signal close <= R2 + 1.0 x ATR14(1h); away: above that | OURS, 1.0 |
| 9 | Entry at next bar open | OURS |
| 10 | R = max(0.5% of entry, 0.6 x ATR14 at the signal bar, entry minus R2); stop = entry - R | 0.5% and 0.6 OURS (common block) |
| 11 | Target R3. If a bar opens beyond stop or target, fill at the OPEN, not the level. Same-bar stop and target: stop first | OURS |
| 12 | Time exit at the last 1h close of the trigger UTC day | OURS |
| 13 | Skip rule: R3 - entry < 1.5 x R. Skipped signals counted and reported. Hit rate reported beside mean R | OURS, 1.5 |
| 14 | Coin-day trend phase UP/DOWN/RANGE | common block |
| 15 | Cycle state MARKUP/MARKDOWN per day, BTC based, thresholds exactly as MTS_BRAINS_SPEC_1114 | OURS (spec ledger) |
| 16 | Close-based exit: 1h close back below R2 (control C11 only) | SOURCED in spirit (NK close-stop), 1h OURS |
| 17 | BTC filter (control C10): BTC daily close > SMA20 and SMA50 at the prior close | rule SOURCED (NK index filter, NKN-03), BTC proxy OURS |
| 18 | Descriptive only, no filter: stacked overhead (weekly R1 or prior-week high between entry and R3) vs clear; entry-hour counts | OURS |

## Crypto translation
- Session open: UTC 00:00 day boundary is the pivot anchor. Weak port; only this one registered.
- Gap replacement: crypto has no overnight gap, so gap-above-R2 ideas are dropped. Triggers use closed 1h bars only. The only gap handling is fill-at-open on gap-through of stop or target.
- Funding / OI: not used (see "Design items not implemented").
- BTC market filter: control row C10 only; the BTC cycle state is already in the primary.
- Does NOT translate: weekly expiry pin and max-pain, overnight gap, equity session close, R3 as a magnet (liquidation levels are the real magnets in 20x perps; no data held, unmeasured). The daily "three days near R3" count is a weak port of a daily-bar equity idea.

## Layer agreement
| Variant | Exact read |
|---|---|
| V0 | Rule alone (pivot trigger + phase cell) |
| V1 | V0 + daily Malkan regime == BULL at the last CLOSED day (day d-1 for a signal on day d); RSI14 on daily closes; short mirror reads BEAR (not run: no short layer cell). 40/60/20 SOURCED to the Malkan layer, daily TF OURS |
| V2 | V1 + 4h Bollinger %B (SMA20, 2 population sd) on the last CLOSED 4h bar >= 0.50; 20 and 2 standard, 0.50 OURS |
- V1-opposite (Malkan BEAR) is control C5 and shows whether the layer adds anything. Max 3 layer variants (V0, V1, V2) as frozen; the opposite state is a control of V1.

## Level type
One primary level type: daily classic floor pivots; R2 trigger, R3 target; mirror S2 and S3. Weekly pivot and prior-week high only as the descriptive stacked-overhead column.
- At-level test: first fresh 1h close above R2 with close <= R2 + 1.0 x ATR14(1h).
- Away-from-level complement (C7): first 1h close of the day above R2 + 1.0 x ATR14 (fresh-cross condition waived), same UP x MARKUP days; compared with at-level on the same days to separate level effect from phase effect.
- Placebo (C12): random 1h long entries in the same coin and same UP x MARKUP cell (labels of the bar's day), VALIDATION signal bars, same UTC hour as the real trade, distance to R2 within +-0.3 ATR of the real trade, same stop/target/exit/room logic and same 12 bp fee. For each real VALIDATION trade up to 40 candidates are simulated; 1000 draws pick one candidate per real trade (trades with no candidate are dropped from both sides); p = (1 + #draws with placebo mean >= real mean) / 1001. P2 is matched the same way on DOWN x MARKDOWN short. P3 (daily): random daily entries in the same coin and UP x MARKUP cell (entry-day labels), VAL signal days, same R, target (that day's R3), 5-day exit and room rule, up to 60 candidates per coin, no distance match (the level is part of the signal).

## Timeframes
- Trigger: 1h primary; 15m and 4h trigger bars as control rows C8 and C9 (levels stay daily; R uses that timeframe's ATR14 with the same floor).
- Native daily row P3: each of the last 3 closed daily closes within 0.5% below the R3 in force on day 3 and none above; R3 frozen at day 3; entry next day open; target R3, stop R (daily ATR14 with 0.5% floor), time exit 5 days. 0.5% and 5 days OURS, single values. One open position per coin; overlapping signals are counted as `busy` and not traded.
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

Total cells tried: 15 (3 primary, 11 controls, 1 placebo). Primary cells: 3 (P1, P2, P3). Controls are reported in their own table, never pooled with a primary; any positive control is read beside the count 15. Timeframes: 1h is primary; 15m and 4h exist only as controls C8 and C9 (long UP x MARKUP), exactly as frozen; no short 15m/4h cell and no extra cell is added. One row per timeframe.

Event study: the same signals before the 1.5R room skip are reported for P1, P2, P3 as an event study (descriptive, cannot PASS). Only the tradeable room-filtered version (P1, P2, P3 above) can PASS.

## Universe
Fixed before any run: the 20 cached Binance spot USDT coins BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO (BTC plus 19 others, all with history on both sides of 2024-01-01; the loader asserts at least 400 days each side). Data end 2026-11-13.

## Splits
DEV = signal bar open time before 2024-01-01 00:00 UTC; VALIDATION = signal bar on/after it. Split by the SIGNAL bar (for P3: the signal day), never by entry or exit bar. VALIDATION is run once, after the code is committed.

## Fees and fills
- Fee-net R at 12 bp taker (verdict) and 6 bp maker (secondary, same fills, not a limit-fill model, so it is a sensitivity row only). nkp2 convention: 12 bp round trip = 6 bp of ENTRY notional + 6 bp of EXIT notional. Formula: fee_R = (bp / 20000) x (entry + exit) / R, with R the stop distance in price units; net R = gross R - fee_R, gross R = side x (exit - entry) / R. 6 bp uses bp = 6.
- R = max(0.5% of entry, 0.6 x ATR14 of the signal timeframe at the signal bar, side x (entry - level)) (floor stated; 0.5% and 0.6 OURS).
- Fills: market entry at the next bar open; gap through a stop or target fills at the bar OPEN; stop first if stop and target are inside one bar; target touch fills at the level. No funding or slippage charge beyond the fee (spot-equivalent bars).

## Statistics and gates (VALIDATION, per primary cell; all needed for PASS)
1. mean net R at 12 bp > 0;
2. trade-level bootstrap 95% CI low (4000 draws) > 0;
3. day-cluster bootstrap 95% CI low (4000 draws, clusters = UTC signal days) > 0;
4. ex-best-5 mean (the 5 days with the largest summed net R removed) > 0;
5. placebo beaten, p < 0.05, like for like (above);
6. Benjamini-Hochberg q <= 0.10 across ALL 3 primary cells of this rule (p = day-cluster one-sided bootstrap p of net R <= 0);
7. n VAL >= 200. Frozen design rule: n VAL < 100 is UNDERPOWERED (not read for or against the rule); 100 <= n VAL < 200: numbers reported, a failing cell is FAIL, a cell that would pass is UNDERPOWERED (cannot PASS). (Stricter than the task floor of 100; the frozen design binds.)
"Beats placebo" is reported separately from "profitable". Overall verdict: PASS if any primary cell PASSes, else FAIL if any primary cell FAILs, else UNDERPOWERED. Total cells tried and primary cells are stated in RESULT.

## Parameters
SOURCED: R2 break leads to R3 (FzNDQm7wC_s 00:09:44); three days at R3 (a8RP5ftOfGo 00:13:56); zones not lines (FzNDQm7wC_s 00:04:44); close-based stop spirit (control C11 only); Malkan 40/60/20 (Malkan layer module); Bollinger 20/2 (standard).
OURS (one value each, no grid): pivot anchor prior UTC day; 1h trigger; fresh cross first per day; 00:00 bar skipped; ATR14 simple mean; at-level cap 1.0 ATR; R floor 0.5% and 0.6 ATR; room rule 1.5 R; day-end time exit; coin trend phase (SMA20 slope 5-day lag, ADX14 >= 20 with DI direction, Wilder alpha 1/14); cycle thresholds (MTS_BRAINS_SPEC_1114); V1 daily timeframe; V2 %B threshold 0.50; P3 band 0.5% and 5-day hold; placebo +-0.3 ATR, 40 candidates per trade, 1000 draws; bootstrap seeds fixed in code.

## Design items not implemented (declared BEFORE any run)
- The 10 fresh holdout coins "run forward once from 2026-11-13": no forward data exists yet and they are not in the cache; not run. Universe is the 20 cached coins only.
- Descriptive columns funding vs 90-day percentile, prior-day OI change and halving age (design #18): not computed (descriptive only, no filter, no cell; omitted to keep the load low). Only the stacked-overhead split and entry-hour counts are reported.
- Short-side V1/V2 and short 15m/4h cells: not in the frozen cell table, not run.
- Data constraint: the cache holds 15m only, with 10-21 exchange-maintenance gaps per coin (max 41 bars); the loader asserts strictly increasing, 15m-aligned timestamps and counts gaps rather than assuming a constant step; any higher-timeframe bar with a missing 15m bar is dropped, ATR needs an unbroken window.

## Kill rules
- n VAL < 100 for a primary cell: UNDERPOWERED, not widened (no phase widening, no loosening of the 1.5R skip or the 1.0 ATR cap).
- Any look-ahead found (test failure) or a placebo that cannot be built: the run is void and fixed as a separately committed BUG.
- A result is never rescued by changing a parameter, a cell or the universe after the run.

## Protocol and tests
`study.py run` refuses to run while PRE_REG.md, study.py, nkn06_core.py or test_study.py has uncommitted changes. `test_study.py` (synthetic data, no cache access): truncation look-ahead test over levels, ATR, trend phase, cycle, Malkan, %B, day extremes and signals; leaky-label power test; cycle label from prior close only; fee on both legs with a hand number; split by signal bar; gap and tie fills; signal rules; control-phase trade never lands in a primary cell; P3 hand case; BH, placebo and verdict; loader asserts; no SyntaxWarning; small files.
