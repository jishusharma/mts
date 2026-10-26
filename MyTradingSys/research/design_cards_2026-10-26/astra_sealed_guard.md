# Simulator desk sealed-window challenge

RESULT (2026-10-26 UTC / 2026-10-27 IST, JIS-NUC), audited HEAD 4cc6e618e: **34 adversarial cases: 27 REFUSED and 7 LEAK paths, plus 4 valid-date controls**. Seven paths are not seven independent defects: cache content is trusted at several boundaries. No real VALIDATION or HOLDOUT bar was read. All bars, cache payloads, ZIP downloads and timestamps used below were synthetic. Production code was unchanged. Trust: UNCHECKED pending independent review; classifications are OURS.

## Threat model and method

Ordinary date-box input cannot select a sealed date. A stale, corrupt or wrongly populated local cache is a separate failure mode: settings/code-hash keys do not establish the dates of the cache contents. Tests deliberately planted synthetic sealed timestamps in temporary caches. A planted payload is a test of validation, not evidence that an existing cache was contaminated. No malicious pickle instructions, credentials, live processes, existing caches, external network or market files were involved.

CUT = 1719792000000 (2024-07-01 00:00 UTC); HOLD = 1751328000000 (2025-07-01 00:00 UTC). Synthetic prices are arbitrary 98..102. Every file written by the probes was under a tempfile.TemporaryDirectory on F:/MTS and removed afterward. SIM_DESK_KLINES was redirected before imports. No study build_cache or real dataset loader was executed. The levels simulator was replaced only with an observation spy to establish which bar timestamps reach its input; the date, cache and idea-routing code was real. Result-cache probes used the real registered RSI normalizer and desk run_setting/statistics, with temporary ledger/cache paths.

Evidence paths below are under `MyTradingSys/research/sim_desk/`: D = desk.py; B = studies/_bars.py; L = studies/levels.py; F = fetch_klines.py; C = conditions.py. Numbers refer to audited source lines.

## Cases and outcomes

| Case / input | Count | Result | Evidence and observation |
|---|---:|---|---|
| Each of krown, levels, rsi, wavetrend: normalize({'end':'2024-07-01'}) | 4 | REFUSED | D:38-49, invoked by each study normalizer. ValueError before cache/market access. |
| Same four studies: end='2025-07-01' | 4 | REFUSED | Same guard; HOLDOUT date refused. |
| Same four: start='2022-03-31' | 4 | REFUSED | Earlier than desk DEV_FIRST, refused. Warm-up data is not selectable as a trade date. |
| Same four: end='2024-06-30T23:59:00' | 4 | REFUSED | Date-only parser refuses datetime suffix; last DEV minute is selected by end='2024-06-30', not a time suffix. |
| Same four: start='2024-06-30', end='2024-06-29' | 4 | REFUSED | Reversed range refused. |
| symbol_of with ../../2025-07, BTCUSDT/../../x, SOLUSDT | 3 | REFUSED | B:47-51 allowlists BTCUSDT/ETHUSDT; traversal and unsupported symbol fail. |
| BTCUSDT vs ETHUSDT normalized RSI result key | 1 | REFUSED | D:225-228 hashes normalized settings; distinct symbols produce distinct keys. This tests cross-symbol cache collision, not contents. |
| load_1m on June .npy containing [CUT-60000,CUT] | 1 | REFUSED | B:79-93 sorts then asserts max < CUT; invalid cold-cache row is loaded into memory but not returned to study. |
| _month('2024-06') on that same .npy | 1 | LEAK L1, component only | B:60-63 returns the CUT row directly. Standard enclosing cold load_1m refuses it, as above. |
| load_1m with pre-populated _ALL['BTCUSDT'] containing CUT | 1 | LEAK L2, requires invalid in-process state | B:83,93 returns hot array without rerunning max check. No ordinary request was shown to populate it this way; its source could be accidental mutation of the shared returned array. |
| run_setting(rsi,{}) with a correctly keyed synthetic result JSON whose touch_t=[CUT,HOLD] | 1 | LEAK L3, result displayed | D:248-255 trusts cached arrays; D:281-295 does not validate content dates. out['trades']['t'] contains both sealed timestamps despite default DEV settings. |
| Same result cache, cond={'side':'long'} | 1 | LEAK L4, same root cause as L3 | D:285-286; C:159-169 filters side without enforcing a global date bound. Both planted timestamps survive. |
| levels._run_month with valid DEV idea.day, but touch_t=CUT and bars[day] containing CUT | 1 | LEAK L5, simulator input | L:198-215 checks idea.day only; synthetic bar at CUT reaches simulate_one spy. The cached key/day and actual bar timestamps are inconsistent but accepted. |
| levels.trade_bars([month,0], valid_DEV_q) on same temp pickle | 1 | LEAK L6, chart/replay input | L:244-250 loads cached ref, resolves bars and returns CUT without date validation. Shares the idea-cache trust boundary with L5. |
| fetch('BTCUSDT') with mocked checksum-valid June ZIP containing CUT | 1 | LEAK L7, ingestion only | F:30-42 verifies bytes/checksum, not record timestamps; writes synthetic sealed row to a DEV-named CSV. No real download. A subsequent normal cold B.load_1m would refuse the row. |
| fetch.months() default list maximum | 1 | REFUSED | F:18-23 default ends 2024-06; no sealed-month URL generated. The payload test replaced only the download and reduced its month list to June. |
| Actual HTTP handler do_POST('/api/run', rsi end='2024-07-01') using BytesIO, no socket | 1 | REFUSED | D:493-516 calls normalizer; returns 400 before cache/study access. |

