# Layer Lab Report: gpt-argon-score-recount

## 1. Verdict

SOUND — the section 3 core score rows recount to MATCH 16, MISMATCH 1, CORRECT_NULL 5, MISSED_NULL 0, INVENTED 4, UNVERIFIED 2 (28 total). The four `UNVERIFIED_LOCAL` top-panel rows are excluded. This confirms score-row arithmetic and consistency with the producer JSON, not the truth labels: that base is marked UNVERIFIED.

## 2. What was checked

- `MyTradingSys/research/layer_lab/reports/2026-10-22_argon-blind-read-7-frames.md:39-70`: manually recounted each section 3 row; omitted top panel rows 63-66 because their truth is `UNVERIFIED_LOCAL`.
- `MyTradingSys/research/layer_lab/argon_blind_read/results_argon-low.json:10-27, 28-286, 329-337`: compared computed counts to producer's descriptive count and the per-evaluation `truth`, `argon_parsed`, and `argon_scores` fields.
- `MyTradingSys/research/lab_guy/pilots/2026-10-18_gemini_frame_read/hard_results_gemini-3.8-flash-low.json`: checked corresponding Flash blind outputs and stored truth for the seven underlying frames.
- `MyTradingSys/research/lab_guy/pilots/2026-10-18_gemini_frame_read/README.md`: checked source provenance; it says truth comes from a 2026-10-12 frame audit and the frame images are not copied.
- No backtest or market data was involved; PRE_REG_TEMPLATE does not apply. No code or specifications changed.

## 3. Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/research/lab_guy/pilots/2026-10-18_gemini_frame_read/README.md:8,16` | NOT_IN_DATA: original image frames are absent here, so I could not independently verify visual truth labels (including the contested k0zm target and T6hDJcHrVBM_0550 stop). | README says frames are not copied and names source `F:/MTS/data/tom_videos/frames`; actual frame files were not found in the available source folder. Truth remains the existing audit's assertion. | Human/source-image review if validating the truth base is required; no change to recount. |
| LOW | `MyTradingSys/research/layer_lab/reports/2026-10-22_argon-blind-read-7-frames.md:39-70`; `MyTradingSys/research/layer_lab/argon_blind_read/results_argon-low.json:10-27` | No score arithmetic error found. Four local-only rows are outside the 28-field core; the remaining rows match the stated breakdown. | Recount excluding rows 63-66: 16 + 1 + 5 + 0 + 4 + 2 = 28. Producer JSON lines 10-17 gives the same totals. | None. |

## 4. Follow-up cards

None. No HIGH findings.

