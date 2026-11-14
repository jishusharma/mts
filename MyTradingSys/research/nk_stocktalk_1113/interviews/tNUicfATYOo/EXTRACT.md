# tNUicfATYOo — Hilega to Milega Strategy Tested 100 Times (Trader Insights)

Source: English auto-captions from YouTube video `tNUicfATYOo` (Trader Insights, 2023-03-27).
Raw transcript cached in `raw_transcripts_canonical/tNUicfATYOo_raw.txt`.
Third-party backtest of NK's Hilega Milega strategy on Nifty & BankNifty futures across 100 trades.

---

## Strategy setup and indicator rules (Third-party restatement)

> "Many people requested testing this strategy on a 15-minute timeframe on Nifty and BankNifty, so here is the video"
**Source GPS: tNUicfATYOo | BEGIN**
- [00:01:04] Timeframe: 15-minute timeframe used for Nifty and BankNifty testing.

> "We will use Nifty Futures in this setup because we will use VWAP and VWAP requires volume data which is not available in normal Nifty."
**Source GPS: tNUicfATYOo | BEGIN**
- [00:02:00] Instrument filter: Trade on futures (Nifty Futures / Bank Nifty Futures) rather than spot index, because VWAP requires volume data.

> "If you are using Bank Nifty, then select Bank Nifty Futures Index Futures."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:02:21] Instrument selection: Bank Nifty Futures Index Futures for Bank Nifty setup.

> "Now, we will set the timeframe to 15 minutes and add the Hilega Mila Indicator using the link in the description."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:02:30] Chart configuration: 15-minute timeframe with Hilega Milega indicator.

> "After that, we will add VWAP."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:02:38] Indicator overlay: VWAP is added to the chart alongside Hilega Milega.

> "They have mentioned several entry signals such as if the red line and RSI blue zone crossover for buy, or if the blue zone turns red, you can enter"
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:02:57] NK entry signals noted: Red line and RSI blue zone crossover for buy, or blue zone turning red.

> "They said many things, but the entry we will test in this video is when the blue zone turns red and then goes inside the red zone, and the price is above VWAP, it is a strong buy signal"
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:03:05] Tested strong buy entry condition: Blue zone turns red and goes inside the red zone while price is above VWAP.

---

## Buy rules

> "Close price should be above VWAP."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:15] Buy rule 1: Candle close price must be above VWAP.

> "The RSI zone should be a red zone."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:15] Buy rule 2: RSI zone must be in the red zone.

> "Entry will be high of the candle."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:21] Buy entry trigger: Buy order placed at the high of the setup candle.

> "Stop Loss at Previous Swing Low."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:21] Buy stop loss: Stop loss placed at the previous swing low.

> "Target is 1.5 times the risk."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:21] Buy profit target: 1.5R (1.5 times risk).

---

## Sell rules

> "The RSI zone should turn from red to blue, the red line should enter from above the blue zone, and the price should be below VWAP."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:31] Sell setup conditions: RSI zone turns from red to blue, red line enters from above the blue zone, and price is below VWAP.

> "The entry signal will be at the low of the candle. The stop loss will be at the previous swing high, and the target will be 1.5 times the risk."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:42] Sell execution: Entry at candle low, stop loss at previous swing high, target at 1.5 times the risk (1.5R).

---

## Risk management & position sizing

> "While testing, we will keep the maximum risk per trade at 5% because we are using swing low or swing high stop loss, which can lead to extremely high stop loss"
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:05:51] Test risk cap: 5% maximum risk per trade cap to guard against wide swing high/low stops.

> "For beginners, I would still advise not to go more than 2% risk per trade."
**Source GPS: tNUicfATYOo | MIDDLE**
- [00:06:01] Risk rule for beginners: Do not risk more than 2% per trade.

---

## Backtest performance & metrics (100 trades)

> "As you can see, there were a total of 100 trades, out of which 54 were wins and 46 were losses, resulting in a win rate of 54%."
**Source GPS: tNUicfATYOo | END**
- [00:08:16] Sample & win rate: 100 trades, 54 wins, 46 losses -> 54% win rate.

> "The total gain in the account was 106.56%, and the maximum drawdown was -9.94%."
**Source GPS: tNUicfATYOo | END**
- [00:08:24] Returns & drawdown: Account gain 106.56%, maximum drawdown -9.94%.

> "The longest continuous win streak was 5, and the longest continuous losing streak was 6"
**Source GPS: tNUicfATYOo | END**
- [00:08:30] Streaks: Longest winning streak 5 trades; longest losing streak 6 trades.

> "The total duration of the test was 9.237 months."
**Source GPS: tNUicfATYOo | END**
- [00:08:34] Test duration: 9.237 months of market data.
