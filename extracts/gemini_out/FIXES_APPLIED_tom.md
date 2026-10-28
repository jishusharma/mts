# FIXES APPLIED - GPT review of Gemini Tom extracts (report: MyTradingSys/research/gpt_burn_2026-10-24/gx2-review-tom-extracts/report.md)

| Finding | File:line | Before | After |
|---|---|---|---|
| F1 (HIGH) volume acceptance promoted to breakaway | 96iPFDpXEcU_gemini.md:40 | "Substantial volume at an opening gap confirms price acceptance and signals a breakaway gap rather than a gap fill." | "Substantial volume at an opening gap confirms price acceptance (P structure); it signals a breakaway only once price breaks out upward, and the direction of the subsequent breakout must still be observed." |
| F1 (shortened context) | 96iPFDpXEcU_gemini.md:32 | "...substantial volume indicate institutional acceptance and form breakaway gaps." | "...substantial volume indicate institutional acceptance, and become breakaway gaps only if price then breaks out upward." |
| F2 (LOW) 32% is slightly profitable | gWjHq5UMisY_gemini.md:16 | "...breaks even theoretically without fees at a 32% win rate." | "...is slightly profitable at a 32% win rate before fees (exact break-even 31.25% under fixed-payoff assumptions)." |
| F3 (HIGH) waiting turned into abandoning | HySZZSjMxF8_gemini.md:17 | "If price fails to trade back down through elevated spike volume, the trade setup must be abandoned." | "If price does not yet trade back down through elevated spike volume, wait for confirmation; the setup is abandoned only on the structural break above the swing high (see negative rule 3)." |
| F4 (LOW) mirrored long-stop presented as sourced | HySZZSjMxF8_gemini.md:15 | "Stop losses are placed above swing highs for short trades or below swing lows for long trades." | "Stop losses are placed above swing highs for short trades (the long-side mirror below swing lows is INFERRED from the short example, not sourced)." |
| F5 (HIGH) negative-rule quotes from description | gWjHq5UMisY_gemini.md:70 | "Most traders completely mix up these two concepts without realizing..." (description only) | "Because many people mix up these concepts." (caption body, raw transcript_gWjHq5UMisY.txt line 14 of pending_raw) |
| F5 | gWjHq5UMisY_gemini.md:75 | "If you don't understand this one point, you won't make money long-term, even with the best setup." (description only) | "the next thing that is absolutely crucial to understand is this." (caption body); its Source GPS tag changed BEGIN -> MIDDLE (verifier thirds, line 76) |
| F6 (LOW) Source GPS tags drift vs caption body | 7BQPMJ39WpI:64 | `**Source GPS: 7BQPMJ39WpI \| MIDDLE**` | `**Source GPS: 7BQPMJ39WpI \| BEGIN**` (aligned with stripped caption-body verifier) |
| F6 | 7BQPMJ39WpI:84 | `**Source GPS: 7BQPMJ39WpI \| END**` | `**Source GPS: 7BQPMJ39WpI \| MIDDLE**` |
| F6 | 7BQPMJ39WpI:89 | `**Source GPS: 7BQPMJ39WpI \| END**` | `**Source GPS: 7BQPMJ39WpI \| MIDDLE**` |
| F6 | gWjHq5UMisY:29 | `**Source GPS: gWjHq5UMisY \| MIDDLE**` | `**Source GPS: gWjHq5UMisY \| BEGIN**` |
| F6 | gWjHq5UMisY:34 | `**Source GPS: gWjHq5UMisY \| MIDDLE**` | `**Source GPS: gWjHq5UMisY \| BEGIN**` |
| F6 | HySZZSjMxF8:34 | `**Source GPS: HySZZSjMxF8 \| MIDDLE**` | `**Source GPS: HySZZSjMxF8 \| BEGIN**` |
| F6 | WQ_OAdz-PJ8:79 | `**Source GPS: WQ_OAdz-PJ8 \| END**` | `**Source GPS: WQ_OAdz-PJ8 \| MIDDLE**` |
| F6 | zAwEX_tRUfE:24 | `**Source GPS: zAwEX_tRUfE \| MIDDLE**` | `**Source GPS: zAwEX_tRUfE \| BEGIN**` |
| F6 | hQ8sOq67x5o:44 | `**Source GPS: hQ8sOq67x5o \| BEGIN**` | Already BEGIN (evaluated at offset 4111/12336, exactly ratio 0.3332 in caption-body coordinates, passes verifier) |

Gate results after edits:
- verify_extract_quotes.py exit 0 on all 7 extracts (7BQPMJ39WpI, 96iPFDpXEcU, gWjHq5UMisY, hQ8sOq67x5o, HySZZSjMxF8, WQ_OAdz-PJ8, zAwEX_tRUfE).
- Caption-body check on gWjHq5UMisY: 12/12 matches (0 non-body quotes).
- All F1-F6 findings addressed and verified.

Not done: no change to aursfDVYzUk or pgdmKLJ0hhA (APPROVE); no change to the audit or Fabio files; no FIXES file outside this one.
