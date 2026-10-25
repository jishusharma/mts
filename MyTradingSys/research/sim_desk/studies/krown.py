"""Krown detectors S5 / S8 / S4 on the desk. EXPLORATORY desk try, NOT the pre-registered study krown-dev-event-study,
NO-RECALL-CLEARANCE; it does not claim the pre-reg window (2017+) and reads only the desk's DEV window.

Uses the repo's own layer code unchanged: backtest/layers/krown/krown_core.py + krown_events.py (setup_s5, setup_s8)
and params/krown_params.json. The desk bars carry no volume, so only price-bar detectors are offered.
SOURCED (research/krown_ta101_2026-10-13/KROWN_RULES.csv): S5 = 21 EMA crosses 55 EMA with price on the 200 SMA side
(KR-M02, krown_params ma_fast/ma_slow/ma_long); S8 = BBWP basis 7 / lookback 100 (KR-Q01), low <= 30 (KR-Q02 gives
25-35), first bar above the 50th percentile (KR-Q02), stop on the opposite side of the compression zone (KR-Q05).
OURS: every entry, stop distance and exit (no source gives one: KR-X01, KR-Z14): market entry at the open of the bar after
the signal bar; stop = the far side of the last 10 bars including the signal bar; target 2 x risk; a trade is closed after
100 bars; the timeframe (4h or daily); S8 recent/break windows and S4 (coil break, range 20, coil < 0.7), all OURS in krown_params.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'backtest' / 'layers' / 'krown'))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402

ID = 'krown'
TITLE = 'Krown (exploratory desk try, not the pre-registered study): S5 MA cross, S8 squeeze break, S4 coil break, BTCUSDT or ETHUSDT'
MAX_HOLD, STOP_BARS = 100, 10
TF = {'4h': '4 hours (ours)', '1d': 'daily (ours)'}
TF_MIN = {'4h': 240, '1d': 1440}
SETUP = {'S5': 'S5: 21/55 EMA cross on the 200 side (trader: KR-M02)', 'S8': 'S8: squeeze then break (trader: KR-Q05)',
         'S4': 'S4: coil then range break (ours)'}
EXIT = {'R': 'target at a multiple of risk (ours)', 'HOLD': 'no target, close after 100 bars (ours)'}
DEFAULT = {'symbol': 'BTCUSDT', 'setup': 'S5', 'tf': '4h', 'exit': 'R', 'target_r': 2.0,
           **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}
SKIPPED = ('S1 zone test, S2 zone break and S7 capitulation need volume (the desk bars have none; the trader quotes CME volume); '
           'S9 tops need volume; S3 range edge needs candle-pattern wicks (all OURS); S6 leash fires at the reconnect bar, after the '
           'move, and names no entry direction (provisional, one video)')


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'setup', 'label': 'Detector', 'choices': SETUP},
            {'name': 'tf', 'label': 'Chart', 'choices': TF},
            {'name': 'exit', 'label': 'Exit (stop: far side of last 10 bars, ours)', 'choices': EXIT},
            {'name': 'target_r', 'label': 'Target, x risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('setup', SETUP), ('tf', TF), ('exit', EXIT)):
        if q[k] not in table:
            raise ValueError(f'{k}: unknown choice {q[k]!r}')
    _bars.symbol_of(q)
    for f in params():
        if f.get('number') and not (f['name'] == 'target_r' and q['exit'] != 'R'):
            try:
                v = float(q[f['name']])
            except (TypeError, ValueError):
                raise ValueError(f"{f['label']}: please type a number")
            if not (f['min'] <= v <= f['max']):
                raise ValueError(f"{f['label']}: {v:g} is outside {f['min']}..{f['max']}")
            q[f['name']] = round(v, 6)
    if q['exit'] != 'R':
        q['target_r'] = None
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else 'hold'
    return (f"{q['setup']} {q['tf']} {ex} fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% "
            f"{q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    ex = f"a target at {q['target_r']:g} x risk" if q['exit'] == 'R' else 'no target'
    return (f"EXPLORATORY desk try, not the pre-registered study krown-dev-event-study, NO-RECALL-CLEARANCE. "
            f"{_bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]}, {TF[q['tf']].split(' (')[0]} Krown {SETUP[q['setup']].split(' (')[0]}: "
            f"market entry at the next bar's open, stop past the last {STOP_BARS} bars, {ex}, closed after {MAX_HOLD} bars; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, plus {q['slip_pct']:g} % slippage on market and stop fills; "
            f"{q['start']} to {q['end']} (development window only). Skipped detectors: {SKIPPED}.")


def signals(setup, o, h, l, c):
    """[(bar index, side +1/-1)] for one detector; the signal at bar i uses bars <= i only."""
    o, h, l, c = ([float(x) for x in s] for s in (o, h, l, c))
    p = kc.load_params()
    if setup == 'S5':
        ev = ke.setup_s5(kc.crosses(kc.ema(c, p['ma_fast']), kc.ema(c, p['ma_slow'])), c, kc.sma(c, p['ma_long']))
    elif setup == 'S8':
        ev = ke.setup_s8(kc.bbwp(c, p['bbwp_basis'], p['bbwp_lookback'], p['bbwp_mult']), h, l, c, p)
    elif setup == 'S4':
        ev = []
        for t in range(1, len(c)):                       # same rule as krown_events.build_events S4
            rs = kc.range_state(h, l, c, t, p)
            if rs and rs['breakout']:
                cs = kc.coil_score(h, l, t - 1, p['coil_recent'], p['range_n'])
                if cs is not None and cs < p['coil_max']:
                    ev.append({'i': t, 'side': 'long' if rs['breakout'] == 'up' else 'short'})
    else:
        raise ValueError(f'setup: unknown choice {setup!r}')
    return sorted((e['i'], 1 if e['side'] == 'long' else -1) for e in ev)


def run(q, progress=print):
    a = _bars.load_1m(progress, _bars.symbol_of(q))
    progress(f"finding Krown {q['setup']} signals")
    tf_ms = TF_MIN[q['tf']] * _bars.MIN
    b = _bars.resample(a, TF_MIN[q['tf']])
    sigs = signals(q['setup'], b[:, 1], b[:, 2], b[:, 3], b[:, 4])

    def make(s):
        i, side = s
        if i < STOP_BARS:
            return None
        stop = float(b[i - STOP_BARS + 1:i + 1, 3].min()) if side > 0 else float(b[i - STOP_BARS + 1:i + 1, 2].max())
        close = float(b[i, 4])
        target = close + side * q['target_r'] * abs(close - stop) if q['exit'] == 'R' else None
        t0 = int(b[i, 0]) + tf_ms                       # the signal bar has closed: trade from the next bar's open
        return [side, t0, None, stop, target, t0 + tf_ms, None, t0 + MAX_HOLD * tf_ms, close]

    progress(f'simulating {len(sigs)} signals on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    return _bars.chart(a, ref, tr, ref[8])
