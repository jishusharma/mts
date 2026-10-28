"""Fail-first tests for crosscheck_desk.py (CROSSCHECK_BRIEF.md, "Tests"). Hand-made inputs only; no market data, no e2_run numbers."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import counts_only as co  # noqa: E402
import crosscheck_desk as cc  # noqa: E402

H4 = 4 * 3600 * 1000


def _t(entry_t, net_r, kind, side=1):
    return dict(entry_t=entry_t, side=side, net_r=net_r, kind=kind)


def test_diff_flags_planted_trade_and_passes_identical_list():
    """(1) one trade with net R off by 0.2 R and a different exit kind is flagged; an identical list is not."""
    same = [_t(1 * H4, 1.5, 'target'), _t(9 * H4, -1.0, 'stop', -1)]
    clean = cc.diff_trades(same, [dict(t) for t in same])
    assert clean['matched'] == 2 and clean['flagged'] == [] and clean['max_abs'] == 0.0 and clean['only_e2'] == [] and clean['only_desk'] == []
    assert clean['kind_agree'] == 2
    desk = [_t(1 * H4, 1.5, 'target'), _t(9 * H4, -0.8, 'time', -1)]      # second trade: +0.2 R and stop -> time
    d = cc.diff_trades(same, desk)
    assert d['matched'] == 2 and len(d['flagged']) == 1
    fl = d['flagged'][0]
    assert fl['entry_t'] == 9 * H4 and fl['side'] == -1
    assert fl['diff'] == pytest.approx(0.2) and fl['kind_e2'] == 'stop' and fl['kind_desk'] == 'time'
    assert d['kind_agree'] == 1 and d['max_abs'] == pytest.approx(0.2) and d['mean_abs'] == pytest.approx(0.1)
    # a gap of exactly the tolerance is not flagged; unmatched trades are listed on the side they belong to
    e = cc.diff_trades([_t(H4, 1.0, 'target'), _t(5 * H4, 1.0, 'target')], [_t(H4, 1.05, 'target'), _t(7 * H4, 1.0, 'target')])
    assert e['flagged'] == [] and e['only_e2'][0]['entry_t'] == 5 * H4 and e['only_desk'][0]['entry_t'] == 7 * H4


def _bars(closes):
    return [(i * H4, c, c + 1, c - 1, c) for i, c in enumerate(closes)]


def _toy_detect(bars):
    """Toy detector: signal at bar i when close[i] > close[i-1] + 5 (long). Stands in for the S8 detector."""
    return [(i, 1) for i in range(1, len(bars)) if bars[i][4] > bars[i - 1][4] + 5]


def test_signal_set_comparison_reports_the_extra_bar():
    """(2) two hand-made bar series, the second with one extra jump: the extra signal bar is reported, the common ones counted."""
    a = _bars([100, 101, 110, 111, 112, 113, 114, 115])
    b = _bars([100, 101, 110, 111, 112, 113, 125, 126])      # extra jump at bar 6
    r = cc.compare_signal_sets(a, b, _toy_detect, lo_ms=0, hi_ms=10 ** 15)
    assert r['n_e2'] == 1 and r['n_desk'] == 2 and r['common'] == 1
    assert r['only_e2'] == [] and r['only_desk'] == [6 * H4]
    same = cc.compare_signal_sets(a, a, _toy_detect, lo_ms=0, hi_ms=10 ** 15)
    assert same['only_e2'] == same['only_desk'] == [] and same['common'] == 1
    # the window is by signal-bar open time: a signal before lo is not counted
    w = cc.compare_signal_sets(a, b, _toy_detect, lo_ms=3 * H4, hi_ms=10 ** 15)
    assert w['n_e2'] == 0 and w['n_desk'] == 1 and w['only_desk'] == [6 * H4]


def test_both_loaders_refuse_bars_at_or_after_2024_07_01(monkeypatch):
    """(3) the E2 loader and the desk loader each raise on a bar at/after the sealed cut (and accept the last allowed bar)."""
    cut = co.CUT_MS
    assert cc.CUT_MS == cut
    bad4 = [(cut - H4, 1, 2, 0.5, 1.5), (cut, 1.5, 2, 1, 1.8)]
    ok4 = bad4[:1]
    monkeypatch.setattr(cc.e2, 'load_bars', lambda sym: bad4)
    with pytest.raises(ValueError):
        cc.load_e2_bars('BTCUSDT')
    monkeypatch.setattr(cc.e2, 'load_bars', lambda sym: ok4)
    assert cc.load_e2_bars('BTCUSDT') == ok4
    bad1 = np.array([[cut - 60000, 1, 2, 0.5, 1.5], [cut, 1.5, 2, 1, 1.8]])
    monkeypatch.setattr(cc._bars, 'load_1m', lambda progress=None, symbol='BTCUSDT': bad1)
    with pytest.raises(ValueError):
        cc.load_desk_1m()
    monkeypatch.setattr(cc._bars, 'load_1m', lambda progress=None, symbol='BTCUSDT': bad1[:1])
    assert len(cc.load_desk_1m()) == 1
    with pytest.raises(ValueError):
        cc.load_e2_bars('ETHUSDT')                     # BTCUSDT only
