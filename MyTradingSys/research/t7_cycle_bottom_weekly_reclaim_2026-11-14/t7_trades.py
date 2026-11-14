"""T7 step A: write trades.csv (one row per event trade, no pooled statistic) and coverage.json. Prints counts only."""
import sys
import csv
import json
import pathlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t7_core as core  # noqa: E402

COLS = ["coin", "seg", "signal_ts", "signal_date", "entry_ts", "entry_date", "d0", "entry_px", "stop", "risk",
        "exit_ts", "exit_px", "exit_reason", "days", "gross", "fee", "funding", "funding_rule", "net_nofund", "net",
        "gross_R", "net_R", "fee_R", "split", "iso_week", "week_i", "ended", "cycle"]


def main():
    print(core.set_below_normal())
    lk = core.acquire_slot("t7_trades")
    try:
        here = pathlib.Path(__file__).resolve().parent
        state = core.load_state_table("F:/MTS/data_cache/mts_brains/phase_daily.csv")
        rows, cov = [], {}
        for coin, sp, fp in core.universe():
            fund = core.load_funding(fp)
            for s in core.load_segments(sp, coin):
                tr = core.event_trades(s, fund)
                for t in tr:
                    t["signal_date"] = core.date_of(t["signal_ts"])
                    t["entry_date"] = core.date_of(t["entry_ts"])
                    t["cycle"] = state.get(t["entry_date"], "NA")
                    rows.append(t)
                cov["%s#%d" % (coin, s.seg_id)] = dict(bars=s.n, ended=s.ended, events=len(core.events(s)), trades=len(tr),
                                                      first=core.date_of(s.ms[0]), last=core.date_of(s.ms[-1]),
                                                      funding_prints=0 if fund is None else int(len(fund.ts)))
        rows.sort(key=lambda r: (r["entry_ts"], r["coin"]))
        with open(here / "trades.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLS)
            for r in rows:
                out = []
                for k in COLS:
                    v = r.get(k)
                    out.append(repr(round(v, 10)) if isinstance(v, float) else v)
                w.writerow(out)
        (here / "coverage.json").write_text(json.dumps(dict(trades=len(rows), per_coin=cov), indent=1), encoding="utf-8")
        print("trades", len(rows), "DEV", sum(r["split"] == "DEV" for r in rows), "VAL", sum(r["split"] == "VAL" for r in rows))
    finally:
        core.release_slot(lk)


if __name__ == "__main__":
    main()
