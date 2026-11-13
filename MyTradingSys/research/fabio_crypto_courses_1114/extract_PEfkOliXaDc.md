# Extract: Fabio Valentini and Andrea Cimi, "Deepdom Launch Week - Session 1 w/ Fabervaale ENG" (`PEfkOliXaDc`)

- **Video ID:** `PEfkOliXaDc`
- **Speaker:** Fabio Valentini (Fabervaale), with Andrea Cimi hosting (DeepCharts live session, mostly Q&A and product talk; the caption says "session number two" while the title says Session 1)
- **Market in the video:** CME Nasdaq (NQ) and S&P 500 (ES) futures, DeepCharts profile framing, IVB, Commitment of Traders report and option flow; no crypto. Session clocks (New York cash open) do not transfer; profile/IVB logic may.
- **Source:** `raw_transcripts_canonical/PEfkOliXaDc_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. Every number he reports is a speaker claim, no data shown, unless stated otherwise. Most of the video is product talk, COT-report commentary and Q&A; no setup is walked through trade by trade.

## Rules

### P1. Three confirmations before an intraday directional trade (SOURCED)

Rule: do not enter blindly. Directional intraday trade needs (1) fundamentals (COT report), (2) profile framing (where the previous cash-session profile, POC and profile low sit and whether price accepts or rejects them), (3) the IVB confirming in the same direction in the first minutes of the cash session. Entry bar, stop and target: NOT stated. BTC has no COT/cash-session equivalent on Binance data; layers (2) and (3) are computable from klines/aggTrades (daily profile, opening range), layer (1) is not.

> "Now, do I enter blindly? No. When I have the profile aligned with fundamentals, I engage with the IVB. So, I wait for the first minutes of the cash session to get aggressive on the downside, okay? And then I engage in direction of it." [0:05:06]
**Source GPS: PEfkOliXaDc | BEGIN**

> "I need to have three confirmation. The first one is fundamentals. The second one is the profile framing. The third one is the confirmation from the IVB, okay?" [0:05:22]
**Source GPS: PEfkOliXaDc | BEGIN**

### P2. Profile acceptance outside the prior range flips the bias (SOURCED)

Rule: bias stays with the prior direction until a cash session closes beyond a key profile level; a close of the profile below the previous range (profile low plus POC area) is what he calls acceptance and the start of a distribution phase. Example level: 28,600 on Nasdaq, bullish "till proven wrong" unless a cash-session close (not the London session) is below it. Cash-session close wording: for BTC the session boundary is OURS (e.g. UTC day).

> "if I don't see a cash session, a cash session not a London, closing below the 28,600, my direction remain bullish till proven wrong." [0:03:30]
**Source GPS: PEfkOliXaDc | BEGIN**

> "So, we have on the 28,550 two sensitive area. We have the profile low. We have the POC, the maximum point of control, and we have the last switch up here, okay? The data is starting to shift on the downside. When we have an acceptance of this, this is what I call a distribution phase." [0:04:41]
**Source GPS: PEfkOliXaDc | BEGIN**

### P3. IVB window: 30 minutes beats 15 and 60 (SOURCED)

Rule: the IVB range is set on the first 30 minutes (default setting was 60); he engages for direction once the first 30 minutes are confirmed. Reasons: statistical validation says 30 is better, results are more stable (lower variance), the 15-minute range breaks both sides more often and gets chopped. Speaker claim, no data shown: the 30-minute range has multiple breakouts in 16 percent of sessions, 15-minute has three or four per session. Entry beyond the range, stop and target: NOT stated.

> "And from statistical validation it's always better on the 30." [0:17:49]
**Source GPS: PEfkOliXaDc | MIDDLE**

> "when you have the first 30 minutes confirmed This is when I usually engage from a directional point of view." [0:18:21]
**Source GPS: PEfkOliXaDc | MIDDLE**

> "The 15 minutes can do three, four multiple break breakouts per session. The 30 minutes it's not so common. It's 16% of the session that does multiple breakout, but usually it's way more reliable." [0:23:33]
**Source GPS: PEfkOliXaDc | END**

### P4. IVB high-probability area filter built on imbalance: sellers aggress, no result (SOURCED)

Rule: the IVB tool includes a filter for high-probability areas based on imbalance: the best setups appear when aggression by one side (sellers in his example) fails to produce a result at the best imbalance in the area, which is the absorption idea. Exact imbalance ratio, entry, stop, target: NOT stated.

> "It's a filter for the high probability area that is based on the imbalance, no? Because when you see the aggression of the sellers not having results on the best uh imbalance on the area, usually you have the the best setups." [0:19:12]
**Source GPS: PEfkOliXaDc | MIDDLE**

### P5. Opening absorption at the bottom of the weekly area, then IVB confirmation (SOURCED)

Rule: accumulation area from the prior week, huge absorption at its bottom during the open, then the IVB (plus his Nasdaq-effort model) confirms upward; with profile and fundamentals unchanged he wants a revisit of the discount area to take a long, not to continue short. Order of events is the rule; no thresholds, stop or target stated.

> "We had a huge amount of absorption at the bottom side of this one. And then the market start to give confirmation from the IVB and Nasdaq effort on the upside." [0:06:51]
**Source GPS: PEfkOliXaDc | BEGIN**

> "Not to continue short, but to take a long from discount area if the fundamental situation and the profile framing don't change, okay?" [0:07:05]
**Source GPS: PEfkOliXaDc | BEGIN**

### P6. No trade before the New York open; frame the day first (SOURCED)

Rule: no pre-open setups; he waits for the New York session open to frame the day's likely direction, and is adding option-flow confirmation (gamma regime, sensitive levels) when IVB is directional. Session rule only; BTC has no fixed open (OURS: UTC 13:30 equity-open or none).

> "Today I don't have any setups because I always wait for the opening of the New York session to frame the the potential direction of the day." [0:07:12]
**Source GPS: PEfkOliXaDc | BEGIN**

### P7. Session persistence as probability booster (SOURCED, example number only)

Rule: his quant is building a "bias persistence" study: after a session closes above value, how likely is the next session also above value. He stacks layers when they agree: session persistence, fundamentals and an IVB break in one direction. The 65 to 70 percent is given as an example of the kind of number, not a measured result (speaker claim, no data shown). Computable on BTC: yes (daily close vs prior value area, conditional hit rate).

> "if you have, for example, session persistence with a 65-70% probability of continuing lower, shifting on the downside, fundamentals on the downside, and IVB breaks on the downside, you have four layer of information paired." [0:15:31]
**Source GPS: PEfkOliXaDc | MIDDLE**

### P8. Target ideas on a confirmed IVB day (SOURCED, thin)

Rule: after the first 30 minutes are confirmed he points at a projection of the range and the "extended average" far above as where price can go; on the Friday example he says the extended average was reached live. What "projection" and "extended average" are is NOT defined here (caption may be garbled: "protection"). Treat as unknown target, OURS: test range-extension multiples.

> "Okay? So, now you will see above look how much was far the protection and there was also the extended average way above." [0:18:31]
**Source GPS: PEfkOliXaDc | MIDDLE**
