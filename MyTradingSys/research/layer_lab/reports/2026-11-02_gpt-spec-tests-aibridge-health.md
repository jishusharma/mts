# gpt-spec-tests-aibridge-health

**20 tests pass; 3/3 scratch mutations detected.**

## Checked

- `scripts/dev/aibridge_health.py:22-91`: read the full source and enumerated branches in `liveness`, `installed_version`, `running_version`, `trunk_current`, `version_report`, and `main`.
- `scripts/dev/test_aibridge_health.py:40-166`: added spec-derived tests using mocked sockets/network/git and temporary filesystem roots. No network call or live path is used.
- `scripts/dev/extra_tests.tsv`: registered the test for the extra-test gate.
- `scripts/dev/aibridge_health.py` was not edited.

## Hand-derived expectations

| Spec case | Expected result | Test |
|---|---|---|
| `recv(256)` exactly at its byte limit, HTTP 503 | Exit 0 and `UP (HTTP/1.1 503)`; any HTTP status qualifies | `test_liveness_accepts_any_http_status_at_256_byte_read_limit` |
| 255-byte HTTP response | Exit 0 | `test_liveness_accepts_one_byte_below_read_limit` |
| 257-byte HTTP response | Exit 0; `recv` is capped at 256 and the status line remains readable | `test_liveness_reply_one_byte_over_limit_still_checks_status_line` |
| Empty reply | Exit 1 because empty status line does not start `HTTP/` | `test_liveness_empty_or_non_http_reply_is_down` |
| Malformed non-HTTP status line | Exit 1 | `test_liveness_malformed_non_http_status_line_is_down` |
| Connect/reply errors | Exit 1; reply error closes socket | `test_liveness_connect_error_is_down`, `test_liveness_recv_error_closes_socket_and_is_down` |
| Missing files, malformed JSON, missing manifest key | Both installed values are `None`, with manifest errors limited to the documented catch set | `test_installed_version_*` |
| Valid `/ping`, empty/malformed/missing field, or request error | Return parsed `agent`, else `None` | `test_running_version_*` |
| `git show` succeeds/fails | Return origin current/source; otherwise checkout current/source | `test_trunk_current_*` |
| Version mismatch warnings | Print installed-vs-trunk warning; print running-vs-installed warning only when both values are truthy | `test_version_report_warns_for_installed_and_running_mismatches` |
| Default root and health exit code | Root defaults to `F:/AIBridge`; `main` returns liveness code after reporting | `test_main_defaults_root_and_returns_liveness_code` |

## Verification

Command: `python -m pytest scripts/dev/test_aibridge_health.py -q` — **20 passed** (one pytest cache warning due to existing cache directory).

Scratch mutation experiments copied the module, its version helper, and test file into a temporary directory under the repository, changed only the copies, and removed the directory at context exit:

| Mutation | Result |
|---|---|
| Force liveness to return up for every reply | Detected: 2 failed, 18 passed |
| Return a non-`None` value for an unreadable manifest | Detected: 3 failed, 17 passed |
| Return an agent value when `/ping` request errors | Detected: 3 failed, 17 passed |

No source mutation was retained. No `git` command was run.
