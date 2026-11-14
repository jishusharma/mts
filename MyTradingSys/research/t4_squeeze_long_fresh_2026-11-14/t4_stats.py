"""T4 step C: statistics on the trade list, exactly the bars of PRE_REG.md. NOT run on real data until the step B audit is clean
(the CLI refuses to run without --run). Every function takes plain arrays or small frames so the committed tests can feed it
synthetic data.

Bars (verdict cell = fresh coins, non-bear, RIDE, all at 12 bp plus actual funding):
  1 power: VAL n >= 30 and >= 20 distinct entry weeks
  2 VAL mean net R > 0 and week-cluster bootstrap 95% CI low > 0 (2000 resamples, seed 1114); one-sided p = (1 + #(means <= 0)) / (2000 + 1)
  3 DEV mean net R > 0
  4 excess over 1000 same-coin, same-split, non-bear, resolved, entry-eligible random entries with the real stop distance (percent of entry)
  5 ex-best-5 entry weeks on the T3R row (VAL) > 0
  6 strategy mean net daily return in position >= equal-weight fresh basket mean daily return on non-bear days (VAL)
  7 top-coin removal: VAL RIDE mean > 0 after removing each coin in turn (else FRAGILE)
"""
import argparse
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t4_core as C  # noqa: E402

SEED = C.SEED
N_BOOT = 2000
N_PLACEBO = 1000
NONBEAR_NAMES = [C.PHASES[i] for i in C.NONBEAR]


# ------------------------------------------------------------------ week bootstrap and ex-best weeks
def week_bootstrap(r, weeks, n_boot=N_BOOT, seed=SEED):
    """Resample ENTRY WEEKS with replacement; each resample takes all trades of the drawn weeks; statistic = mean net R over those
    trades. CI = 2.5th / 97.5th percentiles; one-sided p = (1 + #(resampled means <= 0)) / (n_boot + 1)."""
    r = np.asarray(r, float)
    n = len(r)
    if n == 0:
        return dict(n=0, weeks=0, mean=float("nan"), lo=float("nan"), hi=float("nan"), p=float("nan"), n_boot=n_boot)
    _, inv = np.unique(np.asarray(weeks), return_inverse=True)
    g = int(inv.max()) + 1
    sums = np.bincount(inv, weights=r, minlength=g)
    cnts = np.bincount(inv, minlength=g).astype(float)
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    step = 250
    for a in range(0, n_boot, step):
        b = min(n_boot, a + step)
        ix = rng.integers(0, g, size=(b - a, g))
        means[a:b] = sums[ix].sum(1) / cnts[ix].sum(1)
    return dict(n=n, weeks=g, mean=float(r.mean()), lo=float(np.percentile(means, 2.5)), hi=float(np.percentile(means, 97.5)),
                p=float((1 + (means <= 0).sum()) / (n_boot + 1)), n_boot=n_boot)


def ex_best_weeks(r, weeks, k=5):
    """Rank entry weeks by the sum of net R, drop the k best weeks, mean net R of the remaining trades (NaN if none remain)."""
    r = np.asarray(r, float)
    w = np.asarray(weeks)
    df = pd.DataFrame(dict(r=r, w=w))
    sums = df.groupby("w").r.sum().sort_values(ascending=False, kind="stable")
    drop = set(sums.index[:k])
    rest = df[~df.w.isin(drop)]
    return dict(mean=float(rest.r.mean()) if len(rest) else float("nan"), n_left=int(len(rest)), weeks_dropped=sorted(map(str, drop)),
                weeks_total=int(len(sums)))


# ------------------------------------------------------------------ placebo (random entries, same coin / split / phase flag / stop pct)
def placebo_candidates(coin, window="VAL"):
    """Signal bars a random entry may use: same split, non-bear phase flag at the entry day, entry-eligible, a next bar exists."""
    sig_day = coin.ts // C.DAY
    wmask = (sig_day <= C.DEV_END_DAY) if window == "DEV" else (sig_day >= C.VAL_START_DAY)
    ok = coin.elig & wmask & np.isin(np.nan_to_num(coin.phase, nan=-1), list(C.NONBEAR))
    ok[-1] = False
    return np.flatnonzero(ok)


