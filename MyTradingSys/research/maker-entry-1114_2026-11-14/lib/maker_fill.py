"""maker_fill.py - PRE_REG maker-entry-1114 fill model, pure functions (numpy only).

Fill model (PRE_REG, fixed):
  * Limit order at L placed at the signal bar close (signal_close_ms = open time of the first bar AFTER the signal bar).
    Only 1m bars with t_ms >= signal_close_ms are ever read.
  * FILL only if a 1m bar trades THROUGH L by >= 1 tick (long: low <= L - tick; short: high >= L + tick).
    Touch is no fill. Fill price = L always (a gap-through open also fills at L, never better).
  * Order life = tf_ms from signal_close_ms (60 x 1m for 1h, 15 for 15m), also truncated at time_stop_ms; then miss.
  * Cancel: if the original stop trades before the fill bar, order cancelled (miss). Market-basis stop = touch
    (long low<=stop, short high>=stop); close-basis stop = 1m close through stop.
  * After fill (bars from the fill bar inclusive): stop (market, taker, exit price = stop price; close-basis exits at
    the confirming 1m close), target (resting limit, needs one tick through: long high >= target+tick; maker, exit at
    target), time stop (taker, at open of first 1m bar with t_ms >= time_stop_ms; 'data_end' at last close if data ends).
    Same 1m bar touching stop and target = stop. A bar that fills the entry may also stop it out (stop wins).
    fill_bar_target=True (spec: "from the fill bar") lets the fill bar credit the target; False is stricter.
  * Fees per side of notional: maker 3bp, taker 6bp. Entry maker; target exit maker; stop/time exit taker.
    fee_R = (entry_fee + exit_fee) * L / |L - stop|.  Missed signal: all R = 0.
m1: dict-like with float arrays t_ms,o,h,l,c (sorted, 1m bars; t_ms = bar open time).
"""
import numpy as np

FEES = dict(maker=0.0003, taker=0.0006)
_TICK_CACHE = {}


# ---------------------------------------------------------------- data / tick
def load_m1(sym, root=r"F:\MTS\data_cache\binance_1m"):
    z = np.load(f"{root}\\{sym}_1m.npz")
    return {k: z[k] for k in ("t_ms", "o", "h", "l", "c")}


def estimate_tick(m1, use_cache=True):
    """Smallest nonzero price increment observed in the symbol's 1m data (min gap between distinct o/h/l/c values)."""
    key = (id(m1["t_ms"]), len(m1["t_ms"]))
    if use_cache and key in _TICK_CACHE:
        return _TICK_CACHE[key]
    v = np.unique(np.round(np.concatenate([m1["o"], m1["h"], m1["l"], m1["c"]]), 10))
    d = np.round(np.diff(v), 8)
    d = d[d > 0]
    tick = float(d.min()) if len(d) else 0.0
    if use_cache:
        _TICK_CACHE[key] = tick
    return tick


# ---------------------------------------------------------------- fill simulation
def _miss(reason):
    return dict(filled=False, fill_ms=None, entry_px=None, exit_type=None, exit_ms=None, exit_px=None,
                gross_R=0.0, fee_R=0.0, net_R=0.0, reason_missed=reason)


