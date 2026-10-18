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
import java.time.*;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.*;
import java.util.concurrent.*;

public class MarketDataSnapshot {

    private final BinanceClient client;
    /** Klines for the historical (as-of) path only; null (default) = the REST client, so live behaviour is unchanged. */
    private final HistoricalSource histSource;

    private HistoricalSource hist() { return histSource != null ? histSource : client; }
    private final ObjectMapper mapper;
    private final FvgCalculator fvgCalc;
    private static final double VALUE_AREA_PCT = 0.70;
    private static final String CONFIDENCE_LOW = "LOW";
    private static final String CONFIDENCE_MEDIUM = "MEDIUM";
    private static final String CONFIDENCE_HIGH = "HIGH";

    public MarketDataSnapshot() {
        this.client = new BinanceClient();
        this.histSource = null;
        this.mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
        this.fvgCalc = new FvgCalculator();
    }

    /** Archive mode: historical snapshots come from the local 1m archive under raw/klines; no network in that path. */
    public MarketDataSnapshot(java.nio.file.Path raw) {
        this.client = new BinanceClient();
        this.histSource = ArchiveHistoricalSource.lazy(raw);
        this.mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
        this.fvgCalc = new FvgCalculator();
    }

    /** B084: a null ratio (depth fetch failed / empty ask side) is emitted as JSON null, never a fake 0.0. */
    static void putBookRatio(ObjectNode cond, ObjectNode ob, Double ratio) {
        if (ratio == null) {
            cond.putNull("book_imbalance");
            ob.putNull("bid_ask_ratio");
        } else {
            cond.put("book_imbalance", Math.round(ratio * 100.0) / 100.0);
            ob.put("bid_ask_ratio", Math.round(ratio * 100.0) / 100.0);
        }
    }

    static Double bidAskRatioFromDepth(JsonNode depth, double currentPrice) {
        double bidDepth = 0, askDepth = 0;
        for (JsonNode bid : depth.get("bids")) {
            double p = bid.get(0).asDouble();
            double q = bid.get(1).asDouble();
            if (p >= currentPrice * 0.99) bidDepth += p * q;
        }
        for (JsonNode ask : depth.get("asks")) {
            double p = ask.get(0).asDouble();
            double q = ask.get(1).asDouble();
            if (p <= currentPrice * 1.01) askDepth += p * q;
        }
        return askDepth > 0 ? bidDepth / askDepth : null; // null = unavailable (B084)
    }

