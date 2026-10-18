# Krown Foundations EP08 (order book): what it means for MTS (2026-10-18)

Source: `extracts/extract_ftK2BqggabQ.md` (22 concepts, quote gate PASS 0 problems, number gate 36 checked 0 not found). Video ftK2BqggabQ,
published 2026-10-17, 33 min, titled "The Coinbase Screen Nobody Opens (I Made a Living Inside It)" (alternate title seen: "The Order Book Is Lying to You").
Evidence tier T3: his statements are ideas and definitions, not edge.

## Verdict
An execution lesson, not a setup video. No entry, stop, target or size anywhere. His own conclusion (t=00:25:00): the order book is "one of the worst
ways to pick directions" and "the worst compass to use but it is the best receipt". Direction lives in episodes 1 to 7 (already extracted).
It carries an affiliate (partner link) fee promotion (80% off spot, 10% off derivatives): sponsored, not market data.

## What we need to do (in priority order)
1. **No Krown order-book layer.** Do not build a wall or depth-imbalance layer from this video. His claim is that walls and resting size are advertisement
   (painting, spoofing, iceberg, TWAP). Any wall or depth idea elsewhere in the backlog needs its own PRE_REG with a null expectation; his statement is
   a T3 claim to test as the null, not a rule to follow. Status: decided here by default, no card needed.
2. **Cost and fill realism (the one useful part).** He says maker orders cost significantly less than taker orders and that a limit order only fills if the
   market comes to you; he gives no percentages (t=00:09:44) and his live fee screens do not show a gap (both order types looked equally cheap on his
   discounted tier, t=00:13:05). So take fees from the exchange's published tables, never from his affiliate figures. Where it lands: `gap-g7-stop-slippage`
   (ready), `dsa-audit-06-cost-fill-realism` (CRUCIAL, ready), `gap-g3-shadow-fills` (raw). Suggested arm when one of them runs: a limit-entry case
   (maker fee, fill-rate and adverse-selection haircut) beside taker-both-sides, because a few-bp stop on BTC is dominated by the round-trip fee. These
   cards were not edited here (Lab_Guy stamps and scope hashes); the suggestion is for whoever takes them.
3. **Flow variable, not book variable.** He says market orders are what move price and never appear in the book; the recent trades list shows them.
   That supports measuring taker flow (CVD, aggTrades) and is consistent with the existing Tom CVD work; no new card.
4. **Size versus depth.** His slippage example is 10 Bitcoin against about a quarter Bitcoin at the touch. Our testnet sizes are far smaller; nothing to change.
   The 10-second habit (spread, limit when patient, size vs depth) is a human checklist, not a testable rule.
5. **Keep the series current.** EP08 was one of the 18 ids MANIFEST.csv had marked HIDDEN_UNAVAILABLE (private until it went public on 2026-10-17). The other
   17 were re-checked on 2026-10-18 and are all still private, so they are probably unreleased episodes. EP09 (order types: market, limit, stop) is next.
   Card `krown-foundations-ep08-follow-through` (SONNET, ready): fold EP08 into the ledger as a new family, re-check the 17 ids weekly, extract EP09 when public.

## Cautions
- Auto-captions (en-orig); fee amounts, prices and the 30 to 40 dollar slippage guess are caption text only. Frames are needed before any fee number is used.
- His legal statements on spoofing in crypto are belief ("I don't believe"); do not use them.
- Single video, so any ledger family from it is PROVISIONAL (PROTOCOL L4) until EP09 and other order-type episodes confirm.
