# Blind read: scripts/dev/refresh_main_checkout.py vs test_refresh_main_checkout.py

Reader: Builder, 2026-11-06. Code read first (209 lines), tests mapped after. Protected prefixes (line 23): execution/HALT*,
execution/AUTO_PAUSE*, runtime, .mts_live. Test run: `python -m pytest scripts/dev/test_refresh_main_checkout.py -q` -> **15 passed in 146.59s**.

Protection mechanism: is_protected (l.38) filters protected paths out of staged/unstaged/untracked, so they never make the tree "dirty";
the stash command (l.138) adds `:(exclude)<prefix>` pathspecs (stash_excludes l.28; gitignored prefixes skipped because git rejects
an ignored path in a pathspec). Merge never touches untracked/ignored files except by git's own overwrite refusal.

| path | code line | covering test | status |
|---|---|---|---|
| Dry run never stashes/merges | l.126-135 | test_dry_run_changes_nothing, test_cli_default_is_dry | COVERED |
| Dry run lists protected, leaves in place | l.106 | test_dry_run_lists_protected | COVERED |
| Stash of dirty work excludes untracked HALT/AUTO_PAUSE/runtime | l.138 + stash_excludes | test_apply_never_stashes_protected_untracked | COVERED |
| Only protected files dirty -> no stash created | l.124-125 | test_only_protected_dirty_means_no_stash | COVERED |
| ff-only merge then pop restores dirty work | l.144, 159, 162-168 | test_apply_stashes_ffs_and_restores | COVERED |
| Pop conflict keeps stash, protected files untouched and absent from stash | l.163-167 | test_conflicting_pop_keeps_stash, test_protected_present_while_stash_kept_after_conflict | COVERED |
| Diverged: needs wip branch, wip must exist, must contain HEAD | l.108-118 | test_diverged_needs_wip_branch_and_never_resets, test_wip_branch_missing_blocks | COVERED (HEAD-not-in-wip branch l.115 only by implication: UNCOVERED separately) |
| Diverged merge with --merge-if-diverged succeeds, local commits kept | l.146-153 | test_diverged_needs_wip_branch_and_never_resets | COVERED |
| Gitignored protected dir (.mts_live) with a stash and merge | l.30-34 | test_apply_with_gitignored_protected_dir | COVERED |
| Upstream adds a path equal to a local untracked protected file: merge refuses, local HALT kept | l.144 (git refusal) l.155-157 | test_upstream_adding_same_protected_path_aborts_merge | COVERED |
| is_protected prefix rules (HALT_DAILY_LOSS yes, live_runner.py no) | l.38-40 | test_is_protected | COVERED |
| classify porcelain | l.48-62 | test_classify | COVERED |
| Post step failure fails CLI, no ACK | l.200-203 | test_failed_post_steps_fail_cli | COVERED (post_steps body l.172-184 itself UNCOVERED) |
| Conflicting diverged merge is aborted (`merge --abort`), stash kept | l.147-152 | none | UNCOVERED |
| Wrong branch checked out -> STOP | l.79-81 | none | UNCOVERED |
| `git fetch origin` fails / origin/<branch> missing -> STOP | l.82-90 | none (tests use fetch against a real bare origin) | UNCOVERED |
| Stash failure -> STOP, tree unchanged | l.139-141 | none | UNCOVERED |
| ff-only fails while not diverged (e.g. dirty overlap from excluded protected tracked file) | l.154-157 | partially via the HALT-collision test (git refuses merge) | COVERED indirectly |
| Tracked protected file modified locally and upstream also changes it | l.144 | none; git refuses the merge (safe) but no test | UNCOVERED |

Risk read (no code line is wrong): the protected-state loss paths are (a) stash (excluded, tested), (b) merge overwrite (git refuses
for local changes, tested for the untracked case only), (c) pop (cannot touch excluded files). Over-matching prefix
`MyTradingSys/runtime2` would also be protected (fail-safe direction). The uncovered rows are error/abort branches that leave the tree
as is; none writes protected state.

Counts: 14 covered or indirectly covered, 6 UNCOVERED (merge-abort, wrong branch, fetch/remote missing, stash failure, tracked-protected collision, HEAD-not-in-wip).
Every claim above matches the code; the test file's own claims (protected untracked never stashed; HALT survives conflict) hold at the cited lines.

VERDICT: MATCH
