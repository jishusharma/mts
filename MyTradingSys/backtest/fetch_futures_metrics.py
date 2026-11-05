import sys
sys.dont_write_bytecode = True
"""
MyTradingSys/backtest/fetch_futures_metrics.py  (card metrics-oi-toptrader-into-shared-data, 2026-11-05)

Fetches Binance USD-M futures 5m `metrics` daily files (open interest, top-trader
account and position long/short ratios, global long/short ratio, taker vol ratio)
from the public archive data.binance.vision into ONE shared data root, so every
station and study reads the same copy. Public archive only: no API keys, no
account endpoints.

Data root (never hard-coded): --root, else env MTS_METRICS_ROOT, else
env MTS_DATA_ROOT + "/metrics". Fleet convention: F:/MTS/data/metrics.
Layout: <root>/<SYMBOL>/<SYMBOL>-metrics-YYYY-MM-DD.csv (SHA256-verified, zip dropped).
A re-run skips files already present (idempotent). Gaps are listed per month:
missing days (archive 404) and short days (< 288 five-minute rows).

Run:
  python MyTradingSys/backtest/fetch_futures_metrics.py --symbols BTCUSDT,ETHUSDT --start 2022-01-01
  python MyTradingSys/backtest/fetch_futures_metrics.py --gaps-only --symbols BTCUSDT
"""
import argparse, hashlib, io, os, time, urllib.error, urllib.request, zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = "https://data.binance.vision/data/futures/um/daily/metrics"
ROWS_PER_DAY = 288  # SOURCED: 24h / 5m archive cadence


def resolve_root(cli_root=None, env=None):
    env = os.environ if env is None else env
    if cli_root:
        return Path(cli_root)
    if env.get("MTS_METRICS_ROOT"):
        return Path(env["MTS_METRICS_ROOT"])
    if env.get("MTS_DATA_ROOT"):
        return Path(env["MTS_DATA_ROOT"]) / "metrics"
    raise SystemExit("no data root: pass --root or set MTS_METRICS_ROOT / MTS_DATA_ROOT")


def http_get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MTS-metrics/1.0"})
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


def csv_name(sym, day):
    return f"{sym}-metrics-{day.isoformat()}.csv"


def fetch_day(sym, day, root, get=http_get):
    out = Path(root) / sym
    if (out / csv_name(sym, day)).exists():
        return "skip"
    url = f"{BASE}/{sym}/{sym}-metrics-{day.isoformat()}.zip"
    blob = get(url)
    if blob is None:
        return "404"
    chk = get(url + ".CHECKSUM")
    if chk is None:
        return "nochecksum"
    if hashlib.sha256(blob).hexdigest() != chk.decode().split()[0]:
        raise RuntimeError(f"CHECKSUM MISMATCH {url}")
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        z.extractall(out)
    return "ok"


def days(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def list_gaps(sym, root, start, end):
    """Per month: {'YYYY-MM': {'expected', 'present', 'missing': [iso], 'short': {iso: rows}}}."""
    out, folder = {}, Path(root) / sym
    for d in days(start, end):
        m = out.setdefault(d.strftime("%Y-%m"), {"expected": 0, "present": 0, "missing": [], "short": {}})
        m["expected"] += 1
        p = folder / csv_name(sym, d)
        if not p.exists():
            m["missing"].append(d.isoformat())
            continue
        m["present"] += 1
        with p.open(encoding="utf-8") as f:
            rows = sum(1 for _ in f) - 1
        if rows < ROWS_PER_DAY:
            m["short"][d.isoformat()] = rows
    return out


def run(symbols, start, end, root, get=http_get, workers_sleep=0.0):
    counts = {}
    for sym in symbols:
        c = counts.setdefault(sym, {})
        for d in days(start, end):
            r = fetch_day(sym, d, root, get=get)
            c[r] = c.get(r, 0) + 1
            if r == "ok" and workers_sleep:
                time.sleep(workers_sleep)
    return counts


def format_gaps(sym, gaps):
    lines = [f"{sym} month expected present missing short"]
    for month, g in gaps.items():
        if g["missing"] or g["short"]:
            lines.append(f"{sym} {month} {g['expected']} {g['present']} "
                         f"{','.join(x[-2:] for x in g['missing']) or '-'} "
                         f"{','.join(f'{k[-2:]}:{v}' for k, v in g['short'].items()) or '-'}")
    total_missing = sum(len(g["missing"]) for g in gaps.values())
    total_short = sum(len(g["short"]) for g in gaps.values())
    lines.append(f"{sym} TOTAL days={sum(g['expected'] for g in gaps.values())} missing={total_missing} short={total_short}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT")
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None, help="default: yesterday UTC")
    ap.add_argument("--root", default=None)
    ap.add_argument("--gaps-only", action="store_true")
    a = ap.parse_args(argv)
    root = resolve_root(a.root)
    start = date.fromisoformat(a.start)
    end = date.fromisoformat(a.end) if a.end else datetime.now(timezone.utc).date() - timedelta(days=1)
    syms = [s.strip().upper() for s in a.symbols.split(",") if s.strip()]
    if not a.gaps_only:
        for sym, c in run(syms, start, end, root).items():
            print(sym, " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    for sym in syms:
        print(format_gaps(sym, list_gaps(sym, root, start, end)))


if __name__ == "__main__":
    main()
