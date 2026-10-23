"""scripts/operator/cpu_cleanup.ps1: PowerShell variable names are case-insensitive, so a list variable must not share a
name with a switch parameter ($lenovo vs -Lenovo broke -Audit and -Lenovo on 2026-10-23), the task-path regex escapes
its backslashes, and no keep-list name (Wi-Fi, Remote Desktop, Windows Update, Defender, AIBridge) is in a disable list."""
import re
import unittest
from pathlib import Path

PS1 = Path(__file__).resolve().parents[2] / "scripts" / "operator" / "cpu_cleanup.ps1"
TEXT = PS1.read_text(encoding="utf-8")
BS = chr(92)


class CpuCleanupScriptTest(unittest.TestCase):
    def test_no_variable_shadows_a_switch_parameter(self):
        params = re.findall(r"\[switch\]\$(\w+)", TEXT)
        self.assertTrue(params)
        for p in params:
            self.assertIsNone(re.search(r"^\s*\$" + p + r"\s*=", TEXT, flags=re.M | re.I),
                              f"${p} is assigned but is also a switch")

    def test_task_path_regex_escapes_backslashes(self):
        found = re.findall(r"-notmatch\s+'([^']*)'", TEXT)
        self.assertTrue(found)
        for rx in found:
            single = [i for i, ch in enumerate(rx) if ch == BS and rx[i - 1:i] != BS and rx[i + 1:i + 2] != BS]
            self.assertEqual(single, [], f"unescaped backslash in {rx!r}")

    def test_keep_names_not_in_disable_lists(self):
        lists = re.sub(r"#.*", "", TEXT)
        for keep in ("Dnscache", "WlanSvc", "TermService", "wuauserv", "WinDefend", "AIBridge"):
            self.assertNotIn("'" + keep + "'", lists, keep)


if __name__ == "__main__":
    unittest.main()
