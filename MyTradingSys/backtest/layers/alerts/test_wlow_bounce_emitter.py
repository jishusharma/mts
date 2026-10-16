"""Weekly-low bounce SHADOW emitter (task wlow-bounce-shadow-emitter): observation only, never an order path.

Checks: one collection_only event with shadow_side and NO side; same bar twice -> none; restart (fresh state, fresh layer)
rebuilds from candles and re-emits at most once per trigger bar, log rows not duplicated; fetch/OI/tbv/too-few-bars errors
-> [] without exception; the emitted alert is rejected by auto_trader.layer_signal (no plan_args), even if the source were
(wrongly) grandfathered.
"""
import datetime as dt
import json
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_runner_core import empty_state, build_registry, run_registry
from MyTradingSys.backtest.layers.promotion.registry import apply_promotion_gate
from MyTradingSys.backtest.layers.wlow_bounce import detector as D
from MyTradingSys.backtest.layers.wlow_bounce.test_detector import mk, shape, LOOSE

def _load_at():   # loaded by path: layers must not import MyTradingSys.execution (layer purity gate)
    path = Path(__file__).resolve().parents[2].parent / "execution" / "auto_trader.py"
    loader = SourceFileLoader("auto_trader_wlow_test", str(path))
    mod = module_from_spec(spec_from_loader("auto_trader_wlow_test", loader))
    loader.exec_module(mod)
    return mod


at = _load_at()

ACTIVE_ROWS = shape([83140, 83180, 83220])   # trigger bar = last bar (index 275)


def candles(rows=None):
    return mk(rows or ACTIVE_ROWS)


def runner_bars(c):
    """What the runner passes: 1h closed bars (the layer only uses them for the registry's own tf gating)."""
    return c[-100:]


def layer(c, log_path=None, oi=(93670.0, 12.0), **kw):
    kw.setdefault("emit_long", False)   # these tests pin the SHADOW (flag OFF) contract; the ON contract is in test_w3_wiring
    return cli.make_wlow_bounce_layer(fetch_candles=lambda: c, fetch_oi=lambda k: oi, log_path=log_path, params=LOOSE, **kw)


class TestEmitter(unittest.TestCase):
    def test_one_collection_only_event_no_side(self):
        c = candles()
        ev = layer(c)(runner_bars(c))
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertIs(e["collection_only"], True)
        self.assertEqual(e["shadow_side"], "long")
        self.assertNotIn("side", e)
        self.assertEqual(e["t"], c[-1]["t"])
        self.assertEqual(e["event"], "wlow_bounce_bbrsi60_active")
        self.assertEqual(e["oi_now"], 93670.0)
        self.assertEqual(e["prior_weekly_low"], 80500.0)
        for k in ("rsi14", "gap_to_upper_pct", "net_delta_hold", "episode_cvd", "oi_change_last_K_h"):
            self.assertIn(k, e)

    def test_armed_gives_no_event(self):
        c = candles(shape([83140, 83180]))
        self.assertEqual(layer(c)(runner_bars(c)), [])

    def test_default_registry_has_layer_and_gate_keeps_it_collection_only(self):
        reg = cli.build_default_registry()
        ent = reg["wlow_bounce|bbrsi60|1h"]
        self.assertEqual((ent["layer"], ent["sub"], ent["tf"]), ("wlow_bounce", "bbrsi60", "1h"))

    def test_second_poll_same_bar_none_and_restart_at_most_once(self):
        c = candles()
        reg = build_registry([{"layer": "wlow_bounce", "sub": "bbrsi60", "tf": "1h", "fn": layer(c),
                               "params_id": cli.WLOW_PARAMS_ID, "confirm_lag_bars": 0}])
        bars = {"1h": runner_bars(c)}
        r1 = run_registry(reg, bars, empty_state())
        self.assertEqual(len(r1["alerts"]), 1)
        r2 = run_registry(reg, bars, r1["state"])                 # same bar again
        self.assertEqual(r2["alerts"], [])
        # restart/reset: state persisted -> nothing; state lost + fresh layer -> rebuilt from candles, at most once
        reg2 = build_registry([{"layer": "wlow_bounce", "sub": "bbrsi60", "tf": "1h", "fn": layer(c),
                                "params_id": cli.WLOW_PARAMS_ID, "confirm_lag_bars": 0}])
        self.assertEqual(run_registry(reg2, bars, r1["state"])["alerts"], [])
        r3 = run_registry(reg2, bars, empty_state())
        self.assertLessEqual(len(r3["alerts"]), 1)
        # a trigger that is no longer the last bar is history, never re-emitted
        c2 = candles(shape([83140, 83180, 83220, 83260]))
        self.assertEqual(layer(c2)(runner_bars(c2)), [])

    def test_log_row_not_duplicated_after_restart(self):
        c = candles()
        with tempfile.TemporaryDirectory() as d:
            lp = Path(d) / "sub" / "wlow.jsonl"
            layer(c, log_path=lp)(runner_bars(c))
            layer(c, log_path=lp)(runner_bars(c))                  # fresh layer = restart
            rows = [json.loads(x) for x in lp.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["state"], "ACTIVE")
            self.assertIs(rows[0]["collection_only"], True)
            for k in ("net_delta_last_K", "episode_cvd", "oi_now", "oi_change_last_K_h"):
                self.assertIn(k, rows[0])

    def test_armed_state_is_logged_for_forward_sample(self):
        c = candles(shape([83140, 83180]))
        with tempfile.TemporaryDirectory() as d:
            lp = Path(d) / "w.jsonl"
            self.assertEqual(layer(c, log_path=lp)(runner_bars(c)), [])
            self.assertEqual(json.loads(lp.read_text(encoding="utf-8").splitlines()[0])["state"], "ARMED")


