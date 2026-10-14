"""Independent raw-row spot checks; no new strategy trial or tuning."""
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
r = json.loads((OUT/'results.json').read_text())
parts = []
for item in r['manifest']:
    assert item['month'] <= '2024-06'
    raw = Path(item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['checksum']
    with zipfile.ZipFile(item['path']) as z:
        with z.open(z.namelist()[0]) as stream:
            b = pd.read_csv(stream, header=None, usecols=list(range(6)))
    b = b[pd.to_numeric(b[0], errors='coerce').notna()].astype(float)
    b.index = pd.to_datetime(b.pop(0).astype('int64'), unit='ms', utc=True)
    b.columns = ['o', 'h', 'l', 'c', 'v']
    parts.append(b)
a = pd.concat(parts)
e = pd.read_csv(OUT/'events.csv.gz')
assert len(e) == r['event_rows']
assert len(r['rows']) == 126
assert sum(x['n'] for x in r['rows']) == len(e)
checked = 0
for _, row in e.sample(min(126, len(e)), random_state=41).iterrows():
    end = pd.Timestamp(row.time)
    start = end-pd.Timedelta(minutes=int(row.tf))
    if row.family == 'week':
        boundary = start.floor('D')-pd.Timedelta(days=start.weekday())
        beginning = boundary-pd.Timedelta(days=7)
    else:
        freq = '4h' if row.family == '4h' else '1D'
        boundary = start.floor(freq)
        beginning = boundary-pd.Timedelta(hours=4 if row.family=='4h' else 24)
    parent = a.loc[(a.index>=beginning)&(a.index<boundary)]
    assert len(parent)==int((boundary-beginning).total_seconds()/60)
    level = parent.h.max() if row.edge=='h' else parent.l.min()
    assert abs(level-row.level)<1e-7
    window = a.loc[(a.index>=start)&(a.index<end)]
    assert len(window)==row.tf
    previous = a.loc[start-pd.Timedelta(minutes=1), 'c']
    previous2 = a.loc[start-pd.Timedelta(minutes=int(row.tf)+1), 'c']
    current = window.c.iloc[-1]
    side = row.side
    x, p, q = side*(current-level), side*(previous-level), side*(previous2-level)
    low, high = window.l.min(), window.h.max()
    wick = low<level if side==1 else high>level
    touch = low<=level if side==1 else high>=level
    checks = dict(rejection=p>0 and wick and x>0,
                  acceptance=q<=0 and p>0 and x>0,
                  reclaim=q>0 and p<0 and x>0,
                  retest=q>0 and p>0 and touch and x>0)
    checks['break'] = p<=0 and x>0
    loc = (current-low if side==1 else high-current)/(high-low) if high>low else 0
    body = abs(current-window.o.iloc[0])/(high-low) if high>low else 0
    checks['strong_break'] = checks['break'] and loc>=.75 and body>=.6
    assert checks[row.signature]
    exit_time = end+pd.Timedelta(minutes=60)
    assert len(a.loc[end:exit_time])==61
    gross = side*(a.loc[exit_time, 'o']/a.loc[end, 'o']-1)
    assert abs(gross-row.gross)<1e-12
    assert row.win==float(gross>0)
    checked += 1
for row in r['rows']:
    g = e[(e.tf==row['tf'])&(e.family==row['family'])&(e.signature==row['signature'])]
    assert len(g)==row['n']
    if len(g):
        assert abs(g.win.mean()-row['win'])<1e-12
        assert abs(g.gross.mean()-row['gross'])<1e-12
print(json.dumps(dict(archive_hashes=len(parts), independently_reconstructed_events=checked,
                     arm_count_checks=126, total_rows=len(e), status='PASS')))
