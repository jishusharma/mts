package datafeed;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/** Statemachine JVM must build and connect the liquidation event log without ever blocking the emitter. */
public class LiquidationLogWiringTest {

    static class Stub extends BinanceLiquidationAccumulator {
        boolean connected;
        boolean down;

        Stub(String sym, Path dir) throws Exception {
            super(sym, dir, 16, false);
        }

        @Override public void connect() { connected = true; }
        @Override public void shutdown() { down = true; }
    }

    @TempDir Path dir;

    @Test
    void buildsBtcAndEth() {
        List<String> built = new ArrayList<>();
        List<BinanceLiquidationAccumulator> out = Main.startLiquidationLogs(List.of("BTCUSDT", "ETHUSDT"), sym -> {
            try {
                built.add(sym);
                return new Stub(sym, dir);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
        assertEquals(List.of("BTCUSDT", "ETHUSDT"), built);
        assertEquals(2, out.size());
        for (BinanceLiquidationAccumulator a : out) assertTrue(((Stub) a).connected);
    }

    @Test
    void throwingFactoryNeverPropagates() {
        List<BinanceLiquidationAccumulator> out = assertDoesNotThrow(() ->
                Main.startLiquidationLogs(List.of("BTCUSDT", "ETHUSDT"), sym -> {
                    if (sym.equals("ETHUSDT")) throw new IllegalStateException("boom");
                    try {
                        return new Stub(sym, dir);
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                }));
        assertEquals(1, out.size());
        assertEquals("BTCUSDT", out.get(0).getSymbol());
    }

    @Test
    void closeAllShutsEveryOneEvenIfOneThrows() throws Exception {
        Stub bad = new Stub("BTCUSDT", dir) {
            @Override public void shutdown() { down = true; throw new IllegalStateException("x"); }
        };
        Stub a = new Stub("ETHUSDT", dir);
        assertDoesNotThrow(() -> Main.closeAll(List.of(bad, a)));
        assertTrue(bad.down);
        assertTrue(a.down);
    }

    // ---- shutdown drain ----

    private static String ev(long n, String qty) {
        return "{\"e\":\"forceOrder\",\"E\":" + n + ",\"o\":{\"S\":\"SELL\",\"p\":\"100.0\",\"q\":\"1\",\"ap\":\"100.0\",\"z\":\"" + qty + "\",\"T\":" + n + "}}";
    }

    private List<String> lines(String sym) throws Exception {
        Path f = dir.resolve(sym + ".jsonl");
        return Files.exists(f) ? Files.readAllLines(f) : List.of();
    }

    /** Real shutdown(); socket never opened; events ids first..first+n-1 queued before the writer starts. */
    private BinanceLiquidationAccumulator loaded(String sym, Path d, long first, int n) throws Exception {
        BinanceLiquidationAccumulator a = new BinanceLiquidationAccumulator(sym, d, 1000, false);
        for (int i = 0; i < n; i++) a.onMessage(ev(first + i, "2"));
        a.startLogWriter();
        return a;
    }

    private static long eventTime(String line) {
        java.util.regex.Matcher m = java.util.regex.Pattern.compile("\"eventTime\":(\\d+)").matcher(line);
        assertTrue(m.find(), line);
        return Long.parseLong(m.group(1));
    }

    @Test
    void shutdownWritesAllQueuedLines() throws Exception {
        BinanceLiquidationAccumulator a = loaded("BTCUSDT", dir, 1, 200);
        a.shutdown();
        assertEquals(200, lines("BTCUSDT").size());
        assertFalse(a.isLogWriterAlive());
    }

    @Test
    void restartAppendsWithoutDuplicatesOrLoss() throws Exception {
        loaded("BTCUSDT", dir, 1, 5).shutdown();
        assertEquals(5, lines("BTCUSDT").size());
        loaded("BTCUSDT", dir, 101, 3).shutdown();
        List<Long> ids = new ArrayList<>();
        for (String l : lines("BTCUSDT")) ids.add(eventTime(l));
        assertEquals(List.of(1L, 2L, 3L, 4L, 5L, 101L, 102L, 103L), ids);
    }

    @Test
    void badInputLinesDoNotStopTheDrain() throws Exception {
        BinanceLiquidationAccumulator a = new BinanceLiquidationAccumulator("ETHUSDT", dir, 1000, false);
        a.onMessage(ev(1, "2"));
        a.onMessage("not json at all");
        a.onMessage("{\"e\":\"forceOrder\"}");   // no "o"
        a.onMessage("{\"x\":1}");                // no "e"
        a.onMessage(ev(2, "0"));                 // zero qty is a valid event, still logged
        a.onMessage(ev(3, "2"));
        a.startLogWriter();
        a.shutdown();
        List<String> l = lines("ETHUSDT");
        assertEquals(3, l.size()); // ids 1, 2 (zero qty), 3; the 3 bad inputs are skipped
        assertEquals(3L, eventTime(l.get(2)));
        assertEquals(0, a.getLogErrorCount());
    }

    @Test
    void ioErrorFailsClosedAndShutdownStillReturns() throws Exception {
        Path blocker = dir.resolve("blocker");
        Files.writeString(blocker, "x"); // a file where the log dir should be: every write fails
        BinanceLiquidationAccumulator a = loaded("BTCUSDT", blocker, 1, 5);
        long t0 = System.nanoTime();
        a.shutdown();
        long ms = (System.nanoTime() - t0) / 1_000_000;
        assertTrue(ms < 2500, "shutdown took " + ms + " ms");
        assertEquals(5, a.getLogErrorCount());
        assertFalse(a.isLogWriterAlive());
    }
}
