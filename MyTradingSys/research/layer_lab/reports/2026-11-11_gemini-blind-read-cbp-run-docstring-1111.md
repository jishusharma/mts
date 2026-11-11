counts: MATCH=7 DIFF=0 NOT_IN_DATA=0 (sum 7)

# Gemini Blind Read: scripts/dev/cbp_run.py against its docstring and test

- Date: 2026-11-11
- Card: `gemini-blind-read-cbp-run-docstring-1111`
- Scope In:
  - `scripts/dev/cbp_run.py` (read)
  - `scripts/dev/test_cbp_run.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-cbp-run-docstring-1111.md` (new)
- Scope Out: no edit to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit

## Summary Table

| Clause # | Docstring Clause Requirement | Implementation Status | Implementation Code (`scripts/dev/cbp_run.py`) | Test Verification (`scripts/dev/test_cbp_run.py`) |
|---|---|---|---|---|
| 1 | Single-run fetch, extract, quote-check, store without daemon or scheduler | MATCH | SOURCED `cbp_run.py:1` `"""Run CBP once: fetch new analyst videos (last 5 days), extract, quote-check, store. No scheduler, no daemon.`<br>SOURCED `cbp_run.py:237-283` `run_once(now, fetch=fetch_new, extract=llm_extract, store=None)` executes single pipeline pass and returns `(added, total, rejected)` without loop or daemon. | SOURCED `test_cbp_run.py:36-59` `test_old_thesis_video_gets_a_verdict_not_a_row_and_bad_quote_is_dropped`: calls `run_once` once and verifies store write. |
| 2 | Actionable analysts loop: only enabled analysts in analysts.json fetched, failure on one does not halt the others | MATCH | SOURCED `cbp_run.py:9` `Only the actionable analysts in <CBP_HOME>/cbp_v2/analysts.json are fetched;`<br>SOURCED `cbp_run.py:108-110` `analysts()` loads `cfg["analysts"] if a.get("enabled")`<br>SOURCED `cbp_run.py:113-132` `fetch_new`: iterates `for an in ans:` invoking `fetch_captions_timed.py`, records `incomplete` on non-zero exit and continues without halting other analysts. | SOURCED `test_cbp_run.py:227-234` `test_fetch_new_continues_after_a_nonzero_analyst`: verifies analyst loop continues after exit 1 (`seen == ["A", "B", "C"]`). |
| 3 | DEFERRED on budget or lockout / date failed: non-zero exit flags incomplete, window retried | MATCH | SOURCED `cbp_run.py:6-7` `windows stay open for retries and catch-up.`<br>SOURCED `cbp_run.py:129-132` `if result.returncode: # DEFERRED (per-run --max-videos budget) or DATE_FAILED exits 1: keep going, retry next window ... incomplete.append(an["short"])`<br>SOURCED `cbp_run.py:281-282` `if incomplete: raise FetchIncomplete(incomplete, (added, len(data["rows"]), rejected))`<br>SOURCED `cbp_run.py:348-354` `except FetchIncomplete as e: ... if not partial: write_stamp(...)` (stamp withheld when partial). | SOURCED `test_cbp_run.py:236-251` `test_main_saves_rows_but_withholds_stamp_when_fetch_incomplete`: verifies stamp withheld so next window retries deferred videos. |
| 4 | Row addition & quote-check: new videos checked verbatim, one bad quote rejects whole row | MATCH | SOURCED `cbp_run.py:9-10` `videos already in the store (or already rejected) are skipped; nothing older than 5 days is fetched. One LLM pass per new video.`<br>SOURCED `cbp_run.py:180-201` `build_row`: checks every quote via `vq.first_missing(q, norm_body)`; if bad, returns `None, "quote not in transcript"`, rejecting whole row.<br>SOURCED `cbp_run.py:254` `need_row = video[2] >= cutoff and (video[0], video[1]) not in known`<br>SOURCED `cbp_run.py:267-273` appends row to `data["rows"]` and increments `added`, or appends to `data["rejected"]` and increments `rejected`. | SOURCED `test_cbp_run.py:187-190` in `test_old_thesis_video_gets_a_verdict_not_a_row_and_bad_quote_is_dropped`: verifies row rejected/dropped on invalid quote. |
| 5 | Output format: one line with added rows, total rows, window end, rejected count | MATCH | SOURCED `cbp_run.py:11` `Output: one line "cbp: +<added> rows, <total> total, window end <date>[, <n> rejected]".`<br>SOURCED `cbp_run.py:357` `print("cbp: +%d rows, %d total, window end %s%s" % (added, total, end, ", %d rejected" % rejected if rejected else ""))` | SOURCED `test_cbp_run.py:250` asserts output format handling in `test_main_saves_rows_but_withholds_stamp_when_fetch_incomplete`. |
| 6 | Exit codes: exit 0 on success (including zero-row / not-due / partial), exit 1 on unhandled failure | MATCH | SOURCED `cbp_run.py:341-343` `if not window: print("cbp: not due"); return 0`<br>SOURCED `cbp_run.py:350-352` `except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e: print("cbp: FAILED...", file=sys.stderr); return 1`<br>SOURCED `cbp_run.py:360` returns `0` when completed (even with partial fetch or 0 rows added). | SOURCED `test_cbp_run.py:245-246` asserts `rc == 0` on partial fetch;<br>SOURCED `test_cbp_run.py:261` asserts `rc == 0` on clean run. |
| 7 | Zero-row run: cleanly processes 0 new rows, prunes rows older than 5 days, saves store/verdicts, prints line, rebuilds dashboard | MATCH | SOURCED `cbp_run.py:10` `nothing older than 5 days is fetched.`<br>SOURCED `cbp_run.py:274-278` prunes `data["rows"]` to `cutoff`, saves store and verdicts even when `added == 0`.<br>SOURCED `cbp_run.py:354-357` stamps window (if complete), rebuilds dashboard, and prints `cbp: +0 rows, <total> total...` without error. | SOURCED `test_cbp_run.py:56` asserts `(added, total) == (0, 0)` on zero-row run with successful verdict update and clean exit. |

