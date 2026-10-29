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
        with self.assertRaises(SystemExit):
            api_batch.call('GET', api_batch.API + '/x')


if __name__ == '__main__':
    unittest.main()
