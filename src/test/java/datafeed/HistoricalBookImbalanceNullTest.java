package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * B075 residual / B084: a historical (backtest) snapshot has no order book and no trade tape, so
 * order_book_depth.bid_ask_ratio and trade_flow.net_delta_1m are JSON null. The candidate proof block must carry
 * book_imbalance as JSON null, never 0.0 (live code reads 0.0 as "no depth data" but BT cannot tell it from a real reading).
 * Pattern: MarketDataSnapshot.java cond.putNull("book_imbalance"). Live path (numeric ratio) keeps its rounded number.
 */
public class HistoricalBookImbalanceNullTest {

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

    /** Same short-at-daily_vah scenario as SetupCandidatesBuilderHvnTargetTest, with the live-only fields set per mode. */
    private static ObjectNode root(boolean historical) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "TESTBT");
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
        daily.put("poc", 99.9);
        daily.put("vah", 100.0);
        daily.put("val", 90.0);
        daily.putArray("hvns").add(98.6);
        r.putObject("weekly_vp").putArray("hvns");
        ObjectNode m15 = r.putObject("structure").putObject("15m");
        m15.put("stale", false);
        m15.put("swing_high", 100.5);
        m15.put("swing_low", 99.0);
        ObjectNode cvd = r.putObject("cvd");
        cvd.put("slope", "flat");
        cvd.putObject("cvd_recent").put("slope_1h", "flat");
        ObjectNode tf = r.putObject("trade_flow");
        ObjectNode ob = r.putObject("order_book_depth");
        if (historical) {
            tf.putNull("net_delta_1m");
            ob.putNull("bid_ask_ratio");
        } else {
            tf.put("net_delta_1m", 0.0);
            ob.put("bid_ask_ratio", 1.07);
        }
        return r;
    }

    private static ArrayNode klines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 25; i++) {
            ArrayNode bar = k.addArray();
            bar.add(1_700_000_000_000L + i * 60_000L);
            bar.add(99.9).add(100.0).add(99.8).add(99.95).add(10.0);
            bar.add(0L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
        }
        return k;
    }

    private static JsonNode dailyVahProof(ObjectNode root) {
        ArrayNode out = SetupCandidatesBuilder.build(M, root, new HashMap<>(), klines());
        for (JsonNode c : out) if ("daily_vah".equals(c.get("zone").get("name").asText())) return c.get("proof");
        fail("no daily_vah candidate: " + out.size() + " candidates");
        return null;
    }

    @Test
    void historicalSnapshotYieldsNullBookImbalanceNotZero() {
        JsonNode proof = dailyVahProof(root(true));
        assertTrue(proof.has("book_imbalance"), "key must be present (explicit null), not omitted");
        assertTrue(proof.get("book_imbalance").isNull(), "historical book_imbalance must be JSON null, got " + proof.get("book_imbalance"));
    }

    @Test
    void liveSnapshotKeepsNumericBookImbalance() {
        JsonNode proof = dailyVahProof(root(false));
        assertEquals(1.07, proof.get("book_imbalance").asDouble(), 1e-9);
    }

    @Test
    void historicalSnapshotSourceEmitsNullRatio() throws Exception {
        String all = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get("src/main/java/datafeed/MarketDataSnapshot.java")), "UTF-8");
        String body = all.substring(all.indexOf("public ObjectNode fetchHistoricalSnapshot"), all.indexOf("private Map<String, JsonNode> fetchMultiTimeframeAsOf"));
        assertFalse(body.contains("ob.put(\"bid_ask_ratio\", 0.0)"));
        assertTrue(body.contains("ob.putNull(\"bid_ask_ratio\")"));
    }
}
