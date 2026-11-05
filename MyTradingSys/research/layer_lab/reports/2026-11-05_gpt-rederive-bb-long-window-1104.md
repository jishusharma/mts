BLOCKED - headline counts: 360 weeks total; 0 primary Malkan bear weeks; 57 P40 proxy bear weeks.

## Scope and method

Read `MyTradingSys/research/bb_long_window_2026-11-04/RESULT_LONG.md` (lines 1?44), `counts_long.csv` (header plus matching aggregate records), and `MyTradingSys/backtest/layers/FORMULAS.md` (?13, lines 350?361). Parsed the CSV with Python `csv.DictReader`; no study script was used.

The CSV has counts, days, fill rate, stop percentage, and signal fields, but no per-trade gross return, price in/out, exit, funding, or aggregate gross-return field. A sample record is `counts_long.csv:2`: A_r2r/15m/ALL/signal/range/both has n=9008, days=1560, signals=9008, and no return field. Therefore fee-net returns cannot be independently computed. FORMULAS ?13 defines `net = gross - fee_rt - slip_rt - side_sign * sum(funding)` and explicitly applies only to C1/C2/C3. RESULT_LONG states a separate spot-study round-trip cost of 0.14% at lines 2 and 5, but the required gross returns are absent from `counts_long.csv`; subtracting a fee from counts cannot recover a net return.

## Headline audit

Each row is MATCH only for the reported sample count, directly matched to the cited CSV record. The fee-net return in every paired row is NOT_IN_DATA for the reason above. `RESULT_LONG.md` line citations identify the matched claim.

| RESULT_LONG headline | Reported | CSV result | Verdict / evidence |
|---|---:|---:|---|
| Primary bear weeks (line 1) | 0 | NOT_IN_DATA | NOT_IN_DATA: weekly regime counts are not in counts_long.csv. |
| P40 proxy weeks (line 1) | 57 | NOT_IN_DATA | NOT_IN_DATA: weekly regime counts are not in counts_long.csv. |
| A 15m range signal n (line 13) | 9008 | 9008 | MATCH ? counts_long.csv:2 (`n`). |
| A 15m range signal net (line 13) | -0.128% | NOT_IN_DATA | NOT_IN_DATA ? no gross return/outcome data; formula inputs unavailable. |
| A ungated tagged control n (line 13) | 12066 | 12066 | MATCH ? counts_long.csv:47 (`n`). |
| A ungated tagged control net (line 13) | -0.118% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A bull n (line 13) | 3058 | 3058 | MATCH ? counts_long.csv:92 (`n`). |
| A bull net (line 13) | -0.087% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A 15m wide-band n (line 14) | 3580 | 3580 | MATCH ? counts_long.csv:3 (`n`). |
| A 15m wide-band net (line 14) | -0.133% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A 15m narrow-band n (line 14) | 5428 | 5428 | MATCH ? counts_long.csv:4 (`n`). |
| A 15m narrow-band net (line 14) | -0.125% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A 1h range n (line 14) | 2226 | 2226 | MATCH ? counts_long.csv:452 (`n`). |
| A 1h range net (line 14) | -0.103% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A 4h range n (line 14) | 548 | 548 | MATCH ? counts_long.csv:902 (`n`). |
| A 4h range net (line 14) | -0.091% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| A retest fills / signals (line 16) | 9007 / 9008 | 9007 / 9008 | MATCH ? counts_long.csv:227 (`n` / `signals`). |
| A retest net (line 16) | -0.127% | NOT_IN_DATA | NOT_IN_DATA ? gross returns absent. |
| B range tagged k=0.25 n (line 19; range fill series) | 1590 | 1590 | MATCH ? counts_long.csv:1352 (`fills` / `n`). |
| B range tagged k=0.5 n (line 19; range fill series) | 1660 | 1660 | MATCH ? counts_long.csv:1487 (`fills` / `n`). |
| B range tagged k=1.0 n (line 19; range fill series) | 1717 | 1717 | MATCH ? counts_long.csv:1622 (`fills` / `n`). |
| B P40 k=0.25 n (line 12) | 359 | 359 | MATCH ? counts_long.csv:1370 (`fills` / `n`). |
| B P40 k=0.5 n (line 12) | within 359?385 | 373 | MATCH ? counts_long.csv:1505 (`fills` / `n`). |
| B P40 k=1.0 n (line 12) | within 359?385 | 385 | MATCH ? counts_long.csv:1640 (`fills` / `n`). |
| B range tagged asia k=0.25 fee-net (line 17) | -0.045% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged asia k=0.5 fee-net (line 17) | -0.065% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged asia k=1.0 fee-net (line 17) | -0.084% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged london k=0.25 fee-net (line 17) | -0.208% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged london k=0.5 fee-net (line 17) | -0.212% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged london k=1.0 fee-net (line 17) | -0.238% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B range tagged NY fee-net range (line 17) | -0.139% to -0.144% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |
| B P40 positive fee-net examples (line 18) | +0.083%, +0.049%, +0.037% | NOT_IN_DATA | NOT_IN_DATA ? return observations absent. |

## Follow-up

No follow-up card created. Blocked: the supplied aggregate counts file does not contain the gross return observations needed to apply even a known fee formula. No task completion command was run because the task instruction says not to mark a blocked card done.
