package datafeed;

import java.time.Duration;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Drift-free daily scheduler that runs at 00:05 UTC.
 * Supports multiple symbols and integrates the full snapshot pipeline.
 */
public class Scheduler {

    private final ScheduledExecutorService executor;
    private final List<String> symbols;
    private final MarketDataSnapshot snapshotService;
    private final BinanceLiquidationAccumulator liqBtc;
    private final BinanceLiquidationAccumulator liqEth;
    private volatile boolean running = false;

    public Scheduler(List<String> symbols) throws Exception {
        this.symbols = symbols;
        this.executor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "snapshot-scheduler");
            t.setDaemon(false);
            return t;
        });
        this.snapshotService = new MarketDataSnapshot();
        this.liqBtc = symbols.contains("BTCUSDT") ? new BinanceLiquidationAccumulator("BTCUSDT") : null;
        this.liqEth = symbols.contains("ETHUSDT") ? new BinanceLiquidationAccumulator("ETHUSDT") : null;
    }

    public void start() {
        running = true;
        if (liqBtc != null) liqBtc.connect();
        if (liqEth != null) liqEth.connect();

        scheduleNextRun();
        System.out.println("[Scheduler] Started. Next run at 00:05 UTC.");
    }

    private void scheduleNextRun() {
        ZonedDateTime now = ZonedDateTime.now(ZoneOffset.UTC);
        ZonedDateTime next = now.withHour(0).withMinute(5).withSecond(0).withNano(0);
        if (!now.isBefore(next)) {
            next = next.plusDays(1);
        }
        long delayMs = Duration.between(now, next).toMillis();
        System.out.println("[Scheduler] Next run in " + delayMs + " ms (" + next + ")");

        executor.schedule(() -> {
            try {
                runSnapshotCycle();
            } finally {
                if (running) scheduleNextRun();
            }
        }, delayMs, TimeUnit.MILLISECONDS);
    }

    private void runSnapshotCycle() {
        System.out.println("[Scheduler] Running snapshot cycle at " + ZonedDateTime.now(ZoneOffset.UTC));
        for (String sym : symbols) {
            try {
                BinanceLiquidationAccumulator liq = sym.equals("BTCUSDT") ? liqBtc : liqEth;
                snapshotService.saveSnapshot(sym, liq);
            } catch (Exception e) {
                System.err.println("[Scheduler] Failed snapshot for " + sym + ": " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    public void shutdown() {
        running = false;
        executor.shutdownNow();
        if (liqBtc != null) liqBtc.shutdown();
        if (liqEth != null) liqEth.shutdown();
        snapshotService.shutdown();
        System.out.println("[Scheduler] Shutdown complete.");
    }
}