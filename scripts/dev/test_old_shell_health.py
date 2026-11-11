"""bug-background-shell-runs-12h-1109: sync.py health shows a shell older than 30 min as a NOTE line, not a young one."""
import sys, time, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import sync


class OldShellHealth(unittest.TestCase):
    def test_old_flagged_young_not(self):
        now = time.time()
        rows = [{"pid": 7, "start": now - 12 * 3600, "cmd": "bash -c cat > m.md <<'EOF'"},
                {"pid": 8, "start": now - 60, "cmd": "bash -c git log"}]
        out = sync.old_shell_notes(lister=lambda: rows)
        self.assertEqual(len(out), 1, out)
        self.assertTrue(out[0].startswith("NOTE OLD-SHELL pid 7 720m > 30m"), out[0])

    def test_error_is_empty(self):
        def boom():
            raise OSError("x")
        self.assertEqual(sync.old_shell_notes(lister=boom), [])


if __name__ == "__main__":
    unittest.main()
