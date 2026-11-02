# Simulator: operator requirements and fixes (demo 2026-11-02)

Context: the operator found the simulator "showed nothing useful" and asked for a guided demo (Eagle_Eyes relay, 2026-11-02). Two surfaces exist: the published results page (Artifact, read-only list of every test) and the local desk (`python MyTradingSys/research/sim_desk/desk.py`, settings + Run, DEV window only). One row per thing he asks for, his words verbatim.

Size: S = under an hour, M = a session, L = more than one session.

| # | His words (verbatim) | What it means | Size | Card id |
|---|---|---|---|---|

## Found before the demo (Opus, not his words)
| # | Gap | Size | Card id |
|---|---|---|---|
| P1 | The results page only replays trades already exported; the C30 page had a table and no trades. Fixed for C30 today (35 VALIDATION trades replay, H2 22 trades as a table). Most result files still show "no example trades exported". | M | |
| P2 | The pre-US pullback base rate (8f8e92f10) had no page row; added as `eagle-preus-pullback`. Per-day rows were never saved, so no example days. | S | |
| P3 | No real candle chart on the published page (only percent ladders and running totals); real charts exist only in the local desk (`desk.py`), which he may never have started. | M | |
