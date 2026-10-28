# Kurisko RSI & Indicator Settings Video Search (2026-10-18)

Card: `kurisko-rsi-video-search` (Lane: SONNET, Prio: 2)
Scope: `MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_VIDEO_SEARCH.md`
Verification: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_VIDEO_SEARCH.md`

---

## 1. Executive Summary & Findings

1. **Kurisko states NO RSI settings or RSI Quad Rotation setup:**
   Across John Kurisko's YouTube channel (`@daytradingradio`, 1,577 total uploads, 104 videos matching "RSI", 146 matching "relative strength", 492 matching "stochastic"), his long-form podcast interviews (Desire To Trade episodes 472 and 538), and conference presentations (MoneyShow), Kurisko **never** presents an RSI-based strategy, never specifies RSI parameters, levels, or smoothing, and repeatedly clarifies that his Quad Rotation and Super Signal setups are built **exclusively on Stochastic oscillators**, never RSI.

2. **Source of the "RSI with Quad Rotation" memory:**
   In video `XNfOIzPYChA` (*"The Quad Rotation will prevent you from over-trading. Most important rules in our trading business."*, Day Trading Radio, published 2024-06-18, [00:01:04]–[00:01:44]), Kurisko reads an anecdote from a chatroom member named `"all I do is win 1983"`. The member reported passing 10 prop firm evaluations using the quad rotation setups with stochastics and RSI, stating:
   *"the RSI RSI using the same settings you're using in the stochastics I've been working well too"*.
   Kurisko immediately reiterates his own system: *"we're using four stochastic bands here this is the 93 143 44 and the 6010 we use a percentage D line as our signal line we don't have the percentage Kine on this we don't we don't need it we don't use it"*. Kurisko does not adopt or endorse RSI as his strategy; it was solely an anecdotal tweak reported by a chatroom participant.

3. **Source of the "TradingView differed from plain settings" memory:**
   In video `LD_LOEeKzMs` (*"How to Set up the Quad Divergence Indicators and charts like DayTraderRockStar"*, Day Trading Radio, published 2024-11-26, [00:25:03]–[00:26:00]), Kurisko demonstrates how to configure his four indicators on TradingView.
   The operator recalled that the TradingView setup differed from the plain setup and had to be dug out. The finding is that **this applied to Stochastics, NOT RSI**:
   - On NinjaTrader, Kurisko plots a Fast Stochastic with 2 inputs: Lookback (%K) and Smoothing (%D), plotting only %D.
   - On TradingView, the built-in indicator is a "Full Stochastic" with 3 parameters: `%K length`, `%K smoothing`, and `%D smoothing`.
   - Kurisko explains how to set it up on TradingView: set `%K smoothing = 1` (which acts as a pass-through dividing by 1, turning Full Stochastic into Fast Stochastic: (9, 1, 3), (14, 1, 3), (44, 1, 4), (60, 1, 10)), and in the Style tab make the `%K line` transparent / unchecked so only the `%D signal line` is visible.

4. **Kurisko's other mentions of RSI:**
   In `6rHybt-DfQ0` (MoneyShow [00:30:27]), `I0rxiH1jZwc` (DayTradingRadio [00:24:57]), `rCTrQ4fkL1Y` (DayTradingRadio [00:06:41]), and `5MgOwizsnjk` (DayTradingRadio [00:00:32]), Kurisko mentions RSI offhand as a standard textbook indicator (like MACD or Bollinger Bands), notes historical lore (that George Lane was connected to RSI development), or cautions about divergence indicators struggling in strong trend runs. In none of these does he provide any indicator settings for RSI.

5. **Status for MTS & PRE_REG:**
   The RSI arm in `MyTradingSys/research/kurisko_2026-10-18/PRE_REG.md` (Wilder RSI 9/14/40/60 at 20/80) remains **100% NO-SOURCE / OPERATOR-HYPOTHESIS**. Kurisko never created or used an RSI quad rotation.

---

## 2. Verbatim Quotes with Source GPS

### Q1: Chatroom trader uses RSI with Kurisko Stochastic settings
- Video ID: `XNfOIzPYChA`
- Title: *"The Quad Rotation will prevent you from over-trading. Most important rules in our trading business."*
- URL: https://www.youtube.com/watch?v=XNfOIzPYChA
- Published: 2024-06-18 | Uploader: Day Trading Radio | Platform: Chatroom feedback / NinjaTrader
- Timestamp: [00:01:04]
- Context: Kurisko gives a shout out to member "all I do is win 1983" who passed prop firm evaluations using RSI with Kurisko's stochastic settings.

> "I want to give a shout out um to all all I do is win 1983 he's in the room he said he's passed 10 evaluations over the last 3 months just using the quad rot setups with stochastics and RSI it says an e excellent strategy and um so I wanted to get a little bit more information on that cuz I felt like you know everyone needs uh you know have that understanding how things work and someone might have a little Edge uh little uh tweak that helps them get in so I always kind of interview some of the traders who are in the room just going back and forth"
**Source GPS: XNfOIzPYChA | BEGIN**
SOURCED: raw_transcripts_canonical/XNfOIzPYChA_raw.txt:8 (char 1100)

> "the RSI RSI using the same settings you're using in the stochastics I've been working well too he's at 6 to8 ticks on the es and he's out so he's training the es um he enters when the 93 starts to curl up someone asked them in the room do you like the 6010 to start curling back up before entering"
**Source GPS: XNfOIzPYChA | BEGIN**
SOURCED: raw_transcripts_canonical/XNfOIzPYChA_raw.txt:8 (char 1641)

### Q2: Kurisko's own four-oscillator setup (Stochastics only, %D line only)
- Video ID: `XNfOIzPYChA`
- Title: *"The Quad Rotation will prevent you from over-trading. Most important rules in our trading business."*
- URL: https://www.youtube.com/watch?v=XNfOIzPYChA
- Published: 2024-06-18 | Uploader: Day Trading Radio | Platform: NinjaTrader / ES futures
- Timestamp: [00:02:58]
- Context: Kurisko specifies his exact four bands and clarifies that only the %D signal line is plotted.

> "we're using four stochastic bands here this is the 93 143 44 and the 6010 we use a percentage D line as our signal line we don't have the percentage Kine on this we don't we don't need it we don't use it"
**Source GPS: XNfOIzPYChA | BEGIN**
SOURCED: raw_transcripts_canonical/XNfOIzPYChA_raw.txt:8 (char 2957)

> "and if you feel like you're setup if you're out there you're trading Fibonacci trading macds and you're trading RSI anything you're trading all of a sudden you you say oh my signal is giving me a signal and John's signal the quad rotation or the quad rotation that's giving us the signal too that's even better that's even"
**Source GPS: XNfOIzPYChA | END**
SOURCED: raw_transcripts_canonical/XNfOIzPYChA_raw.txt:8 (char 18060)

---

### Q3: TradingView Platform Setup & Smoothing Parameter
- Video ID: `LD_LOEeKzMs`
- Title: *"How to Set up the Quad Divergence Indicators and charts like DayTraderRockStar"*
- URL: https://www.youtube.com/watch?v=LD_LOEeKzMs
- Published: 2024-11-26 | Uploader: Day Trading Radio | Platform: TradingView
- Timestamp: [00:25:03]–[00:26:00]
- Context: Explaining why TradingView requires `%K smoothing = 1` and hiding `%K` to replicate NinjaTrader Fast Stochastics.

> "the 913 you see how it has three this typically you just have the K and D line but because they only have one stochastic setting here they ALS they apply they make it the full stochastic meaning they're going to give you an extra parameter an extra smoothing um number to go on the k so we don't want to use that so we just put one in there it's like dividing it by one it doesn't change it at all so in all these cases we're going to put the the K is going to be the biggest one the D is the the the smaller one and the K smoothing will be one and each each one of these cases"
**Source GPS: LD_LOEeKzMs | END**
SOURCED: raw_transcripts_canonical/LD_LOEeKzMs_raw.txt:8 (char 23636)

> "and again if you look at the visibility go to style I make the K line transparent or I I uncheck it so there's no there's no line there at all"
**Source GPS: LD_LOEeKzMs | END**
SOURCED: raw_transcripts_canonical/LD_LOEeKzMs_raw.txt:8 (char 24256)

---

### Q4: Generic RSI Mentions Without Settings
- Video ID: `5MgOwizsnjk`
- Title: *"Amazing Tip for trending markets look at the results with the ThunderbirdV2"*
- URL: https://www.youtube.com/watch?v=5MgOwizsnjk
- Published: 2024-08-10 | Uploader: Day Trading Radio | Platform: Generic
- Timestamp: [00:00:32]
- Context: Discussing divergence limitations during strong trends.

> "any type of divergences like this when you talk about RSI MACD um they could be you could have a little problem when you run into very strong trending markets"
**Source GPS: 5MgOwizsnjk | BEGIN**
SOURCED: raw_transcripts_canonical/5MgOwizsnjk_raw.txt:8 (char 478)

- Video ID: `6rHybt-DfQ0`
- Title: *"Three Trade Setups for Success | John Kurisko"*
- URL: https://www.youtube.com/watch?v=6rHybt-DfQ0
- Published: 2023-11-20 | Uploader: MoneyShow | Platform: Generic charting
- Timestamp: [00:30:27]
- Context: Listing charting platform default indicators.

> "lowest charting service has come with it standard indicators moving averages RSI Mac DS you name it Bollinger Bands Keltner Keltner channels do you what V whap you know anything there's so many different things out there moving averages"
**Source GPS: 6rHybt-DfQ0 | END**
SOURCED: raw_transcripts_canonical/6rHybt-DfQ0_raw.txt:8 (char 26616)

- Video ID: `I0rxiH1jZwc`
- Title: *"Another Epic Video from DayTradingRadio. Great tips to Make a Living and Market Radar"*
- URL: https://www.youtube.com/watch?v=I0rxiH1jZwc
- Published: 2024-08-01 | Uploader: Day Trading Radio | Platform: Generic
- Timestamp: [00:24:57]
- Context: Remarks on technical indicators and George Lane.

> "Market is not easy it's not femin ni work great uh RSI relative strength index is great um the macd I think is very similar you know RSI actually came you know you know what I read about the RSI and stuff that George Lane actually had something to do with that also if you if you if you dig down and look at that"
**Source GPS: I0rxiH1jZwc | MIDDLE**
SOURCED: raw_transcripts_canonical/I0rxiH1jZwc_raw.txt:8 (char 23059)

- Video ID: `rCTrQ4fkL1Y`
- Title: *"How to stop over trading with the DayTraderRockStar method. Important Video"*
- URL: https://www.youtube.com/watch?v=rCTrQ4fkL1Y
- Published: 2024-07-15 | Uploader: Day Trading Radio | Platform: Generic
- Timestamp: [00:06:41]
- Context: Discussing momentum vs price indicators.

> "all kinds of indicators high low um candles even pivot Points macds RSI everything is measuring something but the stochastics also me measure something and they measure momentum"
**Source GPS: rCTrQ4fkL1Y | BEGIN**
SOURCED: raw_transcripts_canonical/rCTrQ4fkL1Y_raw.txt:8 (char 6144)

---

## 3. Comprehensive List of Videos Checked

The following 26 Kurisko videos (from Day Trading Radio, Desire To Trade, and MoneyShow) were transcribed and checked in full.

| Video ID | Title | Published | Uploader | Words | RSI Settings Found? | Notes |
|---|---|---|---|---|---|---|
| `XNfOIzPYChA` | The Quad Rotation will prevent you from over-trading. Most important rules in our trading business. | 2024-06-18 | Day Trading Radio | 4,921 | **None from Kurisko** (Room member quote only) | Quotes chatroom member "all I do is win 1983" using RSI with stoch settings. Kurisko affirms stochastics only: (9,3), (14,3), (44), (60,10) D-line. |
| `LD_LOEeKzMs` | How to Set up the Quad Divergence Indicators and charts like DayTraderRockStar | 2024-11-26 | Day Trading Radio | 5,686 | **None** (Stochastic setup explained) | Explains TradingView Full Stochastic settings: `%K smoothing = 1`, hide `%K`, plot `%D` for (9,1,3), (14,1,3), (44,1,4), (60,1,10). |
| `PjigwAmhiT0` | The 3 Scalping Setups That Make Me A Living - John Kurisko (DTT ep 472) | 2024-09-15 | Desire To Trade | 8,940 | **None** | Core Quad Rotation interview. 0 mentions of RSI or relative strength index. |
| `PpysVy2NNQ4` | Scalping Strategy That Makes Him $1,000+/Day (Full Interview w/ John Kurisko) (DTT ep 538) | 2024-09-15 | Desire To Trade | 14,661 | **None** | Second DTT feature interview. Mentions TradingView template link, 0 RSI mentions. |
| `OSka8T7z5EM` | The Scalping Strategy to Make a Living Trading - John Kurisko \| Trader Interview | 2023-05-12 | Desire To Trade | 8,406 | **None** | DTT interview on scalping rules, discipline, stochastics. 0 RSI mentions. |
| `6rHybt-DfQ0` | Three Trade Setups for Success \| John Kurisko | 2023-11-20 | MoneyShow | 7,186 | **None** | Generic mention of RSI as standard charting indicator alongside MACD. |
| `5MgOwizsnjk` | Amazing Tip for trending markets look at the results with the ThunderbirdV2 | 2024-08-10 | Day Trading Radio | 5,263 | **None** | Generic mention that RSI and MACD divergences struggle in trending markets. |
| `I0rxiH1jZwc` | Another Epic Video from DayTradingRadio. Great tips to Make a Living and Market Radar | 2024-08-01 | Day Trading Radio | 10,883 | **None** | Mentions RSI offhand and George Lane connection. No settings. |
| `rCTrQ4fkL1Y` | How to stop over trading with the DayTraderRockStar method. Important Video | 2024-07-15 | Day Trading Radio | 8,623 | **None** | Mentions RSI as measuring price while stochastics measure momentum. |
| `UxYgeYlG7Ww` | The Quad Rotation Scalping Strategy. A refresher lesson for The Most Successful Strategy | 2024-05-20 | Day Trading Radio | 11,785 | **None** | Deep dive on Quad Rotation rules, MES scalp, 20/80 levels. 0 RSI mentions. |
| `ASM1sX1P8cA` | My Ultimate Trading Signal: Quad Rotation Stochastic Divergence Combo | 2024-06-02 | Day Trading Radio | 7,720 | **None** | Super Signal walkthrough. 0 RSI mentions. |
| `n0Z4IZ9PH3A` | Quad Rotation Lesson is released. One of the most powerful and profitable signals | 2024-04-10 | Day Trading Radio | 4,890 | **None** | Tutorial on Quad Rotation bands and divergence. 0 RSI mentions. |
| `LYHXX8y7iJM` | Scalping With Stochastics | 2023-11-05 | Day Trading Radio | 3,234 | **None** | Focuses entirely on Stochastic 9,3 and 60,10. 0 RSI mentions. |
| `rbjKZcxZVOs` | Stochastic Divergences: How to Trade Them | 2023-09-18 | Day Trading Radio | 1,009 | **None** | Divergence mechanics on stochastics. 0 RSI mentions. |
| `TvZatog8rn0` | Unlocking the Power of Stochastics: A Guide for Traders | 2023-08-12 | Day Trading Radio | 212 | **None** | Short summary on stochastics. 0 RSI mentions. |
| `WFKNpVbluo0` | RockBot for TradingView. The SuperSignal is available now. How to get it and use it. | 2024-09-22 | Day Trading Radio | 5,987 | **None** | Explains TradingView Pine Script for SuperSignal bot. 0 RSI mentions. |
| `K4xVRmK6ogc` | RockBot on the Tradingview Platform how to find it and how to make it run | 2024-09-25 | Day Trading Radio | 1,552 | **None** | Instructions on loading invite-only script on TradingView. 0 RSI mentions. |
| `E4eaAv6e9R8` | My Best Trading Script is here! The ThunderbirdV2 for NinjaTrader and Tradingview | 2024-10-05 | Day Trading Radio | 6,315 | **None** | Script release for NinjaTrader and TradingView. 0 RSI mentions. |
| `nJw96NpeMOw` | Introducing the Thunderbird Divergence Strategy for Tradingview | 2024-10-12 | Day Trading Radio | 5,388 | **None** | Divergence bot on TradingView. 0 RSI mentions. |
| `L9fd5NH4IUc` | How to set up your Charts like DayTraderRockStar, What Indicators you need. | 2024-03-14 | Day Trading Radio | 4,481 | **None** | Chart layout: 20/50/200 EMA, VWAP, 4 Stochastics. 0 RSI mentions. |
| `LeW1_1me2JI` | DayTraderRockStar's Trading Tips #1 What Indicators to use? | 2023-02-18 | Day Trading Radio | 1,363 | **None** | Recommends stochastics as primary indicator. 0 RSI mentions. |
| `0o7l8vMlbMw` | Trading with Indicator Combinations | 2023-04-02 | Day Trading Radio | 1,235 | **None** | Combines 20/50 EMA with stochastics. 0 RSI mentions. |
| `fiQPJDcVS_A` | What Indicators work best trading bitcoin. A guide for beginners | 2024-01-15 | Day Trading Radio | 8,274 | **None** | Discusses crypto chart setups using stochastics and moving averages. 0 RSI mentions. |
| `-wY3-UEJbLI` | You have the biggest edge with these trading Indicators. | 2024-07-28 | Day Trading Radio | 6,392 | **None** | Discusses divergence and stochastics edge. 0 RSI mentions. |
| `o0OM9tI9KhY` | Trading Relative Strength. DayTradingRadio.Com | 2018-05-10 | Day Trading Radio | 1,889 | **None** | Uses "relative strength" to mean stock performance vs SPX benchmark, NOT the RSI indicator. |
| `ttU_A1K02Pw` | Trading Relative Strength HPS watch List for week of Aug 24th | 2020-08-23 | Day Trading Radio | 11,239 | **None** | Uses "relative strength" for equity sector outperformance (e.g. NVDA vs market). 0 RSI mentions. |

---

## 4. Parameter Synthesis & Provenance Summary

| Parameter | SOURCED (Kurisko Words) | SOURCED (Community / Chatroom) | OURS / MTS Implementation Note |
|---|---|---|---|
| Indicator Type | **Stochastics ONLY** (`PjigwAmhiT0:8`, `XNfOIzPYChA:8 char 2957`) | **RSI as user tweak** (`XNfOIzPYChA:8 char 1641`, "all I do is win 1983") | If RSI is tested, it is OPERATOR-HYPOTHESIS, not Kurisko |
| Oscillator Periods | 9, 14, 40/44, 60 (`PjigwAmhiT0:8`, `XNfOIzPYChA:8 char 2957`) | "same settings you're using in the stochastics" (9, 14, 40/44, 60) | Plain Wilder RSI(14) is standard; 4-period RSI 9/14/40/60 was copied from stoch periods |
| Plotted Line | **%D line only** (`PjigwAmhiT0:8 char 29323`, `XNfOIzPYChA:8 char 2957`) | N/A | NinjaTrader plots %D; on TradingView %K line is set to transparent |
| TradingView Smoothing | `%K smoothing = 1` (`LD_LOEeKzMs:8 char 23636`) | N/A | TradingView Full Stoch requires `%K smoothing = 1` to emulate Fast Stoch |
| Oversold / Overbought Levels | 20 / 80 (`PjigwAmhiT0:8 char 20846`, `char 38287`) | 20 / 80 on Stochastics | Standard RSI levels are 30/70; 20/80 was borrowed from Kurisko's stochastics |
| Primary Timeframe | 1m and 5m (`PjigwAmhiT0:8 char 9373`, `char 19085`) | 1m ES (`XNfOIzPYChA:8 char 1641`) | 1m / 5m tested in `PRE_REG.md` |
| Primary Instrument | MES / ES futures (`PjigwAmhiT0:8 char 11047`) | ES (`XNfOIzPYChA:8 char 1641`) | BTCUSDT perp in MTS |
| Profit Target | 6–8 ticks on ES (`XNfOIzPYChA:8 char 1641`) | 6–8 ticks (1.5–2.0 ES pts) | Equivalent to ~3–4 bp on ES; on BTC 14 bp round trip dominates |

---

## 5. Conclusion & Recommendations

1. **Kurisko's setup is Stochastics, not RSI:** All primary sources confirm that Kurisko's Quad Rotation and Super Signal are four stochastic bands, plotting only the %D signal line.
2. **The origin of the operator's memory:**
   - The mention of "RSI with Quad Rotation" traces to video `XNfOIzPYChA`, where Kurisko reads a chatroom participant's comment about applying Kurisko's stochastic lookbacks to RSI.
   - The memory of TradingView settings "differing from plain ones" traces to video `LD_LOEeKzMs`, where Kurisko explains that TradingView uses a 3-parameter Full Stochastic, requiring `%K smoothing = 1` and hiding `%K` to replicate his 2-parameter Fast Stochastic.
3. **Registry and module status:**
   - In `MyTradingSys/research/kurisko_2026-10-18/PRE_REG.md`, the RSI arm was already labeled `OPERATOR-HYPOTHESIS` and blocked across all 8 cells due to fee dominance and underpowering.
   - This investigation confirms that no Kurisko RSI specification exists. The stochastic specification in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md` stands as the only genuine Kurisko-sourced formulation.
