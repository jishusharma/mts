"""DAX (Dukascopy DEUIDXEUR, free CFD feed) 1m bars -> the Binance-style 1m kline archive the engine reads.

Operator 2026-10-11 approved the free Dukascopy feed for the Tom DAX probe (research/tom_transfer_2026-10-11/PROBE_PLAN.md).
Usage:
  python -I MyTradingSys/backtest/dax_data.py fetch   --start 2025-01-01 --end 2026-10-10 --raw F:/MTS/data/dax_raw
  python -I MyTradingSys/backtest/dax_data.py convert --raw F:/MTS/data/dax_raw --out F:/MTS/data/dax_archive [--symbol GER40]
Feed format (BID_candles_min_1.bi5): LZMA; records of 24 bytes big-endian >5i1f: seconds from 00:00 UTC of the day, open,
close, low, high (int, price * 1000 for this instrument: checked against the 2025 DAX range), volume (float, the feed's own
volume unit for a CFD: not exchange volume). Days are UTC; the month in the URL is 0-based.
Output: <out>/klines/GER40-1m-YYYY-MM.csv rows `open_ms,o,h,l,c,volume,close_ms,quote_vol,count,taker_buy_vol,taker_buy_quote` (the fields
ArchiveHistoricalSource reads). Minutes the feed does not print (market closed) are NOT forward-filled; a minute with zero
volume and o=h=l=c (Dukascopy's closed-market filler) is dropped. Raw files are untrusted data: run with python -I.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import lzma
import struct
import sys
import time
import urllib.request
from pathlib import Path

URL = "https://datafeed.dukascopy.com/datafeed/{inst}/{y:04d}/{m0:02d}/{d:02d}/{side}_candles_min_1.bi5"
INST = "DEUIDXEUR"
SCALE = 1000.0
REC = struct.Struct(">5if")


def day_url(day, inst=INST, side="BID"):
    side = side.upper()
    if side not in ("BID", "ASK"):
        raise ValueError("side must be BID or ASK")
    return URL.format(inst=inst, y=day.year, m0=day.month - 1, d=day.day, side=side)


def parse_bi5(blob, day, side="BID"):
    """Bytes of one day's .bi5 -> [(open_ms, o, h, l, c, v)], dropping closed-market filler minutes."""
    if side.upper() not in ("BID", "ASK"):
        raise ValueError("side must be BID or ASK")
    if not blob:
        return []
    raw = lzma.decompress(blob)
    base = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp()) * 1000
    out = []
    for k in range(0, len(raw) - REC.size + 1, REC.size):
        sec, o, c, lo, hi, v = REC.unpack_from(raw, k)
        if v == 0 and o == c == lo == hi:
            continue
        out.append((base + sec * 1000, o / SCALE, hi / SCALE, lo / SCALE, c / SCALE, float(v)))
    return out


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
           "Referer": "https://freeserv.dukascopy.com/2.0/"}


def fetch(start, end, raw, workers=1, pause=1.0, side="BID"):
    """The feed rate-limits (429/503): one worker, a pause per request, backoff on refusals."""
    raw.mkdir(parents=True, exist_ok=True)
    days = [start + dt.timedelta(n) for n in range((end - start).days + 1)]

    def one(day):
        f = raw / f"{day:%Y-%m-%d}.bi5"
        if f.exists():
            return day, "have"
        for attempt in range(8):
            time.sleep(pause)
            try:
                with urllib.request.urlopen(urllib.request.Request(day_url(day, side=side), headers=HEADERS), timeout=30) as r:
                    f.write_bytes(r.read())
                return day, "ok"
            except Exception as e:  # 404 = no file for that day; retry refusals and transient errors
                if getattr(e, "code", None) == 404:
                    f.write_bytes(b"")
                    return day, "404"
                time.sleep(min(60, 3 * 2 ** attempt))
        return day, "fail"

    stats = {}
    with cf.ThreadPoolExecutor(workers) as ex:
        for day, st in ex.map(one, days):
            stats[st] = stats.get(st, 0) + 1
            if st == "fail":
                print("FAIL", day, file=sys.stderr)
    print("fetch", stats)
    return stats


def spreads(bid_raw, ask_raw):
    """Join parsed BID and ASK rows on exact open_ms; return [(open_ms, ask_close-bid_close)]."""
    bid = {row[0]: row[4] for row in bid_raw}
    ask = {row[0]: row[4] for row in ask_raw}
    return [(t, ask[t] - bid[t]) for t in sorted(bid.keys() & ask.keys())]


