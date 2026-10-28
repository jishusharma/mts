"""aibridge_verify.py - is the DSA bridge (AIBridge) on THIS machine complete and working? One command, exit 0 = all PASS.

  python scripts/dev/aibridge_verify.py [F:/AIBridge] [--json] [--no-roundtrip]

Rows (PASS / FAIL / NOT_CHECKED, evidence on each line):
  installed        root has src/agent.ps1, config.json, extension/manifest.json
  file:<name>      each payload file (scripts/aibridge) is byte-equal to the installed one (LF-normalised; background.js with the
                   machine's TOKEN / AGENT_CWD / AGENT_URL masked). Covers every shipped fix at once.
  fix:<name>       a marker line of each shipped fix is present in the installed file (the list FIXES below, commit shown)
  agent_ping       GET /ping answers with the payload agent version
  roundtrip        POST /run (token + extension origin) runs `Write-Output <nonce>` and the output comes back
  autostart        informational: scheduled task AIBridge-Agent exists (NOT a FAIL when absent: SCHEDULING_POLICY.md)
  extension_loaded a Chrome profile has the unpacked extension from <root>/extension and its id equals config.allowed_origins
Fix with:  python scripts/dev/aibridge_install.py <root> --fresh|--restart-agent  (then reload the extension, F5 the chat).
This script reads config.json for the token to make the round trip; it never prints the token.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.normpath(os.path.join(HERE, '..', 'aibridge'))
BS = chr(92)

# (fix name, commit, installed file, marker) - markers are lines the fix put in the payload.
FIXES = [
    ('v0.7.0 fluent auto-run, task mode, parallel chats', 'af9f3446a', 'src/concurrency.ps1', 'function Test-ConnectionSlot'),
    ('keep-alive: tab not discarded, worker heartbeat', '2c73ba9fe', 'extension/background.js', 'automatic discarding'),
    ('v0.7.1 hands-free stays armed after a post', '3270e7423', 'extension/loop.js', 'L.postLanded = function (before, now)'),
    ('agent version constant (matches extension)', '3ba37319b', 'src/agent.ps1', "$AgentVersion = '"),
    ('B196 post gate keeps operator draft, auto-off banner', '8fb185ac0', 'extension/loop.js', 'L.postGate = function'),
    ('B196 stop notice banner', '8fb185ac0', 'extension/loop.js', 'L.stopNotice = function'),
    ('policy: fluent auto_mode', 'af9f3446a', 'src/policy.json', '"auto_mode": "fluent"'),
]


def lf(b):
    return b.replace(b'\r\n', b'\n')


def rd(p):
    with open(p, 'rb') as f:
        return f.read()


def payload_files():
    out = []
    for base, _, names in os.walk(PAYLOAD):
        for n in names:
            rel = os.path.relpath(os.path.join(base, n), PAYLOAD).replace(BS, '/')
            if rel.startswith('tests/') or rel == 'policy_patch.json':
                continue
            out.append(rel)
    return sorted(out)


def mask_bg(b):
    s = b.decode('utf-8', 'replace')
    s = re.sub(r"const TOKEN = '[^']*';", "const TOKEN = 'X';", s)
    s = re.sub(r"const AGENT_CWD = '.*';", "const AGENT_CWD = 'X';", s)
    s = re.sub(r"const AGENT_URL = '.*';", "const AGENT_URL = 'X';", s)
    return s.encode('utf-8')


def ext_id_for_path(path):
    h = hashlib.sha256(os.path.normpath(path).replace('/', BS).encode('utf-16-le')).hexdigest()[:32]
    return ''.join(chr(ord('a') + int(c, 16)) for c in h)


def http(method, url, origin, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={'Origin': origin, 'Content-Type': 'text/plain'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode() or '{}')


def check(root, roundtrip=True):
    rows = []

    def add(name, status, ev):
        rows.append({'check': name, 'status': status, 'evidence': ev})

    cfgp = os.path.join(root, 'src', 'config.json')
    need = [os.path.join(root, x) for x in ('src/agent.ps1', 'src/config.json', 'extension/manifest.json')]
    missing = [n for n in need if not os.path.exists(n)]
    if missing:
        add('installed', 'FAIL', 'missing ' + ', '.join(os.path.basename(m) for m in missing) + ' under ' + root +
            ' -> python scripts/dev/aibridge_install.py ' + root + ' --fresh --restart-agent')
        return rows
    add('installed', 'PASS', root)
    cfg = json.loads(rd(cfgp).decode('utf-8').lstrip('\ufeff'))
    for rel in payload_files():
        src, dst = os.path.join(PAYLOAD, rel), os.path.join(root, rel)
        if not os.path.exists(dst):
            add('file:' + rel, 'FAIL', 'not installed')
            continue
        a, b = lf(rd(src)), lf(rd(dst))
        if rel == 'extension/background.js':
            a, b = mask_bg(a), mask_bg(b)
        ok = a == b
        add('file:' + rel, 'PASS' if ok else 'FAIL', 'identical to payload' if ok else 'differs from payload (old version)')
    for name, commit, rel, marker in FIXES:
        dst = os.path.join(root, rel)
        if not os.path.exists(dst):
            add('fix:' + name, 'FAIL', '%s missing (%s)' % (rel, commit))
        else:
            has = marker.encode() in rd(dst)
            add('fix:' + name, 'PASS' if has else 'FAIL', '%s %s [%s]' % (rel, 'has marker' if has else 'lacks marker', commit))
    origin = (cfg.get('allowed_origins') or [''])[0]
    base = 'http://%s:%s' % (cfg.get('bind', '127.0.0.1'), cfg.get('port', 7181))
    want = re.search(r"AgentVersion = '([^']+)'", rd(os.path.join(PAYLOAD, 'src/agent.ps1')).decode()).group(1)
    try:
        st, r = http('GET', base + '/ping', origin, timeout=5)
        ver = str(r.get('version') or r.get('agent') or r)
        add('agent_ping', 'PASS' if want in ver else 'FAIL', 'answers: %s (payload %s)' % (ver[:80], want))
    except Exception as e:
        add('agent_ping', 'FAIL', 'agent not answering on %s (%s) -> aibridge_install.py --restart-agent' % (base, e))
        roundtrip = False
    if roundtrip:
        nonce = hashlib.sha1(os.urandom(8)).hexdigest()[:10]
        try:
            st, r = http('POST', base + '/run', origin, {'cmd': 'Write-Output ' + nonce, 'cwd': root,
                                                         'timeout_s': 20, 'token': cfg.get('token')})
            ok = st == 200 and nonce in str(r.get('out', '')) and r.get('exit') == 0
            add('roundtrip', 'PASS' if ok else 'FAIL', 'exit=%s out=%r' % (r.get('exit'), str(r.get('out', ''))[:40]))
        except Exception as e:
            add('roundtrip', 'FAIL', str(e)[:200])
    else:
        add('roundtrip', 'NOT_CHECKED', 'agent not answering or --no-roundtrip')
    try:
        q = subprocess.run(['schtasks', '/query', '/tn', 'AIBridge-Agent'], capture_output=True, text=True, timeout=20)
        add('autostart', 'PASS' if q.returncode == 0 else 'NOT_CHECKED',
            'task AIBridge-Agent registered' if q.returncode == 0 else
            'no task AIBridge-Agent; SCHEDULING_POLICY.md forbids standing tasks, so start on demand: '
            'powershell -File ' + root + '/scripts/start-agent.ps1')
    except Exception as e:
        add('autostart', 'NOT_CHECKED', str(e)[:100])
    # extension loaded? Chrome keeps unpacked extensions in each profile's (Secure) Preferences under extensions.settings.<id>.path
    extdir = os.path.normpath(os.path.join(root, 'extension')).lower()
    found = None
    local = os.environ.get('LOCALAPPDATA', '')
    pats = [os.path.join(local, 'Google', 'Chrome', 'User Data', '*', '*Preferences'),
            os.path.join(os.environ.get('SystemDrive', 'C:') + os.sep, 'Users', '*', 'AppData', 'Local', 'Google', 'Chrome',
                         'User Data', '*', '*Preferences')]   # other Windows users too (the ssh login is not the desktop login)
    for pf in sorted({x for pat in pats for x in glob.glob(pat)}):
        try:
            txt = rd(pf).decode('utf-8', 'replace')
            data = json.loads(txt)
        except Exception:
            continue
        for eid, ent in (data.get('extensions', {}).get('settings', {}) or {}).items():
            if isinstance(ent, dict) and os.path.normpath(str(ent.get('path', ''))).lower() == extdir:
                found = (eid, os.path.basename(os.path.dirname(pf)))
    if found:
        ok = origin == 'chrome-extension://' + found[0]
        add('extension_loaded', 'PASS' if ok else 'FAIL',
            'Chrome profile %s has id %s; config origin %s' % (found[1], found[0], 'matches' if ok else
            'DIFFERS -> aibridge_install.py %s --origin=chrome-extension://%s --restart-agent' % (root, found[0])))
    else:
        add('extension_loaded', 'FAIL', 'no Chrome profile has %s loaded -> chrome://extensions, Developer mode, Load unpacked '
            '(expected id %s)' % (extdir, ext_id_for_path(os.path.join(root, 'extension'))))
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    root = (args[0] if args else 'F:/AIBridge').rstrip('/\\')
    rows = check(root, roundtrip='--no-roundtrip' not in sys.argv)
    if '--json' in sys.argv:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print('%-12s %-70s %s' % (r['status'], r['check'], r['evidence']))
    bad = [r for r in rows if r['status'] == 'FAIL']
    print('aibridge_verify: %s (%d FAIL of %d)' % ('PASS' if not bad else 'FAIL', len(bad), len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
