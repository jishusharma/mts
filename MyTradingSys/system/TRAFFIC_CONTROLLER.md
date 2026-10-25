# TRAFFIC_CONTROLLER: one allocator for every machine, login and lane, and a lease that keeps singletons single (design 2026-10-19)

**FOLDED 2026-10-20 (operator): Traffic_Controller is no longer a role. Its allocator job is Job 2 of the Lead's pipeline mode (`roles/lead/pipeline.md`; `You are Lead.` then `role_loader.py mode pipeline`); `You are Traffic_Controller.` is an alias. This file stays as the design record. Per-login SPEND state: `python scripts/dev/traffic.py budget`.**

Role file: `roles/lead/pipeline.md` (was `traffic_controller.md`, then `pipeliner.md`). Tools: `scripts/dev/lease.py` (Part A), `scripts/dev/traffic.py` (Part B),
inventory `MyTradingSys/system/traffic_inventory.json`. Extends SUPERVISOR.md (cards SV2-SV8 stay its own; nothing here
repeats them). Order: Pipeliner as allocator (24 h allocation across machines, logins, lanes) > Supervisor (one super session's
workers) and the desk/routing rules > workers.

## Measured first: 72 h, 2026-10-15T22:04Z .. 2026-10-18T22:04Z (`traffic.py measure --hours 72`, every source parsed whole)
Sources: 2218 trunk commits (1346 attributed to a machine: claim `Result: ... on HOST`, merge prefix `into <host>/` plus that
merge's branch-local commits, the Lenovo author id), 1094 signal lines, 52 Codex runs (`F:/codex_home/lab_runs/runs.jsonl`),
40 Gemini jobs (`F:/MTS/gq/*.log`), 47 desk rows closed. A busy hour = at least one event in that clock hour.

| Actor | busy h | idle h | longest idle h | Note |
|---|---|---|---|---|
| JIS-NB | 60 | 12 | 2 | signals + commits |
| JIS-NUC | 59 | 13 | 3 | signals + commits |
| DESKTOP-F7IU69N (Lenovo) | 7 | 65 | 61 | active only the evening of 2026-10-18 |
| lane codex (GPT) | 28 | 44 | 23 | at measure time: STALLED, 16 ready, allowance 47%, 0/10 runs in its window |
| lane gemini-nuc | 7 | 65 | 59 | 0 running at measure time |
| lane gemini-laptop | 7 | 65 | 55 | commits with `MTS-Session ...-GEM-` |
| lane dsa | 3 | 69 | 55 | desk rows closed naming DSA |

Caveats: the signal branch starts 2026-10-16T09:31Z, so the first 11 h have commits only (machine idle may be overstated by
up to 11 h). **Per-login idle hours are not measurable**: no event records which Claude login (A/B/C) ran it (senders are
`host/MTS_ACCOUNT`; NB and Lenovo send `?`). Fix = card tc3-budget-lines.

Duplicate or colliding work in the same window:
- **Pipeliner ran on two machines** the same evening, against its JIS-NUC-only pin: JIS-NUC `ebfffe68` 16:18Z, `4a6b8562`
  16:19Z, `0efac858` 18:40Z; Lenovo Gemini `41c8a303` 21:11Z (`MTS-Session MTS-2026-10-18-2110Z-GEM-BLD-yt-pipeliner`,
  wrote `DRAIN_2026-10-19.md` and ROUTING.md) plus a PIPE signal 21:12Z. Commits do not prove the two overlapped in time;
  nothing stopped them from overlapping. This is the case Part A closes.
- **3 desk rows closed twice** within 16:15-16:19Z (g2-dukascopy, g5-binance-futures, tom-on-btc-t1-footprint): the NUC
  Pipeliner and the `dsa-nuc-rows` runner closed the same rows (`4a6b8562` subject: "G5 done in parallel by dsa-nuc-rows").
  Not two Pipeliners: a Pipeliner and a second desk writer. The lease does not cover that; card tc4-desk-done-once.
- **2 cards worked by a Claude claim and a lab lane at the same time** (`live-orderflow-state-line-1m-5m-15m-pric`,
  `malkan-universe-data-power`: a JIS-NUC claim open while gemini-nuc ran it; UNVERIFIED whether that claim was a separate
  Claude session or gemini_queue's own claim held past its job). 15 more cards passed between hosts or lanes one after the
  other (release before the next start): hand-overs and retries, not collisions. (The first count, 12 collisions, used a set
  over 72 h and was wrong; review finding S8.) Card tc5-lab-lane-dedupe.
- 3 overlapping claims, all same-host re-claims seconds apart (`krown-malkan-event-counts` x4 on NB); 0 desk rows posted twice;
  0 identical work subjects from two hosts; 107 identical signal lines repeated within 5 min by the same sender.
- Lenovo git author reads `e-ngineers@JIS-NB`, so its commits look like NB's (the reviewer checked 19 of its claim bodies:
  all name DESKTOP-F7IU69N). Card tc6-lenovo-git-email.

Budget leakage seen: the GPT lane idle 44 of 72 h with ready cards (16 ready now, STALLED); Gemini idle 65 h; the Lenovo idle
65 h while NB and NUC carried the load; DSA idle 69 h with 17 desk rows pending now.

## Part A: single-instance lease (built, wired, tested)
**Where the lease lives.** `MyTradingSys/system/leases/<role>.json` on origin/fast-track:
`{role, state: held|released, holder {host, account, session}, acquired, renewed, expires, nonce, took_over_from}`.
The session is `sha256(CLAUDE_CODE_SESSION_ID or MTS_LEASE_SESSION)[:12]`; the raw id is never stored (public repo).

**CAS.** Fetch trunk, read the file at the tip, decide (free / mine / held / expired), build a plumbing commit whose parent is
that tip (private `GIT_INDEX_FILE`, the working tree is untouched), `git push origin <commit>:refs/heads/fast-track` without
force. Git accepts it only while trunk still points at the tip that was read, so of two simultaneous acquirers exactly one
lands; the loser's push is rejected (non-fast-forward / stale info / lock), it re-fetches, now sees `held`, and refuses.
Any other push error: re-fetch and look for this write's fresh `write_id`; if absent, retry; if the fetch fails, exit 4. Up to 4 tries (other trunk traffic).

**Why this push path** (lightest safe one): it is the same plumbing pattern `sync.py claim/release` already use
(`push_claim_commit`), so it needs no gate, no merge, no worktree, no rebase and no force-push. `sync.py ship` would run the
544 s smoke gate per heartbeat and merge the branch; a separate lease ref (`refs/leases/*`) would need its own fetch refspec
on every clone and is invisible to `git show origin/fast-track:` readers. CI does not run: the `.github/workflows/ci.yml` push
path list (src, backtest, tests, scripts, ...) does not include `MyTradingSys/system/`.

**Heartbeat and expiry.** TTL 45 min. `require` (called by every guarded command) renews when under
max(25 min, needed + 5 min) left; `sync.py ship` needs 20 min left, so a lease cannot expire during the gate. A lease is
taken over only after `expires + 5 min` skew; the new file records `took_over_from`. The old holder's next guarded command
sees a foreign holder key and is refused; a release by a non-holder is refused too.

**Local same-host lock.** `~/.claude/mts-leases/<role>.json`, written under an O_EXCL `.mutex` (a mutex older than 600 s, longer than a full CAS loop,
is broken). A second session on the same machine is refused locally before any network call, so it is refused even offline.

**Fail closed.** Fetch failure, unreadable or malformed lease file, push error without proof of our nonce: exit 4
(UNREACHABLE) and nothing is written. Exit codes: 0 ok, 3 REFUSED (names holder host/account/session), 4 UNREACHABLE.

**Who is a singleton session.** `MTS_ROLE` env (any spelling: `pipeliner` counts), else any singleton among the role_loader
injection records for this session id (a later mention of another role does not hide it), else the marker `lease.py acquire`
writes. A write with no session id (`CLAUDE_CODE_SESSION_ID` or `MTS_LEASE_SESSION`) is refused (exit 4): two such runners would
share one identity. Non-Claude runners (Gemini, Codex) set `MTS_ROLE` + `MTS_LEASE_SESSION`; card tc2.

**Wired into:** Pipeliner boot step 1 (`lease.py acquire Pipeliner`, refused = stop) and release in Done-when;
`desk.py post|take|done|assign|sweep` and `sync.py claim|ship|release` call `lease.guard` and refuse (exit 3/4) a singleton
session without the lease (non-singleton sessions are untouched); the role_loader banner appends `lease held by <host>/<account>
until <utc>` (or `free`, or `lease UNKNOWN (...)`). The folded allocator (Pipeliner) uses the same lease.

**Test proof** (`MyTradingSys/tests/test_lease.py`, 22 tests, two clones of one bare origin play two machines):
two simultaneous acquirers behind a barrier, exactly one wins (5/5 repeated runs); second machine refused; stale takeover
after TTL + skew and the old holder then refused by require and renew; no takeover inside skew; release frees; require renews
when low; offline acquire and CLI guard exit 4; offline after holding exits 4; malformed lease = ambiguous; non-singleton role
refused by acquire; same-host duplicate refused by the local lock even offline; same-session re-acquire keeps the nonce;
an unlanded push after a renew is not trusted; no session id refused; release by a non-holder refused; a held lease without
holder or expiry is ambiguous; an email-shaped account never reaches trunk; desk sweep / sync ship / sync claim exit 3 for a
Pipeliner without the lease (also spelled `pipeliner`); holder passes guard, other machine refused naming
JIS-NUC; non-singleton unaffected; banner shows the holder. Fail-first: on trunk the module does not exist (collection error);
with the new lease.py but trunk desk/sync/role_loader, the 2 wiring tests fail; the 4 review-fix tests fail on the lease.py
before those fixes (4 failed, run in a scratch copy). Regression: test_desk, test_sync,
test_role_loader, test_role_hook_launcher 120 passed.

## Part B: the allocator (was Traffic_Controller, now Pipeliner Job 2)
**Inventory** (`traffic_inventory.json`, no emails or runtime data): 3 machines (signal ids, branch prefixes, logins usable
there, what each may run), 3 Claude logins A/B/C (labels only), lanes codex (GPT, NUC), gemini-nuc, gemini-laptop (Lenovo,
hand-started), dsa; singleton preferences; pacing 60/70/80 (SUPERVISOR.md Pacing); liveness 30/180 min; 4 slots a machine.

**`traffic.py status [--json]`**: fetches trunk and the signal branch, then reports machines (ACTIVE <= 30 min since its
last signal, IDLE <= 180, else SILENT; open claims), both leases, the codex lane (`codex_run.py status`: on/off, STALLED,
allowance %, window pts/runs, ready), the gemini lane (running jobs, last end), budgets (BUDGET signal lines per login,
plus this login's `~/.claude/mts-budget.json`), desk pending per target (`desk.py sweep --json`), the dispatch queue
(`tasks.py dispatch --json`) and a PROPOSED allocation:
1. A singleton lease `unknown` -> operator line, run nothing as that role. Pipeliner lease free/expired with desk rows pending ->
   start one Pipeliner on JIS-NUC (else the first live machine).
2. Codex on, not at its run cap, allowance under 60% -> `codex_run.py tick` with the next CODEX card; under 8 ready ->
   Session_Planner refines.
3. Gemini idle -> the next CODEX card that needs commands/search/video, never the one just given to codex.
4. Each ACTIVE/IDLE machine: free slots (4 - open claims) filled with SONNET/HAIKU (+ JIS-NB lane on NB) cards; a machine whose
   logins are all at 80%+ gets nothing, 60-80% CRUCIAL only. Each card id is given to at most one worker.
5. A SILENT machine with open claims -> Pipeliner asks it by signal; claims are released only by their own rules.
A card proposed on one wake is reserved for 60 min (`~/.claude/mts-traffic-reserved.json`, local: the controller is a
singleton), so a second wake before the worker's claim lands does not hand it out again. With no BUDGET line for a machine's
logins it proposes one session there, not four. When the trunk or signal fetch fails, it proposes nothing (cached refs are
not current state). It proposes; it never starts, posts or ships, and reads the desk with a non-singleton role so it never
pushes a lease renew. Exit 1 when a source failed (the error is listed, never read as idle).

**`traffic.py measure [--hours N] [--json]`**: the table and duplicate list above.

**How it runs.** A session started as `You are Lead.` and loading pipeline mode (the old `You are Pipeliner.` still opens it); boot = acquire lease, `traffic.py status --json`, BUDGET
line. Each wake (note, signal, operator turn, the one background watcher): renew, status, act on PROPOSED in one message,
end the turn. No scheduler, no polling agent, no timer. Never messages Fable sessions, never deploys, restarts, touches HALT,
trades or releases others' claims. Leakage both ways: no runtime/order/account/secret/email data in commits, cards, signals or
prompts to GPT/Gemini/DSA; idle lanes, duplicate cards and polling are fixed in the allocation.

**Not done / limits.** Login-level budgets need tc3 BUDGET lines (until then `budgets` is empty and the allocation does not
throttle by login). Liveness counts signals only; the Lenovo sends few. Desk double-closes by a non-singleton writer need tc4.

## Review (independent, read-only) and what was folded in
Two reviewers on the same files: (G) GPT via `ask_model.py gpt --effort high` (Codex read-only sandbox, files copied to
`F:/MTS/ask/20261018T215346142386Z`), 9 findings; (S) a Sonnet agent with a read-only brief, 11 findings, verdict "do not ship
yet" on S1/S3. Every finding was checked against the code before it was accepted.

| # | Finding | Decision |
|---|---|---|
| S1 | renew/release kept the nonce, so a push error that did not land looked landed: two holders after expiry | ACCEPTED: fresh `write_id` per write, verified after a push error; test fails before, passes after |
| S3 | no session id = `HOST/nosession` shared by two runners, both "mine" | ACCEPTED: writes and `require` refuse without a session id (exit 4); test |
| S2, G2 | role detection: `roles[-1]` hides a singleton after another role is mentioned; `MTS_ROLE=pipeliner` skipped the exact-name check | ACCEPTED: any injected singleton wins, names canonicalised; test for the spelling. Rest of G2 (fail closed when no role is known) REJECTED: a session that never declared a role cannot be told from any other; lab runners get it via tc2 |
| S4 | local mutex can go stale while held (network inside it) and the stale break races | PARTLY: MUTEX_STALE 600 s (> a full CAS loop). The race stays: two sessions on one host have different keys, so the trunk CAS still refuses the second |
| S5 | no re-check during a long ship; skew assumed < 5 min | DOC ONLY: ship needs 20 min left at start and takeover needs expiry + 5 min, so a ~10 min ship cannot be overtaken unless clocks differ by more than 5 min; stated as a limit |
| S6 | `status` ran the guarded `desk.py sweep` in the session env: refusal swallowed as pending 0, or a renew push from a "read-only" tool | ACCEPTED: sweep runs as a non-singleton reader; its failure goes to `errors` |
| S7, G3 | stateless allocation re-proposes a card on the next wake; stale refs after a failed fetch still produce proposals | ACCEPTED: 60 min local reservation; no proposals when the fetch fails; test |
| S8, G6 | "cards worked by two lanes" counted claim -> release -> later lab run | ACCEPTED: overlap in time required; the published count fell from 12 to 2; test |
| S9 | held lease without holder/expiry read as expired; `codex_status` crashed on empty output | ACCEPTED: ambiguous (exit 4); empty output = unknown; test for the first |
| S10, G1, G9 | account names in the lease and in the inventory (public repo) | ACCEPTED: lease account is a short label (email-shaped -> `?`), inventory logins are A/B/C pointing at CLOUD_ACCOUNTS.md; test |
| S11 | doc said "foreign nonce" (code compares the key); release by a non-holder exited 0 | ACCEPTED: doc fixed; release by a non-holder refused; test |
| G4 | the local budget file was copied whole into status | ACCEPTED: numeric fields only |
| G5 | no BUDGET data = full allocation | ACCEPTED: one session a machine until a BUDGET line arrives; test |
| G7 | `measure` after a failed fetch reads like current data | ACCEPTED: `stale: true` and a STALE note |
| G8 | unreadable signal files skipped silently | ACCEPTED: counted and reported |

## Cards (ready, unfinished work)
| Card | Step | Worker | est_turns |
|---|---|---|---|
| tc2-lab-runners-set-lease-env | `gemini_queue.py`, `codex_run.py` and the Antigravity brief set `MTS_ROLE`/`MTS_LEASE_SESSION` when a card runs a role | session, Sonnet | 12 |
| tc3-budget-lines | every role boot sends `BUDGET login=<A/B/C> 5h=<n>% week=<n>%`; senders on NB/Lenovo set `MTS_ACCOUNT` | agent, Sonnet | 10 |
| tc4-desk-done-once | `desk.py done/take` refuse a row already closed on trunk (CAS on the row file, like the lease) | session, Sonnet | 15 |
| tc5-lab-lane-dedupe | `tasks.py dispatch` and `gemini_queue.py` skip a CODEX card with an open claim or a run in another lane | session, Sonnet | 15 |
| tc6-lenovo-git-email | Lenovo clone sets `user.email` that names DESKTOP-F7IU69N; inventory `authors` updated | agent, Haiku | 5 |
