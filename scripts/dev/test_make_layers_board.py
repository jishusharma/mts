"""MTS Layers page generator: stuck days, missing steps and waiting decisions come out right, and the real repo renders."""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import make_layers_board as mlb  # noqa: E402

NOW = 1_791_936_000  # 2026-10-14 00:00Z, fixed so ages are exact
DAY = 86400


def iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def card(cid, state, age_days, **kw):
    c = {"id": cid, "title": cid.replace("-", " "), "state": state, "lane": "SONNET", "prio": 1,
         "created": iso(NOW - age_days * DAY), "layers": ["alpha"], "depends_on": [], "asks": "", "note": ""}
    c.update(kw)
    return c


def mini_repo(d):
    sysd = Path(d) / "MyTradingSys" / "system"
    (sysd / "tasks").mkdir(parents=True)
    (sysd / "claims").mkdir()
    idx = {"_doc": "", "cross_cutting": [], "families": [{
        "id": "alpha", "name": "Alpha", "tracks": "", "status": "testing", "plain": "a test layer", "spec": [], "code": [], "ledger": [],
        "results": [], "roadmap": [], "cards": [], "layers": ["a1"],
        "path": {"idea": {"s": "done"}, "inputs": {"s": "missing", "note": "no data plan"},
                 "fees": {"s": "planned", "cards": ["a-done"]}, "charts": {"s": "planned", "cards": ["a-ready"]},
                 "built": {"s": "skip"}, "dev": {"s": "failed"}, "oos": {"s": "later"}, "testnet": {"s": "later"}}}]}
    (sysd / "layer_index.json").write_text(json.dumps(idx), encoding="utf-8")
    lmap = {"layers": [{"id": "a1"}], "backtests": [{"id": "BT1", "date": "2026-10-01", "layers": ["a1"], "verdict": "no edge"}]}
    (sysd / "layer_map.json").write_text(json.dumps(lmap), encoding="utf-8")
    for c in (card("a-ready", "ready", 5), card("a-held", "blocked", 1, note="waiting for data"),
              card("a-after", "raw", 0, depends_on=["a-held"]), card("a-done", "done", 9)):
        (sysd / "tasks" / f"{c['id']}.json").write_text(json.dumps(c), encoding="utf-8")
    (sysd / "claims" / "old.md").write_text(f"task: a-ready\nhost: JIS-NUC\naccount: awgp\nepoch: {NOW - 30 * 3600}\n", encoding="utf-8")
    (sysd / "OPERATOR_DECISIONS.md").write_text(
        "# OPERATOR DECISIONS\n\n## q1-open | asked 2026-10-11 | Process | NO AUTO-APPLY\n\nShould we?\n\nRecommended: Yes\n"
        "Answer: (none yet)\nApplied: (not yet)\n\n## q2-done | asked 2026-10-10 | Process\n\nDone one?\n\nRecommended: Yes\n"
        "Answer: Yes\nApplied: 2026-10-11\n\n## q3-pending | asked 2026-10-12 | Process\n\nAnswered only?\n\nRecommended: No\n"
        "Answer: No\nApplied: (not yet)\n", encoding="utf-8")
    (sysd / "HOW_MTS_RUNS.md").write_text("# How\n\n| A | B |\n|---|---|\n| x `y` | **z** |\n\n- one\n- two\n", encoding="utf-8")
    return Path(d)


class LayersBoardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = mlb.build(mini_repo(self.tmp.name), now=NOW)
        self.f = self.data["families"][0]

    def tearDown(self):
        self.tmp.cleanup()

    def test_stuck_reasons_carry_days(self):
        why = {(s["card"], s["why"]) for s in self.f["stuck"]}
        self.assertIn(("a-ready", "ready for 5 d, no session has taken it"), why)
        self.assertNotIn("a-held", {c for c, _ in why}, "a card parked on purpose is on hold, not stuck")
        self.assertEqual([(h["id"], h["why"][0]) for h in self.f["held"]], [("a-held", "on hold 1 d: waiting for data")])
        self.assertIn(("a-after", "waits on a-held, which is blocked"), why)

    def test_missing_steps(self):
        steps = {s["key"]: s["s"] for s in self.f["steps"]}
        self.assertEqual(steps["inputs"], "missing")
        self.assertEqual(steps["fees"], "missing", "a planned step whose only card is done has nothing planned left")
        self.assertEqual(steps["charts"], "planned")
        self.assertEqual([m["step"] for m in self.f["missing"]], ["Inputs in BTC data", "Fees fit"])

    def test_progress_counts_done_and_failed_and_skips_skip(self):
        self.assertEqual(self.f["progress"], [2, 7])

    def test_next_is_first_unheld_open_card(self):
        self.assertEqual(self.f["next"]["id"], "a-ready")
        self.assertEqual(self.f["moved_days"], 0)

    def test_waiting_on_operator(self):
        states = {d["id"]: d["state"] for d in self.data["decisions"]}
        self.assertEqual(states, {"q1-open": "open", "q3-pending": "answered, not applied"})
        self.assertEqual(self.data["totals"]["waiting"], 1)
        self.assertEqual([c["task"] for c in self.data["stale_claims"]], ["a-ready"])
        self.assertEqual([c["id"] for c in self.data["held"]], ["a-held"])

    def test_how_markdown(self):
        h = self.data["how"]
        self.assertIn("<th>A</th>", h)
        self.assertIn("<code>y</code>", h)
        self.assertIn("<strong>z</strong>", h)
        self.assertIn("<li>two</li>", h)

    def test_real_repo_renders_every_family(self):
        data = mlb.build()
        ids = [f["id"] for f in data["families"]]
        idx = json.loads((REPO / "MyTradingSys/system/layer_index.json").read_text(encoding="utf-8"))
        self.assertEqual(ids, [f["id"] for f in idx["families"]])
        page = mlb.render(data)
        self.assertNotIn("__DATA__", page)
        self.assertTrue(page.startswith("<title>MTS Layers</title>"))


if __name__ == "__main__":
    unittest.main()
