package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.SocketTimeoutException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicBoolean;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * T037: StateCodeEmitter signal and state-machine rules (design state_machine_design_2026-09-11.md as summarised in the
 * class header: codes A, A>S, A>L, S, S>L, L, L>S; five signals; 3 signals minimum). Only the pure helpers are exercised
 * (reflection; the emitter is never connected, started or told to emit, so no state_code.json / session log is written).
 * Signal results are Dir enum values (private), compared by name; null means "signal unavailable".
 * Windows are in milliseconds against an explicit nowT, so no wall clock is involved except where nowMsOverride pins it.
 */
public class StateCodeEmitterTest {

    private static final long NOW = 3_600_000L;

    private static StateCodeEmitter emitter() throws Exception {
        StateCodeEmitter e = new StateCodeEmitter("BTCUSDT");
        e.nowMsOverride = NOW;
        return e;
    }

    private static Object tick(long t, double qty, boolean buyerMaker) throws Exception {
        Class<?> c = Class.forName("datafeed.StateCodeEmitter$Tick");
        Constructor<?> k = c.getDeclaredConstructor(long.class, double.class, double.class, boolean.class);
        k.setAccessible(true);
        return k.newInstance(t, 100.0, qty, buyerMaker);
    }

    private static String invoke(StateCodeEmitter e, String name, Class<?>[] types, Object... args) throws Exception {
        Method m = StateCodeEmitter.class.getDeclaredMethod(name, types);
        m.setAccessible(true);
        Object r = m.invoke(e, args);
        return r == null ? null : r.toString();
    }

    private static String ticksSignal(String name, long nowT, List<Object> ticks) throws Exception {
        return invoke(emitter(), name, new Class<?>[]{List.class, long.class}, ticks, nowT);
    }

    private static String next(String state, int bearish, int bullish) throws Exception {
        return invoke(emitter(), "nextTarget", new Class<?>[]{String.class, int.class, int.class}, state, bearish, bullish);
    }

    // ---------- nextTarget: state machine table ----------

    @Test
    public void quietStateMovesTowardTheMajorityDirection() throws Exception {
        assertEquals("A>S", next("A", 2, 1));
        assertEquals("A>S", next("A", 5, 0));
        assertEquals("A>L", next("A", 1, 2));
        assertNull(next("A", 2, 2));
        assertNull(next("A", 0, 0));
        assertNull(next("A", 1, 1));
    }

    @Test
    public void transitionalStatesNeedThreeVotes() throws Exception {
        assertEquals("S", next("A>S", 3, 0));
        assertNull(next("A>S", 2, 0));
        assertEquals("L", next("A>L", 0, 3));
        assertNull(next("A>L", 0, 2));
    }

    @Test
    public void establishedStatesFlipOnOppositeThreeVotes() throws Exception {
        assertEquals("S>L", next("S", 0, 3));
        assertNull(next("S", 3, 0));
        assertEquals("L>S", next("L", 3, 0));
        assertNull(next("L", 0, 3));
    }

    @Test
    public void reversalStatesResolveToEitherSide() throws Exception {
        assertEquals("L", next("S>L", 0, 3));
        assertEquals("S", next("S>L", 3, 0));
        assertEquals("S", next("L>S", 3, 0));
        assertEquals("L", next("L>S", 0, 3));
        assertNull(next("S>L", 1, 1));
    }

    @Test
    public void unknownStateHasNoTarget() throws Exception {
        assertNull(next("X", 5, 5));
    }

    // ---------- computePriceVsVwap: neutral band +-0.05% ----------

    private static String pvv(double price, double cumPV, double cumVol) throws Exception {
        return invoke(emitter(), "computePriceVsVwap", new Class<?>[]{double.class, double.class, double.class},
                price, cumPV, cumVol);
    }

    @Test
    public void priceVersusVwapUsesNeutralBand() throws Exception {
        // cumPV 1000 / cumVol 10 -> vwap 100
        assertEquals("NEUTRAL", pvv(100.04, 1000, 10));   // +0.04% inside the 0.05% band
        assertEquals("NEUTRAL", pvv(99.96, 1000, 10));
        assertEquals("BULLISH", pvv(100.10, 1000, 10));   // +0.10%
        assertEquals("BEARISH", pvv(99.90, 1000, 10));
    }

