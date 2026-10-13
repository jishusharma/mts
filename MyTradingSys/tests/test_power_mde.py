import pytest

from MyTradingSys.backtest.power_mde import power_mde


@pytest.mark.parametrize(
    "p, rr, cost, means, expected_power, expected_80",
    [
        (0.45, 1.5, 0.012, 0.11, (15, 20, 35), 951),
        (0.45, 1.5, 0.062, 0.06, (7, 9, 14), 3059),
        (0.40, 2.0, 0.012, 0.19, (25, 35, 60), 480),
        (0.40, 2.0, 0.062, 0.14, (15, 21, 37), 890),
        (0.45, 2.0, 0.062, 0.29, (49, 66, 92), 211),
        (0.45, 2.5, 0.062, 0.51, (84, 95, 100), 90),
    ],
)
def test_reproduces_g1_table(p, rr, cost, means, expected_power, expected_80):
    results = [power_mde(p, rr, cost, n) for n in (100, 150, 300)]
    assert round(results[0]["mean_net_r"], 2) == pytest.approx(means)
    for result, expected in zip(results, expected_power):
        assert result["power"] * 100 == pytest.approx(expected, abs=2)
    estimate = power_mde(p, rr, cost, 100)["trades_for_80_power"]
    assert estimate == pytest.approx(expected_80, rel=0.02)


def test_requested_anchor_rows():
    low = power_mde(0.45, 1.5, 0.012, 100)
    high = power_mde(0.45, 2.5, 0.062, 100)
    assert round(low["mean_net_r"], 2) == pytest.approx(0.11)
    assert low["power"] == pytest.approx(0.15, abs=0.02)
    assert high["power"] == pytest.approx(0.84, abs=0.02)
    assert power_mde(0.45, 1.5, 0.012, 100)["trades_for_80_power"] == pytest.approx(951, rel=0.05)
    assert power_mde(0.45, 2.5, 0.062, 100)["trades_for_80_power"] == pytest.approx(90, rel=0.05)
