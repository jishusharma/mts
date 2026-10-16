"""R4 HTF context writer (collection-only; WHY_ENGINE_SILENT_2026-10-03.md:47). One JSONL row per 4H close:
  {"timestamp", "bal_4h", "bal_1d", "failed_breakout", "oi_delta_1h_pct"}
(failed_breakout is true / false when computed, null when no previous 4H balance exists) plus a per-day summary file {date, open, close, high, low}. A separate layer: nothing here gates Tom, no orders, no
execution imports, no keys; public USD-M market data only (klines + openInterestHist).

Definitions (see the session record for deviations):
 * 4H / 1D balance = signals.balance() (S1, verbatim) on 1m bars with N = 240 / N = 1440 (spec N is counted in 1m bars;
   240 is a grid value, 1440 = 24 h). A window that is short, gapped or not balanced -> None.
 * Kline bars carry no order-flow footprint, so each 1m bar gets a one-bin fp at floor(hlc3 / 10) * 10 holding its
   taker-buy / taker-sell volume. H, L, R are exact; poc is a 1m-resolution approximation of the true profile POC.
 * failed_breakout = the balance at the PREVIOUS 4H close (H, L) was probed by a 1m close beyond an edge inside the
   just-closed 4H window and the last close of the window is back inside [L, H] (model B probe -> reclaim, models.py:121,
   without the absorbed condition and without the 5-bar limit).
 * oi_delta_1h_pct = (OI[t] - OI[t-1h]) / OI[t-1h] * 100 from openInterestHist period 1h, the two latest points <= close.
OI fetch error or no bars -> no row (fail closed); an already written close is not rewritten.
"""
import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio.v3.signals import balance

MIN_MS = 60000
H4_MS = 4 * 3600 * 1000
N_4H = 240
N_1D = 1440
FP_BIN = 10.0
SYMBOL = "BTCUSDT"
BASE = "https://fapi.binance.com"
DEFAULT_OUT = Path(__file__).resolve().parents[3] / "research" / "htf_context"


def _iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _day(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def klines_to_bars(raw):
    """Binance kline rows -> v3 bar dicts (t,o,h,l,c,buy_vol,sell_vol,delta,fp), ascending, deduplicated."""
    by_t = {}
    for r in raw:
        t, o, h, l, c = int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4])
        v, tbv = float(r[5]), float(r[9])
        sell = v - tbv
        k = math.floor(((h + l + c) / 3.0) / FP_BIN + 1e-9) * FP_BIN
        by_t[t] = {"t": t, "o": o, "h": h, "l": l, "c": c, "buy_vol": tbv, "sell_vol": sell, "delta": tbv - sell,
                   "fp": "%g:%r:%r" % (k, tbv, sell)}
    return [by_t[t] for t in sorted(by_t)]


def oi_delta_pct(rows):
    """openInterestHist rows (any order) -> % change of sumOpenInterest between the two latest points."""
    if len(rows) < 2:
        raise ValueError("need 2 openInterestHist rows, got %d" % len(rows))
    a, b = sorted(rows, key=lambda r: int(r["timestamp"]))[-2:]
    prev, cur = float(a["sumOpenInterest"]), float(b["sumOpenInterest"])
    if not prev > 0:
        raise ValueError("openInterestHist base is not positive")
    return (cur - prev) / prev * 100.0


