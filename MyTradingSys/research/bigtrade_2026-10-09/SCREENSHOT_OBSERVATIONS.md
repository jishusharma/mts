# SCREENSHOT OBSERVATIONS (worker C, observation thread)

Session MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt, 2026-10-09. Purpose (operator): find what the charts show that the Java snapshots and data files do not, so the backtest can test it. Observations are assumptions to be tested (operator caveat); nothing here is trade advice or a verdict. Companion file: observations.csv (85 rows, same ids). Findings: FINDINGS.md F-BT-09 .. F-BT-17.

Classes: MATCH = the chart value is reproduced by files on disk (file and numbers given); MISMATCH = the chart shows one thing and the pipeline/snapshot or the raw data show another; NOT_IN_DATA = the chart shows something no file on disk holds or can be reproduced from. Pixel reads are marked and carry about +-30..60 points. FEATURE lines are HYPOTHESIS: formulas in existing columns, causal (bars closed at t), thresholds are analysis settings (PLAN section 3), never tuned values.

## 0. Result in one table

| Item | Count |
|---|---|
| image files read | 25 (all) |
| trading charts analysed | 12 (C01-C12) |
| skipped (not trading charts) | 13 (S01-S13; S01 and S02 are byte-identical) |
| observations | 85 |
| MATCH | 59 |
| MISMATCH | 13 |
| NOT_IN_DATA | 13 |
| findings appended | F-BT-09 .. F-BT-17 (9) |

What the charts show that the pipeline lacks or gets wrong (details per image and in the findings):

| Chart element | Pipeline state | Evidence | Feature |
|---|---|---|---|
| OI flush at 1m/5m (OI drop while price and CVD fall) | snapshot OI is hourly-stepped (F-BT-10); recorder has 46 h of holes (F-BT-11) | C04-06, C06-09, C08-04 vs C05-08 | FEAT-01 |
| CVD step | MATCH on steps (C04-08, C06-06); chart level is anchored at the first loaded bar and differs by timeframe | C06-05, C07-07, C09-05 | FEAT-01, FEAT-04 |
| Liquidity sweep of a local high/low | sweep flag is prior-day H/L only and latched (F-BT-13) | C04-10, C07-09 | FEAT-02, FEAT-03 |
| HTF levels (daily/prior-day POC rays) | Java POC/VAH/VAL biased (F-BT-09), naked POC list frozen since 08-28 (F-BT-14) | C04-03/04, C05-04/05, C06-03/04 | FEAT-07 |
| VWAP anchor | vwap.price is 00:00Z-anchored while session.vwap_anchor_utc says 13:30Z (F-BT-12); chart VWAP truncated by loaded history | C06-02, C09-02 | FEAT-08 |
| Footprint absorption / imbalance | per-1m USD 10 buckets exist and the deltas equal CoinGlass (33/33 bars); no imbalance flags, no multi-minute footprint | C10-02..05, C12-03 | FEAT-04, FEAT-10 |
| Net Delta panel | not order-flow delta: per-bar step = sign(close-open) x abs(dOI) (inferred); no such field | C04-09, C07-08, C06-11 | FEAT-05 |

## 1. Time bases and how the CoinGlass panels are built (derived from the 12 charts)

- TradingView-based pages (coinglass.com/tv): axis is UTC. Proven by exact bar OHLC matches: 30m 07:00 bar (C05-01), 15m/5m/4h bars of Oct 7 (C06-01, C07-01, C08-01), Aug 31 bars (C01-01, C02-01, C03-01).
- Footprint pages (legend.coinglass.com): axis is IST (clock '02:47:29 (UTC+5.5)'; hour bars start at :30). 33 of 33 closed 15m bar deltas equal orderflow_live only after subtracting 5:30 (C10-02). Screenshot file times in the uploads folder are local IST (02:44 local = 21:14Z). Snapshot file names carry the IST date too (F-BT-16).
- CVD: cumulative from the first loaded bar, so the level differs by timeframe at the same minute (21:14Z Oct 7: 15m -10.776K, 5m -6.869K, 4h -8.322K, 3m -3.902K; our cvd_day -6,656, snapshot -6,658.5). Steps agree with our data (C04-08, C06-06). For the 3m chart the anchor fits ~06:18Z (about 300 bars).
- VWAP: session VWAP (daily reset at 00:00Z) computed from chart-timeframe bars and truncated to the loaded history: 5m/15m reproduce the 00:00Z value within 5 points, 4h is +58 (4h-bar hlc3), 3m (83,461.8) restarts at its first loaded bar (06:06Z, error 0.08).
- Net Delta family (screenshot identities, exact on 15m, 5m, 3m, 4h): Net Delta = Net Longs - Net Shorts; Net Longs(New) - Net Shorts(New) = CVD; Net Longs + Net Shorts = OI change since the first bar. Per-bar step of Net Delta fits sign(close-open) x abs(dOI) (Oct 5 14:50: -51.5 vs -50.9; Oct 7 21:10: -12..-20 vs -18). So the operator's 'Net Delta' is an OI-and-price positioning series, not trade delta (our bar delta for the Oct 5 bar is +17.7). INFERRED, 2 bars.
- Volume profile: the hidden VPVR label on the Aug 31 charts says 24 rows / 70 %; the Oct charts draw fixed-range or session profiles with red POC rays. 24-row POCs from trade-level volume reproduce the ray reads on the 5m/15m/30m charts (C04-C07, FEAT-07); the 4h chart computes its rays from 4h bars (C08-06).
- Footprint: one number per price row plus red/green highlighted cells; the numbers do not sum to bar volume (C12-04), so their meaning is unknown. Per-bar delta labels are exact.

## 2. Images

### C01  BTCUSDT Binance perp, 15m, CoinGlass TradingView page

