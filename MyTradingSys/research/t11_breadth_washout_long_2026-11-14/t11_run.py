"""T11 runner. Modes: count (signals and units only, no outcome), trades (trade list), stats (bars, RESULT.md, results.json).
Usage: python t11_run.py count|trades|stats
Reads F:/MTS/data_cache (never committed). Sets itself to BELOW_NORMAL priority and takes a heavy-job slot.
"""
import sys
import csv
import json
import time
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t11_core as core  # noqa: E402
import t11_stats as st  # noqa: E402

ROOT = pathlib.Path(r"F:/MTS/data_cache/binance")
W2, MN = ROOT / "wave2-1114", ROOT / "combo-edge-miner-1114"
PHASE = r"F:/MTS/data_cache/mts_brains/phase_daily.csv"
SLOTS = pathlib.Path(r"F:/MTS/data_cache/wave3-1114/_slots")
SLOT_ID = "t11"


class Slot:
    def __enter__(self):
        SLOTS.mkdir(parents=True, exist_ok=True)
        while True:
            now = time.time()
            live = [p for p in SLOTS.glob("*.lock") if now - p.stat().st_mtime < 1800 and p.name != SLOT_ID + ".lock"]
            if len(live) < 4:
                break
            time.sleep(30)
        (SLOTS / (SLOT_ID + ".lock")).write_text(str(now), encoding="utf-8")
        return self

    def __exit__(self, *a):
        try:
            (SLOTS / (SLOT_ID + ".lock")).unlink()
        except OSError:
            pass


def _d(day):
    return dt.datetime.fromtimestamp(int(day) * 86400, dt.timezone.utc).strftime("%Y-%m-%d")


def build():
    names = sorted({p.name[:-8] for p in (W2 / "spot_1d").glob("*USDT.csv")} |
                   {p.name[:-8] for p in (MN / "spot_1d").glob("*USDT.csv")})
    coins, funds, src = [], {}, {}
    for n in names:
        p = W2 / "spot_1d" / (n + "USDT.csv")
        folder = W2
        if not p.exists():
            p, folder = MN / "spot_1d" / (n + "USDT.csv"), MN
        coins.append(core.load_coin(p, n))
        src[n] = folder.name
        fp = folder / "funding" / (n + "USDT.csv")
        if not fp.exists():
            for alt in (W2, MN):
                if (alt / "funding" / (n + "USDT.csv")).exists():
                    fp = alt / "funding" / (n + "USDT.csv")
                    break
        funds[n] = core.load_funding(fp)
    mkt = core.Market(coins)
    btc = next(c for c in coins if c.name == "BTC")
    flag = core.sma_flag(btc.c)
    raw = core.load_phase_cycle(PHASE)
    days = sorted(raw)
    sm = core.smooth_state([raw[d] for d in days])
    state_by_day = dict(zip(days, sm))
    return dict(mkt=mkt, funds=funds, names=names, src=src, btc=btc, flag=flag, state=state_by_day, raw=raw)


def above_at(B, day):
    i = day - B["btc"].day0
    if 0 <= i < len(B["flag"]):
        v = B["flag"][i]
        return float(v) if v == v else float("nan")
    return float("nan")


def state_at(B, day):
    """Smoothed BTC state for signal day t = row of day t+1 (built from closes through t)."""
    return B["state"].get(day + 1, "NA")


def events(B):
    mkt = B["mkt"]
    out = []
    for d in core.find_events(mkt.breadth):
        day = mkt.dmin + d
        out.append(dict(d=d, day=day, B=float(mkt.breadth[d]), n_alive=int(mkt.n_alive[d]),
                        eligible=bool(mkt.n_alive[d] >= core.MIN_ALIVE), state=state_at(B, day),
                        above=above_at(B, day)))
    return out


