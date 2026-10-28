"""Hermetic demonstrations of observed audit defects; no production writes/network.
Assertions describe the observed current behavior, NOT the desired behavior.
"""
import sys, json, subprocess, tempfile, os, contextlib, io, copy
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
REPO=Path(__file__).resolve().parents[3]
OUT=Path(os.environ.get('MTS_COORD_AUDIT_OUT') or Path(tempfile.gettempdir())/'mts-coordination-audit'); OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO/'scripts/dev'))
import sync, tasks, supervisor as S, mts_signal, wiring_scan, codex_run, run_all_tests as rat
from test_tasks import good

def git(p,*args):
    r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return r.stdout.strip()

def repos(base):
    remote=base/'remote.git';a=base/'a';b=base/'b'
    remote.mkdir(parents=True);git(remote,'init','--bare','-q')
    a.mkdir();git(a,'init','-q');git(a,'config','user.name','Audit');git(a,'config','user.email','audit@example.invalid')
    git(a,'checkout','-qb','fast-track')
    tasks.save(a,good('predecessor',state='ready'))
    tasks.save(a,good('successor',depends_on=['predecessor']))
    git(a,'add','.');git(a,'commit','-qm','fixture');git(a,'remote','add','origin',str(remote));git(a,'push','-qu','origin','fast-track')
    git(base,'clone','-q','--branch','fast-track',str(remote),str(b));git(b,'config','user.name','Audit B');git(b,'config','user.email','audit-b@example.invalid')
    return a,b,remote

