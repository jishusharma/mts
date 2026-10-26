# Station C watcher and continuous rolling sessions: audit and implementation plan

26 October 2026. Audited tree: ce8194ba2ccaa4e3e058954df95d019a5c2c8ded. Scope: repository code, committed pilot receipts and policies. No timers installed, live processes changed, remote login probed, other chats messaged, private session history or secrets read. This is a plan, not authorization to operate production orchestration.

**Decision:** repair ownership, current-state dispatch and truthful completion before increasing the wake rate. Then test a bounded rolling chain using the existing scheduled-session capability, with durable state and exclusive ownership. A successful scheduled startup is useful evidence; it does not prove reliable continuous operation. Keep Git, cards, signals, existing lease code and worker adapters. No new broker, service, database or fleet daemon is justified.

## Evidence, provenance and limits

- Original GPT/Codex audit: `coordination_audit_20261026/REPORT.md` and `reproduce.py`, commit `3dc47d91d`, explicit `MTS-Session: ...-COD-AUD-coordination` trailer. Shared Git author identity alone would not establish model ownership.
- Independent Claude review: `coordination_audit_20261026/CLAUDE_REVIEW.md`, `c074aca4d`, Claude Sonnet coauthor receipt; `coord-audit-review` is **done**, not waiting for review. Seven findings accepted, one narrowed, parts of historical CI evidence not independently checked. Its result receipt still says UNCHECKED: card state and verification strength are different facts.
- This run reran the original hermetic demonstrations: **12/12 still assert the defects** at the audited revision. These tests assert broken behavior; they must be replaced/supplemented with desired-behavior regressions during implementation. Output retained as `reproductions.json`.
- Supervisor and role-loader tests: **113 passed, 1 failed** in 12.70 s using a fresh pytest temporary directory. The failure is the previously reported `test_pick_cards_jis_nb_lane_follows_the_live_host_file`: expected old JIS-NB name, received canonical JIS-DESKTOP. An initial pytest invocation used a wrong role-test path (no tests ran); a subsequent default-temp run encountered 61 permission setup errors. Fresh `--basetemp` resolved those environment errors. Direct execution of test_supervisor.py exits zero without running its pytest functions and is not test evidence.
- Latest scheduled-start receipt: `chain_test_proof.txt`, commit `ce8194ba2`, Claude Opus coauthor. It records scheduled `chain-test-2` startup at 09:07:23Z, hooks, Bash/PowerShell/Agent tools and deferred scheduled-task tools available. It explicitly says it did not create another scheduled task. The receipt also reports a stale primary checkout and low C: space; these are historical observations, not measurements of this turn.
- This receipt proves one scheduled invocation reportedly reached a usable Code session. It does not contain task registration/run IDs, full predecessor-to-successor lineage, a third hop, exclusive-owner proof, restart recovery, quota-reset handling or cancellation proof. Do not count the filename's “2” as two independently verified hops.
- Context trimming, role consolidation, rotation and super-session policies have Claude coauthor receipts (`220ec4619`, `2c9bbaf9c`, `99712eb55`, `3d0768186`, `b5aac2bf8`). This is not evidence that GPT authored those changes. `5d9748041` is the Claude Sonnet watchcheck implementation. Claims about unreceipted settings or operator-only actions remain unverified.
- Current inventory and exact refs are in `evidence.json`. Current open cards differ from the original audit's all-card historical counts; archived cards must be included before comparing totals. No fleet usage or current remote-control availability is inferred from repository state.

## Critical gaps in the path from startup to next useful work

| Priority | Verified boundary | Consequence and smallest repair |
|---|---|---|
| P1 | `sync.claim` / `push_claim_commit`: two clones both succeed after rejected-push retry | Revalidate owner and scope inside every fresh-tip push attempt. Return reservation identity; reject stale release. Adapt existing lease CAS pattern rather than adding a lock service. |
| P1 | `tasks.open_claims` ignores the side claims ref; dispatch reads worktree cards after fetching | One canonical claims reader; cards/holds/receipts from a pinned fetched trunk snapshot. Share eligibility with next/dispatch/Codex. Do not merge a coordinator's dirty working files just to read current state. |
| P1 | `mts_signal.auto_send_text` emits done from failed ship command text | Emit from successful structured runner/ship outcome, with content SHA and verification state. A notification is not proof of completion. |
| P1 | `run_all_tests.exec_step` timeout is printed/cached as PASS | Preserve DEFERRED separately; never reuse as successful execution. Required CI must complete before a dependent consumer runs. |
| P1 | `supervisor._probe_wait_state` drops per-SHA on_green, omits new eligible work/signals; fast slots not counted | Wake on relevant verification and eligibility changes, all active gate pools and durable receipt changes. Reconcile periodically inside the bounded session even after a missed notification. |
| P2 | `supervisor.brief` omits context reads, tests and done_when; generic dependencies omit upstream results | Reuse `tasks.brief` as the common compact body and add pinned upstream proof references. Test the actual adapter-delivered prompt. |
| P2 | Gemini long ID release differs from truncated claim; review transfer is not durable | Immediate slug normalization/owner checks, then explicit review-ready branch/SHA and reviewer ownership transfer. Release failure must affect job status. |