- File: MyTradingSys/archive/mts_historical/vvp_sc_01_15m.png
- Window: UTC axis, about 2026-08-30 08:00Z to 2026-08-31 10:37Z (countdown 07:51 on a 15m bar = 10:37:09Z)
- Panels and indicators: price with Bollinger(20,2); hidden VPVR (label: 24 rows, up/down 70); RSI(14) with SMA(14) and 40/50/60 lines; CoinGlass OI candles, CVD candles, Net Delta
- Operator annotations: none by the operator (no rays, boxes or labels)
- What happened (data): Range 76.9K-79.3K. Sell-off 23:15-00:15 with a wick to 76,947 at 23:47, recovery to 78.4K by 10:37.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C01-01 | MATCH | Axis is UTC; date is 2026-08-31 (file mtime 17:02 local); header bar 10:30 O78409.3 H78426.9 L78341.4 C78426.9 (forming, countdown 07:51 = 10:37:09Z) | klines 1m 2026-08 aggregated 15m 10:30: O 78409.3 L 78341.4 equal; H 78455.4 / C 78455.4 only because rows run to 10:37:59 vs chart 10:37:09 |
| C01-02 | MATCH | Bollinger(20,2) basis/upper/lower 78270.7 / 78720.4 / 77821.0 | recomputed from 15m closes (last close 78426.9): 78270.7 / 78720.4 / 77821.0, exact |
| C01-03 | MATCH | RSI(14) 58.55 with SMA(14) of RSI 62.14 | Wilder RSI on 15m closes: 58.55 and 62.14, exact |
| C01-04 | MATCH | OI candle close 106.757K | metrics/BTCUSDT-metrics-2026-08-31.csv sum_open_interest 106,734.5 (10:30), 106,746.3 (10:35), 106,831.5 (10:40): within 0.02 % |
| C01-05 | MISMATCH | CVD close -8.735K | day cumulative delta 00:00-10:37 from klines (2*taker_buy-vol) = -40 BTC; chart level is cumulative from the first loaded bar, so the absolute level is not comparable **Feature:** FEAT-01/04 use windowed delta sums, never the absolute CVD level |
| C01-06 | MATCH | Large red 15m bars ~23:15-00:15 with a long lower wick, then recovery | 15m 23:15 O78334.3 L77614.8 C77647.9 delta -1317; 23:45 L76947.2 (at 23:47) C77634.6; OI 106,568 (23:30) -> 106,204 (00:00) = -0.34 %; 00:15 close 77,872 |
| C01-07 | NOT_IN_DATA | Hidden indicator label 'VPVR Number Of Rows 24 Up/Down 70' (24 rows, 70 % value area) | snapshot Java profile uses ~5 USD bins (MarketDataSnapshot.buildVp: numBins=max(50,range/5)); no 24-row profile is emitted anywhere **Feature:** FEAT-07: poc24 (24 equal rows over the anchor range) |
| C01-08 | NOT_IN_DATA | Net Delta panel -634 (series separate from CVD) | no column with that definition; see 'How the CoinGlass panels are built' (Net Delta = Net Longs - Net Shorts, per-bar step = sign(price move) x abs(dOI)) **Feature:** FEAT-05 |

### C02  BTCUSDT Binance perp, 3m, same page and panels as C01 (price, BB, RSI, OI, CVD, Net Delta)

- File: MyTradingSys/archive/mts_historical/vvp_sc_02_3m.png
- Window: UTC axis, 2026-08-31 about 08:12Z to 10:37Z
- Panels and indicators: price with Bollinger(20,2); RSI(14)+SMA; OI candles; CVD candles; Net Delta (VPVR label cropped)
- Operator annotations: none by the operator
- What happened (data): Expansion to ~78.77K around 09:12 (pixel read), then fade to 78.44K.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C02-01 | MATCH | Header 3m bar 10:36 O78375.0 H78444.4 L78374.9 C78444.4 | klines 1m 2026-08 aggregated 3m 10:36: O 78375.0 L 78374.9 exact; H/C differ only by partial-bar timing (+11 USD) as in C01 |
| C02-02 | MATCH | BB(20,2) 78463.6 / 78669.4 / 78257.8 and RSI(14) 50.22, SMA 45.44 | recomputed from 3m closes: identical to the digit |
| C02-03 | MATCH | OI close 106.761K | metrics 5m OI 106,746.3 (10:35) -> 106,831.5 (10:40) |

### C03  BTCUSDT Binance perp, 6h, same page and panels

- File: MyTradingSys/archive/mts_historical/vvp_sc_03_6h.png
- Window: UTC axis, 2026-08-18 .. 2026-09-02 (last bar 06:00Z of Aug 31, countdown 01:21:46 = 10:38:14Z)
- Panels and indicators: price with Bollinger(20,2); RSI(14)+SMA; OI candles; CVD candles; Net Delta
- Operator annotations: none by the operator
- What happened (data): Aug 19 12:00 bar +3,692 with OI +5.3K and delta +24.4K; rally to ~80K by Aug 25 (BB upper 80.3K), then a 76-79K range.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C03-01 | MATCH | Header 6h bar 06:00 O77984.8 H78774.0 L77761.4 C78455.3 | klines 1m 2026-08 aggregated 6h 06:00: O 77984.8 H 78774.0 L 77761.4 exact; close partial |
| C03-02 | MATCH | BB(20,2) 78600.2 / 80302.6 / 76897.8; RSI 54.37, SMA 54.21 | BB exact; RSI 54.34 / SMA 54.16 (0.05 gap = Wilder seeding length) |
| C03-03 | MATCH | Large green 6h candle on Aug 19 with OI and CVD stepping up together | 6h 08-19 12:00: 64,479 -> 68,171 (+3,692, high 70,450), OI 104,717 -> 109,995 (+5,278), delta +24,426; OI max 111,507 at 15:05; Aug 21 highs 75.8K / 79.6K |
| C03-04 | MATCH | OI close 106.763K | metrics 106,746-106,832 at 10:35-10:40 |

### C04  BTCUSDT Binance perp, 5m, CoinGlass TradingView page (the chart cross-checked in OPERATOR_ASKS_2026-10-05 section 1)

