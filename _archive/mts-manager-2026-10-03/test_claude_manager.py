import json, os, pathlib, sys, tempfile, unittest
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import claude_manager as m


class R:  # fake subprocess result
    returncode = 0; stdout = "done"; stderr = ""


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.calls = []
        self.runner = lambda cmd, **kw: (self.calls.append((cmd, kw["input"])), R())[1]
        self.haiku = lambda p: '{"type":"fix","slug":"alert-rate","split":[]}'

    def usage(self, pct):
        m.cmd_usage(pct, root=self.d)

    def go(self, task="fix alert rate", **kw):
        return m.cmd_go(task, root=self.d, haiku=kw.pop("haiku", self.haiku), runner=self.runner, transcripts="skip")

    def test_tiers(self):
        self.assertEqual([m.tier_of(x) for x in (0, 69.9, 70, 85, 94.9, 95, 100)], ["ok", "ok", "70", "85", "85", "hold", "hold"])

    def test_over_95_refuses_and_queues(self):
        self.usage(96); out = self.go()
        self.assertIn("QUEUED", out); self.assertEqual(self.calls, [])
        self.assertEqual(len(json.load(open(m.paths(self.d)["queue"]))), 1)

    def test_unknown_usage_fails_closed(self):
        out = self.go(); self.assertIn("QUEUED", out); self.assertEqual(self.calls, [])

    def test_resume_releases_after_reset(self):
        self.usage(96); self.go(); self.usage(10)
        out = m.cmd_resume(root=self.d, haiku=self.haiku, runner=self.runner, transcripts="skip")
        self.assertIn("released 1", out); self.assertEqual(len(self.calls), 1)
        self.assertEqual(json.load(open(m.paths(self.d)["queue"])), [])

    def test_resume_blocked_while_over(self):
        self.usage(96); self.go(); self.assertIn("not released", m.cmd_resume(root=self.d))

    def test_routes_without_operator_model(self):
        self.usage(10); self.go()
        self.assertEqual(self.calls[0][0][3], "sonnet")
        self.assertEqual(m.route("safety"), ("opus", "high")); self.assertEqual(m.route("question")[0], "haiku")

    def test_opus_blocked_at_70_unless_safety(self):
        self.assertFalse(m.gate(75, "fix", "opus")[0]); self.assertTrue(m.gate(75, "safety", "opus")[0])
        self.assertFalse(m.gate(88, "build", "sonnet")[0])

    def test_record_before_launch_closed_after_and_log(self):
        self.usage(10)
        def runner(cmd, **kw):
            fs = list(m.paths(self.d)["sessions"].glob("*.md")); assert fs and "status: open" in fs[0].read_text()
            return R()
        m.cmd_go("fix alert rate", root=self.d, haiku=self.haiku, runner=runner, transcripts="skip")
        f = list(m.paths(self.d)["sessions"].glob("*.md"))[0]
        self.assertIn("status: closed rc=0", f.read_text())
        self.assertEqual(m.paths(self.d)["log"].read_text().count("mts-manager"), 1)

    def test_model_log_records_tier(self):
        self.usage(10)
        m.cmd_go("fix alert rate", root=self.d, haiku=self.haiku, runner=self.runner, transcripts="skip")
        fs = list(m.paths(self.d)["sessions"].glob("*.md"))
        rec = fs[0].read_text()
        self.assertIn("tier: ", rec)
        self.assertNotIn("model: ", rec)
        ml = m.paths(self.d)["model_log"]
        self.assertTrue(ml.exists())
        rows = ml.read_text().strip().splitlines()
        self.assertEqual(len(rows), 1)
        r = json.loads(rows[0])
        self.assertTrue(r["tier"])
        self.assertIn("sid", r)
        self.assertEqual(r["rc"], "0")

    def test_split_rules_and_cap(self):
        o = {"type": "fix", "slug": "x", "split": ["a", "b", "c", "d"]}
        self.assertEqual(len(m.plan_children("t", o, "ok")), 3)
        self.assertEqual(m.plan_children("t", o, "85"), ["t"])
        self.assertEqual(m.plan_children("t", dict(o, type="safety"), "ok"), ["t"])
        self.assertEqual(m.plan_children("t", dict(o, split=["a"]), "ok"), ["t"])

    def test_one_log_line_per_child(self):
        self.usage(10)
        h = lambda p: '{"type":"fix","slug":"multi","split":["a","b"]}'
        self.go(haiku=h); self.assertEqual(len(self.calls), 2)
        self.assertEqual(m.paths(self.d)["log"].read_text().count("mts-manager"), 2)

    def test_brief_le_20_lines_and_no_invented_files(self):
        b = m.brief("fix x.py:10-20 now", "fix", "sonnet", "medium", "SID")
        self.assertLessEqual(len(b.splitlines()), 20); self.assertIn("x.py:10-20", b)
        self.assertIn("none named", m.brief("do a thing", "fix", "sonnet", "medium", "SID"))

    def test_intake_fallback_on_haiku_failure(self):
        def bad(p): raise RuntimeError("x")
        self.assertEqual(m.intake("run the backtest", bad)["type"], "backtest")
        self.assertEqual(m.intake("hi?", lambda p: "garbage")["type"], "question")

    def test_dedup_finds_existing_slug(self):
        p = m.paths(self.d); p["sessions"].mkdir(parents=True)
        (p["sessions"] / "MTS-2026-10-01-0000Z-CLI-BLD-alert-rate.md").write_text("status: open`n")
        self.usage(10); self.assertIn("resume-existing", self.go()); self.assertEqual(self.calls, [])

    def test_extraction_routes_to_sonnet(self):
        # 2026-10-01: extraction no longer stages for Qwen; it launches Sonnet.
        self.usage(10); self.go("extract transcript", haiku=lambda p: '{"type":"extraction","slug":"ext1","split":[]}')
        self.assertEqual(len(self.calls), 1)
        self.assertIn("sonnet", " ".join(self.calls[0][0]))
        self.assertEqual(len(list(m.paths(self.d)["handoff"].glob("*.md"))), 0)

    def test_status_line(self):
        self.usage(72); s = m.cmd_status(root=self.d, transcripts=self.d)
        self.assertIn("tier: 70", s); self.assertIn("queued: 0", s)


    def test_dedup_ignores_closed_record(self):
        p = m.paths(self.d); p["sessions"].mkdir(parents=True)
        (p["sessions"] / "MTS-2026-10-01-0000Z-CLI-BLD-alert-rate.md").write_text("status: closed rc=1`n")
        self.usage(10); self.assertNotIn("resume-existing", self.go())

if __name__ == "__main__":
    unittest.main()