    @Test
    public void priceVersusVwapUnavailableWithoutVolumeOrPrice() throws Exception {
        assertNull(pvv(100.0, 0, 0));
        assertNull(pvv(0.0, 1000, 10));
    }

    // ---------- computeNetDelta1m ----------

    @Test
    public void netDelta1mSumsSignedVolumeInLastMinute() throws Exception {
        List<Object> t = new ArrayList<>();
        t.add(tick(NOW - 10_000, 2.0, false));   // +2 (buyer is taker)
        t.add(tick(NOW - 20_000, 1.0, true));    // -1
        t.add(tick(NOW - 120_000, 100.0, true)); // outside the window, ignored
        assertEquals("BULLISH", ticksSignal("computeNetDelta1m", NOW, t));
    }

    @Test
    public void netDelta1mBearishAndNeutralAndEmpty() throws Exception {
        List<Object> bear = new ArrayList<>();
        bear.add(tick(NOW - 10_000, 1.0, false));
        bear.add(tick(NOW - 20_000, 3.0, true));
        assertEquals("BEARISH", ticksSignal("computeNetDelta1m", NOW, bear));

        List<Object> flat = new ArrayList<>();
        flat.add(tick(NOW - 10_000, 1.0, false));
        flat.add(tick(NOW - 20_000, 1.0, true));
        assertEquals("NEUTRAL", ticksSignal("computeNetDelta1m", NOW, flat));

        assertNull(ticksSignal("computeNetDelta1m", NOW, new ArrayList<>()));
    }

    // ---------- computeLast3Delta: three consecutive one-minute buckets ----------

    @Test
    public void last3DeltaNeedsAllThreeBucketsSameSign() throws Exception {
        List<Object> bull = new ArrayList<>();
        bull.add(tick(NOW - 30_000, 1.0, false));   // bucket 2
        bull.add(tick(NOW - 90_000, 1.0, false));   // bucket 1
        bull.add(tick(NOW - 150_000, 1.0, false));  // bucket 0
        assertEquals("BULLISH", ticksSignal("computeLast3Delta", NOW, bull));

        List<Object> bear = new ArrayList<>();
        bear.add(tick(NOW - 30_000, 1.0, true));
        bear.add(tick(NOW - 90_000, 1.0, true));
        bear.add(tick(NOW - 150_000, 1.0, true));
        assertEquals("BEARISH", ticksSignal("computeLast3Delta", NOW, bear));

        List<Object> mixed = new ArrayList<>();
        mixed.add(tick(NOW - 30_000, 1.0, false));
        mixed.add(tick(NOW - 90_000, 1.0, true));
        mixed.add(tick(NOW - 150_000, 1.0, false));
        assertEquals("NEUTRAL", ticksSignal("computeLast3Delta", NOW, mixed));
    }

    @Test
    public void last3DeltaUnavailableWhenABucketHasNoTicks() throws Exception {
        List<Object> t = new ArrayList<>();
        t.add(tick(NOW - 30_000, 1.0, false));
        t.add(tick(NOW - 150_000, 1.0, false));   // bucket 1 empty
        assertNull(ticksSignal("computeLast3Delta", NOW, t));
    }

    // ---------- computeVolumeRatio: last minute vs 30-minute per-minute baseline, threshold 2.0 ----------

    private static List<Object> baseline(int minutes) throws Exception {
        // one tick of qty 1 in each of `minutes` distinct historical minutes (window starts at NOW - 1_860_000)
        List<Object> t = new ArrayList<>();
        for (int i = 0; i < minutes; i++) t.add(tick(NOW - 1_860_000 + i * 60_000L + 1_000, 1.0, false));
        return t;
    }

    @Test
    public void volumeRatioAtOrAboveTwoFollowsNetDirection() throws Exception {
        List<Object> up = baseline(10);
        up.add(tick(NOW - 10_000, 2.5, false));          // ratio 2.5 / 1.0, net buy
        assertEquals("BULLISH", ticksSignal("computeVolumeRatio", NOW, up));

        List<Object> down = baseline(10);
        down.add(tick(NOW - 10_000, 2.5, true));         // ratio 2.5, net sell
        assertEquals("BEARISH", ticksSignal("computeVolumeRatio", NOW, down));
    }

