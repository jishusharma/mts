"""nkp4 runner. Stage `dev` (signals < 2024-01-01 only; writes dev_cells.csv, dev_stepA.json, cells_frozen.json).
Stage `val` (refuses unless cells_frozen.json is committed and the study code is unchanged since the commit it names).
Usage: python nkp4_run.py dev | python nkp4_run.py val"""
import sys, json, subprocess, time, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd
import nkp4_phases as PH, nkp4_study as ST, nkp4_stats as SS

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = PH.ROOT / "mts_brains" / "nkp4"
MIN_N, MIN_DAYS, TOP_K, DAYFLOOR = 150, 40, 3, 0.05
FEE_TAKER, FEE_MAKER = 12.0, 6.0
SEED = 20261114


def git(*a):
    return subprocess.check_output(["git", "-C", str(REPO), *a], text=True).strip()


def table_for(built, cid, lo_ts, hi_ts):
    out = {}; D = built["D"]
    for (rn, dirn), idx in built["trades"].items():
        ts = D["ts"][idx]; m = (ts >= lo_ts) & (ts < hi_ts); idx = idx[m]
        b = built["bars"][dirn]
        out[(rn, dirn)] = dict(coin=np.full(len(idx), cid, np.int8), ts=ts[m], gross=b["gross"][idx], fee=b["feeR"][idx],
                               gm=b["gm"][idx], fm=b["fm"][idx], fill=b["fill"][idx], app=b["app"][idx],
                               code=built["code"][idx], ctx=built["ctx"][:, idx], dirn=np.full(len(idx), dirn, np.int8))
    return out


def merge(tabs):
    keys = tabs[0].keys(); out = {}
    for k in keys:
        parts = [t[k] for t in tabs]
        out[k] = {f: (np.concatenate([p[f] for p in parts], axis=1) if f == "ctx" else np.concatenate([p[f] for p in parts]))
                  for f in parts[0]}
    return out


def cat(tables, keys_filter=None):
    """concat trade tables of both directions for a rule."""
    parts = tables
    return {f: (np.concatenate([p[f] for p in parts], axis=1) if f == "ctx" else np.concatenate([p[f] for p in parts]))
            for f in parts[0]}


def net12(t):
    return t["gross"] - FEE_TAKER * t["fee"]


def sel(t, m):
    return {f: (v[:, m] if f == "ctx" else v[m]) for f, v in t.items()}


def day_of(t):
    return t["ts"] // ST.D1


def row(t, rng, full=False):
    if len(t["ts"]) == 0:
        return dict(n=0)
    x = net12(t); d = day_of(t)
    r = SS.cluster(d, x, rng)
    r.update(gross=float(t["gross"].mean()), cost=float((FEE_TAKER * t["fee"]).mean()), win=float((x > 0).mean()))
    if full:
        r["ex5"] = SS.ex_best(d, x)
    return r


def build_all(end_ts, ptab):
    tabs, aux_first = [], {}
    for cid, s in enumerate(ST.SYMS):
        t0 = time.time()
        b = ST.build_coin(s, ptab, end_ts)
        aux_first[s] = {k: dt.datetime.fromtimestamp(v / 1000, dt.UTC).strftime("%Y-%m-%d") for k, v in b["aux_first"].items()}
        tabs.append((b, cid))
        print(s, f"{time.time() - t0:.0f}s", flush=True)
    return tabs, aux_first


def regime_days(ptab):
    out = {}
    for nm, lo, hi in (("DEV", "2019-01-01", "2023-12-31"), ("VAL", "2024-01-01", "2026-11-13")):
        s = ptab.loc[lo:hi, "label"].dropna()
        out[nm] = {k: int(v) for k, v in s.value_counts().items()}
        out[nm + "_total"] = int(len(s))
    return out


