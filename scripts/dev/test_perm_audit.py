import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import perm_audit as p

BASE = ["Bash(git status:*)", "Bash(python:*)"]

class T(unittest.TestCase):
    def test_denied_git_merge_is_finding(self):
        s = {"permissions": {"allow": BASE, "deny": ["Bash(git merge:*)"]}}
        out = p.audit(s)
        self.assertTrue(any("git merge" in f for f in out), out)

    def test_clean_settings_ok(self):
        s = {"permissions": {"allow": BASE, "deny": ["Bash(git rebase:*)", "Bash(git push --force:*)"]}}
        self.assertEqual(p.audit(s), [])

    def test_denied_commit_pull_fetch(self):
        s = {"permissions": {"allow": BASE, "deny": ["Bash(git commit:*)", "Bash(git pull:*)", "Bash(git fetch:*)"]}}
        self.assertEqual(len(p.audit(s)), 3)

    def test_no_bash_allow_is_finding(self):
        s = {"permissions": {"allow": ["Read(*)"], "deny": []}}
        self.assertTrue(any("Bash" in f for f in p.audit(s)))

    def test_path_outside_checkout(self):
        s = {"permissions": {"allow": BASE + ["Write(F:/backup/**)"], "additionalDirectories": ["F:/x"], "deny": []}}
        self.assertEqual(len([f for f in p.audit(s) if "outside" in f]), 2)

    def test_main_exit_code(self):
        self.assertEqual(p.main(["--settings", "nonexistent.json"]), 0)

if __name__ == "__main__":
    unittest.main()
