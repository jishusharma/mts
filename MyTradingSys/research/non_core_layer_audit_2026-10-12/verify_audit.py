"""Read-only audit reproductions; writes evidence only beside this script."""
import collections
import hashlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str) + '\n', encoding='utf-8', newline='\n')

def main():
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_regime
    from MyTradingSys.backtest.layers.rsi.malkan_mtf import state_asof
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    from MyTradingSys.backtest.layers.rsi.run_divergence_mtf import render_report
    results = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    results['rsi_hand_example'] = {'closes': [10,12,11,14,13], 'period':3,
        'expected_seed':100-100/6, 'expected_next':100-100/(1+(10/9)/(5/9)),
        'actual':rsi_core([10,12,11,14,13],3)}
    assert abs(results['rsi_hand_example']['actual'][3]-results['rsi_hand_example']['expected_seed'])<1e-10
    assert abs(results['rsi_hand_example']['actual'][4]-results['rsi_hand_example']['expected_next'])<1e-10
    results['regime_value_mismatch'] = {'input': [65.0]*19+[45.0], 'latest_rsi':45,
        'computed_regime':malkan_regime([65.0]*19+[45.0])[-1],
        'meaning':'BULL is possible with current RSI 45; not equivalent to current RSI >60.'}
    results['state_asof_contract'] = {'open_times':[0], 'value':['BULL'], 'query':1,
        'actual':state_asof([0],['BULL'],1), 'meaning':'No close-time enforcement inside helper; caller must pass availability times.'}
    reg=json.loads((ROOT/'MyTradingSys/backtest/layers/timeframe/registry.json').read_text())
    bars=[dict(t=i*60000,o=100,h=101,l=99,c=100,v=1,tbv=.5) for i in [0,1,3,4]]
    results['gapped_resample']=resample(bars,'5m',reg)
    stats={}
    for name in ['summary.json','summary_T088.json']:
        base=ROOT/'MyTradingSys/research/rsi_divergence_mtf_2026-10-09'
        data=json.loads((base/name).read_text())
        cells=[(tf,col,kind,s) for tf,r in data['tfs'].items() for col,kinds in r['columns'].items() for kind,s in kinds.items()]
        enough=[x for x in cells if x[3]['horizons']['10']['n']>=300]
        report='REPORT.md' if name=='summary.json' else 'REPORT_T088.md'
        stats[name]={'timeframes':len(data['tfs']), 'cells':len(cells), 'verdicts':dict(collections.Counter(x[3]['verdict'] for x in cells)),
            'eligible':len(enough),'eligible_negative_net':sum(x[3]['horizons']['10']['net_mean']<0 for x in enough),
            'report_reproduced_exactly':render_report(data)==(base/report).read_text(encoding='utf-8'),
            'eligible_positive_net':[(a,b,c,s['horizons']['10']) for a,b,c,s in enough if s['horizons']['10']['net_mean']>0]}
    results['summary_recount']=stats
    refs=subprocess.check_output(['git','for-each-ref','--format=%(refname)','refs/heads','refs/remotes'],cwd=ROOT,text=True).splitlines()
    hits={}
    for ref in refs:
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',ref],cwd=ROOT,text=True).splitlines()
        matches=[p for p in paths if p.endswith(('.py','.java','.pine')) and any(s in p.lower() for s in ['wavetrend','squeeze_momentum','better_volume','volume_flow','kurisko'])]
        if matches: hits[ref]=matches
    results['indicator_named_implementation_paths']={'refs_checked':refs,'hits':hits,'limit':'Named paths only; current code text searched separately.'}
    mirror=ROOT/'runtime_data/_mirror'
    manifest=json.loads((mirror/'manifest.json').read_text())
    rows=[json.loads(x) for x in (mirror/'MyTradingSys/execution/auto_trades.jsonl').read_text().splitlines() if x.strip()]
    closed=[x for x in rows if x.get('event')=='trade_closed']
    results['mirror']={'utc':manifest['utc'],'git_head':manifest['git_head'],'rows':len(rows),
        'events':dict(collections.Counter(x.get('event') for x in rows)),
        'closed_by_source':dict(collections.Counter(x.get('source','UNKNOWN') for x in closed)),
        'closed_exit_reasons':dict(collections.Counter(x.get('exit_reason','UNKNOWN') for x in closed)),
        'limitation':'Mirrored auto_trades log, not canonical trade ledger; not live and not deduplicated P/L evidence.'}
    save('reproductions.json',results)
    groups=['rsi','timeframe','cryptocred','positioning','session','turn_of_candle','session_levels','tick','consensus','alerts']
    tests={}
    for group in groups:
        paths=sorted((ROOT/'MyTradingSys/backtest/layers'/group).glob('test_*.py'))
        names=['.'.join(p.relative_to(ROOT).with_suffix('').parts) for p in paths]
        stream=io.StringIO()
        suite=unittest.defaultTestLoader.loadTestsFromNames(names)
        result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
        (OUT/('tests_'+group+'.txt')).write_text(stream.getvalue(),encoding='utf-8',newline='\n')
        tests[group]={'modules':names,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful()}
        print(group,tests[group]['run'],result.wasSuccessful(),flush=True)
    save('test_results.json',tests)
    quote_results={}
    for path in sorted((ROOT/'extracts/processed/malkan').glob('*.md')):
        proc=subprocess.run([sys.executable,'scripts/dev/verify_extract_quotes.py',str(path)],cwd=ROOT,text=True,capture_output=True)
        quote_results[path.name]={'exit_code':proc.returncode,'output':proc.stdout+proc.stderr}
    save('quote_gates.json',quote_results)

if __name__=='__main__':
    main()
