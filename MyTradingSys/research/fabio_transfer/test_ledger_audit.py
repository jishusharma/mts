"""Pins the H1-H6 corrections of the 2026-10-13 Fabio ledger audit (cards fabio-audit-20261013-*).

Expected values come from the audit report (layer_lab/reports/2026-10-13_lab-audit-fabio-ledger-frames.md), not from the ledger.
"""
import csv
import os
import re
import unittest
from pathlib import Path

HERE = Path(os.environ.get('FABIO_LEDGER_DIR') or Path(__file__).resolve().parent)
CSV = HERE / 'FABIO_TRADE_LEDGER.csv'
MD = HERE / 'FABIO_TRADE_LEDGER.md'


def rows():
    with open(CSV, encoding='utf-8', newline='') as f:
        return {r['id']: r for r in csv.DictReader(f)}


class TestH1(unittest.TestCase):
    def test_prices(self):
        r = rows()
        self.assertTrue(r['F8']['entry'].startswith('25034.50'))
        self.assertTrue(r['F9']['stop'].startswith('25019.44'))
        self.assertTrue(r['F10']['entry'].startswith('~25040.00'))
        self.assertTrue(r['F12']['entry'].startswith('25105.78'))
        self.assertTrue(r['F12']['stop'].startswith('25089.75'))
        self.assertTrue(r['F12-m2']['entry'].startswith('25108.50'))
        self.assertTrue(r['F12-m2']['stop'].startswith('25098.75'))
        self.assertTrue(r['F12-m2']['target'].startswith('25148.75'))
        self.assertTrue(r['F13']['entry'].startswith('25106.50'))
        self.assertTrue(r['F13-m1']['entry'].startswith('25108.00'))

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


EXIT_IDS = ['F3c-x', 'F5-x', 'F6-x', 'F7-x', 'F8-x', 'F9-x', 'F10-x', 'F11-x', 'F12-x', 'F13-x', 'F14-x']


class TestH2(unittest.TestCase):
    def test_exit_rows_do_not_claim_fills_or_causes(self):
        r = rows()
        for i in EXIT_IDS:
            fam = r[i]['family']
            self.assertNotRegex(fam, r'RESOLVED|tp_hit|^stopped_out|^profit_taken', i)
            self.assertIn('INFERRED', r[i]['note'], i)
            self.assertIn('AUDIT H2', r[i]['note'], i)
        self.assertNotIn('plus ~80$ slippage', r['F8-x']['note'])
        self.assertNotIn('plus costs/slippage', r['F13-x']['note'])

    def test_missing_46_02_interval_and_day_net_wording(self):
        r = rows()
        self.assertIn('-46.02', r['F11-x']['note'])
        self.assertIn('22239.02', r['F11-x']['note'])
        self.assertNotIn('so day net still +2849', r['F11-x']['note'])

    def test_md_has_h2_section_without_causal_fill_claims(self):
        t = MD.read_text(encoding='utf-8')
        self.assertIn('Audit correction H2', t)
        self.assertNotIn('TP filled ~25001.00', t)
        self.assertNotIn('(TP hit, minus costs)', t)

    def test_f13_gap_1150_not_in_data(self):
        r = rows()
        f13x = r['F13-x']
        exit_price = f13x.get('exit', f13x['entry'])
        self.assertIn(exit_price, ['-', ''])
        self.assertIn('1150', f13x['note'])
        self.assertIn('NOT_IN_DATA', f13x['note'])
        self.assertNotIn('plus costs/slippage', f13x['note'])


        t = MD.read_text(encoding='utf-8')
        f13_m = re.search(r'F13 \(DyS79Eb92Ug t=3525-3775\):[^\n]+', t)
        self.assertIsNotNone(f13_m)
        f13_text = f13_m.group(0)
        self.assertIn('1150', f13_text)
        self.assertIn('NOT_IN_DATA', f13_text)



