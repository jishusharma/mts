"""adx_now.py - the Live Aid "ADX / DI" strip as text (R26), so a reader can quote the reads.

Same data and same rules as adx_strip.js: spot BTCUSDT klines from data-api.binance.vision, Wilder n=14 from
backtest/layers/adx/adx.py, 2d/3d/5d folded from daily bars on epoch-day buckets anchored 1970-01-01, 1w native (Monday).
Prints one table and writes runtime_data/live_aid/adx_state.json (gitignored). Descriptive only: no orders, public data.
Usage: python MyTradingSys/tools/live_aid/adx_now.py [--no-write]
"""
import json
import math
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "adx"))
import adx as ADX  # noqa: E402

BASE = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT"
OUT = ROOT / "runtime_data" / "live_aid" / "adx_state.json"
DAY = 86400000
N = 14
LV_NONE, LV_TREND, LV_STRETCH = 20, 25, 40      # 25 SOURCED (Wilder); 20 and 40 OURS (as in MEASURE/HOW_TO)
ARROW_BARS, THROUGH_BARS, CROSS_BARS = 3, 3, 10
TFS = ["1w", "5d", "3d", "2d", "1d", "4h", "1h", "15m", "5m"]
SRC = {"1w": ("1w", 0), "5d": ("1d", 5), "3d": ("1d", 3), "2d": ("1d", 2), "1d": ("1d", 0),
       "4h": ("4h", 0), "1h": ("1h", 0), "15m": ("15m", 0), "5m": ("5m", 0)}
USE = {"1w": "regime read, thin data", "5d": "regime read, thin data", "3d": "regime read, untested",
       "2d": "regime read, thin data", "1d": "filter: through 25", "4h": "context only, underpowered",
       "1h": "filter only", "15m": "do not use", "5m": "do not use"}


def fold(daily, n_days):
    """Daily kline rows -> n_days buckets on epoch-day anchor 1970-01-01 (OURS); a first bucket that starts before the data is dropped;
    the last bucket may be partial (closeTime = bucket end, so it reads as forming)."""
    out, cur, cur_b, first = [], None, None, True
    for k in daily:
        t, o, h, l, c = int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])
        day = t // DAY
        b = day // n_days * n_days
        if b != cur_b:
            if cur:
                out.append(cur)
            cur_b = b
            cur = None if (first and day != b) else [b * DAY, o, h, l, c, float(k[5]), (b + n_days) * DAY - 1]
            first = False
            continue
        if cur:
            cur[2], cur[3], cur[4], cur[5] = max(cur[2], h), min(cur[3], l), c, cur[5] + float(k[5])
    if cur:
        out.append(cur)
    return out


def closed_of(bars, now_ms):
    if not bars:
        return [], False
    forming = int(bars[-1][6]) >= now_ms
    return (bars[:-1] if forming else list(bars)), forming


def series(bars):
    return ADX.adx_di([float(b[2]) for b in bars], [float(b[3]) for b in bars], [float(b[4]) for b in bars], N)


def chip_of(adx, rising, falling):
    if adx < LV_NONE:
        return "NO TREND"
    if adx >= LV_STRETCH and falling:
        return "STRETCHED"
    if adx >= LV_TREND:
        return "TREND"
    return "BUILDING" if rising else "WEAK"


def row_state(dip, dim, adx):
    """State of the last bar of the series, or None when ADX is not defined there. Same rules as adx_strip.js rowState."""
    if not adx:
        return None
    last = len(adx) - 1
    a, p, q = adx[last], dip[last], dim[last]
    if a is None or p is None or q is None:
        return None
    ago = adx[last - ARROW_BARS] if last - ARROW_BARS >= 0 else None
    arrow = None if ago is None else ("up" if a > ago else "down" if a < ago else "flat")
    through = any(adx[i] is not None and adx[i - 1] is not None and adx[i - 1] < LV_TREND <= adx[i]
                  for i in range(max(1, last - THROUGH_BARS + 1), last + 1))
    cross = [(i, d) for i, d in ADX.crosses(dip, dim)]
    di_cross = None
    if cross and last - cross[-1][0] <= CROSS_BARS:
        di_cross = {"dir": cross[-1][1], "barsAgo": last - cross[-1][0]}
    return {"adx": a, "dip": p, "dim": q, "winner": "plus" if p > q else "minus" if p < q else None, "lead": abs(p - q),
            "arrow": arrow, "chip": chip_of(a, arrow == "up", arrow == "down"), "through25": through, "diCross": di_cross}


def row(bars, now_ms):
    closed, forming = closed_of(bars, now_ms)
    st = row_state(*series(closed))
    if st is None:
        return None
    fm = None
    if forming:
        al = row_state(*series(bars))
        if al:
            fm = {"adx": al["adx"], "dip": al["dip"], "dim": al["dim"]}
    st["forming"] = fm
    st["bars"] = len(closed)
    return st


def fetch(interval, limit=1000):
    req = urllib.request.Request("%s&interval=%s&limit=%d" % (BASE, interval, limit), headers={"User-Agent": "mts-adx-now/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def collect(now_ms=None):
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    cache, rows = {}, {}
    for tf in TFS:
        iv, nd = SRC[tf]
        try:
            if iv not in cache:
                cache[iv] = fetch(iv)
            rows[tf] = row(fold(cache[iv], nd) if nd else cache[iv], now_ms)
        except Exception as e:   # one frame failing must not hide the rest
            rows[tf] = {"error": str(e)[:80]}
    return now_ms, rows


def f(x):
    return "-" if x is None else "%.1f" % x


def render(now_ms, rows):
    lines = ["ADX/DI spot BTCUSDT (Binance, last CLOSED bar; forming bar in brackets) %s UTC" % time.strftime("%Y-%m-%d %H:%M", time.gmtime(now_ms / 1000)),
             "%-4s %-13s %6s %6s %6s  %-10s %-13s %s" % ("TF", "ADX", "+DI", "-DI", "lead", "chip", "marks", "use")]
    for tf in TFS:
        r = rows.get(tf)
        if not r or "error" in r:
            lines.append("%-4s -  %s" % (tf, (r or {}).get("error", "no data")))
            continue
        arrow = {"up": "^", "down": "v", "flat": "="}.get(r["arrow"], " ")
        adx = f(r["adx"]) + arrow + ("(%s)" % f(r["forming"]["adx"]) if r["forming"] else "")
        lead = ("+" if r["winner"] == "plus" else "-" if r["winner"] == "minus" else "=") + f(r["lead"])
        marks = " ".join(m for m in (["up25"] if r["through25"] else []) +
                         (["%s %db" % ("+>-" if r["diCross"]["dir"] == "green" else "->+", r["diCross"]["barsAgo"])] if r["diCross"] else []))
        lines.append("%-4s %-13s %6s %6s %6s  %-10s %-13s %s" % (tf, adx, f(r["dip"]), f(r["dim"]), lead, r["chip"], marks or "-", USE[tf]))
    lines.append("Higher frames (1w/5d/3d/2d) say whether a trend exists; lower frames only say if the current move is strong; a DI cross is not an entry (no fee-net edge measured on any frame).")
    return "\n".join(lines)


def main(argv):
    now_ms, rows = collect()
    print(render(now_ms, rows))
    if "--no-write" not in argv:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"t": now_ms, "src": "binance spot BTCUSDT", "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
