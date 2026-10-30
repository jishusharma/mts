"""Runner for card gap-g7-stop-slippage. DEV days only (< 2024-07-01), one aggTrades day at a time, zip deleted right after parsing.
Usage: python run_g7.py [scratch_dir]   (default F:/MTS_scratch_g7). Writes days.csv, summary.json next to this file."""
import sys
sys.dont_write_bytecode = True
import csv, hashlib, io, json, os, urllib.request, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slippage as S

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "backtest" / "bt"))
import bt_data

KLINES_ROOT = Path("F:/MTS_scratch_g7/kl")   # BTCUSDT-only copy of F:/MTS/data/tom_raw/klines 2022-01..2024-06 (the folder mixes symbols)
URL = "https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-%s.zip"
DELTAS = (0, 250, 1000)
STOPS = (0.20, 0.40, 0.80)
DEV_START = "2022-01-01"
MIN_EVENTS, K0, KMAX, SEED, NBOOT = 500, 4, 8, 20261030, 1000
BUCKETS = ("low", "mid", "high")


def dev_days():
    s = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    e = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
    bars = bt_data.load_klines(KLINES_ROOT, start_ms=s, end_ms=e)
    assert bars and max(b["t"] for b in bars) < e, "a bar at/after 2024-07-01 was read"
    day = defaultdict(lambda: [1e18, 0.0, None])
    for b in bars:
        d = datetime.fromtimestamp(b["t"] / 1000, timezone.utc).strftime("%Y-%m-%d")
        r = day[d]
        r[0] = min(r[0], b["l"]); r[1] = max(r[1], b["h"])
        if r[2] is None:
            r[2] = b["o"]
    n_bars = defaultdict(int)
    for b in bars:
        n_bars[datetime.fromtimestamp(b["t"] / 1000, timezone.utc).strftime("%Y-%m-%d")] += 1
    days = sorted(d for d in day if n_bars[d] >= 1400)          # complete-ish days only (OURS: >= 1400 of 1440 bars)
    return days, {d: (day[d][1] - day[d][0]) / day[d][2] * 100.0 for d in days}


def fetch_day(day, scratch):
    S.assert_dev_day(day)
    z = scratch / ("BTCUSDT-aggTrades-%s.zip" % day)
    req = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "mts-g7"}), timeout=120)
    chk = req(URL % day + ".CHECKSUM").read().decode().split()[0].lower()
    with req(URL % day) as r, open(z, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    sha = hashlib.sha256(z.read_bytes()).hexdigest()
    if sha != chk:
        z.unlink()
        raise ValueError("checksum mismatch %s" % day)
    return z, sha


def day_events(z):
    with zipfile.ZipFile(z) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as f:
            df = pd.read_csv(f, usecols=[1, 5])               # price, transact_time
    if df.columns[0] != "price":
        df.columns = ["price", "transact_time"]
    df = df.sort_values("transact_time", kind="stable")
    t = df["transact_time"].to_numpy(np.int64)
    p = df["price"].to_numpy(float)
    ev = S.crossing_events(t, p)
    out = {d: S.slips_bp(t, p, ev, d) for d in DELTAS}
    return len(t), len(ev), out


def boot_median(per_day, delta, rng):
    ds = [v[delta][~np.isnan(v[delta])] for v in per_day.values()]
    meds = []
    for _ in range(NBOOT):
        pick = rng.integers(0, len(ds), len(ds))
        meds.append(np.median(np.concatenate([ds[i] for i in pick])))
    return float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


def main():
    scratch = Path(sys.argv[1] if len(sys.argv) > 1 else "F:/MTS_scratch_g7")
    scratch.mkdir(parents=True, exist_ok=True)
    days, rng_pct = dev_days()
    terc = dict(zip(days, S.assign_terciles([rng_pct[d] for d in days])))
    by_b = {b: [d for d in days if terc[d] == b] for b in BUCKETS}
    used = {b: [] for b in BUCKETS}
    data = {b: {} for b in BUCKETS}                           # bucket -> day -> {delta: slips}
    meta = {}                                                 # day -> dict
    rnd = 0
    todo = {b: S.pick_days(by_b[b], K0, []) for b in BUCKETS}
    log = []
    while any(todo.values()):
        rnd += 1
        for b in BUCKETS:
            for d in todo[b]:
                z, sha = fetch_day(d, scratch)
                try:
                    nt, ne, out = day_events(z)
                finally:
                    z.unlink()                                  # no aggTrades zip left behind
                used[b].append(d); data[b][d] = out
                meta[d] = dict(day=d, tercile=b, range_pct=round(rng_pct[d], 4), zip_sha256=sha, n_trades=nt, n_events=ne, round=rnd)
                print(rnd, b, d, nt, ne, flush=True)
        todo = {b: [] for b in BUCKETS}
        for b in BUCKETS:
            n_ev = sum(len(v[0]) for v in data[b].values())
            if n_ev < MIN_EVENTS and len(used[b]) < KMAX:
                todo[b] = S.pick_days(by_b[b], min(K0, KMAX - len(used[b])), used[b])
                log.append("round %d: %s had %d events (< %d) after %d days -> extend by %d (counts only)" % (rnd, b, n_ev, MIN_EVENTS, len(used[b]), len(todo[b])))
    rng = np.random.default_rng(SEED)
    rows = []
    for b in BUCKETS:
        for dl in DELTAS:
            allv = np.concatenate([v[dl] for v in data[b].values()])
            allv = allv[~np.isnan(allv)]
            lo, hi = boot_median(data[b], dl, rng)
            row = dict(bucket=b, delta_ms=dl, n_events=int(len(allv)), n_days=len(data[b]),
                       median_bp=float(np.median(allv)), p90_bp=float(np.percentile(allv, 90)), mean_bp=float(allv.mean()),
                       frac_zero=float((allv == 0).mean()), boot_lo_bp=lo, boot_hi_bp=hi, thin=bool(len(allv) < MIN_EVENTS))
            for sp in STOPS:
                row["median_R_%.2f" % sp] = float(S.to_r(row["median_bp"], sp))
                row["p90_R_%.2f" % sp] = float(S.to_r(row["p90_bp"], sp))
            rows.append(row)
    with open(HERE / "days.csv", "w", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=["day", "tercile", "range_pct", "zip_sha256", "n_trades", "n_events", "round"], lineterminator="\n")
        w.writeheader()
        for d in sorted(meta):
            w.writerow(meta[d])
    cuts = {b: [round(min(rng_pct[d] for d in by_b[b]), 3), round(max(rng_pct[d] for d in by_b[b]), 3)] for b in BUCKETS}
    (HERE / "summary.json").write_text(json.dumps(dict(rows=rows, log=log, seed=SEED, nboot=NBOOT, n_dev_days=len(days), range_pct_span=cuts), indent=1), newline="\n")
    print(json.dumps(log))


if __name__ == "__main__":
    main()
