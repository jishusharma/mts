# Gemini layer fact sheets: independent Claude review (2026-10-26)

Reviewer: Claude Opus (Lead-assigned review session, login C) with 3 Sonnet reader agents doing the line-by-line checks; verdicts are the reviewer's.
Producer: Gemini (NUC lane, `origin/gemini-q/lf-<family>-gemini-facts`, 2 commits each).
Truth: `origin/fast-track` at review time. Method: (1) a script checked every `path:line` cite exists and every quote appears within +-3 lines of its cite; (2) readers re-checked every flag, every number and every code claim against trunk; (3) the reviewer re-read the key claims (the invented Malkan quote, the B146/B147 titles, the T090 numbers, the TOM split line, the T055 rerun parameters, the wavetrend verdict rows, the CT-048 timeframe quote) before applying fixes.

**Result: 10 ACCEPT-WITH-FIXES, 0 ACCEPT, 0 REJECT.** No layer was discarded or demoted. The fact sheets are new files only; the branches' only deletions are card bookkeeping (card `state` ready -> done, and the generated `LAYERS.md` dropping the closed card's "open card" line). No trunk content is overwritten.

Counts are the readers' tallies of discrete claims, so they are approximate. "Cite drift" = content true, line number off; drift is **not** rewritten in the sheets (each sheet carries a review banner saying so); the main remaps are in the appendix.

## Verdict table

| branch | verdict | facts checked | WRONG | UNVERIFIED | cite drift | content fixes made |
|---|---|---|---|---|---|---|
| lf-callers | ACCEPT-WITH-FIXES | 62 | 8 | 4 | ~22 | targets "1 to 5" -> one or more (schema.py:59-63); collision rule and power test SOURCED -> OURS; power-test H0/H1 orientation stated both ways; n=22 is labelled candles, not trades; p=0.003 caveats (one cell, rough p, labels in holdout); B190 marked as a keyword hit unrelated to the layer; live_engine "confirmation" -> NOT_IN_DATA |
| lf-cryptocred | ACCEPT-WITH-FIXES | ~230 | 6 | 2 | ~60 | timeframe claim (daily/4h, wrong cites) -> CT-048 quote "daily and weekly ... entries on the hourly" (cross_trader_consolidated.md:515); quote "structure" -> "structures"; tick SOURCED -> OURS (protocol); CC adapter IS/OOS -> NOT_IN_DATA; parity 0-4% marked superseded by the spot rerun (92-100%); EXIT_POLICIES CONTAMINATED caveat added; report card cite :2 -> :16 and tick removed from trader-sourced list |
| lf-fabio | ACCEPT-WITH-FIXES | ~190 | 6 | 3 | ~75 | invented "verbatim" bearish quote -> the real docstring (fabio_cvd_absorption.py:6-7); "was balanced" -> "is balanced"; `va_pct` -> `pct` of value_area at :116; TICK SOURCED -> OURS/SIM; 2 bps is slippage per taker leg, not total fee |
| lf-guidance | ACCEPT-WITH-FIXES | 98 | 6 | 3 | ~46 | S14 quote belonged to S13 -> no verbatim quote, points to FABIO_TRADE_MODEL.md:9-40; VWAP 00:00 anchor SOURCED -> OURS; weekly POC migration SOURCED -> NOT_IN_DATA; Bollinger/Wilder/Malkan attribution -> NO-SOURCE; half split is index N//2, not calendar years; event-study caveat added; B172/B105 marked keyword hits; 98 NUC-local `file:///F:/MTS/gq/...` links -> repo-root links; transcript bare names -> raw_transcripts_canonical/ |
| lf-krown | ACCEPT-WITH-FIXES | ~150 | 2 | 0 | ~45 | "the gold standard" -> transcript "a gold standard" with the real cite (extracts/extract__t_XIBrcjRk.md:119); stop-distance cite -> KROWN_SETUP_CATALOG.md:23; report: "fee-net" -> "NOT fee/funding-adjusted, fixed 14 bp cost screen"; "Tom (10 setups)" -> 10 overlap rows |
| lf-pitchfork | ACCEPT-WITH-FIXES | ~95 | 7 | 6 | ~25 | Dologa attribution removed (source names no author); VA-confluence SOURCED -> OURS; "HOLDOUT unread" -> NOT_IN_DATA (window to 2026-09-26 overlaps the holdout); backtested stops (1.5%/2.0%) noted vs the 1 ATR spec; n=361 is per model; benchmark table marked NOT REPRODUCIBLE (no code computes it); 77.7->86.4/88.4% marked as two inconsistent unbacked claims; biography flagged single-source LLM synthesis; Schiff definition conflict noted |
| lf-positioning | ACCEPT-WITH-FIXES | 88 | 9 | 4 | ~16 | `rulings.json` (does not exist) -> BUGS.md:213; first T055 run marked SUPERSEDED/invalid; stale IS-chosen 180/.99/.01 -> rerun 90/50/.95/.05/48 (T055_BT_RERUN_FULLFUNDING:29); invented oi_delta origin and "intended interaction" -> NOT_IN_DATA with the real BackQuant/T3 cites; CONTEXT slot overstated -> "could fill"; "high autocorrelation" -> clustering on few days; fee cite :1396 -> :1042 |
| lf-rsi | ACCEPT-WITH-FIXES | ~170 | 9 | 3 | ~70 | **invented quote** ("I found no dated trade ledger for Vishal B Malkan...", appears nowhere in the repo) -> real text HOME_FIT_AUDIT_MALKAN.md:19; RSI 14 SOURCED -> CONCEPT-ONLY; FIRES-B1 counts marked superseded perp run; "70/30" split not stated -> removed; T090 anchor probe rewritten with the real file and n=46/47/45/43; 6h/2d n fixed; Super Signal wording per KURISKO_SPEC; (40,4) "contested" caveat; B163 ruling added; 28 bare filenames -> full paths |
| lf-tom | ACCEPT-WITH-FIXES | ~100 | 6 | 3 | ~30 | B147 and B146 had the wrong ruling text -> real titles; "In-sample 2022-01-20..2026-06-25" -> hist/dev/holdout split, all out-of-sample (TOM_CORE_BT.md:20); vp_pivot "confirms tom_core / pitchfork" -> NOT_IN_DATA; 1818 candidates wording; maker net R wording; "thousands per stream" -> min n 1,055 |
| lf-wavetrend | ACCEPT-WITH-FIXES | 92 | 4 | 3 | ~8 | "(TradeStation / MetaTrader)" invented -> removed; event sum 15,604 -> 15,594 (recomputed: 3893+4196+3509+1154+788+538+298+271+947), cells overlap; `rulings.json` -> BUGS.md; layer_index cite -> :716; final labels added (W01-03, W09 FAIL; W04-08 INCONCLUSIVE; research/VERDICTS.csv:56-64); 132 NUC-local links -> repo-root links |

