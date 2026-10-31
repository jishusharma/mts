# ci_watch MIN_STREAK: block after the first red or the second? (measured 2026-10-31)

Source: `gh run list --branch fast-track --limit 300 --json headSha,conclusion,createdAt` (public repo, read-only),
parsed by script, counted (not read off truncated output). 300 pushes; 6 in-flight/cancelled excluded.

| Count | Value |
|---|---|
| runs: success / failure / cancelled / in flight | 213 / 81 / 2 / 4 |
| red streaks (consecutive failures) | 27: length 1 x12, 2 x5, 3 x2, 4 x2, 5 x1, 6 x1, 7 x2, 9 x1, 11 x1 |
| pushes created inside some red's CI window | 68 |
| pushes blocked with MIN_STREAK=1 | 74 |
| pushes blocked with MIN_STREAK=2 (today) | 37 |
| gained by MIN_STREAK=1 (pushes in multi-red streaks) | 18 |
| false blocks by MIN_STREAK=1 (single-red episodes later superseded by green) | 19 |

Card window (10-30 21:31Z .. 10-31 08:10Z) reproduces 26 reds; the card's "17 innocent pushes" measures as 18 pushes landing inside a red's CI
window (window-definition difference).

Verdict: **keep 2**. Going to 1 gains 18 early blocks and costs 19 false blocks (12 single-red episodes cleared by the next green): no net gain.
Reds that matter are caught by the CI RED rule (first to see reverts). OURS: the default is kept; no code change.

Measured by a Haiku MTS_Doctor (script and runs.json were in its scratchpad); the supervisor reran the script on the same data and got the same counts.
