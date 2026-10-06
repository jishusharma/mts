"""
MyTradingSys/backtest/layers/fabio/of_backfill.py - TF3: backfill finished days of live-schema order-flow bars.

Why: the live writer (orderflow_live.py) started 2026-10-03 03:01Z; the offline archive ends 2026-09-28. The days between
have no bars, so a Fabio v3 NY window on those days could never be built. Source = Binance USD-M aggTrades daily archive
(data.binance.vision, same venue as the offline archive), run through the offline code path (orderflow_bars.process_day)
in a scratch dir, then written as <live>/YYYY-MM-DD.csv + <live>/_qhist/YYYY-MM-DD.json.

Collection-only: never touches <live>/_state.json (the live writer's resume cursor), never rewrites an existing day, and
refuses any day >= the day the live writer owns (state "day" or the earliest live CSV). Safe while the writer runs.

Run: python -m MyTradingSys.backtest.layers.fabio.of_backfill --start 2026-09-29 --end 2026-10-02
"""
import argparse
import json
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob
from MyTradingSys.backtest.layers.fabio import orderflow_live as ol


def live_owned_from(live_dir):
    """First day the live writer owns = the day in its _state.json (it appends to that day), or None. Earlier days are
    free; an existing CSV is protected separately in backfill_day."""
    day = ol.load_state(live_dir).get("day")
    return date.fromisoformat(day) if day else None


def stage_hist(stage, live_dir, offline_hist, day):
    """Copy the prior 30 days' histograms (live + offline) into <stage>/_qhist so process_day sees the same causal window."""
    dst = Path(stage) / "_qhist"
    dst.mkdir(parents=True, exist_ok=True)
    for k in range(1, 31):
        name = f"{(day - timedelta(days=k)).isoformat()}.json"
        if (dst / name).exists():
            continue
        for src in (Path(live_dir) / "_qhist", Path(offline_hist)):
            if (src / name).exists():
                shutil.copyfile(src / name, dst / name)
                break


def backfill_day(day, raw_dir, stage, live_dir, offline_hist=ol.OFFLINE_HIST):
    """-> 'skip: ...' | 'ok rows=N thr_days=K' | process_day's failure text. Writes nothing on a failure."""
    live_dir = Path(live_dir)
    owned = live_owned_from(live_dir)
    if owned is not None and day >= owned:
        return f"skip: live writer owns {owned.isoformat()} onward"
    if (live_dir / f"{day.isoformat()}.csv").exists():
        return "skip: exists"
    stage_hist(stage, live_dir, offline_hist, day)
    res = ob.process_day(day, raw_dir, stage)
    if not res.startswith("ok"):
        return res
    rows = ob.load_days(stage, day, day)
    if not rows or any(r["thr_days"] == 0 for r in rows):
        return "refused: thr_days 0 (no causal thresholds)"
    live_dir.mkdir(parents=True, exist_ok=True)
    ol.append_rows(live_dir, day, rows)
    hist = {int(k): v for k, v in json.loads(
        (Path(stage) / "_qhist" / f"{day.isoformat()}.json").read_text(encoding="utf-8")).items()}
    ol.write_hist(live_dir, day, hist)
    return f"ok rows={len(rows)} thr_days={rows[0]['thr_days']}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--live", default=str(ol.DEFAULT_OUT))
    ap.add_argument("--raw", default=None, help="raw aggTrades dir (default: scratch, removed after)")
    a = ap.parse_args(argv)
    scratch = Path(tempfile.mkdtemp(prefix="of_backfill_"))
    raw = Path(a.raw) if a.raw else scratch / "raw"
    stage = scratch / "stage"
    stage.mkdir(parents=True)
    d, end, bad = date.fromisoformat(a.start), date.fromisoformat(a.end), 0
    try:
        while d <= end:
            res = backfill_day(d, raw, stage, a.live)
            print(d.isoformat(), res, flush=True)
            bad += not (res.startswith("ok") or res.startswith("skip"))
            d += timedelta(days=1)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
