package datafeed;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.time.LocalDate;

/**
 * Family A "imbalance fade", PROFILE arm (TOM_LAYER_V2_SPEC sections 2.1 A-C3, 2.2 A-P3 / A-P8, 12, 13; card
 * tom-encode-fade-profile-proofs). Runs beside the PRICE arm behind {@code -Dmts.spikeFade=true}: it takes the A1 candidate
 * of the same instant (idea A-C1, A-C2 already true), adds the volume-profile idea A-C3 as a gate and the profile proofs
 * A-P3 / A-P8, and returns a separate candidate labelled {@code arm = profile}. The PRICE candidate is never touched.
 *
 * <p>Labels. SOURCED (Tom's words, spec 2.1 / 2.2): thin top with the volume below (k0zm5NYn0IQ:21-22,
 * n7ZSkjb7JXs:78-80); P setup whose upside breakout fails and is accepted back inside (n7ZSkjb7JXs:55-59,
 * T6hDJcHrVBM:220-222); b-shaped pullback lower on a smaller timeframe (zQTbdEweG3c:144-146). RANK-DEFAULT (spec 13):
 * thirds of the leg range, top third volume below each lower third, session POC not in the top third. OURS (no number in
 * Tom's words, not tuned, not gated on outcomes): volume sits at the bar's close price; 30 histogram rows (so thirds are
 * exactly 10 rows); the POC is the first max row (lowest on ties); the leg profile uses the bars from the session start to
 * the extreme; A-P3 balance = the 10 bars before the extreme bar (same 10 as the A2 buying zone); P-shape = the leg POC in
 * the upper half of the leg range; A-P8 profile = the 1m bars after the extreme, POC in the lower half of their own range
 * (the smaller timeframe has no source number: 1m). How long price must stay inside the balance (A-P3) has NO-SOURCE:
 * {@code bars_inside} is emitted raw, no minimum.
 *
 * <p>Feed rule (spec 12, PROFILE_PARITY.md 2026-10-13): the PROFILE arm on the DAX CFD feed is NOT_IN_DATA, so no profile
 * candidate for GER40 unless {@code -Dmts.spikeFade.profileDax=true} (set only after tom-profile-shape-parity passes).
 * Missing volume is NOT_IN_DATA too: no candidate, never a false proof.
 */
final class SpikeFadeProfile {
    private SpikeFadeProfile() {}

    static final String DAX_PROPERTY = "mts.spikeFade.profileDax";
    static final int ROWS = 30;
    static final int BALANCE_BARS = 10;

    /** Thirds result of a leg profile. */
    static final class Thin {
        final double bottom, mid, top;
        final int pocRow, pocThird;
        final boolean thin;

        Thin(double bottom, double mid, double top, int pocRow, int pocThird) {
            this.bottom = bottom;
            this.mid = mid;
            this.top = top;
            this.pocRow = pocRow;
            this.pocThird = pocThird;
            this.thin = top < bottom && top < mid && pocThird != 2;
        }
    }

    private static int row(double lo, double hi, double px) {
        int r = (int) Math.floor((px - lo) / (hi - lo) * ROWS);
        return Math.max(0, Math.min(ROWS - 1, r));
    }

    private static double[] rows(double lo, double hi, double[] px, double[] vol) {
        double[] v = new double[ROWS];
        for (int i = 0; i < px.length; i++) v[row(lo, hi, px[i])] += vol[i];
        return v;
    }

    private static int pocRow(double[] v) {
        int p = 0;
        for (int i = 1; i < v.length; i++) if (v[i] > v[p]) p = i;
        return p;
    }

    /** A-C3: volume by thirds of [lo, hi] and the thin test of spec 13. */
    static Thin thin(double lo, double hi, double[] px, double[] vol) {
        double[] v = rows(lo, hi, px, vol);
        double[] t = new double[3];
        for (int i = 0; i < ROWS; i++) t[i / (ROWS / 3)] += v[i];
        int poc = pocRow(v);
        return new Thin(t[0], t[1], t[2], poc, poc / (ROWS / 3));
    }

