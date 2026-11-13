"""Weekly red-streak bounce study. See PRE_REG.md. Usage: python study.py <datadir> <outdir>"""
import sys, os, json, pathlib
import numpy as np
sys.dont_write_bytecode = True
BT = pathlib.Path(__file__).resolve().parents[2] / "backtest"
sys.path.insert(0, str(BT))
import fees  # SOURCED constants
RT = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13   # 0.0012
BUG = os.environ.get("STUDY_BUG", "")                # test hook: 'lookahead'
VAL_START_MS = 1640995200000                          # 2022-01-01
DAY = 86400000


class Coin:
    def __init__(s, name, rows):
        a = np.array(rows, float)
        a = a[np.argsort(a[:, 0])]
        t = (a[:, 0] // DAY).astype(int)
        keep = np.ones(len(t), bool)
        if (np.diff(t) != 1).any():  # drop everything up to the last gap
            g = np.where(np.diff(t) != 1)[0][-1] + 1
            keep[:g] = False
        a, t = a[keep], t[keep]
        mon = (t + 3) % 7 == 0     # epoch day 0 = Thursday; Monday when (t+3)%7==0
        first = int(np.argmax(mon))
        a, t = a[first:], t[first:]
        nw = len(a) // 7
        a, t = a[:nw * 7], t[:nw * 7]
        s.name, s.t = name, t
        s.ms, s.o, s.h, s.l, s.c = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        s.n = len(t)
        s.wo = s.o[0::7]
        s.wc = s.c[6::7]
        s.wh = s.h.reshape(-1, 7).max(1)
        s.wl = s.l.reshape(-1, 7).min(1)
        s.nw = nw
        pc = np.r_[s.c[0], s.c[:-1]]
        tr = np.maximum(s.h - s.l, np.maximum(abs(s.h - pc), abs(s.l - pc)))
        atr = np.full(s.n, np.nan)
        if s.n > 14:
            atr[13] = tr[:14].mean()
            for i in range(14, s.n):
                atr[i] = (atr[i - 1] * 13 + tr[i]) / 14
        s.atr = atr


def events(c, kind):
    """Event = week w completed; d0 = 7*(w+1) is the Monday after."""
    red = c.wc < c.wo
    out = []
    last = -99
    run = 0
    for w in range(c.nw - 1):
        run = run + 1 if red[w] else 0
        fire, sw = False, None
        if kind.startswith("S"):
            N = int(kind[1:])
            if run == N:
                fire, sw = True, w - N + 1
        elif w >= 8:
            prior = c.wc[w - 8:w]
            if c.wc[w] <= 0.8 * prior.max():
                fire, sw = True, w - 8 + int(prior.argmax())
        if fire and w - last >= 8:
            last = w
            d0, sd = 7 * (w + 1), 7 * sw
            bull = bool(c.wc[w] > c.wc[w - 49:w + 1].mean()) if w >= 49 else None
            out.append(dict(w=w, d0=d0, sd=sd, base_low=c.l[sd:d0].min(), L=c.wh[w],
                            ref=c.wl[w], lb=d0 - sd, bull=bull))
    return out


def entry(c, ev, kind):
    """-> (entry_day, price, first_stop_check_day) or None"""
    d0 = ev["d0"]
    if kind == "E1":
        e = d0 - 1 if BUG == "lookahead" else d0
        return e, c.o[e], e
    if kind == "E2":
        swept = False
        for d in range(d0, min(d0 + 21, c.n)):
            if c.l[d] < ev["ref"]:
                swept = True
            if swept and c.c[d] > ev["ref"]:
                e = d + 1
                return (e, c.o[e], e) if e < c.n else None
        return None
    if kind == "E3":
        cd = None
        for d in range(d0, min(d0 + 28, c.n)):
            if c.c[d] > ev["L"]:
                cd = d
                break
        if cd is None:
            return None
        for d in range(cd + 1, min(cd + 11, c.n)):
            if c.l[d] <= ev["L"]:
                return d, min(c.o[d], ev["L"]), d + 1
    return None


def exit_ret(c, e, p, x, base_low, stop_from):
    """-> (net return, R or None) or None if data incomplete / invalid"""
    if x != "XS":
        xd = e + 7 * int(x[1]) - 1
        if xd >= c.n:
            return None
        return c.c[xd] / p - 1 - RT, None
    xd = e + 27
    if xd >= c.n or np.isnan(c.atr[e - 1]):
        return None
    stop = base_low - 0.5 * c.atr[e - 1]
    if p <= stop:
        return None
    risk = (p - stop) / p
    for d in range(stop_from, xd + 1):
        if c.l[d] <= stop:
            r = min(c.o[d], stop) / p - 1 - RT
            return r, r / risk
    r = c.c[xd] / p - 1 - RT
    return r, r / risk


def cluster_ci(trades, rng, nboot=10000):
    cl = {}
    for k, r in trades:
        cl.setdefault(k, []).append(r)
    ks = list(cl)
    s = np.array([sum(cl[k]) for k in ks])
    n = np.array([len(cl[k]) for k in ks], float)
    idx = rng.integers(0, len(ks), (nboot, len(ks)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return float(np.percentile(m, 2.5)), ks, s, n


def run(datadir, outdir):
    datadir, outdir = pathlib.Path(datadir), pathlib.Path(outdir)
    outdir.mkdir(exist_ok=True, parents=True)
    coins = {}
    for f in sorted(datadir.glob("*.json")):
        if f.stem.startswith("_") or f.stem == "BTC_COINBASE":
            continue
        coins[f.stem] = Coin(f.stem, json.load(open(f)))
    rng = np.random.default_rng(7)
    kinds, ents, exits = ["S4", "S5", "S6", "DD20"], ["E1", "E2", "E3"], ["X1", "X2", "X4", "XS"]
    rows = []
    for kd in kinds:
        evs = {n: events(c, kd) for n, c in coins.items()}
        for en in ents:
            tr = []
            for n, c in coins.items():
                for ev in evs[n]:
                    r = entry(c, ev, en)
                    if r:
                        tr.append((n, r[0], r[1], r[2], ev))
            for x in exits:
                obs = []
                for n, e, p, sf, ev in tr:
                    c = coins[n]
                    res = exit_ret(c, e, p, x, ev["base_low"], sf)
                    if res is None:
                        continue
                    obs.append(dict(coin=n, ms=c.ms[e], cl=(int(c.t[e]) + 3) // 7, ret=res[0], R=res[1],
                                    ev=ev, val=bool(c.ms[e] >= VAL_START_MS), bull=ev["bull"]))
                val = [o for o in obs if o["val"]]
                dev = [o for o in obs if not o["val"]]
                key = (lambda o: o["R"]) if x == "XS" else (lambda o: o["ret"])
                row = dict(event=kd, entry=en, exit=x, nDEV=len(dev), nVAL=len(val),
                           devmean=float(np.mean([key(o) for o in dev])) if dev else None, coins_val={})
                for o in val:
                    row["coins_val"][o["coin"]] = row["coins_val"].get(o["coin"], 0) + 1
                kn = [o for o in val if o["bull"] is not None]
                row["bear_share_val"] = (sum(1 for o in kn if o["bull"] is False) / len(kn)) if kn else None
                if val:
                    v = np.array([key(o) for o in val])
                    row["win"] = float(np.mean([o["ret"] > 0 for o in val]))
                    row["mean"] = float(v.mean())
                    row["mean_pct"] = float(np.mean([o["ret"] for o in val]))
                    lo, ks, s, n = cluster_ci([(o["cl"], key(o)) for o in val], rng)
                    row["ci_lo"], row["nclusters"] = lo, len(ks)
                    keep = np.argsort(-s)[3:]
                    row["ex3"] = float(s[keep].sum() / n[keep].sum()) if len(keep) else None
                    pool = []
                    for o in val:
                        c = coins[o["coin"]]
                        days = np.where(c.ms >= VAL_START_MS)[0]
                        days = days[(days + 28 < c.n) & (days > 20)]
                        vals = []
                        for e2 in rng.choice(days, 300):
                            e2 = int(e2)
                            if x == "XS":
                                bl = c.l[max(0, e2 - o["ev"]["lb"]):e2].min()
                                res = exit_ret(c, e2, c.o[e2], x, bl, e2)
                            else:
                                res = exit_ret(c, e2, c.o[e2], x, 0, e2)
                            if res is not None:
                                vals.append(res[1] if x == "XS" else res[0])
                        if vals:
                            pool.append(np.array(vals))
                    if pool:
                        m = np.zeros(5000)
                        for q in pool:
                            m += q[rng.integers(0, len(q), 5000)]
                        m /= len(pool)
                        row["placebo_mean"] = float(m.mean())
                        row["p"] = float(((m >= row["mean"]).sum() + 1) / 5001)
                rows.append(row)
    ps = [(r.get("p") if r.get("p") is not None else 1.0) for r in rows]
    order = np.argsort(ps)
    m, kmax = len(ps), 0
    for rank, i in enumerate(order, 1):
        if ps[i] <= 0.10 * rank / m:
            kmax = rank
    bh = set(order[:kmax].tolist())
    for i, r in enumerate(rows):
        r["bh"] = i in bh
        if r["nVAL"] < 30:
            r["verdict"] = "UNDERPOWERED"
        elif not (r["mean"] > 0 and r["ci_lo"] > 0):
            r["verdict"] = "FAIL: mean/CI"
        elif not (r.get("p") is not None and r["p"] < 0.05):
            r["verdict"] = "FAIL: placebo"
        elif not r["bh"]:
            r["verdict"] = "FAIL: BH"
        elif not (r["ex3"] and r["ex3"] > 0):
            r["verdict"] = "FAIL: best-3-weeks"
        else:
            r["verdict"] = "PASS"
    json.dump(rows, open(outdir / "rows.json", "w"), indent=1)
    return rows


def btc_streaks(path):
    c = Coin("BTC", json.load(open(path)))
    red = c.wc < c.wo
    spans, w = [], 0
    while w < c.nw:
        if red[w]:
            j = w
            while j + 1 < c.nw and red[j + 1]:
                j += 1
            if j - w + 1 >= 5:
                spans.append((w, j))
            w = j + 1
        else:
            w += 1
    res = []
    for a, b in spans:
        d0 = 7 * (b + 1)
        row = dict(start=int(c.ms[7 * a]), end=int(c.ms[7 * b]), n=b - a + 1, depth=float(c.wc[b] / c.wo[a] - 1),
                   low_to_close=float(c.wl[a:b + 1].min() / c.wo[a] - 1))
        for k in (1, 2, 4, 8):
            row[f"r{k}"] = float(c.wc[b + k] / c.o[d0] - 1) if b + k < c.nw else None
        ref, sw, rc = c.wl[b], False, False
        for d in range(d0, min(d0 + 21, c.n)):
            if c.l[d] < ref:
                sw = True
            if sw and c.c[d] > ref:
                rc = True
                break
        row["swept"], row["reclaim"] = sw, rc
        res.append(row)
    return res


if __name__ == "__main__":
    rows = run(sys.argv[1], sys.argv[2])
    bs = btc_streaks(pathlib.Path(sys.argv[1]) / "BTC_COINBASE.json")
    json.dump(bs, open(pathlib.Path(sys.argv[2]) / "btc_streaks.json", "w"), indent=1)
    print(len(rows), "rows;", sum(r["verdict"] == "PASS" for r in rows), "PASS")
