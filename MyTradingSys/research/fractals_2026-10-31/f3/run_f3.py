"""F3: phase-matched nearest-neighbour analog forecast on 1h BTC vs random-walk surrogate and block-shuffled-outcome libraries.

See PRE_REG.md. DEV 2022-01-01..2025-06-30 only; files after 2025-06 are never opened (tf_break `load`).
Usage: python run_f3.py [out_file]
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "MyTradingSys", "backtest"))
sys.path.insert(0, os.path.join(HERE, "..", "phase_tag"))
import fees  # noqa: E402
import harness  # noqa: E402

L = 48                 # query path length (1h bars)
H = 24                 # outcome / hold (1h bars)
K = 10                 # neighbours
AGREE = 0.7            # share of neighbours that must share the forecast sign
SPACING = L            # min distance between chosen neighbour ends (no shared bar)
WARM = 2000            # library windows before the first query
DRAWS = 300
VOL_WIN = 168
BLOCK = 168
BOOT = 2000
SEED = 31
TOPN = 400
FEE_SIDE = fees.BINANCE_TAKER
RT_PCT = 2 * FEE_SIDE * 100.0


def _load_tfb():
    p = os.path.join(REPO, "MyTradingSys", "research", "tf_break_event_study_2026-10-30", "study.py")
    spec = importlib.util.spec_from_file_location("tf_break_study", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hourly_grid(t, c):
    """Full hourly grid from t[0] to t[-1]; close is NaN where an hour is missing."""
    t = np.asarray(t, dtype=np.int64)
    n = int((t[-1] - t[0]) // 3600) + 1
    idx = ((t - t[0]) // 3600).astype(np.int64)
    close = np.full(n, np.nan)
    close[idx] = np.asarray(c, dtype=float)
    return t[0] + np.arange(n, dtype=np.int64) * 3600, close


def log_returns(close):
    lc = np.log(close)
    return np.concatenate([[np.nan], np.diff(lc)])


def z_windows(r, length=L):
    """(n, length) float32 z-normalised path of the `length` returns ending at each bar (row e = r[e-length+1..e]);
    rows with a NaN or zero std are all-zero and flagged invalid. Returns (Z, valid)."""
    n = len(r)
    if n < length:
        return np.zeros((n, length), dtype=np.float32), np.zeros(n, dtype=bool)
    win = np.lib.stride_tricks.sliding_window_view(r, length)      # row j ends at e = j + length - 1
    ok = ~np.isnan(win).any(axis=1)
    w0 = np.where(ok[:, None], win, 0.0)
    mu = w0.mean(axis=1)
    sd = w0.std(axis=1)
    good = ok & (sd > 1e-15)
    zz = (w0 - mu[:, None]) / np.where(good, sd, 1.0)[:, None]
    zz = np.where(good[:, None], zz, 0.0)
    Z = np.concatenate([np.zeros((length - 1, length), dtype=np.float32), zz.astype(np.float32)])
    valid = np.concatenate([np.zeros(length - 1, dtype=bool), good])
    return Z, valid


def forward_log(r, h=H):
    """fwd[e] = sum r[e+1..e+h] (log return from close e to close e+h); NaN if any hour in it is missing or beyond the end."""
    n = len(r)
    bad = np.isnan(r)
    cs = np.cumsum(np.where(bad, 0.0, r))
    cb = np.cumsum(bad.astype(np.int64))
    fwd = np.full(n, np.nan)
    if n > h:
        e = np.arange(n - h)
        ok = (cb[e + h] - cb[e]) == 0
        fwd[: n - h] = np.where(ok, cs[e + h] - cs[e], np.nan)
    return fwd


def trailing_std(r, win=VOL_WIN, shift=0, minp=20):
    """Std of r over the trailing `win` bars ending `shift` bars before each bar (shift=1: strictly past)."""
    s = pd.Series(r).rolling(win, min_periods=minp).std(ddof=0).to_numpy()
    if shift:
        s = np.concatenate([np.full(shift, np.nan), s[: len(s) - shift]])
    return s


def neighbours(Zl, lib_valid, lib_fwd_ok, Zq, qe, ph, use_phase):
    """For each query end qe[j] return the chosen neighbour ends (empty array if fewer than K spaced neighbours exist).

    Library = ends e' <= qe - H, valid window, finite library outcome, and (use_phase) same phase code as the query.
    Distance = Euclidean on z-paths (monotone in -dot because every z-path has the same norm).
    """
    D = Zl @ Zq[qe].T                                  # (n, nq) dot products
    ok_lib = lib_valid & lib_fwd_ok
    out = []
    for j, e in enumerate(qe):
        m = e - H
        mask = ok_lib[: m + 1].copy()
        if use_phase:
            mask &= ph[: m + 1] == ph[e]
        cnt = int(mask.sum())
        if cnt < K:
            out.append(np.empty(0, dtype=np.int64))
            continue
        col = np.where(mask, D[: m + 1, j].astype(np.float64), -np.inf)
        top_n = min(TOPN, cnt)
        top = np.argpartition(-col, top_n - 1)[:top_n]
        top = top[np.argsort(-col[top])]
        chosen = []
        for i in top:
            if all(abs(int(i) - c) >= SPACING for c in chosen):
                chosen.append(int(i))
                if len(chosen) == K:
                    break
        out.append(np.array(chosen if len(chosen) == K else [], dtype=np.int64))
    return out


def decide(nb, lib_fwd):
    """Per query: (answered, position). Position 0 = no trade (unanswered or neighbours disagree)."""
    ans = np.zeros(len(nb), dtype=bool)
    pos = np.zeros(len(nb), dtype=int)
    for j, ix in enumerate(nb):
        if len(ix) < K:
            continue
        ans[j] = True
        o = lib_fwd[ix]
        s = 1 if o.mean() > 0 else -1
        if (np.sign(o) == s).mean() >= AGREE:
            pos[j] = s
    return ans, pos


def trade_net(pos, qe, fwd_real):
    """Net % per trade (taker both legs): returns (taken mask, net %, hit)."""
    taken = pos != 0
    gross = pos * (np.exp(fwd_real[qe]) - 1.0) * 100.0
    net = np.where(taken, gross - RT_PCT, np.nan)
    hit = np.where(taken, (pos * fwd_real[qe]) > 0, False)
    return taken, net, hit


def surrogate_returns(r, rng):
    """Random-walk returns with the real series' trailing (strictly past) volatility; NaN where the real series is NaN."""
    sg = trailing_std(r, shift=1)
    sg = np.where(np.isnan(sg), np.nanmean(sg), sg)
    z = rng.standard_normal(len(r))
    return np.where(np.isnan(r), np.nan, z * sg)


