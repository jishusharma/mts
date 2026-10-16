# ANGLES: the five checks, what each found, and the prior-verdict PIT review (2026-10-16)

Companion to `CONTEXT_FACTORS_SPEC.md`. Every disagreement found by any angle is listed with its resolution. No outcome
column was read anywhere; every number below is a count or an arithmetic comparison.

## (a) Replay build == vectorised build at every t

Result: `python run_compare.py` over every 1h close of DEV (21,888 x 2 sides) plus every 1m bar of days 200-230 (both sides):
**128,736 points, 85 fields compared per point, 0 mismatching fields** (`compare_result.txt`; the two ledger-size fields
`n_levels`/`n_krown` were added afterwards and are covered by `test_replay_equals_vec_synthetic`, the hand check and the
T8 count, which evaluates both at 5,472 further points). Re-run clean under both `PRIOR_RULE` values.

Disagreements found on the way, each a bug, each fixed and recorded:

| id | symptom (where the builds differed) | cause | fix |
|---|---|---|---|
| BUG-1 | `bb_4h_state` / `bb_4h_pctb` at a few hundred 4h closes | vec build used a cumsum-of-squares variance; at BTC price levels (~1e4, squares ~1e8 over 20 bars) the subtraction lost ~8 digits, so %b differed in the 7th digit and the band-touch comparison (`c >= u`) flipped on ties | two-pass windowed mean/variance in the vec build (`context_asof.py:462-475`); replay keeps the direct per-window computation |
| BUG-2 | `atr4` drift of 1e-9 growing along DEV, then `at_level` flips at zone boundaries | vec ATR as a cumsum difference accumulated rounding over 5,400 closed 4h bars | sliding-window mean in the vec build (`_atr` :451-460) |
| TIE | `at_level` and `n_layers` disagree when a level sits exactly K_ZONE x ATR from price | the two builds compared `d/atr <= 0.5` with different float paths | both round to 9 decimals before the comparison (`side_fields` :710 and the replay twin :1247, `layers_in_zone` :360-363) |
| RT-1 | at every day close (23:59) the ledger's "prior day" and the ladder's "prior daily candle" were the day BEFORE the day that just closed, while the candle fields already used the just-closed day | the first draft used `cur_k - 1` for F1/F3 and `last closed` for F4/F5 | `PRIOR_RULE = "last_closed"` in both builds (the fill at open[t+1] lies in the next bucket; a candle that closed at t is closed information, same as the bands); the old rule is kept as the T8 alternative, counted only (`prior_rule_count.md`) |

A test defect found while proving (a): the first vec truncation test was vacuous because `context_at` itself sliced the
tape to `t+1`, so "truncated" and "full" were the same array. Fixed: the vec build runs on whatever array it is given and
the test passes `slice_bars(bars, t+1)` on one side only (`test_context_asof.py:182`, `:221`). After the fix the same test
catches all 7 plants.

## (b) Trader's-eye check at 12 seeded random DEV points

