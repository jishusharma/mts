"""nkp3 runner. Stages: build (trades for all signals), dev (Step A + B on DEV only, writes cells_frozen.json),
val (Step C on frozen cells, refuses unless cells_frozen.json is committed), report (RESULT.md numbers are in results.json).
python run.py build|dev|val"""
import json, subprocess, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import phases as PH
import study as S

HERE = Path(__file__).resolve().parent
WORK = Path(r"F:/MTS/data_cache/mts_brains/nkp3")
COST12, COST6 = 0.0012, 0.0006
SEED = 7
MIN_N, MIN_DAYS, TOPK = 150, 40, 3
FAMILY = {"HM": "NK4 Hilega Milega flip", "BO": "Bollinger breakout", "FO": "Bollinger fakeout fade"}


def git(*a):
    return subprocess.check_output(["git", "-C", str(HERE)] + list(a), text=True).strip()


def study_files_clean():
    st = git("status", "--porcelain", "--", "PRE_REG.md", "study.py", "phases.py", "run.py", "test_study.py", "fetch_vision.py")
    return st == ""


def table():
    return PH.read_table()


# ---------------------------------------------------------------- build
def stage_build():
    WORK.mkdir(parents=True, exist_ok=True)
    tab = table()
    for k in sorted({v[1] for v in S.VARIANTS.values()}):
        t0 = time.time()
        U = S.Univ(k, tab)
        np.savez(WORK / f"univ_{k}.npz", o=U.o, h=U.h, l=U.l, c=U.c, atr=U.atr, tc=U.tc, coin=U.coin, cend=U.cend, ctx=U.ctx, phase=U.phase)
        print("univ", k, len(U.o), round(time.time() - t0), "s", flush=True)
        for v, (fam, kk, cap) in S.VARIANTS.items():
            if kk != k:
                continue
            t = S.make_trades(U, v)
            np.savez(WORK / f"trades_{v}.npz", **t)
            print("trades", v, len(t["g"]), flush=True)


def load_trades(v):
    z = np.load(WORK / f"trades_{v}.npz")
    return {k: z[k] for k in z.files}


def sub(t, m):
    return {k: v[m] for k, v in t.items()}


def net(t, cost=COST12):
    return t["g"] - cost * t["costu"]


# ---------------------------------------------------------------- Step A + B (DEV)
def dir_ok(phase, d):
    return d in PH.ALLOWED.get(int(phase), ())


def step_a(t, rng, label):
    rows = []
    x = net(t)
    for p in range(1, 7):
        row = dict(phase=PH.NAMES[p])
        for d in (1, -1):
            m = (t["phase"] == p) & (t["d"] == d)
            nm = "long" if d == 1 else "short"
            n = int(m.sum())
            row[nm + "_n"] = n
            row[nm + "_days"] = int(len(np.unique(t["day"][m]))) if n else 0
            row[nm + "_gross"] = float(t["g"][m].mean()) if n else np.nan
            row[nm + "_cost"] = float((COST12 * t["costu"][m]).mean()) if n else np.nan
            row[nm + "_net"] = float(x[m].mean()) if n else np.nan
        al = PH.ALLOWED[p]
        row["appropriate"] = "both" if len(al) == 2 else ("long" if al[0] == 1 else "short")
        a_dir = al[0]
        ma = (t["phase"] == p) & (t["d"] == a_dir)
        mo = (t["phase"] == p) & (t["d"] == -a_dir)
        if ma.sum() > 1 and mo.sum() > 1:
            diff = x[ma].mean() - x[mo].mean()
            se = np.hypot(S.cluster_se(x[ma], t["day"][ma]), S.cluster_se(x[mo], t["day"][mo]))
            row["app_minus_opp"] = float(diff)
            row["diff_se"] = float(se)
            row["diff_z"] = float(diff / se) if se > 0 else np.nan
        rows.append(row)
    return rows


def day_fracs(lo_ms, hi_ms):
    tab = table()
    dn = tab.index.values
    m = (dn * S.D1 >= lo_ms) & (dn * S.D1 < hi_ms) & (tab.label.values > 0)
    vc = pd.Series(tab.label.values[m]).value_counts()
    tot = vc.sum()
    return {PH.NAMES[p]: (int(vc.get(p, 0)), float(vc.get(p, 0) / tot)) for p in range(1, 7)}, int(tot)


