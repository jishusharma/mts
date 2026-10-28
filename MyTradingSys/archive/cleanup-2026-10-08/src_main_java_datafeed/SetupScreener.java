package datafeed;

import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.ArrayList;
import java.util.List;

/**
 * Screens market data for trading setups S01–S05.
 * Outputs setup alerts with scores and honest confidence flags.
 * S02/S05 ALWAYS require visual validation (single-exchange data insufficient).
 * S01/S03/S04 require visual validation only when score is below threshold.
 */
public class SetupScreener {

    private final com.fasterxml.jackson.databind.ObjectMapper mapper;

    public SetupScreener(com.fasterxml.jackson.databind.ObjectMapper mapper) {
        this.mapper = mapper;
    }

    public static class Alert {
        public final String setup;
        public final String symbol;
        public final int score;              // 0–100
        public final boolean requiresVisualValidation;
        public final String reason;
        public final String confidence;        // HIGH / MEDIUM / LOW

        public Alert(String setup, String symbol, int score, boolean requiresVisualValidation,
                     String reason, String confidence) {
            this.setup = setup;
            this.symbol = symbol;
            this.score = score;
            this.requiresVisualValidation = requiresVisualValidation;
            this.reason = reason;
            this.confidence = confidence;
        }
    }

    public List<Alert> screen(
            String symbol,
            double price,
            double vwap,
            double sigma,
            double vwapSlopePct,      // e.g. +0.5% = rising
            double poc,
            double vah,
            double val,
            String vpShape,
            double cvd,
            String cvdSlope,
            boolean cvdDivergence,
            double fundingRate,
            double oiValue,
            double lsRatio,
            List<BinanceLiquidationAccumulator.Cluster> liqClusters,
            List<FvgCalculator.Fvg> unfilledFvgs,
            List<NakedPocTracker.PocEntry> revisitingPocs,
            double bidDepth,            // cumulative bid volume near price
            double askDepth             // cumulative ask volume near price
    ) {
        List<Alert> alerts = new ArrayList<>();

        double distToVwapPct = (price - vwap) / vwap;
        double distToPocPct = (price - poc) / poc;
        double distToVahPct = (price - vah) / vwap;
        double distToValPct = (price - val) / vwap;

        // --- S01: Volume Profile Rejection (POC/VAH/VAL bounce) ---
        int s01Score = 0;
        String s01Reason = "";
        if (Math.abs(distToPocPct) < 0.003) {
            s01Score += 30;
            s01Reason += "Price at POC. ";
        }
        if (price > vah && price < vah * 1.005) {
            s01Score += 35;
            s01Reason += "Price at VAH resistance. ";
        }
        if (price < val && price > val * 0.995) {
            s01Score += 35;
            s01Reason += "Price at VAL support. ";
        }
        if ("B".equals(vpShape)) {
            s01Score += 15;
            s01Reason += "Balanced VP (B). ";
        }
        if (s01Score > 0) {
            boolean needVis = s01Score < 60;
            alerts.add(new Alert("S01", symbol, Math.min(s01Score, 95), needVis,
                    s01Reason + "VP rejection candidate.", needVis ? "MEDIUM" : "HIGH"));
        }

        // --- S02: VWAP Mean Reversion (price beyond ±2σ) ---
        int s02Score = 0;
        String s02Reason = "";
        if (Math.abs(distToVwapPct) > 0.02) {
            s02Score += 40;
            s02Reason += String.format("Price %.2f%% from VWAP. ", distToVwapPct * 100);
        }
        if (Math.abs(fundingRate) > 0.001) {
            s02Score += 25;
            s02Reason += String.format("Funding %.4f%% extreme. ", fundingRate * 100);
        }
        if (cvdDivergence) {
            s02Score += 25;
            s02Reason += "CVD divergence detected. ";
        }
        if ("falling".equals(cvdSlope) && price > vwap) {
            s02Score += 10;
            s02Reason += "Price above VWAP but CVD falling. ";
        }
        if ("rising".equals(cvdSlope) && price < vwap) {
            s02Score += 10;
            s02Reason += "Price below VWAP but CVD rising. ";
        }
        if (s02Score > 0) {
            // S02 ALWAYS requires visual validation per architecture
            alerts.add(new Alert("S02", symbol, Math.min(s02Score, 95), true,
                    s02Reason + "Mean reversion candidate — MUST verify on CoinGlass.", "MEDIUM"));
        }

        // --- S03: Liquidation Cluster + Absorption ---
        int s03Score = 0;
        String s03Reason = "";
        if (!liqClusters.isEmpty()) {
            BinanceLiquidationAccumulator.Cluster top = liqClusters.get(0);
            double dist = Math.abs(price - top.priceLevel) / price;
            if (dist < 0.01) {
                s03Score += 50;
                s03Reason += String.format("Price near top liq cluster $%,d. ", top.priceLevel);
            }
            if (top.totalQty > 10.0) {
                s03Score += 20;
                s03Reason += "High liq density. ";
            }
        }
        if (Math.abs(fundingRate) > 0.0005) {
            s03Score += 15;
            s03Reason += "Elevated funding. ";
        }
        if (s03Score > 0) {
            boolean needVis = s03Score < 70;
            alerts.add(new Alert("S03", symbol, Math.min(s03Score, 95), needVis,
                    s03Reason + "Liq cluster setup.", needVis ? "MEDIUM" : "HIGH"));
        }

        // --- S04: Funding Extreme + OI/L-S Flip ---
        int s04Score = 0;
        String s04Reason = "";
        if (Math.abs(fundingRate) > 0.0015) {
            s04Score += 40;
            s04Reason += String.format("Funding extreme %.4f%%. ", fundingRate * 100);
        }
        if (lsRatio > 2.5 || lsRatio < 0.4) {
            s04Score += 30;
            s04Reason += String.format("L/S ratio skewed (%.2f). ", lsRatio);
        }
        if (oiValue > 100000) { // arbitrary large OI threshold
            s04Score += 15;
            s04Reason += "High OI. ";
        }
        if (s04Score > 0) {
            boolean needVis = s04Score < 65;
            alerts.add(new Alert("S04", symbol, Math.min(s04Score, 95), needVis,
                    s04Reason + "Sentiment extreme.", needVis ? "MEDIUM" : "HIGH"));
        }

        // --- S05: Naked POC Revisit + Order Book Thickening ---
        int s05Score = 0;
        String s05Reason = "";
        if (!revisitingPocs.isEmpty()) {
            s05Score += 40;
            s05Reason += "Naked POC revisit. ";
        }
        if (!unfilledFvgs.isEmpty()) {
            FvgCalculator.Fvg nearest = unfilledFvgs.get(0);
            if (nearest.type.equals("bullish") && price < nearest.top && price > nearest.bottom) {
                s05Score += 20;
                s05Reason += "Price inside bullish FVG. ";
            } else if (nearest.type.equals("bearish") && price < nearest.top && price > nearest.bottom) {
                s05Score += 20;
                s05Reason += "Price inside bearish FVG. ";
            }
        }
        double depthRatio = bidDepth / Math.max(askDepth, 0.0001);
        if (depthRatio > 1.5 || depthRatio < 0.67) {
            s05Score += 20;
            s05Reason += String.format("Book imbalance (bid/ask=%.2f). ", depthRatio);
        }
        if (s05Score > 0) {
            // S05 ALWAYS requires visual validation per architecture
            alerts.add(new Alert("S05", symbol, Math.min(s05Score, 95), true,
                    s05Reason + "Structural level — MUST verify on CoinGlass.", "MEDIUM"));
        }

        return alerts;
    }

    public ArrayNode toJsonArray(List<Alert> alerts) {
        ArrayNode arr = mapper.createArrayNode();
        for (Alert a : alerts) {
            ObjectNode o = arr.addObject();
            o.put("setup", a.setup);
            o.put("symbol", a.symbol);
            o.put("score", a.score);
            o.put("requires_visual_validation", a.requiresVisualValidation);
            o.put("reason", a.reason);
            o.put("confidence", a.confidence);
        }
        return arr;
    }
}