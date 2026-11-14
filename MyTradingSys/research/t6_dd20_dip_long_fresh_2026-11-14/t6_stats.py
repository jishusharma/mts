"""T6 step C statistics (written in stage 2, NOT run on real data until the audit passes). See PRE_REG.md pass bars.

Pure functions over lists of trade dicts (schema of t6_core.trade_at + tag_row). run_stats() returns (summary, tables_md);
main() is the only place that touches the cache and files.
"""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t6_core as core  # noqa: E402

SEED = 1114
NBOOT = 2000
NDRAW = 1000


def _nice():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _pct(a, q):
    """Linear-interpolated percentile of a sample (same as numpy's default), written out on the sorted array."""
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def _mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def sub(rows, **kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


def cluster_bootstrap(rows, val="net", nboot=NBOOT, seed=SEED):
    """Resample ISO entry weeks with replacement; resampled mean = sum of returns / number of trades in drawn weeks."""
    rows = [r for r in rows if r.get(val) is not None and r[val] == r[val]]
    if not rows:
        return dict(n=0, weeks=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    cl = {}
    for r in rows:
        cl.setdefault(r["iso_week"], []).append(r[val])
    ks = sorted(cl)
    s = np.array([sum(cl[k]) for k in ks])
    n = np.array([len(cl[k]) for k in ks], float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ks), (nboot, len(ks)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return dict(n=len(rows), weeks=len(ks), mean=float(s.sum() / n.sum()),
                ci_low=_pct(m, 2.5), ci_high=_pct(m, 97.5),
                p_le0=float((np.sum(m <= 0) + 1) / (nboot + 1)))


def placebo(real, pool, val="net", ndraw=NDRAW, seed=SEED, tag_match=True):
    """For each real trade draw a random trade of the SAME coin, split and source tag from pool (fallback: coin + split).
    One draw = mean over the matched set. Returns real mean, draw mean, 97.5th pct, excess and p."""
    real = [r for r in real if r.get(val) is not None and r[val] == r[val]]
    pool = [r for r in pool if r.get(val) is not None and r[val] == r[val]]
    by_full, by_cs = {}, {}
    for r in pool:
        by_full.setdefault((r["coin"], r["split"], r["bull"]), []).append(r[val])
        by_cs.setdefault((r["coin"], r["split"]), []).append(r[val])
    rng = np.random.default_rng(seed)
    acc = np.zeros(ndraw)
    used = fallbacks = skipped = 0
    realvals = []
    for r in real:
        arr = by_full.get((r["coin"], r["split"], r["bull"])) if tag_match else None
        if not arr:
            arr = by_cs.get((r["coin"], r["split"]))
            if not arr:
                skipped += 1
                continue
            fallbacks += 1
        arr = np.asarray(arr)
        acc += arr[rng.integers(0, len(arr), ndraw)]
        used += 1
        realvals.append(r[val])
    if used == 0:
        return dict(n=0, real_mean=float("nan"), draw_mean=float("nan"), p975=float("nan"),
                    excess=float("nan"), p=float("nan"), fallbacks=0, skipped=skipped)
    draws = acc / used
    rm = float(np.mean(realvals))
    return dict(n=used, real_mean=rm, draw_mean=float(draws.mean()), p975=_pct(draws, 97.5),
                excess=rm - float(draws.mean()), p=float((np.sum(draws >= rm) + 1) / (ndraw + 1)),
                fallbacks=fallbacks, skipped=skipped)


def ex_best_weeks(rows, k=5, val="net"):
    rows = [r for r in rows if r[val] == r[val]]
    sums = {}
    for r in rows:
        sums[r["iso_week"]] = sums.get(r["iso_week"], 0.0) + r[val]
    drop = set(sorted(sums, key=lambda w: -sums[w])[:k])
    rest = [r[val] for r in rows if r["iso_week"] not in drop]
    return dict(dropped=sorted(drop), n=len(rest), mean=_mean(rest))


def top_coin_removal(rows, k=3, val="net"):
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
        out.append(dict(removed=list(removed), n=len(rest), mean=_mean(rest)))
    return out


def basket_baseline(pool, split, val="net"):
    """Equal-weight mean across coins for each Monday (complete windows only), then the mean over Mondays."""
    by_mon = {}
    for r in pool:
        if r["split"] == split and not r["delist"] and r[val] == r[val]:
            by_mon.setdefault(r["entry_ts"], []).append(r[val])
    wk = [float(np.mean(v)) for v in by_mon.values()]
    return dict(mondays=len(wk), mean=_mean(wk))


def describe(rows, val="net"):
    v = np.array([r[val] for r in rows if r[val] == r[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                worst=float(v.min()), best=float(v.max()))


def group_table(rows, keyfn, val="net"):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), []).append(r)
    return {k: describe(v, val) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


def _md_table(title, tab):
    lines = ["### " + title, "", "| key | n | mean | median | win | worst | best |", "|---|---|---|---|---|---|---|"]
    for k, d in tab.items():
        if d["n"] == 0:
            continue
        lines.append("| %s | %d | %+.4f | %+.4f | %.2f | %+.3f | %+.3f |" % (k, d["n"], d["mean"], d["median"],
                                                                         d["win"], d["worst"], d["best"]))
    return "\n".join(lines) + "\n"


def run_stats(trades, pool, nboot=NBOOT, ndraw=NDRAW, seed=SEED):
    """trades: event trades (all splits); pool: all-Monday trades of the same coins. Returns (summary, tables_md)."""
    val = sub(trades, split="VAL")
    dev = sub(trades, split="DEV")
    S = dict(n_dev=len(dev), n_val=len(val), val_weeks=len({r["iso_week"] for r in val}))
    for nm, rows in (("val", val), ("dev", dev)):
        S[nm + "_net"] = describe(rows, "net")
        S[nm + "_gross"] = describe(rows, "gross")
        S[nm + "_nofund"] = describe(rows, "net_nofund")
        S[nm + "_net_R"] = describe(rows, "net_R")
        S[nm + "_gross_R"] = describe(rows, "gross_R")
        S[nm + "_stop_R"] = describe(rows, "stop_R")
        S[nm + "_flat_funding_trades"] = sum(1 for r in rows if r["funding_rule"] == "FLAT")
        S[nm + "_delist_exits"] = sum(1 for r in rows if r["delist"])
    S["val_boot_net"] = cluster_bootstrap(val, "net", nboot, seed)
    S["val_boot_nofund"] = cluster_bootstrap(val, "net_nofund", nboot, seed)
    S["val_boot_stop_R"] = cluster_bootstrap(val, "stop_R", nboot, seed)
    pool_val = sub(pool, split="VAL")
    S["placebo_net"] = placebo(val, pool_val, "net", ndraw, seed)
    S["placebo_stop_R"] = placebo(val, pool_val, "stop_R", ndraw, seed)
    S["ex_best5_weeks"] = ex_best_weeks(val, 5)
    S["top_coin_removal"] = top_coin_removal(val, 3)
    S["bh_val"] = {"net": basket_baseline(pool, "VAL", "net"), "gross": basket_baseline(pool, "VAL", "gross")}
    S["bh_dev"] = {"net": basket_baseline(pool, "DEV", "net"), "gross": basket_baseline(pool, "DEV", "gross")}
    # pass bars (PRE_REG); a verdict string is built from these only at step C
    ok1 = S["n_val"] >= 30 and S["val_weeks"] >= 20
    bars = {
        "1_power": ok1,
        "2_val_ci": bool(ok1 and S["val_net"]["mean"] > 0 and S["val_boot_net"]["ci_low"] > 0),
        "3_dev_sign": bool(S["dev_net"].get("n", 0) > 0 and S["dev_net"]["mean"] > 0),
        "4_placebo": bool(S["placebo_net"]["n"] > 0 and S["placebo_net"]["real_mean"] >= S["placebo_net"]["p975"]
                          and S["placebo_net"]["excess"] > 0),
        "5_ex_best5": bool(S["ex_best5_weeks"]["mean"] > 0),
        "6_bh": bool(S["val_net"].get("n", 0) > 0 and S["bh_val"]["net"]["mean"] == S["bh_val"]["net"]["mean"]
                     and S["val_net"]["mean"] >= S["bh_val"]["net"]["mean"]),
        "7_top_coin": bool(S["top_coin_removal"] and S["top_coin_removal"][0]["mean"] > 0),
    }
    S["bars"] = bars
    S["kill"] = dict(a_val_net_le0=bool(S["val_net"].get("n", 0) and S["val_net"]["mean"] <= 0),
                     b_stop_R_le0=bool(S["val_stop_R"].get("n", 0) and S["val_stop_R"]["mean"] <= 0),
                     c_ex_best5_le0=bool(S["ex_best5_weeks"]["mean"] <= 0))
    S["holm_worst_case_p"] = min(1.0, 3 * S["val_boot_net"]["p_le0"]) if S["val_boot_net"]["n"] else float("nan")
    tabs = []
    for nm, rows in (("VAL", val), ("DEV", dev)):
        tabs.append(_md_table("by year (%s, net)" % nm, group_table(rows, lambda r: r["iso_week"][:4])))
        tabs.append(_md_table("by coin (%s, net)" % nm, group_table(rows, lambda r: r["coin"])))
        tabs.append(_md_table("by source tag (%s, net)" % nm, group_table(rows, lambda r: r["bull"])))
        tabs.append(_md_table("by brain cycle (%s, net)" % nm, group_table(rows, lambda r: r.get("cycle", "NA"))))
        tabs.append(_md_table("by brain label (%s, net)" % nm, group_table(rows, lambda r: r.get("label", "NA"))))
    return S, "\n".join(tabs)


# ---- file side (step C only) ----
NUMERIC = ("entry_px", "exit_px", "gross", "fee", "funding", "net_nofund", "net", "risk_unit", "gross_R", "net_R",
           "stop", "stop_exit_px", "stop_gross", "stop_funding", "stop_net", "stop_R")


def read_trades_csv(path):
    import csv
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUMERIC:
                r[k] = float(r[k]) if r.get(k) not in (None, "") else float("nan")
            r["entry_ts"] = int(r["entry_ts"])
            r["delist"] = r["exit_reason"] == "DELIST-EXIT"
            out.append(r)
    return out


def main(cache=r"F:/MTS/data_cache/binance/wave2-1114", here=None):
    _nice()
    here = pathlib.Path(here or pathlib.Path(__file__).resolve().parent)
    trades = read_trades_csv(here / "trades.csv")
    cov = json.load(open(here / "coverage.json", encoding="utf-8"))
    pool = []
    for name in cov["kept"]:
        c = core.load_coin(pathlib.Path(cache) / "spot_1d" / (name + "USDT.csv"), name)
        f = core.load_funding(pathlib.Path(cache) / "funding" / (name + "USDT.csv"))
        pool.extend(core.all_monday_trades(c, f))
    S, tabs = run_stats(trades, pool)
    (here / "summary.json").write_text(json.dumps(S, indent=1, default=str), encoding="utf-8")
    (here / "tables.md").write_text(tabs, encoding="utf-8")
    print("wrote summary.json, tables.md")


if __name__ == "__main__":
    main()
