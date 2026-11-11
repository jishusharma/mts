counts: MATCH=6 DIFF=2 NOT_IN_DATA=0 (sum 8)

# Gemini Blind Read: scripts/dev/dsa_watch.py against its docstring

- Date: 2026-11-11
- Card: `gemini-blind-read-dsa-watch-docstring-1111`
- Scope In:
  - `scripts/dev/dsa_watch.py` (read)
  - `scripts/dev/test_dsa_watch.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-dsa-watch-docstring-1111.md` (new)
- Scope Out: no edit to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit

## Summary Table

| Clause # | Docstring Clause Requirement | Implementation Status | Implementation Code (`scripts/dev/dsa_watch.py`) | Test Verification (`scripts/dev/test_dsa_watch.py`) |
|---|---|---|---|---|
| 1 | Zero-token DSA monitor for supervisor loop: zero-token DSA monitor (no LLM, no network) | MATCH | SOURCED `dsa_watch.py:1` `"""dsa_watch.py: zero-token DSA monitor for a supervisor loop (no LLM, no network).`<br>SOURCED `dsa_watch.py:9-14` standard library imports only (`argparse`, `json`, `os`, `sys`, `datetime`, `pathlib.Path`), no network/LLM calls. | SOURCED `test_dsa_watch.py:9-25` tests `summarize` purely in-memory using mock dictionaries without network or LLM. |
| 2 | CLI invocation and arguments: `python scripts/dev/dsa_watch.py [--stale-hours 3] [--audit F:/AIBridge/src/audit.jsonl]` | MATCH | SOURCED `dsa_watch.py:3` `python scripts/dev/dsa_watch.py [--stale-hours 3] [--audit F:/AIBridge/src/audit.jsonl]`<br>SOURCED `dsa_watch.py:55-59` `ap.add_argument("--stale-hours", type=float, default=3.0)` and `ap.add_argument("--audit", default="F:/AIBridge/src/audit.jsonl")` (also accepts `--queue`, default `MyTradingSys/system/desk_queue`). | SOURCED `test_dsa_watch.py:12` passes `stale_h=3` explicitly to `summarize(rows, NOW, 3)`. |
| 3 | Per-target output line: prints one line per DSA target (DSA, DSA-NB, DSA-NUC) | MATCH | SOURCED `dsa_watch.py:5` `Prints one line per DSA target (DSA, DSA-NB, DSA-NUC): pending, taken, oldest-pending age, and a verdict.`<br>SOURCED `dsa_watch.py:17` `TARGETS = ("DSA", "DSA-NB", "DSA-NUC")`<br>SOURCED `dsa_watch.py:68-69` iterates over `summarize` for each of the 3 targets and prints formatted line. | SOURCED `test_dsa_watch.py:12-24` checks outputs for keys `DSA-NUC`, `DSA-NB`, and `DSA`. |
| 4 | Line metrics format: pending, taken, oldest-pending age, and a verdict | MATCH | SOURCED `dsa_watch.py:5` `pending, taken, oldest-pending age, and a verdict.`<br>SOURCED `dsa_watch.py:41` `out.append((t, len(pend), len(taken), oldest, verdict))`<br>SOURCED `dsa_watch.py:69` `print(f"{t}: pending={pend} taken={taken} oldest_pending={oldest:.1f}h {verdict}")` | SOURCED `test_dsa_watch.py:13-14` validates tuple contents indexing `got["DSA-NUC"][4]` (verdict). |
| 5 | Exit 0 criteria: Exit 0 = every bridge with work is moving | MATCH | SOURCED `dsa_watch.py:6` `Exit 0 = every bridge with work is moving`<br>SOURCED `dsa_watch.py:67-73` `bad = False ... bad = bad or verdict == "STALLED" ... return 1 if bad else 0`. If no target is STALLED (either EMPTY or OK), returns 0. | SOURCED `test_dsa_watch.py:16-25` tests scenarios where targets with work are OK (`got["DSA-NB"][4] == "OK"` and `got["DSA"][4] == "OK"`). |
| 6 | Exit 1 criteria: 1 = at least one STALLED/IDLE-WITH-WORK line | DIFF | SOURCED `dsa_watch.py:6` `1 = at least one STALLED/IDLE-WITH-WORK line.`<br>SOURCED `dsa_watch.py:35-40` verdicts produced by `summarize()` are only `EMPTY`, `STALLED`, or `OK`. `IDLE-WITH-WORK` is never generated anywhere in the codebase. Line 70 checks only `bad = bad or verdict == "STALLED"`. | SOURCED `test_dsa_watch.py:13` tests verdict `"STALLED"`; no test exists for `"IDLE-WITH-WORK"`. |
| 7 | Stop-guard integration and supervisor recommendation: Run it from the stop-guard; only a non-zero exit needs a Claude look | MATCH | SOURCED `dsa_watch.py:6-7` `Run it from the stop-guard; only a non-zero exit needs a Claude look.`<br>SOURCED `dsa_watch.py:73` returns exit code 0 or 1, allowing shell / stop-guard callers to trigger supervisor action on exit code 1. | SOURCED `test_dsa_watch.py:1-28` verifies component functions supporting this design. |
| 8 | Host bridge audit file read and format: The audit file is read for this host's bridge only (last call age) | DIFF | SOURCED `dsa_watch.py:7` `The audit file is read for this host's bridge only (last call age).`<br>SOURCED `dsa_watch.py:45-51` in `audit_age(path, now)` reads the last line of `path` without filtering by host or target bridge identity. Also, the output line printed at line 72 is `bridge_last_call=...`, which is an extra summary line not mentioned in the docstring line format description. | SOURCED `test_dsa_watch.py:1-28` contains no tests for `audit_age` or `bridge_last_call`. |

## Detailed Clause Verification

### 1. Zero-Token Supervisor Monitor
- **Docstring**: SOURCED `dsa_watch.py:1` (`zero-token DSA monitor for a supervisor loop (no LLM, no network)`).
- **Code**: SOURCED `dsa_watch.py:9-14` uses only standard library packages. SOURCED `dsa_watch.py:62-66` inspects local JSON files in `QUEUE` (`MyTradingSys/system/desk_queue`), and SOURCED `dsa_watch.py:45-51` inspects a local audit file. No API or network socket is initialized.
- **Test**: SOURCED `test_dsa_watch.py:9-25` performs unit checks completely offline.
- **Verdict**: MATCH.

### 2. CLI Invocation and Default Parameters
- **Docstring**: SOURCED `dsa_watch.py:3` (`python scripts/dev/dsa_watch.py [--stale-hours 3] [--audit F:/AIBridge/src/audit.jsonl]`).
- **Code**: SOURCED `dsa_watch.py:55-59` defines `ArgumentParser` arguments `--stale-hours` defaulting to `3.0` and `--audit` defaulting to `"F:/AIBridge/src/audit.jsonl"`.
- **Test**: SOURCED `test_dsa_watch.py:12` passes `3` as `stale_h` to `summarize()`.
- **Verdict**: MATCH.

### 3. Per-Target Output Lines
- **Docstring**: SOURCED `dsa_watch.py:5` (`Prints one line per DSA target (DSA, DSA-NB, DSA-NUC)`).
- **Code**: SOURCED `dsa_watch.py:17` defines `TARGETS = ("DSA", "DSA-NB", "DSA-NUC")`. SOURCED `dsa_watch.py:29` and `dsa_watch.py:68-69` iterates through each target in `TARGETS` and prints its line.
- **Test**: SOURCED `test_dsa_watch.py:12-24` checks outputs across `DSA-NUC`, `DSA-NB`, and `DSA`.
- **Verdict**: MATCH.

### 4. Output Metric Format
- **Docstring**: SOURCED `dsa_watch.py:5` (`pending, taken, oldest-pending age, and a verdict`).
- **Code**: SOURCED `dsa_watch.py:41` appends `(t, len(pend), len(taken), oldest, verdict)` in `summarize`. SOURCED `dsa_watch.py:69` prints `f"{t}: pending={pend} taken={taken} oldest_pending={oldest:.1f}h {verdict}"`.
- **Test**: SOURCED `test_dsa_watch.py:13-14` tests the returned verdict at index 4 for targets.
- **Verdict**: MATCH.

### 5. Exit Code 0 Semantics
- **Docstring**: SOURCED `dsa_watch.py:6` (`Exit 0 = every bridge with work is moving`).
- **Code**: SOURCED `dsa_watch.py:35-40` marks targets with work within `stale_h` as `"OK"`, or targets with no pending/taken work as `"EMPTY"`. SOURCED `dsa_watch.py:70-73` evaluates `bad = bad or verdict == "STALLED"` and returns 0 if `bad` is False.
- **Test**: SOURCED `test_dsa_watch.py:19` and `test_dsa_watch.py:24` test that pending work within stale threshold or taken work yields `"OK"`.
- **Verdict**: MATCH.

### 6. Exit Code 1 Semantics & Verdict Set
- **Docstring**: SOURCED `dsa_watch.py:6` (`1 = at least one STALLED/IDLE-WITH-WORK line`).
- **Code**: SOURCED `dsa_watch.py:35-40` evaluates verdicts strictly as:
  ```python
  if not pend and not taken:
      verdict = "EMPTY"
  elif oldest > stale_h:
      verdict = "STALLED"
  else:
      verdict = "OK"
  ```
  `IDLE-WITH-WORK` is never computed or returned. SOURCED `dsa_watch.py:70` only flags `verdict == "STALLED"`.
- **Test**: SOURCED `test_dsa_watch.py:13` verifies `"STALLED"`. There is no test or mention of `"IDLE-WITH-WORK"`.
- **Verdict**: DIFF.

### 7. Supervisor / Stop-Guard Integration
- **Docstring**: SOURCED `dsa_watch.py:6-7` (`Run it from the stop-guard; only a non-zero exit needs a Claude look.`).
- **Code**: SOURCED `dsa_watch.py:73` returns 1 when any target is STALLED, 0 otherwise, providing clean binary status for automation scripts.
- **Test**: SOURCED `test_dsa_watch.py:9-25` tests the verdict conditions that dictate the exit code.
- **Verdict**: MATCH.

### 8. Host Audit File Handling
- **Docstring**: SOURCED `dsa_watch.py:7` (`The audit file is read for this host's bridge only (last call age).`).
- **Code**: SOURCED `dsa_watch.py:45-51` in `audit_age` reads the last line of `a.audit` and parses timestamp `ts`:
  ```python
  last = Path(path).read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1]
  d = _ts(json.loads(last.split("\t", 1)[-1]).get("ts", "")[:26] + "+00:00")
  ```
  It does not inspect or filter by host name or bridge identifier; it assumes the audit file contains records for this host only. Furthermore, line 72 prints an extra non-target line `bridge_last_call=...`.
- **Test**: SOURCED `test_dsa_watch.py:1-28` does not cover `audit_age` or `--audit`.
- **Verdict**: DIFF.
