# Observer severity, session timing and standing context: design note (no code)

Card: observer-severity-context. Decision: OPERATOR_DECISIONS.md `d-observer-severity-context` (2026-10-29). Design only; nothing here is built, run or fitted. Live path untouched.
Label rule: every parameter is SOURCED (quote + file:line) or OURS. A fee-net out-of-sample result, not this note, decides whether a rating is kept.

## Tom quotes used (verifiable)

> "Whenever there are absolute volume peaks, the market does special things."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "It means that there is a very large buyer here who is absorbing everything that's being sold."
**Source GPS: y67l86cSqb8 | MIDDLE**

> "if you take a look at the time here, you'll see it's midday. And during lunchtime, there's usually relatively little volume in the market."
**Source GPS: wPMiyJXL0zU | MIDDLE**

Pointers: TOM_VERBATIM_INDEX.md:181 (TOM-168, volume peaks), :38 (TOM-025, large buyer absorbing), :42 (TOM-029, time of day changes volume). TOM-020 (:33) discusses cumulative delta "not being strongly supported"; excerpt is truncated in the index, so it is a pointer only, not quoted.

## (i) Severity scale per signal

Each signal gets an integer 0-3 (0 none, 1 notable, 2 strong, 3 extreme) computed from data alone at a level. The signal is a rating of how much the data stands out, never a trade trigger.

| # | signal | definition | parameter | label | cut-off rule |
|---|---|---|---|---|---|
| S1 | large-trade size | size of a single aggressive trade vs the trailing distribution of single-trade sizes in the same instrument | percentile bands 90 / 99 / 99.9 of trailing 24 h trade sizes | OURS (the idea "volume peaks matter" is SOURCED: TOM-168, TOM_VERBATIM_INDEX.md:181; "large buyer/seller at a level" TOM-025, :38; the percentiles are OURS) | tune on DEV only |
| S2 | trailing window for S1 | 24 h rolling, point-in-time | 24 h | OURS | fixed before DEV, not tuned |
| S3 | CVD / net-delta divergence at a level | price makes a higher high (or lower low) at the level while CVD over the same bars does not; rating by the size of the CVD shortfall in ATR-normalised units | window = bars since the previous swing at the level; shortfall bands | OURS (concept: Tom reads cumulative delta at levels, TOM-020, TOM_VERBATIM_INDEX.md:33, pointer only; bands OURS). Reuses the live_aid divergence/flow conventions (live_aid.html:467, :477) | DEV |
| S4 | volume vs time-of-day median | volume of the current 1 m (or 5 m) bar over the median of the same minute-of-day over the previous 20 days | ratio bands 2 / 4 / 8 | OURS (time of day changes volume: TOM-029, TOM_VERBATIM_INDEX.md:42; ratio and window OURS) | DEV |
| S5 | composite | max of S1,S3,S4, +1 when two or more are >= 2, capped at 3 | rule | OURS | fixed, not tuned |

Bands are placeholders until the evidence step. Protocol (fee-net, pre-registered): choose cut-offs on DEV; confirm once on VALIDATION; one look at HOLDOUT. If a band does not separate a forward outcome (adverse move within N minutes after the signal vs the unconditional rate, fee-net), it is dropped and the signal is shown unrated. FORMULAS.md rule: expected numbers come from MyTradingSys/backtest/layers/FORMULAS.md, computed independently, never from existing code.

Data available on disk today: Deribit trades/OI/book feeds in live_aid (testnet-safe public data); Binance public trades for DEV/VALIDATION/HOLDOUT. Where a field is missing it shows NOT_IN_DATA, as live_aid already does.

## (i-b) Session timing

Sessions in UTC with DST handled by zone, not by fixed hours:

| session | window | label |
|---|---|---|
| Asia | 00:00-08:00 UTC | OURS, matches CONTEXT_FACTORS_SPEC.md F7 `session` asia < 8 (line 186) |
| London | from 08:00 UTC | OURS, spec line 186 london < 13 |
| NY | from 13:30 UTC in US summer time (14:30 UTC in US winter time) | OURS; reconciles spec line 186 which uses a coarse `ny` start at hour 13, and T054's 13:30 UTC US cash open, DST-aware (items/T054_us_session_news_correlation.md STATE plan item 2) |
| late | after NY close, spec line 186 `ny < 21` | OURS |

Reconciliation: the F7 `session` field is an hour bucket; the observer needs minutes. Keep F7 untouched; add `minutes_since_open` = minutes since the latest session open (Asia 00:00, London 08:00, NY 13:30 DST-aware, computed from `America/New_York` 09:30 local). A large trade is reported as "NY +12 min, severity 3". The operator also noted today's DST; the date of the DST switch is computed from the zone database, never hard-coded.

T054 operator hypothesis (first 10-15 minutes after the US open matter) is a hypothesis, not a finding.

## (iv) Session-timing backtest design (no run)

