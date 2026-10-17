"""Count-only DEV run of trendline_core (card trendline-count-only). COUNTS ONLY.

Reads BTCUSDT-1m klines 2022-01-01..2024-06-30 (DEV, repo split SPLIT_ALIGNMENT_2026-10-17.md), aggregates to closed
1h/4h/1d bars (layers/timeframe/tf_resample via trendline_core.resample_closed), runs TrendlineDetector and counts
lines, contact episodes and breaks per TF / price arm / transform / age cap / eligibility arm / side / slope tercile.

Computes NO forward return, MFE/MAE, fee, or any bar after an event; no output column carries a price change.
The loader refuses any bar >= 2024-07-01 (VALIDATION/HOLDOUT sealed). Event day = UTC date of the event bar's OPEN time.

Usage: python count_only.py --split DEV [--out counts] [--tfs 1d,4h,1h]
"""
import argparse
import csv
import datetime as dt
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from MyTradingSys.backtest.layers.trendlines.trendline_core import TrendlineDetector, resample_closed  # noqa: E402

KLINES = Path("F:/MTS/data/tom_raw/klines")
DEV_START_MS = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
NDAYS_DEV = (dt.date(2024, 7, 1) - dt.date(2022, 1, 1)).days   # 912
TFS = ("1d", "4h", "1h")          # contract F3; 1m excluded (F3) and skipped, see PRE_REG_TRENDLINES.md
# (name, price_arm, transform, max_age): first is the primary family, the rest are sensitivity arms (contract L5/L8/P5)
CONFIGS = (("wick_log_age500", "wick", "log", 500),
           ("wick_log_noage", "wick", "log", None),
           ("wick_linear_age500", "wick", "linear", 500),
           ("close_log_age500", "close", "log", 500))
PRIMARY = "wick_log_age500"
ELIG = ("A", "B", "V")
EVENTS = ("touch", "break")
Z_POWER = 0.84
MDE_MAX_SD = 0.30      # same power rule as wavetrend PRE_REG (OURS)
FORBIDDEN_COLUMNS = ("ret", "return", "pnl", "mfe", "mae", "fee", "pct_change", "price_change", "outcome", "follow", "snapback")


def assert_no_outcome_columns(header):
    bad = [h for h in header if any(f in h.lower() for f in FORBIDDEN_COLUMNS)]
    if bad:
        raise ValueError(f"outcome-like column(s) refused in a count-only output: {bad}")


