# PRE_REG: mined-but-never-backtested analyst rules MAL-R05, NK-R04, NK-R05, NK-R11, CBP-R05 (card edge8-mined-rules-nk-mal-cbp-1114)

Frozen BEFORE any outcome (R, return, win rate, p-value) is computed. Only data fetching and rule-text reading precede it.
Method modelled on `research/malkan_divergence_r03_r04_2026-11-13/` (edge4): close-based divergence, 12/18 bars, bootstrap in two views, placebo, BH.

## Sources (rule text as written in `research/layer_lab/gemini_edge_1113/mine-*/RULES.md`)
| Rule | Text (condensed) | Source |
|---|---|---|
| MAL-R05 | "Divergence visible on Weekly chart"; confirming "third candle (red/black day candle)"; entry "at that red black third candle"; stop "above high"; exit "target reached (point C)"; "Weekly context, Daily entry" ("There will be no direct trade in the weekly because Monday will come first.", "we will trade daily") | mine-malkan/RULES.md:15,111-125 -> extract_Wvq1TZh8aF0.md:500-518 |
| NK-R04 | 14-period RSI on the 15-minute chart "touches the 30 zone"; buy for overnight gap-up; stop = low of the spot candle; exit = trailing stop on each candle low; 10 and 5 minute charts as confirmation | mine-nk/RULES.md:16,54-59 -> nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:23 |
| NK-R05 | "if these three conditions match at closing time, 3:00 to 3:30 trading: 15-minute RSI at the 70 or 30 zone"; short for gap down at 70; stop = swing high; trailing stop on candle highs | RULES.md:17,61-66 -> EXTRACT.md:58 |
| NK-R11 | Bollinger Band breakout / "blast": long when the breakout candle's high is breached; "the candle that breaks, its low is important for us" (stop); "previous candle low treated as SL" (trail); size "scaled by timeframe" | RULES.md:23,103-108 -> wrEEf8o9n9E/EXTRACT.md:42 (and :17-18 for the trail) |
| CBP-R05 | "still holding above its low from September 15" (74,961, dipped to 74,871), higher low "around $77,800", stop = lower high under 77,800 with a daily close under 74,900, exit "the 80,000 range" | mine-cbp/RULES.md:15,51-54 -> cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:11,18 |

## Hypotheses
Each rule, applied mechanically as written on 20 liquid Bybit USDT perps pooled, has fee-net positive expectancy out of sample (2024+). Null: no edge. A transplant caveat applies to NK (index-options trader, NSE closing window, overnight gap) and is stated below; a failure on crypto is a failure of the transplant, not proof about NSE.

## Per-rule definition (exact)

### NOT_TESTABLE
- **CBP-R05: NOT_TESTABLE.** The text is a read of ONE dated BTC chart: absolute prices (74,961 low, 74,871 dip, 77,800 higher low, 74,900 stop, 80,000 target), valid for a single Sep-15 to Nov-06 2026 episode (N = 1). No generic, repeatable rule is written (no swing-lookback, no sweep depth, no confirmation count). Turning it into "any N-bar swing-low sweep with reclaim" would be inventing a rule (card forbids). Analyst calls are Context, never signals (memory: cbp-is-the-context-source). Left to a separate card if the operator names a generic sweep definition.
- NK-R04/R05 and the three-condition / 10 m / 5 m confirmation: only ONE of the "three conditions" (15 m RSI 14 at the 30/70 zone) is stated in the extract; the other two and the 10 m / 5 m confirmation thresholds are NOT_STATED, and Bybit has no 10 m bar. They are NOT tested; the NK cells are therefore labelled PARTIAL TEST (RSI zone + closing window + stated stop/trail only). Index-only scope ("not commodities, not stocks") is also not honoured (crypto transplant, OURS).

