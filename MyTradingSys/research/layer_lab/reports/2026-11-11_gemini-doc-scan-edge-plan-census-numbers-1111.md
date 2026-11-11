COUNTS: MATCH=5 DIFF=0 NOT_IN_DATA=0

# Audit Report: EDGE_PLAN.md (a) and (c) numbers vs CENSUS_5M15M, AUCTION_CENSUS, REVIEW_FABLE, and OPERATOR_DECISIONS

- **Task**: `gemini-doc-scan-edge-plan-census-numbers-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11 UTC
- **Scope In**:
  - `MyTradingSys/research/edge_plan_2026-11-11/EDGE_PLAN.md` (sections a, c; read)
  - `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md` (read)
  - `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/AUCTION_CENSUS_1108.md` (read)
  - `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/REVIEW_FABLE.md` (read)
  - `MyTradingSys/system/OPERATOR_DECISIONS.md` (section `d-phase-first-method-1106`; read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-edge-plan-census-numbers-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## Executive Summary

Audit of `EDGE_PLAN.md` sections (a) and (c) verifying 5 specific clauses against the underlying source documents:
1. **Clause 1**: `-0.106 R n 1,484 for 40 bp fades` cites `CENSUS_5M15M_1109.md`. Found in `CENSUS_5M15M_1109.md:21,54` (net R -0.106, n=1,484, median stop 39.5 bps). Status: **MATCH**.
2. **Clause 2**: `+0.064 R gross` (before fees) for the fades arm in `CENSUS_5M15M_1109.md:20` (gross R per trade +0.064, and summary line 3 "+0.06 R"). Status: **MATCH**.
3. **Clause 3**: `10 bp round trip taker` in `AUCTION_CENSUS_1108.md:19,24` (SOURCED fees.py via auction_context.DEFAULT_TAKER_RT_BPS). Status: **MATCH**.
4. **Clause 4**: Stop-rule null `-0.087 R` in `REVIEW_FABLE.md` section d (`REVIEW_FABLE.md:67`) and summary (`REVIEW_FABLE.md:3,95`). Status: **MATCH**.
5. **Clause 5**: Stop rule cites `d-phase-first-method-1106` (`EDGE_PLAN.md:26`), and that section exists in `OPERATOR_DECISIONS.md:1812-1816`. Status: **MATCH**.

Overall count across all 5 audited clauses: **MATCH=5, DIFF=0, NOT_IN_DATA=0 (sum 5)**.

---

## Verification Table

| # | Clause / Claim | EDGE_PLAN.md Citation (file:line) | Target Source File:Line | Source Text Quoted | Status |
|---|---|---|---|---|---|
| 1 | Fades with 40 bp stops lost -0.106 R, n 1,484 | `EDGE_PLAN.md:15` | `CENSUS_5M15M_1109.md:21,25,54` | `:21` `\| net R, Deribit \| -0.106 (SE 0.078) \|`<br>`:25` `\| median stop \| 39.5 bps; median node target 2.1 R \|`<br>`:54` `\| 15m \| node+BE \| deribit \| session+ladder \| 1484 \| -0.106 \| 0.078 \| -1.4 \|` | MATCH |
| 2 | +0.064 R gross | `EDGE_PLAN.md:15` (referencing CENSUS) | `CENSUS_5M15M_1109.md:3,20` | `:3` `Before fees it makes +0.06 R (about 0.8 SE): the fade carries no direction, and 40 bps stops make fees decisive.`<br>`:20` `\| gross R per trade \| +0.064 (SE 0.077) \|` | MATCH |
| 3 | 10 bp round trip taker | `EDGE_PLAN.md:6` | `AUCTION_CENSUS_1108.md:19,24` | `:19` `Fee-net R = gross R - fee_r, fee_r = 10 bps round trip / stop distance in bps.`<br>`:24` `\| round-trip taker fee \| 10 bps \| SOURCED (fees.py via auction_context.DEFAULT_TAKER_RT_BPS) \|` | MATCH |
| 4 | Null -0.087 R in REVIEW_FABLE d | `EDGE_PLAN.md:26` | `REVIEW_FABLE.md:3,67,95` | `:3` `(re-run byte-for-byte: 2148 FAST_REJECTION events, 1871 gate-pass, -0.087 R; ...)`<br>`:67` `Context strip for 2 setups + per-trade log (session block, level family, htf bias, fee_r) + pre-registered kill: after 30 gate-pass fades on Deribit test, net R <= 0 -> stop and report. Null from this census: -0.087 R at 1R`<br>`:95` `2148 / 1871 / -0.087 R; 50/50 rows match (review_fable_recheck50.py)` | MATCH |
| 5 | Stop rule cites d-phase-first-method-1106 and section exists | `EDGE_PLAN.md:26` | `OPERATOR_DECISIONS.md:1812-1816` | `:1812` `## d-phase-first-method-1106 \| decided 2026-11-06 \| operator (voice, 18:55Z), recorded by Lead C`<br>`:1813` `Method: an edge is judged by market phase and by patterns that hold now, not by long multi-year backtests...`<br>`:1816` `Answer: phase-first, testnet-forward method adopted (operator, 2026-11-06).` | MATCH |

