package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

/**
 * T037: SetupCandidatesBuilder decision rules (state classification, directional filter, distance caps, setup-type map,
 * target pick). Expected values are the rule table in the class comments (TOM-030/031/140/142/144/166) and hand maths:
 * netRR = (|target-entry| - 2*0.0005*entry) / (|entry-stop| + 2*0.0005*entry).
 */
public class SetupCandidatesBuilderRulesTest {

    private static final ObjectMapper M = new ObjectMapper();

    // ---------- reflection helpers (the rules are private static) ----------

    private static Object call(String name, Class<?>[] types, Object... args) throws Exception {
        Method m = SetupCandidatesBuilder.class.getDeclaredMethod(name, types);
        m.setAccessible(true);
        return m.invoke(null, args);
    }

    private static ObjectNode cond(String vwapSlope, String cvdSlope, String priceVsVa, String priceVsPoc) {
        ObjectNode root = M.createObjectNode();
        ObjectNode c = root.putObject("conditions");
        c.put("vwap_slope", vwapSlope);
        c.put("cvd_slope", cvdSlope);
        c.put("price_vs_va", priceVsVa);
        c.put("price_vs_poc", priceVsPoc);
        return root;
    }

    private static String state(ObjectNode root) throws Exception {
        return (String) call("classifyState", new Class<?>[]{ObjectNode.class}, root);
    }

    @SuppressWarnings("unchecked")
    private static List<String> directions(ObjectNode root) throws Exception {
        return (List<String>) call("determineDirections", new Class<?>[]{ObjectNode.class}, root);
    }

    private static double cap(String zoneType) throws Exception {
        return (double) call("getDistanceCap", new Class<?>[]{String.class}, zoneType);
    }

    private static String setupType(String zoneType, String direction, String state) throws Exception {
        Class<?> zc = Class.forName("datafeed.SetupCandidatesBuilder$Zone");
        Constructor<?> ctor = zc.getDeclaredConstructor();
        ctor.setAccessible(true);
        Object zone = ctor.newInstance();
        Field f = zc.getDeclaredField("type");
        f.setAccessible(true);
        f.set(zone, zoneType);
        return (String) call("determineSetupType", new Class<?>[]{zc, String.class, String.class}, zone, direction, state);
    }

    // ---------- build() guards ----------

