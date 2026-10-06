package datafeed;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
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
}
