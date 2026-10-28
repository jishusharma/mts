# GPT cross-vendor review: refresh_main_checkout.py

Scope checked: `scripts/dev/refresh_main_checkout.py`, its test file, and the cited repository safety/ship rules. I listed the direct and post-step Git subcommands in the implementation before opening the test file. The test suite ran once from a scratch copy at `C:\Users\E-NGIN~1\AppData\Local\Temp\refresh-main-audit-df8wd67_`.

| Severity | File:line | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `scripts/dev/refresh_main_checkout.py:190-194` | Post-step failures are reported but not propagated; the CLI still emits the completion acknowledgment and returns success. | `post_steps()` accumulates `ok=False` on any nonzero child exit (`:162-175`), but `main()` ignores the return (`:192`), prints `ACK_LINE` (`:193`), then returns 0 (`:194`). A caller cannot distinguish failed `c_drive_guard`/`wt_maint` steps from a completed run, and the acknowledgment is misleading. | Capture `post_steps()` result; on failure return nonzero and do not print the completion acknowledgment. Add a focused test that stubs a failed post step and checks exit status and acknowledgment. |
| LOW | `scripts/dev/test_refresh_main_checkout.py:146` | One existing test uses a Git option unsupported by the installed Git version, so the prescribed suite does not fully pass in this environment. | Scratch run: 12 passed, 1 failed. `git stash show --include-untracked --name-only stash@{0}` exited with usage error in `test_protected_present_while_stash_kept_after_conflict`; this is a test-command compatibility issue, not evidence that the protected file entered the stash. | Use a version-compatible assertion, or gate the option based on Git capability. |

The goal’s data-preservation claims match the implementation: stash excludes are pathspec exclusions for all four protected prefixes (`refresh_main_checkout.py:18-19, 80-83, 124-126`); apply uses `stash push -u` without any stash-drop command (`:127-130, 143-160`); fast-forward and optional ordinary merge are the only merge modes (`:136-145`); there is no reset, rebase, or push call in this script. A failed stash pop returns while preserving the stash (`:148-159`).

The test suite exercises dry-run, protected paths, failed pop retention, fast-forward and diverged-branch preservation. The scratch run result was 12 passing / 1 failing for the compatibility reason above.

Verdict: FIX-FIRST
