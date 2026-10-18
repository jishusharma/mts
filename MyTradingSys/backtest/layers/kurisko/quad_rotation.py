"""Kurisko Quad Rotation detector. ALERT-ONLY observation module: no routing, no Tom/Fabio gate, enabled stays false.

Four oscillators (stochastic (9,3),(14,3),(40,4),(60,10), or RSI on the same lookbacks as an operator hypothesis).
Long event: all four lines < level_lo, then the fast line (first band) turns up. Short mirror (> level_hi, fast turns down)
is NO-SOURCE (KURISKO_SPEC s5 gap 6). Rule and worked numbers: backtest/layers/FORMULAS.md section 24; parameters with
labels: params/kurisko_default.json.

Causal: the row at bar t uses bars <= t only. Input bars: sequence of (open_time_ms, high, low, close). A NaN bar or a
missing bar (open_time jump != tf_ms) splits the series: windows never span it, lines restart as NaN, and any episode ends.
"""
import json
import math
import sys
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3]))   # repo root: MyTradingSys.backtest.layers.rsi.rsi_core
import stoch_core  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

NAN = float("nan")
_P = json.loads((HERE / "params" / "kurisko_default.json").read_text())["params"]
BANDS = tuple(tuple(b) for b in _P["bands"]["value"])           # (k, d) per band, fast first
RSI_BANDS = tuple(tuple(b) for b in _P["rsi_bands"]["value"])   # (period, 0) per band
LEVEL_LO, LEVEL_HI = _P["level_lo"]["value"], _P["level_hi"]["value"]

Event = namedtuple("Event", "t side episode_start")
Row = namedtuple("Row", "open_time t_close available_at side kind values episode_start_t")


def _segments(bars, tf_ms):
    """Index ranges [a, b) of consecutive valid bars; NaN bars and time gaps split."""
    segs, a, prev = [], None, None
    for i, (t, h, l, c) in enumerate(bars):
        bad = any(math.isnan(v) for v in (h, l, c))
        if bad or (prev is not None and t - prev != tf_ms):
            if a is not None:
                segs.append((a, i))
            a = None
        if not bad and a is None:
            a = i
        prev = t
    if a is not None:
        segs.append((a, len(bars)))
    return segs


def lines(bars, tf_ms, arm="stoch", bands=None):
    """Four lists (one per band, fast first), NaN where undefined."""
    if arm not in ("stoch", "rsi"):
        raise ValueError("arm must be 'stoch' or 'rsi'")
    bands = bands or (BANDS if arm == "stoch" else RSI_BANDS)
    out = [[NAN] * len(bars) for _ in bands]
    for a, b in _segments(bars, tf_ms):
        h = [x[1] for x in bars[a:b]]
        l = [x[2] for x in bars[a:b]]
        c = [x[3] for x in bars[a:b]]
        for j, (k, d) in enumerate(bands):
            if arm == "stoch":
                vals = stoch_core.stoch_line(h, l, c, k, d)
            elif len(c) > k:
                vals = [NAN if v is None else v for v in rsi_core(c, k)]
            else:
                continue
            out[j][a:b] = vals
    return out


def _scan(lns, side, lo, hi):
    """One side's state machine. Episode = consecutive bars with all four lines strictly beyond the level."""
    fast = lns[0]
    ev, s, fired = [], None, False
    for t in range(len(fast)):
        if s is not None and not fired and t > 0 and not math.isnan(fast[t]):
            turn = fast[t] > fast[t - 1] if side == "long" else fast[t] < fast[t - 1]
            if turn:
                ev.append(Event(t, side, s))
                fired = True
        vals = [x[t] for x in lns]
        if any(math.isnan(v) for v in vals):
            inside = False
        elif side == "long":
            inside = all(v < lo for v in vals)
        else:
            inside = all(v > hi for v in vals)
        if inside:
            if s is None:
                s, fired = t, False
        else:
            s, fired = None, False
    return ev


def detect(lns, lo=LEVEL_LO, hi=LEVEL_HI):
    """Events from four line series. Event at the first t > s with all four beyond the level on bars s..t-1 and the fast
    line turning (up for long, down for short) at t; one per episode. Sorted by t."""
    return sorted(_scan(lns, "long", lo, hi) + _scan(lns, "short", lo, hi), key=lambda e: (e.t, e.side))


def compute(bars, tf_ms, arm="stoch", bands=None, lo=LEVEL_LO, hi=LEVEL_HI):
    """One Row per input bar. side is None unless an event closes at that bar."""
    lns = lines(bars, tf_ms, arm, bands)
    evs = {e.t: e for e in detect(lns, lo, hi)}
    kind = "quad_rotation_" + arm
    rows = []
    for i, (t, _h, _l, _c) in enumerate(bars):
        e = evs.get(i)
        rows.append(Row(t, t + tf_ms, t + tf_ms, e.side if e else None, kind if e else None,
                        tuple(x[i] for x in lns), bars[e.episode_start][0] + tf_ms if e else None))
    return rows
