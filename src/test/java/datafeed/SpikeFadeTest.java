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
 * Card tom-encode-spike-fade (TOM_LAYER_V2_SPEC sections 12-15): fade_short, PRICE arm, behind -Dmts.spikeFade.
 * Hand numbers (spec card): prior-day high 24000, session open 24010, impulse to 24110, old high 24080 taken,
 * 5-minute inside bar at the top -> one fade_short at 24110, stop 24130 (A-S2, 20 points), target 24010 (A-T1),
 * gross RR 100/20 = 5.0; GER40 net RR (100 - 0.2411) / (20 + 0.2411) = 99.7589 / 20.2411 = 4.9285, proofs P4 + P5.
 * Prior 20 sessions: price P = 23900, flat bars with a 1-point range; one leg bar per session (high P + leg):
 * 18 sessions leg 20, the session holding the old high leg 180 (24080), the prior day leg 100 (24000).
 * Median prior leg = 20 / 23900 = 0.0837 %; today's leg = 100 / 24010 = 0.4165 %: above the median; the prior day leg 100 / 23900 = 0.4184 % and the 180 leg are above it: rank 18/20 = 0.9.
 * N5 = median true range of the 5-minute bars = 1 point = 1 / 23900 of price; stop in N5 = 20 * 23900 / 24110 = 19.8257.
 */
public class SpikeFadeTest {
    private static final ObjectMapper M = new ObjectMapper();
    private static final ZoneId BERLIN = ZoneId.of("Europe/Berlin");
    private static final LocalDate TODAY = LocalDate.of(2026, 10, 14);   // a Wednesday
    private static final double P = 23900.0;

