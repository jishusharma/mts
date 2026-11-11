MATCH: 4, DIFF: 0, NOT_IN_DATA: 0

# Blind Read Report: sync.py health OLD-SHELL notes (f6824b1ef)
- Date: 2026-11-11
- Task: gemini-blind-read-old-shell-health-1111
- Auditor: Gemini (gemini-3.8-flash-low)
- Commit: `f6824b1ef8a7d3b455f019f8bbb89a6ed7130b3d`
- Scope In:
  - `scripts/dev/sync.py` (old_shell_notes and its caller in health; read)
  - `scripts/dev/bg_watch.py` (live_shells, SHELL_LIMIT_MIN; read)
  - `scripts/dev/test_old_shell_health.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-old-shell-health-1111.md` (new)

## Clause Verification Table

| # | Clause Specification | Status | SOURCED File & Line | Quote / Implementation Evidence |
|---|---|---|---|---|
| 1 | only bash/sh shells older than SHELL_LIMIT_MIN produce a note | MATCH | `scripts/dev/sync.py:717-718`, `scripts/dev/bg_watch.py:328`, `scripts/dev/bg_watch.py:339`, `scripts/dev/bg_watch.py:347` | SOURCED `scripts/dev/sync.py:717-718`: `return [f"NOTE OLD-SHELL pid {r['pid']} {r['age']:.0f}m > {bg_watch.SHELL_LIMIT_MIN}m: {' '.join(r['cmd'].split())[:70]} " f"-> stop it unless a task you own waits on it (bg_watch.py shells --kill)" for r in bg_watch.live_shells(lister=lister)]`<br>SOURCED `scripts/dev/bg_watch.py:328`: `SHELL_LIMIT_MIN = 30`<br>SOURCED `scripts/dev/bg_watch.py:339`: `out = [{**r, "age": (now - r["start"]) / 60} for r in rows if (now - r["start"]) / 60 > limit_min]`<br>SOURCED `scripts/dev/bg_watch.py:347`: `ps = ("Get-CimInstance Win32_Process \| Where-Object { $_.Name -in 'bash.exe','sh.exe' } \| ...` |
| 2 | the note names pid, age and a command cut to 70 chars | MATCH | `scripts/dev/sync.py:717-718` | SOURCED `scripts/dev/sync.py:717-718`: `f"NOTE OLD-SHELL pid {r['pid']} {r['age']:.0f}m > {bg_watch.SHELL_LIMIT_MIN}m: {' '.join(r['cmd'].split())[:70]} " f"-> stop it unless a task you own waits on it (bg_watch.py shells --kill)"` |
| 3 | a lister error yields no note and no exception | MATCH | `scripts/dev/sync.py:719-720`, `scripts/dev/bg_watch.py:337-338` | SOURCED `scripts/dev/sync.py:719-720`: `except Exception: return []`<br>SOURCED `scripts/dev/bg_watch.py:337-338`: `except Exception: return []` |
| 4 | the notes never change the health exit code | MATCH | `scripts/dev/sync.py:778-781` | SOURCED `scripts/dev/sync.py:778-781`: `for line in old_shell_notes(): print(line)` followed by `print(f"HEALTH: {len(issues)} issue(s)")` and `return len(issues)` (notes are printed directly and not appended to `issues`, leaving `len(issues)` unchanged) |

## Test Verification

- `scripts/dev/test_old_shell_health.py:9-20`:
  - Clause 1 & 2 tested:
    SOURCED `scripts/dev/test_old_shell_health.py:9-15`:
    ```python
    def test_old_flagged_young_not(self):
        now = time.time()
        rows = [{"pid": 7, "start": now - 12 * 3600, "cmd": "bash -c cat > m.md <<'EOF'"},
                {"pid": 8, "start": now - 60, "cmd": "bash -c git log"}]
        out = sync.old_shell_notes(lister=lambda: rows)
        self.assertEqual(len(out), 1, out)
        self.assertTrue(out[0].startswith("NOTE OLD-SHELL pid 7 720m > 30m"), out[0])
    ```
  - Clause 3 tested:
    SOURCED `scripts/dev/test_old_shell_health.py:17-20`:
    ```python
    def test_error_is_empty(self):
        def boom():
            raise OSError("x")
        self.assertEqual(sync.old_shell_notes(lister=boom), [])
    ```
  - Test run output:
    `python scripts/dev/test_old_shell_health.py`:
    ```
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.007s

    OK
    ```
