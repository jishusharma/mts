package datafeed;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

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
}
