# Report: gemini-rulebook-vfi-1113 (Volume Flow Indicator Rule Book)

- **Date:** 2026-11-13 (UTC)
- **Task ID:** gemini-rulebook-vfi-1113
- **Worker:** Gemini (gemini-3.8-flash-low)
- **Role:** Builder (Rule book authoring)

## Findings & Citations

1. **Rule book authoring (`MyTradingSys/research/indicator_rulebooks/VFI.md`):**
   - Implemented sections 1 through 8 according to `research/indicator_rulebooks/TEMPLATE.md`.
   - **Section 1 (What it measures):** Details Katsanos' noise-filtered, volatility-threshold, volume-capped rolling volume flow formulation. Cites `backtest/layers/FORMULAS.md`:700-717 (s32) and code `backtest/layers/vfi/vfi.py`. Parity `VERIFIED-TV 2026-11-07` on 4/4 daily bars on BYBIT:BTCUSDT.P (`FORMULAS.md`:716).
   - **Section 2 (Developer's own rules):** Sourced from Markos Katsanos (June 2004 *Technical Analysis of STOCKS & COMMODITIES*, "Using Money Flow to Stay with the Trend", mkatsanos.com; cited in `research/tv_favorites_2026-11/USAGE_vfi.md`:7-15) and LazyBear TradingView Pine script `VFI_LB` (`tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/`). Parameters: Length 130, coef 0.2 (0.1 intraday), vcoef 2.5, stdev length 30, smoothing length 3, signal length 5 EMA (`USAGE_vfi.md`:58-64).
   - **Section 3 (What the internet and crypto traders say):** Sourced claims from QuantifiedStrategies (long-term trend filter, centerline crossover system backtests) and MTS crypto usage notes (`USAGE_vfi.md`:33-55) noting 24/7 calendar distortion and volume sweep divergence.
   - **Section 4 (What our analysts say):** Grepped extract catalogs (`research/**/extract_*.md`, `research/krown_ta101_2026-10-13/*.md`, `research/nk_stocktalk_1113/*.md`, `research/yt_feed_2026-10-31/*.md`); none of our tracked analysts (Krown, Tom, Fabio, Malkan, NK, CCU, Habib/CBP, CryptoCred) mention VFI.
   - **Section 5 (OUR measurements):** Pointers to `research/tv_favorites_2026-11/VFI_STATE.md`, `research/tv_favorites_2026-11/USAGE_vfi.md`, and `backtest/layers/FORMULAS.md` s32; no fee-net outcome backtest has been executed in the repo (UNTESTED).
   - **Section 6 (Live Aid reading):** Verified Live Aid integration in `tools/live_aid/indread.js`:13, 79-80, 100-107 (`ROWS` table, cell calculation requiring 263 bars) and `tools/live_aid/home.js`:113-121, 282-297 (Volume card money flow badge chips, Who is winning card 6-reading vote).
   - **Section 7 (Confluence role):** FLOW (context column / volume agreement filter, not an entry signal).
   - **Section 8 (Open tests):** 4 prospective test studies listed.

2. **Index update (`MyTradingSys/research/indicator_rulebooks/INDEX.md`):**
   - Updated VFI row from `PARTIAL` to `DONE`, updating Live Aid column and pointer.
   - Verified with `python scripts/dev/rulebook_check.py` (exited 0, all 22 layer folders accounted for).

3. **Verification checks:**
   - Ran `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/indicator_rulebooks/VFI.md` -> PASS (0 problems).
   - Ran `python scripts/dev/rulebook_check.py` -> PASS.