- File: C:/Users/E-ngineers/AppData/Local/Temp/claude/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed/54f7bddb-7e77-45fb-a79c-0521a5214ada/images/1.png
- Window: UTC axis, 2026-10-04 ~21:30Z to 2026-10-05 14:55Z (axis '5' = 00:00Z; countdown 00:21 on the 5m bar = 14:54:39Z)
- Panels and indicators: price + daily VWAP (86073.6, vertical reset at 00:00Z) + fixed-range volume profile from 00:00Z with its POC ray; OI candles; CVD candles; Net Delta
- Operator annotations: operator green horizontal ray 85369.0 (from ~05:25Z to the right edge); red POC ray ~86,270 across the profile range; red ray at ~85,246 left of 00:00Z (previous-day POC)
- What happened (data): High 86,976.1 at 01:28; low 85,369.0 at 05:24; rebound to 86,683.9 (14:08); flush 14:30-14:34 to 85,400.1 on OI -1.1 %; 85,369.0 was taken at 15:32.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C04-01 | MATCH | Header 5m bar 14:50 O85645.3 H85664.1 L85440.0 C85573.3 | orderflow_live/2026-10-05.csv 14:50-14:54: O 85645.3 H 85664.1 L 85440.0 C 85575.3 (chart caught the 14:54 minute ~20 s early) |
| C04-02 | MATCH | VWAP 86073.6 (daily line, vertical reset at 00:00Z) | hlc3 x volume from 00:00Z through 14:53 = 86073.86; snapshot vwap.price 86074.51 (14:53:12); from 13:30Z it would be 85968.28 |
| C04-03 | MISMATCH | Fixed-range VP from 00:00Z; red POC ray at ~86,270 (pixel read, +-30) | trade-level 24-row POC row 86,239.5-86,306.5 (agrees with chart); trade-level $10 POC 85,500; Java snapshot daily_vp.poc 85,519.2 (its VAH 86,270.18 sits on the chart POC): Java vs chart -751 **Feature:** FEAT-07 |
| C04-04 | MISMATCH | Left red ray (previous day POC, ends at 00:00Z) at ~85,246 (pixel) | Oct 4 24-row POC row 85,200-85,288 (agrees); Java prior_day.poc in the 14:53 snapshot = 86,574.75 (+1,329 vs chart) **Feature:** FEAT-07 |
| C04-05 | MATCH | Operator green horizontal ray 85,369.0 starting ~05:25Z, not taken at 14:54 | 1m low exactly 85369.0 at 05:24Z; snapshot structure.4h.swing_low 85369.0; min low 05:25-14:54 = 85,400.1 (31.1 above); taken at 15:32Z (low 85,188.3) |
| C04-06 | MATCH | OI falls hard at the 14:30 candle together with price and CVD (chart OI ~97.3K -> 96.1K) | oi_5m_30d: 97,319 (14:30) -> 96,211 (14:40) = -1,108 (-1.14 %); 5m dOI -855 at 14:30 (robust z -22.9, trailing 288 bars); delta -3,063 (z -34.6); ret -0.89 % **Feature:** FEAT-01: z5(dOI5)<=-4 and z5(delta5)<=-4 and ret5<0 [HYPOTHESIS] |
| C04-07 | MISMATCH | Chart OI is clearly falling (-1.1 % in 10 min) | snapshot 14:53:12 open_interest.change_1h_pct 0.0, direction flat, delta_state neutral (B136 pre-fix state, OPERATOR_ASKS section 1); F-BT-10 covers the hourly stepping that remains after the fix |
| C04-08 | MATCH | CVD drops ~3K in the flush candle; CVD level -1.861K | step: cvd_day 14:29 +214 -> 14:34 -2,849 = -3,063 (MATCH); level: cvd_day 14:54 = -2,541, snapshot cvd.value -2,618 vs chart -1,861 (level differs, anchor = first loaded bar) |
| C04-09 | NOT_IN_DATA | Net Delta last bar steps -363.469 -> -414.327 (-50.9) while price fell 72 and OI rose | no field; reproduced as sign(close-open) x abs(dOI) = -(96,138.75-96,087.20) = -51.5; our own bar delta for 14:50-14:54 is +17.7 (opposite sign), so Net Delta is not order-flow delta **Feature:** FEAT-05: nd5 = sign(close-open)*abs(OI[t+5m]-OI[t]) [HYPOTHESIS, 2 bars verified] |
| C04-10 | NOT_IN_DATA | Price took out local highs (poke above the 08Z high 86,463 to 86,684 at ~14:08) then flushed | snapshot session.sweep_flag False / direction none at 14:53: Java only compares with prior-day H/L (86,770 / 84,677.3) from 13:30Z; local pivots are not represented **Feature:** FEAT-02 |
| C04-11 | MATCH | OI rises into the high before the flush (new longs on the breakout) | oi_5m_30d 13:50 96,736 -> 14:00 97,126 -> 14:30 97,319 (+583) while 1m highs reached 86,683.9 |
| C04-12 | MATCH | Price holds above the flush low after the flush (operator: 'has not taken out the low yet') | delta 14:35+14:36+14:37 = +109+370+63 = +542; 1m max_trade 201.8 BTC at 14:36; no 1m low below 85,400.1 from 14:35 through 14:54, and 85,369.0 is first broken at 15:32Z **Feature:** FEAT-03 |
| C04-13 | MATCH | (Not drawn on the chart) big sell prints during the flush | b999_sell_n 14:30..14:34 = 3,4,4,13,13; max_trade 99.6 BTC at 14:34 (columns exist in orderflow_live; the chart has no equivalent) **Feature:** FEAT-09 |
| C04-14 | MATCH | Operator: 'maybe it will take it out - maybe not' (85,369.0 ray) | first 1m low below 85,369.0 = 15:32Z (85,188.3); next 2h range 84,910-85,630; 8h close 85,847.5 (data fact, no verdict) |

### C05  BTCUSDT Binance perp, 30m, CoinGlass TradingView page

- File: C:/Users/E-ngineers/AppData/Local/Temp/claude/C--Users-E-ngineers-IdeaProjects-BinanceDataFeed/ba1b630c-7576-45ac-ab15-fe843ee74671/images/1.png
- Window: UTC axis, 2026-10-04 ~19:40Z to 2026-10-07 09:25Z (countdown 05:01 on a 30m bar = 09:24:59Z); crosshair on 07 Oct 07:00
- Panels and indicators: price + VWAP + three session volume-profile boxes (Oct 5, Oct 6, Oct 7) with red POC rays; OI candles; CVD candles; Net Delta
- Operator annotations: no hand-drawn ray; operator crosshair at 07 Oct 07:00 (header shows that 30m bar)
- What happened (data): Oct 5 14:30 flush; Oct 6 range 85.0-86.7K; Oct 7 01:50-02:05 drop from 85.3K to 83.5K, 84.2K at 07:00, 83.8K at 09:25.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C05-01 | MATCH | Header (crosshair on 07:00 bar) O84182.6 H84228.1 L84110.0 C84196.6; last price tag 83805.0 (countdown 05:01) | orderflow_live/2026-10-07.csv 30m 07:00: O 84182.6 H 84228.1 L 84110.0 C 84196.6 exact; 30m 09:00 close at 09:24 = 83805.0 |
| C05-02 | MATCH | VWAP 84204.2 at the crosshair, 84166.2 on the axis (last) | 00:00Z-anchored hlc3 VWAP from 30m bars: 84,202.0 at 07:29 and 84,163.9 at 09:24 |
| C05-03 | MATCH | Three session profile boxes (Oct 5, 6, 7) with POC rays at ~85.9K, ~85.57K, ~84.06K (pixel, +-60) | 24-row POC rows: Oct 5 85,857-85,943; Oct 6 85,537-85,603; Oct 7 to 09:25 83,929-84,015 **Feature:** FEAT-07 |
| C05-04 | MISMATCH | Oct 6 POC ray ~85.57K | Java snapshot (09:23) prior_day.poc 86,269.35 / VAH 86,414.55 / VAL 85,638.48 vs trade-level POC 85,580, VAH 86,220, VAL 85,430 (+689) **Feature:** FEAT-07 |
| C05-05 | MISMATCH | Oct 5 POC ray ~85.9K | Java snapshot (Oct 6 11:59) prior_day.poc 85,510.32 vs chart/24-row 85,900 (-390; trade-level $10 POC 85,500: the profile is bimodal 85.5K / 86.26K) **Feature:** FEAT-07 |
| C05-06 | MATCH | Oct 7 POC ray ~84.06K at 09:25 | snapshot daily_vp.poc 83,956.0 vs 24-row 83,972: on a one-sided profile the Java POC is close |
| C05-07 | MATCH | Oct 5 14:30 flush visible as red price, OI and CVD candles | same event as C04-06 |
| C05-08 | NOT_IN_DATA | Oct 7 ~01:50-02:05 crash (OI candle with long wick) | price 85,276 -> 83,500 in 15 min and delta -5.0K are in the data; OI is not: oi_1m/oi_5m_30d hole 2026-10-05 15:40 -> 10-07 07:30; snapshot OI frozen at -0.05 flat/neutral from 01:02 to 02:02 (hourly stepping, F-BT-10) **Feature:** FEAT-01 (needs gap fill, F-BT-11) |

