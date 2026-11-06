"""Spec tests (no network) for backtest/fetch_binance_archive.py spot-history parsing and
research/klines_history_2017/regime_mix_long.py RSI series alignment. Expected values hand-derived."""
import hashlib, io, sys, zipfile
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "MyTradingSys" / "research" / "klines_history_2017"))

from MyTradingSys.backtest import fetch_binance_archive as fba  # noqa: E402
import regime_mix_long as rml  # noqa: E402

H = 3600000


def row(t, c="1.0"):
    return f"{t},1.0,2.0,0.5,{c},10.0,0,0,0,0,0,0"


def test_parse_header_skipped_and_counts():
    txt = "open_time,o,h,l,c,v\n" + "\n".join(row(k * H) for k in range(3)) + "\n"
    p = fba.parse_kline_csv(txt, H)
    assert (p["rows"], p["first_t"], p["last_t"], p["gaps"]) == (3, 0, 2 * H, [])


def test_parse_microsecond_normalised_to_ms():
    t_ms = 1_700_000_000_000
    p = fba.parse_kline_csv(row(t_ms * 1000) + "\n" + row((t_ms + H) * 1000), H)
    assert p["first_t"] == t_ms and p["last_t"] == t_ms + H
    # 10**14 boundary: exactly 10**14 is still milliseconds (guard is >)
    assert fba.parse_kline_csv(row(10 ** 14), H)["first_t"] == 10 ** 14


def test_parse_gap_detected_and_exact_bar_not_gap():
    p = fba.parse_kline_csv(row(0) + "\n" + row(H) + "\n" + row(3 * H), H)
    assert p["gaps"] == [(H, 3 * H)]


@pytest.mark.parametrize("txt", [row(5) + "\n" + row(5), row(5) + "\n" + row(4)])
def test_parse_duplicate_or_decreasing_rejected(txt):
    with pytest.raises(ValueError, match="not increasing"):
        fba.parse_kline_csv(txt, H)


def test_parse_bad_rows_and_empty():
    with pytest.raises(ValueError, match="<6 columns"):
        fba.parse_kline_csv("1,2,3,4,5", H)
    with pytest.raises(ValueError, match="bad row"):
        fba.parse_kline_csv("1,a,2,3,4,5", H)
    with pytest.raises(ValueError, match="empty"):
        fba.parse_kline_csv("header\n\n", H)


def test_spot_months_and_estimate():
    assert fba.spot_months(date(2017, 11, 5), date(2018, 2, 1)) == ["2017-11", "2017-12", "2018-01", "2018-02"]
    # 1 symbol x 2 months x 1d (0.02MB) /1024
    assert fba.estimate_gb(["X"], ["1d"], date(2020, 1, 1), date(2020, 2, 28)) == pytest.approx(2 * 0.02 / 1024)


def _zip(text, names=("a.csv",)):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n in names:
            z.writestr(n, text)
    return b.getvalue()


def _getter(blob, chk):
    def get(url):
        return blob if not url.endswith(".CHECKSUM") else chk
    return get


def test_fetch_ok_writes_csv_manifest_then_skip(tmp_path):
    blob = _zip(row(0) + "\n" + row(H) + "\n")
    chk = (hashlib.sha256(blob).hexdigest() + "  x.zip").encode()
    assert fba.fetch_spot_month("BTCUSDT", "1h", "2020-01", tmp_path, _getter(blob, chk)) == "ok"
    assert (tmp_path / "BTCUSDT/1h/klines/BTCUSDT-1h-2020-01.csv").exists()
    m = fba.load_manifest(tmp_path)["BTCUSDT/1h/2020-01"]
    assert m["rows"] == 2 and m["sha256"] == hashlib.sha256(blob).hexdigest()
    boom = lambda u: (_ for _ in ()).throw(AssertionError("network"))
    assert fba.fetch_spot_month("BTCUSDT", "1h", "2020-01", tmp_path, boom) == "skip"


def test_fetch_checksum_mismatch_writes_nothing(tmp_path):
    blob = _zip(row(0))
    with pytest.raises(fba.ChecksumMismatch):
        fba.fetch_spot_month("BTCUSDT", "1h", "2020-01", tmp_path, _getter(blob, b"0" * 64))
    assert not (tmp_path / "BTCUSDT").exists() and fba.load_manifest(tmp_path) == {}


def test_fetch_404_nochecksum_and_multi_member(tmp_path):
    assert fba.fetch_spot_month("B", "1h", "2020-01", tmp_path, lambda u: None) == "404"
    blob = _zip(row(0))
    assert fba.fetch_spot_month("B", "1h", "2020-01", tmp_path, lambda u: None if u.endswith("CHECKSUM") else blob) == "nochecksum"
    two = _zip(row(0), ("a.csv", "b.csv"))
    chk = hashlib.sha256(two).hexdigest().encode()
    with pytest.raises(ValueError, match="expected 1 member"):
        fba.fetch_spot_month("B", "1h", "2020-01", tmp_path, _getter(two, chk))


def test_fetch_history_tally_daily_and_monthly(tmp_path):
    calls = []
    def get(u):
        calls.append(u)
        return None
    t = fba.fetch_spot_history(["B"], ["1d"], date(2020, 1, 30), date(2020, 2, 1), tmp_path, get=get, sleep_s=0, daily=True)
    assert t == {"404": 3}
    assert "/daily/klines/B/1d/B-1d-2020-01-31.zip" in calls[1]
    t = fba.fetch_spot_history(["B", "C"], ["1d"], date(2020, 1, 1), date(2020, 2, 1), tmp_path, get=get, sleep_s=0)
    assert t == {"404": 4}


def test_plan_full_month_monthly_edges_daily():
    jobs = fba.plan("klines", date(2020, 1, 30), date(2020, 3, 31))
    assert jobs == [("daily", "2020-01-30"), ("daily", "2020-01-31"), ("monthly", "2020-02"), ("monthly", "2020-03")]
    assert fba.plan("metrics", date(2020, 2, 1), date(2020, 2, 2)) == [("daily", "2020-02-01"), ("daily", "2020-02-02")]


# ---- regime_mix_long ----
def test_ms_is_utc_epoch():
    assert rml.ms("1970-01-02") == 86400000
    assert rml.ms("2017-08-21") == 1503273600000


def test_rsi_series_alignment_monotone_rising():
    bars = [{"t": k * rml.DAY, "c": 100.0 + k} for k in range(20)]
    ts, rs = rml.rsi_series(bars)
    # RSI defined from index 14; stamped at the NEXT bar open (close time); last bar dropped
    assert ts == [k * rml.DAY for k in range(15, 20)]
    assert rs == [100.0] * 5


def test_rsi_series_flat_is_50_and_falling_is_0():
    flat = [{"t": k, "c": 5.0} for k in range(17)]
    assert set(rml.rsi_series(flat)[1]) == {50.0}
    fall = [{"t": k, "c": 100.0 - k} for k in range(17)]
    assert set(rml.rsi_series(fall)[1]) == {0.0}
