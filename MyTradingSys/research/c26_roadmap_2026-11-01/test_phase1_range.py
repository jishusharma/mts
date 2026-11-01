"""phase1_range.py pure parts: the divergence detector is causal and the 1m -> TF aggregation is right. No network, no bars."""
import importlib.util, os

_spec = importlib.util.spec_from_file_location("phase1_range", os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase1_range.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def test_import_has_no_side_effects():
    assert R.P is None  # phase1_recent (argv, downloads) is loaded by main() only


def test_bearish_divergence_needs_higher_high_and_lower_rsi_within_lookback():
    # pivot highs (K=3) at 5 (100), 15 (101, RSI lower -> divergence), 25 (102, RSI higher -> none), 95 (103, prior pivot 70 bars back -> none)
    H = [90.0] * 100
    for p, h in ((5, 100.0), (15, 101.0), (25, 102.0), (95, 103.0)):
        H[p] = h
    RSI = [50.0] * 100
    RSI[5], RSI[15], RSI[25], RSI[95] = 70.0, 65.0, 80.0, 60.0
    assert R.bearish_divs(H, RSI) == [15]


def test_divergence_is_unknown_before_the_confirming_bar():
    # the same series cut at p+K-1 must not show the signal; cut at p+K it must
    H = [90.0] * 40; H[5], H[15] = 100.0, 101.0
    RSI = [50.0] * 40; RSI[5], RSI[15] = 70.0, 65.0
    assert R.bearish_divs(H[:15 + R.K], RSI[:15 + R.K]) == []
    assert R.bearish_divs(H[:15 + R.K + 1], RSI[:15 + R.K + 1]) == [15]


def test_tf_bars_aggregates_high_low_close_aligned_to_epoch():
    m1 = [[60000 * i, 1.0, 10.0 + i, 5.0 - i, 7.0 + i, 1.0, 0.5] for i in range(6)]
    b = R.tf_bars(m1, 3)
    assert [x[0] for x in b] == [0, 180000]
    assert b[0][1:] == [12.0, 3.0, 9.0] and b[1][1:] == [15.0, 0.0, 12.0]
