"""Tests for consensus/writer.py. Expected values are hand-derived from research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md
(row fields :33-41, append-only :42, acceptance :80-81, :82-83), not copied from the code under test.
Every test writes only under a temp dir (base_dir=...); none touches <repo>/Dumps."""
import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.consensus import writer
from MyTradingSys.backtest.layers.consensus.writer import append_row, consensus_path

UTC = timezone.utc
T1 = datetime(2026, 10, 1, 19, 30, 15, 123456, tzinfo=UTC)      # file consensus_20261001.jsonl, ts ...15.123Z
SIX = ["1m", "3m", "15m", "1h", "4h", "1d"]

SNAP = {"snapshot_id": "S-0001", "current_price": 67123.5, "daily_vp": {"poc": 67000.0}}
TOM = {"alert_no": 17, "verdict": "SETUP_CONFIRMED", "zone_tf": "15m", "time": "19:29", "setup": "pullback_long",
       "side": "long", "entry": 67000.0, "stop": 66800.0, "target": 67500.0, "net_rr": 2.4}
FABIO = {"verdict": "ENTRY", "model": "A", "side": "short", "entry": 67200.0, "stop": 67300.0, "target": 66900.0}
RSI = {"1m": None, "3m": None, "5m": {"rsi": 44.0, "ma_sma": 47.5, "ma_ema": None, "support_or_reject": "support",
                                       "level": 40.0, "t_close": 1790000000000},
       "15m": {"rsi": 51.0, "ma_sma": 49.0, "ma_ema": None, "support_or_reject": None, "level": None, "t_close": None},
       "1h": None, "4h": None, "1d": None}


def lines_of(path):
    with open(path, "rb") as fh:
        data = fh.read()
    return data, [l for l in data.split(b"\n") if l]


class WriterTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.out = self.root / "consensus_out"          # does not exist yet: the writer must create it
        self.f1 = self.out / "consensus_20261001.jsonl"

    def call(self, snap=SNAP, tom=TOM, fabio=FABIO, rsi=RSI, now=T1, **kw):
        return append_row(snap, tom, fabio, rsi, base_dir=self.out, now=now, **kw)

    def row(self, index=-1):
        _, ls = lines_of(self.f1)
        return json.loads(ls[index])


class TestRowShape(WriterTestBase):
    def test_n_calls_write_n_lines_each_valid_json(self):                 # ARCHITECTURE:80-81
        n = 7
        for i in range(n):
            self.assertIs(self.call(now=T1 + timedelta(seconds=i)), True)
        data, ls = lines_of(self.f1)
        self.assertEqual(len(ls), n)
        self.assertEqual(data.count(b"\n"), n)           # every row ends with exactly one LF
        self.assertTrue(data.endswith(b"\n"))
        self.assertNotIn(b"\r", data)                    # LF only
        for l in ls:
            self.assertIsInstance(json.loads(l), dict)

    def test_row_fields_and_order_exactly_per_architecture(self):         # ARCHITECTURE:33-41
        self.call()
        r = self.row()
        self.assertEqual(list(r), ["snapshot_id", "utc_timestamp", "price", "tom", "fabio", "rsi", "notes"])
        self.assertEqual(list(r["tom"]), ["verdict", "setup", "side", "entry", "stop", "target", "net_rr"])
        self.assertEqual(list(r["fabio"]), ["verdict", "model", "side", "entry", "stop", "target"])

    def test_values(self):
        self.call()
        r = self.row()
        self.assertEqual(r["snapshot_id"], "S-0001")
        self.assertEqual(r["utc_timestamp"], "2026-10-01T19:30:15.123Z")
        self.assertEqual(r["price"], 67123.5)
        self.assertEqual(r["tom"], {"verdict": "SETUP_CONFIRMED", "setup": "pullback_long", "side": "long",
                                    "entry": 67000.0, "stop": 66800.0, "target": 67500.0, "net_rr": 2.4})
        self.assertEqual(r["fabio"], FABIO)
        self.assertIsNone(r["notes"])
        # tom extras (alert_no, zone_tf, time) are not part of the documented row
        for extra in ("alert_no", "zone_tf", "time"):
            self.assertNotIn(extra, r["tom"])

    def test_tom_missing_keys_become_null(self):
        self.call(tom={"verdict": "WAIT_ZONE"})
        self.assertEqual(self.row()["tom"], {"verdict": "WAIT_ZONE", "setup": None, "side": None, "entry": None,
                                             "stop": None, "target": None, "net_rr": None})

    def test_tom_none_writes_null_block_fabio_still_written(self):
        self.assertTrue(self.call(tom=None))
        r = self.row()
        self.assertIsNone(r["tom"])
        self.assertEqual(r["fabio"], FABIO)

    def test_fabio_none_writes_null_block(self):
        self.assertTrue(self.call(fabio=None))
        r = self.row()
        self.assertIsNone(r["fabio"])
        self.assertEqual(r["tom"]["verdict"], "SETUP_CONFIRMED")

    def test_both_cores_none_still_writes_a_row_with_six_rsi_keys(self):
        self.assertTrue(self.call(tom=None, fabio=None))
        r = self.row()
        self.assertIsNone(r["tom"])
        self.assertIsNone(r["fabio"])
        self.assertEqual(list(r["rsi"])[:6], SIX)

    def test_non_mapping_core_block_is_null_not_an_error(self):
        with self.assertLogs(writer._LOG, level="WARNING"):
            self.assertTrue(self.call(tom=["not", "a", "dict"]))
        self.assertIsNone(self.row()["tom"])

    def test_non_ascii_notes_round_trip(self):
        self.assertTrue(self.call(notes="café → ok"))
        self.assertEqual(self.row()["notes"], "café → ok")      # SNAP has a snapshot_id: no auto note


