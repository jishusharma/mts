"""Instrument-name parsing, date helpers, delivery-price loader."""
import csv
import datetime
import os
import re
import sys
from collections import namedtuple
from functools import lru_cache

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from bs import payoff_btc  # noqa: E402,F401  (re-export)

DAY_MS = 86400000
HOUR_MS = 3600000
EXPIRY_HOUR_MS = 8 * HOUR_MS

MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}

_NAME_RE = re.compile(r"^([A-Z]+)-(\d{1,2})([A-Z]{3})(\d{2})-(\d+(?:[.d]\d+)?)-([CP])$")
_EPOCH = datetime.date(1970, 1, 1)

Instrument = namedtuple(
    "Instrument", ["name", "underlying", "expiry_ms", "expiry_date", "strike", "is_call", "expiry_weekday"])


def ymd_to_ms(date_str):
    """'YYYY-MM-DD' -> ms at 00:00 UTC."""
    d = datetime.date.fromisoformat(date_str)
    return (d - _EPOCH).days * DAY_MS


def ms_to_ymd(ms):
    return (_EPOCH + datetime.timedelta(days=int(ms // DAY_MS))).isoformat()


def weekday_of_ms(ms):
    """UTC weekday of an epoch-ms instant, Monday=0 .. Sunday=6."""
    return (_EPOCH + datetime.timedelta(days=int(ms // DAY_MS))).weekday()


@lru_cache(maxsize=None)
def parse_instrument(name):
    """BTC-9OCT26-86000-P -> Instrument, or None when the name is not an option name."""
    m = _NAME_RE.match(name) if isinstance(name, str) else None
    if not m:
        return None
    und, dd, mon, yy, strike, cp = m.groups()
    month = MONTHS.get(mon)
    if month is None:
        return None
    try:
        d = datetime.date(2000 + int(yy), month, int(dd))
    except ValueError:
        return None
    expiry_ms = (d - _EPOCH).days * DAY_MS + EXPIRY_HOUR_MS
    return Instrument(name, und, expiry_ms, d.isoformat(), float(strike.replace("d", ".")), cp == "C", d.weekday())


def load_delivery_prices(path):
    """delivery_prices.csv (ts_ms,date,delivery_price) -> {date_str: float}. Missing file -> {}."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, "r", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                out[row["date"]] = float(row["delivery_price"])
            except (KeyError, TypeError, ValueError):
                continue
    return out
