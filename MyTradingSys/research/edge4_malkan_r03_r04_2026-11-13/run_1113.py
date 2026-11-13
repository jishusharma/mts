"""Malkan MAL-R03 (bearish) / MAL-R04 (bullish) regular RSI divergence engine. Rules: PRE_REG.md. Part b = engine only.

Bars are [open_ms, o, h, l, c, v] ascending. Swing = close strictly above (R03) / below (R04) both neighbouring closes
(1 bar each side, OURS); A, B and C use closes only, never wicks. The confirming candle is the bar right after B
(red for R03, green for R04); entry at its close, stop beyond its extreme, target point C.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest")))
import fees  # noqa: E402

COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13  # round trip, fraction of entry price, taker on every fill


def rsi_wilder(closes, n=14):
    """Wilder RSI; None for the first n bars (index n is the first value)."""
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    ch = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    ag = sum(max(c, 0.0) for c in ch[:n]) / n
    al = sum(max(-c, 0.0) for c in ch[:n]) / n

    def val():
        return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    out[n] = val()
    for i in range(n + 1, len(closes)):
        c = ch[i - 1]
        ag = (ag * (n - 1) + max(c, 0.0)) / n
        al = (al * (n - 1) + max(-c, 0.0)) / n
        out[i] = val()
    return out


def find_signals(bars, lookback, rule, rsi=None):
    """Signals for rule 'R03' (short) or 'R04' (long): dicts t (confirm bar index), a, b, entry, stop, target, side.
    A = most recent swing before B, 2..lookback bars earlier; divergence needs price and RSI to disagree."""
    short = rule == "R03"
    c = [b[4] for b in bars]
    if rsi is None:
        rsi = rsi_wilder(c)
    sgn = 1 if short else -1  # compare sgn*close so one code path serves both sides

    def pivot(i):
        return 0 < i < len(c) - 1 and sgn * c[i] > sgn * c[i - 1] and sgn * c[i] > sgn * c[i + 1]
    piv = [i for i in range(len(c)) if pivot(i)]
    out = []
    for k, b in enumerate(piv):
        t = b + 1
        if t >= len(bars):
            continue
        o, h, l, cl = bars[t][1], bars[t][2], bars[t][3], bars[t][4]
        if not (cl < o if short else cl > o):
            continue
        if k == 0:
            continue
        a = piv[k - 1]
        if not (2 <= b - a <= lookback) or rsi[a] is None or rsi[b] is None:
            continue
        if not (sgn * c[b] > sgn * c[a] and sgn * rsi[b] < sgn * rsi[a]):
            continue
        seg = c[a:b + 1]
        target = min(seg) if short else max(seg)
        stop = h if short else l
        if (short and not (stop > cl > target)) or (not short and not (stop < cl < target)):
            continue
        out.append({"t": t, "a": a, "b": b, "entry": cl, "stop": stop, "target": target, "side": "short" if short else "long"})
    return out


def simulate(bars, signals, lookback, iv_ms):
    """One open position per coin: a signal while a trade is open is skipped. Exit at target, stop, or the close of bar
    t + 2*lookback; a bar touching both counts as the stop. Trades whose bars A..exit are not contiguous are dropped.
    net_r = (gross move - COST * entry) / risk."""
    trades = []
    busy_until = -1
    for s in signals:
        t = s["t"]
        if t <= busy_until:
            continue
        short = s["side"] == "short"
        risk = abs(s["stop"] - s["entry"])
        end = min(t + 2 * lookback, len(bars) - 1)
        reason, ex, px = None, None, None
        for j in range(t + 1, end + 1):
            h, l = bars[j][2], bars[j][3]
            hit_stop = h >= s["stop"] if short else l <= s["stop"]
            hit_tgt = l <= s["target"] if short else h >= s["target"]
            if hit_stop:
                reason, ex, px = "stop", j, s["stop"]
            elif hit_tgt:
                reason, ex, px = "target", j, s["target"]
            if reason:
                break
        if reason is None:
            if end < t + 2 * lookback:
                continue  # data ended before the cap: unresolved, not counted
            reason, ex, px = "cap", end, bars[end][4]
        busy_until = ex
        if any(bars[i + 1][0] - bars[i][0] != iv_ms for i in range(s["a"], ex)):
            continue
        move = (s["entry"] - px) if short else (px - s["entry"])
        trades.append({"t": t, "side": s["side"], "entry": s["entry"], "stop": s["stop"], "target": s["target"],
                       "exit": ex, "reason": reason, "net_r": (move - COST * s["entry"]) / risk})
    return trades
