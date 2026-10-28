"""MAL-BB-MID-ENGULF G5 DEV screen. Rules: PRE_REG.md (frozen before the outcome run). DEV only (bars < 2024-07-01).
Screen, ran before G3 marks by operator decision 2026-10-16.

Usage: python study.py --count   (event and arm sizes only, NO return or outcome column is computed)
       python study.py --full    (outcome run, one run, every computed cell is printed / written)
"""
import csv
import datetime as dt
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import common as K  # noqa: E402

HS = (30, 60, 120, 240)          # minutes after the entry open; primary h = 60 (OURS, = the draft's +12 bars)
PRIMARY_H = 60
COOLDOWN = 60                    # minutes between ledger events (OURS, template value)
XS = (0.0, 0.05, 0.10)           # bounce grid, share of band width (draft); primary x = 0 (wick touch of the mid)
RETEST_BARS = 12


# ---------------------------------------------------------------- rules (pure functions on bar arrays)
def _prev(x, fill):
    return np.concatenate(([fill], x[:-1]))


def engulf_a(O, C):
    """Variant (a), the operator's words: previous bar green, this bar red, close below the previous green bar's OPEN."""
    return _prev(C > O, False) & (C < O) & (C < _prev(O, np.nan))


def engulf_b(O, C):
    """Variant (b): (a) and the red bar opens at or above the previous close (classic engulf)."""
    return engulf_a(O, C) & (O >= _prev(C, np.nan))


def engulf_c(O, C, r):
    """Variant (c): (a) and body >= r x the previous body."""
    return engulf_a(O, C) & (np.abs(C - O) >= r * _prev(np.abs(C - O), np.nan))


def bounce(H, mid, width, x, win=3):
    """High of one of the last `win` bars (incl. this one) >= its own BB mid - x * band width."""
    touch = H >= mid - x * width
    out = touch.copy()
    for k in range(1, win):
        out[k:] |= touch[:-k]
    return out


def falling(mid, dl, k=10, d=6):
    """BB mid lower than k bars ago and net taker delta over the last d bars negative (OURS test of 'falling under selling pressure')."""
    prior = np.concatenate((np.full(k, np.nan), mid[:-k]))
    s = pd.Series(dl).rolling(d).sum().to_numpy()
    return (mid < prior) & (s < 0)


def htf_idx(t5, mins):
    """Index of the last CLOSED mins-minute bar when 5m bar t5 has just closed (-1 = none yet)."""
    return ((np.asarray(t5) + 1) * 5) // mins - 1


def second_break(L):
    """Bar i+1 trades below bar i's low (second confirmation after an engulf on bar i)."""
    out = np.zeros(len(L), bool)
    out[:-1] = L[1:] < L[:-1]
    return out


# ---------------------------------------------------------------- state
def build(A):
    a5, a60, a240 = K.agg(A, 5), K.agg(A, 60), K.agg(A, 240)
    lo, mid, up = K.bb(a5["C"])
    width = up - lo
    dl5 = 2.0 * a5["TBV"] - a5["V"]
    n5 = len(a5["O"])
    rsi60, rsi240 = K.rsi_wilder(a60["C"]), K.rsi_wilder(a240["C"])
    _, mid60, _ = K.bb(a60["C"])
    t5 = np.arange(n5)
    i60, i240 = htf_idx(t5, 60), htf_idx(t5, 240)
    g60, g240 = np.clip(i60, 0, None), np.clip(i240, 0, None)
    htf_on = (i60 >= 0) & (i240 >= 0) & (rsi60[g60] < 50) & (rsi240[g240] < 50) & (a5["C"] < mid60[g60])
    st = dict(a5=a5, mid=mid, width=width, dl5=dl5, htf_on=htf_on, fall=falling(mid, dl5), n5=n5,
              atr5=K.atr_sma(a5["H"], a5["L"], a5["C"], 14),
              eng={"a": engulf_a(a5["O"], a5["C"]), "b": engulf_b(a5["O"], a5["C"]), "c1": engulf_c(a5["O"], a5["C"], 1.0),
                   "c1.5": engulf_c(a5["O"], a5["C"], 1.5), "c2": engulf_c(a5["O"], a5["C"], 2.0)},
              bounce={x: bounce(a5["H"], mid, width, x) for x in XS}, sb=second_break(a5["L"]))
    return st


def tdec(idx):
    return (np.asarray(idx, np.int64) + 1) * 5 - 1          # 1m index of the last 1m bar of 5m bar idx


def ledger(mask):
    idx = np.nonzero(mask)[0]
    keep = K.cooldown_mask(tdec(idx), np.zeros(len(idx), int), COOLDOWN)
    return idx[keep]


def sets(st):
    base = st["fall"] & st["bounce"][0.0] & st["htf_on"]
    e1 = ledger(base & st["eng"]["a"])
    sb = st["sb"][e1] & (e1 + 1 < st["n5"])
    return dict(base=base, e1=e1, ctrl1=ledger(base & ~st["eng"]["a"]), e2=e1[sb], e2c=e1[~sb & (e1 + 1 < st["n5"])])


