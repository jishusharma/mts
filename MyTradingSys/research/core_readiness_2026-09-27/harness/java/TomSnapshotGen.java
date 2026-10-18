package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.YearMonth;
import java.time.ZoneOffset;
import java.util.zip.GZIPOutputStream;

/**
 * Offline generator: historical Tom snapshots from the 1m archive (ArchiveHistoricalSource), no network.
 * Built only in a %TEMP% copy (see README_REPLAY.md pattern). Usage:
 *   TomSnapshotGen rawRoot outDir startIso endIso stepMin shardIdx shardCnt
 * Months are dealt round-robin to shards. Output: outDir/YYYY-MM.jsonl.gz (compact JSON, one snapshot per
 * line, only snapshots with >=1 setup candidate) + outDir/YYYY-MM.meta.json (evaluated/kept/errors counts).
 */
public class TomSnapshotGen {
    /** Symbol to replay: -Dmts.symbol=GER40 for the DAX probe (archive file prefix); default BTCUSDT. */
    static final String SYMBOL = System.getProperty("mts.symbol", "BTCUSDT");

    public static void main(String[] a) throws Exception {
        Path raw = Paths.get(a[0]);
        Path out = Paths.get(a[1]);
        Instant start = Instant.parse(a[2]);
        Instant end = Instant.parse(a[3]);
        long stepMs = Long.parseLong(a[4]) * 60_000L;
        int shard = Integer.parseInt(a[5]);
        int shards = Integer.parseInt(a[6]);
        Files.createDirectories(out);
        ObjectMapper om = new ObjectMapper(); // compact
        ArchiveHistoricalSource probe = new ArchiveHistoricalSource(raw, SYMBOL);
        System.out.println("archive bars=" + probe.size() + " first=" + Instant.ofEpochMilli(probe.firstOpenTime())
                + " last=" + Instant.ofEpochMilli(probe.lastOpenTime()));
        MarketDataSnapshot mds = new MarketDataSnapshot(raw);
        long lastAsOf = Math.min(end.toEpochMilli(), probe.lastOpenTime() + 60_000L);
        YearMonth ym = YearMonth.from(start.atZone(ZoneOffset.UTC));
        YearMonth endYm = YearMonth.from(Instant.ofEpochMilli(lastAsOf).atZone(ZoneOffset.UTC));
        int mi = 0;
        for (; !ym.isAfter(endYm); ym = ym.plusMonths(1), mi++) {
            if (mi % shards != shard) continue;
            Path f = out.resolve(ym + ".jsonl.gz");
            Path meta = out.resolve(ym + ".meta.json");
            if (Files.exists(meta)) { System.out.println("skip " + ym); continue; }
            long m0 = Math.max(start.toEpochMilli(), ym.atDay(1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli());
            long m1 = Math.min(lastAsOf, ym.plusMonths(1).atDay(1).atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli() - 1);
            // align to step grid anchored at start
            long t = start.toEpochMilli() + ((m0 - start.toEpochMilli() + stepMs - 1) / stepMs) * stepMs;
            long eval = 0, kept = 0, err = 0, firstT = -1, lastT = -1;
            Path tmp = out.resolve(ym + ".jsonl.gz.part");
            try (BufferedWriter w = new BufferedWriter(new OutputStreamWriter(
                    new GZIPOutputStream(Files.newOutputStream(tmp)), StandardCharsets.UTF_8), 1 << 16)) {
                for (; t <= m1; t += stepMs) {
                    eval++;
                    if (firstT < 0) firstT = t;
                    lastT = t;
                    try {
                        ObjectNode s = mds.fetchHistoricalSnapshot(SYMBOL, Instant.ofEpochMilli(t));
                        s.remove("module_candidates");
                        if (s.get("setup_candidates") != null && s.get("setup_candidates").size() > 0) {
                            w.write(om.writeValueAsString(s));
                            w.write('\n');
                            kept++;
                        }
                    } catch (Exception e) {
                        err++;
                        if (err <= 3) System.err.println("err " + Instant.ofEpochMilli(t) + " " + e);
                    }
                }
            }
            Files.move(tmp, f, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            Files.writeString(meta, "{\"month\":\"" + ym + "\",\"step_min\":" + (stepMs / 60000) + ",\"evaluated\":" + eval
                    + ",\"kept\":" + kept + ",\"errors\":" + err
                    + ",\"first_ms\":" + firstT + ",\"last_ms\":" + lastT + "}\n");
            System.out.println(ym + " eval=" + eval + " kept=" + kept + " err=" + err);
        }
    }
}
