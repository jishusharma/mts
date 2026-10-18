package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Card tom-encode-spike-fade step 5 (spec section 15): with -Dmts.spikeFade unset the builder output is bit-identical
 * on a BTC and a GER40 fixture. The golden files were written by the pre-change builder (run with
 * -Dmts.writeGolden=true on the code before the fade type existed); this test only ever reads them.
 */
public class SpikeFadeFlagOffGoldenTest {
    private static final ObjectMapper M = new ObjectMapper();

    @BeforeEach
    void pin(@TempDir Path tmp) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
    }

    @AfterEach
    void unpin() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
    }

    static ObjectNode root(String asset) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", asset);
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
        daily.put("poc", 99.5);
        daily.put("vah", 100.0);
        daily.put("val", 90.0);
        daily.putArray("hvns");
        r.putObject("weekly_vp").putArray("hvns");
        ObjectNode m15 = r.putObject("structure").putObject("15m");
        m15.put("stale", false);
        m15.put("swing_high", 100.05);
        m15.put("swing_low", 99.0);
        ObjectNode cvd = r.putObject("cvd");
        cvd.put("slope", "flat");
        cvd.putObject("cvd_recent").put("slope_1h", "flat");
        r.putObject("trade_flow").put("net_delta_1m", 0.0);
        r.putObject("order_book_depth").put("bid_ask_ratio", 1.0);
        return r;
    }

    static ArrayNode klines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 25; i++) {
            ArrayNode bar = k.addArray();
            bar.add(1_700_000_000_000L + i * 60_000L).add(99.9).add(100.0).add(99.8).add(99.95).add(10.0)
               .add(0L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
        }
        return k;
    }

    private void check(String asset, String resource) throws Exception {
        String actual = M.writerWithDefaultPrettyPrinter()
                .writeValueAsString(SetupCandidatesBuilder.build(M, root(asset), new HashMap<>(), klines())).replace("\r\n", "\n");
        Path out = Path.of("src", "test", "resources", resource);
        if (Boolean.getBoolean("mts.writeGolden")) {
            Files.writeString(out, actual, StandardCharsets.UTF_8);
        }
        try (var in = getClass().getResourceAsStream("/" + resource)) {
            assertNotNull(in, "missing golden " + resource);
            String golden = new String(in.readAllBytes(), StandardCharsets.UTF_8).replace("\r\n", "\n");
            assertEquals(golden, actual, "flag off must leave the builder output bit-identical (" + asset + ")");
        }
        assertFalse(actual.contains("fade_short"));
    }

    @Test
    void btcFlagOffIdentical() throws Exception {
        System.clearProperty("mts.spikeFade");
        check("BTCUSDT", "spike_fade_flag_off_btc.json");
    }

    @Test
    void ger40FlagOffIdentical() throws Exception {
        System.clearProperty("mts.spikeFade");
        check("GER40", "spike_fade_flag_off_ger40.json");
    }
}
