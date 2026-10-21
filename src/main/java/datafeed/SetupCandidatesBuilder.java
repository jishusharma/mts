package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Builds the setup_candidates array for the MTS screener.
 * Implements all deterministic math + proof detection from the DSA task 012 spec.
 */
public class SetupCandidatesBuilder {

    // Zone representation
    private static class Zone {
        String name;
        String type;       // e.g., "pf_vah", "weekly_poc", etc.
        double price;
        String sourceTF;   // for tie-breaking (weekly > daily > 4h > pf > prior_day > 1h > 15m > 5m)
        int tfRank;        // higher = stronger
    }

    // Candidate representation
    private static class Candidate {
        Zone zone;
        String setupType;  // ct_short, ct_long, scalp_short, scalp_long, tc_short, tc_long, etc.
        String direction;  // "short" or "long"
        double stop;
        double target;
        double runnerTarget;  // next node beyond target, 0 if none
        boolean valid;
        double grossRR;
        double netRR;
        boolean rrSanity;
        boolean netRrSanity;
        int rawScore;
        String confidence;
        int proofCount;
        int confluenceBonus;
        JsonNode proofNode; // built later
    }

    private static final double VALUE_AREA_PCT = 0.70;
    private static final double CONFLUENCE_DIST_PCT = 0.3; // 0.3%
    // MIN_STOP_PCT (0.1% stop floor, A04) removed per T3 ruling (T3_STOP_RULING_2026-10-01): NO-SOURCE.
    private static final int MAX_CANDIDATES = 3;

    /** B066: trigger_ready only within 0.1% of price (a 150 pt / 0.19% zone is conditional); beyond the cap is ignore. */
    static String tierFor(double distPct, double cap) {
        return (distPct <= 0.1) ? "trigger_ready" : (distPct <= cap) ? "conditional" : "ignore";
    }

    public static ArrayNode build(ObjectMapper mapper, ObjectNode root, Map<String, JsonNode> mtf, JsonNode klines1m) {
        return build(mapper, root, mtf, klines1m, null);
    }

