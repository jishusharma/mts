# B092 - DSA write batching

Status: OPEN. Severity: MED. Opened 2026-10-03.

## Defect

DSA appends a Build-Check gate and a gitsnap commit to every write
block. When the operator plans multiple writes before a single
commit, each write pays ~45 seconds of wall time plus a dirty-tree
handling pass. Over a multi-step session this is dozens of wasted
cycles and dozens of tree-dirt events.

The pattern is not a policy in DSA_SESSION_PROMPT.md. It is
habit. Section 6 (WRITING) says "verify by a method other than the
one used to write" and "Report line count, byte count, and
non-ASCII count" but does not say when to gate and commit. DSA
added the gate+commit habit on its own.

## Evidence

Session MTS-2026-10-03-0430Z-DSA-COO. Every write block ended with
Build-Check plus gitsnap, including blocks the operator did not
intend to commit yet.

Timing per Build-Check run (B091 evidence):
  Java compile:  PASS 3.2s
  Math tests:    PASS 219/219 38.5s
  Doc tests:     PASS 5/5 2.2s
  Wall: ~45s.

Tree side effects per cycle: BUILD_REPORT.md rewritten and
session_log.json rewritten; gitsnap warns CRLF->LF on both.

## Fix (Claude decides wording and placement)

Add section 6b "BATCHING" to DSA_SESSION_PROMPT.md. Proposed text:

  Do not append a Build-Check and gitsnap block to every write.
  One gate, one commit, per batch.

  Write blocks end with the write and its verify only. DSA states
  what changed and stops. No gate command, no commit command.

  Print the gate and commit block only when:
    - the operator says gate, commit, or close
    - the session is closing
    - a push to origin is next
    - a change touches a live path or a critical file and the
      operator has said the change ships now

  When gate runs and STATUS is PASS, gitsnap runs in the same block.
  Batches can be one file or twenty.

  Exception kept: any write to a critical file (section 6 list)
  still carries hash-before, edit, hash-after, diff, in the same
  block. That is integrity, not gating.

Operator-side cost, stated in the section:
  The operator must say "gate" before a reboot, or uncommitted work
  sits on disk across the power-off.

## Receipt
## Guard shape (operator 2026-10-03)

Every gate+commit block is guarded. Run Build-Check, then:

    if (Select-String -Path MyTradingSys\runtime\BUILD_REPORT.md -Pattern "STATUS: FAIL" -Quiet) {
      "ABORT: Build-Check FAIL"; return
    }
    gitsnap "..."

Observed 2026-10-03 13:08Z: a commit landed while STATUS was FAIL
because the block had no guard. The guard is the shape of the gate.
Applies to combined prompts too: any block that gates and then
commits must abort on FAIL before the commit line runs.
# END
