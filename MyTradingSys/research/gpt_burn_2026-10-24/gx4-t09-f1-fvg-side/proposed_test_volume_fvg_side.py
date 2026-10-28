import MyTradingSys.backtest.layers.alerts.live_layers as live_layers


def test_volume_fvg_side_matches_backtest_bounce(monkeypatch):
    """A confirmed close above the level produces the backtest bounce-long side."""
    bars = [{"t": i, "l": 9.0, "h": 11.0, "c": 10.5} for i in range(25)]
    monkeypatch.setattr(live_layers, "swing_legs", lambda *a, **k: [{"a_i": 0, "b_i": 20, "confirmed_i": 20}])
    monkeypatch.setattr(live_layers, "build_profile", lambda *a, **k: object())
    monkeypatch.setattr(live_layers, "value_area", lambda *a, **k: object())
    monkeypatch.setattr(live_layers, "lowest_volume_level", lambda *a, **k: {"price_lo": 9.9, "price_hi": 10.1})

    event = live_layers.volume_fvg_layer(bars)[0]

    assert event["side"] == "long"
