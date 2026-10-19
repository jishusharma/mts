# Kurisko module independent GPT review

**FIX-FIRST: provenance labels and sensitivity tuple; numerical implementation checks MATCH.** No source or product-test file was edited. This is not a profitability study or a promotion decision.

Producer established: commit `dd001f2a7902f2de5c1b3821db7ea35bcb613624` explicitly credits Claude Sonnet 5.5 and records the original module/tests. Reviewer: GPT in this session, a different vendor. The original non-Claude specification review was Gemini 4 Argon (`research/lab_guy/spec_review_kurisko_2026-10-18.md:3,11-14`); it required the plotted D line, not raw K. Only committed trunk files were inspected. No backtest, market data, protected returns, or producer worktree was used.

## Scope and findings

All layer paths below begin `MyTradingSys/backtest/layers/kurisko/`; spec is `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; extract is `extracts/processed/kurisko/QUAD_ROTATION.md`.

| Check | Result | Severity | Evidence / conclusion |
|---|---|---|---|
| D calculation and optional slowing | MATCH | — | `stoch_core.py:23-42` computes raw K over inclusive trailing extrema; optional slowing SMA then D SMA. Defaults use D smoothing as required by FORMULAS.md:563 and the prior review. The spoken source R8 establishes D as plotted line; exact smoothing conventions are our definition. |
| Raw K, flat range and NaN smoothing | MATCH | — | `stoch_core.py:13-34`: HH=LL gives NaN; a NaN in the SMA window prevents a value; warmup indices agree with the independent fixture. |
| Episode and strict boundaries | MATCH | — | `quad_rotation.py:71-99` arms when all lines are strictly <20 (or >80 for the OURS short mirror), fires on the first fast uptick/downtick after arming, and prevents later events within the same episode. Current event bar may leave the zone, as explicitly allowed by FORMULAS.md:569. Equal fast values are not turns. Tests :108-151 cover resets, exact 20/80, mirror and NaN fast-line cases. |
| NaN input and missing-bar restart | MATCH | — | `quad_rotation.py:33-68` splits before every NaN OHLC bar and non-unit time jump, recomputes indicator windows within segments, and leaves undefined lines NaN. Independent synthetic default-band probes confirm both restart cases. |
| Closed-bar availability and episode timestamp | MATCH | — | `quad_rotation.py:102-112` reports t_close and available_at=open+tf, and episode_start_t=close time of first oversold bar. Tests :153-173,192-210 verify fixtures, availability and future-spike invariance. |
| SOURCED vs OURS band defaults | MISMATCH | MEDIUM | `params/kurisko_default.json:5` labels the entire bands tuple SOURCED while acknowledging d=4 appears only on an unmatched rehosted slide, not the spoken source. Spec section 5 rows 1-2 explicitly leaves smoothing/roles OPEN and places these numeric smoothing choices under OURS defaults; FORMULAS.md:563 labels the formula OURS. Separate sourced lookbacks from adopted smoothing/role defaults, or mark the combined tuple OURS with its source components documented. Do not alter numerical defaults while correcting attribution. |
| Sensitivity tuple | MISMATCH | LOW | Same params line documents (44,3), while spec section 5 row 1 documents (44,4). No alternative is run by this module. Resolve the documented alternative before a downstream trial rather than silently adding a variant. |
| Plotted D / event / RSI labels | MATCH with note | — | Params :6 names D from R8; :9 turn rule and :10 numeric short mirror are OURS; :11 RSI is OPERATOR-HYPOTHESIS. R2 supports all four under 20; R3 leaves the numeric turn open; R10 does not state all-four-above-80. None of the RSI/short hypotheses is represented as a sourced Kurisko claim. The D name is sourced; its SMA equation remains the adopted formula, not a verbatim sourced smoothing rule. |
| Default OFF / isolation | MATCH | — | Params :4 enabled=false; module emits observation rows and contains no routing/execution call. No live wiring was added or exercised by this audit. |
| Golden fixture and generator independence | MATCH | — | `make_golden.py:10-38` derives the 20-bar fixture directly from arithmetic and imports no producer indicator. Tests :49-103 compare golden output, flat/NaN/slowing fixtures and future-bar changes. The independent recount below uses rational arithmetic and does not execute the generator. |
| Event fixtures / prefix causality | MATCH | — | FORMULAS.md:571 supplies small-k hand fixtures; tests :24-38,153-185 reproduce them and the short mirror. Existing future-spike tests are independent of the production formula, and the audit's six default-band prefix checks also match. |

The MEDIUM provenance finding is the reason for FIX-FIRST; no numerical mismatch or future-data leak was observed in the bounded checks. Labels asserting a trader's settings matter even when execution values remain identical.

## Independent recount and commands

```
python MyTradingSys/research/layer_lab/kurisko_module_review/rederive.py.txt
python -m pytest MyTradingSys/backtest/layers/kurisko/test_quad_rotation.py -q
git show -s --format=full dd001f2a7902
```

Independent script result:

```
golden_rows=20
finite_values_rederived=30
blank_warmup_values=10
prefix_checks=6
gap_nan_restarts=2
first_D_exact=2200/27
first_D_float=81.48148148148148
```

The script first extracts the 20 explicitly listed synthetic OHLC triples from FORMULAS 24.2, computes raw K5 and D3 with fractions, and compares every CSV cell at tolerance 1e-9. Expected values are complete before any observation-module import. It then checks synthetic prefixes and NaN/gap restarts through the module. No producer output is used as an expected number. These are SYNTHETIC formula/causality probes, not a DEV outcome trial.

Existing suite: **28 passed in 0.07s**. The fixture's first raw value is 200/3 at index 4; first D is 2200/27 at index 6. Bars 7 and 8 are individually flat but their five-bar windows have nonzero range, so raw K=100 is correct. The separate all-flat fixture checks HH=LL -> NaN.

## Follow-up and limits

`kurisko-params-provenance-labels`: correct combined SOURCED attribution and reconcile (44,3)/(44,4) documentation while preserving all deployed/default numerical values. No implementation rewrite, additional trial or strategy validation is implied.

This review covers the requested code, params, FORMULAS section 24, source spec, quote-gated extract, prior review, golden generator/CSV, and tests. It does not verify profitability, source-video pixels, actual trading fills or newly inferred parameters. No source edits were made, and no accepted trust tag or live promotion was issued. The executor supplies a separate upstream delivery receipt.
