# testgap-nowin-hook-gemini3-1114 — NO GAP

**Status:** `NO GAP` (stopped at Step 1 per card rule: *"grep tests first; stop with NO GAP if one exists"*).

## Findings

- `git grep -n "nowin_hook" scripts MyTradingSys` found an existing test file: [`scripts/dev/test_nowin_hooks.py`](../../../../scripts/dev/test_nowin_hooks.py) (SOURCED: `scripts/dev/test_nowin_hooks.py:10`, `LAUNCHER = HERE / "nowin_hook.py"`).
- It is registered in [`scripts/dev/run_all_tests.py`](../../../../scripts/dev/run_all_tests.py) (SOURCED: `scripts/dev/run_all_tests.py:64`, `"scripts/dev/test_nowin_hooks.py",`).
- Existing test coverage in `scripts/dev/test_nowin_hooks.py`:
  1. `test_every_repo_hook_goes_through_the_windowless_launcher` (`scripts/dev/test_nowin_hooks.py:21-23`): verifies `.claude/settings.json` hooks do not invoke console `python`/`pythonw` directly.
  2. `test_hook_sh_falls_back_to_python_without_pythonw` (`scripts/dev/test_nowin_hooks.py:26-29`): verifies `scripts/dev/hook.sh` references `command -v pythonw`, `nowin_hook.py`, `exec python`, and uses LF line endings.
  3. `test_launcher_relays_stdin_stdout_stderr_and_exit_code` (`scripts/dev/test_nowin_hooks.py:32-37`): runs `scripts/dev/nowin_hook.py` against a child script with `input=b"abc"` and verifies `(r.stdout, r.stderr, r.returncode) == (b"ABC", b"E", 2)`.
  4. `test_launcher_without_script_exits_2` (`scripts/dev/test_nowin_hooks.py:40-43`): runs `scripts/dev/nowin_hook.py` with no script argument and verifies `r.returncode == 2`.

## Verification

- Command: `python -m pytest scripts/dev/test_nowin_hooks.py`
- Output: `4 passed in 0.35s` (SOURCED: command output).