    @Test
    public void volumeRatioBelowTwoIsNeutral() throws Exception {
        List<Object> t = baseline(10);
        t.add(tick(NOW - 10_000, 1.5, false));           // ratio 1.5 < 2.0
        assertEquals("NEUTRAL", ticksSignal("computeVolumeRatio", NOW, t));
    }

    @Test
    public void volumeRatioUnavailableWithFewerThanTenBaselineMinutes() throws Exception {
        List<Object> t = baseline(9);
        t.add(tick(NOW - 10_000, 5.0, false));
        assertNull(ticksSignal("computeVolumeRatio", NOW, t));
    }

    // ---------- computeCvdSlope: ring of session CVD samples, needs 10, +-2% older-vs-recent half ----------

    private static String cvdAfter(double... samples) throws Exception {
        StateCodeEmitter e = emitter();
        String last = null;
        for (double s : samples) last = invoke(e, "computeCvdSlope", new Class<?>[]{double.class}, s);
        return last;
    }

    @Test
    public void cvdSlopeUnavailableBeforeTenSamples() throws Exception {
        assertNull(cvdAfter(100, 100, 100, 100, 100, 200, 200, 200, 200));   // 9 samples
    }

    @Test
    public void cvdSlopeRisingFallingFlat() throws Exception {
        // 10 samples: older half avg 100, recent half avg 200 -> change +100% (> +2%)
        assertEquals("BULLISH", cvdAfter(100, 100, 100, 100, 100, 200, 200, 200, 200, 200));
        // older 200, recent 100 -> -50%
        assertEquals("BEARISH", cvdAfter(200, 200, 200, 200, 200, 100, 100, 100, 100, 100));
        // identical samples -> 0%
        assertEquals("NEUTRAL", cvdAfter(100, 100, 100, 100, 100, 100, 100, 100, 100, 100));
    }

    // ---------- buildTrigger ----------

    @Test
    public void triggerListsOnlyAvailableSignalsInOrder() throws Exception {
        String t = invoke(emitter(), "buildTrigger", new Class<?>[]{Object[].class},
                (Object) new Object[]{null, "x", null, "y", "z"});
        assertEquals("last_3_delta,cvd_slope,price_vs_vwap", t);
    }

    // ---------- static helpers ----------

    @Test
    public void weekendIsSaturdayAndSundayUtc() throws Exception {
        Method m = StateCodeEmitter.class.getDeclaredMethod("isWeekend", long.class);
        m.setAccessible(true);
        long sat = 1_704_499_200_000L;           // 2024-01-06T00:00:00Z, a Saturday
        long day = 86_400_000L;
        assertFalse((boolean) m.invoke(null, sat - day));       // Friday
        assertTrue((boolean) m.invoke(null, sat));              // Saturday
        assertTrue((boolean) m.invoke(null, sat + day));        // Sunday
        assertFalse((boolean) m.invoke(null, sat + 2 * day));   // Monday
    }

    @Test
    public void utcDayStartTruncatesToMidnight() throws Exception {
        Method m = StateCodeEmitter.class.getDeclaredMethod("utcDayStart", long.class);
        m.setAccessible(true);
        long midnight = 1_704_499_200_000L;
        assertEquals(midnight, (long) m.invoke(null, midnight + 5 * 3_600_000L + 123));
        assertEquals(midnight, (long) m.invoke(null, midnight));
    }

    // ======================================================================================================
    // state-code-accumulator-backfill (audit M1/M2): session CVD / VWAP sums are re-seeded from fapi 1m klines
    // on start and after every WS gap, stitched to live ticks at the last closed minute boundary M, and the
    // two accumulator signals plus the state letter fail closed (INVALID) while the sums are missing/partial.
    // The klines source is an injectable seam (no network); time is pinned through the nowMs seam.
    // ======================================================================================================

    private static final long MIN = 60_000L;
    private static final long D0 = Instant.parse("2026-10-20T00:00:00Z").toEpochMilli();
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @TempDir
    Path tmp;

    /** One closed 1m bar: [openTime, o, h, l, c, volume, closeTime, quoteVolume, trades, takerBuyBase, takerBuyQuote, ignore]. */
    private static JsonNode bar(long openTime, double vol, double takerBuyBase, double quoteVol) {
        ArrayNode r = JsonNodeFactory.instance.arrayNode();
        r.add(openTime).add("100").add("101").add("99").add("100")
         .add(String.valueOf(vol)).add(openTime + MIN - 1).add(String.valueOf(quoteVol))
         .add(10).add(String.valueOf(takerBuyBase)).add("0").add("0");
        return r;
    }

