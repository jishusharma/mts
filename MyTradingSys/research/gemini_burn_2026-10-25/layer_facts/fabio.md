# Layer Fact Sheet: fabio (order-flow layer family)

> **Claude review 2026-10-26** (`MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`): content errors below are fixed; about 75; the analyst name "Fabio Valentini" is sourced at `MyTradingSys/research/fabio_asr_2026-10-16/ASR_EXTRACTION_ADDENDUM.md:14`, not at the code lines cited next to it line cites drift from trunk (content true, line off) and are listed in that report, not rewritten here. Treat any line number as approximate (+-15).

Facts compiled from repository files only for the layer review (card `layer-review-after-simulator`).
No verdict is given on keeping, dropping, demoting, or parking any layer.
Every fact line is tagged with its concrete repo `file:line` or marked `NOT_IN_DATA`.

---

## 1. fabio_cvd_absorption

### Origin
- Analyst/source: Fabio Valentini [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:3-4`]
- Quoted source: "FAB-007 CVD-vs-price divergence absorption detector. This implements FAB-007 from the extract verbatim: 'CVD makes a lower low while price is still on the same level as before' = passive buyers absorbing aggressive sellers (bullish)." [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:3-6`]
- Secondary quote / rule catalog: FAB-007 (o-w5Gxss6T0) cited in rule FR-16 ("Absorption: delta in, price flat; CVD divergence; heavy absorption") [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md:22`]
- Symmetric extension: "The mirror case (CVD higher high, price holds the prior high -> bearish) is implemented as a documented symmetric extension." [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:6-7`; bearish rule at `:65-68`]

### Parameters
- `left`: swing width lookback left, default 2 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:46`]
- `right`: swing width lookback right, default 2 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:46`]
- `use_body`: whether to use bar body for swings, default True [OURS: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:46`]
- `price_tolerance`: tolerance for price holding previous level, default 0.001 (0.1%) [OURS: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:46`]
- Grid parameters: swing width left=right in {2, 3, 5} x price_tolerance in {0.05, 0.1, 0.2, 0.5}% (12 variants) [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:12-13`]
- Per-bar delta formula: `2 * bar['tbv'] - bar['v']` [OURS: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:9-11`]
- CVD anchor / reset point: reset once at the start of input; no session reset [OURS / UNDEFINED in source: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:13-15`]

### Backtests
- Backtest report: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md` [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:1`]
- Data: BTCUSDT 1m resampled to 5m/15m/1h, 2022-01-01..2026-09-26 (2,491,200 bars) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:4-5`]
- Fee-net: Yes, fees 0.10% round trip subtracted from mean return [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:9-10`]
- Split: Chronological 70% IS / 30% OOS per timeframe [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:6`]
- Horizon h=5 OOS trades & metrics:
  - 5m (chosen w5, tol 0.1%): IS n=3373 (h5 gross +0.005%), OOS n=1639 (h5 gross +0.000%, net -0.100%, PBO 0.683) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:27`]
  - 15m (chosen w3, tol 0.2%): IS n=2146 (h5 gross -0.002%), OOS n=982 (h5 gross +0.001%, net -0.099%, PBO 0.330) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:28`]
  - 1h (chosen w5, tol 0.05%): IS n=228 (h5 gross +0.067%), OOS n=109 (h5 gross -0.042%, net -0.142%, PBO 0.333) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:29`]
- Related report: `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md` (1m & 5m price vs CVD divergence backtest on BTCUSDT 2022-01..2026-10-14; fee-net 0.05%/side; 0 of 12 arms pass pre-registered mark) [SOURCED: `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:8-37`]

### Known Bugs & Rulings
- B102: Offline session models anchor NY/London at fixed UTC minutes (no DST); wrong by 1 h on ~40% of days (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- B103: Backtest funding cost is silently 0 outside the locally loaded funding range (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- Fixed-horizon caveat: FABIO_L1 evaluated symmetric close-to-close returns at fixed horizons without state, location, stop, or target management [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:26-30`]

