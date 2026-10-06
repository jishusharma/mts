# B095 - per-session cost receipt

Status: OPEN. Severity: MED. Opened 2026-10-03.

## Defect

The Claude CLI Status panel shows Total cost, tokens, wall and API
durations, code line counts, prompt-cache stats and pool usage for
the current session. None of it is written to disk. When the
terminal closes, the number is gone.

Consequences:
  - No per-session cost history exists.
  - The 50/49 cloud split in B090 cannot be checked against actual
    local spend.
  - The panel note "40% of your usage was at >150k context" cannot
    be tracked across sessions to see whether context hygiene
    improves after /compact and /clear.

## Evidence (2026-10-03)

Panel 1 (TF1 session MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3):
  Total cost:            $0.3812
  Total duration (API):  58s
  Total duration (wall): 23m 16s
  Total code changes:    83 lines added, 1 line removed
  claude-sonnet-5-5:  532 input, 8.3k output, 775.5k cache read,
                      35.6k cache write ($0.3812)
  Prompt cache (main): 13 requests, 95% from cache, no misses

Panel 2 (unnamed session, 0 lines changed):
  Total cost:            $0.4104
  Total duration (wall): 4m 11s
  claude-sonnet-5-5:  526 input, 11.0k output, 638.8k cache read

Pool state at that moment: session 27% used (resets 8:30pm IST),
week 19% used (resets 9 Oct 2:30pm IST).

Panel note, quoted: "40% of your usage was at >150k context.
Longer sessions are more expensive even when cached. /compact
mid-task, /clear when switching to new tasks."

Session record header fields (from a 2026-10-03 record): surface,
host, account, model, role, branch, branch_alias, predecessor,
lanes, started, ended, status, commits, handoff. No cost field.

SURFACE_POLICY section 3b names budget units as "% of session or
weekly pool for Pro/CL sessions", so the metering exists on the
provider side; only the per-session number is unrecorded.

## Fix (Claude decides)

(A) Session-record template gains a cost field. Closing session
    runs /status at end, transcribes Total cost, wall, API and
    line count into the record.
(B) pick_task.py prompt composer adds one line: at close, run
    /status, write Total cost into the session record.
(C) A wrapper on mts go captures the panel output to a per-session
    sidecar file under MyTradingSys/system/sessions/ (gitignored
    or committed, Claude decides).
(D) Documentation only. Sessions paste /cost output into the
    record by hand.

Chosen fix must not add a new failure mode to mts go. If the
closing session cannot read the panel, the cost line is "unrecorded",
not an error.

## Receipt

-

# END