def load_dev_1m(klines=KLINES, cutoff=CUTOFF_MS):
    """1m bars as dicts {t,o,h,l,c,v} for 2022-01..2024-06 files; any bar at/after cutoff raises."""
    bars = []
    for f in sorted(Path(klines).glob("BTCUSDT-1m-????-??.csv")):
        ym = f.stem.split("-")[2:4]
        if (int(ym[0]), int(ym[1])) < (2022, 1) or (int(ym[0]), int(ym[1])) > (2024, 6):
            continue
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= cutoff:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT are sealed): {f}")
                bars.append({"t": t, "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5])})
    bars.sort(key=lambda b: b["t"])
    assert bars and bars[-1]["t"] < cutoff, "no bar at or after 2024-07-01 may be loaded"
    return bars


def day_of(t_ms):
    return dt.datetime.fromtimestamp(t_ms / 1000, tz=dt.timezone.utc).date().isoformat()


def mde_sd(n_days, m):
    """MDE in SD units: (z_{1-0.05/(2m)} + 0.84) / sqrt(n_days). Two-sided alpha 0.05 Holm over m cells, 80 % power."""
    if n_days <= 0:
        return math.inf
    nd = __import__("statistics").NormalDist()
    return (nd.inv_cdf(1 - 0.05 / (2 * m)) + Z_POWER) / math.sqrt(n_days)


def holm_family(n_days_by_cell):
    """Smallest m with #cells(MDE_m <= MDE_MAX_SD) <= m. Returns (m, carried cell ids)."""
    cells = list(n_days_by_cell)
    for m in range(1, len(cells) + 1):
        ok = [c for c in cells if mde_sd(n_days_by_cell[c], m) <= MDE_MAX_SD]
        if len(ok) <= m:
            return m, ok
    return len(cells), [c for c in cells if mde_sd(n_days_by_cell[c], len(cells)) <= MDE_MAX_SD]


def terciles(vals):
    s = sorted(vals)
    if not s:
        return (0.0, 0.0)
    return s[len(s) // 3], s[(2 * len(s)) // 3]


def tercile_of(x, edges):
    return "T1" if x <= edges[0] else ("T2" if x <= edges[1] else "T3")


def run_config(bars, tf, price_arm, transform, max_age):
    det = TrendlineDetector(tf=tf, k=3, transform=transform, price_arm=price_arm, max_age=max_age)
    det.feed(bars)
    return det


def count_detector(det, bars):
    """Return (line rows, event rows). Event rows are (tercile-free) dicts; no price columns."""
    ev_by_line = {}
    for e in det.events:
        ev_by_line.setdefault(e["line"], []).append(e)
    slopes = {s: [abs(ln["slope_atr"]) for ln in det.lines.values() if ln["side"] == s] for s in ("support", "resistance")}
    edges = {s: terciles(v) for s, v in slopes.items()}
    lines, events = [], []
    for lid, ln in det.lines.items():
        terc = tercile_of(abs(ln["slope_atr"]), edges[ln["side"]])
        evs = ev_by_line.get(lid, [])
        n_touch_all = sum(1 for e in evs if e["state"] == "touched")
        row = {"line": lid, "side": ln["side"], "tercile": terc, "n_touch_all": n_touch_all,
               "broken": ln["broken_at"] is not None, "elig": "".join(sorted(ln["eligible"]))}
        lines.append(row)
        for e in evs:
            if e["state"] == "eligible":
                arm, t0 = e["arm"], e["known_at"]
                for e2 in evs:
                    if e2["state"] == "touched" and e2["known_at"] > t0:
                        events.append((arm, "touch", ln["side"], terc, e2["bar"]))
                    elif e2["state"] == "broken" and e2["known_at"] > t0:
                        events.append((arm, "break", ln["side"], terc, e2["bar"]))
    flat = sum(1 for r in det.rejects if r["reject"] == "flat")
    return lines, events, flat, {w: sum(1 for r in det.rejects if r["reject"] == w) for w in ("tie", "flat", "penetration", "spacing")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["DEV"])
    ap.add_argument("--out", default=str(HERE / "counts"))
    ap.add_argument("--tfs", default=",".join(TFS))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    bars1m = load_dev_1m()
    print(f"loaded {len(bars1m)} 1m bars {day_of(bars1m[0]['t'])}..{day_of(bars1m[-1]['t'])}", flush=True)
    cell_rows, day_rows, quality = [], [], []
    for tf in a.tfs.split(","):
        tb = resample_closed(bars1m, tf)
        assert tb[-1]["t"] < CUTOFF_MS
        gaps = sum(b["gap_count"] for b in tb)
        quality.append(f"{tf}: {len(tb)} closed bars, {gaps} missing 1m inside buckets, first {day_of(tb[0]['t'])}, last open {day_of(tb[-1]['t'])}")
        for name, parm, tr, age in CONFIGS:
            ts = time.time()
            det = run_config(tb, tf, parm, tr, age)
            lines, events, flat, rej = count_detector(det, tb)
            quality.append(f"{tf} {name}: lines {len(lines)}, pivots {len(det.pivots)}, rejects {rej}, {time.time() - ts:.0f}s")
            print(quality[-1], flush=True)
            per = {}
            for arm, kind, side, terc, bar in events:
                d = day_of(tb[bar]["t"])
                per.setdefault((arm, kind, terc), {}).setdefault(d, {"support": 0, "resistance": 0})[side] += 1
            n_lines = {}
            for ln in lines:
                for arm in ln["elig"]:
                    n_lines.setdefault((arm, ln["tercile"]), [0, 0, 0])
                    n_lines[(arm, ln["tercile"])][0] += 1
                    n_lines[(arm, ln["tercile"])][1 if ln["side"] == "support" else 2] += 1
            for arm in ELIG:
                for terc in ("T1", "T2", "T3", "ALL"):
                    nl = n_lines.get((arm, terc), [0, 0, 0]) if terc != "ALL" else                         [sum(n_lines.get((arm, t), [0, 0, 0])[i] for t in ("T1", "T2", "T3")) for i in range(3)]
                    for kind in EVENTS:
                        if terc == "ALL":
                            days = {}
                            for t in ("T1", "T2", "T3"):
                                for d, v in per.get((arm, kind, t), {}).items():
                                    x = days.setdefault(d, {"support": 0, "resistance": 0})
                                    x["support"] += v["support"]
                                    x["resistance"] += v["resistance"]
                        else:
                            days = per.get((arm, kind, terc), {})
                        n_ev = sum(s + r for s, r in ((v["support"], v["resistance"]) for v in days.values()))
                        n_sup = sum(v["support"] for v in days.values())
                        cell_rows.append({"cell": f"{tf}|{arm}|{terc}|{kind}", "config": name, "tf": tf, "elig_arm": arm,
                                          "slope_tercile": terc, "event": kind, "eligible_lines": nl[0],
                                          "lines_support": nl[1], "lines_resistance": nl[2], "events": n_ev,
                                          "events_support": n_sup, "events_resistance": n_ev - n_sup,
                                          "event_days": len(days), "events_per_event_day": round(n_ev / len(days), 2) if days else 0})
                        if name == PRIMARY:
                            for d, v in sorted(days.items()):
                                day_rows.append({"cell": f"{tf}|{arm}|{terc}|{kind}", "date": d, "events": v["support"] + v["resistance"]})
            # line totals per config (all lines, any eligibility) incl. contact episodes and breaks
            cell_rows.append({"cell": f"{tf}|ALL|ALL|lines", "config": name, "tf": tf, "elig_arm": "ALL", "slope_tercile": "ALL",
                              "event": "lines", "eligible_lines": len(lines),
                              "lines_support": sum(1 for l in lines if l["side"] == "support"),
                              "lines_resistance": sum(1 for l in lines if l["side"] == "resistance"),
                              "events": sum(l["n_touch_all"] for l in lines), "events_support": sum(1 for l in lines if l["broken"]),
                              "events_resistance": flat, "event_days": 0, "events_per_event_day": 0})
    # power: primary config only
    # Holm family = pooled-tercile primary cells (tf x arm x event); tercile strata are descriptive, never confirmatory
    prim = [r for r in cell_rows if r["config"] == PRIMARY and r["event"] in EVENTS and r["slope_tercile"] == "ALL"]
    nd = {r["cell"]: r["event_days"] for r in prim}
    m, carried = holm_family(nd)
    for r in cell_rows:
        if r["event"] in EVENTS:
            r["mde_sd_holm_m"] = round(mde_sd(r["event_days"], m), 4) if r["event_days"] else "inf"
            r["holm_m"] = m
            r["underpowered"] = (int(r["cell"] not in carried) if r["slope_tercile"] == "ALL" else "stratum_descriptive")                 if r["config"] == PRIMARY else "n/a_sensitivity"
        else:
            r["mde_sd_holm_m"], r["holm_m"], r["underpowered"] = "", m, ""
    fields = list(cell_rows[0].keys())
    assert_no_outcome_columns(fields)
    with open(out / "CELLS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(cell_rows)
    assert_no_outcome_columns(["cell", "date", "events"])
    with open(out / "effective_n_by_day.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["cell", "date", "events"], lineterminator="\n")
        w.writeheader()
        w.writerows(day_rows)
    (out / "quality.txt").write_text("\n".join(quality + [f"holm m={m}, carried={len(carried)} of {len(prim)} primary cells",
                                                         f"total {time.time() - t0:.0f}s"]) + "\n", newline="\n")
    print(f"holm m={m} carried {len(carried)}/{len(prim)}")


if __name__ == "__main__":
    main()