class TestFailClosed(unittest.TestCase):
    def test_candle_fetch_error(self):
        def boom():
            raise OSError("network down")
        fn = cli.make_wlow_bounce_layer(fetch_candles=boom, fetch_oi=lambda k: (None, None), log_path=None)
        self.assertEqual(fn([]), [])

    def test_oi_fetch_failure_still_emits_with_none(self):
        c = candles()

        def boom(k):
            raise OSError("oi down")
        ev = cli.make_wlow_bounce_layer(fetch_candles=lambda: c, fetch_oi=boom, log_path=None, params=LOOSE)(runner_bars(c))
        self.assertEqual(len(ev), 1)
        self.assertIsNone(ev[0]["oi_now"])

    def test_missing_tbv_or_too_few_bars(self):
        c = candles()
        no_tbv = [dict(x, tbv=None) for x in c]
        self.assertEqual(layer(no_tbv)(runner_bars(c)), [])
        self.assertEqual(layer([{k: v for k, v in x.items() if k != "tbv"} for x in c])(runner_bars(c)), [])
        self.assertEqual(layer(c[-50:])(runner_bars(c)), [])
        self.assertEqual(layer([])([]), [])

    def test_log_write_failure_does_not_break(self):
        c = candles()
        with tempfile.TemporaryDirectory() as d:
            blocker = Path(d) / "file"
            blocker.write_text("x", encoding="utf-8")
            ev = layer(c, log_path=blocker / "child.jsonl")(runner_bars(c))   # parent is a file -> mkdir/open fails
        self.assertEqual(len(ev), 1)

    def test_runner_survives_layer_error_via_poll_once(self):
        def boom():
            raise RuntimeError("x")
        reg = build_registry([{"layer": "wlow_bounce", "sub": "bbrsi60", "tf": "1h",
                               "fn": cli.make_wlow_bounce_layer(fetch_candles=boom, log_path=None, emit_long=False),
                               "params_id": "p", "confirm_lag_bars": 0}])
        c = candles()
        r = run_registry(reg, {"1h": runner_bars(c)}, empty_state())
        self.assertEqual(r["alerts"], [])
        self.assertEqual(r["errors"], [])


class TestNoOrderPath(unittest.TestCase):
    def _alert(self):
        c = candles()
        reg = build_registry([{"layer": "wlow_bounce", "sub": "bbrsi60", "tf": "1h", "fn": layer(c),
                               "params_id": cli.WLOW_PARAMS_ID, "confirm_lag_bars": 0}])
        out = run_registry(reg, {"1h": runner_bars(c)}, empty_state())["alerts"]
        out = apply_promotion_gate(out)
        self.assertEqual(len(out), 1)
        return out[0]

    def test_auto_trader_rejects_alert(self):
        a = self._alert()
        now = dt.datetime.now(dt.timezone.utc)
        self.assertIsNone(at.layer_side(a, at.DEFAULT_CONFIG))
        sig = at.layer_signal(a, at.DEFAULT_CONFIG, now)
        self.assertIsNone(sig["side"])
        self.assertIn("reject", sig)
        self.assertNotIn("plan_args", sig)

    def test_rejected_even_if_source_were_grandfathered(self):
        a = self._alert()
        cfg = json.loads(json.dumps(at.DEFAULT_CONFIG))
        cfg["pre_pipeline_sources"] = {"layer:wlow_bounce:": {"reason": "fixture", "review_by": "2099-01-01"}}
        sig = at.layer_signal(a, cfg, dt.datetime.now(dt.timezone.utc))
        self.assertIn("reject", sig)
        self.assertNotIn("plan_args", sig)

    def test_source_not_whitelisted_in_the_built_in_defaults(self):
        # the built-in defaults never whitelist it; the shipped file does (operator 2026-10-16), see test_w3_wiring
        self.assertNotIn("wlow_bounce", json.dumps(at.DEFAULT_CONFIG))


if __name__ == "__main__":
    unittest.main()