    /** @return the profile-arm candidate built from the A1 candidate, or null (arm not applicable / NOT_IN_DATA / not thin). */
    static ObjectNode build(ObjectMapper mapper, ObjectNode a1, SpikeFadeDetector.Bars b, String sym) {
        if ("GER40".equals(sym) && !Boolean.getBoolean(DAX_PROPERTY)) return null;
        if (b.n < 2) return null;
        int last = b.n - 1;
        LocalDate today = b.date[last];
        long zoneMs = a1.path("zone_time_ms").asLong(-1);
        int hIdx = -1, winFirst = -1;
        for (int i = 0; i < b.n; i++) {
            if (!b.date[i].equals(today) || !b.inWindow(i)) continue;
            if (winFirst < 0) winFirst = i;
            if (b.t[i] == zoneMs) hIdx = i;
        }
        if (winFirst < 0 || hIdx < 0) return null;
        for (int i = winFirst; i <= last; i++) if (!(b.v[i] >= 0)) return null;   // NaN or negative volume: NOT_IN_DATA
        double lo = b.o[winFirst], hi = a1.path("zone").path("price").asDouble();
        if (!(hi > lo)) return null;

        // A-C3: profile of the leg (session start to the extreme), volume at the close price
        int n = hIdx - winFirst + 1;
        double[] px = new double[n], vol = new double[n];
        for (int i = 0; i < n; i++) {
            px[i] = b.c[winFirst + i];
            vol[i] = b.v[winFirst + i];
        }
        Thin th = thin(lo, hi, px, vol);
        if (!th.thin) return null;   // the PROFILE arm idea requires A-C3
        double[] legRows = rows(lo, hi, px, vol);
        double legPocFrac = (th.pocRow + 0.5) / ROWS;

        ObjectNode c = a1.deepCopy();
        c.put("arm", "profile");
        ObjectNode items = c.putObject("profile_items");
        ObjectNode c3 = items.putObject("A-C3");
        c3.put("thin", true);
        c3.put("top", th.top);
        c3.put("mid", th.mid);
        c3.put("bottom", th.bottom);
        c3.put("poc_third", th.pocThird);
        c3.put("poc_price", Math.round((lo + (th.pocRow + 0.5) * (hi - lo) / ROWS) * 100.0) / 100.0);
        c3.put("rows", ROWS);

        // A-P3: P-shaped leg, upside breakout fails, price back inside the balance (raw measures; no minimum acceptance)
        ObjectNode p3 = items.putObject("A-P3");
        int balFrom = Math.max(winFirst, hIdx - BALANCE_BARS);
        boolean p3ok = false;
        if (balFrom < hIdx) {
            double balHigh = Double.NEGATIVE_INFINITY, balLow = Double.POSITIVE_INFINITY;
            for (int i = balFrom; i < hIdx; i++) {
                balHigh = Math.max(balHigh, b.h[i]);
                balLow = Math.min(balLow, b.l[i]);
            }
            boolean pShape = legPocFrac >= 0.5;
            boolean brokeOut = hi > balHigh;
            boolean backInside = b.c[last] <= balHigh && b.c[last] >= balLow;
            int inside = 0;
            for (int i = hIdx + 1; i <= last; i++) if (b.c[i] <= balHigh && b.c[i] >= balLow) inside++;
            p3.put("p_shape", pShape);
            p3.put("broke_out", brokeOut);
            p3.put("back_inside", backInside);
            p3.put("bars_inside", inside);
            p3.put("leg_poc_frac", Math.round(legPocFrac * 10000.0) / 10000.0);
            p3.put("balance_high", balHigh);
            p3.put("balance_low", balLow);
            p3ok = pShape && brokeOut && backInside;
        } else {
            p3.put("p_shape", false);
            p3.put("broke_out", false);
            p3.put("back_inside", false);
            p3.put("bars_inside", 0);
        }

        // A-P8: b-shaped profile of the bars after the extreme (POC in the lower half of their own range)
        ObjectNode p8 = items.putObject("A-P8");
        boolean p8ok = false;
        int m = last - hIdx;
        if (m >= 2) {
            double sLo = Double.POSITIVE_INFINITY, sHi = Double.NEGATIVE_INFINITY;
            double[] spx = new double[m], svol = new double[m];
            for (int i = 0; i < m; i++) {
                int j = hIdx + 1 + i;
                sLo = Math.min(sLo, b.l[j]);
                sHi = Math.max(sHi, b.h[j]);
                spx[i] = b.c[j];
                svol[i] = b.v[j];
            }
            if (sHi > sLo) {
                double f = (pocRow(rows(sLo, sHi, spx, svol)) + 0.5) / ROWS;
                p8.put("poc_frac", Math.round(f * 10000.0) / 10000.0);
                p8.put("bars", m);
                p8ok = f < 0.5;
            }
        }
        p8.put("b_shape", p8ok);

        ArrayNode cond = (ArrayNode) c.get("conditions");
        cond.add("A-C3");
        ArrayNode pr = (ArrayNode) c.get("proofs");
        if (p3ok) pr.add("A-P3");
        if (p8ok) pr.add("A-P8");
        c.put("proof_count", pr.size());
        ((ObjectNode) c.get("score")).put("proof_count", pr.size());
        ArrayNode nid = (ArrayNode) c.get("not_in_data");
        ArrayNode kept = mapper.createArrayNode();
        for (JsonNode x : nid) {
            String s = x.asText();
            if (!s.equals("A-C3") && !s.equals("A-P3") && !s.equals("A-P8")) kept.add(s);
        }
        c.set("not_in_data", kept);
        return c;
    }
}
