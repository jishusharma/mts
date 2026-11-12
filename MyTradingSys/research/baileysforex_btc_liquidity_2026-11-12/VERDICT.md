# Verdict: Baileysforex "Backtesting Bitcoin | Easy Liquidity Strategy" (D-0xTsMPwys)

Card baileysforex-btc-liquidity-extract-1112. Analyst statements are context, never signals. Label: SOURCED (video quote) / OURS.
Extract check: `verify_extract_quotes.py extract_D-0xTsMPwys.md` exits 0 (12 quotes OK). The canonical file raw_transcripts_canonical/D-0xTsMPwys_raw.txt was missing in this
tree (folder is gitignored, local only); DECISION (OURS): rebuilt it as a copy of the committed D-0xTsMPwys_timed.txt (same header and text), then ran the check.

## Mechanics checked against the transcript
| Part | In the video | Exact or discretion |
|---|---|---|
| Daily bias | "price was very clearly bullish so we're looking for buys only" (SOURCED) | Discretion: "clearly bullish" is a look at the chart; no indicator, no number. |
| 1h liquidity sweep | "took out this area to the left we grabbed these lows price then flipped back bullish on the 1 hour" (SOURCED) | Partly exact (low taken, then back up). Which low counts (pivot size, how old) is by eye. |
| 15m BOS + demand | "grab of those two lows ... 15 minute then actually flipped bullish ... another breaker structure"; "demand there so if we can get a retest" (SOURCED) | Discretion: structure points and the demand box are drawn by hand. Entry also uses the 5m ("I'm using the five minute for entries"), which the extract omits. |
| Reward to risk | "stops cover in the low ... mechanically Target a one to three" (SOURCED); he also says he targets "between 1 to 3 and 1 to four" and sometimes the next liquidity high | Exact for 1:3. Target is not always 1:3 in the video (first trade "Target this High", ran 3.66). |
| Stop buffer | none; stop under the low, and one trade was "tagged ... by a pip" then hit target | No buffer stated. The extract's 0.1-0.2 ATR / 10-20 bp is OURS, not the video. |
| Sample | 3 trades, 2 wins, +5.7 % in January 2024 | Anecdote (n 3), not evidence. The video also says several setups were skipped (gap up, no structure, zone missed). |
| Shorts | Takes sells in the video after a 1h trend shift and a supply zone | Rule is two-sided in practice; extract only lists longs. |
| Extract defects | Trade log 3.2 gives +3.8 % / +2.9 % per trade and "Trade 3: hit overhead swing high"; the transcript has no per-trade percentages beyond the 5.7 % total | Treat 3.2 as the extractor's gloss, not the video. |

## Verdict
Cannot be written exactly as Bailey does it (structure, zone, "clearly bullish" are by eye; 5m entry timing). It CAN be written as a mechanical stand-in, labelled OURS,
and was tested once, frozen: MyTradingSys/research/edge_views_2026-11-11/BAILEYS_SWEEP/ (PREREG committed first; RESULT.md).
Result on BTC DEV 2022-02..2024-05: n 321, fee-net -0.324 R (t -3.38), gross -0.058 R, win 23.7 % (25 % needed at 3R), both halves, both sides, every year negative;
placebo -0.281 R is no worse. FAIL. Stop-buffer need: median stop is 0.53 % of price, so a 10 bp fee costs about 0.19 R before slippage; a tighter stop is worse, a wider
buffer was not tested (one parameter set). What this does not show: that Bailey's discretionary reading fails; only that this mechanical reading has no edge net of fees.
Not run: VALIDATION (no pass, so none earned). No edge claim, no forecast.
