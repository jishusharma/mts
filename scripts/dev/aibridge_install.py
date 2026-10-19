# Install / update AIBridge to the payload in scripts/aibridge (v0.7.1: fluent auto-run, parallel chats, receipts).
# Usage: python scripts/dev/aibridge_install.py [F:/AIBridge] [--dry] [--restart-agent]
# Run on each host that has an AIBridge (JIS-NB, JIS-NUC). Token-free: the machine's own TOKEN, AGENT_CWD and
# config.json are kept. Every overwritten file is first copied to <name>.pre_v07 (once). policy.json is MERGED, not replaced.
# Afterwards: reload the extension in chrome://extensions (each Chrome profile), F5 each chat tab, restart the agent
# (--restart-agent does it, or: powershell -File <root>\scripts\start-agent.ps1 after stopping the old one).
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.normpath(os.path.join(HERE, '..', 'aibridge'))
VERSION = '0.7.1'

args = [a for a in sys.argv[1:] if not a.startswith('--')]
dry = '--dry' in sys.argv
restart = '--restart-agent' in sys.argv
root = (args[0] if args else 'F:/AIBridge').rstrip('/\\')

POLICY_PATCH = json.load(open(os.path.join(PAYLOAD, 'policy_patch.json'), encoding='utf-8'))
EXTRA_ROOTS = [r'C:\Users\E-ngineers\AppData\Local\Temp', r'F:\AIBridge', r'F:\MTS']


def fail(msg):
    sys.exit('aibridge_install: ' + msg)


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def write(p, s):
    if dry:
        print('  would write', p)
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def backup(p):
    b = p + '.pre_v07'
    if os.path.exists(p) and not os.path.exists(b) and not dry:
        shutil.copy2(p, b)


for need in ('src/agent.ps1', 'src/config.json', 'extension/manifest.json', 'extension/background.js'):
    if not os.path.exists(os.path.join(root, need)):
        fail('%s not found under %s (is this an AIBridge root?)' % (need, root))

bg_old = read(os.path.join(root, 'extension/background.js'))
tm = re.search(r"const TOKEN = '([0-9a-f]{16,})';", bg_old)
cm = re.search(r"const AGENT_CWD = ('(?:[^'\\]|\\.)*');", bg_old)
um = re.search(r"const AGENT_URL = ('[^']+');", bg_old)
if not tm or not cm or not um:
    fail('could not read TOKEN / AGENT_CWD / AGENT_URL from the installed background.js')
bg = read(os.path.join(PAYLOAD, 'extension/background.js'))
bg = bg.replace("'__TOKEN__'", "'" + tm.group(1) + "'")
bg = re.sub(r"const AGENT_CWD = '.*';", lambda m: 'const AGENT_CWD = ' + cm.group(1) + ';', bg, count=1)
bg = re.sub(r"const AGENT_URL = '.*';", lambda m: 'const AGENT_URL = ' + um.group(1) + ';', bg, count=1)

files = [
    ('src/agent.ps1', None), ('src/checks.ps1', None), ('src/concurrency.ps1', None),
    ('extension/content.js', None), ('extension/loop.js', None), ('extension/manifest.json', None),
    ('extension/background.js', bg),
    ('scripts/start-agent.ps1', None),
    ('scripts/run-task.ps1', None),
    ('docs/V07_CONTRACT.md', None),
    ('policy_patch.json', None),
    ('tests/loop.test.js', None),
    ('tests/handsfree.test.js', None),
    ('tests/agent_live_selftest.py', None),
]
for rel, content in files:
    dst = os.path.join(root, rel)
    src = os.path.join(PAYLOAD, rel)
    if content is None:
        if not os.path.exists(src):
            continue
        content = read(src)
    backup(dst)
    write(dst, content)
    print('  ' + rel)

tdir = os.path.join(PAYLOAD, 'tasks')
for tf in sorted(os.listdir(tdir)):
    dst = os.path.join(root, 'tasks', tf)
    backup(dst)
    write(dst, read(os.path.join(tdir, tf)))
    print('  tasks/' + tf)

pp = os.path.join(root, 'src/policy.json')
pol = json.loads(read(pp).lstrip('\ufeff'))
pol.update(POLICY_PATCH)
have = {r.lower() for r in pol.get('roots', [])}
for r in EXTRA_ROOTS:
    if r.lower() not in have:
        pol.setdefault('roots', []).append(r)
pol['_comment'] = ('OPEN MODE + FLUENT AUTO-RUN (v%s, operator 2026-10-14): auto-run runs everything except auto_confirm_regex '
                   '(irreversible forms) and the secrets/keys/HALT denies. Empty auto_confirm_regex to remove even that. '
                   'Set auto_mode to read_only for the old rules.' % VERSION)
backup(pp)
write(pp, json.dumps(pol, indent=2) + '\n')
print('  src/policy.json (merged)')
if not dry:
    print('installed AIBridge v%s into %s' % (VERSION, root))
    if restart:
        ps = os.path.join(root, 'scripts', 'start-agent.ps1')
        cfg = json.loads(read(os.path.join(root, 'src/config.json')).lstrip('\ufeff'))
        stop = ("$c = Get-NetTCPConnection -LocalPort %d -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; "
                "if ($c) { Stop-Process -Id $c.OwningProcess -Force; Start-Sleep -Seconds 1 }" % int(cfg['port']))
        subprocess.call(['powershell.exe', '-NoProfile', '-Command', stop])
        subprocess.call(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps])
    else:
        print('next: reload the extension (chrome://extensions), F5 the chat tab(s), restart the agent '
              '(rerun with --restart-agent, or stop the old one and run scripts\\start-agent.ps1)')
