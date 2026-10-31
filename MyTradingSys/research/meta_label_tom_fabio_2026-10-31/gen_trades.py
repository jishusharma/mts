"""Regenerate the two sim-desk trade lists on DEV (2022-04-01..2024-06-30) by calling the studies' own run(); filled trades only.

(a) Tom VP: the daily-value-area run with the most filled trades among the 12 results/desk-tom_vp-*.json (picked by the
    'filled trades' KPI of the committed result files, see PRE_REG.md): prior_day FADE n6 shift WITH stop 1ATR target POC.
(b) Fabio Model C: the base setting (studies/fabio_v3.py DEFAULT, model C).
Writes <out>/trades_<study>.npz: touch_t (entry time ms), side, net, gross, fees, exit. Prints counts and the unconditional sd only.
Usage: python gen_trades.py [out_dir]   (default F:/MTS/runs/meta_label_tom_fabio_2026-10-31)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SIM = HERE.parent / 'sim_desk'
sys.path.insert(0, str(SIM))
sys.path.insert(0, str(SIM / 'studies'))
import fabio_v3  # noqa: E402
import tom_vp  # noqa: E402

TOM_Q = {'symbol': 'BTCUSDT', 'anchor': 'prior_day', 'setup': 'FADE', 'accept_n': 6, 'shift': 'WITH', 'stop_atr': 1.0, 'target': 'POC'}
FABIO_Q = {'model': 'C'}
OUT = Path('F:/MTS/runs/meta_label_tom_fabio_2026-10-31')


def pick_tom_run():
    """(id, filled, settings label) of the daily-value-area result with the most filled trades."""
    best = None
    for f in sorted((SIM / 'results').glob('desk-tom_vp-*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        lab = next(x['value_plain'] for x in d['what'] if x['name'] == 'Settings')
        n = int(next(k['value'] for k in d['kpis'] if k['label'] == 'filled trades'))
        if lab.startswith('prior_day') and (best is None or n > best[1]):
            best = (d['id'], n, lab)
    return best


def trades(study, p):
    q = study.normalize(p)
    res = study.run(q, progress=lambda *_: None)
    m = np.asarray(res['filled'], bool)
    order = np.argsort(np.asarray(res['touch_t'])[m], kind='stable')
    return q, {k: np.asarray(res[k])[m][order] for k in ('touch_t', 'side', 'net', 'gross', 'fees', 'exit')}


def main(out=OUT):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    print('tom pick:', pick_tom_run())
    for name, study, p in (('tom_vp', tom_vp, TOM_Q), ('fabio_c', fabio_v3, FABIO_Q)):
        q, t = trades(study, p)
        np.savez(out / f'trades_{name}.npz', **t)
        n = len(t['net'])
        print(name, 'label:', study.label(q), '| filled n', n, '| sd(net R, unconditional)', round(float(t['net'].std(ddof=1)), 4),
              '| first/last', int(t['touch_t'][0]), int(t['touch_t'][-1]))


if __name__ == '__main__':
    main(*sys.argv[1:2])
