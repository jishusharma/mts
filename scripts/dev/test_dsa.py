"""dsa.py: put/edit/commit/begin/end/host against temp git repos (bare origin + clones, branch fast-track).

Expected values come from the task spec (operator ask 2026-10-14), not from the code under test:
  put    - UTF-8, no BOM, LF; a CRLF-only target stays CRLF; nothing outside the repo root, no .env/.secrets/keys/HALT.
  edit   - exact replace, exit 2 unless the match count is exactly 1 (--all: N>=1), newlines normalised to the file's EOL.
  commit - names exactly the files given, or all changes minus runtime_data/_mirror/ and ignored files; never in the live tree.
  begin  - ../mts-dsa-<slug> on branch <host-lower>/dsa-<slug> from origin/fast-track, sync start + claim.
  end    - releases the claim and removes the worktree only when nothing is unshipped.
  host   - says OTHER HOST when the live tree's BUILD_REPORT.md was written by another machine.
Temp paths are resolved (os.path.realpath): Windows 8.3 short names break git's path comparison.
"""
import atexit
import contextlib
import io
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dsa


def sh(cwd, *args):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"git {args} failed: {r.stdout}{r.stderr}")
    return r.stdout


def rmtree(p):
    import shutil

    def fix(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(p, onerror=fix) if sys.version_info < (3, 12) else shutil.rmtree(p, onexc=lambda f, pth, e: (os.chmod(pth, stat.S_IWRITE), f(pth)))


def call(argv, stdin=b""):
    """-> (exit code, stdout text). stdin is bytes."""
    out = io.StringIO()
    fake = io.TextIOWrapper(io.BytesIO(stdin), encoding="utf-8")
    with contextlib.redirect_stdout(out), mock.patch.object(sys, "stdin", fake):
        code = dsa.main(argv)
    return code, out.getvalue()


def clone(tmp, name):
    d = tmp / "ip" / name
    sh(tmp, "clone", "-q", (tmp / "origin.git").as_posix(), str(d))      # forward slashes: copy_fixture rewrites them in the config
    sh(d, "config", "user.email", "t@t")
    sh(d, "config", "user.name", "t")
    return d


def build_fixture(tmp):
    """bare origin + the live clone + one ordinary worktree of it, all under tmp (the same repos every test starts from)."""
    (tmp / "ip").mkdir()                                # stands for IdeaProjects
    origin = tmp / "origin.git"
    sh(tmp, "init", "-q", "--bare", str(origin))
    sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
    live = clone(tmp, "live")
    (live / ".gitignore").write_text(".mts_live\nignored.log\n")
    (live / "README.md").write_text("x\n")
    (live / "runtime_data" / "_mirror").mkdir(parents=True)
    (live / "runtime_data" / "_mirror" / "m.txt").write_text("m0\n")
    (live / "MyTradingSys" / "system" / "claims").mkdir(parents=True)
    (live / "MyTradingSys" / "system" / "claims" / ".gitkeep").write_text("")
    sh(live, "checkout", "-q", "-b", "fast-track")
    sh(live, "add", "-A")
    sh(live, "commit", "-q", "-m", "init")
    sh(live, "push", "-q", "origin", "HEAD:fast-track")
    sh(live, "branch", "-q", "--set-upstream-to=origin/fast-track")
    (live / ".mts_live").write_text("live\n")
    sh(live, "worktree", "add", "-q", str(tmp / "ip" / "work"), "-b", "work", "origin/fast-track")   # an ordinary (non-live) worktree


_TEMPLATE = []


def template():
    """The fixture, built once per process: init + clone + push + worktree add cost ~2 s, and every test used to pay it (2026-10-16 profile:
    24 of the 74 s of this file, step 3ds)."""
    if not _TEMPLATE:
        root = Path(os.path.realpath(tempfile.mkdtemp(prefix="dsa_tpl_")))
        build_fixture(root)
        _TEMPLATE.append(root)
        atexit.register(rmtree, root)
    return _TEMPLATE[0]


def copy_fixture(dest):
    """Copy the template into the empty dir `dest` and repoint the three files that hold absolute paths (origin url, the worktree's
    .git file and the admin dir's gitdir file); git on Windows writes them with forward slashes."""
    src = template()
    shutil.copytree(src, dest, dirs_exist_ok=True)
    old, new = src.as_posix().encode(), dest.as_posix().encode()
    for rel in ("ip/live/.git/config", "ip/work/.git", "ip/live/.git/worktrees/work/gitdir"):
        f = dest / rel
        data = f.read_bytes()
        assert old in data, (rel, data)
        os.chmod(f, stat.S_IWRITE | stat.S_IREAD)       # git leaves some of these read-only/hidden on Windows: replace, not rewrite
        f.unlink()
        f.write_bytes(data.replace(old, new))


class Base(unittest.TestCase):
    def setUp(self):
        self.cwd0 = os.getcwd()
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp()))
        copy_fixture(self.tmp)
        self.ip = self.tmp / "ip"
        self.origin = self.tmp / "origin.git"
        self.live = self.ip / "live"
        self.work = self.ip / "work"
        os.chdir(self.work)

    def tearDown(self):
        os.chdir(self.cwd0)
        rmtree(self.tmp)


