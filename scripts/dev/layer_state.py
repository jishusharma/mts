"""layer_state.py: deterministic layer state from the Bible's definitions (d-layer-bible-runtime-1104).

python scripts/dev/layer_state.py wavetrend [--tf 1m,3m,...] [--at 2026-11-04T13:00Z] [--csv bars.csv --tf 3m]

Reads ONLY the Parameters block of MyTradingSys/system/layer_bible/<family>.md and the family's tested module.
Public klines (data-api.binance.vision), closed bars only. Same Bible + same bars = same output.
Missing or short data prints NOT_IN_DATA, never a guess. No orders, no live tree, no secrets.
"""
import argparse
import csv
import datetime as dt
import json
import math
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIBLE_DIR = ROOT / "MyTradingSys" / "system" / "layer_bible"
TF_MS = {"1m": 60000, "3m": 180000, "5m": 300000, "15m": 900000, "30m": 1800000,
         "1h": 3600000, "2h": 7200000, "4h": 14400000, "1d": 86400000}


def load_params(family, bible_dir=BIBLE_DIR):
    """The one fenced ```json layer_state block of the Bible; anything else in the file is prose."""
    p = Path(bible_dir) / f"{family}.md"
    m = re.findall(r"```json layer_state\s*\n(.*?)\n```", p.read_text(encoding="utf-8"), re.S)
    if len(m) != 1:
        raise SystemExit(f"NOT_IN_DATA: {p} must hold exactly one ```json layer_state block (found {len(m)})")
    return json.loads(m[0])


def fetch_bars(symbol, tf, limit, end_ms, host="https://data-api.binance.vision"):
    u = f"{host}/api/v3/klines?symbol={symbol}&interval={tf}&limit={limit}&endTime={end_ms}"
    k = json.load(urllib.request.urlopen(u, timeout=20))
    return [(int(r[0]), float(r[2]), float(r[3]), float(r[4])) for r in k]


def read_csv(path):
    with open(path, newline="") as f:
        return [(int(r["open_time"]), float(r["high"]), float(r["low"]), float(r["close"])) for r in csv.DictReader(f)]


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def wavetrend_state(bars, tf_ms, params, at_ms=None):
    """Pure: bars (open_ms, h, l, c) -> state dict. Uses wavetrend.compute (golden-checked), then the Bible's dot rule."""
    sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "wavetrend"))
    import wavetrend as W
    band = float(params["dot_band"])
    if at_ms is not None:
        bars = [b for b in bars if b[0] + tf_ms <= at_ms]          # closed bars only
    if len(bars) <= W.WARMUP:
        return {"status": "NOT_IN_DATA", "why": f"{len(bars)} closed bars, need more than warm-up {W.WARMUP}"}
    rows = W.compute(bars, tf_ms)
    last = rows[-1]
    if math.isnan(last.wt1):
        return {"status": "NOT_IN_DATA", "why": "last bar inside warm-up or a data gap", "last_bar": iso(last.open_time)}
    crosses, dots = [], []
    basis = params.get("dot_basis", "prev_bar")                     # prev_bar = the wt30_sequence study definition
    for i, r in enumerate(rows):
        if r.event == 0 or math.isnan(r.wt1):
            continue
        kind = "up" if r.event > 0 else "down"
        ref = rows[i - 1].wt1 if basis == "prev_bar" and i > 0 else r.wt1
        valid = (not math.isnan(ref)) and ((kind == "up" and ref <= -band) or (kind == "down" and ref >= band))
        c = {"time": iso(r.open_time), "kind": kind, "wt1": round(r.wt1, 1), "valid_dot": valid,
             "dot": ("bottom" if kind == "up" else "top") if valid else None}
        crosses.append(c)
        if valid:
            dots.append(c)
    st = {"status": "OK", "last_bar": iso(last.open_time), "wt1": round(last.wt1, 1), "wt2": round(last.wt2, 1),
          "zone": last.zone, "last_cross": crosses[-1] if crosses else None,
          "last_valid_dot": dots[-1] if dots else None, "cycle": None}
    if dots:
        ld = dots[-1]
        if ld["dot"] == "bottom":
            st["cycle"] = {"state": "OPEN_UP_CYCLE", "start": ld["time"], "start_wt1": ld["wt1"], "tops_since_start": []}
        else:
            bottoms = [d for d in dots if d["dot"] == "bottom"]
            b = bottoms[-1] if bottoms else None
            tops = [d for d in dots if d["dot"] == "top" and b and d["time"] > b["time"]]
            st["cycle"] = ({"state": "COMPLETED_UP_CYCLE", "start": b["time"], "start_wt1": b["wt1"],
                            "end": ld["time"], "end_wt1": ld["wt1"], "tops_since_start": [t["time"] for t in tops],
                            "new_cycle": "none until the next valid bottom dot"} if b else
                           {"state": "TOP_DOT_NO_PRIOR_BOTTOM_IN_WINDOW", "end": ld["time"], "end_wt1": ld["wt1"]})
    return st


