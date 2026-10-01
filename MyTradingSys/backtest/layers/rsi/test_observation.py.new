"""Tests for rsi/observation.py. Alert lines below are hand-written in the real alert shape: alert_emitter.format_alert
(alert_emitter.py:36-49: layer, sub, tf, params_id, rsi, rsi_ma, t -> t_close, + the event's own keys), plus t_confirm
(live_runner_core.py:151), serialized with sort_keys like append_alerts_jsonl (alert_emitter.py:89). The rsi_events event
keys are rsi_events.py:82-98 (t, event, level_value, tolerance_used, penetration [, direction]). No test touches
MyTradingSys/runtime/alerts."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from MyTradingSys.backtest.layers.rsi import observation
from MyTradingSys.backtest.layers.rsi.observation import read_latest

TFS = ["1m", "3m", "5m", "15m", "1h", "4h", "1d"]
INNER = ["rsi", "ma_sma", "ma_ema", "support_or_reject", "level", "t_close", "t_confirm"]
ALL_NONE = {k: None for k in INNER}

M15 = 900000
T0 = 1790000000000


def rsi_alert(tf="15m", t_close=T0, event="support", rsi=41.2, rsi_ma=44.8, level_value=40.0, confirm_lag=0, **extra):
    """An alert of layer rsi / sub rsi_events as the live runner writes it."""
    rec = {"layer": "rsi", "sub": "rsi_events", "tf": tf, "params_id": "rsi_40_tol0.5_L1_2026-09-29",
           "rsi": rsi, "rsi_ma": rsi_ma, "t_close": t_close, "t_confirm": t_close + confirm_lag,
           "event": event, "level_value": level_value, "tolerance_used": 0.5, "penetration": 0.3}
    rec.update(extra)
    return rec


def other_alert(layer="fabio", sub="cvd_absorption", tf="15m", t_close=T0 + M15, **extra):
    """Another layer's alert in the same <tf>.jsonl: it carries rsi/rsi_ma too (format_alert adds them to every alert)."""
    rec = {"layer": layer, "sub": sub, "tf": tf, "params_id": "x", "rsi": 99.0, "rsi_ma": 98.0, "t_close": t_close,
           "t_confirm": t_close, "event": "something", "side": "long"}
    rec.update(extra)
    return rec


def jl(*recs):
    return "".join(json.dumps(r, sort_keys=True) + "\n" for r in recs)


class ObsBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.d = Path(self._tmp.name)

    def put(self, tf, text, binary=False):
        p = self.d / (tf + ".jsonl")
        if binary:
            p.write_bytes(text)
        else:
            p.write_text(text, encoding="utf-8", newline="\n")
        return p

    def read(self, **kw):
        return read_latest(alerts_dir=self.d, **kw)


class TestShapeAndSources(ObsBase):
    def test_all_seven_tfs_all_inner_keys_in_order(self):
        got = self.read()
        self.assertEqual(list(got), TFS)
        for tf in TFS:
            self.assertEqual(list(got[tf]), INNER)

    def test_empty_dir_everything_none(self):
        got = self.read()
        for tf in TFS:
            self.assertEqual(got[tf], ALL_NONE)

    def test_latest_record_per_tf_and_field_mapping(self):
        self.put("15m", jl(rsi_alert("15m", T0, "support", 41.2, 44.8),
                           rsi_alert("15m", T0 + 2 * M15, "failure", 38.5, 43.25, confirm_lag=M15)))
        self.put("1h", jl(rsi_alert("1h", T0 + 3600000, "cross", 52.0, 48.0, level_value=40.0, direction="up")))
        got = self.read()
        self.assertEqual(got["15m"], {"rsi": 38.5, "ma_sma": 43.25, "ma_ema": None, "support_or_reject": "failure",
                                      "level": 40.0, "t_close": T0 + 2 * M15, "t_confirm": T0 + 3 * M15})
        self.assertEqual(got["1h"], {"rsi": 52.0, "ma_sma": 48.0, "ma_ema": None, "support_or_reject": "cross",
                                     "level": 40.0, "t_close": T0 + 3600000, "t_confirm": T0 + 3600000})
        # tfs without a file stay all None
        for tf in ("1m", "3m", "5m", "4h", "1d"):
            self.assertEqual(got[tf], ALL_NONE)

    def test_latest_means_last_line_of_the_file_not_largest_t_close(self):
        self.put("5m", jl(rsi_alert("5m", T0 + 10, "support", 40.1, 41.0), rsi_alert("5m", T0, "rejection", 60.5, 55.5)))
        self.assertEqual(self.read()["5m"]["t_close"], T0)
        self.assertEqual(self.read()["5m"]["support_or_reject"], "rejection")

    def test_ma_ema_is_always_none_even_if_the_record_carries_an_ema_looking_key(self):
        self.put("15m", jl(rsi_alert("15m", rsi_ma=44.8, rsi_ma_ema=12.0, ma_ema=13.0)))
        got = self.read()["15m"]
        self.assertIsNone(got["ma_ema"])
        self.assertEqual(got["ma_sma"], 44.8)

    def test_record_without_rsi_ma_and_level_keeps_those_none(self):
        rec = rsi_alert("15m")
        del rec["rsi_ma"], rec["level_value"], rec["t_confirm"]
        self.put("15m", jl(rec))
        self.assertEqual(self.read()["15m"], {"rsi": 41.2, "ma_sma": None, "ma_ema": None, "support_or_reject": "support",
                                              "level": None, "t_close": T0, "t_confirm": None})


