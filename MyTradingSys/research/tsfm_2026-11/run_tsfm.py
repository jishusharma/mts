"""Run: <venv python> run_tsfm.py --split DEV [--klines DIR]. Needs torch + chronos-forecasting (venv outside repo)."""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tsfm_lib as L  # noqa: E402

CTX = 256
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def forecast(pipe, logc, torch):
    idx = np.arange(CTX, len(logc))
    out = np.empty((len(idx), 9))
    for s in range(0, len(idx), 128):
        ii = idx[s:][:128]
        ctx = torch.tensor(np.stack([logc[i - CTX:i] for i in ii]), dtype=torch.float32)
        q, _ = pipe.predict_quantiles(ctx, prediction_length=1, quantile_levels=LEVELS)
        out[s:s + len(ii)] = q[:, 0, :].numpy()
    return idx, out


def study(bars, pipe, torch, name):
    logc = np.log(bars['close'].values)
    idx, q = forecast(pipe, logc, torch)
    # forecast at index i predicts logc[i] given logc[i-CTX:i]; trade: decide at close of bar i-1, hold bar i
    prev = logc[idx - 1]
    y = logc[idx] - prev
    qr = q - prev[:, None]
    base_sd = pd.Series(np.diff(logc)).rolling(CTX).std().shift(0).values[idx - 1]
    from statistics import NormalDist
    nd = NormalDist()
    gq = np.stack([base_sd * nd.inv_cdf(t) for t in LEVELS], 1)
    pin, pin_b = L.pinball(y, qr, LEVELS), L.pinball(y, gq, LEVELS)
    cov = L.coverage(y, qr[:, 0], qr[:, -1])
    long = qr[:, 4] > L.COST
    net = np.where(long, y - L.COST, 0.0)
    sd1 = float(np.std(np.diff(logc)))
    t = bars.index[idx]
    weeks = np.array([f'{a}-{b}' for a, b in zip(t.isocalendar().year, t.isocalendar().week)])
    n = int(long.sum())
    res = dict(bar=name, bars=len(idx), n_trades=n, pinball=pin, pinball_gauss=pin_b, coverage80=cov,
               hit=float((y[long] > L.COST).mean()) if n else None)
    if n:
        rt = net[long]
        lo, hi = L.week_boot(rt, weeks[long])
        rng = np.random.default_rng(7)
        sh = np.array([net[rng.permutation(len(net))[:n]].mean() for _ in range(2000)])
        # shuffled control: random bars, long, same count
        rnd = np.array([(y[rng.choice(len(y), n, replace=False)] - L.COST).mean() for _ in range(2000)])
        obs = float(rt.mean())
        p = float((rnd >= obs).mean())
        m = 108
        res.update(mean_net_pct=100 * obs, ci_pct=[100 * lo, 100 * hi], mean_net_R=obs / sd1,
                   ci_R=[lo / sd1, hi / sd1], rand_mean_pct=100 * float(rnd.mean()), p_random=p,
                   bh_always_long_pct=100 * float((y - L.COST).mean()))
        res['verdict'] = ('PASS' if n >= 30 and lo > 0 and p < 0.05 / m else 'FAIL' if hi < 0 else 'INCONCLUSIVE')
        res['underpowered'] = n < 519
    else:
        res['verdict'] = 'INCONCLUSIVE'
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True)
    ap.add_argument('--klines', default=os.path.join(L.ROOT, 'Dumps', 'backtest', 'raw', 'klines'))
    ap.add_argument('--model', default='amazon/chronos-bolt-small')
    a = ap.parse_args()
    if a.split != 'DEV':
        sys.exit('only --split DEV')
    import torch
    from chronos import BaseChronosPipeline
    pipe = BaseChronosPipeline.from_pretrained(a.model, device_map='cpu', torch_dtype=torch.float32)
    df = L.load_1m(a.klines)
    df = df[(df.index >= L.splits.DEV_START) & (df.index < L.splits.DEV_END)]
    out = []
    for rule in ('4h', '8h'):
        b = L.build_bars(df, rule)
        L.guard_dev(b.index)
        out.append(study(b, pipe, torch, rule))
        print(json.dumps(out[-1]), flush=True)
    json.dump(out, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
