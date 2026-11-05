"""Fail-first tests for the Opus E2E review findings (OPUS_E2E_REVIEW_2026-10-28.md), desk/Python side.

- F1: Hagopian target distance is |UML - ML| (RESEARCH_PITCHFORK_LAYER.md:42), OURS reading.
- F6: bounce tine is the line through P2, picked from p2_is_lower, not from the tine name.
- F10: one ZigZag step function; scan_pitchfork_signals and find_pivots_zigzag both call it.
"""
import numpy as np
import pytest

from MyTradingSys.backtest.layers.pitchfork import pitchfork_detector as pd


def walk(n=500, seed=11):
    r = np.random.default_rng(seed)
    c = 20000.0 * np.exp(np.cumsum(r.normal(0.0005, 0.018, n)))
    o = np.r_[c[0], c[:-1]]
    span = c * r.uniform(0.004, 0.015, n)
    return list(np.maximum(o, c) + span), list(np.minimum(o, c) - span), list(c)


@pytest.mark.parametrize('variant', list(pd.PitchforkVariant))
def test_f1_hagopian_target_is_one_uml_to_ml_distance(variant):
    h, l, c = walk()
    ev = [e for e in pd.scan_pitchfork_signals(h, l, c, variant=variant, setup_mode='HAGOPIAN', vp_filter='ALL')
          if e['kind'] == 'HAGOPIAN']
    assert ev
    for e in ev:
        # alternating pivots: ML passes the P1-P2 midpoint, so |UML - ML| = channel_width / 2
        assert abs(e['ml_target'] - c[e['bar_index']]) == pytest.approx(e['channel_width'] / 2.0)
        assert np.sign(e['ml_target'] - c[e['bar_index']]) == e['side']


def test_f6_inverted_fork_bounce_tine_is_the_p2_line():
    # P0 low above P1 high: the fork inverts, P2 (a swing low) sits on the upper tine
    p0 = pd.PitchforkPivot(index=0, price=200.0, is_high=False)
    p1 = pd.PitchforkPivot(index=10, price=150.0, is_high=True)
    p2 = pd.PitchforkPivot(index=20, price=140.0, is_high=False)
    pf = pd.PitchforkChannel(p0, p1, p2, variant=pd.PitchforkVariant.STANDARD)
    assert not pf.p2_is_lower
    for t in (20.0, 25.0):
        p2_line = pf.p2_val + pf.slope * (t - pf.t2)
        assert pd.bounce_tine(pf, t) == pytest.approx(p2_line)
        assert pd.bounce_tine(pf, t) == pytest.approx(pf.get_uml(t))
    # normal fork: P2 low on LML
    pf2 = pd.PitchforkChannel(pd.PitchforkPivot(0, 100.0, False), p1, p2, variant=pd.PitchforkVariant.STANDARD)
    assert pf2.p2_is_lower and pd.bounce_tine(pf2, 22.0) == pytest.approx(pf2.get_lml(22.0))


def test_f10_scan_and_finder_share_one_zigzag_step(monkeypatch):
    h, l, c = walk()
    calls = []
    real = pd.zigzag_step

    def spy(*a, **k):
        calls.append(1)
        return real(*a, **k)

    monkeypatch.setattr(pd, 'zigzag_step', spy)
    pd.scan_pitchfork_signals(h, l, c, lookback=4, min_change_pct=0.03, vp_filter='ALL')
    n_scan = len(calls)
    assert n_scan == len(c) - 8
    piv = pd.find_pivots_zigzag(h, l, lookback=4, min_change_pct=0.03)
    assert len(calls) - n_scan == len(c) - 8
    # pivot equality: stepping bar by bar gives the finder's pivots
    stepped, last = [], None
    for ci in range(8, len(c)):
        last = real(h, l, ci, 4, 0.03, stepped, last)
    assert stepped == piv and len(piv) >= 10
