# Worktree leftovers, swept 2026-10-15 (operator: "clean everything, leave nothing behind")

Everything below was removed from its worktree and kept in the local bare repo `F:/MTS_backup.git` (remote `backup`, private:
it holds runtime files that must never go to the public origin). Nothing was deleted without a copy.

Restore a set: `git fetch backup refs/leftovers/<name>:refs/heads/restore-<name>`, then switch to `restore-<name>`.
Each `refs/leftovers/<tree>` is one commit on top of that tree's old HEAD holding its uncommitted files (mirror and pytest
droppings excluded: the mirror is regenerable by `live_mirror.py pull`). `refs/leftovers/branch/<branch>` are branch tips.

| name | what it holds | who decides |
|---|---|---|
| mts-daxbt | bigtrade `capture.py`, `fires_kline.py`, `parity_kline.py`, `test_fires_kline.py`, FINDINGS.md: older than the same files on fast-track | DSA: diff against fast-track, keep only what is newer |
| mts-extract | `extract_fix_gps.py` (never tracked), `etg6j0JybfE_v2.md` | DSA extraction lane |
| mts-pastehdr | `DSA_SESSION_PASTE_v2.txt`, `patch_hdr.py`, BUILD_REPORT edit | DSA |
| mts-research | core_readiness harness + Java replay, `p1_cost_floor_full.py`, `RestHistoricalSource.java` | DSA (research) |
| mts-krown-layer | `fill_cards.py`, `_patch_prereg.py`, two artifact html edits | Krown lane |
| mts-unstick, mts-eset | feedback inbox json, gate log | none: scratch |
| branch/research/agenda-2026-10-06 | 13 research commits (P1/P4, T055); also tag `archive/research-agenda-2026-10-06` on origin; origin branch deleted | DSA |
| branch/tokopt-* | token-optimization packages; integrated by 901a06e1, remaining diffs conflict with the newer relay prompts | none: superseded |
| branch/jisnb/relay-* | old relay handoff commits, Krown captions run | none unless a card says so |

Left alone on purpose: the live tree, `mts-control-room`, named lanes (`mts-dsa`, `mts-relay`, `mts-refiner`, `mts-push`),
`shots-inbox/*` on origin (screenshot intake, health now ignores it), trees active in the last 3 h, and the NUC claim `b172-trim`
(owned by JIS-NUC).

## Why it will not pile up again
- `scripts/dev/stop_guard.py` (Stop hook): a session that tries to end with uncommitted files or unshipped commits is told once to
  commit and `sync.py ship`. A second stop is allowed so a stuck gate cannot trap it. `MTS_STOP_GUARD=off` disables.
- `sync.py tidy --apply` now repairs case-broken HEADs (`jis-nb/x` vs `JIS-NB/x`, the cause of 23 invisible trees) before it
  looks at anything, and `daily_hygiene.py` runs it every morning (06:30), so finished trees retire without a session.
- Data safety is the existing `MTS-Backup` task: every 15 min it snapshots every worktree (dirty and untracked files too) to
  `refs/heads/backup/<host>/<tree>` on `F:/MTS_backup.git`, never the public origin. Gap: other machines need their own `backup`
  remote. `sync.py new_worktree` now names the branch in the case the ref store already uses.
- Already on fast-track from the token-optimization work: the pulled mirror is untracked and ignored, `where`/`health` print real
  work only, `tidy` retires App and relay trees.
