"""DEV-only 5m session-momentum (T055 C2) daily event table with forward MFE/MAE in R.

One row per UTC day with an event. Side is the sign of the first-30-minute return, entry is the close of the
6th 5m bar (as session_momentum_events does), forward bars run from the next bar to 24:00 UTC of that day
(session end, OURS). R = ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at or
before the entry bar open. Gross R only; no rules.
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
from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events  # noqa: E402


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
DAY = 86_400_000
M5 = 300_000
H1 = 3_600_000
BARS_PER_DAY = DAY // M5
ENTRY_K = 5  # 6th bar: its close is S + 30 min
ATR_N = 14
DIR = Path("F:/MTS/data/bigtrade/cache/perp")
INPUT_5M = DIR / "klines_5m.npz"
INPUT_1H = DIR / "klines_1h.npz"
FIELDS = ["day", "t", "side", "r_first", "entry", "r", "mfe_R", "mae_R", "bars_forward", "status"]


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


def build_event_table(bars_5m, bars_1h):
    """Rows for DEV days; days with an event but incomplete data get status NOT_IN_DATA (blank numbers, never 0)."""
    m5, _ = dev_only(bars_5m, "t")
    h1, _ = dev_only(bars_1h, "t")
    m5 = sorted({b["t"]: b for b in m5}.values(), key=lambda b: b["t"])
    if not m5:
        return []
    hours = {b["t"]: b for b in h1}
    events = {m5[e["i"]]["t"] // DAY: e for e in session_momentum_events(
        m5, bar_min=5, session_start_min=0, first_min=30, entry_min=30, min_abs=0.0)}
    by_day = {}
    for b in m5:
        by_day.setdefault(b["t"] // DAY, {})[b["t"]] = b
    rows = []
    for day in sorted(by_day):
        S = day * DAY
        have = by_day[day]
        ev = events.get(day)
        first_ok = all(S + k * M5 in have for k in range(ENTRY_K + 1))
        if ev is None and first_ok:
            continue
        row = {"day": day, "t": S + ENTRY_K * M5, "side": ev["side"] if ev else "",
               "r_first": ev["r_first"] if ev else "", "entry": "", "r": "", "mfe_R": "", "mae_R": "",
               "bars_forward": 0, "status": "NOT_IN_DATA"}
        rows.append(row)
        if ev is None or not first_ok or not all(S + k * M5 in have for k in range(BARS_PER_DAY)):
            continue
        r = _atr(hours, row["t"])
        if r is None or r <= 0:
            continue
        window = [have[S + k * M5] for k in range(ENTRY_K, BARS_PER_DAY)]
        exc = forward_excursion(window, 0, ev["side"], r, len(window) - 1)
        row.update({"entry": window[0]["c"], "r": r, "mfe_R": exc["mfe_r"], "mae_R": exc["mae_r"],
                    "bars_forward": len(window) - 1, "status": "OK"})
    assert_dev(rows, "t")
    return rows


def _load_dev(path, keys=("t", "o", "h", "l", "c")):
    """Load only bars that open inside DEV; later bars are never materialised."""
    with np.load(Path(path)) as archive:
        t = archive["t"]
        idx = np.flatnonzero((t >= DEV_START_MS) & (t < DEV_END_MS))
        cols = {k: archive[k][idx] for k in keys}
    return [{k: (int(cols[k][j]) if k == "t" else float(cols[k][j])) for k in keys} for j in range(len(idx))]


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
    ap.add_argument("--input", default=str(INPUT_5M), help="5m NPZ; only DEV bars are loaded")
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
    print("rows=%d ok=%d not_in_data=%d long=%d short=%d mean_MFE_R=%.4f mean_MAE_R=%.4f output=%s" % (
        len(rows), len(ok), len(rows) - len(ok), sum(r["side"] == "long" for r in ok),
        sum(r["side"] == "short" for r in ok), mean("mfe_R"), mean("mae_R"), a.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
