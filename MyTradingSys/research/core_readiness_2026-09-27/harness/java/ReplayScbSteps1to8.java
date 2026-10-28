package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.File;
import java.util.*;

/**
 * L1 Tom-core replay, steps 1-8 of SetupCandidatesBuilder.build (state, directions,
 * zones, tier, setup type, stop, target, R:R, confluence) against archived snapshots.
 * Step 9 (proof detection) is NOT replayed: 1m klines are not stored in snapshots, so a
 * flat 30-bar dummy series is passed and proof/score/rank are ignored (task A4 adds it).
 * Needs a TEST BUILD of SetupCandidatesBuilder with MAX_CANDIDATES raised so that
 * ranking truncation (which depends on proof scores) hides nothing. Never edit src/.
 * Verified 2026-09-27 (JDK 21, Jackson 2.16.1): 49 snapshots, 118/118 candidates,
 * 1652/1652 field checks PASS; mutation friction 0.75->0.70 FAIL (136), cap 0.3->0.35 FAIL (13).
 * Working dir must contain runtime_data/naked_pocs/BTCUSDT_naked_pocs.json (repo root).
 */
public class ReplayScbSteps1to8 {
    static final String[] FIELDS = {"setup_type", "zone.price", "zone.type", "math.stop", "math.target",
            "math.gross_rr", "math.net_rr", "math.rr_sanity", "math.net_rr_sanity", "math.tier",
            "math.substate", "math.distance_cap", "math.distance_pct", "score.confluence_bonus"};

    static JsonNode at(JsonNode n, String dotted) {
        for (String k : dotted.split("\\.")) { if (n == null) return null; n = n.get(k); }
        return n;
    }

    public static void main(String[] args) throws Exception {
        ObjectMapper om = new ObjectMapper();
        int files = 0, archived = 0, found = 0, missing = 0, fieldOk = 0, fieldBad = 0;
        Map<String, Integer> badByField = new TreeMap<>();
        List<String> examples = new ArrayList<>();
        for (String f : args) {
            ObjectNode snap = (ObjectNode) om.readTree(new File(f));
            files++;
            JsonNode arch = snap.get("setup_candidates");
            ObjectNode root = snap.deepCopy();
            root.remove("setup_candidates");
            double px = root.get("current_price").asDouble();
            ArrayNode kl = om.createArrayNode();
            long t0 = 1_700_000_000_000L;
            for (int i = 0; i < 30; i++) {
                ArrayNode b = kl.addArray();
                b.add(t0 + i * 60000L); b.add(String.valueOf(px)); b.add(String.valueOf(px)); b.add(String.valueOf(px));
                b.add(String.valueOf(px)); b.add("1.0"); b.add(t0 + i * 60000L + 59999L); b.add("1.0"); b.add(1); b.add("0.5"); b.add("0.5"); b.add("0");
            }
            ArrayNode rep = SetupCandidatesBuilder.build(om, root, new HashMap<>(), kl);
            Map<String, JsonNode> byKey = new HashMap<>();
            for (JsonNode c : rep) byKey.put(c.get("zone").get("name").asText() + "|" + c.get("direction").asText(), c);
            if (arch == null) continue;
            for (JsonNode a : arch) {
                if (a.get("rank").asInt() > 3) continue; // ExtraSetupBuilder candidates (rank 11+) out of scope
                archived++;
                String key = a.get("zone").get("name").asText() + "|" + a.get("direction").asText();
                JsonNode r = byKey.get(key);
                if (r == null) { missing++; if (examples.size() < 8) examples.add("MISSING " + new File(f).getName() + " " + key); continue; }
                found++;
                for (String fld : FIELDS) {
                    JsonNode x = at(a, fld), y = at(r, fld);
                    boolean ok = (x == null && y == null) || (x != null && y != null &&
                            (x.isNumber() && y.isNumber() ? Math.abs(x.asDouble() - y.asDouble()) < 1e-6 : x.asText().equals(y.asText())));
                    if (ok) fieldOk++; else {
                        fieldBad++; badByField.merge(fld, 1, Integer::sum);
                        if (examples.size() < 8) examples.add("DIFF " + new File(f).getName() + " " + key + " " + fld + " archived=" + x + " replay=" + y);
                    }
                }
            }
        }
        System.out.println("snapshots=" + files + " archived_scb_candidates=" + archived + " found_in_replay=" + found + " missing=" + missing);
        System.out.println("field_checks ok=" + fieldOk + " bad=" + fieldBad + " bad_by_field=" + badByField);
        for (String e : examples) System.out.println("  " + e);
        System.out.println(missing == 0 && fieldBad == 0 ? "RESULT: PASS" : "RESULT: FAIL");
    }
}
