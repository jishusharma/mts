"""Operator idea 2026-10-29 (shot f2fb8d432eb7): trade the side a candle takes away from the previous close.
Long when the new bar trades above the previous close, short when below; get out when price goes beyond the previous
candle's low (long) / high (short). Exit question: when to take profit after a Bollinger expansion (his arrow).

Definitions fixed before the first run (OURS where not his words):
- Data: Binance USD-M BTCUSDT 1m archive; DEV = 2022-01-01 .. 2025-12-31 only (2026 = holdout, not read). TF bars built from 1m.
- Trigger (his rule + OURS threshold e): inside bar k, the first 1m bar whose high >= C[k-1]*(1+e) -> long at C[k-1]*(1+e);
  low <= C[k-1]*(1-e) -> short at C[k-1]*(1-e). If one 1m bar touches both, skip the bar. One position at a time.
- Stop (his rule): long = low of the previous TF bar, short = its high. After each TF bar closes the stop trails to that
  closed bar's low/high if tighter (his "below the low of the previous candle", read as trailing: OURS).
  If the trigger 1m bar also touches the stop, the trade is a stop-out.
- Exits (one run each): X1 = stop/trail only; X2 = also exit at the close of the first TF bar that closes outside BB(20,2)
  on the trade side (take profit on expansion: his arrow, OURS rule); X3 = also exit at the close of the first TF bar that
  closes back inside the band after a close outside (OURS); X4 = no bar trail: initial stop only, exit at the close of the first
  TF bar that closes back across the BB mid against the trade (rides an expansion like his arrow; OURS).
- Filter F (his example, OURS): previous TF bar closed across the BB mid in the trade direction (break from the centre line).
- Costs: 10 bp taker round trip + 2 bp slippage = 12 bp of price per trade (fees.py BINANCE_TAKER, FORMULAS.md section 17).
- Report: n, win rate, mean net % per trade, mean R (net), sum net %, per TF, exit, filter. Fee-net, DEV only, no holdout.
"""
import glob, sys
import numpy as np, pandas as pd

COST = 0.0012
fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if '2026' not in f]
df = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4]) for f in fs], ignore_index=True)
df.columns = ['t', 'o', 'h', 'l', 'c']
df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t) // 1000
df = df.drop_duplicates('t').sort_values('t').reset_index(drop=True)
T, H1, L1, C1 = (df[k].to_numpy(float) for k in ['t', 'h', 'l', 'c'])

def run(tf, e, exitmode, filt):
    sec = tf * 60
    g = (T // sec).astype(np.int64)
    starts = np.r_[0, np.nonzero(np.diff(g))[0] + 1]; ends = np.r_[starts[1:], len(g)]
    full = (ends - starts) == tf
    gk = g[starts]
    Hk = np.maximum.reduceat(H1, starts); Lk = np.minimum.reduceat(L1, starts); Ck = C1[ends - 1]
    cs = pd.Series(Ck); mid = cs.rolling(20).mean().to_numpy(); sd = cs.rolling(20).std(ddof=0).to_numpy()
    up, lo = mid + 2 * sd, mid - 2 * sd
    out = []; k = 21; nk = len(starts)
    while k < nk - 1:
        if not (full[k] and full[k - 1]) or gk[k] - gk[k - 1] != 1: k += 1; continue
        pc = Ck[k - 1]; lt, st = pc * (1 + e), pc * (1 - e)
        side = 0; j0 = -1
        for j in range(starts[k], ends[k]):
            a, b = H1[j] >= lt, L1[j] <= st
            if a and b: break
            if a: side, j0 = 1, j; break
            if b: side, j0 = -1, j; break
        if side == 0: k += 1; continue
        if filt:
            ok = (Ck[k - 1] > mid[k - 1] and Ck[k - 2] <= mid[k - 2]) if side == 1 else (Ck[k - 1] < mid[k - 1] and Ck[k - 2] >= mid[k - 2])
            if not ok: k += 1; continue
        ent = lt if side == 1 else st
        stop = Lk[k - 1] if side == 1 else Hk[k - 1]
        risk = abs(ent - stop) / ent
        if risk <= 0: k += 1; continue
        px = None; was_out = False; kk = k; j = j0
        while px is None:
            # walk 1m bars of TF bar kk from j
            for jj in range(j, ends[kk]):
                if (side == 1 and L1[jj] <= stop) or (side == -1 and H1[jj] >= stop):
                    px = stop; break
            if px is not None: break
            # TF bar kk closed
            c = Ck[kk]
            if exitmode == 2 and ((side == 1 and c > up[kk]) or (side == -1 and c < lo[kk])): px = c; break
            if exitmode == 3:
                outside = (side == 1 and c > up[kk]) or (side == -1 and c < lo[kk])
                if was_out and not outside: px = c; break
                was_out = was_out or outside
            if exitmode == 4:
                if (side == 1 and c < mid[kk]) or (side == -1 and c > mid[kk]): px = c; break
            else:
                stop = max(stop, Lk[kk]) if side == 1 else min(stop, Hk[kk])
            kk += 1
            if kk >= nk or gk[kk] - gk[kk - 1] != 1: px = Ck[kk - 1]; kk -= 1; break
            j = starts[kk]
        gross = side * (px - ent) / ent
        out.append((T[starts[k]], gross - COST, (gross - COST) / risk, risk))
        k = kk + 1
    return pd.DataFrame(out, columns=['t', 'net', 'R', 'risk'])

rows = []
for tf in (5, 15, 60):
    for e in (0.0, 0.0005):
        for filt in (False, True):
            for ex in (1, 2, 3, 4):
                r = run(tf, e, ex, filt)
                if len(r) == 0: continue
                rows.append(dict(tf=f'{tf}m', e_bp=e * 1e4, filter='mid-cross' if filt else 'none', exit={1: 'trail', 2: 'trail+TP outside band', 3: 'trail+back inside band', 4: 'stop + exit on mid cross'}[ex],
                                 n=len(r), win=(r.net > 0).mean(), mean_net_pct=r.net.mean() * 100, mean_R=r.R.mean(),
                                 sum_net_pct=r.net.sum() * 100, med_risk_pct=r.risk.median() * 100,
                                 gross_mean_pct=(r.net + COST).mean() * 100))
                print(rows[-1], flush=True)
R = pd.DataFrame(rows)
print(R.to_string(index=False, float_format=lambda v: f'{v:.3f}'))
if len(sys.argv) > 1: R.to_csv(sys.argv[1], index=False)
