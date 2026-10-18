"""Read-only BTC market digest (observation only: no side, no routing, never imported by execution code).

Usage: python scripts/dev/market_guide.py [--stdout] [--now-ms N]
Writes MyTradingSys/runtime/market_guide.md atomically (tmp + os.replace).
"""
import argparse
import datetime
import importlib.util
import inspect
import json
import os
import statistics
import sys
import time

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MTS = os.path.join(REPO, "MyTradingSys")
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma as _rsi_ma  # noqa: E402
from MyTradingSys.backtest.layers.rsi import malkan_40_60  # noqa: E402

_sig = inspect.signature(malkan_40_60.malkan_regime)
MALKAN_LO = _sig.parameters["lo"].default
MALKAN_HI = _sig.parameters["hi"].default

TF_MS = {"5m": 300000, "15m": 900000, "1h": 3600000, "4h": 14400000}
TFS = ["5m", "15m", "1h", "4h"]
ALERT_TFS = ["1m", "5m", "15m", "1h", "4h"]
EXCLUDED_LAYERS = {"turn_of_candle"}
DAY_MS = 86400000
VERDICTS_PATH = os.path.join(REPO, "scripts", "dev", "market_guide_verdicts.json")
CANDLES_PATH = os.path.join(MTS, "research", "candle_patterns_2026-10-04", "pilot", "candles.py")


