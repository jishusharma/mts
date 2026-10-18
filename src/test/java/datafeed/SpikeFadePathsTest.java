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
 * Card tom-encode-fade-entry-paths (TOM_LAYER_V2_SPEC sections 2.3, 2.4 A-S3, 2.6 A-M5, 13): paths A2 and A3 plus one
 * re-entry per session, behind -Dmts.spikeFade. Same prior sessions and 07:00 ramp as SpikeFadeTest (ramp 24010 ->
 * 24110, extreme bar 49: open 24108, high 24110; +2 per bar so the 10 bars before the extreme, bars 39-48, have lows 24088..24106).
 *
 * <p>A3 hand numbers: balance after the extreme = bars 50-59 with high 24110 and low 24090; bar 60 closes 24088 (below
 * 24090) -> A3, entry reference = that close 24088 (entry itself is the NEXT bar's open, bar 61 opens 24087), stop A-S3 =
 * balance high 24110, target 24010 (A-T1). Gross RR = (24088 - 24010) / (24110 - 24088) = 78 / 22 = 3.5454 -> 3.55.
 * GER40 fee = entry * 1e-5 = 0.24088 points: net RR = (78 - 0.24088) / (22 + 0.24088) = 77.75912 / 22.24088 = 3.4963 -> 3.50.
 *
 * <p>A2 hand numbers: first buying zone = lowest low of the 10 bars before the extreme = 24088. Bar 51 closes 24085
 * (traded through), bar 52 pulls back to close 24087 (low since the extreme 24083) -> sell limit 24088, stop 24130
 * (A-S2, same as A1: no prior high above 24110), target 24010. Gross = 78 / 42 = 1.8571 -> 1.86; net = (78 - 0.24088) / (42 + 0.24088)
 * = 77.75912 / 42.24088 = 1.8408 -> 1.84.
 */
public class SpikeFadePathsTest {
    private static final ObjectMapper M = new ObjectMapper();
    private static final ZoneId BERLIN = ZoneId.of("Europe/Berlin");
    private static final LocalDate TODAY = LocalDate.of(2026, 10, 14);
    private static final double P = 23900.0;
    private static final String KEY = SpikeFadeSessionState.key("GER40", TODAY);

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
        System.clearProperty(SpikeFadeSessionState.FILE_PROPERTY);
        SpikeFadeSessionState.resetShared();
    }

    private static ObjectNode root(double price) {
        ObjectNode r = M.createObjectNode();
        r.put("asset", "GER40");
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

    private static void bar(ArrayNode k, int minute, double o, double h, double l, double c) {
        long t = ms(TODAY, 7, 0) + minute * 60_000L;
        ArrayNode b = k.addArray();
        b.add(t).add(o).add(h).add(l).add(c).add(10.0).add(t + 59_999L).add(1000.0).add(10).add(5.0).add(500.0).add(0);
    }

    private static ArrayNode withRamp() {
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
            bar(k, m, prev, c, prev, c);
            prev = c;
        }
        return k;
    }

    /** bars 50-59: balance 24090-24110 after the extreme; bar 60 closes 24088 (break); bar 61 opens 24087. */
    private static ArrayNode a3Series(boolean withBreak) {
        ArrayNode k = withRamp();
        bar(k, 50, 24108, 24110, 24100, 24100);
        bar(k, 51, 24100, 24102, 24090, 24092);
        for (int m = 52; m < 60; m++) bar(k, m, 24095, 24100, 24092, 24095);
        if (withBreak) bar(k, 60, 24095, 24095, 24088, 24088);
        return k;
    }

    private static ArrayNode a2Series() {
        ArrayNode k = withRamp();
        bar(k, 50, 24110, 24110, 24095, 24095);
        bar(k, 51, 24095, 24095, 24083, 24085);
        bar(k, 52, 24085, 24089, 24084, 24087);
        return k;
    }

    private static JsonNode path(ArrayNode out, String p) {
        JsonNode found = null;
        for (JsonNode c : out) if (p.equals(c.path("entry_path").asText())) {
            assertNull(found, "exactly one " + p);
            found = c;
        }
        return found;
    }

    private static ArrayNode build(ArrayNode k, double price) {
        return SetupCandidatesBuilder.build(M, root(price), new HashMap<>(), k);
    }

    @Test
    void a3FiresOnCloseBelowTopBalance() {
        ArrayNode k = a3Series(true);
        JsonNode c = path(build(k, 24088.0), "A3");
        assertNotNull(c, "A3 expected");
        assertEquals("fade_short", c.get("setup_type").asText());
        assertEquals("A-S3", c.get("stop_rule").asText());
        assertEquals("stop_market", c.get("entry_type").asText());
        assertEquals("next_open", c.get("entry_rule").asText());
        assertEquals(24090.0, c.get("zone").get("price").asDouble(), 1e-9);
        assertEquals(24088.0, c.get("entry_ref").asDouble(), 1e-9);
        JsonNode math = c.get("math");
        assertEquals(24110.0, math.get("stop").asDouble(), 1e-9);
        assertEquals(24010.0, math.get("target").asDouble(), 1e-9);
        assertEquals(3.55, math.get("gross_rr").asDouble(), 1e-9);
        assertEquals(3.50, math.get("net_rr").asDouble(), 1e-9);
        // stop_n5 by hand: A1 value 20 * 23900 / 24110 = 19.8257; A3 risk 22 vs A1 risk 20, entry 24088 vs 24110:
        // 19.8257 * (22 / 20) * (24110 / 24088) = 21.828
        assertEquals(21.828, c.get("stop_n5").asDouble(), 0.01);
        assertFalse(c.has("rawStop"));
        assertNull(path(build(k, 24088.0), "A2"), "no pullback bar: not A2");
    }

    @Test
    void a3EntryIsTheNextBarOpen() {
        ArrayNode k = a3Series(true);
        bar(k, 61, 24087, 24087, 24080, 24081);
        long[] t = new long[k.size()];
        double[] o = new double[k.size()], h = new double[k.size()], l = new double[k.size()], c = new double[k.size()];
        for (int i = 0; i < k.size(); i++) {
            JsonNode b = k.get(i);
            t[i] = b.get(0).asLong(); o[i] = b.get(1).asDouble(); h[i] = b.get(2).asDouble();
            l[i] = b.get(3).asDouble(); c[i] = b.get(4).asDouble();
        }
        SpikeFadeDetector.Bars full = new SpikeFadeDetector.Bars(t, o, h, l, c);
        int signal = full.n - 2;   // bar 60
        assertEquals(24087.0, SpikeFadePaths.entryOpen(full, signal), 1e-9);
        assertTrue(Double.isNaN(SpikeFadePaths.entryOpen(full, full.n - 1)), "no next bar yet");
    }

    @Test
    void balanceStillHoldingFiresNoA3() {
        ArrayNode k = a3Series(false);
        bar(k, 60, 24095, 24096, 24091, 24092);   // close 24092 is inside 24090-24110
        assertNull(path(build(k, 24092.0), "A3"));
    }

    @Test
    void a2FiresOnPullbackAfterTradeThrough() {
        JsonNode c = path(build(a2Series(), 24087.0), "A2");
        assertNotNull(c, "A2 expected");
        assertEquals("sell_limit", c.get("entry_type").asText());
        assertEquals(24088.0, c.get("zone").get("price").asDouble(), 1e-9);
        JsonNode math = c.get("math");
        assertEquals(24130.0, math.get("stop").asDouble(), 1e-9);
        assertEquals(24010.0, math.get("target").asDouble(), 1e-9);
        assertEquals(1.86, math.get("gross_rr").asDouble(), 1e-9);
        assertEquals(1.84, math.get("net_rr").asDouble(), 1e-9);
        assertNull(path(build(a2Series(), 24087.0), "A3"), "only 2 bars after the extreme: no balance");
    }

    @Test
    void a2NeedsTheTradeThrough() {
        ArrayNode k = withRamp();
        bar(k, 50, 24110, 24110, 24095, 24095);
        bar(k, 51, 24095, 24100, 24092, 24098);   // never closes below 24088
        assertNull(path(build(k, 24098.0), "A2"));
    }

    @Test
    void secondAttemptAllowedThirdSuppressedAndLogged() {
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        long t0 = ms(TODAY, 7, 55);
        assertTrue(s.admit(TODAY, t0).allowed, "first attempt");
        s.recordEntry(TODAY, t0, "A1");
        assertFalse(s.admit(TODAY, t0 + 60_000L).allowed, "first still open: no second entry");
        s.recordStop(TODAY, t0 + 120_000L);
        assertFalse(s.admit(TODAY, t0 + 120_000L).allowed, "same minute as the stop is not a fresh signal");
        assertTrue(s.admit(TODAY, t0 + 180_000L).allowed, "re-entry after a stop on a fresh signal (A-M5)");
        s.recordEntry(TODAY, t0 + 180_000L, "A3");
        s.recordStop(TODAY, t0 + 240_000L);
        SpikeFadeSessionState.Decision d = s.admit(TODAY, t0 + 300_000L);
        assertFalse(d.allowed);
        assertTrue(d.reason.contains("third"), d.reason);
        assertTrue(s.suppressedLog().size() >= 1);
        assertTrue(s.admit(TODAY.plusDays(1), ms(TODAY.plusDays(1), 7, 30)).allowed, "state resets with the session");
    }

    @Test
    void thirdSignalInTheBuilderIsSuppressed() {
        ArrayNode k = a3Series(true);
        long t0 = ms(TODAY, 7, 30);
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        s.recordEntry(KEY, t0, "A1", 24130.0);
        s.recordStop(KEY, t0 + 60_000L);
        s.recordEntry(KEY, t0 + 120_000L, "A2", 24130.0);
        s.recordStop(KEY, t0 + 180_000L);
        assertNull(path(build(k, 24088.0), "A3"), "third attempt in the session: suppressed");
        assertEquals(1, s.suppressedLog().size());
    }

    @Test
    void stateSurvivesARestartMidSession() {
        long t0 = ms(TODAY, 7, 30);
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        s.recordEntry(KEY, t0, "A1", 24130.0);
        s.recordStop(KEY, t0 + 60_000L);
        s.recordEntry(KEY, t0 + 120_000L, "A2", 24130.0);
        s.recordStop(KEY, t0 + 180_000L);
        SpikeFadeSessionState.resetShared();   // process restart: memory gone, file stays
        assertFalse(SpikeFadeSessionState.shared().admit(KEY, t0 + 300_000L).allowed);
        assertNull(path(build(a3Series(true), 24088.0), "A3"));
    }

    @Test
    void unreadableStateFileFailsClosed() throws Exception {
        Path f = Path.of(System.getProperty(SpikeFadeSessionState.FILE_PROPERTY));
        Files.writeString(f, "{not json");
        SpikeFadeSessionState.resetShared();
        assertFalse(SpikeFadeSessionState.shared().admit(TODAY, ms(TODAY, 7, 30)).allowed);
    }

    @Test
    void flagOffEmitsNoPathCandidates() {
        System.clearProperty("mts.spikeFade");
        assertEquals(0, build(a3Series(true), 24088.0).size());
    }

    @Test
    void pathA1IsUnchangedByThePaths() {
        ArrayNode out = build(a3Series(true), 24088.0);
        assertNotNull(path(out, "A1"), "A1 still emitted beside A3");
    }

    // ---- review round 1 (blind review REJECT): builder records attempts, A2 tightened, one candidate per instant, log once ----

    @Test
    void builderRecordsTheAttemptItEmitsAndRefusesTheNextBar() {
        ArrayNode k = a3Series(true);
        assertNotNull(path(build(k, 24088.0), "A3"));
        assertNotNull(path(build(k, 24088.0), "A3"), "same snapshot again: same signal, same answer");
        bar(k, 61, 24087, 24087, 24080, 24081);   // next bar closes below the balance low again
        assertNull(path(build(k, 24081.0), "A3"), "attempt 1 still open: the repeat signal is not a new attempt");
    }

    @Test
    void stopOutObservedFromBarsOpensTheReEntry() {
        ArrayNode k = a3Series(true);
        assertNotNull(path(build(k, 24088.0), "A3"));   // attempt 1, stop 24110
        bar(k, 61, 24087, 24112, 24087, 24111);          // high 24112 >= stop 24110: stopped out
        for (int m = 62; m < 70; m++) bar(k, m, 24100, 24101, 24095, 24100);
        bar(k, 70, 24095, 24095, 24086, 24086);          // fresh close below the balance
        ArrayNode out = build(k, 24086.0);
        assertNotNull(path(out, "A3"), "re-entry on a fresh signal after the stop: " + out);
        assertEquals(2, SpikeFadeSessionState.shared().attempts(SpikeFadeSessionState.key("GER40", TODAY)));
        for (int m = 71; m < 80; m++) bar(k, m, 24100, 24112, 24095, 24100);   // stop hit again, third signal below
        bar(k, 80, 24095, 24095, 24080, 24080);
        assertNull(path(build(k, 24080.0), "A3"), "third attempt: suppressed");
    }

    @Test
    void oneCandidatePerInstantA3WinsOverA2() {
        ArrayNode k = withRamp();
        bar(k, 50, 24108, 24110, 24100, 24100);
        bar(k, 51, 24100, 24102, 24084, 24085);   // through 24088
        for (int m = 52; m < 57; m++) bar(k, m, 24085, 24086, 24083, 24085);
        bar(k, 57, 24085, 24087, 24084, 24086);   // pullback close 24086 above the prior low 24083, below the zone 24088
        bar(k, 58, 24086, 24086, 24081, 24082);   // closes below the balance low 24083: A3 signal
        ArrayNode out = build(k, 24082.0);
        long n = 0;
        for (JsonNode c : out) if (c.path("entry_path").asText().matches("A2|A3")) n++;
        assertEquals(1, n, out.toString());
        assertNotNull(path(out, "A3"));
    }

    @Test
    void a2DoesNotFireOnTheTradeThroughBarItself() {
        ArrayNode k = withRamp();
        bar(k, 50, 24110, 24110, 24095, 24095);
        bar(k, 51, 24095, 24095, 24083, 24085);   // the bar that trades through is the last bar
        assertNull(path(build(k, 24085.0), "A2"));
    }

    @Test
    void a2DoesNotFireOnceCloseWentBackAboveTheZone() {
        ArrayNode k = withRamp();
        bar(k, 50, 24110, 24110, 24095, 24095);
        bar(k, 51, 24095, 24095, 24083, 24085);
        bar(k, 52, 24085, 24095, 24084, 24093);   // close back above 24088: the limit would have filled
        bar(k, 53, 24093, 24093, 24085, 24087);   // under the zone again
        assertNull(path(build(k, 24087.0), "A2"));
    }

    @Test
    void attemptsAreKeyedBySymbolAndDate() {
        long t0 = ms(TODAY, 7, 30);
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        s.recordEntry(SpikeFadeSessionState.key("GER40", TODAY), t0, "A3", 24110.0);
        assertFalse(s.admit(SpikeFadeSessionState.key("GER40", TODAY), t0 + 60_000L).allowed);
        assertTrue(s.admit(SpikeFadeSessionState.key("BTCUSDT", TODAY), t0 + 60_000L).allowed, "other instrument, own cap");
    }

    @Test
    void unreadableFileIsNeverOverwritten() throws Exception {
        Path f = Path.of(System.getProperty(SpikeFadeSessionState.FILE_PROPERTY));
        Files.writeString(f, "{\"sessions\": {\"GER40|2026-10-14\": [{\"entry_ms\": 1, \"path\": \"A3\"}], \"x\": nope");
        String before = Files.readString(f);
        SpikeFadeSessionState.resetShared();
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        s.recordEntry(TODAY, 5L, "A2");
        s.recordStop(TODAY, 6L);
        assertEquals(before, Files.readString(f), "damaged file kept as found");
        assertFalse(s.admit(TODAY, 9L).allowed);
    }

    @Test
    void stopIsCheckedAgainstTheUnroundedPrice() {
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        long t0 = ms(TODAY, 7, 49);
        String key = SpikeFadeSessionState.key("GER40", TODAY);
        s.recordEntry(key, t0, "A3", 24110.004);
        ArrayNode k = withRamp();
        bar(k, 50, 24108, 24110.0, 24090, 24095);   // high 24110.00 is below the true stop 24110.004
        long[] t = new long[k.size()];
        double[] o = new double[t.length], h = new double[t.length], l = new double[t.length], c = new double[t.length];
        for (int i = 0; i < t.length; i++) {
            JsonNode b = k.get(i);
            t[i] = b.get(0).asLong(); o[i] = b.get(1).asDouble(); h[i] = b.get(2).asDouble();
            l[i] = b.get(3).asDouble(); c[i] = b.get(4).asDouble();
        }
        s.observe(key, TODAY, new SpikeFadeDetector.Bars(t, o, h, l, c));
        assertFalse(s.admit(key, ms(TODAY, 8, 30)).allowed, "not stopped: re-entry stays closed");
    }

    @Test
    void refusalIsLoggedOncePerSessionAndReason() {
        SpikeFadeSessionState s = SpikeFadeSessionState.shared();
        long t0 = ms(TODAY, 7, 30);
        s.recordEntry(TODAY, t0, "A1");
        for (int i = 1; i <= 5; i++) assertFalse(s.admit(TODAY, t0 + i * 60_000L).allowed);
        assertEquals(1, s.suppressedLog().size());
    }

    @Test
    void stateFileChangedByAnotherProcessIsSeen() {
        long t0 = ms(TODAY, 7, 30);
        SpikeFadeSessionState a = SpikeFadeSessionState.shared();
        assertTrue(a.admit(TODAY, t0).allowed);
        SpikeFadeSessionState other = new SpikeFadeSessionState(Path.of(System.getProperty(SpikeFadeSessionState.FILE_PROPERTY)));
        other.recordEntry(TODAY, t0, "A3");
        assertFalse(a.admit(TODAY, t0 + 60_000L).allowed, "first attempt of the other process is open");
    }
}