def valid_legs(B, ev):
    """Leg signals for an event with window validity (count only: reads valid/hole/incomplete flags)."""
    mkt = B["mkt"]
    sigs = core.leg_signals(mkt, ev["d"])
    keep, skipped = [], dict(incomplete=0, hole=0)
    for s in sigs:
        c = mkt.coins[s["ci"]]
        P = core.path_arrays(c, [s["d0"]], B["funds"][c.name])
        if P["valid"][0]:
            keep.append(s)
        elif P["hole"][0]:
            skipped["hole"] += 1
        else:
            skipped["incomplete"] += 1
    return sigs, keep, skipped


def cell_counts(evs):
    """evs: eligible events with at least one valid leg. Episodes per split for the cell."""
    days = sorted(e["day"] for e in evs)
    ids = core.merge_episodes(days)
    first = {}
    for d, i in zip(days, ids):
        first.setdefault(i, d)
    out = dict(DEV=0, VAL=0)
    for i, d in first.items():
        out[st.split_of_day(d)] += 1
    ev_split = dict(DEV=sum(1 for d in days if st.split_of_day(d) == "DEV"),
                    VAL=sum(1 for d in days if st.split_of_day(d) == "VAL"))
    return dict(episodes=out, events=ev_split)


def count():
    B = build()
    mkt = B["mkt"]
    evs = events(B)
    rows, excluded, nolegs = [], [], []
    for e in evs:
        if not e["eligible"]:
            excluded.append(e)
            continue
        sigs, keep, sk = valid_legs(B, e)
        e2 = dict(e, signals=len(sigs), legs=len(keep), skipped=sk, pcts=[s["pct"] for s in keep])
        if not keep:
            nolegs.append(e2)
            continue
        rows.append(e2)
    primary = cell_counts(rows)
    secondary = cell_counts([e for e in rows if e["above"] == 1.0])
    allp = [p for e in rows for p in e["pcts"]]
    med = float(np.median(allp)) if allp else float("nan")
    C = dict(coins=B["names"], n_coins=len(B["names"]), coin_source=B["src"],
             first_day=_d(mkt.dmin), last_day=_d(mkt.dmax),
             events_total=len(evs), events_lt30_alive=len(excluded), events_no_valid_leg=len(nolegs),
             events_used=len(rows), primary=primary, secondary_above_sma200=secondary,
             legs_total=sum(e["legs"] for e in rows),
             legs_dev=sum(e["legs"] for e in rows if st.split_of_day(e["day"]) == "DEV"),
             legs_val=sum(e["legs"] for e in rows if st.split_of_day(e["day"]) == "VAL"),
             median_stop_pct=med, median_fee_R=core.FEE_RT / med if med == med else float("nan"),
             min_stop_pct=float(min(allp)) if allp else float("nan"),
             val_events_by_bin={k: sum(1 for e in rows if st.split_of_day(e["day"]) == "VAL" and lo <= e["B"] < hi)
                                for k, lo, hi in (("15-30", .15, .30), ("30-50", .30, .50), (">=50", .50, 9))},
             val_events_above=sum(1 for e in rows if st.split_of_day(e["day"]) == "VAL" and e["above"] == 1.0),
             val_events_below=sum(1 for e in rows if st.split_of_day(e["day"]) == "VAL" and e["above"] == 0.0),
             dev_events_above=sum(1 for e in rows if st.split_of_day(e["day"]) == "DEV" and e["above"] == 1.0),
             dev_events_below=sum(1 for e in rows if st.split_of_day(e["day"]) == "DEV" and e["above"] == 0.0),
             events_by_state={sp: {s: sum(1 for e in rows if st.split_of_day(e["day"]) == sp and e["state"] == s)
                                   for s in ("BEAR", "BASE", "BULL", "NA")} for sp in ("DEV", "VAL")},
             event_list=[dict(date=_d(e["day"]), B=round(e["B"], 3), alive=e["n_alive"], signals=e["signals"],
                              legs=e["legs"], state=e["state"], above=e["above"], skipped=e["skipped"]) for e in rows],
             excluded_lt30_alive=[dict(date=_d(e["day"]), B=round(e["B"], 3), alive=e["n_alive"]) for e in excluded],
             no_valid_leg=[dict(date=_d(e["day"]), B=round(e["B"], 3)) for e in nolegs])
    (HERE / "counts.json").write_text(json.dumps(C, indent=1, default=str), encoding="utf-8")
    (HERE / "coins.json").write_text(json.dumps(dict(n=len(B["names"]), coins=B["names"], source=B["src"]), indent=1),
                                     encoding="utf-8")
    keys = ["n_coins", "first_day", "last_day", "events_total", "events_lt30_alive", "events_no_valid_leg", "events_used",
            "primary", "secondary_above_sma200", "legs_total", "legs_dev", "legs_val", "median_stop_pct",
            "median_fee_R", "min_stop_pct", "val_events_by_bin", "val_events_above", "val_events_below",
            "dev_events_above", "dev_events_below", "events_by_state"]
    for k in keys:
        print(k, "=", C[k])


