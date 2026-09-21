package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * State-code emitter - design state_machine_design_2026-09-11.md
 *
 * Subscribes to Binance @aggTrade for a single symbol. Maintains a 2h rolling
 * tick buffer plus session CVD / VWAP accumulators. Emits a flow-state code
 * every 60 seconds. Writes mts/runtime/state_code.json atomically and appends
 * one line per fired transition to system/session_end_logs.md.
 *
 * Codes:    A, A>S, A>L, S, S>L, L, L>S
 * Signals:  net_delta_1m, last_3_delta, volume_ratio, cvd_slope, price_vs_vwap
 * Skip:     fewer than 3 available signals -> no state evaluation
 * Hysteresis: 2 consecutive emit ticks with the target condition
 */
public class StateCodeEmitter extends WebSocketClient {

    private static final int  RECONNECT_DELAY_MS = 5_000;
    private static final long EMIT_PERIOD_SEC = 60L;
    private static final long TICK_BUFFER_MS = 2L * 60L * 60L * 1000L;
    private static final int  RING_SIZE = 30;
    private static final int  CVD_SAMPLES = 40;
    private static final int  CVD_MIN_SAMPLES = 10;
    private static final int  MIN_SIGNALS = 3;
    private static final double VOL_RATIO_THRESHOLD = 2.0;
    private static final double VWAP_NEUTRAL_PCT = 0.05;

    private final String symbol;
    private final ObjectMapper mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
    private final ScheduledExecutorService reconnectExecutor;
    private final ScheduledExecutorService emitExecutor;
    private final AtomicBoolean emitScheduled = new AtomicBoolean(false);
    private volatile boolean shuttingDown = false;
    private volatile long lastTickMs = 0L;
    private volatile double lastPrice = 0.0;
    private final java.util.concurrent.atomic.AtomicLong msgCount = new java.util.concurrent.atomic.AtomicLong(0);

    private static final Object BUFFER_LOCK = new Object();
    private final Deque<Tick> ticks = new ArrayDeque<>();
    private long sessionDayStartMs = -1L;
    private double sessionCvd = 0.0;
    private double sessionCumPV = 0.0;
    private double sessionCumVol = 0.0;

    private final Deque<Double> cvdSeries = new ArrayDeque<>();
    private long cvdRingDayStartMs = -1L;

    // T028 test seam: package-private override for CVD-ring day check.
    // Real runtime leaves this at -1 (uses System.currentTimeMillis).
    volatile long nowMsOverride = -1L;

    long nowMs() {
        long o = nowMsOverride;
        return o >= 0 ? o : System.currentTimeMillis();
    }

    private String currentState = "A";
    private String pendingState = null;
    private int pendingCount = 0;
    private int quietCount = 0;
    private long stateSinceMs;
    private final Deque<String> transitionChain = new ArrayDeque<>();

