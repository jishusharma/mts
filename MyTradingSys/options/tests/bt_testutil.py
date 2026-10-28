"""Shared helpers for the options backtest tests: sys.path wiring, synthetic data writers, INDEPENDENT reference maths.

Nothing here imports the backtest modules' logic: expected numbers come from BT_SPEC.md formulas (erf-based normal CDF,
Black-76 with r=0, inverse-option payoffs) or are hand-computed constants in the tests.
OPT_BT_DIR can point the tests at a modified copy of options/backtest (used for the broken-variant checks).
"""
import calendar
import csv
import gzip
import itertools
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BT_DIR = Path(os.environ.get("OPT_BT_DIR") or (HERE.parent / "backtest"))
sys.path.insert(0, str(BT_DIR))

HOUR = 3600000
DAY = 86400000
YEAR_MS = 365 * DAY


def ms(y, mo, d, h=0, mi=0, s=0):
    """UTC epoch ms (calendar.timegm: independent of the implementation and of the local timezone)."""
    return calendar.timegm((y, mo, d, h, mi, s)) * 1000


# -- reference maths (BT_SPEC "Conventions") ------------------------------------------------------------------------
def ref_N(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def ref_b76_usd(F, K, iv_pct, T, is_call):
    s = iv_pct / 100.0
    sd = s * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * s * s * T) / sd
    d2 = d1 - sd
    if is_call:
        return F * ref_N(d1) - K * ref_N(d2)
    return K * ref_N(-d2) - F * ref_N(-d1)


def ref_b76_btc(F, K, iv_pct, T, is_call):
    return ref_b76_usd(F, K, iv_pct, T, is_call) / F


def ref_abs_delta(F, K, iv_pct, T, is_call):
    s = iv_pct / 100.0
    d1 = (math.log(F / K) + 0.5 * s * s * T) / (s * math.sqrt(T))
    return ref_N(d1) if is_call else 1.0 - ref_N(d1)


def ref_payoff_btc(S, K, is_call):
    return (max(0.0, S - K) if is_call else max(0.0, K - S)) / S


# -- synthetic trades / shards ------------------------------------------------------------------------------------
_ids = itertools.count(1000)


def tr(ts, name, direction, price, amount=1.0, iv=50.0, index=80000.0, mark=None, **extra):
    """One trade as the collector stores it (direction = TAKER side). `extra` carries block_trade_id/combo_id/liquidation."""
    d = {"timestamp": ts, "trade_id": str(next(_ids)), "trade_seq": 1, "tick_direction": 0, "instrument_name": name,
         "price": price, "amount": amount, "contracts": amount, "direction": direction, "iv": iv, "index_price": index,
         "mark_price": price if mark is None else mark}
    d.update(extra)
    return d


def utc_date(ts_ms):
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts_ms / 1000.0, _dt.timezone.utc).strftime("%Y-%m-%d")


def write_shards(trades_dir, trades, sort=True):
    """Group trades by UTC day into <trades_dir>/YYYY-MM-DD.jsonl.gz (one JSON per line, like the collector)."""
    import json
    trades_dir = Path(trades_dir)
    trades_dir.mkdir(parents=True, exist_ok=True)
    by_day = {}
    for t in (sorted(trades, key=lambda x: x["timestamp"]) if sort else trades):
        by_day.setdefault(utc_date(t["timestamp"]), []).append(t)
    for day, rows in by_day.items():
        with gzip.open(trades_dir / (day + ".jsonl.gz"), "wt", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return sorted(by_day)


def write_csv(path, header, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def write_delivery(hist_dir, prices):
    """prices: {'YYYY-MM-DD': price}. ts_ms = 00:00 UTC of the date (collector convention)."""
    rows = []
    for date in sorted(prices):
        y, m, d = (int(x) for x in date.split("-"))
        rows.append((ms(y, m, d), date, prices[date]))
    write_csv(Path(hist_dir) / "delivery_prices.csv", ("ts_ms", "date", "delivery_price"), rows)
