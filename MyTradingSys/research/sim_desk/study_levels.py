"""Desk study 1: first touches of 8 price levels on BTCUSDT 1m (card lc-ladder-dev), re-simulated with any setting.

A study module gives the desk: ID, TITLE, params(), normalize(p), label(p), describe(p), run(p, progress) and
trade_bars(ref) for the charts. This one wraps levels_confluence_2026-10-14/ladder.py and ladder_run.py unchanged.

The first run builds a local idea cache once (every first touch plus that day's 1m bars, DEV months only, in
parallel); cache/ is gitignored because the repo is public. After that a run re-simulates every idea in seconds.
"""
import datetime as dt
import hashlib
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / 'levels_confluence_2026-10-14'
sys.path.insert(0, str(STUDY))
import ladder as ld  # noqa: E402
import ladder_run as lr  # noqa: E402

ID = 'levels'
TITLE = 'Price levels: first touch of a level, BTCUSDT 1m'
PRIOR_TAG = 'lc-ladder-dev'   # the original study's TRIALS.md rows (same data, 243 setups)
ROOT = os.environ.get('SIM_DESK_KLINES', 'F:/MTS/data/tom_raw/klines')
DEV_FIRST, DEV_LAST = '2022-04-01', '2024-06-30'
CODE_FILES = ('ladder.py', 'ladder_run.py', 'levels.py', 'event_table.py')
DAY = 86400000

ENTRY = {'E0': 'every first touch', 'E1': 'only when 5m RSI holds 40 (long) / 60 (short)', 'E4': 'only at the outer Bollinger band'}
SCALE = {'S0': 'all in at the touched level', 'S1': 'half at the level, half at the next level beyond',
         'S2': 'all in at the next level beyond (wait for a deeper fill)', 'S3': 'one third at the level, two thirds at the next level'}
STOP = {'K1': 'just past the deepest entry', 'K2': 'just past the next level beyond', 'K3': 'half an hourly ATR past the next level',
        'K4': 'on a 15m close past the next level', 'K5': "just past today's extreme"}
EXIT = {'X0_1R': 'target 1 x risk', 'X0_2R': 'target 2 x risk', 'X1': 'target the first level in favour',
        'X2': 'half at the first level in favour, rest by order flow', 'R': 'target at a chosen multiple of risk'}
DEFAULT = {'entry': 'E1', 'scale': 'S2', 'stop': 'K5', 'stop_pct': ld.MARGIN * 100, 'exit': 'X0_2R', 'target_r': 2.0,
           'maker_pct': ld.MAKER * 100, 'taker_pct': ld.TAKER * 100, 'start': DEV_FIRST, 'end': DEV_LAST}


def params():
    """Fields for the settings strip. Choices plus free-form numbers (hit and try)."""
    return [
        {'name': 'entry', 'label': 'Which touches', 'choices': ENTRY},
        {'name': 'scale', 'label': 'How to enter', 'choices': SCALE},
        {'name': 'stop', 'label': 'Stop', 'choices': STOP},
        {'name': 'stop_pct', 'label': 'Stop distance past it, %', 'number': True, 'min': 0.0, 'max': 5.0, 'step': 0.01},
        {'name': 'exit', 'label': 'Exit', 'choices': EXIT},
        {'name': 'target_r', 'label': 'Target, x risk (for "chosen multiple")', 'number': True, 'min': 0.1, 'max': 20.0, 'step': 0.1},
        {'name': 'maker_pct', 'label': 'Limit fee, %', 'number': True, 'min': 0.0, 'max': 1.0, 'step': 0.001},
        {'name': 'taker_pct', 'label': 'Market fee, %', 'number': True, 'min': 0.0, 'max': 1.0, 'step': 0.001},
        {'name': 'start', 'label': 'From', 'date': True, 'min': DEV_FIRST, 'max': DEV_LAST},
        {'name': 'end', 'label': 'To', 'date': True, 'min': DEV_FIRST, 'max': DEV_LAST},
    ]


