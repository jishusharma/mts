# Report: Open Interest Rule Book (gemini-rulebook-oi-1113)

Date: 2026-11-13 (UTC)
Worker: gemini-3.8-flash-low
Card: `gemini-rulebook-oi-1113`
Target: `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md`

## Summary of Completed Work
1. Read `MyTradingSys/research/indicator_rulebooks/TEMPLATE.md` and `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md` (the model).
2. Gathered developer's canonical rules (CME Group official clearinghouse definitions and contract counting mechanics, Binance USDS-M and COIN-M Futures API specifications, BitMEX continuous perp open interest origin, John J. Murphy technical analysis rules) and opened independent public web sources (Definedge/Quantsapp 6-state scan models, CoinGlass aggregated crypto open interest and leverage analytics). Every claim in Section 2 and Section 3 is marked SOURCED (with primary URL) or UNVERIFIED.
3. Conducted repo-wide grep across extracts (`research/krown_ta101_2026-10-13`, `research/nk_stocktalk_1113`, `research/yt_feed_2026-10-31`, `research/tom_fabio_guidance_2026-10-12`, `research/malkan_extract_2026-10-15`, `research/oi_side_2026-10-30/`) to compile Section 4 with analyst rules and file/timestamp pointers (Krown, Operator, Tom, Fabio, CCU, Malkan, NK, CryptoCred, Habib).
4. Authored `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md` adhering strictly to TEMPLATE.md sections 1 through 8. Section 5 contains pointers to repository studies only (no numbers per task instruction):
   - `MyTradingSys/research/oi_side_2026-10-30/` (`OI_CONCEPTS.md`, `study.py`, `RESULT.md`)
   - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/` (`OI_COMMENTARY_SPEC.md`, `OPERATOR_POINTERS.md`)
   - `MyTradingSys/research/flow_layers_concepts_2026-10-28/` (`README.md`)
   - `MyTradingSys/research/wlow_bounce_bbrsi60_2026-10-16/` (`PRE_REG.md`, `RESULT.md`)
   - `MyTradingSys/research/c26_roadmap_2026-11-01/` (`PHASE1_RANGE.md`, `phase1_liq_look.py`)
   - External candidate side-notes: `edge-oi-flush-1113_RESULTS.md`, `edge-crowding-reversal-1113_RESULTS.md`, `edge-forced-move-fade-1113_RESULTS.md`
5. Updated `MyTradingSys/research/indicator_rulebooks/INDEX.md` row for Open interest from `PARTIAL` to `DONE`, updating the Pointer and status counts.
6. Verified that `scripts/dev/rulebook_check.py` passes cleanly (22 layer folders, all in INDEX).
7. Verified that `scripts/dev/verify_extract_quotes.py` passes cleanly on `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md` (6/6 cites OK, 0 problems).

## Verification and Quality Checks
- `python scripts/dev/rulebook_check.py`: PASS (exited 0)
- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md`: PASS (exited 0, 0 problems)
- `git status --short`: clean before final commit.