### Confluence
- Meant to confirm / be confirmed by:
  - Confirms failed auction and day direction per rule FR-19 [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md:25`]
  - Reuses swing detection `find_swings` from `cc_structure` (CryptoCred layer) [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:17`, `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:19`]
  - Cited as potential confirmation for Tom setups ("Fabio's CVD/absorption is what Tom calls 'proof'") [SOURCED: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:80-83`]

---

## 2. fabio_escalation

### Origin
- Analyst/source: Fabio Valentini [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:2-5`]
- Quoted source: "FAB-002 ('aggression that fails to break a protected level = absorption') and FAB-003 ('escalating aggression -- a record-volume, record-delta bar -- into an already-absorbed level = expect a BREAKOUT in the aggressor's direction, not a reversal'). Both are quoted UNDEFINED on exact thresholds ('really aggressive' delta size, how many attempts, 'all-time high on volume' reference window) -- every threshold below is this module's own explicit grid parameter, not from the video." [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:2-7`]
- Rulebook references: FR-18 ("Escalating aggression into absorbed level -> breakout", citing FAB-003) and FR-16 (citing FAB-002) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md:22`, `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md:24`]

### Parameters
- `left`: swing lookback left, default 2 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- `right`: swing lookback right, default 2 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- `use_body`: whether to use bar body for swings, default True [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- `level_tolerance`: tolerance for being at level, default 0.001 (0.1%) [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- `aggression_k`: multiplier on average delta to qualify as aggressive, default 2.0 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- `record_lookback`: lookback window to calculate average delta, default 20 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:13`]
- Grid parameters: level_tolerance in {0.1, 0.2}% x aggression_k in {1.5, 2, 3} x record_lookback in {20, 50} (12 variants) [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:13`]

### Backtests
- Backtest report: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md` [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:1`]
- Data: BTCUSDT 1m resampled to 5m/15m/1h, 2022-01-01..2026-09-26 (2,491,200 bars) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:4-5`]
- Fee-net: Yes, fees 0.10% round trip subtracted from mean return [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:9-10`]
- Split: Chronological 70% IS / 30% OOS per timeframe [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:6`]
- Horizon h=5 OOS trades & metrics:
  - 5m (chosen lt 0.2%, k 3, lb 50): IS n=16999 (h5 gross +0.016%), OOS n=7908 (h5 gross -0.004%, net -0.104%, PBO 0.657) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:30`]
  - 15m (chosen lt 0.1%, k 1.5, lb 50): IS n=2526 (h5 gross +0.039%), OOS n=1095 (h5 gross -0.069%, net -0.169%, PBO 0.174) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:31`]
  - 1h (chosen lt 0.2%, k 1.5, lb 50): IS n=378 (h5 gross +0.146%), OOS n=182 (h5 gross +0.213%, net +0.113%, PBO 0.756) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:32`]
- Secondary report: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-escalation-event-table.md` (DEV 1h 652 escalation events, gross MFE 4.6065R / MAE 3.9069R over 24 bars, descriptive gross excursion, not an edge claim) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-escalation-event-table.md:3`]

### Known Bugs & Rulings
- Caveat in FABIO_L1_REPORT: Escalation is O(swings x bars) in detector; driver ran on disjoint 1000-bar chunks with 500-bar warmup, so level lived at most ~1500 bars, deviating from unbounded spec [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:17-20`]
- Open card `t09-f4-live-window-99-bars-swing-layers`: 99-bar live window misses 68 of 96 escalation signals [SOURCED: `MyTradingSys/system/LAYERS.md:67`]
- B102: Offline session models anchor NY/London at fixed UTC minutes (no DST) (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- B103: Backtest funding cost is silently 0 outside the locally loaded funding range (CLOSED) [SOURCED: `lab_query.py rulings fabio`]

### Confluence
- Meant to confirm / be confirmed by:
  - Reuses swing detection `find_swings` from `cc_structure` (CryptoCred layer) [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:9`]
  - Escalation requires prior absorption at the level before firing the breakout [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_escalation.py:2-4`]
  - Cross-guidance: examined in Tom/Fabio guidance matrix Q33 [SOURCED: `MyTradingSys/system/LAYERS.md:73-78`]

---

## 3. fabio_volume_fvg

### Origin
- Analyst/source: Fabio Valentini [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:2-7`]
- Quoted source: "FAB-005: anchor a FIXED-RANGE volume profile over one swing leg (point A to point B), compute its value area (70% of volume), and the single lowest-volume PRICE LEVEL inside that value area is the 'real fair value gap'. FAB-006: price is expected to react/reject at that level." [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:4-7`]
- Key caveat quoted: "this module only has 1m kline OHLCV (no aggTrades), so volume-at-price is APPROXIMATED by spreading each bar's volume uniformly across its own [low, high] range into price bins" [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:12-15`]

