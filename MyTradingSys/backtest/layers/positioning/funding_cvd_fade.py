"""
candidate C1. Funding-extreme mean reversion (T2, Memon 2026, 7y Binance, via
research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md; that source does NOT give the percentile threshold, so
`hi`/`lo`/`lookback` are UNDEFINED in source and are grid parameters) merged with a CVD/price divergence
fade (T055a H2). It is an independent layer, never a filter on the Tom core. Signals fade the crowded side:
extreme high funding -> short, extreme low funding -> long. Events use the shape
`{"i": int, "side": "long"|"short", ...}` consumed by `layers/runner.forward_return_stats`; the caller enters
at `closes[i]`.
"""

from bisect import bisect_right


def funding_percentiles(funding: list, lookback: int) -> list:
    """Calculate funding percentiles for each time point."""
    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    if len(funding) < lookback:
        return []
    
    result = []
    for k in range(lookback - 1, len(funding)):
        window = [rate for (_, rate) in funding[k - lookback + 1 : k + 1]]
        r = funding[k][1]
        pct = sum(1 for x in window if x <= r) / lookback
        result.append((funding[k][0], pct))
    return result


def funding_pct_at(series: list, t_ms: int):
    """Get the latest funding percentile before or at time t_ms."""
    if not series:
        return None
    idx = bisect_right([x[0] for x in series], t_ms) - 1
    if idx < 0:
        return None
    return series[idx][1]


def cvd_price_divergence(bars: list, n: int) -> list:
    """Calculate CVD price divergence events."""
    if n < 1 or not bars:
        raise ValueError("n must be >= 1 and bars must not be empty")
    
    # Calculate cumulative CVD
    cvd = [0] * len(bars)
    for i in range(len(bars)):
        cvd[i] = 2 * bars[i]["tbv"] - bars[i]["v"]
        if i > 0:
            cvd[i] += cvd[i - 1]
    
    events = []
    for i in range(n, len(bars)):
        pc = [bars[j]["c"] for j in range(i - n, i)]
        pv = [cvd[j] for j in range(i - n, i)]
        
        price_max = max(pc)
        price_min = min(pc)
        cvd_max = max(pv)
        cvd_min = min(pv)
        
        if bars[i]["c"] > price_max and cvd[i] < cvd_max:
            events.append({"i": i, "kind": "bearish"})
        elif bars[i]["c"] < price_min and cvd[i] > cvd_min:
            events.append({"i": i, "kind": "bullish"})
    
    return events


def funding_cvd_fade_events(bars: list, funding: list, lookback: int = 90, n: int = 20, hi: float = 0.95,
                            lo: float = 0.05, use_divergence: bool = True) -> list:
    """Generate events for funding-extreme reversion merged with CVD/price divergence fade."""
    series = funding_percentiles(funding, lookback)
    if not series:
        return []
    
    events = []
    
    if use_divergence:
        # Use divergence-based approach
        divergences = cvd_price_divergence(bars, n)
        for d in divergences:
            pct = funding_pct_at(series, bars[d["i"]]["t"])
            if pct is None:
                continue
            
            side = None
            if d["kind"] == "bearish" and pct >= hi:
                side = "short"
            elif d["kind"] == "bullish" and pct <= lo:
                side = "long"
            
            if side:
                events.append({
                    "i": d["i"],
                    "side": side,
                    "funding_pct": pct,
                    "div": d["kind"]
                })
    else:
        # Use funding-only approach
        for t, pct in series:
            # Find the first bar with time >= t
            i = None
            for j in range(len(bars)):
                if bars[j]["t"] >= t:
                    i = j
                    break
            
            if i is None:
                continue
                
            side = None
            if pct >= hi:
                side = "short"
            elif pct <= lo:
                side = "long"
            
            if side:
                events.append({
                    "i": i,
                    "side": side,
                    "funding_pct": pct,
                    "div": None
                })
    
    # Sort by index to ensure stable order
    events.sort(key=lambda x: x["i"])
    return events

