"""US cash-open window sizes (BTCUSDT 1m, Binance USD-M, 2022-01..last file). Descriptive, no fees, no signal.

Definitions (OURS, fixed before the run):
- Open O = 09:30 America/New_York on Mon-Fri (SOURCED: NYSE hours); holidays not removed.
- pre60 = 60 bars before O; data slot = the bar at O-60 (08:30 ET, US data releases).
- first30 = bars O..O+29; us4h = bars O..O+239.
- Range = (max high - min low) / open price of O, in %.
- Drift pre60 = close(O-1)/open(O-60) - 1 in %; sign agreement = sign(drift pre60) == sign(close(O+239) - open(O)).
- Two-sided = in us4h price traded at least +0.5 % AND at least -0.5 % from open(O).
- Run: python us_window_stats.py  (prints a JSON summary; the numbers in DESIGN.md come from one run of this file).
"""
import sys
sys.dont_write_bytecode = True
import csv, glob, json, statistics
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SRC = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv"
NY = ZoneInfo("America/New_York")


def load():
    bars = {}
    for f in sorted(glob.glob(SRC)):
        with open(f, newline="") as fh:
            r = csv.reader(fh)
            for row in r:
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                if t > 10**14:      # microsecond files
                    t //= 1000
                bars[t // 60000] = (float(row[1]), float(row[2]), float(row[3]), float(row[4]))
    return bars


def q(xs, p):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(p * len(xs)))], 3)


def main():
    bars = load()
    mins = sorted(bars)
    d0 = datetime.fromtimestamp(mins[0] * 60, timezone.utc).date()
    d1 = datetime.fromtimestamp(mins[-1] * 60, timezone.utc).date()
    out = {"from": str(d0), "to": str(d1)}
    rows = {"dst": [], "std": []}
    day = d0.toordinal()
    while day <= d1.toordinal():
        d = datetime.fromordinal(day).date()
        day += 1
        if d.weekday() >= 5:
            continue
        o_local = datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY)
        o = int(o_local.timestamp()) // 60
        need = range(o - 60, o + 240)
        if any(m not in bars for m in need):
            continue
        op = bars[o][0]
        def rng(a, b):
            return (max(bars[m][1] for m in range(a, b)) - min(bars[m][2] for m in range(a, b))) / op * 100
        hi4 = (max(bars[m][1] for m in range(o, o + 240)) / op - 1) * 100
        lo4 = (min(bars[m][2] for m in range(o, o + 240)) / op - 1) * 100
        drift = (bars[o - 1][3] / bars[o - 60][0] - 1) * 100
        us_ret = bars[o + 239][3] - op
        slot = (bars[o - 60][1] - bars[o - 60][2]) / op * 100
        key = "dst" if o_local.utcoffset().total_seconds() == -4 * 3600 else "std"
        rows[key].append(dict(pre60=rng(o - 60, o), first30=rng(o, o + 30), us4h=rng(o, o + 240),
                              up=hi4, dn=-lo4, drift=drift, agree=(drift > 0) == (us_ret > 0) if drift and us_ret else None,
                              two=hi4 >= 0.5 and lo4 <= -0.5, slot=slot))
    allr = rows["dst"] + rows["std"]
    for name, rs in (("all", allr), ("dst", rows["dst"]), ("std", rows["std"])):
        ag = [r["agree"] for r in rs if r["agree"] is not None]
        out[name] = {
            "n": len(rs),
            "pre60_range_pct_median": q([r["pre60"] for r in rs], .5),
            "first30_range_pct_median": q([r["first30"] for r in rs], .5),
            "us4h_range_pct_p25_p50_p75_p90": [q([r["us4h"] for r in rs], p) for p in (.25, .5, .75, .9)],
            "us4h_max_up_from_open_p50_p90": [q([r["up"] for r in rs], p) for p in (.5, .9)],
            "us4h_max_down_from_open_p50_p90": [q([r["dn"] for r in rs], p) for p in (.5, .9)],
            "first30_share_of_4h_range_median": q([r["first30"] / r["us4h"] for r in rs if r["us4h"]], .5),
            "two_sided_0p5_pct_share": round(sum(r["two"] for r in rs) / len(rs), 3),
            "pre60_drift_sign_matches_us4h_sign": round(sum(ag) / len(ag), 3),
            "data_slot_bar_range_pct_median": q([r["slot"] for r in rs], .5),
            "one_way_move_ge_2pct_share": round(sum(max(r["up"], r["dn"]) >= 2 for r in rs) / len(rs), 3),
        }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
