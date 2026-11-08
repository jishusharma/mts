"""eh-h2-malkan-star-grades: Malkan 5-star (T03) and 7-star (T02) MTF RSI long grades, BTC+ETH daily.

Frozen rules: PRE_REG.md in this folder. Run:
  python star_grades.py dev                 # count + DEV screen (no VALIDATION read)
  python star_grades.py dev --validate      # VALIDATION read, only for trials that passed the DEV screen
Cache (outside the repo): F:/MTS/Dumps/backtest/eh-h2-spot (1d klines), eh-h2-fund (fundingRate).
Repo code read-only: layers/rsi/rsi_core.py (Wilder RSI14), layers/rsi/rsi_divergence.py, fees.py, research_kit.py.
"""
import bisect
import csv
import datetime as dt
import glob
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKTEST = HERE.parents[3] / "backtest"
sys.path.insert(0, str(BACKTEST / "layers" / "rsi"))
sys.path.insert(0, str(BACKTEST))
from rsi_core import rsi_core  # noqa: E402  (Wilder RSI, the only implementation per its header)
from rsi_divergence import rsi_divergence  # noqa: E402
import fees  # noqa: E402

SPOT = Path("F:/MTS/Dumps/backtest/eh-h2-spot")
FUND = Path("F:/MTS/Dumps/backtest/eh-h2-fund/fundingRate")
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

DAY = 86400000


def ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


DEV_LO = ms(2017, 8, 1)
SIGNAL_START = ms(2018, 10, 1)      # OURS: first 14 months after 2017-08 are monthly-RSI warm-up
DEV_END_EXCL = ms(2024, 7, 1)       # DEV = ..2024-06-30
VAL_START = DEV_END_EXCL
VAL_END_EXCL = ms(2025, 7, 1)       # VALIDATION = 2024-07-01..2025-06-30; HOLDOUT (2025-07-01+) refused
TIME_STOP_BARS = 40                 # OURS
COST_RT_BPS = 2 * fees.DERIBIT_TAKER * 1e4 + 2.0   # regime A: 10 bps taker round trip + 2 bps slippage
HOLM_M = 15                         # TRIALS.md, wave-wide


class SplitViolation(ValueError):
    pass


def check_window(rows, lo, hi_excl):
    """Raise SplitViolation if any row lies outside [lo, hi_excl)."""
    for r in rows:
        if r["t"] < lo or r["t"] >= hi_excl:
            raise SplitViolation(f"bar {r['t']} outside [{lo}, {hi_excl})")


def normalize_ms(x):
    """Binance archive has ms for older files and us for 2025 files."""
    x = int(float(x))
    return x // 1000 if x > 10 ** 14 else x


def load_daily(sym, data_end_excl):
    rows = []
    for p in sorted(glob.glob(str(SPOT / sym / "1d" / "klines" / f"{sym}-1d-*.csv"))):
        with open(p, newline="") as f:
            for rec in csv.reader(f):
                if not rec or not rec[0].strip().lstrip("-").isdigit():
                    continue
                rows.append({"t": normalize_ms(rec[0]), "o": float(rec[1]), "h": float(rec[2]),
                             "l": float(rec[3]), "c": float(rec[4])})
    rows.sort(key=lambda r: r["t"])
    dedup = {r["t"]: r for r in rows}
    rows = [dedup[k] for k in sorted(dedup)]
    check_window(rows, DEV_LO, VAL_END_EXCL)          # refuses anything at or after 2025-07-01
    return [r for r in rows if r["t"] < data_end_excl]


def load_funding(sym):
    rows = []
    for p in sorted(glob.glob(str(FUND / f"{sym}-fundingRate-*.csv"))):
        with open(p, newline="") as f:
            for rec in csv.DictReader(f):
                try:
                    rows.append({"t": normalize_ms(rec["calc_time"]), "rate": float(rec["last_funding_rate"])})
                except (KeyError, ValueError, TypeError):
                    continue
    rows.sort(key=lambda r: r["t"])
    check_window(rows, 0, VAL_END_EXCL)
    return [(r["t"], r["rate"]) for r in rows]


def resample(daily, kind):
    """Closed-bar resample in UTC. kind 'M' (calendar month) or 'W' (Monday 00:00 start)."""
    groups = {}
    for b in daily:
        d = dt.datetime.fromtimestamp(b["t"] / 1000, tz=dt.timezone.utc).date()
        if kind == "M":
            start = dt.date(d.year, d.month, 1)
            nxt = dt.date(d.year + (d.month == 12), 1 if d.month == 12 else d.month + 1, 1)
        else:
            start = d - dt.timedelta(days=d.weekday())
            nxt = start + dt.timedelta(days=7)
        key = start
        if key not in groups:
            groups[key] = {"t": ms(start.year, start.month, start.day), "o": b["o"], "h": b["h"],
                           "l": b["l"], "c": b["c"], "close_ms": ms(nxt.year, nxt.month, nxt.day)}
        g = groups[key]
        g["h"] = max(g["h"], b["h"])
        g["l"] = min(g["l"], b["l"])
        g["c"] = b["c"]
    return [groups[k] for k in sorted(groups)]


