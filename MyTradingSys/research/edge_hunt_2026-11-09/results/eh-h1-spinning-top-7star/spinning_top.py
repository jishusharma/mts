"""eh-h1-spinning-top-7star (T01): Malkan's 7-star spinning top, coded literally. Rules: PRE_REG.md.

Stages (python spinning_top.py <stage>):
  count       events per TF / side / symbol / year on DEV (no returns) + DEV regime mix
  dev         DEV simulation, pooled T01 statistics, per-cell and per-year tables (exploratory cells)
  validation  VALIDATION read, run only if the DEV screen passed (guarded by --allow-validation)
Data: spot klines (eh_h1_spot) and USD-M fundingRate archive (eh_h1_fut), outside the repo.
"""
import csv
import json
import math
import os
import pathlib
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO_BACKTEST = HERE.parents[3] / "backtest"   # MyTradingSys/backtest (read-only imports)
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import fees  # noqa: E402  (single cost module; no own fee constant)

# ---- rule constants (PRE_REG.md) ----
BODY_K = 0.25          # OURS
SHADOW_K = 0.25        # OURS
VOL_MULT = 2.0         # OURS
VOL_WIN = 20           # OURS
LOC_WIN = 20           # OURS
TRIGGER_BARS = 3       # OURS
TICK = 0.01            # OURS (Binance spot tick)
TARGET_R = 3.0         # OURS
TIME_BARS = 20         # OURS
FEE_PER_SIDE = fees.DERIBIT_TAKER   # regime A, imported (DERIBIT_TAKER = BINANCE_TAKER = 0.0005)
RT_EXTRA_BPS = 2.0     # round-trip slippage allowance in bp, PLAN s5 / FORMULAS s13 (fees.py has no slippage constant)
FEE_RT_BPS = FEE_PER_SIDE * 2e4 + RT_EXTRA_BPS   # 12 bps round trip

# ---- splits (PRE_REG Data and splits) ----
DEV_END_MS = int(pd.Timestamp("2024-07-01", tz="UTC").timestamp() * 1000)
VAL_END_MS = int(pd.Timestamp("2025-07-01", tz="UTC").timestamp() * 1000)   # VALIDATION_END of splits.py (exclusive)
SPOT_START = "2017-08"
FUT_START = "2019-09"
SYMBOLS = ("BTCUSDT", "ETHUSDT")
TFS = {"4h": 4 * 3600 * 1000, "1d": 24 * 3600 * 1000}


class SplitViolation(ValueError):
    pass


def _cache_root():
    f = pathlib.Path("F:/MTS/Dumps/backtest")
    if f.exists():
        return f
    return pathlib.Path(tempfile.gettempdir()) / "mts_eh_cache"


def spot_root():
    return _cache_root() / "eh_h1_spot"


def fut_root():
    return _cache_root() / "eh_h1_fut"


# ---------- loaders with split refusal ----------

def check_window_end(end):
    """Refuse any end past the VALIDATION end (HOLDOUT is never loaded)."""
    t = pd.Timestamp(end)
    if t.tzinfo is not None:
        t = t.tz_convert(None)
    if t > pd.Timestamp("2025-07-01"):
        raise SplitViolation(f"end {end} is past the VALIDATION end 2025-07-01 (HOLDOUT is sealed)")


def read_monthly(root, symbol, tf, ym):
    p = pathlib.Path(root) / symbol / tf / "klines" / f"{symbol}-{tf}-{ym}.csv"
    if not p.exists():
        return pd.DataFrame(columns=["open_time", "open", "high", "low", "close", "volume", "close_time"])
    df = pd.read_csv(p, header=None, usecols=range(7),
                     names=["open_time", "open", "high", "low", "close", "volume", "close_time"])
    return df


def assert_bars_in_window(df, window):
    end = DEV_END_MS if window == "DEV" else VAL_END_MS
    if len(df) and int(df["close_time"].max()) >= end:
        raise SplitViolation(f"{window} load holds a bar closing at/after the window end")