Four additional controls, one per study, accepted end='2024-06-30' as DEV. The probe output labels these 'REFUSED' in the sense that no sealed date was introduced; they are **positive controls**, excluded from the 34 attack denominator above. Thus its raw count is 38 and its raw non-LEAK label count 31, not 31 rejected attack inputs.

## Failing test sketches for every LEAK

These are desired safety expectations which fail on the current code with the fixture above. The reproducer asserts the actual leakage instead so its complete diagnostic run exits successfully; a zero exit is not proof that the safety expectations passed.

| Leak | Desired expectation / failing test sketch |
|---|---|
| L1 | Seed June .npy with CUT; `assert np.all(_month('2024-06')[:,0] < CUT)` fails. Alternatively expect ValueError before returning those rows. |
| L2 | Seed/mutate `_ALL['BTCUSDT']` with CUT; `assert np.all(load_1m()[:,0] < CUT)` fails. Desired fix must validate/keep immutable trusted memory state. |
| L3 | Seed real RSI key with two synthetic out-of-DEV touch times; `assert max(run_setting(...temp_paths...)['trades']['t']) < CUT` fails. Prefer refusal to silently sanitising an unexplained cache. |
| L4 | Repeat L3 with long side condition; same max-date assertion fails after the condition. A filter is not a cache validator. |
| L5 | Store DEV-tagged idea with CUT bar in temp June pickle; spy records all simulator inputs; `assert all(t < CUT for t in seen)` fails. Validate actual times before simulation, not only idea.day. |
| L6 | Same fixture; `assert all(b['t'] < CUT for b in trade_bars(ref,q)[0])` fails. Chart/replay must share the content check. |
| L7 | Mock valid checksum ZIP with CUT row; after fetch, parse output; `assert max(timestamps) < CUT` fails. Byte integrity alone is not a date guarantee. |

A complete fixture is preserved below for independent rerun. All seven observed LEAK conditions were confirmed using synthetic values; no real sealed-bar read or ordinary UI-only exploit is claimed. B:91 is a Python assert, so it is disabled under -O; that is an additional static concern, not one of the seven executed probes.

## Conditions, source and scope limits

C:131-133 indexes indicator bars closed at or before each decision; C:194-199 uses layer-B events at or before the touch. This was a static review. EMA/ATR and layer-B poisoned-cache variants were not dynamically exercised here. Passing those ordinary causality rules would not validate their source content. Current result cache keys hash settings/code version (D:225-228), not payload timestamps; changing keys does not establish a clean dataset. Fetch symbols are validated at B.symbol_of for study use; the fetch helper itself was not exhaustively tested for path traversal, and no filesystem escape was attempted.

