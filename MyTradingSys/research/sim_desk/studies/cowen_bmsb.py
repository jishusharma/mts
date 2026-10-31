"""Cowen bull market support band: the chart concepts of bekghgecip8 (2026-10-30) as clickable settings, so the desk shows what fails when.

Source check: research/cowen_q4_2026-10-31/COWEN_Q4_CONCEPT_CHECK.md; quotes in extracts/processed/cowen/extract_bekghgecip8.md.
SOURCED (the extract, section ids W1..W10): the band is the 20-week SMA and the 21-week EMA [W2, W6]; a bounce off the band,
then the final drop [W6]; if Bitcoin gives the band up at once and finds no support, the drop is over early [W7]; everything
else at the band while Bitcoin is not = Bitcoin tends to drop [W2]; a close below the 50-day starts the case for a fake-out and
a move to at least the band (earlier video, COWEN_LEVELS_2026-10-31.md bWdXPK3Hlok 00:05:47).
NOT TESTABLE here, and said so on the page: the three midterm lows, the rate-hike lag, the IPO analog, the day-389 clock and the
equity roll-over are one to three events each (2014, 2018, 2022); the desk window holds none of the 2014 or 2018 events.
OURS: the band is read from COMPLETED Monday-to-Sunday weeks only (a trader sees the unfinished week; using it would leak the
future into the signal); daily bars (UTC) for the signals; market entry at the open of the next day; the stop at a multiple of
the 14-day ATR from the signal close; the exit after N daily closes back through the idea's level (band bottom, the 50-day, or the signal close); the 3 % gap and ETH or BTC as the "everything
else" for the catch-down idea (he names Total 2, Total 3, MicroStrategy, S&P, Nasdaq; the desk has only the other coin); the hold limit.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest import vp_pivot_probe as vp  # noqa: E402

ID = 'cowen_bmsb'
TITLE = 'Cowen bull market support band: bounce, band lost, 50-day fake-out, others-at-the-band catch-down, BTCUSDT or ETHUSDT'
SETUP = {'BOUNCE': 'long when a day dips to the band from above and closes above its bottom (trader: bounce off the band)',
         'LOSE': 'short at the first daily close below the band (trader: gives the band up, no support; ours: the entry)',
         'FAKEOUT': 'short at the first daily close below the 50-day average while above the band, aiming at the band (trader: fake-out, at least to the band)',
         'CATCHDOWN': 'short when the other coin sits at its band and this coin is a gap above its own band (trader: everything else at the band, Bitcoin not; ours: the other coin and the gap)'}
TARGET = {'R': 'a multiple of risk (ours)',
          'BAND': 'the top of the band, shorts only: FAKEOUT and CATCHDOWN (trader: heading to the band)'}
DEFAULT = {'symbol': 'BTCUSDT', 'setup': 'BOUNCE', 'gap_pct': 3.0, 'exit_n': 2, 'stop_atr': 2.0, 'target': 'R', 'target_r': 2.0,
           'hold_days': 30, **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}
SMA_W, EMA_W = 20, 21


def _code_hash():
    """Cache key part: an edit to this study must not serve results cached under the old rules."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:10]


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'setup', 'label': 'Trade idea', 'choices': SETUP},
            {'name': 'gap_pct', 'label': 'CATCHDOWN only: how far above its own band this coin must close, % (ours)', 'number': True, 'min': 0.0, 'max': 30, 'step': 0.5},
            {'name': 'exit_n', 'label': 'Daily closes back through the level of the idea against the trade that end it (level: band bottom for BOUNCE and LOSE, the 50-day for FAKEOUT, the signal close for CATCHDOWN); 0 = never (ours)', 'number': True, 'min': 0, 'max': 20, 'step': 1},
            {'name': 'stop_atr', 'label': 'Stop, x ATR14 of daily bars from the signal close (ours)', 'number': True, 'min': 0.25, 'max': 8, 'step': 0.25},
            {'name': 'target', 'label': 'Target', 'choices': TARGET},
            {'name': 'target_r', 'label': 'Target, x risk, when the target is a multiple of risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            {'name': 'hold_days', 'label': 'Longest hold, days (ours)', 'number': True, 'min': 1, 'max': 120, 'step': 1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('setup', SETUP), ('target', TARGET)):
        if q[k] not in table:
            raise ValueError(f'{k}: unknown choice {q[k]!r}')
    _bars.symbol_of(q)
    for f in params():
        if f.get('number') and not (f['name'] == 'target_r' and q['target'] != 'R'):
            try:
                v = float(q[f['name']])
            except (TypeError, ValueError):
                raise ValueError(f"{f['label']}: please type a number")
            if not (f['min'] <= v <= f['max']):
                raise ValueError(f"{f['label']}: {v:g} is outside {f['min']}..{f['max']}")
            q[f['name']] = round(v, 6)
    q['exit_n'], q['hold_days'] = int(q['exit_n']), int(q['hold_days'])
    if q['target'] == 'BAND' and q['setup'] not in ('FAKEOUT', 'CATCHDOWN'):
        raise ValueError('target BAND is for the short ideas FAKEOUT and CATCHDOWN only')
    if q['target'] != 'R':
        q['target_r'] = None
    if q['setup'] != 'CATCHDOWN':
        q['gap_pct'] = 0.0
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    tg = f"target {q['target_r']:g}R" if q['target'] == 'R' else 'target BAND'
    gap = f" gap {q['gap_pct']:g}%" if q['setup'] == 'CATCHDOWN' else ''
    return (f"{q['setup']}{gap} exit{q['exit_n']} stop {q['stop_atr']:g}ATR {tg} hold {q['hold_days']}d "
            f"fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% {q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    coin = _bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]
    other = 'ETH' if _bars.symbol_of(q) == 'BTCUSDT' else 'BTC'
    idea = {'BOUNCE': 'when a daily bar dips to the top of the band from above and closes above its bottom, go long',
            'LOSE': 'at the first daily close below the band, go short',
            'FAKEOUT': 'at the first daily close below the 50-day average while still above the band, go short',
            'CATCHDOWN': f"when {other} trades at its own band and {coin} closes {q['gap_pct']:g} % above its band, go short"}[q['setup']]
    lvl = {'BOUNCE': 'below the band bottom', 'LOSE': 'above the band bottom', 'FAKEOUT': 'above the 50-day average', 'CATCHDOWN': 'above the signal close'}[q['setup']]
    ex = f"; the idea is dropped after {q['exit_n']} daily closes {lvl}" if q['exit_n'] else '; no level exit'
    tg = f"a target at {q['target_r']:g} x risk" if q['target'] == 'R' else 'the top of the band'
    return (f"{coin}, band = 20-week SMA and 21-week EMA of completed weeks: {idea}; market entry at the next day's open, stop {q['stop_atr']:g} x ATR14 "
            f"(daily) from the signal close, exit at {tg}{ex}, or after {q['hold_days']} days; fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, "
            f"plus {q['slip_pct']:g} % slippage on market and stop fills; {q['start']} to {q['end']}, development window only. "
            f"The band needs 21 completed weeks, so the first signals come in June 2022.")


# ---- the band: weekly closes only, completed weeks only ----
def week_index(t_ms):
    """Monday-week number of each time (1970-01-01 was a Thursday)."""
    return (np.asarray(t_ms, np.int64) // _bars.DAY + 3) // 7


def band(t_ms, close):
    """(top, bottom) per daily bar: max and min of the 20-week SMA and the 21-week EMA of the weekly closes of the weeks
    that ended BEFORE this bar's week. NaN until 21 weeks exist. EMA: seed = SMA of the first 21 closes, then alpha 2/22."""
    wk = week_index(t_ms)
    last = np.flatnonzero(np.r_[wk[1:] != wk[:-1], True])         # last daily bar of every week
    wc, wid = np.asarray(close, float)[last], wk[last]
    n = len(wc)
    sma = np.full(n, np.nan)
    ema = np.full(n, np.nan)
    for k in range(SMA_W - 1, n):
        sma[k] = wc[k - SMA_W + 1:k + 1].mean()
    if n >= EMA_W:
        ema[EMA_W - 1] = wc[:EMA_W].mean()
        for k in range(EMA_W, n):
            ema[k] = ema[k - 1] + (wc[k] - ema[k - 1]) * 2.0 / (EMA_W + 1)
    hi, lo = np.fmax(sma, ema), np.fmin(sma, ema)
    both = np.isfinite(sma) & np.isfinite(ema)
    hi, lo = np.where(both, hi, np.nan), np.where(both, lo, np.nan)
    pos = np.searchsorted(wid, wk, side='left') - 1                 # the week before this bar's week
    top, bottom = np.full(len(wk), np.nan), np.full(len(wk), np.nan)
    ok = pos >= 0
    top[ok], bottom[ok] = hi[pos[ok]], lo[pos[ok]]
    return top, bottom


def features(a1m):
    """Daily bars (t, o, h, l, c) with band top and bottom, the 50-day SMA and ATR14, from 1m bars."""
    d = _bars.resample(a1m[:, :5], 1440)
    top, bottom = band(d[:, 0], d[:, 4])
    c = d[:, 4]
    sma50 = np.full(len(d), np.nan)
    if len(d) >= 50:
        cs = np.cumsum(np.r_[0.0, c])
        sma50[49:] = (cs[50:] - cs[:-50]) / 50.0
    atr = vp.atr_sma(d[:, 2], d[:, 3], c)
    return {'d': d, 'top': top, 'bottom': bottom, 'sma50': sma50, 'atr': np.asarray(atr, float)}


def align(main, other):
    """The other coin's daily low and band top on the main coin's days; NaN where it has no bar."""
    idx = np.searchsorted(other['d'][:, 0], main['d'][:, 0])
    idx = np.minimum(idx, len(other['d']) - 1)
    ok = other['d'][idx, 0] == main['d'][:, 0]
    low = np.where(ok, other['d'][idx, 3], np.nan)
    top = np.where(ok, other['top'][idx], np.nan)
    return low, top


def signals(f, setup, gap_pct=3.0, other=None):
    """Causal: the signal on daily bar i uses the band of the weeks completed before it and bars up to i only.
    Returns dicts {i, side, level, top, bottom}."""
    d, top, bot, sma = f['d'], f['top'], f['bottom'], f['sma50']
    o_low, o_top = align(f, other) if (setup == 'CATCHDOWN' and other is not None) else (None, None)
    out = []
    for i in range(1, len(d)):
        if not (np.isfinite(top[i]) and np.isfinite(bot[i])):
            continue
        c, lo, pc = d[i, 4], d[i, 3], d[i - 1, 4]
        side, level = 0, None
        if setup == 'BOUNCE' and pc > top[i] and lo <= top[i] and c >= bot[i]:
            side, level = 1, top[i]
        elif setup == 'LOSE' and pc >= bot[i] and c < bot[i]:
            side, level = -1, bot[i]
        elif setup == 'FAKEOUT' and np.isfinite(sma[i]) and np.isfinite(sma[i - 1]) and pc >= sma[i - 1] and c < sma[i] and c > top[i]:
            side, level = -1, sma[i]
        elif setup == 'CATCHDOWN' and o_low is not None:
            def cond(k):
                return bool(np.isfinite(o_low[k]) and np.isfinite(o_top[k]) and np.isfinite(top[k])
                            and o_low[k] <= o_top[k] and d[k, 4] > top[k] * (1 + gap_pct / 100.0))
            if cond(i) and not cond(i - 1):
                side, level = -1, top[i]
        if side:
            out.append({'i': i, 'side': side, 'level': float(level), 'top': float(top[i]), 'bottom': float(bot[i])})
    return out


def exit_after(f, i, side, n, level):
    """Open time of the day after the n-th consecutive daily close on the wrong side of `level` (an array per day or one number):
    below it for a long, above it for a short; None when n is 0 or it never happens. run_trade closes the trade at the
    close of the day before that time."""
    if not n:
        return None
    d, run = f['d'], 0
    lv = np.broadcast_to(np.asarray(level, float), (len(d),))
    for m in range(i + 1, len(d)):
        beyond = (d[m, 4] < lv[m]) if side > 0 else (d[m, 4] > lv[m])
        run = run + 1 if beyond else 0
        if run >= n:
            return int(d[m, 0]) + _bars.DAY
    return None


def run(q, progress=print):
    sym = _bars.symbol_of(q)
    progress('reading 1m bars')
    f = features(_bars.load_1m(progress, sym))
    other = None
    if q['setup'] == 'CATCHDOWN':
        other = features(_bars.load_1m(progress, 'ETHUSDT' if sym == 'BTCUSDT' else 'BTCUSDT'))
    sigs = signals(f, q['setup'], q['gap_pct'], other)
    d = f['d']
    a = _bars.load_1m(None, sym)[:, :5]

    def make(s):
        i, side = s['i'], s['side']
        r = f['atr'][i]
        if not np.isfinite(r) or r <= 0:
            return None
        close = float(d[i, 4])
        stop = close - side * q['stop_atr'] * r
        if q['target'] == 'R':
            target = close + side * q['target_r'] * q['stop_atr'] * r
        else:
            target = s['top']
            if target >= close:
                return None
        t0 = int(d[i, 0]) + _bars.DAY
        lvl = {'BOUNCE': f['bottom'], 'LOSE': f['bottom'], 'FAKEOUT': f['sma50'], 'CATCHDOWN': close}[q['setup']]
        return [side, t0, None, float(stop), float(target), t0 + _bars.DAY, exit_after(f, i, side, q['exit_n'], lvl),
                t0 + q['hold_days'] * _bars.DAY, s['level']]

    progress(f'simulating {len(sigs)} ideas on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))[:, :5]
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    return _bars.chart(a, ref, tr, ref[8])
