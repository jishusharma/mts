# Schema Specification - Version 5.1.0

Written: 2026-09-16
Source: the compiled-output audit tables A and C, read from disk.

## Purpose

The runtime engine needs session-relative context: where today opened, today's
high and low, and where price sits inside that range. None of that exists today.
This spec adds sixteen session fields as a new snapshot block called session,
and lists seven existing blocks that need corrections.

## The sixteen new fields

| field | type | unit | anchor | compute site | write site |
|---|---|---|---|---|---|
| session_open_price | float | price | trade_session_utc | Java, at session boundary | snapshot.session.open_price |
| session_high | float | price | trade_session_utc | Java, updated each cycle | snapshot.session.high |
| session_low | float | price | trade_session_utc | Java, updated each cycle | snapshot.session.low |
| range_position_pct | float | percent 0-100 | trade_session_utc | Python, from high and low | snapshot.session.range_position_pct |
| gap_from_prior_close | float | price | prior session close | Java, session open vs prior close | snapshot.session.gap_from_prior_close |
| gap_direction | string | up/down/flat | prior session close | Python, derived | snapshot.session.gap_direction |
| initial_balance_high | float | price | trade_session_utc | Java, first N minutes | snapshot.session.initial_balance_high |
| initial_balance_low | float | price | trade_session_utc | Java, first N minutes | snapshot.session.initial_balance_low |
| initial_balance_window_minutes | int | minutes | n/a | config constant | snapshot.session.initial_balance_window_minutes |
| day_type | string | trend/balance/transition/UNKNOWN | n/a | DEFERRED 2026-09-16. VP shape classifier returns B near-constantly; not a reliable source. Build a proper classifier as its own task (see L29). Emit UNKNOWN until then. | snapshot.session.day_type |
| day_type_confidence | string | low/medium/high/none | n/a | DEFERRED with day_type. Emit none until classifier exists. | snapshot.session.day_type_confidence |
| session_vwap_anchor_utc | string | ISO 8601 UTC | n/a | Java, echoed at session start | snapshot.session.vwap_anchor_utc |
| open_location | string | above_value/in_value/below_value | trade_session_utc | Python, session open vs value area | snapshot.session.open_location |
| session_bias | object | {direction, text, committed_at_utc} | n/a | DEFERRED 2026-09-16. Not a Java-emitted field. Echoed by a future runtime tool that reads session_state.json. The other fifteen fields shipped in MarketDataSnapshot.java buildSession(). | snapshot.session.bias |
| sweep_flag | bool | true/false | trade_session_utc | Python, price vs prior day high/low | snapshot.session.sweep_flag |
| liquidity_sweep_direction | string | above/below/none | trade_session_utc | Python | snapshot.session.liquidity_sweep_direction |

## Two anchors

The existing anchor is midnight UTC. It is already in the cvd block, called
session_start_utc. It marks the start of the UTC trading day.

The new anchor is the US cash market open. It is DST-aware. 13:30 UTC in
summer (EDT, UTC-4), 14:30 UTC in winter (EST, UTC-5). It marks the start of the session the engine
actually trades.

Existing fields stay on the UTC anchor. New session fields use the US cash
open anchor.

## Compute order

Session open, high, and low first. Range position and sweep flag depend on
high and low. Initial balance depends on a time window from session open.
Day type depends on existing VP shape and VWAP slope. Session bias is
independent.

## Java versus Python

Java side, in MarketDataSnapshot.java: session open, high, low, gap from prior
close, session VWAP anchor, initial balance high and low. These need
tick-level data that Python does not see.

Python side, in mts_math.py: range position, day type, day type confidence,
open location, sweep flag, liquidity sweep direction. These derive from data
Java already writes.

Config constant: initial balance window length, echoed into the snapshot for
reproducibility.

## Backward compatibility

Old snapshot readers ignore the new block because they only read fields they
already know. New readers find the block. No existing field is renamed or
removed.

## Corrections to existing blocks

| block | issue | action |
|---|---|---|
| top-level metadata | three declared fields not emitted | confirm omission or add back |
| order_book_depth | two declared fields not emitted | demote to optional |
| open_interest | declared value replaced by direction | update schema |
| long_short_ratio | never emitted | mark deprecated |
| oi_breakdown | emitted but not declared | add to schema |
| naked_pocs | declared but not in snapshot | align schema and emitter |
| setup_alerts | declared but superseded | mark deprecated |

## Open decisions

1. Confirm the two anchors.
2. Set the initial balance window length.
3. Confirm sweep flag scope: prior day only, or prior day plus current session.
4. RESOLVED 2026-09-16: day type source deferred. Do not reuse VP shape. See L29.

## End
