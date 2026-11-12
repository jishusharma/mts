# NY Open Rules Sweep (Iteration 3 — Flash)

Scope: Tom Vorwald and Fabio Valentini statements in `raw_transcripts_canonical/*_raw.txt` on NY open, New York open, 9:30, 8:30, cash open, opening range, and London vs NY, compared against our codebase.

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| NY open 30m wait | Fabio | usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session | DyS79Eb92Ug [4:14] | Wait out the first 30 minutes of the NY cash open for stability before taking normal session reads. | SOURCED: 30 minutes | MyTradingSys/backtest/layers/fabio/v3/day_gates.py:19 (GATE_MIN_ELAPSED = 60 when g != off, not 30; no 30m open-wait gate in models A/B/D) |
| NY open 30m lockout | Tom | stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. | Of_wlv3xaZo [no-ts] | Do not trade during the first 30 minutes of the NY session; use that 30-min range to read the day. | SOURCED: 30 minutes | NONE (MyTradingSys/backtest/tom_dax_bt.py has no NY 30m lockout) |
| Narrow 30m open range -> trend | Tom | Watch the open. If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. | Of_wlv3xaZo [no-ts] | A relatively narrow first-30m NY opening range implies large traders could position and the market will likely trend after 30 min. | SOURCED: 30 minutes (threshold for narrow: NOT_SEEN) | NONE |
| Opening range size -> hold/fail | Tom | Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will. | Fj4FDZQxw0I [no-ts] | A very large opening range likely fails to hold; a very small opening range likely holds. | NOT_SEEN | NONE |
| ORB / IB window options | Fabio | You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes. It depends how you want to use it. If you want to use it more scalp or more intraday bias | cUTsoU-15Tc [2:10] | Define the opening range high/low over the first 15, 30, or 60 minutes depending on scalp vs intraday bias. | SOURCED: 15, 30, or 60 minutes | MyTradingSys/backtest/layers/fabio/v3/engine.py:18 (IB_LEN = 30 hardcoded for Model C only; 15 and 60 not implemented) |
| 15m ORB + statistical TP1 | Fabio | You buy or sell the breakout of the first 15 minutes of the cash session. | cUTsoU-15Tc [0:02] | Trade the breakout of the first 15 minutes of the cash session. | SOURCED: 15 minutes | NONE |
| 15m ORB TP1 hit rate | Fabio | So you know that with 65 to 70% probability, you go here | cUTsoU-15Tc [8:55] | Statistical excursion model gives 65-70% probability of reaching TP1 after an ORB/IVB breakout. | SOURCED: 65 to 70% | NONE |
| 30m IB definition | Fabio | The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading. | StaphlRH8NQ [8:10] | Initial balance = high and low established in the first 30 minutes of regular cash trading. | SOURCED: 30 minutes | MyTradingSys/backtest/layers/fabio/v3/engine.py:18 (IB_LEN = 30) |
| 30m ORB Nasdaq upside skew | Fabio | if the opening range of the first 30 minutes hold predicted value over the coin flip. And we can see that we have a skew of 13.5% | StaphlRH8NQ [8:41] | Blind 30-min Nasdaq ORB at 1:1 RR shows a 13.5% skew over a coin flip without order-flow filtering. | SOURCED: 30 minutes; 13.5% skew | MyTradingSys/backtest/layers/session/session_momentum.py:16-17 (first_min = 30, but implements first-30m vs last-30m return, not ORB) |
| ORB low untouched rate | Fabio | because the model is saying look that this low is not getting touched 80% of the time. | DyS79Eb92Ug [1:39:21] | Under the ORB model, the opening range low is not touched again 80% of the time after breakout. | SOURCED: 80% | NONE |
| Range chart vs 1m at NY open | Fabio | I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated. | DyS79Eb92Ug [5:33] | Switch from 1-minute candles to a 40-range chart at the NY open so fast candles do not hide intra-bar order flow. | SOURCED: 40 range | MyTradingSys/backtest/layers/fabio/v3/engine.py:5 (1m bars only; no range-bar aggregation) |
| NY cash open clock | Tom | here was the market open today at say 9:00 in the DAX or at 15:30 the cash session which is where the big money enters the markets in America in this case that's the SNP500 | rrHj24GSR6M [no-ts] | US cash session opens at 15:30 CET (9:30 ET), when big money enters US indices (S&P 500). | SOURCED: 15:30 (CET = 9:30 ET) | MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60-64 (13:30/14:30 UTC DST-aware); MyTradingSys/backtest/layers/session_levels/session_levels.py:30 (US_OPEN_MIN = 840 = 14:00 UTC fixed); MyTradingSys/backtest/layers/alerts/live_level_touch.py:7 (13:30Z fixed) |
| 8:30 ET news vs 9:30 open | Tom (guest DTR) | because of news it was 8:30 and it did get a follow through before coming back down | rCTrQ4fkL1Y [no-ts] | 8:30 ET is the macro news window before the 9:30 ET equity cash open. | SOURCED: 8:30 | NONE |
| RTH vs ETH profile split | Fabio | So this dark orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. These are the ETH or extended or electronic trading hour session. | 9IliXww64uM [3:51] | Separate the NY Regular Trading Hours (RTH) profile from Asian/London Extended Trading Hours (ETH) because ETH has less volume. | NOT_SEEN | MyTradingSys/backtest/layers/fabio/fabio_of_model.py:118-124 (splits 24/7 BTC into asia/london/ny including weekends, no RTH-only vs ETH split) |
| NY-only for US indices | Fabio | and I only trade in the New York session for US indices because it's where the majority of the volume get traded, and I find it from statistical validation, the London session to be usually for US indices not so valuable to add to the profile. So, I only use the cash session profile. | Pz8f0wWW12M [29:00] | For US indices, trade only the NY session and build profiles from the cash (RTH) session only, excluding London. | NOT_SEEN | MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60-71 (defines ny_open_utc and london_open_utc); MyTradingSys/backtest/layers/fabio/fabio_of_model.py:124 |
| Skip London on low PF | Fabio | You can understand you know that London session is not worth to trade for me. My profit factor is really low. I pay a lot of commission but profit factor is really low. | 0KyIEdvVKMQ [no-ts] | Filter out London session if its profit factor is too low after commissions, freeing half the day. | NOT_SEEN | NONE |
| Big-trade threshold NY vs London | Fabio | Always the same. It's 30 contracts. >> If you are in London, I use 20. | DyS79Eb92Ug [27:16] | Big-trade bubble filter is 30 contracts in NY session vs 20 contracts in London session. | SOURCED: 30 contracts (NY), 20 contracts (London) | NONE (MyTradingSys/backtest/layers/fabio/v3/engine.py:25 uses BTC volume z_hi {2.0, 2.5, 3.0}) |
| Open inside prior NY VA -> range day | Fabio | inside of the previous value area. This is already a good sign that we're probably going to stay inside of this range for the rest of the day because there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday. | 9IliXww64uM [6:05] | If Asian/London had no price discovery and NY opens inside yesterday's NY value area, expect a range/balance day. | NOT_SEEN | MyTradingSys/backtest/layers/fabio/fabio_of_model.py:137-140 (checks close > vah / close < val, not NY open inside prior RTH VA) |

