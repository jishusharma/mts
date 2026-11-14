"""Independent recomputation of dated DEV trades from raw 15m bars (plain Python loops, shares NO code with study.py; formulas from FORMULAS.md and PRE_REG.md).
    python verify_trades.py <n_trades>   -> picks trades at fixed positions of dev_trades.csv (primary sample) and prints expected vs study values.
Study-run helper only (reads the F: drive cache); not a committed test."""
import csv, sys, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = Path(r"F:\MTS\data_cache\binance\t1-markdown-rally-rejection")
PH = Path(r"F:\MTS\data_cache\mts_brains\phase_daily.csv")


def ms(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def recompute(coin, t_utc):
    z = np.load(CACHE / f"{coin}USDT_15m.npz")
    T = [int(x) for x in z["t"]]; O, H, L, C, V = (z[k].tolist() for k in "ohlcv")
    idx = {t: k for k, t in enumerate(T)}
    HR = 3600000; DAY = 86400000
    t0 = ms(t_utc)                                    # signal 1h bar open time
    def bar(t, n):                                    # aggregate n 15m bars from t
        ks = [idx[t + 900000 * q] for q in range(n)]
        return (O[ks[0]], max(H[k] for k in ks), min(L[k] for k in ks), C[ks[-1]], sum(V[k] for k in ks))
    # pivots from the prior complete UTC day
    d0 = (t0 // DAY - 1) * DAY
    ks = [idx[d0 + 900000 * q] for q in range(96)]
    hi, lo, cl = max(H[k] for k in ks), min(L[k] for k in ks), C[ks[-1]]
    P = (hi + lo + cl) / 3; R1 = 2 * P - lo; S1 = 2 * P - hi
    o, h, l, c, _ = bar(t0, 4)
    lvl = "R1" if (h > R1 and c < R1) else ("P" if (h > P and c < P) else None)
    # HM on 30m: RSI(9) Wilder, EMA3, WMA21 of the RSI, at the 30m bar that opens t0+30m
    c30, t30 = [], []
    tt = t0 - 400 * HR
    while tt <= t0 + HR // 2:
        if all((tt + 900000 * q) in idx for q in range(2)):
            c30.append(C[idx[tt + 900000]]); t30.append(tt)
        tt += HR // 2
    rs = [None] * len(c30)
    dl = [c30[i] - c30[i - 1] for i in range(1, len(c30))]
    ag = sum(max(x, 0) for x in dl[:9]) / 9; al = sum(max(-x, 0) for x in dl[:9]) / 9
    rs[9] = 100 - 100 / (1 + ag / al)
    for i in range(10, len(c30)):
        ag = (ag * 8 + max(dl[i - 1], 0)) / 9; al = (al * 8 + max(-dl[i - 1], 0)) / 9
        rs[i] = 100 - 100 / (1 + ag / al)
    r = rs[9:]
    e = [sum(r[:3]) / 3]
    for x in r[3:]:
        e.append(e[-1] + (x - e[-1]) * 0.5)
    ema3 = e[-1]
    wma21 = sum((k + 1) * r[len(r) - 21 + k] for k in range(21)) / 231
    hm = wma21 > r[-1] and wma21 > ema3
    # VWAP anchored 00:00 UTC through the signal bar close
    num = den = 0.0
    q = (t0 // DAY) * DAY
    while q < t0 + HR:
        if q in idx:
            k = idx[q]; tp = (H[k] + L[k] + C[k]) / 3; num += tp * V[k]; den += V[k]
        q += 900000
    vw = num / den
    # ATR14 on 1h (plain SMA of TR over the 14 bars ending at the signal bar)
    trs = []
    for m in range(14):
        tb = t0 - m * HR
        _, hh, ll, _, _ = bar(tb, 4); pc = bar(tb - HR, 4)[3]
        trs.append(max(hh - ll, abs(hh - pc), abs(ll - pc)))
    atr = sum(trs) / 14
    entry = bar(t0 + HR, 4)[0]
    D = max(h - entry, atr, 0.012 * entry)
    stop = entry + D
    tgt = P if lvl == "R1" else S1
    out = dict(level=lvl, P=P, S1=S1, hm_sell=hm, below_vwap=c < vw, entry=entry, D=D, target=tgt, skip=(tgt >= entry or entry - tgt < 0.5 * D))
    exitp, why = None, "time"
    for m in range(1, 25):                             # bars after the signal bar: 1 .. 24
        bo, bh, bl, bc, _ = bar(t0 + m * HR, 4)
        if bh >= stop:
            exitp, why = max(stop, bo), "stop"; break
        if bl <= tgt:
            exitp, why = tgt, "target"; break
    if exitp is None:
        exitp = bc
    out.update(exit=why, gross=(entry - exitp) / D, cost=0.0012 * entry / D)
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = [r for r in csv.DictReader(open(HERE / "dev_trades.csv")) if r["sample"] == "primary"]
    pick = [rows[int(len(rows) * (k + 0.5) / n)] for k in range(n)]
    ok = True
    for r in pick:
        x = recompute(r["coin"], r["t_utc"])
        same = (abs(x["gross"] - float(r["gross_R"])) < 1e-3 and abs(x["cost"] - float(r["cost_R_12bp"])) < 1e-3 and x["exit"] == r["exit"] and x["hm_sell"] and x["below_vwap"]
                and not x["skip"] and x["level"] == ("R1" if r["level"] == "R1" else "P"))
        ok &= same
        print(f"{r['coin']} {r['t_utc']} phase {r['phase']}: study gross {r['gross_R']} cost {r['cost_R_12bp']} exit {r['exit']} | independent {x} | {'MATCH' if same else 'MISMATCH'}")
    print("ALL MATCH" if ok else "MISMATCH PRESENT")
