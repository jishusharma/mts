package datafeed;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

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
    static final List<String> LIQ_LOG_SYMBOLS = List.of("BTCUSDT", "ETHUSDT");

    static final Function<String, BinanceLiquidationAccumulator> DEFAULT_LIQ_FACTORY = sym -> {
        try {
            return new BinanceLiquidationAccumulator(sym);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    };

    /** Builds and connects one accumulator per symbol; a failing symbol logs one line and is skipped. */
    static List<BinanceLiquidationAccumulator> startLiquidationLogs(
            List<String> syms, Function<String, BinanceLiquidationAccumulator> factory) {
        List<BinanceLiquidationAccumulator> started = new ArrayList<>();
        for (String sym : syms) {
            try {
                BinanceLiquidationAccumulator acc = factory.apply(sym);
                acc.connect();
                started.add(acc);
            } catch (Throwable t) {
                System.err.println("[Main] Liquidation log not started for " + sym + ": " + t);
            }
        }
        return started;
    }

    /** Shuts down every accumulator; one failure never skips the rest. */
    static void closeAll(List<BinanceLiquidationAccumulator> accs) {
        for (BinanceLiquidationAccumulator acc : accs) {
            try {
                acc.shutdown();
            } catch (Throwable t) {
                System.err.println("[Main] Liquidation log shutdown failed: " + t);
            }
        }
    }

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
            // Liquidation event log (runtime_data/liq_events); connect() is async, failures never stop the emitter.
            final List<BinanceLiquidationAccumulator> liqLogs = startLiquidationLogs(LIQ_LOG_SYMBOLS, DEFAULT_LIQ_FACTORY);
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("[Main] Shutdown signal received.");
                emitter.shutdown();
                closeAll(liqLogs);
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
