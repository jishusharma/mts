"""C30: WaveTrend dots WITH RSI divergence confluence (operator 10-31: "did you use RSI Confluence for selling at the top with divergence
and buying at the bottom with divergence ... when you were testing the wavetrend"). C28/C29 did not; this adds it.
RSI 14 (Wilder) and WT 10/21/4: SOURCED. Divergence rule OURS, known at the close of bar i:
  bearish: p = highest high of bars i-40..i-8, q = highest high of bars i-7..i; H[q] > H[p], RSI[q] < RSI[p], RSI[p] >= 60
  bullish: mirror with lows, RSI[p] <= 40
Signals: sell dot (wt1 >= 0, or >= 53 'red band') + bearish divergence; buy dot (wt1 <= 0, or <= -53) + bullish divergence;
each with trend = any / same-chart structure / last closed 2h structure. Exits X1-X4 as wt_context.py, cap 60 bars, fee BINANCE_TAKER*2.
Window 2022-01..2024-06 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md). Research only, no orders. Usage: python wt_rsi_div.py <repo>"""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavetrend_dots as WD
import wt_context as WC
import wt_lower_tf as LT

CAP, FEE = WC.CAP, WD.FEE


def rsi(C, n=14):
    out = [50.0] * len(C); g = l = 0.0
    for i in range(1, len(C)):
        d = C[i] - C[i - 1]; up, dn = max(d, 0), max(-d, 0)
        if i <= n:
            g += up / n; l += dn / n
        else:
            g = (g * (n - 1) + up) / n; l = (l * (n - 1) + dn) / n
        if i >= n:
            out[i] = 100 - 100 / (1 + g / l) if l else 100.0
    return out


def divergence(H, L, R, i, side):
    """side -1 = bearish (for shorts), +1 = bullish (for longs). Uses bars <= i only."""
    if i < 40:
        return False
    if side < 0:
        p = max(range(i - 40, i - 7), key=lambda m: H[m]); q = max(range(i - 7, i + 1), key=lambda m: H[m])
        return H[q] > H[p] and R[q] < R[p] and R[p] >= 60
    p = min(range(i - 40, i - 7), key=lambda m: L[m]); q = min(range(i - 7, i + 1), key=lambda m: L[m])
    return L[q] < L[p] and R[q] > R[p] and R[p] <= 40


def forward_trade(O, w1, w2, tr, i, side, ex, guard, T):
    n = len(O)
    if i + 1 >= n:
        return None
    E = O[i + 1]; far = False
    for k in range(i + 1, min(n - 1, i + 1 + CAP)):
        opp = (w1[k] < w2[k] and w1[k - 1] >= w2[k - 1]) if side > 0 else (w1[k] > w2[k] and w1[k - 1] <= w2[k - 1])
        far = far or (w1[k] >= 53 if side > 0 else w1[k] <= -53)
        hit = ((w1[k] > 0) if side > 0 else (w1[k] < 0), far, far and opp, opp)[ex]
        if hit or (guard and tr[k] == -side):
            return dict(t=T[i + 1], d=side, net=side * (O[k + 1] / E - 1) * 100 - FEE, bars=k - i)
    k = min(n - 2, i + CAP)
    return dict(t=T[i + 1], d=side, net=side * (O[k + 1] / E - 1) * 100 - FEE, bars=k - i)


SIG = (("sell dot >= 0 + bear div", -1, 0), ("sell dot >= 53 + bear div", -1, 53),
       ("buy dot <= 0 + bull div", 1, 0), ("buy dot <= -53 + bull div", 1, 53))


def run(b, mins):
    O = [x[1] for x in b]; H = [x[2] for x in b]; L = [x[3] for x in b]; C = [x[4] for x in b]; T = [x[0] for x in b]
    w1, w2 = WD.wavetrend(b); R = rsi(C)
    trends = {"any": [0] * len(b), "same": WC.structure(b), "2h": LT.htf_trend(b, mins) if mins < 120 else WC.structure(b)}
    res = []
    for name, side, lvl in SIG:
        fires = [i for i in range(100, len(b) - 2)
                 if ((w1[i] < w2[i] and w1[i - 1] >= w2[i - 1] and w1[i] >= lvl) if side < 0 else
                     (w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -lvl)) and divergence(H, L, R, i, side)]
        for src, tr in trends.items():
            need = 0 if src == "any" else side  # with-trend only: shorts in downtrends, longs in uptrends
            for ex in range(4):
                out, busy = [], -1
                for i in fires:
                    if i > busy and (need == 0 or tr[i] == need):
                        r = forward_trade(O, w1, w2, tr, i, side, ex, need != 0, T)
                        if r:
                            out.append(r); busy = i + r["bars"]
                res.append((name, src, WC.EXITS[ex], out))
    return res


if __name__ == "__main__":
    charts = [("10m", LT.agg5(2), 10), ("15m", LT.agg5(3), 15), ("30m", LT.agg5(6), 30), ("1h", WD.agg(4), 60), ("2h", WD.agg(8), 120), ("4h", WD.agg(16), 240)]
    for tf, b, mins in charts:
        for name, src, ex, x in run(b, mins):
            if tf in ("2h", "4h") and src == "2h":
                continue
            if len(x) < 2:
                print("%s|%s|%s|%s|%d" % (tf, name, src, ex, len(x))); continue
            v = [r["net"] for r in x]; a = [q for r, q in zip(x, v) if r["t"] < WC.HALF]; c = [q for r, q in zip(x, v) if r["t"] >= WC.HALF]
            t = st.mean(v) / (st.stdev(v) / len(v) ** 0.5) if st.stdev(v) else 0
            print("%s|%s|%s|%s|%d|%.0f|%+.3f|%+.2f|%s|%s" % (tf, name, src, ex, len(v), 100 * sum(q > 0 for q in v) / len(v), st.mean(v), t,
                  "%+.3f(%d)" % (st.mean(a), len(a)) if a else "-", "%+.3f(%d)" % (st.mean(c), len(c)) if c else "-"))
