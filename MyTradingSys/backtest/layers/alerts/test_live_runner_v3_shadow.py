"""Fabio v3 live emitter (live_runner_cli.py.new, staged MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow).

Spec: research/FABIO_V3_SOURCING_2026-10-02.md (decision per parameter) and the T5 behaviour in the session brief:
  (a) a SHADOW v3 signal is written with a `collection_only` tag;
  (b) a SHADOW v3 signal produces zero orders (the auto-trader's own layer_signal() rejects it, no plan args);
  (c) a SOURCE v3 signal flows like any other fabio.* layer (carries "side", the auto-trader plans it).
The emitter is loaded from live_runner_cli.py.new while it is staged, else from live_runner_cli.py (after promotion).
V3_SHADOW_TEST_SOURCE=py forces the unpromoted file (fail-first check). The v3 engine is stubbed: these tests check the
routing of a signal, not Fabio's signal maths.
"""
import datetime as dt
import json
import os
import tempfile
import time
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXEC = HERE.parents[2] / "execution"      # MyTradingSys/execution
MIN = 60000
STUB_SIGNAL = {"verdict": "SIGNAL", "model": "B", "side": 1, "entry": 100.0, "stop": 99.0, "target": 103.0}


def _load(path, name):
    loader = SourceFileLoader(name, str(path))
    mod = module_from_spec(spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


def _load_cli():
    staged = HERE / "live_runner_cli.py.new"
    path = staged if staged.exists() and os.environ.get("V3_SHADOW_TEST_SOURCE") != "py" else HERE / "live_runner_cli.py"
    return _load(path, "live_runner_cli_v3_under_test")


cli = _load_cli()
_HAS_V3 = hasattr(cli, "make_fabio_v3_layer") and "fabio|v3_grid|1m" in cli.build_default_registry()
at = _load(EXEC / "auto_trader.py", "auto_trader_v3_shadow_test")
from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl   # noqa: E402
from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry, empty_state, run_registry  # noqa: E402

SMALL_GRID = {"N": (60,), "p": (0.05, 0.10)}          # 2 cells


def flow_bars(n, t_last):
    """n 1m bars ending at open time t_last, with the order-flow columns the v3 engine needs."""
    t0 = t_last - (n - 1) * MIN
    return [{"t": t0 + k * MIN, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "buy_vol": 2.0, "sell_vol": 1.0,
             "delta": 1.0, "b99_buy_vol": 0.5, "b99_sell_vol": 0.0, "thr_days": 30, "fp": "100:2:1"} for k in range(n)]


def make_registry(decisions, grid=SMALL_GRID):
    fn = cli.make_fabio_v3_layer(grid=grid, decisions=decisions, fixed={"g": "off", "entry_mode": "confirm",
                                                                        "mgmt": "event"},
                                 run_fn=lambda win, cfg: dict(STUB_SIGNAL), flow_fn=lambda bars: bars)
    return build_registry([{"layer": "fabio", "sub": "v3_grid", "tf": "1m", "fn": fn, "params_id": "test",
                            "confirm_lag_bars": 0}])


def fresh_bars():
    """A closed 1m bar whose close is `now`, so the auto-trader's staleness check (1.2 bars) passes."""
    return flow_bars(3, int(time.time() * 1000) - MIN)


def alerts_for(decisions):
    res = run_registry(make_registry(decisions), {"1m": fresh_bars()}, empty_state())
    assert res["errors"] == [], res["errors"]
    return res["alerts"]


ALL_SHADOW = {"N": "SHADOW", "p": "SHADOW"}
ALL_SOURCE = {"N": "SOURCE", "p": "SOURCE"}


@unittest.skipUnless(_HAS_V3, "v3 layer absent: staged .new not present and file not promoted")
class TestShadowSignal(unittest.TestCase):
    def test_a_shadow_signal_carries_collection_only(self):
        alerts = alerts_for(ALL_SHADOW)
        self.assertEqual(len(alerts), 2)                                   # one per grid cell
        for a in alerts:
            self.assertIs(a["collection_only"], True)
            self.assertEqual(a["decision"], "SHADOW")
            self.assertEqual(a["shadow_side"], "long")
            self.assertNotIn("side", a)
        self.assertEqual(len({a["event"] for a in alerts}), 2)             # distinct dedup keys per cell
        with tempfile.TemporaryDirectory() as d:                           # the runner's own sink: runtime/alerts/<tf>.jsonl
            p = Path(d) / "alerts" / "1m.jsonl"
            self.assertEqual(append_alerts_jsonl(alerts, p), 2)
            rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(r["collection_only"] is True and "side" not in r for r in rows))

    def test_b_shadow_signal_produces_zero_orders(self):
        now = dt.datetime.now(dt.timezone.utc)
        for a in alerts_for(ALL_SHADOW):
            self.assertIsNone(at.layer_side(a, at.DEFAULT_CONFIG))
            sig = at.layer_signal(a, at.DEFAULT_CONFIG, now)
            self.assertIsNone(sig["side"])
            self.assertIn("reject", sig)
            self.assertNotIn("plan_args", sig)                             # plan_args is the only path to new_plan.py

    def test_partial_source_is_still_shadow(self):
        # one SOURCE parameter next to a SHADOW or missing one must not make the cell tradable (fail closed)
        for dec in ({"N": "SOURCE", "p": "SHADOW"}, {"N": "SOURCE"}, {}):
            alerts = alerts_for(dec)
            self.assertTrue(alerts and all(a["collection_only"] is True and "side" not in a for a in alerts), dec)


