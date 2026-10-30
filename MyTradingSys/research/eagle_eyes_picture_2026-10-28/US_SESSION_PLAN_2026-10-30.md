# US session map, 2026-10-30 (Eagle_Eyes, written 13:20Z)

Trigger: operator shot fb7b376f9328 (Bitstamp BTCUSD 30m, RSI + WT_CROSS_LB, 13:12Z) and his ask for scalp, quick and long-trade plans.
Scenario maps only: levels, what confirms and what kills each side, measured base rates. No entry, exit or size calls (role rule).
Data: Binance spot klines (data-api.binance.vision) and Bybit linear OI/funding, pulled 13:16Z; fapi.binance.com times out from JIS-NB.
Bitstamp printed 77,149 at 13:12Z while Binance spot read about 77,330 at 13:16Z (not the same minute, so the gap is not measured).
Levels are Binance spot. All thresholds and the level picks are OURS; base rates cite their study (descriptive, fee-free).

## Picture at 13:16Z (price 77,321)

| TF | RSI | WT1 / WT2 | BB %b | Read (OURS) |
|---|---|---|---|---|
| 5m | 41.5 | -52.7 / -48.5 | 0.18 | BandWidth in the lowest 9% of the last 300 5m bars (25 h): coiled on 5m only |
| 15m | 38.9 | -51.0 / -48.9 | 0.17 | down, at the WT -53 zone |
| 30m | 36.5 | -41.0 / -37.7 | 0.12 | down since the 08:00Z cross at -7 (the T7 zero rejection) |
| 1h | 34.8 | -44.9 / -41.9 | 0.27 | down |
| 4h | 33.2 | -38.1 / -29.7 | 0.01 | on the lower band; bar highs fall (78,804, 78,241, 77,608) but these are not confirmed pivots (see cross-check) |
| 1D | 34.2 | -51.1 / -41.5 | -0.13 | below the lower band (78,180), under the 10-29 low and close |
| 1W | 51.0 | 26.0 / 28.9 | 0.62 | crossed down 10-26 |

Agreement: 6 of 6 intraday-to-daily columns say down. The odd one: Bybit OI fell 67.9K to 65.5K (-3.6%) since 05:30Z while price fell 1.6%: positions closing, not new shorts. Accounts long-heavy (buy ratio 0.67 to 0.68, rising). Funding 0.01% (flat).

## Levels

| Above | Why | Below | Why |
|---|---|---|---|
| 77,528 / 77,608 | last 30m lower highs | 77,239-77,254 | today's double low, bottom of the pre-US box |
| 77,667 | day VWAP | 77,100 | 30m lower band |
| 77,866 | 11:00Z lower high | 77,000 | Krown 76-77k wick zone |
| 77,910 / 77,992 | 10-29 low / close (daily reclaim line) | 76,500 | today's low = 10-day low (S) |
| 78,019 | 30m BB mid | 76,200 | 1h lower band |
| 78,804 | today's high, top of the pre-US box | 76,022 | daily EMA200 |
| 79,155-79,220 | Jason's weekly minimum, last week's low | 75,000 | Michael / Krown major support |

## Base rates that apply now

| Situation | Study | n | What happened next |
|---|---|---|---|
| Pre-US box 05:30-13:30Z (78,804 / 77,239), 15m BandWidth middle | `pre_us_squeeze_2026-10-29` | 800 | 4h after the open: UP 25%, DOWN 29%, inside 47%; broke both sides 16%; US range median 1.26x box (about 1,970) |
| First break of the box holds to the 4h close | same | 800 | 51% (coin flip) |
| 30m WT reaches -53 and crosses up, 4h WT down (T2) | `wt30_sequence_2026-10-30` | 304 | up 4h 56%; -1% first 49% vs +1% first 42%: a pop, not a turn |
| 5m: short after a close below the mid touches the lower band | `bb_dance_2026-10-30` | 11,051 | close near the band (%b < 0.25): new low first ~60%; close at %b >= 0.25: ~30%; all exits under 0.2% gross vs 0.12% cost |
| OI down + price down (30m) | `oi_side_2026-10-30` | 6,296 | up 60 min 53.5%; -0.5% first 46.7% vs +0.5% 43.3%: small lean, below fees |
| 4h close below the 10-day low (76,500) | `lh_break_2026-10-30` | 44 | CORRECTED: the last 3 confirmed 4h pivots (81,823, 81,789, 81,971) do not fall, so a break now is a CONTROL break: 0.5 H reached 48%, 1 H 18%, back above S within 24 h 70%. H = highest 4h high of 10 days (84,898) - 76,500 = 8,398, so 0.5 H = 72,301 within 7 days |

