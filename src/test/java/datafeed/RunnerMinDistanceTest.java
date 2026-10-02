package datafeed;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Runner min-distance (NO-SOURCE 0.25 %, MyTradingSys/system/runner_min_distance.json). Hand-computed:
 * LONG zone 1000, stop 990 (risk 10), floor 1.25: node 1020 = 2.0R gross, net 1.5 -> target.
 * 1022.5: 2.5/1020 = 0.2451 % (< 0.25, skipped); 1030: 10/1020 = 0.9804 % (runner); 1022.6: 0.2549 % (qualifies).
 */
public class RunnerMinDistanceTest {

    @TempDir
    Path tmp;

    @AfterEach
    void clear() {
        System.clearProperty(RunnerMinDistance.PATH_PROPERTY);
    }

    private void point(String json) throws Exception {
        Path f = tmp.resolve("runner_min_distance.json");
        Files.writeString(f, json);
        System.setProperty(RunnerMinDistance.PATH_PROPERTY, f.toString());
    }

    @Test
    void closeNodeIsSkippedToTheNextThatClears() {
        double[] r = SetupCandidatesBuilder.pickTarget(List.of(1020.0, 1022.5, 1030.0), 1000, 990, false, 1.25, 0.25);
        assertArrayEquals(new double[]{1020.0, 1030.0}, r, 0.0);
    }

    @Test
    void zeroMinimumKeepsTheOldNextNode() {
        assertArrayEquals(new double[]{1020.0, 1022.5},
                SetupCandidatesBuilder.pickTarget(List.of(1020.0, 1022.5, 1030.0), 1000, 990, false, 1.25), 0.0);
    }

    @Test
    void justAboveTheMinimumQualifies() {
        assertArrayEquals(new double[]{1020.0, 1022.6},
                SetupCandidatesBuilder.pickTarget(List.of(1020.0, 1022.6), 1000, 990, false, 1.25, 0.25), 0.0);
    }

    @Test
    void skipToNoneReturnsZeroRunner() {
        // 1022.0: 0.1961 %, 1022.4: 0.2353 % -> both under 0.25
        assertArrayEquals(new double[]{1020.0, 0.0},
                SetupCandidatesBuilder.pickTarget(List.of(1020.0, 1022.0, 1022.4), 1000, 990, false, 1.25, 0.25), 0.0);
    }

    @Test
    void shortSideMeasuresFromTheTarget() {
        // SHORT zone 1000, stop 1010: 980 = 2.0R target; 977.6: 2.4/980 = 0.2449 % skipped; 970: 1.0204 % runner
        assertArrayEquals(new double[]{980.0, 970.0},
                SetupCandidatesBuilder.pickTarget(List.of(980.0, 977.6, 970.0), 1000, 1010, true, 1.25, 0.25), 0.0);
    }

    @Test
    void nanMinimumQualifiesNothing() {
        assertArrayEquals(new double[]{1020.0, 0.0},
                SetupCandidatesBuilder.pickTarget(List.of(1020.0, 1030.0), 1000, 990, false, 1.25, Double.NaN), 0.0);
    }

    @Test
    void readerReadsTheFileAndFailsClosedAsNaN() throws Exception {
        point("{\"runner_min_distance_pct\": 0.25}");
        assertEquals(0.25, RunnerMinDistance.read(), 0.0);
        point("{\"runner_min_distance_pct\": 0}");
        assertEquals(0.0, RunnerMinDistance.read(), 0.0);
        for (String bad : new String[]{"{\"runner_min_distance_pct\": \"x\"}", "{\"runner_min_distance_pct\": true}",
                "{\"runner_min_distance_pct\": -1}", "{\"other\": 1}", "not json", "[]"}) {
            point(bad);
            assertTrue(Double.isNaN(RunnerMinDistance.read()), bad);
        }
        System.setProperty(RunnerMinDistance.PATH_PROPERTY, tmp.resolve("missing.json").toString());
        assertTrue(Double.isNaN(RunnerMinDistance.read()));
    }

    @Test
    void shippedFileIsValid() {
        assertTrue(RunnerMinDistance.read() > 0.0);
    }
}
