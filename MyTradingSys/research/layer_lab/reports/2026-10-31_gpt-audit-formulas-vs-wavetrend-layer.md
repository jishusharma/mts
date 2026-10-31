# WaveTrend formula audit

Verdict: SOUND

## Checked

- MyTradingSys/backtest/layers/FORMULAS.md:516-528 defines the sourced oscillator and OURS conventions.
- MyTradingSys/backtest/layers/wavetrend/wavetrend.py:8-12, 18-43, 46-59, 73-109 implements the indicator, zone, cross, timing and warm-up behavior.
- Toy input: 10 hourly bars, high = low = close = 10, 11, ..., 19; open times are consecutive hourly milliseconds. Synthetic arithmetic, not market data.
- Command: python -c "import sys; sys.path.insert(0,'MyTradingSys/backtest/layers/wavetrend'); import wavetrend; bars=[(i*3600000, p, p, p) for i,p in enumerate(range(10,20))]; rows=wavetrend.compute(bars,3600000,warmup=0); print(...)" (invocation printed all rows). warmup=0 exposes short-series outputs for comparison; production default is 200 (wavetrend.py:12).

## Formula inventory and hand checks

The complete indicator chain used by this layer is §20.1: ap=(h+l+c)/3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4), with EMA alpha 2/(n+1) (FORMULAS.md:520). For this toy, each ap equals its close. EMA states seed on the first valid source (FORMULAS.md:522; code wavetrend.py:92-101). At bar 0 the series is flat and ci is undefined; the first valid bar is index 1.

Hand recurrence: alpha10=2/11, alpha21=1/11. Bar 1: esa=10+(2/11)(11-10)=10.181818182; x=|11-esa|=0.818181818; d=(2/11)x=0.148760331; ci=x/(0.015*d)=366.666666667, so seeded wt1=366.666666667. Bar 2: esa=10.512396694, x=1.487603306, d=0.392186326, ci=252.873563218, wt1=(10/11)(366.666666667)+(1/11)(252.873563218)=356.321839080. Bar 3 gives wt1=341.781850906; bar 4 gives wt1=325.512561489; hence wt2[4]=(366.666666667+356.321839080+341.781850906+325.512561489)/4=347.570729536.

| Check / formula | Formula and code evidence | Hand | Layer output | Result |
|---|---|---:|---:|---|
| WT1 seed, formula chain | FORMULAS.md:520; implementation wavetrend.py:92-101 | index 1: 366.666666667 | index 1: 366.66666666666663 | MATCH |
| WT1 EMA(21), formula chain | FORMULAS.md:520; implementation alpha and recurrence wavetrend.py:76, 100-103 | index 2: 356.321839080 | index 2: 356.32183908045977 | MATCH |
| WT2 SMA(4), formula chain | FORMULAS.md:520, 522; sma wavetrend.py:18-23, applied at :105 | index 4: 347.570729536 | index 4: 347.57072953553654 | MATCH |
| Typical price ap=(h+l+c)/3 | FORMULAS.md:520; wavetrend.py:92 | every toy bar equals its close | used as close-valued ap | MATCH |
| Flat-window and NaN rule | FORMULAS.md:522; wavetrend.py:96-99 | index 0 has d=0, no valid ci | index 0 WT1/WT2 NaN | MATCH |
| Zones ob2 >= 60, ob1 >= 53, os2 <= -60, os1 <= -53, else mid | FORMULAS.md:522; thresholds wavetrend.py:9-10, branches :32-43 | WT1 at indices 1-9 exceeds 60 => ob2 | all indices 1-9 tagged ob2 | MATCH |
| Cross le strict-side behavior; NaN resets | FORMULAS.md:522, 528; wavetrend.py:46-59 | toy WT1/WT2 remain ordered with no reversal, hence no cross | event 0 on all ten bars | MATCH |
| Output availability at bar close | FORMULAS.md:522; row construction wavetrend.py:109 | hourly open + 3,600,000 ms | returned available_at=open_time+tf_ms | MATCH |
| Default 200-bar warm-up convention | FORMULAS.md:522; constant/mask wavetrend.py:12, 104-107 | ten-bar toy is shorter than 200, so normal-default outputs are masked | comparison used documented override warmup=0; default would mask every value | MATCH |
| HTF index convention: last HTF bar closed by t | FORMULAS.md:522; wavetrend.py:62-70 | rule is open + htf_ms <= t | code returns latest qualifying index | MATCH |

No DIFFERENT or NOT_IN_DATA findings. This confirms implementation against the repository formula and conventions on the stated toy fixture; it does not establish TradingView runtime parity (FORMULAS.md:530).

## Follow-up

- None.
