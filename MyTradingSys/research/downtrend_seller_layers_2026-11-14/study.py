"""Shorts at stacked seller layers in DOWN phase. See PRE_REG.md (written before any outcome).
python -I study.py <npz_dir> <out_json>
"""
import sys
import os
import json
import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import fees  # noqa: E402

LAG = int(os.environ.get("E9_LAG", "1"))      # 1 = levels from days strictly before today. 0 = deliberately WRONG (test only)
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT"]
DAY = 86_400_000
HOUR = 3_600_000
BARS_DAY = 96
COST_SIDE = fees.BINANCE_TAKER + fees.BINANCE_TAKER / 5
COST_RT = 2 * COST_SIDE
BIN_VA, BIN_LVN = 0.0005, 0.0025
CLUSTER = 0.002
STOP_PAD = 0.001
HOLD = 48
SPLIT_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
N_BOOT, N_PLC = 5000, 2000
EXITS = ["E1", "E2", "E3"]


def load(npz_dir, sym, now_ms=None):
    a = np.load(Path(npz_dir) / f"{sym}_15m.npz")["a"]
    now_ms = now_ms or int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    a = a[a[:, 0] + 900_000 <= now_ms]                  # closed bars only
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]


def profile(h, l, c, v, bin_frac):
    """HLC3 volume profile. Returns dict poc, vah, val, lvn (price levels)."""
    px = (h + l + c) / 3.0
    b = bin_frac * float(c.mean())
    lo0 = float(px.min())
    idx = np.floor((px - lo0) / b).astype(int)
    vol = np.bincount(idx, weights=v)
    poc = int(np.argmax(vol))
    lo = hi = poc
    acc, tot = vol[poc], vol.sum()
    while acc < 0.70 * tot and (lo > 0 or hi < len(vol) - 1):
        up = vol[hi + 1] if hi + 1 < len(vol) else -1.0
        dn = vol[lo - 1] if lo - 1 >= 0 else -1.0
        if up >= dn:
            hi += 1; acc += up
        else:
            lo -= 1; acc += dn
    out = dict(poc=lo0 + (poc + 0.5) * b, vah=lo0 + (hi + 1) * b, val=lo0 + lo * b, lvn=float("nan"))
    if hi - lo >= 2:
        inner = np.arange(lo + 1, hi)
        mid = (lo + hi) / 2.0
        order = sorted(inner, key=lambda i: (vol[i], abs(i - mid)))
        out["lvn"] = lo0 + (order[0] + 0.5) * b
    return out