Totals: WRONG 63, UNVERIFIED 31, all WRONG items fixed in the sheets; UNVERIFIED items are either fixed to NOT_IN_DATA or carry a caveat.

## Patterns worth fixing in the Gemini prompt (for the next fact-sheet run)

1. **Line numbers drift everywhere** (~400 cites, mostly +-1..20, `layer_map.json` by hundreds). Gemini appears to cite from an older layout or from memory of the file. Ask it to quote the cited line text next to each number, or run `scripts/dev/verify_extract_quotes.py`-style checks before shipping.
2. **Superseded runs reported as current** (FIRES-B1 perp parity, T055-C1 first run, EXIT_POLICIES contamination). Ask it to read the top 10 lines of each report for SUPERSEDED / CONTAMINATED / RERUN banners.
3. **SOURCED labels on OURS values** (tick, VWAP anchor, VA confluence, power test, RSI 14). Ask it to copy the label from the spec row, never infer it.
4. **Keyword-matched rulings** (`lab_query.py rulings <family>` returns rows that merely contain the word: B190 callers, B172/B105 guidance). Ask it to say whether a ruling concerns the layer.
5. **Two invented quotes** (rsi Malkan ledger, fabio bearish "verbatim") and invented glosses (TradeStation/MetaTrader, Dologa attribution, oi_delta "literature"). Every quote must be a grep hit.
6. NUC-local `file:///F:/MTS/gq/...` links in two sheets; use repo-root paths.

## Appendix: main cite remaps (content true, line wrong; `old -> new` on trunk)