    @BeforeEach
    void setUp(@TempDir Path tmp) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
        System.setProperty("mts.spikeFade", "true");
    }

    @AfterEach
    void tearDown() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
        System.clearProperty("mts.spikeFade");
    }

    private static ObjectNode root(String asset, double price) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", asset);
        r.put("current_price", price);
        ObjectNode cond = r.putObject("conditions");
        cond.put("vwap_slope", "flat");
        cond.put("cvd_slope", "flat");
        cond.put("price_vs_va", "in_va");
        cond.put("price_vs_poc", "above");
        cond.putNull("fvg_nearest_unfilled");
        ObjectNode vwap = r.putObject("vwap");
        vwap.put("price", 100.0);   // far from price: no vwap zone survives the distance cap
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

    private static void bar(ArrayNode k, long t, double o, double h, double l, double c) {
        ArrayNode b = k.addArray();
        b.add(t).add(o).add(h).add(l).add(c).add(10.0).add(t + 59_999L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
    }

    /** 20 prior weekdays before TODAY, 07:00-09:00 Berlin; legs[i] per session (oldest first). */
    private static ArrayNode priorSessions(double[] legs) {
        ArrayNode k = M.createArrayNode();
        List<LocalDate> days = new ArrayList<>();
        LocalDate d = TODAY.minusDays(1);
        while (days.size() < 20) {
            if (d.getDayOfWeek() != DayOfWeek.SATURDAY && d.getDayOfWeek() != DayOfWeek.SUNDAY) days.add(0, d);
            d = d.minusDays(1);
        }
        for (int i = 0; i < 20; i++) {
            LocalDate day = days.get(i);
            for (int m = 0; m < 121; m++) {
                long t = ms(day, 7, 0) + m * 60_000L;
                double hi = (m == 10) ? P + legs[i] : P + 0.5;
                bar(k, t, P, hi, P - 0.5, P);
            }
        }
        return k;
    }

    private static double[] legs() {
        double[] l = new double[20];
        java.util.Arrays.fill(l, 20.0);
        l[10] = 180.0;   // old high 24080
        l[19] = 100.0;   // prior day high 24000
        return l;
    }

    /** Today 07:00-07:54: ramp 24010 -> 24110 (+2 per 1m bar, bars 0-49), then flat 24106 (bars 50-54). */
    private static void today(ArrayNode k) {
        long t0 = ms(TODAY, 7, 0);
        double prev = 24010.0;
        for (int m = 0; m < 50; m++) {
            double c = 24010.0 + 2.0 * (m + 1);
            bar(k, t0 + m * 60_000L, prev, c, prev, c);
            prev = c;
        }
        for (int m = 50; m < 55; m++) bar(k, t0 + m * 60_000L, 24106.0, 24106.0, 24106.0, 24106.0);
    }

    private static ArrayNode series() {
        ArrayNode k = priorSessions(legs());
        today(k);
        return k;
    }

    private static JsonNode fade(ArrayNode out) {
        JsonNode found = null;
        for (JsonNode c : out) if ("fade_short".equals(c.path("setup_type").asText())) {
            assertNull(found, "exactly one fade_short");
            found = c;
        }
        return found;
    }

    @Test
    void firesWithHandNumbers() {
        ArrayNode out = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), series());
        JsonNode c = fade(out);
        assertNotNull(c, "fade_short expected: " + out);
        assertEquals("short", c.get("direction").asText());
        assertEquals(24110.0, c.get("zone").get("price").asDouble(), 1e-9);
        JsonNode math = c.get("math");
        assertEquals(24130.0, math.get("stop").asDouble(), 1e-9);
        assertEquals(24010.0, math.get("target").asDouble(), 1e-9);
        assertEquals(5.0, math.get("gross_rr").asDouble(), 1e-9);
        assertEquals(4.93, math.get("net_rr").asDouble(), 1e-9);   // 4.9285 rounded to 2 dp like every candidate
        assertEquals("A-S2", c.get("stop_rule").asText());
        List<String> proofs = new ArrayList<>();
        c.get("proofs").forEach(n -> proofs.add(n.asText()));
        assertEquals(List.of("A-P4", "A-P5"), proofs);
        assertEquals(0.9, c.get("impulse_rank").asDouble(), 1e-9);
        assertEquals("balance", c.get("market_state").asText());
        assertEquals("gap_day", c.get("day_type").asText());      // open 24010 above the prior day's range
        assertEquals("above", c.get("htf_bias").asText());        // 24106 above prior_week_poc 23950
        assertEquals(19.8257, c.get("stop_n5").asDouble(), 1e-3);
    }

    @Test
    void flatSeriesFiresNothing() {
        ArrayNode k = priorSessions(legs());
        long t0 = ms(TODAY, 7, 0);
        for (int m = 0; m < 55; m++) bar(k, t0 + m * 60_000L, 24010.0, 24010.0, 24010.0, 24010.0);
        ArrayNode out = SetupCandidatesBuilder.build(M, root("GER40", 24010.0), new HashMap<>(), k);
        assertNull(fade(out), "leg 0 is not above the median: " + out);
    }

    @Test
    void notAbovePriorDayRangeFiresNothing() {
        double[] l = legs();
        l[19] = 400.0;   // prior day high 24300: price 24106 is inside the prior range, A-C2 fails
        ArrayNode k = priorSessions(l);
        today(k);
        ArrayNode out = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), k);
        assertNull(fade(out), "A-C2 fails when price is inside the prior day range: " + out);
    }

    @Test
    void shortHistoryIsNotInDataAndFiresNothing() {
        ArrayNode k = M.createArrayNode();
        today(k);
        ArrayNode out = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), k);
        assertNull(fade(out), "no prior sessions: impulse_rank is NOT_IN_DATA, fail closed: " + out);
    }

    @Test
    void flagOffEmitsNothingOnTheSameSeries() {
        System.clearProperty("mts.spikeFade");
        ArrayNode out = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), series());
        assertNull(fade(out));
        assertEquals(0, out.size(), out.toString());
    }

    @Test
    void priorHighAboveZoneUsesThatLevelAsStop() {
        // the session holding the old high now reaches 24160: a prior high above 24110 exists -> A-S1, stop = that level, no P5
        double[] l = legs();
        l[10] = 260.0;
        ArrayNode k = priorSessions(l);
        today(k);
        JsonNode c = fade(SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), k));
        assertNotNull(c);
        assertEquals("A-S1", c.get("stop_rule").asText());
        assertEquals(24160.0, c.get("math").get("stop").asDouble(), 1e-9);
        List<String> proofs = new ArrayList<>();
        c.get("proofs").forEach(n -> proofs.add(n.asText()));
        assertEquals(List.of("A-P4"), proofs);
    }

    /** Card tom-v2-recall-fire-rate: a snapshot's 24 h 1m series fails closed; the longer fade series fires. */
    @Test
    void fadeCallUsesTheLongSeriesWhenGiven() {
        ArrayNode shortSeries = M.createArrayNode();
        today(shortSeries);   // 55 bars, no prior sessions: what a 24 h snapshot carries
        ArrayNode none = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), shortSeries);
        assertNull(fade(none), "24 h series alone fails closed: " + none);
        ArrayNode viaLong = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), shortSeries, series());
        JsonNode c = fade(viaLong);
        assertNotNull(c, "long fade series must fire: " + viaLong);
        assertEquals(24110.0, c.get("zone").get("price").asDouble(), 1e-9);
        ArrayNode viaNull = SetupCandidatesBuilder.build(M, root("GER40", 24106.0), new HashMap<>(), shortSeries, null);
        assertNull(fade(viaNull));
    }

    /** A slice of a whole-archive Bars gives the same candidate as the JSON series cut at the same bar (replay harness). */
    @Test
    void slicedBarsEqualJsonSeries() {
        ArrayNode k = series();
        int n = k.size();
        long[] t = new long[n];
        double[] o = new double[n], h = new double[n], l = new double[n], c = new double[n];
        for (int i = 0; i < n; i++) {
            JsonNode b = k.get(i);
            t[i] = b.get(0).asLong();
            o[i] = b.get(1).asDouble();
            h[i] = b.get(2).asDouble();
            l[i] = b.get(3).asDouble();
            c[i] = b.get(4).asDouble();
        }
        SpikeFadeDetector.Bars full = new SpikeFadeDetector.Bars(t, o, h, l, c);
        ObjectNode r = root("GER40", 24106.0);
        ObjectNode fromJson = SpikeFadeDetector.detect(M, r, k, "balance", "GER40");
        ObjectNode fromSlice = SpikeFadeDetector.detect(M, r, new SpikeFadeDetector.Bars(full, 0, n), "balance", "GER40");
        assertNotNull(fromJson);
        assertEquals(fromJson, fromSlice);
        // a cut one bar earlier is the series a snapshot one minute before would see: bar 54 still inside the same window
        ObjectNode earlier = SpikeFadeDetector.detect(M, r, new SpikeFadeDetector.Bars(full, 0, n - 1), "balance", "GER40");
        assertNotNull(earlier);
        assertEquals(24110.0, earlier.get("zone").get("price").asDouble(), 1e-9);
    }
}
