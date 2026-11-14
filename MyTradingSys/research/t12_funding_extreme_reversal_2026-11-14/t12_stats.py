"""T12 statistics: pure functions over lists of trade dicts (t12_core.simulate_plan schema). See PRE_REG.md pass bars.
All means are in R (risk unit = stop distance / entry) unless a key says pct. Seed 1114.
"""
import sys
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

SEED = 1114
NBOOT = 2000
NDRAW = 1000
BLOCK = 2


def _pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def block_bootstrap(rows, val="netp_R", nboot=NBOOT, seed=SEED, block=BLOCK):
    """Moving-block bootstrap over consecutive calendar ISO entry weeks (empty weeks kept), block = 2 weeks.
    Resampled mean = sum of R in drawn weeks / trades in drawn weeks. p_le0 = (#resampled means <= 0 + 1)/(nboot+1)."""
    rows = [r for r in rows if r[val] == r[val]]
    if not rows:
        return dict(n=0, weeks=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"),
                    week_sd=float("nan"))
    wk = np.array([r["week"] for r in rows])
    w0, w1 = int(wk.min()), int(wk.max())
    W = w1 - w0 + 1
    s = np.zeros(W)
    n = np.zeros(W)
    for r in rows:
        s[r["week"] - w0] += r[val]
        n[r["week"] - w0] += 1
    units = s[n > 0] / n[n > 0]
    rng = np.random.default_rng(seed)
    nblk = int(np.ceil(W / block))
    if W < block:
        starts = np.zeros((nboot, nblk), int)
        offs = np.arange(W)[None, :]
        idx = np.zeros((nboot, W), int)
    else:
        starts = rng.integers(0, W - block + 1, (nboot, nblk))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(nboot, -1)
    ss, nn = s[idx].sum(1), n[idx].sum(1)
    ok = nn > 0
    m = ss[ok] / nn[ok]
    return dict(n=len(rows), weeks=int((n > 0).sum()), span_weeks=W, mean=float(s.sum() / n.sum()),
                ci_low=_pct(m, 2.5), ci_high=_pct(m, 97.5),
                p_le0=float((np.sum(m <= 0) + 1) / (len(m) + 1)), week_sd=float(np.std(units, ddof=1)) if len(units) > 1 else float("nan"))


def placebo(pairs, ndraw=NDRAW, seed=SEED):
    """pairs: list of (real_value, candidate_values array). Trades with no candidate are skipped (counted). One draw = mean
    over matched trades of one random candidate each. real mean is taken over the same matched trades."""
    acc = np.zeros(ndraw)
    rng = np.random.default_rng(seed)
    realv, used, skipped = [], 0, 0
    for rv, cand in pairs:
        cand = np.asarray(cand, float)
        cand = cand[~np.isnan(cand)]
        if len(cand) == 0:
            skipped += 1
            continue
        acc += cand[rng.integers(0, len(cand), ndraw)]
        realv.append(rv)
        used += 1
    if used == 0:
        return dict(n=0, skipped=skipped, real_mean=float("nan"), draw_mean=float("nan"), p975=float("nan"),
                    excess=float("nan"), p=float("nan"))
    d = acc / used
    rm = float(np.mean(realv))
    return dict(n=used, skipped=skipped, real_mean=rm, draw_mean=float(d.mean()), p975=_pct(d, 97.5),
                excess=rm - float(d.mean()), p=float((np.sum(d >= rm) + 1) / (ndraw + 1)))


def ex_best_weeks(rows, k=5, val="netp_R"):
    rows = [r for r in rows if r[val] == r[val]]
    sums = {}
    for r in rows:
        sums[r["week"]] = sums.get(r["week"], 0.0) + r[val]
    drop = set(sorted(sums, key=lambda w: -sums[w])[:k])
    rest = [r[val] for r in rows if r["week"] not in drop]
    return dict(k=k, n=len(rest), mean=mean(rest))