    /**
     * @param fadeKlines1m optional longer 1m series for the family A fade call only (card tom-v2-recall-fire-rate: the
     *                     detector needs 21 sessions, a snapshot carries 24 h). Null = use klines1m. Nothing else reads it.
     */
    public static ArrayNode build(ObjectMapper mapper, ObjectNode root, Map<String, JsonNode> mtf, JsonNode klines1m,
                                  JsonNode fadeKlines1m) {
        ArrayNode candidatesArray = mapper.createArrayNode();
        if (root == null || klines1m == null || klines1m.size() < 20) {
            return candidatesArray; // empty
        }

        double currentPrice = root.get("current_price").asDouble();
        final String sym = root.path("asset").asText(null);  // instrument for the per-market fee (null/unknown -> BTC fee, unchanged)
        final double netRrFloor = NetRrFloor.read();  // single source: MyTradingSys/system/net_rr_floor.json; NaN (unreadable) fails every >= below
        final double runnerMinDistancePct = RunnerMinDistance.read();  // MyTradingSys/system/runner_min_distance.json; NaN -> no runner

        // Step 1: State classification
        String state = classifyState(root);

        // Step 2: Directional filter
        List<String> evaluatedDirections = determineDirections(root);

        // Step 3: Extract zones
        List<Zone> zones = extractZones(root, currentPrice);

        // Step 4: Distance + cap + tier; keep only those with tier != ignore
        List<Zone> filteredZones = new ArrayList<>();
        for (Zone z : zones) {
            double distPct = Math.abs(currentPrice - z.price) / currentPrice * 100.0;
            double cap = getDistanceCap(z.type);
            String tier = tierFor(distPct, cap);
            if (!"ignore".equals(tier)) {
                filteredZones.add(z);
            }
        }

        // Step 5: Setup type assignment (per zone + direction + state)
        List<Candidate> candidates = new ArrayList<>();
        for (Zone z : filteredZones) {
            List<String> possibleDirections = evaluatedDirections;
            for (String dir : possibleDirections) {
                String setupType = determineSetupType(z, dir, state);
                if (setupType != null) {
                    Candidate c = new Candidate();
                    c.zone = z;
                    c.direction = dir;
                    c.setupType = setupType;
                    c.stop = 0;
                    c.target = 0;
                    candidates.add(c);
                }
            }
        }

        // Step 6: Stop + target selection
        for (Candidate c : candidates) {
            double zonePrice = c.zone.price;
            String swingTF = getSwingTF(c.zone.type);
            JsonNode structureNode = root.get("structure");
            // RULE TOM-074/TOM-073/TOM-072 (stop beyond last swing / last liquidity); the former 0.2% fallback (A03) and 0.1% floor (A04) were NO-SOURCE and are removed per T3 ruling
            double swingHigh = 0, swingLow = 0;
            boolean tfStale = false;
            if (structureNode != null && structureNode.has(swingTF)) {
                JsonNode tfNode = structureNode.get(swingTF);
                tfStale = tfNode.path("stale").asBoolean(false);
                if (!tfStale) {
                    swingHigh = tfNode.get("swing_high").asDouble();
                    swingLow = tfNode.get("swing_low").asDouble();
                }
            }

            // A03/A04 removed per T3 ruling: a stop exists only when a swing lies beyond the zone (matches the
            // Python path, math_object_builder.py); otherwise the candidate is dropped (fail closed). No fallback, no widening.
            if ("short".equals(c.direction)) {
                c.stop = swingHigh > zonePrice ? swingHigh : 0;
            } else { // long
                c.stop = (swingLow > 0 && swingLow < zonePrice) ? swingLow : 0;
            }
            if (c.stop <= 0) {
                continue; // c.valid stays false -> removed by removeIf below
            }

            // Target selection. RULE TOM-018/TOM-102: target = the next high volume price/area (POCs, HVNs).
            // Operator ruling 2026-10-03: the 2.0R-3.5R window, the VAL/VAH, prior-day high/low and VWAP members and the
            // gross 1.5 R:R drop were NO-SOURCE (A07-A10) and are removed.
            // Rule: nearest node in trade direction whose netRR >= NetRrFloor.read(); if none qualifies, the farthest node
            // in direction (still reported, the verdict net_rr gate decides). No node in direction -> candidate dropped.
            List<Double> nodes = new ArrayList<>();
            addIfPresent(root, "weekly_vp", "poc", nodes);
            addIfPresent(root, "daily_vp", "poc", nodes);
            addIfPresent(root, "intraday_4h_vp", "poc", nodes);
            addIfPresent(root, "prior_day", "poc", nodes);
            addHvns(root, "weekly_vp", nodes);
            addHvns(root, "daily_vp", nodes);
            addHvns(root, "intraday_4h_vp", nodes);
            double[] picked = pickTarget(nodes, zonePrice, c.stop, "short".equals(c.direction), netRrFloor, runnerMinDistancePct, sym);
            c.target = picked[0];
            c.runnerTarget = picked[1];
            if (c.target == 0) {
                continue;
            }

            // Step 7: R:R
            if (c.stop > 0 && c.target > 0 && c.stop != zonePrice && c.target != zonePrice) {
                double risk = Math.abs(zonePrice - c.stop);
                double reward = Math.abs(c.target - zonePrice);
                c.grossRR = reward / risk;
                c.netRR = ExecutionMathConstants.netRR(sym, zonePrice, c.target, c.stop);  // B070: fee model, was gross * 0.75
                c.rrSanity = c.grossRR >= 1.5;   // advisory output flag only; no longer drops the candidate
                c.netRrSanity = c.netRR >= netRrFloor;
                c.valid = true;
            }
        }
        // Remove candidates with no usable node / stop (the verdict net_rr gate decides everything else)
        candidates.removeIf(c -> !c.valid);

        // Step 8: Confluence detection
        Map<Zone, Integer> confluenceCount = computeConfluence(candidates);
        for (Candidate c : candidates) {
            c.confluenceBonus = confluenceCount.getOrDefault(c.zone, 0) > 1 ? 10 : 0;
        }

        // Step 9: Proof detection using klines1m
        for (Candidate c : candidates) {
            ProofResult proofs = detectProofs(c, klines1m, currentPrice, root, filteredZones);
            c.proofCount = proofs.countSignals(c.direction);
            c.proofNode = proofs.toJson(mapper);
        }

        // Step 10: Scoring
        for (Candidate c : candidates) {
            int raw = 50;
            raw += c.proofCount * 7;
            raw += c.confluenceBonus;
            raw = Math.min(95, raw);
            c.rawScore = raw;
            c.confidence = raw >= 70 ? "B" : raw >= 55 ? "C+" : raw >= 40 ? "C" : "D";
        }

        // Step 11: Ranking and output
        candidates.sort((a, b) -> {
            if (b.rawScore != a.rawScore) return b.rawScore - a.rawScore;
            return b.zone.tfRank - a.zone.tfRank; // higher TF first
        });

        int rank = 1;
        for (Candidate c : candidates) {
            if (rank > MAX_CANDIDATES) break;
            ObjectNode candNode = candidatesArray.addObject();
            candNode.put("rank", rank++);
            candNode.put("setup_type", c.setupType);
            candNode.put("direction", c.direction);
            ObjectNode zoneNode = candNode.putObject("zone");
            zoneNode.put("name", c.zone.name);
            zoneNode.put("price", Math.round(c.zone.price * 100.0) / 100.0);
            zoneNode.put("type", c.zone.type);
            ObjectNode mathNode = candNode.putObject("math");
            mathNode.put("distance_pct", Math.round(Math.abs(currentPrice - c.zone.price) / currentPrice * 10000.0) / 100.0);
            mathNode.put("distance_cap", getDistanceCap(c.zone.type));
            double dist = Math.abs(currentPrice - c.zone.price) / currentPrice * 100;
            mathNode.put("tier", tierFor(dist, getDistanceCap(c.zone.type)));
            double distFromZone = Math.abs(currentPrice - c.zone.price) / c.zone.price;
mathNode.put("substate", distFromZone <= 0.001 ? "at_zone" : (currentPrice > c.zone.price ? "above" : "below"));
            mathNode.put("stop", Math.round(c.stop * 100.0) / 100.0);
            mathNode.put("target", Math.round(c.target * 100.0) / 100.0);
            mathNode.put("runner_target", Math.round(c.runnerTarget * 100.0) / 100.0);
            mathNode.put("gross_rr", Math.round(c.grossRR * 100.0) / 100.0);
            mathNode.put("net_rr", Math.round(c.netRR * 100.0) / 100.0);
            mathNode.put("rr_sanity", c.rrSanity);
            mathNode.put("net_rr_sanity", c.netRrSanity);
            candNode.set("proof", c.proofNode);
            ObjectNode scoreNode = candNode.putObject("score");
            scoreNode.put("raw", c.rawScore);
            scoreNode.put("confidence", c.confidence);
            scoreNode.put("proof_count", c.proofCount);
            scoreNode.put("confluence_bonus", c.confluenceBonus);
        }
        // Card tom-encode-spike-fade (TOM_LAYER_V2_SPEC section 15): family A fade_short, PRICE arm; flag off = untouched.
        if (SpikeFadeDetector.enabled()) {
            JsonNode fadeSeries = fadeKlines1m != null ? fadeKlines1m : klines1m;
            ObjectNode fade = SpikeFadeDetector.detect(mapper, root, fadeSeries, state, sym);
            if (fade != null) {
                ObjectNode ranked = mapper.createObjectNode();
                ranked.put("rank", candidatesArray.size() + 1);
                ranked.setAll(fade);
                ranked.put("arm", "price");
                candidatesArray.add(ranked);
                // Card tom-encode-fade-profile-proofs (spec 12): PROFILE arm beside the PRICE arm, a separate candidate.
                if (fadeSeries != null) {
                    ObjectNode prof = SpikeFadeProfile.build(mapper, fade, new SpikeFadeDetector.Bars(fadeSeries), sym);
                    if (prof != null) {
                        ObjectNode pr = mapper.createObjectNode();
                        pr.put("rank", candidatesArray.size() + 1);
                        pr.setAll(prof);
                        candidatesArray.add(pr);
                    }
                }
            }
            // Card tom-encode-fade-entry-paths (spec 2.3, 2.6 A-M5): paths A2 / A3 beside A1, gated by the session attempt state.
            if (fadeSeries != null && fadeSeries.size() >= 2) {
                for (ObjectNode path : SpikeFadePaths.detect(mapper, root, new SpikeFadeDetector.Bars(fadeSeries), state, sym,
                        SpikeFadeSessionState.shared())) {
                    ObjectNode ranked = mapper.createObjectNode();
                    ranked.put("rank", candidatesArray.size() + 1);
                    ranked.setAll(path);
                    ranked.put("arm", "price");
                    candidatesArray.add(ranked);
                }
            }
        }
        // Pitchfork Layer: Modified Schiff tine-bounce candidates with Volume Profile confluence.
        if (PitchforkSignalLayer.enabled()) {
            JsonNode klines4h = mtf != null ? mtf.get("4h") : null;
            List<ObjectNode> pfCandidates = PitchforkSignalLayer.detect(mapper, root, klines4h, klines1m, sym);
            for (ObjectNode pfNode : pfCandidates) {
                pfNode.put("rank", candidatesArray.size() + 1);
                candidatesArray.add(pfNode);
            }
        }
        return candidatesArray;
    }

