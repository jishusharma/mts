package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * T037: ExtraSetupBuilder momentum candidate. B142 (D15 2026-10-10): momentum emission is disabled; the two emission
 * tests were removed and ExtraSetupBuilderDisabledTest pins 0 candidates on this fixture. The hand maths below is history.
 * Fixture: 20 one-minute klines, closes all 100. The first 13 candles have range 1 (high 100.5 / low 99.5); the last 3
 * have range 10 (high 105 / low 95). speedFromKlines looks at the last 10: avg range = (7*1 + 3*10)/10 = 3.7, threshold
 * 1.5*3.7 = 5.55, so exactly the last 3 candles are "large" -> consecutive_large = 3 (the minimum).
 * previousHigh = max high of candles n-3..n-2 = 105; previousLow = min low = 95; previousClose = close of candle n-2 = 100.
 * Hand maths (price 99, short): risk |99-105| = 6, reward |80-99| = 19, gross 19/6 = 3.1667 -> 3.17;
 * cost = 2*0.0005*99 = 0.099, net = (19-0.099)/(6+0.099) = 3.0990 -> 3.1 (above the 1.25 net-RR floor).
 * Long (price 101): risk 6, reward |120-101| = 19, gross 3.17; cost 0.101, net = 18.899/6.101 = 3.0975 -> 3.1.
 */
public class ExtraSetupBuilderMomentumTest {

    private static final ObjectMapper M = new ObjectMapper();

    private static ArrayNode klines(int largeAtEnd) {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 20; i++) {
            boolean large = i >= 20 - largeAtEnd;
            ArrayNode c = k.addArray();
            c.add(i * 60_000L);          // open time
            c.add(100.0);                // open
            c.add(large ? 105.0 : 100.5);// high
            c.add(large ? 95.0 : 99.5);  // low
            c.add(100.0);                // close
        }
        return k;
    }

    private static ObjectNode root(double price, boolean speedUp, boolean withLevels) {
        ObjectNode root = M.createObjectNode();
        root.put("current_price", price);
        ObjectNode cond = root.putObject("conditions");
        cond.put("speed_picking_up", speedUp);
        cond.put("cvd_trade_flow_aligned", true);
        root.putObject("structure");
        if (withLevels) {
            ObjectNode vp = root.putObject("daily_vp");
            vp.put("val", 80.0);
            vp.put("vah", 120.0);
        }
        return root;
    }

    private static ArrayNode build(ObjectNode root, ArrayNode k) {
        return ExtraSetupBuilder.build(M, root, new HashMap<String, JsonNode>(), k);
    }

    @Test
    public void noCandidateWhenSpeedFlagIsOff() {
        assertEquals(0, build(root(99.0, false, true), klines(3)).size());
    }

    @Test
    public void noCandidateWhenFewerThanThreeLargeCandles() {
        // only 2 large candles at the end -> consecutive_large = 2 < 3
        assertEquals(0, build(root(99.0, true, true), klines(2)).size());
    }

    @Test
    public void noCandidateWhenFewerThanTenKlines() {
        ArrayNode k = M.createArrayNode();
        for (int i = 0; i < 9; i++) {
            ArrayNode c = k.addArray();
            c.add(0L); c.add(100.0); c.add(105.0); c.add(95.0); c.add(100.0);
        }
        assertEquals(0, build(root(99.0, true, true), k).size());
    }

    @Test
    public void candidateRejectedWhenNoTargetExists() {
        // no VP levels and no prior_day -> target 0 -> net RR 0, below the floor -> momentum candidate removed
        assertEquals(0, build(root(99.0, true, false), klines(3)).size());
    }

    @Test
    public void candidateRejectedWhenTargetTooCloseForNetRrFloor() {
        // support at 98.9: reward 0.1 less cost 0.099 = 0.001; net ~ 0.0002, far below the floor
        ObjectNode r = root(99.0, true, false);
        r.putObject("daily_vp").put("val", 98.9);
        assertEquals(0, build(r, klines(3)).size());
    }
}