## TOP 5

1. **Both Tom and Fabio independently require waiting out the first 30 minutes of the NY open — our code uses 60 minutes (or 0).** Fabio waits the first 30 minutes (`DyS79Eb92Ug [4:14]`) and Tom explicitly warns to stop trading in the first 30 minutes (`Of_wlv3xaZo [no-ts]`). In our codebase, `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:19` sets `GATE_MIN_ELAPSED = 60` when `g != off`, and models A/B/D have no 30-minute open lockout at all.
2. **Opening-range width as a day-type / hold-vs-fail classifier is central to Tom and Fabio, and completely uncoded.** Tom uses the 30-minute opening range size (narrow -> trend day; very large -> won't hold; very small -> will hold; `Of_wlv3xaZo [no-ts]`, `Fj4FDZQxw0I [no-ts]`), and Fabio pairs 15/30/60-min ORB with statistical excursion targets (65–70% TP1, 80% low untouched, 13.5% Nasdaq upside skew; `cUTsoU-15Tc`, `StaphlRH8NQ`, `DyS79Eb92Ug`). Our `MyTradingSys/backtest/layers/fabio/v3/engine.py:18` only hardcodes `IB_LEN = 30` for Model C and never classifies OR width.
3. **NY RTH-only profile vs ETH (London/Asia) separation is violated in our 24/7 BTC adaptation.** Fabio explicitly excludes London from US-index volume profiles (`Pz8f0wWW12M [29:00]`) and separates RTH vs ETH (`9IliXww64uM [3:51]`), whereas `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:118-124` builds profiles across all three sessions (`asia`, `london`, `ny`) on 24/7 BTC including weekends.
4. **Inconsistent NY open clock across our modules.** `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:60-64` and `MyTradingSys/tools/us_open_alert.py:32-37` correctly compute 13:30 UTC (EDT) / 14:30 UTC (EST), but `MyTradingSys/backtest/layers/session_levels/session_levels.py:30` hardcodes `US_OPEN_MIN = 840` (14:00 UTC, wrong in both EDT and EST) and `MyTradingSys/backtest/layers/alerts/live_level_touch.py:7` hardcodes `13:30Z` (wrong in winter EST).
5. **1-minute bar aggregation loses NY-open order flow.** Fabio switches from 1m/5m candles to a 40-range chart at the NY open because 1m bars aggregate huge moves (`DyS79Eb92Ug [5:33]`); our entire `fabio/v3/engine.py` runs strictly on 1m bars.

## SINGLE BIGGEST HOLE

**Transfer-assumed 24/7 BTC session slicing + missing 30-minute NY open-range regime read.** Both Tom and Fabio treat the first 30 minutes of the 09:30 ET cash open as a distinct liquidity event: do not trade the first 30 minutes, measure the 30-minute opening-range width and whether NY opens inside prior RTH value, and only trade NY RTH volume profiles (excluding low-volume London/Asia ETH). Our code either applies a 60-minute `day_gate` (`GATE_MIN_ELAPSED = 60`), hardcodes `US_OPEN_MIN = 840` (14:00 UTC) in `session_levels.py`, or forces 24/7 BTC into `asia`/`london`/`ny` slices including weekends without any opening-range width or RTH-open-in-VA regime classifier.

## Verbatim quote verification

> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session"
**Source GPS: DyS79Eb92Ug | BEGIN**

> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE**

> "Watch the open. If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that."
**Source GPS: Of_wlv3xaZo | BEGIN**

> "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will."
**Source GPS: Fj4FDZQxw0I | END**

> "You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes. It depends how you want to use it. If you want to use it more scalp or more intraday bias"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "You buy or sell the breakout of the first 15 minutes of the cash session."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "So you know that with 65 to 70% probability, you go here"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading."
**Source GPS: StaphlRH8NQ | MIDDLE**

> "if the opening range of the first 30 minutes hold predicted value over the coin flip. And we can see that we have a skew of 13.5%"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "because the model is saying look that this low is not getting touched 80% of the time."
**Source GPS: DyS79Eb92Ug | END**

> "I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated."
**Source GPS: DyS79Eb92Ug | BEGIN**

> "here was the market open today at say 9:00 in the DAX or at 15:30 the cash session which is where the big money enters the markets in America in this case that's the SNP500"
**Source GPS: rrHj24GSR6M | MIDDLE**

> "because of news it was 8:30 and it did get a follow through before coming back down"
**Source GPS: rCTrQ4fkL1Y | MIDDLE**

> "So this dark orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. These are the ETH or extended or electronic trading hour session."
**Source GPS: 9IliXww64uM | BEGIN**

> "and I only trade in the New York session for US indices because it's where the majority of the volume get traded, and I find it from statistical validation, the London session to be usually for US indices not so valuable to add to the profile. So, I only use the cash session profile."
**Source GPS: Pz8f0wWW12M | END**

> "You can understand you know that London session is not worth to trade for me. My profit factor is really low. I pay a lot of commission but profit factor is really low."
**Source GPS: 0KyIEdvVKMQ | END**

> "Always the same. It's 30 contracts. >> If you are in London, I use 20."
**Source GPS: DyS79Eb92Ug | BEGIN**

> "inside of the previous value area. This is already a good sign that we're probably going to stay inside of this range for the rest of the day because there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday."
**Source GPS: 9IliXww64uM | MIDDLE**
