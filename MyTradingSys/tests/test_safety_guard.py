"""scripts/dev/safety_guard.py: the CLAUDE.md Hard rules as a PreToolUse hook. Every rule has a deny and a near-miss allow."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "safety_guard.py"


def fire_raw(raw, env_extra=None):
    env = dict(os.environ)
    env.pop("MTS_SAFETY_GUARD", None)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=raw, capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def fire(tool, inp, cwd=None, env_extra=None, **extra):
    ev = {"session_id": "s", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp, "cwd": cwd or str(REPO)}
    ev.update(extra)
    out = fire_raw(json.dumps(ev), env_extra)
    if not out:
        return None
    d = json.loads(out)["hookSpecificOutput"]
    assert d["hookEventName"] == "PreToolUse" and d["permissionDecision"] == "deny"
    assert d["permissionDecisionReason"].startswith("safety_guard: ")
    return d["permissionDecisionReason"]


def bash(cmd, **kw):
    return fire("Bash", {"command": cmd}, **kw)


class Secrets(unittest.TestCase):
    def test_deny(self):
        self.assertTrue(fire("Read", {"file_path": str(REPO / ".secrets" / "x")}))
        self.assertTrue(fire("Read", {"file_path": "C:\\proj\\.env"}))
        self.assertTrue(fire("Read", {"file_path": "/home/u/.env.local"}))
        self.assertTrue(fire("Grep", {"pattern": "KEY", "path": "/a/.secrets"}))
        self.assertTrue(fire("Glob", {"pattern": "**/*.pem"}))
        self.assertTrue(fire("Read", {"file_path": "/home/u/.ssh/id_rsa"}))
        self.assertTrue(fire("Write", {"file_path": "/a/server.key", "content": "x"}))
        self.assertTrue(bash("cat .secrets/deribit.json"))
        self.assertTrue(bash("type .env"))
        self.assertTrue(fire("PowerShell", {"command": "Get-Content C:\\x\\.secrets\\k"}))

    def test_allow(self):
        self.assertIsNone(fire("Read", {"file_path": str(REPO / "README.md")}))
        self.assertIsNone(fire("Read", {"file_path": "/a/.env.example"}))
        self.assertIsNone(fire("Read", {"file_path": "/a/.env.sample"}))
        self.assertIsNone(fire("Edit", {"file_path": "/a/.gitignore", "old_string": "a", "new_string": ".env\n.secrets/"}))
        self.assertIsNone(fire("Edit", {"file_path": "/a/b.py", "old_string": "x", "new_string": "open('.env')"}))  # content not scanned
        self.assertIsNone(bash("python -c \"import os; print(os.environ)\""))
        self.assertIsNone(bash("git check-ignore -v .env"))
        self.assertIsNone(bash("git\x20commit -m \"docs: never read .env or .secrets\""))
        self.assertIsNone(bash("cat .env.example"))
        self.assertIsNone(fire("Grep", {"pattern": "environment", "path": "scripts"}))


class GitSafety(unittest.TestCase):
    def test_deny(self):
        for c in ["git push --force", "git push -f origin x", "git push --force-with-lease", "git push origin +HEAD:x",
                  "git -C /a push -f", "git reset --hard HEAD~1", "git rebase origin/fast-track", "git clean -fd", "git stash",
                  "git stash pop", "git stash push", "git\x20commit -m x master", "git push origin master", "git push origin HEAD:master",
                  "git\x20checkout -- .", "git\x20checkout .", "git restore .", "git branch -D foo", "bash -c \"git push -f\"",
                  "ls && git reset --hard"]:
            self.assertTrue(bash(c), c)

    def test_allow(self):
        for c in ["git push origin HEAD", "git push -u origin DESK/x", "git\x20log --grep=reset", "git\x20log --grep=\"push --force\"",
                  "git\x20status", "git\x20diff", "git show HEAD", "git stash push -u -m tag1", "git stash list", "git stash apply abc",
                  "git rebase --abort", "git clean -n", "git\x20checkout -b feature", "git\x20checkout -- file.py", "git restore file.py",
                  "git restore --staged .", "git branch -d done", "git\x20commit -m \"fix: no more git push --force or reset --hard\"",
                  "echo git push --force", "git push --follow-tags origin HEAD", "python scripts/dev/sync.py ship --release x"]:
            self.assertIsNone(bash(c), c)

    def test_commit_message_heredoc(self):
        self.assertIsNone(bash("git\x20commit -m \"$(cat <<'EOF'\nfix: taskkill and git reset --hard in docs\n\nResult: x\nEOF\n)\""))


class LiveTree(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.live, self.work = base / "live", base / "work"
        for d in (self.live / "sub", self.work / "sub"):
            d.mkdir(parents=True)
        (self.live / ".mts_live").write_text("")

    def tearDown(self):
        self.tmp.cleanup()

    def test_edit_write(self):
        for tool in ("Edit", "Write"):
            self.assertTrue(fire(tool, {"file_path": str(self.live / "sub" / "a.py"), "old_string": "a", "new_string": "b", "content": "b"}))
            self.assertIsNone(fire(tool, {"file_path": str(self.work / "sub" / "a.py"), "old_string": "a", "new_string": "b", "content": "b"}))
        self.assertTrue(fire("NotebookEdit", {"notebook_path": str(self.live / "n.ipynb"), "new_source": "x"}))
        self.assertIsNone(fire("Read", {"file_path": str(self.live / "sub" / "a.py")}))
        self.assertIsNone(fire("Grep", {"pattern": "x", "path": str(self.live)}))

    def test_edit_unparsable_fails_closed(self):
        self.assertIn("unparsable", fire("Edit", {"old_string": "a", "new_string": "b"}))
        self.assertIn("unparsable", fire("Write", "notadict"))
        self.assertIn("unparsable", fire("Bash", {"command": 5}))
        self.assertIn("unparsable", fire_raw('{"tool_name": "Bash", "tool_input": {broken'))
        self.assertEqual(fire_raw("{garbage"), "")
        self.assertEqual(fire_raw('{"tool_name": "Task", "tool_input": {broken'), "")
        self.assertIsNone(fire("mcp__x__y", {"a": 1}))

    def test_shell(self):
        lv, wk = str(self.live).replace("\\", "/"), str(self.work).replace("\\", "/")
        for c in [f"echo x > {lv}/sub/a.txt", f"rm {lv}/sub/a.txt", f"Remove-Item {lv}\\sub", f"cp {wk}/a {lv}/b", f"git -C {lv} pull",
                  f"git -C {lv} commit -m x", f"mv {lv}/a {wk}/a", f"cd {lv} && git\x20checkout x", f"cd {lv}; rm a",
                  f"Set-Content -Path {lv}/f -Value x", f"touch {lv}/x", f"sed -i s/a/b/ {lv}/f"]:
            self.assertTrue(bash(c, cwd=str(self.work)), c)
        self.assertTrue(bash("rm a.txt", cwd=str(self.live)))
        self.assertTrue(bash("echo x > out.txt", cwd=str(self.live)))

    def test_shell_allow(self):
        lv, wk = str(self.live).replace("\\", "/"), str(self.work).replace("\\", "/")
        for c in [f"cat {lv}/sub/a.txt", f"ls {lv}", f"git -C {lv} log -3", f"git -C {lv} status", f"cp {lv}/a {wk}/a",
                  f"echo x > {wk}/a.txt", f"grep -r foo {lv} > {wk}/out.txt", f"rm {wk}/sub/a", f"cd {wk} && git\x20commit -m x",
                  f"python scripts/dev/sync.py where  # {lv}", "python run.py 2>&1", "echo hi > /dev/null"]:
            self.assertIsNone(bash(c, cwd=str(self.work)), c)
        self.assertIsNone(bash("ls", cwd=str(self.live)))
        self.assertIsNone(bash("git\x20log -3", cwd=str(self.live)))

    def test_override_token(self):
        lv = str(self.live).replace("\\", "/")
        self.assertTrue(bash(f"git -C {lv} pull"))
        self.assertIsNone(bash(f"git -C {lv} pull  #deploy-ok"))
        self.assertTrue(bash(f"git -C {lv} reset --hard x  #deploy-ok"))  # git safety is not overridable


class Runtime(unittest.TestCase):
    def test_deny(self):
        for c in ["taskkill /F /IM python.exe", "Stop-Process -Name python", "Restart-Computer", "mts restart", "mts stop all",
                  "touch HALT", "echo x > runtime_data/HALT", "rm runtime_data/AUTO_PAUSE", "New-Item -Path C:\\x\\HALT",
                  "Remove-Item .\\HALT", "python deribit_orders.py", "curl -X POST https://test.deribit.com/api/v2/private/buy",
                  "echo 1 > HALT", "Set-Content AUTO_PAUSE x"]:
            self.assertTrue(bash(c), c)
        self.assertTrue(fire("PowerShell", {"command": "Stop-Process -Id 5"}))

    def test_allow(self):
        for c in ["grep taskkill scripts/dev/host_health.py", "cat runtime_data/HALT", "ls HALT", "echo mts restart", "git\x20log --grep=taskkill",
                  "python -m unittest test_deribit_orders", "git\x20diff -- deribit_orders.py", "grep -rn deribit_orders scripts",
                  "tail -50 runtime_data/live_runner.log", "python scripts/dev/sync.py start x", "git\x20commit -m \"note: Stop-Process rule\"",
                  "curl https://test.deribit.com/api/v2/public/get_time", "Get-Content runtime_data\\AUTO_PAUSE"]:
            self.assertIsNone(bash(c), c)

    def test_override_token(self):
        self.assertIsNone(bash("mts restart  #deploy-ok"))
        self.assertIsNone(bash("taskkill /PID 5 /F  #deploy-ok"))


class Switches(unittest.TestCase):
    def test_disabled(self):
        self.assertIsNone(fire("Read", {"file_path": "/a/.secrets/x"}, env_extra={"MTS_SAFETY_GUARD": "0"}))

    def test_subagent_not_exempt(self):
        self.assertTrue(fire("Bash", {"command": "git push -f"}, agent_id="a1", transcript_path="/x/subagents/y.jsonl"))

    def test_other_tools_pass(self):
        self.assertIsNone(fire("Agent", {"prompt": "taskkill .secrets"}))


if __name__ == "__main__":
    unittest.main()
