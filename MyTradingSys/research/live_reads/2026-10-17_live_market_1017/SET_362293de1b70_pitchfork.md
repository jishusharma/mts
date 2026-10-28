# 2026-10-18 operator's own 1W chart with stacked Schiff pitchforks + the tool settings
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 gated). Tag: NOTE (input for the pitchfork layer; the build is claimed by JIS-NUC, see end). -->

Shots: 362293de1b70 (1W chart), eea9183faa19 (Pitchfork settings dialog)
Operator words: "Now my own charts. I use pitch forks. Let us also add that pitchfork layer now!!! Ask Gemini to d" (message cut off after "d").
Clocks: TradingView clock 18:08:53 UTC; weekly countdown 05:51:07 -> weekly close 10-19 00:00Z, so captured 10-18 18:08:53Z. Chart is Binance SPOT BTCUSDT (not the fapi perp of the other reads), linear price axis (0 and -5,000 ticks are evenly spaced), 2017-08 -> 2027-10.
Data: Binance spot /api/v3/klines 1w (479 bars, 2017-08-14 -> 2026-10-12), fetched 10-19.

## Carried context
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_0061b6c6c2bc.md
Different instrument view (spot 1W vs perp 5m); its watch line (cover vs acceptance under 80,955.9) is not scored by a weekly chart: UNTESTED here.

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| 362293de1b70-1 | MATCH | Header O 83,773.12 H 84,352.00 L 79,800.00 C 81,208.44 = week of 10-12 at 18:08Z | spot 1w 10-12 O 83,773.12 H 84,352.00 L 79,800.00 (final close 80,819.98 at 10-19 00:00) |
| 362293de1b70-2 | MATCH | Swing extremes the lines are drawn to: 2017-12 top, 2021-11 top, 2022-11 bottom, 2024-03 top, 2024-08 low, 2025-10 ATH, 2026 lows, 2026-09 high | spot 1w: 19,798.68 (2017-12-11); 64,854 (2021-04-12); 69,000 (2021-11-08); 17,622 (2022-06-13); 15,476 (2022-11-21); 73,777 (2024-03-11); 49,000 (2024-08-05); 126,199.63 (2025-10-06); 60,000 (2026-02-02); 82,850 (2026-05-04); 57,800.19 (2026-06-29); 87,395.67 (2026-09-21) |
| 362293de1b70-3 | MATCH | Price is at a blue (level 1) line from below a red median that capped the Sep high | by pixel: red median at ~88K for Sep 2026 vs high 87,395.67; blue line at ~80-81K vs the 10-12 week low 79,800 and the shot price 81,208 (pixel error ~1.5K) |
| 362293de1b70-4 | NOT_IN_DATA | Exact line prices and anchor coordinates of each pitchfork (P1, P2, P3) | drawings live only in TradingView; the dialog's Coordinates tab shows each fork's three points (price + bar time); no file holds them (T066) |
| 362293de1b70-5 | NOT_IN_DATA | Projected zigzag to ~mid 2027 (peak near ~80K on the blue line, then down to ~55K) | a forward drawing, not data; recorded as the operator's projection only |
| eea9183faa19-1 | MATCH | Tool settings: Style = Schiff, Extend lines on, Median red, only level 1 enabled (blue), other levels (0.382 .. 2.45) off, Background on | read from the dialog |

## What the chart is (for the layer spec)
- Several Schiff pitchforks with nearly the same slope, stacked so that red medians and blue level-1 lines alternate into one rising channel grid from 2017 to 2027. Red zigzags are the A-B-C anchor legs: one fork from the 2020 base -> 2021-11 top -> 2022 drop, one from the 2022-11 bottom -> 2024-03 top -> 2024-08 low, and a projected one for 2026-27.
- Pitchfork geometry (TradingView definitions; confirm against TradingView help when building): pivots P1, P2, P3. Median line from the origin through the midpoint of P2-P3; level-1 lines are parallels through P2 and P3. Original: origin = P1. Schiff: origin shifted to halfway between P1 and P2 in price, P1's time. Modified Schiff: halfway in both time and price. The chart uses Schiff, linear scale. On a linear scale a 2017-2027 channel is a straight line in dollars, so line distances in % shrink as price rises; whether linear or log is the right space is itself a test arm.

## What the layer must solve to be testable (OURS)
1. Anchors: by hand they are chosen with hindsight. A causal layer picks P1-P3 from confirmed pivots only (delayed five-bar rule, CYCLE_DESIGN.md; on 1W a pivot is usable 2 bars after it), and a fork exists only from P3's confirmation time.
2. Signal: price touching a median or level-1 line. Outcome: reversal of k x ATR before continuation, per TF (1W, 1D, 4h; the operator draws on 1W).
3. Placebo: random parallel lines with the same slope and spacing, and the same fork on the log scale. A fork only adds value if line touches reverse more often than placebo lines at the same distance.
4. Power: on 1W there are about 470 bars and maybe 10-20 line touches in 9 years; a 1W fork alone cannot give a probability. Its use is as a location layer (like weekly VA) for lower-TF signals, which is how the operator reads it (price under the red median, at the blue line).
5. Record the operator's actual anchors from the Coordinates tab (one paste per fork) as SOURCED inputs for a parity check against the causal anchors.

## Live system
No change (HALT + HALT_DAILY_LOSS, mirror@2026-10-18 17:56Z). Nothing here touches the live path.

## Routing
Trunk already holds a claim `gemini-pitchfork-study-layer` by JIS-NUC/sharma at 2026-10-18 20:14:25Z (no card file yet). The claim is the lock: this session does not file a second card. This extract is the input; a signal points the NUC session to it.

## Watch next
1W close of the 10-12 week: 80,819.98, inside the blue line zone (~80-81K by pixel), not back above the red median.
