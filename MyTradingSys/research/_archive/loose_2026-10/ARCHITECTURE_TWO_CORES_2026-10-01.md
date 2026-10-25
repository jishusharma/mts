# ARCHITECTURE: TWO CORES + OBSERVATION LAYER
# Written 2026-10-01 by MTS-2026-10-01-1755Z-DSA-COO.
# Direction: operator directive 2026-10-01.

## DOCTRINE

Two cores. Tom core and Fabio core. Each compiled independently.
Each emits its own verdict. Each trade carries its own source flag.
Modules and observation layers never gate either core.

## WHAT A CORE IS

A core is a compiled decision engine with:
- its own input contract (snapshot fields it reads)
- its own rule set (Tom rules; Fabio rules)
- its own verdict vocabulary (Tom: WAIT_*, SETUP_FORMING, SETUP_CONFIRMED; Fabio: per FABIO_V3_SPEC models)
- its own trade plan emitter (entry, stop, target, management)
- its own trade ledger rows

## WHAT A MODULE IS

A module is a switchable computation or display, never a gate:
- RSI 40-60 (MalkanView), per timeframe
- Probability distribution layer
- Tick-delta layer (T040)
- Session-aware frame
Each module emits its own read. None edits core state. None vetoes a core verdict.

## INTEGRATION: CONSENSUS ROW

At the moment an alert fires from either core, write one row:

  consensus_<UTC>.jsonl
    snapshot_id
    utc_timestamp
    price
    tom:    { verdict, setup, side, entry, stop, target, net_rr }
    fabio:  { verdict, model, side, entry, stop, target }
    rsi:    { 1m, 3m, 15m, 1h, 4h, 1d }
    notes:  free text (optional)

Row keyed by snapshot_id. Append-only. Never edited.
Consensus is an observation. It does not gate, veto, or delay any core trade.

## TRADE FLAGS

Every trade in the ledger carries source: tom or fabio.
Every module event carries source: layer:rsi:40_60, layer:rsi:ma_60, etc.
Auto_trader already routes layer alerts to per-source testnet accounts
(auto_trader.py:67 accounts map: layer:fabio: -> fabio). The source
prefix is the flag.

## WHAT THIS CHANGES IN CODE

1. Fabio moves from loose layer alerts into a compiled core.
   Fabio core is the FABIO_V3_SPEC layer, wired as a peer to Tom core.
2. Tom core stays as-is. Compiled engine is Tom's core.
3. RSI 40-60 gets a snapshot-time observation block, per timeframe.
4. A new consensus writer runs at alert time. Read-only on cores;
   writes only the consensus jsonl.
5. Auto_trader config gains source-aware routing for Tom-core,
   Fabio-core, and RSI observation events.

## WHAT THIS DOES NOT CHANGE

- Tom core behavior. No new gates. No new core rules.
- Existing trade logic. Add, do not modify (PROJECT_VISION).
- No new extractions in this build.

## SWITCHABILITY

Each core has an enable flag. Each module has an enable flag.
Flags in a new config block. Default: Tom on, Fabio on, RSI observation on.
With any core off, its alerts stop; no other core is affected.

## ACCEPTANCE

- Two cores emit verdicts independently. Test: disable Fabio, Tom verdicts
  unchanged; disable Tom, Fabio verdicts unchanged.
- Every alert writes one consensus row. Test: fire N alerts, count N rows.
- Every trade row carries source: tom or fabio. Test: ledger scan.
- RSI observation block present per timeframe at alert time. Test: consensus
  row for a firing alert carries all six TF keys.

## OPEN

- live_runner_cli.py cited in the 1800Z chart-read at lines 159-188 does not
  exist at MyTradingSys/layers/live_runner_cli.py. Locate the real path before
  any Fabio-core wiring change.

# END
