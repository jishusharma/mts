# <YYYY-MM-DD> <SYMBOL> screenshots, set <set id>
<!-- Copy this file to MyTradingSys/research/screenshots/<date>_<symbol>_<set>.md. Process: methodology/screenshot_intake.md.
     Claim rows must start with `| <id> | MATCH or MISMATCH or NOT_IN_DATA |` or `shot.py read` refuses the file. No trade advice here. -->

Shots: <12-hex id>, <12-hex id>          (every id this file covers; `shot.py list`)
Operator words: "<verbatim from the intake notice>"
Clocks: <per shot: TradingView page = UTC | footprint page = IST UTC+5:30 | other>
Pre-read (VVP-002 F.1): pass | fail: <what is missing: cursor at right edge, timeframe label, OHLC header, legends, overlays, zone markings>
Operator marks: <rays, boxes, labels the operator drew, each with the price read off the axis; pixel reads marked +-error>
Set timeframes present: <list>   missing: <list>   (a single timeframe makes this context, not a read)

## Carried context
Prior: <path of the previous read's extract of this symbol | none>   (chart extracts without this line are refused, B157)
| Prior falsifier / invalidation (as `shot.py read` lists it) | HELD / BROKEN / UNTESTED | Evidence on this chart |
|---|---|---|
| <line from the prior read> | <class> | <price/time on the new chart> |

## <id> <TF> <source>
- Window: <left edge .. right edge, clock>
- Panels and indicators: <price, VWAP, VP, OI, CVD, net delta, footprint ...>

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| A-01 | MATCH | <what the chart shows, with the number> | <file path + the number it reproduces> |
| A-02 | MISMATCH | <...> | <file + number that differs; why it is not the chart's anchoring> |
| A-03 | NOT_IN_DATA | <...> | <what is missing from disk> |

## Across timeframes (set)
| Level or event | 3m | 5m | 15m | 1h | 4h | Agree? |
|---|---|---|---|---|---|---|

## Six layers (chart_read_protocol) - only if this read names a setup
panel / neutral / cross-view / htf / falsify / invalidation: <one line each>; log with capture.py add --kind chart_read --image <shot id>

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| A-02 | finding | B### |
| A-03 | feature | FEAT-## |
