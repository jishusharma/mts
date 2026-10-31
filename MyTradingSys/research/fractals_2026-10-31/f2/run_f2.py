"""F2: rolling 1h DFA Hurst regime gate on RSI-DIV-MTF and the F1 pivot fade, fee-net. See PRE_REG.md (frozen before the run).

DEV 2022-01-01..2025-06-30 only; files after 2025-06 are never opened.
Usage: python run_f2.py [out_dir]
"""
import importlib.util
import itertools
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F1_DIR = os.path.join(HERE, "..", "f1")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "MyTradingSys", "backtest"))
sys.path.insert(0, os.path.join(HERE, "..", "phase_tag"))
import harness  # noqa: E402
import hseries  # noqa: E402

THR_A = 0.45      # keep H < THR_A (mean-reverting regime)
THR_B = 0.55      # keep H <= THR_B (drop the trending regime)
SEED = 31
NPERM = 1000
BOOT = 2000
MIN_RUN = 24      # hours; shorter state runs do not count as a regime
SPLIT_TS = int(pd.Timestamp("2023-10-01", tz="UTC").timestamp())
START_TS = int(pd.Timestamp("2022-01-01", tz="UTC").timestamp())
PLANT = 0.25      # R added to kept events in the planted-edge check
TESTS = [("F2-1", "RSI-DIV-MTF", "A"), ("F2-2", "RSI-DIV-MTF", "B"), ("F2-3", "FADE", "A"), ("F2-4", "FADE", "B")]


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def kept_mask(h, which):
    """Gate: A keeps H < 0.45, B keeps H <= 0.55. NaN H never gets here (events without H are dropped first)."""
    return (h < THR_A) if which == "A" else (h <= THR_B)


def lift(y, kept):
    if kept.all() or not kept.any():
        return float("nan")
    return float(y[kept].mean() - y[~kept].mean())


def lookup_idx(avail, t):
    """Index of the latest H whose availability (bar open + 3600) is <= the event second t; -1 if none."""
    return np.searchsorted(avail, t, side="right") - 1


def state_switches(h, avail, which, lo_ts, hi_ts):
    """Switches between kept/removed state on the hourly H series in [lo_ts, hi_ts): runs of >= MIN_RUN hours count."""
    sel = (avail >= lo_ts) & (avail < hi_ts) & ~np.isnan(h)
    s = kept_mask(h[sel], which)
    if len(s) == 0:
        return 0
    runs = np.array([len(list(g)) for _, g in itertools.groupby(s.tolist())])
    return max(0, int((runs >= MIN_RUN).sum()) - 1)


def null_lifts(ev, h_series, avail_idx):
    """Lift of each test with the H series swapped for `h_series` (same event set and times)."""
    out = []
    for (_, layer, which) in TESTS:
        y, idx = ev[layer]
        out.append(lift(y, kept_mask(h_series[idx], which)))
    return np.array(out)


def run_nulls(ev, h_full, valid, rng):
    """C1 shuffled-H, C2 random gate (per test), C3 circular-shift (family-wise). Returns dict of arrays."""
    nv = int(valid.sum())
    hv = h_full[valid]
    c1 = np.empty((NPERM, len(TESTS)))
    c3 = np.empty((NPERM, len(TESTS)))
    for b in range(NPERM):
        hs = h_full.copy()
        hs[valid] = rng.permutation(hv)
        c1[b] = null_lifts(ev, hs, None)
        k = int(rng.integers(1, nv))
        hr = h_full.copy()
        hr[valid] = np.roll(hv, k)
        c3[b] = null_lifts(ev, hr, None)
    return c1, c3


def run_c2(ev, h_full, obs_kept_n, rng):
    c2 = np.empty((NPERM, len(TESTS)))
    for j, (_, layer, which) in enumerate(TESTS):
        y, _ = ev[layer]
        for b in range(NPERM):
            m = np.zeros(len(y), bool)
            m[rng.permutation(len(y))[: obs_kept_n[j]]] = True
            c2[b, j] = lift(y, m)
    return c2


def pval(null, obs):
    return float((1 + (null >= obs).sum()) / (1 + len(null)))


def demeaned_by_cell(y, kept):
    z = y.astype(float).copy()
    z[kept] -= z[kept].mean()
    z[~kept] -= z[~kept].mean()
    return z


