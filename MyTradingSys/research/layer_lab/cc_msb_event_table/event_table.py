"""DEV-only 1h CryptoCred market-structure-break (MSB) event table with 24-bar forward MFE/MAE in R.

Swings: find_swings(left 2, right 2, use_body True); events: classify_msb(require_prior_sequence True,
filter_range_noise False), both read only from cc_structure.py. One row per MSB event; direction up
(bull break of a lower high) = long, down (bear break of a higher low) = short. Entry = open of the bar
after the break bar. R = ATR14 (plain SMA of true range, FORMULAS.md section 12) of the bars closed at
that open. Forward window = ``HORIZON`` bars starting with the entry bar (OURS). Gross R only, no rules.
Known simplification: swings and events are computed over the DEV bar list as given; a data gap only
turns an event NOT_IN_DATA when it falls inside the swing, ATR or forward window.
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

from MyTradingSys.backtest.layers.cryptocred.cc_structure import classify_msb, find_swings  # noqa: E402  read only


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
LEFT = RIGHT = 2
DIRECTIONS = {"bull": ("up", "long"), "bear": ("down", "short")}
DEFAULT_INPUT = Path("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")
FIELDS = ["event_t", "swing_t", "direction", "side", "entry_t", "entry", "risk_r", "mfe_R", "mae_R",
          "bars_forward", "status"]


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


def build_event_table(bars, horizon=HORIZON):
    """One row per MSB event on the DEV slice of ``bars`` (dicts with t, o, h, l, c)."""
    keep = sorted({b["t"]: k for k, b in enumerate(bars)
                   if DEV_START_MS <= b["t"] < DEV_END_MS}.values(), key=lambda k: bars[k]["t"])
    data = [bars[k] for k in keep]
    if len(data) < LEFT + RIGHT + 1:
        return []
    swings = find_swings(data, LEFT, RIGHT, True)
    if not swings:
        return []
    events = classify_msb(data, swings, True, False)
    times = [b["t"] for b in data]
    rows = []
    for ev in events:
        k = ev["i"]
        direction, side = DIRECTIONS[ev["direction"]]
        row = {"event_t": ev["t"], "swing_t": times[ev["broken_swing_i"]], "direction": direction,
               "side": side, "entry_t": "", "entry": "", "risk_r": "", "mfe_R": "", "mae_R": "",
               "bars_forward": 0, "status": "NOT_IN_DATA"}
        rows.append(row)
        forward_bars = data[k + 1:k + 1 + horizon]
        atr = atr14_at(data, k)
        lo = min(ev["broken_swing_i"] - LEFT, k - ATR_N)
        if (atr is None or atr <= 0 or len(forward_bars) < horizon
                or not _contiguous(times, max(0, lo), k + horizon)):
            continue
        entry = forward_bars[0]["o"]
        out = _FWD.forward_excursion([{"c": entry}] + forward_bars, 0, side, atr, horizon)
        if out["truncated"]:
            continue
        row.update({"entry_t": forward_bars[0]["t"], "entry": entry, "risk_r": atr,
                    "mfe_R": out["mfe_r"], "mae_R": out["mae_r"],
                    "bars_forward": len(forward_bars), "status": "OK"})
    _GUARD.assert_dev(rows, "event_t")
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
    for label, sub in (("all", ok), ("up/long", [r for r in ok if r["side"] == "long"]),
                       ("down/short", [r for r in ok if r["side"] == "short"])):
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