All seven remain open under the supplied reproductions. The independent review recommends cheap fixes before larger receipt changes; follow that advice. A one-line slug fix removes the immediate long-ID defect but does not establish safe release after ownership replacement.

`watchcheck` is a useful existing improvement: it rejects absent, expired or dead watcher markers. Its PID marker proves a local process appears alive; it does not prove that the app will deliver its exit, that its inputs are fresh, or that another watcher has not replaced the marker. Test delivery and lifecycle ownership, including one watcher's cleanup removing another's marker. Do not call that last race a demonstrated production incident.

## Station C startup and policy contradictions

The start chain is Lead -> Supervisor -> Builders. `WATCHER_TASKS_2026-10-25.md` supplies the Station C goal and historical station assignments; it is not a fresh budget reading or fleet inventory. `roles/supervisor.md` must actually be injected with its version banner. A role receipt proves which instructions arrived, not that the worker followed them. A scheduled successor needs the role line, durable handover path, run limits and current snapshot, just as the rotation test required after clear.

Do not launch the Watcher file verbatim as an operating procedure until these contradictions are reconciled in one documentation change:

| Sources | Conflict | Proposed resolution, not enacted here |
|---|---|---|
| SCHEDULING_POLICY sections 1-2; new chain receipt | Standing routines prohibited; no coordinator means no progress, but scheduled Code startup now demonstrated | Add a narrowly scoped, expiring rolling-pilot exception. Preserve unrelated prohibitions. Historical scheduler removal dates are not today's inventory. |
| Watcher every wake step 1; PARALLEL | Pull in a fixed primary path vs isolated-tree protocol; the receipt hit `.mts_live` refusal | Fetch and read pinned refs in the own tree. Verify hook source revision separately; builders never update or clean the primary/live tree. |
| Watcher 3-4 h handover; SUPER_SESSION 24 h / 200K; role transit five-hour loop; context design 3 h / 150K | Multiple incompatible rotation triggers | One pilot wave target: natural break by 3 h or 150K observed context, with a hard 4 h deadline; durable recovery if compaction intervenes. These are proposed OURS values. Measure before adopting permanently. |
| role header “Read first”; same file “Boot reads only” | Full-doc boot instruction survives the context trim | One explicit minimal boot list plus on-demand references. Verify hook output, including tail and required banner. |
| role says no start_session/model_guard refuses; SUPER_SESSION permits sessions on operator turns | Removed guard and different surface capabilities | Capability table by surface/turn type. Background Agents remain supported workers; scheduled successors require their own tested path. No global claim that one API works everywhere. |
| Watcher sole plan writer; multi-login coordinators and Planner | No enforced exclusive watcher ownership | One fleet-plan lease holder; local coordinators only execute assigned cards. Card reservations remain per-task locks. |
| Watcher only docs/system gets no CI; ci.yml includes tasks and roles | Path shorthand is false | Compute applicable workflow from changed paths. A role/card change can trigger CI; ordinary research Markdown may not. Do not borrow an unrelated green run. |
| Watcher exact headSha; SUPER_SESSION ancestor-green verification | A merge SHA and content SHA may differ | Record both, verify content is reachable from a tested revision with required checks; record explicit no-required-CI where applicable. |
| SUPER_SESSION Boot facts “Gemini ships directly”; gemini_queue review contract | Generation and final reviewed ship conflated | Distinguish produced/review-ready/pushed/verified. Claude review owns final ship on this adapter. |
| C handover cap 79/80; generic B/C cap 75 on desktop | Historical override vs current code | Each bounded run stores cap, source and expiry. No carry-forward of stale quota numbers. Unknown quota stops new paid starts. |

