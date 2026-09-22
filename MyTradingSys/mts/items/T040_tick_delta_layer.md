# T040 - TICK-BASED DELTA LAYER

Register row: MyTradingSys/mts/research/BUGS.md T040.
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

