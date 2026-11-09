"""eh-s3-rsi-line-confluence: RSI14 40/60 line bounce with other-timeframe confluence (T11) and against the HTF bias (T12).

Frozen rules: PRE_REG.md in this folder. Run:
  python line_confluence.py count            # events per year and side, regime mix; no returns computed
  python line_confluence.py dev              # DEV returns (2017-10-01 signals .. 2024-06-30), cells.csv
  python line_confluence.py val              # DEV screen again, then ONE VALIDATION read for the trials that passed it
Data cache lives outside the repo: F:/MTS/Dumps/backtest/spot_2017 (spot 1h/4h klines), eh_s3_conf/fund (fundingRate).
Repo code is imported read-only: layers/rsi/rsi_core.py (Wilder RSI14), fees.py (taker), research_kit.py (ma_side, rsi_band,
regime_mix_line). Event logic is adapted from rsi_40_60_line_behaviour_2026-11-04/study.py (find_entries / classify, copied
in spirit, not imported: the study's band entry is both-sided and its outcome window differs).
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
from rsi_core import rsi_core  # noqa: E402  (Wilder RSI; the only implementation per its header)
import fees  # noqa: E402

SPOT_ROOT = "F:/MTS/Dumps/backtest/spot_2017"
FUND_DIR = "F:/MTS/Dumps/backtest/eh_s3_conf/fund/fundingRate"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
HOUR = 3600000
DAY = 24 * HOUR
TF_MS = {"1h": HOUR, "4h": 4 * HOUR, "12h": 12 * HOUR, "1d": DAY}
TFS = ("1h", "4h", "12h", "1d")
TRADE_TFS = ("1h", "4h")
HTF_OF = {"1h": "4h", "4h": "1d"}          # OURS (the study mapped 4h -> 12h)
LINES = (40, 60)                            # SOURCED Malkan lines
CUSHION = 2.0                               # OURS, fixed, RSI points
WINDOW = 6                                  # OURS, bars after the band entry
TARGET_R = 2.5                              # OURS
MAX_BARS = 48                               # OURS
STALE_BARS = 2                              # OURS: an as-of value older than 2 bar lengths is missing
HOLM_M = 15                                 # TRIALS.md, wave-wide


def ms(y, m, d, hh=0):
    return int(dt.datetime(y, m, d, hh, tzinfo=dt.timezone.utc).timestamp() * 1000)


DEV_LO = ms(2017, 8, 1)
SIGNAL_START = ms(2017, 10, 1)              # OURS: 1d RSI14 warm-up
DEV_END_EXCL = ms(2024, 7, 1)
VAL_START = DEV_END_EXCL
VAL_END_EXCL = ms(2025, 7, 1)               # HOLDOUT (2025-07-01+) is never loaded


class SplitViolation(ValueError):
    pass


def check_window(rows, lo, hi_excl):
    for r in rows:
        if r["t"] < lo or r["t"] >= hi_excl:
            raise SplitViolation(f"bar {r['t']} outside [{lo}, {hi_excl})")


def normalize_ms(x):
    x = int(float(x))
    return x // 1000 if x > 10 ** 14 else x           # 2025 archive files carry microseconds


def _stamp_start(path):
    """First millisecond of the YYYY-MM in a file name like SYM-1h-2024-06.csv (None if unparseable)."""
    stem = Path(path).stem
    try:
        y, m = int(stem[-7:-3]), int(stem[-2:])
        return ms(y, m, 1)
    except ValueError:
        return None


def load_spot(sym, tf, data_end_excl, root=SPOT_ROOT):
    """Spot klines of one symbol/tf with open time < data_end_excl. Refuses data_end past VALIDATION end and any row at or
    after it; files whose month starts at or after data_end are never opened."""
    if data_end_excl > VAL_END_EXCL:
        raise SplitViolation(f"data_end {data_end_excl} is past the VALIDATION end {VAL_END_EXCL} (HOLDOUT is sealed)")
    rows = []
    for p in sorted(glob.glob(str(Path(root) / sym / tf / "klines" / f"{sym}-{tf}-*.csv"))):
        s = _stamp_start(p)
        if s is None or s >= data_end_excl:
            continue
        with open(p, newline="") as f:
            for rec in csv.reader(f):
                if len(rec) < 6 or not rec[0].strip().lstrip("-").isdigit():
                    continue
                rows.append({"t": normalize_ms(rec[0]), "o": float(rec[1]), "h": float(rec[2]), "l": float(rec[3]),
                             "c": float(rec[4]), "v": float(rec[5])})
    rows.sort(key=lambda r: r["t"])
    dedup = {r["t"]: r for r in rows}
    rows = [dedup[k] for k in sorted(dedup)]
    check_window(rows, DEV_LO, VAL_END_EXCL)
    return [r for r in rows if r["t"] < data_end_excl]


class FundingTable:
    def __init__(self, rows):
        rows = sorted(rows)
        self.t = [r[0] for r in rows]
        self.cum = [0.0]
        for _, v in rows:
            self.cum.append(self.cum[-1] + v)

    def sum(self, t0, t1):
        """Sum of rates with t0 < calc_time <= t1."""
        return self.cum[bisect.bisect_right(self.t, t1)] - self.cum[bisect.bisect_right(self.t, t0)]


def load_funding(sym, data_end_excl):
    if data_end_excl > VAL_END_EXCL:
        raise SplitViolation("funding data_end past the VALIDATION end")
    rows = []
    for p in sorted(glob.glob(str(Path(FUND_DIR) / f"{sym}-fundingRate-*.csv"))):
        s = _stamp_start(p)
        if s is None or s >= data_end_excl:
            continue
        with open(p, newline="") as f:
            for rec in csv.DictReader(f):
                try:
                    rows.append((normalize_ms(rec["calc_time"]), float(rec["last_funding_rate"])))
                except (KeyError, ValueError, TypeError):
                    continue
    check_window([{"t": r[0]} for r in rows], 0, VAL_END_EXCL)
    return FundingTable([r for r in rows if r[0] < data_end_excl])


# ------------------------------------------------------------------------------------------------ series
def resample_complete(h1, length_ms):
    """UTC buckets of the 1h bars; a bucket is emitted only when all its hours are present (closed and complete)."""
    need = length_ms // HOUR
    out, cur, key = [], [], None
    for b in h1:
        kb = b["t"] // length_ms
        if kb != key:
            if cur and len(cur) == need:
                out.append(_agg(cur, key, length_ms))
            cur, key = [], kb
        cur.append(b)
    if cur and len(cur) == need:
        out.append(_agg(cur, key, length_ms))
    return out


def _agg(cur, key, length_ms):
    return {"t": key * length_ms, "o": cur[0]["o"], "h": max(b["h"] for b in cur), "l": min(b["l"] for b in cur),
            "c": cur[-1]["c"]}


def _tf_entry(bars, length):
    r = rsi_core([b["c"] for b in bars]) if len(bars) > 14 else [None] * len(bars)
    return {"bars": bars, "t": [b["t"] for b in bars], "close_t": [b["t"] + length for b in bars],
            "rsi": [None if x is None else float(x) for x in r], "len": length}


def build_series_from(h1, h4):
    """tf -> {bars, t, close_t, rsi, len}. 12h and 1d are resampled from the closed 1h bars (brief)."""
    return {"1h": _tf_entry(h1, HOUR), "4h": _tf_entry(h4, 4 * HOUR),
            "12h": _tf_entry(resample_complete(h1, 12 * HOUR), 12 * HOUR),
            "1d": _tf_entry(resample_complete(h1, DAY), DAY)}


def load_series(sym, data_end_excl, root=SPOT_ROOT):
    return build_series_from(load_spot(sym, "1h", data_end_excl, root), load_spot(sym, "4h", data_end_excl, root))


# ------------------------------------------------------------------------------------------------ events
def side_of_line(line):
    """40 = long (+1), 60 = short (-1)."""
    return 1 if line == 40 else -1


def find_bounces(r, t, tf_ms, line, cushion=CUSHION, window=WINDOW, stats=None):
    """Approach + bounce events for one TF series (r = RSI list with None, t = bar open times).
    40: bar k enters [38, 42] with bar k-1 > 42; the first close j in k+1..k+window with RSI > 42, with no RSI < 38 first.
    60: bar k enters [58, 62] with bar k-1 < 58; the first close j with RSI < 58, with no RSI > 62 first.
    Bars k-1..j must be consecutive in time, else the event is skipped (stats['gap'] counts it)."""
    lo, hi = line - cushion, line + cushion
    n = len(r)
    out = []
    for k in range(1, n):
        a, x = r[k - 1], r[k]
        if a is None or x is None or not (lo <= x <= hi):
            continue
        if line == 40 and not a > hi:
            continue
        if line == 60 and not a < lo:
            continue
        for j in range(k + 1, min(k + window, n - 1) + 1):
            v = r[j]
            if v is None:
                break
            if line == 40:
                if v < lo:
                    break
                found = v > hi
            else:
                if v > hi:
                    break
                found = v < lo
            if found:
                if all(t[i + 1] - t[i] == tf_ms for i in range(k - 1, j)):
                    out.append({"k": k, "j": j})
                elif stats is not None:
                    stats["gap"] = stats.get("gap", 0) + 1
                break
    return out


def asof(entry, T):
    """RSI of the last bar of this TF whose close time <= T; None if none, missing, or older than 2 bar lengths."""
    i = bisect.bisect_right(entry["close_t"], T) - 1
    if i < 0 or entry["rsi"][i] is None or T - entry["close_t"][i] > STALE_BARS * entry["len"]:
        return None
    return entry["rsi"][i]


def confluent_tfs(ser, trade_tf, T, line, cushion=CUSHION):
    out = []
    for tf in TFS:
        if tf == trade_tf or tf not in ser:
            continue
        v = asof(ser[tf], T)
        if v is not None and abs(v - line) <= cushion:
            out.append(tf)
    return out


def htf_bias(ser, trade_tf, T):
    tf2 = HTF_OF[trade_tf]
    if tf2 not in ser:
        return None
    v = asof(ser[tf2], T)
    if v is None or v == 50:
        return None
    return "up" if v > 50 else "down"


def is_against(side, bias):
    return (side > 0 and bias == "down") or (side < 0 and bias == "up")


# ------------------------------------------------------------------------------------------------ trade math
def structural_stop(bars, k, j, side):
    if side > 0:
        return min(b["l"] for b in bars[k:j + 1])
    return max(b["h"] for b in bars[k:j + 1])


def rt_cost_bps():
    """Regime A: taker both legs (fees.DERIBIT_TAKER 5 bps each) + 2 bps round-trip slippage (FORMULAS s13)."""
    return 2 * fees.DERIBIT_TAKER * 1e4 + fees.SLIPPAGE_RT_S13 * 1e4


def fee_r(entry, stop):
    return rt_cost_bps() / (abs(entry - stop) / entry * 1e4)


def funding_r(rates, t0, t1, side, entry, risk):
    """side_sign x sum(rate, t0 < calc_time <= t1) x entry / risk (FORMULAS s13; long pays positive funding)."""
    s = rates.sum(t0, t1) if isinstance(rates, FundingTable) else sum(v for t, v in rates if t0 < t <= t1)
    return side * s * entry / risk


def simulate(bars, j, side, entry, stop, target_r=TARGET_R, max_bars=MAX_BARS):
    """Entry at the close of bar j (bar j is not scanned). Scan bars j+1..j+max_bars. Stop wins a same-bar tie; a stop is
    filled at the open when the bar gaps through it, the target at the open when the bar gaps past it. Time stop = close of
    bar j+max_bars. Returns (exit_idx, px, why, gross_R) or (None, None, 'censored', None) when the data ends first."""
    risk = abs(entry - stop)
    target = entry + side * target_r * risk
    last = min(j + max_bars, len(bars) - 1)
    for q in range(j + 1, last + 1):
        b = bars[q]
        if side > 0:
            if b["l"] <= stop:
                px, why = min(b["o"], stop), "stop"
            elif b["h"] >= target:
                px, why = max(b["o"], target), "target"
            elif q == j + max_bars:
                px, why = b["c"], "time"
            else:
                continue
        else:
            if b["h"] >= stop:
                px, why = max(b["o"], stop), "stop"
            elif b["l"] <= target:
                px, why = min(b["o"], target), "target"
            elif q == j + max_bars:
                px, why = b["c"], "time"
            else:
                continue
        return q, px, why, side * (px - entry) / risk
    return None, None, "censored", None


def evaluate_entry(bars, k, j, side, tf_ms, rates):
    """The trade for the event (band entry k, bounce close j): dict, or 'invalid' / 'censored'."""
    entry = bars[j]["c"]
    stop = structural_stop(bars, k, j, side)
    if (side > 0 and stop >= entry) or (side < 0 and stop <= entry):
        return "invalid"
    q, px, why, gross = simulate(bars, j, side, entry, stop)
    if why == "censored":
        return "censored"
    risk = abs(entry - stop)
    fr = fee_r(entry, stop)
    fu = funding_r(rates, bars[j]["t"] + tf_ms, bars[q]["t"] + tf_ms, side, entry, risk)
    return {"gross": gross, "fee_r": fr, "funding_r": fu, "net": gross - fr - fu, "why": why, "stop": stop,
            "entry": entry, "exit_idx": q, "stop_bps": risk / entry * 1e4}


def apply_overlap(sigs, exit_idx_of):
    """One trade at a time. exit_idx_of(j) returns the exit bar index of the trade for entry bar j, or None if it is not a
    trade. An entry bar before the busy-until bar is skipped; entering at the close of the exit bar itself is allowed."""
    taken, skipped, busy = [], 0, -1
    for j in sigs:
        if j < busy:
            skipped += 1
            continue
        ex = exit_idx_of(j)
        if ex is None:
            continue
        taken.append(j)
        busy = ex
    return taken, skipped


# ------------------------------------------------------------------------------------------------ statistics
def cluster_mean_se(vals, keys):
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), 0
    mean = sum(vals) / n
    if n < 2:
        return mean, float("nan"), n
    groups = {}
    for v, k in zip(vals, keys):
        groups[k] = groups.get(k, 0.0) + (v - mean)
    return mean, math.sqrt(sum(g * g for g in groups.values())) / n, n


def cluster_key(trades):
    """UTC day for sets of 1h trades only; ISO week for any set containing 4h trades (PRE_REG)."""
    return "day" if all(t["tf"] == "1h" for t in trades) else "week"


def summarize(trades):
    n = len(trades)
    out = {"n": n}
    if n == 0:
        return out
    key = cluster_key(trades)
    mean, se, _ = cluster_mean_se([t["net"] for t in trades], [t[key] for t in trades])
    out.update({"cluster": key, "hit": sum(1 for t in trades if t["net"] > 0) / n,
                "gross": sum(t["gross"] for t in trades) / n, "fee_r": sum(t["fee_r"] for t in trades) / n,
                "funding_r": sum(t["funding_r"] for t in trades) / n, "net": mean, "se": se})
    if not math.isnan(se):
        out.update({"lo": mean - 1.96 * se, "hi": mean + 1.96 * se, "mde": 2.8 * se})
    return out


def dev_screen(s):
    return s.get("n", 0) >= 30 and s.get("net", -1) > 0 and s.get("lo", -1) > 0


def one_sided_p(s):
    return 0.5 * math.erfc((s["net"] / s["se"]) / math.sqrt(2))


def holm_adjust(pvals, m=HOLM_M):
    """Holm step-down at family size m: smallest p x m, next x (m-1), ... monotone, capped at 1 (unread trials are p = 1)."""
    order = sorted(pvals, key=lambda k: pvals[k])
    out, prev = {}, 0.0
    for i, k in enumerate(order):
        prev = max(prev, min(1.0, (m - i) * pvals[k]))
        out[k] = prev
    return out


def verdict(trial, dev, val, holm_p):
    if dev_screen(dev):
        if val is not None and holm_p is not None and holm_p < 0.05 and val["net"] > 0:
            return "PASS"
        return "INCONCLUSIVE"
    if dev.get("n", 0) > 0 and dev.get("net", 1) <= 0 and dev.get("hi", 1e9) < dev.get("mde", -1):
        return "FAIL"
    return "INCONCLUSIVE"


def asof_val(closes, vals, t):
    i = bisect.bisect_right(closes, t) - 1
    while i >= 0:
        if vals[i] is not None:
            return vals[i]
        i -= 1
    return None


# ------------------------------------------------------------------------------------------------ regime (research_kit logic)
try:
    import research_kit as RK  # noqa: E402
except Exception as _e:  # pragma: no cover
    RK = None
    RK_ERROR = repr(_e)


def resample_wm(daily, kind):
    """Closed-period resample of daily bars in UTC: 'W' (Monday 00:00 start) or 'M'. Adds close_ms (next period start)."""
    groups = {}
    for b in daily:
        d = dt.datetime.fromtimestamp(b["t"] / 1000, tz=dt.timezone.utc).date()
        if kind == "M":
            start = dt.date(d.year, d.month, 1)
            nxt = dt.date(d.year + (d.month == 12), 1 if d.month == 12 else d.month + 1, 1)
        else:
            start = d - dt.timedelta(days=d.weekday())
            nxt = start + dt.timedelta(days=7)
        if start not in groups:
            groups[start] = {"t": ms(start.year, start.month, start.day), "c": b["c"],
                             "close_ms": ms(nxt.year, nxt.month, nxt.day)}
        groups[start]["c"] = b["c"]
    return [groups[k] for k in sorted(groups)]


class Regime:
    """regime_tag contract of research_kit (Malkan weekly+monthly 60/40 band with the daily SMA side), recomputed with the
    same pure helpers (RK.ma_side, RK.rsi_band) as the shipped eh-h2 worker (its _last_closed path returned None)."""

    def __init__(self, daily_bars):
        self.dclose = [b["t"] + DAY for b in daily_bars]
        self.dc = [b["c"] for b in daily_bars]
        wk, mo = resample_wm(daily_bars, "W"), resample_wm(daily_bars, "M")
        self.wc = [w["close_ms"] for w in wk]
        self.wr = rsi_core([w["c"] for w in wk])
        self.mc = [m["close_ms"] for m in mo]
        self.mr = rsi_core([m["c"] for m in mo])
        self.wk = wk

    def at(self, t):
        if RK is None:
            return None
        k = bisect.bisect_right(self.dclose, t)
        side = RK.ma_side(self.dc[:k], RK.MA_N)
        band = RK.rsi_band(asof_val(self.wc, self.wr, t), asof_val(self.mc, self.mr, t))
        if side is None or band is None:
            return None
        if band == "bull" and side == "above":
            return "bull"
        if band == "bear" and side == "below":
            return "bear"
        return "range"


# ------------------------------------------------------------------------------------------------ pipeline
def _date(T):
    return dt.datetime.fromtimestamp(T / 1000, tz=dt.timezone.utc).date()


def collect_events(sym, ser, sig_lo, sig_hi):
    """All band-entry bounce events of this symbol (trade TFs 1h, 4h) with open time of the entry bar in [sig_lo, sig_hi).
    No returns computed here."""
    evs, stats = [], {"gap": 0}
    for tf in TRADE_TFS:
        e = ser[tf]
        for line in LINES:
            for ev in find_bounces(e["rsi"], e["t"], e["len"], line, stats=stats):
                j = ev["j"]
                if not (sig_lo <= e["t"][j] < sig_hi):
                    continue
                T = e["t"][j] + e["len"]
                side = side_of_line(line)
                tfs = confluent_tfs(ser, tf, T, line)
                bias = htf_bias(ser, tf, T)
                d = _date(T)
                iso = d.isocalendar()
                evs.append({"sym": sym, "tf": tf, "line": line, "side": side, "k": ev["k"], "j": j, "T": T,
                            "confl": tfs, "confl_n": len(tfs), "htf": bias or "none", "against": is_against(side, bias),
                            "year": d.year, "date": d.isoformat(), "day": d.isoformat(),
                            "week": f"{iso[0]}-W{iso[1]:02d}"})
    return evs, stats


def run_trades(evs, ser, rates, regime):
    """Evaluate the events: chains per (tf, population); returns (trades, counts)."""
    trades, counts = [], {"invalid": 0, "censored": 0, "overlap": 0}
    for tf in TRADE_TFS:
        bars, tf_ms = ser[tf]["bars"], ser[tf]["len"]
        for pop in ("conf", "none"):
            sub = sorted((e for e in evs if e["tf"] == tf and (e["confl_n"] >= 1) == (pop == "conf")),
                         key=lambda e: (e["j"], e["line"]))
            by_j = {}
            for e in sub:
                by_j.setdefault(e["j"], e)        # a bar can be a bounce for at most one line

            def sim(j, sub_by=by_j, bars=bars, tf_ms=tf_ms, pop=pop):
                e = sub_by[j]
                res = evaluate_entry(bars, e["k"], j, e["side"], tf_ms, rates)
                if res == "invalid":
                    counts["invalid"] += 1
                    return None
                if res == "censored":
                    counts["censored"] += 1
                    return None
                tr = dict(e, pop=pop, **res)
                tr["regime"] = regime.at(e["T"])
                trades.append(tr)
                return res["exit_idx"]

            taken, skipped = apply_overlap(sorted(by_j), sim)
            counts["overlap"] += skipped
    return trades, counts


def load_world(data_end):
    world = {}
    for sym in SYMBOLS:
        ser = load_series(sym, data_end)
        world[sym] = {"ser": ser, "rates": load_funding(sym, data_end), "regime": Regime(ser["1d"]["bars"])}
    return world


def trial_sets(trades):
    t11 = [t for t in trades if t["pop"] == "conf"]
    t12 = [t for t in t11 if t["against"]]
    return {"T11": t11, "T12": t12}


def cells_rows(trades):
    """Every cell (exploratory unless it is T11 or T12), DEV or VALIDATION."""
    rows = []

    def add(name, ts, **meta):
        s = summarize(ts)
        row = {"set": name, "tf": "", "line": "", "nconf": "", "htf": "", "regime": "", "year": "all"}
        row.update(meta)
        row.update(s)
        rows.append(row)

    conf = [t for t in trades if t["pop"] == "conf"]
    none = [t for t in trades if t["pop"] == "none"]
    add("T11", conf)
    add("T12", [t for t in conf if t["against"]])
    for y in sorted({t["year"] for t in conf}):
        add("T11", [t for t in conf if t["year"] == y], year=y)
        add("T12", [t for t in conf if t["against"] and t["year"] == y], year=y)
    for pname, pop in (("T11", conf), ("NOCONF", none)):
        for tf in TRADE_TFS:
            add(pname + "_tf", [t for t in pop if t["tf"] == tf], tf=tf)
            for line in LINES:
                add(pname + "_tf_line", [t for t in pop if t["tf"] == tf and t["line"] == line], tf=tf, line=line)
        for line in LINES:
            add(pname + "_line", [t for t in pop if t["line"] == line], line=line)
        for reg in ("bull", "range", "bear"):
            add(pname + "_regime", [t for t in pop if t["regime"] == reg], regime=reg)
    add("NOCONF", none)
    for n in (1, 2, 3):
        add("T11_nconf", [t for t in conf if t["confl_n"] == n], nconf=n)
        for tf in TRADE_TFS:
            add("T11_nconf_tf", [t for t in conf if t["confl_n"] == n and t["tf"] == tf], nconf=n, tf=tf)
    for h in ("up", "down", "none"):
        add("T11_htf", [t for t in conf if t["htf"] == h], htf=h)
        for tf in TRADE_TFS:
            add("T11_htf_tf", [t for t in conf if t["htf"] == h and t["tf"] == tf], htf=h, tf=tf)
    return rows


CELL_COLS = ["set", "tf", "line", "nconf", "htf", "regime", "year", "n", "cluster", "hit", "gross", "fee_r", "funding_r",
             "net", "se", "lo", "hi", "mde"]


def write_cells(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(CELL_COLS)
        for r in rows:
            w.writerow([("" if r.get(c) is None else (f"{r[c]:.4f}" if isinstance(r.get(c), float) else r.get(c, "")))
                        for c in CELL_COLS])


def fmt(s):
    if s.get("n", 0) == 0:
        return "n=0"
    if "lo" not in s:
        return f"n={s['n']} net={s['net']:+.3f}"
    return (f"n={s['n']} hit={s['hit']:.3f} gross={s['gross']:+.3f} fee_r={s['fee_r']:.3f} fund={s['funding_r']:+.3f} "
            f"net={s['net']:+.3f} se={s['se']:.3f} CI=[{s['lo']:+.3f},{s['hi']:+.3f}] MDE={s['mde']:.3f} ({s['cluster']})")


def regime_mix_line(world):
    if RK is None:
        return "research_kit import failed: " + RK_ERROR
    reg = world["BTCUSDT"]["regime"]
    window = [reg.at(w["t"]) for w in reg.wk if SIGNAL_START <= w["t"] < DEV_END_EXCL]
    return RK.regime_mix_line(window)


def count_pass(world, lo, hi):
    """Events per year x TF x line x population (no returns)."""
    rows = {}
    gaps = 0
    for sym in SYMBOLS:
        evs, st = collect_events(sym, world[sym]["ser"], lo, hi)
        gaps += st["gap"]
        for e in evs:
            key = (e["year"], e["tf"], e["line"], "conf" if e["confl_n"] >= 1 else "none")
            rows[key] = rows.get(key, 0) + 1
    return rows, gaps


def main(argv):
    mode = argv[0] if argv else "dev"
    if mode not in ("count", "dev", "val"):
        print(__doc__)
        return 2
    world = load_world(DEV_END_EXCL)
    print("Regime mix:", regime_mix_line(world))
    if mode == "count":
        rows, gaps = count_pass(world, SIGNAL_START, DEV_END_EXCL)
        print(f"events with a gap skipped: {gaps}")
        with open(HERE / "counts.csv", "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["year", "tf", "line", "side", "population", "events"])
            for (y, tf, line, pop), n in sorted(rows.items()):
                w.writerow([y, tf, line, "long" if line == 40 else "short", pop, n])
        tot = {}
        for (y, tf, line, pop), n in rows.items():
            tot[(tf, line, pop)] = tot.get((tf, line, pop), 0) + n
        for k, n in sorted(tot.items()):
            print("events", k, n)
        return 0

    trades, counts = [], {"invalid": 0, "censored": 0, "overlap": 0}
    for sym in SYMBOLS:
        w = world[sym]
        evs, st = collect_events(sym, w["ser"], SIGNAL_START, DEV_END_EXCL)
        tr, c = run_trades(evs, w["ser"], w["rates"], w["regime"])
        trades += tr
        for k in counts:
            counts[k] += c[k]
    rows = cells_rows(trades)
    write_cells(HERE / "cells.csv", rows)
    print("DEV 2017-10-01..2024-06-30 signals;", counts)
    dev = {k: summarize(v) for k, v in trial_sets(trades).items()}
    for k in ("T11", "T12"):
        print(k, fmt(dev[k]), "SCREEN", "PASS" if dev_screen(dev[k]) else "no")
    for r in rows:
        if r["set"] in ("T11", "T12") and r["year"] != "all":
            print("  year", r["set"], r["year"], fmt(r))
    for r in rows:
        if r["set"] not in ("T11", "T12"):
            tag = " ".join(f"{c}={r[c]}" for c in ("tf", "line", "nconf", "htf", "regime") if r[c] != "")
            print("  expl", r["set"], tag, fmt(r))
    if mode == "val":
        return run_validation(dev)
    return 0


def run_validation(dev):
    marker = HERE / "validation_once.txt"
    if marker.exists():
        print("VALIDATION already read once (validation_once.txt exists); refusing a second read")
        return 3
    passed = [k for k in ("T11", "T12") if dev_screen(dev[k])]
    if not passed:
        print("VALIDATION not read: no trial passed the DEV screen")
        return 0
    marker.write_text("started; trials " + ",".join(passed) + "\n", newline="\n")
    world = load_world(VAL_END_EXCL)
    trades = []
    for sym in SYMBOLS:
        w = world[sym]
        evs, _ = collect_events(sym, w["ser"], VAL_START, VAL_END_EXCL)
        tr, _c = run_trades(evs, w["ser"], w["rates"], w["regime"])
        trades += tr
    sets = trial_sets(trades)
    ps, out = {}, {}
    for k in ("T11", "T12"):
        s = summarize(sets[k])
        out[k] = s
        ps[k] = one_sided_p(s) if (k in passed and s.get("se") and not math.isnan(s["se"])) else 1.0
    holm = holm_adjust(ps, HOLM_M)
    lines = []
    for k in ("T11", "T12"):
        v = verdict(k, dev[k], out[k] if k in passed else None, holm[k] if k in passed else None)
        lines.append(f"{k} VALIDATION {fmt(out[k])} p={ps[k]:.4g} holm_m{HOLM_M}={holm[k]:.4g} verdict={v}")
    print("\n".join(lines))
    marker.write_text("read once\n" + "\n".join(lines) + "\n", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