    // ---------- Helper methods ----------

    // RULE TOM-030/TOM-031 (balance), TOM-140/TOM-056 (trend_unhealthy); thresholds NO-SOURCE (PROVENANCE_AUDIT_TOM M-rows)
    private static String classifyState(ObjectNode root) {
        // Rewritten 2026-09-17 per Rule 32. Old version read daily_vp.shape=="B"
        // and returned balance. buildVp emitted "B" for bell shapes, so it fired
        // on all 2090 snapshots on disk. Engine saw balance always; emitted
        // scalp_short/long at VWAP in trends. Now uses real signals.
        // Rule 32 test: 3/3 outside-VA snapshots changed to trend_healthy.
        String vwapSlope = root.get("conditions").get("vwap_slope").asText();
        String cvdSlope = root.get("conditions").get("cvd_slope").asText();
        String priceVsVa = root.get("conditions").get("price_vs_va").asText();
        if (("flat".equals(vwapSlope) || "sideways".equals(vwapSlope))
                && "flat".equals(cvdSlope)
                && "in_va".equals(priceVsVa)) {
            return "balance";
        }
        if ("divergent".equals(cvdSlope)) return "trend_unhealthy";
        if ("above_vah".equals(priceVsVa) || "below_val".equals(priceVsVa)) return "trend_healthy";
        if ("aligned".equals(cvdSlope)) return "trend_healthy";
        return "balance";
    }

    // RULE TOM-142 (price vs yesterday VAL/VPOC decides which side is tradable)
    private static List<String> determineDirections(ObjectNode root) {
        String priceVsVa = root.get("conditions").get("price_vs_va").asText();
        String priceVsPoc = root.get("conditions").get("price_vs_poc").asText();
        List<String> dirs = new ArrayList<>();
        if ("above_vah".equals(priceVsVa)) {
            dirs.add("short");
            dirs.add("long");
        } else if ("below_val".equals(priceVsVa)) {
            dirs.add("long");
        } else { // in_va
            if ("above".equals(priceVsPoc)) {
                dirs.add("short");
            } else if ("below".equals(priceVsPoc)) {
                dirs.add("long");
            } else {
                dirs.add("short");
                dirs.add("long");
            }
        }
        return dirs;
    }

