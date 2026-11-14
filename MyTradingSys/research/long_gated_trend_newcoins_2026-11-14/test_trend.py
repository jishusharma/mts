"""Tests for edge8. Each guard test is also run against a deliberately wrong implementation (mutant) and must FAIL there."""
import os, sys, datetime as dt
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S
import trend_lib as T


def synth(n=420, seed=3):
    """4 coins with a persistent uptrend + noise, plus BTC trending up (gate open after day 200). Daily bars from 2020-01-01."""
    r = np.random.default_rng(seed)
    dates = np.array([dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(days=i) for i in range(n)])
    C = np.array([100 * np.cumprod(1 + 0.004 + 0.02 * r.standard_normal(n)) for _ in range(4)])
    H, L = C * 1.01, C * 0.99
    btc = 100 * np.cumprod(1 + 0.004 + 0.005 * r.standard_normal(n))
    return H, L, C, dates, btc


def check_cap(cap_fn):
    E = np.array([[0.4, 0.1, 0.0], [0.4, 0.2, 0.0], [0.4, 0.3, 0.0]])       # day sums 1.2, 0.6, 0.0
    out = cap_fn(E)
    assert np.all(out.sum(0) <= 1.0 + 1e-12)
    assert np.allclose(out[:, 0], np.array([0.4, 0.4, 0.4]) / 1.2)     # pro rata, same ratio kept
    assert np.allclose(out[:, 1], E[:, 1])                                                                      # under the cap: untouched


def test_cap_pro_rata():
    check_cap(S.cap)


def test_cap_mutant_fails():
    with pytest.raises(AssertionError):
        check_cap(lambda E: E)                      # "cap not applied" must be caught


def test_book_never_exceeds_one_and_is_long_only():
    H, L, C, dates, btc = synth()
    W, m200 = S.build_W(H, L, C, dates, btc)
    for name, w in W.items():
        assert (w >= 0).all()
        assert (S.build_E(w).sum(0) <= 1.0 + 1e-12).all()
    # parent sizing alone does exceed 1.0 on this input, so the cap is actually doing work
    assert max(w.sum(0).max() for w in W.values()) > 1.0


def test_book_mutant_uncapped_fails():
    H, L, C, dates, btc = synth()
    W, _ = S.build_W(H, L, C, dates, btc)
    E = S.build_E(W["9 GATED-TSM30"], cap_fn=lambda E: E)
    with pytest.raises(AssertionError):
        assert (E.sum(0) <= 1.0 + 1e-12).all()


def prefix_invariant(shift_fn):
    """Position in force on day d (built from the first d+1 bars only, evaluated at d) equals the one from the full series: no look-ahead."""
    H, L, C, dates, btc = synth()
    full, _ = S.build_W(H, L, C, dates, btc)
    E_full = {k: S.build_E(v, shift_fn=shift_fn) for k, v in full.items()}
    for k_end in (260, 300, 350):
        Wp, _ = S.build_W(H[:, :k_end], L[:, :k_end], C[:, :k_end], dates[:k_end], btc[:k_end])
        for name in Wp:
            Ep = S.build_E(Wp[name], shift_fn=shift_fn)
            assert np.allclose(Ep[:, :k_end], E_full[name][:, :k_end]), (name, k_end)


def test_no_lookahead_prefix_invariance():
    prefix_invariant(S.eff)


def test_one_bar_lookahead_mutant_fails():
    def peek(W):                                    # position taken ON the signal bar's own return, and one bar ahead of the signal: shift -1
        E = np.zeros_like(W); E[:, :-1] = W[:, 1:]; return E
    with pytest.raises(AssertionError):
        prefix_invariant(peek)


def test_eff_is_one_day_shift():
    W = np.array([[0, 0.3, 0.3, 0.0]])
    assert list(S.eff(W)[0]) == [0, 0, 0.3, 0.3]


def test_gate_closed_means_flat():
    H, L, C, dates, btc = synth()
    W, m200 = S.build_W(H, L, C, dates, btc)
    closed = ~(btc > m200)
    for w in W.values():
        assert (w[:, closed] == 0).all()
    assert closed.any() and (~closed).any()


def test_costs_charged_on_scale_change():
    # a position whose weight is only rescaled by the cap still pays turnover cost
    E2 = S.cap(np.array([[0.5, 0.5, 0.5], [0.0, 0.5, 0.5], [0.0, 0.0, 0.5]]))
    P = S.pnl_matrix(E2, np.zeros_like(E2), np.zeros_like(E2))
    assert P[0, 1] == 0 and P[0, 2] < 0             # coin 0: weight 0.5, 0.5, then 0.333 only because of the cap: cost charged on the change
