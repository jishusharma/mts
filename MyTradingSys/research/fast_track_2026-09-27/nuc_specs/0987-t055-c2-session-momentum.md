TASK: Write MyTradingSys/backtest/layers/session/session_momentum.py: intraday session-momentum event detector (T055 candidate C2, Shen/Urquhart/Wang 2022, FORMULAS.md section 15).
SCOPE: MyTradingSys/backtest/bt/bt_data.py:10-20
SCOPE: MyTradingSys/backtest/layers/FORMULAS.md:324-345
CREATE: MyTradingSys/backtest/layers/session/session_momentum.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/session/session_momentum.py. Nothing else. No test file.
OUTPUT_TOKENS: 3584
EXPECT: def session_momentum_events(

Python 3.10, stdlib only, pure function, no I/O, no network, no imports from `MyTradingSys.backtest.bt`.
Never mutate inputs. Bars are dicts with at least `"t"` (open time, epoch ms UTC), `"o"`, `"c"`, chronological,
of a fixed width `bar_min` minutes (any width that divides `first_min` and `entry_min`; MAY have gaps).

Module docstring: candidate C2, intraday session momentum. Source: Shen, Urquhart, Wang, Financial Review
57(2), 319-344, 2022 (T1): the return over the first half-hour predicts the return of the last half-hour.
The 24/7 BTC adaptation (session = UTC day from `session_start_min`) is UNDEFINED in the source and is a
parameter, not a claim. Independent layer, never a Tom filter. Events have the shape
`{"i": int, "side": "long"|"short", ...}` consumed by `layers/runner.forward_return_stats`; caller enters at
`closes[i]`.

def session_momentum_events(bars: list, bar_min: int = 1, session_start_min: int = 0, first_min: int = 30,
                            entry_min: int = 30, min_abs: float = 0.0) -> list:
    Raise `ValueError` if `bars` is empty, `bar_min <= 0`, `first_min <= 0`, or `entry_min < first_min`.
    `bar_ms = bar_min * 60000`, `DAY = 86400000`. Group bars by session: for a bar with open time `t`, its
    session start is `S = (t // DAY) * DAY + session_start_min * 60000`; if that `S > t`, use `S - DAY`
    instead (so a session can begin late in the previous UTC day). For each distinct `S` in ascending order,
    with `E = S + first_min * 60000`:
    - `first_bar` = the bar with the smallest `t` satisfying `t >= S` and `t < E` (skip the session if none);
      its `"o"` is the session open price.
    - `last_bar` = the bar with the largest `t` satisfying `t >= S` and `t + bar_ms <= E` (skip if none);
      its `"c"` is the first-window close.
    - `r_first = last_bar["c"] / first_bar["o"] - 1.0` (skip the session if `first_bar["o"] <= 0`).
    - side: `"long"` if `r_first > min_abs`, `"short"` if `r_first < -min_abs`, else skip the session.
    - entry bar = the bar (index `i` in the ORIGINAL `bars` list) with `t + bar_ms == S + entry_min * 60000`
      and `t >= S`; skip the session if there is none.
    Emit `{"i": i, "side": side, "r_first": r_first, "session_start": S}`. Return events sorted by `i`.
    `entry_min == first_min` is "rest of session"; a caller wanting the paper's "last half-hour" passes
    `entry_min = session_length_min - 30`.

Hand-computed check (verify your own logic, do not include as a test file). `bar_min=30`, 30-minute bars:
idx0 t=0 o=100 c=101; idx1 t=1800000 o=101 c=102; idx2 t=86400000 o=200 c=198; idx3 t=88200000 o=198
c=197. Defaults with `bar_min=30`, `first_min=30`, `entry_min=30`: session 0: first_bar idx0, last_bar
idx0, r_first = 101/100-1 = 0.01 -> long, entry bar is idx0 (0+1800000 == 0+1800000). Session 1 (S=86400000):
r_first = 198/200-1 = -0.01 -> short, entry idx2. Events `[i=0 long, i=2 short]`. With `entry_min=60`:
entries are idx1 and idx3. With `min_abs=0.015`: no events.
