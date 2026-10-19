package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.IntToDoubleFunction;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * T037: body tests for MarketDataSnapshot.java (1468 lines at HEAD 9695b36; line numbers below are at that revision).
 * Promotion of MyTradingSys/tests/java/MarketDataSnapshotTest.java.new; style mirrors NetRRConstantTest.java and
 * CountSignalsD4Test.java (pom.xml:41-42 junit-jupiter 5.10.2).
 *
 * SEAM (b): the constructor builds its own client: `this.client = new BinanceClient()` (MarketDataSnapshot.java:29-33).
 * These tests overwrite the private field `client` by reflection with {@link StubClient}, a BinanceClient subclass whose
 * endpoint methods return canned JSON. MarketDataSnapshot.java is untouched. classifyOiDeltaState is `private static`
 * (:1401) and is called by reflection, as in CountSignalsD4Test.java:11-17.
 *
 * Expected values come from: the four-state table in INDICATOR_IMPLEMENTATION_HANDOFF.md:54-58; the root key list of the
 * previous class comment (fetchSnapshot :334-380, :429, :444-447; market_data/data_schema_v1.2.0.md predates several of
 * those keys, it lists weekly_vp, prior_day, trade_flow, structure, order_flow, funding, open_interest, order_book_depth,
 * setup_candidates); research/BUGS.md B075 (historical snapshot: flow fields null + UNAVAILABLE, session attached, no
 * live calls); and hand computations written next to each assertion.
 *
 * Build-order constraints: stubbed aggTrades always throws, so fetchSnapshot takes its catch path and never writes
 * runtime_data/speed_baselines. saveSnapshot / saveHistoricalSnapshot write under the relative runtime_data/snapshots
 * (gitignored); those tests use the symbol ZZTEST and delete only their own ZZTEST_* files.
 */
public class MarketDataSnapshotTest {

    private static final String SYM = "BTCUSDT";
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final Instant AS_OF = Instant.parse("2026-10-01T12:00:00Z");

    // ===================================================================================================
    // Stub + builders
    // ===================================================================================================

    /** Canned BinanceClient: anything not configured throws IOException (the production code catches it). */
    static class StubClient extends BinanceClient {
        final Map<String, JsonNode> klines = new HashMap<>();
        JsonNode depth;
        JsonNode oiHist;
        JsonNode funding;
        JsonNode spot;
        JsonNode premium;
        JsonNode retailRatio;
        JsonNode whaleRatio;
        JsonNode topRatio;
        int shutdownCalls = 0;
        int liveCalls = 0;

        private JsonNode need(JsonNode n, String what) throws IOException {
            liveCalls++;
            if (n == null) throw new IOException("stub: " + what + " not configured");
            return n;
        }

        @Override public JsonNode klines(String s, String interval, int limit) throws IOException {
            JsonNode k = klines.get(interval);
            if (k == null) throw new IOException("stub: no klines " + interval);
            return k.deepCopy();
        }
        @Override public JsonNode klinesRange(String s, String interval, long a, long b, int limit) throws IOException {
            JsonNode k = klines.get(interval);
            return k == null ? MAPPER.createArrayNode() : k.deepCopy();
        }
        @Override public JsonNode orderBookDepth(String s, int limit) throws IOException { return need(depth, "depth"); }
        @Override public JsonNode openInterestHist(String s, String p, int limit) throws IOException { return need(oiHist, "oiHist"); }
        @Override public JsonNode currentFundingRate(String s) throws IOException { return need(funding, "funding"); }
        @Override public JsonNode aggTrades(String s, int limit) throws IOException { return need(null, "aggTrades"); }
        @Override public JsonNode aggTradesRange(String s, long a, long b, int limit) throws IOException { return need(null, "aggTradesRange"); }
        @Override public JsonNode spotPrice(String s) throws IOException { return need(spot, "spot"); }
        @Override public JsonNode premiumIndex(String s) throws IOException { return need(premium, "premium"); }
        @Override public JsonNode longShortRatio(String s, String p, int limit) throws IOException { return need(retailRatio, "retail"); }
        @Override public JsonNode topLongShortPositionRatio(String s, String p, int limit) throws IOException { return need(whaleRatio, "whale"); }
        @Override public JsonNode topLongShortAccountRatio(String s, String p, int limit) throws IOException { return need(topRatio, "top"); }
        @Override public void shutdown() { shutdownCalls++; }
    }

