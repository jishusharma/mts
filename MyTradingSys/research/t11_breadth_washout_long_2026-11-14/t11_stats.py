"""T11 statistics. Pure functions over leg dicts; the only unit of inference is the EPISODE (events within 14 days merge).
Leg dict keys used: coin, sig_day (epoch day of the event signal bar), net_R, gross_R, net, gross, fee_R, days_held,
B (event breadth), state (smoothed BTC cycle at the event), above (1.0/0.0 BTC close > SMA200d at the event), iso_week,
ended, net_pd (net per day held), basket_pd (equal-weight basket net per day, same event), pct (stop %).
run_cell() returns (summary dict, bars, verdict). No file access here.
"""
import sys
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t11_core as core  # noqa: E402

SEED = 1114
NBOOT = 2000
NDRAW = 1000
MIN_VAL_EPISODES = 8


def _pct(a, q):
    s = np.sort(np.asarray(a, float))
    return float(np.interp(q / 100.0 * (len(s) - 1), np.arange(len(s)), s))


def _mean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def day_ms(day):
    return int(day) * core.DAY


def split_of_day(sig_day):
    """Signal bar = daily bar of epoch day `sig_day` (open time sig_day*DAY): DEV when the bar date is <= 2023-12-31."""
    return core.split_of_ms(sig_day * core.DAY)


def year_of_day(sig_day):
    return dt.datetime.fromtimestamp(sig_day * 86400, dt.timezone.utc).year


def assign_episodes(legs):
    """Cell-local episodes: unique event days of these legs are merged (14 d chain); a leg carries ep, ep_first_day and
    split of its episode (split = split of the first event's signal bar). Mutates and returns legs."""
    days = sorted({l["sig_day"] for l in legs})
    ids = core.merge_episodes(days)
    first, ep_of = {}, {}
    for d, e in zip(days, ids):
        ep_of[d] = e
        first.setdefault(e, d)
    for l in legs:
        e = ep_of[l["sig_day"]]
        l["ep"], l["ep_first_day"] = e, first[e]
        l["split"] = split_of_day(first[e])
    return legs


def sub(legs, **kw):
    return [l for l in legs if all(l.get(k) == v for k, v in kw.items())]


def ep_means(legs, val="net_R"):
    """{ep: mean of val over the episode's legs} (legs averaged within an episode first)."""
    g = {}
    for l in legs:
        v = l.get(val)
        if v is not None and v == v:
            g.setdefault(l["ep"], []).append(v)
    return {e: float(np.mean(v)) for e, v in g.items()}


def event_means(legs, val="net_R"):
    g = {}
    for l in legs:
        v = l.get(val)
        if v is not None and v == v:
            g.setdefault(l["sig_day"], []).append(v)
    return {d: float(np.mean(v)) for d, v in g.items()}


def mean_eps(legs, val="net_R"):
    return _mean(list(ep_means(legs, val).values()))


