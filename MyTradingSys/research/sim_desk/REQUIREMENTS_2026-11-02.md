# Simulator: operator requirements and fixes (demo 2026-11-02)

Context: the operator found the simulator "showed nothing useful" and asked for a guided demo (Eagle_Eyes relay, 2026-11-02). Two surfaces exist: the published results page (Artifact, read-only list of every test) and the local desk (`python MyTradingSys/research/sim_desk/desk.py`, settings + Run, DEV window only). One row per thing he asks for, his words verbatim.

Size: S = under an hour, M = a session, L = more than one session.

| # | His words (verbatim) | What it means | Size | Card id |
|---|---|---|---|---|
| 1 | "C30 - not present - why do not u demo by taking control now?" | (a) He searched C30 and got nothing: the search box rebuilt itself on every key and typed text came out backwards ("C30" became "03c"). Fixed on page v16, C30 now found 1 of 337. (b) Demos are driven by Claude in his Chrome (Claude in Chrome), not click instructions. | S | sim-search-caret (fixed, card raw) |
| 2 | "Focus on each time frame is this. That I am seeing here. Here it says how. Five-minute data built into 10-minute, 15-minute, 30-minute. So what it means really, and what is really playing, what is this dot that is moving? What I do not understand is that what is the trade here, like when you get into the trade and when you get out of the trade. When we get stopped out, I do not understand what really is being demoed here. Okay, this dot is moving. And what this dot means? And what are these lines that you have drawn?" | The replay shows only a running total, so he cannot see a trade. Wants, per trade: the candles of the signal chart (30m for H1), where it entered, where it exited, the stop if any, and the indicator readings (WaveTrend dot, RSI divergence) that fired it. Also: state the test's timeframe plainly and label the dot and lines on the chart. | M | sim-trade-candle-view |

## Found before the demo (Opus, not his words)
| # | Gap | Size | Card id |
|---|---|---|---|
| P1 | The results page only replays trades already exported; the C30 page had a table and no trades. Fixed for C30 today (35 VALIDATION trades replay, H2 22 trades as a table). Most result files still show "no example trades exported". | M | |
| P2 | The pre-US pullback base rate (8f8e92f10) had no page row; added as `eagle-preus-pullback`. Per-day rows were never saved, so no example days. | S | |
| P3 | No real candle chart on the published page (only percent ladders and running totals); real charts exist only in the local desk (`desk.py`), which he may never have started. | M | |
