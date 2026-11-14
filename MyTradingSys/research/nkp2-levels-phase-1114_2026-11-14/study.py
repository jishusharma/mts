"""nkp2-levels-phase-1114 driver. Protocol (PRE_REG.md): `python study.py dev` -> Step A (DEV) + Step B selection -> cells_frozen.json (commit it);
`python study.py val` -> Step A (VAL, descriptive) + Step C on the frozen cells only (run once); `python study.py report` -> RESULT.md.
`dev` refuses to run while the study code / PRE_REG.md have uncommitted changes (code is committed before any outcome is computed).
`val` refuses unless the code is unchanged since the commit named in cells_frozen.json and cells_frozen.json itself is committed."""
import os, sys, json, subprocess, pickle, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nkcore as nk
import ctxlib as cx
import mts_phase as mp

REPO = HERE.parents[2]
FROZEN = HERE / "cells_frozen.json"
CODE_FILES = ["PRE_REG.md", "study.py", "nkcore.py", "ctxlib.py", "mts_phase.py", "fetch_ctx.py", "test_study.py"]
SPLIT, DAY = nk.SPLIT, nk.DAY
REG_BASIS = {"NK2-core": "close", "NK2-deep": "close", "NK3-A": "intraday", "NK3-B": "intraday"}
N_MIN, D_MIN, NB_SEL, NB_VAL, NPLACEBO = 150, 40, 2000, 5000, 1000
DEV_START = dt.date(2019, 1, 1).toordinal() - 719163
DEV_END = dt.date(2023, 12, 31).toordinal() - 719163


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def code_dirty():
    out = git("status", "--porcelain", "--", *[str((HERE / f).relative_to(REPO)) for f in CODE_FILES])
    return out


def trades(cache=True):
    p = nk.CACHE / "binance" / "nkp2-levels-phase-1114" / "trades_cache.pkl"
    if cache and p.exists() and not os.environ.get("STUDY_BUG"):
        return pickle.load(open(p, "rb"))
    T = nk.build_trades()
    if cache and not os.environ.get("STUDY_BUG"):
        pickle.dump(T, open(p, "wb"))
    return T


# ---------- statistics ----------
def netr(T, bp=12.0):
    return T["g"] - nk.fee_r(T, bp)


def sub(T, m):
    return {k: v[m] for k, v in T.items()}


def dir_ok(T, p):
    d = mp.PH_DIR[p]
    return np.ones(len(T["d"]), bool) if d == 0 else (T["d"] == d)


def day_arr(T):
    return T["t"] // DAY


