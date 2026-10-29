package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Critical test wave 1, item 3 (research/critical_test_wave1_2026-10-30/ITEM3_SPIKEFADE_CLASSIFYSTATE.md).
 * Hand numbers for classifyState, tier and score arithmetic in SetupCandidatesBuilder.
 *
 * classifyState rule table (code comment 2026-09-17, Rule 32): balance when vwap flat|sideways AND cvd flat AND in_va;
 * else cvd divergent -> trend_unhealthy; else outside the value area -> trend_healthy; else cvd aligned -> trend_healthy;
 * else balance.
 *
 * Scoring (DSA task 012 step 10, OURS, ranking only): raw = min(95, 50 + 7 * proof_count + confluence_bonus);
 * confidence B >= 70, C+ >= 55, C >= 40, else D. Confluence: another candidate zone within 0.3 % (inclusive) of this
 * zone's price gives +10. Scenario: short at daily_vah 100.0, price 99.95 (distance 0.05/99.95 = 0.050025 % <= 0.1 ->
 * trigger_ready, cap 0.4); second short zone prior_day_vah Z with swing_high 100.5 above both and target daily poc 99.5.
 * Z = 100.2: |100.0-100.2|/100.0 = 0.2 % <= 0.3 -> both get +10; distance of Z = 0.25/99.95 = 0.2501 % -> conditional.
 * Z = 100.3: 0.3 % <= 0.3 (inclusive) -> both +10. Z = 100.31: 0.31 % > 0.3 -> both 0.
 */
public class SetupCandidatesCriticalWave1Test {
    private static final ObjectMapper M = new ObjectMapper();