`trader_eye.py` (seed 20261016, fixed before any row was read; grid points after day 70) writes, from the raw bars by hand,
what a trader sees at that minute (last closed D/12h/8h/4h candles, the partial day, nearest support and resistance with
source and distance, phase, Bollinger state, vol regime, session, funding, the stop ladder), then the builder's row and every
disagreement on 19 checked fields. **Result: 12 points, 0 disagreements** (`trader_eye.md`). The prose reads like a desk
note at each point (example, 2023: "nearest support 0.4 ATR below = yesterday's VAL, first touch, 4h closed back inside the
bands"), which is the operator's test of whether the factor is the thing a trader would quote.

## (c) Hand arithmetic per factor from the raw bars

`indep_pandas.py` recomputes every field with pandas resample/rolling and the spec's rules, with no engine code imported for
any number; `hand_check.py` compares it with the engine at 3 points x 2 sides chosen before any row was read (a mid-day 1h
close, a 4h close, a day close, all 2023). **Result: 324 field comparisons, 0 mismatches** (`hand_check.md`). Formula tests
with fixed numbers: `test_hand_atr_formulas_s12` (FORMULAS.md s.12), `test_hand_value_area_18_1` (18.1), `test_hand_bb_state`,
`test_hand_candle_patterns`, `test_hand_ladder`, `test_bucket_convention`.

Disagreement found and resolved: the first hand module resampled with `"7D"` / `"1D"` and an `origin=` of Monday 2022-01-03;
pandas ignores `origin` for day-multiple rules (RuntimeWarning), anchoring the week on the first bar (a Saturday). That gave 4
false mismatches on `c_1w_hl` / `htf_align` and 2 on `n_layers` (the weekly POC moved). Fixed in the CHECKER (`"168h"` /
`"24h"`), not the engine: the engine's Monday anchor was right and the checker was wrong. Recorded here because a hand check
that disagrees is not automatically the engine's fault, and because this is exactly red-team item RT-2.

## (d) Red team: five ways the spec or code is likely wrong, top three tested

| id | suspicion | tested? | result |
|---|---|---|---|
| RT-1 | at a bucket close the "prior" candle is off by one (either skips the candle that just closed, or uses the one still forming) | yes: `test_rt1_day_close_grid_uses_the_day_that_just_closed`, T8 count | real in the first draft (skipped the just-closed day at 23:59): fixed, see (a). 629 of 2,736 8h-close grid points change a level field, every one changes a ladder field |
| RT-2 | week anchor: the "prior week" is Saturday-anchored (the archive starts on a Saturday) instead of Monday 00:00 UTC | yes: hand check (pandas `168h` from Monday), `test_bucket_convention` | engine correct; the first hand module was wrong (see (c)) |
| RT-3 | Bollinger bands with sample SD (ddof=1) or with the forming bar's close; squeeze/vol terciles over the full sample | yes: plants `bb_partial_close`, `pct_fullsample`; `test_hand_bb_state` with ddof=0 numbers | all caught; engine uses population SD and closed bars |
| RT-4 | funding read at the settlement BEFORE it is known (the rate for the next period) | yes: plant `funding_next` | caught; engine uses the last settlement with calc_time <= close of bar t |
| RT-5 | ATR as Wilder RMA instead of the SMA FORMULAS.md s.12 specifies | yes: `test_hand_atr_formulas_s12` | engine matches the SMA formula; Wilder differs in the test numbers |

Items 1-3 are the "top three" by prior probability; 4 and 5 cost one test each so they were run as well. Two further
suspicions not tested, written so the next session can: the `touch_count` convention (completed 1h bars only, the bar
holding t excluded) differs from how a trader counts a touch that is happening now; and `vwap_session` resets at 00:00 UTC
whereas the Java live engine's anchor is NOT VERIFIED (pit_levels REPORT.md section 2 says the same).

## (e) Two definitions, counted under both, one chosen with a reason (never by outcome)

`trials.csv` (8 rows, `outcome_read = no` on every row):

| trial | factor | primary | alternative | counts primary (long/short) | counts alt (long/short) | reason for the primary |
|---|---|---|---|---|---|---|
| T1 | F1 role rule | last closed 1h close vs level | last closed 4h close | 21,888 / 21,888 grid rows with a role | 16,293 / 16,528 | the 1h close is the decision grid; a 4h close flips up to 4 h late |
| T2 | F2 zone width | 0.5 x ATR14(4h) | 1.0 x ATR | 20,688 / 20,687 at_level | 21,610 / 21,594 | half an ATR keeps "at the level" tighter than a typical 4h range |
| T3 | F3 operator condition | close past the prior daily open | partial day's extreme past it | 10,303 / 10,629 | 14,594 / 14,676 | "has moved past the opening" at a decision = the close a trader quotes |
| T4 | F3 width W | 2.5 % | 1.5 % | 12,558 / 12,565 at the 1d rung | 9,365 / 9,392 | 2.5 % is about one DEV median daily range; 1.5 % pushes most days to 12h/8h |
| T5 | F5 short veto | band walk down in progress | %b <= 0 on the last closed 4h bar | 0 / 426 | 0 / 1,382 | the operator's "dance" is the walk, not a single close outside |
| T6 | F6 phase | A: daily fractal pivots | B: 30-day return +/- 7.5 % and SMA50 | 7,505 / 7,515 markup | 6,815 / 6,785 | A is what a trader reads off swing highs and lows; B reuses the repo's trend tag |
| T7 | F6 intraday | 24h range <= 1.5 ATR = balance | 12 closes inside the prior 12 bars' range | 2,841 / 2,837 balance | 8,405 / 8,412 | range-vs-ATR is one number a trader checks |
| T8 | F1/F3 prior bucket | last closed bucket | cur_k - 1 | 2,581 / 2,612 at_level at 8h closes | 2,545 / 2,584 | the fill lies in the next bucket; a closed candle is closed information |

Phase A and phase B agree on 7,646 of 19,606 long events (39 %): the two "phase" words name different things, which is why
one verdict per definition would be two verdicts; PRE_REG.md tests phase A only and logs B.

## Prior-verdict review: was levels / phase / candle context built point-in-time?

For each study the lines that build the context a decision reads, and whether a later bar can reach the decision.

| study | context built | file:line | PIT? |
|---|---|---|---|
| mal_bb_mid_engulf_2026-10-16 | 5m BB(20,2) mid and the 1h/4h RSI and mid for the HTF filter | `study.py:63-65` `htf_idx` = index of the last CLOSED 60/240-min bar at the 5m close; `:86-88` uses that index and the 5m close | yes: the HTF filter reads closed higher-TF bars only; the 5m band uses closed 5m bars |
| opr_bb_mtf_center_2026-10-16 | 30m/1h/4h bands, ATR, RSI; the "last m closed 30m bars" condition | `study.py:112-116` per-TF aggregation of closed bars; `:120-125` `cond30` indexes `2*ks + 1 - i`, the 30m bars that closed at or before the 1h touch bar's close | yes |
| wlow_bounce_bbrsi60_2026-10-16 | prior-week low series, break flags per 1h candle | `study.py:143` `weekly_low_series(candles, week_mode)` (prior full week), `:149` `brk[t-24 .. t]` reads candle t's low at candle t's close | yes (the touch on bar t is known at the close of t, which is the decision time used) |
| opr_weekly_low_round_sweep_2026-10-16 | prior FULL Monday-Sunday week low per 1m bar; round level from the trailing min shifted by one | `study.py:35-46` `week_low_prior`, `:48-50` `round_levels` (`rolling(prev).min().shift(1)`) | yes |
| rsi_divergence_mtf_2026-10-09 | RSI pivots with a right-hand neighbour | `backtest/layers/rsi/rsi_divergence.py:26` `vals[i + 1]` and `:54` event stamped at `ts[b + 1]`, i.e. the event is dated one bar after the pivot, which is when the neighbour is known (allowlist rows 39-40, still "pre-existing, unreviewed") | yes for the one-bar neighbour; the study is not a PRE_REG and read every split at once (`RESULT.md:1` "2022-01-01 .. 2026-10-07", `:9` "every year 2022-2026"): its FAIL is a DEV+VALIDATION+HOLDOUT read |
| gross_effect_screen_2026-10-15 | session extremes as running max/min within the day prefix of complete bars | `screen.py:85-100` `np.maximum.accumulate` / `minimum.accumulate` over the day's bars, `newh`/`newl` from the previous running value | yes |
| eur_low_us_sweep_2026-10-14 | (not in the review list, but relevant to REPORT.md) | `RESULT.md:8` "DEV 2022-2024, VAL 2025, HOLDOUT 2026, reported side by side", `:21`, `:38` per-split numbers; `VERDICTS.csv:3` split_read DEV+VALIDATION+HOLDOUT | the HOLDOUT-read row is REAL, not a parse error |

**Family statement (explicit).** Every row above tests a SETUP: a trigger (engulf, mid touch, weekly-low break, sweep, RSI
divergence, session-extreme fade) whose forward return was read. This study tests a context FILTER: whether the operator's
stop-ladder trade, taken at a level, does better or worse when a context factor holds, against context_null controls that
share hour, vol and trend. That is a different family. The kill scopes that matter:
- `VERDICTS.csv:4-5` gross_effect_screen T (INCONCLUSIVE) and C (FAIL): kill scope "session-extreme fade with delta flow on
  1m BTC". No session-extreme trigger and no delta flow is used here. `verdicts.py check "stop"` lists these two rows only
  because the word "stop" appears in their kill-scope text.
- `VERDICTS.csv:21` wlow_bounce EVENT (INCONCLUSIVE, kill scope none, one_run yes): the weekly-low break + bounce + hold under
  RSI 60 setup. Here the prior-week low is one of nine level sources and no RSI or bounce rule exists; `verdicts.py check
  "Bollinger"` flags the row by word only.
- `VERDICTS.csv:6-7` mal_bb (FAIL, kill scope UNPARSED), `:9-10` opr_bb_mtf (INCONCLUSIVE / FAIL), `:13-14` opr_weekly
  (FAIL): setups on the band mid, the band in a trend, the weekly-low reclaim. None is re-run; PRE_REG.md section 4 names a
  kill scope that excludes every one of them.
- `VERDICTS.csv:17` rsi_divergence (FAIL, all splits): no RSI factor is built here.
- `VERDICTS.csv:3` eur_low_us_sweep (FAIL, all splits): no retest/US-window trigger is built here.

Holm m: `verdicts.py count --split DEV` = 14 distinct (study, arm) variants on DEV, + 8 trials in `trials.csv` = 22 before
this study's own verdicts are added (PRE_REG.md section 4).

## Overlap with `research/pit_levels_2026-10-16/` (not written to, read on origin/fast-track)

That folder audits the EXISTING builders in `backtest/` (12 of 13 family checks PASS, one reporting FAIL in `tom_bt_report.py:161`)
and defines a level-ledger schema (`PIT_CONTRACT.md` section 1: level_id, origin, formed_at, available_at, touch_history, role).
This folder builds a NEW engine with its own ledger (price, source, available-minute) and proves it two ways. The schemas agree
on available_at = close of the confirming bar for fractals and the period end for period levels; ours carries no `invalidated_at`
and no `zone_lo/zone_hi` (every level is a line; the zone is K_ZONE x ATR around price). Its card
`pit-prior-va-failed-auction-dev` tests a setup (failed auction at the prior-day value-area edge); ours tests filters. The two
can share the ledger later; nothing here depends on it.
