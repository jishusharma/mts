"""run_1h4h.py: hand-derived outcome labels (PRE_REG.md Outcome) and the DEV-cut guard (PRE_REG_1H4H.md E1)."""
import datetime as dt
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_1h4h as R  # noqa: E402
import candidates as C  # noqa: E402

H0 = int(dt.datetime(2024, 6, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def _bars(t0=H0, step=3_600_000):
    ohlc = [(100, 101, 99, 100), (100, 105, 95, 102), (102, 111, 98, 108),
            (108, 109, 100, 105), (105, 106, 101, 103), (103, 104, 97, 99)]
    return [{"t": t0 + k * step, "close_ms": t0 + (k + 1) * step, "o": o, "h": h, "l": l, "c": c, "v": 1.0, "tb": 0.5}
            for k, (o, h, l, c) in enumerate(ohlc)]


# Hand derivation, k = 1, H = 3, entry E = open of bar i+1:
# i0 BOTTOM a10: E 100, up 110 / dn 90; bar1 h105 l95, bar2 h111 -> HIT
# i0 TOP    a10: rev 90 / cont 110; bar2 h111 hits cont first -> MISS
# i0 BOTTOM a2:  E 100, up 102 / dn 98; bar1 h105 and l95 hit both -> AMBIGUOUS
# i1 BOTTOM a10: E 102, up 112 / dn 92; bars 2-4 highs 111,109,106 lows 98,100,101 -> TIMEOUT
# i2 TOP    a10: E 108, rev 98 / cont 118; bars 3-5 lows 100,101,97 -> HIT at bar 5
# i3 BOTTOM a10: i + H = 6 > last index 5 -> CENSORED
@pytest.mark.parametrize("i,a,side,want", [
    (0, 10, "BOTTOM", "HIT"), (0, 10, "TOP", "MISS"), (0, 2, "BOTTOM", "AMBIGUOUS"),
    (1, 10, "BOTTOM", "TIMEOUT"), (2, 10, "TOP", "HIT"), (3, 10, "BOTTOM", "CENSORED")])
def test_hand_labels(i, a, side, want):
    assert R.label(_bars(), i, a, side, H=3) == want


def test_refuses_bar_at_or_after_dev_cut():
    bars = _bars(t0=R.T_END - 5 * 3_600_000)  # last bar opens exactly at 2024-07-01
    with pytest.raises(ValueError):
        R.label(bars, 0, 10, "BOTTOM", H=3)


def test_loader_never_returns_a_dev_cut_row(tmp_path):
    f = tmp_path / "k.csv"
    rows = [R.T_END - 60_000, R.T_END, R.T_END + 60_000]
    f.write_text("open_time,o,h,l,c,v,ct,qv,n,tb,tbq,i\n" + "".join(
        f"{t},1,2,0.5,1.5,10,{t + 59999},0,0,4,0,0\n" for t in rows), encoding="utf-8")
    got = R.load_1m([f])
    assert [r["t"] for r in got] == [R.T_END - 60_000]


def test_context_lookback_is_4_bars():
    assert C.TF_BARS_4H[60] == 4 and C.TF_BARS_4H[240] == 4
