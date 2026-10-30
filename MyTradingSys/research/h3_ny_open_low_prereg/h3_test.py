"""H3 test, frozen by PRE_REG.md in this folder. Run once. Reuses Bars/load logic of session_open_study.py."""
import datetime as dt
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.fabio.v3 import day_gates as G  # noqa: E402
from MyTradingSys.backtest import fees as F  # noqa: E402
import MyTradingSys.research.session_sweeps.session_open_study as S  # noqa: E402

MIN, DAY = 60000, 86400000
DUMPS = Path(sys.argv[1])  # directory holding Dumps/backtest
PERIODS = {
    "test_2019-09_2021-12": ([DUMPS / "raw_1m_2019/klines"], dt.date(2019, 9, 1), dt.date(2021, 12, 31), False),
    "main_2022-01_2026-09": ([DUMPS / "raw_1m_2022/klines", DUMPS / "raw/klines"], dt.date(2022, 1, 3), dt.date(2026, 9, 25), True),
}
TAKER_RT = 2 * F.BINANCE_TAKER
MAKER_RT = 2 * F.BINANCE_MAKER


def load(dirs):
    S.DIRS = dirs
    T, R = S.load()
    return S.Bars(T, R)


def events(b, d0, d1, use_nyse):
    out, d, dropped = [], d0, 0
    while d <= d1:
        op = G.ny_open_utc(d)
        if op is not None and not (use_nyse and d in S.NYSE_EXTRA):
            A = S.ms(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc))
            O = S.ms(op)
            if b.missing(A, O + 390 * MIN) > 5 or b.missing(A - DAY, A) > 10:
                dropped += 1
            else:
                P0 = O + 180 * MIN
                lo_w, hi_w = b.lo(P0, P0 + 30 * MIN), b.hi(P0, P0 + 30 * MIN)
                ref_lo, ref_hi = b.lo(A, P0), b.hi(A, P0)
                c30, cE = b.close_at(P0 + 30 * MIN), b.close_at(P0 + 390 * MIN)
                if None not in (lo_w, hi_w, ref_lo, ref_hi, c30, cE) and lo_w < ref_lo and hi_w <= ref_hi and c30 < ref_lo:
                    out.append((d, cE / c30 - 1))
        d += dt.timedelta(days=1)
    return out, dropped


def binom_p_ge(k, n):
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def summarize(ev):
    n = len(ev)
    if n == 0:
        return {"n": 0}
    g = [r for _, r in ev]
    net = [r - TAKER_RT for r in g]
    k = sum(1 for r in g if r > 0)
    p, lo, hi = S.wilson(k, n)
    rnd = random.Random(1)
    boots = sorted(statistics.fmean(rnd.choices(net, k=n)) for _ in range(10000))
    o = {"n": n, "hits": k, "hit": p, "hit_ci": [lo, hi], "p_binom_ge": round(binom_p_ge(k, n), 5),
         "mean_gross_bp": round(statistics.fmean(g) * 1e4, 1), "mean_net_taker_bp": round(statistics.fmean(net) * 1e4, 1),
         "median_net_taker_bp": round(statistics.median(net) * 1e4, 1),
         "boot95_net_taker_bp": [round(boots[250] * 1e4, 1), round(boots[9749] * 1e4, 1)],
         "mean_net_maker_bp": round((statistics.fmean(g) - MAKER_RT) * 1e4, 1), "by_year": {}}
    for y in sorted({d.year for d, _ in ev}):
        yy = [r for d, r in ev if d.year == y]
        o["by_year"][str(y)] = {"n": len(yy), "hit": round(sum(1 for r in yy if r > 0) / len(yy), 3),
                                "mean_net_taker_bp": round((statistics.fmean(yy) - TAKER_RT) * 1e4, 1)}
    return o


def main():
    res = {}
    for name, (dirs, d0, d1, nyse) in PERIODS.items():
        b = load(dirs)
        ev, dropped = events(b, d0, d1, nyse)
        res[name] = summarize(ev)
        res[name]["dropped_days"] = dropped
        res[name]["bars_first_last"] = [dt.datetime.utcfromtimestamp(b.T[0] / 1000).isoformat(), dt.datetime.utcfromtimestamp(b.T[-1] / 1000).isoformat()]
        print(name, json.dumps(res[name]))
    t = res["test_2019-09_2021-12"]
    c = {}
    c["1_n>=30"] = t["n"] >= 30
    c["2_hit>=60_and_p<0.05"] = t["hit"] >= 0.60 and t["p_binom_ge"] < 0.05
    c["3_net>0_and_boot_lo>0"] = t["mean_net_taker_bp"] > 0 and t["boot95_net_taker_bp"][0] > 0
    bad = sum(1 for v in t["by_year"].values() if v["hit"] < 0.5)
    c["4_at_most_1_bad_year"] = bad <= 1
    res["criteria"] = c
    res["verdict"] = "PASS" if all(c.values()) else "FAIL"
    print(c, res["verdict"])
    Path(__file__).with_name("results.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
