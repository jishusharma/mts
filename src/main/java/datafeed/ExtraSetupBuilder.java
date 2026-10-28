package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.*;

public class ExtraSetupBuilder {
    public static ArrayNode build(ObjectMapper mapper, ObjectNode root, Map<String, JsonNode> mtf, JsonNode klines1m) {
        // FVG: EXIT/target area only, never an entry (compiled_engine.md section 2 zone map:
        // "target areas, not entry"; SetupCandidatesBuilder.setupTypeFor returns null for fvg).
        // fvg_short/fvg_long entries removed 2026-10-01 (consolidation TOM trace).

        // Momentum candidates disabled 2026-10-10 (B142, operator D15 "Disable until a sourced stop exists"):
        // their stop was the previous 1m bar high/low with no trader source (no_source_sweep_2026-10-09 RESULT.md).
        // The module_candidates key stays in the snapshot as an empty array.
        return mapper.createArrayNode();
    }
}
