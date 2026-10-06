package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.BufferedReader;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

/**
 * Offline kline source built from the local Binance 1m archive: CSV files under {@code <raw>/klines}
 * (name {@code SYMBOL-1m-*.csv}; Binance column layout, header row optional, duplicates keep first).
 * 1m bars are loaded once into primitive arrays and aggregated on request to any supported interval, aligned to
 * UTC epoch boundaries (1w to Monday 00:00 UTC). A bar whose close time (open + interval - 1) is after endMs is
 * never returned, so there is no look-ahead. Thread-safe (immutable after construction).
 */
public class ArchiveHistoricalSource implements HistoricalSource {
    private static final long WEEK_OFFSET_MS = 4L * 86_400_000L; // epoch (Thu) -> first Monday
    private static final ObjectMapper MAPPER = new ObjectMapper();

    private final String symbol;
    private int n;
    private long[] t;
    private double[] o, h, l, c, v, qv, tbv, tbq;
    private int[] cnt;

    public ArchiveHistoricalSource(Path raw, String symbol) throws IOException {
        this.symbol = symbol;
        Path dir = raw.resolve("klines");
        if (!Files.isDirectory(dir)) throw new IOException("archive klines dir not found: " + dir);
        List<Path> files = new ArrayList<>();
        try (Stream<Path> s = Files.list(dir)) {
            s.filter(p -> p.getFileName().toString().endsWith(".csv")).sorted().forEach(files::add);
        }
        List<Path> mine = new ArrayList<>();
        String prefix = symbol + "-1m-";
        for (Path p : files) if (p.getFileName().toString().startsWith(prefix)) mine.add(p);
        if (mine.isEmpty()) throw new IOException("no " + prefix + "*.csv under " + dir);
        alloc(1 << 16);
        boolean sorted = true;
        for (Path p : mine) sorted &= load(p);
        if (!sorted) sortAndDedupe();
        if (n == 0) throw new IOException("no kline rows for " + symbol + " under " + dir);
    }

    /** A HistoricalSource over any symbol under raw, each symbol loaded lazily (once) on first use. */
    public static HistoricalSource lazy(Path raw) {
        Map<String, ArchiveHistoricalSource> cache = new HashMap<>();
        return (sym, iv, s, e, lim) -> {
            ArchiveHistoricalSource a;
            synchronized (cache) {
                a = cache.get(sym);
                if (a == null) { a = new ArchiveHistoricalSource(raw, sym); cache.put(sym, a); }
            }
            return a.klinesRange(sym, iv, s, e, lim);
        };
    }

    public int size() { return n; }
    public long firstOpenTime() { return t[0]; }
    public long lastOpenTime() { return t[n - 1]; }

    private void alloc(int cap) {
        t = new long[cap]; o = new double[cap]; h = new double[cap]; l = new double[cap]; c = new double[cap];
        v = new double[cap]; qv = new double[cap]; tbv = new double[cap]; tbq = new double[cap]; cnt = new int[cap];
    }

    private void grow() {
        int cap = t.length * 2;
        t = Arrays.copyOf(t, cap); o = Arrays.copyOf(o, cap); h = Arrays.copyOf(h, cap); l = Arrays.copyOf(l, cap);
        c = Arrays.copyOf(c, cap); v = Arrays.copyOf(v, cap); qv = Arrays.copyOf(qv, cap);
        tbv = Arrays.copyOf(tbv, cap); tbq = Arrays.copyOf(tbq, cap); cnt = Arrays.copyOf(cnt, cap);
    }

    /** Appends one file; returns false if the global order is no longer strictly increasing. */
    private boolean load(Path p) throws IOException {
        boolean sorted = true;
        try (BufferedReader r = Files.newBufferedReader(p, StandardCharsets.UTF_8)) {
            String line;
            while ((line = r.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || !Character.isDigit(line.charAt(0))) continue; // header / blank
                String[] f = line.split(",");
                if (f.length < 6) continue;
                if (n == t.length) grow();
                long ot = Long.parseLong(f[0]);
                if (n > 0 && ot <= t[n - 1]) sorted = false;
                t[n] = ot;
                o[n] = Double.parseDouble(f[1]); h[n] = Double.parseDouble(f[2]);
                l[n] = Double.parseDouble(f[3]); c[n] = Double.parseDouble(f[4]); v[n] = Double.parseDouble(f[5]);
                qv[n] = f.length > 7 ? Double.parseDouble(f[7]) : 0.0;
                cnt[n] = f.length > 8 ? Integer.parseInt(f[8]) : 0;
                tbv[n] = f.length > 9 ? Double.parseDouble(f[9]) : 0.0;
                tbq[n] = f.length > 10 ? Double.parseDouble(f[10]) : 0.0;
                n++;
            }
        }
        return sorted;
    }

