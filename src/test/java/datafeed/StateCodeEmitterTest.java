package datafeed;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for StateCodeEmitter pure computation methods.
 * Tests current behavior of directional signal calculation and state transitions.
 * Private methods are tested via reflection following existing project patterns.
 */
public class StateCodeEmitterTest {

    /**
     * Helper: create a Tick using reflection
     */
    private static Object createTick(long T, double price, double qty, boolean buyerMaker)
            throws Exception {
        Class<?> tickClass = Class.forName("datafeed.StateCodeEmitter$Tick");
        Constructor<?> ctor = tickClass.getDeclaredConstructor(long.class, double.class, double.class, boolean.class);
        ctor.setAccessible(true);
        return ctor.newInstance(T, price, qty, buyerMaker);
    }

    /**
     * Helper: get Dir enum value
     */
    private static Object getDirBullish() throws Exception {
        Class<?> dirClass = Class.forName("datafeed.StateCodeEmitter$Dir");
        return dirClass.getField("BULLISH").get(null);
    }

    private static Object getDirBearish() throws Exception {
        Class<?> dirClass = Class.forName("datafeed.StateCodeEmitter$Dir");
        return dirClass.getField("BEARISH").get(null);
    }

    private static Object getDirNeutral() throws Exception {
        Class<?> dirClass = Class.forName("datafeed.StateCodeEmitter$Dir");
        return dirClass.getField("NEUTRAL").get(null);
    }

    /**
     * Helper: invoke computeNetDelta1m method
     */
    private static Object computeNetDelta1m(Object emitter, List<?> snap, long nowT)
            throws Exception {
        Method m = emitter.getClass().getDeclaredMethod("computeNetDelta1m", List.class, long.class);
        m.setAccessible(true);
        return m.invoke(emitter, snap, nowT);
    }

    /**
     * Helper: invoke computeLast3Delta method
     */
    private static Object computeLast3Delta(Object emitter, List<?> snap, long nowT)
            throws Exception {
        Method m = emitter.getClass().getDeclaredMethod("computeLast3Delta", List.class, long.class);
        m.setAccessible(true);
        return m.invoke(emitter, snap, nowT);
    }

    /**
     * Helper: invoke computeVolumeRatio method
     */
    private static Object computeVolumeRatio(Object emitter, List<?> snap, long nowT)
            throws Exception {
        Method m = emitter.getClass().getDeclaredMethod("computeVolumeRatio", List.class, long.class);
        m.setAccessible(true);
        return m.invoke(emitter, snap, nowT);
    }

    /**
     * Helper: invoke nextTarget method
     */
    private static String nextTarget(Object emitter, String state, int bearish, int bullish)
            throws Exception {
        Method m = emitter.getClass().getDeclaredMethod("nextTarget", String.class, int.class, int.class);
        m.setAccessible(true);
        return (String) m.invoke(emitter, state, bearish, bullish);
    }

    /**
     * Helper: create a test StateCodeEmitter instance
     */
    private static Object createEmitter() throws Exception {
        // StateCodeEmitter constructor requires URI, which requires WebSocket connection
        // We'll use reflection to bypass that for testing purposes
        Constructor<?> ctor = StateCodeEmitter.class.getDeclaredConstructor(String.class);
        ctor.setAccessible(true);
        try {
            return ctor.newInstance("BTCUSDT");
        } catch (Exception e) {
            // If WebSocket fails, that's expected in unit tests
            // The computation methods should still be testable
            throw e;
        }
    }

    // --- computeNetDelta1m tests ---

    @Test
    void netDelta1m_empty_snapshot_returns_null() throws Exception {
        Object emitter = createEmitter();
        List<?> emptySnap = new ArrayList<>();
        long now = System.currentTimeMillis();

        Object result = computeNetDelta1m(emitter, emptySnap, now);

        assertNull(result, "Empty snapshot should return null");
    }

