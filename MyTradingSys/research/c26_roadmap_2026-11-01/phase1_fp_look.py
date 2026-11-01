"""Design look (SEEN window, descriptive, not a test): the CoinGlass Footprint page (shots c0a8fc721e58 aggregated, 82d84b32fe1a
Binance perp, 4H, 2026-11-01) rebuilt as far as our data allows, at the 30 DOWN-high take-outs of phase1_recent.py. A footprint
cell is bid x ask volume per price row per bar; the page's signals are imbalance (one side >= 300 % of the other on the diagonal),
absorption (heavy selling at a low that does not break) and unfinished auction (volume stacked at the bar's top or bottom).
We have no bid/ask per price row; the proxy (OURS) assigns each Binance SPOT 1m bar's taker delta (2 x taker_buy - volume) to the
price row of its close (100 USD rows) over the excursion above H1 (take-out bar to the excursion high):
  top delta   = taker delta of the rows in the top quarter of the excursion's range (who won the auction at the high)
  top share   = volume share of that top quarter (stacked top = "unfinished auction top" in the page's words)
  POC pos     = where the excursion's point of control sits, 0 = at the low, 1 = at the high
  sell imb    = rows in the top quarter where taker sells >= 3 x taker buys (the page's 300 % ratio, per row, not diagonal)
Split against the single short of phase1_ladder_look.py (enter at the first close back under H1, stop 1 %, target L1, 24h).
Usage: python phase1_fp_look.py <repo> <cache> [--until 2026-11-01T07:45]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_range as R  # noqa: E402
import phase1_ladder_look as LL  # noqa: E402
import phase1_card as CARD  # noqa: E402

ROW, TOPQ, IMB = 100.0, 0.25, 3.0  # OURS


def main():
    R._load()
    P = R.P
    m1 = json.load(open(os.path.join(P.CACHE, "btc1m_recent.json")))
    if P.UNTIL:
        m1 = [r for r in m1 if r[0] + 60000 <= P.UNTIL]
    by_t = {r[0]: r for r in m1}
    ev = [e for e in P.run(1) if e["_take"] is not None and e["phase"] == "DOWN"]
    rows, recs = [], []
    for e in ev:
        take, lvl = e["_take"], e["h1"]
        x = R.excursion(e)
        ext = take + x["exc_bars"]
        mins = [by_t[t] for k in range(take, ext + 1) for t in range(P.T[k], P.T[k] + P.TF, 60000) if t in by_t]
        if not mins:
            continue
        hi, lo = max(r[2] for r in mins), min(r[3] for r in mins)
        cut = hi - TOPQ * (hi - lo)
        vol = sum(r[5] for r in mins) or 1.0
        top = [r for r in mins if r[4] >= cut]
        top_d = sum(2 * r[6] - r[5] for r in top)
        top_share = sum(r[5] for r in top) / vol
        prof, buy, sell = {}, {}, {}
        for r in mins:
            b = int(r[4] // ROW)
            prof[b] = prof.get(b, 0.0) + r[5]
            buy[b] = buy.get(b, 0.0) + r[6]; sell[b] = sell.get(b, 0.0) + (r[5] - r[6])
        poc = max(prof, key=prof.get) * ROW
        poc_pos = (poc - lo) / (hi - lo) if hi > lo else 0.5
        imb = sum(1 for b in prof if b * ROW >= cut and buy[b] > 0 and sell[b] >= IMB * buy[b])
        net, _, why = LL.book(e, "close", 1.0)
        recs.append(dict(net=net, why=why, top_d=top_d, top_share=top_share, poc_pos=poc_pos, imb=imb))
        rows.append([P.utc(P.T[take]).strftime("%m-%d %H:%M"), "%.0f" % lvl, "%d" % (ext - take + 1), "%+.1f" % top_d,
                     "%.0f %%" % (100 * top_share), "%.2f" % poc_pos, str(imb), "%+.2f %s" % (net, why)])
    print("## Q9. Footprint proxy over the excursion above H1 at the DOWN-high take-outs (design look, OURS, n=%d)\n" % len(recs))
    cols = ["take-out (UTC)", "H1", "excursion bars", "top-quarter taker delta (BTC)", "top-quarter volume share",
            "POC position (0 low, 1 high)", "sell-imbalance rows at top", "single short net, exit"]
    print(R.table(cols, rows))
    facts = (("top-quarter delta negative (sellers won the high)", lambda r: r["top_d"] < 0),
             ("top-quarter volume share >= 35 % (stacked top)", lambda r: r["top_share"] >= 0.35),
             ("POC in the lower half (top rejected)", lambda r: r["poc_pos"] < 0.5),
             ("a sell-imbalance row at the top", lambda r: r["imb"] > 0))
    out = []
    for name, f in facts:
        cells = []
        for want in (True, False):
            g = [r for r in recs if f(r) == want]
            cells.append("%d: %d L1, %+.2f" % (len(g), sum(1 for r in g if r["why"] == "L1"), sum(r["net"] for r in g) / len(g)) if g else "0")
        out.append([name] + cells)
    print()
    fcols = ["footprint fact over the excursion", "yes: n, reached L1, mean net unit-%", "no: n, reached L1, mean net unit-%"]
    print(R.table(fcols, out))
    if CARD.arg("--card"):
        sellers = sum(1 for r in recs if r["top_d"] < 0)
        imbs = sum(1 for r in recs if r["imb"] > 0)
        CARD.write(CARD.arg("--card"), CARD.card(
            "c26-q9-footprint",
            "C26 Q9: a footprint proxy over the excursion above H1 (taker delta per 100 USD row) at the DOWN-high take-outs",
            [CARD.P("Events", "C26 held highs taken out in a DOWN phase (phase1_recent.py), 15m Binance spot BTCUSDT"),
             CARD.P("Footprint proxy", "1m bars of the excursion above H1 binned into %.0f USD rows by close: taker buy and taker sell volume per row "
                                       "(a footprint chart has this per price level per bar; the 1m close is the proxy)" % ROW),
             CARD.P("Top quarter", "rows in the top %.0f %% of the excursion's high-low range" % (100 * TOPQ)),
             CARD.P("Sell-imbalance row", "sell volume >= %.0fx buy volume in a top-quarter row (footprint '300 %%' rule)" % IMB),
             CARD.P("Outcome read", "single short: first 15m close back under H1, stop H1 + 1.0 %, target L1, 24h, fee-net"),
             CARD.FEE],
            "phase1_fp_look.py <repo> <cache> --until 2026-11-01T07:45 --card <this file>; 1m bars from data.binance.vision (fetch_1m.py). "
            "CoinGlass Footprint 4H shots c0a8fc721e58 (aggregated) and 82d84b32fe1a (Binance perp) set what to rebuild.",
            "Design look on SEEN, n=%d: buyers won the top quarter in %d of %d (taker delta positive); %d take-outs had a sell-imbalance row at the top"
            % (len(recs), len(recs) - sellers, len(recs), imbs), "info",
            ["The high of a take-out is made by buyers lifting offers, so a positive top-quarter delta is the normal case, not a tell.",
             "A footprint 'absorption' read needs sellers winning the top rows; it almost never shows here, so it is no Phase 3 filter.",
             "The CoinGlass page's 'Absorption bullish' label is its bottom signal and was stale (fired before the 82k top), not a top signal."],
            [{"label": "take-outs", "value": str(len(recs))}, {"label": "buyers won the top quarter", "value": "%d of %d" % (len(recs) - sellers, len(recs))},
             {"label": "sell-imbalance row at the top", "value": str(imbs)}],
            [CARD.table("The take-outs, footprint proxy over the excursion", cols, rows, "no prices: the H1 column is dropped on this page"),
             CARD.table("Each footprint fact split yes / no", fcols, out, "n, how many reached L1, mean fee-net unit-% of the single short")],
            ["phase1_fp_look.py", "PHASE1_RANGE.md"]))


if __name__ == "__main__":
    main()
