# PIT_CONTRACT: the as-of contract for levels, phases and sessions (2026-10-16, Fable 5.1)

Rule (operator 2026-10-16): every level, zone, phase and session a backtest reads at decision bar t is built from bars
whose close is <= the decision time. Decision time = the close of bar t (features) or the open of bar t (a level "in
force" for a touch on bar t). Nothing below is tuned; every number is SOURCED (file:line) or OURS and is never varied in G3.

## 1. Level ledger schema (pivot_pattern_audit_2026-10-14/REPORT.md:41)
One row per level instance, written when it becomes available, never edited (a change = a new row with a new `algo_version`).
| field | type | meaning |
|---|---|---|
| level_id | str | `<origin>:<source_tf>:<formed_at>` |
| origin | enum | prior_day_h/l/poc/vah/val, prior_week_*, session_dev_*, weekly_dev_*, swing_high/low, fractal_high/low, A1_profile_*, A2_profile_*, vwap_session, atr_band |
| source_tf | str | bars the level is built from (1m, 5m, 1h, 1d, 1w) |
| price, zone_lo, zone_hi | float | a line (zone_lo = zone_hi) or a zone; USDT |
| formed_at | ms | open time of the last bar whose data the level uses |
| available_at | ms | first decision time at which it may be read = close of the confirming bar (fractal: close of i+n, FORMULAS 18.2; period levels: the period's end; developing profiles: each 15-min refresh, bars closed before the refresh) |
| touch_history | list | (t, side, outcome_known_at); readable once outcome_known_at <= reading time |
| age_bars | int | bars since available_at at the reading time |
| role | enum | support / resistance / flipped (first close beyond; known at that close) |
| invalidated_at | ms or null | first close beyond the level by > 1 x ATR14 of source_tf (OURS) |
| algo_version | str | builder file + git sha |
Readers join on `available_at <= decision_time`. A replaced pivot keeps its row (no repainting).

## 2. OURS definitions (written once; rows that need them)
Each definition says how it is computed from bars <= t and what a trader sees on the chart at t.

**D-SESSION BTC session anchor (OURS, CATALOGUE_AUDIT D1).** The UTC day: s = 00:00 UTC. "Prior session" = the previous
UTC day; a profile "of the session" = bars from 00:00 UTC up to the last closed bar. Chart: a vertical line at midnight UTC.
Other clocks (later variants only): US open and London with DST per `fabio/v3/day_gates.py:46-71`.
Rows: TOM-1a, TOM-2, TOM-3 (inside day), TOM-12, FAB-4, FAB-6.

**D-BAL balance (OURS).** On bars of timeframe TF, a window of N closed bars is in balance iff every one of the last N
closes lies inside [L, H] where H = max high and L = min low of the window, and (H - L) <= k x sqrt(N) x ATR_N(t)
(the Fabio v3 S1 rule, `fabio/v3/signals.py:183-205`, k = 0.8 NS-fixed), evaluated at the close of t. Defaults for G3:
TF = 5m, N = 48 (4 h); daily rows: TF = 1d, N = 10. Chart: a box drawn from the window's high to its low; price has not
closed outside it. Rows: TOM-2, TOM-7, TOM-12 (the "old balance"), FAB-1, FAB-4, KR-S3, KR-S4.

**D-PBD P / B / D profile shape by closing prices (OURS, replaces the catalogue's "taught elsewhere").** For the prior
UTC day's 1m bars build the profile (FORMULAS 18.1, w = 10). Let the day's range be split in thirds by price.
P = POC in the top third and >= 60 % of closes in the top third; b = POC in the bottom third and >= 60 % of closes in the
bottom third; D = otherwise (closes spread, POC in the middle third). Computed at 00:00 UTC for the day just closed.
Chart: where the fat part of yesterday's profile sits. Rows: TOM-1a, TOM-1b (B-profile top), TOM-2, TOM-12.

**D-THIN thin top / finished auction (OURS).** At the close of t on 5m bars: the current session's high was set within
the last 6 bars, the profile of the session (bars closed before t's open) holds < 10 % of its volume in the top
10 % of its range, and the last 3 closes are below the session high. Chart: a tail at the top of the developing
profile with single prints. Rows: TOM-1a, TOM-15, TOM-16.

**D-BIG big trade (SOURCED anchor + OURS transfer).** Fabio: "It's 30 contracts ... If you are in London, I use 20"
(DyS79Eb92Ug captions, CATALOGUE_AUDIT.md section 3.3 F-2) = about 1.5 % of NQ's average 1-minute volume in his
examples (OURS estimate of the ratio, not his words). BTC transfer: a trade (aggTrades row) is big iff its quantity
>= the 99th percentile of row quantities over the prior 30 calendar days (`orderflow_bars.py:19-23`, thr99; days with
thr_days = 0 excluded). Venue assumption: Binance USDT-M alone (OURS). Chart: the footprint's largest prints. Rows:
FAB-1, FAB-2, FAB-5, TOM-16, TOM-17.

**D-TREND healthy trend (OURS, from Tom's test "volume under the move").** On 1h bars at the close of t: the last
confirmed fractal pivot low (n = 2, FORMULAS 18.2) is above the one before it, and the developing session POC is above
the prior-day POC (VPOC shift up); mirror for down. Chart: higher lows with the profile's fat part moving up. Rows:
TOM-4 (+5), TOM-6, TOM-9, KR-S5.

**D-LEVELS prior-period levels.** Prior UTC day / ISO week high, low, close, POC, VAH, VAL from the completed period's
1m bars (FORMULAS 8 buckets, 18.1 profile); available from the first bar of the next period. Developing session /
weekly profile: refreshed on the 15-min grid from bars closed before the refresh (FORMULAS 18.4). Chart: yesterday's
lines carried forward. Rows: TOM-1a, TOM-3, TOM-4, TOM-6, TOM-12, FAB-4, FAB-6, KR-S1, KR-S2.

**D-PIVOT swing / fractal pivots.** Fractal width n (FORMULAS 18.2, strict), usable from the open of bar i+n+1;
CryptoCred body swings left = right = 2 (`cc_structure.py:11-60`), usable when confirmed_i < k. The level is the
pivot bar's high / low. Chart: a swing that has two closed bars on each side. Rows: TOM-4, TOM-6, TOM-15, KR-S12, MAL-16/17/18.

**D-STOPFLOOR cost floor (SOURCED: `TOM_ON_BTC.md:24`, `TOM_LAYER_V2_SPEC` section 11).** A row is traded in a
backtest only when its stop is >= 0.40 % of price with taker legs or >= 0.20 % with a maker entry; smaller stops are
counted, not traded. Rows: all.

## 3. Forbidden
Full-sample percentiles/terciles (tom_bt_report.py:161); a profile holding the touch bar; a CVD *level*
(`orderflow_bars.py:186-189`, series-start dependent: windowed sums only); labels at bar open; moving an alert to a
later-confirmed extreme.
