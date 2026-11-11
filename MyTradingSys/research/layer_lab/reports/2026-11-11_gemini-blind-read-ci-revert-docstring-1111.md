MATCH=8 DIFF=0 NOT_IN_DATA=0

# Gemini Blind Read: ci_revert.py Docstring & Test Audit

- **Card**: `gemini-blind-read-ci-revert-docstring-1111`
- **Date**: 2026-11-11 UTC
- **Auditor**: Gemini (`gemini-3.8-flash-low`, throwaway worktree `gemini-q/gemini-blind-read-ci-revert-docstring-1111`)
- **Scope In**:
  - `scripts/dev/ci_revert.py` (read)
  - `scripts/dev/test_ci_revert.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-ci-revert-docstring-1111.md` (new)
- **Scope Out**:
  - No edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Clause Verification Table

| # | Docstring Clause Requirement | Status | SOURCED Docstring file:line | SOURCED Code & Test file:line | Implementation Evidence & Verification Quotes |
|---|---|---|---|---|---|
| 1 | Dry run / plan mode: `python scripts/dev/ci_revert.py` dry run prints plan or why it refuses, changing nothing | MATCH | SOURCED `scripts/dev/ci_revert.py:3` (`"    python scripts/dev/ci_revert.py           dry run: print the plan (or why it refuses), change nothing"`) | SOURCED `scripts/dev/ci_revert.py:81-84`, SOURCED `scripts/dev/test_ci_revert.py:55-63` | SOURCED `scripts/dev/ci_revert.py:81-84`: `print(f"PLAN: git revert --no-commit {sha}; commit 'Result: reverts {sha} (CI red)'; {' '.join(SHIP_CMD[1:])}")` and `if "--apply" not in argv: print("dry run: nothing changed (add --apply)"); return 0`. Verified in test SOURCED `scripts/dev/test_ci_revert.py:55-63` (`test_plan_names_A_and_dry_run_makes_no_commit`), asserting plan output and `_g(r, "rev-parse", "HEAD") == head and _g(r, "status", "--porcelain") == ""`. |
| 2 | Apply mode: `python scripts/dev/ci_revert.py --apply` reverts in this worktree, then runs `sync.py ship --fix-ci` | MATCH | SOURCED `scripts/dev/ci_revert.py:4` (`"    python scripts/dev/ci_revert.py --apply   git revert it in THIS worktree, then sync.py ship --fix-ci"`) | SOURCED `scripts/dev/ci_revert.py:20`, SOURCED `scripts/dev/ci_revert.py:85`, SOURCED `scripts/dev/test_ci_revert.py:102-113` | SOURCED `scripts/dev/ci_revert.py:20`: `SHIP_CMD = [sys.executable, "scripts/dev/sync.py", "ship", "--fix-ci"]`. SOURCED `scripts/dev/ci_revert.py:85`: `return apply(repo, sha, ship or _ship)`. Verified in test SOURCED `scripts/dev/test_ci_revert.py:102-113` (`test_apply_makes_one_revert_commit_and_ships_without_force`), asserting revert commit creation and invocation of ship command. |
| 3 | First red commit selection: Breaking commit is the first red run of the streak trunk is still in (`mts_doctor.first_red_sha` over `ci_fetch`) | MATCH | SOURCED `scripts/dev/ci_revert.py:6` (`"The breaking commit = the first red run of the streak trunk is still in (mts_doctor.first_red_sha over ci_fetch)."`) | SOURCED `scripts/dev/ci_revert.py:68-72`, SOURCED `scripts/dev/test_ci_revert.py:48-53` | SOURCED `scripts/dev/ci_revert.py:68-72`: `runs = D.ci_fetch()`, `sha = D.first_red_sha(runs, gated=gated or (lambda s: D.ci_gated(s, repo)))`. SOURCED `scripts/dev/test_ci_revert.py:48-53` (`test_first_red_sha_names_the_first_red_of_the_open_streak`) verifies streak logic: `D.first_red_sha(runs, gated=GATED) == "a" * 40`. |
| 4 | Refusal when merge commit: Refuses and prints manual steps when breaking commit is a merge commit | MATCH | SOURCED `scripts/dev/ci_revert.py:6-8` (`"Refuses, printing the manual steps, when that commit is a merge..."`) | SOURCED `scripts/dev/ci_revert.py:31-32`, SOURCED `scripts/dev/ci_revert.py:76-80`, SOURCED `scripts/dev/test_ci_revert.py:65-76` | SOURCED `scripts/dev/ci_revert.py:31-32`: `if len(_git(repo, "rev-list", "--parents", "-n", "1", sha).stdout.split()) > 2: return f"{sha[:8]} is a merge commit (revert by hand: git revert -m 1 {sha})"`. SOURCED `scripts/dev/ci_revert.py:78-80` prints `REFUSED: ...` and manual instructions. Verified in SOURCED `scripts/dev/test_ci_revert.py:65-76` (`test_merge_commit_refused`). |
| 5 | Refusal when not on trunk: Refuses and prints manual steps when breaking commit is not on `origin/fast-track` | MATCH | SOURCED `scripts/dev/ci_revert.py:6-8` (`"Refuses, printing the manual steps, when that commit... is not on origin/fast-track..."`) | SOURCED `scripts/dev/ci_revert.py:29-30`, SOURCED `scripts/dev/ci_revert.py:76-80`, SOURCED `scripts/dev/test_ci_revert.py:87-94` | SOURCED `scripts/dev/ci_revert.py:29-30`: `if _git(repo, "merge-base", "--is-ancestor", sha, TRUNK).returncode != 0: return f"{sha[:8]} is not on {TRUNK}"`. Verified in test SOURCED `scripts/dev/test_ci_revert.py:87-94` (`test_not_on_trunk_refused`). |
| 6 | Refusal when later trunk commits touch same files: Refuses when later commits on `origin/fast-track` touch the same files | MATCH | SOURCED `scripts/dev/ci_revert.py:7-8` (`"...or later trunk commits touch the same files (a revert would undo or clash with them: a person decides)."`)| SOURCED `scripts/dev/ci_revert.py:33-36`, SOURCED `scripts/dev/test_ci_revert.py:78-85` | SOURCED `scripts/dev/ci_revert.py:33-36`: diffs files modified by `sha` against `TRUNK` via `_git(repo, "diff", "--name-only", sha, TRUNK, "--", *files)`; returns `f"later commits on {TRUNK} touch the same files: {', '.join(later[:5])}"`. Verified in test SOURCED `scripts/dev/test_ci_revert.py:78-85` (`test_later_commit_touching_same_files_refused`). |
| 7 | Safety constraints: Never forces, rebases or resets; run by hand only, never scheduled or hooked | MATCH | SOURCED `scripts/dev/ci_revert.py:8-9` (`"Never forces, rebases or resets; run by hand only, never scheduled or hooked (SCHEDULING_POLICY.md)."`)| SOURCED `scripts/dev/ci_revert.py:20`, SOURCED `scripts/dev/test_ci_revert.py:112` | SOURCED `scripts/dev/ci_revert.py:20`: `SHIP_CMD = [sys.executable, "scripts/dev/sync.py", "ship", "--fix-ci"]`. No git rebase, reset, or push --force is invoked anywhere in the script. SOURCED `scripts/dev/test_ci_revert.py:112` explicitly asserts: `assert not any(w in " ".join(CR.SHIP_CMD) for w in ("--force", "rebase", "reset"))`. |
| 8 | Conflict handling: Revert conflict runs `git revert --abort` and leaves worktree unchanged | MATCH | SOURCED `scripts/dev/ci_revert.py:9` (`"A revert conflict runs git revert --abort and leaves the tree as it was."`) | SOURCED `scripts/dev/ci_revert.py:44-47`, SOURCED `scripts/dev/test_ci_revert.py:115-123` | SOURCED `scripts/dev/ci_revert.py:44-47`: `if _git(repo, "revert", "--no-commit", sha).returncode != 0: _git(repo, "revert", "--abort"); print(f"REFUSED: revert of {sha[:8]} conflicts in this worktree; aborted, tree unchanged. Revert by hand: git revert {sha}"); return REFUSED`. Verified in test SOURCED `scripts/dev/test_ci_revert.py:115-123` (`test_apply_conflict_aborts_and_leaves_tree_clean`). |

---

## Detailed Findings & Revert Commit Message Format

### Revert Commit Structure
In apply mode, the commit message constructed by `ci_revert.py` conforms to MTS protocol:
- **Title line**: `Revert "<subject>"` (SOURCED `scripts/dev/ci_revert.py:48-49`)
- **Body**: `This reverts commit <sha>.` (SOURCED `scripts/dev/ci_revert.py:49`)
- **Result line**: `Result: reverts <sha> (CI red)` (SOURCED `scripts/dev/ci_revert.py:49`)
- **Next line**: `Next: END: trunk back to the last green code` (SOURCED `scripts/dev/ci_revert.py:49`)
Verified in SOURCED `scripts/dev/test_ci_revert.py:109-110`.
