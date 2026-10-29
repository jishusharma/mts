# Cross-Review Report: api_batch.py

- **Reviewer:** Gemini (Antigravity session, JIS-NUC)
- **Target:** `scripts/dev/api_batch.py` (Claude-built)
- **Reference card:** `gemini-api-batch-crossreview`
- **Date:** 2026-10-30

## 1. Price Constants & Estimate Formula

### Price Constants (`scripts/dev/api_batch.py:27`)
```python
PRICE_PER_MTOK = {'claude-haiku-5-5': (1.0, 5.0), 'claude-sonnet-5-5': (3.0, 15.0), 'claude-opus-5-5': (5.0, 25.0)}  # OURS
```
Prices represent `(price_in, price_out)` in USD per million tokens (ceiling placeholders without batch discount).

### Estimate Formula (`scripts/dev/api_batch.py:31-32, 55-58`)
- Token estimator: `est_tokens(text) = len(text) // 3 + 1` (deliberately conservative at 3 chars/token).
- Worst case cost:
  ```python
  tin = sum(est_tokens(j['prompt'] + j.get('system', '')) for j in jobs)
  worst_case_usd = (tin * pin + len(jobs) * max_tokens * pout) / 1e6
  ```

## 2. Three-File Cost Table (Hand vs Script)

Tested on model `claude-haiku-5-5` ($1.0 / Mtok in, $5.0 / Mtok out) with `max_tokens = 1024`:

| Job File | Description | Jobs (N) | Input Tokens (`tin`) | Hand Calculated USD | Script `worst_case_usd` | Match |
|---|---|---|---|---|---|---|
| `jobs_1.jsonl` | 1 single job | 1 | 8 | $0.005128 | $0.005128 | EXACT |
| `jobs_100.jsonl` | 100 batch jobs | 100 | 790 | $0.512790 | $0.512790 | EXACT |
| `jobs_long.jsonl` | Long prompt + system prompt (~3.3k chars) | 1 | 1132 | $0.006252 | $0.006252 | EXACT |

### Refusal Threshold Behavior (`scripts/dev/api_batch.py:116-120`)
- `if cost > a.max_usd`: prints `api_batch: over the cap, nothing sent` and exits with code `2`.
- When `max_usd` > `cost`: passes check.
- When `cost == max_usd`: condition `cost > a.max_usd` is `False`, allowing execution (exit code `0` under `--dry-run`).
- Verified via subprocess CLI invocations with `--dry-run`.

## 3. Key Handling and Network Call Grep Verification

### API Key Security Audit
- `scripts/dev/api_batch.py:72-76`: Key is fetched directly from `os.environ.get('ANTHROPIC_API_KEY')` and passed into header `'x-api-key': key`.
- Grep of all `print`, `sys.stdout.write`, and file write calls confirmed that `key` or `ANTHROPIC_API_KEY` is NEVER printed, logged, or serialized to disk.
- Line 28 defines `BLOCKED = ('.secrets', '.env', '.pem', '.key', 'api_key', 'apikey')`: any prompt containing key/secret references is refused before dispatch.

### Network Calls Under `--dry-run`
- `scripts/dev/api_batch.py:119-120`:
  ```python
  if a.dry_run:
      return 0
  ```
  Execution terminates and returns `0` before line 121 (`call('POST', API, ...)`).
- Subprocess verification confirmed that running `submit --dry-run` makes zero network attempts and succeeds even when `ANTHROPIC_API_KEY` is unset.

## 4. Findings Table

| Severity | File:Line | Evidence | Proposed Fix |
|---|---|---|---|
| None | `scripts/dev/api_batch.py` | Strict compliance with cost estimation, security, threshold guarding, and dry-run boundaries. | No code changes required. |

## 5. Verdict

**SOUND**