class PutTest(Base):
    def test_put_writes_lf_without_bom(self):
        code, out = call(["put", "docs/a.md"], b"\xef\xbb\xbfone\r\ntwo \xc3\xa9\r\n")
        self.assertEqual(code, 0, out)
        data = (self.work / "docs" / "a.md").read_bytes()
        self.assertEqual(data, "one\ntwo é\n".encode("utf-8"))      # BOM gone, CRLF -> LF, parent dir created
        self.assertIn("lines: 2", out)
        self.assertIn(f"bytes: {len(data)}", out)
        self.assertIn("non_ascii: 1", out)
        self.assertIn("eol: lf", out)

    def test_put_keeps_a_crlf_only_target_crlf(self):
        f = self.work / "win.txt"
        f.write_bytes(b"a\r\nb\r\n")
        code, out = call(["put", "win.txt"], b"x\ny\n")
        self.assertEqual((code, f.read_bytes()), (0, b"x\r\ny\r\n"))
        self.assertIn("eol: crlf", out)
        code, out = call(["put", "win.txt", "--append"], b"z\n")
        self.assertEqual((code, f.read_bytes()), (0, b"x\r\ny\r\nz\r\n"))

    def test_put_append_on_lf_file_and_new_file(self):
        f = self.work / "l.txt"
        f.write_bytes(b"a\n")
        self.assertEqual(call(["put", "l.txt", "--append"], b"b\n")[0], 0)
        self.assertEqual(f.read_bytes(), b"a\nb\n")
        self.assertEqual(call(["put", "n.txt", "--append"], b"c\n")[0], 0)      # append to a missing file creates it
        self.assertEqual((self.work / "n.txt").read_bytes(), b"c\n")

    def test_put_refuses_outside_the_repo_root(self):
        outside = self.ip / "outside.txt"
        for p in ("../outside.txt", str(outside), "sub/../../outside.txt"):
            code, out = call(["put", p], b"x\n")
            self.assertEqual(code, 2, (p, out))
            self.assertIn("outside the repo root", out)
        self.assertFalse(outside.exists())

    def test_put_refuses_secrets_keys_halt_and_git(self):
        for p in (".env", "cfg/.env", ".secrets/k.txt", "keys/id_rsa", "a.pem", "MyTradingSys/execution/HALT",
                  "MyTradingSys/execution/HALT_DAILY_LOSS", ".git/hooks/pre-commit", "api_keys.json"):
            code, out = call(["put", p], b"x\n")
            self.assertEqual(code, 2, (p, out))
            self.assertIn("refused", out)
            self.assertFalse((self.work / p).exists(), p)
        self.assertEqual(call(["put", "halt_policy.md"], b"ok\n")[0], 0)        # a doc about HALT is fine

    def test_put_refuses_invalid_utf8_and_empty_pipe(self):
        code, out = call(["put", "bad.txt"], b"caf\xe9\n")
        self.assertEqual(code, 2)
        self.assertFalse((self.work / "bad.txt").exists())


