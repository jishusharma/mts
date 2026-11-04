"""Regime mix over the long window (spot BTCUSDT daily from 2017-08). Context comes only from research_kit (regime_tag, regime_mix_line).
Weeks are Monday 00:00 UTC; the tag is as-of (no look-ahead). Weeks without enough history (SMA200, weekly/monthly RSI14) count as n/a.
Usage: python regime_mix_long.py [--root F:/MTS/Dumps/backtest/spot_2017] [--from 2018-01-01]"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest.bt.bt_data import load_klines  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample  # noqa: E402

DAY = 86400000


def rsi_series(bars):
    r = rsi_core([x["c"] for x in bars], 14)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]
    return [bars[k + 1]["t"] for k in keep], [r[k] for k in keep]


def ms(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="F:/MTS/Dumps/backtest/spot_2017")
    ap.add_argument("--from", dest="lo", default="2017-08-21")
    ap.add_argument("--to", default="2026-10-26")
    a = ap.parse_args()
    d = load_klines(Path(a.root) / "BTCUSDT" / "1d")
    reg = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    wk, mo = rsi_series(resample(d, "1w", reg)), rsi_series(resample(d, "1M", reg))
    lo, hi = ms(a.lo), ms(a.to)
    d0 = lo // DAY
    d0 += (4 - d0) % 7
    starts = [k * DAY for k in range(d0, hi // DAY, 7)]
    tags = rk.weekly_regimes(starts, daily, wk, mo)
    print(f"daily bars {len(d)}: {d[0]['t'] // DAY} .. {d[-1]['t'] // DAY} (epoch days); weeks {a.lo}..{a.to}")
    print("Regime mix: " + rk.regime_mix_line(tags))
    print(f"bear weeks: {tags.count('bear')}")
    first = next((s for s, t in zip(starts, tags) if t is not None), None)
    if first is not None:
        known = [t for t in tags if t is not None]
        print(f"first tagged week {datetime.fromtimestamp(first / 1000, timezone.utc):%Y-%m-%d}; tagged-only mix: " + rk.regime_mix_line(known))
    by_year = {}
    for s, t in zip(starts, tags):
        y = datetime.fromtimestamp(s / 1000, timezone.utc).year
        by_year.setdefault(y, {}).setdefault(t or "n/a", 0)
        by_year[y][t or "n/a"] += 1
    for y in sorted(by_year):
        print(y, by_year[y])


if __name__ == "__main__":
    main()
