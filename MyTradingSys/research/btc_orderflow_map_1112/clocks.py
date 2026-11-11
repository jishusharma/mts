"""Card btc-of-map-clocks-1112: BTC own clocks from 1m taker delta, DEV only (PREREG.md split table).

    python clocks.py --split dev [--dir <klines dir>] [--draws 300]

Binance USD-M BTCUSDT 1m klines (monthly BTCUSDT-1m-YYYY-MM.csv or .zip; F:/MTS/data/tom_raw/klines on the desktop, else
data.binance.vision). DEV = 2022-02-01 .. 2024-05-31 (PREREG.md frozen split). Files and rows outside the split are never read:
VALIDATION / HOLDOUT are refused here (card 2 reads DEV only; VALIDATION only for cells that clear DEV, PREREG.md).
Definitions (OURS unless noted):
- delta per 1m bar = 2 * taker_buy_volume - volume (as fabio_cvd_2026-10-30/cvd_u7_u8.py, SOURCED).
- buckets: 24 UTC hours; 3 funding windows = bars within -30..+29 min of 00Z / 08Z / 16Z (the rest = 'other'); 7 weekdays (Mon=0).
- per bucket: n bars, delta share = sum delta / sum volume, mean abs 1m return bp, forward net bp = sign(bar delta) *
  (close[i+h] / open[i+1] - 1) * 1e4 - 10 (h = 15 and 60 min; 10 bp round trip, SOURCED 0.05 % per side taker, repo fee).
  Entries overlap (every minute is an entry), so n is bars, not independent trades: no t-stat is claimed; the placebo z is.
- placebo (seed 1112): each UTC day gets a random hour offset (hour and funding labels) and the weekday labels are permuted across
  days; z = (observed - placebo mean) / placebo sd per bucket and statistic. |z| < 2 is marked noise.
"""
import argparse
import csv
import glob
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import numpy as np

DEV_START_MS = 1643673600000  # 2022-02-01T00:00Z
DEV_END_MS = 1717200000000    # 2024-06-01T00:00Z (exclusive)
DEV_FIRST, DEV_LAST = "2022-02", "2024-05"
FEE_BP = 10.0
HORIZONS = (15, 60)
SEED = 1112
FUND_HALF = 30
STATS = ("delta_share", "absret", "fwd15", "fwd60")


def month_files(folder):
    out = []
    for f in sorted(glob.glob(os.path.join(folder, "BTCUSDT-1m-????-??.*"))):
        if not f.endswith((".csv", ".zip")):
            continue
        tag = os.path.basename(f)[len("BTCUSDT-1m-"):][:7]
        if DEV_FIRST <= tag <= DEV_LAST:
            out.append(f)
    return out


def _open(f):
    if f.endswith(".zip"):
        z = zipfile.ZipFile(f)
        return io.TextIOWrapper(z.open(z.namelist()[0]), "utf-8")
    return open(f, newline="", encoding="utf-8")


def load_dev(folder):
    """Arrays t_ms, open, close, volume, taker_buy for DEV rows only (rows outside the DEV window are dropped)."""
    cols = [[] for _ in range(5)]
    for f in month_files(folder):
        with _open(f) as fh:
            for r in csv.reader(fh):
                if r[0] == "open_time":
                    continue
                t = int(r[0])
                if t > 10 ** 14:
                    t //= 1000
                if not DEV_START_MS <= t < DEV_END_MS:
                    continue
                for c, v in zip(cols, (t, r[1], r[4], r[5], r[9])):
                    c.append(v)
    t = np.array(cols[0], dtype=np.int64)
    o, c, v, tb = (np.array(x, dtype=float) for x in cols[1:])
    order = np.argsort(t)
    return t[order], o[order], c[order], v[order], tb[order]


def features(t, o, c, v, tb):
    """Per-bar arrays: delta, volume, abs 1m return bp, signed forward net bp per horizon (NaN where not contiguous)."""
    delta = 2 * tb - v
    absret = np.abs(c / o - 1) * 1e4
    sign = np.sign(delta)
    n = len(t)
    fwd = {}
    for h in HORIZONS:
        f = np.full(n, np.nan)
        if n > h + 1:
            m = n - h
            ok = (t[h:] - t[:m] == h * 60000) & (t[1:m + 1] - t[:m] == 60000)
            val = sign[:m] * (c[h:] / o[1:m + 1] - 1) * 1e4 - FEE_BP
            val[~ok | (sign[:m] == 0)] = np.nan
            f[:m] = val
        fwd[h] = f
    return {"delta": delta, "vol": v, "absret": absret, "fwd": fwd}


