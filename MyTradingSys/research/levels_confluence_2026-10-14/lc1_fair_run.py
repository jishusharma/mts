"""Re-state LC1 on the fair control.  python MyTradingSys/research/levels_confluence_2026-10-14/lc1_fair_run.py [--skip-real]
DEV decisions 2022-04-01..2024-06-30 only (bars end asserted < 2024-07-01). Writes lc1_fair_dev.csv next to this file."""
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from levels import levels_by_day  # noqa: E402
import levels_hold as LH  # noqa: E402
from MyTradingSys.backtest.bt.bt_data import load_klines  # noqa: E402

UTC = dt.timezone.utc
START = int(dt.datetime(2022, 3, 21, tzinfo=UTC).timestamp() * 1000)
DEC0 = int(dt.datetime(2022, 4, 1, tzinfo=UTC).timestamp() * 1000)
END = int(dt.datetime(2024, 7, 1, tzinfo=UTC).timestamp() * 1000)


def windowed_levels(bars):
    """Each decision day reads only the prior 14 days; build from a 14-day window (same function, same rows)."""
    byday = defaultdict(list)
    for b in bars:
        byday[int(b['t']) // LH.DAY_MS].append(b)
    out = {}
    for d in sorted(byday):
        if d * LH.DAY_MS < DEC0:
            continue
        win = [b for k in range(d - 14, d + 1) for b in byday.get(k, [])]
        out[d] = levels_by_day(win).get(d, [])
    return out


def main(skip_real=False):
    # load_klines globs every csv in the folder; other symbols (ETHUSDT-...) now sit beside BTC, so stage BTC only.
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix='lc1_btc_'))
    (tmp / 'klines').mkdir()
    for f in Path('F:/MTS/data/tom_raw/klines').glob('BTCUSDT-1m-202[234]-*.csv'):
        shutil.copy(f, tmp / 'klines' / f.name)
    bars = load_klines(tmp, start_ms=START, end_ms=END)
    shutil.rmtree(tmp, ignore_errors=True)
    assert max(b['t'] for b in bars) < END
    levels = windowed_levels(bars)
    dev = [b for b in bars if b['t'] >= DEC0]
    res = LH.analyze_fair(dev, levels, skip_real=skip_real)
    name = 'lc1_fair_dev_skipreal.csv' if skip_real else 'lc1_fair_dev.csv'
    rows = [dict(family=f, **r) for f, r in res.items()]
    with open(HERE / name, 'w', newline='\n', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='
')
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r['family'], r['n_touch'], f"{r['hold']:.3f} fair {r['fair_ctl_hold']:.3f} diff {r['diff']:+.3f} "
              f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] {r['verdict']} (pub {r['pub_verdict']})")
    print('KEEP:', [r['family'] for r in rows if r['verdict'] == 'KEEP'])


if __name__ == '__main__':
    main('--skip-real' in sys.argv)
