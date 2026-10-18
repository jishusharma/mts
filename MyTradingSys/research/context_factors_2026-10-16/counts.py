"""COUNT-ONLY tables for COUNTS.md and trials.csv (no outcome column is read or built).

  python counts.py      -> COUNTS.md, trials.csv, events_dev.csv (decision events with factor values, no outcome)
Event ledger (OURS, fixed before any count): a LONG (SHORT) decision event is a DEV decision hour where the nearest
support (resistance) is within K_EVENT x ATR14(1h) of the close (f1_at_level), and no event of the same side was taken in
the previous COOLDOWN_H decision hours (greedy, in time order). The PRE_REG outcome needs a stop, so the tradeable ledger
also requires f3_stop_tf != none; both are counted.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest"))
import research_kit as RK  # noqa: E402
import context_asof as C  # noqa: E402

COOLDOWN_H = 4             # OURS
SD_R = 1.5                 # OURS: sd of a 1R-stop / 2R-target trade at break-even hit rate p = 1/3 is 3 x sqrt(p(1-p)) = 1.41 R; rounded up
PLAUSIBLE_R = 0.20         # OURS: about a quarter of the best SOURCED whole-setup expectancy (+0.75 R, CATALOGUE T-3 via FABLE_RUNS_AUDIT 3.2)
YEARS = (("2022", 1_648_771_200_000, 1_672_531_200_000), ("2023", 1_672_531_200_000, 1_704_067_200_000),
         ("2024H1", 1_704_067_200_000, C.DEV_END_MS))
FACTORS = ["f1_near_layer", "f2_conf_obj", "f2_touch_cat", "f3_armed", "f3_stop_tf", "f4_D_align", "f4_12h_align",
           "f4_8h_align", "f4_4h_align", "f5_1h", "f5_4h", "f5_veto", "f5_conf", "f6_phaseA", "f6_phaseB", "f6_intraday",
           "f7_volreg", "f7_squeeze", "f7_session", "f7_weekend", "f7_approach", "f7_sweep", "f7_htf_align", "f7_funding"]
PAIRS = [("f2_conf_obj", "f6_phaseA"), ("f3_armed", "f4_D_align"), ("f5_1h", "f6_phaseA"), ("f4_D_align", "f5_1h")]


def ledger(f):
    at = f["f1_at_level"].to_numpy(bool)
    T = f["T"].to_numpy(np.int64)
    keep = np.zeros(len(f), bool)
    last = -10**18
    for i in np.flatnonzero(at):
        if T[i] - last > COOLDOWN_H * C.HOUR:
            keep[i] = True
            last = T[i]
    return f[keep].copy()


def bucket(v):
    if isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_)):
        return str(min(int(v), 3)) + ("+" if int(v) >= 3 else "")
    return str(v)


def n_needed(cost_r):
    gap = PLAUSIBLE_R - cost_r
    return int(np.ceil((RK.MDE_Z * SD_R / gap) ** 2)) if gap > 0 else None


def main():
    fr = {s: pd.read_pickle(C.CACHE / f"frame_{s}.pkl") for s in ("long", "short")}
    ev = {s: ledger(fr[s]) for s in fr}
    tr = {s: ev[s][ev[s]["f3_stop_tf"] != "none"] for s in ev}
    allev = pd.concat([tr["long"], tr["short"]])
    allev["day"] = allev["T"] // C.DAY
    allev["year"] = np.select([(allev["T"] >= a) & (allev["T"] < b) for _, a, b in YEARS], [y for y, _, _ in YEARS], "pre")
    allev.drop(columns=[c for c in allev.columns if c.startswith("f4_") and c.endswith("_cat")]).to_csv(
        HERE / "events_dev.csv", index=False, float_format="%.6g")
    cost_med = float(allev["f3_cost_R"].median())
    need = n_needed(cost_med)
    L = ["# COUNTS: DEV decision events per factor value (counts only, no outcome read)", "",
         "Built by `counts.py` from the vectorised frames (`run_dev.py vec`), DEV decision hours 2022-04-01 .. 2024-06-30 "
         "(bar open < 2024-07-01). No forward return, win/loss or exit exists in any file of this folder.", "",
         "## Ledger", "",
         "| step | long | short |", "|---|---|---|",
         f"| DEV decision hours | {len(fr['long'])} | {len(fr['short'])} |",
         f"| at a same-side level (nearest within {C.K_EVENT} x ATR14 1h) | {int(fr['long']['f1_at_level'].sum())} | {int(fr['short']['f1_at_level'].sum())} |",
         f"| after the {COOLDOWN_H} h same-side cooldown | {len(ev['long'])} | {len(ev['short'])} |",
         f"| with a valid ladder stop (stop_tf != none): **tradeable ledger** | **{len(tr['long'])}** | **{len(tr['short'])}** |",
         f"| distinct UTC days in the tradeable ledger | {tr['long']['T'].floordiv(C.DAY).nunique()} | {tr['short']['T'].floordiv(C.DAY).nunique()} |", "",
         "## Power: n needed for a decisive test (research_kit)", "",
         f"- Outcome unit R (the PRE_REG trade: ladder stop, fixed 2 R target, all-taker cost). Per-trade sd = {SD_R} R (OURS: "
         "a 1 R stop / 2 R target trade at the break-even hit rate 1/3 has sd 3 x sqrt(2/9) = 1.41 R; rounded up).",
         "- Cross-check with FABLE_RUNS_AUDIT 1.5: per-trade sd 1.97 % at a 4 h hold. Divided by the median ladder stop "
         f"({allev['f3_stop_pct'].median():.2f} %) that is {1.97 / allev['f3_stop_pct'].median():.2f} R per trade, below {SD_R} R, so {SD_R} R is the conservative choice.",
         f"- Cost in R: median of the tradeable ledger = 0.14 % / stop % = **{cost_med:.3f} R** (all-taker); maker-in 0.09 % gives "
         f"{cost_med * 0.09 / 0.14:.3f} R.",
         f"- Plausible effect of one context filter = {PLAUSIBLE_R} R (OURS: about a quarter of the best SOURCED whole-setup "
         "expectancy, +0.75 R gross, CATALOGUE T-3 quoted in FABLE_RUNS_AUDIT 3.2).",
         f"- `research_kit.power_check`: MDE = 2.8 x sd / sqrt(n) must satisfy MDE + cost <= {PLAUSIBLE_R} R  =>  "
         f"**n_needed = {need} independent units** per bucket and side. Units are UTC days (day-clustered SE), so a bucket is "
         "flagged LOW when its distinct-day count is below n_needed. The matched-baseline difference adds about "
         "sqrt(1 + 1/K) = 1.025 to the SE at K = 20 controls; ignored here (within rounding).", ""]
    chk = RK.power_check(need, SD_R, PLAUSIBLE_R, cost_med)
    L.append(f"- Check: power_check(n={need}, sd={SD_R}, plausible={PLAUSIBLE_R}, cost={cost_med:.3f}) -> mde {chk['mde']:.3f} R, "
             f"needed {chk['needed']:.3f} R, proceed={chk['proceed']}.")
    L += ["", "## Per factor value (tradeable ledger)", "",
          "n = events, d = distinct UTC days; per-year columns are events. LOW = d < n_needed.", "",
          "| factor | value | long n | long d | short n | short d | 2022 (Apr-Dec) | 2023 | 2024H1 | flag |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    enough = {}
    for fct in FACTORS:
        vals = allev[fct].map(bucket)
        for val in sorted(vals.unique()):
            m = vals == val
            sub = allev[m]
            nl = sub[sub["side"] == "long"]; ns = sub[sub["side"] == "short"]
            dl, ds = nl["day"].nunique(), ns["day"].nunique()
            yc = [int((sub["year"] == y).sum()) for y, _, _ in YEARS]
            ok_l, ok_s = dl >= need, ds >= need
            enough[(fct, val)] = (ok_l, ok_s)
            flag = "ok both" if ok_l and ok_s else "ok long" if ok_l else "ok short" if ok_s else "LOW"
            L.append(f"| {fct} | {val} | {len(nl)} | {dl} | {len(ns)} | {ds} | {yc[0]} | {yc[1]} | {yc[2]} | {flag} |")
    L += ["", "## Pairs (operator-named factors; events, long / short)", ""]
    for a, b in PAIRS:
        tab = allev.assign(A=allev[a].map(bucket), B=allev[b].map(bucket)).groupby(["A", "B", "side"]).size().unstack("side", fill_value=0)
        tab = tab.reindex(columns=["long", "short"], fill_value=0)
        L += [f"### {a} x {b}", "", "| " + a + " | " + b + " | long | short | flag |", "|---|---|---|---|---|"]
        for (va, vb), r in tab.iterrows():
            sub = allev[(allev[a].map(bucket) == va) & (allev[b].map(bucket) == vb)]
            dl = sub[sub.side == "long"]["day"].nunique(); ds = sub[sub.side == "short"]["day"].nunique()
            flag = "LOW" if max(dl, ds) < need else "ok"
            L.append(f"| {va} | {vb} | {r['long']} | {r['short']} | {flag} |")
        L.append("")
    L += ["## Stop ladder (F3): widths and cost in R per timeframe (tradeable ledger; widths only)", "",
          "| side | stop tf | n | stop % p10 | p50 | p90 | cost R p10 | p50 | p90 |", "|---|---|---|---|---|---|---|---|---|"]
    for s in ("long", "short"):
        e = tr[s]
        for k in ("D", "12h", "8h"):
            x = e[e["f3_stop_tf"] == k]
            if len(x):
                q = x["f3_stop_pct"].quantile([.1, .5, .9]).to_numpy(); cr = x["f3_cost_R"].quantile([.1, .5, .9]).to_numpy()
                L.append(f"| {s} | {k} | {len(x)} | {q[0]:.2f} | {q[1]:.2f} | {q[2]:.2f} | {cr[0]:.3f} | {cr[1]:.3f} | {cr[2]:.3f} |")
    L += ["", "Ladder outcome on the cooled-down ledger before the stop filter (why events have no stop):", "",
          "| side | D | 12h | 8h | none | of none: some width > W_max | all valid widths < W_min |", "|---|---|---|---|---|---|---|"]
    for s in ("long", "short"):
        e = ev[s]
        vc = e["f3_stop_tf"].value_counts()
        nn = e[e["f3_stop_tf"] == "none"]
        w = nn[["f3_w_D", "f3_w_12h", "f3_w_8h"]]
        wide = int((w.gt(nn["f3_wmax"], axis=0)).any(axis=1).sum())
        tight = int(((w.lt(C.W_MIN)) | w.isna()).all(axis=1).sum())
        L.append(f"| {s} | {vc.get('D', 0)} | {vc.get('12h', 0)} | {vc.get('8h', 0)} | {vc.get('none', 0)} | {wide} | {tight} |")
    (HERE / "COUNTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    n_ok = sum(1 for v in enough.values() if v[0] or v[1])
    print(f"ledger long {len(tr['long'])} short {len(tr['short'])}; cost_med {cost_med:.3f} R; n_needed {need}; "
          f"buckets ok on a side {n_ok}/{len(enough)}")
    trials(fr, ev)


def trials(fr, ev):
    """Angle e: two reasonable definitions, counts under each (decision events = cooled-down ledger)."""
    rows = []
    for s in ("long", "short"):
        f, e = fr[s], ev[s]
        rows += [
            ("F1 role flip", "1h close through the level (CHOSEN)", s, "mean same-side levels per hour", round(f["f1_n_levels"].mean(), 3)),
            ("F1 role flip", "1h and last 4h close both through (contested excluded)", s, "mean same-side levels per hour", round(f["f1_n_levels_v4h"].mean(), 3)),
            ("F2 confluence", "distinct layers (objects) in zone (CHOSEN)", s, "events with >= 2", int((e["f2_conf_obj"] >= 2).sum())),
            ("F2 confluence", "distinct trader/source names in zone", s, "events with >= 2", int((e["f2_conf_name"] >= 2).sum())),
            ("F3 armed", "close past the prior D open (CHOSEN)", s, "events armed", int(e["f3_armed"].sum())),
            ("F3 armed", "partial-day extreme past the prior D open", s, "events armed", int(e["f3_armed_B"].sum())),
            ("F3 W_max", "1.0 x ATR14(D) (CHOSEN)", s, "events with a stop", int((e["f3_stop_tf"] != "none").sum())),
            ("F3 W_max", "fixed 3.0 %", s, "events with a stop", int(_ladder_fixed(e, 3.0).ne("none").sum())),
            ("F4 engulf (D)", "operator: colour flip + close past previous open (CHOSEN)", s, "events with D engulf on the trade side",
             int((e["f4_D_cat"] == ("bull_engulf" if s == "long" else "bear_engulf")).sum())),
            ("F4 engulf (D)", "classic body engulf incl. open <= previous close", s, "events with D engulf on the trade side",
             int((e["f4_D_eng_cls"] == ("bull" if s == "long" else "bear")).sum())),
            ("F5 at the band", "close at/beyond the band (CHOSEN)", s, "events in a 1h walk (either band)", int(e["f5_1h"].str.startswith("walk").sum())),
            ("F5 at the band", "%b cushion 0.05", s, "events in a 1h walk (either band)", int(e["f5_1h_cush"].str.startswith("walk").sum())),
            ("F5 veto", "prompt: walk on the band against the trade (CHOSEN)", s, "events vetoed", int(e["f5_veto"].sum())),
            ("F5 veto", "operator 'dance' reading: any close at/below the lower band (short) / upper (long), last 2 bars", s,
             "events vetoed", int(e["f5_1h"].isin(("walk_lower", "break_lower", "reenter_lower") if s == "short"
                                                   else ("walk_upper", "break_upper", "reenter_upper")).sum())),
        ]
        for ph in ("f6_phaseA", "f6_phaseB"):
            lab = "weekly close vs SMA10(W) + slope (CHOSEN)" if ph == "f6_phaseA" else "30 d trend tag + 90 d range position"
            vc = e[ph].value_counts()
            for k in ("markup", "distribution", "markdown", "accumulation", "balance", "na"):
                rows.append(("F6 phase", lab, s, f"events {k}", int(vc.get(k, 0))))
    t = pd.DataFrame(rows, columns=["factor", "definition", "side", "count_of", "n"])
    t.insert(0, "study", "context_factors_2026-10-16")
    t["split"] = "DEV"
    t["outcome_read"] = "no"
    t.to_csv(HERE / "trials.csv", index=False, lineterminator="\n")
    print(t.groupby(["factor", "definition"])["n"].sum().to_string())


def _ladder_fixed(e, wmax):
    out = pd.Series("none", index=e.index)
    for k in ("8h", "12h", "D"):          # reverse so D wins
        w = e[f"f3_w_{k}"]
        out[(w >= C.W_MIN) & (w <= wmax)] = k
    return out


if __name__ == "__main__":
    main()
