# MTS PLAYBOOK - reference card
# Updated 2026-09-20 from session MTS-2026-09-20-0541Z.

---

## Every reply - baseline
*   Answer the question asked. Do not redirect to a checklist.
*   Paste is truth. If a number is not in the paste, it is not known.
*   One decision per reply. All reads for that decision go in one block.
*   Do not ask the same question twice. Note it pending.
*   Corrections are one line. No filler. No apologies. No emoji.
*   No invented commands or aliases.

---

## When starting - orient first
*   What is it - how does it work? Current state - what remains?
*   Plan -> validate vs req -> test -> compare -> fix -> retest -> done. No skip.
*   Evidence format: command, output, reason.
*   Before change: confirm sense. After change: confirm no regression.
*   Ambiguous -> stop, ask. Do not guess.

---

## Task library - call by name
*   BOOT - read paste, list files, run Build-Check, state role + mission + first action.
*   VALIDATE - restate request, list reqs, read disk, compare, propose minimal change, list tests, stop.
*   READ FILE - name range, one batch, cite range, quote verbatim.
*   WRITE FILE - hash before, detect endings, re-read anchor (count=1), compose .new, diff, splice, hash after, BOM check, Build-Check.
*   POSITION - fresh panel every reply, never memory. Retract prior math if size changed. Levels from disk only. Stop on the book, not in the plan. State isolated/cross once.
*   LIVE MONITOR - one feed cycle, report deltas (price, CVD, ND, OI, state), no change if none.
*   MOMENTUM - CVD slope + OI dir + ND 1m/5m/15m/1h + state. Map to one of six states: trend up / squeeze / distribution / trend down / long-liq / accumulation. State 30-min implication.
*   IMAGE - 7 layers: panel ID, neutral, cross-view, HTF, bias check, invalidation, disk cross-check. Label chart-reads vs system-reads. liquidation_clusters deprecated.
*   WORKER - DISPATCH.md, R1-R5, receipt tags, no checks executed, Confirmed coordinator-only.
*   BUG - confirm from disk, next ID, append before # END, verify tail.
*   WRAP - ledger + repo state + BUGS tail + log tail, one block, proof inline.
*   SESSION CLOSE - stop-day, mts-live-stop, section 11, ledger, Build-Check, gitsnap. Do not close on FAIL.

---

## Position discipline (added 2026-09-20)
*   Recompute from the live panel every reply. Never from the last turn.
*   If size changed, retract the prior exit math in one line and recompute.
*   Isolated or cross: recorded once. Do not re-ask.
*   Exit levels come from disk (VAH / VAL / swing) or the operator. Never invented.
*   A stop in the plan is not a stop. Say so once, do not repeat.

---

## Audit lenses
*   Scope - what is it, how works, what remains.
*   Behavior - does the change need a new test?
*   Artifacts - who consumes this output? Is it consumed?
*   Data integrity - does the AI have confirmed inputs at every step?
*   Domain:
    1. higher-lows / lower-highs tracked as sequences?
    2. expected outcome - did it play out?
    3. higher / lower frame agree?
    4. live alerts - break, approach, divergence, indicator state.

---

## Commands - most used

    # SESSION OPEN
    .\scripts\start-session.ps1
    mts-live

    # ORIENT (batch)
    quick
    health
    alerts

    # PULSE (any time)
    Get-Content .\runtime_data\apparatus_log.txt -Tail 30
    Get-Content .\MyTradingSys\runtime\current_market_state.md -Tail 40
    Get-Content .\MyTradingSys\research\BUGS.md -Tail 30

    # BEFORE WRITE
    .\scripts\Build-Check.ps1

    # AFTER WRITE
    "hash:  " + (Get-FileHash $path -Algorithm SHA256).Hash
    "lines: " + ([IO.File]::ReadAllLines($path).Count)

    # LOOP CONTROL (single command each, never combined)
    .\scripts\core\stop-day.ps1
    .\scripts\core\mode.ps1 -M armed

    # SNAPSHOT
    gitsnap "one line"
    gitsee

    # SESSION CLOSE
    .\scripts\core\stop-day.ps1
    mts-live-stop
    gitsnap "close: one line"

---

# END