def _get(path, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_klines(start_ms, end_ms):
    return _get("/fapi/v1/klines", {"symbol": SYMBOL, "interval": "1m", "startTime": start_ms, "endTime": end_ms,
                                    "limit": 1500})


def fetch_oi(end_ms):
    return oi_delta_pct(_get("/futures/data/openInterestHist",
                             {"symbol": SYMBOL, "period": "1h", "endTime": end_ms, "limit": 2}))


def failed_breakout(bars, i, prev_bal):
    """True / False for a computed answer; None when there is no previous 4H balance to probe (unknown, not False)."""
    if prev_bal is None:
        return None
    H, L = prev_bal["H"], prev_bal["L"]
    win = bars[i - N_4H + 1:i + 1]
    probed = any(b["c"] > H or b["c"] < L for b in win)
    return bool(probed and L <= win[-1]["c"] <= H)


def build_row(bars, close_ms, oi_pct):
    """bars: 1m bars ending at close_ms - 1m. Returns the row dict, or None when the bars do not end at the close."""
    if not bars or bars[-1]["t"] != close_ms - MIN_MS:
        return None
    i = len(bars) - 1
    prev = balance(bars, i - N_4H, N_4H) if i - N_4H >= 0 else None
    return {"timestamp": _iso(close_ms), "bal_4h": balance(bars, i, N_4H), "bal_1d": balance(bars, i, N_1D),
            "failed_breakout": failed_breakout(bars, i, prev) if i >= N_4H else None, "oi_delta_1h_pct": oi_pct}


def _write(path, text, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write(text)


RETRY_MS = 120000


def row_written(now_ms, out_dir):
    """True when the row for the last 4H close <= now_ms is already on disk."""
    close_ms = (now_ms // H4_MS) * H4_MS
    f = Path(out_dir) / (_day(close_ms - 1) + ".jsonl")
    ts = _iso(close_ms)
    return f.exists() and any(json.loads(x).get("timestamp") == ts for x in f.read_text(encoding="utf-8").splitlines() if x)


def run_once(now_ms, fetch_klines_fn, fetch_oi_fn, out_dir):
    """Write the row for the last 4H close <= now_ms. Returns the row, or None (no bars / OI error / already written)."""
    close_ms = (now_ms // H4_MS) * H4_MS
    day = _day(close_ms - 1)
    out = Path(out_dir)
    f = out / (day + ".jsonl")
    ts = _iso(close_ms)
    if f.exists() and any(json.loads(x).get("timestamp") == ts for x in f.read_text(encoding="utf-8").splitlines() if x):
        return None
    start = close_ms - (N_1D + 1) * MIN_MS
    bars = [b for b in klines_to_bars(fetch_klines_fn(start, close_ms - 1)) if start <= b["t"] < close_ms]
    if not bars or bars[-1]["t"] != close_ms - MIN_MS:
        return None
    try:
        oi = fetch_oi_fn(close_ms)
    except Exception as e:                                      # fail closed: no OI -> no row
        print("htf_context: OI fetch failed, no row for %s: %r" % (ts, e), file=sys.stderr)
        return None
    row = build_row(bars, close_ms, oi)
    _write(f, json.dumps(row, sort_keys=True) + "\n", "a")
    d0 = int(datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    dbars = [b for b in bars if b["t"] >= d0]
    summ = {"date": day, "open": dbars[0]["o"], "close": dbars[-1]["c"], "high": max(b["h"] for b in dbars),
            "low": min(b["l"] for b in dbars)}
    _write(out / (day + "_summary.json"), json.dumps(summ, sort_keys=True) + "\n", "w")
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--once", action="store_true", help="write the last closed 4H row and exit (default)")
    ap.add_argument("--loop", action="store_true", help="wake 90 s after every 4H close")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    while True:
        now = int(time.time() * 1000)
        t0 = time.time()
        try:
            row = run_once(now, fetch_klines, fetch_oi, a.out_dir)
        except Exception as e:                                  # transient network error: retry below, never die
            row = None
            print("htf_context: run failed: %r" % (e,), file=sys.stderr)
        print(json.dumps({"row": row, "runtime_s": round(time.time() - t0, 3)}, sort_keys=True))
        if not a.loop:
            return 0
        nxt = (now // H4_MS + 1) * H4_MS + 90000
        if not row_written(now, a.out_dir):                     # 2026-10-15: one OI hiccup left the 20:00Z row missing for 4 h
            nxt = min(nxt, int(time.time() * 1000) + RETRY_MS)
        time.sleep(max(60, (nxt - int(time.time() * 1000)) / 1000))


if __name__ == "__main__":
    sys.exit(main())
