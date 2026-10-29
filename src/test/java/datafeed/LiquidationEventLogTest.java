package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/** Trust-ledger card: every forceOrder event is appended to runtime_data/liq_events/SYMBOL.jsonl (H3 has no REST backfill). */
public class LiquidationEventLogTest {

    private static final ObjectMapper M = new ObjectMapper();

    private static String force(String sym, String side, String ap, String z, long e, long t) {
        return "{\"e\":\"forceOrder\",\"E\":" + e + ",\"o\":{\"s\":\"" + sym + "\",\"S\":\"" + side
                + "\",\"o\":\"LIMIT\",\"q\":\"0.014\",\"p\":\"9910\",\"ap\":\"" + ap + "\",\"X\":\"FILLED\",\"l\":\"0.014\",\"z\":\""
                + z + "\",\"T\":" + t + "}}";
    }

    private static List<String> lines(Path dir, String sym) throws Exception {
        Path f = dir.resolve(sym + ".jsonl");
        return Files.exists(f) ? Files.readAllLines(f) : List.of();
    }

    @Test
    void forceOrderAppendsOneJsonlLine(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir);
        acc.onMessage(force("BTCUSDT", "SELL", "9910.5", "0.014", 1568014460893L, 1568014460891L));
        assertTrue(acc.awaitLogIdle(5000));
        List<String> ls = lines(dir, "BTCUSDT");
        assertEquals(1, ls.size());
        JsonNode n = M.readTree(ls.get(0));
        assertEquals(9910.5, n.get("price").asDouble(), 0);
        assertEquals(0.014, n.get("qty").asDouble(), 0);
        assertEquals("SELL", n.get("side").asText());
        assertEquals(1568014460893L, n.get("eventTime").asLong());
        assertEquals(1568014460891L, n.get("tradeTime").asLong());
        assertEquals("BTCUSDT", n.get("symbol").asText());
        assertEquals(1, acc.getTopClusters(5).size());
        acc.shutdown();
    }

    @Test
    void restartAppendsAndResetKeepsOldLines(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator a = new BinanceLiquidationAccumulator("ETHUSDT", dir);
        a.onMessage(force("ETHUSDT", "BUY", "2500", "1", 1L, 1L));
        assertTrue(a.awaitLogIdle(5000));
        a.shutdown();
        BinanceLiquidationAccumulator b = new BinanceLiquidationAccumulator("ETHUSDT", dir);
        b.onMessage(force("ETHUSDT", "BUY", "2501", "2", 2L, 2L));
        b.reset(); // daily snapshot reset must not touch the log
        assertTrue(b.awaitLogIdle(5000));
        assertEquals(2, lines(dir, "ETHUSDT").size());
        b.shutdown();
    }

    @Test
    void nonTradeAndMalformedMessagesAppendNothingAndDoNotThrow(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir);
        acc.onMessage("{\"result\":null,\"id\":1}");
        acc.onMessage("{\"e\":\"error\",\"code\":-1003,\"msg\":\"Too many requests\"}");
        acc.onMessage("not json");
        assertTrue(acc.awaitLogIdle(5000));
        assertEquals(0, lines(dir, "BTCUSDT").size());
        acc.shutdown();
    }

    @Test
    void unwritableLogFailsOpenForFeedAndCountsErrors(@TempDir Path dir) throws Exception {
        Path blocker = dir.resolve("file-not-dir");
        Files.writeString(blocker, "x");
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", blocker); // dir path is a file
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 1L, 1L));
        assertTrue(acc.awaitLogIdle(5000));
        assertEquals(1, acc.getLogErrorCount());
        assertEquals(1, acc.getTopClusters(5).size()); // feed aggregation unaffected
        acc.shutdown();
    }

    @Test
    void fullQueueDropsAndCountsInsteadOfBlocking(@TempDir Path dir) throws Exception {
        // writer not started: queue of 2 fills, the other 8 must be dropped without blocking
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir, 2, false);
        long t0 = System.nanoTime();
        for (int i = 0; i < 10; i++) acc.onMessage(force("BTCUSDT", "SELL", "100", "1", i, i));
        assertTrue((System.nanoTime() - t0) < 2_000_000_000L);
        assertEquals(8, acc.getLogDroppedCount());
        acc.shutdown();
    }
}
