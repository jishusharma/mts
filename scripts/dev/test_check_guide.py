"""Tests for check_guide.py: each kind of drift between mts.ps1 and the guide is caught."""
import sys
sys.dont_write_bytecode = True

import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_guide import check  # noqa: E402

MTS = '''
# VERBS-BEGIN
$Verbs = @(
    @("Market loop", "start", "Start"),
    @("Trading",     "trade", "Trade")
)
# VERBS-END
'''

GUIDE = '''# MTS User Guide
Last reviewed: 2026-09-28

## 8. All commands
| `mts start` | Start |
| `mts trade <plan>` | Trade |

## 9. Where things are
| Plans | `plans\\` |
| Log   | `logs\\run.txt` |

## 10. Known limits
`mts ghost` is mentioned here, outside the command table - not a drift.
'''


class CheckGuideTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "plans").mkdir()
        (self.repo / "logs").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_in_sync_passes(self):
        self.assertEqual(check(MTS, GUIDE, self.repo), [])

    def test_verb_missing_from_guide(self):
        guide = GUIDE.replace("| `mts trade <plan>` | Trade |\n", "")
        self.assertEqual(check(MTS, guide, self.repo), ["guide 'All commands' is missing: mts trade"])

    def test_guide_lists_removed_verb(self):
        mts = MTS.replace('    @("Trading",     "trade", "Trade")\n', "").replace('"Start"),', '"Start")')
        self.assertEqual(check(mts, GUIDE, self.repo),
                         ["guide 'All commands' lists a command mts.ps1 does not have: mts trade"])

    def test_missing_folder(self):
        (self.repo / "plans").rmdir()
        self.assertEqual(check(MTS, GUIDE, self.repo), ["guide 'Where things are' path not found: plans\\"])

    def test_file_path_needs_only_its_folder(self):
        self.assertFalse((self.repo / "logs" / "run.txt").exists())
        (self.repo / "logs").rmdir()
        self.assertEqual(check(MTS, GUIDE, self.repo), ["guide 'Where things are' path not found: logs\\run.txt"])

    def test_review_date_required(self):
        guide = GUIDE.replace("Last reviewed: 2026-09-28", "Last reviewed: soon")
        self.assertEqual(check(MTS, guide, self.repo), ["guide has no 'Last reviewed: YYYY-MM-DD' line"])

    def test_missing_verb_table(self):
        self.assertEqual(check("no table here", GUIDE, self.repo),
                         ["mts.ps1: verb table (VERBS-BEGIN/END) not found or empty"])


if __name__ == "__main__":
    unittest.main()
