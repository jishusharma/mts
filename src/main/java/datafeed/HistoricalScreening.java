package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.time.*;
import java.util.*;
import java.io.*;

public class HistoricalScreening {
    public static void run(String symbol, Instant start, Instant end, int intervalHours) {
        MarketDataSnapshot mds = new MarketDataSnapshot();
        BinanceClient client = new BinanceClient();
        List<Result> results = new ArrayList<>();
        String prevOiTrend1 = "";
        String prevOiTrend2 = "";
        StringBuilder csv = new StringBuilder("timestamp,price,weekly_poc,distance_pct,oi_trend,prev_oi_trend_1,prev_oi_trend_2,speed_up,all_short,outcome_6h_pnl_pct\n");

        Instant ts = start;
        while (!ts.isAfter(end)) {
                String oiTrend = "";
            try {
                ObjectNode snap = mds.fetchHistoricalSnapshot(symbol, ts);
                double price = snap.get("current_price").asDouble();
                double poc = snap.get("weekly_vp").get("poc").asDouble();
                double distPct = Math.abs(price - poc) / poc;
                if (distPct > 0.001) { ts = ts.plus(Duration.ofHours(intervalHours)); continue; }

                JsonNode setups = snap.get("setup_candidates");
                boolean allShort = setups.size() > 0;
                for (JsonNode s : setups) {
                    if (!"short".equals(s.get("direction").asText())) { allShort = false; break; }
                }
                if (!allShort) { ts = ts.plus(Duration.ofHours(intervalHours)); continue; }

                oiTrend = snap.get("open_interest").get("direction").asText();
                boolean speedUp = snap.get("conditions").get("speed_picking_up").asBoolean(false);
                if (!speedUp) { ts = ts.plus(Duration.ofHours(intervalHours)); prevOiTrend2 = prevOiTrend1; prevOiTrend1 = oiTrend; continue; }

                // Check OI rising -> flat within last 2 hours
                boolean oiStall = ("rising".equals(prevOiTrend1) || "rising".equals(prevOiTrend2)) && "flat".equals(oiTrend);
                if (!oiStall) { ts = ts.plus(Duration.ofHours(intervalHours)); prevOiTrend2 = prevOiTrend1; prevOiTrend1 = oiTrend; continue; }

                // Forward outcome 6h later
                Instant future = ts.plus(Duration.ofHours(6));
                double futurePrice = price;
            try {
                    JsonNode futureKlines = client.klinesRange(symbol, "1h", future.toEpochMilli(), future.plus(Duration.ofHours(1)).toEpochMilli(), 1);
                    if (futureKlines.size() > 0) futurePrice = futureKlines.get(0).get(4).asDouble();
                } catch (Exception e) { }
                double pnlPct = (futurePrice - price) / price * 100.0;

                Result r = new Result(ts.toString(), price, poc, distPct, oiTrend, prevOiTrend1, prevOiTrend2, speedUp, allShort, pnlPct);
                results.add(r);
                csv.append(ts).append(",").append(price).append(",").append(poc).append(",").append(distPct).append(",").append(oiTrend).append(",").append(prevOiTrend1).append(",").append(prevOiTrend2).append(",").append(speedUp).append(",").append(allShort).append(",").append(pnlPct).append("\n");
            } catch (Exception e) {
                // skip timestamps with errors
            }
            ts = ts.plus(Duration.ofHours(intervalHours));
            prevOiTrend2 = prevOiTrend1;
            prevOiTrend1 = oiTrend;
        }

        // Save CSV
        try (PrintWriter out = new PrintWriter("runtime_data/screening_results.csv", "UTF-8")) {
            out.print(csv.toString());
        } catch (Exception e) { }

        // Print summary
        System.out.println("=== HISTORICAL SCREENING RESULTS ===");
        System.out.println("Matches: " + results.size());
        if (!results.isEmpty()) {
            double winRate = results.stream().filter(r -> r.pnlPct < 0).count() * 100.0 / results.size();
            double avgMove = results.stream().mapToDouble(r -> r.pnlPct).average().orElse(0);
            System.out.println("Win rate (breakdown below weekly POC): " + winRate + "%");
            System.out.println("Average move 6h later: " + avgMove + "%");
            for (Result r : results) System.out.println(r);
        }
        client.shutdown();
    }

    static class Result {
        String timestamp; double price, poc, distPct; String oiTrend, prev1, prev2; boolean speedUp, allShort; double pnlPct;
        Result(String t, double p, double poc, double d, String oi, String p1, String p2, boolean s, boolean a, double pnl) { timestamp=t; price=p; this.poc=poc; distPct=d; oiTrend=oi; prev1=p1; prev2=p2; speedUp=s; allShort=a; pnlPct=pnl; }
        public String toString() { return String.format("%s | price=%.2f | poc=%.2f | dist=%.4f%% | oi=%s | prev1=%s | prev2=%s | speed=%b | short=%b | pnl=%.2f%%", timestamp, price, poc, distPct*100, oiTrend, prev1, prev2, speedUp, allShort, pnlPct); }
    }
}