def boot_means(R, day, nb, seed):
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    nn = np.bincount(inv).astype(float)
    D = len(u)
    rng = np.random.default_rng(seed)
    out = []
    chunk = max(1, int(4e6 // D))
    done = 0
    while done < nb:
        b = min(chunk, nb - done)
        ix = rng.integers(0, D, (b, D))
        out.append(sR[ix].sum(axis=1) / nn[ix].sum(axis=1))
        done += b
    return np.concatenate(out)


def ex_best5(R, day):
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    worst = np.argsort(-sR)[:5]
    m = ~np.isin(inv, worst)
    return float(R[m].mean()) if m.any() else float("nan")


def basic(T, bp=12.0):
    n = len(T["g"])
    if n == 0:
        return dict(n=0, days=0, gross=np.nan, cost=np.nan, net=np.nan)
    f = nk.fee_r(T, bp)
    return dict(n=n, days=int(len(np.unique(day_arr(T)))), gross=float(T["g"].mean()), cost=float(f.mean()), net=float((T["g"] - f).mean()))


def diff_app_opp(T, p, bp=12.0):
    """phase-appropriate minus opposite direction, day-clustered difference and bootstrap se (p in 1,2,3,5,6)."""
    d = mp.PH_DIR[p]
    m = T["ph"] == p
    R = netr(T, bp)
    a, o = m & (T["d"] == d), m & (T["d"] == -d)
    if a.sum() < 20 or o.sum() < 20:
        return None
    days = np.unique(day_arr(T)[a | o])
    ix = {x: i for i, x in enumerate(days)}
    def agg(mm):
        s = np.zeros(len(days)); c = np.zeros(len(days))
        for dd, r in zip(day_arr(T)[mm], R[mm]):
            s[ix[dd]] += r; c[ix[dd]] += 1
        return s, c
    sa, ca = agg(a); so, co = agg(o)
    rng = np.random.default_rng(99)
    D = len(days)
    diffs = []
    for _ in range(40):
        j = rng.integers(0, D, (50, D))
        diffs.append(sa[j].sum(1) / np.maximum(ca[j].sum(1), 1) - so[j].sum(1) / np.maximum(co[j].sum(1), 1))
    diffs = np.concatenate(diffs)
    pt = R[a].mean() - R[o].mean()
    return dict(app_n=int(a.sum()), opp_n=int(o.sum()), app_net=float(R[a].mean()), opp_net=float(R[o].mean()), diff=float(pt), se=float(diffs.std()), z=float(pt / diffs.std()) if diffs.std() > 0 else np.nan)


def phase_day_mix():
    days, lab = mp.phase_table_for_study()
    out = {}
    last = int(days.max())
    for nm, a, b in (("DEV", DEV_START, DEV_END), ("VAL", DEV_END + 1, last)):
        m = (days >= a) & (days <= b)
        tot = int(m.sum())
        out[nm] = {mp.PH_NAMES[p]: (int(((lab == p) & m).sum()), round(float(((lab == p) & m).sum() / tot), 4)) for p in range(1, 7)}
        out[nm]["_days"] = tot
    return out


def table_stepA(T, which):
    """rows per rule x phase x direction. which = 'DEV' or 'VAL' (descriptive only on VAL, after the freeze)."""
    rows = []
    for r in nk.RULES:
        reg = REG_BASIS[r]
        alt = "intraday" if reg == "close" else "close"
        A = T[(r, reg, "taker")]
        B = T[(r, alt, "taker")]
        sel = lambda X: ((X["t"] < SPLIT) if which == "DEV" else (X["t"] >= SPLIT)) & (X["ph"] >= 1)
        A, B = sub(A, sel(A)), sub(B, sel(B))
        for p in range(1, 7):
            for d in (1, -1):
                ma, mb = (A["ph"] == p) & (A["d"] == d), (B["ph"] == p) & (B["d"] == d)
                s = basic(sub(A, ma))
                s2 = basic(sub(B, mb))
                app = "appropriate" if mp.PH_DIR[p] in (d, 0) else "opposite"
                if mp.PH_DIR[p] == 0:
                    app = "both"
                rows.append(dict(rule=r, split=which, phase=mp.PH_NAMES[p], dir="long" if d > 0 else "short", role=app, basis=reg, **s, alt_basis=alt, alt_net=s2["net"], alt_n=s2["n"]))
    return rows


def diff_table(T, which):
    rows = []
    for r in nk.RULES:
        X = T[(r, REG_BASIS[r], "taker")]
        X = sub(X, ((X["t"] < SPLIT) if which == "DEV" else (X["t"] >= SPLIT)) & (X["ph"] >= 1))
        for p in (1, 2, 3, 5, 6):
            q = diff_app_opp(X, p)
            if q:
                rows.append(dict(rule=r, split=which, phase=mp.PH_NAMES[p], **q))
    return rows


def level_table(T, which):
    rows = []
    for r in ("NK2-core", "NK2-deep"):
        X = T[(r, "close", "taker")]
        X = sub(X, ((X["t"] < SPLIT) if which == "DEV" else (X["t"] >= SPLIT)) & (X["ph"] >= 1))
        for li, L in enumerate(nk.LEVELS):
            m = X["lvl"] == li
            if not m.any():
                continue
            for lab, mm in (("appropriate-direction trades", np.array([mp.PH_DIR[p] in (0, d) for p, d in zip(X["ph"], X["d"])])), ("all trades", np.ones(len(X["d"]), bool))):
                rows.append(dict(rule=r, split=which, level=L, subset=lab, **basic(sub(X, m & mm))))
    return rows


# ---------- Step B ----------
def select_cells(T, dev_share):
    """returns (kept cells, scored cells, no-data notes). cell = rule, phase, layer, bucket."""
    kept, scored, nodata = {}, [], []
    cid = 0
    for r in nk.RULES:
        X = T[(r, REG_BASIS[r], "taker")]
        X = sub(X, (X["t"] < SPLIT) & (X["ph"] >= 1))
        R = netr(X)
        cand = []
        for li, L in enumerate(cx.LAYERS):
            if (X["ctx"][:, li] >= 0).sum() < N_MIN:
                nodata.append(dict(rule=r, layer=L, note="NO-DATA (<150 DEV signals with this layer)"))
                continue
            for p in range(1, 7):
                if dev_share[p] < 0.05:
                    continue
                dm = dir_ok(X, p)
                for b in range(3):
                    cid += 1
                    m = (X["ph"] == p) & dm & (X["ctx"][:, li] == b)
                    n = int(m.sum())
                    days = int(len(np.unique(X["t"][m] // DAY))) if n else 0
                    row = dict(rule=r, phase=mp.PH_NAMES[p], phase_id=p, layer=L, bucket=cx.BUCKET_NAMES[L][b], bucket_id=b, n=n, days=days, mean=float(R[m].mean()) if n else np.nan, score=np.nan)
                    if n >= N_MIN and days >= D_MIN and row["mean"] > 0:
                        bm = boot_means(R[m], X["t"][m] // DAY, NB_SEL, 1000 + cid)
                        row["score"] = float(np.percentile(bm, 5))
                    scored.append(row)
                    if row["score"] == row["score"] and row["score"] > 0:
                        cand.append(row)
        cand.sort(key=lambda x: -x["score"])
        used = set()
        keep = []
        for c in cand:
            if c["layer"] in used:
                continue
            used.add(c["layer"])
            keep.append(c)
            if len(keep) == 3:
                break
        kept[r] = keep
    return kept, scored, nodata


def eligible_counts(scored):
    out = {}
    for r in nk.RULES:
        rows = [x for x in scored if x["rule"] == r]
        out[r] = dict(cells_scored=len(rows), cells_n_days_ok=sum(1 for x in rows if x["n"] >= N_MIN and x["days"] >= D_MIN),
                      positive_dev_mean=sum(1 for x in rows if x["n"] >= N_MIN and x["days"] >= D_MIN and x["mean"] > 0), score_gt0=sum(1 for x in rows if x["score"] == x["score"] and x["score"] > 0))
    return out


def write_csv(path, rows):
    if not rows:
        Path(path).write_text("")
        return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join("" if r.get(k) is None else (f"{r[k]:.5g}" if isinstance(r[k], float) else str(r[k]).replace(",", ";")) for k in keys) + "\n")


def cmd_dev():
    d = code_dirty()
    if d and not os.environ.get("STUDY_ALLOW_DIRTY"):
        sys.exit("REFUSED: study code/PRE_REG.md has uncommitted changes; commit first (code before outcomes):\n" + d)
    head = git("rev-parse", "HEAD")
    T = trades()
    mix = phase_day_mix()
    dev_share = {p: mix["DEV"][mp.PH_NAMES[p]][1] for p in range(1, 7)}
    A_dev = table_stepA(T, "DEV")
    diff_dev = diff_table(T, "DEV")
    kept, scored, nodata = select_cells(T, dev_share)
    write_csv(HERE / "stepA_dev.csv", A_dev)
    write_csv(HERE / "stepA_appropriate_vs_opposite_dev.csv", diff_dev)
    write_csv(HERE / "levels_dev.csv", level_table(T, "DEV"))
    write_csv(HERE / "dev_cells_scored.csv", [x for x in scored if x["n"] >= N_MIN and x["days"] >= D_MIN])
    frozen = dict(code_commit=head, created_utc=dt.datetime.now(dt.timezone.utc).isoformat(), spec="MTS_BRAINS_SPEC_1114", dev_end="2023-12-31", val_start="2024-01-01",
                  dev_phase_share={mp.PH_NAMES[p]: dev_share[p] for p in dev_share}, eligible=eligible_counts(scored), no_data=nodata,
                  cells=[dict(rule=c["rule"], phase=c["phase"], phase_id=c["phase_id"], layer=c["layer"], bucket=c["bucket"], bucket_id=c["bucket_id"],
                              direction={1: "long", -1: "short", 0: "both"}[mp.PH_DIR[c["phase_id"]]], basis=REG_BASIS[c["rule"]], dev_n=c["n"], dev_days=c["days"], dev_net=c["mean"], dev_score=c["score"])
                         for r in kept for c in kept[r]])
    FROZEN.write_text(json.dumps(frozen, indent=1, default=float))
    print("kept cells:", len(frozen["cells"]))
    for c in frozen["cells"]:
        print(c)
    print(json.dumps(frozen["eligible"], indent=1))
    print("frozen ->", FROZEN)


# ---------- Step C ----------
def cell_mask(X, c, extra_dir=None, other_phases=False):
    p = c["phase_id"]
    dm = dir_ok(X, p) if extra_dir is None else (X["d"] == extra_dir)
    ph = (X["ph"] != p) & (X["ph"] >= 1) if other_phases else (X["ph"] == p)
    return ph & dm & (X["ctx"][:, cx.LAYERS.index(c["layer"])] == c["bucket_id"])


def cell_stats(X, m, bp=12.0, seed=7):
    Y = sub(X, m)
    n = len(Y["g"])
    if n == 0:
        return dict(n=0)
    R = netr(Y, bp)
    day = day_arr(Y)
    f = nk.fee_r(Y, bp)
    wins = R > 0
    bm = boot_means(R, day, NB_VAL, seed) if n > 1 else np.array([np.nan])
    aw = R[wins].mean() if wins.any() else 0.0
    al = -R[~wins].mean() if (~wins).any() else 0.0
    return dict(n=n, days=int(len(np.unique(day))), win=float(wins.mean() * 100), be_win=float(al / (aw + al) * 100) if aw + al > 0 else np.nan, gross=float(Y["g"].mean()),
                cost=float(f.mean()), net=float(R.mean()), ci_lo=float(np.percentile(bm, 2.5)), ci_hi=float(np.percentile(bm, 97.5)), p_le0=float((1 + (bm <= 0).sum()) / (len(bm) + 1)),
                ex5=ex_best5(R, day))


_D = {}


def get_D(ci):
    if ci not in _D:
        pdays, plab = mp.phase_table_for_study()
        _D[ci] = nk.prep(nk.COINS[ci], pdays, plab)
    return _D[ci]


def placebo(rule, c, Xval_cell, rng):
    """1000 random entries from the same cell (phase day, bucket, direction, exit + stop rule) matched on hour of the real trade; returns (placebo mean, p)."""
    li = cx.LAYERS.index(c["layer"])
    basis = REG_BASIS[rule]
    real_hr = (Xval_cell["t"] // nk.H1) % 24
    real_d = Xval_cell["d"]
    real_df = Xval_cell["df"]
    pool = {}
    need = set(zip(real_d.tolist(), real_hr.tolist()))
    cand = {}
    for ci in range(len(nk.COINS)):
        D = get_D(ci)
        okb = D["valid"] & (D["t"] >= SPLIT) & (D["ph"] == c["phase_id"]) & (D["ctx"][li] == c["bucket_id"]) & ~np.isnan(D["atr"])
        okb[-60:] = False
        hr = (D["t"] // nk.H1) % 24
        for h in range(24):
            ix = np.flatnonzero(okb & (hr == h))
            if len(ix):
                cand.setdefault(h, []).append((ci, ix))
    for (d, h) in need:
        lst = cand.get(h, [])
        if not lst:
            continue
        allc = [(ci, i) for ci, ix in lst for i in ix]
        sel = rng.choice(len(allc), size=min(80, len(allc)), replace=False)
        vals = []
        for s in sel:
            ci, i = allc[s]
            D = get_D(ci)
            if rule.startswith("NK2"):
                tr = nk.nk2_trade(D, int(i), d, basis, False)
            else:
                e = D["o"][i + 1]
                dist = real_df[rng.integers(0, len(real_df))] * e
                stop, tgt = e - d * dist, e + d * nk.TGT_R * dist
                xpx, xi = nk.exit_sim(D, i + 1, d, e, stop, tgt, basis, tgt_first=True)
                tr = dict(g=d * (xpx - e) / dist, df=dist / e, e=e, x=xpx)
            if tr is None:
                continue
            fee = (12 / 2e4) * (tr["e"] + tr["x"]) / (tr["df"] * tr["e"])
            vals.append(tr["g"] - fee)
        if vals:
            pool[(d, h)] = np.array(vals)
    keys = [(d, h) for d, h in zip(real_d.tolist(), real_hr.tolist()) if (d, h) in pool]
    if len(keys) < 20:
        return dict(placebo_mean=np.nan, placebo_p=np.nan, placebo_n=len(keys))
    means = np.array([np.mean([pool[k][rng.integers(0, len(pool[k]))] for k in keys]) for _ in range(NPLACEBO)])
    return dict(placebo_mean=float(means.mean()), placebo_n=len(keys), _means=means)


def bh(ps, q=0.10):
    """Benjamini-Hochberg: returns (reject flags, adjusted q-values)."""
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        j = order[rank - 1]
        prev = min(prev, ps[j] * m / rank)
        adj[j] = prev
    return adj <= q, [float(x) for x in adj]


def cmd_val():
    fr = json.loads(FROZEN.read_text())
    if code_dirty() and not os.environ.get("STUDY_ALLOW_DIRTY"):
        sys.exit("REFUSED: code dirty")
    if git("status", "--porcelain", "--", str(FROZEN.relative_to(REPO))):
        sys.exit("REFUSED: cells_frozen.json is not committed")
    chg = git("diff", "--name-only", fr["code_commit"], "--", *[str((HERE / f).relative_to(REPO)) for f in CODE_FILES])
    if chg:
        sys.exit("REFUSED: code changed since the freeze commit:\n" + chg)
    T = trades()
    mix = phase_day_mix()
    A_val = table_stepA(T, "VAL")
    write_csv(HERE / "stepA_val.csv", A_val)
    write_csv(HERE / "stepA_appropriate_vs_opposite_val.csv", diff_table(T, "VAL"))
    write_csv(HERE / "levels_val.csv", level_table(T, "VAL"))
    rng = np.random.default_rng(20261114)
    res = []
    for k, c in enumerate(fr["cells"]):
        r = c["rule"]
        X = sub(T[(r, c["basis"], "taker")], T[(r, c["basis"], "taker")]["t"] >= SPLIT)
        M = sub(T[(r, c["basis"], "maker")], T[(r, c["basis"], "maker")]["t"] >= SPLIT)
        m = cell_mask(X, c)
        row = dict(cell=c, val=cell_stats(X, m, 12.0, 11 + k))
        row["maker6bp"] = cell_stats(M, cell_mask(M, c), 6.0, 31 + k)
        row["maker_fill_ratio"] = float(row["maker6bp"]["n"] / max(row["val"]["n"], 1))
        Y = sub(X, m)
        pl = placebo(r, c, Y, rng)
        means = pl.pop("_means", None)
        if means is not None:
            real = row["val"]["net"]
            pl["placebo_p"] = float((1 + (means >= real).sum()) / (len(means) + 1))
            pl["real_minus_placebo"] = float(real - pl["placebo_mean"])
        row["placebo"] = pl
        d0 = mp.PH_DIR[c["phase_id"]]
        row["control_opposite_dir"] = cell_stats(X, cell_mask(X, c, extra_dir=(-d0 if d0 else None)), 12.0, 51) if d0 else None
        row["control_other_phases_same_bucket"] = cell_stats(X, cell_mask(X, c, other_phases=True) & (dir_ok(X, c["phase_id"])), 12.0, 52)
        row["control_unconditional"] = cell_stats(X, (X["ph"] >= 1) & dir_ok(X, c["phase_id"]), 12.0, 53)
        res.append(row)
    if res:
        ok, qs = bh(np.array([x["val"].get("p_le0", 1.0) if x["val"]["n"] > 1 else 1.0 for x in res]), 0.10)
        for x, o, q in zip(res, ok, qs):
            v = x["val"]
            x["bh_q"] = q
            checks = dict(n=v["n"] >= N_MIN, net=v["net"] > 0 if v["n"] else False, ci=(v["ci_lo"] > 0) if v["n"] else False, ex5=(v["ex5"] > 0) if v["n"] else False,
                          placebo=(x["placebo"].get("placebo_p", 1) < 0.05), bh=q < 0.10)
            x["checks"] = checks
            x["verdict"] = "PASS" if all(checks.values()) else ("UNDERPOWERED" if not checks["n"] else "FAIL")
    out = dict(frozen=fr, mix=mix, val_cells=res, passed=sum(1 for x in res if x.get("verdict") == "PASS"), signals_per_phase=signals_per_phase(T), today=today_block(fr))
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("passed",)}), "cells", len(res))
    for x in res:
        print(x["cell"]["rule"], x["cell"]["phase"], x["cell"]["layer"], x["cell"]["bucket"], x["verdict"], x["val"].get("n"), round(x["val"].get("net", np.nan), 4), round(x["val"].get("ci_lo", np.nan), 4))


def signals_per_phase(T):
    out = {}
    for r in nk.RULES:
        X = T[(r, REG_BASIS[r], "taker")]
        for nm, m in (("DEV", X["t"] < SPLIT), ("VAL", X["t"] >= SPLIT)):
            out[f"{r}_{nm}"] = {mp.PH_NAMES[p]: int(((X["ph"] == p) & m).sum()) for p in range(1, 7)}
    return out


def today_block(fr):
    d, h, l, c = mp.load_btc_daily()
    dl, lab, state, F = mp.day_labels(d, h, l, c, lag=1)
    rows = []
    for k in range(len(d) - 9, len(d)):
        rows.append(dict(day_closed=dt.date.fromordinal(int(d[k]) + 719163).isoformat(), label_for_next_day=mp.PH_NAMES[int(lab[k])], close=float(c[k]), sma50=float(F["s50"][k]), sma200=float(F["s200"][k]), w200=float(F["w200"][k]), state=str(state[k])))
    part = mp.load_btc_partial_today()
    prov = None
    if part:
        d2, h2, l2, c2 = np.r_[d, part[0]], np.r_[h, part[1]], np.r_[l, part[2]], np.r_[c, part[3]]
        dl2, lab2, st2, F2 = mp.day_labels(d2, h2, l2, c2, lag=1)
        prov = dict(partial_day=dt.date.fromordinal(part[0] + 719163).isoformat(), bars=part[4], provisional_label_for_next_day=mp.PH_NAMES[int(lab2[-1])], close=part[3])
    # label that APPLIES to the latest UTC day (from the csv) and context of the latest closed 1h bar for BTC/ETH
    days, plab = mp.phase_table_for_study()
    cur = dict(latest_label_day=dt.date.fromordinal(int(days[-1]) + 719163).isoformat(), phase=mp.PH_NAMES[int(plab[-1])])
    ctxnow = {}
    for coin in ("BTC", "ETH"):
        D = get_D(nk.COINS.index(coin))
        ctxnow[coin] = dict(last_1h_open=str(np.datetime64(int(D["t"][-1]), "ms")), phase=mp.PH_NAMES[int(D["ph"][-1])] if D["ph"][-1] else "none",
                            ctx={L: cx.BUCKET_NAMES[L][int(D["ctx"][i, -1])] if D["ctx"][i, -1] >= 0 else "NO-DATA" for i, L in enumerate(cx.LAYERS)})
    active = []
    for c0 in fr["cells"]:
        for coin in ("BTC", "ETH"):
            cc = ctxnow[coin]
            if cc["phase"] == c0["phase"] and cc["ctx"][c0["layer"]] == c0["bucket"]:
                active.append(dict(coin=coin, rule=c0["rule"], phase=c0["phase"], layer=c0["layer"], bucket=c0["bucket"]))
    return dict(last_10_closed_days=rows, provisional=prov, applied_label=cur, context_now=ctxnow, kept_cells_active_now=active)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"dev": cmd_dev, "val": cmd_val}.get(cmd, lambda: sys.exit("usage: study.py dev|val"))()
