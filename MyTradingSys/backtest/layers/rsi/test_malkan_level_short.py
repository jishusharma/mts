"""malkan-level-short-4h-count-1109: the 5 operator-marked shorts (research/malkan_level_shorts_2026-11-09/READING.md)
against the mechanical 5-layer stack. Hand-picked points: the test pins which fire, so a rule change that loses one is seen."""
import csv
import datetime as dt
from pathlib import Path

from MyTradingSys.backtest.layers.rsi import malkan_level_short as M

FX = Path(__file__).parent / "fixtures"


def load(iv):
    with open(FX / f"malkan_btc_{iv}_2026.csv", newline="") as f:
        r = csv.DictReader(f)
        return [{"t": int(x["t"]), "o": float(x["o"]), "h": float(x["h"]), "l": float(x["l"]), "c": float(x["c"])} for x in r]


def ms(s):
    return int(dt.datetime.strptime("2026-" + s, "%Y-%m-%d %H").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


# operator trigger bars (READING.md); a signal within 3 bars (12 h) counts as the same read
POINTS = {"C1": ms("08-28 04"), "C2": ms("09-04 12"), "V1": ms("09-23 00"), "V2": ms("10-06 12"), "C3": ms("10-22 00")}


def near(sigs, t, tol=3 * 4 * 3600 * 1000):
    return any(abs(s["t_trigger"] - t) <= tol for s in sigs)


def test_indicators_match_reading_md():
    b = load("4h")
    ind = M.indicators(b)
    i = next(k for k, x in enumerate(b) if x["t"] == ms("09-23 00"))
    assert abs(ind["rsi"][i] - 76.2) < 0.6 and abs(ind["rsi_ma"][i] - 76.7) < 0.6


def test_operator_points_fire():
    b4, b1d, b1w = load("4h"), load("1d"), load("1w")
    base = M.signals(b4, b1d, b1w, layers=M.BASE)            # level + trigger
    assert all(near(base, t) for t in POINTS.values()), {k: near(base, t) for k, t in POINTS.items()}
    full = M.signals(b4, b1d, b1w, layers=M.FULL)
    hit = {k: near(full, t) for k, t in POINTS.items()}
    assert hit == M.OPERATOR_POINTS_FULL_STACK, hit         # misses are named in REPORT.md


def test_trade_outcome_is_fee_net_in_r():
    bars = [{"t": i, "o": 100, "h": 100.5, "l": 99.5, "c": 100} for i in range(5)]
    bars += [{"t": 5, "o": 100, "h": 100.2, "l": 97.0, "c": 97.5}]
    r = M.outcome(bars, 4, entry=100.0, stop=101.0, target_r=2.0, fee=0.0004, max_bars=10)
    assert r["hit_1r"] and abs(r["net_r"] - (2.0 - 2 * 0.0004 * 100 / 1.0)) < 1e-9
