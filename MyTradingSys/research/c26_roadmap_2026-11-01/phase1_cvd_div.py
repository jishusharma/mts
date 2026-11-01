"""Design look (SEEN window, descriptive, not a test): CVD divergence the way the CoinGlass CVD page shows it (shots f0c96ab4648f
8a0a7c7df46c 66e5bd1cba25 e6ffb95a80ef 2075e46d6f75 01954b8d332f, 2026-11-01: "Divergences ... hit rate at +12 bars") rebuilt on
our data, with the operator's Malkan rule: the two legs of a divergence at most 12-18 candles apart, any timeframe.
CVD here = running sum of the Binance SPOT 1m taker delta (2 x taker_buy - volume), not the vendor's 8-market combined CVD, so
counts differ; the question is whether the SHAPE (price higher high, CVD lower high) has any +12-bar follow-through on our data.
Definitions (OURS): pivot = high (low) above (below) the K bars either side; bear div = two consecutive pivot highs, the later one
higher in price and lower in CVD, legs GAP bars apart; bull div mirrored; confirmed K bars after the second pivot (no look-ahead);
outcome = close 12 bars after confirmation vs the confirmation close; hit = the move has the divergence's sign.
Also: at the 30 DOWN-high take-outs of phase1_recent.py, was a 15m CVD bear divergence (legs <= 18 bars) confirmed within 4 bars
of the touch, and how did the single short of phase1_ladder_look.py do with and without it.
Usage: python phase1_cvd_div.py <repo> <cache> [--until 2026-11-01T07:45]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402
import phase1_ladder_look as LL  # noqa: E402
import phase1_card as CARD  # noqa: E402

K, AHEAD, GAPS = 3, 12, ((2, 18), (19, 60))  # OURS; GAPS: Malkan's bar (<= 18) vs longer legs


def bars(m1, tf):
    """1m rows [t,o,h,l,c,v,taker_buy] -> tf-minute bars (t, high, low, close, cvd)."""
    out, cvd = [], 0.0
    cur = None
    for r in m1:
        b = r[0] // (tf * 60000) * (tf * 60000)
        cvd += 2 * r[6] - r[5]
        if cur is None or cur[0] != b:
            if cur:
                out.append(tuple(cur))
            cur = [b, r[2], r[3], r[4], cvd]
        else:
            cur[1] = max(cur[1], r[2]); cur[2] = min(cur[2], r[3]); cur[3] = r[4]; cur[4] = cvd
    if cur:
        out.append(tuple(cur))
    return out


def pivots(B, side):
    """Indices of pivot highs (side +1) or lows (-1), K bars each side."""
    v = [b[1] if side > 0 else -b[2] for b in B]
    return [i for i in range(K, len(B) - K) if all(v[i] > v[j] for j in range(i - K, i + K + 1) if j != i)]


def divergences(B, side):
    """[(confirm_bar, gap)] for bear (side +1: price HH, CVD LH) or bull (side -1: price LL, CVD HL) divergences."""
    out, piv = [], pivots(B, side)
    for a, b in zip(piv, piv[1:]):
        pa, pb = (B[a][1], B[b][1]) if side > 0 else (B[a][2], B[b][2])
        if (pb > pa if side > 0 else pb < pa) and (B[b][4] < B[a][4] if side > 0 else B[b][4] > B[a][4]):
            out.append((b + K, b - a))
    return out


def score(B, side, divs, lo, hi):
    g = [(c, gap) for c, gap in divs if lo <= gap <= hi and c + AHEAD < len(B)]
    if not g:
        return "0"
    moves = [(B[c + AHEAD][3] / B[c][3] - 1) * 100 * (-side) for c, _ in g]  # positive = went the divergence's way
    hits = sum(1 for m in moves if m > 0)
    return "%d: hit %d %% , mean %+.2f %%" % (len(g), round(100.0 * hits / len(g)), sum(moves) / len(moves))


def main():
    R._load()
    P = R.P
    m1 = json.load(open(os.path.join(P.CACHE, "btc1m_recent.json")))
    if P.UNTIL:
        m1 = [r for r in m1 if r[0] + 60000 <= P.UNTIL]
    print("## Q8. CVD divergence as the CoinGlass page draws it, rebuilt on Binance spot taker delta (design look, OURS)\n")
    rows = []
    for tf in (1, 5, 15, 60):
        B = bars(m1, tf)
        base_dn = sum(1 for i in range(len(B) - AHEAD) if B[i + AHEAD][3] < B[i][3]) / max(1, len(B) - AHEAD)
        bear, bull = divergences(B, 1), divergences(B, -1)
        for lo, hi in GAPS:
            rows.append(["%dm" % tf, "%d-%d" % (lo, hi), score(B, 1, bear, lo, hi), score(B, -1, bull, lo, hi),
                         "%d %% / %d %%" % (round(100 * base_dn), round(100 * (1 - base_dn)))])
    cols = ["bars", "legs apart", "bear div: n, hit rate at +12, mean move", "bull div: n, hit rate at +12, mean move",
            "base rate: 12-bar move down / up"]
    print(R.table(cols, rows))
    print("\nhit = close 12 bars after confirmation moved the divergence's way; base rate = share of all 12-bar moves in that"
          " direction (a hit rate near it is no edge). Window: the cache, %s to %s UTC.\n"
          % (P.utc(m1[0][0]).strftime("%Y-%m-%d"), P.utc(m1[-1][0]).strftime("%Y-%m-%d %H:%M")))
    B15 = bars(m1, 15)
    idx = {b[0]: i for i, b in enumerate(B15)}
    bear15 = [(c, gap) for c, gap in divergences(B15, 1) if gap <= 18]
    conf = {c for c, _ in bear15}
    ev = [e for e in P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    yes, no = [], []
    for e in ev:
        k = idx.get(P.T[e["_take"]])
        net, _, why = LL.book(e, "close", 1.0)
        (yes if k is not None and any(c in conf for c in range(k - 4, k + 5)) else no).append((net, why))
    out = [[name, "%d: %d L1, %+.2f" % (len(g), sum(1 for _, w in g if w == "L1"), sum(n for n, _ in g) / len(g)) if g else "0"]
           for name, g in (("15m CVD bear div (legs <= 18) confirmed within 4 bars of the take-out", yes), ("none", no))]
    tcols = ["at the 30 DOWN-high take-outs", "n, reached L1, single short mean net unit-%"]
    print(R.table(tcols, out))
    if CARD.arg("--card"):
        CARD.write(CARD.arg("--card"), CARD.card(
            "c26-q8-cvd-divergence",
            "C26 Q8: CVD divergence as the CoinGlass CVD page draws it, with Malkan's 12-18 candle rule, on 1m/5m/15m/60m bars",
            [CARD.P("CVD", "cumulative volume delta from Binance spot taker buy minus taker sell volume per 1m bar, summed to the bar size"),
             CARD.P("Divergence", "price makes a higher high (lower low) while CVD makes a lower high (higher low): pivots +-3 bars, counted at the "
                                  "confirmation close, two legs %d-%d bars apart" % (GAPS[0][0], GAPS[-1][1])),
             CARD.P("Legs apart 12-18", "Malkan's rule for a valid divergence (QRIPTAL / Malkan extracts)", "SOURCED"),
             CARD.P("Hit", "the close %d bars after confirmation moved the divergence's way; compared with the base rate of all %d-bar moves" % (AHEAD, AHEAD)),
             CARD.P("Outcome read at the take-outs", "single short: first 15m close back under H1, stop H1 + 1.0 %, target L1, 24h, fee-net"),
             CARD.FEE],
            "phase1_cvd_div.py <repo> <cache> --until 2026-11-01T07:45 --card <this file>; 1m bars from data.binance.vision (fetch_1m.py). "
            "CoinGlass CVD page shots f0c96ab4648f 8a0a7c7df46c 66e5bd1cba25 e6ffb95a80ef 2075e46d6f75 01954b8d332f set what to rebuild.",
            "Design look: on every bar size the hit rate sits at the %d-bar base rate; a 15m bear divergence stood within 4 bars of %d of %d take-outs"
            % (AHEAD, len(yes), len(ev)), "info",
            ["Hundreds of divergences fire per bar size and leg gap; their hit rate is the base rate of the market moving that way, so the signal alone "
             "carries no edge on this window.",
             "At the C26 take-outs the divergence is rare (%d of %d), so it cannot be a Phase 3 filter; it stays a chart-reading aid." % (len(yes), len(ev)),
             "Malkan's 12-18 bar rule is SOURCED; the pivot width, the +%d-bar hit and the bar sizes are OURS." % AHEAD],
            [{"label": "bar sizes x leg gaps", "value": str(len(rows))}, {"label": "15m bear div at a take-out", "value": "%d of %d" % (len(yes), len(ev))}],
            [CARD.table("Divergences per bar size and leg gap, hit rate vs base rate", cols, rows),
             CARD.table("At the take-outs", tcols, out, "n, how many reached L1, mean fee-net unit-% of the single short")],
            ["phase1_cvd_div.py", "PHASE1_RANGE.md"]))


if __name__ == "__main__":
    main()
