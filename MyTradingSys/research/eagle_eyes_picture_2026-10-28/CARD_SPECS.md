# Eagle_Eyes card specs (2026-10-30)

Long text for task cards lives here so each card stays under the `tasks.py check` length limits. Card id = section heading.

## level-approach-study-daily-last-lower-hi

Original title (kept for reference): level-approach study on the daily "last lower high" line (operator definition: the highest high since the leg that made the latest lower low, e.g. 82,035 from 10-23) and on prior-day highs. Classify every approach as near-miss / wick-through-close-back / close-through-then-fail (1st, 2nd close) / accepted, per 1m, 5m, 15m and 1h close. Record OI, CVD, net delta, RSI and the daily BB mid at that moment, plus the forward move. Binance BTC history; descriptive first.

Done when (full): a table per approach class x TF with n, the forward move, and the confirm and invalidation sequences that best separated outcomes, as measured base rates (descriptive, fee-free, labelled). Dev/holdout split before any rule is proposed; the result feeds the live_aid panel. Before the run, PRE_REG_TEMPLATE gate 0g is answered: the line and approach classes are checked against at least 3 of the operator's dated shots (e.g. 1bb324a9ad96, 19991af5d4a3, a83eefa84968).

## anticipation-map-from-current-layer-stat

Goal (full): prepare the operator for a live trade. For the current layer state, show every plausible reading of the same data (e.g. price up + OI up = new aggressive longs, OR shorts opening into the rally, OR other exchanges doing something Binance is not). Give the probability of each (a measured base rate where we have one, else labelled UNMEASURED), the layer that would decide between them, and a prepared confirm/kill per reading.

## alerts-v2-on-both-screens-one-alert-feed

One alert feed shown on JIS-NB (desktop) and DESKTOP-F7IU69N (laptop), with a per-alert-type on/off toggle. Retire the old MTS ALERT popups. The new alert set = what the engine actually fires: signals, testnet orders, Tom/layer setups including prior-day and multi-day high/low take-and-fail, and the coil/pierce state from the live_aid panel. CRITICAL_TEST_PLAN T6: every candidate and every order produces exactly one visible alert on each screen.

## critical-test-wave-2-critical-test-plan-

CRITICAL_TEST_PLAN.md wave 2, items 6-8:
- 6: the Binance-vs-Deribit venue gap.
- 7: a funding coverage census of perp backtests.
- 8: trial count vs Minimum Backtest Length per layer verdict.

Each result goes in as a row in TEST_LEDGER.md, with a second-model review.

## level-approach-prep

Operator ask 10-30 (relayed via Supervisor C; shots 451c4523247f, bca9025ce84f, 45dbcb33e4ca): get the engine prepared at a level BEFORE price arrives. Five parts, each one a live_aid panel row and one alert:

1. **Pre-level checklist.** At about 0.5% from a marked level (prior-day high/low, 2-day, weekly, range floor, last lower high), list what the approach must show for hold vs break.
2. **Absorption signature.** Effort without result: aggressive volume or delta (taker buy/sell, CoinGlass large orders) on a push that does not extend. The measure is delta share or volume ratio vs the price move over the next N 1m bars.
3. **Who absorbed (OI).** During the failed push, OI rising = shorts opening into the buying (or longs into the selling). OI flat or falling = passive limit sellers or long profit-taking.
4. **Confirm-entry rule (descriptive, never a call).** A 5m close back through the stuck swing; the invalidation is beyond the absorption extreme.
5. **Strength = flag count.** One flag each for: absorption, OI tells, a level within 0.5%, RSI extreme, coil/pierce context, a 1m/2m/3m/5m wick rejection.

Every part is UNTESTED on our data until the study in `UNKNOWNS` below is run. The panel shows base rates only with n; otherwise it says UNMEASURED.

## pitchfork-operator-charts-prep

Operator 10-30: he drew one pitchfork years ago from 3 pivots (high/low/lower-high) and still copies that same fork (same slope and width) and pastes it shifted up/down/left/right onto later price. He finds price still respects those copies. He wants the layer prepared well and will share his pitchfork charts next.

What exists (trunk, 10-30):
- The detector has Standard, Schiff and Modified Schiff modes (`backtest/layers/pitchfork/`, 13 tests).
- Sim desk 4H tine-bounce DEV gives n=77, PF 1.24, +0.16R net. This is in-sample only; the Opus review flagged citing it as evidence HIGH.
- Java PF-REV/PF-HAG exist. Live `mts.pitchfork=true` is inert: live asks for 3 four-hour bars and the layer needs 15. Even if it fired, PF candidates cannot arm an order (side=None, PF_ARM_TRACE.md).

To do:
- **Classify shots.** Classify the operator's pitchfork shots (shot.py), record each fork's 3 pivots, TF and price scale (log vs linear).
- **Measure "copy-paste" forks.** Copy-paste forks are parallel copies with the same slope and width, anchored at a later pivot; this is close to Andrews' sliding parallels and reaction lines. Measure how often price reacts at a copied fork's median line and tines vs a random parallel with the same slope (control).
- **Pre-register first.** Write the pre-reg before any run. Holdout stays untouched.

## UNKNOWNS (open ledger rows, how to measure)

| # | Unknown | How to measure |
|---|---|---|
| U1 | Does absorption (high delta, no extension) at a level predict a reversal more often than a matched non-absorption approach? | 1m archive: approaches within 0.3% of prior-day H/L; absorption = delta share >= +0.3 (or <= -0.3) with a move under 0.1% in the next 3 bars; compare the reversal rate vs distance-matched non-absorption approaches |
| U2 | Does OI rising during a failed push mean shorts opening (a stronger fade) vs OI falling (a weaker fade)? | Needs 5m OI history (Binance futures/data openInterestHist, 30 days only, or the CoinGlass archive); split U1 events by OI change sign |
| U3 | Does the 1m/2m/3m/5m wick-rejection count at a level change the hold rate? | Count wicks with a close back inside per TF in the 15 min before a touch; hold rate by count |
| U4 | Does a 5m close back through the stuck swing beat a 1m close as confirmation (false-signal rate vs move captured)? | Same events, both rules, fee-free descriptive; dev/holdout split |
| U5 | Do copied (pasted) pitchforks attract price more than random parallels? | pitchfork-operator-charts-prep, after the operator's shots |
| U6 | Is the range floor 79.1-79.3k (10-16 low) a hold or a break? | Scenario only; scored in SCENARIO_LEDGER, never a call |
