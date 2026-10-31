import csv
import glob
import os
from pathlib import Path
from bisect import bisect_right
from datetime import datetime, timezone
import itertools
import warnings


MICRO_THRESHOLD = 10 ** 14  # DECISION (OURS): an open time above this is microseconds (ms 1e14 = year 5138)


def load_klines(root, dataset="klines", start_ms=None, end_ms=None, report=None):
    """Load kline data from CSV files in root/dataset.

    Hardening (T01-F1/F4): microsecond stamps are converted to ms; two rows with
    the same open time that differ in OHLCV raise ValueError (identical repeats
    are dropped and counted); out-of-order rows are sorted with a counted
    warning. If `report` is a dict it is filled with dups, conflicts(0),
    micro, unsorted and gaps (list of (prev_t, next_t)).
    """
    root = Path(root)
    dataset_path = root / dataset
    rep = {"dups": 0, "micro": 0, "unsorted": 0, "gaps": []}
    if report is not None:
        report.update(rep)
    if not dataset_path.exists():
        return []

    bars = {}
    prev_t = None
    for csv_file in sorted(dataset_path.glob("*.csv")):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = next(reader, None)
            if first_row is None:
                continue
            has_header = not first_row[0].isdigit()
            if not has_header:  # Opus fix: a headerless file's first row is data, not to be dropped
                reader = itertools.chain([first_row], reader)
            for row in reader:
                t = int(row[0])  # open_time
                if t > MICRO_THRESHOLD:
                    t //= 1000
                    rep["micro"] += 1
                if start_ms is not None and t < start_ms:
                    continue
                if end_ms is not None and t >= end_ms:
                    continue
                bar = {
                    't': t,
                    'o': float(row[1]),
                    'h': float(row[2]),
                    'l': float(row[3]),
                    'c': float(row[4]),
                    'v': float(row[5]),
                    'tbv': float(row[9])
                }
                if prev_t is not None and t < prev_t:
                    rep["unsorted"] += 1
                prev_t = t
                if t in bars:
                    if bars[t] != bar:
                        raise ValueError(
                            "load_klines: conflicting duplicate open_time %d in %s" % (t, csv_file))
                    rep["dups"] += 1
                    continue  # identical repeat: keep first
                bars[t] = bar
    result = list(bars.values())
    result.sort(key=lambda x: x['t'])
    if rep["unsorted"]:
        warnings.warn("load_klines: %d out-of-order rows sorted" % rep["unsorted"])
    if len(result) > 1:
        step = min(b['t'] - a['t'] for a, b in zip(result, result[1:]))
        rep["gaps"] = check_gaps(result, step)
    if report is not None:
        report.update(rep)
    return result


def load_metrics(root, start_ms=None, end_ms=None):
    """Load metrics data from CSV files."""
    root = Path(root)
    dataset_path = root / "metrics"
    if not dataset_path.exists():
        return []

    bars = []
    for csv_file in sorted(dataset_path.glob("*.csv")):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = next(reader, None)
            if first_row is None:
                continue
            has_header = not first_row[0].isdigit()
            if not has_header:  # Opus fix: a headerless file's first row is data, not to be dropped
                reader = itertools.chain([first_row], reader)
            for row in reader:
                t = int(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000)
                if start_ms is not None and t < start_ms:
                    continue
                if end_ms is not None and t >= end_ms:
                    continue
                bars.append({
                    't': t,
                    'oi': float(row[2]),
                    'oi_usd': float(row[3])
                })
    bars.sort(key=lambda x: x['t'])
    return bars


FUNDING_SUBDIRS = ("raw_fund/fundingRate", "raw/fundingRate")   # tried in this order under a Dumps/backtest base


def resolve_funding_dir(base):
    """First existing funding folder under base (raw_fund first, then raw); raises if neither exists (fail closed)."""
    for sub in FUNDING_SUBDIRS:
        d = Path(base) / sub
        if d.is_dir():
            return d
    raise FileNotFoundError(f"no funding folder under {base}: tried {', '.join(FUNDING_SUBDIRS)}")


def load_funding_strict(base, end_ms=None):
    """Shared screen loader: resolve the folder (raises when absent), return sorted (calc_time_ms, rate) with calc_time < end_ms."""
    d = resolve_funding_dir(base)
    rates = [r for r in load_funding(d.parent) if end_ms is None or r[0] < end_ms]
    if not rates:
        raise ValueError(f"funding folder {d} holds no rates before {end_ms}")
    return rates


FUNDING_SNAP_MS = 1000   # settlement stamps are floored to the second (DECISION OURS: boundary jitter rule)


def funding_cost_pct(funding, entry_ms, exit_ms, side):
    """Funding cost in % of notional: side x sum(rate of settlements s, entry < s <= exit). side +1 long pays a positive rate,
    side -1 short receives it. entry_ms / exit_ms / side broadcast as numpy arrays; funding = [(t_ms, rate)] sorted."""
    import numpy as np
    ts = np.array([x[0] for x in funding], np.int64)
    cum = np.concatenate(([0.0], np.cumsum([x[1] for x in funding])))
    ts = ts - ts % FUNDING_SNAP_MS   # archive calc_time is 1-31 ms after the 8h boundary: snap so (entry, exit] sees the nominal stamp
    a = np.searchsorted(ts, np.asarray(entry_ms, np.int64), side="right")
    b = np.searchsorted(ts, np.asarray(exit_ms, np.int64), side="right")
    return np.asarray(side) * (cum[b] - cum[a]) * 100.0


def load_funding(root):
    """Load funding rate data from CSV files."""
    root = Path(root)
    dataset_path = root / "fundingRate"
    if not dataset_path.exists():
        return []

    rates = []
    for csv_file in sorted(dataset_path.glob("*.csv")):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = next(reader, None)
            if first_row is None:
                continue
            has_header = not first_row[0].isdigit()
            if not has_header:  # Opus fix: a headerless file's first row is data, not to be dropped
                reader = itertools.chain([first_row], reader)
            for row in reader:
                t = int(row[0])  # calc_time
                rate = float(row[2])
                rates.append((t, rate))
    rates.sort()
    return rates


def funding_rate_at(funding, t_ms):
    """Get the latest funding rate before or at time t_ms."""
    if not funding:
        return 0.0
    idx = bisect_right([x[0] for x in funding], t_ms) - 1
    if idx < 0:
        return 0.0
    return funding[idx][1]


def cvd_delta(bar):
    """Calculate signed taker volume delta."""
    return 2 * bar['tbv'] - bar['v']


def check_gaps(bars, step_ms=60000):
    """Find gaps in time series."""
    if len(bars) < 2:
        return []
    gaps = []
    for i in range(1, len(bars)):
        prev_t = bars[i-1]['t']
        next_t = bars[i]['t']
        if next_t - prev_t != step_ms:
            gaps.append((prev_t, next_t))
    return gaps
