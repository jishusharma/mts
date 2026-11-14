"""T12 run: trades list, statistics per PRE_REG, RESULT.md and results.json. Rules are frozen in PRE_REG.md; this script
only executes them. Reads the real cache; BelowNormal priority and a heavy-job slot are taken at the top."""
import sys
import csv
import json
import pathlib
import datetime as dt
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t12_core as core  # noqa: E402
import t12_stats as st  # noqa: E402

DAY = core.DAY
WIN_DAYS = 56          # +/- 8 ISO weeks
LUNA_FTT = ("LUNAUSDT", "FTTUSDT")


def year_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).year


def ymd(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d")


def load_oi():
    out = {}
    for p in (core.MN / "oi").glob("*.csv"):
        a = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1)))
        out[p.stem] = {int((t + 1) // DAY - 1): v for t, v in a}
    return out


def build_cell(cell, coins, funds, phase, alive, oi):
    side = core.CELLS[cell]["side"]
    trades, noflag = [], {}
    base_days = {}
    skips = {}
    for c in coins:
        f = funds.get(c.name)
        flags = core.day_flags(c, f, phase, cell, alive)
        noflag[c.name] = [r for r in flags if not r["rev"]]
        for r in flags:                                         # baseline: flagged-state days (VAL only)
            ms = int(c.ms[r["i"]])
            if core.split_of(ms) != "VAL":
                continue
            fr = core.flagged_next_day(c, f, r["i"], side)
            if fr is not None:
                base_days.setdefault(ms // DAY, []).append(fr)
        for r in core.signals(c, f, phase, cell, alive):
            p, why = core.plan_trade(c, f, r["i"], side)
            if p is None:
                skips[why] = skips.get(why, 0) + 1
                continue
            t = core.simulate_plan(c, f, p)
            day = p["sig_ms"] // DAY
            t.update(cell=cell, label=r["label"], cycle=phase.cycle(day), year=year_of(p["sig_ms"]),
                     lunaftt=c.name in LUNA_FTT)
            o = oi.get(c.name)
            if o and day in o and day - 7 in o and o[day - 7] > 0:
                t["oi7"] = o[day] / o[day - 7] - 1.0
            else:
                t["oi7"] = float("nan")
            trades.append(t)
    return trades, noflag, base_days, skips


def placebo_pairs(cell, rows, coins_by_name, funds, noflag, window):
    side = core.CELLS[cell]["side"]
    out = dict(netp=[], nett=[])
    for t in rows:
        c = coins_by_name[t["coin"]]
        f = funds[t["coin"]]
        cn, ct = [], []
        for r in noflag[t["coin"]]:
            ms = int(c.ms[r["i"]])
            if core.split_of(ms) != "VAL" or r["i"] == t["i"] or r["label"] != t["label"]:
                continue
            if window and abs(ms - t["sig_ms"]) > WIN_DAYS * DAY:
                continue
            p, _ = core.plan_trade(c, f, r["i"], side, stop_pct=t["stop_pct"])
            if p is None:
                continue
            s = core.simulate_plan(c, f, p)
            cn.append(s["netp_R"])
            ct.append(s["nett_R"])
        out["netp"].append((t["netp_R"], np.array(cn)))
        out["nett"].append((t["nett_R"], np.array(ct)))
    return out


def fmt(x, d=3):
    return "nan" if x != x else ("%.*f" % (d, x))


def evaluate(cell, trades, coins_by_name, funds, noflag, base_days):
    dev = [t for t in trades if t["split"] == "DEV"]
    val = [t for t in trades if t["split"] == "VAL"]
    res = dict(cell=cell, n_dev=len(dev), n_val=len(val))
    summ = {}
    for name, rows in (("DEV", dev), ("VAL", val)):
        summ[name] = dict(n=len(rows), weeks=len({r["week"] for r in rows}),
                          gross_R=st.mean([r["gross_R"] for r in rows]), fee_R=st.mean([r["fee_R"] for r in rows]),
                          fund_R=st.mean([r["fund_R"] for r in rows]), netp_R=st.mean([r["netp_R"] for r in rows]),
                          nett_R=st.mean([r["nett_R"] for r in rows]),
                          gross_pct=100 * st.mean([r["gross"] for r in rows]), netp_pct=100 * st.mean([r["netp"] for r in rows]),
                          nett_pct=100 * st.mean([r["nett"] for r in rows]),
                          carry_bp=1e4 * st.mean([r["fund"] for r in rows]),
                          reasons={k: sum(1 for r in rows if r["reason"] == k) for k in ("TIME", "STOP", "STOP-GAP", "ENDED")},
                          stop_pct_median=100 * float(np.median([r["stop_pct"] for r in rows])) if rows else float("nan"))
    res["summary"] = summ
    bp, bt = st.block_bootstrap(val, "netp_R"), st.block_bootstrap(val, "nett_R")
    res["boot_val_price"], res["boot_val_total"] = bp, bt
    res["boot_dev_price"], res["boot_dev_total"] = st.block_bootstrap(dev, "netp_R"), st.block_bootstrap(dev, "nett_R")
    pw = placebo_pairs(cell, val, coins_by_name, funds, noflag, True)
    pg = placebo_pairs(cell, val, coins_by_name, funds, noflag, False)
    res["placebo_window_price"], res["placebo_window_total"] = st.placebo(pw["netp"]), st.placebo(pw["nett"])
    res["placebo_global_price"], res["placebo_global_total"] = st.placebo(pg["netp"]), st.placebo(pg["nett"])
    wk = len({r["week"] for r in val})
    ex = st.ex_best_weeks(val, k=5 if wk >= 30 else 2)
    res["ex_best"] = ex
    res["ex_best_total"] = st.ex_best_weeks(val, k=5 if wk >= 30 else 2, val="nett_R")
    res["top3"] = st.top_coin_removal(val)
    res["top3_total"] = st.top_coin_removal(val, val="nett_R")
    res["loyo"] = st.leave_one_year_out(val)
    res["loyo_total"] = st.leave_one_year_out(val, val="nett_R")
    bd = list(base_days.values())
    bpd = float(np.mean([np.mean([x[0] for x in v]) for v in bd])) if bd else float("nan")
    btd = float(np.mean([np.mean([x[0] - x[1] for x in v]) for v in bd])) if bd else float("nan")
    res["baseline"] = st.baseline_compare(val, bpd, btd)
    res["baseline"]["base_carry_bp_day"] = 1e4 * float(np.mean([np.mean([x[1] for x in v]) for v in bd])) if bd else float("nan")
    res["baseline"]["base_days"] = len(bd)
    flip, mo, ma = st.sign_flip(val, cell)
    res["sign_flip"] = dict(flag=flip, opposite_mean=mo, aligned_mean=ma)
    v, bars = st.verdict(cell, val, dev, bp, bt, res["placebo_window_price"], res["baseline"], ex, res["top3"], res["loyo"], flip)
    res["verdict"], res["bars"] = v, {str(k): bool(x) for k, x in bars.items()}
    res["first_failing_bar"] = next((k for k in sorted(bars) if not bars[k]), None)
    res["rows"] = {}
    for name, rows in (("DEV", dev), ("VAL", val)):
        res["rows"][name] = dict(cycle=st.group_rows(rows, "cycle"), year=st.group_rows(rows, "year"),
                                 label=st.group_rows(rows, "label"))
    res["ex_ended"] = dict(price=st.mean([t["netp_R"] for t in val if not t["ended"]]), total=st.mean([t["nett_R"] for t in val if not t["ended"]]),
                           n=sum(1 for t in val if not t["ended"]), n_ended=sum(1 for t in val if t["ended"]))
    res["ex_lunaftt"] = dict(price=st.mean([t["netp_R"] for t in val if not t["lunaftt"]]), total=st.mean([t["nett_R"] for t in val if not t["lunaftt"]]),
                             n=sum(1 for t in val if not t["lunaftt"]), n_dropped=sum(1 for t in val if t["lunaftt"]))
    oi_rows = [t for t in trades if t["oi7"] == t["oi7"]]
    oi = dict(n=len(oi_rows))
    if len(oi_rows) >= 9:
        q1, q2 = np.percentile([t["oi7"] for t in oi_rows], [100 / 3, 200 / 3])
        for nm, f in (("low", lambda x: x <= q1), ("mid", lambda x: q1 < x <= q2), ("high", lambda x: x > q2)):
            g = [t for t in oi_rows if f(t["oi7"])]
            oi[nm] = dict(n=len(g), price_R=st.mean([t["netp_R"] for t in g]), total_R=st.mean([t["nett_R"] for t in g]))
        oi["cut_low"], oi["cut_high"] = float(q1), float(q2)
    res["oi_terciles"] = oi
    return res


def regime_mix(trades):
    out = {}
    for s in ("DEV", "VAL"):
        rows = [t for t in trades if t["split"] == s]
        n = max(len(rows), 1)
        out[s] = {k: sum(1 for t in rows if t["cycle"] == k) / n for k in ("BULL", "BASE", "BEAR")}
    return out


def main():
    print("priority:", core.set_below_normal())
    with core.Slot("t12-run"):
        coins, funds, data_end, names = core.load_universe()
        by = {c.name: c for c in coins}
        phase = core.load_phase(core.PHASE_CSV)
        alive = core.alive_counts(coins)
        oi = load_oi()
        out = dict(universe=len(coins), cells={})
        all_trades = {}
        mixes = {}
        for cell in ("A", "B"):
            trades, noflag, base_days, skips = build_cell(cell, coins, funds, phase, alive, oi)
            all_trades[cell] = trades
            print("cell", cell, "trades", len(trades), "skips", skips, flush=True)
            # trades list written BEFORE any pooled statistic is printed
            res = evaluate(cell, trades, by, funds, noflag, base_days)
            res["skips"] = skips
            mixes[cell] = regime_mix(trades)
            out["cells"][cell] = res
        # overall
        A, B = out["cells"]["A"], out["cells"]["B"]
        p2 = {"A": A["boot_val_price"]["p_le0"], "B": B["boot_val_price"]["p_le0"]}
        out["holm_two_cells"] = st.holm(p2)
        out["family9_worst_case"] = {k: min(1.0, 9 * v) for k, v in p2.items()}
        p1 = A["bars"].get("1") and B["bars"].get("1")
        k_a = bool(p1 and A["summary"]["VAL"]["netp_R"] <= 0 and B["summary"]["VAL"]["netp_R"] <= 0)
        n_val = A["n_val"] + B["n_val"]
        k_b = bool(p1 and n_val >= 100 and A["placebo_window_price"]["real_mean"] <= A["placebo_window_price"]["p975"]
                   and B["placebo_window_price"]["real_mean"] <= B["placebo_window_price"]["p975"])
        out["kill"] = dict(a_both_val_price_le0=k_a, b_both_placebo_le_p975=k_b, killed=bool(k_a or k_b))
        out["regime_mix"] = mixes
        write_outputs(out, all_trades)


def write_outputs(out, all_trades):
    A, B = out["cells"]["A"], out["cells"]["B"]
    # trades csv (minimal columns), only if < 1 MB
    cols = ["cell", "coin", "split", "sig_date", "entry_date", "exit_reason", "days", "stop_pct", "gross_R", "fee_R", "fund_R",
            "netp_R", "nett_R", "label", "cycle", "ended"]
    p = HERE / "trades.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for cell in ("A", "B"):
            for t in all_trades[cell]:
                w.writerow([cell, t["coin"], t["split"], ymd(t["sig_ms"]), ymd(t["entry_ms"]), t["reason"], t["days"],
                            "%.4f" % t["stop_pct"], "%.4f" % t["gross_R"], "%.4f" % t["fee_R"], "%.4f" % t["fund_R"],
                            "%.4f" % t["netp_R"], "%.4f" % t["nett_R"], t["label"], t["cycle"], int(t["ended"])])
    big = p.stat().st_size > 1_000_000
    out["trades_csv_bytes"] = p.stat().st_size
    if big:
        p.unlink()
    def small(r):
        keep = ["cell", "n_dev", "n_val", "summary", "boot_val_price", "boot_val_total", "boot_dev_price", "boot_dev_total",
                "placebo_window_price", "placebo_window_total", "placebo_global_price", "placebo_global_total", "ex_best",
                "ex_best_total", "top3", "top3_total", "loyo", "loyo_total", "baseline", "sign_flip", "verdict", "bars",
                "first_failing_bar", "rows", "ex_ended", "ex_lunaftt", "oi_terciles", "skips"]
        return {k: r[k] for k in keep}
    js = dict(study="T12", cells={k: small(v) for k, v in out["cells"].items()}, holm_two_cells=out["holm_two_cells"],
              family9_worst_case=out["family9_worst_case"], kill=out["kill"], regime_mix=out["regime_mix"],
              trades_csv_bytes=out["trades_csv_bytes"])
    (HERE / "results.json").write_text(json.dumps(js, indent=1, default=float))
    (HERE / "RESULT.md").write_text(render(out))
    print("wrote RESULT.md, results.json; verdicts A=%s B=%s kill=%s" % (A["verdict"], B["verdict"], out["kill"]["killed"]))


def render(out):
    A, B = out["cells"]["A"], out["cells"]["B"]
    L = []
    kill = out["kill"]["killed"]
    overall = "KILL (dead at the daily level)" if kill else ("partial" if ("PASS" in (A["verdict"], B["verdict"])) else "no pass")
    L.append("**T12 funding extreme reversal: Cell A (long) %s, Cell B (short) %s; overall %s. VAL n %d / %d, price-only net %s R / %s R.**"
             % (A["verdict"], B["verdict"], overall, A["n_val"], B["n_val"], fmt(A["summary"]["VAL"]["netp_R"]), fmt(B["summary"]["VAL"]["netp_R"])))
    L.append("")
    mx = out["regime_mix"]
    L.append("Regime mix: share of trades by BTC smoothed cycle state at the signal day (BULL/BASE/BEAR). " + "; ".join(
        "Cell %s %s %s" % (c, s, "/".join("%d%%" % round(100 * mx[c][s][k]) for k in ("BULL", "BASE", "BEAR"))) for c in "AB" for s in ("DEV", "VAL")) + ".")
    L.append("")
    L.append("Protocol: PRE_REG.md frozen and committed before any outcome. Primary metric mean R per trade (risk unit = stop distance); price-only net = gross - 12 bp fee; total net adds real signed funding. Survivorship direction: longs biased UP, shorts biased DOWN (hindsight list of listed coins).")
    L.append("")
    L.append("## Summary table")
    L.append("")
    L.append("| Cell | Split | n | weeks | gross R | fee R | funding R | price-only net R | total net R | gross % | price-only net % | total net % | carry bp/trade |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c, r in (("A long", A), ("B short", B)):
        for s in ("DEV", "VAL"):
            x = r["summary"][s]
            L.append("| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                c, s, x["n"], x["weeks"], fmt(x["gross_R"]), fmt(x["fee_R"], 4), fmt(x["fund_R"]), fmt(x["netp_R"]), fmt(x["nett_R"]),
                fmt(x["gross_pct"], 2), fmt(x["netp_pct"], 2), fmt(x["nett_pct"], 2), fmt(x["carry_bp"], 1)))
    L.append("")
    L.append("## Bars (price-only net R, VAL unless stated)")
    L.append("")
    L.append("| # | Bar | Cell A | Cell B |")
    L.append("|---|---|---|---|")
    names = {"1": "VAL n>=30 and >=20 weeks", "2": "VAL mean>0 and block-bootstrap CI low>0", "3": "DEV mean>0",
             "4": "placebo (same-window, price-only): real >= p97.5 and excess>0", "5": "ex-best-5 weeks (ex-best-2 if <30 weeks) mean>0",
             "6": "baseline basket per day in position", "7": "top-3 coin removal mean>0", "8": "leave-one-year-out all>0"}
    def pf(r, k):
        b = r["bars"]
        return ("PASS" if b[k] else "FAIL") if k in b else "not evaluated (UNDERPOWERED)"
    for k in "12345678":
        L.append("| %s | %s | %s | %s |" % (k, names[k], pf(A, k), pf(B, k)))
    L.append("| 9 | rows by cycle and year printed; SIGN-FLIP | %s | %s |" % (
        "SIGN-FLIP" if A["sign_flip"]["flag"] else "no flip", "SIGN-FLIP" if B["sign_flip"]["flag"] else "no flip"))
    L.append("")
    L.append("Verdict A: %s (first failing bar: %s). Verdict B: %s (first failing bar: %s)." % (A["verdict"], A["first_failing_bar"], B["verdict"], B["first_failing_bar"]))
    L.append("Bars passed A: %s; failed A: %s. Bars passed B: %s; failed B: %s." % (
        ",".join(k for k in sorted(A["bars"]) if A["bars"][k]) or "none", ",".join(k for k in sorted(A["bars"]) if not A["bars"][k]) or "none",
        ",".join(k for k in sorted(B["bars"]) if B["bars"][k]) or "none", ",".join(k for k in sorted(B["bars"]) if not B["bars"][k]) or "none"))
    L.append("")
    L.append("## Statistics detail")
    L.append("")
    L.append("| Item | Cell A | Cell B |")
    L.append("|---|---|---|")
    def row(label, fa, fb):
        L.append("| %s | %s | %s |" % (label, fa(A), fb(B)))
    for key, nm in (("boot_val_price", "VAL price-only"), ("boot_val_total", "VAL total"), ("boot_dev_price", "DEV price-only"), ("boot_dev_total", "DEV total")):
        f = lambda r, key=key: "mean %s, CI [%s, %s], p(<=0) %s, weeks %d, week sd %s" % (
            fmt(r[key]["mean"]), fmt(r[key]["ci_low"]), fmt(r[key]["ci_high"]), fmt(r[key]["p_le0"], 4), r[key]["weeks"], fmt(r[key]["week_sd"]))
        row("Block bootstrap %s (R)" % nm, f, f)
    for key, nm in (("placebo_window_price", "placebo +/-8 wk price-only"), ("placebo_window_total", "placebo +/-8 wk total"),
                    ("placebo_global_price", "placebo global price-only"), ("placebo_global_total", "placebo global total")):
        f = lambda r, key=key: "n %d (skipped %d), real %s, draws %s, p97.5 %s, excess %s, p %s" % (
            r[key]["n"], r[key]["skipped"], fmt(r[key]["real_mean"]), fmt(r[key]["draw_mean"]), fmt(r[key]["p975"]), fmt(r[key]["excess"]), fmt(r[key]["p"], 4))
        row(nm, f, f)
    row("Ex-best weeks price-only (k, n, mean)", lambda r: "k %d, n %d, %s" % (r["ex_best"]["k"], r["ex_best"]["n"], fmt(r["ex_best"]["mean"])),
        lambda r: "k %d, n %d, %s" % (r["ex_best"]["k"], r["ex_best"]["n"], fmt(r["ex_best"]["mean"])))
    row("Ex-best weeks total", lambda r: fmt(r["ex_best_total"]["mean"]), lambda r: fmt(r["ex_best_total"]["mean"]))
    t3 = lambda r: "; ".join("%s -> %s (n %d)" % ("+".join(x["removed"]), fmt(x["mean"]), x["n"]) for x in r["top3"])
    row("Top-3 coin removal price-only", t3, t3)
    t3t = lambda r: "; ".join("%s -> %s" % ("+".join(x["removed"]), fmt(x["mean"])) for x in r["top3_total"])
    row("Top-3 coin removal total", t3t, t3t)
    ly = lambda r: "; ".join("-%s: %s" % (y, fmt(v["mean"])) for y, v in r["loyo"].items())
    row("Leave-one-year-out price-only", ly, ly)
    bl = lambda r: "trade price %s%%/d vs basket %s%%/d (ok %s); trade total %s%%/d vs basket %s%%/d; carry basket %s bp/d (%d days)" % (
        fmt(100 * r["baseline"]["trade_price_daily"], 3), fmt(100 * r["baseline"]["base_price_daily"], 3), r["baseline"]["ok"],
        fmt(100 * r["baseline"]["trade_total_daily"], 3), fmt(100 * r["baseline"]["base_total_daily"], 3), fmt(r["baseline"]["base_carry_bp_day"], 2), r["baseline"]["base_days"])
    row("Baseline", bl, bl)
    row("Ex-ENDED (VAL, price/total, n)", lambda r: "%s / %s, n %d, ended %d" % (fmt(r["ex_ended"]["price"]), fmt(r["ex_ended"]["total"]), r["ex_ended"]["n"], r["ex_ended"]["n_ended"]),
        lambda r: "%s / %s, n %d, ended %d" % (fmt(r["ex_ended"]["price"]), fmt(r["ex_ended"]["total"]), r["ex_ended"]["n"], r["ex_ended"]["n_ended"]))
    row("Ex-LUNA/FTT (VAL, price/total, n)", lambda r: "%s / %s, n %d, dropped %d" % (fmt(r["ex_lunaftt"]["price"]), fmt(r["ex_lunaftt"]["total"]), r["ex_lunaftt"]["n"], r["ex_lunaftt"]["n_dropped"]),
        lambda r: "%s / %s, n %d, dropped %d" % (fmt(r["ex_lunaftt"]["price"]), fmt(r["ex_lunaftt"]["total"]), r["ex_lunaftt"]["n"], r["ex_lunaftt"]["n_dropped"]))
    row("Exit reasons VAL", lambda r: str(r["summary"]["VAL"]["reasons"]), lambda r: str(r["summary"]["VAL"]["reasons"]))
    row("Median stop % VAL", lambda r: fmt(r["summary"]["VAL"]["stop_pct_median"], 1), lambda r: fmt(r["summary"]["VAL"]["stop_pct_median"], 1))
    row("SIGN-FLIP read (opposite / aligned mean)", lambda r: "%s / %s" % (fmt(r["sign_flip"]["opposite_mean"]), fmt(r["sign_flip"]["aligned_mean"])),
        lambda r: "%s / %s" % (fmt(r["sign_flip"]["opposite_mean"]), fmt(r["sign_flip"]["aligned_mean"])))
    L.append("")
    L.append("Holm over the two cells (bar-2 one-sided p, adjusted): A %s, B %s. Wave-3 family (9 cells) worst case min(1, 9p): A %s, B %s; the coordinator completes the family Holm." % (
        fmt(out["holm_two_cells"]["A"], 4), fmt(out["holm_two_cells"]["B"], 4), fmt(out["family9_worst_case"]["A"], 4), fmt(out["family9_worst_case"]["B"], 4)))
    k = out["kill"]
    L.append("Kill criteria: (a) both VAL price-only <= 0 with bar 1: %s; (b) both placebo <= p97.5 with >= 100 trades: %s; killed: %s." % (
        k["a_both_val_price_le0"], k["b_both_placebo_le_p975"], k["killed"]))
    L.append("")
    for s in ("DEV", "VAL"):
        for cname, r in (("A", A), ("B", B)):
            L.append("## Cell %s %s rows by BTC cycle, year, phase label (n / price-only R / total R)" % (cname, s))
            L.append("")
            L.append("| Group | Key | n | price-only R | total R |")
            L.append("|---|---|---|---|---|")
            for g in ("cycle", "year", "label"):
                for key, v in r["rows"][s][g].items():
                    L.append("| %s | %s | %d | %s | %s |" % (g, key, v["n"], fmt(v["mean_price"]), fmt(v["mean_total"])))
            L.append("")
    L.append("## OI terciles (descriptive, 20 coins with OI, DEV+VAL pooled, 7-day OI change at the signal day; no verdict)")
    L.append("")
    L.append("| Cell | tercile | n | price-only R | total R |")
    L.append("|---|---|---|---|---|")
    for cname, r in (("A", A), ("B", B)):
        o = r["oi_terciles"]
        for t in ("low", "mid", "high"):
            if t in o:
                L.append("| %s | %s | %d | %s | %s |" % (cname, t, o[t]["n"], fmt(o[t]["price_R"]), fmt(o[t]["total_R"])))
        if "low" not in o:
            L.append("| %s | n/a | %d | NOT_IN_DATA (fewer than 9 trades with OI) | |" % (cname, o["n"]))
    L.append("")
    L.append("Skipped signals: A %s, B %s. Trades csv bytes %d (kept in the folder if under 1 MB)." % (A["skips"], B["skips"], out["trades_csv_bytes"]))
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
