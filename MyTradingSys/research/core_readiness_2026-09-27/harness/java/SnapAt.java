package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.List;

/** P1 helper: regenerate snapshots at given asOf instants from the archive. Usage: SnapAt rawRoot instantsFile outJsonl
 *  (instantsFile: one ISO instant per line, already floored to the minute). Built only in a %TEMP% copy. */
public class SnapAt {
    /** Symbol to replay: -Dmts.symbol=GER40 for the DAX probe (archive file prefix); default BTCUSDT. */
    static final String SYMBOL = System.getProperty("mts.symbol", "BTCUSDT");

    public static void main(String[] a) throws Exception {
        MarketDataSnapshot mds = new MarketDataSnapshot(Paths.get(a[0]));
        ObjectMapper om = new ObjectMapper();
        List<String> ts = Files.readAllLines(Paths.get(a[1]));
        try (BufferedWriter w = Files.newBufferedWriter(Paths.get(a[2]), StandardCharsets.UTF_8)) {
            for (String t : ts) {
                if (t.isBlank()) continue;
                ObjectNode s = mds.fetchHistoricalSnapshot(SYMBOL, Instant.parse(t.trim()));
                w.write(om.writeValueAsString(s));
                w.write('\n');
            }
        }
        System.out.println("done " + ts.size());
    }
}
