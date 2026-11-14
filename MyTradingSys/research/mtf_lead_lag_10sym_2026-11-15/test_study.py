"""Tests for mtf_lead_lag_10sym study helpers (sign, look-forward only, hit window)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S  # noqa: E402


def _bars(n):
    return [{"t": i * 3600000, "h": 0, "l": 0, "c": 100.0 + i} for i in range(n)]


def test_fwd_ret_sign_and_horizon():
    b = _bars(200)
    ts = [x["t"] + 3600000 for x in b]
    t = ts[10]
    up = S.fwd_ret(b, ts, t, "BULL", 3)
    assert abs(up - (b[10 + 72]["c"] / b[10]["c"] - 1)) < 1e-12
    assert S.fwd_ret(b, ts, t, "BEAR", 3) == -up
    assert S.fwd_ret(b, ts, ts[150], "BULL", 3) is None       # no full window: dropped, never padded


def test_hit_same_direction_within_week_only():
    d_f = [(1000, "BEAR"), (2000 + S.WEEK, "BULL"), (500 + S.WEEK, "BULL")]
    d_f.sort()
    d_ts = [x[0] for x in d_f]
    assert S.hit(500, "BULL", d_ts, d_f) == 1                  # 500+WEEK is within t + WEEK
    assert S.hit(500, "BEAR", d_ts, d_f) == 1
    assert S.hit(1500, "BEAR", d_ts, d_f) == 0                 # the BEAR flip at 1000 is before t: never counts


def test_cost_is_research_kit():
    assert S.rk.TAKER_RT_PCT == 0.14