def block_permute(x, block, rng):
    n = len(x)
    nb = -(-n // block)
    order = rng.permutation(nb)
    parts = [x[b * block: min((b + 1) * block, n)] for b in order]
    return np.concatenate(parts)


def shuffled_fwd(fwd, block, rng):
    out = fwd.copy()
    ix = np.flatnonzero(np.isfinite(fwd))
    out[ix] = block_permute(fwd[ix], block, rng)
    return out


def first_query(lib_valid, lib_fwd_ok, warm=WARM):
    ok = np.cumsum(lib_valid & lib_fwd_ok)
    for e in range(H, len(ok)):
        if ok[e - H] >= warm:
            return e
    return None


def make_queries(r_real, warm=WARM):
    Z, valid = z_windows(r_real)
    fwd = forward_log(r_real)
    ok = np.isfinite(fwd)
    e0 = first_query(valid, ok, warm)
    if e0 is None:
        return Z, valid, fwd, np.empty(0, dtype=np.int64)
    qe = np.arange(e0, len(r_real) - H, H)            # non-overlapping, step 24
    qe = qe[valid[qe] & ok[qe]]
    return Z, valid, fwd, qe


def week_bootstrap(vals, weeks, rng, n=BOOT):
    """95 % percentile CI of the mean with weeks as blocks."""
    vals = np.asarray(vals, dtype=float)
    uw, inv = np.unique(weeks, return_inverse=True)
    s = np.bincount(inv, weights=vals)
    c = np.bincount(inv)
    means = np.empty(n)
    for i in range(n):
        pick = rng.integers(0, len(uw), len(uw))
        means[i] = s[pick].sum() / c[pick].sum()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def holm(ps):
    ps = np.asarray(ps, dtype=float)
    order = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * ps[i])
        adj[i] = min(1.0, run)
    return adj


