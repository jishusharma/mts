"""T5 step C: statistics, pass bars, verdict, tables. NOT run on real data until step B (recompute + audit) is clean.

    python t5_stats.py [--cache F:/MTS/data_cache/binance/wave2-1114] [--dir <study folder>]

Reads trades.csv (step A) and the wave2 cache (placebo, baseline, regime mix); writes summary.json and tables.md.
All statistic functions are pure numpy and are exercised by test_t5_core.py on synthetic bars.
Seeds: 1114 everywhere (SOURCED, design note).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t5_core as T  # noqa: E402

SEED = 1114
NBOOT = 2000
NDRAW = 1000
ROWS = {"12_nofund": (T.RT_COST, False), "12_fund": (T.RT_COST, True),
        "6_nofund": (T.RT_COST_HALF, False), "6_fund": (T.RT_COST_HALF, True)}
MAIN_ROWS = ("12_nofund", "12_fund")
# Source-cell summary numbers (buyzone_test3 REPORT, copied as given in PRE_REG; not re-run): (n, mean R without funding, with funding)
SOURCE22 = {"DEV": (287, 0.107, 0.111), "VAL": (211, 0.090, 0.092), "POOLED": (498, 0.100, 0.103)}


def lower_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


# ---------------------------------------------------------------- basic statistics
def mean_sd(R):
    R = np.asarray(R, float)
    if len(R) == 0:
        return None, None
    return float(R.mean()), (float(R.std(ddof=1)) if len(R) > 1 else None)


def week_boot(R, weeks, nboot=NBOOT, seed=SEED):
    """Cluster bootstrap on ISO entry week: resample whole weeks with replacement, statistic = mean R of the pooled trades of the
    resampled weeks. Percentile 95% CI; one-sided p = (1 + #(resample means <= 0)) / (nboot + 1)."""
    R = np.asarray(R, float)
    if len(R) == 0:
        return dict(mean=None, lo=None, hi=None, p_one=None, n_weeks=0)
    uw, inv = np.unique(np.asarray(weeks), return_inverse=True)
    sums = np.bincount(inv, weights=R, minlength=len(uw))
    cnts = np.bincount(inv, minlength=len(uw)).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(uw), size=(nboot, len(uw)))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return dict(mean=float(R.mean()), lo=float(np.percentile(means, 2.5)), hi=float(np.percentile(means, 97.5)),
                p_one=float((1 + np.sum(means <= 0)) / (nboot + 1)), n_weeks=int(len(uw)))


def ex_best_weeks(R, weeks, k=5):
    """Mean R of the trades left after removing the k ISO weeks with the largest summed R (None if nothing is left)."""
    R = np.asarray(R, float)
    weeks = np.asarray(weeks)
    uw, inv = np.unique(weeks, return_inverse=True)
    sums = np.bincount(inv, weights=R, minlength=len(uw))
    drop = set(np.argsort(-sums, kind="stable")[:k].tolist())
    keep = np.array([i not in drop for i in inv], dtype=bool)
    return (float(R[keep].mean()) if keep.any() else None), int(keep.sum())


def top_coin_removed(R, coins):
    """Remove the coin with the largest summed R; mean R of the rest."""
    R = np.asarray(R, float)
    coins = np.asarray(coins)
    if len(R) == 0:
        return None, None, 0
    best = max(set(coins.tolist()), key=lambda s: R[coins == s].sum())
    keep = coins != best
    return best, (float(R[keep].mean()) if keep.any() else None), int(keep.sum())


def placebo_percentile(real, draws):
    """Share of draw means below the real mean, ties counted half, in percent."""
    draws = np.asarray(draws, float)
    if len(draws) == 0 or real is None:
        return None
    return float(100.0 * (np.sum(draws < real) + 0.5 * np.sum(draws == real)) / len(draws))


def beats_placebo(real, draws):
    draws = np.asarray(draws, float)
    return bool(len(draws) and real is not None and real > np.percentile(draws, 97.5))


