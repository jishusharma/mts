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
 * B059: with fixedBinSize 10 the bin edges snap to a 10-point grid, so POC/VAH/VAL do not move when the
 * window extends downward (before the fix the origin was minP, so every new low shifted all bin edges).
 */
public class BuildVpFixedGridTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static ArrayNode bar(long t, double h, double l, double c, double vol) {
        ArrayNode a = MAPPER.createArrayNode();
        a.add(t).add(c).add(h).add(l).add(c).add(vol).add(t + 59_999L).add(0.0).add(1).add(0.0);
        return a;
    }

    private static ObjectNode vp(List<JsonNode> bars, double fixedBinSize) throws Exception {
        Method m = MarketDataSnapshot.class.getDeclaredMethod("buildVp", List.class, boolean.class, double.class);
        m.setAccessible(true);
        return (ObjectNode) m.invoke(new MarketDataSnapshot(), bars, false, fixedBinSize);
    }

    private static List<JsonNode> windowA() {
        List<JsonNode> bars = new ArrayList<>();
        long t = 1_700_000_000_000L;
        for (int i = 0; i < 20; i++) bars.add(bar(t + i * 60_000L, 80378.0, 80371.0, 80374.0, 10.0));
        return bars;
    }

    @Test
    void pocVahValStayOnGridWhenWindowExtendsDownward() throws Exception {
        List<JsonNode> a = windowA();
        ObjectNode va = vp(a, 10.0);
        assertEquals(80375.0, va.get("poc").asDouble(), 1e-9);
        assertEquals(80380.0, va.get("vah").asDouble(), 1e-9);
        assertEquals(80370.0, va.get("val").asDouble(), 1e-9);

        List<JsonNode> b = new ArrayList<>(a);
        b.add(bar(1_700_000_000_000L + 20 * 60_000L, 80360.0, 80352.0, 80356.0, 1.0));
        ObjectNode vb = vp(b, 10.0);
        assertEquals(80375.0, vb.get("poc").asDouble(), 1e-9);
        assertEquals(80380.0, vb.get("vah").asDouble(), 1e-9);
        assertEquals(80370.0, vb.get("val").asDouble(), 1e-9);
    }
}
