# CONTEXT FACTORS: point-in-time definitions for backtesting (DEV only, 2026-10-16)

Session: Fable 5.1, worktree branch `claude/context-factors-backtesting-1a25f2`, claim `context-factors`. Data: BTCUSDT 1m,
DEV = bar open 2022-01-01 00:00 UTC .. 2024-06-30 23:59 UTC (912 days, 1,313,280 bars, 0 missing; loader refuses later bars,
`test_loader_refuses_validation_bars`). No VALIDATION or HOLDOUT bar was read. No outcome column exists anywhere in this folder.

Engine: `context_asof.py`, `context_at(bars, t, side, impl) -> dict` with `impl="vec"` (table build) and `impl="replay"`
(bar-by-bar state machine). Both return the same 87 fields; `run_compare.py` proved them equal at every 1h close of DEV plus
every 1m bar of days 200-230 (128,736 points, 0 mismatching fields, `compare_result.txt`). Hand arithmetic from the raw CSVs
(`indep_pandas.py`, `hand_check.md`) and a trader's-eye read at 12 seeded points (`trader_eye.md`) agree with the engine.

Labels: SOURCED = a trader's words (quote + file:line) or an operator quote (operator chat 2026-10-16); OURS = our judgement
or a default. OURS values were chosen before any count was read; the alternatives live in `trials.csv` (counts only).

## 0. Conventions every factor uses

**Decision time.** A row at bar `t` is what is known at the close of 1m bar `t` (open time + 60 s). A trade decided there fills
at the open of bar `t+1`. The decision grid is every 1h close (`t % 60 == 59`): 21,888 points x 2 sides on DEV.

**Buckets** (FORMULAS.md s.8 convention; `context_asof.py:14-22`). For period P minutes and offset `off` (0 for 1h/4h/8h/12h/1d,
2880 = Monday 2022-01-03 00:00 UTC for 1w): `cur_k = (t - off) // P`; `complete = (t + 1 - off) % P == 0`;
`last closed = cur_k if complete else cur_k - 1`. Every candle-based field (F3, F4, F5, ATR, pivots, profiles, the ledger's
prior day/week) reads only candles with index <= last closed. The candle that completes exactly at `t` IS closed
information at `t` (`PRIOR_RULE = "last_closed"`, red-team RT-1; the alternative `cur_k_minus_1` is trial T8).

**Partial candle.** The developing candle holding `t` (open, running high/low, close = `C[t]`) is a separate object and only
feeds the "partial daily candle" fields (`p_1d`, `p_4h`) and the touch-rule alternative of F3 (trial T3). It never feeds a
pattern, a band, an ATR or a level.

**Side.** `side="long"` looks for supports strictly below price; `side="short"` for resistances strictly above price.
A level's role at `t` is support iff the last closed 1h close is above it, resistance iff below it (rule A, OURS,
`nearest_side` `context_asof.py:332-351`; rule B uses the last closed 4h close, counted only, trial T1).

**ATR.** ATR14 on closed 4h bars, plain SMA of true range (FORMULAS.md s.12, lines 324-342: SMA, not Wilder),
`context_asof.py:451-460`; hand test `test_hand_atr_formulas_s12`.

**Look-ahead lint.** `python scripts/dev/lookahead_lint.py`: 0 unlisted hits; the 20 hits in this folder are allowlisted with
the reviewed reason each (fractal right-neighbour stored with its confirmation index; profile of a completed day; trailing
percentile window; test-tape construction; reporting percentiles in `counts.py`).

**What the plant tests do.** `PLANT[name] = True` switches one deliberate leak into the VEC build only; the test
`test_planted_lookahead_is_caught[name]` then requires that at least one field at some decision point differs between the
tape cut at `t+1` and a longer tape, OR that replay != vec. All 7 plants are caught; with no plant the same tests prove
truncation invariance (`test_truncation_invariance_vec`, `test_truncation_invariance_replay`).

## F1. Side-aware levels (9 sources, `levels_at` `context_asof.py:627-675`)

**Operator (SOURCED, chat 2026-10-16):** support layers for longs and resistance layers for shorts "from Tom, Fabio and other
confluence layers".

