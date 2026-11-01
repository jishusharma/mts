"""Design look (SEEN window, descriptive, not a test): the operator's 2026-11-01 "first touch after the bottom" read, measured
on the 30 DOWN-high take-outs of phase1_recent.py. Shots e40e870ab33b / b98031bacd10 (CoinGlass 15m) and the TradingView WT shot:
at the touch of the level he looks for (a) RSI(14) 15m bearish divergence: price higher high than H1, RSI lower, and how many bars
apart; (b) a 15m close outside the upper Bollinger(20,2); (c) StochRSI K at the top; (d) WaveTrend (LazyBear) OB and the cross
down; (e) CVD "forces": 15m taker-delta impulses (Binance spot 1m taker buy: delta = 2 x taker_buy - volume), how many fire
after the touch, when the first up-impulse comes and where RSI sits then; (f) OI change around the touch.
Each factor is split against the single short of phase1_ladder_look.py (enter at the first 15m close back under H1, stop 1.0 %,
target L1, time 24h): did the factor pick the winners? All definitions OURS: impulse = |15m delta| > 1.5 x the std of the prior
96 bars' deltas; OB = wt1 >= 53 (phase1_recent); StochRSI top = K >= 80; outside BB = close > upper band of closes incl. the bar.
Usage: python phase1_touch_look.py <repo> <cache> [--until 2026-11-01T07:45]
"""
import importlib.util, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402
import phase1_ladder_look as LL  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
_spec = importlib.util.spec_from_file_location("chart_verify", os.path.join(REPO, "scripts", "dev", "chart_verify.py"))
CV = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(CV)

IMP_K, IMP_W, OB, STOCH_TOP, HOLD = 1.5, 96, 53, 80, 96  # OURS


def delta15(m1, T):
    """15m taker delta aligned to the 15m bars T (None where no 1m rows)."""
    acc = {}
    for r in m1:
        b = r[0] // R.P.TF * R.P.TF
        acc[b] = acc.get(b, 0.0) + (2 * r[6] - r[5])
    return [acc.get(t) for t in T]


def impulses(D):
    """+1 / -1 / 0 per bar: |delta| above IMP_K x std of the prior IMP_W deltas."""
    out = [0] * len(D)
    for i in range(IMP_W, len(D)):
        w = [d for d in D[i - IMP_W:i] if d is not None]
        if D[i] is None or len(w) < IMP_W // 2:
            continue
        m = sum(w) / len(w)
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / len(w))
        if sd and abs(D[i]) > IMP_K * sd:
            out[i] = 1 if D[i] > 0 else -1
    return out


