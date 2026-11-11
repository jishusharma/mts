# Extract: How to Backtest a Trading Strategy (Step-by-Step Guide) (`K31xH-6g9Vc`)

- **Video ID:** `K31xH-6g9Vc`
- **Title:** How to Backtest a Trading Strategy (Step-by-Step Guide) | The Long & The Short Ep. 12
- **Channel:** In The Money by Zerodha (host Sandeep Rao); analyst tag `LongShort` (DECISION OURS, card extract-backtest-howto-K31xH-6g9Vc-1112)
- **Published:** 2025-11-26; duration 21:03
- **Source:** `raw_transcripts_canonical/K31xH-6g9Vc_raw.txt` (yt_dlp auto captions, fetched 2026-11-11T20:42Z by `fetch_captions_timed.py --analyst LongShort`)
- **Instrument context:** Nifty spot and MCX GoldM continuous futures on TradingView; nothing in the video is BTC-specific
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Taught steps

### S1. Five-step process (SOURCED)

Rule: hypothesis, method/indicator, code it, run it, then analyse the trade log; the last step is called the most important.

> "Now, backtesting involves five key steps. First is hypothesis selection or creation, which means defining the specific strategy or idea you want to test."
**Source GPS: K31xH-6g9Vc | BEGIN**

> "And finally, the fifth and the most important step is to download and analyze the trade logs"
**Source GPS: K31xH-6g9Vc | BEGIN**

### S2. Narrow the hypothesis (SOURCED)

Rule: make the hypothesis specific, e.g. long-only trend following, ignoring short signals.

> "You can make it more specific by saying long only trend following strategy on Nifty."
**Source GPS: K31xH-6g9Vc | BEGIN**

### S3. LLM writes the strategy code (SOURCED)

Rule: an LLM (Claude) writes the Pine Script; the defaults it picks are accepted at first.

> "The third step is to code the strategy in Pine Script, a step where we will use Claude AI to write the strategy code."
**Source GPS: K31xH-6g9Vc | BEGIN**

### S4. Fills on bar close, fixed size (SOURCED)

Rule: set a fixed order size and register trades on bar close only.

> "you would have to click on bar close, which means the trade would get registered only if or on bar close."
**Source GPS: K31xH-6g9Vc | BEGIN**

### S5. Compare with buy and hold; split long vs short (SOURCED)

Rule: equity curve against buy-and-hold, drawdown, then long and short contribution separately; a weak side can be dropped.

> "So, long has made around 111%, and the short has contributed just about 7% from this particular strategy. So, you could actually let go of short"
**Source GPS: K31xH-6g9Vc | MIDDLE**

### S6. Sanity-check the trade log against the chart first (SOURCED)

Rule: before any metric, print the latest trades and match entries/exits against the chart; a wrong log wastes all later analysis.

> "we could go back to the chart and compare and check if the entries and exits are matching with what we see in the log. Because if this is wrong, then all further analysis is obviously going to go waste."
**Source GPS: K31xH-6g9Vc | MIDDLE**

### S7. A fixed metric list computed from the log, not the platform report (SOURCED)

Rule: the host keeps his own fixed set of metrics (19) and computes them from the exported trade log every time.

> "I have a set of metrics that I always want Claude to calculate for me."
**Source GPS: K31xH-6g9Vc | MIDDLE**

### S8. Year-by-month P&L table (SOURCED)

Rule: tabulate points by year and month to see bad and good years.

> "Can you make a year and month-wise table in points with the total column for each year?"
**Source GPS: K31xH-6g9Vc | MIDDLE**

### S9. Back-adjust continuous futures before testing (SOURCED)

Rule: stitched futures jump at rollover; use proportional back adjustment (next/current price ratio applied to all earlier prices) before running.

> "To solve this, TradingView follows a proportional back adjustment process, that is, divides the next month futures price by the current month futures price and multiplies that factor to all the previous months."
**Source GPS: K31xH-6g9Vc | END**

### S10. Parameter play by best return (SOURCED; flagged as a risk, see GAP_TABLE)

Rule (as taught): change the parameter and the long/short mode and keep what gives the better return.

> "So, you can kind of play around with the settings and see which one gives you a better return."
**Source GPS: K31xH-6g9Vc | END**

### S11. Stated limits: one symbol, no in-sample/out-of-sample, no walk-forward (SOURCED)

Rule: the platform cannot test a portfolio and has no IS/OOS split or walk-forward; the workaround is to export separate periods.

> "there are no features for segregating the data as in-sample and out-sample, or even stuff like walk-forward analysis, etc. Though this can be taken care of by selecting different time periods while backtesting and downloading the data separately as two different data sets"
**Source GPS: K31xH-6g9Vc | END**

### S12. A backtest is not a guarantee (SOURCED)

> "But remember, just backtesting by itself does not guarantee success. For all you know, the blind monkey may still win."
**Source GPS: K31xH-6g9Vc | END**

## Not in the video (OURS, checked by reading the whole transcript)
- No fees, slippage or spread are set anywhere in the demo (only currency, order size, bar close).
- No placebo / random-entry baseline beyond buy-and-hold; no multiple-testing correction for the parameter play in S10.
- No regime split, no minimum trade count, no pre-registration.