def step_a(tables, rng):
    """Per rule x phase: appropriate vs opposite direction (day-clustered diff, se), plus per-direction rows."""
    rows = []
    for rn in ST.RULES:
        tl = [tables[(rn, 1)], tables[(rn, -1)]]
        for j, nm in enumerate(PH.LABELS):
            for dirn in (1, -1):
                t = tables[(rn, dirn)]; m = t["code"] == j
                if m.sum():
                    r = row(sel(t, m), rng); r.update(rule=rn, phase=nm, dirn=dirn, kind="dir")
                    rows.append(r)
            pooled = cat(tl); m = pooled["code"] == j
            a = sel(pooled, m & (pooled["app"] == 1)); o = sel(pooled, m & (pooled["app"] == -1))
            if len(a["ts"]) > 10 and len(o["ts"]) > 10:
                d, se = SS.diff_cluster(day_of(a), net12(a), day_of(o), net12(o), rng)
                ra = row(a, rng); ro = row(o, rng)
                rows.append(dict(rule=rn, phase=nm, kind="app_vs_opp", n_app=ra["n"], n_opp=ro["n"], days_app=ra["days"],
                                 gross_app=ra["gross"], cost_app=ra["cost"], net_app=ra["mean"], gross_opp=ro["gross"],
                                 net_opp=ro["mean"], diff=d, se=se))
    return rows


def dev_stage():
    st = git("status", "--porcelain", "--", str(HERE))
    if st:
        sys.exit("study dir not clean/committed:\n" + st)
    head = git("rev-parse", "HEAD")
    ptab = PH.build_phase_daily()
    bad = PH.verify_phase()
    assert not bad, bad
    built, aux_first = build_all(ST.VAL_START, ptab)
    tables = merge([table_for(b, cid, 0, ST.VAL_START) for b, cid in built])
    rng = np.random.default_rng(SEED)
    A = step_a(tables, rng)
    rd = regime_days(ptab)
    dev_days = rd["DEV_total"]
    ok_phase = {nm for nm in PH.LABELS if rd["DEV"].get(nm, 0) / dev_days >= DAYFLOOR}
    cells, kept, nodata = [], [], {}
    for rn in ST.RULES:
        pool = cat([tables[(rn, 1)], tables[(rn, -1)]])
        pool = sel(pool, pool["app"] == 1)
        nodata[rn] = {"C4_signals": int((pool["ctx"][3] >= 0).sum()), "C5_signals": int((pool["ctx"][4] >= 0).sum()),
                      "all_signals": int(len(pool["ts"]))}
        rc = []
        for j, nm in enumerate(PH.LABELS):
            pm = pool["code"] == j
            for li, ln in enumerate(ST.LAYERS):
                for bi, bn in enumerate(ST.BUCKETS[ln]):
                    m = pm & (pool["ctx"][li] == bi)
                    n = int(m.sum())
                    rec = dict(rule=rn, phase=nm, layer=ln, bucket=bn, n=n)
                    if n >= MIN_N:
                        t = sel(pool, m); days = len(np.unique(day_of(t)))
                        rec["days"] = days
                        if days >= MIN_DAYS:
                            r = row(t, rng); rec.update(r)
                            rec["eligible"] = nm in ok_phase
                    rc.append(rec)
        cells += rc
        ok = [r for r in rc if r.get("eligible") and r.get("lo90", -9) > 0]
        ok.sort(key=lambda r: -r["lo90"]); used = set(); k = []
        for r in ok:
            if r["layer"] in used: continue
            used.add(r["layer"]); k.append(r)
            if len(k) == TOP_K: break
        for r in k:
            d = PH.PHASE_DIR[r["phase"]]
            kept.append(dict(rule=rn, phase=r["phase"], layer=r["layer"], bucket=r["bucket"],
                             bucket_idx=ST.BUCKETS[r["layer"]].index(r["bucket"]), layer_idx=ST.LAYERS.index(r["layer"]),
                             direction=("long" if d > 0 else "short" if d < 0 else "ACCUM: long at lower third, short at upper third"),
                             dev_n=r["n"], dev_days=r["days"], dev_net=r["mean"], dev_lo90=r["lo90"], dev_gross=r["gross"]))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(cells).to_csv(HERE / "dev_cells.csv", index=False)
    (HERE / "dev_stepA.json").write_text(json.dumps(dict(stepA=A, regime_days=rd, nodata=nodata, aux_first=aux_first,
                                                          cells_evaluated=int(sum(1 for c in cells if "mean" in c)),
                                                          ok_phase=sorted(ok_phase)), indent=1))
    (HERE / "cells_frozen.json").write_text(json.dumps(dict(code_commit=head, dev_end="2023-12-31", kept=kept), indent=1))
    print("kept cells:", len(kept))
    for k in kept: print(k)