def boot(vals, nboot=NBOOT, seed=SEED):
    """Plain bootstrap of the mean of independent units (episodes or events)."""
    v = np.asarray([x for x in vals if x == x], float)
    if len(v) == 0:
        return dict(n=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    rng = np.random.default_rng(seed)
    m = v[rng.integers(0, len(v), (nboot, len(v)))].mean(1)
    return dict(n=int(len(v)), mean=float(v.mean()), ci_low=_pct(m, 2.5), ci_high=_pct(m, 97.5),
                p_le0=float((np.sum(m <= 0) + 1) / (nboot + 1)))


def week_cluster_boot(legs, val="net_R", nboot=NBOOT, seed=SEED):
    """Resample ISO entry weeks (block of one week); resampled mean = sum in drawn weeks / legs in drawn weeks."""
    rows = [l for l in legs if l.get(val) is not None and l[val] == l[val]]
    if not rows:
        return dict(n=0, weeks=0, mean=float("nan"), ci_low=float("nan"), ci_high=float("nan"), p_le0=float("nan"))
    cl = {}
    for l in rows:
        cl.setdefault(l["iso_week"], []).append(l[val])
    ks = sorted(cl)
    s = np.array([sum(cl[k]) for k in ks])
    n = np.array([len(cl[k]) for k in ks], float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ks), (nboot, len(ks)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return dict(n=len(rows), weeks=len(ks), mean=float(s.sum() / n.sum()), ci_low=_pct(m, 2.5),
                ci_high=_pct(m, 97.5), p_le0=float((np.sum(m <= 0) + 1) / (nboot + 1)))


# ------------------------------------------------------------------ robustness rows
def ex_best_eps(legs, k=2, val="net_R"):
    em = ep_means(legs, val)
    drop = set(sorted(em, key=lambda e: -em[e])[:k])
    rest = [v for e, v in em.items() if e not in drop]
    return dict(dropped=sorted(drop), n=len(rest), mean=_mean(rest))


def leave_one_event_out(legs, val="net_R"):
    """Drop each event (all its legs), recompute the episode-mean of the rest. Returns min, max, count of sign flips."""
    days = sorted({l["sig_day"] for l in legs})
    base = mean_eps(legs, val)
    res = []
    for d in days:
        rest = [l for l in legs if l["sig_day"] != d]
        res.append(mean_eps(rest, val))
    res = [r for r in res if r == r]
    if not res:
        return dict(n=0, min=float("nan"), max=float("nan"), flips=0, base=base)
    flips = sum(1 for r in res if (r > 0) != (base > 0))
    return dict(n=len(res), min=float(min(res)), max=float(max(res)), flips=int(flips), base=base)


def top_coin_removal(legs, k=3, val="net_R"):
    legs = [l for l in legs if l[val] == l[val]]
    removed, out = [], []
    for _ in range(k):
        sums = {}
        for l in legs:
            if l["coin"] not in removed:
                sums[l["coin"]] = sums.get(l["coin"], 0.0) + l[val]
        if not sums:
            break
        removed.append(max(sums, key=lambda c: sums[c]))
        rest = [l for l in legs if l["coin"] not in removed]
        out.append(dict(removed=list(removed), n_legs=len(rest), mean=mean_eps(rest, val)))
    return out


def leave_one_year_out(legs, val="net_R"):
    ys = sorted({year_of_day(l["ep_first_day"]) for l in legs})
    out = {}
    for y in ys:
        rest = [l for l in legs if year_of_day(l["ep_first_day"]) != y]
        out[str(y)] = dict(n_eps=len(ep_means(rest, val)), mean=mean_eps(rest, val))
    return out


def group_rows(legs, keyfn, val="net_R"):
    g = {}
    for l in legs:
        g.setdefault(keyfn(l), []).append(l)
    out = {}
    for k in sorted(g, key=str):
        rows = g[k]
        em = event_means(rows, val)
        out[str(k)] = dict(legs=len(rows), events=len(em), episodes=len({l["ep"] for l in rows}),
                           mean_event=_mean(list(em.values())), mean_leg=_mean([l[val] for l in rows]))
    return out


def dose_response(legs, val="net_R"):
    """Event-level mean net R by event breadth bin; monotone = weakly rising with breadth over populated bins."""
    em = event_means(legs, val)
    bd = {}
    for l in legs:
        bd[l["sig_day"]] = l["B"]
    bins = {"15-30": [], "30-50": [], ">=50": []}
    for d, v in em.items():
        b = bd[d]
        bins["15-30" if b < 0.30 else ("30-50" if b < 0.50 else ">=50")].append(v)
    rows = {k: dict(events=len(v), mean=_mean(v)) for k, v in bins.items()}
    pop = [rows[k]["mean"] for k in ("15-30", "30-50", ">=50") if rows[k]["events"] > 0]
    testable = len(pop) >= 2
    mono = bool(testable and all(pop[i] <= pop[i + 1] for i in range(len(pop) - 1)))
    return dict(bins=rows, testable=testable, monotone=mono)


def strata_prediction(legs, val="net_R"):
    """Pre-registered: mean > 0 when BTC close > SMA200d at the event, mean <= 0 when below (event level)."""
    em = event_means(legs, val)
    ab = {}
    for l in legs:
        ab[l["sig_day"]] = l["above"]
    up = [v for d, v in em.items() if ab[d] == 1.0]
    dn = [v for d, v in em.items() if ab[d] == 0.0]
    r = dict(above=dict(events=len(up), mean=_mean(up)), below=dict(events=len(dn), mean=_mean(dn)))
    r["testable"] = bool(up and dn)
    r["holds"] = bool(r["testable"] and r["above"]["mean"] > 0 and r["below"]["mean"] <= 0)
    r["flipped"] = bool(r["testable"] and r["above"]["mean"] <= 0 and r["below"]["mean"] > 0)
    return r


# ------------------------------------------------------------------ legs and pools (shared by run script and tests)
def _d(day):
    return dt.datetime.fromtimestamp(int(day) * 86400, dt.timezone.utc).strftime("%Y-%m-%d")


def make_legs(mkt, funds, state_fn, above_fn, events=None):
    """All legs of all eligible events (>= 30 alive coins) with a valid window. funds: {coin: Funding|None};
    state_fn(sig_day) -> smoothed BTC state; above_fn(sig_day) -> 1.0/0.0/nan. Also the basket per-day net of the event
    (all alive coins, same entry open, same 10-day hold, no stop, same fee and funding)."""
    out = []
    evs = core.find_events(mkt.breadth) if events is None else events
    for d in evs:
        if mkt.n_alive[d] < core.MIN_ALIVE:
            continue
        day = mkt.dmin + d
        legs = []
        for s in core.leg_signals(mkt, d):
            c = mkt.coins[s["ci"]]
            r = core.simulate_leg(c, s["d0"], s["pct"], funds.get(c.name))
            if r is not None:
                legs.append((s, r))
        if not legs:
            continue
        bk = []
        for i, c in enumerate(mkt.coins):
            if not mkt.alive[i, d]:
                continue
            d0 = mkt.dmin + d - c.day0 + 1
            if d0 >= c.n:
                continue
            P = core.path_arrays(c, [d0], funds.get(c.name))
            if not P["valid"][0]:
                continue
            nr = int(P["nreal"][0])
            bk.append((P["rel_close"][0, nr - 1] - core.FEE_RT - P["fund"][0, nr - 1]) / nr)
        bpd = float(np.mean(bk)) if bk else float("nan")
        for s, r in legs:
            out.append(dict(coin=r["coin"], sig_day=day, sig_date=_d(day), entry_date=_d(r["ent_day"]),
                            exit_date=_d(r["ent_day"] + r["days_held"] - 1), B=float(mkt.breadth[d]),
                            state=state_fn(day), above=above_fn(day), rsi=s["rsi"], pct=r["pct"],
                            entry_px=r["entry_px"], gross=r["gross"], fee=r["fee"], funding=r["funding"],
                            funding_rule=r["funding_rule"], net=r["net"], gross_R=r["gross_R"], net_R=r["net_R"],
                            fee_R=r["fee_R"], days_held=r["days_held"], exit_reason=r["exit_reason"],
                            ended=r["ended"], iso_week=core.iso_week_of(r["entry_ts"]), basket_pd=bpd,
                            net_pd=r["net"] / r["days_held"]))
    out.sort(key=lambda l: (l["sig_day"], l["coin"]))
    return out


def pool_entries(mkt, funds, state_fn):
    """Placebo pools. kind 'pri': coin's own RSI14 <= 35 and market breadth < 10% (and >= 30 alive coins); kind 'sec':
    every alive day. Valid windows only; state_fn(sig_day) -> BTC state ('NA' rows are dropped)."""
    ents = []
    for kind in ("pri", "sec"):
        for i, c in enumerate(mkt.coins):
            ts = np.arange(0, c.n - 1)
            dd = c.day0 + ts - mkt.dmin
            ok = mkt.alive[i, dd] & (mkt.n_alive[dd] >= core.MIN_ALIVE)
            if kind == "pri":
                ok &= (mkt.rsi[i, dd] <= core.ENTRY_RSI) & (mkt.breadth[dd] < core.PLACEBO_B)
            ts = ts[ok]
            if len(ts) == 0:
                continue
            sig_day = c.day0 + ts
            state = np.array([state_fn(int(d)) for d in sig_day])
            keep = state != "NA"
            ts, sig_day, state = ts[keep], sig_day[keep], state[keep]
            if len(ts) == 0:
                continue
            P = core.path_arrays(c, ts + 1, funds.get(c.name))
            ix = np.where(P["valid"])[0]
            ents.append(dict(coin=c.name, kind=kind, sig_day=sig_day[ix], state=state[ix], P=_take(P, ix),
                             split=np.array([split_of_day(int(d)) for d in sig_day[ix]])))
    return build_pools(ents)


# ------------------------------------------------------------------ placebo
def build_pools(entries):
    """entries: list of per-coin dicts {coin, kind, sig_day (arr), state (arr of str), P (path arrays, valid rows only)}.
    Returns {kind: {coin: entry}}."""
    out = {}
    for e in entries:
        out.setdefault(e["kind"], {})[e["coin"]] = e
    return out


def _take(P, ix):
    return {k: (v[ix] if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == len(P["valid"]) else v)
            for k, v in P.items()}


def placebo(legs, pools, kind="pri", variant="window", ndraw=NDRAW, seed=SEED):
    """Like-for-like placebo for the legs of ONE split. Each real leg is replaced by a random pool entry of the same
    coin, split, BTC state, with the real leg's stop distance in %, same exit rule (core.outcome_vec) and the same
    fees/funding. variant 'window' = +/- 56 days around the real signal day (fallback global with the same state, then
    same coin+split; counted); 'global' = whole split. One draw = mean over episodes of the episode means.
    Returns real episode-mean (over used legs), draw mean, 97.5th pct, excess, one-sided p."""
    rng = np.random.default_rng(seed)
    eps = sorted({l["ep"] for l in legs})
    ei = {e: i for i, e in enumerate(eps)}
    esum = np.zeros((len(eps), ndraw))
    ecnt = np.zeros(len(eps))
    real_sum = np.zeros(len(eps))
    skipped = fb_global = fb_state = 0
    P_by = pools.get(kind, {})
    for l in legs:
        ent = P_by.get(l["coin"])
        if ent is None or len(ent["sig_day"]) == 0:
            skipped += 1
            continue
        sd, st_ = ent["sig_day"], ent["state"]
        spl = np.array([split_of_day(int(d)) for d in sd]) if "split" not in ent else ent["split"]
        m_split = spl == l["split"]
        m_state = st_ == l["state"]
        cand = None
        if variant == "window":
            m = m_split & m_state & (np.abs(sd - l["sig_day"]) <= core.WINDOW_DAYS)
            if m.any():
                cand = np.where(m)[0]
            else:
                fb_global += 1
        if cand is None:
            m = m_split & m_state
            if m.any():
                cand = np.where(m)[0]
            else:
                m = m_split
                if m.any():
                    cand = np.where(m)[0]
                    fb_state += 1
        if cand is None:
            skipped += 1
            continue
        o = core.outcome_vec(_take(ent["P"], cand), l["pct"])
        draw = o["net_R"][rng.integers(0, len(cand), ndraw)]
        i = ei[l["ep"]]
        esum[i] += draw
        ecnt[i] += 1
        real_sum[i] += l["net_R"]
    used = ecnt > 0
    if not used.any():
        return dict(n_legs=0, skipped=skipped, real=float("nan"), draw_mean=float("nan"), p975=float("nan"),
                    excess=float("nan"), p=float("nan"), fb_global=fb_global, fb_state=fb_state)
    draws = (esum[used] / ecnt[used][:, None]).mean(0)
    real = float((real_sum[used] / ecnt[used]).mean())
    return dict(n_legs=int(ecnt.sum()), n_eps=int(used.sum()), skipped=skipped, real=real,
                draw_mean=float(draws.mean()), p975=_pct(draws, 97.5), excess=real - float(draws.mean()),
                p=float((np.sum(draws >= real) + 1) / (ndraw + 1)), fb_global=fb_global, fb_state=fb_state)


# ------------------------------------------------------------------ cell
def describe(legs, val):
    v = np.array([l[val] for l in legs if l[val] == l[val]], float)
    if not len(v):
        return dict(n=0)
    return dict(n=int(len(v)), mean=float(v.mean()), median=float(np.median(v)), win=float((v > 0).mean()),
                worst=float(v.min()), best=float(v.max()))


def split_block(legs, nboot, seed):
    em = ep_means(legs, "net_R")
    S = dict(legs=len(legs), events=len({l["sig_day"] for l in legs}), episodes=len(em),
             weeks=len({l["iso_week"] for l in legs}),
             net_R=mean_eps(legs, "net_R"), gross_R=mean_eps(legs, "gross_R"), fee_R=mean_eps(legs, "fee_R"),
             net_pct=mean_eps(legs, "net"), gross_pct=mean_eps(legs, "gross"),
             net_R_leg=describe(legs, "net_R"), gross_R_leg=describe(legs, "gross_R"),
             net_pd=mean_eps(legs, "net_pd"), basket_pd=mean_eps(legs, "basket_pd"),
             flat_exits=dict((r, sum(1 for l in legs if l["exit_reason"] == r)) for r in core.REASONS + ("ENDED-EXIT",)),
             funding_not_in_data=sum(1 for l in legs if l["funding_rule"] == "NOT_IN_DATA"))
    S["boot_episode"] = boot(list(em.values()), nboot, seed)
    S["boot_event"] = boot(list(event_means(legs, "net_R").values()), nboot, seed)
    S["boot_week"] = week_cluster_boot(legs, "net_R", nboot, seed)
    return S


def run_cell(legs, pools, nboot=NBOOT, ndraw=NDRAW, seed=SEED):
    """legs: all legs of one cell (DEV + VAL), already with episodes assigned by assign_episodes."""
    val, dev = sub(legs, split="VAL"), sub(legs, split="DEV")
    S = dict(VAL=split_block(val, nboot, seed), DEV=split_block(dev, nboot, seed))
    S["ex_best2_eps"] = ex_best_eps(val, 2)
    S["loeo"] = leave_one_event_out(val)
    S["top_coin"] = top_coin_removal(val, 3)
    S["ex_ended"] = dict(mean=mean_eps([l for l in val if not l["ended"]], "net_R"),
                         eps=len(ep_means([l for l in val if not l["ended"]])))
    nl = [l for l in val if l["coin"] not in core.HOLES]
    S["ex_luna_ftt"] = dict(mean=mean_eps(nl, "net_R"), eps=len(ep_means(nl)))
    S["ex_luna_ftt_dev"] = dict(mean=mean_eps([l for l in dev if l["coin"] not in core.HOLES], "net_R"))
    S["loyo"] = leave_one_year_out(val)
    S["dose_val"] = dose_response(val)
    S["dose_pooled"] = dose_response(legs)
    S["strata_val"] = strata_prediction(val)
    S["strata_dev"] = strata_prediction(dev)
    S["strata_pooled"] = strata_prediction(legs)
    S["by_state"] = {sp: group_rows(sub(legs, split=sp), lambda l: l["state"]) for sp in ("DEV", "VAL")}
    S["by_year"] = {sp: group_rows(sub(legs, split=sp), lambda l: year_of_day(l["sig_day"])) for sp in ("DEV", "VAL")}
    S["by_above"] = {sp: group_rows(sub(legs, split=sp), lambda l: {1.0: "above", 0.0: "below"}.get(l["above"], "NA"))
                     for sp in ("DEV", "VAL")}
    S["placebo"] = {}
    for sp, rows in (("VAL", val), ("DEV", dev)):
        for kind in ("pri", "sec"):
            for var in ("window", "global"):
                S["placebo"]["%s_%s_%s" % (sp, kind, var)] = (
                    placebo(rows, pools, kind, var, ndraw, seed) if rows else dict(n_legs=0))
    S["bars"], S["kill"] = bars_and_kill(S)
    S["verdict"] = verdict_of(S)
    return S


def bars_and_kill(S):
    V, D = S["VAL"], S["DEV"]
    n_ep = V["episodes"]
    ok1 = n_ep >= MIN_VAL_EPISODES
    pb = S["placebo"].get("VAL_pri_window", {})
    pbg = S["placebo"].get("VAL_pri_global", {})
    pb_ok = bool(pb.get("n_legs", 0) > 0 and pb["real"] > pb["p975"] and pb["excess"] > 0)
    pbg_ok = bool(pbg.get("n_legs", 0) > 0 and pbg["real"] > pbg["p975"] and pbg["excess"] > 0)
    tc = S["top_coin"]
    bars = {
        "1_power_ge8_val_episodes": ok1,
        "2_val_mean_gt0_and_episode_ci_low_gt0": bool(ok1 and V["net_R"] > 0 and V["boot_episode"]["ci_low"] > 0),
        "3_dev_mean_gt0": bool(D["episodes"] > 0 and D["net_R"] > 0),
        "4_placebo_primary_window": pb_ok,
        "4g_placebo_primary_global_reported": pbg_ok,
        "5_ex_best2_gt0_and_loeo_all_gt0": bool(S["ex_best2_eps"]["mean"] > 0 and S["loeo"]["n"] > 0
                                                and S["loeo"]["min"] > 0),
        "6_vs_basket_per_day": bool(V["net_pd"] == V["net_pd"] and V["basket_pd"] == V["basket_pd"]
                                    and V["net_pd"] >= V["basket_pd"]),
        "7_ex_luna_ftt_and_top3_coin_gt0": bool(S["ex_luna_ftt"]["mean"] > 0 and len(tc) == 3
                                                 and all(t["mean"] > 0 for t in tc)),
        "8_loyo_all_gt0": bool(S["loyo"] and all(v["mean"] > 0 for v in S["loyo"].values())),
        "dose_response_monotone": bool(S["dose_val"]["monotone"]),
        "strata_prediction_holds": bool(S["strata_val"]["holds"]),
    }
    kill = {
        "a_val_mean_le0_with_ge8_eps": bool(ok1 and V["net_R"] <= 0),
        "b_loeo_flips_sign_with_lt12_eps": bool(ok1 and n_ep < 12 and S["loeo"]["flips"] > 0),
        "c_placebo_excess_le_p975": bool(ok1 and pb.get("n_legs", 0) > 0 and not (pb["real"] > pb["p975"])),
    }
    return bars, kill


def verdict_of(S):
    b, k, V = S["bars"], S["kill"], S["VAL"]
    if V["episodes"] < MIN_VAL_EPISODES:
        return "UNDERPOWERED"
    if any(k.values()):
        return "FAIL"
    if S["strata_val"]["flipped"] and V["net_R"] > 0:
        return "SIGN-FLIP"
    core_keys = ["1_power_ge8_val_episodes", "2_val_mean_gt0_and_episode_ci_low_gt0", "3_dev_mean_gt0",
                 "4_placebo_primary_window", "5_ex_best2_gt0_and_loeo_all_gt0", "6_vs_basket_per_day",
                 "dose_response_monotone", "strata_prediction_holds"]
    if not all(b[x] for x in core_keys):
        return "NOT-A-PASS"
    if not (b["7_ex_luna_ftt_and_top3_coin_gt0"] and b["8_loyo_all_gt0"]):
        return "FRAGILE"
    return "PASS"


def holm(pvals):
    """Holm step-down adjusted p-values for a dict {name: p}."""
    names = sorted(pvals, key=lambda n: pvals[n])
    m = len(names)
    out, run = {}, 0.0
    for i, n in enumerate(names):
        run = max(run, min(1.0, (m - i) * pvals[n]))
        out[n] = run
    return out