    public ObjectNode fetchSnapshot(String symbol, BinanceLiquidationAccumulator liqAccumulator) throws IOException {
        long t0 = System.currentTimeMillis();

        Map<String, JsonNode> mtf = fetchMultiTimeframe(symbol);
        JsonNode klines1m = mtf.get("1m");
        JsonNode klines1h = mtf.get("1h");
        if (klines1m == null || klines1m.size() == 0) {
            throw new IOException("Failed to fetch 1m klines for " + symbol);
        }

        double currentPrice = klines1m.get(klines1m.size() - 1).get(4).asDouble();

        // ===== TEMPORARY TEST OVERRIDE (DSA_TASK_012 Test 1) =====

        // ===== END TEMPORARY OVERRIDE =====
        ZonedDateTime now = ZonedDateTime.now(ZoneOffset.UTC);

        // ── Daily bars (since 00:00 UTC) ──
        long todayStartMs = now.truncatedTo(ChronoUnit.DAYS).toInstant().toEpochMilli();
        List<JsonNode> dailyBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= todayStartMs) dailyBars.add(bar);
        }
        if (dailyBars.isEmpty()) {
            int start = Math.max(0, klines1m.size() - 200);
            for (int i = start; i < klines1m.size(); i++) dailyBars.add(klines1m.get(i));
        }

        // ── Weekly bars (Monday 00:00 UTC to now, 1h) ──
        ZonedDateTime mondayStart = now.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
                .truncatedTo(ChronoUnit.DAYS);
        long mondayStartMs = mondayStart.toInstant().toEpochMilli();
        List<JsonNode> weeklyBars = new ArrayList<>();
        if (klines1h != null) {
            for (JsonNode bar : klines1h) {
                if (bar.get(0).asLong() >= mondayStartMs) weeklyBars.add(bar);
            }
        }

        // ── Post-funding bars (last 08:00 UTC) ──
        ZonedDateTime lastEightUtc = now.withHour(8).withMinute(0).withSecond(0).withNano(0);
        if (now.isBefore(lastEightUtc)) lastEightUtc = lastEightUtc.minusDays(1);
        long postFundingStartMs = lastEightUtc.toInstant().toEpochMilli();
        List<JsonNode> postFundingBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= postFundingStartMs) postFundingBars.add(bar);
        }

        // ── 4H intraday bars ──
        int boundaryHour = (now.getHour() / 4) * 4;
        ZonedDateTime lastFourHourBoundary = now.withHour(boundaryHour).withMinute(0).withSecond(0).withNano(0);
        long fourHourStartMs = lastFourHourBoundary.toInstant().toEpochMilli();
        List<JsonNode> intraday4hBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= fourHourStartMs) intraday4hBars.add(bar);
        }

        // ── Prior day bars ──
        ZonedDateTime yesterdayStartUtc = now.minusDays(1).truncatedTo(ChronoUnit.DAYS);
        ZonedDateTime yesterdayEndUtc = yesterdayStartUtc.plusDays(1).minusNanos(1);
        JsonNode yesterdayKlines = client.klinesRange(symbol, "1m",
                yesterdayStartUtc.toInstant().toEpochMilli(),
                yesterdayEndUtc.toInstant().toEpochMilli(), 1440);
        List<JsonNode> priorDayBars = new ArrayList<>();
        if (yesterdayKlines != null) {
            for (JsonNode bar : yesterdayKlines) priorDayBars.add(bar);
        }

        // ── Alignment check ──
        boolean alignmentPass = true;
        double refClose = currentPrice;
        for (String tf : new String[]{"1w","1d","4h","1h","15m","5m","1m"}) {
            JsonNode k = mtf.get(tf);
            if (k == null || k.size() == 0) continue;
            double close = k.get(k.size()-1).get(4).asDouble();
            double drift = Math.abs(close - refClose) / refClose;
            if (drift >= 0.001) { alignmentPass = false; break; }
        }

        // ── Build minimal VP nodes ──
        ObjectNode weeklyVp = buildVp(weeklyBars, false);
        // Previous two weeks VPOC
        ZonedDateTime prevWeekMonday = mondayStart.minusWeeks(1);
        ZonedDateTime prevWeekSunday = prevWeekMonday.plusDays(6).withHour(23).withMinute(59).withSecond(59).withNano(0);
        JsonNode prevWeekKlines = client.klinesRange(symbol, "1h",
                prevWeekMonday.toInstant().toEpochMilli(),
                prevWeekSunday.toInstant().toEpochMilli(), 168);
        List<JsonNode> prevWeekBars = new ArrayList<>();
        if (prevWeekKlines != null) {
            for (JsonNode bar : prevWeekKlines) prevWeekBars.add(bar);
        }
        ObjectNode prevWeekVp = buildVp(prevWeekBars, false);
        double priorWeekPoc = prevWeekVp.get("poc").asDouble();

        ZonedDateTime twoWeekMonday = mondayStart.minusWeeks(2);
        ZonedDateTime twoWeekSunday = twoWeekMonday.plusDays(6).withHour(23).withMinute(59).withSecond(59).withNano(0);
        JsonNode twoWeekKlines = client.klinesRange(symbol, "1h",
                twoWeekMonday.toInstant().toEpochMilli(),
                twoWeekSunday.toInstant().toEpochMilli(), 168);
        List<JsonNode> twoWeekBars = new ArrayList<>();
        if (twoWeekKlines != null) {
            for (JsonNode bar : twoWeekKlines) twoWeekBars.add(bar);
        }
        ObjectNode twoWeekVp = buildVp(twoWeekBars, false);
        double twoWeekAgoPoc = twoWeekVp.get("poc").asDouble();

        weeklyVp.put("prior_week_poc", Math.round(priorWeekPoc * 100.0) / 100.0);
        weeklyVp.put("two_week_ago_poc", Math.round(twoWeekAgoPoc * 100.0) / 100.0);
        ObjectNode dailyVp = buildVp(dailyBars, true);
        ObjectNode postFundingVp = buildVp(postFundingBars, false, 10.0); // [SCREENER] bin=10.0 - B059 untagged, no citation
        ObjectNode intraday4hVp = buildVp(intraday4hBars, false);
        ObjectNode priorDayVp = buildVp(priorDayBars, false);
        double priorDayClose = 0.0, priorDayHigh = 0.0, priorDayLow = Double.MAX_VALUE;
        for (JsonNode bar : priorDayBars) {
            double h = bar.get(2).asDouble();
            double l = bar.get(3).asDouble();
            if (h > priorDayHigh) priorDayHigh = h;
            if (l < priorDayLow) priorDayLow = l;
        }
        if (!priorDayBars.isEmpty()) {
            priorDayClose = priorDayBars.get(priorDayBars.size() - 1).get(4).asDouble();
        }
        priorDayVp.put("close", Math.round(priorDayClose * 100.0) / 100.0);
        priorDayVp.put("high", Math.round(priorDayHigh * 100.0) / 100.0);
        priorDayVp.put("low", priorDayLow == Double.MAX_VALUE ? 0.0 : Math.round(priorDayLow * 100.0) / 100.0);

        // F-BT-14: the naked-POC list had no writer after 2026-08-28; record the finished prior UTC day and
        // mark POCs the recent 1m bars traded through. Live path only (the historical builder must not write).
        updateNakedPocs(new NakedPocTracker(symbol), priorDayVp, yesterdayStartUtc.toLocalDate(), priorDayBars.size(),
                now.toLocalDate(), klines1m);

        // Add prior_day close / high / low

        // ── VWAP (trimmed) ──
        ObjectNode vwapNode = buildVwap(dailyBars);
        vwapNode.remove("+3s");
        vwapNode.remove("-3s");

        // ── CVD (session-scoped) ──
        // DSA-HYG-006 fix (2026-09-10): align with VWAP scope.
        // Previously used klines1m (24h rolling) while VWAP used dailyBars (session).
        // This caused JSON CVD to mismatch CoinGlass (which resets at 00:00 UTC).
        ArrayNode dailyBarsForCvd1 = mapper.createArrayNode();
        for (JsonNode bar : dailyBars) dailyBarsForCvd1.add(bar);
        ObjectNode cvdNode = buildCvd(dailyBarsForCvd1, klines1m);
        cvdNode.put("scope", "session");
        cvdNode.put("gating_window", "rolling_1m");  // B070: slope/last_3_delta/cvd_recent are not anchored to 00:00 UTC
        cvdNode.put("session_start_utc", now.truncatedTo(ChronoUnit.DAYS).toInstant().toString());

        // ── Trade flow net delta (multi-window from klines1m) ──
        // DSA-HYG-007 (2026-09-11): all windows from same formula for consistency.
        // netDelta per bar = 2 * takerBuyBaseAssetVolume - volume.
        // Windows: 1m, 5m, 15m, 1h.
        double nd1m = 0, nd5m = 0, nd15m = 0, nd1h = 0;
        int _n = klines1m.size();
        int _start = Math.max(0, _n - 60);
        for (int i = _start; i < _n; i++) {
            JsonNode bar = klines1m.get(i);
            double vol = bar.get(5).asDouble();
            double takerBuy = bar.get(9).asDouble();
            double barDelta = 2 * takerBuy - vol;
            if (i >= _n - 1) nd1m += barDelta;
            if (i >= _n - 5) nd5m += barDelta;
            if (i >= _n - 15) nd15m += barDelta;
            if (i >= _n - 60) nd1h += barDelta;
        }

        // ── Structure (swing levels only) ──
        ObjectNode structure = buildStructure(mtf, currentPrice);

        // ── Order book ratio ──
        Double bidAskRatioBox = null;
        try {
            bidAskRatioBox = bidAskRatioFromDepth(client.orderBookDepth(symbol, 100), currentPrice);
        } catch (Exception e) { /* depth unavailable: stays null (B084) */ }

        // ── Open interest direction ──
        ObjectNode oiFetch = oiFromHistory(client, symbol, mapper);
        String oiDirection = oiFetch.get("direction").asText();
        boolean oiAvailable = !"UNAVAILABLE".equals(oiDirection);
        double oiChangePct = oiAvailable ? oiFetch.get("change_1h_pct").asDouble() : 0.0;

        // ── Funding ──
        double fundingRate = 0.0;
        try {
            fundingRate = client.currentFundingRate(symbol).get("lastFundingRate").asDouble();
        } catch (Exception e) { /* keep 0 */ }

        // ── Session timing ──
        ObjectNode sessionTiming = buildSessionTiming(now);

        // ── Liquidation warning ──
        ObjectNode liquidationWarning = mapper.createObjectNode();
        liquidationWarning.put("status", "none");
        liquidationWarning.putNull("nearest_cluster_distance_pct");
        liquidationWarning.put("note", "Liquidation data requires API key. When available, emit warning only if cluster within 0.5% of proposed stop.");

        // ── Speed picking up ──
        boolean speedPickingUp = computeSpeedPickingUp(klines1m);

        // ── Rejection wick at zone ──
        Boolean rejectionWick = computeRejectionWick(klines1m, currentPrice);

        // ── Conditions object (minimal) ──

        // volume_spike_at_level: current 5m/15m volume > 2× average volume at same price level (last 4h)
        boolean volumeSpikeAtLevel = false;
        double currentPriceLevel = Math.round(currentPrice); // round to nearest dollar
        double totalVolumeAtLevel = 0.0;
        int candlesAtLevel = 0;
        double current5mVolume = 0.0;
        boolean current5mAtLevel = false;

        JsonNode klines5m = mtf.get("5m");
        if (klines5m != null && klines5m.size() > 0) {
            int start5 = Math.max(0, klines5m.size() - 48); // last 4 hours of 5m candles
            for (int i = start5; i < klines5m.size(); i++) {
                JsonNode bar = klines5m.get(i);
                double close = bar.get(4).asDouble();
                double vol = bar.get(5).asDouble();
                if (Math.abs(close - currentPriceLevel) < 1.0) { // within $1
                    totalVolumeAtLevel += vol;
                    candlesAtLevel++;
                    if (i == klines5m.size() - 1) {
                        current5mVolume = vol;
                        current5mAtLevel = true;
                    }
                }
            }
            if (candlesAtLevel > 1 && current5mAtLevel) {
                double avgVolumeAtLevel = totalVolumeAtLevel / candlesAtLevel;
                if (current5mVolume > 2.0 * avgVolumeAtLevel) {
                    volumeSpikeAtLevel = true;
                }
            }
        }        ObjectNode cond = mapper.createObjectNode();
        double poc = dailyVp.get("poc").asDouble();
        double vah = dailyVp.get("vah").asDouble();
        double val = dailyVp.get("val").asDouble();
        String priceVsPoc = currentPrice > poc ? "above" : currentPrice < poc ? "below" : "at_poc";
        String priceVsVa = currentPrice > vah ? "above_vah" : currentPrice < val ? "below_val" : "in_va";
        cond.put("price_vs_poc", priceVsPoc);
        cond.put("price_vs_va", priceVsVa);
        cond.put("vp_shape", dailyVp.get("shape").asText());
        cond.put("vwap_slope", vwapNode.get("slope").asText());
        cond.put("cvd_slope", cvdNode.get("slope").asText());
        boolean cvdAligned = !"flat".equals(cvdNode.get("cvd_recent").get("slope_1h").asText()) &&
                (("rising".equals(cvdNode.get("cvd_recent").get("slope_1h").asText()) && nd1m > 0) ||
                 ("falling".equals(cvdNode.get("cvd_recent").get("slope_1h").asText()) && nd1m < 0));
        cond.put("cvd_trade_flow_aligned", cvdAligned);
        int unfilledCount = 0;
        ObjectNode nearestUnfilled = null;
        List<FvgCalculator.Fvg> fvgs = fvgCalc.detect(klines1m, 5);
        for (FvgCalculator.Fvg f : fvgs) {
            if (!f.filled) {
                unfilledCount++;
                if (nearestUnfilled == null) {
                    nearestUnfilled = mapper.createObjectNode();
                    nearestUnfilled.put("type", f.type);
                    nearestUnfilled.put("top", Math.round(f.top * 100.0) / 100.0);
                    nearestUnfilled.put("bottom", Math.round(f.bottom * 100.0) / 100.0);
                }
            }
        }
        cond.put("fvg_unfilled_count", unfilledCount);
        if (nearestUnfilled != null) cond.set("fvg_nearest_unfilled", nearestUnfilled);
        else cond.putNull("fvg_nearest_unfilled");
        cond.put("funding_extreme", Math.abs(fundingRate) > 0.001);
        cond.put("oi_trend", oiDirection);
        cond.put("speed_picking_up", speedPickingUp);
        cond.put("volume_spike_at_level", volumeSpikeAtLevel);
        if (rejectionWick == null) cond.putNull("rejection_wick_at_zone");
        else cond.put("rejection_wick_at_zone", rejectionWick);

        // ── Spot-perp basis ──
        ObjectNode spotPerpBasis = buildSpotPerpBasis(symbol);

        // ── Liquidation clusters ──
        ObjectNode liquidationClusters = mapper.createObjectNode();
        liquidationClusters.putObject("nearest_above").put("price", 0.0);
        liquidationClusters.putObject("nearest_below").put("price", 0.0);
        liquidationClusters.put("warning", false);

        // ── Build root ──
        ObjectNode root = mapper.createObjectNode();
        root.put("timestamp_utc", Instant.now().toString());
        root.put("asset", symbol);
        root.put("current_price", Math.round(currentPrice * 100.0) / 100.0);
        root.put("alignment_pass", alignmentPass);
        root.set("weekly_vp", weeklyVp);
        root.set("daily_vp", dailyVp);
        root.set("post_funding_vp", postFundingVp);
        root.set("intraday_4h_vp", intraday4hVp);
        root.set("vwap", vwapNode);
        root.set("cvd", cvdNode);
        ObjectNode tradeFlow = mapper.createObjectNode();
        tradeFlow.put("net_delta_1m", Math.round(nd1m * 1000.0) / 1000.0);
        tradeFlow.put("net_delta_5m", Math.round(nd5m * 1000.0) / 1000.0);
        tradeFlow.put("net_delta_15m", Math.round(nd15m * 1000.0) / 1000.0);
        tradeFlow.put("net_delta_1h", Math.round(nd1h * 1000.0) / 1000.0);
        tradeFlow.put("confidence", CONFIDENCE_HIGH);
        root.set("trade_flow", tradeFlow);
        root.set("structure", structure);
        ObjectNode ob = mapper.createObjectNode();
        putBookRatio(cond, ob, bidAskRatioBox);
        ob.put("confidence", CONFIDENCE_HIGH);
        root.set("order_book_depth", ob);
        root.set("conditions", cond);
        root.set("prior_day", priorDayVp);
        ObjectNode fund = mapper.createObjectNode();
        fund.put("current_rate", fundingRate);
        fund.put("extreme", Math.abs(fundingRate) > 0.001);
        fund.put("confidence", CONFIDENCE_HIGH);
        root.set("funding", fund);
        ObjectNode oi = mapper.createObjectNode();
        oi.put("direction", oiDirection);
        if (oiAvailable) oi.put("change_1h_pct", Math.round(oiChangePct * 100.0) / 100.0); else oi.putNull("change_1h_pct");
        oi.put("delta_state", classifyOiDeltaState(oiDirection, nd1h));
        double priceDelta1h = 0.0;
        if (klines1m != null && klines1m.size() >= 61) {
            double nowClose = klines1m.get(klines1m.size() - 1).get(4).asDouble();
            double agoClose = klines1m.get(klines1m.size() - 61).get(4).asDouble();
            priceDelta1h = nowClose - agoClose;
        }
        oi.put("delta_state_price", classifyOiDeltaState(oiDirection, priceDelta1h));
        oi.put("confidence", oiAvailable ? CONFIDENCE_HIGH : CONFIDENCE_LOW);
        root.set("open_interest", oi);
        root.set("session", buildSession(klines1m, priorDayClose, currentPrice, dailyVp.get("vah").asDouble(), dailyVp.get("val").asDouble(), priorDayVp.get("high").asDouble(), priorDayVp.get("low").asDouble()));
        root.set("session_timing", sessionTiming);
        root.set("spot_perp_basis", spotPerpBasis);
        root.set("liquidation_clusters", liquidationClusters);
        root.set("oi_breakdown", buildOiBreakdown(symbol));

        // ── Order-flow tick rate (DSA_TASK_013) ──
        // Tom's "speed" primitive: rate of order-book / trade interaction.
        // Not candle range. Compare current window of aggTrades to a baseline window.
        ObjectNode orderFlow = mapper.createObjectNode();
        try {
            JsonNode currentTrades = client.aggTrades(symbol, 1000);
            long nowMs = System.currentTimeMillis();
            JsonNode baselineTrades = client.aggTradesRange(symbol, nowMs - 20L * 60L * 1000L, nowMs - 15L * 60L * 1000L, 1000);

            double[] cur = computeFlowStats(currentTrades);
            double[] base = computeFlowStats(baselineTrades);
            double curTps = cur[0], curVps = cur[1];
            double baseTps = base[0], baseVps = base[1];

            double tradesRatio = baseTps > 0 ? curTps / baseTps : 0.0;
            double volumeRatio = baseVps > 0 ? curVps / baseVps : 0.0;

            String speedState;
            if (baseTps <= 0 || baseVps <= 0) {
                speedState = "unknown";
            } else if (tradesRatio >= 1.5 && volumeRatio >= 1.5) {
                speedState = "accelerating";
            } else if (tradesRatio <= 0.7 && volumeRatio <= 0.7) {
                speedState = "decelerating";
            } else {
                speedState = "maintaining";
            }

            orderFlow.put("trades_per_sec", Math.round(curTps * 100.0) / 100.0);
            orderFlow.put("volume_per_sec", Math.round(curVps * 100.0) / 100.0);
            orderFlow.put("baseline_trades_per_sec", Math.round(baseTps * 100.0) / 100.0);
            orderFlow.put("baseline_volume_per_sec", Math.round(baseVps * 100.0) / 100.0);
            orderFlow.put("trades_ratio", Math.round(tradesRatio * 100.0) / 100.0);
            orderFlow.put("volume_ratio", Math.round(volumeRatio * 100.0) / 100.0);
            orderFlow.put("speed_state", speedState);
            orderFlow.put("confidence", "HIGH");
            orderFlow.put("note", "DSA_TASK_013. Current = last 1000 aggTrades. Baseline = 20-15 min ago. Thresholds provisional, not Tom-derived.");

            // DSA_TASK_014: per-instrument historical baseline
            updateAndApplyHistoricalBaseline(symbol, curTps, curVps, orderFlow);
        } catch (Exception e) {
            orderFlow.put("trades_per_sec", 0.0);
            orderFlow.put("volume_per_sec", 0.0);
            orderFlow.put("speed_state", "unknown");
            orderFlow.put("confidence", "LOW");
            orderFlow.put("note", "DSA_TASK_013 unavailable: " + e.getMessage());
        }
        root.set("order_flow", orderFlow);

        // --- Setup Candidates (v1.3.0) ---
        ArrayNode setupCandidates = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m);
        ArrayNode extraCandidates = ExtraSetupBuilder.build(mapper, root, mtf, klines1m);
        double clusterAbovePrice = liquidationClusters.get("nearest_above").get("price").asDouble();
        double clusterBelowPrice = liquidationClusters.get("nearest_below").get("price").asDouble();
        boolean warning = false;
        for (JsonNode cand : setupCandidates) {
            double stop = cand.get("math").get("stop").asDouble();
            double target = cand.get("math").get("target").asDouble();
            if (clusterAbovePrice > 0 && (Math.abs(clusterAbovePrice - stop) / stop < 0.005 || Math.abs(clusterAbovePrice - target) / target < 0.005)) warning = true;
            if (clusterBelowPrice > 0 && (Math.abs(clusterBelowPrice - stop) / stop < 0.005 || Math.abs(clusterBelowPrice - target) / target < 0.005)) warning = true;
        }
        ((com.fasterxml.jackson.databind.node.ObjectNode)liquidationClusters).put("warning", warning);
        root.set("setup_candidates", setupCandidates);
        root.set("module_candidates", extraCandidates);
        root.set("liquidation_clusters", liquidationClusters);
        root.set("setup_candidates", setupCandidates);
        return root;
    }

    /** Rule 37 fix: drop the forming (incomplete) kline before any derivation.
     *  Binance kline index 6 = close time. If closeTime > referenceMs, bar is still forming. */
    private void dropFormingBar(JsonNode klines, long referenceMs) {
        if (klines == null || klines.size() == 0) return;
        JsonNode last = klines.get(klines.size() - 1);
        long closeTime = last.get(6).asLong();
        if (closeTime > referenceMs) {
            ((ArrayNode) klines).remove(klines.size() - 1);
        }
    }

    private Map<String, JsonNode> fetchMultiTimeframe(String symbol) {
        Map<String, Integer> configs = Map.of(
                "1w", 2, "1d", 7, "4h", 3, "1h", 168, "15m", 16, "5m", 48, "1m", 1440
        );
        Map<String, JsonNode> result = new ConcurrentHashMap<>();
        ExecutorService pool = Executors.newFixedThreadPool(4);
        List<Future<?>> futures = new ArrayList<>();
        for (Map.Entry<String, Integer> e : configs.entrySet()) {
            String tf = e.getKey();
            int limit = e.getValue();
            futures.add(pool.submit(() -> {
                try {
                    JsonNode k = client.klines(symbol, tf, limit);
                    dropFormingBar(k, System.currentTimeMillis());
                    result.put(tf, k);
                }
                catch (IOException ex) { System.err.println("[MTF] Failed " + tf + ": " + ex.getMessage()); }
            }));
        }
        for (Future<?> f : futures) { try { f.get(30, TimeUnit.SECONDS); } catch (Exception ignored) {} }
        pool.shutdownNow();
        return result;
    }

    /**
     * F-BT-14. Never throws into the snapshot: the tracker is advisory (SetupCandidatesBuilder reads it).
     * A prior day with fewer than 1000 of its 1440 bars is partial (outage or API gap): its POC is not recorded.
     */
    static void updateNakedPocs(NakedPocTracker tracker, JsonNode priorDayVp, java.time.LocalDate priorDay,
                                int priorDayBarCount, java.time.LocalDate todayUtc, JsonNode klines1m) {
        try {
            if (priorDay != null && priorDayVp != null && priorDayVp.has("poc") && priorDayBarCount >= 1000) {
                tracker.recordPoc(priorDay, priorDayVp.get("poc").asDouble());
            }
            if (klines1m != null && klines1m.size() > 0) {
                List<JsonNode> bars = new ArrayList<>();
                for (JsonNode b : klines1m) bars.add(b);
                tracker.markVisitedByBars(bars, todayUtc);
            }
        } catch (Exception e) {
            System.err.println("naked_poc update failed: " + e);
        }
    }

    private ObjectNode buildVp(List<JsonNode> bars, boolean includeHvnsLvns) {
        return buildVp(bars, includeHvnsLvns, 0.0);
    }

    // B059 fix (2026-09-24): fixedBinSize > 0 snaps bin edges to a stable
    // grid so POC/VAH/VAL do not drift when minP/maxP extend. Used for
    // post_funding_vp only.
    private ObjectNode buildVp(List<JsonNode> bars, boolean includeHvnsLvns, double fixedBinSize) {
        ObjectNode node = mapper.createObjectNode();
        // Fail closed: a non-finite OHLCV value (NaN/Inf) gives the empty profile, never a guessed level.
        boolean finite = true;
        for (JsonNode bar : bars) {
            for (int k = 2; k <= 5; k++) {
                if (!Double.isFinite(bar.get(k).asDouble())) finite = false;
            }
        }
        if (bars.isEmpty() || !finite) {
            node.put("poc", 0.0);
            node.put("vah", 0.0);
            node.put("val", 0.0);
            node.put("shape", "D");
            node.put("confidence", CONFIDENCE_LOW);
            if (includeHvnsLvns) {
                node.putArray("hvns");
                node.putArray("lvns");
            }
            return node;
        }

        double minP = Double.MAX_VALUE, maxP = Double.MIN_VALUE;
        for (JsonNode bar : bars) {
            double low = bar.get(3).asDouble();
            double high = bar.get(2).asDouble();
            if (low < minP) minP = low;
            if (high > maxP) maxP = high;
        }
        double range = maxP - minP;
        double binSize;
        int numBins;
        double binOrigin;
        if (fixedBinSize > 0) {
            binSize = fixedBinSize;
            binOrigin = Math.floor(minP / binSize) * binSize;
            numBins = Math.max(50, (int)Math.ceil(range / binSize) + 1);
        } else {
            numBins = Math.max(50, (int)(range / 5));
            binSize = range / numBins;
            binOrigin = minP;
        }
        if (binSize <= 0) binSize = 1;

        TreeMap<Double, Double> profile = new TreeMap<>();
        for (int i = 0; i <= numBins; i++) profile.put(binOrigin + i * binSize, 0.0);

        for (JsonNode bar : bars) {
            double high = bar.get(2).asDouble();
            double low = bar.get(3).asDouble();
            double close = bar.get(4).asDouble();
            double vol = bar.get(5).asDouble();
            double tp = (high + low + close) / 3.0;
            double halfRange = (high - low) / 2.0;
            int n = (int) Math.max(1, (high - low) / binSize);
            // F-BT-09: normalise the triangular weights per bar so a bar adds exactly its own volume.
            // Unnormalised, a bar added ~vol*n/2 (fast minutes up to 30x a quiet one) and a single-bin bar
            // with tp above mid-range added nothing. A zero or NaN weight sum puts the volume on the tp bin.
            double[] ps = new double[n];
            double[] ws = new double[n];
            double wsum = 0.0;
            for (int i = 0; i < n; i++) {
                ps[i] = low + i * (high - low) / n;
                double w = halfRange > 0 ? 1.0 - Math.abs(ps[i] - tp) / halfRange : 0.0;
                ws[i] = (w > 0) ? w : 0.0;
                wsum += ws[i];
            }
            if (wsum > 0) {
                for (int i = 0; i < n; i++) {
                    Double key = profile.floorKey(ps[i]);
                    if (key == null) key = profile.firstKey();
                    profile.merge(key, vol * ws[i] / wsum, Double::sum);
                }
            } else {
                Double key = profile.floorKey(tp);
                if (key == null) key = profile.firstKey();
                profile.merge(key, vol, Double::sum);
            }
        }

        double poc = profile.entrySet().stream().max(Map.Entry.comparingByValue()).get().getKey();
        double totalVol = profile.values().stream().mapToDouble(Double::doubleValue).sum();
        double targetVol = totalVol * VALUE_AREA_PCT;
        List<Double> prices = new ArrayList<>(profile.keySet());
        int pocIdx = prices.indexOf(poc);
        int lower = pocIdx, upper = pocIdx;
        double accVol = profile.get(poc);
        while (accVol < targetVol && (lower > 0 || upper < prices.size()-1)) {
            double lowerVol = lower > 0 ? profile.get(prices.get(lower-1)) : -1;
            double upperVol = upper < prices.size()-1 ? profile.get(prices.get(upper+1)) : -1;
            if (lowerVol >= upperVol && lower > 0) { lower--; accVol += profile.get(prices.get(lower)); }
            else if (upper < prices.size()-1) { upper++; accVol += profile.get(prices.get(upper)); }
            else if (lower > 0) { lower--; accVol += profile.get(prices.get(lower)); }
            else break;
        }
        // FORMULAS 18.1 edge convention: map keys are bin lower edges; POC = bin centre, VAH = top edge of its
        // bin, VAL = bottom edge of its bin.
        double vah = prices.get(upper) + binSize;
        double val = prices.get(lower);
        double pocPrice = poc + binSize / 2.0;

        // shape heuristic
        double maxVol = profile.get(poc), secondPeakVol = 0;
        for (Map.Entry<Double,Double> e : profile.entrySet()) {
            if (e.getKey() != poc && e.getValue() < maxVol && e.getValue() > secondPeakVol) secondPeakVol = e.getValue();
        }
        String shape;
        // Heuristic: bell/two-peak shape. NOT Tom's B (top-heavy weakness).
        // Old code emitted "B" for both meanings; classifyState then forced
        // every snapshot to balance. Renamed 2026-09-17 to end the collision.
        if (secondPeakVol > 0.6 * maxVol) shape = "TWOPEAK";
        else {
            double leftVol = 0, rightVol = 0;
            for (Map.Entry<Double,Double> e : profile.entrySet()) {
                if (e.getKey() < poc) leftVol += e.getValue();
                else if (e.getKey() > poc) rightVol += e.getValue();
            }
            double ratio = leftVol / Math.max(rightVol, 0.0001);
            shape = (ratio > 0.8 && ratio < 1.2) ? "D" : "P";
        }

        node.put("poc", Math.round(pocPrice*100.0)/100.0);
        node.put("vah", Math.round(vah*100.0)/100.0);
        node.put("val", Math.round(val*100.0)/100.0);
        node.put("shape", shape);
        node.put("confidence", CONFIDENCE_MEDIUM);
        if (includeHvnsLvns) {
            // compute hvns/lvns simplified
            int window = Math.max(3, profile.size()/20);
            List<Double> vols = new ArrayList<>();
            for (double p : prices) vols.add(profile.get(p));
            List<Double> smoothed = new ArrayList<>();
            for (int i=0; i<vols.size(); i++) {
                double sum=0; int cnt=0;
                for (int j=Math.max(0,i-window); j<Math.min(vols.size(),i+window+1); j++) { sum+=vols.get(j); cnt++; }
                smoothed.add(sum/cnt);
            }
            List<Double> hvns = new ArrayList<>(), lvns = new ArrayList<>();
            for (int i=1; i<smoothed.size()-1; i++) {
                if (smoothed.get(i) > smoothed.get(i-1) && smoothed.get(i) > smoothed.get(i+1)) hvns.add(prices.get(i));
                if (smoothed.get(i) < smoothed.get(i-1) && smoothed.get(i) < smoothed.get(i+1)) lvns.add(prices.get(i));
            }
            ArrayNode hvnArr = node.putArray("hvns");
            hvns.stream().map(v -> Math.round(v*100.0)/100.0).distinct().sorted(Comparator.reverseOrder()).limit(3).forEach(hvnArr::add);
            ArrayNode lvnArr = node.putArray("lvns");
            lvns.stream().map(v -> Math.round(v*100.0)/100.0).distinct().sorted().limit(3).forEach(lvnArr::add);
        }
        return node;
    }

    private ObjectNode buildVwap(List<JsonNode> bars) {
        ObjectNode node = mapper.createObjectNode();
        if (bars.isEmpty()) {
            node.put("price", 0.0);
            node.put("slope", "flat");
            node.put("slope_pct", 0.0);
            node.putObject("bands");
            node.put("confidence", CONFIDENCE_LOW);
            return node;
        }
        double cumPV = 0, cumVol = 0;
        List<Double> vwaps = new ArrayList<>(), tps = new ArrayList<>(), vols = new ArrayList<>();
        for (JsonNode bar : bars) {
            double high = bar.get(2).asDouble(), low = bar.get(3).asDouble(), close = bar.get(4).asDouble(), vol = bar.get(5).asDouble();
            double tp = (high+low+close)/3;
            cumPV += tp*vol; cumVol += vol;
            vwaps.add(cumVol>0 ? cumPV/cumVol : 0);
            tps.add(tp); vols.add(vol);
        }
        double vwap = cumVol>0 ? cumPV/cumVol : 0;
        double cumVar = 0;
        for (int i=0; i<tps.size(); i++) cumVar += vols.get(i) * (tps.get(i)-vwap)*(tps.get(i)-vwap);
        double sigma = cumVol>0 ? Math.sqrt(cumVar/cumVol) : 0;
        int mid = vwaps.size()/2;
        double firstHalf = mid>0 ? vwaps.subList(0,mid).stream().mapToDouble(Double::doubleValue).average().orElse(0) : vwap;
        double secondHalf = vwaps.size()>mid ? vwaps.subList(mid,vwaps.size()).stream().mapToDouble(Double::doubleValue).average().orElse(0) : vwap;
        double slopePct = firstHalf>0 ? (secondHalf-firstHalf)/firstHalf : 0;
        String slope = slopePct>0.0005 ? "rising" : slopePct<-0.0005 ? "falling" : "flat";
        node.put("price", Math.round(vwap*100.0)/100.0);
        node.put("slope", slope);
        node.put("slope_pct", Math.round(slopePct*10000.0)/10000.0);
        ObjectNode bands = node.putObject("bands");
        bands.put("+1s", Math.round((vwap+sigma)*100.0)/100.0);
        bands.put("+2s", Math.round((vwap+2*sigma)*100.0)/100.0);
        bands.put("-1s", Math.round((vwap-sigma)*100.0)/100.0);
        bands.put("-2s", Math.round((vwap-2*sigma)*100.0)/100.0);
        node.put("confidence", CONFIDENCE_MEDIUM);
        return node;
    }

    /**
     * B070: the UTC 00:00 session anchor is display-only. "value" is the session CVD (bars since 00:00 UTC, matches
     * CoinGlass). Everything a verdict reads (slope, last_3_delta, cvd_recent) comes from the rolling 1m window, so it
     * never changes at the UTC rollover.
     */
    private ObjectNode buildCvd(JsonNode sessionBars, JsonNode rollingBars) {
        ObjectNode node = buildCvdRolling(rollingBars);
        double session = 0;
        for (JsonNode bar : sessionBars) {
            double vol = bar.get(5).asDouble(), buy = bar.get(9).asDouble();
            session += (buy - (vol-buy));
        }
        node.put("value", Math.round(session*1000.0)/1000.0);
        return node;
    }

    private ObjectNode buildCvdRolling(JsonNode klines) {
        ObjectNode node = mapper.createObjectNode();
        int size = klines.size();
        if (size == 0) {
            node.put("value", 0.0);
            node.put("slope", "flat");
            node.set("last_3_delta", mapper.valueToTree(List.of()));
            node.putObject("cvd_recent");
            node.put("confidence", CONFIDENCE_LOW);
            return node;
        }
        double cvd = 0;
        List<Double> cvdSeries = new ArrayList<>();
        for (JsonNode bar : klines) {
            double vol = bar.get(5).asDouble(), buy = bar.get(9).asDouble();
            cvd += (buy - (vol-buy));
            cvdSeries.add(cvd);
        }
        List<String> last3 = new ArrayList<>();
        for (int i = Math.max(0,size-3); i<size; i++) {
            double vol = klines.get(i).get(5).asDouble(), buy = klines.get(i).get(9).asDouble();
            last3.add((2*buy-vol)>0 ? "positive" : "negative");
        }
        String slope = "flat";
        if (cvdSeries.size()>=40) {
            double recent = cvdSeries.subList(cvdSeries.size()-20,cvdSeries.size()).stream().mapToDouble(Double::doubleValue).average().orElse(0);
            double older = cvdSeries.subList(cvdSeries.size()-40,cvdSeries.size()-20).stream().mapToDouble(Double::doubleValue).average().orElse(0);
            double change = older!=0 ? (recent-older)/Math.abs(older) : 0;
            if (change>0.02) slope="rising";
            else if (change<-0.02) slope="falling";
        }
        node.put("value", Math.round(cvd*1000.0)/1000.0);
        node.put("slope", slope);
        node.set("last_3_delta", mapper.valueToTree(last3));
        ObjectNode recent = node.putObject("cvd_recent");
        double delta1h=0, delta4h=0;
        if (cvdSeries.size()>=60) delta1h = cvdSeries.get(cvdSeries.size()-1) - cvdSeries.get(cvdSeries.size()-60);
        if (cvdSeries.size()>=240) delta4h = cvdSeries.get(cvdSeries.size()-1) - cvdSeries.get(cvdSeries.size()-240);
        recent.put("slope_1h", delta1h>0.001 ? "rising" : delta1h<-0.001 ? "falling" : "flat");
        recent.put("slope_4h", delta4h>0.001 ? "rising" : delta4h<-0.001 ? "falling" : "flat");
        recent.put("delta_1h", Math.round(delta1h*1000.0)/1000.0);
        recent.put("delta_4h", Math.round(delta4h*1000.0)/1000.0);
        node.put("confidence", CONFIDENCE_MEDIUM);
        return node;
    }

    private ObjectNode buildStructure(Map<String, JsonNode> mtf, double currentPrice) {
        ObjectNode node = mapper.createObjectNode();
        // T042: emit structure for every tf present in mtf.
        String[] tfs = {"1w","1d","4h","1h","15m","5m"};
        int[] lookbacks = {2,7,3,24,16,12};
        for (int t=0; t<tfs.length; t++) {
            JsonNode klines = mtf.get(tfs[t]);
            ObjectNode tfNode = node.putObject(tfs[t]);
            if (klines==null || klines.size()==0) {
                tfNode.put("swing_high", 0.0);
                tfNode.put("swing_low", 0.0);
                tfNode.put("stale", true);
                continue;
            }
            int start = Math.max(0, klines.size()-lookbacks[t]);
            double high = Double.MIN_VALUE, low = Double.MAX_VALUE;
            for (int i=start; i<klines.size(); i++) {
                double h = klines.get(i).get(2).asDouble();
                double l = klines.get(i).get(3).asDouble();
                if (h>high) high=h;
                if (l<low) low=l;
            }
            // swing detection simplified: use close pivots if found, else high/low
            double swingHigh = high, swingLow = low;
            for (int i=klines.size()-2; i>start; i--) {
                double prevClose = klines.get(i-1).get(4).asDouble();
                double curClose = klines.get(i).get(4).asDouble();
                double nextClose = klines.get(i+1).get(4).asDouble();
                if (swingHigh==high && prevClose<curClose && curClose>nextClose) swingHigh=curClose;
                if (swingLow==low && prevClose>curClose && curClose<nextClose) swingLow=curClose;
                if (swingHigh!=high && swingLow!=low) break;
            }
            if (swingLow > swingHigh) { double sw = swingLow; swingLow = swingHigh; swingHigh = sw; }
            boolean stale = (swingHigh < currentPrice) || (swingLow > currentPrice);
            tfNode.put("swing_high", Math.round(swingHigh*100.0)/100.0);
            tfNode.put("swing_low", Math.round(swingLow*100.0)/100.0);
            tfNode.put("stale", stale);
        }
        return node;
    }

    private ObjectNode buildSession(JsonNode klines1m, double priorDayClose, double currentPrice, double dailyVah, double dailyVal, double priorDayHigh, double priorDayLow) {
        ObjectNode node = mapper.createObjectNode();
        ZonedDateTime now = ZonedDateTime.now(ZoneOffset.UTC);
        ZonedDateTime nyOpen = ZonedDateTime.of(now.toLocalDate(), LocalTime.of(9,30), ZoneId.of("America/New_York"));
        ZonedDateTime nyOpenUtc = nyOpen.withZoneSameInstant(ZoneOffset.UTC);
        long openMs = nyOpenUtc.toInstant().toEpochMilli();
        long ibEndMs = openMs + 30L * 60L * 1000L;

        double openPx = 0.0, highPx = 0.0, lowPx = Double.MAX_VALUE;
        double ibHigh = 0.0, ibLow = Double.MAX_VALUE;
        long lastSweepAbove = 0L, lastSweepBelow = 0L;
        boolean seen = false;
        if (klines1m != null) {
            for (JsonNode bar : klines1m) {
                long t = bar.get(0).asLong();
                if (t < openMs) continue;
                double o = bar.get(1).asDouble();
                double h = bar.get(2).asDouble();
                double l = bar.get(3).asDouble();
                if (!seen) { openPx = o; seen = true; }
                if (h > highPx) highPx = h;
                if (l < lowPx) lowPx = l;
                if (t < ibEndMs) {
                    if (h > ibHigh) ibHigh = h;
                    if (l < ibLow) ibLow = l;
                }
                if (priorDayHigh > 0 && h > priorDayHigh) { lastSweepAbove = t; }
                if (priorDayLow > 0 && l < priorDayLow) { lastSweepBelow = t; }
            }
        }
        node.put("vwap_anchor_utc", nyOpenUtc.toInstant().toString());
        node.put("initial_balance_window_minutes", 30);
        if (!seen) {
            node.put("open_price", 0.0);
            node.put("high", 0.0);
            node.put("low", 0.0);
            node.put("gap_from_prior_close", 0.0);
            node.put("initial_balance_high", 0.0);
            node.put("initial_balance_low", 0.0);
        } else {
            node.put("open_price", Math.round(openPx * 100.0) / 100.0);
            node.put("high", Math.round(highPx * 100.0) / 100.0);
            node.put("low", lowPx == Double.MAX_VALUE ? 0.0 : Math.round(lowPx * 100.0) / 100.0);
            node.put("gap_from_prior_close", priorDayClose > 0 ? Math.round((openPx - priorDayClose) * 100.0) / 100.0 : 0.0);
            node.put("initial_balance_high", ibHigh > 0 ? Math.round(ibHigh * 100.0) / 100.0 : 0.0);
            node.put("initial_balance_low", ibLow == Double.MAX_VALUE ? 0.0 : Math.round(ibLow * 100.0) / 100.0);
        }
        // derived: range_position_pct
        double rp = 0.0;
        if (seen && highPx > lowPx) rp = (currentPrice - lowPx) / (highPx - lowPx) * 100.0;
        node.put("range_position_pct", Math.round(rp * 100.0) / 100.0);

        // derived: gap_direction
        double gapThresh = priorDayClose > 0 ? priorDayClose * 0.001 : 0.0;
        double gapVal = seen ? (openPx - priorDayClose) : 0.0;
        String gapDir = (priorDayClose <= 0 || Math.abs(gapVal) < gapThresh) ? "flat" : (gapVal > 0 ? "up" : "down");
        node.put("gap_direction", gapDir);

        // derived: open_location vs daily value area
        String openLoc = "in_value";
        if (seen && dailyVah > 0 && dailyVal > 0) {
            if (openPx > dailyVah) openLoc = "above_value";
            else if (openPx < dailyVal) openLoc = "below_value";
        }
        node.put("open_location", openLoc);

        // derived: sweep_flag + liquidity_sweep_direction
        boolean above = lastSweepAbove > 0;
        boolean below = lastSweepBelow > 0;
        boolean sweep = above || below;
        String sweepDir = "none";
        if (above && below) sweepDir = (lastSweepAbove >= lastSweepBelow) ? "above" : "below";
        else if (above) sweepDir = "above";
        else if (below) sweepDir = "below";
        node.put("sweep_flag", sweep);
        node.put("liquidity_sweep_direction", sweepDir);

        // derived: day_type (screener-provisional, not Tom-derived)
        // Ratio of initial balance width to prior day range classifies opening.
        // No Tom threshold exists. Provisional until 3-snapshot evidence.
        String dayType = "UNKNOWN";
        String dayTypeConf = "none";
        if (seen && ibHigh > 0 && ibLow > 0 && ibHigh > ibLow
                && priorDayHigh > 0 && priorDayLow > 0 && priorDayHigh > priorDayLow) {
            double ibWidth = ibHigh - ibLow;
            double priorRange = priorDayHigh - priorDayLow;
            double ibRatio = ibWidth / priorRange;
            double extAbove = (highPx - ibHigh) / ibWidth;
            double extBelow = (ibLow - lowPx) / ibWidth;
            boolean trendUp = ibRatio < 0.5 && extAbove > 1.0;
            boolean trendDown = ibRatio < 0.5 && extBelow > 1.0;
            if (trendUp) { dayType = "trend_up"; dayTypeConf = "provisional"; }
            else if (trendDown) { dayType = "trend_down"; dayTypeConf = "provisional"; }
            else if (ibRatio > 0.7) { dayType = "range"; dayTypeConf = "provisional"; }
            else { dayType = "balance"; dayTypeConf = "provisional"; }
        }
        node.put("day_type", dayType);
        node.put("day_type_confidence", dayTypeConf);
        return node;
    }

    /** D3: US cash open 09:30 America/New_York as UTC for a date: 13:30Z during EDT, 14:30Z during EST. */
    static ZonedDateTime usEquityOpenUtc(LocalDate date) {
        return ZonedDateTime.of(date, LocalTime.of(9,30), ZoneId.of("America/New_York")).withZoneSameInstant(ZoneOffset.UTC);
    }

    private ObjectNode buildSessionTiming(ZonedDateTime now) {
        ObjectNode node = mapper.createObjectNode();
        LocalDate today = now.toLocalDate();
        if (today.equals(LocalDate.of(2026,11,27)) || today.equals(LocalDate.of(2026,12,24))) {
            ZonedDateTime earlyClose = ZonedDateTime.of(today, LocalTime.of(13,0), ZoneId.of("America/New_York")).withZoneSameInstant(ZoneOffset.UTC);
            long minutesUntilClose = ChronoUnit.MINUTES.between(now, earlyClose);
            node.put("current_session", "us_early_close");
            node.put("us_equity_open_window", !now.isBefore(earlyClose) && now.isBefore(earlyClose.plusMinutes(30)));
            if (minutesUntilClose < 0) node.putNull("us_equity_open_in_minutes"); else node.put("us_equity_open_in_minutes", minutesUntilClose);
            node.put("holiday_note", "Early close - US markets close at 1pm ET");
            return node;
        }
        Set<LocalDate> holidays = new HashSet<>(java.util.Arrays.asList(
            LocalDate.of(2026,1,1), LocalDate.of(2026,1,19), LocalDate.of(2026,2,16),
            LocalDate.of(2026,4,3), LocalDate.of(2026,5,25), LocalDate.of(2026,6,19),
            LocalDate.of(2026,7,3), LocalDate.of(2026,9,7), LocalDate.of(2026,11,26),
            LocalDate.of(2026,12,25)
        ));
        if (holidays.contains(today)) {
            node.put("current_session", "us_holiday");
            node.put("us_equity_open_window", false);
            node.putNull("us_equity_open_in_minutes");
            String holidayName;
            if (today.equals(LocalDate.of(2026,1,1))) holidayName = "New Year's Day";
            else if (today.equals(LocalDate.of(2026,1,19))) holidayName = "Martin Luther King Jr. Day";
            else if (today.equals(LocalDate.of(2026,2,16))) holidayName = "Presidents' Day";
            else if (today.equals(LocalDate.of(2026,4,3))) holidayName = "Good Friday";
            else if (today.equals(LocalDate.of(2026,5,25))) holidayName = "Memorial Day";
            else if (today.equals(LocalDate.of(2026,6,19))) holidayName = "Juneteenth";
            else if (today.equals(LocalDate.of(2026,7,3))) holidayName = "Independence Day (observed)";
            else if (today.equals(LocalDate.of(2026,9,7))) holidayName = "Labor Day";
            else if (today.equals(LocalDate.of(2026,11,26))) holidayName = "Thanksgiving";
            else if (today.equals(LocalDate.of(2026,12,25))) holidayName = "Christmas";
            else holidayName = "US Holiday";
            node.put("holiday_note", holidayName + " - US markets closed");
            return node;
        }
        int hour = now.getHour();
        // BUG-009 fix (2026-09-10): use decimal hour so us_cash_open can fire.
        double hourDec = hour + now.getMinute() / 60.0;
        // L25 fix (2026-09-16): session labels DST-aware. US cash open shifts with DST.
        ZonedDateTime nyOpenUtcRef = usEquityOpenUtc(now.toLocalDate());
        double usOpenHr = nyOpenUtcRef.getHour() + nyOpenUtcRef.getMinute() / 60.0;
        String session;
        if (hourDec >= 0.0 && hourDec < 7.0) session = "asian";
        else if (hourDec >= 7.0 && hourDec < 9.0) session = "asia_europe_overlap";
        else if (hourDec >= 9.0 && hourDec < usOpenHr - 0.5) session = "european";
        else if (hourDec >= usOpenHr - 0.5 && hourDec < usOpenHr) session = "us_premarket";
        else if (hourDec >= usOpenHr && hourDec < usOpenHr + 1.5) session = "us_cash_open";
        else if (hourDec >= usOpenHr + 1.5 && hourDec < usOpenHr + 3.0) session = "us_europe_overlap";
        else if (hourDec >= usOpenHr + 3.0 && hourDec < 20.0) session = "us_core";
        else if (hourDec >= 20.0 && hourDec < 21.0) session = "us_close";
        else session = "after_hours";
        node.put("current_session", session);

        int[] fundingHours = {0,8,16};
        int minute = now.getMinute();
        boolean fundingWindow = false;
        for (int h : fundingHours) {
            int minToFunding = (h - hour) * 60 - minute;
            if (minToFunding < 0) minToFunding += 24*60;
            if (minToFunding <= 5 || minToFunding >= 24*60-5) { fundingWindow = true; break; }
        }
        node.put("funding_reset_window", fundingWindow);

        ZonedDateTime nyOpenUtc = usEquityOpenUtc(now.toLocalDate());
        boolean usOpenWindow = !now.toLocalDate().equals(nyOpenUtc.toLocalDate()) ? false : now.isAfter(nyOpenUtc) && now.isBefore(nyOpenUtc.plusMinutes(90));
        node.put("us_equity_open_window", usOpenWindow);
        long minutesUntilUsOpen = ChronoUnit.MINUTES.between(now, nyOpenUtc);
        if (minutesUntilUsOpen < 0) minutesUntilUsOpen += 24*60;
        node.put("us_equity_open_in_minutes", minutesUntilUsOpen);
        return node;
    }

    private boolean computeSpeedPickingUp(JsonNode klines1m) {
        if (klines1m == null || klines1m.size() < 15) return false;
        int size = klines1m.size();
        double recentSum = 0, priorSum = 0;
        for (int i = size-15; i < size; i++) {
            double range = klines1m.get(i).get(2).asDouble() - klines1m.get(i).get(3).asDouble();
            recentSum += range;
        }
        for (int i = size-60; i < size-15; i++) {
            if (i < 0) continue;
            double range = klines1m.get(i).get(2).asDouble() - klines1m.get(i).get(3).asDouble();
            priorSum += range;
        }
        double recentAvg = recentSum / 15;
        double priorAvg = priorSum / 45;
        return priorAvg > 0 && recentAvg > priorAvg * 1.5;
    }

    private Boolean computeRejectionWick(JsonNode klines1m, double currentPrice) {
        if (klines1m == null || klines1m.size() < 3) return null;
        int size = klines1m.size();
        for (int i = size-3; i < size; i++) {
            JsonNode bar = klines1m.get(i);
            double open = bar.get(1).asDouble(), high = bar.get(2).asDouble(), low = bar.get(3).asDouble(), close = bar.get(4).asDouble();
            double body = Math.abs(close - open);
            double upperWick = high - Math.max(open, close);
            double lowerWick = Math.min(open, close) - low;
            if (upperWick > 2 * body && high >= currentPrice * 1.001) return true;
            if (lowerWick > 2 * body && low <= currentPrice * 0.999) return true;
        }
        return false;
    }


    /**
     * Fetch a snapshot as of a historical timestamp.
     * Used for validation (Rule 32). Live-only fields are set to neutral defaults.
     */
    public ObjectNode fetchHistoricalSnapshot(String symbol, Instant asOf) throws IOException {
        ZonedDateTime now = asOf.atZone(ZoneOffset.UTC);
        long asOfMillis = asOf.toEpochMilli();

        // Fetch multi-timeframe klines as of asOf
        Map<String, JsonNode> mtf = fetchMultiTimeframeAsOf(symbol, asOf);
        JsonNode klines1m = mtf.get("1m");
        JsonNode klines1h = mtf.get("1h");
        if (klines1m == null || klines1m.size() == 0) {
            throw new IOException("Failed to fetch historical 1m klines for " + symbol + " at " + asOf);
        }

        double currentPrice = klines1m.get(klines1m.size() - 1).get(4).asDouble();

        // ── Daily bars (since 00:00 UTC of asOf date) ──
        long todayStartMs = now.truncatedTo(ChronoUnit.DAYS).toInstant().toEpochMilli();
        List<JsonNode> dailyBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= todayStartMs) dailyBars.add(bar);
        }
        if (dailyBars.isEmpty()) {
            int start = Math.max(0, klines1m.size() - 200);
            for (int i = start; i < klines1m.size(); i++) dailyBars.add(klines1m.get(i));
        }

        // ── Weekly bars (Monday 00:00 UTC to asOf, 1h) ──
        ZonedDateTime mondayStart = now.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
                .truncatedTo(ChronoUnit.DAYS);
        long mondayStartMs = mondayStart.toInstant().toEpochMilli();
        List<JsonNode> weeklyBars = new ArrayList<>();
        if (klines1h != null) {
            for (JsonNode bar : klines1h) {
                if (bar.get(0).asLong() >= mondayStartMs) weeklyBars.add(bar);
            }
        }

        // ── Post-funding bars (last 08:00 UTC before asOf) ──
        ZonedDateTime lastEightUtc = now.withHour(8).withMinute(0).withSecond(0).withNano(0);
        if (now.isBefore(lastEightUtc)) lastEightUtc = lastEightUtc.minusDays(1);
        long postFundingStartMs = lastEightUtc.toInstant().toEpochMilli();
        List<JsonNode> postFundingBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= postFundingStartMs) postFundingBars.add(bar);
        }

        // ── 4H intraday bars ──
        int boundaryHour = (now.getHour() / 4) * 4;
        ZonedDateTime lastFourHourBoundary = now.withHour(boundaryHour).withMinute(0).withSecond(0).withNano(0);
        long fourHourStartMs = lastFourHourBoundary.toInstant().toEpochMilli();
        List<JsonNode> intraday4hBars = new ArrayList<>();
        for (JsonNode bar : klines1m) {
            if (bar.get(0).asLong() >= fourHourStartMs) intraday4hBars.add(bar);
        }

        // ── Prior day bars ──
        ZonedDateTime yesterdayStartUtc = now.minusDays(1).truncatedTo(ChronoUnit.DAYS);
        ZonedDateTime yesterdayEndUtc = yesterdayStartUtc.plusDays(1).minusNanos(1);
        JsonNode yesterdayKlines = hist().klinesRange(symbol, "1m",
                yesterdayStartUtc.toInstant().toEpochMilli(),
                yesterdayEndUtc.toInstant().toEpochMilli(), 1440);
        List<JsonNode> priorDayBars = new ArrayList<>();
        if (yesterdayKlines != null) {
            for (JsonNode bar : yesterdayKlines) priorDayBars.add(bar);
        }

        // ── Alignment check ──
        boolean alignmentPass = true;
        double refClose = currentPrice;
        for (String tf : new String[]{"1w","1d","4h","1h","15m","5m","1m"}) {
            JsonNode k = mtf.get(tf);
            if (k == null || k.size() == 0) continue;
            double close = k.get(k.size()-1).get(4).asDouble();
            double drift = Math.abs(close - refClose) / refClose;
            if (drift >= 0.001) { alignmentPass = false; break; }
        }

        // ── Build VP nodes ──
        ObjectNode weeklyVp = buildVp(weeklyBars, false);
        // Previous two weeks VPOC (requires additional historical fetches)
        ZonedDateTime prevWeekMonday = mondayStart.minusWeeks(1);
        ZonedDateTime prevWeekSunday = prevWeekMonday.plusDays(6).withHour(23).withMinute(59).withSecond(59).withNano(0);
        JsonNode prevWeekKlines = hist().klinesRange(symbol, "1h",
                prevWeekMonday.toInstant().toEpochMilli(),
                prevWeekSunday.toInstant().toEpochMilli(), 168);
        List<JsonNode> prevWeekBars = new ArrayList<>();
        if (prevWeekKlines != null) {
            for (JsonNode bar : prevWeekKlines) prevWeekBars.add(bar);
        }
        ObjectNode prevWeekVp = buildVp(prevWeekBars, false);
        double priorWeekPoc = prevWeekVp.get("poc").asDouble();

        ZonedDateTime twoWeekMonday = mondayStart.minusWeeks(2);
        ZonedDateTime twoWeekSunday = twoWeekMonday.plusDays(6).withHour(23).withMinute(59).withSecond(59).withNano(0);
        JsonNode twoWeekKlines = hist().klinesRange(symbol, "1h",
                twoWeekMonday.toInstant().toEpochMilli(),
                twoWeekSunday.toInstant().toEpochMilli(), 168);
        List<JsonNode> twoWeekBars = new ArrayList<>();
        if (twoWeekKlines != null) {
            for (JsonNode bar : twoWeekKlines) twoWeekBars.add(bar);
        }
        ObjectNode twoWeekVp = buildVp(twoWeekBars, false);
        double twoWeekAgoPoc = twoWeekVp.get("poc").asDouble();

        weeklyVp.put("prior_week_poc", Math.round(priorWeekPoc * 100.0) / 100.0);
        weeklyVp.put("two_week_ago_poc", Math.round(twoWeekAgoPoc * 100.0) / 100.0);
        ObjectNode dailyVp = buildVp(dailyBars, true);
        ObjectNode postFundingVp = buildVp(postFundingBars, false, 10.0); // [SCREENER] bin=10.0 - B059 untagged, no citation
        ObjectNode intraday4hVp = buildVp(intraday4hBars, false);
        ObjectNode priorDayVp = buildVp(priorDayBars, false);
        double priorDayClose = 0.0, priorDayHigh = 0.0, priorDayLow = Double.MAX_VALUE;
        for (JsonNode bar : priorDayBars) {
            double h = bar.get(2).asDouble();
            double l = bar.get(3).asDouble();
            if (h > priorDayHigh) priorDayHigh = h;
            if (l < priorDayLow) priorDayLow = l;
        }
        if (!priorDayBars.isEmpty()) {
            priorDayClose = priorDayBars.get(priorDayBars.size() - 1).get(4).asDouble();
        }
        priorDayVp.put("close", Math.round(priorDayClose * 100.0) / 100.0);
        priorDayVp.put("high", Math.round(priorDayHigh * 100.0) / 100.0);
        priorDayVp.put("low", priorDayLow == Double.MAX_VALUE ? 0.0 : Math.round(priorDayLow * 100.0) / 100.0);

        // ── VWAP (trimmed) ──
        ObjectNode vwapNode = buildVwap(dailyBars);
        vwapNode.remove("+3s");
        vwapNode.remove("-3s");

        // ── CVD (trimmed) ──
        // DSA-HYG-006 (2026-09-10): session-scope CVD. Was using klines1m (24h).
        // Wrap dailyBars (List<JsonNode>) in ArrayNode since buildCvd takes JsonNode.
        ArrayNode dailyBarsForCvd = mapper.createArrayNode();
        for (JsonNode bar : dailyBars) dailyBarsForCvd.add(bar);
        ObjectNode cvdNode = buildCvd(dailyBarsForCvd, klines1m);
        cvdNode.put("scope", "session");
        cvdNode.put("gating_window", "rolling_1m");  // B070: slope/last_3_delta/cvd_recent are not anchored to 00:00 UTC
        cvdNode.put("session_start_utc", now.truncatedTo(ChronoUnit.DAYS).toInstant().toString());

        // ── Structure ──
        ObjectNode structure = buildStructure(mtf, currentPrice);

        // ── Conditions (minimal, live-only proofs set defaults) ──
        ObjectNode cond = mapper.createObjectNode();
        double poc = dailyVp.get("poc").asDouble();
        double vah = dailyVp.get("vah").asDouble();
        double val = dailyVp.get("val").asDouble();
        String priceVsPoc = currentPrice > poc ? "above" : currentPrice < poc ? "below" : "at_poc";
        String priceVsVa = currentPrice > vah ? "above_vah" : currentPrice < val ? "below_val" : "in_va";
        cond.put("price_vs_poc", priceVsPoc);
        cond.put("price_vs_va", priceVsVa);
        cond.put("vp_shape", dailyVp.get("shape").asText());
        cond.put("vwap_slope", vwapNode.get("slope").asText());
        cond.put("cvd_slope", cvdNode.get("slope").asText());
        cond.put("cvd_trade_flow_aligned", false); // live-only, set false
        int unfilledCount = 0;
        ObjectNode nearestUnfilled = null;
        List<FvgCalculator.Fvg> fvgs = fvgCalc.detect(klines1m, 5);
        for (FvgCalculator.Fvg f : fvgs) {
            if (!f.filled) {
                unfilledCount++;
                if (nearestUnfilled == null) {
                    nearestUnfilled = mapper.createObjectNode();
                    nearestUnfilled.put("type", f.type);
                    nearestUnfilled.put("top", Math.round(f.top * 100.0) / 100.0);
                    nearestUnfilled.put("bottom", Math.round(f.bottom * 100.0) / 100.0);
                }
            }
        }
        cond.put("fvg_unfilled_count", unfilledCount);
        if (nearestUnfilled != null) cond.set("fvg_nearest_unfilled", nearestUnfilled);
        else cond.putNull("fvg_nearest_unfilled");
        cond.putNull("book_imbalance");
        cond.put("funding_extreme", false);
        cond.put("oi_trend", "flat");
        cond.put("speed_picking_up", computeSpeedPickingUp(klines1m));
        Boolean rejectionWick = computeRejectionWick(klines1m, currentPrice);
        if (rejectionWick == null) cond.putNull("rejection_wick_at_zone");
        else cond.put("rejection_wick_at_zone", rejectionWick);
        cond.put("volume_spike_at_level", false);

        // ── Spot-perp basis ──
        ObjectNode spotPerpBasis = unavailableNode("historical snapshot: no live spot/mark data");
        spotPerpBasis.putNull("spot_price");
        spotPerpBasis.putNull("mark_price");
        spotPerpBasis.putNull("basis_pct");
        spotPerpBasis.put("direction", "unknown");

        // ── Liquidation clusters ──
        ObjectNode liquidationClusters = mapper.createObjectNode();
        liquidationClusters.putObject("nearest_above").put("price", 0.0);
        liquidationClusters.putObject("nearest_below").put("price", 0.0);
        liquidationClusters.put("warning", false);

        // ── Build root ──
        ObjectNode root = mapper.createObjectNode();
        root.put("timestamp_utc", asOf.toString());
        root.put("asset", symbol);
        root.put("current_price", Math.round(currentPrice * 100.0) / 100.0);
        root.put("alignment_pass", alignmentPass);
        root.set("weekly_vp", weeklyVp);
        root.set("daily_vp", dailyVp);
        root.set("post_funding_vp", postFundingVp);
        root.set("intraday_4h_vp", intraday4hVp);
        root.set("vwap", vwapNode);
        root.set("cvd", cvdNode);
        ObjectNode tradeFlow = mapper.createObjectNode();
        tradeFlow.putNull("net_delta_1m");
        tradeFlow.putNull("net_delta_5m");
        tradeFlow.putNull("net_delta_15m");
        tradeFlow.putNull("net_delta_1h");
        tradeFlow.put("confidence", "UNAVAILABLE");
        root.set("trade_flow", tradeFlow);
        root.set("structure", structure);
        ObjectNode ob = mapper.createObjectNode();
        ob.putNull("bid_ask_ratio");
        ob.put("confidence", "LOW");
        root.set("order_book_depth", ob);
        root.set("conditions", cond);
        root.set("prior_day", priorDayVp);
        ObjectNode fund = mapper.createObjectNode();
        fund.putNull("current_rate");
        fund.put("extreme", false);
        fund.put("confidence", "UNAVAILABLE");
        root.set("funding", fund);
        ObjectNode oi = mapper.createObjectNode();
        oi.put("direction", "flat");
        oi.put("change_1h_pct", 0.0);
        oi.put("delta_state", "neutral");
        oi.put("delta_state_price", "neutral");
        oi.put("confidence", "LOW");
        root.set("open_interest", oi);
        ObjectNode sessionTiming = buildSessionTiming(now);
        root.set("session_timing", sessionTiming);
        root.set("spot_perp_basis", spotPerpBasis);
        root.set("liquidation_clusters", liquidationClusters);
        ObjectNode oiBreakdown = unavailableNode("historical snapshot: no live long/short ratio data");
        oiBreakdown.putNull("retail");
        oiBreakdown.putNull("whale");
        oiBreakdown.putNull("topAccounts");
        root.set("oi_breakdown", oiBreakdown);
        ObjectNode liquidationWarning = mapper.createObjectNode();
        liquidationWarning.put("status", "none");
        liquidationWarning.putNull("nearest_cluster_distance_pct");
        liquidationWarning.put("note", "Historical snapshot; liquidation data not available.");
        root.set("liquidation_warning", liquidationWarning);
        root.set("session", buildSession(klines1m, priorDayClose, currentPrice, dailyVp.get("vah").asDouble(), dailyVp.get("val").asDouble(), priorDayVp.get("high").asDouble(), priorDayVp.get("low").asDouble()));
        ObjectNode dataQuality = mapper.createObjectNode();
        ArrayNode unavailableFields = dataQuality.putArray("unavailable_fields");
        for (String f : new String[]{"spot_perp_basis", "oi_breakdown", "trade_flow.net_delta_1m", "trade_flow.net_delta_5m",
                "trade_flow.net_delta_15m", "trade_flow.net_delta_1h", "conditions.book_imbalance", "order_book_depth.bid_ask_ratio", "funding.current_rate"}) {
            unavailableFields.add(f);
        }
        dataQuality.put("reason", "historical reconstruction from klines only; live-only inputs are null/UNAVAILABLE, never 0.0");
        root.set("data_quality", dataQuality);

        // ── Spot-perp basis ──

        // ── Liquidation clusters (historical fallback) ──

        // ── Setup Candidates ──
        ArrayNode setupCandidates = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m, fadeSeries1m(symbol, asOf));
        ArrayNode extraCandidates = ExtraSetupBuilder.build(mapper, root, mtf, klines1m);
        double clusterAbovePrice = liquidationClusters.get("nearest_above").get("price").asDouble();
        double clusterBelowPrice = liquidationClusters.get("nearest_below").get("price").asDouble();
        boolean warning = false;
        for (JsonNode cand : setupCandidates) {
            double stop = cand.get("math").get("stop").asDouble();
            double target = cand.get("math").get("target").asDouble();
            if (clusterAbovePrice > 0 && (Math.abs(clusterAbovePrice - stop) / stop < 0.005 || Math.abs(clusterAbovePrice - target) / target < 0.005)) warning = true;
            if (clusterBelowPrice > 0 && (Math.abs(clusterBelowPrice - stop) / stop < 0.005 || Math.abs(clusterBelowPrice - target) / target < 0.005)) warning = true;
        }
        ((com.fasterxml.jackson.databind.node.ObjectNode)liquidationClusters).put("warning", warning);
        root.set("setup_candidates", setupCandidates);
        root.set("module_candidates", extraCandidates);
        root.set("liquidation_clusters", liquidationClusters);
        root.set("setup_candidates", setupCandidates);
        return root;
    }

    private ObjectNode unavailableNode(String reason) {
        ObjectNode node = mapper.createObjectNode();
        node.put("confidence", "UNAVAILABLE");
        node.put("reason", reason);
        return node;
    }

    private Map<String, JsonNode> fetchMultiTimeframeAsOf(String symbol, Instant asOf) {
        Map<String, Integer> configs = Map.of(
                "1w", 2, "1d", 7, "4h", 3, "1h", 168, "15m", 16, "5m", 48, "1m", 1440
        );
        Map<String, JsonNode> result = new ConcurrentHashMap<>();
        ExecutorService pool = Executors.newFixedThreadPool(4);
        List<Future<?>> futures = new ArrayList<>();
        for (Map.Entry<String, Integer> e : configs.entrySet()) {
            String tf = e.getKey();
            int limit = e.getValue();
            futures.add(pool.submit(() -> {
                try {
                    long durationMs = getDurationMillis(tf);
                    long start = asOf.toEpochMilli() - durationMs * limit;
                    JsonNode k = hist().klinesRange(symbol, tf, start, asOf.toEpochMilli(), limit);
                    dropFormingBar(k, asOf.toEpochMilli());
                    result.put(tf, k);
                } catch (IOException ex) {
                    System.err.println("[MTF] Failed " + tf + ": " + ex.getMessage());
                }
            }));
        }
        for (Future<?> f : futures) { try { f.get(30, TimeUnit.SECONDS); } catch (Exception ignored) {} }
        pool.shutdownNow();
        return result;
    }

    /** Calendar days of 1m bars handed to the family A fade call: 20 prior sessions plus today with holiday margin. */
    static final int FADE_SERIES_DAYS = 40;

    /**
     * Longer 1m series for SpikeFadeDetector (card tom-v2-recall-fire-rate): a snapshot's mtf 1m is 24 h, the detector
     * needs 21 sessions. Only with -Dmts.spikeFade=true; null (flag off or no data) = the detector sees the 24 h series
     * and fails closed. Used by this as-of path only; the live path is unchanged and research replays only reach it.
     */
    private JsonNode fadeSeries1m(String symbol, Instant asOf) {
        if (!SpikeFadeDetector.enabled()) return null;
        try {
            long end = asOf.toEpochMilli();
            JsonNode k = hist().klinesRange(symbol, "1m", end - FADE_SERIES_DAYS * 86_400_000L, end, FADE_SERIES_DAYS * 1440);
            dropFormingBar(k, end);
            return k;
        } catch (IOException ex) {
            System.err.println("[FADE] long 1m series failed: " + ex.getMessage());
            return null;
        }
    }

    private long getDurationMillis(String tf) {
        switch (tf) {
            case "1w": return 7L * 24 * 60 * 60 * 1000;
            case "1d": return 24L * 60 * 60 * 1000;
            case "4h": return 4L * 60 * 60 * 1000;
            case "1h": return 60L * 60 * 1000;
            case "15m": return 15L * 60 * 1000;
            case "5m": return 5L * 60 * 1000;
            case "1m": return 60L * 1000;
            default: return 60L * 60 * 1000;
        }
    }


    /**
     * Save a historical snapshot (for validation) to the snapshots directory.
     */
    public void saveHistoricalSnapshot(String symbol, Instant asOf) throws IOException {
        ObjectNode snapshot = fetchHistoricalSnapshot(symbol, asOf);
        Path dir = Paths.get("runtime_data", "snapshots");
        Files.createDirectories(dir);
        String file = symbol + "_historical_" + asOf.toString().replace(":", "").replace("-", "") + ".json";
        Path path = dir.resolve(file);
        mapper.writeValue(path.toFile(), snapshot);
        System.out.println("Snapshot saved to " + path.toAbsolutePath());
        System.out.println(snapshot.toPrettyString());
    }


    /** DSA_TASK_013 helper: compute [trades_per_sec, volume_per_sec] from an aggTrades array. */
    private double[] computeFlowStats(JsonNode trades) {
        if (trades == null || trades.size() < 2) return new double[]{0.0, 0.0};
        long firstTs = trades.get(0).get("T").asLong();
        long lastTs = trades.get(trades.size() - 1).get("T").asLong();
        long spanMs = lastTs - firstTs;
        if (spanMs <= 0) return new double[]{0.0, 0.0};
        double spanSec = spanMs / 1000.0;
        double count = trades.size();
        double totalQty = 0.0;
        for (JsonNode t : trades) {
            totalQty += t.get("q").asDouble();
        }
        return new double[]{count / spanSec, totalQty / spanSec};
    }

    /** DSA_TASK_014 helper: update per-instrument historical baseline and populate order_flow fields. */
    private void updateAndApplyHistoricalBaseline(String symbol, double curTps, double curVps, ObjectNode orderFlow) {
        Path dir = Paths.get("runtime_data", "speed_baselines");
        Path file = dir.resolve(symbol + "_speed_baseline.json");
        try {
            Files.createDirectories(dir);
            ObjectNode root;
            ArrayNode samples;
            if (Files.exists(file)) {
                root = (ObjectNode) mapper.readTree(file.toFile());
                samples = (ArrayNode) root.get("samples");
                if (samples == null) {
                    samples = root.putArray("samples");
                }
            } else {
                root = mapper.createObjectNode();
                samples = root.putArray("samples");
            }

            // Append current sample
            ObjectNode s = samples.addObject();
            s.put("ts", System.currentTimeMillis());
            s.put("tps", curTps);
            s.put("vps", curVps);

            // Prune: keep only samples within 30 days AND at most 100 samples
            long cutoff = System.currentTimeMillis() - 30L * 24L * 60L * 60L * 1000L;
            while (samples.size() > 0 && samples.get(0).get("ts").asLong() < cutoff) {
                samples.remove(0);
            }
            while (samples.size() > 100) {
                samples.remove(0);
            }

            // Compute medians
            List<Double> tpsList = new ArrayList<>();
            List<Double> vpsList = new ArrayList<>();
            for (JsonNode n : samples) {
                tpsList.add(n.get("tps").asDouble());
                vpsList.add(n.get("vps").asDouble());
            }
            Collections.sort(tpsList);
            Collections.sort(vpsList);
            double medTps = median(tpsList);
            double medVps = median(vpsList);
            int sampleCount = samples.size();

            String conf = sampleCount >= 20 ? "HIGH" : (sampleCount >= 5 ? "MEDIUM" : "LOW");

            orderFlow.put("historical_baseline_trades_per_sec", Math.round(medTps * 100.0) / 100.0);
            orderFlow.put("historical_baseline_volume_per_sec", Math.round(medVps * 100.0) / 100.0);
            orderFlow.put("historical_baseline_samples", sampleCount);
            orderFlow.put("historical_baseline_confidence", conf);
            orderFlow.put("speed_vs_historical", medTps > 0 ? Math.round((curTps / medTps) * 100.0) / 100.0 : 0.0);

            // Persist
            root.put("updated_utc", java.time.Instant.now().toString());
            root.put("symbol", symbol);
            root.put("sample_count", sampleCount);
            mapper.writerWithDefaultPrettyPrinter().writeValue(file.toFile(), root);
        } catch (Exception e) {
            orderFlow.put("historical_baseline_trades_per_sec", 0.0);
            orderFlow.put("historical_baseline_volume_per_sec", 0.0);
            orderFlow.put("historical_baseline_samples", 0);
            orderFlow.put("historical_baseline_confidence", "LOW");
            orderFlow.put("speed_vs_historical", 0.0);
            System.err.println("[DSA_TASK_014] baseline error for " + symbol + ": " + e.getMessage());
        }
    }

    /** DSA_TASK_014 helper: median of a sorted list. Returns 0.0 on empty. */
    private double median(List<Double> sorted) {
        if (sorted.isEmpty()) return 0.0;
        int n = sorted.size();
        if (n % 2 == 1) return sorted.get(n / 2);
        return (sorted.get(n / 2 - 1) + sorted.get(n / 2)) / 2.0;
    }

    private ObjectNode buildSpotPerpBasis(String symbol) {
        ObjectNode node = mapper.createObjectNode();
        try {
            JsonNode spot = client.spotPrice(symbol);
            JsonNode premium = client.premiumIndex(symbol);
            double spotPx = spot.get("price").asDouble();
            double markPx = premium.get("markPrice").asDouble();
            double basisPct = (markPx - spotPx) / spotPx * 100.0;
            node.put("spot_price", spotPx);
            node.put("mark_price", markPx);
            node.put("basis_pct", Math.round(basisPct * 100.0) / 100.0);
            node.put("direction", basisPct >= 0 ? "premium" : "discount");
            node.put("confidence", "HIGH");
        } catch (Exception e) {
            node.put("spot_price", 0.0);
            node.put("mark_price", 0.0);
            node.put("basis_pct", 0.0);
            node.put("direction", "unknown");
            node.put("confidence", "LOW");
        }
        return node;
    }

    /** 1h OI direction from openInterestHist; any failure or short history yields UNAVAILABLE/LOW, never a fake flat. */
    static ObjectNode oiFromHistory(BinanceClient client, String symbol, ObjectMapper mapper) {
        ObjectNode n = mapper.createObjectNode();
        try {
            JsonNode h = client.openInterestHist(symbol, "1h", 2);
            if (h != null && h.size() >= 2) {
                double prev = h.get(0).get("sumOpenInterest").asDouble();
                double curr = h.get(1).get("sumOpenInterest").asDouble();
                String dir = "flat";
                if (curr > prev * 1.001) dir = "rising";
                else if (curr < prev * 0.999) dir = "falling";
                n.put("direction", dir);
                n.put("change_1h_pct", prev != 0 ? (curr - prev) / prev * 100.0 : 0.0);
                n.put("confidence", "HIGH");
                return n;
            }
        } catch (Exception e) { /* fall through to UNAVAILABLE */ }
        n.put("direction", "UNAVAILABLE");
        n.putNull("change_1h_pct");
        n.put("confidence", "LOW");
        return n;
    }

        // OI delta 4-state classifier per INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 2.
    // Input: volume delta (trade_flow.net_delta_1h), sign only. Family per dictionary:
    // net_delta_* maps to CoinGlass "Volume Delta" (flow), not positioning.
    // Mapping: rising OI + pos delta = aggressive_long; rising + neg = aggressive_short;
    //          falling + neg = rekt_long; falling + pos = rekt_short.
    // Window (1h) matches open_interest.change_1h_pct. Bar-to-bar at 5m is the
    // professional standard (BackQuant, GoCharting); B044 tracks the delta source swap.
    // Sibling field delta_state_price will be emitted for backtest comparison of both schools.
    private static String classifyOiDeltaState(String oiDirection, double netDelta1h) {
        boolean rising = "rising".equals(oiDirection);
        boolean falling = "falling".equals(oiDirection);
        if (rising && netDelta1h > 0) return "aggressive_long";
        if (rising && netDelta1h < 0) return "aggressive_short";
        if (falling && netDelta1h < 0) return "rekt_long";
        if (falling && netDelta1h > 0) return "rekt_short";
        return "neutral";
    }
