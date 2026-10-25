"""tasks.py: the Definition of Ready is fail closed, ordering and buffer rules, dependency gating, operator actions,
registry sweep, the brief length cap, and a CLI round-trip. Spec: MyTradingSys/system/TASK_REFINEMENT.md."""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks as T


NL = chr(10)


def good(cid="B900", **kw):
    c = T.blank(cid, "Run the 28 cells")
    c.update(lane="SONNET", size="S", goal="Runner for 28 pre-registered cells", scope_in=["MyTradingSys/backtest/htf/"],
             steps=["write runner", "run once on holdout"], tests="test_runner fails on old code", done_when="results.csv has 28 rows",
             state="ready", est_turns=12, worker="agent")
    c.update(kw)
    return c


def run_cli(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = T.main(list(argv))
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
            if isinstance(e.code, str):
                print(e.code)  # SystemExit(msg) prints to stderr at interpreter exit
    return rc, out.getvalue()


class DefinitionOfReadyTest(unittest.TestCase):
    def test_good_card_passes(self):
        self.assertEqual(T.problems(good()), [])

    def test_each_required_field_is_enforced(self):
        for k, empty in (("goal", ""), ("done_when", " "), ("scope_in", []), ("steps", []), ("size", ""), ("lane", "")):
            with self.subTest(k=k):
                self.assertTrue(T.problems(good(**{k: empty})), k)

    def test_worker_type_is_set_up_front_and_consistent(self):
        """WORKERS.md: agent = size S and est_turns <= 15, session otherwise; code lanes only."""
        has = lambda c, w: any(w in m for m in T.problems(c))
        self.assertTrue(has(good(est_turns=None), "est_turns"))
        self.assertTrue(has(good(est_turns=0), "est_turns"))
        self.assertTrue(has(good(est_turns="12"), "est_turns"))
        self.assertTrue(has(good(worker=""), "worker"))
        self.assertTrue(has(good(worker="subagent"), "worker"))
        self.assertTrue(has(good(est_turns=30), "session"))          # too long for an agent
        self.assertTrue(has(good(size="M"), "session"))              # M is never an agent
        self.assertEqual(T.problems(good(size="M", est_turns=30, worker="session")), [])
        self.assertEqual(T.problems(good(est_turns=5, worker="session")), [])   # a session may take a small card
        self.assertTrue(has(good(est_turns=41, worker="session"), "split"))   # over the 40-turn cap: split
        self.assertEqual(T.problems(good(lane="DSA-NB", tests="", commands=["x"], est_turns=None, worker="")), [])   # run lanes exempt

    def test_size_L_must_be_split(self):
        self.assertTrue(any("split" in m for m in T.problems(good(size="L"))))

    def test_code_lane_needs_tests_run_lane_needs_commands(self):
        self.assertTrue(any("tests" in m for m in T.problems(good(tests=""))))
        self.assertEqual(T.problems(good(lane="DSA-NB", tests="", commands=["python x.py"])), [])
        self.assertTrue(any("commands" in m for m in T.problems(good(lane="DSA-NB", tests=""))))

    def test_opus_needs_operator_approval(self):
        self.assertTrue(any("approved_by" in m for m in T.problems(good(lane="OPUS"))))
        self.assertTrue(any("crucial" in m for m in T.problems(good(lane="OPUS", approved_by="operator"))))
        self.assertEqual(T.problems(good(lane="OPUS", approved_by="operator", crucial="rewrites live order state, no undo")), [])

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

    def test_brief_prints_read_first_ruled_out_traps_and_first_commands(self):
        c = good(context={"reads": ["scripts/dev/desk.py", "scripts/dev/lease.py"], "misses": 2}, commands=["pytest -q x"],
                 note="HOLD two clones must close the row in one second" + NL + "tried a second lease",
                 latest=[{"kind": "decision", "ref": "r", "utc": "2026-10-25T00:00:00Z", "line": "no second lease"}])
        b = T.brief(c)
        self.assertIn("Read first: scripts/dev/desk.py, scripts/dev/lease.py", b)
        self.assertIn("Ruled out: no second lease | tried a second lease", b)
        self.assertIn("Traps: HOLD two clones", b)
        self.assertIn('First commands: python scripts/dev/sync.py start B900; python scripts/dev/sync.py claim "B900"; pytest -q x', b)
        self.assertLessEqual(len(b.splitlines()), T.MAX_BRIEF)
        self.assertNotIn("Read first:", T.brief(good()))
        self.assertEqual(T.problems(c), [])
        self.assertTrue(any("context" in m for m in T.problems(good(context={"reads": [str(i) for i in range(9)]}))))

    def test_weight_field_is_validated_optional_and_shown_in_brief(self):
        self.assertTrue(any("BOGUS" in m for m in T.problems(good(weight="BOGUS"))))
        self.assertEqual(T.problems(good(weight="CRUCIAL")), [])
        self.assertEqual(T.problems(good()), [])
        self.assertEqual(T.problems(good(weight="")), [])
        self.assertIn("Weight: CRUCIAL", T.brief(good(weight="CRUCIAL")))
        self.assertNotIn("Weight:", T.brief(good()))
        self.assertEqual(T.blank("B1", "t")["weight"], "")

    def test_weight_line_counts_toward_the_30_line_brief(self):
        base = len(T.brief(good(steps=["s0"])).splitlines())
        steps = [f"step {i}" for i in range(T.MAX_BRIEF - base + 1)]
        self.assertEqual(len(T.brief(good(steps=steps)).splitlines()), T.MAX_BRIEF)
        self.assertEqual(T.problems(good(steps=steps)), [])
        self.assertTrue(any("30 lines" in m for m in T.problems(good(steps=steps, weight="CRUCIAL"))))

    def test_dependencies_must_be_done_or_registry_closed(self):
        dep = good("B901", state="active")
        self.assertTrue(any("B901" in m for m in T.problems(good(depends_on=["B901"]), [dep])))
        dep["state"] = "done"
        self.assertEqual(T.problems(good(depends_on=["B901"]), [dep]), [])
        self.assertEqual(T.problems(good(depends_on=["B050"]), [], {"B050": "CLOSED"}), [])
        self.assertTrue(T.problems(good(depends_on=["B050"]), [], {"B050": "OPEN"}))
        self.assertTrue(T.problems(good(depends_on=["B404"]), [], {}))



class LayerFieldTest(unittest.TestCase):
    """A card names its layer family (layer_index.json) so LAYERS.md and the brief point the session at the layer's files."""
    def test_unknown_layer_fails_ready_known_layer_passes(self):
        self.assertTrue(any("not a family" in m for m in T.problems(good(layers=["tom_v9"]))))
        self.assertEqual(T.problems(good(layers=["tom", "fabio"])), [])

    def test_brief_points_at_the_layer_index(self):
        self.assertIn("LAYERS.md", T.brief(good(layers=["fabio"])))
        self.assertNotIn("LAYERS.md", T.brief(good()))

    def test_every_card_in_the_repo_names_known_layers(self):
        fams = T.layer_families()
        for c in T.load_all():
            for x in c.get("layers", []):
                self.assertIn(x, fams, c["id"])

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

    def test_new_with_layer_records_it_and_refuses_an_unknown_one(self):
        rc, _ = self.run_cli("new", "Spike fade recall", "--id", "x1", "--layer", "tom")
        self.assertEqual((rc, T.get(self.repo, "x1")["layers"]), (0, ["tom"]))
        rc, out = self.run_cli("new", "Bad layer", "--id", "x2", "--layer", "nope")
        self.assertNotEqual(rc, 0)
        self.assertFalse(T.path_of(self.repo, "x2").exists())

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

    def test_check_cli_rejects_a_bogus_weight(self):
        T.save(self.repo, good("B2", state="refined", weight="BOGUS"))
        rc, out = self.run_cli("check", "B2")
        self.assertIn("NOT READY", out)
        self.assertIn("BOGUS", out)
        self.assertEqual(T.get(self.repo, "B2")["state"], "refined")

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

    def test_ready_card_closes_without_take_when_every_gate_passes(self):
        T.save(self.repo, good("B1"))
        rc, out = self.run_cli("done", "B1", "--result", "28 rows")
        self.assertEqual(rc, 0, out)
        c = T.get(self.repo, "B1")
        self.assertEqual(c["state"], "done")
        self.assertTrue(c["taken"])

    def test_ready_card_that_fails_a_gate_does_not_close(self):
        T.save(self.repo, good("B1", goal=""))
        rc, out = self.run_cli("done", "B1", "--result", "x")
        self.assertNotEqual(rc, 0)
        self.assertEqual(T.get(self.repo, "B1")["state"], "ready")
        T.save(self.repo, good("B2", state="refined"))
        rc, _ = self.run_cli("done", "B2", "--result", "x")
        self.assertNotEqual(rc, 0)

    def test_check_all_demotes_a_ready_card_that_regressed(self):
        T.save(self.repo, good("B1", goal=""))
        rc, _ = self.run_cli("check", "--demote")
        self.assertEqual(rc, 1)
        self.assertEqual(T.get(self.repo, "B1")["state"], "refined")

    def test_one_raw_card_two_hours_old_with_five_ready_is_refine_needed(self):
        made = datetime(2026, 10, 23, 10, 0, tzinfo=timezone.utc)
        T.save(self.repo, good("B1", state="raw", created="2026-10-23T10:00:00Z"))
        for i in range(5):
            T.save(self.repo, good(f"R{i}"))
        cards = T.load_all(self.repo)
        self.assertTrue(T.status_line(cards, made + timedelta(hours=2)).startswith("REFINE_NEEDED"))
        self.assertTrue(T.status_line(cards, made + timedelta(minutes=30)).startswith("REFINE_OK"))   # too young

    def test_fresh_raw_card_with_empty_builder_stock_is_refine_needed_at_once(self):
        """The 1 h age rule alone left an empty queue idle for an hour."""
        made = datetime(2026, 10, 23, 10, 0, tzinfo=timezone.utc)
        T.save(self.repo, good("B1", state="raw", created="2026-10-23T10:00:00Z"))
        cards = T.load_all(self.repo)
        self.assertTrue(T.status_line(cards, made + timedelta(minutes=5)).startswith("REFINE_NEEDED"))
        self.assertEqual([c["id"] for c in T.refine_due(cards, made + timedelta(minutes=5))], ["B1"])

    def test_old_refined_card_with_empty_builder_stock_is_refine_needed(self):
        """A refined card (past raw, not yet ready) still wakes the refiner when builders run dry."""
        T.save(self.repo, good("B1", state="refined", created="2020-01-01T00:00:00Z"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))

    def test_no_raw_cards_is_refine_ok(self):
        for i in range(5):
            T.save(self.repo, good(f"R{i}"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_OK"))
        for i in range(5):
            (self.repo / T.DIR / f"R{i}.json").unlink()
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_OK"))   # nothing at all

    def test_parked_raw_card_does_not_trigger_refine_needed(self):
        T.save(self.repo, good("B1", state="raw", created="2020-01-01T00:00:00Z", asks="Which year?"))
        line = T.status_line(T.load_all(self.repo))
        self.assertTrue(line.startswith("REFINE_OK"), line)
        self.assertIn("parked=1", line)

    def test_ready_run_lane_cards_do_not_fill_the_builder_buffer(self):
        T.save(self.repo, good("B1", state="raw", created="2020-01-01T00:00:00Z"))
        for i in range(3):
            T.save(self.repo, good(f"D{i}", lane="DSA-NB"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))

    def test_parked_cards_do_not_keep_the_refiner_firing(self):
        """The brake: a card the refiner cannot finish must not start a session every dispatcher tick."""
        T.save(self.repo, good("B1", state="raw", goal="", created="2020-01-01T00:00:00Z"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))
        self.run_cli("tried", "B1")
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))     # 1 of 2 tries used
        rc, out = self.run_cli("tried", "B1")
        self.assertIn("no tries left", out)
        line = T.status_line(T.load_all(self.repo))
        self.assertTrue(line.startswith("REFINE_OK"), line)
        self.assertIn("parked=1", line)
        self.run_cli("apply-op", "B1", "retry")                                              # operator answered: back in play
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))

    def test_asking_the_operator_parks_at_once_and_ready_clears_the_question(self):
        T.save(self.repo, good("B1", state="refined", goal=""))
        self.run_cli("tried", "B1", "--asks", "Which year is the holdout?")
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_OK"))
        row = T.summary(self.repo)["rows"][0]
        self.assertEqual((row["parked"], row["asks"]), (True, "Which year is the holdout?"))
        c = T.get(self.repo, "B1")
        c.update(goal="holdout 2025", asks="", refine_tries=0)
        T.save(self.repo, c)
        self.run_cli("check", "B1")
        self.assertEqual((T.get(self.repo, "B1")["state"], T.get(self.repo, "B1")["asks"]), ("ready", ""))

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

    def test_sweep_archive_moves_closed_cards_and_keeps_them_resolvable(self):
        T.save(self.repo, good("C1"))
        T.save(self.repo, good("C2"))
        self.run_cli("apply-op", "C2", "drop")
        self.run_cli("sweep", "--archive")
        self.assertTrue((T.tdir(self.repo) / "C2.json").exists())          # dry run moves nothing
        self.run_cli("sweep", "--archive", "--apply")
        self.assertFalse((T.tdir(self.repo) / "C2.json").exists())
        self.assertTrue((T.tdir(self.repo) / "archive" / "C2.json").exists())
        self.assertTrue((T.tdir(self.repo) / "C1.json").exists())
        self.assertEqual(T.get(self.repo, "C2")["state"], "dropped")
        self.assertIn("C2", [c["id"] for c in T.load_all(self.repo)])

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


