package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * FVG is an EXIT/target area, never an entry (compiled_engine.md section 2 zone map "target areas, not entry";
 * SetupCandidatesBuilder.setupTypeFor returns null for zone type fvg). ExtraSetupBuilder used to emit
 * fvg_short / fvg_long entries; this pins that it no longer does, for both FVG directions, with a
 * price inside 0.15% of the gap edge and a support/resistance level that satisfied the old R:R sanity.
 */
public class ExtraSetupBuilderFvgTest {

    private static ArrayNode build(String fvgType, double price, double top, double bottom) {
        ObjectMapper m = new ObjectMapper();
        ObjectNode root = m.createObjectNode();
        root.put("current_price", price);
        ObjectNode cond = root.putObject("conditions");
        cond.put("speed_picking_up", false);
        cond.put("cvd_trade_flow_aligned", false);
        ObjectNode fvg = cond.putObject("fvg_nearest_unfilled");
        fvg.put("type", fvgType);
        fvg.put("top", top);
        fvg.put("bottom", bottom);
        root.putObject("structure");
        // levels on both sides so the old builder's target/R:R sanity would pass
        ObjectNode vp = root.putObject("daily_vp");
        vp.put("val", bottom - 500.0);
        vp.put("vah", top + 500.0);
        return ExtraSetupBuilder.build(m, root, new HashMap<String, JsonNode>(), m.createArrayNode());
    }

    @Test
    public void bearishFvgNearPriceEmitsNoEntry() {
        // price just below the gap top (within 0.15%) -> old code emitted fvg_short
        assertEquals(0, build("bearish", 99_950.0, 100_000.0, 99_800.0).size());
    }

    @Test
    public void bullishFvgNearPriceEmitsNoEntry() {
        // price just above the gap bottom (within 0.15%) -> old code emitted fvg_long
        assertEquals(0, build("bullish", 100_050.0, 100_300.0, 100_000.0).size());
    }
}
