package datafeed;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** B075 / D1-L0: the historical snapshot path must make no live calls and must not fabricate 0.0 for live-only flow fields. */
public class HistoricalSnapshotNoLiveCallsTest {

    private static String historicalMethodBody() throws Exception {
        Path src = Paths.get(System.getProperty("b075.source", "src/main/java/datafeed/MarketDataSnapshot.java"));
        String all = new String(Files.readAllBytes(src), "UTF-8");
        int a = all.indexOf("public ObjectNode fetchHistoricalSnapshot");
        int b = all.indexOf("private Map<String, JsonNode> fetchMultiTimeframeAsOf");
        assertTrue(a > 0 && b > a, "method markers not found");
        return all.substring(a, b);
    }

    @Test
    void noLiveCalls() throws Exception {
        String body = historicalMethodBody();
        for (String f : new String[]{"spotPrice", "premiumIndex", "longShortRatio", "topLongShortPositionRatio",
                "buildSpotPerpBasis", "buildOiBreakdown"}) {
            assertFalse(body.contains(f), "historical path still references " + f);
        }
    }

    @Test
    void liveOnlyFieldsAreNullNotZero() throws Exception {
        String body = historicalMethodBody();
        assertFalse(body.contains("cond.put(\"book_imbalance\", 0.0)"));
        assertFalse(body.contains("fund.put(\"current_rate\", 0.0)"));
        assertFalse(body.contains("tradeFlow.put(\"net_delta_1h\", 0.0)"));
        assertTrue(body.contains("cond.putNull(\"book_imbalance\")"));
        assertTrue(body.contains("\"UNAVAILABLE\""));
        assertTrue(body.contains("root.set(\"session\""));
        assertTrue(body.contains("root.set(\"liquidation_warning\""));
        assertTrue(body.contains("root.set(\"data_quality\""));
    }
}
