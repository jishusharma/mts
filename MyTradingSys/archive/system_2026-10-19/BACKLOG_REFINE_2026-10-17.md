# Backlog refine 2026-10-17 (backlog-refine-1017, JIS-NUC)

Scope: every card in ready/refined/blocked (73 at start) checked against origin/fast-track (c3ff8607 + faceef19), the G3 blindness audit rerun, PLAN_2026-10-17_NEXT_5H.md and the card files on disk. Cards and this note only; no product code, no live tree, no VALIDATION/HOLDOUT data.
Stock after: raw 58 | refined 7 | ready 38 | blocked 29 | done 144 | dropped 5; `tasks.py lint` OK (281 cards); builder_ready 12.

## Marked done (shipped)
- trendline-contract-spec: TRENDLINE_CONTRACT.md + FORMULAS s19 on fast-track; lint_contract.py re-run: rows=48 problems=0.
- Not done though signals say shipped: wavetrend-prereg-counts (NB claim, PRE_REG.md not on fast-track yet); stays a card, promoted to ready only so its gate is clean.

## Shipped WRONG (new fix card)
- g3-chart-rebuild (NEW, ready, p1, S, 12 turns): g3-pack-code-fixes and g3-remove-visible-chart-cues were closed done, but the 213 PNGs were never redrawn; the audit rerun says `Draw rebuild: YES` and README.md:3 gates marking on it. No card existed. Command: `g3_pack.py draw` (never `build`: it rewrites the key).
- Flag only, no card: tom-layer-v2-cost is done, but its own note says to start only after the four tom-ledger-* repair cards; those are held (DAX chain, q11). Treat its numbers as provisional.
- Checked and still holding: g3-remove-visible-chart-cues (14 tests pass per audit), nb-live-tree-deploy-cleanup (AutoDeploy clear), every done card's done_when file paths exist.

## Dropped
- None. No card was made moot by a newer finding: the DAX/Tom cards are an operator hold (q11), not obsolete, so they stay blocked. T01-T10 DSA audit reports do not exist yet (only AUDIT_BRIEF.md), so nothing could be marked from them.

## Stale fixed
- trendline-causal-module: scope_in path lacked the MyTradingSys/ prefix; dependency done -> ready.
- trendline-g3-marks-pack: steps now require the 2026-10-17 g3_pack blindness fixes (ids <unit>-NN, no clock labels, unconditional overlays); ready.
- krown-recall-check, krown-dev-event-study: unparked by the operator 2026-10-17 but left raw/blocked; both now refined (chain: v0-detectors -> recall-check -> dev-event-study).
- cryptocred-home-fit-audit (p1): depended on fabio-layer-v2-markets (p5, paused OPUS) = deadlock; dep removed (DEFAULT, revert if the audit needs Fabio part B); ready. malkan- and positioning-home-fit-audit (p4) keep that dep and stay refined.
- wavetrend-observation-module, wavetrend-prereg-counts: missing est_turns/worker added; ready. wavetrend-dev-atlas waits on both.

## Promoted to ready
g3-chart-rebuild (new), trendline-causal-module, trendline-g3-marks-pack, cryptocred-home-fit-audit, wavetrend-observation-module, wavetrend-prereg-counts.
Left refined (dep not done): trendline-count-only, wavetrend-dev-atlas, krown-recall-check, krown-dev-event-study, fabio-layer-v2-markets, malkan-/positioning-home-fit-audit.

## Next 10, fundamentals first
1. g3-chart-rebuild (NUC, S) - unblocks the operator's 213 marks.
2. dsa-audit-01..10 (DSA-NB, operator-run via bridge; start T07/T08, they gate Q87/Q88 and two SONNET cards). Operator must reload the Chrome extension first. T01 claim is 25h STALE.
3. trendline-causal-module (NUC, claimed) - contract card done.
4. context-factors-pit-audit (NUC, claimed).
5. trendline-g3-marks-pack (after g3-chart-rebuild, so it reuses the fixed builder).
6. wavetrend-prereg-counts (NB claim) then wavetrend-observation-module, then wavetrend-dev-atlas (chain, one at a time).
7. confluence-read-encode, prob-dist-layer-design-brief (gated on DSA T07/T08).
8. cryptocred-home-fit-audit.
9. krown-layer-v0-detectors -> krown-recall-check -> krown-dev-event-study; krown-catalogue-gpt-audit.
10. Last: the 9 gptb-* event-table CODEX cards (new layers/event tables), malkan/krown caption fetches.

## Defaults taken (no operator asked)
- Left blocked: all 12 DAX/Tom held cards, 2 parked RV-DSA, gap-g6-trial-ledger (each has an explicit hold reason).
- Priorities not renumbered; order above is the recommended pick order, `tasks.py next` still sorts by prio then age.
