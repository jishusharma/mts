# Claude handoff: reusable lab pilot (2026-10-16)

Operator request: extend reuse, use Sol 6.1/Astra on critical tasks, optimize tokens without a quality cap,
and use predefined ordered model lenses that keep work aligned to its goal. Finish autonomously.
Operator later instructed Codex to make no further computer-control calls; honor that instruction.

Implemented interface: `MyTradingSys/system/LAB_RECIPES.md`. Script: `scripts/dev/lab_flow.py`.
Recipes generate ordinary CODEX cards, preserving the existing claim/runner/ship mechanism. Sol maps or
builds; Astra independently challenges critical work. Mechanical run-review uses Luna then Sol.
Criterion receipts, report hashes and source hashes prevent a bare done flag or stale evidence from
unlocking the next lens. Packs use source indexes, not repeated boot/source dumps. Recipe cards bypass
old share/count caps, retain real allowance headroom and never silently reroute to a different model family.

Pilot spec: `research/layer_lab/examples/pilot-spec.json`, id `recipe-pilot` (already launched; do not launch twice).
Expected synthetic result: sum claim 31 is MISMATCH (30), mean 10 MATCH, net-after-fees NOT_IN_DATA.
This is a plumbing/acceptance pilot, not evidence that the recipes improve strategy research quality.

## Your one task (Sonnet; no subagents, no UI control, no operator input)

1. Run `sync.py start claude-recipe-pilot` in your own worktree and claim `claude-recipe-pilot`.
2. Read LAB_RECIPES.md, lab_flow.py, its tests, and `lab_flow.py status recipe-pilot`.
3. Run `python -m pytest scripts/dev/test_lab_flow.py scripts/dev/test_tasks.py scripts/dev/test_codex_run.py scripts/dev/test_codex_pack.py -q`.
4. Read both pilot reports and card receipts on origin/fast-track. Independently recompute 10+11+9 and one receipt hash.
   If a stage has not delivered, report PENDING with the exact blocker; do not rerun accepted stages or invent a review.
5. Check whether the stage criteria and source hashes actually prevent goal drift; reproduce any defect before proposing a fix.
6. Write `MyTradingSys/research/layer_lab/reports/2026-10-16_claude-recipe-pilot.md`: verdict, test totals,
   one checked claim/hash, design findings, measured usage if available, next high-ROI pilot recommendation.
7. Close desk request `Reusable lab recipes Claude pilot` with that report path; commit with Result, ship, release and verify.

Defaults: retain Astra low effort pending measured evidence; no holdout or market rerun; no live-path work.
If a material flaw is found, file one scoped follow-up card and keep the conclusion FIX-FIRST. Do not redesign
the relay or scheduled tasks. No operator answers are required. One report per pilot is enough.

The headless Sonnet attempt returned HTTP 429 `usage_limit_reached`, resetting 2026-10-16 at 14:30 IST,
with zero model tokens consumed. Codex did not obtain a Claude review. The desk row is a request, not an execution receipt.
Both real GPT stages have since delivered and shipped. Their measured results and independent receipt checks are in
`reports/2026-10-16_recipe-pilot-summary.md`; the next action is your spot-check, not relaunching either stage.