### C06  BTCUSDT Binance perp, 15m, CoinGlass TradingView page; first of a 7-image batch uploaded 2026-10-08 02:44 local (= 21:14Z)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/0e1744d6-image.png
- Window: UTC axis, 2026-10-06 ~15:30Z to 2026-10-07 21:15Z (countdown 00:41 = 21:14:19Z)
- Panels and indicators: price + VWAP 83726.8 + fixed-range VP from 07 Oct 00:00 with POC ray + previous-day POC ray at the left; OI candles; CVD candles; Net Delta; Net Longs; Net Longs(New); Net Shorts; Net Shorts(New)
- Operator annotations: fixed-range VP box and per-day POC rays only; no hand-drawn horizontal ray
- What happened (data): Day high 85,559.5 at 00:12; crash 01:50-02:05 to 83.5K; slide with an OI flush to the 82,706.2 low at 13:48; recovery to 83,653.6 (16:30); 83.0-83.6K range; 20:33 drop; 83.3K at 21:14.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C06-01 | MATCH | Header 15m bar 21:00 O83388.3 H83411.2 L83282.7 C83309.1 (forming, countdown 00:41) | orderflow_live/2026-10-07.csv 15m 21:00: O 83388.3 H 83411.2 L 83282.7, close 83326.3 at 21:14:59 (chart ~40 s earlier) |
| C06-02 | MATCH | VWAP 83726.8 | hlc3 x vol from 00:00Z using 15m bars 83,723.2; using 1m 83,722.6; snapshot vwap.price 83,722.76; from 13:30Z 83,205.7 |
| C06-03 | MISMATCH | Fixed range from 00:00Z; red POC ray at ~83,333 (pixel), price 83,309 sitting on it | trade-level 24-row POC row 83,300.6-83,419.5, $10 POC 83,400 (agree); Java daily_vp.poc 83,702.35 / VAH 84,062.77 / VAL 83,081.63 (POC +369 vs chart, in a valley between the peaks 83,400 and 83,800) **Feature:** FEAT-07 |
| C06-04 | MISMATCH | Top-left red ray at ~85,568 = Oct 6 POC, ends at 00:00Z | Oct 6 24-row POC row 85,537-85,603; Java prior_day.poc in the Oct 7 snapshots = 86,269.35 (+701) **Feature:** FEAT-07 |
| C06-05 | MISMATCH | CVD close -10.776K | cvd_day 21:14 = -6,656 (snapshot -6,658.5 at 21:13:12); the chart is 4.12K lower here and the four timeframes disagree with each other at the same minute: 5m -6.869K, 3m -3.902K, 4h -8.322K, 15m -10.776K (anchor = first loaded bar) |
| C06-06 | MATCH | CVD steps down ~3.0-3.3K in the 01:45 candle | 15m delta 01:45 = -3,336.9 (cvd_day -724.0 -> -4,061.0); next bar -741.9 |
| C06-07 | MATCH | Big red 15m candle at 01:45 (price ~85.3K -> ~84.3K) | 15m 01:45 O85259.4 H85300.7 L84330.2 C84330.7; 5m 01:50 delta -1,122 and 01:55 -2,248; 02:00 bar low 83,500.0 |
| C06-08 | MATCH | OI peaks ~97K near 11:30-12:15, bottoms ~95.4K at ~19:30, rises after | oi_5m_30d: max 97,331.8 at 11:30; min 95,446.2 at 19:30; 21:10 96,359.7 (+913, +0.96 % since 19:30) |
| C06-09 | MATCH | OI, price and CVD fall together 12:30-13:48 into the 82,706 low, then price recovers | OI 97,058.3 (12:30) -> 96,209.9 (13:50) = -848 (-0.87 %); cvd_day -4,618 -> -5,684 (-1,065); price 83,441 -> low 82,706.2 at 13:48; 5m 13:45 dOI -305 (z -5.8), delta -1,062 (z -8.1) **Feature:** FEAT-01 [HYPOTHESIS] |
| C06-10 | MATCH | Recovery after the low (chart: price back to ~83.5K by 16:30) | max high 83,653.6 at 16:30 (+947 from 82,706.2) within 2h42; snapshot session.high 83,653.6 / session.low 82,706.2 |
| C06-11 | NOT_IN_DATA | Panels: Net Delta -1.768K = Net Longs -2.19K minus Net Shorts -0.4216K; Net Longs(New) -7.958K minus Net Shorts(New) +2.83K = -10.788K ~ CVD -10.776K | identities hold exactly on this and the 5m/3m/4h screenshots; none of the six series exist in our columns **Feature:** FEAT-05 |
| C06-12 | MATCH | OI rising since 19:30 | snapshot 21:13:12 open_interest direction rising, change_1h_pct 0.27, delta_state aggressive_short (value last updated 21:01, hourly) |
| C06-13 | NOT_IN_DATA | Operator drawings: fixed-range VP box anchored 07 Oct 00:00 and per-day POC rays (no hand-drawn horizontal ray on this chart) | nothing in runtime_data stores the operator's VP anchors or rays; the POC rays reproduce with FEAT-07 **Feature:** FEAT-07 |

### C07  BTCUSDT Binance perp, 5m, same page and panels as C06 (second image, 02:44 local = 21:14Z)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/5df13649-image.png
- Window: UTC axis, 2026-10-07 ~12:08Z to 21:15Z (countdown 00:11 = 21:14:49Z); left label 07 Oct '26 00:00 and right label 21:10 belong to the selected fixed-range VP
- Panels and indicators: price + VWAP 83720.7 + fixed-range VP (selected, floating toolbar, bottom label 82706.2) with POC ray at the last price; OI; CVD; Net Delta; Net Longs/Shorts and (New) pairs
- Operator annotations: the operator was editing the fixed-range profile (selection handles and toolbar visible)
- What happened (data): Low 82,706.2 at 13:48 on an OI flush; 20:30 candle -187 delta; flat close 83,320.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C07-01 | MATCH | Header 5m bar 21:10 O83328.8 H83328.9 L83282.7 C83320.0 | orderflow_live 5m 21:10: O 83328.8 H 83328.9 L 83282.7, close 83326.3 at 21:14:59 |
| C07-02 | MATCH | VWAP 83720.7 | 5m-bar hlc3 VWAP from 00:00Z 83,717.15; 1m basis 83,722.6 |
| C07-03 | MATCH | Fixed-range VP selected (floating toolbar), range 07 Oct 00:00 -> 21:10, bottom label 82706.2 | day low 82,706.2 at 13:48Z in both klines and orderflow_live; day high 85,559.5 at 00:12Z |
| C07-04 | MATCH | Red POC ray at ~83,348 (pixel), price label 83,320 right on it | 24-row POC mid 83,360 (row 83,300.6-83,419.5) **Feature:** FEAT-07 |
| C07-05 | MATCH | Big red 5m candle at 20:30 (from ~83.52K to ~83.34K) | 5m 20:30 O 83,524.9 H 83,532.4 L 83,337.8 C 83,352.7, delta -187.18 (identical to the footprint label in C12) |
| C07-06 | MATCH | OI close 96.333K (3-decimal K) | oi_5m_30d 96,359.7 (21:10), 96,347.3 (21:15); CoinGlass vs Binance differ by 0.01-0.03 % |
| C07-07 | MISMATCH | CVD close -6.869K | cvd_day -6,656 (offset -213); see C06-05 |
| C07-08 | NOT_IN_DATA | Net Delta bar step -3.245K -> -3.263K (-18) on a down bar with OI -20 | rule sign(close-open) x abs(dOI) gives -20 (CoinGlass OI) or -12.4 (Binance 5m hist); our bar delta -19.55 **Feature:** FEAT-05 |
| C07-09 | MATCH | 13:45 candle: long lower wick to 82,706 with OI falling | 5m 13:45 O83052.9 L82706.2 C82907.0, delta -1,062, dOI -305; next bar 13:50 close 83,300.4 (+393) **Feature:** FEAT-02 |

