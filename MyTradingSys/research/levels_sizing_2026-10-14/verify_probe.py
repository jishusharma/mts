"""Independent arithmetic/path checks for this research-only simulator."""
import json
import numpy as np
from probe import run, levels, OUT


def verify():
    # Entry 100, stop 99, both stop and target 102 touched: stop wins.
    a = np.array([[0, 100, 103, 98, 100, 0]], dtype=float)
    r = run(a, (0, 1, 100, 99, 102, 104), 'single', False)
    q = 50/(1+.0006*199)
    assert abs(r['pnl']-(-50-q*100*.0001/480)) < 1e-9
    assert r['fills'][-1][1] == 'stop'
    # Short mirror, same explicit stop-plus-cost sizing.
    r = run(a, (0, -1, 100, 101, 98, 96), 'single', False)
    q = 50/(1+.0006*201)
    assert abs(r['pnl']-(-50-q*100*.0001/480)) < 1e-9
    # A gap cannot fill at an imaginary stop price.
    a = np.array([[0,100,100.1,99.9,100,0], [60000,97,98,96,97,0]], dtype=float)
    r = run(a, (0,1,100,99,102,104), 'single', False)
    assert r['fills'][-1][1:] == ['gap_stop', r['fills'][0][2], 97.0]
    assert r['pnl'] < -50
    # Add triggered by close, filled next open, not earlier in the trigger bar.
    a = np.array([[0,100,100.1,99.7,99.7,0], [60000,99.7,100,99.6,99.8,0]], dtype=float)
    r = run(a, (0,1,100,99,102,104), 'equal_dip', False)
    assert [f[0] for f in r['fills'] if f[1]=='entry'] == [0,60000]
    # Known footprint: POC 100; 70% requires neighboring 110 (volume 3 vs 2).
    assert levels([dict(fp='90:2:0|100:5:0|110:3:0', l='89',h='111')]) == [89,100,110,111]
    d = json.loads((OUT/'results.json').read_text())
    assert d['trials']==8 and not d['validation_read']
    for r in d['records']:
        assert r['day'] < '2025-04-01'
        assert 1 <= r['entries'] <= 3
        bought = sum(f[2] for f in r['fills'] if f[1]=='entry')
        sold = sum(f[2] for f in r['fills'] if f[1]!='entry')
        assert abs(bought-sold) < 1e-8
        assert r['peak_notional'] <= 20000+1e-8
        # Independent whole-campaign cash-flow accounting, long and short.
        gross = r['side']*sum((1 if f[1]!='entry' else -1)*f[2]*f[3] for f in r['fills'])
        assert abs(gross-r['fees_slip']-r['funding_stress']-r['pnl']) < 1e-7
    print('PASS: 5 synthetic path/profile checks; 936 campaign cash-flow, inventory, cap and DEV-window checks')


if __name__ == '__main__':
    verify()
