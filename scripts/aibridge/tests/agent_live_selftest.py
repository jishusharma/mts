# Live self-test for the AIBridge agent (v0.7.1). Starts a scratch agent from the src folder next to this tests folder
# (or from --src), on a free local port, with a scratch policy, and drives it over HTTP exactly like the extension does.
#   python tests/agent_live_selftest.py [--src <dir with agent.ps1>] [--port N]  (default: a free port picked per run, so concurrent gates never share one)
# Exit 0 = all checks passed. Windows only (needs powershell.exe).
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import winreg

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]


def _unique_env_name():
    """Registry variable for the fresh-environment check. One name per run: the check writes it under HKCU\\Environment, which every
    process of the user shares, so two selftests at once (concurrent ship gates, or the concurrent pytest) used to delete each other's
    value before the agent read it (FAIL 'registry change is visible without an agent restart')."""
    return 'AIB_SELFTEST_' + os.urandom(6).hex().upper()


if '--print-env-name' in args:   # lets the pytest guard prove two runs never share the name, without starting an agent
    print(_unique_env_name())
    sys.exit(0)

SRC = os.path.normpath(args[args.index('--src') + 1]) if '--src' in args else os.path.normpath(os.path.join(HERE, '..', 'src'))
def _free_port():
    import socket
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


PORT = int(args[args.index('--port') + 1]) if '--port' in args else _free_port()
PATCH = os.path.normpath(os.path.join(HERE, '..', 'policy_patch.json'))
ORIGIN = 'chrome-extension://selftestselftestselftestselftest'
TOKEN = 'selftest' + os.urandom(8).hex()

work = tempfile.mkdtemp(prefix='aibridge_selftest_')
sdir = os.path.join(work, 'src')
os.makedirs(sdir)
for f in ('agent.ps1', 'checks.ps1', 'concurrency.ps1', 'audit.ps1'):
    shutil.copy(os.path.join(SRC, f), sdir)
os.makedirs(os.path.join(work, 'scripts'))
os.makedirs(os.path.join(work, 'tasks'))
shutil.copy(os.path.join(SRC, '..', 'scripts', 'run-task.ps1'), os.path.join(work, 'scripts'))
open(os.path.join(work, 'tasks', 'demo.json'), 'w').write(json.dumps({
    'name': 'demo', 'description': 'selftest', 'params': {'who': None, 'repo': work},
    'steps': [
        {'name': 'hello', 'cmd': 'Write-Output "hi {who}"', 'cwd': '{repo}', 'expect': r'hi \w+'},
        {'name': 'cap', 'cmd': 'Write-Output "WT: abc123"', 'cwd': '{repo}', 'capture': {'wt': r'WT: (\w+)'}},
        {'name': 'use', 'cmd': 'Write-Output "got {wt}"', 'cwd': '{repo}'},
    ]}))
json.dump({'token': TOKEN, 'allowed_origins': [ORIGIN], 'port': PORT, 'bind': '127.0.0.1'}, open(os.path.join(sdir, 'config.json'), 'w'))
pol = {
    'roots': [work, os.environ.get('TEMP', work)],
    'deny_path_regex': [{'re': r"(^|[\\/\s'\"=(,;@])\.secrets(?![A-Za-z0-9_])", 'why': 'secrets directory'}],
    'timeout_soft_s': 60, 'timeout_hard_s': 300, 'max_output_bytes': 262144, 'mode': 'open',
}
pol.update(json.load(open(PATCH, encoding='utf-8')))
json.dump(pol, open(os.path.join(sdir, 'policy.json'), 'w'))

proc = subprocess.Popen(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(sdir, 'agent.ps1')],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
fails = []
n_ok = 0