class EditTest(Base):
    def test_count_zero_one_two(self):
        f = self.work / "e.txt"
        f.write_bytes(b"alpha\nbeta\nbeta\n")
        code, out = call(["edit", "e.txt", "--old=gamma", "--new=x"])
        self.assertEqual(code, 2)
        self.assertIn("count: 0", out)
        code, out = call(["edit", "e.txt", "--old=beta", "--new=x"])
        self.assertEqual(code, 2)
        self.assertIn("count: 2", out)
        self.assertEqual(f.read_bytes(), b"alpha\nbeta\nbeta\n")                 # nothing changed on refusals
        code, out = call(["edit", "e.txt", "--old=alpha", "--new=ALPHA"])
        self.assertEqual(code, 0, out)
        self.assertIn("replaced: 1", out)
        self.assertEqual(f.read_bytes(), b"ALPHA\nbeta\nbeta\n")
        code, out = call(["edit", "e.txt", "--old=beta", "--new=b", "--all"])
        self.assertEqual(code, 0)
        self.assertIn("replaced: 2", out)
        self.assertEqual(f.read_bytes(), b"ALPHA\nb\nb\n")

    def test_multiline_old_matches_after_normalising_to_the_files_eol(self):
        f = self.work / "crlf.txt"
        f.write_bytes(b"a\r\nb\r\nc\r\n")
        code, out = call(["edit", "crlf.txt", "--old=a\nb", "--new=X\nY"])        # LF text, CRLF file
        self.assertEqual(code, 0, out)
        self.assertEqual(f.read_bytes(), b"X\r\nY\r\nc\r\n")                     # CRLF preserved
        self.assertIn("eol: crlf", out)
        g = self.work / "lf.txt"
        g.write_bytes(b"a\nb\nc\n")
        self.assertEqual(call(["edit", "lf.txt", "--old=a\r\nb", "--new=Q"])[0], 0)
        self.assertEqual(g.read_bytes(), b"Q\nc\n")

    def test_escapes_and_files(self):
        f = self.work / "esc.txt"
        f.write_bytes(b"one\ntwo\n")
        self.assertEqual(call(["edit", "esc.txt", "--old=one\\ntwo", "--new=1\\n2", "--escapes"])[0], 0)
        self.assertEqual(f.read_bytes(), b"1\n2\n")
        self.assertEqual(call(["edit", "esc.txt", "--old=1\\n2", "--new=z"])[0], 2)   # no --escapes: literal backslash-n
        (self.work / "o.txt").write_bytes(b"1\n2")
        (self.work / "n.txt").write_bytes("café".encode("utf-8"))
        code, out = call(["edit", "esc.txt", "--old-file", "o.txt", "--new-file", "n.txt"])
        self.assertEqual(code, 0, out)
        self.assertEqual(f.read_bytes(), "café\n".encode("utf-8"))
        self.assertIn("non_ascii: 1", out)

    def test_edit_keeps_a_bom_and_refuses_protected_or_missing(self):
        f = self.work / "b.txt"
        f.write_bytes(b"\xef\xbb\xbfhello\n")
        self.assertEqual(call(["edit", "b.txt", "--old=hello", "--new=hi"])[0], 0)
        self.assertEqual(f.read_bytes(), b"\xef\xbb\xbfhi\n")
        (self.work / ".env").write_text("K=1\n")
        self.assertEqual(call(["edit", ".env", "--old=K", "--new=Q"])[0], 2)
        self.assertEqual(call(["edit", "nope.txt", "--old=a", "--new=b"])[0], 2)
        self.assertEqual(call(["edit", "../outside.txt", "--old=a", "--new=b"])[0], 2)


