"""US open first-3-minutes rederive: CONT / FADE of the first 3 minutes, 10 symbols, fee-net, DEV 2021-23 vs VALIDATION 2024+.
Rules frozen in PRE_REG.md. python study.py [--cache DIR]. Writes results.json and RESULT.md next to this file."""
import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # MyTradingSys parent for `backtest`
from backtest import research_kit as RK  # noqa: E402

NY = ZoneInfo("America/New_York")
MIN = 60_000
WINDOW = 60                       # bars T0..T0+59 must all exist
SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "LINK", "LTC"]
ENTRY_OFFSET = 3                  # entry = open of bar T0+3 (0 would be a look-ahead: the open of the first bar)
HORIZON_BAR = {27: 29, 57: 59}    # exit = close of bar T0+k
COST_BP = RK.TAKER_RT_PCT * 100   # 0.14 % -> 14 bp
DEV_START, VAL_START = date(2021, 1, 1), date(2024, 1, 1)
BIG_Q = 0.75
ROWS = [(s, h, f) for s in ("CONT", "FADE") for h in (27, 57) for f in ("all", "big")]


def open_ms(d):
    return int(datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(timezone.utc).timestamp() * 1000)


def load(sym, cache):
    z = np.load(Path(cache) / f"{sym}USDT_1m.npz")
    t = z["t_ms"].astype(np.int64)
    return t, z["o"], z["c"]


def events_for(t, o, c, days, entry_offset=ENTRY_OFFSET):
    """List of dict(day, m3, r27, r57 as exit/entry-1). Skips days without 60 consecutive bars from T0."""
    out, skipped = [], 0
    for d in days:
        t0 = open_ms(d)
        i = int(np.searchsorted(t, t0))
        fwd_t = t[i:i + WINDOW]
        if len(fwd_t) < WINDOW or fwd_t[0] != t0 or fwd_t[-1] != t0 + (WINDOW - 1) * MIN:
            skipped += 1
            continue
        fwd_o, fwd_c = o[i:i + WINDOW], c[i:i + WINDOW]
        m3 = fwd_c[2] / fwd_o[0] - 1
        if m3 == 0:
            continue
        e = fwd_o[entry_offset]
        out.append(dict(day=d, m3=float(m3), r27=float(fwd_c[HORIZON_BAR[27]] / e - 1), r57=float(fwd_c[HORIZON_BAR[57]] / e - 1)))
    return out, skipped


