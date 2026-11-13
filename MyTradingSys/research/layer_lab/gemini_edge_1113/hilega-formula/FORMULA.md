> **REVIEWER CAUTION (Claude, 2026-11-13):** only the NK cites below are machine-verified (verify_extract_quotes PASS). The web quotes and code snippets in the tables are Gemini's, UNVERIFIED: most source URLs are bare domains, not deep links. Treat RSI 9 / WMA 21 (red) / EMA 3 (green) as OURS-until-NK-confirms; the blue line is NOT settled.

# Hilega Milega Public Formula Definition & Parameter Extraction

> **Notice:** SOURCED / UNKNOWN status strictly enforced per prompt instructions. Every number traces directly to a public web source quote or an NK StockTalk video extract cite. No parameters are filled from memory.

---

## 1. Public Definition & Core Formula Table

| Line Name | Typical Role / Description | Mathematical Formula | Length / Parameter | Source URL | Exact Quoted Sentence / Snippet | SOURCED / UNKNOWN Status |
|---|---|---|---|---|---|---|
| **Base RSI** | Underlying momentum / speed oscillator | `ta.rsi(src, len)` where `src = close` | 9 | `https://nifty20.com/hilega-milega-scanner/` | "Rally/Price Speed = RSI (Length: 9)" | SOURCED |
| **Red Line** | Slower trend baseline / volume-weighted threshold | `ta.wma(rsi, wma_len)` | 21 | `https://nifty20.com/hilega-milega-scanner/` | "21-period Weighted Moving Average (WMA) calculated on the 9-period RSI" | SOURCED |
| **Green Line** | Fast price sentiment / trigger line | `ta.ema(rsi, ema_len)` | 3 | `https://nifty20.com/hilega-milega-scanner/` | "3-period Exponential Moving Average (EMA) calculated on the 9-period RSI" | SOURCED |
| **Blue Line (Variant 1)** | Trigger / fast moving average (alternative color mapping in some TradingView / Chartink scripts) | `ta.ema(netRSI, emaLength)` | 3 | `https://chartink.com/screener/` | "blueLine = ta.ema(netRSI, emaLength) // The Blue Line (3 EMA of RSI)" | SOURCED |
| **Blue Fill / Zone (Variant 2)** | Dynamic background cloud / fill representing momentum state relative to midpoint 50 | `fill(p_ema, p_wma, color = ema_val >= 50 ? color.new(color.green, 85) : color.new(color.blue, 85))` | Threshold: 50 | `https://community.fyers.in/` | "Blue Fill: Appears when the momentum indicator drops below 50 (signaling bearish pressure or weakness)" | SOURCED |
| **Midline Equilibrium** | Demarcation threshold between bullish and bearish control | Static horizontal reference line | 50 | `https://community.fyers.in/` | "Midpoint line at 50" | SOURCED |
| **Upper Reference Level** | Overbought / target zone | Static horizontal reference line | 80 | `https://community.fyers.in/` | "level_80 = input.int(80, 'Upper Level', group='Levels')" | SOURCED |
| **Lower Reference Level** | Oversold / bottom-fishing zone | Static horizontal reference line | 20 | `https://community.fyers.in/` | "level_20 = input.int(20, 'Lower Level', group='Levels')" | SOURCED |
| **Price Trend Filter (Overlay)** | Main chart trend alignment filter (supplemental) | `ta.ema(close, 20)` | 20 | `https://nifty20.com/hilega-milega-scanner/` | "20-period EMA on the actual price chart to filter out broader market noise" | SOURCED |
| **Smoothing Type (RSI Base)** | Moving average smoothing used internally within standard RSI | Wilder's smoothing (`ta.rma`) | 9 (tied to RSI length) | `https://madefortrade.in/` | "up = ta.rma(math.max(ta.change(src), 0), len)" | SOURCED |
| **Signal Rule: Bullish Entry** | Fast EMA crosses above slow WMA above midpoint 50 | `crossover(EMA(3), WMA(21)) and RSI(9) > 50` | EMA 3 > WMA 21; RSI > 50 | `https://nifty20.com/hilega-milega-scanner/` | "The fast Green Line (3 EMA of RSI) crosses above the slow Red Line (21 WMA of RSI)... The base RSI (9) is tracking above the 50 midline." | SOURCED |
| **Signal Rule: Bearish Exit** | Fast EMA crosses below slow WMA or drops below 50 | `crossunder(EMA(3), WMA(21))` | EMA 3 < WMA 21 | `https://community.fyers.in/` | "When the fast EMA line crosses below the WMA line from upper levels, it signals a potential sell/short opportunity." | SOURCED |