# ---------------------------------------------------------------- placebo (random eligible bars, same coin / split / stop distance)
class CoinTable:
    """Per-coin windows for every 4h bar as a possible entry bar, so any (entry bar, stop distance r) is evaluated in one go."""

    def __init__(self, ts, o, h, l, c, bear_a, lab_a, G, first_fund):
        n = len(c)
        self.n, self.ts = n, np.asarray(ts)
        atr = T.wilder_atr(h, l, c)
        nanp = np.full(T.HOLD, np.nan)
        pad = lambda a: np.concatenate([np.asarray(a, float), nanp])
        win = lambda a: sliding_window_view(pad(a), T.HOLD)[:n]
        self.O, self.H, Lw, Aw = win(o), win(h), win(l), win(atr)
        cm = np.minimum.accumulate(Lw, axis=1)
        self.Tw = np.full((n, T.HOLD), np.inf)
        self.Tw[:, 1:] = cm[:, :-1] + T.TRAIL_ATR * Aw[:, :-1]
        self.Cend = pad(c)[T.HOLD - 1:T.HOLD - 1 + n]
        self.Gp, self.G0 = pad(G), np.asarray(G, float)
        self.cov = np.zeros(n, bool) if first_fund is None else (self.ts >= first_fund)
        ok = np.asarray(bear_a, bool) & (np.asarray(lab_a) != "")
        ok[:T.WARM4] = False
        self.eligible = ok

    def pool(self, split):
        ok = self.eligible.copy()
        if split == "DEV":
            ok &= self.ts < T.VAL_START
        elif split == "VAL":
            ok &= self.ts >= T.VAL_START
        return np.nonzero(ok)[0]

    def outcome(self, idx, r):
        """(gross, funding) for shorts at the open of bars idx with stop distance r (arrays of one shape (m, ...)); NaN where the
        trade is still open at the data end."""
        idx = np.asarray(idx)
        shp = idx.shape
        i, rr = idx.ravel(), np.asarray(r, float).ravel()
        entry = self.O[i, 0]
        lvl = np.minimum((entry * (1 + rr))[:, None], self.Tw[i])
        hit = self.H[i] >= lvl
        anyhit = hit.any(1)
        first = hit.argmax(1)
        lv_f = np.take_along_axis(lvl, first[:, None], 1)[:, 0]
        op_f = np.take_along_axis(self.O[i], first[:, None], 1)[:, 0]
        px = np.where(anyhit, np.maximum(op_f, lv_f), self.Cend[i])
        gross = (entry - px) / entry
        xk = np.where(anyhit, first, T.HOLD - 1)
        fund = np.where(self.cov[i], self.Gp[i + xk] - self.G0[i], 0.0)
        gross = np.where(np.isnan(px), np.nan, gross)
        return gross.reshape(shp), fund.reshape(shp)


def placebo_draws(tables, trades, split, ndraw=NDRAW, seed=SEED, chunk=200):
    """trades: list of (coin, r). One draw = a matched set: each real trade is replaced by a short at a uniformly random eligible bar of
    the same coin and split (BEAR true, past warm-up) with the real trade's own r and the same exit rule; draw statistic = mean R over
    the set (trades that stay open at the data end are dropped from that draw). No lockout on draws. Returns
    ({row: draw means}, n_matched, n_unmatched)."""
    rng = np.random.default_rng(seed)
    by = defaultdict(list)
    for coin, r in trades:
        by[coin].append(r)
    parts, unmatched = [], 0
    for coin in sorted(by):
        pool = tables[coin].pool(split) if coin in tables else np.array([], int)
        if len(pool) == 0:
            unmatched += len(by[coin])
            continue
        parts.append((coin, pool, np.array(by[coin], float)))
    out = {k: [] for k in ROWS}
    if not parts:
        return {k: np.array([]) for k in ROWS}, 0, unmatched
    matched = sum(len(p[2]) for p in parts)
    for s in range(0, ndraw, chunk):
        m = min(chunk, ndraw - s)
        tot = {k: np.zeros(m) for k in ROWS}
        cnt = np.zeros(m)
        for coin, pool, r in parts:
            idx = pool[rng.integers(0, len(pool), size=(m, len(r)))]
            rr = np.broadcast_to(r, idx.shape)
            g, fu = tables[coin].outcome(idx, rr)
            valid = ~np.isnan(g)
            cnt += valid.sum(1)
            for k, (cost, wf) in ROWS.items():
                v = (g - cost + (fu if wf else 0.0)) / rr
                tot[k] += np.where(valid, v, 0.0).sum(1)
        for k in ROWS:
            out[k].append(tot[k] / np.maximum(cnt, 1))
    return {k: np.concatenate(v) for k, v in out.items()}, matched, unmatched


