# Blind Spec Review: Layer Bible + layer_state.py runtime (C2)

- **Target Spec**: `MyTradingSys/research/layer_bible/DESIGN.md` (commit 1712eb6b75aa)
- **Reviewer**: Gemini 3.8 Flash (independent non-Claude review lens per Lab_Guy v3.1 / C2 policy)
- **Date**: 2026-11-04
- **Scope & Context**: `MyTradingSys/research/layer_bible/DESIGN.md`, `MyTradingSys/backtest/layers/FORMULAS.md` s20, `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`
- **Focus**: Defects only, classified under E1-E7 per `MyTradingSys/system/roles/lab_guy.md:20-27`, with severity and concrete fixes.

---

## 1. Executive Summary & Core Mandate Questions

1. **Can the runtime stop memory answers?**
   - **Partially, but not as specified.** Section 3 states that any answer must quote `layer_state.py` output with its stamp. However, `DESIGN.md:12-16` only specifies an interactive CLI (`scripts/dev/layer_state.py <family>`). It provides no programmatic assertion, schema verification, caching hook, or automated linter in prompt/session guards or `tasks.py check` to mechanically reject memory answers. Furthermore, Section 3 acknowledges it will be written into CLAUDE.md only *after* the pilot passes, meaning during the entire pilot phase, answers will remain vulnerable to memory hallucination.

2. **Is the Bible enforceable?**
   - **No, format enforcement is missing concrete schema and machine tooling.** Section 1 specifies `system/layer_bible/<family>.md` with fixed sections and states "Format is lint-checked at 0 tokens". However, no parser, schema, or AST specification is defined for how Python runtime scripts will reliably extract the "machine-readable block" from markdown text without breaking on formatting nuances.

3. **Can the tests fail?**
   - **The proposed 11-04 test case has undefined and underspecified failure conditions.** Section 4 specifies testing the 11-04 case ("3m swing 03:12-11:39 = completed cycle; 12:21 at -49 is NOT a valid bottom dot"). However, Section 5 explicitly admits: *"The exact 'valid cycle dot' rule (+-53 only, or cross required, how a cycle completes): not yet sourced in one place"*. If the completion and dot rules are unsettled and marked OURS, a test cannot fail against an objective standard—it risks being tailored to pass whichever heuristic is arbitrarily coded into the pilot runtime.

---

## 2. Defects Tagged by Error Class (E1–E7)

### Defect 1: [E2 Definition / E1 Data] Unspecified data window and lookback requirement for recursive EMA warmup
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:13-16`
- **Severity**: HIGH
- **Evidence**:
  - `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:18` defines `WARMUP = 200` bars.
  - `MyTradingSys/backtest/layers/FORMULAS.md:20.2` states: `output used only after WARMUP=200 bars from series start, from any gap or from any NaN ci`.
  - `DESIGN.md:14` specifies fetching public klines from `data-api.binance.vision` with `--at <utc>` to replay a past time, but does NOT specify the lookback depth (number of bars) to fetch.
  - On higher timeframes (e.g. 4h or 1D in the "1m to 4h stack" cited in `DESIGN.md:15`), fetching 200 closed bars requires 800 hours (~33.3 days) of historical klines. On Binance REST API, default limit is 500 or 1000 bars. If the runtime only fetches default bar chunks or does not strictly enforce `n >= WARMUP + lookback`, `wavetrend.py` will emit `NAN` (or worse, un-warmed values if altered), triggering `NOT_IN_DATA`.
- **Concrete Fix**:
  - Update `DESIGN.md` Section 2 to specify exact bar fetch depth per timeframe: `fetch_depth = WARMUP + required_cycle_window` (at least 300 bars per TF). For `--at <utc>`, explicitly require querying the interval `[utc - (WARMUP + N)*tf_ms, utc]`.

---

### Defect 2: [E2 Definition] Undefined "valid cycle dot" and cycle completion rules in the Bible definition
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:15,26`
- **Severity**: HIGH
- **Evidence**:
  - `DESIGN.md:15` states the runtime prints `last valid cycle dot (time, wt1), cycle completed or open`.
  - `DESIGN.md:26` admits: *"The exact 'valid cycle dot' rule (+-53 only, or cross required, how a cycle completes): not yet sourced in one place; the pilot extracts it from the operator's wt30_sequence/OPERATOR_DIRECTION words and marks OURS where he did not say it."*
  - In `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:46-59`, the indicator emits raw `cross_events` and `zone(wt1)` (`ob1 >= 53`, `os1 <= -53`). It has NO internal concept of a "cycle dot", "cycle swing", or "cycle completed".
  - If the Bible is meant to be the single source of truth containing only canonical formulas and operator rules, deferring the definition of the primary state machine entity ("cycle") to ad-hoc extraction during implementation violates the core premise of the C2 design.
- **Concrete Fix**:
  - Formalize the exact cycle state-machine definition in `DESIGN.md` before building Phase 2:
    1. A valid cycle dot requires: `zone in ('ob1', 'ob2')` for top dot, `zone in ('os1', 'os2')` for bottom dot, AND a confirmed cross event (`event != 0`).
    2. A cycle completes when an opposite valid dot occurs, or when the oscillator crosses the zero/mid line. State explicitly whether intermediate crosses within mid reset or abort the cycle.