The Watcher file also says “start no new tooling” pending a decision. This audit creates no orchestration tooling. Before implementation, the Lead should reconcile that constraint against the operator's selected repair cards; do not silently treat the old task list as approval for unlimited infrastructure work.

## Communication, identity, leases and reach

Git is durable shared state; `mts-signals` is a hint channel. `mts_signal.news` advances a timestamp cursor before displaying only the last SHOW_MAX ordinary signals. Thus it does not guarantee every ordinary signal is individually surfaced; durable reconciliation must discover work without it. Broadcast acknowledgements distinguish none/told/done and told expires after two hours, which is useful. `ack_state` keys by broadcast ID and host, while a station is device + login. That is adequate for a device-wide disk cleanup but not proof that both logins on that host acted. Add a station-scoped receipt only where the action requires it; retain device-scoped deduplication for device work.

Use canonical host aliases, login identifier, provider, session ID and run ID in coordination identity. Never publish email addresses, private history or quota/account details. `supervisor.live_supervisors` is keyed by login and heartbeats expire at 75 min. It is a liveness estimate and shard hint, **not** exclusive ownership: two coordinators can believe they are the same login's owner. CRC shards can change when a peer appears; card claims must be correct before rebalancing is safe.

`lease.py` already implements fresh-tip CAS, session identity, nonce, write ID and fail-closed require/renew/release; currently SINGLETONS contains only Pipeliner. Reuse its implementation pattern for watcher ownership, with explicit scope and generation. Do not simply reuse its current role name or assume its 45 min TTL fits the watcher's 50 min wait. Require renewal before a lease can expire during a wait, or choose TTL/wait together and test clock skew. Fence every dispatch/plan mutation on the current generation. A heartbeat going stale is not permission to steal a worker's card reservation.

Remote Control, SSH and app tools are separate capabilities. A local session API may start linked sessions on its current login; repository signals cannot cause a remote app to execute commands. Existing SSH/nuc_wake plumbing can reach a configured host, but the audit did not probe it and cannot attest to power, network, credentials, signed-in account or current allowance. Never infer actual reach from a key path existing. Pilot receipts must record a harmless challenge/response, canonical host, login identifier, capability, expiry and success/failure for each intended station. Do not export or collect credentials. Remote Control being off caused a real rotation failure in pilot 2; leave it off unless the bounded run explicitly needs and has authority for it.

## Proposed bounded authority for rolling testing

This is the exact policy shape to approve and implement later. It does not install anything now. Continuous means sequential recoverable waves within an authorized window, with bounded idle time and explicit stops; it does not mean an immortal context or a permanent keep-alive loop.

1. One run manifest in the existing coordinator handover/card state: run ID, scope, eligible stations/providers, allowed actions, start/end UTC, quota source/caps, owner lease generation, handover content SHA, next hop and cancellation state. Local app/task IDs stay private; public receipts contain only non-sensitive proof references.
2. First real trial: two-worker default, non-live disjoint cards, one active local ship per machine. Up to three coordinator waves and 12 h total, each at most 4 h. No automatic extension or new provider/login enrollment. Values are **OURS proposed pilot limits**, not established capacity.
3. One enabled successor trigger per ownership scope, with a unique `(run, scope, hop)` key. It may start only the next scoped coordinator, load its handover, claim the coordinator lease and reconcile. It cannot run arbitrary broadcast command text. An early successor may observe/drain but cannot dispatch before transfer. If the app only supports recurring triggers, bound the recurrence and disable it at deadline/cancel; prove this before the real pilot. Do not assume scheduled sessions can self-schedule because tools are merely visible.
4. Prepare handover and record next-hop intent before arming; record registration acknowledgement and actual delivery. Old owner publishes transfer, successor acknowledges the same content revision and acquires the next generation. Handle crashes at every step by reconciling the existing task and lease before retry, not by blindly creating another trigger. Duplicate invocation exits without paid workers after ownership refusal.
5. At every wake and before paid spawn: fresh board/STOP, lease, signed-in identity, pinned dispatch state, applicable CI and current budget. Initial cap follows the explicit manifest and approved account policy; no historical meter reuse. At quota stop, park workers safely and optionally arm one already-authorized reset wake before the global deadline. Unknown quota or permission is a visible blocked state.
6. Kill switch: durable run cancelled or deadline passed prevents dispatch even if a timer fires late. Disable/remove owned triggers, release only own coordinator lease, retain card reservations or explicitly transfer them, and record drain status. No restart/deploy/HALT/orders/mainnet or machine power-setting changes in this authority.
7. Keep-alive is one bounded watcher per active coordinator, not dummy model messages, artificial quota consumption or sleep prevention. A watchdog can report loss of delivery; a local PID cannot guarantee revival after app exit, sleep, logout or reboot. These require separate measured pilot cases and must fail visibly rather than spawning loops.

