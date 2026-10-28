# OBSERVATION CAPTURE PROTOCOL
# Purpose: every live session logs what it saw on charts and what it called, so missed trades can be counted.
# Scope: live sessions that read charts, answer trading questions, or make trade calls with the operator.
# Written 2026-10-08 (thread "Missed-trade capture pipeline"). Tool: MyTradingSys/observation/capture.py.

## THE RULE
A live session is in observation mode. It never trades, never edits the live system, and logs one capture
line the moment it gives a chart read, a trade call, a correction, or an answer worth keeping.
Logging is one command. It appends one line to a file and does nothing else.

## WHAT TO LOG
| kind | When | Must carry |
|---|---|---|
| chart_read | any read of a screenshot or chart panel | symbol, --tf, --at; label is forced to "chart read" |
| trade_call | any "long/short from X, stop Y" said in the session | --side and --stop (no invalidation, no read) |
| system_quote | a number quoted from a system paste | label is forced to "system" |
| question / answer | an operator question and the answer given | the operator's words verbatim in --text |
| correction | a read turned out wrong (live_session_protocol rule 9) | --supersedes <obs_id of the wrong one> |
| note | anything else worth keeping | text |

A chart_read with a direction is a setup: give --side, --stop (the invalidation price), and --entry and --target
when the read names them. Without --entry the setup is scored from the close of the bar holding the read.

## TIME
--at is the market time the read refers to, not when you typed it. Chart clocks differ (Binance footprint
screenshots have been on IST). A time with no offset is refused: pass --tz +05:30 for an IST chart.

## SIX LAYERS (chart_read_protocol.md)
Pass what you have: --panel --neutral --cross-view --htf --falsify --invalidation. Missing layers do not block
the capture; they are flagged six_layer_missing in the dataset. A footprint read with no POC/VAH/VAL lines on it
gets --chart-source footprint and no --zones-marked; it is flagged footprint_no_zones (VVP-002 C.1).

## COMMAND (from any checkout; data goes to the live machine's store)
```
python MyTradingSys/observation/capture.py --dir C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\runtime_data\observations add --session <session name> --kind chart_read --symbol BTCUSDT --tf 15m --at "2026-10-08 02:47" --tz +05:30 --side short --entry 83550 --stop 83700 --target 82706 --chart-source "binance footprint" --text "<the read as said>"
```
It prints `OK <obs_id> ...` or `REFUSED: <why>`. Fix and resend on REFUSED; nothing was written.

## WHAT IT IS NOT
- Not a signal. Captures never reach the gate, the auto-trader, or a dashboard verdict.
- Not system data. Numbers keep their label; a chart read stays "chart read" in every derived file.
