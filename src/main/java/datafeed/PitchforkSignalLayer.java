package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.*;

/**
 * Pitchfork Signal Layer (MTS Layer Family 'pitchfork').
 * Implements Modified Schiff Pitchfork geometry, anchored volume profile confluence (FORMULAS 18.1),
 * and resting limit tine-touch execution.
 *
 * <p>Reference Specifications:
 * - RESEARCH_PITCHFORK_LAYER.md: Rules P-01 (Pivots), P-02 (Schiff angle normalization), P-03 (80% ML rule).
 * - PHASE2_4H_POC_STUDY.md: 4H timeframe validation (1,273 setups, 2020-2026), proving that resting
 *   limit orders on tine retests eliminate fee drag (+0.05% to +0.88% net) and Value Area confluence
 *   boosts net return to +0.61% with a 1.63 Profit Factor.
 *
 * <p>Activation:
 * Controlled by JVM property {@code -Dmts.pitchfork=true} (default false).
 */
public final class PitchforkSignalLayer {

    public static final String FLAG = "mts.pitchfork";

    public static boolean enabled() {
        return Boolean.getBoolean(FLAG);
    }

    public static final double DEFAULT_W_BIN = 10.0; // FORMULAS 18.1 canonical bin width for BTC (10 USD)
    public static final double VA_RATIO = 0.70;      // 70% Value Area threshold
    public static final double STOP_OFFSET_PCT = 0.015; // 1.5% structural stop beyond tine
    public static final double POC_TOLERANCE_PCT = 0.015; // 1.5% POC confluence band
    public static final double TIGHT_POC_TOLERANCE_PCT = 0.0075; // 0.75% high conviction POC band

    public static class Pivot {
        public final int index;
        public final double price;
        public final boolean isHigh;
        public final long timestamp;

        public Pivot(int index, double price, boolean isHigh, long timestamp) {
            this.index = index;
            this.price = price;
            this.isHigh = isHigh;
            this.timestamp = timestamp;
        }
    }

    public static class VolumeProfile {
        public final double pocPrice;
        public final double vah;
        public final double val;
        public final double totalVolume;

        public VolumeProfile(double pocPrice, double vah, double val, double totalVolume) {
            this.pocPrice = pocPrice;
            this.vah = vah;
            this.val = val;
            this.totalVolume = totalVolume;
        }
    }

    public static class PitchforkGeometry {
        public final Pivot p0;
        public final Pivot p1;
        public final Pivot p2;
        public final double t0Eff;
        public final double p0Eff;
        public final double tm;
        public final double pm;
        public final double slope;
        public final double offsetUml;
        public final double offsetLml;
        public final double channelWidth;
        public final boolean isAscending;
        public final boolean p2IsLower;

        public PitchforkGeometry(Pivot p0, Pivot p1, Pivot p2) {
            this.p0 = p0;
            this.p1 = p1;
            this.p2 = p2;

            // Modified Schiff: shift P0 by 50% in price towards P1, keep original time
            this.t0Eff = (double) p0.index;
            this.p0Eff = p0.price + 0.5 * (p1.price - p0.price);

            // Midpoint of P1 and P2
            this.tm = ((double) p1.index + (double) p2.index) / 2.0;
            this.pm = (p1.price + p2.price) / 2.0;

            double dt = this.tm - this.t0Eff;
            if (dt <= 0) {
                throw new IllegalArgumentException("Invalid geometry: tm <= t0Eff");
            }
            this.slope = (this.pm - this.p0Eff) / dt;
            this.isAscending = this.slope > 0;

            // Calculate vertical offsets for parallel lines
            double mlAtT1 = this.p0Eff + this.slope * ((double) p1.index - this.t0Eff);
            double offsetP1 = p1.price - mlAtT1;

            double mlAtT2 = this.p0Eff + this.slope * ((double) p2.index - this.t0Eff);
            double offsetP2 = p2.price - mlAtT2;

            if (offsetP1 >= offsetP2) {
                this.offsetUml = offsetP1;
                this.offsetLml = offsetP2;
            } else {
                this.offsetUml = offsetP2;
                this.offsetLml = offsetP1;
            }

            this.p2IsLower = (offsetP2 <= 0.0);
            this.channelWidth = Math.abs(this.offsetUml - this.offsetLml);
        }

        public double getMl(double t) {
            return this.p0Eff + this.slope * (t - this.t0Eff);
        }