## Phased implementation and card reuse

| Phase / owner role | Concrete deliverable and existing-card home | Exit proof |
|---|---|---|
| 0 Lead + Planner | Reconcile above policy/start text; freeze eligible ready cards; inspect current scope and branches before assigning work. `coord-audit-review` stays done. | One policy authority and a run contract; no timers enabled. |
| 1 Builder, serial central-file edits | Canonical claims + fresh-tip retry validation + owner-safe release. Reuse `q17-p4-bookkeeping-out-of-git` only after refining its scope; `tandem-dispatch-host-lanes` for snapshot/eligibility. | Same-card and overlapping-area two-clone races yield one winner; stale owner cannot release replacement; fetched dependency unlocks successor. |
| 2 Builder | Truthful ship/DEFERRED/receipt lifecycle; reuse `ship-signal-send-done-only-on-a-complete`, `bug-session-handoff-ship-speed-audit`, `gemini-laptop-open-questions`. | Failed/unknown push never reports done; release failure visible; reviewed revision bound to result; elapsed phases explain command wall time. |
| 3 Builder + Checker | Useful wake inputs, watcher lifecycle tests and full CI registration. Extend the completed watchcheck card's proven mechanism through a scoped follow-up, not a second watcher framework. | Green transition, new eligible card, missed signal and fast-pool release wake correctly; restart reconstructs pending verification. |
| 4 Builder | Common brief and lifecycle context fold; reuse `context-gap-fold-on-ship`, `score-context-reads-automatically-carrie`, `context-cost-rules-compact-before-idle-o`. | Actual Claude/GPT/Gemini prompts preserve objective, constraints, tests, acceptance, reads and upstream proof; no private transcript copied. |
| 5 Lead + scoped Builder | Exclusive rolling ownership and bounded scheduler adapter, using lease code and handover fields. A new narrow card is justified only for missing ownership/chain behavior and deterministic end-to-end drill. | Three local simulated hops, duplicate/late/cancelled trigger tests, then one real harmless scheduled hop with acknowledgement. |
| 6 Station coordinators + Checker | Real 2-clone / 2-adapter drill, then three-wave station trial, then second provider. Do not start all fleet logins at once. | Acceptance matrix below; publish aggregate proof and explicit uncovered cases. |

`dispatch-a-critical-crucial-blocker-outr` and `gemini-queue-claim-release-push-hangs-fo` are now done: reuse their code and regression tests, not their closed status as proof of all dispatch/release behavior. `registering-a-test-in-scripts-dev-run-ex` is done (EXTRA moved to extra_tests.tsv); pilot 2's registration bottleneck is historical and must be remeasured. Avoid opening duplicate “fix registration” work. Restore the excluded Supervisor suite plus alias expectation; wiring inventory alone is not behavior proof. New regressions must fail against the pre-fix code.

## Acceptance drill and failure matrix

Run A produces -> B independently reviews -> C consumes, using harmless fixture output. First use two local clones; then desktop/laptop/NUC, covering two logins, the same login moving hosts, two logins on one host where supported, canonical host rename, and GPT/Gemini adapters. Prove each cell independently; unavailable stations remain NOT TESTED. No layer holdout reads or trading actions are needed.

| Injected condition | Required result / proof |
|---|---|
| Same card / overlapping scope claim race | Exactly one reservation; loser takes another eligible task; two successful owners is a hard failure. |
| Duplicate wake, delayed signal, more signals than display cap | One dispatch effect; durable state recovers every eligible successor despite notification omission. |
| Network loss before push / ambiguous push acknowledgement | Unknown outcome reconciled by revision/write ID; no false completion, no blind duplicate production. |
| CI pending, red, green out of order; docs-only no-run | Consumer waits for applicable evidence; red stops new shipping; required tested ancestry checked; no-run reason derived from paths. |
| Worker dies before result / after push / before release | Existing output rediscovered; reservations retained or transferred explicitly; no cleanup of another owner's work. |
| Coordinator dies before/after trigger acknowledgement or transfer | At most one new owner; successor recovers handover and pending reviews; old generation fenced. |
| App exits, PC sleeps/reboots, logout/login swap | Record delivery delay/failure and identity mismatch; no unauthorized renewal. Resume only inside still-valid run scope. |
| Lease expires; old owner resumes; clock skew | Old owner cannot dispatch/release new owner; unknown clock or identity fails closed. |
| Clear/compaction while workers run | Recover exact worker/claim/receipt/CI/deadline state; no repeat of finished work; refuse unsupported clear safely. |
| Gemini long ID / review branch not shipped | No orphan reservation, exactly one reviewer, consumed revision is reviewed revision. |
| Quota stale, exhausted, reset; STOP/HOLD or cancellation | No paid new starts while blocked; bounded reset wake only if authorized; late trigger exits; cancellation and drain receipt durable. |
| Gate CPU/disk pressure / missing remote capability | Stay at one ship locally, reduce starts, expose exact blocker. No inferred capacity or process killing. |

