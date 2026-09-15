# RESEARCH BRIEF: Binance API Data Feed for MTS
**Topic:** How to correctly use Binance API for Market Analysis & Signal Generation
**Purpose:** Feed expert recommendations into MTS DSA (Data Screener Agent) design
**Date:** 2026-09-05
**Sources:** Binance Official Docs, Medium (Joao TX), CoinMarketCap Academy, Binance Academy
**Status:** READY FOR NEXT SESSION ANALYSIS

---

## 1. WHAT EXPERTS SAY: BINANCE API BEST PRACTICES

### 1.1 Architecture: REST vs WebSocket — The Critical Choice

**Expert consensus (Binance Official, CoinMarketCap Academy, Medium):**

| Data Need | REST (costs weight) | WebSocket (free stream) | Expert Recommendation |
|-----------|---------------------|------------------------|----------------------|
| Orderbook updates | `GET /api/v1/depth` | `<symbol>@depth` | **WebSocket** — real-time, no weight cost |
| Price updates | `GET /api/v1/ticker/24hr` | `<symbol>@ticker` | **WebSocket** — continuous, no polling |
| Trade execution | `GET /api/v1/order` (polling) | User Data Stream (`executionReport`) | **WebSocket** — event-driven |
| Balance changes | `GET /api/v1/accountV2` (polling) | User Data Stream (`outboundAccountPosition`) | **WebSocket** — push, not pull |
| Historical klines | `GET /api/v3/klines` | N/A | **REST** — one-time fetch, cache locally |
| Exchange info | `GET /api/v3/exchangeInfo` | N/A | **REST** — fetch once, cache |

**Key expert quote:**
> "WebSocket streams do NOT count toward REST API rate limits. Prefer WebSocket over polling REST endpoints." — Binance Thailand API Docs

**Key expert quote:**
> "Use CMC [or exchange APIs] for the market-intelligence layer: research, signals, monitoring. Use exchange APIs for the execution layer: private balances, order placement, fills, positions." — CoinMarketCap Academy

### 1.2 Rate Limits: The #1 Mistake

**Binance Spot API:** 1,200 request weight per minute (IP-based)
**Binance Futures API:** 2,400 request weight per minute (IP-based)
**Order rate limits:** Shared between REST and WebSocket API (per UID)

**Weight costs (Spot — updated 2023):**
| Endpoint | Weight |
|----------|--------|
| `/api/v3/trades` | 2 |
| `/api/v3/depth` (1-100 levels) | 2 |
| `/api/v3/depth` (101-500 levels) | 25 |
| `/api/v3/depth` (501-1000 levels) | 50 |
| `/api/v3/depth` (1001-5000 levels) | 250 |
| `/api/v3/klines` | 2 |
| `/api/v3/ticker/24hr` | 1-40 (single vs all symbols) |

**Expert recommendation:**
> "Calculate the total weight of your polling loop per cycle. Ensure your cycle fits within the 10-second and 1-minute windows. Leave headroom for ad-hoc requests." — Binance Thailand API Docs

> "Implement a token bucket or sliding window counter in your client. Deduct the endpoint weight from your budget before every request. Queue or delay requests when the budget is exhausted." — Binance Thailand API Docs

### 1.3 Common Mistakes (Expert-Documented)

| # | Mistake | Why It Happens | Fix |
|---|---------|----------------|-----|
| 1 | **Polling REST for real-time data** | Easy to code, familiar pattern | Switch to WebSocket streams. REST is for historical/one-time data only. |
| 2 | **Hitting rate limits** | No request budgeting, no weight tracking | Implement token bucket rate limiter. Track weight per request. |
| 3 | **No backpressure handling** | Assuming API always available | Design for 429/418 responses. Implement exponential backoff. |
| 4 | **Not using Testnet** | Testing on production with real funds | Binance Testnet available for safe development. |
| 5 | **Wrong API for the job** | Using Spot API for futures data | Use FAPI for USD-M futures, DAPI for coin-margined. |
| 6 | **No connection management** | WebSocket drops, no reconnect | Implement auto-reconnect with exponential backoff. |
| 7 | **Ignoring filter rules** | Orders rejected due to PRICE_FILTER, LOT_SIZE | Fetch `/exchangeInfo` once, cache filter rules locally. |
| 8 | **Not verifying signatures** | HMAC SHA256 errors, auth failures | Use proper signature generation. Test on Testnet first. |