Ledger at a 1h grid point `t` = list of (price, source, available-from-minute):

| source | level(s) | available from | label |
|---|---|---|---|
| `prior_d_hl` | high and low of the last closed daily candle | that day's last minute | SOURCED: the operator's "previous daily candle"; which day = OURS (RT-1) |
| `prior_w_hl` | high and low of the last closed Monday-anchored week | that week's last minute | OURS (Monday anchor SOURCED: exchange week, red-team RT-2) |
| `fabio_vp_day` | POC, VAH, VAL of the last closed day's volume profile (bin 10 USD, value area 70 %, FORMULAS.md 18.1 lines 414-428; lowest bin on a POC tie) | that day's last minute | SOURCED formula (Fabio session profile); bin width OURS |
| `tom_vp_week` | POC, VAH, VAL of the last closed week's profile, same formula | that week's last minute | SOURCED formula (Tom "70 % of the trades", FORMULAS 18.1); weekly window OURS |
| `krown_zone` | fractal pivot highs/lows on closed 4h bars, width PIVOT_N = 3 each side, kept for KROWN_MAX_AGE = 360 closed 4h bars | the close of the 3rd bar after the pivot bar | OURS (Krown-style swing zones; 3 and 360 OURS) |
| `malkan_bb_d` | daily Bollinger mid, upper, lower (20, 2 population SD) of the last closed day | that day's last minute | SOURCED bands (bollinger_2026-10-14/SOURCES.md s.5 "Bands"); use as levels = mal_bb_mid_engulf study |
| `vwap_session` | developing VWAP since 00:00 UTC through bar `t` | 00:00 of the day (value updates each bar) | OURS |
| `vwap_week` | developing VWAP since Monday 00:00 UTC through bar `t` | Monday 00:00 | OURS |
| `round_1k` | the 1000-multiples just below and above price (two above when price sits on one) | always | SOURCED step (opr_weekly_low_round_sweep PRE_REG round-1000) |

Side fields (`side_fields` `context_asof.py:687-753`): `near_price`, `near_src`, `near_dist_atr` (distance in ATR14(4h)),
`level_age_h` (hours since available), `touch_count` (completed 1h bars since availability, at most the last 720, whose range
covers the level, excluding the bar holding `t`; `touches_before` :677-685), `first_touch` (= 0 touches), `at_level`
(`near_dist_atr <= K_ZONE = 0.5`, OURS; 1.0 counted as trial T2), `n_levels`, `n_krown`, `near_src_4hrule`.

**Look-ahead trap.** Using today's high/low/profile (the day the decision sits in) as "the daily level", or a pivot before its
right-hand bars have closed. **Plants:** `vp_include_today` (profile of the day holding `t`), `pivot_unconfirmed` (pivot
available one bar early). **Tests:** `test_planted_lookahead_is_caught[vp_include_today]`, `[pivot_unconfirmed]`,
`test_rt1_day_close_grid_uses_the_day_that_just_closed`, `test_hand_value_area_18_1`, hand check `near_price`/`near_src`/
`n_levels` at 3 points x 2 sides (0 mismatches), trader's eye 12 points (0 disagreements).

**What a trader sees.** "Price 27,410, nearest support 27,180 = yesterday's VAL, 0.4 ATR below, first touch, the level is
19 hours old; the 1k round number 27,000 is next." The engine row carries exactly these words (`trader_eye.md`).

## F2. Confluence, age, touches (`layers_in_zone` `context_asof.py:354-366`)

`n_layers` = number of DISTINCT sources with a level of the right role inside the zone (price - K_ZONE x ATR, price) for a
long, (price, price + K_ZONE x ATR) for a short. `n_layers_k1` = the same with K_ZONE_ALT = 1.0 (trial T2); `n_layers_4hrule`
= rule B role (trial T1). `level_age_h`, `touch_count`, `first_touch` as in F1.

**Operator (SOURCED):** "confluence layers"; counting distinct sources rather than distinct prices = OURS.

