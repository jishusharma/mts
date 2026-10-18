"""Count-only pass for the Kurisko Quad Rotation PRE_REG (card kurisko-prereg-fire-counts). DEV only (< 2024-07-01).

Events come from the kurisko module (backtest/layers/kurisko/quad_rotation.py: lines + detect), not a re-implementation.
Computed: events, distinct UTC event-days (of the event bar's close), side split, pattern stop width in bp.
Stop width (OURS, KURISKO_SPEC s5 gap 5): long = (close_t - min low over bars episode_start..t) / close_t, short =
(max high over bars episode_start..t - close_t) / close_t. It is a price-range at the event bar, not a return after it.
NO return, MFE/MAE, hit rate or any bar after an event is computed anywhere.

Usage: python count_events.py --out counts
"""
import argparse
import csv
import datetime as dt
import hashlib
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "kurisko"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "timeframe"))
import quad_rotation as qr  # noqa: E402
import tf_resample  # noqa: E402

ARCH = Path("F:/MTS/data/tom_raw/klines")
MANIFEST = ROOT / "MyTradingSys" / "research" / "gross_effect_screen_2026-10-15" / "DATA_MANIFEST.csv"
MS = 60_000
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
FEE_BP = 14.0   # round trip: fees SOURCED fees.py (2 x BINANCE_TAKER 5 bp) + 4 bp slippage OURS
TFS = {"1m": MS, "5m": 5 * MS}
REG5 = {"timeframes": {"5m": {"unit": "seconds", "seconds": 300}}}


def dev_files():
    return [ARCH / f"BTCUSDT-1m-{y}-{m:02d}.csv" for y in (2022, 2023, 2024) for m in range(1, 13)
            if (y, m) <= (2024, 6)]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_1m(files, check_sha=True):
    """[(open_time_ms, high, low, close)]; refuses any bar >= 2024-07-01 and (optionally) any sha not in DATA_MANIFEST."""
    want = {}
    if check_sha:
        for r in csv.DictReader(open(MANIFEST, newline="", encoding="utf-8")):
            want[r["file"]] = r["sha256"]
    bars = []
    for f in files:
        f = Path(f)
        if check_sha and sha256(f) != want.get(f.name):
            raise ValueError(f"sha256 of {f.name} differs from DATA_MANIFEST.csv")
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= CUTOFF_MS:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT sealed): {f}")
                bars.append((t, float(r[2]), float(r[3]), float(r[4])))
    return bars


def to_5m(bars_1m):
    """5m closed bars via tf_resample (FORMULAS 8); a bucket with a missing 1m bar is dropped (no bridging)."""
    src = [{"t": t, "o": c, "h": h, "l": l, "c": c} for t, h, l, c in bars_1m]
    return [(b["t"], b["h"], b["l"], b["c"]) for b in tf_resample.resample(src, "5m", REG5) if b["gap_count"] == 0]


def count_events(bars, tf_ms, arm, bands=None):
    lns = qr.lines(bars, tf_ms, arm, bands)
    out = []
    for e in qr.detect(lns):
        t_open, _, _, c = bars[e.t]
        win = bars[e.episode_start:e.t + 1]
        if e.side == "long":
            stop = (c - min(b[2] for b in win)) / c
        else:
            stop = (max(b[1] for b in win) - c) / c
        out.append({"side": e.side, "t": e.t, "episode_start": e.episode_start, "t_close_ms": t_open + tf_ms,
                    "stop_bp": stop * 1e4})
    return out


def summarise(rows, side):
    r = [x for x in rows if x["side"] == side]
    days = {x["t_close_ms"] // 86_400_000 for x in r}
    stops = [x["stop_bp"] for x in r]
    return {"events": len(r), "event_days": len(days),
            "median_stop_bp": statistics.median(stops) if stops else float("nan"),
            "share_stop_ge_fee": (sum(s >= FEE_BP for s in stops) / len(stops)) if stops else float("nan"),
            # per-event risk sizing (stop = 1 R): the mean fee cost is mean(FEE_BP / stop_i), not FEE_BP / median stop
            # (1/x is convex; GATE_AUDIT Q2). No outcome is read in a count pass, so there is no daily-mean R sd.
            "mean_cost_R": statistics.fmean(FEE_BP / s for s in stops) if stops else float("nan"),
            "sd_daily_mean_R": "n/a: no outcome"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "counts"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(exist_ok=True)
    files = dev_files()
    bars1 = load_1m(files)
    data = {"1m": bars1, "5m": to_5m(bars1)}
    sha = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", "MyTradingSys/backtest/layers/kurisko"],
                         capture_output=True, text=True).stdout.strip()
    rows = []
    for tf, bars in data.items():
        for arm in ("stoch", "rsi"):
            ev = count_events(bars, TFS[tf], arm)
            for side in ("long", "short"):
                s = summarise(ev, side)
                rows.append({"tf": tf, "arm": arm, "side": side, "bars": len(bars), **s})
                print(rows[-1], flush=True)
    with open(out / "counts.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["tf", "arm", "side", "bars", "events", "event_days", "median_stop_bp", "share_stop_ge_fee", "mean_cost_R",
                           "sd_daily_mean_R"],
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    (out / "run_meta.txt").write_text(f"kurisko module commit {sha}\nfiles {len(files)} bars_1m {len(bars1)} bars_5m "
                                      f"{len(data['5m'])}\n", newline="\n")


if __name__ == "__main__":
    main()