    /** n constant bars from day start: volume 10, takerBuy 7 (cvd +4/bar), quote 1000. */
    private static ArrayNode constBars(long dayStart, int n) {
        ArrayNode a = JsonNodeFactory.instance.arrayNode();
        for (int i = 0; i < n; i++) a.add(bar(dayStart + i * MIN, 10.0, 7.0, 1000.0));
        return a;
    }

    private interface Behaviour { JsonNode run(long startMs, long endMs) throws Exception; }

    private static final class FakeKlines implements StateCodeEmitter.KlineSource {
        final AtomicInteger calls = new AtomicInteger();
        volatile long lastStart = -1, lastEnd = -1;
        volatile Behaviour behaviour = (st, en) -> constBars(st, (int) ((en + 1 - st) / MIN));
        public JsonNode fetch(String symbol, long startMs, long endMs) throws Exception {
            calls.incrementAndGet();
            lastStart = startMs; lastEnd = endMs;
            return behaviour.run(startMs, endMs);
        }
    }

    private StateCodeEmitter fresh(FakeKlines src, long now) throws Exception {
        StateCodeEmitter e = new StateCodeEmitter("BTCUSDT", tmp.resolve("state_code.json"), src);
        e.nowMsOverride = now;
        return e;
    }

    private static String trade(long T, double price, double qty, boolean buyerMaker) {
        return "{\"e\":\"aggTrade\",\"E\":" + T + ",\"s\":\"BTCUSDT\",\"a\":1,\"p\":\"" + price + "\",\"q\":\"" + qty
                + "\",\"f\":1,\"l\":1,\"T\":" + T + ",\"m\":" + buyerMaker + "}";
    }

    private JsonNode emit(StateCodeEmitter e) throws Exception {
        e.evaluateAndEmit();
        return MAPPER.readTree(tmp.resolve("state_code.json").toFile());
    }

    private static void assertInvalid(JsonNode j) {
        assertFalse(j.get("session_accumulators_valid").asBoolean());
        assertEquals("INVALID", j.get("state").asText());
        assertTrue(j.get("signals").get("cvd_slope").isNull());
        assertTrue(j.get("signals").get("price_vs_vwap").isNull());
        assertTrue(j.get("session_cvd").isNull());
        assertTrue(j.get("session_cum_pv").isNull());
        assertTrue(j.get("session_cum_vol").isNull());
        assertFalse(j.get("session_accumulators_reason").asText().isEmpty());
    }

    private static final long CONNECT = D0 + 5 * 3_600_000L + 28 * MIN + 10_000L;   // 05:28:10
    private static final long NOW1 = D0 + 5 * 3_600_000L + 30 * MIN + 20_000L;      // 05:30:20 -> M = 05:30:00
    private static final long M1 = D0 + 5 * 3_600_000L + 30 * MIN;
    private static final int BARS1 = 330;

    // (a) restart mid-session with stale restored sums: the emitted sums are kline totals + post-boundary ticks
    @Test
    public void restartReplacesStaleRestoredSumsWithBackfill() throws Exception {
        Files.writeString(tmp.resolve("state_code.json"),
                "{\"state\":\"S\",\"timestamp_utc\":\"2026-10-20T05:20:00Z\",\"session_day_start_ms\":" + D0
                        + ",\"session_cvd\":999.0,\"session_cum_pv\":9.9E9,\"session_cum_vol\":5000.0}");
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        e.onMessage(trade(CONNECT + 20_000L, 100.0, 1.0, false));   // 05:28:30 < M: inside the klines, must be dropped
        e.onMessage(trade(M1 + 5_000L, 101.0, 2.0, false));         // +2
        e.onMessage(trade(M1 + 10_000L, 99.0, 0.5, true));          // -0.5

        assertInvalid(emit(e));                                      // restored 999 / 9.9E9 never shown as a session value
        assertTrue(e.backfillNow());
        assertEquals(D0, src.lastStart);
        assertEquals(M1 - 1, src.lastEnd);
        JsonNode j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        assertEquals(330 * 4.0 + 1.5, j.get("session_cvd").asDouble(), 1e-6);
        assertEquals(3300.0 + 2.5, j.get("session_cum_vol").asDouble(), 1e-6);
        assertEquals(330 * 1000.0 + 2 * 101.0 + 0.5 * 99.0, j.get("session_cum_pv").asDouble(), 1e-6);
        assertTrue(j.get("signals").get("cvd_slope").isNull());      // ring was cleared: the jump cannot read as slope
    }

