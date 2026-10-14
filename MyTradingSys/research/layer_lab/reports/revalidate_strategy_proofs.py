"""Synthetic audit witnesses only. No market files/network; no performance rerun."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'MyTradingSys/research/orderflow_views_2026-10-14/study.py'
spec = importlib.util.spec_from_file_location('audited_study', STUDY)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
proofs = {}

# Every falling-price/rising-CVD window here is both DIV and CONTROL.
B = np.zeros((250, 6))
B[:, 0] = B[:, 3] = 200 - np.arange(250) * .1
B[:, 1], B[:, 2] = B[:, 3] + .05, B[:, 3] - .05
B[:, 4], B[:, 5] = 2, 1.5
sig, _, _ = m.signals(B, 15, .0025, 'long')
assert sig[0].sum() > 0 and np.array_equal(sig[0], sig[1])
proofs['shared_events'] = {'div': int(sig[0].sum()), 'control': int(sig[1].sum()),
                          'intersection': int((sig[0] & sig[1]).sum())}

# Execute the actual edge assignment in isolation: no DEV -> no possible pass,
# however favorable validation/holdout may be. This is classification, not data.
tree = ast.parse(STUDY.read_text(encoding='utf-8'))
assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                          and t.value.id == 'line' and isinstance(t.slice, ast.Constant)
                          and t.slice.value == 'edge' for t in n.targets))
env = {'d': None, 'line': {'VAL': {'diff': 99}, 'HOLDOUT': {'diff': 99}}}
exec(compile(ast.Module(body=[assignment], type_ignores=[]), str(STUDY), 'exec'), env)
assert env['line']['edge'] is False
proofs['no_dev_forces_false'] = env['line']

# Executable synthetic path: long at 100, stop99, later bar opens90 high91.
# study.trade books a stop99 although that bar never traded99.
A = np.tile([100., 100.2, 99.8, 100., 2., 1.], (122, 1))
A[1:] = [90., 91., 89., 90., 2., 1.]
r = m.trade(A, 0, 99 / .999, 'long')
assert abs(r[3] - (-1.1)) < 1e-8
proofs['gap_stop'] = {'reported_percent': r[3], 'open90_percent_same_fee': -10.1,
                     'bar_high': 91, 'assumed_stop_fill': 99}

# Same common population: subset-v-all attenuates subgroup-v-complement.
x, z = np.array([2., 4.]), np.array([0., 2.])
y = np.r_[x, z]
assert x.mean() - y.mean() == .5 * (x.mean() - z.mean())
proofs['estimand'] = {'subset_minus_all': float(x.mean()-y.mean()),
                     'subset_minus_complement': float(x.mean()-z.mean()),
                     'note': 'identity before independent cooldown sampling; no historical effect estimate'}

# Copy current line evidence with hashes so the review remains inspectable.
selections = {
 'MyTradingSys/research/orderflow_views_2026-10-14/study.py': [(8,26),(153,179),(182,215),(220,275)],
 'MyTradingSys/system/tasks/tom-v2-btc-min-stop-width.json': [(5,22),(39,54)],
 'MyTradingSys/system/tasks/tom-btc-event-study.json': [(5,20),(35,47)],
 'MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md': [(60,68),(118,143)],
 'MyTradingSys/research/tom_btc_2026-10-13/chart_lab.py': [(134,153),(193,250)],
 'MyTradingSys/backtest/tom_bt.py': [(175,221)],
 'MyTradingSys/backtest/layers/fabio/orderflow_bars.py': [(5,23),(198,211)],
 'MyTradingSys/backtest/layers/fabio/v3/day_gates.py': [(85,105)],
 'MyTradingSys/system/GO_LIVE_BAR.md': [(1,20)],
 'MyTradingSys/system/CODEX_START.md': [(58,66)],
}
evidence = {}
for relative, ranges in selections.items():
    p = ROOT / relative
    raw = p.read_bytes()
    lines = raw.decode('utf-8').splitlines()
    evidence[relative] = {'sha256': hashlib.sha256(raw).hexdigest(),
                         'excerpts': [f'{i}: {lines[i-1]}' for a,b in ranges for i in range(a,min(b,len(lines))+1)]}
out = {'scope': 'synthetic mechanics only; no historical magnitude inferred', 'proofs': proofs, 'evidence': evidence}
destination = Path(__file__).with_name('2026-10-15_strategy-proof-pack.json')
destination.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(proofs, indent=2))
print('PASS: 4 synthetic witnesses; source excerpts and SHA256 saved to', destination)
