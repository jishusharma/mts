"""Descriptive context sheet for 2026-10-14..16 from the live mirror on disk. No returns, no outcome stats.
Run: python MyTradingSys/research/confluence_read_2026-10-17/context_sheet.py  (prints markdown tables)."""
import csv, os, datetime as dt, statistics as st

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "runtime_data", "_mirror", "MyTradingSys", "runtime")
OF = "orderflow_live/2026-10-16.csv"
OI5 = "oi_live/oi_5m_30d.csv"
OI1 = "oi_live/oi_1m.csv"
RAYS = (81800.0, 82459.8, 82900.5)


BAD_OI5 = []


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


def load_of():
    with open(os.path.join(ROOT, OF), newline="") as fh:
        return [dict(t=int(r["t"]), o=float(r["o"]), h=float(r["h"]), l=float(r["l"]), c=float(r["c"]),
                     bv=float(r["buy_vol"]), sv=float(r["sell_vol"]), d=float(r["delta"]), cvd=float(r["cvd_day"]))
                for r in csv.DictReader(fh)]


def load_oi5():
    out = []
    with open(os.path.join(ROOT, OI5), newline="") as fh:
        for r in csv.reader(fh):
            oi, notional = float(r[3]), float(r[4])
            if notional <= 0:  # bad row (zero notional): counted and dropped, see BAD_OI5
                BAD_OI5.append(int(r[0]))
                continue
            out.append(dict(t=int(r[0]), oi=oi, px=notional / oi))  # px = implied price (notional / OI), a proxy
    return out


def load_oi1():
    with open(os.path.join(ROOT, OI1), newline="") as fh:
        return [(int(r["ts_ms"]), float(r["openInterest"])) for r in csv.DictReader(fh)]


def day(ms):
    return utc(ms).strftime("%Y-%m-%d")


def main():
    of, oi5, oi1 = load_of(), load_oi5(), load_oi1()
    print("## A. 10-16 1m tape (%s)" % OF)
    print("bars=%d first=%s last=%s" % (len(of), utc(of[0]["t"]).strftime("%H:%M"), utc(of[-1]["t"]).strftime("%H:%M")))
    hi = max(of, key=lambda b: b["h"]); lo = min(of, key=lambda b: b["l"])
    print("O=%.1f H=%.1f (%s) L=%.1f (%s) C=%.1f range=%.1f cvd_day_end=%.1f" % (
        of[0]["o"], hi["h"], utc(hi["t"]).strftime("%H:%M"), lo["l"], utc(lo["t"]).strftime("%H:%M"), of[-1]["c"], hi["h"] - lo["l"], of[-1]["cvd"]))
    vmax = max(of, key=lambda b: b["bv"] + b["sv"])
    print("max-volume 1m bar %s vol=%.1f BTC wick H=%.1f L=%.1f delta=%.1f" % (
        utc(vmax["t"]).strftime("%H:%M"), vmax["bv"] + vmax["sv"], vmax["h"], vmax["l"], vmax["d"]))
    for r in RAYS:
        first = next((b for b in of if b["h"] >= r), None)
        print("ray %.1f: first 1m high >= ray %s" % (r, utc(first["t"]).strftime("%H:%M") if first else "never on 10-16"))
    print("\n| hour UTC | open | close | range | delta sum | cvd end | price dir vs delta |\n|---|---|---|---|---|---|---|")
    diverge = 0
    for h in range(24):
        bs = [b for b in of if utc(b["t"]).hour == h]
        if not bs:
            continue
        o, c = bs[0]["o"], bs[-1]["c"]
        dsum = sum(b["d"] for b in bs)
        rng = max(b["h"] for b in bs) - min(b["l"] for b in bs)
        dv = (c - o) * dsum < 0
        diverge += dv
        print("| %02d | %.1f | %.1f | %.1f | %.0f | %.0f | %s |" % (h, o, c, rng, dsum, bs[-1]["cvd"], "OPPOSED" if dv else "same"))
    print("hours with price change and delta of opposite sign: %d of 24 (descriptive, one day)" % diverge)
    rph = [max(b["h"] for b in bs) - min(b["l"] for b in bs) for h in range(24) for bs in [[b for b in of if utc(b["t"]).hour == h]] if bs]
    print("range per hour: median=%.1f max=%.1f" % (st.median(rph), max(rph)))

    print("\n## B. OI 5m, 30d (%s); px = notional / OI, an implied-price PROXY" % OI5)
    days = {}
    for r in oi5:
        days.setdefault(day(r["t"]), []).append(r)
    print("rows=%d first=%s last=%s days=%d" % (len(oi5), utc(oi5[0]["t"]).strftime("%m-%d %H:%M"), utc(oi5[-1]["t"]).strftime("%m-%d %H:%M"), len(days)))
    print("| day | rows | px open | px high | px low | px close | px range | OI open | OI close | OI chg % | px range per hour of rows |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for d in sorted(days):
        rs = days[d]
        pxs = [r["px"] for r in rs]
        print("| %s | %d | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.2f | %.0f |" % (
            d, len(rs), pxs[0], max(pxs), min(pxs), pxs[-1], max(pxs) - min(pxs), rs[0]["oi"], rs[-1]["oi"],
            (rs[-1]["oi"] / rs[0]["oi"] - 1) * 100, (max(pxs) - min(pxs)) / max(1, len(rs) / 12)))
    print("\n| window ending 10-16 | days | px high | px low | px range | px drift (first-day first row to last-day last row) | OI chg % |\n|---|---|---|---|---|---|---|")
    ds = sorted(days)
    i16 = ds.index("2026-10-16")
    for n in (2, 3, 5, 10, 14):
        w = ds[max(0, i16 - n + 1):i16 + 1]
        rs = [r for d in w for r in days[d]]
        pxs = [r["px"] for r in rs]
        first_close = days[w[0]][-1]
        print("| last %d | %d | %.0f | %.0f | %.0f | %+.0f | %+.2f |" % (
            n, len(w), max(pxs), min(pxs), max(pxs) - min(pxs), days[w[-1]][-1]["px"] - days[w[0]][0]["px"],
            (days[w[-1]][-1]["oi"] / days[w[0]][0]["oi"] - 1) * 100))
    print("\n## C. OI 1m poll on 10-16 (%s)" % OI1)
    d16 = [(t, v) for t, v in oi1 if day(t) == "2026-10-16"]
    print("rows=%d of 1440 expected" % len(d16))
    if d16:
        print("OI first=%.0f last=%.0f max=%.0f min=%.0f" % (d16[0][1], d16[-1][1], max(v for _, v in d16), min(v for _, v in d16)))
        if vmax:
            near = [(t, v) for t, v in d16 if abs(t - vmax["t"]) <= 180000]
            print("OI polls within 3 min of the max-volume bar: " + ", ".join("%s %.0f" % (utc(t).strftime("%H:%M:%S"), v) for t, v in near))


main()
