TASK: Write MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py: funding-extreme reversion merged with the CVD/price divergence fade (T055 candidate C1, FORMULAS.md section 14).
SCOPE: MyTradingSys/backtest/bt/bt_data.py:81-119
SCOPE: MyTradingSys/backtest/layers/FORMULAS.md:324-345
CREATE: MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py. Nothing else. No test file.
OUTPUT_TOKENS: 5120
EXPECT: def funding_percentiles(
EXPECT: def funding_pct_at(
EXPECT: def cvd_price_divergence(
EXPECT: def funding_cvd_fade_events(

Python 3.10, stdlib only, pure functions, no I/O, no network, no imports from `MyTradingSys.backtest.bt`
(reimplement the one-line delta formula shown at the SCOPE path, with a comment noting it matches
`bt_data.cvd_delta`). Funding list shape = what `bt_data.load_funding` returns: list of `(calc_time_ms, rate)`
tuples, sorted ascending. `bisect` allowed. Never mutate inputs.

Module docstring: candidate C1. Funding-extreme mean reversion (T2, Memon 2026, 7y Binance, via
research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md; that source does NOT give the percentile threshold, so
`hi`/`lo`/`lookback` are UNDEFINED in source and are grid parameters) merged with a CVD/price divergence
fade (T055a H2). It is an independent layer, never a filter on the Tom core. Signals fade the crowded side:
extreme high funding -> short, extreme low funding -> long. Events use the shape
`{"i": int, "side": "long"|"short", ...}` consumed by `layers/runner.forward_return_stats`; the caller enters
at `closes[i]`.

def funding_percentiles(funding: list, lookback: int) -> list:
    Raise `ValueError` if `lookback < 1`. For each index `k` from `lookback-1` to `len(funding)-1`: window
    `w = [rate for (_, rate) in funding[k-lookback+1 : k+1]]` (includes the current record), `r = funding[k][1]`,
    `pct = sum(1 for x in w if x <= r) / lookback`. Return a list of `(calc_time_ms_of_k, pct)` in order. Fewer
    than `lookback` records returns `[]`.

def funding_pct_at(series: list, t_ms: int):
    `series` is the output of `funding_percentiles`. Return the `pct` of the latest entry whose time is
    `<= t_ms`, or `None` if there is none (no look-ahead).

def cvd_price_divergence(bars: list, n: int) -> list:
    `bars`: dicts with at least `"c"`, `"v"`, `"tbv"`, chronological. Raise `ValueError` if `n < 1` or `bars` is
    empty. `cvd[i]` = running sum of `2*tbv - v` over bars `0..i`. For each `i` from `n` to `len(bars)-1`:
    `pc = [bars[j]["c"] for j in range(i-n, i)]`, `pv = [cvd[j] for j in range(i-n, i)]`. Bearish if
    `bars[i]["c"] > max(pc)` and `cvd[i] < max(pv)`. Bullish if `bars[i]["c"] < min(pc)` and `cvd[i] > min(pv)`
    (all comparisons strict; the two cases cannot both hold). Return a list of `{"i": i, "kind": "bearish"|"bullish"}`
    in ascending `i`.

def funding_cvd_fade_events(bars: list, funding: list, lookback: int = 90, n: int = 20, hi: float = 0.95,
                            lo: float = 0.05, use_divergence: bool = True) -> list:
    `series = funding_percentiles(funding, lookback)`; if `series` is empty return `[]`.
    If `use_divergence` is True: for each divergence event `d` from `cvd_price_divergence(bars, n)`, get
    `pct = funding_pct_at(series, bars[d["i"]]["t"])`; skip if `None`. `kind == "bearish"` and `pct >= hi` ->
    event side `"short"`; `kind == "bullish"` and `pct <= lo` -> side `"long"`. Event =
    `{"i": d["i"], "side": side, "funding_pct": pct, "div": d["kind"]}`.
    If `use_divergence` is False (funding-only variant): for each `(t, pct)` in `series`, `i` = index of the
    first bar with `bar["t"] >= t` (skip if none); `pct >= hi` -> `"short"`, `pct <= lo` -> `"long"`, else skip.
    Event = `{"i": i, "side": side, "funding_pct": pct, "div": None}`. Two records mapping to the same `i` keep
    both events (do not dedupe). Return events sorted by `i` (stable).

Hand-computed check (verify your own logic, do not include as a test file). Rates `[0.0001,0.0002,0.0003,
0.0004,0.0001]` at any increasing times, `lookback=4`: k=3 window [1,2,3,4], r=4 -> 4/4 = 1.0; k=4 window
[2,3,4,1], r=1 -> 1/4 = 0.25; result has two entries. Divergence, `n=3`, closes `[10,11,12,13,14,15]`, deltas
`[5,5,5,5,-5,-5]` (cvd `[5,10,15,20,15,10]`): i=3 price 13>12 but cvd 20 is not < 15 -> none; i=4 price 14>13
and cvd 15<20 -> bearish; i=5 price 15>14 and cvd 10<20 -> bearish.
