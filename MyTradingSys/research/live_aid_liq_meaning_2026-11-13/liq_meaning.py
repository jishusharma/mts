"""Measure what BTCUSDT did after a 1m / 2m forced-selling or forced-buying burst (Live Aid card question, 2026-11-13).
Input: runtime_data/live_aid/xliq_events.jsonl (xliq_collector.py; line {v,t,s,usd,px}; s='long' = a LONG was liquidated). Gitignored.
Prices: Binance spot BTCUSDT 1m closes (data-api.binance.vision, public), cached under runtime_data/liq_rates/ (gitignored).
Writes: MyTradingSys/tools/live_aid/liq_rates.js (rewrites its DATA line only) and prints a table.
With too little history it writes rows: [] and says why.
Usage: python liq_meaning.py [--events PATH] [--out PATH]
"""
import argparse
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVENTS = ROOT / "runtime_data" / "live_aid" / "xliq_events.jsonl"
OUT = ROOT / "MyTradingSys" / "tools" / "live_aid" / "liq_rates.js"
CACHE = ROOT / "runtime_data" / "liq_rates"
MIN_SPAN_H = 24                                   # OURS: below this the file is "not measured"
BUCKETS = [("250k-1M", 250_000, 1_000_000), ("1M-5M", 1_000_000, 5_000_000), ("5M+", 5_000_000, 1e12)]  # OURS (USD)
WINS = {"1m": 60_000, "2m": 120_000}              # the card's windows
DEDUP_MS = 15 * 60_000                            # OURS: same-side bursts within 15 min of a counted one are dropped
HORIZ = (5, 15, 60)                               # minutes, OURS
URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime=%d"


def load_events(path):
    ev = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
            ev.append((int(e["t"]), e["s"], float(e["usd"])))
        except (ValueError, KeyError, TypeError):
            continue
    return sorted(ev)


def closes(t0, t1):
    """{minute_open_ms: close} from public klines."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out, t = {}, t0 // 60_000 * 60_000
    while t <= t1:
        with urllib.request.urlopen(URL % t, timeout=30) as r:
            rows = json.load(r)
        if not rows:
            break
        for k in rows:
            out[int(k[0])] = float(k[4])
        t = int(rows[-1][0]) + 60_000
        time.sleep(0.2)
    (CACHE / "closes.json").write_text(json.dumps(out), encoding="utf-8")
    return out


def bursts(ev, win_ms):
    """Aligned bins by side, venues summed: [(bin_end_ms, side, usd)], first one per DEDUP_MS per side."""
    bins = {}
    for t, s, usd in ev:
        k = (t // win_ms, s)
        bins[k] = bins.get(k, 0.0) + usd
    last, out = {}, []
    for (b, s), usd in sorted(bins.items()):
        end = (b + 1) * win_ms
        if usd < BUCKETS[0][1] or end - last.get(s, -10 ** 18) < DEDUP_MS:
            continue
        last[s] = end
        out.append((end, s, usd))
    return out


def rows_from(ev, px):
    rows = []
    for wn, wms in WINS.items():
        bs = bursts(ev, wms)
        for side in ("long", "short"):
            for name, lo, hi in BUCKETS:
                mv = {h: [] for h in HORIZ}
                for end, s, usd in bs:
                    if s != side or not (lo <= usd < hi):
                        continue
                    t_ref = end // 60_000 * 60_000 - 60_000      # last full minute inside the bin
                    ref = px.get(t_ref)
                    if ref is None:
                        continue
                    for h in HORIZ:
                        f = px.get(t_ref + h * 60_000)
                        if f is not None:
                            mv[h].append((f / ref - 1) * 100)
                n = len(mv[15])
                if not n:
                    continue
                sign = -1 if side == "long" else 1                # longs forced out: down = continued

                def rate(h):
                    return round(sum(1 for m in mv[h] if m * sign > 0) / len(mv[h]), 3) if mv[h] else None
                rows.append({"win": wn, "side": side, "bucket": name, "lo": lo, "hi": hi, "n": n,
                             "cont5": rate(5), "cont15": rate(15), "cont60": rate(60),
                             "med15": round(statistics.median(mv[15]), 3)})
    return rows


def write_js(path, asof, span, rows, note):
    obj = {"asof": asof, "span": span, "source": "xliq_events.jsonl + Binance spot 1m closes", "rows": rows, "note": note}
    text = Path(path).read_text(encoding="utf-8")
    head, rest = text.split("/*DATA*/", 1)
    tail = rest.split("/*END*/", 1)[1]
    Path(path).write_text(head + "/*DATA*/var DATA = " + json.dumps(obj) + ";/*END*/" + tail, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=str(EVENTS))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    asof = time.strftime("%Y-%m-%d", time.gmtime())
    if not Path(a.events).exists():
        write_js(a.out, asof, "none", [], "not measured: no liquidation history on disk (xliq_events.jsonl missing); needs live-aid-liq-history-log-1113")
        print("NOT MEASURED: no events file")
        return 0
    ev = load_events(a.events)
    span_h = (ev[-1][0] - ev[0][0]) / 3.6e6 if ev else 0
    if span_h < MIN_SPAN_H:
        write_js(a.out, asof, "%.1fh" % span_h, [], "not measured: only %d events over %.1f h (need >= %d h)" % (len(ev), span_h, MIN_SPAN_H))
        print("NOT MEASURED: %d events, %.1f h" % (len(ev), span_h))
        return 0
    px = closes(ev[0][0], ev[-1][0] + 61 * 60_000)
    rows = rows_from(ev, px)
    d0 = time.strftime("%Y-%m-%d", time.gmtime(ev[0][0] / 1000))
    d1 = time.strftime("%Y-%m-%d", time.gmtime(ev[-1][0] / 1000))
    span = "%s..%s (%.1f d, %d events)" % (d0, d1, span_h / 24, len(ev))
    low = [r for r in rows if r["n"] < 30]
    write_js(a.out, asof, span, rows, "measured; %d of %d rows have n < 30 (read as anecdote)" % (len(low), len(rows)))
    print("win side bucket n cont5 cont15 cont60 med15%")
    for r in rows:
        print(r["win"], r["side"], r["bucket"], r["n"], r["cont5"], r["cont15"], r["cont60"], r["med15"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