def convert(raw, out, symbol="GER40", end_ms=None):
    """Raw .bi5 days -> monthly kline CSVs. With end_ms only complete bars that close by end_ms are decoded and
    written; later raw days are not read, and a leftover archive month wholly at/after end_ms is refused."""
    kd = out / "klines"
    kd.mkdir(parents=True, exist_ok=True)
    if end_ms is not None:
        for p in sorted(kd.glob(f"{symbol}-1m-*.csv")):
            ym = p.stem.rsplit("-1m-", 1)[1]
            month_start = int(dt.datetime(int(ym[:4]), int(ym[5:7]), 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
            if month_start >= end_ms:
                raise ValueError("archive month %s starts at/after the authorized cutoff; use a fresh archive directory" % p)
    months, days_with_bars = {}, 0
    for f in sorted(raw.glob("*.bi5")):
        day = dt.date.fromisoformat(f.stem)
        if end_ms is not None and int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp() * 1000) >= end_ms:
            continue
        rows = parse_bi5(f.read_bytes(), day)
        if end_ms is not None:
            rows = [r for r in rows if r[0] + 60000 <= end_ms]
        if rows:
            days_with_bars += 1
        months.setdefault(f"{day:%Y-%m}", []).extend(rows)
    n = 0
    for ym, rows in sorted(months.items()):
        rows.sort()
        with open(kd / f"{symbol}-1m-{ym}.csv", "w", newline="\n", encoding="utf-8") as w:
            for t, o, h, lo, c, v in rows:
                # No aggressor split in a CFD feed: taker-buy = half the volume keeps kline-derived delta/CVD at 0
                # (neutral, the order-flow proofs cannot fire) instead of reading every bar as all-sell (tbv 0).
                # volume prints with 6 decimals and the engine computes delta = 2 * takerBuy - volume: taker-buy needs 7
                # decimals (half of a 6-decimal number) or the rounding leaves delta = +-1e-6 and the order-flow proofs
                # fire on noise (volumes here are as small as 0.001).
                vs = f"{v:.6f}"
                w.write(f"{t},{o:.3f},{h:.3f},{lo:.3f},{c:.3f},{vs},{t + 59999},{v * c:.4f},0,{float(vs) / 2:.7f},{v * c / 2:.4f}\n")
        n += len(rows)
    print(f"convert {symbol}: {n} bars, {days_with_bars} days with bars, {len(months)} month files -> {kd}")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("fetch"); a.add_argument("--start", required=True); a.add_argument("--end", required=True)
    a.add_argument("--raw", required=True); a.add_argument("--workers", type=int, default=1)
    a.add_argument("--pause", type=float, default=1.0); a.add_argument("--side", choices=("BID", "ASK"), default="BID")
    b = sp.add_parser("convert"); b.add_argument("--raw", required=True); b.add_argument("--out", required=True)
    b.add_argument("--symbol", default="GER40")
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--end-ms", type=int, default=None, help="authorized development cutoff (epoch ms); later bars are never decoded")
    g.add_argument("--read-holdout", action="store_true", help="explicitly authorized unbounded conversion")
    c = sp.add_parser("spread"); c.add_argument("--bid-raw", required=True); c.add_argument("--ask-raw", required=True)
    c.add_argument("--day", required=True, help="UTC date (YYYY-MM-DD)")
    x = ap.parse_args(argv)
    if x.cmd == "fetch":
        fetch(dt.date.fromisoformat(x.start), dt.date.fromisoformat(x.end), Path(x.raw), x.workers, x.pause, x.side)
    elif x.cmd == "convert":
        convert(Path(x.raw), Path(x.out), x.symbol, x.end_ms)
    else:
        day = dt.date.fromisoformat(x.day)
        bid_path = Path(x.bid_raw) / f"{day:%Y-%m-%d}.bi5"
        ask_path = Path(x.ask_raw) / f"{day:%Y-%m-%d}.bi5"
        if not bid_path.exists() or not ask_path.exists():
            raise SystemExit(f"missing raw day: BID={bid_path.exists()} ASK={ask_path.exists()}")
        bid_rows = parse_bi5(bid_path.read_bytes(), day)
        ask_rows = parse_bi5(ask_path.read_bytes(), day, side="ASK")
        for open_ms, spread in spreads(bid_rows, ask_rows):
            print(f"{open_ms},{spread:.6f}")


if __name__ == "__main__":
    main()