def count_text(A, st, S):
    miss = int(np.isnan(A["O"]).sum())
    base = S["base"]
    nvar = {k: len(ledger(base & v)) for k, v in st["eng"].items()}
    L = ["## Count section (no return or outcome column was computed)", "",
         f"1m bars missing on the DEV tape: {miss} of {len(A['O'])}. 5m bars {st['n5']} ({int(np.isnan(st['a5']['O']).sum())} incomplete). "
         f"Bars in a falling state {int(np.nansum(st['fall']))}; falling + wick touch of the 5m BB mid in the last 3 bars (x = 0) {int((st['fall'] & st['bounce'][0.0]).sum())}; "
         f"+ HTF filter on (1h and 4h RSI14 < 50, close below the 1h BB mid) {int(base.sum())}.",
         f"Ledger sizes after the 60-minute cooldown, bounce x = 0, HTF on: engulf (a) **n = {len(S['e1'])}**, (b) {nvar['b']}, (c) r=1 {nvar['c1']}, r=1.5 {nvar['c1.5']}, r=2 {nvar['c2']}; "
         f"control (bounce state, no engulf (a)) n = {len(S['ctrl1'])}.",
         f"Second break (next 5m bar trades below the engulf low): arm A2 n = {len(S['e2'])}; its control (engulf without the second break) n = {len(S['e2c'])}.",
         "OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed."]
    return "\n".join(L)


