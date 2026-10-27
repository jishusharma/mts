# SESSION ANCHOR OPTIONS -- NOTE
# Written: 2026-09-18 by MTS-2026-09-18-0456Z
# Status: NOTE ONLY. No spec. No engine change. No verdict wiring.
# Rule 32 applies to any future wiring. Rule 33 applies to any new field.

## QUESTION

Should the runtime emit session-anchored data feeds (Asian, European, US,
after-hours, each with its own open/high/low/VWAP/opening range) in addition
to the current single US-cash-open anchor? Or UTC-anchored only? Or both?

## TODAY

Two anchors exist in one snapshot.

1. CVD anchor = 00:00 UTC daily. Field cvd.session_start_utc.
2. Session block anchor = US cash open. Field session.vwap_anchor_utc.
   Currently 13:30 UTC in summer, 14:30 UTC in winter.

Every other session field inherits the US anchor: open, high, low,
range_position_pct, initial_balance_high/low, gap_from_prior_close,
sweep_flag, liquidity_sweep_direction.

Consequence: before 13:30 UTC the session block is all zeros. Asian and
European trades are invisible to every session-scoped field. No session
high, no session low, no session VWAP, no opening range, no sweep flag.

## OPTION A -- UTC ANCHOR ONLY (current)

One anchor at 00:00 UTC. The whole UTC day is one session. session.open is
the first print after midnight UTC. session.high/low span 24 hours.

Gains: simple, comparable across days, already implemented.
Losses: no session structure. Cannot see Asian range, London range, or the
handoffs at 08:00 and 13:30 UTC. Cannot evaluate SR-001 through SR-010
against anything but wall clock.

## OPTION B -- SESSION ANCHORS ONLY

Four anchors: Asian 00:00, European 08:00, US cash open 13:30/14:30,
after-hours 21:00. Each session owns open, high, low, VWAP, opening range
(first 30 min), range position, sweep flag.

Gains: session structure visible. Asian range becomes a level. London range
becomes a level. Per-session VWAP. Per-session opening range. Handoff
questions become answerable (did London sweep the Asian high, did the US
open sweep the London low).
Losses: four times the session data. Cross-day comparison harder. Tom has
no session rules -- this is crypto adaptation. Drift risk if session
boundaries shift.

## OPTION C -- BOTH TOGETHER

Emit UTC-anchored daily block and per-session blocks in the same snapshot.
UTC block answers "how is the day going." Session blocks answer "how is this
session going."

Gains: day-level context plus session-level context. Both questions
answerable from one paste.
Losses: largest payload. Two anchor semantics live side by side. Risk that
a reader mixes them, which is the same failure class the dictionary already
flags for CVD (DSA vs CoinGlass anchor mismatch).

## WHAT EACH OPTION LETS US EVALUATE

| Question | A | B | C |
|---|---|---|---|
| Is price inside today's UTC range | yes | no | yes |
| Is price inside the Asian range | no | yes | yes |
| Was the Asian high swept in London | no | yes | yes |
| Was the London low swept at the US open | no | yes | yes |
| Is price above Asian VWAP but below European VWAP | no | yes | yes |
| Is today a wide-range day | yes | no | yes |
| Is this session a wide-range session | no | yes | yes |
| Can SR-001 fire on "US open AND outside Asian range" | no | yes | yes |

## CONSTRAINTS

1. Tom defines only the US session. Asian, European, and after-hours are
   crypto adaptation, from session_timing_rules.md. Research-backed, not
   Tom-backed. They stay informational until Rule 32 proves a verdict
   change.
2. Rule 33: every field requested must be read by a rule. Four session
   blocks is four times the session data. Request only what a rule reads.
3. Rule 32: adding fields is annotation. Reading them in a verdict gate is
   an engine rule and must change at least one of three verdicts.
4. The engine already treats session timing as informational only. No hard
   session rule exists. That was a deliberate call.
5. Anchor ambiguity is a live bug class. Dictionary flags three family
   confusions already (flow vs positioning, anchor mismatch, same name
   different source). A two-anchor snapshot must label each field with its
   anchor or it compounds the existing problem.

## RECOMMENDED SEQUENCE IF WE PROCEED

Phase 1, annotation only:
- Add session.asian, session.europe, session.after blocks alongside the
  existing US block.
- Each carries open, high, low, vwap, opening_range_high, opening_range_low,
  range_position_pct.
- Add a handoff block: asian_high_swept_in_europe, asian_low_swept_in_europe,
  europe_high_swept_in_us, europe_low_swept_in_us.
- Every field carries its anchor explicitly.
- Do not read any of it in the verdict path.

Phase 2, verdict wiring:
- Each rule that reads a session field is an engine rule. Rule 32 gate.
- Test set: 3 live snapshots where the rule changes the verdict.
- If zero of three change, reject as documentation bloat.

## DECISION PENDING

Option A, B, or C. No field added, no rule wired, until the user picks.

# END
## EVIDENCE

### Snapshot 2026-09-17T20:11:15.875919100Z

Source: boot paste of this session, file BTCUSDT_2026-09-17_201.json.

session block:
    vwap_anchor_utc              = 2026-09-17T13:30:00Z
    open_price                   = 76440.9
    high                         = 77096.7
    low                          = 75975.0
    gap_from_prior_close         = 266.3
    initial_balance_high         = 76676.9
    initial_balance_low          = 75975.0
    range_position_pct           = 54.94
    gap_direction                = up
    open_location                = in_value
    sweep_flag                   = true
    liquidity_sweep_direction    = above
    day_type                     = balance
    day_type_confidence          = provisional

session_timing block:
    current_session              = us_close
    funding_reset_window         = false
    us_equity_open_window        = false
    us_equity_open_in_minutes    = 1039

State: 20:11 UTC. US session, post-close. Fields populated because the
anchor at 13:30 UTC has passed.

### Snapshot 2026-09-18T05:04:15.771173300Z

Source: MTS-SESS block from the live feed, pasted by user this session.

    MTS-SESS open=0.0 hi=0.0 lo=0.0 ibH=0.0 ibL=0.0
            gap=0.0/flat loc=in_value sweep=False/none
            day=UNKNOWN/none rpos=0.0

State: 05:04 UTC. Asian session. Same field names, same snapshot schema.
Every value is zero or default because the anchor at 13:30 UTC has not
arrived. Asian trades are not reflected.

### Comparison

Same field, two snapshots, different UTC hour. Only the anchor clock
changed. Before 13:30 UTC: zeros. After 13:30 UTC: real session range.
The gap is the defect this note documents.

# END
## DECISION - 2026-09-18T09:43:33Z

Option C. Both anchors, applied as layers in different contexts.
- Session anchor (US open, 13:30 UTC): intraday decision context.
- UTC anchor (00:00): structural VWAP and CVD baseline.
Consumers pick the anchor for their scope. Do not cross-compare anchored values without explicit conversion.
Decided by user, MTS-2026-09-18-0848Z.

