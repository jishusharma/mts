import sys
sys.dont_write_bytecode = True
"""Count of Tom's "price returns to value ~70 % of the time" claim on BTCUSDT (DEV only).

Pre-registration: research/tom_transfer_2026-10-11/vp_return/PRE_REG.md (written before any run). A COUNT, not a trade test:
no entry, stop, target or cost. Profile = FORMULAS 18.1 (vp_pivot_probe.build_profile), placebo = 18.6 adapted to one
refresh per UTC day, statistics = 18.7 (day-block bootstrap, 2000 resamples, seed 20261009, vp_pivot_probe.boot_stat).

Per UTC day D (5m bars, complete days only): value = profile of day D-1. Event = first 5m close of D above VAH or below
VAL. RETURN = a later 5m bar of D whose range contains the prior POC. Part B: accepted_N = the event bar and the next
N-1 bars all close beyond the same edge; outcome = a bar after the N-th close touches the POC.

CLI: python MyTradingSys/backtest/vp_return_to_value.py --out <dir>
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vp_pivot_probe as P  # noqa: E402
from splits import DEV_END, DEV_START, assert_dev_only  # noqa: E402

NS = (3, 6, 12)                                   # Part B N set: from the card, NO-SOURCE, reported for all three
PLACEBO_D = P.PLACEBO_D                           # 18.6 cycle (-3,-2,-1,-0.5,0.5,1,2,3)
NAKED_PCT = 0.003                                 # SOURCED: NakedPocTracker.java:26 REVISIT_THRESHOLD_PCT
BARS_PER_DAY = 288
DAY_MS = P.DAY_MS


def shift_levels(levels, d, r_ref):
    """18.6: every level moves by d * R_ref."""
    s = d * r_ref
    return {"poc_price": levels["poc_price"] + s, "vah": levels["vah"] + s, "val": levels["val"] + s}


def _touch(h, l, level):
    return bool(np.any((np.asarray(l, float) <= level) & (np.asarray(h, float) >= level)))


def analyse_day(levels, h, l, c, ns=NS):
    """One UTC day of 5m bars against a band. Uses bars up to the event close for the event; later bars only for outcomes."""
    h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    poc, vah, val = levels["poc_price"], levels["vah"], levels["val"]
    out = (c > vah) | (c < val)
    if not out.any():
        return {"event": None, "side": 0, "returned": None, "back_inside": None,
                "acc": {n: {"applicable": False, "accepted": False, "returned": None} for n in ns}}
    e = int(np.argmax(out))
    side = 1 if c[e] > vah else -1
    returned = _touch(h[e + 1:], l[e + 1:], poc)
    cl = c[e + 1:]
    back_inside = bool(np.any((cl >= val) & (cl <= vah)))
    acc = {}
    for n in ns:
        applicable = e + n - 1 <= len(c) - 1
        accepted = False
        ret = None
        if applicable:
            seg = c[e:e + n]
            accepted = bool(np.all(seg > vah)) if side == 1 else bool(np.all(seg < val))
            if accepted:
                ret = _touch(h[e + n:], l[e + n:], poc)
        acc[n] = {"applicable": applicable, "accepted": accepted, "returned": ret}
    return {"event": e, "side": side, "returned": returned, "back_inside": back_inside, "acc": acc}


# ------------------------------------------------------------------ study over the DEV window
def _utc_ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


def build_days(bars, start_ms, end_ms):
    """Yield per-day dicts with the prior-day levels, R_ref and the day's 5m arrays. Complete days only; drops are counted."""
    t5, h5, l5, c5, v5 = bars["t5"], bars["h5"], bars["l5"], bars["c5"], bars["v5"]
    t1, h1, l1, c1 = bars["t1"], bars["h1"], bars["l1"], bars["c1"]
    atr1 = P.atr_sma(h1, l1, c1)
    d5 = t5 // DAY_MS
    first = int(np.searchsorted(t5, start_ms))
    days, dropped = [], {"incomplete_day": 0, "no_atr": 0, "empty_profile": 0}
    ud, st = np.unique(d5, return_index=True)
    en = np.concatenate([st[1:], [len(t5)]])
    sl = {int(d): (int(a), int(b)) for d, a, b in zip(ud, st, en)}
    for d in range(start_ms // DAY_MS + 1, end_ms // DAY_MS):       # first day needs a prior day
        if d not in sl or d - 1 not in sl:
            dropped["incomplete_day"] += 1
            continue
        (a, b), (pa, pb) = sl[d], sl[d - 1]
        if b - a != BARS_PER_DAY or pb - pa != BARS_PER_DAY:
            dropped["incomplete_day"] += 1
            continue
        lv = P.build_profile(l5[pa:pb], h5[pa:pb], v5[pa:pb])
        if lv is None:
            dropped["empty_profile"] += 1
            continue
        day_start = d * DAY_MS
        k = int(np.searchsorted(t1 + P.HOUR_MS, day_start, side="right")) - 1   # last 1h bar closed at or before 00:00
        r = atr1[k] if k >= 0 else np.nan
        if not np.isfinite(r):
            dropped["no_atr"] += 1
            continue
        days.append({"d": d, "idx": d - start_ms // DAY_MS, "levels": lv, "r_ref": float(r),
                     "h": h5[a:b], "l": l5[a:b], "c": c5[a:b]})
    return days, dropped


def _naked(day, levels):
    poc = levels["poc_price"]
    h, l = day["h"], day["l"]
    return _touch(h, l, poc), bool(np.any((l <= poc * (1 + NAKED_PCT)) & (h >= poc * (1 - NAKED_PCT))))


def study(days):
    """Arrays per day, for the real band and the placebo band."""
    nd = len(days)

    def blank():
        z = lambda: np.zeros(nd)  # noqa: E731
        return {"event": z(), "ret": z(), "inside": z(), "up": z(), "naked_exact": z(), "naked_near": z(),
                "acc_app": {n: z() for n in NS}, "acc": {n: z() for n in NS}, "acc_ret": {n: z() for n in NS}}

    res = {"real": blank(), "placebo": blank()}
    dvals = np.zeros(nd)
    for i, dy in enumerate(days):
        dv = float(PLACEBO_D[dy["idx"] % 8])
        dvals[i] = dv
        for key, lv in (("real", dy["levels"]), ("placebo", shift_levels(dy["levels"], dv, dy["r_ref"]))):
            r = analyse_day(lv, dy["h"], dy["l"], dy["c"])
            o = res[key]
            ex, nr = _naked(dy, lv)
            o["naked_exact"][i], o["naked_near"][i] = ex, nr
            if r["event"] is None:
                continue
            o["event"][i] = 1
            o["ret"][i] = r["returned"]
            o["inside"][i] = r["back_inside"]
            o["up"][i] = r["side"] == 1
            for n in NS:
                a = r["acc"][n]
                o["acc_app"][n][i] = a["applicable"]
                o["acc"][n][i] = a["accepted"]
                o["acc_ret"][n][i] = bool(a["returned"])
    return res, dvals


# ------------------------------------------------------------------ statistics (18.7)
def _idx(n_days):
    return np.random.default_rng(P.BOOT_SEED).integers(0, n_days, size=(P.N_BOOT, n_days))


def _pct(x):
    return [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]


def share(num, den, mask):
    """Share num/den over the days in mask with a day-block bootstrap CI. Returns dict (n = sum den)."""
    num, den = num[mask], den[mask]
    n = int(den.sum())
    if len(num) == 0 or n == 0:
        return {"n": n, "share": None, "ci": None}
    ci = _pct(P.boot_stat(num, den, _idx(len(num))))
    return {"n": n, "share": float(num.sum() / den.sum()), "ci": ci}


def diff(numA, denA, numB, denB, mask):
    """share(A) - share(B) with the SAME resampled days."""
    a, b, c, d = numA[mask], denA[mask], numB[mask], denB[mask]
    if len(a) == 0 or b.sum() == 0 or d.sum() == 0:
        return {"diff": None, "ci": None}
    idx = _idx(len(a))
    x = P.boot_stat(a, b, idx) - P.boot_stat(c, d, idx)
    return {"diff": float(a.sum() / b.sum() - c.sum() / d.sum()), "ci": _pct(x)}


def underpowered(n):
    return "UNDERPOWERED (n<100)" if n < 100 else ""


def compute(res, days, dvals, dropped, meta):
    nd = len(days)
    yrs = np.array([datetime.fromtimestamp(d["d"] * DAY_MS / 1000, timezone.utc).year for d in days])
    allm = np.ones(nd, bool)
    R, Pl = res["real"], res["placebo"]
    out = {"meta": meta, "days_used": nd, "dropped": dropped}

    def pair(mask):
        return {"real": share(R["ret"], R["event"], mask), "placebo": share(Pl["ret"], Pl["event"], mask),
                "diff": diff(R["ret"], R["event"], Pl["ret"], Pl["event"], mask)}

    out["A"] = pair(allm)
    out["A_back_inside"] = {"real": share(R["inside"], R["event"], allm), "placebo": share(Pl["inside"], Pl["event"], allm)}
    out["fire_rate"] = {"real": float(R["event"].mean()), "placebo": float(Pl["event"].mean())}
    out["by_year"] = {int(y): pair(yrs == y) for y in np.unique(yrs)}
    out["by_side"] = {"up": pair(R["up"] == 1), "down": pair((R["up"] == 0) & (R["event"] == 1))}
    # per-d rows are descriptive: the placebo band for the days that used each d
    out["by_d"] = {f"{dv:+.1f}": share(Pl["ret"], Pl["event"], dvals == dv) for dv in PLACEBO_D}
    near = np.abs(dvals) <= 1.0                      # descriptive, added after seeing by_d (post-hoc, OURS); not the verdict
    out["A_near_placebo"] = pair(near)
    out["B"] = {}
    for n in NS:
        row = {"real": share(R["acc_ret"][n], R["acc"][n], allm), "placebo": share(Pl["acc_ret"][n], Pl["acc"][n], allm),
               "diff": diff(R["acc_ret"][n], R["acc"][n], Pl["acc_ret"][n], Pl["acc"][n], allm),
               "vs_A": diff(R["acc_ret"][n], R["acc"][n], R["ret"], R["event"], allm),
               "accepted_of_applicable": {"applicable": int(R["acc_app"][n].sum()), "accepted": int(R["acc"][n].sum())}}
        out["B"][n] = row
    out["naked"] = {k: {"real": float(R[k].mean()), "placebo": float(Pl[k].mean())} for k in ("naked_exact", "naked_near")}
    out["naked_ci"] = {k: {"real": share(R[k], np.ones(nd), allm), "placebo": share(Pl[k], np.ones(nd), allm),
                           "diff": diff(R[k], np.ones(nd), Pl[k], np.ones(nd), allm)}
                       for k in ("naked_exact", "naked_near")}
    return out


# ------------------------------------------------------------------ report
def _p(x, nd=1):
    return "NOT_IN_DATA" if x is None else f"{100 * x:.{nd}f}%"


def _ci(ci):
    return "NOT_IN_DATA" if ci is None else f"{100 * ci[0]:.1f}..{100 * ci[1]:.1f}"


def _dp(x):
    return "NOT_IN_DATA" if x is None else f"{100 * x:+.1f} pp"


def verdict(a):
    """Rule fixed in PRE_REG 0f, applied mechanically."""
    r, d = a["real"], a["diff"]
    lo, hi = r["ci"]
    if lo <= 0.70 <= hi:
        vs70 = "the 70 % claim is inside the CI"
    elif hi < 0.70:
        vs70 = "his 70 % is above the CI: it does not reproduce on BTC UTC-day value"
    else:
        vs70 = "the share is above 70 %"
    dl, dh = d["ci"]
    if dl <= 0 <= dh:
        vp = "difference to placebo CI contains zero: a property of any band, not of value"
    elif dl > 0:
        vp = "share above placebo, CI excludes zero: value-specific excess over a shifted band"
    else:
        vp = "share below placebo, CI excludes zero: value returns LESS than a shifted band"
    return vs70, vp


def render_md(out):
    A, M = out["A"], out["meta"]
    vs70, vp = verdict(A)
    L = []
    w = L.append
    w("# RESULT: price returns to prior-day value after leaving it? (Tom's 70/30 claim, BTCUSDT)\n")
    w(f"Card `tom-vp-return-to-value-count`. Pre-registration `PRE_REG.md` (written before the run). Generated by `backtest/vp_return_to_value.py` on {M['run_utc']}.")
    w(f"DEV only, {M['first_day']}..{M['last_day']} (`splits.py` DEV 2022-01-01..2024-06-30; VALIDATION and HOLDOUT not read). "
      f"{out['days_used']} complete UTC days used; dropped (NOT_IN_DATA, not zero): {out['dropped']}.")
    w("Labels: SOURCED = his claim or a file:line; OURS = our reading fixed in the pre-reg; NO-SOURCE = a measurement choice (bin 10 USD, d cycle, N set); every share below is an OURS count.\n")
    w("## Verdict (rule from PRE_REG 0f, applied mechanically)")
    w(f"- Return share {_p(A['real']['share'])} (95 % day-block CI {_ci(A['real']['ci'])}) vs placebo {_p(A['placebo']['share'])}; difference {_dp(A['diff']['diff'])} (CI {_ci(A['diff']['ci'])}).")
    w(f"- {vs70}; {vp}.")
    nv = out["A_near_placebo"]
    w(f"- Caution (post-hoc, OURS): placebo bands within 1 ATR of the real value return {_p(nv['placebo']['share'])} vs real {_p(nv['real']['share'])} on the same days "
      f"(difference {_dp(nv['diff']['diff'])}, CI {_ci(nv['diff']['ci'])}), so the pooled excess comes from the far-shifted bands; a band near value behaves like value.\n")
    w("## Part A: return to prior-day POC after the first 5m close outside prior-day value")
    w("| Band | Events (OURS) | Return share (OURS) | 95 % CI | His claim (SOURCED, extract_BB3c8visnkI.md:38) |")
    w("|---|---|---|---|---|")
    w(f"| Real prior-day value | {A['real']['n']} | {_p(A['real']['share'])} | {_ci(A['real']['ci'])} | 70 % |")
    w(f"| Placebo, shifted d x ATR14 (NO-SOURCE, 18.6) | {A['placebo']['n']} | {_p(A['placebo']['share'])} | {_ci(A['placebo']['ci'])} | n/a |")
    w(f"| Real minus placebo | | {_dp(A['diff']['diff'])} | {_ci(A['diff']['ci'])} (pp) | n/a |")
    w(f"\nFire rate (event days / days): real {_p(out['fire_rate']['real'])}, placebo {_p(out['fire_rate']['placebo'])}.")
    w(f"Secondary (OURS): a later 5m close back INSIDE value: real {_p(out['A_back_inside']['real']['share'])} (CI {_ci(out['A_back_inside']['real']['ci'])}), placebo {_p(out['A_back_inside']['placebo']['share'])}.\n")
    w("### Per year")
    w("| Year | Real n | Real share | Real CI | Placebo share | Diff (pp) | Diff CI |")
    w("|---|---|---|---|---|---|---|")
    for y, r in out["by_year"].items():
        w(f"| {y} | {r['real']['n']} | {_p(r['real']['share'])} | {_ci(r['real']['ci'])} | {_p(r['placebo']['share'])} | {_dp(r['diff']['diff'])} | {_ci(r['diff']['ci'])} |")
    w("\n### By leave side")
    w("| Side | Real n | Real share | Real CI | Placebo share | Diff (pp) | Diff CI |")
    w("|---|---|---|---|---|---|---|")
    for s, r in out["by_side"].items():
        w(f"| leave {s} | {r['real']['n']} | {_p(r['real']['share'])} | {_ci(r['real']['ci'])} | {_p(r['placebo']['share'])} | {_dp(r['diff']['diff'])} | {_ci(r['diff']['ci'])} |")
    w("\n### Placebo by d (descriptive; days that used each d; band moves d x ATR14 from the real value)")
    w("| d (NO-SOURCE) | Events | Return share | CI |")
    w("|---|---|---|---|")
    for k, r in out["by_d"].items():
        w(f"| {k} | {r['n']} | {_p(r['share'])} | {_ci(r['ci'])} |")
    npl = out["A_near_placebo"]
    w(f"\nPost-hoc descriptive (OURS, added after seeing the per-d rows, NOT the verdict): on the days with |d| <= 1 the placebo share is {_p(npl['placebo']['share'])} "
      f"(n {npl['placebo']['n']}, CI {_ci(npl['placebo']['ci'])}) against {_p(npl['real']['share'])} for the real band on the same days (n {npl['real']['n']}); "
      f"difference {_dp(npl['diff']['diff'])} (CI {_ci(npl['diff']['ci'])}). The pooled placebo is pulled down by the far-shifted bands (|d| >= 2), whose POC lies far from the open.")
    w("\n## Part B: accepted away (N consecutive 5m closes beyond the same value edge; N NO-SOURCE, all three shown, none picked)")
    w("Outcome = a 5m bar after the N-th close touches the prior POC. `Applicable` = events with at least N-1 later bars in the day.")
    w("| N | Applicable | Accepted | Return share after acceptance | CI | Placebo (same rule, shifted band) | Real minus placebo (pp) | CI | Minus Part A share (pp) | CI | Flag |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for n, r in out["B"].items():
        ac = r["accepted_of_applicable"]
        w(f"| {n} | {ac['applicable']} | {ac['accepted']} | {_p(r['real']['share'])} | {_ci(r['real']['ci'])} | {_p(r['placebo']['share'])} | "
          f"{_dp(r['diff']['diff'])} | {_ci(r['diff']['ci'])} | {_dp(r['vs_A']['diff'])} | {_ci(r['vs_A']['ci'])} | {underpowered(r['real']['n'])} |")
    nk, nc = out["naked"], out["naked_ci"]
    w("\n## Naked-POC side column (all days with a prior day, event or not)")
    w("Share of days on which day D reaches the D-1 POC. Threshold 0.3 % = SOURCED `NakedPocTracker.java:26`. This is the D-1 POC only, not the live tracker's older-POC chain (OURS).")
    w("| Touch rule | Real share | CI | Placebo share | Real minus placebo (pp) | CI |")
    w("|---|---|---|---|---|---|")
    for k, lab in (("naked_exact", "bar range contains POC"), ("naked_near", "bar range within 0.3 % of POC")):
        r = nc[k]
        w(f"| {lab} | {_p(r['real']['share'])} | {_ci(r['real']['ci'])} | {_p(r['placebo']['share'])} | {_dp(r['diff']['diff'])} | {_ci(r['diff']['ci'])} |")
    w("\n## Not in data / limits")
    w("- Cash-session profile (TOM-281): NOT_IN_DATA for BTC; every value here is a UTC-day value (OURS). His drawn levels: NOT_IN_DATA.")
    w("- LVN: not built; \"beyond the LVN side\" is read as beyond the value-area edge (OURS).")
    w("- A count of a claim, not a trade test: no fee, stop, target or edge is claimed. No rule or gate is added.")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    start_ms = int(DEV_START.timestamp() * 1000)
    end_ms = int(DEV_END.timestamp() * 1000)
    assert_dev_only(DEV_START, DEV_END - np.timedelta64(1, "m"))
    bars = P.load_bars(start_ms, end_ms)
    assert int(bars["t5"].max()) < end_ms, "bars past DEV end"
    days, dropped = build_days(bars, start_ms, end_ms)
    res, dvals = study(days)
    fmt = lambda d: datetime.fromtimestamp(d * DAY_MS / 1000, timezone.utc).strftime("%Y-%m-%d")  # noqa: E731
    meta = {"first_day": fmt(days[0]["d"]), "last_day": fmt(days[-1]["d"]), "bars_meta": {k: v for k, v in bars["meta"].items() if k != "largest_gaps"},
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}
    out = compute(res, days, dvals, dropped, meta)
    od = Path(args.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    (od / "RESULT.md").write_text(render_md(out), encoding="utf-8", newline="\n")
    print(render_md(out))


if __name__ == "__main__":
    main()
