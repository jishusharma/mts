# Extract: Andrea Cimi, "How to ACTUALLY Make your first $10k Trading" (`3Zs52kfCwiU`)

- **Video ID:** `3Zs52kfCwiU`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, Fabio Valentini's partner)
- **Market in the video:** US stock index (Nasdaq 100, S&P 500), single stocks around earnings; no crypto, no order-flow rules. Mostly a life-and-money roadmap (saving, prop firm vs broker); that part is skipped as marketing and story.
- **Source:** `raw_transcripts_canonical/3Zs52kfCwiU_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Overall data status:** every performance figure below is a speaker claim, no data shown (no trade list, no chart of results, no test period beyond "last 6 years", no costs stated).

## Rules

### O1. Opening range breakout, 30-minute candle (SOURCED)

Rule: phase = intraday drift on a directional day; instrument Nasdaq 100 (index), long only. Entry: take the first 30-minute candle of the session, mark its high and low, and buy as soon as a candle closes above the opening-range high. Stop: below the breakout candle. Target: the speaker is inconsistent in one passage: first "1:0.5" with the take profit at half the stop distance, then a profit "at the same distance with the stop loss" and calls it 1:1. Treat target as unclear (0.5R or 1R). Risk per trade for this ORB: garbled in the caption, NOT reliably stated. Computable from klines (BTC session open is OURS: untested): yes.

> "So, what basically what we do is we just take the first 30-minute candle, we draw out the high, we draw out the low, and we wait." [0:22:48]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

> "As soon as there is a candle that closes above the high of the opening range, we just buy and we either place our stop loss below the candle that breaks out with a 1:0.5 risk to reward ratio." [0:22:58]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

> "And if it goes up, we sell at a profit at the same distance with the stop loss." [0:23:14]
**Source GPS: 3Zs52kfCwiU | END**

> "And this, exactly like the earning surprise, is a long only strategy." [0:23:21]
**Source GPS: 3Zs52kfCwiU | END**

### O2. Opening range breakout, 15-minute version, long and short (SOURCED)

Rule: same idea on the 15-minute opening range, both directions, called a short-term scalp using momentum more than drift. Stop above (short) or below (long) the breakout candle, 1:0.5 risk-to-reward. Reported result: Sharpe 1.84, about 30 percent annual return, 10 percent maximum drawdown, over the last 6 years. Win rate is missing in the caption ("has around win rate"). Which version (30 or 15 minute) the numbers belong to is ambiguous: they are spoken right after the 15-minute description. Speaker claim, no data shown; he says "we've done the analysis" but shows nothing.

> "There's another version of the same strategy that uses the 15-minute opening range instead. And it works both long and short, but it's like a a short-term scalp strategy." [0:23:34]
**Source GPS: 3Zs52kfCwiU | END**

> "You place your stop above the candle that breaks out or below the candle that breaks out 1:0.5 risk to reward." [0:23:42]
**Source GPS: 3Zs52kfCwiU | END**

> "a sharp ratio of 1.84, ladies and gentlemen, with a annual rate of return of around 30% and a maximum drawdown of 10%." [0:24:01]
**Source GPS: 3Zs52kfCwiU | END**

> "Now, this is the performance over the last 6 years." [0:24:09]
**Source GPS: 3Zs52kfCwiU | END**

> "Of course, past performance doesn't mean future performance." [0:24:12]
**Source GPS: 3Zs52kfCwiU | END**

### O3. Post-earnings-announcement drift, 60-day hold (SOURCED)

Rule: after a positive earnings surprise a stock gaps up and then trends for about 60 days; buy and hold 60 days. Reported: win rate about 60 percent, average R 1 to 1.5, profit factor above 2, about 15 percent a year, drawdown below 15 percent, Sharpe above 1, under 100 trades a year. Speaker claim, no data shown. Not computable for BTC (needs earnings events): no.

> "Just buy and don't sell until 60 days. This strategy alone would have a win rate of around 60% with around a 1 to 1.5 average risk reward, a profit factor of more than two, an annual rate of return of around 15% with an average drawdown below 15% with a potential sharp ratio of above one" [0:21:22]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

### O4. Order-flow autocorrelation as the mechanism (SOURCED)

Rule: large institutional parent orders are split into many child orders (a mix of passive and aggressive flow, paced by algorithms), so aggressive buys tend to be followed by more aggressive buys. Testable claim for BTC: the sign of aggressive trades (aggTrades buyer-maker flag) autocorrelates and net aggressor flow over a window predicts the next window's return direction. Computable from aggTrades: yes. No entry, stop or target given. The "vast scientific proof" is not shown.

> "They take these huge orders that we call meta orders and they split it into multiple small orders." [0:17:42]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

> "called order flow auto correlation, which basically means buy orders will lead to more buy orders." [0:19:16]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

### O5. Risk rules the speaker states (SOURCED)

Rule: a hard daily risk budget fixed in advance (a platform risk manager blocks trading beyond it); size per trade set from historical data so a normal drawdown does not burn the account; prop-firm example 0.4 to 0.5 percent risk per trade, later 1 or 2 percent on a funded 150k account. His own mistakes: over-risking, over-sizing, emotional and revenge trading. Percentages are his illustration, not a tested rule (OURS: untested for BTC).

> "you can trade only what you preset your maximum risk for the day is." [0:26:43]
**Source GPS: 3Zs52kfCwiU | END**

> "a lot of the mistakes I've made were mostly because of over-risking, over-sizing, getting emotional about trades, and being revengeful" [0:26:19]
**Source GPS: 3Zs52kfCwiU | END**

> "if on the prop firm I will risk maybe 0.5% per trade, let's say, or 0.4% per trade" [0:28:49]
**Source GPS: 3Zs52kfCwiU | END**

> "Any risk that is calculated to not burn my account based on statistical data, of course." [0:31:41]
**Source GPS: 3Zs52kfCwiU | END**

### O6. Benchmark test for any strategy (SOURCED)

Rule: a strategy is worth trading only if it systematically beats buy-and-hold of the index on a risk-adjusted basis. Benchmark numbers quoted: index Sharpe about 0.5; a diversified portfolio about 0.7 to 0.8. OURS: for BTC the benchmark would be BTC buy-and-hold over the same window.

> "So, a good strategy in finance is anything that systematically outperform buying and holding the American stock market, either the Nasdaq or the S&P 500." [0:10:21]
**Source GPS: 3Zs52kfCwiU | BEGIN**

> "And S&P and Nasdaq, they have around a 0.5 Sharpe ratio." [0:13:39]
**Source GPS: 3Zs52kfCwiU | MIDDLE**

### O7. Retail failure statistic (SOURCED, speaker claim, no data shown)

Rule: none (context number). He states that of 100 traders who put in 5,000 dollars, 90 percent lost it all, 7 percent broke even, under 1 percent were profitable; no source is given.

> "out of 100 traders that put $5,000 into their trading account, 90% of them lost it all." [0:08:29]
**Source GPS: 3Zs52kfCwiU | BEGIN**
