# D8. A simpler way of running the work (machines, accounts, lists)

Constraint from the operator (q17 note): "I need flexibility to run any a/c on any machine", one more account coming.
HOW_MTS_RUNS.md P1-P5 and q17 were prior thinking; this proposal starts from the measured waste instead.

## The waste (RESULT)
- Bookkeeping commits: 44 % of trunk commits in the last 24 h (STATUS.md 2026-10-20); 68 % / 60 % / 64 % on the
  TRAFFIC_BUSTERS baselines; 1,246 commits 10-01..10-13 at 44 % bookkeeping (HOW_MTS_RUNS.md).
- Five lists plus BUGS plus claims plus the Control Room inbox: 462 card files, 17 desk rows (7 untouched for 4 days),
  8 Codex rows, 71 OPEN bugs, 5 inbox entries, a 19.7 KB NEXT_SESSION.md.
- 63 worktrees, 24 branches ahead of trunk, 14 ships at once on 8 CPUs (FLOW_2026-10-20.md).
- Fixed cost 70-80k tokens per coordinator turn (SUPER_SESSION.md audit): 4,077 turns in 24 h.

## The proposal (six rules, replacing the lists above)
1. One work list: task cards. The desk, the Codex queue, the Control Room backlog and the inbox become card fields
   (lane, worker, est_turns, operator_note). Done cards leave the live folder (tasks-sweep-closed-cards). BUGS.md rows
   become cards with a stage tag or are closed (D1 section 4).
2. One dispatcher: the human-started coordinator. It reads cards, not NEXT_SESSION.md. NEXT_SESSION.md shrinks to one
   hand-over block of at most 40 lines; older blocks are deleted on each ship, not appended.
3. One ship gate per machine (unjam branch), FIFO, bounded. Every worker ships through it once per task (B3). Claims
   move off trunk (q17 P4) so a claim is a local file, not a commit: this alone removes most of the 44 %.
4. Any account on any machine: the account is a login, the machine is a tree. The gate is per machine, the card is per
   task, the lane is a model name, never a login name. A login logs in wherever budget is (CLOUD_ACCOUNTS.md), picks the
   next card, works in a worktree, ships. Nothing in a card names a login; traffic_inventory.json maps what ran where,
   after the fact.
5. Lanes collapse to three: Claude (Sonnet default, Haiku mechanical, Opus by name), Codex (prepaid, cross-vendor reviewer
   and lab runner while its queue is below 8), Operator (eye-reads, decisions, keys). DSA/Gemini and the DeepSeek AIBridge
   lane are retired unless their rows drain in S0 (7 DSA-NB rows untouched 4 days; AIBridge rows 93 h stale).
6. Two pages: the decision page (questions with yes/no/change, one line per stage per week) and STATUS.md. Every other
   generated page stops being rebuilt; the artifacts rebuild branch is shipped once and then not maintained.

## Measures (the only four, read weekly from STATUS.md)
| Measure | Today | S0 exit |
|---|---|---|
| bookkeeping share of trunk commits | 44 % | < 30 % |
| ship p90 on JIS-NB (traffic_report.py) | 137 min slots on 2026-10-20 | < 20 min |
| ready cards | 48 | <= 15 |
| stale claims | 3 | 0 |

## What this does not change
Testnet only; the live tree changes only by a deploy; builders never deploy; no scheduled tasks or routines (the keeper list
in q-v1-keepers is the one explicit exception, in writing, with an owner); public repo rules. The same rules, fewer places
to read them.
