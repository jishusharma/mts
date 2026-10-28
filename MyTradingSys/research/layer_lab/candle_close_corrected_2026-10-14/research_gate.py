"""Explicit numerical research gate: skipped pipeline tests mean FAIL."""
import sys
import unittest
from pathlib import Path

if __name__=='__main__':
    here=Path(__file__).resolve().parent
    suite=unittest.TestSuite()
    for name in ['test_rules.py','test_import_guard.py','test_engine.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(here),pattern=name))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
