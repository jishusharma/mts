package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Stream;

/**
 * Wave-1 item 4: replay the engine's snapshot path (MarketDataSnapshot.fetchHistoricalSnapshot, archive mode) at every 1m
 * bar of one UTC day. Built only in a %TEMP% copy of the class output; never touches src/ or the live tree.
 * Usage: ItemFourReplay rawRoot outCsv utcDate label     (flags: -Dmts.pitchfork=true [-Dmts.spikeFade=true])
 * One CSV row per bar (asOf = bar open + 1 min): candidates per family, rank-1 winner, and a family-A gate trace that
 * re-states the SpikeFadeDetector gates (window, high>open, 20 prior sessions, A-C1 leg>median, A-C2 close>prior high,
 * risk/reward) so a "no fire" has a named blocker. The trace is a diagnostic only; the engine's own output is the answer.
 */
public class ItemFourReplay {
    static final String SYMBOL = "BTCUSDT";
    static final char NL = (char) 10;

    static String family(JsonNode c) {
        String t = c.path("setup_type").asText();
        if ("fade_short".equals(t)) {
            if ("profile".equals(c.path("arm").asText())) return "fadeA_profile";
            return "fadeA_" + c.path("entry_path").asText("A1");
        }
        if (t.startsWith("pitchfork") || t.startsWith("pf_")) return "pitchfork";
        return "core";
    }

    public static void main(String[] a) throws Exception {
        Path raw = Paths.get(a[0]);
        LocalDate day = LocalDate.parse(a[2]);
        String label = a[3];
        long d0 = day.atStartOfDay(java.time.ZoneOffset.UTC).toInstant().toEpochMilli();
        long d1 = d0 + 86_400_000L;

        // whole series as primitives for the gate trace
        List<Path> files = new ArrayList<>();
        try (Stream<Path> st = Files.list(raw.resolve("klines"))) {
            st.filter(p -> p.getFileName().toString().startsWith(SYMBOL + "-1m-") && p.toString().endsWith(".csv")).sorted().forEach(files::add);
        }
        TreeMap<Long, double[]> m = new TreeMap<>();
        for (Path p : files) {
            try (BufferedReader r = Files.newBufferedReader(p, StandardCharsets.UTF_8)) {
                String ln;
                while ((ln = r.readLine()) != null) {
                    ln = ln.trim();
                    if (ln.isEmpty() || !Character.isDigit(ln.charAt(0))) continue;
                    String[] f = ln.split(",");
                    m.putIfAbsent(Long.parseLong(f[0]), new double[]{Double.parseDouble(f[1]), Double.parseDouble(f[2]), Double.parseDouble(f[3]), Double.parseDouble(f[4])});
                }
            }
        }
        int n = m.size();
        long[] t = new long[n];
        double[] o = new double[n], h = new double[n], l = new double[n], c = new double[n];
        int k = 0;
        for (Map.Entry<Long, double[]> e : m.entrySet()) {
            t[k] = e.getKey(); o[k] = e.getValue()[0]; h[k] = e.getValue()[1]; l[k] = e.getValue()[2]; c[k] = e.getValue()[3]; k++;
        }
        SpikeFadeDetector.Bars full = new SpikeFadeDetector.Bars(t, o, h, l, c);
        long span = MarketDataSnapshot.FADE_SERIES_DAYS * 86_400_000L;

        MarketDataSnapshot mds = new MarketDataSnapshot(raw);
        boolean fadeOn = SpikeFadeDetector.enabled(), pfOn = PitchforkSignalLayer.enabled();
        int from = 0;
        int rows = 0, errs = 0;
        try (BufferedWriter w = Files.newBufferedWriter(Paths.get(a[1]), StandardCharsets.UTF_8)) {
            w.write("label,bar_open_utc,close,high,core_n,fadeA1_n,fadeA2_n,fadeA3_n,fadeProfile_n,pitchfork_n,total_n,winner_family,winner_type,winner_dir,winner_zone,winner_score_raw,winner_net_rr,core_rank1_type,core_rank1_zone,core_rank1_score,core_rank1_proofs,core_rank1_conf_bonus,all_candidates,fade_gate,legPct,legMedian,priorDayHigh,sessHigh,sessOpen" + NL);
            for (int i = 0; i < n; i++) {
                if (t[i] < d0 || t[i] >= d1) continue;
                long asOf = t[i] + 60_000L;
                ObjectNode s;
                try {
                    s = mds.fetchHistoricalSnapshot(SYMBOL, Instant.ofEpochMilli(asOf));
                } catch (Exception ex) {
                    errs++;
                    System.err.println("err " + Instant.ofEpochMilli(asOf) + " " + ex);
                    continue;
                }
                JsonNode sc = s.get("setup_candidates");
                int core = 0, a1 = 0, a2 = 0, a3 = 0, prof = 0, pf = 0;
                StringBuilder all = new StringBuilder();
                JsonNode coreTop = null;
                for (JsonNode cd : sc) {
                    String fam = family(cd);
                    switch (fam) {
                        case "core": core++; if (coreTop == null) coreTop = cd; break;
                        case "fadeA_A1": a1++; break;
                        case "fadeA_A2": a2++; break;
                        case "fadeA_A3": a3++; break;
                        case "fadeA_profile": prof++; break;
                        default: pf++;
                    }
                    if (all.length() > 0) all.append(" ; ");
                    all.append(cd.path("rank").asInt()).append(':').append(fam).append('/').append(cd.path("setup_type").asText())
                       .append('/').append(cd.path("direction").asText()).append('@').append(cd.path("zone").path("price").asText())
                       .append(" sc=").append(cd.path("score").path("raw").asText());
                }
                JsonNode win = sc.size() > 0 ? sc.get(0) : null;

                // gate trace (diagnostic)
                while (from < i && full.t[from] < asOf - span) from++;
                SpikeFadeDetector.Bars b = new SpikeFadeDetector.Bars(full, from, i + 1);
                double[] st = new double[5];
                String gate = gate(b, st);

                w.write(String.join(",",
                    label, Instant.ofEpochMilli(t[i]).toString(), fmt(c[i]), fmt(h[i]),
                    "" + core, "" + a1, "" + a2, "" + a3, "" + prof, "" + pf, "" + sc.size(),
                    win == null ? "" : family(win), win == null ? "" : win.path("setup_type").asText(), win == null ? "" : win.path("direction").asText(),
                    win == null ? "" : win.path("zone").path("price").asText(), win == null ? "" : win.path("score").path("raw").asText(),
                    win == null ? "" : win.path("math").path("net_rr").asText(),
                    coreTop == null ? "" : coreTop.path("setup_type").asText(), coreTop == null ? "" : coreTop.path("zone").path("price").asText(),
                    coreTop == null ? "" : coreTop.path("score").path("raw").asText(), coreTop == null ? "" : coreTop.path("score").path("proof_count").asText(),
                    coreTop == null ? "" : coreTop.path("score").path("confluence_bonus").asText(),
                    "\"" + all + "\"", gate, fmt(st[0]), fmt(st[1]), fmt(st[2]), fmt(st[3]), fmt(st[4])));
                w.write(NL);
                rows++;
            }
        }
        System.out.println(label + " rows=" + rows + " errs=" + errs + " fadeOn=" + fadeOn + " pitchforkOn=" + pfOn);
    }

