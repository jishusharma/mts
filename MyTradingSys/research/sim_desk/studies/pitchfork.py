"""Pitchfork (Andrews / Schiff / Modified Schiff): 3-pivot median-line channel bounce and Hagopian failure breakout.

Uses the repo's own layer code unchanged: backtest/layers/pitchfork/pitchfork_detector.py (PitchforkChannel,
PitchforkVariant, scan_pitchfork_signals) + backtest/vp_pivot_probe.py (build_profile, FORMULAS 18.1).
SOURCED (research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md): Andrews 3-pivot Median Line and 80% return-to-ML
rule (:28-56); Schiff 50% time+price shift (:60-66); Modified Schiff 50% price-only shift (:68-75, Dologa 2007);
Hagopian failure rule when price reverses before reaching the Median Line and breaks the origin tine (:95-103).
OURS: ZigZag pivot confirmation delay (4 bars on 4h, 3 bars on 1d) and minimum swing size (3% on 4h, 4% on 1d);
anchored profile Value Area (70%) and Point of Control (1.5%) confluence filter over the P0-P2 swing (the desk bars
carry no volume, so the profile weights each bar equally = Time-Price Opportunity / TPO profile); market entry at the
next bar's open after the setup bar closes; structural stop 1.5% beyond the tine/bar extreme; optional fixed-R target;
a trade is closed after 60 bars.
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bars  # noqa: E402
from MyTradingSys.backtest.layers.pitchfork import pitchfork_detector as pd  # noqa: E402

ID = 'pitchfork'
TITLE = 'Pitchfork (Andrews / Modified Schiff): tine bounce to the median line and Hagopian failure breakout, BTCUSDT or ETHUSDT'
MAX_HOLD = 60
STOP_OFFSET_PCT = 0.015
TF = {'4h': '4 hours (ours)', '1d': 'daily (ours)'}
TF_MIN = {'4h': 240, '1d': 1440}
VARIANT = {
    'modified_schiff': 'Modified Schiff: P0 shifted 50% in price (trader: Schiff / Dologa)',
    'schiff': 'Schiff: P0 shifted 50% in time and price (trader: Jerome Schiff)',
    'standard': 'Standard Andrews: unshifted P0 (trader: Alan Andrews)',
}
SETUP = {
    'BOUNCE': 'tine bounce to the median line (trader: Andrews 80% rule)',
    'HAGOPIAN': 'Hagopian failure breakout after stalling before ML (trader: Andrews Hagopian rule)',
    'BOTH': 'both tine bounce and Hagopian failure (trader: Andrews)',
}
FILTER = {
    'VA': 'P2 inside 70% TPO value area of P0-P2 swing (ours)',
    'POC': 'P2 within 1.5% of P0-P2 TPO point of control (ours)',
    'ALL': 'all confirmed 3-pivot swings, no profile filter (trader)',
}
EXIT = {
    'ML': 'at the median line / 1x channel width target (trader)',
    'R': 'target at a chosen multiple of risk (ours)',
}
DEFAULT = {
    'symbol': 'BTCUSDT',
    'tf': '4h',
    'variant': 'modified_schiff',
    'setup': 'BOUNCE',
    'vp_filter': 'VA',
    'exit': 'R',
    'target_r': 2.0,
    **_bars.FEE_DEFAULT,
    'start': '2022-04-01',
    'end': '2024-06-30',
}


def _code_hash():
    """Cache key part: an edit to pitchfork_detector.py or this study must not serve stale cached numbers."""
    h = hashlib.sha256()
    for f in (Path(__file__), Path(pd.__file__).resolve()):
        h.update(f.read_bytes())
    return h.hexdigest()[:10]


def params():
    return [
        _bars.SYMBOL_PARAM,
        {'name': 'tf', 'label': 'Chart', 'choices': TF},
        {'name': 'variant', 'label': 'Channel geometry', 'choices': VARIANT},
        {'name': 'setup', 'label': 'Setup rule', 'choices': SETUP},
        {'name': 'vp_filter', 'label': 'Swing profile filter', 'choices': FILTER},
        {'name': 'exit', 'label': 'Exit (stop: 1.5% beyond tine/bar extreme, ours)', 'choices': EXIT},
        {'name': 'target_r', 'label': 'Target, x risk (ours)', 'number': True, 'min': 0.5, 'max': 10, 'step': 0.1},
        *_bars.FEE_PARAMS,
        {'name': 'start', 'label': 'From', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
        {'name': 'end', 'label': 'To', 'date': True, 'min': '2022-04-01', 'max': '2024-06-30'},
    ]


def normalize(p):
    import desk
    q = dict(DEFAULT)
    q.update({k: v for k, v in (p or {}).items() if k in DEFAULT and v not in (None, '')})
    for k, table in (('tf', TF), ('variant', VARIANT), ('setup', SETUP), ('vp_filter', FILTER), ('exit', EXIT)):
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
    ex = f"target {q['target_r']:g}R" if q['exit'] == 'R' else 'ML target'
    return (f"{q['variant']} {q['setup']} {q['vp_filter']} {q['tf']} {ex} "
            f"fees {q['maker_pct']:g}/{q['taker_pct']:g}% slip {q['slip_pct']:g}% "
            f"{q['start']}..{q['end']}{_bars.coin_tag(q)}")


def describe(q):
    ex = f"a target at {q['target_r']:g} x risk" if q['exit'] == 'R' else 'the Median Line (or 1x channel width on Hagopian breakouts)'
    return (f"{_bars.SYMBOLS[_bars.symbol_of(q)].split(' (')[0]}, {TF[q['tf']].split(' (')[0]} "
            f"Pitchfork ({VARIANT[q['variant']].split(' (')[0]}), {SETUP[q['setup']].split(' (')[0]}, "
            f"filter: {FILTER[q['vp_filter']].split(' (')[0]}; "
            f"market entry at the next bar's open, stop 1.5% beyond the active tine/bar extreme, exit on {ex} or after {MAX_HOLD} bars; "
            f"fees {q['maker_pct']:g} % limit / {q['taker_pct']:g} % market, plus {q['slip_pct']:g} % slippage on market and stop fills; "
            f"{q['start']} to {q['end']} (development window only).")


def signals(variant, setup, vp_filter, tf, h, l, c):
    """Causal signal list from bar arrays (h, l, c); signal at bar_index uses bars <= bar_index only."""
    h_list = [float(x) for x in h]
    l_list = [float(x) for x in l]
    c_list = [float(x) for x in c]
    lookback = 4 if tf == '4h' else 3
    min_change = 0.03 if tf == '4h' else 0.04
    mean_px = sum(c_list[:min(50, len(c_list))]) / max(1, min(50, len(c_list)))
    bin_w = 10.0 if mean_px >= 5000.0 else (1.0 if mean_px >= 500.0 else 0.5)
    return pd.scan_pitchfork_signals(
        highs=h_list,
        lows=l_list,
        closes=c_list,
        variant=pd.PitchforkVariant(variant),
        setup_mode=setup,
        vp_filter=vp_filter,
        lookback=lookback,
        min_change_pct=min_change,
        stop_offset_pct=STOP_OFFSET_PCT,
        max_eval_bars=MAX_HOLD,
        bin_width=bin_w,
    )


def run(q, progress=print):
    a = _bars.load_1m(progress, _bars.symbol_of(q))
    progress(f"finding Pitchfork {q['variant']} {q['setup']} signals")
    tf_ms = TF_MIN[q['tf']] * _bars.MIN
    b = _bars.resample(a, TF_MIN[q['tf']])
    sigs = signals(q['variant'], q['setup'], q['vp_filter'], q['tf'], b[:, 2], b[:, 3], b[:, 4])

    def make(s):
        i = s['bar_index']
        side = int(s['side'])
        close = float(b[i, 4])
        stop = float(s['stop'])
        risk = abs(close - stop)
        if risk <= 0 or (side > 0 and stop >= close) or (side < 0 and stop <= close):
            return None
        if q['exit'] == 'R':
            target = close + side * q['target_r'] * risk
        else:
            target = float(s['ml_target'])
            if (side > 0 and target <= close) or (side < 0 and target >= close):
                return None
        t0 = int(b[i, 0]) + tf_ms
        return [side, t0, None, stop, target, t0 + tf_ms, None, t0 + MAX_HOLD * tf_ms, float(s['tine_level'])]

    progress(f'simulating {len(sigs)} signals on 1m bars')
    return _bars.collect(sigs, a, q, make)


def chart_trade(ref, q):
    a = _bars.load_1m(symbol=_bars.symbol_of(q))
    tr = _bars.replay(a, ref, q)
    if tr is None or not tr['filled']:
        return None
    return _bars.chart(a, ref, tr, ref[8])
