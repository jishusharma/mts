"""Recompute RSI / Bollinger / StochRSI from public Binance fapi klines at a shot clock and
compare with values typed from a CoinGlass chart. Read-only, label-only: no signals, no orders.

  python scripts/dev/chart_verify.py BTCUSDT 15m 2026-10-12T09:30 --seen RSI=69,BB_up=81146.6

Formulas: MyTradingSys/backtest/layers/FORMULAS.md s1 (RSI), s22 (Bollinger), s23 (StochRSI).
Klines with open time <= the shot clock are used; the last bar is the one forming at the shot,
so its close is the bar's final close (exact only if you shoot near the close of that bar).
"""
import argparse, datetime as dt, json, math, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "rsi"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "observation"))
from rsi_core import rsi_core  # noqa: E402
import capture  # noqa: E402

FAPI = "https://fapi.binance.com/fapi/v1/klines"
# capture.TF_MINUTES is the one map; these capture-only intervals are not served by fapi klines
FAPI_UNSUPPORTED = {"4m", "3h", "7h"}
TFS = set(capture.TF_MINUTES) - FAPI_UNSUPPORTED


def rsi(closes, period=14):
    return rsi_core(list(closes), period)


def _sma(xs, n):
    out = [None] * len(xs)
    for i in range(n - 1, len(xs)):
        w = xs[i - n + 1:i + 1]
        if all(v is not None for v in w):
            out[i] = sum(w) / n
    return out


def bollinger(closes, n=20, mult=2.0):
    """-> (upper, mid, lower); population sd (FORMULAS.md s22)."""
    up, mid, lo = [None] * len(closes), [None] * len(closes), [None] * len(closes)
    for i in range(n - 1, len(closes)):
        w = closes[i - n + 1:i + 1]
        m = sum(w) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / n)
        up[i], mid[i], lo[i] = m + mult * sd, m, m - mult * sd
    return up, mid, lo


def stochrsi(closes, rsi_len=14, stoch_len=14, k_len=3, d_len=3):
    """-> (K, D) in 0..100 (FORMULAS.md s23)."""
    r = rsi(closes, rsi_len)
    raw = [None] * len(r)
    for i in range(len(r)):
        w = r[i - stoch_len + 1:i + 1] if i >= stoch_len - 1 else None
        if w and all(v is not None for v in w):
            hi, lo = max(w), min(w)
            raw[i] = 0.0 if hi == lo else 100.0 * (r[i] - lo) / (hi - lo)
    k = _sma(raw, k_len)
    return k, _sma(k, d_len)


def compute(closes):
    up, mid, lo = bollinger(closes)
    k, d = stochrsi(closes)
    r = rsi(closes)
    return {"RSI": r[-1], "BB_up": up[-1], "BB_mid": mid[-1], "BB_low": lo[-1],
            "StochRSI_K": k[-1], "StochRSI_D": d[-1]}


def compare(calc, seen, tol_rsi=0.5, tol_stoch=1.0, tol_bb_pct=0.01):
    lines = []
    for name, val in seen.items():
        c = calc.get(name)
        if c is None:
            lines.append(f"{name:11s} seen={val:g} calc=n/a (not enough bars or unknown name) MISMATCH")
            continue
        diff = val - c
        if name.startswith("BB_"):
            ok, tol = abs(diff) / abs(c) * 100 <= tol_bb_pct, f"{tol_bb_pct}%"
        else:
            t = tol_rsi if name == "RSI" else tol_stoch
            ok, tol = abs(diff) <= t, f"{t}"
        lines.append(f"{name:11s} seen={val:g} calc={c:.4f} diff={diff:+.4f} tol={tol} {'MATCH' if ok else 'MISMATCH'}")
    return lines


def fetch_closes(symbol, tf, shot_ms, limit=600):
    url = f"{FAPI}?symbol={symbol}&interval={tf}&endTime={shot_ms}&limit={limit}"
    with urllib.request.urlopen(url, timeout=20) as f:
        rows = json.load(f)
    return [float(r[4]) for r in rows], int(rows[-1][0])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("symbol")
    ap.add_argument("tf")
    ap.add_argument("utc", help="shot clock, e.g. 2026-10-12T09:30 (UTC)")
    ap.add_argument("--seen", default="", help="NAME=value,... from {RSI,BB_up,BB_mid,BB_low,StochRSI_K,StochRSI_D}")
    ap.add_argument("--tol-rsi", type=float, default=0.5)
    ap.add_argument("--tol-stoch", type=float, default=1.0)
    ap.add_argument("--tol-bb-pct", type=float, default=0.01)
    a = ap.parse_args(argv)
    if a.tf not in TFS:
        ap.error(f"tf must be one of {sorted(TFS)}")
    t = dt.datetime.fromisoformat(a.utc.replace("Z", ""))
    shot_ms = int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    closes, last_open = fetch_closes(a.symbol.upper(), a.tf, shot_ms)
    calc = compute(closes)
    print(f"{a.symbol.upper()} {a.tf} shot={a.utc}Z last_bar_open={dt.datetime.fromtimestamp(last_open/1000, dt.timezone.utc):%Y-%m-%dT%H:%MZ} bars={len(closes)}")
    seen = {}
    for part in filter(None, a.seen.split(",")):
        k, v = part.split("=")
        seen[k.strip()] = float(v)
    for k, v in calc.items():
        print(f"{k:11s} calc={v:.4f}" if v is not None else f"{k:11s} calc=n/a")
    for line in compare(calc, seen, a.tol_rsi, a.tol_stoch, a.tol_bb_pct):
        print(line)


if __name__ == "__main__":
    main()