def simulate_maker(side, L, stop, target, signal_close_ms, tf_ms, time_stop_ms, stop_close_basis, m1, fees=None,
                   tick=None, fill_bar_target=True):
    """side +1/'long' or -1/'short'. target may be None (hold to time stop). Returns dict(filled, fill_ms, entry_px,
    exit_type in {stop,stop_close,target,time,data_end}, exit_ms, exit_px, gross_R, fee_R, net_R, reason_missed)."""
    fees = fees or FEES
    sd = 1 if side in (1, "long", "LONG", "L") else -1
    L, stop = float(L), float(stop)
    risk = (L - stop) * sd
    if not risk > 0:
        raise ValueError("stop must be on the losing side of L")
    if target is not None and not (target - L) * sd > 0:
        raise ValueError("target must be on the winning side of L")
    t, o, h, l, c = m1["t_ms"], m1["o"], m1["h"], m1["l"], m1["c"]
    if tick is None:
        tick = estimate_tick(m1)
    i0 = int(np.searchsorted(t, signal_close_ms, side="left"))   # first bar strictly after the signal bar
    end_ms = signal_close_ms + tf_ms
    if time_stop_ms is not None:
        end_ms = min(end_ms, time_stop_ms)
    ie = int(np.searchsorted(t, end_ms, side="left"))
    if ie <= i0:
        return _miss("no_data")
    # ---- fill search over the order life
    if sd > 0:
        thru = l[i0:ie] <= L - tick
        stp = (c[i0:ie] <= stop) if stop_close_basis else (l[i0:ie] <= stop)
    else:
        thru = h[i0:ie] >= L + tick
        stp = (c[i0:ie] >= stop) if stop_close_basis else (h[i0:ie] >= stop)
    f = int(thru.argmax()) if thru.any() else -1
    s = int(stp.argmax()) if stp.any() else -1
    if f < 0:
        return _miss("stop_before_fill" if s >= 0 else "no_through")
    if s >= 0 and s < f:
        return _miss("stop_before_fill")
    fi = i0 + f
    # ---- after fill: bars from the fill bar to the time stop
    xe = len(t) if time_stop_ms is None else int(np.searchsorted(t, time_stop_ms, side="left"))
    xe = max(xe, fi + 1)
    hh, ll, cc = h[fi:xe], l[fi:xe], c[fi:xe]
    if sd > 0:
        sh = (cc <= stop) if stop_close_basis else (ll <= stop)
        th = (hh >= target + tick) if target is not None else np.zeros(len(hh), bool)
    else:
        sh = (cc >= stop) if stop_close_basis else (hh >= stop)
        th = (ll <= target - tick) if target is not None else np.zeros(len(hh), bool)
    if not fill_bar_target and len(th):
        th = th.copy()
        th[0] = False
    sx = int(sh.argmax()) if sh.any() else -1
    gx = int(th.argmax()) if th.any() else -1
    if sx >= 0 and (gx < 0 or sx <= gx):
        j = fi + sx
        if stop_close_basis:
            exit_type, exit_px = "stop_close", float(c[j])
        else:
            exit_type, exit_px = "stop", stop
        exit_ms, exit_fee = float(t[j]), fees["taker"]
    elif gx >= 0:
        j = fi + gx
        exit_type, exit_px, exit_ms, exit_fee = "target", float(target), float(t[j]), fees["maker"]
    elif xe < len(t) and time_stop_ms is not None:
        exit_type, exit_px, exit_ms, exit_fee = "time", float(o[xe]), float(t[xe]), fees["taker"]
    else:
        exit_type, exit_px, exit_ms, exit_fee = "data_end", float(c[-1]), float(t[-1]), fees["taker"]
    gross = (exit_px - L) * sd / risk
    fee_R = (fees["maker"] + exit_fee) * L / risk
    return dict(filled=True, fill_ms=float(t[fi]), entry_px=L, exit_type=exit_type, exit_ms=exit_ms, exit_px=exit_px,
                gross_R=float(gross), fee_R=float(fee_R), net_R=float(gross - fee_R), reason_missed=None)


# ---------------------------------------------------------------- summary / stats
def _boot_mean_ci(x, n, rng, chunk=250):
    x = np.asarray(x, float)
    m = np.empty(n)
    for a in range(0, n, chunk):
        b = min(n, a + chunk)
        m[a:b] = x[rng.integers(0, len(x), size=(b - a, len(x)))].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _day_of(r):
    if r.get("day") is not None:
        return int(r["day"])
    ms = r.get("fill_ms") if r.get("filled") else r.get("signal_close_ms")
    return int(ms // 86400000) if ms is not None else 0


def summarize(results, n_boot=10000, n_cluster=5000, seed=7, thin_fill_rate=0.30):
    """results: list of per-signal dicts from simulate_maker (optionally with 'day' = UTC day number, else derived
    from fill_ms). Misses count as 0 R in per_signal_R. Bootstrap: per-trade (n_boot) then UTC-day cluster
    (n_cluster) with default_rng(seed). ex_best5_days: mean net R over filled trades after dropping the 5 UTC days with
    the highest total net R."""
    n = len(results)
    filled = [r for r in results if r["filled"]]
    nf = len(filled)
    out = dict(n_signals=n, n_filled=nf, fill_rate=(nf / n if n else float("nan")),
               thin=bool(n and nf / n < thin_fill_rate))
    if nf == 0:
        out.update(mean_net_R_filled=float("nan"), mean_gross_R_filled=float("nan"), mean_fee_R_filled=float("nan"),
                   per_signal_R=0.0, ci_trade=(float("nan"),) * 2, ci_day=(float("nan"),) * 2,
                   ex_best5_days=float("nan"), n_days=0)
        return out
    net = np.array([r["net_R"] for r in filled])
    gross = np.array([r["gross_R"] for r in filled])
    fee = np.array([r["fee_R"] for r in filled])
    days = np.array([_day_of(r) for r in filled])
    out.update(mean_net_R_filled=float(net.mean()), mean_gross_R_filled=float(gross.mean()),
               mean_fee_R_filled=float(fee.mean()), per_signal_R=float(net.sum() / n))
    rng = np.random.default_rng(seed)
    out["ci_trade"] = _boot_mean_ci(net, n_boot, rng)
    ud, inv = np.unique(days, return_inverse=True)
    S = np.bincount(inv, weights=net, minlength=len(ud))
    N = np.bincount(inv, minlength=len(ud)).astype(float)
    idx = rng.integers(0, len(ud), size=(n_cluster, len(ud)))
    cm = S[idx].sum(axis=1) / N[idx].sum(axis=1)
    out["ci_day"] = (float(np.percentile(cm, 2.5)), float(np.percentile(cm, 97.5)))
    keep = np.ones(len(ud), bool)
    keep[np.argsort(-S, kind="stable")[:5]] = False
    out["n_days"] = int(len(ud))
    out["ex_best5_days"] = float(S[keep].sum() / N[keep].sum()) if N[keep].sum() > 0 else float("nan")
    return out


def benjamini_hochberg(pvals, q=0.05):
    """Returns (reject list[bool], adjusted p list) in input order."""
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p, kind="stable")
    ranked = p[order] * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1.0)
    out = np.empty(m)
    out[order] = adj
    return [bool(x <= q) for x in out], out.tolist()


