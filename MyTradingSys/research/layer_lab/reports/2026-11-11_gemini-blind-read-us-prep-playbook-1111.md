MATCH: 5, DIFF: 0, NOT_IN_DATA: 0

# Blind Read Report: us_prep.py Live Aid Playbook Rebuild Wiring (commit 33d9eaf0c)
- Date: 2026-11-11
- Task: gemini-blind-read-us-prep-playbook-1111
- Target: `scripts/dev/us_prep.py` and `scripts/dev/test_us_prep.py` (shipped `33d9eaf0c25a`)
- Auditor: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-blind-read-us-prep-playbook-1111`)

## Clause Verification Table

| # | Clause Specification | Status | SOURCED File & Line | Quote / Implementation Evidence |
|---|---|---|---|---|
| 1 | P1, P2 and P3 each call build_playbook | MATCH | `scripts/dev/us_prep.py:361-375`, `scripts/dev/test_us_prep.py:240-253` | SOURCED `scripts/dev/us_prep.py:367-374`: `if a.phase == "P4": ... OUTDIR.mkdir ... print(render_p4_md(res))` / `else:` / `    print(build_playbook())`<br>Phase choices: `scripts/dev/us_prep.py:36`: `PHASE_UTC = {"P1": (9, 0), "P2": (13, 15), "P3": (14, 45), "P4": (21, 15)}`<br>SOURCED test: `scripts/dev/test_us_prep.py:249-253`: `for ph in ("P1", "P2", "P3"): up.main(["--phase", ph, ...])` / `assert len(seen) == 3 ... up.main(["--phase", "P4", ...])` / `assert len(seen) == 3` |
| 2 | main_checkout resolves the main checkout from git rev-parse --git-common-dir | MATCH | `scripts/dev/us_prep.py:276-285`, `scripts/dev/test_us_prep.py:228-238` | SOURCED `scripts/dev/us_prep.py:276-284`: `def main_checkout(root=ROOT, run=subprocess.run):` / `    try:` / `        r = run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, timeout=20, **_quiet())` / `        top = Path(r.stdout.strip()).parent` / `        return top if r.returncode == 0 and r.stdout.strip() and (top / PLAYBOOK_REL).is_dir() else None` |
| 3 | playbook_data.js is copied there only after a successful build | MATCH | `scripts/dev/us_prep.py:293-305`, `scripts/dev/test_us_prep.py:198-226` | SOURCED `scripts/dev/us_prep.py:293-305`: `r = run([sys.executable, str(root / PLAYBOOK_REL / "daily_playbook.py")], cwd=str(root), capture_output=True, text=True, timeout=300, **_quiet())` / `if r.returncode != 0 or not js.exists(): ... return f"PLAYBOOK FAILED: exit {r.returncode}: {tail[:200]}"` / `...` / `shutil.copyfile(js, dest)` / `return f"PLAYBOOK built and copied to {dest}"`<br>SOURCED test: `scripts/dev/test_us_prep.py:214-226`: verified that failure leaves main untouched |
| 4 | any build or copy error prints a PLAYBOOK FAILED line and never stops the prep | MATCH | `scripts/dev/us_prep.py:289`, `scripts/dev/us_prep.py:295-297`, `scripts/dev/us_prep.py:306-307`, `scripts/dev/us_prep.py:374-375`, `scripts/dev/test_us_prep.py:213-226` | SOURCED `scripts/dev/us_prep.py:289`: `Returns one status line and never raises: the brief must print even when the playbook cannot be built.`<br>SOURCED `scripts/dev/us_prep.py:295-297`: `if r.returncode != 0 or not js.exists(): ... return f"PLAYBOOK FAILED: exit {r.returncode}: {tail[:200]}"`<br>SOURCED `scripts/dev/us_prep.py:306-307`: `except Exception as exc: return f"PLAYBOOK FAILED: {type(exc).__name__}: {str(exc)[:200]}"`<br>SOURCED `scripts/dev/us_prep.py:374-375`: `print(build_playbook())` / `print("wrote", p)` |
| 5 | the subprocess calls pass CREATE_NO_WINDOW | MATCH | `scripts/dev/us_prep.py:272-273`, `scripts/dev/us_prep.py:280`, `scripts/dev/us_prep.py:294` | SOURCED `scripts/dev/us_prep.py:272-273`: `def _quiet(): return {"creationflags": 0x08000000} if sys.platform == "win32" else {}  # CREATE_NO_WINDOW: no console flash`<br>SOURCED `scripts/dev/us_prep.py:280`: `r = run(["git", "-C", str(root), ...], capture_output=True, text=True, timeout=20, **_quiet())`<br>SOURCED `scripts/dev/us_prep.py:294`: `r = run([sys.executable, str(root / PLAYBOOK_REL / "daily_playbook.py")], cwd=str(root), capture_output=True, text=True, timeout=300, **_quiet())` (where 0x08000000 is `subprocess.CREATE_NO_WINDOW`) |

## Verification Details

- **Clause 1 (P1, P2 and P3 each call build_playbook)**:
  `us_prep.py:361` parses `--phase` which is restricted to `PHASE_UTC` keys (`P1`, `P2`, `P3`, `P4`). At line 367, if `a.phase == "P4"`, it scores P4. In the `else:` branch (`us_prep.py:373-374`), it calls `build_playbook()` and prints the returned string. Thus, P1, P2, and P3 each execute `print(build_playbook())`. This is directly tested in `test_us_prep.py:240-253` (`test_main_runs_playbook_on_p1_to_p3_not_p4`). Verdict: MATCH.

- **Clause 2 (main_checkout resolves main checkout from git rev-parse --git-common-dir)**:
  `us_prep.py:276-285` executes `git -C <root> rev-parse --path-format=absolute --git-common-dir`. It obtains the git common dir and resolves `top = Path(r.stdout.strip()).parent`. If returncode is 0, stdout non-empty, and `(top / PLAYBOOK_REL).is_dir()`, it returns `top`. Verdict: MATCH.

- **Clause 3 (playbook_data.js is copied there only after a successful build)**:
  `us_prep.py:293-305` first runs `daily_playbook.py`. If `r.returncode != 0 or not js.exists()`, it returns a failure string without copying anything. Only when successful does it proceed to check `main_root` and invoke `shutil.copyfile(js, dest)` (or return in-place build message if `dest.resolve() == js.resolve()`). Tested by `test_us_prep.py:213-226` confirming stale `playbook_data.js` remains untouched on failure. Verdict: MATCH.

- **Clause 4 (any build or copy error prints a PLAYBOOK FAILED line and never stops prep)**:
  `us_prep.py:287-308` wraps all execution in a try-except block catching `Exception`, formatting exceptions as `PLAYBOOK FAILED: <type>: <msg>`. Failed process exit or missing js outputs `PLAYBOOK FAILED: exit <rc>: <tail>`. Line 374 prints the returned string and continues to line 375 (`print("wrote", p)`), ensuring `us_prep` never crashes or halts prep. Verdict: MATCH.

- **Clause 5 (subprocess calls pass CREATE_NO_WINDOW)**:
  `us_prep.py:272-273` defines `_quiet()` returning `{"creationflags": 0x08000000}` on `win32` (`0x08000000` is `CREATE_NO_WINDOW`). Both `main_checkout` at line 280 and `build_playbook` at line 294 pass `**_quiet()` to `run(...)`. Verdict: MATCH.
