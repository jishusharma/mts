"""OURS exploratory event study; see frozen METHOD.md. No account access."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
from statistics import NormalDist
import urllib.request
import zipfile

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
DATA = Path('F:/MTS/data/candle_close_dev_2022_2024')
TFS = [1, 2, 3, 5, 15, 30, 60]
NAMES = ['rejection', 'break', 'acceptance', 'reclaim', 'retest', 'strong_break']
MONTHS = [str(x) for x in pd.period_range('2022-01', '2024-06', freq='M')]


def check_month(month):
    if month not in MONTHS:
        raise ValueError('DEV ONLY: month outside frozen 2022-01..2024-06')


def fetch(month):
    check_month(month)
    name = f'BTCUSDT-1m-{month}.zip'
    url = f'https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m/{name}'
    path = DATA/name
    DATA.mkdir(parents=True, exist_ok=True)
    expected = urllib.request.urlopen(url+'.CHECKSUM', timeout=60).read().decode().split()[0]
    raw = path.read_bytes() if path.exists() else urllib.request.urlopen(url, timeout=120).read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise ValueError(f'checksum mismatch {month}')
    if not path.exists():
        path.write_bytes(raw)
    return dict(month=month, url=url, path=str(path), sha256=actual, checksum=expected)


def validate(a):
    if not a.index.is_unique or not a.index.is_monotonic_increasing:
        raise ValueError('duplicate or unordered minute')
    if not np.isfinite(a.to_numpy()).all() or (a[['o', 'h', 'l', 'c']]<=0).any().any():
        raise ValueError('nonfinite or nonpositive prices')
    if ((a.h<a[['o', 'c', 'l']].max(axis=1)) | (a.l>a[['o', 'c', 'h']].min(axis=1))).any():
        raise ValueError('invalid OHLC')


def load():
    manifest = list(ThreadPoolExecutor(max_workers=4).map(fetch, MONTHS))
    parts = []
    for item in manifest:
        with zipfile.ZipFile(item['path']) as z:
            table = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None, dtype=str)
        # Some futures files carry a column header; remove only a verified header row.
        if table.iloc[0, 0] == 'open_time':
            table = table.iloc[1:]
        a = table.iloc[:, :6].astype(float)
        a.columns = ['t', 'o', 'h', 'l', 'c', 'v']
        a.index = pd.to_datetime(a.pop('t').astype('int64'), unit='ms', utc=True)
        month = item['month']
        if not (a.index.strftime('%Y-%m') == month).all():
            raise ValueError('archive month/timestamp mismatch')
        parts.append(a)
    a = pd.concat(parts)
    validate(a)
    gaps = np.where(np.asarray(a.index[1:]-a.index[:-1]) != pd.Timedelta(minutes=1))[0]
    audit = [dict(before=str(a.index[i]), after=str(a.index[i+1]),
                  missing=int((a.index[i+1]-a.index[i]).total_seconds()/60)-1) for i in gaps]
    (OUT/'gaps.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8', newline='\n')
    return a, manifest


def aggregate(a, minutes):
    rs = a.resample(f'{minutes}min', origin='epoch', closed='left', label='right')
    b = rs.agg(dict(o='first', h='max', l='min', c='last', v='sum'))
    return b[rs.c.count()==minutes]


def known(series, times):
    return series.reindex(times, method='ffill').to_numpy()


def forward(a, times, minutes):
    exit_times = times+pd.Timedelta(minutes=minutes)
    out = a.o.reindex(exit_times).to_numpy()/a.o.reindex(times).to_numpy()-1
    full = a.o.reindex(pd.date_range(a.index[0], a.index[-1], freq='min'))
    complete = full.rolling(minutes+1).count().reindex(exit_times).to_numpy()==minutes+1
    out[~complete] = np.nan
    return out


def signatures(b, level, side):
    c = side*(b.c.to_numpy()-level)
    p = side*(b.c.shift(1).to_numpy()-level)
    q = side*(b.c.shift(2).to_numpy()-level)
    wick = b.l.to_numpy()<level if side==1 else b.h.to_numpy()>level
    touch = b.l.to_numpy()<=level if side==1 else b.h.to_numpy()>=level
    span = (b.h-b.l).to_numpy()
    loc = np.divide((b.c-b.l if side==1 else b.h-b.c).to_numpy(), span,
                    out=np.zeros(len(b)), where=span>0)
    body = np.divide(abs(b.c-b.o).to_numpy(), span, out=np.zeros(len(b)), where=span>0)
    br = (p<=0)&(c>0)
    return dict(rejection=(p>0)&wick&(c>0), break_=br,
                acceptance=(q<=0)&(p>0)&(c>0), reclaim=(q>0)&(p<0)&(c>0),
                retest=(q>0)&(p>0)&touch&(c>0), strong_break=br&(loc>=.75)&(body>=.6)) | {'break': br}


def make_events(a):
    # Keep invalid parent periods as NaN, so as-of joins never carry an older level across them.
    day = aggregate(a, 1440).reindex(a.resample('1440min', origin='epoch', label='right').size().index)
    four = aggregate(a, 240).reindex(a.resample('240min', origin='epoch', label='right').size().index)
    # Weekly left boundaries Monday 00:00; labels are availability times.
    wr = a.resample('W-MON', closed='left', label='right')
    week = wr.agg(dict(o='first', h='max', l='min', c='last', v='sum'))
    week.loc[wr.c.count()!=10080, :] = np.nan
    ret30 = day.c/day.c.shift(30)-1
    er = abs(day.c-day.c.shift(30))/day.c.diff().abs().rolling(30).sum()
    phase = pd.Series(np.where(ret30>.1, 'bull', np.where(ret30<-.1, 'bear', 'neutral')), index=day.index)
    trend = pd.Series(np.where(er>=.3, 'trending', 'ranging'), index=day.index)
    fourdir = pd.Series(np.sign(four.c.diff()), index=four.index)
    events = []
    for tf in TFS:
        b = aggregate(a, tf)
        start = b.index-pd.Timedelta(minutes=tf)
        consecutive = pd.Series(b.index).diff().eq(pd.Timedelta(minutes=tf)).to_numpy(copy=True)
        consecutive &= np.roll(consecutive, 1)
        consecutive[:2] = False
        warm = np.isfinite(known(ret30, start)) & np.isfinite(known(er, start))
        returns = forward(a, b.index, 60)
        base = pd.DataFrame(dict(time=b.index, day=b.index.floor('D'), slot=b.index.hour//6,
                                 phase=known(phase, start), trend=known(trend, start),
                                 fourdir=known(fourdir, start), gross=returns))
        for family, parent in [('4h', four), ('day', day), ('week', week)]:
            for edge in ['h', 'l']:
                level = known(parent[edge], start)
                eligible = warm & np.isfinite(returns) & (abs(b.c.to_numpy()/level-1)<=.0025)
                for side in [1, -1]:
                    frame = base.copy()
                    frame['gross'] = returns*side
                    frame['win'] = (returns*side>0).astype(float)
                    frame['level'] = level
                    # Within edge as well as family: tighter match than the pooled report.
                    controls = frame.loc[eligible].groupby(['day', 'slot', 'phase'])[['win', 'gross']].mean()
                    frame = frame.join(controls.rename(columns={'win':'base_win', 'gross':'base_gross'}),
                                       on=['day', 'slot', 'phase'])
                    masks = signatures(b, level, side)
                    for name in NAMES:
                        e = frame.loc[eligible & consecutive & masks[name]].copy()
                        e['tf'], e['family'], e['edge'], e['side'], e['signature'] = tf, family, edge, side, name
                        events.append(e)
        print(f'tf={tf} complete', flush=True)
    e = pd.concat(events).sort_values(['time', 'edge'])
    e = e.drop_duplicates(['day', 'family', 'side', 'signature', 'tf'])
    e['lift'] = e.win-e.base_win
    e['return_lift'] = e.gross-e.base_gross
    return e


def summarize(e, a, manifest):
    calendar = pd.date_range(a.index[0].floor('D'), a.index[-1].floor('D'), freq='D')
    rng = np.random.default_rng(20261014)
    nday = len(calendar)
    starts = rng.integers(0, nday, size=(1000, (nday+6)//7))
    sample = ((starts[:, :, None]+np.arange(7))%nday).reshape(1000, -1)[:, :nday]
    z = NormalDist().inv_cdf(1-.05/(2*126))
    rows = []
    for tf in TFS:
        for family in ['4h', 'day', 'week']:
            for name in NAMES:
                g = e[(e.tf==tf)&(e.family==family)&(e.signature==name)]
                row = dict(tf=tf, family=family, signature=name, n=len(g), days=g.day.nunique())
                if len(g):
                    daily = g.groupby('day')[['win', 'lift', 'gross', 'return_lift']].sum().reindex(calendar, fill_value=0)
                    counts = g.groupby('day').size().reindex(calendar, fill_value=0).to_numpy()
                    denom = counts[sample].sum(axis=1)
                    for col in daily.columns:
                        draws = daily[col].to_numpy()[sample].sum(axis=1)/np.maximum(denom, 1)
                        draws = draws[denom>0]
                        mean = float(g[col].mean())
                        se = float(draws.std(ddof=1))
                        row[col] = mean
                        row[col+'_ci'] = np.quantile(draws, [.025, .975]).tolist()
                        row[col+'_bonf'] = [mean-z*se, mean+z*se]
                    row['screen14_bps'] = row['gross']*10000-14
                    row['screen20_bps'] = row['gross']*10000-20
                    row['candidate'] = bool(row['n']>=100 and row['days']>=30 and row['lift_bonf'][0]>0 and row['gross_bonf'][0]>.0014)
                else:
                    row['candidate'] = False
                rows.append(row)
    for col in ['phase', 'trend', 'fourdir', 'slot', 'side']:
        table = e.groupby(['tf', 'family', 'signature', col]).agg(n=('win','size'), days=('day','nunique'),
                       win=('win','mean'), lift=('lift','mean'), gross=('gross','mean'))
        table.to_csv(OUT/f'by_{col}.csv', lineterminator='\n')
    e.assign(month=e.time.dt.strftime('%Y-%m')).groupby(['tf','family','signature','month']).agg(
        n=('win','size'), win=('win','mean'), lift=('lift','mean'), gross=('gross','mean')).to_csv(OUT/'by_month.csv', lineterminator='\n')
    e.to_csv(OUT/'events.csv.gz', index=False, compression={'method':'gzip', 'mtime':0}, lineterminator='\n')
    result = dict(data_start=str(a.index[0]), data_end=str(a.index[-1]), bars=len(a), calendar_days=nday,
                  event_rows=len(e), arms=126, candidates=sum(r['candidate'] for r in rows), manifest=manifest, rows=rows,
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  method_sha256=hashlib.sha256((OUT/'METHOD.md').read_bytes()).hexdigest())
    (OUT/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    pd.DataFrame(rows).to_csv(OUT/'TRIAL_REGISTRY.csv', index=False, lineterminator='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['manifest','rows']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch-only', action='store_true')
    args = parser.parse_args()
    if args.fetch_only:
        print(json.dumps(list(ThreadPoolExecutor(max_workers=4).map(fetch, MONTHS)), indent=2))
    else:
        if (OUT/'results.json').exists():
            raise SystemExit('Results exist: log and explicitly archive before another trial')
        raw, manifest = load()
        summarize(make_events(raw), raw, manifest)