### Parameters
- `n_bins`: number of bins for profile, default 20 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:46`]
- `pct` (argument of `value_area`): value area percentage, default 0.70 (70%) [OURS / SOURCED concept: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:116`; the name `va_pct` exists only in `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:74`]
- `left`, `right`: swing lookback, default 2, 2 [OURS: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:18`]
- `use_body`: whether to use bar body for swings, default True [OURS: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:18`]
- `touch_bars`: first touch within 200 bars [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:14`]
- Fixed grid: 20 bins, 70% VA, swings 2/2, first touch within 200 bars; no grid tuning, compared against random-VA-bin control [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:14-15`]

### Backtests
- Backtest report: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md` [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:1`]
- Data: BTCUSDT 1m resampled to 5m/15m/1h, 2022-01-01..2026-09-26 (2,491,200 bars) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:4-5`]
- Fee-net: Gross returns reported (no grid, compared to random control; fee subtracted = minus 0.10%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:9-10`, `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:38`]
- Split: Chronological 70% IS / 30% OOS [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:6`]
- Results vs Random-VA-bin Control at h=5:
  - 5m bounce: Real IS n=2660 (-0.013%), Real OOS n=1228 (+0.011%) vs Control IS n=2699 (-0.004%), Control OOS n=1222 (-0.003%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:40`]
  - 5m through: Real IS n=2660 (+0.013%), Real OOS n=1228 (-0.011%) vs Control IS n=2699 (+0.004%), Control OOS n=1222 (+0.003%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:41`]
  - 15m bounce: Real IS n=823 (+0.004%), Real OOS n=377 (-0.002%) vs Control IS n=825 (+0.010%), Control OOS n=379 (+0.027%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:42`]
  - 15m through: Real IS n=823 (-0.004%), Real OOS n=377 (+0.002%) vs Control IS n=825 (-0.010%), Control OOS n=379 (-0.027%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:43`]
  - 1h bounce: Real IS n=186 (+0.062%), Real OOS n=93 (+0.274%) vs Control IS n=189 (+0.134%), Control OOS n=91 (+0.130%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:44`]
  - 1h through: Real IS n=186 (-0.062%), Real OOS n=93 (-0.274%) vs Control IS n=189 (-0.134%), Control OOS n=91 (-0.130%) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:45`]
- Secondary report: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-lvn-touch-event-table.md` (DEV 1h LVN touch event table, descriptive event table) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-lvn-touch-event-table.md:1-8`]

### Known Bugs & Rulings
- Caveat: "FVG 'touch' side is not defined in the source, so both readings are reported (bounce = fade the touch, through = continuation); they are exact mirror images" [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:21-22`]
- Caveat: Kline approximation of volume profile instead of true footprint aggTrades [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:12-15`]
- B102: Offline session models anchor NY/London at fixed UTC minutes (no DST) (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- B103: Backtest funding cost is silently 0 outside the locally loaded funding range (CLOSED) [SOURCED: `lab_query.py rulings fabio`]

### Confluence
- Meant to confirm / be confirmed by:
  - Reuses swing detection `find_swings` from `cc_structure` (CryptoCred layer) [SOURCED: `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:18`]
  - Sourced rules contrast: Tom teaches LVN as bounce/fill/revert, while Fabio teaches sweep-then-empty-level fast through [SOURCED: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:42-45`]

---

## 4. fabio_v3