class NextSkipsClaimedTest(unittest.TestCase):
    """`tasks.py next` hides a card that holds an open claim on origin/fast-track (NEXT_SESSION: "skips claimed"). The claim is the
    lock (sync.py): a session that took the first line anyway died in `sync.py claim` with 'already claimed' (b172-trim, 2026-10-14)."""
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name).resolve()  # git calls an 8.3 short TEMP path (E-NGIN~1) "outside repository"
        self._repo = T.REPO
        T.REPO = self.repo
        self.git("init", "-q")

    def tearDown(self):
        T.REPO = self._repo
        self.d.cleanup()

    def git(self, *a):
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(self.repo), *a], check=True, capture_output=True)

    def claim(self, slug, host="JIS-NUC", account="sharma"):
        """A claim file as sync.py writes it, committed and visible as origin/fast-track (what read_claims reads)."""
        p = self.repo / "MyTradingSys" / "system" / "claims" / f"{slug}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(chr(10).join([f"task: {slug}", f"host: {host}", f"account: {account}", "area: -", "epoch: 1", ""]), encoding="utf-8", newline=chr(10))
        self.git("add", str(p))
        self.git("commit", "-q", "-m", f"claim {slug}")
        self.git("update-ref", "refs/remotes/origin/fast-track", "HEAD")

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            try:
                rc = T.main(list(argv))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
        return rc, out.getvalue()

    def test_next_skips_a_card_with_an_open_claim(self):
        T.save(self.repo, good("B1", prio=1))   # claim files are lower-case slugs of the id (sync.slugify)
        T.save(self.repo, good("B2", prio=2))
        self.claim("b1")
        rc, out = self.run_cli("next")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.splitlines(), ["B2 [SONNET, S, p2] Run the 28 cells"])

    def test_next_n_counts_only_the_cards_a_session_can_take(self):
        for i in (1, 2, 3):
            T.save(self.repo, good(f"B{i}", prio=i))
        self.claim("b1")
        rc, out = self.run_cli("next", "--n", "1")
        self.assertEqual([ln.split()[0] for ln in out.splitlines()], ["B2"])

    def test_next_all_lists_the_claimed_card_with_its_owner(self):
        T.save(self.repo, good("B1", prio=1))
        T.save(self.repo, good("B2", prio=2))
        self.claim("b1", host="JIS-NUC", account="sharma")
        rc, out = self.run_cli("next", "--all")
        lines = out.splitlines()
        self.assertEqual(rc, 0, out)
        self.assertEqual(lines[0], "B1 [SONNET, S, p1] Run the 28 cells (claimed by JIS-NUC/sharma)")
        self.assertEqual(lines[1], "B2 [SONNET, S, p2] Run the 28 cells")

    def test_next_with_every_ready_card_claimed_says_so(self):
        T.save(self.repo, good("B1"))
        self.claim("b1")
        rc, out = self.run_cli("next")
        self.assertEqual(rc, 1)
        self.assertIn("NO_READY_CARD", out)
        self.assertIn("1 ready card(s) held by an open claim", out)
        self.assertNotIn("B1 [", out)


