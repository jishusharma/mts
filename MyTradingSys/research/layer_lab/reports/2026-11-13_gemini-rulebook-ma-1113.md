# Report: Moving averages Rule Book (gemini-rulebook-ma-1113)

Date: 2026-11-13 (UTC)
Worker: gemini-3.8-flash-low
Card: `gemini-rulebook-ma-1113`
Target: `MyTradingSys/research/indicator_rulebooks/MOVING_AVERAGES.md`

## Summary of Completed Work
1. Read `MyTradingSys/research/indicator_rulebooks/TEMPLATE.md` and `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md` (the model).
2. Gathered developer's canonical rules (Eric Krown TA 101 stack: 21 EMA, 55 EMA, 200 SMA/EMA; classic SMA/EMA origins from Hooker/Yule, Donchian, Haurlan, Granville) and opened independent public web sources. Every claim in Section 2 and Section 3 is marked SOURCED (with primary URL or verbatim extract file:line) or UNVERIFIED.
3. Conducted repo-wide grep across extracts (`research/krown_ta101_2026-10-13`, `research/nk_stocktalk_1113`, `research/yt_feed_2026-10-31`, `research/tom_fabio_guidance_2026-10-12`, `research/malkan_extract_2026-10-15`, orderflow extracts) to compile Section 4 with verbatim analyst rules and file/timestamp pointers (Krown, CCU, NK, Tom, Fabio, Malkan, CryptoCred, Habib).
4. Authored `MyTradingSys/research/indicator_rulebooks/MOVING_AVERAGES.md` adhering strictly to TEMPLATE.md sections 1 through 8. Section 5 contains pointers to repository studies only (no numbers per task instruction):
   - `MyTradingSys/research/ma_layer_2026-11/`
   - `MyTradingSys/research/setup_alpha_beta_v2_2026-10/`
   - `MyTradingSys/research/btc_ma_2026-10-03/`
   - `MyTradingSys/research/btc_50w_ma_j-JVi02_1112/`
   - `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/`
5. Updated `MyTradingSys/research/indicator_rulebooks/INDEX.md` row for Moving averages from `PARTIAL` to `DONE`, updating the Pointer and status counts.
6. Verified that `scripts/dev/rulebook_check.py` passes cleanly (22 layer folders, all in INDEX).

## Verification and Quality Checks
- `python scripts/dev/rulebook_check.py`: PASS (exited 0)
- `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md`: PASS (exited 0)
- `git status --short`: clean check before commit.
