package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.io.File;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * B153: the Python side (MyTradingSys/tests/test_net_rr_parity_b153.py) reads the same file. Expected values are
 * hand-worked from FORMULAS.md section 17, so a drift in either language fails against the table, not against the other.
 */
public class NetRRParityFixtureTest {

    @Test
    void javaMatchesEveryVector() throws Exception {
        JsonNode root = new ObjectMapper().readTree(new File("MyTradingSys/tests/fixtures/net_rr_vectors.json"));
        double tol = root.get("tolerance").asDouble();
        JsonNode cases = root.get("cases");
        assertTrue(cases.size() >= 7);
        for (JsonNode c : cases) {
            double got = ExecutionMathConstants.netRR(c.get("entry").asDouble(), c.get("target").asDouble(), c.get("stop").asDouble());
            assertEquals(c.get("expected").asDouble(), got, tol, c.get("name").asText());
        }
    }
}