class TestSkippedRecords(ObsBase):
    def test_other_layers_last_line_is_skipped_for_the_newest_rsi_events_line(self):
        self.put("15m", jl(rsi_alert("15m", T0, "support", 41.2, 44.8), other_alert("fabio", "cvd_absorption", "15m"),
                           other_alert("cryptocred", "sr_flip", "15m")))
        got = self.read()["15m"]
        self.assertEqual(got["rsi"], 41.2)              # not the 99.0 of the fabio / cryptocred lines
        self.assertEqual(got["ma_sma"], 44.8)
        self.assertEqual(got["t_close"], T0)

    def test_only_other_layers_in_file_means_all_none(self):
        self.put("1m", jl(other_alert("turn_of_candle", "turn_of_candle", "1m")))      # live_runner_cli.py:185
        self.assertEqual(self.read()["1m"], ALL_NONE)

    def test_rsi_layer_but_other_sub_is_not_a_source(self):
        # malkan_bull / malkan_bear (live_runner_cli.py:180-181) are layer "rsi" with a different sub and event names
        self.put("1h", jl(rsi_alert("1h", T0, "support", 42.0, 45.0),
                          {**rsi_alert("1h", T0 + 3600000, "malkan_support", 40.2, 46.0), "sub": "malkan_bull"}))
        got = self.read()["1h"]
        self.assertEqual(got["support_or_reject"], "support")
        self.assertEqual(got["t_close"], T0)

    def test_record_whose_tf_differs_from_its_file_is_skipped(self):
        self.put("15m", jl(rsi_alert("15m", T0, "support", 41.2, 44.8), rsi_alert("1h", T0 + 5, "cross", 70.0, 60.0)))
        self.assertEqual(self.read()["15m"]["t_close"], T0)

    def test_garbled_last_line_falls_back_to_previous_valid_rsi_record(self):
        good = jl(rsi_alert("15m", T0, "support", 41.2, 44.8))
        self.put("15m", good + '{"layer": "rsi", "sub": "rsi_events", "tf": "15m", "rsi": 4')   # cut mid-write
        got = self.read()["15m"]
        self.assertEqual((got["rsi"], got["support_or_reject"], got["t_close"]), (41.2, "support", T0))

    def test_garbled_only_line_means_all_none(self):
        self.put("15m", '{"layer": "rsi", "sub": "rsi_ev')
        self.assertEqual(self.read()["15m"], ALL_NONE)

    def test_non_object_json_empty_and_binary_lines_are_skipped(self):
        good = jl(rsi_alert("15m", T0, "rejection", 61.0, 55.0))
        junk = b'\n\n[1, 2]\nnull\n123\n"str"\n\xff\xfe\x00garbage\n   \n'
        self.put("15m", good.encode("utf-8") + junk, binary=True)
        got = self.read()["15m"]
        self.assertEqual((got["rsi"], got["support_or_reject"]), (61.0, "rejection"))

    def test_valid_last_line_without_trailing_newline_is_accepted(self):
        self.put("5m", jl(rsi_alert("5m", T0, "support", 41.2, 44.8)).rstrip("\n"))
        self.assertEqual(self.read()["5m"]["t_close"], T0)

    def test_non_finite_and_wrong_typed_values_become_none(self):
        raw = ('{"layer":"rsi","sub":"rsi_events","tf":"15m","rsi":NaN,"rsi_ma":"44.8","t_close":true,'
               '"t_confirm":1.5,"event":7,"level_value":Infinity}\n')
        self.put("15m", raw)
        self.assertEqual(self.read()["15m"], ALL_NONE)

    def test_integral_float_timestamp_is_accepted_as_int(self):
        raw = '{"layer":"rsi","sub":"rsi_events","tf":"15m","rsi":50,"t_close":1790000000000.0,"event":"cross"}\n'
        self.put("15m", raw)
        got = self.read()["15m"]
        self.assertEqual(got["t_close"], 1790000000000)
        self.assertIsInstance(got["t_close"], int)
        self.assertEqual(got["rsi"], 50)


