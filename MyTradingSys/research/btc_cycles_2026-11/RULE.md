# Cycle-bottom long (testnet) - written rule

Operator 2026-11-06 (d-carry-dropped-leverage-direction-1106, d-phase-first-method-1106): low-leverage long near a confirmed cycle
bottom, bought on or after a good retest, held long. Phase-first: no long backtest precondition; the testnet run is the record.
Testnet only. The trade is operator-called via the operator-called testnet tool; this folder places no orders. Daily line: `python MyTradingSys/research/btc_cycles_2026-11/cycle_bottom_flag.py`.

Labels: SOURCED = quoted from an analyst row (`scripts/dev/analyst_levels.py`, CBP store) or cycles.md; OURS = our choice.

| # | Item | Value | Label |
|---|---|---|---|
| 1 | Clock window | peak 2025-10-06 + 363..406 days = 2026-10-04 .. 2026-11-16 (cycles 1-3 peak-to-bottom 406, 363, 376 d) | SOURCED cycles.md |
| 2 | Reclaim level | 5-day close above 80,450 | SOURCED Krown 2026-11-05: "2-day close above 80,350 needed; 3-day close above 79,675; 5-day close above 80,450" |
| 3 | Weekly floor | last completed weekly close >= 75,000 | SOURCED Krown 2026-11-05: "75,000 weekly close is his line in the sand" |
| 4 | 5-day block anchor | blocks anchored 1970-01-01, close = last day of block | OURS (analyst anchor unstated) |
| 5 | Weeks | Monday-Sunday UTC, close = Sunday close | OURS |
| 6 | Bottom confirmed | #2 AND #3 on completed bars only, AND either inside the window, or after it (day > 2026-11-16) with no completed daily low since the peak under 57,800 (the July bottom stands) | OURS combination of SOURCED parts; 57,800 SOURCED BIBLE.md |
| 7 | Entry | after confirmation, a day whose low is within 2 % above 80,450 (zone 80,450-82,059) and whose daily close is >= 80,450 | OURS (2 %) |
| 8 | Stop | 1 % below the lowest low of the retest touch streak | OURS |
| 9 | Leverage | 2x on testnet, operator may change | OURS |
| 10 | Exit | weekly close back below 80,450; the flag then re-arms and needs a new confirmation | OURS |

Caveats
- 80,450 and 75,000 are one analyst's lines from 11-05; they are context, not signals (cbp-is-the-context-source). If a later CBP row moves them, edit the constants and the quoted row together (test checks the quote parses to the constant).
- History check (not a backtest): replayed on btc_daily.csv the rule shows an entry 2026-10-09 at 82,636 and an exit 2026-10-25; the stop (80,787) would have been hit first. Record such cases; this is how the rule is judged (phase-first).
- Not modelled: stop fills, funding, fees. The testnet run supplies them.
- Today (2026-11-06 data): d397, -40.0 % from peak, price under the reclaim level: WAIT.

Wiring: `scripts/dev/market_guide.py` prints the one-line flag in the market guide. `MyTradingSys/tools/live_aid` shows the same line (cycle_flag.js, refreshed by build_artifact.py).
