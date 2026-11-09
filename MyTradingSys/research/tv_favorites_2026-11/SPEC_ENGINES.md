# SPEC: Squeeze Momentum and Volume Flow Indicator engines (cards squeeze-momentum-engine-1107, vfi-engine-1107)

Operator 2026-11-07: "Yes, build both" (FAVORITES_2026-11-07.md P2/P3), "use login A and C and other gemini models to get things
done". Context columns only; no signal, no order, no promoted setup. Formulas SOURCED from LazyBear's public Pine scripts; the
defaults below are the scripts' defaults (SOURCED); anything else is OURS and labelled.

## A. Squeeze Momentum (card squeeze-momentum-engine-1107, login A, Sonnet)
Formula (SOURCED, LazyBear "Squeeze Momentum Indicator"):
- BB: basis = SMA(close, 20); dev = 2.0 x stdev(close, 20); upper/lower = basis +- dev.
- KC: ma = SMA(close, 20); range = TR (true range); rangema = SMA(range, 20); upper/lower = ma +- 1.5 x rangema.
- squeeze ON when BB lower > KC lower and BB upper < KC upper; squeeze OFF when BB lower < KC lower and BB upper > KC upper; else "no squeeze" (neither).
- momentum = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), SMA(close, 20)), 20, 0) (the value of the 20-bar least-squares line at the current bar).
Done when:
1. `MyTradingSys/backtest/layers/FORMULAS.md` gets section "Squeeze Momentum (LazyBear)" with the formula and a 25-bar toy series whose squeeze flags and momentum values are computed by hand in the section (not from code); Bollinger reuses section 22's definition.
2. `MyTradingSys/backtest/layers/squeeze/squeeze.py`: `squeeze_momentum(high, low, close, bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, mom_len=20, textbook_bb=False) -> (squeeze_on: list[bool|None], squeeze_off: list[bool|None], momentum: list[float|None])`; `test_squeeze.py` asserts the hand values and FAILS on the pre-change tree (no module); registered in run_all_tests.py; wiring_registry entry (WIRE, ref vfi-engine-1107 or the W2 wick card).
   Note (card squeeze-script-bb-mult-1107, 2026-11-07): LazyBear's script sizes the BB half-width with the KC multiplier (`dev = multKC * stdev`), so the default BB half-width is kc_mult*sd = 1.5*sd (script quirk, SOURCED) and `bb_mult` is used only with `textbook_bb=True` (OURS). FORMULAS s31.
3. A one-screen `research/tv_favorites_2026-11/SQUEEZE_STATE.md`: on BTCUSDT 1d, 1h, 15m (Bybit/Binance public klines, last 90 days) the share of bars in squeeze, median squeeze length in bars, and the last 5 squeeze releases with the sign of momentum at release and the move over the next 12 bars (descriptive, n printed, no verdict).
4. Ship with `Result: <share in squeeze on 1d/1h/15m>` and `Next: END: C verifies on TradingView (3 bars, squeeze flag + momentum sign)`.

## B. Volume Flow Indicator (card vfi-engine-1107, API credit, Sonnet via api_job --engine api)
Formula (SOURCED, LazyBear "Volume Flow Indicator", after Katsanos 2004):
- typical = hlc3; inter = log(typical) - log(typical[1]); vinter = stdev(inter, 30); cutoff = coef x vinter x close, coef = 0.2.
- vave = SMA(volume, 130)[1] (CORRECTED 11-07: the script uses one `length`; the 50 here was Lead C's recall); vmax = vave x vcoef, vcoef = 2.5; vc = min(volume, vmax).
- mf = typical - typical[1]; vcp = +vc if mf > cutoff, -vc if mf < -cutoff, else 0.
- vfi = sum(vcp, 130) / vave; if smoothing, vfi = SMA(vfi, 3) (CORRECTED 11-07, VERIFIED-TV 4/4 bars, FORMULAS s32; smoothVFI default false; both outputs returned).
Done when:
1. FORMULAS.md section "Volume Flow Indicator (LazyBear / Katsanos)" with the formula and a short toy series (length parameters reduced for the toy, stated) computed by hand.
2. `MyTradingSys/backtest/layers/vfi/vfi.py`: `vfi(high, low, close, volume, length=130, coef=0.2, vcoef=2.5, smooth=3) -> (vfi_raw, vfi_smoothed)`; `test_vfi.py` asserts the hand values, FAILS pre-change; registered in run_all_tests.py; wiring_registry entry.
3. `research/tv_favorites_2026-11/VFI_STATE.md`: BTCUSDT 1d and 15m, last 90 days: share of bars with vfi > 0, the last 5 zero crosses with the 12-bar move after, and VFI at the Friday 2026-11-06 15:00Z sweep bar (15m) with the 20 bars before it (was flow falling into the test?). Descriptive, n printed.
4. Ship with `Result: <vfi sign at the 11-06 sweep; share > 0 on 1d>` and `Next: END: C verifies on TradingView (3 bars)`.

## Both
- Public market data only (Bybit `api.bybit.com/v5/market/kline` works from the desktop; Binance times out there); no runtime/order data.
- No HOLDOUT file is opened; nothing is tuned; every number in the STATE files is descriptive.
- Verification: Lead C runs the Haiku Chrome read on the operator's signed-in TradingView (built-in or LazyBear script with the same inputs) and writes the VERIFIED-TV line, as for ADX/DI (TV_CROSSCHECK.md pattern).