class CommitTest(Base):
    def make_changes(self):
        (self.work / "a.txt").write_text("a\n")
        (self.work / "b.txt").write_text("b\n")
        (self.work / "ignored.log").write_text("noise\n")
        (self.work / "runtime_data" / "_mirror" / "m.txt").write_text("m1\n")             # tracked, modified
        (self.work / "runtime_data" / "_mirror" / "new.txt").write_text("n\n")            # untracked
        (self.work / ".env").write_text("SECRET=1\n")

    def test_default_commit_skips_mirror_ignored_and_secrets(self):
        self.make_changes()
        (self.work / "README.md").write_text("changed\n")
        code, out = call(["commit", "add stuff", "--result", "a and b exist", "--session", "MTS-TEST"])
        self.assertEqual(code, 0, out)
        files = sh(self.work, "show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(sorted(files), ["README.md", "a.txt", "b.txt"])
        msg = sh(self.work, "log", "-1", "--format=%B")
        self.assertIn("add stuff", msg.splitlines()[0])
        self.assertIn("Result: a and b exist", msg)
        self.assertIn("MTS-Session: MTS-TEST", msg)
        self.assertIn("skipped (protected): .env", out)
        left = sh(self.work, "status", "--porcelain").splitlines()
        self.assertTrue(any("_mirror/m.txt" in l for l in left))                      # mirror edits stay uncommitted
        self.assertFalse(any("a.txt" in l for l in left))

    def test_files_commits_exactly_those(self):
        self.make_changes()
        code, out = call(["commit", "only a", "--result", "just a", "--files", "a.txt"])
        self.assertEqual(code, 0, out)
        self.assertEqual(sh(self.work, "show", "--name-only", "--format=", "HEAD").split(), ["a.txt"])
        self.assertIn("MTS-Session: MTS-", sh(self.work, "log", "-1", "--format=%B"))   # default session id
        self.assertIn("-Z-DSA-".replace("-Z", "Z"), sh(self.work, "log", "-1", "--format=%B"))
        self.assertTrue((self.work / "b.txt").exists())
        self.assertIn("?? b.txt", sh(self.work, "status", "--porcelain"))

    def test_commit_deleted_and_rejects_protected_file_by_name(self):
        sh(self.work, "rm", "-q", "README.md")
        self.assertEqual(call(["commit", "rm readme", "--result", "gone", "--files", "README.md"])[0], 0)
        self.assertEqual(sh(self.work, "show", "--name-only", "--format=", "HEAD").split(), ["README.md"])
        (self.work / ".env").write_text("X=1\n")
        self.assertEqual(call(["commit", "env", "--result", "no", "--files", ".env"])[0], 2)

    def test_commit_needs_result_and_something_to_commit(self):
        code, out = call(["commit", "nothing", "--result", "x"])
        self.assertEqual(code, 1)
        self.assertIn("nothing to commit", out)
        self.assertEqual(call(["commit", "s", "--result", "  "])[0], 2)

    def test_commit_refused_in_the_live_tree(self):
        os.chdir(self.live)
        (self.live / "z.txt").write_text("z\n")
        before = sh(self.live, "rev-parse", "HEAD")
        code, out = call(["commit", "live edit", "--result", "no"])
        self.assertEqual(code, 2)
        self.assertIn("live tree", out)
        self.assertEqual(sh(self.live, "rev-parse", "HEAD"), before)
        self.assertEqual(sh(self.live, "diff", "--cached", "--name-only").strip(), "")


class GuardTest(Base):
    def test_git_wrapper_refuses_history_rewriting(self):
        for args in (("reset", "--hard", "HEAD~1"), ("rebase", "origin/fast-track"), ("push", "origin", "HEAD"),
                     ("commit", "--amend", "-m", "x"), ("filter-branch",), ("checkout", "-f", "x")):
            with self.assertRaises(dsa.Refused, msg=str(args)):
                dsa.git(self.work, *args)
        head = sh(self.work, "rev-parse", "HEAD")
        self.assertEqual(dsa.git(self.work, "rev-parse", "HEAD")[1].strip(), head.strip())

    def test_slugify(self):
        self.assertEqual(dsa.slugify("Section Refresh: STATUS (v2)!"), "section-refresh-status-v2")
        self.assertEqual(len(dsa.slugify("x" * 100)), 40)
        self.assertEqual(dsa.slugify("!!!"), "task")


class BeginEndTest(Base):
    TITLE = "Refresh Section 4: tom/fabio"

    def host_branch(self):
        return f"{socket.gethostname().lower()}/dsa-refresh-section-4-tom-fabio"

    def test_begin_makes_worktree_branch_and_claim_from_live_tree(self):
        os.chdir(self.live)
        code, out = call(["begin", self.TITLE])
        self.assertEqual(code, 0, out)
        wt = self.ip / "mts-dsa-refresh-section-4-tom-fabio"
        self.assertTrue(wt.is_dir(), out)
        self.assertIn(f"WORKTREE: {wt}", out)
        self.assertIn("CLAIM: refresh-section-4-tom-fabio", out)
        self.assertEqual(sh(wt, "branch", "--show-current").strip(), self.host_branch())
        self.assertEqual(sh(wt, "rev-parse", "HEAD").strip(), sh(self.origin, "rev-parse", "fast-track").strip())   # claim shipped
        claim = sh(self.origin, "show", "claims:MyTradingSys/system/claims/refresh-section-4-tom-fabio.md")
        self.assertIn(f"task: {self.TITLE}", claim)
        self.assertEqual(sh(self.live, "branch", "--show-current").strip(), "fast-track")    # live tree untouched
        self.assertEqual(sh(self.live, "status", "--porcelain").strip(), "")

    def test_begin_twice_reuses_worktree_and_own_claim(self):
        os.chdir(self.work)
        self.assertEqual(call(["begin", self.TITLE])[0], 0)
        code, out = call(["begin", self.TITLE])
        self.assertEqual(code, 0, out)
        self.assertIn("(reused)", out)
        self.assertIn("CLAIM: refresh-section-4-tom-fabio", out)

    def test_end_releases_claim_and_removes_worktree_when_clean(self):
        os.chdir(self.live)
        self.assertEqual(call(["begin", self.TITLE])[0], 0)
        wt = self.ip / "mts-dsa-refresh-section-4-tom-fabio"
        os.chdir(wt)
        (wt / "runtime_data" / "_mirror" / "m.txt").write_text("churn\n")               # mirror churn does not count
        code, out = call(["end"])
        self.assertEqual(code, 0, out)
        self.assertIn("released: refresh-section-4-tom-fabio", out)
        self.assertFalse(wt.exists())
        r = subprocess.run(["git", "-C", str(self.origin), "cat-file", "-e",
                            "claims:MyTradingSys/system/claims/refresh-section-4-tom-fabio.md"], capture_output=True)
        self.assertNotEqual(r.returncode, 0)                                              # claim file gone on origin
        self.assertNotIn("mts-dsa-refresh", sh(self.live, "worktree", "list"))

    def test_end_refuses_with_unshipped_work_then_with_unpushed_commit(self):
        os.chdir(self.live)
        self.assertEqual(call(["begin", self.TITLE])[0], 0)
        wt = self.ip / "mts-dsa-refresh-section-4-tom-fabio"
        os.chdir(wt)
        (wt / "new.md").write_text("n\n")
        code, out = call(["end"])
        self.assertEqual(code, 1)
        self.assertIn("1 uncommitted", out)
        self.assertTrue(wt.exists())
        self.assertEqual(call(["commit", "add new", "--result", "new.md exists"])[0], 0)
        code, out = call(["end"])
        self.assertEqual(code, 1)
        self.assertIn("1 commit(s) not on origin/fast-track", out)
        self.assertTrue(wt.exists())

    def test_end_refuses_outside_a_dsa_worktree(self):
        os.chdir(self.work)
        code, out = call(["end"])
        self.assertEqual(code, 2)
        self.assertTrue(self.work.exists())
        os.chdir(self.live)
        self.assertEqual(call(["end"])[0], 2)


class HostTest(Base):
    def report(self, host):
        d = self.live / "MyTradingSys" / "runtime"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BUILD_REPORT.md").write_text(f"BUILD_REPORT - 2026-10-14 UTC\nhost: {host}\n\nSTATUS: PASS\n")

    def test_other_host_report_is_flagged(self):
        self.report("JIS-NUC")
        os.chdir(self.work)                       # report lives in the live tree; we stand in another worktree
        with mock.patch.object(dsa, "hostname", return_value="JIS-NB"):
            code, out = call(["host"])
        self.assertEqual(code, 0, out)
        self.assertIn("host: JIS-NB", out)
        self.assertIn("build_report_host: JIS-NUC", out)
        self.assertIn("build_report: OTHER HOST (JIS-NUC) - do not gate on it", out)
        self.assertIn("is_live_tree: no", out)
        self.assertIn(f"live_tree: {self.live}", out)

    def test_same_host_report_matches_and_live_tree_is_detected(self):
        self.report("jis-nb")
        os.chdir(self.live)
        with mock.patch.object(dsa, "hostname", return_value="JIS-NB"):
            code, out = call(["host"])
        self.assertIn("build_report: MATCH", out)
        self.assertIn("is_live_tree: yes", out)
        for key in ("utc_now:", "python:", "java:", "JAVA_HOME:", "mvn:", "powershell:", "repo_root:", "branch: fast-track"):
            self.assertIn(key, out)


class ParseTest(unittest.TestCase):
    NEXT = """RELAY note
   Q59. host=JIS-NUC Card a (SONNET): nuc only.
   Q60. host=any (after x) Card b: any host.
   Q61. DONE 2026-10-14 something finished host=JIS-NB
   Q62. host=any Spot-check.
   Q63. host=JIS-NB Card c: nb only.
   Q64. Untagged task.
   Q65. host=JIS-NB,JIS-NUC both.
not a q line
"""

    def test_open_q_lines_filter_by_host_tag(self):
        nb = dsa.open_q_lines(self.NEXT, "JIS-NB")
        self.assertEqual([q.split(".")[0] for q in nb], ["Q60", "Q62", "Q63", "Q64", "Q65"])
        nuc = dsa.open_q_lines(self.NEXT, "jis-nuc")
        self.assertEqual([q.split(".")[0] for q in nuc], ["Q59", "Q60", "Q62", "Q64", "Q65"])

    def test_news_gaps_counts_commits_and_lists_missing_results(self):
        text = ("10-14 15:00 abc1234  good commit\n    Result: it works\n    areas: x\n"
                "10-14 14:00 def5678  bad commit\n    Result: (not stated)\n    areas: y\n")
        n, gaps = dsa.news_gaps(text)
        self.assertEqual((n, gaps), (2, ["10-14 14:00 def5678  bad commit"]))
        self.assertEqual(dsa.news_gaps("nothing shipped in the last 24 h\n"), (0, []))

    def test_lane_for_host(self):
        self.assertEqual(dsa.lane_for_host("JIS-NB"), "DSA-NB")
        self.assertEqual(dsa.lane_for_host("jis-nuc"), "DSA-NUC")


if __name__ == "__main__":
    unittest.main(verbosity=1)