def usable(close_ms, day_open_ms):
    """A higher-TF bar is known at the close of daily bar `day_open_ms` iff it closed by that bar's close."""
    return close_ms <= day_open_ms + DAY


def last_usable(closes, vals, day_open_ms):
    """Latest higher-TF value (non-None) whose bar closed by the daily bar's close; None if none."""
    k = bisect.bisect_right(closes, day_open_ms + DAY) - 1
    while k >= 0:
        if vals[k] is not None:
            return vals[k]
        k -= 1
    return None


def fee_r(entry, stop):
    stop_bps = (entry - stop) / entry * 1e4
    return COST_RT_BPS / stop_bps


def funding_r(rates, t0, t1, entry, risk):
    """Long pays positive funding: sum of rates with t0 <= calc_time < t1, times entry, in R."""
    s = sum(r for t, r in rates if t0 <= t < t1)
    return s * entry / risk


def simulate_long(bars, entry_idx, stop, target, max_bars=TIME_STOP_BARS):
    """Enter at bars[entry_idx].open. Stop wins a same-bar tie. Stop/target fills: stop-market gap at the open
    if the open is through it, limit gap at the open if the open is past it. Time stop: close of the max_bars-th bar.
    Returns (exit_idx, exit_price, reason, gross_R); reason 'censored' if data ends before any exit."""
    entry = bars[entry_idx]["o"]
    risk = entry - stop
    last = min(entry_idx + max_bars - 1, len(bars) - 1)
    for k in range(entry_idx, last + 1):
        b = bars[k]
        if b["l"] <= stop:
            px, why = min(b["o"], stop), "stop"
        elif b["h"] >= target:
            px, why = max(b["o"], target), "target"
        elif k == entry_idx + max_bars - 1:
            px, why = b["c"], "time"
        else:
            continue
        return k, px, why, (px - entry) / risk
    if last == entry_idx + max_bars - 1:
        return last, bars[last]["c"], "time", (bars[last]["c"] - entry) / risk
    return None, None, "censored", None


def bullish_divergences(close, rsi, ts):
    """Malkan regular bullish divergence, close to close, 3-10 bars (malkan_divergence_default.json)."""
    return rsi_divergence(close=close, rsi=rsi, ts=ts, min_bars=3, max_bars=10, kind="bullish")


def reverse_divergences(close, rsi, ts, kind):
    """Exploratory only: PRD/NRD, 5-50 bars (GbXnw_tNMtw:456-465), repo reverse path (levels 60/40)."""
    return rsi_divergence(close=close, rsi=rsi, ts=ts, min_bars=5, max_bars=50, kind=kind)


def span_low(low, a, i):
    return min(low[a:i + 1])


def is_green(bars, i):
    """OURS: close > open AND close > prior close."""
    return i >= 1 and bars[i]["c"] > bars[i]["o"] and bars[i]["c"] > bars[i - 1]["c"]


def apply_overlap(sigs, exit_idx_of):
    """One trade at a time per symbol. exit_idx_of(i) simulates the trade for signal i and returns its exit bar
    index, or None when it is not a trade (invalid entry or censored). Signals with i < busy-until are skipped."""
    taken, skipped = [], 0
    busy = -1
    for i in sigs:
        if i < busy:
            skipped += 1
            continue
        ex = exit_idx_of(i)
        if ex is None:
            continue
        taken.append(i)
        busy = ex
    return taken, skipped


def cluster_mean_se(vals, keys):
    """Mean and cluster-robust SE (clusters = keys, e.g. ISO week)."""
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), 0
    mean = sum(vals) / n
    if n < 2:
        return mean, float("nan"), n
    groups = {}
    for v, k in zip(vals, keys):
        groups[k] = groups.get(k, 0.0) + (v - mean)
    se = math.sqrt(sum(g * g for g in groups.values())) / n
    return mean, se, n


def summarize(trades):
    net = [t["net"] for t in trades]
    keys = [t["week"] for t in trades]
    mean, se, n = cluster_mean_se(net, keys)
    out = {"n": n}
    if n == 0:
        return out
    out.update({
        "hit": sum(1 for x in net if x > 0) / n,
        "gross": sum(t["gross"] for t in trades) / n,
        "fee_r": sum(t["fee_r"] for t in trades) / n,
        "funding_r": sum(t["funding_r"] for t in trades) / n,
        "net": mean, "se": se,
    })
    if not math.isnan(se):
        out.update({"lo": mean - 1.96 * se, "hi": mean + 1.96 * se, "mde": 2.8 * se})
    return out


