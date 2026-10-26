# Retained worktrees: decisions and recovery order (2026-10-26)

The prior 79 was a guarded-cleanup keep count, not 79 unfinished tasks or running sessions. A new inventory found 82 registered checkouts including the primary, persistent lanes, recent sessions and this new review checkout. Each has a disposition and exact commit/file hashes in DISPOSITIONS.json. Counts are this snapshot, not a fleet census.

## Decisions already made

- Retire old queue checkouts after saving all edits and ignored files locally, retaining their branches and verifying a complete all-ref Git bundle. A checkout is disposable; an unreviewed result is not automatically useful or correct. Nothing is blindly merged.
- Seventeen queue trees have committed delta files byte-identical to trunk. Ten more hold the pre-review Gemini fact sheets; current corrected versions and the independent review are already on trunk. Keep those corrected versions. Old cards, LAYERS.md and draft patches must not overwrite current queue or code state.
- Archive optional platform research, video retry/extract drafts and superseded repairs. Do not turn every saved folder into a new task. UNVERIFIED video notes remain unverified.
- Preserve primary and persistent lanes, the current review, and recently active owner checkouts. Directory activity is not proof of a live AI session. No live processes, schedules, ACLs, account settings or deployments were changed.

## Relevant work, in priority order

1. **Host reliability:** the recently active runaway-process author branch contains a guard design and original local cards not on trunk; preserve its owner checkout and request the author ship that package after independent review. The archived codex-stuck branch contains ACL helpers and an old-Git test-fixture compatibility change. Recover them for review; do not execute the elevated helpers automatically. This matters directly to session health and memory exhaustion. Review these within existing `opus-station-review-act`, not a competing new repair hierarchy.
2. **Coordination reliability:** continue the existing Opus review/repair card. The two Lenovo-start reports are additional historical inputs. Do not claim them as present-day capability verification or start a second scheduler system.
3. **Use existing research repair cards:** LC1 touched-only control (`re-state-lc1-keep-list-on-the-touched-on`), Tom extraction corrections (`apply-gpt-review-fix-items-to-gemini-ext`), RV05 blind-read adjudication (`rv05-h2-position-line-evidence`), and G7 (`gap-g7-stop-slippage`). Their archived evidence is linked in the manifest. G7 output explicitly says blocked before fetch, not measured slippage. This review does not waive any spec/review/holdout gate.
4. **Historical evidence only:** T04/T09 have current canonical completed audits. Compare any genuinely missing proofs or contradictory claims with those canonical results. Do not rerun all studies. FVG-side, tested-exit and StateCode repair cards are already done; archive their old patches.
5. **Deferred:** remaining platform comparisons, new video drafts and missing audit helper scripts stay in the indexed archive. Pull one only when an active existing card needs it. No automatic repeated audits or fetching to use quota.

## How archived work is recovered

On the NUC, all branch names and commit IDs in the manifest remain in Git. Inspect with `git show <sha>:<path>` or compare `git diff origin/fast-track <sha> -- <path>`. Start an isolated tree with sync.py before applying selected accepted changes; never merge an entire old branch with stale task cards. File snapshots, binary staged/unstaged patches and SHA256 manifests are saved outside the public repo under `F:/MTS/audits/worktree-disposition-20261026/saved-work/`; complete history is in the verified `all-refs-before-archive.bundle` there. Local-only evidence must be exported and reviewed on the NUC before another device can use it. Backup existence does not mean published or accepted.

## Monitoring gap and acceptance

The current producer/harvester handoff allows a locally committed result to linger without a receipt. The existing Opus lifecycle repair should enforce produced -> reviewed -> pushed -> verified -> checkout retired, with a durable owner and explicit blocked/deferred reason. Worktree counts measure storage; they do not measure active jobs. Accept cleanup from verified snapshots and actual directory removal, and accept research only through the original card's independent evidence gates.

This is a local disposition and archival action. No claims about other stations being cleaned or all findings being fixed are made. A signal asks existing owners to pick up; it does not wake a sleeping session or prove pickup.

## Snapshot decisions

| Category | Checkouts |
|---|---:|
| BLOCKED_EXISTING | 1 |
| COMPARE_CANONICAL | 2 |
| COMPLETED_OR_RESIDUE | 11 |
| COORDINATION_REFERENCE | 2 |
| DEFER_ARCHIVE | 12 |
| EVIDENCE_ARCHIVE | 6 |
| EXACT_DUPLICATE | 17 |
| HOST_RELIABILITY_REVIEW | 2 |
| PROTECTED_WORKSPACE | 3 |
| RECENT_WORKSPACE | 2 |
| RECOVER_EXISTING | 3 |
| SUPERSEDED | 13 |
| SUPERSEDED_OR_UNVERIFIED | 8 |

## Completed cleanup and preservation

Reviewed 82 checkouts; retired 75 registrations. Fully removed 73 archived checkouts; moved two residual directories intact into the recovery archive after Git removal partially failed. 7 registered checkouts remain: primary, Codex project, Codex lab, current review, Gemini owner workspace and two recently active runaway-investigation workspaces. These are not seven queued jobs.

Verified all 554 saved file hashes (215,984,234 bytes), all 82 original commit objects, and the complete all-ref Git bundle. Local snapshots preserve data and edits; nothing from those snapshots was publicly committed. Exact removal/preservation counts are in CLEANUP_RECEIPT.json. The follow-up native deletion of the two residual directories was rejected by automatic approval review ('blocked by policy'); reversible archival succeeded.
