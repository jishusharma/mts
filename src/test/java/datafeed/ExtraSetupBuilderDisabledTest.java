package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * B142 / operator D15 (2026-10-10): momentum candidates are disabled until a sourced stop exists
 * (their stop was the previous 1m bar high/low, NO-SOURCE). Same fixture as ExtraSetupBuilderMomentumTest
 * (20 klines, last 3 range 10, speed_picking_up true, daily_vp val 80 vah 120), which emitted 1 candidate
 * at price 99 (short) and at price 101 (long) before the fix.
 */
public class ExtraSetupBuilderDisabledTest {

    private static final ObjectMapper M = new ObjectMapper();

    private static ArrayNode klines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 20; i++) {
            boolean large = i >= 17;
            ArrayNode c = k.addArray();
            c.add(i * 60_000L);
            c.add(100.0);
            c.add(large ? 105.0 : 100.5);
            c.add(large ? 95.0 : 99.5);
            c.add(100.0);
        }
        return k;
    }

    private static ObjectNode root(double price) {
        ObjectNode root = M.createObjectNode();
        root.put("current_price", price);
        ObjectNode cond = root.putObject("conditions");
        cond.put("speed_picking_up", true);
        cond.put("cvd_trade_flow_aligned", true);
        root.putObject("structure");
        ObjectNode vp = root.putObject("daily_vp");
        vp.put("val", 80.0);
        vp.put("vah", 120.0);
        return root;
    }

    @Test
    public void noMomentumCandidateBelowPreviousClose_B142() {
        assertEquals(0, ExtraSetupBuilder.build(M, root(99.0), new HashMap<String, JsonNode>(), klines()).size());
    }

    @Test
    public void noMomentumCandidateAbovePreviousClose_B142() {
        assertEquals(0, ExtraSetupBuilder.build(M, root(101.0), new HashMap<String, JsonNode>(), klines()).size());
    }
}
