# rsi_40_60_line_behaviour (PRE_REG.md frozen first; DEV 2017-08..2024-06, VALIDATION 2024-07..2025-06 once on picks, HOLDOUT never loaded; BTCUSDT+ETHUSDT SPOT; cost 0.14 %; trials 544 DEV, 6 VALIDATION, Holm m = 6)

**In plain words (answer to d-rsi-40-60-line-behaviour-1104)**
- **RSI at 40/60 behaves almost like a coin with a built-in lean, not like a wall.** At the picked cushion an approach ends as hold 25-58 %, break 15-51 %, range (chop) 21-33 % of the time depending on timeframe and side, and a pure random walk gives nearly the same split; averaged over the 16 timeframe x line x side cells the real lines hold only +1.5 points more and break 1.7 points less than chance. No line is a reliable bounce or a reliable break.
- **The "best cushion" is mostly geometry.** An event starts at the band edge nearest where it came from, so on the side RSI came from a wide cushion (5 points) makes "hold" look likely and a narrow one (1 point) makes "break" look likely; the random-walk benchmark shows the same pattern. Real excess over chance is real but small and only on 1h/4h: +4.4 (1h, 40 from above), +6.7 (1h, 60 from below), +5.5 (4h, 40 from above) points of hold.
- **What changes the odds is the other timeframes, not the phase.** When another timeframe's RSI sits at the same line the hold rate is higher (+7 points on 1h, +12 on 4h, +18 on 12h, +17 on 1d, all CIs above 0). When the higher-timeframe bias agrees with the bounce, the bounce holds LESS (-10 points on 1h, -12 on 4h, -14 on 12h; 1d -2, unclear). BTC regime (bull vs range) and fresh vs mature trend change hold by 0-1 point (1d is too thin to read); the bear regime never occurs in the data.
- **No default play.** Of 214 play cells that reached n >= 30, 15 have a DEV fee-net CI above 0 (7 %, chance alone gives about 5 %); the 6 picked cells keep only 2-9 events each on VALIDATION (CIs span 0). Every play cell is underpowered at m = 6, so each is capped INCONCLUSIVE. "Take the bounce" and "wait for the break" are both about 0 % fee-net on average in the unfiltered cells (mean of the 16 cells: bounce +0.005 %, wait +0.028 %).
- **Rule for now (`rules.json`):** `default_play` is null for all 16 cells. Treat the picked cushions and rates as description. Worth a larger study: "another timeframe at the same line" (confluence) is the one factor with a clear, consistent hold-rate effect.

Regime mix: 360 weeks: bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%) (BTCUSDT, regime as of Monday 00:00 UTC). Regime and phase are context columns, the study is otherwise ungated; the Malkan bear regime never occurs on BTC, so every reg_bear cell is empty.

All tuned values are OURS (cushion grid, outcome window N per TF, the crossing count that makes a chop, the 60-day phase cut, the 12h build, confluence/bias definitions, sd for the gate). The 40 and 60 lines are the SOURCED Malkan levels. Definitions are in PRE_REG.md.

## Table 1: behaviour at the picked cushion (DEV, rates of all events; benchmark = random walk, same rules)

Hold = RSI leaves the band back on the side it came from; break = it closes beyond the line by more than c on the far side; range = chop (crossed the line twice or more) or stayed inside for N bars. Cushion pick = largest |hold - break| among c in {1, 2, 3, 5} (n >= 100, >= 40 days). The full 64-row grid is `behaviour_dev.csv`.

