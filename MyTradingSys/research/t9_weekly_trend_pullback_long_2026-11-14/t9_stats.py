"""T9 statistics: pure functions over trade dicts (schema of t9_core.trade_from_signal) plus the file-side main().
Pass bars, kill criteria and verdict vocabulary follow PRE_REG.md exactly."""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t9_core as core  # noqa: E402

SEED, NBOOT, NDRAW, BLOCK = 1114, 2000, 1000, 4
CAP_R = 3.0


def pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def week_index(entry_ms):
    """Calendar week ordinal of a Monday (epoch day 0 = Thursday)."""
    return int((entry_ms // core.DAY + 3) // 7)


def sub(rows, **kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


def capped(rows, key="net_R"):
    return [dict(r, **{key: min(r[key], CAP_R)}) for r in rows]


def block_bootstrap(rows, val="net_R", block=BLOCK, nboot=NBOOT, seed=SEED):
    """Moving-block bootstrap over the calendar series of entry weeks (empty weeks included). Resampled mean = sum / count."""
    rows = [r for r in rows if r[val] == r[val]]
    if not rows:
        return dict(n=0, weeks=0, W=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    wk = np.array([week_index(r["entry_ts"]) for r in rows])
    v = np.array([r[val] for r in rows], float)
    lo, hi = int(wk.min()), int(wk.max())
    W = hi - lo + 1
    s = np.zeros(W)
    c = np.zeros(W)
    for i in range(len(rows)):
        s[wk[i] - lo] += v[i]
        c[wk[i] - lo] += 1
    b = min(block, W)
    nb = int(np.ceil(W / b))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, W - b + 1, (nboot, nb))
    offs = np.arange(b)
    idx = (starts[:, :, None] + offs[None, None, :]).reshape(nboot, nb * b)[:, :W]
    ss, cc = s[idx].sum(1), c[idx].sum(1)
    ok = cc > 0
    m = ss[ok] / cc[ok]
    return dict(n=len(rows), weeks=int((c > 0).sum()), W=W, mean=float(s.sum() / c.sum()), ci_low=pct(m, 2.5),
                ci_high=pct(m, 97.5), p_le0=float((np.sum(m <= 0) + 1) / (len(m) + 1)))


def episodes(rows, block=BLOCK):
    """Non-overlapping 4-week blocks from the first entry week that hold at least one trade."""
    if not rows:
        return 0
    wk = sorted({week_index(r["entry_ts"]) for r in rows})
    return len({(w - wk[0]) // block for w in wk})


def placebo_draw(real_vals, cand_lists, ndraw=NDRAW, seed=SEED):
    """real_vals: R of each real trade; cand_lists: per real trade the array of placebo R candidates (empty = skipped)."""
    used = [(rv, np.asarray(c, float)) for rv, c in zip(real_vals, cand_lists) if len(c)]
    skipped = len(real_vals) - len(used)
    if not used:
        return dict(n=0, skipped=skipped, real_mean=float("nan"), draw_mean=float("nan"), p975=float("nan"),
                    excess=float("nan"), p=float("nan"))
    rng = np.random.default_rng(seed)
    acc = np.zeros(ndraw)
    for _, c in used:
        acc += c[rng.integers(0, len(c), ndraw)]
    draws = acc / len(used)
    rm = float(np.mean([u[0] for u in used]))
    return dict(n=len(used), skipped=skipped, real_mean=rm, draw_mean=float(draws.mean()), p975=pct(draws, 97.5),
                excess=rm - float(draws.mean()), p=float((np.sum(draws >= rm) + 1) / (ndraw + 1)),
                pct_rank=float(np.mean(draws < rm) * 100.0))


def ex_best_weeks(rows, k, val="net_R"):
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
        top = max(sums, key=lambda c: sums[c])
        removed.append(top)
        out.append(dict(removed=list(removed), n=len([r for r in rows if r["coin"] not in removed]),
                        mean=mean([r[val] for r in rows if r["coin"] not in removed])))
    return out


def leave_one_year_out(rows, val="net_R"):
    rows = [r for r in rows if r[val] == r[val]]
    years = sorted({r["entry_year"] for r in rows})
    out = {y: dict(n=len([r for r in rows if r["entry_year"] != y]),
                   mean=mean([r[val] for r in rows if r["entry_year"] != y])) for y in years}
    ok = bool(out) and all(d["n"] > 0 and d["mean"] > 0 for d in out.values()) if len(years) > 1 else False
    return dict(by_year=out, all_positive=ok)


def describe(rows, val="net_R"):
    v = np.array([r[val] for r in rows if r[val] == r[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                worst=float(v.min()), best=float(v.max()))


def group_table(rows, keyfn, val="net_R"):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), []).append(r)
    return {k: describe(v, val) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


def in_position_daily(rows):
    """Pooled net % per day in position = sum(net) / sum(days)."""
    d = sum(r["days"] for r in rows)
    return float(sum(r["net"] for r in rows) / d) if d > 0 else float("nan")


def verdict(S):
    """Verdict from the PRE_REG bars. S holds the summary numbers (see run_stats). Returns (verdict, failing_bars, kill, flags)."""
    b = S["bars"]
    fails = [k for k in ("2", "3", "4", "5", "6") if not b[k]]
    kill = [k for k, v in S["kill"].items() if v]
    if not b["1"]:
        return "UNDERPOWERED", ["1"], [], []
    if fails or kill:
        v = "FAIL (first failing bar %s)" % (fails[0] if fails else "none, kill only")
        if kill:
            v += " KILL " + "+".join(kill)
        flags = [x for x in ("7", "8") if not b[x]]
        return v, fails, kill, ["FRAGILE bar " + x for x in flags]
    if not b["7"] or not b["8"]:
        return "FRAGILE", [k for k in ("7", "8") if not b[k]], [], []
    return "PASS", [], [], []


def run_stats(trades, placebo_in, baseline_in, extra=None):
    """trades: all trades with entry_year; placebo_in: {split: {'win': [(real_R, cands)], 'glob': [...]}};
    baseline_in: {split: basket mean daily net return}. Returns the summary dict S."""
    extra = extra or {}
    val, dev = sub(trades, split="VAL"), sub(trades, split="DEV")
    S = dict(n_dev=len(dev), n_val=len(val))
    for nm, rows in (("val", val), ("dev", dev)):
        S[nm + "_weeks"] = len({r["iso_week"] for r in rows})
        S[nm + "_net_R"] = describe(rows, "net_R")
        S[nm + "_gross_R"] = describe(rows, "gross_R")
        S[nm + "_fee_R"] = mean([r["fee_R"] for r in rows])
        S[nm + "_net_pct"] = mean([r["net"] for r in rows])
        S[nm + "_gross_pct"] = mean([r["gross"] for r in rows])
        S[nm + "_net_flat_R"] = mean([r["net_flat_R"] for r in rows])
        S[nm + "_capped_net_R"] = describe(capped(rows), "net_R")
        S[nm + "_boot"] = block_bootstrap(rows)
        S[nm + "_boot_capped"] = block_bootstrap(capped(rows))
        S[nm + "_episodes"] = episodes(rows)
        wm = {}
        for r in rows:
            wm.setdefault(r["iso_week"], []).append(r["net_R"])
        wv = [float(np.mean(v)) for v in wm.values()]
        S[nm + "_week_sd_R"] = float(np.std(wv, ddof=1)) if len(wv) > 1 else float("nan")
        S[nm + "_funding_not_in_data"] = sum(1 for r in rows if not r["funding_covered"])
        S[nm + "_in_pos_daily"] = in_position_daily(rows)
        S[nm + "_exit_reasons"] = {k: sum(1 for r in rows if r["exit_reason"] == k)
                                   for k in sorted({r["exit_reason"] for r in rows})}
    for sp in ("val", "dev"):
        pin = placebo_in.get(sp.upper(), {})
        for key in ("win", "glob"):
            lst = pin.get(key, [])
            S["placebo_%s_%s" % (sp, key)] = placebo_draw([a for a, _ in lst], [c for _, c in lst])
    k_best = 5 if S["val_weeks"] >= 30 else 2
    S["ex_best_capped"] = ex_best_weeks(capped(val), k_best)
    S["ex_best_uncapped"] = ex_best_weeks(val, k_best)
    S["top_coin"] = top_coin_removal(val, 3)
    S["loyo_val"] = leave_one_year_out(val)
    S["loyo_pooled"] = leave_one_year_out(trades)
    S["baseline"] = baseline_in
    S["ex_ended_val"] = describe([r for r in val if not r["ended"]])
    S["ex_luna_ftt_val"] = describe([r for r in val if r["coin"] not in ("LUNA", "FTT")])
    S["ex_ended_dev"] = describe([r for r in dev if not r["ended"]])
    S["ex_luna_ftt_dev"] = describe([r for r in dev if r["coin"] not in ("LUNA", "FTT")])
    S.update(extra)
    pv = S["placebo_val_win"]
    vb = S["val_boot"]
    base_val = baseline_in.get("VAL", float("nan"))
    base_dev = baseline_in.get("DEV", float("nan"))
    ok1 = S["n_val"] >= 30 and S["val_weeks"] >= 20
    S["bars"] = {
        "1": bool(ok1),
        "2": bool(ok1 and S["val_net_R"].get("n", 0) > 0 and S["val_net_R"]["mean"] > 0 and vb["ci_low"] > 0),
        "3": bool(S["dev_net_R"].get("n", 0) >= 10 and S["dev_net_R"]["mean"] > 0),
        "4": bool(pv["n"] > 0 and pv["real_mean"] >= pv["p975"] and pv["excess"] > 0),
        "5": bool(S["ex_best_capped"]["n"] > 0 and S["ex_best_capped"]["mean"] > 0),
        "6": bool(S["val_in_pos_daily"] == S["val_in_pos_daily"] and base_val == base_val
                  and S["val_in_pos_daily"] >= base_val),
        "7": bool(len(S["top_coin"]) == 3 and S["top_coin"][-1]["mean"] > 0),
        "8": bool(S["loyo_val"]["all_positive"]),
    }
    S["dev_only_positive"] = bool(S["dev_net_R"].get("n", 0) and S["dev_net_R"]["mean"] > 0
                                  and S["val_net_R"].get("n", 0) and S["val_net_R"]["mean"] <= 0)
    S["kill"] = dict(
        a_val_mean_le0=bool(S["val_net_R"].get("n", 0) > 0 and S["val_net_R"]["mean"] <= 0),
        b_placebo=bool(pv["n"] > 0 and S["n_val"] >= 60 and pv["real_mean"] <= pv["p975"]),
        c_below_basket_both=bool(S["val_in_pos_daily"] < base_val and S["dev_in_pos_daily"] < base_dev))
    S["bar3_underpowered"] = S["dev_net_R"].get("n", 0) < 10
    S["holm_p_study"] = vb["p_le0"]
    S["holm_p_family_worst"] = min(1.0, 9 * vb["p_le0"]) if vb["n"] else float("nan")
    S["verdict"], S["failing"], S["kill_fired"], S["flags"] = verdict(S)
    if S["dev_only_positive"]:
        S["flags"] = list(S["flags"]) + ["FRAGILE dev-only positive"]
    return S


def fmt(d, k="mean"):
    return "%+.3f" % d[k] if d.get("n", 0) else "NA"


def md_table(title, tab):
    lines = ["### " + title, "", "| key | n | mean R | median | win | worst | best |", "|---|---|---|---|---|---|---|"]
    for k, d in tab.items():
        if d["n"]:
            lines.append("| %s | %d | %+.3f | %+.3f | %.2f | %+.2f | %+.2f |" % (k, d["n"], d["mean"], d["median"],
                                                                              d["win"], d["worst"], d["best"]))
    return "\n".join(lines) + "\n"
