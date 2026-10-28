"""Tests for check_rv05_h2.py. Each test copies the ledger files to a temp dir (FABIO_LEDGER_DIR) and plants a defect."""
import importlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent
FILES = ['FABIO_TRADE_LEDGER.csv', 'FABIO_TRADE_LEDGER.md', 'RV05_H2_READS.csv']


class T(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        for f in FILES:
            if (SRC / f).exists():
                shutil.copy(SRC / f, self.d / f)
        os.environ['FABIO_LEDGER_DIR'] = str(self.d)
        import check_rv05_h2
        self.m = importlib.reload(check_rv05_h2)

    def tearDown(self):
        os.environ.pop('FABIO_LEDGER_DIR', None)
        shutil.rmtree(self.d, ignore_errors=True)

    def edit(self, name, old, new):
        p = self.d / name
        s = p.read_text(encoding='utf-8')
        self.assertIn(old, s)
        p.write_text(s.replace(old, new, 1), encoding='utf-8', newline='')

    def test_clean_passes(self):
        self.assertEqual(self.m.check(), [])

    def test_missing_reads_file_fails(self):
        (self.d / 'RV05_H2_READS.csv').unlink()
        self.assertTrue(self.m.check())

    def test_missing_status_table_fails(self):
        self.edit('FABIO_TRADE_LEDGER.md', '## RV05 H2 adjudication', '## other')
        self.assertTrue(self.m.check())

    def test_planted_csv_edit_without_frame_time_caught(self):
        # F13 entry is CHANGED; strip its frame time from the cell
        q = self.d / 'FABIO_TRADE_LEDGER.csv'
        q.write_text(q.read_text(encoding='utf-8').replace('t=3375', 'frame unknown'), encoding='utf-8', newline='')
        self.assertTrue(any('frame time' in e for e in self.m.check()))

    def test_planted_edit_to_kept_cell_caught(self):
        self.edit('FABIO_TRADE_LEDGER.csv', '25021.75,unknown', '25021.50,unknown')
        self.assertTrue(any("('F8', 'stop')" in e for e in self.m.check()))

    def test_contested_must_keep_csv_value(self):
        self.edit('FABIO_TRADE_LEDGER.csv', '"25098.75 (t3150);', '"25098.25 (t3150);')
        self.assertTrue(any("('F12-m2', 'stop')" in e for e in self.m.check()))

    def test_wrong_status_in_table_caught(self):
        self.edit('FABIO_TRADE_LEDGER.md', '| F12-m2 | stop | CONTESTED |', '| F12-m2 | stop | CHANGED |')
        self.assertTrue(self.m.check())

    def test_compute_status(self):
        c = self.m.compute_status
        self.assertEqual(c(25034.53, 25034.50, []), 'KEPT')
        self.assertEqual(c(25105.18, 25105.78, [25105.78, 25105.18]), 'CHANGED')
        self.assertEqual(c(25098.25, 25098.75, [25098.75]), 'CONTESTED')
        self.assertEqual(c(None, 1.0, []), 'NOT_IN_DATA')


if __name__ == '__main__':
    unittest.main()