## Scenario maps (no side marked more likely: the base rates are near even)

| Horizon | A: down | B: up | Kill / "I was wrong" |
|---|---|---|---|
| Scalp (1-5m) | 5m close below 77,239 with taker delta red and OI flat/up = shorts pressing; next 77,100, 77,000 | 5m close above 77,607 (5m upper band) with delta green and OI up; next 77,667 VWAP | A dies on a 5m close back above 77,438 (5m mid); B dies back below 77,438. The 5m coil says size, not side |
| Quick (15m-30m) | 30m close below 77,239, WT keeps falling to -53 without a cross: 77,000, then 76,500 | His setup: 30m close above the last lower high 77,866 with the 30m WT crossing up, before or at the open: VWAP held, then 78,019-78,289 | A dies on a 30m close back above 77,667 (VWAP); B dies on a 30m close back below 77,528 |
| Long (4h-1D) | 4h close below 76,500 (a control break by the study rule; 70% closed back above within 24 h): 76,022 daily EMA200, then 75,000 (Michael, Krown) | Daily close back above 77,992 (10-29 close) and 78,180 (daily lower band): back inside the band, 4h WT cross up | A dies on a daily close above 78,180; B dies on a 4h close below 76,500 |

Calendar: monthly (and Krown's 2-month) close is 10-31 24:00Z; Krown named a 2-month close below the 5 EMA at 77,500 as worrisome. Price is under it now. US DST ends 11-01, so today's cash open is 13:30Z.

## Yesterday's mistakes and the rule for today

| 10-29 mistake | Rule now |
|---|---|
| Marked side A "more likely" with no base rate (02:20Z map); B happened | Mark a side only with a measured base rate and its n; otherwise "no side" |
| Under-called the move size by about 650 | Size from a measured range multiple (US range 1.26x box) and ATR, never a guess |
| Two of my commits turned trunk CI red (lint; role-file paths) | No role-file edits in a live session; ship only research files |
| Essays instead of pointers in trade | Bullets only, max about 8 lines plus the grid |
| Two ledger rows left "pending" | Scored in SCENARIO_LEDGER.md the same day |
| Analyst levels quoted without age | CBP rows are 10-26/27 (CBP stalled after 10-28): quote the date |

## Shot fb7b376f9328: claims checked (Binance spot 30m, pulled 13:16Z)

Prior: MyTradingSys/research/wt30_sequence_2026-10-30/RESULT.md

| id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |
|---|---|---|---|
| c1 | MATCH | RSI just under 40 and falling | 30m RSI 36.5 (prev 38.4) |
| c2 | MATCH | WT about -40, green line under red, falling | wt1 -41.0, wt2 -37.7, prev wt1 -38.8 |
| c3 | MATCH | last WT cross down (red dot) around 08:00Z near 0 | cross down on the 08:00Z bar at wt1 -7.3 |
| c4 | MATCH | 10-30 low near 76.5k around 02:00Z | Binance spot low 76,500.11 in the 02:00Z bar |
| c5 | MATCH | bounce high about 78.6-78.8k mid-morning | 78,804.01 in the 06:30Z bar |
| c6 | NOT_IN_DATA | Bitstamp last 77,149 at 13:12Z | Binance spot 77,321 at 13:16Z; no same-minute Bitstamp data, gap not measured |

## Shot c2fdb0b39295: CoinGlass Legend, Binance perp 30m, liquidation heatmap + large trades (13:22Z)

Prior: MyTradingSys/research/eagle_eyes_picture_2026-10-28/US_SESSION_PLAN_2026-10-30.md

Heatmap bands are pixel reads (scale 7.92 USD/px from the 77,600 and 76,800 gridlines); MTS has no heatmap recorder, so this shot is the only record.

| id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |
|---|---|---|---|
| h1 | MATCH | 10-29 perp high 81,953.7 | lh_break_2026-10-30 / SCENARIO_LEDGER 10-29 row: 81,953.7 |
| h2 | MATCH | 10-30 perp low 76,444.0 | lh_break_2026-10-30/RESULT.md: perp low 76,444 |
| h3 | NOT_IN_DATA | brightest band 79.0-79.4k ends where the 10-29 23:30Z-10-30 00:00Z drop crossed it (band hit) | no heatmap history in MTS; spot 30m bars 23:30Z 78,880-77,910, 00:00Z 78,274-76,856 crossed it |
| h4 | NOT_IN_DATA | bands left now: below about 77,210 (dim), 77,040 (brighter), 76,510, 76,080; above about 78,700-78,880 (dim), 82,100-82,300 (bright) | pixel read only |
| h5 | NOT_IN_DATA | big green large-trade bubbles at the 81.9k top (10-29 ~19:00Z) and at about 77.7k in the 10-30 ~04:30Z drop; price went lower after both | large_trade_absorption_2026-10-30: buy-aggression n=1,155 up 60 min 47.4%; buy-absorbed (red bar) n=99 50.5% |
| h6 | NOT_IN_DATA | last bar O 77,435.0 C 77,384.7 at 13:22Z | fapi.binance.com times out from JIS-NB; spot 77,321 at 13:16Z |

## Shot 3d6e6faf1551: CoinGlass Legend, Binance perp 1D footprint + heatmap (13:23Z)

Prior: MyTradingSys/research/eagle_eyes_picture_2026-10-28/US_SESSION_PLAN_2026-10-30.md

| id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |
|---|---|---|---|
| d1 | MATCH | today's low 76,444.0 (perp) | lh_break_2026-10-30/RESULT.md: perp low 76,444 |
| d2 | MATCH | today's open 77,962.7 (perp), high 78,776.5 | Binance spot day: open 77,991.89, high 78,804.01 (spot runs about 30 above perp today) |
| d3 | NOT_IN_DATA | day delta -9.89K BTC on 10-29, -6.40K on 10-30 so far | fapi times out from JIS-NB; spot daily taker delta 10-29 -619, 10-30 -1,545 (spot only, different venue) |
| d4 | NOT_IN_DATA | today's biggest sell cells sit at about 77.4-77.5k and 76.9-77.1k; few green cells, only near 78.0k | pixel read; MTS footprint rolls exist in the live order-flow writer, not read here |
| d5 | NOT_IN_DATA | heatmap bands today: about 77,125 (just under price), 76,440 (at the low), 78,660 (above) | pixel read, 7.92 USD/px |

## Shot a25c204526aa: CoinGlass Legend, Binance perp 3m heatmap + large trades (13:25Z, 5 min before the US open)

Prior: MyTradingSys/research/eagle_eyes_picture_2026-10-28/US_SESSION_PLAN_2026-10-30.md

Pixel scale 3.37 USD/px (78,900 and 78,600 gridlines). Axis labels are IST (19:00 = 13:30Z).

| id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |
|---|---|---|---|
| m1 | MATCH | today's perp high 78,776.5 and low 76,444.0 | daily shot 3d6e6faf1551 and lh_break RESULT |
| m2 | MATCH | lower highs since 05:30Z (78.78k, 78.6k, 77.87k, 77.55k) on a 77.24-77.25k shelf tested 3 times | Binance spot 30m: highs 78,804 / 77,866 / 77,608 / 77,528; lows 77,239 (11:30Z), 77,254 (13:00Z) |
| m3 | NOT_IN_DATA | brightest bands: 76,570-76,640 below (built after the 76,444 low), 78,815-79,000 above | pixel read; no heatmap history in MTS |
| m4 | NOT_IN_DATA | a band at 77,020-77,085 brightening toward 13:25Z; price sits in a band at 77,240-77,310 | pixel read |
| m5 | NOT_IN_DATA | big buys at 78.5-78.6k (07:15-07:30Z) and big sells at the 78.7k top (05:45Z) and in the 77.5-77.6k lows; price fell after the big buys | large_trade_absorption_2026-10-30: buy-aggression n=1,155 up 60 min 47.4% |

Reading (OURS): the pre-US box bottom (77,239), the 3-test shelf and the nearest long-liquidation bands line up on the down side (77.05k, then 76.6k); the short-liquidation band 78.8-79.0k sits just above the box top (78,804). Heatmap bands as magnets are not measured (BACKTEST_CANDIDATES C6, 2 instances).

## Cross-check, 13:40Z (operator: "cross check everything")

Each claim of this session re-read against the study code or recomputed from Binance spot klines.

| Claim | Check | Verdict |
|---|---|---|
| Pre-US state "middle" (15m BandWidth) | Study rule: BW at 13:30Z ranked in the prior 30 days of 15m bars. Recomputed: rank 68.5% (n=2,880); my first number (42%) used 3 days. Still the middle bucket (20-80%) | number wrong, row right |
| Box 78,804 / 77,239, range 1,565, US range 1.26x = about 1,970 | Recomputed from 15m bars 05:30-13:30Z | MATCH |
| 4h "3 falling highs" | Study rule: confirmed pivots (2 bars each side). Last 3 pivots 81,823 / 81,789 / 81,971: not falling. My list used raw bar highs | WRONG, corrected above (control break, 0.5 H = 72,301) |
| Story B "big sells on a bar that holds: -0.5% first 54.7%" (13:30Z 5m) | That class (sell-absorbed) needs a GREEN bar. The 13:30Z 5m bar closed red (perp 77,250 to about 77,169, spot 77,284 to 77,249). If it was a large-sell bar it is sell-aggression: up 60 min 53.5%, +0.5% first 46.6% vs -0.5% 45.2% (n=1,168). Whether it passed the top-2% large-net cut is NOT_IN_DATA here | WRONG class, corrected |
| "OI down + price down" row applied to Bybit OI over 7.5 h | Study unit: 30-minute windows, Binance OI change >= 0.25%. Not the same measure | misapplied, dropped |
| "This is the 16% both-sides case" (13:35Z reply) | Both sides means the BOX (78,804 / 77,239). Only the low broke; 78,804 is untouched | WRONG, withdrawn |
| Bitstamp vs Binance gap "about 150" | 13:29Z: Bitstamp 77,160 (at 13:29:12) vs Binance 1m close 77,284: 124, not the same second | about 120-150 |
| Daily EMA200 76,022 | 300 daily bars, EMA seeded at the first close: about 5% seed weight left | approximate |
| Binance OI +390 BTC on the 13:32-13:33Z drop | CoinGlass shot only (fapi times out here); Bybit OI on the same minutes moved +45 then -99 | venue split, NOT_IN_DATA for Binance |
| 08:10 ledger row: -1% first? | -1% = 77,234 was crossed in the 13:30Z minute (spot low 77,129); +1% (78,794) never reached | scored in SCENARIO_LEDGER.md |

Mistake pattern: three of the five errors are one kind, quoting a study row without checking that today's reading meets the study's own definition (pivots, bar colour, measurement unit). Rule from now: before quoting a base rate, check the trigger against the study header.
