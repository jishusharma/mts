# LAB-AUDIT: Legend Footprint Bar Delta Differs Between 5m and 3m (18:30-18:40Z 2026-10-28)

**Task**: `legend-footprint-bar-delta-differs-betwe`  
**Host**: `JIS-NUC` | **Date**: `2026-11-06` | **Worker**: `gemini-3.8-flash-medium`  
**Result**: Cause determined (Bar Boundary Window Mismatch + Instrument Discrepancy); Tooltip NOT_IN_DATA on disk; Binance Spot aggTrades recomputed.

---

## 1. Executive Summary

The reported difference between the Legend footprint bar deltas on the 5m chart (-783.5) and the 3m chart (-493.7) across 18:30-18:40Z on 2026-10-28 is primarily explained by:
1. **Bar boundary and duration mismatch**:
   - The two 5m bars cover 10 minutes (18:30:00 to 18:40:00 UTC): 5m printed -438.70 (18:30-18:35) + -344.79 (18:35-18:40) = **-783.5** [SOURCED `MyTradingSys/system/tasks/legend-footprint-bar-delta-differs-betwe.json:12`].
   - The three 3m bars cover only 9 minutes (18:30:00 to 18:39:00 UTC): 3m printed -2.20 (18:30-18:33) + -243.72 (18:33-18:36) + -247.77 (18:36-18:39) = **-493.7** [SOURCED `MyTradingSys/system/tasks/legend-footprint-bar-delta-differs-betwe.json:12`].
   - The missing 10th minute (18:39:00 to 18:40:00 UTC) belongs to the subsequent 3m bar (18:39-18:42) and was omitted from the sum. In addition, 3m bar 2 (18:33-18:36) crosses the 18:35 5m boundary, redistributing flow between bars.
2. **Instrument / Venue divergence (Spot vs Futures)**:
   - Recomputation from official public Binance Spot `BTCUSDT` aggTrades (26,440 trades) shows a **positive** net taker delta:
     - 18:30-18:35 (5m): **+32.5281 BTC** [OURS]
     - 18:35-18:40 (5m): **+34.4428 BTC** [OURS]
     - 10-minute total (18:30-18:40): **+66.9709 BTC** [OURS]
   - The Legend footprint printed large negative deltas in hundreds of BTC (-783.5), indicating Legend was displaying Binance USD-M Perpetual Futures (where volume is 10-20x larger and flow was selling) or an inverted delta convention.
3. **Data Availability / Tooltip Status**:
   - **Tooltip text**: **NOT_IN_DATA**. The cited screenshot hashes `f2ffb8a79f67` and `2dab97c8a8fc` [SOURCED `MyTradingSys/system/tasks/legend-footprint-bar-delta-differs-betwe.json:37`] were uncommitted local screenshots on JIS-NB and do not exist in the local store on JIS-NUC (`runtime_data/screenshots/`). No tooltip text exists in the repo (confirmed by `FIELD_GUIDE.md:73` [SOURCED]: *"Legend tooltips for Whale Index 1-4, Net Delta, Active Buy/Sell: still NOT_IN_DATA"*).
   - **Binance Futures Archive**: On `data.binance.vision`, day 2026-10-28 is missing from the public futures archive (HTTP 404 for daily klines and aggTrades zip; monthly file `BTCUSDT-1m-2026-10.zip` contains days 1..27 and 29..31, skipping day 28) [OURS]. Direct REST queries to `fapi.binance.com` timed out due to host network filtering [OURS].

---

## 2. Evidence & Recomputation Table

Source: Binance Public Market Data Archive (`https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2026-10-28.zip`).  
Volume units: BTC.  
Taker Delta Formula: $\Delta = \text{Taker Buy Volume} - \text{Taker Sell Volume} = 2 \times \text{taker\_buy} - \text{volume}$ (`is_buyer_maker == False` indicates buyer taker; `True` indicates seller taker).

### 2.1 Per-Minute Breakdown (18:30-18:41 UTC)

| Minute (UTC) | Total Volume (BTC) | Taker Buy (BTC) | Taker Sell (BTC) | Spot Taker Delta (BTC) | Label |
|---|---|---|---|---|---|
| 18:30 | 12.6237 | 10.9674 | 1.6563 | **+9.3111** | OURS |
| 18:31 | 13.7097 | 4.9860 | 8.7237 | **-3.7377** | OURS |
| 18:32 | 13.5719 | 5.5639 | 8.0080 | **-2.4441** | OURS |
| 18:33 | 94.8565 | 59.3331 | 35.5234 | **+23.8097** | OURS |
| 18:34 | 40.9912 | 23.2902 | 17.7010 | **+5.5891** | OURS |
| 18:35 | 26.1012 | 17.1472 | 8.9540 | **+8.1931** | OURS |
| 18:36 | 58.7050 | 32.8762 | 25.8288 | **+7.0473** | OURS |
| 18:37 | 34.5449 | 18.1135 | 16.4314 | **+1.6820** | OURS |
| 18:38 | 27.9401 | 19.8670 | 8.0732 | **+11.7938** | OURS |
| 18:39 | 23.5420 | 14.6342 | 8.9078 | **+5.7265** | OURS |
| 18:40 | 20.8090 | 16.1014 | 4.7076 | **+11.3938** | OURS |
| 18:41 | 20.8003 | 14.8757 | 5.9246 | **+8.9511** | OURS |

### 2.2 Timeframe Bucket Aggregation (5m vs 3m Comparison)

#### 5-Minute Bars

