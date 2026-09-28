"""
This implements the D1 / TF-B5 correctness gate ("resampled 1d from 1m must
equal Binance's native 1d archive bars exactly (open, high, low, close, volume)
over the overlap") noted as a follow-up in layers/timeframe/TEST_PLAN.md Case TF-B5.
This script is that integration check. It never modifies any CSV file (read-only)
and never fetches data over the network itself (fetch_binance_archive.py populates
these directories). The gap_count != 0 check exists because a real 1440-bar day can be
genuinely short a few 1m bars in the raw archive itself (an upstream data gap, not a bug
in resample) and this gate reports that distinctly from an o/h/l/c/v mismatch.
"""
import csv
import json
import argparse
import sys
import pathlib
from datetime import datetime
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample

def load_klines_csv(path: str) -> list:
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        result = []
        for row in reader:
            result.append({
                "t": int(row['open_time']),
                "o": float(row['open']),
                "h": float(row['high']),
                "l": float(row['low']),
                "c": float(row['close']),
                "v": float(row['volume'])
            })
        return sorted(result, key=lambda x: x["t"])

def compare_month(symbol: str, year_month: str, raw_1m_dir: str, raw_1d_dir: str, registry_path: str, tolerance: float = 1e-6) -> dict:
    m1_path = f"{raw_1m_dir}/{symbol}-1m-{year_month}.csv"
    m1_file = pathlib.Path(m1_path)
    m1_exists = m1_file.exists()
    
    m1d_path = f"{raw_1d_dir}/{symbol}-1d-{year_month}.csv"
    m1d_file = pathlib.Path(m1d_path)
    m1d_exists = m1d_file.exists()

    if not m1_exists or not m1d_exists:
        reason = "missing 1m" if not m1_exists else "missing 1d"
        return {
            "year_month": year_month,
            "status": "SKIP",
            "reason": reason,
            "n_matched": 0,
            "n_mismatched": 0,
            "mismatches": []
        }

    bars_1m = load_klines_csv(m1_path)
    with open(registry_path) as f:
        registry = json.load(f)

    resampled_bars = resample(bars_1m, "1d", registry)
    native_bars = load_klines_csv(m1d_path)
    native_by_t = {bar["t"]: bar for bar in native_bars}

    mismatches = []
    n_matched = 0
    n_mismatched = 0

    for bucket in resampled_bars:
        t = bucket["t"]
        if t not in native_by_t:
            mismatches.append({
                "t": t,
                "field": "MISSING_NATIVE",
                "resampled": None,
                "native": None
            })
            n_mismatched += 1
            continue

        native_bar = native_by_t[t]
        bucket_has_mismatch = False

        if bucket["gap_count"] != 0:
            mismatches.append({
                "t": t,
                "field": "gap_count",
                "resampled": bucket["gap_count"],
                "native": None,
                "diff": bucket["gap_count"]
            })
            bucket_has_mismatch = True
            n_mismatched += 1
        else:
            n_matched += 1

        for field in ("o", "h", "l", "c", "v"):
            resampled_val = bucket[field]
            native_val = native_bar[field]
            diff = abs(resampled_val - native_val)
            rel_tolerance = max(tolerance, tolerance * abs(native_val))
            if diff >= rel_tolerance:
                mismatches.append({
                    "t": t,
                    "field": field,
                    "resampled": resampled_val,
                    "native": native_val,
                    "diff": diff
                })
                bucket_has_mismatch = True
                n_mismatched += 1

        if bucket_has_mismatch:
            n_mismatched += 1
        else:
            n_matched += 1

    return {
        "year_month": year_month,
        "status": "OK" if not mismatches else "MISMATCH",
        "n_matched": n_matched,
        "n_mismatched": n_mismatched,
        "mismatches": mismatches
    }

def _selftest() -> bool:
    # Create a synthetic 1m dataset for testing
    registry = {
        "timeframes": {
            "10m": {"unit": "seconds", "seconds": 600}
        }
    }
    
    bars_1m = []
    for i in range(25):
        bars_1m.append({
            "t": i * 60000,
            "o": float(i),
            "h": float(i),
            "l": float(i),
            "c": float(i),
            "v": 1.0
        })

    resampled = resample(bars_1m, "10m", registry)
    
    expected = [
        {"t": 0, "o": 0.0, "h": 9.0, "l": 0.0, "c": 9.0, "v": 10.0, "gap_count": 0, "n_bars": 10},
        {"t": 600000, "o": 10.0, "h": 19.0, "l": 10.0, "c": 19.0, "v": 10.0, "gap_count": 0, "n_bars": 10}
    ]
    
    if resampled != expected:
        print("FAIL: Self-test mismatch")
        print(f"Expected: {expected}")
        print(f"Got:      {resampled}")
        return False
    
    print("PASS: Self-test passed")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--start", default="2022-01")
    parser.add_argument("--end", default="2025-08")
    parser.add_argument("--raw-1m-dir", default="Dumps/backtest/raw_1m_2022/klines")
    parser.add_argument("--raw-1d-dir", default="Dumps/backtest/raw_1d/klines")
    parser.add_argument("--registry", default="MyTradingSys/backtest/layers/timeframe/registry.json")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    
    args = parser.parse_args()
    
    if not _selftest():
        print("Self-test failed. Aborting.")
        sys.exit(1)

    start_date = datetime.strptime(args.start, "%Y-%m")
    end_date = datetime.strptime(args.end, "%Y-%m")
    
    current = start_date
    n_ok = 0
    n_mismatch = 0
    n_skip = 0
    
    while current <= end_date:
        year_month = current.strftime("%Y-%m")
        result = compare_month(
            args.symbol,
            year_month,
            args.raw_1m_dir,
            args.raw_1d_dir,
            args.registry,
            args.tolerance
        )
        
        status = result["status"]
        print(f"{year_month} {status} {result['n_matched']} {result['n_mismatched']}")
        
        if status == "MISMATCH":
            n_mismatch += 1
            mismatches = result["mismatches"][:20]
            for mismatch in mismatches:
                print(f"  MISMATCH: t={mismatch['t']}, field={mismatch['field']}, resampled={mismatch.get('resampled')}, native={mismatch.get('native')}")
        elif status == "OK":
            n_ok += 1
        elif status == "SKIP":
            n_skip += 1
            
        current = datetime(current.year + (1 if current.month == 12 else 0), 
                           1 if current.month == 12 else current.month + 1, 1)
    
    print(f"TOTAL: {n_ok} OK, {n_mismatch} MISMATCH, {n_skip} SKIP")
    
    if n_mismatch > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
