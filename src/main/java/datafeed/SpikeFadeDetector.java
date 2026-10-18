package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.time.DayOfWeek;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Family A "imbalance fade", PRICE arm (MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md sections
 * 2, 12-15, card tom-encode-spike-fade). Candidate type {@code fade_short}, behind {@code -Dmts.spikeFade=true}
 * (default off; the caller never reaches this class with the flag off). Entry path A1 only (sell limit at the
 * session extreme); paths A2/A3, re-entry, profile and aggressor proofs are other cards.
 *
 * <p>Condition ids stay in the output: ideas A-C1 and A-C2 (range form) must hold, then every proof that holds from
 * OHLC alone is listed (A-P2, A-P4, A-P5, A-P7). Nothing is counted or thresholded on the proof list (spec 13:
 * the count is reported, k* is fixed by the recall card). Missing history is NOT_IN_DATA and fails closed.
 *
 * <p>Parameters that are not Tom's words (spec 11/13 labels): session window START 07:00 Berlin (OURS, the pre-market
 * label; window end 17:35 Berlin is the spec 13 time exit), lookback 20 sessions (RANK-DEFAULT), A-C1 gate = above the
 * median of the prior legs (RANK-DEFAULT), no buffer on an A-S1 level (buffer NO-SOURCE).
 */
final class SpikeFadeDetector {
    private SpikeFadeDetector() {}

    static final String FLAG = "mts.spikeFade";
    static final ZoneId BERLIN = ZoneId.of("Europe/Berlin");
    static final LocalTime WINDOW_START = LocalTime.of(7, 0);
    static final LocalTime WINDOW_END = LocalTime.of(17, 35);
    static final int LOOKBACK = 20;
    static final double A_S2_POINTS = 20.0;   // A-S2, k0zm5NYn0IQ:22-24
    private static final long FIVE_MIN_MS = 300_000L;

    static boolean enabled() {
        return Boolean.getBoolean(FLAG);
    }

    static final class Bars {
        final int n;
        final long[] t;
        final double[] o, h, l, c;
        final double[] v;   // volume (kline index 5); NaN when the series carries none -> profile items NOT_IN_DATA
        final LocalDate[] date;
        final LocalTime[] time;

        Bars(JsonNode k) {
            n = k.size();
            t = new long[n];
            o = new double[n];
            h = new double[n];
            l = new double[n];
            c = new double[n];
            v = new double[n];
            date = new LocalDate[n];
            time = new LocalTime[n];
            for (int i = 0; i < n; i++) {
                JsonNode b = k.get(i);
                v[i] = b.size() > 5 && b.get(5).isNumber() ? b.get(5).asDouble() : Double.NaN;
                t[i] = b.get(0).asLong();
                o[i] = b.get(1).asDouble();
                h[i] = b.get(2).asDouble();
                l[i] = b.get(3).asDouble();
                c[i] = b.get(4).asDouble();
                var z = Instant.ofEpochMilli(t[i]).atZone(BERLIN);
                date[i] = z.toLocalDate();
                time[i] = z.toLocalTime();
            }
        }

        /** Whole-archive series from primitive arrays (replay harness): date/time computed once. */
        Bars(long[] t, double[] o, double[] h, double[] l, double[] c) {
            n = t.length;
            this.t = t;
            this.o = o;
            this.h = h;
            this.l = l;
            this.c = c;
            v = new double[n];
            Arrays.fill(v, Double.NaN);
            date = new LocalDate[n];
            time = new LocalTime[n];
            for (int i = 0; i < n; i++) {
                var z = Instant.ofEpochMilli(t[i]).atZone(BERLIN);
                date[i] = z.toLocalDate();
                time[i] = z.toLocalTime();
            }
        }

        /** Bars [from, to) of a longer series: the same view detect() gets from a snapshot cut at to-1 (no look-ahead). */
        Bars(Bars full, int from, int to) {
            n = to - from;
            t = Arrays.copyOfRange(full.t, from, to);
            o = Arrays.copyOfRange(full.o, from, to);
            h = Arrays.copyOfRange(full.h, from, to);
            l = Arrays.copyOfRange(full.l, from, to);
            c = Arrays.copyOfRange(full.c, from, to);
            v = Arrays.copyOfRange(full.v, from, to);
            date = Arrays.copyOfRange(full.date, from, to);
            time = Arrays.copyOfRange(full.time, from, to);
        }