def dev_screen(s):
    return s.get("n", 0) >= 30 and s.get("net", -1) > 0 and s.get("lo", -1) > 0


def one_sided_p(s):
    z = s["net"] / s["se"]
    return 0.5 * math.erfc(z / math.sqrt(2))


def build_trades(sym, daily, fund, sig_lo, sig_hi, data_end):
    """Run T02 and T03 for one symbol on daily bars closed before data_end; signals with sig_lo <= t < sig_hi."""
    bars = [b for b in daily if b["t"] < data_end]
    close = [b["c"] for b in bars]
    low = [b["l"] for b in bars]
    ts = [b["t"] for b in bars]
    rsi_d = rsi_core(close)
    mon = resample(bars, "M")
    wk = resample(bars, "W")
    mon_rsi = rsi_core([m["c"] for m in mon])
    wk_rsi = rsi_core([w["c"] for w in wk])
    mon_close = [m["close_ms"] for m in mon]
    wk_close = [w["close_ms"] for w in wk]

    div_idx = {}
    for e in bullish_divergences(close, rsi_d, ts):
        div_idx.setdefault(e["i"], e)

    def hf(i):
        return last_usable(mon_close, mon_rsi, ts[i]), last_usable(wk_close, wk_rsi, ts[i])

    cands = {"T02": [], "T03": []}
    for i in range(len(bars)):
        if not (sig_lo <= ts[i] < sig_hi) or rsi_d[i] is None:
            continue
        mv, wv = hf(i)
        if mv is not None and mv >= 60 and rsi_d[i] < 40 and i in div_idx:
            cands["T02"].append(i)
        if mv is not None and wv is not None and mv > 60 and wv > 60 and 38 <= rsi_d[i] <= 42 and is_green(bars, i):
            cands["T03"].append(i)

    out = {}
    for trial, mult in (("T02", 4.0), ("T03", 2.0)):
        trades, counts = [], {"invalid": 0, "censored": 0}

        def sim(i, trial=trial, mult=mult):
            entry_i = i + 1
            if entry_i >= len(bars):
                counts["censored"] += 1
                return None
            entry = bars[entry_i]["o"]
            stop = span_low(low, div_idx[i]["a_i"], i) if trial == "T02" else bars[i]["l"]
            if stop >= entry:
                counts["invalid"] += 1
                return None
            target = entry + mult * (entry - stop)
            ex_i, ex_p, why, gross = simulate_long(bars, entry_i, stop, target)
            if why == "censored":
                counts["censored"] += 1
                return None
            fr = fee_r(entry, stop)
            fu = funding_r(fund, bars[entry_i]["t"], bars[ex_i]["t"] + DAY, entry, entry - stop)
            d = dt.datetime.fromtimestamp(bars[i]["t"] / 1000, tz=dt.timezone.utc).date()
            iso = d.isocalendar()
            trades.append({"date": d.isoformat(), "symbol": sym, "grade": trial, "gross": gross,
                           "fee_r": fr, "funding_r": fu, "net": gross - fr - fu, "why": why,
                           "week": f"{iso[0]}-W{iso[1]:02d}", "year": d.year,
                           "entry_date": dt.datetime.fromtimestamp(bars[entry_i]["t"] / 1000,
                                                                   tz=dt.timezone.utc).date().isoformat(),
                           "stop_bps": (entry - stop) / entry * 1e4})
            return ex_i

        taken, skipped = apply_overlap(sorted(cands[trial]), sim)
        out[trial] = {"trades": trades, "candidates": len(cands[trial]), "skipped_overlap": skipped,
                      "invalid": counts["invalid"], "censored": counts["censored"]}

    # Exploratory PRD/NRD event counts (no trial, no returns)
    expl = {}
    for kind in ("prd", "nrd"):
        evs = rsi_divergence(close=close, rsi=rsi_d, ts=ts, min_bars=5, max_bars=50, kind=kind)
        expl[kind] = [ts[e["i"]] for e in evs if sig_lo <= ts[e["i"]] < sig_hi]
    out["expl"] = expl

    # Weekly regime tags (research_kit.regime_tag) for DEV Mondays, BTC only
    regimes = []
    if RK is not None:
        daily_closes = [(t + DAY) for t in ts]
        for w in wk:
            if DEV_LO <= w["t"] < DEV_END_EXCL and w["t"] >= SIGNAL_START:
                try:
                    tag = regime_pure(w["t"], (daily_closes, close),
                                        (wk_close, wk_rsi), (mon_close, mon_rsi))["regime"]
                except Exception:
                    tag = None
                regimes.append(tag)
    out["regimes"] = regimes
    return out


