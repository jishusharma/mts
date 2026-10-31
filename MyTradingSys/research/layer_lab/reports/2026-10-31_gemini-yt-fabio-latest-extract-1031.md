# Task Report: gemini-yt-fabio-latest-extract-1031

- **Task ID:** `gemini-yt-fabio-latest-extract-1031`
- **Lane / Weight:** CODEX / ROUTINE
- **Date:** 2026-10-31 UTC
- **Worker / Model:** JIS-NUC / Gemini Flash
- **Registry:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`

## 1. Scope & Objective

From the latest 8 videos of Fabio's channel (`@fabervaaleEng`): extract his session timing, CVD and order-flow entry rules, and stated levels as a structured table with video ID, timestamp, and verbatim caption quotes (or `NOT_IN_DATA`). No verdict.

## 2. Ingestion & Captions Summary

Executed timed caption download command:
```powershell
python scripts/dev/fetch_captions_timed.py --analyst Fabio --channel "@fabervaaleEng" --latest 8 --out MyTradingSys/research/gemini_burn_2026-10-31/transcripts_fabio-latest
```
All 8 latest videos from channel `@fabervaaleEng` were fetched and captioned:
1. `StaphlRH8NQ` ("5 Edges that refuse to die.") - 2026-06-16 - 2,417 words - Captioned (auto, en)
2. `LQvv5xgy_ik` ("Exposing my Risk Management Protocol") - 2026-05-13 - 5,972 words - Captioned (auto, en)
3. `FawPrRUGNpk` ("The Only Liquidity Guide You'll Ever Need") - 2026-05-07 - 8,485 words - Captioned (auto, en)
4. `Khgj5q1-ln8` ("My Signature Orderflow Model") - 2026-02-21 - 1,947 words - Captioned (manual, en)
5. `cUTsoU-15Tc` ("The Simplest Orderflow Trading Model") - 2026-02-17 - 4,377 words - Captioned (auto, en)
6. `Pz8f0wWW12M` ("The Only Orderflow Guide You'll Ever Need") - 2026-02-11 - 6,606 words - Captioned (auto, en)
7. `8CWKfoSJu3c` ("How I did 20R in one NQ Session") - 2026-01-19 - 1,598 words - Captioned (auto, en)
8. `06R-ebyOhDI` ("How To Find The BEST Entry Zones") - 2025-11-19 - 1,132 words - Captioned (auto, en)

Total videos read: [OURS] 8. Captioned: [OURS] 8. UNVERIFIED: [OURS] 0.

## 3. Extracted Deliverables & Findings

Deliverable file created:
- [`FABIO_LATEST_RULES.md`](file:///F:/MTS/gq/gemini-yt-fabio-latest-extract-1031/MyTradingSys/research/gemini_burn_2026-10-31/FABIO_LATEST_RULES.md)

### Key Rules & Levels Extracted (29 Verbatim Quoted GPS Blocks across 37 Summary Rows):

1. **Session Timing Rules:**
   - **Initial Balance & Cash Session Definition:** Regular cash session opening range is defined as the first 30 minutes (`StaphlRH8NQ` at `[00:08:13]` [SOURCED], `cUTsoU-15Tc` at `[00:11:45]` [SOURCED]). First 15 minutes defines opening range breakout baseline (`cUTsoU-15Tc` at `[00:00:06]` [SOURCED]).
   - **Session Volume Dominance:** New York session holds the maximum volume for US indices / NQ (`cUTsoU-15Tc` at `[00:01:30]` [SOURCED], `Pz8f0wWW12M` at `[00:29:02]` [SOURCED]). London session provides interaction context (`Pz8f0wWW12M` at `[00:09:20]` [SOURCED], `06R-ebyOhDI` at `[00:00:38]` [SOURCED]), but Fabio explicitly uses exclusively cash session profiles for US index profiling (`Pz8f0wWW12M` at `[00:29:18]` [SOURCED]).
   - **Session Extreme Behavior:** Book sweeping occurs close to New York session high or range extremes (`FawPrRUGNpk` at `[00:10:47]` [SOURCED]).

2. **CVD Dynamics & Order-Flow Rules:**
   - **CVD Directional Warning:** When CVD is flipping lower during a bullish day, aggressive downside sellers dominate; no reversal longs are permitted while sellers control the auction (`FawPrRUGNpk` at `[00:39:08]` [SOURCED], `[00:39:17]` [SOURCED]).
   - **Imbalance / Aggression Triggers:** Best entries are triggered by order flow imbalances or aggression at qualified levels (`cUTsoU-15Tc` at `[00:01:00]` [SOURCED]).
   - **Confluence Zones:** Best entry zones combine Value Area High (VAH), big trades, and delta footprint levels (`06R-ebyOhDI` at `[00:02:26]` [SOURCED]).
   - **Risk Management & Stop Placement:** Breakout beyond protection level warrants moving stop loss to break-even (`Pz8f0wWW12M` at `[00:40:00]` [SOURCED]); re-entry is protected behind delta seller clusters (`06R-ebyOhDI` at `[00:03:42]` [SOURCED]).

3. **Stated Price Levels:**
   - **NASDAQ / NQ Levels (`8CWKfoSJu3c`):**
     - Clean resistance: `25,650` (`[00:02:38]` [SOURCED])
     - Overhead cluster: `25,7630` (`[00:02:48]` [SOURCED])
     - Intermediate target: `25,630` (`[00:04:04]` [SOURCED])
     - Breakdown / reload level: `25,584.3` (`[00:05:52]` [SOURCED])
     - Psychological support & absorption level: `25,550` (`[00:07:25]` [SOURCED])
     - Terminal cluster / target: `2534` (`[00:08:12]` [SOURCED])
   - **NASDAQ / NQ Psychological Level (`Pz8f0wWW12M`):** `25,500` (`[00:32:19]` [SOURCED])
   - **NASDAQ / NQ Liquidity Heatmap Level (`FawPrRUGNpk`):** `27,925` (`[00:32:16]` [SOURCED])
   - **Videos without Stated Price Levels:** `StaphlRH8NQ`, `LQvv5xgy_ik`, `Khgj5q1-ln8`, `cUTsoU-15Tc`, and `06R-ebyOhDI` focus on conceptual models and record `NOT_IN_DATA` for stated price levels.

## 4. Verification Gate Results

Ran verification script:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/gemini_burn_2026-10-31/FABIO_LATEST_RULES.md
```
Result:
```
PASS: 0 problem(s) (29 of 29 quote blocks verified verbatim against canonical raw transcripts with matching thirds position tags)
```
Exit code: [OURS] 0.