    // (b) WS reconnect gap: sums = kline totals + ticks with T >= M; a tick with T < M is not counted twice
    @Test
    public void reconnectGapSeamIsExact() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        assertTrue(e.backfillNow());
        e.onMessage(trade(M1 + 15_000L, 100.0, 4.0, false));         // live, counted once

        long closedAt = M1 + 70_000L;                                 // 05:31:10 socket drops
        e.onStreamClosed("ws_closed");
        assertInvalid(emit(e));
        e.onMessage(trade(closedAt + 5_000L, 100.0, 9.0, false));     // arrives while invalid: buffered, not summed
        assertInvalid(emit(e));

        long reopen = M1 + 2 * MIN + 5_000L;                          // 05:32:05 reconnect
        e.onStreamOpen(reopen);
        e.onMessage(trade(reopen + 10_000L, 100.0, 1.0, false));      // 05:32:15 < M2: inside the new klines
        long m2 = M1 + 3 * MIN;                                       // 05:33:00
        e.nowMsOverride = m2 + 12_000L;                               // 05:33:12
        e.onMessage(trade(m2 + 2_000L, 100.0, 3.0, true));            // >= M2: counted (-3)
        e.onMessage(trade(m2 + 4_000L, 102.0, 2.0, false));           // >= M2: counted (+2)
        assertTrue(e.backfillNow());
        assertEquals(m2 - 1, src.lastEnd);
        JsonNode j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        int bars = (int) ((m2 - D0) / MIN);
        assertEquals(bars * 4.0 - 1.0, j.get("session_cvd").asDouble(), 1e-6);
        assertEquals(bars * 10.0 + 5.0, j.get("session_cum_vol").asDouble(), 1e-6);
        assertEquals(bars * 1000.0 + 300.0 + 204.0, j.get("session_cum_pv").asDouble(), 1e-6);
    }

    @Test
    public void latePreBoundaryTickAfterBackfillDoesNotChangeSessionSums() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        assertTrue(e.backfillNow());
        JsonNode before = emit(e);
        assertEquals(1320.0, before.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3300.0, before.get("session_cum_vol").asDouble(), 1e-9);

        // A delayed buy from a minute already represented by the closed klines.
        e.onMessage(trade(M1 - 1, 100.0, 2.0, false));
        JsonNode after = emit(e);
        assertEquals(1320.0, after.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3300.0, after.get("session_cum_vol").asDouble(), 1e-9);
        e.onMessage(trade(M1, 100.0, 2.0, false));
        JsonNode atBoundary = emit(e);
        assertEquals(1322.0, atBoundary.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3302.0, atBoundary.get("session_cum_vol").asDouble(), 1e-9);
    }

    @Test
    public void lateSeamTickIsFilteredAfterReconnectAndAcrossMidnight() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        assertTrue(e.backfillNow());
        e.onStreamClosed("reconnect_seam");
        long reconnect = M1 + MIN + 10_000L;
        long reconnectM = M1 + 2 * MIN;
        e.onStreamOpen(reconnect);
        e.nowMsOverride = reconnectM + 20_000L;
        assertTrue(e.backfillNow());
        e.onMessage(trade(reconnectM - 1, 100.0, 2.0, false));
        JsonNode afterLateReconnectTick = emit(e);
        assertEquals(1328.0, afterLateReconnectTick.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3320.0, afterLateReconnectTick.get("session_cum_vol").asDouble(), 1e-9);
        e.onMessage(trade(reconnectM, 100.0, 2.0, false));
        JsonNode atReconnectBoundary = emit(e);
        assertEquals(1330.0, atReconnectBoundary.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3322.0, atReconnectBoundary.get("session_cum_vol").asDouble(), 1e-9);

        long midnightM = D0 + MIN;
        StateCodeEmitter midnight = fresh(src, midnightM + 20_000L);
        midnight.onStreamOpen(D0 - 20_000L);
        assertTrue(midnight.backfillNow());
        midnight.onMessage(trade(midnightM - 1, 100.0, 2.0, false));
        JsonNode afterLateMidnightTick = emit(midnight);
        assertEquals(4.0, afterLateMidnightTick.get("session_cvd").asDouble(), 1e-9);
        assertEquals(10.0, afterLateMidnightTick.get("session_cum_vol").asDouble(), 1e-9);
        midnight.onMessage(trade(midnightM, 100.0, 2.0, false));
        JsonNode atMidnightBoundary = emit(midnight);
        assertEquals(6.0, atMidnightBoundary.get("session_cvd").asDouble(), 1e-9);
        assertEquals(12.0, atMidnightBoundary.get("session_cum_vol").asDouble(), 1e-9);
    }

    @Test
    public void closeBetweenEmitSnapshotAndPublishCannotRepublishValidState() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        assertTrue(e.backfillNow());
        PrintStream original = System.out;
        AtomicBoolean closed = new AtomicBoolean(false);
        PrintStream intercept = new PrintStream(new OutputStream() {
            private final StringBuilder line = new StringBuilder();
            @Override public void write(int b) {
                if (b == '\n') {
                    if (line.toString().startsWith("[StateCode] emit") && closed.compareAndSet(false, true))
                        e.onStreamClosed("test_close_at_emit_log");
                    line.setLength(0);
                } else if (line.length() < 200) line.append((char) b);
            }
        }, true);
        try {
            System.setOut(intercept);
            assertInvalid(emit(e));
            assertTrue(closed.get(), "close callback must run between snapshot and publication");
        } finally {
            System.setOut(original);
            intercept.close();
        }
    }

    // (c) backfill failure of every kind: INVALID, signals null, retry delay 30 s, recovers on a later success
    @Test
    public void backfillErrorsFailClosedAndRecover() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        e.onMessage(trade(M1 + 5_000L, 100.0, 1.0, false));

        Behaviour[] bad = new Behaviour[]{
                (st, en) -> { throw new IOException("HTTP 429"); },
                (st, en) -> { throw new SocketTimeoutException("timeout"); },
                (st, en) -> constBars(st, BARS1 - 1),                                    // short list
                (st, en) -> constBars(st, BARS1 + 1),                                    // long list
                (st, en) -> null,
                (st, en) -> { ArrayNode a = constBars(st, BARS1);                        // duplicate openTime
                              a.set(10, a.get(9)); return a; },
                (st, en) -> { ArrayNode a = constBars(st, BARS1);                        // non-monotonic
                              JsonNode x = a.get(20); a.set(20, a.get(21)); a.set(21, x); return a; },
                (st, en) -> { ArrayNode a = constBars(st, BARS1);                        // malformed row
                              ((ArrayNode) a.get(5)).removeAll(); return a; },
        };
        for (Behaviour b : bad) {
            src.behaviour = b;
            assertFalse(e.backfillNow());
            assertEquals(30_000L, e.retryDelayMs);
            for (int i = 0; i < 12; i++) assertInvalid(emit(e));   // 12 emits: the cvd ring must not fill up either
        }
        src.behaviour = (st, en) -> constBars(st, (int) ((en + 1 - st) / MIN));
        assertTrue(e.backfillNow());
        JsonNode j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        assertEquals(BARS1 * 4.0 + 1.0, j.get("session_cvd").asDouble(), 1e-6);
    }

    // (d) continuous control: no gap, sums equal the plain tick sums exactly (zero klines needed, no HTTP)
    @Test
    public void continuousStreamSumsEqualPlainTickSums() throws Exception {
        FakeKlines src = new FakeKlines();
        src.behaviour = (st, en) -> { throw new AssertionError("no klines are needed at the day start"); };
        StateCodeEmitter e = fresh(src, D0 + 30_000L);
        e.onStreamOpen(D0 - 10_000L);                                  // stream already running before midnight
        e.onMessage(trade(D0 - 5_000L, 100.0, 7.0, false));            // previous day: never in today's sums
        assertTrue(e.backfillNow());
        assertEquals(0, src.calls.get());
        Random rnd = new Random(42);
        double cvd = 0, vol = 0, pv = 0;
        for (int i = 0; i < 500; i++) {
            long t = D0 + 1_000L + i * 40L;
            double px = 100 + rnd.nextInt(500) / 10.0, q = 0.001 + rnd.nextInt(2000) / 1000.0;
            boolean m = rnd.nextBoolean();
            e.onMessage(trade(t, px, q, m));
            cvd += m ? -q : q; vol += q; pv += px * q;
        }
        JsonNode j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        assertEquals(cvd, j.get("session_cvd").asDouble(), 1e-9);
        assertEquals(vol, j.get("session_cum_vol").asDouble(), 1e-9);
        assertEquals(pv, j.get("session_cum_pv").asDouble(), 1e-6);
    }

    // (e) a non-trade message (or garbage) leaves the sums unchanged and is not buffered while invalid
    @Test
    public void nonTradeMessageLeavesSumsUnchanged() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        e.onMessage("{\"e\":\"depthUpdate\",\"T\":" + (M1 + 1_000L) + ",\"p\":\"1\",\"q\":\"50\",\"m\":false}");   // before backfill
        assertTrue(e.backfillNow());
        JsonNode before = emit(e);
        e.onMessage("{\"result\":null,\"id\":1}");
        e.onMessage("{\"e\":\"markPriceUpdate\",\"T\":" + (M1 + 2_000L) + ",\"p\":\"77\",\"q\":\"9\",\"m\":true}");
        e.onMessage("not json at all");
        JsonNode after = emit(e);
        assertTrue(after.get("session_accumulators_valid").asBoolean());
        assertEquals(before.get("session_cvd").asDouble(), after.get("session_cvd").asDouble(), 0.0);
        assertEquals(before.get("session_cum_vol").asDouble(), after.get("session_cum_vol").asDouble(), 0.0);
        assertEquals(before.get("session_cum_pv").asDouble(), after.get("session_cum_pv").asDouble(), 0.0);
        assertEquals(330 * 4.0, after.get("session_cvd").asDouble(), 1e-9);
    }

    // (f) replay: klines built from the same ticks; the restarted emitter reproduces the full-day tick/kline CVD within 0.1 BTC
    @Test
    public void replayFixtureCvdMatchesKlinesWithinTenthOfABtc() throws Exception {
        Random rnd = new Random(7);
        int n = 30_000;
        long span = NOW1 - D0 - 2_000L;
        long[] ts = new long[n];
        for (int i = 0; i < n; i++) ts[i] = D0 + (long) (rnd.nextDouble() * span);
        java.util.Arrays.sort(ts);
        int minutes = (int) ((M1 - D0) / MIN);
        double[] vol = new double[minutes], tbb = new double[minutes], qv = new double[minutes];
        double plainCvd = 0, plainVol = 0, plainPv = 0, klineCvd = 0;
        double[] px = new double[n], q = new double[n];
        boolean[] mk = new boolean[n];
        for (int i = 0; i < n; i++) {
            px[i] = 80_000 + rnd.nextInt(2000) / 10.0; q[i] = 0.001 + rnd.nextInt(3000) / 1000.0; mk[i] = rnd.nextBoolean();
            plainCvd += mk[i] ? -q[i] : q[i]; plainVol += q[i]; plainPv += px[i] * q[i];
            int b = (int) ((ts[i] - D0) / MIN);
            if (b < minutes) { vol[b] += q[i]; qv[b] += px[i] * q[i]; if (!mk[i]) tbb[b] += q[i]; }
        }
        for (int b = 0; b < minutes; b++) klineCvd += 2 * tbb[b] - vol[b];
        FakeKlines src = new FakeKlines();
        src.behaviour = (st, en) -> {
            ArrayNode a = JsonNodeFactory.instance.arrayNode();
            for (int b = 0; b < (en + 1 - st) / MIN; b++) a.add(bar(st + b * MIN, vol[b], tbb[b], qv[b]));
            return a;
        };
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        for (int i = 0; i < n; i++) if (ts[i] >= CONNECT) e.onMessage(trade(ts[i], px[i], q[i], mk[i]));   // restart: only post-connect ticks
        assertTrue(e.backfillNow());
        JsonNode j = emit(e);
        assertEquals(plainCvd, j.get("session_cvd").asDouble(), 0.1);
        assertEquals(plainVol, j.get("session_cum_vol").asDouble(), 0.1);
        assertEquals(plainPv, j.get("session_cum_pv").asDouble(), 1.0);
        double tail = 0;
        for (int i = 0; i < n; i++) if (ts[i] >= M1) tail += mk[i] ? -q[i] : q[i];
        assertEquals(klineCvd + tail, j.get("session_cvd").asDouble(), 0.1);
    }

    // day rollover: continuous stream resets to zero at 00:00Z as before; rollover while INVALID re-backfills the NEW day
    @Test
    public void dayRolloverContinuousResetsAndInvalidRebackfillsNewDay() throws Exception {
        long prev = D0 - 86_400_000L;
        FakeKlines src = new FakeKlines();
        long now = prev + 23 * 3_600_000L + 50 * MIN + 20_000L;
        StateCodeEmitter e = fresh(src, now);
        e.onStreamOpen(prev + 23 * 3_600_000L);
        assertTrue(e.backfillNow());
        assertEquals(prev, src.lastStart);
        e.onMessage(trade(D0 - 10_000L, 100.0, 1.0, false));
        e.onMessage(trade(D0 + 5_000L, 100.0, 3.0, true));            // new day: sums restart from this tick
        JsonNode j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        assertEquals(-3.0, j.get("session_cvd").asDouble(), 1e-9);
        assertEquals(3.0, j.get("session_cum_vol").asDouble(), 1e-9);
        assertEquals(D0, j.get("session_day_start_ms").asLong());

        e.onStreamClosed("ws_closed");                                  // gap over midnight
        e.onStreamOpen(D0 + 10_000L);
        e.nowMsOverride = D0 + 80_000L;                                 // 00:01:20 -> M = 00:01:00, one bar of the NEW day
        e.onMessage(trade(D0 + 61_000L, 100.0, 2.0, false));
        assertTrue(e.backfillNow());
        assertEquals(D0, src.lastStart);
        assertEquals(D0 + MIN - 1, src.lastEnd);
        j = emit(e);
        assertEquals(4.0 + 2.0, j.get("session_cvd").asDouble(), 1e-9);
        assertEquals(10.0 + 2.0, j.get("session_cum_vol").asDouble(), 1e-9);
    }

    // seam timing: a backfill is only accepted for a boundary M that lies after the (re)connect, otherwise [M, connect) is missing
    @Test
    public void backfillWaitsForAMinuteBoundaryAfterTheConnect() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, M1 + 20_000L);                 // 05:30:20
        e.onStreamOpen(M1 + 10_000L);                                   // connected 05:30:10: trades 05:30:00-05:30:10 were never seen
        assertFalse(e.backfillNow());
        assertEquals(0, src.calls.get());
        assertInvalid(emit(e));
        assertTrue(e.retryDelayMs >= 1_000L && e.retryDelayMs <= 65_000L);
        e.nowMsOverride = M1 + MIN + 20_000L;                           // 05:31:20 -> M = 05:31:00 > connect
        assertTrue(e.backfillNow());
        assertEquals(M1 + MIN - 1, src.lastEnd);
    }

    // a socket close wipes valid sums and the cvd ring: the post-backfill jump must not read as slope
    @Test
    public void closeInvalidatesAndClearsTheCvdRing() throws Exception {
        FakeKlines src = new FakeKlines();
        StateCodeEmitter e = fresh(src, NOW1);
        e.onStreamOpen(CONNECT);
        assertTrue(e.backfillNow());
        JsonNode j = null;
        for (int i = 0; i < 12; i++) {
            e.onMessage(trade(M1 + 1_000L + i * 1_000L, 100.0, 20.0 * (i + 1), false));
            j = emit(e);
        }
        assertFalse(j.get("signals").get("cvd_slope").isNull());        // ring full while valid
        e.onStreamClosed("ws_closed");
        assertInvalid(emit(e));
        e.onStreamOpen(M1 + 3 * MIN);
        e.nowMsOverride = M1 + 4 * MIN + 20_000L;
        assertTrue(e.backfillNow());
        j = emit(e);
        assertTrue(j.get("session_accumulators_valid").asBoolean());
        assertTrue(j.get("signals").get("cvd_slope").isNull());         // fresh ring: 1 sample
    }
}
