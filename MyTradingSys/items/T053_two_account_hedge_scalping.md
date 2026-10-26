# T053 - TWO-ACCOUNT HEDGE / LEVERAGED SCALPING RESEARCH

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T048 satellite framework (the "cluster and satellite" idea grew from this ask).

## VERBATIM ASK (operator, earlier; re-stated 2026-09-28)
I need to research on a technique/method for trading/scalping BTC highly leveraged setups. Let us first refine the requirements.
Look for - Two accounts method that uses a hedging technique. Ex - If you are long on BTC perpetual Binance chart at say prince X dollars,
and market moves up in your direction say y dollars is the delta price up.
Then we have these among other possible choices -
a. Short to Hedge after a defined threshold such that exchange fee paid is covered + some profit is covered.
b. b1 - Short to Hedge after a considerable price or market condition is reached for example price outside Bollinger Bands, DVD divergence, etc.
   b2 - Short to create a new position and after a considerable price or market condition is reached for example price outside Bollinger Bands, DVD divergence, etc
In this way the strategy could be quick in quick out or a continuous loop that runs with stops losses and on algorithms.
I know it is risky stuff - but I have ben trading futures for a lot of time and i understand the risks.
Since i am buiklding MTS - MyTradingSystem - I need these future perpetual leveraged positions strategies. I need to know what ppl do in this space that actually works.

## STATE
2026-09-28 OPEN, on fast-track (operator). Nothing researched or built yet; not covered by T048's doc.
Plan: (1) research what practitioners actually do (hedge mode vs two accounts, grid/hedge loops, fee math) with sources;
(2) define a, b1, b2 precisely; (3) backtest on 1m data with Deribit/Binance fees + funding; (4) testnet only.
Note: Deribit supports one position per instrument per account (net), so a true two-sided hedge needs two subaccounts.
2026-10-04 RESEARCH DONE (doc-only, no backtest): research/_archive/loose_2026-10/T053_TWO_ACCOUNT_HEDGE_RESEARCH.md; no validated external evidence for hedge loops; equal-size hedge is delta-neutral so expectancy must come from the unhedge/trigger rule; next = our backtest per D1; 5 questions open for operator.
