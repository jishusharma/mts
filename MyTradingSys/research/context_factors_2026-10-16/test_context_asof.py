"""Tests for context_asof.py on synthetic tapes (no market data, CI-safe).

1. replay == vectorised at sampled decision hours (both sides, every key).
2. truncation invariance: the vectorised row at T is the same from bars[0..t] and from bars[0..t+N].
3. every planted leak (context_asof.LEAKS) is caught by the truncation test, and the clean build passes at the same T.
4. hand values: candle patterns, Krown chaining, BB state, phase A, F3 cost floor, DEV guard.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_asof as C  # noqa: E402
import synth  # noqa: E402

BARS = synth.tape(110)
FULL = {s: C.context_frame(BARS, s) for s in ("long", "short")}


def _cut(bars, t):
    return {k: (v[:t + 1] if k in ("ot", "o", "h", "l", "c", "v") else v) for k, v in bars.items()}


def test_replay_equals_vectorised():
    Ts = list(synth.hour_ts(BARS, 2, every=97)) + list(synth.hour_ts(BARS, 92, every=11))
    n = 0
    for T in Ts:
        t = C.decision_index(BARS, T)
        if t < 0:
            continue
        both = C._replay_both(BARS, t)
        for s in ("long", "short"):
            diff = C.row_diff(both[s], FULL[s].loc[T].to_dict())
            assert not diff, (T, s, {k: (both[s][k], FULL[s].loc[T, k]) for k in diff})
        n += 1
    assert n >= 40


def test_replay_ignores_bars_after_t():
    T = int(synth.hour_ts(BARS, 95, every=1)[5])
    t = C.decision_index(BARS, T)
    a = C._replay_both(BARS, t)
    b = C._replay_both(_cut(BARS, t), t)
    for s in ("long", "short"):
        assert not C.row_diff(a[s], b[s])


def _trunc_rows(side, T, leak=None, N=2100):
    t = C.decision_index(BARS, T)
    short = C.context_frame(_cut(BARS, t), side, leak=leak, decisions=[T]).iloc[0].to_dict()
    long_ = C.context_frame(_cut(BARS, min(t + N, len(BARS["ot"]) - 1)), side, leak=leak, decisions=[T]).iloc[0].to_dict()
    return short, long_


def test_truncation_invariance_clean():
    for T in synth.hour_ts(BARS, 93, every=331)[:5]:
        if C.decision_index(BARS, T) < 0:
            continue
        for s in ("long", "short"):
            a, b = _trunc_rows(s, int(T))
            assert not C.row_diff(a, b), (T, s, C.row_diff(a, b))


@pytest.mark.parametrize("leak", C.LEAKS)
def test_planted_leak_is_caught(leak):
    side = "short" if leak == "f5_next_bar" else "long"
    leaky = C.context_frame(BARS, side, leak=leak)
    clean = FULL[side]
    cand = [int(T) for T in clean.index if C.row_diff(leaky.loc[T].to_dict(), clean.loc[T].to_dict())
            and C.decision_index(BARS, int(T)) >= 0 and int(T) < int(BARS["ot"][-1]) - 8 * C.DAY]
    assert cand, f"{leak}: the planted leak changes nothing on this tape"
    caught = 0
    for T in cand[:: max(1, len(cand) // 4)][:4]:
        a, b = _trunc_rows(side, T, leak=leak)
        caught += bool(C.row_diff(a, b))
        ca, cb = _trunc_rows(side, T)
        assert not C.row_diff(ca, cb), (leak, T, "clean build not invariant")
    assert caught >= 1, f"{leak}: truncation test missed the planted leak"


def test_candle_hand_values():
    # bull engulf: red 100->95, then green 94->101 (opens below the red close, closes above the red open)
    assert C._candle_cat([90, 100, 94], [91, 101, 102], [89, 94, 93], [91, 95, 101]) == "bull_engulf"
    # classic variant also needs the open at/below the previous close; with a 0.1 tick gap up it fails
    assert C._engulf_cls([90, 100, 94], [91, 95, 101]) == "bull"
    assert C._engulf_cls([90, 100, 95.1], [91, 95, 101]) == "none"
    assert C._candle_cat([90, 100, 95.1], [91, 101, 102], [89, 94, 93], [91, 95, 101]) == "bull_engulf"
    # inside bar: high 104 <= 105, low 99 >= 98, body not small enough for a pin
    assert C._candle_cat([90, 100, 100], [91, 105, 104], [89, 98, 99], [91, 101, 103]) == "inside"
    # pin bull: range 10, lower wick 7 (>= 6), body 1 (<= 3)
    assert C._candle_cat([90, 100, 107], [91, 109, 110], [89, 99, 100], [91, 105, 108]) == "pin_bull"
    assert C._align("pin_bull", "long") == "with" and C._align("pin_bull", "short") == "against"


def test_krown_cluster_hand_values():
    # tol 10: 100, 105 chain (gap 5); 130 alone; 200, 209, 215 chain (gaps 9, 6)
    piv = [(105, 3), (100, 1), (130, 2), (209, 6), (200, 9), (215, 4)]
    got = C._cluster(piv, 10)
    assert got == [(102.5, 3), (208.0, 6)]


def test_bb_state_hand_values():
    bw_up = [1.0, 1.1, 1.2, 1.3]
    assert C._bb_state([False, True, True, True], [False] * 4, bw_up, 3) == "walk_lower"
    assert C._bb_state([False, True, True, True], [False] * 4, [1.3, 1.2, 1.1, 1.0], 3) == "break_lower"
    assert C._bb_state([False, False, True, False], [False] * 4, bw_up, 3) == "reenter_lower"


def test_phase_and_cost_floor():
    assert C._phase_a(+1.0, +0.5) == "markup" and C._phase_a(+1.0, -0.5) == "distribution"
    assert C._phase_a(-1.0, -0.5) == "markdown" and C._phase_a(-1.0, +0.5) == "accumulation"
    assert abs(C.W_MIN - 0.56) < 1e-12


def test_dev_guard():
    b = {k: v.copy() for k, v in BARS.items()}
    b["ot"] = b["ot"] + (C.DEV_END_MS - int(b["ot"][0]))
    with pytest.raises(ValueError):
        C.context_frame(b, "long")