def weekdays(a, b):
    d = a
    while d <= b:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def btc_regime(t, c, days):
    """{day: 'bull'|'bear'|None}: last completed UTC daily close (day before the event date) vs SMA200 of completed daily closes."""
    ud = t // 86_400_000
    last = np.r_[np.nonzero(np.diff(ud))[0], len(ud) - 1]
    dayn, close = ud[last], c[last]
    idx = {int(k): j for j, k in enumerate(dayn)}
    out = {}
    for d in days:
        n = (datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() // 86400) - 1
        j = idx.get(int(n))
        out[d] = None if j is None or j < 199 else ("bull" if close[j] > close[j - 199:j + 1].mean() else "bear")
    return out


def net_bp(side, ret):
    return side * ret * 10000 - COST_BP


def pct(xs, q):
    return sorted(xs)[int(q * (len(xs) - 1))]


def one_row(evs, side_name, h, filt, cuts):
    """evs: {sym: [events]}; returns per-trade arrays for DEV and VAL."""
    res = {}
    for part in ("DEV", "VAL"):
        net, gross, day, sym, reg = [], [], [], [], []
        for s, lst in evs.items():
            for e in lst:
                inpart = e["day"] >= VAL_START if part == "VAL" else e["day"] < VAL_START
                if not inpart or (filt == "big" and abs(e["m3"]) < cuts[s]):
                    continue
                sg = (1 if e["m3"] > 0 else -1) * (1 if side_name == "CONT" else -1)
                r = e["r%d" % h]
                gross.append(sg * r * 10000)
                net.append(net_bp(sg, r))
                day.append(e["day"].toordinal())
                sym.append(s)
                reg.append(e["reg"])
        res[part] = dict(net=np.array(net), gross=np.array(gross), day=np.array(day), sym=np.array(sym), reg=np.array(reg))
    return res


def summarize_row(d):
    net, day = d["net"], d["day"]
    n = len(net)
    if n == 0:
        return dict(n=0)
    m, se = RK.cluster_mean_se(net, day)
    out = dict(n=n, net_mean=float(m), gross_mean=float(d["gross"].mean()), win=float((net > 0).mean()), se=float(se),
               lo95=float(m - 1.96 * se) if se == se else None, t=RK.t_stat(m, se))
    out["sym_pos"] = int(sum(1 for s in SYMBOLS if (d["sym"] == s).any() and net[d["sym"] == s].mean() > 0))
    byday = {}
    for x, dd in zip(net, day):
        byday[dd] = byday.get(dd, 0.0) + x
    drop = set(sorted(byday, key=lambda k: -byday[k])[:5])
    keep = np.array([dd not in drop for dd in day])
    out["net_mean_drop5"] = float(net[keep].mean()) if keep.any() else None
    out["by_regime"] = {r: dict(n=int((d["reg"] == r).sum()), net_mean=float(net[d["reg"] == r].mean()))
                        for r in ("bull", "bear") if (d["reg"] == r).any()}
    return out


def run(cache):
    days = list(weekdays(DEV_START, date.today()))
    evs, skipped, reg = {}, {}, None
    for s in SYMBOLS:
        t, o, c = load(s, cache)
        last_day = datetime.fromtimestamp(t[-1] / 1000, timezone.utc).date()
        dd = [d for d in days if d < last_day]
        evs[s], skipped[s] = events_for(t, o, c, dd)
        if s == "BTC":
            reg = btc_regime(t, c, dd)
    for s in SYMBOLS:
        for e in evs[s]:
            e["reg"] = reg.get(e["day"]) or "na"
    cuts = {s: pct([abs(e["m3"]) for e in evs[s] if e["day"] < VAL_START], BIG_Q) for s in SYMBOLS}
    rows = []
    for side, h, f in ROWS:
        r = one_row(evs, side, h, f, cuts)
        rows.append(dict(side=side, h=h, filt=f, DEV=summarize_row(r["DEV"]), VAL=summarize_row(r["VAL"])))
    p = []
    for r in rows:
        v = r["VAL"]
        t = v.get("t")
        p.append(1.0 if (not v.get("n") or t is None or t != t or v["net_mean"] <= 0) else 0.5 * RK.norm_p_two(t))
    adj = RK.holm(p)
    for r, pa, pr in zip(rows, adj, p):
        v = r["VAL"]
        v["p_one"], v["p_holm"] = pr, float(pa)
        if not v.get("n") or v["n"] < 100:
            r["verdict"] = "UNDERPOWERED"
        else:
            ok = (v["lo95"] is not None and v["lo95"] > 0 and pa < 0.05 and v["sym_pos"] >= 6
                  and v["net_mean_drop5"] is not None and v["net_mean_drop5"] > 0)
            r["verdict"] = "PASS" if ok else "FAIL"
    mix = {}
    for part, sel in (("DEV", lambda e: e["day"] < VAL_START), ("VAL", lambda e: e["day"] >= VAL_START)):
        xs = [e["reg"] for s in SYMBOLS for e in evs[s] if sel(e)]
        mix[part] = {k: xs.count(k) / len(xs) for k in ("bull", "bear", "na")}
    return dict(rows=rows, cuts=cuts, skipped=skipped, n_events={s: len(evs[s]) for s in SYMBOLS}, regime_mix=mix, cost_bp=COST_BP,
                overall="EDGE" if any(r["verdict"] == "PASS" for r in rows) else "NO EDGE",
                last_day=str(max(e["day"] for s in SYMBOLS for e in evs[s])))


def result_md(t):
    L = ["# US open first 3 minutes, CONT / FADE, 10 symbols, fee-net (rederive 2026-11-15)", "",
         "Verdict: **%s**. Cost %.0f bp round trip (research_kit.TAKER_RT_PCT). VALIDATION = 2024-01-01 .. %s, DEV = 2021-2023 (descriptive). Rules: PRE_REG.md."
         % (t["overall"], t["cost_bp"], t["last_day"]), "",
         "Regime mix: VAL events bull %.0f%% / bear %.0f%% / na %.0f%%; DEV bull %.0f%% / bear %.0f%% / na %.0f%% (BTC close vs SMA200, split reported not gated)."
         % tuple(100 * t["regime_mix"][p][k] for p in ("VAL", "DEV") for k in ("bull", "bear", "na")), "",
         "n events per symbol: " + ", ".join("%s %d" % kv for kv in t["n_events"].items()) + "; skipped (gaps): "
         + ", ".join("%s %d" % kv for kv in t["skipped"].items()), "",
         "| side | min | filter | n DEV | DEV net bp | n VAL | gross bp | net bp | lo95 | win | syms+ | drop5 | Holm p | bull / bear net | verdict |",
         "|" + "---|" * 15]
    g = lambda x: "%.2f" % x if x is not None else "-"  # noqa: E731
    for r in t["rows"]:
        d, v = r["DEV"], r["VAL"]
        br = " / ".join("%s n%d %.1f" % (k, x["n"], x["net_mean"]) for k, x in v.get("by_regime", {}).items())
        L.append("| %s | %d | %s | %d | %s | %d | %s | %s | %s | %.1f%% | %d | %s | %.3f | %s | %s |" % (
            r["side"], r["h"], r["filt"], d.get("n", 0), g(d.get("net_mean")), v["n"], g(v.get("gross_mean")), g(v.get("net_mean")),
            g(v.get("lo95")), 100 * v.get("win", 0), v.get("sym_pos", 0), g(v.get("net_mean_drop5")), v.get("p_holm", 1), br, r["verdict"]))
    L += ["", "Big cut (|m3| DEV p75, frozen): " + ", ".join("%s %.3f%%" % (s, 100 * x) for s, x in t["cuts"].items()), ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=r"F:\MTS\data_cache\binance_1m")
    a = ap.parse_args(argv)
    t = run(a.cache)
    (HERE / "results.json").write_text(json.dumps(t, indent=1, sort_keys=True, default=float) + "\n", encoding="utf-8", newline="\n")
    (HERE / "RESULT.md").write_text(result_md(t), encoding="utf-8", newline="\n")
    print(result_md(t))


if __name__ == "__main__":
    main()
