package datafeed;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * T037: SetupScreener S01-S05 scoring. Expected scores are summed by hand from the point values in the class's own rule
 * table (S01 POC 30 / VAH 35 / VAL 35 / balanced VP 15; S02 40/25/25/10; S03 50/20/15; S04 40/30/15; S05 40/20/20),
 * with a cap of 95.
 */
public class SetupScreenerTest {

    private final SetupScreener screener = new SetupScreener(new ObjectMapper());

    private static final List<BinanceLiquidationAccumulator.Cluster> NO_CLUSTERS = Collections.emptyList();
    private static final List<FvgCalculator.Fvg> NO_FVGS = Collections.emptyList();
    private static final List<NakedPocTracker.PocEntry> NO_POCS = Collections.emptyList();

    private List<SetupScreener.Alert> screen(double price, double vwap, double poc, String vpShape, double funding,
                                             double oi, double ls, boolean cvdDiv, String cvdSlope,
                                             List<BinanceLiquidationAccumulator.Cluster> clusters,
                                             List<FvgCalculator.Fvg> fvgs, List<NakedPocTracker.PocEntry> pocs,
                                             double bid, double ask) {
        return screener.screen("BTCUSDT", price, vwap, 1.0, 0.0, poc, 110.0, 90.0, vpShape, 0.0, cvdSlope, cvdDiv,
                funding, oi, ls, clusters, fvgs, pocs, bid, ask);
    }

    private static SetupScreener.Alert find(List<SetupScreener.Alert> alerts, String setup) {
        for (SetupScreener.Alert a : alerts) if (a.setup.equals(setup)) return a;
        return null;
    }

    @Test
    public void quietMarketProducesNoAlerts() {
        List<SetupScreener.Alert> a = screen(100, 100, 95, "T", 0.0, 0, 1.0, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1);
        assertTrue(a.isEmpty());
    }

    @Test
    public void s01PocPlusBalancedShapeScores45AndNeedsVisual() {
        // price on POC (+30) + vpShape B (+15) = 45 < 60 -> visual validation, MEDIUM
        List<SetupScreener.Alert> a = screen(100, 100, 100, "B", 0.0, 0, 1.0, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1);
        assertEquals(1, a.size());
        SetupScreener.Alert s01 = a.get(0);
        assertEquals("S01", s01.setup);
        assertEquals("BTCUSDT", s01.symbol);
        assertEquals(45, s01.score);
        assertTrue(s01.requiresVisualValidation);
        assertEquals("MEDIUM", s01.confidence);
    }

    @Test
    public void s01AboveVahPlusBalancedShapeScores50() {
        // price 110.2 is above vah 110 and below vah*1.005 (+35), vpShape B (+15) = 50; poc 95 far away
        List<SetupScreener.Alert> a = screen(110.2, 110.2, 95, "B", 0.0, 0, 1.0, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1);
        SetupScreener.Alert s01 = find(a, "S01");
        assertEquals(50, s01.score);
    }

    @Test
    public void s02ScoreIsCappedAt95AndAlwaysNeedsVisual() {
        // 3% from VWAP (+40) + funding 0.002 (+25) + divergence (+25) + falling CVD above VWAP (+10) = 100 -> capped 95
        List<SetupScreener.Alert> a = screen(103, 100, 95, "T", 0.002, 0, 1.0, true, "falling", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1);
        SetupScreener.Alert s02 = find(a, "S02");
        assertEquals(95, s02.score);
        assertTrue(s02.requiresVisualValidation);
        assertEquals("MEDIUM", s02.confidence);
        // same inputs also trip S03 (funding > 0.0005 -> 15) and S04 (funding > 0.0015 -> 40)
        assertEquals(15, find(a, "S03").score);
        assertEquals(40, find(a, "S04").score);
        assertEquals(3, a.size());
    }

    @Test
    public void s02RisingCvdBelowVwapAddsTen() {
        // 3% below VWAP (+40) + rising CVD below VWAP (+10) = 50
        List<SetupScreener.Alert> a = screen(97, 100, 95, "T", 0.0, 0, 1.0, false, "rising", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1);
        assertEquals(50, find(a, "S02").score);
    }

