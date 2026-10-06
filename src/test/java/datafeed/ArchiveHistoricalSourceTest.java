package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

/** Archive-backed historical klines: aggregation, no look-ahead, and an offline MarketDataSnapshot(raw). */
public class ArchiveHistoricalSourceTest {
    static final long BASE = 1_700_006_400_000L; // 2023-11-15T00:00:00Z, multiple of 1h, 1d and 4h
    static final String HDR = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n";

    /** minute i: o=100+i, h=o+2, l=o-1, c=o+1, v=i+1, tbv=(i+1)/2 */
    static String row(long baseMs, int i) {
        double o = 100 + i;
        long t = baseMs + i * 60_000L;
        return t + "," + o + "," + (o + 2) + "," + (o - 1) + "," + (o + 1) + "," + (i + 1) + "," + (t + 59_999) + ","
                + (i + 1) * 10 + ",3," + ((i + 1) / 2.0) + "," + (i + 1) + ",0\n";
    }

    static Path archive(Path dir, int minutes, boolean header) throws Exception {
        Path k = dir.resolve("klines");
        Files.createDirectories(k);
        StringBuilder sb = new StringBuilder(header ? HDR : "");
        for (int i = 0; i < minutes; i++) sb.append(row(BASE, i));
        Files.writeString(k.resolve("BTCUSDT-1m-2023-11-15.csv"), sb.toString());
        return dir;
    }

    @Test
    void aggregatesTo5m(@TempDir Path d) throws Exception {
        ArchiveHistoricalSource a = new ArchiveHistoricalSource(archive(d, 120, true), "BTCUSDT");
        assertEquals(120, a.size());
        JsonNode k = a.klinesRange("BTCUSDT", "5m", BASE, BASE + 3_600_000L, 100);
        // minutes 0..4: o=100 h=max(o+2)=106 l=min(o-1)=99 c=104+1=105 v=1+2+3+4+5=15 tbv=7.5
        JsonNode b0 = k.get(0);
        assertEquals(BASE, b0.get(0).asLong());
        assertEquals(100.0, b0.get(1).asDouble(), 1e-9);
        assertEquals(106.0, b0.get(2).asDouble(), 1e-9);
        assertEquals(99.0, b0.get(3).asDouble(), 1e-9);
        assertEquals(105.0, b0.get(4).asDouble(), 1e-9);
        assertEquals(15.0, b0.get(5).asDouble(), 1e-9);
        assertEquals(BASE + 300_000L - 1, b0.get(6).asLong());
        assertEquals(150.0, b0.get(7).asDouble(), 1e-9);
        assertEquals(15, b0.get(8).asInt());
        assertEquals(7.5, b0.get(9).asDouble(), 1e-9);
        // second bar: minutes 5..9, v = 6+..+10 = 40, tbv 20
        assertEquals(40.0, k.get(1).get(5).asDouble(), 1e-9);
        assertEquals(20.0, k.get(1).get(9).asDouble(), 1e-9);
    }

    @Test
    void aggregatesTo1hAndDropsFormingBar(@TempDir Path d) throws Exception {
        ArchiveHistoricalSource a = new ArchiveHistoricalSource(archive(d, 120, false), "BTCUSDT"); // headerless file
        // endMs = 01:30 -> hour 1 still forming; only hour 0 returned
        JsonNode k = a.klinesRange("BTCUSDT", "1h", BASE, BASE + 90 * 60_000L, 100);
        assertEquals(1, k.size());
        // minutes 0..59: h=161 l=99 c=160 v=sum(1..60)=1830 tbv=915
        assertEquals(100.0, k.get(0).get(1).asDouble(), 1e-9);
        assertEquals(161.0, k.get(0).get(2).asDouble(), 1e-9);
        assertEquals(99.0, k.get(0).get(3).asDouble(), 1e-9);
        assertEquals(160.0, k.get(0).get(4).asDouble(), 1e-9);
        assertEquals(1830.0, k.get(0).get(5).asDouble(), 1e-6);
        assertEquals(915.0, k.get(0).get(9).asDouble(), 1e-6);
    }

    @Test
    void neverReturnsBarClosingAfterEnd(@TempDir Path d) throws Exception {
        ArchiveHistoricalSource a = new ArchiveHistoricalSource(archive(d, 120, true), "BTCUSDT");
        long end = BASE + 10 * 60_000L; // as-of 00:10:00 -> last complete 1m bar opens 00:09
        JsonNode k1 = a.klinesRange("BTCUSDT", "1m", BASE, end, 1000);
        assertEquals(10, k1.size());
        for (String iv : new String[]{"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"}) {
            JsonNode k = a.klinesRange("BTCUSDT", iv, BASE - 86_400_000L, end, 1000);
            for (JsonNode b : k) assertTrue(b.get(6).asLong() <= end, iv + " bar closes after endMs");
        }
        // end one ms before the last bar close drops that bar
        assertEquals(9, a.klinesRange("BTCUSDT", "1m", BASE, end - 60_001L, 1000).size());
    }

    @Test
    void limitAndStartRespected(@TempDir Path d) throws Exception {
        ArchiveHistoricalSource a = new ArchiveHistoricalSource(archive(d, 120, true), "BTCUSDT");
        JsonNode k = a.klinesRange("BTCUSDT", "1m", BASE + 30 * 60_000L, BASE + 120 * 60_000L, 5);
        assertEquals(5, k.size());
        assertEquals(BASE + 30 * 60_000L, k.get(0).get(0).asLong());
    }

    @Test
    void marketDataSnapshotArchiveModeIsOffline(@TempDir Path d) throws Exception {
        // 3 days of 1m bars so the 1m/1h/4h/1d look-backs have data
        Path k = d.resolve("klines");
        Files.createDirectories(k);
        long start = BASE - 3 * 86_400_000L;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 4 * 1440; i++) {
            double o = 40_000 + 50 * Math.sin(i / 90.0);
            long t = start + i * 60_000L;
            sb.append(t).append(',').append(o).append(',').append(o + 5).append(',').append(o - 5).append(',')
              .append(o + 1).append(',').append(10 + i % 7).append(',').append(t + 59_999).append(',')
              .append(400000).append(',').append(50).append(',').append(5 + i % 3).append(',').append(200000).append(",0\n");
        }
        Files.writeString(k.resolve("BTCUSDT-1m-test.csv"), sb.toString());
        MarketDataSnapshot m = new MarketDataSnapshot(d);
        ObjectNode s = m.fetchHistoricalSnapshot("BTCUSDT", Instant.ofEpochMilli(BASE + 90_000_000L - 86_400_000L + 3_600_000L));
        assertNotNull(s);
        assertTrue(s.has("setup_candidates") || s.size() > 3, "snapshot should be populated");
    }
}
