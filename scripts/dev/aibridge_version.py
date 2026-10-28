"""aibridge_version.py - the DSA bridge version guard (operator 2026-10-28: every bridge fix bumps the bridge version, ALWAYS).

Fingerprint = sha256 over the DSA-bridge files: scripts/aibridge/** (payload and its tests), scripts/dev/dsa.py,
aibridge_install.py, aibridge_verify.py, aibridge_health.py, bridge_selftest.ps1, scripts/sched/register_aibridge.ps1.
Line endings are normalised to LF so a Windows autocrlf checkout hashes the same as the repo.

scripts/aibridge/RELEASES.json holds {"current": V, "releases": {V: fingerprint-at-V}}. A change to any bridge file
changes the fingerprint, so check() fails until the version is bumped in the three version strings and a new release is
recorded with `--record <new>`. aibridge_install.py reads its VERSION from RELEASES.json, so there is no fourth copy.

CLI:  python scripts/dev/aibridge_version.py            check this checkout (exit 0 = consistent, 1 = problems)
      python scripts/dev/aibridge_version.py --record V  after bumping the version strings to V, record its fingerprint
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
PAYLOAD_REL = 'scripts/aibridge'
RELEASES_REL = 'scripts/aibridge/RELEASES.json'
EXTRA_REL = ('scripts/dev/dsa.py', 'scripts/dev/aibridge_install.py', 'scripts/dev/aibridge_verify.py',
             'scripts/dev/aibridge_health.py', 'scripts/dev/bridge_selftest.ps1', 'scripts/sched/register_aibridge.ps1')
# the three copies of the version string (aibridge_install.py reads RELEASES.json, so it is not a copy)
VERSION_SITES = (
    ('scripts/aibridge/extension/manifest.json', r'"version": "([^"]+)"'),
    ('scripts/aibridge/extension/loop.js', r"L\.VERSION = '([^']+)'"),
    ('scripts/aibridge/src/agent.ps1', r"\$AgentVersion = '([^']+)'"),
)


def read_bytes(root, rel):
    with open(os.path.join(root, rel), 'rb') as f:
        return f.read()


def bridge_files(root=REPO):
    """Sorted repo-relative paths of every DSA-bridge file that exists under root (RELEASES.json itself excluded)."""
    out = []
    base = os.path.join(root, PAYLOAD_REL)
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if x != '__pycache__']
        for f in files:
            rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/')
            if rel != RELEASES_REL and not f.endswith('.pyc'):
                out.append(rel)
    out += [r for r in EXTRA_REL if os.path.isfile(os.path.join(root, r))]
    return sorted(out)


def fingerprint(root=REPO):
    h = hashlib.sha256()
    for rel in bridge_files(root):
        data = read_bytes(root, rel).replace(b'\r\n', b'\n')
        h.update(rel.encode() + b'\0' + str(len(data)).encode() + b'\0' + data)
    return h.hexdigest()


def load(root=REPO):
    with open(os.path.join(root, RELEASES_REL), encoding='utf-8') as f:
        return json.load(f)


def version_at(text, pattern):
    m = re.search(pattern, text, re.M)
    return m.group(1) if m else None


def check(root=REPO):
    """Problems as text lines; [] = every version string agrees and the bridge files match the recorded release."""
    problems = []
    rel = load(root)
    cur = rel['current']
    for path, pattern in VERSION_SITES:
        with open(os.path.join(root, path), encoding='utf-8') as f:
            found = version_at(f.read(), pattern)
        if found != cur:
            problems.append('%s says %r, RELEASES.json current is %r' % (path, found, cur))
    fp = fingerprint(root)
    recorded = rel['releases'].get(cur)
    if recorded is None:
        problems.append('%s has no fingerprint for current %s' % (RELEASES_REL, cur))
    elif recorded != fp:
        problems.append('bridge files changed since %s was recorded (fingerprint %s, recorded %s): bump the bridge version '
                        'in the 3 version strings, then python scripts/dev/aibridge_version.py --record <new>'
                        % (cur, fp[:12], recorded[:12]))
    return problems


def record(new, root=REPO):
    """Record the current fingerprint as release `new` and make it current. Refuses an already recorded version."""
    rel = load(root)
    if new in rel['releases']:
        raise SystemExit('aibridge_version: %s is already recorded; bump to a new number' % new)
    rel['releases'][new] = fingerprint(root)
    rel['current'] = new
    with open(os.path.join(root, RELEASES_REL), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(rel, indent=2) + '\n')
    return rel


def main(argv):
    if '--record' in argv:
        new = argv[argv.index('--record') + 1]
        rel = record(new)
        print('recorded %s %s' % (new, rel['releases'][new]))
        return 0
    problems = check(REPO)
    for p in problems:
        print('FAIL ' + p)
    print('aibridge_version: %s, fingerprint %s, %d problem(s)' % (load(REPO)['current'], fingerprint(REPO)[:12], len(problems)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
