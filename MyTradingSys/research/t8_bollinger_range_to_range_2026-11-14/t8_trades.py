"""T8 steps: `python t8_trades.py count` = signal and unit counts only (no outcome is computed);
`python t8_trades.py trades` = trades list with mirror columns (no pooled statistic), written to the data cache folder
(and copied next to this file only when under 1 MB). Reads real data: BelowNormal priority + heavy-job slot.
"""
import sys
import csv
import json
import pathlib
import shutil
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t8_core as core  # noqa: E402

OUT = pathlib.Path(r"F:/MTS/data_cache/wave3-1114/t8")
COLS = ["coin", "tf", "side", "split", "signal_date", "entry_date", "iso_week", "week", "entry_px", "stop_pct", "tgt_pct",
        "reason", "bars", "ended", "status", "gross", "fee", "fund", "fund_cov", "net_nofund", "net", "gross_R", "fee_R",
        "nofund_R", "net_R", "m_reason", "m_gross_R", "m_net_R", "label", "cycle"]


def tag_phase(rows, phase):
    for r in rows:
        lab, cyc = core.phase_tag(phase, r["entry_ms"])
        r["label"], r["cycle"] = lab, cyc
    return rows


def count_mode():
    uni, funds, cnt_days, uend = core.load_universe()
    res = dict(universe_1d=sorted(uni["1d"]), universe_4h=sorted(uni["4h"]), n_1d=len(uni["1d"]), n_4h=len(uni["4h"]),
               universe_end_utc=core.date_of(uend - core.DAY),
               dates_lt30=sum(1 for v in cnt_days.values() if v < core.MIN_ALIVE_COINS),
               first_date_ge30=core.date_of(min(d for d, v in cnt_days.items() if v >= core.MIN_ALIVE_COINS) * core.DAY),
               ended_coins=sorted({s.coin for ss in uni["1d"].values() for s in ss if s.ended}),
               segments_1d={n: len(ss) for n, ss in uni["1d"].items() if len(ss) > 1},
               segments_4h={n: len(ss) for n, ss in uni["4h"].items() if len(ss) > 1})
    for tf in ("1d", "4h"):
        c = {}
        weeks = {"DEV": set(), "VAL": set()}
        n_by = {}
        sps, tps = [], []
        for n, segs in uni[tf].items():
            for s in segs:
                for side, t, plan, last, st in core.plan_trades(s, c):
                    sp = core.split_of(int(s.ms[t]))
                    weeks[sp].add(core.week_index(int(s.ms[plan["e"]])))
                    k = "%s_%s" % (sp, "long" if side > 0 else "short")
                    n_by[k] = n_by.get(k, 0) + 1
                    sps.append(plan["stop_pct"])
                    tps.append(plan["tgt_pct"])
        res[tf] = dict(counts=c, trades_by_split_side=n_by, dev_entry_weeks=len(weeks["DEV"]),
                       val_entry_weeks=len(weeks["VAL"]),
                       val_trades=n_by.get("VAL_long", 0) + n_by.get("VAL_short", 0),
                       dev_trades=n_by.get("DEV_long", 0) + n_by.get("DEV_short", 0),
                       stop_pct_p10_p50_p90=[float(x) for x in np.percentile(sps, [10, 50, 90])],
                       target_pct_p10_p50_p90=[float(x) for x in np.percentile(tps, [10, 50, 90])],
                       fee_R_at_median_stop=core.FEE_RT / float(np.median(sps)))
    (HERE / "counts.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for tf in ("1d", "4h"):
        print(tf, json.dumps(res[tf]))
    print("coins 1d %d 4h %d; dates with <30 alive coins: %d; first date >=30: %s; ended: %s" % (
        res["n_1d"], res["n_4h"], res["dates_lt30"], res["first_date_ge30"], res["ended_coins"]))


def trades_mode():
    uni, funds, cnt_days, uend = core.load_universe()
    phase = core.load_phase_table(core.PHASE)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for tf in ("1d", "4h"):
        rows, c = core.build_trades(uni[tf], funds, tf)
        tag_phase(rows, phase)
        path = OUT / ("trades_%s.csv" % tf)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLS)
            for r in rows:
                w.writerow([("%.10g" % r[k]) if isinstance(r[k], float) else r[k] for k in COLS])
        size = path.stat().st_size
        dst = HERE / ("trades_%s.csv" % tf)
        if size < 1_000_000:
            shutil.copyfile(path, dst)
        elif dst.exists():
            dst.unlink()
        summary[tf] = dict(counts=c, rows=len(rows), csv_bytes=size, copied_to_study=bool(size < 1_000_000))
        print(tf, "trades", len(rows), "csv bytes", size, "counts", c)
    (OUT / "trades_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    print(core.set_low_priority())
    lock = core.acquire_slot("t8-" + mode)
    try:
        count_mode() if mode == "count" else trades_mode()
    finally:
        core.release_slot(lock)
