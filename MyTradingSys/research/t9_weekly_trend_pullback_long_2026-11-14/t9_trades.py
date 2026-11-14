"""T9 step A: write trades.csv (one row per signal trade, no pooled statistic) and coverage.json. Prints counts only."""
import sys
import csv
import json
import pathlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t9_core as core  # noqa: E402

WAVE2 = r"F:/MTS/data_cache/binance/wave2-1114"
MINER = r"F:/MTS/data_cache/binance/combo-edge-miner-1114"
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"
COLS = ["coin", "w", "signal_date", "entry_ts", "entry_date", "entry_px", "stop", "risk", "exit_ts", "exit_date", "exit_px",
        "exit_reason", "days", "gross", "fee", "funding", "funding_covered", "net", "net_flat", "gross_R", "fee_R", "net_R",
        "net_flat_R", "split", "btc_state", "iso_week", "ended", "overlap"]


def main():
    cls = core.set_low_priority()
    print("priority class 0x%x (0x4000 = BELOW_NORMAL)" % (cls or 0))
    slot = core.acquire_slot("t9-trades")
    here = pathlib.Path(__file__).resolve().parent
    try:
        state = core.load_btc_state(PHASE)
        rows, cov = [], {}
        for name, (sp, fp) in core.universe(WAVE2, MINER).items():
            c = core.load_coin(sp, name)
            f = core.load_funding(fp)
            sigs = core.signals(c, state)
            tr = [t for t in (core.trade_from_signal(c, s, f) for s in sigs) if t]
            prev_exit = None
            for t in tr:
                t["overlap"] = bool(prev_exit is not None and t["entry_ts"] < prev_exit)
                prev_exit = t["exit_ts"] if prev_exit is None else max(prev_exit, t["exit_ts"])
                t["signal_date"] = core.day_str(t["signal_ms"])
                t["entry_date"] = core.day_str(t["entry_ts"])
                t["exit_date"] = core.day_str(t["exit_ts"])
                rows.append(t)
            cov[name] = dict(spot=str(sp), funding_file=pathlib.Path(fp).exists(), bars=c.n, weeks=c.nw,
                             dropped_rows_noncontiguous=c.dropped_rows, ended=c.ended, signals=len(sigs), trades=len(tr),
                             excluded_unresolved_open=len(sigs) - len(tr),
                             first=core.day_str(int(c.ms[0])) if c.n else None, last=core.day_str(int(c.ms[-1])) if c.n else None)
        rows.sort(key=lambda r: (r["entry_ts"], r["coin"]))
        with open(here / "trades.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLS)
            for r in rows:
                w.writerow([("" if isinstance(r[k], float) and r[k] != r[k] else (repr(round(r[k], 10)) if isinstance(r[k], float) else r[k]))
                            for k in COLS])
        summ = dict(universe=sorted(cov), n_coins=len(cov), trades=len(rows),
                    trades_dev=sum(r["split"] == "DEV" for r in rows), trades_val=sum(r["split"] == "VAL" for r in rows),
                    ended_trades=sum(r["ended"] for r in rows), overlap_trades=sum(r["overlap"] for r in rows),
                    funding_not_in_data=sum(not r["funding_covered"] for r in rows),
                    excluded_unresolved_open=sum(v["excluded_unresolved_open"] for v in cov.values()), per_coin=cov)
        (here / "coverage.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
        print("coins %d trades %d DEV %d VAL %d ended %d overlap %d funding NOT_IN_DATA %d excluded open %d" % (
            len(cov), len(rows), summ["trades_dev"], summ["trades_val"], summ["ended_trades"], summ["overlap_trades"],
            summ["funding_not_in_data"], summ["excluded_unresolved_open"]))
    finally:
        core.release_slot(slot)


if __name__ == "__main__":
    main()
