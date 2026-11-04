"""Tests for layer_state.py (WaveTrend pilot). Offline: fixture = 1000 BTCUSDT 3m bars ending 2026-11-04 13:42Z.
Expected values are derived INDEPENDENTLY of wavetrend.py: pandas ewm/rolling recursion of FORMULAS.md s20.1 and the
Bible's dot rule, plus the 11-04 operator case. Run: python -m pytest scripts/dev/test_layer_state.py -q
"""
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layer_state as L

FIX = L.ROOT / "MyTradingSys" / "research" / "layer_bible" / "fixtures" / "fixture_btcusdt_3m_2026-11-04.csv"
P = {"family": "wavetrend", "symbol": "BTCUSDT", "source": "t", "tfs": ["3m"], "bars": 1000, "dot_band": 53,
     "dot_basis": "prev_bar"}
TF = 180000


def at(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


@pytest.fixture(scope="module")
def bars():
    return L.read_csv(FIX)


def pandas_dots(bars_, band=53.0, warm=200):
    """FORMULAS s20.1 via pandas (adjust=False == seed with the first value), cross 'le', prior-bar dot rule."""
    df = pd.DataFrame(bars_, columns=["t", "h", "l", "c"])
    ap = (df.h + df.l + df.c) / 3
    esa = ap.ewm(alpha=2 / 11, adjust=False).mean()
    d = (ap - esa).abs().ewm(alpha=2 / 11, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    wt1 = ci.ewm(alpha=2 / 22, adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    side = np.sign(wt1 - wt2).to_numpy()
    out, last = [], 0
    for i in range(len(df)):
        s = side[i]
        if i < warm or np.isnan(wt2.iloc[i]):
            continue
        if s != 0:
            if last != 0 and s != last:
                prev = wt1.iloc[i - 1]
                if (s > 0 and prev <= -band) or (s < 0 and prev >= band):
                    out.append((L.iso(int(df.t.iloc[i])), "bottom" if s > 0 else "top"))
            last = s
    return out


def test_1104_case_completed_cycle_and_invalid_1221(bars):
    st = L.wavetrend_state(bars, TF, P, at("2026-11-04T12:30Z"))
    assert st["status"] == "OK"
    assert st["last_cross"]["time"] == "2026-11-04T12:21Z" and st["last_cross"]["kind"] == "up"
    assert st["last_cross"]["valid_dot"] is False                       # -49.3 is not a valid bottom dot (OURS band rule)
    assert st["last_valid_dot"]["dot"] == "top" and st["last_valid_dot"]["time"] == "2026-11-04T11:39Z"
    cy = st["cycle"]
    assert cy["state"] == "COMPLETED_UP_CYCLE"
    assert cy["start"] == "2026-11-04T03:12Z" and cy["end"] == "2026-11-04T11:39Z"
    assert cy["tops_since_start"][-1] == "2026-11-04T11:39Z" and len(cy["tops_since_start"]) >= 2


def test_open_cycle_right_after_bottom_dot(bars):
    st = L.wavetrend_state(bars, TF, P, at("2026-11-04T03:30Z"))
    assert st["cycle"]["state"] == "OPEN_UP_CYCLE" and st["cycle"]["start"] == "2026-11-04T03:12Z"


def test_dots_match_independent_pandas_derivation(bars):
    want = pandas_dots(bars)
    st = L.wavetrend_state(bars, TF, P)
    # the runtime's last valid dot must equal the independent derivation's last dot
    assert st["last_valid_dot"]["time"] == want[-1][0] and st["last_valid_dot"]["dot"] == want[-1][1]
    assert want and ("2026-11-04T03:12Z", "bottom") in want and ("2026-11-04T11:39Z", "top") in want
    assert ("2026-11-04T12:21Z", "bottom") not in want


def test_closed_bars_only(bars):
    # bar 12:21 closes 12:24; at 12:22 it is still open and must not be used
    st = L.wavetrend_state(bars, TF, P, at("2026-11-04T12:22Z"))
    assert st["last_bar"] == "2026-11-04T12:18Z" and st["last_cross"]["time"] != "2026-11-04T12:21Z"


def test_deterministic(bars):
    a = L.wavetrend_state(bars, TF, P, at("2026-11-04T12:30Z"))
    assert a == L.wavetrend_state(list(bars), TF, P, at("2026-11-04T12:30Z"))


def test_short_data_is_not_in_data_never_a_guess(bars):
    st = L.wavetrend_state(bars[:150], TF, P)
    assert st["status"] == "NOT_IN_DATA"
    assert "NOT_IN_DATA" in L.line("wavetrend", "BTCUSDT", "3m", st)


def test_dot_band_param_is_read_not_hardcoded(bars):
    loose = dict(P, dot_band=45)
    st = L.wavetrend_state(bars, TF, loose, at("2026-11-04T12:30Z"))
    assert st["last_cross"]["valid_dot"] is True                           # prior bar -50.9 passes a 45 band


def test_bible_has_exactly_one_param_block_and_parses():
    p = L.load_params("wavetrend")
    assert p["dot_band"] == 53 and "3m" in p["tfs"] and p["dot_basis"] == "prev_bar"


def test_missing_param_block_fails_closed(tmp_path):
    (tmp_path / "x.md").write_text("no block here")
    with pytest.raises(SystemExit):
        L.load_params("x", tmp_path)


def test_cli_offline_prints_stamp_and_1104_line(capsys):
    L.main(["wavetrend", "--tf", "3m", "--csv", str(FIX), "--at", "2026-11-04T12:30Z"])
    out = capsys.readouterr().out
    assert "NOT a valid dot" in out and "COMPLETED bottom 2026-11-04T03:12Z" in out and "STAMP bible=wavetrend.md@" in out


def test_fixture_is_pinned():
    import hashlib
    assert hashlib.sha256(FIX.read_bytes()).hexdigest() == "abb8d293499981aaf799f71566b66d82e70e14165225caf579cfa5e12e883350"
