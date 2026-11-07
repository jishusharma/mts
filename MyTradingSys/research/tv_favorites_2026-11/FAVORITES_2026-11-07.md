# The operator's TradingView favourites: what they are, what MTS has, how MTS would use them (2026-11-07, Lead C)

Source: his indicators dialog, 2026-11-07 19:37 IST, BINANCE:BTCUSDT.P 1M chart (shot 9.png). Five favourites. Formulas below are
SOURCED from the public Pine scripts (LazyBear's are open source); every threshold MTS would use is OURS until measured.
Rule (phase-first, 11-06): each becomes a CONTEXT column that is verified against his TradingView first, then used in the context
gate of the current phase. None becomes a signal on its own.

| Favourite (author) | What it is (SOURCED) | MTS today | MTS use (proposed, context) |
|---|---|---|---|
| ADX and DI (BeikabuOyaji) | Wilder DMI in one pane: DI+, DI-, ADX (len 14) with a strength line (20-25). Same maths as the built-in DMI. | `layers/adx/adx.py` (M1, 11-07); 2d cross census CENSUS.md; TradingView check pending (card adx-di-tradingview-crosscheck-1107) | trend-strength bucket at a 2d DI cross (CCU, Steve): <20 no trend, 20-40 trend, >40 stretched; ADX slope "coming from way high" = exhaustion read |
| Indicator: WaveTrend Oscillator [WT] (LazyBear) | ap = hlc3; esa = EMA(ap, 10); d = EMA(abs(ap - esa), 10); ci = (ap - esa) / (0.015 d); wt1 = EMA(ci, 21); wt2 = SMA(wt1, 4); OB 60/53, OS -60/-53 | `layers/wavetrend/wavetrend.py` (parity contract 10-17); atlas 9 cells INCONCLUSIVE; extreme-cross census 11-04: crosses come before a bounce, no edge after | OB/OS STATE as a phase column (where in the swing we are), never the cross as entry; multi-TF WT state is already on the live-aid page card |
| WaveTrend with Crosses [LazyBear] (lonestar108) | the same WT with dots where wt1 crosses wt2, coloured by OB/OS zone | same engine; nothing new to build | the dot = the cross we already count; only the zone (OB/OS) adds information |
| Squeeze Momentum Indicator [LazyBear] | squeeze ON when Bollinger (20, 2.0) sits inside Keltner (20, 1.5 x TR); momentum = linreg(close - avg(avg(hh20, ll20), sma20), 20); grey/black dots = squeeze, histogram = momentum | not in MTS (no engine, no FORMULAS section) | compression -> expansion state: Tom's balance/range before the move; his own BB range-to-range claim; squeeze ON + at a level = wait for release, squeeze OFF = the move is on. Column for W2 (wicks) and the range detector |
| Volume Flow Indicator [LazyBear] (Katsanos) | typical-price log change vs cutoff 0.2 x stdev(30) x price; signed volume counted only when the change beats the cutoff, volume capped at 2.5 x SMA(volume, 50); VFI = SMA(sum, 130) / SMA(volume, 50), smoothed EMA 3; above 0 bullish flow, below 0 bearish; divergences | not in MTS; nearest: CVD/footprint studies (NO-EDGE) | participation/effort behind a level test (M5 volume layer): VFI falling into a support test = no buyer participation; VFI divergence at a sweep = the "bought back" evidence the wick plan needs |

## Where each one is strongest for us (reading the five together, OURS)
- Phase: 2d DI cross + ADX bucket (direction and strength), WT zone (how far into the swing).
- Setup: squeeze ON at a Tom/Fabio level or an analyst cluster = energy stored; the release direction is read, not predicted.
- Confirmation: VFI sign and divergence, with the volume ratio and rejection speed from the wick note.
That is the three-layer shape of the roadmap (context -> setup -> confirmation); none of these five trades alone.

## Plan (P1-P4; nothing beyond P1 starts before the operator's go; all engines on the API credit, Haiku, about 1 USD each)
| # | Piece | Builds on | Verify |
|---|---|---|---|
| P1 | ADX/DI TradingView read (running now: he is signed in) | adx.py | 3 daily bars, tol 0.5, then VERIFIED-TV in FORMULAS |
| P2 | Squeeze Momentum engine + FORMULAS section + hand test | Bollinger exists (FORMULAS s22, `alerts/live_bb_top_reversal.bollinger`); Keltner and the linreg momentum are new | 3 bars on his chart, squeeze flag and momentum sign |
| P3 | VFI engine + FORMULAS section + hand test | daily and 15m klines with volume | 3 bars on his chart, sign and value |
| P4 | columns into the running work: ADX bucket -> CENSUS cascade (M4); squeeze state -> wick W2; VFI -> volume layer M5 | P1-P3 | hit rates per cell, n printed |

## Questions (defaults in brackets)
1. Build P2 and P3 now on the credit [yes, Haiku, about 2 USD] or after the TradingView read of ADX passes?
2. Timeframes for squeeze/VFI columns: 15m and 1h for session trades, 1d for the cycle context [yes]?
3. The BeikabuOyaji "ADX and DI" script: read it on his chart too, or is the built-in DMI enough [built-in; same maths]?
