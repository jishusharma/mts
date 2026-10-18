"""Gross-effect screen, DEV only. Rules: PRE_REG.md (frozen 2026-10-15). Nothing here chooses a parameter.

Usage: python screen.py --count | --full
Global bar index i = (open_time - TS0) / 60000 over DEV 2022-01-01 .. 2024-06-30; the loader refuses any bar >= CUTOFF.
Implementation decisions (OURS, conservative, logged in RESULT.md):
 - verdict statistics use G minus funding (funding NOT_IN_DATA -> 1 bp per straddling encounter);
 - an exit beyond the last DEV bar is NaN (VALIDATION is never read) and counted as dropped;
 - MDD of the arm is the peak-to-trough of cumulative net % of one clip (sum of encounter nets), BH MDD is in % of price;
 - INCONCLUSIVE is tested on n_T after PASS_FLOW and PASS_CONTROL, literal reading of section 4.
"""
import csv
import datetime as dt
import hashlib
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCH = Path("F:/MTS/data/tom_raw/klines")
DAYMIN = 1440
MS = 60_000
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
NDAYS_DEV = (dt.date(2024, 7, 1) - dt.date(2022, 1, 1)).days          # 912
DS = (0, 1, 2, 5, 15)
HS = (5, 15, 30, 60, 120, 240)
PRIMARY = (1, 60)
C_PCT = 0.14
CM_PCT = 0.09
FUND_PCT = 0.01
TICK = 0.1
N_MIN = 200
CLIP = 1000.0


def delta(v, tbv):
    return 2.0 * np.asarray(tbv, float) - np.asarray(v, float)


# ---------------------------------------------------------------- data
def load_dev(files, ts0=TS0, cutoff=CUTOFF_MS, ndays=NDAYS_DEV):
    n = ndays * DAYMIN
    A = {k: np.full(n, np.nan) for k in ("O", "H", "L", "C", "V", "TBV", "QV")}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= cutoff:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT are sealed): {f}")
                i = (t - ts0) // MS
                if 0 <= i < n:
                    A["O"][i], A["H"][i], A["L"][i], A["C"][i] = float(r[1]), float(r[2]), float(r[3]), float(r[4])
                    A["V"][i], A["QV"][i], A["TBV"][i] = float(r[5]), float(r[7]), float(r[9])
    return A


def dev_files():
    out = []
    for y, m in [(2022, i) for i in range(1, 13)] + [(2023, i) for i in range(1, 13)] + [(2024, i) for i in range(1, 7)]:
        out.append(ARCH / f"BTCUSDT-1m-{y}-{m:02d}.csv")
    return out


# ---------------------------------------------------------------- ledger
def apply_cooldown(cands, cd=60):
    last = {}
    out = []
    for idx, side in sorted(cands):
        if side in last and idx - last[side] <= cd:
            continue
        last[side] = idx
        out.append((idx, side))
    return out


def col_percentile(ref, q):
    """np.nanpercentile(ref, q, axis=0) (linear method, NaN where a column has no value) from one sort.
    nanpercentile loops over the 1440 columns in Python: 90 s for a 330-day ledger, about 1 s here."""
    s = np.sort(ref, axis=0)                                       # NaN sorts last
    cnt = (~np.isnan(ref)).sum(0)
    v = np.maximum(cnt - 1, 0) * (q / 100)
    lo = np.floor(v).astype(np.int64)
    hi = np.minimum(lo + 1, np.maximum(cnt - 1, 0))
    t = v - lo
    cols = np.arange(ref.shape[1])
    a, b = s[lo, cols], s[hi, cols]
    d = b - a
    out = a + d * t
    np.subtract(b, d * (1 - t), out=out, where=t >= 0.5)           # numpy's own two-sided lerp
    return np.where(cnt > 0, out, np.nan)


