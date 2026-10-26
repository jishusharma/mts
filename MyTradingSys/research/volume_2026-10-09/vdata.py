# T01-F2: raw_1d is a distinct snapshot, NOT the 1m resample (905 of 912 DEV days differ on open, 847 on volume, max 12.01%); derive daily bars from 1m for new work. See MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md
"""Volume study data layer (PRE_REG_VOLUME_2026-10-09.md section 1). numpy + stdlib.

Bars are dicts of numpy arrays: t (open time epoch ms UTC), o, h, l, c, v (base volume), tbv (taker-buy base volume).
Sealed-window guard: every loader refuses an end after VALID_END_MS unless unseal=True (V0/V1 never pass it);
stage "dev" cuts at DEV_END_MS, stage "valid" at VALID_END_MS.
"""
import sys
sys.dont_write_bytecode = True
import bisect
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "Dumps" / "backtest"
HOUR = 3600000
DAY = 86400000


def ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


START_MS = ms(2020, 1, 1)
DEV_END_MS = ms(2024, 7, 1)      # exclusive
VALID_END_MS = ms(2025, 7, 1)    # exclusive; HOLDOUT = [VALID_END_MS, end of archive), sealed
STAGE_END = {"dev": DEV_END_MS, "valid": VALID_END_MS}
STAGE_START = {"dev": START_MS, "valid": DEV_END_MS}


def _read_dir(d):
    rows = {}
    for f in sorted(Path(d).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            rd = csv.reader(fh)
            for row in rd:
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                if t not in rows:
                    rows[t] = (t, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[9]))
    ts = sorted(rows)
    a = np.array([rows[t] for t in ts], dtype=float)
    return {"t": a[:, 0].astype(np.int64), "o": a[:, 1], "h": a[:, 2], "l": a[:, 3], "c": a[:, 4], "v": a[:, 5], "tbv": a[:, 6]}


def _cut(bars, start_ms, end_ms):
    m = (bars["t"] >= start_ms) & (bars["t"] < end_ms)
    return {k: x[m] for k, x in bars.items()}


def _guard(end_ms, unseal):
    if end_ms > VALID_END_MS and not unseal:
        raise PermissionError("HOLDOUT is sealed (PRE_REG section 1): end_ms must be <= VALID_END_MS")


def load_1d(start_ms=START_MS, end_ms=DEV_END_MS, unseal=False):
    _guard(end_ms, unseal)
    return _cut(_read_dir(RAW / "raw_1d" / "klines"), start_ms, end_ms)


def load_1h(start_ms=START_MS, end_ms=DEV_END_MS, unseal=False):
    _guard(end_ms, unseal)
    return _cut(_read_dir(RAW / "raw_1h" / "klines"), start_ms, end_ms)


def resample(b1h, k=4):
    """k consecutive 1h bars -> one bar, bucket start = floor(t / (k*HOUR)) * k*HOUR; only complete buckets."""
    step = k * HOUR
    bucket = b1h["t"] // step
    out = {key: [] for key in b1h}
    n = len(bucket)
    i = 0
    while i < n:
        j = i
        while j < n and bucket[j] == bucket[i]:
            j += 1
        if j - i == k and (b1h["t"][j - 1] - b1h["t"][i]) == (k - 1) * HOUR:
            out["t"].append(bucket[i] * step)
            out["o"].append(b1h["o"][i])
            out["h"].append(b1h["h"][i:j].max())
            out["l"].append(b1h["l"][i:j].min())
            out["c"].append(b1h["c"][j - 1])
            out["v"].append(b1h["v"][i:j].sum())
            out["tbv"].append(b1h["tbv"][i:j].sum())
        i = j
    res = {key: np.array(val) for key, val in out.items()}
    res["t"] = res["t"].astype(np.int64)
    return res


def load_4h(start_ms=START_MS, end_ms=DEV_END_MS, unseal=False):
    _guard(end_ms, unseal)
    # load a little beyond the window so a bucket straddling the cut is complete, then cut
    full = _read_dir(RAW / "raw_1h" / "klines")
    return _cut(resample(full), start_ms, end_ms)


class Funding:
    """8h settlements from the archive. sum(t0, t1) = sum of rates settled in (t0, t1]: a long pays, a short receives
    (FORMULAS.md section 13). Read from the full file; funding is not a signal input, only a cost."""

    def __init__(self):
        rows = []
        for f in sorted((RAW / "raw_fund" / "fundingRate").glob("*.csv")):
            with open(f, newline="", encoding="utf-8") as fh:
                for row in csv.reader(fh):
                    if row and row[0].isdigit():
                        rows.append((int(row[0]), float(row[2])))
        rows.sort()
        self.times = [t for t, _ in rows]
        self.cum = [0.0]
        for _, r in rows:
            self.cum.append(self.cum[-1] + r)

    def sum(self, t0, t1):
        i = bisect.bisect_right(self.times, t0)
        j = bisect.bisect_right(self.times, t1)
        return self.cum[j] - self.cum[i]

    def window(self, t_arr, entry_idx, exit_idx):
        """vectorised: funding in (t[entry], t[exit]] for index arrays."""
        times = np.array(self.times, dtype=np.int64)
        cum = np.array(self.cum)
        i = np.searchsorted(times, t_arr[entry_idx], side="right")
        j = np.searchsorted(times, t_arr[exit_idx], side="right")
        return cum[j] - cum[i]


def gaps(b, step_ms):
    d = np.diff(b["t"])
    return [int(i + 1) for i in np.nonzero(d != step_ms)[0]]
