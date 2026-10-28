"""Fetch public Binance spot BTCUSDT 1d/1h klines from data.binance.vision to MTS_DUMPS.

Covers 2020-01 through 2025-06 (66 months). Sealed window 2025-07+ is strictly NOT fetched.
Verifies SHA256 against official .CHECKSUM files for every downloaded archive.
"""
import os, sys, urllib.request, hashlib, io, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DUMPS = os.environ.get("MTS_DUMPS", r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest")
SYMBOL = "BTCUSDT"
BASE = "https://data.binance.vision/data/spot/monthly/klines"

# Months 2020-01 to 2025-06 (66 months)
MONTHS = []
for y in range(2020, 2026):
    for m in range(1, 13):
        if y == 2025 and m > 6:
            break
        MONTHS.append(f"{y}-{m:02d}")


def fetch_month(interval, stamp):
    out_dir = Path(DUMPS) / f"spot_{interval}" / "klines"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_file = out_dir / f"{SYMBOL}-{interval}-{stamp}.csv"
    if csv_file.exists():
        return f"{interval} {stamp}: skip"

    url = f"{BASE}/{SYMBOL}/{interval}/{SYMBOL}-{interval}-{stamp}.zip"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MTS-carry-basis/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            blob = r.read()
    except Exception as e:
        return f"{interval} {stamp}: ERROR download {e}"

    chk_url = url + ".CHECKSUM"
    try:
        req_chk = urllib.request.Request(chk_url, headers={"User-Agent": "MTS-carry-basis/1.0"})
        with urllib.request.urlopen(req_chk, timeout=30) as r:
            chk_text = r.read().decode("utf-8").strip()
            chk_expected = chk_text.split()[0]
    except Exception as e:
        return f"{interval} {stamp}: ERROR checksum fetch {e}"

    calc = hashlib.sha256(blob).hexdigest()
    if calc.lower() != chk_expected.lower():
        raise RuntimeError(f"Checksum mismatch for {url}: expected {chk_expected}, got {calc}")

    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        z.extractall(out_dir)

    return f"{interval} {stamp}: OK (sha256 verified)"


def run():
    print(f"Target dumps: {DUMPS}")
    print(f"Fetching {len(MONTHS)} months (2020-01..2025-06) for 1d and 1h spot...")
    tasks = []
    for iv in ("1d", "1h"):
        for m in MONTHS:
            tasks.append((iv, m))

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda t: fetch_month(*t), tasks))

    errs = [r for r in results if "ERROR" in r]
    print(f"Completed {len(results)} tasks. Errors: {len(errs)}")
    if errs:
        for e in errs:
            print("  ", e)
        sys.exit(1)


if __name__ == "__main__":
    run()