This is not a general network/service security audit. It establishes content-validation gaps under planted cache corruption and clean normal request guards. It makes no decision about keeping, dropping, demoting or parking a trading layer.

## Reproducer

Verification: 7 existing date-lock tests passed; all 23 conditions tests passed with pytest temporary storage redirected to F:/MTS. The first conditions run hit a local C:/Temp permission error during five tmp_path setups (18 tests passed); rerunning with a fresh temporary base resolved all five setup errors. No production fix was needed. A raw SONNET follow-up card, sim-desk-cache-date-validation, carries these findings for implementation/review; this audit's scope is report only.

Copy the Python block to an external temporary script; adjust HERE to the sim_desk folder in a clean checkout. Run with normal Python (not -O) and numpy installed. It creates and removes only its own temporary folder; it uses no credentials or market data.

```python
"""Synthetic-only adversarial probe; all file writes confined to its temporary folder."""
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile
from unittest.mock import patch

HERE = Path('F:/MTS/mts-jis-nuc-queue-batch/MyTradingSys/research/sim_desk')
TEMP = tempfile.TemporaryDirectory(prefix='sealed-audit-', dir='F:/MTS')
T = Path(TEMP.name)
os.environ['SIM_DESK_KLINES'] = str(T/'source')
sys.path.insert(0,str(HERE))
import numpy as np
import desk
import fetch_klines as fetch
import conditions
from studies import levels
from studies import _bars as bars

CUT=1719792000000
HOLD=1751328000000
results=[]
def record(name, result, evidence):
    results.append(dict(name=name, result=result, evidence=evidence))
def refused(name, fn):
    try:
        fn()
    except (ValueError, AssertionError) as e:
        record(name,'REFUSED',str(e))
    else:
        raise AssertionError('expected refusal: '+name)

for sid, s in desk.STUDIES.items():
    for tag, p in [('validation-end',{'end':'2024-07-01'}), ('holdout-end',{'end':'2025-07-01'}),
                   ('pre-dev',{'start':'2022-03-31'}), ('time-suffix',{'end':'2024-06-30T23:59:00'}),
                   ('reversed',{'start':'2024-06-30','end':'2024-06-29'})]:
        refused(sid+'/'+tag, lambda s=s,p=p:s.normalize(p))
    q=s.normalize({'end':'2024-06-30'})
    assert q['end']=='2024-06-30'
    record(sid+'/last-dev-date','REFUSED','Boundary accepted as DEV; no sealed date introduced')
for symbol in ['../../2025-07','BTCUSDT/../../x','SOLUSDT']:
    refused('symbol/'+symbol,lambda symbol=symbol:bars.symbol_of({'symbol':symbol}))
q1=desk.STUDIES['rsi'].normalize({'symbol':'BTCUSDT'})
q2=desk.STUDIES['rsi'].normalize({'symbol':'ETHUSDT'})
assert desk._key(desk.STUDIES['rsi'],q1)!=desk._key(desk.STUDIES['rsi'],q2)
record('symbol/cache-key','REFUSED','BTC and ETH use distinct normalized cache keys')

synthetic=np.array([[CUT-60000,100,101,99,100],[CUT,100,102,98,101]],float)
(T/'bars').mkdir()
np.save(T/'bars/BTCUSDT-1m-2024-06.npy',synthetic)
with patch.object(bars,'BAR_CACHE',T/'bars'), patch.object(bars,'WARMUP_FROM','2024-06'), patch.object(bars,'_ALL',{}):
    refused('cold-bar-cache/sealed-row',lambda:bars.load_1m())
    assert bars._month('2024-06')[-1,0]==CUT
    record('month-loader/direct','LEAK','_month returns synthetic bar at CUT; enclosing load_1m refuses it')
with patch.object(bars,'_ALL',{'BTCUSDT':synthetic}):
    assert bars.load_1m()[-1,0]==CUT
    record('warm-memory-cache','LEAK','pre-populated _ALL is returned without timestamp revalidation; requires corrupted/mutated in-process state')

# Poison result cache only; use actual registered RSI normalizer and desk computations.
s=desk.STUDIES['rsi']
q=s.normalize({})
c=T/'results'; c.mkdir()
day=CUT//86400000
payload=dict(day=[day,day],touch_t=[CUT,HOLD],side=[1,1],net=[.1,-.2],gross=[.2,-.1],fees=[.1,.1],
             filled=[True,True],refs=[None,None],all_days=[day])
(c/f'{s.ID}_{desk._key(s,q)}.json').write_text(json.dumps(payload))
for tag, cond in [('plain',None),('side-condition',{'side':'long'})]:
    out=desk.run_setting(s,{},trials_path=T/f'{tag}.md',cache_dir=c,progress=lambda _:None,cond=cond)
    assert out['cached'] and out['trades']['t']==[CUT,HOLD]
    record('result-cache/'+tag,'LEAK','run_setting reports synthetic VALIDATION/HOLDOUT timestamps under DEV-only settings')

# Persist an idea-cache fixture; observe what reaches simulation, rather than run market logic.
month=CUT-30*86400000
idea=dict(day=day-1,touch_t=CUT,touch_i=0,side=1,E1=True)
blob=dict(ideas=[idea],bars={day-1:np.array([[CUT,100,101,99,100,1,1]],float)})
p=T/'month.pkl'
import pickle
p.write_bytes(pickle.dumps(blob))
seen=[]
def spy(db, idea, q, ctx=None):
    seen.extend(b['t'] for b in db)
    return dict(net_r=0.,gross_r=.1,fees_r=.1,filled_qty=1)
with patch.object(levels,'_month_file',lambda _:p),patch.object(levels,'simulate_one',spy):
    out=levels._run_month((month,levels.normalize({})))
    assert seen==[CUT] and out['touch_t']==[CUT]
    record('levels-idea-cache','LEAK','valid DEV idea.day admits synthetic CUT bar to simulator; cached timestamps not checked')
    db,_,_=levels.trade_bars([month,0],levels.normalize({}))
    assert db[0]['t']==CUT
    record('levels-chart-replay','LEAK','trade_bars returns synthetic CUT bar from cached ref without boundary check')

# No network: stub a checksum-valid ZIP containing a single synthetic post-cut row.
b=io.BytesIO()
with zipfile.ZipFile(b,'w') as z:
    z.writestr('BTCUSDT-1m-2024-06.csv',f'{CUT},100,101,99,100\n')
zdata=b.getvalue()
urls=[]
def fake_get(url):
    urls.append(url)
    return hashlib.sha256(zdata).hexdigest().encode()+b' file.zip' if url.endswith('.CHECKSUM') else zdata
root=T/'fetch';root.mkdir()
with patch.object(fetch,'months',lambda:iter(['2024-06'])),patch.object(fetch,'get',fake_get):
    fetch.fetch('BTCUSDT',root=root)
assert (root/'BTCUSDT-1m-2024-06.csv').read_text().startswith(str(CUT))
record('fetch/payload','LEAK','checksum-valid wrong-date synthetic row written; ingestion-only, cold bar loader separately refuses')
assert max(fetch.months())=='2024-06'
record('fetch/month-selection','REFUSED','default month list ends 2024-06; no sealed-month URL requested')

# HTTP validation path, no server or socket: invoke the real handler with BytesIO.
h=object.__new__(desk.Handler) if hasattr(desk,'Handler') else None
handler_cls=next(v for v in vars(desk).values() if isinstance(v,type) and hasattr(v,'do_POST') and v.__module__=='desk')
h=object.__new__(handler_cls)
request=json.dumps(dict(study='rsi',params={'end':'2024-07-01'})).encode()
h.path='/api/run';h.rfile=io.BytesIO(request);h.headers={'Content-Length':str(len(request))}
replies=[]
h._send=lambda code,body,*args:replies.append((code,body))
h.do_POST()
assert replies[0][0]==400
record('HTTP/run-date','REFUSED','real do_POST returns HTTP 400 before any study/cache read')
print(json.dumps(dict(count=len(results),leaks=sum(r['result']=='LEAK' for r in results),results=results),indent=2))
TEMP.cleanup()

```
