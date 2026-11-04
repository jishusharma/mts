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


# ---------------------------------------------------------------------------
# Spot history extension (2026-11-04): BTCUSDT/ETHUSDT spot klines back to 2017-08 (futures UM only starts 2019-09).
# Layout: <out>/<SYMBOL>/<tf>/klines/<SYMBOL>-<tf>-<stamp>.csv  (load_klines(<out>/<SYMBOL>/<tf>) reads it as is)
# Manifest: <out>/manifest.json  key "SYMBOL/tf/stamp" -> sha256 of the zip (verified against the published .CHECKSUM),
# rows, first/last open, gaps. Existing files with a manifest entry are skipped (resumable).
# ---------------------------------------------------------------------------
import json as _json

SPOT_BASE = "https://data.binance.vision/data/spot"
TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000, "30m": 1800000, "1h": 3600000, "4h": 14400000, "1d": 86400000}
SPOT_START = date(2017, 8, 1)
# rough zipped MB per symbol-month (conservative upper bounds), used only for the disk estimate
_MB_PER_MONTH = {"1m": 3.0, "5m": 0.8, "15m": 0.4, "30m": 0.25, "1h": 0.12, "4h": 0.05, "1d": 0.02}


class ChecksumMismatch(RuntimeError):
    pass


def spot_months(start: date, end: date):
    out, y, m = [], start.year, start.month
    while (y, m) <= (end.year, end.month):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def estimate_gb(symbols, tfs, start: date, end: date) -> float:
    n = len(spot_months(start, end))
    return len(symbols) * n * sum(_MB_PER_MONTH[t] for t in tfs) / 1024


def parse_kline_csv(text: str, tf_ms: int) -> dict:
    """Validate one kline CSV: >=6 numeric columns, strictly increasing open times (us stamps -> ms). Gaps = (prev, next)
    open times more than one bar apart. A non-numeric first line is a header."""
    rows, prev, gaps, first = 0, None, [], None
    for ln, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        cells = line.split(",")
        if ln == 0 and not cells[0].strip().isdigit():
            continue
        if len(cells) < 6:
            raise ValueError(f"bad row (<6 columns): {line[:60]!r}")
        try:
            t = int(cells[0])
            [float(c) for c in cells[1:6]]
        except ValueError as e:
            raise ValueError(f"bad row: {line[:60]!r}") from e
        if t > 10 ** 14:
            t //= 1000
        if prev is not None:
            if t <= prev:
                raise ValueError(f"open times not increasing at {t} (prev {prev})")
            if t - prev > tf_ms:
                gaps.append((prev, t))
        if first is None:
            first = t
        prev, rows = t, rows + 1
    if rows == 0:
        raise ValueError("empty kline file")
    return {"rows": rows, "first_t": first, "last_t": prev, "gaps": gaps}


def _manifest_path(out_root: Path) -> Path:
    return Path(out_root) / "manifest.json"


def load_manifest(out_root: Path) -> dict:
    p = _manifest_path(out_root)
    return _json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _save_manifest(out_root: Path, man: dict) -> None:
    p = _manifest_path(out_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(_json.dumps(man, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    tmp.replace(p)


def fetch_spot_month(sym, tf, stamp, out_root, get, period="monthly") -> str:
    """One archive file (monthly stamp YYYY-MM, or daily YYYY-MM-DD with period='daily'). Returns skip|404|nochecksum|ok.
    Raises ChecksumMismatch (nothing written) when the zip sha256 differs from the published .CHECKSUM."""
    out_root = Path(out_root)
    key = f"{sym}/{tf}/{stamp}"
    d = out_root / sym / tf / "klines"
    name = f"{sym}-{tf}-{stamp}"
    man = load_manifest(out_root)
    if key in man and (d / f"{name}.csv").exists():
        return "skip"
    url = f"{SPOT_BASE}/{period}/klines/{sym}/{tf}/{name}.zip"
    blob = get(url)
    if blob is None:
        return "404"
    chk = get(url + ".CHECKSUM")
    if chk is None:
        return "nochecksum"
    sha = hashlib.sha256(blob).hexdigest()
    if sha != chk.decode().split()[0]:
        raise ChecksumMismatch(f"CHECKSUM MISMATCH {url}")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        if len(names) != 1:
            raise ValueError(f"{url}: expected 1 member, got {names}")
        text = z.read(names[0]).decode("utf-8")
    p = parse_kline_csv(text, TF_MS[tf])
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.csv").write_text(text, encoding="utf-8", newline="\n")
    man = load_manifest(out_root)
    man[key] = {"sha256": sha, "bytes": len(blob), "rows": p["rows"], "first_t": p["first_t"], "last_t": p["last_t"],
                "gaps": p["gaps"]}
    _save_manifest(out_root, man)
    return "ok"


def fetch_spot_history(symbols, tfs, start: date, end: date, out_root, get=None, sleep_s=0.3, daily=False, log=None):
    """Tally dict of statuses. Throttled (sleep_s between network fetches). 404 = month not listed yet (expected before listing)."""
    get = get or _get
    tally = {}
    if daily:
        stamps = [("daily", (start + timedelta(days=k)).isoformat()) for k in range((end - start).days + 1)]
    else:
        stamps = [("monthly", m) for m in spot_months(start, end)]
    for sym in symbols:
        for tf in tfs:
            for period, stamp in stamps:
                s = fetch_spot_month(sym, tf, stamp, out_root, get, period)
                if s != "skip" and sleep_s:
                    time.sleep(sleep_s)
                tally[s] = tally.get(s, 0) + 1
                if log and s != "skip":
                    log(f"{sym} {tf} {stamp} {s}")
    return tally


def main_spot(a) -> int:
    syms = a.symbols.split(",")
    tfs = a.tfs.split(",")
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    est = estimate_gb(syms, tfs, start, end)
    print(f"estimated download {est:.2f} GB (limit {a.max_gb} GB)")
    if est > a.max_gb:
        print("ABORT: estimate over the limit")
        return 2
    try:
        tally = fetch_spot_history(syms, tfs, start, end, Path(a.out_spot), sleep_s=a.sleep, daily=a.daily, log=print)
    except ChecksumMismatch as e:
        print(f"ERROR {e}")
        return 1
    print(f"spot history {tally}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot-history", action="store_true", help="spot klines back to 2017-08 into --out-spot")
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT")
    ap.add_argument("--tfs", default="15m,30m,1h,4h,1d")
    ap.add_argument("--out-spot", default="F:/MTS/Dumps/backtest/spot_2017")
    ap.add_argument("--max-gb", type=float, default=15.0)
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--daily", action="store_true", help="daily archive files (for a short slice)")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--datasets", default="klines,metrics,fundingRate,markPriceKlines,bookDepth")
    ap.add_argument("--out", default=str(ROOT / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--interval", default="1m", help="kline interval, e.g. 1m, 1h, 1d")
    a = ap.parse_args()
    if a.spot_history:
        return main_spot(a)
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
