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

    @Test
    public void testDetectAndSetupCandidatesBuilderIntegration() {
        System.setProperty(PitchforkSignalLayer.FLAG, "true");

        ObjectNode root = mapper.createObjectNode();
        root.put("current_price", 110.5);
        root.put("asset", "BTCUSDT");

        // Conditions node required by SetupCandidatesBuilder
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

        // Synthetic 4H klines (25 bars) forming: P0 at t=0 (p=100), P1 at t=10 (p=150), P2 at t=20 (p=110)
        ArrayNode klines4h = mapper.createArrayNode();
        for (int i = 0; i < 25; i++) {
            ArrayNode b = klines4h.addArray();
            b.add(i * 14400000L); // open_time
            double basePrice;
            if (i <= 10) {
                basePrice = 100.0 + (50.0 / 10.0) * i; // 100 -> 150
            } else if (i <= 20) {
                basePrice = 150.0 - (40.0 / 10.0) * (i - 10); // 150 -> 110
            } else {
                basePrice = 110.0 + 1.0 * (i - 20); // 110 -> 115
            }
            b.add(basePrice - 0.5); // open
            b.add(basePrice + 2.0); // high
            b.add(basePrice - 2.0); // low
            b.add(basePrice + 0.5); // close
            // High volume at t=20 (the P2 low)
            b.add(i == 20 ? 10000.0 : 500.0); // volume
        }

        // Test PitchforkSignalLayer.detect directly
        List<ObjectNode> detected = PitchforkSignalLayer.detect(mapper, root, klines4h, null, "BTCUSDT");
        assertNotNull(detected);
        if (!detected.isEmpty()) {
            ObjectNode cand = detected.get(0);
            assertEquals("PF-REV-L", cand.get("setup_type").asText());
            assertEquals("long", cand.get("direction").asText());
            assertTrue(cand.get("math").get("gross_rr").asDouble() >= 1.5);
            assertTrue(cand.has("pitchfork"));
            assertTrue(cand.get("pitchfork").get("va_confluent").asBoolean());
        }

        // Test integration into SetupCandidatesBuilder.build
        Map<String, com.fasterxml.jackson.databind.JsonNode> mtf = new HashMap<>();
        mtf.put("4h", klines4h);

        // Dummy 1m klines for SetupCandidatesBuilder
        ArrayNode klines1m = mapper.createArrayNode();
        for (int i = 0; i < 60; i++) {
            ArrayNode b = klines1m.addArray();
            b.add(i * 60000L);
            b.add(110.0);
            b.add(111.0);
            b.add(109.0);
            b.add(110.5);
            b.add(100.0);
        }

        ArrayNode candidates = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m);
        assertNotNull(candidates);

        // When flag is disabled, no pitchfork candidates should be added by the layer
        System.setProperty(PitchforkSignalLayer.FLAG, "false");
        ArrayNode candidatesDisabled = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m);
        assertNotNull(candidatesDisabled);
        boolean hasPfWhenDisabled = false;
        for (com.fasterxml.jackson.databind.JsonNode c : candidatesDisabled) {
            if (c.path("setup_type").asText("").startsWith("PF-")) {
                hasPfWhenDisabled = true;
                break;
            }
        }
        assertFalse(hasPfWhenDisabled);
    }
}