### 1.4 Data Feed Architecture Recommendations

**For MTS-style market analysis (volume profile, order flow, structure):**

| Data Type | Binance Source | MTS Use Case | Recommended Approach |
|-----------|---------------|--------------|---------------------|
| Klines (OHLCV) | `/fapi/v1/klines` or `@kline` stream | Volume Profile, VWAP, structure | REST for historical build, WebSocket for live updates |
| Order book depth | `/fapi/v1/depth` or `@depth` stream | Bid/ask ratio, absorption | WebSocket @depth@100ms or @depth@250ms |
| Recent trades | `/fapi/v1/trades` or `@aggTrade` | Delta, CVD, trade flow | WebSocket @aggTrade for real-time |
| Funding rate | `/fapi/v1/fundingRate` | Funding extreme detection | REST — check every 8h (00:00, 08:00, 16:00 UTC) |
| Open interest | `/fapi/v1/openInterest` | OI trend | REST — check every 1h |
| Best bid/ask | `/fapi/v1/ticker/bookTicker` or `@bookTicker` | Spread, book imbalance | WebSocket @bookTicker |
| 24h ticker | `/fapi/v1/ticker/24hr` or `@ticker` | Volume spike, price change | WebSocket @ticker |

**Key insight:** MTS needs **aggregated data** (CoinGlass-style), not raw Binance data. Binance API provides per-exchange data. For MTS's multi-exchange aggregated view, Binance alone is insufficient — but it's the primary source for BTCUSDT/ETHUSDT perp data.

---

## 2. HOW MTS CURRENTLY USES BINANCE API

### 2.1 Current DSA Architecture (from session analysis)

The DSA (Java, BinanceDataFeed project) appears to use:
- **REST API** for snapshot generation (`mvn compile exec:java`)
- **Polling pattern** for market data fetch
- **Single-symbol** focus (BTCUSDT)
- **JSON output** with pre-computed metrics (VP, VWAP, CVD, etc.)

### 2.2 Gaps Identified

| Gap | Current State | Expert Recommendation | Priority |
|-----|--------------|----------------------|----------|
| **Real-time vs snapshot** | Snapshot mode only (manual trigger) | WebSocket streams for continuous data | P1 |
| **Rate limit awareness** | Unknown if tracked | Implement weight budget + token bucket | P0 |
| **Data source aggregation** | Binance only | Multi-exchange aggregation (CoinGlass model) | P2 |
| **Historical data caching** | Unknown | Local cache for klines, rebuild VP from cache | P1 |
| **Connection resilience** | Unknown | Auto-reconnect, heartbeat, backoff | P1 |
| **Testnet usage** | Unknown | Use Testnet for DSA development/testing | P1 |

---

## 3. EXPERT RECOMMENDATIONS FOR MTS DSA

### 3.1 Immediate (P0)

1. **Implement rate limit tracking** — Every REST request must deduct its weight from a budget. Never exceed 1,200 weight/min (spot) or 2,400 (futures).

2. **Switch real-time data to WebSocket** — Order book, trades, ticker should use WebSocket streams. REST only for historical klines and exchange info.

3. **Use Binance Testnet** — All DSA development and testing should use Testnet before production.

### 3.2 Short-term (P1)

4. **Implement local kline cache** — Fetch historical klines once, store locally, update from WebSocket @kline stream. Rebuild VP/VWAP from cache, not from repeated REST calls.

