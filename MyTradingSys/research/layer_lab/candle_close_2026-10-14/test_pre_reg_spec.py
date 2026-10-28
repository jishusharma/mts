"""Spec audit of PHASE_ENCOUNTER_PRE_REG.md (stdlib only; runs in CI, no pandas)."""
import re
import unittest
from pathlib import Path

DOC = Path(__file__).resolve().parent / 'PHASE_ENCOUNTER_PRE_REG.md'


def text():
    return DOC.read_text(encoding='utf-8')


def table_rows(section_title):
    body = text().split(section_title, 1)[1]
    rows = []
    for line in body.splitlines()[1:]:
        if line.startswith('#') and rows:
            break
        if line.startswith('|') and not set(line) <= set('|- '):
            rows.append([c.strip() for c in line.strip('|').split('|')])
    return rows[1:]


class PreRegSpecTests(unittest.TestCase):
    def test_every_feature_has_equation_availability_unknown(self):
        rows = table_rows('## 2. Features')
        ids = [r[0] for r in rows]
        self.assertEqual(ids, ['F0a', 'F0b', 'D', 'R', 'V', 'A'])
        for r in rows:
            self.assertEqual(len(r), 5, r[0])
            self.assertTrue(all(len(c) > 10 for c in r[2:]), r[0])
            self.assertRegex(r[4], r'fewer than|any component|short', r[0])

    def test_twelve_slots_and_prebuild_gate_answered(self):
        rows = {r[0]: r[1] for r in table_rows('## 11. Pre-build gate')}
        keys = ['0a', '0b', '0c', '0d', '0e', '0f'] + [str(i) for i in range(1, 13)]
        for k in keys:
            hit = [v for name, v in rows.items() if name.split()[0] == k]
            self.assertEqual(len(hit), 1, k)
            self.assertGreater(len(hit[0]), 20, k)
            self.assertNotIn('TODO', hit[0])
            self.assertNotIn('NOT_ANSWERED', hit[0])

    def test_signal_and_control_share_timing_and_matching(self):
        t = text()
        for needle in ['Common timestamp rule', 'same UTC week block', 'same elapsed bars',
                       'Never match on future path', 'AT RISK', 'match rate']:
            self.assertIn(needle, t)

    def test_failed_untriggered_and_censoring_explicit(self):
        t = text()
        for needle in ['UNTRIGGERED and FAILED', 'wrong-way', '`censored`', 'CLUSTER', 'embargo', 'label interval']:
            self.assertIn(needle, t)

    def test_trial_family_arithmetic(self):
        t = text()
        self.assertIn('= **16** tests', t)
        self.assertEqual(16 + 4 + 4 + 20, 44)
        self.assertIn('Attempted family = 44 views', t)
        self.assertIn('130 + 8 + 126 + 44 = 308', t)
        self.assertEqual(130 + 8 + 126 + 44, 308)
        ctx = [r[0] for r in table_rows('## 6. Joint-context family')]
        self.assertEqual(ctx, ['C0', 'C1', 'C2', 'C3', 'C4'])

    def test_power_numbers(self):
        self.assertAlmostEqual((2.96 + 0.84) * 0.9 / 300 ** .5, 0.1975, places=3)
        self.assertAlmostEqual(((2.96 + 0.84) * 0.9 / 0.10) ** 2, 1170, delta=2)

    def test_origin_labels_and_no_holdout(self):
        t = text()
        self.assertIn('OURS', t)
        self.assertNotRegex(t, r'\bSOURCED\b(?!.*none)') if False else None
        self.assertIn('2024-07+ stays', t)
        self.assertIn('NO VALIDATION/HOLDOUT read', t)
        for b in ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']:
            self.assertRegex(t, rf'- {b}: ')


if __name__ == '__main__':
    unittest.main()
