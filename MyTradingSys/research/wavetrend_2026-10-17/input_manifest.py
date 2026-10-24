"""DEV-only content manifest for the WaveTrend 1m input files (card wavetrend-data-inference).

Reads ONLY column 0 (open time) of each kline CSV: no price, volume, return or outcome field is parsed.
Refuses any file named at/after 2024-07 and any timestamp at/after 2024-07-01 UTC (VALIDATION/HOLDOUT sealed).

Usage: python input_manifest.py [--klines-dir F:/MTS/data/tom_raw/klines] [--out input_manifest.json]
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

import numpy as np

MS = 60_000
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MONTH = "2024-07"
EXPECTED_FILES = 30
TFS = {"5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
_NAME = re.compile(r"^BTCUSDT-1m-(\d{4}-\d{2})\.csv$")


class CutoffRefusal(ValueError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _month_bounds_ms(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    a = dt.datetime(y, m, 1, tzinfo=dt.timezone.utc)
    b = dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=dt.timezone.utc)
    return int(a.timestamp() * 1000), int(b.timestamp() * 1000)


def read_open_times(path):
    """Open-time column only, in file order (ms). Header/blank rows skipped. Refuses timestamps >= cutoff."""
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.reader(fh):
            if not r or not r[0][:1].isdigit():
                continue
            t = int(float(r[0]))
            if t > 1e14:
                t //= 1000
            if t >= CUTOFF_MS:
                raise CutoffRefusal(f"timestamp {t} >= 2024-07-01 refused: {path}")
            out.append(t)
    return out


def _check_name(path):
    m = _NAME.match(Path(path).name)
    if not m:
        raise ValueError(f"unexpected file name {Path(path).name}")
    if m.group(1) >= CUTOFF_MONTH:
        raise CutoffRefusal(f"{Path(path).name} is at/after {CUTOFF_MONTH}: refused (VALIDATION/HOLDOUT sealed)")
    return m.group(1)


def scan_file(path):
    """Per-file entry plus the set of minute indexes (relative to TS0) present inside the file's month."""
    path = Path(path)
    ym = _check_name(path)
    ts = read_open_times(path)
    lo, hi = _month_bounds_ms(ym)
    uniq = sorted(set(ts))
    in_month = [t for t in uniq if lo <= t < hi]
    expected = (hi - lo) // MS
    entry = {
        "name": path.name, "size": path.stat().st_size, "sha256": sha256_file(path),
        "rows": len(ts), "unique_minutes": len(uniq),
        "duplicate_rows": len(ts) - len(uniq),
        "out_of_month_minutes": len(uniq) - len(in_month),
        "expected_minutes": expected, "missing_minutes": expected - len(in_month),
        "first_ms": uniq[0] if uniq else None, "last_ms": uniq[-1] if uniq else None,
    }
    return entry, {(t - TS0) // MS for t in in_month}


def usable_bars(minute_idx, n_minutes):
    """Complete higher-timeframe buckets on the TS0 grid (every 1m present). Counts presence only."""
    present = np.zeros(n_minutes, bool)
    for i in minute_idx:
        if 0 <= i < n_minutes:
            present[i] = True
    return {tf: int(present[: n_minutes // m * m].reshape(-1, m).all(axis=1).sum()) for tf, m in TFS.items()}


def build_manifest(files):
    files = sorted(Path(f) for f in files)
    for f in files:                      # refuse by name before opening anything
        _check_name(f)
    entries, allidx = [], set()
    for f in files:
        e, idx = scan_file(f)
        entries.append(e)
        allidx |= idx
    n_min = (_month_bounds_ms(entries[-1]["name"][12:19])[1] - TS0) // MS if entries else 0
    firsts = [e["first_ms"] for e in entries if e["first_ms"] is not None]
    lasts = [e["last_ms"] for e in entries if e["last_ms"] is not None]
    return {
        "version": 1, "cutoff_utc": "2024-07-01", "source_dir_note": "F:/MTS/data/tom_raw/klines",
        "n_files": len(entries), "files": entries,
        "totals": {"rows": sum(e["rows"] for e in entries),
                   "duplicate_rows": sum(e["duplicate_rows"] for e in entries),
                   "missing_minutes": sum(e["missing_minutes"] for e in entries)},
        "usable_bars": usable_bars(allidx, n_min),
        "coverage_first_ms": min(firsts) if firsts else None,
        "coverage_last_ms": max(lasts) if lasts else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines-dir", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "input_manifest.json"))
    a = ap.parse_args()
    files = [f for f in sorted(Path(a.klines_dir).glob("BTCUSDT-1m-202[234]-*.csv")) if f.stem[-7:] < CUTOFF_MONTH]
    if len(files) != EXPECTED_FILES:
        raise SystemExit(f"expected {EXPECTED_FILES} DEV files, found {len(files)} in {a.klines_dir}")
    man = build_manifest(files)
    with open(a.out, "w", newline="\n", encoding="utf-8") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print(f"wrote {a.out}: {man['n_files']} files, {man['totals']}")


if __name__ == "__main__":
    main()
