# MODEL ALIGNMENT - 2026-09-21

Written 2026-09-21 by MTS-2026-09-21-0721Z. Carry-forward from the
MTS-2026-09-21-0444Z close note.

Two tags used throughout.
DISK: supported by a file on this machine, cited by path and line.
UNVERIFIED-WEB: about remote documentation. No web search was run. This
surface has no web tool. Every web claim carries this tag.

---

## 1. Reasoning effort per task

DISK: no per-task effort rule exists. Sweep of DSA_SESSION_PROMPT.md for
effort|reasoning|thinking returned one hit, line 92, unrelated (routing a
verify to a reasoning surface). DSA is 232 lines, 8764 bytes.

WEB: low / high / max effort tiers. UNVERIFIED-WEB.

Gap: real on disk. If the surface exposes effort control, no rule uses it.

## 2. System prompt placement

DISK: SESSION_PASTE.txt is built once per session by
scripts/start-session.ps1 (319 lines). No re-injection path exists. The
trading loop scripts/core/start-trading-day.ps1 never re-reads
DSA_SESSION_PROMPT.md.

WEB: mid-session instruction drift, reduced by periodic re-injection.
UNVERIFIED-WEB.

Gap: partial. Mechanism absent. Whether it is needed has no disk evidence.

## 3. Instruction decay past N tokens

DISK: DSA is 232 lines, 8764 bytes. No token measurement exists on disk.
No file defines N. Sweep for token returned zero rule hits.

WEB: 750-token threshold. UNVERIFIED-WEB.

Gap: real on disk, but the trigger number is not set by any file. Before
any rule, measure the token count of DSA and of a typical boot paste.

## 4. Context self-conditioning

DISK: no pruning rule exists. DSA section 5b limits verify claims to three
kinds. DSA section 9 limits prose. Neither removes a failed step from the
conversation. No script trims the chat.

WEB: context self-conditioning, negative-example contamination.
UNVERIFIED-WEB.

Gap: real on disk. Failed steps stay in the paste chain. The mitigation, if
wanted, is a compact "what is already settled" line in each turn.

## 5. Thinking mode toggle

DISK: no per-task thinking-mode rule exists. Sweep of DSA for thinking
returned zero rule hits.

WEB: extended thinking on/off per request. UNVERIFIED-WEB.

Gap: real on disk. If the surface exposes this, no rule uses it.

## 6. Pre-committed chain - does this surface support it

Question: does this surface support pre-committed mechanical chains without
losing intermediate state. If yes, which MTS operations convert and what is
the measured turn reduction. If no, what breaks.

Answer, disk evidence from session MTS-2026-09-21-0444Z (commit 0947724).

YES, with two guards. Measured evidence:

- Journal entry, DSA section 11, runtime snapshot, and Build-Check landed in
  one paste block. Previously this took many turns. Turn count fell.
- Two clipboard re-entries occurred that session. Both were caught by
  anchor-count checks before any write landed. Without the anchor check,
  duplicate applies would have corrupted files.

Convertible operations (done this session):

- Append a journal entry and update DSA section 11 in one block.
- Write a batch of independent file edits where each anchor is unique.
- Run a verification block that reads only.

What breaks:

- A single-line anchor that survives its own replacement can apply twice on
  a re-pasted block. Guard: anchor-count must be 1.
- A here-string over 30 lines corrupts on paste. Two blocks in 0947724 lost
  their tail for this reason. Guard: keep each here-string under 30 lines, or
  use a temp file.

Measured turn reduction: not numerically captured this session. Only the
qualitative before/after exists. To make the number real, the next pre-
committed chain must log a turn count at start and end.

---

END