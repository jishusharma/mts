"""T7 statistics. Pure functions over lists of trade dicts (schema of t7_core.trade_at); main() touches data and files.
Primary metric: net R (net return after 12 bp fee and real funding where cached, divided by the stop distance).
Units: ISO entry week with a 4-week moving-block bootstrap; episode as the second unit. Never the trade.
"""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t7_core as core  # noqa: E402

SEED = 1114
NBOOT = 2000
NDRAW = 1000
BLOCK = 4
WINDOW_WEEKS = 8
FAMILY_CELLS = 9


def _pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def _mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def sub(rows, **kw):
    return [r for r in rows if all(r.get(k) == v for k, v in kw.items())]


def week_arrays(rows, val="net_R"):
    """Calendar-contiguous weekly (sum, count) arrays from the first to the last entry week of the rows."""
    rows = [r for r in rows if r[val] == r[val]]
    if not rows:
        return np.array([]), np.array([])
    lo = min(r["week_i"] for r in rows)
    hi = max(r["week_i"] for r in rows)
    s = np.zeros(hi - lo + 1)
    n = np.zeros(hi - lo + 1)
    for r in rows:
        s[r["week_i"] - lo] += r[val]
        n[r["week_i"] - lo] += 1
    return s, n


def block_bootstrap(rows, val="net_R", nboot=NBOOT, seed=SEED, block=BLOCK):
    """Moving-block bootstrap over calendar ISO weeks (block of 4 consecutive weeks, blocks start anywhere). The resampled
    mean = sum of returns / number of trades in the drawn weeks."""
    rows = [r for r in rows if r[val] == r[val]]
    nan = float("nan")
    if not rows:
        return dict(n=0, weeks=0, mean=nan, ci_low=nan, ci_high=nan, p_le0=nan)
    s, n = week_arrays(rows, val)
    W = len(s)
    b = min(block, W)
    nb = int(np.ceil(W / b))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, W - b + 1, (nboot, nb))
    idx = (starts[:, :, None] + np.arange(b)[None, None, :]).reshape(nboot, nb * b)[:, :W]
    m = s[idx].sum(1) / n[idx].sum(1)
    return dict(n=len(rows), weeks=int((n > 0).sum()), mean=float(s.sum() / n.sum()), ci_low=_pct(m, 2.5),
                ci_high=_pct(m, 97.5), p_le0=float((np.sum(m <= 0) + 1) / (nboot + 1)))


def episodes(rows, gap_days=28):
    """Entries sorted by date; an entry chains to the current episode when its gap to the previous entry is < 28 days.
    -> list of lists of rows."""
    rs = sorted(rows, key=lambda r: (r["entry_ts"], r["coin"]))
    out, last = [], None
    for r in rs:
        if last is not None and (r["entry_ts"] - last) < gap_days * core.DAY:
            out[-1].append(r)
        else:
            out.append([r])
        last = r["entry_ts"]
    return out


def episode_stats(rows, val="net_R", nboot=NBOOT, seed=SEED):
    eps = episodes([r for r in rows if r[val] == r[val]])
    vals = np.array([_mean([r[val] for r in e]) for e in eps])
    nan = float("nan")
    if not len(vals):
        return dict(episodes=0, mean=nan, ci_low=nan, ci_high=nan, ex_best2=nan)
    rng = np.random.default_rng(seed)
    m = vals[rng.integers(0, len(vals), (nboot, len(vals)))].mean(1)
    rest = np.sort(vals)[:-2] if len(vals) > 2 else np.array([])
    return dict(episodes=int(len(vals)), mean=float(vals.mean()), ci_low=_pct(m, 2.5), ci_high=_pct(m, 97.5),
                ex_best2=float(rest.mean()) if len(rest) else nan)


def ex_best_weeks(rows, k=5, val="net_R"):
    rows = [r for r in rows if r[val] == r[val]]
    sums = {}
    for r in rows:
        sums[r["iso_week"]] = sums.get(r["iso_week"], 0.0) + r[val]
    drop = set(sorted(sums, key=lambda w: -sums[w])[:k])
    rest = [r[val] for r in rows if r["iso_week"] not in drop]
    return dict(k=k, dropped=sorted(drop), n=len(rest), mean=_mean(rest))


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
        out.append(dict(removed=list(removed), n=len(rest), mean=_mean(rest)))
    return out