Question: are large-trade clusters concentrated near session opens?

- Event: S1 >= 2 (a trade above the 99th percentile of its trailing 24 h), de-duplicated into clusters (events within 5 minutes merge; 5 minutes OURS).
- Statistic: histogram of cluster start by minutes since the latest session open, 5-minute bins, 0-120 min, for each of Asia, London, NY.
- Null: uniform placement across the day, plus a stronger null that preserves the volume-of-day shape (shuffle cluster times within the same hour-of-day across days). Report the observed count in the first 15 min vs null mean and a permutation p-value; multiple-session testing is Bonferroni-corrected (3 sessions).
- Splits: DEV for choosing bin width and de-dup gap; VALIDATION once; HOLDOUT once. No re-looks after HOLDOUT.
- Second step only if concentration holds: does the cluster direction predict the next 30-60 min fee-net move? Independent pre-registration before any run; otherwise it is descriptive only.
- Chart readings from the operator are HYPOTHESES to test, pixel-estimated, not findings: red cluster ~81,800 about 08:30 UTC (London open region); green about 19:00-20:00 UTC; red cluster at 79,830 low about 01:00-01:45 UTC (Asia). Each becomes one pre-registered check against the data on its day (a timestamp lookup in the trade tape), not a pattern claim from one chart.

## (ii) Standing context card (loaded at observer start)

A fixed card shown at the top of the observer panel, loaded once at start and re-read when the file changes. File: `MyTradingSys/system/observer_context.json` (to be created by the build card; no secrets, no positions).

| field | content now | data source | refresh | label |
|---|---|---|---|---|
| cycle_position | BTC came from about 60k to about 87k | operator statement 2026-10-29 (OPERATOR_DECISIONS d-observer-severity-context) | operator edits; stale-after 7 days shows "STALE" | OURS (operator-stated) |
| bull_trap_worry | bull-trap worry; bear market then | same | same | OURS (operator-stated) |
| four_year_cycle | 4-year cycle not complete | same | same | OURS (operator-stated) |
| cbp_bottom_view | CBP project's bottom-finding context | MyTradingSys/research/ CBP status (read-only link, not copied numbers) | when the CBP status file changes | OURS |
| key_levels | levels from live_aid Levels block | live_aid Levels block (operator-typed or computed) | each page refresh | OURS |
| price_now | last price | Deribit public feed already in live_aid | live | SOURCED feed |

Every field shows its source name and "as of" time; a field older than its refresh limit shows NOT_IN_DATA style "STALE", never a silent old value. Context never gates a trade; it is shown beside the rating.

## (iii) Plug into live_aid.html in-trade panel

Current panel (`renderInTrade`, live_aid.html:431-483) has 8 bullets. Plan: add a severity badge (0-3, with the S1/S3/S4 parts and "session +minutes") to the bullets they describe; the panel structure does not change.

| bullet | live_aid.html line | severity attached |
|---|---|---|
| 1 support / resistance | :443 | S4 at the level (volume vs same-time median) |
| 2 DOM +/-0.25% | :448 | S1 (large resting size) |
| 3 Day VWAP | :454 | none (no signal) |
| 4 divergences | :467 | S3 |
| 5 squeeze | :468-472 | S4 |
| 6 CVD vs delta | :477 | S3 and S1 (large aggressor trades in the window) |
| 7 stay confidence | :482 | shows composite S5 beside flags for/against |
| 8 rule R | :483 | unchanged; severity never changes rule R (OURS, fixed in STEPS.md) |

Context card sits above the panel; session badge ("NY +12 min") in the panel header. The new bullet text labels each rating "OURS, bands from DEV" until evidence says otherwise. Maths go in `live_aid_indicators.js` per the file's own convention (:431 comment), with tests that fail on old code and cover restart/reset state, non-trade balance moves and API errors (live-path rule); no code in this card.

Worked example, 10-28 about 81,800 top sell, from data alone (to be reproduced by the build card from the trade tape; numbers below are the design target, not results): at ~14:00 UTC (NY +30 min on 10-28, US summer time ended 2026-11-01 so NY open was 13:30 UTC) the observer should show S1 = 3 if the sell prints above the 99.9th percentile of the trailing 24 h, S4 >= 2 if volume is over twice the same-minute median, S3 >= 1 if CVD fails to confirm the high, composite 3, "NY +30 min", context card "bull-trap worry" beside it. Whether the data actually gives that is the check; the chart reading (red bubbles ~81,800) is a hypothesis.

## Build order for the follow-up card (not this one)

1. Replay tool over stored trade tape: compute S1, S3, S4 for 10-28 and print the worked example. 2. Session-timing backtest on DEV, then VALIDATION, then HOLDOUT. 3. Context card file and loader. 4. live_aid plug-in with tests. Each step ships separately; (4) only after (1)-(2) give a fee-net reason to keep a rating.
