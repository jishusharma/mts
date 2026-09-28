"""
MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py - FAB-007 CVD-vs-price divergence absorption detector.

This implements FAB-007 from the extract verbatim:
"CVD makes a lower low while price is still on the same level as before" = passive buyers absorbing
aggressive sellers (bullish). The mirror case (CVD higher high, price holds the prior high -> bearish)
is implemented as a documented symmetric extension.

Per-bar delta = 2 * bar["tbv"] - bar["v"] (same as MyTradingSys.backtest.bt.bt_data.cvd_delta;
do NOT import bt_data, since this package must not depend on `bt/` -- reimplement the one-line formula
here with a comment noting it matches `bt_data.cvd_delta`).

CVD = the running cumulative sum of that per-bar delta, reset once at the start of the input (no session
reset -- reset-point is out of scope, per the extract's own "UNDEFINED: CVD anchor/reset point").

Swing detection: reuse find_swings from cc_structure unchanged.
"""

from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings


def cumulative_cvd(bars: list) -> list:
    """
    Calculate cumulative CVD (Volume Delta) for each bar in the input.

    `bars` is a list of dicts each with at least `"v"` (volume) and `"tbv"` (taker buy volume),
    in chronological order. Returns a list the same length as `bars`, where `result[i]` is the
    running sum of `(2*bars[j]["tbv"] - bars[j]["v"])` for `j` in `0..i` inclusive.
    `result[0]` = bar 0's own delta.

    Raise `ValueError` if `bars` is empty.
    """
    if not bars:
        raise ValueError("bars must not be empty")

    result = []
    cvd = 0
    for bar in bars:
        delta = 2 * bar["tbv"] - bar["v"]
        cvd += delta
        result.append(cvd)
    return result


def cvd_absorption_events(bars: list, left: int = 2, right: int = 2, use_body: bool = True, price_tolerance: float = 0.001) -> list:
    """
    Detects FAB-007 bullish and (symmetric-extension) bearish absorption between CONSECUTIVE
    same-kind confirmed swings.

    1. `swings = find_swings(bars, left=left, right=right, use_body=use_body)` (raises whatever
       `find_swings` raises, e.g. on empty `bars` -- do not catch it).
    2. `cvd = cumulative_cvd(bars)`.
    3. Walk `swings` in order; for each kind ("low" or "high") independently, compare each swing to
       the PREVIOUS swing of the SAME kind (skip if there is no earlier same-kind swing).
       - Bullish (kind == "low"): let `prev`, `cur` be the previous and current low swings. Bullish
         absorption fires if BOTH: (a) `cvd[cur["i"]] < cvd[prev["i"]]` (CVD makes a lower low -- a
         STRICT decrease), AND (b) price holds: `cur["price"] >= prev["price"] * (1 - price_tolerance)`
         (price at the current low is not below the prior low by more than `price_tolerance`, i.e. it
         did NOT confirm a new price low to the same degree CVD did). If both hold, append an event:
         `{"t": bars[cur["confirmed_i"]]["t"], "i": cur["confirmed_i"], "swing_i": cur["i"], "side":
         "long", "kind": "bullish_absorption", "cvd_prev": cvd[prev["i"]], "cvd_cur": cvd[cur["i"]],
         "price_prev": prev["price"], "price_cur": cur["price"]}`. The event's time/index is the
         CONFIRMATION bar (`confirmed_i`), never the swing's own bar `i` -- that is what makes this
         look-ahead-free (the swing, and therefore the event, is only known `right` bars after `i`).
       - Bearish (kind == "high", documented symmetric extension, NOT stated in the video): fires if
         BOTH: (a) `cvd[cur["i"]] > cvd[prev["i"]]` (CVD makes a higher high), AND (b)
         `cur["price"] <= prev["price"] * (1 + price_tolerance)` (price does not confirm a new high to
         the same degree). Event: same shape, `"side": "short"`, `"kind": "bearish_absorption"`.
    4. Return all events sorted by `"i"` ascending (stable sort; if two events share the same `i`,
       preserve the order they were generated in, bullish before bearish at that index).
    Raise `ValueError` if `len(bars) != len(cvd)` can never happen internally, but DO raise `ValueError`
    if `price_tolerance < 0`.
    """
    if price_tolerance < 0:
        raise ValueError("price_tolerance must be non-negative")

    swings = find_swings(bars, left=left, right=right, use_body=use_body)
    cvd = cumulative_cvd(bars)

    events = []
    prev_low = None
    prev_high = None

    for swing in swings:
        if swing["kind"] == "low":
            if prev_low is not None:
                # Check for bullish absorption
                if (cvd[swing["i"]] < cvd[prev_low["i"]] and
                        swing["price"] >= prev_low["price"] * (1 - price_tolerance)):
                    events.append({
                        "t": bars[swing["confirmed_i"]]["t"],
                        "i": swing["confirmed_i"],
                        "swing_i": swing["i"],
                        "side": "long",
                        "kind": "bullish_absorption",
                        "cvd_prev": cvd[prev_low["i"]],
                        "cvd_cur": cvd[swing["i"]],
                        "price_prev": prev_low["price"],
                        "price_cur": swing["price"]
                    })
            prev_low = swing
        elif swing["kind"] == "high":
            if prev_high is not None:
                # Check for bearish absorption (symmetric extension)
                if (cvd[swing["i"]] > cvd[prev_high["i"]] and
                        swing["price"] <= prev_high["price"] * (1 + price_tolerance)):
                    events.append({
                        "t": bars[swing["confirmed_i"]]["t"],
                        "i": swing["confirmed_i"],
                        "swing_i": swing["i"],
                        "side": "short",
                        "kind": "bearish_absorption",
                        "cvd_prev": cvd[prev_high["i"]],
                        "cvd_cur": cvd[swing["i"]],
                        "price_prev": prev_high["price"],
                        "price_cur": swing["price"]
                    })
            prev_high = swing

    # Sort events by index ascending, preserving order for same index (stable sort)
    events.sort(key=lambda x: x["i"])
    return events