    public StateCodeEmitter(String symbol) throws Exception {
        super(new URI("wss://fstream.binance.com/market/ws/" + symbol.toLowerCase() + "@aggTrade"));
        this.symbol = symbol;
        this.stateSinceMs = System.currentTimeMillis();
        this.reconnectExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "state-reconnect-" + symbol);
            t.setDaemon(true);
            return t;
        });
        this.emitExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "state-emit-" + symbol);
            t.setDaemon(true);
            return t;
        });
        setConnectionLostTimeout(30);
        restoreStateFromDisk();
        if (transitionChain.isEmpty()) transitionChain.addLast(currentState);
    }

    @Override
    public void onOpen(ServerHandshake h) {
        System.out.println("[StateCode WS] Connected: " + symbol);
        if (emitScheduled.compareAndSet(false, true)) {
            emitExecutor.scheduleAtFixedRate(this::safeEmit,
                    EMIT_PERIOD_SEC, EMIT_PERIOD_SEC, TimeUnit.SECONDS);
        }
    }

    @Override
    public void onMessage(String message) {
        long msgN = msgCount.incrementAndGet();
        if (msgN == 1) {
            System.out.println("[StateCode WS] first message received");
        } else if (msgN % 1000 == 0) {
            System.out.println("[StateCode WS] msg#" + msgN + " total");
        }
        try {
            JsonNode root = mapper.readTree(message);
            if (!root.has("e") || !"aggTrade".equals(root.get("e").asText())) return;
            long T = root.get("T").asLong();
            double p = root.get("p").asDouble();
            double q = root.get("q").asDouble();
            boolean buyerMaker = root.get("m").asBoolean();
            Tick t = new Tick(T, p, q, buyerMaker);
            synchronized (BUFFER_LOCK) {
                ticks.addLast(t);
                long cutoff = T - TICK_BUFFER_MS;
                while (!ticks.isEmpty() && ticks.peekFirst().T < cutoff) ticks.pollFirst();
                applySessionAccumulator(t);
            }
            lastTickMs = T;
            lastPrice = p;
        } catch (Exception e) {
            System.err.println("[StateCode WS] Parse error (" + symbol + "): " + e.getMessage());
        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        System.out.println("[StateCode WS] Closed: " + symbol + " | " + reason);
        if (!shuttingDown) scheduleReconnect();
    }

    @Override
    public void onError(Exception ex) {
        System.err.println("[StateCode WS] Error (" + symbol + "): " + ex.getMessage());
    }

    private void scheduleReconnect() {
        reconnectExecutor.schedule(() -> {
            try {
                System.out.println("[StateCode WS] Reconnecting: " + symbol);
                reconnectBlocking();
            } catch (Exception e) {
                System.err.println("[StateCode WS] Reconnect failed (" + symbol + "): " + e.getMessage());
            }
        }, RECONNECT_DELAY_MS, TimeUnit.MILLISECONDS);
    }

    public void shutdown() {
        shuttingDown = true;
        reconnectExecutor.shutdownNow();
        emitExecutor.shutdownNow();
        close();
    }

    private void applySessionAccumulator(Tick t) {
        long dayStart = utcDayStart(t.T);
        if (sessionDayStartMs != dayStart) {
            sessionDayStartMs = dayStart;
            sessionCvd = 0.0;
            sessionCumPV = 0.0;
            sessionCumVol = 0.0;
        }
        double signed = t.buyerMaker ? -t.qty : t.qty;
        sessionCvd += signed;
        sessionCumPV += t.price * t.qty;
        sessionCumVol += t.qty;
    }

    private static long utcDayStart(long epochMs) {
        return Instant.ofEpochMilli(epochMs).atZone(ZoneOffset.UTC)
                .truncatedTo(ChronoUnit.DAYS).toInstant().toEpochMilli();
    }

    private static class Tick {
        final long T; final double price; final double qty; final boolean buyerMaker;
        Tick(long T, double price, double qty, boolean buyerMaker) {
            this.T = T; this.price = price; this.qty = qty; this.buyerMaker = buyerMaker;
        }
    }

    private enum Dir { BEARISH, BULLISH, NEUTRAL }

    private void safeEmit() {
        try { evaluateAndEmit(); }
        catch (Exception e) {
            System.err.println("[StateCode] emit error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void evaluateAndEmit() throws Exception {
        long nowT;
        double sessionCvdSnap, sessionCumPVSnap, sessionCumVolSnap;
        List<Tick> snapshot = new ArrayList<>();
        synchronized (BUFFER_LOCK) {
            snapshot.addAll(ticks);
            sessionCvdSnap = sessionCvd;
            sessionCumPVSnap = sessionCumPV;
            sessionCumVolSnap = sessionCumVol;
        }
        nowT = lastTickMs > 0 ? lastTickMs : System.currentTimeMillis();

        Dir nd1m = computeNetDelta1m(snapshot, nowT);
        Dir l3d = computeLast3Delta(snapshot, nowT);
        Dir vr = computeVolumeRatio(snapshot, nowT);
        Dir cvd = computeCvdSlope(sessionCvdSnap);
        Dir pvv = computePriceVsVwap(lastPrice, sessionCumPVSnap, sessionCumVolSnap);

        Object[] signals = new Object[]{nd1m, l3d, vr, cvd, pvv};

        int bearish = 0, bullish = 0, available = 0;
        for (Object o : signals) {
            if (o == null) continue;
            available++;
            if (o == Dir.BEARISH) bearish++;
            else if (o == Dir.BULLISH) bullish++;
        }

        long nowMs = System.currentTimeMillis();
        String firedFrom = null, firedTo = null, trigger = null;

        if (available >= MIN_SIGNALS) {
            String target = nextTarget(currentState, bearish, bullish);
            if (target != null && !target.equals(currentState)) {
                if (target.equals(pendingState)) pendingCount++;
                else { pendingState = target; pendingCount = 1; }
                if (pendingCount >= 2) {
                    firedFrom = currentState;
                    firedTo = target;
                    trigger = buildTrigger(signals);
                    currentState = target;
                    stateSinceMs = nowMs;
                    pendingState = null;
                    pendingCount = 0;
                    quietCount = 0;
                    transitionChain.addLast(currentState);
                    while (transitionChain.size() > RING_SIZE) transitionChain.pollFirst();
                }
            } else {
                pendingState = null;
                pendingCount = 0;
            }

            if (firedFrom == null) {
                if (bearish < 3 && bullish < 3) quietCount++;
                else quietCount = 0;

                if (quietCount >= 2 && !"A".equals(currentState)) {
                    firedFrom = currentState;
                    firedTo = "A";
                    trigger = "quiet-decay";
                    currentState = "A";
                    stateSinceMs = nowMs;
                    quietCount = 0;
                    pendingState = null;
                    pendingCount = 0;
                    transitionChain.addLast(currentState);
                    while (transitionChain.size() > RING_SIZE) transitionChain.pollFirst();
                }
            }
        }

        System.out.println("[StateCode] emit  state=" + currentState
                + " B=" + bearish + " Bl=" + bullish
                + " av=" + available + " ticks=" + snapshot.size());

        writeStateJson(signals, bearish, bullish, available, nowMs);

        if (firedFrom != null) {
            appendTransitionLog(firedFrom, firedTo, bearish, bullish, trigger, nowMs);
        }
    }

    private Dir computeNetDelta1m(List<Tick> snap, long nowT) {
        if (snap.isEmpty()) return null;
        long oneMinAgo = nowT - 60_000L;
        double s = 0.0;
        for (Tick t : snap) if (t.T >= oneMinAgo) s += (t.buyerMaker ? -t.qty : t.qty);
        return s > 0 ? Dir.BULLISH : s < 0 ? Dir.BEARISH : Dir.NEUTRAL;
    }

    private Dir computeLast3Delta(List<Tick> snap, long nowT) {
        if (snap.isEmpty()) return null;
        long b0 = nowT - 180_000L, b1 = nowT - 120_000L, b2 = nowT - 60_000L;
        double[] buckets = new double[3];
        boolean[] seen = new boolean[3];
        for (Tick t : snap) {
            double s = t.buyerMaker ? -t.qty : t.qty;
            if (t.T >= b2) { buckets[2] += s; seen[2] = true; }
            else if (t.T >= b1) { buckets[1] += s; seen[1] = true; }
            else if (t.T >= b0) { buckets[0] += s; seen[0] = true; }
        }
        if (!seen[0] || !seen[1] || !seen[2]) return null;
        if (buckets[0] < 0 && buckets[1] < 0 && buckets[2] < 0) return Dir.BEARISH;
        if (buckets[0] > 0 && buckets[1] > 0 && buckets[2] > 0) return Dir.BULLISH;
        return Dir.NEUTRAL;
    }

    private Dir computeVolumeRatio(List<Tick> snap, long nowT) {
        if (snap.isEmpty()) return null;
        long oneMinAgo = nowT - 60_000L;
        long window30Start = nowT - 30L * 60_000L - 60_000L;
        double cur1mVol = 0.0, net1m = 0.0;
        double[] volPerMin = new double[30];
        int[] seenMin = new int[30];
        for (Tick t : snap) {
            double signed = t.buyerMaker ? -t.qty : t.qty;
            if (t.T >= oneMinAgo) { cur1mVol += t.qty; net1m += signed; }
            else if (t.T >= window30Start) {
                int idx = (int) ((t.T - window30Start) / 60_000L);
                if (idx >= 0 && idx < 30) { volPerMin[idx] += t.qty; seenMin[idx] = 1; }
            }
        }
        double sum = 0.0; int cnt = 0;
        for (int i = 0; i < 30; i++) if (seenMin[i] == 1) { sum += volPerMin[i]; cnt++; }
        if (cnt < 10) return null;
        double baseline = sum / cnt;
        if (baseline <= 0) return null;
        double ratio = cur1mVol / baseline;
        if (ratio < VOL_RATIO_THRESHOLD) return Dir.NEUTRAL;
        return net1m > 0 ? Dir.BULLISH : net1m < 0 ? Dir.BEARISH : Dir.NEUTRAL;
    }

    private Dir computeCvdSlope(double sessionCvdSnap) {
        long ringDay = utcDayStart(nowMs());
        if (cvdRingDayStartMs != ringDay) { cvdSeries.clear(); cvdRingDayStartMs = ringDay; }
        cvdSeries.addLast(sessionCvdSnap);
        while (cvdSeries.size() > CVD_SAMPLES) cvdSeries.pollFirst();
        if (cvdSeries.size() < CVD_MIN_SAMPLES) return null;
        int n = cvdSeries.size();
        int half = n / 2;
        List<Double> lst = new ArrayList<>(cvdSeries);
        double recent = 0, older = 0;
        for (int i = n - half; i < n; i++) recent += lst.get(i);
        for (int i = 0; i < half; i++) older += lst.get(i);
        recent /= half; older /= half;
        double denom = Math.max(Math.abs(older), 1.0);
        double change = (recent - older) / denom;
        if (change > 0.02) return Dir.BULLISH;
        if (change < -0.02) return Dir.BEARISH;
        return Dir.NEUTRAL;
    }

    private Dir computePriceVsVwap(double price, double cumPV, double cumVol) {
        if (cumVol <= 0 || price <= 0) return null;
        double vwap = cumPV / cumVol;
        double dev = (price - vwap) / vwap * 100.0;
        if (Math.abs(dev) <= VWAP_NEUTRAL_PCT) return Dir.NEUTRAL;
        return dev > 0 ? Dir.BULLISH : Dir.BEARISH;
    }

    private String nextTarget(String state, int b, int bl) {
        switch (state) {
            case "A":
                if (b >= 2 && bl <= 1) return "A>S";
                if (bl >= 2 && b <= 1) return "A>L";
                return null;
            case "A>S":
                if (b >= 3) return "S";
                return null;
            case "A>L":
                if (bl >= 3) return "L";
                return null;
            case "S":
                if (bl >= 3) return "S>L";
                return null;
            case "L":
                if (b >= 3) return "L>S";
                return null;
            case "S>L":
                if (bl >= 3) return "L";
                if (b >= 3) return "S";
                return null;
            case "L>S":
                if (b >= 3) return "S";
                if (bl >= 3) return "L";
                return null;
        }
        return null;
    }

    private String buildTrigger(Object[] signals) {
        String[] names = {"net_delta_1m", "last_3_delta", "volume_ratio", "cvd_slope", "price_vs_vwap"};
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < signals.length; i++) {
            if (signals[i] == null) continue;
            if (sb.length() > 0) sb.append(",");
            sb.append(names[i]);
        }
        return sb.toString();
    }

    private void writeStateJson(Object[] signals, int bearish, int bullish, int available, long nowMs) throws Exception {
        ObjectNode root = mapper.createObjectNode();
        root.put("timestamp_utc", Instant.ofEpochMilli(nowMs).toString());
        root.put("state", currentState);
        root.put("bearish_count", bearish);
        root.put("bullish_count", bullish);
        root.put("available_signals", available);
        root.put("seconds_in_state", (nowMs - stateSinceMs) / 1000);
        root.put("last_transition_utc",
                transitionChain.size() > 1 ? Instant.ofEpochMilli(stateSinceMs).toString() : null);
        ArrayNode chain = root.putArray("transition_chain_15m");
        int start = Math.max(0, transitionChain.size() - 15);
        int i = 0;
        for (String s : transitionChain) if (i++ >= start) chain.add(s);
        root.put("weekend", isWeekend(nowMs));
        // B057: persist session accumulators so mid-day restarts do not
        // silently shrink the cvd_slope and price_vs_vwap windows.
        root.put("session_day_start_ms", sessionDayStartMs);
        root.put("session_cvd",           sessionCvd);
        root.put("session_cum_pv",        sessionCumPV);
        root.put("session_cum_vol",       sessionCumVol);

        ObjectNode sig = root.putObject("signals");
        String[] names = {"net_delta_1m", "last_3_delta", "volume_ratio", "cvd_slope", "price_vs_vwap"};
        for (int k = 0; k < signals.length; k++) {
            Object o = signals[k];
            if (o == null) sig.putNull(names[k]);
            else sig.put(names[k], ((Dir) o).name().toLowerCase());
        }

        Path dir = Paths.get("MyTradingSys", "mts", "runtime");
        Files.createDirectories(dir);
        Path target = dir.resolve("state_code.json");
        Path tmp = dir.resolve("state_code.json.tmp");
        mapper.writeValue(tmp.toFile(), root);
        Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
    }

    private static boolean isWeekend(long epochMs) {
        int dow = Instant.ofEpochMilli(epochMs).atZone(ZoneOffset.UTC).getDayOfWeek().getValue();
        return dow == 6 || dow == 7;
    }

    private void appendTransitionLog(String from, String to, int b, int bl, String trigger, long nowMs) {
        Path dir = Paths.get("MyTradingSys", "system");
        Path log = dir.resolve("session_end_logs.md");
        String line = Instant.ofEpochMilli(nowMs).toString()
                + "  " + from + " -> " + to
                + "  bearish=" + b + " bullish=" + bl
                + "  trigger=" + (trigger == null ? "unknown" : trigger)
                + System.lineSeparator();
        try {
            Files.createDirectories(dir);
            Files.write(log, line.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (Exception e) {
            System.err.println("[StateCode] log append failed: " + e.getMessage());
        }
    }

    private void restoreStateFromDisk() {
        Path p = Paths.get("MyTradingSys", "mts", "runtime", "state_code.json");
        if (!Files.exists(p)) return;
        try {
            JsonNode root = mapper.readTree(p.toFile());
            if (root.has("state")) {
                String s = root.get("state").asText();
                if (s != null && !s.isEmpty()) currentState = s;
            }
            if (root.has("transition_chain_15m")) {
                for (JsonNode n : root.get("transition_chain_15m")) transitionChain.addLast(n.asText());
            }
            if (root.has("timestamp_utc")) {
                try { stateSinceMs = Instant.parse(root.get("timestamp_utc").asText()).toEpochMilli(); }
                catch (Exception ignored) { stateSinceMs = System.currentTimeMillis(); }
            }
            // B057: restore accumulators
            if (root.has("session_day_start_ms")) sessionDayStartMs = root.get("session_day_start_ms").asLong();
            if (root.has("session_cvd"))           sessionCvd         = root.get("session_cvd").asDouble();
            if (root.has("session_cum_pv"))        sessionCumPV       = root.get("session_cum_pv").asDouble();
            if (root.has("session_cum_vol"))       sessionCumVol      = root.get("session_cum_vol").asDouble();
            System.out.println("[StateCode] Restored state from disk: " + currentState);
        } catch (Exception e) {
            System.err.println("[StateCode] restore failed: " + e.getMessage());
        }
    }
}
