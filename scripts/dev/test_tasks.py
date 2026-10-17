"""tasks.py: the Definition of Ready is fail closed, ordering and buffer rules, dependency gating, operator actions,
registry sweep, the brief length cap, and a CLI round-trip. Spec: MyTradingSys/system/TASK_REFINEMENT.md."""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
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

    def test_ready_run_lane_cards_do_not_fill_the_builder_buffer(self):
        T.save(self.repo, good("B1", state="raw"))
        for i in range(3):
            T.save(self.repo, good(f"D{i}", lane="DSA-NB"))
        self.assertTrue(T.status_line(T.load_all(self.repo)).startswith("REFINE_NEEDED"))

    def test_parked_cards_do_not_keep_the_refiner_firing(self):
        """The brake: a card the refiner cannot finish must not start a session every dispatcher tick."""
        T.save(self.repo, good("B1", state="raw", goal=""))
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

    def test_cited_scope_automatically_marks_source_b_shared(self):
        source = good("BASE1")
        citing = good("USE1", scope_in=["BASE1 results.md"])
        T.save(self.repo, source)
        T.save(self.repo, citing)
        self.assertEqual(T.get(self.repo, "BASE1")["weight"], "B-SHARED")
        self.assertEqual(T.problems(T.get(self.repo, "BASE1")), [])

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
        c["note"] = "REVIEWED: reviewer 2026-10-18"
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
            rc, out = run_cli("done", "GATE1", "--result", "receipt")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("REVIEWED", out)
            self.assertEqual(T.get(repo, "GATE1")["state"], "ready")
        finally:
            T.REPO = previous
            d.cleanup()

    def test_cli_done_requires_receipt_for_reviewed_c2(self):
        d = tempfile.TemporaryDirectory()
        repo = Path(d.name)
        previous = T.REPO
        T.REPO = repo
        try:
            T.save(repo, good("GATE2", weight="ROUTINE", note="class=C2 REVIEWED: reviewer 2026-10-18"))
            rc, out = run_cli("done", "GATE2", "--result", "")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("receipt", out)
            self.assertEqual(T.get(repo, "GATE2")["state"], "ready")
        finally:
            T.REPO = previous
            d.cleanup()


if __name__ == "__main__":
    unittest.main()
