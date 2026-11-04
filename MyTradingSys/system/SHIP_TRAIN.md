# SHIP_TRAIN - should one coordinator land every machine's ships in order? (design, 2026-11-04)

Operator ask (2026-11-04): development feels slow; instead of every LLM on every machine pushing its own ship straight to fast-track,
should one coordinator collect ships and land them in an optimal order, so a break is traced to its source at once?
Measured and designed here. Nothing is built. Method: `gh run list --branch fast-track --limit 200` (2026-11-01T21:17Z .. 11-03T20:15Z),
`gh run view <id> --json jobs` and `--log-failed` for every one of the 56 red runs, parsed for FAILED/FAIL lines (not tail-read), joined to
trunk commits. Raw numbers re-derived this turn, not taken from the brief.

## 1. What the numbers say

| Fact | Value | Meaning |
|---|---|---|
| Runs / red | 200 / 56 (28%); 7 cancelled | matches the brief |
| CI wall (finished runs) | median 5.2 min, p90 9.5 min (brief: 5.9 / 12 incl. in-flight) | one verdict every ~5 min is the floor of any design |
| Red-state time | 21 red streaks, 1526 min of 2818 min span = 54% of the window had a red latest run | trunk is red more often than green-and-quiet |
| Red runs that were repeats | 38 content-break runs come from ~12 distinct failing tests (my count, one breaker each): ~26 runs (68%) re-reported a break already on trunk | ships kept landing on a red trunk; each one paid a full CI run |
| Flaky | 18 red runs (32% of reds), 15 streaks, all cleared by the next run with no fix | would eject an innocent ship under any queue unless a shard retry comes first |
| Blame | 684 of 697 trunk commits carry the same git author (`gemini-queue`) | author cannot say which machine/session broke it; the ship record must |
| Wrong commit blamed | CI `push: paths:` skips docs/data-only shas. Two confirmed breakers (`9d9e1bdb4` TRIAL_REGISTRY rows, `915c162c4` OPERATOR_DECISIONS.md) never had their own run; the first red run was the next code commit (`9867ff753`, `5fb3ce500`) | first-viewer revert (CLAUDE.md) can revert an innocent commit |
| Blame ambiguous | 8 of 21 streak origins had 3..14 commits since the previous CI run | bisect is needed anyway |
| Merges | 104 of 291 trunk commits in 24 h are merge commits; 20 of 38 content-break runs headed by a merge | sessions merge trunk into their branch and re-push: the race the gate re-runs for |
| Branch CI | none (CI runs on fast-track push and PRs; ships are direct pushes) | "each branch green alone, red only after merge" cannot be measured from CI; only the local smoke gate saw the branch |
| Local ship wall | 90 rows (this host, since 10-31): median 9 s, p90 104 s, 7 over 5 min, 9 failed (brief, JIS-NB-wide: 11 s / 138 s / 11 / 17) | the local step is not the slowness; the 5-10 min CI plus red-trunk blocks are |
| Last-24 h trunk mix | 108 work, 104 merge, 27 card, 24 "ship: regenerated LAYERS.md", 13 fold, 10 heartbeat/handover, 5 revert (brief) | 8% of commits only regenerate a derived file |

### Cause class -> runs, red minutes (all 56 red runs; a run with a content cause counts as content)

Red-state minutes = first red run of a streak to the next green run's start (includes quiet gaps when no code push triggers CI).
Run-minutes = sum of those runs' own wall time.

| Class | Runs | Streaks | Red-state min | Run-min | Cleared how |
|---|---|---|---|---|---|
| A. Flaky / runner-environment, next run green with no fix | 18 | 15 | 511 (438 is one overnight gap) | 83 | next run |
| B. Content break after trunk merge (a test coupled to files another ship changed), needed fix or revert | 38 | 6 | 1015 (782 is one overnight gap) | 236 | fix or revert, 5 reverts in 24 h |

Class B split by failing test (runs containing it; one run can hold several):

