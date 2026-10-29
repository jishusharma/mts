"""Per-layer alert-rate watchdog: DEAD vs QUIET vs OK.

Expected rate = events/day of the layer's own detector over the last --days (default 30) of cached 1m klines
(Dumps/backtest/raw/klines, aggregated to the layer's tf), because the backtest reports carry counts for
different splits/params but no per-day live rate. Actual = alerts in runtime/alerts/*.jsonl with t_close within
the last --hours (default 12). One line per registered layer:
  DEAD  actual < floor*expected AND expected >= --min-expected (silence is implausible: P(0) <= ~5%)
  QUIET actual < floor*expected but expected is too small to call it dead
  OK    otherwise
Usage: python scripts/dev/alert_rate_check.py [--hours 12] [--days 30] [--floor 0.2]
"""
import argparse
import csv
import json
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "MyTradingSys" / "observation"))
import capture

DAY = 86400000
TF_MIN = {k: capture.TF_MINUTES[k] for k in ("1m", "3m", "5m", "15m", "1h", "4h", "1d")}


def aggregate(bars, tf_min):
    """1m bars -> complete tf_min buckets (epoch-aligned). Pure."""
    if tf_min == 1:
        return list(bars)
    span = tf_min * 60000
    out, cur = [], None
    for b in bars:
        k = b["t"] // span * span
        if cur is None or cur["t"] != k:
            if cur is not None and cur["n"] == tf_min:
                out.append({x: cur[x] for x in ("t", "o", "h", "l", "c", "v", "tbv")})
            cur = {"t": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"], "tbv": b["tbv"], "n": 1}
        else:
            cur["h"] = max(cur["h"], b["h"]); cur["l"] = min(cur["l"], b["l"]); cur["c"] = b["c"]
            cur["v"] += b["v"]; cur["tbv"] += b["tbv"]; cur["n"] += 1
    if cur is not None and cur["n"] == tf_min:
        out.append({x: cur[x] for x in ("t", "o", "h", "l", "c", "v", "tbv")})
    return out


def classify(actual, expected_window, floor=0.2, min_expected=3.0):
    if actual >= floor * expected_window:
        return "OK"
    return "DEAD" if expected_window >= min_expected else "QUIET"


def read_alerts(alerts_dir, since_ms):
    counts = {}
    for f in pathlib.Path(alerts_dir).glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            a = json.loads(line)
            if a.get("t_close", 0) >= since_ms:
                k = f'{a["layer"]}|{a["sub"]}|{a["tf"]}'
                counts[k] = counts.get(k, 0) + 1
    return counts


def load_funding(root):
    out = []
    for f in sorted(pathlib.Path(root, "fundingRate").glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            rd = csv.reader(fh)
            next(rd, None)
            out += [(int(r[0]), float(r[2])) for r in rd if r]
    return sorted(out)


def expected_per_day(registry, root, days, now_ms):
    from MyTradingSys.backtest.bt.bt_data import load_klines
    warm = 3  # extra days so 99-bar-lookback layers are warm at the window start
    start = now_ms - (days + warm) * DAY
    m1 = load_klines(root, "klines", start_ms=start)
    if not m1:
        return {}, 0.0
    win_start = m1[-1]["t"] - days * DAY
    span_days = (m1[-1]["t"] - win_start) / DAY
    rates, cache = {}, {}
    for key, e in registry.items():
        tf = e["tf"]
        if tf not in cache:
            cache[tf] = aggregate(m1, TF_MIN[tf])
        bars = cache[tf]
        try:
            fn = getattr(e["fn"], "raw", e["fn"])   # history-wrapped W3 layers: replay the bare adapter on the long window
            if e["sub"] == "funding_cvd_fade":
                from MyTradingSys.backtest.layers.alerts import live_layers as ll
                funding = load_funding(root)
                fn = ll.make_funding_layer(lambda s, n: funding)
            ev = fn(bars)
            rates[key] = sum(1 for x in ev if x["t"] >= win_start) / span_days
        except Exception as exc:  # report, do not crash the watchdog
            rates[key] = None
            print(f"# {key}: expected-rate computation failed: {exc}", file=sys.stderr)
    return rates, span_days


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--floor", type=float, default=0.2)
    ap.add_argument("--min-expected", type=float, default=3.0)
    ap.add_argument("--root", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--alerts-dir", default=str(REPO / "MyTradingSys" / "runtime" / "alerts"))
    args = ap.parse_args(argv)
    from MyTradingSys.backtest.layers.alerts.live_runner_cli import build_default_registry
    reg = build_default_registry()
    now_ms = int(time.time() * 1000)
    rates, span = expected_per_day(reg, args.root, args.days, now_ms)
    actual = read_alerts(args.alerts_dir, now_ms - int(args.hours * 3600000))
    for key in sorted(reg):
        r = rates.get(key)
        a = actual.get(key, 0)
        if r is None:
            print(f"{key:44s} N/A    actual={a} expected=n/a")
            continue
        exp = r * args.hours / 24.0
        print(f"{key:44s} {classify(a, exp, args.floor, args.min_expected):5s}  actual_{args.hours:g}h={a} "
              f"expected_{args.hours:g}h={exp:.1f} ({r:.2f}/day over {span:.0f}d)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