results={}
with tempfile.TemporaryDirectory(prefix='repro-',dir=OUT) as td:
    root=Path(td)
    a,b,remote=repos(root/'snap')
    c=tasks.get(b,'predecessor');c['state']='done';tasks.save(b,c)
    git(b,'add','.');git(b,'commit','-qm','predecessor completed');git(b,'push','-q')
    S.fetch_origin(a)
    remote_state=json.loads(git(a,'show','origin/fast-track:MyTradingSys/system/tasks/predecessor.json'))['state']
    snap=S._dispatch_raw(a,datetime.now(timezone.utc),host='JIS-NUC')
    excluded={r['id']:r for r in snap['excluded']}
    assert remote_state=='done' and tasks.get(a,'predecessor')['state']=='ready'
    assert excluded['successor']['reason_code']=='dependency'
    results['fetch_does_not_refresh_dispatch']={'remote_predecessor':remote_state,'dispatch_predecessor':tasks.get(a,'predecessor')['state'],'successor':excluded['successor']}

    a,b,remote=repos(root/'claims')
    orig=sync.git;injected=False;logs=io.StringIO()
    def racing_git(repo,*args,**kw):
        global injected
        if Path(repo)==a and args[:1]==('push',) and args[-1].endswith(':refs/heads/claims') and not injected:
            injected=True
            with patch.dict(os.environ,{'MTS_ACCOUNT':'worker-b'}): sync.claim(b,'same-task',force=True)
        return orig(repo,*args,**kw)
    with contextlib.redirect_stdout(logs),patch.object(sync,'git',racing_git),patch.dict(os.environ,{'MTS_ACCOUNT':'worker-a'}):
        sync.claim(a,'same-task',force=True)
    rows=dict(sync.open_claims(a,fetch=False))
    assert logs.getvalue().count('claimed same-task;')==2
    results['racing_claims_both_succeed']={'success_messages':logs.getvalue().count('claimed same-task;'),'final_owner':rows['same-task']['account'],'log':logs.getvalue()}
    assert 'same-task' in rows and 'same-task' not in tasks.open_claims(a)
    results['tasks_misses_side_claim']={'sync_open_claims':list(rows),'tasks_open_claims':list(tasks.open_claims(a))}

    c=good('already-shipped')
    with patch.object(tasks.TS,'state_tag',return_value='SHIPPED@deadbeef'):
        stop=tasks.stop_tag(c,a)
        snap=tasks.dispatch([c],{},[],{}, {'status':'up'},datetime.now(timezone.utc),'JIS-NUC',a)
    assert stop and snap['dispatch'][0]['id']==c['id']
    results['dispatch_bypasses_stop_tag']={'stop_tag':stop,'dispatched':[r['id'] for r in snap['dispatch']]}

    with patch.object(mts_signal,'last_result',return_value='Result: old successful result'):
        signal=mts_signal.auto_send_text({'hook_event_name':'PostToolUse','tool_name':'Bash','cwd':str(a),'tool_input':{'command':'python scripts/dev/sync.py ship --release failed-task'},'tool_response':{'exit_code':1,'stdout':'offline gate failed; nothing pushed'}})
    assert signal[1]=='done'
    results['failed_ship_emits_done']={'failed_exit_code':1,'signal':signal}

    # The real watcher probe drops on_green and carries neither dispatch nor signals.
    with patch.object(S,'read_shas',return_value={'abc':{'on_trunk':True,'on_green':False}}),patch.object(S,'read_ci',return_value={'red':False}),patch.object(S,'read_gate_slots',return_value={'busy':0,'total':2}):
        before=S._probe_wait_state(a,['abc'])
        with patch.object(S,'read_shas',return_value={'abc':{'on_trunk':True,'on_green':True}}): after=S._probe_wait_state(a,['abc'])
    assert before==after and S._detect_transition(before,after) is None
    rc,reason=S.wait_for_transition(repo=a,shas=['abc'],timeout=3000,interval=300,probe=lambda r,s:after,fetcher=lambda r:None,sleeper=lambda s:None)
    assert rc==3
    results['green_completion_not_watched']={'before':before,'after':after,'virtual_wait_seconds':3000,'return':reason}

    # A freshly added dev tool with no call site still passes the wiring gate.
    toy=root/'wire';(toy/'scripts/dev').mkdir(parents=True)
    (toy/'scripts/dev/uninvoked_feature.py').write_text('def run():\n    return 42\n',encoding='utf-8')
    classified=wiring_scan.classify(toy)
    errs=wiring_scan.check(classified,{})
    assert classified['scripts/dev/uninvoked_feature.py']=='DEV-TOOL' and not errs
    results['uninvoked_tool_passes_wiring']={'classification':classified,'gate_errors':errs,'warnings':wiring_scan.dev_no_reader(toy,*wiring_scan.build(toy))}

    # Gemini passes a full card ID to release, while claims are truncated to 40.
    cid='a-card-name-that-is-deliberately-longer-than-forty-characters'
    with contextlib.redirect_stdout(io.StringIO()): sync.claim(a,cid,force=True)
    try: sync.release(a,cid)
    except sync.SyncError as e: err=str(e)
    else: raise AssertionError('expected release mismatch')
    assert sync.slugify(cid) in dict(sync.open_claims(a,fetch=False))
    results['gemini_full_id_release_mismatch']={'id':cid,'claim_slug':sync.slugify(cid),'release_error':err}

    # CLI observes CI only after ship() has returned and recorded its timing.
    events=[]
    def fake_ship(*args,**kwargs): events.extend(['ship_wall_recorded','push_returned']);return sync.Pushed('abc',['scripts/dev/example.py'])
    with patch.object(sync,'run_host_health'),patch.object(sync,'toplevel_or_none',return_value=a),patch.object(sync,'toplevel',return_value=a),patch.object(sync,'ship',fake_ship),patch.object(sync,'ci_path_filter',return_value=['scripts/**']),patch.object(sync,'wait_own_ci',side_effect=lambda *a,**k:events.append('ci_wait_started') or 'green'),patch.object(sync,'lease_guard',return_value=None),patch.dict(os.environ,{},clear=False):
        os.environ.pop('SYNC_NO_CI_WAIT',None)
        sync.main(['ship'])
    assert events.index('ship_wall_recorded')<events.index('ci_wait_started')
    results['ship_wall_excludes_ci_wait']={'order':events,'CI_wait_cap_seconds':sync.CI_WAIT_S}

    with patch.dict(os.environ,{'MTS_GATE_SLOTS_DIR':str(root/'slots')}):
        with sync.gate_slot(a,name='gate-slots-fast'):
            busy=S.read_gate_slots(a)
            fast=list((root/'slots/gate-slots-fast').glob('slot-*'))
            assert len(fast)==1 and busy['busy']==0
    results['fast_gate_missing_from_supervisor']={'actual_fast_slots_busy':len(fast),'supervisor_busy':busy['busy']}

    # The same return value drives printed PASS and the reusable pass record.
    with patch.object(rat,'STEP_TIMEOUT_S',60),patch.object(rat,'TIMEOUT_DEFERS',True),patch.object(rat.subprocess,'run',side_effect=subprocess.TimeoutExpired(['test'],60)):
        ok,msg=rat.exec_step(['test'])
    step=rat.Step('audit','deferred probe','probe',cmd=['test'])
    assert ok is True
    rat.save_record([step],{step.num:ok},root=b)
    reused=rat.load_reused([step],root=b)
    assert step.num in reused
    results['timeout_cached_as_pass']={'return_ok':ok,'message':msg,'printed':rat.format_step('audit','probe','test',ok,msg,60),'reused':reused}

    predecessor=good('upstream',state='done',result='REPORT.md contains the verified result',context={'reads':['SPEC.md']})
    successor=good('downstream',depends_on=['upstream'])
    brief=tasks.brief(successor)
    worker=S.brief(successor['id'],repo=a,card={**successor,'context':{'reads':['NEEDED.md']},'tests':'ESSENTIAL_TEST','done_when':'ESSENTIAL_ACCEPTANCE'})
    assert 'upstream' not in brief and 'REPORT.md' not in brief
    assert all(x not in worker for x in ['NEEDED.md','ESSENTIAL_TEST','ESSENTIAL_ACCEPTANCE'])
    results['worker_brief_drops_context_contract']={'task_brief_includes_dependency_id':False,'supervisor_brief_includes_context_tests_done_when':False,'supervisor_brief':worker}

(OUT/'reproductions.json').write_text(json.dumps(results,indent=2),encoding='utf-8',newline='\n')
print(json.dumps(results,indent=2))
