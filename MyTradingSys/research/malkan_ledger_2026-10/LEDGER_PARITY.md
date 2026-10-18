# Malkan: Dated-Call Ledger Feasibility and RSI Parity Points (Gate 0c)

Date: 2026-10-18
Card: `malkan-ledger-parity-feasibility`
Checklist: `MyTradingSys/backtest/PRE_REG_TEMPLATE.md` (items 2, 3, 5; Gate 0c)
Sources: `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md`, `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md`
Scope in: 6 extracted videos (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/`), saved captions (`raw_transcripts_canonical/`), channel priority metadata (`MyTradingSys/research/video_priority_2026-10-15/`)

## 0. Summary and Gate 0c Verdict

- Dated calls: 0
- RSI parity points: 6
- Minute timestamps possible: NO
- Design/check split possible: NO
- Verdict: HYPOTHESIS

Gate 0c criterion (SOURCED: `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:14`): "0c Record: does the source have dated calls or trades we can score on BTC data? Score them first (B162 is the template). No record: hypothesis, never a core."
Threshold rule (SOURCED: `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:21`): "Fewer than 20 scorable calls means the layer stays a hypothesis under gate 0c, not a core."
Because 0 dated calls or trades exist in the corpus (SOURCED: `SETUP_SUMMARY.md:37,78`, `HOME_FIT_AUDIT_MALKAN.md:19`), the layer cannot be scored against a historical trade ledger. It must be classified as a HYPOTHESIS layer, not a core.

---

## 1. Audit of Dated Trades and Calls across 6 Extracts and Saved Captions

Total dated trades or calls found: 0 (SOURCED: `MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md:37,78`, `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:19`).
Every setup row in `SETUP_SUMMARY.md` records: "0 trades in a ledger (lecture video; on-screen examples are not counted)" (SOURCED: `SETUP_SUMMARY.md:78,114,142,174,203,232,260,285,313,343,365,390,411,438,458,484,510,536,562,587`).

### 1.1 Extract `-CBvFi40sIQ` (5 Star RSI Strategy Screener)
- Speaker: Learn2Earn presenter recapping Malkan's strategy; Malkan does not speak (SOURCED: `extracts/extract_-CBvFi40sIQ.md:339`).
- Candidate date references:
  - Line 237: > "these criteria were met in Ujjivan, then you can go in and check the chart of Ujjivan on 28th Jan" (SOURCED: `extracts/extract_-CBvFi40sIQ.md:237`).
  - Line 241: > "On 20th Oct one stock was there Ujjivan Small Finance Bank" (SOURCED: `extracts/extract_-CBvFi40sIQ.md:241`).
  - Line 243: > "so both of these cases you can do backtest and check" (SOURCED: `extracts/extract_-CBvFi40sIQ.md:243`).
- Assessment: 0 dated trades. These are historical dates displayed on a third-party screener web page presented as illustrative examples. The host does not state outcomes, entry levels, stops, or execution details (SOURCED: `extracts/extract_-CBvFi40sIQ.md:235,338`).

### 1.2 Extract `2HcJ3NeZmEQ` (RSI 5 Star Set Up #1 Sell Setup)
- Speaker: Vishal Malkan.
- Candidate mentions: Tata Motors and Reliance Infrastructure mentioned on screen as stocks meeting the weekly RSI < 40 condition.
  - Quote: > "here the weekly chart is below 40 right and if you go to daily... Tata Motors is on the list" (SOURCED: `extracts/extract_2HcJ3NeZmEQ.md:61`).
  - Assessment: 0 dated trades. Malkan explicitly states that data for the last 2-3 days was missing and specifies no trade or entry level (SOURCED: `extracts/extract_2HcJ3NeZmEQ.md:240`). No calendar dates or timestamps.

### 1.3 Extract `A-CQiV_UFB4` (8. RSI Reverse Divergence)
- Speaker: Vishal Malkan (Hindi audio, machine-translated English).
- Assessment: 0 dated trades. Teaches reverse divergence concepts (positive and negative reverse divergence). No dates, timestamps, or trade calls (SOURCED: `SETUP_SUMMARY.md:260,285,313,587`).

### 1.4 Extract `cQ-y1oULkBw` (Divergence Trading Strategy)
- Speaker: Vishal Malkan.
- Assessment: 0 dated trades. Conceptual lecture demonstrating divergence identification on educational charts. No dates, timestamps, or trade calls (SOURCED: `SETUP_SUMMARY.md:438,458`).

### 1.5 Extract `W1HrDl70Lhk` (5 Star RSI Strategy)
- Speaker: Trader Insights presenter (secondary source, Hindi audio with machine translation).
- Candidate mentions: Shows stock chart examples with a price target 2068 (> "target is 2068 solar heater go", SOURCED: `extracts/extract_W1HrDl70Lhk.md:503`).
- Assessment: 0 dated trades. The target number 2068 is a chart price level, not a dated trade. The sell example outcome was unobserved because the presenter left for a meeting (SOURCED: `extracts/extract_W1HrDl70Lhk.md:621`). No trade ledger (SOURCED: `SETUP_SUMMARY.md:78,114,142,174,203,232`).

### 1.6 Extract `Wvq1TZh8aF0` (RSI Divergence Explained Simply)
- Speaker: Vishal Malkan.
- Candidate mentions:
  - Mentions stock examples without dates: Tata Motors weekly (`extracts/extract_Wvq1TZh8aF0.md:88`), Jindal Steel daily (`:106`), Astral daily (`:175`).
  - Hypothetical trade interval: "suppose one high was made in April and the second one was made in October" (`:555`).
  - Worked bearish trade on Nifty weekly (A 74.29, B 71, close 6176; `:284-306`): educational walk-through without calendar dates or year.
  - Worked bullish trade on Nifty weekly (37.72 and 38.89, closes 36000, 33000, 32000; `:331-360`): educational walk-through without calendar dates or year.
  - Current market commentary: Commentary on Nifty setup waiting for Monday confirmation (> "When it goes up on Monday , we will trade because support is already visible at 40 there.", SOURCED: `:411`), general discussion of Modi and Trump election rallies (`:406-415`), and unexecuted watch on Zydus Lifesciences ("Jaydis Life", `:422-430`).
- Assessment: 0 dated trades. None carry calendar execution dates, entry prices, or trade logs (SOURCED: `SETUP_SUMMARY.md:484,510,536,562`).

### 1.7 Saved Caption `GbXnw_tNMtw_raw.txt` (Reverse Divergence)
- Speaker: Vishal Malkan.
- Candidate mentions:
  - Quote: "[14:37] in 2011 one of the best years of my life and one of the best trades I did in commodity markets is when daily weekly and monthly RSI hits 90 plus and price double from 70 RSI" (SOURCED: `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt:304-308`).
- Assessment: 0 dated trades. An anecdotal reminiscence mentioning commodity silver in the year 2011. No trade date, no order price, no stop, no exit, and no minute timestamp.

---

## 2. Quoted Chart RSI Values (Parity Points)

Total RSI chart parity points quoted: 6 (OURS count).
All 6 represent specific RSI levels read from chart examples that can serve as parity points for indicator calculation against matching OHLC history.

| # | Chart / Instrument | Point / Feature | Quoted RSI Value | Stated Tolerance | Source Extract (file:line) | Raw Transcript (file:line) |
|---|---|---|---|---|---|---|
| 1 | Nifty Weekly | Bearish divergence Point A | **74.29** | NOT STATED | `extracts/extract_Wvq1TZh8aF0.md:289` | `raw_transcripts_canonical/Wvq1TZh8aF0_raw.txt:7` |
| 2 | Nifty Weekly | Bearish divergence Point B | **71** | NOT STATED | `extracts/extract_Wvq1TZh8aF0.md:289` | `raw_transcripts_canonical/Wvq1TZh8aF0_raw.txt:7` |
| 3 | Unspecified Chart | Peak point (close 6176) | **77.97** | NOT STATED | `extracts/extract_Wvq1TZh8aF0.md:291` | `raw_transcripts_canonical/Wvq1TZh8aF0_raw.txt:7` |
| 4 | Nifty Weekly | Bullish divergence Point A | **37.72** | ~0.5 decimal tolerance | `extracts/extract_Wvq1TZh8aF0.md:334,336` | `raw_transcripts_canonical/Wvq1TZh8aF0_raw.txt:7` |
| 5 | Nifty Weekly | Bullish divergence Point B | **38.89** | ~0.5 decimal tolerance | `extracts/extract_Wvq1TZh8aF0.md:334,336` | `raw_transcripts_canonical/Wvq1TZh8aF0_raw.txt:7` |
| 6 | Unspecified Chart | Lowest RSI on example | **31.73** | NOT STATED (example value) | `extracts/extract_cQ-y1oULkBw.md:180,342` | `raw_transcripts_canonical/cQ-y1oULkBw_raw.txt:7` |

### Verbatim Quotes for Parity Points
1. Point 1 & 2 (74.29, 71):
   - Quote: > "RSI is 74.29 and what is the RSI at point B? 71"
   - Source: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:289`
   - GPS: `Wvq1TZh8aF0 | END`
2. Point 3 (77.97):
   - Quote: > "The RSI value is 77.97 and the closing price at that time is 6176"
   - Source: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:291`
   - GPS: `Wvq1TZh8aF0 | END`
3. Point 4 & 5 (37.72, 38.89):
   - Mechanics quote: "RSI points A 37.72 and B 38.89 on a weekly chart; small decimal differences are acceptable." (SOURCED: `extracts/extract_Wvq1TZh8aF0.md:334`)
   - Verbatim quote: > "It happens in decimals too, 37.7 and 37.2 will also work. Right now it is 38.89."
   - Source: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:336`
   - GPS: `Wvq1TZh8aF0 | END`
   - Stated tolerance: "small decimal differences are acceptable" (specifically illustrating that 37.7 and 37.2 work for a point near 37-38, representing ~0.5 RSI points tolerance).
4. Point 6 (31.73):
   - Quote: > "So, what is the easiest way? The lowest C is this, which is visible here. This one is the lowest C, meaning the lowest RSI is how much? 31, 31.73 now. Is there any price lower than this price?"
   - Source: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:180`
   - GPS: `cQ-y1oULkBw | MIDDLE`
   - Stated tolerance: Not stated as a rule; extract records "the 31.73 reading is an example value, not a rule" (SOURCED: `extracts/extract_cQ-y1oULkBw.md:342`).

### Parity Verification Feasibility
As established in `HOME_FIT_AUDIT_MALKAN.md:40-41`, these 6 parity points are NOT_IN_DATA today because the repo contains Binance spot and Coinbase BTC series, but no historical Indian equity OHLC series (Nifty index weekly bars or stock data). Parity verification must await the acquisition of Indian EOD series scoped in follow-up card C2 (`malkan-universe-data-power`).

---

## 3. Minute Timestamps, Design/Check Split, and Gate 0c Feasibility

### 3.1 Minute Timestamps Possible: NO
- SOURCED: `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:19-20`: "NOT_IN_DATA. There is no dated Malkan trade list. Six videos are extracted (19 setups plus one grade) and every row records '0 trades in a ledger': they are lectures, and on-screen examples are not counted... Chart frames are not in the transcripts, so a candle or level he points at cannot be read ('made here' stops)."
- Without timestamped execution records or video chart frame feeds, minute timestamps are completely NOT_IN_DATA and cannot be constructed.

### 3.2 Design / Check Split Possible: NO
- Item 2 of the 12-item readiness checklist (`PRE_REG_TEMPLATE.md:24`) requires: "The ledger is split into design and check sets."
- With 0 dated calls/trades, no split can be formed.

### 3.3 Gate 0c Verdict: HYPOTHESIS
- SOURCED: `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:14` (Gate 0c): "does the source have dated calls or trades we can score on BTC data? Score them first (B162 is the template). No record: hypothesis, never a core."
- SOURCED: `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:21`: "Fewer than 20 scorable calls means the layer stays a hypothesis under gate 0c, not a core."
- Final Verdict: **HYPOTHESIS**. The Malkan system cannot be backtested as an empirical replica of verified historical trader calls. It must proceed as a rule-based hypothesis test.

---

## 4. Sequence and Handoff to Downstream Cards

Per `HOME_FIT_AUDIT_MALKAN.md:106-110`:
1. **C1 `malkan-ledger-parity-feasibility` (this card)**: Completed. Verdict HYPOTHESIS, 0 dated calls, 6 RSI parity points cataloged.
2. **C2 `malkan-universe-data-power` (items 1, 4, 10; gates 0d, 0e)**: Next. Evaluates free public Indian EOD data sources, candidate universes (50, 100, 500 stocks), N per period and MDE with `power_mde.py`.
3. **C3 `malkan-prereg-dwm-equities` (items 6, 7, 8, 9, 11, 12; gates 0a, 0f)**: Pre-registration for D/W/M Indian equity home test as a HYPOTHESIS layer.
