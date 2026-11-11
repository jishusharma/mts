# Open Interest (OI) Usage & Order-Flow Concepts for BTC (2026-10-30)

Operator ask: Find BTC open-interest teaching (OI + price + delta + funding, liquidation maps) on crypto order-flow channels, as concept rows with verified quotes. Map each concept to a measurement on `F:/MTS/data/binance_metrics`.

Labels:
- SOURCED = verbatim quote from canonical transcript (`[video id]`), verified by `scripts/dev/verify_extract_quotes.py`.
- OURS = our interpretation, structural framework, and metric measurement formula.

---

## 1. Video Inventory & Channel Sweep

Channels and order-flow video corpus surveyed for Open Interest, Funding, Liquidation Cascades, and Order-Flow Liquidity:

| # | Video ID | Channel / Analyst | Title | Length / Words | OI / Liquidation Passages |
|---|---|---|---|---|---|
| 1 | P3rDSh187TE | Krown (Eric Krown) | Why Crypto Drops 10% in Minutes: Liquidation Cascades Explained (Former NYSE ARCA Market Maker) | 7,302 words | SOURCED primary source: 17 OI passages, 21 funding passages, 45 liquidation cascade passages. SOURCED quotes OI-01 to OI-12 below. |
| 2 | Vd83oo_geMk | World Class Edge | THE TRUTH about Heatmap & Liquidity – This is how the World Champion REALLY trades! | 2,670 words | Liquidity heat map mechanics: passive resting orders vs aggressive market orders; stops hunted at extremes. |
| 3 | FawPrRUGNpk | Fabervaale ENG (Fabio) | The Only Liquidity Guide You will Ever Need | 9,900 words | Liquidity pools, heat maps, and reload patterns. (Zero OI: NQ trader; confirmed channel has no OI). |
| 4 | Pz8f0wWW12M | Fabervaale ENG (Fabio) | The Only Orderflow Guide You will Ever Need | 7,800 words | Delta footprint, absorption mid-candle, volume leading price. (Zero OI: NQ futures). |
| 5 | cUTsoU-15Tc | Fabervaale ENG (Fabio) | The Simplest Orderflow Trading Model | 5,100 words | Imbalance tests, range edge absorption/exhaustion. (Zero OI: NQ futures). |
| 6 | Is1HvdfQm5c | HijoTrades (feat. Fabio) | World Cup Trader Reveals His Order Flow LIVE \| Fabio Valentini Full Uncut Session | 17,227 words | Absorption at range highs, CVD leading price. (Zero OI: NQ futures). |
| 7 | DyS79Eb92Ug | Fabio Valentini | Trader Interview / Live Session | 24,641 words | Session CVD reset, liquidation points of protection, failed auctions. (Zero OI: NQ futures). |
| 8 | 0jM5Y31YJak | Fabervaale ENG (Fabio) | My Top 3 Trades from the Competition | 1,400 words | Pressure build-up prior to breakout; CVD divergence. (Zero OI: NQ futures). |
| 9 | o-w5Gxss6T0 | Fabervaale ENG (Fabio) | 3 Order-flow Trading Tricks Exposed! | 1,400 words | Volume spread analysis: effort vs result; failuction. (Zero OI: NQ futures). |
| 10 | 8CWKfoSJu3c | Fabervaale ENG (Fabio) | How I did 20R in one NQ Session | 1,800 words | Value area low absorption clusters; path of least resistance. (Zero OI: NQ futures). |

**Note on Network Fetch Lockout:**
The guarded caption fetcher (`scripts/dev/fetch_captions_timed.py`) reports host JIS-NUC under Level 3/3 lockout until 2026-11-13T13:58:11Z (budget 0/40 in 24h, blocked at IP level). Captions for candidate guest videos (`agjftXPkLUE`, `cLgdXZnLL_0`, `feV6CATGUqo`, `pZai3k1e-Jg`) are deferred until the guard window lifts. Analysis uses canonical local transcripts in `raw_transcripts_canonical/`.

---

## 2. Concept Summary Table

