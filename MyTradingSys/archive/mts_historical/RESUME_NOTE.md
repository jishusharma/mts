# RESUME NOTE
# Written 2026-09-19T08:25Z by MTS-2026-09-19-0755Z.
# Read after boot. Then read BUGS.md for the queue.

## WHAT WE WERE DOING

Preparing manual alerts for live entry. Operator trades on a different
exchange, reads the alert, places the order himself. No order code needed.

## IN-FLIGHT

1. Verify Build-Card SESSION and US_OPEN lines appear on a live alert.
   Code landed at dc1a239, loaded by loop restart at 07:48:30Z.
   No alert has fired since the restart.
   Action: read .\runtime_data\last_alert.json after any alert fires.
   Expect two lines: "SESSION: <name>" and "US_OPEN: <N> min".
   If missing, stop and report.

2. Card payload improvement (deferred, not started).
   Three fields exist on the snapshot but are not on the card:
     $top.math.distance_pct   (proximity to entry)
     $v.regime                (TREND_UP / RANGE / TREND_DOWN)
     $top.score.raw/confidence (already computed, e.g. 95 / B)
   Decision pending: add these to Build-Card? Three lines, no engine change.
   This is the "option B" from the 0552Z session. Option A (WATCH popup
   suppression) is a separate smaller change.

3. Queue is B003, B044, T032, T033, T034, T035. Read BUGS.md for titles.

## STALE ITEMS TO FIX

DSA section 11 close time says 07:51Z. Actual close was 07:54:22Z.
Commit 6a8dad5 has a false message; corrected by dc1a239; journal records it.
Both low priority.

## RUNTIME AT NOTE WRITE

Lock 15296, java 5928. No supervisor. Build PASS.
Latest snapshot around 08:20Z. Verdict WAIT_RR on ct_long @ daily_val.

# END
