"""edge2_capitulation_long_2026-11 runner (PRE_REG.md frozen first). Outputs cells.csv + stdout tables."""
import csv, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core2  # noqa: E402
from MyTradingSys.backtest.bigtrade.bigmoves import atr as atr_fn  # noqa: E402

REPO = core2.REPO
D1 = REPO.parent / "mts-jis-nb-edge-extreme-confirm-template-1113" / "runtime_data" / "edge-extreme-confirm-template-1113"
D2 = REPO / "runtime_data" / "edge2-capitulation-long-1113"
OLD = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
NEW = json.load(open(D2 / "coins.json"))
H1, DAY, WEEK = 3600000, 86400000, 7 * 86400000
DEV_END, VAL_END = 1719792000000, 1751328000000
B, SEED, NPLC = 2000, 1113, 500
SPL = ("DEV", "VALIDATION", "RECENT")
EXITS = {"1h": {"24h": 24, "3d": 72}, "4h": {"24h": 6, "3d": 18}}


def split_arr(tc):
    return np.where(tc < DEV_END, 0, np.where(tc < VAL_END, 1, 2))


def load(coin, tf):
    d = D1 if coin in OLD else D2
    k = np.array(json.load(open(d / (coin + "_1h.json"))))
    f = np.array(json.load(open(d / (coin + "_fund.json"))))
    t = k[:, 0].astype(np.int64)
    if tf == "4h":
        g = t // (4 * H1)
        u, idx, cnt = np.unique(g, return_index=True, return_counts=True)
        rows = []
        for i, c_ in zip(idx, cnt):
            if c_ == 4 and (t[i:i + 4] == t[i] + np.arange(4) * H1).all():
                b = k[i:i + 4]
                rows.append([b[0, 0], b[0, 1], b[:, 2].max(), b[:, 3].min(), b[3, 4]])
        k = np.array(rows)
        t = k[:, 0].astype(np.int64)
    o, h, l, c = k[:, 1], k[:, 2], k[:, 3], k[:, 4]
    a = np.array([np.nan if x is None else float(x) for x in atr_fn(list(h), list(l), list(c))])
    ft = f[:, 0].astype(np.int64)
    cs = np.concatenate([[0.0], np.cumsum(f[:, 1])])
    return t, o, h, l, c, a, ft, cs


def month_key(tc):
    return tc.astype("datetime64[ms]").astype("datetime64[M]").astype(int)


def coin_data(coin, tf, hold):
    t, o, h, l, c, a, ft, cs = load(coin, tf)
    bar = H1 if tf == "1h" else 4 * H1
    ret, xj = core2.fwd_trades(t, o, l, c, a, hold, bar, ft, cs)
    n = len(c)
    cap = core2.capitulation(h, l, c, a)
    conf = np.zeros(n, bool)
    conf[:-1] = c[1:] > c[:-1]
    trig = np.where(cap & conf & np.isfinite(ret))[0]
    tc = t + bar  # setup close time
    spl = split_arr(tc)
    mk = month_key(tc)
    free, sel = -1, []
    for i in trig:
        if i + 1 <= free:
            continue
        free = xj[i]
        sel.append(i)
    sel = np.array(sel, int)
    pool = np.where(np.isfinite(ret))[0]
    return dict(coin=coin, ret=ret, spl=spl, mk=mk, sel=sel, pool=pool, wk=(t + bar) // WEEK, t=t, n=n)


def boot(wk, r, rng):
    if len(r) == 0:
        return [np.nan] * 4
    u, inv = np.unique(wk, return_inverse=True)
    sm = np.bincount(inv, weights=r)
    ct = np.bincount(inv).astype(float)
    idx = rng.integers(0, len(u), size=(B, len(u)))
    bm = sm[idx].sum(1) / ct[idx].sum(1)
    return [float(r.mean()), float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5)), (1 + float((bm <= 0).sum())) / (B + 1)]


