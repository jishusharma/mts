package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.ArrayList;
import java.util.List;

/**
 * Family A entry paths A2 and A3 (TOM_LAYER_V2_SPEC sections 2.3, 2.4 A-S3, 2.6 A-M5, 13, card tom-encode-fade-entry-paths),
 * behind {@code -Dmts.spikeFade=true}. Path A1 stays in {@link SpikeFadeDetector} untouched. Both paths need the same idea
 * (A-C1, A-C2) as A1: they are derived from the A1 candidate of the same instant (zone = session extreme, target A-T1,
 * proofs), so nothing fires on a day the idea fails. Entry is a reference price here; the fill is the NEXT bar's open
 * ({@link #entryOpen}), which a snapshot cannot know.
 *
 * <p>A3 "break of the top balance", Tom: "if I now see that we actually break out of this range to the downside, then I
 * would definitely look for another position down here" (k0zm5NYn0IQ:308-312). Top balance = high/low of the 1m bars after
 * the session extreme, at least {@value #BALANCE_MIN_BARS} bars (OURS: Tom gives no bar count); the signal is a 1m close
 * below that low (the card's rule). Entry type stop-market (spec 13: NO-SOURCE, stated). Stop A-S3: "my stop loss is now set
 * exactly above the last volume levels" (k0zm5NYn0IQ:460-463), observed from OHLC as the balance high, no buffer (NO-SOURCE).
 * The signal repeats on every later bar that closes below the (re-formed) balance low; the caller dedups to first attempts.
 *
 * <p>A2 "pullback after proof", Tom: "Anyone who wants to play it safe with such counter trades logically has to wait until
 * this let's call it bullish zone here where you can also clearly see the liquidity gets traded through"
 * (k0zm5NYn0IQ:316-321). First buying zone = lowest low of the {@value #BUYZONE_BARS} 1m bars before the extreme (OURS,
 * the last demand shelf under the high). Traded through = a 1m close below it after the extreme. Pullback = the last close
 * is back above the lowest low since the extreme but still below the zone; sell limit AT the zone (passive side, spec 13).
 * Stop and its rule are A1's (A-S1 or A-S2, above the extreme); target A-T1.
 */
final class SpikeFadePaths {
    private SpikeFadePaths() {}

    static final int BALANCE_MIN_BARS = 5;   // OURS
    static final int BUYZONE_BARS = 10;      // OURS

    /** The fill of a signal on bar signalIdx: the open of the next bar, NaN while that bar does not exist yet. */
    static double entryOpen(SpikeFadeDetector.Bars b, int signalIdx) {
        return signalIdx + 1 < b.n ? b.o[signalIdx + 1] : Double.NaN;
    }

    /** A2 and A3 candidates of the last bar that the session state admits (suppressions are logged by the state). */
    static List<ObjectNode> detect(ObjectMapper mapper, ObjectNode root, SpikeFadeDetector.Bars b, String marketState, String sym,
                                   SpikeFadeSessionState state) {
        List<ObjectNode> out = new ArrayList<>();
        ObjectNode base = SpikeFadeDetector.detect(mapper, root, b, marketState, sym);
        if (base == null) return out;
        int last = b.n - 1;
        int hIdx = indexOf(b, base.get("zone_time_ms").asLong());
        if (hIdx < 0 || hIdx >= last) return out;
        double target = base.get("math").get("target").asDouble();
        double close = b.c[last];
        double high = b.h[hIdx];

        ObjectNode a3 = a3(mapper, b, base, hIdx, last, target, close, sym);
        if (a3 != null) add(out, a3, b, state);
        ObjectNode a2 = a2(mapper, b, base, hIdx, last, target, high, sym);
        if (a2 != null) add(out, a2, b, state);
        return out;
    }

    private static void add(List<ObjectNode> out, ObjectNode c, SpikeFadeDetector.Bars b, SpikeFadeSessionState state) {
        if (state.admit(b.date[b.n - 1], b.t[b.n - 1]).allowed) out.add(c);
    }

