"""T05 eh-h4-speed-time-at-level: speed-in x time-at-level at prior-day high/low touches (research only).

Rules: see PRE_REG.md (frozen). Stages:
  python speed_time.py count       DEV touches, speed cut-off, regime mix. No returns.
  python speed_time.py dev         DEV returns, DEV screen, exploratory 2x2. Writes dev_passed.json in the cache.
  python speed_time.py validation  ONE read of 2024-07-01..2025-06-30, only if dev_passed.json says so.
Cache (outside the repo): F:/MTS/Dumps/backtest/eh-h4-speed-time-at-level (else %TEMP%/mts_eh_cache/...).
"""
import bisect
import datetime as dt
import importlib.util
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BT = HERE.parents[3] / "backtest"          # MyTradingSys/backtest (read-only imports)
SLUG = "eh-h4-speed-time-at-level"
_F = Path("F:/MTS/Dumps/backtest") / SLUG
CACHE = _F if Path("F:/MTS").exists() else Path(tempfile.gettempdir()) / "mts_eh_cache" / SLUG

BAR = 900000                 # 15 min in ms
DAY_MS = 86400000
BARS_PER_DAY = 96


def _ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


DEV_START_MS = _ms("2020-01-01")   # archive has no BTCUSDT 15m before 2020-01 (404, checked 2026-11-09)
DEV_END_MS = _ms("2024-07-01")     # exclusive: last DEV bar 2024-06-30 23:45
VAL_END_MS = _ms("2025-07-01")     # exclusive: last VALIDATION bar 2025-06-30 23:45
HOLDOUT_MS = VAL_END_MS            # HOLDOUT starts here and is never loaded
WARM_MS = 2 * DAY_MS               # VALIDATION loads 2 warm-up days (DEV bars) for prior-day levels only
WINDOWS = {"DEV": (DEV_START_MS, DEV_END_MS), "VALIDATION": (DEV_END_MS, VAL_END_MS)}

COST_RT = 0.0012                   # regime A taker 5 bps per side (fees.py DERIBIT_TAKER) + 2 bps RT slippage
TIME_BARS = 96
FAST_CUT = 0.08679781992469922                    # PENDING: DEV 66.67th percentile of touch speed, set by the count stage
Z_MDE = 1.959963984540054 + 0.841621233572914   # 97.5 % + 80 % power
ALPHA = 0.05
M_HOLM = 15


class SplitViolation(ValueError):
    pass


def guard_bars(ts, window):
    """Refuse any bar at or after the window's end. HOLDOUT is never loaded."""
    if window == "HOLDOUT" or window not in WINDOWS:
        raise SplitViolation(f"window {window!r} is not loadable (HOLDOUT is sealed)")
    hi = WINDOWS[window][1]
    if len(ts) and int(np.max(ts)) >= hi:
        raise SplitViolation(f"{window}: bar at {int(np.max(ts))} at or after window end {hi}")
    return True


def speed_in(c, t):
    """abs(close[t-1] - close[t-13]) / close[t-13] / 12, in % per bar."""
    base = c[t - 13]
    return abs(c[t - 1] - base) / base / 12.0 * 100.0


def contiguous_breaks(ts):
    return np.concatenate(([0], np.cumsum(np.diff(ts) != BAR)))


def day_index(ts, brk):
    days = ts // DAY_MS
    uniq, first, counts = np.unique(days, return_index=True, return_counts=True)
    info = {}
    for d, f, n in zip(uniq, first, counts):
        f, n = int(f), int(n)
        full = n == BARS_PER_DAY and (brk[f + BARS_PER_DAY - 1] - brk[f] == 0)
        info[int(d)] = (f, n, full)
    return info