try:
    sys.path.insert(0, str(BACKTEST))
    import research_kit as RK  # noqa: E402
except Exception as _e:  # pragma: no cover
    RK = None
    RK_ERROR = repr(_e)


def regime_pure(t, daily, weekly_rsi, monthly_rsi):
    """Same contract as research_kit.regime_tag (its _last_closed path returned None for every Monday in the
    count run, so the as-of lookups are redone here with the same pure helpers: ma_side, rsi_band, and
    last-closed-bar cutoff at t). Returns {'regime': bull|bear|range|None}."""
    td, cd = daily
    k = bisect.bisect_right(td, t)
    side = RK.ma_side(list(cd[:k]), RK.MA_N)
    band = RK.rsi_band(last_usable(weekly_rsi[0], weekly_rsi[1], t - DAY),
                       last_usable(monthly_rsi[0], monthly_rsi[1], t - DAY))
    if side is None or band is None:
        regime = None
    elif band == "bull" and side == "above":
        regime = "bull"
    elif band == "bear" and side == "below":
        regime = "bear"
    else:
        regime = "range"
    return {"regime": regime}


def main(argv):
    validate = "--validate" in argv
    end_dev = DEV_END_EXCL
    per_sym = {}
    for sym in SYMBOLS:
        daily = load_daily(sym, end_dev)
        fund = load_funding(sym)
        per_sym[sym] = build_trades(sym, daily, fund, SIGNAL_START, DEV_END_EXCL, end_dev)

    all_dev = {}
    print("DEV 2018-10-01..2024-06-30 (signals), data to 2024-06-30")
    for trial in ("T02", "T03"):
        trades = [t for sym in SYMBOLS for t in per_sym[sym][trial]["trades"]]
        trades.sort(key=lambda t: (t["date"], t["symbol"]))
        all_dev[trial] = trades
        cand = sum(per_sym[s][trial]["candidates"] for s in SYMBOLS)
        skip = sum(per_sym[s][trial]["skipped_overlap"] for s in SYMBOLS)
        inv = sum(per_sym[s][trial]["invalid"] for s in SYMBOLS)
        cen = sum(per_sym[s][trial]["censored"] for s in SYMBOLS)
        s = summarize(trades)
        print(f"{trial} candidates={cand} trades={len(trades)} overlap_skipped={skip} invalid={inv} censored={cen}")
        print(f"  summary {s}")
        print(f"  screen={'PASS' if dev_screen(s) else 'no'}")
        for y in sorted({t['year'] for t in trades}):
            ys = summarize([t for t in trades if t["year"] == y])
            print(f"  year {y}: n={ys['n']} net={ys.get('net', float('nan')):+.3f}")
        for sym in SYMBOLS:
            print(f"  {sym}: cand={per_sym[sym][trial]['candidates']} trades={len(per_sym[sym][trial]['trades'])}")
    for sym in SYMBOLS:
        for kind in ("prd", "nrd"):
            ev = per_sym[sym]["expl"][kind]
            yrs = (DEV_END_EXCL - SIGNAL_START) / (365.25 * DAY)
            print(f"EXPLORATORY {sym} {kind.upper()} events={len(ev)} per_year={len(ev) / yrs:.2f}")
    print("regime mix (BTC, DEV weeks):", end=" ")
    if RK is None:
        print("research_kit import failed:", RK_ERROR)
    else:
        print(RK.regime_mix_line(per_sym["BTCUSDT"]["regimes"]))

    with open(HERE / "events.csv", "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["date", "symbol", "grade", "R"])
        for trial in ("T02", "T03"):
            for t in all_dev[trial]:
                w.writerow([t["date"], t["symbol"], t["grade"], f"{t['net']:.4f}"])

    if validate:
        for trial in ("T02", "T03"):
            s = summarize(all_dev[trial])
            if not dev_screen(s):
                print(f"VALIDATION {trial}: not read (DEV screen not passed)")
                continue
            vdaily = {sym: load_daily(sym, VAL_END_EXCL) for sym in SYMBOLS}
            vt = []
            for sym in SYMBOLS:
                vt += build_trades(sym, vdaily[sym], load_funding(sym), VAL_START, VAL_END_EXCL,
                                   VAL_END_EXCL)[trial]["trades"]
            vs = summarize(vt)
            p = one_sided_p(vs) if vs.get("se") else float("nan")
            p_h = min(1.0, p * HOLM_M)
            print(f"VALIDATION {trial}: {vs} p={p:.4g} holm_m{HOLM_M}={p_h:.4g}")
            with open(HERE / "validation_once.txt", "a", newline="\n") as f:
                f.write(f"{trial} {vs} p={p:.6g} holm={p_h:.6g}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
