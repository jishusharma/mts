"""T6 step A: write trades.csv (one row per DD20 event trade, no pooled statistic) and coverage.json. Prints counts only.
Usage: python t6_trades.py [cache_dir]
"""
import sys
import csv
import json
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t6_core as core  # noqa: E402

CACHE = r"F:/MTS/data_cache/binance/wave2-1114"
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"
COLS = ["coin", "signal_bar_date", "signal_close_ts", "entry_ts", "entry_date", "entry_px", "stop", "exit_ts", "exit_px",
        "exit_reason", "gross", "fee", "funding", "funding_rule", "net_nofund", "net", "risk_unit", "gross_R", "net_R",
        "stop_exit_ts", "stop_exit_px", "stop_reason", "stop_gross", "stop_funding", "stop_funding_rule", "stop_net",
        "stop_R", "split", "bull", "cycle", "label", "iso_week"]


def _nice():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _d(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d")


def main(cache=CACHE):
    _nice()
    here = pathlib.Path(__file__).resolve().parent
    cache = pathlib.Path(cache)
    phase = core.load_phase_table(PHASE)
    btc = np.loadtxt(cache / "spot_1d" / "BTCUSDT.csv", delimiter=",", skiprows=1, usecols=(0, 4))
    btc_close = {_d(int(t)): float(c) for t, c in btc}
    checked, leaks = core.phase_leak_count(phase, btc_close)
    rows, cov = [], {}
    kept, dropped = [], []
    for name in core.FRESH:
        p = cache / "spot_1d" / (name + "USDT.csv")
        if not p.exists():
            dropped.append(dict(coin=name, reason="no spot_1d file", weeks=0))
            continue
        c = core.load_coin(p, name)
        info = dict(coin=name, bars=c.n, weeks=c.nw, dropped_rows_noncontiguous=c.dropped_rows, ended=c.ended,
                    first=_d(int(c.ms[0])) if c.n else None, last=_d(int(c.ms[-1])) if c.n else None)
        if c.nw < core.MIN_WEEKS:
            info["kept"] = False
            dropped.append(dict(coin=name, reason="fewer than %d complete weeks" % core.MIN_WEEKS, weeks=c.nw))
            cov[name] = info
            continue
        f = core.load_funding(cache / "funding" / (name + "USDT.csv"))
        evs = core.events_dd20(c)
        tr = core.event_trades(c, f)
        info.update(kept=True, events=len(evs), trades=len(tr), skipped_incomplete_window=len(evs) - len(tr),
                    n_prints=0 if f is None else int(len(f.ts)))
        kept.append(name)
        cov[name] = info
        for r in tr:
            lab, cyc = core.phase_tag(phase, r["entry_ts"])
            r.update(label=lab, cycle=cyc, signal_bar_date=_d(r["signal_bar_ts"]), signal_close_ts=r["entry_ts"],
                     entry_date=_d(r["entry_ts"]))
            rows.append(r)
    rows.sort(key=lambda r: (r["entry_ts"], r["coin"]))
    with open(here / "trades.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLS)
        for r in rows:
            out = []
            for k in COLS:
                v = r.get(k)
                if k in ("exit_ts", "stop_exit_ts"):
                    v = "" if v is None else v
                if isinstance(v, float):
                    v = "" if v != v else repr(round(v, 10))
                out.append(v if v is not None else "")
            w.writerow(out)
    src_overlap = [c for c in core.CANDIDATES if c in core.SOURCE_UNIVERSE]
    summary = dict(candidates=len(core.CANDIDATES), source_overlap_removed=src_overlap, fresh=len(core.FRESH),
                   kept=kept, dropped=dropped, trades=len(rows),
                   trades_dev=sum(r["split"] == "DEV" for r in rows), trades_val=sum(r["split"] == "VAL" for r in rows),
                   phase_rows_checked=checked, phase_rows_leaking=leaks,
                   funding_flat_trades=sum(r["funding_rule"] == "FLAT" for r in rows),
                   delist_exit_trades=sum(r["exit_reason"] == "DELIST-EXIT" for r in rows),
                   stop_row_missing=sum(r["stop_reason"] == "" for r in rows), per_coin=cov,
                   survivorship="hindsight candidate list; collapsed coins exit at last close (optimistic)")
    (here / "coverage.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("kept %d dropped %d trades %d DEV %d VAL %d flat-funding %d delist-exit %d phase leaks %d/%d" % (
        len(kept), len(dropped), len(rows), summary["trades_dev"], summary["trades_val"],
        summary["funding_flat_trades"], summary["delist_exit_trades"], leaks, checked))


if __name__ == "__main__":
    main(*sys.argv[1:2])