---

### Defect 3: [E3 Implementation / E4 Wrong Question] Unspecified machine-readable serialization format for "Parameters" block
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:8,13`
- **Severity**: MEDIUM
- **Evidence**:
  - `DESIGN.md:8` states: *"Parameters (machine-readable block the runtime reads)"*.
  - `DESIGN.md:13` states: *"Reads ONLY the Bible's Parameters block and the family's tested module... invents no definition."*
  - The spec does NOT define the syntax or schema of this machine-readable block: is it a fenced ` ```json ` block, ` ```yaml `, or key-value pairs?
  - Markdown parsers without a strict block contract risk parsing failures or ambiguous type conversions (e.g. floats, ints, lists).
- **Concrete Fix**:
  - Mandate in `DESIGN.md:8` that the **Parameters** section must contain exactly one fenced ```` ```json:parameters ```` block conforming to a strict JSON Schema validated by `jsonschema` or `json.loads()` at runtime.

---

### Defect 4: [E1 Data / E3 Implementation] Kline boundary semantics, venue discrepancies, and partial bar leak
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:14,27`
- **Severity**: MEDIUM
- **Evidence**:
  - `DESIGN.md:14` states: *"Fetches public klines (data-api.binance.vision, public market data, pre-approved); closed bars only; `--at` replays a past time"*.
  - Binance kline REST API returns `[open_time, open, high, low, close, volume, close_time, ...]`. The current (latest) bar returned by Binance is often unclosed (live).
  - Filtering by `close_time <= at_time` vs `open_time + tf_ms <= at_time` must align strictly with `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:62-70` (`htf_index`: `o + htf_ms <= t`) and `available_at` (`bar_open + timeframe`).
  - Furthermore, `DESIGN.md:27` defaults to Binance klines for WaveTrend, while live execution operates on Deribit or other feeds. Basis drift between Binance and Deribit has caused historical discrepancies (`EXEC_PROVENANCE_AUDIT.md:14`).
- **Concrete Fix**:
  - Specify the precise closed-bar filter: discard any bar where `bar[6] > at_ms` or `bar[0] + tf_ms > at_ms`.
  - Document Binance spot/perp symbol mapping explicitly (e.g. `BTCUSDT` spot vs `BTCUSDT` perp on Binance Vision).

---

### Defect 5: [E4 Wrong Question] Lack of automated enforcement mechanism in "Answer contract"
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:19-21`
- **Severity**: MEDIUM
- **Evidence**:
  - `DESIGN.md:20` states: *"Any answer about a layer's current state or definition quotes the `layer_state.py` output (with its stamp) and the Bible line; no stamp = 'not computed'. Written into CLAUDE.md-side docs only after the pilot passes"*.
  - This relies purely on voluntary LLM compliance. Past incidents (e.g. the 11-04 failure cited in line 3) occurred precisely because agents answered from context memory without running verification tools.
  - Without a mechanical check (such as a commit hook, linter, or pre-response validation rule), a purely descriptive contract will not prevent future memory answers.
- **Concrete Fix**:
  - In Section 3, specify the mechanical gate: add an enforcement script or rule in `.agents/hooks.json` or `scripts/dev/tasks.py check` that flags any research or review card asserting indicator state without citing an executable stdout hash/stamp from `layer_state.py`.

---

### Defect 6: [E3 Implementation / E7 Broken Gate] Ambiguous test falsifiability and golden verification
- **Location**: `MyTradingSys/research/layer_bible/DESIGN.md:23`
- **Severity**: MEDIUM
- **Evidence**:
  - Section 4 step 2 specifies: *"expected numbers from FORMULAS s20 computed independently; tests red on a stub first, incl. the 11-04 case... Haiku blind re-derivation of 1-3 numbers"*.
  - However, for the 11-04 case (`3m swing 03:12-11:39 = completed cycle; 12:21 at -49 is NOT a valid bottom dot`), the exact timestamp, price series, and kline fixture are not pinned by hash or path in `DESIGN.md`.
  - Without a pinned fixture CSV or JSON containing the exact kline series for 2026-11-04, test runs cannot be guaranteed to fail predictably on old/stub code or pass deterministically across machines.
- **Concrete Fix**:
  - Require a pinned fixture file: `MyTradingSys/research/layer_bible/fixtures/wavetrend_btc_20261104_3m.csv` with SHA-256 hash referenced in the test plan before writing Phase 2 code.

---

## 3. Review Summary & Recommendation

The design addresses a genuine vulnerability in the MTS workflow: agent hallucinations and fragmented layer definitions. The core architectural decision—unifying layer definitions into a single authoritative Bible and driving state reporting through a deterministic CLI runtime reading that Bible—is conceptually sound.

However, the design contains significant specification gaps:
1. It defers the formal definition of "cycle dot" and "completed cycle" to an ad-hoc implementation step despite making them primary outputs of the runtime (`DESIGN.md:15,26`).
2. It omits warmup depth requirements for recursive indicators (`wavetrend.py:18` requires 200 bars).
3. It relies on prose guidelines rather than mechanical gates to enforce the answer contract.
4. It lacks a pinned data fixture for the critical 11-04 test case.

Therefore, the specification should incorporate these concrete fixes prior to proceeding with Phase 2 implementation.

VERDICT: FIX-FIRST
