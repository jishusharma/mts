"""Planted bars: one close-break of a swing low that holds (class H, price keeps falling) and one wick sweep (class W1).
Also: pivots are causal (appending later bars never changes an earlier event) and the 1m loader dedupes by timestamp."""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study  # noqa: E402

N_BARS = 300


def planted(n=N_BARS):
    rows = []
    for k in range(n):
        o, h, l, c = 100.0, 100.5, 99.5, 100.0
        if k == 120:
            l = 90.0                      # swing low, level 90 (confirmed at bar 125)
        if k == 140:
            o, h, l, c = 99.5, 99.6, 89.0, 88.0   # close beyond 90 by more than 0.1 ATR: a break
        if 141 <= k <= 165:               # keeps falling, never closes back above 90: the break holds
            c = 88.0 - 0.5 * (k - 140)
            o, h, l = c + 0.5, c + 0.6, c - 0.5
        if k == 200:
            o, h, l, c = 100.0, 100.5, 74.0, 99.0  # pierces the 75 swing low of bar 165 but closes inside: wick sweep
        rows.append((k * 900.0, o, h, l, c, 10.0, 5.0))
    return pd.DataFrame(rows, columns=['t', 'o', 'h', 'l', 'c', 'v', 'tbv'])


def run(b):
    return study.events(b, '15m', -1, False, np.random.default_rng(1))


def test_planted_break_holds_and_wick_sweeps():
    ev = run(planted())
    by_t = {int(r['t'] // 900): r for r in ev}
    assert by_t[140]['cls'] == 'H'
    assert by_t[200]['cls'] == 'W1'
    assert len(ev) == 2
    assert by_t[140]['split'] == 'DEV'


def test_signs_continuation_is_in_break_direction():
    ev = {int(r['t'] // 900): r for r in run(planted())}
    h = ev[140]
    assert h['cont4'] > 0                 # low broke and kept falling: positive in the break direction
    assert h['flow_at'] == 0              # balanced taker flow in the fixture


def test_events_are_causal_when_bars_are_appended():
    a = run(planted(300))
    extra = planted(300).copy()
    tail = extra.iloc[-40:].copy()
    tail['t'] = tail['t'] + 40 * 900.0 * 8
    longer = pd.concat([extra, tail], ignore_index=True)
    b = run(longer)
    key = lambda e: [(r['t'], r['cls']) for r in e]
    assert key(b)[:len(a)] == key(a)


def test_load_filters_symbol_dedupes_and_skips_holdout(tmp_path):
    hdr = 'open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n'
    row = lambda ms: f'{ms},1,2,0.5,1.5,10,{ms + 59999},0,0,5,0,0\n'
    (tmp_path / 'BTCUSDT-1m-2025-06.csv').write_text(hdr + row(1748736000000) + row(1748736060000))
    (tmp_path / 'BTCUSDT-1m-2025-06-01.csv').write_text(hdr + row(1748736000000))   # overlapping daily file
    (tmp_path / 'ETHUSDT-1m-2025-06.csv').write_text(hdr + row(1748736120000))
    (tmp_path / 'BTCUSDT-1m-2025-07.csv').write_text(hdr + row(1751328000000))      # holdout month
    df = study.load(str(tmp_path))
    assert list(df.t) == [1748736000, 1748736060]
