# RV03 [HIGH] sync.py tidy, claim/release, hot-file auto-resolve (b3dadf1, 28e1b5d)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV03. Report: `MyTradingSys/research/revalidation/RV03_<UTC date>.md`.

Scope in: scripts/dev/sync.py, scripts/dev/test_sync.py, MyTradingSys/system/PARALLEL.md, MyTradingSys/system/claims/.
Scope out: running `tidy --apply` anywhere real; run it only inside a throwaway repo built by the test helpers.
Why risky: `tidy --apply` deletes directories; hot-file auto-resolve silently picks origin's text.
Checks (each one a failing-then-passing test written in the scratchpad, shipped to scripts/dev/test_sync.py only on request):
1. A worktree just made by `new_worktree` (clean, branch tip == origin/fast-track) and one that holds a live claim: does `tidy --apply`
   remove it? (test_tidy_removes_only_clean_shipped_session_worktrees asserts the removal of exactly such a tree.)
2. Ignored but valuable files (`.gitignore`d data, e.g. Dumps/, runtime_data/): the porcelain status listing omits them; does
   `git worktree remove` delete them? Name every ignored path pattern in .gitignore that holds non-reproducible data.
3. Another tree's current directory / running process inside the worktree: any guard?
4. `claim`: two sessions claim the same slug within one fetch window; claim of a slug that differs only by case or punctuation.
5. Hot-file auto-resolve: when both sides edited NEXT_SESSION.md, local edit is discarded: is it logged anywhere the editor sees?
Already known (confirm or refute): (a) checks 1 and 2 are true: the shipped test encodes the removal; on JIS-NUC 2026-10-12 a dry
run listed `mts-jis-nuc-s1012-164721` (last commit 22:23 +0530, hours-old) as removable; (b) 1m klines for Q33 were fetched into a
gitignored Dumps/ of a session worktree and are no longer on the machine.
