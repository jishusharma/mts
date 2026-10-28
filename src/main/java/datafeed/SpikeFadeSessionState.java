package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeMap;

/**
 * Attempts per session for family A paths A2/A3 (TOM_LAYER_V2_SPEC 2.6 A-M5 and 13): one first attempt plus at most one
 * re-entry, and the re-entry only after the first attempt was stopped out and on a signal strictly after the stop. A third
 * candidate in the session is suppressed and logged (once per session and reason). Session = Berlin calendar date of the
 * signal (OURS; the state resets when the date changes). The "one re-entry" count is frame-observed (spec 2.6).
 *
 * <p>The builder records the attempt it emits (an emitted A2/A3 candidate is an attempt, fill not modelled: OURS) and
 * {@link #observe} marks it stopped from the bars: the first bar after the entry whose high reaches the stop price (spec 13:
 * 1 lot, fixed bracket). The same signal bar asked twice (a re-evaluated snapshot, a restart) gets the same answer. Path A1
 * is the idea-level signal the detector re-emits on every bar and has no fill in the builder, so it is neither recorded nor
 * gated here (OURS; the card keeps A1 unchanged); an executor may record A1 entries via {@link #recordEntry}.
 *
 * <p>Persistence: with {@code -Dmts.spikeFade.stateFile=<path>} every record is written to that file (temp file + move) and
 * every call re-reads it when it changed, so a restart or a second process sees the count. An unreadable file fails closed
 * (every admit is refused). Without the property the state lives in memory only.
 */
final class SpikeFadeSessionState {
    static final String FILE_PROPERTY = "mts.spikeFade.stateFile";
    static final int MAX_ATTEMPTS = 2;   // first attempt + one re-entry
    private static final ObjectMapper M = new ObjectMapper();
    private static SpikeFadeSessionState shared;

    static final class Decision {
        final boolean allowed;
        final String reason;
        Decision(boolean allowed, String reason) { this.allowed = allowed; this.reason = reason; }
    }

    private static final class Attempt {
        final long entryMs;
        final String path;
        final double stopPrice;   // NaN when unknown (never observed as stopped)
        long stopMs = -1;
        Attempt(long entryMs, String path, double stopPrice) { this.entryMs = entryMs; this.path = path; this.stopPrice = stopPrice; }
    }

    private final Path file;
    private final TreeMap<String, List<Attempt>> sessions = new TreeMap<>();
    private final List<String> suppressed = new ArrayList<>();
    private final Set<String> loggedKeys = new HashSet<>();
    private boolean unreadable;
    private long loadedModified = Long.MIN_VALUE;
    private long loadedSize = -1;

    SpikeFadeSessionState(Path file) {
        this.file = file;
        reload();
    }

    static synchronized SpikeFadeSessionState shared() {
        if (shared == null) {
            String p = System.getProperty(FILE_PROPERTY);
            shared = new SpikeFadeSessionState(p == null || p.isBlank() ? null : Path.of(p));
        }
        return shared;
    }

    static synchronized void resetShared() {
        shared = null;
    }

    /** Re-read the file when it changed since the last read or write. */
    private void reload() {
        if (file == null || !Files.exists(file)) return;
        try {
            long mod = Files.getLastModifiedTime(file).toMillis(), size = Files.size(file);
            if (mod == loadedModified && size == loadedSize) return;
            JsonNode root = M.readTree(Files.readString(file));
            if (root == null || !root.path("sessions").isObject()) throw new IllegalStateException("no sessions object");
            TreeMap<String, List<Attempt>> parsed = new TreeMap<>();
            var it = root.get("sessions").fields();
            while (it.hasNext()) {
                var e = it.next();
                List<Attempt> list = new ArrayList<>();
                for (JsonNode a : e.getValue()) {
                    double sp = a.has("stop_price") && a.get("stop_price").isNumber() ? a.get("stop_price").asDouble() : Double.NaN;
                    Attempt at = new Attempt(a.get("entry_ms").asLong(), a.path("path").asText(), sp);
                    at.stopMs = a.path("stop_ms").asLong(-1);
                    list.add(at);
                }
                parsed.put(e.getKey(), list);
            }
            sessions.clear();
            sessions.putAll(parsed);
            loadedModified = mod;
            loadedSize = size;
            unreadable = false;
        } catch (Exception ex) {
            unreadable = true;   // fail closed: cannot know how many attempts were taken
            note("state-file-unreadable", "state file unreadable: " + ex);
        }
    }

