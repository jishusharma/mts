# DSA DEVELOPER IMPLEMENTATION TASKS
# MTS v4.2.0-p5 — Binance API WebSocket Migration
# Version: 1.1.0 (merged AI + Claude research)
# Date: 2026-09-05
# Status: READY FOR IMPLEMENTATION

---

## BEFORE YOU START

1. Read `mts/research/binance_api_integration_recommendations.md` (50KB) for full context.
2. All code must run on **Testnet first**: `https://testnet.binancefuture.com`
3. Re-run the 98/98 math test suite after each phase. A data-source change should never silently alter math-layer output.
4. Each task has: **Priority**, **Estimated Time**, **Acceptance Criteria**, **Files to Modify**.

---

## PHASE 0: FOUNDATION (Week 1-2)

### TASK 0.1 — Token Bucket Rate Limiter
**Priority:** P0 | **Time:** 4-6 hours | **Files:** `BinanceRateLimiter.java` (new)

**What to build:**
A thread-safe, weight-aware token bucket that reconciles against Binance's `X-MBX-USED-WEIGHT-1M` headers.

**Key requirements:**
- Futures limit: 2,400 weight/min. Use **85% safety margin** = 2,040 max.
- Three budget types: MARKET_DATA (70%), HISTORICAL (20%), EMERGENCY (10%).
- `tryConsume(int weight, BudgetType type)` returns true/false.
- `reconcile(int serverUsedWeight)` called after every response.
- On HTTP 429: honor `Retry-After` header exactly.
- On HTTP 418: emergency halt for full ban duration.

**Acceptance criteria:**
- [ ] Unit test: consume 2,040 weight → 2,041st call returns false.
- [ ] Unit test: reconcile with server weight higher than local → local corrected.
- [ ] Integration test: 1,000 rapid REST calls → no 429/418.

**Code skeleton (from research doc Section 2.2):**
```java
public class BinanceRateLimiter {
    private final long maxWeightPerMinute;
    private final AtomicLong currentWeight;
    private volatile Instant windowStart;
    private final ReentrantLock lock = new ReentrantLock();
    private final AtomicLong marketDataBudget;
    private final AtomicLong historicalBudget;
    private final AtomicLong emergencyBudget;

    public boolean tryConsume(int weight, BudgetType type) { ... }
    public void reconcile(int serverUsedWeight) { ... }
    public enum BudgetType { MARKET_DATA, HISTORICAL, EMERGENCY }
}
```

---

### TASK 0.2 — SQLite Cache Schema
**Priority:** P0 | **Time:** 3-4 hours | **Files:** `CacheSchema.java` or `schema.sql` (new)

**What to build:**
SQLite database with 4 tables. Use JDBC or a lightweight ORM.

**Schema (copy-paste ready):**
```sql
CREATE TABLE klines (
    symbol TEXT NOT NULL,
    interval TEXT NOT NULL,
    open_time INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    quote_volume REAL NOT NULL,
    taker_buy_base REAL NOT NULL,
    taker_buy_quote REAL NOT NULL,
    trade_count INTEGER NOT NULL,
    PRIMARY KEY (symbol, interval, open_time)
);
CREATE INDEX idx_klines_symbol_interval ON klines(symbol, interval, open_time);

CREATE TABLE volume_profiles (
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    poc REAL NOT NULL,
    vah REAL NOT NULL,
    val REAL NOT NULL,
    vah_1std REAL NOT NULL,
    val_1std REAL NOT NULL,
    total_volume REAL NOT NULL,
    shape TEXT NOT NULL,
    PRIMARY KEY (symbol, date)
);

CREATE TABLE funding_rates (
    symbol TEXT NOT NULL,
    funding_time INTEGER NOT NULL,
    funding_rate REAL NOT NULL,
    mark_price REAL NOT NULL,
    PRIMARY KEY (symbol, funding_time)
);

CREATE TABLE open_interest (
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open_interest REAL NOT NULL,
    sum_open_interest_value REAL NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);
```

