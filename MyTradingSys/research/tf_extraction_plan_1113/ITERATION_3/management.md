# Iteration 3 merge: management

Sources: flash + argon. Rows 31: AGREED 7, SINGLE 22, CONFLICT 2, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 17.
Pattern, ledger and fix columns are assigned by rule from the source rows (code column, numbers, transfer words); the ledger column matches video id plus two shared content words. First-pass labels, not a re-read. Rows paired across models by same video id plus quote or rule word overlap.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| MG-01 | Break-even is fast and event-driven: stop to zero within the first minute or before one candle closes; repeated break-evens are accepted | AGREED | 4 | N | re-code |
| MG-02 | Move to risk-free when order flow confirms same-side adding and strong candle result | SINGLE | 4 | N | re-code |
| MG-03 | Move to BE once a breakout is sustained by fresh liquidity (break-and-protect), even on a small move | SINGLE | NEW | N | test |
| MG-04 | Do not move stop until price reaches a zone where the opposite side is expected | SINGLE | NEW | N | test |
| MG-05 | Trail aggressively behind seller control level once nice floating profit exists and a new low breaks | SINGLE | 4 | N | re-code |
| MG-06 | Trail the stop behind successive aggression and absorption prints on the tape, not a fixed distance | AGREED | 4 | N | re-code |
| MG-07 | Trail behind the last significant volume area or dividing line of liquidity (5-minute chart in one video) | AGREED | 4 | Y L21 | re-code |
| MG-08 | Trail or not: Argon says no trail with a clean planned target; Flash says always trail behind structure | CONFLICT | 3 | N | re-frame |
| MG-09 | Take partials at liquidity clusters or resistance where exhaustion may occur; let the runner ride | AGREED | 2 | N | re-code |
| MG-10 | Take profit early to bring negative day balance back to flat when in loss for the day | SINGLE | 2 | N | extract |
| MG-11 | Partials when well ahead: Argon says hold the full target; Flash says take partials rather than wait for 1:20-1:30 | CONFLICT | 3 | N | re-frame |
| MG-12 | Decide on partial profits by reading momentum at key price level | SINGLE | 2 | N | extract |
| MG-13 | Scale out / trade partial sequences conditioned on ongoing liquidity aggression in book | SINGLE | 2 | N | extract |
| MG-14 | Add in trend direction after first leg is at BE, funded by first trade's profit | SINGLE | 4 | N | re-code |
| MG-15 | Do not add short exposure low in the curve (or long exposure high in the curve) | SINGLE | NEW | N | test |
| MG-16 | Start with small contracts and scale in as session profit builds | AGREED | 4 | N | re-code |
| MG-17 | Add at breakout only if price maintains steady upward speed | SINGLE | 2 | N | extract |
| MG-18 | Add on liquidity push and simultaneously tighten stop above last major trades | SINGLE | 4 | N | re-code |
| MG-19 | Targets are named levels: opposite extreme of the curve, session value-area high, past high-volume levels | AGREED | 4 | N | extract |
| MG-20 | Extend target from 1:2 to 1:5 while moving stop to BE after level break | SINGLE | 2 | N | extract |
| MG-21 | Adjust profit target dynamically as VWAP moves | SINGLE | 2 | N | extract |
| MG-22 | Cut or exit early when price is accepted back against the trade or the auction fails to confirm | AGREED | 2 | N | re-code |
| MG-23 | Exit / tighten aggressively if final attempt at target stalls | SINGLE | 2 | N | extract |
| MG-24 | Re-enter after a stop-out when price/order flow sets up again | SINGLE | NEW | N | test |
| MG-25 | Never allow a large open floating profit (e.g. 20k) to retrace all the way to breakeven; treat giveback as a real loss. | SINGLE | 2 | N | extract |
| MG-26 | On squeeze trades, trail stop loss immediately as price pushes into the liquidation zone to lock in gains. | SINGLE | NEW | N | test |
| MG-27 | Widening target distance reduces win probability; better to take realistic targets at key auction levels. | SINGLE | 2 | N | extract |
| MG-28 | Manage positions using multi-stage targets: structural level for position close vs larger session-wide movement. | SINGLE | 2 | N | extract |
| MG-29 | At target, choose between full exit or trailing the stop-loss if further expansion journey is probable. | SINGLE | 2 | N | extract |
| MG-30 | When price is at all-time highs without prior volume profile levels, mirror the prior momentum swing distance to project target. | SINGLE | 2 | N | extract |
| MG-31 | When trading two lots, take one lot off as partial profit when performing well and move stop loss up (trail) on the remainder. | SINGLE | 2 | N | extract |

