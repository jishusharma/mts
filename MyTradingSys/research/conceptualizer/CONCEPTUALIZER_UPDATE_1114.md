# CONCEPTUALIZER_UPDATE_1114

Commit: 1d0c657ba on branch JIS-NB/conceptualizer-wire-1114 (ship status: see end of file; verify `git cherry origin/fast-track JIS-NB/conceptualizer-wire-1114` is empty).

## Done
- Wiring is machine-enforced. `scripts/dev/make_conceptualizer.py` fails the build when a layer_index family has no Conceptualizer layer, a layer claims an unknown family, or a tests row has no 7th source cell or a path that does not exist. 5 new tests (14 total pass); the 5 new ones fail 5/5 on the old generator.
- layer_index.json: +4 families (nk_stocktalk, cycle_context, edge_harness, adx_trend). LAYERS.md regenerated, pointers ok.
- concepts.json: 16 layers (before: 11 mapped; after: 16 with tom-fabio, malkan, cryptocred, krown, positioning, session-timing, volume-ma, callers, wavetrend, pitchfork, pizzino, nk-stocktalk, adx-trend, cycle-context, edge-harness, live-engine). `updated` 2026-11-14. Every test row has a source path in the repo (`research/conceptualizer/sources_1114/` holds copies of notes-only results).
- Rows now per layer (tests / concepts): tom-fabio 31/8, malkan 35/7, cryptocred 7/7, krown 8/8, positioning 29/11, session-timing 15/6, volume-ma 14/9, callers 10/8, wavetrend 13/6, pitchfork 10/6, pizzino 6/5, nk-stocktalk 36/13, adx-trend 13/6, cycle-context 53/5, edge-harness 50+4/4, live-engine 5/4.
- Added from the check agents: T4 FAIL, T6 FAIL, T5 UNTESTED, Maker M2/M4/M6 FAIL, NKN-01..03 UNDERPOWERED. Corrections: NK T2 washout PASS to FAIL (blind review, VAL -0.2156R n 1487), krown fire-rate PASS to DESCR., oi_flush to failed, NK CAPITULATION and HM-RANGE moved from promising to inconclusive.
- Leaks scrubbed from sources_1114 (local paths, private artifact URL, browser-profile lines).

## Haiku / Sonnet check findings
4 agents (2 Haiku, 2 Sonnet). Found: missing results, wrong verdicts, OURS/SOURCED mis-tags, a forecast-like line, numbers not in cited files, leaks. Fixed above where listed.

## NOT done (budget freeze, no new agents)
- Europe-high-fade FAIL (BTC VAL n 1327, -0.291R) and Live Aid flags (0 of 30 cells pass, 66,559 events) rows: reports not located in time.
- B1/B2 level-auction rows (n 524 -0.136%, n 480 -0.113%); Wave-3 T7..T12 as UNTESTED; large-trade evidence rows.
- Verdict consistency across layers for the same study (nk5, nkp3, edge4 divergence/NY value, edge7/8, weekly streak bounce); INCONCL. to FAIL where source says FAIL; moot-point status calls (whale, sma200w, dilution, c30; pivot-r2-r3 to untested).
- Tags: malkan dilution split, candle/stars, tom-fabio fees.py as OURS, cryptocred stop as NOT_SEEN, adx-trend secondary-page params; "bottom due 2026-10-04..11-16" cycle-clock wording and the Habib 11-10 call (promising to untested) still to reword.
- Number-miss repoints: tom-fabio #6, volume-ma #0 and #5, malkan #3, positioning #4, wavetrend #0, pitchfork #0; volume-ma KPI should read 14 studies.
- NKN-04..06 still RUNNING.
Exact next step: one Sonnet session applies the list above to concepts.json, rebuilds, ships.

## Files for the independent Opus reviewer
- scripts/dev/make_conceptualizer.py (wiring_problems, family_ids, load)
- scripts/dev/test_make_conceptualizer.py (5 new tests)
- scripts/dev/conceptualizer.tpl.html (Source column)
- MyTradingSys/system/layer_index.json
- MyTradingSys/research/conceptualizer/concepts.json (spot-check edge-harness, nk-stocktalk, krown, positioning)
- MyTradingSys/research/conceptualizer/sources_1114/ (secrets/leaks scan)
- NOTES: CONCEPTUALIZER_GAPS_1114.md

## Ship result
- 1d0c657ba is on origin/fast-track and origin/green/fast-track; `git cherry origin/fast-track JIS-NB/conceptualizer-wire-1114` empty at 2026-11-14.
- Page republished over the existing url (version 14); registry row updated locally (published_sha b7b33439cdd0). The registry-only commit may still be unshipped: re-run `sync.py ship` from worktree mts-jis-nb-conceptualizer-wire2-1114 if `git cherry` shows one line.
- First ship attempt failed the offline quick gate (cause not captured); the second shipped.

## Opus review fixes (1114)
- malkan Deep RSI grid row INCONCL. -> FAIL (source grades the grid FAIL).
- live-engine consensus "not wired" removed: live_runner_cli.py calls consensus.hook.consensus_after_poll every poll (observation only); gap is now "rows not yet scored".
- New test test_review_fixes_1114_data_matches_sources fails on the old data.
- Registry record commit 11006989b; this file is also copied into the repo.
