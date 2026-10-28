# T040 - TICK-BASED DELTA LAYER

Register row: MyTradingSys/research/BUGS.md T040.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (operator, 2026-09-22)

this was asked to worked upon - i need a worker for this for the new python layer

Attached parent note (source: operator, external). Tick-delta section quoted verbatim:

## The tick-based delta layer

- A standalone Python process subscribing to the raw tick feed (independent of the candle-close snapshot writer)
- Computes fast deltas on selected indicators (price, CVD, whatever else proves useful) over a short rolling tick window
- Checks against a threshold - only when crossed does it emit an event (avoids flooding the assistant with tick noise)
- Writes to a separate event stream/file, tagged clearly as source: tick vs source: candle, so the assistant's context always knows the granularity and recency of what it is looking at
- Needs its own cooldown, same as the existing candle-alert cooldown, or tick noise will spam it constantly

One thing worth flagging for your DSA/research protocol: any tick-based thresholds you pick (what counts as a "significant" CVD delta, say) will need the same Tom-citation-or-documented-exception treatment your other indicators go through - this is new rule surface, not just plumbing, so it likely needs to go through the same research-tier process before it's trusted in a live decision.

## STATE

2026-09-22 OPEN. Design not started. Worker dispatch created: Dumps/workers/T040_tick_delta/DISPATCH.md
Constraint: read-only against the engine. No verdict-path wiring. Threshold values are new rule surface, must go through research-tier process before trust.

## UPDATES (chronological, newest last)
### 2026-09-24T09:45Z - operator clarification, session MTS-2026-09-24-0639Z

Scope clarified by operator. Tick layer is not about recording ticks. It is
about flagging unusual changes. Verbatim operator text below.

> well! i think we need to separate things here! This tick based is diff
> python layer i need to detect only un usual candles - we will not record
> all ticks but only flag unusual increase or decrease(the change) in price
> or cvd or volume or oi or net delta etc.
>
> There is sub task for it - we need to refine this -> "For indicators like
> CVD, OI, Net Delta -> For a historical data set, duration/range of ALL
> TIME using our Binance exchange API -> Compute for each time frame 1m,
> 2m, 3m, 5m, 10m and 15 minutes ->
>
> Our goal is to find out for example take 1 min -> Check the highest
> readings for 1 min all time historical data with Binance API ->
>
> Then the second highest 1min reading and check the diff from 1st ->
> check third highest and check the diff from 2nd -> In this way detect a
> range to group these as per categories of severity/intensity/strength ->
>
> Also note the time period (when it happened - session info etc.) ->
> Calculate the % change in price during the corresponding time period.
>
> So this is for all indicators and all mentioned time frames.
>
> And the SAME IN THE OPPOSITE way -> We need to do the same for LOWEST
> READINGS!

Refined design (not yet built):

  Indicators:  CVD, OI, Net Delta (extendable).
  Timeframes:  1m, 2m, 3m, 5m, 10m, 15m.
  Data:        full historical dataset via Binance exchange API.
  Method:      per (indicator, timeframe):
                 - compute the raw per-bar value across all history
                 - rank readings descending (top end) and ascending
                   (bottom end)
                 - measure deltas between consecutive ranks
                 - detect natural breaks in the delta distribution
                 - bucket into severity / intensity / strength tiers
                 - record the session context (Asian, London, NY, funding
                   window) at each occurrence
                 - record the % price change over the same window
  Output:      a lookup table: indicator x timeframe x tier -> threshold
               band. Consumer emits a flag when a live reading crosses
               a tier boundary.

Threshold values from this method are data-derived, not invented. That
may satisfy the research-tier requirement for new rule surface, OR it
may not - depends on whether "empirically derived from full history"
counts as Tom-citation-or-documented-exception. Decide before building.

Status: OPEN. Design refined. Not started.
- 2026-09-28 s3: 091 reply PARTIAL -> tick_extremes.py.new passes 16/17 Sonnet tests; fails test_shape_and_skips_undersized_timeframes (key "volume" missing from tier table). Next: repair spec with that failure, or 1-line fix + re-gate. 092/093 + audit 094-098 queued.
