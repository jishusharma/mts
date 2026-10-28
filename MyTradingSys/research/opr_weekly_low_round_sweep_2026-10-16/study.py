"""OPR-WEEKLY-LOW-ROUND-SWEEP G5 DEV screen. Rules: PRE_REG.md (frozen before the outcome run). DEV only (bars < 2024-07-01).
Screen, ran before G3 marks by operator decision 2026-10-16.

Usage: python study.py --count   (event counts only, NO return and no A/B/C or other outcome column is computed)
       python study.py --full    (outcome run, one run, every computed cell is printed / written)
"""
import csv
import datetime as dt
import hashlib
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import common as K  # noqa: E402

NY = ZoneInfo("America/New_York")
HS = (30, 60, 120)               # minutes after the entry open; primary h = 60 (OURS, template; the draft's MFE/MAE grid is 30/60/120)
PRIMARY_H = 60
COOLDOWN = 60                    # minutes between ledger events (OURS, template value)
P_GRID, P_PRIMARY = (0.0, 0.001, 0.002, 0.003), 0.001     # penetration grid (draft); primary 0.1 %
K_GRID, K_PRIMARY = (3, 5, 10, 15), 5                      # reclaim-within-k-minutes grid; primary 5
M_PRIMARY = 3                    # consecutive closes below for acceptance (draft grid 3, 5)
WINDOW = 60                      # event window in minutes after the first break
HOLD = 15                        # no close below the level for 15 minutes after the reclaim (draft)
PREV = 60                        # all of the previous 60 closes were at/above the level before the first break (OURS)
BIG = 10 ** 6


# ---------------------------------------------------------------- rules (pure functions)
def week_low_prior(L1m):
    """Per 1m bar: the low of the previous FULL Monday-Sunday UTC week (NaN where there is none). Day 0 = Saturday 2022-01-01."""
    nd = len(L1m) // K.DAYMIN
    wk = (np.arange(nd) + 5) // 7
    out = np.full(len(L1m), np.nan)
    for w in range(2, int(wk.max()) + 1):
        prev, cur = np.nonzero(wk == w - 1)[0], np.nonzero(wk == w)[0]
        if len(prev) < 7 or len(cur) == 0:
            continue
        out[cur[0] * K.DAYMIN:(cur[-1] + 1) * K.DAYMIN] = np.nanmin(L1m[prev[0] * K.DAYMIN:(prev[-1] + 1) * K.DAYMIN])
    return out


def round_levels(Cl, prev=PREV):
    m = pd.Series(Cl).rolling(prev).min().shift(1).to_numpy()
    return np.floor(m / 1000.0) * 1000.0


def break_candidates(Lo, Cl, lvl, p, prev=PREV):
    """Bars whose low is at least p below the level while all of the previous `prev` closes were at or above it (first break)."""
    m = pd.Series(Cl).rolling(prev).min().shift(1).to_numpy()
    with np.errstate(invalid="ignore"):
        ok = (m >= lvl) & (Lo <= lvl * (1.0 - p))
    return np.nonzero(ok)[0]


def first_above(Cw, lvl):
    ab = Cw > lvl[:, None]
    return np.where(ab.any(1), ab.argmax(1), BIG)


def accepted_first3(Cw, lvl):
    return (Cw[:, :3] < lvl[:, None]).all(1)


def abc_parts(Cw, lvl, k=K_PRIMARY, m=M_PRIMARY, hold=HOLD):
    """A reclaim: first close above within k minutes AND no close below in the next `hold` minutes AND it comes before m consecutive closes below.
    B acceptance: m consecutive closes below at some point in the window (and not A). C: neither. X: missing data."""
    n, w = Cw.shape
    below = Cw < lvl[:, None]
    r = first_above(Cw, lvl)
    run, s = np.zeros(n, int), np.full(n, BIG)
    for c in range(w):
        run = np.where(below[:, c], run + 1, 0)
        s = np.where((run >= m) & (s == BIG), c, s)
    held = np.ones(n, bool)
    for i in np.nonzero(r <= k)[0]:
        held[i] = not below[i, r[i] + 1:r[i] + 1 + hold].any()
    A = (r <= k) & held & (r < s)
    B = ~A & (s < BIG)
    cls = np.where(A, "A", np.where(B, "B", "C"))
    cls[np.isnan(Cw).any(1)] = "X"
    return cls, r, s