def placebo(cds, sp, rng):
    """Same coin, same calendar month, same count of random long entries (any bar), same mechanics; 500 draws."""
    tot = 0
    sums = np.zeros(NPLC)
    for d in cds:
        s = d["sel"][d["spl"][d["sel"]] == sp]
        if len(s) == 0:
            continue
        tot += len(s)
        pidx = d["pool"][d["spl"][d["pool"]] == sp]
        if len(pidx) == 0:
            return np.nan, np.nan
        keys, cnt = np.unique(d["mk"][s], return_counts=True)
        for kk, m in zip(keys, cnt):
            pm = pidx[d["mk"][pidx] == kk]
            if len(pm) == 0:
                pm = pidx
            sums += rng.choice(d["ret"][pm], size=(NPLC, m), replace=True).sum(1)
    if tot == 0:
        return np.nan, np.nan
    pm_ = sums / tot
    return float(pm_.mean()), float(np.percentile(pm_, 95))


def stats(cds, rng):
    row = {}
    for si, sp in enumerate(SPL):
        r = np.concatenate([d["ret"][d["sel"][d["spl"][d["sel"]] == si]] for d in cds])
        wk = np.concatenate([d["wk"][d["sel"][d["spl"][d["sel"]] == si]] for d in cds])
        mean, lo, hi, p = boot(wk, r, rng)
        pm, p95 = placebo(cds, si, rng)
        row.update({sp + "_n": len(r), sp + "_mean": mean, sp + "_lo": lo, sp + "_hi": hi, sp + "_p": p,
                    sp + "_plc_mean": pm, sp + "_plc_p95": p95})
    return row


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    cache = {}
    groups = [("1h", "NEW20", NEW, True), ("4h", "OLD10", OLD, True), ("4h", "NEW20", NEW, True),
              ("1h", "ALL30", OLD + NEW, False), ("4h", "ALL30", OLD + NEW, False), ("1h", "OLD10", OLD, False)]
    for tf, gname, coins, tested in groups:
        for ex, hold in EXITS[tf].items():
            cds = []
            for cn in coins:
                key = (cn, tf, hold)
                if key not in cache:
                    cache[key] = coin_data(cn, tf, hold)
                cds.append(cache[key])
            row = dict(tf=tf, group=gname, exit=ex, tested=tested, ncoins=len(coins))
            row.update(stats(cds, rng))
            rows.append(row)
            print(tf, gname, ex, "VALn", row["VALIDATION_n"], "RECn", row["RECENT_n"], flush=True)
    tr = [r for r in rows if r["tested"]]
    ps = sorted((r["VALIDATION_p"] if r["VALIDATION_n"] >= 30 else 9.0, i) for i, r in enumerate(tr))
    cut = 0
    for rank, (p, i) in enumerate(ps, 1):
        if p <= 0.10 * rank / len(tr):
            cut = rank
    bh = {i for rank, (p, i) in enumerate(ps, 1) if rank <= cut}
    for i, r in enumerate(tr):
        r["BH"] = i in bh
        r["passV"] = bool(r["VALIDATION_n"] >= 30 and r["VALIDATION_mean"] > 0 and r["VALIDATION_lo"] > 0
                          and r["VALIDATION_mean"] > r["VALIDATION_plc_p95"] and r["BH"])
        r["passVR"] = bool(r["passV"] and r["RECENT_n"] >= 30 and r["RECENT_mean"] > 0 and r["RECENT_lo"] > 0)
    for r in rows:
        r.setdefault("BH", ""); r.setdefault("passV", ""); r.setdefault("passVR", "")
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        s = "%s %s %s %s |" % ("T" if r["tested"] else "d", r["tf"], r["group"], r["exit"])
        for sp in SPL:
            s += " %s n%d %+.2f%% [%+.2f,%+.2f] plc %+.2f/%+.2f |" % (sp[:3], r[sp + "_n"], 100 * r[sp + "_mean"], 100 * r[sp + "_lo"],
                                                                     100 * r[sp + "_hi"], 100 * r[sp + "_plc_mean"], 100 * r[sp + "_plc_p95"])
        print(s, "BH", r["BH"], "passV", r["passV"], "passVR", r["passVR"])


if __name__ == "__main__":
    main()