def http(method, path, body=None, timeout=180):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request('http://127.0.0.1:%d%s' % (PORT, path), data=data, method=method,
                                 headers={'Origin': ORIGIN, 'Content-Type': 'text/plain'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')


def run(cmd, auto=True, http_timeout=180, **kw):
    b = {'cmd': cmd, 'cwd': work, 'token': TOKEN, 'auto': auto}
    b.update(kw)
    return http('POST', '/run', b, timeout=http_timeout)


def check(name, cond, detail=''):
    global n_ok
    if cond:
        n_ok += 1
        print('PASS', name)
    else:
        fails.append(name)
        print('FAIL', name, detail)


try:
    up = False
    for _ in range(60):
        time.sleep(0.5)
        if proc.poll() is not None:
            break
        try:
            up = http('GET', '/ping', timeout=3)[1].get('ok')
            if up:
                break
        except Exception:
            pass
    check('agent starts and answers /ping', up)
    if not up:
        raise SystemExit(1)
    st, p = http('GET', '/ping')
    check('ping reports version host shell', p.get('agent') == '0.7.1' and p.get('host') and p.get('shell_version', '').startswith('5.'), p)

    st, r = run("Write-Output 'one'\nWrite-Output 'two'\nWrite-Output 'three'", rid='r1')
    check('multi-line block: every line runs', st == 200 and r['out'].split() == ['one', 'two', 'three'], r)
    check('receipt: rid echoed, lines counted, sha present', r.get('rid') == 'r1' and r.get('cmd_lines') == 3 and len(r.get('cmd_sha', '')) == 12, r)

    st1, a = run('Write-Output same')
    st2, b = run('Write-Output same')
    check('identical command, identical verdict (deterministic)', st1 == st2 == 200 and a['out'] == b['out'])
    st, r = run('Write-Output fresh1', rid='x1')
    st, r2 = run('Write-Output fresh2', rid='x2')
    check('no cached result: different command gives different output and rid', r['out'].strip() == 'fresh1' and r2['out'].strip() == 'fresh2' and r['rid'] != r2['rid'])

    st, r = run('python --version')
    check('auto-run: python runs without a click', st == 200 and r['exit'] == 0 and r['kind'] == 'program', r)
    st, r = run('git --version; git status --short')
    check('auto-run: git status runs', st == 200, r)
    st, r = run("Set-Content -Path a.txt -Value hello; Get-Content a.txt")
    check('auto-run: a write runs and reads back', st == 200 and r['out'].strip() == 'hello' and r['kind'] == 'write', r)

    st, r = run('Remove-Item -Recurse -Force .\\nothing_here')
    check('auto-run: irreversible form needs a click, named', st == 403 and 'manual_click_required' in r['reason'] and 'Run (click needed)' in r['reason'], r)
    st, r = run('Remove-Item -Recurse -Force .\\nothing_here', auto=False, dry=True)
    check('manual click path passes the check (dry)', st == 200 and r['ok'] is True, r)
    st, r = run('git reset --hard HEAD')
    check('auto-run: git reset --hard needs a click', st == 403 and 'manual_click_required' in r['reason'], r)
    st, r = run('git push --force origin x')
    check('auto-run: force push needs a click', st == 403, r)

    st, r = run('Write-Output (Get-Date).Year; $env:USERNAME')
    check('$env: is allowed', st == 200 and r['exit'] == 0, r)
    st, r = run('Write-Output $env:TEMP')
    check('child TEMP is the bridge run\\tmp folder, not the shared Temp', st == 200 and r['out'].strip().lower().endswith('run\\tmp'), r)
    st, r = run('Get-ChildItem -Path "$env:TEMP" | Select-Object -First 1')
    check('temp folder usable', st == 200 and r['exit'] == 0, r)

    st, r = run('Write-Output a && Write-Output b')
    check('ps7-only && is refused before running, with the fix', st == 403 and 'ps7_only' in r['reason'] and 'shell=pwsh' in r['reason'], r)
    st, r = run("Write-Output 'a && b'")
    check('&& inside a string is fine', st == 200 and r['out'].strip() == 'a && b', r)
    if http('GET', '/ping')[1].get('pwsh'):
        st, r = run('Write-Output a && Write-Output b', shell='pwsh')
        check('shell=pwsh runs PS7 syntax', st == 200 and r['out'].split() == ['a', 'b'], r)

    st, r = run('Write-Output x', cwd=r'C:\Windows')
    check('cwd outside roots refused with a code', st == 403 and 'cwd_outside_roots' in r['reason'], r)
    st, r = run('Get-Content .secrets\\key')
    check('secrets stay denied', st == 403 and 'denied_path' in r['reason'], r)

    # fresh environment: a variable written to the registry AFTER the agent started is visible to the next command
    name = _unique_env_name()
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE)
    try:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, 'fresh42')
        st, r = run('Write-Output $env:' + name)
        check('registry change is visible without an agent restart', st == 200 and r['out'].strip() == 'fresh42', r)
    finally:
        try:
            winreg.DeleteValue(k, name)
        except OSError:
            pass
        winreg.CloseKey(k)

    # parallel chats: a slow command must not block a quick one. Ordering, not wall time: a blocking agent answers quick only after
    # slow ends. A fixed seconds bound tripped under ship-time load (4.4-4.5 s, 2026-10-15) and so did a 6 s sleep (the quick command
    # needs its own PowerShell start, which outlasts 5 s on a starved host), so the slow command now HOLDS until the test releases it
    # after quick has answered: slow is provably still running whatever either latency was.
    started_flag = os.path.join(work, 'slow_started.flag')
    release_flag = os.path.join(work, 'slow_release.flag')
    slow_cmd = ("Set-Content -LiteralPath '%s' -Value 1; $until = (Get-Date).AddSeconds(200); "
                "while (-not (Test-Path -LiteralPath '%s') -and (Get-Date) -lt $until) { Start-Sleep -Milliseconds 200 }; "
                "Write-Output slow" % (started_flag, release_flag))
    res = {}
    t = threading.Thread(target=lambda: res.update(slow=run(slow_cmd, timeout_s=280, http_timeout=300)))   # the reply comes after the release
    t.start()
    st, r, slow_running, quick = 0, {}, False, 0.0
    try:
        wait_until = time.time() + 240   # until the slow command reports it is running (a starved PowerShell start can take a while)
        while not os.path.exists(started_flag) and t.is_alive() and time.time() < wait_until:
            time.sleep(0.2)
        t0 = time.time()
        try:
            st, r = run('Write-Output quick')
        except Exception as e:   # a blocking agent never answers quick while slow holds: report it as this check's failure
            st, r = 0, {'error': repr(e)}
        quick = time.time() - t0
        slow_running = t.is_alive()
    finally:
        open(release_flag, 'w').write('1')
    check('parallel: quick command answers while a slow one runs', st == 200 and slow_running,
          'took %.1fs, slow still running=%s' % (quick, slow_running))
    t.join()
    slow = res.get('slow', (0, {}))
    check('parallel: the slow one still completes', slow[0] == 200 and slow[1].get('out', '').strip() == 'slow', slow)

    st, r = run('', task='list')
    check('task=list shows the playbook', st == 200 and 'demo:' in r['out'] and 'who=<required>' in r['out'], r)
    st, r = run('', task='demo', task_params={'who': 'dsa'})
    check('task: whole playbook in one call, params filled', st == 200 and r['exit'] == 0 and 'TASK RESULT: PASS 3 steps' in r['out'] and 'hi dsa' in r['out'], r)
    check('task: capture feeds a later step', st == 200 and 'got abc123' in r['out'], r)
    st, r = run('', task='demo')
    check('task: missing parameter is named', 'missing parameter(s): who' in r['out'], r)
    st, r = run('', task='nope')
    check('task: unknown playbook says so', 'unknown task' in r['out'], r)
    plan = {'steps': [{'name': 'a', 'cmd': 'Write-Output ok-a', 'cwd': work}, {'name': 'b', 'cmd': 'exit 3', 'cwd': work},
                      {'name': 'c', 'cmd': 'Write-Output never', 'cwd': work}, ]}
    st, r = run('', task='inline', task_spec=json.dumps(plan))
    check('task inline: stops at the failing step, later steps SKIP', r['exit'] == 1 and 'FAIL  b' in r['out'] and 'SKIP  c' in r['out'] and 'never' not in r['out'].replace('SKIP', ''), r)
    plan['steps'][1] = {'name': 'b', 'cmd': 'exit 3', 'cwd': work, 'on_fail': 'continue'}
    st, r = run('', task='inline', task_spec=json.dumps(plan))
    check('task inline: on_fail=continue keeps going', 'PASS  c' in r['out'] and 'FAIL  b' in r['out'], r)
    bad = {'steps': [{'name': 'x', 'cmd': 'git reset --hard HEAD', 'cwd': work}]}
    st, r = run('', task='inline', task_spec=json.dumps(bad))
    check('task inline: an irreversible step is refused up front, naming the step', st == 403 and 'task step 1' in r['reason'] and 'manual_click_required' in r['reason'], r)
    st, r = run('', task='inline', task_spec='not json')
    check('task inline: bad plan refused with a code', st == 403 and 'bad_task_spec' in r['reason'], r)
    st, r = run('', task='demo', task_params={'who': 'x'}, dry=True)
    check('task dry run', st == 200 and r['ok'] is True and r['kind'] == 'task', r)
    left = [f for f in os.listdir(os.path.join(sdir, 'run')) if f.startswith('task_')] if os.path.isdir(os.path.join(sdir, 'run')) else []
    check('task spec files are cleaned up', not left, left)

    st, r = run('Start-Sleep -Seconds 20', timeout_s=2)
    check('timeout kills and reports', st == 200 and r['timed_out'] is True, r)
finally:
    proc.kill()
    try:
        subprocess.call(['taskkill', '/T', '/F', '/PID', str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    shutil.rmtree(work, ignore_errors=True)

print('%d passed, %d failed' % (n_ok, len(fails)))
sys.exit(1 if fails else 0)
