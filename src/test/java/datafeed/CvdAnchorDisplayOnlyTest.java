package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * B070: the UTC 00:00 session anchor is display-only. Hand-computed: a bar with volume 2 and taker-buy 1.5 has delta
 * 2*1.5 - 2 = +1; taker-buy 0.5 gives -1. Rolling window of 50 bars at +1: series 1..50, last-20 mean 40.5, older-20 mean
 * 20.5, change (40.5-20.5)/20.5 = 0.976 > 0.02 -> "rising", last_3_delta all positive. Session value = sum of session
 * bar deltas, whatever the rolling window says.
 */
public class CvdAnchorDisplayOnlyTest {

    private static final ObjectMapper M = new ObjectMapper();

    private static ArrayNode bars(int n, double buy) {
        ArrayNode a = M.createArrayNode();
        for (int i = 0; i < n; i++) {
            ArrayNode b = a.addArray();
            for (int k = 0; k < 10; k++) b.add(0.0);
            b.set(5, M.getNodeFactory().numberNode(2.0));
            b.set(9, M.getNodeFactory().numberNode(buy));
        }
        return a;
    }

    private static JsonNode cvd(ArrayNode session, ArrayNode rolling) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod("buildCvd", JsonNode.class, JsonNode.class);
        m.setAccessible(true);
        return (JsonNode) m.invoke(new MarketDataSnapshot(), session, rolling);
    }

    @Test
    void valueFollowsSessionBars() throws Exception {
        assertEquals(3.0, cvd(bars(3, 1.5), bars(50, 1.5)).get("value").asDouble(), 1e-9);
        assertEquals(-5.0, cvd(bars(5, 0.5), bars(50, 1.5)).get("value").asDouble(), 1e-9);
    }

    @Test
    void slopeAndLast3IgnoreTheSessionAnchor() throws Exception {
        for (ArrayNode session : new ArrayNode[]{bars(3, 1.5), bars(5, 0.5), bars(0, 1.5)}) {
            JsonNode n = cvd(session, bars(50, 1.5));
            assertEquals("rising", n.get("slope").asText());
            assertEquals(3, n.get("last_3_delta").size());
            assertEquals("positive", n.get("last_3_delta").get(2).asText());
        }
    }
}
