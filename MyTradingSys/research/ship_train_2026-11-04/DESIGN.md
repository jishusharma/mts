# Ship train - why CI is red 28% of runs, and one queue for every machine (design only, 2026-11-04)

Card `ship-train-design-1104`. Design only: no edit to `sync.py` or `ci.yml`. Options, cutover cards and the list of checks the
train makes redundant: `MyTradingSys/system/SHIP_TRAIN.md` (same card, earlier run). This file is the measured cause table and the rules.

Method (parsed, not eyeballed): `gh run list --workflow ci.yml --branch fast-track --limit 400 --json`, window 2026-11-01T21:17Z ..
11-03T20:15Z (exclusive) = 200 runs, 56 `failure`. For each red run `gh run view <id> --json jobs` (failing jobs) and `--log-failed`
(regex over `FAILED|FAIL|ERROR <test id>`); first matching cause wins, content causes before flaky ones (a run holding both is content).
Joined to `git log -1 --format=%an|%P|%s <headSha>`. Host = the `into <host>/<slug>` of the head merge commit, else of the first merge on
the ancestry path to trunk (inferred). The 57th red in a window to 20:16Z is `65a9edc97` (the card-filing commit itself), excluded.

## 1. The 56 red runs by cause

| Class | Cause (failing test) | Runs | Merge-headed | Host of head commit | First red |
|---|---|---|---|---|---|
| B content | MTS Home size cap, `test_hub_folds_link_help_and_stays_compact` | 7 | 3 | jis-nuc 4, DESKTOP-F7IU69N 3 | `5fb3ce500` 11-03 15:40 |
| B content | card moved, `test_runner_card_exists_and_valid` | 5 | 2 | jis-nuc 3, JIS-NB 2 | `a67e1245e` 11-03 16:06 |
| B content | doc forbidden refs, `test_2_no_forbidden_refs` | 4 | 4 | DESKTOP-F7IU69N 2, jis-nuc 2 | `1340591bf` 11-03 16:01 |
| B content | dev_ext data absent, `meta_label_dev_ext` | 4 | 3 | jis-nuc 2, DESKTOP-F7IU69N 2 | `ffb905d6c` 11-02 11:35 |
| B content | sim_desk catalogue vs cards, `test_backfill` / `test_artifact` | 4 | 1 | jis-nuc 2, DESKTOP-F7IU69N 1, cloud 1 | `3aacac208` 11-02 12:05 |
| B content | trial ledger, `test_live_repo_trial_ledger_built` | 4 | 0 | JIS-NB 4 | `9867ff753` 11-03 09:40 |
| B content | scratch dir inside checkout, `CheckoutTest` | 3 | 2 | jis-nuc 3 | `41d35ee4e` 11-03 16:59 |
| B content | role budget / roster, `test_role_loader` | 2 | 2 | DESKTOP-F7IU69N 2 | `dd1effff3` 11-02 17:03 |
| B content | open-card count, `test_list_spawns_few_git_processes` | 2 | 1 | DESKTOP-F7IU69N 2 | `45af07196` 11-02 17:08 |
| B content | bridge changed without bump, `test_bridge_version_is_bumped...` | 2 | 2 | JIS-NB 1, cloud 1 | `bfb8ae7ca` 11-02 20:21 |
| B content | captions all-skipped counted as FAIL, `test_fetch_captions` | 1 | 0 | JIS-NB 1 | `14b12f2c2` 11-03 16:33 |
| A flaky | `c_drive_buckets` (Windows runner has no browser-cache bucket) | 10 | 5 | jis-nuc 8, DESKTOP-F7IU69N 2 | `e294f987c` 11-01 21:46 |
| A flaky | `gemini_queue` two-process claim race | 2 | 1 | DESKTOP-F7IU69N 1, cloud 1 | `e97827bd3` 11-02 13:09 |
| A flaky | `test_sync` fix_ci LAYERS.md add | 2 | 0 | JIS-NB 1, jis-nuc 1 | `124800210` 11-03 18:32 |
| A flaky | `mts_doctor` missing memory dir | 1 | 0 | DESKTOP-F7IU69N 1 | `58980d9ba` 11-02 18:30 |
| A flaky | `c_drive_guard` ProcsTest | 1 | 0 | jis-nuc 1 | `c46868c76` 11-02 19:05 |
| A flaky | aibridge node helpers | 1 | 1 | JIS-NB 1 | `7cfc66710` 11-02 19:46 |
| A flaky | `spec_news` keywords | 1 | 1 | gemini-queue tree 1 | `ca38a5b3d` 11-03 19:13 |
| **Total** | | **56** | **28** | | |

Class totals: **B content 38 (68%)**, **A flaky 18 (32%)**. Rows sum to 56 (printed `red 56 sum 56` by the classifier).

### By author class

