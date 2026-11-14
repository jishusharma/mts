"""Step C: every statistic and bar of PRE_REG.md, from trades.csv. NOT to be run before steps A and B are clean.
Writes RESULT.md and RESULT_raw.json. Seed 1114 everywhere."""
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
import trades as T  # noqa: E402

SEED = 1114
BOOT = 2000
PLACEBO_DRAWS = 1000
CHUNK = 100
MIN_EP = 30
MIN_VAL_EP = 10
MIN_FRESH_EP = 10
ALPHA = 0.025  # one-sided, equals the 95% two-sided CI used in bar 2 (OURS, stated in RESULT)
CELLS = {"BULL+BASE": ("BULL", "BASE"), "BEAR": ("BEAR",)}


# ------------------------------------------------------------------ helpers
def episode_table(tr):
    g = tr.sort_values(["signal_ms", "coin"]).groupby("episode", sort=True)
    ep = pd.DataFrame({
        "n_trades": g.size(),
        "R12": g["R_net12"].mean(),
        "R6": g["R_net6"].mean(),
        "Rg": g["R_gross"].mean(),
        "cycle": g["episode_cycle"].first(),
        "split": g["split"].first(),
        "first_ms": g["signal_ms"].min(),
    })
    ep["year"] = pd.to_datetime(ep["first_ms"], unit="ms", utc=True).dt.year
    return ep


def boot(x, seed=SEED, B=BOOT):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(axis=1)
    return m


