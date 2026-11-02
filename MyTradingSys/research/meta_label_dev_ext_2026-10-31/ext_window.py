"""Window loader for the Fabio Model C dev_ext rerun (PRE_REG_EXT.md): 1m bars with open in [2020-01-01, 2022-04-01) only.

2020-01..2021-12 from F:/MTS/data/dev_ext_2019_2021/klines, 2022-01..03 from the desk's own files (warm-up months before DEV 2022-04-01).
Nothing at or after CUT_MS is ever returned; the loader raises instead of trimming silently when a source month leaks past it.
"""
import datetime as dt
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE.parent
sys.path.insert(0, str(RES / 'sim_desk'))
sys.path.insert(0, str(RES / 'sim_desk' / 'studies'))
sys.path.insert(0, str(RES / 'context_factors_2026-10-16'))
sys.path.insert(0, str(RES / 'meta_label_tom_fabio_2026-10-31'))
import _bars  # noqa: E402
import dev_ext  # noqa: E402
import fabio_v3  # noqa: E402
import tom_vp  # noqa: E402

DAY = 86400000
CUT_MS = (dt.date(2022, 4, 1) - dt.date(1970, 1, 1)).days * DAY      # first millisecond NOT read
EXT_START_MS = dev_ext.DEV_EXT_START_MS                               # 2020-01-01
FIRST_TRADE_DAY, LAST_TRADE_DAY = '2020-01-02', '2022-03-31'
EXT_FUND_DIR = Path('F:/MTS/data/dev_ext_2019_2021/funding')
DEV_FUND_ZIPS = Path('F:/MTS/data/candle_close_dev_2022_2024')


def guard(ts, what, cut=CUT_MS):
    a = np.asarray(ts, float)
    if a.size and not a.max() < cut:
        raise ValueError(f'{what}: timestamp {int(a.max())} is at or after the window cut {cut} (2022-04-01 UTC); refusing')
    return ts


def load_window(cut_ms=CUT_MS):
    """(a6, a5): 1m arrays [open ms, o, h, l, c, volume] and the first five columns, sorted, no duplicates, open < cut_ms.
    cut_ms exists only so the test can build a deliberately too-wide variant; production calls use the default."""
    m = dev_ext.load_ext_1m()
    ext = m[['ot', 'o', 'h', 'l', 'c', 'v']].to_numpy(float)
    parts = [ext] + [tom_vp._month_v(f'2022-{k:02d}', 'BTCUSDT') for k in (1, 2, 3)]
    a = np.concatenate(parts)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    a = a[(a[:, 0] >= EXT_START_MS) & (a[:, 0] < cut_ms)]
    return a, a[:, :5]


def load_funding():
    import csv
    import io
    import zipfile
    import features as F
    t1, r1 = F.load_funding('2020-01', '2021-12', folder=EXT_FUND_DIR)
    ts, rs = [], []
    for k in (1, 2, 3):
        z = zipfile.ZipFile(DEV_FUND_ZIPS / f'BTCUSDT-fundingRate-2022-{k:02d}.zip')
        for row in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8')):
            if row and row[0].isdigit():
                ts.append(int(row[0]))
                rs.append(float(row[2]))
    t = np.r_[t1, np.array(ts, np.int64)]
    r = np.r_[r1, np.array(rs, float)]
    o = np.argsort(t, kind='stable')
    t, r = t[o], r[o]
    guard(t, 'funding')
    return t, r


def install(a6, a5):
    """Point the unchanged studies at the window bars and pre-fill Fabio's idea cache for the window days (same logic as
    fabio_v3.ideas with the two dates changed). Returns the normalised Model C query with start/end set to the window."""
    guard(a6[:, 0], 'window bars')
    _bars._ALL['BTCUSDT'] = a5
    tom_vp._ALLV['BTCUSDT'] = a6
    q = fabio_v3.normalize({'model': 'C'})
    q['start'], q['end'] = FIRST_TRADE_DAY, LAST_TRADE_DAY
    key = (q['model'], (q['m'], q['push']))
    out = []
    for d in range(_bars.day_ms(FIRST_TRADE_DAY) // DAY, _bars.day_ms(LAST_TRADE_DAY) // DAY + 1):
        o = fabio_v3.ny_open_utc(dt.date(1970, 1, 1) + dt.timedelta(days=d))
        if o is None:
            continue
        o_ms = int(o.timestamp() * 1000)
        got = fabio_v3._day_bars(a6, o_ms, 0)
        if got is None:
            continue
        bars, oi = got
        c = fabio_v3._ideas_c(bars, oi, q['m'], q['push'])
        if c:
            out.append((o_ms, c))
    fabio_v3._IDEAS.clear()
    fabio_v3._IDEAS[key] = out
    return q
