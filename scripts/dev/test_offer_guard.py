"""offer_guard.py: a session may not end its reply by asking the operator's leave for work it can do (operator 2026-10-22)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer_guard as G


class OfferGuardTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        os.environ["MTS_STOP_GUARD_HOME"] = self.d.name

    def tearDown(self):
        os.environ.pop("MTS_STOP_GUARD_HOME", None)
        self.d.cleanup()

    def run_hook(self, reply, sid="s1", active=False):
        return G.hook(json.dumps({"session_id": sid, "last_assistant_message": reply, "stop_hook_active": active}))

    def test_trailing_offer_blocks_once(self):
        reply = "CI fixes are written up in the diagnosis.\n\nBoth are PENDING OPERATOR; say go for #1 and I'll file it."
        out = json.loads(self.run_hook(reply))
        self.assertEqual(out["decision"], "block")
        self.assertIn("OFFER GUARD", out["reason"])
        self.assertEqual(self.run_hook(reply), "")

    def test_common_offer_phrasings_are_caught(self):
        for s in ("Want me to file the card?", "Shall I ship it now?", "If you'd like, I can add the hook too.",
                  "Let me know if you want the Windows split as well.", "I can also republish the pages if you want."):
            self.assertTrue(G.flagged("Done.\n" + s), s)

    def test_operator_only_quotes_and_early_lines_pass(self):
        self.assertEqual(G.flagged("OPERATOR-ONLY: mainnet keys: shall I wait for your account?"), [])
        self.assertEqual(G.flagged('The hook blocks endings like "want me to" and `say go`.'), [])
        early = "Want me to explain? No: here it is.\n" + "\n".join(f"line {i}" for i in range(6))
        self.assertEqual(G.flagged(early), [])
        self.assertEqual(G.flagged("```\nwant me to\n```\nShipped."), [])

    def test_second_stop_and_switch_off_allow(self):
        self.assertEqual(self.run_hook("Want me to ship it?", active=True), "")
        os.environ["MTS_OFFER_GUARD"] = "off"
        try:
            self.assertEqual(self.run_hook("Want me to ship it?", sid="s2"), "")
        finally:
            os.environ.pop("MTS_OFFER_GUARD", None)

    def test_registered_as_stop_hook(self):
        root = Path(__file__).resolve().parents[2]
        stops = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]["Stop"]
        cmds = [h["command"] for e in stops for h in e["hooks"]]
        self.assertTrue(any("offer_guard.py" in c for c in cmds), cmds)


if __name__ == "__main__":
    unittest.main()
