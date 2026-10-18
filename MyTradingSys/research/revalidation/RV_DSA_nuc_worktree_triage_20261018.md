# JIS-NUC worktree triage (read only), 2026-10-18

| tree | state | verdict |
|---|---|---|
| mts-dsa (jisnb/dsa) | STATUS.md modified; 3 untracked files (B184 item, BETA_RESULTS.md, beta_sweep.py) already on origin/fast-track | DISCARD-CANDIDATE for the 3 untracked; ASK owner on STATUS.md |
| mts-krown | not a git repo (broken .git, 16 entries incl. _archive, my_charts) | ASK (BROKEN per sync.py where) |
| mts-nuc-b172 (jis-nuc/b172-trim) | clean, 0 commits ahead | DISCARD-CANDIDATE |
| mts-nuc-recover (jis-nuc/recover-s1013) | clean, 0 commits ahead | DISCARD-CANDIDATE |
| mts-jis-nuc-s1012-181720, -194730, mts-codex, mts-codex-lab, mts-levels-quick | directories no longer exist | gone |
| BinanceDataFeed (fast-track, live tree) | 6 modified, 1 untracked dir, 1 commit 7ffb330a ahead (mts_signal git window fix; not on origin by cherry) | SHIP by owners (live tree; not touched) |
