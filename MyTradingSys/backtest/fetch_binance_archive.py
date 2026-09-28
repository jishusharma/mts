import sys
sys.dont_write_bytecode = True
"""
MyTradingSys/backtest/fetch_binance_archive.py  (T051 data layer, 2026-09-27)

Bulk, free, checksummed history from Binance's official archive
(data.binance.vision) for BTCUSDT USD-M perpetual - the same venue/symbol
MTS computes signals on. Replaces fetch_bars.py's paged REST crawl for
anything longer than a few days (no rate limits, SHA256-verified, resumable).

Datasets (key -> what MTS layer it feeds):
  klines          1m OHLCV + taker_buy_volume   -> price path, structure, VWAP, CVD (exact at 1m)
  aggTrades       every aggregated trade        -> exact volume profile / CVD (LARGE: ~0.1-0.3 GB/day zipped)
  metrics         5m OI + long/short ratios     -> oi_trend, oi_breakdown
  fundingRate     8h funding (monthly files)    -> funding, funding_extreme
  bookDepth       +-1..5% depth bands, ~30-60s  -> book-imbalance PROXY (not top-of-book; see handoff)
  markPriceKlines 1m mark                        -> stop-trigger realism (Deribit stops trigger on mark)
  premiumIndexKlines 1m premium                  -> basis/premium context

Layout: <repo>/Dumps/backtest/raw/<dataset>/<file>.csv  (zip deleted after verify+extract)
Skips files already extracted -> safe to re-run / resume.

Run (desktop or NUC, needs internet):
  python MyTradingSys/backtest/fetch_binance_archive.py --start 2025-09-01 --end 2026-09-26
  python MyTradingSys/backtest/fetch_binance_archive.py --start 2026-09-01 --end 2026-09-26 --datasets klines,metrics,fundingRate,bookDepth,aggTrades
Default datasets: klines,metrics,fundingRate,markPriceKlines,bookDepth (aggTrades opt-in: size).
"""
import argparse, hashlib, io, urllib.request, urllib.error, zipfile, time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://data.binance.vision/data/futures/um"
SYM = "BTCUSDT"
MONTHLY_OK = {"klines", "aggTrades", "fundingRate", "markPriceKlines", "premiumIndexKlines"}
DAILY_ONLY = {"metrics", "bookDepth"}
INTERVAL = {"klines", "markPriceKlines", "premiumIndexKlines"}
BAR = "1m"  # --interval (1m default; 1d for multi-year layer backtests)


def _get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MTS-T051-archive/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == retries - 1:
                raise
        except Exception:
            if i == retries - 1:
                raise
        time.sleep(2 ** i)


def _url(ds, period, stamp):
    iv = f"/{BAR}" if ds in INTERVAL else ""
    name = f"{SYM}-{BAR}-{stamp}" if ds in INTERVAL else f"{SYM}-{ds}-{stamp}"
    return f"{BASE}/{period}/{ds}/{SYM}{iv}/{name}.zip"


def fetch_one(ds, period, stamp, out: Path) -> str:
    url = _url(ds, period, stamp)
    csv_name = url.rsplit("/", 1)[1].replace(".zip", ".csv")
    if (out / csv_name).exists():
        return "skip"
    blob = _get(url)
    if blob is None:
        return "404"
    chk = _get(url + ".CHECKSUM")
    if chk is None:
        return "nochecksum"
    if hashlib.sha256(blob).hexdigest() != chk.decode().split()[0]:
        raise RuntimeError(f"CHECKSUM MISMATCH {url}")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        z.extractall(out)
    return "ok"


def plan(ds, start: date, end: date):
    """Full calendar months inside [start,end] -> monthly files (when offered); edges -> daily."""
    jobs, d = [], start
    while d <= end:
        m_end = (date(d.year + (d.month == 12), d.month % 12 + 1, 1) - timedelta(days=1))
        if ds in MONTHLY_OK and d.day == 1 and m_end <= end:
            jobs.append(("monthly", d.strftime("%Y-%m")))
            d = m_end + timedelta(days=1)
        elif ds == "fundingRate":  # monthly only
            jobs.append(("monthly", d.strftime("%Y-%m")))
            d = m_end + timedelta(days=1)
        else:
            jobs.append(("daily", d.isoformat()))
            d += timedelta(days=1)
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--datasets", default="klines,metrics,fundingRate,markPriceKlines,bookDepth")
    ap.add_argument("--out", default=str(ROOT / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--interval", default="1m", help="kline interval, e.g. 1m, 1h, 1d")
    a = ap.parse_args()
    global BAR
    BAR = a.interval
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    bad = 0
    for ds in a.datasets.split(","):
        out = Path(a.out) / ds
        out.mkdir(parents=True, exist_ok=True)
        tally = {}
        for period, stamp in plan(ds, start, end):
            try:
                s = fetch_one(ds, period, stamp, out)
            except Exception as e:  # noqa: BLE001
                s = "ERROR"
                bad += 1
                print(f"  ERROR {ds} {stamp}: {e}")
            tally[s] = tally.get(s, 0) + 1
        print(f"{ds:20s} {tally}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
