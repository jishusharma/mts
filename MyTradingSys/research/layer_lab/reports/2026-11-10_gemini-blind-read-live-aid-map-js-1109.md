MATCH: 10 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `map.js` & `level_registry.js` vs `REQUIREMENTS.md` (Map Section)

- **Card**: `gemini-blind-read-live-aid-map-js-1109`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target Files**:
  - `MyTradingSys/tools/live_aid/map.js`
  - `MyTradingSys/tools/live_aid/level_registry.js`
- **Specification Source**:
  - `MyTradingSys/tools/live_aid/REQUIREMENTS.md:61` (Map section: card `live-aid-bias-map-one-screen-1109`)
- **Scope In / Out**:
  - In: Blind read of `map.js` and `level_registry.js` against REQUIREMENTS.md Map section; level distances, ordering, empty-data and NaN handling; verification without reading test files.
  - Out: No edits to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; no trade or order.

---

## 1. Requirements Clauses Extracted from `REQUIREMENTS.md:61`

The Map section of `REQUIREMENTS.md` specifies the following requirements for the Live Aid Map tab (`live-aid-bias-map-one-screen-1109`):

1. **Clause 1 (View & Layout)**: "Now-table row Map and view `#playbook`; one screen, no scroll at 1920x1040 and 400x860, 60 words or fewer."
2. **Clause 2 (Top Bias Dial)**: "Top bias dial LONG / SHORT / HOLD (green / red / grey) from six section verdicts (analysts, price vs VWAP, RSI 1h, RSI 4h, pierce, playbook lean) with the count agreeing;"
3. **Clause 3 (Price Ladder Scope & Proximity)**: "price ladder, 3 nearest zones each side,"
4. **Clause 4 (Level Merging & Tolerance)**: "levels within 0.15 % merged into one zone"
5. **Clause 5 (Source Badges & Registry Providers)**: "with source badges (`level_registry.js`: playbook levels, analyst calls, Levels panel, MA strip);"
6. **Clause 6 (Session Strip & Current Highlight)**: "session strip Asia / Europe / US with the current one lit,"
7. **Clause 7 (Session Direction Arrows)**: "one arrow each"
8. **Clause 8 (Next Event Countdown)**: "and the next event as a countdown chip;"
9. **Clause 9 (Scenario Cards Count & Ledger Reference)**: "at most 3 scenario cards, each with its scenario-ledger id."
10. **Clause 10 (Fail Closed / Missing & NaN Handling)**: Descriptive only, fail closed; empty data reads `NOT_IN_DATA`, stale data reads `STALE`, non-finite/NaN prices and timestamps handled cleanly.

---

## 2. Requirement-by-Requirement Audit & Reconciliation Table

| Clause # | Requirement Summary | Specification Quote (`REQUIREMENTS.md:61`) | Code Reference & Implementation Verification | Label | Status | Repro / Audit Verification Notes |
|---:|---|---|---|---|---|---|
| 1 | One screen, <= 60 words | "one screen, no scroll at 1920x1040 and 400x860, 60 words or fewer." | `map.js:5,124-136` | SOURCED (`REQUIREMENTS.md:61`) | MATCH | Compact CSS grid layout without scrollbars; compact responsive media query (`@media(max-width:480px)`). Text output is strictly symbolic and data-driven (price numbers, ticker symbols, badges). Typical rendered word count is ~26 words, well below the 60-word limit. |
| 2 | Top Bias Dial (6 sections) | "Top bias dial LONG / SHORT / HOLD (green / red / grey) from six section verdicts (analysts, price vs VWAP, RSI 1h, RSI 4h, pierce, playbook lean) with the count agreeing;" | `map.js:10,19-26,77-82,115-118` | SOURCED (`REQUIREMENTS.md:61`, `map.js:10`) | MATCH | `SECTIONS` defines 6 sections. `bias()` tallies votes requiring >= 3 valid votes; assigns LONG (`cls: 'up'` green), SHORT (`cls: 'down'` red), or HOLD (`cls: 'dim'` grey) with agree counts. Playbook vote dynamically evaluated via `playbookVote()`. |
| 3 | Price Ladder (3 nearest each side) | "price ladder, 3 nearest zones each side," | `level_registry.js:8,73-81`; `map.js:88-96` | SOURCED (`REQUIREMENTS.md:61`, `level_registry.js:8`) | MATCH | `NEAR_N = 3`. `ladder()` partitions zones into `above` (sorted ascending by `lo`), `below` (sorted descending by `hi`), and `at`, slicing exactly `NEAR_N` (3) nearest zones each side. `ladderHtml()` displays `above` (reversed so highest price is at top), current price `▶ px`, and `below` descending. |
| 4 | Level Merging (0.15% tolerance) | "levels within 0.15 % merged into one zone" | `level_registry.js:7,54-70` | SOURCED (`REQUIREMENTS.md:61`, `level_registry.js:7`) | MATCH | `MERGE = 0.0015` (0.15%). `merge()` sorts candidate prices ascending and clusters levels satisfying `it.price / z.lo - 1 <= tol + 1e-9`. Non-chaining logic ensures one zone never spans wider than 0.15% from its base. |
| 5 | Source Badges & Providers | "with source badges (`level_registry.js`: playbook levels, analyst calls, Levels panel, MA strip);" | `level_registry.js:9-12,21-52,61-70,82`; `map.js:85-86` | SOURCED (`REQUIREMENTS.md:61`, `level_registry.js:9-12`) | MATCH | Pulls from all 4 providers: `fromPlaybook`, `fromPanel`, `fromMA`, `fromAnalysts`. Dedupes badges (`badges.push(it.badge)`) and formats badges in `<span>` tags. Multi-source clusters labeled "Cluster" and display composite badges. |
| 6 | Session Strip & Current Highlight | "session strip Asia / Europe / US with the current one lit," | `map.js:9,46-53,98-102` | SOURCED (`REQUIREMENTS.md:61`, `map.js:9`) | MATCH | `SESSIONS` defines Asia (0-8Z), Europe (7-13Z), US (13-21Z). `sessions()` marks `on: h >= s[1] && h < s[2]`. `strip()` assigns `.lms2.on` styling with amber highlight; draws a `lmnow` vertical marker at current UTC time. |
| 7 | Session Direction Arrows | "one arrow each" | `map.js:40-45,51,99` | SOURCED (`REQUIREMENTS.md:61`, `map.js:40-45`) | MATCH | Each session block computes `arrow()`: scenario likely UP (`↑`), DOWN (`↓`), or flat (`→`); completed sessions with today's close vs open use realized direction; else neutral dot (`·`). |
| 8 | Next Event Countdown Chip | "and the next event as a countdown chip;" | `map.js:60-70,101` | SOURCED (`REQUIREMENTS.md:61`, `map.js:60-70`) | MATCH | `nextEvent()` gathers upcoming session events where `t0 > now`, dedupes them via `REG.dedupe`, sorts ascending by timestamp `t0`, and returns earliest event. `countdown()` formats remaining time (`d`, `h`, `m`). Rendered as `.lmn` chip. |
| 9 | Scenario Cards (<= 3 cards + ledger id) | "at most 3 scenario cards, each with its scenario-ledger id." | `map.js:11,54-59,104-110` | SOURCED (`REQUIREMENTS.md:61`, `map.js:11`) | MATCH | `MAX_SCEN = 3`. `scenarios()` filters unique scenarios for the active/next session, capped at `MAX_SCEN`. `scenHtml()` renders cards with `data-ledger` and displays `s.id` (e.g., `PB 10 Asia 1`). |
| 10 | Fail Closed / Empty & NaN Handling | Fail closed: empty data reads `NOT_IN_DATA`, stale reads `STALE`, invalid px/timestamps handled safely. | `map.js:4-5,71-74,89,114,120,144,148`; `level_registry.js:14,23,29,36,47,56` | SOURCED (`REQUIREMENTS.md:61`, `map.js:4-5`) | MATCH | Missing/empty payload returns `<p class="pbmsg">NOT_IN_DATA</p>` or `'MAP NOT_IN_DATA'`. Non-finite or <= 0 prices are discarded by `num()` in `level_registry.js`. Missing `px` renders `<div class="lmz dim">NOT_IN_DATA</div>` in ladder. Stale timestamps trigger `<p class="pbmsg stale">STALE</p>`. |