def normalize(p):
    """Fill defaults, type and validate; raises ValueError on a bad value or a date outside DEV."""
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('entry', ENTRY), ('scale', SCALE), ('stop', STOP), ('exit', EXIT)):
        if q[k] not in table:
            raise ValueError(f'{k}: unknown choice {q[k]!r}')
    for f in params():
        if f.get('number') and not (f['name'] == 'target_r' and q['exit'] != 'R'):
            try:
                v = float(q[f['name']])
            except (TypeError, ValueError):
                raise ValueError(f"{f['label']}: please type a number")
            if not (f['min'] <= v <= f['max']) or v != v:
                raise ValueError(f"{f['label']}: {v} is outside {f['min']}..{f['max']}")
            q[f['name']] = round(v, 6)
    if q['exit'] != 'R':
        q['target_r'] = None
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    """Short code for the ledger row (codes are the study's own pre-registered names)."""
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else q['exit']
    return (f"{q['entry']} {q['scale']} {q['stop']} {ex} stop+{q['stop_pct']:g}% fees {q['maker_pct']:g}/{q['taker_pct']:g}% "
            f"{q['start']}..{q['end']}")


def describe(q):
    """Plain words, no study codes."""
    ex = f"target {q['target_r']:g} x risk" if q['exit'] == 'R' else EXIT[q['exit']]
    return (f"Trade {ENTRY[q['entry']]}; {SCALE[q['scale']]}; stop {STOP[q['stop']]} (+{q['stop_pct']:g} %); {ex}; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market; {q['start']} to {q['end']}.")


# ---- idea cache ----
def _code_hash():
    h = hashlib.sha256()
    for name in CODE_FILES:
        h.update((STUDY / name).read_bytes())
    return h.hexdigest()[:12]


def cache_dir():
    return HERE / 'cache' / ID / f'ideas_{_code_hash()}'


def _months():
    return lr.months()


def _month_file(m_start):
    return cache_dir() / f'{dt.datetime.fromtimestamp(m_start / 1000, dt.timezone.utc):%Y-%m}.pkl'


def cache_ready():
    try:
        return all(_month_file(a).exists() for a, _ in _months())
    except OSError:
        return False


