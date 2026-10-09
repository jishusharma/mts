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


class GateRunsIt(unittest.TestCase):
    def test_run_all_tests_runs_wiring_check_before_quick_cutoff(self):
        src = Path(rat.__file__).read_text(encoding='utf-8')
        needle = '"scripts/dev/wiring_scan.py", "--check"'
        i = src.find(needle)
        self.assertGreater(i, 0, 'run_all_tests.py does not run wiring_scan.py --check')
        self.assertLess(i, src.find('# Step 5: mvn test'), 'wiring check must sit before the --quick cutoff')


if __name__ == '__main__':
    unittest.main()