5. **Add connection resilience** — WebSocket auto-reconnect with exponential backoff. Heartbeat/ping handling.

6. **Multi-timeframe data management** — Maintain separate kline caches for 1m, 5m, 15m, 1h, 4h, 1D, 1W. Build VP from appropriate timeframe.

### 3.3 Medium-term (P2)

7. **Multi-exchange aggregation** — Binance + Bybit + OKX data combined (like CoinGlass). Weighted average for VP, VWAP, CVD.

8. **Real-time proof detection** — Use WebSocket @aggTrade + @depth for live delta, absorption, speed detection instead of snapshot-based polling.

---

## 4. MISTAKES TO AVOID (Expert-Documented)

### 4.1 Technical Mistakes

| Mistake | Why It Breaks MTS | Prevention |
|---------|-------------------|------------|
| REST polling for live data | Hits rate limits, stale data, missed signals | WebSocket streams |
| No weight tracking | IP ban (418), system halt | Token bucket rate limiter |
| No reconnect logic | Missed data during disconnects | Auto-reconnect + backoff |
| Testing on production | Real fund risk, API key exposure | Testnet only for dev |
| Ignoring exchange filters | Order rejections, failed execution | Cache `/exchangeInfo` filters |
| Single exchange data | Biased VP, missed cross-exchange flow | Multi-exchange aggregation |

### 4.2 MTS-Specific Mistakes

| Mistake | Why It Breaks MTS | Prevention |
|---------|-------------------|------------|
| Snapshot-only mode | Delayed signals, missed triggers | Continuous WebSocket feed |
| No data validation | False proofs (BUG #6), bad signals | Cross-validate with visual |
| Over-reliance on single TF | Missed HTF context | Multi-TF cache (1m to 1W) |
| No local caching | Repeated REST calls, rate limit hits | Local kline + VP cache |
| Ignoring funding schedule | Missed funding extreme windows | Schedule-based checks |

---

## 5. SOURCES & REFERENCES

1. **Binance Official Developer Docs** — developers.binance.com (Authority: A)
   - WebSocket API General Info: Rate limits, response format
   - Spot API Changelog: Weight limit updates

2. **Binance Academy** — binance.com/en/academy (Authority: A)
   - "What Are Binance WebSocket Limits?" (2025-04-22)

3. **CoinMarketCap Academy** — coinmarketcap.com/academy (Authority: A)
   - "Best Crypto API for Trading Bots & Algorithmic Trading (2026)"

4. **Medium — Joao TX** — medium.com/@joaotx (Authority: A)
   - "Building a Binance Futures Client in Python — Part II" (2025-08-28)

5. **Binance Thailand API Docs** — binance.th/api-docs (Authority: NA)
   - REST Open API v1.0.0 — Rate limits, market data flow

---

## 6. NEXT SESSION ACTION ITEMS

For the next AI session, research and document:

1. **Binance WebSocket stream specifics for MTS data needs:**
   - Which streams map to which MTS metrics (VP, VWAP, CVD, delta, etc.)
   - Stream subscription management (combined streams vs individual)
   - Data frequency: @depth@100ms vs @depth@250ms vs @depth@500ms

2. **Rate limit implementation pattern:**
   - Token bucket design for Java (DSA is Java)
   - Weight tracking per request type
   - Budget allocation: market data vs order execution

3. **Local caching strategy:**
   - Kline storage format (SQLite, file-based, in-memory)
   - VP rebuild from cached klines
   - Cache invalidation rules

4. **Multi-exchange aggregation approach:**
   - How CoinGlass aggregates Binance + Bybit + OKX
   - Weighted vs simple average for VP
   - Data normalization across exchanges

5. **DSA architecture redesign options:**
   - Current: REST snapshot → JSON output
   - Option A: WebSocket continuous → local cache → periodic JSON snapshot
   - Option B: Hybrid — WebSocket for live, REST for historical backfill
   - Recommendation based on expert best practices

---

# END
