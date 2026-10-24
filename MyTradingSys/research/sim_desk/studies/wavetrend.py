"""WaveTrend (LazyBear): WT1 crosses up through WT2 below the oversold band -> long; down above overbought -> short.

Uses the repo's own layer code unchanged: backtest/layers/wavetrend/wavetrend.py (formula SOURCED there: 10/21/4,
0.015, bands 53/60; warm-up 200 bars OURS).
SOURCED (MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md): long on an up-cross below the oversold band,
short on a down-cross above overbought (:13, :23, LazyBear); long-only, stop at the preceding three-bar low, target
1.5 x risk (:24, TrendCrypto2022).
OURS: the cross must happen with both lines beyond the band; entry at the next bar's open after the cross bar
closes (market); the three bars are the cross bar and the two before it; exit at the opposite cross as an option;
a trade is closed after 100 bars; the timeframe (no source names one).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest.layers.wavetrend import wavetrend as wt  # noqa: E402

ID = 'wavetrend'
TITLE = 'WaveTrend (LazyBear): cross out of the overbought / oversold band, BTCUSDT or ETHUSDT'
MAX_HOLD = 100
TF = {'1h': '1 hour (ours)', '4h': '4 hours (ours)', '15m': '15 minutes (ours)'}
TF_MIN = {'1h': 60, '4h': 240, '15m': 15}
BAND = {'53': 'beyond 53 (trader)', '60': 'beyond 60 (trader)'}
SIDES = {'BOTH': 'long and short (trader: LazyBear)', 'LONG': 'long only (trader: TrendCrypto2022)'}
EXIT = {'R': 'target at a multiple of risk (trader: 1.5 x)', 'CROSS': 'at the opposite cross (ours)'}
DEFAULT = {'symbol': 'BTCUSDT', 'tf': '1h', 'band': '53', 'sides': 'BOTH', 'exit': 'R', 'target_r': 1.5,
           **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'tf', 'label': 'Chart', 'choices': TF},
            {'name': 'band', 'label': 'Cross must happen', 'choices': BAND},
            {'name': 'sides', 'label': 'Trades', 'choices': SIDES},
            {'name': 'exit', 'label': 'Exit (stop: 3-bar low/high, trader)', 'choices': EXIT},
            {'name': 'target_r', 'label': 'Target, x risk (trader: 1.5)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    q['band'] = str(q['band'])
    for k, table in (('tf', TF), ('band', BAND), ('sides', SIDES), ('exit', EXIT)):
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
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else 'opposite cross'
    return (f"{q['tf']} band {q['band']} {q['sides']} {ex} fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% "
            f"{q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    ex = f"a target at {q['target_r']:g} x risk" if q['exit'] == 'R' else 'the opposite cross'
    who = 'long when' if q['sides'] == 'LONG' else 'long when'
    short = '' if q['sides'] == 'LONG' else f"; short on a down-cross above +{q['band']}"
    return (f"{_bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]}, {TF[q['tf']].split(' (')[0]} WaveTrend: {who} WT1 crosses up through WT2 below -{q['band']}{short}; "
            f"market entry at the next bar, stop past the last 3 bars, exit on {ex} or after {MAX_HOLD} bars; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, plus {q['slip_pct']:g} % slippage on market and stop fills; {q['start']} to {q['end']}.")


def run(q, progress=print):
    a = _bars.load_1m(progress, _bars.symbol_of(q))
    progress('computing WaveTrend')
    tf_ms = TF_MIN[q['tf']] * _bars.MIN
    b = _bars.resample(a, TF_MIN[q['tf']])
    rows = wt.compute([(int(r[0]), float(r[2]), float(r[3]), float(r[4])) for r in b.tolist()], tf_ms)
    band = float(q['band'])
    sigs = []
    for i, r in enumerate(rows):
        if i < 2 or r.event == 0:
            continue
        if r.event > 0 and r.wt1 <= -band and r.wt2 <= -band:
            sigs.append((i, 1))
        elif r.event < 0 and r.wt1 >= band and r.wt2 >= band and q['sides'] == 'BOTH':
            sigs.append((i, -1))
    ev = [r.event for r in rows]

    def make(s):
        i, side = s
        stop = float(b[i - 2:i + 1, 3].min()) if side > 0 else float(b[i - 2:i + 1, 2].max())
        close = float(b[i, 4])
        target = close + side * q['target_r'] * abs(close - stop) if q['exit'] == 'R' else None
        t_exit = None
        if q['exit'] == 'CROSS':
            for m in range(i + 1, min(i + 1 + MAX_HOLD, len(b))):
                if ev[m] == -side:
                    t_exit = int(b[m, 0]) + tf_ms
                    break
        t0 = int(b[i, 0]) + tf_ms
        return [side, t0, None, stop, target, t0 + tf_ms, t_exit, t0 + MAX_HOLD * tf_ms, close]

    progress(f'simulating {len(sigs)} crosses on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    return _bars.chart(a, ref, tr, ref[8])