def _load_candles(path=CANDLES_PATH):
    spec = importlib.util.spec_from_file_location("mg_candles", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- data
def load_klines(path, now_ms):
    """Closed bars only (close_time < now_ms), as dicts {t,o,h,l,c,v,ct}. Missing file -> []."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for r in raw:
        try:
            if int(r["close_time"]) >= now_ms:
                continue
            out.append({"t": int(r["open_time"]), "o": float(r["open"]), "h": float(r["high"]),
                        "l": float(r["low"]), "c": float(r["close"]), "v": float(r["volume"]),
                        "ct": int(r["close_time"])})
        except (KeyError, TypeError, ValueError):
            continue
    out.sort(key=lambda b: b["t"])
    return out


def resample_4h(bars_1h):
    """Complete UTC 4h buckets only (all four 1h bars present)."""
    buckets = {}
    for b in bars_1h:
        buckets.setdefault(b["t"] // TF_MS["4h"], []).append(b)
    out = []
    for k in sorted(buckets):
        g = sorted(buckets[k], key=lambda b: b["t"])
        start = k * TF_MS["4h"]
        if [b["t"] for b in g] != [start + i * 3600000 for i in range(4)]:
            continue
        out.append({"t": start, "o": g[0]["o"], "h": max(b["h"] for b in g), "l": min(b["l"] for b in g),
                    "c": g[-1]["c"], "v": sum(b["v"] for b in g), "ct": g[-1]["ct"]})
    return out


# ---------------------------------------------------------------- indicators
def sma_series(vals, n):
    out = [None] * len(vals)
    for i in range(n - 1, len(vals)):
        out[i] = sum(vals[i - n + 1:i + 1]) / n
    return out


def ema_series(vals, n):
    out = [None] * len(vals)
    if len(vals) < n:
        return out
    prev = sum(vals[:n]) / n
    out[n - 1] = prev
    a = 2.0 / (n + 1)
    for i in range(n, len(vals)):
        prev = (vals[i] - prev) * a + prev
        out[i] = prev
    return out


def last_cross(fast, slow):
    """(direction, bars_ago) of the most recent sign change of fast-slow, or None."""
    last = len(fast) - 1
    prev_sign = None
    res = None
    for i in range(len(fast)):
        if fast[i] is None or slow[i] is None:
            continue
        d = fast[i] - slow[i]
        s = 1 if d > 0 else (-1 if d < 0 else 0)
        if s == 0:
            continue
        if prev_sign is not None and s != prev_sign:
            res = ("up" if s > 0 else "down", last - i)
        prev_sign = s
    return res


def _sign(x):
    return "up" if x > 0 else ("down" if x < 0 else "flat")


def ma_info(bars):
    c = [b["c"] for b in bars]
    out = {"price": c[-1] if c else None, "rows": [], "cross_ema": None, "cross_sma": None, "slope50": None}
    if not c:
        return out
    series = {}
    for name, fn, n in (("SMA20", sma_series, 20), ("SMA50", sma_series, 50), ("SMA200", sma_series, 200),
                        ("EMA9", ema_series, 9), ("EMA21", ema_series, 21)):
        series[name] = fn(c, n)
        v = series[name][-1]
        out["rows"].append((name, v, None if v is None else (c[-1] - v) / v * 100.0))
    out["cross_ema"] = last_cross(series["EMA9"], series["EMA21"])
    out["cross_sma"] = last_cross(series["SMA50"], series["SMA200"])
    s50 = series["SMA50"]
    if len(s50) >= 6 and s50[-1] is not None and s50[-6] is not None:
        out["slope50"] = _sign(s50[-1] - s50[-6])
    return out


def rsi_info(bars):
    c = [b["c"] for b in bars]
    out = {"rsi": None, "ma": None}
    try:
        rs = rsi_core(c, period=14)
    except ValueError:
        return out
    ma = _rsi_ma(rs, "SMA", 14)
    r = rs[-1]
    out["rsi"], out["ma"] = r, ma[-1]
    out["vs_ma"] = None if ma[-1] is None else ("above" if r > ma[-1] else ("below" if r < ma[-1] else "equal"))
    out["regime"] = "above %g" % MALKAN_HI if r > MALKAN_HI else ("below %g" % MALKAN_LO if r < MALKAN_LO else
                                                                   "%g-%g" % (MALKAN_LO, MALKAN_HI))
    lvl = min((MALKAN_LO, MALKAN_HI), key=lambda x: abs(r - x))
    out["level"], out["dist"] = lvl, r - lvl
    out["slope"] = None
    out["toward"] = None
    if len(rs) >= 4 and rs[-4] is not None:
        sl = r - rs[-4]
        out["slope"] = _sign(sl)
        if (lvl > r and sl > 0) or (lvl < r and sl < 0):
            out["toward"] = lvl
    return out


def candle_info(bars, candles_mod):
    n = len(bars)
    if n == 0:
        return []
    sig = candles_mod.signals(bars)
    found = []
    for name, idxs in sig.items():
        for i in idxs:
            if i >= n - 3:
                found.append((name, n - 1 - i))
    return sorted(found, key=lambda x: (x[1], x[0]))


# ---------------------------------------------------------------- volume context
# SOURCED: MyTradingSys/research/volume_2026-10-09/vfeat.py:13 (STRIDE={"4h": 6})
# SOURCED: MyTradingSys/research/volume_2026-10-09/vfeat.py:14 (KBASE={"4h": 20})
def volume_info(bars, k=20, stride=6):
    """Time-adjusted relative volume vs same-slot baseline (descriptive only: effort vs result, match OI scope)."""
    if not bars:
        return {"volume": None, "baseline": None, "relative_volume": None, "n": 0, "label": "descriptive only"}
    volumes = [b["v"] if isinstance(b, dict) else float(b) for b in bars]
    current = volumes[-1]
    priors = [volumes[-1 - stride * j] for j in range(1, k + 1) if len(volumes) - 1 - stride * j >= 0]
    n = len(priors)
    if n > 0:
        base = float(statistics.median(priors))
        rv = current / base if base > 0 else None
    else:
        base = None
        rv = None
    return {"volume": current, "baseline": base, "relative_volume": rv, "n": n, "label": "descriptive only"}


volume_context = volume_info


def volume_line(vinfo):
    rv = vinfo.get("relative_volume")
    n = vinfo.get("n", 0)
    val_str = "n/a" if rv is None else ("%.2fx" % rv)
    return "4h time-adjusted relative volume: %s (slot baseline n=%d) | effort vs result, match OI scope | descriptive only" % (val_str, n)


# ---------------------------------------------------------------- alerts
def load_alerts(path, now_ms):
    out = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("layer") in EXCLUDED_LAYERS:
                    continue
                t = d.get("t_close")
                if not isinstance(t, (int, float)) or t < now_ms - DAY_MS or t > now_ms:
                    continue
                out.append(d)
    except OSError:
        return None
    return out


def load_verdicts(path=VERDICTS_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def verdict_tag(verdicts, key):
    v = verdicts.get(key)
    return v.get("tag", "UNTESTED") if isinstance(v, dict) else "UNTESTED"


# ---------------------------------------------------------------- render
def _f(x, nd=2):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def _age(ms):
    m = int(ms // 60000)
    return "%dm" % m if m < 120 else "%.1fh" % (m / 60.0)


def _cx(c):
    return "n/a" if c is None else "%s %d bars ago" % (c[0], c[1])


def build(now_ms, kdir, adir, verdicts, candles_mod):
    bars = {tf: load_klines(os.path.join(kdir, "BTCUSDT_%s.json" % tf), now_ms) for tf in ("5m", "15m", "1h")}
    bars["4h"] = resample_4h(bars["1h"])
    last_px = None
    for tf in ("5m", "15m", "1h"):
        if bars[tf]:
            last_px = bars[tf][-1]["c"]
            break
    utc = datetime.datetime.fromtimestamp(now_ms / 1000.0, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = ["# BTC market guide", "",
         "Generated %s | last price %s" % (utc, _f(last_px)), "",
         "> Context only - not trade signals. Verdict tags from backtests.", ""]
    stale = {}
    for tf in TFS:
        b = bars[tf]
        stale[tf] = (not b) or (now_ms - b[-1]["ct"] > 2 * TF_MS[tf])
        if stale[tf]:
            L.append("**FEED STALE: %s**" % tf)
    if any(stale.values()):
        L.append("")
    tagma, tagr, tagc = (verdict_tag(verdicts, k) for k in ("ma", "rsi", "candles"))
    L += ["## MA [%s] (periods: textbook convention, observation only, NO-SOURCE for trading)" % tagma, "",
          "| tf | SMA20 | SMA50 | SMA200 | EMA9 | EMA21 | EMA9x21 | SMA50x200 | SMA50 slope(5) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for tf in TFS:
        m = ma_info(bars[tf])
        cells = []
        for name, v, pct in m["rows"]:
            cells.append("n/a" if v is None else "%s (%+.2f%%)" % (_f(v, 1), pct))
        if not m["rows"]:
            cells = ["n/a"] * 5
        L.append("| %s | %s | %s | %s | %s |" % (tf, " | ".join(cells), _cx(m["cross_ema"]), _cx(m["cross_sma"]),
                                                 m["slope50"] or "n/a"))
    L += ["", "## RSI(14) + SMA14 [%s] (Malkan levels %g/%g)" % (tagr, MALKAN_LO, MALKAN_HI), "",
          "| tf | rsi | rsi_ma | vs ma | regime | nearest | dist | slope(3) | note |",
          "|---|---|---|---|---|---|---|---|---|"]
    for tf in TFS:
        r = rsi_info(bars[tf]) if bars[tf] else {"rsi": None}
        if r["rsi"] is None:
            L.append("| %s | n/a | n/a | n/a | n/a | n/a | n/a | n/a | |" % tf)
            continue
        note = "moving toward %g" % r["toward"] if r["toward"] is not None else ""
        L.append("| %s | %s | %s | %s | %s | %g | %+.1f | %s | %s |" % (
            tf, _f(r["rsi"], 1), _f(r["ma"], 1), r["vs_ma"] or "n/a", r["regime"], r["level"], r["dist"],
            r["slope"] or "n/a", note))
    L += ["", "## Candles, last 3 closed bars [%s]" % tagc, "", "| tf | patterns (bars ago) |", "|---|---|"]
    for tf in TFS:
        ci = candle_info(bars[tf], candles_mod)
        L.append("| %s | %s |" % (tf, ", ".join("%s (%d)" % x for x in ci) if ci else "none"))
    tagv = verdict_tag(verdicts, "volume")
    vinfo = volume_info(bars.get("4h", []))
    L += ["", "## Volume [%s] (same-slot baseline, effort vs result, OI scope)" % tagv, "",
          volume_line(vinfo)]
    L += ["", "## Alerts, last 24h (turn_of_candle excluded)", "",
          "| tf | layer/sub/event | n | verdict | newest |", "|---|---|---|---|---|"]
    for tf in ALERT_TFS:
        al = load_alerts(os.path.join(adir, "%s.jsonl" % tf), now_ms)
        if al is None:
            L.append("| %s | n/a (no alert stream) | | | |" % tf)
            continue
        if not al:
            L.append("| %s | none | 0 | | |" % tf)
            continue
        groups = {}
        for a in al:
            k = (a.get("layer"), a.get("sub"), a.get("event"))
            g = groups.setdefault(k, [0, a])
            g[0] += 1
            if a["t_close"] > g[1]["t_close"]:
                g[1] = a
        items = sorted(groups.items(), key=lambda kv: (-kv[1][0], str(kv[0])))
        for k, (n, newest) in items[:6]:
            dr = newest.get("direction") or newest.get("side")
            ev = str(k[2])
            if len(ev) > 28:
                ev = ev[:25] + "..."
            L.append("| %s | %s/%s/%s | %d | %s | %s ago%s |" % (
                tf, k[0], k[1], ev, n, verdict_tag(verdicts, k[0]), _age(now_ms - newest["t_close"]),
                " " + str(dr) if dr else ""))
        if len(items) > 6:
            L.append("| %s | +%d more groups | %d | | |" % (tf, len(items) - 6, sum(g[0] for _, g in items[6:])))
    return "\n".join(L) + "\n"


def write_atomic(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--now-ms", type=int, default=None)
    ap.add_argument("--out", default=os.path.join(MTS, "runtime", "market_guide.md"))
    ap.add_argument("--klines-dir", default=os.path.join(MTS, "market_data", "klines"))
    ap.add_argument("--alerts-dir", default=os.path.join(MTS, "runtime", "alerts"))
    a = ap.parse_args(argv)
    now_ms = a.now_ms if a.now_ms is not None else int(time.time() * 1000)
    text = build(now_ms, a.klines_dir, a.alerts_dir, load_verdicts(), _load_candles())
    if a.stdout:
        sys.stdout.write(text)
    else:
        write_atomic(a.out, text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
