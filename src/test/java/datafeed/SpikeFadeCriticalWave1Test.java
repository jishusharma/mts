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
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Critical test wave 1, item 3 (MyTradingSys/research/critical_test_wave1_2026-10-30/ITEM3_SPIKEFADE_CLASSIFYSTATE.md).
 * Hand numbers for the family A fade trigger (TOM_LAYER_V2_SPEC sections 2, 13: A-C1 leg above the median of the prior
 * 20 same-clock legs, A-C2 close above the prior day's high, A-S1/A-S2 stop, A-T1 target = session open, A-P2/P5 proofs,
 * FORMULAS 17 net R:R with BTC taker 0.0005/side). Computed by hand, not from the detector:
 *
 * Prior 20 weekdays (07:00-09:00 Berlin, 1m bars, flat 1000 +-0.5 with one leg bar at minute 10 of high 1000+leg):
 *   legs 5 everywhere except the prior day (index 19) leg 20. Same-clock leg % = leg/1000*100: 19 x 0.5 %, 1 x 2.0 %.
 *   Median of 20 = (sorted[9] + sorted[10]) / 2 = 0.5 %. Prior day high = 1020; every other prior high = 1005.
 * Case A today: bar i closes 1010+i up to the high 1040 at bar 30, then 1039..1030 at bars 31..40 (no wicks).
 *   leg = 30/1010*100 = 2.9703 %: above the median; rank = 20/20 = 1.0. Last close 1030 > prior high 1020: A-C2 holds.
 *   Nothing above 1040 among prior highs -> A-S2 on BTC (OURS, TLV2:323 min width): stop 1040 * 1.004 = 1044.16.
 *   Target = open 1010. risk 4.16, reward 30, gross 7.2115 -> 7.21.
 *   net = (30 - 2*0.0005*1040) / (4.16 + 1.04) = 28.96 / 5.2 = 5.5692 -> 5.57.
 *   A-P2: fall rate (1040-1030)/10 = 1.0 is NOT above the leg rate 30/30 = 1.0 -> no. A-P5: 1040 > 1020 yes.
 *   A-P7: no low under 1010 after the high. A-P4: last 1m bar 07:40 opens a new 5m bucket (incomplete), completed
 *   buckets 07:30 (low 1036) and 07:35 (low 1031 < 1036) -> not inside -> no. Proofs = [A-P5].
 */
public class SpikeFadeCriticalWave1Test {
    private static final ObjectMapper M = new ObjectMapper();
    private static final ZoneId BERLIN = ZoneId.of("Europe/Berlin");
    private static final LocalDate TODAY = LocalDate.of(2026, 10, 14);   // Wednesday, CEST

