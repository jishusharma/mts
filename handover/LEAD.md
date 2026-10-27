# Lead hand-over (2026-10-27, JIS-NUC gateway)

ROLE LOADED: Lead v1 · token star-door · MyTradingSys/system/roles/lead.md @ 604619a1

Discussions closed this session:
- **JIS-NUC hardware verdict (nec-hw-diagnosis).** Operator asked whether to sell the NUC: 14 watchdog resets in 4 days (4 in 2 h today), heat/idle/memory/disk ruled out by the 10-25 idle logger row, socket fix did not stop it; adapter (DC delivery) still the leading suspect. Default taken: order the 19 V 120 W 5.5x2.5 adapter as the single-variable 48 h test, then BIOS 0067 + CR2032 in one attended window; sell only on a confirmed board DC-DC/VRM failure. Logged `d-nuc-hw-verdict` (OPERATOR_DECISIONS.md), empirical verdict table added to NUC_SHUTDOWN_HANDOVER.md, signal to all hosts pausing heavy NUC routing until the 48 h check. Logged in `0b8af54e`/`51908bdb`, main-checkout has zero unshipped commits (data loss = F: re-copy only).
- **CI-REVERT was a stale alarm.** The doctor's 6-WARN line carried `trunk is red now since d39c665a`, but trunk has since moved to `604619a1` and its CI run (`40394946045`, success 2026-10-26 20:21Z) is green. No revert needed; the red at `d39c665a` was superseded by the next green ship. Recorded in the re-run doctor report (shipped `b6ae603a`).
- **The 5 "WAITING-ON-OPERATOR" cards are stale tags, not open decisions.** `java-popups`, `machine-rename-aliases`, `move-live-host-generated-files-status-md`, `state-code-accumulator-backfill`, `supervisor-handover-fixed-form` all read `STATE STALE` with real work already shipped on top of them. Clear them with `tasks.py tag <id> --refresh` (mechanical, no operator input), not by asking the operator.

Next Lead (one mode, then a worker):
- Load **pipeline** mode, keep the NUC busy per GATEWAY_NUC (gateway up, login B off, NUC takes the next card on ship). Top of queue = the p1 bugs `bug-station-session-stops-after-one-task` / `bug-instruction-conflicts-not-logged`, or the p1 `bug-lease-blocks-lead-ship-after-pipeline-mode` (note: I am NOT in pipeline mode, so that lease bug does not block my ship — it only bites a Lead that loaded pipeline mode to look at the desk while another host holds the Pipeliner lease).
- Hand-over pointer from the last Fable map session: the next reviewer starts the **confluence review from `FABLE_CONFLUENCE_MAP.md`** (pairs to deduplicate are at the bottom of it). If the operator names it, start there instead of the p1 bugs.

Open health (doctor, non-blocking, route not act):
- HOOK-REG: main checkout is 70 commits behind `origin/fast-track` (limit 50) → `git pull --ff-only` on the primary checkout (JIS-NB side, not from a worktree).
- STALE-CLAIMS: 50 over 24 h → `sync.py release <slug>` from the owner host, or ask the owner; do not force-release others' claims from a gateway session.
- BROADCAST: 8 jis-laptop signals unacked (22-33 h) → run the cmd on the laptop and `mts_signal.py ack <id> done`; no session is on that host, so it is a by-hand step.