    // RULE TOM-166 (overlaps: volume nodes, value highs, POCs), TOM-144 (VPOC as equilibrium level); zone list = A07
    private static List<Zone> extractZones(ObjectNode root, double currentPrice) {
        List<Zone> zones = new ArrayList<>();
        addZoneIfPresent(root, "weekly_vp", "poc", "weekly_poc", zones, 10);
        addZoneIfPresent(root, "weekly_vp", "vah", "weekly_vah", zones, 10);
        addZoneIfPresent(root, "weekly_vp", "val", "weekly_val", zones, 10);
        addZoneIfPresent(root, "daily_vp", "poc", "daily_poc", zones, 9);
        addZoneIfPresent(root, "daily_vp", "vah", "daily_vah", zones, 9);
        addZoneIfPresent(root, "daily_vp", "val", "daily_val", zones, 9);
        // DEMOTED 2026-09-24: pf_poc, pf_vah, pf_val removed from candidate zone list.
        // Module, not core. PROJECT_VISION.md doctrine; crypto_adaptations.md hack #6.
        addZoneIfPresent(root, "intraday_4h_vp", "poc", "4h_poc", zones, 7);
        addZoneIfPresent(root, "intraday_4h_vp", "vah", "4h_vah", zones, 7);
        addZoneIfPresent(root, "intraday_4h_vp", "val", "4h_val", zones, 7);
        addZoneIfPresent(root, "vwap", "price", "vwap", zones, 6);
        // vwap bands +1, +2, -1, -2
        JsonNode vwapBands = root.get("vwap").get("bands");
        if (vwapBands != null) {
            addZoneIfPresent(vwapBands, "+1s", "vwap_band_+1", zones, 6);
            addZoneIfPresent(vwapBands, "+2s", "vwap_band_+2", zones, 6);
            addZoneIfPresent(vwapBands, "-1s", "vwap_band_-1", zones, 6);
            addZoneIfPresent(vwapBands, "-2s", "vwap_band_-2", zones, 6);
        }
        addZoneIfPresent(root, "prior_day", "poc", "prior_day_poc", zones, 5);
        addZoneIfPresent(root, "prior_day", "vah", "prior_day_vah", zones, 5);
        addZoneIfPresent(root, "prior_day", "val", "prior_day_val", zones, 5);
        addZoneIfPresent(root, "prior_day", "close", "prior_day_close", zones, 5);
        // structure swings
        JsonNode structure = root.get("structure");
        if (structure != null) {
            // B065: skip swing zones whose source tf is flagged stale in the snapshot.
            boolean stale1h  = structure.path("1h").path("stale").asBoolean(false);
            boolean stale15m = structure.path("15m").path("stale").asBoolean(false);
            boolean stale5m  = structure.path("5m").path("stale").asBoolean(false);
            if (!stale1h) {
                addZoneIfPresent(structure, "1h", "swing_high", "1h_swing_high", zones, 4);
                addZoneIfPresent(structure, "1h", "swing_low", "1h_swing_low", zones, 4);
            }
            if (!stale15m) {
                addZoneIfPresent(structure, "15m", "swing_high", "15m_swing_high", zones, 3);
                addZoneIfPresent(structure, "15m", "swing_low", "15m_swing_low", zones, 3);
            }
            if (!stale5m) {
                addZoneIfPresent(structure, "5m", "swing_high", "5m_swing_high", zones, 2);
                addZoneIfPresent(structure, "5m", "swing_low", "5m_swing_low", zones, 2);
            }
        }
        // FVG nearest
        JsonNode fvg = root.get("conditions").get("fvg_nearest_unfilled");
        if (fvg != null && !fvg.isNull()) {
            double top = fvg.get("top").asDouble();
            double bottom = fvg.get("bottom").asDouble();
            // add mid? spec says zone source is conditions.fvg_nearest_unfilled, type fvg
            // Use mid point as zone price
            double mid = (top + bottom) / 2;
            Zone z = new Zone();
            z.name = "fvg_nearest";
            z.type = "fvg";
            z.price = mid;
            z.tfRank = 1;
            zones.add(z);
        }
        // Naked POCs: load from NakedPocTracker (may fail silently)
        try {
            NakedPocTracker tracker = new NakedPocTracker(root.get("asset").asText());
            JsonNode nakedPocs = tracker.getNakedPocsNode();
            if (nakedPocs.has("naked_pocs")) {
                for (JsonNode np : nakedPocs.get("naked_pocs")) {
                    double price = np.get("poc").asDouble();
                    Zone z = new Zone();
                    z.name = "naked_poc_" + np.get("date").asText();
                    z.type = "weekly_poc"; // per spec
                    z.price = price;
                    z.tfRank = 11; // treat as weekly-level
                    zones.add(z);
                }
            }
        } catch (Exception e) {
            // ignore
        }
        // v1.3.1 fix: vwap.price type must be "vwap_band"
        for (Zone z : zones) {
            if ("vwap".equals(z.name) && "vwap".equals(z.type)) {
                z.type = "vwap_band";
            }
        }
        return zones;
    }

    private static void addZoneIfPresent(JsonNode node, String field, String zoneName, List<Zone> zones, int tfRank) {
        addZoneIfPresent(node, field, zoneName, zones, tfRank, false);
    }

    private static void addZoneIfPresent(JsonNode node, String field, String zoneName, List<Zone> zones, int tfRank, boolean isSwing) {
        if (node != null && node.has(field) && !node.get(field).isNull()) {
            double price = node.get(field).asDouble();
            if (price > 0) {
                Zone z = new Zone();
                z.name = zoneName;
                z.type = zoneName; // simplify; later mapping done in getDistanceCap
                z.price = price;
                z.tfRank = tfRank;
                zones.add(z);
            }
        }
    }

    private static void addZoneIfPresent(JsonNode parent, String child, String field, String zoneName, List<Zone> zones, int tfRank) {
        if (parent != null && parent.has(child) && !parent.get(child).isNull()) {
            JsonNode childNode = parent.get(child);
            if (childNode.has(field) && !childNode.get(field).isNull()) {
                double price = childNode.get(field).asDouble();
                if (price > 0) {
                    Zone z = new Zone();
                    z.name = zoneName;
                    z.type = zoneName;
                    z.price = price;
                    z.tfRank = tfRank;
                    zones.add(z);
                }
            }
        }
    }

    private static double getDistanceCap(String zoneType) {
        if (zoneType.startsWith("weekly_")) return 0.5;
        if (zoneType.startsWith("daily_") || zoneType.startsWith("pf_") || zoneType.startsWith("4h_") || zoneType.startsWith("prior_day_")) return 0.4;
        if (zoneType.startsWith("1h_swing_") || zoneType.startsWith("15m_swing_")) return zoneType.startsWith("1h_") ? 0.5 : 0.3;
        if (zoneType.startsWith("5m_swing_")) return 0.3;
        if (zoneType.startsWith("vwap_band")) return 0.2;
        if (zoneType.equals("fvg")) return 0.2;
        if (zoneType.equals("vwap")) return 0.2;
        return 0.4; // default
    }

