# SPEC: "Start DSA bridge" typed as the first line of a new DeepSeek chat boots DSA (card aibridge-start-dsa-trigger-1107)

Operator order 2026-11-07 (q-9d225e, relayed by B): no terminal, no clipboard paste. Today a new chat needs `python scripts/dev/dsa.py
start --open` (seed on the clipboard, paste, Enter). Supersedes card aibridge-posts-the-dsa-seed-itself-zero- (that one still needed a
terminal).

Lives in MyTradingSys/system, not scripts/aibridge/docs: every file there is bridge payload, fingerprinted by RELEASES.json and
installed by aibridge_install.py (the first placement broke CI at d04560aa0, reverted).

## Behaviour
1. In a DeepSeek chat tab with the AIBridge panel (hands-free box) the user types exactly `Start DSA bridge` (case-insensitive; a
   trailing `.` or `!` allowed; nothing else in the message) and presses Enter.
2. The extension intercepts that send BEFORE it reaches DeepSeek, asks the loopback agent for the seed, replaces the composer text
   with the seed and sends it. DSA then boots through its first bridge block, prints the BOOT banner and WAITS for an order
   (d-dsa-seed-then-wait-1107). Nothing else changes in the chat flow.
3. If the agent is down or refuses, the extension sends nothing and shows one line in the panel: `agent down: run aibridge_install.py
   --restart-agent`; the typed phrase stays in the composer.

## Pieces
| Piece | Where | Rule |
|---|---|---|
| `GET /seed` | `scripts/aibridge/src/agent.ps1` | same token check as `/run`; runs `python scripts/dev/dsa.py start --print` in the repo root the agent already uses; returns text/plain; 10 s timeout; audit line like the other routes |
| trigger + swap | `scripts/aibridge/extension/content.js` (or `loop.js`, wherever the composer send is already observed) | exact-phrase matcher as a pure function; seed fetched through the existing agent-call path (token handling stays where it is today); composer text replaced, then the normal send |
| version | `manifest.json` 0.7.30, `RELEASES.json` current 0.7.30 + note | installer reads `current` |
| tests | `scripts/aibridge/tests/` | matcher: phrase, case, dot, NOT a longer sentence, NOT a second message; `/seed`: token required, returns the dsa.py output (fake python); both fail on the pre-change tree |
| docs | `MyTradingSys/system/AIBRIDGE_LANE.md` | one paragraph "Start DSA bridge" + the fallback line |
| rollout | this machine: `python scripts/dev/aibridge_install.py --restart-agent`, `aibridge_health.py` UP 0.7.30; other hosts: `mts_signal.py broadcast --cmd "python scripts/dev/aibridge_install.py --restart-agent"` | the operator reloads the extension once per Chrome profile (chrome://extensions, reload) |

## Never
- Open, print or diff `F:/AIBridge/extension/background.js` or `F:/AIBridge/src/config.json` (bridge token). The repo copies are
  edited only if the agent-call path lives there; the token stays a placeholder; no token in any log, test or commit.
- Write anything into a DeepSeek chat other than the seed; no live tree; no HALT; no orders.

## Done when
Typing `Start DSA bridge` in a fresh chat on this machine produces the BOOT banner with no terminal and no paste (checked by the
builder through Claude in Chrome on the Profile 4 tab, or reported as "install done, chat check pending" if that tab is busy);
tests green; health UP 0.7.30; shipped with `Result:` and `Next: END: operator reloads the extension; NUC/laptop run the broadcast`.

## The list rule (card dsa-seed-full-task-list-1107)
`dsa.py start --print` appends, under the 4000-byte seed cap, a DSA QUEUE (every open card in lanes DSA, DSA-NB, DSA-NUC plus every
open desk row addressed to them, both hosts, from the repo files only) and DSA FILED (the 5 newest cards whose provenance field
names DSA: `tasks.py new ... --source "DSA chat <host>"`). Overflow prints `+N more`. The filer is not otherwise recorded on a
card, so older DSA filings are NOT_IN_DATA, never guessed. Data from the other host's checkout is not read: what the repo holds is listed.
