# Findings Report: Pitchfork Indicator Rule Book (`gemini-rulebook-pitchfork-1113`)

- Card ID: `gemini-rulebook-pitchfork-1113`
- Host / Worktree: JIS-NUC / `gemini-rulebook-pitchfork-1113`
- Date: 2026-11-13 UTC
- Target Document: `MyTradingSys/research/indicator_rulebooks/PITCHFORK.md`
- Index Registry: `MyTradingSys/research/indicator_rulebooks/INDEX.md:24`

## Findings and Sources
1. **Developer's Origin & Original Rules (SOURCED):**
   - Inventor: Dr. Alan H. Andrews (1900–1985), MIT engineer/mathematician, developing the *Babson Action-Reaction Course* (1960–1975) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`].
   - 80% Rule (Median Line Magnet): Prices reach the Median Line approximately 80% of the time following Pivot 2 completion [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:83`, citing Alan H. Andrews via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:34`].
   - Hagopian Rule: Price failing to reach the Median Line signals acute order flow imbalance and violent reversal breaking out through the opposite tine [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:97`, citing Alan H. Andrews via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:39`].
   - Schiff Pitchfork: Jerome Schiff modification shifting anchor P0 halfway in time and price toward P1 [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`].
   - Modified Schiff Pitchfork: Preserves origin time coordinate $t_0$, shifts price to the midpoint between P0 and P1 [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:131-134`].
2. **Independent Web Sources:**
   - Investopedia (`https://www.investopedia.com/terms/a/andrewspitchfork.asp`): General overview of Andrews' Pitchfork, 3-point construction, median line 80% magnet concept, dynamic support/resistance tines (Grade: anecdote) [SOURCED].
   - TradingView Help (`https://www.tradingview.com/support/solutions/43000518204-modified-schiff-pitchfork/`): Drawing tool specification and slope adjustment for shallower trends (Grade: anecdote) [SOURCED].
   - Optuma (`https://www.optuma.com`): Market geometry, Hagopian rule and failure trendline breakouts (Grade: anecdote) [SOURCED].
3. **Analyst Extracts:**
   - Rumers (Doug & Sylvia): 15m/1h Pitchfork Three-Part Reversal Candlestick Entry Trigger at support/resistance boundary [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_3.md:22,36-37,43`].
   - Operator: Weekly spot BTC stacked Schiff pitchforks [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:3-6,21-25`].
   - Krown, Tom, Fabio, Malkan, NK, CCU, Habib/CBP: Grepped with zero pitchfork rules found (`none found`).
4. **Repository Studies (Pointers Only in Section 5):**
   - `MyTradingSys/research/pitchfork_2026-10-19/` (Phase 1 1D event study and Phase 2 4H POC study).
   - `MyTradingSys/research/mts_audit_2026-11-03/` (Causal audit recheck of 4H Modified Schiff resting tine limit retests).
   - `MyTradingSys/research/rumers_2026-11-01/` (Systematic backtest of Rumers Setup R5).
   - `MyTradingSys/research/sim_desk/` (Synthetic pitchfork test harness).
5. **Quality and Rulebook Checks:**
   - `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/indicator_rulebooks/PITCHFORK.md`: PASS (0 problems).
   - `python scripts/dev/rulebook_check.py`: OK (22 layer folders, all in INDEX).
