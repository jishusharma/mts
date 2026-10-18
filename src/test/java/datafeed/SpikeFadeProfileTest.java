package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Card tom-encode-fade-profile-proofs (TOM_LAYER_V2_SPEC sections 2.1 A-C3, 2.2 A-P3 / A-P8, 12, 13), PROFILE arm.
 *
 * <p>Thirds hand numbers (spec 13): leg 24010-24110, 30 rows of 3.3333 points, thirds = rows 0-9 / 10-19 / 20-29
 * (24010-24043.33 / -24076.67 / -24110). Volume by third bottom/mid/top 500 / 300 / 100 with the POC row in the bottom
 * third -> thin = true. Top third 400 (not below the mid 300) -> false. Top 120 on a single price (row max) with the
 * lower thirds in rows of 100 -> POC in the top third -> false.
 *
 * <p>Integration: the 50-bar ramp of SpikeFadePathsTest (close 24010 + 2 (m+1), extreme bar 49 high 24110) with volume per
 * bar set here: bars 0-32 carry 10, bars 33-49 carry 2, one heavy bar carries 100. Thirds with the heavy bar 2:
 * bottom (bars 0-15) 160 + 90 = 250, mid (16-32) 170, top (33-49) 34 -> thin, POC third 0.
 */
public class SpikeFadeProfileTest {
    private static final ObjectMapper M = new ObjectMapper();
    private static final ZoneId BERLIN = ZoneId.of("Europe/Berlin");
    private static final LocalDate TODAY = LocalDate.of(2026, 10, 14);
    private static final double P = 23900.0;

