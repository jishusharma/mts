package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/**
 * WebSocket listener for Binance futures forceOrder (liquidation) events.
 * Aggregates liquidations into $100 price buckets.
 * Supports multiple symbols via separate instances.
 */
public class BinanceLiquidationAccumulator extends WebSocketClient {

    private static final int BUCKET_SIZE = 100; // $100 price buckets
    private static final int RECONNECT_DELAY_MS = 5_000;

    private final String symbol;
    private final ObjectMapper mapper = new ObjectMapper();
    private final ConcurrentMap<Integer, Bucket> buckets = new ConcurrentHashMap<>();
    private final ScheduledExecutorService reconnectExecutor;
    private volatile boolean shuttingDown = false;
    private volatile long lastEventTime = 0;

    // --- append-only event log (H3 has no REST backfill; unrecorded data is lost) ---
    static final Path DEFAULT_LOG_DIR = Paths.get("runtime_data", "liq_events");
    private static final int LOG_QUEUE_CAP = 10_000;
    private static final long LOG_ERR_INTERVAL_MS = 60_000;
    private final Path logDir;
    private final BlockingQueue<String> logQueue;
    private final AtomicLong logEnqueued = new AtomicLong();
    private final AtomicLong logDone = new AtomicLong();
    private final AtomicLong logDropped = new AtomicLong();
    private final AtomicLong logErrors = new AtomicLong();
    private volatile long lastLogErrPrint = 0;
    private Thread logWriter;

    public BinanceLiquidationAccumulator(String symbol) throws Exception {
        this(symbol, DEFAULT_LOG_DIR);
    }

    public BinanceLiquidationAccumulator(String symbol, Path logDir) throws Exception {
        this(symbol, logDir, LOG_QUEUE_CAP, true);
    }

