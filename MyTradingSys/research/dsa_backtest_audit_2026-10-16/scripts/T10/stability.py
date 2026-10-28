"""T10-F4 stability cuts per study on DEV bars only (2022-01-01..2024-06-30). No new backtest logic.

A trade row is (t_ms, side, net) with side +1 long / -1 short, net in percent (pp for LC1).
Cuts: per UTC year, long/short, and the mean with the 5 best days removed (days ranked by summed net).
Studies read: gross_effect_screen ledger.csv (published DEV trades), levels_hold analyze() touches,
run_rsi_backtest trades_from_events at the chosen params of RERUN_FUNDING.md. Run: python stability.py
"""
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
DAY_MS = 86_400_000
DEV_END_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
BAR_PCT = 0.14  # pass bar, % round trip (PRE_REG gross_effect_screen C_PCT)
TOPN = 5


def _year(t_ms):
    return dt.datetime.fromtimestamp(t_ms / 1000, dt.timezone.utc).year


def _mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def stats(rows):
    """rows: [(t_ms, side, net)] -> n, sum, mean."""
    nets = [r[2] for r in rows]
    return {"n": len(nets), "sum": sum(nets), "mean": _mean(nets)}


def drop_top_days(rows, k=TOPN):
    """Remove every trade on the k days with the largest summed net (ties: earlier day first)."""
    by_day = defaultdict(float)
    for t, _, net in rows:
        by_day[t // DAY_MS] += net
    top = set(d for d, _ in sorted(by_day.items(), key=lambda kv: (-kv[1], kv[0]))[:k])
    return [r for r in rows if r[0] // DAY_MS not in top]


def cuts(rows):
    out = {"all": stats(rows), "top5_removed": stats(drop_top_days(rows)),
           "long": stats([r for r in rows if r[1] > 0]), "short": stats([r for r in rows if r[1] < 0])}
    out["year"] = {y: stats([r for r in rows if _year(r[0]) == y]) for y in sorted({_year(r[0]) for r in rows})}
    out["year_side"] = {(y, s): stats([r for r in rows if _year(r[0]) == y and (r[1] > 0) == (s == "long")])
                        for y in out["year"] for s in ("long", "short")}
    return out


def _sgn(x):
    return 0 if x != x or x == 0 else (1 if x > 0 else -1)


def sign_changes(c):
    """True when the mean after removing the top-5 days has the opposite sign of the full mean."""
    return _sgn(c["all"]["mean"]) != _sgn(c["top5_removed"]["mean"])


# ----------------------------------------------------------------- study readers
def gross_rows(arm="T", path=None):
    """Published ledger.csv, primary cell d=1, h=60: net = G - 0.01 flat funding if the 8h settlement
    lies in [entry, exit] - 0.14 cost (all PRE_REG values). Entry minute = t_open_time + (1+d) min."""
    path = path or REPO / "MyTradingSys/research/gross_effect_screen_2026-10-15/ledger.csv"
    per, rows = 8 * 3600 * 1000, []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            g = float(r["G_d1_h60"]) if r["G_d1_h60"] not in ("", "nan") else float("nan")
            if g != g or (arm == "T" and r["F"] != "1"):
                continue
            te = int(r["t_open_time"]) + 2 * 60_000
            fund = 0.01 if (te + 60 * 60_000) // per > te // per else 0.0
            rows.append((int(r["t_open_time"]), int(r["side"]), g - fund - BAR_PCT))
    return rows


def lc1_rows():
    """LEGACY 8-family set, void since T05-F5: the fair control (levels_hold.md) has KEEP none, 0 of 12. Kept as published.
    levels_hold on standard DEV: per touch of a KEEP family, net = HOLD(1/0) minus the family's pooled
    random-line hold rate, in pp, so the mean equals the study 'difference'. Side = level above/below midnight."""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "MyTradingSys/research/levels_confluence_2026-10-14"))
    from levels import levels_by_day
    from levels_hold import analyze
    from MyTradingSys.backtest.bt.bt_data import load_klines
    s = int(dt.datetime(2022, 3, 21, tzinfo=dt.timezone.utc).timestamp() * 1000)
    d0 = int(dt.datetime(2022, 4, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    bars = load_klines("F:/MTS/data/tom_raw", start_ms=s, end_ms=DEV_END_MS)
    assert bars and max(b["t"] for b in bars) < DEV_END_MS
    dev = [b for b in bars if b["t"] >= d0]
    res = analyze(dev, levels_by_day(bars))
    keep = {"prior_day_high", "prior_day_low", "prior_day_poc", "naked_poc", "4h_fractal_low",
            "4h_fractal_high", "round_1000", "prior_week_high"}
    rate = {k: v["random_hold_rate"] for k, v in res["families"].items()}
    return [(e["day"] * DAY_MS, e["side"], 100.0 * ((e["outcome"] == "HOLD") - rate[e["family"]]))
            for e in res["touches"] if e["family"] in keep]


RSI_ROWS = [  # chosen params, RERUN_FUNDING.md (SOURCED); funding off (raw_fund absent here, effect <= 0.015 pp)
    ("malkan_40_60", "1h", {"period": 21, "tolerance": 2.0, "lookback": 40}),
    ("malkan_40_60", "4h", {"period": 10, "tolerance": 1.0, "lookback": 10}),
    ("malkan_40_60", "1d", {"period": 10, "tolerance": 3.0, "lookback": 20}),
    ("rsi_ma_events", "15m", {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}),
    ("rsi_ma_events", "1h", {"period": 14, "ma_length": 14, "tolerance": 2.0, "mode": "cross"}),
    ("rsi_ma_events", "4h", {"period": 14, "ma_length": 9, "tolerance": 0.5, "mode": "touch"}),
]


def rsi_rows():
    sys.path.insert(0, str(REPO))
    from MyTradingSys.backtest.bt.bt_data import load_klines
    from MyTradingSys.backtest.layers.rsi import run_rsi_backtest as R
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    bars = [b for b in load_klines("F:/MTS/data/tom_raw", end_ms=DEV_END_MS) if b["t"] < DEV_END_MS]
    reg = R.load_registry()
    out = {}
    for fam, tf, p in RSI_ROWS:
        b = resample(bars, tf, reg)
        fn = R.malkan_events if fam == "malkan_40_60" else R.rsi_ma_family_events
        tr = R.trades_from_events(fn(b, p), b, funding=[])
        out["%s %s" % (fam, tf)] = [(t["t"], 1 if t["side"] == "long" else -1, 100.0 * t["net"]) for t in tr]
    return out


# ----------------------------------------------------------------- report
def _f(x):
    return "n/a" if x != x else "%+.4f" % x


def table(name, unit, rows):
    c = cuts(rows)
    L = []
    for kind, key in [("all", None), ("top5_removed", None)]:
        L.append("| %s | all | %s | %d | %s |" % (name, kind, c[kind]["n"], _f(c[kind]["mean"])))
    for y, s in c["year"].items():
        L.append("| %s | %d | year | %d | %s |" % (name, y, s["n"], _f(s["mean"])))
    for (y, side), s in c["year_side"].items():
        L.append("| %s | %d | %s | %d | %s |" % (name, y, side, s["n"], _f(s["mean"])))
    for side in ("long", "short"):
        L.append("| %s | all | %s | %d | %s |" % (name, side, c[side]["n"], _f(c[side]["mean"])))
    return L, c


def main():
    studies = [("gross_effect_screen arm T", "% net of 0.14 cost+funding", gross_rows("T")),
               ("gross_effect_screen arm C", "% net of 0.14 cost+funding", gross_rows("C")),
               ("levels_hold LC1 KEEP (LEGACY 8-family set, void since T05-F5; fair control KEEP none)", "pp hold minus random", lc1_rows())]
    studies += [("rsi " + k, "% net (fees)", v) for k, v in rsi_rows().items()]
    lines = ["| study | year | cut | n | mean |", "|---|---|---|---|---|"]
    flips = []
    for name, unit, rows in studies:
        L, c = table(name, unit, rows)
        lines += L
        if sign_changes(c):
            flips.append("%s (%s -> %s %s)" % (name, _f(c["all"]["mean"]), _f(c["top5_removed"]["mean"]), unit))
    print("\n".join(lines))
    print("\nSIGN CHANGE WHEN TOP 5 DAYS GO: " + ("; ".join(flips) if flips else "none"))


if __name__ == "__main__":
    main()