---

## Detailed Clause Verification

### Clause 1: Fades with 40 bp stops lost -0.106 R, n 1,484
- **EDGE_PLAN statement (`EDGE_PLAN.md:15`)**:
  > "Fades with 40 bp stops lost -0.106 R, n 1,484 (CENSUS_5M15M_1109.md)."
- **Source verification (`CENSUS_5M15M_1109.md`)**:
  - Line 3: `The pre-registered H1 (15m rejection fades, London/NY only, with the HTF ladder, node-to-node exit with break-even and half off at POC, Deribit maker fees) loses 0.11 R per trade over 1,484 trades (t = -1.4)`
  - Line 19: `| trades | 1,484 |`
  - Line 21: `| net R, Deribit | -0.106 (SE 0.078) |`
  - Line 25: `| median stop | 39.5 bps; median node target 2.1 R |`
  - Line 54: `| 15m | node+BE | deribit | session+ladder | 1484 | -0.106 | 0.078 | -1.4 |`
- **Result**: SOURCED match (`-0.106 R`, `n = 1,484`, median stop `39.5 bps` ~ 40 bps).

### Clause 2: +0.064 R gross
- **EDGE_PLAN context (`EDGE_PLAN.md:15`)**:
  - Refers to the fades study from `CENSUS_5M15M_1109.md`.
- **Source verification (`CENSUS_5M15M_1109.md`)**:
  - Line 3: `Before fees it makes +0.06 R (about 0.8 SE): the fade carries no direction, and 40 bps stops make fees decisive.`
  - Line 20: `| gross R per trade | +0.064 (SE 0.077) |`
- **Result**: SOURCED match (`+0.064 R` gross per trade, exact match to table row in `CENSUS_5M15M_1109.md:20`).

### Clause 3: 10 bp round trip taker in AUCTION_CENSUS_1108.md
- **EDGE_PLAN statement (`EDGE_PLAN.md:6`)**:
  > "Win rate needed with target = stop = the move (OURS arithmetic; 10 bp round trip taker SOURCED fees.py via AUCTION_CENSUS_1108.md; source table: four_model_review_2026-11-11/COMPARE.md s4):"
- **Source verification (`AUCTION_CENSUS_1108.md`)**:
  - Line 19: `Fee-net R = gross R - fee_r, fee_r = 10 bps round trip / stop distance in bps.`
  - Line 24: `| round-trip taker fee | 10 bps | SOURCED (fees.py via auction_context.DEFAULT_TAKER_RT_BPS) |`
- **Result**: SOURCED match (`10 bps` round trip taker fee citing fees.py via auction_context.DEFAULT_TAKER_RT_BPS in `AUCTION_CENSUS_1108.md:24`).

### Clause 4: Null -0.087 R in REVIEW_FABLE d
- **EDGE_PLAN statement (`EDGE_PLAN.md:26`)**:
  > "30 closed trades, then net R per trade <= 0 means the slot stops (SOURCED: REVIEW_FABLE d, null -0.087 R; OD d-phase-first-method-1106)."
- **Source verification (`REVIEW_FABLE.md`)**:
  - Line 3: `Verdict: the census is arithmetically right (re-run byte-for-byte: 2148 FAST_REJECTION events, 1871 gate-pass, -0.087 R; ...)`
  - Line 67 (Section d): `Context strip for 2 setups + per-trade log (session block, level family, htf bias, fee_r) + pre-registered kill: after 30 gate-pass fades on Deribit test, net R <= 0 -> stop and report. Null from this census: -0.087 R at 1R`
  - Line 95: `2148 / 1871 / -0.087 R; 50/50 rows match (review_fable_recheck50.py)`
- **Result**: SOURCED match (Null `-0.087 R` in `REVIEW_FABLE.md` Section d, line 67).

### Clause 5: The stop rule cites d-phase-first-method-1106 and that section exists
- **EDGE_PLAN statement (`EDGE_PLAN.md:26`)**:
  > "... (SOURCED: REVIEW_FABLE d, null -0.087 R; OD d-phase-first-method-1106)."
- **Source verification (`OPERATOR_DECISIONS.md`)**:
  - Section heading at line 1812:
    `## d-phase-first-method-1106 | decided 2026-11-06 | operator (voice, 18:55Z), recorded by Lead C`
  - Section content lines 1813-1816:
    - Line 1813: `Method: an edge is judged by market phase and by patterns that hold now, not by long multi-year backtests. A pattern visible in the current phase goes to the testnet at once and keeps trading until it stops working; we record when it works and the conditions in which it fails. Large-history backtests are not a precondition for testnet trades.`
    - Line 1814: `Example: the BTC four-year cycle (3 up, 1 down) held for 4 cycles; it needs no backtest...`
    - Line 1815: `Bound (Hard rules, unchanged): testnet only; mainnet still needs the fee-net out-of-sample record, which the testnet run now supplies.`
    - Line 1816: `Answer: phase-first, testnet-forward method adopted (operator, 2026-11-06).`
- **Result**: MATCH (Section exists and defines phase-first, testnet-forward method where patterns trade until they fail/stop working).
