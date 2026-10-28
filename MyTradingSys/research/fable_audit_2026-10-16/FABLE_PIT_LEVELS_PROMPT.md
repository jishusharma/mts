# Fable 5.1 prompt: point-in-time levels, phases and cost (paste everything below the line into the compacted Fable session)

Why this prompt: FABLE_RUNS_AUDIT.md (same folder) found that the three Fable runs never asked the edge-deciding questions.
The operator added a fourth (2026-10-16): when a trader's rule is backtested, every support/resistance level, phase
(balance / trend / P-B-D) and session must be built only from data that existed at the decision bar.

What exists already (claims to check, not evidence):
- `pivot_pattern_audit_2026-10-14/REPORT.md:36-41` defines available_at (a pivot that needs 2 later bars is usable at the
  close of j+2) and asks for an as-of level ledger (:65). It is NOT built: `available_at` appears in no backtest module.
- `cc_structure.py:98` uses a swing only when `confirmed_i < k` (correct).
- `tom_bt.py:255` regime tags use data <= t.
- `mts_flow_audit_2026-10-13/REPORT.md:109` says volume-profile look-ahead is "mostly fixed".
- `CATALOGUE_AUDIT.md:127` says balance, P/B/D, "thin", "big" and the BTC session have no definition at all.

---

MTS Fable session (Fable 5.1, effort high). Boot per CLAUDE.md steps 1-2 only (sync.py start, STATUS.md). OPERATOR OVERRIDE
for this session only: the tool-turn cap is 40; do not hand over mid-way; write the deliverable section by section as you go.

**Your three earlier runs, and what an independent audit found they missed.** Read `MyTradingSys/research/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md` in full.
Open each deliverable only where this task uses it.
| Run | Prompt | Deliverable | Gap to close in THIS session |
|---|---|---|---|
| R1 pilot | `layer_rebuild_2026-10-15/FABLE_PILOT_PROMPT.md` | `gross_effect_screen_2026-10-15/PRE_REG.md`, `RESULT.md`, `decay.csv` | You froze the PRE_REG with no count-only power check (n_T = 40, MDE 0.365 % vs 0.14 % cost). The headline hid a powered control FAIL (n = 1,439, t_cost -6.0) and a decay sign flip (+0.02 % at 5 m, -0.10 % at 240 m). Your step 5 must count first, give one verdict per arm, and limit the kill scope to the tested family |
| R2 adversarial | (six questions, restated in the review) | `fable_audit_2026-10-16/PROMOTION_REVIEW.md` | You checked that the gate fails closed, not whether it can tell an edge from luck: 95 % CI with no variant adjustment, MIN_TRADES 30. The testnet records no decision price, so it cannot measure slippage. Your PRE_REG must state its multiple-testing treatment (Holm over the trial-ledger variant count) and must not use testnet fills as cost evidence |
| R3 A3 catalogue | `layer_rebuild_2026-10-15/FABLE_PROMPT_PACK.md` section A3 | `fable_audit_2026-10-16/CATALOGUE_AUDIT.md` | You checked fidelity, not cost: Tom's stated stops cost 1.1-3.2 R at Binance taker fees. Completeness was sampled (3 of 3 V1-only videos held misses) but not extrapolated. Steps 3-4 below finish that work; reuse your 4.3 markability table and your P3 definition list rather than starting over |
Disagree with the audit where the code or data says otherwise, and say so with file:line.

**Usage guard.** Call `get_usage` first and last and record both in `PIT_USAGE.md`. Stop, write up and ship if
weekly all-models rises 8 points or reaches 95 %.

**Rules.** No VALIDATION or HOLDOUT bars (DEV = bar open 2022-01-01..2024-06-30). No production or live-path code edits. Tests
and scripts go in the output folder only. Every number is SOURCED (file:line or quote) or OURS. Expected values come from
`backtest/layers/FORMULAS.md` or your own arithmetic, never from the code under test.

**The question.** For each level/phase family the setup catalogue and the layers use, is the value the backtest sees at
decision bar t exactly the value a trader could have drawn at t? And among the setups whose levels pass, which can clear
BTC costs at their natural stop?

