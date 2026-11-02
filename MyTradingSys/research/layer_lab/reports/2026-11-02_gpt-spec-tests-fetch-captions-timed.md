# Spec tests for `fetch_captions_timed.py`

**10 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_fetch_captions_timed.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/fetch_captions_timed.py` lines 1-506. Audited pure components covering `parse_vtt`, `ip_hash`, `daily_budget`, `budget_used`, `current_level`, `fleet_block`, and `_local_blocked_until`.
- Branches covered:
  - `parse_vtt`: timestamp parsing `HH:MM:SS`, HTML entity unescaping (`&amp;`, `&gt;`, `&lt;`), tag stripping (`<c>...</c>`), deduplication of consecutive identical captions (`last == t`), and handling empty / non-cue lines.
  - `ip_hash`: empty IP handling, 8-character hex SHA-256 digest calculation.
  - `daily_budget`: default budget (40), environment override parsing (`YT_DAILY_BUDGET`), fallback on invalid integer parse, and proxy budget (150).
  - `budget_used`: aggregation of rolling 24 h local request timestamps with remote fleet `ytuse` signals, filtering out own-host signals and outside-window signals.
  - `current_level`: resolution of the newest event between local record timestamp and fleet `ytblock`/`ytclean` rows, including reset to level 0 upon clean signal.
  - `fleet_block`: latest block detection and clean cancellation override.
  - `_local_blocked_until`: expiration checks against future/past timestamps, and IP mismatch handling (home vs proxy/VPN IP).
- `python -m pytest scripts/dev/test_fetch_captions_timed.py -v`: **10 passed in 1.05s**.
- Scratch mutations on temporary copies:
  - M1: Hour conversion modified from `h * 3600` to `h * 60` in `parse_vtt` (**1 failed, 9 passed**; caught by `test_parse_vtt_hours_calculation`).
  - M2: Disabled HTML tag stripping in `parse_vtt` (**1 failed, 9 passed**; caught by `test_parse_vtt_basic_cues_and_entity_decoding`).
  - M3: Changed `ip_hash` digest truncation from `[:8]` to `[:6]` (**1 failed, 9 passed**; caught by `test_ip_hash_empty_and_known_vector`).
- Audited source unchanged: SHA-256 of `scripts/dev/fetch_captions_timed.py` is `9b66748a964b7fe75e2c657094984716adebe9a367ccf89a36e393007d0a7907`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/fetch_captions_timed.py:1-506` | MATCH | Pure functions match spec, error fallbacks, and fleet contracts. Audited source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:186` | MATCH | Registered `scripts/dev/test_fetch_captions_timed.py` into extra test runner. | None. |

## Follow-up cards

None.