# ---------------------------------------------------------------- full run
def full(A, st, S):
    mdd_bh = K.S.bh_mdd(A)
    n5 = st["n5"]
    a5 = st["a5"]
    trials = []

    def gset(idx, shift, side=-1):
        t = tdec(np.asarray(idx) + shift)
        G = K.net_cells(A, t, np.full(len(t), side), HS)
        return t, G, (t + 1 + K.DELAY) // K.DAYMIN

    def arm(name, idx, shift, cidx, cshift, h, verdict=False):
        t, G, day = gset(idx, shift)
        tc, Gc, dayc = gset(cidx, cshift)
        r = K.verdict_arm(G[h], day, Gc[h], dayc, t, mdd_bh)
        trials.append([name, h, r["n"], f"{r['mean']:.5f}", f"{r['se']:.5f}", f"{r['net']:.5f}", f"{r['t_net']:.3f}", f"{r['diff']:.5f}", f"{r['t_diff']:.3f}",
                       r["verdict"] if verdict else "secondary"])
        return r if verdict else dict(r, verdict="secondary")

    A1 = arm("A1: engulf (a) close, SHORT, h=60", S["e1"], 0, S["ctrl1"], 0, PRIMARY_H, True)
    A2 = arm("A2: second break close, SHORT, h=60", S["e2"], 1, S["e2c"], 1, PRIMARY_H, True)
    sec = []
    for h in HS:
        if h != PRIMARY_H:
            sec.append((f"A1 h={h}", arm(f"A1 h={h}", S["e1"], 0, S["ctrl1"], 0, h)))
            sec.append((f"A2 h={h}", arm(f"A2 h={h}", S["e2"], 1, S["e2c"], 1, h)))
    # E3: short at the close of the first bar within 12 whose high retests the engulf-time mid
    e3 = []
    for i in S["e1"]:
        w = np.nonzero(a5["H"][i + 1:i + 1 + RETEST_BARS] >= st["mid"][i])[0]
        if len(w) and i + 1 + w[0] + 1 < n5:
            e3.append(i + 1 + w[0])
    e3 = np.array(e3, np.int64)
    sec.append(("E3 midline retest close h=60", arm("E3 midline retest close h=60", e3, 0, np.array([], np.int64), 0, PRIMARY_H)))
    # variant grid: entry E1, h=60, control not used
    grid = []
    for en in ("a", "b", "c1", "c1.5", "c2"):
        for htf in (True, False):
            for x in XS:
                m = st["fall"] & st["bounce"][x] & st["eng"][en] & (st["htf_on"] if htf else True)
                nm = f"engulf {en}, HTF {'on' if htf else 'off'}, x={x}"
                grid.append((nm, arm(nm, ledger(m), 0, np.array([], np.int64), 0, PRIMARY_H)))
    # placebo, MFE/MAE, Wilson, flow 2x2
    t1, G1, d1 = gset(S["e1"], 0)
    gp, dp, _ = K.placebo_gross(A, t1, np.full(len(t1), -1), PRIMARY_H)
    ok = ~np.isnan(gp)
    pm, ps = K.cm_se(gp[ok], dp[ok])
    exc = []
    for bars in (6, 12, 24):
        fav, adv = K.excursion(A, t1 + 1 + K.DELAY, np.full(len(t1), -1), bars * 5, st["atr5"][S["e1"]])
        exc.append([bars, int((~np.isnan(fav)).sum()), f"{np.nanmedian(fav):.2f}", f"{np.nanmedian(adv):.2f}"])
    wil = []
    for nm, idx, sh in (("A1", S["e1"], 0), ("A2", S["e2"], 1), ("control (no engulf)", S["ctrl1"], 0)):
        _, G, _ = gset(idx, sh)
        g = G[PRIMARY_H][~np.isnan(G[PRIMARY_H])]
        wil.append([nm, K.fmt_ci(int((g > 0).sum()), len(g))])
    flow = []
    e1 = S["e1"]
    for dn, dm in ((st["dl5"][e1] < 0, "engulf-bar taker delta < 0"), (st["dl5"][e1] >= 0, "engulf-bar taker delta >= 0")):
        for ex, em in ((st["width"][e1] > st["width"][np.maximum(e1 - 10, 0)], "BB width expanding"), (st["width"][e1] <= st["width"][np.maximum(e1 - 10, 0)], "BB width not expanding")):
            m = dn & ex & ~np.isnan(G1[PRIMARY_H])
            mu, se = K.cm_se(G1[PRIMARY_H][m], d1[m])
            flow.append([dm, em, int(m.sum()), f"{mu:.4f}", f"{se:.4f}"])
    word = K.headline([A1["verdict"], A2["verdict"]])
    L = [word, "",
         "# RESULT: MAL-BB-MID-ENGULF, midline bounce + bearish engulf + second break, DEV screen (primary cell 1 min extra delay, h=60, cost 0.14 % round trip)", "",
         "**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. "
         "Rules frozen in PRE_REG.md (committed before this file). SOURCED = the operator's words in the draft (close below the previous green bar's open, second break lower); "
         "every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop).", "",
         f"Study word = {word} (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: A1 {A1['verdict']}; A2 {A2['verdict']}.", "",
         "## Verdict arms (mean G % of notional after funding, SHORT; SE day-clustered)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row("A1: engulf (a) close, SHORT, h=60", A1), K.arm_row("A2: second break close, SHORT, h=60", A2)]), "",
         "Controls: A1 = bounce-state bars (falling, wick touch of the mid, HTF on) with NO engulf (a), same 60-minute cooldown, same SHORT h=60. A2 = the engulf events whose next bar did NOT trade below the engulf low, entered at the same bar close. "
         f"Buy-and-hold DEV max drawdown {mdd_bh:.2f} % of price. PASS needs n >= {K.N_MIN}, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.", "",
         "## Secondary cells (no verdict; cannot rescue a FAIL)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row(nm, r) for nm, r in sec]), "",
         "## Variant grid (entry at the engulf close, SHORT h=60, no control; every cell is a trial)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row(nm, r) for nm, r in grid]), "",
         "## Placebo, report only (A1 side and hour taken 7 days earlier and later)", "",
         f"n = {int(ok.sum())}, mean G {pm:.4f} %, SE {ps:.4f}.", "",
         "## Frequencies: share of trades with G > 0 (price lower after the entry) at h=60, Wilson 95 % CI", "",
         K.md_table(["set", "P(G > 0)"], wil), "",
         "## MFE / MAE in ATR(14, 5m) from the entry open (A1, medians)", "",
         K.md_table(["bars (5m)", "n", "median MFE", "median MAE"], exc), "",
         "## Flow / expansion 2 x 2 on A1 (mean G %, SE day-clustered)", "",
         K.md_table(["engulf-bar delta", "BB width", "n", "mean G %", "SE"], flow), "",
         "## Data and decisions", "",
         "OI/CVD level: OI NOT_IN_DATA on DEV; CVD level not used (windowed delta only). Funding: flat 1 bp per settlement crossed. A PASS here is a gross-effect finding on the Binance tape only.", "",
         count_text(A, st, S)]
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "trials.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell", "h", "n", "mean_G", "se", "net", "t_net", "diff_vs_ctrl", "t_diff", "verdict"])
        w.writerows(trials)
    with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["engulf_bar_open_utc_ms", "bounce_x0", "htf_on", "second_break", "G_short_h60"])
        for k, i in enumerate(S["e1"]):
            w.writerow([K.TS0 + int(i) * 5 * K.MS, 1, int(st["htf_on"][i]), int(st["sb"][i]), f"{G1[PRIMARY_H][k]:.5f}"])
    sha = hashlib.sha256((HERE / "PRE_REG.md").read_bytes()).hexdigest()
    with open(HERE / "EXPOSURE_LEDGER.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["mal_bb_mid_engulf_2026-10-16", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "F:/MTS/data/tom_raw/klines 1m",
                    "2022-01-01..2024-06-30", "DEV", sha, word, "whether a bearish engulf at the 5m BB mid in a falling market has a gross effect above 0.14 % (screen before G3 marks)"])
    print(word)
    print("\n".join(L[1:16]))
    return 0


def main(argv):
    if "--count" not in argv and "--full" not in argv:
        print(__doc__)
        return 1
    A = K.load()
    st = build(A)
    S = sets(st)
    if "--count" in argv:
        txt = count_text(A, st, S)
        (HERE / "COUNT.md").write_text("# COUNT (pre-outcome)\n\n" + txt + "\n", encoding="utf-8", newline="\n")
        print(txt)
        return 0
    return full(A, st, S)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
