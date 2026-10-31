# Task Report: gemini-yt-krown-latest-trades-extract

- **Task ID:** `gemini-yt-krown-latest-trades-extract`
- **Lane / Weight:** CODEX / ROUTINE
- **Date:** 2026-10-31 UTC
- **Worker / Model:** JIS-NUC / Gemini Flash
- **Registry:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`

## 1. Scope & Objective

Ingest the latest 10 videos from Eric Krown (@ECKrown) on YouTube, capture timed captions, and extract his latest stated trade setups on Bitcoin (BTC) and altcoins (entry, stop, target, invalidation levels, lines in the sand) with timed quotes.

## 2. Ingestion & Captions Summary

Executed timed caption download:
```powershell
python scripts/dev/fetch_captions_timed.py --analyst Krown --channel "@ECKrown" --latest 10 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_krown-latest-trades
```
All 10 latest videos were read and captioned (with fallback to canonical transcript storage in `raw_transcripts_canonical/` where HTTP 429 rate limit errors occurred):
1. `dLq5Jyir3Iw` ("Is Bitcoin Putting In Its Next Major Low? Here's My Signal") - 2026-10-27 - 4731 words - Captioned
2. `zay_owGmjo0` ("Bitcoin: A Viewer Sent Me a Cross That Hasn't Failed Since 2022") - 2026-10-27 - 5146 words - Captioned
3. `M_p2k4uvRKc` ("Order Flow Trading Explained: How to Read the Tape (From a Former NYSE ARCA Market Maker)") - 2026-10-25 - 5685 words - Captioned
4. `OR3Q2Vf1lrM` ("I Built a Free AI Trading Bot With Claude in 20 Minutes. No Code. Every Step.") - 2026-10-24 - 3288 words - Captioned
5. `YAF6fCuVWaI` ("The 3 Buttons That Decide What Every Trade Costs You (Order Types Explained)") - 2026-10-24 - 7015 words - Captioned
6. `8cC9Jpc8D5c` ("Is Bitcoin Faking Us Out? Not Until This Line Breaks") - 2026-10-22 - 4262 words - Captioned
7. `LMRNBdMiQ2g` ("Bitcoin Is Setting Up Another Higher Low. Here's My Line in the Sand") - 2026-10-22 - 3513 words - Captioned
8. `bXug2l6qICc` ("Why Bitcoin Is Still Bullish (The $79,700 Warning)") - 2026-10-20 - 3899 words - Captioned
9. `ro6tMlqbbBI` ("Bitcoin: 83% Chance of Upside (Here Is Why)") - 2026-10-20 - 4454 words - Captioned
10. `P3rDSh187TE` ("Why Crypto Drops 10% in Minutes: Liquidation Cascades Explained (Former NYSE ARCA Market Maker)") - 2026-10-18 - 7302 words - Captioned

Total videos read: 10. Captioned: 10. UNVERIFIED: 0.

## 3. Extracted Deliverable & Key Findings

Deliverable file created:
- [`KROWN_LATEST_TRADES_2026-10-31.md`](file:///F:/MTS/gq/gemini-yt-krown-latest-trades-extract/MyTradingSys/research/yt_feed_2026-10-31/KROWN_LATEST_TRADES_2026-10-31.md)

### Key Setups, Levels, & Quotes Sourced:
1. **Primary BTC Line in the Sand / Bullish Invalidation ($79,700):**
   - Krown identifies last week's low ($79,700) as the critical inflection point / line in the sand separating bullish continuation from a corrective drop across multiple videos:
     - `dLq5Jyir3Iw` at `[00:12:10]`: *"Bitcoin's closed above there, which is 79,700 on a daily timeframe, I can't even be looking for that short-term corrective move to happen somewhere between like 77 5 to to 78 5, let's say"*
     - `LMRNBdMiQ2g` at `[00:07:18]`: *"treating last week's low as a major inflection point now meaning that as long as Bitcoin is above last week's low 79,700, I am bullish. I have no reason to be bearish but that is my line in the sand now."*
     - `bXug2l6qICc` at `[00:08:22]`: *"And And of course, there is, as always, a nice invalidation point for this. So to be super fucking clear, if this is going to play out in the short term, then absolutely we we do expect Bitcoin has found its low for this current consolidation at last week's low, low, which is 79,700."*
2. **BTC Downside Targets ($77,350 / CME Gap $76,000 - $77,000):**
   - If Bitcoin loses $81,000 on a 2-day close, the 2-day 55 EMA corrective setup fires targeting ~$77,350 (`dLq5Jyir3Iw` at `[00:11:04]`, `zay_owGmjo0` at `[00:04:37]`).
   - If $79,700 breaks down, the next target is filling the CME gap at $76,000 - $77,000 (`bXug2l6qICc` at `[00:09:08]`).
3. **BTC Macro Invalidation / Bull Trap Stop ($75,000):**
   - Daily close below $75,000 invalidates the entire higher-timeframe bullish structure (`dLq5Jyir3Iw` at `[00:12:30]`: *"devastating for the bullish case for the long-term is if Bitcoin actually were to come back down and trade and close more specifically below 75,000 bucks"*).
4. **BTC Upside Breakout Triggers & Targets ($83,900 -> $87,000; $84,280 Breakout; $90,000 - $95,000 Month-End Target):**
   - CME close above $83,900 targets $87,000 (`LMRNBdMiQ2g` at `[00:09:24]`).
   - Daily close above $84,280 confirms technical breakout (`8cC9Jpc8D5c` at `[00:00:48]`).
   - Higher-probability upside target model projected $90,000 - $95,000 (`ro6tMlqbbBI` at `[00:07:24]`).
5. **Altcoin Setup (Ethereum $2,330 Line in the Sand):**
   - Ethereum 2-day close below $2,330 confirms structural breakdown towards $2,000 (`ro6tMlqbbBI` at `[00:11:43]`: *"about 2330 is where I'd be looking at similar things what we did uh did say before. This would be pertaining to a 2-day time frame closure if Bitcoin no, if Ethereum closed below there, I would call it a breakdown."*).
6. **Educational & Bot Videos (NOT_IN_DATA):**
   - 4 videos (`M_p2k4uvRKc`, `OR3Q2Vf1lrM`, `YAF6fCuVWaI`, `P3rDSh187TE`) focus on order book mechanics, Claude AI bot scripting, stop-loss order mechanics, and liquidation cascade theory, containing no active live market trade setups (categorized as `NOT_IN_DATA`).

## 4. Verification Gate

Ran verification command:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/KROWN_LATEST_TRADES_2026-10-31.md
```
Result: `PASS: 0 problem(s)` (Exit code 0).
Every verbatim quote matches canonical transcript text and exact positional thirds (`BEGIN`, `MIDDLE`, `END`).