        boolean inWindow(int i) {
            return !time[i].isBefore(WINDOW_START) && !time[i].isAfter(WINDOW_END);
        }
    }

    /** @return the fade_short candidate node (rank not set), or null when nothing fires. */
    static ObjectNode detect(ObjectMapper mapper, ObjectNode root, JsonNode klines1m, String marketState, String sym) {
        if (klines1m == null || klines1m.size() < 2) return null;
        return detect(mapper, root, new Bars(klines1m), marketState, sym);
    }

    /** Same detector on a prepared series (card tom-v2-recall-fire-rate: replay slices, no JSON per minute). */
    static ObjectNode detect(ObjectMapper mapper, ObjectNode root, Bars b, String marketState, String sym) {
        if (b.n < 2) return null;
        int last = b.n - 1;
        LocalDate today = b.date[last];
        if (!b.inWindow(last)) return null;

        // dates present, in order; indices per date
        TreeMap<LocalDate, List<Integer>> byDate = new TreeMap<>();
        for (int i = 0; i < b.n; i++) byDate.computeIfAbsent(b.date[i], d -> new ArrayList<>()).add(i);

        // today's window: session open, running extreme
        int winFirst = -1, hIdx = -1;
        double high = Double.NEGATIVE_INFINITY;
        for (int i : byDate.get(today)) {
            if (!b.inWindow(i)) continue;
            if (winFirst < 0) winFirst = i;
            if (b.h[i] > high) { high = b.h[i]; hIdx = i; }
        }
        if (winFirst < 0) return null;
        double open = b.o[winFirst];
        double lastClose = b.c[last];
        if (!(high > open)) return null;

        // prior sessions: last LOOKBACK dates before today with a window bar
        List<LocalDate> prior = new ArrayList<>();
        for (LocalDate d : byDate.headMap(today).keySet().stream().sorted(java.util.Comparator.reverseOrder()).toArray(LocalDate[]::new)) {
            boolean hasWindow = false;
            for (int i : byDate.get(d)) if (b.inWindow(i)) { hasWindow = true; break; }
            if (hasWindow) prior.add(0, d);
            if (prior.size() == LOOKBACK) break;
        }
        if (prior.size() < LOOKBACK) return null;   // impulse_rank NOT_IN_DATA: fail closed

        // A-C1: leg to the extreme (% of session open), same clock window, ranked among the prior legs
        LocalTime clock = b.time[last];
        double[] legs = new double[LOOKBACK];
        double[] dayHigh = new double[LOOKBACK];
        for (int k = 0; k < LOOKBACK; k++) {
            double pOpen = Double.NaN, pMax = Double.NEGATIVE_INFINITY, dMax = Double.NEGATIVE_INFINITY;
            for (int i : byDate.get(prior.get(k))) {
                if (b.h[i] > dMax) dMax = b.h[i];
                if (!b.inWindow(i) || b.time[i].isAfter(clock)) continue;
                if (Double.isNaN(pOpen)) pOpen = b.o[i];
                if (b.h[i] > pMax) pMax = b.h[i];
            }
            if (Double.isNaN(pOpen) || pOpen <= 0) return null;   // no same-clock bars on a prior session: NOT_IN_DATA
            legs[k] = (pMax - pOpen) / pOpen * 100.0;
            dayHigh[k] = dMax;
        }
        double legPct = (high - open) / open * 100.0;
        double[] sorted = legs.clone();
        Arrays.sort(sorted);
        double median = (sorted[LOOKBACK / 2 - 1] + sorted[LOOKBACK / 2]) / 2.0;
        if (!(legPct > median)) return null;
        int below = 0;
        for (double v : legs) if (v < legPct) below++;
        double impulseRank = below / (double) LOOKBACK;

        // A-C2 (range form): price above the prior day's range
        double priorHigh = dayHigh[LOOKBACK - 1];
        if (!(lastClose > priorHigh)) return null;

        // stop: A-S1 nearest prior-session high above the zone, else A-S2 fixed 20 points
        double above = Double.POSITIVE_INFINITY, maxPrior = Double.NEGATIVE_INFINITY;
        for (double d : dayHigh) {
            if (d > high && d < above) above = d;
            if (d > maxPrior) maxPrior = d;
        }
        boolean s1 = above != Double.POSITIVE_INFINITY;
        double stop = s1 ? above : high + A_S2_POINTS;
        double target = open;   // A-T1: start of the impulse
        double risk = stop - high;
        double reward = high - target;
        if (!(risk > 0) || !(reward > 0)) return null;

        // proofs from OHLC (spec 12)
        List<String> proofs = new ArrayList<>();
        int barsSince = last - hIdx;
        int legBars = Math.max(1, hIdx - winFirst);
        if (barsSince >= 1 && (high - lastClose) > 0
                && (high - lastClose) / barsSince > (high - open) / legBars) proofs.add("A-P2");
        if (insideBarAtTop(b, byDate.get(today), winFirst, last, high)) proofs.add("A-P4");
        if (high > maxPrior) proofs.add("A-P5");
        for (int i = hIdx + 1; i <= last; i++) {
            if (b.inWindow(i) && b.date[i].equals(today) && b.l[i] < open) { proofs.add("A-P7"); break; }
        }

        double n5pct = n5Pct(b, byDate, prior);

        ObjectNode c = mapper.createObjectNode();
        c.put("setup_type", "fade_short");
        c.put("direction", "short");
        ObjectNode zone = c.putObject("zone");
        zone.put("name", "session_high");
        zone.put("price", Math.round(high * 100.0) / 100.0);
        zone.put("type", "session_high");
        ObjectNode math = c.putObject("math");
        math.put("distance_pct", Math.round(Math.abs(lastClose - high) / lastClose * 10000.0) / 100.0);
        math.put("stop", Math.round(stop * 100.0) / 100.0);
        math.put("target", Math.round(target * 100.0) / 100.0);
        math.put("runner_target", 0.0);
        double grossRR = reward / risk;
        double netRR = ExecutionMathConstants.netRR(sym, high, target, stop);
        double floor = NetRrFloor.read();
        math.put("gross_rr", Math.round(grossRR * 100.0) / 100.0);
        math.put("net_rr", Math.round(netRR * 100.0) / 100.0);
        math.put("rr_sanity", grossRR >= 1.5);
        math.put("net_rr_sanity", netRR >= floor);
        c.put("stop_rule", s1 ? "A-S1" : "A-S2");
        c.put("entry_path", "A1");
        var cond = c.putArray("conditions");
        cond.add("A-C1");
        cond.add("A-C2");
        var pr = c.putArray("proofs");
        proofs.forEach(pr::add);
        var nid = c.putArray("not_in_data");
        for (String s : new String[]{"A-C3", "A-C4", "A-P1", "A-P3", "A-P6", "A-P8", "A-P9", "A-P10"}) nid.add(s);
        c.put("zone_time_ms", b.t[hIdx]);
        c.put("bars_since_zone", barsSince);
        c.put("price_left_zone_points", Math.round((high - lastClose) * 100.0) / 100.0);
        c.put("proof_count", proofs.size());
        // spec 14 snapshot fields (selection-test inputs, never gates)
        c.put("market_state", marketState);
        c.put("day_type", dayType(b, byDate, prior.get(LOOKBACK - 1), today, open));
        c.put("htf_bias", htfBias(root, lastClose));
        c.put("impulse_rank", Math.round(impulseRank * 10000.0) / 10000.0);
        c.put("impulse_leg_pct", Math.round(legPct * 10000.0) / 10000.0);
        if (n5pct > 0) c.put("stop_n5", Math.round(risk / high * 100.0 / n5pct * 10000.0) / 10000.0);
        else c.putNull("stop_n5");
        ObjectNode score = c.putObject("score");
        score.put("raw", 0);
        score.put("confidence", "n/a");
        score.put("proof_count", proofs.size());
        score.put("confluence_bonus", 0);
        return c;
    }

