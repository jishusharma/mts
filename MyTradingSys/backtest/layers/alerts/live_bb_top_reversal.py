"""Live adapter: 15m top-reversal candle at the upper Bollinger Band -> short (alert / testnet calibration data).

Definition source (card system/tasks/bb-top-reversal-candle-backtest.json, field "goal", line 10):
  "the operator's 15m top-reversal short pays: price climbs into resistance at or near the upper Bollinger Band,
   the prior 15m candle is green, the next candle turns red and trades/closes below the green candle's open or low."
Card "note" (line 14): entry variants E0..E3 pre-registered; "E2 closes below it" (below the prior green open);
  'Band touch has a cushion (operator: close enough counts): high within k x bandwidth of the upper band, k from
  sources or OURS.' Screenshot 2026-10-14_BTCUSDT_9fda889f1529.md row 3: green candle at the top, red candle after.
The card defines ONLY the top (short) side, so there is no mirror: short only.

Detector at bar i (all inputs <= bar i, causal):
  prior bar i-1 green (c>o) and its high >= upper_{i-1} - K*(upper_{i-1}-lower_{i-1});
  bar i red (c<o), closes below the prior green open (E2), and closes back inside (c_i <= upper_i).
Bollinger bands: SMA(20) of close +/- 2 * POPULATION stdev (Bollinger's own definition; FORMULAS.md section 22).

DECISION (OURS): BB 20/2 (card default; 24/7 candidates have no backtested source, SOURCES.md sec 1).
DECISION (OURS): K = 0.05 of bandwidth for "close enough" (no source gives a number, SOURCES.md sec 1).
DECISION (OURS): entry variant E2 (close-based; a bar-close alert has no intrabar fills), short only.
DECISION (OURS): "sampling": True - unrun card, calibration/data source only, no edge claim. Never a Tom filter.
Stdlib only. Bars are closed klines {t,o,h,l,c,v,tbv}; event "t" = signal bar OPEN time.
"""
import math

BB_N = 20
BB_MULT = 2.0
TOUCH_K = 0.05


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def bollinger(closes, n=BB_N, mult=BB_MULT):
    """-> (upper, lower) lists; None until n finite closes are available (a NaN in the window gives None)."""
    up, lo = [None] * len(closes), [None] * len(closes)
    for i in range(n - 1, len(closes)):
        w = closes[i - n + 1:i + 1]
        if not all(_num(x) for x in w):
            continue
        m = sum(w) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / n)
        up[i], lo[i] = m + mult * sd, m - mult * sd
    return up, lo


def _ok(b):
    return all(_num(b.get(k)) for k in ("o", "h", "l", "c"))


def bb_top_reversal_layer(bars):
    """15m bars. Short on the E2 top-reversal described in the module docstring."""
    if len(bars) < BB_N + 1:
        return []
    up, lo = bollinger([b["c"] if _ok(b) else float("nan") for b in bars])
    out = []
    for i in range(BB_N, len(bars)):
        p, b = bars[i - 1], bars[i]
        if up[i] is None or up[i - 1] is None or not (_ok(p) and _ok(b)):
            continue
        bw = up[i - 1] - lo[i - 1]
        touched = p["h"] >= up[i - 1] - TOUCH_K * bw
        if p["c"] > p["o"] and touched and b["c"] < b["o"] and b["c"] < p["o"] and b["c"] <= up[i]:
            out.append({"t": b["t"], "side": "short", "event": "bb_top_reversal_short",
                        "upper": round(up[i - 1], 2), "sampling": True})
    return out