### C08  BTCUSDT Binance perp, 4h, same page and panels as C06 (third image, 02:44 local)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/98d7546b-image.png
- Window: UTC axis, 2026-09-19 .. 2026-10-09 (last bar 20:00Z of Oct 7, countdown 02:45:30 = 21:14:30Z)
- Panels and indicators: price + VWAP 83782.9 (resets daily) + one session profile per day with red POC ray; OI; CVD; Net Delta; Net Longs/Shorts pairs
- Operator annotations: per-day profile boxes and POC rays that end at the box edge
- What happened (data): Sep 21 rally 80K -> 86K on flat OI; Sep 23 12:00 flush (OI -5.4 %); Sep 24 08:00 lower low 82.8K; 86K area into Oct 6; Oct 7 drop to 83.3K.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C08-01 | MATCH | Header 4h bar 20:00 O83399.3 H83569.4 L83282.7 C83320.0 | 4h 20:00 from orderflow_live: O 83399.3 H 83569.4 L 83282.7 exact |
| C08-02 | MATCH | OI header O96.057K H96.368K L96.004K C96.334K | oi_5m_30d: 20:00 96,054.2; max in bar 96,368.1 (21:05); close ~96,34x |
| C08-03 | MATCH | VWAP 83782.9 | 4h-bar hlc3 VWAP from 00:00Z 83,780.6; the 1m basis is 83,722.6 (a 4h chart overstates VWAP by +58 here); resets daily |
| C08-04 | MATCH | Largest OI candle on the chart (Sep 23, red, ~106K -> ~100.6K) with a red price candle | metrics 5m OI: 4h 09-23 12:00 106,252 -> 100,521 (-5,732, -5.4 %); price 85,623 -> 83,961 (-1,662); delta -3,615; second lower flush 09-24 08:00: OI -1,187, price -1,017 to low 82,832, delta -3,947, then +923 next bar **Feature:** FEAT-01 |
| C08-05 | MATCH | Big green candle Sep 21 (80K -> 85K) with almost no OI change | 4h 09-21 08:00: 81,700 -> 84,850 (+3,150, +3.9 %), OI +297 (+0.3 %), delta +11,397 (next bars +468, +702) |
| C08-06 | NOT_IN_DATA | Per-day session profiles with red POC rays that stop at each day's box edge (6 bars per box) | rays are computed by the chart from 4h bars; we hold no per-day POC list (naked POC file frozen 2026-08-28, F-BT-14); last-day ray reads ~83.3-83.6K (pixel +-50) **Feature:** FEAT-07 |
| C08-07 | NOT_IN_DATA | CVD close -8.322K; Net Longs +316.948 minus Net Shorts -11.172K = Net Delta +11.489K | no start bar in the Sep-Oct kline-derived delta reproduces -8,322 (the 4h chart starts before Sep 19, anchor not recoverable); Net Longs + Net Shorts = dOI since the first bar (-10.855K) **Feature:** FEAT-05 |

### C09  BTCUSDT Binance perp, 3m, same page and panels as C06 (fourth image, 02:45 local)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/a2caa2bd-image.png
- Window: UTC axis, 2026-10-07 ~12:12Z to 21:18Z (countdown 02:47 = bar opened 21:15:13Z)
- Panels and indicators: price + VWAP 83461.8; OI; CVD; Net Delta; Net Longs/Shorts and (New) pairs
- Operator annotations: none
- What happened (data): Low ~82.7K at 13:48, climb to 83.65K, range, 20:33 drop of ~190 with OI stepping up; right edge 83,326.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C09-01 | MATCH | Header 3m bar 21:15 O83326.3 H83326.3 L83326.2 C83326.3 (13 s old, countdown 02:47) | equals the 21:14 1m close 83,326.3 |
| C09-02 | MISMATCH | VWAP 83461.8, flat blue line far below the 5m/15m VWAP | 00:00Z-anchored VWAP is 83,722.6 (snapshot 83,722.76); 83,461.8 is reproduced (error 0.08) only by anchoring at 06:06Z = first loaded 3m bar (~300 bars): the chart VWAP restarts at the left edge of the loaded history **Feature:** FEAT-08: vwap_00z and vwap_ny from raw 1m, never from chart TF |
| C09-03 | MATCH | 20:33 candle: price drops hard, OI steps up (green) and Net Delta steps down (new shorts) | 3m 20:33 O83480.1 L83292.2 C83317.1 delta -195.2; OI 96,029 (20:30) -> 96,243 (20:35) -> 96,335 (20:40) = +306 in 10 min (price down + OI up) **Feature:** FEAT-05: quadrant5 = (sign ret5, sign dOI5) |
| C09-04 | MATCH | OI climbs from 19:30 to the right edge while price stays in a ~83.3-83.55K range | OI 95,446 (19:30) -> 96,360 (21:10) = +913 (+0.96 %); price 83,269.7-83,569.4; afterwards 21:30 first minute below 83,282.7, 6h low 82,829, 22h low 80,344.8 **Feature:** FEAT-06: oi_build |
| C09-05 | MISMATCH | CVD close -3.902K | cvd_day -6,656; cumulative delta from 06:18Z to 21:14Z = -3,903.8 (anchor consistent with ~300 loaded bars); same effect as C06-05 |
| C09-06 | NOT_IN_DATA | Net Delta -1.056K = Net Longs -455.947 minus Net Shorts 600.54 | identity exact; series not in data **Feature:** FEAT-05 |

### C10  BTCUSDT Binance perp, 15m footprint, legend.coinglass.com (CoinGlass Legend), fifth image 02:47 local

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/bfb6518a-image.png
- Window: IST axis (clock '02:47:29 (UTC+5.5)'): 18:30 IST 2026-10-07 to 02:45 IST 10-08 = 13:00Z to 21:15Z
- Panels and indicators: footprint candles with a delta number above/below each bar, one volume number per price row, red/green highlighted cells (imbalance), dashed last-price line
- Operator annotations: none (dashed green line is the last price 83,330.1)
- What happened (data): Same session as C06: -785 delta at the 13:45Z low, recovery to 83,653.6, the 20:15Z spike to 83.57K and the 20:30Z drop.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C10-01 | MATCH | Footprint page clock '02:47:29 (UTC+5.5)': x-axis is IST (bar label 02:45 = 21:15Z); the TradingView pages are UTC | bar-by-bar delta labels only match orderflow_live when the axis is shifted by -5:30 (33 of 33 closed bars) |
| C10-02 | MATCH | Per-bar delta labels for 34 bars 18:30 IST .. 02:45 IST (e.g. -365.02, -539.00, +305.18, -785.18 ... -140.59, -5.03) | orderflow_live delta summed per 15m bar equals the label to <= 0.07 BTC for 33 closed bars (largest gaps -144.60 vs -144.62, 130.70 vs 130.76, -203.00 vs -203.07); last bar is forming: -5.03 at 21:17:29 vs ours -5.77 over 21:15-21:16 **Feature:** per-bar delta = sum of 1m delta |
| C10-03 | MATCH | Bar 19:15 IST (13:45Z): delta -785.18 with a green body and a long lower wick to 82,706.2 | 15m 13:45 O83052.9 H83358.0 L82706.2 C83145.1, delta -785.18 (ours -785.18); price then +947 by 16:30Z (high 83,653.6 labelled at the top of the chart) **Feature:** FEAT-04: delta15 z<=-3, close>open, lower wick>=0.5*range [HYPOTHESIS] |
| C10-04 | MATCH | Bar 01:15 IST (19:45Z): delta -567.2 on a tiny body | 15m 19:45 O83415.9 H83415.9 L83272.1 C83399.3 (-16.6) delta -567.22; next bars +29.3, +30.1 reach 83,569.4 (20:17Z) then the 20:30 bar -233.5 **Feature:** FEAT-04 |
| C10-05 | NOT_IN_DATA | Cells highlighted red/green inside bars (imbalance flags) and one number per row; row height looks like ~USD 15 | orderflow_live keeps per-1m buckets of USD 10 with buy/sell volume and a per-minute POC only; no multi-minute footprint, no imbalance flags; the single number per row and the highlight rule are not recoverable from the picture **Feature:** FEAT-10 |
| C10-06 | MATCH | Labels 83,653.6 (top) and 82,706.2 (bottom) | session.high 83,653.6 (16:30Z) and session.low 82,706.2 (13:48Z) in snapshot 21:13:12 |

