"""T8 stage 3: statistics on the trades list and RESULT.md / results.json. Reads real data (BelowNormal + slot).
Usage: python t8_report.py
"""
import sys
import json
import pathlib
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t8_core as core  # noqa: E402
import t8_stats as st  # noqa: E402
import t8_trades as tt  # noqa: E402

RANGE_LABELS = ("ACCUM-RANGE", "DISTRIBUTION")


def episodes_of(phase):
    """{date: episode id} for BTC days whose label is ACCUM-RANGE or DISTRIBUTION; a maximal run of such days = one episode."""
    import datetime as dt
    ep, cur, prev = {}, 0, None
    for d in sorted(phase):
        if phase[d][0] in RANGE_LABELS:
            day = dt.date.fromisoformat(d)
            if prev is None or (day - prev).days != 1:
                cur += 1
            ep[d] = cur
            prev = day
        else:
            prev = None
    return ep


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if o != o else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def mix_line(rows):
    if not rows:
        return "none"
    n = len(rows)
    lab_r = sum(1 for r in rows if r["label"] == "ACCUM-RANGE") / n
    lab_d = sum(1 for r in rows if r["label"] == "DISTRIBUTION") / n
    cyc = {k: sum(1 for r in rows if r["cycle"] == k) / n for k in ("BULL", "BASE", "BEAR", "NA")}
    return "ACCUM-RANGE %.0f%%, DISTRIBUTION %.0f%%, other labels %.0f%%; cycle BULL %.0f%% / BASE %.0f%% / BEAR %.0f%% / NA %.0f%%" % (
        100 * lab_r, 100 * lab_d, 100 * (1 - lab_r - lab_d), 100 * cyc["BULL"], 100 * cyc["BASE"], 100 * cyc["BEAR"], 100 * cyc["NA"])


def f(x, d=3):
    return "n/a" if x is None or x != x else ("%+." + str(d) + "f") % x


def main():
    print(core.set_low_priority())
    lock = core.acquire_slot("t8-report")
    try:
        _main()
    finally:
        core.release_slot(lock)


