"""Tom volume profile: the concepts of BB3c8visnkI (2026-10-30) as clickable settings, so the desk shows what fails when.

Uses the repo's own profile code unchanged: backtest/vp_pivot_probe.py build_profile (FORMULAS 18.1: bin grid, POC,
70 % value area) and atr_sma (FORMULAS 12). Source check: research/tom_transfer_2026-10-11/VP_VIDEO_CONCEPT_CHECK_2026-10-31.md.
SOURCED (extracts/processed/tom/extract_BB3c8visnkI.md, ids in TOM_VERBATIM_INDEX.md):
  value area = 70 % of the period's volume [TOM-277]; the market returns to liquidity, balance 60-70 % of the time, a
  breakout runs away about 30 % [TOM-275, TOM-278, TOM-280]; from the edge of value a counter-trade back to equilibrium
  [TOM-279]; a thin area crossed and accepted = new fair price, the old range is left [TOM-273, TOM-274]; daily profiles,
  a shifted equilibrium after an excess move = trend change [TOM-281..284]; gaps need not close when value shifted [TOM-285].
OURS: the UTC day or Monday week as the profile period (he uses the cash session; BTC has none); 5-minute bars for the
signals; market entry at the next bar after the signal bar closes; the stop at a multiple of ATR14 (1h) from the signal
close; N consecutive closes outside value as "accepted"; the migration rule (yesterday's value entirely beyond the day
before's); a trade is closed when the period ends. Every number box says (trader) or (ours) on the page.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest import vp_pivot_probe as vp  # noqa: E402

ID = 'tom_vp'
TITLE = 'Tom volume profile: value area, return to value, accepted away, shifted equilibrium, BTCUSDT or ETHUSDT'
BAR = 5                      # signal bars, minutes (ours)
ANCHOR = {'prior_day': "yesterday's profile, UTC day (trader: daily profile; ours: UTC day, no cash session)",
          'prior_week': "last week's profile, Monday to Sunday UTC (trader: weekly profile)"}
SETUP = {'RETURN': 'first close outside value: trade back to the point of control (trader: market returns to liquidity)',
         'FADE': 'touch of the value edge from inside, close back in: trade to the point of control (trader: counter-trade to equilibrium)',
         'ACCEPT': 'N closes outside value: trade on away from value (trader: new fair price accepted; ours: N)'}
SHIFT = {'OFF': 'no filter (trader: not stated as a filter)',
         'WITH': 'skip trades against a value migration: yesterday\'s value entirely beyond the day before\'s (trader: shifted equilibrium; ours: the rule)'}
TARGET = {'POC': 'the point of control; for ACCEPT one value-area width (trader: back to equilibrium; ours: the width)',
          'R': 'a multiple of risk (ours)'}
DEFAULT = {'symbol': 'BTCUSDT', 'anchor': 'prior_day', 'setup': 'RETURN', 'accept_n': 6, 'shift': 'OFF', 'stop_atr': 1.0,
           'target': 'POC', 'target_r': 2.0, **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}
_ALLV = {}


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'anchor', 'label': 'Profile of', 'choices': ANCHOR},
            {'name': 'setup', 'label': 'Trade idea', 'choices': SETUP},
            {'name': 'accept_n', 'label': 'Closes outside value that count as accepted; RETURN and FADE exit there, ACCEPT enters there; 0 = never (ours)',
             'number': True, 'min': 0, 'max': 48, 'step': 1},
            {'name': 'shift', 'label': 'Value migration', 'choices': SHIFT},
            {'name': 'stop_atr', 'label': 'Stop, x ATR14 of 1h bars from the signal close (ours)', 'number': True, 'min': 0.25, 'max': 5, 'step': 0.25},
            {'name': 'target', 'label': 'Target', 'choices': TARGET},
            {'name': 'target_r', 'label': 'Target, x risk, when the target is a multiple of risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('anchor', ANCHOR), ('setup', SETUP), ('shift', SHIFT), ('target', TARGET)):
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
    q['accept_n'] = int(q['accept_n'])
    if q['setup'] == 'ACCEPT' and q['accept_n'] < 1:
        raise ValueError('ACCEPT needs at least 1 close outside value')
    if q['target'] != 'R':
        q['target_r'] = None
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    tg = f"target {q['target_r']:g}R" if q['target'] == 'R' else 'target POC'
    return (f"{q['anchor']} {q['setup']} n{q['accept_n']} shift {q['shift']} stop {q['stop_atr']:g}ATR {tg} "
            f"fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% {q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    coin = _bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]
    period = 'UTC day' if q['anchor'] == 'prior_day' else 'Monday week'
    idea = {'RETURN': 'at the first 5-minute close outside yesterday\'s value area, trade back toward its point of control',
            'FADE': 'when a 5-minute bar touches the value edge from inside and closes back inside, trade toward the point of control',
            'ACCEPT': f"after {q['accept_n']} consecutive 5-minute closes outside the value area, trade on in that direction"}[q['setup']]
    acc = ('' if q['setup'] == 'ACCEPT' else (f"; the idea is dropped (exit) after {q['accept_n']} consecutive closes outside value"
                                             if q['accept_n'] else '; no acceptance exit'))
    sh = '; trades against a value migration are skipped' if q['shift'] == 'WITH' else ''
    tg = f"a target at {q['target_r']:g} x risk" if q['target'] == 'R' else ('the point of control' if q['setup'] != 'ACCEPT' else 'one value-area width')
    return (f"{coin}, profile of the previous {period} (70 % value area): {idea}; market entry at the next bar, stop {q['stop_atr']:g} x ATR14 (1h) "
            f"from the signal close, exit at {tg}{acc}{sh}, or when the {period} ends; fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, "
            f"plus {q['slip_pct']:g} % slippage on market and stop fills; {q['start']} to {q['end']}, development window only.")


# ---- data: 1m bars with volume (the shared cache has no volume column) ----
def _month_v(m, symbol):
    f = _bars.BAR_CACHE / f'{symbol}-1mv-{m}.npy'
    if f.exists():
        a = np.load(f)
        _bars.guard_ms(a[:, 0], f'bar cache {f.name}')
        return a
    src = _bars.ROOT / f'{symbol}-1m-{m}.csv'
    if not src.exists():
        raise FileNotFoundError(src)
    with open(src, encoding='utf-8') as fh:
        skip = 0 if fh.readline()[:1].isdigit() else 1
    a = np.loadtxt(src, delimiter=',', skiprows=skip, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    a = a[np.unique(a[:, 0], return_index=True)[1]]
    _bars.BAR_CACHE.mkdir(parents=True, exist_ok=True)
    _bars.guard_ms(a[:, 0], f'bar file {src.name}')
    np.save(f, a)
    return a


def load_1m_vol(progress=None, symbol='BTCUSDT'):
    """1m bars (time, o, h, l, c, volume) from the warm-up month to the end of DEV; sealed data is refused."""
    if symbol not in _bars.SYMBOLS:
        raise ValueError(f'symbol: unknown choice {symbol!r}')
    if symbol not in _ALLV:
        parts = []
        for m in _bars._months(_bars.WARMUP_FROM, _bars.LAST_MONTH):
            if progress:
                progress(f'reading 1m bars with volume {m}')
            parts.append(_month_v(m, symbol))
        a = np.concatenate(parts)
        a = a[np.argsort(a[:, 0], kind='stable')]
        _bars.guard_ms(a[:, 0], f'bars {symbol}')
        _ALLV[symbol] = a
    _bars.guard_ms(_ALLV[symbol][:, 0], f'hot bar cache {symbol}')
    return _ALLV[symbol]


# ---- profiles per period ----
def period_index(t_ms, anchor):
    """Period number of each bar time: the UTC day index, or the Monday-week index (1970-01-01 was a Thursday)."""
    d = np.asarray(t_ms, np.int64) // _bars.DAY
    return d if anchor == 'prior_day' else (d + 3) // 7


def period_start_ms(p, anchor):
    return int(p) * _bars.DAY if anchor == 'prior_day' else (int(p) * 7 - 3) * _bars.DAY


def bin_width(close):
    m = float(np.mean(close[:min(50, len(close))])) if len(close) else 0.0
    return 10.0 if m >= 5000.0 else (1.0 if m >= 500.0 else 0.5)


def period_profiles(a, anchor, w=None):
    """{period p: profile of the bars OF period p} (FORMULAS 18.1 on 1m bars). The study trades period p+1 with it."""
    w = w or bin_width(a[:, 4])
    per = period_index(a[:, 0], anchor)
    starts = np.flatnonzero(np.r_[True, per[1:] != per[:-1]])
    ends = np.r_[starts[1:], len(a)]
    out = {}
    for s, e in zip(starts, ends):
        pr = vp.build_profile(a[s:e, 3], a[s:e, 2], a[s:e, 5], w)
        if pr is not None:
            out[int(per[s])] = pr
    return out


def atr_for(a5, a):
    """ATR14 of the 1h bars (FORMULAS 12), one value per 5m bar: the last 1h bar that closed before the 5m bar opened."""
    h1 = _bars.resample(a[:, :5], 60)
    atr = vp.atr_sma(h1[:, 2], h1[:, 3], h1[:, 4])
    idx = np.searchsorted(h1[:, 0], a5[:, 0] - 60 * _bars.MIN, side='right') - 1
    out = np.full(len(a5), np.nan)
    ok = idx >= 0
    out[ok] = atr[idx[ok]]
    return out


def migration(prof, p):
    """+1 when value of period p-1 lies entirely above value of p-2, -1 when entirely below, else 0 (ours)."""
    y, b = prof.get(p - 1), prof.get(p - 2)
    if y is None or b is None:
        return 0
    if y['val'] > b['vah']:
        return 1
    if y['vah'] < b['val']:
        return -1
    return 0


def signals(a5, prof, anchor, setup, accept_n, shift):
    """Causal: the signal at 5m bar i uses the profile of the previous period and closes up to bar i only.

    Returns dicts {i, side, level, poc, vah, val, p}: RETURN at the first close outside value in the period (side = back
    toward the POC); FADE when a bar's extreme touches the edge from an inside previous close and the close is back inside;
    ACCEPT at the accept_n-th consecutive close outside (side = away)."""
    per = period_index(a5[:, 0], anchor)
    out = []
    cur = None
    for i in range(1, len(a5)):
        p = int(per[i])
        if p != cur:
            cur, pr, mig = p, prof.get(p - 1), (migration(prof, p) if shift == 'WITH' else 0)
            run_side, run_n, left = 0, 0, {1: False, -1: False}
        if pr is None:
            continue
        c, h, l, pc = a5[i, 4], a5[i, 2], a5[i, 3], a5[i - 1, 4]
        outside = 1 if c > pr['vah'] else (-1 if c < pr['val'] else 0)
        run_side, run_n = (outside, run_n + 1) if outside and outside == run_side else (outside, 1 if outside else 0)
        side, level = 0, None
        if setup == 'RETURN' and outside and not left[outside]:
            left[outside] = True
            side, level = -outside, (pr['vah'] if outside > 0 else pr['val'])
        elif setup == 'FADE':
            if h >= pr['vah'] > c >= pr['val'] and pc < pr['vah']:        # touched the top edge, closed back inside value
                side, level = -1, pr['vah']
            elif l <= pr['val'] < c <= pr['vah'] and pc > pr['val']:
                side, level = 1, pr['val']
        elif setup == 'ACCEPT' and outside and run_n == accept_n:
            side, level = outside, (pr['vah'] if outside > 0 else pr['val'])
        if not side or (mig and side == -mig):
            continue
        out.append({'i': i, 'side': side, 'level': float(level), 'poc': pr['poc_price'], 'vah': pr['vah'], 'val': pr['val'], 'p': p})
    return out


def accept_exit(a5, i, side, vah, val, n):
    """Open time of the 5m bar after the n-th consecutive close beyond the value edge the trade works against, or None."""
    if not n:
        return None
    run = 0
    for m in range(i + 1, len(a5)):
        c = a5[m, 4]
        beyond = (c > vah) if side < 0 else (c < val)
        run = run + 1 if beyond else 0
        if run >= n:
            return int(a5[m, 0]) + BAR * _bars.MIN
    return None


def run(q, progress=print):
    a = load_1m_vol(progress, _bars.symbol_of(q))
    a5 = _bars.resample(a[:, :5], BAR)
    progress('building value areas')
    prof = period_profiles(a, q['anchor'])
    atr = atr_for(a5, a)
    sigs = signals(a5, prof, q['anchor'], q['setup'], q['accept_n'], q['shift'])
    bar_ms = BAR * _bars.MIN

    def make(s):
        i, side = s['i'], s['side']
        r = atr[i]
        if not np.isfinite(r) or r <= 0:
            return None
        close = float(a5[i, 4])
        stop = close - side * q['stop_atr'] * r
        if q['target'] == 'R':
            target = close + side * q['target_r'] * q['stop_atr'] * r
        elif q['setup'] == 'ACCEPT':
            target = close + side * (s['vah'] - s['val'])
        else:
            target = s['poc']
            if (side > 0 and target <= close) or (side < 0 and target >= close):
                return None
        t0 = int(a5[i, 0]) + bar_ms
        t_exit = accept_exit(a5, i, side, s['vah'], s['val'], q['accept_n']) if q['setup'] != 'ACCEPT' else None
        t_hold = period_start_ms(s['p'] + 1, q['anchor'])
        if t_hold <= t0:
            return None
        return [side, t0, None, float(stop), float(target), t0 + bar_ms, t_exit, t_hold, s['level']]

    progress(f'simulating {len(sigs)} ideas on 1m bars')
    return _bars.collect(sigs, a[:, :5], q, make)


def chart_trade(ref, q):
    a = load_1m_vol(symbol=_bars.symbol_of(q))[:, :5]
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    out = _bars.chart(a, ref, tr, ref[8])
    out['note'] = {'RETURN': 'Return to value: first 5m close outside the previous period value area; trade back toward the point of control',
                   'FADE': 'Edge fade: a 5m bar touched the value-area edge from inside and closed back in; trade toward the point of control',
                   'ACCEPT': 'Accepted away: N consecutive 5m closes outside value; trade on in that direction'}[q['setup']]
    return out
