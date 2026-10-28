package datafeed;

import org.junit.jupiter.api.Test;
import java.time.LocalDate;
import java.time.ZonedDateTime;
import static org.junit.jupiter.api.Assertions.assertEquals;

class UsEquityOpenDstTest {
    @Test
    void summerOpenIs1330Utc() {
        ZonedDateTime z = MarketDataSnapshot.usEquityOpenUtc(LocalDate.of(2026, 10, 5));
        assertEquals(13, z.getHour());
        assertEquals(30, z.getMinute());
    }

    @Test
    void winterOpenIs1430Utc() {
        ZonedDateTime z = MarketDataSnapshot.usEquityOpenUtc(LocalDate.of(2026, 12, 7));
        assertEquals(14, z.getHour());
        assertEquals(30, z.getMinute());
    }
}
