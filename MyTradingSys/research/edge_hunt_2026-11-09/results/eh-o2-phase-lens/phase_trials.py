"""T14 (1h level fade in the balance cell) and T15 (MLK-S1 4h RSI-40 long in ACCUMULATION/BULL, weekly zone MID/HIGH).

eh-o2-phase-lens, edge hunt 2026-11-09. Rules: PRE_REG.md (frozen before any return). Run:
  python phase_trials.py --count        events per year and side, regime mix, no returns
  python phase_trials.py --dev          DEV returns, cells.csv, phase_calendar.csv, dev_summary.json
  python phase_trials.py --validation   only for a trial that passed the DEV screen (read once)
Data cache outside the repo (MTS_EH_CACHE, default F:/MTS/Dumps/backtest/eh_o2_phase; spot from MTS_EH_SPOT).
"""
import argparse
import bisect
import csv
import glob
import inspect
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 5)))
for _p in (_ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from MyTradingSys.backtest import fees  # noqa: E402  (read-only)
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest.splits import SplitViolation, DEV_END, VALIDATION_END  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bull  # noqa: E402
import phase_label as pl  # noqa: E402

H1 = 3_600_000
H4 = 4 * H1
DAY = 86_400_000
DEV_END_MS = int(DEV_END.tz_localize("UTC").timestamp() * 1000)
VALIDATION_END_MS = int(VALIDATION_END.tz_localize("UTC").timestamp() * 1000)

# Regime A (SOURCED fees.py, FORMULAS.md s13): taker both legs + 2 bps round-trip slippage, fraction of entry notional.
COST_RT_A = 2 * fees.DERIBIT_TAKER + fees.SLIPPAGE_RT_S13

# T14 (OURS, brief): 12 bars back inside, reclaim within 3 bars, 2R, 24 bars.
T14_BACK, T14_RECLAIM, T14_TARGET_R, T14_MAX_BARS = 12, 3, 2.0, 24
# T15: Malkan defaults read from malkan_40_60 itself (D2 rule: the 40/60 numbers live only there); exit OURS.
_MSB = inspect.signature(malkan_setup_bull).parameters
T15_LEVEL, T15_TOL = _MSB["level"].default, _MSB["tolerance"].default
T15_TARGET_R, T15_MAX_BARS = 2.5, 30

CACHE = os.environ.get("MTS_EH_CACHE", "F:/MTS/Dumps/backtest/eh_o2_phase")
SPOT = os.environ.get("MTS_EH_SPOT", "F:/MTS/Dumps/backtest/spot_2017")


# ------------------------------------------------------------------ loaders (refuse HOLDOUT)
def _check_end(end):
    if end > VALIDATION_END_MS:
        raise SplitViolation(f"end {end} is past VALIDATION end {VALIDATION_END_MS}: HOLDOUT is never loaded")


def load_klines(folder, symbol, tf, end, start=0):
    """(t_open_ms, o, h, l, c) with start <= t < end. Refuses end past the VALIDATION end; never opens a later month."""
    _check_end(end)
    out = []
    for f in sorted(glob.glob(os.path.join(folder, f"{symbol}-{tf}-*.csv"))):
        m = re.search(r"-(\d{4})-(\d{2})(?:-\d{2})?\.csv$", f)
        if not m:
            continue
        mstart = int(datetime(int(m.group(1)), int(m.group(2)), 1, tzinfo=timezone.utc).timestamp() * 1000)
        if mstart >= end:
            continue
        with open(f, encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                if t > 10**14:  # spot archive switched to microseconds in 2025
                    t //= 1000
                if start <= t < end:
                    out.append((t, float(row[1]), float(row[2]), float(row[3]), float(row[4])))
    out.sort()
    ded = []
    for b in out:
        if not ded or ded[-1][0] != b[0]:
            ded.append(b)
    assert not ded or ded[-1][0] < end
    return ded


def load_funding(folder, symbol, end):
    _check_end(end)
    out = []
    for f in sorted(glob.glob(os.path.join(folder, f"{symbol}-fundingRate-*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                if t < end:
                    out.append((t, float(row[2])))
    out.sort()
    return out


def funding_sum(fund, t_in, t_out):
    """Sum of rates with t_in < calc_time <= t_out (FORMULAS.md:354-356)."""
    ts = [x[0] for x in fund] if not isinstance(fund, tuple) else fund[0]
    rs = [x[1] for x in fund] if not isinstance(fund, tuple) else fund[1]
    a = bisect.bisect_right(ts, t_in)
    b = bisect.bisect_right(ts, t_out)
    return float(sum(rs[a:b]))


# ------------------------------------------------------------------ R arithmetic and exits
def net_r(gross_r, side, entry, stop, funding_sum):
    stop_frac = abs(entry - stop) / entry
    fee_r = COST_RT_A / stop_frac
    funding_r = side * funding_sum / stop_frac
    return {"gross_r": gross_r, "fee_r": fee_r, "funding_r": funding_r, "net_r": gross_r - fee_r - funding_r,
            "stop_bps": stop_frac * 1e4}


def simulate_exit(bars, ei, side, entry, stop, target_r, max_bars):
    """Exit from bar ei+1 on: stop wins a same-bar tie, target touch, else the close of bar ei+max_bars.
    Returns None when the data ends before the trade is resolved (open trade dropped, counted)."""
    risk = abs(entry - stop)
    target = entry + side * target_r * risk
    for k in range(1, max_bars + 1):
        j = ei + k
        if j >= len(bars):
            return None
        _, o, h, lo, c = bars[j]
        hit_stop = lo <= stop if side > 0 else h >= stop
        hit_tgt = h >= target if side > 0 else lo <= target
        if hit_stop:
            return {"gross_r": -1.0, "exit_idx": j, "reason": "stop"}
        if hit_tgt:
            return {"gross_r": target_r, "exit_idx": j, "reason": "target"}
        if k == max_bars:
            return {"gross_r": side * (c - entry) / risk, "exit_idx": j, "reason": "time"}
    return None


# ------------------------------------------------------------------ T14 events
def t14_events(bars):
    """Sweep of the prior UTC day high (short) / low (long), first bar of the excursion (close before inside) with the
    close 12 bars earlier inside, closed back strictly inside within 3 bars (breach bar + 2). One event per level/day."""
    by_day = defaultdict(list)
    for i, b in enumerate(bars):
        by_day[(b[0] // DAY) * DAY].append(i)
    days = sorted(by_day)
    ev = []
    for d in days:
        prev = by_day.get(d - DAY)
        if not prev or len(prev) < 20:  # OURS: the prior day must be (nearly) complete
            continue
        H = max(bars[k][2] for k in prev)
        L = min(bars[k][3] for k in prev)
        done = {"PDH": False, "PDL": False}
        for i in by_day[d]:
            if i < T14_BACK:
                continue
            c12, c1 = bars[i - T14_BACK][4], bars[i - 1][4]
            if not (L <= c12 <= H and L <= c1 <= H):
                continue
            for lvl, side in (("PDH", -1), ("PDL", 1)):
                if done[lvl]:
                    continue
                beyond = bars[i][2] > H if side < 0 else bars[i][3] < L
                if not beyond:
                    continue
                for j in range(i, min(i + T14_RECLAIM, len(bars))):
                    if L < bars[j][4] < H:
                        ext = (max(bars[k][2] for k in range(i, j + 1)) if side < 0
                               else min(bars[k][3] for k in range(i, j + 1)))
                        ev.append({"idx": j, "t": bars[j][0], "side": side, "entry": bars[j][4], "stop": ext,
                                   "level": lvl, "day": d})
                        done[lvl] = True
                        break
    ev.sort(key=lambda e: (e["t"], e["level"]))
    return ev


# ------------------------------------------------------------------ T15 events
def _in_band(v):
    return v is not None and T15_LEVEL - T15_TOL <= v <= T15_LEVEL + T15_TOL


def swing_low_for_signal(bars, rsi, idx):
    """Lowest low from the first bar of the RSI band run before the signal through the signal bar (OURS)."""
    k = idx
    while k - 1 >= 0 and _in_band(rsi[k - 1]):
        k -= 1
    return min(b[3] for b in bars[k:idx + 1])


def t15_signals(bars, rsi):
    """MLK-S1 exactly as malkan_40_60 defines it (own-TF malkan_regime BULL, support at 40, green candle)."""
    regime = malkan_regime(rsi)
    dbars = [{"t": b[0], "o": b[1], "h": b[2], "l": b[3], "c": b[4]} for b in bars]
    pos = {b[0]: i for i, b in enumerate(bars)}
    out = []
    for s in malkan_setup_bull(dbars, rsi, regime):
        i = pos[s["t"]]
        out.append({"idx": i, "t": s["t"], "side": 1, "entry": bars[i][4], "stop": swing_low_for_signal(bars, rsi, i)})
    return out


# ------------------------------------------------------------------ cells and statistics
def in_balance(phase, zone):
    return zone == "MID" and phase not in ("PEAK_WINDOW", "BOTTOM_WINDOW") and phase is not None


def in_t15_cell(phase, zone):
    return phase in ("ACCUMULATION", "BULL") and zone in ("MID", "HIGH")


def stats(x, clusters):
    x = [float(v) for v in x]
    n = len(x)
    mean, se = rk.cluster_mean_se(x, clusters) if n else (float("nan"), float("nan"))
    ci_lo, ci_hi = mean - 1.96 * se, mean + 1.96 * se
    return {"n": n, "mean": mean, "se": se, "ci_lo": ci_lo, "ci_hi": ci_hi, "mde": rk.mde(se) if n else float("nan")}


def dev_screen(s):
    return bool(s["n"] >= 30 and s["mean"] > 0 and s["ci_lo"] > 0)


def verdict(dev, val):
    if val is not None and val.get("pass"):
        return "PASS"
    if dev["mean"] <= 0 and dev["ci_hi"] < dev["mde"]:
        return "FAIL"
    return "INCONCLUSIVE"


def _iso_week(t):
    y, w, _ = datetime.fromtimestamp(t / 1000, tz=timezone.utc).isocalendar()
    return y * 100 + w


def _year(t):
    return datetime.fromtimestamp(t / 1000, tz=timezone.utc).year


def _date(t):
    return datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


# ------------------------------------------------------------------ data assembly
def load_all(end):
    d = {}
    d["btc_1d"] = load_klines(os.path.join(SPOT, "BTCUSDT", "1d", "klines"), "BTCUSDT", "1d", end)
    d["eth_1d"] = load_klines(os.path.join(SPOT, "ETHUSDT", "1d", "klines"), "ETHUSDT", "1d", end)
    d["btc_4h"] = load_klines(os.path.join(SPOT, "BTCUSDT", "4h", "klines"), "BTCUSDT", "4h", end)
    d["eth_4h"] = load_klines(os.path.join(SPOT, "ETHUSDT", "4h", "klines"), "ETHUSDT", "4h", end)
    d["btc_1h_fut"] = load_klines(os.path.join(CACHE, "fut", "klines"), "BTCUSDT", "1h", end)
    d["fund_btc"] = load_funding(os.path.join(CACHE, "fut", "fundingRate"), "BTCUSDT", end)
    d["fund_eth"] = load_funding(os.path.join(CACHE, "fut", "fundingRate"), "ETHUSDT", end)
    return d


def build_trades(d, lo, hi, with_returns=True):
    """All T14 and T15 events with entry time in [lo, hi), labelled with PHASE_LABEL at the entry time."""
    btc_lab = pl.PhaseLabeler(d["btc_1d"])
    eth_lab = pl.PhaseLabeler(d["btc_1d"], weekly_daily=d["eth_1d"])
    trades, dropped = [], defaultdict(int)
    # T14
    bars = d["btc_1h_fut"]
    fund = ([x[0] for x in d["fund_btc"]], [x[1] for x in d["fund_btc"]])
    for e in t14_events(bars):
        t_in = e["t"] + H1
        if not lo <= t_in < hi:
            continue
        ph, z = btc_lab.label(t_in)
        rec = {"trial": "T14", "symbol": "BTCUSDT", "side": e["side"], "t_in": t_in, "level": e["level"],
               "phase": ph, "zone": z, "in_cell": in_balance(ph, z), "cluster": t_in // DAY, "year": _year(t_in)}
        if with_returns:
            x = simulate_exit(bars, e["idx"], e["side"], e["entry"], e["stop"], T14_TARGET_R, T14_MAX_BARS)
            if x is None:
                dropped["T14"] += 1
                continue
            t_out = bars[x["exit_idx"]][0] + H1
            rec.update(net_r(x["gross_r"], e["side"], e["entry"], e["stop"], funding_sum(fund, t_in, t_out)))
            rec["reason"] = x["reason"]
        trades.append(rec)
    # T15
    for sym, key, lab, fk in (("BTCUSDT", "btc_4h", btc_lab, "fund_btc"), ("ETHUSDT", "eth_4h", eth_lab, "fund_eth")):
        bars = d[key]
        fund = ([x[0] for x in d[fk]], [x[1] for x in d[fk]])
        rsi = rsi_core([b[4] for b in bars], 14)
        for e in t15_signals(bars, rsi):
            t_in = e["t"] + H4
            if not lo <= t_in < hi:
                continue
            if e["stop"] >= e["entry"]:
                dropped["T15_nostop"] += 1
                continue
            ph, z = lab.label(t_in)
            rec = {"trial": "T15", "symbol": sym, "side": 1, "t_in": t_in, "level": "RSI40", "phase": ph, "zone": z,
                   "in_cell": in_t15_cell(ph, z), "cluster": _iso_week(t_in), "year": _year(t_in)}
            if with_returns:
                x = simulate_exit(bars, e["idx"], 1, e["entry"], e["stop"], T15_TARGET_R, T15_MAX_BARS)
                if x is None:
                    dropped["T15"] += 1
                    continue
                t_out = bars[x["exit_idx"]][0] + H4
                rec.update(net_r(x["gross_r"], 1, e["entry"], e["stop"], funding_sum(fund, t_in, t_out)))
                rec["reason"] = x["reason"]
            trades.append(rec)
    return trades, dict(dropped)


def full_stats(rows):
    s = stats([r["net_r"] for r in rows], [r["cluster"] for r in rows])
    if rows:
        s["hit"] = sum(1 for r in rows if r["gross_r"] > 0) / len(rows)
        for k in ("gross_r", "fee_r", "funding_r"):
            s["mean_" + k] = sum(r[k] for r in rows) / len(rows)
        s["median_stop_bps"] = sorted(r["stop_bps"] for r in rows)[len(rows) // 2]
    return s


def regime_mix(d, lo, hi):
    daily = d["btc_1d"]
    dt = ([b[0] + DAY for b in daily], [b[4] for b in daily])
    w = pl.weekly_rsi(daily)
    m = pl.monthly_rsi(daily)
    weeks = []
    t = pl._week_start(lo) + (0 if pl._week_start(lo) >= lo else pl.WEEK_MS)
    while t < hi:
        weeks.append(t)
        t += pl.WEEK_MS
    return rk.regime_mix_line(rk.weekly_regimes(weeks, dt, w, m))


def phase_calendar(d, lo, hi):
    lab = pl.PhaseLabeler(d["btc_1d"])
    rows = []
    t = pl._week_start(lo) + pl.WEEK_MS
    while t < hi:
        ph, z = lab.label(t)
        rows.append((_date(t), ph, z))
        t += pl.WEEK_MS
    return rows


def _fmt(s):
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--count", action="store_true")
    g.add_argument("--dev", action="store_true")
    g.add_argument("--validation", nargs="+", help="trial ids that passed the DEV screen")
    a = ap.parse_args()
    if a.count or a.dev:
        d = load_all(DEV_END_MS)
        lo, hi = 0, DEV_END_MS
        trades, dropped = build_trades(d, lo, hi, with_returns=a.dev)
        print("Regime mix (DEV weeks, 2017-08-14..2024-06-30):", regime_mix(d, d["btc_1d"][0][0], DEV_END_MS))
        print("Regime mix (DEV weeks, T14 span 2020-01..2024-06):", regime_mix(d, d["btc_1h_fut"][0][0], DEV_END_MS))
        cnt = defaultdict(int)
        for r in trades:
            cnt[(r["trial"], r["year"], r["side"], r["in_cell"])] += 1
        print("count trial year side in_cell n")
        for k in sorted(cnt):
            print(*k, cnt[k])
        cells = defaultdict(int)
        for r in trades:
            cells[(r["trial"], r["phase"], r["zone"])] += 1
        for k in sorted(cells, key=str):
            print("cell", *k, cells[k])
        print("dropped", dropped)
        if a.count:
            return
        out = {"dropped": dropped}
        for tr in ("T14", "T15"):
            rows = [r for r in trades if r["trial"] == tr and r["in_cell"]]
            s = full_stats(rows)
            s["screen"] = dev_screen(s)
            s["verdict_if_no_val"] = verdict(s, None)
            s["per_year"] = {y: _fmt(full_stats([r for r in rows if r["year"] == y]))
                             for y in sorted({r["year"] for r in rows})}
            s["by_symbol"] = {sy: _fmt(full_stats([r for r in rows if r["symbol"] == sy]))
                              for sy in sorted({r["symbol"] for r in rows})}
            s["by_side"] = {str(sd): _fmt(full_stats([r for r in rows if r["side"] == sd]))
                            for sd in sorted({r["side"] for r in rows})}
            s["all_phases_pooled"] = _fmt(full_stats([r for r in trades if r["trial"] == tr]))
            out[tr] = _fmt(s)
        print(json.dumps(out, indent=1, default=str))
        with open(os.path.join(HERE, "cells.csv"), "w", newline="\n", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["trial", "phase", "zone", "confirmatory_cell", "n", "hit", "mean_gross_r", "mean_fee_r",
                        "mean_net_r", "se", "ci_lo", "ci_hi"])
            for tr in ("T14", "T15"):
                keys = sorted({(r["phase"] or "n/a", r["zone"] or "n/a") for r in trades if r["trial"] == tr})
                for ph, z in keys:
                    rows = [r for r in trades if r["trial"] == tr and (r["phase"] or "n/a") == ph
                            and (r["zone"] or "n/a") == z]
                    s = full_stats(rows)
                    conf = in_balance(ph, z) if tr == "T14" else in_t15_cell(ph, z)
                    w.writerow([tr, ph, z, conf, s["n"], round(s.get("hit", float("nan")), 3),
                                round(s.get("mean_gross_r", float("nan")), 4), round(s.get("mean_fee_r", float("nan")), 4),
                                round(s["mean"], 4), round(s["se"], 4), round(s["ci_lo"], 4), round(s["ci_hi"], 4)])
        with open(os.path.join(HERE, "phase_calendar.csv"), "w", newline="\n", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["week", "phase", "zone"])
            for row in phase_calendar(d, d["btc_1d"][0][0], DEV_END_MS):
                w.writerow([row[0], row[1], row[2] or "n/a"])
        with open(os.path.join(CACHE, "dev_summary.json"), "w", newline="\n") as f:
            json.dump(out, f, indent=1, default=str)
        return
    # VALIDATION: read once, only for trials passed on DEV
    d = load_all(VALIDATION_END_MS)
    trades, dropped = build_trades(d, DEV_END_MS, VALIDATION_END_MS)
    for tr in a.validation:
        rows = [r for r in trades if r["trial"] == tr and r["in_cell"]]
        s = full_stats(rows)
        z = s["mean"] / s["se"] if s["se"] and s["se"] > 0 else float("nan")
        p = 0.5 * math.erfc(z / math.sqrt(2)) if z == z else 1.0
        s["p_one_sided"] = p
        s["holm_bound_m15"] = min(1.0, 15 * p)
        s["pass"] = bool(s["mean"] > 0 and s["holm_bound_m15"] < 0.05)
        print(tr, json.dumps(_fmt(s)))


if __name__ == "__main__":
    main()
