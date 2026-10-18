# Fable 5.1 pilot: usage bookkeeping (2026-10-15)

Session: Fable 5.1, effort high, JIS-NB worktree friendly-tereshkova-a255c3, claim `fable-pilot-pre-reg`. Task: PRE_REG.md + card
`gross-effect-screen-dev` (Q72, behind Q65). Operator rule: zero operator input; budget stop at +3 points on `Weekly - all models`.

| Check | UTC | 5-hour limit | Weekly - all models | Weekly - Fable | Context tokens |
|---|---|---|---|---|---|
| Start (after boot, before any read) | 2026-10-15T17:36Z | 46 % (reset 17:40Z) | 32 % | 0 % | 86k |
| Before ship (deliverable + card done) | 2026-10-15T17:43Z | 0 % (window reset at 17:40Z; new window to 22:40Z) | 32 % | 2 % | 178k |
| After ship landed (git cherry 0) | 2026-10-15T18:53Z | 14 % | 34 % | 3 % | 222k |

Delta over the whole pilot: all models +2 pts, Fable +3 pts. Budget stop (+3 on all models) not reached. The 5-hour window reset
during the session, so its first two readings are not comparable; the weekly columns are. The hour between the second and third
check went on shipping, not on the deliverable: the gate failed twice on inherited and self-made breakage (RELAY.md over its 6144 B
size cap after f0cc1f1a, fixed upstream by 45747d28 and taken as-is; my one-off make_card.py tripped the wiring orphan check and was
dropped), each gate run is 12 min, and one push lost the race once. The all-models weekly meter also carries the other sessions below.

Other sessions with activity between the two checks (`list_sessions`, excluding this one):
- `Fable 5.1 model usage and optimization` (local_1c4041fd, running, remote control on, last activity 17:43Z).
- No `Mts dispatcher` tick landed in the window: the last dispatcher activity is 17:08Z (ticks every 10 min per NEXT_SESSION.md; the 17:18-17:38Z ticks are not in the list). Last before start: `CBP analyst feed` 17:19Z, `Coordinator 2` 17:10Z.

Tool turns: 28 by the hook's count at the time of writing (hook cap 15; operator instruction for the pilot was end to end, so the
cap was not applied). Reads: three audit reports, TOM_ON_BTC.md, orderflow_views RESULT.md + study.py header/trade(), fees.py,
GO_LIVE_BAR.md, PRE_REG_VOLUME head, tasks.py, Q65 and G6 cards, NEXT_SESSION.md, LAYER_REBUILD_PLAN headings. No VALIDATION or
HOLDOUT bars, no market data, no production code.