    private static ObjectNode a3(ObjectMapper m, SpikeFadeDetector.Bars b, ObjectNode base, int hIdx, int last, double target,
                                 double close, String sym) {
        int n = last - 1 - hIdx;   // bars strictly between the extreme and the breaking bar
        if (n < BALANCE_MIN_BARS) return null;
        double lo = Double.POSITIVE_INFINITY, hi = Double.NEGATIVE_INFINITY;
        for (int i = hIdx + 1; i < last; i++) {
            if (!b.date[i].equals(b.date[last])) return null;
            lo = Math.min(lo, b.l[i]);
            hi = Math.max(hi, b.h[i]);
        }
        if (!(close < lo)) return null;
        double stop = hi;   // A-S3
        return build(m, base, "A3", "A-S3", "stop_market", "balance_low", lo, close, stop, target, sym);
    }

    private static ObjectNode a2(ObjectMapper m, SpikeFadeDetector.Bars b, ObjectNode base, int hIdx, int last, double target,
                                 double high, String sym) {
        if (hIdx < BUYZONE_BARS || !b.date[hIdx - BUYZONE_BARS].equals(b.date[hIdx])) return null;
        double zone = Double.POSITIVE_INFINITY;
        for (int i = hIdx - BUYZONE_BARS; i < hIdx; i++) zone = Math.min(zone, b.l[i]);
        if (!(zone < high)) return null;
        boolean through = false;
        double lowSince = Double.POSITIVE_INFINITY;
        for (int i = hIdx + 1; i <= last; i++) {
            if (b.c[i] < zone) through = true;
            lowSince = Math.min(lowSince, b.l[i]);
        }
        double close = b.c[last];
        if (!through || !(close > lowSince) || !(close < zone)) return null;
        double stop = base.get("math").get("stop").asDouble();
        return build(m, base, "A2", base.get("stop_rule").asText(), "sell_limit", "buying_zone", zone, zone, stop, target, sym);
    }

    private static ObjectNode build(ObjectMapper m, ObjectNode base, String path, String stopRule, String entryType, String zoneName,
                                    double zonePrice, double entryRef, double stop, double target, String sym) {
        double risk = stop - entryRef, reward = entryRef - target;
        if (!(risk > 0) || !(reward > 0)) return null;
        ObjectNode c = base.deepCopy();
        c.put("entry_path", path);
        c.put("stop_rule", stopRule);
        c.put("entry_type", entryType);
        c.put("entry_rule", "A3".equals(path) ? "next_open" : "limit_at_zone");
        c.put("entry_ref", Math.round(entryRef * 100.0) / 100.0);
        ObjectNode zone = (ObjectNode) c.get("zone");
        zone.put("name", zoneName);
        zone.put("price", Math.round(zonePrice * 100.0) / 100.0);
        zone.put("type", zoneName);
        ObjectNode math = (ObjectNode) c.get("math");
        math.put("stop", Math.round(stop * 100.0) / 100.0);
        math.put("target", Math.round(target * 100.0) / 100.0);
        double grossRR = reward / risk;
        double netRR = ExecutionMathConstants.netRR(sym, entryRef, target, stop);
        math.put("gross_rr", Math.round(grossRR * 100.0) / 100.0);
        math.put("net_rr", Math.round(netRR * 100.0) / 100.0);
        math.put("rr_sanity", grossRR >= 1.5);
        math.put("net_rr_sanity", netRR >= NetRrFloor.read());
        JsonNode n5 = base.get("stop_n5");   // stop width in N5 units scales with the new risk and entry
        if (n5 != null && n5.isNumber()) {
            double baseHigh = base.get("zone").get("price").asDouble();
            double baseRisk = base.get("math").get("stop").asDouble() - baseHigh;
            c.put("stop_n5", Math.round(n5.asDouble() * (risk / baseRisk) * (baseHigh / entryRef) * 10000.0) / 10000.0);
        }
        return c;
    }

    private static int indexOf(SpikeFadeDetector.Bars b, long t) {
        for (int i = b.n - 1; i >= 0; i--) if (b.t[i] == t) return i;
        return -1;
    }
}