| Failing test / step | Runs | Breaker and fix |
|---|---|---|
| MTS Home size cap, `test_hub_folds_link_help_and_stays_compact` (30339 > 30000 B) | 7 | `915c162c4` decision text; revert `133fae87a` |
| `test_integrity::test_2_no_forbidden_refs` (doc text) | 7 | a doc line in 11-03 15:59-16:04Z runs; same test recurred later on SUPERVISOR_B.md:8 (revert `b0349341c`) |
| `TestTomProbePrereg::test_runner_card_exists_and_valid` (card moved) | 7 | fixed `14b12f2c2` |
| `test_bridge_version_bump` (bridge changed without bump), 11-02 and 11-03 | 6 | fixed `14b12f2c2` and an earlier bump |
| `test_dev_ext_window` (data absent) | 4 | fix `46df6a6cd` |
| `test_backfill` / `test_artifact` sim-desk catalogue vs cards | 4 | fixes `896b120f1`, `d4ad357af` |
| `test_tasks_list_git_spawns` (needs N open cards) | 4 | fix `87bd7e7c3` |
| `test_live_repo_trial_ledger_built` | 4 | revert `e3e1ac4ac` |
| `CheckoutTest` scratch dir inside checkout | 3 | later ship |
| `test_fetch_captions.py` all-skipped counted as FAIL (no yt_dlp) | 3 | fixes `6da563194`, `0f92c7fcc` |
| `test_role_loader` / role budget / roster | 2 | `45af07196` budget bump |

Class A split: `c_drive_buckets` BucketTest (Windows shard, runner has no browser-cache bucket) 12 runs (chronic, card exists, unfixed);
git claim race 2; `test_sync` fix_ci LAYERS.md add 2; doctor missing-memory, c_drive_guard ProcsTest, aibridge node helpers, spec_news 1 each.

Read: 38 of 56 reds (68%) and 2/3 of red time are one ship breaking a test coupled to another ship's files, found only on trunk. 18 are noise.
Both feed the same remedy: nothing red should reach trunk, and a breaker must be named at once.

## 2. Options

Landing time today: push is instant (ship wall median ~10 s), verdict 5-10 min later, trunk red meanwhile.

| | Time to land (verified) | What breaks | Cost | Rules it removes |
|---|---|---|---|---|
| A. Direct push + post-CI (today) | 10 s unverified; verdict +5-10 min | trunk red 54% of window; repeat reds 68%; wrong-commit revert; flaky blocks everyone (X6) | 200 runs x 15 jobs / 2 days | none |
| B. GitHub merge queue | n/a | Not available here: repo `jishusharma/mts` is user-owned (`owner.type=User`), public, no rulesets, branch not protected, no PRs. GitHub offers merge queue only on org-owned public repos (or Enterprise private); it also requires PRs and a ruleset. Moving the repo to an org is a go-private-style ownership change (operator-only) and still forces every ship into a PR | org move, PR per ship (cloud containers already open PRs) | would match C, but gated on the move |
| C. Custom queue ref + one Actions runner (recommended) | 6-8 min typical (collect <=1 min + 1 CI run on the batch); red path +6-12 min for the ships behind a breaker | Actions outage stops landing (needs break-glass); Actions keeps only 1 pending run per concurrency group (design must scan all queue refs each run); pushes by GITHUB_TOKEN do not trigger other workflows (the train must be the CI itself); batching hides which of 3 broke until bisected | Actions minutes on a public repo are free; runs drop to about 1 per batch (est. 3 ships) instead of 1 per ship; a bisect on red = n parallel single-ref runs (n<=4) | X6 block, revert-first, green/fast-track deploy gate (fast-track IS green), gate slots on full gates, X7 wait, ci_watch/CI-REVERT doctor check, `ship --fix-ci` |
| D. Per-machine shipper session | session minutes + tokens; same CI cadence | each machine still pushes alone; no global order; no cross-machine bisect; a new LLM session to babysit (operator wants fewer steps) | model budget on every machine | none |

Industry names: A = trunk-based development with post-merge CI (what breaks is the "red trunk"); B/C = merge queue / merge train
(GitHub merge queue, GitLab merge trains, Bors/Mergify/Zuul gating); C's bisect-and-eject = Zuul/Bors batch-bisect. D has no standard analogue.

How C works (the minimum, OURS):
1. `sync.py ship` keeps the local smoke gate, then pushes `queue/<host>/<slug>` (not fast-track). The ref name is the blame record (author is useless).
2. Workflow `train.yml` on push to `queue/**`, one run at a time. It lists ALL queue refs, orders them, builds candidate = fast-track tip + each ref merged (a merge conflict ejects that ref at once).
3. Order (optimal = cheapest to verify first, riskiest last): docs/data-only refs first on a 1-2 min lane (the integrity subset: the tests that broke on `915c162c4` and `9d9e1bdb4`); code refs next, oldest first; refs touching live-path or `.github/` alone, last. Batch cap 4.
4. Candidate runs the existing 15-shard matrix once (reused via `workflow_call`; a failed shard reruns once before it counts). Green: fast-forward fast-track and green/fast-track, delete the queue refs. Red: run each ref alone on the tip in parallel, eject the failing ones, re-run the rest; each ejected ref gets an `mts_signal` to its host/slug with the failing test id and a link.
5. Status in a small file on the `mts-signals` branch so `ship --wait` replaces X7.
6. Break-glass: `ship --direct` (operator/coordinator only) for an Actions outage.