def top_coin_removal(rows, k=3, val="netp_R"):
    rows = [r for r in rows if r[val] == r[val]]
    out, removed = [], []
    for _ in range(k):
        sums = {}
        for r in rows:
            if r["coin"] not in removed:
                sums[r["coin"]] = sums.get(r["coin"], 0.0) + r[val]
        if not sums:
            break
        top = max(sums, key=lambda c: sums[c])
        removed.append(top)
        rest = [r[val] for r in rows if r["coin"] not in removed]
        out.append(dict(removed=list(removed), n=len(rest), mean=mean(rest)))
    return out


def leave_one_year_out(rows, val="netp_R"):
    ys = sorted({r["year"] for r in rows})
    return {y: dict(n=sum(1 for r in rows if r["year"] != y), mean=mean([r[val] for r in rows if r["year"] != y])) for y in ys}


def group_rows(rows, key, val="netp_R", val2="nett_R"):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r)
    return {k: dict(n=len(v), mean_price=mean([x[val] for x in v]), mean_total=mean([x[val2] for x in v]))
            for k, v in sorted(out.items(), key=lambda kv: str(kv[0]))}


def holm(ps):
    """Holm step-down adjusted p-values for a dict {name: p}."""
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for k, (name, p) in enumerate(items):
        run = max(run, min(1.0, (m - k) * p))
        out[name] = run
    return out


def bar1(rows):
    n = len(rows)
    w = len({r["week"] for r in rows})
    return dict(n=n, weeks=w, ok=bool(n >= 30 and w >= 20))


def baseline_compare(rows, base_price_daily, base_total_daily):
    """Mean net return per day in position of the trades (pct, fee included) vs the flagged-state basket."""
    tp = mean([r["netp"] / r["days"] for r in rows])
    tt = mean([r["nett"] / r["days"] for r in rows])
    return dict(trade_price_daily=tp, trade_total_daily=tt, base_price_daily=base_price_daily,
                base_total_daily=base_total_daily, ok=bool(tp >= base_price_daily))


def sign_flip(rows, cell, val="netp_R"):
    """Positive only in the cycle state opposite to the gate (A long: BULL; B short: BEAR), not in the aligned states."""
    opp = ("BULL",) if cell == "A" else ("BEAR",)
    al = ("BEAR", "BASE") if cell == "A" else ("BULL", "BASE")
    mo = mean([r[val] for r in rows if r["cycle"] in opp])
    ma = mean([r[val] for r in rows if r["cycle"] in al])
    return bool(mo == mo and mo > 0 and (ma != ma or ma <= 0)), mo, ma


def verdict(cell, val_rows, dev_rows, boot_p, boot_t, pl_w, base, ex5, top3, loyo, flip):
    """Apply bars 1-9 on price-only R. Returns (verdict string, dict of bar booleans)."""
    b1 = bar1(val_rows)
    bars = {1: b1["ok"]}
    if not b1["ok"]:
        return "UNDERPOWERED", bars
    bars[2] = bool(boot_p["mean"] > 0 and boot_p["ci_low"] > 0)
    bars[3] = bool(mean([r["netp_R"] for r in dev_rows]) > 0)
    bars[4] = bool(pl_w["n"] > 0 and pl_w["real_mean"] >= pl_w["p975"] and pl_w["excess"] > 0)
    bars[5] = bool(ex5["mean"] > 0)
    bars[6] = bool(base["ok"])
    bars[7] = bool(len(top3) == 3 and top3[-1]["mean"] > 0)
    bars[8] = bool(all(v["mean"] > 0 for v in loyo.values())) if loyo else False
    core_ok = all(bars[k] for k in (2, 3, 4, 5, 6))
    if core_ok:
        if flip:
            return "SIGN-FLIP", bars
        if not (bars[7] and bars[8]):
            return "FRAGILE", bars
        return "PASS", bars
    total_ok = bool(boot_t["mean"] > 0 and boot_t["ci_low"] > 0)
    if total_ok and not bars[2]:
        return "CARRY-ONLY", bars
    return "FAIL", bars