    // RULE TOM-140 (POC counter-trend only in unhealthy trend), TOM-030 (balance -> scalp at VWAP)
    private static String determineSetupType(Zone zone, String direction, String state) {
        String zoneType = zone.type;
        boolean isShort = "short".equals(direction);
        if ("transition".equals(state)) return null;
        // CT setups
        if (zoneType.contains("vah") || zoneType.contains("swing_high") || zoneType.equals("prior_day_vah")) {
            if ("trend_healthy".equals(state)) return null;
            return isShort ? "ct_short" : null;
        }
        if (zoneType.contains("val") || zoneType.contains("swing_low") || zoneType.equals("prior_day_val")) {
            return isShort ? null : "ct_long";
        }
        if (zoneType.contains("poc")) {
            // POC: CT only in unhealthy trend
            if ("trend_unhealthy".equals(state)) {
                return isShort ? "ct_short" : "ct_long";
            }
            return null;
        }
        if (zoneType.equals("vwap") || zoneType.startsWith("vwap_band")) {
            // Scalp if sideways
            if ("balance".equals(state) || "sideways".equals(state)) {
                return isShort ? "scalp_short" : "scalp_long";
            }
            // TC long: pullback to VWAP in a healthy uptrend
            if ("trend_healthy".equals(state) && !isShort) return "tc_long";
            return null;
        }
        if (zoneType.equals("fvg")) {
            return null; // FVG not a setup zone, only exit
        }
        if (zoneType.equals("prior_day_close")) {
            return isShort ? "ct_short" : "ct_long"; // simplified
        }
        return null;
    }

    private static String getSwingTF(String zoneType) {
        if (zoneType.startsWith("weekly_")) return "1h";
        if (zoneType.startsWith("daily_") || zoneType.startsWith("pf_") || zoneType.startsWith("4h_") || zoneType.startsWith("prior_day_")) return "15m";
        if (zoneType.startsWith("vwap") || zoneType.equals("fvg") || zoneType.startsWith("5m_swing_")) return "5m";
        if (zoneType.startsWith("15m_swing_")) return "15m";
        if (zoneType.startsWith("1h_swing_")) return "1h";
        return "15m"; // default
    }

    /** pickTarget with no runner minimum distance (any strictly farther node is the runner). */
    static double[] pickTarget(List<Double> nodes, double zonePrice, double stop, boolean isShort, double netRrFloor) {
        return pickTarget(nodes, zonePrice, stop, isShort, netRrFloor, 0.0);
    }

    /**
     * Target pick from volume nodes (POC/HVN). Returns {target, runner_target}; {0,0} when no node lies in the trade
     * direction. Nearest node first; the first whose netRR >= floor wins, else the farthest node. runner = the next node
     * beyond the target whose distance from the target is at least runnerMinDistancePct percent of the target price
     * (nodes closer than that are skipped), 0 if none. NaN floor never qualifies (fail closed -> farthest); NaN
     * runnerMinDistancePct never qualifies (fail closed -> no runner).
     */
    static double[] pickTarget(List<Double> nodes, double zonePrice, double stop, boolean isShort, double netRrFloor,
                               double runnerMinDistancePct) {
        return pickTarget(nodes, zonePrice, stop, isShort, netRrFloor, runnerMinDistancePct, null);
    }

    static double[] pickTarget(List<Double> nodes, double zonePrice, double stop, boolean isShort, double netRrFloor,
                               double runnerMinDistancePct, String symbol) {
        List<Double> dir = new ArrayList<>();
        for (double p : nodes) {
            if (isShort ? p < zonePrice : p > zonePrice) dir.add(p);
        }
        if (dir.isEmpty()) return new double[]{0, 0};
        dir.sort((x, y) -> Double.compare(Math.abs(x - zonePrice), Math.abs(y - zonePrice)));
        int idx = dir.size() - 1;  // fallback: farthest
        for (int i = 0; i < dir.size(); i++) {
            if (ExecutionMathConstants.netRR(symbol, zonePrice, dir.get(i), stop) >= netRrFloor) { idx = i; break; }
        }
        double target = dir.get(idx);
        double runner = 0;
        for (int i = idx + 1; i < dir.size(); i++) {
            if (Math.abs(dir.get(i) - zonePrice) > Math.abs(target - zonePrice)
                    && Math.abs(dir.get(i) - target) / target * 100.0 >= runnerMinDistancePct) { runner = dir.get(i); break; }
        }
        return new double[]{target, runner};
    }

    private static void addIfPresent(ObjectNode root, String objName, String field, List<Double> list) {
        JsonNode obj = root.get(objName);
        if (obj != null && obj.has(field) && !obj.get(field).isNull()) {
            double val = obj.get(field).asDouble();
            if (val > 0) list.add(val);
        }
    }

    /** Adds numeric, positive entries of root[objName].hvns to list (non-numeric / non-positive ignored). */
    static void addHvns(ObjectNode root, String objName, List<Double> list) {
        JsonNode obj = root.get(objName);
        if (obj == null || !obj.has("hvns") || !obj.get("hvns").isArray()) return;
        for (JsonNode n : obj.get("hvns")) {
            if (n.isNumber() && n.asDouble() > 0) list.add(n.asDouble());
        }
    }

    private static Map<Zone, Integer> computeConfluence(List<Candidate> candidates) {
        Map<Zone, Integer> counts = new HashMap<>();
        List<Zone> allZones = candidates.stream().map(c -> c.zone).distinct().collect(Collectors.toList());
        for (Zone z : allZones) {
            int count = 0;
            for (Zone other : allZones) {
                if (z == other) continue;
                double dist = Math.abs(z.price - other.price) / z.price * 100;
                if (dist <= CONFLUENCE_DIST_PCT) count++;
            }
            counts.put(z, count + 1); // +1 for itself
        }
        return counts;
    }

