"""Read-only data-quality check over the raw 1m kline CSVs (studies/_bars.py:97: resample leaves
missing minutes simply absent -- a silent hole there mis-fills every study's stops and targets).

check() is a pure function over raw open-time rows exactly as read off disk: unsorted, possibly
duplicated -- never run them through _bars.load_1m first, since that sorts and de-duplicates and
would hide the very rows this check exists to find.

main() reads each symbol's raw klines for the DEV window (2022-04-01..2024-06-30) from the shared
klines folder and prints counts only. No price data is ever printed or committed (public repo).

python MyTradingSys/research/sim_desk/data_check.py
"""
import csv
import datetime as dt
import os
import sys
from pathlib import Path

MIN_MS = 60000
DAY_MS = 86400000
ROOT = Path(os.environ.get('SIM_DESK_KLINES', 'F:/MTS/data/tom_raw/klines'))

# Sealed cut: no row at or after this is ever read (matches studies/_bars.py's CUT_MS / fetch_klines.py's CUT_MS).
CUT_MS = (dt.date(2024, 7, 1) - dt.date(1970, 1, 1)).days * DAY_MS
DEV_START_MS = (dt.date(2022, 4, 1) - dt.date(1970, 1, 1)).days * DAY_MS
DEV_END_MS = CUT_MS   # DEV window is 2022-04-01..2024-06-30 inclusive; end is exclusive at the cut

SYMBOLS = ('BTCUSDT', 'ETHUSDT')
_MONTHS_FIRST, _MONTHS_LAST = '2022-04', '2024-06'


def _months(first=_MONTHS_FIRST, last=_MONTHS_LAST):
    y, m = map(int, first.split('-'))
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def check(rows, start_ms, end_ms):
    """rows: raw open-time values in ms, in file order (not sorted, not de-duplicated).

    Returns {'expected', 'present', 'missing', 'duplicates', 'out_of_order', 'longest_gap'} -- counts
    only, no prices. `expected`/`present`/`missing`/`longest_gap` are over the 1-minute grid
    [start_ms, end_ms); `duplicates`/`out_of_order` are over the full row sequence as given.

    Raises ValueError (never sanitises) if any row is at or after the sealed cut -- a look-ahead
    guard: this must trip regardless of the start_ms/end_ms window asked for.
    """
    ts = [int(r) for r in rows]
    for t in ts:
        if t >= CUT_MS:
            raise ValueError(f'row {t} is at or after the sealed cut {CUT_MS} (2024-07-01 UTC); refusing')

    out_of_order = sum(1 for i in range(1, len(ts)) if ts[i] < ts[i - 1])

    seen = set()
    duplicates = 0
    for t in ts:
        if t in seen:
            duplicates += 1
        else:
            seen.add(t)

    expected = max(0, (end_ms - start_ms) // MIN_MS)
    present = sum(1 for t in seen if start_ms <= t < end_ms)
    missing = expected - present

    longest_gap = 0
    run = 0
    t = start_ms
    while t < end_ms:
        if t in seen:
            run = 0
        else:
            run += 1
            longest_gap = max(longest_gap, run)
        t += MIN_MS

    return {'expected': expected, 'present': present, 'missing': missing,
            'duplicates': duplicates, 'out_of_order': out_of_order, 'longest_gap': longest_gap}


def _raw_open_times(path):
    """The first column of each data row, in file order -- no sort, no dedup (that's the point)."""
    with open(path, encoding='utf-8', newline='') as fh:
        first_line = fh.readline()
        fh.seek(0)
        reader = csv.reader(fh)
        all_rows = list(reader)
    skip = 0 if first_line[:1].isdigit() else 1
    return [int(r[0]) for r in all_rows[skip:] if r]


def _symbol_rows(symbol, root=ROOT):
    rows = []
    for m in _months():
        p = Path(root) / f'{symbol}-1m-{m}.csv'
        if not p.exists():
            raise FileNotFoundError(p)
        rows.extend(_raw_open_times(p))
    return rows


def main():
    if not Path(ROOT).exists():
        print('NOT_IN_DATA: klines folder absent on this machine:', ROOT)
        return
    for symbol in SYMBOLS:
        try:
            rows = _symbol_rows(symbol)
        except FileNotFoundError as e:
            print(symbol, 'NOT_IN_DATA:', e)
            continue
        counts = check(rows, DEV_START_MS, DEV_END_MS)
        print(symbol, counts)


if __name__ == '__main__':
    sys.exit(main())