def classify_abc(Cw, lvl, k=K_PRIMARY, m=M_PRIMARY, hold=HOLD):
    return abc_parts(Cw, lvl, k, m, hold)[0]


def win(arr, t0, w):
    idx = np.asarray(t0, np.int64)[:, None] + np.arange(w)[None, :]
    return np.where(idx < len(arr), arr[np.minimum(idx, len(arr) - 1)], np.nan)


def open_idx(d):
    u = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(dt.timezone.utc)
    return int((int(u.timestamp() * 1000) - K.TS0) // K.MS)


# ---------------------------------------------------------------- ledgers
def family(A, fam, p, Lw):
    lvl = round_levels(A["C"]) if fam == "round" else Lw
    j = break_candidates(A["L"], A["C"], lvl, p)
    j = j[K.cooldown_mask(j, np.zeros(len(j), int), COOLDOWN)]
    return j, lvl[j]


def pooled(A, p, Lw):
    jw, lw = family(A, "weekly", p, Lw)
    jr, lr = family(A, "round", p, Lw)
    j, lvl = np.concatenate((jw, jr)), np.concatenate((lw, lr))
    fam = np.concatenate((np.ones(len(jw), int), np.zeros(len(jr), int)))        # weekly first on a tie
    keep = K.cooldown_mask(j, np.zeros(len(j), int), COOLDOWN)
    o = np.argsort(j[keep], kind="stable")
    return j[keep][o], lvl[keep][o], fam[keep][o]


def stacked(lvl, fam, j, Lw, x):
    other = np.where(fam == 0, Lw[j], np.round(lvl / 1000.0) * 1000.0)       # round event: prior-week low; weekly event: nearest round-1000
    with np.errstate(invalid="ignore"):
        return np.abs(lvl - other) / lvl <= x


def count_text(A, Lw):
    L = ["## Count section (no return and no A/B/C or other outcome column was computed)", "",
         f"1m bars missing on the DEV tape: {int(np.isnan(A['O']).sum())} of {len(A['O'])}. Prior-week low available on {int((~np.isnan(Lw)).sum()) // K.DAYMIN} of {K.NDAYS_DEV} days.",
         "First-break events after the 60-minute cooldown (all of the previous 60 closes at/above the level, then a 1m low at least p below it):", ""]
    rows = []
    for p in P_GRID:
        jr, _ = family(A, "round", p, Lw)
        jw, _ = family(A, "weekly", p, Lw)
        j, lvl, fam = pooled(A, p, Lw)
        rows.append([f"{100 * p:.1f} %", len(jr), len(jw), len(j), "  ".join(f"{x}: {int(stacked(lvl, fam, j, Lw, x).sum())}" for x in (0.001, 0.0025, 0.005))])
    L += [K.md_table(["penetration p", "round-1000 events", "prior-week-low events", "pooled ledger", "pooled events stacked within 0.1 % / 0.25 % / 0.5 %"], rows), "",
          "Primary p = 0.1 %%: pooled ledger **n = %d** (round %d, weekly %d). Arm sizes (reclaim within 5 minutes; first three closes below) depend on the 1m closes after the break and are printed with the outcome run, not here." % (
              len(pooled(A, P_PRIMARY, Lw)[0]), len(family(A, "round", P_PRIMARY, Lw)[0]), len(family(A, "weekly", P_PRIMARY, Lw)[0])),
          "OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed."]
    return "\n".join(L)


def abc_row(name, cls):
    ok = cls != "X"
    n = int(ok.sum())
    return [name, n] + [K.fmt_ci(int((cls == c).sum()), n) for c in "ABC"]


ABC_HEAD = ["set", "n", "P(A reclaim)", "P(B acceptance)", "P(C neither)"]


# ---------------------------------------------------------------- full run
def full(A, Lw):
    mdd_bh = K.S.bh_mdd(A)
    a60, a240 = K.agg(A, 60), K.agg(A, 240)
    atr60 = K.atr_sma(a60["H"], a60["L"], a60["C"], 14)
    rsi60, rsi240 = K.rsi_wilder(a60["C"]), K.rsi_wilder(a240["C"])
    lo240 = K.bb(a240["C"])[0]
    dl = 2.0 * A["TBV"] - A["V"]
    trials = []
    # ---- grid: family x p x k (m=3) and m=5 at k=5
    grid = []
    for fam in ("round", "weekly"):
        for p in P_GRID:
            j, lvl = family(A, fam, p, Lw)
            Cw = win(A["C"], j, WINDOW + 1)
            for k in K_GRID:
                grid.append(abc_row(f"{fam}, p={100 * p:.1f} %, k={k}, m=3", classify_abc(Cw, lvl, k, 3)))
            grid.append(abc_row(f"{fam}, p={100 * p:.1f} %, k=5, m=5", classify_abc(Cw, lvl, 5, 5)))
    # ---- pooled primary events
    j, lvl, fam = pooled(A, P_PRIMARY, Lw)
    n = len(j)
    Cw = win(A["C"], j, WINDOW + 1)
    cls, r, s = abc_parts(Cw, lvl)
    i60, i240 = np.clip((j + 1) // 60 - 1, 0, None), np.clip((j + 1) // 240 - 1, 0, None)
    stretch = (rsi60[i60] < 35) & (rsi240[i240] < 35) & (A["C"][j] < lo240[i240])
    pre5 = np.array([dl[x - 5:x].sum() for x in j])
    post5 = np.array([dl[x:x + 5].sum() for x in j])
    flip = (pre5 < 0) & (post5 > 0)
    sess = np.zeros(n, bool)
    for i, x in enumerate(j):
        d = dt.date(2022, 1, 1) + dt.timedelta(days=int(x // K.DAYMIN))
        if d.weekday() < 5:
            sess[i] = 0 <= (x + 1) - open_idx(d) <= 60
    cond = [abc_row("all pooled events (unconditional)", cls), abc_row("round-1000 events", cls[fam == 0]), abc_row("prior-week-low events", cls[fam == 1])]
    for x in (0.001, 0.0025, 0.005):
        st = stacked(lvl, fam, j, Lw, x)
        cond += [abc_row(f"stacked within {100 * x:.2f} %", cls[st]), abc_row(f"single level (not stacked within {100 * x:.2f} %)", cls[~st])]
    for nm, v in (("US-open window (0-60 min after 09:30 NY, weekdays)", sess), ("HTF stretch (1h and 4h RSI14 < 35, close below the 4h lower BB)", stretch),
                  ("CVD flip (5-bar delta before < 0 and after > 0; uses 5 bars after the break, descriptive only)", flip), ("break-bar taker delta > 0", dl[j] > 0)):
        cond += [abc_row(nm, cls[v]), abc_row("not: " + nm.split(" (")[0], cls[~v])]
    ok = cls != "X"
    pen = (lvl - A["L"][j]) / lvl
    maxpen = (lvl - win(A["L"], j, WINDOW + 1).min(1)) / lvl
    atr_b = atr60[i60]
    cstrict = (cls == "C") & (np.nanmax(np.abs(Cw - lvl[:, None]), axis=1) <= 0.3 * atr_b)
    # ---- after A / after B
    after = []
    isA, isB = cls == "A", cls == "B"
    swing = np.array([A["H"][x - 720:x].max() if x >= 720 else np.nan for x in j])
    for h in HS:
        e = j + np.where(isA, r, 0) + 1 + K.DELAY
        fav, adv = K.excursion(A, e[isA], np.full(int(isA.sum()), 1), h, atr_b[isA])
        after.append(["after A (reclaim close, LONG)", h, int((~np.isnan(fav)).sum()), f"{np.nanmedian(fav):.2f}", f"{np.nanmedian(adv):.2f}"])
        e = j + np.where(isB, s, 0) + 1 + K.DELAY
        fav, adv = K.excursion(A, e[isB], np.full(int(isB.sum()), -1), h, atr_b[isB])
        after.append(["after B (acceptance close, SHORT)", h, int((~np.isnan(fav)).sum()), f"{np.nanmedian(fav):.2f}", f"{np.nanmedian(adv):.2f}"])
    hit_sw = tot_sw = hit_nx = tot_nx = 0
    for i in np.nonzero(isA)[0]:
        w = A["H"][j[i] + r[i] + 1:j[i] + r[i] + 121]
        if len(w) == 120 and not np.isnan(w).any() and not np.isnan(swing[i]):
            tot_sw += 1
            hit_sw += int(w.max() >= swing[i])
    for i in np.nonzero(isB)[0]:
        w = A["L"][j[i] + s[i] + 1:j[i] + s[i] + 121]
        if len(w) == 120 and not np.isnan(w).any():
            tot_nx += 1
            hit_nx += int(w.min() <= np.floor((lvl[i] - 1e-6) / 1000.0) * 1000.0)
    # ---- verdict arms (causal entries), pooled ledger, h = 60
    def gset(t, side):
        t = np.asarray(t, np.int64)
        return t, K.net_cells(A, t, np.full(len(t), side), HS), (t + 1 + K.DELAY) // K.DAYMIN

    def arm(name, mask, tm, cmask, tc, side, h, verdict=False):
        t, G, day = gset(tm[mask], side)
        t2, G2, day2 = gset(tc[cmask], side)
        res = K.verdict_arm(G[h], day, G2[h], day2, t, mdd_bh)
        trials.append([name, side, h, res["n"], f"{res['mean']:.5f}", f"{res['se']:.5f}", f"{res['net']:.5f}", f"{res['t_net']:.3f}", f"{res['diff']:.5f}",
                       f"{res['t_diff']:.3f}", res["verdict"] if verdict else "secondary"])
        return res if verdict else dict(res, verdict="secondary")

    okw = ~np.isnan(Cw).any(1)
    rl = (r <= K_PRIMARY) & okw
    rl_c = (r > K_PRIMARY) & okw
    asm = accepted_first3(Cw, lvl) & okw
    as_c = ~accepted_first3(Cw, lvl) & okw
    t_rl, t_rl_c = j + np.minimum(r, K_PRIMARY), j + K_PRIMARY
    t_as = j + 2
    RL = arm("RL: reclaim within 5 min, LONG at the reclaim close, h=60", rl, t_rl, rl_c, t_rl_c, 1, PRIMARY_H, True)
    AS = arm("AS: first three closes below, SHORT at the third close, h=60", asm, t_as, as_c, t_as, -1, PRIMARY_H, True)
    sec = []
    for h in HS:
        if h != PRIMARY_H:
            sec.append((f"RL h={h}", arm(f"RL h={h}", rl, t_rl, rl_c, t_rl_c, 1, h)))
            sec.append((f"AS h={h}", arm(f"AS h={h}", asm, t_as, as_c, t_as, -1, h)))
    for fn, fv in (("round", fam == 0), ("weekly", fam == 1)):
        sec.append((f"RL {fn} only h=60", arm(f"RL {fn} only h=60", rl & fv, t_rl, rl_c & fv, t_rl_c, 1, PRIMARY_H)))
        sec.append((f"AS {fn} only h=60", arm(f"AS {fn} only h=60", asm & fv, t_as, as_c & fv, t_as, -1, PRIMARY_H)))
    st25 = stacked(lvl, fam, j, Lw, 0.0025)
    sec.append(("RL stacked 0.25 % h=60", arm("RL stacked 0.25 % h=60", rl & st25, t_rl, rl_c & st25, t_rl_c, 1, PRIMARY_H)))
    sec.append(("AS stacked 0.25 % h=60", arm("AS stacked 0.25 % h=60", asm & st25, t_as, as_c & st25, t_as, -1, PRIMARY_H)))
    plc = []
    for nm, mask, tm, side in (("RL", rl, t_rl, 1), ("AS", asm, t_as, -1)):
        gp, dp, _ = K.placebo_gross(A, tm[mask], np.full(int(mask.sum()), side), PRIMARY_H)
        okp = ~np.isnan(gp)
        mu, se = K.cm_se(gp[okp], dp[okp])
        plc.append([nm, "-7 d, +7 d", int(okp.sum()), f"{mu:.4f}", f"{se:.4f}"])
    word = K.headline([RL["verdict"], AS["verdict"]])
    nm_rl, nm_as = "RL: reclaim within 5 min, LONG at the reclaim close, h=60", "AS: first three closes below, SHORT at the third close, h=60"
    L = [word, "",
         "# RESULT: OPR-WEEKLY-LOW-ROUND-SWEEP, weekly low / round-1000 break, reclaim vs acceptance, DEV screen (primary cell 1 min extra delay, h=60, cost 0.14 % round trip)", "",
         "**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). "
         "SOURCED = the operator's words in the draft (weekly low and round numbers taken together; reclaim, acceptance, range); every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop). "
         "Related evidence (a different question, HOLD not sweep-and-reclaim): `research/levels_confluence_2026-10-14/levels_hold.md` (round_1000 KEEP n=322; prior_week_low DROP at n=20).", "",
         f"Study word = {word} (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: RL {RL['verdict']}; AS {AS['verdict']}.", "",
         "## Verdict arms (pooled ledger, p = 0.1 %; mean G % of notional after funding; SE day-clustered)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row(nm_rl, RL), K.arm_row(nm_as, AS)]), "",
         "Controls (same elapsed time, no signal): RL = first breaks with NO close above the level in the first six 1m bars (indices 0-5), LONG at the close of bar index 5. AS = first breaks whose first three closes are NOT all below, SHORT at the close of bar index 2. "
         f"Buy-and-hold DEV max drawdown {mdd_bh:.2f} % of price. PASS needs n >= {K.N_MIN}, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.", "",
         "## Secondary cells (no verdict)", "", K.md_table(K.ARM_HEAD, [K.arm_row(nm, x) for nm, x in sec]), "",
         "## P(A), P(B), P(C) by family, penetration p, reclaim window k, acceptance m (draft grid; event window 60 min; Wilson 95 % CI; cells with n < 10 are not read)", "", K.md_table(ABC_HEAD, grid), "",
         "## P(A), P(B), P(C) at the primary cell (p = 0.1 %, k = 5, m = 3), unconditional and by condition", "", K.md_table(ABC_HEAD, cond), "",
         f"Penetration at the first break bar: median {100 * np.nanmedian(pen[ok]):.3f} %; maximum penetration inside the window: median {100 * np.nanmedian(maxpen[ok]):.3f} %. Share of C events that stay within 0.3 x ATR(14, 1h) of the level: {int(cstrict.sum())} of {int((cls == 'C').sum())}.", "",
         "## After A / after B (medians in ATR(14, 1h) from the entry open after the reclaim / acceptance close)", "", K.md_table(["event", "h (min)", "n", "median MFE", "median MAE"], after), "",
         f"After A: prior 12 h high exceeded within 120 minutes of the reclaim close: {K.fmt_ci(hit_sw, tot_sw)}. After B: next round-1000 level below reached within 120 minutes of the acceptance close: {K.fmt_ci(hit_nx, tot_nx)}. "
         "Pre-open tops and OI were not used (pre-open top logic belongs to the sibling screen; OI NOT_IN_DATA on DEV).", "",
         "## Placebo, report only (arm side and hour taken 7 days earlier and later)", "", K.md_table(["arm", "lags", "n", "mean G %", "SE"], plc), "",
         "## Data and decisions", "", "Funding flat 1 bp per settlement crossed. The draft's range outcome C is reported as 'neither A nor B'; the extra ATR-band condition is the share printed above. A PASS would be a gross-effect finding on the Binance tape only.", "",
         count_text(A, Lw)]
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "trials.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell", "side", "h", "n", "mean_G", "se", "net", "t_net", "diff_vs_ctrl", "t_diff", "verdict"])
        w.writerows(trials)
    with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["first_break_bar_open_utc_ms", "family", "level", "class_k5_m3", "first_close_above_idx"])
        for i in range(n):
            w.writerow([K.TS0 + int(j[i]) * K.MS, "weekly" if fam[i] else "round", f"{lvl[i]:.1f}", cls[i], "" if r[i] >= BIG else int(r[i])])
    sha = hashlib.sha256((HERE / "PRE_REG.md").read_bytes()).hexdigest()
    with open(HERE / "EXPOSURE_LEDGER.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["opr_weekly_low_round_sweep_2026-10-16", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "F:/MTS/data/tom_raw/klines 1m",
                    "2022-01-01..2024-06-30", "DEV", sha, word, "whether reclaim after a weekly-low / round-1000 break has a gross effect above 0.14 % (screen before G3 marks)"])
    print(word)
    print("\n".join(L[1:12]))
    return 0


def main(argv):
    if "--count" not in argv and "--full" not in argv:
        print(__doc__)
        return 1
    A = K.load()
    Lw = week_low_prior(A["L"])
    if "--count" in argv:
        txt = count_text(A, Lw)
        (HERE / "COUNT.md").write_text("# COUNT (pre-outcome)\n\n" + txt + "\n", encoding="utf-8", newline="\n")
        print(txt)
        return 0
    return full(A, Lw)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