def _main():
    uni, funds, cnt_days, uend = core.load_universe()
    phase = core.load_phase_table(core.PHASE)
    eps = episodes_of(phase)
    cells, tabs, trades_by = {}, {}, {}
    for tf in ("1d", "4h"):
        rows, c = core.build_trades(uni[tf], funds, tf)
        tt.tag_phase(rows, phase)
        trades_by[tf] = rows
        S, tb = st.run_cell(rows, funds, tf, eps)
        S["skip_counts"] = c
        cells[tf] = S
        tabs[tf] = tb
        print(tf, "VAL n", S["n_val"], "DEV n", S["n_dev"], "net R VAL", S["val_net_R"].get("mean"), flush=True)
    # Holm over the two cells; worst-case family value
    ps = {tf: cells[tf]["p_val"] for tf in cells}
    adj = st.holm(ps)
    for tf in cells:
        b = dict(cells[tf]["bars"])
        b["holm_adj"] = adj[tf]
        cells[tf]["holm_adj_m2"] = adj[tf]
        cells[tf]["family9_worst_case"] = min(1.0, 9 * ps[tf])
        cells[tf]["verdict"] = st.assemble_verdict(b)
    P, Q = cells["1d"], cells["4h"]
    names = {"bar1": "1 VAL n>=200 and weeks>=40", "bar2": "2 VAL net>0 and CI low>0", "bar3": "3 DEV net>0",
             "bar4": "4 placebo p97.5 and excess CI low>0", "bar5": "5 ex-best-5 weeks>0", "bar6": "6 baselines (bracket, 20d hold)",
             "bar7": "7 top coin / top-3 removal>0", "bar8": "8 leave-one-year-out>0", "mirror_pos": "M real minus mirror>0",
             "sides_pos": "S both sides>0", "worst_week_ok": "W worst week > -4 R"}
    pass_fail = {tf: dict(passed=[names[k] for k in names if cells[tf]["bars"][k]],
                          failed=[names[k] for k in names if not cells[tf]["bars"][k]]) for tf in cells}
    allv = trades_by["1d"]
    regime = "Regime mix: VAL 1d trades %s. DEV 1d trades %s. VAL 4h trades %s." % (
        mix_line([r for r in allv if r["split"] == "VAL"]), mix_line([r for r in allv if r["split"] == "DEV"]),
        mix_line([r for r in trades_by["4h"] if r["split"] == "VAL"]))
    L = []
    L.append("**%s: T8 Bollinger range-to-range, 1d primary cell, VAL n %d trades over %d entry weeks, net %s R (CI %s to %s), gross %s R, fee %s R.**" % (
        P["verdict"], P["n_val"], P["val_weeks"], f(P["val_net_R"].get("mean")), f(P["val_boot"]["ci_low"]),
        f(P["val_boot"]["ci_high"]), f(P["val_gross_R"].get("mean")), f(P["val_fee_R_mean"])))
    L.append("")
    L.append(regime)
    L.append("")
    L.append("4h secondary row verdict: **%s** (VAL n %d, %d weeks, net %s R). Kill status 1d: %s." % (
        Q["verdict"], Q["n_val"], Q["val_weeks"], f(Q["val_net_R"].get("mean")),
        "KILLED (1d range-to-range dead)" if (P["bars"]["kill_val_le0"] or P["bars"]["kill_mirror_le0"] or P["bars"]["kill_placebo"]) and P["bars"]["bar1"] else "not triggered or underpowered"))
    L.append("")
    L.append("## Summary table (R units; VAL = signal bar >= 2024-01-01)")
    L.append("")
    L.append("| cell | split | n | weeks | gross R | fee R | net R | net CI low | net CI high | net % per trade | mirror net R | real minus mirror (CI) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tf, S in cells.items():
        for sp in ("val", "dev"):
            wk = S["val_weeks"] if sp == "val" else S["dev_weeks"]
            bt = S["val_boot"] if sp == "val" else S["dev_boot"]
            rm = ("%s (%s, %s)" % (f(S["val_real_minus_mirror"]["mean"]), f(S["val_real_minus_mirror"]["ci_low"]),
                                   f(S["val_real_minus_mirror"]["ci_high"]))) if sp == "val" else f(S["dev_real_minus_mirror"])
            L.append("| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                tf, sp.upper(), S["n_" + sp], wk, f(S[sp + "_gross_R"].get("mean")), f(S[sp + "_fee_R_mean"]),
                f(S[sp + "_net_R"].get("mean")), f(bt["ci_low"]), f(bt["ci_high"]), f(S[sp + "_net_pct"], 2),
                f(S[sp + "_mirror_net_R"].get("mean")), rm))
    L.append("")
    L.append("## Bars (numbered; PRE_REG pass bars)")
    L.append("")
    for tf in cells:
        L.append("- **%s** passed: %s" % (tf, "; ".join(pass_fail[tf]["passed"]) or "none"))
        L.append("- **%s** failed: %s" % (tf, "; ".join(pass_fail[tf]["failed"]) or "none"))
    L.append("")
    L.append("## Detail, 1d primary (VAL)")
    L.append("")
    pw, pg = P["placebo_window"], P["placebo_global"]
    L.append("| item | value |")
    L.append("|---|---|")
    L.append("| p one-sided (week-block bootstrap) | %.4f; Holm m=2 adjusted %.4f; worst-case family-of-9 %.4f |" % (P["p_val"], P["holm_adj_m2"], P["family9_worst_case"]))
    L.append("| by side VAL net R (n) | long %s (%d), short %s (%d) |" % (
        f(P["val_by_side"]["long"].get("mean")), P["val_by_side"]["long"].get("n", 0),
        f(P["val_by_side"]["short"].get("mean")), P["val_by_side"]["short"].get("n", 0)))
    L.append("| by side VAL net R CI | long [%s, %s], short [%s, %s] |" % (
        f(P["val_by_side_boot"]["long"]["ci_low"]), f(P["val_by_side_boot"]["long"]["ci_high"]),
        f(P["val_by_side_boot"]["short"]["ci_low"]), f(P["val_by_side_boot"]["short"]["ci_high"])))
    L.append("| placebo same-window (n, real, draw mean, p97.5, excess, p, excess CI) | %d, %s, %s, %s, %s, %.4f, [%s, %s] |" % (
        pw.get("n", 0), f(pw.get("real_mean")), f(pw.get("draw_mean")), f(pw.get("p975")), f(pw.get("excess")),
        pw.get("p", float("nan")), f(pw.get("excess_ci_low")), f(pw.get("excess_ci_high"))))
    L.append("| placebo global (n, real, draw mean, p97.5, excess, p) | %d, %s, %s, %s, %s, %.4f |" % (
        pg.get("n", 0), f(pg.get("real_mean")), f(pg.get("draw_mean")), f(pg.get("p975")), f(pg.get("excess")), pg.get("p", float("nan"))))
    L.append("| baselines daily net return: real / 1:1 bracket / 20d hold | %s / %s / %s |" % (
        f(pw.get("real_daily"), 5), f(pw.get("bracket_daily"), 5), f(pw.get("hold_daily"), 5)))
    L.append("| ex-best-5 weeks (n, mean R) | %d, %s |" % (P["ex_best5"]["n"], f(P["ex_best5"]["mean"])))
    L.append("| top-coin removal 1 / 2 / 3 (mean R) | %s |" % " / ".join(f(x["mean"]) for x in P["top_coin_removal"]))
    L.append("| removed coins | %s |" % ", ".join(P["top_coin_removal"][-1]["removed"]) if P["top_coin_removal"] else "| removed coins | n/a |")
    L.append("| leave-one-year-out (VAL) | %s |" % ", ".join("%s %s" % (k, f(v["mean"])) for k, v in P["loyo"].items()))
    L.append("| worst entry week sum (R) | %s |" % f(P["worst_week_R"], 2))
    L.append("| ex-ENDED VAL / ex-LUNA-FTT VAL (net R, n) | %s (%d) / %s (%d) |" % (
        f(P["ex_ended"].get("mean")), P["ex_ended"].get("n", 0), f(P["ex_luna_ftt"].get("mean")), P["ex_luna_ftt"].get("n", 0)))
    L.append("| exits VAL | %s |" % ", ".join("%s %d" % kv for kv in P["val_exit_mix"].items()))
    L.append("| funding NOT_IN_DATA trades (VAL / DEV); covered-only VAL net R | %d / %d; %s (n %d) |" % (
        P["val_fund_not_in_data"], P["dev_fund_not_in_data"], f(P["val_funding_covered_net_R"].get("mean")),
        P["val_funding_covered_net_R"].get("n", 0)))
    L.append("| fee-only VAL net R (no funding) | %s |" % f(P["val_nofund_R"].get("mean")))
    L.append("| ENDED trades VAL / DEV | %d / %d |" % (P["val_ended"], P["dev_ended"]))
    L.append("| realised sd: per-trade VAL net R / DEV week-level sd of weekly sums | %s / %s |" % (f(P["val_net_R"].get("sd")), f(P["dev_week_sd"])))
    ep = P.get("val_episodes", {})
    L.append("| second unit: BTC range episodes VAL (episodes, trades, mean of episode means, CI) | %d, %d, %s, [%s, %s] |" % (
        ep.get("episodes", 0), ep.get("trades", 0), f(ep.get("mean_of_episode_means")), f(ep.get("ci_low")), f(ep.get("ci_high"))))
    L.append("| pass-bar 9: SIGN-FLIP | not applicable (no cycle gate) |")
    L.append("")
    L.append("Survivorship: longs biased up, shorts biased down (hindsight universe; ENDED coins exit at their last close). Short side on spot as a perp proxy.")
    L.append("")
    L.append("## Rows by BTC cycle state, label and year (1d, net R)")
    L.append("")
    L.append(tabs["1d"])
    L.append("## 4h secondary row (VAL net R detail)")
    L.append("")
    pw4 = Q["placebo_window"]
    L.append("4h: VAL n %d, weeks %d, net %s R CI [%s, %s], DEV net %s R, real minus mirror %s, placebo p97.5 %s vs real %s, sides long %s short %s, top-coin removal %s." % (
        Q["n_val"], Q["val_weeks"], f(Q["val_net_R"].get("mean")), f(Q["val_boot"]["ci_low"]), f(Q["val_boot"]["ci_high"]),
        f(Q["dev_net_R"].get("mean")), f(Q["val_real_minus_mirror"]["mean"]), f(pw4.get("p975")), f(pw4.get("real_mean")),
        f(Q["val_by_side"]["long"].get("mean")), f(Q["val_by_side"]["short"].get("mean")),
        " / ".join(f(x["mean"]) for x in Q["top_coin_removal"])))
    L.append("")
    L.append(tabs["4h"])
    L.append("")
    L.append("Holm m=2 over the two bootstrap p-values: 1d %.4f, 4h %.4f (raw %.4f, %.4f)." % (adj["1d"], adj["4h"], ps["1d"], ps["4h"]))
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    slim = {tf: {k: v for k, v in S.items() if k not in ("val_by_cycle", "val_by_label", "val_by_year", "dev_by_cycle", "dev_by_year")}
            for tf, S in cells.items()}
    for tf in slim:
        slim[tf]["val_by_cycle"] = {k: dict(n=v["n"], mean=v.get("mean")) for k, v in cells[tf]["val_by_cycle"].items()}
        slim[tf]["val_by_year"] = {k: dict(n=v["n"], mean=v.get("mean")) for k, v in cells[tf]["val_by_year"].items()}
        slim[tf]["val_by_label"] = {k: dict(n=v["n"], mean=v.get("mean")) for k, v in cells[tf]["val_by_label"].items()}
    (HERE / "results.json").write_text(json.dumps(clean(dict(cells=slim, pass_fail=pass_fail, holm=adj, regime=regime)), indent=1),
                                       encoding="utf-8")
    print("verdict 1d:", P["verdict"], "| 4h:", Q["verdict"])


if __name__ == "__main__":
    main()
