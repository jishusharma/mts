# Retested low, then a break in the US window: base rates and leveraged short tests (BTCUSDT 1m, 2022-01..2026-10-13)

Ask (operator, 2026-10-14, shot e2379c5fdf2e): "a local low is set - then a retest - does not take it out so that longs
build then on US session start - low broken! happens quite often!" Then: short from the daily high, buy back at a Tom
pivot and go long, sell a double top before the US open and short again. Use 5-20x leverage, wide stops, build the
position fixed-fixed-double-triple. "A valid back test must be established first."
Script: `study.py` (definitions are in the header, fixed before the first run). Output: `results.json`.
All numbers are OURS. Nothing was tuned: one definition, one run. DEV 2022-2024, VAL 2025, HOLDOUT 2026, reported side by side.
Taker fee 0.05% per side on every fill. Funding is not modelled.

## Definitions (short form)
- Weekdays only. A = US cash open (13:30Z under US DST, otherwise 14:30Z). Decision time T0 = A-90 min, i.e. before the
  08:30 ET data slot. L = lowest low of the 24 h before T0.
- RETESTED: within the 6 h before T0 (06:00-12:00Z in summer, the EU session), price came back to within 0.20% of L,
  at least 2 h after L was set and after a bounce of at least 0.6%. SINGLE: L was never retested. Price at T0 must be
  at least 0.2% above L.
- Outcome window: T0 to T0+4 h. "Break" = any trade below L. "Reclaim" = a close back above L within 120 min of the break.

## Findings
1. **On retested days the low breaks in the US window 57% of the time** (n=99, 95% CI 47-66%). On single-low days it
   breaks 26% of the time (n=1027). By split: DEV 53%, VAL 48%, HOLDOUT 72%.
2. **The retest does not cause the extra breaks. Distance to the low does.** Retested days sit closer to L when the
   decision is made. Inside the same distance bucket the break rates match:
   - 0.2-0.5% away: retested 74% (n=43), single 79% (n=65)
   - 0.5-1% away: retested 58% (n=31), single 58% (n=153)
   - 1-2% away: retested 22% (n=23), single 29% (n=301)

   Conclusion: "longs build on the retest, so the low breaks" is not visible in price data. Price near a level in the
   US window breaks it at the same rate either way.
3. **The US window breaks levels more often than other times of day. That is volatility.** Retested lows break 57%
   in the US window and 30-34% with the window moved 6 or 12 hours (placebo anchors). Single lows break 26% vs 12-18%.
   This matches F1 in `BTC_SESSION_SWEEPS_2026-10-04.md`: the US open is real for volatility, not for direction.
   The placebo comparison is not distance-matched.
4. **Most breaks are sweeps.** After a break, price closes back above L within 120 min 95% of the time on retested
   days (n=56) and 93% on single days. A break is a place to cover the short and look for a long, not to add short.
   This needs a separate test: whether a long after the reclaim pays net of fees.
5. **The short has no edge.** Entry at T0, stop 0.1% above the 6 h high, target L-0.3%, time exit at T0+4 h:
   - Retested days: mean -0.02% per trade, t -0.24, win 42%. DEV +0.10%, VAL -0.37% (t -3.1), HOLDOUT +0.01%.
   - Single days: mean -0.13%, t -4.0.
6. **Fixed-fixed-double-triple (1-1-2-3 units) does not create an edge.** Adds at +0.4%, +0.8% and +1.2%; one stop at
   +1.6%. On retested days it wins 64% of trades, but the mean is -0.02% of full-size notional (t -0.32). It is a
   martingale: many small wins, a few 7-unit losses.
   A first version of the script averaged P&L per filled unit, which weighted a 7-unit loser the same as a 1-unit
   winner. That showed +0.30% (t 3.4) and was wrong. It was fixed before this write-up (`_pnl` docstring).
7. **Leverage multiplies the result; it never makes one.** Compounded over all 99 retested days, equity multiple and
   max drawdown for the flat short:
   - 5x: 0.83 equity, 56% max drawdown
   - 10x: 0.60 equity, 82% max drawdown
   - 20x: 0.19 equity, 98% max drawdown

   The 1-1-2-3 ladder at full size: 10x ends at 0.72 equity with a 67% max drawdown; 20x ends at 0.39 with a 91% max
   drawdown. With these stops, no trade got near the liquidation price at 5-20x. The stop, not liquidation, sets the
   loss, and leverage scales that loss straight into the account.

## Today (2026-10-14), checked against 1m data
- First low 82912.8 at 13 Oct 17:54Z (US afternoon, not the EU session). Retest 82930.0 at 14 Oct 10:06Z (EU) held.
  Bounce high 84117.6 at 08:10Z. A lower high of 83930.1 at 12:30Z (a double-top shape before the US open).
- The break came in ONE 1m bar at 12:30:00Z (83930 to 82669), which is 08:30 ET: the US data slot, 60 min before the cash open.
- Low 82290.7 at 13:21Z (0.75% under L). By 13:47Z price was back above L at 83008, which is the reclaim pattern from
  finding 4. Today is not in the counts: its outcome window was still open when the data was pulled.

## Verdict
EXPLORATORY NEGATIVE for the short leg, as defined. The pattern is real as a description (lows near price break
often in the US window) but adds nothing over distance plus time of day. The fixed-fixed-double-triple ladder and 5-20x
leverage do not change the sign.
Open legs (card filed): (a) a long after a sweep and reclaim, with a stability test; (b) RSI divergence on smaller
timeframes as the trigger for the short from the daily high; (c) the double-top short before the US open. Each needs
its own pre-registered definition before it is run.
