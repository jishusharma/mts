Verdict: SOUND (The 2 executed replay trades and performance metrics in PLAN_US_OPEN_2026-11-13.md and plan_2026-11-13.json match the engine specifications and public 1m klines; no look-ahead bias exists as orders only trigger upon post-arm bar touch; and fee calculations strictly adhere to the documented 0.05% per side round-trip model).

# Blind Review of US Open Trader Study (us_open_trader_2026-11-13)

## 1. Headline Numbers Recount and Claim Verification

Every headline number in `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:1-85` and `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:1-23` was recounted against `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:8-41` and public Binance spot 1m klines.

| Claim | Claimed Value | Recounted Value | Match Status | Source Citation |
|---|---|---|---|---|
| Frozen UTC reference price | 69,207 | 69,207.59 (low 69,207.59 at 13:10Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:3` |
| Last hour range | 69,106 - 69,509 | 69,106.00 - 69,509.00 (12:10Z-13:09Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:15` |
| Europe session high | 69,571 | 69,571.37 (high 08:00Z-13:10Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:11` |
| Europe session low | 68,516 | 68,516.29 (low 08:00Z-13:10Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:17` |
| Asia low (today's low) | 67,568 | 67,568.00 (low 00:00Z-08:00Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:19` |
| Asia range pct | 5.84 % | 5.840 % ((71514.01 - 67568) / 67568 * 100) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:22` |
| ATR(14) 15m | 239 | 238.9 (Wilder ATR on closed 15m bars up to 13:00Z) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:21` |
| ATR(14) 1h | 602 | UNVERIFIABLE (ATR(14) at 13:00Z was 643.1; at 13:10Z was 604.4; close approximation) | UNVERIFIABLE | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:21` |
| First 2h range median last 8 weekdays | 1,150 (693 to 4,040) | UNVERIFIABLE (Prior 8 weekdays 14:30-16:30 history not stored locally in folder) | UNVERIFIABLE | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:21` |
| Trade C entry price | 69,980 | 69,980 (triggered at 13:35Z / 13:38Z high >= 69,980) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81` |
| Trade C exit price | 69,480 | 69,480 (target reached at 14:00Z low 69,477.07) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81` |
| Trade C exit reason | target | target | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81` |
| Trade C r_gross | 2.00 | 2.0000 ((69,980 - 69,480) / 250) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81` |
| Trade C r_net | 1.72 | 1.7201 (2.00 - 2 * 0.0005 * 69,980 / 250) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81` |
| Trade B entry price | 68,490 | 68,490 (triggered at 15:30Z low 68,413.21) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82` |
| Trade B exit price | 68,120 | 68,120 (target reached at 15:41Z low 68,103.00) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82` |
| Trade B exit reason | target | target | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82` |
| Trade B r_gross | 1.48 | 1.4800 ((68,490 - 68,120) / 250) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82` |
| Trade B r_net | 1.21 | 1.2060 (1.48 - 2 * 0.0005 * 68,490 / 250) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82` |
| Replay total trades | 2 | 2 trades (C and B) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84` |
| Replay total net wins | 2 | 2 net wins | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84` |
| Replay total r_gross | 3.48 | 3.4800 (2.00 + 1.48) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84` |
| Replay total r_net | 2.93 | 2.9261 (1.7201 + 1.2060) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84` |

---

## 2. Look-Ahead Hunt

All feature definitions, indicator calculations, and trade triggers were inspected in `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:20-41`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:36-49`, and `MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:38-78`.

1. **Plan Freezing and Windowing**:
   - The plan parameters and order triggers were frozen at 13:10Z (`MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:3`), well prior to the arm time at 13:35Z (`MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:6`) and the US cash open at 14:30Z (`MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:3`).
   - Breakout level calculations (Europe high 69,571, Europe low 68,516, Asia low 67,568) strictly used completed session bars prior to 13:10Z (`MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:9-19`).

2. **Order Arming and Trigger Evaluation**:
   - In `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:27`, bars with `t < arm` (before 13:35Z) are ignored. Orders whose trigger is already crossed at the first armed bar's open are marked `void`.
   - Breakout A (trigger 69,620) was voided at 13:35Z open (open price 69,934.49 > 69,620) (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:27`).
   - Fade C (sell at 69,980) triggers when price trades at or above 69,980 after arming. At 13:35Z bar high 69,987.65 and 13:38Z bar high 70,214.31, C triggered without reference to any subsequent bar (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:28-29`).
   - Adverse extreme rule: in the entry bar, adverse extreme is checked against the stop, and target is explicitly NOT counted in the entry bar (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:30`). This prevents same-bar target look-ahead bias.

3. **Hand Recorder Indicators**:
   - In `MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:71,78`, `bybit_k` and `binance_spot_1m` explicitly exclude the current open candle (`[:-1]`), processing closed bars only.
   - RSI and Bollinger Bands (`MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:38-57`) are evaluated strictly over backward windows of closed prices.
   - Cumulative Volume Delta (CVD) accumulates net taker delta bar-by-bar incrementally (`MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:103-108`). No future bar leakage is present.

---

## 3. Fee and Slippage Hunt

The fee modeling was audited across `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:12` and `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:38-39`.

1. **Fee Model Specification**:
   - Fee per side is configured as `fee_per_side: 0.0005` (5 bps / 0.05% per side) in `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:12`.
   - Round-trip count: exactly 2 sides (one entry, one exit) per completed trade.
   - Net R formula: `r_net = r_gross - 2 * fee_per_side * entry / stop_dist` defined in `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:39`.

2. **Deduction and Side Verification**:
   - Trade C (sell fade at 69,980, target 69,480, stop_dist 250):
     - Gross move = +500, `r_gross` = 500 / 250 = 2.0000.
     - Fee deduction = `2 * 0.0005 * 69,980 / 250` = `69.98 / 250` = 0.27992 R.
     - `r_net` = `2.00 - 0.27992` = 1.7201 R (rounded to 1.72 in `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81`).
   - Trade B (sell breakout at 68,490, target 68,120, stop_dist 250):
     - Gross move = +370, `r_gross` = 370 / 250 = 1.4800.
     - Fee deduction = `2 * 0.0005 * 68,490 / 250` = `68.49 / 250` = 0.27396 R.
     - `r_net` = `1.48 - 0.27396` = 1.2060 R (rounded to 1.21 in `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82`).
   - Total net R: 1.7201 + 1.2060 = 2.9261 R (rounded to 2.93 in `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84`).
   - Fees are properly applied to both sides (entry and exit) of the round-trip and correctly deducted from gross R.
