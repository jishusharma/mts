"""Bulk non-urgent LLM jobs on the Claude API credit (Message Batches, half price). Stdlib only.

  python scripts/dev/api_batch.py submit jobs.jsonl --max-usd 2 [--model claude-haiku-5-5] [--max-tokens 1024] [--dry-run]
  python scripts/dev/api_batch.py status <batch_id>
  python scripts/dev/api_batch.py fetch  <batch_id> [--out results.jsonl]
  python scripts/dev/api_batch.py wait   <batch_id> --out results.jsonl [--timeout-min 90]   (polls every 60 s; exit 3 on timeout)

jobs.jsonl: one JSON per line {"id": "...", "prompt": "...", "system": "..." (optional)}.
Results: one JSON per line {"id", "status", "text", "in_tokens", "out_tokens"}.

Key: env ANTHROPIC_API_KEY, else the file named by env MTS_API_KEY_FILE, else F:/ClaudePlaform/key.txt (outside the repo,
whitespace stripped, never printed). Works the same on the NUC and the desktop. Set a spend limit in the console too.
Guard: `submit` estimates the worst-case cost and refuses above --max-usd. Prices below are OURS placeholders
(USD per million tokens, batch rate not applied, so the estimate is a ceiling); check them against the console.
Use for: extractions, quote checks, classification, judge passes. Not for live path, accounts or secrets: a prompt
containing a secret-like path is refused. Prompt text is sent to Anthropic; keep runtime/order/account data out.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True

API = 'https://api.anthropic.com/v1/messages/batches'
PRICE_PER_MTOK = {'claude-haiku-5-5': (1.0, 5.0), 'claude-sonnet-5-5': (3.0, 15.0), 'claude-opus-5-5': (5.0, 25.0)}  # OURS
KEY_FILE_DEFAULT = 'F:/ClaudePlaform/key.txt'
POLL_S = 60
BLOCKED = ('.secrets', '.env', '.pem', '.key', 'api_key', 'apikey')


def est_tokens(text: str) -> int:
    return len(text) // 3 + 1  # deliberately high (3 chars/token)


def load_jobs(path: Path) -> list[dict]:
    jobs, seen = [], set()
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        j = json.loads(line)
        if not j.get('id') or not j.get('prompt'):
            raise SystemExit(f'api_batch: line {n} needs id and prompt')
        if j['id'] in seen:
            raise SystemExit(f'api_batch: duplicate id {j["id"]}')
        seen.add(j['id'])
        low = (j['prompt'] + j.get('system', '')).lower()
        if any(b in low for b in BLOCKED):
            raise SystemExit(f'api_batch: line {n} mentions a secret-like path; refusing')
        jobs.append(j)
    if not jobs:
        raise SystemExit('api_batch: no jobs')
    return jobs


def worst_case_usd(jobs: list[dict], model: str, max_tokens: int) -> float:
    pin, pout = PRICE_PER_MTOK.get(model, max(PRICE_PER_MTOK.values()))
    tin = sum(est_tokens(j['prompt'] + j.get('system', '')) for j in jobs)
    return (tin * pin + len(jobs) * max_tokens * pout) / 1e6


def build_requests(jobs: list[dict], model: str, max_tokens: int) -> list[dict]:
    reqs = []
    for j in jobs:
        params = {'model': model, 'max_tokens': max_tokens, 'messages': [{'role': 'user', 'content': j['prompt']}],
                  'thinking': {'type': 'disabled'}}   # Claude 5.5 thinks by default and can spend the whole max_tokens on it (337-job Haiku run 2026-11-03: 225 empty replies)
        if j.get('system'):
            params['system'] = j['system']
        reqs.append({'custom_id': j['id'], 'params': params})
    return reqs


def get_key() -> str:
    key = (os.environ.get('ANTHROPIC_API_KEY') or '').strip()
    if key:
        return key
    path = Path(os.environ.get('MTS_API_KEY_FILE') or KEY_FILE_DEFAULT)
    try:
        key = path.read_text(encoding='utf-8').strip()
    except OSError:
        raise SystemExit(f'api_batch: no ANTHROPIC_API_KEY and key file not readable: {path}')
    if not key:
        raise SystemExit(f'api_batch: key file is empty: {path}')
    return key


def call(method: str, url: str, body: dict | None = None, opener=urllib.request.urlopen) -> bytes:
    key = get_key()
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None, headers={
        'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    with opener(req, timeout=120) as r:
        return r.read()


def parse_results(raw: str) -> list[dict]:
    out = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        res = r.get('result', {})
        msg = res.get('message') or {}
        text = ''.join(b.get('text', '') for b in msg.get('content', []) if b.get('type') == 'text')
        use = msg.get('usage', {})
        out.append({'id': r.get('custom_id'), 'status': res.get('type'), 'text': text,
                    'in_tokens': use.get('input_tokens', 0), 'out_tokens': use.get('output_tokens', 0)})
    return out


def main(argv=None, opener=urllib.request.urlopen, sleep=time.sleep) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('submit')
    s.add_argument('jobs')
    s.add_argument('--model', default='claude-haiku-5-5')
    s.add_argument('--max-tokens', type=int, default=1024)
    s.add_argument('--max-usd', type=float, required=True)
    s.add_argument('--dry-run', action='store_true')
    st = sub.add_parser('status')
    st.add_argument('batch_id')
    f = sub.add_parser('fetch')
    f.add_argument('batch_id')
    f.add_argument('--out')
    w = sub.add_parser('wait')
    w.add_argument('batch_id')
    w.add_argument('--out', required=True)
    w.add_argument('--timeout-min', type=float, default=90)
    a = ap.parse_args(argv)

    if a.cmd == 'submit':
        jobs = load_jobs(Path(a.jobs))
        cost = worst_case_usd(jobs, a.model, a.max_tokens)
        print(f'{len(jobs)} jobs, model {a.model}, worst-case ${cost:.4f} (cap ${a.max_usd:.2f}, batch discount not counted)')
        if cost > a.max_usd:
            print('api_batch: over the cap, nothing sent')
            return 2
        if a.dry_run:
            return 0
        resp = json.loads(call('POST', API, {'requests': build_requests(jobs, a.model, a.max_tokens)}, opener))
        print(f'batch {resp["id"]} {resp.get("processing_status")}')
        return 0
    if a.cmd == 'status':
        resp = json.loads(call('GET', f'{API}/{a.batch_id}', None, opener))
        print(resp.get('processing_status'), json.dumps(resp.get('request_counts')))
        return 0
    if a.cmd == 'wait':
        waited = 0
        while True:
            resp = json.loads(call('GET', f'{API}/{a.batch_id}', None, opener))
            if resp.get('processing_status') == 'ended':
                break
            if waited + POLL_S > a.timeout_min * 60:
                print(f'api_batch: timed out after {waited}s ({resp.get("processing_status")})')
                return 3
            sleep(POLL_S)
            waited += POLL_S
        return write_results(resp, a.out, opener)
    resp = json.loads(call('GET', f'{API}/{a.batch_id}', None, opener))
    if resp.get('processing_status') != 'ended':
        print(f'api_batch: not ended yet ({resp.get("processing_status")})')
        return 3
    return write_results(resp, a.out, opener)


def write_results(resp: dict, out: str | None, opener) -> int:
    rows = parse_results(call('GET', resp['results_url'], None, opener).decode('utf-8'))
    text = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    if out:
        Path(out).write_text(text, encoding='utf-8', newline='\n')
        print(f'{len(rows)} results -> {out}')
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
