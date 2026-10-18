# PRE-REGISTRATION: Qriptal volume-anomaly candle as a filter and a veto on the lc-levels-hold level layer, BTCUSDT 1m, DEV (frozen 2026-10-16)

Session: card `imb-filter-on-levels` (lane SONNET, task Q74, B171 follow-up), worktree JIS-NB, base origin/fast-track 02a46e28.
Question source: `imbalance_qriptal_2026-10-16/README.md` section 5 ("level + imbalance + reaction"; the imbalance fade alone has no edge).
The commit that adds this file precedes every commit that adds an outcome; `git log` is the proof (convention of
`gross_effect_screen_2026-10-15/PRE_REG.md`). Status: EXPLORATORY TRIAL. Nothing here adopts a rule or makes a layer.
Labels: SOURCED = trader quote with file:line, or a repo file:line; OURS = our judgement, fixed here, never varied after a result.

## 0. Contract for the executing session
- Run sections 2-6 as written; a missing number is BLOCKED with the item named, never chosen.
- One outcome run. Rules in this file are not edited after the first outcome is computed. A bar is never lowered after a number is seen.
- DEV only: no bar with open >= 2024-07-01 is read for any input or outcome. The loader opens only `BTCUSDT-1m-YYYY-MM.csv`
  with YYYY-MM <= 2024-06 and raises on any later bar (`filter_join.assert_dev`, `dev_month_files`).
- `levels_confluence_2026-10-14/event_table.csv` is NOT read: its bars are 2024-11-21..2025-03-31, inside the standard
  VALIDATION window (2024-07-01..2025-06-30), so its MFE/MAE columns are VALIDATION outcomes. The layer's touches are rebuilt
  on standard DEV with the same level builder (`levels.py`, unchanged).
- No outcome column exists before this file is committed. The first heavy step is `run_filter.py counts` (flags and sizes, no outcome).

## 1. Why this layer (lc-levels-hold), not pit-levels
- `lc-levels-hold` (LC1, `levels_confluence_2026-10-14/levels_hold.md`) has 8 level families that survived its own random-line
  control (KEEP: prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_low, 4h_fractal_high, round_1000,
  prior_week_high). LC1 chose them on 2024-12..2025-03, a window outside this DEV, so the family choice is not tuned on these bars.
- `pit-levels` (Fable audit) froze one rule only (failed auction at prior-day VAH/VAL on 5m closes, own card
  `pit-prior-va-failed-auction-dev`, no ledger yet) and its levels are a subset of lc's. lc gives more events and more families.
- Level availability is point-in-time: `levels.py` reads only bars before the day's 00:00 UTC (`test_levels.py:test_levels_day_two_do_not_read_bars_at_or_after_midnight`;
  the pit-levels leakage proof covers the prior-day/period builders it shares, `pit_levels_2026-10-16/REPORT.md` section 3).
- Known defect NOT inherited: LC2's `event_table.py` sets `side = 1 if touch_bar_close >= level else -1`, which reads the close of the touch bar
  (look-ahead inside the 1m bar). This study sets the side from the close of the bar BEFORE the touch bar (section 2).
  Reported to the lc owner in RESULT.md; no lc file is edited.

## 2. The layer's trade (OURS encoding of the LC1 first-touch fade)
| item | rule | label |
|---|---|---|
| days | UTC days 2022-04-01 .. 2024-06-30 (warmup 90 days: the 50-bar volume median of the 1d candles and the 10-day / 1-week level seeds). A day or its prior day with < 1,400 1m bars is skipped and counted (DEV has 912 complete days) | OURS |
| levels | `levels.levels_by_day`, families restricted to the 8 KEEP above; built in blocks of 30 target days with 15 days of history, checked equal to a longer window (`test_filter_join.py`, `run_filter.py check-levels`) | LC1 code, OURS wrapper |
| dedup | levels of one day with the same price (e.g. prior_day_poc = naked_poc) make ONE trade; families are joined in the `family` column | OURS |
| touch | the first 1m bar of the UTC day with low <= level <= high (LC1/LC2 rule) | LC1 `levels_hold.analyze` |
| side (fade) | previous bar's close above the level: LONG (support); below: SHORT (resistance); equal: skipped and counted | OURS (causal replacement of LC2) |
| entry | the level price, filled on the touch (resting limit at the level, touch fill; trade-through not required). This is the lc assumption and is the optimistic fill: disclosed, same for every group | LC1/LC2 |
| width W | `levels_hold.stop_width(day_open, level) = max(0.004 x open of the 00:00 bar, 0.001 x level)` | LC1 `levels_hold.py:12` (itself OURS, PLAN.md) |
| stop | level - side x W | OURS |
| target | level + side x rr x W; rr = 1 primary (the LC1 HOLD definition), rr = 2 secondary | OURS |
| exit order | touch bar: only the stop can be hit (a target move inside the touch bar may precede the fill); later bars: stop first when one bar holds both; a bar that opens beyond the stop fills at its open; no hit: exit at the close of the 23:59 bar (time exit) | OURS (`imb.py` stop-first rule, `tom_bt.py:203-204` gap rule) |
| overlap | several levels of one day are separate trades and may overlap; every statistic is day-clustered | OURS |

