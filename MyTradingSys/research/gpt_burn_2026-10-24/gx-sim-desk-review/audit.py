"""Offline audit probes. No source edits, network, real data, or repo caches.

Run from repo root: python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/audit.py
Expectations are derived from FORMULAS.md sections 8, 9, 13, 18.5, 20.2.
Fill-path choices not specified there are explicitly labelled OURS in report.md.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import math
import re
import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / 'MyTradingSys/research/sim_desk'))
import desk
import charts
import fetch_klines

studies = desk.STUDIES
b = studies['wavetrend']._bars
levels = studies['levels']
MIN = 60000
BASE = b.day_ms('2022-04-01')
checks = []


def record(name, actual, expected, **detail):
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        matched = math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-10)
    else:
        matched = actual == expected
    checks.append(dict(name=name, actual=actual, expected=expected, matched=matched, **detail))


def bars(rows, base=BASE):
    return np.array([[base + k * MIN, *r] for k, r in enumerate(rows)], float)


def trade(a, side=1, trig=None, stop=98, target=102, start=None, window=None, exit_at=None, hold=None, taker=.0005, maker=.0002):
    start = int(a[0, 0]) if start is None else start
    window = int(a[-1, 0] + MIN) if window is None else window
    hold = int(a[-1, 0] + MIN) if hold is None else hold
    return b.run_trade(a, side, start, trig, stop, target, window, exit_at, hold, taker, maker)


# FORMULAS 18.5: both-side fees on actual leg prices, all-taker canonical example.
a = bars([(100, 101, 99, 100), (100, 103, 99, 102), (102, 103, 101, 102)])
r = trade(a, maker=.0005)
record('canonical_long_target_fees', r['net_r'], (2 - .0005*100 - .0005*102)/2)
r = trade(a, side=-1, stop=102, target=98)
record('short_stop_both_fees', r['net_r'], (-2 - .0005*100 - .0005*102)/2)
a = bars([(100, 101, 99, 100), (100, 103, 97, 100), (100, 101, 99, 100)])
r = trade(a)
record('both_hit_stop_first', r['net_r'], (-2-.0005*100-.0005*98)/2)
a = bars([(100, 101, 99, 100), (95, 96, 94, 95), (95, 96, 94, 95)])
r = trade(a)
record('shared_gap_stop', r['net_r'], (-5-.0005*100-.0005*95)/2)
a = bars([(100, 101, 99, 100), (100, 101, 99, 100), (100, 103, 99, 102)])
r = trade(a, trig=102, window=BASE+2*MIN)
record('entry_window_end_exclusive', r['filled'], False)
r = trade(a, target=None, hold=BASE+2*MIN)
record('hold_boundary_excludes_next_bar', r['exit'][1], 100)
record('UTC_epoch_day', b.day_ms('2022-04-01'), 1648771200000)
record('DEV_end_rejected', None, None)
try:
    desk.check_dates('2024-06-30', '2024-07-01')
    checks[-1]['actual'] = 'accepted'
    checks[-1]['matched'] = False
except ValueError:
    checks[-1].update(actual='rejected', expected='rejected', matched=True)

# A market entry at the open precedes the entire intrabar path: no touch ambiguity.
a = bars([(100, 103, 99, 102), (102, 102, 97, 98), (98, 99, 97, 98)])
r = trade(a)
record('market_entry_target_on_fill_bar', r['net_r'], (2-.0005*100-.0002*102)/2, exit=r['exit'])

# An opening price before a later breakout cannot be an exit after that breakout.
a = bars([(90, 105, 89, 104), (104, 105, 103, 104)])
r = trade(a, trig=100, stop=95, target=110, taker=0, maker=0)
record('breakout_fill_bar_pre_entry_open_as_stop', r['exit'][1], 95, entry=r['entry'], net_r=r['net_r'])

# Closed-bar indicator exit vs the first executable next-bar open (OURS causal execution).
a = bars([(100, 101, 99, 100), (100, 102, 99, 101), (90, 91, 89, 90), (90, 91, 89, 90)])
r = trade(a, stop=80, target=None, exit_at=BASE+2*MIN)
record('signal_exit_at_already_closed_price', r['net_r'], (-10-.0005*100-.0005*90)/20, exit=r['exit'])

# Canonical UTC aggregation: no partial trailing higher-timeframe bucket (s8).
a = bars([(100, 101, 99, 100)] * 61)
agg = b.resample(a, 60)
record('partial_trailing_bucket', len(agg), 1)
# A missing minute is silently hidden by aggregation; record as a scope limitation.
agg_gap = b.resample(np.delete(a[:60], 30, axis=0), 60)
record('missing_minute_emits_ordinary_hour', len(agg_gap), 1, rows_present=59, gap_flag_available=False)

# Exercise the actual WaveTrend adapter. Only detector output is injected; real
# resampling, make(), collect(), run_trade(), normalization and fees are executed.
a = bars([(100, 101, 99, 100)] * 300)
a[0, 3] = 90
a[180:, 1:] = [110, 116, 109, 110]
wt = studies['wavetrend']
rows = [SimpleNamespace(event=0, wt1=0, wt2=0) for _ in range(5)]
rows[2] = SimpleNamespace(event=1, wt1=-61, wt2=-62)
q = wt.normalize({'tf': '1h', 'target_r': 1.5, 'maker_pct': 0, 'taker_pct': 0, 'start': '2022-04-01', 'end': '2022-04-01'})
with patch.object(wt._bars, 'load_1m', return_value=a), patch.object(wt.wt, 'compute', return_value=rows):
    res = wt.run(q, progress=lambda _: None)
ref = res['refs'][0]
record('WT_target_uses_actual_fill_risk', ref[4], 110 + 1.5*(110-90), actual_net=float(res['net'][0]), actual_fill=110, signal_close=100)
record('WT_signal_to_fill_boundary', ref[1], BASE+180*MIN)

# RSI breakout gap: same target error through a different adapter.
rsi_study = studies['rsi']
qr = rsi_study.normalize({'tf':'1h','entry':'BREAK','exit':'R','target_r':2,
                          'maker_pct':0,'taker_pct':0,'start':'2022-04-01','end':'2022-04-01'})
hourly = b.resample(a, 60)
hourly[2, 2:5] = [100, 90, 99]
signals = [dict(t=int(hourly[2,0]), side='long')]
a[181,2] = 121
with patch.object(rsi_study._bars, 'load_1m', return_value=a), patch.object(rsi_study, '_signals', return_value=(hourly,[None]*5,signals)):
    rr = rsi_study.run(qr, progress=lambda _: None)
record('RSI_gap_target_uses_actual_fill_risk', rr['refs'][0][4], 110+2*(110-90), actual_fill=110)


def daybars(rows):
    return [dict(t=int(x[0]), o=x[1], h=x[2], l=x[3], c=x[4], v=1., tbv=.5) for x in bars(rows)]


idea = dict(side=1, L1=100., L2=98., T1=110., T2=120., atr1h=2., touch_i=0)
q = levels.normalize({'entry': 'E0', 'scale': 'S0', 'stop': 'K2', 'exit': 'X1', 'maker_pct': 0, 'taker_pct': 0})
db = daybars([(101, 102, 99, 100), (95, 96, 94, 95), (95, 96, 94, 95)])
r = levels.simulate_one(db, idea, q)
risk = 100 - 98*(1-.001)
record('levels_gap_stop_fills_trigger', r['net_r'], (95-100)/risk, actual_exit=r['exits'][0][0], expected_exit=95)

# Prefix invariance: changing only the touch bar's post-entry low changes K5.
q5 = dict(q, stop='K5')
idea5 = dict(idea, touch_i=1)
db1 = daybars([(105, 106, 99, 105), (105, 106, 99.5, 100), (100, 101, 99.5, 100)])
db2 = daybars([(105, 106, 99, 105), (105, 106, 90, 100), (100, 101, 99.5, 100)])
r1 = levels.simulate_one(db1, idea5, q5)
r2 = levels.simulate_one(db2, idea5, q5)
record('K5_uses_post_entry_touch_low', r2['stop'], 99*(1-.001), baseline_stop=r1['stop'], net_r=r2['net_r'])

# Fee and quantity conservation with only one of the planned half-size legs filled.
qh = dict(q, scale='S1', maker_pct=.02, taker_pct=.05)
db = daybars([(101, 102, 99, 100), (100, 111, 99, 110), (110, 111, 109, 110)])
r = levels.simulate_one(db, idea, qh)
risk_half = (100*.5+98*.5)-98*(1-.001)
record('levels_partial_size_net', r['net_r'], (.5*(110-100)-.0002*100*.5-.0002*110*.5)/risk_half, filled_qty=r['filled_qty'])

# Costs scope: same flat trade across the FORMULAS 13 funding timestamps.
a = bars([(100, 100, 100, 100)] * 962)
r = trade(a, stop=98, target=None, exit_at=BASE+960*MIN, taker=.0005)
record('funding_absent_long', r['net_r'], (-.0005*100-.0005*100-100*(.0001+.0003))/2)
rs = trade(a, side=-1, stop=102, target=None, exit_at=BASE+960*MIN, taker=.0005)
record('funding_absent_short', rs['net_r'], (-.0005*100-.0005*100+100*(.0001+.0003))/2)
record('slippage_absent', r['net_r'], (-.0005*100-.0005*100-.0002*100)/2)

# Clipped candle windows lose timestamp keys; markers retain the unclipped origin.
db = daybars([(100, 101, 99, 100)]*11)
tr = dict(bars=db, side=1, level=100, entries=[(BASE,100)], stop=98, target=102,
          exits=[(BASE+10*MIN,100,'HOLD')], net_r=-.05)
svg = charts.svg(tr)
cx = float(re.search(r'<circle cx="([^"]+)"', svg).group(1))
record('chart_entry_at_day_open', cx, 50., SVG_width=300)

# Fetcher does not read/revalidate any existing CSV; network deliberately mocked.
with patch.object(Path, 'exists', return_value=True), patch.object(fetch_klines, 'get') as get:
    fetch_klines.fetch('ETHUSDT', root=REPO / 'MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review')
    record('existing_fetch_files_network_calls', get.call_count, 0, months=len(list(fetch_klines.months())))

# Full desk orchestration with synthetic in-memory bars and redirected artifacts.
# TemporaryDirectory is inside the only authorized directory and is removed.
from tempfile import TemporaryDirectory
with TemporaryDirectory(prefix='offline_', dir=Path(__file__).parent) as tmp:
    a = bars([(100,101,99,100)]*300)
    a[0,3] = 90
    a[180:,1:] = [110,116,109,110]
    with patch.object(wt._bars, 'load_1m', return_value=a), patch.object(wt.wt, 'compute', return_value=rows):
        out = desk.run_setting(
            wt, {'tf':'1h','target_r':1.5,'maker_pct':0,'taker_pct':0,'start':'2022-04-01','end':'2022-04-01'},
            trials_path=Path(tmp)/'TRIALS.md', cache_dir=Path(tmp)/'results', progress=lambda _: None, charts=True)
    record('desk_offline_run_n', out['n'], 1, charts=len(out['charts']), mean=out['mean'], verdict=out['verdict'])

for check in checks:
    print(json.dumps(check, default=lambda x: x.item() if isinstance(x,np.generic) else str(x), sort_keys=True))
print(json.dumps(dict(total=len(checks), matched=sum(x['matched'] for x in checks), mismatched=sum(not x['matched'] for x in checks))))