class Coin:
    def __init__(self, npz_dir, sym, now_ms=None):
        self.sym = sym
        self.t, self.o, self.h, self.l, self.c, self.v = load(npz_dir, sym, now_ms)
        self.n = len(self.t)
        self.dn = self.t // DAY
        days, first, cnt = np.unique(self.dn, return_index=True, return_counts=True)
        self.dfirst = {int(d): int(f) for d, f, k in zip(days, first, cnt) if k == BARS_DAY}
        self.days = sorted(self.dfirst)
        self.dclose = {d: self.c[self.dfirst[d] + BARS_DAY - 1] for d in self.days}
        self._daily_phase()
        self._rsi1h()

    def sl(self, d):
        f = self.dfirst[d]
        return slice(f, f + BARS_DAY)

    def _daily_phase(self):
        ds = pd.Series({d: self.dclose[d] for d in self.days})
        full = ds.reindex(range(self.days[0], self.days[-1] + 1))
        sma = full.rolling(20).mean()
        self.down = {}
        for d in range(self.days[0] + 26, self.days[-1] + 2):    # trade day d uses closes through d-1
            c1, s1, s6 = full.get(d - 1), sma.get(d - 1), sma.get(d - 6)
            if any(x is None or np.isnan(x) for x in (c1, s1, s6)):
                continue
            self.down[d] = bool(c1 < s1 and s1 < s6)
        self.sma200 = full.rolling(200).mean()
        self.fullclose = full

    def _rsi1h(self):
        hr = self.t // HOUR
        df = pd.DataFrame({"hr": hr, "c": self.c, "t": self.t})
        g = df.groupby("hr").agg(c=("c", "last"), n=("c", "size"))
        g = g.reindex(range(int(g.index.min()), int(g.index.max()) + 1))
        close = g["c"].where(g["n"] == 4)
        close = close.ffill()
        d = close.diff()
        up, dnn = d.clip(lower=0), (-d).clip(lower=0)
        au = up.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        ad = dnn.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        rsi = 100 - 100 / (1 + au / ad.replace(0, np.nan))
        self.rsi = rsi

    def rsi_at(self, t_ms):
        """RSI of the last CLOSED 1h bar before the 15m bar starting at t_ms (bar of hour H uses hour H-1)."""
        return self.rsi.get(int(t_ms // HOUR) - 1, np.nan)

    def levels_for(self, d, lag=None):
        """Seller levels for trade day d from days before d (lag=1). lag=0 is the deliberately wrong version."""
        lag = LAG if lag is None else lag
        p1 = d - lag                       # 'prior day'
        need = [p1, p1 - 1, p1 - 2]
        if any(x not in self.dfirst for x in need):
            return None
        s1 = self.sl(p1)
        pr = profile(self.h[s1], self.l[s1], self.c[s1], self.v[s1], BIN_VA)
        a, b = self.sl(p1 - 2).start, s1.stop
        p3 = profile(self.h[a:b], self.l[a:b], self.c[a:b], self.v[a:b], BIN_LVN)
        return dict(L1=pr["vah"], L2=pr["poc"], L3=float(self.h[s1].max()), L4=p3["lvn"], PDL=float(self.l[s1].min()))


def signals(cn):
    """Candidate signal bars: list of (j, dayno, k, flags[L1..L5], pdl)."""
    out = []
    lvl_cache = {}
    for d in cn.days:
        lv = cn.levels_for(d)
        if lv is None:
            continue
        lvl_cache[d] = lv
    for d, lv in lvl_cache.items():
        f = cn.dfirst[d]
        P = np.array([lv["L1"], lv["L2"], lv["L3"], lv["L4"]])
        o, h, c = cn.o[f:f + BARS_DAY], cn.h[f:f + BARS_DAY], cn.c[f:f + BARS_DAY]
        for i in range(BARS_DAY):
            ok = ~np.isnan(P)
            tch = ok & (o[i] < P) & (h[i] >= P) & (c[i] < P)
            if not tch.any():
                continue
            R = P[tch].max()
            inc = ok & (np.abs(P - R) <= CLUSTER * R)
            rsi = cn.rsi_at(cn.t[f + i])
            l5 = bool(rsi >= 60) if not np.isnan(rsi) else False
            fl = list(inc) + [l5]
            out.append((f + i, d, int(inc.sum()) + int(l5), fl, lv["PDL"]))
    out.sort(key=lambda x: x[0])
    return out


def run_exit(cn, sigs, ex, down_only):
    trades = []
    free_after = -1
    for j, d, k, fl, pdl in sigs:
        if down_only and not cn.down.get(d, False):
            continue
        if j <= free_after or j + HOLD >= cn.n:
            continue
        e0 = j + 1
        entry = cn.o[e0]
        stop = cn.h[j] * (1 + STOP_PAD)
        if entry >= stop:
            continue
        risk = (stop - entry) / entry
        if ex == "E1":
            tgt = entry * (1 - risk)
        elif ex == "E2":
            tgt = entry * (1 - 2 * risk)
        else:
            if (entry - pdl) / entry < 3 * COST_RT:
                continue
            tgt = pdl
        H, L = cn.h[e0:e0 + HOLD], cn.l[e0:e0 + HOLD]
        hs, ht = H > stop, L <= tgt
        i_s = int(np.argmax(hs)) if hs.any() else 10 ** 9
        i_t = int(np.argmax(ht)) if ht.any() else 10 ** 9
        if i_s <= i_t and i_s < 10 ** 9:
            ex_px, hold = stop, i_s + 1
        elif i_t < 10 ** 9:
            ex_px, hold = tgt, i_t + 1
        else:
            ex_px, hold = cn.c[e0 + HOLD - 1], HOLD
        free_after = e0 + hold - 1
        g = -(ex_px - entry) / entry
        trades.append(dict(coin=cn.sym, j=j, e0=e0, t=int(cn.t[j]), day=int(d), hour=int((cn.t[e0] // HOUR) % 24), hold=hold,
                           k=k, fl=[bool(x) for x in fl], risk=risk, rg=g / risk, rn=(g - COST_RT) / risk,
                           down=bool(cn.down.get(d, False))))
    return trades


def boot_cluster(days, R, rng):
    ud, inv = np.unique(days, return_inverse=True)
    S = np.bincount(inv, weights=R)
    N = np.bincount(inv).astype(float)
    D = len(ud)
    cnt = rng.multinomial(D, np.ones(D) / D, size=N_BOOT)
    m = (cnt @ S) / (cnt @ N)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())


def boot_trade(R, rng):
    idx = rng.integers(0, len(R), size=(N_BOOT, len(R)))
    m = R[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def bh(p, q=0.10):
    p = np.asarray(p, float)
    order = np.argsort(p)
    m = len(p)
    thr = -1
    for rank, i in enumerate(order, 1):
        if p[i] <= q * rank / m:
            thr = rank
    keep = np.zeros(m, bool)
    for rank, i in enumerate(order, 1):
        if rank <= thr:
            keep[i] = True
    return keep


def main(npz_dir, out_json):
    rng = np.random.default_rng(20261114)
    coins = {s: Coin(npz_dir, s) for s in COINS if (Path(npz_dir) / f"{s}_15m.npz").exists()}
    cov = {s: [dt.datetime.fromtimestamp(c.t[0] / 1000, dt.timezone.utc).strftime("%Y-%m-%d"), c.n] for s, c in coins.items()}
    sigs = {s: signals(c) for s, c in coins.items()}
    nsig = {s: len(v) for s, v in sigs.items()}
    T = {}   # (ex, set) -> trades
    for ex in EXITS:
        for name, dn in (("down", True), ("all", False)):
            T[(ex, name)] = [t for s, c in coins.items() for t in run_exit(c, sigs[s], ex, dn)]
    # placebo candidate pools: per coin, per hour, VAL DOWN-day 15m bars
    pool = {}
    for s, c in coins.items():
        dnb = np.array([c.down.get(int(d), False) for d in c.dn])
        valb = c.t >= SPLIT_MS
        hr = ((c.t // HOUR) % 24)
        for hh in range(24):
            pool[(s, hh)] = np.where(dnb & valb & (hr == hh))[0]

    def placebo_R(trs, dist_cache={}):
        """For each trade candidate net-return vectors (before / risk)."""
        cands = []
        for t in trs:
            c = coins[t["coin"]]
            ix = pool[(t["coin"], t["hour"])]
            ix = ix[ix + t["hold"] - 1 < c.n]
            r = (-(c.c[ix + t["hold"] - 1] - c.o[ix]) / c.o[ix] - COST_RT) / t["risk"]
            cands.append(r)
        return cands

    rows_def = [("ALL", lambda t: True), ("K1", lambda t: t["k"] == 1), ("K2", lambda t: t["k"] == 2), ("K3+", lambda t: t["k"] >= 3),
                ("L1 VAH", lambda t: t["fl"][0]), ("L2 POC", lambda t: t["fl"][1]), ("L3 PDH", lambda t: t["fl"][2]),
                ("L4 LVN", lambda t: t["fl"][3]), ("L5 RSI>=60", lambda t: t["fl"][4])]
    res = []
    for ex in EXITS:
        for rname, fn in rows_def:
            r = dict(row=rname, ex=ex)
            for setn in ("down", "all"):
                trs = [t for t in T[(ex, setn)] if fn(t)]
                dev = [t for t in trs if t["t"] < SPLIT_MS]
                val = [t for t in trs if t["t"] >= SPLIT_MS]
                r[setn] = dict(n_dev=len(dev), n_val=len(val))
                if dev:
                    Rd = np.array([t["rn"] for t in dev]); r[setn]["dev_mean"] = float(Rd.mean()); r[setn]["dev_win"] = float((Rd > 0).mean())
                if len(val) >= 2:
                    R = np.array([t["rn"] for t in val]); Rg = np.array([t["rg"] for t in val]); days = np.array([t["day"] for t in val])
                    lo_t, hi_t = boot_trade(R, rng)
                    lo_c, hi_c, p_c = boot_cluster(days, R, rng)
                    ud = np.unique(days)
                    sums = {d: R[days == d].sum() for d in ud}
                    best5 = set(sorted(sums, key=sums.get, reverse=True)[:5])
                    keep = np.array([d not in best5 for d in days])
                    r[setn].update(mean=float(R.mean()), gross=float(Rg.mean()), win=float((R > 0).mean()), ci_trade=[lo_t, hi_t],
                                   ci_day=[lo_c, hi_c], p_day=p_c, days=int(len(ud)),
                                   no_best5=float(R[keep].mean()) if keep.any() else float("nan"))
                    if setn == "down":
                        cands = placebo_R(val)
                        if all(len(x) for x in cands):
                            lens = np.array([len(x) for x in cands]); offs = np.concatenate([[0], np.cumsum(lens)[:-1]])
                            flat = np.concatenate(cands)
                            u = rng.random((N_PLC, len(cands)))
                            pick = offs + (u * lens).astype(int)
                            pm = flat[pick].mean(axis=1)
                            r[setn]["placebo_mean"] = float(pm.mean()); r[setn]["placebo_p"] = float((pm >= R.mean()).mean())
            res.append(r)
    ps = [r["down"].get("p_day", 1.0) if r["down"].get("n_val", 0) >= 100 else 1.0 for r in res]
    keep = bh(ps)
    for r, kp in zip(res, keep):
        d = r["down"]
        ok = ("mean" in d and d["mean"] > 0 and d["ci_trade"][0] > 0 and d["ci_day"][0] > 0 and d["n_val"] >= 100
              and d.get("placebo_p", 1) < 0.05 and kp and d["no_best5"] > 0)
        d["bh"] = bool(kp)
        if ok:
            r["verdict"] = "PASS"
        elif d.get("n_val", 0) < 100 and d.get("mean", -1) > 0:
            r["verdict"] = "UNDERPOWERED"
        else:
            r["verdict"] = "FAIL"
    # regime mix
    btc = coins["BTCUSDT"]
    reg = {"DEV": {"bull": 0, "bear": 0, "range": 0, "na": 0}, "VAL": {"bull": 0, "bear": 0, "range": 0, "na": 0}}
    for d in btc.days:
        c, m = btc.dclose[d], btc.sma200.get(d)
        sp = "VAL" if d * DAY >= SPLIT_MS else "DEV"
        if m is None or np.isnan(m):
            reg[sp]["na"] += 1
        else:
            reg[sp]["bull" if c > m * 1.05 else "bear" if c < m * 0.95 else "range"] += 1
    btc_down = {sp: [sum(1 for d, v in btc.down.items() if v and ((d * DAY >= SPLIT_MS) == (sp == "VAL"))),
                     sum(1 for d in btc.down if ((d * DAY >= SPLIT_MS) == (sp == "VAL")))] for sp in ("DEV", "VAL")}
    allsig_down = {sp: [sum(1 for t in T[("E2", "all")] if t["down"] and ((t["t"] >= SPLIT_MS) == (sp == "VAL"))),
                        sum(1 for t in T[("E2", "all")] if ((t["t"] >= SPLIT_MS) == (sp == "VAL")))] for sp in ("DEV", "VAL")}
    # BTC levels today
    lv = {}
    for dstr in ("2026-11-13", "2026-11-14"):
        d = int(dt.datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() // 86400)
        lv[dstr] = dict(levels=btc.levels_for(d, 1), down=btc.down.get(d))
    lv["last_close"] = float(btc.c[-1]); lv["last_bar_utc"] = dt.datetime.fromtimestamp(btc.t[-1] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    lv["rsi1h_last"] = float(btc.rsi_at(btc.t[-1]))
    json.dump(dict(rows=res, coverage=cov, n_signal_bars=nsig, regime_btc=reg, btc_down_days=btc_down, down_share_signals=allsig_down,
                   btc_levels=lv, lag=LAG, n_trades={f"{k[0]}-{k[1]}": len(v) for k, v in T.items()}), open(out_json, "w"), indent=1, default=float)
    print("done", out_json)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
