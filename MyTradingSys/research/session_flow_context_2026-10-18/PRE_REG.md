# PRE-REGISTRATION: context-conditioned session flow states (BTCUSDT perp, DEV only, descriptive state study)

Card: `context-conditioned-session-flow-states`. Operator claim (2026-10-18): price / CVD / OI behaviour is stable only inside a context
(HTF balance vs trend, 10-20d range position, volatility percentile, OI trend, weekday), not across the whole year.
Labels: SOURCED = quote + file:line; OURS = judgement (chosen here, before any outcome was read).
Frozen: 2026-10-23, before `event_table.py` was ever run. `build_rows.py` was run once to produce `rows_dev.csv` (it contains the
next-session columns) and only row COUNTS per pattern x cell were printed (power table, s.7); no outcome mean, sign or SE was looked at.

## 0. Why this is not the closed "session-extreme fade" family
`verdicts.py check` BLOCKs on `context_factors_2026-10-16` / `context_factors_pit_2026-10-16` (kill scope: session-extreme fade with delta
flow on 1m BTC, a TRADE test with entries, stops and R). This study opens no trade: it measures the next-session return after a
session state, and asks whether the effect's sign/size differs across context cells. Different hypothesis (heterogeneity of a state
effect, not an entry rule), different unit (session, next-session return in bps, not R), no stops, no fills. If the kill scope of
that family is read to cover state studies too, this study stops at its report and no detector/chart/layer work follows from it either way.

## 1. Data and splits
Futures UM BTCUSDT: 1m klines (`Dumps/backtest/raw/klines`, taker_buy_volume col 9) and 5m metrics (`Dumps/backtest/raw/metrics`,
sum_open_interest col 2), via `MyTradingSys/backtest/bt/bt_data.py`. **Data gate (card step 1) is only partly met:** the daily metrics files
on disk start 2025-09-01 (391 files to 2026-09-26), not 2020-09-01 (`fetch_binance_archive.py:14,36`; `backtest_gap_review_2026-10-13/REPORT.md:141`
says the archive starts 2020-09-01, so the older files were never fetched). Binance `openInterestHist` keeps 30 days only (out of scope).
Decision (OURS, conservative): run the first slice on what exists, state the power limit, leave the long-history fetch on the card.
Splits by session start date (all OURS): WARMUP 2025-09-01..09-30 (feature look-back only), **DEV 2025-10-01..2026-02-28**,
VALIDATION 2026-03-01..06-30, HOLDOUT 2026-07-01.. . `build_rows.py` loads only bars with open time < 2026-03-01 and raises on any
other split; VALIDATION and HOLDOUT are unread. The last DEV session has no next session on disk, so it carries no outcome (dropped from tests).