def placebo_draws(coins, trades, n_draw=N_PLACEBO, seed=SEED, window="VAL", rounds=12):
    """coins = {sym: Coin}; trades = frame with columns coin, risk (the real RIDE trades of the window). One draw = for every real
    trade one random bar of the same coin (resolved, not overlap-filtered), the real S / entry as stop distance, the RIDE exit rules,
    12 bp plus the actual funding of its own window; draw statistic = mean net R over the matched set. Returns dict(means, dropped)
    where dropped counts matches that stayed unresolved after `rounds` redraws."""
    rng = np.random.default_rng(seed)
    sum_r = np.zeros(n_draw)
    cnt = np.zeros(n_draw)
    dropped = 0
    for sym, g in trades.groupby("coin"):
        coin = coins[sym]
        cand = placebo_candidates(coin, window)
        if cand.size == 0:
            dropped += len(g) * n_draw
            continue
        risk = np.tile(g.risk.to_numpy(float), n_draw)
        draw_id = np.repeat(np.arange(n_draw), len(g))
        pick = rng.choice(cand, size=len(risk))
        todo = np.arange(len(risk))
        for _ in range(rounds):
            if todo.size == 0:
                break
            sg = pick[todo]
            nxt = sg + 1                                 # entry bar = the bar after the random signal bar
            S = risk[todo] * coin.o[nxt]
            sm = C.simulate(coin.o, coin.h, coin.l, coin.c, sg, S, "RIDE", coin.exit_lvl)
            res = sm["xi"] >= 0
            ok_i = todo[res]
            fund = C.funding_paid(coin.cf, sm["e"][res], sm["xt"][res])
            rr = C.net_r(sm["ret"][res], fund, risk[ok_i])
            np.add.at(sum_r, draw_id[ok_i], rr)
            np.add.at(cnt, draw_id[ok_i], 1)
            todo = todo[~res]
            if todo.size:
                pick[todo] = rng.choice(cand, size=todo.size)
        dropped += int(todo.size)
    means = np.where(cnt > 0, sum_r / np.maximum(cnt, 1), np.nan)
    return dict(means=means, dropped=dropped)


def placebo_verdict(real_mean, means):
    means = np.asarray(means, float)
    means = means[~np.isnan(means)]
    p975 = float(np.percentile(means, 97.5))
    return dict(real=float(real_mean), placebo_mean=float(means.mean()), placebo_p975=p975, excess=float(real_mean - means.mean()),
                percentile=float((means < real_mean).mean()), beats=bool(real_mean > p975 and real_mean - means.mean() > 0),
                n_draws=int(len(means)))


# ------------------------------------------------------------------ buy-and-hold baseline
def basket_daily(closes, starts, table, day_lo, day_hi):
    """Equal-weight basket mean daily return over the UTC days in [day_lo, day_hi] whose phase label (keyed to that day, built from
    closes of days <= D-1) is non-bear. closes = {sym: (day_numbers, closes)}, starts = {sym: first eligible day number}. A coin counts
    on day D if it has closes on D and D-1 and D >= its entry-window start. Returns dict(mean, days)."""
    days = np.arange(day_lo, day_hi + 1)
    lab = C.phase_for_days(table, days)
    good = np.isin(np.nan_to_num(lab, nan=-1), list(C.NONBEAR))
    acc = np.zeros(len(days))
    cnt = np.zeros(len(days))
    for sym, (dn, cl) in closes.items():
        s = pd.Series(np.asarray(cl, float), index=np.asarray(dn))
        today = s.reindex(days)
        prev = s.reindex(days - 1)
        ret = today.to_numpy() / prev.to_numpy() - 1
        ok = np.isfinite(ret) & (days >= starts.get(sym, 0))
        acc[ok] += ret[ok]
        cnt[ok] += 1
    use = good & (cnt > 0)
    if not use.any():
        return dict(mean=float("nan"), days=0)
    return dict(mean=float((acc[use] / cnt[use]).mean()), days=int(use.sum()))