def check_frozen():
    f = HERE / "cells_frozen.json"
    git("ls-files", "--error-unmatch", str(f))
    if git("status", "--porcelain", "--", str(HERE)):
        sys.exit("study dir not clean: commit cells_frozen.json before the VAL run")
    fz = json.loads(f.read_text())
    git("merge-base", "--is-ancestor", fz["code_commit"], "HEAD")
    changed = git("diff", "--name-only", fz["code_commit"], "HEAD", "--", str(HERE / "*.py"))
    if changed:
        sys.exit("study code changed since the frozen commit:\n" + changed)
    return fz


def val_slice(built, lo_ts):
    D = built["D"]; m = D["ts"] >= lo_ts
    out = dict(ts=D["ts"][m], code=built["code"][m], ctx=built["ctx"][:, m], c=D["c"][m])
    for dirn in (1, -1):
        b = built["bars"][dirn]
        out[dirn] = dict(net=(b["gross"] - FEE_TAKER * b["feeR"])[m].astype(np.float32), app=b["app"][m], valid=b["valid"][m])
    return out


def placebo(cell_mask_fn, real, slices, rng, nd=1000):
    """Random entries from the same cell (phase, bucket, appropriate direction), matched on (direction, hour) of each real trade."""
    pools = {}
    for sl in slices:
        base = (sl["code"] == cell_mask_fn["phase_idx"]) & (sl["ctx"][cell_mask_fn["layer_idx"]] == cell_mask_fn["bucket_idx"])
        hour = (sl["ts"] % ST.D1) // ST.H1
        for dirn in (1, -1):
            m = base & (sl[dirn]["app"] == 1) & sl[dirn]["valid"] & np.isfinite(sl[dirn]["net"])
            for h in np.unique(hour[m]):
                pools.setdefault((dirn, int(h)), []).append(sl[dirn]["net"][m & (hour == h)])
    pools = {k: np.concatenate(v) for k, v in pools.items()}
    rh = (real["ts"] % ST.D1) // ST.H1
    sums = np.zeros(nd); n = 0
    for dirn in (1, -1):
        for h in np.unique(rh[real["dirn"] == dirn]):
            m = (real["dirn"] == dirn) & (rh == h); cnt = int(m.sum())
            p = pools.get((dirn, int(h)))
            if p is None: continue
            sums += p[rng.integers(0, len(p), (cnt, nd))].sum(0); n += cnt
    pm = sums / max(n, 1)
    rm = float(net12(real).mean())
    return dict(placebo_mean=float(pm.mean()), real_minus_placebo=rm - float(pm.mean()),
                placebo_p=float((np.sum(pm >= rm) + 1) / (nd + 1)), n_matched=n)