| Author class | Red runs | Note |
|---|---|---|
| git author `gemini-queue` | 56 of 56 | every machine commits as the same git user: the author field names no one |
| head = merge of trunk into a session branch | 28 of 56 | sessions merge fast-track, re-push; the run blames the merge, not the change |
| host (from branch name): jis-nuc / DESKTOP-F7IU69N / JIS-NB / cloud `claude/*` / other | 26 / 16 / 10 / 3 / 1 | inferred for non-merge heads; no machine is the single source |

Read: 11 content causes produced 38 red runs, so ~27 runs re-reported a break already on trunk,
because ships kept landing on a red trunk. Two causes (`915c162c4` decision text -> home size cap; `9d9e1bdb4` registry rows -> trial
ledger) were docs/data-only commits that `ci.yml push: paths:` never ran; the first red landed on the next code commit (SHIP_TRAIN.md s1).

## 2. Queue design (one page)

One queue, `queue/<host>/<slug>` refs, drained by one Actions workflow; fast-track moves only by that workflow. Every rule cites a row above.

| # | Rule | Cites |
|---|---|---|
| R1 | **Every machine ships the same way:** `sync.py ship` keeps the local smoke gate, then pushes `queue/<host>/<slug>` instead of fast-track. Cloud containers push the same ref shape (`queue/cloud/<slug>`). No direct push to fast-track except break-glass `--direct` (coordinator). | reds come from 5 host classes 26/16/10/3/1 = 56 (jis-nuc / DESKTOP-F7IU69N / JIS-NB / cloud / other, table above); no single machine to fix |
| R2 | **The ref name is the author.** Blame = `<host>/<slug>` + the slug's claim, stamped into the message of each candidate merge commit the train builds (R3) and into the status file. fast-track gets those merge commits by fast-forward, so the stamp rides on commits that already exist; no extra landing commit. Git author is ignored. | 56/56 reds carry author `gemini-queue` |
| R3 | **Nothing red lands.** The train builds candidate = fast-track tip + queued refs merged (oldest first, cap 4), runs the existing CI matrix on it, and fast-forwards fast-track to the green candidate tip only on green (landing form = fast-forward only; the stamped merge commits of R2 are part of that candidate, built before CI). Merge conflict = eject that ref at once. | 38 content reds (68%) were found only on trunk; ~27 were repeats on an already-red trunk |
| R4 | **Docs/data ships ride the train too, on a fast lane** (integrity + size-cap + ledger subset, 1-2 min) and are ordered first. The `push: paths:` filter stops deciding what runs. | home size cap 7 + trial ledger 4 = 11 runs, both started by docs/data-only commits CI never ran |
| R5 | **Eject the breaker, not the batch.** Red candidate -> each ref runs alone on the tip in parallel (n <= 4); refs that fail alone are ejected, the rest re-run and land. If all refs are green alone but the candidate is red (pairwise conflict): bisect by halves, i.e. run the first ceil(n/2) refs merged; red half recurses, green half is kept as the base and the other half is added one ref at a time (oldest first); the first ref whose addition turns the candidate red is ejected, not the last-queued one. Max rounds = n (<= 4); if the remaining set is still red after n rounds, eject all remaining refs except the oldest and re-queue it alone, and signal the coordinator (R7). | 11 distinct content causes inside 38 runs; 8 of 21 streak origins held 3..14 commits (SHIP_TRAIN.md) |
| R6 | **A flake never ejects.** A failed shard reruns once before it counts; a test that fails then passes on the same sha is logged to the quarantine list, not charged to the ref. | 18 flaky reds (32%), 10 of them one test (`c_drive_buckets`), all green next run with no fix |
| R7 | **Name the breaker to its owner.** An ejected ref gets a signal record (host + slug, failing test id, run link) written by the Actions workflow to the `mts-signals` branch status file (same file as R8); the owner's `ship --wait` polls that file by `git fetch` (Actions has no inbound route to local machines), and the host then raises `mts_signal` locally; its claim stays open. Never auto-revert. | 28/56 heads were merge commits: first-viewer revert hits the wrong commit |
| R8 | **One status file is the wait.** The train writes `queue status` (landed / ejected / position) on the `mts-signals` branch; `ship --wait` reads it (git fetch poll) instead of polling CI; R7 signals use this same file. | every red run cost every later shipper a full CI wait (56 runs) |

Out of this design (owned elsewhere): tree retire and ship-commit noise (`ship-commit-noise-and-tree-retire-1104`, `worktree-gone-after-ship`);
building the train (SHIP_TRAIN.md cards 1-5, shadow-first). DECISION (OURS): batch cap 4 and one shard retry are starting values,
to be measured in the shadow week, not SOURCED. New numbers in R5 (halves, max rounds = n, oldest-first re-queue) are OURS, no source.

Open items (Gemini blind read BLIND_READ_SHIP_TRAIN_DESIGN_1104.md, not addressed here): U3, U4, M1, M2, M3, M4, M5, M6.

Reproduce: `gh run list` + `gh run view` as above; classifier patterns are the test ids in the Cause column.