def stage_dev():
    assert study_files_clean(), "study files not committed: commit PRE_REG + code before any outcome"
    head = git("rev-parse", "HEAD")
    dev_days, ndev = day_fracs(S.PH.pd.Timestamp("2019-01-01").value // 10**6, S.VAL_START)
    val_days, nval = day_fracs(S.VAL_START, 10**14)
    thin = {p for p in range(1, 7) if dev_days[PH.NAMES[p]][1] < 0.05}
    rng = np.random.default_rng(SEED)
    out = dict(code_commit=head, dev_days=dev_days, val_days=val_days, thin_phases=[PH.NAMES[p] for p in sorted(thin)], variants={})
    allcells, stepa, kept_all = [], [], []
    for v in S.VARIANTS:
        t = load_trades(v)
        d = sub(t, t["tc"] < S.VAL_START)
        sa = step_a(d, rng, "DEV")
        for r in sa:
            r["variant"] = v
        stepa += sa
        x = net(d)
        nsig = {PH.NAMES[p]: int((d["phase"] == p).sum()) for p in range(1, 7)}
        nodata = {}
        for L in (3, 4):
            nodata[S.LAYERS[L]] = bool((d["ctx"][:, L] < 3).sum() < MIN_N)
        cells = []
        for p in range(1, 7):
            for dr in PH.ALLOWED[p]:
                mp = (d["phase"] == p) & (d["d"] == dr)
                if mp.sum() < MIN_N:
                    continue
                for L in range(8):
                    for b in range(3):
                        m = mp & (d["ctx"][:, L] == b)
                        n = int(m.sum())
                        if n < MIN_N:
                            continue
                        nd = len(np.unique(d["day"][m]))
                        if nd < MIN_DAYS:
                            continue
                        st = S.day_stats(x[m], d["day"][m], rng)
                        cells.append(dict(variant=v, phase=PH.NAMES[p], phase_id=p, layer=S.LAYERS[L], layer_id=L, bucket=b, bucket_name=S.BUCKETS[S.LAYERS[L]][b],
                                          dir=dr, n=n, days=nd, gross=float(d["g"][m].mean()), cost=float((COST12 * d["costu"][m]).mean()),
                                          net=st["mean"], lo90=st["lo90"], ci_lo=st["ci_lo"], thin=p in thin))
        cells.sort(key=lambda c: -c["lo90"])
        kept, used = [], set()
        for c in cells:
            if len(kept) >= TOPK:
                break
            if c["lo90"] <= 0 or c["thin"] or nodata.get(c["layer"], False) or c["layer"] in used:
                continue
            kept.append(c)
            used.add(c["layer"])
        out["variants"][v] = dict(n_dev_signals=int(len(x)), signals_per_phase=nsig, cells_eligible=len(cells), kept=kept, no_data_layers=nodata,
                                  best_dev_cell=cells[0] if cells else None)
        allcells += cells
        kept_all += kept
        print(v, "dev signals", len(x), "eligible cells", len(cells), "kept", len(kept), flush=True)
    pd.DataFrame(stepa).to_csv(HERE / "dev_step_a.csv", index=False)
    pd.DataFrame(allcells).to_csv(HERE / "dev_cells.csv", index=False)
    (HERE / "cells_frozen.json").write_text(json.dumps(out, indent=1))
    print("kept total", len(kept_all))


# ---------------------------------------------------------------- Step C (VAL)
def placebo(U, cell, real, rng, cap, n_entries=1000):
    p, L, b, dr = cell["phase_id"], cell["layer_id"], cell["bucket"], cell["dir"]
    g = np.arange(len(U.o))
    ok = (U.tc >= S.VAL_START) & (U.phase == p) & (U.ctx[:, L] == b) & ~np.isnan(U.atr) & (U.cend - g > cap + 3)
    pool = g[ok]
    if len(pool) == 0 or len(real["hour"]) == 0:
        return None
    hours = (U.tc[pool] // S.H1) % 24
    byh = {h: pool[hours == h] for h in range(24)}
    pick = rng.integers(0, len(real["hour"]), n_entries)
    gj = np.empty(n_entries, dtype=np.int64)
    for i, r in enumerate(pick):
        cand = byh[int(real["hour"][r])]
        if len(cand) == 0:
            cand = pool
        gj[i] = cand[rng.integers(0, len(cand))]
    e = gj + 1
    d = np.full(n_entries, dr)
    Sx = np.maximum(S.STOP_ATR * U.atr[gj], S.STOP_PCT * U.o[e])
    tl = real["tlen"][pick]
    gg, _ = S.sim(U.o, U.h, U.l, e, d, Sx, tl, U.o[e])
    return gg - COST12 * U.o[e] / Sx


def maker_row(U, t, m, rng):
    """6bp row with fill model: limit at the signal bar close, filled only if the next bar trades through it; entry = limit."""
    gj, d = t["gj"][m], t["d"][m]
    e = gj + 1
    lim = U.c[gj]
    filled = np.where(d == 1, U.l[e] < lim, U.h[e] > lim)
    if filled.sum() == 0:
        return dict(n=0, fill_rate=0.0)
    gj, d, e, lim = gj[filled], d[filled], e[filled], lim[filled]
    Sx, tl = t["S"][m][filled], t["tlen"][m][filled]
    gg, _ = S.sim(U.o, U.h, U.l, e, d, Sx, tl, lim)
    x = gg - COST6 * lim / Sx
    day = t["day"][m][filled]
    st = S.day_stats(x, day, rng, boot=5000)
    st["fill_rate"] = float(filled.mean())
    st["gross"] = float(gg.mean())
    return st


def cell_mask(t, c, phase=None, d=None, ctxb=True):
    p = c["phase_id"] if phase is None else phase
    dr = c["dir"] if d is None else d
    m = (t["tc"] >= S.VAL_START) & (t["d"] == dr)
    if p != 0:
        m &= t["phase"] == p
    if ctxb:
        m &= t["ctx"][:, c["layer_id"]] == c["bucket"]
    return m


def stage_val():
    fro = HERE / "cells_frozen.json"
    assert git("status", "--porcelain", "--", "cells_frozen.json", "dev_cells.csv", "dev_step_a.csv") == "", "frozen cells not committed"
    assert git("log", "-1", "--format=%H", "--", "cells_frozen.json"), "cells_frozen.json not in git"
    froz = json.loads(fro.read_text())
    commit_cells = git("log", "-1", "--format=%H", "--", "cells_frozen.json")
    rng = np.random.default_rng(SEED + 1)
    res = dict(code_commit=froz["code_commit"], cells_commit=commit_cells, variants={}, kept=[], step_a_val=[], today={})
    tab = table()
    univ = {}
    kept_all = [(v, c) for v, vv in froz["variants"].items() for c in vv["kept"]]
    for k in sorted({S.VARIANTS[v][1] for v in S.VARIANTS}):
        z = np.load(WORK / f"univ_{k}.npz")

        class _U:
            pass
        U = _U()
        for n_ in z.files:
            setattr(U, n_, z[n_])
        univ[k] = U
    # Step A on VAL (unconditional per phase, control table)
    for v in S.VARIANTS:
        t = load_trades(v)
        vt = sub(t, t["tc"] >= S.VAL_START)
        sa = step_a(vt, rng, "VAL")
        for r in sa:
            r["variant"] = v
        res["step_a_val"] += sa
        res["variants"][v] = dict(n_val=int(len(vt["g"])), signals_per_phase={PH.NAMES[p]: int((vt["phase"] == p).sum()) for p in range(1, 7)},
                                  uncond_net=float(net(vt).mean()) if len(vt["g"]) else None, uncond_gross=float(vt["g"].mean()) if len(vt["g"]) else None)
    pvals = []
    for v, c in kept_all:
        t = load_trades(v)
        U = univ[S.VARIANTS[v][1]]
        cap = S.VARIANTS[v][2]
        m = cell_mask(t, c)
        x = net(t)[m]
        day = t["day"][m]
        st = S.day_stats(x, day, rng, boot=5000)
        g = t["g"][m]
        row = dict(variant=v, phase=c["phase"], layer=c["layer"], bucket=c["bucket_name"], dir=c["dir"], dev_net=c["net"], dev_lo90=c["lo90"], dev_n=c["n"])
        row.update(n=st["n"], days=st.get("days", 0), win=st.get("win"), gross=float(g.mean()) if len(g) else None,
                   cost=float((COST12 * t["costu"][m]).mean()) if len(g) else None, net=st.get("mean"), ci_lo=st.get("ci_lo"), ci_hi=st.get("ci_hi"),
                   ex5=st.get("ex5"), p_day=st.get("p"))
        if len(x):
            w, l = x[x > 0], -x[x <= 0]
            row["breakeven_win"] = float(l.mean() / (w.mean() + l.mean())) if len(w) and len(l) else None
        row["maker6"] = maker_row(U, t, m, rng) if m.sum() else None
        pl = placebo(U, c, dict(hour=t["hour"][m], tlen=t["tlen"][m]), rng, cap) if m.sum() else None
        if pl is not None and len(x):
            row["placebo_mean"] = float(pl.mean())
            row["real_minus_placebo"] = float(x.mean() - pl.mean())
            sd = pl.std(ddof=1)
            z = (x.mean() - pl.mean()) / (sd / np.sqrt(len(x))) if sd > 0 else np.nan
            from math import erfc, sqrt
            row["placebo_p"] = float(0.5 * erfc(z / sqrt(2))) if z == z else None
        # controls
        ctl = {}
        for nm, mm in (("opposite_dir_same_cell", cell_mask(t, c, d=-c["dir"])),
                       ("same_bucket_other_phases", cell_mask(t, c, phase=0) & (t["phase"] != c["phase_id"]) & (t["phase"] > 0)),
                       ("unconditional_same_phase_dir", cell_mask(t, c, ctxb=False)),
                       ("unconditional_rule_dir", cell_mask(t, c, phase=0, ctxb=False))):
            if mm.sum() > 1:
                xs = S.day_stats(net(t)[mm], t["day"][mm], rng, boot=1000)
                ctl[nm] = dict(n=xs["n"], net=xs["mean"], gross=float(t["g"][mm].mean()), ci_lo=xs.get("ci_lo"))
        row["controls"] = ctl
        pvals.append(row.get("p_day", 1.0))
        res["kept"].append(row)
    adj = S.bh(pvals, 0.10)
    for r, q in zip(res["kept"], adj):
        r["bh_q"] = float(q)
        ok = (r["n"] >= 150 and r["net"] is not None and r["net"] > 0 and r["ci_lo"] is not None and r["ci_lo"] > 0 and r["ex5"] is not None and r["ex5"] > 0
              and r.get("placebo_p") is not None and r["placebo_p"] < 0.05 and q < 0.10)
        r["verdict"] = "PASS" if ok else ("UNDERPOWERED" if r["n"] < 150 else "FAIL")
    res["n_kept"] = len(kept_all)
    res["n_pass"] = sum(r["verdict"] == "PASS" for r in res["kept"])
    res["n_net_pos"] = sum((r["net"] or -1) > 0 for r in res["kept"])
    # today block (descriptive)
    td = {}
    nowday = int(tab.index.max())
    td["table_tail"] = [dict(date=str(tab.loc[i, "date"]) if "date" in tab else "", label=PH.NAMES[int(tab.loc[i, "label"])], state=str(tab.loc[i, "state"]),
                             btc_close=float(tab.loc[i, "f_c"]), sma50=float(tab.loc[i, "f_sma50"]), sma200=float(tab.loc[i, "f_sma200"]), w200=float(tab.loc[i, "f_w200"]))
                        for i in tab.index[-10:]]
    td["label_today"] = PH.NAMES[int(tab.loc[nowday, "label"])]
    cur = {}
    for k, U in univ.items():
        for coin in ("BTC", "ETH"):
            ci = S.COINS.index(coin)
            idx = np.nonzero(U.coin == ci)[0]
            last = idx[-1]
            cur[f"{coin}_{k}"] = dict(tc=int(U.tc[last]), ctx=[int(z) for z in U.ctx[last]])
    td["current_ctx"] = cur
    act = []
    for r, (v, c) in zip(res["kept"], kept_all):
        k = S.VARIANTS[v][1]
        for coin in ("BTC", "ETH"):
            cc = cur[f"{coin}_{k}"]["ctx"][c["layer_id"]]
            lab = PH.NAMES[int(tab.loc[nowday, "label"])]
            act.append(dict(variant=v, cell=f"{c['phase']}/{c['layer']}={c['bucket_name']}/{'long' if c['dir']==1 else 'short'}", coin=coin,
                            phase_match=(lab == c["phase"]), bucket_now=int(cc), bucket_match=(cc == c["bucket"]), verdict=r["verdict"]))
    td["kept_cells_now"] = act
    res["today"] = td
    (HERE / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print("kept", res["n_kept"], "pass", res["n_pass"], "net>0", res["n_net_pos"])


if __name__ == "__main__":
    {"build": stage_build, "dev": stage_dev, "val": stage_val}[sys.argv[1]]()