COLS = ["coin", "sig_day", "sig_date", "entry_date", "exit_date", "B", "state", "above", "rsi", "pct", "entry_px",
        "gross", "fee", "funding", "funding_rule", "net", "gross_R", "net_R", "fee_R", "days_held", "exit_reason",
        "ended", "iso_week", "basket_pd", "net_pd"]


def trades():
    B = build()
    legs = st.make_legs(B["mkt"], B["funds"], lambda d: state_at(B, d), lambda d: above_at(B, d))
    rows = []
    for l in legs:
        r = dict(l)
        for k in ("B", "rsi", "pct", "gross", "funding", "net", "gross_R", "net_R", "fee_R", "basket_pd", "net_pd"):
            r[k] = repr(round(l[k], 8))
        r["entry_px"], r["fee"] = repr(l["entry_px"]), repr(l["fee"])
        r["ended"] = int(l["ended"])
        rows.append(r)
    with open(HERE / "trades.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("trades written:", len(rows), "legs;", len({r["sig_day"] for r in rows}), "events")


NUM = ("B", "above", "rsi", "pct", "entry_px", "gross", "fee", "funding", "net", "gross_R", "net_R", "fee_R",
       "basket_pd", "net_pd")


def read_trades():
    out = []
    with open(HERE / "trades.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUM:
                r[k] = float(r[k])
            r["sig_day"] = int(r["sig_day"])
            r["days_held"] = int(r["days_held"])
            r["ended"] = bool(int(r["ended"]))
            out.append(r)
    return out


def fmt(x, p=4):
    return "n/a" if x is None or x != x else ("%+.*f" % (p, x))


def regime_mix(legs):
    out = []
    for sp in ("DEV", "VAL"):
        ev = {}
        for l in st.sub(legs, split=sp):
            ev[l["sig_day"]] = l
        n = len(ev)
        if not n:
            out.append("%s none" % sp)
            continue
        sh = {s: sum(1 for l in ev.values() if l["state"] == s) / n for s in ("BULL", "BASE", "BEAR")}
        ab = sum(1 for l in ev.values() if l["above"] == 1.0) / n
        out.append("%s events %d: BULL %.0f%% BASE %.0f%% BEAR %.0f%%, BTC above SMA200d %.0f%%" %
                   (sp, n, 100 * sh["BULL"], 100 * sh["BASE"], 100 * sh["BEAR"], 100 * ab))
    return "; ".join(out)


def stats():
    B = build()
    legs = read_trades()
    pools = st.pool_entries(B["mkt"], B["funds"], lambda d: state_at(B, d))
    prim = [dict(l) for l in legs]
    sec = [dict(l) for l in legs if l["above"] == 1.0]
    res = {}
    for name, rows in (("primary", prim), ("btc_above_sma200", sec)):
        st.assign_episodes(rows)
        res[name] = st.run_cell(rows, pools)
    p1 = res["primary"]["VAL"]["boot_episode"]["p_le0"]
    p2 = res["btc_above_sma200"]["VAL"]["boot_episode"]["p_le0"]
    ps = {"primary": p1, "btc_above_sma200": p2}
    hm = st.holm(ps)
    res["holm_study_m2"] = hm
    res["family_worst_case_m9"] = {k: min(1.0, 9 * v) for k, v in ps.items()}
    res["regime_mix"] = regime_mix(prim)
    (HERE / "results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    write_result(res, prim)
    print("verdict primary:", res["primary"]["verdict"], "| secondary:", res["btc_above_sma200"]["verdict"])


def write_result(res, prim):
    P, S = res["primary"], res["btc_above_sma200"]
    L = []
    L.append("**T11 breadth washout long: %s (primary cell, 1d, VAL episodes %d); BTC > SMA200d row: %s**" %
             (P["verdict"], P["VAL"]["episodes"], S["verdict"]))
    L.append("")
    L.append("Regime mix: " + res["regime_mix"])
    L.append("")
    L.append("Research, not advice. Fee 12 bp (fees.py) + real funding, stop max(2.5 ATR14, 8%), exit close of day 10. "
             "Unit = episode (events within 14 days merged). R = return / stop distance. Survivorship: longs biased UP.")
    L.append("")
    L.append("| cell | split | events | episodes | legs | gross R | net R | fee R | net % | CI95 episode | CI95 event | "
             "CI95 week | DEV/VAL n pooled |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for nm, C in (("primary", P), ("BTC>SMA200d", S)):
        for sp in ("DEV", "VAL"):
            b = C[sp]
            L.append("| %s | %s | %d | %d | %d | %s | %s | %s | %s | [%s, %s] | [%s, %s] | [%s, %s] | |" % (
                nm, sp, b["events"], b["episodes"], b["legs"], fmt(b["gross_R"]), fmt(b["net_R"]), fmt(b["fee_R"]),
                fmt(100 * b["net_pct"], 2), fmt(b["boot_episode"]["ci_low"]), fmt(b["boot_episode"]["ci_high"]),
                fmt(b["boot_event"]["ci_low"]), fmt(b["boot_event"]["ci_high"]), fmt(b["boot_week"]["ci_low"]),
                fmt(b["boot_week"]["ci_high"])))
    L.append("")
    L.append("Pooled DEV+VAL is a power row only: %d episodes, %d events." % (
        P["DEV"]["episodes"] + P["VAL"]["episodes"], P["DEV"]["events"] + P["VAL"]["events"]))
    L.append("")
    for nm, C in (("primary", P), ("BTC>SMA200d row", S)):
        L.append("### Bars, %s (verdict %s)" % (nm, C["verdict"]))
        L.append("")
        L.append("| bar | met |")
        L.append("|---|---|")
        for k, v in C["bars"].items():
            L.append("| %s | %s |" % (k, "PASS" if v else "not met"))
        L.append("")
        L.append("Kill criteria: " + ", ".join("%s=%s" % (k, v) for k, v in C["kill"].items()))
        L.append("")
        pb = C["placebo"]
        L.append("| placebo (VAL) | legs | real | draw mean | p97.5 | excess | p | fallbacks (global/state) | skipped |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for k in ("VAL_pri_window", "VAL_pri_global", "VAL_sec_window", "VAL_sec_global",
                  "DEV_pri_window", "DEV_pri_global"):
            q = pb[k]
            if q.get("n_legs", 0) == 0:
                L.append("| %s | 0 | | | | | | | |" % k)
                continue
            L.append("| %s | %d | %s | %s | %s | %s | %.3f | %d/%d | %d |" % (
                k, q["n_legs"], fmt(q["real"]), fmt(q["draw_mean"]), fmt(q["p975"]), fmt(q["excess"]), q["p"],
                q["fb_global"], q["fb_state"], q["skipped"]))
        L.append("")
        L.append("Robustness (VAL): ex-best-2 episodes %s (dropped %s); leave-one-event-out min %s max %s flips %d; "
                 "ex-LUNA/FTT %s; ex-ENDED %s; top-3 coin removal %s; per-day net %s vs basket %s." % (
                     fmt(C["ex_best2_eps"]["mean"]), C["ex_best2_eps"]["dropped"], fmt(C["loeo"]["min"]),
                     fmt(C["loeo"]["max"]), C["loeo"]["flips"], fmt(C["ex_luna_ftt"]["mean"]),
                     fmt(C["ex_ended"]["mean"]),
                     "; ".join("%s -> %s" % (t["removed"], fmt(t["mean"])) for t in C["top_coin"]),
                     fmt(C["VAL"]["net_pd"], 5), fmt(C["VAL"]["basket_pd"], 5)))
        L.append("")
        L.append("Leave-one-year-out (VAL): " + "; ".join("without %s: %s (%d eps)" % (y, fmt(v["mean"]), v["n_eps"])
                                                         for y, v in C["loyo"].items()))
        L.append("")
        L.append("Dose-response VAL: " + "; ".join("%s: %d ev %s" % (k, v["events"], fmt(v["mean"]))
                                                   for k, v in C["dose_val"]["bins"].items()) +
                 " (testable %s, monotone %s). Pooled: " % (C["dose_val"]["testable"], C["dose_val"]["monotone"]) +
                 "; ".join("%s: %d ev %s" % (k, v["events"], fmt(v["mean"]))
                           for k, v in C["dose_pooled"]["bins"].items()) +
                 " (monotone %s)." % C["dose_pooled"]["monotone"])
        L.append("")
        sv, sd, sp_ = C["strata_val"], C["strata_dev"], C["strata_pooled"]
        L.append("Strata prediction: VAL above %s (%d ev), below %s (%d ev), holds %s; DEV above %s (%d), below %s (%d); "
                 "pooled above %s, below %s." % (
                     fmt(sv["above"]["mean"]), sv["above"]["events"], fmt(sv["below"]["mean"]), sv["below"]["events"],
                     sv["holds"], fmt(sd["above"]["mean"]), sd["above"]["events"], fmt(sd["below"]["mean"]),
                     sd["below"]["events"], fmt(sp_["above"]["mean"]), fmt(sp_["below"]["mean"])))
        L.append("")
        for title, key in (("by BTC smoothed state", "by_state"), ("by BTC vs SMA200d", "by_above"), ("by year", "by_year")):
            L.append("| %s | split | key | legs | events | episodes | mean event net R | mean leg net R |" % title)
            L.append("|---|---|---|---|---|---|---|---|")
            for sp in ("DEV", "VAL"):
                for k, v in C[key][sp].items():
                    L.append("| | %s | %s | %d | %d | %d | %s | %s |" % (sp, k, v["legs"], v["events"], v["episodes"],
                                                                       fmt(v["mean_event"]), fmt(v["mean_leg"])))
            L.append("")
    L.append("Holm over the two T11 cells (m=2): %s. Worst-case family adjustment (9 x p): %s." % (
        {k: round(v, 4) for k, v in res["holm_study_m2"].items()},
        {k: round(v, 4) for k, v in res["family_worst_case_m9"].items()}))
    L.append("")
    L.append("Funding NOT_IN_DATA legs (funding 0): VAL %d, DEV %d. Exit reasons VAL: %s." % (
        P["VAL"]["funding_not_in_data"], P["DEV"]["funding_not_in_data"], P["VAL"]["flat_exits"]))
    L.append("")
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("count", "trades", "stats"):
        sys.exit("usage: t11_run.py count|trades|stats")
    cls = core.set_below_normal()
    print("priority class: 0x%x (0x4000 = BELOW_NORMAL)" % cls if cls >= 0 else "priority class: unavailable")
    with Slot():
        {"count": count, "trades": trades, "stats": stats}[mode]()
