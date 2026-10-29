"""Per-finding re-check of coordination_audit_20261026/reproduce.py on the current tree.

reproduce.py stops at the first fixture that no longer shows its defect; this runner isolates each of the
12 fixtures (same code, same assertions, which describe the DEFECT, not the desired behaviour) so one fixed
finding does not hide the others. Status per key: REPRODUCED (defect still present), NOT_REPRODUCED (the
defect assertion failed: fixed or changed), ERROR (fixture no longer runs; message kept).
Hermetic: temp git repos only, no network, no production writes. Output dir: MTS_COORD_AUDIT_OUT or %TEMP%.
"""
import sys, json, subprocess, tempfile, os, contextlib, io, traceback
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
OUT = Path(os.environ.get('MTS_COORD_AUDIT_OUT') or Path(tempfile.gettempdir()) / 'mts-coordination-recheck')
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO / 'scripts/dev'))
import sync, tasks, supervisor as S, mts_signal, wiring_scan, run_all_tests as rat  # noqa: E402
from test_tasks import good  # noqa: E402


def git(p, *args):
    r = subprocess.run(['git', '-C', str(p), *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


def repos(base):
    remote = base / 'remote.git'; a = base / 'a'; b = base / 'b'
    remote.mkdir(parents=True); git(remote, 'init', '--bare', '-q')
    a.mkdir(); git(a, 'init', '-q'); git(a, 'config', 'user.name', 'Audit'); git(a, 'config', 'user.email', 'audit@example.invalid')
    git(a, 'checkout', '-qb', 'fast-track')
    tasks.save(a, good('predecessor', state='ready'))
    tasks.save(a, good('successor', depends_on=['predecessor']))
    git(a, 'add', '.'); git(a, 'commit', '-qm', 'fixture'); git(a, 'remote', 'add', 'origin', str(remote)); git(a, 'push', '-qu', 'origin', 'fast-track')
    git(base, 'clone', '-q', '--branch', 'fast-track', str(remote), str(b)); git(b, 'config', 'user.name', 'Audit B'); git(b, 'config', 'user.email', 'audit-b@example.invalid')
    return a, b, remote


def f_fetch_does_not_refresh_dispatch(root):
    a, b, _ = repos(root / 'snap')
    c = tasks.get(b, 'predecessor'); c['state'] = 'done'; tasks.save(b, c)
    git(b, 'add', '.'); git(b, 'commit', '-qm', 'predecessor completed'); git(b, 'push', '-q')
    S.fetch_origin(a)
    remote_state = json.loads(git(a, 'show', 'origin/fast-track:MyTradingSys/system/tasks/predecessor.json'))['state']
    snap = S._dispatch_raw(a, datetime.now(timezone.utc), host='JIS-NUC')
    excluded = {r['id']: r for r in snap['excluded']}
    assert remote_state == 'done' and tasks.get(a, 'predecessor')['state'] == 'ready'
    assert excluded.get('successor', {}).get('reason_code') == 'dependency', f"successor not excluded by dependency; dispatch={[r['id'] for r in snap.get('dispatch', [])]}"
    return {'remote_predecessor': remote_state, 'successor': excluded['successor']}


def _race(root, key):
    a, b, _ = repos(root / key)
    orig = sync.git; injected = []; logs = io.StringIO()

    def racing_git(repo, *args, **kw):
        if Path(repo) == a and args[:1] == ('push',) and args[-1].endswith(':refs/heads/claims') and not injected:
            injected.append(1)
            with patch.dict(os.environ, {'MTS_ACCOUNT': 'worker-b'}):
                sync.claim(b, 'same-task', force=True)
        return orig(repo, *args, **kw)
    err = None
    with contextlib.redirect_stdout(logs), patch.object(sync, 'git', racing_git), patch.dict(os.environ, {'MTS_ACCOUNT': 'worker-a'}):
        try:
            sync.claim(a, 'same-task', force=True)
        except sync.SyncError as e:
            err = str(e)
    return a, logs.getvalue(), err


def f_racing_claims_both_succeed(root):
    a, log, err = _race(root, 'claims')
    rows = dict(sync.open_claims(a, fetch=False))
    assert log.count('claimed same-task;') == 2, f'success messages={log.count("claimed same-task;")} err={err}'
    return {'success_messages': log.count('claimed same-task;'), 'final_owner': rows['same-task']['account'], 'log': log}


def f_tasks_misses_side_claim(root):
    a, b, _ = repos(root / 'side')
    with contextlib.redirect_stdout(io.StringIO()), patch.dict(os.environ, {'MTS_ACCOUNT': 'worker-a'}):
        sync.claim(a, 'same-task', force=True)
    rows = dict(sync.open_claims(a, fetch=False))
    assert 'same-task' in rows and 'same-task' not in tasks.open_claims(a), f'tasks.open_claims={list(tasks.open_claims(a))}'
    return {'sync_open_claims': list(rows), 'tasks_open_claims': list(tasks.open_claims(a))}


def f_dispatch_bypasses_stop_tag(root):
    a, b, _ = repos(root / 'stop')
    c = good('already-shipped')
    with patch.object(tasks.TS, 'state_tag', return_value='SHIPPED@deadbeef'):
        stop = tasks.stop_tag(c, a)
        snap = tasks.dispatch([c], {}, [], {}, {'status': 'up'}, datetime.now(timezone.utc), 'JIS-NUC', a)
    assert stop and snap['dispatch'] and snap['dispatch'][0]['id'] == c['id'], f'dispatch={snap["dispatch"]} excluded={snap.get("excluded")}'
    return {'stop_tag': stop, 'dispatched': [r['id'] for r in snap['dispatch']]}


def f_failed_ship_emits_done(root):
    with patch.object(mts_signal, 'last_result', return_value='Result: old successful result'):
        signal = mts_signal.auto_send_text({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash', 'cwd': str(root),
                                            'tool_input': {'command': 'python scripts/dev/sync.py ship --release failed-task'},
                                            'tool_response': {'exit_code': 1, 'stdout': 'offline gate failed; nothing pushed'}})
    assert signal and signal[1] == 'done', f'signal={signal}'
    return {'failed_exit_code': 1, 'signal': signal}


def f_green_completion_not_watched(root):
    a = root
    with patch.object(S, 'read_shas', return_value={'abc': {'on_trunk': True, 'on_green': False}}), \
            patch.object(S, 'read_ci', return_value={'red': False}), \
            patch.object(S, 'read_gate_slots', return_value={'busy': 0, 'total': 2}):
        before = S._probe_wait_state(a, ['abc'])
        with patch.object(S, 'read_shas', return_value={'abc': {'on_trunk': True, 'on_green': True}}):
            after = S._probe_wait_state(a, ['abc'])
    assert before == after and S._detect_transition(before, after) is None
    rc, reason = S.wait_for_transition(repo=a, shas=['abc'], timeout=3000, interval=300, probe=lambda r, s: after,
                                       fetcher=lambda r: None, sleeper=lambda s: None)
    assert rc == 3
    return {'before': before, 'after': after, 'return': reason}


def f_uninvoked_tool_passes_wiring(root):
    toy = root / 'wire'; (toy / 'scripts/dev').mkdir(parents=True)
    (toy / 'scripts/dev/uninvoked_feature.py').write_text('def run():\n    return 42\n', encoding='utf-8')
    classified = wiring_scan.classify(toy)
    errs = wiring_scan.check(classified, {})
    assert classified['scripts/dev/uninvoked_feature.py'] == 'DEV-TOOL' and not errs
    return {'classification': classified, 'gate_errors': errs}


def f_gemini_full_id_release_mismatch(root):
    a, b, _ = repos(root / 'gq')
    cid = 'a-card-name-that-is-deliberately-longer-than-forty-characters'
    with contextlib.redirect_stdout(io.StringIO()):
        sync.claim(a, cid, force=True)
    import gemini_queue
    src = Path(gemini_queue.__file__).read_text(encoding='utf-8')
    # the defect is the caller passing the full id; sync.release itself is slug-keyed
    calls_full = "'release', card" in src or '"release", card' in src
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sync.release(a, cid)
        err = None
    except sync.SyncError as e:
        err = str(e)
    assert err is not None and calls_full, f'release(full id) err={err} gemini_queue passes full id={calls_full}'
    return {'id': cid, 'claim_slug': sync.slugify(cid), 'release_error': err, 'gemini_queue_passes_full_id': calls_full}


def f_ship_wall_excludes_ci_wait(root):
    a = root
    events = []

    def fake_ship(*args, **kwargs):
        events.extend(['ship_wall_recorded', 'push_returned']); return sync.Pushed('abc', ['scripts/dev/example.py'])
    with patch.object(sync, 'run_host_health'), patch.object(sync, 'toplevel_or_none', return_value=a), \
            patch.object(sync, 'toplevel', return_value=a), patch.object(sync, 'ship', fake_ship), \
            patch.object(sync, 'ci_path_filter', return_value=['scripts/**']), \
            patch.object(sync, 'wait_own_ci', side_effect=lambda *x, **k: events.append('ci_wait_started') or 'green'), \
            patch.object(sync, 'lease_guard', return_value=None), patch.dict(os.environ, {}, clear=False):
        os.environ.pop('SYNC_NO_CI_WAIT', None)
        with contextlib.redirect_stdout(io.StringIO()):
            sync.main(['ship'])
    assert events.index('ship_wall_recorded') < events.index('ci_wait_started')
    return {'order': events, 'CI_wait_cap_seconds': sync.CI_WAIT_S}


def f_fast_gate_missing_from_supervisor(root):
    a = root
    with patch.dict(os.environ, {'MTS_GATE_SLOTS_DIR': str(root / 'slots')}):
        with sync.gate_slot(a, name='gate-slots-fast'):
            busy = S.read_gate_slots(a)
            fast = list((root / 'slots/gate-slots-fast').glob('slot-*'))
            assert len(fast) == 1 and busy['busy'] == 0, f'fast={len(fast)} busy={busy}'
    return {'actual_fast_slots_busy': len(fast), 'supervisor_busy': busy['busy']}


def f_timeout_cached_as_pass(root):
    _, b, _ = repos(root / 'rec')   # the pass record lives in the git dir: needs a real clean clone
    with patch.object(rat, 'STEP_TIMEOUT_S', 60), patch.object(rat, 'TIMEOUT_DEFERS', True), \
            patch.object(rat.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['test'], 60)):
        ok, msg = rat.exec_step(['test'])
    step = rat.Step('audit', 'deferred probe', 'probe', cmd=['test'])
    assert ok is True
    rat.save_record([step], {step.num: ok}, root=b)
    reused = rat.load_reused([step], root=b)
    assert step.num in reused
    return {'return_ok': ok, 'message': msg, 'reused': reused}


def f_worker_brief_drops_context_contract(root):
    a = root
    successor = good('downstream', depends_on=['upstream'])
    brief = tasks.brief(successor)
    worker = S.brief(successor['id'], repo=a, card={**successor, 'context': {'reads': ['NEEDED.md']},
                                                    'tests': 'ESSENTIAL_TEST', 'done_when': 'ESSENTIAL_ACCEPTANCE'})
    assert 'upstream' not in brief
    assert all(x not in worker for x in ['NEEDED.md', 'ESSENTIAL_TEST', 'ESSENTIAL_ACCEPTANCE'])
    return {'task_brief_includes_dependency_id': False, 'supervisor_brief_includes_context_tests_done_when': False}


FIXTURES = [f_fetch_does_not_refresh_dispatch, f_racing_claims_both_succeed, f_tasks_misses_side_claim,
            f_dispatch_bypasses_stop_tag, f_failed_ship_emits_done, f_green_completion_not_watched,
            f_uninvoked_tool_passes_wiring, f_gemini_full_id_release_mismatch, f_ship_wall_excludes_ci_wait,
            f_fast_gate_missing_from_supervisor, f_timeout_cached_as_pass, f_worker_brief_drops_context_contract]


def main():
    results = {}
    for f in FIXTURES:
        key = f.__name__[2:]
        with tempfile.TemporaryDirectory(prefix='recheck-', dir=OUT) as td:
            try:
                results[key] = {'status': 'REPRODUCED', 'evidence': f(Path(td))}
            except AssertionError as e:
                results[key] = {'status': 'NOT_REPRODUCED', 'detail': str(e)}
            except Exception as e:  # fixture drift: keep the message, never count it as fixed
                results[key] = {'status': 'ERROR', 'detail': f'{type(e).__name__}: {e}', 'trace': traceback.format_exc()[-600:]}
    head = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    out = {'head': head, 'results': results,
           'counts': {s: sum(1 for r in results.values() if r['status'] == s) for s in ('REPRODUCED', 'NOT_REPRODUCED', 'ERROR')}}
    (OUT / 'recheck.json').write_text(json.dumps(out, indent=2, default=str), encoding='utf-8', newline='\n')
    print(json.dumps(out, indent=2, default=str))


if __name__ == '__main__':
    main()