| TF | line | from | cushion c | n events | hold % [95 % CI] | break % | range % (chop / inside) | benchmark hold / break / range % | hold minus benchmark (pp) |
|---|---|---|---|---|---|---|---|---|---|
| 1h | 40 | above | 5 | 6026 | 56.8 [55.4, 58.2] | 18.4 | 24.8 (24.8 / 0.0) | 52.3 / 19.0 / 28.6 | +4.4 |
| 1h | 40 | below | 1 | 1574 | 25.5 [23.4, 27.7] | 48.4 | 26.0 (26.0 / 0.0) | 26.2 / 49.1 / 24.7 | -0.7 |
| 1h | 60 | above | 1 | 1693 | 25.8 [23.7, 27.8] | 46.0 | 28.2 (28.2 / 0.0) | 25.8 / 49.9 / 24.3 | -0.1 |
| 1h | 60 | below | 5 | 6222 | 58.2 [56.9, 59.6] | 17.4 | 24.4 (24.4 / 0.0) | 51.5 / 20.3 / 28.2 | +6.7 |
| 4h | 40 | above | 5 | 1456 | 57.4 [54.6, 60.3] | 19.0 | 23.6 (23.5 / 0.1) | 52.0 / 19.4 / 28.7 | +5.5 |
| 4h | 40 | below | 2 | 627 | 29.7 [25.9, 33.4] | 43.7 | 26.6 (26.6 / 0.0) | 27.8 / 47.0 / 25.2 | +1.9 |
| 4h | 60 | above | 1 | 461 | 27.8 [23.6, 31.9] | 39.7 | 32.5 (32.5 / 0.0) | 26.4 / 49.9 / 23.7 | +1.3 |
| 4h | 60 | below | 5 | 1361 | 53.9 [51.0, 56.8] | 21.5 | 24.6 (24.5 / 0.1) | 51.2 / 20.4 / 28.4 | +2.7 |
| 12h | 40 | above | 5 | 465 | 51.4 [46.4, 56.4] | 20.4 | 28.2 (27.7 / 0.4) | 53.0 / 18.9 / 28.0 | -1.6 |
| 12h | 40 | below | 1 | 142 | 28.2 [20.4, 36.0] | 50.7 | 21.1 (21.1 / 0.0) | 25.6 / 49.3 / 25.1 | +2.6 |
| 12h | 60 | above | 1 | 150 | 24.7 [17.8, 31.6] | 48.7 | 26.7 (26.7 / 0.0) | 26.6 / 47.6 / 25.7 | -2.0 |
| 12h | 60 | below | 5 | 414 | 48.6 [43.6, 53.5] | 22.9 | 28.5 (28.3 / 0.2) | 51.6 / 20.7 / 27.8 | -3.0 |
| 1d | 40 | above | 5 | 248 | 57.7 [51.0, 64.3] | 15.3 | 27.0 (25.4 / 1.6) | 51.8 / 19.4 / 28.8 | +5.8 |
| 1d | 40 | below | 2 | 105 | 27.6 [19.1, 36.2] | 41.9 | 30.5 (30.5 / 0.0) | 27.0 / 46.7 / 26.3 | +0.6 |
| 1d | 60 | above | 5 | 147 | 40.1 [32.0, 48.3] | 27.2 | 32.7 (30.6 / 2.0) | 33.3 / 39.7 / 27.1 | +6.9 |
| 1d | 60 | below | 5 | 209 | 44.0 [37.0, 51.0] | 28.7 | 27.3 (26.8 / 0.5) | 51.2 / 20.6 / 28.3 | -7.2 |

- All 64 grid rows are in `behaviour_dev.csv`; averaged per timeframe over the 16 rows of each, the real hold rate exceeds the benchmark by +1.95 (12h) to +4.98 (4h) points and the break rate is below it by 2.3 to 5.6 points: lines are slightly sticky, not walls. RANGE is 21-33 % of events in every one of the 64 rows; "stayed inside the whole window" is almost never the reason (0-7 %), the range is repeated crossing of the line.
- Stability: on VALIDATION (2024-07..2025-06, `behaviour_val.csv`) the 1h and 4h cells with n >= 200 stay within about 5 points of DEV (1h 40 from above c=5 hold 53.6 vs 56.8; 1h 60 from below 57.3 vs 58.2; 4h 60 from below 53.9 vs 53.9). 12h and 1d cells have 19-98 events there and are too thin to read.

## Table 2: what changes the odds (DEV hold-rate difference, day-clustered 95 % CI, pooled per TF over its picked line x side cells)

Aligned = the higher-TF bias (next TF up, RSI14 vs 50) points the way a bounce would go (bias sign equals the side RSI came from); opposed = the other way. Confluence = at least one of the other three TFs has RSI inside the same band, vs none.

| TF | contrast (hold-rate A vs B) | n A / n B | hold % A / B | difference pp [95 % CI] |
|---|---|---|---|---|
| 1h | htf_aligned_vs_opposed | 7617 / 7883 | 45.7 / 55.7 | -10.0 [-11.6, -8.3] |
| 1h | confl_1plus_vs_0 | 6228 / 9287 | 55.0 / 48.0 | +7.0 [+5.3, +8.7] |
| 1h | fresh_vs_mature | 5015 / 9243 | 50.8 / 50.9 | -0.1 [-2.0, +1.8] (spans 0) |
| 1h | bull_vs_range | 2760 / 10040 | 50.4 / 50.6 | -0.2 [-2.5, +2.1] (spans 0) |
| 4h | htf_aligned_vs_opposed | 2074 / 1824 | 42.5 / 54.8 | -12.3 [-15.5, -9.1] |
| 4h | confl_1plus_vs_0 | 2222 / 1683 | 53.6 / 41.2 | +12.4 [+9.2, +15.7] |
| 4h | fresh_vs_mature | 1272 / 2329 | 48.5 / 48.1 | +0.4 [-3.3, +4.1] (spans 0) |
| 4h | bull_vs_range | 730 / 2505 | 47.0 / 48.3 | -1.3 [-5.7, +3.0] (spans 0) |
| 12h | htf_aligned_vs_opposed | 489 / 680 | 36.0 / 50.1 | -14.2 [-20.0, -8.3] |
| 12h | confl_1plus_vs_0 | 728 / 443 | 51.1 / 32.7 | +18.4 [+12.6, +24.2] |
| 12h | fresh_vs_mature | 367 / 718 | 43.6 / 44.7 | -1.1 [-7.6, +5.4] (spans 0) |
| 12h | bull_vs_range | 213 / 776 | 45.1 / 44.1 | +1.0 [-6.6, +8.6] (spans 0) |
| 1d | htf_aligned_vs_opposed | 416 / 264 | 44.2 / 46.2 | -2.0 [-10.0, +6.0] (spans 0) |
| 1d | confl_1plus_vs_0 | 503 / 206 | 50.5 / 33.5 | +17.0 [+8.9, +25.1] |
| 1d | fresh_vs_mature | 226 / 427 | 40.3 / 47.5 | -7.3 [-15.6, +1.0] (spans 0) |
| 1d | bull_vs_range | 137 / 447 | 51.8 / 44.1 | +7.8 [-2.1, +17.6] (spans 0) |