private ObjectNode buildOiBreakdown(String symbol) {
        ObjectNode node = mapper.createObjectNode();
        try {
            JsonNode retailAcc = client.longShortRatio(symbol, "1h", 5);
            JsonNode whalePos = client.topLongShortPositionRatio(symbol, "1h", 5);
            double retailRatio = retailAcc.get(retailAcc.size()-1).get("longShortRatio").asDouble();
            double whaleRatio = whalePos.get(whalePos.size()-1).get("longShortRatio").asDouble();
            double retailChange1h = retailAcc.size()>=2 ? retailAcc.get(retailAcc.size()-1).get("longShortRatio").asDouble() - retailAcc.get(retailAcc.size()-2).get("longShortRatio").asDouble() : 0.0;
            double retailChange4h = retailAcc.size()>=5 ? retailAcc.get(retailAcc.size()-1).get("longShortRatio").asDouble() - retailAcc.get(retailAcc.size()-5).get("longShortRatio").asDouble() : 0.0;
            double whaleChange1h = whalePos.size()>=2 ? whalePos.get(whalePos.size()-1).get("longShortRatio").asDouble() - whalePos.get(whalePos.size()-2).get("longShortRatio").asDouble() : 0.0;
            double whaleChange4h = whalePos.size()>=5 ? whalePos.get(whalePos.size()-1).get("longShortRatio").asDouble() - whalePos.get(whalePos.size()-5).get("longShortRatio").asDouble() : 0.0;
            ObjectNode retail = node.putObject("retail");
            retail.put("long_short_ratio", retailRatio);
            retail.put("change_1h", Math.round(retailChange1h*10000.0)/10000.0);
            retail.put("change_4h", Math.round(retailChange4h*10000.0)/10000.0);
            ObjectNode whale = node.putObject("whale");
            whale.put("long_short_ratio", whaleRatio);
            whale.put("change_1h", Math.round(whaleChange1h*10000.0)/10000.0);
            whale.put("change_4h", Math.round(whaleChange4h*10000.0)/10000.0);
            ObjectNode topAccounts = node.putObject("topAccounts");
            try {
                JsonNode topAcc = client.topLongShortAccountRatio(symbol, "1h", 5);
                double topRatio = topAcc.get(topAcc.size()-1).get("longShortRatio").asDouble();
                double topChange1h = topAcc.size()>=2 ? topAcc.get(topAcc.size()-1).get("longShortRatio").asDouble() - topAcc.get(topAcc.size()-2).get("longShortRatio").asDouble() : 0.0;
                double topChange4h = topAcc.size()>=5 ? topAcc.get(topAcc.size()-1).get("longShortRatio").asDouble() - topAcc.get(topAcc.size()-5).get("longShortRatio").asDouble() : 0.0;
                topAccounts.put("long_short_ratio", topRatio);
                topAccounts.put("change_1h", Math.round(topChange1h*10000.0)/10000.0);
                topAccounts.put("change_4h", Math.round(topChange4h*10000.0)/10000.0);
            } catch (Exception eTop) {
                node.putNull("topAccounts");   // B153/B136: unavailable is null, never a fake 0.0 ratio
                node.put("topAccounts_note", "unavailable");
            }
            node.put("confidence", "MEDIUM");
            node.put("note", "Proxy data - account/position ratio, not absolute OI");
        } catch (Exception e) {
            node.putNull("retail");   // B153/B136: unavailable is null, never a fake 0.0 ratio
            node.putNull("whale");
            node.putNull("topAccounts");
            node.put("confidence", "UNAVAILABLE");
            node.put("note", "OI breakdown unavailable");
        }
        return node;
    }
    public void saveSnapshot(String symbol, BinanceLiquidationAccumulator liqAccumulator) throws IOException {
        ObjectNode snapshot = fetchSnapshot(symbol, liqAccumulator);
        Path dir = Paths.get("runtime_data", "snapshots");
        Files.createDirectories(dir);
        String file = symbol + "_" + java.time.LocalDate.now() + "_" + System.currentTimeMillis() + ".json";
        Path path = dir.resolve(file);
        mapper.writeValue(path.toFile(), snapshot);
        System.out.println("Snapshot saved to " + path.toAbsolutePath());
        System.out.println(snapshot.toPrettyString());
    }

    public void shutdown() { client.shutdown(); }
}

