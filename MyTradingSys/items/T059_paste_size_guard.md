# T059 - PASTE SIZE GUARD AND AUTO-SPLIT

Register row: MyTradingSys/research/BUGS.md T059.
Opened: 2026-09-29 by session MTS-2026-09-29-1039Z.
Severity: LOW. Status: OPEN (NUC spec 121-paste-size-guard running).

## PROBLEM

start-session.ps1 regenerates Dumps\SESSION_PASTE.txt every mts-start run,
but never splits it. Current paste is 135540 bytes (132.4 KB), over the
DSA_SESSION_PROMPT.md section-2 80 KB threshold. Operator splits by hand.

## EVIDENCE (2026-09-29 revalidate)

- Paste mtime 2026-09-29 16:09:06 IST, bytes 135540, lines 2864.
- BUILD_REPORT.md mtime 16:09:00, six seconds before the paste.
- current_market_state.md and state_code.json moved 134 min after the paste;
  the paste is a frozen snapshot, not a live document.

## FIX

NUC spec 121-paste-size-guard: when block > 80 KB, split at the nearest
top-level "### " boundary to the midpoint, write part1/part2/HEAD, keep
the original SESSION_PASTE.txt for path-compatible tools.

## RECEIPT

Pending. Verify with: python scripts\worker\queue_tool.py verify 121-paste-size-guard

# END