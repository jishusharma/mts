"""Pre-backtest checks for Eagle_Eyes studies (operator 10-31: "look at the bugs that we have found so far. What are the patterns?
And then do a testing around it before you even attempt the backtesting").
Each check targets a bug class that already bit us; a study result is not reported until its checks pass.
  P1 data coverage   resampled bars vs the span (C27 1h/2h/4h silently lost ~half the bars to an alignment bug)
  P2 prefix test     indicator / trend at bar i is identical when computed on bars[:i+1] only (look-ahead, unconfirmed pivots: WT C1)
  P3 twin variants   (n >= 5) different rules or exits must not give identical trade lists (C28 counter-trend exit fired on bar 1 for all 4 exits)
  P4 hold degeneracy (n >= 5) median hold of 1 bar or one hold value for all trades = an exit firing at once
  P5 rarity          a rule with n < 30 in 2.5 years is unreachable as written (C28 red-band sell dots in downtrends: n=5)
  P6 fee identity    net = gross - BINANCE_TAKER*2, re-derived from prices outside the study code
  P7 overlap         no two trades of one rule open at the same time unless the rule says so
  P8 random entries  the same exit on random entries of the same count and side; the signal must beat it, else the exit made the result
Research only, no orders. Usage: python bt_preflight.py <repo>"""
import os, random, statistics as st, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavetrend_dots as WD
import wt_context as WC

FAILS = []


def check(name, ok, detail):
    print("%-4s %-60s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        FAILS.append(name)


def p1_coverage():
    span = (WD.R15[-1][0] - WD.R15[0][0]) // 900000 + 1
    check("P1 15m bars vs span", len(WD.R15) >= 0.995 * span, "%d of %d" % (len(WD.R15), span))
    for tf, k in (("1h", 4), ("2h", 8), ("4h", 16)):
        n = len(WD.agg(k))
        check("P1 %s bars vs span" % tf, n >= 0.99 * span / k, "%d of %d" % (n, span // k))


def p2_prefix(k=8, cuts=25):
    b = WD.agg(k); w1, w2 = WD.wavetrend(b); tr = WC.structure(b)
    rnd = random.Random(7); bad = 0
    for i in rnd.sample(range(300, len(b) - 1), cuts):
        pw1, pw2 = WD.wavetrend(b[:i + 1]); ptr = WC.structure(b[:i + 1])
        bad += abs(pw1[-1] - w1[i]) > 1e-9 or abs(pw2[-1] - w2[i]) > 1e-9 or ptr[-1] != tr[i]
    check("P2 prefix: WT and trend at bar i use bars <= i only", bad == 0, "%d of %d cut points differ" % (bad, cuts))


def sig(tr):
    return [(r["t"], r["bars"], round(r["net"], 6)) for r in tr]


def p3_to_p8():
    for tf, k in (("1h", 4), ("2h", 8), ("4h", 16)):
        b = WD.agg(k); O = [x[1] for x in b]; T = {x[0]: j for j, x in enumerate(b)}
        for rule in WC.RULES:
            runs = [WC.trades(tf, k, rule, ex) for ex in range(4)]
            tag = "%s %s" % (tf, rule[0])
            twins = [(a, c) for a in range(4) for c in range(a + 1, 4) if len(runs[a]) >= 5 and sig(runs[a]) == sig(runs[c])]
            check("P3 twins " + tag, not twins, "identical exits %s" % twins if twins else "4 exits differ")
            for ex, x in enumerate(runs):
                if not x:
                    continue
                hb = [r["bars"] for r in x]
                if ex == 0:
                    check("P5 rarity " + tag, len(x) >= 30, "n=%d" % len(x))
                if len(x) >= 5:
                    check("P4 hold %s X%d" % (tag, ex + 1), st.median(hb) > 1 and len(set(hb)) > 1, "median %s bars, %d distinct" % (st.median(hb), len(set(hb))))
                worst = 0.0
                for r in x:
                    j = T[r["t"]]; e = j + r["bars"]  # entry bar j, exit at the open after bar j+bars-1
                    gross = r["d"] * (O[e] / O[j] - 1) * 100 if e < len(O) else None
                    if gross is not None:
                        worst = max(worst, abs(r["net"] - (gross - WD.FEE)))
                check("P6 fee identity %s X%d" % (tag, ex + 1), worst < 1e-6, "max gap %.2e" % worst)
                ov = sum(1 for a, c in zip(x, x[1:]) if T[c["t"]] < T[a["t"]] + a["bars"])
                check("P7 overlap %s X%d" % (tag, ex + 1), ov == 0, "%d overlaps" % ov)
            p8_random(tf, k, rule, runs[2])


def p8_random(tf, k, rule, real, draws=30):
    """Same exit X3, random entry bars in the same trend state; reports where the real mean sits."""
    if len(real) < 30:
        return
    b = WD.agg(k); w1, w2 = WD.wavetrend(b); tr = WC.structure(b); name, need, side, _ = rule
    pool = [i for i in range(100, len(b) - 2) if tr[i] == need]
    rnd = random.Random(11); means = []
    for _ in range(draws):
        v = [WC.forward_trade(b, w1, w2, tr, i, side, 2, guard=need == side) for i in rnd.sample(pool, len(real))]
        means.append(st.mean(r["net"] for r in v if r))
    m = st.mean(r["net"] for r in real); beat = sum(m > q for q in means)
    print("INFO P8 random entries %s %s X3: real %+.3f%% vs random median %+.3f%%, beats %d/%d" % (tf, name, m, st.median(means), beat, draws))


if __name__ == "__main__":
    p1_coverage(); p2_prefix(); p3_to_p8()
    print("FAILS: %d %s" % (len(FAILS), FAILS[:12]))
