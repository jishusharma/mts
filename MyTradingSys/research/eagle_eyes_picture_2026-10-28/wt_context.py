"""C28: WaveTrend inside market structure (operator 10-31): in a downtrend sell the WT top (sell dot in the red band),
buy only on a WT buy dot; exit where history says (four exits compared, chosen AFTER seeing them = in-sample only).
WT 10/21/4, bands +-53: SOURCED (LazyBear). Everything else OURS:
  swing high/low = highest high / lowest low of +-W bars, known W bars later (W=5)
  trend flips DOWN when a close breaks the last known swing low, UP when a close breaks the last known swing high
  entries at the next bar's open; exits at the next bar's open after the exit bar; trend flip against a with-trend trade = exit (counter-trend buys exit on the WT rule or the cap only)
  exits: X1 wt1 crosses 0 | X2 wt1 reaches the far band (+-53) | X3 first opposite dot after the far band | X4 first opposite dot
  cap 60 bars. Fee BINANCE_TAKER*2. Window 2022-01..2024-06 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md).
Research only, no orders. Usage: python wt_context.py <repo>"""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavetrend_dots as WD

FEE, W, CAP = WD.FEE, 5, 60
EXITS = ("X1 centre cross", "X2 far band", "X3 dot after far band", "X4 opposite dot")


def structure(b):
    """trend[i] known at the close of bar i (+1 up, -1 down, 0 unknown)."""
    H = [x[2] for x in b]; L = [x[3] for x in b]; C = [x[4] for x in b]
    tr = [0] * len(b); sh = sl = None; s = 0
    for i in range(2 * W, len(b)):
        p = i - W  # pivot candidate confirmed now
        if H[p] == max(H[p - W:i + 1]):
            sh = H[p]
        if L[p] == min(L[p - W:i + 1]):
            sl = L[p]
        if sl is not None and C[i] < sl:
            s = -1
        elif sh is not None and C[i] > sh:
            s = 1
        tr[i] = s
    return tr


def forward_trade(b, w1, w2, tr, i, side, ex, guard=True):
    O = [x[1] for x in b]; n = len(b)
    if i + 1 >= n:
        return None
    E = O[i + 1]; far = False
    for k in range(i + 1, min(n - 1, i + 1 + CAP)):
        cross_opp = (w1[k] < w2[k] and w1[k - 1] >= w2[k - 1]) if side > 0 else (w1[k] > w2[k] and w1[k - 1] <= w2[k - 1])
        far = far or (w1[k] >= 53 if side > 0 else w1[k] <= -53)
        hit = {0: (w1[k] > 0) if side > 0 else (w1[k] < 0), 1: far, 2: far and cross_opp, 3: cross_opp}[ex]
        if hit or (guard and tr[k] == -side):
            return dict(t=b[i + 1][0], d=side, net=(side * (O[k + 1] / E - 1)) * 100 - FEE, bars=k - i,
                        why="trend flip" if (guard and tr[k] == -side and not hit) else EXITS[ex])
    k = min(n - 2, i + CAP)
    return dict(t=b[i + 1][0], d=side, net=(side * (O[k + 1] / E - 1)) * 100 - FEE, bars=k - i, why="cap")


RULES = (("Downtrend: sell dot >= 53", -1, -1, lambda w1, w2, i: w1[i] < w2[i] and w1[i - 1] >= w2[i - 1] and w1[i] >= 53),
         ("Downtrend: sell dot >= 0", -1, -1, lambda w1, w2, i: w1[i] < w2[i] and w1[i - 1] >= w2[i - 1] and w1[i] >= 0),
         ("Downtrend: buy dot <= -53", -1, 1, lambda w1, w2, i: w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -53),
         ("Uptrend: buy dot <= -53", 1, 1, lambda w1, w2, i: w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -53),
         ("Uptrend: buy dot <= 0", 1, 1, lambda w1, w2, i: w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= 0))


def trades(tf, k, rule, ex):
    b = WD.agg(k); w1, w2 = WD.wavetrend(b); tr = structure(b)
    name, need, side, cond = rule
    out, busy = [], -1
    for i in range(100, len(b) - 2):
        if i > busy and tr[i] == need and cond(w1, w2, i):
            r = forward_trade(b, w1, w2, tr, i, side, ex, guard=need == side)
            if r:
                out.append(r); busy = i + r["bars"]
    return out


HALF = 1680307200000  # 2023-04-01: two DEV halves


if __name__ == "__main__":
    for tf, k in (("1h", 4), ("2h", 8), ("4h", 16)):
        for rule in RULES:
            for ex in range(4):
                x = trades(tf, k, rule, ex)
                if len(x) < 5:
                    continue
                v = [r["net"] for r in x]; a = [r["net"] for r in x if r["t"] < HALF]; c = [r["net"] for r in x if r["t"] >= HALF]
                t = st.mean(v) / (st.stdev(v) / len(v) ** 0.5) if len(v) > 1 and st.stdev(v) else 0
                print("%s|%s|%s|%d|%.0f|%+.3f|%+.1f|%+.2f|%s|%s|%.0f" % (tf, rule[0], EXITS[ex], len(v), 100 * sum(q > 0 for q in v) / len(v), st.mean(v), sum(v), t,
                      "%+.3f(%d)" % (st.mean(a), len(a)) if a else "-", "%+.3f(%d)" % (st.mean(c), len(c)) if c else "-", st.mean(r["bars"] for r in x)))