def _build_month(args):
    root, m_start, m_end, out = args
    lr.ARMS = []        # skip the 240-arm grid inside the study runner: only the ideas are needed here
    recs = lr.ideas_for_month(root, m_start, m_end)
    bars = lr.load_range(root, m_start, m_end)
    assert not bars or bars[-1]['t'] < lr.ms(lr.DEV_END), 'read past DEV'
    byday = {}
    for b in bars:
        byday.setdefault(b['t'] // DAY, []).append((b['t'], b['o'], b['h'], b['l'], b['c'], b['v'], b['tbv']))
    ideas = [{k: r[k] for k in ('day', 'touch_t', 'touch_i', 'side', 'L1', 'L2', 'T1', 'T2', 'atr1h', 'E1', 'E4', 'families')}
             for r in recs]
    blob = {'ideas': ideas, 'bars': {d: np.array(v, dtype=float) for d, v in byday.items()}}
    tmp = Path(out).with_suffix('.tmp')
    tmp.write_bytes(pickle.dumps(blob, protocol=pickle.HIGHEST_PROTOCOL))
    os.replace(tmp, out)
    return len(ideas)


def build_cache(progress=print, root=ROOT):
    """One-time build of the idea cache, months in parallel. DEV months only (the study's own month list)."""
    if not Path(root).exists():
        raise FileNotFoundError(f'1m bars not found at {root}')
    cache_dir().mkdir(parents=True, exist_ok=True)
    todo = [(root, a, b, str(_month_file(a))) for a, b in _months() if not _month_file(a).exists()]
    if not todo:
        return
    t0 = time.time()
    progress(f'Building the data cache once: {len(todo)} months...')
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        for k, n in enumerate(ex.map(_build_month, todo), 1):
            progress(f'cache {k}/{len(todo)} months ({time.time() - t0:.0f} s)')


def _load_month(m_start):
    return pickle.loads(_month_file(m_start).read_bytes())


def _daybars(arr):
    return [{'t': int(r[0]), 'o': r[1], 'h': r[2], 'l': r[3], 'c': r[4], 'v': r[5], 'tbv': r[6]} for r in arr]


def _fees(q):
    maker = ld.MAKER if q['maker_pct'] == DEFAULT['maker_pct'] else q['maker_pct'] / 100
    taker = ld.TAKER if q['taker_pct'] == DEFAULT['taker_pct'] else q['taker_pct'] / 100
    return {'entry': maker, 'add': taker, 'target': maker, 'stop': taker, 'market': taker}


def simulate_one(daybars, idea, q, ctx=None):
    """One idea under setting q; None when the setting does not apply to it. ladder.simulate unchanged."""
    fees = _fees(q)
    ctx = ctx or ld.DayCtx(daybars)
    i = idea['touch_i']
    old = ld.MARGIN
    ld.MARGIN = q['stop_pct'] / 100 if q['stop_pct'] != DEFAULT['stop_pct'] else old
    try:
        if q['exit'] == 'R':
            sp = ld.stop_price(ctx, i, idea, q['scale'], q['stop'], fees)
            if sp is None:
                return None
            idea = dict(idea, T1=sp['avg_planned'] + idea['side'] * q['target_r'] * sp['R_price'])
            return ld.simulate(daybars, i, idea, q['scale'], q['stop'], 'X1', fees, ctx)
        return ld.simulate(daybars, i, idea, q['scale'], q['stop'], q['exit'], fees, ctx)
    finally:
        ld.MARGIN = old


def _day_num(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp() * 1000) // DAY


def _run_month(args):
    m_start, q = args
    blob = _load_month(m_start)
    d0, d1 = _day_num(q['start']), _day_num(q['end'])
    out = {'day': [], 'touch_t': [], 'net': [], 'gross': [], 'fees': [], 'filled': [], 'refs': [], 'all_days': set()}
    ctxs = {}
    for k, idea in enumerate(blob['ideas']):
        d = idea['day']
        if not d0 <= d <= d1:
            continue
        out['all_days'].add(d)
        if q['entry'] != 'E0' and idea[q['entry']] is not True:
            continue
        if d not in ctxs:
            db = _daybars(blob['bars'][d])
            ctxs = {d: (db, ld.DayCtx(db))}
        db, ctx = ctxs[d]
        r = simulate_one(db, idea, q, ctx)
        if r is None:
            continue
        out['day'].append(d); out['touch_t'].append(idea['touch_t'])
        out['net'].append(r['net_r']); out['gross'].append(r['gross_r']); out['fees'].append(r['fees_r'])
        out['filled'].append(r['filled_qty'] > 0)
        out['refs'].append([m_start, k])
    return out


def run(q, progress=print):
    """All ideas of the date range under setting q: per-trade fee-net, gross and fee R plus chart refs."""
    if not cache_ready():
        build_cache(progress)
    d0, d1 = _day_num(q['start']), _day_num(q['end'])
    todo = [(a, q) for a, b in _months() if a // DAY <= d1 and (b - 1) // DAY >= d0]
    with ProcessPoolExecutor(max_workers=max(1, min(len(todo), (os.cpu_count() or 2) - 1))) as ex:
        parts = list(ex.map(_run_month, todo))
    res = {k: [] for k in ('day', 'touch_t', 'net', 'gross', 'fees', 'filled', 'refs')}
    days = set()
    for p in parts:
        for k in res:
            res[k] += p[k]
        days |= p['all_days']
    out = {k: np.array(v, dtype=np.int64 if k in ('day', 'touch_t') else bool if k == 'filled' else float)
           for k, v in res.items() if k != 'refs'}
    out['refs'] = res['refs']
    out['all_days'] = np.array(sorted(days), dtype=np.int64)
    return out


def trade_bars(ref, q):
    """(daybars, idea, simulate() result) of one trade, for the charts."""
    m_start, k = ref
    blob = _load_month(m_start)
    idea = blob['ideas'][k]
    db = _daybars(blob['bars'][idea['day']])
    return db, idea, simulate_one(db, idea, q)


def chart_trade(ref, q):
    """The generic chart shape (charts.py) of one trade. Prices are simulate()'s own; exit times are located as the
    first bar after the previous event whose range holds the exit price (day end for a time exit)."""
    db, idea, r = trade_bars(ref, q)
    if r is None or r['filled_qty'] <= 0:
        return None
    lo = np.array([b['l'] for b in db]); hi = np.array([b['h'] for b in db])
    entries = [(db[bar]['t'], p) for p, _, bar in r['fills']]
    start = max((bar for _, _, bar in r['fills']), default=idea['touch_i'])
    exits = []
    for px, _, reason in r['exits']:
        if reason == 'TIME':
            j = len(db) - 1
        else:
            hit = np.flatnonzero((lo[start:] <= px) & (hi[start:] >= px))
            j = start + int(hit[0]) if hit.size else len(db) - 1
        exits.append((db[j]['t'], px, reason))
        start = j
    return {'bars': db, 'side': idea['side'], 'level': idea['L1'], 'entries': entries, 'stop': r['stop'],
            'target': r['target'], 'exits': exits, 'net_r': r['net_r']}