    private static JsonNode json(String s) {
        try { return MAPPER.readTree(s); } catch (IOException e) { throw new RuntimeException(e); }
    }

    /** Binance kline row: [openTime, open, high, low, close, volume, closeTime, quoteVol, trades, takerBuyBase]. */
    private static ArrayNode bar(long openTime, double o, double h, double l, double c, double vol, long closeTime, double takerBuy) {
        ArrayNode a = MAPPER.createArrayNode();
        a.add(openTime).add(o).add(h).add(l).add(c).add(vol).add(closeTime).add(0.0).add(1).add(takerBuy);
        return a;
    }

    /** n closed 1m bars; the last one closes 1 ms before refMs. */
    private static ArrayNode closedBars(long refMs, int n, IntToDoubleFunction close, double vol, double takerBuy) {
        ArrayNode out = MAPPER.createArrayNode();
        for (int i = 0; i < n; i++) {
            long closeTime = refMs - (long) (n - 1 - i) * 60_000L - 1;
            long openTime = closeTime - 59_999L;
            double c = close.applyAsDouble(i);
            out.add(bar(openTime, c, c + 0.5, c - 0.5, c, vol, closeTime, takerBuy));
        }
        return out;
    }

    /** Every timeframe gets the same closed series, so fetchSnapshot has all seven mtf entries. */
    private static StubClient stubWith(ArrayNode series) {
        StubClient s = new StubClient();
        for (String tf : new String[]{"1w", "1d", "4h", "1h", "15m", "5m", "1m"}) s.klines.put(tf, series.deepCopy());
        return s;
    }

    private static MarketDataSnapshot withStub(StubClient stub) throws Exception {
        MarketDataSnapshot m = new MarketDataSnapshot();
        Field f = MarketDataSnapshot.class.getDeclaredField("client");
        f.setAccessible(true);
        f.set(m, stub);
        return m;
    }

    private static ObjectNode live(StubClient s) throws Exception {
        return withStub(s).fetchSnapshot(SYM, null);
    }

    private static ObjectNode historical(StubClient s) throws Exception {
        return withStub(s).fetchHistoricalSnapshot(SYM, AS_OF);
    }

