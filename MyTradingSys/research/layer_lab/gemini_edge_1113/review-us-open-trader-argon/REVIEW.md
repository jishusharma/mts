VERDICT: UNVERIFIABLE (arithmetic and rules are SOUND; live/replay kline data is not in the folder)

# Blind Review: `us_open_trader_2026-11-13` (Argon Twin)

Reviewed files in `MyTradingSys/research/us_open_trader_2026-11-13/`:
- `DESIGN.md`
- `PLAN_US_OPEN_2026-11-13.md`
- `plan_2026-11-13.json`
- `record_now.py`

## 1. Headline Number Recount

| Claim | Claimed Value | Recounted Value | Status | Source |
|---|---|---|---|---|
| `day` / `frozen_utc` / `arm_utc` / `flat_utc` | `2026-11-13` / `13:10Z` / `13:35` / `16:30` | `2026-11-13` / `2026-11-13T13:10Z` / `13:35` / `16:30` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:2-7`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:1,3,40` |
| `max_entries` / `amount_usd` / `fee_per_side` | `3` / `5,000 USD` / `0.05 %` | `3` / `5000` / `0.0005` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:8-12`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:24,41,84` |
| Order A (long breakout) entry / stop / target | `69,620` / `69,370 (-250)` / `69,980 (+360)` | `69620` / `69620-250=69370` / `69620+360=69980` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:14`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:28` |
| Order A risk / reward USD | `18 USD` / `26 USD` | `5000*250/69620 = 17.95` / `5000*360/69620 = 25.85` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:28` |
| Order B (short breakout) entry / stop / target | `68,490` / `68,740 (+250)` / `68,120 (-370)` | `68490` / `68490+250=68740` / `68490-370=68120` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:16`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:29` |
| Order B risk / reward USD | `18 USD` / `27 USD` | `5000*250/68490 = 18.25` / `5000*370/68490 = 27.01` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:29` |
| Order C (short fade) entry / stop / target | `69,980` / `70,230 (+250)` / `69,480 (-500)` | `69980` / `69980+250=70230` / `69980-500=69480` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:18`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:30` |
| Order C risk / reward USD | `18 USD` / `36 USD` | `5000*250/69980 = 17.86` / `5000*500/69980 = 35.72` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:30` |
| Order D (long fade) entry / stop / target | `68,120` / `67,870 (-250)` / `68,620 (+500)` | `68120` / `68120-250=67870` / `68120+500=68620` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:20`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:31` |
| Order D risk / reward USD | `18 USD` / `36 USD` | `5000*250/68120 = 18.35` / `5000*500/68120 = 36.70` | MATCH (reward rounds to 37) | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:31` |
| Stop % of price | `0.36 %` | `250 / 69207 = 0.3612%` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:33` |
| Replay Trade C `r_gross` / `r_net` | `2.00` / `1.72` | `500/250 = 2.00` / `2.00 - 2*0.0005*69980/250 = 1.72008` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:81`, `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:39` |
| Replay Trade B `r_gross` / `r_net` | `1.48` / `1.21` | `370/250 = 1.48` / `1.48 - 2*0.0005*68490/250 = 1.20604` | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:82`, `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:39` |
| Replay Totals `r_gross` / `r_net` | `3.48` / `2.93` | `2.00+1.48 = 3.48` / `1.72008+1.20604 = 2.92612` (`1.72+1.21=2.93`) | MATCH | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84` |
| Replay fills (C, B triggered on 1m klines) | 2 trades, 2 net wins | No 1m kline data in folder | UNVERIFIABLE | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:77-85` |
| Market levels & ATRs (`69,207`, `ATR15=239`, `ATR1h=602`, `5.84%`, etc.) | Listed in Levels table | No kline/session data in folder | UNVERIFIABLE | `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:9-22` |

## 2. Look-Ahead Hunt

No look-ahead found in the code or engine specification:
- `MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:71` (`bybit_k`): `rows = sorted(rows["result"]["list"], key=lambda x: int(x[0]))[:-1]` explicitly drops the in-progress bar, using only closed bars.
- `MyTradingSys/research/us_open_trader_2026-11-13/record_now.py:78` (`binance_spot_1m`): `for x in rows[:-1]` explicitly drops the in-progress 1m bar, using only closed bars.
- `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:27-36` (`engine.py` rules):
  - Bars with `t < arm` are ignored (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:27`).
  - On the entry bar, only stop is checked; target is NOT counted on the entry bar (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:30`).
  - `move_stop` becomes effective from the **next** bar (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:33`).
  - `V2-3` fade arming (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:142-145`): fade arms from the bar **after** its `arm_after` order closed/cancelled/void.
  - `V2-4` (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:148`): runner steps the engine only on closed 1m klines.

## 3. Fee and Slippage Hunt

- **Fee model**: `fee_per_side = 0.0005` (0.05% / 5 bps per side) (`MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json:12`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:84`).
- **Round-trip count**: 2 sides (entry + exit = 10 bps), computed as `2 * fee_per_side * entry / stop_dist` (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:39`).
  - Minor note: using `entry` for both sides instead of `entry + exit` differs by `< 0.002 R` on a 500-pt target at 69,980.
- **Slippage**: Replay assumes zero slippage (fills at exact `trigger`, `MyTradingSys/research/us_open_trader_2026-11-13/PLAN_US_OPEN_2026-11-13.md:85`, `MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:28`). Live/V2-2 uses actual average fill price and enforces a slippage guard of `0.25 * stop_dist` (`MyTradingSys/research/us_open_trader_2026-11-13/DESIGN.md:134-138`).
