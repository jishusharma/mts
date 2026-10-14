# B176 - AIBridge auto-run refuses read-only python/node script blocks

Status: OPEN (filed 2026-10-11). Severity MED.
Source: BUGS.md row B176; Control Room inbox cul8u9eoqc0s86tt29e7.

## Verbatim ask

Auto-run must accept read-only script invocations.

## State

AIBridge lives at F:\AIBridge, outside the MTS repo. Fix 1 src\policy.json auto_write_regex: drop python|node|npm|mvn|pip (or narrow to python -c/node -e); proof: python scripts/dev/desk.py list auto-runs, Set-Content foo.txt x still refuses. Fix 2 src\agent.ps1 Read-Line/accept loop: ReceiveTimeout + try/finally close; proof: GET 127.0.0.1:7181 returns 404 within 1 s. Minor: add F:\AIBridge to policy roots; honor aibridge_autoran after reload (content.js:413); F:\AIBridge tree is dirty (10 modified, 20 untracked) - commit first. AIBridge edits are outside this repo and outside builder scope until the operator confirms; not a live-path MTS change.

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN row has a matching items/ file. State copied from the BUGS.md row.