## 3. Recommendation: C, built shadow-first, in 5 cards

DECISION (OURS): go with C, not B (unavailable) and not D (more babysitting, same blame problem). Shadow mode first (queue lands on a
`fast-track-shadow` branch, real fast-track untouched) so the cutover rests on a measured week, not a design.
DECISION (OURS): docs/data-only ships also go through the train (fast lane): two of the confirmed breakers were docs-only.
DECISION (OURS): batch cap 4, one shard retry before ejecting, ejected ship is signalled, never auto-reverted.
DECISION (OURS): `GITHUB_TOKEN` with contents:write does the fast-forward; no PAT. If branch protection is later needed, a ruleset bypass for the Actions app is the open item; not needed today (branch is unprotected).

| # | Card (id) | Done when |
|---|---|---|
| 1 | `ship-train-flake-floor` | `c_drive_buckets` flake fixed or quarantined (X5), one-shot rerun of failed shards in ci.yml, the docs-integrity subset runs on docs-only pushes; the 18 class-A reds drop to ~0 over 3 days |
| 2 | `ship-train-runner` | `train.yml` batches `queue/**` refs, merges, runs CI, lands on `fast-track-shadow` on green; test with 3 fake refs incl. one conflicting and one red |
| 3 | `ship-train-bisect-eject-signal` | red batch -> per-ref parallel runs -> eject + `mts_signal` to host/slug; `sync.py ship --train` pushes the queue ref and waits on the status file (replaces X7 for it); flag off by default |
| 4 | `ship-train-shadow-week` | 3-7 days both paths; report: red-state minutes on shadow vs trunk, land time p50/p90, false ejects (target 0), repeat-red runs; operator-visible table |
| 5 | `ship-train-cutover` | flip default, add `--direct`, remove the redundant checks (section 4), update CLAUDE.md / GATE_SPEED / DEPLOY_RUNBOOK; live-tree deploy still manual (DEPLOY_RUNBOOK) |

The 5 cards exist as READY task cards (tasks.py new + fill worked without a planner); order is in each card's note (tasks.py has no depends flag for fill).

Live-path note: card 5 changes how code reaches the tree that deploys; it needs the live-path test list (restart/reset, API errors) only if `auto_deploy`
changes, which it should not (it keeps reading green/fast-track as an alias for one cycle).

## 4. Checks that become redundant after cutover (operator: remove unnecessary steps)

| Today | Why redundant under C | When |
|---|---|---|
| X6 "two reds block the next code ship" | trunk cannot be red; a red candidate never lands | card 5 |
| CLAUDE.md first-viewer `git revert` rule + doctor CI-REVERT, `ship --fix-ci` | breaker is ejected before landing; revert only for break-glass | card 5 |
| `mark-green` job and `green/fast-track` ref | fast-track equals the last green; keep green as an alias one cycle for deploy | card 5 |
| X7 `wait_own_ci` / `ci_watch` polling | replaced by the status file | card 3/5 |
| Local full gate (gate slots, X3 pools, `race_overlap`, re-merge of trunk before push) | the train merges and runs the full suite on the real candidate; local keeps smoke only (seconds) | card 5 |
| "ship: regenerated LAYERS.md" commits (24 of 291) | regenerate once per batch in the train instead of one commit per ship (follow-up, not in the 5 cards) | after 5 |
| CI `push: paths:` filter | the train decides lane by diff; the filter is what hid two breakers | card 1/2 |
| SPAWN-on-CI-RED planner lines and the usage-gate conflict card | no red trunk to spawn for | card 5 |

Not removed: the local smoke gate (keeps most bad ships off the queue), the quarantine file, and the full CI matrix itself (it is the train's test).

## 5. Open items and honesty

- Merge-queue availability is from GitHub's published rule (org-owned only) plus `gh api repos/jishusharma/mts` showing `owner.type=User`; not tested by trying to enable it.
- "Branch green alone, red after merge" is inferred, not measured (no branch CI). Card 4 should log it: run the candidate and each ref alone.
- Red-state minutes include quiet gaps; 1220 of the 1526 are two overnight streaks (782 + 438) where no code push re-ran CI. Under C those gaps vanish because nothing red lands.
- Ship-wall rows were re-read from this host's trees only (90); the brief's 124 JIS-NB-wide figures were not re-derived.
- Estimates (batch of 3, 6-8 min, 12 parallel runs) are OURS until card 4 measures them.
