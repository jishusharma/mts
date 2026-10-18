"""Angle (b): trader's-eye check at 12 seeded random DEV decision points. For each point the script writes, from the raw
bars by hand (indep_pandas.py), what a trader sees at that minute: the last closed D/12h/8h/4h candles, the partial daily
candle, the nearest support and resistance with their sources, the phase and the Bollinger state; then the builder's
row for the same minute, and every disagreement. Seed fixed (OURS) before any row was read.

  python trader_eye.py          -> trader_eye.md
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import context_asof as CA      # noqa: E402
import indep_pandas as IP      # noqa: E402
import hand_check as HC        # noqa: E402

SEED = 20261016
N_POINTS = 12
CHECK = ["c_1d", "c_12h", "c_8h", "c_4h", "p_1d", "near_price", "near_src", "n_layers", "phase_a", "bb_4h_state", "bb_1d_state",
         "ladder_rung", "ladder_stop_pct", "pat_4h", "pat_1d", "intraday", "vol_regime", "session", "funding"]


def candle_words(c):
    if c is None:
        return "none"
    o, h, l, cl = c
    col = "green" if cl > o else "red" if cl < o else "doji"
    return f"O {o:.1f} H {h:.1f} L {l:.1f} C {cl:.1f} ({col}, range {h - l:.1f})"


def main():
    rng = np.random.default_rng(SEED)
    # grid points after the first 70 days (every factor populated) up to the DEV end
    ks = rng.choice(np.arange(70 * 24, CA.N_DEV // 60), size=N_POINTS, replace=False)
    ks.sort()
    bars = CA.load_dev(cache=HC.CACHE)
    fund = CA.load_funding()
    V = CA.VecTables(bars, fund)
    out = [f"# Angle (b): trader's-eye check at {N_POINTS} seeded random DEV decision points (seed {SEED})", "",
           "Each block: what a trader sees at that minute, computed by hand from the raw bars (pandas), then the builder's row and",
           "the disagreements on the checked fields. Both sides are shown for the nearest level; the random side is the one checked.", ""]
    n_bad = 0
    findings = []
    for k in ks:
        t = int(k) * 60 + 59
        side = "long" if rng.random() < 0.5 else "short"
        df = IP.bars_upto(t)
        h = IP.hand_context(t, side, df)
        other = IP.hand_context(t, "short" if side == "long" else "long", df)
        e = V.context(t, side)
        ts = IP.utc(t)
        sup = h if side == "long" else other
        res = other if side == "long" else h
        out += [f"## {ts.strftime('%Y-%m-%d %H:%M')} UTC close (t = {t}), checked side: {side}", "",
                f"- Price {h['price']:.1f}. Last closed daily: {candle_words(h['c_1d'])}. Last closed 12h: {candle_words(h['c_12h'])}.",
                f"- Last closed 8h: {candle_words(h['c_8h'])}. Last closed 4h: {candle_words(h['c_4h'])}; pattern {h['pat_4h']} (daily {h['pat_1d']}).",
                f"- Partial daily so far: {candle_words(h['p_1d'])}.",
                f"- Nearest support below: {HC.fmt(sup['near_price'])} ({sup['near_src']}, {HC.fmt(sup['near_dist_atr'])} ATR away, {sup['n_layers']} layer(s) within 0.5 ATR). "
                f"Nearest resistance above: {HC.fmt(res['near_price'])} ({res['near_src']}, {HC.fmt(res['near_dist_atr'])} ATR away, {res['n_layers']} layer(s)).",
                f"- Phase A {h['phase_a']} / phase B {h['phase_b']}; intraday {h['intraday']}; 4h Bollinger {h['bb_4h_state']} (%b {HC.fmt(h['bb_4h_pctb'])}), daily {h['bb_1d_state']}; "
                f"vol regime {h['vol_regime']}; session {h['session']}{' (weekend)' if h['weekend'] else ''}; funding {h['funding']}.",
                f"- Stop ladder ({side}): daily rung {HC.fmt(h['stop_d_pct'])} %, 12h {HC.fmt(h['stop_12_pct'])} %, 8h {HC.fmt(h['stop_8_pct'])} % -> rung {h['ladder_rung']} ({HC.fmt(h['ladder_stop_pct'])} %, cost {HC.fmt(h['ladder_cost_r'])} R).", ""]
        bad = [(f, h[f], e[f]) for f in CHECK if not HC.same(h[f], e[f])]
        out.append("Builder row: " + ", ".join(f"{f}={HC.fmt(e[f])}" for f in CHECK) + ".")
        if bad:
            n_bad += len(bad)
            out.append("**Disagreements:** " + "; ".join(f"{f}: trader {HC.fmt(a)} vs builder {HC.fmt(b)}" for f, a, b in bad))
            findings.append((t, side, bad))
        else:
            out.append("Disagreements: none.")
        out.append("")
    out += [f"**{N_POINTS} points, {n_bad} field disagreements.**", ""]
    with open(os.path.join(HERE, "trader_eye.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"{N_POINTS} points, {n_bad} disagreements -> trader_eye.md")
    for t, side, bad in findings:
        print(t, side, bad)


if __name__ == "__main__":
    main()
