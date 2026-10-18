# NUC -> NB hand-off, 2026-10-16 ~15:45Z (shared plan, pilot of NUC_NB_LINK.md)

From the JIS-NUC super session (lagging tasks + layer readiness). Read with `NUC_NB_LINK.md` and
`research/layer_readiness_2026-10-16/LIVE_CHECK.md`.

## State at hand-off (mirror@2026-10-16 15:41Z)
- Live tree on fc9794f4 (contains W3 wiring). Flags raised: HALT, HALT_DAILY_LOSS. No trades since 09:50Z; runner errors 0.
- The live runner process dates from 10:21Z, before W3 (10:58Z). The 5 new layers (rsi_divergence, session_levels,
  bb_top_reversal, candle_close, levels) are NOT loaded: no poll line carries their keys. wlow_bounce (new side) is loaded.
- Cause: AutoDeploy killed `live_runner_cli.py`, the runner runs as `-m ...alerts.live_runner_cli`. Fixed twice on
  fast-track (NUC LIVE_CHECK fix, NB 692afe63); takes effect only on a deploy that touches alerts/ or a stale-restart.
- Offline, all 6 new layers pass `auto_trader.layer_signal` with the real config (20/2 size, jishu_21, grandfathered in
  `pre_pipeline_sources` until review_by 2026-10-23).

## NB (live-path owner) - in this order
1. Restart the alert runner per DEPLOY_RUNBOOK (manual fallback) or let AutoDeploy deploy the current tip; then check the
   next mirror: the poll line shows the 5 new layer keys (27 keys total). Signal `[nb->nuc] runner: restarted, <n> keys`.
2. HALT and HALT_DAILY_LOSS: operator decision; nothing on NUC depends on it except seeing the new layers trade.
3. Fabio v3_grid 1m: 72 variants reject as `unmapped fabio:v3_*` every 45 min (no `layer_rules` entry). Decide: add a rule,
   or mark the family `collection_only` so it stops filling the reject log. (Fabio is excluded on NUC.)
4. NEXT_SESSION.md: drop Q76, Q77, Q78, Q79 (already shipped: bbffceda, 6bd38b55, 3b3ea9df; Q78 by the lab fixer). Keep Q75
   and Q73 (live path, NB).
5. Routine: read `mts_signal.py read --hours 3` at the start of each coordinator turn; answer `ask` lines within one turn.

## NUC - in this order
1. After NB's restart signal: re-run the live check on the next mirror (new keys present, decisions from the 6 new sources,
   rejects only for HALT) and append to LIVE_CHECK.md.
2. GPT lab: keep 8+ ready build cards (10 ready now: bigtrade, OI-delta, candle patterns, volume, context V2 fixes); repair
   BLOCKED cards each wake. Spend guard now 10 runs/window, 60 week pts.
3. Research leftovers: pit-levels zone grid/weighting standardisation (needs an operator choice; ZONE_MISMATCH.md);
   bigtrade stays NO-SOURCE (BIGTRADE_SPEC.md) until a sourced rule turns up.
4. Layer-rebuild plan s6 items that are not Tom/Fabio and not live path, after checking claims and the last 24 h of commits.

## Shared rules (both sides)
- Before starting any queue item: check claims (`sync.py where`) and the last 24 h of fast-track commits for its id; skip if hit.
- Whoever ships a queue item removes it from NEXT_SESSION.md in the same ship.
- Never make the operator click a card; worker type per WORKERS.md (session default, Agent only size S).
- Live path, deploy, restart, HALT: NB only. Research, lab feeding, verification off the mirror: NUC.
