"""c_drive_guard prunes only old, known-prefix %TEMP% entries and old Claude session dirs; it reports runaway task outputs."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_drive_guard as g

TEST_KEY = r"Software\MTSTempGuardTest"
TEST_NAME = "MTSTempGuardTest"


def make(root, rel, age_h, size=10):
    """Write root/rel and age the file and every directory below root to age_h hours."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    t = time.time() - age_h * 3600
    while path != root:
        os.utime(path, (t, t))
        path = path.parent
    return root / rel


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        self.logdir = tempfile.TemporaryDirectory()
        self.old_temp, self.old_log, self.old_stamp = g.TEMP, g.LOG, g.STAMP
        g.TEMP = self.root
        g.LOG = Path(self.logdir.name) / "c_drive_guard.log"
        g.STAMP = Path(self.logdir.name) / "c_drive_guard.stamp"
        self.old_lock = g.LOCK
        g.LOCK = Path(self.logdir.name) / "c_drive_guard.lock"
        g.STAMP.write_text("x", encoding="utf-8")      # daily run not due unless a test ages this
        self.real_tidy = g.run_tidy
        g.run_tidy = lambda apply: []                  # never run the real worktree job against this checkout from a test

    def tearDown(self):
        g.TEMP, g.LOG, g.STAMP = self.old_temp, self.old_log, self.old_stamp
        g.LOCK = self.old_lock
        g.run_tidy = self.real_tidy
        self.d.cleanup()
        self.logdir.cleanup()

    def test_prunes_only_old_known_prefix_and_old_sessions(self):
        r = self.root
        make(r, "mts_s4_old/bt/f.txt", 30)
        make(r, "tmpabc12345/f.txt", 30)
        make(r, "mts_s4_new/f.txt", 1)
        make(r, "precious/f.txt", 500)
        make(r, "claude/proj/sess_old/tasks/a.output", 100)
        make(r, "claude/proj/sess_new/tasks/a.output", 10)
        n, freed = g.prune(apply=True)
        self.assertEqual(n, 3)
        self.assertEqual(freed, 30)
        left = sorted(p.name for p in self.root.iterdir())
        self.assertEqual(left, ["claude", "mts_s4_new", "precious"])
        self.assertEqual([p.name for p in (self.root / "claude" / "proj").iterdir()], ["sess_new"])

    def test_prunes_the_gate_and_test_prefixes_seen_in_temp(self):
        for name in ("gate_budget_test_abc", "dsa_tpl_x1", "e2e_a2_q", "dsa-boot-3"):
            make(self.root, name + "/f.txt", 30)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 4)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_git_worktrees_are_never_pruned(self):
        # desk.py makes its scratch checkout with `git worktree add` under %TEMP%\desk-*: a crashed post leaves unshipped commits
        make(self.root, "desk-y_51efmr/wt/.git", 30)
        make(self.root, "gate_budget_test_wt/tree/.git", 30)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertTrue((self.root / "desk-y_51efmr").exists())
        self.assertTrue((self.root / "gate_budget_test_wt").exists())

    def test_state_dirs_other_code_reads_are_never_pruned(self):
        for name in ("mts_roles", "mts_host_health", "mts_gate_slots", "mts_relay"):
            make(self.root, name + "/state.json", 500)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertEqual(len(list(self.root.iterdir())), 4)

    def test_one_new_file_deep_inside_keeps_the_whole_entry(self):
        make(self.root, "tmpdeep/a/b/old.txt", 30)
        make(self.root, "tmpdeep/a/b/new.txt", 1)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertTrue((self.root / "tmpdeep").exists())

    def test_dry_run_deletes_nothing(self):
        make(self.root, "tmpabc12345/f.txt", 30)
        n, _ = g.prune(apply=False)
        self.assertEqual(n, 1)
        self.assertTrue((self.root / "tmpabc12345").exists())

    def test_runaway_output_is_reported(self):
        p = make(self.root, "claude/proj/sess/tasks/big.output", 0)
        old = g.RUNAWAY_MB
        g.RUNAWAY_MB = 0
        try:
            self.assertEqual([r[0] for r in g.runaways()], [str(p)])
        finally:
            g.RUNAWAY_MB = old

    def test_hook_is_silent_above_the_limit(self):
        os.environ["MTS_C_MIN_FREE_GB"] = "0"
        try:
            self.assertEqual(g.main(["hook"]), 0)
        finally:
            os.environ.pop("MTS_C_MIN_FREE_GB", None)

    def test_own_gate_basetemps_go_after_6_h_other_prefixes_after_24(self):
        make(self.root, "mts_s4_8h/f.txt", 8)
        make(self.root, "mts_s5c_8h/f.txt", 8)
        make(self.root, "tmpabc_8h/f.txt", 8)
        make(self.root, "mts_s4_1h/f.txt", 1)
        g.prune(apply=True)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["mts_s4_1h", "tmpabc_8h"])

    def test_plan_lists_each_item_with_a_reason_and_deletes_nothing(self):
        make(self.root, "mts_s4_old/f.txt", 30)
        old = g.run_tidy
        g.run_tidy = lambda apply: ["would remove  agent-1 [b]: clean, no ignored data, on origin/fast-track, idle 2.0 h",
                                    "would remove 1; kept 0"]
        try:
            rows = g.plan()
        finally:
            g.run_tidy = old
        self.assertEqual([(r[0], Path(r[1]).name) for r in rows], [("temp", "mts_s4_old"), ("worktree", "agent-1 [b]")])
        self.assertTrue(all(r[3] for r in rows))
        self.assertTrue((self.root / "mts_s4_old").exists())

    def test_never_deletes_other_apps_files_or_the_claude_app_folder(self):
        make(self.root, "OtherApp/f.txt", 900)
        make(self.root, "Claude/f.txt", 900)           # the app's own data folder name, never matches a prefix
        make(self.root, "AnthropicClaude/f.txt", 900)
        make(self.root, "xmts_s4_notprefix/f.txt", 900)
        g.prune(apply=True)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["AnthropicClaude", "Claude", "OtherApp", "xmts_s4_notprefix"])
        self.assertEqual(g.candidates(), [])

    def test_hook_runs_the_guard_once_a_day_and_not_again(self):
        started = []
        old = g.start_apply_detached
        g.start_apply_detached = lambda: started.append(1)
        os.environ["MTS_C_MIN_FREE_GB"] = "0"
        try:
            t = time.time() - 30 * 3600
            os.utime(g.STAMP, (t, t))
            g.main(["hook"])
            g.main(["hook"])
        finally:
            g.start_apply_detached = old
            os.environ.pop("MTS_C_MIN_FREE_GB", None)
        self.assertEqual(started, [1])

    def test_apply_logs_one_line_with_the_gb_freed(self):
        make(self.root, "mts_s4_old/f.txt", 30)
        old, old_note = g.run_tidy, g.main_checkout_note
        g.run_tidy = lambda apply: ["removed  agent-1 [b]: x"]
        g.main_checkout_note = lambda pull=True: "main checkout 3 behind; hook may be stale"
        try:
            g.apply_all("apply")
        finally:
            g.run_tidy, g.main_checkout_note = old, old_note
        lines = g.LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("freed", lines[0])
        self.assertIn("1 worktrees retired", lines[0])
        self.assertIn("main checkout 3 behind; hook may be stale", lines[0])

    def test_two_guards_at_once_only_one_runs_tidy(self):
        calls = []
        old, old_note = g.run_tidy, g.main_checkout_note

        def tidy(apply):
            calls.append(apply)
            if len(calls) == 1:
                g.main(["--apply"])        # the second copy starts while the first is inside tidy
            return []
        g.run_tidy = tidy
        g.main_checkout_note = lambda pull=True: "x"
        try:
            g.main(["--apply"])
        finally:
            g.run_tidy, g.main_checkout_note = old, old_note
        self.assertEqual(calls, [True])
        self.assertFalse(g.LOCK.exists())          # released at the end

    def test_a_stale_lock_of_a_dead_pid_is_replaced(self):
        g.LOCK.write_text("999999999", encoding="utf-8")
        self.assertTrue(g.take_lock())
        self.assertFalse(g.take_lock())            # our own live pid now holds it
        g.drop_lock()

    def test_every_child_is_started_without_a_console_window(self):
        seen = []
        real = subprocess.Popen
        g.subprocess.Popen = lambda *a, **k: seen.append(k) or None
        try:
            g.start_apply_detached()
        finally:
            g.subprocess.Popen = real
        self.assertEqual(len(seen), 1)
        self.assertTrue(seen[0]["creationflags"] & g.NO_WINDOW or os.name != "nt")
        self.assertFalse(seen[0]["creationflags"] & getattr(subprocess, "DETACHED_PROCESS", 0))
        self.assertNotEqual(seen[0]["stdout"], subprocess.DEVNULL)

    def test_low_space_on_the_repo_drive_counts_not_only_c(self):
        old_free, old_drive = g.free_gb, g.repo_drive
        g.repo_drive = lambda: "F:\\"
        g.free_gb = lambda d="C:\\": 50.0 if d == "C:\\" else 4.0
        try:
            self.assertEqual(g.low_drives(15), [("F:\\", 4.0)])
            g.repo_drive = lambda: "C:\\"
            self.assertEqual(g.low_drives(15), [])
        finally:
            g.free_gb, g.repo_drive = old_free, old_drive

    def _repo_pair(self, tmp):
        def sh(cwd, *a):
            subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True)
        origin, main = Path(tmp) / "origin.git", Path(tmp) / "main"
        sh(tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        sh(tmp, "clone", "-q", str(origin), str(main))
        for c in (main,):
            sh(c, "config", "user.email", "a@b.c")
            sh(c, "config", "user.name", "t")
        sh(main, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git 2.24 clones an empty repo onto master
        (main / "a.txt").write_text("1", newline="\n")
        sh(main, "add", "."); sh(main, "commit", "-q", "-m", "one"); sh(main, "push", "-q", "-u", "origin", "fast-track")
        other = Path(tmp) / "other"
        sh(tmp, "clone", "-q", str(origin), str(other))
        sh(other, "config", "user.email", "a@b.c"); sh(other, "config", "user.name", "t")
        (other / "b.txt").write_text("2", newline="\n")
        sh(other, "add", "."); sh(other, "commit", "-q", "-m", "two"); sh(other, "push", "-q", "origin", "HEAD:fast-track")
        return main

    def test_main_checkout_behind_is_pulled_when_clean_and_left_alone_when_dirty(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = self._repo_pair(tmp)
            old = g.main_checkout
            g.main_checkout = lambda: main
            try:
                (main / "a.txt").write_text("edited", newline="\n")
                note = g.main_checkout_note()
                self.assertIn("main checkout 1 behind; hook may be stale", note)
                self.assertIn("not pulled", note)
                self.assertFalse((main / "b.txt").exists())
                subprocess.run(["git", "-C", str(main), "checkout", "-q", "--", "a.txt"], check=True)
                self.assertIn("pulled", g.main_checkout_note())
                self.assertTrue((main / "b.txt").exists())
            finally:
                g.main_checkout = old

    def test_logon_prunes_whatever_the_free_space_and_logs_one_line(self):
        make(self.root, "tmpold/f.txt", 30)
        make(self.root, "mts_s4_new/f.txt", 1)
        self.assertEqual(g.main(["logon"]), 0)
        self.assertFalse((self.root / "tmpold").exists())
        self.assertTrue((self.root / "mts_s4_new").exists())
        lines = g.LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("logon: C free", lines[0])
        self.assertIn("pruned 1 temp entries", lines[0])

    def test_logon_also_retires_finished_worktrees_with_the_maintenance_job(self):
        g.run_tidy = lambda apply: ["removed  mts-old [b]", "kept  x"] if apply else []
        g.logon()
        self.assertIn("1 worktrees retired", g.LOG.read_text(encoding="utf-8"))

    def test_worktree_retirement_runs_wt_maint_with_no_log(self):
        seen = []
        old = g.subprocess.run
        g.subprocess.run = lambda cmd, **kw: seen.append(cmd) or type("R", (), {"stdout": ""})()
        try:
            self.real_tidy(True)
        finally:
            g.subprocess.run = old
        self.assertTrue(seen[0][1].endswith("wt_maint.py"))
        self.assertIn("--apply", seen[0])
        self.assertIn("--no-log", seen[0])

    def test_the_run_value_can_name_another_clone_whose_worktrees_it_retires(self):
        cmd = g.logon_command(python="py", script="s.py", repos=[r"C:\other\repo"])
        self.assertTrue(cmd.endswith(' logon --repo "C:\\other\\repo"'))
        self.assertEqual(g.repo_args(["logon", "--repo", "A", "--repo", "B"]), ["A", "B"])
        seen = []
        old = g.subprocess.run
        g.subprocess.run = lambda c, **kw: seen.append(c) or type("R", (), {"stdout": ""})()
        try:
            self.real_tidy(True, ["A"])
        finally:
            g.subprocess.run = old
        self.assertEqual(len(seen), 2)
        self.assertNotIn("--repo", seen[0])
        self.assertEqual(seen[1][-2:], ["--repo", "A"])

    def test_logon_command_is_headless_and_runs_the_logon_mode(self):
        cmd = g.logon_command(python=r"C:\Py\python.exe", script=r"C:\repo\scripts\dev\c_drive_guard.py")
        self.assertIn("--headless", cmd)
        self.assertIn(r'"C:\Py\python.exe" "C:\repo\scripts\dev\c_drive_guard.py" logon', cmd)
        self.assertTrue(cmd.endswith(" logon"))

    @unittest.skipUnless(os.name == "nt", "junctions are Windows reparse points")
    def test_a_junction_is_never_walked_or_pruned(self):
        target = tempfile.TemporaryDirectory()
        link = self.root / "tmpjunction"
        try:
            keep = make(Path(target.name), "precious.txt", 500)
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), target.name], check=True, capture_output=True)
            n, _ = g.prune(apply=True)
            self.assertEqual(n, 0)
            self.assertTrue(keep.exists())
        finally:
            if link.exists():
                os.rmdir(link)     # removes the junction only
            target.cleanup()

    @unittest.skipUnless(os.name == "nt", "junctions are Windows reparse points")
    def test_a_junction_under_claude_is_never_followed(self):
        # a junction in %TEMP%\claude\<proj> pointing at a folder outside %TEMP% must not lead the guard into it
        target = tempfile.TemporaryDirectory()
        proj_link = self.root / "claude" / "projjunction"
        try:
            keep = make(Path(target.name), "sess_old/tasks/a.output", 100)
            proj_link.parent.mkdir(parents=True)
            subprocess.run(["cmd", "/c", "mklink", "/J", str(proj_link), target.name], check=True, capture_output=True)
            n, _ = g.prune(apply=True)
            self.assertEqual(n, 0)
            self.assertTrue(keep.exists())
        finally:
            if proj_link.exists():
                os.rmdir(proj_link)     # removes the junction only
            target.cleanup()

    def test_install_refuses_a_git_worktree(self):
        with tempfile.TemporaryDirectory() as wt, contextlib.redirect_stdout(io.StringIO()) as out:
            Path(wt, ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
            Path(wt, "scripts", "dev").mkdir(parents=True)
            Path(wt, "scripts", "dev", "c_drive_guard.py").write_text("", encoding="utf-8")
            self.assertEqual(g.install(checkout=wt, key=TEST_KEY, name=TEST_NAME), 2)
        self.assertIn("git worktree", out.getvalue())
        self.assertIsNone(g.installed_command(TEST_KEY, TEST_NAME))


@unittest.skipUnless(os.name == "nt", "HKCU Run is Windows only")
class RunKeyTest(unittest.TestCase):
    def setUp(self):
        self.co = tempfile.TemporaryDirectory()
        Path(self.co.name, ".git").mkdir()
        Path(self.co.name, "scripts", "dev").mkdir(parents=True)
        Path(self.co.name, "scripts", "dev", "c_drive_guard.py").write_text("", encoding="utf-8")

    def tearDown(self):
        import winreg
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, TEST_KEY)
        except OSError:
            pass
        self.co.cleanup()

    def test_install_status_uninstall_roundtrip(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(g.install(checkout=self.co.name, key=TEST_KEY, name=TEST_NAME), 0)
            cmd = g.installed_command(TEST_KEY, TEST_NAME)
            self.assertIn(str(Path(self.co.name, "scripts", "dev", "c_drive_guard.py")), cmd)
            self.assertEqual(g.uninstall(key=TEST_KEY, name=TEST_NAME), 0)
        self.assertIsNone(g.installed_command(TEST_KEY, TEST_NAME))


NOW = 1_800_000_000.0     # fixed clock for the process tests (epoch seconds)


def proc(pid, ppid, name, cmd, age_h, now=NOW):
    return {"pid": pid, "ppid": ppid, "name": name, "cmd": cmd, "created": now - age_h * 3600, "cpu": 0.0}


def leftovers_jis_nb(now=NOW):
    """The JIS-NB leftovers of 2026-10-28 (parents already gone), a live claude.exe tree with us in it, and a young sim desk run."""
    return [
        proc(100, 1, "explorer.exe", "C:\\Windows\\explorer.exe", 300, now),
        proc(200, 100, "claude.exe", "claude.exe --session x", 50, now),
        proc(201, 200, "python.exe", "python.exe scripts/dev/c_drive_guard.py", 0.1, now),
        proc(300, 1, "pythonw.exe", "pythonw.exe -m MyTradingSys.backtest.layers.fabio.htf_context_live --loop", 146, now),
        proc(301, 1, "pythonw.exe", "pythonw.exe -m MyTradingSys.backtest.layers.fabio.htf_context_live --loop", 146, now),
        proc(400, 8460, "python.exe", "python.exe desk.py --no-browser --port 8790", 48, now),
        proc(401, 400, "python.exe", "python.exe desk.py --no-browser --port 8790", 48, now),
        proc(500, 16256, "cmd.exe", "cmd /d /s /c chrome-native-host.exe chrome-extension://x", 72, now),
        proc(600, 1, "python.exe", "python.exe MyTradingSys/research/sim_desk/desk.py", 5, now),
    ]


class ProcsTest(unittest.TestCase):
    def verdicts(self, rows):
        return {r["pid"]: r["verdict"] for r in rows}

    def test_jis_nb_leftovers_are_listed_with_their_verdicts(self):
        v = self.verdicts(g.proc_rows(leftovers_jis_nb(), NOW))
        self.assertEqual(v, {300: "PROTECTED", 301: "PROTECTED", 400: "KILL", 401: "KILL", 500: "UNMATCHED"})

    def test_young_and_own_processes_are_no_candidates(self):
        v = self.verdicts(g.proc_rows(leftovers_jis_nb(), NOW))
        self.assertNotIn(600, v)
        self.assertNotIn(201, v)

    def test_safe_old_desk_py_is_kill(self):
        self.assertEqual(g.proc_verdict(proc(9, 1, "python.exe", "python desk.py --port 8790", 30), {}, NOW)[0], "KILL")

    def test_young_process_is_no_candidate(self):
        self.assertIsNone(g.proc_verdict(proc(9, 1, "python.exe", "python desk.py", 23.9), {}, NOW))

    def test_unknown_start_time_is_no_candidate(self):
        p = proc(9, 1, "python.exe", "python desk.py", 30)
        p["created"] = 0
        self.assertIsNone(g.proc_verdict(p, {}, NOW))

    def test_claude_ancestor_protects_a_safe_pattern(self):
        rows = [proc(10, 1, "claude.exe", "claude.exe", 100), proc(11, 10, "python.exe", "python desk.py", 30)]
        by = {p["pid"]: p for p in rows}
        self.assertEqual(g.proc_verdict(rows[1], by, NOW)[0], "PROTECTED")

    def test_never_kill_text_protects_even_with_a_safe_pattern(self):
        for text in (".mts_live", "live_runner_cli", "loop-supervisor", "start-trading-day", "oi_recorder", "orderflow_live",
                     "htf_context_live", "deploy", "wait_then_ship"):
            cmd = "python desk.py --tag " + text
            self.assertEqual(g.proc_verdict(proc(9, 1, "python.exe", cmd, 30), {}, NOW)[0], "PROTECTED", text)

    def test_never_kill_text_in_an_ancestor_protects_the_child(self):
        rows = [proc(10, 1, "pythonw.exe", "pythonw -m MyTradingSys.live_runner_cli", 80), proc(11, 10, "python.exe", "python desk.py", 30)]
        by = {p["pid"]: p for p in rows}
        self.assertEqual(g.proc_verdict(rows[1], by, NOW)[0], "PROTECTED")

    def test_sync_py_ship_is_protected(self):
        self.assertEqual(g.proc_verdict(proc(9, 1, "python.exe", "python scripts/dev/sync.py ship --release x", 30), {}, NOW)[0], "PROTECTED")

    def test_java_is_never_killed(self):
        for name in ("java.exe", "javaw.exe"):
            v = g.proc_verdict(proc(9, 1, name, "java desk.py", 300), {}, NOW)
            self.assertNotEqual(v and v[0], "KILL", name)

    def test_unmatched_shell_is_reported_and_never_killed(self):
        self.assertEqual(g.proc_verdict(proc(9, 1, "cmd.exe", "cmd /c something unknown", 72), {}, NOW)[0], "UNMATCHED")

    def test_other_image_names_are_no_candidates(self):
        self.assertIsNone(g.proc_verdict(proc(9, 1, "notepad.exe", "notepad desk.py", 300), {}, NOW))

    def test_apply_kills_only_kill_rows_by_pid(self):
        killed_pids = []
        snap = leftovers_jis_nb()
        k, s = g.procs_apply(snapshot=lambda: snap, now=NOW, kill=lambda pid: killed_pids.append(pid) or True)
        self.assertEqual(sorted(killed_pids), [400, 401])
        self.assertEqual(sorted(k), [400, 401])
        self.assertEqual(s, [])

    def test_pid_reused_between_report_and_kill_is_not_killed(self):
        first = leftovers_jis_nb()
        second = [dict(p) for p in first]
        for p in second:
            if p["pid"] == 400:
                p["created"] = NOW - 1 * 3600          # PID 400 was reused by a young process
        calls = iter([first, second])
        killed_pids = []
        k, s = g.procs_apply(snapshot=lambda: next(calls), now=NOW, kill=lambda pid: killed_pids.append(pid) or True)
        self.assertEqual(killed_pids, [401])
        self.assertTrue(any("PID 400" in line for line in s))

    def test_report_run_kills_nothing(self):
        def boom(*a, **k):
            raise AssertionError("the report must never kill")
        with mock.patch.object(g, "kill_pid", boom), mock.patch.object(g, "procs_apply", boom):
            line = g.procs_summary(procs=leftovers_jis_nb(), now=NOW)
        self.assertIn("2 KILL candidate(s)", line)
        self.assertIn("2 PROTECTED", line)
        self.assertIn("1 UNMATCHED", line)

    def test_summary_never_raises(self):
        self.assertTrue(g.procs_summary(procs=[{"bad": 1}], now=NOW).startswith("unavailable"))

    def test_kill_is_by_pid_never_by_image_name(self):
        seen = []
        with mock.patch.object(g.subprocess, "run", lambda args, **kw: seen.append(args) or subprocess.CompletedProcess(args, 0)):
            self.assertTrue(g.kill_pid(4242))
        self.assertEqual(seen, [["taskkill", "/PID", "4242", "/F"]])
        src = Path(g.__file__).read_text(encoding="utf-8")
        self.assertNotIn('"/IM"', src)
        self.assertNotIn('"/T"', src[src.index("def kill_pid"):src.index("def procs_apply")])

    def test_daily_run_logs_the_procs_count_and_never_kills(self):
        with mock.patch.object(g, "procs_summary", lambda *a, **k: "0 KILL candidate(s) []"), \
                mock.patch.object(g, "procs_apply", side_effect=AssertionError("no kill in the daily run")), \
                mock.patch.object(g, "prune", lambda apply: (0, 0)), mock.patch.object(g, "run_tidy", lambda apply, repos=(): []), \
                mock.patch.object(g, "main_checkout_note", lambda: "main checkout 0 behind"):
            with tempfile.TemporaryDirectory() as d:
                old_log = g.LOG
                g.LOG = Path(d) / "c_drive_guard.log"
                try:
                    g.apply_all("apply")
                    text = g.LOG.read_text(encoding="utf-8")
                finally:
                    g.LOG = old_log
        self.assertIn("procs (report only): 0 KILL candidate(s)", text)


if __name__ == "__main__":
    unittest.main()
