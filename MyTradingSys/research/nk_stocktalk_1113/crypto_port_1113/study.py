"""Run the PRE_REG.md study. Usage: python study.py [--regime]"""
import sys, os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'backtest'))
import rules, fees
DATA = os.path.join(HERE, '..', '..', '..', '..', 'runtime_data', 'edge-nk-rsi-hilega-1113')
SYMS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'BNBUSDT', 'ADAUSDT', 'LINKUSDT', 'LTCUSDT', 'AVAXUSDT']
FEE = 2 * fees.BINANCE_TAKER
M5 = pd.Timedelta(minutes=5)
SPL = {'DEV': ('2020-01-01', '2024-07-01'), 'VALIDATION': ('2024-07-01', '2025-07-01'), 'RECENT': ('2025-07-01', '2100-01-01')}
COLS = ['sym', 'ts', 'ei', 'xi', 'dir', 'gross']


class Sym:
    def __init__(self, name):
        self.name = name
        d5 = rules.load5(os.path.join(DATA, name + '_5m.csv'))
        self.grid = pd.date_range(d5.index[0], d5.index[-1], freq='5min')
        self.d5 = d5.reindex(self.grid)
        self.c = self.d5['c'].values
        self.d15 = rules.resample(d5, '15min', 3)
        self.d10 = rules.resample(d5, '10min', 2)
        self.d1 = rules.resample(d5, '1D', 288)
        self.r15 = rules.rsi_wilder(self.d15['c'], 14)
        self.s5 = rules.hilega_state(d5['c'])
        self.s10 = rules.hilega_state(self.d10['c'])
        self.s15 = rules.hilega_state(self.d15['c'])
        self.s1d = rules.hilega_state(self.d1['c'])
        self.t0 = self.grid[0]

    def idx(self, ts):
        return np.asarray((pd.DatetimeIndex(ts) - self.t0) // M5).astype(int)


def trades_df(sym, ts_entry, ei, xi, direction):
    ret = rules.fwd_ret(sym.c, np.asarray(ei), np.asarray(xi))
    df = pd.DataFrame({'sym': sym.name, 'ts': pd.DatetimeIndex(ts_entry), 'ei': ei, 'xi': xi,
                       'dir': direction, 'gross': np.asarray(direction) * ret})
    return df.dropna(subset=['gross'])


def state_at(series, ts):
    return series.reindex(pd.DatetimeIndex(ts)).fillna(0).values


def r1_trades(sym, E_hour, h, variant, confirm=False):
    days = pd.date_range(sym.t0.normalize() + pd.Timedelta(days=1), sym.grid[-1].normalize(), freq='1D')
    E = days + pd.Timedelta(hours=E_hour)
    E = E[(E + pd.Timedelta(hours=h)) <= sym.grid[-1] + M5]
    a = sym.r15.reindex(E - pd.Timedelta(minutes=30)).values
    b = sym.r15.reindex(E - pd.Timedelta(minutes=15)).values
    with np.errstate(invalid='ignore'):
        up = (a >= 70) | (b >= 70)
        dn = (a <= 30) | (b <= 30)
    sig = np.where(up & ~dn, 1, np.where(dn & ~up, -1, 0))
    if confirm:
        s5 = state_at(sym.s5, E - M5)
        s10 = state_at(sym.s10, E - pd.Timedelta(minutes=10))
        sig = np.where((sig == 1) & (s5 == 1) & (s10 == 1), 1,
                       np.where((sig == -1) & (s5 == -1) & (s10 == -1), -1, 0))
    m = sig != 0
    Em = E[m]
    d = sig[m] * (1 if variant == 'CONT' else -1)
    ei = sym.idx(Em) - 1
    xi = ei + h * 12
    return trades_df(sym, Em, ei, xi, d)


def r2_trades(sym, tf, side):
    d = {10: sym.d10, 15: sym.d15}[tf]
    s = {10: sym.s10, 15: sym.s15}[tf]
    tfm = pd.Timedelta(minutes=tf)
    want = 1 if side == 'LONG' else -1
    sv = s.values
    prev = np.r_[0, sv[:-1]]
    close_t = d.index + tfm
    dday = close_t.normalize() - pd.Timedelta(days=1)
    dst = sym.s1d.reindex(dday).fillna(0).values
    flips = np.where((sv == want) & (prev != want) & (dst == want))[0]
    lo = d['l'].values
    hi = d['h'].values
    op = d['o'].values
    cl = d['c'].values
    opp = (sv == -want)
    nxt_opp = np.full(len(sv), len(sv))
    last = len(sv)
    for i in range(len(sv) - 1, -1, -1):
        nxt_opp[i] = last
        if opp[i]:
            last = i
    rows = []
    for i in flips:
        j = nxt_opp[i]
        if j >= len(sv):
            continue
        stop = lo[i] if want == 1 else hi[i]
        hit = (lo[i + 1:j + 1] <= stop) if want == 1 else (hi[i + 1:j + 1] >= stop)
        entry = cl[i]
        if hit.any():
            k = i + 1 + int(np.argmax(hit))
            ex = min(stop, op[k]) if want == 1 else max(stop, op[k])
            xt = d.index[k]
        else:
            ex = cl[j]
            xt = d.index[j]
        rows.append((close_t[i], entry, ex, close_t[i] - M5, xt + tfm - M5))
    if not rows:
        return pd.DataFrame(columns=COLS)
    ent = np.array([r[1] for r in rows])
    ex = np.array([r[2] for r in rows])
    return pd.DataFrame({'sym': sym.name, 'ts': pd.DatetimeIndex([r[0] for r in rows]),
                         'ei': sym.idx([r[3] for r in rows]), 'xi': sym.idx([r[4] for r in rows]),
                         'dir': want, 'gross': want * (ex / ent - 1)})


def r4_trades(sym, side):
    d = sym.d1
    want = 1 if side == 'LONG' else -1
    c = d['c']
    sma = c.rolling(20).mean()
    st = sym.s1d.reindex(d.index).fillna(0)
    wk = d.copy()
    wk['wk'] = wk.index - pd.to_timedelta(wk.index.dayofweek, unit='D')
    w = wk.groupby('wk').agg(o=('o', 'first'), c=('c', 'last'), n=('c', 'count'))
    w = w[w['n'] == 7]
    po, pc = w['o'].shift(1), w['c'].shift(1)
    bull = (w['c'] > w['o']) & (pc < po) & (w['c'] >= po) & (w['o'] <= pc)
    bear = (w['c'] < w['o']) & (pc > po) & (w['c'] <= po) & (w['o'] >= pc)
    flag = (bull if want == 1 else bear).copy()
    flag.index = flag.index + pd.Timedelta(days=6)
    wf = flag.reindex(d.index).ffill().fillna(False).astype(bool)
    cond = ((st == want) & ((c > sma) if want == 1 else (c < sma))) | wf
    cond = cond & sma.notna()
    cv = cond.values
    prev = np.r_[False, cv[:-1]]
    ent = np.where(cv & ~prev)[0]
    sv = st.values
    rows = []
    for i in ent:
        js = np.where(sv[i + 1:] == -want)[0]
        if not len(js):
            continue
        j = i + 1 + js[0]
        rows.append((d.index[i] + pd.Timedelta(days=1), c.values[i], c.values[j], d.index[j] + pd.Timedelta(days=1)))
    if not rows:
        return pd.DataFrame(columns=COLS)
    ent_p = np.array([r[1] for r in rows])
    ex_p = np.array([r[2] for r in rows])
    return pd.DataFrame({'sym': sym.name, 'ts': pd.DatetimeIndex([r[0] for r in rows]),
                         'ei': sym.idx([r[0] - M5 for r in rows]), 'xi': sym.idx([r[3] - M5 for r in rows]),
                         'dir': want, 'gross': want * (ex_p / ent_p - 1)})


def placebo(syms, tr, split, draws=500, seed=7):
    rng = np.random.default_rng(seed)
    a_ts, b_ts = [pd.Timestamp(x) for x in SPL[split]]
    parts = []
    for name, g in tr.groupby('sym'):
        s = syms[name]
        a = max(0, int((a_ts - s.t0) // M5))
        b = min(len(s.c), int((b_ts - s.t0) // M5))
        if b - a < 1000:
            continue
        ei = g['ei'].values
        dur = (g['xi'] - g['ei']).values
        dr = g['dir'].values
        sh = rng.integers(3 * 288, 60 * 288, (draws, len(g))) * np.where(rng.random((draws, len(g))) < 0.5, 1, -1)
        e2 = a + np.mod(ei[None, :] - a + sh, b - a)
        x2 = e2 + dur[None, :]
        n = len(s.c)
        ok = x2 < n
        ce = s.c[np.clip(e2, 0, n - 1)]
        cx = s.c[np.clip(x2, 0, n - 1)]
        with np.errstate(invalid='ignore', divide='ignore'):
            r = dr[None, :] * (cx / ce - 1) - FEE
        parts.append(np.where(ok, r, np.nan))
    if not parts:
        return np.full(draws, np.nan)
    return np.nanmean(np.concatenate(parts, axis=1), axis=1)


def build_cells(syms):
    cells = {}
    for var in ['CONT', 'REV']:
        for E_name, E_hour in [('00UTC', 0), ('20UTC', 20), ('21UTC', 21)]:
            for h in [1, 4, 8]:
                cells[f'R1_{var}_{E_name}_{h}h'] = [r1_trades(s, E_hour, h, var) for s in syms.values()]
                cells[f'R3_{var}_{E_name}_{h}h'] = [r1_trades(s, E_hour, h, var, confirm=True) for s in syms.values()]
    for tf in [10, 15]:
        for side in ['LONG', 'SHORT']:
            cells[f'R2_{tf}m_{side}'] = [r2_trades(s, tf, side) for s in syms.values()]
    for side in ['LONG', 'SHORT']:
        cells[f'R4_daily_{side}'] = [r4_trades(s, side) for s in syms.values()]
    return cells


def main():
    syms = {n: Sym(n) for n in SYMS if os.path.exists(os.path.join(DATA, n + '_5m.csv'))}
    print('symbols', list(syms), flush=True)
    if '--regime' in sys.argv:
        d = syms['BTCUSDT'].d1['c']
        sma = d.rolling(200).mean()
        for sp, (a, b) in SPL.items():
            x = d[(d.index >= a) & (d.index < b)]
            print(f"{sp}: BTC {x.iloc[0]:.0f}->{x.iloc[-1]:.0f} ({x.iloc[-1] / x.iloc[0] - 1:+.0%}), up days "
                  f"{(x.pct_change() > 0).mean():.0%}, days above SMA200 {(x > sma.reindex(x.index)).mean():.0%}, n_days {len(x)}")
        return
    cells = build_cells(syms)
    res = []
    persym = {}
    for name, lst in cells.items():
        parts = [x for x in lst if len(x)]
        tr = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=COLS)
        if len(tr):
            tr['net'] = tr['gross'] - FEE
            tr['split'] = tr['ts'].map(rules.split_of)
        for sp in SPL:
            g = tr[tr['split'] == sp] if len(tr) else tr
            row = {'cell': name, 'split': sp, 'n': len(g)}
            if len(g) >= 5:
                wk = (g['ts'] - pd.to_timedelta(g['ts'].dt.dayofweek, unit='D')).dt.normalize().values.astype('int64')
                ci, p = rules.week_bootstrap(g['net'].values, wk)
                pl = placebo(syms, g, sp)
                p95 = float(np.nanpercentile(pl, 95))
                row.update(mean_gross=g['gross'].mean(), mean_net=g['net'].mean(), ci_lo=ci[0], ci_hi=ci[1], p=p,
                           winrate=(g['net'] > 0).mean(), plc_mean=float(np.nanmean(pl)), plc_p95=p95,
                           beats_plc=bool(g['net'].mean() > p95))
                if sp == 'VALIDATION' and g['net'].mean() > 0:
                    persym[name] = g.groupby('sym')['net'].agg(['count', 'mean']).round(5).to_dict('index')
            res.append(row)
        print('done', name, flush=True)
    R = pd.DataFrame(res)
    R['bh'] = False
    v = R[(R.split == 'VALIDATION') & R['p'].notna()]
    if len(v):
        R.loc[v.index, 'bh'] = rules.bh(v['p'].values, 0.10)
    R['pass'] = False
    for i, r in R[R.split == 'VALIDATION'].iterrows():
        rec = R[(R.cell == r.cell) & (R.split == 'RECENT')]
        rec_pos = bool(len(rec) and rec.iloc[0].get('mean_net', -1) > 0)
        R.loc[i, 'pass'] = bool(r.n >= 30 and r.get('mean_net', -1) > 0 and r.get('ci_lo', -1) > 0
                                and r.get('beats_plc', False) and r['bh'] and rec_pos)
    R.to_csv(os.path.join(HERE, 'results.csv'), index=False)
    json.dump(persym, open(os.path.join(HERE, 'persym_validation.json'), 'w'), indent=1)
    pd.set_option('display.width', 250)
    print(R.round(5).to_string())


if __name__ == '__main__':
    main()
