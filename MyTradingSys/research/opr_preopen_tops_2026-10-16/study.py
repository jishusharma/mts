"""OPR-PREOPEN-TOPS G5 DEV screen. Rules: PRE_REG.md (frozen before the outcome run). DEV only (bars < 2024-07-01).
Screen, ran before G3 marks by operator decision 2026-10-16.

Usage: python study.py --count   (events and arm sizes only, NO return or outcome column is computed)
       python study.py --full    (outcome run, one run, every computed cell is printed / written)
"""
import csv
import datetime as dt
import hashlib
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import common as K  # noqa: E402

NY = ZoneInfo("America/New_York")
SESSION_MIN = 390          # US cash session length; the break must happen inside it (OURS)
BREAK_FRAC = 0.1           # break = 3m close above the top by >= 0.1 x ATR(14, 3m) (OURS, draft grid middle value)
HS = (60, 180, 390)        # +1 h, +3 h, +6.5 h after the break close (draft); primary h = 60 (OURS)
PRIMARY_H = 60
COOLDOWN = 60              # minutes between ledger events (OURS)


def open_idx(d):
    """1m tape index of the 09:30 New York open of date d (13:30Z in EDT, 14:30Z in EST)."""
    u = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(dt.timezone.utc)
    return int((int(u.timestamp() * 1000) - K.TS0) // K.MS)


def swing_highs(H, lo, hi, w=3):
    """Indices k in [lo, hi] whose high is strictly above the w bars to the left and >= the w bars to the right."""
    out = []
    for k in range(max(lo, w), min(hi, len(H) - w - 1) + 1):
        left, right = H[k - w:k], H[k + 1:k + w + 1]
        if np.isnan(H[k]) or np.isnan(left).any() or np.isnan(right).any():
            continue
        if H[k] > left.max() and H[k] >= right.max():
            out.append(k)
    return out


def unbroken(H, k, end):
    x = H[k + 1:end]
    return (not np.isnan(x).any()) and (len(x) == 0 or x.max() <= H[k])


def first_break(C, atr, top, start, stop, frac=BREAK_FRAC):
    thr = top + frac * atr[start:stop]
    hit = C[start:stop] > thr                       # NaN compares False
    return int(start + hit.argmax()) if hit.any() else -1


def speeds(H, L, C, atr, o3, j, top):
    """S1 minutes from the open to the break-bar close; S2 ATR-normalised approach; S3 dwell bars near the top."""
    s1 = (j + 1 - o3) * 3
    s2 = (C[j] - np.min(L[j - 10:j])) / atr[j]
    s3 = int(np.sum(H[o3:j] >= top - 0.25 * atr[o3:j]))
    return s1, float(s2), s3


def groups(s, qlo=1 / 3, qhi=2 / 3, quick_high=False):
    s = np.asarray(s, float)
    ok = ~np.isnan(s)
    lo, hi = np.quantile(s[ok], [qlo, qhi])
    g = np.full(len(s), "mid", dtype="<U5")
    if quick_high:
        g[s <= lo] = "slow"
        g[s >= hi] = "quick"
    else:
        g[s >= hi] = "slow"
        g[s <= lo] = "quick"
    g[~ok] = "nan"
    return g


# ---------------------------------------------------------------- ledger
def build(A):
    a3, a15, a60 = K.agg(A, 3), K.agg(A, 15), K.agg(A, 60)
    atr3 = K.atr_sma(a3["H"], a3["L"], a3["C"], 14)
    atr60 = K.atr_sma(a60["H"], a60["L"], a60["C"], 14)
    dl = 2.0 * A["TBV"] - A["V"]
    cnt = dict(weekdays=0, dropped_days=0, days_with_top=0, tops=0, broken_tops=0)
    rows = []
    for di in range(K.NDAYS_DEV):
        d = dt.date(2022, 1, 1) + dt.timedelta(days=di)
        if d.weekday() >= 5:
            continue
        cnt["weekdays"] += 1
        oi = open_idx(d)
        o3, o15, o60 = oi // 3, oi // 15, oi // 60
        po, atr1h = A["O"][oi], atr60[o60 - 1]
        if np.isnan(po) or np.isnan(atr1h):
            cnt["dropped_days"] += 1
            continue
        ks = swing_highs(a15["H"], di * 96, o15 - 1 - 3, 3)
        tops = sorted(set(float(a15["H"][k]) for k in ks if unbroken(a15["H"], k, o15) and 0 < a15["H"][k] - po <= 3 * atr1h))
        cnt["tops"] += len(tops)
        cnt["days_with_top"] += bool(tops)
        brk = {}
        for top in tops:
            j = first_break(a3["C"], atr3, top, o3, o3 + SESSION_MIN // 3)
            if j >= 0:
                cnt["broken_tops"] += 1
                brk.setdefault(j, top)               # tops ascending: the lowest top broken on that bar
        for j, top in sorted(brk.items()):
            if j < 10:
                continue
            s1, s2, s3 = speeds(a3["H"], a3["L"], a3["C"], atr3, o3, j, top)
            t = (j + 1) * 3 - 1
            nxt = next((x for x in tops if x > top), np.nan)
            rows.append((t, top, nxt, s1, s2, s3, float(dl[t - 11:t + 1].sum()), float(atr60[(t + 1) // 60 - 1]), float(a3["C"][j])))
    rows.sort()
    ev = {k: np.array([r[i] for r in rows], float) for i, k in enumerate(("t", "top", "nxt", "S1", "S2", "S3", "delta4", "atr1h", "cbreak"))}
    ev["t"] = ev["t"].astype(np.int64)
    n0 = len(ev["t"])
    keep = K.cooldown_mask(ev["t"], np.zeros(n0, int), COOLDOWN)
    cnt["events_before_cooldown"] = n0
    ev = {k: v[keep] for k, v in ev.items()}
    cnt["events"] = int(keep.sum())
    return ev, cnt, dict(a15=a15, a60=a60)


def count_text(A, ev, cnt):
    miss = int(np.isnan(A["O"]).sum())
    g1 = groups(ev["S1"])
    q1, q2 = np.quantile(ev["S1"], [1 / 3, 2 / 3])
    lines = ["## Count section (no return or outcome column was computed)", "",
             f"1m bars missing on the DEV tape: {miss} of {len(A['O'])}. Weekdays {cnt['weekdays']}, dropped for a missing open/ATR bar {cnt['dropped_days']}, "
             f"weekdays with >= 1 qualifying top {cnt['days_with_top']}.",
             f"Qualifying tops {cnt['tops']}; tops broken inside the 390-minute session {cnt['broken_tops']}; break events before the 60-minute cooldown "
             f"{cnt['events_before_cooldown']}; events after the cooldown (the ledger) **n = {cnt['events']}**.",
             f"S1 tertile cut points (minutes from the open): {q1:.1f} / {q2:.1f}. Arm sizes by S1: quick {int((g1 == 'quick').sum())}, mid {int((g1 == 'mid').sum())}, "
             f"slow {int((g1 == 'slow').sum())} (verdict arms H1 = quick, H2 = slow; each needs n >= {K.N_MIN}).",
             f"S2 quick (top tertile) {int((groups(ev['S2'], quick_high=True) == 'quick').sum())}, S2 slow {int((groups(ev['S2'], quick_high=True) == 'slow').sum())}; "
             f"S3 quick {int((groups(ev['S3']) == 'quick').sum())}, S3 slow {int((groups(ev['S3']) == 'slow').sum())} (secondary, no verdict).",
             "OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed."]
    return "\n".join(lines)


# ---------------------------------------------------------------- full run
def full(A, ev, cnt, aux):
    n = len(ev["t"])
    t = ev["t"]
    e = t + 1 + K.DELAY
    day = e // K.DAYMIN
    mdd_bh = K.S.bh_mdd(A)
    G = {side: K.net_cells(A, t, np.full(n, side), HS) for side in (-1, 1)}
    S1g = groups(ev["S1"])
    S2g = groups(ev["S2"], quick_high=True)
    S3g = groups(ev["S3"])
    med = np.median(ev["S1"])
    S1m = np.where(ev["S1"] <= med, "quick", "slow")
    trials = []

    def arm(name, mask, ctrl, side, h, verdict_arm=False):
        g = G[side][h]
        r = K.verdict_arm(g[mask], day[mask], g[ctrl], day[ctrl], t[mask], mdd_bh)
        trials.append([name, side, h, r["n"], f"{r['mean']:.5f}", f"{r['se']:.5f}", f"{r['net']:.5f}", f"{r['t_net']:.3f}", f"{r['diff']:.5f}",
                       f"{r['t_diff']:.3f}", r["verdict"] if verdict_arm else "secondary"])
        if not verdict_arm:
            r = dict(r, verdict="secondary")
        return r

    primary = [("H1: S1 quick, SHORT at the break close, h=60", S1g == "quick", S1g != "quick", -1),
               ("H2: S1 slow, LONG at the break close, h=60", S1g == "slow", S1g != "slow", 1)]
    prim = [(nm, arm(nm, m, c, s, PRIMARY_H, True)) for nm, m, c, s in primary]
    sec = []
    for lab, grp in (("S1", S1g), ("S2", S2g), ("S3", S3g), ("S1 median split", S1m)):
        for h in HS:
            sec.append((f"{lab} quick SHORT h={h}", arm(f"{lab} quick SHORT h={h}", grp == "quick", grp != "quick", -1, h, False)))
            sec.append((f"{lab} slow LONG h={h}", arm(f"{lab} slow LONG h={h}", grp == "slow", grp != "slow", 1, h, False)))
    # all groups x sides x horizons, mean G (decay table)
    decay = []
    for lab, grp in (("S1", S1g), ("S2", S2g), ("S3", S3g)):
        for gname in ("quick", "mid", "slow"):
            for side in (-1, 1):
                for h in HS:
                    m = (grp == gname) & ~np.isnan(G[side][h])
                    mu, se = K.cm_se(G[side][h][m], day[m])
                    decay.append([lab, gname, "SHORT" if side == -1 else "LONG", h, int(m.sum()), f"{mu:.4f}", f"{se:.4f}", f"{mu - K.C_PCT:.4f}"])
    # placebo (report only): same side, hour, +-7 days
    plc = []
    for nm, m, c, s in primary:
        gp, dp, _ = K.placebo_gross(A, t[m], np.full(int(m.sum()), s), PRIMARY_H)
        ok = ~np.isnan(gp)
        mu, se = K.cm_se(gp[ok], dp[ok])
        plc.append([nm, "-7 d, +7 d", int(ok.sum()), f"{mu:.4f}", f"{se:.4f}"])
    # frequency tables (draft outcomes), Wilson CI, groups of S1/S2/S3
    a15 = aux["a15"]
    up15 = K.bb(a15["C"])[2]
    freq = []
    for lab, grp in (("S1", S1g), ("S2", S2g), ("S3", S3g)):
        for gname in ("quick", "mid", "slow"):
            m = np.nonzero(grp == gname)[0]
            row = [lab, gname, len(m)]
            for h in HS:
                cb, ch = A["C"][t[m]], A["C"][np.minimum(t[m] + h, len(A["C"]) - 1)]
                ok = ~np.isnan(cb) & ~np.isnan(ch) & (t[m] + h < len(A["C"]))
                row.append(K.fmt_ci(int((ch[ok] < cb[ok]).sum()), int(ok.sum())))
            tag, nv = 0, 0
            nt, nk = 0, 0
            for i in m:
                m0 = -(-(t[i] + 1) // 15)
                hh, uu = a15["H"][m0:m0 + 26], up15[m0:m0 + 26]
                if len(hh) == 26 and not np.isnan(hh).any() and not np.isnan(uu).any():
                    nv += 1
                    tag += bool((hh >= uu).any())
                if not np.isnan(ev["nxt"][i]):
                    w = A["H"][t[i] + 1:t[i] + 1 + SESSION_MIN]
                    if len(w) == SESSION_MIN and not np.isnan(w).any():
                        nk += 1
                        nt += bool(w.max() >= ev["nxt"][i] + 0.1)
            row += [K.fmt_ci(tag, nv), K.fmt_ci(nt, nk)]
            freq.append(row)
    # flow 2x2 (net taker delta over the break bar and 3 bars before), primary arms only
    flow = []
    for nm, m, c, s in primary:
        for sg, lab in ((ev["delta4"] > 0, "delta4 > 0"), (ev["delta4"] <= 0, "delta4 <= 0")):
            mm = m & sg & ~np.isnan(G[s][PRIMARY_H])
            mu, se = K.cm_se(G[s][PRIMARY_H][mm], day[mm])
            flow.append([nm.split(",")[0], lab, int(mm.sum()), f"{mu:.4f}", f"{se:.4f}"])
    # MFE / MAE in ATR(14, 1h) from the entry bar
    exc = []
    for nm, m, c, s in primary:
        for h in HS:
            fav, adv = K.excursion(A, e[m], np.full(int(m.sum()), s), h, ev["atr1h"][m])
            exc.append([nm.split(",")[0], h, int((~np.isnan(fav)).sum()), f"{np.nanmedian(fav):.2f}", f"{np.nanmedian(adv):.2f}"])
    # write
    verdicts = [r["verdict"] for _, r in prim]
    word = K.headline(verdicts)
    L = [word, "",
         "# RESULT: OPR-PREOPEN-TOPS, break speed vs session outcome, DEV screen (primary cell d=1 min delay, h=60, cost 0.14 % round trip)", "",
         "**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. "
         "Rules frozen in PRE_REG.md (committed before this file). Labels: SOURCED = the operator's words in the draft; every threshold, entry, horizon and cost "
         "choice below is OURS, written in PRE_REG.md before the run (the operator's reads state no entry or stop).", "",
         f"Study word = {word} (rule: PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: "
         + "; ".join(f"{nm.split(':')[0]} {r['verdict']}" for nm, r in prim) + ".", "",
         "## Verdict arms (mean G in % of notional after 1 bp-per-settlement funding; SE day-clustered; control = the other S1 groups, same side and horizon)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row(nm, r) for nm, r in prim]), "",
         f"Buy-and-hold DEV max drawdown {mdd_bh:.2f} % (of price). PASS needs n >= {K.N_MIN}, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD. "
         "MDE at 80 % power = 2.8 x SE (column above).", "",
         "## Secondary cells (all computed cells printed; no verdict, cannot rescue a FAIL)", "",
         K.md_table(K.ARM_HEAD, [K.arm_row(nm, r) for nm, r in sec]), "",
         "## Mean G by group, side and horizon (S1/S2/S3 tertiles; S2 quick = top tertile, S3 slow = top dwell tertile)", "",
         K.md_table(["def", "group", "side", "h", "n", "mean G %", "SE", "net of 0.14 %"], decay), "",
         "## Placebo, report only (same side and hour taken 7 days earlier and later)", "",
         K.md_table(["arm", "lags", "n", "mean G %", "SE"], plc), "",
         "## Frequencies with Wilson 95 % CI (draft outcomes; cells with n < 10 are not read)", "",
         K.md_table(["def", "group", "n", "close < break close at +1 h", "at +3 h", "at +6.5 h", "15m upper BB(20,2) tagged within 6.5 h", "next higher top exceeded within 6.5 h"], freq), "",
         "## Flow split (taker delta over the break bar and the 3 bars before; CVD level not used)", "",
         K.md_table(["arm", "split", "n", "mean G %", "SE"], flow), "",
         "## MFE / MAE in ATR(14, 1h) from the entry open (medians; side of the arm)", "",
         K.md_table(["arm", "h", "n", "median MFE", "median MAE"], exc), "",
         "## Data and decisions", "",
         "OI: NOT_IN_DATA on DEV. Funding: flat 1 bp per 00/08/16 UTC settlement crossed (raw_fund archive absent). Participation: not computed (research clip, no fill claim).",
         "A PASS here is a gross-effect finding on the Binance tape only; no entry, stop or rule is adopted.", "", count_text(A, ev, cnt)]
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(HERE / "trials.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell", "side", "h", "n", "mean_G", "se", "net", "t_net", "diff_vs_ctrl", "t_diff", "verdict"])
        w.writerows(trials)
    with open(HERE / "ledger.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["break_close_utc_ms", "top", "next_top", "S1_min", "S2_atr", "S3_dwell", "delta4", "G_short_h60", "G_long_h60"])
        for i in range(n):
            w.writerow([K.TS0 + (int(t[i]) + 1) * K.MS, f"{ev['top'][i]:.1f}", "" if np.isnan(ev["nxt"][i]) else f"{ev['nxt'][i]:.1f}", int(ev["S1"][i]),
                        f"{ev['S2'][i]:.3f}", int(ev["S3"][i]), f"{ev['delta4'][i]:.2f}", f"{G[-1][60][i]:.5f}", f"{G[1][60][i]:.5f}"])
    sha = hashlib.sha256((HERE / "PRE_REG.md").read_bytes()).hexdigest()
    with open(HERE / "EXPOSURE_LEDGER.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["study", "run_utc", "data_source", "window_read", "split", "rule_sha256", "verdict", "decision_informed"])
        w.writerow(["opr_preopen_tops_2026-10-16", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "F:/MTS/data/tom_raw/klines 1m",
                    "2022-01-01..2024-06-30", "DEV", sha, word, "whether pre-open top break speed has a gross effect above 0.14 % (screen before G3 marks)"])
    print(word)
    print("\n".join(L[1:24]))
    return 0


def main(argv):
    if "--count" not in argv and "--full" not in argv:
        print(__doc__)
        return 1
    A = K.load()
    ev, cnt, aux = build(A)
    txt = count_text(A, ev, cnt)
    if "--count" in argv:
        (HERE / "COUNT.md").write_text("# COUNT (pre-outcome)\n\n" + txt + "\n", encoding="utf-8", newline="\n")
        print(txt)
        return 0
    return full(A, ev, cnt, aux)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