class TestRsiBlock(WriterTestBase):
    def test_six_tf_keys_present_in_order_and_extra_5m_carried_unchanged(self):   # ARCHITECTURE:82-83
        self.call()
        r = self.row()
        self.assertEqual(list(r["rsi"]), ["1m", "3m", "15m", "1h", "4h", "1d", "5m"])
        self.assertEqual(r["rsi"]["5m"], RSI["5m"])
        self.assertEqual(r["rsi"]["15m"], RSI["15m"])
        for tf in ("1m", "3m", "1h", "4h", "1d"):
            self.assertIsNone(r["rsi"][tf])

    def test_missing_tf_keys_are_written_as_null(self):
        self.call(rsi={"1h": {"rsi": 55.5}})
        r = self.row()
        self.assertEqual(list(r["rsi"]), SIX)
        self.assertEqual(r["rsi"]["1h"], {"rsi": 55.5})
        self.assertEqual([r["rsi"][k] for k in SIX if k != "1h"], [None] * 5)

    def test_rsi_none_writes_six_null_keys(self):
        self.call(rsi=None)
        self.assertEqual(self.row()["rsi"], {k: None for k in SIX})

    def test_rsi_empty_dict_writes_six_null_keys(self):
        self.call(rsi={})
        self.assertEqual(self.row()["rsi"], {k: None for k in SIX})

    def test_non_mapping_rsi_writes_six_nulls(self):
        with self.assertLogs(writer._LOG, level="WARNING"):
            self.assertTrue(self.call(rsi="oops"))
        self.assertEqual(self.row()["rsi"], {k: None for k in SIX})


class TestSnapshotFields(WriterTestBase):
    def test_snapshot_id_absent_gives_null_and_note(self):
        self.call(snap={"current_price": 100.0})
        r = self.row()
        self.assertIsNone(r["snapshot_id"])
        self.assertEqual(r["notes"], "snapshot_id absent in input")

    def test_snapshot_id_absent_note_is_appended_to_caller_notes(self):
        self.call(snap={"current_price": 100.0}, notes="tom alert #17")
        self.assertEqual(self.row()["notes"], "tom alert #17; snapshot_id absent in input")

    def test_snapshot_id_present_is_taken_verbatim_no_auto_note(self):
        self.call(snap={"snapshot_id": "abc", "current_price": 1.0}, notes="x")
        r = self.row()
        self.assertEqual(r["snapshot_id"], "abc")
        self.assertEqual(r["notes"], "x")

    def test_price_prefers_current_price_then_price_then_null(self):
        self.call(snap={"snapshot_id": "a", "current_price": 10.5, "price": 99.0})
        self.call(snap={"snapshot_id": "b", "price": 99.0})
        self.call(snap={"snapshot_id": "c", "current_price": None, "price": 98.0})
        self.call(snap={"snapshot_id": "d"})
        _, ls = lines_of(self.f1)
        self.assertEqual([json.loads(l)["price"] for l in ls], [10.5, 99.0, 98.0, None])

    def test_none_snapshot_gives_null_id_and_price(self):
        self.assertTrue(self.call(snap=None))
        r = self.row()
        self.assertIsNone(r["snapshot_id"])
        self.assertIsNone(r["price"])
        self.assertEqual(r["notes"], "snapshot_id absent in input")