    // Proof detection

    private static class ProofResult {
        String rejectionWick = "NONE";
        boolean absorptionDetected = false;
        String absorptionStrength = "none";
        int absorptionCandleCount = 0;
        double absorptionVolRatio = 0;
        boolean finishedAuctionDetected = false;
        String finishedAuctionDirection = "";
        double finishedAuctionExtremeDelta = 0;
        double finishedAuctionReversalDelta = 0;
        boolean finishedAuctionFollowThrough = false;
        boolean deltaFlipDetected = false;
        boolean deltaFlipFromNegative = false;
        boolean deltaFlipAtZone = false;
        double deltaFlipZoneLevel = 0;
        int deltaFlipCandlesSince = 0;
        boolean volumeSpikeDetected = false;
        double volumeSpikeMagnitude = 0;
        boolean volumeSpikeAtLevel = false;
        double volumeSpikeLevel = 0;
        boolean speedPickingUp = false;
        double speedScore = 0;
        String speedDirection = "";
        double speedAtrRatio = 0;
        int speedConsecutiveLarge = 0;
        boolean cvdAligned = false;
        Double bookImbalance = null;   // null = no order-book data (historical/BT); never 0.0 on that path
        // Proximity fields (0.1% threshold)
        double rejectionWickProximityPct = 0.0;
        double rejectionWickActualLevel = 0.0;
        double deltaFlipProximityPct = 0.0;
        double deltaFlipActualLevel = 0.0;
        double speedProximityPct = 0.0;
        double speedActualLevel = 0.0;
        double volumeSpikeProximityPct = 0.0;
        double volumeSpikeActualLevel = 0.0;

        int countSignals(String direction) {
            int count = 0;
            if (!"NONE".equals(rejectionWick)) count++;
            if (absorptionDetected) count++;
            if (finishedAuctionDetected) {
                // D4: count only when the exhausted side is opposite the trade direction
                // (long favours a finished sell-side auction; short favours a finished buy-side auction).
                boolean favoursTrade = "long".equals(direction) ? "sell".equals(finishedAuctionDirection) : "buy".equals(finishedAuctionDirection);
                if (favoursTrade) count++;
            }
            if (deltaFlipDetected && deltaFlipAtZone) count++;
            // B144: volume spike (2.0x over 240 bars) has no source (operator D17): not counted, still emitted in the proof JSON.
            // D4: speed proxy no longer counted toward proof (still emitted in the proof JSON).
            if (cvdAligned) count++;
            // B131: book_imbalance is not counted (no Tom source; ask-heavy side is far more common, so it
            // gave every short +1 and every long +0). Still emitted in the proof JSON.
            return count;
        }

        JsonNode toJson(ObjectMapper mapper) {
            ObjectNode proof = mapper.createObjectNode();
            proof.put("rejection_wick", rejectionWick);
            if (!"NONE".equals(rejectionWick)) {
                proof.put("rejection_wick_proximity_pct", Math.round(rejectionWickProximityPct * 10000.0) / 10000.0);
                proof.put("rejection_wick_actual_level", Math.round(rejectionWickActualLevel * 100.0) / 100.0);
            }
            ObjectNode absorption = proof.putObject("absorption");
            absorption.put("detected", absorptionDetected);
            absorption.put("strength", absorptionStrength);
            absorption.put("candle_count", absorptionCandleCount);
            absorption.put("vol_ratio", Math.round(absorptionVolRatio * 100.0) / 100.0);
            ObjectNode finished = proof.putObject("finished_auction");
            finished.put("detected", finishedAuctionDetected);
            finished.put("direction", finishedAuctionDirection);
            finished.put("extreme_delta", finishedAuctionExtremeDelta);
            finished.put("reversal_delta", finishedAuctionReversalDelta);
            finished.put("follow_through", finishedAuctionFollowThrough);
            ObjectNode deltaFlip = proof.putObject("delta_flip");
            deltaFlip.put("detected", deltaFlipDetected && deltaFlipAtZone);
            deltaFlip.put("from_negative", deltaFlipFromNegative);
            deltaFlip.put("at_zone", deltaFlipAtZone);
            deltaFlip.put("zone_level", Math.round(deltaFlipZoneLevel * 100.0) / 100.0);
            deltaFlip.put("candles_since", deltaFlipCandlesSince);
            if (deltaFlipDetected) {
                deltaFlip.put("actual_level", Math.round(deltaFlipActualLevel * 100.0) / 100.0);
                deltaFlip.put("proximity_pct", Math.round(deltaFlipProximityPct * 10000.0) / 10000.0);
            }
            ObjectNode volSpike = proof.putObject("volume_spike");
            volSpike.put("detected", volumeSpikeDetected && volumeSpikeAtLevel);
            volSpike.put("magnitude", Math.round(volumeSpikeMagnitude * 100.0) / 100.0);
            volSpike.put("at_level", volumeSpikeAtLevel);
            volSpike.put("level", Math.round(volumeSpikeLevel * 100.0) / 100.0);
            if (volumeSpikeDetected) {
                volSpike.put("actual_level", Math.round(volumeSpikeActualLevel * 100.0) / 100.0);
                volSpike.put("proximity_pct", Math.round(volumeSpikeProximityPct * 10000.0) / 10000.0);
            }
            ObjectNode speed = proof.putObject("speed");
            speed.put("picking_up", speedPickingUp);
            speed.put("regime", speedScore < 3 ? "quiet" : speedScore <= 6 ? "building" : speedScore <= 10 ? "active" : "volatile");
            speed.put("score", Math.round(speedScore * 100.0) / 100.0);
            speed.put("direction", speedDirection);
            speed.put("atr_ratio", Math.round(speedAtrRatio * 100.0) / 100.0);
            speed.put("consecutive_large", speedConsecutiveLarge);
            if (speedPickingUp) {
                speed.put("actual_level", Math.round(speedActualLevel * 100.0) / 100.0);
                speed.put("proximity_pct", Math.round(speedProximityPct * 10000.0) / 10000.0);
            }
            proof.put("cvd_aligned", cvdAligned);
            if (bookImbalance == null) proof.putNull("book_imbalance");
            else proof.put("book_imbalance", Math.round(bookImbalance * 100.0) / 100.0);
            return proof;
        }
    }

