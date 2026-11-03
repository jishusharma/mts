import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_batch


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def jobs_file(rows):
    p = Path(tempfile.mkdtemp()) / 'jobs.jsonl'
    p.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
    return str(p)


class ApiBatchTest(unittest.TestCase):
    def setUp(self):
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    def test_over_cap_sends_nothing(self):
        calls = []
        p = jobs_file([{'id': 'a', 'prompt': 'x' * 3000}])
        rc = api_batch.main(['submit', p, '--max-usd', '0.0001'], opener=lambda *a, **k: calls.append(a))
        self.assertEqual(rc, 2)
        self.assertEqual(calls, [])

    def test_secret_like_prompt_refused(self):
        p = jobs_file([{'id': 'a', 'prompt': 'read .secrets/key'}])
        with self.assertRaises(SystemExit):
            api_batch.load_jobs(Path(p))

    def test_duplicate_id_refused(self):
        p = jobs_file([{'id': 'a', 'prompt': 'x'}, {'id': 'a', 'prompt': 'y'}])
        with self.assertRaises(SystemExit):
            api_batch.load_jobs(Path(p))

    def test_submit_posts_requests(self):
        seen = {}

        def opener(req, timeout=0):
            seen['body'] = json.loads(req.data)
            seen['key'] = req.get_header('X-api-key')
            return FakeResp(json.dumps({'id': 'msgbatch_1', 'processing_status': 'in_progress'}).encode())
        p = jobs_file([{'id': 'a', 'prompt': 'hi', 'system': 's'}])
        with contextlib.redirect_stdout(io.StringIO()):
            rc = api_batch.main(['submit', p, '--max-usd', '1'], opener=opener)
        self.assertEqual(rc, 0)
        self.assertEqual(seen['key'], 'test-key')
        r = seen['body']['requests'][0]
        self.assertEqual(r['custom_id'], 'a')
        self.assertEqual(r['params']['system'], 's')
        self.assertEqual(r['params']['model'], 'claude-haiku-5-5')

    def test_parse_results(self):
        raw = json.dumps({'custom_id': 'a', 'result': {'type': 'succeeded', 'message': {
            'content': [{'type': 'text', 'text': 'ok'}], 'usage': {'input_tokens': 5, 'output_tokens': 2}}}})
        self.assertEqual(api_batch.parse_results(raw)[0], {'id': 'a', 'status': 'succeeded', 'text': 'ok', 'in_tokens': 5, 'out_tokens': 2})

    def test_fetch_waits_until_ended(self):
        opener = lambda req, timeout=0: FakeResp(json.dumps({'processing_status': 'in_progress'}).encode())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(api_batch.main(['fetch', 'b1'], opener=opener), 3)

    def test_missing_key_fails_closed(self):
        del os.environ['ANTHROPIC_API_KEY']
        os.environ['MTS_API_KEY_FILE'] = str(Path(tempfile.mkdtemp()) / 'absent.txt')
        self.addCleanup(os.environ.pop, 'MTS_API_KEY_FILE', None)
        with self.assertRaises(SystemExit):
            api_batch.call('GET', api_batch.API + '/x')

    def _keyfile(self, text):
        d = Path(tempfile.mkdtemp())
        f = d / 'key.txt'
        f.write_text(text, encoding='utf-8')
        return str(f)

    def _clear_env(self):
        os.environ.pop('ANTHROPIC_API_KEY', None)
        self.addCleanup(os.environ.pop, 'MTS_API_KEY_FILE', None)

    def test_key_from_file_when_env_unset(self):
        self._clear_env()
        os.environ['MTS_API_KEY_FILE'] = self._keyfile('  file-key-1' + chr(13) + chr(10))
        keys = []

        def opener(req, timeout=0):
            keys.append(req.get_header('X-api-key'))
            return FakeResp(json.dumps({'processing_status': 'in_progress', 'request_counts': {}}).encode())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(api_batch.main(['status', 'b1'], opener=opener), 0)
        self.assertEqual(keys, ['file-key-1'])

    def test_env_wins_over_file(self):
        os.environ['MTS_API_KEY_FILE'] = self._keyfile('file-key')
        self.addCleanup(os.environ.pop, 'MTS_API_KEY_FILE', None)
        self.assertEqual(api_batch.get_key(), 'test-key')

    def test_missing_file_clear_error_no_key_leak(self):
        self._clear_env()
        os.environ['MTS_API_KEY_FILE'] = str(Path(tempfile.mkdtemp()) / 'nope.txt')
        with self.assertRaises(SystemExit) as cm:
            api_batch.get_key()
        self.assertIn('key file', str(cm.exception))

    def test_empty_file_refused(self):
        self._clear_env()
        os.environ['MTS_API_KEY_FILE'] = self._keyfile('  ' + chr(10))
        with self.assertRaises(SystemExit):
            api_batch.get_key()

    def test_wait_polls_then_fetches(self):
        out = Path(tempfile.mkdtemp()) / 'r.jsonl'
        state = {'n': 0}
        row = json.dumps({'custom_id': 'a', 'result': {'type': 'succeeded', 'message': {
            'content': [{'type': 'text', 'text': 'ok'}], 'usage': {}}}})

        def opener(req, timeout=0):
            if req.full_url.endswith('/results'):
                return FakeResp(row.encode())
            state['n'] += 1
            st = 'ended' if state['n'] >= 3 else 'in_progress'
            return FakeResp(json.dumps({'processing_status': st, 'results_url': api_batch.API + '/b1/results'}).encode())
        sleeps = []
        with contextlib.redirect_stdout(io.StringIO()):
            rc = api_batch.main(['wait', 'b1', '--out', str(out)], opener=opener, sleep=sleeps.append)
        self.assertEqual(rc, 0)
        self.assertEqual(sleeps, [60, 60])
        self.assertIn('"text": "ok"', out.read_text(encoding='utf-8'))

    def test_wait_timeout_exits_3(self):
        opener = lambda req, timeout=0: FakeResp(json.dumps({'processing_status': 'in_progress'}).encode())
        sleeps = []
        with contextlib.redirect_stdout(io.StringIO()):
            rc = api_batch.main(['wait', 'b1', '--out', 'x', '--timeout-min', '3'], opener=opener, sleep=sleeps.append)
        self.assertEqual(rc, 3)
        self.assertEqual(sum(sleeps), 180)


if __name__ == '__main__':
    unittest.main()