def find_touches(ts, h, l, c):
    """One touch per UTC day: the first 15m bar beyond the prior-day high or low (OURS: one per day)."""
    ts = np.asarray(ts, dtype=np.int64)
    h, l, c = np.asarray(h, dtype=float), np.asarray(l, dtype=float), np.asarray(c, dtype=float)
    brk = contiguous_breaks(ts)
    info = day_index(ts, brk)
    stats = {"no_prior_day": 0, "no_break": 0, "both_sides": 0, "gap": 0, "lookback_outside": 0}
    out = []
    for d in sorted(info):
        f, n, full = info[d]
        if not full:
            continue
        if (d - 1) not in info or not info[d - 1][2]:
            stats["no_prior_day"] += 1
            continue
        ps = info[d - 1][0]
        pdh = h[ps:ps + BARS_PER_DAY].max()
        pdl = l[ps:ps + BARS_PER_DAY].min()
        sh, sl = h[f:f + BARS_PER_DAY], l[f:f + BARS_PER_DAY]
        mask = (sh > pdh) | (sl < pdl)
        if not mask.any():
            stats["no_break"] += 1
            continue
        k = int(np.argmax(mask))
        i = f + k
        if sh[k] > pdh and sl[k] < pdl:
            stats["both_sides"] += 1
            continue
        if i - 13 < 0 or brk[i] - brk[i - 13] != 0:
            stats["gap"] += 1
            continue
        if not (pdl < c[i - 12] < pdh):
            stats["lookback_outside"] += 1
            continue
        side = "high" if sh[k] > pdh else "low"
        out.append({"t": int(i), "day": int(d), "side": side,
                    "level": float(pdh if side == "high" else pdl),
                    "pdh": float(pdh), "pdl": float(pdl),
                    "speed": float(speed_in(c, i)), "ts": int(ts[i])})
    return out, stats


def reclaim_bar(c, t, pdh, pdl):
    """First bar r in t..t+3 whose close is strictly back inside (pdl, pdh); k = 0 allowed."""
    for j in range(t, min(t + 4, len(c))):
        if pdl < c[j] < pdh:
            return j
    return None


def time_at_level(c, level, t, r):
    """Bars j in t..r whose close is within 0.2 % of the level."""
    seg = np.asarray(c[t:r + 1], dtype=float)
    return int(np.sum(np.abs(seg - level) / level <= 0.002))


def fee_r(stop_frac):
    """Round-trip cost (12 bps) over the stop distance."""
    return COST_RT / stop_frac


def simulate_trade(ts, h, l, c, fund_ts, fund_rate, t, r, side, level):
    """Entry at close[r] (taker). side 'high' = fade short at PDH; 'low' = fade long at PDL.
    Stop = extreme over t..r; target 2R; time stop = close of r + 96. Stop wins a same-bar tie.
    Returns None when the window ends before r + 96 (censored)."""
    if r + TIME_BARS >= len(c):
        return None
    entry = float(c[r])
    short = side == "high"
    if short:
        stop = float(np.max(h[t:r + 1]))
        R = stop - entry
        target = entry - 2 * R
        cont = level + R
        adv, fav = h, l
    else:
        stop = float(np.min(l[t:r + 1]))
        R = entry - stop
        target = entry + 2 * R
        cont = level - R
        adv, fav = l, h
    if R <= 0:
        return None
    a = adv[r + 1:r + TIME_BARS + 1]
    f = fav[r + 1:r + TIME_BARS + 1]
    if short:
        adv_hit, fav_hit, cont_hit = a >= stop, f <= target, a >= cont
    else:
        adv_hit, fav_hit, cont_hit = a <= stop, f >= target, a <= cont
    i_adv = int(np.argmax(adv_hit)) if adv_hit.any() else None
    i_fav = int(np.argmax(fav_hit)) if fav_hit.any() else None
    i_cont = int(np.argmax(cont_hit)) if cont_hit.any() else None
    if i_adv is not None and (i_fav is None or i_adv <= i_fav):
        outcome, gross, exit_idx = "stop", -1.0, r + 1 + i_adv
    elif i_fav is not None:
        outcome, gross, exit_idx = "target", 2.0, r + 1 + i_fav
    else:
        exit_idx = r + TIME_BARS
        cx = float(c[exit_idx])
        gross = (entry - cx) / R if short else (cx - entry) / R
        outcome = "time"
    cont_flag = i_cont is not None and (i_fav is None or i_cont < i_fav)
    stop_frac = R / entry
    fr = fee_r(stop_frac)
    exit_ts = int(ts[exit_idx])
    fund_cost_frac = 0.0
    if fund_ts is not None and len(fund_ts):
        m = (fund_ts > ts[r]) & (fund_ts <= exit_ts)
        sign_long = -1.0 if short else 1.0       # longs pay positive funding; shorts receive it
        fund_cost_frac = sign_long * float(np.sum(fund_rate[m]))
    fcr = fund_cost_frac / stop_frac
    return {"outcome": outcome, "gross_r": gross, "fee_r": fr, "funding_cost_r": fcr,
            "net_r": gross - fr - fcr, "entry": entry, "stop": stop, "target": target, "R": R,
            "stop_frac": stop_frac, "exit_index": int(exit_idx), "exit_ts": exit_ts,
            "cont": bool(cont_flag), "side": side}


