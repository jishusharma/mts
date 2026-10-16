"""Pins the H1-H6 corrections of the 2026-10-13 Fabio ledger audit (cards fabio-audit-20261013-*).

Expected values come from the audit report (layer_lab/reports/2026-10-13_lab-audit-fabio-ledger-frames.md), not from the ledger.
"""
import csv
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE / 'FABIO_TRADE_LEDGER.csv'
MD = HERE / 'FABIO_TRADE_LEDGER.md'


def rows():
    with open(CSV, encoding='utf-8', newline='') as f:
        return {r['id']: r for r in csv.DictReader(f)}


class TestH1(unittest.TestCase):
    def test_prices(self):
        r = rows()
        self.assertTrue(r['F8']['entry'].startswith('25034.53'))
        self.assertTrue(r['F9']['stop'].startswith('25019.44'))
        self.assertTrue(r['F10']['entry'].startswith('~25040.00'))
        self.assertTrue(r['F12']['entry'].startswith('25105.78'))
        self.assertTrue(r['F12']['stop'].startswith('25089.75'))
        self.assertTrue(r['F12-m2']['entry'].startswith('25108.50'))
        self.assertTrue(r['F12-m2']['stop'].startswith('25098.75'))
        self.assertTrue(r['F12-m2']['target'].startswith('25148.75'))
        self.assertTrue(r['F13']['entry'].startswith('25108.90'))
        self.assertTrue(r['F13-m1']['entry'].startswith('25108.05'))

    def test_f13_add_is_buy_and_old_values_gone(self):
        r = rows()
        self.assertIn('BUY add', r['F13']['target'])
        self.assertNotIn('sell LMT +2 partial', r['F13']['target'])
        for old, rid, col in [('~25032.5', 'F8', 'entry'), ('~25010.4 initial', 'F9', 'stop'), ('~25040.5', 'F10', 'entry'),
                              ('~25085.75', 'F12', 'stop'), ('~25140.75', 'F12-m2', 'target'), ('~25104 ', 'F13', 'entry')]:
            self.assertNotIn(old, r[rid][col])

    def test_md_carries_corrections(self):
        t = MD.read_text(encoding='utf-8')
        self.assertIn('Audit correction H1', t)
        self.assertNotIn('long 8 lots ~25032.5', t)
        self.assertNotIn('25085.75 (21pt)', t)


if __name__ == '__main__':
    unittest.main()