def analyse(ev, ts, h_full, avail, out_dir, f1m):
    lines = []
    valid = ~np.isnan(h_full)
    rng = np.random.default_rng(SEED)
    # observed
    obs, rows, kept_n = [], [], []
    for (tid, layer, which) in TESTS:
        y, idx = ev[layer]
        k = kept_mask(h_full[idx], which)
        obs.append(lift(y, k))
        kept_n.append(int(k.sum()))
    obs = np.array(obs)
    c1, c3 = run_nulls(ev, h_full, valid, rng)
    c2 = run_c2(ev, h_full, kept_n, rng)
    null_max = c3.max(axis=1)
    thr95 = float(np.quantile(null_max, 0.95))
    lines.append("| test | layer | gate | n kept | n removed | kept mean R [95% CI] | removed mean R | lift [95% CI] | S1 lift | S2 lift | switches S1/S2 | C1 p | C2 p | C3 flag | verdict |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    verdicts = {}
    res = {}
    for j, (tid, layer, which) in enumerate(TESTS):
        y, idx = ev[layer]
        t = ts[layer]
        k = kept_mask(h_full[idx], which)
        d, dlo, dhi = f1m.week_boot(t[k], y[k], t[~k], y[~k], B=BOOT, seed=SEED)
        km, klo, khi = f1m.week_boot(t[k], y[k], B=BOOT, seed=SEED)
        s1 = t < SPLIT_TS
        l1 = lift(y[s1], k[s1])
        l2 = lift(y[~s1], k[~s1])
        sw1 = state_switches(h_full, avail, which, START_TS, SPLIT_TS)
        sw2 = state_switches(h_full, avail, which, SPLIT_TS, hseries.END_TS)
        p1 = pval(c1[:, j], obs[j])
        p2 = pval(c2[:, j], obs[j])
        flag = bool(obs[j] > thr95)
        nk, nr = int(k.sum()), int((~k).sum())
        if nk < 200 or nr < 30:
            v = "NOT_DECIDABLE"
        elif dhi < 0:
            v = "FAIL"
        elif dlo > 0 and sw1 >= 10 and sw2 >= 10 and l1 > 0 and l2 > 0 and p1 < 0.05 and p2 < 0.05 and flag:
            v = "PASS_LIFT"
        else:
            v = "INCONCLUSIVE"
        verdicts[tid] = v
        res[tid] = dict(n_kept=nk, n_rem=nr, kept=km, lift=d, lo=dlo, hi=dhi, p1=p1, p2=p2, flag=flag, v=v, sw1=sw1, sw2=sw2, l1=l1, l2=l2)
        lines.append(f"| {tid} | {layer} | {which} | {nk} | {nr} | {km:+.4f} [{klo:+.4f}, {khi:+.4f}] | {y[~k].mean():+.4f} | {d:+.4f} [{dlo:+.4f}, {dhi:+.4f}] | {l1:+.4f} | {l2:+.4f} | {sw1}/{sw2} | {p1:.3f} | {p2:.3f} | {'yes' if flag else 'no'} | {v} |")
    lines += ["", f"C3 family-wise: 95th percentile of the null max lift over 4 tests = {thr95:+.4f} R (1,000 circular shifts of the H series, seed {SEED}). Observed lifts: " + ", ".join(f"{TESTS[j][0]} {obs[j]:+.4f}" for j in range(len(TESTS))) + "."]
    # planted-edge check (cells demeaned first, same pipeline, same nulls). Scenario 1 is the pre-registered one.
    base = {}
    for L in ev:
        y, idx = ev[L]
        base[L] = (demeaned_by_cell(y, kept_mask(h_full[idx], "A")), idx)
    scen = [("no plant", {}), ("plant +0.25 R on RSI A kept (pre-registered)", {"RSI-DIV-MTF": 0.25}),
            ("plant +0.50 R on RSI A kept (extra, diagnostic)", {"RSI-DIV-MTF": 0.50}),
            ("plant +0.25 R on FADE A kept (extra, diagnostic)", {"FADE": 0.25})]
    pl = {}
    lines += ["", "Planted edge (cells demeaned first on gate A; real H and event times; same C3 nulls):"]
    for name, amt in scen:
        e = {}
        for L, (z, idx) in base.items():
            zz = z.copy()
            if L in amt:
                zz[kept_mask(h_full[idx], "A")] += amt[L]
            e[L] = (zz, idx)
        rng2 = np.random.default_rng(SEED + 1)
        o = null_lifts(e, h_full, None)
        nm = np.empty(NPERM)
        for b in range(NPERM):
            hr = h_full.copy()
            hr[valid] = np.roll(h_full[valid], int(rng2.integers(1, int(valid.sum()))))
            nm[b] = null_lifts(e, hr, None).max()
        th = float(np.quantile(nm, 0.95))
        fl = [TESTS[j][0] for j in range(len(TESTS)) if o[j] > th]
        cis = []
        for L in amt:
            j = [q for q, tt in enumerate(TESTS) if tt[1] == L and tt[2] == "A"][0]
            yy, idx = e[L]
            kk = kept_mask(h_full[idx], "A")
            tt_ = ts[L]
            d, lo, hi = f1m.week_boot(tt_[kk], yy[kk], tt_[~kk], yy[~kk], B=BOOT, seed=SEED)
            cis.append(f"{TESTS[j][0]} CI [{lo:+.3f}, {hi:+.3f}]")
        pl[name] = (fl, th, o)
        lines.append(f"- {name}: C3 threshold {th:+.4f}; lifts " + ", ".join(f"{TESTS[j][0]} {o[j]:+.3f}" for j in range(len(TESTS))) + f"; flagged {fl}" + ("; " + ", ".join(cis) if cis else "") + ".")
    sd = float(np.std(ev["RSI-DIV-MTF"][0], ddof=1))
    sd2 = float(np.std(ev["FADE"][0], ddof=1))
    lines += ["", f"Power: sd of net R per event RSI-DIV-MTF {sd:.3f}, FADE {sd2:.3f}; n per cell for a 0.17 R effect at 80 % power: RSI {harness.power_n(sd, 0.17)}, FADE {harness.power_n(sd2, 0.17)}."]
    anyp = any(v == "PASS_LIFT" for v in verdicts.values())
    overall = "PASS" if anyp else "NEGATIVE"
    lines += ["", f"F2 overall: {overall}."]
    return lines, verdicts, res, pl, overall


def main(out_dir=None):
    out_dir = out_dir or "F:/MTS/runs/fractal_f2"
    os.makedirs(out_dir, exist_ok=True)
    tfb = hseries.load_tfb()
    df = tfb.load()
    hs = hseries.build(df)
    avail = hs["avail"].to_numpy(np.int64)
    h_full = hs["h"].to_numpy(float)
    f1 = load_mod("run_f1", os.path.join(F1_DIR, "run_f1.py"))
    evf, _ = f1.build_events(df)
    fade = evf[evf.kind == "real"].sort_values("t")
    rsi = pd.read_csv(os.path.join(HERE, "..", "p1b_rsi_feenet", "events_feenet.csv"))
    rsi["ts"] = (pd.to_datetime(rsi["time"], utc=True) - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
    raw = {"RSI-DIV-MTF": (rsi["ts"].to_numpy(np.int64), rsi["r_net"].to_numpy(float)),
           "FADE": (fade["t"].to_numpy(np.int64), fade["net_r"].to_numpy(float))}
    ev, ts, dropped = {}, {}, {}
    for L, (t, y) in raw.items():
        idx = lookup_idx(avail, t)
        ok = idx >= 0
        ok[ok] = ~np.isnan(h_full[idx[ok]])
        dropped[L] = int((~ok).sum())
        ev[L] = (y[ok], idx[ok])
        ts[L] = t[ok]
    lines, verdicts, res, pl, overall = analyse(ev, ts, h_full, avail, out_dir, f1)
    head = [f"F2 run: H hours valid {int((~np.isnan(h_full)).sum())} of {len(h_full)}; events kept / dropped for no H: " +
            ", ".join(f"{L} {len(ev[L][0])} / {dropped[L]}" for L in ev) + ".", ""]
    text = "\n".join(head + lines)
    with open(os.path.join(HERE, "output.md"), "w", newline="\n") as fh:
        fh.write(text + "\n")
    print(text)
    return overall


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