def htf_closed_asof(t_close, vals, t):
    """Value of the last higher-TF bar whose close time <= t; None before the first close."""
    k = int(np.searchsorted(np.asarray(t_close), t, side="right")) - 1
    if k < 0:
        return None
    return float(np.asarray(vals)[k])


def cluster_mean_se(x, day):
    """Mean and SE clustered by day: sqrt(sum_g (sum_{i in g}(x_i - mean))^2) / N."""
    x = np.asarray(x, dtype=float)
    day = np.asarray(day)
    N = len(x)
    mean = float(x.mean())
    resid = {}
    for xi, di in zip(x, day):
        resid[di] = resid.get(di, 0.0) + (xi - mean)
    se = math.sqrt(sum(v * v for v in resid.values())) / N
    return mean, se


def stats(x, day):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return {"n": 0}
    mean, se = cluster_mean_se(x, day)
    p_one = 1.0 - 0.5 * (1.0 + math.erf((mean / se) / math.sqrt(2))) if se > 0 else float("nan")
    return {"n": n, "mean": mean, "se": se, "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se,
            "mde80": Z_MDE * se, "p_one": p_one}


# ---------- data ----------

def _months(lo, hi):
    d0 = dt.datetime.fromtimestamp(lo / 1000, dt.timezone.utc)
    d1 = dt.datetime.fromtimestamp((hi - 1) / 1000, dt.timezone.utc)
    y, m = d0.year, d0.month
    out = []
    while (y, m) <= (d1.year, d1.month):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def load_bars(window):
    lo, hi = WINDOWS[window]
    if window == "VALIDATION":
        lo = lo - WARM_MS
    months = _months(lo, hi)
    arrs, frs = [], []
    for mo in months:
        p = CACHE / "klines" / f"BTCUSDT-15m-{mo}.csv"
        arrs.append(np.genfromtxt(p, delimiter=",", usecols=(0, 1, 2, 3, 4), ndmin=2))
        q = CACHE / "fundingRate" / f"BTCUSDT-fundingRate-{mo}.csv"
        frs.append(np.genfromtxt(q, delimiter=",", usecols=(0, 2), ndmin=2))
    raw = np.concatenate(arrs); raw = raw[np.isfinite(raw[:, 0])]
    guard_bars(raw[:, 0].astype(np.int64), window)
    order = np.argsort(raw[:, 0])
    raw = raw[order]
    m = (raw[:, 0] >= lo) & (raw[:, 0] < hi)
    raw = raw[m]
    ts = raw[:, 0].astype(np.int64)
    fr = np.concatenate(frs); fr = fr[np.isfinite(fr[:, 0])]
    fr = fr[np.argsort(fr[:, 0])]
    fm = (fr[:, 0] >= lo) & (fr[:, 0] < hi)
    return {"ts": ts, "o": raw[:, 1], "h": raw[:, 2], "l": raw[:, 3], "c": raw[:, 4],
            "f_ts": fr[fm, 0].astype(np.int64), "f_rate": fr[fm, 1]}


def build_events(D, window):
    """Touches in the window; reclaim; trade (returns) only when called from the dev/validation stage."""
    lo, hi = WINDOWS[window]
    ts, h, l, c = D["ts"], D["h"], D["l"], D["c"]
    touches, tstats = find_touches(ts, h, l, c)
    touches = [t for t in touches if lo <= t["day"] * DAY_MS < hi]
    brk = contiguous_breaks(ts)
    return touches, tstats, brk


def run_trades(D, touches, brk, want_trades):
    ts, h, l, c = D["ts"], D["h"], D["l"], D["c"]
    rows, cens = [], {"no_reclaim": 0, "censored": 0, "gap": 0}
    for tc in touches:
        t, lev = tc["t"], tc["level"]
        r = reclaim_bar(c, t, tc["pdh"], tc["pdl"])
        if r is None:
            cens["no_reclaim"] += 1
            continue
        tt = time_at_level(c, lev, t, r)
        td = time_at_level(c, lev, t, min(t + 7, len(c) - 1))
        if not want_trades:
            continue
        if brk[min(r + TIME_BARS, len(c) - 1)] - brk[r] != 0:
            cens["gap"] += 1
            continue
        sim = simulate_trade(ts, h, l, c, D["f_ts"], D["f_rate"], t, r, tc["side"], lev)
        if sim is None:
            cens["censored"] += 1
            continue
        row = {"day": tc["day"], "year": dt.datetime.fromtimestamp(tc["day"] * DAY_MS / 1000, dt.timezone.utc).year,
               "side": tc["side"], "speed": tc["speed"], "reclaim_k": r - t, "time_trade": tt, "time_desc": td}
        row.update(sim)
        rows.append(row)
    return rows, cens