**Look-ahead trap.** A touch count that includes the bar holding `t` (its high/low are not final at a 1h close only when `t` is
not the bar's last minute; on the grid it is, so the exclusion is a convention that keeps replay == vec at every 1m bar).
**Tests:** truncation invariance covers `touch_count`/`n_layers`; hand check compares both at 3 points x 2 sides.

**What a trader sees.** "Three things line up within half an ATR under price: the weekly POC, a 4h swing low and the daily
lower band; the swing low has been tested twice this month."

## F3. Operator's daily-candle stop ladder (`ladder` `context_asof.py:207-229`, `ladder_cond` :232-240)

**Operator (SOURCED, chat 2026-10-16):** "If a daily candle has moved past the opening of the previous daily candle, the stop
would be below the previous daily candle. And if it is too much, then it should be refined for 12 hours or 8 hours."

Definition at `t` for a long (mirror for a short with highs):
- prior daily candle = the last closed daily candle (RT-1); prior 12h and prior 8h candles likewise.
- `stop_d_pct` = (price - prior daily low) / price x 100 when the low is below price, else not valid; same for 12h, 8h.
- rung = the FIRST of (1d, 12h, 8h) whose width is <= W_LADDER_PCT = 2.5 % (OURS; 1.5 % = trial T4); when every valid rung
  is wider, the tightest valid rung; when none is valid (price below every prior low), rung `none`.
- `ladder_stop_pct`, `ladder_cost_r` = 0.14 % / stop width (all-taker round trip, research_kit TAKER_RT_PCT),
  `ladder_below_floor` = stop < STOP_FLOOR_PCT = 0.56 % (OURS: cost > 0.25 R).
- `ladder_cond` (operator condition, close rule, primary) = current close beyond the prior daily OPEN in the trade direction;
  `ladder_cond_alt` (touch rule, trial T3) = the partial day's extreme beyond the prior open.

**Why W is tied to cost in R.** The ladder decides the stop, the stop decides R, and the fee is fixed in %, so "too much" must
be read together with "too little": COUNTS.md F3 shows the chosen stop's median 1.20 % at the 1d rung (cost 0.116 R
taker) and the p10 of 0.37 % (cost 0.38 R). Both distributions are reported there; nothing is tuned.

**Look-ahead trap.** Reading today's final daily OHLC (the day holding `t`) as "the previous daily candle"; at 23:59 the trap
is the opposite one (skipping the candle that just closed, RT-1). **Plant:** `ladder_final_day`. **Tests:**
`test_planted_lookahead_is_caught[ladder_final_day]`, `test_hand_ladder`, `test_rt1_day_close_grid_uses_the_day_that_just_closed`,
hand check of all ladder fields at 3 x 2 points.

**What a trader sees.** "Yesterday's low is 2.9 % below, too much; the last 12h candle's low is 1.4 % below, that is the stop;
0.10 R goes to fees."

## F4. Candle patterns on the last COMPLETED candle (`candle_patterns` `context_asof.py:135-166`)

**Operator (SOURCED, chat 2026-10-16):** "Candlestick pattern will also provide you some confidence."

