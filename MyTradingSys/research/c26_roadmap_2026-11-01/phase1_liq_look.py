"""Design look (SEEN window, descriptive, not a test): a liquidation-band PROXY at the 30 DOWN-high take-outs of phase1_recent.py.
Operator 2026-11-01 (shot fd1787b08c1b, CoinGlass Legend 15m with the Liquidation Heatmap): "do liquidation levels give an idea where
to short if we combine this layer? how to use these heatmaps, they develop in different timeframes". No CoinGlass history exists in
the repo (liquidation_layer_2026-10-28/README.md), so this builds the same KIND of picture the vendor's Model 1 describes (OURS):
  * every 15m bar whose Binance USDT-M open interest rose adds dOI of new positions at that bar's close, half long, half short;
  * each position would liquidate at close x (1 -/+ 1/L) for L in 10, 25, 50, 100 (equal weights), kept on a 0.1 % price grid;
  * a bucket is cleared the moment a later bar trades through it (that is why bands on the heatmap end where price went);
  * a bucket older than the window W is dropped: W is the "timeframe" of the heatmap (24h / 72h / 7d compared below).
At each take-out, looking only at bars before it: the nearest short-liquidation band above H1 (density >= the top-20 % bucket
cutoff of the standing bands within 5 % of price), its distance, whether the excursion reached it, the nearest long band under the
entry versus L1, and the single short of phase1_ladder_look.py (enter at the first close back under H1, stop 1 %, target L1, 24h)
split by those facts. A base rate over all bars says whether "a band within 0.5 %" is special at all.
Usage: python phase1_liq_look.py <repo> <cache> [--until 2026-11-01T07:45] [--window 72]
"""
import os, sys
from bisect import bisect_right

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402
import phase1_ladder_look as LL  # noqa: E402
import phase1_card as CARD  # noqa: E402

LEV = (10, 25, 50, 100)  # OURS, after CoinGlass's own "Model 1 = 10x 25x 50x 100x" statement (A_liquidation.md S1)
GRID, NEAR, TOP, HOLD = 0.001, 5.0, 0.20, 96  # OURS
WINDOW_H = 72
for i, a in enumerate(sys.argv):
    if a == "--window":
        WINDOW_H = int(sys.argv[i + 1])


def bucket(p):
    return int(round(p / 100.0))  # 100 USD buckets (OURS; about 0.1 % at 80k, GRID kept for the record)


class Heat:
    """Standing proxy bands: bucket -> list of (bar, amount) still unconsumed, for each side."""

    def __init__(self, P):
        self.P = P
        self.short = {}  # bands ABOVE price: shorts liquidate there
        self.long = {}   # bands BELOW price
        self.oi = None
        self.win = WINDOW_H * 4

    def step(self, k):
        P = self.P
        for side in (self.short, self.long):  # consume what this bar traded through
            for b in [b for b in side if P.L[k] <= b * 100.0 <= P.H[k]]:
                del side[b]
        oi = P.oi_at(P.T[k] + P.TF)
        if oi is not None and self.oi is not None and oi > self.oi:
            d = (oi - self.oi) / 2.0 / len(LEV)
            for L in LEV:
                self.short.setdefault(bucket(P.C[k] * (1 + 1.0 / L)), []).append((k, d))
                self.long.setdefault(bucket(P.C[k] * (1 - 1.0 / L)), []).append((k, d))
        if oi is not None:
            self.oi = oi
        for side in (self.short, self.long):  # drop what is older than the window
            for b in list(side):
                side[b] = [(j, d) for j, d in side[b] if k - j < self.win]
                if not side[b]:
                    del side[b]

    def bands(self, side, price):
        tot = {b: sum(d for _, d in v) for b, v in side.items() if abs(b * 100.0 / price - 1) * 100 <= NEAR}
        if not tot:
            return {}, 0.0
        vals = sorted(tot.values(), reverse=True)
        cut = vals[max(0, int(len(vals) * TOP) - 1)]
        return {b: d for b, d in tot.items() if d >= cut}, cut

    def nearest_above(self, price):
        strong, _ = self.bands(self.short, price)
        above = [b * 100.0 for b in strong if b * 100.0 > price]
        return min(above) if above else None

    def nearest_below(self, price):
        strong, _ = self.bands(self.long, price)
        below = [b * 100.0 for b in strong if b * 100.0 < price]
        return max(below) if below else None


