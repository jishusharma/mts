"""Spec tests for aibridge_version.py. Expected values come from its docstring, derived by hand; temp dirs only."""
import hashlib
import json
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import aibridge_version as av

V = '1.2.3'
MANIFEST = '{\n  "name": "x",\n  "version": "%s"\n}\n'
LOOP = "var L = {};\nL.VERSION = '%s';\n"
AGENT = "$AgentVersion = '%s'\n"


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode())


def make_bridge(root, ver=V, release=True):
    put(root, 'scripts/aibridge/extension/manifest.json', MANIFEST % ver)
    put(root, 'scripts/aibridge/extension/loop.js', LOOP % ver)
    put(root, 'scripts/aibridge/src/agent.ps1', AGENT % ver)
    put(root, 'scripts/aibridge/RELEASES.json', json.dumps({'current': ver, 'releases': {}}))
    if release:
        rel = av.load(root)
        rel['releases'][ver] = av.fingerprint(root)
        put(root, 'scripts/aibridge/RELEASES.json', json.dumps(rel))


class T(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = self._td.name

    def tearDown(self):
        self._td.cleanup()

    # at the limit: everything agrees
    def test_consistent_checkout_has_no_problems(self):
        make_bridge(self.root)
        self.assertEqual(av.check(self.root), [])

    # one below/above: a single version string off by one
    def test_one_version_string_disagrees(self):
        make_bridge(self.root)
        put(self.root, 'scripts/aibridge/extension/loop.js', LOOP % '1.2.2')
        # loop.js is a bridge file, so the fingerprint also moves: exactly 2 problems, the first names loop.js
        probs = av.check(self.root)
        self.assertEqual(len(probs), 2)
        self.assertEqual(probs[0], "scripts/aibridge/extension/loop.js says '1.2.2', RELEASES.json current is '1.2.3'")
        self.assertIn('bridge files changed since 1.2.3', probs[1])

    def test_extra_byte_in_bridge_file_breaks_fingerprint_only(self):
        make_bridge(self.root)
        put(self.root, 'scripts/aibridge/src/other.ps1', 'x')
        probs = av.check(self.root)
        self.assertEqual(len(probs), 1)
        self.assertIn('bridge files changed since 1.2.3', probs[0])
        self.assertIn('--record <new>', probs[0])

    # empty input
    def test_empty_payload_fingerprint_is_sha256_of_nothing(self):
        os.makedirs(os.path.join(self.root, 'scripts/aibridge'))
        self.assertEqual(av.bridge_files(self.root), [])
        self.assertEqual(av.fingerprint(self.root), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')

    def test_golden_fingerprint_single_file(self):
        put(self.root, 'scripts/aibridge/a.txt', b'hi\n')
        # sha256(b'scripts/aibridge/a.txt\0' + b'3\0' + b'hi\n'), computed by hand with hashlib
        self.assertEqual(av.fingerprint(self.root), 'c474eccf846441038cf4b8e4dac95125887a38838b4012c7953bb20b8866a825')

    def test_crlf_hashes_same_as_lf(self):
        put(self.root, 'scripts/aibridge/a.txt', b'hi\n')
        lf = av.fingerprint(self.root)
        put(self.root, 'scripts/aibridge/a.txt', b'hi\r\n')
        self.assertEqual(av.fingerprint(self.root), lf)

    def test_bridge_files_filtering_and_extras(self):
        put(self.root, 'scripts/aibridge/b.txt', 'b')
        put(self.root, 'scripts/aibridge/RELEASES.json', '{}')
        put(self.root, 'scripts/aibridge/__pycache__/m.txt', 'c')
        put(self.root, 'scripts/aibridge/m.pyc', 'c')
        put(self.root, 'scripts/dev/dsa.py', 'x')
        put(self.root, 'scripts/dev/aibridge_health.py', 'x')
        put(self.root, 'scripts/dev/not_listed.py', 'x')
        self.assertEqual(av.bridge_files(self.root),
                         ['scripts/aibridge/b.txt', 'scripts/dev/aibridge_health.py', 'scripts/dev/dsa.py'])

    # malformed input
    def test_missing_version_string_reports_none(self):
        make_bridge(self.root)
        put(self.root, 'scripts/aibridge/src/agent.ps1', 'no version here\n')
        probs = av.check(self.root)
        self.assertEqual(probs[0], "scripts/aibridge/src/agent.ps1 says None, RELEASES.json current is '1.2.3'")

    def test_malformed_releases_json_raises(self):
        make_bridge(self.root)
        put(self.root, 'scripts/aibridge/RELEASES.json', '{not json')
        with self.assertRaises(ValueError):
            av.check(self.root)

    # error path
    def test_current_without_recorded_fingerprint(self):
        make_bridge(self.root, release=False)
        probs = av.check(self.root)
        self.assertEqual(probs, ['scripts/aibridge/RELEASES.json has no fingerprint for current 1.2.3'])

    def test_missing_version_file_raises(self):
        make_bridge(self.root)
        os.remove(os.path.join(self.root, 'scripts/aibridge/extension/manifest.json'))
        with self.assertRaises(FileNotFoundError):
            av.check(self.root)

    # record
    def test_record_sets_current_and_check_passes(self):
        make_bridge(self.root)
        for rel, tpl in (('scripts/aibridge/extension/manifest.json', MANIFEST),
                         ('scripts/aibridge/extension/loop.js', LOOP), ('scripts/aibridge/src/agent.ps1', AGENT)):
            put(self.root, rel, tpl % '1.2.4')
        rel = av.record('1.2.4', self.root)
        self.assertEqual(rel['current'], '1.2.4')
        self.assertEqual(set(rel['releases']), {'1.2.3', '1.2.4'})
        self.assertEqual(rel['releases']['1.2.4'], av.fingerprint(self.root))
        self.assertEqual(av.check(self.root), [])
        raw = open(os.path.join(self.root, 'scripts/aibridge/RELEASES.json'), 'rb').read()
        self.assertTrue(raw.endswith(b'}\n'))
        self.assertNotIn(b'\r', raw)

    def test_record_refuses_already_recorded_version(self):
        make_bridge(self.root)
        with self.assertRaises(SystemExit) as c:
            av.record(V, self.root)
        self.assertIn('already recorded', str(c.exception))


if __name__ == '__main__':
    unittest.main()