    @Test
    void netDelta1m_all_buys_returns_bullish() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Create 3 buy-side trades (buyerMaker=false means buy-side)
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, false));  // buy 10
        snap.add(createTick(baseTime - 20_000, 100.1, 5.0, false));   // buy 5
        snap.add(createTick(baseTime - 10_000, 100.2, 8.0, false));   // buy 8

        Object result = computeNetDelta1m(emitter, snap, baseTime);

        assertEquals(getDirBullish(), result, "All buys in 1m should return BULLISH");
    }

    @Test
    void netDelta1m_all_sells_returns_bearish() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Create 3 sell-side trades (buyerMaker=true means sell-side)
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, true));   // sell 10
        snap.add(createTick(baseTime - 20_000, 100.1, 5.0, true));    // sell 5
        snap.add(createTick(baseTime - 10_000, 100.2, 8.0, true));    // sell 8

        Object result = computeNetDelta1m(emitter, snap, baseTime);

        assertEquals(getDirBearish(), result, "All sells in 1m should return BEARISH");
    }

    @Test
    void netDelta1m_balanced_returns_neutral() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Create balanced trades (equal buy/sell volume)
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, false));  // buy 10
        snap.add(createTick(baseTime - 20_000, 100.1, 10.0, true));   // sell 10

        Object result = computeNetDelta1m(emitter, snap, baseTime);

        assertEquals(getDirNeutral(), result, "Balanced trades should return NEUTRAL");
    }

    @Test
    void netDelta1m_ignores_trades_older_than_1m() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Create a sell outside 1m window and a buy inside
        snap.add(createTick(baseTime - 90_000, 100.0, 100.0, true));   // sell 100 (outside window)
        snap.add(createTick(baseTime - 30_000, 100.0, 5.0, false));    // buy 5 (inside window)

        Object result = computeNetDelta1m(emitter, snap, baseTime);

        assertEquals(getDirBullish(), result, "Should only count trades within 1m window");
    }

    // --- computeLast3Delta tests ---

    @Test
    void last3Delta_empty_snapshot_returns_null() throws Exception {
        Object emitter = createEmitter();
        List<?> emptySnap = new ArrayList<>();
        long now = System.currentTimeMillis();

        Object result = computeLast3Delta(emitter, emptySnap, now);

        assertNull(result, "Empty snapshot should return null");
    }

    @Test
    void last3Delta_insufficient_buckets_returns_null() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Only add trades to one bucket (only within last minute)
        snap.add(createTick(baseTime - 10_000, 100.0, 10.0, false));

        Object result = computeLast3Delta(emitter, snap, baseTime);

        assertNull(result, "Missing any of 3 buckets should return null");
    }

    @Test
    void last3Delta_all_negative_returns_bearish() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // All three 1m buckets have net negative delta
        snap.add(createTick(baseTime - 150_000, 100.0, 20.0, true));   // b0: sell 20
        snap.add(createTick(baseTime - 90_000, 100.0, 15.0, true));    // b1: sell 15
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, true));    // b2: sell 10

        Object result = computeLast3Delta(emitter, snap, baseTime);

        assertEquals(getDirBearish(), result, "All negative buckets should return BEARISH");
    }

    @Test
    void last3Delta_all_positive_returns_bullish() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // All three 1m buckets have net positive delta
        snap.add(createTick(baseTime - 150_000, 100.0, 20.0, false));  // b0: buy 20
        snap.add(createTick(baseTime - 90_000, 100.0, 15.0, false));   // b1: buy 15
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, false));   // b2: buy 10

        Object result = computeLast3Delta(emitter, snap, baseTime);

        assertEquals(getDirBullish(), result, "All positive buckets should return BULLISH");
    }

    @Test
    void last3Delta_mixed_returns_neutral() throws Exception {
        Object emitter = createEmitter();
        List<Object> snap = new ArrayList<>();
        long baseTime = System.currentTimeMillis();

        // Mixed signs across buckets
        snap.add(createTick(baseTime - 150_000, 100.0, 20.0, true));   // b0: sell 20 (negative)
        snap.add(createTick(baseTime - 90_000, 100.0, 15.0, false));   // b1: buy 15 (positive)
        snap.add(createTick(baseTime - 30_000, 100.0, 10.0, true));    // b2: sell 10 (negative)

        Object result = computeLast3Delta(emitter, snap, baseTime);

        assertEquals(getDirNeutral(), result, "Mixed buckets should return NEUTRAL");
    }

    // --- nextTarget state transition tests ---

    @Test
    void nextTarget_A_with_2_bearish_1_bullish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "A", 2, 1);

        assertEquals("A>S", result, "From A with b>=2, bl<=1 should target A>S");
    }

    @Test
    void nextTarget_A_with_1_bearish_2_bullish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "A", 1, 2);

        assertEquals("A>L", result, "From A with bl>=2, b<=1 should target A>L");
    }

    @Test
    void nextTarget_A_with_balanced() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "A", 1, 1);

        assertNull(result, "From A with balanced signals should return null");
    }

    @Test
    void nextTarget_AS_to_S_requires_3_bearish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "A>S", 3, 0);

        assertEquals("S", result, "From A>S with b>=3 should transition to S");
    }

    @Test
    void nextTarget_AS_stays_pending_with_2_bearish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "A>S", 2, 0);

        assertNull(result, "From A>S with b<3 should return null (stay pending)");
    }

    @Test
    void nextTarget_S_to_SL_with_3_bullish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "S", 0, 3);

        assertEquals("S>L", result, "From S with bl>=3 should transition to S>L");
    }

    @Test
    void nextTarget_L_to_LS_with_3_bearish() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "L", 3, 0);

        assertEquals("L>S", result, "From L with b>=3 should transition to L>S");
    }

    @Test
    void nextTarget_invalid_state_returns_null() throws Exception {
        Object emitter = createEmitter();

        String result = nextTarget(emitter, "INVALID", 5, 5);

        assertNull(result, "Invalid state should return null");
    }
}
