TASK: Write MyTradingSys/backtest/layers/positioning/trade_costs.py: net-of-cost trade return with Binance taker fee, slippage and funding (T055 shared cost model, FORMULAS.md section 13).
SCOPE: MyTradingSys/backtest/bt/bt_data.py:81-119
SCOPE: MyTradingSys/backtest/layers/FORMULAS.md:324-345
CREATE: MyTradingSys/backtest/layers/positioning/trade_costs.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/positioning/trade_costs.py. Nothing else. No test file.
OUTPUT_TOKENS: 3072
EXPECT: def funding_paid(
EXPECT: def net_return(

Python 3.10, stdlib only, pure functions, no I/O, no network, no imports from `MyTradingSys.backtest.bt`
(the funding list shape is the one `bt_data.load_funding` returns, shown at the SCOPE path: a list of
`(calc_time_ms, rate)` tuples sorted ascending; do not import it). Never mutate inputs. `bisect` is allowed.

Module docstring: T055 shared cost model for candidates C1 (funding_cvd_fade), C2 (session_momentum) and
C3 (turn_of_candle). Binance USDT-M perp taker fee 10 bps round trip, plus a slippage allowance, plus
perpetual funding: a long pays a positive funding rate and a short receives it. Funding is charged as a
fraction of ENTRY notional (documented simplification). Nothing here places orders.

def funding_paid(side: str, t_in: int, t_out: int, funding: list) -> float:
    `side` is "long" or "short" (raise `ValueError` for anything else; raise `ValueError` if
    `t_out < t_in`). `sgn = 1.0` for long, `-1.0` for short. Sum `rate` over every `(t, rate)` in `funding`
    with `t_in < t <= t_out` (entry instant EXCLUDED, exit instant INCLUDED). Return `sgn * that_sum`.
    A positive result is a cost to the trader, a negative result is income. Empty `funding` or no record in
    the interval returns `0.0`.

def net_return(side: str, p_in: float, p_out: float, t_in: int, t_out: int, funding: list,
               fee_rt: float = 0.0010, slip_rt: float = 0.0002) -> float:
    `gross = sgn * (p_out - p_in) / p_in` with `sgn` as above. Return
    `gross - fee_rt - slip_rt - funding_paid(side, t_in, t_out, funding)`. Raise `ValueError` if
    `p_in <= 0` or `side` is invalid.

Hand-computed check (verify your own logic, do not include as a test file). `funding = [(28800000, 0.0001),
(57600000, 0.0003), (0, 0.0009)]` sorted as `[(0, 0.0009), (28800000, 0.0001), (57600000, 0.0003)]`.
Long, `p_in=100, p_out=101, t_in=0, t_out=57600000`: the record at t=0 is excluded (entry instant), so
funding sum = 0.0001 + 0.0003 = 0.0004; `net = 0.01 - 0.0010 - 0.0002 - 0.0004 = 0.0084`.
Short, `p_in=100, p_out=99`, same times: gross = -1 * (99-100)/100 = 0.01; `funding_paid = -0.0004`;
`net = 0.01 - 0.0012 + 0.0004 = 0.0092`.
