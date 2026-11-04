# Re-Check Spec Review: Layer Bible + layer_state.py runtime (DESIGN.md v2)

- **Target Spec**: `MyTradingSys/research/layer_bible/DESIGN.md` (commit deff345f2714)
- **Reviewer**: Gemini 3.8 Flash (same review lens re-checking against `REVIEW_GEMINI_1104.md`)
- **Date**: 2026-11-04
- **Scope**: Items 1-6 from `REVIEW_GEMINI_1104.md` and new defects in `DESIGN.md` v2 additions (lines 25-36).

---

## 1. Item-by-Item Disposition Check (Items 1–6)

- Item 1 [no fetch depth vs 200-bar warm-up]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:28` specifies Parameters carry `bars` (1000 per TF, 800 above warm-up 200), that fewer closed bars than warm-up prints `NOT_IN_DATA`, and `--at` fetches the 1000 bars ending at `at`.
- Item 2 [cycle/dot rule deferred]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:29` sources cycle start/end from operator quote 11-04 ~13:30Z (up-cross from lower zone to opposite cross), tags OURS for turning dot prior-bar wt1 at/beyond +-53 and intermediate crosses not ending cycle, specifies COMPLETED when valid top dot prints, and justifies rejecting Gemini's zero/mid-line completion rule because operator did not say it.
- Item 3 [Parameters block format unspecified]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:30` specifies exactly one fenced ```` ```json layer_state ```` block read by `json.loads` and fails closed on zero or multiple blocks.
- Item 4 [closed-bar filter, venue]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:31` mandates closed-bar filter `open + tf <= at` (tested), sources Binance spot klines via `data-api.binance.vision`, explicitly adds `symbol` and `source` to Parameters, and clarifies perp vs spot usage.
- Item 5 [contract has no mechanical gate]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:32` disposes as DEFERRED with clear justification: separate card later for a lint flagging layer-state claims without a STAMP, avoiding new CI gates while CI is red.
- Item 6 [11-04 fixture not pinned]: RESOLVED. SOURCED `MyTradingSys/research/layer_bible/DESIGN.md:33` pins fixture file `fixture_btcusdt_3m_2026-11-04.csv` and its SHA-256 hash `abb8d293499981aaf799f71566b66d82e70e14165225caf579cfa5e12e883350` to be asserted by test.

---

## 2. Check for New Defects in v2 Text

- Scanned `DESIGN.md:25-36` (v2 changes table and open question on valid tops).
- No new E1-E7 defects found. The handling of multiple valid tops in open question (`DESIGN.md:36`) reporting all and last is safe and deterministic.

---

VERDICT: ACCEPT