def _months(start, end_ym):
    return [str(p) for p in pd.period_range(start, end_ym, freq="M")]


def load_bars(symbol, tf, window, root=None):
    """DEV: bars that close before 2024-07-01. VALIDATION: bars that close before 2025-07-01 (DEV bars are the
    warm-up for the 20-bar windows; the VALIDATION trades are taken from the window start only). HOLDOUT: refused."""
    if window not in ("DEV", "VALIDATION"):
        raise SplitViolation(f"window {window!r} is not loadable (HOLDOUT is sealed)")
    end_ms = DEV_END_MS if window == "DEV" else VAL_END_MS
    end_ym = "2024-06" if window == "DEV" else "2025-06"
    root = pathlib.Path(root) if root is not None else spot_root()
    parts = [read_monthly(root, symbol, tf, ym) for ym in _months(SPOT_START, end_ym)]
    df = pd.concat(parts, ignore_index=True).sort_values("open_time").drop_duplicates("open_time")
    df = df[df["close_time"] < end_ms].reset_index(drop=True)
    assert_bars_in_window(df, window)
    return df


def load_funding(symbol, window, root=None):
    end_ms = DEV_END_MS if window == "DEV" else VAL_END_MS
    root = pathlib.Path(root) if root is not None else fut_root()
    out_t, out_r = [], []
    for ym in _months(FUT_START, "2025-06"):
        p = root / "fundingRate" / f"{symbol}-fundingRate-{ym}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p)
        d = d[d["calc_time"] < end_ms]
        out_t.append(d["calc_time"].to_numpy(dtype=np.int64))
        out_r.append(d["last_funding_rate"].to_numpy(dtype=float))
    if not out_t:
        return np.array([], dtype=np.int64), np.array([], dtype=float)
    t = np.concatenate(out_t)
    r = np.concatenate(out_r)
    order = np.argsort(t)
    return t[order], r[order]


# ---------- rules ----------

def setup_flags(o, h, l, c, v):
    """Boolean arrays (long, short) per bar. Uses bars at or before i only."""
    o, h, l, c, v = (np.asarray(x, dtype=float) for x in (o, h, l, c, v))
    n = len(o)
    lf = np.zeros(n, dtype=bool)
    sf = np.zeros(n, dtype=bool)
    rng = h - l
    body = np.abs(c - o)
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    for i in range(max(VOL_WIN, LOC_WIN - 1), n):
        r = rng[i]
        if not (r > 0):
            continue
        small_body = body[i] <= BODY_K * r
        shadows = upper[i] >= SHADOW_K * r and lower[i] >= SHADOW_K * r
        if not (small_body and shadows):
            continue
        med = float(np.median(v[i - VOL_WIN:i]))
        if not (v[i] >= VOL_MULT * med):
            continue
        if l[i] <= np.min(l[i - LOC_WIN + 1:i + 1]):
            lf[i] = True
        if h[i] >= np.max(h[i - LOC_WIN + 1:i + 1]):
            sf[i] = True
    return lf, sf


def fee_r(stop_frac):
    """Round-trip cost (regime A + 2 bps slippage) in R: cost fraction of entry / stop fraction of entry."""
    return (FEE_RT_BPS / 1e4) / stop_frac


def funding_sum(ts, rates, a_ms, b_ms):
    """Sum of funding rates with calc_time in (a, b]."""
    if len(ts) == 0:
        return 0.0
    m = (ts > a_ms) & (ts <= b_ms)
    return float(np.sum(rates[m]))


def net_r(gross, stop_frac, fund_sum, side):
    side_sign = 1.0 if side == "long" else -1.0
    funding_r = side_sign * fund_sum / stop_frac
    return gross - fee_r(stop_frac) - funding_r


