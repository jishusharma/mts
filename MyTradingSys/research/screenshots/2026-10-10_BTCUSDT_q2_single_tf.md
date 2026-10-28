# 2026-10-10 BTCUSDT screenshots, three single-TF context shots (relay Q2)

Shots: 65656faa31ba, 359bdb0c7cf9, 23416389787e
Operator words: 65656faa31ba "Yesterday, why MTS was not able to signal the shrot after the US session open? Was it prepared for it During or before the session start? ..." (full text: `shot.py show 65656faa31ba`); 359bdb0c7cf9 and 23416389787e: image only (why recorded at classify)
Clocks: both charts are the CoinGlass tv page = UTC. 23416389787e is the Claude App (no market clock).
Pre-read (VVP-002 F.1): 65656faa31ba pass (30m label, OHLC header, VWAP legend, OI / CVD / net delta panels, countdown 05:01 on the live bar); 359bdb0c7cf9 pass (15m label, OHLC header, VWAP legend, OI / CVD / net delta, countdown 04:11); 23416389787e n/a (app screen)
Operator marks: none drawn on either chart. Both show the CoinGlass volume-profile boxes (one per session block) with a red horizontal at each box's developing POC; pixel reads below are +-10 points
Set timeframes present: 30m (65656faa31ba) and 15m (359bdb0c7cf9), two different days   missing: 1h, 4h, 5m   (single timeframe per day: context, not a set read; classify checks already hold: kinds chart, chart, app)

## Carried context
Prior: none
(No earlier extract covers 2026-10-07 09:24 or 2026-10-09 13:41; the 10-09 5m/1m reads 850745dc9d8d and 90e55256ec34 are 14:15 and 14:23 shots of a different TF, not a prior for this 15m view.)
| Prior falsifier / invalidation | HELD / BROKEN / UNTESTED | Evidence on this chart |
|---|---|---|
| none carried | UNTESTED | no prior falsifier exists for these shots |

## 65656faa31ba 30m CoinGlass Binance BTCUSDT (10-07 09:24:59 UTC)
- Window: 2026-10-05 ~03:00 .. 2026-10-07 09:25 UTC; cursor on the 10-07 07:00 bar
- Panels: price + VWAP + VP boxes (3), OI candles, CVD candles, net delta. Engine snapshot for this instant: `research/screenshots/engine/65656faa31ba.json` (as_of 09:24Z, klines only)

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| 65656faa31ba-01 | MATCH | cursor bar 10-07 07:00 O 84182.6 H 84228.1 L 84110.0 C 84196.6 | BTCUSDT-1m-2026-10-07.csv aggregated 07:00-07:30: 84182.6 / 84228.1 / 84110.0 / 84196.6, exact |
| 65656faa31ba-02 | MATCH | live bar last price 83805.0 with countdown 05:01 (bar closes 09:30, so 09:24:59) | 1m close 09:24 = 83805.0 (bar 09:00-09:25: O 83909.9 H 83965.5 L 83728.0) |
| 65656faa31ba-03 | MATCH | the big red leg after the 10-07 UTC midnight, then a shelf near 84,000-84,400 | biggest 30m bar of 10-07 is 01:30-02:00: O 85225.1 -> C 84330.7 (-894.4), volume 10,053 BTC; 00:00-04:00 range 83,500.0 - 85,559.5 |
| 65656faa31ba-04 | MATCH | wick low of the sell-off ~83,500 (pixel read, +-40) | 4h swing_low 83500.0 in the engine file and in the 1m archive (low of 00:00-04:00) |
| 65656faa31ba-05 | MATCH | CVD candles fall into the right edge, panel label -8.464K | engine cvd.slope falling, slope_1h and slope_4h falling (delta_1h -1421.7, delta_4h -1378.5 BTC); levels not compared (chart anchors at its first loaded bar) |
| 65656faa31ba-06 | MISMATCH | VWAP at the right edge 84166.2 (legend VWAP 84204.2 at the cursor bar) | engine vwap.price 84183.06 at 09:24: 16.9 points (0.02%) above the chart; engine vwap_anchor_utc reads 2026-10-10T13:30:00Z, a date after the shot, so the anchor of this historical rebuild is not the chart's session start; the 17-point gap is small but the anchor field is wrong |
| 65656faa31ba-07 | MISMATCH | red developing POC line of the 10-07 profile box at ~84,044 (pixel read, +-10) | engine daily_vp.poc 83956.0, intraday_4h_vp.poc 83963.7, post_funding_vp.poc 83960.0: about 85 points below the chart line; the chart box starts at the 10-07 open and its binning is unknown, so this adds one more sample to the known VP offset, it is not a new defect |
| 65656faa31ba-08 | NOT_IN_DATA | OI panel: 96.496K at the right edge, bars rising off ~95.9K; net delta 9.063K (cursor 10.513K) | engine open_interest.confidence LOW, direction flat, change_1h 0.0; trade_flow.net_delta_* are null (live-only); the OI series is not rebuilt per 30m bar on disk and the net-delta unit (+9.063K vs +156 BTC from klines at 07:00) is unknown |

