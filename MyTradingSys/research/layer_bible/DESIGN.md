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

## v2 changes after the Gemini review (REVIEW_GEMINI_1104.md, FIX-FIRST; each item REAL, REJECTED or DEFERRED)
| # | finding | disposition |
|---|---|---|
| 1 | no fetch depth vs 200-bar warm-up (E2) | REAL: Parameters carry `bars` (1000 per TF, 800 above warm-up 200); fewer closed bars than warm-up prints NOT_IN_DATA; `--at` fetches the 1000 bars ending at `at` |
| 2 | cycle/dot rule deferred (E2) | REAL, now sourced: operator quote 11-04 ~13:30Z (Bible, Operator rules): a cycle starts at an up-cross from the lower zone and ends at the opposite cross. OURS: the turning dot needs prior-bar wt1 at or beyond +-53 (as the wt30 study); intermediate crosses inside a cycle do not end it; COMPLETED when a valid top dot prints, every valid top since the bottom is listed. Gemini's "or crosses zero/mid" REJECTED: the operator did not say it |
| 3 | Parameters block format unspecified (E3) | REAL: exactly one fenced ```json layer_state block read by `json.loads`; zero or several blocks fail closed (tested) |
| 4 | closed-bar filter, venue (E1) | REAL: keep only bars with open + tf <= at (tested); source = Binance spot klines via data-api.binance.vision; `symbol` and `source` are Parameters; the studies used the perp (labelled in the Bible), the live panel uses spot |
| 5 | contract has no mechanical gate (E4) | DEFERRED: card later for a lint flagging layer-state claims without a STAMP; no new CI gate while CI is red |
| 6 | 11-04 fixture not pinned (E1) | REAL: `fixture_btcusdt_3m_2026-11-04.csv` sha256 `abb8d293499981aaf799f71566b66d82e70e14165225caf579cfa5e12e883350` asserted by a test |

## Open question (default taken, operator can overrule)
Which valid top ends the cycle (11-04 3m: bottom 03:12 has valid tops 05:03, 05:54, 07:33, 11:39; he drew 11:39): the runtime reports all and the last; the operator confirms the reading.