@unittest.skipUnless(_HAS_V3, "v3 layer absent: staged .new not present and file not promoted")
class TestSourceSignal(unittest.TestCase):
    def test_c_source_signal_flows_as_ordinary_layer(self):
        alerts = alerts_for(ALL_SOURCE)
        self.assertEqual(len(alerts), 2)
        now = dt.datetime.now(dt.timezone.utc)
        for a in alerts:
            self.assertEqual(a["side"], "long")
            self.assertNotIn("collection_only", a)
            self.assertNotIn("shadow_side", a)
            self.assertEqual((a["layer"], a["sub"], a["tf"]), ("fabio", "v3_grid", "1m"))
            cfg = json.loads(json.dumps(at.DEFAULT_CONFIG))   # fable H1: fabio is grandfathered in the shipped config
            cfg["pre_pipeline_sources"] = {"layer:fabio:": {"reason": "fixture", "review_by": "2026-10-23"}}
            sig = at.layer_signal(a, cfg, now)
            self.assertEqual(sig["side"], "long")
            self.assertNotIn("reject", sig)
            self.assertEqual(sig["plan_args"][:2], ["--side", "long"])
            self.assertTrue(sig["source"].startswith("layer:fabio:"))      # routes to the fabio testnet account

    def test_short_signal_maps_to_short(self):
        fn = cli.make_fabio_v3_layer(grid={"N": (60,)}, decisions={"N": "SOURCE"},
                                     run_fn=lambda w, c: {**STUB_SIGNAL, "side": -1}, flow_fn=lambda b: b)
        ev = fn(fresh_bars())
        self.assertEqual([e["side"] for e in ev], ["short"])


@unittest.skipUnless(_HAS_V3, "v3 layer absent: staged .new not present and file not promoted")
class TestDefaults(unittest.TestCase):
    def test_default_registry_is_all_shadow_and_registered(self):
        reg = cli.build_default_registry()
        self.assertIn("fabio|v3_grid|1m", reg)
        self.assertEqual(set(cli.FABIO_V3_DECISIONS.values()), {"SHADOW"})   # FABIO_V3_SOURCING: 0 of 8 SOURCE
        cells = cli.fabio_v3_cells()
        self.assertEqual(len(cells), 3 * 2 * 3 * 2 * 2)
        self.assertEqual({cli.fabio_v3_cell_decision(c) for c in cells}, {"SHADOW"})

    def test_klines_feed_is_silent(self):
        # plain klines have no order-flow columns: the layer returns [] and raises nothing
        klines = [{"t": k * MIN, "o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": 1.0, "tbv": 0.5} for k in range(5)]
        self.assertIsNone(cli.fabio_v3_flow_window(klines))
        self.assertEqual(cli.make_fabio_v3_layer()(klines), [])

    def test_flow_window_starts_at_ny_open_and_rejects_gaps(self):
        t_open = int(dt.datetime(2026, 10, 2, 13, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)   # Fri, US DST
        bars = flow_bars(50, t_open + 39 * MIN)                      # 10 bars before the open + 40 from the open
        win = cli.fabio_v3_flow_window(bars)
        self.assertEqual((win[0]["t"], len(win)), (t_open, 40))
        gap = bars[:30] + bars[31:]
        self.assertIsNone(cli.fabio_v3_flow_window(gap))
        self.assertIsNone(cli.fabio_v3_flow_window([{**b, "thr_days": 0} for b in bars]))
        sat = flow_bars(5, int(dt.datetime(2026, 10, 3, 14, 0, tzinfo=dt.timezone.utc).timestamp() * 1000))
        self.assertIsNone(cli.fabio_v3_flow_window(sat))             # Saturday: no NY window

    def test_emitter_has_no_execution_import(self):
        src = (HERE / "live_runner_cli.py.new" if (HERE / "live_runner_cli.py.new").exists()
               else HERE / "live_runner_cli.py").read_text(encoding="utf-8")
        for line in src.splitlines():
            if line.lstrip().startswith(("import ", "from ")):
                self.assertNotIn("execution", line)


if __name__ == "__main__":
    unittest.main()