## 359bdb0c7cf9 15m CoinGlass Binance BTCUSDT (10-09, live bar 13:30-13:45 with 04:11 left, so ~13:40:49 UTC)
- Window: 2026-10-07 ~03:00 .. 2026-10-09 13:41 UTC. The shot's recorded `at` 13:45 is the bar end; the capture instant is ~13:41
- Panels: price + VWAP (82568.8) + VP boxes (3), OI candles, CVD candles, net delta

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| 359bdb0c7cf9-01 | MATCH | the drop of the 10-08 US session to a low near 80,400 around 17:30-18:00 (pixel read +-50) | BTCUSDT-1m-2026-10-08.csv: low 80,344.8 at 17:26 UTC; 15m bar 17:45-18:15 O 80800.1 H 80860.0 L 80505.0 C 80767.4 |
| 359bdb0c7cf9-02 | MATCH | the left edge: the leg down from ~85,500 on 10-07 (first 15m bar high at the left) | 10-07 00:00-00:15 bar H 85,559.5, O 85,507.6 (same day's 4h swing_high 85559.5) |
| 359bdb0c7cf9-03 | NOT_IN_DATA | live bar O 82533.5 H 82730.0 L 82456.7 C 82626.4, 12:00 spike to ~83,400 | the 1m archive ends 2026-10-08 (no BTCUSDT-1m-2026-10-09.csv); `shot.py engine 359bdb0c7cf9` would refuse (archive missing the day). Needs refresh_klines.py for 10-09 (queued as Q4a) |
| 359bdb0c7cf9-04 | NOT_IN_DATA | OI 91.999K at the edge (down from ~96K at 10-08 14:00, steepest fall 10-08 14:30-18:00); CVD -13.053K; net delta -7.139K | no OI history or CVD rebuild for 10-08/10-09 on disk; CVD levels are chart-anchored, steps only |
| 359bdb0c7cf9-05 | NOT_IN_DATA | the red POC lines of the three profile boxes (~83,400 left, ~82,950 centre, ~82,600 right) and VWAP 82568.8 | no 10-09 data to rebuild session VWAP / VP; values read from the chart legend and pixels only |

## 23416389787e Claude App, MTS Control Room page (app screen, not a chart)
- Content: six decision cards, all answered, each with a green "Applied: 2026-10-09 ..." line: F-BT-02 (D01 turn_of_candle), F-BT-08 (D02 1m ground truth), F-BT-09/14/B146 (D03 Java restart), F-BT-19 (D04 uptime), X-BTD/X-MAKER (D05 priority), X-GATE (D06 go-live bar)
- Checked against the Control Room database `decisions` collection read 2026-10-10 ~16:30Z

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| 23416389787e-01 | MATCH | D01 shows answer "Cap it to one slot (recommended)", applied note "researched (research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md) ... one slot (own account jishu_1)" | decisions D01-toc: answer "Cap it to one slot", applied text identical |
| 23416389787e-02 | MATCH | D02 "Yes, build it" and applied note "1m ground truth (legs_1m.csv 51 MB, labels_1m.csv 264 MB) exists on F:\MTS\data\bigtrade" | decisions D02-gt1m: same answer and text |
| 23416389787e-03 | MATCH | D03 "Ask me when ready" with the operator note "right now! next time u need a java engine restart - do it right away", applied "restarted now ... 2m20s without snapshots" | decisions D03-java: same |
| 23416389787e-04 | MATCH | D04 keep awake, D05 approve, D06 accept the bar, each with its applied line (sleep timeouts 'never'; T081/T080 handed to two Sonnet workers; GO_LIVE_BAR.md T086) | decisions D04-uptime, D05-priority, D06-gate: same answers and applied text |
| 23416389787e-05 | MATCH | the page is the pickup's input: the operator's why says it must also read D08-D10 | the same collection holds D08-D10 answered and applied (D08 4-12 h imbalance test, D09 fee gate 0.3, D10 heartbeat 10 minutes); D07-D23 are all answered and applied as of 2026-10-10 12:45Z, so nothing is pending |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| 65656faa31ba-06 | the 17-point VWAP gap is within the anchor ambiguity; the wrong vwap_anchor_utc (2026-10-10 on a 10-07 rebuild) is a historical-rebuild field, not the live path | noaction |
| 65656faa31ba-07 | one more sample of the known profile POC offset, filed with the earlier VP findings | noaction |
| 359bdb0c7cf9-03..05 | blocked on the 10-09 kline refresh (Q4a); no new claim lost | noaction |