    @Test
    public void s03TopClusterAtPriceWithHighDensityIsHighConfidence() {
        // cluster at price (+50) + totalQty 12 > 10 (+20) = 70 >= 70 -> no visual needed, HIGH
        List<BinanceLiquidationAccumulator.Cluster> c = new ArrayList<>();
        c.add(new BinanceLiquidationAccumulator.Cluster(100, 12.0, 6.0, 6.0));
        SetupScreener.Alert s03 = find(screen(100, 100, 95, "T", 0.0, 0, 1.0, false, "flat", c, NO_FVGS, NO_POCS, 1, 1), "S03");
        assertEquals(70, s03.score);
        assertFalse(s03.requiresVisualValidation);
        assertEquals("HIGH", s03.confidence);
    }

    @Test
    public void s03ClusterBeyondOnePercentDoesNotScore() {
        List<BinanceLiquidationAccumulator.Cluster> c = new ArrayList<>();
        c.add(new BinanceLiquidationAccumulator.Cluster(102, 5.0, 2.5, 2.5));
        assertEquals(null, find(screen(100, 100, 95, "T", 0.0, 0, 1.0, false, "flat", c, NO_FVGS, NO_POCS, 1, 1), "S03"));
    }

    @Test
    public void s04ExtremeFundingSkewedRatioAndHighOiIsHighConfidence() {
        // funding 0.002 (+40) + L/S 3.0 (+30) + OI 200000 (+15) = 85 >= 65 -> HIGH
        SetupScreener.Alert s04 = find(screen(100, 100, 95, "T", 0.002, 200000, 3.0, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1), "S04");
        assertEquals(85, s04.score);
        assertFalse(s04.requiresVisualValidation);
        assertEquals("HIGH", s04.confidence);
    }

    @Test
    public void s04LowLongShortRatioAloneScores30() {
        SetupScreener.Alert s04 = find(screen(100, 100, 95, "T", 0.0, 0, 0.3, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 1, 1), "S04");
        assertEquals(30, s04.score);
        assertTrue(s04.requiresVisualValidation);
    }

    @Test
    public void s05NakedPocFvgAndBookImbalanceScores80AndAlwaysNeedsVisual() {
        List<NakedPocTracker.PocEntry> pocs = new ArrayList<>();
        pocs.add(new NakedPocTracker.PocEntry("2026-10-01", 100.0, false));
        List<FvgCalculator.Fvg> fvgs = new ArrayList<>();
        fvgs.add(new FvgCalculator.Fvg("bullish", 101.0, 99.0, 0, 0L, false));
        // revisit (+40) + inside bullish FVG (+20) + bid/ask 200/100 = 2.0 > 1.5 (+20) = 80
        SetupScreener.Alert s05 = find(screen(100, 100, 95, "T", 0.0, 0, 1.0, false, "flat", NO_CLUSTERS, fvgs, pocs, 200, 100), "S05");
        assertEquals(80, s05.score);
        assertTrue(s05.requiresVisualValidation);
        assertEquals("MEDIUM", s05.confidence);
    }

    @Test
    public void s05ThinBidSideAlsoCountsAsImbalance() {
        // bid/ask = 50/100 = 0.5 < 0.67 -> +20 only
        SetupScreener.Alert s05 = find(screen(100, 100, 95, "T", 0.0, 0, 1.0, false, "flat", NO_CLUSTERS, NO_FVGS, NO_POCS, 50, 100), "S05");
        assertEquals(20, s05.score);
    }

    @Test
    public void toJsonArrayCarriesEveryAlertField() {
        List<SetupScreener.Alert> a = new ArrayList<>();
        a.add(new SetupScreener.Alert("S04", "ETHUSDT", 85, false, "why", "HIGH"));
        ArrayNode arr = screener.toJsonArray(a);
        assertEquals(1, arr.size());
        assertEquals("S04", arr.get(0).get("setup").asText());
        assertEquals("ETHUSDT", arr.get(0).get("symbol").asText());
        assertEquals(85, arr.get(0).get("score").asInt());
        assertFalse(arr.get(0).get("requires_visual_validation").asBoolean());
        assertEquals("why", arr.get(0).get("reason").asText());
        assertEquals("HIGH", arr.get(0).get("confidence").asText());
    }
}