**Acceptance criteria:**
- [ ] Database file created on DSA startup if not exists.
- [ ] Insert 1,000 klines → query returns in <10ms.
- [ ] Query last 30 days of 1m klines → returns in <100ms.

---

### TASK 0.3 — Exchange Info Cache
**Priority:** P1 | **Time:** 2 hours | **Files:** `BinanceExchangeInfo.java` (new)

**What to build:**
Fetch `GET /fapi/v1/exchangeInfo` (weight: 20) once on startup, cache symbol filters, price precision, lot size. Refresh daily.

**Acceptance criteria:**
- [ ] Cached on disk (JSON or SQLite).
- [ ] DSA startup uses cache → no REST call needed.
- [ ] Refresh triggered if cache older than 24h.

---

## PHASE 1: WEBSOCKET CORE (Week 3-4)

### TASK 1.1 — WebSocket Client with Auto-Reconnect
**Priority:** P0 | **Time:** 8-10 hours | **Files:** `BinanceWebSocketClient.java` (new)

**What to build:**
OkHttp-based WebSocket client with exponential backoff reconnect.

**CRITICAL: Use the 2026 URL split:**
- Public (high-freq): `wss://fstream.binance.com/public`
- Market (regular): `wss://fstream.binance.com/market`
- Private (user data): `wss://fstream.binance.com/private`

**Connection topology for MTS:**
```
Conn 1 (Public):  btcusdt@depth@100ms, btcusdt@bookTicker, ethusdt@depth@100ms, ethusdt@bookTicker
Conn 2 (Market):  btcusdt@aggTrade, btcusdt@kline_1m..1w, btcusdt@ticker, btcusdt@markPrice@1s
Conn 3 (Market):  ethusdt@aggTrade, ethusdt@kline_1m..1w, ethusdt@ticker, ethusdt@markPrice@1s
```

**Key requirements:**
- Exponential backoff: 500ms → 1s → 2s → 4s → 8s → 16s → 30s (cap).
- Jitter: +/- 30% randomization on each delay.
- Ping every 30s (OkHttp `pingInterval(30, TimeUnit.SECONDS)`).
- On reconnect: invalidate stale cache entries, request fresh snapshot for order book.
- **Validate all streams in a subscription resolve to the same category** before connecting. Mixed-category = silent dead feed.

**Acceptance criteria:**
- [ ] All 3 connections stable for 24 hours.
- [ ] Manual network disconnect → auto-reconnect within 30s.
- [ ] Reconnect count logged; no infinite loop.
- [ ] Testnet validation: all streams receive data.

**Code skeleton (from research doc Section 7.1):**
```java
public class BinanceWebSocketClient {
    private static final String BASE_PUBLIC = "wss://fstream.binance.com/public/stream?streams=";
    private static final String BASE_MARKET = "wss://fstream.binance.com/market/stream?streams=";
    // ... exponential backoff, jitter, ping, reconnect logic
}
```

---

### TASK 1.2 — Message Router
**Priority:** P1 | **Time:** 3-4 hours | **Files:** `BinanceMessageRouter.java` (new)

**What to build:**
Route incoming WebSocket JSON to appropriate handlers.

**Two message formats:**
1. Combined stream: `{"stream":"btcusdt@kline_1m","data":{...}}`
2. Direct stream: `{"e":"kline","E":123456789,...}`

**Handlers needed:**
- `KlineHandler` → writes to SQLite cache on close (`"x": true`)
- `AggTradeHandler` → feeds delta/CVD accumulator
- `DepthHandler` → feeds local order book manager
- `TickerHandler` → 24h stats
- `MarkPriceHandler` → funding rate + mark price

**Acceptance criteria:**
- [ ] 1,000 messages routed correctly → zero misrouted.
- [ ] Kline close triggers SQLite insert.
- [ ] Malformed JSON logged, not crashed.

---

