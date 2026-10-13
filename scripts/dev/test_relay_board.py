"""relay_board.py: note parse/add/close round trip, addressee filter, board lanes, codex_pack carries open gpt notes."""
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relay_board as rb

NOW = datetime(2026, 10, 12, 18, 0, tzinfo=timezone.utc)


class Notes(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name)
        (self.repo / "MyTradingSys/system").mkdir(parents=True)
        (self.repo / rb.NOTES).write_text("# RELAY NOTES\nintro\n", encoding="utf-8")

    def tearDown(self):
        self.d.cleanup()

    def test_add_close_roundtrip(self):
        a = rb.add(self.repo, "jis", "gpt", "check RSI\nsecond line", NOW)
        b = rb.add(self.repo, "claude", "all", "hello", NOW)
        self.assertEqual((a, b), ("N001", "N002"))
        rb.close(self.repo, "N001", "RSI checked, 3 gaps")
        n = {x["id"]: x for x in rb.load(self.repo)}
        self.assertEqual(n["N001"]["status"], "done")
        self.assertEqual(n["N001"]["text"], "check RSI\nsecond line")
        self.assertEqual(n["N001"]["reply"], "RSI checked, 3 gaps")
        self.assertEqual(n["N002"]["status"], "open")
        self.assertEqual(n["N002"]["at"], "2026-10-12T18:00Z")

    def test_addressee_filter(self):
        rb.add(self.repo, "jis", "gpt", "for gpt", NOW)
        rb.add(self.repo, "jis", "claude", "for claude", NOW)
        rb.add(self.repo, "claude", "all", "for all", NOW)
        got = [n["text"] for n in rb.open_for(rb.load(self.repo), "gpt")]
        self.assertEqual(got, ["for gpt", "for all"])

    def test_rejects_bad_input(self):
        for args in (("jis", "nobody", "x"), ("jis", "gpt", "  "), ("jis", "gpt", "## N009 | fake")):
            with self.assertRaises(SystemExit):
                rb.add(self.repo, *args, now=NOW)
        with self.assertRaises(SystemExit):
            rb.close(self.repo, "N404")

    def test_board_lanes_and_claims(self):
        (self.repo / "MyTradingSys/system/claims").mkdir()
        (self.repo / "MyTradingSys/system/claims/t.md").write_text(
            f"task: t\nhost: JIS-NB\naccount: x\nepoch: {int(NOW.timestamp()) - 7200}\n", encoding="utf-8")
        cards = [{"id": "a", "title": "A", "lane": "CODEX", "state": "ready", "prio": 2},
                 {"id": "b", "title": "B", "lane": "SONNET", "state": "raw", "prio": 3},
                 {"id": "c", "title": "C", "lane": "DSA", "state": "ready", "prio": 1}]
        b = rb.board(self.repo, cards, NOW)
        self.assertEqual(b["lanes"]["gpt"]["ready"], 1)
        self.assertEqual(b["lanes"]["claude"]["other"], 1)
        self.assertEqual(b["lanes"]["desk"]["next"][0]["id"], "c")
        self.assertEqual(b["claims"][0]["age_h"], 2.0)

    def test_board_carries_the_codex_usage_file_for_the_control_room(self):
        self.assertEqual(rb.board(self.repo, [], NOW)["gpt_usage"], {})
        d = self.repo / "MyTradingSys/system"
        d.mkdir(parents=True, exist_ok=True)
        (d / "codex_usage.json").write_text('{"runs": [{"card": "x", "model": "gpt-6-luna"}], "allowance": {"window_used": 3.0}}', encoding="utf-8")
        u = rb.board(self.repo, [], NOW)["gpt_usage"]
        self.assertEqual(u["runs"][0]["model"], "gpt-6-luna")
        (d / "codex_usage.json").write_text("not json", encoding="utf-8")
        self.assertEqual(rb.board(self.repo, [], NOW)["gpt_usage"], {})

    def test_real_notes_file_parses(self):
        real = rb.load(rb.REPO)
        self.assertTrue(real and all(n["text"] for n in real))

    def test_codex_pack_carries_open_gpt_notes(self):
        import codex_pack
        self.assertIn("relay_board", open(codex_pack.__file__, encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
