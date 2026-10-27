package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class PitchforkSignalLayerTest {

    private final ObjectMapper mapper = new ObjectMapper();

    @AfterEach
    public void cleanup() {
        System.clearProperty(PitchforkSignalLayer.FLAG);
    }

    @Test
    public void testFlagDefaultOff() {
        System.clearProperty(PitchforkSignalLayer.FLAG);
        assertFalse(PitchforkSignalLayer.enabled());
    }

    @Test
    public void testFlagEnabled() {
        System.setProperty(PitchforkSignalLayer.FLAG, "true");
        assertTrue(PitchforkSignalLayer.enabled());
    }

    @Test
    public void testModifiedSchiffGeometry() {
        // P0=(0, 100), P1=(10, 150), P2=(20, 110)
        PitchforkSignalLayer.Pivot p0 = new PitchforkSignalLayer.Pivot(0, 100.0, false, 0L);
        PitchforkSignalLayer.Pivot p1 = new PitchforkSignalLayer.Pivot(10, 150.0, true, 10000L);
        PitchforkSignalLayer.Pivot p2 = new PitchforkSignalLayer.Pivot(20, 110.0, false, 20000L);

        PitchforkSignalLayer.PitchforkGeometry pf = new PitchforkSignalLayer.PitchforkGeometry(p0, p1, p2);

        // Effective P0 shifted 50% in price: (0, 125.0)
        assertEquals(0.0, pf.t0Eff, 1e-6);
        assertEquals(125.0, pf.p0Eff, 1e-6);

        // Midpoint of P1 and P2: tm = 15, pm = 130
        assertEquals(15.0, pf.tm, 1e-6);
        assertEquals(130.0, pf.pm, 1e-6);

        // Slope = (130 - 125) / (15 - 0) = 5.0 / 15.0 = 0.3333333333
        assertEquals(5.0 / 15.0, pf.slope, 1e-6);
        assertTrue(pf.isAscending);
        assertTrue(pf.p2IsLower);

        // ML at t=20: 125 + (5/15) * 20 = 125 + 6.666667 = 131.666667
        double ml20 = pf.getMl(20.0);
        assertEquals(125.0 + (5.0 / 15.0) * 20.0, ml20, 1e-6);

        // P2 price is 110, so LML at t=20 must equal 110.0
        assertEquals(110.0, pf.getLml(20.0), 1e-6);

        // Channel width > 0
        assertTrue(pf.channelWidth > 0.0);
    }

    @Test
    public void testVolumeProfileCalculation() {
        double[] lows = {100.0, 105.0, 109.5, 110.0, 110.5, 120.0, 130.0, 140.0};
        double[] highs = {102.0, 110.0, 112.0, 113.0, 112.5, 125.0, 135.0, 145.0};
        // Massive volume around 110 (support node)
        double[] volumes = {100.0, 200.0, 5000.0, 6000.0, 4500.0, 300.0, 200.0, 100.0};

        PitchforkSignalLayer.VolumeProfile vp = PitchforkSignalLayer.computeVolumeProfile(lows, highs, volumes, 1.0);
        assertNotNull(vp);

        // POC must be around 110.0 - 112.0
        assertTrue(vp.pocPrice >= 109.0 && vp.pocPrice <= 113.0);
        // Value area must contain 110.0
        assertTrue(110.0 >= vp.val && 110.0 <= vp.vah);
    }

    @Test
    public void testZigZagPivotDetection() {
        double[] highs = {100, 105, 110, 120, 115, 110, 105, 95, 90, 85, 95, 105, 115, 125, 120, 115};
        double[] lows =  { 98, 103, 108, 118, 113, 108, 103, 93, 88, 83, 93, 103, 113, 123, 118, 113};
        long[] timestamps = new long[highs.length];
        for (int i = 0; i < highs.length; i++) timestamps[i] = i * 14400000L;

        List<PitchforkSignalLayer.Pivot> pivots = PitchforkSignalLayer.findPivotsZigZag(highs, lows, timestamps, 2, 0.05);
        assertNotNull(pivots);
        assertTrue(pivots.size() >= 2);
    }

    // ---- independent expectations: FORMULAS 18.1 worked examples A/B/C (w = 1), computed by hand in the spec ----

    @Test
    public void testProfileWorkedA() {
        PitchforkSignalLayer.VolumeProfile vp = PitchforkSignalLayer.computeVolumeProfile(
                new double[]{0, 1, 1}, new double[]{2, 3, 2}, new double[]{6, 4, 10}, 1.0);
        assertEquals(1.5, vp.pocPrice, 1e-9);
        assertEquals(1.0, vp.val, 1e-9);
        assertEquals(2.0, vp.vah, 1e-9);
    }

    @Test
    public void testProfileWorkedB() {
        PitchforkSignalLayer.VolumeProfile vp = PitchforkSignalLayer.computeVolumeProfile(
                new double[]{0.5, 1.5, 2.5, 3.5, 4.5}, new double[]{0.5, 1.5, 2.5, 3.5, 4.5},
                new double[]{1, 2, 10, 4, 3}, 1.0);
        assertEquals(2.5, vp.pocPrice, 1e-9);
        assertEquals(2.0, vp.val, 1e-9);
        assertEquals(4.0, vp.vah, 1e-9);
    }

    @Test
    public void testProfileWorkedCTieGoesLower() {
        PitchforkSignalLayer.VolumeProfile vp = PitchforkSignalLayer.computeVolumeProfile(
                new double[]{0.5, 1.5, 2.5}, new double[]{0.5, 1.5, 2.5}, new double[]{3, 10, 3}, 1.0);
        assertEquals(1.5, vp.pocPrice, 1e-9);
        assertEquals(0.0, vp.val, 1e-9);
        assertEquals(2.0, vp.vah, 1e-9);
    }

    // ---- 4H fixture: P0 low (5, 98), P1 high (15, 152), P2 low (25, 108), 31 bars, hand-derived geometry:
    // p0Eff = 98 + 0.5*(152-98) = 125; tm = 20, pm = 130; slope = 5/15; ML(30) = 125 + 25/3 = 133.3333;
    // P1/P2 offsets = +/-23.6667; LML(30) = 109.6667; stop = LML*0.985 = 108.0217; RR = 23.6667/1.645 = 14.387.
    // Profile over bars 5..25 (w = 10, independent python transcription of 18.1): POC 115, VAL 100, VAH 120
    // -> P2 (108) inside the VA, not near the POC.

    private static double base(int i) {
        if (i <= 5) return 110 - 2 * i;
        if (i <= 15) return 100 + 5 * (i - 5);
        if (i <= 25) return 150 - 4 * (i - 15);
        return 110 + (i - 25);
    }

    private ArrayNode fixture4h() {
        ArrayNode k = mapper.createArrayNode();
        for (int i = 0; i < 31; i++) {
            ArrayNode b = k.addArray();
            double m = base(i);
            b.add(i * 14400000L);
            b.add(m);
            b.add(m + 2.0);
            b.add(m - 2.0);
            b.add(m);
            b.add(i == 25 ? 10000.0 : 100.0);
        }
        return k;
    }

    private ObjectNode rootNode(double price) {
        ObjectNode root = mapper.createObjectNode();
        root.put("current_price", price);
        root.put("asset", "BTCUSDT");
        return root;
    }

    @Test
    public void testDetectExactNumbers() {
        List<ObjectNode> d = PitchforkSignalLayer.detect(mapper, rootNode(2000.0), fixture4h(), null, "BTCUSDT");
        assertEquals(1, d.size());
        ObjectNode c = d.get(0);
        assertEquals("PF-REV-L", c.get("setup_type").asText());
        assertEquals("long", c.get("direction").asText());
        ObjectNode m = (ObjectNode) c.get("math");
        assertEquals(109.67, m.get("entry").asDouble(), 1e-9);
        assertEquals(108.02, m.get("stop").asDouble(), 1e-9);
        assertEquals(133.33, m.get("target").asDouble(), 1e-9);
        assertEquals(14.39, m.get("gross_rr").asDouble(), 0.011);
        assertEquals("ignore", m.get("tier").asText());
        ObjectNode pf = (ObjectNode) c.get("pitchfork");
        assertEquals(115.0, pf.get("vp_poc").asDouble(), 1e-9);
        assertEquals(100.0, pf.get("vp_val").asDouble(), 1e-9);
        assertEquals(120.0, pf.get("vp_vah").asDouble(), 1e-9);
        assertTrue(pf.get("va_confluent").asBoolean());
        assertFalse(pf.get("poc_confluent").asBoolean());
        assertEquals(2, c.get("proof").get("proof_count").asInt()); // VA + RR>=2
        assertEquals(85, c.get("score").get("raw").asInt());
    }

    @Test
    public void testFailClosedOnBadInput() {
        assertTrue(PitchforkSignalLayer.detect(mapper, null, fixture4h(), null, "BTCUSDT").isEmpty());
        assertTrue(PitchforkSignalLayer.detect(null, rootNode(2000.0), fixture4h(), null, "BTCUSDT").isEmpty());
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(Double.NaN), fixture4h(), null, "BTCUSDT").isEmpty());
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(-5), fixture4h(), null, "BTCUSDT").isEmpty());
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), null, null, "BTCUSDT").isEmpty());
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), mapper.createObjectNode(), null, "BTCUSDT").isEmpty());
        // price below the 10 USD bin grid's meaning (non-BTC scale): no signal
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(50.0), fixture4h(), null, "XRPUSDT").isEmpty());
    }

    @Test
    public void testFailClosedOnMalformedBars() {
        ArrayNode k = fixture4h();
        ((ArrayNode) k.get(7)).removeAll(); // short row: threw NPE into the builder before
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k, null, "BTCUSDT").isEmpty());

        ArrayNode k2 = fixture4h();
        ((ArrayNode) k2.get(10)).set(2, mapper.getNodeFactory().numberNode(Double.NaN));
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k2, null, "BTCUSDT").isEmpty());

        ArrayNode k3 = fixture4h();
        k3.set(12, mapper.getNodeFactory().textNode("junk"));
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k3, null, "BTCUSDT").isEmpty());

        ArrayNode k4 = fixture4h();
        ((ArrayNode) k4.get(9)).set(2, mapper.getNodeFactory().numberNode(50.0)); // high < low
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k4, null, "BTCUSDT").isEmpty());
    }

    // ---- wiring into SetupCandidatesBuilder ----

    private ObjectNode builderRoot() {
        ObjectNode root = rootNode(2000.0);
        ObjectNode cond = root.putObject("conditions");
        cond.put("vwap_slope", "flat");
        cond.put("cvd_slope", "flat");
        cond.put("price_vs_va", "in_va");
        cond.put("price_vs_poc", "below");
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = root.putObject("vwap");
        vwap.put("price", 100.0);
        vwap.put("slope", "flat");
        vwap.putObject("bands");
        root.putObject("daily_vp").putArray("hvns");
        ObjectNode weekly = root.putObject("weekly_vp");
        weekly.putArray("hvns");
        weekly.put("prior_week_poc", 100.0);
        root.putObject("prior_day");
        root.putObject("structure");
        return root;
    }

    private ArrayNode klines1m() {
        ArrayNode k = mapper.createArrayNode();
        for (int i = 0; i < 60; i++) {
            ArrayNode b = k.addArray();
            b.add(i * 60000L);
            b.add(110.0);
            b.add(111.0);
            b.add(109.0);
            b.add(110.5);
            b.add(100.0);
        }
        return k;
    }

    @Test
    public void testFlagOffIsByteIdenticalAndFlagOnOnlyAppends() throws Exception {
        Map<String, com.fasterxml.jackson.databind.JsonNode> mtf = new HashMap<>();
        mtf.put("4h", fixture4h());
        ObjectNode root = builderRoot();

        System.clearProperty(PitchforkSignalLayer.FLAG);
        String unset = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m()).toString();
        System.setProperty(PitchforkSignalLayer.FLAG, "false");
        String off = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m()).toString();
        assertEquals(unset, off);
        assertFalse(off.contains("PF-REV"));

        System.setProperty(PitchforkSignalLayer.FLAG, "true");
        ArrayNode on = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m());
        ArrayNode offArr = (ArrayNode) mapper.readTree(off);
        assertEquals(offArr.size() + 1, on.size());
        for (int i = 0; i < offArr.size(); i++) {
            assertEquals(offArr.get(i).toString(), on.get(i).toString());
        }
        ObjectNode last = (ObjectNode) on.get(on.size() - 1);
        assertEquals("PF-REV-L", last.get("setup_type").asText());
        assertEquals(on.size(), last.get("rank").asInt());
    }

    @Test
    public void testFlagOnWithoutFourHourSeriesAddsNothing() {
        ObjectNode root = builderRoot();
        System.setProperty(PitchforkSignalLayer.FLAG, "true");
        String on = SetupCandidatesBuilder.build(mapper, root, new HashMap<>(), klines1m()).toString();
        String onNull = SetupCandidatesBuilder.build(mapper, root, null, klines1m()).toString();
        System.clearProperty(PitchforkSignalLayer.FLAG);
        String off = SetupCandidatesBuilder.build(mapper, root, new HashMap<>(), klines1m()).toString();
        assertEquals(off, on);
        assertEquals(off, onNull);
    }

    @Test
    public void testShortSetupTargetBelowEntry() {
        ArrayNode k = mapper.createArrayNode();
        for (int i = 0; i < 31; i++) {
            ArrayNode b = k.addArray();
            double m = 6000.0 - 10.0 * base(i); // inverted, 10x amplitude (the stop is 1.5% of price): high, low, high pivots
            b.add(i * 14400000L);
            b.add(m);
            b.add(m + 20.0);
            b.add(m - 20.0);
            b.add(m);
            b.add(i == 25 ? 10000.0 : 100.0);
        }
        List<ObjectNode> d = PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k, null, "BTCUSDT");
        assertEquals(1, d.size());
        ObjectNode m = (ObjectNode) d.get(0).get("math");
        assertEquals("PF-REV-S", d.get(0).get("setup_type").asText());
        assertTrue(m.get("target").asDouble() < m.get("entry").asDouble());
        assertTrue(m.get("stop").asDouble() > m.get("entry").asDouble());
    }

    @Test
    public void testReviewFindings() {
        // out-of-order timestamps
        ArrayNode k = fixture4h();
        ((ArrayNode) k.get(8)).set(0, mapper.getNodeFactory().numberNode(1L));
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(2000.0), k, null, "BTCUSDT").isEmpty());

        // one absurd bar must not blow up the profile grid
        PitchforkSignalLayer.VolumeProfile vp = PitchforkSignalLayer.computeVolumeProfile(
                new double[]{1000.0}, new double[]{1e12}, new double[]{5.0}, 10.0);
        assertNull(vp);
        assertNull(PitchforkSignalLayer.computeVolumeProfile(
                new double[]{1, 2}, new double[]{2, 3}, new double[]{Double.MAX_VALUE, Double.MAX_VALUE}, 1.0));

        // 10x fixture: long entry ~1096.67, stop ~1080.2. Price through the stop = stale, no candidate.
        ArrayNode big = mapper.createArrayNode();
        for (int j = 0; j < 31; j++) {
            ArrayNode b = big.addArray();
            double m = base(j) * 10.0;
            b.add(j * 14400000L);
            b.add(m);
            b.add(m + 20.0);
            b.add(m - 20.0);
            b.add(m);
            b.add(j == 25 ? 10000.0 : 100.0);
        }
        assertEquals(1, PitchforkSignalLayer.detect(mapper, rootNode(1100.0), big, null, "BTCUSDT").size());
        assertTrue(PitchforkSignalLayer.detect(mapper, rootNode(1070.0), big, null, "BTCUSDT").isEmpty());
    }
}
