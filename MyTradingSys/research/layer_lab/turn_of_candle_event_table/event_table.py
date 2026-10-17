"""DEV-only turn-of-candle (T055 C3) per-quarter-hour event table with forward MFE/MAE in R, both sides.

One row per entry bar with minute-of-quarter 14 (lead_minutes 1, FORMULAS.md section 16, cross-checked against
turn_of_candle_events): entry is its close, the next bar (minute 0) is the boundary bar. Forward bars are the
next 15 one-minute bars (15 is OURS). R = ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars
closed at or before the entry bar open. Gross R only; no rules.
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
LAB = HERE.parents[1]
ROOT = HERE.parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import turn_of_candle_events  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, LAB / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_guard = _load("dev_split_guard_event_table", "dev_split_guard/event_table.py")
_fwd = _load("forward_excursion_event_table", "forward_excursion/event_table.py")
dev_only, assert_dev, forward_excursion = _guard.dev_only, _guard.assert_dev, _fwd.forward_excursion

DEV_START_MS = _guard.DEV_START_MS
DEV_END_MS = _guard.DEV_END_EXCLUSIVE_MS
M1 = 60_000
H1 = 3_600_000
HORIZON = 15  # forward 1m bars, OURS
ATR_N = 14
DIR = Path("F:/MTS/data/bigtrade/cache/perp")
INPUT_1M = DIR / "klines_1m.npz"
INPUT_1H = DIR / "klines_1h.npz"
SIDES = ("long", "short")
FIELDS = ["t", "entry", "r", "ret_first_min", "long_mfe_R", "long_mae_R", "short_mfe_R", "short_mae_R",
          "bars_forward", "status"]


def _atr(hours, entry_open):
    """Plain-SMA ATR14 of the 1h bars closed at or before entry_open, or None if any needed bar is missing."""
    last = (entry_open - H1) // H1 * H1
    ts = [last - j * H1 for j in range(ATR_N, -1, -1)]
    if any(t not in hours for t in ts):
        return None
    trs = []
    for prev_t, t in zip(ts, ts[1:]):
        b, pc = hours[t], hours[prev_t]["c"]
        trs.append(max(b["h"] - b["l"], abs(b["h"] - pc), abs(b["l"] - pc)))
    return sum(trs) / ATR_N


def build_event_table(bars_1m, bars_1h):
    """One row per minute-of-quarter-14 entry bar; missing forward bars or ATR history = NOT_IN_DATA, never 0."""
    m1, _ = dev_only(bars_1m, "t")
    h1, _ = dev_only(bars_1h, "t")
    m1 = sorted({b["t"]: b for b in m1}.values(), key=lambda b: b["t"])
    hours = {b["t"]: b for b in h1}
    rows = []
    for ev in turn_of_candle_events(m1, lead_minutes=1):
        i = ev["i"]
        fwd = m1[i:i + HORIZON + 1]  # entry bar + next 15
        window = fwd
        row = {"t": m1[i]["t"], "entry": "", "r": "", "ret_first_min": "", "long_mfe_R": "", "long_mae_R": "",
               "short_mfe_R": "", "short_mae_R": "", "bars_forward": 0, "status": "NOT_IN_DATA"}
        rows.append(row)
        if len(window) < HORIZON + 1 or window[-1]["t"] - window[0]["t"] != HORIZON * M1:
            continue  # strictly increasing unique t: span == 15 minutes means no gap
        r = _atr(hours, row["t"])
        if r is None or r <= 0:
            continue
        boundary = window[1]
        row.update({"entry": window[0]["c"], "r": r, "ret_first_min": (boundary["c"] - boundary["o"]) / boundary["o"],
                    "bars_forward": HORIZON, "status": "OK"})
        for side in SIDES:
            exc = forward_excursion(window, 0, side, r, HORIZON)
            row[side + "_mfe_R"], row[side + "_mae_R"] = exc["mfe_r"], exc["mae_r"]
    assert_dev(rows, "t")
    return rows


def _load_dev(path, keys=("t", "o", "h", "l", "c")):
    """Load only bars that open inside DEV; later bars are never materialised."""
    with np.load(Path(path)) as archive:
        t = archive["t"]
        idx = np.flatnonzero((t >= DEV_START_MS) & (t < DEV_END_MS))
        cols = {k: archive[k][idx].tolist() for k in keys}
    return [{k: cols[k][j] for k in keys} for j in range(len(idx))]


def write_csv(rows, output):
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default=str(INPUT_1M), help="1m NPZ; only DEV bars are loaded")
    ap.add_argument("--input-1h", default=str(INPUT_1H), help="1h NPZ for R; only DEV bars are loaded")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    for p in (a.input, a.input_1h):
        if not Path(p).exists():
            print("NOT_IN_DATA: input not found: " + p)
            return 2
    rows = build_event_table(_load_dev(a.input), _load_dev(a.input_1h))
    write_csv(rows, a.output)
    ok = [r for r in rows if r["status"] == "OK"]
    mean = lambda k: sum(r[k] for r in ok) / len(ok) if ok else float("nan")
    print("rows=%d ok=%d not_in_data=%d long_mfe=%.4f long_mae=%.4f short_mfe=%.4f short_mae=%.4f output=%s" % (
        len(rows), len(ok), len(rows) - len(ok), mean("long_mfe_R"), mean("long_mae_R"),
        mean("short_mfe_R"), mean("short_mae_R"), a.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