- **layer_map.json (tom)**: tom_core module :49 -> :9; min_proof :52-62 -> :12-22; fee_model :63-74 -> :23-34; tom_vp_pivot block :118-124 -> :78-84; barrier :168-176 -> :127-135; TOM-CORE-0929 :415-429 -> :848-865; TOM-CORE-1007 :430-444 -> :867-884; TOM-VP-PHASE2 :445-459 -> :886-902; DAX-SMOKE :460-474 -> :904-921; TOM-DIAG-BTC :499-510 -> :1106-1122; VP-PIVOT-P2 :511-523 -> :1124-1140.
- **layer_map.json (rsi)**: :448-478 -> :269-344; :626-641 -> :719-736; :710-724 -> :1014-1030; :738-755 -> :1160-1182; :643-659 -> :923-938.
- **layer_map.json (positioning)**: :590-593 -> :380-388; :597-600 -> :389-397; :604-607 -> :398-406; :610-613 -> :407-416; :617-620 -> :417-425; :626-630 -> :622-629.
- **layer_index.json**: callers :206-253 -> :558-630; rsi :104 -> :232-258; krown :426 -> :635, :442 -> :654; guidance :161 -> :178-199; wavetrend :15 -> :716.
- **LAYERS.md**: cryptocred :106-116 -> :108-118; krown :222 -> :224; pitchfork :256/:259 -> :262/:265; callers :208-220 -> :210-221; positioning :122 -> :124; rsi :88-89 -> :89-90; wavetrend :243-255 -> :248-255.
- **cryptocred**: STOP_SOURCES.md Run 6 :47-69 -> :51-79 (each table row +6); cc_structure.py :68 -> :81, :47 -> :63; CC_SETUPS_RERUN_LIMITFILL Run 2/3 :1-125 -> :20-151, :144-245 -> :157-313; B145 :29-34 -> :31; BACKTEST_L1_REPORT.md :39-42 -> :41-43.
- **krown**: KROWN_SETUP_CATALOG.md overlap rows :980-996 -> :981-997 (each +1); quotes at :1021, :1005, :1032; candle_close REPORT.md cost :3,13 -> :11.
- **fabio**: FABIO_L1_REPORT.md :27-32 -> :33-38, :40-45 -> :53-58; fabio_of_model.py :27-32 -> :34-39; PRE_REG_FABIO_V3.md :39-42 -> :44-47; SOURCED_RULES.md :80-83 -> :58-59; analyst name -> fabio_asr_2026-10-16/ASR_EXTRACTION_ADDENDUM.md:14.
- **rsi**: rsi_divergence_mtf RESULT.md :5 -> :7, :8 -> :11, :9 -> :12, :15-16 -> :18-19; KURISKO_SPEC.md :7 -> :10, :12 -> :15; malkan_divergence_default.json :10 -> :11.
- **guidance**: SOURCED_RULES.md every :N (14-27) -> :N+2; FAST_MOVE_CATALOGUE.md :46 -> :37; matrix_q33.py functions moved (e.g. :6-35 -> :65-95, :58-65 -> :181-197); tom_bt.py fabio_tag :280-290 -> :303-304.
- **pitchfork**: SET_362293de1b70_pitchfork.md :4,19 -> :5,21; swing threshold actually used: 0.04 (1D, run_pitchfork_event_study.py:135), 0.03 (4H, run_pitchfork_4h_poc_study.py:146).
- **callers**: schema.py :50-51 -> :49, :65-68 -> :66-70; score_analysts.py :27-29 -> :17,20,21, :114-135 -> :41-106.

## Open observations (not fixed; for the GPT re-derive cards `lf-<family>-gpt-rederive`)

- pitchfork: PHASE2 table Avg Win/Avg Loss disagree with `TRIALS_PITCHFORK_4H.csv` in 27 of 32 rows; PHASE1 text says breach 42.5% while its table says 50.97%; reach 76.8-81.2% in text vs 89.2/90.03% in table.
- callers: qriptal SCORECARD DEV 11 + HOLDOUT 67 = 78, not the stated 81.
- krown: LAYER_SHEETS.md:23-24 says "detectors not built" and "15 of 19 videos" are stale.
- rsi: LAYER_SHEETS.md:11 still lists T09 F3 (live event set differs) although the spot rerun passed parity.
