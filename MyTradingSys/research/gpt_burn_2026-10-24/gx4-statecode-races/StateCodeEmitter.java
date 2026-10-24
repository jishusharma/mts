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
 * every 60 seconds. Writes mts/runtime/state_code.json atomically.
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
    volatile boolean shuttingDown = false;
    private volatile long lastTickMs = 0L;
    private volatile double lastPrice = 0.0;
    private final java.util.concurrent.atomic.AtomicLong msgCount = new java.util.concurrent.atomic.AtomicLong(0);

    private static final Object BUFFER_LOCK = new Object();
    private final Deque<Tick> ticks = new ArrayDeque<>();
    private long sessionDayStartMs = -1L;
    private double sessionCvd = 0.0;
    private double sessionCumPV = 0.0;
    private double sessionCumVol = 0.0;
    private long acceptedBoundaryMs = -1L;

    private final Deque<Double> cvdSeries = new ArrayDeque<>();
    private long cvdRingDayStartMs = -1L;
    private long cvdRingEpoch = 0L;

    // Accumulator backfill (audit M1/M2, OURS). The three session sums are VALID only after a complete 1m-kline
    // backfill (UTC day start .. last closed minute boundary M) stitched to the ticks seen since the connect. Until then
    // (start, WS close, failed or incomplete backfill) they are INVALID: ticks are buffered, not summed, the two signals
    // that use the sums are null and the emitted state is "INVALID". All fields below are guarded by BUFFER_LOCK.
    private static final long SETTLE_MS = 2_000L;           // let the exchange finalise the just-closed minute
    private static final long CONNECT_SLACK_MS = 5_000L;    // M must be this far after the connect (clock skew)
    private static final long FAIL_RETRY_MS = 30_000L;
    private static final long PENDING_KEEP_MS = 5L * 60_000L;
    private static final int  KLINE_LIMIT = 1500;           // fapi max rows; one UTC day is <= 1440 bars
    private boolean accValid = false;
    private String accReason = "startup_no_backfill";
    private long accEpoch = 0L;                              // bumped on every invalidate / completion
    private long connectedAtMs = Long.MAX_VALUE;             // local time of the latest onOpen; MAX = not connected
    private long connectEpoch = 0L;
    private final Deque<Tick> pendingTicks = new ArrayDeque<>();
    volatile long retryDelayMs = FAIL_RETRY_MS;
    private final AtomicBoolean backfillQueued = new AtomicBoolean(false);
    private final ScheduledExecutorService backfillExecutor = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread t = new Thread(r, "state-backfill");
        t.setDaemon(true);
        return t;
    });
    private final Object sourceLock = new Object();
    private KlineSource defaultSource;
    private static final java.util.Set<String> VALID_STATES =
            java.util.Set.of("A", "A>S", "A>L", "S", "S>L", "L", "L>S");

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

    /** Seam for the 1m-kline backfill (no network in tests). */
    interface KlineSource { JsonNode fetch(String symbol, long startMs, long endMs) throws Exception; }

    final Path stateFile;
    final KlineSource klineSource;

    public StateCodeEmitter(String symbol) throws Exception {
        this(symbol, Paths.get("MyTradingSys", "runtime", "state_code.json"), null);
    }

    StateCodeEmitter(String symbol, Path stateFile, KlineSource klineSource) throws Exception {
        super(new URI("wss://fstream.binance.com/market/ws/" + symbol.toLowerCase() + "@aggTrade"));
        this.symbol = symbol;
        this.stateFile = stateFile;
        this.klineSource = klineSource;
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
        onStreamOpen(nowMs());
        requestBackfill(0L);
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
                if (accValid) {
                    if (utcDayStart(T) != sessionDayStartMs || T >= acceptedBoundaryMs) {
                        applySessionAccumulator(t);
                    }
                } else {
                    // Gap or no backfill yet: hold the tick for the seam, keep only what a later backfill can need.
                    pendingTicks.addLast(t);
                    long keep = T - PENDING_KEEP_MS;
                    while (!pendingTicks.isEmpty() && pendingTicks.peekFirst().T < keep) pendingTicks.pollFirst();
                }
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
        onStreamClosed("ws_closed code=" + code);
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
        backfillExecutor.shutdownNow();
        close();
    }

    private void applySessionAccumulator(Tick t) {
        long dayStart = utcDayStart(t.T);
        if (sessionDayStartMs != dayStart) {
            sessionDayStartMs = dayStart;
            acceptedBoundaryMs = -1L;
            sessionCvd = 0.0;
            sessionCumPV = 0.0;
            sessionCumVol = 0.0;
        }
        double signed = t.buyerMaker ? -t.qty : t.qty;
        sessionCvd += signed;
        sessionCumPV += t.price * t.qty;
        sessionCumVol += t.qty;
    }

    /**
     * A new socket: ticks seen so far are history. The next backfill is only accepted for a boundary M that lies after
     * this connect (plus slack), so every trade with T >= M has been received on this socket.
     */
    void onStreamOpen(long openedAtMs) {
        synchronized (BUFFER_LOCK) {
            connectedAtMs = openedAtMs;
            connectEpoch++;
            pendingTicks.clear();
            invalidateLocked("waiting_for_backfill_after_connect");
        }
    }

    /** Socket closed: from here a gap exists, the sums are no longer a session value. */
    void onStreamClosed(String why) {
        synchronized (BUFFER_LOCK) {
            connectedAtMs = Long.MAX_VALUE;
            connectEpoch++;
            pendingTicks.clear();
            invalidateLocked(why);
        }
    }

    private void invalidateLocked(String reason) {
        accValid = false;
        accReason = reason;
        accEpoch++;
        sessionCvd = 0.0;
        sessionCumPV = 0.0;
        sessionCumVol = 0.0;
        sessionDayStartMs = -1L;
        acceptedBoundaryMs = -1L;
    }

    private KlineSource source() {
        if (klineSource != null) return klineSource;
        synchronized (sourceLock) {
            if (defaultSource == null) {
                final BinanceClient client = new BinanceClient();
                defaultSource = (sym, startMs, endMs) -> client.klinesRange(sym, "1m", startMs, endMs, KLINE_LIMIT);
            }
            return defaultSource;
        }
    }

    private boolean failBackfill(String reason, long retryMs) {
        synchronized (BUFFER_LOCK) {
            if (!accValid) accReason = reason;
        }
        retryDelayMs = retryMs;
        System.err.println("[StateCode] backfill not complete (" + symbol + "): " + reason + " | retry in " + retryMs + " ms");
        return false;
    }

    /**
     * Re-seed the session sums from fapi 1m klines of CLOSED bars: UTC day start .. last closed minute boundary M,
     * stitched to the ticks received since the connect (T >= M only, so nothing is counted twice and nothing is missing).
     * Any other outcome (HTTP/JSON error, timeout, wrong bar count, duplicate/non-monotonic openTime, bad row, reconnect or
     * day change during the call) leaves the accumulators INVALID. Returns true when the sums are valid.
     */
    boolean backfillNow() {
        long now = nowMs();
        long dayStart = utcDayStart(now);
        long m = Math.max(dayStart, ((now - SETTLE_MS) / 60_000L) * 60_000L);
        long epoch;
        synchronized (BUFFER_LOCK) {
            if (accValid) return true;
            epoch = connectEpoch;
            if (connectedAtMs == Long.MAX_VALUE) {
                retryDelayMs = FAIL_RETRY_MS;
                return false;
            }
            long needM = connectedAtMs + CONNECT_SLACK_MS;
            if (m < needM) {
                long b = ((needM + 59_999L) / 60_000L) * 60_000L;
                accReason = "waiting_for_minute_boundary";
                retryDelayMs = Math.max(1_000L, b + SETTLE_MS - now + 250L);
                return false;
            }
        }

        long expected = (m - dayStart) / 60_000L;
        double cvd = 0.0, pv = 0.0, vol = 0.0;
        if (expected > 0) {
            JsonNode k;
            try {
                k = source().fetch(symbol, dayStart, m - 1);
            } catch (Throwable ex) {
                return failBackfill("backfill_error: " + ex.getClass().getSimpleName() + " " + ex.getMessage(), FAIL_RETRY_MS);
            }
            if (k == null || !k.isArray()) return failBackfill("backfill_bad_response", FAIL_RETRY_MS);
            if (k.size() != expected) {
                return failBackfill("backfill_bar_count " + k.size() + " expected " + expected, FAIL_RETRY_MS);
            }
            for (int i = 0; i < k.size(); i++) {
                JsonNode r = k.get(i);
                if (r == null || !r.isArray() || r.size() < 10) return failBackfill("backfill_malformed_row " + i, FAIL_RETRY_MS);
                if (r.get(0).asLong(-1L) != dayStart + i * 60_000L) {
                    return failBackfill("backfill_open_time_mismatch at bar " + i, FAIL_RETRY_MS);
                }
                double v, qv, tb;
                try {
                    v = Double.parseDouble(r.get(5).asText());
                    qv = Double.parseDouble(r.get(7).asText());
                    tb = Double.parseDouble(r.get(9).asText());
                } catch (NumberFormatException nfe) {
                    return failBackfill("backfill_unparseable_row " + i, FAIL_RETRY_MS);
                }
                if (!(v >= 0) || !(qv >= 0) || !(tb >= 0) || tb > v + 1e-6
                        || Double.isInfinite(v) || Double.isInfinite(qv)) {
                    return failBackfill("backfill_bad_values at bar " + i, FAIL_RETRY_MS);
                }
                cvd += 2.0 * tb - v;
                vol += v;
                pv += qv;
            }
        }

        synchronized (BUFFER_LOCK) {
            if (accValid) return true;
            if (epoch != connectEpoch) return failBackfill("reconnected_during_backfill", 1_000L);
            if (utcDayStart(nowMs()) != dayStart) return failBackfill("day_rolled_during_backfill", 1_000L);
            sessionDayStartMs = dayStart;
            acceptedBoundaryMs = m;
            sessionCvd = cvd;
            sessionCumPV = pv;
            sessionCumVol = vol;
            for (Tick t : pendingTicks) if (t.T >= m) applySessionAccumulator(t);
            pendingTicks.clear();
            accValid = true;
            accReason = "ok";
            accEpoch++;
        }
        System.out.println("[StateCode] backfill ok (" + symbol + "): " + expected + " bars to "
                + Instant.ofEpochMilli(m) + " cvd=" + cvd + " vol=" + vol);
        return true;
    }

    private void requestBackfill(long delayMs) {
        if (shuttingDown) return;
        if (!backfillQueued.compareAndSet(false, true)) return;
        try {
            backfillExecutor.schedule(() -> {
                backfillQueued.set(false);
                boolean ok = false;
                try { ok = backfillNow(); }
                catch (Throwable t) { failBackfill("backfill_exception: " + t, FAIL_RETRY_MS); }
                if (!ok && !shuttingDown) requestBackfill(retryDelayMs);
            }, Math.max(0L, delayMs), TimeUnit.MILLISECONDS);
        } catch (java.util.concurrent.RejectedExecutionException rex) {
            backfillQueued.set(false);
        }
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

    void evaluateAndEmit() throws Exception {
        long nowT;
        double sessionCvdSnap, sessionCumPVSnap, sessionCumVolSnap;
        boolean validSnap;
        String reasonSnap;
        long dayStartSnap, epochSnap;
        List<Tick> snapshot = new ArrayList<>();
        synchronized (BUFFER_LOCK) {
            snapshot.addAll(ticks);
            sessionCvdSnap = sessionCvd;
            sessionCumPVSnap = sessionCumPV;
            sessionCumVolSnap = sessionCumVol;
            validSnap = accValid;
            reasonSnap = accReason;
            dayStartSnap = sessionDayStartMs;
            epochSnap = accEpoch;
        }
        nowT = lastTickMs > 0 ? lastTickMs : System.currentTimeMillis();

        Dir nd1m = computeNetDelta1m(snapshot, nowT);
        Dir l3d = computeLast3Delta(snapshot, nowT);
        Dir vr = computeVolumeRatio(snapshot, nowT);
        // Fail closed: the two accumulator signals exist only on a complete backfill. The slope ring restarts on every
        // invalidate and on backfill completion so the jump to the backfilled value cannot read as slope.
        if (epochSnap != cvdRingEpoch) { cvdSeries.clear(); cvdRingEpoch = epochSnap; }
        Dir cvd = null, pvv = null;
        if (validSnap) {
            cvd = computeCvdSlope(sessionCvdSnap);
            pvv = computePriceVsVwap(lastPrice, sessionCumPVSnap, sessionCumVolSnap);
        }

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

        if (!validSnap) {
            pendingState = null;
            pendingCount = 0;
            quietCount = 0;
        } else if (available >= MIN_SIGNALS) {
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
                + " av=" + available + " ticks=" + snapshot.size()
                + (validSnap ? "" : " INVALID(" + reasonSnap + ")"));

        synchronized (BUFFER_LOCK) {
            // Reconcile the computed snapshot with invalidation and publication under one lock.
            boolean publishValid = validSnap && accValid && epochSnap == accEpoch;
            String publishReason = publishValid ? reasonSnap : accReason;
            long publishDay = publishValid ? dayStartSnap : -1L;
            if (!publishValid) {
                signals[3] = null;
                signals[4] = null;
            }
            writeStateJson(signals, bearish, bullish, available, nowMs, publishValid, publishReason, publishDay,
                    publishValid ? sessionCvd : 0.0, publishValid ? sessionCumPV : 0.0,
                    publishValid ? sessionCumVol : 0.0);
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

    private void writeStateJson(Object[] signals, int bearish, int bullish, int available, long nowMs,
                                boolean valid, String reason, long dayStart,
                                double cvd, double cumPV, double cumVol) throws Exception {
        ObjectNode root = mapper.createObjectNode();
        root.put("timestamp_utc", Instant.ofEpochMilli(nowMs).toString());
        // Readers match ^S / ^L on "state"; INVALID matches neither, so no adverse-flow alert fires on partial data.
        root.put("state", valid ? currentState : "INVALID");
        root.put("state_last_valid", currentState);
        root.put("session_accumulators_valid", valid);
        root.put("session_accumulators_reason", valid ? "ok" : (reason == null || reason.isEmpty() ? "unknown" : reason));
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
        // Session sums are informational: never restored (a restart re-seeds them from klines; B057 replaced).
        // While INVALID they are null so a partial value is never shown as a session value.
        if (valid) {
            root.put("session_day_start_ms", dayStart);
            root.put("session_cvd",           cvd);
            root.put("session_cum_pv",        cumPV);
            root.put("session_cum_vol",       cumVol);
        } else {
            root.putNull("session_day_start_ms");
            root.putNull("session_cvd");
            root.putNull("session_cum_pv");
            root.putNull("session_cum_vol");
        }

        ObjectNode sig = root.putObject("signals");
        String[] names = {"net_delta_1m", "last_3_delta", "volume_ratio", "cvd_slope", "price_vs_vwap"};
        for (int k = 0; k < signals.length; k++) {
            Object o = signals[k];
            if (o == null) sig.putNull(names[k]);
            else sig.put(names[k], ((Dir) o).name().toLowerCase());
        }

        Path target = stateFile;
        Path dir = target.toAbsolutePath().getParent();
        Files.createDirectories(dir);
        Path tmp = dir.resolve(target.getFileName() + ".tmp");
        mapper.writeValue(tmp.toFile(), root);
        Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
    }

    private static boolean isWeekend(long epochMs) {
        int dow = Instant.ofEpochMilli(epochMs).atZone(ZoneOffset.UTC).getDayOfWeek().getValue();
        return dow == 6 || dow == 7;
    }

    private void restoreStateFromDisk() {
        Path p = stateFile;
        if (!Files.exists(p)) return;
        try {
            JsonNode root = mapper.readTree(p.toFile());
            String saved = root.has("state_last_valid") ? root.get("state_last_valid").asText()
                    : root.has("state") ? root.get("state").asText() : null;
            if (saved != null && VALID_STATES.contains(saved)) currentState = saved;
            if (root.has("transition_chain_15m")) {
                for (JsonNode n : root.get("transition_chain_15m")) transitionChain.addLast(n.asText());
            }
            if (root.has("timestamp_utc")) {
                try { stateSinceMs = Instant.parse(root.get("timestamp_utc").asText()).toEpochMilli(); }
                catch (Exception ignored) { stateSinceMs = System.currentTimeMillis(); }
            }
            // Accumulators are NOT restored: ticks missed while down make them partial (audit M1/M2). They stay
            // INVALID until the kline backfill succeeds.
            System.out.println("[StateCode] Restored state from disk: " + currentState);
        } catch (Exception e) {
            System.err.println("[StateCode] restore failed: " + e.getMessage());
        }
    }
}