        public double getUml(double t) {
            return getMl(t) + this.offsetUml;
        }

        public double getLml(double t) {
            return getMl(t) + this.offsetLml;
        }
    }

    /**
     * Computes the uniform-spread Volume Profile over a set of bars (FORMULAS 18.1).
     */
    public static VolumeProfile computeVolumeProfile(double[] lows, double[] highs, double[] volumes, double w) {
        if (lows == null || lows.length == 0 || w <= 0) {
            return null;
        }
        int n = lows.length;
        double minPrice = Double.MAX_VALUE;
        double maxPrice = Double.MIN_VALUE;
        double totalVolume = 0.0;

        for (int i = 0; i < n; i++) {
            if (lows[i] < minPrice) minPrice = lows[i];
            if (highs[i] > maxPrice) maxPrice = highs[i];
            totalVolume += volumes[i];
        }

        if (totalVolume <= 0 || maxPrice <= minPrice) {
            return null;
        }

        int kMin = (int) Math.floor(minPrice / w);
        int kMax = (int) Math.floor(maxPrice / w);
        int numBins = kMax - kMin + 1;
        double[] binVol = new double[numBins];

        for (int i = 0; i < n; i++) {
            double l = lows[i];
            double h = highs[i];
            double v = volumes[i];
            if (v <= 0) continue;

            if (h <= l) {
                int k = (int) Math.floor(l / w) - kMin;
                if (k >= 0 && k < numBins) {
                    binVol[k] += v;
                }
            } else {
                double span = h - l;
                int kl = (int) Math.floor(l / w);
                int kh = (int) Math.floor(h / w);
                for (int k = kl; k <= kh; k++) {
                    double binLow = k * w;
                    double binHigh = (k + 1) * w;
                    double overlap = Math.max(0.0, Math.min(h, binHigh) - Math.max(l, binLow));
                    int binIdx = k - kMin;
                    if (binIdx >= 0 && binIdx < numBins) {
                        binVol[binIdx] += v * (overlap / span);
                    }
                }
            }
        }

        // POC: bin with highest volume (ties go to lower bin per FORMULAS 18.1)
        int pocIdx = 0;
        double maxBinVol = -1.0;
        for (int i = 0; i < numBins; i++) {
            if (binVol[i] > maxBinVol) {
                maxBinVol = binVol[i];
                pocIdx = i;
            }
        }
        double pocPrice = (kMin + pocIdx) * w + w / 2.0;

        // Value Area: 70% expansion from POC
        double targetVaVol = VA_RATIO * totalVolume;
        int lo = pocIdx;
        int hi = pocIdx;
        double acc = binVol[pocIdx];

        while (acc < targetVaVol && (lo > 0 || hi < numBins - 1)) {
            double vl = (lo > 0) ? binVol[lo - 1] : -1.0;
            double vh = (hi < numBins - 1) ? binVol[hi + 1] : -1.0;

            if (vl >= vh && lo > 0) {
                lo--;
                acc += vl;
            } else if (hi < numBins - 1) {
                hi++;
                acc += vh;
            } else if (lo > 0) {
                lo--;
                acc += vl;
            } else {
                break;
            }
        }

        double val = (kMin + lo) * w;
        double vah = (kMin + hi + 1) * w;

        return new VolumeProfile(pocPrice, vah, val, totalVolume);
    }

    /**
     * Extracts ZigZag pivots from high and low arrays.
     */
    public static List<Pivot> findPivotsZigZag(double[] highs, double[] lows, long[] timestamps, int lookback, double minChangePct) {
        List<Pivot> pivots = new ArrayList<>();
        if (highs == null || lows == null || highs.length < 2 * lookback + 1) {
            return pivots;
        }

        int n = highs.length;
        Boolean lastType = null; // true = peak, false = trough

        for (int i = lookback; i < n - lookback; i++) {
            boolean isLocalHigh = true;
            boolean isLocalLow = true;

            for (int j = 1; j <= lookback; j++) {
                if (highs[i] < highs[i - j] || highs[i] < highs[i + j]) {
                    isLocalHigh = false;
                }
                if (lows[i] > lows[i - j] || lows[i] > lows[i + j]) {
                    isLocalLow = false;
                }
            }

            long ts = (timestamps != null && i < timestamps.length) ? timestamps[i] : (long) i;

            if (isLocalHigh && (lastType == null || !lastType)) {
                if (pivots.isEmpty() || Math.abs(highs[i] - pivots.get(pivots.size() - 1).price) / pivots.get(pivots.size() - 1).price >= minChangePct) {
                    pivots.add(new Pivot(i, highs[i], true, ts));
                    lastType = true;
                }
            } else if (isLocalHigh && Boolean.TRUE.equals(lastType)) {
                // Swing extension: update peak if higher
                if (highs[i] > pivots.get(pivots.size() - 1).price) {
                    pivots.set(pivots.size() - 1, new Pivot(i, highs[i], true, ts));
                }
            } else if (isLocalLow && (lastType == null || lastType)) {
                if (pivots.isEmpty() || Math.abs(lows[i] - pivots.get(pivots.size() - 1).price) / pivots.get(pivots.size() - 1).price >= minChangePct) {
                    pivots.add(new Pivot(i, lows[i], false, ts));
                    lastType = false;
                }
            } else if (isLocalLow && Boolean.FALSE.equals(lastType)) {
                // Swing extension: update trough if lower
                if (lows[i] < pivots.get(pivots.size() - 1).price) {
                    pivots.set(pivots.size() - 1, new Pivot(i, lows[i], false, ts));
                }
            }
        }

        return pivots;
    }