    @Test
    public void buildReturnsEmptyForNullRootNullKlinesOrFewerThan20Klines() {
        assertEquals(0, SetupCandidatesBuilder.build(M, null, new HashMap<String, JsonNode>(), M.createArrayNode()).size());
        assertEquals(0, SetupCandidatesBuilder.build(M, M.createObjectNode(), new HashMap<String, JsonNode>(), null).size());
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 19; i++) k.addArray();
        assertEquals(0, SetupCandidatesBuilder.build(M, M.createObjectNode(), new HashMap<String, JsonNode>(), k).size());
    }

    // ---------- classifyState ----------

    @Test
    public void flatSlopesInsideValueAreaIsBalance() throws Exception {
        assertEquals("balance", state(cond("flat", "flat", "in_va", "above")));
        assertEquals("balance", state(cond("sideways", "flat", "in_va", "above")));
    }

    @Test
    public void divergentCvdIsTrendUnhealthy() throws Exception {
        assertEquals("trend_unhealthy", state(cond("rising", "divergent", "above_vah", "above")));
    }

    @Test
    public void outsideValueAreaOrAlignedCvdIsTrendHealthy() throws Exception {
        assertEquals("trend_healthy", state(cond("rising", "flat", "above_vah", "above")));
        assertEquals("trend_healthy", state(cond("rising", "flat", "below_val", "below")));
        assertEquals("trend_healthy", state(cond("rising", "aligned", "in_va", "above")));
    }

    @Test
    public void unmatchedConditionsFallBackToBalance() throws Exception {
        assertEquals("balance", state(cond("rising", "flat", "in_va", "above")));
    }

    // ---------- determineDirections (TOM-142) ----------

    @Test
    public void directionsFollowPriceVersusValueAreaAndPoc() throws Exception {
        assertEquals(Arrays.asList("short", "long"), directions(cond("flat", "flat", "above_vah", "above")));
        assertEquals(Arrays.asList("long", "short"), directions(cond("flat", "flat", "below_val", "below")));
        assertEquals(Arrays.asList("short"), directions(cond("flat", "flat", "in_va", "above")));
        assertEquals(Arrays.asList("long"), directions(cond("flat", "flat", "in_va", "below")));
        assertEquals(Arrays.asList("short", "long"), directions(cond("flat", "flat", "in_va", "at")));
    }

    // ---------- getDistanceCap ----------

    @Test
    public void distanceCapPerZoneFamily() throws Exception {
        assertEquals(0.5, cap("weekly_poc"), 0.0);
        assertEquals(0.4, cap("daily_vah"), 0.0);
        assertEquals(0.4, cap("pf_val"), 0.0);
        assertEquals(0.4, cap("4h_poc"), 0.0);
        assertEquals(0.4, cap("prior_day_vah"), 0.0);
        assertEquals(0.5, cap("1h_swing_high"), 0.0);
        assertEquals(0.3, cap("15m_swing_low"), 0.0);
        assertEquals(0.3, cap("5m_swing_high"), 0.0);
        assertEquals(0.2, cap("vwap_band_upper"), 0.0);
        assertEquals(0.2, cap("vwap"), 0.0);
        assertEquals(0.2, cap("fvg"), 0.0);
        assertEquals(0.4, cap("something_else"), 0.0);
    }

    // ---------- determineSetupType (TOM-030/140) ----------

    @Test
    public void vahAndSwingHighAreCounterTrendShortsInEveryState() throws Exception {
        assertEquals("ct_short", setupType("daily_vah", "short", "balance"));
        assertEquals("ct_short", setupType("1h_swing_high", "short", "trend_unhealthy"));
        assertEquals("ct_short", setupType("daily_vah", "short", "trend_healthy"));
        assertNull(setupType("daily_vah", "long", "trend_healthy"));
        assertNull(setupType("daily_vah", "long", "balance"));
    }

    @Test
    public void valAndSwingLowAreCounterTrendLongs() throws Exception {
        assertEquals("ct_long", setupType("daily_val", "long", "balance"));
        assertEquals("ct_long", setupType("15m_swing_low", "long", "trend_healthy"));
        assertNull(setupType("daily_val", "short", "balance"));
    }

    @Test
    public void pocIsCounterTrendOnlyInUnhealthyTrend() throws Exception {
        assertEquals("ct_short", setupType("weekly_poc", "short", "trend_unhealthy"));
        assertEquals("ct_long", setupType("weekly_poc", "long", "trend_unhealthy"));
        assertNull(setupType("weekly_poc", "short", "balance"));
        assertNull(setupType("weekly_poc", "long", "trend_healthy"));
    }

    @Test
    public void vwapIsScalpInBalanceAndPullbackLongInHealthyTrend() throws Exception {
        assertEquals("scalp_short", setupType("vwap", "short", "balance"));
        assertEquals("scalp_long", setupType("vwap_band_lower", "long", "balance"));
        assertEquals("tc_long", setupType("vwap", "long", "trend_healthy"));
        assertNull(setupType("vwap", "short", "trend_healthy"));
    }

    @Test
    public void fvgNeverASetupAndTransitionStateSuppressesEverything() throws Exception {
        assertNull(setupType("fvg", "short", "balance"));
        assertNull(setupType("fvg", "long", "trend_healthy"));
        assertNull(setupType("daily_vah", "short", "transition"));
        assertNull(setupType("vwap", "long", "transition"));
    }

    @Test
    public void priorDayCloseIsCounterTrendEitherWay() throws Exception {
        assertEquals("ct_short", setupType("prior_day_close", "short", "balance"));
        assertEquals("ct_long", setupType("prior_day_close", "long", "balance"));
    }

    // ---------- breakdown-continuation short below VAL, asserted on the CANDIDATE list (card java-below-val-short-no-setup-type-1109) ----------

    private static ObjectNode belowValRoot(String vwapSlope, String cvdSlope, String priceVsVa) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "TESTBV");
        r.put("current_price", 100.0);
        ObjectNode cond = r.putObject("conditions");
        cond.put("vwap_slope", vwapSlope);
        cond.put("cvd_slope", cvdSlope);
        cond.put("price_vs_va", priceVsVa);
        cond.put("price_vs_poc", "below");
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = r.putObject("vwap");
        vwap.put("price", 150.0);   // far away: no vwap zone inside its cap
        vwap.put("slope", vwapSlope);
        ObjectNode daily = r.putObject("daily_vp");
        daily.put("poc", 95.0);     // node below the VAL zone: short target
        daily.put("val", 100.1);    // zone 0.1% above price
        daily.putArray("hvns");
        ObjectNode weekly = r.putObject("weekly_vp");
        weekly.put("poc", 105.0);   // node above: long target
        weekly.putArray("hvns");
        ObjectNode m15 = r.putObject("structure").putObject("15m");
        m15.put("stale", false);
        m15.put("swing_high", 101.0);
        m15.put("swing_low", 99.0);
        ObjectNode cvd = r.putObject("cvd");
        cvd.put("slope", cvdSlope);
        cvd.putObject("cvd_recent").put("slope_1h", cvdSlope);
        r.putObject("trade_flow").put("net_delta_1m", 0.0);
        r.putObject("order_book_depth").put("bid_ask_ratio", 1.0);
        return r;
    }

    private static ArrayNode flatKlines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 25; i++) {
            ArrayNode bar = k.addArray();
            bar.add(1_700_000_000_000L + i * 60_000L).add(99.9).add(100.0).add(99.8).add(99.95).add(10.0)
               .add(0L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
        }
        return k;
    }

    private static List<String> candidateTypes(ObjectNode root) {
        ArrayNode out = SetupCandidatesBuilder.build(M, root, new HashMap<String, JsonNode>(), flatKlines());
        java.util.ArrayList<String> types = new java.util.ArrayList<>();
        for (JsonNode c : out) {
            if (c.has("zone") && "daily_val".equals(c.get("zone").path("name").asText())) {
                types.add(c.get("setup_type").asText() + ":" + c.get("direction").asText());
            }
        }
        return types;
    }

    @Test
    public void belowValTrendHealthyProducesTcShortCandidateAndKeepsCtLong() {
        // vwap falling + cvd falling (aligned, not opposed) below VAL = trend_healthy
        List<String> types = candidateTypes(belowValRoot("falling", "falling", "below_val"));
        org.junit.jupiter.api.Assertions.assertTrue(types.contains("tc_short:short"), "candidates: " + types);
        org.junit.jupiter.api.Assertions.assertTrue(types.contains("ct_long:long"), "ct_long at VAL unchanged: " + types);
    }

    @Test
    public void belowValTrendUnhealthyProducesNoShortCandidate() {
        // vwap rising + cvd falling = opposed outside VA = trend_unhealthy
        List<String> types = candidateTypes(belowValRoot("rising", "falling", "below_val"));
        org.junit.jupiter.api.Assertions.assertFalse(types.stream().anyMatch(t -> t.endsWith(":short")), "candidates: " + types);
        org.junit.jupiter.api.Assertions.assertTrue(types.contains("ct_long:long"), "candidates: " + types);
    }

    @Test
    public void shortAtValNeedsBelowValTrendHealthyAndValZone() throws Exception {
        Class<?> zc = Class.forName("datafeed.SetupCandidatesBuilder$Zone");
        Constructor<?> ctor = zc.getDeclaredConstructor();
        ctor.setAccessible(true);
        Class<?>[] sig = new Class<?>[]{zc, String.class, String.class, String.class};
        for (String zt : new String[]{"daily_val", "weekly_val", "4h_val", "prior_day_val"}) {
            Object zone = ctor.newInstance();
            Field f = zc.getDeclaredField("type");
            f.setAccessible(true);
            f.set(zone, zt);
            assertEquals("tc_short", call("determineSetupType", sig, zone, "short", "trend_healthy", "below_val"));
            assertNull(call("determineSetupType", sig, zone, "short", "trend_unhealthy", "below_val"));
            assertNull(call("determineSetupType", sig, zone, "short", "transition", "below_val"));
            assertNull(call("determineSetupType", sig, zone, "short", "balance", "below_val"));
            assertNull(call("determineSetupType", sig, zone, "short", "trend_healthy", "in_va"));
            assertNull(call("determineSetupType", sig, zone, "short", "trend_healthy", null));
            assertEquals("ct_long", call("determineSetupType", sig, zone, "long", "trend_healthy", "below_val"));
        }
        assertNull(setupType("daily_val", "short", "trend_healthy"));          // 3-arg form: no location, fail closed
        assertNull(setupType("15m_swing_low", "short", "trend_healthy"));
    }

    // ---------- pickTarget (floor 1.25, runner min distance 0 unless stated) ----------

    @Test
    public void pickTargetNearestNodeMeetingFloorWinsAndNextIsRunner() {
        // long, zone 100, stop 95: node 110 -> (10-0.1)/(5+0.1) = 1.94 >= 1.25 -> target 110, runner 120
        assertArrayEquals(new double[]{110.0, 120.0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(110.0, 120.0), 100.0, 95.0, false, 1.25), 1e-9);
    }

    @Test
    public void pickTargetSkipsNodesBelowFloor() {
        // node 100.5 -> (0.5-0.1)/5.1 = 0.08 < 1.25; node 120 -> 19.9/5.1 = 3.9 >= 1.25 -> target 120, no runner
        assertArrayEquals(new double[]{120.0, 0.0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(100.5, 120.0), 100.0, 95.0, false, 1.25), 1e-9);
    }

    @Test
    public void pickTargetShortUsesNodesBelowZone() {
        // short, zone 100, stop 105: node 90 -> 9.9/5.1 = 1.94 -> target 90, runner 80 (|80-90|/90 = 11.1% >= 0)
        assertArrayEquals(new double[]{90.0, 80.0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(90.0, 80.0, 110.0), 100.0, 105.0, true, 1.25), 1e-9);
    }

    @Test
    public void pickTargetRunnerNeedsMinimumDistanceFromTarget() {
        // runner 80 is 11.1% beyond target 90: required 20% -> no runner
        assertArrayEquals(new double[]{90.0, 0.0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(90.0, 80.0), 100.0, 105.0, true, 1.25, 20.0), 1e-9);
    }

    @Test
    public void pickTargetNaNFloorFailsClosedToFarthestNode() {
        assertArrayEquals(new double[]{120.0, 0.0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(110.0, 120.0), 100.0, 95.0, false, Double.NaN), 1e-9);
    }

    @Test
    public void pickTargetNoNodeInTradeDirectionReturnsZeros() {
        assertArrayEquals(new double[]{0, 0},
                SetupCandidatesBuilder.pickTarget(Arrays.asList(90.0), 100.0, 95.0, false, 1.25), 0.0);
    }

    // ---------- B131: proof_count independent of book_imbalance ----------

    private static int proofCount(int nonBookSignals, Double bookImbalance, String direction) throws Exception {
        Class<?> pc = Class.forName("datafeed.SetupCandidatesBuilder$ProofResult");
        Constructor<?> ctor = pc.getDeclaredConstructor();
        ctor.setAccessible(true);
        Object p = ctor.newInstance();
        // five counted slots: wick, absorption, finished_auction, delta_flip, cvd (B144: volume spike not counted); fire the first n
        boolean[] on = new boolean[5];
        for (int i = 0; i < nonBookSignals; i++) on[i] = true;
        set(pc, p, "rejectionWick", on[0] ? "BULLISH" : "NONE");
        set(pc, p, "absorptionDetected", on[1]);
        set(pc, p, "finishedAuctionDetected", on[2]);
        set(pc, p, "finishedAuctionDirection", "long".equals(direction) ? "sell" : "buy");
        set(pc, p, "deltaFlipDetected", on[3]);
        set(pc, p, "deltaFlipAtZone", on[3]);
        set(pc, p, "cvdAligned", on[4]);
        set(pc, p, "bookImbalance", bookImbalance);
        Method m = pc.getDeclaredMethod("countSignals", String.class);
        m.setAccessible(true);
        return (Integer) m.invoke(p, direction);
    }

    private static void set(Class<?> c, Object o, String name, Object v) throws Exception {
        Field f = c.getDeclaredField(name);
        f.setAccessible(true);
        f.set(o, v);
    }

    @Test
    public void proofCountFourOfFiveIgnoresBookImbalance() throws Exception {
        for (String dir : new String[]{"long", "short"}) {
            assertEquals(4, proofCount(4, 0.34, dir));
            assertEquals(4, proofCount(4, 2.0, dir));
            assertEquals(4, proofCount(4, null, dir));
        }
    }

    @Test
    public void proofCountFiveOfFiveIgnoresBookImbalance() throws Exception {
        for (String dir : new String[]{"long", "short"}) {
            assertEquals(5, proofCount(5, 0.34, dir));
            assertEquals(5, proofCount(5, 2.0, dir));
        }
    }
}