    @BeforeEach
    void setUp(@TempDir Path tmp) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, "{\"net_rr_floor\": 1.25}");
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
    }

    @AfterEach
    void tearDown() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
    }

    private static long ms(LocalDate d, int h, int m) {
        return d.atTime(LocalTime.of(h, m)).atZone(BERLIN).toInstant().toEpochMilli();
    }

    private static void bar(ArrayNode k, long t, double o, double h, double l, double c) {
        k.addArray().add(t).add(o).add(h).add(l).add(c).add(10.0);
    }

    /** 20 prior weekdays; baseline price p, leg bar at minute 10 of session i has high p + legs[i]. */
    private static ArrayNode prior(double p, double[] legs) {
        ArrayNode k = M.createArrayNode();
        List<LocalDate> days = new ArrayList<>();
        LocalDate d = TODAY.minusDays(1);
        while (days.size() < 20) {
            if (d.getDayOfWeek() != DayOfWeek.SATURDAY && d.getDayOfWeek() != DayOfWeek.SUNDAY) days.add(0, d);
            d = d.minusDays(1);
        }
        for (int i = 0; i < 20; i++) {
            for (int m = 0; m < 121; m++) {
                double hi = (m == 10) ? p + legs[i] : p + 0.5;
                bar(k, ms(days.get(i), 7, 0) + m * 60_000L, p, hi, p - 0.5, p);
            }
        }
        return k;
    }

    private static double[] legs(double base, double priorDayLeg) {
        double[] l = new double[20];
        java.util.Arrays.fill(l, base);
        l[19] = priorDayLeg;
        return l;
    }

    /** One no-wick bar per entry of closes: bar i opens at the previous close (bar 0 at open0). */
    private static void today(ArrayNode k, double open0, double[] closes) {
        long t0 = ms(TODAY, 7, 0);
        double prev = open0;
        for (int i = 0; i < closes.length; i++) {
            double o = prev, c = closes[i];
            bar(k, t0 + i * 60_000L, o, Math.max(o, c), Math.min(o, c), c);
            prev = c;
        }
    }

    private static double[] up30DownTo(double start, double top, double end, int downBars) {
        // bars 0..30 close start+i until top, then downBars bars falling 1 per bar to end
        int up = (int) (top - start);
        double[] c = new double[up + 1 + downBars];
        for (int i = 0; i <= up; i++) c[i] = start + i;
        for (int j = 1; j <= downBars; j++) c[up + j] = top - j;
        assertEquals(end, c[c.length - 1], 0.0);
        return c;
    }

    private static ObjectNode detect(ArrayNode k) {
        return SpikeFadeDetector.detect(M, M.createObjectNode(), k, "balance", "BTCUSDT");
    }

    @Test
    void caseA_a_normal_fade_fires_with_hand_numbers() {
        ArrayNode k = prior(1000.0, legs(5.0, 20.0));
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        ObjectNode c = detect(k);
        assertNotNull(c, "idea A-C1 + A-C2 hold: must fire");
        assertEquals("fade_short", c.get("setup_type").asText());
        assertEquals(1040.0, c.get("zone").get("price").asDouble(), 0.0);
        assertEquals(1044.16, c.get("math").get("stop").asDouble(), 0.0);
        assertEquals("A-S2", c.get("stop_rule").asText());
        assertEquals(1010.0, c.get("math").get("target").asDouble(), 0.0);
        assertEquals(7.21, c.get("math").get("gross_rr").asDouble(), 0.0);
        assertEquals(5.57, c.get("math").get("net_rr").asDouble(), 0.0);
        assertTrue(c.get("math").get("rr_sanity").asBoolean(), "gross 7.21 >= 1.5");
        assertTrue(c.get("math").get("net_rr_sanity").asBoolean(), "5.57 >= floor 1.25");
        assertEquals(1.0, c.get("impulse_rank").asDouble(), 0.0);
        assertEquals(2.9703, c.get("impulse_leg_pct").asDouble(), 0.0);
        assertEquals(10, c.get("bars_since_zone").asInt());
        assertEquals(10.0, c.get("price_left_zone_points").asDouble(), 0.0);
        assertEquals(ms(TODAY, 7, 30), c.get("zone_time_ms").asLong());
        assertEquals(0.97, c.get("math").get("distance_pct").asDouble(), 0.0);
        assertEquals(4.0, c.get("stop_n5").asDouble(), 1e-3, "4.16/1040*100 / 0.1 (N5 = 1/1000 of price)");
        List<String> proofs = new ArrayList<>();
        for (JsonNode p : c.get("proofs")) proofs.add(p.asText());
        assertEquals(List.of("A-P5"), proofs, "P2 tie 1.0 vs 1.0 is not 'above'; P4/P7 absent; P5 1040 > 1020");
        assertEquals("other", c.get("day_type").asText());
        assertEquals("unknown", c.get("htf_bias").asText());
    }

    /** Today: bars 0..9 flat 1000, bar 10 (07:10, same clock as the prior leg bars) o 1000 h hi l lo c close, bar 11 flat at close. */
    private static ArrayNode todayShort(ArrayNode k, double hi, double lo, double close) {
        long t0 = ms(TODAY, 7, 0);
        for (int i = 0; i < 10; i++) bar(k, t0 + i * 60_000L, 1000, 1000, 1000, 1000);
        bar(k, t0 + 10 * 60_000L, 1000, hi, lo, close);
        bar(k, t0 + 11 * 60_000L, close, close, close, close);
        return k;
    }

    /**
     * Case B (A-C1 gate is strict). Prior baseline 900, all 20 legs 4.5 = 0.5 % (same clock up to 07:11 includes the
     * leg bar at 07:10) -> median 0.5 %, prior high 904.5. Today open 1000, high 1005 -> leg 5/1000 = 0.5 %:
     * NOT above the median -> no candidate. Same series with high 1005.5 -> leg 0.55 % > 0.5 % -> fires:
     * A-C2 1004 > 904.5, stop 1005.5 * 1.004 = 1009.522 -> 1009.52 (A-S2 BTC, OURS 0.40 %), target 1000, risk 4.022,
     * reward 5.5, gross 5.5/4.022 = 1.3675.
     */
    @Test
    void caseB_leg_equal_to_median_does_not_fire_just_above_does() {
        assertNull(detect(todayShort(prior(900.0, legs(4.5, 4.5)), 1005.0, 1000.0, 1004.0)),
                "leg 0.5 % == median 0.5 %: the gate is strictly above");
        ObjectNode c = detect(todayShort(prior(900.0, legs(4.5, 4.5)), 1005.5, 1000.0, 1004.0));
        assertNotNull(c, "leg 0.55 % > median 0.5 %");
        assertEquals(1009.52, c.get("math").get("stop").asDouble(), 0.0);
        assertEquals(1000.0, c.get("math").get("target").asDouble(), 0.0);
        assertEquals(1.3675, c.get("math").get("gross_rr").asDouble(), 0.006);
        assertEquals(1.0, c.get("impulse_rank").asDouble(), 0.0);
    }

    /** Case C (A-C2 is strict): last close equal to the prior day's high (904.5) -> none; 904.6 -> fires. */
    @Test
    void caseC_c2_above_prior_day_is_recorded_not_gated() {
        ObjectNode eq = detect(todayShort(prior(900.0, legs(4.5, 4.5)), 1005.5, 904.5, 904.5));
        assertNotNull(eq, "close 904.5 == prior day high 904.5 still fires (A-C2 is a caveat)");
        assertFalse(eq.get("c2_above_prior_day").asBoolean());
        ObjectNode up = detect(todayShort(prior(900.0, legs(4.5, 4.5)), 1005.5, 904.5, 904.6));
        assertNotNull(up, "close 904.6 > 904.5");
        assertTrue(up.get("c2_above_prior_day").asBoolean());
        boolean hasC2 = false;
        for (JsonNode cd : up.get("conditions")) if ("A-C2".equals(cd.asText())) hasC2 = true;
        assertTrue(hasC2, "A-C2 listed when c2 true");
    }


    /**
     * Case D (A-S1): one prior session (index 5) has leg 70 -> high 1070, above today's 1040. It is the only prior high
     * above the zone, so stop = 1070 (A-S1, no buffer). reward 30, risk 30, gross 1.0,
     * net = (30 - 1.04) / (30 + 1.04) = 28.96 / 31.04 = 0.9330 -> 0.93; below the floor 1.25. A-P5 is absent (1040 < 1070).
     */
    @Test
    void caseD_stop_is_nearest_prior_high_above_the_zone() {
        double[] l = legs(5.0, 20.0);
        l[5] = 70.0;
        ArrayNode k = prior(1000.0, l);
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        ObjectNode c = detect(k);
        assertNotNull(c);
        assertEquals("A-S1", c.get("stop_rule").asText());
        assertEquals(1070.0, c.get("math").get("stop").asDouble(), 0.0);
        assertEquals(1.0, c.get("math").get("gross_rr").asDouble(), 0.0);
        assertEquals(0.93, c.get("math").get("net_rr").asDouble(), 0.0);
        assertFalse(c.get("math").get("net_rr_sanity").asBoolean());
        assertFalse(c.get("math").get("rr_sanity").asBoolean());
        for (JsonNode p : c.get("proofs")) assertNotEquals("A-P5", p.asText());
    }

    /**
     * Case F (A-S1 proxy cap, OURS 3 %): the only prior high above the zone is 1100, 60 above the 1040 zone
     * (5.77 %), beyond the cap, so it is ignored and A-S2 applies: stop 1044.16, risk 4.16, reward 30, gross 7.21.
     * A prior high at 1070 (2.88 %) stays within the cap (case D).
     */
    @Test
    void caseF_far_non_proxy_prior_high_beyond_cap_is_ignored() {
        double[] l = legs(5.0, 20.0);
        l[5] = 100.0;
        ArrayNode k = prior(1000.0, l);
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        ObjectNode c = detect(k);
        assertNotNull(c);
        assertEquals("A-S2", c.get("stop_rule").asText());
        assertEquals(1044.16, c.get("math").get("stop").asDouble(), 0.0);
        assertEquals(7.21, c.get("math").get("gross_rr").asDouble(), 0.0);
    }

    /**
     * Case G (proxy cap, audit CRITICAL_24H Finding 2): the prior-day high proxy itself (session index 19) is 1100, 5.77 %
     * above the 1040 zone, beyond the OURS 3 % cap. The proxy is untrustworthy, so no candidate (null), never the
     * unscaled high + 20 A-S2 stop. A far high on any other prior day stays ignored (case F).
     */
    @Test
    void caseG_prior_day_high_proxy_beyond_cap_returns_null() {
        double[] l = legs(5.0, 100.0);
        ArrayNode k = prior(1000.0, l);
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        assertNull(detect(k), "proxy 1100 is 5.77 % above the zone: fail closed, no high+20 stop");
    }


    /** Like todayShort but bar 10 carries volume v10 (the other bars 10); closes at close. */
    private static ArrayNode todayVol(ArrayNode k, double hi, double close, double v10) {
        long t0 = ms(TODAY, 7, 0);
        for (int i = 0; i < 10; i++) bar(k, t0 + i * 60_000L, 1000, 1000, 1000, 1000);
        k.addArray().add(t0 + 10 * 60_000L).add(1000.0).add(hi).add(1000.0).add(close).add(v10);
        bar(k, t0 + 11 * 60_000L, close, close, close, close);
        return k;
    }

    /**
     * Case H (A-C3 price arm, TLV2:61, k0zm5NYn0IQ:357-360; ratio 0.5 is OURS, thin has NO-SOURCE). Session leg 1000 -> 1005.5,
     * 30 rows of 0.1833: bars 0..9 close 1000 -> row 0 holds 100 (the POC); bar 10 closes 1004 -> row 21.
     * Volume above the POC row = bar 10's volume. 90 / 100 = 0.9 > 0.5: volume above the VPOC, no candidate.
     * 10 / 100 = 0.1 and exactly 50 / 100 = 0.5 pass (strictly above rejects); A-C3 then leaves not_in_data.
     */
    @Test
    void caseH_volume_above_session_vpoc_rejects_price_arm() {
        assertNull(detect(todayVol(prior(900.0, legs(4.5, 4.5)), 1005.5, 1004.0, 90.0)),
                "0.9 of the POC volume sits above the VPOC: A-C3 fails");
        ObjectNode thin = detect(todayVol(prior(900.0, legs(4.5, 4.5)), 1005.5, 1004.0, 10.0));
        assertNotNull(thin, "0.1 of the POC volume above: thin top");
        assertEquals(0.1, thin.get("c3_above_poc_ratio").asDouble(), 1e-9);
        List<String> nid = new ArrayList<>();
        for (JsonNode x : thin.get("not_in_data")) nid.add(x.asText());
        assertFalse(nid.contains("A-C3"), "A-C3 is checked now");
        List<String> cond = new ArrayList<>();
        for (JsonNode x : thin.get("conditions")) cond.add(x.asText());
        assertTrue(cond.contains("A-C3"));
        assertNotNull(detect(todayVol(prior(900.0, legs(4.5, 4.5)), 1005.5, 1004.0, 50.0)), "ratio 0.5 is not above 0.5");
    }

    /** Case I (A-C3 NOT_IN_DATA): a series without volume is not gated and keeps A-C3 listed. */
    @Test
    void caseI_no_volume_keeps_a_c3_not_in_data() {
        ArrayNode k = prior(900.0, legs(4.5, 4.5));
        long t0 = ms(TODAY, 7, 0);
        for (int i = 0; i < 10; i++) k.addArray().add(t0 + i * 60_000L).add(1000.0).add(1000.0).add(1000.0).add(1000.0);
        k.addArray().add(t0 + 10 * 60_000L).add(1000.0).add(1005.5).add(1000.0).add(1004.0);
        k.addArray().add(t0 + 11 * 60_000L).add(1004.0).add(1004.0).add(1004.0).add(1004.0);
        ObjectNode c = detect(k);
        assertNotNull(c);
        boolean listed = false;
        for (JsonNode x : c.get("not_in_data")) if ("A-C3".equals(x.asText())) listed = true;
        assertTrue(listed);
        assertFalse(c.has("c3_above_poc_ratio"));
    }

    /**
     * Case J (A-S2 per symbol, TLV2:94,323): GER40 keeps the fixed 20 points (stop 1060), BTCUSDT uses 0.40 % of the zone high
     * (1040 * 0.004 = 4.16, never 20 dollars), ETHUSDT likewise.
     */
    @Test
    void caseJ_a_s2_width_scales_per_symbol() {
        ArrayNode k = prior(1000.0, legs(5.0, 20.0));
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        ObjectNode btc = SpikeFadeDetector.detect(M, M.createObjectNode(), k, "balance", "BTCUSDT");
        assertEquals(1044.16, btc.get("math").get("stop").asDouble(), 0.0);
        ObjectNode eth = SpikeFadeDetector.detect(M, M.createObjectNode(), k, "balance", "ETHUSDT");
        assertEquals(1044.16, eth.get("math").get("stop").asDouble(), 0.0);
        ObjectNode dax = SpikeFadeDetector.detect(M, M.createObjectNode(), k, "balance", "GER40");
        assertEquals(1060.0, dax.get("math").get("stop").asDouble(), 0.0);
    }
    /** Case E (fail closed): fewer than 20 prior sessions -> no candidate even when the idea is plain. */
    @Test
    void caseE_short_history_fails_closed() {
        ArrayNode k = M.createArrayNode();
        today(k, 1010.0, up30DownTo(1010.0, 1040.0, 1030.0, 10));
        assertNull(detect(k));
    }
}