class TestNeverRaisesAndReadOnly(ObsBase):
    def test_missing_dir_is_all_none_and_not_created(self):
        gone = self.d / "nope"
        got = read_latest(alerts_dir=gone)
        self.assertEqual(list(got), TFS)
        self.assertTrue(all(got[tf] == ALL_NONE for tf in TFS))
        self.assertFalse(gone.exists())

    def test_alerts_dir_is_a_regular_file(self):
        f = self.d / "afile"
        f.write_bytes(b"x")
        got = read_latest(alerts_dir=f)
        self.assertTrue(all(got[tf] == ALL_NONE for tf in TFS))
        self.assertEqual(f.read_bytes(), b"x")

    def test_tf_file_is_a_directory(self):
        (self.d / "15m.jsonl").mkdir()
        self.put("1h", jl(rsi_alert("1h", T0, "support", 41.0, 44.0)))
        got = self.read()
        self.assertEqual(got["15m"], ALL_NONE)
        self.assertEqual(got["1h"]["rsi"], 41.0)          # the other tf is unaffected

    def test_empty_file(self):
        self.put("15m", "")
        self.assertEqual(self.read()["15m"], ALL_NONE)

    def test_str_path_is_accepted(self):
        self.put("15m", jl(rsi_alert("15m")))
        self.assertEqual(read_latest(alerts_dir=str(self.d))["15m"]["rsi"], 41.2)

    def test_files_and_directory_are_not_modified(self):
        self.put("15m", jl(rsi_alert("15m", T0), other_alert()) + '{"garbled')
        self.put("1h", jl(rsi_alert("1h", T0)))
        (self.d / "sub").mkdir()

        def snap():
            out = {}
            for p in sorted(self.d.rglob("*")):
                out[str(p.relative_to(self.d))] = (hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "dir",
                                                   p.stat().st_mtime_ns if p.is_file() else 0)
            return out

        before = snap()
        for _ in range(3):
            self.read()
        self.assertEqual(snap(), before)

    def test_result_dicts_are_fresh_per_call(self):
        a = self.read()
        a["15m"]["rsi"] = 1.0
        self.assertIsNone(self.read()["15m"]["rsi"])


class TestTailReading(ObsBase):
    def test_finds_old_rsi_record_below_a_large_body_of_other_layer_lines(self):
        body = jl(*[other_alert(t_close=T0 + i) for i in range(3000)])      # ~0.5 MB, > 64 KiB chunk
        self.assertGreater(len(body), 3 * observation._CHUNK)
        self.put("15m", jl(rsi_alert("15m", T0, "support", 41.2, 44.8)) + body)
        got = self.read()["15m"]
        self.assertEqual((got["rsi"], got["t_close"]), (41.2, T0))

    def test_scan_limit_stops_the_search_and_means_all_none(self):
        body = jl(*[other_alert(t_close=T0 + i) for i in range(3000)])
        self.put("15m", jl(rsi_alert("15m", T0, "support", 41.2, 44.8)) + body)
        self.assertEqual(self.read(max_scan_bytes=1000)["15m"], ALL_NONE)         # stated rule: a match beyond the limit is not found
        self.assertEqual(self.read(max_scan_bytes=0)["15m"], ALL_NONE)

    def test_record_just_inside_a_scan_limit_is_found_and_just_outside_is_not(self):
        rec = jl(rsi_alert("15m", T0, "support", 41.2, 44.8))
        tail = jl(other_alert(t_close=T0 + 1))
        self.put("15m", rec + tail)
        n = len(rec) + len(tail)
        self.assertEqual(self.read(max_scan_bytes=n)["15m"]["t_close"], T0)       # whole file scanned
        self.assertEqual(self.read(max_scan_bytes=n - 1)["15m"], ALL_NONE)        # first line is cut by the limit: dropped

    def test_chunk_boundaries_never_lose_or_split_the_record(self):
        # shrink the chunk so a short file crosses many boundaries; slide the record across every alignment
        for chunk in (1, 2, 3, 7, 16, 64):
            with mock.patch.object(observation, "_CHUNK", chunk):
                for pad in range(0, 2 * 130, 3):
                    text = ("filler-line\n" * 3 + jl(rsi_alert("15m", T0, "support", 41.2, 44.8)) +
                            "".join(json.dumps(other_alert(t_close=T0 + 1 + i)) + "\n" for i in range(pad % 5)) +
                            "x" * (pad % 40))
                    self.put("15m", text)
                    got = self.read()["15m"]
                    self.assertEqual(got["t_close"], T0, (chunk, pad))

    def test_multibyte_characters_split_across_chunks(self):
        rec = rsi_alert("15m", T0, "support", 41.2, 44.8, params_id="rsi_éü€_\U0001F600")
        text = "é€\n" + json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n" + "ü€\n"
        for chunk in (1, 2, 3, 5):
            with mock.patch.object(observation, "_CHUNK", chunk):
                self.put("15m", text)
                self.assertEqual(self.read()["15m"]["rsi"], 41.2, chunk)

    def test_first_line_of_file_is_reachable(self):
        self.put("5m", jl(rsi_alert("5m", T0, "rejection", 61.0, 55.0)))
        with mock.patch.object(observation, "_CHUNK", 5):
            self.assertEqual(self.read()["5m"]["support_or_reject"], "rejection")


