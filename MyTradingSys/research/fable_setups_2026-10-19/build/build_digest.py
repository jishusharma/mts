"""Write pack/RULES_DIGEST.md. Every quote is asserted to be a substring of the cited file:line (whitespace-normalised),
so the digest cannot drift from its sources. Usage: python build_digest.py <pack_dir>"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
F = {
 "V2": "MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md",
 "SR": "MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md",
 "TV": "MyTradingSys/research/TOM_VERBATIM_INDEX.md",
 "FR": "MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md",
 "FM": "MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md",
 "LY": "MyTradingSys/system/LAYERS.md",
}
N = lambda s: " ".join(s.split())
TOM = [
 ("Balance and value", [
  ("TV", 43, "where the market is in balance, everyone is satisfied. And where the market is out of balance, there is often dissatisfaction among the big players."),
  ("TV", 44, "when supply and demand are balanced, the market will always try to return to that equilibrium."),
  ("TV", 46, "balance profile means the probability is high for now that the market will repeatedly try to play in balance."),
  ("TV", 48, "if you see that a market has spent a lot of time at a certain price range, the probability is relatively high that a lot of trades have also taken place there."),
  ("TV", 59, "markets are only about 30% truly stably trending. And about 70% they're just not."),
  ("TV", 71, "when such a balance profile comes after a strong trend, then it means the market is starting to sort itself out."),
 ]),
 ("Weekly POC and value trend (HTF context)", [
  ("TV", 54, "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling"),
  ("TV", 66, "try drawing a trend based only on the V POX and the value areas and you'll find that you can immediately see if a market is flattening out in terms of global money flow or not."),
  ("TV", 77, "Where are we in balance or are we currently in an active aggressive trend?"),
  ("TV", 78, "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial."),
  ("V2", 60, "we are of course above the previous day. That means it's a very risky trade"),
  ("V2", 60, "we're above last week's value"),
 ]),
 ("Rejection, acceptance, targets at value", [
  ("TV", 23, "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me."),
  ("TV", 31, "if it accepts new prices, then it looks for the next high volume price and that is your target."),
  ("TV", 32, "Not with quick spikes but with real acceptance."),
  ("TV", 26, "When there are high volumes at the tops or lows, the auctions are very often not yet finished, not yet completed."),
  ("V2", 102, "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur"),
  ("V2", 101, "we'll take out the entire distance below the start of the impulse"),
  ("V2", 138, "if the market were to accumulate large volumes there then yes I would definitely be looking for a long position"),
  ("SR", 16, "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas."),
  ("SR", 21, "this trend isn't entirely healthy."),
  ("SR", 24, "if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend."),
 ]),
 ("Stops, risk, hit rate (Tom's own arithmetic)", [
  ("TV", 85, "my stop loss belongs below the last liquidity."),
  ("TV", 104, "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three"),
  ("V2", 27, "have a hit rate somewhere in the range of 40 to 45% with such counter trading"),
  ("V2", 93, "my stop loss is immediately above the 258"),
  ("V2", 134, "such counter trades, they often get stopped out again"),
  ("V2", 112, "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that"),
 ]),
 ("Method order", [
  ("SR", 23, "how we connect the dynamic context and then use the order flow to get the timing right."),
  ("V2", 52, "First, you have an idea. Second, you have proof that it's really time now to implement"),
 ]),
]
FAB = [
 ("Fabio model (FM lines are the supervisor's reading; quoted words are Fabio's)", [
  ("FM", 26, "if these aggressive buyers take back control, I want to be out"),
  ("FM", 24, "redistribution"),
  ("FM", 20, "risking again the profit"),
  ("FM", 21, "last point of aggression/break"),
  ("SR", 28, "see what the CVD is telling us"),
  ("SR", 28, "reaching the value area low"),
 ]),
 ("Fabio rulebook lines (rule text, FR-nn; class and data need are in the file)", [
  ("FR", 20, "Absorption: delta in, price flat; CVD divergence; heavy absorption"),
  ("FR", 21, "Absorption + reload = sustained move / entry"),
  ("FR", 15, "First entry on volume plus price confirmation"),
  ("FR", 19, "Exit when big trades stop pushing / get stopped out"),
  ("FR", 70, "No counter-trend long while CVD is falling"),
  ("FR", 74, "Flat CVD while price rises = no buyer aggression"),
  ("FR", 66, "Price above VWAP +1 SD = buyers in control"),
  ("FR", 95, "Do not trend-follow on compression days"),
  ("FR", 94, "Do not cut profit early on choppy days"),
  ("FR", 17, "Minimum 1:3 reward-to-risk on initial trades"),
  ("FR", 100, "Price rejects at the volume-defined FVG"),
  ("FR", 150, "is proprietary/undefined"),
  ("FR", 151, "has no numeric threshold."),
  ("FR", 152, "has no numeric threshold."),
 ]),
]
FAILED = [
 ("LY", 13, "STOP: do not backtest or tune the current BTC encoding", "tom_core: stopped, being redefined"),
 ("LY", 23, "no edge: gross -0.07 R, net -0.30 R, holdout net -0.32 R (n=254)", "TOM-CORE-0929"),
 ("LY", 21, "no edge: gross -0.15 R, net -2.91 R; holdout -2.80 R", "TOM-CORE-1007"),
 ("LY", 15, "closed: no anchor beats placebo", "tom_vp_pivot (VP anchors)"),
 ("LY", 19, "no anchor has an edge; 46/48 real-minus-placebo CIs straddle 0; every year negative", "TOM-VP-PHASE2"),
 ("LY", 20, "negative net R; no level beats placebo", "VP-PIVOT-P2"),
 ("LY", 43, "OOS FAIL (only model C evaluable, 79 trades, mean -0.1038R)", "Fabio v3"),
 ("LY", 45, "L1 no edge / insufficient n", "fabio_cvd_absorption"),
 ("LY", 46, "L1 no edge / insufficient n", "fabio_escalation"),
 ("LY", 53, "no edge / insufficient n (stands under correct fees", "FABIO-OF"),
 ("LY", 51, "NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m", "PRICE-CVD-DIV-1M5M"),
]
NOSRC = [
 ("SR", 43, "Bollinger bands as a trigger or level | NO-SOURCE"),
 ("SR", 48, "Every numeric threshold (percentiles, windows, 1.5x volume) | NO-SOURCE"),
 ("SR", 44, "RSI(14) and the 40-60 regime | NO-SOURCE for Tom and Fabio"),
]


def main(pack):
    cache = {}

    def line(k, n):
        if k not in cache:
            cache[k] = open(os.path.join(ROOT, F[k]), encoding="utf-8").read().split("\n")
        return N(cache[k][n - 1])

    def chk(k, n, q):
        assert N(q) in line(k, n), f"quote not at {F[k]}:{n}: {q[:60]}"
        return f"{F[k].split('/')[-1]}:{n}"

    out = ["# RULES_DIGEST: Tom and Fabio, SOURCED quotes only (Fable run 4 pack)", "",
           "Every quote below was machine-checked as a substring of the cited file:line when this file was built",
           "(`build/build_digest.py`). Files are under `MyTradingSys/` (`research/...`, `system/LAYERS.md`).",
           "Tom's words are AI-translated captions: a quote proves what he says he looks at, never a price or a threshold.",
           "Where a rule needs a number the source does not give, that number is OURS in your setup and you must say so.",
           "Quotes about 1m order flow, L2 or footprint cannot be used as such: the pack has 4h/12h/1d/1w bars, taker buy",
           "volume and the level tables only (README).", ""]
    for title, groups in (("TOM", TOM), ("FABIO", FAB)):
        out.append(f"## {title}")
        for g, items in groups:
            out += ["", f"### {g}"]
            for k, n, q in items:
                out.append(f'- "{q}" ({chk(k, n, q)})')
        out.append("")
    out += ["## What already failed (system/LAYERS.md; do not re-propose, or say what is different)", "",
            "| Item | Result (verbatim) | file:line |", "|---|---|---|"]
    for k, n, q, who in FAILED:
        out.append(f"| {who} | {q} | {chk(k, n, q)} |")
    out += ["", "In words: TOM-CORE net -0.30 R (-2.91 R on the rerun); VP anchors (a plain touch of a VP level) show no edge over",
            "placebo; Fabio v3 OOS -0.10 R; CVD divergence adds nothing over price alone on 1m/5m.", "",
            "## NO-SOURCE list (never present these as Tom or Fabio)", ""]
    for k, n, q in NOSRC:
        out.append(f"- {q} ({chk(k, n, q)})")
    out += ["", "## Cost and R", "",
            "- Round trip cost in this pack: 14 bp (README). R cost of a trade = 14 bp / stop distance in percent.",
            "- Tom's own arithmetic: hit rate 40-45 % needs RR >= 1.5 (TOM_LAYER_V2_SPEC.md:27 above); on BTC a stop of 0.25 %",
            "  of price already costs 0.14/0.25 = 0.56 R, so tight stops cannot pass by arithmetic."]
    assert len(out) <= 250, len(out)
    with open(os.path.join(pack, "RULES_DIGEST.md"), "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("digest lines", len(out))


if __name__ == "__main__":
    main(sys.argv[1])
