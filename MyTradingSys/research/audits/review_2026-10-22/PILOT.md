# 2-hour pilot: current Supervisor vs plain Sonnet + rule card (2026-10-22)

Question: do the extra roles and rules (Supervisor path) beat a plain session with a one-page card on time, waiting, context and rule-following? Not proven yet; this is the test (review step 8).

## Setup (operator, 2 minutes)
- Two NEW Sonnet sessions started within 5 minutes of each other, on two DIFFERENT logins (own budgets), same device type if possible. Note start time.
- Arm S (Supervisor), paste:
  `You are Supervisor. Login <A|B|C>. Pilot 2 hours, then stop and hand over. Tasks, in order: pipeliner-boot-diet, ai-behavior-fold-or-archive, tasks-sweep-closed-cards.`
- Arm P (plain), paste (no role line):
  `Read MyTradingSys/research/audits/review_2026-10-22/PILOT_RULE_CARD.md and follow it. Pilot 2 hours. Cards, in order: shot-py-store-path-nuc, gate-quarantine-expiry-cap, mid-turn-image-intake-gap.`
- Do not help either arm beyond answering a direct question. Same rule for both. Do not broadcast during the pilot.
- Known limit: the card sets differ (all small Sonnet cards); compare process, not lines of code. Swap the card sets in a second run if the result is close.

## Score (after 2 hours; I can compute 1-4 from the transcripts)
| # | Measure | How |
|---|---|---|
| 1 | First-turn context tokens | first_turn_tokens.py.txt |
| 2 | Minutes waiting on tools (ship, spawn) | wait_by_kind.py.txt, ship_calls.py.txt |
| 3 | Cards shipped to origin/fast-track in 2 h | `git log origin/fast-track --since` by card |
| 4 | Hook/banner/rule errors seen (ROLE NOT LOADED, denied spawn, CI red caused) | session_summary.py.txt |
| 5 | Operator corrections needed | count your messages that fix a mistake |
| 6 | Rules broken (card rule 3 fail-first test missing, rule 5 spawns) | read the diffs |

## Decision rule (set before the run)
- Plain wins if it ships >= the same cards with less waiting and fewer errors: then Supervisor is for multi-login budget pacing only, and roles shrink.
- Supervisor wins if it ships clearly more cards (>= 1.5x) without more errors: keep it, fix what the errors show.
- Otherwise rerun once with the card sets swapped.
