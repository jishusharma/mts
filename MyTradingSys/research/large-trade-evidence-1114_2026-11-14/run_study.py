"""Run the pre-registered tests (PRE_REG.md). Writes results.json and tables.md next to this file (aggregates only).
Usage: python -I run_study.py [--only public|our] """
import glob, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(next(q for q in HERE.parents if (q / "MyTradingSys").is_dir())))
import lib as L  # noqa: E402

DATA = "F:/MTS/data_cache/large_trades/large-trade-evidence-1114"
DAILY = "F:/MTS/data_cache/btc_anatomy/BTCUSDT_1d.csv"
WS = {"15m": 1, "1h": 4, "4h": 16}      # trailing windows in 15m buckets
HS = (1, 4, 24)
GROUPS = ["all", "UP", "DOWN", "RANGE", "B0", "B1", "B2", "B3", "DOWN&B2+3"]
BOOT = L.Boot(B=20000, seed=1114)


def load_public():
    fs = sorted(glob.glob(f"{DATA}/bars1m/*.csv.gz"))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True).drop_duplicates("t").sort_values("t").reset_index(drop=True)
    for T in ("250k", "500k", "1M", "5M"):
        d["ld" + T] = d["bu" + T] - d["se" + T]
    return d


def load_our():
    d = pd.read_csv(f"{DATA}/our_orderflow_1m_cols.csv.gz")
    d["ldb999"] = (d.b999_buy_vol - d.b999_sell_vol) * d.c
    d["ldb99"] = (d.b99_buy_vol - d.b99_sell_vol) * d.c
    return d