| # | Concept | What the Trader Says (SOURCED) | Plain Meaning (OURS) | Binance Metrics Measurement (`F:/MTS/data/binance_metrics` & 1m Kline) |
|---|---|---|---|---|
| OI-01 | **OI Definition: Leverage Count** | "open interest effectively relates to how many leverage contracts exist right now" [P3rDSh187TE] | OI counts open leveraged contracts, not dollars or volume. Side-neutral: 1 OI = 1 long + 1 short. | `sum_open_interest` on 5m grid; absolute count of open contracts across the venue. |
| OI-02 | **Every Open Contract Is a Future Exit** | "every open and contract is a future exit" [P3rDSh187TE] | Open positions must eventually close via market or limit order. Accumulated OI represents future forced or voluntary closing flow. | Cumulative OI level relative to 30-day baseline; high OI = large inventory of pending market exits. |
| OI-03 | **High Leverage Stacking at Highs** | "when the open interest climbs fast while price climbs, for example, that new leverage stacking in at the highs, well, guess what, every one of those contracts has the liquidation price sitting below" [P3rDSh187TE] | Rapid OI increase during a price rally means aggressive late longs using leverage, placing liquidation stop clusters immediately below the rally base. | `dOI > +0.5%` & `dP > +0.3%` over 30m window; liquidation threshold estimated from leverage bands (e.g. 50x = -2%, 20x = -5%). |
| OI-04 | **OI as Fuel Gauge / Potential Energy** | "you can think of an open interest as like a fuel gauge. Open interest is potential energy" [P3rDSh187TE] | OI does not dictate direction; it indicates volatility potential and move magnitude once triggered. | Volatility expansion expectation: compute forward realized volatility `std(returns, 4h)` conditioned on `sum_open_interest_value` percentile (>80th vs <20th). |
| OI-05 | **Weather Warning: Stacked OI + Hot Funding** | "High open interest plus hot funding doesn't tell you when the avalanche comes. Nothing will of course, but same rule as always. It tells you the mountain is loaded with snow and that avalanche has a potential to come now" [P3rDSh187TE] | High OI + extreme positive/negative funding does not time the top/bottom, but marks fragility where any catalyst sparks a cascade. | Dual filter: `sum_open_interest` in top decile AND 8h funding rate `> +0.03%` (or `count_long_short_ratio > 2.0`). |
| OI-06 | **Anti-Cascade Sizing: Stand Aside at Peaks** | "when open interest gets incredibly high, one of the better strategies is to kind of pull your money away from the market, wait for a cascade to happen, wait for the dust to settle, and then enter on the other side" [P3rDSh187TE] | Avoid chasing breakouts when OI is at extreme highs. De-risk or reduce size, wait for liquidation cascade flush, enter on exhaustion. | Regime veto: reduce leverage / position size when `sum_open_interest` reaches 95th percentile of 30-day rolling window. |
| OI-07 | **Weather Warning Indicator** | "hot funding plus stacked OI is a weather warning" [P3rDSh187TE] | Macro context / risk gauge rather than an execution trigger. Conditions are primed for violent unwinds. | State flag: `weather_warning = (z_score(OI, 30d) > 2.0) & (abs(funding_rate) > 0.02%)`. |
| OI-08 | **Check the Weather Before Sizing** | "Check the weather before you size. Funding and open interest are free" [P3rDSh187TE] | Check funding rates and open interest before determining trade size. Risk sizing should scale inversely with leverage crowding. | Position sizing multiplier: `size_mult = 0.5` if `weather_warning == True` else `1.0`. |
| OI-09 | **Comparative OI Regime** | "And open interest, you know, if that's just normally high, like extremely high compared to whatever you're looking back to over here, yeah, that will also be an issue here" [P3rDSh187TE] | Absolute OI number drifts over cycles; evaluate OI relative to recent lookback baseline (moving averages / percentiles). | Rolling relative OI: `oi_ratio = sum_open_interest / mean(sum_open_interest, 20d)`. |
| OI-10 | **V-Shaped Cascades: Involuntary Deleveraging** | "that's why cascades so often end up in V-shaped recoveries once the borrowed positions are gone there's nobody left who actually wanted to sell" [P3rDSh187TE] | Cascades are involuntary liquidations, not organic selling. Once leveraged inventory is purged, absence of natural sellers creates sharp V-reversals. | Cascade flush signature: `dOI <= -2.0%` within 30m accompanied by sharp price drop, followed by taker buy ratio (`sum_taker_long_short_vol_ratio > 1.2`) marking bounce. |
| OI-11 | **Liquidation Prints Carry No Opinion** | "a liquidation print carries no opinion. The seller didn't decide anything" [P3rDSh187TE] | Forced liquidations reflect algorithmic stop executions, not informed conviction. Treating liquidation volume as organic trend continuation is a mistake. | Price recovery after OI flush: measure 1h forward return from bar where `dOI` drops > 1.5% with price below lower 2-sigma Bollinger Band. |
| OI-12 | **Liquidation Heat Map & Margin Buffer** | "Liquidation price should always be far from the pools. You should be actively, proactively managing risk" [P3rDSh187TE] | Identify where high-density liquidation pools cluster; ensure stops/liquidation prices are placed outside vulnerable liquidity pockets. | Estimate liquidation bands using `count_toptrader_long_short_ratio` and historical high/low swing clusters; buffer protective stops beyond high-OI nodes. |

---

## 3. Verified Quote Blocks (Scripts / Verification)

All quotes extracted verbatim from `raw_transcripts_canonical/P3rDSh187TE_raw.txt`. Verified by `scripts/dev/verify_extract_quotes.py`.

### OI-01: OI Definition: Leverage Count

