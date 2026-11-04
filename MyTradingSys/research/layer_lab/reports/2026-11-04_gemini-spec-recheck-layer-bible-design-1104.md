# Gemini Spec Re-check Report: Layer Bible DESIGN.md v2

- **Card ID**: `gemini-spec-recheck-layer-bible-design-1104`
- **Date**: 2026-11-04 (UTC)
- **Reviewer**: Gemini 3.8 Flash (same review lens)
- **Target File**: `MyTradingSys/research/layer_bible/DESIGN.md` (commit `deff345f2714`)
- **Review Reference**: `MyTradingSys/research/layer_bible/REVIEW_GEMINI_1104.md`
- **Output Document**: `MyTradingSys/research/layer_bible/RECHECK_GEMINI_1104.md`

## Summary of Findings

All 6 items from `REVIEW_GEMINI_1104.md` were re-checked against `DESIGN.md:25-36`:

1. **Item 1 (Fetch depth vs 200-bar warmup)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:28`). Parameters carry `bars` (1000 per TF), `< warmup` prints `NOT_IN_DATA`.
2. **Item 2 (Cycle / dot rule definition)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:29`). Sourced operator rule 11-04 ~13:30Z, tagged OURS for turning dot prior-bar wt1 at/beyond +-53. Rejection of zero/mid-line completion rule justified as operator did not state it.
3. **Item 3 (Parameters block serialization format)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:30`). Exactly one fenced `json layer_state` block parsed by `json.loads`, fails closed on zero or multiple.
4. **Item 4 (Closed-bar filter & venue mapping)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:31`). Filter `open + tf <= at` specified, Binance spot klines selected and added to Parameters.
5. **Item 5 (Mechanical gate for answer contract)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:32`). DEFERRED with valid justification: follow-up card to add lint flagging layer-state claims without STAMP, avoiding adding new gates while CI is red.
6. **Item 6 (Pinned fixture for 11-04 test case)**: RESOLVED (SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:33`). Pinned file `fixture_btcusdt_3m_2026-11-04.csv` and SHA-256 hash `abb8d293499981aaf799f71566b66d82e70e14165225caf579cfa5e12e883350`.

No new E1–E7 defects detected in v2 text (`DESIGN.md:25-36`).

Verdict: `VERDICT: ACCEPT` recorded in `MyTradingSys/research/layer_bible/RECHECK_GEMINI_1104.md`.
Test verification passed:
`python -c "import pathlib; t=pathlib.Path('MyTradingSys/research/layer_bible/RECHECK_GEMINI_1104.md').read_text(); assert 'VERDICT:' in t"` (Exit code 0).