### TASK 1.3 — Kline Handler + Cache Write
**Priority:** P1 | **Time:** 4-5 hours | **Files:** `KlineHandler.java`, `KlineCache.java` (new)

**What to build:**
Process `@kline` stream updates. Write closed klines to SQLite. Update in-memory current kline for live VWAP.

**Key logic:**
```java
if (isClosed) {
    cache.insert(kline);           // Persist to SQLite
    if ("1d".equals(interval)) {
        vpComputer.rebuild(symbol); // Rebuild VP on daily close
    }
} else {
    cache.updateCurrent(kline);    // In-memory only
}
```

**Acceptance criteria:**
- [ ] WebSocket kline close matches REST kline exactly (validation: diff = 0).
- [ ] SQLite insert within 50ms of close.
- [ ] 30 days of 1m klines queryable from cache.

---

### TASK 1.4 — AggTrade Handler (Delta + CVD)
**Priority:** P1 | **Time:** 4-5 hours | **Files:** `AggTradeHandler.java`, `CvdAccumulator.java` (new)

**What to build:**
Process `@aggTrade` stream. Compute delta and CVD.

**Delta logic:**
- `m = false` → buyer was taker (aggressive buy) → add to buy volume
- `m = true` → seller was taker (aggressive sell) → add to sell volume
- `delta = buy_volume - sell_volume`
- `cvd = cumulative_delta` (running sum since session start)