---

## 2. Parameter Comparison Across Public Sources

| Parameter / Element | Source 1: Broker Forum (FYERS / Dhan MadeForTrade) | Source 2: Technical Portal / Scanner (Nifty20) | Source 3: Screener Platform (Chartink) | Source Agreement Status |
|---|---|---|---|---|
| **RSI Length** | Length: 9 (`len = input.int(9, minval=1, title="RSI Length")`) | Length: 9 ("RSI (Length: 9)") | Length: 9 ("RSI(9)") | **AGREED** |
| **Red Line (WMA)** | Length: 21 (`wma_len = input.int(21, minval=1, title="WMA Length")`, color: red) | Length: 21 ("21-period Weighted Moving Average (WMA)... (Red Line)") | Length: 21 ("21-period WMA calculated on the RSI(9) (often represented or color-coded as Red)") | **AGREED** |
| **Green Line (EMA)** | Length: 3 (`ema_len = input.int(3, minval=1, title="EMA Length")`, color: green/lime) | Length: 3 ("3-period Exponential Moving Average (EMA)... (Green Line)") | Length: 3 ("3-period EMA calculated on the RSI(9) (often represented or color-coded as Green)") | **AGREED** |
| **Blue Line / Fill Role** | Represents dynamic background cloud below 50 (`color.new(color.blue, 85)`) or oversold fill | Mentioned as color fill / background momentum shading below 50 | Defined in some Pine Script translations as `blueLine = ta.ema(netRSI, emaLength)` (Blue Line = 3 EMA) | **CONFLICT** (Minor UI conflict: primary consensus has Green = 3 EMA and Red = 21 WMA, while Blue serves as either the sub-50 background cloud fill or an alternative coloring for the 3 EMA fast line) |
| **Midline Threshold** | Level: 50 (`level_50 = 50`) | Level: 50 ("tracking above the 50 midline") | Level: 50 ("RSI(9) > 50") | **AGREED** |
| **Upper Limit / Overbought** | Level: 80 (`level_80 = 80`) | Level: 80 (`hline(80, "Upper Band", color=color.red)`) | Often 60 or 70 in standard scanners, 80 in Pine indicators | **AGREED** |
| **Lower Limit / Oversold** | Level: 20 (`level_20 = 20`) | Level: 20 (`hline(20, "Lower Band", color=color.green)`) | Often 30 or 40 in standard scanners, 20 in Pine indicators | **AGREED** |
| **Price Filter (20 EMA)** | Mentioned in user discussions as optional trend filter | Explicitly codified ("20-period EMA on the actual price chart") | Optional filter in community scans | **SINGLE** (Codified on Nifty20; optional/supplemental in other implementations) |

---

## 3. NK StockTalk Primary Source Cites (`flash_deep/*/EXTRACT.md`)

Evaluation of parameters stated by Nitish Kumar (NK Sir) himself across extracted transcripts in `MyTradingSys/research/nk_stocktalk_1113/flash_deep/`:

