"""shot.py: pasted images are saved once whatever route they took, nothing leaves 'new' without a classification, a chart
is not 'read' without claim rows, and nothing is 'done' without an outcome that exists. Spec: methodology/screenshot_intake.md."""
import base64
import contextlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shot

SID = "11111111-aaaa-bbbb-cccc-222222222222"


def png(seed, w=1920, h=1040):
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h) + seed.encode() * 4


def paste_rec(data, text, sid=SID, ts="2026-10-09T00:40:40.678Z"):
    return {"type": "user", "sessionId": sid, "timestamp": ts, "imagePasteIds": [1],
            "message": {"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(data).decode()}},
                {"type": "text", "text": text}]}}


def tool_rec(data):
    return {"type": "user", "sessionId": SID, "timestamp": "2026-10-09T00:41:00.000Z",
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(data).decode()}}]}]}}


class FakeStdin:
    def __init__(self, text):
        self.buffer = io.BytesIO(text.encode("utf-8"))

    def isatty(self):
        return False


class ShotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.store = self.tmp / "store"
        self.home = self.tmp / "claude"
        self.temp = self.tmp / "temp"
        self.proj = self.home / "projects" / "SLUG"
        self.proj.mkdir(parents=True)
        self.t = self.proj / f"{SID}.jsonl"
        env = {"MTS_SHOT_DIR": str(self.store), "MTS_CLAUDE_HOME": str(self.home), "MTS_SHOT_TEMP": str(self.temp),
               "MTS_SHOT_SLUGS": "SLUG"}
        p = mock.patch.dict(os.environ, env)
        p.start()
        self.addCleanup(p.stop)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_transcript(self, *recs, partial=None):
        text = "".join(json.dumps(r) + "\n" for r in recs) + (partial or "")
        self.t.write_text(text, encoding="utf-8", newline="\n")

    def state(self):
        return shot.fold(shot.load_events(self.store))

    def run_main(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if stdin is not None:
                with mock.patch("sys.stdin", FakeStdin(stdin)):
                    rc = shot.main(list(argv))
            else:
                rc = shot.main(list(argv))
        return rc, out.getvalue(), err.getvalue()

    # ------------------------------------------------------------ landing
    def test_paste_lands_with_operator_words_and_tool_screenshots_do_not(self):
        a, b = png("a"), png("b")
        self.write_transcript(paste_rec(a, "5 min chart for you - look carefully"), tool_rec(b))
        new = shot.ingest_all(self.store)
        self.assertEqual(len(new), 1)
        s = self.state()[new[0]["id"]]
        self.assertEqual((s["route"], s["status"], s["w"], s["h"]), ("paste", "new", 1920, 1040))
        self.assertIn("look carefully", s["operator_text"])
        self.assertTrue((self.store / "img" / f"{s['id']}.png").read_bytes() == a)

    def test_same_bytes_via_paste_upload_and_temp_are_one_shot(self):
        a = png("a")
        self.write_transcript(paste_rec(a, "x"))
        (self.home / "uploads" / SID).mkdir(parents=True)
        (self.home / "uploads" / SID / "h-image.png").write_bytes(a)
        (self.temp / "SLUG" / SID / "images").mkdir(parents=True)
        (self.temp / "SLUG" / SID / "images" / "1.png").write_bytes(a)
        self.assertEqual(len(shot.ingest_all(self.store)), 1)
        self.assertEqual(len(self.state()), 1)

    def test_landing_the_same_bytes_twice_is_one_shot_even_after_a_cursor_reset(self):
        a = png("a")
        self.assertIsNotNone(shot.land(self.store, a, "paste", SID, "t", "x"))
        self.assertIsNone(shot.land(self.store, a, "upload", SID, "t", "y"))
        self.write_transcript(paste_rec(a, "again"))
        self.assertEqual(shot.ingest_all(self.store), [])  # same pixels, already landed
        (self.store / "cursors.json").unlink()
        self.assertEqual(shot.ingest_all(self.store), [])  # transcript re-read from byte 0 lands nothing new
        self.assertEqual(len(self.state()), 1)
        self.assertEqual(len(shot.load_events(self.store)), 1)

    def test_ingest_is_idempotent_and_survives_temp_cleanup(self):
        a = png("a")
        d = self.temp / "SLUG" / SID / "images"
        d.mkdir(parents=True)
        (d / "1.png").write_bytes(a)
        first = shot.ingest_all(self.store)
        (d / "1.png").unlink()
        self.assertEqual(shot.ingest_all(self.store), [])
        self.assertTrue((self.store / "img" / f"{first[0]['id']}.png").exists())

    def test_half_written_last_line_is_left_for_the_next_run(self):
        a = png("a")
        line = json.dumps(paste_rec(a, "late"))
        self.write_transcript(partial=line[:60])
        self.assertEqual(shot.ingest_all(self.store), [])
        self.write_transcript(partial=line + "\n")
        self.assertEqual(len(shot.ingest_all(self.store)), 1)

    def test_non_images_and_foreign_sessions_are_ignored(self):
        (self.home / "uploads" / SID).mkdir(parents=True)
        (self.home / "uploads" / SID / "notes.png").write_bytes(b"not an image at all")
        other = self.home / "uploads" / "99999999-other-project"
        other.mkdir(parents=True)
        (other / "x-image.png").write_bytes(png("z"))
        self.write_transcript(paste_rec(png("a"), "x"))
        new = shot.ingest_all(self.store)
        self.assertEqual([e["route"] for e in new], ["paste"])

    def test_inbox_folder_lands_images_the_operator_drops(self):
        (self.store / "inbox").mkdir(parents=True)
        (self.store / "inbox" / "snip.png").write_bytes(png("q"))
        new = shot.ingest_all(self.store)
        self.assertEqual([e["route"] for e in new], ["inbox"])

    # ------------------------------------------------------------ classify
    def landed(self, seed="a", text="look"):
        return shot.land(self.store, png(seed), "paste", SID, "2026-10-09T00:40:40Z", "t", text)["id"]

    def test_classify_gate(self):
        i = self.landed()
        with self.assertRaises(shot.ShotError):  # reason missing
            shot.classify(self.store, i, "app", "x")
        with self.assertRaises(shot.ShotError):  # chart without its identity
            shot.classify(self.store, i, "chart", "15m footprint of the 20:30 drop")
        with self.assertRaises(shot.ShotError):  # naive chart time needs the clock's offset
            shot.classify(self.store, i, "chart", "15m footprint of the 20:30 drop", "btcusdt", "15m", "2026-10-08 02:47", None, "footprint")
        with self.assertRaises(shot.ShotError):
            shot.classify(self.store, i, "chart", "15m footprint of the 20:30 drop", "btcusdt", "7m", "2026-10-08T02:47+05:30", None, "footprint")
        self.assertEqual(self.state()[i]["status"], "new")

    def test_chart_time_is_stored_in_utc_from_an_ist_clock(self):
        i = self.landed()
        shot.classify(self.store, i, "chart", "15m footprint of the 20:30 drop", "btcusdt", "15m", "2026-10-08 02:47", "+05:30", "binance footprint")
        s = self.state()[i]
        self.assertEqual((s["status"], s["symbol"], s["at"]), ("classified", "BTCUSDT", "2026-10-07T21:17:00Z"))

    def test_noise_closes_immediately_with_its_reason_kept(self):
        i = self.landed()
        shot.classify(self.store, i, "noise", "chrome extensions page, not about the project")
        s = self.state()[i]
        self.assertEqual((s["status"], s["outcome"]), ("done", "noaction:noise"))

    # ------------------------------------------------------------ read / done
    def chart(self, seed, tf, at="2026-10-07T21:15:00Z"):
        i = self.landed(seed)
        shot.classify(self.store, i, "chart", f"{tf} chart of the flush", "BTCUSDT", tf, at, None, "coinglass tv")
        return i

    def extract(self, text):
        p = self.tmp / "extract.md"
        p.write_text(text, encoding="utf-8", newline="\n")
        return p

    def test_read_needs_classification_the_id_and_claim_rows(self):
        n = self.landed("n")
        c = self.chart("c", "5m")
        good = "Shots: %s\nPrior: none\n| C1-01 | MATCH | header O 83388 | klines equal |\n| C1-02 | MISMATCH | CVD -10.7K | cvd_day -6.6K |\n| C1-03 | NOT_IN_DATA | net delta | no field |\n" % c
        with self.assertRaises(shot.ShotError):
            shot.read_extract(self.store, [n], self.extract("Shots: %s\n" % n))  # still new
        with self.assertRaises(shot.ShotError):
            shot.read_extract(self.store, [c], self.extract("no id here\n| C1-01 | MATCH | a | b |\n"))
        with self.assertRaises(shot.ShotError):
            shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: none\nprose only, no claim rows\n" % c))
        ids, counts, prior = shot.read_extract(self.store, [c], self.extract(good))
        self.assertEqual(counts, {"MATCH": 1, "MISMATCH": 1, "NOT_IN_DATA": 1})
        self.assertEqual(self.state()[c]["status"], "read")

    def test_chart_read_carries_the_prior_reads_falsifiers(self):  # B157
        c = self.chart("c", "5m")
        rows = "| C1-01 | MATCH | a | b |\n"
        with self.assertRaises(shot.ShotError):  # (a) no Prior line: the read would start cold
            shot.read_extract(self.store, [c], self.extract("Shots: %s\n%s" % (c, rows)))
        with self.assertRaises(shot.ShotError):  # (c) Prior names a file that does not exist
            shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: %s\n%s" % (c, self.tmp / "gone.md", rows)))
        ids, counts, prior = shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: none\n%s" % (c, rows)))  # (b)
        self.assertEqual(prior, (None, []))
        old = self.tmp / "prior_read.md"
        old.write_text("Shots: x\n- Invalidation: acceptance outside 82450-83470\nnoise line\nFalsify: acceptance under 82630\n"
                       "  - falsify if CVD flips\n", encoding="utf-8", newline="\n")
        ids, counts, prior = shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: %s\n%s" % (c, old, rows)))  # (d)
        self.assertEqual(prior[1], ["Invalidation: acceptance outside 82450-83470", "Falsify: acceptance under 82630",
                                    "falsify if CVD flips"])
        self.assertTrue(str(prior[0]).endswith("prior_read.md"))
        self.assertTrue(self.state()[c]["prior"].endswith("prior_read.md"))

    def test_read_stores_each_claim_row_in_the_manifest(self):  # B159
        real = Path(shot.REPO) / "MyTradingSys" / "research" / "screenshots" / "2026-10-09_BTCUSDT_78f967b4e253.md"
        c = self.chart("c", "5m")
        body = real.read_text(encoding="utf-8").replace("78f967b4e253", c)
        ids, counts, prior = shot.read_extract(self.store, [c], self.extract("Prior: none\n" + body))
        self.assertEqual(counts, {"MATCH": 4, "MISMATCH": 0, "NOT_IN_DATA": 5})  # status_line counts unchanged
        read = [e for e in shot.load_events(self.store) if e["event"] == "read"][-1]
        rows = read["claim_rows"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["id"], "D-01")
        self.assertEqual(rows[0]["class"], "MATCH")
        self.assertEqual(rows[0]["claim"], "price 82366 on 5m, bar low 82315.6")
        self.assertTrue(rows[0]["evidence"].startswith("Binance fapi 5m klines fetched 20:14Z"))
        self.assertEqual([r["class"] for r in rows].count("NOT_IN_DATA"), 5)
        self.assertEqual(len(self.state()[c]["claim_rows"]), 9)
        line, _ = shot.status_line(self.state())
        self.assertIn("claims MATCH 4 MISMATCH 0 NOT_IN_DATA 5", line)

    def test_malformed_claim_row_is_refused_with_its_line_number(self):  # B159
        c = self.chart("c", "5m")
        head = "Shots: %s\nPrior: none\n" % c
        for bad in ("| C1-02 | MATCH | claim without evidence |\n",          # 3 cells
                    "| C1-02 | MATCH |  | evidence but no claim |\n",       # empty claim
                    "| C1-02 | Match | a | b |\n"):                         # class spelled off the contract
            with self.assertRaises(shot.ShotError) as cm:
                shot.read_extract(self.store, [c], self.extract(head + "| C1-01 | MATCH | a | b |\n" + bad))
            self.assertIn("line 4", str(cm.exception), bad)
        self.assertEqual([e["event"] for e in shot.load_events(self.store)].count("read"), 0)  # nothing appended
        shot.read_extract(self.store, [c], self.extract(head + "| C1-01 | MATCH | a | b |\n"))  # a good one still passes

    def test_non_chart_extract_needs_no_prior_line(self):  # B157 default
        a = self.landed("a")
        shot.classify(self.store, a, "positions", "testnet positions table")
        ids, counts, prior = shot.read_extract(self.store, [a], self.extract("Shots: %s\nprose\n" % a))
        self.assertEqual(prior, (None, []))

    # ------------------------------------------------------------ engine at the shot (B160)
    def archive(self, *names):
        raw = Path(tempfile.mkdtemp(dir=self.tmp))
        (raw / "klines").mkdir(parents=True, exist_ok=True)
        for n in names:
            (raw / "klines" / n).write_text("", encoding="utf-8")
        return raw

    def test_engine_refuses_a_shot_without_an_instant_or_archive(self):
        raw = self.archive("BTCUSDT-1m-2026-10.csv")
        app = self.landed("a")
        shot.classify(self.store, app, "app", "claude desktop thread list")
        with self.assertRaises(shot.ShotError):  # not a chart
            shot.engine_plan(self.store, app, raw)
        old = self.landed("o")  # a chart classified before `at` was required
        shot.append(self.store, {"event": "classified", "id": old, "ts": "2026-10-01T00:00:00Z", "kind": "chart", "why": "old chart, no time", "symbol": "BTCUSDT"})
        with self.assertRaisesRegex(shot.ShotError, "no `at`"):
            shot.engine_plan(self.store, old, raw)
        c = self.chart("c", "5m", "2026-10-09T20:13:59Z")
        with self.assertRaisesRegex(shot.ShotError, "2026-10-09"):  # daily files stop at 10-08: refused, not a short replay
            shot.engine_plan(self.store, c, self.archive("BTCUSDT-1m-2026-10-08.csv"))
        rc, out, err = self.run_main("engine", c[:8], "--raw", str(self.tmp / "nowhere"), "--plan")
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", err)

    def test_engine_floors_the_shot_time_and_writes_the_instants_file(self):
        c = self.chart("c", "5m", "2026-10-09T20:13:59Z")
        for name in ("BTCUSDT-1m-2026-10.csv", "BTCUSDT-1m-2026-10-09.csv"):  # monthly or daily file both cover the day
            plan = shot.engine_plan(self.store, c, self.archive(name))
            self.assertEqual((plan["as_of"], plan["at"]), ("2026-10-09T20:13:00Z", "2026-10-09T20:13:59Z"))
        self.assertTrue(plan["out"].endswith(f"{c}.json"))
        p = shot.write_instants(plan, self.tmp)
        self.assertEqual(p.read_bytes(), b"2026-10-09T20:13:00Z\n")

    def test_engine_runs_snapat_and_saves_one_cited_record(self):
        c = self.chart("c", "5m", "2026-10-07T09:24:59Z")
        m2 = self.tmp / "m2"
        for j in shot.ENGINE_JARS:
            (m2 / "x" / j).parent.mkdir(parents=True, exist_ok=True)
            (m2 / "x" / j).write_bytes(b"")
        calls = []

        def fake(cmd, **kw):
            calls.append(cmd)
            if cmd[0] == "java":
                self.assertEqual(Path(cmd[-2]).read_text(encoding="utf-8"), "2026-10-07T09:24:00Z\n")
                Path(cmd[-1]).write_text(json.dumps({"price": 121000.5, "vp_poc": 120800.0}) + "\n", encoding="utf-8")
            return mock.Mock(returncode=0, stdout="done 1", stderr="")
        with mock.patch.dict(os.environ, {"MTS_M2": str(m2), "MTS_SHOT_ENGINE_DIR": str(self.tmp / "engine")}):
            plan = shot.engine_plan(self.store, c, self.archive("BTCUSDT-1m-2026-10-07.csv"))
            path = shot.run_engine(plan, runner=fake)
            self.assertEqual([k[0] for k in calls], ["javac", "java"])
            self.assertIn("datafeed.SnapAt", calls[1])
            self.assertTrue(any(a.endswith("SnapAt.java") for a in calls[0]))
            rec = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual((rec["shot"], rec["as_of"], rec["snapshot"]["vp_poc"]), (c, "2026-10-07T09:24:00Z", 120800.0))

            def empty(cmd, **kw):  # SnapAt printing null (no data at the instant) is a refusal, not an empty record
                if cmd[0] == "java":
                    Path(cmd[-1]).write_text("null\n", encoding="utf-8")
                return mock.Mock(returncode=0, stdout="", stderr="")
            path.unlink()
            with self.assertRaises(shot.ShotError):
                shot.run_engine(plan, runner=empty)
            self.assertFalse(path.exists())

    def test_done_needs_a_read_chart_and_an_outcome_that_exists(self):
        c = self.chart("c", "5m")
        with self.assertRaises(shot.ShotError):  # not read yet
            shot.done(self.store, [c], "noaction:nothing to see here at all")
        shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: none\n| C1-01 | MISMATCH | a | b |\n" % c))
        with self.assertRaises(shot.ShotError):  # a MISMATCH cannot be waved away in a few words
            shot.done(self.store, [c], "noaction:chart quirk")
        with self.assertRaises(shot.ShotError):  # item id shape
            shot.done(self.store, [c], "finding:bug")
        with self.assertRaises(shot.ShotError):  # well-formed ids that are not filed anywhere (this very line mentions B999)
            shot.done(self.store, [c], "finding:B999")
        with self.assertRaises(shot.ShotError):
            shot.done(self.store, [c], "feature:FEAT-9999")
        with self.assertRaises(shot.ShotError):
            shot.done(self.store, [c], "finding:F-BT-9999")
        with self.assertRaises(shot.ShotError):
            shot.done(self.store, [c], "closed")
        with self.assertRaises(shot.ShotError):  # a task card that does not exist
            shot.done(self.store, [c], "finding:card:no-such-card-for-this-test")
        shot.done(self.store, [c], "finding:B001")  # B001 is a real BUGS.md row
        d = self.chart("d", "15m")
        shot.read_extract(self.store, [d], self.extract("Shots: %s\nPrior: none\n| C1-01 | MISMATCH | a | b |\n" % d))
        shot.done(self.store, [d], "finding:card:tom-trade-ledger")  # a real task card file files the finding too
        self.assertEqual(self.state()[d]["status"], "done")
        self.assertEqual(self.state()[c]["status"], "done")

    def test_done_note_on_mismatch_shot_refused(self):
        """RV07: a MISMATCH is a B-item or an explained noaction (screenshot_intake.md); note:/feature: must not close it."""
        c = self.chart("c", "5m")
        shot.read_extract(self.store, [c], self.extract("Shots: %s\nPrior: none\n| C1-01 | MISMATCH | a | b |\n" % c))
        with mock.patch.object(shot, "outcome_exists", return_value=True):
            with self.assertRaises(shot.ShotError):
                shot.done(self.store, [c], "note:looked at it, fine")
            with self.assertRaises(shot.ShotError):
                shot.done(self.store, [c], "feature:FEAT-11")
            self.assertEqual(self.state()[c]["status"], "read")
            d = self.chart("d", "15m")
            shot.read_extract(self.store, [d], self.extract("Shots: %s\nPrior: none\n| C1-01 | NOT_IN_DATA | a | b |\n" % d))
            shot.done(self.store, [d], "feature:FEAT-11")  # NOT_IN_DATA becomes a feature hypothesis
            self.assertEqual(self.state()[d]["status"], "done")

    def test_outcome_exists_whole_token(self):
        """RV07: FEAT-1 must not count as filed because FEAT-11 is in a doc (git grep -F was a substring match)."""
        repo = self.tmp / "repo"
        repo.mkdir()
        shot.git("init", "-q", cwd=repo)
        (repo / "doc.md").write_text("FEAT-11 and F-BT-23 are filed here\n", encoding="utf-8", newline="\n")
        with mock.patch.object(shot, "REPO", repo), mock.patch.dict(os.environ, {"MTS_SHOT_SKIP_REPO_CHECK": ""}):
            self.assertTrue(shot.outcome_exists("FEAT-11"))
            self.assertTrue(shot.outcome_exists("F-BT-23"))
            self.assertFalse(shot.outcome_exists("FEAT-1"))
            self.assertFalse(shot.outcome_exists("F-BT-2"))

    def test_non_chart_can_close_without_a_read(self):
        a = self.landed("a")
        shot.classify(self.store, a, "app", "claude desktop showing the bypass-permissions prompt")
        shot.done(self.store, [a], "note:operator showed the permission dialog; no project change")
        self.assertEqual(self.state()[a]["status"], "done")

    def test_prefix_must_be_unique_and_long_enough(self):
        i = self.landed()
        with self.assertRaises(shot.ShotError):
            shot.resolve(self.state(), i[:3])
        self.assertEqual(shot.resolve(self.state(), i[:8]), i)

    # ------------------------------------------------------------ sets
    def test_sets_group_by_symbol_and_time_and_flag_single_timeframe(self):
        a = self.chart("a", "15m", "2026-10-07T21:14:00Z")
        b = self.chart("b", "5m", "2026-10-07T21:15:00Z")
        c = self.chart("c", "4h", "2026-10-07T21:18:00Z")
        d = self.chart("d", "15m", "2026-10-07T23:00:00Z")
        sets = shot.make_sets(self.state())
        self.assertEqual([s["ids"] for s in sets], [[a, b, c], [d]])
        self.assertEqual(sets[0]["tfs"], ["5m", "15m", "4h"])
        self.assertFalse(sets[0]["single_tf"])
        self.assertTrue(sets[1]["single_tf"])

    # ------------------------------------------------------------ gate
    def test_status_is_the_gate(self):
        old = shot.land(self.store, png("o"), "paste", SID, "2020-01-01T00:00:00Z", "t")["id"]
        rc, out, _ = self.run_main("status")
        self.assertEqual(rc, 1)
        self.assertIn("OVERDUE", out)
        shot.classify(self.store, old, "noise", "nothing about the project")
        rc, out, _ = self.run_main("status")
        self.assertEqual(rc, 0, out)
        self.assertIn("done 1", out)

    # ------------------------------------------------------------ hook
    def payload(self, event="UserPromptSubmit"):
        return json.dumps({"session_id": SID, "transcript_path": str(self.t), "cwd": "SLUG", "hook_event_name": event})

    def test_hook_saves_and_tells_the_session(self):
        self.write_transcript(paste_rec(png("a"), "stop those, 32 % gone"))
        rc, out, _ = self.run_main("hook", stdin=self.payload())
        self.assertEqual(rc, 0)
        i = next(iter(self.state()))
        self.assertIn("SAVED", out)
        self.assertIn(i, out)
        self.assertIn("32 % gone", out)
        rc, out, _ = self.run_main("hook", stdin=self.payload())  # nothing new: silent
        self.assertEqual((rc, out), (0, ""))

    def test_hook_session_start_reports_the_backlog(self):
        self.landed()
        rc, out, _ = self.run_main("hook", stdin=self.payload("SessionStart"))
        self.assertEqual(rc, 0)
        self.assertIn("not closed", out)
        rc, out, _ = self.run_main("hook", stdin=self.payload("SessionStart"))  # a second session within hours: not nagged again
        self.assertEqual((rc, out), (0, ""))
        cur = shot.load_cursors(self.store)
        cur["_nag"] = "2020-01-01T00:00:00Z"
        shot.save_cursors(self.store, cur)
        rc, out, _ = self.run_main("hook", stdin=self.payload("SessionStart"))  # long ago: reminded again
        self.assertIn("not closed", out)

    def test_hook_never_fails_a_prompt(self):
        for bad in ("", "not json", "[]"):
            rc, out, _ = self.run_main("hook", stdin=bad)
            self.assertEqual(rc, 0)
        blocker = self.tmp / "iamafile"
        blocker.write_text("x")
        with mock.patch.dict(os.environ, {"MTS_SHOT_DIR": str(blocker / "sub")}):
            self.write_transcript(paste_rec(png("a"), "x"))
            rc, _, _ = self.run_main("hook", stdin=self.payload())
        self.assertEqual(rc, 0)

    # ------------------------------------------------------------ carried falsifiers (T092)
    def test_falsifier_status_price_level_held(self):
        # SOURCED line: "Falsify: acceptance under 82630" (test_shot.py:211, B157_screenshot_read_starts_cold.md:7)
        # OURS fixture: low touches/dips to 82600 (tested), but close 82650 holds above 82630
        line = "Falsify: acceptance under 82630"
        klines = [{"o": 82700.0, "h": 82750.0, "l": 82600.0, "c": 82650.0}]
        self.assertEqual(shot.falsifier_status(line, klines), "HELD")

    def test_falsifier_status_price_level_broken_by_close(self):
        # SOURCED line: "Falsify: acceptance under 82630" (test_shot.py:211, B157_screenshot_read_starts_cold.md:7)
        # OURS fixture: close 82550 is below 82630
        line = "Falsify: acceptance under 82630"
        klines = [{"o": 82700.0, "h": 82750.0, "l": 82500.0, "c": 82550.0}]
        self.assertEqual(shot.falsifier_status(line, klines), "BROKEN")

    def test_falsifier_status_price_level_not_yet_reached(self):
        # SOURCED line: "Falsify: acceptance under 82630" (test_shot.py:211, B157_screenshot_read_starts_cold.md:7)
        # OURS fixture: low 82680 never reaches 82630
        line = "Falsify: acceptance under 82630"
        klines = [{"o": 82700.0, "h": 82800.0, "l": 82680.0, "c": 82750.0}]
        self.assertEqual(shot.falsifier_status(line, klines), "UNTESTED")

    def test_falsifier_status_range_and_non_price_lines(self):
        # SOURCED line: "Invalidation: acceptance outside 82450-83470" (test_shot.py:211)
        line = "Invalidation: acceptance outside 82450-83470"
        # Level held: low probes 82400 but close is 82460 (inside range)
        self.assertEqual(shot.falsifier_status(line, [{"o": 82500, "h": 82600, "l": 82400, "c": 82460}]), "HELD")
        # Broken: close 82400 (outside range)
        self.assertEqual(shot.falsifier_status(line, [{"o": 82500, "h": 82600, "l": 82350, "c": 82400}]), "BROKEN")
        # Unreached: all bars inside [82450, 83470] without touching bounds
        self.assertEqual(shot.falsifier_status(line, [{"o": 82500, "h": 83000, "l": 82500, "c": 82900}]), "UNTESTED")
        # SOURCED line: "- falsify if CVD flips" (test_shot.py:212) -> non-price line -> UNTESTED
        self.assertEqual(shot.falsifier_status("- falsify if CVD flips", [{"o": 82500, "h": 82600, "l": 82400, "c": 82460}]), "UNTESTED")

    def test_read_prints_status_for_each_carried_falsifier(self):
        c = self.chart("c", "5m")
        rows = "| C1-01 | MATCH | a | b |\n"
        old = self.tmp / "prior_read.md"
        old.write_text("Shots: x\n- Invalidation: acceptance outside 82450-83470\nFalsify: acceptance under 82630\n- falsify if CVD flips\n",
                       encoding="utf-8", newline="\n")
        ext = self.extract("Shots: %s\nPrior: %s\n%s" % (c, old, rows))
        # Provide klines where 82630 and 82450 are broken by close (close 82400 < 82450 < 82630)
        kpath = self.tmp / "klines.json"
        kpath.write_text(json.dumps([{"o": 82700, "h": 82750, "l": 82350, "c": 82400}]), encoding="utf-8", newline="\n")
        rc, out, _ = self.run_main("read", c, "--extract", str(ext), "--klines", str(kpath))
        self.assertEqual(rc, 0)
        self.assertIn("[BROKEN] Falsify: acceptance under 82630", out)
        self.assertIn("[BROKEN] Invalidation: acceptance outside 82450-83470", out)
        self.assertIn("[UNTESTED] falsify if CVD flips", out)


class MainRootOldGit(unittest.TestCase):
    def test_git_224_flag_echo_is_not_a_path(self):
        """git 2.24 prints the unsupported flag as line 1 then the dir; the store path must be the dir."""
        def fake(*a, cwd=None):
            return "--path-format=absolute\nC:/x/MTS/.git\n" if "--path-format=absolute" in a else ""
        with mock.patch.object(shot, "git", fake):
            self.assertEqual(shot.main_root(), Path("C:/x/MTS"))


class HookStartupTest(unittest.TestCase):
    def test_hook_path_does_not_import_heavy_modules(self):
        """2026-10-22: shot.py hook cost 1.4 s per prompt; argparse/tempfile/traceback/hashlib are imported only when used."""
        import subprocess
        here = Path(__file__).resolve().parent
        code = ("import sys, io; sys.path.insert(0, %r); sys.argv = ['shot.py', 'hook']; sys.stdin = io.TextIOWrapper(io.BytesIO(b'{}'));"
                " import shot; shot.main(); heavy = [m for m in ('argparse', 'tempfile', 'traceback', 'hashlib', 'shutil') if m in sys.modules];"
                " print(heavy)" % str(here))
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "MTS_SHOT_DIR": d, "MTS_SHOT_TEMP": d, "MTS_CLAUDE_HOME": d}
            r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        self.assertEqual(r.stdout.strip().splitlines()[-1], "[]", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
