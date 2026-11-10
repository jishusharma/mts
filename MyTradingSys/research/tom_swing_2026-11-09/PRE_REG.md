# Pre-Registration: Tom Swing Trading Fee-Net Event Count on BTC 4h & 1d (2017–2026)

**Card:** `tom-swing-trendline-extract-1109`  
**Study ID:** `tom-swing-btc-4h-1d-count`  
**Analyst / Source:** Tom Vorwald, Video `M7ompiwv5co` ("The Easiest Way to Start Trading (Swing Trading for Beginners)", 2026-11-04)  
**Contract Baseline:** `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md` (v1.1)  
**Fee Baseline:** `MyTradingSys/backtest/fees.py` (Binance spot taker fee schedule)  
**Scope:** Specification and Pre-Registration only; **no backtest execution or live orders in this card**.

---

## Context

- **Regime:** Bull, Bear, and Range macro environments across BTC 2017–2026 (Binance spot era).
- **Phase:** Two distinct phases per Tom's framework: Phase 1 Range/Accumulation ("rubber band" sideways phase) vs Phase 2 Directional Trend (momentum breakout).
- **Session:** Higher-timeframe closed bars (`4h` and `1d` candle closes, UTC timestamped per `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md:17`); intraday session timing is none, because swing trades are evaluated purely on daily/4h closing prices and held for several days to 1–2 weeks.
- **Entry:** Breakout confirmation on a closed candle above the consolidation boundary / trendline, confirmed by volume expansion (volume > 20-period SMA volume), with minimum projected R:R $\ge 1.5$.

---

## 1. Parameters & Provenance

| # | Parameter | Value | Tag | Provenance / Source Citation |
|---|---|---|---|---|
| **P01** | Instrument & Venue | `BTCUSDT` spot on Binance (`2017-08-17` to `2026-11-08`) | **OURS** | Repo standard benchmark (`MyTradingSys/backtest/fees.py:12-14`, `MyTradingSys/research/monday_open_2026-11-09/ARGON_CHECK.md:5`). |
| **P02** | Timeframes | `4h` and `1d` | **SOURCED** (`1d`) + **OURS** (`4h`) | SOURCED: "wait for daily closing prices" (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:41`); 4h included as OURS sensitivity arm for swing structure. |
| **P03** | Holding Period | 3 to 14 days (several days up to 1–2 weeks) | **SOURCED** | "meaning trades held for several days, sometimes even one or two weeks" (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:38`). |
| **P04** | Bar Geometry | Closed bars only; evaluation on bar close | **SOURCED** | "wait for daily closing prices, we can trade much, much more patiently" (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:41`). |
| **P05** | Pivot Detection ($k$) | $k=3$ bars on each side for swing high / swing low | **OURS** | `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md:29` ($k=3$ primary; strictly higher lows / lower highs). |
| **P06** | Pivot Price Arm | Primary: Line chart closes (price_arm `close`); Sensitivity: Wicks (price_arm `wick`) | **SOURCED** (close) + **OURS** (wick) | SOURCED: "Let's just take this line chart here, yeah? And look at what kind of ideas it gives us." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:50`). |
| **P07** | Trendline Definition | Rising support through swing lows ($p_b > p_a$); falling resistance through swing highs ($p_b < p_a$) | **OURS** | `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md:43`. |
| **P08** | Consolidation Range / Sideways Base | Minimum 5 bars consolidation within boundary | **OURS** | Formalization of "rubber band" sideways accumulation phase. |
| **P09** | Entry Trigger | Breakout close beyond boundary / trendline | **SOURCED** | "Then, I have my boundary clearly marked here, and I have a breakout right here." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:53`). |
| **P10** | Volume Confirmation Gate | Breakout candle volume $>$ 20-bar SMA volume | **SOURCED** (concept) + **OURS** (threshold) | SOURCED: "Trading volumes that have increased here, so we know that the momentum is driven by liquidity." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:59`). Threshold 20-SMA volume is OURS. |
| **P11** | Stop Loss Level | Lowest swing low of the consolidation phase prior to breakout | **SOURCED** | "I would always place the risk below the last sideways phase at the latest" (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:62`). |
| **P12** | Profit Target (Primary: HVN) | Prior High-Volume Node (POC / HVN cluster) | **SOURCED** | "I'll define the next target where there was a lot of liquidity. Because the fact that the market will slow down there at first is simply a probability." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:68`). |
| **P13** | Profit Target (Secondary: Measured Move) | Projected distance $\alpha$ mirrored from consolidation base | **SOURCED** | "Alternatively, if we happen to be trading at all-time highs, we simply mirror the current momentum move to the upside to determine our next target." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:71`). |
| **P14** | Minimum Risk-Reward Ratio (RRR) | Projected $R:R \ge 1.5$ | **SOURCED** | "And only if that is, for example, at least greater than 1.5 or so, then I have a really great strategy that will make me money." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:77`). |
| **P15** | Sample Size Target | $\ge 200$ to $300$ candidate trades across full history | **SOURCED** | "I always say, you should have two or 300 trades." (`MyTradingSys/research/tom_swing_2026-11-09/extract_M7ompiwv5co.md:80`). |
| **P16** | Fee Schedule | Binance spot standard tier: 10 bps round-trip taker (5 bps per side) | **OURS** | `MyTradingSys/backtest/fees.py:12-14` (`BINANCE_TAKER = 0.0005`, 10 bps RT taker). |
| **P17** | Slippage Allowance | 2 bps round-trip slippage | **OURS** | `MyTradingSys/backtest/fees.py:61-62` (`SLIPPAGE_RT_S13 = 0.0002`). |