def build(df, ld_cols, label):
    """Hourly decision table + arrays on the 15m grid."""
    G = L.to_grid15(df, ld_cols)
    hi = L.hour_idx(G)
    ho, hh, hl, hc = L.hourly_bars(G, hi)
    atr = L.atr_sma(hh, hl, hc, 14)
    t = L.tdec(G, hi)
    day = (t // L.DAY).astype(np.int64)
    ph = L.phase_table(pd.read_csv(DAILY, usecols=["t", "o", "h", "l", "c"]))
    phase = ph["phase"].reindex(day).fillna("NA").values
    ddb = ph["ddb"].reindex(day).values
    S = dict(label=label, G=G, hi=hi, ho=ho, hh=hh, hl=hl, hc=hc, atr=atr, t=t, day=day, phase=phase, ddb=ddb,
             era=np.where(t < L.ERA_B_START, "A", "B"), ld={}, z={}, ret={})
    for k in ld_cols:
        for w, nb in WS.items():
            x = L.trailing(G[k], hi, nb)
            S["ld"][(k, w)] = x
            S["z"][(k, w)] = L.zscore_hourly(x)
    for h in HS:
        S["ret"][h] = L.fwd_ret(G, hi, h)
    S["ph"] = ph
    return S


def masks(S):
    p, d = S["phase"], S["ddb"]
    m = {"all": p != "NA", "UP": p == "UP", "DOWN": p == "DOWN", "RANGE": p == "RANGE"}
    for b in range(4):
        m[f"B{b}"] = (d == b) & (p != "NA")
    m["DOWN&B2+3"] = (p == "DOWN") & (d >= 2)
    return m


def clusters(S, h):
    return S["day"] if h <= 4 else S["day"] // 3


def test1(S, Ts):
    M = masks(S)
    rows = []
    for T in Ts:
        for w in WS:
            z = S["z"][(T, w)]
            for h in HS:
                r = S["ret"][h]
                cl = clusters(S, h)
                for g in GROUPS:
                    m = M[g] & ~np.isnan(z) & ~np.isnan(r)
                    zz, rr, cc = z[m], r[m], cl[m]
                    res = L.corr_cluster(zz, rr, cc, BOOT)
                    row = dict(src=S["label"], T=T, W=w, H=h, group=g, **res)
                    if res["n"] >= 100:
                        q = np.quantile(zz, [0.2, 0.4, 0.6, 0.8])
                        qb = np.searchsorted(q, zz, side="right")
                        row["q_mean_bp"] = [float(rr[qb == i].mean() * 1e4) for i in range(5)]
                        sp = L.diff_cluster(rr * 1e4, qb == 4, qb == 0, cc, BOOT)
                        row.update(spread_bp=sp["d"], spread_lo=sp["lo"], spread_hi=sp["hi"], spread_p=sp["p"])
                        for era in ("A", "B"):
                            me = m & (S["era"] == era)
                            ce = L.corr_cluster(z[me], r[me], cl[me], L.Boot(B=2000, seed=7)) if me.sum() > 100 else dict(ic=np.nan, K=0, n=int(me.sum()))
                            row[f"ic_{era}"] = ce["ic"]; row[f"K_{era}"] = ce["K"]
                    rows.append(row)
    return rows


def primary1(rows, T, lab):
    prim = [r for r in rows if r["T"] == T and r["group"] in ("UP", "DOWN", "RANGE") and ((r["W"], r["H"]) in (("1h", 4), ("4h", 24)))]
    ok = L.holm([r["p"] for r in prim])
    for r, o in zip(prim, ok):
        r["holm_pass"] = o
        r["pass"] = bool(o and r["ic_A"] * r["ic"] > 0 and r["ic_B"] * r["ic"] > 0 and r["K_A"] >= 60 and r["K_B"] >= 60)
    return prim


def test2(S, T):
    """Absorption at 24h extremes. Returns event rows (per hour index) and summary cells."""
    hl, hh, ho, hc, hi = S["hl"], S["hh"], S["ho"], S["hc"], S["hi"]
    n = len(hl)
    z = S["z"][(T, "1h")]
    lowev = np.zeros(n, bool); highev = np.zeros(n, bool)
    for k in range(24, n):
        a = hl[k - 24:k]; b = hh[k - 24:k]
        if np.isnan(a).any() or np.isnan(hl[k]):
            continue
        lowev[k] = hl[k] < a.min(); highev[k] = hh[k] > b.max()
    ret1 = hc / ho - 1
    absl = lowev & (ret1 < 0) & (z >= 1)
    absh = highev & (ret1 > 0) & (z <= -1)
    ft = np.full(n, np.nan)
    ev = np.nonzero(lowev | highev)[0]
    ft[ev] = L.first_touch(S["G"], hi[ev], S["atr"][ev])
    cells = []
    M = masks(S)
    for side, evm, absm in (("low", lowev, absl), ("high", highev, absh)):
        rev = (ft == 1) if side == "low" else (ft == -1)
        cont = (ft == -1) if side == "low" else (ft == 1)
        revf = np.where(np.isnan(ft), np.nan, rev.astype(float)); contf = np.where(np.isnan(ft), np.nan, cont.astype(float))
        sg = 1 if side == "low" else -1   # reversal return sign: long after lows, short after highs
        for g in GROUPS:
            a = absm & M[g]; b_ = evm & ~absm & M[g]
            cl = S["day"]
            row = dict(src=S["label"], side=side, group=g, n_abs=int(a.sum()), n_rest=int(b_.sum()))
            for nm, v in (("rev_first", revf), ("cont_first", contf)):
                d = L.diff_cluster(v, a, b_, cl, BOOT)
                row[nm] = d
            for h in (4, 24):
                v = sg * S["ret"][h] * 1e4
                row[f"rev_ret{h}_bp"] = L.diff_cluster(v, a, b_, cl if h == 4 else S["day"] // 3, BOOT)
            for era in ("A", "B"):
                row["d_rev_" + era] = L.diff_cluster(revf, a & (S["era"] == era), b_ & (S["era"] == era), cl, L.Boot(B=2000, seed=7))
            cells.append(row)
    return cells, dict(lowev=lowev, highev=highev, absl=absl, absh=absh, ft=ft)


def primary2(cells):
    prim = [r for r in cells if r["group"] in ("UP", "DOWN", "RANGE")]
    ok = L.holm([r["rev_first"]["p"] for r in prim])
    for r, o in zip(prim, ok):
        d = r["rev_first"]["d"]
        r["holm_pass"] = o
        r["pass"] = bool(o and r["d_rev_A"]["d"] * d > 0 and r["d_rev_B"]["d"] * d > 0 and r["d_rev_A"]["K"] >= 60 and r["d_rev_B"]["K"] >= 60)
    return prim


def test3(S, T):
    G, hi = S["G"], S["hi"]
    ld = S["ld"][(T, "1h")]
    bull, bear = L.divergence_flags(S["hl"], S["hh"], ld)
    out = []
    M = masks(S)
    for side, flags in ((+1, bull), (-1, bear)):
        net, ex, sp = L.simulate_entries(G, hi, S["atr"], side)
        entry = hi + 1
        k_all = np.nonzero(flags & ~np.isnan(net))[0]
        keep = k_all[L.one_at_a_time(entry[k_all], ex[k_all])] if len(k_all) else np.array([], int)
        for g in GROUPS:
            gm = M[g]
            kk = keep[gm[keep]] if len(keep) else keep
            row = dict(src=S["label"], T=T, side="long" if side > 0 else "short", group=g, n=int(len(kk)))
            if len(kk) >= 5:
                v = net[kk] * 1e4
                mc = L.mean_cluster(v, S["day"][kk], BOOT)
                pool = net[gm & ~np.isnan(net)]
                pp, pm = L.placebo_p(pool, len(kk), net[kk].mean())
                row.update(mean_bp=mc["mean"], lo=mc["lo"], hi=mc["hi"], win=float((net[kk] > 0).mean()),
                           meanR=float((net[kk] / sp[kk]).mean()), placebo_p=pp, placebo_mean_bp=pm * 1e4,
                           pool_mean_bp=float(pool.mean() * 1e4), pool_n=int(len(pool)))
                for era in ("A", "B"):
                    ke = kk[S["era"][kk] == era]
                    row[f"mean_{era}_bp"] = float(net[ke].mean() * 1e4) if len(ke) else np.nan
                    row[f"n_{era}"] = int(len(ke))
            out.append(row)
        S.setdefault("trades", {})[side] = dict(keep=keep, net=net, sp=sp)
    return out


def primary3(rows):
    prim = [r for r in rows if r["group"] in ("UP", "DOWN", "RANGE")]
    ok = L.holm([r.get("placebo_p", np.nan) for r in prim])
    for r, o in zip(prim, ok):
        r["holm_pass"] = o
        r["pass"] = bool(o and r.get("mean_bp", -1) > 0 and r.get("mean_A_bp", -1) > 0 and r.get("mean_B_bp", -1) > 0 and r["n"] >= 60)
    return prim


def coverage_public(d):
    d = d.copy(); d["yr"] = pd.to_datetime(d.t, unit="ms").dt.year
    g = d.groupby("yr").agg(minutes=("t", "size"), first=("t", "min"), last=("t", "max"), **{f"prints_{k}": (f"nb{k}", "sum") for k in ("250k", "500k", "1M", "5M")},
                             **{f"sells_{k}": (f"ns{k}", "sum") for k in ("250k", "500k", "1M", "5M")})
    g["first"] = pd.to_datetime(g["first"], unit="ms").dt.strftime("%Y-%m-%d"); g["last"] = pd.to_datetime(g["last"], unit="ms").dt.strftime("%Y-%m-%d")
    return g


def coverage_our(d):
    d = d.copy(); d["yr"] = pd.to_datetime(d.t, unit="ms").dt.year
    g = d.groupby("yr").agg(minutes=("t", "size"), first=("t", "min"), last=("t", "max"), b99_buy_n=("b99_buy_n", "sum"), b99_sell_n=("b99_sell_n", "sum"),
                             b999_buy_n=("b999_buy_n", "sum"), b999_sell_n=("b999_sell_n", "sum"), thr99_med=("thr99", "median"), thr999_med=("thr999", "median"))
    g["first"] = pd.to_datetime(g["first"], unit="ms").dt.strftime("%Y-%m-%d"); g["last"] = pd.to_datetime(g["last"], unit="ms").dt.strftime("%Y-%m-%d")
    return g


def phase_mix(S, mask=None):
    p = S["phase"] if mask is None else S["phase"][mask]
    s = pd.Series(p)
    # days not hours
    dd = pd.DataFrame({"day": S["day"] if mask is None else S["day"][mask], "phase": p}).drop_duplicates("day")
    return dd.phase.value_counts().to_dict()


def snapshot(S, T="ld1M"):
    """Descriptive: the last 50 days of daily large-trade delta and the latest hours, with percentile vs same-phase history."""
    G = S["G"]
    df = pd.DataFrame({"t": G["t0"] + np.arange(G["n"]) * L.M15, "c": G["c"], "h": G["h"], "l": G["l"], "o": G["o"], "ld1M": G[T], })
    return df


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    R = {}
    t0 = time.time()
    if only != "our":
        pub = load_public()
        R["coverage_public"] = coverage_public(pub).reset_index().to_dict("records")
        S = build(pub, ["ld1M", "ld5M"], "PUBLIC")
        print("built public", time.time() - t0, flush=True)
        R["phase_mix_days_public"] = phase_mix(S)
        R["phase_mix_days_public_eraA"] = phase_mix(S, S["era"] == "A")
        R["phase_mix_days_public_eraB"] = phase_mix(S, S["era"] == "B")
        r1 = test1(S, ["ld1M", "ld5M"])
        print("test1", time.time() - t0, flush=True)
        R["test1"] = r1
        R["test1_primary"] = primary1(r1, "ld1M", "PUBLIC")
        c2, ev = test2(S, "ld1M")
        R["test2"] = c2; R["test2_primary"] = primary2(c2)
        print("test2", time.time() - t0, flush=True)
        r3 = test3(S, "ld1M") + test3(S, "ld5M")
        R["test3"] = r3; R["test3_primary"] = primary3([r for r in r3 if r["T"] == "ld1M"])
        print("test3", time.time() - t0, flush=True)
        # recent snapshot data (aggregated)
        np.savez_compressed(f"{DATA}/public_hourly_state.npz", t=S["t"], phase=S["phase"].astype(str), ddb=np.nan_to_num(S["ddb"], nan=-1), z1m_1h=S["z"][("ld1M", "1h")],
                            z1m_4h=S["z"][("ld1M", "4h")], ld1m_1h=S["ld"][("ld1M", "1h")], ld1m_4h=S["ld"][("ld1M", "4h")], ld5m_4h=S["ld"][("ld5M", "4h")],
                            c=S["hc"], h=S["hh"], l=S["hl"], lowev=ev["lowev"], absl=ev["absl"], highev=ev["highev"], absh=ev["absh"], ft=ev["ft"])
        S_pub = S
    if only != "public":
        our = load_our()
        R["coverage_our"] = coverage_our(our).reset_index().to_dict("records")
        So = build(our, ["ldb999", "ldb99"], "OUR")
        R["phase_mix_days_our"] = phase_mix(So)
        r1 = test1(So, ["ldb999", "ldb99"])
        R["test1_our"] = r1
        R["test1_our_primary"] = [r for r in r1 if r["T"] == "ldb999" and r["group"] in ("UP", "DOWN", "RANGE") and ((r["W"], r["H"]) in (("1h", 4), ("4h", 24)))]
        c2, _ = test2(So, "ldb999")
        R["test2_our"] = c2
        r3 = test3(So, "ldb999") + test3(So, "ldb99")
        R["test3_our"] = r3
        if only != "our":
            # data check: hourly net-delta correlation, PUBLIC 1M vs OUR b999 (1h window), overlap only
            a = pd.Series(S_pub["ld"][("ld1M", "1h")], index=S_pub["t"]); b = pd.Series(So["ld"][("ldb999", "1h")], index=So["t"])
            j = pd.concat([a, b], axis=1, keys=["pub", "our"]).dropna()
            R["data_check"] = dict(n=int(len(j)), corr=float(j.corr().iloc[0, 1]), rank_corr=float(j.corr(method="spearman").iloc[0, 1]))
            tail = our[our.t >= L.ERA_B_START]
    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return o
    suffix = {"public": "_public", "our": "_our"}.get(only, "")
    Path(HERE / f"results{suffix}.json").write_text(json.dumps(clean(R), indent=1))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
