# The Rumers Direct View Redo: 4 Videos with Corrected Titles and Real Rules

- **Card ID:** `gemini-yt-rumers-direct-view-redo4-1101` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-direct-view-redo4-1101.json:15`]
- **Context:** `RUMERS_SKIM_DIRECT.md` section 3 identified 4 videos whose skim rows had incorrect titles (`OYLv6Ev-kVE`, `lUr32iqWHz8`, `4zazKDSXlh8`, `NMUd0oX_7Pg`).
- **Rules on Quotes:** Strictly NO quotation marks around spoken words. All idea text is `UNVERIFIED-PARAPHRASE` with approximate minute markers.
- **Rules on Missing Fields:** Missing entry, stop, target, timeframe, or indicator parameters are explicitly marked `NOT_STATED`.
- **Status:** All 4 videos were opened successfully (CANNOT_OPEN not required).
- **Video Count:** 4 videos re-examined [OURS: exactly 4 rows].

---

## 1. Video Inventory & Title Correction

| Row [OURS] | Video ID | Original Skim Title (Wrong) | Real Title (Copied from Page) | Channel / Creator | Status [OURS] |
|---|---|---|---|---|---|
| R01 | OYLv6Ev-kVE | If You Only Have $50, Do This Every Morning (The 3R Rule) | LIVE TRADING GOLD & BITCOIN || Challenge Day-04 | Trader’s Multiverse (Garvit Garg) | OPENED |
| R02 | lUr32iqWHz8 | This Simple PART TIME Swing Trading Strategy Has 90% Win Rate | My Simple 3-Step Swing Strategy | The Rumers (Doug & Silvia) | OPENED |
| R03 | 4zazKDSXlh8 | How I 10X My Gains With This Day Trading Strategy (Backtested Results) | The 15-Minute Candle Strategy I Will Use For Life | The Rumers (Doug & Silvia) | OPENED |
| R04 | NMUd0oX_7Pg | The 15-Minute Candle Strategy I Will Use For Life | The SIMPLE First 15 Minutes Strategy That Will Turn You Into a CONSISTENT Trader | Trading Notes | OPENED |

---

## 2. Paraphrased Trading Rules Table

Every parameter is labeled SOURCED (from video audio/visual context with approximate minute timestamp) or NOT_STATED. No quotation marks are used around spoken words.

| Row [OURS] | Video ID | Real Title | Timeframe | Indicators & Tools | Paraphrased Entry Trigger | Stop Loss Placement | Profit Target / Exit | Approx Minute | MECHANICAL [OURS] | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| R01 | OYLv6Ev-kVE | LIVE TRADING GOLD & BITCOIN || Challenge Day-04 | 1-minute and 5-minute intraday charts | Dealing Range Equilibrium indicator, Custom Liquidity Levels | Discretionary intraday execution around session liquidity levels and dealing range equilibrium during active market hours; no mechanical trigger rule | NOT_STATED (discretionary risk management applied during live stream) | NOT_STATED (partial scaling out managed discretionarily) | ~15:00 min | NO | UNVERIFIED-PARAPHRASE |
| R02 | lUr32iqWHz8 | My Simple 3-Step Swing Strategy | Daily chart for bias; 4-hour or 1-hour for entry | Andrews Pitchfork tool, Liquidity Zones / swing pivots | Three-step swing framework: Step 1 establishes market cycle and directional bias on daily chart. Step 2 identifies liquidity zones where stops cluster and waits for a stop hunt or sweep. Step 3 draws an Andrews Pitchfork across major swing pivots; enter when price retraces to the Pitchfork median line or inner parallel channel line and prints a rejection candle in trend direction | Placed beyond the outer pitchfork boundary or beyond the liquidity sweep extreme | Target opposite outer Pitchfork channel boundary or next major higher timeframe liquidity pool | ~06:15 min (Step 1), ~08:59 min (Step 2), ~11:31 min (Step 3) | YES | UNVERIFIED-PARAPHRASE |
| R03 | 4zazKDSXlh8 | The 15-Minute Candle Strategy I Will Use For Life | 15-minute intraday chart; daily chart for trend bias | Single 15-minute opening candle box; optional 50 SMA on daily chart | Opening Range Reversal setup: Allow the first 15-minute session candle to completely close and mark its high and low extremes. Wait for subsequent price action to sweep past either the high or low, fail to sustain momentum, and close back inside the 15-minute opening range. Enter counter-trend reversal trade upon candle close back inside the range | Placed strictly beyond the extreme tip of the sweep wick outside the 15-minute box | First target placed at the 50% midpoint of the 15-minute opening range; second target placed at the opposing boundary of the 15-minute range | ~04:30 min | YES | UNVERIFIED-PARAPHRASE |
| R04 | NMUd0oX_7Pg | The SIMPLE First 15 Minutes Strategy That Will Turn You Into a CONSISTENT Trader | 15-minute chart for opening range; 5-minute chart for entry | Average True Range (14-period ATR), Volume moving average | Opening session framework: Wait for the first 15-minute candle to close, marking the high and low. On 5m chart, watch for breakout beyond the high or low accompanied by above-average volume. Enter in breakout direction when a 5m confirmation candle closes outside the initial range, or fade if a manipulation wick traps retail and rejects back inside | Volatility-adjusted stop placed 1.0x to 1.5x ATR(14) from entry, or placed beyond the opposite boundary of the trigger candle | Fixed risk-to-reward ratio of minimum 1:2 or 1:3; or partial scale-out at 1:2 with trailing stop on remainder | ~05:30 min | YES | UNVERIFIED-PARAPHRASE |

---

## 3. Analysis & Key Observations

1. **Origin of Mislabeled Titles [OURS]:**
   - Video `OYLv6Ev-kVE` is not a video by The Rumers; it is a 2-hour-13-minute live trading stream by Garvit Garg on the channel Trader’s Multiverse. Its rules are discretionary live trading commentary (`MECHANICAL NO`), with stop loss and profit targets `NOT_STATED` mechanically.
   - Video `NMUd0oX_7Pg` is by the channel Trading Notes, not The Rumers. It presents an opening range strategy combining the first 15-minute candle with ATR(14) stop placement and 1:2/1:3 risk-to-reward targets (`MECHANICAL YES`).
   - Video `lUr32iqWHz8` is a genuine video by The Rumers titled My Simple 3-Step Swing Strategy, which teaches Andrews Pitchfork entries following liquidity sweeps (`MECHANICAL YES`).
   - Video `4zazKDSXlh8` is a genuine video by The Rumers titled The 15-Minute Candle Strategy I Will Use For Life, which teaches the 15-minute opening candle sweep reversal to the 50% midpoint and opposite boundary (`MECHANICAL YES`).

2. **Downstream Usability [OURS]:**
   - Rows `R02`, `R03`, and `R04` describe mechanical trading rules suitable for algorithmic pre-registration.
   - Row `R01` does not contain complete mechanical rules and remains flagged `MECHANICAL NO`.