### Origin
- Analyst/source: Fabio Valentini [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:8-12`]
- Quoted source: "FABIO V3 SPEC - trade model as a layer module (location -> context -> trigger -> management). Version: v3.1 (2026-09-30): folds in FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md 5.4 (M1-M8, M10) and the operator decisions on the v3.0 open items... Transcripts raw_transcripts_canonical/<id>_raw.txt: fZ = fZlNGWvd2Ko, ja = jasv3L-d8ZE, 0j = 0jM5Y31YJak, 8C = 8CWKfoSJu3c, LQ = LQvv5xgy_ik." [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:1-10`]
- Trade walkthrough quotes:
  - 0jM5Y31YJak: "the market is balanced at this time... the market is clearly building pressure down... where the big players are pushing the price... confirmation from price was exactly this candle" [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:192-199`]
  - 8CWKfoSJu3c: "the punch to the wall... the last point of aggression of the sellers... to raise the exposure low in the curve... take back control, I want to be out of the market" [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:195-206`]
  - fZlNGWvd2Ko: "capitalize on the failed auction of the seller and then aggression of the level of the buyers... stop loss to zero. Why? Because we already saw that the sellers got stopped again" [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:200-208`]

### Parameters
(Labeled per Section 7.1 Provenance Table, lines 190-232 of `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md`):
- `P01`: S1 balance window `N` in {60, 120, 240} [OURS / NS-grid: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:192`]
- `P02`: `k_bal` 0.8, POC band 0.25 [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:193`]
- `P03`: S2 pressure `p` in {0.05, 0.10}; drift `q` 0.25 [OURS / NS-grid; NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:194`]
- `P04`: S3 `L` 60, `z_hi` in {2.0, 2.5, 3.0}, `r_abs` 0.25, `r_ctl` 1.0 [OURS / NS-grid / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:195`]
- `P05`: Big trade = 99th/99.9th pct, rolling prior 30 d [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:196`]
- `P06`: Tier VR 1.5, 20 d, min 10 [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:197`]
- `P07`: S4 window `m` in {5, 15} (C), 15 [OURS / NS-grid / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:198`]
- `P08`: S5 trigger on the close [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:199`]
- `P09`: S5D / model D failed auction trigger [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:200`]
- `P10`: S6 anchor = last own control [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:201`]
- `P11`: S7 add gate on; VA 70% [SOURCED (add gate) / OURS (VA 70% NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:202`]
- `P12`: S7 off variant [OURS / NS-grid: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:203`]
- `P13`: S8(a) exhaustion decay 15 bars [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:204`]
- `P14`: S8(b) redistribution exit; N 60 [SOURCED (rule) / OURS (N 60 NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:205`]
- `P15`: S8(c) opposite control break exit [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:206`]
- `P16`: S8(d) climax + failed auction exit; 1-bar lookback [SOURCED (rule) / OURS (1-bar NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:207`]
- `P17`: E_opp stop to BE on opposite absorption [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:208`]
- `P18`: E_opp ratchet to pullback [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:209`]
- `P19`: E_own de-risk by stop (not size) [SOURCED (rule) / OURS (stop NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:210`]
- `P20`: Trail after defended break [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:211`]
- `P21`: Management dist, `be_k` in {1.0, 2.0} [OURS / NS-grid: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:212`]
- `P22`: Max adds = 2 (3 entries total) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:213`]
- `P23`: `add_mode` be (default) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:214`]
- `P24`: `add_mode` day (variant) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:215`]
- `P25`: Add cap q1; min add 0.25 q1 [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:216`]
- `P26`: Floor at day R 0 [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:217`]
- `P27`: Carry London profit -> NY; first-leg risk <= closed day profit [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:218`]
- `P28`: Stop after recovery; -1R [SOURCED (stop after recovery) / OURS (-1R NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:219`]
- `P29`: Daily stop -3R [OURS / SAFETY: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:220`]
- `P30`: Max 10 first legs; Dmax 1.0% [OURS / SAFETY; NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:221`]
- `P31`: Stop floor `f` in {0.3%, 0.5%} [OURS / NS-grid: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:222`]
- `P32`: Structural stop behind level + 1 TICK [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:223`]
- `P33`: NY cash-open window 390 min; cutoff 330; window-end exit [SOURCED (NY session) / OURS (window conventions SIM/NS-fixed): `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:224`]
- `P34`: US_CLOSED dates excluded [OURS / SIM: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:225`]
- `P35`: Model A LVN retrace 25% [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:226`]
- `P36`: Model B reclaim 5, rest 3 bars, edge target [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:227`]
- `P37`: Model B trail variant [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:228`]
- `P38`: Model C initial balance 30 min [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:229`]
- `P39`: Model D rest validity 3 bars [OURS / NS-fixed: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:230`]
- `P40`: Day gate `g` in {off, 0.8}, 20 d lookback, open+60 [OURS / NS-grid: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:231`]
- `P41`: Venue fees, slippage, funding, fills, 1 tick stress [OURS / SIM: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:232`]

### Backtests
- Pre-registration and result document: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md` [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:4`]
- Status review document: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md` [SOURCED: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:1`]
- Data: Binance USD-M BTCUSDT 1m order flow bars, IS 266 windows, OOS 120 windows [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:38`]
- Fee-net: Yes. Maker 0.0, taker 0.0005, plus 2 bps slippage per taker leg for the primary figure; 0 and 5 bps slippage also reported (`MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:8-9,43-47`) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:21`, `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:41`]
- Results by model (IS selection frozen; primary readout OOS):
  - Model A (`A|N60|p0.05|f0.003|rest|g0.8`): IS mean +0.0061 (1 trade day); OOS mean 0.0000 at 2 bps, 0 trade days, CI95 [0.0000, 0.0000], DSR 2.43e-27, PBO 0.500 (NOT EVALUABLE / absence of trades) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:39`, `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:19`]
  - Model B (`B|N60|z2|f0.003|rest`): IS mean 0.0000 (0 trade days); OOS mean 0.0000 at 2 bps, 0 trade days, CI95 [0.0000, 0.0000], PBO 1.000 (NOT EVALUABLE / absence of trades) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:40`, `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:20`]
  - Model C (`C|m5|f0.005|rest|g0.8`): IS mean -0.0141 (142 trade days); OOS mean -0.1038 at 2 bps (0 bps -0.0802, 5 bps -0.1391), 79 trade days, CI95 [-0.2087, -0.0053], DSR 7.39e-13, PBO 0.196 (FAIL) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:41`, `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:21`]
  - Model D (`D|N240|p0.05|f0.003|rest`): IS mean +0.0001 (1 trade day); OOS mean 0.0000 at 2 bps, 0 trade days, CI95 [0.0000, 0.0000], DSR 2.43e-27, PBO 0.767 (NOT EVALUABLE / absence of trades) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:42`, `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:22`]
- Holdout status: Holdout 2026-06-26.. was NOT read for Fabio v3 (holdout step was not executed per B147 correction) [SOURCED: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:10`]
- Related report: `MyTradingSys/research/layer_lab/reports/2026-10-23_t02-f3-fixtures-fabio-v3-grid.md` (T02-F3 look-ahead truncation fixtures for Fabio v3 grid) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-23_t02-f3-fixtures-fabio-v3-grid.md:1-5`]

### Known Bugs & Rulings
- B099: OOS pass hung during the initial 2026-10-04 run and had to be killed; re-run performed as a new trial row after fix [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:36-38`]
- B147: Holdout status clarification (corrected false note that holdout was burned for Fabio; holdout was not executed) [SOURCED: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md:10`]
- Declared engine limits: `engine.run` returns first leg only (multi-leg adds not executed); Model B IN_TRADE and Model A confirm IN_TRADE reported unmanaged (0 R); Tier S4 fixed '99' without `prior_vols` [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:30-34`]
- B102: Offline session models anchor NY/London at fixed UTC minutes (no DST) (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- B103: Backtest funding cost is silently 0 outside the locally loaded funding range (CLOSED) [SOURCED: `lab_query.py rulings fabio`]

### Confluence
- Meant to confirm / be confirmed by:
  - Fabio is specified as a standalone layer, explicitly independent of Tom ("Fabio is a separate layer, never a Tom filter") [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:6-7`]
  - Connects order-flow pressure (CVD) and effort-vs-result to location (LVN, balance ranges, failed auctions) [SOURCED: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:1-3`]
  - Confluence matrix evaluated under card Q33 (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md`): no cross-guidance cell survived [SOURCED: `MyTradingSys/system/LAYERS.md:73-78`]

---

## 5. fabio_of

### Origin
- Analyst/source: Fabio Valentini [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:6-8`]
- Quoted source: "Fabio on true order flow (aggTrades) - conditional-model test. Modules: orderflow_bars.py (aggTrades -> 1m order-flow bars), fabio_of_model.py (state/location/trigger/management simulator)... Replaces the fixed-horizon 'every trigger fire' test of FABIO_L1 with the model the videos describe (state -> location -> trigger -> management), simulated bar by bar on 1m." [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:6-8`, `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:4-6`]

### Parameters
- `TICK`: 0.1 USD [OURS / SIM (Binance BTCUSDT tick): `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:34`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:33,232`]
- `TOL`: 0.001 (0.1% location tolerance) [OURS: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:28`]
- `BIN`: 10.0 USD profile bin size [OURS: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:29`]
- `STATE_MIN`: first 15 minutes of session determine balance vs imbalance [OURS: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:30`]
- `RETEST_BARS`: 6 bars max for retest touch [OURS: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:31`]
- `FILL_TF_BARS`: 3 timeframe bars for limit order fill window [OURS: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:32`]
- Session bounds: Asia (00:00-08:00 UTC), London (08:00-13:30 UTC), NY (13:30-21:00 UTC) [OURS / SIM: `MyTradingSys/backtest/layers/fabio/fabio_of_model.py:36`, `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:33-34`]
- Grid parameter space:
  - Timeframe `tf` in {5m, 15m} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49`]
  - Big trade percentile in {99th, 99.9th} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49`]
  - Aggression multiplier `k` in {1.5, 2.5} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49`]
  - Entry in {market, limit} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49`]
  - Management in {plain, trail} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49-50`]
  - Minimum stop in {spec tight stop (1 tick beyond bar extreme), widened stop >= 0.15% of price} [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:49-50`]
- Total variants: 64 true flow variants, 32 proxy control variants [OURS: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:50-51`]

