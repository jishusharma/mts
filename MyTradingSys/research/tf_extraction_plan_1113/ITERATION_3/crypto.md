# Iteration 3 merge: crypto

Sources: flash only. Rows 23: AGREED 0, SINGLE 23, CONFLICT 0, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 12.
Only one model ran this topic, so no row can be AGREED; every row is SINGLE. Pattern, ledger and fix columns are assigned by rule from the source row (code column, numbers, transfer words) and the ledger column matches video id plus two shared content words; both are first-pass labels, not a re-read.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| CY-01 | Does not use order flow on Bitcoin; uses on-chain analysis instead (ASR note: "order from" = order flow). | SINGLE | 2 | N | extract |
| CY-02 | Directly contradicts Is1HvdfQm5c: trades crypto order flow on Saturdays when bored. | SINGLE | 5 | N | re-frame |
| CY-03 | Market is open every day including crypto, so do not force 5-25 trades per day. | SINGLE | 5 | N | re-frame |
| CY-04 | Leveraged crypto suffers slippage and missed fills on news shocks (e.g., tariff tweets). | SINGLE | NEW | N | test |
| CY-05 | Built starting capital in crypto; trades leveraged bull runs aligned with crypto halving cycles. | SINGLE | NEW | N | test |
| CY-06 | After FTX collapse, never keep crypto capital on a single exchange/broker. | SINGLE | 4 | N | re-code |
| CY-07 | Use on-chain MVRV Z-score (and miner constraints in LQvv5xgy_ik [32:40]) to size long-term BTC accumulation dynamically instead of static buy-and-hold. | SINGLE | 2 | N | extract |
| CY-08 | Unlike equities, BTC has no cash-flow valuation anchor; cycles are purely behavioral/reflexive. | SINGLE | 2 | N | extract |
| CY-09 | Weekend and off-hour crypto order books have shallow liquidity and fewer participants, amplifying liquidation cascades. | SINGLE | 5 | N | re-frame |
| CY-10 | Monitor perpetual futures funding rate as a crowding/cascade gauge; funding settles every 1h, 4h, or 8h depending on venue. | SINGLE | NEW | N | test |
| CY-11 | Expect 2-3 major liquidation cascades per year in BTC/crypto; BTC drops amplify ~5x on illiquid altcoins (e.g., Oct 10, 2025: 14% BTC -> 70-80% alts). | SINGLE | NEW | N | test |
| CY-12 | Do not trust large resting walls on crypto order books (e.g., 1,000 BTC at $80k) because spoofing is not illegal in crypto. | SINGLE | 2 | N | extract |
| CY-13 | Crypto spot/exchange volume can be faked via wash trading; cross-check against a composite index or CME Bitcoin futures. | SINGLE | 2 | N | extract |
| CY-14 | Crypto daily candles always close at 00:00 UTC (8 p.m. ET). | SINGLE | 5 | N | re-frame |
| CY-15 | Use the Daily timeframe as the primary anchor for crypto, versus Weekly for equities. | SINGLE | 2 | N | extract |
| CY-16 | Equities trade 6.5h/day; crypto trades 24/7 with daily candle reset at 00:00 UTC. | SINGLE | 5 | N | re-frame |
| CY-17 | Real institutional trading occurs on ~21-22 weekdays/month; weekend BTC action is mostly low-relevance drift. | SINGLE | 5 | N | re-frame |
| CY-18 | Watch the 200-week SMA (~4 years of price) as BTC's primary historical macro support/cycle line. | SINGLE | 2 | N | extract |
| CY-19 | High volatility on BTC is >85%; markets compress ~70% of the time and break out ~30%. | SINGLE | 2 | N | extract |
| CY-20 | Watch Bitcoin first as a leading liquidity/risk-on barometer for indices (DAX, S&P, Nikkei). | SINGLE | 2 | N | extract |
| CY-21 | Reads BTC market/volume profile shape (e.g., B-structure in 0CrkbfuIhkc) and equilibrium by eye without needing futures data. | SINGLE | 5 | N | re-frame |
| CY-22 | Cross-exchange arbitrage and order-flow front-running work in crypto because exchanges are fragmented and unregulated. | SINGLE | 2 | N | extract |
| CY-23 | Size conservatively because BTC can move 10-15% rapidly. | SINGLE | 2 | N | extract |

## Evidence

#### CY-03 SINGLE
> "you have time the market is open every day if we include crypto every day of the week why are you running why are you trying to take five seven ten twenty five trades per day"
**Source GPS: Is1HvdfQm5c | BEGIN**

#### CY-05 SINGLE
> "I also trade on crypto. You can imagine with leverage what you can do with crypto like I managed to take one single bull run on leverage"
**Source GPS: DyS79Eb92Ug | MIDDLE**

#### CY-06 SINGLE
> "I was ranking in the leaderboard of FTX, I was an extremely active crypto scalper, and in this case, FTX decided to shut down everything"
**Source GPS: LQvv5xgy_ik | END**

#### CY-07 SINGLE
> "The blockchain intelligence model use the market value to realize value, the MVRV zeta score to identify macro market cycles and adjust allocation size dynamically"
**Source GPS: StaphlRH8NQ | END**

#### CY-10 SINGLE
> "So there's two free numbers that you can reference gauge number one is gonna be the funding rate so perpetual futures Which is crypto's like best and most favorite product of course have no expiration"
**Source GPS: P3rDSh187TE | BEGIN**

#### CY-11 SINGLE
> "realistically in crypto or should I say Bitcoin, especially altcoins, you see two to three of these events per year, typically"
**Source GPS: P3rDSh187TE | BEGIN**

#### CY-14 SINGLE
> "remember daily timeframes always close at zero zero UTC. No matter where you are in the world, it is zero zero UTC. So if you are in Eastern time zone, that's gonna be 8 p.m."
**Source GPS: _t_XIBrcjRk | BEGIN**

#### CY-16 SINGLE
> "It's only going for six and a half hours per day But when it comes to crypto or 24 seven markets, yeah, or even 20 24 or five markets Yeah, just you know weekdays. Yeah zero zero UTC is usually the going rate"
**Source GPS: 8MvxK_nxO-0 | BEGIN**

#### CY-17 SINGLE
> "you get about 21 to 22 days per month of real trading. And yes, Bitcoin does trade over the weekends, as do a lot of things nowadays. But what happens over the weekend? Not all that much realistically."
**Source GPS: -NXzJs5JRks | BEGIN**

#### CY-18 SINGLE
> "This 200 simple on the weekly, which is basically four years of price in one line, that's Bitcoin's one of its most favorite indicators, in fact, or one of its most favorite moving averages, historically speaking."
**Source GPS: -NXzJs5JRks | MIDDLE**

#### CY-19 SINGLE
> "markets are compressing for about 70% of the time and they're breaking out for 30% of the time."
**Source GPS: kcMnnQr1VFg | MIDDLE**

#### CY-23 SINGLE
> "Because something as highly volatile as Bitcoin can move 10 or 15% in no time at all."
**Source GPS: DVZVE9rXGtU | MIDDLE**
