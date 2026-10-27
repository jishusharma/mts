# Compaction effectiveness report (2026-10-16)

Method: the same audit as the 2026-10-15 one (`audit_comp2.py`), re-run over all session transcripts since 2026-10-14, split at the audit (2026-10-15 17:43Z). Cost model is unchanged so the numbers compare: a compaction costs `pre*0.1 + post*1.25 + 40k` input-equivalent tokens (cache read of the old context, cache write of the new one, ~8k of summary output at 5x). It saves `(pre-post)*0.1` per later turn.

## Result

| | Before audit | After audit (this time) |
|---|---|---|
| Compactions | 70 (32 sessions) | 20 (12 sessions) |
| Avg context at compaction | 170k | 268k |
| Avg context after | 71k | 72k (the fixed floor) |
| Turns after, median | 25.5 | 36.5 |
| Done with <5 turns left | 14 (20%) | 3 (15%), see below |
| Losing money | 39 of 70 (56%) | 3 of 20 (15%) |
| Cost / saving (M input-equiv) | 10.2 / 18.5 | 3.1 / 14.1 |
| Saving per unit of cost | 1.8x | 4.5x |

**Verdict: yes, much more effective.** Each compaction now pays back about 2.5x better, and the share that lost money fell from 56% to 15%.

## Why it worked
- Compacting later (268k vs 170k) means each one removes ~195k tokens instead of ~100k, so a similar fixed cost buys about twice the saving.
- Median 36 turns of life after each one, against the ~15-turn break-even.
- Post-compaction context is always ~72k, the fixed overhead (tools, MCP, skills, memory). Nothing more can be squeezed out.
- Re-reads of files after compaction are tiny (about 200 tokens per compaction, down from 1.7k).

## The three that lost
- 22:38Z (krown-malkan-p6) and 00:15Z (catalogue audit rebuild, Fable): the session ended right after, so the compaction bought nothing.
- 06:01Z (the Fable usage session): just done, so the result is not in yet.
Rule: if the session will end in under 15 turns, hand off or stop instead of compacting.

## Caveats
- Costs are modelled from transcript token counts, not billed amounts.
- Three events show 0 turns after because the transcript ended or has not continued yet; the 03:26Z `03f2a64b` event had a parsing quirk (post-context 0, 64 turns after), which makes its cost slightly understated.
- The one caveat on "later is better": the turns just before a late compaction ran at ~270k per turn. Going past ~300k (several reached 300-375k) gives diminishing returns. A target of 220-280k looks like the sweet spot.

## Update 2026-10-17 (12 more compactions, through 2026-10-16 17:12Z)

After the audit: 32 compactions in 16 sessions (31 manual, 1 auto). Avg context at compaction 250k, after 78k. Median 46.5 turns afterwards. Saving per unit of cost 4.4x (was 4.5x, was 1.8x before the audit). 4 of 32 lost money (was 3 of 20).

The 12 new ones: 9 clearly paid (27 to 113 turns left each). Not paid: 08:26Z (Opus, only 7 turns left), 08:18Z (`6a545399`, ended right after). 16:35Z was the only auto compaction (Fable session `4b37f3f9`, at 246k), harmless, still 50 turns afterwards.
Trend: the 09:20Z and 15:57Z ones fired at 154k to 170k (earlier than the 220k to 280k target) but still had 54 to 90 turns left, so they paid too.
