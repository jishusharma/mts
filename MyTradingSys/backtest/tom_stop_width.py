import sys
sys.dont_write_bytecode = True
"""B146: net R of the Tom core simulation by stop-width bucket and by fee-to-stop admission threshold.

Reads the 2026-10-07 verdict rows (TOM_WORK_DIR) and the 1m archive, runs the SENSITIVITY signal variants (the live rule has
0 signals), and splits by period. HOLDOUT (2026-06-26..) is NOT read: it is burned for Tom (B147).
Output: research/fast_track_2026-09-27/TOM_STOP_WIDTH_2026-10-09.md. Analysis only; nothing here is a live parameter.
Usage: python MyTradingSys/backtest/tom_stop_width.py"""
import datetime as dt
import os
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import tom_bt as T  # noqa: E402
from MyTradingSys.backtest.fees import FEES_ALL_TAKER, FEES_DERIBIT  # noqa: E402

WORK = Path(os.environ.get("TOM_WORK_DIR", r"F:\MTS\data\tom_bt_2026-10-07"))
RAW = Path(os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw")) / "klines"
OUT = ROOT / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "TOM_STOP_WIDTH_2026-10-09.md"
HOLDOUT_START = dt.datetime(2026, 6, 26, tzinfo=dt.timezone.utc).timestamp()
DEV_START = dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp()
BUCKETS = [(0.0, 0.001, "<0.10%"), (0.001, 0.002, "0.10-0.20%"), (0.002, 0.004, "0.20-0.40%"), (0.004, 9.0, ">=0.40%")]
FEE_STOP_CUTS = [None, 0.5, 0.3, 0.2, 0.1, 0.05]   # admit only if round-trip taker fee / stop distance <= cut
RT_FEE = 2 * FEES_ALL_TAKER["entry"]               # 0.0010 of price, taker both legs (worst case)


def load_rows():
    import json
    rows = []
    for p in sorted(WORK.glob("*.rows.jsonl")):
        with open(p, encoding="utf-8") as fh:
            rows.extend(json.loads(line) for line in fh)
    rows.sort(key=lambda r: r["t"])
    return rows


def period(t):
    if t >= HOLDOUT_START:
        return "holdout"
    return "dev" if t >= DEV_START else "hist"


def stop_frac(t):
    return abs(float(t["zprice"]) - float(t["stop"])) / float(t["zprice"])


def stats(ts, key):
    xs = [t[key] for t in ts]
    if not xs:
        return "n=0"
    return "n=%d mean %+.3f med %+.3f" % (len(xs), statistics.fmean(xs), statistics.median(xs))


def main():
    rows = [r for r in load_rows() if r["t"] < HOLDOUT_START]
    print("rows (holdout excluded):", len(rows), flush=True)
    b = T.load_bars_1m(RAW)
    print("bars:", b.n, flush=True)
    lines = ["# TOM stop width vs fees (B146), %s" % dt.date.today().isoformat(), "",
             "Rows: %s (holdout 2026-06-26.. excluded, burned per B147). Bars: %s. Signal variants are SENSITIVITY "
             "(watch_episode = WATCH or SETUP_FORMING, p4_episode = proof>=4); the live rule has 0 signals." % (WORK, RAW),
             "Fees: DERIBIT = maker entry/target 0, taker stop/timeout 5 bp; ALL_TAKER = 5 bp every leg. R = |entry - stop|. "
             "Trials registered here: 2 variants x 2 fee profiles x 4 buckets + 6 admission cuts (all printed, none dropped).", ""]
    for variant in ("watch_episode", "p4_episode"):
        sigs = T.signals(rows, variant)
        for fname, fees in (("DERIBIT", FEES_DERIBIT), ("ALL_TAKER", FEES_ALL_TAKER)):
            trades = [t for t in T.run_variant(sigs, b, fees=fees) if t.get("filled")
                      and t["reason"] in ("target", "stop", "timeout")]
            for t in trades:
                t["stop_frac"] = stop_frac(t)
                t["period"] = period(t["t"])
            lines += ["## %s / %s: %d filled trades" % (variant, fname, len(trades)), "",
                      "### By stop width", "", "| bucket | period | gross R | net R | fee R |", "|---|---|---|---|---|"]
            for lo, hi, name in BUCKETS:
                for per in ("hist", "dev"):
                    sel = [t for t in trades if lo <= t["stop_frac"] < hi and t["period"] == per]
                    lines.append("| %s | %s | %s | %s | %s |" % (name, per, stats(sel, "gross_r"), stats(sel, "net_r"),
                                                                  stats(sel, "fee_r")))
            lines += ["", "### Fee-to-stop admission (round trip taker fee / stop distance <= cut)", "",
                      "| cut | period | admitted | net R |", "|---|---|---|---|"]
            for cut in FEE_STOP_CUTS:
                for per in ("hist", "dev"):
                    sel = [t for t in trades if t["period"] == per and (cut is None or RT_FEE / t["stop_frac"] <= cut)]
                    lines.append("| %s | %s | %d | %s |" % ("none" if cut is None else cut, per, len(sel), stats(sel, "net_r")))
            lines.append("")
            print(variant, fname, len(trades), flush=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