    /** A-P4: the last completed 5-minute bar is inside the 5-minute bar that holds the session high. */
    private static boolean insideBarAtTop(Bars b, List<Integer> todayIdx, int winFirst, int last, double high) {
        long lastBucket = Math.floorDiv(b.t[last], FIVE_MIN_MS);
        boolean lastComplete = b.t[last] + 60_000L >= (lastBucket + 1) * FIVE_MIN_MS;
        TreeMap<Long, double[]> buckets = new TreeMap<>();   // bucket -> {high, low}
        for (int i : todayIdx) {
            if (i < winFirst || i > last || !b.inWindow(i)) continue;
            long bk = Math.floorDiv(b.t[i], FIVE_MIN_MS);
            double[] hl = buckets.get(bk);
            if (hl == null) buckets.put(bk, new double[]{b.h[i], b.l[i]});
            else { hl[0] = Math.max(hl[0], b.h[i]); hl[1] = Math.min(hl[1], b.l[i]); }
        }
        if (!lastComplete) buckets.remove(lastBucket);
        if (buckets.size() < 2) return false;
        Map.Entry<Long, double[]> cur = buckets.lastEntry();
        Map.Entry<Long, double[]> mother = buckets.lowerEntry(cur.getKey());
        if (mother == null) return false;
        double[] m = mother.getValue(), x = cur.getValue();
        return m[0] == high && x[0] <= m[0] && x[1] >= m[1];
    }