# ---------------------------------------------------------------- baseline: short-and-hold of the basket over BEAR coin-days
def basket_short_daily(coins, start_ms, end_ms, with_funding):
    """coins: list of dict(dts, close, bear, fund_day) where bear[t] is the flag built from daily bars through t and fund_day maps
    UTC day number -> summed funding prints. Day d counts a coin iff the flag at daily bar d-1 is true and closes exist for d-1 and d.
    Return of the day = -(Close[d]/Close[d-1] - 1) (+ that coin's funding prints inside day d when with_funding); equal weight
    across the counted coins; no fee, no rebalance cost. Returns (mean over days in [start, end) with at least one coin, n_days)."""
    d0, d1 = start_ms // T.DAY, end_ms // T.DAY
    tot = np.zeros(d1 - d0 + 1)
    cnt = np.zeros(d1 - d0 + 1)
    for cn in coins:
        days = np.asarray(cn["dts"]) // T.DAY
        c, bear = np.asarray(cn["close"], float), np.asarray(cn["bear"], bool)
        for i in range(1, len(days)):
            d = days[i]
            if d < d0 or d >= d1 or days[i - 1] != d - 1 or not bear[i - 1]:
                continue
            v = -(c[i] / c[i - 1] - 1.0)
            if with_funding:
                v += cn["fund_day"].get(int(d), 0.0)
            tot[d - d0] += v
            cnt[d - d0] += 1
    ok = cnt > 0
    if not ok.any():
        return None, 0
    return float((tot[ok] / cnt[ok]).mean()), int(ok.sum())


def signal_rate(trades, row):
    """(sum of net return per trade) / (sum of days held), held bars = exit bar - entry bar + 1, one bar = 4/24 day."""
    if not trades:
        return None
    cost, wf = ROWS[row]
    num = sum(t["gross"] - cost + (t["funding"] if wf else 0.0) for t in trades)
    den = sum(t["bars_held"] * 4.0 / 24.0 for t in trades)
    return float(num / den)


# ---------------------------------------------------------------- verdict
def verdict(rows):
    """rows: {'12_nofund': info, '12_fund': info}, info keys: val_n, val_weeks, val_mean, val_ci_lo, dev_mean, pooled_mean,
    val_pct, val_beats, exbest5, sig_rate, base_rate, topcoin_rest, one_year, val_p. Order: UNDERPOWERED, KILL, PASS, REPLICATED-WEAK, FAIL."""
    notes = {}
    for k, v in rows.items():
        b = {1: v["val_n"] >= 30 and v["val_weeks"] >= 20,
             2: v["val_mean"] is not None and v["val_mean"] > 0 and v["val_ci_lo"] is not None and v["val_ci_lo"] > 0,
             3: v["dev_mean"] is not None and v["dev_mean"] > 0,
             4: bool(v["val_beats"]),
             5: v["exbest5"] is not None and v["exbest5"] > 0,
             6: v["sig_rate"] is not None and v["base_rate"] is not None and v["sig_rate"] >= v["base_rate"],
             7: v["topcoin_rest"] is not None and v["topcoin_rest"] > 0}
        notes[k] = b
    labels = []
    if not all(notes[k][1] for k in notes):
        return dict(verdict="UNDERPOWERED", labels=labels, failing={k: [i for i, ok in notes[k].items() if not ok] for k in notes}, bars=notes)
    kill = any(v["pooled_mean"] is None or v["pooled_mean"] <= 0 or (v["val_pct"] is not None and v["val_pct"] < 90 and v["val_n"] >= 200)
               for v in rows.values())
    failing = {k: [i for i, ok in notes[k].items() if not ok] for k in notes}
    if kill:
        return dict(verdict="KILL", labels=labels, failing=failing, bars=notes)
    if not all(notes[k][7] for k in notes):
        labels.append("FRAGILE")
    if any(v["one_year"] for v in rows.values()):
        labels.append("ONE-YEAR")
    if all(not failing[k] for k in notes) and not labels:
        return dict(verdict="PASS", labels=labels, failing=failing, bars=notes)
    pos = all(v["pooled_mean"] > 0 and v["dev_mean"] > 0 and v["val_mean"] > 0 for v in rows.values())
    if pos:
        return dict(verdict="REPLICATED-WEAK", labels=labels, failing=failing, bars=notes)
    return dict(verdict="FAIL", labels=labels, failing=failing, bars=notes)