**Step 1: inventory (READ).** List every builder of a level, zone, phase or session in `backtest/` and
`backtest/layers/`. Include at least:
- prior-period high/low (engine 4h/day/week aggregation);
- fractal / swing pivots (`cc_structure.py`, `vp_pivot_probe.py` 18.2, CYCLE_DESIGN);
- volume profile POC/VAH/VAL, both anchored and "last major high to last major low" (FORMULAS 18);
- VWAP and its anchor;
- session anchors (00:00 UTC and others);
- regime / phase tags (`tom_bt.py` trend_tag and tercile_cuts, any balance or P/B/D code);
- percentile thresholds (gross-screen L4, orderflow_bars thr_days);
- ATR.

For each, write one row: formed_at, available_at, where in the code it is consumed, and whether any input after
available_at reaches a decision at t.

**Step 2: leakage proof (RE-DERIVED).** For the 6 highest-risk families, write one test in the output folder. Each test
builds the series on bars[0..t] and again on bars[0..t+N], then asserts the value used at t is identical.

Prove each test works: it must FAIL on a planted look-ahead (a version that peeks one bar ahead) and PASS on the repo code.
Watch for these traps:
- pivot used before its right window closes;
- a profile that includes the decision bar or later bars;
- full-sample percentiles or terciles;
- day/week buckets aligned to bar open vs close;
- the CVD level depending on the series start;
- a level that "moves" when a later pivot replaces it (repainting);
- labels at bar open.

Record PASS/FAIL per family with file:line.

**Step 3: the as-of contract (spec, OURS where needed).** Write `PIT_CONTRACT.md`, max 6 KB. It covers:
- the level ledger schema from pivot_pattern_audit :41 (origin, source TF, price/zone, formed_at, available_at, touch history,
  age, role flip, invalidation, algo version);
- OURS definitions, written once and never varied in G3, of balance (N closes inside a range), P/B/D by closing prices, thin
  top, big trade (Fabio's 30 NQ contracts as the SOURCED anchor, BTC equivalent OURS), BTC session anchor, "healthy trend";
- for each one: how it is computed from bars <= t, and what a trader would see on the chart at t.

Each definition names the catalogue rows (TOM-x / FAB-x / KR / MAL) that need it.

**Step 4: cost-in-R per row (RE-DERIVED).** For every catalogue row with a stated or derivable stop, give:
- stop as % of price;
- timeframe;
- cost in R at 0.14 % (all-taker) and 0.09 % (maker in);
- the trader's own SOURCED hit rate and R:R where one exists (hQ8sOq67x5o metrics, CATALOGUE_AUDIT.md:64);
- break-even stop % = cost / gross expectancy.

Mark each row FEASIBLE (stop >= 0.40 % taker, or maker entry in the setup) or NOT AS WRITTEN.

**Step 5: one experiment a Sonnet card can run mechanically.** Pick the single row that passes steps 2 and 4 and has the most
DEV events, from a count-only pass you run yourself (counts only, no outcome column). Write `PRE_REG.md` per the existing
template (`gross_effect_screen_2026-10-15/PRE_REG.md`) with these additions:
- n and MDE printed from your count, and the file refuses to freeze if MDE + cost exceeds a plausible gross effect (state the
  plausible effect and its source);
- one verdict per arm (T and a location-only control);
- levels and phase taken only from the PIT_CONTRACT builders;
- kill scope limited to that rule family.

Then write one card (`tasks.py new`, lane SONNET) that runs it.

**Deliverable** `MyTradingSys/research/pit_levels_2026-10-16/`, containing:
- `REPORT.md`: verdict paragraph, inventory table, leakage PASS/FAIL table, cost-in-R table, the chosen experiment and why,
  at most 5 operator decisions each with a default;
- `PIT_CONTRACT.md`, `PRE_REG.md`, the tests, `PIT_USAGE.md`.

Run `python scripts/dev/run_all_tests.py --quick` if you touched anything the gate covers. Then `sync.py ship` with
`Result: <n families PASS/FAIL leakage>, <n rows FEASIBLE>, card <slug>, usage +X pts`, then `sync.py release`.

Reply in 6 lines: leakage verdict, feasible rows, chosen experiment, card slug, usage delta, next step.
