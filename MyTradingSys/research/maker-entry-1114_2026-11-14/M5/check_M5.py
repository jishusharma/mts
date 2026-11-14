r"""Independent checker for M5. Own scalar bar-by-bar fill sim (does NOT import maker_fill). Signals come from
parent_study/orig_study5 (signal generation only), 1m bars from raw F:\MTS\data_cache\binance_1m."""
import sys, pickle, datetime as dt, random
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parent_study as ps, orig_study5 as s5
ORIG = r"F:\MTS\data_cache\moved_from_worktrees\mts-jis-nb-edge5-ny-value-poc-target-1113-2\runtime_data\edge5-ny-value-poc"
MK, TK = 0.0003, 0.0006

def tick_of(m):
    v = np.unique(np.round(np.concatenate([m['o'], m['h'], m['l'], m['c']]), 10))
    d = np.diff(v); d = d[d > 1e-12]
    return float(d.min())

def sim(m, tick, L, stop, poc, t_close, t_end, cut=None):
    """SHORT only. bars with t>=t_close. returns (status, net_R, gross_R, exit)"""
    t, h, l, o = m['t_ms'], m['h'], m['l'], m['o']
    n = len(t)
    if cut is not None: n = int(np.searchsorted(t, cut))
    i = int(np.searchsorted(t[:n], t_close))
    life_end = min(t_close + 30 * 60000, t_end)
    filled = None
    j = i
    while j < n and t[j] < life_end:
        if h[j] >= L + tick:
            filled = j; break
        if h[j] >= stop:     # stop trades before/at same bar and not through L -> cancel
            return ('miss_stop', 0, 0, None)
        j += 1
    if filled is None: return ('miss', 0, 0, None)
    risk = stop - L
    k = filled
    while k < n and t[k] < t_end:
        if h[k] >= stop:
            ex, fee, kind = stop, TK, 'stop'; break
        if l[k] <= poc - tick:
            ex, fee, kind = poc, MK, 'target'; break
        k += 1
    else:
        kk = int(np.searchsorted(t[:n], t_end))
        if kk >= n: return ('open', None, None, None)
        ex, fee, kind = o[kk], TK, 'time'
    g = (L - ex) / risk
    return ('fill', g - (MK + fee) * L / risk, g, kind)

def main():
    random.seed(5)
    rows = []
    allv = []
    for sym in s5.NEW:
        sigs, _ = pickle.loads((Path(r"F:\MTS\maker_cache\M5") / f"{sym}.pkl").read_bytes())
        ev_list, ns, bars, sess = ps.day_events(sym, ORIG)
        z = np.load(rf"F:\MTS\data_cache\binance_1m\{sym}_1m.npz")
        m = {k: z[k] for k in ('t_ms', 'o', 'h', 'l', 'c')}
        tick = tick_of(m)
        t = bars[0]
        # raw-data cross check original vs fills data
        a = np.searchsorted(m['t_ms'], t[0]); 
        evd = {e['date']: e for e in ev_list}
        for r in sigs:
            if r['ms'] < ps.SPLIT_MS: continue
            ev = evd[r['date']]; ei = r['ei']
            ext = float(ev['H'][:ei + 1].max()); stop = ext * (1 + ps.BUF_FRAC)
            s0, s1 = ps.ac.ny_session_window(dt.date.fromisoformat(ev['date']))
            tsig = int(t[ev['i0'] + ei])
            assert tsig == r['t_sig']
            res = sim(m, tick, float(ev['vah']), stop, float(ev['poc']), tsig + 60000, int(s1))
            # truncation: cut data after order expiry (life end), and after signal close only (decision at fill)
            life_end = min(tsig + 60000 + 30 * 60000, int(s1))
            res_cut = sim(m, tick, float(ev['vah']), stop, float(ev['poc']), tsig + 60000, int(s1), cut=life_end)
            fill_same = (res[0] == 'fill') == (res_cut[0] in ('fill', 'open'))
            mk = r['maker']
            allv.append((sym, r['date'], res, mk, fill_same, res_cut, tsig + 60000 >= int(s1)))
    nf_me = sum(1 for x in allv if x[2][0] == 'fill'); nf_st = sum(1 for x in allv if x[3]['filled'])
    print('VAL n', len(allv), 'fills mine', nf_me, 'study', nf_st)
    dis = [x for x in allv if (x[2][0] == 'fill') != x[3]['filled']]
    print('fill disagreements', len(dis))
    for x in dis[:15]: print(x[0], x[1], x[2], x[3]['filled'], x[3]['reason_missed'])
    both = [x for x in allv if x[2][0] == 'fill' and x[3]['filled']]
    dn = [abs(x[2][1] - x[3]['net_R']) for x in both]
    print('both filled', len(both), 'max |net diff|', max(dn) if dn else None)
    bad = [x for x in both if abs(x[2][1] - x[3]['net_R']) > 1e-6 or x[2][3] != x[3]['exit_type']]
    for x in bad[:15]: print('MISMATCH', x[0], x[1], x[2], x[3]['net_R'], x[3]['exit_type'])
    mine = [x[2][1] for x in allv if x[2][0] == 'fill']
    print('my net R per filled', np.mean(mine), 'per signal', sum(mine) / len(allv), 'fill rate', nf_me / len(allv))
    print('truncation fill decision same for all:', all(x[4] for x in allv))
    print('statuses', {s: sum(1 for x in allv if x[2][0] == s) for s in ('fill', 'miss', 'miss_stop', 'open')})
    nod = [x for x in allv if x[3]['reason_missed'] == 'no_data']
    print('no_data are all signal-close>=session-end:', all(x[6] for x in nod))
    print('study no_data n', len(nod), [(x[0], x[1], x[2][0]) for x in nod])
if __name__ == '__main__': main()

