# Task Report: gemini-yt-rumers-direct-view-1101

- **Task ID:** `gemini-yt-rumers-direct-view-1101` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-1101.json:15`]
- **Lane / Weight:** CODEX / ROUTINE [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-1101.json:17,56`]
- **Date (UTC):** 2026-11-01
- **Worker / Model:** Gemini 3.8 Flash (Medium)
- **Registry / Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-1101.json:36`]

## 1. Scope & Objective

Execute direct view analysis of the 10 operator-picked videos from YouTube channel `@the.rumers` (Doug & Silvia) without running caption fetchers or `yt-dlp` (avoiding HTTP 429 rate limit). Record all trading rules as `UNVERIFIED-PARAPHRASE` with approximate minute markers, strictly avoid quotation marks around spoken words, and establish a ranked candidate list of complete entry/exit setups for downstream caption checking and DEV backtesting.

Target videos [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:15`, `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:15`]:
1. `6WfTIyJ-YzQ` - If I Could Only Trade ONE Strategy... This Would Be It
2. `EoQDQVblmMY` - The One Box Theory Strategy That Works Everyday
3. `N6zlfBJsoRc` - I Always Wait For THIS Before Entering Trades - Unsharp Candles
4. `kozesVBKkg4` - 2 Stupid Simple VWAP Trading Strategies
5. `aTMFouI9mF4` - The ONE CANDLE Scalping Strategy I Will Use For Life
6. `T0H_jpQXdVI` - This 15-Minute Scalping Strategy Shouldn't Work... But It Makes Me $2,392/Day
7. `pcYO-yzAtrQ` - If I Had to Make $500 by Tomorrow, I'd Use This Trading Strategy
8. `hMURCHLnZVE` - The ONLY INDICATOR That Predicts Every Mega Move - Most Traders Use It Wrong
9. `xtN0U-j_4Jc` - The One Line Indicator That Flat Out Delivers
10. `l0j1irTKIUw` - The ONLY INDICATOR That Predicts Monster Moves - Most Traders Use It Wrong

## 2. Deliverables & Verification

1. **Direct View Extraction File:** `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md`
   - Total videos covered: `10` [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md:16-27`]
   - Total rules extracted: `35` rows [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md:37-71`]
   - All rows tagged: `UNVERIFIED-PARAPHRASE` with approximate minute marker [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_direct_view.py`]
   - Quotation marks check: `0` quotation marks around spoken words [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_direct_view.py`]
   - Complete entry/exit setups identified: `7` ranked candidate setups [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW.md:77-123`]

2. **Verification Suite:** `MyTradingSys/research/rumers_2026-11-01/verify_direct_view.py`
   - Tested on pre-change code: exit code 1 (`FAIL: MyTradingSys\research\rumers_2026-11-01\RUMERS_DIRECT_VIEW.md does not exist`)
   - Tested on post-change code: exit code 0 (`PASS: MyTradingSys\research\rumers_2026-11-01\RUMERS_DIRECT_VIEW.md verified successfully (35 rules across 10 videos, all UNVERIFIED-PARAPHRASE, no quotes, ranked list present).`)

## 3. Ranked Candidate Rules for DEV Backtest

| Rank [OURS] | Setup Identifier [OURS] | Source Video(s) | Key Setup Concept | Timeframe | Complete Entry & Exit |
|---|---|---|---|---|---|
| 1 | `RUMERS-ORB-MANIP-REVERSAL` | `6WfTIyJ-YzQ`, `T0H_jpQXdVI`, `aTMFouI9mF4` | 15m opening range manipulation (>= 20% Daily ATR), 5m reversal hammer/engulfing, stop beyond day extreme, target 50% midpoint | 15m / 5m | YES |
| 2 | `RUMERS-BOX-PDH-PDL-FADE` | `EoQDQVblmMY`, `pcYO-yzAtrQ` | Sweep of Previous Day High/Low, 5m close back inside box, stop beyond sweep wick, target 50% midpoint | 1D / 5m | YES |
| 3 | `RUMERS-EMA9-PULLBACK-TREND` | `xtN0U-j_4Jc`, `l0j1irTKIUw` | 5m 9 EMA trend filter, pullback touch rejection, stop below pullback low, target 1:2 R or 9 EMA trail | 5m | YES |
| 4 | `RUMERS-VWAP-BOUNCE` | `kozesVBKkg4` | Intraday VWAP trend filter, pullback touch rejection, stop below swing low, target session high or 1:2 R | 5m | YES |
| 5 | `RUMERS-EMA9-SEPARATOR-RETEST` | `l0j1irTKIUw` | Separator distance surge (>= 2 ATR), retest of 9 EMA holding, stop below retest low, target 1:2 R | 5m | YES |
| 6 | `RUMERS-RSI-STRUCTURAL-DIVERGENCE` | `hMURCHLnZVE` | Key structural level touch + RSI divergence / hook from extreme (<30 / >70), 5m reversal candle, stop beyond pivot | 15m / 5m | YES |
| 7 | `RUMERS-UNSHARP-3CANDLE-EXEC` | `N6zlfBJsoRc` | 3-candle execution sequence (Lead, Confirmation, Execution) at structural level, stop beyond Confirmation extreme, target 1:2 R | 5m | YES |

## 4. Downstream Recommendations

1. **Pre-Registration:** Formally register `RUMERS-ORB-MANIP-REVERSAL` and `RUMERS-BOX-PDH-PDL-FADE` into `TRIAL_REGISTRY_rumers.csv` under the rules defined in `MyTradingSys/research/rumers_2026-11-01/HARNESS.md`.
2. **Session Anchor Definition:** When testing 24/7 crypto (BTCUSDT), explicit session open anchors (e.g., 00:00 UTC or 13:30 UTC NY open) must be frozen as `OURS` in `PRE_REG` before execution.

Noticed: The operator-picked videos from `@the.rumers` fall into two clear mechanical clusters: Opening Range / Previous Day boundary fades (`6WfTIyJ-YzQ`, `EoQDQVblmMY`, `aTMFouI9mF4`, `T0H_jpQXdVI`, `pcYO-yzAtrQ`) and single-indicator trend pullbacks (`kozesVBKkg4`, `xtN0U-j_4Jc`, `l0j1irTKIUw`), both of which map directly into existing MTS layer primitives (`layers/levels` and `layers/momentum`).
