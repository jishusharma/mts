package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * Tracks daily POCs and detects when price revisits a "naked" POC
 * (a POC from a previous day that has not yet been revisited).
 */
public class NakedPocTracker {

    private static final DateTimeFormatter FMT = DateTimeFormatter.ISO_LOCAL_DATE;
    private static final double REVISIT_THRESHOLD_PCT = 0.003; // 0.3%

    private final String symbol;
    private final ObjectMapper mapper;
    private final Path filePath;

    public NakedPocTracker(String symbol) {
        this.symbol = symbol;
        this.mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
        this.filePath = Paths.get("data", "naked_pocs", symbol + "_naked_pocs.json");
    }

    public static class PocEntry {
        public String date;
        public double poc;
        public boolean visited;

        public PocEntry() {}
        public PocEntry(String date, double poc, boolean visited) {
            this.date = date;
            this.poc = poc;
            this.visited = visited;
        }
    }

    public List<PocEntry> loadEntries() throws IOException {
        if (!Files.exists(filePath)) return new ArrayList<>();
        String json = Files.readString(filePath);
        JsonNode root = mapper.readTree(json);
        List<PocEntry> list = new ArrayList<>();
        for (JsonNode n : root) {
            PocEntry e = new PocEntry();
            e.date = n.get("date").asText();
            e.poc = n.get("poc").asDouble();
            e.visited = n.get("visited").asBoolean();
            list.add(e);
        }
        return list;
    }

    public void saveEntries(List<PocEntry> entries) throws IOException {
        Files.createDirectories(filePath.getParent());
        ArrayNode arr = mapper.valueToTree(entries);
        mapper.writeValue(filePath.toFile(), arr);
    }

    /**
     * Check if current price is near any unvisited (naked) POC.
     * Marks them visited if within threshold.
     * @return list of naked POCs that are currently being revisited
     */
    public List<PocEntry> checkRevisit(double currentPrice) throws IOException {
        List<PocEntry> entries = loadEntries();
        List<PocEntry> revisiting = new ArrayList<>();
        String today = LocalDate.now().toString();

        for (PocEntry e : entries) {
            if (e.visited || e.date.equals(today)) continue;
            double dist = Math.abs(currentPrice - e.poc) / e.poc;
            if (dist <= REVISIT_THRESHOLD_PCT) {
                e.visited = true;
                revisiting.add(e);
            }
        }
        saveEntries(entries);
        return revisiting;
    }

    /**
     * Record today's POC. If today already exists, update it.
     */
    public void recordTodayPoc(double poc) throws IOException {
        List<PocEntry> entries = loadEntries();
        String today = LocalDate.now().toString();
        boolean found = false;
        for (PocEntry e : entries) {
            if (e.date.equals(today)) {
                e.poc = poc;
                found = true;
                break;
            }
        }
        if (!found) {
            entries.add(new PocEntry(today, poc, false));
        }
        // Keep last 90 days only
        if (entries.size() > 90) {
            entries = entries.subList(entries.size() - 90, entries.size());
        }
        saveEntries(entries);
    }

    public ObjectNode getNakedPocsNode() throws IOException {
        List<PocEntry> entries = loadEntries();
        ObjectNode node = mapper.createObjectNode();
        ArrayNode nakedArr = node.putArray("naked_pocs");
        ArrayNode visitedArr = node.putArray("visited_pocs");
        for (PocEntry e : entries) {
            ObjectNode o = (e.visited ? visitedArr : nakedArr).addObject();
            o.put("date", e.date);
            o.put("poc", Math.round(e.poc * 100.0) / 100.0);
        }
        return node;
    }
}