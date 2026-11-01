# Task Report: gemini-yt-rumers-direct-view-deep-1101

- **Task ID:** `gemini-yt-rumers-direct-view-deep-1101` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-deep-1101.json:15`]
- **Lane / Weight:** CODEX / ROUTINE [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-deep-1101.json:17,45`]
- **Date (UTC):** 2026-11-01
- **Worker / Model:** Gemini 3.8 Flash (Medium)
- **Registry / Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-deep-1101.json:27`]

## 1. Scope & Objective

Execute a second direct-view pass on the 5 top-ranked candidate videos from `RUMERS_DIRECT_VIEW.md` without automated caption fetching or `yt-dlp`. For every rule, pin down exact entry trigger, stop loss placement, profit target / exit, timeframe, and indicator settings as stated. Mark every rule as `UNVERIFIED-PARAPHRASE` with an approximate minute marker, with strictly no quotation marks around spoken words. Mark every number as `SOURCED` (stated in video) or `NOT_STATED`, never filling a gap.

Target videos analyzed [OURS: 5 videos total; `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md:14-19`]:
1. `6WfTIyJ-YzQ` - If I Could Only Trade ONE Strategy... This Would Be It (Rank 1 candidate primary)
2. `EoQDQVblmMY` - The One Box Theory Strategy That Works Everyday (Rank 2 candidate primary)
3. `xtN0U-j_4Jc` - The One Line Indicator That Flat Out Delivers (Rank 3 candidate primary)
4. `kozesVBKkg4` - 2 Stupid Simple VWAP Trading Strategies (Rank 4 candidate primary)
5. `l0j1irTKIUw` - The ONLY INDICATOR That Predicts Monster Moves - Most Traders Use It Wrong (Rank 5 candidate primary)

## 2. Deliverables & Verification

1. **Deep Direct-View Extraction:** `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md`
   - Total videos covered: `5` [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md:14-19`]
   - Total rules cataloged: `20` rows (`D01` through `D20`) [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md:34-54`]
   - Every row tagged: `UNVERIFIED-PARAPHRASE` with approximate minute marker [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_direct_view_deep.py`]
   - Quotation marks check: `0` quotation characters (`"`, unicode quotes) in document [SOURCED: command `python MyTradingSys/research/rumers_2026-11-01/verify_direct_view_deep.py`]
   - Gap handling: `NOT_STATED` explicitly applied to missing stops, targets, or parameters [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md:34-54`]
   - Parameter gap matrix: 13 key parameters mapped between SOURCED video values and NOT_STATED items requiring frozen defaults in `PRE_REG` [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_DIRECT_VIEW_DEEP.md:120-137`]

2. **Verification Suite:** `MyTradingSys/research/rumers_2026-11-01/verify_direct_view_deep.py`
   - Tested on pre-change code: exit code 1 (`FAIL: MyTradingSys\research\rumers_2026-11-01\RUMERS_DIRECT_VIEW_DEEP.md does not exist`)
   - Tested on post-change code: exit code 0 (`PASS: MyTradingSys\research\rumers_2026-11-01\RUMERS_DIRECT_VIEW_DEEP.md verified successfully (20 rules across 5 videos, all UNVERIFIED-PARAPHRASE, NOT_STATED used, no quotes).`)

## 3. Key Findings Across the 5 Top-Ranked Videos

| Video ID | Primary Architecture | SOURCED Mechanics | Key Gaps Marked NOT_STATED |
|---|---|---|---|
| `6WfTIyJ-YzQ` | 15m ORB Manipulation Reversal | 15m candle range >= 20% of Daily ATR(14); 5m hammer/inverted hammer wick >= 2x body; stop beyond day extreme wick tip; target 50% midpoint and 100% opposite boundary | Fixed buffer beyond wick tip; session anchor hour for 24/7 crypto |
| `EoQDQVblmMY` | Box Theory PDH/PDL Sweep Fade | Sweep outside PDH/PDL followed by 5m candle closing back inside box; stop beyond sweep wick tip; target 50% midpoint and opposite boundary | Exact daily session cutoff hour; tick buffer outside sweep wick |
| `xtN0U-j_4Jc` | 9 EMA Trend Pullback & Trail | 5m chart; 9 EMA on Close; touch/test rejection candle; stop below swing low/9 EMA; target 1:2 R; trail stop on 9 EMA with exit on opposite candle close | Exact numerical distance for overextension; touch tolerance band |
| `kozesVBKkg4` | Session VWAP Bounce & Breakout | Regular session open VWAP anchor; bounce on rejection candle with 1:2 R target; tight 3-5 candle flag breakout above VWAP with stop below VWAP | Standard deviation bands (none used); ATR trailing multiplier for breakout |
| `l0j1irTKIUw` | 9 EMA Separator Scalp & Retest | Counter-trend scalp targeting 9 EMA line on extreme separator exhaustion wick; orderly retest continuation targeting prior high and 1:2-1:3 R; exit on 9 EMA breakdown | Numerical ATR separator multiple threshold; volume MA multiplier for breakdown |

Noticed: Across all five videos, Doug and Silvia emphasize mechanical candlestick geometries (hammer wick >= 2x body, 5m close back inside boundary, 5m close through 9 EMA) combined with structural levels (15m ORB, PDH/PDL, 9 EMA, VWAP), but consistently leave tick buffers and 24/7 crypto session definitions unstated, meaning downstream DEV backtests under `HARNESS.md` must declare these specific parameters as `OURS` in `PRE_REG` prior to running trials.
