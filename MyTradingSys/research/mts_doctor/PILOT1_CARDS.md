# PILOT 1 frozen card list (start condition 3) - Session_Planner, 2026-10-24

Frozen: 6/6. Do not add, swap or edit these cards before the pilot starts. All six: STATE ready (`tasks.py check` passes), no live claim, run on JIS-NB alone (F:/MTS/data and F:/ are on NB; no NUC, no desktop data), all non-live-path, all Sonnet, est_turns total 140.
Disjointness: written files below were compared pairwise by path prefix (script, 0 overlaps). `F:/MTS/data` is read-only for both dsa cards.

| # | id | files written | live-path | est_turns | worker | weight / review |
|---|---|---|---|---|---|---|
| 1 | `t02-f1-review-allowlist-chunk-4` | `scripts/dev/lookahead_allowlist.tsv` (own 30 rows), `research/dsa_backtest_audit_2026-10-16/T02_F1_unsafe.md` | n | 22 | session, Sonnet | ROUTINE, none |
| 2 | `find-gemini-antigravity-quota-command-an` | `research/thinker/2026-10-23_gemini_quota_find.md`, `scripts/dev/codex_status_parse.py` (new), `scripts/dev/test_codex_status_parse.py` (new) | n | 12 | agent, Sonnet | ROUTINE, none |
| 3 | `mid-turn-image-intake-gap` | `scripts/dev/shot.py`, `scripts/dev/test_shot.py`, `methodology/screenshot_intake.md` | n | 12 | agent, Sonnet | untagged (S, coordinator spot-check) |
| 4 | `bt-engine-wire-real-funding-rsi-cc-rerun` | `backtest/layers/rsi/run_rsi_backtest.py`, `backtest/layers/cryptocred/run_cc_setups.py`, `backtest/bt/bt_data.py`, `research/dsa_backtest_audit_2026-10-16/RERUN_FUNDING.md` | n | 20 | session, Sonnet | IMPORTANT, coordinator reads Result + file list |
| 5 | `dsa-audit-04-clean-room-twin` | `research/dsa_backtest_audit_2026-10-16/T04_clean_room_twin.md`, `.../scripts/T04/` (new files) | n | 36 | session, Sonnet | IMPORTANT, coordinator reads Result + file list |
| 6 | `dsa-audit-10-missing-aspects` | `.../T10_missing_aspects.md`, `.../scripts/T10/` (matrix.csv, playbook, new files) | n | 38 | session, Sonnet | CRUCIAL: review Agent (Sonnet) on the diff before `sync.py ship` |

(Paths in cols 3 are relative to `MyTradingSys/` except `scripts/dev/`, which is repo-root.)

## Card edits made for this freeze (all shipped with this commit)
- `t02-f1-review-allowlist-chunk-4`: `depends_on` chunk-3 cleared (chunk-3 card no longer exists; `f1_rows.py c1..c3 --count` = 0 each; c4 = 30). Pointers refreshed.
- `find-gemini-antigravity-quota-command-an`: scope trimmed to the 3 files it writes; no `usage_log.py` wiring (that file is not in the repo).
- `mid-turn-image-intake-gap`: desktop claim (24 h stale) released with `sync.py release`; pointers refreshed.
- `dsa-audit-04-clean-room-twin`, `dsa-audit-10-missing-aspects`: reviewer Agent (Sonnet, saw card + evidence only) FIX applied, stamp `REVIEWED:2026-10-24 ACCEPT`. T04: test-line wording and ledger column note; T10: output paths and S1/S2 carding step added, matrix columns capped.
- `bt-engine-wire-real-funding-rsi-cc-rerun`: no change (passes).

## Retired during the freeze (dropped with a note, not deleted)
- `bug-guard-blocks-interactive-roles`: model_guard.py was removed by the hook trim (43d3bfc8f); the bug no longer exists.
- `cbp-one-acked-row-through-queue-consumer`: already done in 6fd789b81; cbp_adapter.py deleted in f9fcf77b4.
- `snapshot-vwap-anchor-label` (reviewer found it stale): fixed already, `MarketDataSnapshot.java:862` writes the UTC day start and `liveSession_vwapAnchorIsUtcDayStartAndNeverInTheFuture` exists. Also removes the live-path slot candidate; the pilot has 0 live-path cards.
- `aibridge-version-not-bumped`: manifest.json and loop.js already read 0.7.1 (3270e7423).

## Excluded, one line each
- `research-top-level-declutter`: Doctor exclusion (183-file move, touches the whole research/ tree and every other card's paths).
- `context-composite-v2-dev-read`: Doctor exclusion (30 turns of DEV reads, folder shared with confluence work).
- `hook-reminder-get-usage-before-after-age`: needs `usage_reminder.py`/`usage_log.py` (absent) and edits `.claude/settings.json`, the file the trimmed-hooks pilot is testing; hooks load from the main checkout.
- `analyst-ingest-roman-x`: done_when needs real public X calls with source URLs (live network scrape), not verifiable on a fixed budget; stale scope.
- `rv05-h2-position-line-evidence`: needs a non-Claude blind read via a DSA-NUC desk row and video frames (A-7); not NB alone.
- `cbp-add-channel-latest-n-to-fetch-captio`: overlaps the open `cbp-ultra` claim (fetch_captions_timed.py).
- `dsa-audit-05/06/07/09`: stamps voided and unreviewed; 06 overlaps the funding rerun (card 4), 05/07 are heavy NB-CPU reruns on the live host, 09 reads the live tree. 08 is a CODEX-lane card.
- `confluence-s0-registry`, `confluence-s1-context-counts`, `context-conditioned-session-flow-states`: depend on an unstamped Lab_Guy card, or hold a live claim.
- `gap-g7-stop-slippage`: shares `bt_data.py` with card 4, 30 turns of aggTrades download.
- `krown-data-cme-btc-volume`, `live-loop-timeouts-b191`: public-web hunt / needs the live runner log mirror (not NB-alone), no real review stamp.
- JIS-NB desk cards (`cpu-audit-jis-nb`, `docker-vs-windows-test-speed`, `host-legacy-tasks-unregister`, `java-popups`, `state-code-accumulator-backfill`, `move-live-host-generated-files-status-md`, `malkan-w1hr-local-whisper-asr`): operate on the live host or its scheduler; builders never touch those.
- Any card needing NUC data (`argon-blind-read-7-frames`, `lc-validation`, `tom-btc-validation`, `rv-dsa-ledger-mechanical`): excluded by rule.

## Risks the coordinator should know
- Cards 5 and 6 are the long ones (36-38 turns, reviewer estimates 2-4 h); cap them at 3 h and let the optional parts (T04 third twin) go.
- Card 6 shows T04-T07, T09 reports are missing; its playbook lists them as missing, it does not wait.
- Cards 5 and 6 write into the same folder (`dsa_backtest_audit_2026-10-16/`) but only to their own T04/T10 files; a worker must not touch the folder's index or brief.
