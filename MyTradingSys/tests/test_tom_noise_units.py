"""tom_noise_units: true range per FORMULAS.md section 12 and complete-bucket aggregation (hand numbers)."""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "dev"))
import tom_noise_units as t


def test_true_range_formulas_12_example():
    # FORMULAS.md 12 worked example: TR = 2, 2, 2.5 (i >= 1); here as a fraction of each bar's close.
    bars = [(10, 9, 9.5), (11, 9, 10.5), (12, 10, 11.5), (11, 9, 10)]
    got = t.true_ranges(bars)
    assert [round(x, 6) for x in got] == [round(2 / 10.5, 6), round(2 / 11.5, 6), round(2.5 / 10, 6)]


def test_incomplete_bucket_and_gap_are_dropped():
    m = 60000
    rows = {i * m: (100.0, 101.0, 99.0, 100.0) for i in range(5)}            # bucket 0 complete
    rows.update({(5 + i) * m: (100.0, 103.0, 100.0, 102.0) for i in range(5)})  # bucket 1 complete
    rows.update({(10 + i) * m: (102.0, 102.5, 101.5, 102.0) for i in range(4)})  # bucket 2: 4 of 5 minutes
    rows.update({(20 + i) * m: (102.0, 104.0, 102.0, 103.0) for i in range(5)})  # bucket 4 complete, bucket 3 missing
    agg = t.aggregate(rows, 5)
    assert [a[0] for a in agg] == [0, 5 * m, 20 * m]
    v = t.tr_fracs(agg, 5, lambda b: True)
    # only bucket 1 has an adjacent previous bucket: TR = max(103-100, |103-100|, |100-100|) = 3, close 102
    assert [round(x, 6) for x in v] == [round(3 / 102.0, 6)]