def gates(summary, placebo_p, bh_reject):
    """PRE_REG PASS gates 1-6 -> dict(gates={1..6: bool}, passed, failed list, thin)."""
    s = summary
    g = {1: s["n_filled"] >= 100,
         2: s["n_filled"] > 0 and s["mean_net_R_filled"] > 0,
         3: s["n_filled"] > 0 and s["ci_trade"][0] > 0 and s["ci_day"][0] > 0,
         4: placebo_p is not None and placebo_p < 0.05,
         5: bool(bh_reject),
         6: s["n_filled"] > 0 and s["ex_best5_days"] > 0}
    g = {k: bool(v) for k, v in g.items()}
    return dict(gates=g, passed=all(g.values()), failed=[k for k, v in g.items() if not v], thin=s["thin"])


# ---------------------------------------------------------------- placebo helpers
def signal_offsets_atr(side, L, signal_close, atr):
    """Empirical passive offset of the real signals in ATR units: positive = L farther from the close in the passive
    direction (long: close - L; short: L - close). side: array of +1/-1 (or scalar)."""
    sd = np.where(np.asarray(side) > 0, 1.0, -1.0)
    return (np.asarray(signal_close, float) - np.asarray(L, float)) * sd / np.asarray(atr, float)


def placebo_limit(side, close, atr, offset_atr):
    """Limit level for a random bar: close shifted passively by offset_atr * atr (long below, short above)."""
    sd = 1 if side in (1, "long", "LONG", "L") else -1
    return close - sd * offset_atr * atr


def placebo_pvalue(observed_mean, run_one, candidates, offsets, n_filled, n_draws=1000, seed=7, max_tries_factor=200):
    """Like-for-like placebo. Each draw: sample random candidate bars (same symbol/side/phase/tf/VALIDATION, built by
    the caller) with replacement and an offset from the empirical `offsets` array, call run_one(candidate, offset) ->
    simulate_maker result (caller builds L via placebo_limit and the same stop/target machinery, and MUST use
    simulate_maker), until n_filled FILLED trades are collected; draw statistic = their mean net R.
    p = (1 + #(draw >= observed)) / (n_draws + 1). Returns (p, draws array)."""
    rng = np.random.default_rng(seed)
    offsets = np.asarray(offsets, float)
    draws = np.empty(n_draws)
    for d in range(n_draws):
        got, tries, acc = 0, 0, 0.0
        while got < n_filled:
            tries += 1
            if tries > max_tries_factor * n_filled:
                raise RuntimeError("placebo fill rate too low to reach n_filled")
            cand = candidates[int(rng.integers(0, len(candidates)))]
            r = run_one(cand, float(offsets[int(rng.integers(0, len(offsets)))]))
            if r["filled"]:
                got += 1
                acc += r["net_R"]
        draws[d] = acc / n_filled
    return float((1 + np.sum(draws >= observed_mean)) / (n_draws + 1)), draws
