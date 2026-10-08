# T059 - PASTE SIZE GUARD AND AUTO-SPLIT

Register row: MyTradingSys/research/BUGS.md T059.
Opened: 2026-09-29 by session MTS-2026-09-29-1039Z.
Severity: LOW. Status: WONTFIX 2026-10-08 (see RECEIPT).

## PROBLEM

start-session.ps1 regenerates Dumps\SESSION_PASTE.txt every mts-start run,
but never splits it. Current paste is 135540 bytes (132.4 KB), over the
DSA_SESSION_PROMPT.md section-2 150 KB threshold. Operator splits by hand.

## EVIDENCE (2026-09-29 revalidate)

- Paste mtime 2026-09-29 16:09:06 IST, bytes 135540, lines 2864.
- BUILD_REPORT.md mtime 16:09:00, six seconds before the paste.
- current_market_state.md and state_code.json moved 134 min after the paste;
  the paste is a frozen snapshot, not a live document.

## FIX

NUC spec 121-paste-size-guard: when block > 150 KB, split at the nearest
top-level "### " boundary to the midpoint, write part1/part2/HEAD, keep
the original SESSION_PASTE.txt for path-compatible tools.

## RECEIPT

WONTFIX 2026-10-08, operator (MTS-2026-10-08-0806Z-APP-BLD-dsa-direct-mode): "i do not care if sessionpaste is 100kb or 250 kb - it should work".
No split. DSA_SESSION_PROMPT.md section 2 now says paste size is not a limit; the warning in
scripts/start-session.ps1 and the check in scripts/sched/check_paste_size.py moved from 80/150 KB to 400 KB.
Guard: MyTradingSys/tests/test_dsa_direct_mode.py::test_paste_size_alarms_sit_above_250_kb.

# END