---

## 2. Fee-Net Accounting Framework

In intraday scalping (e.g. 5m / 1m Tom order-flow tests in `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/AUDIT_AND_COURSE_CORRECTION.md:14`), a 10 bps round-trip fee on an 8 bps stop represented a devastating drag of **$2.76\text{ R}$ per trade**, making net profitability mathematically impossible.

In Tom's swing trading framework:
1. **Stop Width:** On BTC `4h` and `1d` charts, the consolidation base stop width typically spans **$3.0\%$ to $8.0\%$ ($300\text{ to }800\text{ bps}$)**.
2. **Fee Drag as Fraction of R:**
   $$\text{Fee Drag (R)} = \frac{\text{Round-Trip Fee} + \text{Slippage}}{\text{Stop Distance}} = \frac{10\text{ bps} + 2\text{ bps}}{300\text{ bps} \dots 800\text{ bps}} = 0.015\text{ R to } 0.040\text{ R}$$
3. **Net Edge Viability:** With fee drag below $0.04\text{ R}$ per trade (less than $4\%$ of risk), a gross edge meeting Tom's target $R:R \ge 1.5$ with win rate $50\%\dots60\%$ easily survives exchange friction.

---

## 3. Cell Matrix & Power Calculations

| Cell ID | Timeframe | Price Arm | Target Model | Window | Target Sample Size ($n$) | Required MDE ($\alpha=0.05, \beta=0.20$) |
|---|---|---|---|---|---|---|
| `CELL-4H-CLOSE-HVN` | 4h | Close (line) | Prior HVN / Liquidity | 2017–2026 | $\ge 200$ | $\le 0.20\text{ SD}$ |
| `CELL-4H-CLOSE-MM` | 4h | Close (line) | Measured Move ($\alpha$) | 2017–2026 | $\ge 200$ | $\le 0.20\text{ SD}$ |
| `CELL-1D-CLOSE-HVN` | 1d | Close (line) | Prior HVN / Liquidity | 2017–2026 | $\ge 100$ | $\le 0.28\text{ SD}$ |
| `CELL-1D-CLOSE-MM` | 1d | Close (line) | Measured Move ($\alpha$) | 2017–2026 | $\ge 100$ | $\le 0.28\text{ SD}$ |

---

## 4. Execution Prerequisites (FIX-FIRST Gaps)

This pre-registration cannot proceed to execution until the following code fixes are verified in `trendline_core.py`:
1. **Fix Gap 1 (`price_arm="close"`):** Patch `_penetration_ok` and `_advance` in `trendline_core.py` to evaluate `bar["c"]` instead of wicks when `price_arm == "close"`.
2. **Fix Gap 2 (Pre-availability replay):** Ensure state transitions only count strictly after anchor availability ($j > ib + k$).
3. **Fix Gap 3 (Anchor poisoning):** Narrow `_broken_anchor` so inner line breaks do not void outer macro swing lines.
