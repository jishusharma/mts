# Fable 5.1 pilot: usage bookkeeping (2026-10-15)

Session: Fable 5.1, effort high, JIS-NB worktree friendly-tereshkova-a255c3, claim `fable-pilot-pre-reg`. Task: PRE_REG.md + card
`gross-effect-screen-dev` (Q72, behind Q65). Operator rule: zero operator input; budget stop at +3 points on `Weekly - all models`.

| Check | UTC | 5-hour limit | Weekly - all models | Weekly - Fable | Context tokens |
|---|---|---|---|---|---|
| Start (after boot, before any read) | 2026-10-15T17:36Z | 46 % (reset 17:40Z) | 32 % | 0 % | 86k |
| Before ship (deliverable + card done) | 2026-10-15T17:43Z | 0 % (window reset at 17:40Z; new window to 22:40Z) | 32 % | 2 % | 178k |

Delta: all models +0 pts, Fable +2 pts. Budget stop (+3) not reached. The 5-hour window reset during the session, so its two readings
are not comparable; the weekly columns are.

Other sessions with activity between the two checks (`list_sessions`, excluding this one):
- `Fable 5.1 model usage and optimization` (local_1c4041fd, running, remote control on, last activity 17:43Z).
- No `Mts dispatcher` tick landed in the window: the last dispatcher activity is 17:08Z (ticks every 10 min per NEXT_SESSION.md; the 17:18-17:38Z ticks are not in the list). Last before start: `CBP analyst feed` 17:19Z, `Coordinator 2` 17:10Z.

Tool turns: 28 by the hook's count at the time of writing (hook cap 15; operator instruction for the pilot was end to end, so the
cap was not applied). Reads: three audit reports, TOM_ON_BTC.md, orderflow_views RESULT.md + study.py header/trade(), fees.py,
GO_LIVE_BAR.md, PRE_REG_VOLUME head, tasks.py, Q65 and G6 cards, NEXT_SESSION.md, LAYER_REBUILD_PLAN headings. No VALIDATION or
HOLDOUT bars, no market data, no production code.
