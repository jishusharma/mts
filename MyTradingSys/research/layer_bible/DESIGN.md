# Layer Bible + runtime: design (d-layer-bible-runtime-1104, 2026-11-04, Lab_Guy; C2, review before build)

**Problem.** Layer knowledge sits in 7+ places per family (WaveTrend: FORMULAS s20, wavetrend_c30_retest, wt30_sequence, OPERATOR_DIRECTION, DISPOSITION, LIVE_NOTE, OPERATOR_POINTERS, decisions, Eagle Bible) and answers come from memory or scratch scripts. 11-04: a wrong "new cycle at 12:21" because nothing applied the +-53 rule.

**Then vs now.** Then (Aug-Sep): `runtime/compiled_engine.md` + `mts_math.py` + `current_market_state.md`, fed by the Java snapshot; deterministic, stale since early Oct (engine last changed 09-28; both py helpers gone). Now: `LAYERS.md` (generated from `layer_index.json`) holds status only; definitions live in FORMULAS.md and per-study folders; state comes from ad-hoc scripts. Not rebuilt: the old engine (Java-fed, tied to retired layers). Kept: the idea, one deterministic runtime, no AI in the loop.

## 1. The Bible (one file per family: `system/layer_bible/<family>.md`)
Fixed sections, nothing else: **Definition** (formula, each constant tagged SOURCED with file:line, or OURS) | **Parameters** (machine-readable block the runtime reads) | **Operator rules** (his words, date, decision id) | **Findings** (each: claim, n, p or CI, window, source link, trust tag; DEV/VALIDATION never mixed) | **Corrections** (what was wrong, who, date) | **Status** (family row of layer_index, open cards).
Rules: a fact lives in the Bible once; every other doc links to it and is secondary. Only Lab_Guy-checked (or operator-stated) content enters. Format is lint-checked at 0 tokens (sections present, every number has a source link, every Parameter has SOURCED/OURS).
Feedback loop: Eagle_Eyes observations and lessons go in as a **Candidate** line (date, claim, n) in the Bible; promoted to Findings only after a measured count over all past days (existing Eagle rule) and a source link; the operator's own statements go straight to Operator rules.

## 2. The runtime (`scripts/dev/layer_state.py <family> [--tf 1m,3m,...] [--at <utc>]`)
- Reads ONLY the Bible's Parameters block and the family's tested module (WaveTrend: `layers/wavetrend/wavetrend.py`, golden-checked at 1e-9); invents no definition.
- Fetches public klines (data-api.binance.vision, public market data, pre-approved); closed bars only; `--at` replays a past time (this is what makes it testable against 11-04).
- Prints state, one line per TF: zone, last valid cycle dot (time, wt1), cycle completed or open, plus the 1m to 4h stack, then `bible@<commit> data@<last bar utc> code@<sha>`.
- Deterministic: same Bible + same bars = same output. No network or AI choice changes the logic; a missing/short data window prints NOT_IN_DATA, never a guess.
- Not in scope: orders, live tree, HALT, runtime/secrets. Public data only.

## 3. Answer contract (the rule that fixes the failure)
Any answer about a layer's current state or definition quotes the `layer_state.py` output (with its stamp) and the Bible line; no stamp = "not computed". Written into CLAUDE.md-side docs only after the pilot passes (a one-line pointer, size cap 7168 B is nearly full).

## 4. Build and safety order
1. This design -> non-Claude review (Gemini) -> operator-facing summary. 2. WaveTrend pilot: Bible + runtime; expected numbers from FORMULAS s20 computed independently; tests red on a stub first, incl. the 11-04 case (3m swing 03:12-11:39 = completed cycle; 12:21 at -49 is NOT a valid bottom dot); Haiku blind re-derivation of 1-3 numbers; no new files in CI's red steps. 3. Archive plan: list superseded files, move to `research/_archive/<family>/` with a pointer line, delete nothing. 4. Roll out per LAYERS.md, one family per ship.

## Open questions (defaults taken)
- The exact "valid cycle dot" rule (+-53 only, or cross required, how a cycle completes): not yet sourced in one place; the pilot extracts it from the operator's wt30_sequence/OPERATOR_DIRECTION words and marks OURS where he did not say it. Default: ask him only to confirm the reading.
- Multi-venue data (Deribit vs Binance): Binance public klines by default, as the studies used.