class TestRealProducerShape(ObsBase):
    """Contract check against the REAL producer chain (live_layers.rsi_level_layer -> live_runner_core.run_registry ->
    alert_emitter.format_alert -> append_alerts_jsonl), so the hand-written alert shape above cannot drift from it."""

    def test_real_alert_written_by_the_runner_chain_is_read_back(self):
        import random
        from MyTradingSys.backtest.layers.alerts import live_layers as ll
        from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl
        from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry, empty_state, run_registry

        rng = random.Random(7)                       # deterministic random walk of 15m closes
        closes = [100.0]
        for _ in range(400):
            closes.append(closes[-1] + rng.uniform(-1, 1))
        bars = [{"t": T0 + i * M15, "o": c, "h": c + 0.5, "l": c - 0.5, "c": c, "v": 1.0, "tbv": 0.5}
                for i, c in enumerate(closes)]
        reg = build_registry([{"layer": "rsi", "sub": "rsi_events", "tf": "15m", "fn": ll.rsi_level_layer,
                               "params_id": "rsi_40_tol0.5_L1_2026-09-29"}])
        alerts = []
        for n in range(30, len(bars)):               # first prefix of the series on which the runner emits an alert
            alerts = run_registry(reg, {"15m": bars[:n]}, empty_state())["alerts"]
            if alerts:
                break
        self.assertEqual(len(alerts), 1)
        a = alerts[0]
        self.assertIsNotNone(a["rsi"])
        self.assertIsNotNone(a["rsi_ma"])
        append_alerts_jsonl(alerts, self.d / "15m.jsonl")

        got = self.read()["15m"]
        self.assertEqual(got["rsi"], a["rsi"])
        self.assertEqual(got["ma_sma"], a["rsi_ma"])
        self.assertIsNone(got["ma_ema"])
        self.assertEqual(got["support_or_reject"], a["event"])
        self.assertIn(a["event"], ("support", "rejection", "failure", "cross"))     # rsi_events.py:70,78,93
        self.assertEqual(got["level"], 40.0)                                       # live_layers.py:142 RSI_LEVEL
        self.assertEqual(got["t_close"], a["t_close"])
        self.assertEqual(got["t_confirm"], a["t_confirm"])
        self.assertEqual(got["t_confirm"], bars[n - 1]["t"])                       # latest closed bar when first seen
        for tf in ("1m", "3m", "5m", "1h", "4h", "1d"):
            self.assertEqual(self.read()[tf], ALL_NONE)


class TestBoundary(unittest.TestCase):
    def test_module_imports_only_stdlib(self):
        import ast
        tree = ast.parse(Path(observation.__file__).read_text(encoding="utf-8"))
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        self.assertEqual(mods, {"json", "math", "os", "contextlib", "pathlib"})

    def test_default_alerts_dir_is_the_runtime_alerts_dir(self):
        repo = Path(__file__).resolve().parents[4]
        self.assertEqual(observation.DEFAULT_ALERTS_DIR, repo / "MyTradingSys" / "runtime" / "alerts")


if __name__ == "__main__":
    unittest.main()