### Common
- Data: Bybit v5 public linear USDT perp klines (`api.bybit.com`, never a Binance futures host). 20 coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT TRX ATOM NEAR UNI ETC BCH FIL AAVE XLM (whatever each lists from 2020-01-01; OURS). 15m for NK rules, daily for MAL-R05 (weekly folded from daily, UTC Monday-anchored, complete weeks only). Closed bars only. Cache in `runtime_data/` (git-ignored).
- Indicators on closes known at the signal bar close: Wilder RSI(14) (SOURCED, NK extract "14 period"; Malkan RSI 14), Bollinger(20, 2.0) on closes (20 SOURCED via NK 20 SMA; 2.0 standard, OURS).
- Entry: next bar open after the signal bar closes. Exception, NK-R11 only: the rule is a stop-entry ("when the breakout candle high is breached"), so it fills at the trigger level (or the open if gapped above it) inside the next 4 bars after the breakout bar; never earlier than the bar after the signal.
- Costs: 2 x `fees.BINANCE_TAKER` + `fees.SLIPPAGE_RT_S13` = 12 bp round trip, imported from `MyTradingSys/backtest/fees.py`, charged on entry price, converted to R by dividing by the stop distance. Funding not modelled (holds <= 24 h for 15m rules; daily rule up to 30 days, limitation).
- Walk-forward exit: stop checked on every bar incl. the entry bar; same-bar stop + target = stop first; stop fills at the stop or the bar open if gapped through; trailing stop ratchets only (never loosens) using the PREVIOUS completed bar (the entry bar's own low/high counts from the second bar on); time exit at the close of the last bar. Trades without a full forward window are dropped.

### MAL-R05 (daily bars, weekly signal)
1. Weekly RSI(14) on weekly closes. Divergence on weekly CLOSES (SOURCED, operator relay: closes not wicks) via `backtest/layers/rsi/rsi_divergence.py::rsi_divergence`, min spacing 3, max W in {12, 18} weekly bars (W SOURCED operator relay "12/18"; applied to the weekly chart is OURS). Bearish (price higher close, RSI lower) = short; bullish = long. The divergence is known when the weekly bar after swing B closes (week i).
2. Confirming candle (OURS reading of "third day red/black candle"): the THIRD daily candle (Wednesday) of the week after week i; it must be red (close < open) for a short, green for a long, else no trade. Signal bar = that daily candle; entry = next daily open.
3. Stop (SOURCED kind "above the high"; span OURS): high (short) / low (long) of the signal daily candle, incl. shadow. Skip if entry is not strictly inside the stop.
4. Target = point C (SOURCED): short: lowest weekly CLOSE between swing A and swing B inclusive; long: highest weekly close there (closes basis OURS). Skip if C is not beyond entry in the trade direction. Time cap 30 daily bars (OURS), exit at close. Exit set: C only (stated). 4 cells: side {short, long} x W {12, 18}.

### NK-R04 / NK-R05 (15m)
1. Signal bar i: RSI14[i] <= 30 (R04, long) / >= 70 (R05, short); "touches the zone" is measured at the bar close only (OURS; intrabar RSI not available).
2. Variant WIN (the rule as stated): signal bar opens 09:30 or 09:45 UTC (= 15:00-15:30 IST, the NK closing window, SOURCED) and is the first qualifying bar of that coin, day and side. Variant ALL (descriptive transplant, OURS): any bar whose RSI is in the zone while the previous bar's RSI was not (fresh touch). Both are in the BH family.
3. Stop (SOURCED kind): low (long) / high (short) of the signal bar (OURS reading of "low of the spot candle"). Trail (SOURCED): previous candle low (long) / high (short). Time cap 96 bars = 24 h (OURS stand-in for "overnight gap"). Skip if entry open is not strictly inside the stop. 4 cells: {R04 long, R05 short} x {WIN, ALL}.

### NK-R11 (15m, long)
1. Breakout candle j: close[j] > upper BB(20, 2.0)[j] and close[j-1] <= upper BB[j-1] (first close outside; "fresh", OURS). Timeframe 15m (rule says "scaled by timeframe"; 15m = NK native in this card, OURS).
2. Trigger = high[j]. Armed for the next 4 bars (OURS, 1 h): first bar k in j+1..j+4 with high[k] >= trigger fills at max(open[k], trigger); no fill = no trade.
3. Stop (SOURCED): low[j]. Trail (SOURCED): previous candle low, ratchet. Cap 96 bars after the fill bar. 1 cell.

## Parameters
| Parameter | Value | Label |
|---|---|---|
| RSI length | 14 Wilder | SOURCED |
| RSI zones | 30 / 70 | SOURCED (NK) |
| Closing window | 09:30-10:00 UTC | SOURCED (15:00-15:30 IST) |
| Divergence price series | closes | SOURCED (operator) |
| Divergence spacing | 3..12 / 3..18 bars | SOURCED relay (12/18); min 3 SOURCED |
| BB length / width | 20 / 2.0 | SOURCED / OURS |
| Third candle = 3rd day of week after weekly confirmation | | OURS |
| Stop spans, trail previous candle | as above | SOURCED kind, OURS span |
| Point C on closes | | OURS |
| Time caps (30 daily, 96 x 15m), 4-bar arm | | OURS |
| Entry next open (R11: trigger fill) | | OURS (card) |
| Costs | fees.py 12 bp RT | fees.py |
| Universe, timeframes | 20 coins; 15m / D | OURS |

## Context
- MAL-R05: reversal / counter-trend at the end of a weekly leg; Malkan: bearish divergence "upward speed has reduced at point B", bullish "in a down trend". Needs a weekly swing structure with spacing 12-18 weeks; no trend filter in the primary cells. Daily timing "Monday will come first": the weekly signal is traded on the daily chart.
- NK-R04/R05: mean reversion into the 30/70 RSI zone on 15m, near the session close, to call an overnight gap. Needs a session close and an overnight gap that the market prices; crypto has neither (24/7), so the WIN variant tests only the time-of-day label; read results accordingly. In his words: "only index, not commodities, not stocks, the story is different there".
- NK-R11: trend-initiation / volatility expansion (Bollinger "blast"), long breakout; needs a market leaving a range with expanding bands; ride with previous-candle-low trail ("you can ride the trade for a long time").
- Regime: no regime gate. `Regime mix:` per split = share of weeks BTC close is above / below / inside +-5 % of its 200-day SMA (bull / bear / range), descriptive only (how it is read, not used to select trades).
- Session: UTC entry-hour blocks reported descriptively.
Phase: none as a gate; each rule is its own pattern: MAL-R05 weekly-leg reversal, NK-R04/R05 RSI-zone mean reversion near the close, NK-R11 Bollinger breakout (see bullets above).
Entry: next bar open after the signal bar closes (MAL-R05: 3rd daily candle after weekly divergence; NK-R04/R05: 15m RSI14 <= 30 / >= 70; NK-R11: stop-entry at breakout high within 4 bars).
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## Splits
DEV: trades with entry time <= 2023-12-31 23:59 UTC (descriptive only; nothing is tuned or dropped on DEV). VALIDATION: entry >= 2024-01-01 (to data end). Every cell is tested once on VALIDATION.

## Statistics
- Metric: fee-net mean R per trade, VALIDATION. Bootstrap 2000 resamples, seed fixed, 2.5/97.5 percentiles, one-sided p = share of resampled means <= 0: (A) day-clustered (one block per UTC entry day, all coins) and (B) per-trade i.i.d. Both reported; BOTH lower bounds must be > 0.
- Placebo: per cell 200 draws. Each real VALIDATION trade is replaced by a random bar of the SAME coin in the SAME ISO week with a full forward window, same side, same stop distance as a fraction of price (and same target-distance fraction for MAL-R05), same exit machinery (trail or target) and same cost; placebo p = share of draw means >= real mean. Real vs placebo mean holding time (bars) reported, since exits are rule-driven. "Beats placebo" = p < 0.05.
- BH at 10 % over all cell day-clustered p-values (9 cells).
- Best-5-days: drop the 5 UTC entry days with the highest summed R in VALIDATION; mean of the rest must stay > 0.

## Pass rule (per cell, all required)
VAL mean R > 0; day-clustered AND per-trade 95 % CI lower bound > 0; n_VAL >= 100 (else UNDERPOWERED); placebo p < 0.05; BH 10 % significant; mean R without best 5 days > 0. Else FAIL. A PASS is a lead needing a causal replay test and an independent re-run (CLAUDE.md), not a deployable rule. NK cells are PARTIAL TESTS: a FAIL does not refute NK's full rule, and a PASS is not NK's rule.

## Limitations
Bybit perp, not Binance; 20 coins correlated (day blocks absorb part); no funding; 15m trailing stops fill at the level; stop fills have no slippage beyond the 2 bp; 4 NK cells share events (WIN is a subset of ALL up to the first-bar-per-day rule), so tests are not independent.
