package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

/**
 * Card tom-v2-recall-fire-rate: replay SpikeFadeDetector (family A, PRICE arm) at every 1m bar of the given Berlin
 * dates, each call seeing exactly the bars a snapshot cut there would give the fade call: bars with open time in
 * [asOf - FADE_SERIES_DAYS, asOf), asOf = last bar open + 1 minute. Writes one JSON line per instant that fires.
 * Usage: FadeReplay rawRoot datesFile outJsonl shardIdx shardCnt   (datesFile: one YYYY-MM-DD Berlin date per line)
 * Built only in a temp copy by scripts of this card; -Dmts.symbol=GER40 -Dmts.spikeFade=true.
 */
public class FadeReplay {
    static final String SYMBOL = System.getProperty("mts.symbol", "GER40");

    public static void main(String[] a) throws Exception {
        System.setProperty("mts.spikeFade", "true");
        Path raw = Paths.get(a[0]);
        Set<LocalDate> dates = new HashSet<>();
        for (String s : Files.readAllLines(Paths.get(a[1]))) if (!s.isBlank()) dates.add(LocalDate.parse(s.trim()));
        int shard = Integer.parseInt(a[3]), shards = Integer.parseInt(a[4]);

        long[] t = new long[1 << 20];
        double[] o = new double[t.length], h = new double[t.length], l = new double[t.length], c = new double[t.length];
        int n = 0;
        List<Path> files = new ArrayList<>();
        try (Stream<Path> st = Files.list(raw.resolve("klines"))) {
            st.filter(p -> p.getFileName().toString().startsWith(SYMBOL + "-1m-") && p.toString().endsWith(".csv"))
                    .sorted().forEach(files::add);
        }
        for (Path p : files) {
            try (BufferedReader r = Files.newBufferedReader(p, StandardCharsets.UTF_8)) {
                String ln;
                while ((ln = r.readLine()) != null) {
                    ln = ln.trim();
                    if (ln.isEmpty() || !Character.isDigit(ln.charAt(0))) continue;
                    String[] f = ln.split(",");
                    long ot = Long.parseLong(f[0]);
                    if (n > 0 && ot <= t[n - 1]) continue;
                    if (n == t.length) {
                        t = Arrays.copyOf(t, n * 2); o = Arrays.copyOf(o, n * 2); h = Arrays.copyOf(h, n * 2);
                        l = Arrays.copyOf(l, n * 2); c = Arrays.copyOf(c, n * 2);
                    }
                    t[n] = ot; o[n] = Double.parseDouble(f[1]); h[n] = Double.parseDouble(f[2]);
                    l[n] = Double.parseDouble(f[3]); c[n] = Double.parseDouble(f[4]);
                    n++;
                }
            }
        }
        SpikeFadeDetector.Bars full = new SpikeFadeDetector.Bars(Arrays.copyOf(t, n), Arrays.copyOf(o, n),
                Arrays.copyOf(h, n), Arrays.copyOf(l, n), Arrays.copyOf(c, n));
        ObjectMapper om = new ObjectMapper();
        ObjectNode root = om.createObjectNode();
        long span = MarketDataSnapshot.FADE_SERIES_DAYS * 86_400_000L;
        long calls = 0, fires = 0;
        int from = 0;
        int dayIdx = 0;
        LocalDate prevDay = null;
        try (BufferedWriter w = Files.newBufferedWriter(Paths.get(a[2]), StandardCharsets.UTF_8)) {
            for (int i = 0; i < n; i++) {
                LocalDate d = full.date[i];
                if (!dates.contains(d) || !full.inWindow(i)) continue;
                if (!d.equals(prevDay)) { prevDay = d; dayIdx++; }
                if ((dayIdx % shards) != shard) continue;
                long asOf = full.t[i] + 60_000L;
                while (from < i && full.t[from] < asOf - span) from++;
                SpikeFadeDetector.Bars b = new SpikeFadeDetector.Bars(full, from, i + 1);
                ObjectNode cand = SpikeFadeDetector.detect(om, root, b, "n/a", SYMBOL);
                calls++;
                if (cand == null) continue;
                fires++;
                ObjectNode r = om.createObjectNode();
                r.put("date", d.toString());
                r.put("t", full.t[i]);
                r.put("close", full.c[i]);
                r.put("zone", cand.path("zone").path("price").asDouble());
                r.put("stop", cand.path("math").path("stop").asDouble());
                r.put("target", cand.path("math").path("target").asDouble());
                r.put("stop_rule", cand.path("stop_rule").asText());
                r.set("proofs", cand.get("proofs"));
                r.put("proof_count", cand.path("proof_count").asInt());
                r.put("bars_since_zone", cand.path("bars_since_zone").asInt());
                r.put("price_left_zone_points", cand.path("price_left_zone_points").asDouble());
                r.set("stop_n5", cand.get("stop_n5"));
                r.put("impulse_rank", cand.path("impulse_rank").asDouble());
                r.put("day_type", cand.path("day_type").asText());
                w.write(om.writeValueAsString(r));
                w.write('\n');
            }
        }
        System.out.println("shard " + shard + "/" + shards + " calls=" + calls + " fires=" + fires);
    }
}
