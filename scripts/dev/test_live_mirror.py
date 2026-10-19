"""live_mirror.py: tests derived from MyTradingSys/system/LIVE_MIRROR.md (and the Opus review of it)."""
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_mirror as lm

REPO = Path(__file__).resolve().parents[2]
T0 = dt.datetime(2026, 10, 9, 20, 0, tzinfo=dt.timezone.utc)


def put(repo, rel, text):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def age(path, minutes):
    t = (T0 - dt.timedelta(minutes=minutes)).timestamp()
    os.utime(path, (t, t))


def make_live(tmp):
    live = Path(tmp) / "live"
    live.mkdir()
    (live / ".mts_live").write_text("x")
    snap = put(live, "runtime_data/snapshots/s1.json",
               json.dumps({"vwap": 82600.5, "regime": "RANGE", "oi": {"change_1h": 0.07}}))
    age(snap, 1)
    put(live, "runtime_data/last_alert.json", json.dumps({"number": 273, "price": 83106.5, "ssot_thesis": "x"}))
    put(live, "runtime_data/live_runner.log", "".join(f"line {i}\n" for i in range(5000)))
    put(live, "MyTradingSys/execution/auto_trades.jsonl", '{"outcome":"skipped"}\n')
    put(live, "MyTradingSys/execution/AUTO_PAUSE", "owner x")
    return live


class MirrorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.live = make_live(self.tmp)
        self.root = Path(self.tmp) / "share"
        self.root.mkdir()
        self.nuc = Path(self.tmp) / "nuc"
        self.nuc.mkdir()

    def pub(self, now=T0):
        return lm.publish(self.live, self.root, now=now)

    # --- who may run what
    def test_publish_refuses_outside_live_tree(self):
        with self.assertRaises(lm.MirrorError):
            lm.publish(self.nuc, self.root)

    def test_pull_refuses_in_live_tree(self):
        self.pub()
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.live, self.root)

    # --- secrets
    def test_allowlisted_secret_path_fails_publish_and_leaves_nothing(self):
        put(self.live, "MyTradingSys/execution/plans/x.secret.json", "{}")
        before = set(p.name for p in self.root.iterdir())
        with self.assertRaises(lm.MirrorError):
            self.pub()
        self.assertEqual(before, set(p.name for p in self.root.iterdir()))

    def test_secrets_dir_never_copied(self):
        put(self.live, ".secrets/deribit.json", '{"client_secret": "abcdefghijklmnopqrstuvwxyz0123"}')
        m = self.pub()
        self.assertFalse(any(".secrets" in f["rel"] for f in m["files"]))

    def test_key_shaped_line_redacted_hash_kept(self):
        h = hashlib.sha256(b"a").hexdigest()
        put(self.live, "MyTradingSys/runtime/alerts/5m.jsonl",
            '{"plan_id":"%s"}\n{"api_key": "AbCdEfGhIjKlMnOpQrSt1234"}\n' % h)
        m = self.pub()
        text = (self.root / m["version"] / "MyTradingSys/runtime/alerts/5m.jsonl").read_text()
        self.assertIn(h, text)
        self.assertNotIn("AbCdEfGhIj", text)
        self.assertEqual(m["redacted_lines"], 1)

    # --- content and flags
    def test_tail_and_flags(self):
        m = self.pub()
        log = (self.root / m["version"] / "runtime_data/live_runner.log").read_text().splitlines()
        self.assertEqual((len(log), log[-1]), (3000, "line 4999"))
        self.assertTrue(m["flags"]["AUTO_PAUSE"])
        self.assertFalse(m["flags"]["HALT"])

    def test_pointer_moves_last_and_old_versions_pruned(self):
        for i in range(5):
            self.pub(T0 + dt.timedelta(minutes=i))
        vs = sorted(p.name for p in self.root.iterdir() if p.is_dir())
        self.assertEqual(len(vs), lm.KEEP_VERSIONS)
        self.assertEqual((self.root / "CURRENT").read_text(), vs[-1])

    # --- pull
    def test_pull_roundtrip_lands_in_mirror_dir_not_runtime_paths(self):
        self.pub()
        self.assertEqual(lm.pull(self.nuc, self.root)[0], "pulled")
        self.assertTrue((self.nuc / lm.MIRROR_DIR / "runtime_data/last_alert.json").exists())
        self.assertFalse((self.nuc / "runtime_data/last_alert.json").exists())
        self.assertEqual(lm.pull(self.nuc, self.root)[0], "up to date")

    def test_pull_does_not_modify_share(self):
        self.pub()

        def snap():
            return sorted((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in self.root.rglob("*"))
        before = snap()
        lm.pull(self.nuc, self.root)
        self.assertEqual(before, snap())

    def test_bad_hash_keeps_previous_mirror(self):
        self.pub()
        lm.pull(self.nuc, self.root)
        good = (self.nuc / lm.MIRROR_DIR / "manifest.json").read_text()
        m = self.pub(T0 + dt.timedelta(minutes=5))
        (self.root / m["version"] / "runtime_data/last_alert.json").write_text("tampered")
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)
        self.assertEqual(good, (self.nuc / lm.MIRROR_DIR / "manifest.json").read_text())
        self.assertFalse([p for p in self.nuc.rglob("*") if ".tmp" in p.name])

    def test_missing_or_partial_pointer_fails(self):
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)
        (self.root / "CURRENT").write_text("v2026")
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)
        (self.root / "CURRENT").write_text("v20261009T200000Z")
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)

    def test_manifest_path_escape_refused(self):
        m = self.pub()
        mp = self.root / m["version"] / "manifest.json"
        d = json.loads(mp.read_text())
        d["files"].append({"rel": "../evil.txt", "size": 0, "sha256": hashlib.sha256(b"").hexdigest(),
                           "mtime": T0.isoformat()})
        mp.write_text(json.dumps(d))
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)

    def test_lock_serialises_and_stale_lock_recovers(self):
        lock = self.nuc / "runtime_data" / "_mirror.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("123")
        self.pub()
        with self.assertRaises(lm.MirrorError):
            lm.pull(self.nuc, self.root)
        old = time.time() - lm.LOCK_STALE_S - 5
        os.utime(lock, (old, old))
        self.assertEqual(lm.pull(self.nuc, self.root)[0], "pulled")

    # --- brief
    def pulled(self):
        self.pub()
        lm.pull(self.nuc, self.root)

    def test_brief_ok_warn_stale_boundaries(self):
        self.pulled()
        first = lambda mins: lm.brief_lines(self.nuc, now=T0 + dt.timedelta(minutes=mins))
        self.assertIn(" OK:", first(5)[0])
        self.assertIn(" WARN:", first(lm.WARN_MIN + 1)[0])
        out = "\n".join(first(lm.STALE_MIN + 1))
        self.assertIn(" STALE:", out)
        self.assertIn("do NOT present", out)

    def test_brief_stale_when_manifest_fresh_but_snapshot_old(self):
        age(self.live / "runtime_data/snapshots/s1.json", 300)
        self.pulled()
        self.assertIn(" STALE:", lm.brief_lines(self.nuc, now=T0 + dt.timedelta(minutes=1))[0])

    def test_brief_no_mirror_never_reads_git_snapshot(self):
        put(self.nuc, "runtime_data/snapshots/git_committed.json", '{"vwap": 1}')
        out = "\n".join(lm.brief_lines(self.nuc))
        self.assertIn("NO MIRROR", out)
        self.assertNotIn("vwap", out)

    def test_brief_shows_flags_alert_and_snapshot_fields(self):
        self.pulled()
        out = "\n".join(lm.brief_lines(self.nuc, now=T0 + dt.timedelta(minutes=2)))
        for needle in ("AUTO_PAUSE", "number=273", "vwap=82600.5", "regime=RANGE", "mirror@2026-10-09 20:00Z"):
            self.assertIn(needle, out)

    GENERATED = ("MyTradingSys/runtime/oi_live/oi_1m.csv", "MyTradingSys/runtime/oi_live/oi_5m_30d.csv",
                 "MyTradingSys/research/htf_context/2026-10-08.jsonl")

    def test_generated_files_untracked_in_git_are_still_published(self):
        """Card move-live-host-generated-files: oi_live csv and htf_context are git-ignored and untracked, so the mirror must read the
        working tree, not git. Present + ignored -> published."""
        subprocess.run(["git", "init", "-q"], cwd=self.live, check=True)
        shutil.copy(REPO / ".gitignore", self.live / ".gitignore")
        for rel in self.GENERATED:
            put(self.live, rel, "a,b\n1,2\n")
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=self.live,
                            capture_output=True, text=True).stdout
        self.assertEqual([r for r in self.GENERATED if r in st], [], "generated files must be ignored by git")
        got = {f["rel"] for f in self.pub()["files"]}
        self.assertTrue(set(self.GENERATED) <= got)

    def test_generated_files_absent_publish_still_works_and_lists_nothing_invented(self):
        """Absent generated inputs (fresh clone, merge removed them) are skipped, never crash, never faked; the brief still keys on the snapshot."""
        m = self.pub()
        got = {f["rel"] for f in m["files"]}
        self.assertEqual(got & set(self.GENERATED), set())
        lm.pull(self.nuc, self.root)
        self.assertIn(" STALE:", "\n".join(lm.brief_lines(self.nuc, now=T0 + dt.timedelta(minutes=lm.STALE_MIN + 1))))

    # --- brief pulls first when this tree's copy is missing or old (trees made by the App never run `sync.py start`)
    def test_brief_pulls_when_no_mirror_yet(self):
        self.pub()
        out = lm.brief(self.nuc, self.root)
        self.assertIn("pulled v20261009T200000Z", out[0])
        self.assertTrue((self.nuc / lm.MIRROR_DIR / "manifest.json").exists())
        self.assertIn("mirror@2026-10-09 20:00Z", "\n".join(out))

    def test_brief_pulls_the_newer_version_when_the_copy_is_old(self):
        self.pulled()
        m2 = self.pub(T0 + dt.timedelta(minutes=5))
        out = lm.brief(self.nuc, self.root)  # the real clock is far past T0: the copy is stale
        self.assertIn("pulled " + m2["version"], out[0])
        manifest = json.loads((self.nuc / lm.MIRROR_DIR / "manifest.json").read_text())
        self.assertEqual(manifest["version"], m2["version"])

    def test_failed_publish_is_recorded_and_shown_in_brief_then_cleared(self):
        self.pulled()
        bad = put(self.live, "MyTradingSys/execution/plans/x.secret.json", "{}")
        with self.assertRaises(lm.MirrorError):
            lm.publish_recorded(self.live, self.root, now=T0 + dt.timedelta(minutes=5))
        with self.assertRaises(lm.MirrorError):
            lm.publish_recorded(self.live, self.root, now=T0 + dt.timedelta(minutes=10))
        line = lm.publish_fail_line(self.root, now=T0 + dt.timedelta(minutes=12))
        self.assertIn("PUBLISHER FAILING for 7 min", line)
        out = lm.brief(self.nuc, self.root, now=T0 + dt.timedelta(minutes=12))
        self.assertTrue(any("PUBLISHER FAILING" in l for l in out))
        bad.unlink()
        lm.publish_recorded(self.live, self.root, now=T0 + dt.timedelta(minutes=15))
        self.assertIsNone(lm.publish_fail_line(self.root))

    def test_main_publish_unexpected_error_exits_nonzero_and_records(self):
        with mock.patch.object(lm, "publish", side_effect=OSError("disk full")):
            rc = lm.main(["publish", "--repo", str(self.live), "--root", str(self.root)])
        self.assertEqual(rc, 3)
        self.assertIn("disk full", lm.publish_fail_line(self.root))

    def test_brief_does_not_pull_while_the_copy_is_fresh(self):
        now = lm.utcnow()
        lm.publish(self.live, self.root, now=now - dt.timedelta(minutes=3))
        lm.pull(self.nuc, self.root)
        lm.publish(self.live, self.root, now=now - dt.timedelta(minutes=1))
        out = lm.brief(self.nuc, self.root)
        self.assertFalse(any(l.startswith("mirror: ") for l in out), out)
        manifest = json.loads((self.nuc / lm.MIRROR_DIR / "manifest.json").read_text())
        self.assertEqual(manifest["version"], lm.stamp(now - dt.timedelta(minutes=3)))

    def test_brief_with_unreachable_root_still_says_no_mirror(self):
        out = lm.brief(self.nuc, Path(self.tmp) / "no-such-share")
        self.assertIn("pull skipped", out[0])
        self.assertIn("NO MIRROR", "\n".join(out))

    def test_brief_never_pulls_into_the_live_tree(self):
        self.pub()
        out = lm.brief(self.live, self.root)
        self.assertFalse(any(l.startswith("mirror: ") for l in out), out)
        self.assertFalse((self.live / lm.MIRROR_DIR).exists())

    def test_brief_gives_up_on_a_hung_share(self):
        def hang(repo, root):
            time.sleep(3)
        with mock.patch.object(lm, "pull", hang):
            t0 = time.time()
            out = lm.brief(self.nuc, self.root, pull_timeout=0.2)
        self.assertLess(time.time() - t0, 2)
        self.assertIn("timed out", out[0])

    def test_brief_lines_are_clipped_to_one_screen_width(self):
        put(self.live, "runtime_data/snapshots/s1.json",
            json.dumps({f"k{i}": {"vwap": 82600.5 + i, "poc": 1, "regime": "RANGE" * 5} for i in range(30)}))
        age(self.live / "runtime_data/snapshots/s1.json", 1)
        self.pub()
        out = lm.brief(self.nuc, self.root)
        self.assertTrue(all(len(l) <= lm.BRIEF_WIDTH for l in out), [len(l) for l in out])
        self.assertTrue(any(l.endswith("...") for l in out))

    # --- export-obs
    def test_export_obs_dedups(self):
        put(self.nuc, "runtime_data/observations/captures/2026-10-09.jsonl", '{"obs_id":"a1"}\n{"obs_id":"b2"}\n')
        self.assertEqual(lm.export_obs(self.nuc)[0], 2)
        self.assertEqual(lm.export_obs(self.nuc)[0], 0)
        put(self.nuc, "runtime_data/observations/captures/2026-10-10.jsonl", '{"obs_id":"c3"}\n')
        self.assertEqual(lm.export_obs(self.nuc)[0], 1)