    private static Object call(Object target, String name, Class<?>[] types, Object... args) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod(name, types);
        m.setAccessible(true);
        return m.invoke(target, args);
    }

    private static long nowMs() { return System.currentTimeMillis(); }

    // ===================================================================================================
    // fetchSnapshot (public, MarketDataSnapshot.java:35) - live snapshot field contract
    // ===================================================================================================

    @Test
    void fetchSnapshot_throwsIOException_whenNo1mKlines() throws Exception {
        // :39-43 - missing or empty 1m klines -> IOException("Failed to fetch 1m klines for " + symbol).
        StubClient empty = new StubClient();
        empty.klines.put("1m", MAPPER.createArrayNode());
        IOException e1 = assertThrows(IOException.class, () -> live(empty));
        assertEquals("Failed to fetch 1m klines for BTCUSDT", e1.getMessage());

        StubClient missing = new StubClient(); // klines() throws for every interval -> mtf has no "1m"
        IOException e2 = assertThrows(IOException.class, () -> live(missing));
        assertEquals("Failed to fetch 1m klines for BTCUSDT", e2.getMessage());
    }

    @Test
    void fetchSnapshot_rootFieldContract() throws Exception {
        ObjectNode root = live(stubWith(closedBars(nowMs(), 61, i -> 100.0, 10.0, 5.0)));
        Set<String> expected = new HashSet<>(List.of(
                "timestamp_utc", "asset", "current_price", "alignment_pass", "weekly_vp", "daily_vp", "post_funding_vp",
                "intraday_4h_vp", "vwap", "cvd", "trade_flow", "structure", "order_book_depth", "conditions", "prior_day",
                "funding", "open_interest", "session", "session_timing", "spot_perp_basis", "liquidation_clusters",
                "oi_breakdown", "order_flow", "setup_candidates", "module_candidates"));
        Set<String> actual = new HashSet<>();
        root.fieldNames().forEachRemaining(actual::add);
        assertEquals(expected, actual);
        assertEquals(SYM, root.get("asset").asText());
        // trade_flow keys (:345-351) and open_interest keys (:364-375)
        Set<String> tf = new HashSet<>();
        root.get("trade_flow").fieldNames().forEachRemaining(tf::add);
        assertEquals(new HashSet<>(List.of("net_delta_1m", "net_delta_5m", "net_delta_15m", "net_delta_1h", "confidence")), tf);
        Set<String> oi = new HashSet<>();
        root.get("open_interest").fieldNames().forEachRemaining(oi::add);
        assertEquals(new HashSet<>(List.of("direction", "change_1h_pct", "delta_state", "delta_state_price", "confidence")), oi);
    }

    @Test
    void fetchSnapshot_currentPriceIsLast1mClose_roundedToTwoDecimals() throws Exception {
        // last closed close 100.123456 -> 100.12 by hand. A forming bar (close 999.0, closeTime in the future) is
        // appended: dropFormingBar (:453-459) must remove it before the price is read.
        ArrayNode bars = closedBars(nowMs(), 3, i -> i == 2 ? 100.123456 : 100.0, 10.0, 5.0);
        long t = nowMs();
        bars.add(bar(t, 999.0, 999.5, 998.5, 999.0, 10.0, t + 60_000L, 5.0));
        StubClient s = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0));
        s.klines.put("1m", bars);
        assertEquals(100.12, live(s).get("current_price").asDouble(), 1e-9);
    }

    @Test
    void fetchSnapshot_openInterestBlockFields() throws Exception {
        // OI history 1000 -> 1010: change = (1010 - 1000) / 1000 * 100 = 1.0 %; 1010 > 1000 * 1.001 -> "rising".
        // 61 closes 100.0 + 0.1 * i (price up 6.0 over 60 bars); taker buy 6 of volume 10 -> +2 per bar (net buy).
        StubClient s = stubWith(closedBars(nowMs(), 61, i -> 100.0 + 0.1 * i, 10.0, 6.0));
        s.oiHist = json("[{\"sumOpenInterest\":\"1000\"},{\"sumOpenInterest\":\"1010\"}]");
        ObjectNode oi = (ObjectNode) live(s).get("open_interest");
        assertEquals("rising", oi.get("direction").asText());
        assertEquals(1.0, oi.get("change_1h_pct").asDouble(), 1e-9);
        assertEquals("aggressive_long", oi.get("delta_state").asText());
        assertEquals("aggressive_long", oi.get("delta_state_price").asText());
        assertEquals("HIGH", oi.get("confidence").asText());

        // rounding to 2 dp: 1000 -> 1003 is 0.3 %, 1000 -> 1000.12345 is 0.012345 % -> 0.01 (and flat: not above 1.001x)
        StubClient r = stubWith(closedBars(nowMs(), 61, i -> 100.0, 10.0, 5.0));
        r.oiHist = json("[{\"sumOpenInterest\":\"1000\"},{\"sumOpenInterest\":\"1000.12345\"}]");
        ObjectNode oiR = (ObjectNode) live(r).get("open_interest");
        assertEquals(0.01, oiR.get("change_1h_pct").asDouble(), 1e-9);
        assertEquals("flat", oiR.get("direction").asText());
    }

    // ===================================================================================================
    // T033 - OI delta four-state classifier (research/BUGS.md:119; INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 2, lines 54-58)
    // ===================================================================================================

    @Test
    void oiDeltaState_volumeSchool_fromNetDelta1h() throws Exception {
        // delta_state uses nd1h = sum over the last 60 bars of (2 * takerBuy - volume) (:183-195). Table 54-58:
        // +delta & OI up = Aggressive Longs; -delta & OI up = Aggressive Shorts; -delta & OI down = Rekt Longs;
        // +delta & OI down = Rekt Shorts. Bars: volume 10, takerBuy 6 -> +2 each; takerBuy 4 -> -2 each.
        String up = "[{\"sumOpenInterest\":\"1000\"},{\"sumOpenInterest\":\"1010\"}]";
        String down = "[{\"sumOpenInterest\":\"1000\"},{\"sumOpenInterest\":\"990\"}]";
        assertEquals("aggressive_long", volumeState(up, 6.0));
        assertEquals("aggressive_short", volumeState(up, 4.0));
        assertEquals("rekt_long", volumeState(down, 4.0));
        assertEquals("rekt_short", volumeState(down, 6.0));
        assertEquals("neutral", volumeState(up, 5.0)); // zero delta is not in the table
    }

    private static String volumeState(String oiJson, double takerBuy) throws Exception {
        StubClient s = stubWith(closedBars(nowMs(), 61, i -> 100.0, 10.0, takerBuy));
        s.oiHist = json(oiJson);
        return live(s).get("open_interest").get("delta_state").asText();
    }

    @Test
    void oiDeltaState_priceSchool_fromCloseDeltaOver60Bars() throws Exception {
        // delta_state_price = state(oiDirection, close[last] - close[last-60]) (:367-374), only when >= 61 bars.
        // OI rising; closes fall 100.0 -> 90.0 (delta -10.0) while taker flow is net buying (+2 per bar), so the two
        // schools disagree: volume school aggressive_long, price school aggressive_short (table row "-delta & OI up").
        String up = "[{\"sumOpenInterest\":\"1000\"},{\"sumOpenInterest\":\"1010\"}]";
        StubClient s = stubWith(closedBars(nowMs(), 61, i -> 100.0 - i * (10.0 / 60.0), 10.0, 6.0));
        s.oiHist = json(up);
        ObjectNode oi = (ObjectNode) live(s).get("open_interest");
        assertEquals("aggressive_long", oi.get("delta_state").asText());
        assertEquals("aggressive_short", oi.get("delta_state_price").asText());

        // exactly 60 bars: the price delta keeps its initial 0.0 -> no table row -> "neutral"
        StubClient f = stubWith(closedBars(nowMs(), 60, i -> 100.0 - i * (10.0 / 60.0), 10.0, 6.0));
        f.oiHist = json(up);
        ObjectNode oiF = (ObjectNode) live(f).get("open_interest");
        assertEquals("aggressive_long", oiF.get("delta_state").asText());
        assertEquals("neutral", oiF.get("delta_state_price").asText());
    }

    @Test
    void oiDeltaState_helperMapping_fourStatesAndNeutral() throws Exception {
        // Expected labels from the four-state table in INDICATOR_IMPLEMENTATION_HANDOFF.md:54-58:
        // +delta & OI up = Aggressive Longs; -delta & OI up = Aggressive Shorts;
        // -delta & OI down = Rekt Longs; +delta & OI down = Rekt Shorts.
        assertEquals("aggressive_long", classify("rising", 5.0));
        assertEquals("aggressive_short", classify("rising", -5.0));
        assertEquals("rekt_long", classify("falling", -5.0));
        assertEquals("rekt_short", classify("falling", 5.0));
        // not in the table: zero delta, flat / unknown / null direction
        assertEquals("neutral", classify("rising", 0.0));
        assertEquals("neutral", classify("falling", 0.0));
        assertEquals("neutral", classify("flat", 5.0));
        assertEquals("neutral", classify("flat", -5.0));
        assertEquals("neutral", classify(null, 5.0));
    }

    private static String classify(String direction, double delta) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod("classifyOiDeltaState", String.class, double.class);
        m.setAccessible(true);
        return (String) m.invoke(null, direction, delta);
    }

    @Test
    void oiDeltaState_historicalSnapshotFallback_isNeutral() throws Exception {
        // :1182-1186 historical open_interest block: direction "flat", change 0.0, both states "neutral", confidence "LOW".
        StubClient s = stubWith(closedBars(AS_OF.toEpochMilli(), 61, i -> 100.0 + i, 10.0, 6.0));
        ObjectNode oi = (ObjectNode) historical(s).get("open_interest");
        assertEquals("flat", oi.get("direction").asText());
        assertEquals(0.0, oi.get("change_1h_pct").asDouble(), 0.0);
        assertEquals("neutral", oi.get("delta_state").asText());
        assertEquals("neutral", oi.get("delta_state_price").asText());
        assertEquals("LOW", oi.get("confidence").asText());
    }

    // ===================================================================================================
    // Order-book ratio no-data sentinel (feeds math_object_builder; see TWO_CORES_FIX_PASS_2026-10-02.md item 1)
    // ===================================================================================================

    @Test
    void bidAskRatio_isZeroWhenDepthFetchFails() throws Exception {
        // :200-215 - a depth exception is swallowed and the ratio stays 0.0, published in both fields (0.0 = no data,
        // market_data/dsa_task_012_setup_candidates.md:514).
        StubClient s = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0)); // depth not configured -> IOException
        ObjectNode root = live(s);
        assertEquals(0.0, root.get("conditions").get("book_imbalance").asDouble(), 0.0);
        assertEquals(0.0, root.get("order_book_depth").get("bid_ask_ratio").asDouble(), 0.0);
    }

    @Test
    void bidAskRatio_isBidOverAskWithinOnePercentOfPrice() throws Exception {
        // price 100.0; band: bids >= 99.0, asks <= 101.0. bids: 99.5 x 2 = 199.0 inside; 98.0 x 5 outside.
        // asks: 100.5 x 1 = 100.5 inside; 101.5 x 3 outside. ratio = 199.0 / 100.5 = 1.98009... -> 1.98.
        StubClient s = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0));
        s.depth = json("{\"bids\":[[\"99.5\",\"2\"],[\"98.0\",\"5\"]],\"asks\":[[\"100.5\",\"1\"],[\"101.5\",\"3\"]]}");
        ObjectNode root = live(s);
        assertEquals(1.98, root.get("conditions").get("book_imbalance").asDouble(), 1e-9);
        assertEquals(1.98, root.get("order_book_depth").get("bid_ask_ratio").asDouble(), 1e-9);

        // no asks inside the band -> askDepth 0 -> 0.0 (division guard :215)
        StubClient z = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0));
        z.depth = json("{\"bids\":[[\"99.5\",\"2\"]],\"asks\":[[\"150.0\",\"3\"]]}");
        assertEquals(0.0, live(z).get("order_book_depth").get("bid_ask_ratio").asDouble(), 0.0);
    }

    // ===================================================================================================
    // fetchHistoricalSnapshot (public, MarketDataSnapshot.java:960)
    // ===================================================================================================

    @Test
    void fetchHistoricalSnapshot_throwsIOException_whenNo1mKlines() {
        // :968-970 - IOException("Failed to fetch historical 1m klines for " + symbol + " at " + asOf).
        StubClient s = new StubClient(); // klinesRange returns an empty array for every interval
        IOException e = assertThrows(IOException.class, () -> historical(s));
        assertEquals("Failed to fetch historical 1m klines for BTCUSDT at 2026-10-01T12:00:00Z", e.getMessage());
    }

    @Test
    void liveSession_vwapAnchorIsUtcDayStartAndNeverInTheFuture() throws Exception {
        // audit M3: the label was today's NY 09:30 in UTC (13:30Z), a future time for 00:00-13:30Z; the VWAP itself is UTC-day based.
        StubClient s = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0));
        Instant anchor = Instant.parse(live(s).get("session").get("vwap_anchor_utc").asText());
        Instant now = Instant.now();
        assertEquals(anchor.truncatedTo(java.time.temporal.ChronoUnit.DAYS), anchor);
        assertTrue(!anchor.isAfter(now));
        assertTrue(anchor.isAfter(now.minusSeconds(86_400)));
    }

    @Test
    void fetchHistoricalSnapshot_timestampIsAsOf() throws Exception {
        StubClient s = stubWith(closedBars(AS_OF.toEpochMilli(), 3, i -> 100.0, 10.0, 5.0));
        assertEquals("2026-10-01T12:00:00Z", historical(s).get("timestamp_utc").asText());
    }

    @Test
    void fetchHistoricalSnapshot_zeroedFieldContract() throws Exception {
        // Pins the INTENDED behaviour (research/BUGS.md B075, partial fix 86313de): a historical snapshot makes no live
        // calls, flow fields are null + UNAVAILABLE (never 0.0), session is attached, order_flow is not emitted.
        StubClient s = stubWith(closedBars(AS_OF.toEpochMilli(), 61, i -> 100.0, 10.0, 6.0));
        ObjectNode root = historical(s);
        assertEquals(0, s.liveCalls, "historical mode must not call live endpoints");

        assertTrue(root.get("conditions").get("book_imbalance").isNull());
        assertTrue(root.get("order_book_depth").get("bid_ask_ratio").isNull());
        assertEquals("LOW", root.get("order_book_depth").get("confidence").asText());
        assertTrue(root.get("funding").get("current_rate").isNull());
        assertEquals("UNAVAILABLE", root.get("funding").get("confidence").asText());
        for (String k : new String[]{"net_delta_1m", "net_delta_5m", "net_delta_15m", "net_delta_1h"}) {
            assertTrue(root.get("trade_flow").get(k).isNull(), k);
        }
        assertEquals("UNAVAILABLE", root.get("trade_flow").get("confidence").asText());
        assertEquals("UNAVAILABLE", root.get("spot_perp_basis").get("confidence").asText());
        assertEquals("unknown", root.get("spot_perp_basis").get("direction").asText());
        assertEquals("UNAVAILABLE", root.get("oi_breakdown").get("confidence").asText());
        assertTrue(root.get("oi_breakdown").get("retail").isNull());
        assertTrue(root.has("session"));
        assertFalse(root.has("order_flow"));

        Set<String> unavailable = new HashSet<>();
        root.get("data_quality").get("unavailable_fields").forEach(n -> unavailable.add(n.asText()));
        assertTrue(unavailable.containsAll(List.of("spot_perp_basis", "oi_breakdown", "trade_flow.net_delta_1h",
                "conditions.book_imbalance", "order_book_depth.bid_ask_ratio", "funding.current_rate")));
    }

    // ===================================================================================================
    // buildStructure (private, :704) - six timeframe blocks
    // ===================================================================================================

    private static ArrayNode hlcBars(double[][] hlc) {
        ArrayNode out = MAPPER.createArrayNode();
        for (int i = 0; i < hlc.length; i++) {
            out.add(bar(i * 60_000L, hlc[i][2], hlc[i][0], hlc[i][1], hlc[i][2], 1.0, i * 60_000L + 59_999L, 0.5));
        }
        return out;
    }

    @Test
    void buildStructure_sixTimeframeBlocks_andStaleFlags() throws Exception {
        // currentPrice 100.0. Rows are {high, low, close}. Algorithm (:704-742): window = last lookback bars
        // (1w 2, 1d 7, 4h 3, 1h 24, 15m 16, 5m 12); high/low = window extremes; then scanning i = size-2 down to start+1,
        // a close pivot (prev < cur > next) replaces the swing high, (prev > cur < next) the swing low; stale when
        // swingHigh < price or swingLow > price.
        Map<String, JsonNode> mtf = new HashMap<>();
        // 1w: 2 bars, no scan iteration -> high 130, low 80; straddles 100 -> not stale.
        mtf.put("1w", hlcBars(new double[][]{{130, 80, 100}, {125, 85, 110}}));
        // 1d: empty -> zeros + stale (:709-713).
        mtf.put("1d", MAPPER.createArrayNode());
        // 4h: high 92, low 80; i=1 closes 85<90>88 -> swingHigh 90; swingLow stays 80. 90 < 100 -> stale.
        mtf.put("4h", hlcBars(new double[][]{{90, 80, 85}, {92, 82, 90}, {91, 83, 88}}));
        // 1h: high 120, low 90; i=1 closes 100<115>105 -> swingHigh 115; swingLow stays 90. Straddles 100 -> not stale.
        mtf.put("1h", hlcBars(new double[][]{{110, 90, 100}, {120, 95, 115}, {112, 98, 105}}));
        // 15m: high 125, low 110; i=1 closes 115>113<118 -> swingLow 113; swingHigh stays 125. 113 > 100 -> stale.
        mtf.put("15m", hlcBars(new double[][]{{120, 110, 115}, {125, 112, 113}, {122, 111, 118}}));
        // 5m: absent -> zeros + stale.

        ObjectNode st = (ObjectNode) call(new MarketDataSnapshot(), "buildStructure",
                new Class<?>[]{Map.class, double.class}, mtf, 100.0);

        assertBlock(st, "1w", 130.0, 80.0, false);
        assertBlock(st, "1d", 0.0, 0.0, true);
        assertBlock(st, "4h", 90.0, 80.0, true);
        assertBlock(st, "1h", 115.0, 90.0, false);
        assertBlock(st, "15m", 125.0, 113.0, true);
        assertBlock(st, "5m", 0.0, 0.0, true);
        assertEquals(6, st.size());
    }

    private static void assertBlock(ObjectNode st, String tf, double high, double low, boolean stale) {
        JsonNode b = st.get(tf);
        assertEquals(high, b.get("swing_high").asDouble(), 1e-9, tf + " swing_high");
        assertEquals(low, b.get("swing_low").asDouble(), 1e-9, tf + " swing_low");
        assertEquals(stale, b.get("stale").asBoolean(), tf + " stale");
    }

    // ===================================================================================================
    // buildOiBreakdown (private, :1410) and buildSpotPerpBasis (private, :1370)
    // ===================================================================================================

    @Test
    void buildOiBreakdown_nullRatioInput_isUnavailableNeverZero() throws Exception {
        // client returns null for the retail ratio -> NPE inside the try -> catch (:1397-1402 fallback block).
        StubClient s = new StubClient();
        s.retailRatio = MAPPER.nullNode(); // need() only rejects Java null; a JSON null node has size() 0 -> get(-1) null -> NPE
        s.whaleRatio = json("[{\"longShortRatio\":\"1.0\"}]");
        ObjectNode node = (ObjectNode) call(withStub(s), "buildOiBreakdown", new Class<?>[]{String.class}, SYM);
        // B136 residual (B153): a failed fetch is UNAVAILABLE with null blocks, never a fake 0.0 ratio
        assertEquals("UNAVAILABLE", node.get("confidence").asText());
        assertEquals("OI breakdown unavailable", node.get("note").asText());
        for (String k : new String[]{"retail", "whale", "topAccounts"}) {
            assertTrue(node.get(k).isNull(), k);
        }

        // client not configured at all (IOException) takes the same path
        ObjectNode unconfigured = (ObjectNode) call(withStub(new StubClient()), "buildOiBreakdown", new Class<?>[]{String.class}, SYM);
        assertEquals("UNAVAILABLE", unconfigured.get("confidence").asText());
    }

    @Test
    void buildOiBreakdown_ratios_changesAndTopAccountsFallback() throws Exception {
        // retail ratios 1.0 1.1 1.2 1.3 1.5: last 1.5; change_1h = 1.5 - 1.3 = 0.2; change_4h (5 samples) = 1.5 - 1.0 = 0.5.
        // whale 2.0 2.5: last 2.5; change_1h = 0.5; change_4h needs 5 samples -> 0.0.
        StubClient s = new StubClient();
        s.retailRatio = json("[{\"longShortRatio\":\"1.0\"},{\"longShortRatio\":\"1.1\"},{\"longShortRatio\":\"1.2\"},"
                + "{\"longShortRatio\":\"1.3\"},{\"longShortRatio\":\"1.5\"}]");
        s.whaleRatio = json("[{\"longShortRatio\":\"2.0\"},{\"longShortRatio\":\"2.5\"}]");
        // topRatio left null -> the inner catch marks topAccounts null with note "unavailable" (no fake 0.0)
        ObjectNode node = (ObjectNode) call(withStub(s), "buildOiBreakdown", new Class<?>[]{String.class}, SYM);
        assertEquals(1.5, node.get("retail").get("long_short_ratio").asDouble(), 1e-9);
        assertEquals(0.2, node.get("retail").get("change_1h").asDouble(), 1e-9);
        assertEquals(0.5, node.get("retail").get("change_4h").asDouble(), 1e-9);
        assertEquals(2.5, node.get("whale").get("long_short_ratio").asDouble(), 1e-9);
        assertEquals(0.5, node.get("whale").get("change_1h").asDouble(), 1e-9);
        assertEquals(0.0, node.get("whale").get("change_4h").asDouble(), 0.0);
        assertTrue(node.get("topAccounts").isNull());
        assertEquals("unavailable", node.get("topAccounts_note").asText());
        assertEquals("MEDIUM", node.get("confidence").asText());
    }

    @Test
    void buildSpotPerpBasis_premiumDiscountAndFailure() throws Exception {
        // spot 100.0, mark 100.5: (100.5 - 100.0) / 100.0 * 100 = 0.5 % premium; mark 99.0 -> -1.0 % discount.
        StubClient p = new StubClient();
        p.spot = json("{\"price\":\"100.0\"}");
        p.premium = json("{\"markPrice\":\"100.5\"}");
        ObjectNode up = (ObjectNode) call(withStub(p), "buildSpotPerpBasis", new Class<?>[]{String.class}, SYM);
        assertEquals(0.5, up.get("basis_pct").asDouble(), 1e-9);
        assertEquals("premium", up.get("direction").asText());
        assertEquals("HIGH", up.get("confidence").asText());

        StubClient d = new StubClient();
        d.spot = json("{\"price\":\"100.0\"}");
        d.premium = json("{\"markPrice\":\"99.0\"}");
        ObjectNode down = (ObjectNode) call(withStub(d), "buildSpotPerpBasis", new Class<?>[]{String.class}, SYM);
        assertEquals(-1.0, down.get("basis_pct").asDouble(), 1e-9);
        assertEquals("discount", down.get("direction").asText());

        ObjectNode bad = (ObjectNode) call(withStub(new StubClient()), "buildSpotPerpBasis", new Class<?>[]{String.class}, SYM);
        assertEquals("unknown", bad.get("direction").asText());
        assertEquals("LOW", bad.get("confidence").asText());
        assertEquals(0.0, bad.get("basis_pct").asDouble(), 0.0);
    }

    // ===================================================================================================
    // dropFormingBar (private, :453)
    // ===================================================================================================

    @Test
    void dropFormingBar_removesOnlyBarsClosingAfterReference() throws Exception {
        // Binance kline index 6 = close time. Reference 1500: bar closing at 2000 is forming -> dropped; at 1000 -> kept.
        ArrayNode k = MAPPER.createArrayNode();
        k.add(bar(0, 1, 1, 1, 1, 1, 1000L, 0.5));
        k.add(bar(1000, 1, 1, 1, 1, 1, 2000L, 0.5));
        call(new MarketDataSnapshot(), "dropFormingBar", new Class<?>[]{JsonNode.class, long.class}, k, 1500L);
        assertEquals(1, k.size());
        call(new MarketDataSnapshot(), "dropFormingBar", new Class<?>[]{JsonNode.class, long.class}, k, 1500L);
        assertEquals(1, k.size(), "a closed last bar must be kept");
        call(new MarketDataSnapshot(), "dropFormingBar", new Class<?>[]{JsonNode.class, long.class}, null, 1500L); // null-safe
    }

    // ===================================================================================================
    // Persistence helpers (public) - write under the relative runtime_data/snapshots (gitignored); ZZTEST_* only
    // ===================================================================================================

    private static final Path SNAP_DIR = Paths.get("runtime_data", "snapshots");

    private static List<File> zztestFiles() {
        List<File> out = new ArrayList<>();
        File[] all = SNAP_DIR.toFile().listFiles();
        if (all != null) for (File f : all) if (f.getName().startsWith("ZZTEST_")) out.add(f);
        return out;
    }

    private static void cleanZztest() {
        for (File f : zztestFiles()) f.delete();
    }

    @Test
    void saveSnapshot_writesJsonUnderRuntimeDataSnapshots() throws Exception {
        // :1455-1464 file name symbol_<LocalDate>_<epochMillis>.json in runtime_data/snapshots, content = snapshot JSON.
        cleanZztest();
        try {
            StubClient s = stubWith(closedBars(nowMs(), 3, i -> 100.0, 10.0, 5.0));
            withStub(s).saveSnapshot("ZZTEST", null);
            List<File> written = zztestFiles();
            assertEquals(1, written.size());
            assertTrue(Pattern.matches("ZZTEST_\\d{4}-\\d{2}-\\d{2}_\\d+\\.json", written.get(0).getName()), written.get(0).getName());
            JsonNode back = MAPPER.readTree(Files.readAllBytes(written.get(0).toPath()));
            assertEquals("ZZTEST", back.get("asset").asText());
            assertTrue(back.has("current_price"));
        } finally {
            cleanZztest();
        }
    }

    @Test
    void saveHistoricalSnapshot_fileNamePattern() throws Exception {
        // :1307-1316 symbol + "_historical_" + asOf with ':' and '-' removed + ".json".
        // 2026-10-01T12:00:00Z -> strip ':' and '-' -> 20261001T120000Z (by hand).
        cleanZztest();
        try {
            StubClient s = stubWith(closedBars(AS_OF.toEpochMilli(), 3, i -> 100.0, 10.0, 5.0));
            withStub(s).saveHistoricalSnapshot("ZZTEST", AS_OF);
            List<File> written = zztestFiles();
            assertEquals(1, written.size());
            assertEquals("ZZTEST_historical_20261001T120000Z.json", written.get(0).getName());
            assertEquals("2026-10-01T12:00:00Z", MAPPER.readTree(Files.readAllBytes(written.get(0).toPath())).get("timestamp_utc").asText());
        } finally {
            cleanZztest();
        }
    }

    @Test
    void shutdown_delegatesToClient() throws Exception {
        StubClient s = new StubClient();
        MarketDataSnapshot m = withStub(s);
        assertEquals(0, s.shutdownCalls);
        m.shutdown();
        assertEquals(1, s.shutdownCalls);
    }
}
