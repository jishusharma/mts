"""Fail-first tests for the CryptoCred S3 DEV wrapper (cc_s3_run.py). Expected numbers are hand-computed
from FORMULAS.md (R definition, 18.7 day-block bootstrap worked example, Wilder ATR) and the PRE_REG."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))

import cc_s3_run as S  # noqa: E402

DEV_END_MS = 1719792000000  # 2024-07-01T00:00Z exclusive


def _bar(t, o=1.0, h=1.0, l=1.0, c=1.0):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": 1.0}


def test_runner_raises_on_any_bar_after_dev_end():
    ok = [_bar(DEV_END_MS - 60000)]
    S.assert_bars_dev_only(ok)  # last DEV minute is fine
    bad = ok + [_bar(DEV_END_MS)]  # 2024-07-01 00:00 is VALIDATION
    with pytest.raises(Exception):
        S.assert_bars_dev_only(bad)
    with pytest.raises(Exception):
        S.assert_bars_dev_only([_bar(1640995200000 - 60000)])  # before DEV start


def test_mean_net_r_of_three_trade_ledger():
    # hand: (1.4 + (-1.1) + 1.4) / 3 = 1.7 / 3 = 0.566666...
    ledger = [{"net_r": 1.4}, {"net_r": -1.1}, {"net_r": 1.4}]
    assert S.mean_net_r(ledger) == pytest.approx(0.5666666667, abs=1e-9)
    assert S.mean_net_r([]) is None


def test_day_block_worked_example_from_formulas_18_7():
    # day A R=[1,3], day B R=[-2]; (A,A) -> 2.0, (B,B) -> -2.0, (A,B) -> 0.6667
    sums, counts = [4.0, -2.0], [2, 1]
    assert S.day_block_mean(sums, counts, [0, 0]) == pytest.approx(2.0)
    assert S.day_block_mean(sums, counts, [1, 1]) == pytest.approx(-2.0)
    assert S.day_block_mean(sums, counts, [0, 1]) == pytest.approx(2.0 / 3.0)


def test_wilder_atr_hand_example():
    # TR = 2, 3, 4, 6 (prev close inside range). period 3: seed = (2+3+4)/3 = 3; next = (3*2 + 6)/3 = 4
    bars = [_bar(0, 11, 12, 10, 11), _bar(1, 11, 14, 11, 12), _bar(2, 12, 16, 12, 15), _bar(3, 15, 21, 15, 20)]
    assert S.true_ranges(bars) == [2.0, 3.0, 4.0, 6.0]
    assert S.wilder_atr(bars, 2, 3) == pytest.approx(3.0)
    assert S.wilder_atr(bars, 3, 3) == pytest.approx(4.0)
    assert S.wilder_atr(bars, 1, 3) is None  # not enough history; no forward bars used


def test_redesign_stop_is_invalidation_plus_atr_buffer_and_target_recomputed():
    long_sig = {"side": "long", "entry_price": 100.0, "entry_t": 5, "stop": 100.0,
                "targets": [(100.0, 1.0)], "meta": {"setup": "sr_flip", "target_r": 1.5}}
    s = S.redesign_signal(long_sig, atr=2.0, k=1.0)
    assert s["stop"] == pytest.approx(98.0)
    assert s["targets"][0][0] == pytest.approx(103.0)  # 100 + 1.5 * 2
    s5 = S.redesign_signal(long_sig, atr=2.0, k=0.5)
    assert s5["stop"] == pytest.approx(99.0) and s5["targets"][0][0] == pytest.approx(101.5)
    short_sig = dict(long_sig, side="short", stop=100.0)
    t = S.redesign_signal(short_sig, atr=2.0, k=1.0)
    assert t["stop"] == pytest.approx(102.0) and t["targets"][0][0] == pytest.approx(97.0)


def test_validation_read_is_gated_on_dev_pass_flag(tmp_path):
    f = tmp_path / "RESULT.md"
    f.write_text("# r\nDEV_PASS: no\n", encoding="utf-8")
    with pytest.raises(Exception):
        S.require_dev_pass(f)
    f.write_text("# r\nDEV_PASS: yes\n", encoding="utf-8")
    S.require_dev_pass(f)
    with pytest.raises(Exception):
        S.require_dev_pass(tmp_path / "missing.md")


def test_verdict_classes():
    # n<100 -> INCONCLUSIVE in advance even with a big mean
    assert S.classify(n=50, mean=0.5, lo=0.2, holm_p=0.001) == "INCONCLUSIVE"
    assert S.classify(n=200, mean=0.3, lo=0.1, holm_p=0.01) == "PASS"
    assert S.classify(n=200, mean=0.1, lo=-0.05, holm_p=0.4) == "INCONCLUSIVE"  # 0..MDE is never "no edge"
    assert S.classify(n=200, mean=-0.1, lo=-0.3, holm_p=1.0) == "FAIL"
