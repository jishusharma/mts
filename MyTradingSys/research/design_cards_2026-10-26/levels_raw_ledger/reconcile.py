"""Reconcile ledger.csv independently of the producer: gross_R = s*(X-E)/R, fee_R = (fee_in+fee_out)/R, net = gross - fee
(FORMULAS.md:468-470). Exit code 1 on any failure. Uses csv/decimal only (no study imports).

  python reconcile.py [ledger.csv]      # default: ledger.csv beside this file
"""
import csv
import sys
from decimal import Decimal as D
from pathlib import Path

HERE = Path(__file__).resolve().parent
LC = HERE.parents[1] / 'levels_confluence_2026-10-14' / 'ladder_ideas_dev.csv'
DEV_END_MS = 1719792000000  # 2024-07-01T00:00Z
DEV_START_MS = 1648771200000  # 2022-04-01T00:00Z
TOL = D('0.000501')  # stored net is rounded to 3 decimals (half-unit 0.0005 plus float noise)


def rows_R(side, e, x, r, fin, fout):
    """(gross_R, fee_R, net_R); rejects missing/nonpositive risk and unknown sides."""
    if side not in (1, -1):
        raise ValueError('unknown side')
    if r is None or r <= 0:
        raise ValueError('nonpositive risk')
    g = side * (x - e) / r
    f = (fin + fout) / r
    return g, f, g - f


def hand_check():
    """3 hand-computed rows (OURS fixtures; fee = rate*price, qty 1). Long win, short loss, long timeout."""
    cases = [(1, D(100), D(102), D(2), D('0.02'), D('0.0204'), D(1), D('0.0202'), D('0.9798')),
             (-1, D(100), D(101), D(1), D('0.02'), D('0.0505'), D(-1), D('0.0705'), D('-1.0705')),
             (1, D(100), D('100.5'), D(2), D('0.05'), D('0.05025'), D('0.25'), D('0.050125'), D('0.199875'))]
    for s, e, x, r, fi, fo, g, f, n in cases:
        got = rows_R(s, e, x, r, fi, fo)
        assert got == (g, f, n), (got, (g, f, n))
        assert got[2] == got[0] - got[1]
    for bad in ((0, D(1), D(1), D(1), D(0), D(0)), (1, D(1), D(1), D(0), D(0), D(0))):
        try:
            rows_R(*bad)
        except ValueError:
            continue
        raise AssertionError('bad row accepted')


def reconcile(path):
    rows = list(csv.DictReader(Path(path).open(newline='', encoding='utf-8')))
    filled = [r for r in rows if r['filled'] == 'Y']
    unf = [r for r in rows if r['filled'] == 'N']
    assert len(rows) == 772 and len(filled) == 255 and len(unf) == 517, (len(rows), len(filled), len(unf))
    src = [r for r in csv.DictReader(LC.open(newline='', encoding='utf-8')) if r['E1'] == 'True' and r['S2_K5_X0_2R'] != '']
    src.sort(key=lambda r: int(r['touch_t']))  # stable: ledger id order; (day, touch_t) alone is not unique
    stored = {r['id']: D(s['S2_K5_X0_2R']) for r, s in zip(rows, src)}
    assert all(r['touch_t'] == s['touch_t'] for r, s in zip(rows, src)), 'ledger order differs from source'
    diffs, sg, sf, sn, wins = [], D(0), D(0), D(0), 0
    for r in rows:
        t = int(r['touch_t'])
        assert DEV_START_MS <= t < DEV_END_MS, ('outside DEV', r['id'])
        if r['filled'] == 'N':
            assert r['entry'] == '' and r['exit'] == '' and stored[r['id']] == 0, ('unfilled row', r['id'])
            continue
        assert int(r['entry_t']) < DEV_END_MS and int(r['exit_t']) < DEV_END_MS and int(r['exit_t']) >= int(r['entry_t'])
        g, f, n = rows_R(int(r['side']), D(r['entry']), D(r['exit']), D(r['R_dist']), D(r['fee_in']), D(r['fee_out']))
        assert abs(g - D(r['gross_R'])) < D('1e-9') and abs(f - D(r['fee_R'])) < D('1e-9') and abs(n - (g - f)) == 0
        d = n - stored[r['id']]
        if abs(d) > TOL:
            diffs.append((r['id'], str(n), str(stored[r['id']])))
        sg += g; sf += f; sn += n; wins += n > 0
    k = D(len(filled))
    print(f'filled={len(filled)} unfilled={len(unf)} mean_gross_R={sg / k:.6f} mean_fee_R={sf / k:.6f} mean_net_R={sn / k:.6f} win%={D(100) * wins / k:.2f}')
    print(f'rows where recomputed net differs from stored 3dp net by > {TOL}: {len(diffs)}')
    for x in diffs[:20]:
        print('  UNEXPLAINED', x)
    return diffs


if __name__ == '__main__':
    hand_check()
    print('hand rows OK (3)')
    try:
        d = reconcile(sys.argv[1] if len(sys.argv) > 1 else HERE / 'ledger.csv')
    except (AssertionError, KeyError, ValueError) as e:
        print('RECONCILE FAIL', repr(e))
        sys.exit(1)
    sys.exit(1 if d else 0)