- Context split of the rates for every picked cell (ALL, bias up/down, confluence 0/1plus, regime, phase) is `context_dev.csv`; the 10 context values average hold 37-43 % and break 29-33 % with no value standing out except confluence (hold 43 % vs 37 %).
- Bias "aligned" holding LESS is the opposite of the common story; it is measured here on 2 symbols and not explained, so read it as a hypothesis for the next study, not a rule.

## Table 3: plays on VALIDATION (the 6 DEV picks, tested once; fee-net %, entry at the next bar open after the exit bar, exit N bars later)

Picks are the top 6 of 214 eligible DEV cells (best of 320), at most one per TF x line x side. DEV nets of +2 to +7.5 % come from n = 37-86 events with N-bar returns whose sd is 5-10 % (4h to 1d).

| Cell (TF, line, from, context, play) | c | DEV n / days, net % [CI] | DEV gate | VALIDATION n / days, net % [CI] | Holm | Verdict |
|---|---|---|---|---|---|---|
| 1d, 60, below, ph_mature, wait | 5 | 39 / 38, +7.51 [+2.01, +13.02] | BLOCK | 2 / 2, +1.44 [-5.02, +7.89] | 1.00 | INCONCLUSIVE |
| 1d, 60, above, confl_1plus, bounce | 5 | 49 / 48, +4.42 [+0.94, +7.91] | BLOCK | 5 / 5, +4.59 [-0.26, +9.43] | 0.38 | INCONCLUSIVE |
| 12h, 60, below, ph_mature, wait | 5 | 58 / 54, +2.22 [-1.11, +5.56] | BLOCK | 4 / 4, +1.61 [-7.62, +10.83] | 1.00 | INCONCLUSIVE |
| 4h, 40, below, confl_1plus, bounce | 2 | 86 / 79, +2.14 [+0.25, +4.04] | BLOCK | 8 / 8, -1.49 [-7.46, +4.47] | 1.00 | INCONCLUSIVE |
| 12h, 60, above, ALL, bounce | 1 | 37 / 37, +1.85 [-1.29, +4.99] | BLOCK | 5 / 5, +4.39 [-5.71, +14.50] | 1.00 | INCONCLUSIVE |
| 12h, 40, above, htf_up, bounce | 5 | 57 / 53, +1.82 [-0.95, +4.60] | BLOCK | 9 / 7, +0.93 [-5.97, +7.84] | 1.00 | INCONCLUSIVE |

- Verdict: **NO DEFAULT PLAY.** All 6 cells are INCONCLUSIVE (underpowered, not FAIL): the power gate (m = 6) blocks every play cell because even all events of a cell span too few days (smallest MDE 0.22 % on 1h vs 0.16 % allowed). VALIDATION holds 2-9 events per pick, with CIs from -7.6 to +14.5 %. None gets a default; `rules.json` has `default_play: null` for all 16 cells.
- Across the unfiltered cells (context ALL) the mean fee-net per cell is bounce +0.005 % and wait +0.028 % (median -0.16 and -0.08 %): after 0.14 % cost neither play beats zero.
- 15 of 214 eligible DEV play cells have a CI above 0, about what chance gives for 214 looks at 5 %.

## Trial count and caveats

- DEV evaluations 544 (rates 64, context splits 144, contrasts 16, plays 320), VALIDATION 6 (Holm m = 6), HOLDOUT unread. The random-walk benchmark is not a trial.
- Spot not futures; 2 symbols; DEV overlaps the sibling long-window studies; the entry counts as an event only when RSI enters the band from outside (a bar that jumps across the whole band is not an event); events whose outcome window runs past the window end are dropped; gaps in the archive are not filled.
- The 1d and 12h rows have 100-470 events; their rates carry wide CIs (Table 1). The play result says nothing about other symbols or a longer history; the conclusion "no default play" is about power as much as about edge.
