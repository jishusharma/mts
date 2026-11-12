# Extraction: Open Handling, Day Filters, Exhausted Open, and Cash vs 24h Profile (tf-y3-open-dayfilter-exhaust-1113)

Source: `raw_transcripts_canonical/<id>_raw.txt` for `Of_wlv3xaZo`, `Fj4FDZQxw0I`, `Ld1dhjGdTCA`, `DyS79Eb92Ug`, `43JaKHRvxHk`, `9VN9y2DVtGQ`, `LQvv5xgy_ik`, `jasv3L-d8ZE`, `Khgj5q1-ln8`, `C9n_d91Uitc`, `k0zm5NYn0IQ`, `UOBgXV20yCM`, `96iPFDpXEcU`, `0KyIEdvVKMQ`.
Every quote is spoken text only (no video descriptions), verified by `scripts/dev/verify_extract_quotes.py`.

---

### Q21 First 30 minutes and open type

**Verdict: ANSWER** (qualitative open-type rule; numeric open-range size threshold is NOT_SEEN). Both Tom and Fabio wait out the first 30 minutes of the New York session (15:30–16:00 CET) before trading, then classify the day from the opening range size: a narrow/small opening range indicates balanced positioning and a higher probability of a trend day, while a very large/explosive opening range indicates imbalance where large participants could not execute calmly and price is likely to revert or fail to hold.

> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE** (Tom)

> "If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. Why? Everyone was able to take their positions and is now moving business to the next levels where they think it looks good."
**Source GPS: Of_wlv3xaZo | BEGIN** (Tom)

> "If the market starts explosively right away like here, you often get a counter up here because the market will try to find fair prices, which are usually found back near the opening range since many large participants couldn't even do their business yet."
**Source GPS: Of_wlv3xaZo | BEGIN** (Tom)

> "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will."
**Source GPS: Fj4FDZQxw0I | END** (Tom)

> "Is the market opening range very large? Or is it very small? And think about it, if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend."
**Source GPS: Ld1dhjGdTCA | END** (Tom)

> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN** `[4:14]` (Fabio)

> "On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END** `[31:42]` (Fabio)

---

### Q22 Day filters (news, gap, choppy, bias, volatility)

**Verdict: PARTIAL** (filters and directional rules are stated; exact numeric thresholds for gap size, news buffer minutes, and choppy-day ATR/range are NOT_SEEN, except VIX > 20). Tom skips days with groundbreaking overnight gaps or major scheduled news releases (e.g. GDP, central bank, inflation), stays out when the opening contradicts the planned day type, and notes large investors stay out or hedge when the volatility index exceeds 20. Fabio skips counter-trend setups against his profile-framing daily bias, skips trades outside session timing, locks out a side for the day if a key level breaks, and identifies days where every move is absorbed in the first two hours as unsuitable for trend following.

> "The first thing I look at in the morning is what news is coming out today. The second thing is will I even trade today or have such groundbreaking things happened overnight that brings us to the gap so I'd better stay on the sidelines for now."
**Source GPS: Ld1dhjGdTCA | BEGIN** (Tom)

> "during this time as a day trader, I shouldn't necessarily have positions open because when the GDP is released and there's a deviation, the higher it is than the forecast, it leads to major movements."
**Source GPS: Ld1dhjGdTCA | MIDDLE** (Tom)

> "And if you put that into context and you're planning a balanced day, for example, but you see at the market opening everything is different, your result can be many times better because you know exactly now I'd better stay out of the trading day."
**Source GPS: Ld1dhjGdTCA | END** (Tom)

> "large institutionals generally assume increased volatility for anything over 20 and increased risk assessment and many of the large investors stay out in such market phases or engage in hedging operations to simply protect their large portfolios."
**Source GPS: C9n_d91Uitc | BEGIN** (Tom)

> "Every movement got absorbed in the first two hours. This is the worst market condition you can get for my strategy."
**Source GPS: jasv3L-d8ZE | BEGIN** `[0:13]` (Fabio)

> "So, all the short setup if I have a bias, I'm not interested into taking, okay? So, I can save the counter trend setups."
**Source GPS: Khgj5q1-ln8 | MIDDLE** `[7:13]` (Fabio)

> "Unfortunately, when they are outside the timing or counter trend in respect to the bias, we don't take it."
**Source GPS: Khgj5q1-ln8 | END** `[11:22]` (Fabio)

> "If this area gets broken, I don't want to be long for the day. So it will be really with a big probability a consolidation day."
**Source GPS: DyS79Eb92Ug | BEGIN** `[8:31]` (Fabio)

> "you know that London session is not worth to trade for me. My profit factor is really low."
**Source GPS: 0KyIEdvVKMQ | END** (Fabio)

---

### Q23 Exhausted open signs