---

## 3. Deep-Dive Edge Cases & Logic Inspection

### A. Level Distances & Ladder Ordering
- In `level_registry.js:77-79`, zones above `px` are sorted ascending by `lo` (`up.sort((a,b) => a.lo - b.lo)`), so index 0 is nearest to `px`. Zones below `px` are sorted descending by `hi` (`dn.sort((a,b) => b.hi - a.hi)`), so index 0 is nearest to `px`.
- In `map.js:90-94`, `lad.above.slice().reverse()` renders the highest zone at the top of the HTML ladder down towards `px`, followed by `px`, followed by `lad.below` descending down to the lowest zone. This matches natural visual price ladder orientation.
- In `map.js:84`, distance calculation `dist = Math.abs((side === 'above' ? z.lo : z.hi) / px - 1)` correctly measures proximity using the nearest boundary of the zone to `px`.

### B. Level Merging Tolerance
- `MERGE = 0.0015` (0.15% relative difference).
- The merge condition `it.price / z.lo - 1 <= tol + 1e-9` anchors each zone to `z.lo`. When subsequent prices arrive, they are checked against `z.lo` rather than the expanding `z.hi`. Thus, chaining is prevented and no single zone exceeds 0.15% width.

### C. NaN, Null, and Empty Data Handling
- `level_registry.js` enforces `num(x)`: `typeof x === 'number' ? x : parseFloat(x); return isFinite(v) && v > 0 ? v : null;`. Any `NaN`, `undefined`, `null`, negative price, or non-numeric string is filtered out cleanly before merging.
- When `px` is `NaN`, 0, or null, `map.html` falls back to `data.price`; if `data.price` is also invalid, `ladderHtml` renders `<div class="lmz dim">NOT_IN_DATA</div>`.
- When `data` or `data.sessions` is missing, `map.html` immediately returns `<p class="pbmsg">NOT_IN_DATA</p>`.

### D. Bias Calculation & Agreement Count
- `bias()` in `map.js:19-26` requires at least 3 valid votes in data (`v.length < 3 ? 'HOLD'`).
- LONG condition: `bull >= 2 && bull >= 2 * bear`.
- SHORT condition: `bear >= 2 && bear >= 2 * bull`.
- Neutral / split votes fall back to `HOLD`.
- When `b.thin` is true, the display shows `X of Y in data`. When `HOLD`, it displays `▲bull ▼bear of total`. When directional (`LONG` / `SHORT`), it shows `agree of total`.

---

## 4. Findings Summary

- **Total Clauses Checked**: 10
- **Matches**: 10
- **Differences (DIFF)**: 0
- **Not in Data (NOT_IN_DATA)**: 0
- **Logic Errors Found**: None. Implementation strictly adheres to specification in `REQUIREMENTS.md:61`.
