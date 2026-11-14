# 24h Diff Review: Indicator Rule Books (`diffreview-indicator-rulebooks-gemini3-1114`)

**Verdict: 6 BUG, 5 RISK, 3 STYLE, 15 CLEAN across 29 commits (2026-11-13..2026-11-14).**

Reviewed all 29 commits returned by `git log --since='24 hours ago' --format='%h %s' origin/fast-track -- MyTradingSys/research/indicator_rulebooks` (also equal to full `git log` count = 29).

Full per-SHA table: `MyTradingSys/research/layer_lab/gemini_1114c/diffreview-indicator-rulebooks/REVIEW.md`.

## Key Findings (file:line)
- **BUG (`7b894a6a2`, `MyTradingSys/research/indicator_rulebooks/PITCHFORK.md:5`):** Result line still claims "only resting limit retests at the outer tine combined with volume profile confluence produce positive expectancy in backtests", contradicting `MyTradingSys/research/indicator_rulebooks/PITCHFORK.md:54-55` (4h PASS withdrawn, `EXACT -0.011%`).
- **BUG (`b3e800d32`, `MyTradingSys/research/indicator_rulebooks/MOVING_AVERAGES.md:5`):** Result line claims "(0 of 384 intraday MA rules profitable)", a misattributed number (from RSI's 384 cells in `MyTradingSys/research/indicator_rulebooks/RSI.md:5`) with no backing in Section 5 (`MyTradingSys/research/indicator_rulebooks/MOVING_AVERAGES.md:57-65`).
- **BUG (`758d81d0c`, `MyTradingSys/research/indicator_rulebooks/HILEGA_MILEGA.md:5,57` & `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:11`):** Claims "Our backtests find raw crosses bleed fees on every timeframe" for Hilega Milega even though Section 5 (`MyTradingSys/research/indicator_rulebooks/HILEGA_MILEGA.md:43,46`) marks Hilega flips `NOT_MEASURED`; `FUNDING_LS.md` line 11 cites nonexistent `research/fast_track_2026-09-27/run_t055.py` (actual path `MyTradingSys/backtest/layers/run_t055.py`).
- **BUG (`307a39949`, `ac94e4057`, `5fec8d062`, `MyTradingSys/research/indicator_rulebooks/INDEX.md:14,16,18,20,23,26,44-54`):** Parallel merges/edits reverted `DONE` statuses for Moving averages, CVD, Funding/LS, Hilega Milega, and Trend lines back to `PARTIAL`, left `Stochastic RSI` as `MISSING`, and stacked 11 `Status counts` lines at lines 44-54.
- **RISK (`02d144104`, `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:5`):** Overstates an `n=22` `UNDERPOWERED` gross count (`MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:51`) as "persistent drain doubles the likelihood of outsized volatility".
- **RISK (`19881058d`, `MyTradingSys/research/indicator_rulebooks/VWAP_VALUE_AREA.md:45-51`):** `MyTradingSys/research/indicator_rulebooks/INDEX.md:17` marks `VWAP and value area` `DONE`, while Section 5 contains only folder pointers without the required `n | fee-net result | verdict` table.