def strategy_daily(trades):
    """Mean net fractional return per position-day, trades pooled: each trade contributes net_ret / hold_days for each of its
    hold_days, so the pooled mean is sum(net_ret) / sum(hold_days)."""
    hd = trades.hold_days.to_numpy(float)
    return dict(mean=float(trades.net_ret.sum() / hd.sum()) if hd.sum() > 0 else float("nan"), position_days=float(hd.sum()))


# ------------------------------------------------------------------ top-coin removal and tables
def top_coin_removal(df):
    """VAL mean net R after removing each coin in turn."""
    out = {}
    for c in sorted(df.coin.unique()):
        rest = df[df.coin != c]
        out[c] = float(rest.R.mean()) if len(rest) else float("nan")
    ok = all((v > 0) for v in out.values() if v == v) and len(out) > 0
    worst = min(out, key=lambda k: out[k]) if out else None
    return dict(by_coin=out, all_positive=bool(ok), worst_coin=worst, worst_mean=out[worst] if worst else float("nan"))


def group_table(df, col):
    g = df.groupby(col).R.agg(["count", "mean", "std"])
    g["gross_R"] = (df.gross / df.risk).groupby(df[col]).mean()
    return g.reset_index()


def with_year(df):
    d = df.copy()
    d["year"] = d.entry_utc.str[:4]
    return d