class TestPathAndTime(WriterTestBase):
    def test_utc_date_rollover_writes_two_files(self):
        before = datetime(2026, 10, 1, 23, 59, 59, 999000, tzinfo=UTC)
        after = datetime(2026, 10, 2, 0, 0, 0, 0, tzinfo=UTC)
        self.call(now=before)
        self.call(now=before)
        self.call(now=after)
        f2 = self.out / "consensus_20261002.jsonl"
        self.assertEqual(sorted(p.name for p in self.out.iterdir()),
                         ["consensus_20261001.jsonl", "consensus_20261002.jsonl"])
        self.assertEqual(len(lines_of(self.f1)[1]), 2)
        self.assertEqual(len(lines_of(f2)[1]), 1)
        self.assertEqual(json.loads(lines_of(self.f1)[1][0])["utc_timestamp"], "2026-10-01T23:59:59.999Z")
        self.assertEqual(json.loads(lines_of(f2)[1][0])["utc_timestamp"], "2026-10-02T00:00:00.000Z")

    def test_aware_non_utc_is_converted_naive_is_taken_as_utc(self):
        plus2 = timezone(timedelta(hours=2))
        self.call(now=datetime(2026, 10, 2, 1, 30, 0, tzinfo=plus2))     # = 2026-10-01 23:30 UTC
        self.call(now=datetime(2026, 10, 1, 5, 6, 7))                    # naive -> UTC
        _, ls = lines_of(self.f1)
        self.assertEqual([json.loads(l)["utc_timestamp"] for l in ls],
                         ["2026-10-01T23:30:00.000Z", "2026-10-01T05:06:07.000Z"])
        self.assertEqual(os.listdir(self.out), ["consensus_20261001.jsonl"])

    def test_default_directory_is_repo_root_dumps_consensus(self):
        repo = Path(__file__).resolve().parents[4]
        self.assertEqual(writer.DEFAULT_DIR, repo / "Dumps" / "consensus")
        self.assertEqual(consensus_path(T1), repo / "Dumps" / "consensus" / "consensus_20261001.jsonl")
        self.assertEqual(consensus_path(T1, self.out), self.f1)

    def test_default_dir_is_gitignored(self):
        gi = (Path(__file__).resolve().parents[4] / ".gitignore")
        if not gi.exists():
            self.skipTest("no .gitignore in this tree")
        text = gi.read_text(encoding="utf-8").splitlines()
        self.assertIn("Dumps/*", text)                    # Dumps/consensus falls under it
        self.assertNotIn("!Dumps/consensus", text)


