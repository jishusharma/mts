"""W3 wiring: layers shipped by W1a/W1b/W2a (+ wlow long flag) registered for TESTNET sampling (operator 2026-10-16).

Pins: the registry keys; the history store (cold start, incremental, restart, API error, gap, wrong symbol, short
history -> fail closed); wlow flag ON = long / OFF = side-less; shipped config sizes + grandfather entries; a source
WITHOUT a pre_pipeline entry is still rejected by the promotion gate; the new sources open no new account.
"""
import copy
import datetime as dt
import json
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.test_wlow_bounce_emitter import candles, runner_bars
from MyTradingSys.backtest.layers.wlow_bounce.test_detector import LOOSE

_AT = Path(__file__).resolve().parents[2].parent / "execution" / "auto_trader.py"   # by path: layer purity gate
_loader = SourceFileLoader("auto_trader_w3_test", str(_AT))
at = module_from_spec(spec_from_loader("auto_trader_w3_test", _loader))
_loader.exec_module(at)
SHIPPED = _AT.parent / "auto_trader_config.json"

NEW_KEYS = {  # registry key -> (source prefix, tf)
    "rsi_divergence|rsi_divergence|1h": ("layer:rsi_divergence:", "1h"),
    "bb_top_reversal|bb_top_reversal|15m": ("layer:bb_top_reversal:", "15m"),
    "session_levels|session_levels|1m": ("layer:session_levels:", "1m"),
    "candle_close|candle_close|1m": ("layer:candle_close:", "1m"),
    "levels|confluence|1m": ("layer:levels:", "1m"),
    "wlow_bounce|bbrsi60|1h": ("layer:wlow_bounce:", "1h"),
}
UNREG = "unregistered (promotion pipeline)"
MIN = 60000
T0 = 1_700_000_040_000 // MIN * MIN


def shipped():
    c = at.load_config(SHIPPED)
    c["trade_blocklist"], c["trade_blocklist_reasons"] = [], {}   # promotion gate only
    return c


