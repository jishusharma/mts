"""DEV-only 1h RSI 40/60 reclaim event table with 24-bar forward MFE/MAE in R.

Events come from the read-only rsi_reclaim_events on RSI14 (rsi_core): level 40 direction up (long) and
level 60 direction down (short), clearance 2.0 (OURS). One row per reclaim; dwell_below, band_bars and
depth are copied from the event (no retest filter, no bucket cut-offs). Entry = open of the bar after
the reclaim bar. R = ATR14 (plain SMA of true range, FORMULAS.md section 12) of the bars closed at that
open. Forward window = ``HORIZON`` bars starting with the entry bar (OURS). Gross R only, no rules.
Known simplification: RSI is computed over the DEV bar list as given; a data gap only turns an event
NOT_IN_DATA when it falls inside the below-run, the ATR window or the forward window.
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
LAYER_LAB = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402  read only
from MyTradingSys.backtest.layers.rsi.rsi_reclaim import rsi_reclaim_events  # noqa: E402  read only


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, LAYER_LAB / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_GUARD = _load("dev_split_guard/event_table.py", "mts_dev_split_guard_readonly")
_FWD = _load("forward_excursion/event_table.py", "mts_forward_excursion_readonly")

DEV_START_MS = _GUARD.DEV_START_MS
DEV_END_MS = _GUARD.DEV_END_EXCLUSIVE_MS
BAR_MS = 3_600_000
HORIZON = 24          # OURS
ATR_N = 14
RSI_N = 14
CLEARANCE = 2.0       # OURS
SIDES = (("long", 40.0, "up"), ("short", 60.0, "down"))
DEFAULT_INPUT = Path("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")
FIELDS = ["timestamp", "side", "dwell_below", "band_bars", "depth", "entry_t", "entry", "risk_r",
          "mfe_R", "mae_R", "bars_forward", "status"]


def atr14_at(bars, i):
    """Plain-SMA ATR14 of bars[..i]; None if fewer than 15 bars (TR needs a prior close)."""
    if i < ATR_N:
        return None
    trs = []
    for j in range(i - ATR_N + 1, i + 1):
        b, prev_c = bars[j], bars[j - 1]["c"]
        trs.append(max(b["h"] - b["l"], abs(b["h"] - prev_c), abs(b["l"] - prev_c)))
    return sum(trs) / ATR_N


def _contiguous(times, lo, hi):
    return all(times[k] - times[k - 1] == BAR_MS for k in range(lo + 1, hi + 1))


def build_event_table(bars, rsi=None, horizon=HORIZON):
    """One row per 40/60 reclaim; ``rsi`` overrides the computed RSI14 (tests only)."""
    keep = sorted({b["t"]: k for k, b in enumerate(bars)
                   if DEV_START_MS <= b["t"] < DEV_END_MS}.values(), key=lambda k: bars[k]["t"])
    data = [bars[k] for k in keep]
    if rsi is None:
        rsi = rsi_core([b["c"] for b in data], RSI_N) if len(data) > RSI_N else [None] * len(data)
    else:
        rsi = [rsi[k] for k in keep]
    times = [b["t"] for b in data]
    index = {t: k for k, t in enumerate(times)}
    events = []
    for side, level, direction in SIDES:
        for ev in rsi_reclaim_events(rsi, times, level, CLEARANCE, direction):
            events.append((side, ev))
    rows = []
    for side, ev in sorted(events, key=lambda p: (p[1]["t"], p[0])):
        i = ev["i"]
        row = {"timestamp": ev["t"], "side": side, "dwell_below": ev["dwell_below"],
               "band_bars": ev["band_bars"], "depth": ev["depth"], "entry_t": "", "entry": "",
               "risk_r": "", "mfe_R": "", "mae_R": "", "bars_forward": 0, "status": "NOT_IN_DATA"}
        rows.append(row)
        forward_bars = data[i + 1:i + 1 + horizon]
        atr = atr14_at(data, i)
        lo = min(index[ev["run_start_t"]], max(0, i - ATR_N))
        if (atr is None or atr <= 0 or len(forward_bars) < horizon
                or not _contiguous(times, lo, i + horizon)):
            continue
        entry = forward_bars[0]["o"]
        out = _FWD.forward_excursion([{"c": entry}] + forward_bars, 0, side, atr, horizon)
        if out["truncated"]:
            continue
        row.update({"entry_t": forward_bars[0]["t"], "entry": entry, "risk_r": atr,
                    "mfe_R": out["mfe_r"], "mae_R": out["mae_r"],
                    "bars_forward": len(forward_bars), "status": "OK"})
    _GUARD.assert_dev(rows, "timestamp")
    return rows


def load_dev_npz(path=DEFAULT_INPUT):
    """Load only the DEV timestamp slice; bars opening on/after 2024-07-01 are never materialised."""
    path = Path(path)
    if not path.exists():
        return None
    with np.load(path) as archive:
        idx = np.flatnonzero((archive["t"] >= DEV_START_MS) & (archive["t"] < DEV_END_MS))
        cols = {k: archive[k][idx] for k in ("t", "o", "h", "l", "c")}
    return [{"t": int(cols["t"][k]), "o": float(cols["o"][k]), "h": float(cols["h"][k]),
             "l": float(cols["l"][k]), "c": float(cols["c"][k])} for k in range(len(idx))]


def write_csv(rows, output):
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return out


def summarize(rows):
    ok = [r for r in rows if r["status"] == "OK"]
    mean = lambda key, sub: (sum(r[key] for r in sub) / len(sub)) if sub else float("nan")
    parts = ["rows=%d OK=%d NOT_IN_DATA=%d" % (len(rows), len(ok), len(rows) - len(ok))]
    for label, sub in (("all", ok), ("long", [r for r in ok if r["side"] == "long"]),
                       ("short", [r for r in ok if r["side"] == "short"])):
        parts.append("%s n=%d meanMFE_R=%.4f meanMAE_R=%.4f" % (label, len(sub), mean("mfe_R", sub), mean("mae_R", sub)))
    return "; ".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="1h NPZ; only DEV bars are loaded")
    parser.add_argument("--output", help="optional CSV path (delete after counting)")
    args = parser.parse_args()
    bars = load_dev_npz(args.input)
    if bars is None:
        print("NOT_IN_DATA: input not found: " + args.input)
        return 2
    rows = build_event_table(bars)
    if args.output:
        write_csv(rows, args.output)
    print("bars=%d %s" % (len(bars), summarize(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
