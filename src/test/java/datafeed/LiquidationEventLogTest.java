package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

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
    @Test
    void shutdownDrainsAcceptedEventsBeforeReturning(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir);
        for (int i = 0; i < 200; i++)
            acc.onMessage(force("BTCUSDT", "SELL", "100", "1", i, i));
        acc.shutdown();
        assertEquals(200, lines(dir, "BTCUSDT").size());
        assertEquals(0, acc.getLogDroppedCount());
        assertEquals(0, acc.getLogErrorCount());
    }

    @Test
    void shutdownCountsAbandonedQueueWhenNoWriterExists(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir, 2, false);
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 1, 1));
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 2, 2));
        acc.shutdown();
        assertEquals(2, acc.getLogDroppedCount());
        assertTrue(acc.awaitLogIdle(100));
        acc.shutdown();
        assertEquals(2, acc.getLogDroppedCount());
    }

    @Test
    void shutdownWaitsForAnAcceptedBlockedWrite(@TempDir Path dir) throws Exception {
        CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        Runnable gate = () -> {
            entered.countDown();
            try { release.await(); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); throw new IllegalStateException(e); }
        };
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir, 10, true, gate);
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 1, 1));
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 2, 2));
        CountDownLatch started = new CountDownLatch(1), finished = new CountDownLatch(1);
        Thread shutdown = new Thread(() -> { started.countDown(); acc.shutdown(); finished.countDown(); });
        shutdown.start();
        try {
            assertTrue(started.await(1, TimeUnit.SECONDS));
            assertFalse(finished.await(100, TimeUnit.MILLISECONDS), "shutdown must wait for the blocked write");
        } finally {
            release.countDown();
            shutdown.join(7000);
        }
        assertFalse(shutdown.isAlive(), "shutdown must be bounded");
        assertEquals(2, lines(dir, "BTCUSDT").size());
        assertTrue(acc.awaitLogIdle(100));
    }

    @Test
    void timedOutDrainCountsLossAndPrintsEvenWhenRateLimited(@TempDir Path dir) throws Exception {
        CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        Runnable gate = () -> {
            entered.countDown();
            try { release.await(); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); throw new IllegalStateException(e); }
        };
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir, 10, true, gate);
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 1, 1));
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 2, 2));
        java.io.ByteArrayOutputStream captured = new java.io.ByteArrayOutputStream();
        java.io.PrintStream previous = System.err;
        long start = System.nanoTime();
        try {
            System.setErr(new java.io.PrintStream(captured));
            acc.shutdown();
            assertTrue(acc.awaitLogIdle(2000));
        } finally {
            System.setErr(previous);
            release.countDown();
        }
        assertTrue(System.nanoTime() - start < 8_000_000_000L, "stalled writer cannot hang shutdown");
        assertEquals(1, acc.getLogDroppedCount());
        assertEquals(1, acc.getLogErrorCount());
        assertTrue(captured.toString().contains("shutdown dropped 1 queued events"));
    }

    @Test
    void postShutdownEventIsCountedAsDropped(@TempDir Path dir) throws Exception {
        BinanceLiquidationAccumulator acc = new BinanceLiquidationAccumulator("BTCUSDT", dir);
        acc.shutdown();
        acc.onMessage(force("BTCUSDT", "SELL", "100", "1", 1, 1));
        assertEquals(1, acc.getLogDroppedCount());
        assertEquals(0, lines(dir, "BTCUSDT").size());
        assertTrue(acc.awaitLogIdle(100));
    }

}