def summarise(net, hit, taken, qe, split_e):
    a = taken & (qe < split_e)
    b = taken & (qe >= split_e)

    def mean_of(m):
        return float(np.mean(net[m])) if m.any() else float("nan")

    return {"n": int(taken.sum()), "mean": mean_of(taken), "hit": float(hit[taken].mean()) if taken.any() else float("nan"),
            "nA": int(a.sum()), "meanA": mean_of(a), "nB": int(b.sum()), "meanB": mean_of(b)}


def load_bars():
    tfb = _load_tfb()
    df = tfb.load()
    b = tfb.bars(df, 60)
    b = b[b.t < int(pd.Timestamp("2025-07-01", tz="UTC").timestamp())]
    return hourly_grid(b["t"].to_numpy(), b["c"].to_numpy())


def phase_codes(t):
    """Integer code per bar of the (cowen_side, sma200_side) pair of the bar's UTC date; -1 if missing."""
    tg = pd.read_csv(os.path.join(HERE, "..", "phase_tag", "tags.csv"), usecols=["date", "cowen_side", "sma200_side"])
    key = (tg["cowen_side"].astype(str) + "|" + tg["sma200_side"].astype(str)).to_numpy()
    date = pd.to_datetime(tg["date"]).dt.strftime("%Y-%m-%d").to_numpy()
    lut = dict(zip(date, key))
    days = pd.to_datetime(t, unit="s", utc=True).strftime("%Y-%m-%d")
    names = [lut.get(d, "nan|nan") for d in days]
    code = {u: i for i, u in enumerate(sorted(set(names)))}
    return np.array([-1 if "nan" in x else code[x] for x in names], dtype=np.int64)


