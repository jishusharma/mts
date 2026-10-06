package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * B084: on the live path book_imbalance / bid_ask_ratio must be JSON null (unavailable), never a fake 0.0,
 * when the depth fetch fails or the ask side is empty. Same fail-closed shape as the historical path (putNull).
 * (SetupCandidatesBuilder already maps a null ratio to a null proof book_imbalance: HistoricalBookImbalanceNullTest.)
 */
public class BookImbalanceUnavailableTest {
    private static final ObjectMapper M = new ObjectMapper();

    private static JsonNode depth(double[][] bids, double[][] asks) {
        ObjectNode d = M.createObjectNode();
        ArrayNode b = d.putArray("bids");
        for (double[] x : bids) b.addArray().add(x[0]).add(x[1]);
        ArrayNode a = d.putArray("asks");
        for (double[] x : asks) a.addArray().add(x[0]).add(x[1]);
        return d;
    }

    @Test
    void emptyAskSideIsUnavailable() {
        assertNull(MarketDataSnapshot.bidAskRatioFromDepth(depth(new double[][]{{100, 1}}, new double[][]{}), 100.0));
    }

    @Test
    void askOutsideBandIsUnavailable() {
        assertNull(MarketDataSnapshot.bidAskRatioFromDepth(depth(new double[][]{{100, 1}}, new double[][]{{150, 1}}), 100.0));
    }

    @Test
    void normalDepthGivesRatio() {
        Double r = MarketDataSnapshot.bidAskRatioFromDepth(depth(new double[][]{{100, 3}}, new double[][]{{100, 1}}), 100.0);
        assertNotNull(r);
        assertEquals(3.0, r, 1e-9);
    }

    @Test
    void jsonEmitsNullNotZeroAndKeepsBothFieldsConsistent() {
        ObjectNode cond = M.createObjectNode();
        ObjectNode ob = M.createObjectNode();
        MarketDataSnapshot.putBookRatio(cond, ob, null);
        assertTrue(cond.get("book_imbalance").isNull());
        assertTrue(ob.get("bid_ask_ratio").isNull());
        MarketDataSnapshot.putBookRatio(cond, ob, 1.234);
        assertEquals(1.23, cond.get("book_imbalance").asDouble(), 1e-9);
        assertEquals(1.23, ob.get("bid_ask_ratio").asDouble(), 1e-9);
    }
}
