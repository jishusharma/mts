"""Derives the archive-mode patch of MarketDataSnapshot.java.new (staged, never the live original).
Writes src/main/java/datafeed/MarketDataSnapshot.java.archive_mode.new (gitignored *.new).
Changes vs MarketDataSnapshot.java.new (fetchSnapshot = live path ends up identical to the committed original):
  0. The staged .new wired the 3 range calls (yesterday/prevWeek/twoWeek) in the LIVE fetchSnapshot instead of
     fetchHistoricalSnapshot. Revert the live ones to client.klinesRange, wire the historical ones + dropFormingBar.
  1. archive mode: spot_perp_basis and oi_breakdown are NOT fetched from live REST (look-ahead, F7); a neutral
     node with "source":"unavailable" is emitted instead.
  2. trade_flow.net_delta_{1m,5m,15m,1h} and conditions.cvd_trade_flow_aligned are derived from the 1m klines with
     the exact live formula (2*takerBuyBase - volume) instead of hard-coded 0.0/false (L1_ADAPTER_REVIEW item 5).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "src" / "main" / "java" / "datafeed"
NL = chr(10)


def _once(t, old, new, last=False):
    i = t.rfind(old) if last else t.find(old)
    assert i >= 0 and (last or t.count(old) == 1), old
    return t[:i] + new + t[i + len(old):]


def _rewire(t):
    L = t.split(NL)
    for name, endvar in (("yesterday", "yesterdayEndUtc"), ("prevWeek", "prevWeekSunday"), ("twoWeek", "twoWeekSunday")):
        key = "JsonNode %sKlines = " % name
        idx = [i for i, l in enumerate(L) if key in l]
        assert len(idx) == 2, (name, idx)
        i0, i1 = idx
        assert "historicalSource(symbol).klines(" in L[i0] and "client.klinesRange(symbol, " in L[i1]
        L[i0] = L[i0].replace("historicalSource(symbol).klines(", "client.klinesRange(symbol, ")
        j = next(k for k in range(i0, i1) if L[k].strip().startswith("dropFormingBar(%sKlines" % name))
        del L[j]
        i1 -= 1
        L[i1] = L[i1].replace("client.klinesRange(symbol, ", "historicalSource(symbol).klines(")
        e = next(k for k in range(i1, i1 + 6) if L[k].rstrip().endswith(");"))
        L.insert(e + 1, "        dropFormingBar(%sKlines, %s.toInstant().toEpochMilli());" % (name, endvar))
    return NL.join(L)


def patch(txt):
    t = _rewire(txt)
    t = _once(t, "        ObjectNode spotPerpBasis = buildSpotPerpBasis(symbol);",
              "        ObjectNode spotPerpBasis = archiveRawRoot != null ? unavailableNode() : buildSpotPerpBasis(symbol);", last=True)
    t = _once(t, '        root.set("oi_breakdown", buildOiBreakdown(symbol));',
              '        root.set("oi_breakdown", archiveRawRoot != null ? unavailableNode() : buildOiBreakdown(symbol));', last=True)
    t = _once(t, "        // ── Conditions (minimal, live-only proofs set defaults) ──",
"""        // ── Trade flow from 1m klines (same formula as fetchSnapshot; no live data, no look-ahead) ──
        double nd1m = 0, nd5m = 0, nd15m = 0, nd1h = 0;
        {
            int _n = klines1m.size();
            for (int i = Math.max(0, _n - 60); i < _n; i++) {
                JsonNode bar = klines1m.get(i);
                double barDelta = 2 * bar.get(9).asDouble() - bar.get(5).asDouble();
                if (i >= _n - 1) nd1m += barDelta;
                if (i >= _n - 5) nd5m += barDelta;
                if (i >= _n - 15) nd15m += barDelta;
                if (i >= _n - 60) nd1h += barDelta;
            }
        }
        // ── Conditions (minimal, live-only proofs set defaults) ──""")
    t = _once(t, '        cond.put("cvd_trade_flow_aligned", false); // live-only, set false',
"""        String cvdSlope1h = cvdNode.get("cvd_recent").get("slope_1h").asText();
        cond.put("cvd_trade_flow_aligned", !"flat".equals(cvdSlope1h)
                && (("rising".equals(cvdSlope1h) && nd1m > 0) || ("falling".equals(cvdSlope1h) && nd1m < 0)));""")
    for k, v in (("net_delta_1m", "nd1m"), ("net_delta_5m", "nd5m"), ("net_delta_15m", "nd15m"), ("net_delta_1h", "nd1h")):
        t = _once(t, '        tradeFlow.put("%s", 0.0);' % k,
                  '        tradeFlow.put("%s", Math.round(%s * 1000.0) / 1000.0);' % (k, v))
    t = _once(t, '        tradeFlow.put("confidence", "LOW");', '        tradeFlow.put("confidence", "HIGH");')
    t = _once(t, "    private ObjectNode buildSpotPerpBasis(String symbol) {",
"""    /** Archive mode: no raw source for this block yet; neutral values, explicitly labelled (never live REST). */
    private ObjectNode unavailableNode() {
        ObjectNode node = mapper.createObjectNode();
        node.put("source", "unavailable");
        node.put("basis_pct", 0.0);
        node.put("direction", "unknown");
        node.put("confidence", "LOW");
        node.putObject("retail").put("long_short_ratio", 0.0).put("change_1h", 0.0).put("change_4h", 0.0);
        node.putObject("whale").put("long_short_ratio", 0.0).put("change_1h", 0.0).put("change_4h", 0.0);
        node.putObject("topAccounts").put("long_short_ratio", 0.0).put("change_1h", 0.0).put("change_4h", 0.0);
        return node;
    }

    private ObjectNode buildSpotPerpBasis(String symbol) {""")
    return t


def main():
    src = (D / "MarketDataSnapshot.java.new").read_text(encoding="utf-8")
    out = D / "MarketDataSnapshot.java.archive_mode.new"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(patch(src))
    print("wrote", out)


if __name__ == "__main__":
    main()