def build_ledger(A, ndays):
    O, H, L, V, TBV = A["O"], A["H"], A["L"], A["V"], A["TBV"]
    dl = delta(V, TBV)
    j = np.arange(DAYMIN)
    legs = np.full((ndays, DAYMIN), np.nan)
    st = []
    for i in range(ndays):
        s = slice(i * DAYMIN, (i + 1) * DAYMIN)
        o, h, l = O[s], H[s], L[s]
        bad = np.isnan(o) | np.isnan(h) | np.isnan(l) | np.isnan(dl[s])
        pv = np.cumsum(bad) == 0                                   # prefix of complete bars
        hf = np.where(bad, -np.inf, h)
        lf = np.where(bad, np.inf, l)
        hmax = np.maximum.accumulate(hf)
        lmin = np.minimum.accumulate(lf)
        leg = (hmax - lmin) / o[0] if not np.isnan(o[0]) else np.full(DAYMIN, np.nan)
        leg = np.where(pv, leg, np.nan)
        legs[i] = leg
        newh = hf > np.concatenate(([-np.inf], hmax[:-1]))
        newl = lf < np.concatenate(([np.inf], lmin[:-1]))
        seth = np.maximum.accumulate(np.where(newh, j, -1))
        setl = np.maximum.accumulate(np.where(newl, j, -1))
        cs = np.cumsum(np.where(bad, 0.0, dl[s]))
        d5 = cs - np.concatenate((np.zeros(5), cs[:-5]))
        st.append((pv, seth, setl, d5))
    cands, info = [], {}
    for i in range(ndays):
        pv, seth, setl, d5 = st[i]
        ref = legs[max(0, i - 20):i]
        if len(ref) == 0:
            continue
        cnt = (~np.isnan(ref)).sum(0)
        thr = col_percentile(ref, 80)
        ok =(cnt >= 15) & ~np.isnan(thr) & pv & (j >= 60) & (legs[i] >= np.where(np.isnan(thr), np.inf, thr))
        short = ok & (seth >= j - 2) & (setl < seth)
        long_ = ok & (setl >= j - 2) & (seth < setl)
        for side, m in ((-1, short), (1, long_)):
            for jj in np.nonzero(m)[0]:
                g = i * DAYMIN + int(jj)
                cands.append((g, side))
                info[(g, side)] = (float(d5[jj]), float(legs[i][jj]))
    elig = apply_cooldown(cands, 60)
    t = np.array([e[0] for e in elig], dtype=np.int64)
    side = np.array([e[1] for e in elig], dtype=np.int64)
    d5 = np.array([info[e][0] for e in elig])
    leg = np.array([info[e][1] for e in elig])
    F = np.where(side == -1, d5 < 0, d5 > 0)
    return dict(t=t, side=side, D5=d5, leg=leg, F=F, day=t // DAYMIN, j=t % DAYMIN)


def compute_cells(A, led, ndays):
    O, H, L = A["O"], A["H"], A["L"]
    n = len(O)
    t, side = led["t"], led["side"]
    G, FUND, FILL, PIN = {}, {}, {}, {}
    for d in DS:
        e = t + 1 + d
        pin = np.where(e < n, O[np.minimum(e, n - 1)], np.nan)
        PIN[d] = pin
        # maker: first bar after the entry bar that trades through p_in by one tick in the entry's favour
        k = np.arange(1, max(HS) + 1)
        idx = e[:, None] + k[None, :]
        inb = idx < n
        ii = np.minimum(idx, n - 1)
        hi = np.where(inb, H[ii], np.nan)
        lo = np.where(inb, L[ii], np.nan)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hit = np.where(side[:, None] == -1, hi >= pin[:, None] + TICK - 1e-9, lo <= pin[:, None] - TICK + 1e-9)
        hit = hit & ~np.isnan(hi)
        first = np.where(hit.any(1), hit.argmax(1) + 1, 10 ** 6)      # k of the first trade-through
        for h in HS:
            x = e + h
            pout = np.where(x < n, O[np.minimum(x, n - 1)], np.nan)
            G[(d, h)] = side * (pout / pin - 1.0) * 100.0
            te = TS0 + e * MS
            tx = TS0 + x * MS
            per = 8 * 3600 * 1000
            FUND[(d, h)] = np.where((tx // per) - (te // per) > 0, FUND_PCT, 0.0)
            FILL[(d, h)] = first <= h - 1                             # fill bar strictly before the exit bar
    return dict(G=G, FUND=FUND, FILL=FILL, PIN=PIN, led=led)


# ---------------------------------------------------------------- stats
def cluster_mean_se(g, day):
    g = np.asarray(g, float)
    n = len(g)
    m = g.mean()
    s2 = 0.0
    for d in np.unique(day):
        s2 += (g[day == d] - m).sum() ** 2
    return m, np.sqrt(s2) / n


def diff_cluster(g, f, day):
    g = np.asarray(g, float)
    f = np.asarray(f, float)
    if f.sum() == 0 or f.sum() == len(f):
        return np.nan, np.nan
    X = np.column_stack((np.ones(len(g)), f))
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ g
    e = g - X @ b
    meat = np.zeros((2, 2))
    for d in np.unique(day):
        s = X[day == d].T @ e[day == d]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi
    return b[1], float(np.sqrt(V[1, 1]))


def tstat(num, se):
    if se == 0 or np.isnan(se):
        return float("inf") if num > 0 else (float("-inf") if num < 0 else float("nan"))
    return num / se


def max_dd(x):
    c = np.concatenate(([0.0], np.cumsum(x)))
    return float((np.maximum.accumulate(c) - c).max())


def bh_mdd(A):
    c = A["C"].copy()
    for i in range(1, len(c)):
        if np.isnan(c[i]):
            c[i] = c[i - 1]
    c = c[~np.isnan(c)]
    return float(((np.maximum.accumulate(c) - c) / np.maximum.accumulate(c)).max() * 100.0)


def arm_masks(led):
    F = led["F"]
    return {"T": F, "notF": ~F, "C": np.ones(len(F), bool)}


def evaluate(cells, A, ndays):                                      
    led = cells["led"]
    masks = arm_masks(led)
    d, h = PRIMARY
    Gf = cells["G"][PRIMARY] - cells["FUND"][PRIMARY]
    ok = ~np.isnan(Gf)
    out = {"mdd_bh": bh_mdd(A)}
    for arm in ("T", "notF", "C"):
        m = masks[arm] & ok
        g = Gf[m]
        day = led["day"][m]
        if len(g) == 0:
            out[arm] = dict(n=0, mean=np.nan, se=np.nan, t_cost=np.nan, mdd=0.0)
            continue
        mean, se = cluster_mean_se(g, day)
        order = np.argsort(led["t"][m])
        out[arm] = dict(n=int(len(g)), mean=float(mean), se=float(se), t_cost=float(tstat(mean - C_PCT, se)),
                        mdd=max_dd((g - C_PCT)[order]), total_net=float((g - C_PCT).sum()))
    m = ok
    diff, dse = diff_cluster(Gf[m], led["F"][m].astype(float), led["day"][m])
    out["diff"], out["diff_se"] = diff, dse
    out["t_diff"] = float(tstat(diff, dse)) if not np.isnan(diff) else float("nan")
    T, Cc = out["T"], out["C"]
    pf = (T["n"] >= N_MIN and T["mean"] >= C_PCT and T["t_cost"] >= 2.0 and diff >= 0.05 and out["t_diff"] >= 2.0
          and T["mdd"] <= out["mdd_bh"])
    pc = (not pf and Cc["n"] >= N_MIN and Cc["mean"] >= C_PCT and Cc["t_cost"] >= 2.0 and Cc["mdd"] <= out["mdd_bh"])
    if pf:
        out["verdict"] = "PASS_FLOW"
    elif pc:
        out["verdict"] = "PASS_CONTROL"
    elif T["n"] < N_MIN:
        out["verdict"] = "INCONCLUSIVE"
    else:
        out["verdict"] = "FAIL"
    out["mde_T"] = 2.8 * T["se"] if T["n"] else float("nan")
    return out


# ---------------------------------------------------------------- reporting
def manifest(files, path=None):
    target = Path(path) if path is not None else HERE / "DATA_MANIFEST.csv"
    if target.exists():
        return
    rows = []
    for f in files:
        h = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        rows.append((Path(f).name, h, Path(f).stat().st_size))
    with open(target, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["file", "sha256", "bytes"])
        w.writerows(rows)
    return rows


def check_manifest(files, path=None):
    target = Path(path) if path is not None else HERE / "DATA_MANIFEST.csv"
    if not target.exists():
        return manifest(files, path=target)

    # Load stored rows
    stored = {}
    with open(target, "r", newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            stored[row["file"]] = row["sha256"]

    current_files = {Path(f).name: f for f in files}

    # Compare exact file-name set
    if set(current_files.keys()) != set(stored.keys()):
        missing = set(stored.keys()) - set(current_files.keys())
        extra = set(current_files.keys()) - set(stored.keys())
        diff_files = sorted(missing | extra)
        raise SystemExit(f"DATA_MANIFEST mismatch in file set: difference in {diff_files}")

    # Compare sha256 per file to stored rows
    rows = []
    for name, f in sorted(current_files.items()):
        h = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        if h != stored[name]:
            raise SystemExit(f"DATA_MANIFEST mismatch in {name}: expected {stored[name]}, got {h}")
        rows.append((name, h, Path(f).stat().st_size))

    return rows



def count_text(A, led, cells, files):
    n = len(A["O"])
    miss = np.isnan(A["O"])
    lines = ["## Count section (no outcome column)", ""]
    lines.append(f"Files: {len(files)} (SHA256 in DATA_MANIFEST.csv). Bars present {int((~miss).sum())} of {n}; missing {int(miss.sum())}.")
    gaps, run = [], 0
    for x in miss:
        if x:
            run += 1
        elif run:
            gaps.append(run)
            run = 0
    if run:
        gaps.append(run)
    lines.append(f"Gaps: {len(gaps)}; longest {max(gaps) if gaps else 0} bars.")
    months = {}
    for i in np.nonzero(miss)[0]:
        d = dt.datetime.fromtimestamp((TS0 + int(i) * MS) / 1000, dt.timezone.utc)
        months[d.strftime("%Y-%m")] = months.get(d.strftime("%Y-%m"), 0) + 1
    lines.append("Missing bars per month: " + (", ".join(f"{k}:{v}" for k, v in sorted(months.items())) or "none"))
    masks = arm_masks(led)
    nT, nN, nC = (int(masks[k].sum()) for k in ("T", "notF", "C"))
    pv = ~np.isnan(cells["G"][PRIMARY])
    lines.append(f"Ledger encounters (after shared cooldown): n_T={nT}, n_notF={nN}, n_C={nC}; SHORT {int((led['side']==-1).sum())}, LONG {int((led['side']==1).sum())}.")
    lines.append(f"With bars present for the primary cell (d=1,h=60): n_T={int((masks['T']&pv).sum())}, n_notF={int((masks['notF']&pv).sum())}, n_C={int((masks['C']&pv).sum())}; dropped_missing_bars (or exit beyond DEV end)={int((~pv).sum())}.")
    perday = np.bincount(led["day"], minlength=NDAYS_DEV)
    lines.append(f"Encounters per day: mean {perday.mean():.3f}, max {perday.max()}, days with >=1: {int((perday>0).sum())} of {NDAYS_DEV} (per-day list: counts_per_day.csv).")
    lines.append(f"OI: NOT_IN_DATA in DEV. Funding: {'raw_fund archive present' if Path('F:/MTS/Dumps/backtest/raw_fund').exists() else 'funding NOT_IN_DATA (flat 1 bp per straddling encounter)'}.")
    return "\n".join(lines), perday


def sidename(s):
    return {0: "ALL", -1: "SHORT", 1: "LONG"}[s]


def decay_rows(led, cells):
    masks = arm_masks(led)
    rows = []
    for arm in ("T", "notF", "C"):
        for sd in (0, -1, 1):
            for d in DS:
                for h in HS:
                    G = cells["G"][(d, h)]
                    Gf = G - cells["FUND"][(d, h)]
                    m = masks[arm] & ~np.isnan(G) & ((led["side"] == sd) if sd else True)
                    if m.sum() == 0:
                        rows.append([arm, sidename(sd), d, h, 0] + [""] * 8)
                        continue
                    mean, se = cluster_mean_se(Gf[m], led["day"][m])
                    fm = m & cells["FILL"][(d, h)]
                    nm = float((Gf[fm] - CM_PCT).mean()) if fm.sum() else ""
                    rows.append([arm, sidename(sd), d, h, int(m.sum()), f"{G[m].mean():.5f}", f"{se:.5f}", f"{mean:.5f}",
                                 f"{mean - C_PCT:.5f}", f"{tstat(mean - C_PCT, se):.3f}", nm if nm == "" else f"{nm:.5f}",
                                 int(fm.sum()), f"{fm.sum() / m.sum():.3f}"])
    return rows


def write_outputs(A, led, cells, files):
    cols = ["arm", "side", "d", "h", "n", "mean_G", "se", "mean_G_after_funding", "net_C", "t_cost", "net_Cm_filled_only", "n_filled", "fill_rate"]
    with open(HERE / "decay.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        w.writerows(decay_rows(led, cells))
    hdr = ["t_open_time", "side", "F", "D5", "leg"] + [f"p_in_d{d}" for d in DS] + [f"G_d{d}_h{h}" for d in DS for h in HS] + ["dropped"]
    with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(hdr)
        for i in range(len(led["t"])):
            row = [TS0 + int(led["t"][i]) * MS, int(led["side"][i]), int(led["F"][i]), f"{led['D5'][i]:.4f}", f"{led['leg'][i]:.6f}"]
            row += [f"{cells['PIN'][d][i]:.2f}" for d in DS]
            row += [("" if np.isnan(cells["G"][(d, h)][i]) else f"{cells['G'][(d, h)][i]:.5f}") for d in DS for h in HS]
            row += [int(np.isnan(cells["G"][PRIMARY][i]))]
            w.writerow(row)


def main(argv):
    full = "--full" in argv
    if not full and "--count" not in argv:
        print(__doc__)
        return 1
    files = dev_files()
    rows = check_manifest(files)
    A = load_dev(files)
    led = build_ledger(A, NDAYS_DEV)
    cells = compute_cells(A, led, NDAYS_DEV)
    ctext, perday = count_text(A, led, cells, files)
    with open(HERE / "counts_per_day.csv", "w", newline="\n", encoding="utf-8") as fh:
        fh.write("day,encounters\n")
        for i, c in enumerate(perday):
            fh.write(f"{(dt.date(2022, 1, 1) + dt.timedelta(days=i)).isoformat()},{int(c)}\n")
    if not full:
        txt = "# RESULT (count section only; outcome run not yet executed)\n\n" + ctext + "\n"
        (HERE / "RESULT.md").write_text(txt, encoding="utf-8", newline="\n")
        print(txt)
        return 0
    write_outputs(A, led, cells, files)
    res = evaluate(cells, A, NDAYS_DEV)
    masks = arm_masks(led)
    med_qv = float(np.nanmedian(A["QV"]))
    share = CLIP / med_qv * 100
    L = [f"{res['verdict']}", "", f"# RESULT: gross-effect screen on DEV (primary cell d=1, h=60, C=0.14 %). Verdict above is per PRE_REG.md section 4, one run.", ""]
    L.append("## Primary cell (mean of G after funding, % of notional; SE day-clustered)")
    L.append("| arm | n | mean | SE | t_cost | MDD (% of clip) |")
    L.append("|---|---|---|---|---|---|")
    for arm in ("T", "notF", "C"):
        r = res[arm]
        L.append(f"| {arm} | {r['n']} | {r['mean']:.4f} | {r['se']:.4f} | {r['t_cost']:.2f} | {r['mdd']:.2f} |")
    L.append("")
    L.append(f"DIFF (T - notF) = {res['diff']:.4f} %, SE {res['diff_se']:.4f}, t_DIFF = {res['t_diff']:.2f}. Buy-and-hold DEV max drawdown = {res['mdd_bh']:.2f} %. MDE (80 % power) for arm T = 2.8 x SE = {res['mde_T']:.4f} %.")
    L.append("")
    pv = ~np.isnan(cells["G"][PRIMARY])
    f_t = res["T"]["n"] * 60 / (NDAYS_DEV * DAYMIN)
    bh = (np.nanlast(A["C"]) if hasattr(np, "nanlast") else A["C"][~np.isnan(A["C"])][-1]) / A["O"][~np.isnan(A["O"])][0] - 1
    L.append("## Benchmarks (report only)")
    L.append(f"Cash = 0. Arm T total net = {res['T'].get('total_net', 0):.2f} (sum of %-of-clip nets, cost C). Buy-and-hold DEV return {bh*100:.1f} %, scaled by time in market f={f_t:.4f} (n x h / DEV minutes) = {bh*100*f_t:.2f}. Arm C total net = {res['C'].get('total_net', 0):.2f}.")
    L.append("")
    L.append("## Participation")
    L.append(f"Median 1m quote volume {med_qv:,.0f} USDT; clip 1,000 USDT = {share:.4f} % of it ({'size-limited' if share > 1 else 'not size-limited'}).")
    L.append("")
    L.append("## Per-side rows at the primary cell and decay grid")
    L.append("Full 3 arms x ALL/SHORT/LONG x 5 d x 6 h table: decay.csv (30 cells per arm). Primary-cell per-side rows:")
    L.append("")
    L.append("| arm | side | n | mean_G | net_C | t_cost | net_Cm (filled only) | fill rate |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in decay_rows(led, cells):
        if r[2] == 1 and r[3] == 60:
            L.append(f"| {r[0]} | {r[1]} | {r[4]} | {r[5]} | {r[8]} | {r[9]} | {r[10]} | {r[12]} |")
    L.append("")
    L.append("## Funding, drops, decisions")
    L.append("Funding NOT_IN_DATA (F:/MTS/Dumps/backtest/raw_fund absent): flat 1 bp per encounter whose [entry, exit] contains a 00/08/16 UTC settlement; verdict statistics use G minus funding.")
    L.append(f"dropped_missing_bars (primary cell, incl. exit beyond DEV end, never read): {int((~pv).sum())} of {len(pv)}.")
    L.append("DECISION (OURS): INCONCLUSIVE tested after PASS_FLOW and PASS_CONTROL on n_T; maker readout counts a fill when a bar after the entry bar trades through p_in by 0.1 USDT before the exit bar; arm MDD is the sum-of-nets drawdown in % of one clip vs BH in % of price.")
    L.append("")
    L.append(ctext)
    L.append("")
    if res["verdict"] in ("PASS_FLOW", "PASS_CONTROL"):
        L.append("Next steps (cards NOT created here): a validation-read card and a Deribit execution-check card.")
    else:
        L.append("FAIL/INCONCLUSIVE: stop; no detector, chart, layer or management work follows on this family.")
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    sha = hashlib.sha256((HERE / "PRE_REG.md").read_bytes()).hexdigest()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    ex = HERE / "EXPOSURE_LEDGER.csv"
    with open(ex, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["gross_effect_screen_2026-10-15", now, "F:/MTS/data/tom_raw/klines 1m", "2022-01-01..2024-06-30", "DEV", sha, res["verdict"], "whether session-extreme fade with 1m delta flow has a gross effect above 0.14 %"])
        w.writerow(["orderflow_views_2026-10-14/study.py", "2026-10-14", "klines 1m + fapi top-up", "2022-2024 DEV, 2025 VAL, 2026 HOLDOUT", "DEV+VAL+HOLDOUT", "prior", "published (RESULT.md:37-42)", "divergence rule; all three splits published"])
        w.writerow(["tom_btc_2026-10-13/chart_lab.py", "2026-10-13", "BTC charts", "80 charts, window per charts/index.csv (not read here)", "unknown", "prior", "n/a", "chart reading for Tom layer"])
    print(L[0])
    print("\n".join(L[1:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