    BinanceLiquidationAccumulator(String symbol, Path logDir, int queueCap, boolean startWriter) throws Exception {
        super(new URI("wss://fstream.binance.com/market/ws/" + symbol.toLowerCase() + "@forceOrder"));
        this.symbol = symbol;
        this.reconnectExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "liq-reconnect-" + symbol);
            t.setDaemon(true);
            return t;
        });
        setConnectionLostTimeout(30);
        this.logDir = logDir;
        this.logQueue = new ArrayBlockingQueue<>(queueCap);
        if (startWriter) {
            logWriter = new Thread(this::logLoop, "liq-log-" + symbol);
            logWriter.setDaemon(true);
            logWriter.start();
        }
    }

    /** Never blocks and never throws: a full queue drops the line and counts it (fail open for the feed). */
    private void enqueueLog(String line) {
        if (logQueue.offer(line)) logEnqueued.incrementAndGet();
        else {
            logDropped.incrementAndGet();
            logErr("log queue full, event dropped");
        }
    }

    private void logLoop() {
        while (!Thread.currentThread().isInterrupted()) {
            String line;
            try {
                line = logQueue.take();
            } catch (InterruptedException ie) {
                return;
            }
            try {
                Files.createDirectories(logDir);
                Files.write(logDir.resolve(symbol + ".jsonl"), (line + '\n').getBytes(StandardCharsets.UTF_8),
                        StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            } catch (Throwable t) {
                logErrors.incrementAndGet();
                logErr("write failed: " + t);
            } finally {
                logDone.incrementAndGet();
            }
        }
    }

    private void logErr(String msg) {
        long now = System.currentTimeMillis();
        if (now - lastLogErrPrint >= LOG_ERR_INTERVAL_MS) {
            lastLogErrPrint = now;
            System.err.println("[Liquidation WS] event log (" + symbol + "): " + msg);
        }
    }

    /** True once every queued line has been written (or failed); for tests and clean shutdown. */
    public boolean awaitLogIdle(long timeoutMs) throws InterruptedException {
        long end = System.currentTimeMillis() + timeoutMs;
        while (logDone.get() < logEnqueued.get()) {
            if (System.currentTimeMillis() > end) return false;
            Thread.sleep(5);
        }
        return true;
    }

    public long getLogErrorCount() { return logErrors.get(); }
    public long getLogDroppedCount() { return logDropped.get(); }

    @Override
    public void onOpen(ServerHandshake handshake) {
        System.out.println("[Liquidation WS] Connected: " + symbol);
    }

    @Override
    public void onMessage(String message) {
        try {
            JsonNode root = mapper.readTree(message);
            // Debug: print raw event once every ~5 minutes or on first event
            if (lastEventTime == 0 || System.currentTimeMillis() - lastEventTime > 300_000) {
                System.out.println("[Liquidation WS] Raw event (" + symbol + "): " + message);
            }
            lastEventTime = System.currentTimeMillis();

            if (!"forceOrder".equals(root.get("e").asText())) return;

            JsonNode o = root.get("o");
            double price = o.get("ap").asDouble();
            double qty = o.get("z").asDouble();
            String side = o.get("S").asText(); // "BUY" = short liquidation, "SELL" = long liquidation

            try {
                com.fasterxml.jackson.databind.node.ObjectNode ev = mapper.createObjectNode();
                ev.put("symbol", symbol);
                ev.put("eventTime", root.path("E").asLong());
                ev.put("tradeTime", o.path("T").asLong());
                ev.put("side", side);
                ev.put("price", price);
                ev.put("qty", qty);
                ev.put("origPrice", o.path("p").asDouble());
                ev.put("origQty", o.path("q").asDouble());
                enqueueLog(mapper.writeValueAsString(ev));
            } catch (Throwable t) {
                logErrors.incrementAndGet();
                logErr("serialize failed: " + t);
            }

            int bucketPrice = (int) (Math.floor(price / BUCKET_SIZE) * BUCKET_SIZE);

            buckets.compute(bucketPrice, (k, b) -> {
                if (b == null) b = new Bucket(bucketPrice);
                b.add(qty, side);
                return b;
            });
        } catch (Exception e) {
            System.err.println("[Liquidation WS] Parse error (" + symbol + "): " + e.getMessage());
        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        System.out.println("[Liquidation WS] Closed: " + symbol + " | " + reason + " (remote=" + remote + ")");
        if (!shuttingDown) scheduleReconnect();
    }

    @Override
    public void onError(Exception ex) {
        System.err.println("[Liquidation WS] Error (" + symbol + "): " + ex.getMessage());
    }

    private void scheduleReconnect() {
        reconnectExecutor.schedule(() -> {
            try {
                System.out.println("[Liquidation WS] Reconnecting: " + symbol);
                reconnectBlocking();
            } catch (Exception e) {
                System.err.println("[Liquidation WS] Reconnect failed (" + symbol + "): " + e.getMessage());
            }
        }, RECONNECT_DELAY_MS, TimeUnit.MILLISECONDS);
    }

    public List<Cluster> getTopClusters(int n) {
        return buckets.values().stream()
                .sorted(Comparator.comparingDouble(Bucket::getTotalQty).reversed())
                .limit(n)
                .map(b -> new Cluster(b.price, b.totalQty, b.longLiqQty, b.shortLiqQty))
                .collect(Collectors.toList());
    }

    public boolean hasReceivedEvents() {
        return lastEventTime > 0;
    }

    public long getLastEventTime() {
        return lastEventTime;
    }

    public void reset() {
        buckets.clear();
        lastEventTime = 0;
    }

    public void shutdown() {
        shuttingDown = true;
        reconnectExecutor.shutdownNow();
        if (logWriter != null) logWriter.interrupt();
        close();
    }

    public String getSymbol() {
        return symbol;
    }

    // --- Inner classes ---

    private static class Bucket {
        final int price;
        double totalQty = 0;
        double longLiqQty = 0;   // side = SELL (longs got liquidated)
        double shortLiqQty = 0;  // side = BUY (shorts got liquidated)

        Bucket(int price) { this.price = price; }

        synchronized void add(double qty, String side) {
            totalQty += qty;
            if ("SELL".equals(side)) longLiqQty += qty;
            else if ("BUY".equals(side)) shortLiqQty += qty;
        }

        double getTotalQty() { return totalQty; }
    }

    public static class Cluster {
        public final int priceLevel;
        public final double totalQty;
        public final double longLiquidationQty;
        public final double shortLiquidationQty;

        public Cluster(int priceLevel, double totalQty, double longLiqQty, double shortLiqQty) {
            this.priceLevel = priceLevel;
            this.totalQty = totalQty;
            this.longLiquidationQty = longLiqQty;
            this.shortLiquidationQty = shortLiqQty;
        }

        @Override
        public String toString() {
            return String.format("Cluster[$%,d | total=%.3f | longLiq=%.3f | shortLiq=%.3f]",
                    priceLevel, totalQty, longLiquidationQty, shortLiquidationQty);
        }
    }
}