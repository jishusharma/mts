TASK: Write MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py: turn-of-candle minute statistics and event detector on 1-minute bars (T055 candidate C3, Shanaev/Vasenin/Stepanov, FORMULAS.md section 16).
MODEL: qwen3-coder:30b
SCOPE: MyTradingSys/backtest/bt/bt_data.py:10-20
SCOPE: MyTradingSys/backtest/layers/FORMULAS.md:324-345
CREATE: MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py. Nothing else. No test file.
OUTPUT_TOKENS: 6144
EXPECT: def minute_of_quarter(
EXPECT: def toc_minute_stats(
EXPECT: def turn_of_candle_events(

Python 3.10, stdlib only, pure functions, no I/O, no network, no imports from `MyTradingSys.backtest.bt`.
Never mutate inputs. Bars are 1-minute dicts with at least `"t"` (open time epoch ms UTC), `"o"`, `"c"`,
chronological, MAY have gaps.

Module docstring: candidate C3, turn-of-candle effect. Source: Shanaev, Vasenin, Stepanov, Heliyon
(PMC10015199, T1): returns concentrate at the opening of 15-minute candles, i.e. minutes 0, 15, 30, 45 of the
hour. The paper has no cost model, and the effect direction is not stated in our report, so `side` is a
parameter and the sign of the turn-minute mean is reported by `toc_minute_stats`. Independent layer, never a
Tom filter. Events have the shape `{"i": int, "side": "long"|"short"}` consumed by
`layers/runner.forward_return_stats`; the caller enters at `closes[i]`.

def minute_of_quarter(t_ms: int) -> int:
    `(t_ms // 60000) % 15`. Epoch-aligned; 15 divides 60 so 0 is the first minute of every quarter hour.

def toc_minute_stats(bars: list) -> dict:
    Raise `ValueError` if `bars` is empty or any bar has `o == 0`. Per-bar return `(c - o) / o`. Group by
    `minute_of_quarter(bar["t"])`. Return `{"turn_mean": ..., "other_mean": ..., "turn_n": int, "other_n": int,
    "by_minute": {m: mean_return for m in 0..14 that have at least one bar}}`. `turn_mean` is the mean
    return over bars with minute 0 (or `None` if there are none); `other_mean` is the mean over all remaining
    bars (or `None`). `by_minute` keys are ints.

def turn_of_candle_events(bars: list, lead_minutes: int = 1, side: str = "long") -> list:
    Raise `ValueError` if `lead_minutes` is not in `1..14`, or `side` is not "long" or "short". Emit
    `{"i": i, "side": side}` for every index `i` whose bar has `minute_of_quarter(bar["t"]) == 15 - lead_minutes`
    (the entry is at that bar's close, immediately before the next candle opens). Ascending `i`. Empty `bars`
    returns `[]`.

Hand-computed check (verify your own logic, do not include as a test file). 30 bars `t = k*60000`,
`k=0..29`, all `o=100, c=100` except: k=0 c=101 (ret 0.01), k=15 c=103 (0.03), k=1 c=99 (-0.01). Turn bars
(minute 0) are k=0 and k=15: `turn_mean = 0.02`, `turn_n = 2`. The other 28 bars sum to -0.01, so
`other_mean = -0.01/28`, `other_n = 28`. `by_minute[1] = (-0.01 + 0.0)/2 = -0.005`. With `lead_minutes=1` events
are at minute 14: i=14 and i=29; with `lead_minutes=2`: i=13 and i=28.