def t05_mask(rows):
    fast = np.array([x["speed"] >= FAST_CUT for x in rows])
    rec = np.array([True for _ in rows])
    tt = np.array([x["time_trade"] <= 2 for x in rows])
    return fast & rec & tt


def regime_mix(D):
    """research_kit.regime_tag per Monday week in DEV. Weekly and monthly RSI14 on closed bars only."""
    sys.path.insert(0, str(HERE.parents[4]))
    spec = importlib.util.spec_from_file_location("rk_eh_h4", BT / "research_kit.py")
    rk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rk)
    ts, c = D["ts"], D["c"]
    brk = contiguous_breaks(ts)
    info = day_index(ts, brk)
    full_days = sorted(d for d in info if info[d][2])
    td = [(d + 1) * DAY_MS for d in full_days]
    cd = [float(c[info[d][0] + BARS_PER_DAY - 1]) for d in full_days]
    weeks = {}
    for d, cc in zip(full_days, cd):
        weeks.setdefault((d - 4) // 7, []).append((d, cc))
    wk_t, wk_c, wk_start = [], [], []
    for w in sorted(weeks):
        seq = weeks[w]
        if len(seq) < 7:
            continue
        wk_t.append((seq[-1][0] + 1) * DAY_MS)
        wk_c.append(seq[-1][1])
        wk_start.append((w * 7 + 4) * DAY_MS)
    wr = wilder_rsi(wk_c)
    mo = {}
    for d, cc in zip(full_days, cd):
        key = dt.datetime.fromtimestamp(d * DAY_MS / 1000, dt.timezone.utc).strftime("%Y-%m")
        mo[key] = (d, cc)
    mk = sorted(mo)
    mt, mc = [], []
    for key in mk:
        y, m = int(key[:4]), int(key[5:])
        nxt = _ms(f"{y + (m == 12)}-{1 if m == 12 else m + 1:02d}-01")
        if nxt <= DEV_END_MS:
            mt.append(nxt)
            mc.append(mo[key][1])
    mr = wilder_rsi(mc)
    wpair = [(t, v) for t, v in zip(wk_t, wr) if not math.isnan(v)]
    mpair = [(t, v) for t, v in zip(mt, mr) if not math.isnan(v)]
    tags = rk.weekly_regimes(wk_start, (td, cd), ([p[0] for p in wpair], [p[1] for p in wpair]),
                             ([p[0] for p in mpair], [p[1] for p in mpair]))
    return rk.regime_mix_line(tags)


def wilder_rsi(closes, n=14):
    closes = [float(x) for x in closes]
    out = [float("nan")] * len(closes)
    if len(closes) <= n:
        return out
    ch = np.diff(closes)
    gain = np.where(ch > 0, ch, 0.0)
    loss = np.where(ch < 0, -ch, 0.0)
    ag, al = gain[:n].mean(), loss[:n].mean()
    out[n] = 100.0 - 100.0 / (1.0 + (ag / al if al > 0 else np.inf))
    for i in range(n + 1, len(closes)):
        ag = (ag * (n - 1) + gain[i - 1]) / n
        al = (al * (n - 1) + loss[i - 1]) / n
        out[i] = 100.0 - 100.0 / (1.0 + (ag / al if al > 0 else np.inf))
    return out


# ---------- stages ----------

def stage_count():
    D = load_bars("DEV")
    touches, tstats, brk = build_events(D, "DEV")
    speeds = np.array([t["speed"] for t in touches])
    cut = float(np.percentile(speeds, 100 * 2 / 3))
    years = {}
    for t in touches:
        y = dt.datetime.fromtimestamp(t["day"] * DAY_MS / 1000, dt.timezone.utc).year
        years.setdefault(y, {"high": 0, "low": 0})[t["side"]] += 1
    rows, cens = run_trades(D, touches, brk, want_trades=False)   # reclaim counts only, no returns
    out = {"touches": len(touches), "touch_skips": tstats, "per_year": years,
           "reclaim_touches": len(touches) - cens["no_reclaim"], "fast_cut_pct": cut,
           "regime_mix_dev": regime_mix(D), "bars": int(len(D["ts"]))}
    CACHE.mkdir(parents=True, exist_ok=True)
    print(json.dumps(out, indent=1, default=str))
    return out


def stage_dev():
    D = load_bars("DEV")
    touches, tstats, brk = build_events(D, "DEV")
    rows, cens = run_trades(D, touches, brk, want_trades=True)
    t05 = [x for x, m in zip(rows, t05_mask(rows)) if m]
    s05 = stats([x["net_r"] for x in t05], [x["day"] for x in t05])
    passed = s05.get("n", 0) >= 30 and s05.get("mean", -1) > 0 and s05.get("ci_lo", -1) > 0
    cells = {}
    for x in rows:
        k = ("fast" if x["speed"] >= FAST_CUT else "slow") + "/" + ("time<=2" if x["time_desc"] <= 2 else "time>2")
        cells.setdefault(k, []).append(x)
    cell_out = {}
    for k, xs in sorted(cells.items()):
        cell_out[k] = {"n": len(xs),
                       "reversal_rate": float(np.mean([x["outcome"] == "target" for x in xs])),
                       "continuation_rate": float(np.mean([x["cont"] for x in xs])),
                       "mean_net_r": float(np.mean([x["net_r"] for x in xs]))}
    years = {}
    for y in sorted({x["year"] for x in t05}):
        ys = [x for x in t05 if x["year"] == y]
        years[y] = stats([x["net_r"] for x in ys], [x["day"] for x in ys]) if ys else {"n": 0}
    out = {"T05": s05, "T05_hit": float(np.mean([x["outcome"] == "target" for x in t05])) if t05 else None,
           "T05_mean_gross": float(np.mean([x["gross_r"] for x in t05])) if t05 else None,
           "T05_mean_fee_r": float(np.mean([x["fee_r"] for x in t05])) if t05 else None,
           "T05_mean_fund_r": float(np.mean([x["funding_cost_r"] for x in t05])) if t05 else None,
           "T05_per_year": years, "T05_cens": cens, "touch_skips": tstats, "touches": len(touches),
           "dev_passed": bool(passed), "exploratory_2x2": cell_out,
           "all_reclaim_trades": len(rows)}
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "dev_summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    (CACHE / "dev_passed.json").write_text(json.dumps({"dev_passed": bool(passed)}), encoding="utf-8")
    _write_trades(CACHE / "trades_DEV.csv", rows)
    print(json.dumps(out, indent=1, default=str))
    return out


def _write_trades(path, rows):
    keys = ["day", "year", "side", "speed", "reclaim_k", "time_trade", "time_desc", "outcome", "gross_r",
            "fee_r", "funding_cost_r", "net_r", "entry", "stop", "R", "cont"]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(",".join(keys) + "\n")
        for x in rows:
            fh.write(",".join(str(x[k]) for k in keys) + "\n")


def stage_validation():
    dp = CACHE / "dev_passed.json"
    if not dp.exists() or not json.loads(dp.read_text(encoding="utf-8"))["dev_passed"]:
        raise SystemExit("VALIDATION refused: DEV screen did not pass (no dev_passed.json)")
    done = CACHE / "validation_done.json"
    if done.exists():
        raise SystemExit("VALIDATION refused: already read once")
    D = load_bars("VALIDATION")
    touches, tstats, brk = build_events(D, "VALIDATION")
    rows, cens = run_trades(D, touches, brk, want_trades=True)
    t05 = [x for x, m in zip(rows, t05_mask(rows)) if m]
    s = stats([x["net_r"] for x in t05], [x["day"] for x in t05])
    holm_ok = s.get("p_one", 1.0) <= ALPHA / M_HOLM and s.get("mean", -1) > 0
    out = {"T05": s, "holm_threshold": ALPHA / M_HOLM, "pass": bool(holm_ok), "cens": cens}
    done.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    _write_trades(CACHE / "trades_VALIDATION.csv", rows)
    print(json.dumps(out, indent=1, default=str))
    return out


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "count":
        stage_count()
    elif stage == "dev":
        stage_dev()
    elif stage == "validation":
        stage_validation()
    else:
        raise SystemExit(__doc__)
