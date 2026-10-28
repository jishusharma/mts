package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * HVNs from weekly_vp / daily_vp / intraday_4h_vp are target candidates [TOM-018] "it looks for the next high volume
 * price and that is your target". Operator ruling 2026-10-03: the 2.0R-3.5R window is gone; the target is the NEAREST
 * node in trade direction whose netRR >= floor, else the farthest node.
 *
 * Hand-computed scenario (floor pinned to 1.25; B070 fee model net = (reward - 2*0.0005*entry) / (risk + 2*0.0005*entry); short at daily_vah, state balance):
 *   zone 100.0, swing_high (15m) 100.5 -> stop 100.5, risk 0.5; daily POC 99.9 = 0.1 below zone = 0.2R gross, net 0.0
 *   -> fails the floor. HVN 98.6 = 1.4 below = 2.8R gross, net 2.1 -> qualifies.
 */
public class SetupCandidatesBuilderHvnTargetTest {

    private static final ObjectMapper M = new ObjectMapper();

    @org.junit.jupiter.api.BeforeEach
    void pinFloor(@org.junit.jupiter.api.io.TempDir java.nio.file.Path tmp) throws Exception {
        java.nio.file.Path f = tmp.resolve("net_rr_floor.json");
        java.nio.file.Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
    }

    @org.junit.jupiter.api.AfterEach
    void unpinFloor() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
    }

    private static ObjectNode root(double[] dailyHvns, double[] weeklyHvns) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "TESTHVN");
        r.put("current_price", 99.95);
        ObjectNode cond = r.putObject("conditions");
        cond.put("vwap_slope", "flat");
        cond.put("cvd_slope", "flat");
        cond.put("price_vs_va", "in_va");
        cond.put("price_vs_poc", "above");   // -> short only
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = r.putObject("vwap");
        vwap.put("price", 101.0);            // above zone: not a short target
        vwap.put("slope", "flat");
        ObjectNode daily = r.putObject("daily_vp");
        daily.put("poc", 99.9);              // 0.1 below zone = 0.2R, outside window
        daily.put("vah", 100.0);
        daily.put("val", 90.0);
        ArrayNode dh = daily.putArray("hvns");
        for (double v : dailyHvns) dh.add(v);
        ObjectNode weekly = r.putObject("weekly_vp");
        ArrayNode wh = weekly.putArray("hvns");
        for (double v : weeklyHvns) wh.add(v);
        ObjectNode structure = r.putObject("structure");
        ObjectNode m15 = structure.putObject("15m");
        m15.put("stale", false);
        m15.put("swing_high", 100.5);
        m15.put("swing_low", 99.0);
        ObjectNode cvd = r.putObject("cvd");
        cvd.put("slope", "flat");
        cvd.putObject("cvd_recent").put("slope_1h", "flat");
        r.putObject("trade_flow").put("net_delta_1m", 0.0);
        r.putObject("order_book_depth").put("bid_ask_ratio", 1.0);
        return r;
    }

    private static ArrayNode klines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 25; i++) {
            ArrayNode bar = k.addArray();
            bar.add(1_700_000_000_000L + i * 60_000L); // 0 open time
            bar.add(99.9);   // 1 open
            bar.add(100.0);  // 2 high
            bar.add(99.8);   // 3 low
            bar.add(99.95);  // 4 close
            bar.add(10.0);   // 5 volume
            bar.add(0L);     // 6 close time
            bar.add(1000.0); // 7 quote vol
            bar.add(10);     // 8 trades
            bar.add(5.0);    // 9 taker buy base
            bar.add(500.0);  // 10 taker buy quote
            bar.add(0);      // 11 ignore
        }
        return k;
    }

    private static JsonNode only(ArrayNode out) {
        assertEquals(1, out.size(), "expected exactly the daily_vah ct_short candidate: " + out);
        return out.get(0);
    }

    /** The daily_vah candidate (the 15m swing-high is itself a zone at the real-shape prices, so more than one survives). */
    private static JsonNode daily(ArrayNode out) {
        for (JsonNode c : out) if ("daily_vah".equals(c.get("zone").get("name").asText())) return c;
        fail("no daily_vah candidate: " + out.size() + " candidates");
        return null;
    }

    @Test
    void onlyPocBelowFloorIsStillReportedAsFarthestNode() {
        // old code: POC 99.9 outside [98.25, 99.0] -> candidate dropped. new: only node, fails floor, kept as farthest.
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{}, new double[]{}), new HashMap<>(), klines());
        JsonNode math = only(out).get("math");
        assertEquals(99.9, math.get("target").asDouble(), 1e-9);
        assertEquals(0.2, math.get("gross_rr").asDouble(), 1e-9);   // 0.1 / 0.5
        assertEquals(0.0, math.get("net_rr").asDouble(), 1e-9);     // B070 fee model: (0.1 - 2*0.0005*100) / (0.5 + 0.1) = 0
        assertEquals(0.0, math.get("runner_target").asDouble(), 1e-9);
    }

    @Test
    void dailyHvnQualifyingBecomesTargetAndPocIsSkipped() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{98.6}, new double[]{}), new HashMap<>(), klines());
        JsonNode math = only(out).get("math");
        assertEquals(98.6, math.get("target").asDouble(), 1e-9);
        assertEquals(100.5, math.get("stop").asDouble(), 1e-9);
        assertEquals(2.8, math.get("gross_rr").asDouble(), 1e-9); // 1.4 / 0.5
        assertEquals(0.0, math.get("runner_target").asDouble(), 1e-9); // no node beyond 98.6
    }

    @Test
    void weeklyHvnQualifyingBecomesTarget() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{}, new double[]{98.7}), new HashMap<>(), klines());
        assertEquals(98.7, only(out).get("math").get("target").asDouble(), 1e-9);
    }

    @Test
    void nearestQualifyingHvnWinsAndNextNodeIsRunner() {
        // distances from 100: POC 0.1, HVN 1.4 (98.6), HVN 1.7 (98.3). 98.6 is the nearest that qualifies; runner 98.3.
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{98.3, 98.6}, new double[]{}), new HashMap<>(), klines());
        JsonNode math = only(out).get("math");
        assertEquals(98.6, math.get("target").asDouble(), 1e-9);
        assertEquals(98.3, math.get("runner_target").asDouble(), 1e-9);
    }

    @Test
    void hvnOnWrongSideOfShortIsIgnored() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{101.5}, new double[]{}), new HashMap<>(), klines());
        assertEquals(99.9, only(out).get("math").get("target").asDouble(), 1e-9); // 101.5 above zone is not a short target
    }

    @Test
    void noNodeInDirectionDropsTheCandidate() {
        ObjectNode r = root(new double[]{}, new double[]{});
        ((ObjectNode) r.get("daily_vp")).put("poc", 100.6);   // above the short zone: no node below
        assertEquals(0, SetupCandidatesBuilder.build(M, r, new HashMap<>(), klines()).size());
    }

    @Test
    void closeNodesFailingFloorAreSkippedForFarOne() {
        // real-shape case: short at 87064, stop 87238 (risk 174). Nodes 86900 (164 = 0.943R gross, fee-model net < 0: skip),
        // 83851 (3213 / 174 = 18.466R gross, fee-model net 11.97: qualifies). Old window [348, 609] holds neither -> dropped.
        ObjectNode r = root(new double[]{86900, 83851}, new double[]{});
        ((ObjectNode) r.get("daily_vp")).put("poc", 0.0).put("vah", 87064.0).put("val", 80000.0);
        r.put("current_price", 87063.0);
        ((ObjectNode) r.get("vwap")).put("price", 88000.0);
        ObjectNode s = (ObjectNode) r.get("structure").get("15m");
        s.put("swing_high", 87238.0).put("swing_low", 86000.0);
        JsonNode math = daily(SetupCandidatesBuilder.build(M, r, new HashMap<>(), klines())).get("math");
        assertEquals(83851.0, math.get("target").asDouble(), 1e-9);
        assertEquals(87238.0, math.get("stop").asDouble(), 1e-9);
        assertEquals(18.47, math.get("gross_rr").asDouble(), 1e-9);   // 3213/174 = 18.4655 rounded to 2dp
    }

    @Test
    void realShapeNearestQualifyingWithRunner() {
        // short at 87064, stop 87238 (risk 174): 86600 = 464 = 2.667R gross, fee-model net (464 - 87.064) / 261.064 = 1.444 >= 1.25 -> target; runner 83851.
        ObjectNode r = root(new double[]{86600, 83851}, new double[]{});
        ((ObjectNode) r.get("daily_vp")).put("poc", 0.0).put("vah", 87064.0).put("val", 80000.0);
        r.put("current_price", 87063.0);
        ((ObjectNode) r.get("vwap")).put("price", 88000.0);
        ObjectNode s = (ObjectNode) r.get("structure").get("15m");
        s.put("swing_high", 87238.0).put("swing_low", 86000.0);
        JsonNode math = daily(SetupCandidatesBuilder.build(M, r, new HashMap<>(), klines())).get("math");
        assertEquals(86600.0, math.get("target").asDouble(), 1e-9);
        assertEquals(83851.0, math.get("runner_target").asDouble(), 1e-9);
    }

    @Test
    void singleNodeAtFiveRKeptWhereOldWindowDroppedIt() {
        // short at 87064, risk 174: only node 86194 = 870 below = 5.0R gross (> 3.5R old cap), fee-model net (870 - 87.064) / 261.064 = 2.999 -> 3.0 at 2dp. Old: dropped.
        ObjectNode r = root(new double[]{86194}, new double[]{});
        ((ObjectNode) r.get("daily_vp")).put("poc", 0.0).put("vah", 87064.0).put("val", 80000.0);
        r.put("current_price", 87063.0);
        ((ObjectNode) r.get("vwap")).put("price", 88000.0);
        ObjectNode s = (ObjectNode) r.get("structure").get("15m");
        s.put("swing_high", 87238.0).put("swing_low", 86000.0);
        JsonNode math = daily(SetupCandidatesBuilder.build(M, r, new HashMap<>(), klines())).get("math");
        assertEquals(86194.0, math.get("target").asDouble(), 1e-9);
        assertEquals(5.0, math.get("gross_rr").asDouble(), 1e-9);
        assertEquals(3.0, math.get("net_rr").asDouble(), 1e-9);
    }

    @Test
    void addHvnsIgnoresNonNumericAndNonPositive() {
        ObjectNode r = M.createObjectNode();
        ArrayNode h = r.putObject("daily_vp").putArray("hvns");
        h.add(98.6).add("x").add(-1.0).add(0.0).addNull();
        java.util.List<Double> pool = new java.util.ArrayList<>();
        SetupCandidatesBuilder.addHvns(r, "daily_vp", pool);
        SetupCandidatesBuilder.addHvns(r, "weekly_vp", pool); // missing profile
        assertEquals(java.util.List.of(98.6), pool);
    }
}