### C11  BTCUSDT Binance perp, 1H footprint, same page (sixth image, 02:46:56 IST)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/e4ec30ad-image.png
- Window: IST axis, hour bars start at :30 IST: 18:30 IST = 13:00Z .. 02:30 IST = 21:00Z
- Panels and indicators: footprint candles (hourly), one number per row with highlighted cells, delta per bar, last price 83,325.8
- Operator annotations: none
- What happened (data): Hourly deltas -1.38K, -268, +444, -596, -317, +547, -676, -235, -147 (13:00Z..21:00Z).

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C11-01 | MATCH | Header 1H bar 21:00Z O83388.3 H83411.2 L83282.7 C83325.8 V36.04M Amplitude 128.5; hour bars start at :30 IST | O/H/L equal the 15m 21:00 bar; H-L = 128.5; USD volume 21:00-21:16 = 36.05M (chart 36.04M) |
| C11-02 | MATCH | Hourly delta labels -1.38K, -268.15, +444.16, -595.72, -317.22, +546.73, -676.26, -234.88, -146.56 (13:00Z .. 21:00Z) | ours: -1,384.0, -268.15, +444.17, -595.72, -317.22, +546.60, -674.62, -234.87, -146.4 (21:00-21:16); worst gap 1.64 BTC at 19:00Z (minute-boundary trades) |
| C11-03 | NOT_IN_DATA | Large single-row prints, e.g. 197.58 / 195.25 / 162.61 sell rows in the 13:00Z hour and 161.62 in the 15:00Z hour | our fp has USD 10 buckets per minute; rows of the chart are a different size, so a row value cannot be reproduced **Feature:** FEAT-10 |

### C12  BTCUSDT Binance perp, 5m footprint, same page (seventh image, 02:48:08 IST)

- File: C:/Users/E-ngineers/.claude/uploads/bcdd21c8-fadf-43b4-b061-adc5c5a63625/e85d2233-image.png
- Window: IST axis: 01:20 IST to 02:45 IST 10-08 = 19:50Z to 21:15Z
- Panels and indicators: footprint candles (5m), delta per bar, one number per row with highlights, last price 83,339.7
- Operator annotations: none
- What happened (data): 20:15-20:20Z spike to 83,569.4, 20:30Z bar -187 with sell cells down to 83.28K, flat after.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C12-01 | MATCH | Delta labels for 18 bars 01:20 IST .. 02:45 IST (-145.97, -144.41, +49.32, -28.25, +8.27, +22.60, -29.27, +36.77, -187.18, ... +3.08) | orderflow_live 5m delta equals the label to <= 0.02 BTC for 17 closed bars (e.g. 20:30Z -187.18, 21:00Z -108.02); last bar forming (+3.08 vs ours +2.32 for three minutes) |
| C12-02 | MATCH | Labels 83,569.4 (top) and 83,272.1 (bottom) | 1m high 83,569.4 at 20:17Z; low 83,272.1 is the low of the 19:45Z 15m bar (minute not pinned) |
| C12-03 | MATCH | 20:30Z bar (red, delta -187.18): column of sell-highlighted cells in the lower two thirds | fp $10 buckets for 20:30-20:34: sell >= 3x buy in 9 consecutive rows 83,490..83,410 (e.g. 83,430: 0/20.45, 83,420: 0/30.34, 83,410: 3.75/53.08); buy-dominant rows only at 83,510-83,520 **Feature:** FEAT-10: stacked(t) = >=3 consecutive $10 rows with sell>=3*max(buy,eps) [HYPOTHESIS] |
| C12-04 | MISMATCH | Numbers in the cells of the 20:30Z bar sum to 228 BTC | bar volume is 538.1 BTC (buy 175.5, sell 362.6): the single number per row is neither total, buy nor sell volume; semantics unknown |

## 3. Skipped (not trading charts)

| Id | File | What it is |
|---|---|---|
| S01 | uploads/07ecf51c-b3a8-4515-833d-4a18c6a0a767/3afdcb12-image.png | Claude desktop app, project 'Crypto Buy System' overview (2026-10-06 20:11 local). Not a chart. |
| S02 | uploads/b380b952-3615-44b6-ae8d-822a24c66584/3afdcb12-image.png | Byte-identical copy of S01 (md5 6d5d4819...). Not a chart. |
| S03 | uploads/5b76bd67-da41-4b0e-96b9-72c9c621f73d/b4608b57-image.png | Claude desktop app, thread 'Backtesting tasks and pipeline' (2026-10-06 22:51 local). Not a chart. |
| S04 | uploads/db871a23-aaab-43cd-9915-92f150a46bd9/b0c6b257-image.png | Spreadsheet of exchange account transactions (BTC-PERP trades, transfer, settlement; times are mm:ss with no date). Not a chart; not analysed. |
| S05 | Temp/claude/C--...BinanceDataFeed/b6f0305e-3b69-47e6-9b36-510bdb4c1a17/images/1.png | DeepSeek chat page with the Claude side panel. Not a chart. |
| S06 | Temp/claude/F--AIBridge/00a58c90-.../images/1.png | chrome://extensions page. Not a chart. |
| S07 | Temp/claude/F--AIBridge/00a58c90-.../images/2.png | Chrome Web Store page for the Claude extension. Not a chart. |
| S08 | Temp/claude/F--AIBridge/00a58c90-.../images/3.png | Chrome Web Store page with the Claude side panel and DeepSeek tabs. Not a chart. |
| S09 | Temp/claude/F--AIBridge/00a58c90-.../images/4.png | Chrome new-tab page with the Claude side panel. Not a chart. |
| S10 | Temp/claude/F--AIBridge/00a58c90-.../images/5.png | DeepSeek 'Tool loop test first block' with AIBridge auto-run strip. Not a chart. |
| S11 | projects/F--AIBridge/00a58c90-.../tool-results/mcp-claude-in-chrome-blob-1791455249644-8o1wtb.jpg | DeepSeek AIBridge loop screenshot. Not a chart. |
| S12 | projects/F--AIBridge/00a58c90-.../tool-results/mcp-claude-in-chrome-blob-1791455255831-zpynbn.jpg | DeepSeek AIBridge loop screenshot. Not a chart. |
| S13 | projects/F--AIBridge/00a58c90-.../tool-results/mcp-claude-in-chrome-blob-1791455364415-c4yea8.jpg | DeepSeek AIBridge loop screenshot. Not a chart. |

