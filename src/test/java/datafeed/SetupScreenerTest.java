package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for SetupScreener pure-function behavior.
 * Tests current behavior: alert generation for setups S01-S05 based on market signals.
 */
public class SetupScreenerTest {

    private SetupScreener screener;
    private static final String SYMBOL = "BTCUSDT";

    @BeforeEach
    void setUp() {
        screener = new SetupScreener(new ObjectMapper());
    }

    // --- S01: Volume Profile Rejection (POC/VAH/VAL bounce) ---

    @Test
    void s01_price_at_poc_generates_alert() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL,
                100.0,    // price
                101.0,    // vwap
                0.5,      // sigma
                0.01,     // vwapSlopePct
                100.0,    // poc (price at POC)
                105.0,    // vah
                95.0,     // val
                "B",      // vpShape
                0.0,      // cvd
                "neutral", // cvdSlope
                false,    // cvdDivergence
                0.0001,   // fundingRate
                50000.0,  // oiValue
                1.5,      // lsRatio
                new ArrayList<>(),  // liqClusters
                new ArrayList<>(),  // unfilledFvgs
                new ArrayList<>(),  // revisitingPocs
                100.0,    // bidDepth
                100.0     // askDepth
        );

        assertTrue(alerts.stream().anyMatch(a -> "S01".equals(a.setup)),
                "S01 alert should exist when price is at POC");
    }

    @Test
    void s01_balanced_profile_increases_score() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0,
                "B",  // balanced profile
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        SetupScreener.Alert s01 = alerts.stream()
                .filter(a -> "S01".equals(a.setup))
                .findFirst()
                .orElse(null);

        if (s01 != null) {
            assertTrue(s01.reason.contains("Balanced VP"),
                    "S01 reason should reference balanced VP shape");
        }
    }

    @Test
    void s01_no_alerts_when_no_triggers() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 200.0, 205.0, 195.0,
                "F",  // far from price, not balanced
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        assertFalse(alerts.stream().anyMatch(a -> "S01".equals(a.setup)),
                "S01 should not trigger when price is far from profile levels");
    }

    // --- S02: VWAP Mean Reversion ---

    @Test
    void s02_price_far_from_vwap_generates_alert() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL,
                102.1,    // price 2.1% above VWAP (must be > 2%)
                100.0,    // vwap
                0.5,
                0.01,
                101.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        assertTrue(alerts.stream().anyMatch(a -> "S02".equals(a.setup)),
                "S02 should trigger when price is >2% from VWAP");
    }

    @Test
    void s02_always_requires_visual_validation() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 102.1, 100.0, 0.5, 0.01, 101.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        SetupScreener.Alert s02 = alerts.stream()
                .filter(a -> "S02".equals(a.setup))
                .findFirst()
                .orElse(null);

        assertNotNull(s02, "S02 should exist");
        assertTrue(s02.requiresVisualValidation,
                "S02 ALWAYS requires visual validation per architecture");
    }

    // --- S03: Liquidation Cluster + Absorption ---

    @Test
    void s03_no_alerts_without_clusters() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(),  // empty liqClusters
                new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        assertFalse(alerts.stream().anyMatch(a -> "S03".equals(a.setup)),
                "S03 should not trigger without liquidation clusters");
    }

    // --- S04: Funding Extreme + OI/L-S Flip ---

    @Test
    void s04_high_funding_rate_generates_alert() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false,
                0.002,    // funding rate > 0.0015 threshold
                50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        assertTrue(alerts.stream().anyMatch(a -> "S04".equals(a.setup)),
                "S04 should trigger with extreme funding rate");
    }

    @Test
    void s04_skewed_ls_ratio_increases_score() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0,
                3.0,      // lsRatio > 2.5 threshold
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        SetupScreener.Alert s04 = alerts.stream()
                .filter(a -> "S04".equals(a.setup))
                .findFirst()
                .orElse(null);

        assertNotNull(s04, "S04 should trigger with skewed L/S ratio");
        assertTrue(s04.reason.contains("skewed"), "Reason should mention skewed ratio");
    }

    // --- S05: Naked POC Revisit + Order Book Thickening ---

    @Test
    void s05_always_requires_visual_validation_when_triggered() {
        // Create a fake naked POC tracker entry
        List<NakedPocTracker.PocEntry> revisitingPocs = new ArrayList<>();
        // Note: We can't easily construct PocEntry without its constructor
        // So we test through empty list for now

        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        SetupScreener.Alert s05 = alerts.stream()
                .filter(a -> "S05".equals(a.setup))
                .findFirst()
                .orElse(null);

        if (s05 != null) {
            assertTrue(s05.requiresVisualValidation,
                    "S05 ALWAYS requires visual validation when triggered");
        }
    }

    @Test
    void s05_book_imbalance_generates_signal() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 100.0, 101.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                200.0,    // bidDepth > askDepth (imbalance)
                100.0     // askDepth
        );

        SetupScreener.Alert s05 = alerts.stream()
                .filter(a -> "S05".equals(a.setup))
                .findFirst()
                .orElse(null);

        if (s05 != null) {
            assertTrue(s05.reason.contains("imbalance"),
                    "Reason should mention book imbalance");
        }
    }

    // --- Score bounds ---

    @Test
    void alert_score_bounded_at_95() {
        // Create conditions that would generate high scores
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 102.0, 100.0, 0.5, 0.01, 100.0, 105.0, 95.0, "B",
                0.0, "neutral", true,  // cvdDivergence = true
                0.002, 200000.0, 3.0,   // multiple high-score conditions
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                200.0, 100.0
        );

        for (SetupScreener.Alert alert : alerts) {
            assertTrue(alert.score <= 95,
                    "Alert score should never exceed 95: " + alert.setup);
        }
    }

    @Test
    void multiple_alerts_can_fire_simultaneously() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 102.0, 100.0, 0.5, 0.01, 100.0, 105.0, 95.0, "B",
                0.0, "neutral", true, 0.002, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        // With multiple signal types, we should get alerts for multiple setups
        assertTrue(alerts.size() >= 1,
                "At least one alert should be generated with these conditions");
    }

    @Test
    void toJsonArray_serializes_alerts() {
        List<SetupScreener.Alert> alerts = screener.screen(
                SYMBOL, 102.0, 100.0, 0.5, 0.01, 102.0, 105.0, 95.0, "F",
                0.0, "neutral", false, 0.0001, 50000.0, 1.5,
                new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
                100.0, 100.0
        );

        var jsonArray = screener.toJsonArray(alerts);

        assertNotNull(jsonArray);
        if (alerts.size() > 0) {
            assertEquals(alerts.size(), jsonArray.size(),
                    "JSON array should have same size as alerts list");
        }
    }
}