Net R: `gross_R = side x (exit - level) / W`; `net_R = gross_R - 0.0007 x (level + exit) / W` (taker both legs, 5 bp fee + 2 bp slippage per leg =
0.14 % round trip; fee SOURCED `backtest/fees.py:27-28`, slippage OURS `PRE_REG_VOLUME_2026-10-09.md:28`, form as `research_kit.TAKER_RT_PCT`).
Readout only, never a rescue: maker entry `0.0002 x level + 0.0007 x exit` (0.09 % round trip).
At W = 0.40 % of price the cost is 0.35 R per trade, so a 1R : 1R bracket needs a hit rate near 67.5 % to break even.

## 3. The imbalance condition (Qriptal's construct F, README section 2)
His rule, in his words (staged raw transcripts):
- Small body, volume anomaly = trapped traders: "volume anomalies but you have very small bodies" (`extracts/_staged_2026-09-27/raw/qriptal_ZPFK3ZsLwoo_raw.txt:576-577`).
- Large body = strength, do not fade: "this is not an imbalance to pay attent attention to for a short because it has a very large body" (`qriptal_ZPFK3ZsLwoo_raw.txt:565-568`).
- Three parts: "I look for a good resistance or support. I look for imbalances, and I look for a good reaction" (`qriptal_wveE-r1mzTc_raw.txt:112-114`).
- Higher timeframes weigh more: "you need higher time frame imbalances" (`qriptal_dYlk1gtY2Lk_raw.txt:96-97`).
His formula and thresholds are not public; everything numeric below is OURS (the same detector as `imb.py`, defined before any outcome was read).

