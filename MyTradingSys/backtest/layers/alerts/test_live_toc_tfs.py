"""Spec (operator 2026-09-30): turn_of_candle alerts carry side = sign of opening (minute-0) taker imbalance +
sampling flag; extra timeframes registered; default --tfs covers every registered tf."""
from MyTradingSys.backtest.layers.alerts import live_layers as ll
from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli

Q = 900000
T0 = 1_700_000_100_000 // Q * Q  # quarter-aligned


def _quarter(open_v, open_tbv, gap=False):
    bars = []
    for m in range(15):
        if gap and m == 0:
            continue
        v, tbv = (open_v, open_tbv) if m == 0 else (10.0, 5.0)
        bars.append({"t": T0 + m * 60000, "o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": v, "tbv": tbv})
    return bars


def test_buy_imbalance_long_and_sampling():
    ev = ll.turn_of_candle_layer(_quarter(10.0, 7.5))   # imbalance (15-10)/10 = +0.5
    assert len(ev) == 1
    assert ev[0]["side"] == "long" and ev[0]["sampling"] is True
    assert ev[0]["event"] == "toc_m14" and ev[0]["t"] == T0 + 14 * 60000


def test_sell_imbalance_short():
    ev = ll.turn_of_candle_layer(_quarter(10.0, 2.0))   # (4-10)/10 = -0.6
    assert ev[0]["side"] == "short" and ev[0]["sampling"] is True


def test_zero_imbalance_no_side():
    ev = ll.turn_of_candle_layer(_quarter(10.0, 5.0))
    assert len(ev) == 1 and "side" not in ev[0] and ev[0]["sampling"] is True


def test_zero_volume_or_missing_open_bar_no_side():
    e0 = ll.turn_of_candle_layer(_quarter(0.0, 0.0))[0]
    assert "side" not in e0 and e0["sampling"] is True
    ev = ll.turn_of_candle_layer(_quarter(10.0, 9.0, gap=True))
    assert ev and "side" not in ev[0] and ev[0]["sampling"] is True


def test_registry_has_new_timeframes():
    reg = cli.build_default_registry(fetch_funding=lambda s, n: [])
    for k in ("rsi|rsi_events|5m", "fabio|cvd_absorption|15m", "fabio|escalation|15m", "fabio|volume_fvg|15m",
              "cryptocred|sr_flip|15m", "cryptocred|fib_pullback|15m", "cryptocred|failed_msb|15m"):
        assert k in reg, k
    for k in ("rsi|rsi_events|1h", "rsi|rsi_events|15m", "turn_of_candle|turn_of_candle|1m"):
        assert k in reg, k


def test_default_tfs_cover_registry(monkeypatch, tmp_path):
    seen = {}

    def fake_poll(registry, symbol, tfs, fetch_fn, state, limit=100):
        seen["tfs"] = set(tfs)
        seen["reg"] = {e["tf"] for e in registry.values()}
        return {"alerts": [], "state": state, "errors": []}
    monkeypatch.setattr(cli, "poll_once", fake_poll)
    assert cli.main(["--once", "--alerts-dir", str(tmp_path), "--state-path", str(tmp_path / "s.json")]) == 0
    assert seen["reg"] <= seen["tfs"] and "5m" in seen["tfs"]
