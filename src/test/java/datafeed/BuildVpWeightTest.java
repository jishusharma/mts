package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * F-BT-09: buildVp must conserve volume. Each bar spreads exactly its own volume over its price points
 * (weights normalised per bar); before the fix a bar added about vol*n/2 and a single-bin bar with the typical
 * price above mid-range added nothing, so fast minutes outweighed quiet ones by up to 30x and the POC moved
 * 300-690 points away from the trade-level POC.
 */
public class BuildVpWeightTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static ArrayNode bar(long t, double h, double l, double c, double vol) {
        ArrayNode a = MAPPER.createArrayNode();
        a.add(t).add(c).add(h).add(l).add(c).add(vol).add(t + 59_999L).add(0.0).add(1).add(0.0);
        return a;
    }

    private static ObjectNode vp(List<JsonNode> bars, boolean hvns) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod("buildVp", List.class, boolean.class);
        m.setAccessible(true);
        return (ObjectNode) m.invoke(new MarketDataSnapshot(), bars, hvns);
    }

    /** 40 quiet bars carry 4000 of volume around 100; one wide bar carries 100 across 100..200. */
    @Test
    void wideBarDoesNotOutweighQuietHeavyVolume() throws Exception {
        List<JsonNode> bars = new ArrayList<>();
        long t = 1_700_000_000_000L;
        for (int i = 0; i < 40; i++) bars.add(bar(t + i * 60_000L, 100.10, 100.00, 100.05, 100.0));
        bars.add(bar(t + 40 * 60_000L, 200.0, 100.0, 150.0, 100.0));
        double poc = vp(bars, false).get("poc").asDouble();
        assertTrue(Math.abs(poc - 100.0) < 5.0, "POC must sit where the volume traded, got " + poc);
    }

    /** A single-bin bar whose typical price is above its low used to get weight 0: its volume vanished. */
    @Test
    void singleBinBarKeepsItsVolume() throws Exception {
        List<JsonNode> bars = new ArrayList<>();
        long t = 1_700_000_000_000L;
        // 30 bars at 100 (tp above the low, old weight 0) and 5 bars at 130 (zero range, old weight NaN -> dropped).
        for (int i = 0; i < 30; i++) bars.add(bar(t + i * 60_000L, 100.10, 100.00, 100.10, 10.0));
        for (int i = 0; i < 5; i++) bars.add(bar(t + (30 + i) * 60_000L, 130.0, 130.0, 130.0, 20.0));
        bars.add(bar(t + 40 * 60_000L, 150.0, 100.0, 125.0, 1.0));
        double poc = vp(bars, false).get("poc").asDouble();
        assertTrue(Math.abs(poc - 100.0) < 2.0, "300 volume at 100 beats 100 volume at 130, got " + poc);
    }

    @Test
    void zeroRangeBarIsFiniteNotNaN() throws Exception {
        List<JsonNode> bars = new ArrayList<>();
        long t = 1_700_000_000_000L;
        bars.add(bar(t, 100.0, 100.0, 100.0, 5.0));
        bars.add(bar(t + 60_000L, 110.0, 100.0, 105.0, 1.0));
        ObjectNode v = vp(bars, true);
        assertTrue(Double.isFinite(v.get("poc").asDouble()));
        assertEquals(100.0, v.get("poc").asDouble(), 1.0);
    }

    /** Acceptance from the escalation: POC within 50 of the trade-level POC on the two audited days. */
    @Test
    void realDaysPocMatchesTradeLevelProfile() throws Exception {
        assertDay("2026-10-06", 85_580.0);
        assertDay("2026-10-07", 83_400.0);
    }

    private static void assertDay(String day, double tradeLevelPoc) throws Exception {
        Path f = null;
        for (String root : new String[]{"Dumps", "../BinanceDataFeed/Dumps", "C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps"}) {
            Path p = Paths.get(root, "backtest", "raw", "klines", "BTCUSDT-1m-" + day + ".csv");
            if (Files.exists(p)) { f = p; break; }
        }
        Assumptions.assumeTrue(f != null, "1m kline file for " + day + " not on this machine");
        List<JsonNode> bars = new ArrayList<>();
        List<String> lines = Files.readAllLines(f);
        for (int i = 1; i < lines.size(); i++) {
            String[] c = lines.get(i).split(",");
            bars.add(bar(Long.parseLong(c[0]), Double.parseDouble(c[2]), Double.parseDouble(c[3]),
                    Double.parseDouble(c[4]), Double.parseDouble(c[5])));
        }
        double poc = vp(bars, false).get("poc").asDouble();
        assertTrue(Math.abs(poc - tradeLevelPoc) <= 50.0, day + " POC " + poc + " vs trade-level " + tradeLevelPoc);
    }
}
