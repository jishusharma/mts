"""T8 statistics. Pure functions over trade dicts (schema of t8_core.trades_for_seg) plus the file side (main).
See PRE_REG.md pass bars. Nothing here changes a rule; every threshold is the frozen one.
"""
import sys
import json
import math
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t8_core as core  # noqa: E402

SEED = core.SEED
NBOOT = 2000
NDRAW = 1000
BLOCK = 2


def _pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def _mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def sub(rows, **kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


# ---------------------------------------------------------------- bootstrap (moving block over calendar weeks)
def block_boot(weeks, vals, nboot=NBOOT, seed=SEED, block=BLOCK):
    """weeks: Monday-based week index per trade; vals: value per trade. Calendar weeks from first to last week, empty
    weeks kept (zero trades). Moving block of `block` consecutive weeks; resampled mean = sum / number of trades."""
    weeks = np.asarray(weeks, np.int64)
    vals = np.asarray(vals, float)
    keep = vals == vals
    weeks, vals = weeks[keep], vals[keep]
    if len(vals) == 0:
        return dict(n=0, weeks=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    w0 = int(weeks.min())
    W = int(weeks.max()) - w0 + 1
    s = np.bincount(weeks - w0, weights=vals, minlength=W)
    n = np.bincount(weeks - w0, minlength=W).astype(float)
    rng = np.random.default_rng(seed)
    b = min(block, W)
    nb = int(math.ceil(W / b))
    starts = rng.integers(0, W - b + 1, (nboot, nb))
    idx = (starts[:, :, None] + np.arange(b)[None, None, :]).reshape(nboot, -1)
    den = n[idx].sum(1)
    den = np.where(den == 0, np.nan, den)
    m = s[idx].sum(1) / den
    m = m[~np.isnan(m)]
    return dict(n=int(len(vals)), weeks=int(len(set(weeks.tolist()))), mean=float(vals.mean()),
                ci_low=_pct(m, 2.5), ci_high=_pct(m, 97.5), p_le0=float((np.sum(m <= 0) + 1) / (len(m) + 1)))


def boot_rows(rows, val="net_R", nboot=NBOOT, seed=SEED):
    return block_boot([r["week"] for r in rows], [r[val] for r in rows], nboot, seed)


def describe(rows, val="net_R"):
    v = np.array([r[val] for r in rows if r[val] == r[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                sd=float(v.std(ddof=1)) if len(v) > 1 else float("nan"), worst=float(v.min()), best=float(v.max()))


def week_sums(rows, val="net_R"):
    d = {}
    for r in rows:
        if r[val] == r[val]:
            d[r["week"]] = d.get(r["week"], 0.0) + r[val]
    return d


def ex_best_weeks(rows, k, val="net_R"):
    sums = week_sums(rows, val)
    drop = set(sorted(sums, key=lambda w: -sums[w])[:k])
    rest = [r[val] for r in rows if r["week"] not in drop and r[val] == r[val]]
    return dict(k=k, dropped=len(drop), n=len(rest), mean=_mean(rest))


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
        top = max(sums, key=lambda c: sums[c])
        removed.append(top)
        rest = [r[val] for r in rows if r["coin"] not in removed]
        out.append(dict(removed=list(removed), n=len(rest), mean=_mean(rest)))
    return out


def leave_one_year_out(rows, val="net_R"):
    years = sorted({r["entry_date"][:4] for r in rows})
    out = {}
    for y in years:
        rest = [r[val] for r in rows if r["entry_date"][:4] != y and r[val] == r[val]]
        out[y] = dict(n=len(rest), mean=_mean(rest))
    return out


def group_table(rows, keyfn, val="net_R"):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), []).append(r)
    return {k: describe(v, val) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


# ---------------------------------------------------------------- candidates (placebo and baselines)
def candidate_bars(tr, window=True, cap=core.CAND_CAP, rng=None):
    """Bars t' of the same coin and segment: gate true, alive, date-ok, same split, (within +/-56 days), t' != t,
    entry t'+1 passes the availability rules and no LUNA/FTT hole. Capped at `cap` by one seeded draw."""
    seg, t = tr["seg"], tr["sig_t"]
    ok = seg.gate & seg.alive & seg.date_ok
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return []
    ms = seg.ms[idx]
    same = (ms < core.DEV_END_MS) == (tr["split"] == "DEV")
    keep = same & (idx != t)
    if window:
        keep &= np.abs(ms - seg.ms[t]) <= core.PLACEBO_WINDOW_DAYS * core.DAY
    idx = idx[keep]
    e = idx + 1
    cap_bars = seg.cell["cap"]
    last = e + cap_bars - 1
    good = e < seg.n
    if not (seg.is_final and seg.ended):
        good &= last < seg.n
    idx = idx[good]
    if core.HOLES.get(seg.coin) is not None:
        idx = np.array([i for i in idx if not core.hole_hit(seg, i + 1, min(i + cap_bars, seg.n - 1))], dtype=int)
    if len(idx) > cap:
        rng = rng or np.random.default_rng(SEED)
        idx = np.sort(rng.choice(idx, size=cap, replace=False))
    return [int(i) for i in idx]


def path_value(seg, tp, side, sp, tgt, fund, mode):
    """Leg started on signal bar tp (entry tp+1 open). mode: 'placebo' (stop sp / target tgt), 'bracket' (stop=target=sp),
    'hold' (no stop, no target). Returns (net_R_for_real_stop, net_pct, bars)."""
    e = tp + 1
    last = min(e + seg.cell["cap"] - 1, seg.n - 1)
    entry = float(seg.o[e])
    if mode == "hold":
        k, px = last, float(seg.c[last])
    else:
        t_pct = sp if mode == "bracket" else tgt
        stop = entry * (1 - side * sp)
        target = entry * (1 + side * t_pct)
        k, px, _ = core.simulate(seg, e, side, entry, stop, target, last)
    gross = side * (px / entry - 1.0)
    end_ms = int(seg.ms[k]) + seg.cell["bar"]
    fp, _ = core.funding_part(fund, int(seg.ms[e]), end_ms, side)
    net = gross - core.FEE_RT - fp
    return net / sp, net, k - e + 1


def placebo_eval(real, funds, window=True, with_baselines=False, seed=SEED, ndraw=NDRAW):
    """-> dict. Same-window or global candidates; one draw = mean over trades of one random candidate's net R."""
    rng_c = np.random.default_rng(seed)
    per_R, mean_cand, daily_pb, daily_hold, daily_real, used_rows = [], [], [], [], [], []
    skipped = 0
    for tr in real:
        seg = tr["seg"]
        cands = candidate_bars(tr, window=window, rng=rng_c)
        if not cands:
            skipped += 1
            continue
        side, sp, tgt = tr["side"], tr["stop_pct"], tr["tgt_pct"]
        fund = funds.get(tr["coin"])
        vals = np.array([path_value(seg, tp, side, sp, tgt, fund, "placebo")[0] for tp in cands])
        per_R.append(vals)
        mean_cand.append(float(vals.mean()))
        used_rows.append(tr)
        if with_baselines:
            bar_days = seg.cell["bar"] / core.DAY
            pb, hd = [], []
            for tp in cands:
                _, n1, b1 = path_value(seg, tp, side, sp, tgt, fund, "bracket")
                pb.append(n1 / (b1 * bar_days))
                _, n2, b2 = path_value(seg, tp, side, sp, tgt, fund, "hold")
                hd.append(n2 / (b2 * bar_days))
            daily_pb.append(float(np.mean(pb)))
            daily_hold.append(float(np.mean(hd)))
            daily_real.append(tr["net"] / (tr["bars"] * bar_days))
    if not used_rows:
        return dict(n=0, skipped=skipped)
    rng = np.random.default_rng(seed)
    acc = np.zeros(ndraw)
    for vals in per_R:
        acc += vals[rng.integers(0, len(vals), ndraw)]
    draws = acc / len(per_R)
    realv = np.array([r["net_R"] for r in used_rows])
    rm = float(realv.mean())
    excess_i = realv - np.array(mean_cand)
    ex_boot = block_boot([r["week"] for r in used_rows], excess_i, NBOOT, seed)
    out = dict(n=len(used_rows), skipped=skipped, real_mean=rm, draw_mean=float(draws.mean()), p975=_pct(draws, 97.5),
               excess=rm - float(draws.mean()), p=float((np.sum(draws >= rm) + 1) / (ndraw + 1)),
               excess_ci_low=ex_boot["ci_low"], excess_ci_high=ex_boot["ci_high"], excess_per_trade_mean=float(excess_i.mean()))
    if with_baselines:
        out.update(real_daily=float(np.mean(daily_real)), bracket_daily=float(np.mean(daily_pb)),
                   hold_daily=float(np.mean(daily_hold)))
    return out


# ---------------------------------------------------------------- verdict assembly
def assemble_verdict(b):
    """b: dict of booleans/values. Order fixed in PRE_REG: UNDERPOWERED, FAIL, SIDE-SPLIT, FRAGILE, PASS."""
    if not b["bar1"]:
        return "UNDERPOWERED"
    kill = b["kill_val_le0"] or b["kill_mirror_le0"] or b["kill_placebo"]
    if kill or not (b["bar2"] and b["bar3"] and b["bar4"] and b["bar5"] and b["bar6"] and b["mirror_pos"]):
        return "FAIL"
    if not b["sides_pos"]:
        return "SIDE-SPLIT"
    if not (b["bar7"] and b["bar8"] and b["worst_week_ok"]):
        return "FRAGILE"
    return "PASS" + (" MULTIPLICITY-FLAGGED" if b.get("holm_adj", 0.0) > 0.05 else "")


def holm(ps):
    """Holm-Bonferroni adjusted p-values for a dict {name: p}."""
    names = sorted(ps, key=lambda k: ps[k])
    m = len(names)
    adj, run = {}, 0.0
    for i, k in enumerate(names):
        run = max(run, min(1.0, (m - i) * ps[k]))
        adj[k] = run
    return adj


def run_cell(trades, funds, tf, episodes=None, nboot=NBOOT, ndraw=NDRAW, do_placebo=True):
    """trades: all trades of one cell. Returns (summary dict, tables markdown)."""
    val = sub(trades, split="VAL")
    dev = sub(trades, split="DEV")
    S = dict(tf=tf, n_dev=len(dev), n_val=len(val), val_weeks=len({r["week"] for r in val}),
             dev_weeks=len({r["week"] for r in dev}))
    for nm, rows in (("val", val), ("dev", dev)):
        S[nm + "_net_R"] = describe(rows, "net_R")
        S[nm + "_gross_R"] = describe(rows, "gross_R")
        S[nm + "_nofund_R"] = describe(rows, "nofund_R")
        S[nm + "_fee_R_mean"] = _mean([r["fee_R"] for r in rows])
        S[nm + "_net_pct"] = _mean([r["net"] for r in rows]) * 100
        S[nm + "_gross_pct"] = _mean([r["gross"] for r in rows]) * 100
        S[nm + "_fund_not_in_data"] = sum(1 for r in rows if not r["fund_cov"])
        S[nm + "_funding_covered_net_R"] = describe([r for r in rows if r["fund_cov"]], "net_R")
        S[nm + "_ended"] = sum(1 for r in rows if r["ended"])
        S[nm + "_exit_mix"] = {k: sum(1 for r in rows if r["reason"] == k) for k in ("TARGET", "STOP", "STOP_GAP", "TIME")}
        S[nm + "_mirror_net_R"] = describe(rows, "m_net_R")
    S["val_boot"] = boot_rows(val, "net_R", nboot)
    S["val_boot_gross"] = boot_rows(val, "gross_R", nboot)
    S["dev_boot"] = boot_rows(dev, "net_R", nboot)
    diff = [dict(week=r["week"], d=r["net_R"] - r["m_net_R"]) for r in val]
    S["val_real_minus_mirror"] = block_boot([d["week"] for d in diff], [d["d"] for d in diff], nboot)
    S["dev_real_minus_mirror"] = _mean([r["net_R"] - r["m_net_R"] for r in dev])
    S["val_by_side"] = {("long" if s > 0 else "short"): describe(sub(val, side=s)) for s in (1, -1)}
    S["val_by_side_boot"] = {("long" if s > 0 else "short"): boot_rows(sub(val, side=s), "net_R", nboot) for s in (1, -1)}
    S["dev_by_side"] = {("long" if s > 0 else "short"): describe(sub(dev, side=s)) for s in (1, -1)}
    S["ex_best5"] = ex_best_weeks(val, 5)
    S["ex_best2"] = ex_best_weeks(val, 2)
    S["top_coin_removal"] = top_coin_removal(val, 3)
    S["loyo"] = leave_one_year_out(val)
    ws = week_sums(val)
    S["worst_week_R"] = float(min(ws.values())) if ws else float("nan")
    S["val_weekly_mean_sd"] = float(np.std([ws[w] for w in ws], ddof=1)) if len(ws) > 1 else float("nan")
    S["dev_week_sd"] = float(np.std(list(week_sums(dev).values()), ddof=1)) if len(week_sums(dev)) > 1 else float("nan")
    S["ex_ended"] = describe([r for r in val if not r["ended"]])
    S["ex_luna_ftt"] = describe([r for r in val if r["coin"] not in core.HOLES])
    S["ex_ended_dev"] = describe([r for r in dev if not r["ended"]])
    S["ex_luna_ftt_dev"] = describe([r for r in dev if r["coin"] not in core.HOLES])
    if do_placebo:
        S["placebo_window"] = placebo_eval(val, funds, True, True, SEED, ndraw)
        S["placebo_global"] = placebo_eval(val, funds, False, False, SEED, ndraw)
    else:
        S["placebo_window"] = dict(n=0)
        S["placebo_global"] = dict(n=0)
    # episodes (second unit, descriptive)
    if episodes is not None:
        eps = {}
        for r in val:
            ep = episodes.get(r["entry_date"])
            if ep is not None:
                eps.setdefault(ep, []).append(r["net_R"])
        em = np.array([np.mean(v) for v in eps.values()]) if eps else np.array([])
        rng = np.random.default_rng(SEED)
        lo = hi = float("nan")
        if len(em) > 1:
            bm = em[rng.integers(0, len(em), (nboot, len(em)))].mean(1)
            lo, hi = _pct(bm, 2.5), _pct(bm, 97.5)
        S["val_episodes"] = dict(episodes=len(em), trades=int(sum(len(v) for v in eps.values())),
                                 mean_of_episode_means=float(em.mean()) if len(em) else float("nan"),
                                 ci_low=lo, ci_high=hi)
    # bars
    pw, pg = S["placebo_window"], S["placebo_global"]
    bars = dict(
        bar1=bool(S["n_val"] >= 200 and S["val_weeks"] >= 40),
        bar2=bool(S["n_val"] and S["val_net_R"]["mean"] > 0 and S["val_boot"]["ci_low"] > 0),
        bar3=bool(S["n_dev"] and S["dev_net_R"]["mean"] > 0),
        bar4=bool(pw.get("n", 0) > 0 and pw["real_mean"] > pw["p975"] and pw["excess_ci_low"] > 0),
        bar5=bool((S["ex_best5"] if S["val_weeks"] >= 30 else S["ex_best2"])["mean"] > 0),
        bar6=bool(pw.get("n", 0) > 0 and pw.get("real_daily", float("nan")) >= pw.get("bracket_daily", float("inf"))
                  and pw["real_daily"] >= pw.get("hold_daily", float("inf"))),
        bar7=bool(S["top_coin_removal"] and S["top_coin_removal"][0]["mean"] > 0
                  and S["top_coin_removal"][-1]["mean"] > 0),
        bar8=bool(S["loyo"] and all(v["mean"] > 0 for v in S["loyo"].values())),
        mirror_pos=bool(S["val_real_minus_mirror"]["n"] and S["val_real_minus_mirror"]["mean"] > 0),
        sides_pos=bool(all(d.get("n", 0) > 0 and d["mean"] > 0 for d in S["val_by_side"].values())),
        worst_week_ok=bool(S["worst_week_R"] > -4.0),
        kill_val_le0=bool(S["n_val"] == 0 or S["val_net_R"]["mean"] <= 0),
        kill_mirror_le0=bool(S["val_real_minus_mirror"]["n"] == 0 or S["val_real_minus_mirror"]["mean"] <= 0),
        kill_placebo=bool(S["n_val"] >= 200 and pw.get("n", 0) > 0 and not (pw["real_mean"] > pw["p975"])),
    )
    S["bars"] = bars
    S["p_val"] = S["val_boot"]["p_le0"]
    tabs = []
    for nm, rows in (("VAL", val), ("DEV", dev)):
        tabs.append(_md("by year (%s, net R)" % nm, group_table(rows, lambda r: r["entry_date"][:4])))
        tabs.append(_md("by BTC cycle, smoothed (%s, net R)" % nm, group_table(rows, lambda r: r.get("cycle", "NA"))))
        tabs.append(_md("by BTC label (%s, net R)" % nm, group_table(rows, lambda r: r.get("label", "NA"))))
        tabs.append(_md("by side (%s, net R)" % nm, group_table(rows, lambda r: "long" if r["side"] > 0 else "short")))
        tabs.append(_md("by coin (%s, net R)" % nm, group_table(rows, lambda r: r["coin"])))
    S["val_by_year"] = {k: v for k, v in group_table(val, lambda r: r["entry_date"][:4]).items()}
    S["val_by_cycle"] = {k: v for k, v in group_table(val, lambda r: r.get("cycle", "NA")).items()}
    S["val_by_label"] = {k: v for k, v in group_table(val, lambda r: r.get("label", "NA")).items()}
    S["dev_by_cycle"] = {k: v for k, v in group_table(dev, lambda r: r.get("cycle", "NA")).items()}
    S["dev_by_year"] = {k: v for k, v in group_table(dev, lambda r: r["entry_date"][:4]).items()}
    return S, "\n".join(tabs)


def _md(title, tab):
    lines = ["### " + title, "", "| key | n | mean | median | win | sd | worst | best |", "|---|---|---|---|---|---|---|---|"]
    for k, d in tab.items():
        if d["n"] == 0:
            continue
        lines.append("| %s | %d | %+.4f | %+.4f | %.2f | %.3f | %+.2f | %+.2f |" % (
            k, d["n"], d["mean"], d["median"], d["win"], d.get("sd", float("nan")), d["worst"], d["best"]))
    return "\n".join(lines) + "\n"