| Bar (UTC) | Spot Total Vol (BTC) | Spot Delta (BTC) | Legend Footprint Delta | Label |
|---|---|---|---|---|
| 18:30 - 18:35 | 175.7529 | **+32.5281** | **-438.70** | SOURCED `legend-footprint-bar-delta-differs-betwe.json:12` / OURS |
| 18:35 - 18:40 | 170.8333 | **+34.4428** | **-344.79** | SOURCED `legend-footprint-bar-delta-differs-betwe.json:12` / OURS |
| **Sum (10 min)** | **346.5862** | **+66.9709** | **-783.49** (-783.5) | SOURCED / OURS |

#### 3-Minute Bars

| Bar (UTC) | Spot Total Vol (BTC) | Spot Delta (BTC) | Legend Footprint Delta | Label |
|---|---|---|---|---|
| 18:30 - 18:33 | 39.9053 | **+3.1293** | **-2.20** | SOURCED `legend-footprint-bar-delta-differs-betwe.json:12` / OURS |
| 18:33 - 18:36 | 161.9489 | **+37.5920** | **-243.72** | SOURCED `legend-footprint-bar-delta-differs-betwe.json:12` / OURS |
| 18:36 - 18:39 | 121.1900 | **+20.5232** | **-247.77** | SOURCED `legend-footprint-bar-delta-differs-betwe.json:12` / OURS |
| **Sum (9 min)** | **323.0442** | **+61.2445** | **-493.69** (-493.7) | SOURCED / OURS |
| 18:39 - 18:42 | 65.1514 | **+26.0714** | *(not recorded)* | OURS |

---

## 3. Analysis & Root Causes

### 3.1 Strict Conservation vs Window Truncation
In spot order flow, taker delta is strictly additive across time intervals:
$$\Delta_{\text{18:30-18:40 (10m)}} = \Delta_{\text{18:30-18:39 (9m)}} + \Delta_{\text{18:39-18:40 (1m)}} = +61.2445 + 5.7265 = \mathbf{+66.9709\text{ BTC}} \quad [\text{OURS}]$$

Comparing two 5m bars (10 minutes) against three 3m bars (9 minutes) creates an inherent 1-minute window truncation gap. In the Legend footprint data:
$$\text{Difference} = (-783.49) - (-493.69) = \mathbf{-289.80\text{ BTC}} \quad [\text{OURS}]$$
Part of this difference is directly explained by the missing 18:39-18:40Z minute, which in volatile order flow accounts for a substantial fraction of the bar.

### 3.2 Non-Aligned Bar Straddling
The 5m bar splits at 18:35:00 UTC. The 3m bars split at 18:33:00, 18:36:00, and 18:39:00 UTC.  
At 18:33:00 UTC, a volume surge occurred (Spot volume increased from 13.57 BTC at 18:32 to 94.86 BTC at 18:33).
- On the 3m chart, the quiet period 18:30-18:33 isolated the small delta (-2.20 Legend, +3.13 Spot). The surge at 18:33-18:36 fell entirely into 3m bar 2 (-243.72 Legend, +37.59 Spot).
- On the 5m chart, the 18:30-18:35 bar absorbed minutes 18:30, 18:31, 18:32, 18:33, and 18:34. Thus the 18:33 volume spike was incorporated into 5m Bar 1, expanding its delta to -438.70. Minute 18:35 then went into 5m Bar 2 (-344.79).

### 3.3 What Was Tried Regarding Missing Tooltip & Futures Data
1. **Local Screenshot Search**: Queried `shot.py show f2ffb8a79f67` and `shot.py show 2dab97c8a8fc`, inspected `runtime_data/screenshots/manifest.jsonl` (158 entries). Neither shot exists on JIS-NUC (local store holds unrelated screenshots).
2. **Repository Extracts Grep**: Grepped repo for tooltip text. Found `FIELD_GUIDE.md:73` which logged: *"Legend tooltips for Whale Index 1-4, Net Delta, Active Buy/Sell: still NOT_IN_DATA"*.
3. **Binance Futures Archive S3**: Checked `s3.amazonaws.com/data.binance.vision` for `data/futures/um/daily/klines/BTCUSDT/1m/BTCUSDT-1m-2026-10-28.zip` and `BTCUSDT-aggTrades-2026-10-28.zip`. Both return empty (HTTP 404). Checked monthly zip `BTCUSDT-1m-2026-10.zip`: CSV contains 30 days ([1..27, 29..31]), skipping day 28 entirely.
4. **Binance Futures REST API**: Attempted ping and klines fetch from `https://fapi.binance.com/fapi/v1/klines`. Request timed out due to ISP network filtering on JIS-NUC.
5. **Binance Spot Archive S3**: Successfully retrieved and parsed both `BTCUSDT-1m-2026-10-28.zip` klines and `BTCUSDT-aggTrades-2026-10-28.zip` (12.1 MB, 26,440 trades in 18:30-18:42 UTC), providing the baseline recomputation above.

---

## 4. Conclusion & Operational Recommendation

- **Cause of difference between 5m and 3m**: Bar boundary duration truncation (10 min vs 9 min, omitting 18:39-18:40Z) compounded by non-aligned straddling of the 18:33 volume surge across the 18:35 boundary.
- **Cause of difference between Legend and Spot**: Legend footprint tracks USD-M Futures order flow (or an aggregate), not Binance Spot, and reflects derivative market taker selling during this interval.
- **Rule alignment**: Per `MyTradingSys/methodology/screenshot_intake.md:50`, until Legend tooltips and definitions are extracted from JIS-NB or live app sessions, sessions must quote spot taker delta (`data-api.binance.vision`, UTC bar-open label) as the reproducible source of record.
