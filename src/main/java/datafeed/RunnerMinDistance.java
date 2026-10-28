package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Single Java reader of the runner minimum distance: MyTradingSys/system/runner_min_distance.json, key
 * runner_min_distance_pct (percent of the target price, NO-SOURCE, see the session record that set it).
 * MyTradingSys/runtime/runner_min_distance.py reads the same file.
 *
 * read() returns NaN when the file is missing, unparsable, non-numeric, non-finite or negative. A NaN distance
 * qualifies no node, so the runner is 0 and the plan stays single-target (fail closed to the pre-R2 behaviour).
 * 0 is a valid value (any strictly farther node qualifies). There is no fallback number.
 */
public final class RunnerMinDistance {

    /** Test hook: absolute or cwd-relative path that replaces the default file. */
    public static final String PATH_PROPERTY = "mts.runnerMinDistanceFile";

    private RunnerMinDistance() {
    }

    public static double read() {
        String override = System.getProperty(PATH_PROPERTY);
        Path p = override != null ? Paths.get(override) : Paths.get("MyTradingSys", "system", "runner_min_distance.json");
        try {
            JsonNode n = new ObjectMapper().readTree(p.toFile()).get("runner_min_distance_pct");
            if (n == null || !n.isNumber()) {
                return Double.NaN;
            }
            double v = n.asDouble();
            return (Double.isFinite(v) && v >= 0) ? v : Double.NaN;
        } catch (Exception e) {
            return Double.NaN;
        }
    }
}