def labels(t, hour_off=None, wd_perm=None):
    """(hour, funding id 0..2 or 3 = other, weekday) per bar; offsets / permutation implement the day-label placebo."""
    day = t // 86400000
    d0 = day - day.min()
    mod = (t // 60000) % 1440
    if hour_off is not None:
        mod = (mod + 60 * hour_off[d0]) % 1440
    hour = mod // 60
    fund = np.full(len(t), 3)
    for k, centre in enumerate((0, 480, 960)):
        d = (mod - centre + 720) % 1440 - 720
        fund[(d >= -FUND_HALF) & (d < FUND_HALF)] = k
    wd = (day + 3) % 7  # 1970-01-01 was a Thursday; Mon = 0
    if wd_perm is not None:
        wd = wd_perm[d0]
    return hour, fund, wd


def bucket_stats(feat, lab, nb):
    out = {"n": np.bincount(lab, minlength=nb).astype(float)}
    sd = np.bincount(lab, weights=feat["delta"], minlength=nb)
    sv = np.bincount(lab, weights=feat["vol"], minlength=nb)
    with np.errstate(invalid="ignore", divide="ignore"):
        out["delta_share"] = sd / sv
        out["absret"] = np.bincount(lab, weights=feat["absret"], minlength=nb) / out["n"]
        for h in HORIZONS:
            f = feat["fwd"][h]
            ok = ~np.isnan(f)
            cnt = np.bincount(lab[ok], minlength=nb)
            out[f"fwd{h}"] = np.bincount(lab[ok], weights=f[ok], minlength=nb) / cnt
    return out


def run(t, feat, draws=300, seed=SEED):
    """Observed stats and placebo z per clock: {clock: {labels, n, stat, stat_z}}."""
    day0 = int(t.min() // 86400000)
    ndays = int(t.max() // 86400000) - day0 + 1
    rng = np.random.default_rng(seed)
    clocks = {"hour": (0, 24), "funding": (1, 4), "weekday": (2, 7)}
    obs_lab = labels(t)
    obs = {k: bucket_stats(feat, obs_lab[i], nb) for k, (i, nb) in clocks.items()}
    plc = {k: {s: [] for s in STATS} for k in clocks}
    day_wd = (np.arange(ndays) + day0 + 3) % 7
    for _ in range(draws):
        lab = labels(t, hour_off=rng.integers(0, 24, ndays), wd_perm=rng.permutation(day_wd))
        for k, (i, nb) in clocks.items():
            st = bucket_stats(feat, lab[i], nb)
            for s in STATS:
                plc[k][s].append(st[s])
    names = {"hour": [f"{h:02d}Z" for h in range(24)], "funding": ["00Z", "08Z", "16Z", "other"],
             "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
    res = {}
    for k in clocks:
        r = {"labels": names[k], "n": obs[k]["n"].tolist()}
        for s in STATS:
            arr = np.array(plc[k][s])
            mu, sd = np.nanmean(arr, axis=0), np.nanstd(arr, axis=0)
            r[s] = obs[k][s].tolist()
            r[s + "_z"] = ((obs[k][s] - mu) / sd).tolist()
        res[k] = r
    return res


def table_md(res):
    lines = []
    for k, r in res.items():
        lines += [f"### Clock: {k}", "",
                  "| bucket | n bars | delta share | z | mean abs ret bp | z | fwd 15m net bp | z | fwd 60m net bp | z | mark |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for i, name in enumerate(r["labels"]):
            zs = [r[s + "_z"][i] for s in STATS]
            mark = "noise" if all(abs(z) < 2 for z in zs) else ""
            lines.append(f"| {name} | {int(r['n'][i])} | {r['delta_share'][i]:+.4f} | {zs[0]:+.1f} | {r['absret'][i]:.2f} | {zs[1]:+.1f} | "
                         f"{r['fwd15'][i]:+.2f} | {zs[2]:+.1f} | {r['fwd60'][i]:+.2f} | {zs[3]:+.1f} | {mark} |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", default="dev")
    ap.add_argument("--dir", default=os.environ.get("BTC_KLINES_DIR", "F:/MTS/data/tom_raw/klines"))
    ap.add_argument("--draws", type=int, default=300)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    a = ap.parse_args(argv)
    if a.split != "dev":
        print("refused: card 2 reads DEV only (PREREG.md); VALIDATION is read once, later, for cells that clear DEV")
        return 2
    t, o, c, v, tb = load_dev(a.dir)
    if len(t) == 0:
        print(f"no DEV klines under {a.dir}")
        return 1
    feat = features(t, o, c, v, tb)
    res = run(t, feat, a.draws)
    expected = (DEV_END_MS - DEV_START_MS) // 60000
    meta = {"split": "DEV 2022-02-01..2024-05-31", "bars": int(len(t)), "expected_bars": int(expected),
            "missing_bars": int(expected - len(t)), "fee_bp_round_trip": FEE_BP, "draws": a.draws, "seed": SEED}
    Path(a.out, "results_clocks.json").write_text(json.dumps({"meta": meta, "clocks": res}, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(meta))
    print(table_md(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
