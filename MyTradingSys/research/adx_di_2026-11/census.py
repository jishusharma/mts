"""
MyTradingSys/research/adx_di_2026-11/census.py - ADX/DI 2d cross census (card adx-di-2d-cross-census-1107, SPEC.md).
Context layer: no orders, no edge claim. Every threshold is OURS. Writes CENSUS.md next to this file.
  python census.py            (reads research/btc_cycles_2026-11/btc_daily.csv)
"""
import csv
import datetime
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "backtest", "layers", "adx"))
sys.path.insert(0, os.path.join(ROOT, "backtest", "layers", "timeframe"))
from adx import adx_di, crosses  # noqa: E402
from tf_resample import resample  # noqa: E402

DAILY = os.path.join(ROOT, "research", "btc_cycles_2026-11", "btc_daily.csv")
REGISTRY = os.path.join(ROOT, "backtest", "layers", "timeframe", "registry.json")
DAY_MS = 86400000
FWD = 30          # 2d bars searched for the swing extreme (OURS)
SLOPE = 5         # ADX slope lookback in bars (OURS)
SPLITS = [("DEV 2020-01-01..2024-06-30", "2020-01-01", "2024-06-30"),
          ("VALIDATION 2024-07-01..2025-06-30", "2024-07-01", "2025-06-30"),
          ("RECENT 2025-07-01..2026-11-07 (descriptive; holds CCU's Oct-2025 / Jan-2026 / May-2026 cases)",
           "2025-07-01", "2026-11-07")]
WARMUP_START = "2017-01-01"


