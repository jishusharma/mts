import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.lang.reflect.*;
import java.util.List;

public class ScbTest {
    static int pass = 0;
    static int fail = 0;

    static void check(String label, Object actual, Object expected) {
        boolean ok;
        if (expected == null) { ok = (actual == null); }
        else { ok = expected.equals(actual); }
        if (ok) { pass++; System.out.println("PASS " + label + " -> " + actual); }
        else { fail++; System.out.println("FAIL " + label + " expected=" + expected + " actual=" + actual); }
    }

    static Object mkZone(Class<?> zc, String name, String type, double price) throws Exception {
        Constructor<?> c = zc.getDeclaredConstructor();
        c.setAccessible(true);
        Object z = c.newInstance();
        Field f1 = zc.getDeclaredField("name"); f1.setAccessible(true); f1.set(z, name);
        Field f2 = zc.getDeclaredField("type"); f2.setAccessible(true); f2.set(z, type);
        Field f3 = zc.getDeclaredField("price"); f3.setAccessible(true); f3.setDouble(z, price);
        return z;
    }

    public static void main(String[] args) throws Exception {
        Class<?> scb = Class.forName("datafeed.SetupCandidatesBuilder");
        Class<?> zc = Class.forName("datafeed.SetupCandidatesBuilder$Zone");
        Method d = scb.getDeclaredMethod("determineSetupType", zc, String.class, String.class);
        d.setAccessible(true);

        Object zVah = mkZone(zc, "4h_vah", "4h_vah", 80000.0);
        check("B049 VAH short trend_healthy", d.invoke(null, zVah, "short", "trend_healthy"), null);
        check("VAH short balance", d.invoke(null, zVah, "short", "balance"), "ct_short");
        check("VAH short trend_unhealthy", d.invoke(null, zVah, "short", "trend_unhealthy"), "ct_short");
        check("VAH long trend_healthy", d.invoke(null, zVah, "long", "trend_healthy"), null);

        Object zVal = mkZone(zc, "4h_val", "4h_val", 75000.0);
        check("VAL long balance", d.invoke(null, zVal, "long", "balance"), "ct_long");
        check("VAL long trend_unhealthy", d.invoke(null, zVal, "long", "trend_unhealthy"), "ct_long");

        Object zVwap = mkZone(zc, "vwap", "vwap", 80000.0);
        check("T024 VWAP long trend_healthy", d.invoke(null, zVwap, "long", "trend_healthy"), "tc_long");
        check("VWAP short trend_healthy", d.invoke(null, zVwap, "short", "trend_healthy"), null);
        check("VWAP long balance", d.invoke(null, zVwap, "long", "balance"), "scalp_long");
        check("VWAP short balance", d.invoke(null, zVwap, "short", "balance"), "scalp_short");

        ObjectMapper om = new ObjectMapper();
        ObjectNode root = om.createObjectNode();
        ObjectNode cond = om.createObjectNode();
        cond.put("price_vs_va", "above_vah");
        cond.put("price_vs_poc", "above");
        root.set("conditions", cond);
        Method dm = scb.getDeclaredMethod("determineDirections", ObjectNode.class);
        dm.setAccessible(true);
        Object dirs = dm.invoke(null, root);
        check("T024 dirs above_vah contains short", ((List<?>)dirs).contains("short"), true);
        check("T024 dirs above_vah contains long", ((List<?>)dirs).contains("long"), true);

        System.out.println("TOTAL pass=" + pass + " fail=" + fail);
        System.exit(fail == 0 ? 0 : 1);
    }
}
