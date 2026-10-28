import sys
sys.dont_write_bytecode = True
"""Driver for the Tom core outcome backtest. Subcommands (each cached under F:\\MTS\\data\\tom_bt):
  rows    snapshots (F:\\MTS\\data\\tom_snapshots/*.jsonl.gz) -> verdict rows  (multiprocess, one task per month)
  fabio   1m archive -> Fabio kline-detector events (DESCRIPTIVE tags only)
  report  rows + fabio -> simulate, split, write TOM_CORE_BT.md + bt_runs registry
Usage: python MyTradingSys/backtest/tom_bt_run.py rows|fabio|report"""
import gzip
import json
import multiprocessing as mp
import os
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

SNAP_DIR = Path(os.environ.get("TOM_SNAP_DIR", r"F:\MTS\data\tom_snapshots"))
WORK = Path(os.environ.get("TOM_WORK_DIR", r"F:\MTS\data\tom_bt"))
RAW = Path(os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw")) / "klines"


def _rows_month(path):
    from snapshots import parse_ts
    from verdict import compute_verdict, proof_dir_of
    import tom_bt
    out = WORK / (Path(path).name.replace(".jsonl.gz", "") + ".rows.jsonl")
    if out.exists():
        return out.name, -1
    n = 0
    tmp = out.with_suffix(".part")
    with gzip.open(path, "rt", encoding="utf-8") as fh, open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for line in fh:
            s = json.loads(line)
            fo.write(json.dumps(tom_bt.snapshot_to_row(s, parse_ts, compute_verdict, proof_dir_of)) + "\n")
            n += 1
    tmp.replace(out)
    return out.name, n


def cmd_rows(procs=4):
    WORK.mkdir(parents=True, exist_ok=True)
    files = [str(p) for p in sorted(SNAP_DIR.glob("*.jsonl.gz"))
             if (SNAP_DIR / (p.name.replace(".jsonl.gz", "") + ".meta.json")).exists()]
    t0 = time.time()
    with mp.Pool(procs) as pool:
        for name, n in pool.imap_unordered(_rows_month, files):
            print(name, n, "%.0fs" % (time.time() - t0), flush=True)


def load_rows():
    rows = []
    for p in sorted(WORK.glob("*.rows.jsonl")):
        with open(p, encoding="utf-8") as fh:
            rows.extend(json.loads(l) for l in fh)
    rows.sort(key=lambda r: r["t"])
    return rows


# ------------------------------------------------------------------ fabio
FABIO_CFG = {  # frozen IS-best parameters from FABIO_L1_REPORT.md (no re-tuning here)
    "cvd_absorption": {5: dict(left=5, right=5, price_tolerance=0.001), 15: dict(left=3, right=3, price_tolerance=0.002),
                       60: dict(left=5, right=5, price_tolerance=0.0005)},
    "escalation": {5: dict(level_tolerance=0.002, aggression_k=3.0, record_lookback=50),
                   15: dict(level_tolerance=0.001, aggression_k=1.5, record_lookback=50),
                   60: dict(level_tolerance=0.002, aggression_k=1.5, record_lookback=50)},
}


def _fabio_job(args):
    det, tf_min = args
    import tom_bt
    from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import cvd_absorption_events
    from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events
    from MyTradingSys.backtest.layers.fabio import run_backtest as rb
    from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (swing_legs, build_profile, value_area,
                                                                     lowest_volume_level)
    b = tom_bt.load_bars_1m(RAW)
    bars = tom_bt.resample_dicts(b, tf_min)
    ev = []
    if det == "cvd_absorption":
        for e in cvd_absorption_events(bars, **FABIO_CFG[det][tf_min]):
            ev.append((e["t"], e["side"]))
    elif det == "escalation":
        for e in rb.chunked_events(escalation_events, bars, **FABIO_CFG[det][tf_min]):
            ev.append((e["t"], e["side"]))
    else:  # fvg_bounce: same event definition as run_backtest.run_fvg 'real' + 'bounce'
        closes = [x["c"] for x in bars]
        for leg in swing_legs(bars, left=2, right=2, use_body=True):
            a_i, b_i = min(leg["a_i"], leg["b_i"]), max(leg["a_i"], leg["b_i"])
            if b_i - a_i < 20:
                continue
            try:
                prof = build_profile(bars, a_i, b_i, n_bins=20)
                lv = lowest_volume_level(prof, value_area(prof, pct=0.70))
            except ValueError:
                continue
            mid = (lv["price_lo"] + lv["price_hi"]) / 2.0
            start = leg["confirmed_i"]
            from_above = closes[start] > mid
            for i in range(start + 1, min(start + 201, len(bars) - 1)):
                if bars[i]["l"] <= mid <= bars[i]["h"]:
                    ev.append((bars[i]["t"], "long" if from_above else "short"))
                    break
    ev.sort()
    return det, tf_min, [(t + tf_min * 60000, sd, tf_min * 60000) for t, sd in ev]


def cmd_fabio(procs=2):
    WORK.mkdir(parents=True, exist_ok=True)
    jobs = [(d, tf) for d in ("cvd_absorption", "escalation", "fvg_bounce") for tf in (5, 15, 60)]
    out = {}
    with mp.Pool(procs) as pool:
        for det, tf, ev in pool.imap_unordered(_fabio_job, jobs):
            out["%s_%dm" % (det, tf)] = ev
            print(det, tf, len(ev), flush=True)
    json.dump(out, open(WORK / "fabio_events.json", "w"), separators=(",", ":"))


if __name__ == "__main__":
    mp.freeze_support()
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "rows":
        cmd_rows(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif c == "fabio":
        cmd_fabio()
    elif c == "report":
        import tom_bt_report
        tom_bt_report.main()
    else:
        print(__doc__)
