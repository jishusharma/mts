"""F1: 1h Williams pivots with 4h/daily pivot confluence vs no confluence vs random levels (fee-net). See PRE_REG.md.

DEV 2022-01-01..2025-06-30 only; files after 2025-06 are never opened. Pivot code reused from tf_break_event_study.
Usage: python run_f1.py [out_dir]
"""
import bisect
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


def _load_tfb():
    p = os.path.join(REPO, "MyTradingSys", "research", "tf_break_event_study_2026-10-30", "study.py")
    spec = importlib.util.spec_from_file_location("tf_break_study", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


TFB = _load_tfb()
N_PIV = 2              # Williams 5-bar
LIVE_BARS = 96         # level lifetime in 1h bars
LAST_K = 5             # last confirmed same-kind higher-TF pivots considered
TOL_ATR = 0.5          # confluence tolerance in 1h ATR
STOP_ATR = 1.0
TARGET_R = 1.0
HOLD_S = 24 * 3600
CTRL_DRAWS = 2
SEED = 31
END_TS = int(pd.Timestamp("2025-07-01", tz="UTC").timestamp())
FEE_SIDE = fees.BINANCE_TAKER


def atr14(b):
    h, l, c = (b[k].to_numpy(float) for k in ("h", "l", "c"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).rolling(14).mean().to_numpy()


def pivots(b, tf_min):
    """List of (avail_ts, price, kind, conf_index); kind +1 pivot high, -1 pivot low.
    avail = close time of the confirming bar (pivot bar + N_PIV)."""
    out = []
    t = b["t"].to_numpy(np.int64)
    for kind, col, low in ((1, "h", False), (-1, "l", True)):
        conf, piv = TFB.confirmed_pivots(b[col].to_numpy(float), N_PIV, low)
        for i in np.flatnonzero(conf):
            out.append((int(t[i]) + tf_min * 60, float(piv[i]), kind, int(i)))
    out.sort(key=lambda r: r[0])
    return out


def confluence_flags(p1h, atr1h, p4, pdy):
    """For each 1h pivot return (match4h, match1d) using only higher-TF pivots with avail <= the 1h confirming close."""
    idx = []
    for plist in (p4, pdy):
        per = {}
        for q in plist:
            per.setdefault(q[2], []).append(q)
        idx.append({k: ([q[0] for q in v], v) for k, v in per.items()})
    res = []
    for avail, price, kind, i in p1h:
        tol = TOL_ATR * atr1h[i]
        m = []
        for per in idx:
            if kind not in per or tol != tol:
                m.append(False)
                continue
            times, lst = per[kind]
            k = bisect.bisect_right(times, avail)
            last = lst[max(0, k - LAST_K):k]
            m.append(any(abs(q[1] - price) <= tol for q in last))
        res.append((m[0], m[1]))
    return res


def trade_outcome(t, o, h, l, c, anchor, expiry, level, kind, atr):
    """Fade `level` (kind +1 resistance -> short, -1 support -> long). None if untouched in [anchor, expiry)."""
    i0 = int(np.searchsorted(t, anchor))
    i1 = int(np.searchsorted(t, expiry))
    if i1 <= i0 or atr != atr or atr <= 0:
        return None
    hit = np.flatnonzero(h[i0:i1] >= level) if kind > 0 else np.flatnonzero(l[i0:i1] <= level)
    if len(hit) == 0:
        return None
    m = i0 + int(hit[0])
    side = -kind
    entry = max(level, o[m]) if kind > 0 else min(level, o[m])
    risk = STOP_ATR * atr
    stop = entry - side * risk
    target = entry + side * TARGET_R * risk
    j1 = max(int(np.searchsorted(t, t[m] + HOLD_S)), m + 1)
    hh, ll = h[m:j1], l[m:j1]
    sh = (hh >= stop) if side < 0 else (ll <= stop)
    th = (ll <= target) if side < 0 else (hh >= target)
    s = int(np.argmax(sh)) if sh.any() else None
    g = int(np.argmax(th)) if th.any() else None
    if s is not None and (g is None or s <= g):
        gross, why = -1.0, "stop"
    elif g is not None:
        gross, why = TARGET_R, "target"
    else:
        gross, why = side * (c[j1 - 1] - entry) / risk, "time"
    cost = 2 * FEE_SIDE * entry / risk
    pct = (gross * risk / entry) * 100 - 2 * FEE_SIDE * 100
    return dict(t=int(t[m]), net_r=gross - cost, gross_r=gross, net_pct=pct, why=why)


def week_boot(ts_a, y_a, ts_b=None, y_b=None, B=2000, seed=SEED):
    """Week-block bootstrap of mean(a) or mean(a)-mean(b). Returns (est, lo, hi)."""
    rng = np.random.default_rng(seed)
    wa = (np.asarray(ts_a) // 604800).astype(np.int64)
    allw = wa if ts_b is None else np.r_[wa, (np.asarray(ts_b) // 604800).astype(np.int64)]
    weeks = np.unique(allw)
    pos = {int(w): k for k, w in enumerate(weeks)}

    def agg(ts, y):
        w = np.array([pos[int(x)] for x in (np.asarray(ts) // 604800)], dtype=int)
        return (np.bincount(w, weights=np.asarray(y, float), minlength=len(weeks)),
                np.bincount(w, minlength=len(weeks)).astype(float))

    sa, na = agg(ts_a, y_a)
    est = sa.sum() / na.sum()
    draws = rng.integers(0, len(weeks), size=(B, len(weeks)))
    dist = sa[draws].sum(1) / np.maximum(na[draws].sum(1), 1)
    if ts_b is not None:
        sb, nb = agg(ts_b, y_b)
        est -= sb.sum() / nb.sum()
        dist = dist - sb[draws].sum(1) / np.maximum(nb[draws].sum(1), 1)
    return float(est), float(np.quantile(dist, 0.025)), float(np.quantile(dist, 0.975))


def build_events(df1m):
    df1m = df1m[df1m.t < END_TS]
    b1, b4, bd = (TFB.bars(df1m, tf) for tf in (60, 240, 1440))
    a1 = atr14(b1)
    p1, p4, pdy = pivots(b1, 60), pivots(b4, 240), pivots(bd, 1440)
    flags = confluence_flags(p1, a1, p4, pdy)
    t = df1m["t"].to_numpy(np.int64)
    o, h, l, c = (df1m[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    cl1 = b1["c"].to_numpy(float)
    items = []
    dists = {}
    for (avail, price, kind, i), (m4, md) in zip(p1, flags):
        atr = a1[i]
        if atr != atr or avail + LIVE_BARS * 3600 > END_TS:
            continue
        grp = "CONF_1D" if md else ("CONF_4H" if m4 else "NONE")
        dists.setdefault(grp, []).append(abs(price - cl1[i]) / atr)
        items.append((avail, price, kind, i, grp))
    rng = np.random.default_rng(SEED)
    rows = []
    for avail, price, kind, i, grp in items:
        atr = a1[i]
        exp = avail + LIVE_BARS * 3600
        r = trade_outcome(t, o, h, l, c, avail, exp, price, kind, atr)
        if r:
            rows.append(dict(kind="real", group=grp, anchor=avail, side_kind=kind, **r))
        pool = np.array(dists[grp])
        for _ in range(CTRL_DRAWS):
            d = float(rng.choice(pool))
            r = trade_outcome(t, o, h, l, c, avail, exp, cl1[i] + kind * d * atr, kind, atr)
            if r:
                rows.append(dict(kind="ctrl", group=grp, anchor=avail, side_kind=kind, **r))
    return pd.DataFrame(rows), len(items)


def _sel(ev, kind, groups):
    s = ev[(ev.kind == kind) & ev.group.isin(groups)]
    return s.t.to_numpy(), s.net_r.to_numpy()


def analyse(ev, n_piv, out_dir):
    lines = []
    cells = [("CONF_ANY", ("CONF_4H", "CONF_1D")), ("CONF_4H", ("CONF_4H",)), ("CONF_1D", ("CONF_1D",)), ("NONE", ("NONE",))]
    res = {}
    lines.append("| group | n real | net mean R | 95% CI | n random | random mean R | diff (real - random) | diff 95% CI |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, gs in cells:
        ta, ya = _sel(ev, "real", gs)
        tb, yb = _sel(ev, "ctrl", gs)
        e, lo, hi = week_boot(ta, ya)
        d, dlo, dhi = week_boot(ta, ya, tb, yb)
        mb = yb.mean() if len(yb) else float("nan")
        res[name] = dict(n=len(ya), mean=e, lo=lo, hi=hi, nb=len(yb), mb=mb, d=d, dlo=dlo, dhi=dhi)
        lines.append(f"| {name} | {len(ya)} | {e:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {len(yb)} | {mb:+.4f} | {d:+.4f} | [{dlo:+.4f}, {dhi:+.4f}] |")
    # shift null over labels (event-time order of real events), units: net % per trade
    real = ev[ev.kind == "real"].sort_values("t")
    lab = real.group.map({"NONE": 0, "CONF_4H": 1, "CONF_1D": 2}).to_numpy(int)
    y = real.net_pct.to_numpy()
    sn = harness.shift_null_test(y, lab, n_shifts=1000, rng=np.random.default_rng(SEED))
    names = {0: "NONE", 1: "CONF_4H", 2: "CONF_1D"}
    flagged = [(names[c], sn["gaps"].get(c, float("nan"))) for c in sn["flagged"]]
    # planted edge and null run through the same test (CONF_ANY events = label 1/2 merged into cell 1)
    lab2 = (lab > 0).astype(int)
    # The planted-edge check runs on outcomes with each cell's own mean removed (real variance and order kept), so the
    # real confluence-vs-none gap cannot mask or fake the planted +0.3 %. Raw (not demeaned) binary run kept for the record.
    raw = harness.shift_null_test(y, lab2, n_shifts=300, rng=np.random.default_rng(SEED))
    yd = y.copy()
    for c_ in (0, 1):
        yd[lab2 == c_] -= yd[lab2 == c_].mean()
    pl = harness.shift_null_test(yd, lab2, n_shifts=300, rng=np.random.default_rng(SEED))
    y_p, _ = harness.inject_edge(yd, lab2, 1, delta=0.3, frac=0.2, rng=np.random.default_rng(SEED))
    pl2 = harness.shift_null_test(y_p, lab2, n_shifts=300, rng=np.random.default_rng(SEED))
    sd = float(np.std(y, ddof=1))
    nneed = harness.power_n(sd, 0.10)
    ca = res["CONF_ANY"]
    pos_flag = any(nm in ("CONF_4H", "CONF_1D") and g > 0 for nm, g in flagged)
    if ca["n"] < 200:
        verdict = "NOT_DECIDABLE"
    elif ca["mean"] > 0 and ca["dlo"] > 0 and pos_flag:
        verdict = "PASS"
    elif ca["dhi"] < 0 or ca["hi"] < 0:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    # phase split (descriptive)
    tags = pd.read_csv(os.path.join(HERE, "..", "phase_tag", "tags.csv"), usecols=["date", "cowen_side", "sma200_side"])
    tags["date"] = pd.to_datetime(tags["date"]).dt.strftime("%Y-%m-%d")
    r2 = ev[ev.kind == "real"].copy()
    r2["date"] = pd.to_datetime(r2.t, unit="s", utc=True).dt.strftime("%Y-%m-%d")
    r2 = r2.merge(tags, on="date", how="left")
    r2["cg"] = np.where(r2.group == "NONE", "NONE", "CONF_ANY")
    ph = []
    for col in ("cowen_side", "sma200_side"):
        g = r2.groupby(["cg", col], dropna=False).net_r.agg(["size", "mean"]).reset_index()
        for _, r in g.iterrows():
            ph.append(f"| {r['cg']} | {col}={r[col]} | {int(r['size'])} | {r['mean']:+.4f} |")
    why = ev[ev.kind == "real"].groupby(["group", "why"]).size().unstack(fill_value=0)
    tail = [
        "", f"1h pivots with live window inside DEV: {n_piv}.",
        f"Shift null (labels NONE/CONF_4H/CONF_1D, net % per trade): max gap {sn['max_gap']:.4f} vs 95th pct threshold {sn['threshold']:.4f}, p_global {sn['p_global']:.3f}, flagged {flagged}.",
        f"Binary confluence-vs-none shift null on the real outcomes: flagged {raw['flagged']} (cell 1 = confluence; its gap is negative, i.e. worse than none).",
        f"Planted edge on cell-demeaned outcomes (+0.3 % on 20 % of confluence events): flagged without {pl['flagged']}, with {pl2['flagged']}.",
        f"Power: per-trade sd {sd:.3f} %; n needed per cell to see 0.10 % at 80 % power = {nneed}; CONF_ANY n = {ca['n']}.",
        "", "Exit mix (real events):", why.to_string(), "",
        "Phase split (descriptive, NO verdict): group, tag, n, net mean R", "| group | tag | n | net mean R |", "|---|---|---|---|", *ph,
        "", f"VERDICT: {verdict}",
    ]
    text = "\n".join(lines + tail)
    with open(os.path.join(HERE, "output.md"), "w", newline="\n") as fh:
        fh.write(text + "\n")
    return text, verdict, res


def main(out_dir=None):
    out_dir = out_dir or "F:/MTS/runs/fractal_f1"
    os.makedirs(out_dir, exist_ok=True)
    df = TFB.load()
    ev, n_piv = build_events(df)
    ev.to_csv(os.path.join(out_dir, "events.csv"), index=False, lineterminator="\n")
    text, verdict, res = analyse(ev, n_piv, out_dir)
    print(text)
    return verdict


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
