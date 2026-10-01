package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * T1 (DSA_TASKS_2026-10-01): HVNs from weekly_vp / daily_vp / intraday_4h_vp are target candidates
 * [TOM-018] "it looks for the next high volume price and that is your target".
 *
 * Hand-computed scenario (short at daily_vah, state balance, so only ct_short at daily_vah survives):
 *   zone 100.0, swing_high (15m) 100.5 -> stop 100.5, risk 0.5
 *   target window [2.0R, 3.5R] below zone = [98.25, 99.0]
 *   every POC/VAL/VWAP/prior-day level is placed OUTSIDE that window, so without HVNs there is no target
 *   and the candidate is dropped; with an HVN at 98.6 the target is 98.6 (gross R:R 2.8).
 * Nearest-in-window rule: of two HVNs 98.6 and 98.3, the nearer to the zone (98.6) wins.
 * Direction filter: an HVN above the zone (101.5) is ignored for a short.
 */
public class SetupCandidatesBuilderHvnTargetTest {

    private static final ObjectMapper M = new ObjectMapper();

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

    @Test
    void noHvnMeansNoTargetAndNoCandidate() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{}, new double[]{}), new HashMap<>(), klines());
        assertEquals(0, out.size(), "all levels outside [2R,3.5R]: candidate must be dropped");
    }

    @Test
    void dailyHvnInWindowBecomesTarget() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{98.6}, new double[]{}), new HashMap<>(), klines());
        JsonNode math = only(out).get("math");
        assertEquals(98.6, math.get("target").asDouble(), 1e-9);
        assertEquals(100.5, math.get("stop").asDouble(), 1e-9);
        assertEquals(2.8, math.get("gross_rr").asDouble(), 1e-9); // 1.4 / 0.5
    }

    @Test
    void weeklyHvnInWindowBecomesTarget() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{}, new double[]{98.7}), new HashMap<>(), klines());
        assertEquals(98.7, only(out).get("math").get("target").asDouble(), 1e-9);
    }

    @Test
    void nearestInWindowHvnWins() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{98.3, 98.6}, new double[]{}), new HashMap<>(), klines());
        assertEquals(98.6, only(out).get("math").get("target").asDouble(), 1e-9);
    }

    @Test
    void hvnOnWrongSideOfShortIsIgnored() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(new double[]{101.5}, new double[]{}), new HashMap<>(), klines());
        assertEquals(0, out.size(), "HVN above the zone is not a short target");
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
