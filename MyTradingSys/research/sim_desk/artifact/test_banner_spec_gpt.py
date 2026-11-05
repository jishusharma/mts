"""Independent spec tests for banner_of's trade-list fallback."""
from MyTradingSys.research.sim_desk.artifact.build_artifact import banner_of


def result_with_trades(nets, verdict="PASS"):
    return {
        "verdict": {"label": verdict, "tone": "good"},
        "kpis": [],
        "examples": [{"kind": "trade_chart", "trades": [{"net": x} for x in nets]},],
    }


def test_trade_list_supplies_trade_count_and_hand_computed_mean_percent():
    # Hand calculation: (1.2 - 0.3 + 0.6) / 3 = 0.5 % per trade.
    out = banner_of(result_with_trades([1.2, -0.3, 0.6]))
    assert out["n"] == 3
    assert out["net_pct"] == 0.5


def test_trade_list_fallback_never_turns_written_pass_into_pass():
    # Even a positive mean and a written PASS do not make percentage returns into R.
    out = banner_of(result_with_trades([1.0] * 30))
    assert out["state"] != "PASS"
    assert "PASS" not in out["text"].split("·")[0]


def test_trade_list_with_fewer_than_thirty_is_too_few():
    out = banner_of(result_with_trades([0.2] * 29, verdict="PASS"))
    assert out["n"] == 29
    assert out["state"] == "TOO_FEW"
    assert "TOO FEW" in out["text"]


def test_percent_fallback_keeps_net_r_none():
    out = banner_of(result_with_trades([1.2, -0.3, 0.6]))
    assert out["net_r"] is None
    assert out["net_pct"] == 0.5


def test_thirty_trade_fallback_remains_unclear_even_with_positive_mean():
    # Hand calculation: thirty trades at +0.4% average +0.4 %/trade.
    out = banner_of(result_with_trades([0.4] * 30))
    assert out["n"] == 30
    assert out["net_pct"] == 0.4
    assert out["state"] == "UNCLEAR"
