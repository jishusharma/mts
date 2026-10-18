package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * FORMULAS 18.1 edge convention: POC = bin centre, VAH = top edge of its bin, VAL = bottom edge of its bin.
 * Expected numbers are worked by hand from 18.1 (Worked B and C scaled to w = 10, origin 1000), not from the code.
 * Point-mass bars (high == low) put all volume in the bin holding that price.
 */
public class BuildVpEdgeConventionTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final double W = 10.0;

    private static ArrayNode bar(long t, double price, double vol) {
        ArrayNode a = MAPPER.createArrayNode();
        a.add(t).add(price).add(price).add(price).add(price).add(vol).add(t + 59_999L).add(0.0).add(1).add(0.0);
        return a;
    }

    private static List<JsonNode> bars(double... priceVolPairs) {
        List<JsonNode> out = new ArrayList<>();
        for (int i = 0; i < priceVolPairs.length; i += 2) out.add(bar(1_700_000_000_000L + i * 30_000L, priceVolPairs[i], priceVolPairs[i + 1]));
        return out;
    }

    private static ObjectNode vp(MarketDataSnapshot snap, List<JsonNode> bars) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod("buildVp", List.class, boolean.class, double.class);
        m.setAccessible(true);
        return (ObjectNode) m.invoke(snap, bars, false, W);
    }

    private static void assertLevels(ObjectNode n, double poc, double vah, double val) {
        assertEquals(poc, n.get("poc").asDouble(), 1e-9, "poc");
        assertEquals(vah, n.get("vah").asDouble(), 1e-9, "vah");
        assertEquals(val, n.get("val").asDouble(), 1e-9, "val");
    }

    /** 18.1 Worked B: bin volumes [1,2,10,4,3] -> POC bin 2, value area bins 2..3: val 20, vah 40, poc 25 (+1000). */
    @Test
    void workedB() throws Exception {
        List<JsonNode> b = bars(1005, 1, 1015, 2, 1025, 10, 1035, 4, 1045, 3);
        assertLevels(vp(new MarketDataSnapshot(), b), 1025.0, 1040.0, 1020.0);
    }

    /** 18.1 Worked C (tie goes to the lower bin): volumes [3,10,3] -> bins 0..1: val 1000, vah 1020, poc 1015. */
    @Test
    void workedCTie() throws Exception {
        List<JsonNode> b = bars(1005, 3, 1015, 10, 1025, 3);
        assertLevels(vp(new MarketDataSnapshot(), b), 1015.0, 1020.0, 1000.0);
    }

    /** One-bin profile: POC centre 1005, VAL bottom 1000, VAH top 1010. */
    @Test
    void oneBinProfile() throws Exception {
        assertLevels(vp(new MarketDataSnapshot(), bars(1005, 5)), 1005.0, 1010.0, 1000.0);
    }

    /** Restart/reset: a fresh instance and a reused instance give identical levels (no carried state). */
    @Test
    void noStateAcrossCallsOrInstances() throws Exception {
        MarketDataSnapshot s = new MarketDataSnapshot();
        vp(s, bars(2005, 9, 2015, 1));
        assertLevels(vp(s, bars(1005, 1, 1015, 2, 1025, 10, 1035, 4, 1045, 3)), 1025.0, 1040.0, 1020.0);
        assertLevels(vp(new MarketDataSnapshot(), bars(1005, 1, 1015, 2, 1025, 10, 1035, 4, 1045, 3)), 1025.0, 1040.0, 1020.0);
    }

    @Test
    void emptyProfileIsZero() throws Exception {
        assertLevels(vp(new MarketDataSnapshot(), new ArrayList<>()), 0.0, 0.0, 0.0);
    }

    /** Fail closed: NaN price or volume gives the empty profile, not a guessed level. */
    @Test
    void nanFailsClosed() throws Exception {
        assertLevels(vp(new MarketDataSnapshot(), bars(1005, 1, Double.NaN, 5, 1025, 10)), 0.0, 0.0, 0.0);
        assertLevels(vp(new MarketDataSnapshot(), bars(1005, 1, 1015, Double.NaN)), 0.0, 0.0, 0.0);
    }
}