class StateTagTest(NextSkipsClaimedTest):
    """TASK_REFINEMENT.md "State tag": a card carries pointers to its latest ship/report/audit; stale pointers are named, and lint
    fails a ready card whose scope changed more than the grace ago without a refresh."""
    def commit(self, rel, text, when="2026-10-01T00:00:00+00:00", msg=None):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline=chr(10))
        self.git("add", rel)
        env = {**__import__("os").environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(self.repo), "commit", "-q", "-m", msg or f"edit {rel}"],
                       check=True, capture_output=True, env=env)

    def card(self, **kw):
        c = good("TS1", scope_in=["src/a.py (the module)"], refs=["B900"])
        c.update(kw)
        T.save(self.repo, c)
        return c

    def test_tag_refresh_records_ship_and_audit_pointers(self):
        self.commit("src/a.py", "x=1" + NL, msg="a: first")
        self.commit("MyTradingSys/research/B900_audit.md", "# audit" + NL, "2026-10-02T00:00:00+00:00", "audit B900")
        self.card()
        rc, out = self.run_cli("tag", "TS1", "--refresh")
        self.assertEqual(rc, 0)
        self.assertIn("STATE READY", out)
        self.assertIn("LATEST ship", out)
        self.assertIn("LATEST audit MyTradingSys/research/B900_audit.md", out)
        c = T.get(self.repo, "TS1")
        self.assertTrue(c["refreshed"] and c["scope_sha"])

    def test_scope_change_makes_card_stale_and_refresh_clears_it(self):
        self.commit("src/a.py", "x=1" + NL)
        self.card()
        self.run_cli("tag", "TS1", "--refresh")
        self.assertEqual(self.run_cli("stale")[0], 0)
        self.commit("src/a.py", "x=2" + NL, "2026-10-02T00:00:00+00:00")
        rc, out = self.run_cli("stale")
        self.assertEqual(rc, 1)
        self.assertIn("scope changed", out)
        self.assertIn("STATE STALE:scope changed", self.run_cli("tag", "TS1")[1])
        rc, out = self.run_cli("stale", "--refresh")
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_cli("stale")[0], 0)

    def test_lint_only_warns_about_stale_ready_cards(self):
        """A stale pointer is reported, never fatal: lint feeds the ship gate and trunk CI, which every session shares."""
        self.commit("src/a.py", "x=1" + NL)
        self.card()
        rc, out = self.run_cli("lint")
        self.assertEqual(rc, 0)          # never refreshed
        self.assertIn("WARN TS1", out)
        self.assertIn("never refreshed", out)
        self.run_cli("tag", "TS1", "--refresh")
        rc, out = self.run_cli("lint")
        self.assertEqual((rc, "WARN" in out), (0, False))
        self.commit("src/a.py", "x=2" + NL, "2026-10-02T00:00:00+00:00")          # long ago: past the grace
        rc, out = self.run_cli("lint")
        self.assertEqual(rc, 0)
        self.assertIn("scope changed", out)
        self.assertEqual(self.run_cli("stale")[0], 1)          # the explicit command still exits 1
        self.run_cli("stale", "--refresh")
        self.commit("src/a.py", "x=3" + NL, T.now())                              # just now: inside the grace
        self.assertEqual(self.run_cli("lint")[1].count("WARN"), 0)

    def test_shallow_clone_never_reports_stale(self):
        """CI checks out depth 1: git log then names HEAD for every path, so staleness cannot be judged there."""
        import task_state
        self.commit("src/a.py", "x=1" + NL)
        self.card()
        self.run_cli("tag", "TS1", "--refresh")
        self.commit("src/a.py", "x=2" + NL, "2026-10-02T00:00:00+00:00")
        c = T.get(self.repo, "TS1")
        real = task_state.is_shallow
        task_state.is_shallow = lambda repo: True
        try:
            self.assertEqual(task_state.overdue(c, self.repo), "")
            self.assertEqual(task_state.stale_reason(c, self.repo), "")
        finally:
            task_state.is_shallow = real
        self.assertTrue(task_state.overdue(c, self.repo))

    def test_check_promotion_refreshes_and_done_records_ship(self):
        self.commit("src/a.py", "x=1" + NL)
        self.card(state="refined")
        self.run_cli("check", "TS1")
        c = T.get(self.repo, "TS1")
        self.assertEqual(c["state"], "ready")
        self.assertTrue(c["refreshed"])
        c["state"] = "active"
        T.save(self.repo, c)
        self.run_cli("done", "TS1", "--result", "9 rows")
        c = T.get(self.repo, "TS1")
        self.assertEqual(c["latest"][0]["kind"], "ship")
        self.assertIn("9 rows", c["latest"][0]["line"])
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "ship TS1")
        self.assertRegex(self.run_cli("tag", "TS1")[1], r"STATE SHIPPED@[0-9a-f]+")

    def test_manual_pointer_survives_refresh_and_brief_prints_latest(self):
        self.commit("src/a.py", "x=1" + NL)
        self.card()
        self.run_cli("tag", "TS1", "--add", "decision:MyTradingSys/system/CONTROL_ROOM.md", "--line", "operator chose X")
        self.run_cli("tag", "TS1", "--refresh")
        rc, out = self.run_cli("brief", "TS1")
        self.assertEqual(rc, 0)
        self.assertIn("LATEST decision MyTradingSys/system/CONTROL_ROOM.md", out)
        self.assertIn("LATEST ship", out)


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

    def test_sized_open_model_cards_carry_worker_fields(self):
        """card-worker-fields: an open SONNET/HAIKU/OPUS card with a size also has worker and est_turns (WORKERS.md)."""
        for c in T.load_all(T.REPO):
            if c["state"] in ("done", "dropped") or c.get("lane") not in ("SONNET", "HAIKU", "OPUS") or not c.get("size"):
                continue
            with self.subTest(card=c["id"]):
                self.assertTrue(c.get("worker") and c.get("est_turns"))



class LabMachineChecksTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name)
        self._repo = T.REPO
        self._runs = T.RUNS_JSONL
        T.REPO = self.repo
        T.RUNS_JSONL = self.repo / "runs.jsonl"
        formula = self.repo / T.FORMULAS
        formula.parent.mkdir(parents=True)
        formula.write_text("## 1. Example\n## 2. Other\n", encoding="utf-8")
        (self.repo / T.TRIALS).parent.mkdir(parents=True)
        (self.repo / T.TRIALS).write_text("| date | card | command | data | result |\n|---|---|---|---|---|\n", encoding="utf-8")
        T.RUNS_JSONL.write_text("", encoding="utf-8")

    def tearDown(self):
        T.REPO = self._repo
        T.RUNS_JSONL = self._runs
        self.d.cleanup()

    def test_unknown_formula_id_refused_and_known_id_passes(self):
        self.assertTrue(any("formula id" in e for e in T.problems(good(formula_ids=["s999"]))))
        self.assertEqual(T.problems(good(formula_ids=["s1"])), [])

    def test_run_trial_count_must_match_runner_rows(self):
        import json
        card = good(lane="CODEX", kind="run", formula_ids=[], commands=["python study.py"])
        (self.repo / T.TRIALS).write_text("| date | card | command | data | result |\n|---|---|---|---|---|\n| 2026-01-01 | B900 | cmd | DEV | ok |\n", encoding="utf-8")
        T.RUNS_JSONL.write_text("", encoding="utf-8")
        self.assertTrue(any("trial-ledger count" in e for e in T.problems(card)))
        T.RUNS_JSONL.write_text(json.dumps({"card": "B900"}) + "\n", encoding="utf-8")
        self.assertEqual(T.problems(card), [])

    def test_run_accounting_is_skipped_when_the_lab_host_file_is_absent(self):
        # CI runners and other machines have no F:/codex_home; a missing runs.jsonl must not fail every CODEX run card (CI red 2026-10-17)
        card = good(lane="CODEX", kind="run", formula_ids=[], commands=["python study.py"])
        T.RUNS_JSONL.unlink()
        self.assertEqual(T.problems(card), [])

    def test_save_of_citing_card_leaves_cited_card_bytes_untouched(self):
        source = good("BASE1")
        citing = good("USE1", scope_in=["BASE1 results.md"])
        T.save(self.repo, source)
        before = T.path_of(self.repo, "BASE1").read_bytes()
        T.save(self.repo, citing)
        self.assertEqual(T.path_of(self.repo, "BASE1").read_bytes(), before)
        self.assertNotEqual(T.get(self.repo, "BASE1")["weight"], "B-SHARED")

    def test_promote_shared_still_marks_when_called_explicitly(self):
        T.save(self.repo, good("BASE1"))
        T.save(self.repo, good("USE1", scope_in=["BASE1 results.md"]))
        T.promote_shared(self.repo)
        self.assertEqual(T.get(self.repo, "BASE1")["weight"], "B-SHARED")

    def test_build_requires_a_dummy_or_shuffled_output_mutation_probe(self):
        card = good(lane="CODEX", kind="build", mutation_check="")
        self.assertTrue(any("mutation_check" in e for e in T.problems(card)))
        probe = self.repo / "scripts/dev/test_mutation.py"
        probe.parent.mkdir(parents=True)
        probe.write_text("def test_dummy_output_rejected():\n    assert output != 'dummy'\n", encoding="utf-8")
        card["mutation_check"] = "scripts/dev/test_mutation.py::test_dummy_output_rejected"
        self.assertEqual(T.problems(card), [])
        probe.write_text("def test_dummy_output_rejected():\n    assert output == 'normal'\n", encoding="utf-8")
        self.assertTrue(any("assert rejection" in e for e in T.problems(card)))


