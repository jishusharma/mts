"""Wiring gate tests: undeclared unwired code and stale declarations fail; the real repo passes; the gate runs it."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiring_scan as ws
import run_all_tests as rat

REG = ws.REGISTRY_PATH


def write(root, rel, text='x = 1\n'):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def make_root(tmp, registry=None):
    """A tiny repo: one live launcher importing live_mod; orphan_tool is referenced by nothing."""
    write(tmp, 'scripts/live/runner.py', 'import MyTradingSys.runtime.live_mod\n')
    write(tmp, 'MyTradingSys/runtime/live_mod.py')
    write(tmp, 'MyTradingSys/backtest/orphan_tool.py')
    if registry is not None:
        write(tmp, REG, json.dumps({'entries': registry}))
    return tmp


def run_check(root):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ws.main(['--check', '--root', root])
    return rc, buf.getvalue()


ORPHAN = 'MyTradingSys/backtest/orphan_tool.py'


class WiringGate(unittest.TestCase):
    def test_undeclared_orphan_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = run_check(make_root(tmp))
            self.assertEqual(rc, 1)
            self.assertIn('UNDECLARED ORPHAN: ' + ORPHAN, out)

    def test_declared_orphan_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = run_check(make_root(tmp, {ORPHAN: {'disp': 'TOOL', 'why': 'run by hand, see doc:1'}}))
            self.assertEqual(rc, 0, out)

    def test_stale_declaration_file_gone_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = {ORPHAN: {'disp': 'TOOL', 'why': 'x'}, 'MyTradingSys/backtest/gone.py': {'disp': 'TOOL', 'why': 'x'}}
            rc, out = run_check(make_root(tmp, reg))
            self.assertEqual(rc, 1)
            self.assertIn('STALE MyTradingSys/backtest/gone.py', out)

    def test_stale_declaration_now_live_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = {ORPHAN: {'disp': 'TOOL', 'why': 'x'}, 'MyTradingSys/runtime/live_mod.py': {'disp': 'TOOL', 'why': 'x'}}
            rc, out = run_check(make_root(tmp, reg))
            self.assertEqual(rc, 1)
            self.assertIn('STALE MyTradingSys/runtime/live_mod.py: now LIVE', out)

    def test_lab_entry_now_live_does_not_fail_the_gate(self):
        lab = 'MyTradingSys/research/layer_lab/x/event_table.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            write(root, lab)
            write(root, 'scripts/live/runner.py', 'import MyTradingSys.runtime.live_mod\nimport MyTradingSys.research.layer_lab.x.event_table\n')
            write(root, REG, json.dumps({'entries': {ORPHAN: {'disp': 'TOOL', 'why': 'x'}, lab: {'disp': 'TOOL', 'why': 'x'}}}))
            rc, out = run_check(root)
            self.assertEqual(rc, 0, out)

    def test_study_scripts_never_fail_the_gate_declared_or_not(self):
        """Run-once study scripts need no registry entry; a stale or gone entry for one is not a failure either."""
        study = 'MyTradingSys/research/study_x/run_it.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            write(root, study)
            write(root, 'MyTradingSys/research/study_x/test_run_it.py', 'import run_it\n')
            write(root, REG, json.dumps({'entries': {ORPHAN: {'disp': 'TOOL', 'why': 'x'},
                                                       'MyTradingSys/research/study_x/gone.py': {'disp': 'REPRO', 'why': 'x'}}}))
            rc, out = run_check(root)
            self.assertEqual(rc, 0, out)
        with tempfile.TemporaryDirectory() as tmp:       # outside research/ the same file still has to be declared
            root = make_root(tmp)
            write(root, 'MyTradingSys/backtest/study_x/run_it.py')
            write(root, 'MyTradingSys/backtest/study_x/test_run_it.py', 'import run_it\n')
            write(root, REG, json.dumps({'entries': {ORPHAN: {'disp': 'TOOL', 'why': 'x'}}}))
            self.assertEqual(run_check(root)[0], 1)

    def test_bad_disposition_empty_why_and_wire_without_ref_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            for e, needle in (({'disp': 'MAYBE', 'why': 'x'}, 'BAD'), ({'disp': 'TOOL', 'why': ' '}, 'why is empty'),
                              ({'disp': 'WIRE', 'why': 'x'}, 'WIRE needs ref')):
                rc, out = run_check(make_root(tmp, {ORPHAN: e}))
                self.assertEqual(rc, 1, e)
                self.assertIn(needle, out)

    def test_real_repo_passes(self):
        rc, out = run_check(str(rat.REPO))
        self.assertEqual(rc, 0, out)

    def test_real_registry_entries_all_carry_evidence(self):
        reg = ws.load_registry(str(rat.REPO))
        self.assertGreater(len(reg), 0, 'registry missing or empty')
        for p, e in reg.items():
            self.assertTrue(e['why'].strip(), p)
            if e['disp'] == 'PARKED':
                self.assertTrue(e.get('ref', '').strip(), p + ': PARKED must name the parked item')


class DevToolNoReader(unittest.TestCase):
    """scripts/dev files are all roots, so a dead one-off script there never shows as unwired; --check warns (never fails)."""

    def dev_root(self, tmp):
        write(tmp, 'scripts/dev/dead_tool.py')
        write(tmp, 'scripts/dev/test_dead_tool.py', 'import dead_tool\n')     # its own test does not count as a reader
        write(tmp, 'scripts/dev/doc_tool.py')
        write(tmp, 'scripts/dev/driver.py', 'import called_tool\n')
        write(tmp, 'scripts/dev/called_tool.py')
        write(tmp, 'CLAUDE.md', 'Run `python scripts/dev/doc_tool.py` first; driver.py is the entry.\n')
        write(tmp, '_archive/2026-10-15-scripts-dev/old_tool.py')
        write(tmp, 'MyTradingSys/system/03_FILE_INDEX.md', '| scripts/dev/dead_tool.py | tool |\n')   # an inventory is no reader
        return tmp

    def test_unread_dev_tool_is_warned_and_the_gate_still_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = run_check(self.dev_root(tmp))
            self.assertEqual(rc, 0, out)
            warn = [ln for ln in out.splitlines() if ln.startswith('WARN NO-READER')]
            self.assertEqual(len(warn), 1, out)
            self.assertIn('dead_tool.py', warn[0])
            for fine in ('doc_tool.py', 'called_tool.py', 'driver.py', 'old_tool.py', 'test_dead_tool.py'):
                self.assertNotIn(fine, warn[0].split(':', 1)[1])

    def test_naming_the_tool_in_an_entry_doc_clears_the_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn('dead_tool.py', run_check(self.dev_root(tmp))[1].split('WARN NO-READER')[1])
            write(tmp, 'MyTradingSys/system/PARALLEL.md', 'dead_tool.py is the monthly cleanup.\n')
            self.assertNotIn('WARN NO-READER', run_check(tmp)[1])

    def test_dev_no_reader_lists_only_the_unread_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.dev_root(tmp)
            built = ws.build(tmp)
            self.assertEqual(ws.dev_no_reader(tmp, built[0], built[1]), ['scripts/dev/dead_tool.py'])


class GateRunsIt(unittest.TestCase):
    def test_run_all_tests_runs_wiring_check_before_quick_cutoff(self):
        src = Path(rat.__file__).read_text(encoding='utf-8')
        needle = '"scripts/dev/wiring_scan.py", "--check"'
        i = src.find(needle)
        self.assertGreater(i, 0, 'run_all_tests.py does not run wiring_scan.py --check')
        self.assertLess(i, src.find('# Step 5: mvn test'), 'wiring check must sit before the --quick cutoff')


if __name__ == '__main__':
    unittest.main()