    private void save() {
        if (file == null || unreadable) return;   // never overwrite a file we could not read
        try {
            ObjectNode root = M.createObjectNode();
            ObjectNode s = root.putObject("sessions");
            for (var e : sessions.entrySet()) {
                ArrayNode arr = s.putArray(e.getKey());
                for (Attempt a : e.getValue()) {
                    ObjectNode o = arr.addObject();
                    o.put("entry_ms", a.entryMs);
                    o.put("path", a.path);
                    if (!Double.isNaN(a.stopPrice)) o.put("stop_price", a.stopPrice);
                    o.put("stop_ms", a.stopMs);
                }
            }
            Path tmp = file.resolveSibling(file.getFileName() + ".tmp");
            Files.writeString(tmp, M.writerWithDefaultPrettyPrinter().writeValueAsString(root));
            try {
                Files.move(tmp, file, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (java.nio.file.AtomicMoveNotSupportedException nm) {
                Files.move(tmp, file, StandardCopyOption.REPLACE_EXISTING);
            }
            loadedModified = Files.getLastModifiedTime(file).toMillis();
            loadedSize = Files.size(file);
        } catch (Exception ex) {
            unreadable = true;   // cannot persist: later admits fail closed
            note("state-file-not-writable", "state file not writable: " + ex);
        }
    }

    /** Session key: the symbol and the Berlin date (one cap per instrument and session). */
    static String key(String sym, LocalDate session) {
        return (sym == null ? "" : sym) + "|" + session;
    }

    synchronized void recordEntry(LocalDate session, long entryMs, String path) {
        recordEntry(session.toString(), entryMs, path, Double.NaN);
    }

    synchronized void recordEntry(String session, long entryMs, String path, double stopPrice) {
        reload();
        List<Attempt> list = sessions.computeIfAbsent(session, d -> new ArrayList<>());
        for (Attempt a : list) if (a.entryMs == entryMs) return;   // same signal recorded twice: one attempt
        list.add(new Attempt(entryMs, path, stopPrice));
        save();
    }

    /** Marks the latest open attempt of the session as stopped out at stopMs. */
    synchronized void recordStop(LocalDate session, long stopMs) {
        recordStop(session.toString(), stopMs);
    }

    synchronized void recordStop(String session, long stopMs) {
        reload();
        List<Attempt> list = sessions.get(session);
        if (list == null) return;
        for (int i = list.size() - 1; i >= 0; i--) {
            if (list.get(i).stopMs < 0) { list.get(i).stopMs = stopMs; break; }
        }
        save();
    }

    /** Marks every open attempt of the session stopped at the first later bar whose high reached its stop price. */
    synchronized void observe(String session, LocalDate day, SpikeFadeDetector.Bars b) {
        reload();
        List<Attempt> list = sessions.get(session);
        if (list == null) return;
        boolean changed = false;
        for (Attempt a : list) {
            if (a.stopMs >= 0 || Double.isNaN(a.stopPrice)) continue;
            for (int i = 0; i < b.n; i++) {
                if (b.t[i] > a.entryMs && b.date[i].equals(day) && b.h[i] >= a.stopPrice) {
                    a.stopMs = b.t[i];
                    changed = true;
                    break;
                }
            }
        }
        if (changed) save();
    }

    synchronized int attempts(LocalDate session) {
        return attempts(session.toString());
    }

    synchronized int attempts(String session) {
        reload();
        return sessions.getOrDefault(session, List.of()).size();
    }

    /** May a candidate signalled at signalMs in this session be taken? A refusal is logged once per session and reason. */
    synchronized Decision admit(LocalDate session, long signalMs) {
        return admit(session.toString(), signalMs);
    }

    synchronized Decision admit(String session, long signalMs) {
        reload();
        if (unreadable) return refuse(session, "state unreadable, fail closed");
        List<Attempt> list = sessions.getOrDefault(session, List.of());
        for (Attempt a : list) if (a.entryMs == signalMs) return new Decision(true, "same signal re-evaluated");
        if (list.size() >= MAX_ATTEMPTS) return refuse(session, "third attempt in the session (A-M5: one re-entry)");
        if (list.isEmpty()) return new Decision(true, "first attempt");
        Attempt first = list.get(0);
        if (first.stopMs < 0) return refuse(session, "first attempt still open, no re-entry (A-M5)");
        if (signalMs <= first.stopMs) return refuse(session, "not a fresh signal: not after the stop (A-M5)");
        return new Decision(true, "re-entry on a fresh signal");
    }

    private Decision refuse(String session, String why) {
        note(session + "|" + why, "spikeFade suppressed " + session + ": " + why);
        return new Decision(false, why);
    }

    private void note(String key, String line) {
        if (!loggedKeys.add(key)) return;
        suppressed.add(line);
        System.err.println(line);
    }

    synchronized List<String> suppressedLog() {
        return new ArrayList<>(suppressed);
    }
}
