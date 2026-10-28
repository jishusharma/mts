package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** F-BT-14: NakedPocTracker had no writer, so the naked-POC list froze at 2026-08-28 while setups still read it. */
public class NakedPocWriterTest {

    private static final ObjectMapper M = new ObjectMapper();
    private static final LocalDate D5 = LocalDate.of(2026, 10, 5);
    private static final LocalDate D6 = LocalDate.of(2026, 10, 6);
    private static final LocalDate D7 = LocalDate.of(2026, 10, 7);

    private static long ms(LocalDate d, int hour) {
        return d.atStartOfDay().plusHours(hour).toInstant(ZoneOffset.UTC).toEpochMilli();
    }

    private static ArrayNode bars(Object[][] rows) {
        ArrayNode out = M.createArrayNode();
        for (Object[] r : rows) {
            ArrayNode a = out.addArray();
            a.add((long) r[0]).add(0.0).add((double) r[1]).add((double) r[2]).add(0.0).add(1.0);
        }
        return out;
    }

    private static ObjectNode vp(double poc) {
        ObjectNode n = M.createObjectNode();
        n.put("poc", poc);
        return n;
    }

    @Test
    void recordsFinishedPriorDayAndKeepsOrder(@TempDir Path dir) throws Exception {
        NakedPocTracker t = new NakedPocTracker("BTCUSDT", dir.resolve("p.json"));
        MarketDataSnapshot.updateNakedPocs(t, vp(85_500.0), D6, 1440, D7, bars(new Object[][]{}));
        MarketDataSnapshot.updateNakedPocs(t, vp(85_000.0), D5, 1440, D7, bars(new Object[][]{}));
        List<NakedPocTracker.PocEntry> e = t.loadEntries();
        assertEquals(2, e.size());
        assertEquals("2026-10-05", e.get(0).date);
        assertEquals("2026-10-06", e.get(1).date);
        assertFalse(e.get(1).visited);
    }

    @Test
    void sameDayIsUpdatedNotDuplicatedAndVisitedFlagSurvives(@TempDir Path dir) throws Exception {
        NakedPocTracker t = new NakedPocTracker("BTCUSDT", dir.resolve("p.json"));
        t.recordPoc(D6, 85_500.0);
        t.markVisitedByBars(bars(new Object[][]{{ms(D7, 3), 85_600.0, 85_400.0}}), D7);
        t.recordPoc(D6, 85_510.0);
        List<NakedPocTracker.PocEntry> e = t.loadEntries();
        assertEquals(1, e.size());
        assertEquals(85_510.0, e.get(0).poc, 1e-9);
        assertTrue(e.get(0).visited);
    }

    @Test
    void partialDayAndEmptyProfileAreNotRecorded(@TempDir Path dir) throws Exception {
        NakedPocTracker t = new NakedPocTracker("BTCUSDT", dir.resolve("p.json"));
        MarketDataSnapshot.updateNakedPocs(t, vp(85_500.0), D6, 400, D7, bars(new Object[][]{}));
        MarketDataSnapshot.updateNakedPocs(t, vp(0.0), D6, 1440, D7, bars(new Object[][]{}));
        MarketDataSnapshot.updateNakedPocs(t, vp(Double.NaN), D6, 1440, D7, bars(new Object[][]{}));
        assertTrue(t.loadEntries().isEmpty());
    }

    @Test
    void wickThroughPocAfterItsDayMarksVisited_barsBeforeOrOnItsDayDoNot(@TempDir Path dir) throws Exception {
        NakedPocTracker t = new NakedPocTracker("BTCUSDT", dir.resolve("p.json"));
        t.recordPoc(D5, 85_500.0);
        t.recordPoc(D6, 86_000.0);
        ArrayNode b = bars(new Object[][]{
                {ms(D5, 12), 85_600.0, 85_400.0},     // same day as D5 POC: ignored
                {ms(D6, 9), 85_700.0, 85_450.0},      // after D5: visits 85,500
                {ms(D6, 10), 85_900.0, 85_800.0}});   // never reaches 86,000
        List<NakedPocTracker.PocEntry> hit = t.markVisitedByBars(b, D7);
        assertEquals(1, hit.size());
        assertEquals("2026-10-05", hit.get(0).date);
        for (NakedPocTracker.PocEntry e : t.loadEntries()) assertEquals(e.date.equals("2026-10-05"), e.visited);
    }

    @Test
    void trackerFailureNeverReachesTheSnapshot(@TempDir Path dir) {
        NakedPocTracker t = new NakedPocTracker("BTCUSDT", dir); // a directory, not a file: every read/write throws
        MarketDataSnapshot.updateNakedPocs(t, vp(85_500.0), D6, 1440, D7, bars(new Object[][]{{ms(D7, 1), 1.0, 0.5}}));
    }
}