# ---------------------------------------------------------------- loading
def load_trades(path):
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = dict(r)
            for k in ("gross", "funding", "r", "R12_nofund", "R12_fund", "R6_nofund", "R6_fund", "net12_nofund", "net12_fund"):
                t[k] = float(r[k])
            for k in ("bars_held", "bear", "fund_covered", "fund_gap", "recent", "year", "sig_ts", "entry_ts"):
                t[k] = int(r[k])
            out.append(t)
    return out


def rvec(trs, row):
    return np.array([t["R" + row] for t in trs], float)


def cell(trs, row):
    R = rvec(trs, row)
    m, sd = mean_sd(R)
    out = dict(n=len(R), mean=m, sd=sd, win=(float((R > 0).mean()) if len(R) else None), weeks=len(set(t["iso_week"] for t in trs)))
    if len(R):
        out.update({k: v for k, v in week_boot(R, [t["iso_week"] for t in trs]).items() if k in ("lo", "hi", "p_one")})
    return out


def load_world(cache, coins):
    """Rebuild per-coin tables and daily info from the cache with the same loaders and flags as step A."""
    import t5_trades as A
    tables, daily = {}, []
    reg = defaultdict(lambda: defaultdict(Counter))
    for sym in coins:
        k4 = A.load_klines(os.path.join(cache, "spot_4h", sym + "USDT.csv"))
        k1 = A.load_klines(os.path.join(cache, "spot_1d", sym + "USDT.csv"))
        ts = k4[:, 0].astype(np.int64)
        dts = k1[:, 0].astype(np.int64)
        bear_d, lab_d = T.daily_bear(k1[:, 2], k1[:, 3], k1[:, 4])
        bearA = T.map_day_flag(ts, dts, bear_d, False)
        labA = T.map_day_flag(ts, dts, lab_d, "")
        fund = A.load_funding(os.path.join(cache, "funding", sym + "USDT.csv")) or []
        G, first_f, _ = T.funding_cum(ts, fund)
        tables[sym] = CoinTable(ts, k4[:, 1], k4[:, 2], k4[:, 3], k4[:, 4], bearA, labA, G, first_f)
        fd = defaultdict(float)
        for s, r in fund:
            fd[int(s // T.DAY)] += r
        daily.append(dict(dts=dts, close=k1[:, 4], bear=bear_d, fund_day=dict(fd)))
        # regime mix: coin-days with a defined phase, by split of the day (flag read at D-1 is the same series shifted by a day)
        for i in range(1, len(dts)):
            if lab_d[i - 1] == "":
                continue
            sp = "DEV" if dts[i] < T.VAL_START else "VAL"
            reg[sp]["bear"][bool(bear_d[i - 1])] += 1
            reg[sp]["label"][lab_d[i - 1]] += 1
    return tables, daily, reg


# ---------------------------------------------------------------- main (step C)
def md_table(head, rows):
    f = lambda v: "n/a" if v is None else ("%.3f" % v if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(f(x) for x in r) + " |" for r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="F:/MTS/data_cache/binance/wave2-1114")
    ap.add_argument("--dir", default=HERE)
    ap.add_argument("--ndraw", type=int, default=NDRAW)
    a = ap.parse_args()
    lower_priority()
    trades = load_trades(os.path.join(a.dir, "trades.csv"))
    cov = json.load(open(os.path.join(a.dir, "coverage.json"), encoding="utf-8"))
    claim = [t for t in trades if t["bear"] == 1]
    ctrl = [t for t in trades if t["bear"] == 0]
    sel = {"DEV": [t for t in claim if t["split"] == "DEV"], "VAL": [t for t in claim if t["split"] == "VAL"],
           "POOLED": claim, "RECENT": [t for t in claim if t["recent"] == 1]}
    tables, daily, reg = load_world(a.cache, cov["kept"])
    S, md = {"cells": {}, "placebo": {}, "bars": {}, "baseline": {}}, []
    for sp, trs in sel.items():
        for row in ROWS:
            S["cells"]["%s|%s" % (sp, row)] = cell(trs, row)
    for sp in ("DEV", "VAL", "POOLED"):
        key = {"DEV": "DEV", "VAL": "VAL", "POOLED": "ALL"}[sp]
        d, nm, nu = placebo_draws(tables, [(t["coin"], t["r"]) for t in sel[sp]], key, a.ndraw)
        for row in ROWS:
            real = cell(sel[sp], row)["mean"]
            S["placebo"]["%s|%s" % (sp, row)] = dict(pct=placebo_percentile(real, d[row]), beats=beats_placebo(real, d[row]),
                                                     p97_5=(float(np.percentile(d[row], 97.5)) if len(d[row]) else None),
                                                     matched=nm, unmatched=nu)
    base = {}
    for sp, (s0, s1) in {"DEV": (0, T.VAL_START), "VAL": (T.VAL_START, 4102444800000)}.items():
        for row in MAIN_ROWS:
            sr = signal_rate(sel[sp], row)
            br, nd = basket_short_daily(daily, s0, s1, ROWS[row][1])
            base["%s|%s" % (sp, row)] = dict(signal_rate=sr, base_rate=br, base_days=nd)
    S["baseline"] = base
    info = {}
    for row in MAIN_ROWS:
        v = sel["VAL"]
        R = rvec(v, row)
        yrs = Counter(t["year"] for t in v)
        c = S["cells"]["VAL|" + row]
        info[row] = dict(val_n=c["n"], val_weeks=c["weeks"], val_mean=c["mean"], val_ci_lo=c.get("lo"), val_p=c.get("p_one"),
                         dev_mean=S["cells"]["DEV|" + row]["mean"], pooled_mean=S["cells"]["POOLED|" + row]["mean"],
                         val_pct=S["placebo"]["VAL|" + row]["pct"], val_beats=S["placebo"]["VAL|" + row]["beats"],
                         exbest5=ex_best_weeks(R, [t["iso_week"] for t in v])[0] if len(R) else None,
                         sig_rate=base["VAL|" + row]["signal_rate"], base_rate=base["VAL|" + row]["base_rate"],
                         topcoin_rest=top_coin_removed(R, [t["coin"] for t in v])[1],
                         top_coin=top_coin_removed(R, [t["coin"] for t in v])[0],
                         one_year=bool(len(v) and max(yrs.values()) / len(v) > 0.85))
    S["bars"] = info
    S["verdict"] = verdict(info)
    S["verdict"]["raw_val_p_larger_row"] = max((i["val_p"] for i in info.values() if i["val_p"] is not None), default=None)
    # descriptive cuts
    S["by_year"] = {str(y): {r: cell([t for t in claim if t["year"] == y], r) for r in MAIN_ROWS} for y in sorted(set(t["year"] for t in claim))}
    S["by_coin"] = {s: dict(cell([t for t in claim if t["coin"] == s], "12_fund"), underpowered=sum(1 for t in claim if t["coin"] == s) < 30)
                    for s in sorted(set(t["coin"] for t in claim))}
    S["by_btc_cycle"] = {k: cell([t for t in claim if t["btc_cycle"] == k], "12_fund") for k in sorted(set(t["btc_cycle"] for t in claim))}
    S["by_btc_label"] = {k: cell([t for t in claim if t["btc_label"] == k], "12_fund") for k in sorted(set(t["btc_label"] for t in claim))}
    S["control_by_t1_label"] = {k: {r: cell([t for t in ctrl if t["t1_label"] == k], r) for r in MAIN_ROWS}
                                for k in T.T1_PHASES}
    S["regime_mix"] = {sp: dict(bear_share=(reg[sp]["bear"][True] / max(1, sum(reg[sp]["bear"].values()))),
                                t1_label_share={k: reg[sp]["label"][k] / max(1, sum(reg[sp]["label"].values())) for k in T.T1_PHASES})
                       for sp in ("DEV", "VAL")}
    S["regime_mix"]["claim_trade_share_by_year"] = {sp: {str(y): n / len(sel[sp]) for y, n in sorted(Counter(t["year"] for t in sel[sp]).items())}
                                                    for sp in ("DEV", "VAL", "POOLED") if sel[sp]}
    S["regime_mix"]["claim_trade_btc_cycle_share"] = {k: n / len(claim) for k, n in Counter(t["btc_cycle"] for t in claim).items()} if claim else {}
    S["time_in_market_bars"] = {sp: int(sum(t["bars_held"] for t in sel[sp])) for sp in sel}
    S["sd_R"] = {"%s|%s" % (sp, r): cell(sel[sp], r)["sd"] for sp in sel for r in MAIN_ROWS}
    S["dropped_entry_ge_stop"] = sum(v["drop_entry_ge_stop"] for v in cov["per_coin"].values())
    S["trades_without_funding_cover"] = sum(1 for t in claim if t["fund_covered"] == 0)
    S["trades_hold_past_funding_end"] = sum(1 for t in claim if t["fund_gap"] == 1)
    # old 22 + fresh pooled: n-weighted from the SOURCE summary numbers, NOT re-run
    S["old22_plus_fresh_not_rerun"] = {}
    for sp in ("DEV", "VAL", "POOLED"):
        n0, m_nf, m_f = SOURCE22[sp]
        for lab, m0, row in (("nofund", m_nf, "12_nofund"), ("fund", m_f, "12_fund")):
            c = S["cells"]["%s|%s" % (sp, row)]
            if c["n"]:
                S["old22_plus_fresh_not_rerun"]["%s|%s" % (sp, lab)] = dict(n=n0 + c["n"], mean=(n0 * m0 + c["n"] * c["mean"]) / (n0 + c["n"]))
    with open(os.path.join(a.dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(S, f, indent=1, default=lambda o: None if o is None else str(o))
    md.append("# T5 tables (step C output, generated)\n")
    md.append("Verdict: **%s** labels %s failing bars %s raw VAL p (larger row) %s\n" % (
        S["verdict"]["verdict"], S["verdict"]["labels"], S["verdict"]["failing"], S["verdict"]["raw_val_p_larger_row"]))
    md.append(md_table(["split|row", "n", "weeks", "mean R", "sd", "win", "CI lo", "CI hi", "p one"],
                       [[k, c["n"], c["weeks"], c["mean"], c["sd"], c["win"], c.get("lo"), c.get("hi"), c.get("p_one")] for k, c in S["cells"].items()]))
    md.append("\nPlacebo (12 bp rows)\n")
    md.append(md_table(["split|row", "pct", "beats 97.5", "p97.5 draw mean", "matched", "unmatched"],
                       [[k, p["pct"], p["beats"], p["p97_5"], p["matched"], p["unmatched"]] for k, p in S["placebo"].items() if k.split("|")[1] in MAIN_ROWS]))
    md.append("\nBaseline (per day)\n")
    md.append(md_table(["split|row", "signal rate", "baseline rate", "baseline days"],
                       [[k, b["signal_rate"], b["base_rate"], b["base_days"]] for k, b in base.items()]))
    md.append("\nBy coin (12 bp with funding)\n")
    md.append(md_table(["coin", "n", "mean R", "underpowered"], [[k, c["n"], c["mean"], c["underpowered"]] for k, c in S["by_coin"].items()]))
    md.append("\nBy year (12 bp with funding)\n")
    md.append(md_table(["year", "n", "mean R"], [[y, v["12_fund"]["n"], v["12_fund"]["mean"]] for y, v in S["by_year"].items()]))
    md.append("\nControl, BEAR false by Test 1 label (12 bp with funding)\n")
    md.append(md_table(["label", "n", "mean R"], [[k, v["12_fund"]["n"], v["12_fund"]["mean"]] for k, v in S["control_by_t1_label"].items()]))
    with open(os.path.join(a.dir, "tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("verdict", S["verdict"]["verdict"], "- see summary.json and tables.md")


if __name__ == "__main__":
    main()
