"""tasks.py: the Definition of Ready is fail closed, ordering and buffer rules, dependency gating, operator actions,
registry sweep, the brief length cap, and a CLI round-trip. Spec: MyTradingSys/system/TASK_REFINEMENT.md."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks as T


def good(cid="B900", **kw):
    c = T.blank(cid, "Run the 28 cells")
    c.update(lane="SONNET", size="S", goal="Runner for 28 pre-registered cells", scope_in=["MyTradingSys/backtest/htf/"],
             steps=["write runner", "run once on holdout"], tests="test_runner fails on old code", done_when="results.csv has 28 rows",
             state="ready")
    c.update(kw)
    return c


class DefinitionOfReadyTest(unittest.TestCase):
    def test_good_card_passes(self):
        self.assertEqual(T.problems(good()), [])

    def test_each_required_field_is_enforced(self):
        for k, empty in (("goal", ""), ("done_when", " "), ("scope_in", []), ("steps", []), ("size", ""), ("lane", "")):
            with self.subTest(k=k):
                self.assertTrue(T.problems(good(**{k: empty})), k)

    def test_size_L_must_be_split(self):
        self.assertTrue(any("split" in m for m in T.problems(good(size="L"))))

    def test_code_lane_needs_tests_run_lane_needs_commands(self):
        self.assertTrue(any("tests" in m for m in T.problems(good(tests=""))))
        self.assertEqual(T.problems(good(lane="DSA-NB", tests="", commands=["python x.py"])), [])
        self.assertTrue(any("commands" in m for m in T.problems(good(lane="DSA-NB", tests=""))))

    def test_opus_needs_operator_approval(self):
        self.assertTrue(any("approved_by" in m for m in T.problems(good(lane="OPUS"))))
        self.assertEqual(T.problems(good(lane="OPUS", approved_by="operator")), [])

    def test_live_path_never_goes_to_a_relay_lane(self):
        self.assertTrue(any("live_path" in m for m in T.problems(good(live_path=True))))
        self.assertEqual(T.problems(good(lane="JIS-NB", live_path=True, commands=["desk"], tests="")), [])

    def test_placeholders_and_long_fields_are_rejected(self):
        self.assertTrue(any("placeholder" in m for m in T.problems(good(goal="figure out the cells"))))
        self.assertTrue(any("placeholder" in m for m in T.problems(good(steps=["TBD"]))))
        self.assertTrue(any("chars" in m for m in T.problems(good(goal="x" * 401))))

    def test_brief_is_capped_at_30_lines(self):
        c = good(steps=[f"step {i}" for i in range(40)])
        self.assertTrue(any("30 lines" in m for m in T.problems(c)))
        self.assertLessEqual(len(T.brief(good()).splitlines()), T.MAX_BRIEF)

    def test_dependencies_must_be_done_or_registry_closed(self):
        dep = good("B901", state="active")
        self.assertTrue(any("B901" in m for m in T.problems(good(depends_on=["B901"]), [dep])))
        dep["state"] = "done"
        self.assertEqual(T.problems(good(depends_on=["B901"]), [dep]), [])
        self.assertEqual(T.problems(good(depends_on=["B050"]), [], {"B050": "CLOSED"}), [])
        self.assertTrue(T.problems(good(depends_on=["B050"]), [], {"B050": "OPEN"}))
        self.assertTrue(T.problems(good(depends_on=["B404"]), [], {}))


class QueueTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name)
        self._repo = T.REPO
        T.REPO = self.repo

    def tearDown(self):
        T.REPO = self._repo
        self.d.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            try:
                rc = T.main(list(argv))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
                out.write(str(e.code) if not isinstance(e.code, int) else "")
        return rc, out.getvalue()

    def test_ready_order_pin_then_prio_then_age(self):
        T.save(self.repo, good("B1", prio=3, created="2026-10-01"))
        T.save(self.repo, good("B2", prio=2, created="2026-10-09"))
        T.save(self.repo, good("B3", prio=5, created="2026-10-01", pinned=True))
        T.save(self.repo, good("B4", prio=2, created="2026-10-02"))
        cs, _ = T.ready_cards(self.repo)
        self.assertEqual([c["id"] for c in cs], ["B3", "B4", "B2", "B1"])

    def test_hand_edited_ready_card_that_fails_is_not_served_and_lint_fails(self):
        T.save(self.repo, good("B1", goal=""))
        self.assertEqual(T.ready_cards(self.repo)[0], [])
        rc, out = self.run_cli("lint")
        self.assertEqual(rc, 1)
        self.assertIn("goal is empty", out)
        rc, out = self.run_cli("next")
        self.assertEqual(rc, 1)
        self.assertIn("NO_READY_CARD", out)

    def test_check_promotes_only_when_it_passes(self):
        c = good("B1", state="refined", goal="")
        T.save(self.repo, c)
        rc, out = self.run_cli("check", "B1")
        self.assertIn("NOT READY", out)
        self.assertEqual(T.get(self.repo, "B1")["state"], "refined")
        c["goal"] = "do the thing"
        T.save(self.repo, c)
        self.run_cli("check", "B1")
        self.assertEqual(T.get(self.repo, "B1")["state"], "ready")

    def test_check_all_demotes_a_ready_card_that_regressed(self):
        T.save(self.repo, good("B1", goal=""))
        rc, _ = self.run_cli("check", "--demote")
        self.assertEqual(rc, 1)
        self.assertEqual(T.get(self.repo, "B1")["state"], "refined")

    def test_status_line_refine_needed_only_when_work_waits_and_buffer_low(self):
        T.save(self.repo, good("B1", state="raw"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))
        for i in range(3):
            T.save(self.repo, good(f"R{i}"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_OK"))
        for i in range(3):
            (self.repo / T.DIR / f"R{i}.json").unlink()
        (self.repo / T.DIR / "B1.json").unlink()
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_OK"))   # nothing waiting

    def test_take_and_done_lifecycle(self):
        T.save(self.repo, good("B1"))
        self.assertEqual(self.run_cli("take", "B1", "--claim", "slug")[0], 0)
        self.assertEqual(T.get(self.repo, "B1")["state"], "active")
        self.assertNotEqual(self.run_cli("take", "B1")[0], 0)          # already active
        self.run_cli("done", "B1", "--result", "28 rows in results.csv")
        c = T.get(self.repo, "B1")
        self.assertEqual((c["state"], c["result"]), ("done", "28 rows in results.csv"))

    def test_take_refuses_a_card_that_no_longer_passes(self):
        T.save(self.repo, good("B1", done_when=""))
        self.assertNotEqual(self.run_cli("take", "B1")[0], 0)
        self.assertEqual(T.get(self.repo, "B1")["state"], "ready")

    def test_operator_actions(self):
        T.save(self.repo, good("B1", lane="OPUS"))
        self.run_cli("apply-op", "B1", "approve")
        self.assertEqual(T.get(self.repo, "B1")["approved_by"], "operator")
        self.run_cli("apply-op", "B1", "bump", "--note", "do first")
        c = T.get(self.repo, "B1")
        self.assertEqual((c["prio"], c["pinned"], c["note"]), (1, True, "do first"))
        self.run_cli("apply-op", "B1", "hold")
        self.assertEqual(T.get(self.repo, "B1")["state"], "blocked")
        self.run_cli("apply-op", "B1", "release")
        self.assertEqual(T.get(self.repo, "B1")["state"], "refined")
        self.run_cli("apply-op", "B1", "drop")
        self.assertEqual(T.get(self.repo, "B1")["state"], "dropped")

    def test_sweep_retires_cards_whose_registry_rows_closed(self):
        bugs = self.repo / T.BUGS
        bugs.parent.mkdir(parents=True)
        bugs.write_text("| ID | Opened | Status | Severity | Title | Evidence | Receipt |\n|---|---|---|---|---|---|---|\n"
                        "| B900 | 2026-10-01 | CLOSED | MED | t | e | r |\n| B901 | 2026-10-01 | OPEN | MED | t | e | |\n", encoding="utf-8")
        T.save(self.repo, good("C1", refs=["B900"]))
        T.save(self.repo, good("C2", refs=["B900", "B901"]))
        T.save(self.repo, good("C3", refs=[]))
        self.run_cli("sweep")
        self.assertEqual(T.get(self.repo, "C1")["state"], "ready")        # dry run changes nothing
        self.run_cli("sweep", "--apply")
        self.assertEqual([T.get(self.repo, i)["state"] for i in ("C1", "C2", "C3")], ["done", "ready", "ready"])

    def test_new_creates_a_raw_card_and_refuses_duplicates(self):
        rc, _ = self.run_cli("new", "Check the funding sign", "--id", "B950", "--ref", "B950", "--from-inbox", "abc")
        c = T.get(self.repo, "B950")
        self.assertEqual((rc, c["state"], c["refs"], c["from_inbox"]), (0, "raw", ["B950"], "abc"))
        self.assertNotEqual(self.run_cli("new", "again", "--id", "B950")[0], 0)

    def test_summary_flags_missing_and_unapproved_opus(self):
        T.save(self.repo, good("B1", lane="OPUS"))
        T.save(self.repo, good("B2", state="refined", goal=""))
        T.save(self.repo, good("B3", state="done"))
        s = T.summary(self.repo)
        by = {r["id"]: r for r in s["rows"]}
        self.assertNotIn("B3", by)
        self.assertTrue(by["B1"]["needs_approval"])
        self.assertIn("goal is empty", by["B2"]["missing"])

    def test_summary_shows_ready_before_refined_before_raw(self):
        T.save(self.repo, good("A", state="raw"))
        T.save(self.repo, good("B", state="refined"))
        T.save(self.repo, good("C"))
        self.assertEqual([r["id"] for r in T.summary(self.repo)["rows"]], ["C", "B", "A"])


class RepoDataTest(unittest.TestCase):
    def test_every_committed_card_is_consistent(self):
        cards = T.load_all(T.REPO)
        reg = T.registry(T.REPO)
        for c in cards:
            with self.subTest(card=c["id"]):
                self.assertIn(c["state"], T.STATES)
                self.assertEqual(c["id"] + ".json", T.path_of(T.REPO, c["id"]).name)
                if c["state"] in T.LIVE:
                    self.assertEqual(T.problems(c, cards, reg), [])


if __name__ == "__main__":
    unittest.main()
