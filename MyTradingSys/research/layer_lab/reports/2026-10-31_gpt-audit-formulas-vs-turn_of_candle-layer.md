# GPT audit: FORMULAS.md vs turn_of_candle

Verdict: SOUND — the three checked toy outputs match the section 16 definitions.

## Scope and method

Read `MyTradingSys/backtest/layers/FORMULAS.md:392-403` and `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:1-75`. The layer uses section 16, T055 C3: epoch-aligned minute-of-quarter `mq=(t_ms//60000)%15`; per-bar simple return `(c-o)/o`; means split between `mq==0` and other bars, with per-minute means; event indices satisfy `mq == 15-lead_minutes` and carry the configured side. Cost/kill criteria are documented context, not computed by this module.

Toy series (10 bars, indices 0..9): timestamp `t=i*60,000 ms`, every open 100; closes `[101,99,100,100,100,100,100,100,100,100]`. Thus bar returns are `[+0.01,-0.01,0,...,0]`, with `mq=0..9`. Command: `python -c "from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import toc_minute_stats,turn_of_candle_events; M=60000; bars=[{'t':k*M,'o':100,'c':101 if k==0 else (99 if k==1 else 100)} for k in range(10)]; print(toc_minute_stats(bars)); print(turn_of_candle_events(bars,lead_minutes=14,side='long'))"`.

## Findings

| Severity | Formula / evidence | Hand result | Code result | Verdict |
|---|---|---:|---:|---|
| LOW | Section 16 `turn_mean`, FORMULAS.md:396-398; return and mq implementation `turn_of_candle.py:21-28,35-39`, mean `:41-45` | Only mq=0 bar is +0.01, so turn mean = 0.01 | `turn_mean: 0.01` | MATCH / SAME |
| LOW | Section 16 `other_mean`, FORMULAS.md:396-398; selection and mean `turn_of_candle.py:35-45` | Other nine returns sum −0.01; mean = −0.01/9 = −0.001111111111… | `other_mean: -0.0011111111111111111` | MATCH / SAME |
| LOW | Section 16 event rule, FORMULAS.md:399-401; target and selection `turn_of_candle.py:59-74` | lead=14 -> target mq=1; the only matching toy index is 1, side long | `[{'i': 1, 'side': 'long'}]` | MATCH / SAME |

The implementation’s `minute_of_quarter` matches the specified timestamp formula (`turn_of_candle.py:1-3`). No mismatch found in the three sampled outputs. This small audit does not establish performance or fee-adjusted edge.

## Follow-up cards

None.