> "open interest effectively relates to how many leverage contracts exist right now"

**Source GPS: P3rDSh187TE | MIDDLE**

### OI-02: Every Open Contract Is a Future Exit

> "every open and contract is a future exit"

**Source GPS: P3rDSh187TE | MIDDLE**

### OI-03: High Leverage Stacking at Highs

> "when the open interest climbs fast while price climbs, for example, that new leverage stacking in at the highs, well, guess what, every one of those contracts has the liquidation price sitting below"

**Source GPS: P3rDSh187TE | MIDDLE**

### OI-04: OI as Fuel Gauge / Potential Energy

> "you can think of an open interest as like a fuel gauge. Open interest is potential energy"

**Source GPS: P3rDSh187TE | MIDDLE**

### OI-05: Weather Warning: Stacked OI + Hot Funding

> "High open interest plus hot funding doesn't tell you when the avalanche comes. Nothing will of course, but same rule as always. It tells you the mountain is loaded with snow and that avalanche has a potential to come now"

**Source GPS: P3rDSh187TE | MIDDLE**

### OI-06: Anti-Cascade Sizing: Stand Aside at Peaks

> "when open interest gets incredibly high, one of the better strategies is to kind of pull your money away from the market, wait for a cascade to happen, wait for the dust to settle, and then enter on the other side"

**Source GPS: P3rDSh187TE | END**

### OI-07: Weather Warning Indicator

> "hot funding plus stacked OI is a weather warning"

**Source GPS: P3rDSh187TE | END**

### OI-08: Check the Weather Before Sizing

> "Check the weather before you size. Funding and open interest are free"

**Source GPS: P3rDSh187TE | END**

### OI-09: Comparative OI Regime

> "And open interest, you know, if that's just normally high, like extremely high compared to whatever you're looking back to over here, yeah, that will also be an issue here"

**Source GPS: P3rDSh187TE | END**

### OI-10: V-Shaped Cascades: Involuntary Deleveraging

> "that's why cascades so often end up in V-shaped recoveries once the borrowed positions are gone there's nobody left who actually wanted to sell"

**Source GPS: P3rDSh187TE | BEGIN**

### OI-11: Liquidation Prints Carry No Opinion

> "a liquidation print carries no opinion. The seller didn't decide anything"

**Source GPS: P3rDSh187TE | END**

### OI-12: Liquidation Heat Map & Margin Buffer

> "Liquidation price should always be far from the pools. You should be actively, proactively managing risk"

**Source GPS: P3rDSh187TE | END**

---

## 4. Mapping Concepts to MTS Binance Metrics Archive

The Binance USD-M metrics archive (`F:/MTS/data/metrics/BTCUSDT` / `F:/MTS/data/binance_metrics`) provides 5-minute snapshots with fields:
- `create_time`: Timestamp UTC.
- `sum_open_interest`: Aggregate open interest in BTC contracts.
- `sum_open_interest_value`: Aggregate open interest in USDT value.
- `count_toptrader_long_short_ratio`: Top trader account ratio (longs/shorts).
- `sum_toptrader_long_short_ratio`: Top trader position size ratio.
- `count_long_short_ratio`: Global account long/short ratio.
- `sum_taker_long_short_vol_ratio`: Taker buy/sell volume ratio.

Combined with 1-minute BTCUSDT Kline data (`taker_buy_base_asset_volume` for taker delta), the concepts translate into 3 empirical regimes:

1. **Leverage Build-up Regime (OI-03, OI-04, OI-05, OI-09):**
   - Condition: `sum_open_interest` rises > 0.5% over 30 minutes while price is flat (`|dP| <= 0.15%`) or rising.
   - Sidedness: OI alone does not choose direction (`RESULT.md` shows next 60m up rate 48.5% to 52.7%, indistinguishable from 50%).
   - Taker delta indicates who is hitting market orders; top trader ratio (`count_toptrader_long_short_ratio`) indicates smart money positioning.
   - Role in MTS: Volatility regime warning (`weather_warning`), scaling position size down prior to breakouts.

2. **Deleveraging / Cascade Flush Regime (OI-02, OI-06, OI-10, OI-11):**
   - Condition: Rapid drop in `sum_open_interest` (`dOI <= -1.0%` within 15-30m) accompanied by 3-sigma price move outside Bollinger Bands.
   - Mechanism: Involuntary margin closeouts ("liquidation prints carry no opinion").
   - Result: In bull regimes (2024-2025), short-covering rallies continue (55% up); in bear regimes (2022), bounces fade (44% up) (`RESULT.md` section A2).
   - Role in MTS: Mean-reversion trigger for V-shaped recoveries when taker volume reverses (`sum_taker_long_short_vol_ratio > 1.2`).

3. **Liquidation Map & Stop Buffer (OI-08, OI-12):**
   - Protective stops are placed beyond estimated liquidation clusters calculated from recent swing pivots and open interest spikes.