    /**
     * Builds setup candidate ObjectNodes for active Pitchfork setups.
     */
    public static List<ObjectNode> detect(ObjectMapper mapper, ObjectNode root, JsonNode klines4h, JsonNode klines1m, String symbol) {
        List<ObjectNode> candidates = new ArrayList<>();
        if (root == null || mapper == null) {
            return candidates;
        }

        double currentPrice = root.has("current_price") ? root.get("current_price").asDouble() : 0.0;
        if (currentPrice <= 0) {
            return candidates;
        }

        // Parse 4H bars if available
        if (klines4h == null || klines4h.size() < 15) {
            return candidates;
        }

        int n4h = klines4h.size();
        double[] highs = new double[n4h];
        double[] lows = new double[n4h];
        double[] closes = new double[n4h];
        double[] volumes = new double[n4h];
        long[] timestamps = new long[n4h];

        for (int i = 0; i < n4h; i++) {
            JsonNode b = klines4h.get(i);
            timestamps[i] = b.get(0).asLong();
            highs[i] = b.get(2).asDouble();
            lows[i] = b.get(3).asDouble();
            closes[i] = b.get(4).asDouble();
            volumes[i] = b.size() > 5 ? b.get(5).asDouble() : 1.0;
        }

        int lookback = 4;
        double minChangePct = 0.03;
        List<Pivot> pivots = findPivotsZigZag(highs, lows, timestamps, lookback, minChangePct);
        if (pivots.size() < 3) {
            return candidates;
        }

        // Take latest confirmed triplet
        Pivot p0 = pivots.get(pivots.size() - 3);
        Pivot p1 = pivots.get(pivots.size() - 2);
        Pivot p2 = pivots.get(pivots.size() - 1);

        if (p0.isHigh == p1.isHigh || p1.isHigh == p2.isHigh) {
            return candidates; // Not alternating
        }

        PitchforkGeometry pf;
        try {
            pf = new PitchforkGeometry(p0, p1, p2);
        } catch (Exception e) {
            return candidates;
        }

        // Anchored Volume Profile over foundational swing P0 -> P2
        int p0Idx = Math.min(p0.index, p2.index);
        int p2Idx = Math.max(p0.index, p2.index);
        int segLen = p2Idx - p0Idx + 1;
        if (segLen < 2) return candidates;

        double[] subL = new double[segLen];
        double[] subH = new double[segLen];
        double[] subV = new double[segLen];
        System.arraycopy(lows, p0Idx, subL, 0, segLen);
        System.arraycopy(highs, p0Idx, subH, 0, segLen);
        System.arraycopy(volumes, p0Idx, subV, 0, segLen);

        VolumeProfile vp = computeVolumeProfile(subL, subH, subV, DEFAULT_W_BIN);
        if (vp == null) return candidates;

        // Confluence Gate
        boolean inValueArea = (p2.price >= vp.val && p2.price <= vp.vah);
        double pocDiff = Math.abs(p2.price - vp.pocPrice) / vp.pocPrice;
        boolean nearPoc = (pocDiff <= POC_TOLERANCE_PCT);
        boolean tightPoc = (pocDiff <= TIGHT_POC_TOLERANCE_PCT);

        // Require at least Value Area confluence or POC confluence (Phase 2 finding)
        if (!inValueArea && !nearPoc) {
            return candidates;
        }

        double currentBarT = (double) (n4h - 1);
        double mlNow = pf.getMl(currentBarT);
        double umlNow = pf.getUml(currentBarT);
        double lmlNow = pf.getLml(currentBarT);

        boolean isLong = !p2.isHigh; // Swing low -> bounce long towards ML
        String setupType = isLong ? "PF-REV-L" : "PF-REV-S";
        String direction = isLong ? "long" : "short";

        double entryPrice = isLong ? lmlNow : umlNow;
        double stopPrice = isLong ? entryPrice * (1.0 - STOP_OFFSET_PCT) : entryPrice * (1.0 + STOP_OFFSET_PCT);
        double targetPrice = mlNow;

        double risk = Math.abs(entryPrice - stopPrice);
        double reward = Math.abs(targetPrice - entryPrice);
        if (risk <= 0 || reward / risk < 1.5) {
            return candidates; // Fails R:R floor
        }

        double grossRR = reward / risk;
        double netRR = (reward - entryPrice * 0.0012) / (risk + entryPrice * 0.0012);
        double distPct = Math.abs(currentPrice - entryPrice) / currentPrice * 100.0;
        String tier = (distPct <= 0.1) ? "trigger_ready" : (distPct <= 0.5) ? "conditional" : "ignore";

        ObjectNode cand = mapper.createObjectNode();
        cand.put("setup_type", setupType);
        cand.put("direction", direction);

        ObjectNode zone = cand.putObject("zone");
        zone.put("name", isLong ? "pitchfork_lml" : "pitchfork_uml");
        zone.put("price", Math.round(entryPrice * 100.0) / 100.0);
        zone.put("type", "pitchfork_tine");

        ObjectNode math = cand.putObject("math");
        math.put("entry", Math.round(entryPrice * 100.0) / 100.0);
        math.put("stop", Math.round(stopPrice * 100.0) / 100.0);
        math.put("target", Math.round(targetPrice * 100.0) / 100.0);
        math.put("runner_target", Math.round((isLong ? targetPrice + pf.channelWidth : targetPrice - pf.channelWidth) * 100.0) / 100.0);
        math.put("gross_rr", Math.round(grossRR * 100.0) / 100.0);
        math.put("net_rr", Math.round(netRR * 100.0) / 100.0);
        math.put("rr_sanity", grossRR >= 1.5);
        math.put("net_rr_sanity", netRR >= 1.4);
        math.put("distance_pct", Math.round(distPct * 100.0) / 100.0);
        math.put("distance_cap", 0.5);
        math.put("tier", tier);
        math.put("substate", distPct <= 0.1 ? "at_zone" : (currentPrice > entryPrice ? "above" : "below"));

        ObjectNode pfNode = cand.putObject("pitchfork");
        pfNode.put("variant", "modified_schiff");
        pfNode.put("slope", Math.round(pf.slope * 100.0) / 100.0);
        pfNode.put("channel_width", Math.round(pf.channelWidth * 100.0) / 100.0);
        pfNode.put("p0_price", p0.price);
        pfNode.put("p1_price", p1.price);
        pfNode.put("p2_price", p2.price);
        pfNode.put("vp_poc", Math.round(vp.pocPrice * 100.0) / 100.0);
        pfNode.put("vp_val", Math.round(vp.val * 100.0) / 100.0);
        pfNode.put("vp_vah", Math.round(vp.vah * 100.0) / 100.0);
        pfNode.put("va_confluent", inValueArea);
        pfNode.put("poc_confluent", nearPoc);
        pfNode.put("tight_poc_confluent", tightPoc);

        ObjectNode proof = cand.putObject("proof");
        int proofCount = 0;
        if (inValueArea) proofCount++;
        if (nearPoc) proofCount++;
        if (grossRR >= 2.0) proofCount++;
        proof.put("proof_count", proofCount);
        proof.put("proof_va_confluent", inValueArea);
        proof.put("proof_poc_confluent", nearPoc);
        proof.put("proof_rr_favorable", grossRR >= 2.0);

        ObjectNode score = cand.putObject("score");
        score.put("raw", inValueArea ? (tightPoc ? 95 : 85) : 75);
        score.put("confidence", tightPoc ? "HIGH" : "MEDIUM");
        score.put("proof_count", proofCount);
        score.put("confluence_bonus", inValueArea ? 20 : 10);

        candidates.add(cand);
        return candidates;
    }
}