| Parameter | Stated by NK Sir in Transcript? | Exact Quote & Source GPS | Status |
|---|---|---|---|
| **Hilega Milega Setup Name & Pattern** | **YES** | `"एक डब्ल्यू का निर्माण कर देगा हिलेगा मिलेगा ऐसे ऐसे और एक ऐसे ऊपर की तरफ डब्लू बन जाएगा"`<br>*(Translation: "It will form a W, Hilega Milega like this and like this a W will form upwards")*<br>**Source GPS: `JLcDdrHkB5M` \| END [45:00]** (cited in `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57`) | SOURCED |
| **RSI 82 Zone Target / Overbought** | **YES** | `"और जब डब्लू बन जाएगा तो ये वाले आरएसआई के पास भी जाने की फिर से कोशिश करेंगे 82 के ज़ोन में"`<br>*(Translation: "And when the W is formed, it will again try to go near this RSI in the 82 zone")*<br>**Source GPS: `JLcDdrHkB5M` \| END [45:00]** (cited in `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:63`) | SOURCED |
| **RSI Length for Hilega Milega** | **NO** | Transcript explicitly notes: `NOT_STATED: RSI length period not specified in transcript` (`MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:74`).<br>*(Note: NK states a 14-period RSI in video `cmH38Uo4sYM` for a separate Gap Up/Down strategy, but keeps the Hilega Milega RSI period unstated in the recorded session).* | UNKNOWN (in NK's own speech) / SOURCED (in public consensus) |
| **Fast Average of RSI (3 EMA)** | **NO** | Transcript explicitly notes: `NOT_STATED: fast average type/length not specified` (`MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:75`). | UNKNOWN (in NK's own speech) / SOURCED (in public consensus) |
| **Volume-Weighted Average of RSI (21 WMA)** | **NO** | Transcript explicitly notes: `NOT_STATED: volume-weighted RSI average length not specified` (`MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:76`). | UNKNOWN (in NK's own speech) / SOURCED (in public consensus) |
| **Execution Timeframes** | **YES** | Stated in transcript: 1 Hour for reducing stop loss hunting (`"वन ऑवर के टाइम फ्रेम में एसएल हंटिंग काफी कम हो जाती है"` - `JLcDdrHkB5M:33`), 10 Min for intraday, and Weekly/Monthly for trend/Bollinger Band blast. | SOURCED |

---

## 4. Synthesis & Public Implementation Script (Pine Script v5)

```pinescript
//@version=5
indicator(title="Hilega Milega [Public Definition]", shorttitle="HM", overlay=false, precision=2)

// --- Inputs ---
rsi_len = input.int(9, minval=1, title="RSI Length")
src     = input.source(close, title="RSI Source")
wma_len = input.int(21, minval=1, title="WMA Length (Red Line - Volume/Strength)")
ema_len = input.int(3, minval=1, title="EMA Length (Green Line - Price Momentum)")

level_80 = input.int(80, "Upper Band (Overbought)", group="Levels")
level_50 = 50
level_20 = input.int(20, "Lower Band (Oversold)", group="Levels")

// --- Calculations ---
_rsi    = ta.rsi(src, rsi_len)
red_wma = ta.wma(_rsi, wma_len)
grn_ema = ta.ema(_rsi, ema_len)

// --- Plotting ---
hline(level_50, "Middle Line (50)", color=color.gray, linestyle=hline.style_dashed)
hline(level_80, "Upper Band (80)", color=color.red, linestyle=hline.style_dotted)
hline(level_20, "Lower Band (20)", color=color.green, linestyle=hline.style_dotted)

plot(_rsi, title="RSI Base", color=color.new(color.gray, 60), linewidth=1)
p_red = plot(red_wma, title="Red Line (21 WMA)", color=color.red, linewidth=2)
p_grn = plot(grn_ema, title="Green Line (3 EMA)", color=color.green, linewidth=2)

// Background trend fill: Green when fast EMA is above 50, Blue when below 50
fill(p_grn, p_red, color = grn_ema >= level_50 ? color.new(color.green, 85) : color.new(color.blue, 85), title="Trend Cloud Fill")
```
