package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.*;
import java.util.concurrent.*;
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

    public BinanceLiquidationAccumulator(String symbol) throws Exception {
        super(new URI("wss://fstream.binance.com/market/ws/" + symbol.toLowerCase() + "@forceOrder"));
        this.symbol = symbol;
        this.reconnectExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "liq-reconnect-" + symbol);
            t.setDaemon(true);
            return t;
        });
        setConnectionLostTimeout(30);
    }

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