## Detailed Clause Verification

### 1. Single-run Fetch & Store Architecture
- **Docstring**: SOURCED `cbp_run.py:1` (`Run CBP once: fetch new analyst videos (last 5 days), extract, quote-check, store. No scheduler, no daemon.`)
- **Code**: SOURCED `cbp_run.py:237-283` defines `run_once` performing discrete sequential steps: determining cutoff dates, loading store, fetching via `fetch(vcut, known)`, extracting via `extract()`, validating via `build_row()` and `build_verdict()`, pruning, and persisting store and verdicts.
- **Test**: SOURCED `test_cbp_run.py:51-53` demonstrates execution of `cbp_run.run_once` in isolation without long-running processes.
- **Verdict**: MATCH.

### 2. Actionable Analyst Loop
- **Docstring**: SOURCED `cbp_run.py:9` (`Only the actionable analysts in <CBP_HOME>/cbp_v2/analysts.json are fetched;`)
- **Code**: SOURCED `cbp_run.py:108-110` loads analysts configuration and filters `[a for a in cfg["analysts"] if a.get("enabled")]`. SOURCED `cbp_run.py:120-132` loops through each enabled analyst; if `result.returncode != 0`, appends to `incomplete` and continues loop.
- **Test**: SOURCED `test_cbp_run.py:227-234` (`test_fetch_new_continues_after_a_nonzero_analyst`) configures exit codes `{"A": 1, "B": 0, "C": 1}` and verifies `seen == ["A", "B", "C"]` and `got == ["A", "C"]`.
- **Verdict**: MATCH.

### 3. DEFERRED Handling & Window Retry
- **Docstring**: SOURCED `cbp_run.py:6-7` (`windows stay open for retries and catch-up.`)
- **Code**: SOURCED `cbp_run.py:129-131` notes returncode indicates `DEFERRED (per-run --max-videos budget) or DATE_FAILED exits 1`. SOURCED `cbp_run.py:281-282` raises `FetchIncomplete(incomplete, (added, len(data["rows"]), rejected))`. SOURCED `cbp_run.py:348-354` intercepts `FetchIncomplete`, saves row data, but bypasses `write_stamp(now, ...)` so `is_due(...)` remains due in the current window for subsequent retries.
- **Test**: SOURCED `test_cbp_run.py:236-251` (`test_main_saves_rows_but_withholds_stamp_when_fetch_incomplete`) asserts `rows.json` and `verdicts.json` exist, but `stamp.json` does not exist.
- **Verdict**: MATCH.

### 4. Row Addition and Quote Verification
- **Docstring**: SOURCED `cbp_run.py:9-10` (`videos already in the store (or already rejected) are skipped; nothing older than 5 days is fetched. One LLM pass per new video.`)
- **Code**: SOURCED `cbp_run.py:180-201` checks each quote against normalized body using `vq.first_missing(q, norm_body)`. If any quote is missing or empty, returns `(None, "quote not in transcript: ...")`. If valid, validates row with `cbp.validate_row(row)`. SOURCED `cbp_run.py:267-273` appends valid rows to `data["rows"]` (`added += 1`) and rejected rows to `data["rejected"]` (`rejected += 1`).
- **Test**: SOURCED `test_cbp_run.py:47-58` verifies unverified quotes are rejected/omitted.
- **Verdict**: MATCH.

### 5. Standard Output Line Format
- **Docstring**: SOURCED `cbp_run.py:11` (`Output: one line "cbp: +<added> rows, <total> total, window end <date>[, <n> rejected]".`)
- **Code**: SOURCED `cbp_run.py:356-357`:
  ```python
  end = now.astimezone(timezone.utc).date().isoformat()
  print("cbp: +%d rows, %d total, window end %s%s" % (added, total, end, ", %d rejected" % rejected if rejected else ""))
  ```
- **Test**: SOURCED `test_cbp_run.py:250` verifies stdout logging output during run.
- **Verdict**: MATCH.

### 6. Process Exit Codes
- **Docstring**: SOURCED `cbp_run.py:3-4` (`python scripts/dev/cbp_run.py --due`, `--force`) and implicit command protocol.
- **Code**: SOURCED `cbp_run.py:341-343` returns `0` if not due (`print("cbp: not due")`). SOURCED `cbp_run.py:350-352` catches exceptions (`OSError`, `ValueError`, `RuntimeError`, `subprocess.SubprocessError`), prints failure to `stderr`, and returns `1`. SOURCED `cbp_run.py:360` returns `0` on completed run.
- **Test**: SOURCED `test_cbp_run.py:246` and `test_cbp_run.py:261` verify return code is `0`.
- **Verdict**: MATCH.

### 7. Zero-row Run Behavior
- **Docstring**: SOURCED `cbp_run.py:10` (`nothing older than 5 days is fetched`) and SOURCED `cbp_run.py:11` (`Output: one line...`).
- **Code**: SOURCED `cbp_run.py:248` computes `known`. When no new videos are found, `local_videos(vcut)` produces no unhandled items; `added == 0`. SOURCED `cbp_run.py:274-278` prunes expired rows (`r["published"] >= cutoff`), persists data, stamps window (if complete), rebuilds dashboard, and prints `+0 rows`.
- **Test**: SOURCED `test_cbp_run.py:51-56` executes `run_once` resulting in `added == 0, total == 0` without error.
- **Verdict**: MATCH.