class TestH3(unittest.TestCase):
    def test_no_unsourced_dates(self):
        for i, row in rows().items():
            self.assertTrue(row['date'].startswith('UNKNOWN'), (i, row['date']))
        r = rows()
        self.assertIn('screenshot', r['F4a']['date'])
        self.assertIn('December', r['F2']['date'])
        self.assertIn('October', r['F7']['date'])
        self.assertNotRegex(r['F7']['date'], r'^2026')

    def test_entry_rows_name_a_timezone_source(self):
        r = rows()
        for i in ['F1', 'F2', 'F3a', 'F4a', 'F5', 'F6', 'F7', 'F13']:
            self.assertIn('timezone:', r[i]['entry_time_src'], i)
        self.assertNotEqual(r['F3b']['time_local'], 'NY session')

    def test_md_has_no_universal_session_claim(self):
        t = MD.read_text(encoding='utf-8')
        self.assertNotIn('US cash for every frame', t)
        self.assertNotIn('NY/US cash session for all frames', t)
        self.assertIn('Audit correction H3', t)


class TestH4(unittest.TestCase):
    def test_inventory_section_matches_computation(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ledger_stats
        md = MD.read_text(encoding='utf-8')
        self.assertIn(ledger_stats.render(), md)
        s = ledger_stats.stats()
        self.assertEqual(s['n'], 13)
        self.assertAlmostEqual(s['min'], 3.38, places=2)   # F3c: 24568.38 - 24565.00, from the CSV cells
        self.assertAlmostEqual(s['max'], 30.83, places=2)  # F6: 24914.33 - 24883.50

    def test_old_final_claims_are_superseded(self):
        md = MD.read_text(encoding='utf-8')
        self.assertNotIn('Status: DONE 2026-10-11', md)
        self.assertNotIn('## FINAL stats (all five downloaded videos read end to end', md)
        self.assertIn('SUPERSEDED (H4; the min 1.5pt', md)
        self.assertIn('PARTIAL, not "all available"', md)
        self.assertIn('0jM5Y31YJak.en.vtt:1026-1058', md)


class TestH5(unittest.TestCase):
    def test_no_universal_management_rules(self):
        md = MD.read_text(encoding='utf-8')
        self.assertNotIn('stop moves only toward profit', md)
        self.assertNotIn('stops move only toward profit,', md)
        self.assertNotIn('TP fixed far', md)
        self.assertNotIn('was an order ticket that never filled', md)
        self.assertIn('Audit correction H5', md)
        self.assertIn('25513.25', md)

    def test_row_semantics(self):
        r = rows()
        self.assertIn('STP', r['F11']['note'])
        self.assertNotIn('two buy LMT +2 orders', r['F11']['note'])
        self.assertIn('drawing', r['F15-draft-6975-7025']['family'])
        self.assertNotIn('not_filled', r['F15-draft-6975-7025']['family'])
        self.assertIn('25513.25', r['F1-m2']['note'])
        self.assertIn('25089.75', r['F12']['note'])


class TestH6(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[3]

    def test_ledger_labels_secondary_source(self):
        md = MD.read_text(encoding='utf-8')
        self.assertIn('SECONDARY_NOT_SOURCED', md)
        self.assertNotIn('His stated settings', md)
        self.assertIn('Audit correction H6', md)

    def test_citing_docs_do_not_call_it_his_own(self):
        cat = (self.ROOT / 'MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md').read_text(encoding='utf-8')
        self.assertNotIn('FL:50 already holds the gLHd slide', cat)
        self.assertIn('SECONDARY_NOT_SOURCED, H6', cat)
        spec = (self.ROOT / 'MyTradingSys/research/layer_readiness_2026-10-16/BIGTRADE_SPEC.md').read_text(encoding='utf-8')
        self.assertIn('gLHd "30 to 40 on NQ" slide is secondary', spec)


if __name__ == '__main__':
    unittest.main()