class ReviewGateTest(unittest.TestCase):
    def test_malformed_note_class_fails_closed(self):
        for note in ('class C2', 'class=2', 'class: 2', 'class: C 2',
                     'class:C-2', 'Class: **C2**', 'class: "C2"', 'class=Cx'):
            with self.subTest(note=note):
                self.assertEqual(T.card_class(good(note=note)), 'C3')
                self.assertTrue(T.review_gate(good(note=note)))
        for value in ([], {}, False, 0, ['class=C2']):
            with self.subTest(value=value):
                self.assertTrue(T.review_gate(good(note=value)))
        for value in ('C9', 'wat', [], {}, False, 0):
            with self.subTest(field=value):
                self.assertEqual(T.card_class(good(**{'class': value})), 'C3')
                self.assertTrue(T.review_gate(good(**{'class': value})))

    def test_weight_and_live_path_malformed_values_fail_closed(self):
        self.assertEqual(T.needs_review(good(weight=' IMPORTANT ')), 'soft')
        for weight in (' CRUCIAL', 'CRUCIAL ', 'critical', ['CRUCIAL'], {}, 1, False):
            with self.subTest(weight=weight):
                self.assertTrue(T.review_gate(good(weight=weight), True, 'evidence'))
        for live in ('true', 'false', 1, 0, [], {}):
            with self.subTest(live=live):
                self.assertTrue(T.review_gate(good(live_path=live), True, 'evidence'))
        # Malformed data cannot be rescued by a syntactically valid stamp.
        self.assertTrue(T.review_gate(good(weight=['CRUCIAL'], note='REVIEWED: Argon 2026-10-18')))
        self.assertTrue(T.review_gate(good(weight='BOGUS', note='REVIEWED: Argon 2026-10-18')))
        for key, value in (('note', []), ('class', []), ('weight', []), ('live_path', 'true')):
            c = good(**{key: value})
            c['review_receipt'] = T.make_review_receipt(c, 'Argon')
            self.assertTrue(T.review_gate(c), key)

    def test_each_producer_identity_independently_rejects_own_review(self):
        for key in ('producer', 'producer_model', 'vendor', 'model', 'worker', 'refined_by', 'author'):
            for note in ('REVIEWED: Argon 2026-10-18', 'REVIEWED:2026-10-18 ACCEPT reviewer=Argon'):
                with self.subTest(key=key, note=note):
                    c = good(weight='CRUCIAL', note=note, **{key: ' Argon '})
                    self.assertEqual(T.stamp_kind(c), '')
            c = good(weight='CRUCIAL', **{key: ' Argon '})
            c['review_receipt'] = T.make_review_receipt(c, 'Argon')
            self.assertEqual(T.stamp_kind(c), '', key)
        self.assertEqual(T.stamp_kind(good(weight='CRUCIAL', note='REVIEWED: Argon 2026-10-18', producer='Other')), 'real')

    def test_dates_anchors_case_and_single_line_independently(self):
        for note in ('REVIEWED: Argon 2026-13-45', 'REVIEWED:2026-13-45 ACCEPT',
                     'quoted REVIEWED:2026-10-18 ACCEPT',
                     'REVIEWED:\n2026-10-18 ACCEPT', 'REVIEWED:\nArgon 2026-10-18',
                     'REVIEWED: Argon\n2026-10-18', 'REVIEWED:2026-10-18\nACCEPT'):
            with self.subTest(note=note):
                self.assertEqual(T.stamp_kind(good(note=note)), '')
        self.assertEqual(T.stamp_kind(good(note='preamble\nREVIEWED: Argon 2026-10-18')), 'real')
        self.assertEqual(T.card_class(good(**{'class': 'c2'})), 'C2')
        self.assertEqual(T.card_class(good(note='class=C0 class=C3')), 'C3')
        self.assertTrue(T.review_gate(good(weight='critical')))
        self.assertEqual(T.needs_review(good(weight='important')), 'soft')

    def test_forged_stamp_forms_are_rejected(self):
        forged = (
            "REVIEWED: <reviewer> 2026-10-18",
            "REVIEWED: producer 2026-10-18",
            "REVIEWED: self 2026-10-18",
            "REVIEWED: x 2026-13-45",
            "TODO: need REVIEWED: Argon 2026-10-18 first",
        )
        for note in forged:
            with self.subTest(note=note):
                self.assertTrue(T.review_gate(good(weight="CRUCIAL", note=note)), note)

    def test_class_field_cannot_downgrade_note_class(self):
        card = good(weight="ROUTINE", **{"class": "C0"}, note="class=C3")
        self.assertTrue(T.review_gate(card))
        for malformed in ("class = C2", "class: C2", "class=C10"):
            with self.subTest(note=malformed):
                self.assertTrue(T.review_gate(good(weight="ROUTINE", note=malformed)))

    def test_whitespace_receipt_is_rejected(self):
        card = good(weight="CRUCIAL", note="REVIEWED: Argon 2026-10-18")
        self.assertTrue(any("receipt" in e for e in T.review_gate(card, True, "   ")))

    def test_done_requires_ready_or_active_state(self):
        d = tempfile.TemporaryDirectory()
        repo = Path(d.name)
        previous = T.REPO
        T.REPO = repo
        try:
            T.save(repo, good("STATE1", state="refined"))
            rc, out = run_cli("done", "STATE1", "--result", "receipt")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("only a ready or active", out)
            self.assertEqual(T.get(repo, "STATE1")["state"], "refined")
        finally:
            T.REPO = previous
            d.cleanup()

    def test_sweep_cannot_close_hard_card_without_real_review(self):
        d = tempfile.TemporaryDirectory()
        repo = Path(d.name)
        previous = T.REPO
        T.REPO = repo
        try:
            bugs = repo / T.BUGS
            bugs.parent.mkdir(parents=True)
            bugs.write_text("| ID | Opened | Status | Severity | Title | Evidence | Receipt |\n|---|---|---|---|---|---|---|\n| B900 | 2026-10-01 | CLOSED | MED | t | e | r |\n", encoding="utf-8")
            T.save(repo, good("SWP1", refs=["B900"], weight="CRUCIAL"))
            run_cli("sweep", "--apply")
            self.assertEqual(T.get(repo, "SWP1")["state"], "ready")
        finally:
            T.REPO = previous
            d.cleanup()

    def test_crucial_needs_reviewed_stamp_to_take_and_receipt_to_finish(self):
        c = good(weight="CRUCIAL", note="[PLAN weight=CRUCIAL]")
        self.assertTrue(any("REVIEWED" in e for e in T.review_gate(c)))
        self.assertTrue(any("receipt" in e for e in T.review_gate(dict(c, note="REVIEWED: Argon 2026-10-18"), True, "")))
        self.assertEqual(T.review_gate(dict(c, note="REVIEWED: Argon 2026-10-18"), True, "tests 5/5"), [])

    def test_class_c2_c3_gated_even_with_routine_weight(self):
        self.assertTrue(T.review_gate(good(weight="ROUTINE", note="class=C2")))
        self.assertTrue(T.review_gate(good(weight="IMPORTANT", **{"class": "C3"})))

    def test_routine_important_c0_c1_not_blocked(self):
        for w, n in (("ROUTINE", ""), ("IMPORTANT", "class=C1"), ("", "class=C0")):
            self.assertEqual(T.review_gate(good(weight=w, note=n), True, ""), [])

    def test_reviewed_stamp_requires_reviewer_and_iso_date(self):
        c = good(weight="CRITICAL", note="REVIEWED: reviewer")
        self.assertTrue(T.review_gate(c))
        c["note"] = "REVIEWED: Argon 2026-10-18"
        self.assertEqual(T.review_gate(c), [])

    def test_t0_only_stamp_is_not_a_review_for_crucial(self):
        c = good(weight="CRUCIAL", note="REVIEWED:2026-10-18 T0-ONLY LAB:data CLASS:C1")
        self.assertTrue(T.review_gate(c))
        self.assertEqual(T.review_gate(dict(c, note="REVIEWED:2026-10-18 ACCEPT CLASS:C1")), [])

    def test_planner_class_format_and_live_path_floor(self):
        self.assertEqual(T.card_class(good(note="REVIEWED:2026-10-18 ACCEPT CLASS:C2")), "C2")
        self.assertEqual(T.card_class(good(note="class=C1", live_path=True)), "C3")
        self.assertTrue(T.review_gate(good(weight="IMPORTANT", note="REVIEWED:2026-10-18 T0-ONLY", live_path=True)))

    def test_promotion_needs_real_review_for_important_and_c1(self):
        t0 = good(weight="IMPORTANT", note="REVIEWED:2026-10-18 T0-ONLY CLASS:C1")
        self.assertTrue(T.promotion_problems(t0, holds=()))
        self.assertEqual(T.promotion_problems(dict(t0, note="REVIEWED:2026-10-18 ACCEPT CLASS:C1"), holds=()), [])
        self.assertEqual(T.promotion_problems(good(weight="ROUTINE", note="REVIEWED:2026-10-18 T0-ONLY"), holds=()), [])

    def test_active_hold_blocks_promotion_until_cleared(self):
        c = good(weight="ROUTINE", note="HOLD A-20261018-5: reads unchecked base")
        self.assertTrue(T.promotion_problems(c, holds={"A-20261018-5"}))
        self.assertEqual(T.promotion_problems(c, holds=()), [])
        self.assertEqual(T.promotion_problems(dict(c, note=c["note"] + " HOLD-CLEARED A-20261018-5"), holds={"A-20261018-5"}), [])

    def test_cli_take_and_done_refuse_unreviewed_crucial_card(self):
        d = tempfile.TemporaryDirectory()
        repo = Path(d.name)
        previous = T.REPO
        T.REPO = repo
        try:
            c = good("GATE1", weight="CRUCIAL", note="[PLAN weight=CRUCIAL]")
            T.save(repo, c)
            rc, out = run_cli("take", "GATE1", "--claim", "slug")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("REVIEWED", out)
            self.assertEqual(T.get(repo, "GATE1")["state"], "ready")
            active = T.get(repo, "GATE1")
            active["state"] = "active"
            T.save(repo, active)
            rc, out = run_cli("done", "GATE1", "--result", "receipt")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("REVIEWED", out)
            self.assertEqual(T.get(repo, "GATE1")["state"], "active")
        finally:
            T.REPO = previous
            d.cleanup()

    def test_cli_done_requires_receipt_for_reviewed_c2(self):
        d = tempfile.TemporaryDirectory()
        repo = Path(d.name)
        previous = T.REPO
        T.REPO = repo
        try:
            T.save(repo, good("GATE2", state="active", weight="ROUTINE", note="class=C2 REVIEWED: reviewer 2026-10-18"))
            rc, out = run_cli("done", "GATE2", "--result", "")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("receipt", out)
            self.assertEqual(T.get(repo, "GATE2")["state"], "active")
        finally:
            T.REPO = previous
            d.cleanup()


class ResultTrustTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / 'base.py').write_text('v1\n', encoding='utf-8')
        (self.repo / 'data.csv').write_text('t,x\n1,2\n', encoding='utf-8')
        (self.repo / 'proof.md').write_text('independent check\n', encoding='utf-8')
        self.base = good('BASE', state='done', scope_in=['base.py', 'data.csv'])
        T.save(self.repo, self.base)
        self.consumer = good('USE', scope_in=['card:BASE'], **{'class': 'C1'})

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self, tag='VERIFIED-C1'):
        self.base['result_receipt'] = {'trust': T.make_result_trust(
            self.base, tag, 'independent-model', 'medium', 'proof.md', repo=self.repo)}
        T.save(self.repo, self.base)

    def test_unchecked_refused_verified_c1_allowed(self):
        self.assertTrue(T.result_trust_problems(self.consumer, self.repo))
        self.verify()
        self.assertEqual(T.result_trust_problems(self.consumer, self.repo), [])
        self.assertTrue(T.result_trust_problems(dict(self.consumer, **{'class': 'C2'}), self.repo))
        self.verify('VERIFIED-C2')
        self.assertEqual(T.result_trust_problems(dict(self.consumer, **{'class': 'C2'}), self.repo), [])

    def test_trust_expires_on_data_code_or_evidence_change(self):
        for file in ('base.py', 'data.csv', 'proof.md'):
            with self.subTest(file=file):
                self.verify()
                path = self.repo / file
                original = path.read_bytes()
                path.write_bytes(original + b'changed\n')
                self.assertTrue(T.result_trust_problems(self.consumer, self.repo))
                path.write_bytes(original)

    def test_disputed_missing_malformed_or_weak_trust_fails_closed(self):
        for tag in ('UNCHECKED', 'MACHINE-OK', 'DISPUTED'):
            self.verify(tag)
            self.assertTrue(T.result_trust_problems(self.consumer, self.repo))
        self.verify()
        for field in ('checker_model', 'effort', 'date', 'data_hash', 'code_revision', 'evidence'):
            original = dict(self.base['result_receipt']['trust'])
            self.base['result_receipt']['trust'][field] = ''
            T.save(self.repo, self.base)
            self.assertTrue(T.result_trust_problems(self.consumer, self.repo), field)
            self.base['result_receipt']['trust'] = original
        self.assertTrue(T.result_trust_problems(good(scope_in=['card:MISSING']), self.repo))

    def test_citation_marks_base_shared_without_query_side_effects(self):
        self.verify()
        T.result_trust_problems(self.consumer, self.repo)
        self.assertEqual(T.get(self.repo, 'BASE')['weight'], '')
        T.mark_shared_bases(self.consumer, self.repo)
        shared = T.get(self.repo, 'BASE')
        self.assertEqual(shared['weight'], 'B-SHARED')
        self.assertEqual(T.card_class(shared), 'C2')
        self.assertEqual(shared['shared_consumers'], ['USE'])
        self.assertEqual(T.result_trust_problems(self.consumer, self.repo), [])

    def test_take_and_active_done_enforce_result_trust(self):
        previous = T.REPO
        T.REPO = self.repo
        try:
            T.save(self.repo, self.consumer)
            rc, out = run_cli('take', 'USE')
            self.assertNotEqual(rc, 0, out)
            self.consumer['state'] = 'active'
            T.save(self.repo, self.consumer)
            rc, out = run_cli('done', 'USE', '--result', 'evidence')
            self.assertNotEqual(rc, 0, out)
            self.assertEqual(T.get(self.repo, 'USE')['state'], 'active')
        finally:
            T.REPO = previous

    def test_directory_input_cannot_get_a_false_verified_pin(self):
        (self.repo / 'data_dir').mkdir()
        self.base['scope_in'] = ['data_dir/']
        with self.assertRaisesRegex(ValueError, 'explicit file'):
            self.verify()

    def test_no_data_result_and_flow_data_scope_are_bound(self):
        self.base['scope_in'] = ['base.py']
        self.verify()
        self.assertEqual(T.result_trust_problems(self.consumer, self.repo), [])
        self.base['flow'] = {'data_scope': ['data.csv']}
        self.base['flow_receipt'] = {'trust': T.make_result_trust(
            self.base, 'VERIFIED-C1', 'independent-model', 'medium', 'proof.md', repo=self.repo)}
        T.save(self.repo, self.base)
        self.assertEqual(T.result_trust_problems(self.consumer, self.repo), [])
        (self.repo / 'data.csv').write_text('changed', encoding='utf-8')
        self.assertTrue(T.result_trust_problems(self.consumer, self.repo))

    def test_flow_ready_and_active_close_require_trusted_base(self):
        import lab_flow
        for state in ('ready', 'active'):
            c = dict(self.consumer, state=state, flow={'id': 'test-flow'})
            T.save(self.repo, c)
            with self.assertRaisesRegex(ValueError, 'UNCHECKED'):
                lab_flow.finish(self.repo, 'USE', 'missing.md', 'PASS', 'receipt')
            self.assertEqual(T.get(self.repo, 'USE')['state'], state)

    def test_card_file_citation_and_changed_upstream_receipt_expire(self):
        self.verify('VERIFIED-C2')
        consumer = dict(self.consumer, scope_in=['MyTradingSys/system/tasks/BASE.json'])
        self.assertEqual(T.result_trust_problems(consumer, self.repo), [])
        self.base['result_receipt']['trust']['tag'] = 'DISPUTED'
        T.save(self.repo, self.base)
        self.assertTrue(T.result_trust_problems(consumer, self.repo))

    def test_transitive_input_change_is_not_hidden_by_unchanged_card_json(self):
        root = good('ROOT', state='done', scope_in=['base.py'])
        root['result_receipt'] = {'trust': T.make_result_trust(
            root, 'VERIFIED-C2', 'independent-model', 'high', 'proof.md', repo=self.repo)}
        T.save(self.repo, root)
        self.base['scope_in'] = ['card:ROOT']
        self.verify()
        self.assertEqual(T.result_trust_problems(self.consumer, self.repo), [])
        (self.repo / 'base.py').write_text('new input code', encoding='utf-8')
        self.assertTrue(T.result_trust_problems(self.consumer, self.repo))

    def test_declared_flow_risk_class_requires_matching_result_trust(self):
        self.verify()
        consumer = dict(self.consumer, **{'class': 'C0'}, flow={'risk_class': 'C2'})
        self.assertTrue(T.result_trust_problems(consumer, self.repo))

    def test_flow_finish_defaults_to_unchecked_without_claiming_verification(self):
        # The normal finish contract is tested in test_lab_flow; assert its receipt
        # default here through the same fixture helpers, without a model call.
        import lab_flow
        previous = T.REPO
        T.REPO = self.repo
        try:
            (self.repo / 'source.md').write_text('source', encoding='utf-8')
            spec = {'id': 'trust-default', 'recipe': 'critical-audit', 'goal': 'check',
                    'criteria': ['source checked'], 'scope_in': ['source.md']}
            c = lab_flow.launch(self.repo, spec)[0]
            proof = self.repo / T.LAB_REPORTS / 'flow.md'
            proof.parent.mkdir(parents=True, exist_ok=True)
            proof.write_text(c['id']+'\nC1: PASS\nsource.md:1\n', encoding='utf-8')
            done = lab_flow.finish(self.repo, c['id'], str(proof.relative_to(self.repo)), 'PASS', 'evidence')
            self.assertEqual(done['flow_receipt']['trust'], {'tag': 'UNCHECKED'})
        finally:
            T.REPO = previous


