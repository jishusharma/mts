"""R3: the Fabio v3 emitter (live_runner_cli.py.new) reads the live order-flow writer's files when the klines feed has no
order-flow columns. Loaded from the staged .new while it exists, else from live_runner_cli.py (after promotion);
OF_FEED_TEST_SOURCE=py forces the unpromoted file (fail-first check). Writer rows are real orderflow_bars.COLUMNS rows."""
import datetime as dt
import os
import tempfile
import time
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN = 60000


def _load_cli():
    staged = HERE / "live_runner_cli.py.new"
    path = staged if staged.exists() and os.environ.get("OF_FEED_TEST_SOURCE") != "py" else HERE / "live_runner_cli.py"
    loader = SourceFileLoader("live_runner_cli_of_feed_under_test", str(path))
    mod = module_from_spec(spec_from_loader("live_runner_cli_of_feed_under_test", loader))
    loader.exec_module(mod)
    return mod


cli = _load_cli()
from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob  # noqa: E402
from MyTradingSys.backtest.layers.fabio import orderflow_live as ol  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc  # noqa: E402
from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry, empty_state, run_registry  # noqa: E402

_HAS = hasattr(cli, "fabio_v3_live_flow")
DAY = dt.date(2026, 10, 5)  # a Monday
T0 = int(ny_open_utc(DAY).timestamp() * 1000)


def of_row(t, thr_days=5):
    r = {c: 0.0 for c in ob.COLUMNS}
    r.update({"t": t, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "buy_vol": 2.0, "sell_vol": 1.0, "delta": 1.0,
              "b99_buy_vol": 0.5, "n_agg": 3, "n_trades": 3, "thr_days": thr_days, "fp": "100:2.0:1.0"})
    for c in ob.INT_COLS:
        r[c] = int(r[c])
    return r


def kline(t):
    return {"t": t, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 3.0, "tbv": 2.0}


def write(d, ts, thr_days=5):
    ol.append_rows(d, DAY, [of_row(t, thr_days) for t in ts])


class TestLiveFlow(unittest.TestCase):
    def setUp(self):
        self.assertTrue(_HAS, "fabio_v3_live_flow absent: emitter lacks the order-flow file reader")
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.ts = [T0 + k * MIN for k in range(10)]

    def flow(self, klines):
        return cli.fabio_v3_live_flow(klines, of_dir=self.d)

    def test_klines_plus_writer_files_give_window(self):
        write(self.d, self.ts)
        win = self.flow([kline(t) for t in self.ts[-5:]])
        self.assertEqual([b["t"] for b in win], self.ts)
        self.assertEqual(win[0]["thr_days"], 5)

    def test_no_files_silent(self):
        self.assertIsNone(self.flow([kline(t) for t in self.ts[-5:]]))

    def test_gap_silent(self):
        write(self.d, self.ts[:4] + self.ts[5:])
        self.assertIsNone(self.flow([kline(t) for t in self.ts[-5:]]))

    def test_thr_days_zero_silent(self):
        write(self.d, self.ts, thr_days=0)
        self.assertIsNone(self.flow([kline(t) for t in self.ts[-5:]]))

    def test_writer_behind_klines_silent(self):
        write(self.d, self.ts[:-1])
        self.assertIsNone(self.flow([kline(t) for t in self.ts[-5:]]))

    def test_writer_ahead_is_cut_at_last_kline(self):
        write(self.d, self.ts)
        win = self.flow([kline(t) for t in self.ts[:6]])
        self.assertEqual(win[-1]["t"], self.ts[5])

    def test_corrupt_file_silent(self):
        (self.d / f"{DAY.isoformat()}.csv").write_text("t,o\nxx,1\n")
        self.assertIsNone(self.flow([kline(t) for t in self.ts[-5:]]))

    def test_bars_with_flow_columns_do_not_read_files(self):
        bars = [of_row(t) for t in self.ts]
        self.assertEqual(self.flow(bars), bars)

    def test_empty_bars(self):
        self.assertFalse(self.flow([]))

    def test_layer_emits_from_files_through_registry(self):
        write(self.d, self.ts)
        old = cli.FABIO_V3_OF_DIR
        cli.FABIO_V3_OF_DIR = self.d
        try:
            fn = cli.make_fabio_v3_layer(grid={"N": (60,)}, decisions={"N": "SHADOW"},
                                         fixed={"g": "off", "entry_mode": "confirm", "mgmt": "event"},
                                         run_fn=lambda win, cfg: {"verdict": "SIGNAL", "model": "B", "side": 1,
                                                                  "entry": 100.0, "stop": 99.0, "target": 103.0})
            reg = build_registry([{"layer": "fabio", "sub": "v3_grid", "tf": "1m", "fn": fn, "params_id": "t",
                                   "confirm_lag_bars": 0}])
            res = run_registry(reg, {"1m": [kline(t) for t in self.ts[-5:]]}, empty_state())
        finally:
            cli.FABIO_V3_OF_DIR = old
        self.assertEqual(res["errors"], [])
        self.assertEqual(len(res["alerts"]), 1)
        a = res["alerts"][0]
        self.assertTrue(a.get("collection_only"))
        self.assertNotIn("side", a)


if __name__ == "__main__":
    unittest.main()