def load_daily(path=DAILY, start=WARMUP_START):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["date"] < start:
                continue
            d = datetime.datetime.strptime(r["date"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
            out.append({"t": int(d.timestamp() * 1000), "date": r["date"], "h": float(r["high"]),
                        "l": float(r["low"]), "c": float(r["close"])})
    return out


def to_2d(daily, registry):
    """2d bars through tf_resample bucket '2d'; each daily bar is stamped at its last minute so the last closed bucket is kept."""
    bars = [{"t": b["t"] + DAY_MS - 60000, "o": b["c"], "h": b["h"], "l": b["l"], "c": b["c"]} for b in daily]
    return resample(bars, "2d", registry)


def date_of(t_ms):
    return datetime.datetime.fromtimestamp(t_ms / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d")


def cross_rows(bars, n=14, fwd=FWD, slope=SLOPE):
    """One row per DI cross on bars (dicts t,h,l,c; 2d). Cross bar = the closed bar where the DI order flips."""
    H = [b["h"] for b in bars]
    L = [b["l"] for b in bars]
    C = [b["c"] for b in bars]
    dip, dim, adx = adx_di(H, L, C, n)
    cr = crosses(dip, dim)
    dirs = {i: d for i, d in cr}
    rows = []
    for i, d in cr:
        a = adx[i]
        sl = (a - adx[i - slope]) if (a is not None and i - slope >= 0 and adx[i - slope] is not None) else None
        win = bars[i + 1:i + 1 + fwd]
        row = {"date": date_of(bars[i]["t"]), "i": i, "dir": d, "adx": a, "slope": sl, "close": C[i],
               "nfwd": len(win), "bars_to": None, "depth": None}
        if len(win) == fwd:
            if d == "red":
                j = min(range(fwd), key=lambda k: win[k]["l"])
                row["depth"] = win[j]["l"] / C[i] - 1
            else:
                j = max(range(fwd), key=lambda k: win[k]["h"])
                row["depth"] = win[j]["h"] / C[i] - 1
            row["bars_to"] = j + 1
        for k in (1, 2, 3):
            hit = any(dirs.get(i + q) not in (None, d) for q in range(1, k + 1))
            row["ws%d" % k] = True if hit else (None if len(bars) - 1 - i < k else False)
        rows.append(row)
    return rows


def bucket(a):
    if a is None:
        return None
    return "<20" if a < 20 else ("20-40" if a <= 40 else ">40")


def cell(rows, absdepth=False):
    n = len(rows)
    ws = [r["ws3"] for r in rows if r["ws3"] is not None]
    dp = [abs(r["depth"]) if absdepth else r["depth"] for r in rows if r["depth"] is not None]
    bt = [r["bars_to"] for r in rows if r["bars_to"] is not None]
    return {"n": n, "n_ws": len(ws), "ws": (sum(ws) / len(ws)) if ws else None,
            "n_dp": len(dp), "depth": statistics.median(dp) if dp else None,
            "bars": statistics.median(bt) if bt else None}


def fmt(v, pct=False, d=1):
    if v is None:
        return "-"
    return ("%.*f%%" % (d, v * 100)) if pct else ("%.*f" % (d, v))


def in_split(r, lo, hi):
    return lo <= r["date"] <= hi


def cascade(rows2d, bars2d, rows1d, bars1d):
    """For each 2d cross: lead in days of the first same-direction 1d cross whose close lies in the previous 10 2d bars (20 days).
    Plus the share of 1d crosses followed by a same-direction 2d cross (close time) within 5 2d bars (10 days)."""
    c1 = [(bars1d[r["i"]]["t"] + DAY_MS, r["dir"]) for r in rows1d]
    c2 = [(bars2d[r["i"]]["t"] + 2 * DAY_MS, r["dir"], r) for r in rows2d]
    leads = []
    for tc, d, r in c2:
        cand = [tc - t1 for t1, d1 in c1 if d1 == d and 0 <= tc - t1 <= 20 * DAY_MS]
        leads.append((r, (max(cand) // DAY_MS) if cand else None))
    fol = [(t1, d1, any(d2 == d1 and 0 <= t2 - t1 <= 10 * DAY_MS for t2, d2, _ in c2)) for t1, d1 in c1]
    return leads, fol


def render(daily, bars2d, rows, rows1d, bars1d):
    L = ["# ADX/DI 2d cross census", "",
         "Card adx-di-2d-cross-census-1107; SPEC.md; formulas FORMULAS.md section 30. Context layer, no orders, no edge claim; every "
         "threshold is OURS (CCU, Steve 2026-11-05, names none). Data: btc_daily.csv (%s..%s, %d daily bars -> %d closed 2d bars), "
         "n = 14, indicator warm-up from %s, crosses reported from 2020-01-01. Swing extreme = lowest low (red) / highest high (green) "
         "in the %d 2d bars after the cross; depth = extreme / close at the cross - 1; rows with fewer than %d bars after are '-' "
         "and not counted in the depth/bars columns (n_dp). Whipsaw = opposite cross within k bars; cells need k bars after (n_ws)."
         % (daily[0]["date"], daily[-1]["date"], len(daily), len(bars2d), WARMUP_START, FWD, FWD),
         "", "**1h / 4h not run:** no 1h/4h BTC kline file covering 2020-2026 is on this machine (F:/MTS/data holds aggTrades and "
         "short orderflow files only), so table (c) is 1d-vs-2d only (DECISION OURS).", ""]
    L.append("## (b) bucket x slope (per split)")
    for name, lo, hi in SPLITS:
        sub = [r for r in rows if in_split(r, lo, hi) and r["adx"] is not None]
        L += ["", "### %s: %d crosses (red %d, green %d)" % (name, len(sub), sum(r["dir"] == "red" for r in sub),
                                                               sum(r["dir"] == "green" for r in sub)), "",
              "| dir | ADX | slope | n | n_ws | whipsaw<=3 | n_dp | median depth (dir all = absolute) | median bars to extreme |", "|---|---|---|---|---|---|---|---|---|"]
        for dr in ("all", "red", "green"):
            for bk in ("<20", "20-40", ">40"):
                for sg in ("falling", "rising"):
                    cs = [r for r in sub if (dr == "all" or r["dir"] == dr) and bucket(r["adx"]) == bk and r["slope"] is not None
                          and (r["slope"] < 0) == (sg == "falling")]
                    c = cell(cs, dr == "all")
                    L.append("| %s | %s | %s | %d | %d | %s | %d | %s | %s |" % (dr, bk, sg, c["n"], c["n_ws"], fmt(c["ws"], True),
                                                                                  c["n_dp"], fmt(c["depth"], True), fmt(c["bars"])))
        c = cell(sub, True)
        L.append("| all | all | all | %d | %d | %s | %d | %s | %s |" % (c["n"], c["n_ws"], fmt(c["ws"], True), c["n_dp"],
                                                                      fmt(c["depth"], True), fmt(c["bars"])))
    red = [r for r in rows if r["dir"] == "red" and r["depth"] is not None and "2020-01-01" <= r["date"] <= "2025-06-30"]
    L += ["", "## CCU check: red crosses, 2020-01-01..2025-06-30 (DEV+VALIDATION, full %d-bar window), n = %d" % (FWD, len(red)), "",
          "| bars to the low (2d bars) | n | share | median depth |", "|---|---|---|---|"]
    for lo, hi in ((1, 3), (4, 7), (8, 12), (13, 20), (21, 30)):
        s = [r for r in red if lo <= r["bars_to"] <= hi]
        L.append("| %d-%d | %d | %s | %s |" % (lo, hi, len(s), fmt(len(s) / len(red) if red else None, True),
                                              fmt(statistics.median([r["depth"] for r in s]) if s else None, True)))
    L += ["", "(CCU: 1-3 weeks of consolidation = 7-10 bars of 2d, then a straight fall. The table counts where the low actually sits "
          "after EVERY red cross, not his three cases.)", ""]
    L += ["## (a) every 2d cross", "", "| date | dir | ADX | slope5 | bars to extreme | depth | nfwd | whip1 | whip2 | whip3 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["date"] < "2020-01-01":
            continue
        w = lambda v: "-" if v is None else ("yes" if v else "no")  # noqa: E731
        L.append("| %s | %s | %s | %s | %s | %s | %d | %s | %s | %s |" % (r["date"], r["dir"], fmt(r["adx"]), fmt(r["slope"]),
                                                                          r["bars_to"] if r["bars_to"] else "-", fmt(r["depth"], True),
                                                                          r["nfwd"], w(r["ws1"]), w(r["ws2"]), w(r["ws3"])))
    L += ["", "n = %d crosses from 2020-01-01." % sum(r["date"] >= "2020-01-01" for r in rows), ""]
    leads, fol = cascade(rows, bars2d, rows1d, bars1d)
    leads = [(r, l) for r, l in leads if r["date"] >= "2020-01-01"]
    L += ["## (c) cascade 1d -> 2d (1h and 4h not run, see top)", "",
          "| split | 2d crosses | with a same-direction 1d cross in the previous 20 days | share | median lead (days) |", "|---|---|---|---|---|"]
    for name, lo, hi in SPLITS:
        s = [(r, l) for r, l in leads if in_split(r, lo, hi)]
        h = [l for _, l in s if l is not None]
        L.append("| %s | %d | %d | %s | %s |" % (name.split(" ")[0], len(s), len(h), fmt(len(h) / len(s) if s else None, True),
                                                 fmt(statistics.median(h) if h else None)))
    L += ["", "Lead per 2d cross (days from the first same-direction 1d cross close to the 2d cross close; 'none' = no 1d cross in the previous 20 days):", "",
          "| date | dir | lead days |", "|---|---|---|"]
    for r, l in leads:
        L.append("| %s | %s | %s |" % (r["date"], r["dir"], "none" if l is None else l))
    fl = [(t, d, f) for t, d, f in fol if date_of(t) >= "2020-01-01"]
    L += ["", "1d crosses followed by a same-direction 2d cross within 5 2d bars (10 days): %d of %d (%s); red %d of %d; green %d of %d."
          % (sum(f for *_, f in fl), len(fl), fmt(sum(f for *_, f in fl) / len(fl) if fl else None, True),
             sum(f for _, d, f in fl if d == "red"), sum(d == "red" for _, d, _ in fl),
             sum(f for _, d, f in fl if d == "green"), sum(d == "green" for _, d, _ in fl)), ""]
    L.append("n is printed in every table; no conclusion is drawn here (operator reads this file).")
    return "\n".join(L) + "\n"


def main():
    with open(REGISTRY) as f:
        registry = json.load(f)
    daily = load_daily()
    bars2d = to_2d(daily, registry)
    rows = cross_rows(bars2d)
    # 1d crosses: same engine on the daily bars, window 30 bars is irrelevant here
    rows1d = cross_rows(daily)
    out = render(daily, bars2d, rows, rows1d, daily)
    with open(os.path.join(HERE, "CENSUS.md"), "w", newline="\n") as f:
        f.write(out)
    print("2d bars", len(bars2d), "2d crosses", len(rows), "1d crosses", len(rows1d))


if __name__ == "__main__":
    main()