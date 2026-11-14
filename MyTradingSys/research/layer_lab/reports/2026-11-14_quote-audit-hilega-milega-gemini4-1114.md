# Quote Audit Report: `HILEGA_MILEGA.md`

- **Card:** `quote-audit-hilega-milega-gemini4-1114`
- **Audited File:** `MyTradingSys/research/indicator_rulebooks/HILEGA_MILEGA.md`
- **Deliverable:** `MyTradingSys/research/layer_lab/gemini_1114d/quote-audit-hilega-milega/QUOTES.md`

## Summary Findings (OURS)
- **Result:** `10 FOUND / 3 NOT FOUND` across the 13 cited quoted spans in `HILEGA_MILEGA.md` (lines 14, 16, 17, 18, 19).
- **Verbatim Hindi quotes (5/5 FOUND):** All 5 Hindi quotes on `HILEGA_MILEGA.md:16-18` match `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md` (lines 57, 63, 33, 39, 51) and `raw_transcripts_canonical/JLcDdrHkB5M_raw.txt:8` after whitespace normalization. Two on `HILEGA_MILEGA.md:18` omit leading/trailing words (`और 10:15 है` on line 39; `तो ` on line 51) without an ellipsis.
- **Extract translations & metadata (5/5 FOUND):** The 2 quoted English translations on `HILEGA_MILEGA.md:16-17` match `EXTRACT.md:60` and `EXTRACT.md:66` verbatim, and the 3 `NOT_STATED:` strings on `HILEGA_MILEGA.md:19` match `EXTRACT.md:74-76` verbatim.
- **Unverified / NOT FOUND quoted aliases (3/3 NOT FOUND):** `HILEGA_MILEGA.md:14` places `"NK Sir"`, `"Hilega To Milega"`, and `"Hilbe_milbe"` in double quotes while citing `NK_EXT:7, NK_MINE:3`; none of the three appear in `EXTRACT.md`, `RULES.md`, `concepts.json`, or `JLcDdrHkB5M_raw.txt`.
- **Tool check:**
  - `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/indicator_rulebooks/HILEGA_MILEGA.md`: `PASS: 0 problem(s)` (checks only backticked `path:line` cites on lines 29 and 34; skips shorthand `NK_EXT:` cites on lines 14–19).
  - `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md`: `PASS: 0 problem(s)` (9/9 quotes OK).