def standing(P, heat, k):
    """The proxy's strong bands around the close of bar k (what the vendor's picture would show at the right edge)."""
    price = P.C[k]
    out = []
    for name, side in (("short bands above", heat.short), ("long bands below", heat.long)):
        strong, cut = heat.bands(side, price)
        tot = sum(strong.values()) or 1.0
        for b, d in sorted(strong.items(), key=lambda x: -x[1])[:4]:
            out.append([name, "%.0f" % (b * 100.0), "%+.2f" % ((b * 100.0 / price - 1) * 100), "%.0f %%" % (100 * d / tot)])
    print("\nStanding proxy bands at %s (close %.0f), window %dh, share of the strong bands' density:\n"
          % (P.utc(P.T[k]).strftime("%m-%d %H:%M"), price, WINDOW_H))
    print(R.table(["side", "band", "dist % from close", "share"], out))


def main():
    R._load()
    P = R.P
    if "--standing" in sys.argv:
        heat = Heat(P)
        for k in range(P.N):
            heat.step(k)
        return standing(P, heat, P.N - 1)
    ev = [e for e in P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    takes = {e["_take"]: e for e in ev}
    heat = Heat(P)
    rows, recs = [], []
    base_n = base_near = 0
    for k in range(P.N):
        if k >= 96 * 7 and k % 4 == 0:  # base rate: a strong short band within 0.5 % above the close, sampled hourly
            nb = heat.nearest_above(P.C[k])
            base_n += 1
            base_near += nb is not None and (nb / P.C[k] - 1) * 100 <= 0.5
        if k in takes:
            e = takes[k]
            lvl, l1 = e["h1"], e["l1"]
            x = R.excursion(e)
            reach = P.H[k + x["exc_bars"]] if k + x["exc_bars"] < P.N else P.H[k]
            nb = heat.nearest_above(lvl)
            d_up = (nb / lvl - 1) * 100 if nb else None
            hit = nb is not None and reach >= nb
            end = min(P.N - 1, k + HOLD)
            entry = next((j for j in range(k, end + 1) if P.C[j] < lvl), None)
            nlow = heat.nearest_below(P.C[entry] if entry is not None else lvl)
            d_dn = (1 - nlow / lvl) * 100 if nlow else None
            d_l1 = (1 - l1 / lvl) * 100
            low_after = min(P.L[j] for j in range(k, end + 1))
            hit_low = nlow is not None and low_after <= nlow
            net, _, why = LL.book(e, "close", 1.0)
            recs.append(dict(net=net, why=why, d_up=d_up, hit=hit, d_dn=d_dn, d_l1=d_l1, hit_low=hit_low,
                             overshoot=(reach / lvl - 1) * 100))
            rows.append([P.utc(P.T[k]).strftime("%m-%d %H:%M"), "%.0f" % lvl, P.fmt(nb, "%.0f"), P.fmt(d_up, "%+.2f"),
                         "%+.2f" % ((reach / lvl - 1) * 100), "yes" if hit else "no", P.fmt(nlow, "%.0f"), P.fmt(d_dn, "%.2f"),
                         "%.2f" % d_l1, "yes" if hit_low else "no", "%+.2f %s" % (net, why)])
        heat.step(k)
    cols = ["take-out (UTC)", "H1", "short band above", "dist % above H1", "excursion % above H1", "excursion reached band",
            "long band below entry", "dist % below H1", "L1 dist % below H1", "trade reached long band", "single short net, exit"]
    print("## Q7. Liquidation-band proxy at the DOWN-high take-outs (OURS Model-1-like proxy from Binance OI, window %dh; %d events"
          " on %d distinct take-out bars, same-bar duplicates collapsed)\n" % (WINDOW_H, len(ev), len(takes)))
    print(R.table(cols, rows))
    print("\nBands = standing proxy buckets (100 USD) in the top 20 %% by density within 5 %% of price, built from bars before the"
          " take-out only. Base rate: a strong short band within 0.5 %% above the close stood at %d of %d hourly samples (%.0f %%).\n"
          % (base_near, base_n, 100.0 * base_near / max(1, base_n)))
    facts = (("short band within 0.5 % above H1", lambda r: r["d_up"] is not None and r["d_up"] <= 0.5),
             ("short band within 1.0 % above H1", lambda r: r["d_up"] is not None and r["d_up"] <= 1.0),
             ("excursion reached the band", lambda r: r["hit"]),
             ("excursion stopped short of the band", lambda r: r["d_up"] is not None and not r["hit"]),
             ("long band nearer than L1", lambda r: r["d_dn"] is not None and r["d_dn"] < r["d_l1"]),
             ("trade reached the long band", lambda r: r["hit_low"]))
    out = []
    for name, f in facts:
        cells = []
        for want in (True, False):
            g = [r for r in recs if f(r) == want]
            cells.append("%d: %d L1, %+.2f, overshoot %.2f" % (len(g), sum(1 for r in g if r["why"] == "L1"),
                                                               sum(r["net"] for r in g) / len(g),
                                                               sum(r["overshoot"] for r in g) / len(g)) if g else "0")
        out.append([name] + cells)
    fcols = ["fact at the touch", "yes: n, reached L1, mean net unit-%, mean overshoot %",
             "no: n, reached L1, mean net unit-%, mean overshoot %"]
    print(R.table(fcols, out))
    if CARD.arg("--card"):
        reach = next(r for r in out if r[0] == "excursion reached the band")
        base_pct = 100.0 * base_near / max(1, base_n)
        CARD.write(CARD.arg("--card"), CARD.card(
            "c26-q7-liquidation-bands",
            "C26 Q7: a liquidation-band proxy at the DOWN-high take-outs (bands built from Binance open-interest rises, %dh window)" % WINDOW_H,
            [CARD.P("Events", "C26 held highs taken out in a DOWN phase (phase1_recent.py), 15m Binance spot BTCUSDT"),
             CARD.P("Band proxy", "a liquidation band is where leveraged entries would be liquidated: each 15m open-interest rise is spread over "
                                  "10x/25x/50x/100x liquidation prices in 100 USD buckets, decays over the window, dies when price trades through it "
                                  "(a CoinGlass-heatmap-like model; nothing from CoinGlass itself)"),
             CARD.P("Strong band", "top 20 % of bucket density within 5 % of price, from bars before the take-out only"),
             CARD.P("Outcome read", "single short: first 15m close back under H1, stop H1 + 1.0 %, target L1, 24h time stop, fee-net"),
             CARD.FEE],
            "phase1_liq_look.py <repo> <cache> --until 2026-11-01T07:45 --window %d --card <this file>; open interest from the Binance USDT-M 5m "
            "metrics files. Shot fd1787b08c1b (CoinGlass Legend 15m heatmap) is what the proxy imitates; `--standing` prints today's bands." % WINDOW_H,
            "Design look on SEEN, n=%d: excursions that reached the short band above H1: %s; that stopped short of it: %s; base rate of a strong "
            "band within 0.5 %% above price %.0f %%" % (len(ev), reach[1], reach[2], base_pct), "info",
            ["The band above H1 marks how far the take-out overshoots: when the excursion stops short of the band the single short wins, when it "
             "reaches the band it loses on average.",
             "A strong band stands close above price most of the time (base rate), so 'a band is there' is not a filter; 'the excursion reached it' is a "
             "candidate for the Phase 3b card (band consumed -> reclaim under H1 -> short, stop above the band top).",
             "OURS proxy, not the vendor's heatmap: the Binance liquidation log (Lenovo, runtime_data/liq_events) is the stable source to compare against."],
            [{"label": "take-outs", "value": str(len(ev))}, {"label": "strong band within 0.5 % above price (base rate)", "value": "%.0f %%" % base_pct},
             {"label": "excursion reached the band", "value": reach[1]}, {"label": "stopped short of the band", "value": reach[2]}],
            [CARD.table("The take-outs and the nearest bands", cols, rows, "no prices: the H1 and band columns are dropped; distances in % of H1 stay"),
             CARD.table("Each band fact split yes / no", fcols, out, "n, how many reached L1, mean fee-net unit-% of the single short, mean overshoot above H1")],
            ["phase1_liq_look.py", "PHASE1_RANGE.md", "BANDS_LEDGER.csv"]))


if __name__ == "__main__":
    main()