def simulate(o, h, l, c, v, t, lf, sf, bar_ms, funding=None, start=0, sym=""):
    """One position per symbol and TF. Long: buy stop above the setup high (live 3 bars); stop = setup low;
    target 3R; time stop 20 bars (fill bar included) at close. Short mirrored. Stop wins same-bar ties.
    Setups at a bar where both flags fire: long kept, short suppressed (counted)."""
    o, h, l, c, v = (np.asarray(x, dtype=float) for x in (o, h, l, c, v))
    n = len(o)
    trades = []
    cnt = {"flag_long": 0, "flag_short": 0, "unfilled": 0, "skipped_busy": 0, "both_side_suppressed": 0,
           "open_at_end": 0}
    ft, fr = funding if funding is not None else (np.array([], dtype=np.int64), np.array([], dtype=float))
    busy_until = -1
    for i in range(start, n - 1):
        if not (lf[i] or sf[i]):
            continue
        if lf[i]:
            cnt["flag_long"] += 1
        if sf[i]:
            cnt["flag_short"] += 1
        if i <= busy_until:
            cnt["skipped_busy"] += 1
            continue
        if lf[i] and sf[i]:
            cnt["both_side_suppressed"] += 1
        side = "long" if lf[i] else "short"
        if side == "long":
            trig = h[i] + TICK
            stop = l[i]
        else:
            trig = l[i] - TICK
            stop = h[i]
        j = None
        for k in range(i + 1, min(i + TRIGGER_BARS, n - 1) + 1):
            if side == "long" and h[k] >= trig:
                j = k
                fill = max(o[k], trig)
                break
            if side == "short" and l[k] <= trig:
                j = k
                fill = min(o[k], trig)
                break
        if j is None:
            cnt["unfilled"] += 1
            continue
        risk = abs(fill - stop)
        if not (risk > 0):
            continue
        target = fill + TARGET_R * risk if side == "long" else fill - TARGET_R * risk
        last_k = min(j + TIME_BARS - 1, n - 1)
        outcome = None
        exit_idx = None
        exit_px = None
        mfe = 0.0
        for k in range(j, last_k + 1):
            if side == "long":
                mfe = max(mfe, (h[k] - fill) / risk)
                if l[k] <= stop:
                    exit_idx, exit_px, outcome = k, min(o[k], stop), "stop"
                    break
                if h[k] >= target:
                    exit_idx, exit_px, outcome = k, max(o[k], target), "target"
                    break
            else:
                mfe = max(mfe, (fill - l[k]) / risk)
                if h[k] >= stop:
                    exit_idx, exit_px, outcome = k, max(o[k], stop), "stop"
                    break
                if l[k] <= target:
                    exit_idx, exit_px, outcome = k, min(o[k], target), "target"
                    break
        if outcome is None:
            if j + TIME_BARS - 1 <= n - 1:
                exit_idx, exit_px, outcome = j + TIME_BARS - 1, c[j + TIME_BARS - 1], "time"
            else:
                exit_idx, exit_px, outcome = n - 1, c[n - 1], "open_end"
                cnt["open_at_end"] += 1
        gross = (exit_px - fill) / risk if side == "long" else (fill - exit_px) / risk
        stop_frac = risk / fill
        fsum = funding_sum(ft, fr, int(t[j]), int(t[exit_idx]) + bar_ms)
        trades.append({
            "sym": sym, "side": side, "setup_idx": i, "fill_idx": j, "exit_idx": exit_idx,
            "t_setup": int(t[i]), "t_fill": int(t[j]), "t_exit": int(t[exit_idx]),
            "entry": float(fill), "stop": float(stop), "target": float(target), "outcome": outcome,
            "exit_price": float(exit_px), "gross_r": float(gross), "stop_frac": float(stop_frac),
            "fee_r": float(fee_r(stop_frac)), "funding_r": float((1.0 if side == "long" else -1.0) * fsum / stop_frac),
            "net_r": float(net_r(gross, stop_frac, fsum, side)), "mfe_r": float(mfe),
        })
        busy_until = exit_idx
    return trades, cnt


# ---------- statistics ----------