class DefaultRootTest(unittest.TestCase):
    """Which folder a session reads: JIS-NB sessions run as a user the SMB share ACL does not list (only E-ngineers and
    mtsworker are), so on JIS-NB every tree reads the local folder; other hosts keep the UNC share."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.local = Path(self.tmp) / "Mirror"
        self.local.mkdir()
        self.work = Path(self.tmp) / "work"
        self.work.mkdir()
        self.marked = Path(self.tmp) / "marked"
        self.marked.mkdir()
        (self.marked / ".mts_live").write_text("x")
        p = mock.patch.object(lm, "LIVE_ROOT", str(self.local))
        p.start()
        self.addCleanup(p.stop)
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("MTS_MIRROR_ROOT", None)

    def host(self, name):
        p = mock.patch.object(lm.socket, "gethostname", return_value=name)
        p.start()
        self.addCleanup(p.stop)

    def test_worktree_on_jis_nb_reads_local_folder(self):
        self.host("JIS-NB")
        self.assertEqual(lm.default_root(self.work), str(self.local))

    def test_hostname_case_does_not_matter(self):
        self.host("jis-nb")
        self.assertEqual(lm.default_root(self.work), str(self.local))

    def test_other_host_keeps_unc_share(self):
        self.host("JIS-NUC")
        self.assertEqual(lm.default_root(self.work), lm.DEFAULT_ROOT)

    def test_jis_nb_without_local_folder_falls_back_to_unc(self):
        self.host("JIS-NB")
        shutil.rmtree(self.local)
        self.assertEqual(lm.default_root(self.work), lm.DEFAULT_ROOT)

    def test_live_tree_uses_local_folder_on_any_host(self):
        self.host("SOMEWHERE")
        shutil.rmtree(self.local)  # publish creates the version folder; the marker alone decides
        self.assertEqual(lm.default_root(self.marked), str(self.local))

    def test_main_pull_in_worktree_on_jis_nb_reads_local_folder(self):
        self.host("JIS-NB")
        live = make_live(self.tmp)
        lm.publish(live, self.local, now=T0)
        self.assertEqual(lm.main(["pull", "--repo", str(self.work)]), 0)
        self.assertTrue((self.work / lm.MIRROR_DIR / "manifest.json").exists())

    def test_main_env_override_wins(self):
        self.host("JIS-NB")
        other = Path(self.tmp) / "other"
        other.mkdir()
        os.environ["MTS_MIRROR_ROOT"] = str(other)
        live = make_live(self.tmp)
        lm.publish(live, self.local, now=T0)  # data only in the local folder; the override points at an empty one
        self.assertEqual(lm.main(["pull", "--repo", str(self.work)]), 2)
        self.assertFalse((self.work / lm.MIRROR_DIR).exists())

    def test_main_explicit_root_wins_over_default(self):
        self.host("JIS-NB")
        elsewhere = Path(self.tmp) / "elsewhere"
        elsewhere.mkdir()
        self.assertEqual(lm.main(["pull", "--repo", str(self.work), "--root", str(elsewhere)]), 2)

    def test_auto_trades_stays_a_500_line_tail(self):
        modes = dict(lm.ALLOW)
        self.assertEqual(modes["MyTradingSys/execution/auto_trades.jsonl"], ("tail", 500))


class RepoContractTest(unittest.TestCase):
    def test_no_trading_or_gating_code_reads_the_mirror(self):
        bad = []
        for sub in ("MyTradingSys/execution", "MyTradingSys/backtest/layers", "MyTradingSys/runtime"):
            for p in (REPO / sub).rglob("*.py"):
                if re.search(r"runtime_data[/\\]_mirror|live_mirror|MIRROR_DIR", p.read_text(encoding="utf-8", errors="ignore")):
                    bad.append(str(p.relative_to(REPO)))
        self.assertEqual(bad, [])

    def test_pulled_mirror_is_ignored_and_untracked(self):
        """A pull rewrites runtime_data/_mirror in every work tree; tracked, it made each fresh tree dirty within minutes
        (sync.py where UNSHIPPED, tidy refusing). Publishing goes through the share, never through git."""
        if subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-dir"], capture_output=True).returncode != 0:
            self.skipTest("not a git checkout")
        for rel in ("runtime_data/_mirror/runtime_data/last_alert.json", "runtime_data/_mirror/manifest.json",
                    "runtime_data/_mirror.lock", "runtime_data/_mirror.old/x", "runtime_data/_mirror.tmp123/x"):
            r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", rel], capture_output=True)
            self.assertEqual(r.returncode, 0, f"{rel} is not git-ignored")
        tracked = subprocess.run(["git", "-C", str(REPO), "ls-files", "runtime_data/_mirror"],
                                 capture_output=True, text=True).stdout.split()
        self.assertEqual(tracked, [])

    def test_allowlist_names_exist_in_the_code_that_writes_them(self):
        """Each allowlisted name must appear in tracked source, so a renamed output cannot silently drop out."""
        src = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                        for ext in ("*.py", "*.ps1", "*.java") for p in REPO.rglob(ext)
                        if ".git" not in p.parts and p.name not in ("live_mirror.py", "test_live_mirror.py"))
        src += (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        missing = []
        for pattern, _ in lm.ALLOW:
            base = pattern.split("/")[-1]
            token = base if "*" not in base else pattern.split("/")[-2]
            if token not in src:
                missing.append(pattern)
        self.assertEqual(missing, [], "allowlist entries no code mentions (renamed output?)")


if __name__ == "__main__":
    unittest.main()
