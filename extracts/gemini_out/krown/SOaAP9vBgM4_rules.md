# Krown Video Rules Extract - SOaAP9vBgM4

- URL: https://www.youtube.com/watch?v=SOaAP9vBgM4
- Title: How Bitcoin Data Fools You: +60% Becomes +7%
- Upload Date: 2026-10-07

## Trading Rules Stated (SOURCED)

### Mechanical Rules Status
- NO RULES STATED.
- No direct trade execution setup, entry trigger, stop loss order, or position sizing formula is stated in this 54-second educational Short.

### Quantitative Data & Methodology Rules (Filter / Data Protocol)
1. **Sample Partitioning / Pre-2018 Distortion Filter (Backtest Protocol / Filter)**
   - SOURCED: "If we only include results from 2018 and onwards, those results go down significantly in fact. In fact, to the point where they're actually not that interesting. So, I do want to be super honest about this because I just want to show you how people can kind of fool you with data. And this is very common. This is why a lot of people who I think are including like super early results for Bitcoin..." (URL: https://www.youtube.com/watch?v=SOaAP9vBgM4 at 00:00 - 00:19)
   - SOURCED: "since 2018, those results would be eight, you know, plus 8% plus 7% plus 8 and 1/2%. I would prefer the previous ones personally, but hey, still positive results overall. Um, and I would say that this is maybe a little bit more of a a down-to-earth one. Still very high highly probable to be green during that time, but those returns get, you know, sliced and diced. So, let's just say, you know, maybe close to like 8% for all these, you know, across the board. Where does that put Bitcoin? Basically, 90,000 bucks." (URL: https://www.youtube.com/watch?v=SOaAP9vBgM4 at 00:23 - 00:52)
   - Comparison with `krown_params.json`: MATCH. `zone_lookback`: 250 in `krown_params.json` bounds structural memory. In MTS research methodology, early pre-2018 Bitcoin data is segregated from modern regimes because unpartitioned all-history medians massively overstate expected returns (e.g. +60% historical median drops to ~7-8% post-2018).

2. **Specific Trading Parameters (Setup / Entry / Stop / Target / Sizing)**
   - Setup: NO SETUP RULE STATED.
   - Entry: NO ENTRY RULE STATED.
   - Stop: NO STOP RULE STATED.
   - Target: Projecting post-2018 median returns (~8%) from current price puts Bitcoin at ~$90,000.
   - Sizing: NO SIZING RULE STATED.

## Notes (OURS)

- Short 54-second clip illustrating the danger of unadjusted historical backtests on Bitcoin.
- Including pre-2018 exponential market data distorts expected returns and inflates hit-rate profitability estimates.
- Modern Bitcoin event-study setups (post-2018) exhibit much tighter median returns (~7% to 8.5%) than the ~60% figures cited by commentators using full history.
- Reinforces the MTS mandate to test and report pre-2018 and post-2018 performance separately across all quantitative layers.
