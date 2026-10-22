"""RSI 40/60 (Malkan): in an up-trend RSI dips to 40 and a green candle forms there -> long; mirror at 60 -> short.

Uses the repo's own layer code unchanged: rsi_core (Wilder RSI) and malkan_40_60 (trend check + 40/60 setups).
SOURCED (MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md): RSI 14 (:35); daily chart, green candle at
40 = buy, red candle at 60 = sell (:116-120, :143-144); entry above the signal candle's high (:117); stop below its
low / above its high (:123, :147, :248-249); target RSI 60 for a long, 40 for a short (:128, :152).
OURS: band around 40/60 (2 points) and trend-check length (20 bars) = the layer module's defaults; the entry order
lives for one bar; a trade is closed after 100 bars (run_rsi_backtest.py MAX_BARS); other timeframes; a fixed-R target.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime, malkan_setup_bear, malkan_setup_bull  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

ID = 'rsi'
TITLE = 'RSI 40/60 (Malkan): bounce at 40 in an up-trend, reject at 60 in a down-trend, BTCUSDT or ETHUSDT'
PERIOD, MAX_HOLD = 14, 100
TF = {'1d': 'daily (trader)', '4h': '4 hours (ours)', '1h': '1 hour (ours)'}
TF_MIN = {'1d': 1440, '4h': 240, '1h': 60}
ENTRY = {'BREAK': 'order above the signal candle high / below its low (trader)', 'CLOSE': 'at the signal candle close (ours)'}
EXIT = {'LEVEL': 'when RSI reaches 60 (long) / 40 (short) (trader)', 'R': 'target at a chosen multiple of risk (ours)'}
DEFAULT = {'symbol': 'BTCUSDT', 'tf': '1d', 'entry': 'BREAK', 'exit': 'LEVEL', 'target_r': 2.0, 'tolerance': 2.0, 'lookback': 20,
           **_bars.FEE_DEFAULT, 'start': '2022-04-01', 'end': '2024-06-30'}


def params():
    return [_bars.SYMBOL_PARAM,
            {'name': 'tf', 'label': 'Chart', 'choices': TF},
            {'name': 'entry', 'label': 'Entry', 'choices': ENTRY},
            {'name': 'exit', 'label': 'Exit (stop: past the signal candle, trader)', 'choices': EXIT},
            {'name': 'target_r', 'label': 'Target, x risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
            {'name': 'tolerance', 'label': 'How close to 40/60 counts, RSI points (ours)', 'number': True, 'min': 0.5, 'max': 5, 'step': 0.5},
            {'name': 'lookback', 'label': 'Trend check, bars (ours)', 'number': True, 'min': 5, 'max': 60, 'step': 1},
            *_bars.FEE_PARAMS,
            {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
            {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'}]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('tf', TF), ('entry', ENTRY), ('exit', EXIT)):
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
    q['lookback'] = int(q['lookback'])
    if q['exit'] != 'R':
        q['target_r'] = None
    q['start'], q['end'] = desk.check_dates(str(q['start']), str(q['end']))
    return q


def label(q):
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else 'RSI 60/40'
    return (f"{q['tf']} {q['entry']} {ex} band {q['tolerance']:g} trend {q['lookback']} "
            f"fees {q['maker_pct']:g}/{q['taker_pct']:g}% {q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    ex = f"a target at {q['target_r']:g} x risk" if q['exit'] == 'R' else 'RSI reaching 60 (long) or 40 (short)'
    return (f"{_bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]}, {TF[q['tf']].split(' (')[0]} RSI {PERIOD}: long when RSI dips to within {q['tolerance']:g} of 40 "
            f"and turns up on a green candle in an up-trend (short: mirror at 60); "
            f"{ENTRY[q['entry']].split(' (')[0]}, stop past the signal candle, exit on {ex} or after {MAX_HOLD} bars; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market; {q['start']} to {q['end']}.")


def _signals(q, a):
    tf = TF_MIN[q['tf']]
    b = _bars.resample(a, tf)
    bars = [{'t': int(r[0]), 'o': r[1], 'h': r[2], 'l': r[3], 'c': r[4]} for r in b]
    rsi = rsi_core([x['c'] for x in bars], PERIOD)
    regime = malkan_regime(rsi, lookback=q['lookback'])
    sigs = malkan_setup_bull(bars, rsi, regime, tolerance=q['tolerance']) + \
        malkan_setup_bear(bars, rsi, regime, tolerance=q['tolerance'])
    return b, rsi, sorted(sigs, key=lambda s: s['t'])


def run(q, progress=print):
    a = _bars.load_1m(progress, _bars.symbol_of(q))
    progress('finding RSI setups')
    b, rsi, sigs = _signals(q, a)
    tf_ms = TF_MIN[q['tf']] * _bars.MIN
    index = {int(t): i for i, t in enumerate(b[:, 0])}

    def make(s):
        k = index[s['t']]
        side = 1 if s['side'] == 'long' else -1
        hi, lo, close = float(b[k, 2]), float(b[k, 3]), float(b[k, 4])
        stop = lo if side > 0 else hi
        trig = (hi if side > 0 else lo) if q['entry'] == 'BREAK' else None
        ref_px = trig if trig is not None else close
        target = ref_px + side * q['target_r'] * abs(ref_px - stop) if q['exit'] == 'R' else None
        t_exit = None
        if q['exit'] == 'LEVEL':
            for m in range(k + 1, min(k + 1 + MAX_HOLD, len(b))):
                if rsi[m] is not None and (rsi[m] >= 60 if side > 0 else rsi[m] <= 40):
                    t_exit = int(b[m, 0]) + tf_ms
                    break
        t0 = int(b[k, 0]) + tf_ms
        return [side, t0, trig, stop, target, t0 + tf_ms, t_exit, t0 + MAX_HOLD * tf_ms, ref_px]

    progress(f'simulating {len(sigs)} setups on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    return _bars.chart(a, ref, tr, ref[8])