    static String fmt(double v) { return Double.isNaN(v) ? "" : (v == Math.rint(v) ? String.format("%.1f", v) : String.format("%.4f", v)); }

    /** Re-states SpikeFadeDetector.detect gates in order; returns the first blocker or PASS. st = {legPct, median, priorHigh, sessHigh, sessOpen}. */
    static String gate(SpikeFadeDetector.Bars b, double[] st) {
        Arrays.fill(st, Double.NaN);
        if (b.n < 2) return "TOO_FEW_BARS";
        int last = b.n - 1;
        LocalDate today = b.date[last];
        if (!b.inWindow(last)) return "G0_OUT_OF_WINDOW(07:00-17:35 Berlin)";
        TreeMap<LocalDate, List<Integer>> byDate = new TreeMap<>();
        for (int i = 0; i < b.n; i++) byDate.computeIfAbsent(b.date[i], d -> new ArrayList<>()).add(i);
        int winFirst = -1;
        double high = Double.NEGATIVE_INFINITY;
        for (int i : byDate.get(today)) {
            if (!b.inWindow(i)) continue;
            if (winFirst < 0) winFirst = i;
            if (b.h[i] > high) high = b.h[i];
        }
        if (winFirst < 0) return "G0_NO_WINDOW_BAR_TODAY";
        double open = b.o[winFirst];
        st[3] = high; st[4] = open;
        if (!(high > open)) return "G1_HIGH_NOT_ABOVE_OPEN";
        List<LocalDate> prior = new ArrayList<>();
        List<LocalDate> keys = new ArrayList<>(byDate.headMap(today).keySet());
        Collections.reverse(keys);
        for (LocalDate d : keys) {
            boolean hw = false;
            for (int i : byDate.get(d)) if (b.inWindow(i)) { hw = true; break; }
            if (hw) prior.add(0, d);
            if (prior.size() == 20) break;
        }
        if (prior.size() < 20) return "G2_FEWER_THAN_20_PRIOR_SESSIONS";
        java.time.LocalTime clock = b.time[last];
        double[] legs = new double[20];
        double priorHigh = Double.NaN;
        for (int q = 0; q < 20; q++) {
            double pOpen = Double.NaN, pMax = Double.NEGATIVE_INFINITY, dMax = Double.NEGATIVE_INFINITY;
            for (int i : byDate.get(prior.get(q))) {
                if (b.h[i] > dMax) dMax = b.h[i];
                if (!b.inWindow(i) || b.time[i].isAfter(clock)) continue;
                if (Double.isNaN(pOpen)) pOpen = b.o[i];
                if (b.h[i] > pMax) pMax = b.h[i];
            }
            if (Double.isNaN(pOpen)) return "G2_NO_SAME_CLOCK_BARS_ON_PRIOR_SESSION";
            legs[q] = (pMax - pOpen) / pOpen * 100.0;
            if (q == 19) priorHigh = dMax;
        }
        double leg = (high - open) / open * 100.0;
        double[] so = legs.clone();
        Arrays.sort(so);
        double med = (so[9] + so[10]) / 2.0;
        st[0] = leg; st[1] = med; st[2] = priorHigh;
        if (!(leg > med)) return "G3_A-C1_LEG_NOT_ABOVE_MEDIAN";
        // c4ad479e0: A-C2 is a recorded caveat, not a gate; detect() only fails closed on a proxy beyond the 3 % cap.
        if (priorHigh > high && (priorHigh - high) / high * 100.0 > 3.0) return "G4_PRIOR_DAY_HIGH_PROXY_BEYOND_CAP";
        return "G5_PASS(A1 fires if risk/reward>0)";
    }
}