ADAPTERS = {"wavetrend": wavetrend_state}


def line(family, symbol, tf, st):
    if st["status"] != "OK":
        return f"{family} {symbol} {tf}: NOT_IN_DATA ({st['why']})"
    lc, ld, cy = st["last_cross"], st["last_valid_dot"], st["cycle"]
    s = f"{family} {symbol} {tf} | bar {st['last_bar']} wt1={st['wt1']} wt2={st['wt2']} zone={st['zone']}"
    if lc:
        s += f" | last cross {lc['kind']} {lc['time']} wt1={lc['wt1']} " + (f"VALID {lc['dot']} dot" if lc["valid_dot"] else "NOT a valid dot (|wt1|<band)")
    s += " | last valid dot: " + (f"{ld['dot']} {ld['time']} wt1={ld['wt1']}" if ld else "none in window")
    if cy:
        if cy["state"] == "OPEN_UP_CYCLE":
            s += f" | cycle OPEN since bottom {cy['start']} ({cy['start_wt1']})"
        elif cy["state"] == "COMPLETED_UP_CYCLE":
            s += (f" | cycle COMPLETED bottom {cy['start']} ({cy['start_wt1']}) -> top {cy['end']} ({cy['end_wt1']}); "
                  f"valid tops in between: {','.join(t[11:16] for t in cy['tops_since_start'])}; {cy['new_cycle']}")
        else:
            s += f" | {cy['state']}"
    return s


def code_sha():
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run(family, tfs, at_ms=None, csv_path=None, params=None):
    params = params or load_params(family)
    out, last_bar = [], None
    for tf in tfs:
        if csv_path:
            bars = read_csv(csv_path)
        else:
            end = at_ms or int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
            bars = fetch_bars(params["symbol"], tf, int(params["bars"]), end)
        st = ADAPTERS[family](bars, TF_MS[tf], params, at_ms)
        out.append(line(family, params["symbol"], tf, st))
        if st["status"] == "OK":
            last_bar = max(last_bar or "", st["last_bar"])
    out.append(f"STAMP bible={family}.md@{code_sha()} data@{last_bar or 'NOT_IN_DATA'} source={'csv' if csv_path else params['source']}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("family", choices=sorted(ADAPTERS))
    ap.add_argument("--tf", default=None)
    ap.add_argument("--at", default=None, help="UTC time, e.g. 2026-11-04T13:00Z (replay)")
    ap.add_argument("--csv", default=None, help="offline bars file (tests)")
    a = ap.parse_args(argv)
    params = load_params(a.family)
    tfs = (a.tf or ",".join(params["tfs"])).split(",")
    at = None
    if a.at:
        at = int(dt.datetime.strptime(a.at, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    print("\n".join(run(a.family, tfs, at, a.csv, params)))


if __name__ == "__main__":
    main()
