"""scripts/dev/desk.py sweep (RU2): a read-only dry run over the pending desk rows ON TRUNK (git show, never local files).
Fixture repo, in-process, no network. Expected proposals follow the card's done_when: duplicate, stale, likely-done and
blocked rows each get their proposal; two runs give the same answer; local files that differ from trunk are ignored."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import desk  # noqa: E402

AS_OF = datetime(2026, 10, 18, 12, 0, 0, tzinfo=timezone.utc)
ROUTING = "| Run script | JIS-NUC | desk row `--target DSA-NUC` | DeepSeek |\n| Deploy | JIS-NB | desk row `--target JIS-NB` | x |\n"
ANNOUNCE = ("# Board\n### A-20261018-6 STOP Do not rerun `gap-g2-dax-ask-candles` as written\n- Applies to: all\n"
            "## EXPIRED\n### A-20261018-5 HOLD Old hold on `expired-thing` entirely\n")


def git(repo, *args, env=None):
    import os
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", **(env or {}))
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=e)
    assert r.returncode == 0, r.stderr
    return r.stdout


def row(rid, title, posted, target="JIS-NUC", need="exact commands", status="pending"):
    return {"id": rid, "title": title, "need": need, "done_when": "x", "target": target, "from": "JIS-NB", "posted": posted, "status": status}


class SweepTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "checkout", "-q", "-b", "fast-track")
        (self.repo / desk.QUEUE).mkdir(parents=True)
        for rel, text in ((desk.ROUTING, ROUTING), (desk.ANNOUNCE, ANNOUNCE)):
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8", newline="\n")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, msg, when, rows=(), files=None):
        for r in rows:
            (self.repo / desk.QUEUE / f"{r['id']}.json").write_text(json.dumps(r), encoding="utf-8", newline="\n")
        for rel, text in (files or {}).items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8", newline="\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", msg, env={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
        git(self.repo, "update-ref", "refs/remotes/origin/fast-track", "HEAD")

    def proposals(self):
        res = desk.sweep(self.repo, as_of=AS_OF)
        return res, {o["id"]: o for o in res["proposals"]}

    def test_stale_row_over_48h(self):
        self.commit("desk rows", "2026-10-15T08:00:00Z", [row("old", "Fetch funding history archive", "2026-10-15T08:00:00Z"),
                                                          row("fresh", "Count rows in inventory csv", "2026-10-18T10:00:00Z")])
        _, p = self.proposals()
        self.assertEqual(p["old"]["proposal"], "STALE")
        self.assertIn("h old", p["old"]["evidence"])
        self.assertEqual(p["fresh"]["proposal"], "KEEP")

    def test_duplicate_row_points_at_the_earlier_one(self):
        self.commit("rows", "2026-10-18T09:00:00Z", [
            row("a1", "Fetch Dukascopy DAX candles for the DEV window", "2026-10-18T09:00:00Z"),
            row("a2", "Fetch Dukascopy DAX candles for the DEV window", "2026-10-18T09:30:00Z")])
        _, p = self.proposals()
        self.assertEqual(p["a1"]["proposal"], "KEEP")
        self.assertEqual(p["a2"]["proposal"], "DUPLICATE")
        self.assertIn("a1", p["a2"]["evidence"])

    def test_likely_done_names_candidate_commit(self):
        self.commit("rows", "2026-10-18T06:00:00Z", [row("cme", "Krown CME BTC futures daily volume arm", "2026-10-18T06:00:00Z")])
        self.commit("Krown CME BTC futures volume arm fetched", "2026-10-18T08:00:00Z", files={"data/cme_volume.csv": "x"})
        self.commit("unrelated change", "2026-10-18T09:00:00Z", files={"misc.txt": "y"})
        _, p = self.proposals()
        self.assertEqual(p["cme"]["proposal"], "LIKELY DONE")
        sha = git(self.repo, "log", "--format=%h", "--grep=Krown CME").strip()
        self.assertIn(sha, p["cme"]["evidence"])

    def test_commit_before_posting_does_not_count(self):
        self.commit("Krown CME BTC futures volume arm fetched", "2026-10-18T05:00:00Z", files={"a.txt": "x"})
        self.commit("rows", "2026-10-18T06:00:00Z", [row("cme", "Krown CME BTC futures daily volume arm", "2026-10-18T06:00:00Z")])
        _, p = self.proposals()
        self.assertEqual(p["cme"]["proposal"], "KEEP")

    def test_blocked_by_active_stop_not_expired_hold(self):
        self.commit("rows", "2026-10-18T09:00:00Z", [
            row("g2", "Rerun gap-g2-dax-ask-candles on DEV", "2026-10-18T09:00:00Z"),
            row("ex", "Look at expired-thing again", "2026-10-18T09:00:00Z")])
        _, p = self.proposals()
        self.assertEqual(p["g2"]["proposal"], "BLOCKED")
        self.assertIn("A-20261018-6", p["g2"]["evidence"])
        self.assertEqual(p["ex"]["proposal"], "KEEP")

    def test_wrong_target_and_counts_and_stale_claims(self):
        self.commit("rows+claim", "2026-10-18T09:00:00Z", [row("w", "Do a thing", "2026-10-18T09:00:00Z", target="NOWHERE")], files={
            "MyTradingSys/system/claims/old.md": f"host: H\naccount: A\ntask: t\nepoch: {int(AS_OF.timestamp()) - 30 * 3600}\n",
            "MyTradingSys/system/claims/new.md": f"host: H\naccount: A\ntask: t\nepoch: {int(AS_OF.timestamp()) - 2 * 3600}\n"})
        res, p = self.proposals()
        self.assertEqual(p["w"]["proposal"], "WRONG TARGET")
        self.assertEqual(res["pending_per_target"], {"NOWHERE": 1})
        self.assertEqual([c["claim"] for c in res["stale_claims"]], ["old"])

    def test_second_run_proposes_the_same(self):
        self.commit("rows", "2026-10-15T08:00:00Z", [row("old", "Fetch funding history archive", "2026-10-15T08:00:00Z"),
                                                     row("d1", "Same title twice here", "2026-10-18T08:00:00Z"),
                                                     row("d2", "Same title twice here", "2026-10-18T08:30:00Z")])
        first = desk.sweep(self.repo, as_of=AS_OF)
        self.assertEqual(first, desk.sweep(self.repo, as_of=AS_OF))
        self.assertEqual(desk.render_sweep(first), desk.render_sweep(desk.sweep(self.repo, as_of=AS_OF)))

    def test_local_files_differing_from_trunk_are_ignored(self):
        self.commit("rows", "2026-10-18T09:00:00Z", [row("t1", "Count rows in inventory csv", "2026-10-18T09:00:00Z")])
        before = desk.sweep(self.repo, as_of=AS_OF)
        (self.repo / desk.QUEUE / "t1.json").write_text(json.dumps(row("t1", "Count rows in inventory csv", "2026-10-18T09:00:00Z", status="done")))
        (self.repo / desk.QUEUE / "local-only.json").write_text(json.dumps(row("local-only", "Never pushed row", "2026-10-01T00:00:00Z")))
        after = desk.sweep(self.repo, as_of=AS_OF)
        self.assertEqual(before, after)
        self.assertEqual([o["id"] for o in after["proposals"]], ["t1"])

    def test_sweep_changes_no_row(self):
        self.commit("rows", "2026-10-15T08:00:00Z", [row("old", "Fetch funding history archive", "2026-10-15T08:00:00Z")])
        head = git(self.repo, "rev-parse", "HEAD")
        desk.sweep(self.repo, as_of=AS_OF)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
