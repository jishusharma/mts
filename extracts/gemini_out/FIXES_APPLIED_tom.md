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
| F6 (LOW) nine Source GPS tags drift vs caption body | 7BQPMJ39WpI:63,83,88; gWjHq5UMisY:28,33; hQ8sOq67x5o:43; HySZZSjMxF8:33; WQ_OAdz-PJ8:78; zAwEX_tRUfE:23 | tags as in report table | **DEFERRED, not applied.** Reason: verify_extract_quotes.py computes thirds on the text after the first `# ---` marker, which still contains the nested metadata header (verifier line 43, body split). Re-tagging to caption-body thirds fails the gate: probe on gWjHq5UMisY set 5 tags to BEGIN/MIDDLE by caption position and the verifier reported POSITION failures at lines 28, 33, 38, 43, 75. Fixing F6 needs the verifier to normalise to the caption body (separate card). Tags are left as they pass the gate. |

Gate results after edits:
- verify_extract_quotes.py exit 0 on all 7 extracts (7BQPMJ39WpI, 96iPFDpXEcU, gWjHq5UMisY, hQ8sOq67x5o, HySZZSjMxF8, WQ_OAdz-PJ8, zAwEX_tRUfE).
- Caption-body check on gWjHq5UMisY (independent re-implementation: pending_raw body after first `# ---`, alphanumeric match): 12/12 (was 10/12).
- The report's audit.py is not present in this worktree; the caption-body check above was run directly.

Not done: no change to aursfDVYzUk or pgdmKLJ0hhA (APPROVE); no change to the audit or Fabio files; no FIXES file outside this one.