def mean_ci(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return {"n": 0, "mean": None, "lo": None, "hi": None, "p_le0": None}
    m = boot(x)
    return {"n": int(len(x)), "mean": float(x.mean()), "lo": float(np.percentile(m, 2.5)),
            "hi": float(np.percentile(m, 97.5)), "p_le0": float((np.sum(m <= 0) + 1) / (len(m) + 1))}


def holm(pvals):
    """Holm step-down adjusted p-values (family m = len(pvals)); returns dict name -> adjusted p."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def cycle_per_bar(hours_ms, pdays, pcyc):
    d = hours_ms // lib.DAY_MS * lib.DAY_MS
    pos = np.searchsorted(pdays, d)
    pc = np.minimum(pos, len(pdays) - 1)
    hit = (pos < len(pdays)) & (pdays[pc] == d)
    return np.where(hit, pcyc[pc], "NA")


def fmt(x, nd=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


# ------------------------------------------------------------------ placebo
def placebo(cell_tr, grids, pools, rng):
    """cell_tr: trades of the cell (DataFrame, with 'ep_idx' 0..n_ep-1). Returns draw means (episode level)."""
    n_tr = len(cell_tr)
    n_ep = int(cell_tr["ep_idx"].max()) + 1
    ind = np.zeros((n_tr, n_ep))
    ind[np.arange(n_tr), cell_tr["ep_idx"].to_numpy()] = 1.0
    ind /= ind.sum(axis=0, keepdims=True)
    sf = (cell_tr["D"] / cell_tr["entry"]).to_numpy()
    fee_term = lib.FEE_RT_12 / sf
    coins = cell_tr["coin"].to_numpy()
    cyc = cell_tr["cycle"].to_numpy()
    spl = cell_tr["split"].to_numpy()
    groups = {}
    for i in range(n_tr):
        groups.setdefault((coins[i], cyc[i], spl[i]), []).append(i)
    empty = sum(len(v) for k, v in groups.items() if len(pools.get(k, [])) == 0)
    if empty > 0:
        raise RuntimeError(f"placebo: {empty} trades have an empty candidate pool")
    means = []
    for _ in range(PLACEBO_DRAWS // CHUNK):
        Rn = np.full((CHUNK, n_tr), np.nan)
        for key, members in groups.items():
            pool = pools.get(key)
            if pool is None or len(pool) == 0:
                continue
            members = np.array(members)
            pick = pool[(rng.random((CHUNK, len(members))) * len(pool)).astype(int)]
            g = grids[key[0]]
            sf_rep = np.broadcast_to(sf[members], pick.shape).ravel()
            R, _, ok = lib.sim_many(g["o"], g["l"], pick.ravel(), sf_rep)
            R = np.where(ok, R, np.nan).reshape(pick.shape)
            Rn[:, members] = R - fee_term[members][None, :]
        # an unusable draw (cannot happen: pools are pre-validated) would leave NaN; fail loudly
        if np.isnan(Rn).any():
            raise RuntimeError("placebo produced NaN")
        means.append((Rn @ ind).mean(axis=1))
    return np.concatenate(means), int(empty)


def build_pools(all_tr, grids, pdays, pcyc):
    """Candidate placebo entry bars per (coin, cycle, split): valid 25 bars ahead, not inside a real position."""
    pools = {}
    for coin, g in grids.items():
        n = g["n"]
        hours = g["t0"] + np.arange(n, dtype=np.int64) * lib.HOUR_MS
        bad = np.isnan(g["o"]) | np.isnan(g["l"])
        cs = np.concatenate(([0], np.cumsum(bad)))
        idx = np.arange(n)
        okfwd = np.zeros(n, bool)
        m = idx + lib.HOLD_BARS < n
        okfwd[m] = (cs[idx[m] + lib.HOLD_BARS + 1] - cs[idx[m]]) == 0
        occ = np.zeros(n, bool)
        for _, r in all_tr[all_tr["coin"] == coin].iterrows():
            occ[int(r["entry_idx"]):int(r["exit_idx"]) + 1] = True
        cyc = cycle_per_bar(hours, pdays, pcyc)
        spl = np.where(hours < T.VAL_START_MS, "DEV", "VAL")
        base = okfwd & ~occ
        for c in ("BULL", "BASE", "BEAR"):
            for s in ("DEV", "VAL"):
                pools[(coin, c, s)] = np.flatnonzero(base & (cyc == c) & (spl == s))
    return pools


# ------------------------------------------------------------------ cell evaluation
def evaluate_cell(name, cyc_set, tr, ep, grids, pools):
    ep_c = ep[ep["cycle"].isin(cyc_set)]
    tr_c = tr[tr["episode"].isin(ep_c.index)].copy()
    ids = {e: i for i, e in enumerate(ep_c.index)}
    tr_c["ep_idx"] = tr_c["episode"].map(ids)
    res = {"cell": name, "n_episodes": int(len(ep_c)), "n_trades": int(len(tr_c))}
    x = ep_c["R12"].to_numpy()
    res["pooled"] = mean_ci(x) if len(x) else mean_ci([])
    res["ex_best5_mean"] = float(np.sort(x)[:-5].mean()) if len(x) > 5 else None
    res["gross_mean"] = float(ep_c["Rg"].mean()) if len(x) else None
    res["net6_mean"] = float(ep_c["R6"].mean()) if len(x) else None
    res["sd_trade_R12"] = float(tr_c["R_net12"].std(ddof=1)) if len(tr_c) > 1 else None
    res["sd_episode_R12"] = float(ep_c["R12"].std(ddof=1)) if len(ep_c) > 1 else None
    res["mean_trade_pct_net12"] = float((tr_c["R_net12"] * tr_c["D"] / tr_c["entry"]).mean()) if len(tr_c) else None
    res["mean_hold_hours"] = float((tr_c["exit_idx"] - tr_c["entry_idx"]).mean()) if len(tr_c) else None
    res["split"] = {s: mean_ci(ep_c.loc[ep_c["split"] == s, "R12"]) for s in ("DEV", "VAL")}
    # fresh-8 alone: episodes rebuilt from the fresh trades only
    fr = tr_c[tr_c["group"] == "fresh"]
    if len(fr):
        fid = lib.assign_episodes(fr["signal_ms"].to_numpy())
        fm = fr.assign(fe=fid).groupby("fe")["R_net12"].mean()
        res["fresh"] = {"n_episodes": int(len(fm)), "mean": float(fm.mean())}
    else:
        res["fresh"] = {"n_episodes": 0, "mean": None}
    # by symbol, top-coin removal
    sym = {}
    for coin, g in tr_c.groupby("coin"):
        sym[coin] = {"n": int(len(g)), "mean_R12": float(g["R_net12"].mean()), "sum_R12": float(g["R_net12"].sum())}
    res["by_symbol"] = sym
    if sym:
        top = max(sym, key=lambda k: sym[k]["sum_R12"])
        rest = tr_c[tr_c["coin"] != top]
        if len(rest):
            rid = lib.assign_episodes(rest["signal_ms"].to_numpy())
            rm = rest.assign(re=rid).groupby("re")["R_net12"].mean().mean()
        else:
            rm = None
        res["top_coin_removal"] = {"coin": top, "mean_after": None if rm is None else float(rm),
                                   "FRAGILE": bool(rm is not None and rm <= 0)}
    else:
        res["top_coin_removal"] = None
    res["by_year"] = {int(y): {"n_ep": int(len(g)), "mean_R12": float(g["R12"].mean())} for y, g in ep_c.groupby("year")}
    res["by_phase_label"] = {str(k): {"n_trades": int(len(g)), "mean_R12": float(g["R_net12"].mean())}
                             for k, g in tr_c.groupby("phase_label")}
    res["by_cycle_state"] = {str(k): {"n_ep": int(len(g)), "mean_R12": float(g["R12"].mean())}
                             for k, g in ep_c.groupby("cycle")}
    # placebo
    if len(tr_c) and len(ep_c):
        rng = np.random.default_rng(SEED)
        pm, empty = placebo(tr_c, grids, pools, rng)
        real = float(x.mean())
        res["placebo"] = {"draws": int(len(pm)), "mean": float(pm.mean()), "p97_5": float(np.percentile(pm, 97.5)),
                          "p2_5": float(np.percentile(pm, 2.5)), "real": real, "excess": real - float(pm.mean()),
                          "trades_without_pool": empty}
    else:
        res["placebo"] = None
    return res


def bars_for(res, holm_adj):
    p = res["pooled"]
    out = {}
    out["1 >=30 episodes"] = (res["n_episodes"] >= MIN_EP, f"n={res['n_episodes']}")
    ok2 = p["n"] > 0 and p["mean"] > 0 and p["lo"] > 0
    out["2 mean>0 and CI low>0"] = (ok2, f"mean={fmt(p['mean'])} CI=[{fmt(p['lo'])},{fmt(p['hi'])}]")
    out["3 ex-best-5 mean>0"] = (res["ex_best5_mean"] is not None and res["ex_best5_mean"] > 0, fmt(res["ex_best5_mean"]))
    pl = res["placebo"]
    ok4 = bool(pl) and pl["real"] >= pl["p97_5"] and pl["excess"] > 0
    out["4 beats placebo p97.5, excess>0"] = (ok4, "n/a" if not pl else
                                              f"real={fmt(pl['real'])} placebo mean={fmt(pl['mean'])} p97.5={fmt(pl['p97_5'])} excess={fmt(pl['excess'])}")
    d, v = res["split"]["DEV"], res["split"]["VAL"]
    under = v["n"] < MIN_VAL_EP
    ok5 = (not under) and d["n"] > 0 and d["mean"] > 0 and v["mean"] > 0
    out["5 DEV>0 and VAL>0"] = (ok5, f"DEV n={d['n']} mean={fmt(d['mean'])}; VAL n={v['n']} mean={fmt(v['mean'])}" + (" UNDERPOWERED" if under else ""))
    f = res["fresh"]
    ok6 = f["n_episodes"] < MIN_FRESH_EP or f["mean"] > 0
    out["6 fresh-8 mean>0 (if >=10 ep)"] = (ok6, f"n_ep={f['n_episodes']} mean={fmt(f['mean'])}" + (" (reported only)" if f["n_episodes"] < MIN_FRESH_EP else ""))
    passed = all(v_[0] for v_ in out.values())
    flagged = passed and holm_adj > ALPHA
    return out, passed, flagged


# ------------------------------------------------------------------ main
def main():
    tr = pd.read_csv(os.path.join(HERE, "trades.csv"))
    ep = episode_table(tr)
    pdays, pcyc, plab = T.load_phase()
    coins = sorted(tr["coin"].unique())
    grids = {}
    for c in coins:
        grp = "core" if c in T.CORE else "fresh"
        grids[c] = T.load_hourly(c, grp)
    pools = build_pools(tr, grids, pdays, pcyc)

    results = {name: evaluate_cell(name, cs, tr, ep, grids, pools) for name, cs in CELLS.items()}
    pv = {k: (r["pooled"]["p_le0"] if r["pooled"]["p_le0"] is not None else 1.0) for k, r in results.items()}
    hadj = holm(pv)
    verdicts = {}
    for k, r in results.items():
        bars, passed, flagged = bars_for(r, hadj[k])
        verdicts[k] = {"bars": {b: {"pass": bool(v[0]), "detail": v[1]} for b, v in bars.items()},
                       "PASS": bool(passed), "MULTIPLICITY_FLAGGED": bool(flagged), "holm_adj_p": hadj[k],
                       "raw_p": pv[k]}

    # descriptive: all three states separately
    states = {}
    for s in ("BULL", "BASE", "BEAR"):
        e = ep[ep["cycle"] == s]
        states[s] = mean_ci(e["R12"].to_numpy()) if len(e) else mean_ci([])

    # regime mix
    mix = {}
    for s in ("DEV", "VAL"):
        t = tr[tr["split"] == s]
        mix[s] = {"signals": {c: int((t["cycle"] == c).sum()) for c in ("BULL", "BASE", "BEAR")},
                  "episodes": {c: int(((ep["split"] == s) & (ep["cycle"] == c)).sum()) for c in ("BULL", "BASE", "BEAR")}}
    d0 = int(tr["trap_ms"].min()) // lib.DAY_MS * lib.DAY_MS
    d1 = int(tr["trap_ms"].max()) // lib.DAY_MS * lib.DAY_MS
    sel = (pdays >= d0) & (pdays <= d1)
    cal = {c: float((pcyc[sel] == c).mean()) for c in ("BULL", "BASE", "BEAR")}
    sig_share = {c: float((tr["cycle"] == c).mean()) for c in ("BULL", "BASE", "BEAR")}

    # buy-and-hold basket (equal weight over coins), time in market
    year_ret, state_ret, state_hours = {}, {}, {}
    sums = {s: [] for s in ("BULL", "BASE", "BEAR")}
    cnts = {s: [] for s in ("BULL", "BASE", "BEAR")}
    yret = {}
    mkt_hours = {s: 0 for s in ("BULL", "BASE", "BEAR")}
    for c, g in grids.items():
        n = g["n"]
        hours = g["t0"] + np.arange(n, dtype=np.int64) * lib.HOUR_MS
        cl = g["c"]
        lr = np.full(n, np.nan)
        lr[1:] = np.log(cl[1:] / cl[:-1])
        cyc_b = cycle_per_bar(hours, pdays, pcyc)
        for s in sums:
            m = (cyc_b == s) & ~np.isnan(lr)
            sums[s].append(lr[m].sum())
            cnts[s].append(int(m.sum()))
            mkt_hours[s] += int(((cyc_b == s) & ~np.isnan(cl)).sum())
        yrs = pd.to_datetime(hours, unit="ms", utc=True).year
        for y in np.unique(yrs):
            v = cl[(yrs == y) & ~np.isnan(cl)]
            if len(v) > 24 * 30:
                yret.setdefault(int(y), []).append(v[-1] / v[0] - 1)
    year_ret = {y: {"basket_ret": float(np.mean(v)), "n_coins": len(v)} for y, v in sorted(yret.items())}
    for s in sums:
        tot_h = sum(cnts[s])
        state_ret[s] = {"basket_mean_24h_logret": float(sum(sums[s]) / tot_h * 24) if tot_h else None,
                        "basket_mean_coin_cum_ret": float(np.mean([np.expm1(x) for x in sums[s]])),
                        "coin_hours": tot_h}
    tim = {}
    for s in ("BULL", "BASE", "BEAR"):
        t = tr[tr["cycle"] == s]
        held = float((t["exit_idx"] - t["entry_idx"]).sum())
        tim[s] = {"hours_in_position": held, "coin_hours_in_state": mkt_hours[s],
                  "share": held / mkt_hours[s] if mkt_hours[s] else None}

    # registered prediction
    bb = results["BULL+BASE"]["pooled"]["mean"]
    be = results["BEAR"]["pooled"]["mean"]
    pred = (bb is not None and be is not None and bb > 0 and be <= 0)

    raw = {"seed": SEED, "results": results, "verdicts": verdicts, "states": states, "regime_mix": mix,
           "calendar_share": cal, "signal_share": sig_share, "year_basket": year_ret, "state_basket": state_ret,
           "time_in_market": tim, "prediction_confirmed": bool(pred), "n_trades": int(len(tr)),
           "n_episodes": int(len(ep))}
    with open(os.path.join(HERE, "RESULT_raw.json"), "w") as f:
        json.dump(raw, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

    # ---------------- RESULT.md
    L = ["# RESULT: T2 washout Supertrap LONG by cycle state", "",
         f"Seed {SEED}; 12 bp fee-net R primary; episode = unit of verdict; {len(tr)} trades, {len(ep)} episodes.", ""]
    L.append("Regime mix: calendar days %s | signals %s | episodes DEV %s, VAL %s" % (
        ", ".join(f"{c} {cal[c]*100:.0f}%" for c in cal),
        ", ".join(f"{c} {sig_share[c]*100:.0f}%" for c in sig_share),
        mix["DEV"]["episodes"], mix["VAL"]["episodes"]))
    L.append("")
    L.append("## Verdict (family m = 2, Holm)")
    for k, v in verdicts.items():
        label = "PASS" if v["PASS"] else "FAIL"
        if v["MULTIPLICITY_FLAGGED"]:
            label += " (MULTIPLICITY-FLAGGED)"
        L.append(f"### {k}: {label}  (raw p {v['raw_p']:.4f}, Holm-adj p {v['holm_adj_p']:.4f}, alpha {ALPHA} one-sided)")
        L.append("| Bar | Result | Detail |")
        L.append("|---|---|---|")
        for b, d in v["bars"].items():
            L.append(f"| {b} | {'PASS' if d['pass'] else 'FAIL'} | {d['detail']} |")
        L.append("")
    L.append("Registered prediction (BULL+BASE mean > 0 and BEAR mean <= 0): %s" % ("CONFIRMED" if pred else "REFUTED"))
    if verdicts["BEAR"]["PASS"]:
        L.append("BEAR passed bars 1-6: reported as the tradable result, labelled by itself (m = 2).")
    if verdicts["BULL+BASE"]["PASS"]:
        L.append("A PASS still needs the blind review. A FAIL is UNTESTED/underpowered, not proof of no edge.")
    L.append("")
    L.append("## Cells in detail")
    L.append("| Cell | Ep | Trades | Mean R12 | CI | Gross | 6bp | sd trade | sd ep | Mean pct net/trade | Hold h |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, r in results.items():
        p = r["pooled"]
        L.append(f"| {k} | {r['n_episodes']} | {r['n_trades']} | {fmt(p['mean'])} | [{fmt(p['lo'])},{fmt(p['hi'])}] | "
                 f"{fmt(r['gross_mean'])} | {fmt(r['net6_mean'])} | {fmt(r['sd_trade_R12'])} | {fmt(r['sd_episode_R12'])} | "
                 f"{fmt(r['mean_trade_pct_net12'], 4)} | {fmt(r['mean_hold_hours'], 1)} |")
    L.append("")
    L.append("## Each state separately (descriptive)")
    L.append("| State | Ep | Mean R12 | CI |")
    L.append("|---|---|---|---|")
    for s, v in states.items():
        L.append(f"| {s} | {v['n']} | {fmt(v['mean'])} | [{fmt(v['lo'])},{fmt(v['hi'])}] |")
    for k, r in results.items():
        L.append("")
        L.append(f"## {k}: cuts")
        tc = r["top_coin_removal"]
        if tc:
            L.append(f"Top-coin removal ({tc['coin']}, largest summed R): mean after {fmt(tc['mean_after'])}; {'FRAGILE' if tc['FRAGILE'] else 'not fragile'}")
        L.append("By year (episodes): " + "; ".join(f"{y}: n={d['n_ep']} mean {fmt(d['mean_R12'])}" for y, d in r["by_year"].items()))
        L.append("By phase label (trades, descriptive): " + "; ".join(f"{p}: n={d['n_trades']} mean {fmt(d['mean_R12'])}" for p, d in r["by_phase_label"].items()))
        L.append("By symbol (trades): " + "; ".join(f"{c}: n={d['n']} mean {fmt(d['mean_R12'])}" for c, d in sorted(r["by_symbol"].items())))
    L.append("")
    L.append("## Buy-and-hold equal-weight basket (reported, not a gate)")
    L.append("| Year | Basket return (first to last close in year) | Coins |")
    L.append("|---|---|---|")
    for y, d in year_ret.items():
        L.append(f"| {y} | {d['basket_ret']*100:.1f}% | {d['n_coins']} |")
    L.append("")
    L.append("| State | Basket mean 24h log return | Mean per-coin cumulative return in state days | Coin-hours | Strategy share of coin-hours in position |")
    L.append("|---|---|---|---|---|")
    for s in ("BULL", "BASE", "BEAR"):
        b = state_ret[s]
        L.append(f"| {s} | {fmt(b['basket_mean_24h_logret'], 5)} | {fmt(b['basket_mean_coin_cum_ret'], 3)} | {b['coin_hours']} | {fmt(tim[s]['share'], 4)} |")
    L.append("")
    L.append("Notes: bar 4 placebo episodes reuse the real trade's episode structure; Holm alpha 0.025 one-sided matches the 95% two-sided CI (OURS). See NOTES.md for reading choices.")
    with open(os.path.join(HERE, "RESULT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