    private void sortAndDedupe() {
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        Arrays.sort(idx, Comparator.comparingLong((Integer i) -> t[i])); // stable: first occurrence wins
        long[] t2 = new long[n];
        double[] o2 = new double[n], h2 = new double[n], l2 = new double[n], c2 = new double[n],
                v2 = new double[n], qv2 = new double[n], tbv2 = new double[n], tbq2 = new double[n];
        int[] cnt2 = new int[n];
        int m = 0;
        for (int k = 0; k < n; k++) {
            int i = idx[k];
            if (m > 0 && t[i] == t2[m - 1]) continue;
            t2[m] = t[i]; o2[m] = o[i]; h2[m] = h[i]; l2[m] = l[i]; c2[m] = c[i]; v2[m] = v[i];
            qv2[m] = qv[i]; tbv2[m] = tbv[i]; tbq2[m] = tbq[i]; cnt2[m] = cnt[i]; m++;
        }
        t = t2; o = o2; h = h2; l = l2; c = c2; v = v2; qv = qv2; tbv = tbv2; tbq = tbq2; cnt = cnt2; n = m;
    }

    static long intervalMs(String iv) {
        switch (iv) {
            case "1m": return 60_000L;
            case "3m": return 180_000L;
            case "5m": return 300_000L;
            case "15m": return 900_000L;
            case "30m": return 1_800_000L;
            case "1h": return 3_600_000L;
            case "2h": return 7_200_000L;
            case "4h": return 14_400_000L;
            case "1d": return 86_400_000L;
            case "1w": return 7L * 86_400_000L;
            default: throw new IllegalArgumentException("unsupported interval " + iv);
        }
    }

    private int lowerBound(long x) { // first index with t >= x
        int lo = 0, hi = n;
        while (lo < hi) { int mid = (lo + hi) >>> 1; if (t[mid] < x) lo = mid + 1; else hi = mid; }
        return lo;
    }

    @Override
    public JsonNode klinesRange(String sym, String interval, long startMs, long endMs, int limit) throws IOException {
        if (!symbol.equals(sym)) throw new IOException("archive source is for " + symbol + ", not " + sym);
        long dur = intervalMs(interval);
        long off = interval.equals("1w") ? WEEK_OFFSET_MS : 0L;
        ArrayNode out = MAPPER.createArrayNode();
        long b = Math.floorDiv(startMs - off, dur) * dur + off; // first bucket whose open >= startMs
        if (b < startMs) b += dur;
        int i = lowerBound(b);
        while (i < n && out.size() < limit) {
            long bs = Math.floorDiv(t[i] - off, dur) * dur + off;
            if (bs + dur - 1 > endMs) break; // forming / future bar: never returned
            int j = i;
            double hi = h[i], lo = l[i], sv = 0, sq = 0, stv = 0, stq = 0;
            int sc = 0;
            while (j < n && t[j] < bs + dur) {
                if (h[j] > hi) hi = h[j];
                if (l[j] < lo) lo = l[j];
                sv += v[j]; sq += qv[j]; stv += tbv[j]; stq += tbq[j]; sc += cnt[j];
                j++;
            }
            ArrayNode row = out.addArray();
            row.add(bs);
            row.add(str(o[i])); row.add(str(hi)); row.add(str(lo)); row.add(str(c[j - 1])); row.add(str(sv));
            row.add(bs + dur - 1);
            row.add(str(sq)); row.add(sc); row.add(str(stv)); row.add(str(stq)); row.add("0");
            i = j;
        }
        return out;
    }

    private static String str(double d) { return BigDecimal.valueOf(d).toPlainString(); }
}