## Evidence

#### MG-01 AGREED
> "We mark the level from before we know exactly where there is the high probability of rejecting and we have time To go stop losing at zero so fast not even one candle"
**Source GPS: Is1HvdfQm5c | MIDDLE**

#### MG-02 SINGLE
> "the information for me that I can put my position at risk-free comes immediately 3 minutes after when the market is telling me, Look at that. They are adding short position."
**Source GPS: Pz8f0wWW12M | END**

#### MG-06 AGREED
> "You can trail your position following the aggression of the market. So, this one print a new one, you bring your stop loss here and you continue"
**Source GPS: Pz8f0wWW12M | END**

#### MG-07 AGREED
> "Look, now I'll show you again how to trail your stop-loss. What do I do now? I see here that the last time there was significant trading volume on the 5-minut chart was at 603. And if it drops below that, things will break down, of course."
**Source GPS: 4MoNjEQ2Dd8 | END**

#### MG-08 CONFLICT
- Flash claims: Always trail stops behind validated structural test levels to protect capital (Is1HvdfQm5c, Fabio, ASR).
- Argon claims: Tom does not trail a trade with a clean about 6:1 plan; moving the stop up early turns a high-RR trade into 1:1 (k0zm5NYn0IQ, UOBgXV20yCM).
- Check that settles it: Speaker split, not a fact error: Argon rows are Tom, Flash row is Fabio on ASR text. Settle by listing every trail line per trader (per-trade choice per iteration 2 Q6); the lead or a third reader checks k0zm5NYn0IQ and Is1HvdfQm5c at the quoted spots.
> "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that because I just see that the overall position with a riskreward ratio of about 6 to1 is simply so good that I don't worry about it."
**Source GPS: k0zm5NYn0IQ | BEGIN**
> "You might move your stop up price range here. And the market makes a quick reversal. And all of a sudden, your risk-reward ratio is only at one."
**Source GPS: UOBgXV20yCM | END**
> "where did you got stopped out you trail your stop I want to help you"
**Source GPS: Is1HvdfQm5c | END**

#### MG-09 AGREED
> "And these are all partial profit that you can take, because the market usually reach a point of exhaustion here when there are there is a cluster of liquidity level, and then reverts."
**Source GPS: FawPrRUGNpk | MIDDLE**

#### MG-11 CONFLICT
- Flash claims: Take partial profits as the trade runs into expansion rather than waiting for 1:20-1:30 targets to retrace to zero (DyS79Eb92Ug).
- Argon claims: Hold for the full target rather than conservative partials when already well up on the day (8CWKfoSJu3c).
- Check that settles it: Third read of both passages for the P&L state at that moment; likely a day-P&L-keyed rule (up on the day vs flat), which neither model states.
> "considering that we have $27,000 profit plus $12,000 profit floating for the day. Doesn't make sense to be super conservative on the profit taking."
**Source GPS: 8CWKfoSJu3c | MIDDLE**
> "And when it's personal account and when you are giving back to the market 40 50,000 trust me that you start to take partials."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### MG-16 AGREED
> "I will scale in with small contracts and as we build profit even if we are already 11,000 in profit"
**Source GPS: DyS79Eb92Ug | BEGIN**

#### MG-19 AGREED
> "the total riskto-reward to get to the low of the curve is like 1 to 16 1 to 19 on the final target."
**Source GPS: 8CWKfoSJu3c | MIDDLE**

#### MG-20 SINGLE
> "if you decide to enter here like this with a target here, okay, you can decide to go from 1 to 2 to 1 to 5 and put your stop loss to break even."
**Source GPS: Pz8f0wWW12M | END**

#### MG-22 AGREED
> "to see if there is a reaction here at yesterday's value high or if we re-enter the range, whether the market finds acceptance there. And then I would also exit the corresponding trade."
**Source GPS: k0zm5NYn0IQ | END**

#### MG-25 SINGLE
> "Okay, I have my break even here and someone says I'm already break even. I don't care. And no, it's not like this because you are willing to sacrifice 20,000 on the down."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### MG-26 SINGLE
> "We are trying to make 3,000, risking, 1560. And as soon as we go high trail stop- loss and get back inside. Why? Because this level is creating a liquidation."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### MG-31 SINGLE
> "Or if the trade is performing well, take your profit and move your stop loss further up. >> Ah, okay. Then you trail the stop. Okay. >> Well, trail take profit or you can if you're really in with two units, so with two lots. >> Mhm. >> Uh already take one out."
**Source GPS: 5Ljfwvtktek | BEGIN**
