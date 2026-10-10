package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.*;

public class ExtraSetupBuilder {
    public static ArrayNode build(ObjectMapper mapper, ObjectNode root, Map<String, JsonNode> mtf, JsonNode klines1m) {
        ArrayNode extra = mapper.createArrayNode();
        double price = root.get("current_price").asDouble();
        ObjectNode cond = (ObjectNode) root.get("conditions");
        ObjectNode structure = (ObjectNode) root.get("structure");

        // FVG: EXIT/target area only, never an entry (compiled_engine.md section 2 zone map:
        // "target areas, not entry"; SetupCandidatesBuilder.setupTypeFor returns null for fvg).
        // fvg_short/fvg_long entries removed 2026-10-01 (consolidation TOM trace).


        // Momentum setup
        boolean speedUp = cond.get("speed_picking_up").asBoolean(false);
        int consec = speedFromKlines(klines1m);
        if (speedUp && consec >= 3) {
            String dir = price < previousClose(klines1m) ? "short" : "long";
            String setupType = "momentum_" + dir;
            ObjectNode cand = extra.addObject();
            cand.put("rank", 10 + extra.size());
            cand.put("setup_type", setupType);
            cand.put("direction", dir);
            ObjectNode zone = cand.putObject("zone");
            zone.put("name", "current_price");
            zone.put("price", price);
            zone.put("type", "momentum");
            ObjectNode math = cand.putObject("math");
            math.put("distance_pct", 0.0);
            math.put("tier", "trigger_ready");
            math.put("substate", "at_zone");
            double stop = dir.equals("short") ? previousHigh(klines1m) : previousLow(klines1m);
            double target = dir.equals("short") ? nearestSupport(root, price) : nearestResistance(root, price);
            math.put("stop", stop);
            math.put("target", target);
            math.put("gross_rr", target > 0 ? Math.round(Math.abs(target-price)/Math.abs(price-stop)*100.0)/100.0 : 0.0);
            double _net   = target > 0 ? ExecutionMathConstants.netRR(root.path("asset").asText(null), price, target, stop) : 0.0;  // B070: fee model, was gross * 0.75
            math.put("net_rr", Math.round(_net*100.0)/100.0);
            double _gross = target > 0 ? Math.abs(target-price)/Math.abs(price-stop) : 0.0;
            math.put("rr_sanity", _gross >= 1.5);
            final double netRrFloor = NetRrFloor.read();  // single source: MyTradingSys/system/net_rr_floor.json
            math.put("net_rr_sanity", _net >= netRrFloor);
            if (!(_net >= netRrFloor)) {  // negated so an unreadable floor (NaN) rejects
                // B039: no RR gate — reject momentum candidate
                extra.remove(extra.size() - 1);
                return extra;
            }
            ObjectNode proof = cand.putObject("proof");
            proof.put("speed_picking_up", true);
            proof.put("consecutive_large", consec);
            proof.put("cvd_aligned", cond.get("cvd_trade_flow_aligned").asBoolean());
            ObjectNode score = cand.putObject("score");
            score.put("raw", 70);
            score.put("confidence", "B");
            score.put("proof_count", 2);
            score.put("confluence_bonus", 0);
        }
        return extra;
    }

    private static double previousClose(JsonNode klines) { if (klines.size()<2) return 0; return klines.get(klines.size()-2).get(4).asDouble(); }
    private static double previousHigh(JsonNode klines) { if (klines.size()<3) return 0; double h=0; for(int i=klines.size()-3;i<klines.size()-1;i++) h=Math.max(h,klines.get(i).get(2).asDouble()); return h; }
    private static double previousLow(JsonNode klines) { if (klines.size()<3) return Double.MAX_VALUE; double l=Double.MAX_VALUE; for(int i=klines.size()-3;i<klines.size()-1;i++) l=Math.min(l,klines.get(i).get(3).asDouble()); return l==Double.MAX_VALUE?0:l; }
    private static int speedFromKlines(JsonNode klines) { int n=klines.size(); if(n<10) return 0; double avgRange=0; for(int i=n-10;i<n;i++) avgRange += klines.get(i).get(2).asDouble()-klines.get(i).get(3).asDouble(); avgRange/=10; int consec=0; for(int i=n-10;i<n;i++){ double r=klines.get(i).get(2).asDouble()-klines.get(i).get(3).asDouble(); if(r>1.5*avgRange) consec++; else consec=0; } return consec; }
    private static double nearestSupport(ObjectNode root, double below) { double best=0; String[] objs={"post_funding_vp","intraday_4h_vp","daily_vp","weekly_vp"}; for(String o:objs){ JsonNode vp=root.get(o); if(vp!=null&&vp.has("val")){ double v=vp.get("val").asDouble(); if(v<below && v>best) best=v; } } if(best==0 && root.has("prior_day") && root.get("prior_day").has("low")){ best=root.get("prior_day").get("low").asDouble(); } return best; }
    private static double nearestResistance(ObjectNode root, double above) { double best=Double.MAX_VALUE; String[] objs={"post_funding_vp","intraday_4h_vp","daily_vp","weekly_vp"}; for(String o:objs){ JsonNode vp=root.get(o); if(vp!=null&&vp.has("vah")){ double v=vp.get("vah").asDouble(); if(v>above && v<best) best=v; } } if(best==Double.MAX_VALUE && root.has("prior_day") && root.get("prior_day").has("high")){ best=root.get("prior_day").get("high").asDouble(); } return best==Double.MAX_VALUE?0:best; }
}
