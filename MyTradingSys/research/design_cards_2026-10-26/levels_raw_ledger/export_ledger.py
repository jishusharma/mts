"""Export the raw DEV fill ledger of the frozen levels rule E1 S2 K5 X0_2R (zero slippage, maker entry/target, taker stop/time).

Ideas (day, touch_t, side, L1, L2, T1, atr1h) come from ladder_ideas_dev.csv (the 2026-10-21 DEV run output; DEV only,
touch_t < 2024-07-01). Each is replayed with ladder.simulate on the DEV 1m klines. No current sim_desk defaults are imported.

  python export_ledger.py [--root F:/MTS/data/tom_raw/klines]
"""
import argparse
import csv
import datetime as dt
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LC = HERE.parents[1] / 'levels_confluence_2026-10-14'
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(LC))
import ladder as ld  # noqa: E402
import ladder_run as lr  # noqa: E402

DAY = 86400000
DEV_END_MS = lr.ms(lr.DEV_END)
COLS = ['id', 'side', 'entry_t', 'entry', 'exit_t', 'exit', 'qty', 'fee_in', 'fee_out', 'R_dist', 'filled', 'src_sha',
        'exit_reason', 'gross_R', 'fee_R', 'net_R', 'day', 'touch_t', 'L1', 'L2', 'stop', 'target']


def fnum(v):
    return '' if v is None else repr(float(v))


def build(root):
    ideas = [r for r in csv.DictReader((LC / 'ladder_ideas_dev.csv').open(newline='', encoding='utf-8'))
             if r['E1'] == 'True' and r['S2_K5_X0_2R'] != '']
    sha = subprocess.run(['git', '-C', str(HERE), 'log', '-1', '--format=%H', '--', str(LC / 'ladder.py')],
                         capture_output=True, text=True).stdout.strip()
    ideas.sort(key=lambda r: int(r['touch_t']))
    cache = {}
    rows = []
    for n, r in enumerate(ideas):
        d, t = int(r['day']), int(r['touch_t'])
        assert t < DEV_END_MS, 'read past DEV'
        if d not in cache:
            cache.clear()
            bars = lr.load_range(root, d * DAY, (d + 1) * DAY)
            cache[d] = (bars, ld.DayCtx(bars))
        bars, ctx = cache[d]
        i = next(k for k, b in enumerate(bars) if b['t'] == t)
        idea = {'side': int(r['side']), 'L1': float(r['L1']), 'L2': float(r['L2']), 'T1': float(r['T1']) if r['T1'] else None,
                'atr1h': float(r['atr1h']) if r['atr1h'] else None}
        res = ld.simulate(bars, i, idea, 'S2', 'K5', 'X0_2R', ld.FEES_MAIN, ctx)
        rid = f'L{n + 1:04d}'
        base = {'id': rid, 'side': idea['side'], 'day': d, 'touch_t': t, 'L1': idea['L1'], 'L2': idea['L2'], 'src_sha': sha}
        if res is None or res['filled_qty'] <= 0:
            rows.append({**base, 'filled': 'N', 'qty': 0, 'exit_reason': 'NO_FILL',
                         'R_dist': fnum(res and res['R_price']), 'stop': fnum(res and res['stop']), 'target': fnum(res and res['target'])})
            continue
        (fp, fq, fb), = res['fills']
        (xp, xq, xr), = res['exits']
        s = ctx.first_adverse(idea['side'], res['stop'], i)
        tb = ctx.first_favorable(idea['side'], res['target'], i + 1)
        xb = s if xr == 'STOP' else tb if xr == 'X0' else ctx.n - 1
        rate = ld.FEES_MAIN['stop'] if xr in ('STOP', 'TIME') else ld.FEES_MAIN['target']
        fin, fout = ld.FEES_MAIN['entry'] * fp * fq, rate * xp * xq
        rows.append({**base, 'filled': 'Y', 'entry_t': bars[fb]['t'], 'entry': fnum(fp), 'exit_t': bars[xb]['t'], 'exit': fnum(xp),
                     'qty': fnum(fq), 'fee_in': fnum(fin), 'fee_out': fnum(fout), 'R_dist': fnum(res['R_price']),
                     'exit_reason': xr, 'gross_R': fnum(res['gross_r']), 'fee_R': fnum(res['fees_r']), 'net_R': fnum(res['net_r']),
                     'stop': fnum(res['stop']), 'target': fnum(res['target'])})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='F:/MTS/data/tom_raw/klines')
    a = ap.parse_args()
    rows = build(a.root)
    out = HERE / 'ledger.csv'
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(out, len(rows), sum(r['filled'] == 'Y' for r in rows), hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