def _norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def cluster_stats(x, weeks):
    """Mean with week-clustered SE (small-G correction), 95 % CI, MDE at 80 % power, one-sided p for mean > 0."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float("nan"), "se": float("nan")}
    mean = float(x.mean())
    e = x - mean
    s = pd.Series(e).groupby(np.asarray(weeks)).sum().to_numpy()
    g = len(s)
    var = (g / (g - 1)) * float(np.sum(s * s)) / (n * n) if g > 1 else float(np.var(e, ddof=1)) / n
    se = math.sqrt(var)
    z = mean / se if se > 0 else float("nan")
    return {"n": n, "clusters": g, "mean": mean, "se": se, "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
            "mde80": 2.8 * se, "p_one_sided": _norm_sf(z) if se > 0 else float("nan"),
            "hit_rate": float(np.mean(np.asarray(x) > 0))}


def iso_week(t_ms):
    d = pd.to_datetime(np.asarray(t_ms, dtype="int64"), unit="ms")
    iso = d.isocalendar()
    return (iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)).to_numpy()


def trades_frame(trades):
    return pd.DataFrame(trades)


def stats_for(trades):
    if not trades:
        return {"n": 0}
    df = trades_frame(trades)
    st_ = cluster_stats(df["net_r"].to_numpy(), iso_week(df["t_fill"].to_numpy()))
    st_["mean_gross_r"] = float(df["gross_r"].mean())
    st_["mean_fee_r"] = float(df["fee_r"].mean())
    st_["mean_funding_r"] = float(df["funding_r"].mean())
    st_["share_mfe_ge_10r"] = float((df["mfe_r"] >= 10).mean())
    st_["outcomes"] = df["outcome"].value_counts().to_dict()
    return st_


def dev_screen(s):
    return s.get("n", 0) >= 30 and s.get("mean", -1) > 0 and s.get("ci_lo", -1) > 0


def verdict(dev, val=None):
    if val is not None and dev_screen(dev) and val.get("p_one_sided", 1) <= 0.05 / 15 and val.get("mean", -1) > 0:
        return "PASS"
    if dev.get("n", 0) > 0 and dev.get("mean", 1) <= 0 and dev.get("ci_hi", 0) < dev.get("mde80", 0):
        return "FAIL"
    return "INCONCLUSIVE"


# ---------- stages ----------

def _arrays(df):
    return (df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy(),
            df["volume"].to_numpy(), df["open_time"].to_numpy(dtype=np.int64))


def stage_count():
    rows = []
    for sym in SYMBOLS:
        for tf, bar_ms in TFS.items():
            df = load_bars(sym, tf, "DEV")
            o, h, l, c, v, t = _arrays(df)
            lf, sf = setup_flags(o, h, l, c, v)
            yrs = pd.to_datetime(t, unit="ms").year
            for side, flag in (("long", lf), ("short", sf)):
                for y in sorted(set(yrs)):
                    rows.append({"window": "DEV", "sym": sym, "tf": tf, "side": side, "year": int(y),
                                 "flags": int(np.sum(flag & (yrs == y)))})
    out = HERE / "counts.csv"
    with open(out, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    total = {}
    for r in rows:
        total[(r["tf"], r["side"])] = total.get((r["tf"], r["side"]), 0) + r["flags"]
    print("counts.csv written:", len(rows), "rows; totals by (tf, side):", total)
    print("Regime mix:", regime_mix_dev())
    return total


def _rsi14(closes):
    d = pd.Series(closes).diff()
    g = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    return (100 - 100 / (1 + g / l)).to_numpy()


def regime_mix_dev():
    """Weekly regime tags (research_kit.regime_tag, as-of each DEV week start) on BTCUSDT daily DEV bars."""
    sys.path.insert(0, str(HERE.parents[4]))
    sys.path.insert(0, str(REPO_BACKTEST))
    try:
        import research_kit as rk
    except Exception as e:  # noqa: BLE001
        return f"NOT_IN_DATA: research_kit import failed ({type(e).__name__}: {e})"
    d = load_bars("BTCUSDT", "1d", "DEV")
    ts = pd.to_datetime(d["open_time"], unit="ms")
    close = d["close"].astype(float).to_numpy()
    daily = (list(ts + pd.Timedelta(days=1)), list(close))
    wk = ts.dt.to_period("W-SUN")
    wk_close = pd.Series(close).groupby(wk.values).last()
    wk_start = [p.start_time for p in wk_close.index]
    wk_t = [s_ + pd.Timedelta(days=7) for s_ in wk_start]
    mo = ts.dt.to_period("M")
    mo_close = pd.Series(close).groupby(mo.values).last()
    mo_t = [p.end_time.normalize() + pd.Timedelta(days=1) for p in mo_close.index]
    weekly_rsi = (wk_t, list(_rsi14(wk_close.to_numpy())))
    monthly_rsi = (mo_t, list(_rsi14(mo_close.to_numpy())))
    starts = [s_ for s_ in wk_start if s_ >= ts.iloc[0] + pd.Timedelta(days=20)]
    try:
        tags = rk.weekly_regimes(starts, daily, weekly_rsi, monthly_rsi)
        return rk.regime_mix_line(tags)
    except Exception as e:  # noqa: BLE001
        return f"NOT_IN_DATA: research_kit.regime_tag failed ({type(e).__name__}: {e})"


def stage_run(window):
    all_trades = []
    cells = {}
    counters = {}
    for sym in SYMBOLS:
        fund = load_funding(sym, window)
        for tf, bar_ms in TFS.items():
            df = load_bars(sym, tf, window)
            o, h, l, c, v, t = _arrays(df)
            lf, sf = setup_flags(o, h, l, c, v)
            start = 0 if window == "DEV" else int(np.searchsorted(t, DEV_END_MS))
            tr, cnt = simulate(o, h, l, c, v, t, lf, sf, bar_ms, funding=fund, start=start, sym=sym)
            key = f"{sym}-{tf}"
            for x in tr:
                x["tf"] = tf
            cells[key] = tr
            counters[key] = cnt
            all_trades += tr
            print(key, "bars", len(df), "trades", len(tr), cnt)
    pooled = stats_for(all_trades)
    per_cell = {k: stats_for(v) for k, v in cells.items()}
    per_side = {s: stats_for([x for x in all_trades if x["side"] == s]) for s in ("long", "short")}
    per_tf = {tf: stats_for([x for x in all_trades if x["tf"] == tf]) for tf in TFS}
    years = {}
    if all_trades:
        yrs = pd.to_datetime(np.array([x["t_fill"] for x in all_trades]), unit="ms").year
        for y in sorted(set(yrs)):
            sub = [x for x, yy in zip(all_trades, yrs) if yy == y]
            years[int(y)] = {"n": len(sub), "mean_net_r": float(np.mean([x["net_r"] for x in sub]))}
    return all_trades, {"pooled": pooled, "per_cell": per_cell, "per_side": per_side, "per_tf": per_tf,
                        "per_year": years, "counters": counters}


def main(argv):
    stage = argv[1] if len(argv) > 1 else "count"
    if stage == "count":
        stage_count()
        return 0
    if stage == "dev":
        trades, summ = stage_run("DEV")
        print(json.dumps(summ, indent=1, default=str))
        cache = _cache_root() / "eh_h1_results"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "dev_trades.json").write_text(json.dumps(trades, default=str), encoding="utf-8")
        print("DEV screen:", dev_screen(summ["pooled"]), "verdict if no VALIDATION:", verdict(summ["pooled"]))
        return 0
    if stage == "validation":
        if "--allow-validation" not in argv:
            print("refused: VALIDATION is read only with --allow-validation after a DEV screen pass")
            return 2
        dev_trades, dev_summ = stage_run("DEV")
        if not dev_screen(dev_summ["pooled"]):
            print("DEV screen not passed; VALIDATION not read")
            return 3
        trades, summ = stage_run("VALIDATION")
        print(json.dumps(summ, indent=1, default=str))
        print("VERDICT:", verdict(dev_summ["pooled"], summ["pooled"]))
        return 0
    print("unknown stage", stage)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