def main():
    R._load()
    P = R.P
    m1 = __import__("json").load(open(os.path.join(P.CACHE, "btc1m_recent.json")))
    if P.UNTIL:
        m1 = [r for r in m1 if r[0] + 60000 <= P.UNTIL]
    D = delta15(m1, P.T)
    IMP = impulses(D)
    up, mid, lo = CV.bollinger(P.C)
    K, _ = CV.stochrsi(P.C)
    WT = P.wt_compute([(P.T[i], P.H[i], P.L[i], P.C[i]) for i in range(P.N)], P.TF)
    ev = [e for e in P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    rows, recs = [], []
    for e in ev:
        p, take, lvl, l1 = e["_p"], e["_take"], e["h1"], e["l1"]
        x = R.excursion(e)
        ext = take + x["exc_bars"]
        end = min(P.N - 1, take + HOLD)
        entry = next((k for k in range(take, end + 1) if P.C[k] < lvl), None)
        net, _, why = LL.book(e, "close", 1.0)
        div = P.RSI[ext] is not None and P.RSI[p] is not None and P.H[ext] > P.H[p] and P.RSI[ext] < P.RSI[p]
        bb_take = up[take] is not None and P.C[take] > up[take]
        bb_any = any(up[k] is not None and P.C[k] > up[k] for k in range(take, ext + 1))
        stoch = K[take]
        wt1, wt2 = WT[take].wt1, WT[take].wt2
        cross = next((k for k in range(take, end + 1) if WT[k].wt1 == WT[k].wt1 and WT[k].wt1 < WT[k].wt2), None)
        oi0, oi1 = P.oi_at(P.T[take - 1] + P.TF), P.oi_at(P.T[min(P.N - 1, take + 4)] + P.TF)
        doi = (oi1 / oi0 - 1) * 100 if oi0 and oi1 else None
        imp_touch = IMP[take]
        after = range(entry, end + 1) if entry is not None else range(take, end + 1)
        n_up = sum(1 for k in after if IMP[k] == 1); n_dn = sum(1 for k in after if IMP[k] == -1)
        first_up = next((k for k in after if IMP[k] == 1), None)
        recs.append(dict(e=e, net=net, why=why, div=div, apart=ext - p, bb_take=bb_take, bb_any=bb_any, stoch=stoch, wt1=wt1,
                         wt_ob=wt1 == wt1 and wt1 >= OB, cross_h=(cross - take) / 4 if cross is not None else None, doi=doi,
                         imp_touch=imp_touch, n_up=n_up, n_dn=n_dn, first_up_h=(first_up - take) / 4 if first_up is not None else None,
                         rsi_first_up=P.RSI[first_up] if first_up is not None else None, reach=x["reach"]))
        rows.append([P.utc(P.T[take]).strftime("%m-%d %H:%M"), "%.0f" % lvl, "yes %db" % (ext - p) if div else "no",
                     "yes" if bb_take else ("exc" if bb_any else "no"), P.fmt(stoch, "%.0f"), P.fmt(wt1 if wt1 == wt1 else None, "%.0f"),
                     P.fmt(recs[-1]["cross_h"]), P.fmt(doi, "%+.2f"), {1: "up", -1: "down", 0: "-"}[imp_touch],
                     "%d / %d" % (n_up, n_dn), P.fmt(recs[-1]["first_up_h"]), P.fmt(recs[-1]["rsi_first_up"], "%.0f"),
                     "%+.2f %s" % (net, why)])
    cols = ["take-out (UTC)", "H1", "RSI div vs H1", "close > BB up", "StochRSI K", "wt1", "WT cross dn (h)", "OI -1..+4 bars %",
            "CVD impulse at touch", "up / down impulses after", "first up-impulse (h)", "RSI then", "single short net, exit"]
    print("## Q5. The touch after the bottom: what the 15m chart showed at the 30 DOWN-high take-outs (design look, n=%d)\n" % len(ev))
    print(R.table(cols, rows))
    print("\nRSI div = excursion-high bar above H1 with lower RSI(14) than the H1 bar, 'Nb' = bars between the two highs; BB = close of the"
          " take-out bar above the upper band ('exc' = some bar of the excursion was); impulses counted from the single short's entry"
          " (else the take-out) to its exit; OI = Binance USDT-M sum_open_interest, close of the bar before the touch to 1h after.\n")
    facts = (("RSI div vs H1", lambda r: r["div"]), ("close > BB up at touch", lambda r: r["bb_take"]),
             ("close > BB up in excursion", lambda r: r["bb_any"]), ("StochRSI K >= 80", lambda r: None if r["stoch"] is None else r["stoch"] >= STOCH_TOP),
             ("WT OB (wt1 >= 53)", lambda r: r["wt_ob"]), ("WT cross down <= 2h", lambda r: r["cross_h"] is not None and r["cross_h"] <= 2),
             ("OI up -1..+4 bars", lambda r: None if r["doi"] is None else r["doi"] > 0), ("CVD up-impulse at touch", lambda r: r["imp_touch"] == 1),
             ("CVD up-impulse within 2h after entry", lambda r: r["first_up_h"] is not None and r["first_up_h"] <= 2))
    out = []
    for name, f in facts:
        cells = []
        for want in (True, False):
            g = [r for r in recs if f(r) is not None and f(r) == want]
            cells.append("%d: %d L1, %+.2f" % (len(g), sum(1 for r in g if r["why"] == "L1"), sum(r["net"] for r in g) / len(g)) if g else "0")
        out.append([name] + cells)
    print(R.table(["factor at the touch", "yes: n, reached L1, mean net unit-%", "no: n, reached L1, mean net unit-%"], out))
    sess = {}
    for k in range(IMP_W, P.N):
        s = P.session(P.T[k])
        sess.setdefault(s, [0, 0, 0]); sess[s][0] += 1; sess[s][1] += IMP[k] == 1; sess[s][2] += IMP[k] == -1
    print("\nCVD impulses per session over the whole window (bars, up, down, up per 24h of that session):\n")
    print(R.table(["session", "bars", "up", "down", "up per session-day"],
                  [[s, str(v[0]), str(v[1]), str(v[2]), "%.2f" % (v[1] / (v[0] / {"ASIA": 28, "LONDON": 26, "US": 26, "LATE": 16}[s]))]
                   for s, v in sess.items()]))
    bins = {"<40": 0, "40-50": 0, "50-60": 0, ">=60": 0}
    for k in range(IMP_W, P.N):
        if IMP[k] == 1 and P.RSI[k] is not None:
            r = P.RSI[k]; bins["<40" if r < 40 else "40-50" if r < 50 else "50-60" if r < 60 else ">=60"] += 1
    print("\nRSI(14) 15m at the bar of every up-impulse (operator: the next push comes near the 40 line):\n")
    print(R.table(["RSI at up-impulse", "count"], [[k, str(v)] for k, v in bins.items()]))


if __name__ == "__main__":
    main()