| item | rule | label |
|---|---|---|
| candles | Binance USD-M BTCUSDT 1m resampled to 1h, 4h, 12h, 1d by UTC epoch buckets (`imb.resample`; bar-for-bar equal to Binance's own TF klines, README section 3.1). 30m is excluded (chance explains 75-95 % of its label hits, README 3) | OURS |
| volume anomaly | `rv = volume / median(volume of the prior 50 bars of the same TF)` (`imb.rel_volume`); k = 2.0 primary (the B171 primary), k = 3.0 sensitivity | OURS |
| body | `bf = |close - open| / (high - low)`; small <= 0.30, large >= 0.70 (`imb.SMALL_BODY`, `imb.LARGE_BODY`) | OURS |
| closed only | a candle counts for a touch bar opening at time t only if candle_open + TF <= t | OURS (causality) |
| window | candle opened within the last 7 / 14 / 30 / 60 days for 1h / 4h / 12h / 1d (`imb.LOOKBACK_DAYS`) | OURS |
| at the level | the candle midpoint (high+low)/2 lies within 0.25 % of the level (`imb.level_match(.., "mid")`, `imb.TOL_MID`): he uses "the midpoint or the open of an imbalance candle as support/resistance" (README section 2). Direction of the candle is not used | OURS |
| SMALL flag | any TF has a closed candle at the level with rv >= k and bf <= 0.30 | OURS |
| LARGE flag | any TF has a closed candle at the level with rv >= k and bf >= 0.70 | OURS |
| CTRL flag | any TF has a closed candle at the level with rv < 1.2 and bf <= 0.30 (same shape, no volume anomaly; the B171 `normal_small` control) | OURS |
| NaN | rv or bf undefined (fewer than 50 prior bars, zero range): no flag | OURS |

Why a closed candle and not the touch bar: the touch bar is still forming at the entry, so its volume is not knowable. The condition therefore reads
"an anomalous candle has already printed at this price", which is also how he marks imbalances (zones from the past, README section 2).
The third part of his rule, the reaction (a wick), is the layer's own outcome here (the entry is at the touch, the hold is the reaction). A wick-confirmation entry is NOT tested.

## 4. Hypotheses, groups, statistics
Groups (a trade can sit in several): IMB = SMALL flag at k; NOIMB = no SMALL flag. LARGE = LARGE flag at k; NOLARGE = no LARGE flag.
CTRLONLY = CTRL flag and no SMALL flag (the shape-only control). ALL = every layer trade.
Statistics (`research_kit`): mean net R per group, day-clustered SE (`cluster_mean_se`), difference with day-clustered SE (`cluster_diff`, same-day covariance counted),
t = estimate / SE, two-sided normal p (`norm_p_two`), MDE = 2.8 x SE.
Halves (stability): H1 = touch days 2022-04-01..2023-03-31, H2 = 2023-04-01..2024-06-30.

- **H1 (filter).** Primary cell: k = 2, rr = 1. Delta1 = mean(IMB) - mean(NOIMB).
  PASS_IMB iff all of: (a) n_IMB >= 200, n_NOIMB >= 200 and IMB spans >= 100 days; (b) mean net R of IMB > 0 with t >= 2.0;
  (c) Delta1 > 0 and the Holm-adjusted p (m = 16, below) <= 0.05; (d) Delta1 > 0 in H1 and in H2; (e) mean(IMB) > mean(CTRLONLY) (point estimate).
  INCONCLUSIVE iff (a) fails, or the verdict would be FAIL while MDE(Delta1) > 0.15 R (a FAIL below that power reads INCONCLUSIVE).
  FAIL otherwise. Sub-label printed with a FAIL: "filter lifts" if (c) and (d) hold but (b) fails (the filter helps and the layer still loses to costs), else "no lift".
- **H2 (veto).** Primary cell: k = 2, rr = 1. Delta2 = mean(LARGE) - mean(NOLARGE).
  PASS_VETO iff: n_LARGE >= 200; Delta2 < 0 with Holm-adjusted p (m = 16) <= 0.05; Delta2 < 0 in H1 and in H2.
  INCONCLUSIVE iff n_LARGE < 200, or the verdict would be FAIL while MDE(Delta2) > 0.15 R. FAIL otherwise. (Plausible effect 0.15 R: OURS, about 40 % of the cost of one trade.)
- Holm: m = 16 = 14 variants already read on DEV (`verdicts.py count --split DEV`, run 2026-10-16) + these 2 primaries. p-values of H1 and H2 are Holm-adjusted together.
- A PASS only qualifies the frozen rule for one VALIDATION run on a separate card. Nothing trades. HOLDOUT sealed (operator).
- Every cell not named H1/H2 is descriptive: it can inform the next hypothesis, never rescue a FAIL, never be reported as a result without the primary next to it.

## 5. Declared trial count: 28 outcome cells (2 verdict-bearing)
| block | cells |
|---|---|
| verdict-bearing: H1 (SMALL, k2, rr1), H2 (LARGE, k2, rr1) | 2 |
| sensitivity: SMALL and LARGE x k {2,3} x rr {1,2}, minus the two above | 6 |
| control CTRLONLY at rr 1 and rr 2 | 2 |
| per-TF SMALL (1h, 4h, 12h, 1d), k2, rr1 | 4 |
| base layer ALL at rr 1 and rr 2 | 2 |
| halves H1/H2 of the two primaries | 4 |
| base layer by family (8 KEEP families), rr1 (stratified readout, B154) | 8 |
One layer encoding, one detector family, one DEV window, one run. The study row goes to `research/VERDICTS.csv` and the cells to `trials.csv`.

## 6. Power (computed by the counts step, no outcome)
Expected touches: about 20 per day x 820 days; a 1R:1R bracket has unit-sized outcomes, so SD per trade is about 1 R.
`run_filter.py counts` prints n, days, and the share carrying each flag (no outcome column). The n >= 200 gates above are the only use of those counts;
no definition in sections 2-3 is changed after seeing them. If a flag share is degenerate (< 2 % or > 90 % of trades), RESULT.md says so and the test reads as weak, not re-specified.

## 7. Known traps (each a check in the script or the tests)
1. Imbalance candle closed before the touch bar opens, and no candle from the touch day's future (hand-built join test).
2. Side from the previous bar's close, not the touch bar's.
3. Touch bar: no credit for a target move that may have come before the fill.
4. Stop first when one bar holds both; gap through the stop fills at the open.
5. Same-price levels are one trade (dedup), so duplicated families do not double count.
6. Day-clustered SE; no i.i.d. t. Trades of one day overlap.
7. Level builder blocks equal a longer window (look-ahead-free wrapper).
8. Venue: a PASS is a Binance-tape finding; Deribit fills need a separate execution check. Touch fill at the level is optimistic.

## 8. Outputs
`filter_join.py` (library), `test_filter_join.py`, `run_filter.py` (`counts`, `check-levels`, `run`), `COUNTS.md`, `events_dev.csv` (flags, no outcome),
`trades_dev.csv` (after the run), `trials.csv`, `RESULT.md` (verdict words first, then the verdict-arms table, the cells, the trial count, the parameter labels).