    /** N5 as % of close: median true range of completed 5-minute window bars of the prior sessions (FORMULAS section 12). */
    private static double n5Pct(Bars b, TreeMap<LocalDate, List<Integer>> byDate, List<LocalDate> prior) {
        List<Double> v = new ArrayList<>();
        for (LocalDate d : prior) {
            TreeMap<Long, double[]> buckets = new TreeMap<>();   // {high, low, close}
            for (int i : byDate.get(d)) {
                if (!b.inWindow(i)) continue;
                long bk = Math.floorDiv(b.t[i], FIVE_MIN_MS);
                double[] x = buckets.get(bk);
                if (x == null) buckets.put(bk, new double[]{b.h[i], b.l[i], b.c[i]});
                else { x[0] = Math.max(x[0], b.h[i]); x[1] = Math.min(x[1], b.l[i]); x[2] = b.c[i]; }
            }
            double prevClose = Double.NaN;
            for (double[] x : buckets.values()) {
                double tr = x[0] - x[1];
                if (!Double.isNaN(prevClose)) tr = Math.max(tr, Math.max(Math.abs(x[0] - prevClose), Math.abs(x[1] - prevClose)));
                if (x[2] > 0) v.add(tr / x[2] * 100.0);
                prevClose = x[2];
            }
        }
        if (v.isEmpty()) return Double.NaN;
        double[] a = v.stream().mapToDouble(Double::doubleValue).sorted().toArray();
        return a.length % 2 == 1 ? a[a.length / 2] : (a[a.length / 2 - 1] + a[a.length / 2]) / 2.0;
    }

    /** day_type: monday, gap_day (session open outside the prior day's full range), other. Selection field only. */
    private static String dayType(Bars b, TreeMap<LocalDate, List<Integer>> byDate, LocalDate priorDate, LocalDate today, double open) {
        if (today.getDayOfWeek() == DayOfWeek.MONDAY) return "monday";
        double hi = Double.NEGATIVE_INFINITY, lo = Double.POSITIVE_INFINITY;
        for (int i : byDate.get(priorDate)) { hi = Math.max(hi, b.h[i]); lo = Math.min(lo, b.l[i]); }
        return (open > hi || open < lo) ? "gap_day" : "other";
    }

    /** htf_bias: side of the prior week's value; the snapshot carries the prior week POC only. */
    private static String htfBias(ObjectNode root, double price) {
        JsonNode poc = root.path("weekly_vp").path("prior_week_poc");
        if (!poc.isNumber() || poc.asDouble() <= 0) return "unknown";
        return price > poc.asDouble() ? "above" : price < poc.asDouble() ? "below" : "at";
    }
}
