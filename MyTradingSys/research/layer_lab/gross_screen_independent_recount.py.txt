from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np

ROOT = Path(r"F:/MTS/data/tom_raw/klines")
BASE = Path(__file__).resolve().parents[1] / "gross_effect_screen_2026-10-15"
MANIFEST = BASE / "DATA_MANIFEST.csv"
START = np.datetime64("2022-01-01T00:00", "m")
END = np.datetime64("2024-07-01T00:00", "m")
N_DAYS = int((END - START) / np.timedelta64(1, "D"))
CUTOFF_MS = int(END.astype("datetime64[ms]").astype(np.int64))
EXPECTED_MONTHS = [
    f"{year}-{month:02d}"
    for year in range(2022, 2025)
    for month in range(1, 13)
    if "2022-01" <= f"{year}-{month:02d}" <= "2024-06"
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


manifest = {}
with MANIFEST.open(newline="", encoding="utf-8") as stream:
    for row in csv.DictReader(stream):
        manifest[row["file"]] = row["sha256"]

files = [f"BTCUSDT-1m-{month}.csv" for month in EXPECTED_MONTHS]
if set(files) != set(manifest):
    raise SystemExit(f"manifest/file set mismatch: expected {len(files)}, got {len(manifest)}")

all_ts, all_o, all_h, all_l, all_v, all_tbv = [], [], [], [], [], []
for name in files:
    path = ROOT / name
    if sha256(path) != manifest[name]:
        raise SystemExit(f"SHA256 mismatch: {name}")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.reader(stream)
        header = next(rows)
        indexes = {
            key: header.index(key)
            for key in ("open_time", "open", "high", "low", "volume", "taker_buy_volume")
        }
        month_ts, month_o, month_h, month_l, month_v, month_tbv = [], [], [], [], [], []
        for row in rows:
            ts = int(row[indexes["open_time"]])
            if ts >= CUTOFF_MS:
                raise SystemExit(f"post-DEV bar encountered: {name} {ts}")
            month_ts.append(ts)
            month_o.append(float(row[indexes["open"]]))
            month_h.append(float(row[indexes["high"]]))
            month_l.append(float(row[indexes["low"]]))
            month_v.append(float(row[indexes["volume"]]))
            month_tbv.append(float(row[indexes["taker_buy_volume"]]))
    all_ts.extend(month_ts)
    all_o.extend(month_o)
    all_h.extend(month_h)
    all_l.extend(month_l)
    all_v.extend(month_v)
    all_tbv.extend(month_tbv)

ts = np.asarray(all_ts, dtype=np.int64)
minute_index = ((ts - int(START.astype("datetime64[ms]").astype(np.int64))) // 60000).astype(np.int64)
day_index, minute = np.divmod(minute_index, 1440)
shape = (N_DAYS, 1440)
open_ = np.full(shape, np.nan)
high = np.full(shape, np.nan)
low = np.full(shape, np.nan)
volume = np.full(shape, np.nan)
tbv = np.full(shape, np.nan)
open_[day_index, minute] = np.asarray(all_o)
high[day_index, minute] = np.asarray(all_h)
low[day_index, minute] = np.asarray(all_l)
volume[day_index, minute] = np.asarray(all_v)
tbv[day_index, minute] = np.asarray(all_tbv)
valid = np.isfinite(open_)
if len(ts) != len(np.unique(ts)):
    raise SystemExit("duplicate open_time values")
missing_minutes = int(valid.size - valid.sum())

# Section 2: cumulative session extremes and the same-minute prior-20-day range.
daily_leg = np.full(shape, np.nan)
max_idx = np.zeros(shape, dtype=np.int16)
min_idx = np.zeros(shape, dtype=np.int16)
cum_high = np.empty(shape)
cum_low = np.empty(shape)
for d in range(N_DAYS):
    hrow = np.where(valid[d], high[d], -np.inf)
    lrow = np.where(valid[d], low[d], np.inf)
    cum_high[d] = np.maximum.accumulate(hrow)
    cum_low[d] = np.minimum.accumulate(lrow)
    hset = np.zeros(1440, dtype=bool)
    lset = np.zeros(1440, dtype=bool)
    hset[0] = valid[d, 0]
    lset[0] = valid[d, 0]
    hset[1:] = valid[d, 1:] & (high[d, 1:] > cum_high[d, :-1])
    lset[1:] = valid[d, 1:] & (low[d, 1:] < cum_low[d, :-1])
    max_idx[d] = np.maximum.accumulate(np.where(hset, np.arange(1440), 0))
    min_idx[d] = np.maximum.accumulate(np.where(lset, np.arange(1440), 0))
    if valid[d, 0]:
        daily_leg[d] = (cum_high[d] - cum_low[d]) / open_[d, 0]

threshold = np.full(shape, np.nan)
for d in range(N_DAYS):
    lo = max(0, d - 20)
    for m in range(1440):
        ref = daily_leg[lo:d, m]
        ref = ref[np.isfinite(ref)]
        if len(ref) >= 15:
            # DECISION (OURS): NumPy's linear 80th percentile; PRE_REG does not specify interpolation.
            threshold[d, m] = np.quantile(ref, 0.80, method="linear")

delta = 2.0 * tbv - volume
eligible_by_side = {"SHORT": [], "LONG": []}
for d in range(N_DAYS):
    if not valid[d, 0]:
        continue
    mins = np.arange(1440)
    leg = (cum_high[d] - cum_low[d]) / open_[d, 0]
    common = (mins >= 60) & valid[d] & np.isfinite(threshold[d]) & (leg >= threshold[d])
    short_mask = common & (max_idx[d] >= mins - 2) & (min_idx[d] < max_idx[d])
    long_mask = common & (min_idx[d] >= mins - 2) & (max_idx[d] < min_idx[d])
    for side, mask in (("SHORT", short_mask), ("LONG", long_mask)):
        candidates = np.flatnonzero(mask)
        last = -10_000
        for m in candidates:
            if m - last <= 60:
                continue
            if m < 4 or not np.isfinite(delta[d, m - 4:m + 1]).all():
                continue
            d5 = float(delta[d, m - 4:m + 1].sum())
            flow = (d5 < 0) if side == "SHORT" else (d5 > 0)
            eligible_by_side[side].append((d * 1440 + int(m), flow, -1 if side == "SHORT" else 1))
            last = int(m)

rows = [item for side in ("SHORT", "LONG") for item in eligible_by_side[side]]
n_c = len(rows)
n_t = sum(flow for _, flow, _ in rows)
n_notf = n_c - n_t
print(f"manifest_sha256=PASS files={len(files)}")
print(f"DEV bars={int(valid.sum()):,} missing_minutes={missing_minutes:,} range=2022-01-01..2024-06-30")
print(f"eligible ledger n_C={n_c} n_T={n_t} n_notF={n_notf}")
for side in ("SHORT", "LONG"):
    side_rows = eligible_by_side[side]
    print(f"{side}: n={len(side_rows)} n_T={sum(flow for _, flow, _ in side_rows)} n_notF={sum(not flow for _, flow, _ in side_rows)}")
print("cooldown=greedy shared per side; next eligible must be >60 bars later")
print("percentile=NumPy quantile(method='linear'); D5 undefined if any of five bars is missing")

# Section 4: recompute only arm T at primary cell d=1, h=60.
open_flat = open_.reshape(-1)
epoch_ms = int(START.astype("datetime64[ms]").astype(np.int64))
settlement_ms = 8 * 3600 * 1000
primary = []
dropped = 0
dropped_all = 0
primary_counts = {"T": 0, "notF": 0, "C": 0}
for index, flow, side_sign in rows:
    entry = index + 1 + 1
    exit_ = entry + 60
    if exit_ >= len(open_flat) or not np.isfinite(open_flat[entry]) or not np.isfinite(open_flat[exit_]):
        dropped_all += 1
        if flow:
            dropped += 1
        continue
    primary_counts["C"] += 1
    primary_counts["T" if flow else "notF"] += 1
    if not flow:
        continue
    gross = side_sign * (open_flat[exit_] / open_flat[entry] - 1.0) * 100.0
    entry_ms = epoch_ms + entry * 60_000
    exit_ms = epoch_ms + exit_ * 60_000
    funding = 0.01 if (exit_ms // settlement_ms) - (entry_ms // settlement_ms) > 0 else 0.0
    primary.append((index // 1440, gross - funding))

values = np.asarray([value for _, value in primary], dtype=float)
days = np.asarray([day for day, _ in primary], dtype=np.int64)
mean = float(values.mean())
cluster_sums = [float((values[days == day] - mean).sum()) for day in np.unique(days)]
se = float(np.sqrt(np.square(cluster_sums).sum()) / len(values))
t_cost = (mean - 0.14) / se
raw_values = values + np.asarray([
    0.01 if ((epoch_ms + (index + 62) * 60_000) // settlement_ms) - ((epoch_ms + (index + 2) * 60_000) // settlement_ms) > 0 else 0.0
    for index, flow, _ in rows if flow and index + 62 < len(open_flat)
])
print(f"primary available counts={primary_counts} dropped_all={dropped_all} (independent; DEV boundary only)")
print(f"T primary d=1 h=60: n={len(values)} dropped={dropped} mean_G_raw={raw_values.mean():.6f} mean_after_funding={mean:.6f} SE_day_clustered={se:.6f} t_cost={t_cost:.6f}")
print(f"T share of ledger encounters={n_t}/{n_c}={100*n_t/n_c:.4f}%")
