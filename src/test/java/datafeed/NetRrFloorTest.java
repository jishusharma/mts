package datafeed;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** NetRrFloor reads MyTradingSys/system/net_rr_floor.json; hand-computed: file 1.25 -> 1.25, file 2 -> 2.0, bad -> NaN. */
public class NetRrFloorTest {

    @TempDir
    Path tmp;

    @AfterEach
    void clear() {
        System.clearProperty(NetRrFloor.PATH_PROPERTY);
    }

    private void point(String json) throws Exception {
        Path f = tmp.resolve("net_rr_floor.json");
        Files.writeString(f, json);
        System.setProperty(NetRrFloor.PATH_PROPERTY, f.toString());
    }

    @Test
    void readsTheFileEveryCall() throws Exception {
        point("{\"net_rr_floor\": 1.25}");
        assertEquals(1.25, NetRrFloor.read(), 0.0);
        point("{\"net_rr_floor\": 2}");
        assertEquals(2.0, NetRrFloor.read(), 0.0);
    }

    @Test
    void shippedFileIsValid() {
        assertTrue(NetRrFloor.read() > 0.0);  // default path, cwd = repo root under mvn test
    }

    @Test
    void failsClosedAsNaN() throws Exception {
        for (String bad : new String[]{"{\"net_rr_floor\": \"x\"}", "{\"net_rr_floor\": true}", "{\"net_rr_floor\": 0}",
                "{\"net_rr_floor\": -1}", "{\"other\": 1}", "not json", "[]"}) {
            point(bad);
            double v = NetRrFloor.read();
            assertTrue(Double.isNaN(v), bad);
            assertFalse(3.0 >= v, "a gate using >= must reject when the floor is unreadable: " + bad);
        }
        System.setProperty(NetRrFloor.PATH_PROPERTY, tmp.resolve("missing.json").toString());
        assertTrue(Double.isNaN(NetRrFloor.read()));
    }
}