## 2. Units and rows
Session split UTC (OURS): ASIA 00:00-08:00, LDN 08:00-13:30, US 13:30-20:00, LATE 20:00-24:00. A session needs >= 90 % of its 1m bars (OURS).
Per session: `chg_bps` = (close / open - 1) 1e4; taker delta = sum(2 tbv - v) (FORMULAS.md s.14 / `bt_data.cvd_delta`), `delta_norm` = delta / volume;
`oi_chg` = OI(end) / OI(start) - 1 where OI(t) = latest 5m sample with stamp <= t - 1 ms and age <= 10 min, else NaN (NOT_IN_DATA, never 0; the
sample stamped exactly at the session end is treated as not yet known, OURS); `range_pct` = (high - low) / open.
Outcome (the only forward-looking columns): `next_ret_bps` and `next_range_pct` of the immediately following session (must start at this session's end).

## 3. Labels (all OURS unless marked)
- **Quadrant** (price x OI sign): NEW_LONG (up, OI up), SHORT_COVER (up, OI down), NEW_SHORT (down, OI up), LONG_LIQ (down, OI down); zero change or OI NaN = NA. `delta_agree` = sign(delta) == sign(price) stored, not tested.
- **Sweep-reclaim**: high > prior-24h high AND close < that prior high = SR_BEAR; low < prior-24h low AND close > it = SR_BULL; both = BOTH, neither = NONE (a close beyond the level is acceptance, not a reclaim).
- **Context cells** (all as of the session end, bars with open time + 1 m <= end):
  1. `htf`: 30-day return (close / open 30 d earlier - 1): UP > +7.5 %, DOWN < -7.5 %, else BALANCE. Threshold **SOURCED from repo code** `MyTradingSys/backtest/tom_bt.py:290` (`trend_tag(ret30, thr=0.075)`), not a trader's words; the 30 d window follows it.
  2. `rangepos`: close position in the trailing **15-day** high/low (OURS, middle of the operator's 10-20 d): LOW < 1/3, HIGH > 2/3, else MID.
  3. `vol`: range_pct percentile among the previous 20 sessions of the same name (>= 10 needed): LOW <= 1/3, HIGH >= 2/3, else MID.
  4. `oitrend`: OI change over the last 5 days: UP > +2 %, DOWN < -2 %, else FLAT.
  5. `wkend`: session start weekday Sat/Sun = WEEKEND else WEEKDAY.
- **Patterns** (6): the four quadrants, SR_BEAR, SR_BULL.
- **Signed outcome** x = direction * next_ret_bps, direction = sign(session chg) for quadrant patterns (continuation), -1 for SR_BEAR, +1 for SR_BULL.

## 4. Estimands
For each pattern x context cell (and the ALL cell): n, distinct days, mean x, **day-clustered SE** (sum of within-day deviations / n, no small-sample
correction), t, realised MDE = (z_Holm + 0.84) * SE with m = 87 (z = 3.44), H1/H2 sign agreement (H1 = dates < 2025-12-16, H2 = later), mean next_range_pct.
Cost reference: 12 bps round trip (FORMULAS.md s.13: 10 bps taker + 2 bps slippage). No costs enter the tests (state study).

## 5. The operator's claim, made testable (applied verbatim)
"Stable within a context, not across": for each pattern x context dimension (6 x 5 = 30 tests) a cluster-robust Wald test that the cell means are
equal (cells with >= 15 distinct days only; chi-square survival function implemented in `event_table.py`, checked against known values).
Holm/Bonferroni family **m = 87** = 57 DEV variants already read repo-wide (`verdicts.py count --split DEV`, 2026-10-23) + 30 here; alpha = 0.05 / 87 = 5.7e-4.
- **CONSISTENT-DEV**: at least one test has p <= alpha. Only then is one VALIDATION check allowed (s.8). Within-cell H1/H2 agreement is reported next to it, not part of the rule.
- **INCONCLUSIVE (underpowered)**: no test passes AND fewer than half of the context cells are powered (MDE <= 50 bps, OURS = about 4x the 12 bps round trip, and >= 15 distinct days).
- **NOT SUPPORTED on DEV**: no test passes and at least half of the cells are powered.
No other verdict word. A cell mean is never traded on; "trade advice" is out of scope.

## 6. Kill / next
FAIL (= NOT SUPPORTED) ends the heterogeneity claim for the 4 quadrant + 2 sweep-reclaim patterns on the 5-month DEV window only (Oct 2025 to Feb 2026; 13 months of OI exist on disk, the rest is sealed); it does not speak for 2020-2025.
INCONCLUSIVE keeps the claim open and the next step is the long OI fetch (desk, DSA-NUC: `fetch_binance_archive.py` metrics 2020-09-01..2025-08-31), then the same code re-run
with a new PRE_REG that re-cuts DEV (the splits above would then be re-registered before any read, OURS).

## 7. Power (count-only, printed before freeze; `rows_dev.csv`: first build 600 rows / 150 days; a loop bug skipped 2026-02-28 and the corrected file has 604 / 151; counts below are from the first build, outcomes unread)
Events with an outcome, distinct days: NEW_LONG 143 / 100, SHORT_COVER 150 / 104, NEW_SHORT 147 / 93, LONG_LIQ 159 / 110, SR_BEAR 55 / 46, SR_BULL 63 / 54.
Cells run from 2 to ~116 events (htf UP has 2-16 per pattern). `prereg_gate.py --n 25 --sd 1.0 --cost 0.12 --m 87` (n = a typical cell in days) prints
**BLOCK** (MDE 0.857 sd + cost vs 0.30): at m = 87 an ordinary cell cannot detect anything below about 0.9 sd of the per-event outcome, and 0.30 sd needs 566 days per cell. So per
template item 0e this is declared **INCONCLUSIVE in advance for every single cell**; only the pooled Wald heterogeneity tests (s.5) can return CONSISTENT-DEV, and only for a very large effect.
The gate's R units do not apply (outcome in bps, no stops); sd(per-event outcome) is deliberately NOT measured before the freeze.

## 8. Seal
VALIDATION: one read, only after a CONSISTENT-DEV verdict, with the same code and thresholds. HOLDOUT: once, after VALIDATION, never tuned. Any change to a threshold above after
the first `event_table.py` run is a new variant in `trials.csv` and a new Holm count. Trial ledger row: `MyTradingSys/research/TRIAL_LEDGER.csv` (study `session_flow_context_2026-10-18`).
