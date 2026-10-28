"""Count-only DEV run of trendline_core (cards trendline-count-only, trendline-count-only-v2). COUNTS ONLY.

v2 (2026-10-28, audit gap 4): first_touch (one per eligible line) beside all_touches, retested/reclaimed counts, causal
(expanding) slope terciles, sha256 digest of every kline file read, Holm m = DEV variants already read (verdicts.py) + carried.

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
import hashlib
import io
import math
import re
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
EVENTS = ("first_touch", "all_touches", "break", "retested", "reclaimed")
FAMILY_EVENTS = ("first_touch", "break", "retested", "reclaimed")   # all_touches repeats surviving lines: descriptive only (OURS)
MIN_HISTORY = 9        # earlier same-side lines needed before a tercile is assigned, else T0 warm-up (OURS)
Z_POWER = 0.84
MDE_MAX_SD = 0.30      # same power rule as wavetrend PRE_REG (OURS)
FORBIDDEN_TOKENS = ("ret", "return", "pnl", "mfe", "mae", "fee", "outcome", "follow", "snapback")   # whole name tokens: "retested" is a count
FORBIDDEN_PHRASES = ("pct_change", "price_change")


def assert_no_outcome_columns(header):
    bad = [h for h in header if any(t in FORBIDDEN_TOKENS for t in re.split(r"[^a-z0-9]+", h.lower()))
           or any(f in h.lower() for f in FORBIDDEN_PHRASES)]
    if bad:
        raise ValueError(f"outcome-like column(s) refused in a count-only output: {bad}")


def load_dev_1m(klines=KLINES, cutoff=CUTOFF_MS, digests=None):
    """1m bars as dicts {t,o,h,l,c,v} for 2022-01..2024-06 files; any bar at/after cutoff raises.
    digests (list) gets {file, bytes, sha256} of the exact bytes parsed, one per file read."""
    bars = []
    for f in sorted(Path(klines).glob("BTCUSDT-1m-????-??.csv")):
        ym = f.stem.split("-")[2:4]
        if (int(ym[0]), int(ym[1])) < (2022, 1) or (int(ym[0]), int(ym[1])) > (2024, 6):
            continue
        raw = f.read_bytes()
        if digests is not None:
            digests.append({"file": f.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        with io.StringIO(raw.decode("utf-8"), newline="") as fh:
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


def holm_family(n_days_by_cell, base_m=0):
    """Smallest k with #cells(MDE at m=base_m+k <= floor) <= k. base_m = variants already read on DEV (verdicts.py count).
    Returns (m = base_m + k, carried cell ids). base_m=0 is the v1 rule."""
    cells = list(n_days_by_cell)
    for k in range(1, len(cells) + 1):
        ok = [c for c in cells if mde_sd(n_days_by_cell[c], base_m + k) <= MDE_MAX_SD]
        if len(ok) <= k:
            return base_m + k, ok
    m = base_m + len(cells)
    return m, [c for c in cells if mde_sd(n_days_by_cell[c], m) <= MDE_MAX_SD]


def terciles(vals):
    s = sorted(vals)
    if not s:
        return (0.0, 0.0)
    return s[len(s) // 3], s[(2 * len(s)) // 3]


def tercile_of(x, edges):
    return "T1" if x <= edges[0] else ("T2" if x <= edges[1] else "T3")


def causal_terciles(lines):
    """{line id: T0|T1|T2|T3}. A line's tercile uses only same-side lines proposed STRICTLY earlier (available_at),
    expanding window; fewer than MIN_HISTORY earlier lines -> T0 (warm-up). Appending later lines never changes it."""
    out = {}
    for side in ("support", "resistance"):
        ls = sorted((l for l in lines if l["side"] == side), key=lambda l: l["available_at"])
        hist, i = [], 0
        while i < len(ls):
            j = i
            while j < len(ls) and ls[j]["available_at"] == ls[i]["available_at"]:
                j += 1
            edges = terciles(hist) if len(hist) >= MIN_HISTORY else None
            for l in ls[i:j]:
                out[l["id"]] = tercile_of(abs(l["slope_atr"]), edges) if edges else "T0"
            hist.extend(abs(l["slope_atr"]) for l in ls[i:j])
            i = j
    return out


def run_config(bars, tf, price_arm, transform, max_age):
    det = TrendlineDetector(tf=tf, k=3, transform=transform, price_arm=price_arm, max_age=max_age)
    det.feed(bars)
    return det


def count_detector(det, bars):
    """Return (line rows, events, flat, rejects). events = (arm, kind, side, tercile, bar): kind first_touch (first contact
    after the line is eligible in that arm), all_touches (every contact after eligibility), break (first close beyond),
    retested / reclaimed (after a break that was itself counted in that arm). No price columns."""
    ev_by_line = {}
    for e in det.events:
        ev_by_line.setdefault(e["line"], []).append(e)
    terc_of = causal_terciles(list(det.lines.values()))
    lines, events = [], []
    for lid, ln in det.lines.items():
        terc = terc_of[lid]
        evs = ev_by_line.get(lid, [])
        n_touch_all = sum(1 for e in evs if e["state"] == "touched")
        lines.append({"line": lid, "side": ln["side"], "tercile": terc, "n_touch_all": n_touch_all,
                      "broken": ln["broken_at"] is not None, "elig": "".join(sorted(ln["eligible"]))})
        for e in evs:
            if e["state"] != "eligible":
                continue
            arm, t0 = e["arm"], e["known_at"]
            first_done, broke = False, False
            for e2 in evs:
                if e2["known_at"] <= t0:
                    continue
                st = e2["state"]
                if st == "touched":
                    if not first_done:
                        first_done = True
                        events.append((arm, "first_touch", ln["side"], terc, e2["bar"]))
                    events.append((arm, "all_touches", ln["side"], terc, e2["bar"]))
                elif st == "broken":
                    broke = True
                    events.append((arm, "break", ln["side"], terc, e2["bar"]))
                elif st in ("retested", "reclaimed") and broke:
                    events.append((arm, st, ln["side"], terc, e2["bar"]))
    flat = sum(1 for r in det.rejects if r["reject"] == "flat")
    return lines, events, flat, {w: sum(1 for r in det.rejects if r["reject"] == w) for w in ("tie", "flat", "penetration", "spacing")}


def dev_variants_read():
    """Distinct (study, arm) variants already read on DEV = base for Holm m (scripts/dev/verdicts.py count; same value as
    prereg_gate.py --m auto before its --new-cells)."""
    sys.path.insert(0, str(HERE.parents[2] / "scripts" / "dev"))
    import verdicts
    seen, _ = verdicts.count_variants(verdicts.CSV_PATH, "DEV")
    return len(seen)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["DEV"])
    ap.add_argument("--out", default=str(HERE / "counts"))
    ap.add_argument("--tfs", default=",".join(TFS))
    ap.add_argument("--base-m", default="auto", help="DEV variants already read; 'auto' = verdicts.py count --split DEV")
    a = ap.parse_args(argv)
    base_m = dev_variants_read() if a.base_m == "auto" else int(a.base_m)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    digests = []
    bars1m = load_dev_1m(digests=digests)
    print(f"loaded {len(bars1m)} 1m bars {day_of(bars1m[0]['t'])}..{day_of(bars1m[-1]['t'])}, {len(digests)} files", flush=True)
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
            per = {}      # (arm, kind, tercile) -> day -> {support, resistance}
            for arm, kind, side, terc, bar in events:
                per.setdefault((arm, kind, terc), {}).setdefault(day_of(tb[bar]["t"]), {"support": 0, "resistance": 0})[side] += 1
            n_lines = {}  # (arm, tercile) -> [all, support, resistance]
            for ln in lines:
                for arm in ln["elig"]:
                    for key in ((arm, ln["tercile"]), (arm, "ALL")):
                        x = n_lines.setdefault(key, [0, 0, 0])
                        x[0] += 1
                        x[1 if ln["side"] == "support" else 2] += 1
            for arm in ELIG:
                for terc in ("T0", "T1", "T2", "T3", "ALL"):
                    nl = n_lines.get((arm, terc), [0, 0, 0])
                    if terc == "T0" and nl[0] == 0:
                        continue
                    row = {"cell": f"{tf}|{arm}|{terc}", "config": name, "tf": tf, "elig_arm": arm, "slope_tercile": terc,
                           "eligible_lines": nl[0], "lines_support": nl[1], "lines_resistance": nl[2]}
                    for kind in EVENTS:
                        if terc == "ALL":
                            days = {}
                            for t in ("T0", "T1", "T2", "T3"):
                                for d, v in per.get((arm, kind, t), {}).items():
                                    x = days.setdefault(d, {"support": 0, "resistance": 0})
                                    x["support"] += v["support"]
                                    x["resistance"] += v["resistance"]
                        else:
                            days = per.get((arm, kind, terc), {})
                        row[kind] = sum(v["support"] + v["resistance"] for v in days.values())
                        row[kind + "_days"] = len(days)
                        if name == PRIMARY:
                            for d, v in sorted(days.items()):
                                day_rows.append({"cell": f"{tf}|{arm}|{terc}|{kind}", "date": d, "events": v["support"] + v["resistance"]})
                    cell_rows.append(row)
            # line totals per config (all lines, any eligibility): broken lines, contact episodes, flat anchor pairs
            cell_rows.append({"cell": f"{tf}|ALL|ALL", "config": name, "tf": tf, "elig_arm": "ALL", "slope_tercile": "ALL",
                              "eligible_lines": len(lines),
                              "lines_support": sum(1 for l in lines if l["side"] == "support"),
                              "lines_resistance": sum(1 for l in lines if l["side"] == "resistance"),
                              "all_touches": sum(l["n_touch_all"] for l in lines), "broken_lines": sum(1 for l in lines if l["broken"]),
                              "flat_pairs": flat})
    # power: primary config, pooled-tercile cells (tf x arm x kind in FAMILY_EVENTS); strata and all_touches are descriptive
    nd = {f"{r['tf']}|{r['elig_arm']}|{k}": r[k + "_days"] for r in cell_rows
          if r["config"] == PRIMARY and r["slope_tercile"] == "ALL" and r["elig_arm"] in ELIG for k in FAMILY_EVENTS}
    m, carried = holm_family(nd, base_m)
    for r in cell_rows:
        r["holm_base_m"], r["holm_m"] = base_m, m
        for k in EVENTS:
            r["mde_" + k] = (round(mde_sd(r[k + "_days"], m), 4) if r[k + "_days"] else "inf") if k + "_days" in r else ""
        if "broken_lines" in r:
            r["carried_kinds"] = ""
        elif r["config"] != PRIMARY:
            r["carried_kinds"] = "n/a_sensitivity"
        elif r["slope_tercile"] != "ALL":
            r["carried_kinds"] = "stratum_descriptive"
        else:
            r["carried_kinds"] = ";".join(k for k in FAMILY_EVENTS if f"{r['tf']}|{r['elig_arm']}|{k}" in carried)
    fields = ["cell", "config", "tf", "elig_arm", "slope_tercile", "eligible_lines", "lines_support", "lines_resistance"]
    for k in EVENTS:
        fields += [k, k + "_days"]
    fields += ["broken_lines", "flat_pairs"] + ["mde_" + k for k in EVENTS] + ["holm_base_m", "holm_m", "carried_kinds"]
    assert_no_outcome_columns(fields)
    for r in cell_rows:
        for f in fields:
            r.setdefault(f, "")
    with open(out / "CELLS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator=chr(10))
        w.writeheader()
        w.writerows(cell_rows)
    assert_no_outcome_columns(["cell", "date", "events"])
    with open(out / "effective_n_by_day.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["cell", "date", "events"], lineterminator=chr(10))
        w.writeheader()
        w.writerows(day_rows)
    with open(out / "KLINE_DIGESTS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "bytes", "sha256"], lineterminator=chr(10))
        w.writeheader()
        w.writerows(digests)
    (out / "quality.txt").write_text(chr(10).join(quality + [f"holm base_m={base_m} (DEV variants read) + carried -> m={m}, carried={len(carried)} of {len(nd)} primary cells: "
                                                         + ", ".join(sorted(carried)), f"total {time.time() - t0:.0f}s"]) + chr(10), newline=chr(10))
    print(f"holm base {base_m} m={m} carried {len(carried)}/{len(nd)}: {sorted(carried)}")


if __name__ == "__main__":
    main()
