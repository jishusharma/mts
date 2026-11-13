"""c_drive_guard buckets: regenerable caches outside %TEMP% are pruned; work, profiles, memory and live trees never are."""
import contextlib
import io
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_drive_guard as g
import wt_maint

BARS = "MyTradingSys/research/sim_desk/cache/bars"
# The guard's "stale" cutoff is `now`; a file written this tick has mtime == now on a coarse-clock runner (Windows ~16 ms, some Linux fs 1-2 s) and
# an mtime equal to the cutoff is NOT stale: the result then depended on the machine's clock (29 red CI runs, 2026-10-30..11-11). Every
# test here passes a `now` an hour ahead of the real clock, so the fresh fixture files are stale on every machine.
LATER = lambda: time.time() + 3600   # noqa: E731


def make(root, rel, age_d=0, size=10):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * size)
    t = time.time() - age_d * 86400
    q = p
    while q != Path(root):
        os.utime(q, (t, t))
        q = q.parent
    return p


class BucketTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        self.old = g.HOME, g.LOCALAPPDATA, g.MAIN
        g.HOME, g.LOCALAPPDATA, g.MAIN = self.root / "home", self.root / "local", self.root / "repo" / "main"
        # the runner's real %LOCALAPPDATA% must never leak in (a fresh guard import reads these env vars)
        env = mock.patch.dict(os.environ, {"LOCALAPPDATA": str(self.root / "local"),
                                           "MTS_GUARD_LOCALAPPDATA": str(self.root / "local")})
        env.start()
        self.addCleanup(env.stop)

    def tearDown(self):
        g.HOME, g.LOCALAPPDATA, g.MAIN = self.old
        self.d.cleanup()

    def paths(self, rows):
        return {Path(p).relative_to(self.root).as_posix() for _, p, _, _ in rows}

    def test_rescue_cache_pruned_rescued_work_kept(self):
        # age_d=1: an mtime equal to the cutoff (same coarse clock tick on a Windows CI runner) is not stale (CI red bb59029e)
        r = "repo/main/Dumps/wt_rescue/t1/"
        make(self.root, r + BARS + "/BTCUSDT-1mv-2023-01.npy", size=2000, age_d=1)
        make(self.root, "repo/main/Dumps/wt_rescue/t0/files/" + BARS + "/old.npy", size=3000, age_d=1)   # older rescue layout
        make(self.root, r + "MyTradingSys/research/sim_desk/cache/results/a.json", age_d=1)
        make(self.root, r + "uncommitted.patch", age_d=1)
        rows = g.rescue_cache_rows(g.MAIN, now=LATER())
        self.assertEqual(self.paths(rows), {r + BARS, "repo/main/Dumps/wt_rescue/t0/files/" + BARS})
        self.assertEqual(sum(s for _, _, s, _ in rows), 5000)
        g.prune_buckets(True, rows)
        self.assertFalse((self.root / r / BARS).exists())
        self.assertTrue((self.root / r / "uncommitted.patch").exists())
        self.assertTrue((self.root / r / "MyTradingSys/research/sim_desk/cache/results/a.json").exists())

    def test_a_file_written_this_tick_is_stale_only_against_a_later_now(self):
        """Fail-first for the machine-dependence: the same fixture is not stale at its own mtime (equal = fresh) and is stale one hour on."""
        make(self.root, "repo/main/Dumps/wt_rescue/t9/" + BARS + "/x.npy", size=10)
        stamp = os.stat(self.root / "repo/main/Dumps/wt_rescue/t9" / BARS).st_mtime
        self.assertEqual(g.rescue_cache_rows(g.MAIN, now=stamp), [])
        self.assertEqual(len(g.rescue_cache_rows(g.MAIN, now=stamp + 3600)), 1)

    def test_wt_maint_rescue_does_not_copy_the_bar_cache(self):
        tree = self.root / "repo" / "mts-x"
        make(tree, BARS + "/b.npy")
        make(tree, "MyTradingSys/research/sim_desk/cache/results/r.json")
        row = dict(path=str(tree), name="mts-x", data=["MyTradingSys/research/sim_desk/cache/"])
        with mock.patch.object(wt_maint, "primary", return_value=g.MAIN):
            dest = wt_maint.rescue_data(self.root, row)
        self.assertTrue((dest / "MyTradingSys/research/sim_desk/cache/results/r.json").exists())
        self.assertFalse((dest / BARS).exists())

    def test_browser_cache_only_when_not_running_and_never_profile_data(self):
        u = "local/Google/Chrome/User Data/"
        for rel in ("Default/Cache/f", "Profile 5/Code Cache/f", "GrShaderCache/f", "Default/Service Worker/CacheStorage/f",
                    "Default/Cookies", "Default/Login Data"):
            make(self.root, u + rel)
        self.assertEqual(g.browser_rows(g.LOCALAPPDATA, run=lambda image: True, now=LATER()), [])
        got = self.paths(g.browser_rows(g.LOCALAPPDATA, run=lambda image: False, now=LATER()))
        self.assertEqual(got, {u + "Default/Cache", u + "Profile 5/Code Cache", u + "GrShaderCache"})

    def test_claude_logs_old_sessions_only_never_memory(self):
        p = "home/.claude/projects/C--repo/"
        sid, new = "0123abcd-0000-4000-8000-00000000000a", "0123abcd-0000-4000-8000-00000000000b"
        make(self.root, p + sid + ".jsonl", age_d=20)
        make(self.root, p + sid + "/subagents/a.jsonl", age_d=20)
        make(self.root, p + new + ".jsonl", age_d=2)
        make(self.root, p + "memory/MEMORY.md", age_d=90)
        got = self.paths(g.claude_log_rows(g.HOME))
        self.assertEqual(got, {p + sid + ".jsonl", p + sid})

    def test_playwright_keeps_the_newest_revision(self):
        make(self.root, "local/ms-playwright/chromium-1200/x", age_d=5)
        make(self.root, "local/ms-playwright/chromium-1243/x", age_d=5)
        make(self.root, "local/ms-playwright/ffmpeg-1011/x", age_d=5)
        self.assertEqual(self.paths(g.playwright_rows(g.LOCALAPPDATA)), {"local/ms-playwright/chromium-1200"})

    def test_orphans_only_without_git_and_not_a_worktree(self):
        make(self.root, "repo/mts-gone/src/a.py", age_d=10)
        make(self.root, "repo/mts-fresh/src/a.py", age_d=1)
        make(self.root, "repo/mts-tree/.git", age_d=10)
        make(self.root, "repo/mts-listed/a.py", age_d=10)
        make(self.root, "repo/mts-live/.mts_live", age_d=10)
        make(self.root, "repo/main/.claude/worktrees/agent-x/a.py", age_d=10)
        listed = {os.path.normcase(str((self.root / "repo/mts-listed").resolve()))}
        got = self.paths(g.orphan_rows(g.MAIN, trees=listed))
        self.assertEqual(got, {"repo/mts-gone", "repo/main/.claude/worktrees/agent-x"})
        with mock.patch.object(g, "worktree_paths", return_value=None):     # git cannot list the trees: prune nothing
            self.assertEqual(g.orphan_rows(g.MAIN), [])

    def test_dry_run_prints_gb_per_bucket_and_deletes_nothing(self):
        # aged 2 days: a cache written this tick sits exactly on the guard's cutoff on a coarse-clock runner (mtime >= cutoff = not stale)
        f = make(self.root, "local/Google/Chrome/User Data/Default/Cache/f", age_d=2, size=5000)
        out = io.StringIO()
        with mock.patch.object(g, "running", return_value=False), mock.patch.object(g, "TEMP", self.root / "temp"), \
                contextlib.redirect_stdout(out):
            self.assertEqual(g.main([]), 0)
        self.assertIn("browser-cache", out.getvalue())
        self.assertTrue(f.exists())


if __name__ == "__main__":
    unittest.main()
