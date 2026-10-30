# B206 - Role worktree starts stale and the hook says so on every prompt: the Eagle_Eyes worktree was 1016 commits behi

Filed: 2026-10-26
Status: OPEN
Priority: LOW
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B206 | 2026-10-26 | OPEN | LOW | Role worktree starts stale and the hook says so on every prompt: the Eagle_Eyes worktree was 1016 commits behind origin/fast-track (58 h), and the session cannot run `git merge origin/fast-track` in it (auto-mode classifier denied the merge on 10-26 ~20:40Z; the sanctioned path is `sync.py start`, which the role session has already used). Result: STATUS.md, cards and QUICK_ANSWERS read in the worktree are 58 h old. Also the local clock is past UTC midnight (hooks print 2026-10-27 while the market log is UTC 10-26). Fix: sync.py start for a role session fast-forwards the worktree; hooks print UTC date and local date together. | TRUNK LAG hook line on every prompt; merge denied by auto mode classifier | |