def run_variant(use_phase, Zr, vr, fwd, qe, split_e, ph, r, rng):
    """Real result plus RW-surrogate and SHUF control summaries for one variant."""
    nb_real = neighbours(Zr, vr, np.isfinite(fwd), Zr, qe, ph, use_phase)
    ans, pos = decide(nb_real, fwd)
    taken, net, hit = trade_net(pos, qe, fwd)
    real = summarise(net, hit, taken, qe, split_e)
    real.update(forecasts=int(ans.sum()), forecastsA=int((ans & (qe < split_e)).sum()),
                forecastsB=int((ans & (qe >= split_e)).sum()), net=net, taken=taken, pos=pos)
    shuf = []
    for _ in range(DRAWS):
        fs = shuffled_fwd(fwd, BLOCK, rng)
        _, p2 = decide(nb_real, fs)
        t2, n2, h2 = trade_net(p2, qe, fwd)
        shuf.append(summarise(n2, h2, t2, qe, split_e))
    rw = []
    for d in range(DRAWS):
        rs = surrogate_returns(r, np.random.default_rng(SEED * 1000 + d))
        Zs, vs = z_windows(rs)
        fs = forward_log(rs)
        nb = neighbours(Zs, vs, np.isfinite(fs), Zr, qe, ph, use_phase)
        _, p2 = decide(nb, fs)
        t2, n2, h2 = trade_net(p2, qe, fwd)
        rw.append(summarise(n2, h2, t2, qe, split_e))
    return real, shuf, rw


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "output.md")
    rng = np.random.default_rng(SEED)
    t, close = load_bars()
    r = log_returns(close)
    Zr, vr, fwd, qe = make_queries(r)
    ph = phase_codes(t)
    split_e = qe[len(qe) // 2]
    sd24 = trailing_std(r) * np.sqrt(24) * 100.0
    weeks = (t[qe] // (7 * 86400)).astype(np.int64)
    lines = [f"# F3 output (DEV 2022-01-01..2025-06-30; {len(qe)} non-overlapping queries; split at {pd.Timestamp(int(t[split_e]), unit='s')})", ""]
    res = {}
    for name, use_phase in (("UNFILT", False), ("PHASE", True)):
        res[name] = run_variant(use_phase, Zr, vr, fwd, qe, split_e, ph, r, rng)
        print(name, "done", flush=True)
    rows = ["variant,time,side,net_pct,split"]   # percent only, no prices (read by sim_desk/fractals_export.py)
    for name in ("UNFILT", "PHASE"):
        rl = res[name][0]
        for k in np.flatnonzero(rl["taken"]):
            ts = pd.Timestamp(int(t[qe[k]]), unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
            rows.append(f"{name},{ts},{'long' if rl['pos'][k] > 0 else 'short'},{rl['net'][k]:.6f},{'A' if qe[k] < split_e else 'B'}")
    with open(os.path.join(HERE, "trades_pct.csv"), "w", newline=chr(10)) as f:
        f.write(chr(10).join(rows) + chr(10))
    keys, p_all = [], []
    for name in ("UNFILT", "PHASE"):
        real, shuf, rw = res[name]
        for cname, ctl in (("RW", rw), ("SHUF", shuf)):
            cm = np.array([c["mean"] for c in ctl], dtype=float)
            cm = cm[np.isfinite(cm)]
            p_all.append((1 + (cm >= real["mean"]).sum()) / (1 + len(cm)))
            keys.append((name, cname, cm))
    adj = holm(p_all)
    boot_rng = np.random.default_rng(SEED)
    lines.append("| variant | forecasts (A/B) | trades n | hit | net %/trade | R/trade | week-boot 95% CI | control | control mean [2.5,97.5] | p | Holm p | meanA | meanB |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    ci = {}
    for i, (name, cname, cm) in enumerate(keys):
        real = res[name][0]
        tk = real["taken"]
        nets = real["net"][tk]
        if name not in ci:
            ci[name] = week_bootstrap(nets, weeks[tk], boot_rng)
        lo, hi = ci[name]
        rr = float(np.mean(nets / sd24[qe][tk]))
        lines.append(f"| {name} | {real['forecasts']} ({real['forecastsA']}/{real['forecastsB']}) | {real['n']} | {real['hit']:.3f} | {real['mean']:.4f} | {rr:.3f} | [{lo:.4f}, {hi:.4f}] | {cname} | {cm.mean():.4f} [{np.percentile(cm, 2.5):.4f}, {np.percentile(cm, 97.5):.4f}] | {p_all[i]:.4f} | {adj[i]:.4f} | {real['meanA']:.4f} (n {real['nA']}) | {real['meanB']:.4f} (n {real['nB']}) |")
    for j, name in enumerate(("UNFILT", "PHASE")):
        real = res[name][0]
        lo, hi = ci[name]
        decid = real["n"] >= 200 and real["forecastsA"] >= 500 and real["forecastsB"] >= 500
        passed = real["mean"] > 0 and adj[2 * j] < 0.05 and adj[2 * j + 1] < 0.05 and real["meanA"] > 0 and real["meanB"] > 0
        if not decid:
            v = "NOT_DECIDABLE"
        elif passed:
            v = "PASS"
        elif hi < 0:
            v = "FAIL"
        else:
            v = "INCONCLUSIVE"
        sd = float(np.std(real["net"][real["taken"]]))
        lines.append("")
        lines.append(f"{name}: verdict {v}; sd of net %/trade {sd:.3f}; trades needed to see 0.10 % at 80 % power: {harness.power_n(sd, 0.10)}")
    u, p_ = res["UNFILT"][0], res["PHASE"][0]
    nu, npv = u["net"][u["taken"]], p_["net"][p_["taken"]]
    wu, wp = weeks[u["taken"]], weeks[p_["taken"]]
    allw = np.unique(np.concatenate([wu, wp]))
    brng = np.random.default_rng(SEED)
    ds = []
    for _ in range(BOOT):
        pick = brng.choice(allw, len(allw), replace=True)
        a = np.concatenate([nu[wu == w] for w in pick])
        b = np.concatenate([npv[wp == w] for w in pick])
        if len(a) and len(b):
            ds.append(b.mean() - a.mean())
    lines.append("")
    lines.append(f"PHASE minus UNFILT pooled net %/trade: {p_['mean'] - u['mean']:.4f}, week-boot 95% CI [{np.percentile(ds, 2.5):.4f}, {np.percentile(ds, 97.5):.4f}] (descriptive, no verdict)")
    with open(out, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