For each of 4h, 8h, 12h, 1d the last closed candle `a`, the one before `b`, the one before that `c` (OURS definitions):
`bull_engulf` (b red, a green, a close > b open, a open <= b close), `bear_engulf` (mirror), `bull_pin` (lower wick >= 60 % of
the range and body <= 30 %), `bear_pin` (mirror), `inside` (a inside b), `outside` (a engulfs b's range), `three_up` /
`three_down` (three same-colour closes). Several names can hold at once (sorted tuple, `|`-joined in the csv); `none` otherwise.

**Look-ahead trap.** Reading the pattern off the candle that is still forming. **Plant:** `candle_partial` (uses the partial
candle as `a`). **Tests:** `test_planted_lookahead_is_caught[candle_partial]`, `test_hand_candle_patterns`, hand check of
`pat_4h/8h/12h/1d` at 3 x 2 points, trader's eye.

**What a trader sees.** "The last closed 4h candle is a bullish pin bar sitting on the weekly POC."

## F5. Bollinger state (`bb_state_from` `context_asof.py:173-204`)

**Operator (SOURCED, chat 2026-10-16):** "If you are jumping out of the lower band of the Bollinger band, then also there could
be some confidence. But it is very dangerous to short in the lower band because there could be a Bollinger band dance."

Bands: SMA20 of closes +/- 2 population SD (`ddof=0`), on closed 4h and closed 1d bars (SOURCED bands:
bollinger_2026-10-14/SOURCES.md s.5; N and K are the book defaults). State of the last closed bar:
- `inside`; `reenter_from_lower` (now inside, previous close at/below the lower band); `reenter_from_upper`;
- `walk_up` / `walk_down`: WALK_N = 3 consecutive closes at/beyond the band AND bandwidth wider than 3 bars earlier
  (SOURCES.md s.1 "three or more", the count N = 3 OURS, the expanding-bandwidth clause OURS);
- `break_up` / `break_down` (first close beyond); `outside_up` / `outside_down` (beyond, no walk, not the first close).
- `bb_4h_pctb`, `bb_4h_bw` (bandwidth = (upper - lower) / mid), same for 1d.
- `bb_long_conf` = long side and 4h state `reenter_from_lower` (the operator's "jumping out of the lower band").
- `bb_short_veto_walk` = short side and 4h state `walk_down` (the "dance", primary); `bb_short_veto_band` = short side and
  %b <= 0 on the last closed 4h bar (trial T5).

**Look-ahead trap.** Bands computed with the partial bar's close (the common charting default: the current bar's band moves
until it closes). **Plant:** `bb_partial_close`. **Tests:** `test_planted_lookahead_is_caught[bb_partial_close]`,
`test_hand_bb_state`, hand check `bb_*` at 3 x 2 points. Also caught in building: BUG-1 (cumsum precision in %b) made replay
and vec disagree on `bb_4h_state` at band-touch ties; fixed by a two-pass mean/variance in the vec build (ANGLES.md a).

**What a trader sees.** "4h closed back inside the bands after two closes below; the daily band is still walking down since
Tuesday, no shorts into it."

## F6. Phase (`_pivots_1d` `context_asof.py:511-545`, `_phase` :582-605)

**Operator (SOURCED, chat 2026-10-16):** phase matters (markup, markdown, accumulation, distribution).

Two candidate definitions, both counted (trial T6):
- **Phase A (primary, OURS):** daily fractal pivots (PIVOT_N = 3 closed days each side, confirmed 3 days later). Markup when
  the last two confirmed highs and lows are both higher; markdown when both lower; otherwise `distribution` when the last trend
  was up, `accumulation` when it was down, `range_initial` before any trend.
- **Phase B (counted only):** 30-day close return >= +7.5 % = markup, <= -7.5 % = markdown (threshold SOURCED from the repo's
  trend tag, backtest/tom_bt.py:270-271), else `distribution` above SMA50 of daily closes / `accumulation` below (OURS).
- `intraday` (trial T7 primary): 24h range <= BAL_K = 1.5 x ATR14(4h) = `balance`, else `trend_up`/`trend_down` by the 24h
  close change; `intraday_alt`: last 12 1h closes inside the prior 12 bars' range.

**Look-ahead trap.** A pivot used on the day it forms (needs the 3 right-hand days); phase B with the partial day's close.
**Plant:** `pivot_unconfirmed` (shared with F1). **Tests:** `test_planted_lookahead_is_caught[pivot_unconfirmed]`, hand check
`phase_a`/`phase_b`/`intraday` at 3 x 2 points, trader's eye.

**What a trader sees.** "Daily structure: higher highs and higher lows since the March low, markup; the last 24 hours are a
balance inside 1.1 ATR."

## F7. Own additions (`_f7` `context_asof.py:607-625`, side part in `side_fields`)

| field | definition (OURS unless noted) | trap and test |
|---|---|---|
| `vol_regime` | ATR14(4h) tercile within the trailing PCT_WIN = 180 closed 4h bars (30 days) | full-sample terciles; plant `pct_fullsample` caught |
| `squeeze` | 4h bandwidth <= its 10th percentile over the same trailing window (SQUEEZE_PCT SOURCED: SOURCES.md s.5 "Squeeze"; window OURS) | same plant |
| `session` | UTC hour: asia < 8, london < 13, ny < 21, else late | none (clock) |
| `weekend` | Saturday/Sunday UTC | none (clock) |
| `approach` | move of the last 4 closed 1h closes toward the nearest level: fast (>= 1 ATR), slow, away | truncation invariance |
| `sweep` | a wick through the nearest level in the last 6 closed 1h bars (the close rule already puts price back on the right side) | truncation invariance |
| `htf_align` | weekly close above (long) / below (short) the close 4 weeks earlier | week anchor (RT-2, hand check) |
| `funding` | last SETTLED Binance funding rate at or before `t` (settlement times 00/08/16 UTC): neg, low (<= 0.01 % = exchange baseline, SOURCED), high | plant `funding_next` (uses the next settlement) caught |
| open interest | NOT_IN_DATA: no OI history on disk for DEV; not built | n/a |

**What a trader sees.** "Low-vol regime, bands squeezed, Asia session on a Sunday, price drifting slowly into the level,
funding flat."

## 8. Parameter table (one row per number)

| name | value | label | source |
|---|---|---|---|
| ATR_N | 14, SMA | SOURCED | FORMULAS.md s.12 lines 324-342 |
| BB_N, BB_K | 20, 2 (pop SD) | SOURCED | bollinger_2026-10-14/SOURCES.md s.5 "Bands" |
| WALK_N | 3 | OURS (SOURCES.md s.1 "three or more") | trial-free: no alternative counted |
| K_ZONE / K_ZONE_ALT | 0.5 / 1.0 ATR | OURS | trial T2 |
| W_LADDER_PCT | 2.5 % (alt 1.5 %) | OURS | trial T4 |
| STOP_FLOOR_PCT | 0.56 % | OURS (0.14 % <= 0.25 R) | research_kit TAKER_RT_PCT |
| PIVOT_N | 3 | OURS | - |
| KROWN_MAX_AGE | 360 closed 4h bars | OURS | - |
| VP_BIN / VA_PCT | 10 USD / 0.70 | SOURCED (VA) / OURS (bin) | FORMULAS.md 18.1 lines 414-428 |
| ROUND_STEP | 1000 | SOURCED | opr_weekly_low_round_sweep_2026-10-16 PRE_REG |
| RET30_THR | 0.075 | SOURCED | backtest/tom_bt.py:270-271 |
| SMA_PHASE | 50 | OURS | - |
| BAL_K | 1.5 ATR | OURS | trial T7 |
| PCT_WIN / SQUEEZE_PCT | 180 / 10 | OURS / SOURCED | SOURCES.md s.5 "Squeeze" |
| APPROACH_BARS / APPROACH_FAST | 4 / 1.0 ATR | OURS | - |
| SWEEP_BARS | 6 | OURS | - |
| FUND_HIGH | 0.0001 per 8h | SOURCED | Binance baseline rate |
| WEEKLY_TREND_BARS | 4 | OURS | - |
| TOUCH_LOOKBACK | 720 closed 1h bars | OURS | - |
| PRIOR_RULE | last_closed | OURS (RT-1) | trial T8 |
| role rule | A: last closed 1h close | OURS | trial T1 |
| ladder condition | close rule | OURS reading of the operator's words | trial T3 |
| short veto | walk_down | OURS reading of "dance" | trial T5 |

## 9. Files

`context_asof.py` engine; `test_context_asof.py` 18 tests (in `scripts/dev/run_extra_tests.py`); `run_compare.py` +
`compare_result.txt` replay vs vec; `counts.py` -> `COUNTS.md`, `trials.csv`; `indep_pandas.py` + `hand_check.py` ->
`hand_check.md`; `trader_eye.py` -> `trader_eye.md`; `prior_rule_count.py` -> `prior_rule_count.md`; `ANGLES.md`;
`PRE_REG.md`; `REPORT.md`. `grid_context.csv` (VEC rows at every 1h close, 43,776 rows, no outcome column) is generated,
not committed.