if __name__ == "__main__":
    unittest.main()


class NeedTest(unittest.TestCase):
    """Operator 2026-10-22: pre-run items live in the queue (tasks.py need), not in the operator's head."""
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name)
        self._repo = T.REPO
        T.REPO = self.repo
        T.save(self.repo, good("main-card"))

    def tearDown(self):
        T.REPO = self._repo
        self.d.cleanup()

    def test_need_makes_an_owned_prereq_card_and_blocks_the_main_card(self):
        rc, _ = run_cli("need", "main-card", "Lab_Guy review stamp", "--lane", "SONNET", "--role", "Lab_Guy")
        self.assertEqual(rc, 0)
        main = T.get(self.repo, "main-card")
        nid = "main-card-need-lab-guy-review-stamp"
        self.assertEqual(main["depends_on"], [nid])
        pre = T.get(self.repo, nid)
        self.assertEqual((pre["lane"], pre["role"], pre["state"]), ("SONNET", "Lab_Guy", "raw"))
        self.assertTrue(any(p.startswith("depends_on " + nid) for p in T.problems(main, T.load_all(self.repo), {})))
        run_cli("need", "main-card", "Lab_Guy review stamp", "--lane", "SONNET")   # idempotent
        self.assertEqual(T.get(self.repo, "main-card")["depends_on"], [nid])

    def test_need_without_lane_is_refused(self):
        rc, out = run_cli("need", "main-card", "stamp it")
        self.assertNotEqual(rc, 0)
        self.assertIn("--lane", out)

    def test_host_pin_excludes_other_machines_and_shows_in_brief(self):
        run_cli("need", "main-card", "--host", "JIS-NB", "--host", "DESKTOP-F7IU69N")
        c = T.get(self.repo, "main-card")
        self.assertEqual(c["hosts"], ["DESKTOP-F7IU69N", "JIS-NB"])
        self.assertIn("Host: run only on DESKTOP-F7IU69N or JIS-NB", T.brief(c))
        lane_st = {"status": "up"}
        from datetime import datetime, timezone
        now = datetime(2026, 10, 22, tzinfo=timezone.utc)
        args = ([c], {}, [], {}, lane_st, now)
        self.assertEqual(T.exclusion(c, *args[:5], now, "JIS-NUC", self.repo)[0], "host")
        self.assertIsNone(T.exclusion(c, *args[:5], now, "JIS-NB", self.repo))


