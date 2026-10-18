"""config_check: settings.json parses and its hook scripts exist; secret paths stay ignored (gate step 3js, GATE_SPEED D5)."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config_check as cc


CLEAN = []


def repo(settings=None, gitignore=".secrets/\n.env\n.env.*\n"):
    d = Path(tempfile.mkdtemp())
    CLEAN.append(d)
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    (d / ".gitignore").write_text(gitignore, encoding="utf-8", newline="\n")
    (d / "scripts" / "dev").mkdir(parents=True)
    (d / "scripts" / "dev" / "real.py").write_text("", encoding="utf-8")
    if settings is not None:
        (d / ".claude").mkdir()
        (d / ".claude" / "settings.json").write_text(settings if isinstance(settings, str) else json.dumps(settings), encoding="utf-8")
    return d


def hooks(*cmds):
    return {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": c} for c in cmds]}]}}


class ConfigCheck(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        for d in CLEAN:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_real_repo_passes(self):
        self.assertEqual(cc.problems(), [])

    def test_good_settings_and_ignores_pass(self):
        self.assertEqual(cc.problems(repo(hooks('python "$CLAUDE_PROJECT_DIR/scripts/dev/real.py" hook'))), [])

    def test_unparseable_settings_fail(self):
        bad = cc.problems(repo('{"hooks": {'))
        self.assertEqual(len(bad), 1)
        self.assertIn("does not parse", bad[0])

    def test_hook_naming_a_missing_script_fails(self):
        bad = cc.problems(repo(hooks('python "$CLAUDE_PROJECT_DIR/scripts/dev/gone.py" hook')))
        self.assertEqual(bad, [".claude/settings.json: hook script missing: scripts/dev/gone.py"])

    def test_secret_paths_must_stay_ignored(self):
        bad = cc.problems(repo(gitignore="runtime_data/\n"))
        self.assertEqual(sorted(bad), sorted(f".gitignore: secret path not ignored: {s}" for s in cc.SECRET_SENTINELS))


if __name__ == "__main__":
    unittest.main()
