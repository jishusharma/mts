package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;

/**
 * Attempts per session for family A (TOM_LAYER_V2_SPEC 2.6 A-M5 and 13): one first attempt plus at most one re-entry,
 * and the re-entry only after the first attempt was stopped out and on a fresh signal (a signal strictly after the stop).
 * A third candidate in the session is suppressed and logged. Session = Berlin calendar date of the signal (OURS; the
 * state resets when the date changes). The "one re-entry" count is frame-observed (spec 2.6), not Tom's words.
 *
 * <p>Persistence: with {@code -Dmts.spikeFade.stateFile=<path>} every record is written through to that file so a restart
 * mid-session keeps the count. An unreadable file fails closed (every admit is refused). Without the property the state
 * lives in memory only. Callers record entries and stops ({@link #recordEntry}, {@link #recordStop}); the candidate
 * builder only reads ({@link #admit}).
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
        long stopMs = -1;
        Attempt(long entryMs, String path) { this.entryMs = entryMs; this.path = path; }
    }

    private final Path file;
    private final TreeMap<LocalDate, List<Attempt>> sessions = new TreeMap<>();
    private final List<String> suppressed = new ArrayList<>();
    private boolean unreadable;

    SpikeFadeSessionState(Path file) {
        this.file = file;
        if (file != null && Files.exists(file)) load();
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

    private void load() {
        try {
            JsonNode root = M.readTree(Files.readString(file));
            if (root == null || !root.path("sessions").isObject()) throw new IllegalStateException("no sessions object");
            var it = root.get("sessions").fields();
            while (it.hasNext()) {
                var e = it.next();
                List<Attempt> list = new ArrayList<>();
                for (JsonNode a : e.getValue()) {
                    Attempt at = new Attempt(a.get("entry_ms").asLong(), a.path("path").asText());
                    at.stopMs = a.path("stop_ms").asLong(-1);
                    list.add(at);
                }
                sessions.put(LocalDate.parse(e.getKey()), list);
            }
        } catch (Exception ex) {
            unreadable = true;   // fail closed: cannot know how many attempts were taken
            suppressed.add("state file unreadable: " + ex);
        }
    }

    private void save() {
        if (file == null) return;
        try {
            ObjectNode root = M.createObjectNode();
            ObjectNode s = root.putObject("sessions");
            for (var e : sessions.entrySet()) {
                ArrayNode arr = s.putArray(e.getKey().toString());
                for (Attempt a : e.getValue()) {
                    ObjectNode o = arr.addObject();
                    o.put("entry_ms", a.entryMs);
                    o.put("path", a.path);
                    o.put("stop_ms", a.stopMs);
                }
            }
            Path tmp = file.resolveSibling(file.getFileName() + ".tmp");
            Files.writeString(tmp, M.writerWithDefaultPrettyPrinter().writeValueAsString(root));
            Files.move(tmp, file, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        } catch (Exception ex) {
            unreadable = true;   // cannot persist: later admits fail closed
            suppressed.add("state file not writable: " + ex);
        }
    }

    synchronized void recordEntry(LocalDate session, long entryMs, String path) {
        sessions.computeIfAbsent(session, d -> new ArrayList<>()).add(new Attempt(entryMs, path));
        save();
    }

    /** Marks the latest open attempt of the session as stopped out at stopMs. */
    synchronized void recordStop(LocalDate session, long stopMs) {
        List<Attempt> list = sessions.get(session);
        if (list == null) return;
        for (int i = list.size() - 1; i >= 0; i--) {
            if (list.get(i).stopMs < 0) { list.get(i).stopMs = stopMs; break; }
        }
        save();
    }

    /** May a candidate signalled at signalMs in this session be taken? A refusal is logged. */
    synchronized Decision admit(LocalDate session, long signalMs) {
        if (unreadable) return refuse(session, signalMs, "state unreadable, fail closed");
        List<Attempt> list = sessions.getOrDefault(session, List.of());
        if (list.size() >= MAX_ATTEMPTS) return refuse(session, signalMs, "third attempt in the session (A-M5: one re-entry)");
        if (list.isEmpty()) return new Decision(true, "first attempt");
        Attempt first = list.get(0);
        if (first.stopMs < 0) return refuse(session, signalMs, "first attempt still open, no re-entry (A-M5)");
        if (signalMs <= first.stopMs) return refuse(session, signalMs, "not a fresh signal: not after the stop (A-M5)");
        return new Decision(true, "re-entry on a fresh signal");
    }

    private Decision refuse(LocalDate session, long signalMs, String why) {
        String line = "spikeFade suppressed " + session + " signal_ms=" + signalMs + ": " + why;
        suppressed.add(line);
        System.err.println(line);
        return new Decision(false, why);
    }

    synchronized List<String> suppressedLog() {
        return new ArrayList<>(suppressed);
    }
}