### Backtests
- Backtest report: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md` [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:1`]
- Data: Binance USD-M BTCUSDT aggTrades, 2026-06-01..2026-09-28 (120 days total; June warm-up, active window 90 days: IS 62 days Jul 1-Aug 31, OOS 28 days Sep 1-28) [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:13-15`]
- Fee-net: Evaluated net of fees, but see Fee Note below [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:1-4`]
- Primary results (OOS 28 days, R-multiples):
  - True flow, balance_fade, all sessions (chosen: 15m, p99, k2.5, limit, trail, floor 0.0015): IS n=67 (exp net -0.509R); OOS n=29, win 24%, avg gross R -0.031, exp net R -0.498, PF 0.40, maxDD 14.4R, BE share 21%, PBO 0.11 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:60`]
  - True flow, balance_fade, NY session (chosen: 15m, p999, k1.5, limit, plain, floor 0.0015): IS n=33 (exp net -0.196R); OOS n=22, win 32%, avg gross R +0.367, exp net R -0.099, PF 0.88, maxDD 8.7R, BE share 14%, PBO 0.28 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:61`]
  - True flow, imb_break, all sessions (chosen: 5m, p999, k2.5, mkt, plain, floor 0.0015): IS n=48 (exp net -0.387R); OOS n=37, win 24%, avg gross R +0.088, exp net R -0.426, PF 0.53, maxDD 15.9R, BE share 19%, PBO 0.31 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:64`]
  - True flow, imb_break, NY session (chosen: 5m, p999, k1.5, mkt, plain, floor 0.0015): IS n=31 (exp net -0.594R); OOS n=31, win 29%, avg gross R +0.260, exp net R -0.265, PF 0.67, maxDD 8.2R, BE share 19%, PBO 0.70 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:65`]
  - True flow, combined, all sessions (chosen: 15m, p99, k2.5, limit, trail, floor 0.0015): IS n=89 (exp net -0.513R); OOS n=42, win 29%, avg gross R +0.041, exp net R -0.428, PF 0.43, maxDD 18.0R, BE share 24%, PBO 0.12 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:68`]
  - True flow, combined, NY session (chosen: 15m, p999, k2.5, limit, trail, floor 0.0015): IS n=22 (exp net -0.198R); OOS n=16, win 44%, avg gross R +0.393, exp net R -0.053, PF 0.90, maxDD 4.7R, BE share 19%, PBO 0.20 [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:69`]