class TwinCardTest(unittest.TestCase):
    """Doctor 2026-10-23: two sessions filed one job as doctor-main-checkout-behind and jis-nb-fast-forward-the-main-checkout-to."""
    REAL_A = ("Main checkout is 102 commits behind origin/fast-track so every session runs stale settings.json/turn_meter.py; "
              "find why it does not auto-pull and fix (coordinator pulls ff-only)")
    REAL_B = ("JIS-NB: fast-forward the main checkout to origin/fast-track so PC hooks run the event-turn guard (f47d4cae7) "
              "and BOOT probe")
    OTHERS = ["Trust re-check: lab-data-pin-hash", "Trust re-check: lab-dax-net-fee-verdict", "Krown pre-registration fire counts",
              "Wire real funding into the RSI backtest rerun", "Gemini queue reads results back after each run",
              "CI windows leg on a dev drive", "Fabio v3 grid fixtures for the lookahead lint", "Session levels for WLOW fixtures",
              "Refresh the stale layer map page after a ship", "Codex spend guard counts 151 of 65 points on 3 runs"]

    def cards(self):
        out = [T.blank("a", self.REAL_A), T.blank("b", self.REAL_B)]
        out += [T.blank(f"o{i}", t) for i, t in enumerate(self.OTHERS)]
        out[0]["created"], out[1]["created"] = "2026-10-22T22:48:51Z", "2026-10-23T03:39:15Z"   # the real pair, 5 h apart
        for i, c in enumerate(out[2:]):
            c["created"] = f"2026-10-{10 + i:02d}T00:00:00Z"                                    # one per day: no batches
        return out

    def test_one_sessions_batch_is_not_a_twin(self):
        cs = self.cards() + [T.blank("c", "Codex spend guard counts 151 of 65 points on 3 runs")]
        for gap, flagged in (("00:00:00", False), ("00:30:00", False), ("00:31:00", True)):
            cs[-1]["created"] = f"2026-10-19T{gap}Z"                                         # o9 was created 2026-10-19T00:00Z
            self.assertEqual(("o9", "c") in self.ids(cs, only="c"), flagged, gap)
        cs[-1]["created"] = "?"                                                           # no usable time: no silence
        self.assertIn(("o9", "c"), self.ids(cs, only="c"))
        cs[0]["created"] = "2026-10-23T03:20:00Z"                                         # the real pair, if filed 19 min apart
        self.assertNotIn(("a", "b"), self.ids(cs))

    def ids(self, cards, **kw):
        return {(x, y) for _, x, y, _ in T.twin_pairs(cards, **kw)}

    def test_the_real_pair_is_a_twin_and_a_series_is_not(self):
        got = self.ids(self.cards())
        self.assertIn(("a", "b"), got)
        self.assertNotIn(("o0", "o1"), got)          # "Trust re-check: X" siblings differ in X
        self.assertEqual(got, {("a", "b")})

    def test_same_title_is_a_twin(self):
        cs = self.cards() + [T.blank("c", "Codex spend guard counts 151 of 65 points on 3 runs")]
        self.assertEqual(self.ids(cs, only="c"), {("o9", "c")})

    def test_two_shared_rare_files_make_a_twin_but_a_file_and_its_test_do_not(self):
        cs = self.cards()
        cs[2]["scope_in"] = ["scripts/dev/shot.py", "scripts/dev/test_shot.py"]
        cs[3]["scope_in"] = ["scripts/dev/shot.py", "MyTradingSys/tests/test_shot.py"]
        self.assertNotIn(("o0", "o1"), self.ids(cs))
        cs[2]["refs"] = ["MyTradingSys/research/x/SPEC.md"]
        cs[3]["refs"] = ["MyTradingSys/research/x/SPEC.md"]
        self.assertIn(("o0", "o1"), self.ids(cs))

    def test_a_path_many_cards_share_is_not_evidence(self):
        cs = self.cards()
        for c in cs[2:7]:
            c["refs"] = ["MyTradingSys/research/x/SPEC.md", "MyTradingSys/research/x/FRAMING.md"]
        self.assertEqual(self.ids(cs), {("a", "b")})

    def test_not_twin_of_depends_on_and_final_cards_silence_a_pair(self):
        for change in ({"not_twin_of": ["b"]}, {"depends_on": ["b"]}, {"state": "dropped"}):
            cs = self.cards()
            cs[0].update(change)
            self.assertNotIn(("a", "b"), self.ids(cs), change)

    def test_new_warns_on_a_likely_twin(self):
        with tempfile.TemporaryDirectory() as d:
            repo, old = Path(d), T.REPO
            T.REPO = repo
            try:
                for c in self.cards()[1:]:
                    T.save(repo, c)
                rc, out = run_cli("new", self.REAL_A, "--id", "a")
                self.assertEqual(rc, 0)
                self.assertIn("WARN likely twin of b", out)
                self.assertTrue(T.path_of(repo, "a").exists())        # a warning, not a refusal
                rc, out = run_cli("twins")
                self.assertIn("TWIN a b", out)
            finally:
                T.REPO = old