def leave_one_year_out(rows, val="net_R"):
    years = sorted({r["iso_week"][:4] for r in rows})
    out = {}
    for y in years:
        rest = [r[val] for r in rows if r["iso_week"][:4] != y and r[val] == r[val]]
        out[y] = dict(n=len(rest), mean=_mean(rest))
    return out


def describe(rows, val="net_R"):
    v = np.array([r[val] for r in rows if r[val] == r[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                worst=float(v.min()), best=float(v.max()), weeks=len({r["iso_week"] for r in rows}))


def group_table(rows, keyfn, val="net_R"):
    g = {}
    for r in rows:
        g.setdefault(keyfn(r), []).append(r)
    return {k: describe(v, val) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


# ---------------------------------------------------------------- placebo
def placebo_from_candidates(real_vals, cand_lists, ndraw=NDRAW, seed=SEED):
    """real_vals[i] = real net R of trade i; cand_lists[i] = array of net R of its placebo candidates (same coin, same DD
    flag, same stop %, same exit). Trades without candidates are skipped. One draw = mean over matched trades."""
    rng = np.random.default_rng(seed)
    acc, used, rv = np.zeros(ndraw), 0, []
    for r, arr in zip(real_vals, cand_lists):
        arr = np.asarray([x for x in arr if x == x], float)
        if not len(arr):
            continue
        acc += arr[rng.integers(0, len(arr), ndraw)]
        used += 1
        rv.append(r)
    nan = float("nan")
    if used == 0:
        return dict(n=0, skipped=len(real_vals), real_mean=nan, draw_mean=nan, p975=nan, excess=nan, p=nan)
    d = acc / used
    rm = float(np.mean(rv))
    return dict(n=used, skipped=len(real_vals) - used, real_mean=rm, draw_mean=float(d.mean()), p975=_pct(d, 97.5),
                excess=rm - float(d.mean()), p=float((np.sum(d >= rm) + 1) / (ndraw + 1)))


def placebo_candidates(real, segmap, fundmap, thin_ms, same_window=True, val="net_R"):
    """Per real trade: net R of every DD-flagged Monday entry of the same coin segment and split (not thin), with the real
    trade's stop % and the same exit. same_window: entry week within +/- 8 ISO weeks of the real trade (real week excluded)."""
    out = []
    for r in real:
        seg = segmap[(r["coin"], r["seg"])]
        fund = fundmap.get(r["coin"])
        vals = []
        for (_k, s, d0) in seg.dd_weeks():
            sig = int(seg.ms[s])
            if core.split_of(sig) != r["split"] or sig in thin_ms:
                continue
            wi = core.week_index(int(seg.ms[d0]))
            if wi == r["week_i"]:
                continue
            if same_window and abs(wi - r["week_i"]) > WINDOW_WEEKS:
                continue
            t = core.trade_at(seg, d0, fund, risk=r["risk"])
            if t is not None:
                vals.append(t[val])
        out.append(vals)
    return out


# ---------------------------------------------------------------- baseline basket
def basket_daily(real, segmap, fundmap, thin_ms):
    """Equal-weight basket of every coin in DD state entered on the same Mondays (distinct real entry Mondays), held 28
    days, no stop, 12 bp + funding. Returns mean net return per day in position, pooled per Monday then averaged."""
    mons = sorted({r["entry_ts"] for r in real})
    monset = set(mons)
    per = {}
    for seg in segmap.values():
        for (_k, s, d0) in seg.dd_weeks():
            em = int(seg.ms[d0])
            if em in monset and int(seg.ms[s]) not in thin_ms:
                t = core.trade_at(seg, d0, fundmap.get(seg.name), use_stop=False)
                if t is not None:
                    per.setdefault(em, []).append(t)
    vals = []
    for em, ts in per.items():
        vals.append(sum(t["net"] for t in ts) / sum(t["days"] for t in ts))
    return dict(mondays=len(vals), daily=_mean(vals), mean_trade_net=_mean([t["net"] for ts in per.values() for t in ts]),
                n_trades=sum(len(v) for v in per.values()))


def real_daily(rows):
    d = sum(r["days"] for r in rows)
    return sum(r["net"] for r in rows) / d if d else float("nan")


# ---------------------------------------------------------------- verdict
def build_bars(S):
    v = S["val_R"]
    ok1 = S["n_val"] >= 30 and S["val_weeks"] >= 20
    pb = S["placebo_window"]
    eps_ok = S["val_episodes"]["episodes"] >= 8
    ex5 = S["ex_best_weeks"]["mean"] > 0
    ex_ep = (S["val_episodes"]["ex_best2"] > 0) if eps_ok else True
    bars = {
        "1_power": ok1,
        "2_val_ci": bool(ok1 and v["mean"] > 0 and S["val_boot"]["ci_low"] > 0),
        "3_dev_sign": bool(S["dev_R"].get("n", 0) > 0 and S["dev_R"]["mean"] > 0),
        "4_placebo": bool(pb["n"] > 0 and pb["real_mean"] > pb["p975"] and pb["excess"] > 0),
        "5_ex_best": bool(ex5 and ex_ep),
        "6_baseline": bool(S["real_daily"] == S["real_daily"] and S["baseline"]["daily"] == S["baseline"]["daily"]
                           and S["real_daily"] >= S["baseline"]["daily"]),
        "7_top_coin": bool(S["top_coin_removal"] and S["top_coin_removal"][0]["mean"] > 0),
        "8_loyo": bool(S["loyo"] and all(x["mean"] > 0 for x in S["loyo"].values())),
    }
    S["fragile_top3"] = bool(len(S["top_coin_removal"]) >= 3 and S["top_coin_removal"][-1]["mean"] <= 0)
    S["kill"] = dict(a_val_net_le0=bool(S["val_weeks"] >= 20 and v.get("n", 0) and v["mean"] <= 0),
                     b_placebo_not_above=bool(S["n_val"] >= 100 and pb["n"] > 0 and pb["real_mean"] <= pb["p975"]))
    st = S["strata_val"]
    pos = lambda k: (k in st and st[k].get("n", 0) > 0 and st[k]["mean"] > 0)  # noqa: E731
    S["sign_flip"] = bool(v.get("n", 0) and v["mean"] > 0 and pos("BULL") and not pos("BEAR") and not pos("BASE"))
    return bars


def verdict(S):
    b = S["bars"]
    flags = []
    if not b["1_power"]:
        return "UNDERPOWERED", flags
    if S["sign_flip"]:
        flags.append("SIGN-FLIP")
    kill = any(S["kill"].values())
    first_fail = next((k for k in ("2_val_ci", "3_dev_sign", "4_placebo", "5_ex_best", "6_baseline") if not b[k]), None)
    if kill or first_fail:
        flags.insert(0, "KILL" if kill else "first failing bar " + first_fail)
        return "FAIL", flags
    if not b["7_top_coin"] or not b["8_loyo"] or S["fragile_top3"]:
        return "FRAGILE", flags
    if S["sign_flip"]:
        return "FAIL", flags
    return "PASS", flags


# ---------------------------------------------------------------- run
def run_stats(trades, segmap, fundmap, alive, btc_rows=None, nboot=NBOOT, ndraw=NDRAW, seed=SEED):
    thin_ms = {ms for ms, c in alive.items() if c < core.MIN_ALIVE_COINS}
    thin = [t for t in trades if t["signal_ts"] in thin_ms]
    use = [t for t in trades if t["signal_ts"] not in thin_ms and t["net_R"] == t["net_R"]]
    val, dev = sub(use, split="VAL"), sub(use, split="DEV")
    S = dict(n_total=len(trades), n_thin_excluded=len(thin), n_dev=len(dev), n_val=len(val),
             val_weeks=len({r["iso_week"] for r in val}), dev_weeks=len({r["iso_week"] for r in dev}))
    for nm, rows in (("val", val), ("dev", dev)):
        S[nm + "_R"] = describe(rows, "net_R")
        S[nm + "_gross_R"] = describe(rows, "gross_R")
        S[nm + "_fee_R"] = describe(rows, "fee_R")
        S[nm + "_pct"] = describe(rows, "net")
        S[nm + "_gross_pct"] = describe(rows, "gross")
        S[nm + "_nofund_pct"] = describe(rows, "net_nofund")
        S[nm + "_funding_not_in_data"] = sum(1 for r in rows if r["funding_rule"] == "NOT_IN_DATA")
        S[nm + "_ended"] = sum(1 for r in rows if r["ended"])
        S[nm + "_stop_exits"] = sum(1 for r in rows if r["exit_reason"].startswith("STOP"))
    S["val_boot"] = block_bootstrap(val, "net_R", nboot, seed)
    S["val_boot_pct"] = block_bootstrap(val, "net", nboot, seed)
    S["dev_boot"] = block_bootstrap(dev, "net_R", nboot, seed)
    wk_s, wk_n = week_arrays(dev, "net_R")
    wm = wk_s[wk_n > 0] / wk_n[wk_n > 0] if len(wk_s) else np.array([])
    S["dev_week_sd_R"] = float(wm.std(ddof=1)) if len(wm) > 1 else float("nan")
    S["val_episodes"] = episode_stats(val, "net_R", nboot, seed)
    S["dev_episodes"] = episode_stats(dev, "net_R", nboot, seed)
    k = 5 if S["val_weeks"] >= 30 else 2
    S["ex_best_weeks"] = ex_best_weeks(val, k)
    S["top_coin_removal"] = top_coin_removal(val, 3)
    S["loyo"] = leave_one_year_out(val)
    S["loyo_all"] = leave_one_year_out(use)
    cw = placebo_candidates(val, segmap, fundmap, thin_ms, True)
    cg = placebo_candidates(val, segmap, fundmap, thin_ms, False)
    rv = [r["net_R"] for r in val]
    S["placebo_window"] = placebo_from_candidates(rv, cw, ndraw, seed)
    S["placebo_global"] = placebo_from_candidates(rv, cg, ndraw, seed)
    S["baseline"] = basket_daily(val, segmap, fundmap, thin_ms)
    S["baseline_dev"] = basket_daily(dev, segmap, fundmap, thin_ms)
    S["real_daily"] = real_daily(val)
    S["real_daily_dev"] = real_daily(dev)
    S["strata_val"] = group_table(val, lambda r: r.get("cycle", "NA"))
    S["strata_dev"] = group_table(dev, lambda r: r.get("cycle", "NA"))
    S["by_year_val"] = group_table(val, lambda r: r["iso_week"][:4])
    S["by_year_dev"] = group_table(dev, lambda r: r["iso_week"][:4])
    S["val_bear_boot"] = block_bootstrap(sub(val, cycle="BEAR"), "net_R", nboot, seed)
    S["val_base_boot"] = block_bootstrap(sub(val, cycle="BASE"), "net_R", nboot, seed)
    S["val_ex_ended"] = describe([r for r in val if not r["ended"]])
    S["val_ex_luna_ftt"] = describe([r for r in val if r["coin"] not in ("LUNA", "FTT")])
    S["dev_ex_ended"] = describe([r for r in dev if not r["ended"]])
    S["dev_ex_luna_ftt"] = describe([r for r in dev if r["coin"] not in ("LUNA", "FTT")])
    S["val_by_coin"] = group_table(val, lambda r: r["coin"])
    S["bars"] = build_bars(S)
    S["verdict"], S["flags"] = verdict(S)
    p = S["val_boot"]["p_le0"]
    S["holm_study_p"] = p
    S["holm_family_p"] = min(1.0, FAMILY_CELLS * p) if p == p else float("nan")
    S["btc_row"] = btc_rows
    return S


# ---------------------------------------------------------------- BTC descriptive row (a)
def btc_basket_row(btc, state, segmap, fundmap, thin_ms):
    """Descriptive: for each BTC reclaim event, a basket of coins in DD state at that completed weekly bar, entered at the
    Monday open, exited at the open after the first BTC weekly close below the reclaim-week low, or after 26 weeks.
    No stop; 12 bp + funding. BTC alone is the sign check."""
    out = []
    for ev in core.btc_reclaim_events(btc, state):
        k = ev["k"]
        exit_ms = None
        for j in range(k + 1, min(k + 27, len(btc.wc))):
            if btc.wc[j] < ev["reclaim_low"]:
                e = int(btc.wclose_idx[j]) + 1
                exit_ms = int(btc.ms[e]) if e < btc.n else None
                break
        if exit_ms is None:
            e = int(btc.wstart[k]) + 7 * 27
            exit_ms = int(btc.ms[e]) if e < btc.n else None
        entry_ms = int(btc.ms[ev["d0"]])
        rets, btc_ret = [], float("nan")
        for seg in list(segmap.values()) + [btc]:
            if seg is not btc and seg.name == "BTC":
                continue
            ii = np.where(seg.ms == entry_ms)[0]
            if not len(ii):
                continue
            d0 = int(ii[0])
            s = d0 - 1
            if seg is not btc and not (s >= 0 and seg.dd_state(s, seg.c[s]) and seg.ms[s] == btc.ms[ev["s"]]
                                       and int(seg.ms[s]) not in thin_ms):
                continue
            if exit_ms is None:
                continue
            jj = np.where(seg.ms == exit_ms)[0]
            if len(jj):
                xi, px = int(jj[0]), float(seg.o[int(jj[0])])
            elif seg.ended and seg.ms[-1] < exit_ms:
                xi, px = seg.n - 1, float(seg.c[-1])
            else:
                continue
            fc, _ = core.funding_cost(fundmap.get(seg.name), entry_ms, int(seg.ms[min(xi, seg.n - 1)]) + core.DAY)
            r = px / float(seg.o[d0]) - 1.0 - core.FEE_RT - fc
            if seg is btc:
                btc_ret = r
            else:
                rets.append(r)
        out.append(dict(signal_date=core.date_of(btc.ms[ev["s"]]), entry_date=core.date_of(entry_ms),
                        exit_date=core.date_of(exit_ms) if exit_ms else None, n_coins=len(rets),
                        basket_net=_mean(rets), btc_net=btc_ret,
                        split=core.split_of(int(btc.ms[ev["s"]]))))
    return out


# ---------------------------------------------------------------- file side
NUMERIC = ("entry_px", "stop", "risk", "exit_px", "gross", "fee", "funding", "net_nofund", "net", "gross_R", "net_R",
           "fee_R")
INTS = ("signal_ts", "entry_ts", "exit_ts", "d0", "seg", "days", "week_i")


def read_trades_csv(path):
    import csv
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUMERIC:
                r[k] = float(r[k]) if r.get(k) not in (None, "") else float("nan")
            for k in INTS:
                r[k] = int(r[k])
            r["ended"] = r["ended"] == "True"
            out.append(r)
    return out


def _f(x, fmt="%+.3f"):
    return "n/a" if x != x else fmt % x


def render_result(S, bars_text):
    v, d = S["val_R"], S["dev_R"]
    reg = {}
    for split, rows in (("VAL", S["strata_val"]), ("DEV", S["strata_dev"])):
        tot = sum(x["n"] for x in rows.values()) or 1
        reg[split] = " ".join("%s %.0f%%" % (k, 100.0 * x["n"] / tot) for k, x in rows.items())
    L = []
    L.append("**T7 cycle-bottom weekly-reclaim long: %s%s. VAL n %d trades in %d entry weeks, net %s R (CI %s to %s), "
             "gross %s R, fee %s R per trade.**" % (
                 S["verdict"], (" (" + "; ".join(S["flags"]) + ")") if S["flags"] else "", S["n_val"], S["val_weeks"],
                 _f(v.get("mean", float("nan"))), _f(S["val_boot"]["ci_low"]), _f(S["val_boot"]["ci_high"]),
                 _f(S["val_gross_R"].get("mean", float("nan"))), _f(S["val_fee_R"].get("mean", float("nan"), ), "%.4f")))
    L.append("")
    L.append("Regime mix: BTC smoothed cycle state of the entry day, VAL: %s; DEV: %s (trades, not weeks; the market is "
             "mostly bear or base at these entries by construction of the 55%% drawdown gate)." % (reg["VAL"], reg["DEV"]))
    L.append("")
    L.append("| Row | n trades | entry weeks | mean net R | CI low | CI high | gross R | net % | note |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for nm, key, bk in (("VAL", "val", "val_boot"), ("DEV", "dev", "dev_boot")):
        L.append("| %s | %d | %d | %s | %s | %s | %s | %s | funding NOT_IN_DATA on %d, ENDED %d, stop exits %d |" % (
            nm, S["n_" + key], S[key + "_R"].get("weeks", 0), _f(S[key + "_R"].get("mean", float("nan"))),
            _f(S[bk]["ci_low"]), _f(S[bk]["ci_high"]), _f(S[key + "_gross_R"].get("mean", float("nan"))),
            _f(100 * S[key + "_pct"].get("mean", float("nan")), "%+.2f"), S[key + "_funding_not_in_data"],
            S[key + "_ended"], S[key + "_stop_exits"]))
    L.append("")
    L.append(bars_text)
    return "\n".join(L) + "\n"


def bars_text(S):
    b = S["bars"]
    names = {"1_power": "VAL n>=30 trades and >=20 entry weeks", "2_val_ci": "VAL mean net R > 0 and block-bootstrap CI low > 0",
             "3_dev_sign": "DEV mean net R > 0", "4_placebo": "real mean above placebo 97.5th (same-window)",
             "5_ex_best": "ex-best entry weeks mean > 0 (and ex-best-2 episodes if >= 8 episodes)",
             "6_baseline": "net daily return in position >= DD-basket baseline", "7_top_coin": "top-coin removal mean > 0",
             "8_loyo": "leave-one-year-out stays > 0"}
    L = ["Bars passed: %s." % (", ".join(k for k in b if b[k]) or "none"),
         "Bars failed: %s." % (", ".join(k for k in b if not b[k]) or "none"), "",
         "| Bar | Pass | Statement |", "|---|---|---|"]
    for k in b:
        L.append("| %s | %s | %s |" % (k, "yes" if b[k] else "NO", names[k]))
    L.append("")
    pw, pg = S["placebo_window"], S["placebo_global"]
    L.append("Placebo same-window: real %s, draw mean %s, 97.5th %s, excess %s, p %s, n %d (skipped %d). Global: real %s, "
             "draw mean %s, 97.5th %s, excess %s, p %s." % (
                 _f(pw["real_mean"]), _f(pw["draw_mean"]), _f(pw["p975"]), _f(pw["excess"]), _f(pw["p"], "%.3f"), pw["n"],
                 pw["skipped"], _f(pg["real_mean"]), _f(pg["draw_mean"]), _f(pg["p975"]), _f(pg["excess"]),
                 _f(pg["p"], "%.3f")))
    L.append("")
    L.append("Baseline (DD basket, same Mondays, 28d, no stop): %s per day vs real %s per day (VAL); DEV baseline %s vs real %s." % (
        _f(100 * S["baseline"]["daily"], "%+.3f%%"), _f(100 * S["real_daily"], "%+.3f%%"),
        _f(100 * S["baseline_dev"]["daily"], "%+.3f%%"), _f(100 * S["real_daily_dev"], "%+.3f%%")))
    L.append("")
    L.append("Kill criteria: %s. Top-3 coin removal (sequential): %s. Ex-best weeks (k=%d): mean %s." % (
        S["kill"], [(x["removed"][-1], _f(x["mean"])) for x in S["top_coin_removal"]], S["ex_best_weeks"]["k"],
        _f(S["ex_best_weeks"]["mean"])))
    L.append("")
    e = S["val_episodes"]
    L.append("Episodes VAL: %d (reading %s); mean %s R, CI %s to %s, ex-best-2 %s. DEV episodes %d." % (
        e["episodes"], "valid" if e["episodes"] >= 8 else "UNDERPOWERED (< 8, no kill)", _f(e["mean"]), _f(e["ci_low"]),
        _f(e["ci_high"]), _f(e["ex_best2"]), S["dev_episodes"]["episodes"]))
    L.append("")
    L.append("Leave-one-year-out VAL: %s." % {y: _f(x["mean"]) for y, x in S["loyo"].items()})
    L.append("Holm: per-study p %s (one cell), family (9 cells) p %s. DEV week-level sd (measured now) %s R." % (
        _f(S["holm_study_p"], "%.4f"), _f(S["holm_family_p"], "%.4f"), _f(S["dev_week_sd_R"])))
    L.append("")
    for title, key in (("BTC cycle state VAL", "strata_val"), ("BTC cycle state DEV", "strata_dev"),
                       ("by year VAL", "by_year_val"), ("by year DEV", "by_year_dev")):
        L.append("### " + title)
        L.append("")
        L.append("| key | n | weeks | mean net R | median | win | worst | best |")
        L.append("|---|---|---|---|---|---|---|---|")
        for k, x in S[key].items():
            if x["n"]:
                L.append("| %s | %d | %d | %+.3f | %+.3f | %.2f | %+.2f | %+.2f |" % (
                    k, x["n"], x["weeks"], x["mean"], x["median"], x["win"], x["worst"], x["best"]))
        L.append("")
    L.append("BEAR-only VAL: n %d, mean %s, CI %s to %s. BASE-only VAL: n %d, mean %s, CI %s to %s." % (
        S["val_bear_boot"]["n"], _f(S["val_bear_boot"]["mean"]), _f(S["val_bear_boot"]["ci_low"]),
        _f(S["val_bear_boot"]["ci_high"]), S["val_base_boot"]["n"], _f(S["val_base_boot"]["mean"]),
        _f(S["val_base_boot"]["ci_low"]), _f(S["val_base_boot"]["ci_high"])))
    L.append("Survivorship: ex-ENDED VAL n %s mean %s; ex-LUNA/FTT VAL n %s mean %s (DEV: ex-ENDED %s, ex-LUNA/FTT %s). "
             "Direction: longs are biased UP (hindsight list, collapsed coins exit at a last close that may not be tradable)." % (
                 S["val_ex_ended"].get("n"), _f(S["val_ex_ended"].get("mean", float("nan"))),
                 S["val_ex_luna_ftt"].get("n"), _f(S["val_ex_luna_ftt"].get("mean", float("nan"))),
                 _f(S["dev_ex_ended"].get("mean", float("nan"))), _f(S["dev_ex_luna_ftt"].get("mean", float("nan")))))
    L.append("Thin dates (< 30 alive coins) excluded: %d trades." % S["n_thin_excluded"])
    L.append("")
    L.append("BTC descriptive row (a), not a pass cell: %s" % json.dumps(S.get("btc_row")))
    return "\n".join(L)


def main(here=None):
    print(core.set_below_normal())
    lk = core.acquire_slot("t7_stats")
    try:
        here = pathlib.Path(here or pathlib.Path(__file__).resolve().parent)
        trades = read_trades_csv(here / "trades.csv")
        segmap, fundmap, allsegs = {}, {}, []
        for coin, sp, fp in core.universe():
            for s in core.load_segments(sp, coin):
                segmap[(coin, s.seg_id)] = s
                allsegs.append(s)
            fundmap[coin] = core.load_funding(fp)
        alive = core.alive_counts(allsegs)
        state = core.load_state_table("F:/MTS/data_cache/mts_brains/phase_daily.csv")
        thin_ms = {ms for ms, c in alive.items() if c < core.MIN_ALIVE_COINS}
        btc = max((s for (c, _), s in segmap.items() if c == "BTC"), key=lambda s: s.n)
        btc_rows = btc_basket_row(btc, state, segmap, fundmap, thin_ms)
        S = run_stats(trades, segmap, fundmap, alive, btc_rows)
        (here / "summary_full.json").write_text(json.dumps(S, indent=1, default=str), encoding="utf-8")
        bt = bars_text(S)
        (here / "RESULT.md").write_text(render_result(S, bt), encoding="utf-8")
        small = {k: S[k] for k in ("n_total", "n_thin_excluded", "n_dev", "n_val", "val_weeks", "dev_weeks", "val_R",
                                   "dev_R", "val_gross_R", "val_fee_R", "val_pct", "val_boot", "dev_boot", "bars", "kill",
                                   "flags", "verdict", "placebo_window", "placebo_global", "baseline", "real_daily",
                                   "val_episodes", "ex_best_weeks", "top_coin_removal", "loyo", "holm_study_p",
                                   "holm_family_p", "dev_week_sd_R", "sign_flip", "fragile_top3")}
        (here / "results.json").write_text(json.dumps(small, indent=1, default=str), encoding="utf-8")
        print("verdict", S["verdict"], S["flags"])
    finally:
        core.release_slot(lk)


if __name__ == "__main__":
    main()