    @BeforeEach
    void setUp(@TempDir Path tmp) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
        System.setProperty("mts.spikeFade", "true");
        System.setProperty(SpikeFadeSessionState.FILE_PROPERTY, tmp.resolve("fade_state.json").toString());
        SpikeFadeSessionState.resetShared();
    }

    @AfterEach
    void tearDown() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
        System.clearProperty("mts.spikeFade");
        System.clearProperty(SpikeFadeProfile.DAX_PROPERTY);
        System.clearProperty(SpikeFadeSessionState.FILE_PROPERTY);
        SpikeFadeSessionState.resetShared();
    }

    // ---- thirds (pure function) ----

    @Test
    void thinTopWhenTopThirdIsSmallestAndPocBelow() {
        SpikeFadeProfile.Thin t = SpikeFadeProfile.thin(24010, 24110, new double[]{24020, 24060, 24100}, new double[]{500, 300, 100});
        assertEquals(500.0, t.bottom, 1e-9);
        assertEquals(300.0, t.mid, 1e-9);
        assertEquals(100.0, t.top, 1e-9);
        assertEquals(0, t.pocThird);
        assertTrue(t.thin);
    }

    @Test
    void notThinWhenTopThirdNotBelowMid() {
        SpikeFadeProfile.Thin t = SpikeFadeProfile.thin(24010, 24110, new double[]{24020, 24060, 24100}, new double[]{500, 300, 400});
        assertEquals(400.0, t.top, 1e-9);
        assertFalse(t.thin);
    }

    @Test
    void notThinWhenPocInTopThird() {
        double[] px = {24012, 24018, 24022, 24028, 24034, 24055, 24060, 24065, 24100};
        double[] v = {100, 100, 100, 100, 100, 100, 100, 100, 120};   // bottom 500 in 5 rows, mid 300 in 3, top 120 in 1
        SpikeFadeProfile.Thin t = SpikeFadeProfile.thin(24010, 24110, px, v);
        assertEquals(120.0, t.top, 1e-9);
        assertEquals(2, t.pocThird);
        assertFalse(t.thin);
    }

    // ---- integration through the builder ----

    private static ObjectNode root(double price) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "BTCUSDT");
        r.put("current_price", price);
        ObjectNode cond = r.putObject("conditions");
        cond.put("vwap_slope", "flat");
        cond.put("cvd_slope", "flat");
        cond.put("price_vs_va", "in_va");
        cond.put("price_vs_poc", "above");
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = r.putObject("vwap");
        vwap.put("price", 100.0);
        vwap.put("slope", "flat");
        r.putObject("daily_vp").putArray("hvns");
        ObjectNode weekly = r.putObject("weekly_vp");
        weekly.putArray("hvns");
        weekly.put("prior_week_poc", 23950.0);
        r.putObject("structure");
        ObjectNode cvd = r.putObject("cvd");
        cvd.put("slope", "flat");
        cvd.putObject("cvd_recent").put("slope_1h", "flat");
        r.putObject("trade_flow").put("net_delta_1m", 0.0);
        r.putObject("order_book_depth").put("bid_ask_ratio", 1.0);
        return r;
    }

    private static long ms(LocalDate d, int h, int m) {
        return d.atTime(LocalTime.of(h, m)).atZone(BERLIN).toInstant().toEpochMilli();
    }

    private static void bar(ArrayNode k, int minute, double o, double h, double l, double c, double vol) {
        long t = ms(TODAY, 7, 0) + minute * 60_000L;
        ArrayNode b = k.addArray();
        b.add(t).add(o).add(h).add(l).add(c).add(vol).add(t + 59_999L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
    }

    private static ArrayNode series(int heavyBar, boolean pullback) {
        ArrayNode k = M.createArrayNode();
        List<LocalDate> days = new ArrayList<>();
        LocalDate d = TODAY.minusDays(1);
        while (days.size() < 20) {
            if (d.getDayOfWeek() != DayOfWeek.SATURDAY && d.getDayOfWeek() != DayOfWeek.SUNDAY) days.add(0, d);
            d = d.minusDays(1);
        }
        double[] legs = new double[20];
        java.util.Arrays.fill(legs, 20.0);
        legs[10] = 180.0;
        legs[19] = 100.0;
        for (int i = 0; i < 20; i++) {
            for (int m = 0; m < 121; m++) {
                long t = ms(days.get(i), 7, 0) + m * 60_000L;
                double hi = (m == 10) ? P + legs[i] : P + 0.5;
                ArrayNode b = k.addArray();
                b.add(t).add(P).add(hi).add(P - 0.5).add(P).add(10.0).add(t + 59_999L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
            }
        }
        double prev = 24010.0;
        for (int m = 0; m < 50; m++) {
            double c = 24010.0 + 2.0 * (m + 1);
            double vol = m == heavyBar ? 100.0 : (m <= 32 ? 10.0 : 2.0);
            bar(k, m, prev, c, prev, c, vol);
            prev = c;
        }
        if (pullback) {   // balance after the extreme: back inside the 10 bars before it
            bar(k, 50, 24108, 24110, 24100, 24100, 10);
            bar(k, 51, 24100, 24102, 24090, 24092, 10);
            for (int m = 52; m < 60; m++) bar(k, m, 24095, 24100, 24092, 24095, 10);
        }
        return k;
    }

    /** The single A1 fade_short candidate of the given arm, or null. */
    private static JsonNode arm(ArrayNode out, String a) {
        JsonNode found = null;
        for (JsonNode c : out) {
            if (a.equals(c.path("arm").asText()) && "fade_short".equals(c.path("setup_type").asText())
                    && (!c.has("entry_path") || "A1".equals(c.get("entry_path").asText()))) {
                assertNull(found, "exactly one " + a + " A1 candidate");
                found = c;
            }
        }
        return found;
    }

    private static ArrayNode build(ArrayNode k, double price) {
        return SetupCandidatesBuilder.build(M, root(price), new HashMap<>(), k);
    }

    @Test
    void profileArmFiresBesidePriceArmAndPriceIsUnchanged() {
        ArrayNode out = build(series(2, false), 24110.0);
        JsonNode price = arm(out, "price");
        JsonNode prof = arm(out, "profile");
        assertNotNull(price, "price arm A1");
        assertNotNull(prof, "profile arm A1 (thin top, POC in the bottom third)");
        assertEquals(24110.0, price.get("zone").get("price").asDouble(), 1e-9);
        assertEquals(24130.0, price.get("math").get("stop").asDouble(), 1e-9);
        assertEquals(24010.0, price.get("math").get("target").asDouble(), 1e-9);
        assertFalse(price.has("profile_items"));
        List<String> cond = new ArrayList<>();
        for (JsonNode x : prof.get("conditions")) cond.add(x.asText());
        assertEquals(List.of("A-C1", "A-C2", "A-C3"), cond);
        JsonNode c3 = prof.get("profile_items").get("A-C3");
        assertTrue(c3.get("thin").asBoolean());
        assertEquals(0, c3.get("poc_third").asInt());
        assertEquals(34.0, c3.get("top").asDouble(), 1e-9);
        assertEquals(170.0, c3.get("mid").asDouble(), 1e-9);
        assertEquals(250.0, c3.get("bottom").asDouble(), 1e-9);
        assertEquals(price.get("math").get("stop").asDouble(), prof.get("math").get("stop").asDouble(), 1e-9);
        for (JsonNode n : prof.get("not_in_data")) {
            assertNotEquals("A-C3", n.asText());
            assertNotEquals("A-P3", n.asText());
            assertNotEquals("A-P8", n.asText());
        }
    }

    @Test
    void noProfileArmWhenTopIsNotThin() {
        ArrayNode k = series(2, false);
        for (int i = k.size() - 50; i < k.size(); i++) ((ArrayNode) k.get(i)).set(5, M.getNodeFactory().numberNode(10.0));
        ArrayNode out = build(k, 24110.0);
        assertNotNull(arm(out, "price"));
        assertNull(arm(out, "profile"));
    }

    @Test
    void noProfileArmWithoutVolume() {
        ArrayNode k = series(2, false);
        for (int i = k.size() - 50; i < k.size(); i++) ((ArrayNode) k.get(i)).set(5, M.getNodeFactory().nullNode());
        assertNull(arm(build(k, 24110.0), "profile"), "volume NOT_IN_DATA: no profile arm, never a false proof");
    }

    @Test
    void daxFeedIsNotInDataUntilParityPasses() {
        ObjectNode r = root(24110.0);
        r.put("asset", "GER40");
        ArrayNode out = SetupCandidatesBuilder.build(M, r, new HashMap<>(), series(2, false));
        assertNotNull(arm(out, "price"));
        assertNull(arm(out, "profile"), "PROFILE_PARITY.md: PROFILE arm on DAX = NOT_IN_DATA");
        System.setProperty(SpikeFadeProfile.DAX_PROPERTY, "true");
        assertNotNull(arm(SetupCandidatesBuilder.build(M, r, new HashMap<>(), series(2, false)), "profile"));
    }

    @Test
    void failedPBreakoutAndLowerBShapeAreListed() {
        // POC row of bar 30 (close 24072, row 18 of 30, fraction (18.5)/30 = 0.6167 >= 0.5): P-shaped leg.
        // Extreme 24110 > balance high (bars 39-48, high 24108); last close 24095 inside 24088-24108 ; bars 50-59 all close inside.
        // Sub-profile of bars 50-59: range 24090-24110, rows of 0.6667; closes 24095 x8 = 80 (row 7) -> fraction 7.5/30 = 0.25.
        ArrayNode out = build(series(30, true), 24095.0);
        JsonNode prof = arm(out, "profile");
        assertNotNull(prof);
        JsonNode p3 = prof.get("profile_items").get("A-P3");
        assertTrue(p3.get("p_shape").asBoolean());
        assertTrue(p3.get("broke_out").asBoolean());
        assertTrue(p3.get("back_inside").asBoolean());
        assertEquals(10, p3.get("bars_inside").asInt());
        assertEquals(0.25, prof.get("profile_items").get("A-P8").get("poc_frac").asDouble(), 1e-9);
        List<String> proofs = new ArrayList<>();
        for (JsonNode x : prof.get("proofs")) proofs.add(x.asText());
        assertTrue(proofs.contains("A-P3"), proofs.toString());
        assertTrue(proofs.contains("A-P8"), proofs.toString());
        assertEquals(proofs.size(), prof.get("proof_count").asInt());
        assertEquals(proofs.size(), prof.get("score").get("proof_count").asInt());
    }

    @Test
    void pocInLowerThirdIsNotAPShape() {
        JsonNode prof = arm(build(series(2, true), 24095.0), "profile");
        assertNotNull(prof);
        assertFalse(prof.get("profile_items").get("A-P3").get("p_shape").asBoolean());
        for (JsonNode x : prof.get("proofs")) assertNotEquals("A-P3", x.asText());
    }

    @Test
    void flagOffAddsNothing() {
        System.clearProperty("mts.spikeFade");
        ArrayNode out = build(series(2, false), 24110.0);
        for (JsonNode c : out) {
            assertFalse(c.has("arm"));
            assertNotEquals("fade_short", c.path("setup_type").asText());
        }
    }
}
