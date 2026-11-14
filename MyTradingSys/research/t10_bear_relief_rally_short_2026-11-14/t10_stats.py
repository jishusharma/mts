"""T10 statistics. Pure functions over trade dicts (schema of t10_core.make_trade + tags cycle/label/episode); main() is the
only place that touches the cache and files. Pass bars and verdict logic are the ones frozen in PRE_REG.md.
Primary value = net_R (price-only, fee-net, in units of the stop distance). total_R adds real funding where cached.
"""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t10_core as core  # noqa: E402

SEED = 1114
NBOOT = 2000
NDRAW = 1000
BLOCK = 2


def pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def sub(rows, **kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


def year_of(r):
    return r["iso_week"][:4] if "year" not in r else r["year"]


def entry_year(r):
    return core.day_str(r["entry_day"])[:4]


def _ratio_boot(s, n, blocks, nboot, seed):
    rng = np.random.default_rng(seed)
    k = len(s)
    nb = int(np.ceil(k / float(blocks)))
    starts = rng.integers(0, max(k - blocks + 1, 1), (nboot, nb))
    idx = np.minimum(starts[:, :, None] + np.arange(blocks)[None, None, :], k - 1).reshape(nboot, -1)
    den = n[idx].sum(1)
    return s[idx].sum(1) / np.where(den > 0, den, np.nan)


def week_block_bootstrap(rows, val="net_R", block=BLOCK, nboot=NBOOT, seed=SEED):
    """Entry weeks that hold trades, in time order; moving blocks of `block` adjacent such weeks; resampled mean =
    sum of values / number of trades in the drawn blocks."""
    rows = [r for r in rows if r.get(val) == r.get(val)]
    if not rows:
        return dict(n=0, weeks=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    cl = {}
    for r in rows:
        cl.setdefault(r["iso_week"], []).append(r[val])
    ks = sorted(cl)
    s = np.array([sum(cl[k]) for k in ks])
    n = np.array([len(cl[k]) for k in ks], float)
    m = _ratio_boot(s, n, min(block, len(ks)), nboot, seed)
    m = m[~np.isnan(m)]
    return dict(n=len(rows), weeks=len(ks), mean=float(s.sum() / n.sum()), ci_low=pct(m, 2.5), ci_high=pct(m, 97.5),
                p_le0=float((np.sum(m <= 0) + 1) / (len(m) + 1)))


def episode_bootstrap(rows, val="net_R", nboot=NBOOT, seed=SEED):
    """Second unit: rally episode (entry days of all coins chained within 14 days). iid resample of episodes."""
    rows = [r for r in rows if r.get(val) == r.get(val)]
    if not rows:
        return dict(n=0, episodes=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"))
    cl = {}
    for r in rows:
        cl.setdefault(r["episode"], []).append(r[val])
    ks = sorted(cl)
    s = np.array([sum(cl[k]) for k in ks])
    n = np.array([len(cl[k]) for k in ks], float)
    m = _ratio_boot(s, n, 1, nboot, seed)
    return dict(n=len(rows), episodes=len(ks), mean=float(s.sum() / n.sum()), ci_low=pct(m, 2.5), ci_high=pct(m, 97.5),
                ep_means=[round(float(a / b), 3) for a, b in zip(s, n)])


def placebo_draws(real_vals, cand_lists, ndraw=NDRAW, seed=SEED):
    """One draw = mean over the matched set of one random candidate outcome per real trade. Real trades with no candidate
    are skipped (counted). Returns real mean over used trades, draw mean, 97.5th pct, excess, percentile rank, p."""
    pairs = [(v, c) for v, c in zip(real_vals, cand_lists) if len(c) > 0]
    skipped = len(real_vals) - len(pairs)
    if not pairs:
        return dict(n=0, skipped=skipped, real_mean=float("nan"), draw_mean=float("nan"), p975=float("nan"),
                    excess=float("nan"), rank_pct=float("nan"), p=float("nan"))
    rng = np.random.default_rng(seed)
    acc = np.zeros(ndraw)
    for _v, c in pairs:
        c = np.asarray(c, float)
        acc += c[rng.integers(0, len(c), ndraw)]
    draws = acc / len(pairs)
    rm = float(np.mean([v for v, _c in pairs]))
    return dict(n=len(pairs), skipped=skipped, real_mean=rm, draw_mean=float(draws.mean()), p975=pct(draws, 97.5),
                excess=rm - float(draws.mean()), rank_pct=float(100.0 * np.mean(draws < rm)),
                p=float((np.sum(draws >= rm) + 1) / (ndraw + 1)))


def ex_best_weeks(rows, k=5, val="net_R"):
    rows = [r for r in rows if r[val] == r[val]]
    sums = {}
    for r in rows:
        sums[r["iso_week"]] = sums.get(r["iso_week"], 0.0) + r[val]
    drop = set(sorted(sums, key=lambda w: -sums[w])[:k])
    rest = [r[val] for r in rows if r["iso_week"] not in drop]
    return dict(k=k, dropped=sorted(drop), n=len(rest), mean=mean(rest))


def top_coin_removal(rows, k=3, val="net_R"):
    rows = [r for r in rows if r[val] == r[val]]
    out, removed = [], []
    for _ in range(k):
        sums = {}
        for r in rows:
            if r["coin"] not in removed:
                sums[r["coin"]] = sums.get(r["coin"], 0.0) + r[val]
        if not sums:
            break
        removed.append(max(sums, key=lambda c: sums[c]))
        rest = [r[val] for r in rows if r["coin"] not in removed]
        out.append(dict(removed=list(removed), n=len(rest), mean=mean(rest)))
    return out


def leave_one_year_out(rows, val="net_R"):
    ys = sorted({entry_year(r) for r in rows})
    return {y: dict(n=len([r for r in rows if entry_year(r) != y]),
                    mean=mean([r[val] for r in rows if entry_year(r) != y])) for y in ys}


def describe(rows, val="net_R"):
    v = np.array([r[val] for r in rows if r[val] == r[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                worst=float(v.min()), best=float(v.max()))


def group_rows(rows, keyfn):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), []).append(r)
    out = {}
    for k, v in sorted(g.items(), key=lambda kv: str(kv[0])):
        out[k] = dict(n=len(v), weeks=len({r["iso_week"] for r in v}), gross_R=mean([r["gross_R"] for r in v]),
                      fee_R=mean([r["fee_R"] for r in v]), net_R=mean([r["net_R"] for r in v]),
                      total_R=mean([r["total_R"] for r in v]))
    return out


def md_group(title, tab):
    L = ["### " + title, "", "| key | n | weeks | gross R | fee R | net R | total R (fund) |", "|---|---|---|---|---|---|---|"]
    for k, d in tab.items():
        L.append("| %s | %d | %d | %+.3f | %.3f | %+.3f | %+.3f |" % (k, d["n"], d["weeks"], d["gross_R"], d["fee_R"],
                                                                   d["net_R"], d["total_R"]))
    return "\n".join(L) + "\n"


def bear_period(r):
    d = core.day_str(r["entry_day"])
    if d[:4] == "2018":
        return "2018"
    if d[:4] == "2022":
        return "2022"
    if d >= "2025-10-01":
        return "2025-26"
    return "other"


def per_day_net(rows):
    """Mean net return per day in position: sum of net % returns / sum of days held."""
    days = sum(r["hold_days"] for r in rows)
    return float(sum(r["net"] for r in rows) / days) if days else float("nan")


def first_fail(bars):
    for k in sorted(bars):
        if k[0] in "234567" and not bars[k]:
            return k
    return None


def verdict(S):
    """Verdict from the numbers only (PRE_REG 'Verdict vocabulary'). Returns (label, detail)."""
    b = S["bars"]
    if not b["1_power"]:
        return "UNDERPOWERED", "bar 1 fails (n_val %d, weeks %d); DEV is the main read" % (S["n_val"], S["val_weeks"])
    if S["carry_only"]:
        return "CARRY-ONLY", "price-only VAL net <= 0, price+funding > 0"
    kills = [k for k, v in S["kill"].items() if v]
    if kills:
        return "FAIL", "KILL " + ",".join(kills)
    if S["sign_flip"]:
        return "SIGN-FLIP", "positive only in the phase opposite to the gate"
    ff = first_fail(b)
    if ff:
        return "FAIL", "first failing bar " + ff
    if not (b["7_top3_coin"] and b["8_loyo"]):
        return "FRAGILE", "bar 7 or 8 fails"
    return "PASS", "bars 1-8 hold, no kill, no sign flip"


def run_stats(trades, placebo_win, placebo_glob, base, nboot=NBOOT, ndraw=NDRAW, seed=SEED):
    """trades: primary-cell trades (all splits, already screened). placebo_win/placebo_glob: {id(trade): [candidate net_R]}.
    base: {'DEV': mean daily short return, 'VAL': ...} of the downtrending-coin basket on gated days."""
    val, dev = sub(trades, split="VAL"), sub(trades, split="DEV")
    S = dict(n_dev=len(dev), n_val=len(val), val_weeks=len({r["iso_week"] for r in val}),
             dev_weeks=len({r["iso_week"] for r in dev}))
    for nm, rows in (("val", val), ("dev", dev)):
        for col in ("gross_R", "fee_R", "net_R", "fund_R", "total_R", "net", "gross"):
            S["%s_%s" % (nm, col)] = describe(rows, col)
        S[nm + "_fund_covered"] = sum(1 for r in rows if r["fund_rule"] == "REAL")
        S[nm + "_ended"] = sum(1 for r in rows if r["exit_reason"] == "ENDED")
        cov = [r for r in rows if r["fund_rule"] == "REAL"]
        S[nm + "_covered_net_R"] = mean([r["net_R"] for r in cov])
        S[nm + "_covered_total_R"] = mean([r["total_R"] for r in cov])
        S[nm + "_exit_mix"] = {k: sum(1 for r in rows if r["exit_reason"] == k) for k in sorted({r["exit_reason"] for r in rows})}
    S["val_boot"] = week_block_bootstrap(val, "net_R", BLOCK, nboot, seed)
    S["dev_boot"] = week_block_bootstrap(dev, "net_R", BLOCK, nboot, seed)
    S["val_boot_total"] = week_block_bootstrap(val, "total_R", BLOCK, nboot, seed)
    S["val_episode"] = episode_bootstrap(val, "net_R", nboot, seed)
    S["dev_episode"] = episode_bootstrap(dev, "net_R", nboot, seed)
    for nm, rows in (("val", val), ("dev", dev)):
        rv = [r["net_R"] for r in rows]
        S["placebo_win_" + nm] = placebo_draws(rv, [placebo_win.get(id(r), []) for r in rows], ndraw, seed)
        S["placebo_glob_" + nm] = placebo_draws(rv, [placebo_glob.get(id(r), []) for r in rows], ndraw, seed)
    kx = 5 if S["val_weeks"] >= 30 else 2
    S["ex_best"] = ex_best_weeks(val, kx)
    S["ex_best5"] = ex_best_weeks(val, 5)
    S["top_coin"] = top_coin_removal(val, 3)
    S["loyo_val"] = leave_one_year_out(val)
    S["loyo_all"] = leave_one_year_out(trades)
    S["strat_per_day_net_val"] = per_day_net(val)
    S["strat_per_day_net_dev"] = per_day_net(dev)
    S["baseline_per_day"] = base
    S["ex_ended_val"] = describe([r for r in val if r["exit_reason"] != "ENDED"])
    S["ex_lunaftt_val"] = describe([r for r in val if r["coin"] not in ("LUNA", "FTT")])
    S["ex_ended_dev"] = describe([r for r in dev if r["exit_reason"] != "ENDED"])
    S["ex_lunaftt_dev"] = describe([r for r in dev if r["coin"] not in ("LUNA", "FTT")])
    S["bear_periods"] = {k: describe([r for r in trades if bear_period(r) == k]) for k in ("2018", "2022", "2025-26")}
    cyc = group_rows(val, lambda r: r["cycle"])
    S["val_cycle"] = cyc
    S["dev_cycle"] = group_rows(dev, lambda r: r["cycle"])
    bear, bull = cyc.get("BEAR"), cyc.get("BULL")
    S["sign_flip"] = bool(S["val_net_R"].get("n", 0) and S["val_net_R"]["mean"] > 0 and bear and bull
                          and bear["n"] >= 10 and bull["n"] >= 10 and bear["net_R"] <= 0 < bull["net_R"])
    pw, pn = S["placebo_win_val"], S["val_net_R"]
    ok1 = S["n_val"] >= 30 and S["val_weeks"] >= 20
    vm = S["val_net_R"].get("mean", float("nan"))
    bars = {
        "1_power": ok1,
        "2_val_ci": bool(ok1 and vm > 0 and S["val_boot"]["ci_low"] > 0),
        "3_dev_sign": bool(S["dev_net_R"].get("n", 0) >= 10 and S["dev_net_R"]["mean"] > 0),
        "4_placebo": bool(pw["n"] > 0 and pw["real_mean"] > pw["p975"] and pw["excess"] > 0),
        "5_ex_best": bool(S["ex_best"]["mean"] > 0),
        "6_baseline": bool(base.get("VAL") == base.get("VAL") and S["strat_per_day_net_val"] >= base["VAL"]),
        "7_top3_coin": bool(len(S["top_coin"]) == 3 and S["top_coin"][2]["mean"] > 0),
        "8_loyo": bool(S["loyo_val"] and all(v["mean"] > 0 for v in S["loyo_val"].values())),
    }
    S["bars"] = bars
    S["carry_only"] = bool(S["val_net_R"].get("n", 0) and vm <= 0 and S["val_total_R"]["mean"] > 0)
    S["kill"] = dict(
        a_val_total_le0=bool(S["n_val"] >= 40 and S["val_total_R"].get("mean", 1) <= 0),
        b_placebo_le_p975=bool(pw["n"] >= 60 and pw["real_mean"] <= pw["p975"]),
        c_dev_sign_neg=bool(ok1 and S["dev_net_R"].get("n", 0) and S["dev_net_R"]["mean"] < 0))
    S["holm_family9_worst_p"] = min(1.0, 9 * S["val_boot"]["p_le0"]) if S["val_boot"]["n"] else float("nan")
    S["verdict"], S["verdict_detail"] = verdict(S)
    return S


# ---------------------------------------------------------------- file side
def build_placebo(D, rows, flag_cache):
    """Candidate outcomes for each real trade: same coin, flagged days (BTC gate + downtrend), same split, same stop %,
    same target %, same 10-bar cap. Window variant = entry within +/-56 days of the real entry day."""
    win, glob = {}, {}
    for r in rows:
        runs, _f = D["coins"][r["coin"]]
        run = runs[r["run"]]
        key = (r["coin"], r["run"])
        if key not in flag_cache:
            flag_cache[key] = np.where(core.flagged_mask(run, D["gate"], D["alive_n"]))[0]
        w, g = [], []
        for tc in flag_cache[key]:
            tc = int(tc)
            if tc == r["t"] or core.split_of_day(int(run.day[tc])) != r["split"]:
                continue
            v = core.placebo_outcome_R(run, tc, r["stop_pct"], r["tgt_pct"])
            if v is None:
                continue
            g.append(v)
            if abs(int(run.day[tc + 1]) - r["entry_day"]) <= core.PLACEBO_WINDOW_DAYS:
                w.append(v)
        win[id(r)], glob[id(r)] = w, g
    return win, glob


def baseline_daily(D):
    by_day = {}
    for name, (runs, _f) in D["coins"].items():
        for run in runs:
            fl = np.where(core.flagged_mask(run, D["gate"], D["alive_n"]))[0]
            for t in fl:
                if t + 1 < run.n:
                    by_day.setdefault(int(run.day[t + 1]), []).append(-(run.c[t + 1] / run.c[t] - 1.0))
    out = {"DEV": [], "VAL": []}
    for d, v in by_day.items():
        out[core.split_of_day(d)].append(float(np.mean(v)))
    return {k: (float(np.mean(v)) if v else float("nan")) for k, v in out.items()}, {k: len(v) for k, v in out.items()}


def fmt(x, f="%+.3f"):
    return f % x if x == x else "n/a"


def result_md(S, mix, descr_rescue):
    v = S["val_net_R"]
    pw = S["placebo_win_val"]
    L = []
    L.append("**T10 bear-phase relief-rally short: %s (%s). VAL n %d trades, %d entry weeks, net %s R (price-only, fee-net), "
             "CI %s..%s.**" % (S["verdict"], S["verdict_detail"], S["n_val"], S["val_weeks"], fmt(v.get("mean", float("nan"))),
                               fmt(S["val_boot"]["ci_low"]), fmt(S["val_boot"]["ci_high"])))
    L.append("")
    L.append("Regime mix: " + mix)
    L.append("")
    L.append("| row | n | weeks | gross R | fee R | net R | total R (with real funding) |")
    L.append("|---|---|---|---|---|---|---|")
    for nm, key in (("VAL", "val"), ("DEV", "dev")):
        n = S["n_" + key]
        L.append("| %s | %d | %d | %s | %s | %s | %s |" % (nm, n, S[key + "_weeks"] if key + "_weeks" in S else S["val_weeks"],
                                                           fmt(S[key + "_gross_R"].get("mean", float("nan"))),
                                                           fmt(S[key + "_fee_R"].get("mean", float("nan")), "%.3f"),
                                                           fmt(S[key + "_net_R"].get("mean", float("nan"))),
                                                           fmt(S[key + "_total_R"].get("mean", float("nan")))))
    L.append("")
    L.append("Bars: " + ", ".join("%s=%s" % (k, "PASS" if b else "FAIL") for k, b in sorted(S["bars"].items())))
    L.append("")
    L.append("Failed bars: " + (", ".join(k for k, b in sorted(S["bars"].items()) if not b) or "none")
             + ". Kill flags: " + (", ".join(k for k, b in S["kill"].items() if b) or "none")
             + ". Flags: carry_only=%s sign_flip=%s." % (S["carry_only"], S["sign_flip"]))
    L.append("")
    L.append("Placebo (same-window, VAL): real %s R, draw mean %s, 97.5th %s, rank %.1f%%, n %d. Global variant: real %s, "
             "draw mean %s, 97.5th %s, rank %.1f%%." % (
                 fmt(pw["real_mean"]), fmt(pw["draw_mean"]), fmt(pw["p975"]), pw["rank_pct"], pw["n"],
                 fmt(S["placebo_glob_val"]["real_mean"]), fmt(S["placebo_glob_val"]["draw_mean"]),
                 fmt(S["placebo_glob_val"]["p975"]), S["placebo_glob_val"]["rank_pct"]))
    L.append("")
    L.append("Baseline (short-and-hold of downtrending coins on gated days, mean daily return): VAL %s, DEV %s; strategy per "
             "day in position VAL %s, DEV %s." % (fmt(S["baseline_per_day"]["VAL"], "%+.5f"), fmt(S["baseline_per_day"]["DEV"], "%+.5f"),
                                                  fmt(S["strat_per_day_net_val"], "%+.5f"), fmt(S["strat_per_day_net_dev"], "%+.5f")))
    L.append("")
    L.append("Ex-best-%d weeks (VAL) mean %s; ex-best-5 %s. Top-3 coin removal (VAL): %s. Leave-one-year-out (VAL): %s." % (
        S["ex_best"]["k"], fmt(S["ex_best"]["mean"]), fmt(S["ex_best5"]["mean"]),
        "; ".join("%s -> %s" % ("+".join(t["removed"]), fmt(t["mean"])) for t in S["top_coin"]),
        "; ".join("%s -> %s" % (y, fmt(t["mean"])) for y, t in S["loyo_val"].items())))
    L.append("")
    L.append("Second unit (rally episode): VAL %d episodes, mean of pooled R %s, CI %s..%s; DEV %d episodes, mean %s." % (
        S["val_episode"].get("episodes", 0), fmt(S["val_episode"].get("mean", float("nan"))),
        fmt(S["val_episode"].get("ci_low", float("nan"))), fmt(S["val_episode"].get("ci_high", float("nan"))),
        S["dev_episode"].get("episodes", 0), fmt(S["dev_episode"].get("mean", float("nan")))))
    L.append("")
    L.append("Funding: VAL trades with real funding %d of %d (rest NOT_IN_DATA, no funding imputed); covered-only net %s, total %s. "
             "Survivorship direction: shorts biased DOWN by survivor-only lists, UP by delisting collapses; ex-ENDED VAL mean %s "
             "(n %d), ex-LUNA/FTT VAL mean %s (n %d)." % (
                 S["val_fund_covered"], S["n_val"], fmt(S["val_covered_net_R"]), fmt(S["val_covered_total_R"]),
                 fmt(S["ex_ended_val"].get("mean", float("nan"))), S["ex_ended_val"].get("n", 0),
                 fmt(S["ex_lunaftt_val"].get("mean", float("nan"))), S["ex_lunaftt_val"].get("n", 0)))
    L.append("")
    L.append("Three bear periods (sign report, not a test; net R): " + "; ".join(
        "%s n %d mean %s" % (k, d.get("n", 0), fmt(d.get("mean", float("nan")))) for k, d in S["bear_periods"].items()))
    L.append("")
    L.append("Holm: single-cell p (week-block bootstrap, one-sided) %.4f; worst case over the 9-cell family %.4f." % (
        S["val_boot"]["p_le0"], S["holm_family9_worst_p"]))
    L.append("")
    L.append("Rescue row (descriptive only, rally threshold 8%%, never the verdict): %s" % descr_rescue)
    L.append("")
    return "\n".join(L)


def main():
    core.lower_priority()
    lk = core.slot_acquire("t10-stats")
    try:
        import t10_trades as tt
        D = tt.load_all()
        phase = tt.load_phase()
        rows, skips = tt.build(D, "12")
        tt.write_trades(rows, HERE / "trades.csv", phase)           # tags rows (cycle, label, episode)
        rows8, _s8 = tt.build(D, "8")
        tt.write_trades(rows8, HERE / "trades_rescue8.csv", phase)
        flag_cache = {}
        win, glob = build_placebo(D, rows, flag_cache)
        base, base_days = baseline_daily(D)
        S = run_stats(rows, win, glob, base)
        S["baseline_days"] = base_days
        S["skips"] = skips
        mixd = {}
        for sp in ("DEV", "VAL"):
            sel = sub(rows, split=sp)
            mixd[sp] = {c: sum(1 for r in sel if r["cycle"] == c) for c in ("BULL", "BASE", "BEAR")}
        gd = tt.gate_days(D)
        mix = ("gate = BTC < SMA200d on %d DEV and %d VAL days (all bear by gate). Entries by smoothed BTC cycle state: "
               "DEV BULL %d / BASE(range) %d / BEAR %d; VAL BULL %d / BASE(range) %d / BEAR %d." % (
                   gd["DEV"], gd["VAL"], mixd["DEV"]["BULL"], mixd["DEV"]["BASE"], mixd["DEV"]["BEAR"],
                   mixd["VAL"]["BULL"], mixd["VAL"]["BASE"], mixd["VAL"]["BEAR"]))
        v8, d8 = sub(rows8, split="VAL"), sub(rows8, split="DEV")
        b8 = week_block_bootstrap(v8, "net_R")
        resc = ("VAL n %d, weeks %d, net R %s (CI %s..%s), total R %s; DEV n %d, net R %s." % (
            len(v8), b8["weeks"], fmt(mean([r["net_R"] for r in v8])), fmt(b8["ci_low"]), fmt(b8["ci_high"]),
            fmt(mean([r["total_R"] for r in v8])), len(d8), fmt(mean([r["net_R"] for r in d8]))))
        S["rescue8"] = dict(val_n=len(v8), val_weeks=b8["weeks"], val_net_R=mean([r["net_R"] for r in v8]),
                            val_ci=[b8["ci_low"], b8["ci_high"]], dev_n=len(d8), dev_net_R=mean([r["net_R"] for r in d8]))
        tabs = []
        for nm, sel in (("VAL", sub(rows, split="VAL")), ("DEV", sub(rows, split="DEV")), ("ALL", rows)):
            tabs.append(md_group("by smoothed BTC cycle state (%s)" % nm, group_rows(sel, lambda r: r["cycle"])))
            tabs.append(md_group("by year of entry (%s)" % nm, group_rows(sel, entry_year)))
            tabs.append(md_group("by BTC brain label (%s)" % nm, group_rows(sel, lambda r: r["label"])))
            tabs.append(md_group("by exit reason (%s)" % nm, group_rows(sel, lambda r: r["exit_reason"])))
        (HERE / "tables.md").write_text("\n".join(tabs), encoding="utf-8")
        md = result_md(S, mix, resc) + "\n## Tables\n\n" + "\n".join(tabs)
        (HERE / "RESULT.md").write_text(md, encoding="utf-8")
        keep = {k: S[k] for k in ("n_dev", "n_val", "val_weeks", "dev_weeks", "verdict", "verdict_detail", "bars", "kill",
                                  "carry_only", "sign_flip", "holm_family9_worst_p", "strat_per_day_net_val",
                                  "strat_per_day_net_dev", "baseline_per_day", "rescue8", "bear_periods")}
        for k in ("val_net_R", "val_gross_R", "val_fee_R", "val_total_R", "dev_net_R", "dev_gross_R", "dev_total_R",
                  "val_boot", "dev_boot", "val_episode", "placebo_win_val", "placebo_glob_val", "ex_best", "ex_best5",
                  "top_coin", "loyo_val", "ex_ended_val", "ex_lunaftt_val", "val_fund_covered"):
            keep[k] = S[k]
        (HERE / "results.json").write_text(json.dumps(keep, indent=1, default=str), encoding="utf-8")
        print(S["verdict"], S["verdict_detail"])
    finally:
        core.slot_release(lk)


if __name__ == "__main__":
    main()
