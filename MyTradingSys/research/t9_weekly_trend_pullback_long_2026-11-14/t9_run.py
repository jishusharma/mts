"""T9 step C: statistics, RESULT.md and results.json from trades.csv + the data cache. Run after t9_trades.py."""
import sys
import csv
import json
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t9_core as core  # noqa: E402
import t9_stats as st  # noqa: E402

WAVE2 = r"F:/MTS/data_cache/binance/wave2-1114"
MINER = r"F:/MTS/data_cache/binance/combo-edge-miner-1114"
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"
NUM = ("entry_px", "stop", "risk", "exit_px", "days", "gross", "fee", "funding", "net", "net_flat", "gross_R", "fee_R", "net_R",
       "net_flat_R")


def read_trades(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUM:
                r[k] = float(r[k]) if r[k] != "" else float("nan")
            r["entry_ts"], r["exit_ts"], r["w"] = int(r["entry_ts"]), int(r["exit_ts"]), int(r["w"])
            r["funding_covered"] = r["funding_covered"] == "True"
            r["ended"] = r["ended"] == "True"
            r["overlap"] = r["overlap"] == "True"
            r["entry_year"] = r["entry_date"][:4]
            out.append(r)
    return out


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if o != o else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    cls = core.set_low_priority()
    print("priority class 0x%x (0x4000 = BELOW_NORMAL)" % (cls or 0))
    slot = core.acquire_slot("t9-run")
    here = pathlib.Path(__file__).resolve().parent
    try:
        trades = read_trades(here / "trades.csv")
        state = core.load_btc_state(PHASE)
        uni = core.universe(WAVE2, MINER)
        coins, funds = {}, {}
        for name, (sp, fp) in uni.items():
            coins[name] = core.load_coin(sp, name)
            funds[name] = core.load_funding(fp)
        # ---- placebo candidates (like-for-like: only the touch trigger removed)
        cand_cache = {}
        pin = {"VAL": {"win": [], "glob": []}, "DEV": {"win": [], "glob": []}}
        for t in trades:
            c = coins[t["coin"]]
            if t["coin"] not in cand_cache:
                cand_cache[t["coin"]] = core.candidate_mondays(c, state)
            mine = [m for m in cand_cache[t["coin"]] if m["split"] == t["split"] and m["btc_state"] == t["btc_state"]]
            rw = st.week_index(t["entry_ts"])
            for key in ("win", "glob"):
                pool = [m for m in mine if key == "glob" or abs(st.week_index(m["entry_ms"]) - rw) <= 8]
                alt = [m for m in pool if m["entry_ms"] != t["entry_ts"]]
                pool = alt if alt else pool
                vals = []
                for m in pool:
                    s = core.simulate(c, m["d0"], t["risk"], funds[t["coin"]])
                    if s is not None:
                        vals.append(s["net_R"])
                pin[t["split"]][key].append((t["net_R"], vals))
        # ---- baseline basket over the calendar weeks in which a strategy trade is open
        week_set = set()
        for t in trades:
            for w in range(st.week_index(t["entry_ts"]), st.week_index(t["exit_ts"]) + 1):
                week_set.add(w)
        day_rets = {}
        for name, c in coins.items():
            for d in range(1, c.n):
                wk = d // 7 - 1
                if wk < core.FIRST_FLAG_WEEK or wk >= c.nw or not c.flag[wk] or c.dd20[wk]:
                    continue
                if state.get(core.day_str(int(c.ms[d]))) not in ("BULL", "BASE"):
                    continue
                ms = int(c.ms[d])
                fc, _cov = core.funding_cost(funds[name], ms, ms + core.DAY)
                day_rets.setdefault(ms, []).append(c.c[d] / c.c[d - 1] - 1.0 - fc)
        base = {"DEV": [], "VAL": []}
        for ms, v in day_rets.items():
            monday = ms - ((ms // core.DAY + 3) % 7) * core.DAY
            if st.week_index(monday) in week_set:
                base["DEV" if ms < core.DEV_END_MS else "VAL"].append(float(np.mean(v)))
        baseline = {k: (float(np.mean(v)) if v else float("nan")) for k, v in base.items()}
        baseline_days = {k: len(v) for k, v in base.items()}
        # ---- regime mix
        mondays = {"DEV": {}, "VAL": {}}
        for d, s in state.items():
            try:
                dd = dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
            except ValueError:
                continue
            if dd.weekday() == 0 and s and dd.year >= 2019:
                sp = "DEV" if dd.year < 2024 else "VAL"
                mondays[sp][s] = mondays[sp].get(s, 0) + 1
        mix = {}
        for sp in ("DEV", "VAL"):
            tr = [t for t in trades if t["split"] == sp]
            mix[sp] = dict(trades={k: sum(1 for t in tr if t["btc_state"] == k) for k in ("BULL", "BASE", "BEAR")},
                           mondays=mondays[sp])
        extra = dict(baseline_days=baseline_days, regime_mix=mix,
                     overlap_trades=sum(1 for t in trades if t["overlap"]),
                     ended_trades=sum(1 for t in trades if t["ended"]),
                     funding_not_in_data_total=sum(1 for t in trades if not t["funding_covered"]))
        S = st.run_stats(trades, pin, baseline, extra)
        tabs = []
        for sp in ("VAL", "DEV"):
            rows = st.sub(trades, split=sp)
            tabs.append(st.md_table("by entry year (%s, net R)" % sp, st.group_table(rows, lambda r: r["entry_year"])))
            tabs.append(st.md_table("by BTC smoothed cycle state (%s, net R)" % sp, st.group_table(rows, lambda r: r["btc_state"])))
            tabs.append(st.md_table("by exit reason (%s, net R)" % sp, st.group_table(rows, lambda r: r["exit_reason"])))
            tabs.append(st.md_table("by coin (%s, net R)" % sp, st.group_table(rows, lambda r: r["coin"])))
        (here / "tables.md").write_text("\n".join(tabs), encoding="utf-8")
        (here / "results.json").write_text(json.dumps(clean(S), indent=1), encoding="utf-8")
        write_result(here, S)
        print(S["verdict"], "VAL n", S["n_val"], "net R %.3f" % S["val_net_R"].get("mean", float("nan")))
    finally:
        core.release_slot(slot)


def _g(S, sp, k, lab):
    if k is None:
        return str(S["n_" + sp])
    v = S[sp + "_" + k]
    if isinstance(v, dict):
        return "%+.3f" % v["mean"] if v.get("n") else "NA"
    if isinstance(v, int):
        return "%d" % v
    return "%+.4f" % v if "%" in lab else "%+.3f" % v


def write_result(here, S):
    b = S["bars"]
    pv, pg = S["placebo_val_win"], S["placebo_val_glob"]
    vb, db = S["val_boot"], S["dev_boot"]
    mix = S["regime_mix"]

    def share(d):
        tot = sum(d.values()) or 1
        return " ".join("%s %.0f%%" % (k, 100.0 * v / tot) for k, v in sorted(d.items()))

    L = []
    flags = (" [" + "; ".join(S["flags"]) + "]") if S["flags"] else ""
    L.append("**T9 weekly-trend pullback long: %s%s; VAL n %d trades / %d weeks, net %+.3f R (CI %+.3f..%+.3f), DEV net %+.3f R.**" % (
        S["verdict"], flags, S["n_val"], S["val_weeks"], S["val_net_R"].get("mean", float("nan")), vb["ci_low"], vb["ci_high"],
        S["dev_net_R"].get("mean", float("nan"))))
    L.append("")
    L.append("Regime mix: DEV trades by BTC smoothed state: %s (calendar Mondays: %s); VAL trades: %s (calendar Mondays: %s). BEAR is gated out by construction." % (
        share(mix["DEV"]["trades"]), share(mix["DEV"]["mondays"]), share(mix["VAL"]["trades"]), share(mix["VAL"]["mondays"])))
    L.append("")
    L.append("| row | DEV | VAL |")
    L.append("|---|---|---|")
    for lab, k in (("trades", None), ("entry weeks", "weeks"), ("gross R mean", "gross_R"), ("net R mean (primary)", "net_R"),
                   ("net R mean, 3R-capped", "capped_net_R"), ("fee in R (mean)", "fee_R"), ("net % per trade (mean)", "net_pct"),
                   ("gross % per trade (mean)", "gross_pct"), ("net R, flat-funding sensitivity (uncovered at 1 bp per 8h)", "net_flat_R"),
                   ("week-level sd of net R", "week_sd_R"), ("independent 4-week blocks", "episodes"),
                   ("funding NOT_IN_DATA trades", "funding_not_in_data"), ("net % per day in position (pooled)", "in_pos_daily")):
        L.append("| %s | %s | %s |" % (lab, _g(S, "dev", k, lab), _g(S, "val", k, lab)))
    L.append("| bootstrap 95%% CI (4-wk moving block, 2000, seed 1114) | %+.3f..%+.3f | %+.3f..%+.3f |" % (db["ci_low"], db["ci_high"], vb["ci_low"], vb["ci_high"]))
    L.append("| basket net % per day (same weeks) | %+.4f | %+.4f |" % (S["baseline"]["DEV"], S["baseline"]["VAL"]))
    L.append("")
    L.append("## Pass bars (PRE_REG)")
    L.append("")
    L.append("| bar | result | numbers |")
    L.append("|---|---|---|")
    ps = lambda x: "PASS" if x else "FAIL"
    L.append("| 1 power (VAL n>=30, weeks>=20) | %s | n %d, weeks %d |" % (ps(b["1"]), S["n_val"], S["val_weeks"]))
    L.append("| 2 VAL mean>0 and CI low>0 | %s | %+.3f, CI low %+.3f |" % (ps(b["2"]), S["val_net_R"].get("mean", float("nan")), vb["ci_low"]))
    L.append("| 3 DEV mean>0 | %s | %+.3f (n %d)%s |" % (ps(b["3"]), S["dev_net_R"].get("mean", float("nan")), S["n_dev"], " UNDERPOWERED" if S["bar3_underpowered"] else ""))
    L.append("| 4 placebo same-window | %s | real %+.3f, draws mean %+.3f, p97.5 %+.3f, excess %+.3f, p %.3f, rank %.1f pct, n %d skipped %d |" % (
        ps(b["4"]), pv["real_mean"], pv["draw_mean"], pv["p975"], pv["excess"], pv["p"], pv.get("pct_rank", float("nan")), pv["n"], pv["skipped"]))
    L.append("| 4g placebo global (not a bar) | - | real %+.3f, draws mean %+.3f, p97.5 %+.3f, p %.3f, rank %.1f pct |" % (
        pg["real_mean"], pg["draw_mean"], pg["p975"], pg["p"], pg.get("pct_rank", float("nan"))))
    L.append("| 5 ex-best-%d weeks, 3R-capped | %s | %+.3f (n %d); uncapped %+.3f |" % (
        S["ex_best_capped"]["k"], ps(b["5"]), S["ex_best_capped"]["mean"], S["ex_best_capped"]["n"], S["ex_best_uncapped"]["mean"]))
    L.append("| 6 in-position net daily >= basket | %s | VAL strategy %+.5f vs basket %+.5f; DEV %+.5f vs %+.5f |" % (
        ps(b["6"]), S["val_in_pos_daily"], S["baseline"]["VAL"], S["dev_in_pos_daily"], S["baseline"]["DEV"]))
    L.append("| 7 top-3 coin removal | %s | %s |" % (ps(b["7"]), "; ".join("%s: %+.3f" % ("+".join(x["removed"]), x["mean"]) for x in S["top_coin"])))
    L.append("| 8 leave-one-year-out (VAL) | %s | %s ; pooled all positive: %s |" % (
        ps(b["8"]), "; ".join("-%s: %+.3f" % (y, d["mean"]) for y, d in S["loyo_val"]["by_year"].items()), S["loyo_pooled"]["all_positive"]))
    L.append("| 9 rows by state and year | printed | tables.md |")
    L.append("")
    L.append("Passed bars: %s. Failed bars: %s." % (", ".join(k for k in sorted(b) if b[k]) or "none", ", ".join(k for k in sorted(b) if not b[k]) or "none"))
    L.append("Kill criteria fired: %s." % (", ".join(S["kill_fired"]) or "none"))
    L.append("Holm: per-study p %.4f; family (9 cells) worst case %.4f." % (S["holm_p_study"], S["holm_p_family_worst"]))
    L.append("")
    L.append("## Robustness rows")
    L.append("")
    L.append("- VAL ex-ENDED trades: %s; ex-LUNA/FTT coins: %s (DEV: %s / %s). Survivorship: hindsight universe, longs biased UP." % (
        st.fmt(S["ex_ended_val"]), st.fmt(S["ex_luna_ftt_val"]), st.fmt(S["ex_ended_dev"]), st.fmt(S["ex_luna_ftt_dev"])))
    L.append("- exit reasons VAL: %s; DEV: %s." % (S["val_exit_reasons"], S["dev_exit_reasons"]))
    L.append("- same-coin overlapping trades: %d; ENDED exits: %d; funding NOT_IN_DATA trades: %d (zero funding charged)." % (
        S["overlap_trades"], S["ended_trades"], S["funding_not_in_data_total"]))
    L.append("- DEV-only positive flag: %s. Baseline days used: %s." % (S["dev_only_positive"], S["baseline_days"]))
    L.append("")
    L.append("Tables by year, BTC state, exit reason and coin: tables.md. Numbers: results.json.")
    (here / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
