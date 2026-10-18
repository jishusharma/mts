"""DEV-only 1h Fabio volume-profile LVN touch event table with forward MFE/MAE in R (both sides).

For each swing leg (swing_legs left 2 / right 2 / body, as fabio_volume_fvg) the profile over a_i..b_i
(20 bins) gives the value area (70%) and its lowest-volume bin; the level is that bin's midpoint (OURS).
One row at the FIRST bar after confirmed_i, within 48 bars (OURS), whose high-low range touches the level;
no row if a newer leg is confirmed before the touch. The module states no direction, so long and short
excursions are both recorded. Entry = open of the bar after the touch bar; horizon 24 bars from that open
(OURS, the entry bar included). R = ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars
closed at the entry bar open. Gross R only; no rules.
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
from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (  # noqa: E402
    build_profile, lowest_volume_level, swing_legs, value_area)


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
H1 = 3_600_000
ATR_N = 14
TOUCH_WINDOW = 48  # bars after confirmed_i (OURS)
HORIZON = 24       # bars from the entry bar open (OURS)
N_BINS, VA_PCT, SWING_LR = 20, 0.70, 2
INPUT_1H = Path("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")
FIELDS = ["leg_a_i", "leg_b_i", "confirmed_i", "level", "touch_t", "t", "entry", "r",
          "long_mfe_R", "long_mae_R", "short_mfe_R", "short_mae_R", "bars_forward", "status"]


def _contiguous(bars, lo, hi):
    if lo < 0 or hi >= len(bars):
        return False
    times = [b["t"] for b in bars[lo:hi + 1]]
    return all(b - a == H1 for a, b in zip(times, times[1:]))


def _atr(bars, last):
    """Plain-SMA ATR14 of bars[..last], or None if history is short or has a gap."""
    if not _contiguous(bars, last - ATR_N, last):
        return None
    trs = []
    for j in range(last - ATR_N + 1, last + 1):
        h, l, pc = bars[j]["h"], bars[j]["l"], bars[j - 1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs) / ATR_N


def _blank(leg, t, level="", touch_t=""):
    return {"leg_a_i": leg["a_i"], "leg_b_i": leg["b_i"], "confirmed_i": leg["confirmed_i"], "level": level,
            "touch_t": touch_t, "t": t, "entry": "", "r": "", "long_mfe_R": "", "long_mae_R": "",
            "short_mfe_R": "", "short_mae_R": "", "bars_forward": 0, "status": "NOT_IN_DATA"}


def build_event_table(bars_1h):
    """Rows for DEV legs; a leg with a touch but incomplete data gets NOT_IN_DATA (blank numbers, never 0)."""
    bars, _ = dev_only(bars_1h, "t")
    bars = sorted({b["t"]: b for b in bars}.values(), key=lambda b: b["t"])
    if len(bars) < 2 * SWING_LR + 2:
        return []
    legs = swing_legs(bars, left=SWING_LR, right=SWING_LR, use_body=True)
    rows = []
    for n, leg in enumerate(legs):
        conf = leg["confirmed_i"]
        if conf >= len(bars):
            continue
        try:
            prof = build_profile(bars, leg["a_i"], leg["b_i"], N_BINS)
            lvn = lowest_volume_level(prof, value_area(prof, VA_PCT))
        except ValueError:
            rows.append(_blank(leg, bars[conf]["t"]))
            continue
        level = (lvn["price_lo"] + lvn["price_hi"]) / 2.0
        later = legs[n:][1:]
        newer = later[0]["confirmed_i"] if later else None
        for k in range(conf + 1, min(conf + TOUCH_WINDOW, len(bars) - 1) + 1):
            if newer is not None and newer < k:
                break
            if bars[k]["l"] <= level <= bars[k]["h"]:
                rows.append(_row(bars, leg, level, k))
                break
    assert_dev(rows, "t")
    return rows


def _row(bars, leg, level, k):
    touch_t = bars[k]["t"]
    row = _blank(leg, touch_t + H1, level, touch_t)
    if k + HORIZON >= len(bars) or not _contiguous(bars, k, k + HORIZON):
        return row
    r = _atr(bars, k)
    if r is None or r <= 0:
        return row
    fwd = bars[k:][1:HORIZON + 1]  # entry bar first
    entry = fwd[0]["o"]
    window = [{"o": entry, "h": entry, "l": entry, "c": entry}] + fwd
    lng = forward_excursion(window, 0, "long", r, HORIZON)
    sht = forward_excursion(window, 0, "short", r, HORIZON)
    row.update({"t": fwd[0]["t"], "entry": entry, "r": r, "long_mfe_R": lng["mfe_r"],
                "long_mae_R": lng["mae_r"], "short_mfe_R": sht["mfe_r"], "short_mae_R": sht["mae_r"],
                "bars_forward": HORIZON, "status": "OK"})
    return row


def _load_dev(path, keys=("t", "o", "h", "l", "c", "v")):
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
    ap.add_argument("--input", default=str(INPUT_1H), help="1h NPZ; only DEV bars are loaded")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    if not Path(a.input).exists():
        print("NOT_IN_DATA: input not found: " + a.input)
        return 2
    rows = build_event_table(_load_dev(a.input))
    write_csv(rows, a.output)
    ok = [r for r in rows if r["status"] == "OK"]
    mean = lambda k: sum(r[k] for r in ok) / len(ok) if ok else float("nan")
    print("rows=%d ok=%d not_in_data=%d long_mfe=%.4f long_mae=%.4f short_mfe=%.4f short_mae=%.4f output=%s" % (
        len(rows), len(ok), len(rows) - len(ok), mean("long_mfe_R"), mean("long_mae_R"),
        mean("short_mfe_R"), mean("short_mae_R"), a.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