## Measurement and expansion criteria

Use existing timing/usage/context scripts, cards and CI receipts; add fields at the producer only where missing. Record ready -> claim -> first useful action -> produced -> pushed -> required verification -> successor claim. Separate gate wait/run, push retries, CI job queue/run and entire command wall time. Count verified cards with acceptance proof, not commits, messages or model starts. Report median/p90 by task class, adapter and station; include sample sizes and dropped/blocked outcomes.

Historical pilot 1b: 7 ships, gate/CPU/rework failures. Pilot 2: 13 ships, 0 reported CI reds, typical gates 35 s-3m23 but ~2.5 min median, long outliers, rotation required operator input, ready cards ran out early. These are pilot observations, not proof that six workers is economical. Its account delta includes other sessions and cannot price individual workers. The ultra-pilot report still has pending sections; it cannot establish a completed comparison.

Context baseline file has one 38-session row: median 26 calls to edit, p90 61, median edit context 128,264. No paired post-fix improvement is established. Fixed context of roughly 69-75K is historical Claude measurement, not this session's measured floor. Trimming role text further cannot be assumed to remove app/tool overhead. Compare same task classes with/without delivered context; include review tasks whose first useful action is not an edit. Settings/connector trimming is a separate controlled trial, not a production rollout bundled with scheduling.

Proposed OURS promotion criteria:

- Zero duplicate owners/starts, false completion, premature consumers, lost successors or unauthorized actions; 100% handovers reconstruct exact state. Any failure blocks fleet expansion.
- Three consecutive coordinator waves finish within their declared deadlines, with zero operator interventions after initial start, no owned trigger remaining active after cancellation/end, and every unavailable station explicitly accounted for.
- Active-session successor pickup p90 <= 10 min at five-minute polling; scheduled handover pickup <= 10 min after its due time on an awake connected station. Sleep/network failures are reported separately, not silently excluded.
- Non-live local gate median < 2 min and gate queue median < 2 min; separately record command-to-exit median/p90. CI creation-to-required-green p90 target <= 4 min, job queue p90 <= 1 min. Failure to meet latency is a capacity/fairness finding, never permission to skip required checks.
- Matched minimum 10 verified routine cards per variant, at least 24 h rework observation: lower total input/cache/output tokens per verified card (target >=20% reduction), no added rework. Paid price conversion only with current sourced rate and actual attribution; shared quota percentages are coarse ceilings, not exact cost.
- Existing context design's median 8 calls / 0 unnamed reads / 85K edit context / <=1 rewrite per session are experimental targets, not guarantees. Record cache misses and coordinator overhead per verified card too.
- Maintain at least six truly eligible disjoint ready cards before increasing workers; two-worker default until the matched run improves verified cards/hour without worsening cost/card, queue p90 or failure rate. Increase one worker or one station at a time.

CI currently declares 15 offline jobs per applicable push (3 Linux + 12 Windows), plus mark-green. Per-commit concurrency prevents cancellation starvation but can multiply job demand: N applicable pushes imply 15N offline job starts before retries. Actual runner capacity, billed minutes and queue delays were not measured here. Query run/job timestamps in the real trial before adding shards or workers; local gate slots and cloud CI capacity are separate constraints. No new self-hosted runner project is justified by current evidence.

## Deliverable boundary

This report extends the accepted audit with startup, policy, rolling authority and fleet acceptance requirements. It does not claim unattended continuity is already solved. The next implementation unit is ownership plus authoritative dispatch, followed by truthful completion and useful wakeups. Roll out scheduling only after those invariants pass and its bounded authority is made explicit.
