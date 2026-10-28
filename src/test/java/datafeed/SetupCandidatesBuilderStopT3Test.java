package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * T3 ruling (MyTradingSys/research/_archive/loose_2026-10/T3_STOP_RULING_2026-10-01.md), provenance rows A03/A04: no 0.2% fallback stop
 * and no 0.1% minimum stop floor; matches the Python path (no swing-based stop -> candidate rejected).
 * Scenario: short at daily_vah 100.0 (price_vs_poc above -> short only), floor pinned to 1.25.
 * Fee model (B070): cost = 2*0.0005*100 = 0.1; net = (reward - 0.1) / (risk + 0.1).
 */
public class SetupCandidatesBuilderStopT3Test {
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

    private static ObjectNode root(boolean swingStale, double swingHigh) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "TESTT3");
        r.put("current_price", 99.95);
        ObjectNode cond = r.putObject("conditions");
        cond.put("vwap_slope", "flat");
        cond.put("cvd_slope", "flat");
        cond.put("price_vs_va", "in_va");
        cond.put("price_vs_poc", "above");
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = r.putObject("vwap");
        vwap.put("price", 101.0);
        vwap.put("slope", "flat");
        ObjectNode daily = r.putObject("daily_vp");
        daily.put("poc", 99.5);   // the only node below the zone: reward 0.5
        daily.put("vah", 100.0);
        daily.put("val", 90.0);
        daily.putArray("hvns");
        r.putObject("weekly_vp").putArray("hvns");
        ObjectNode m15 = r.putObject("structure").putObject("15m");
        m15.put("stale", swingStale);
        m15.put("swing_high", swingHigh);
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
            bar.add(1_700_000_000_000L + i * 60_000L).add(99.9).add(100.0).add(99.8).add(99.95).add(10.0)
               .add(0L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
        }
        return k;
    }

    @Test
    void noSwingMeansNoFallbackStopAndCandidateDropped() {
        // Old code: stale swing -> stop = 100*1.002 = 100.2 and the candidate was kept (target 99.5).
        ArrayNode out = SetupCandidatesBuilder.build(M, root(true, 100.5), new HashMap<>(), klines());
        assertEquals(0, out.size(), "no swing stop => no candidate (A03 fallback removed per T3): " + out);
    }

    @Test
    void swingNotBeyondZoneMeansNoStopAndCandidateDropped() {
        // swing_high 99.9 is not above the short zone 100.0: no valid swing stop. Old code used 100.2.
        ArrayNode out = SetupCandidatesBuilder.build(M, root(false, 99.9), new HashMap<>(), klines());
        assertEquals(0, out.size(), "swing not beyond zone => dropped (A03 removed per T3): " + out);
    }

    @Test
    void tightSwingStopIsNotWidened() {
        // swing_high 100.05 is 0.05% above the zone (< old 0.1% floor). Old code widened the stop to 100.2.
        ArrayNode out = SetupCandidatesBuilder.build(M, root(false, 100.05), new HashMap<>(), klines());
        assertEquals(1, out.size(), "tight swing stop must be kept (A04 floor removed per T3): " + out);
        JsonNode math = out.get(0).get("math");
        assertEquals(100.05, math.get("stop").asDouble(), 1e-9);
        assertEquals(99.5, math.get("target").asDouble(), 1e-9);
        assertEquals(10.0, math.get("gross_rr").asDouble(), 1e-6);   // 0.5 / 0.05
    }
}