class TestNeverRaises(WriterTestBase):
    def test_io_error_base_dir_is_a_regular_file(self):
        blocker = self.root / "iam_a_file"
        blocker.write_bytes(b"keep me")
        with self.assertLogs(writer._LOG, level="WARNING"):
            res = append_row(SNAP, TOM, FABIO, RSI, base_dir=blocker, now=T1)
        self.assertIs(res, False)
        self.assertEqual(blocker.read_bytes(), b"keep me")

    def test_io_error_base_dir_below_a_regular_file(self):
        blocker = self.root / "iam_a_file"
        blocker.write_bytes(b"keep me")
        with self.assertLogs(writer._LOG, level="WARNING"):
            res = append_row(SNAP, TOM, FABIO, RSI, base_dir=blocker / "sub", now=T1)
        self.assertIs(res, False)
        self.assertEqual(blocker.read_bytes(), b"keep me")

    def test_io_error_target_file_is_a_directory(self):
        self.f1.mkdir(parents=True)                       # consensus_20261001.jsonl exists as a directory
        with self.assertLogs(writer._LOG, level="WARNING"):
            self.assertIs(self.call(), False)
        self.assertTrue(self.f1.is_dir())

    def test_serialization_error_returns_false_and_writes_nothing(self):
        with self.assertLogs(writer._LOG, level="WARNING"):
            res = self.call(tom={"verdict": {"a", "set"}})   # a set is not JSON serializable
        self.assertIs(res, False)
        self.assertFalse(self.out.exists())                  # nothing created: serialization happens first

    def test_nan_price_is_refused_so_every_line_stays_valid_json(self):
        self.call()
        before, _ = lines_of(self.f1)
        with self.assertLogs(writer._LOG, level="WARNING"):
            res = self.call(snap={"snapshot_id": "n", "current_price": float("nan")})
        self.assertIs(res, False)
        self.assertEqual(lines_of(self.f1)[0], before)

    def test_bad_now_returns_false(self):
        with self.assertLogs(writer._LOG, level="WARNING"):
            self.assertIs(self.call(now="2026-10-01"), False)

    def test_failure_is_logged_not_printed_to_stdout(self):
        blocker = self.root / "f"
        blocker.write_bytes(b"x")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertLogs(writer._LOG, level="WARNING") as cm:
            append_row(SNAP, TOM, FABIO, RSI, base_dir=blocker, now=T1)
        self.assertEqual(buf.getvalue(), "")
        self.assertEqual(len(cm.records), 1)
        self.assertIn("row not written", cm.output[0])

    def test_success_prints_nothing(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertTrue(self.call())
        self.assertEqual(buf.getvalue(), "")


class TestNoMutationAndAppendOnly(WriterTestBase):
    def test_inputs_are_not_modified(self):
        snap, tom, fabio, rsi = (copy.deepcopy(x) for x in (SNAP, TOM, FABIO, RSI))
        snap0, tom0, fabio0, rsi0 = (copy.deepcopy(x) for x in (snap, tom, fabio, rsi))
        self.assertTrue(append_row(snap, tom, fabio, rsi, notes="n", base_dir=self.out, now=T1))
        self.assertEqual((snap, tom, fabio, rsi), (snap0, tom0, fabio0, rsi0))
        # also with the "absent" shapes
        snap2, rsi2 = {"current_price": 1.0}, {"1h": {"rsi": 1.0}}
        snap20, rsi20 = copy.deepcopy(snap2), copy.deepcopy(rsi2)
        self.assertTrue(append_row(snap2, None, None, rsi2, base_dir=self.out, now=T1))
        self.assertEqual((snap2, rsi2), (snap20, rsi20))

    def test_existing_lines_are_byte_identical_after_more_appends(self):
        for i in range(3):
            self.call(now=T1 + timedelta(seconds=i))
        before, ls_before = lines_of(self.f1)
        self.assertEqual(len(ls_before), 3)
        for i in range(2):
            self.call(now=T1 + timedelta(minutes=1, seconds=i))
        after, ls_after = lines_of(self.f1)
        self.assertEqual(len(ls_after), 5)
        self.assertEqual(after[:len(before)], before)         # old bytes untouched
        self.assertEqual(ls_after[:3], ls_before)

    def test_foreign_existing_content_is_never_rewritten(self):
        self.out.mkdir(parents=True)
        self.f1.write_bytes(b'{"pre":"existing"}\n')
        self.call()
        data, ls = lines_of(self.f1)
        self.assertTrue(data.startswith(b'{"pre":"existing"}\n'))
        self.assertEqual(len(ls), 2)

    def test_a_failed_append_leaves_the_file_unchanged(self):
        self.call()
        before = lines_of(self.f1)[0]
        with self.assertLogs(writer._LOG, level="WARNING"):
            self.assertIs(self.call(tom={"verdict": object()}), False)
        self.assertEqual(lines_of(self.f1)[0], before)

    def test_no_write_outside_base_dir(self):
        cwd_dir = self.root / "cwd"
        cwd_dir.mkdir()
        (self.root / "bystander.txt").write_bytes(b"b")

        def tree():
            return sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))

        old = os.getcwd()
        os.chdir(cwd_dir)
        try:
            for i in range(3):
                self.call(now=T1 + timedelta(days=i))
        finally:
            os.chdir(old)
        self.assertEqual(tree(), sorted([
            "bystander.txt", "cwd", "consensus_out",
            "consensus_out/consensus_20261001.jsonl", "consensus_out/consensus_20261002.jsonl",
            "consensus_out/consensus_20261003.jsonl"]))
        self.assertEqual(os.listdir(cwd_dir), [])             # the cwd was not used
        self.assertEqual((self.root / "bystander.txt").read_bytes(), b"b")


class TestDoesNotImportExecution(unittest.TestCase):
    def test_writer_source_imports_only_stdlib(self):
        import ast
        src = Path(writer.__file__).read_text(encoding="utf-8")
        mods = set()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        self.assertEqual(mods, {"json", "logging", "collections", "datetime", "pathlib"})


if __name__ == "__main__":
    unittest.main()
