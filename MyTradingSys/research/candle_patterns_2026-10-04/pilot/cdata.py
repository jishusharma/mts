# T01-F2: raw_1d is a distinct snapshot, NOT the 1m resample (905 of 912 DEV days differ on open, 847 on volume, max 12.01%); derive daily bars from 1m for new work. See MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md
"""Pilot data layer. Stdlib only. Reuses backtest/bt/bt_data.py loaders (raw archive CSVs).

DEV-only guard (PRE_REG_CANDLE_PILOT.md section 1): every loader refuses an end date after DEV_END_MS
unless the caller passes `unseal=True`, which the pilot scripts never do.
Bars are dicts {t,o,h,l,c,v,tbv}, t = open time epoch ms (UTC).
"""
import sys
sys.dont_write_bytecode = True
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # repo root
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "bt"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest"))
import bt_data  # noqa: E402

RAW = ROOT / "Dumps" / "backtest"
DAY = 86400000
HOUR = 3600000


def ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


DAILY_START_MS = ms(2020, 1, 1)
DEV_END_MS = ms(2024, 7, 1)          # exclusive: DEV is < 2024-07-01
HOURLY_START_MS = ms(2022, 1, 1)
VALID_END_MS = ms(2025, 7, 1)        # exclusive: VALIDATION is [2024-07-01, 2025-07-01)


def _guard(end_ms, unseal):
    if end_ms is None or end_ms > DEV_END_MS:
        if not unseal:
            raise PermissionError("pilot is DEV-only: end_ms must be <= DEV_END_MS (PRE_REG section 1)")


def load_daily(start_ms=DAILY_START_MS, end_ms=DEV_END_MS, unseal=False):
    _guard(end_ms, unseal)
    bars = bt_data.load_klines(RAW / "raw_1d", "klines", start_ms, end_ms)
    return bars


def load_1m(start_ms, end_ms, unseal=False):
    """1m bars from raw_1m_2022 (2022-01..2025-08) then raw (2025-09..)."""
    _guard(end_ms, unseal)
    a = bt_data.load_klines(RAW / "raw_1m_2022", "klines", start_ms, end_ms)
    b = bt_data.load_klines(RAW / "raw", "klines", start_ms, end_ms)
    seen = {x["t"] for x in a}
    return a + [x for x in b if x["t"] not in seen]


def resample_offset(bars_1m, tf_min, offset_min=0):
    """Closed, complete buckets only. Bucket start = floor((t - off)/tf)*tf + off. Returns bars + count of dropped partial buckets."""
    tf_ms, off = tf_min * 60000, offset_min * 60000
    out, cur, cur_start, dropped = [], [], None, 0
    for b in bars_1m:
        s = ((b["t"] - off) // tf_ms) * tf_ms + off
        if s != cur_start:
            if cur:
                if len(cur) == tf_min:
                    out.append(_agg(cur_start, cur))
                else:
                    dropped += 1
            cur, cur_start = [], s
        cur.append(b)
    if cur and len(cur) == tf_min:
        out.append(_agg(cur_start, cur))
    elif cur:
        dropped += 1
    return out, dropped


def _agg(start, bs):
    return {"t": start, "o": bs[0]["o"], "h": max(x["h"] for x in bs), "l": min(x["l"] for x in bs),
            "c": bs[-1]["c"], "v": sum(x["v"] for x in bs), "tbv": sum(x["tbv"] for x in bs)}


class Funding:
    """8h funding settlements (00/08/16 UTC) from the archive."""

    def __init__(self, rows=None):
        self.rows = rows if rows is not None else bt_data.load_funding(RAW / "raw")
        self.times = [t for t, _ in self.rows]

    def sum(self, t0, t1):
        """Sum of rates settled in (t0, t1]. A long pays it, a short receives it."""
        import bisect
        i, j = bisect.bisect_right(self.times, t0), bisect.bisect_right(self.times, t1)
        return sum(r for _, r in self.rows[i:j])


def contiguous(bars, step_ms):
    """Return list of gap positions (index i where bars[i].t - bars[i-1].t != step)."""
    return [i for i in range(1, len(bars)) if bars[i]["t"] - bars[i - 1]["t"] != step_ms]