- Overall grid survival: 0 of 64 variants net-positive OOS with n >= 30 in any model/scope [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:118`]

### Known Bugs & Rulings
- Fee Note / B081 residue: "results in this report were produced with the legacy fee pair (3.5 bp taker, -1.5 bp maker rebate, per side), not the fees stated in the text below (taker 5 bp, maker 2 bp). The API-verified Deribit schedule (fees.py) is taker 5 bp, maker 0. Correct fees only lower net R, so the 'no edge / insufficient n' verdicts stand. A rerun is needed before any reuse of the numbers." [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:1-4`]
- MSB swing audit #14: Commit 051084e440 fixed MSB to use most recent confirmed swing [SOURCED: `lab_query.py layers:fabio_of`]
- B102: Offline session models anchor NY/London at fixed UTC minutes (no DST) (CLOSED) [SOURCED: `lab_query.py rulings fabio`]
- B103: Backtest funding cost is silently 0 outside the locally loaded funding range (CLOSED) [SOURCED: `lab_query.py rulings fabio`]

### Confluence
- Meant to confirm / be confirmed by:
  - Uses true order flow footprint levels (VAH, VAL, POC, LVN) to place trades, confirming direction via big-trade delta [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:34-43`]
  - Explicit non-confluence rule: "Tom-with-Fabio agreement not computed (no offline Tom detector on these bars); Fabio stays a separate layer and must not gate Tom." [SOURCED: `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md:133-134`]

---

## 6. General Family Ledger Audits & Rulings Summary

- Active rulings for family `fabio` from `scripts/dev/lab_query.py rulings fabio`:
  - `B179` (OPEN, MED): operator: turn the Tom and Fabio layers story (principles and concepts) into a slide deck artifact so the operator can learn what they taught [SOURCED: `lab_query.py rulings fabio`]
  - `B167` (OPEN, MED): PROJECT_VISION.md is stale (last real edit 2026-09-28, 833 commits behind) [SOURCED: `lab_query.py rulings fabio`]
  - `B137` (OPEN, MED): Device roles are undecided after the Qwen lane ended [SOURCED: `lab_query.py rulings fabio`]
  - `B127` (CLOSED, MED): Audit PARTIAL group (e): 13 findings where code exists but test is missing or staged as .new [SOURCED: `lab_query.py rulings fabio`]
  - `B123` (OPEN, MED): Zero-trade and QUIET family follow-ups from 2026-09-30 report (fabio jishu_3 / jishu_4) [SOURCED: `lab_query.py rulings fabio`]
  - `B103` (CLOSED, MED): Backtest funding cost silently 0 outside locally loaded range [SOURCED: `lab_query.py rulings fabio`]
  - `B102` (CLOSED, LOW): Offline session models anchor NY/London at fixed UTC minutes (no DST) [SOURCED: `lab_query.py rulings fabio`]
  - `B095` (OPEN, MED): Per-session cost is visible only inside Claude CLI Status panel [SOURCED: `lab_query.py rulings fabio`]
  - `B090` (OPEN, HIGH): Cloud credit approval plan [SOURCED: `lab_query.py rulings fabio`]
- Ledger frame audit (`MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`):
  - Verdict: FIX-FIRST [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:1`]
  - H1: Date `2026` asserted for Jpd96fLqr5M / DyS79Eb92Ug sessions while contract is Dec-2025 (`NQ-202512`, true date UNKNOWN <= 2025-12-19) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:18`]
  - H2: Entry cells disagree with frame's own STP dollar label (F8, F12, F12-m2, F13, F13-m1) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:19`]
  - H3: F13-x row says `stopped_out_RESOLVED` with Daily P/L delta -$2910 while visible stop label is -$1760 (only 8 of 10 lots covered) [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:20`]
  - M1: F4a/F4b date is screenshot file name, not trade date; scale-in is inference; no stop/target [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:21`]
  - M2: All exit rows are inferred from Daily P/L deltas, not on any frame [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:22`]
  - M3: F2 teaching example without order labels [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:23`]
  - M4: Month-level dates and mixed chart/local clock times [SOURCED: `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md:24`]