def row(t):
    c = 100.0 + (t // MIN) % 50
    return [t, c, c + 1, c - 1, c, 10.0, t + MIN - 1, 0.0, 1, 5.0, 0.0, 0]


class Feed:
    """Fake kline pages over 1m bars T0..T0+n-1 (the last row is the still-open bar, as on Binance)."""
    def __init__(self, n, symbol="BTCUSDT", fail=None, gap_at=None):
        self.n, self.symbol, self.fail, self.gap_at, self.calls = n, symbol, fail, gap_at, []
        self.shift = 0.0

    def __call__(self, symbol, interval, start_ms, limit):
        self.calls.append(start_ms)
        if self.fail:
            raise OSError("boom")
        rows = [row(T0 + i * MIN) for i in range(self.n) if T0 + i * MIN >= start_ms and i != self.gap_at]
        if symbol != self.symbol:
            rows = [r[:4] + [r[4] + 5] + r[5:] for r in rows]
        return rows[:limit]

    def closed(self, k):
        """The k newest closed bars, the way the runner passes them (open bar dropped)."""
        return cli.klines_to_bars([row(T0 + i * MIN) for i in range(self.n - 1 - k, self.n - 1)])


class TestRegistry(unittest.TestCase):
    def test_new_keys_registered_with_expected_tf(self):
        reg = cli.build_default_registry()
        for key, (prefix, tf) in NEW_KEYS.items():
            self.assertIn(key, reg)
            self.assertEqual(reg[key]["tf"], tf)
            self.assertEqual("layer:%s:%s:%s" % tuple(key.split("|")), "%s%s:%s" % (prefix, key.split("|")[1], tf))

    def test_history_layers_carry_raw_adapter_for_the_rate_watchdog(self):
        reg = cli.build_default_registry()
        for key in ("session_levels|session_levels|1m", "candle_close|candle_close|1m", "levels|confluence|1m"):
            self.assertTrue(callable(getattr(reg[key]["fn"], "raw", None)), key)
        for key in ("rsi_divergence|rsi_divergence|1h", "bb_top_reversal|bb_top_reversal|15m"):
            self.assertFalse(hasattr(reg[key]["fn"], "raw"), key)

    def test_wiring_registry_no_longer_lists_the_three_wired_adapters(self):
        wr = json.loads((_AT.parent.parent / "system" / "wiring_registry.json").read_text(encoding="utf-8"))["entries"]
        for m in ("live_levels_confluence", "live_rsi_divergence", "live_session_levels"):
            self.assertNotIn("MyTradingSys/backtest/layers/alerts/%s.py" % m, wr)


class TestHistoryStore(unittest.TestCase):
    def test_cold_start_returns_exactly_need_bars_ending_at_runner_last(self):
        f = Feed(5000)
        st = cli.HistoryStore(f)
        win = st.get("1m", f.closed(99), 2900)
        self.assertEqual(len(win), 2900)
        self.assertEqual(win[-1]["t"], T0 + 4998 * MIN)
        self.assertTrue(all(b["t"] - a["t"] == MIN for a, b in zip(win, win[1:])))
        self.assertLessEqual(len(f.calls), 2900 // cli.HIST_PAGE + 2)

    def test_next_bar_is_one_small_request(self):
        f = Feed(5000)
        st = cli.HistoryStore(f)
        st.get("1m", f.closed(99), 2900)
        f.n = 5001
        n0 = len(f.calls)
        win = st.get("1m", f.closed(99), 2900)
        self.assertEqual(len(f.calls) - n0, 1)
        self.assertEqual((len(win), win[-1]["t"]), (2900, T0 + 4999 * MIN))

    def test_restart_new_store_gives_identical_window(self):
        f = Feed(5000)
        a = cli.HistoryStore(f).get("1m", f.closed(99), 2900)
        b = cli.HistoryStore(f).get("1m", f.closed(99), 2900)
        self.assertEqual(a, b)

    def test_runner_window_already_long_enough_is_used_as_is(self):
        f = Feed(500)
        st = cli.HistoryStore(f)
        bars = f.closed(300)
        self.assertEqual(st.get("1m", bars, 200), bars)
        self.assertEqual(f.calls, [])

    def test_api_error_fails_closed_and_recovers(self):
        f = Feed(5000, fail=True)
        st = cli.HistoryStore(f)
        self.assertIsNone(st.get("1m", f.closed(99), 2900))
        f.fail = None
        self.assertEqual(len(st.get("1m", f.closed(99), 2900)), 2900)

    def test_gap_in_history_fails_closed(self):
        f = Feed(5000, gap_at=4000)
        self.assertIsNone(cli.HistoryStore(f).get("1m", f.closed(99), 2900))

    def test_history_shorter_than_asked_fails_closed(self):
        f = Feed(1500)
        self.assertIsNone(cli.HistoryStore(f).get("1m", f.closed(99), 2900))

    def test_history_behind_the_runner_fails_closed(self):
        f = Feed(5000)
        bars = f.closed(99)
        f.n = 4000                                    # feed lags the runner's bars
        self.assertIsNone(cli.HistoryStore(f).get("1m", bars, 2900))

    def test_other_symbol_fails_closed(self):
        f = Feed(5000, symbol="ETHUSDT")              # fetch returns a different price series than the runner's bars
        bars = Feed(5000).closed(99)
        self.assertIsNone(cli.HistoryStore(f).get("1m", bars, 2900))

    def test_layer_returns_no_events_without_history_and_never_raises(self):
        f = Feed(5000, fail=True)
        seen = []
        fn = cli.make_history_layer(lambda w: seen.append(len(w)) or [{"t": w[-1]["t"], "event": "x"}], "1m", 2900,
                                    cli.HistoryStore(f))
        self.assertEqual(fn(f.closed(99)), [])
        self.assertEqual(seen, [])
        f.fail = None
        self.assertEqual(len(fn(f.closed(99))), 1)
        self.assertEqual(seen, [2900])


class TestWlowFlag(unittest.TestCase):
    def _ev(self, **kw):
        c = candles()
        fn = cli.make_wlow_bounce_layer(fetch_candles=lambda: c, fetch_oi=lambda k: (1.0, 2.0), log_path=None,
                                        params=LOOSE, **kw)
        return fn(runner_bars(c))[0]

    def test_flag_is_on_by_default(self):
        self.assertIs(cli.WLOW_EMIT_LONG, True)
        e = self._ev()
        self.assertEqual(e["side"], "long")
        self.assertNotIn("collection_only", e)

    def test_flag_off_stays_side_less_and_collection_only(self):
        e = self._ev(emit_long=False)
        self.assertNotIn("side", e)
        self.assertIs(e["collection_only"], True)
        self.assertEqual(e["shadow_side"], "long")

    def test_module_flag_off_via_constant(self):
        saved = cli.WLOW_EMIT_LONG
        self.addCleanup(setattr, cli, "WLOW_EMIT_LONG", saved)
        cli.WLOW_EMIT_LONG = False
        self.assertNotIn("side", self._ev())

    def test_forward_log_still_written_with_flag_on(self):
        import tempfile
        c = candles()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.jsonl"
            cli.make_wlow_bounce_layer(fetch_candles=lambda: c, fetch_oi=lambda k: (1.0, 2.0), log_path=str(p),
                                       params=LOOSE)(runner_bars(c))
            rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(rows and rows[0]["collection_only"] is True)


class TestShippedConfig(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(SHIPPED.read_text(encoding="utf-8"))

    def test_new_prefixes_have_size_and_grandfather_entry(self):
        for prefix, _tf in NEW_KEYS.values():
            self.assertEqual(self.raw["size_overrides"][prefix], {"size_usd": 20, "max_loss_usd": 2}, prefix)
            g = self.raw["pre_pipeline_sources"][prefix]
            self.assertEqual(g["reason"], "grandfathered testnet calibration, operator 2026-10-16 all-layers direction; "
                                          "not an edge claim")
            self.assertEqual(g["review_by"], "2026-10-23")

    def test_failed_msb_sized_like_sr_flip_15m(self):
        so = self.raw["size_overrides"]
        self.assertEqual(so["layer:cryptocred:failed_msb:"], so["layer:cryptocred:sr_flip:15m"])

    def test_no_new_accounts(self):
        acc = self.raw["accounts"]
        self.assertFalse([k for k in acc if any(k.startswith(p) for p, _ in NEW_KEYS.values())])
        self.assertFalse([k for k in acc if "failed_msb" in k])
        self.assertEqual(set(acc.values()) - {"jishu_%d" % i for i in range(1, 22)}, set())

    def test_new_sources_trade_on_the_shared_catch_all_account(self):
        for prefix, tf in NEW_KEYS.values():
            src = "%sx:%s" % (prefix, tf)
            best = max((k for k in self.raw["accounts"] if src.startswith(k)), key=len)
            self.assertEqual(self.raw["accounts"][best], "jishu_21", src)


def _alert(layer, sub, tf, **kw):
    now = dt.datetime.now(dt.timezone.utc)
    t = int((now.timestamp() - at.TF_SECONDS[tf] * 1.1) * 1000)
    return {"layer": layer, "sub": sub, "tf": tf, "side": "long", "event": "x", "t_close": t, "sampling": True, **kw}, now


class TestPromotionGate(unittest.TestCase):
    def test_each_new_source_trades_with_shipped_config_at_20_usd(self):
        for key in NEW_KEYS:
            layer, sub, tf = key.split("|")
            a, now = _alert(layer, sub, tf)
            sig = at.layer_signal(a, shipped(), now)
            self.assertNotIn("reject", sig, (key, sig.get("reject")))
            args = sig["plan_args"]
            self.assertEqual(args[args.index("--size") + 1], "20")
            self.assertEqual(args[args.index("--max-loss") + 1], "2")

    def test_source_without_pre_pipeline_entry_is_still_rejected(self):
        for key, (prefix, _tf) in NEW_KEYS.items():
            cfg = shipped()
            del cfg["pre_pipeline_sources"][prefix]
            layer, sub, tf = key.split("|")
            a, now = _alert(layer, sub, tf)
            sig = at.layer_signal(a, cfg, now)
            self.assertEqual(sig.get("reject"), UNREG, key)
            self.assertNotIn("plan_args", sig)

    def test_wlow_flag_off_alert_is_rejected_by_the_shipped_config(self):
        a, now = _alert("wlow_bounce", "bbrsi60", "1h", collection_only=True)
        del a["side"]
        a["shadow_side"] = "long"
        sig = at.layer_signal(a, shipped(), now)
        self.assertIn("reject", sig)
        self.assertNotIn("plan_args", sig)

    def test_unreadable_config_rejects_new_sources_fail_closed(self):
        cfg = copy.deepcopy(shipped())
        cfg["pre_pipeline_sources"] = None
        a, now = _alert("levels", "confluence", "1m")
        self.assertIn("reject", at.layer_signal(a, cfg, now))

    def test_failed_msb_sized_at_200_4(self):
        a, now = _alert("cryptocred", "failed_msb", "15m")
        args = at.layer_signal(a, shipped(), now)["plan_args"]
        self.assertEqual((args[args.index("--size") + 1], args[args.index("--max-loss") + 1]), ("200", "4"))


if __name__ == "__main__":
    unittest.main()