def fmt_table(t):
    t = t.copy()
    for c in t.columns:
        if t[c].dtype.kind == "f":
            t[c] = t[c].map(lambda x: f"{x:.3f}")
    cols = list(t.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in t.iterrows():
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(lines)


# ------------------------------------------------------------------ verdict assembly
def verdict(trades, coins, table, closes, starts, n_boot=N_BOOT, n_draw=N_PLACEBO):
    """All seven bars on the fresh non-bear trade list `trades` (frame with the trades.csv columns). Returns the summary dict."""
    ride = trades[trades.kind == "RIDE"]
    t3r = trades[trades.kind == "T3R"]
    vr, dr = ride[ride.split == "VAL"], ride[ride.split == "DEV"]
    vt = t3r[t3r.split == "VAL"]
    s = dict(counts=dict(dev=int(len(dr)), val=int(len(vr)), val_weeks=int(vr.entry_week.nunique()), dev_weeks=int(dr.entry_week.nunique()),
                         t3r_val=int(len(vt))))
    s["bar1_power"] = bool(len(vr) >= 30 and vr.entry_week.nunique() >= 20)
    s["val_boot"] = week_bootstrap(vr.R, vr.entry_week, n_boot)
    s["bar2"] = bool(len(vr) > 0 and vr.R.mean() > 0 and s["val_boot"]["lo"] > 0)
    s["dev_mean_R"] = float(dr.R.mean()) if len(dr) else float("nan")
    s["bar3"] = bool(len(dr) > 0 and dr.R.mean() > 0)
    if len(vr):
        pl = placebo_draws(coins, vr[["coin", "risk"]], n_draw)
        s["placebo"] = placebo_verdict(vr.R.mean(), pl["means"])
        s["placebo"]["dropped_matches"] = pl["dropped"]
    else:
        s["placebo"] = dict(beats=False)
    s["bar4"] = bool(s["placebo"]["beats"])
    s["ex_best5_t3r"] = ex_best_weeks(vt.R, vt.entry_week, 5)
    s["ex_best5_ride"] = ex_best_weeks(vr.R, vr.entry_week, 5)
    s["bar5"] = bool(s["ex_best5_t3r"]["mean"] > 0)
    lo = int(C.VAL_START_DAY)
    hi = int(max(max(dn) for dn, _ in closes.values()))
    s["strategy_daily_val"] = strategy_daily(vr)
    s["basket_daily_val"] = basket_daily(closes, starts, table, lo, hi)
    s["bar6"] = bool(s["strategy_daily_val"]["mean"] >= s["basket_daily_val"]["mean"])
    s["top_coin_removal"] = top_coin_removal(vr)
    s["bar7"] = bool(s["top_coin_removal"]["all_positive"])
    s["fragile"] = not s["bar7"]
    bars = [s["bar2"], s["bar3"], s["bar4"], s["bar5"], s["bar6"], s["bar7"]]
    s["verdict"] = "UNDERPOWERED" if not s["bar1_power"] else ("PASS" if all(bars) else "FAIL")
    s["kill"] = bool(s["bar1_power"] and (not (len(vr) and vr.R.mean() > 0) or not (s["ex_best5_t3r"]["mean"] > 0) or
                                          (len(vr) >= 60 and not s["bar4"])))
    s["prediction_confirmed"] = bool(len(vr) and vr.R.mean() > 0 and len(vt) and vt.R.mean() < vr.R.mean())
    return s


def build_tables(trades, control, old20):
    parts = []
    ride = trades[trades.kind == "RIDE"]
    for name, d in (("fresh RIDE", ride), ("fresh T3R", trades[trades.kind == "T3R"])):
        for sp in ("DEV", "VAL"):
            dd = with_year(d[d.split == sp])
            parts.append(f"## {name} {sp} by year\n\n" + fmt_table(group_table(dd, "year")))
        parts.append(f"## {name} VAL by coin\n\n" + fmt_table(group_table(d[d.split == 'VAL'], "coin")))
        parts.append(f"## {name} VAL by miner phase\n\n" + fmt_table(group_table(d[d.split == 'VAL'], "phase")))
        parts.append(f"## {name} VAL by brain label\n\n" + fmt_table(group_table(d[d.split == 'VAL'].assign(brain_label=lambda x: x.brain_label.replace('', 'NA')), "brain_label")))
    for name, d in (("control DOWN", control), ("old-20", old20)):
        if d is not None and len(d):
            d = d[d.kind == "RIDE"]
            parts.append(f"## {name} RIDE by split\n\n" + fmt_table(group_table(d, "split")))
    return "\n\n".join(parts) + "\n"


def load_closes(wave, syms):
    closes, starts = {}, {}
    for s in syms:
        p = os.path.join(wave, "spot_1d", f"{s}USDT.csv")
        pf = os.path.join(wave, "funding", f"{s}USDT.csv")
        if not (os.path.isfile(p) and os.path.isfile(pf)):
            continue
        d1 = C.load_bars(p, "1d")
        fts, _ = C.load_funding(pf)
        closes[s] = (d1["ts"] // C.DAY, d1["c"])
        starts[s] = max(C.START_DAY, int(fts[0] // C.DAY) + (1 if fts[0] % C.DAY else 0)) if len(fts) else 10 ** 9
    return closes, starts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="required: step C runs only after the step B audit is clean")
    ap.add_argument("--wave", default=r"F:\MTS\data_cache\binance\wave2-1114")
    ap.add_argument("--miner", default=r"F:\MTS\data_cache\binance\combo-edge-miner-1114")
    ap.add_argument("--dir", default=HERE)
    a = ap.parse_args()
    if not a.run:
        print("refusing to run: pass --run once the step B audit is clean")
        return 2
    C.lower_priority()
    tr = pd.read_csv(os.path.join(a.dir, "trades.csv"))
    ctl = pd.read_csv(os.path.join(a.dir, "trades_control.csv"))
    p20 = os.path.join(a.dir, "trades_old20.csv")
    old = pd.read_csv(p20) if os.path.isfile(p20) else None
    btc = C.load_bars(os.path.join(a.miner, "spot_1d", "BTCUSDT.csv"), "1d")
    table = C.phase_table(btc["ts"], btc["c"])
    coins = {}
    for s in sorted(tr.coin.unique()):
        D4 = C.load_bars(os.path.join(a.wave, "spot_4h", f"{s}USDT.csv"), "4h")
        d1 = C.load_bars(os.path.join(a.wave, "spot_1d", f"{s}USDT.csv"), "1d")
        fund = C.load_funding(os.path.join(a.wave, "funding", f"{s}USDT.csv"))
        coins[s] = C.build_coin(s, D4, d1, fund, table)
    kept = sorted(json.load(open(os.path.join(a.dir, "coverage.json"), encoding="utf-8"))["fresh_kept"])
    closes, starts = load_closes(a.wave, kept)
    s = verdict(tr, coins, table, closes, starts)
    with open(os.path.join(a.dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(a.dir, "tables.md"), "w", encoding="utf-8") as f:
        f.write(build_tables(tr, ctl, old))
    print("verdict", s["verdict"], "counts", s["counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
