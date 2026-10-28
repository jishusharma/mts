package datafeed;

import java.util.List;

/**
 * Entry point for BinanceDataFeed.
 *
 * Usage:
 *   mvn exec:java -Dexec.mainClass="datafeed.Main" -Dexec.args="snapshot BTCUSDT ETHUSDT"
 *   mvn exec:java -Dexec.mainClass="datafeed.Main" -Dexec.args="scheduler BTCUSDT ETHUSDT"
 *
 * Default (no args): single snapshot for BTCUSDT only.
 */
public class Main {
    public static void main(String[] args) throws Exception {
        String mode = "snapshot";
        List<String> symbols = List.of("BTCUSDT");

        if (args.length > 0) {
            mode = args[0].toLowerCase();
            if (args.length > 1) {
                symbols = List.of(java.util.Arrays.copyOfRange(args, 1, args.length));
            }
        }

        System.out.println("[Main] Mode: " + mode + " | Symbols: " + symbols);

        if ("statemachine".equals(mode)) {
            if (symbols.isEmpty()) {
                System.err.println("Usage: statemachine <symbol>");
                System.exit(1);
            }
            String symbol = symbols.get(0);
            StateCodeEmitter emitter = new StateCodeEmitter(symbol);
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("[Main] Shutdown signal received.");
                emitter.shutdown();
            }));
            emitter.connectBlocking();
            Thread.sleep(Long.MAX_VALUE);
        } else if ("screenhistorical".equals(mode)) {
            if (args.length < 4) { System.err.println("Usage: screenHistorical <symbol> <startISO> <endISO> <intervalHours>"); System.exit(1); }
            String symbol = args[1];
            java.time.Instant start = java.time.Instant.parse(args[2]);
            java.time.Instant end = java.time.Instant.parse(args[3]);
            int interval = Integer.parseInt(args[4]);
            HistoricalScreening.run(symbol, start, end, interval);
            System.exit(0);
        } else if ("historical".equals(mode)) {
            if (args.length < 3) {
                System.err.println("Usage: historical <symbol> <ISO_TIMESTAMP>");
                System.exit(1);
            }
            String symbol = args[1];
            java.time.Instant asOf = java.time.Instant.parse(args[2]);
            MarketDataSnapshot service = new MarketDataSnapshot();
            try {
                System.out.println("[Main] Fetching historical snapshot for " + symbol + " as of " + asOf + "...");
                service.saveHistoricalSnapshot(symbol, asOf);
            } catch (Exception e) {
                System.err.println("[Main] Historical snapshot failed: " + e.getMessage());
                e.printStackTrace();
            } finally {
                service.shutdown();
                System.exit(0);
            }
        } else if ("scheduler".equals(mode)) {
            Scheduler scheduler = new Scheduler(symbols);
            // Add shutdown hook
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("[Main] Shutdown signal received.");
                scheduler.shutdown();
            }));
            scheduler.start();
            // Block main thread
            Thread.sleep(Long.MAX_VALUE);
        } else {
            MarketDataSnapshot service = new MarketDataSnapshot();
            for (String sym : symbols) {
                try {
                    System.out.println("[Main] Fetching snapshot for " + sym + "...");
                    service.saveSnapshot(sym, null);
                } catch (Exception e) {
                    System.err.println("[Main] Snapshot failed for " + sym + ": " + e.getMessage());
                    e.printStackTrace();
                }
            }
            service.shutdown();
            System.exit(0);
        }
    }
}