    private static ProofResult detectProofs(Candidate c, JsonNode klines1m, double currentPrice, ObjectNode root, List<Zone> allZones) {
        ProofResult res = new ProofResult();
        double zonePrice = c.zone.price;
        String direction = c.direction;

        // Extract arrays for computation
        int n = klines1m.size();
        double[] closes = new double[n];
        double[] opens = new double[n];
        double[] highs = new double[n];
        double[] lows = new double[n];
        double[] volumes = new double[n];
        double[] deltas = new double[n];
        for (int i = 0; i < n; i++) {
            JsonNode bar = klines1m.get(i);
            opens[i] = bar.get(1).asDouble();
            highs[i] = bar.get(2).asDouble();
            lows[i] = bar.get(3).asDouble();
            closes[i] = bar.get(4).asDouble();
            volumes[i] = bar.get(5).asDouble();
            double takerBuy = bar.get(9).asDouble();
            deltas[i] = 2 * takerBuy - volumes[i];
        }

        // 9.1 rejection_wick (no proximity gate; wick must touch zone)
        String bestWickQuality = "NONE";
        double bestProximityPct = Double.MAX_VALUE;
        double bestActualLevel = 0.0;
        for (int i = Math.max(0, n - 20); i < n; i++) {
            boolean touchAndReject = false;
            double wickExtreme = 0.0;
            if ("short".equals(direction)) { // resistance rejection
                wickExtreme = highs[i];
                if (highs[i] >= zonePrice && closes[i] < zonePrice) {
                    touchAndReject = true;
                }
            } else { // support rejection
                wickExtreme = lows[i];
                if (lows[i] <= zonePrice && closes[i] > zonePrice) {
                    touchAndReject = true;
                }
            }
            if (touchAndReject) {
                double proximityPct = Math.abs(wickExtreme - zonePrice) / zonePrice;
                double range = highs[i] - lows[i];
                if (range == 0) continue;
                double body = Math.abs(closes[i] - opens[i]);
                double wickPct = 1.0 - (body / range);
                double bodyPct = body / range;
                String quality;
                if (wickPct > 0.8 && bodyPct < 0.2) quality = "STRONG";
                else if (wickPct > 0.5 && bodyPct < 0.5) quality = "MODERATE";
                else quality = "WEAK";
                if (quality.equals("STRONG") || ("MODERATE".equals(quality) && !"STRONG".equals(bestWickQuality))) {
                    bestWickQuality = quality;
                    bestProximityPct = proximityPct;
                    bestActualLevel = wickExtreme;
                } else if ("WEAK".equals(quality) && !"STRONG".equals(bestWickQuality) && !"MODERATE".equals(bestWickQuality)) {
                    bestWickQuality = "WEAK";
                    bestProximityPct = proximityPct;
                    bestActualLevel = wickExtreme;
                }
            }
        }
        res.rejectionWick = bestWickQuality;
        if (!"NONE".equals(bestWickQuality)) {
            res.rejectionWickProximityPct = bestProximityPct;
            res.rejectionWickActualLevel = bestActualLevel;
        }

        // 9.2 absorption
        double avgVol20 = average(volumes, Math.max(0, n - 20), n);
        double atr14 = averageTrueRange(highs, lows, closes, Math.max(0, n - 14), n);
        int absCount = 0;
        double maxVolRatio = 0;
        for (int i = Math.max(0, n - 10); i < n; i++) {
            double distPct = Math.abs(closes[i] - zonePrice) / zonePrice * 100;
            if (distPct <= 0.1) {
                boolean cond1 = volumes[i] > 2.0 * avgVol20;
                double range = highs[i] - lows[i];
                boolean cond2 = range < 0.3 * atr14;
                boolean cond3 = (deltas[i] > 0 && closes[i] < opens[i]) || (deltas[i] < 0 && closes[i] > opens[i]);
                if (cond1 && cond2 && cond3) {
                    absCount++;
                    double volRatio = volumes[i] / avgVol20;
                    if (volRatio > maxVolRatio) maxVolRatio = volRatio;
                }
            }
        }
        if (absCount > 0) {
            res.absorptionDetected = true;
            res.absorptionStrength = maxVolRatio > 5.0 ? "strong" : "moderate";
            res.absorptionCandleCount = absCount;
            res.absorptionVolRatio = maxVolRatio;
        }

        // 9.3 finished_auction
        double avgDelta20 = averageAbs(deltas, Math.max(0, n - 20), n);
        for (int i = Math.max(0, n - 20); i < n - 1; i++) {
            if (Math.abs(deltas[i]) > 3.0 * avgDelta20) {
                boolean reversal = (deltas[i] < 0 && closes[i + 1] > closes[i]) || (deltas[i] > 0 && closes[i + 1] < closes[i]);
                boolean noFollow = Math.abs(deltas[i + 1]) < 0.5 * Math.abs(deltas[i]);
                if (reversal && noFollow) {
                    res.finishedAuctionDetected = true;
                    res.finishedAuctionDirection = deltas[i] < 0 ? "sell" : "buy";
                    res.finishedAuctionExtremeDelta = deltas[i];
                    res.finishedAuctionReversalDelta = deltas[i + 1];
                    res.finishedAuctionFollowThrough = false;
                    break;
                }
            }
        }

        // 9.4 delta_flip (nearest-zone attribution)
        for (int i = Math.max(1, n - 20); i < n; i++) {
            if ((deltas[i - 1] < 0 && deltas[i] > 0) || (deltas[i - 1] > 0 && deltas[i] < 0)) {
                double flipActual = closes[i];
                double proximityPct = Math.abs(flipActual - zonePrice) / zonePrice;
                if (proximityPct <= 0.001) {
                    // Check if another zone is closer to the flip
                    boolean nearest = true;
                    for (Zone other : allZones) {
                        if (other == c.zone) continue;
                        double otherDist = Math.abs(flipActual - other.price) / other.price;
                        if (otherDist < proximityPct && otherDist <= 0.001) {
                            nearest = false;
                            break;
                        }
                    }
                    if (nearest) {
                        res.deltaFlipDetected = true;
                        res.deltaFlipFromNegative = deltas[i - 1] < 0;
                        res.deltaFlipAtZone = true;
                        res.deltaFlipZoneLevel = zonePrice;
                        res.deltaFlipCandlesSince = n - i;
                        res.deltaFlipProximityPct = proximityPct;
                        res.deltaFlipActualLevel = flipActual;
                        break;
                    }
                }
            }
        }

        // 9.5 volume_spike (using last bar or recent)
        double avgVol4h = average(volumes, Math.max(0, n - 240), n); // 4h = 240 minutes
        double currentVol = volumes[n - 1];
        double magnitude = currentVol / avgVol4h;
        boolean atLevel = Math.abs(closes[n - 1] - zonePrice) / zonePrice <= 0.001;
        res.volumeSpikeDetected = magnitude > 2.0;
        res.volumeSpikeMagnitude = magnitude;
        res.volumeSpikeAtLevel = atLevel;
        res.volumeSpikeLevel = zonePrice;
        if (atLevel) {
            res.volumeSpikeProximityPct = Math.abs(closes[n - 1] - zonePrice) / zonePrice;
            res.volumeSpikeActualLevel = closes[n - 1];
        }

        // 9.6 speed
        double atrCurrent = averageTrueRange(highs, lows, closes, n - 14, n);
        double atrBaseline = averageTrueRange(highs, lows, closes, Math.max(0, n - 34), n - 14);
        double atrRatio = atrCurrent / atrBaseline;
        double avgRange = averageRange(highs, lows, Math.max(0, n - 20), n);
        int largeCount = 0, consec = 0, maxConsec = 0;
        for (int i = Math.max(0, n - 10); i < n; i++) {
            if (highs[i] - lows[i] > 1.5 * avgRange) {
                largeCount++;
                consec++;
                if (consec > maxConsec) maxConsec = consec;
            } else {
                consec = 0;
            }
        }
        double speedScore = Math.min(10, atrRatio * 3 + maxConsec * 2);
        res.speedPickingUp = speedScore > 5;
        res.speedScore = speedScore;
        String vwapSlope = root.get("vwap").get("slope").asText();
        res.speedDirection = "rising".equals(vwapSlope) ? "up" : "falling".equals(vwapSlope) ? "down" : "flat";
        res.speedAtrRatio = atrRatio;
        res.speedConsecutiveLarge = maxConsec;

        // 9.7 cvd_aligned
        String mainCvdSlope = root.get("cvd").get("slope").asText();
        JsonNode netDeltaNode = root.get("trade_flow").get("net_delta_1m");
        boolean netDeltaKnown = netDeltaNode != null && !netDeltaNode.isNull();   // historical mode: null, no tape
        double netDelta = netDeltaKnown ? netDeltaNode.asDouble() : 0.0;
        boolean cvdAligned = false;
        if (!netDeltaKnown) {
            // no trade flow: cannot confirm alignment, leave false
        } else if ("rising".equals(mainCvdSlope) && netDelta > 0) cvdAligned = true;
        else if ("falling".equals(mainCvdSlope) && netDelta < 0) cvdAligned = true;
        else if ("flat".equals(mainCvdSlope) || mainCvdSlope.isEmpty()) {
            // tiebreaker: cvd_recent.slope_1h
            String slope1h = root.get("cvd").get("cvd_recent").get("slope_1h").asText();
            if ("rising".equals(slope1h) && netDelta > 0) cvdAligned = true;
            else if ("falling".equals(slope1h) && netDelta < 0) cvdAligned = true;
        }
        res.cvdAligned = cvdAligned;

        // 9.8 book_imbalance
        JsonNode ratioNode = root.get("order_book_depth").get("bid_ask_ratio");
        res.bookImbalance = (ratioNode == null || ratioNode.isNull()) ? null : ratioNode.asDouble();

        return res;
    }

    // Helper stats
    private static double average(double[] arr, int start, int end) {
        if (start >= end) return 0;
        double sum = 0;
        for (int i = start; i < end && i < arr.length; i++) sum += arr[i];
        return sum / (end - start);
    }
    private static double averageAbs(double[] arr, int start, int end) {
        if (start >= end) return 0;
        double sum = 0;
        for (int i = start; i < end && i < arr.length; i++) sum += Math.abs(arr[i]);
        return sum / (end - start);
    }
    private static double averageTrueRange(double[] highs, double[] lows, double[] closes, int start, int end) {
        if (start >= end || start < 1) return 0;
        double sum = 0;
        for (int i = start; i < end; i++) {
            double tr = Math.max(highs[i] - lows[i], Math.max(Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1])));
            sum += tr;
        }
        return sum / (end - start);
    }
    private static double averageRange(double[] highs, double[] lows, int start, int end) {
        if (start >= end) return 0;
        double sum = 0;
        for (int i = start; i < end; i++) sum += highs[i] - lows[i];
        return sum / (end - start);
    }
}