    @BeforeEach
    void pinFloor(@TempDir Path tmp) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
    }

    @AfterEach
    void unpinFloor() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
    }

    // ---------- classifyState ----------

    private static String state(String vwap, String cvd, String va) throws Exception {
        ObjectNode root = M.createObjectNode();
        ObjectNode c = root.putObject("conditions");
        c.put("vwap_slope", vwap);
        c.put("cvd_slope", cvd);
        c.put("price_vs_va", va);
        c.put("price_vs_poc", "above");
        Method m = SetupCandidatesBuilder.class.getDeclaredMethod("classifyState", ObjectNode.class);
        m.setAccessible(true);
        return (String) m.invoke(null, root);
    }

    @Test
    void classifyStateHandTable() throws Exception {
        assertEquals("balance", state("flat", "flat", "in_va"));
        assertEquals("balance", state("sideways", "flat", "in_va"));
        assertEquals("trend_healthy", state("flat", "flat", "above_vah"), "balance gate needs in_va");
        assertEquals("trend_healthy", state("rising", "flat", "below_val"));
        assertEquals("trend_unhealthy", state("rising", "divergent", "in_va"));
        assertEquals("trend_unhealthy", state("rising", "divergent", "above_vah"), "divergent wins over outside-VA");
        assertEquals("trend_healthy", state("flat", "aligned", "in_va"));
        assertEquals("balance", state("rising", "rising", "in_va"), "fall-through");
        assertEquals("balance", state("falling", "flat", "in_va"), "vwap not flat -> not the balance gate, fall-through");
    }

    /**
     * The snapshot producer (MarketDataSnapshot cvd/vwap builders) only ever emits rising | falling | flat for the
     * slopes, never "divergent" or "aligned". Over that real vocabulary the hand result is: in_va -> balance
     * (gate or fall-through), outside the value area -> trend_healthy; trend_unhealthy is unreachable.
     */
    @Test
    void classifyStateOverProductionVocabulary() throws Exception {
        String[] slopes = {"rising", "falling", "flat"};
        String[] vas = {"in_va", "above_vah", "below_val"};
        int healthy = 0, balance = 0;
        for (String v : slopes) for (String c : slopes) for (String va : vas) {
            String s = state(v, c, va);
            assertNotEquals("trend_unhealthy", s, v + "/" + c + "/" + va);
            assertEquals("in_va".equals(va) ? "balance" : "trend_healthy", s, v + "/" + c + "/" + va);
            if (s.equals("balance")) balance++; else healthy++;
        }
        assertEquals(9, balance);
        assertEquals(18, healthy);
    }

    // ---------- tier + score + confluence through build() ----------

    private static ObjectNode root(double priorDayVah) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "TESTCW1");
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
        r.putObject("prior_day").put("vah", priorDayVah);
        ObjectNode m15 = r.putObject("structure").putObject("15m");
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
            bar.add(1_700_000_000_000L + i * 60_000L).add(99.9).add(100.0).add(99.8).add(99.95).add(10.0)
               .add(0L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
        }
        return k;
    }

    private static JsonNode byZone(ArrayNode out, String name) {
        for (JsonNode c : out) if (name.equals(c.get("zone").get("name").asText())) return c;
        fail("no candidate for zone " + name + " in " + out);
        return null;
    }

    private static String band(int raw) {
        return raw >= 70 ? "B" : raw >= 55 ? "C+" : raw >= 40 ? "C" : "D";   // hand table, step 10
    }

    private static void assertScore(JsonNode cand, int expectedBonus) {
        JsonNode s = cand.get("score");
        int pc = s.get("proof_count").asInt();
        assertTrue(pc >= 0 && pc <= 5, "at most 5 counted signals today: " + pc);
        assertEquals(expectedBonus, s.get("confluence_bonus").asInt());
        int raw = Math.min(95, 50 + 7 * pc + expectedBonus);
        assertEquals(raw, s.get("raw").asInt());
        assertEquals(band(raw), s.get("confidence").asText());
    }

    @Test
    void confluentPairGetsBonusAndTiersAreHandComputed() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(100.2), new HashMap<>(), klines());
        assertEquals(2, out.size(), out.toString());
        JsonNode a = byZone(out, "daily_vah"), b = byZone(out, "prior_day_vah");
        assertScore(a, 10);
        assertScore(b, 10);
        assertEquals("trigger_ready", a.get("math").get("tier").asText());
        assertEquals("conditional", b.get("math").get("tier").asText());
        assertEquals(0.4, a.get("math").get("distance_cap").asDouble(), 0.0);
        assertEquals(0.05, a.get("math").get("distance_pct").asDouble(), 0.0);
        assertEquals(0.25, b.get("math").get("distance_pct").asDouble(), 0.0);
        assertEquals("ct_short", a.get("setup_type").asText());
        assertEquals(99.5, a.get("math").get("target").asDouble(), 0.0);
        assertEquals(100.5, a.get("math").get("stop").asDouble(), 0.0);
        // gross = 0.5 / 0.5 = 1.0; net = (0.5 - 0.1) / (0.5 + 0.1) = 0.6667 (cost 2*0.0005*100)
        assertEquals(1.0, a.get("math").get("gross_rr").asDouble(), 0.0);
        assertEquals(0.67, a.get("math").get("net_rr").asDouble(), 0.0);
    }

    @Test
    void confluenceBoundaryIsInclusiveAtPointThreePercent() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(100.3), new HashMap<>(), klines());
        assertEquals(2, out.size(), out.toString());
        assertScore(byZone(out, "daily_vah"), 10);
        assertScore(byZone(out, "prior_day_vah"), 10);
    }

    @Test
    void noConfluenceBeyondPointThreePercent() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root(100.31), new HashMap<>(), klines());
        assertEquals(2, out.size(), out.toString());
        assertScore(byZone(out, "daily_vah"), 0);
        assertScore(byZone(out, "prior_day_vah"), 0);
    }

    @Test
    void tierCutoffsAndNanSafeBands() {
        assertEquals("trigger_ready", SetupCandidatesBuilder.tierFor(0.1, 0.4));
        assertEquals("conditional", SetupCandidatesBuilder.tierFor(0.1000001, 0.4));
        assertEquals("conditional", SetupCandidatesBuilder.tierFor(0.4, 0.4));
        assertEquals("ignore", SetupCandidatesBuilder.tierFor(0.4000001, 0.4));
        assertEquals("ignore", SetupCandidatesBuilder.tierFor(0.2000001, 0.2));
        // price 100000, zone 99900 -> 100/100000*100 = 0.1 exactly by hand: trigger_ready
        assertEquals("trigger_ready", SetupCandidatesBuilder.tierFor(Math.abs(100000.0 - 99900.0) / 100000.0 * 100.0, 0.4));
    }
}
