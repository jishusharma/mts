"""Pure forward MFE/MAE measurement for synthetic or caller-provided OHLC bars."""


def forward_excursion(bars, i_entry, side, r_price, horizon):
    """Measure forward excursions from the close of ``bars[i_entry]`` in R units.

    ``horizon`` counts bars after the entry bar. If the requested horizon extends
    beyond available data, all available forward bars are used and ``truncated``
    is true. A bar touching both 1R levels is resolved stop first (OURS).
    """
    if r_price <= 0:
        raise ValueError("r_price must be > 0")
    if side not in ("long", "short"):
        raise ValueError("side must be 'long' or 'short'")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 0:
        raise ValueError("horizon must be a nonnegative integer")
    if not isinstance(i_entry, int) or isinstance(i_entry, bool) or not 0 <= i_entry < len(bars):
        raise ValueError("i_entry must identify a bar in bars")

    entry = bars[i_entry]["c"]
    start = i_entry + 1
    available = max(0, len(bars) - start)
    count = min(horizon, available)
    forward = bars[start:start + count]
    favorable = adverse = 0.0
    target = entry + r_price if side == "long" else entry - r_price
    stop = entry - r_price if side == "long" else entry + r_price
    first_hit = None

    for bar in forward:
        high, low = bar["h"], bar["l"]
        if side == "long":
            favorable = max(favorable, (high - entry) / r_price)
            adverse = max(adverse, (entry - low) / r_price)
            hit_target, hit_stop = high >= target, low <= stop
        else:
            favorable = max(favorable, (entry - low) / r_price)
            adverse = max(adverse, (high - entry) / r_price)
            hit_target, hit_stop = low <= target, high >= stop
        if first_hit is None:
            if hit_stop:
                first_hit = "stop_1R"
            elif hit_target:
                first_hit = "target_1R"

    return {
        "mfe_r": max(0.0, favorable),
        "mae_r": max(0.0, adverse),
        "first_hit": first_hit,
        "truncated": horizon > available,
    }
