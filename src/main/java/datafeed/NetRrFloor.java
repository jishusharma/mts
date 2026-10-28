package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Single Java reader of the net_rr floor: MyTradingSys/system/net_rr_floor.json, the only place the number is
 * written. start-trading-day.ps1 and MyTradingSys/runtime/net_rr_floor.py read the same file.
 *
 * read() returns NaN when the file is missing, unparsable, non-numeric or not positive. Every comparison
 * against NaN is false, so a gate written as {@code netRR >= NetRrFloor.read()} fails closed. There is no
 * fallback number: a fallback would be a second copy of the value.
 *
 * Each snapshot is built by a fresh JVM (mvn exec:java), so the file is read once per cycle.
 */
public final class NetRrFloor {

    /** Test hook: absolute or cwd-relative path that replaces the default file. */
    public static final String PATH_PROPERTY = "mts.netRrFloorFile";

    private NetRrFloor() {
    }

    public static double read() {
        String override = System.getProperty(PATH_PROPERTY);
        Path p = override != null ? Paths.get(override) : Paths.get("MyTradingSys", "system", "net_rr_floor.json");
        try {
            JsonNode n = new ObjectMapper().readTree(p.toFile()).get("net_rr_floor");
            if (n == null || !n.isNumber()) {
                return Double.NaN;
            }
            double v = n.asDouble();
            return (Double.isFinite(v) && v > 0) ? v : Double.NaN;
        } catch (Exception e) {
            return Double.NaN;
        }
    }
}
