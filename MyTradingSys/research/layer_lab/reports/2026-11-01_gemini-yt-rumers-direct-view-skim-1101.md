# Task Report: gemini-yt-rumers-direct-view-skim-1101

- **Task ID:** `gemini-yt-rumers-direct-view-skim-1101` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-skim-1101.json:15`]
- **Lane / Weight:** CODEX / ROUTINE [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-skim-1101.json:17,45`]
- **Date (UTC):** 2026-11-01
- **Worker / Model:** Gemini 3.8 Flash (Medium)
- **Registry / Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-skim-1101.json:27`]

## 1. Scope & Objective

Execute direct view analysis on the newest 20 videos from YouTube channel `@the.rumers` (Doug & Silvia) without running caption fetchers or `yt-dlp` (avoiding HTTP 429 rate limit). List title and the trading idea each teaches, skipping the 10 videos already analyzed in `RUMERS_DIRECT_VIEW.md`. Record all trading ideas as `UNVERIFIED-PARAPHRASE` with approximate minute markers, strictly avoid quotation marks around spoken words, and flag each video with `MECHANICAL YES/NO` indicating whether complete entry, stop loss, and target parameters were stated.

Scope [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-skim-1101.json:30,33`]:
- In: `MyTradingSys/research/rumers_2026-11-01/` (new files only)
- Out: live tree; engine and layer code; any backtest; `.secrets` and `.env`

Target videos reviewed [OURS: 20 videos total, 0 overlap with the 10 videos in `RUMERS_DIRECT_VIEW.md`]:
1. `zspMXJVbfAY` - How Trading Like an Idiot Makes Me $10,000/Month (15 Minutes a Day)
2. `OYLv6Ev-kVE` - If You Only Have $50, Do This Every Morning (The 3R Rule)
3. `T3eQDnYHOw4` - I Traded Markets for 26 Years: Here's What They Don't Tell You
4. `8vufTzGZqiI` - The One Day Trading Strategy I Make A Living From (20 Years Backtested)
5. `9ba0p8ZPL4c` - This SIMPLE SUNDAY SETUP Makes Me $9K a Week (Live Trading)
6. `LuCo80sOn3k` - 90% of Traders Lose Money at the Market Open. I Make It There.
7. `UEUeSC-7tuA` - 7 Painful Lessons I Learned From Blowing Up 7 Trading Accounts
8. `bojw33VZYHk` - The One Trading Indicator I Will Use For Life
9. `lUr32iqWHz8` - This Simple PART TIME Swing Trading Strategy Has 90% Win Rate
10. `Gd5AiA3fVxY` - Why Price Action Is The Language Of The Market
11. `lANSXWlbINE` - The Day Trading Strategy I Use for SNIPER ENTRIES
12. `y4ca1B9RKVY` - I Wasted 3+ Years Trading the Wrong Time Frame (You're Probably Doing It Too)
13. `R7XkHW9i65g` - I Use This One Trading Strategy Every Day (And It's Stupid Simple)
14. `VjXeD-Ez7VM` - The Only Day Trading Strategy That Actually Works (Powerful And Proven)
15. `4zazKDSXlh8` - How I 10X My Gains With This Day Trading Strategy (Backtested Results)
16. `NMUd0oX_7Pg` - The 15-Minute Candle Strategy I Will Use For Life
17. `I3V94DfU4CY` - What You Never Learn About Candlesticks Until It's Too Late
18. `1oEk7QfJOhk` - How To Grow A Small Trading Account (The Right Way)
19. `3fMOGRdBT_c` - How I Beat the Market for 22 Years Straight
20. `dP7GXUNcF8g` - Using the Box Theory for Power Scalping (Live Trades)

## 2. Deliverables & Verification

1. **Direct View Skim File:** `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md` [OURS]
   - Total videos covered: `20` rows [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:20-39`]
   - Overlap with `RUMERS_DIRECT_VIEW.md`: `0` videos [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py`]
   - All rows tagged: `UNVERIFIED-PARAPHRASE` with approximate minute marker [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py`]
   - Quotation marks check: `0` quotation marks around spoken words [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py`]
   - Mechanical count: `11` flagged `MECHANICAL YES`, `9` flagged `MECHANICAL NO` [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:43-47`]

2. **Verification Suite:** `MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py` [OURS]
   - Tested on pre-change code: exit code 1 (`FAIL: MyTradingSys\research\rumers_2026-11-01\RUMERS_SKIM_DIRECT.md does not exist`) [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py`]
   - Tested on post-change code: exit code 0 (`PASS: MyTradingSys\research\rumers_2026-11-01\RUMERS_SKIM_DIRECT.md verified successfully (20 unique rows, all UNVERIFIED-PARAPHRASE, no quotes, all required fields valid).`) [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_skim_direct.py`]

## 3. Findings & Mechanical Candidate Setups

Across the 20 skimmed videos, 11 contain complete entry and exit criteria. Top mechanical setups suitable for subsequent DEV backtesting:
1. `RUMERS-SKIM-15M-ORB-EXPANSION` (`NMUd0oX_7Pg` / S16): Stop orders 1 tick outside opening 15m candle, 50% midpoint stop loss, 100% projection target [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:35`].
2. `RUMERS-SKIM-BOX-BOUNDARY-FADE` (`zspMXJVbfAY` / S01 & `dP7GXUNcF8g` / S20): 5m rejection close back inside previous day box, stop beyond sweep wick, target 50% equilibrium midpoint [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:20,39`].
3. `RUMERS-SKIM-OPEN-TRAP-FADE` (`LuCo80sOn3k` / S06 & `lANSXWlbINE` / S11): 15m opening manipulation candle with >50% wick, 5m counter-trend break trigger, stop beyond trap extreme, target at midpoint / prior demand [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:25,30`].
4. `RUMERS-SKIM-20EMA-TREND-PULLBACK` (`8vufTzGZqiI` / S04): Daily higher high / higher low trend alignment with 5m 20 EMA touch rejection close, stop below swing, fixed 1:2 RR [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:23`].
5. `RUMERS-SKIM-SUNDAY-GAP-FADE` (`9ba0p8ZPL4c` / S05): Weekend gap >0.5% on Sunday open, 5m rejection bar fade toward Friday settlement price, stop 5 ticks beyond Sunday wick [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_SKIM_DIRECT.md:24`].

Noticed: Across both the initial 10-video extract set (`RUMERS_DIRECT_VIEW.md`) and this 20-video skim set (`RUMERS_SKIM_DIRECT.md`), Doug Rumer's actionable mechanical setups consistently rely on two core principles: fading failed breakout sweeps of reference boundaries (Opening Range or Previous Day High/Low) back toward the 50% equilibrium midpoint, and trend continuation pullbacks to short EMAs (9 or 20 EMA) on the 5-minute timeframe.