**Verdict: ANSWER** (qualitative order-flow signs; numeric volume/delta thresholds are NOT_SEEN). Tom identifies an exhausted open suitable for a counter-trade when an extreme opening expansion / large initial balance occurs without real volume or liquidity, driven by forced "I have to buy / push" hedging flow, followed by a finished (completed) auction at the top and absorption with no further momentum.

> "And at the top you can simply see that nothing was happening anymore. And we also had a finished auction. That means the market formed a completed auction at the top."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)

> "In my opinion, the market open was too extreme. And above all, it wasn't accompanied by real volume, but rather there was an I have to push sentiment."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)

> "Very little liquidity down here. That means there was an I have to buy sentiment in the market. So they had to go long."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)

> "because the initial balance is so large meaning the expansion of the trading opening is just very very big and that means here traders had to buy at the market open at that point they don't really care what the price is because these are hedging transactions and they will certainly be corrected later"
**Source GPS: k0zm5NYn0IQ | MIDDLE** (Tom)

> "There were large volumes up here. Yes, but why didn't the market keep rising then? Because there was no more momentum. Absorption took place. And all of a sudden the market participants were able to show very clearly in the order book funds over."
**Source GPS: 9VN9y2DVtGQ | END** (Tom)

---

### Q24 24h versus cash-session profile reason

**Verdict: ANSWER**. Tom states that referring to 24-hour profiles when trading only the cash session is inherently meaningless because almost all volume (e.g., 6 million vs 6.5 million contracts) trades in the cash session, so including thin overnight/after-hours volume shifts the calculated value area and equilibrium to price levels where big players never transacted, and can even flip a balance profile into an apparent trend profile. Similarly, cash-session closing gaps (around 22:00 CET) matter because ETFs execute in the closing auction, whereas midnight closes have no institutional liquidity.

> "You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
**Source GPS: Of_wlv3xaZo | END** (Tom)

> "In this specific cash session, we saw approximately 6 million contracts being traded. When we look at the entire period, including the after-hours trading session combined with the cash session, the total volume reaches 6.5 million contracts. Now, observe how the value area shifts significantly along with the equilibrium point, the value area low, and the value area high."
**Source GPS: Of_wlv3xaZo | END** (Tom)

> "you're referring to value areas that have a mathematical calculation based on 24-hour volume, but where far too little volume has occurred for you to have a meaningful relationship to the actual main trading volume."
**Source GPS: Of_wlv3xaZo | END** (Tom)

> "when you trade cash time frames, please also use the cash session profiles because they can change. You can have a trend profile in the 24-hour chart, and in the cash session the day before you suddenly have a balance profile."
**Source GPS: Of_wlv3xaZo | END** (Tom)

> "if you examine the gaps only from the cash session, so 10:00 p.m. and a bit, then you'll see that this close is much much more important than for example, a gap close from midnight. Nobody cares about that because there was no liquidity at all because what happens at the end of the cash session? All the ETFs have to enter their positioning in closing auction"
**Source GPS: Of_wlv3xaZo | END** (Tom)

---

## Summary Table

| parameter | trader's value | SOURCED or NOT_SEEN | id |
|---|---|---|---|
| NY open skip / observation window | first 30 minutes (15:30–16:00 CET) | SOURCED | Of_wlv3xaZo, DyS79Eb92Ug, LQvv5xgy_ik |
| Open range size threshold (large vs small) | qualitative only ("very large" vs "very small" / "narrow") | NOT_SEEN | Of_wlv3xaZo, Fj4FDZQxw0I, Ld1dhjGdTCA |
| Volatility index regime filter | VIX > 20 (large investors stay out or hedge) | SOURCED | C9n_d91Uitc |
| Choppy / absorbed day observation window | first two hours absorbed = worst condition for trend following | SOURCED | jasv3L-d8ZE |
| News skip buffer (minutes before/after) | stay flat during major release (e.g. GDP); exact minutes unstated | NOT_SEEN | Ld1dhjGdTCA |
| Gap skip threshold (points / %) | "groundbreaking" overnight gap -> stay on sidelines; exact size unstated | NOT_SEEN | Ld1dhjGdTCA |
| Bias-only filter | skip counter-trend setups against daily bias and outside timing | SOURCED | Khgj5q1-ln8 |
| Day-side lock rule | if key VAL/POC area breaks, no longer long for the day | SOURCED | DyS79Eb92Ug |
| Exhausted open signs | extreme open, no real volume, forced hedging/buy sentiment, finished auction, absorption | SOURCED | k0zm5NYn0IQ, 9VN9y2DVtGQ |
| Exhausted open volume/delta threshold | qualitative only; no numeric threshold | NOT_SEEN | k0zm5NYn0IQ |
| Cash session hours (US, CET) | 15:30 to 22:00+ CET; use cash-session profile, not 24h | SOURCED | Of_wlv3xaZo |