## 4. Ranked list: 10 most testable features (all HYPOTHESIS)

Ranking = data already on disk, causal at bar close, fewest free parameters, and direct link to a chart observation. Backtest definitions of legs, catchability, costs and splits are in PLAN sections 3-4; none of these is a trading parameter.

| Rank | Id | Feature | Data on disk now | Main gap |
|---|---|---|---|---|
| 1 | FEAT-01 | oi_flush_5m (price, delta and OI fall together, abnormally large vs adjacent bars) | oi_5m_30d (from 09-05, holes), metrics to 09-26, orderflow_live from 09-29 | OI holes F-BT-11 |
| 2 | FEAT-02 | pivot_sweep_reclaim (local low/high taken, then reclaimed) | klines 1m 2022..2026-10-07, orderflow_live | none |
| 3 | FEAT-03 | post_flush_absorption (sells absorbed after a flush, low holds) | orderflow_live (delta, max_trade, thr99) from 09-29 | short history; aggTrades on F: for older |
| 4 | FEAT-04 | delta_divergence_bar (footprint absorption proxy from 1m columns) | orderflow_live delta from 09-29; klines taker volume gives delta for the whole archive | none for delta, wick rule is price only |
| 5 | FEAT-05 | net_positioning_proxy (CoinGlass Net Delta / Net Longs / Net Shorts rebuilt) and 5m quadrant | oi_5m_30d + klines | definition inferred from 2 bars; OI holes |
| 6 | FEAT-06 | oi_build (positions building inside a quiet range) | oi_5m_30d + klines | OI holes; one example |
| 7 | FEAT-07 | poc24 and naked POC (coarse-row POC, per-day rays, first revisit) | orderflow_live fp (USD 10 buckets) from 09-29; klines for coarse versions | fp history short; row count sensitivity |
| 8 | FEAT-08 | vwap_00z and vwap_ny (both anchors from raw 1m) | klines 1m | DST anchor for 2026-11-01 |
| 9 | FEAT-09 | bigprint_burst (clustered large prints) | orderflow_live b999 columns from 09-29 | short history |
| 10 | FEAT-10 | stacked_imbalance (footprint imbalance rebuilt from fp) | orderflow_live fp (1m buckets) | chart rule and row size unknown |

### FEAT-01  oi_flush_5m (price, delta and OI fall together, abnormally large vs adjacent bars)

- Formula (HYPOTHESIS): dOI5(t)=OI(t+5m)-OI(t) from oi_live/oi_5m_30d.csv sumOpenInterest (stamp = bar open); delta5(t)=sum of the five 1m `delta` of orderflow_live in [t,t+5m); ret5(t)=close/open-1 of the 5m bar; z(x)=(x-median(x over the prior 288 bars))/(1.4826*MAD). FLUSH(t) = z(dOI5)<=-4 AND z(delta5)<=-4 AND ret5<0, fired at t+5m. Mirror (short squeeze): z(dOI5)<=-4, z(delta5)>=+4, ret5>0.
- Chart/data evidence: Oct 5 14:30 bar z -22.9 / -34.6; Oct 7 13:45 z -5.8 / -8.1; 10 qualifying 5m bars on 10-04..10-07 (10-04 16:00, 23:35; 10-05 02:30, 04:20, 08:45, 09:15, 14:30, 15:30; 10-07 10:05, 13:45); 4h: Sep 23 12:00 (OI -5.4 %, price -1.9 %), Sep 24 08:00.
- Caveats: -4 and 288 are analysis settings, not tuned values. OI holes (F-BT-11) remove 10-06 and 10-07 00:00-07:30 until refilled; metrics cover to 09-26.

### FEAT-02  pivot_sweep_reclaim (local low/high taken, then reclaimed)

- Formula (HYPOTHESIS): On 5m bars: L(t)=min(low[t-12..t-1]); SWEEP_LOW(t) = low[t] < L(t); RECLAIM = exists k in {1,2}: close[t+k] > L(t); fire at the close of the first reclaim bar. Mirror for highs with H(t)=max(high[t-12..t-1]). Variant OI_POKE: OI(t)-OI(t-6 bars) > 0 during the sweep bar (new positions on the break).
- Chart/data evidence: Oct 7 13:45: low 82,706.2 vs prior-12-bar low 83,038.1 (13:40), -331.9; close 82,907.0 (below), 13:50 close 83,300.4 (reclaim, fire 13:55); then +947 to 83,653.6. Oct 5: 14:07-14:08 high 86,683.9 above the 08Z high 86,463 with OI +583 (13:50 -> 14:30), flush at 14:30. Snapshot sweep flag shows none / latched (F-BT-13).
- Caveats: 12 bars, k<=2 and zero buffer are analysis settings. Pivot-fractal versions (n bars each side) are a variant; the 13:40 bar is not a fractal low because 13:45 is lower.

### FEAT-03  post_flush_absorption (sells absorbed after a flush, low holds)

- Formula (HYPOTHESIS): After a FLUSH bar f (FEAT-01): A = sum(delta[f+1..f+3]) over three 5m bars; fire at close of f+3 if A > 0 AND min(low[f+1..f+3]) >= low[f]. Optional strength: max(max_trade over f+1..f+3) >= thr99 of the day (column thr99).
- Chart/data evidence: Oct 5: flush low 85,400.1 at 14:34; delta 14:35-14:37 +542, 1m max_trade 201.8 BTC at 14:36; low not broken through 14:54 (broken 15:32). Oct 7: 13:48 low 82,706.2 never re-broken that day; 13:50 bar delta +284.
- Caveats: Three bars is an analysis setting. Direction of any edge is not assumed; outcome columns per PLAN section 3.

### FEAT-04  delta_divergence_bar (footprint absorption proxy from 1m columns)

- Formula (HYPOTHESIS): On 15m bars (sum of 1m): d=sum(delta); z(d) vs prior 96 bars (median/MAD); LONG_ABSORB = z(d)<=-3 AND close>open AND (min(open,close)-low) >= 0.5*(high-low); SHORT_ABSORB mirrored (z>=3, close<open, upper wick >= 0.5*range). Fire at bar close.
- Chart/data evidence: 13:45Z bar: delta -785.18, green body, wick to 82,706.2, then +947 (footprint C10-03). 19:45Z bar: delta -567.2 on a -16.6 body (C10-04).
- Caveats: Thresholds are analysis settings. The 13:45 bar also passes FEAT-02; keep them separate columns.

### FEAT-05  net_positioning_proxy (CoinGlass Net Delta / Net Longs / Net Shorts rebuilt) and 5m quadrant