**Two time windows (addresses BUG #4):**
- `cvd.slope` → cumulative since DSA start (long-term trend)
- `trade_flow.net_delta` → recent window (e.g., last 5 minutes)

**Acceptance criteria:**
- [ ] CVD from WebSocket matches REST-computed CVD within 0.1%.
- [ ] Delta sign correct for 100 test trades.
- [ ] Both cumulative and recent-window CVD available to proof engine.

---

## PHASE 2: ORDER BOOK (Week 5-6)

### TASK 2.1 — Local Order Book Manager
**Priority:** P0 | **Time:** 10-12 hours | **Files:** `OrderBookManager.java`, `DepthUpdate.java` (new)

**What to build:**
Maintain local order book from `@depth` diff stream + REST snapshot.

**EXACT Binance algorithm (getting this wrong = silent corruption):**
```
1. Connect to btcusdt@depth@100ms on /public → buffer events
2. GET /fapi/v1/depth?symbol=BTCUSDT&limit=1000 → note lastUpdateId
3. Discard events where event.u < lastUpdateId
4. First applied event: U <= lastUpdateId AND u >= lastUpdateId
5. Each subsequent event: pu == previous_u. If not → RESYNC
6. Replace quantities (don't add). qty=0 → remove level.
```

**CRITICAL: Periodic resync every 4 hours.**
A gap-free sequence does NOT guarantee correctness. Stale levels accumulate.

**BUG #5 fix:** Use `limit=1000` (weight: 50) for snapshots. `limit=100` only covers ~0.12% at $80K — insufficient for 1% depth metrics.

**Acceptance criteria:**
- [ ] Local book best bid/ask matches `@bookTicker` within 100ms.
- [ ] Gap detected → full resync triggered, logged.
- [ ] 4-hour scheduled resync → no drift after 24h uptime.
- [ ] `order_book_depth_expanded` thresholds show distinct values (BUG #5 fixed).

---

### TASK 2.2 — Bid/Ask Ratio Computation
**Priority:** P1 | **Time:** 3 hours | **Files:** `OrderBookMetrics.java` (new)

**What to build:**
Compute bid_depth_pct and ask_depth_pct at thresholds: 0.1%, 0.2%, 0.5%, 1.0%.

**Acceptance criteria:**
- [ ] Values distinct at all thresholds (not identical).
- [ ] Sum of bid_depth + ask_depth ≈ 100%.
- [ ] Values stable (no wild swings between ticks).

---

## PHASE 3: COMPUTED METRICS (Week 7-8)

### TASK 3.1 — Volume Profile Rebuild
**Priority:** P1 | **Time:** 6-8 hours | **Files:** `VolumeProfileComputer.java` (new)

**What to build:**
Rebuild VP from cached klines on daily close. Use 30 days of 1m klines for intraday, daily klines for weekly/monthly.

**Note:** True VP needs tick data (`@aggTrade`). Kline-based is an approximation sufficient for daily/weekly. For 1h/4h VP, use `@aggTrade` aggregation.

**Acceptance criteria:**
- [ ] WebSocket-derived POC within 0.1% of REST-derived POC.
- [ ] VP rebuild completes in <5 seconds for 30 days of 1m data.
- [ ] Shape classification (B, p, D, thin) matches existing DSA logic.

---

### TASK 3.2 — VWAP from AggTrade Stream
**Priority:** P1 | **Time:** 3-4 hours | **Files:** `VwapComputer.java` (new)

**What to build:**
Compute VWAP from `@aggTrade` stream: `cumulative(price * qty) / cumulative(qty)`.

**Acceptance criteria:**
- [ ] VWAP from stream matches REST-computed VWAP within 0.05%.
- [ ] Intrabar VWAP available for live deviation checks.

---

### TASK 3.3 — Cache Freshness Layer
**Priority:** P1 | **Time:** 2-3 hours | **Files:** Add to all handler classes

**What to build:**
Every cache layer exposes `lastUpdated` timestamp. Proof-evaluation checks freshness before using data.

**Rule:** Depth cache older than 2s → suppress order-book signals. Kline cache older than 5s → flag stale.

**Acceptance criteria:**
- [ ] Stale depth cache triggers warning, not false signal.
- [ ] All cache entries have `lastUpdated` accessible.

---

## PHASE 4: CONTINUOUS OUTPUT (Week 9-10)

### TASK 4.1 — Continuous JSON Stream
**Priority:** P1 | **Time:** 6-8 hours | **Files:** `DsaOutputStream.java` (new)

**What to build:**
Replace single JSON snapshot with continuous output. Emit on:
- Kline close
- VP rebuild
- Proof detection
- Every 60 seconds (heartbeat)

**Acceptance criteria:**
- [ ] Output emitted within 100ms of triggering event.
- [ ] Periodic full snapshot every 5 minutes for cold starts.
- [ ] JSON schema backward-compatible with current trading card format.

---

### TASK 4.2 — Hybrid Run Mode
**Priority:** P1 | **Time:** 4 hours | **Files:** `DsaHybridRunner.java` (new)

**What to build:**
Run REST snapshot and WebSocket feed in parallel. Compare outputs.

**Validation gate:** 20 consecutive trading cards from WebSocket DSA match REST DSA within ±3 confidence points → switch production to WebSocket.

**Acceptance criteria:**
- [ ] Both paths running, logging differences.
- [ ] Divergence >3 points triggers alert, not silent override.

---

## PHASE 5: MULTI-EXCHANGE (Week 11-14)

### TASK 5.1 — Exchange Data Feed Interface
**Priority:** P2 | **Time:** 4 hours | **Files:** `ExchangeDataFeed.java` (interface, new)

**What to build:**
Abstract interface for exchange-agnostic data feeds.

```java
public interface ExchangeDataFeed {
    OrderBook getOrderBook(String symbol);
    List<Kline> getKlines(String symbol, String interval, int limit);
    double getFundingRate(String symbol);
    double getOpenInterest(String symbol);
    double getVwap(String symbol);
    double getCvd(String symbol);
}
```

**Acceptance criteria:**
- [ ] Binance implementation passes all tests.
- [ ] Interface documented for Bybit/OKX future implementations.

---

## CRITICAL PITFALLS CHECKLIST

Before marking any phase complete, verify:

- [ ] **No mixed-category subscriptions.** `/public` and `/market` streams on separate connections.
- [ ] **No instant reconnect loops.** Backoff with jitter enforced.
- [ ] **Rate limiter active on every REST call.** Including "quick" debug calls.
- [ ] **Order book resyncs scheduled.** Not just on reconnect.
- [ ] **Kline close flag respected.** Never commit partial candle to cache.
- [ ] **Testnet first.** Every phase validated on Testnet before prod.
- [ ] **98/98 math tests pass.** After every phase.

---

## FILES TO CREATE (summary)

| File | Phase | Purpose |
|------|-------|---------|
| `BinanceRateLimiter.java` | 0.1 | Weight-aware token bucket |
| `schema.sql` | 0.2 | SQLite DDL |
| `BinanceExchangeInfo.java` | 0.3 | Symbol filters cache |
| `BinanceWebSocketClient.java` | 1.1 | OkHttp WS client + reconnect |
| `BinanceMessageRouter.java` | 1.2 | Message routing |
| `KlineHandler.java` | 1.3 | Kline processing + cache write |
| `KlineCache.java` | 1.3 | SQLite kline persistence |
| `AggTradeHandler.java` | 1.4 | Trade processing |
| `CvdAccumulator.java` | 1.4 | Delta/CVD computation |
| `OrderBookManager.java` | 2.1 | Local book snapshot+diff |
| `DepthUpdate.java` | 2.1 | Depth event model |
| `OrderBookMetrics.java` | 2.2 | Bid/ask ratio |
| `VolumeProfileComputer.java` | 3.1 | VP rebuild from cache |
| `VwapComputer.java` | 3.2 | VWAP from aggTrade |
| `DsaOutputStream.java` | 4.1 | Continuous JSON output |
| `DsaHybridRunner.java` | 4.2 | Parallel REST+WS validation |
| `ExchangeDataFeed.java` | 5.1 | Abstract interface |

---

## DEPENDENCIES TO ADD

```xml
<!-- OkHttp for WebSocket -->
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.12.0</version>
</dependency>

<!-- Jackson for JSON parsing -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.0</version>
</dependency>

<!-- SQLite JDBC -->
<dependency>
    <groupId>org.xerial</groupId>
    <artifactId>sqlite-jdbc</artifactId>
    <version>3.45.0.0</version>
</dependency>
```

---

## TESTNET CONFIGURATION

```java
public class BinanceConfig {
    // Production
    public static final String REST_BASE = "https://fapi.binance.com";
    public static final String WS_PUBLIC = "wss://fstream.binance.com/public";
    public static final String WS_MARKET = "wss://fstream.binance.com/market";

    // Testnet (use this for ALL development)
    public static final String TESTNET_REST = "https://testnet.binancefuture.com";
    public static final String TESTNET_WS = "wss://stream.binancefuture.com";

    public static final boolean USE_TESTNET = true; // Flip to false ONLY for prod deploy
}
```

---

## VERIFICATION CHECKLIST (before each phase deploy)

| Check | How |
|-------|-----|
| Rate limiter working | Run 100 REST calls, verify no 429/418 |
| WebSocket stable | 24-hour uptime test, zero disconnects without reconnect |
| Kline accuracy | Compare WS close vs REST kline for 100 candles |
| Book accuracy | Local best bid/ask matches `@bookTicker` within 100ms |
| VP accuracy | WS-derived POC within 0.1% of REST-derived |
| BUG #5 fixed | Depth thresholds show distinct values |
| BUG #6 prevention | Stale cache triggers suppression, not false signal |
| Math tests | 98/98 pass with WebSocket data |
| Memory | No leaks after 24h (heap dump analysis) |
| Testnet | All tests pass on Testnet before prod |

---

## QUESTIONS?

Refer to `mts/research/binance_api_integration_recommendations.md` for:
- Full stream-to-metric mapping table
- Complete Java code for rate limiter, WebSocket client, message router
- Order book snapshot+diff algorithm with exact sequence checks
- Migration roadmap with week estimates
- Risk assessment matrix
- 14 expert citations with URLs

---

# END OF TASK DOCUMENT

**Next session:** Test implementation against this checklist.