def val_stage():
    fz = check_frozen()
    ptab = PH.build_phase_daily(); bad = PH.verify_phase(); assert not bad, bad
    built_list, aux_first = build_all(None, ptab)
    tables = merge([table_for(b, cid, ST.VAL_START, 2 ** 62) for b, cid in built_list])
    slices = [val_slice(b, ST.VAL_START) for b, cid in built_list]
    rng = np.random.default_rng(SEED + 1)
    A = step_a(tables, rng)
    res = []
    for k in fz["kept"]:
        rn = k["rule"]; j = PH.LABELS.index(k["phase"]); li, bi = k["layer_idx"], k["bucket_idx"]
        pool = cat([tables[(rn, 1)], tables[(rn, -1)]])
        cellm = (pool["code"] == j) & (pool["ctx"][li] == bi)
        cell = sel(pool, cellm & (pool["app"] == 1))
        r = dict(k); r.update(row(cell, rng, full=True) if len(cell["ts"]) else dict(n=0))
        if r["n"] >= 10:
            r.update(placebo(dict(phase_idx=j, layer_idx=li, bucket_idx=bi), cell, slices, rng))
            mk = cell["fill"]
            xm = (cell["gm"] - FEE_MAKER * cell["fm"])[mk]
            r["maker6_n_filled"] = int(mk.sum()); r["maker6_fill_rate"] = float(mk.mean())
            r["maker6_net"] = float(xm.mean()) if len(xm) else None
            r["maker6_gross"] = float(cell["gm"][mk].mean()) if len(xm) else None
        opp = sel(pool, cellm & (pool["app"] == -1)); r["ctl_opposite"] = row(opp, rng)
        dirs = [1] if PH.PHASE_DIR[k["phase"]] > 0 else [-1] if PH.PHASE_DIR[k["phase"]] < 0 else [1, -1]
        oth = cat([tables[(rn, d)] for d in dirs]); oth = sel(oth, (oth["code"] != j) & (oth["ctx"][li] == bi))
        r["ctl_other_phases"] = row(oth, rng)
        ph_only = sel(pool, (pool["code"] == j) & (pool["app"] == 1)); r["ctl_phase_all_buckets"] = row(ph_only, rng)
        r["ctl_unconditional_rule"] = row(pool, rng)
        res.append(r)
    ps = [r["p"] for r in res if r["n"] >= 10]
    q = SS.bh(ps, 0.10); qi = 0
    for r in res:
        if r["n"] >= 10:
            r["bh_q"] = float(q[qi]); qi += 1
        gates = r["n"] >= MIN_N and r.get("mean", -1) > 0 and r.get("lo95", -1) > 0 and r.get("ex5", -1) > 0 \
            and r.get("placebo_p", 1) < 0.05 and r.get("bh_q", 1) < 0.10
        r["verdict"] = "PASS" if gates else ("UNDERPOWERED" if r["n"] < MIN_N else "FAIL")
    # today block: last 10 labels, and each kept cell active state on BTC / ETH last closed bar
    last10 = ptab.tail(10)[["label", "cycle", "provisional"]].reset_index().astype({"date": str}).to_dict("records")
    btc = ptab.loc[:, ["close_used"]].tail(1)
    today = dict(last10=last10, active=[])
    for sym in ("BTC", "ETH"):
        cid = ST.SYMS.index(sym); b = built_list[cid][0]
        i = len(b["D"]["ts"]) - 1
        ctxv = {ln: ST.BUCKETS[ln][int(b["ctx"][li, i])] if b["ctx"][li, i] >= 0 else "NO-DATA" for li, ln in enumerate(ST.LAYERS)}
        today[sym] = dict(last_bar=dt.datetime.fromtimestamp(int(b["D"]["ts"][i]) / 1000, dt.UTC).strftime("%Y-%m-%d %H:%M"),
                          code=int(b["code"][i]), phase=PH.LABELS[int(b["code"][i])] if b["code"][i] >= 0 else None, ctx=ctxv)
        for k in fz["kept"]:
            if b["code"][i] == PH.LABELS.index(k["phase"]) and b["ctx"][k["layer_idx"], i] == k["bucket_idx"]:
                today["active"].append(dict(sym=sym, rule=k["rule"], phase=k["phase"], layer=k["layer"], bucket=k["bucket"],
                                            rule_signal_now=None))
    (HERE / "val_results.json").write_text(json.dumps(dict(cells=res, stepA=A, regime_days=regime_days(ptab), aux_first=aux_first,
                                                           today=today, code_commit=fz["code_commit"]), indent=1, default=float))
    for r in res:
        print(r["rule"], r["phase"], r["layer"], r["bucket"], r["n"], round(r.get("mean", float("nan")), 3), r["verdict"])


if __name__ == "__main__":
    {"dev": dev_stage, "val": val_stage}[sys.argv[1]]()