- Formula (HYPOTHESIS): nd5(t)=sign(close-open)*abs(OI(t+5m)-OI(t)); ND_cum(W)=sum of nd5 over the last W bars. Quadrant5(t)=(sign(ret5), sign(dOI5)): (+,+) new longs, (-,+) new shorts, (+,-) short cover, (-,-) long liquidation; replaces the hourly delta_state. NL/NS split by quadrant, ND=NL-NS (identity seen on 4 screenshots).
- Chart/data evidence: Oct 5 14:50 bar: rule -51.5 vs chart -50.9; Oct 7 21:10 bar: -12.4..-20 vs chart -18; Oct 7 20:30 bar: price down, OI +213 -> new shorts (C09-03). Net Delta is NOT order-flow delta (our delta for the Oct 5 bar is +17.7).
- Caveats: HYPOTHESIS: two bars verified, one bar (3m 21:15, flat price) not reproduced. Definition inferred from screenshots only.

### FEAT-06  oi_build (positions building inside a quiet range)

- Formula (HYPOTHESIS): On 5m bars, window 24 bars (2h): OI_BUILD(t) = OI(t)/OI(t-24)-1 >= +0.8 % AND (max(high)-min(low))/close over the window <= 0.4 %. Companion: sign of the later break (reported, not assumed).
- Chart/data evidence: Oct 7 19:30 -> 21:10: OI +913 (+0.96 %) with price in 83,269.7-83,569.4 (0.36 %). Afterwards (data fact): first minute below 83,282.7 at 21:30, 6h low 82,829, 22h low 80,344.8.
- Caveats: 0.8 % and 0.4 % are analysis settings; one example only, so expect to sweep thresholds under PLAN section 4.

### FEAT-07  poc24 and naked POC (coarse-row POC, per-day rays, first revisit)

- Formula (HYPOTHESIS): poc24(a,t): between min(low) and max(high) since anchor a (00:00Z day, or fixed range), cut 24 equal rows; row volume = sum of fp bucket volume (orderflow_live `fp`, USD 10 buckets); POC row = argmax, report row mid and the second-highest row. Naked(d)=poc24 of day d with no 1m bar touching it since 00:00Z of d+1; first revisit = first 1m bar with low<=poc<=high. Also dist_poc24 in ATR.
- Chart/data evidence: Chart POC rays reproduce: Oct 4 85,200-85,288 (chart ~85,246), Oct 5 86,239.5-86,306.5 (~86,270) and full-day 85,857-85,943 (~85.9K), Oct 6 85,537-85,603 (~85.57K), Oct 7 83,300.6-83,419.5 (~83,333). Java POC misses by 300-1,300 (F-BT-09).
- Caveats: 24 rows is the VPVR default seen on the vvp charts; row count changes the POC on bimodal days (Oct 5: 5-67 USD rows give 85,500 or 86,2xx), so report the top two rows. fp exists from 2026-09-29 only in orderflow_live (aggTrades 2024-12.. on F: for older).

### FEAT-08  vwap_00z and vwap_ny (both anchors from raw 1m)

- Formula (HYPOTHESIS): vwap_a(t)=sum(vol*hlc3)/sum(vol) over 1m rows from anchor a to t, a = 00:00Z and a = US cash open (13:30Z summer, 14:30Z after DST end); dist_a=(close-vwap_a)/ATR.
- Chart/data evidence: Oct 7 21:13: vwap_00z 83,722.6 (snapshot 83,722.76), vwap_ny 83,205.7; Oct 5 14:53: 86,073.9 vs 85,968.3. Chart values: 15m 83,726.8, 5m 83,720.7, 4h 83,782.9, 3m 83,461.8 (loaded-history anchor).
- Caveats: Deterministic; the point is to stop reading VWAP off a chart timeframe. F-BT-12.

### FEAT-09  bigprint_burst (clustered large prints)

- Formula (HYPOTHESIS): bp(t)=sum over 5 minutes of b999_sell_n (and b999_buy_n); BURST = bp>=10 AND bp>=3*median(bp over the prior 288 five-minute windows); thr999 is the file's own 30-day threshold (column thr999).
- Chart/data evidence: Oct 5 14:30-14:34: b999_sell_n 3,4,4,13,13, max_trade 99.6 BTC (14:34); 14:36 max_trade 201.8 BTC with delta +370.
- Caveats: 10 and 3x are analysis settings. Columns exist only since 2026-09-29; the chart itself has no big-trade layer, so this is a data-side addition.

### FEAT-10  stacked_imbalance (footprint imbalance rebuilt from fp)

- Formula (HYPOTHESIS): For a bar (5m/15m) sum fp over its minutes per USD 10 row: SELLIMB(row) = sell >= 3*max(buy,eps); STACKED = >=3 consecutive rows; same for buys. Count rows and report the price span.
- Chart/data evidence: Oct 7 20:30Z 5m bar: 9 consecutive sell-dominant rows 83,490..83,410 (C12-03); chart bar shows a column of sell-highlighted cells and delta -187.18.
- Caveats: 3x is an analysis setting; the chart's highlight rule and row size (~USD 15) are unknown, so a match is directional only. Lowest rank: needs the most unknowns resolved.

## 5. Findings appended to FINDINGS.md

| Id | Severity | One line |
|---|---|---|
| F-BT-09 | HIGH | Java buildVp does not conserve volume; POC/VAH/VAL biased to fast-move bars (300-690 off trade-level) |
| F-BT-10 | MEDIUM | snapshot OI is hourly-stepped, blind to the 1m/5m OI flush |
| F-BT-11 | MEDIUM | OI recorder holes, 46 h incl. all of 10-06 |
| F-BT-12 | MEDIUM | vwap.price 00:00Z-anchored vs session.vwap_anchor_utc 13:30Z |
| F-BT-13 | LOW | sweep flag latches on prior-day H/L breach, local pivots invisible |
| F-BT-14 | MEDIUM | NakedPocTracker has no writer, list frozen at 2026-08-28 |
| F-BT-15 | LOW | first snapshot after 00:00Z has a wrong cvd.value (3 of 3 testable days) |
| F-BT-16 | LOW | snapshot file date is IST; footprint pages IST; snapshots miss 88.7 h |
| F-BT-17 | INFO | orderflow_live vs klines boundary differences, not a defect |

Reproducible audit script for the volume-profile finding: MyTradingSys/backtest/bigtrade/obs_vp_check.py (read-only). No live-path file was edited, moved or restarted; no orders; no .secrets/.env read. All Java findings are escalated, none fixed here.

## 6. Limits

- Pixel reads of rays, panel levels and unlabeled candles are approximate; every numeric check above uses file data, not pixels.
- CoinGlass OI differs from Binance 5m history by 0.01-0.03 %; OI for 10-06 and 10-07 00:00-07:30 is not on disk.
- The Net Delta rule and the footprint cell semantics are inferred from screenshots only.
- C01-C03 (Aug 31) are older VVP-protocol images; their OI check uses Dumps metrics, their CVD cannot be compared (anchor).
- Not checked: HTF structure.1d/1w staleness (snapshots 10-07 21:13 and 10-08 19:39 both show structure.1d.stale True), the Net Longs(New)/Net Shorts(New) definitions, the 4h-chart per-day profile values.
- 2026-10-18: Net Delta panel regression (card identify-the-coinglass-net-delta-panel-u): candidate A sign(close-open)*abs(dOI) fits 5m/8h/12h bars (ratios 0.90-1.03) but lacks 1m/3m OI data, while trade delta (perp/spot) diverges 0.06-13.8x; verdict UNIDENTIFIED (n=7). See MyTradingSys/research/netdelta_panel_2026-10-18/RESULT.md.

