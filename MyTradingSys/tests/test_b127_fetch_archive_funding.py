"""B127 B103-F2: fetch_binance_archive funding path. Expected URL/plan values come from the data.binance.vision layout
(futures/um/<period>/fundingRate/BTCUSDT/BTCUSDT-fundingRate-<stamp>.zip, monthly files only), not from the module."""
import hashlib
import io
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtest"))
import fetch_binance_archive as fba  # noqa: E402


def test_funding_url_is_monthly_layout():
    assert fba._url("fundingRate", "monthly", "2020-01") == (
        "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip")


def test_funding_plan_is_monthly_even_for_partial_months():
    jobs = fba.plan("fundingRate", date(2020, 1, 1), date(2020, 3, 15))
    assert jobs == [("monthly", "2020-01"), ("monthly", "2020-02"), ("monthly", "2020-03")]


def test_klines_plan_uses_daily_for_partial_month_edges():
    jobs = fba.plan("klines", date(2020, 1, 30), date(2020, 2, 1))
    assert jobs == [("daily", "2020-01-30"), ("daily", "2020-01-31"), ("daily", "2020-02-01")]


def _zip_bytes(name, text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, text)
    return buf.getvalue()


def test_fetch_one_extracts_when_checksum_matches(tmp_path, monkeypatch):
    csv_name = "BTCUSDT-fundingRate-2020-01.csv"
    blob = _zip_bytes(csv_name, "calc_time,funding_interval_hours,last_funding_rate" + chr(10) + "1,8,0.0001" + chr(10))
    digest = hashlib.sha256(blob).hexdigest()
    monkeypatch.setattr(fba, "_get", lambda url, retries=3: (blob if url.endswith(".zip") else f"{digest}  x.zip".encode()))
    assert fba.fetch_one("fundingRate", "monthly", "2020-01", tmp_path) == "ok"
    assert (tmp_path / csv_name).exists()
    assert fba.fetch_one("fundingRate", "monthly", "2020-01", tmp_path) == "skip"


def test_fetch_one_rejects_checksum_mismatch_and_writes_nothing(tmp_path, monkeypatch):
    blob = _zip_bytes("BTCUSDT-fundingRate-2020-01.csv", "x" + chr(10))
    monkeypatch.setattr(fba, "_get", lambda url, retries=3: (blob if url.endswith(".zip") else b"0" * 64 + b"  x.zip"))
    with pytest.raises(RuntimeError, match="CHECKSUM MISMATCH"):
        fba.fetch_one("fundingRate", "monthly", "2020-01", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_fetch_one_404_is_reported_not_raised(tmp_path, monkeypatch):
    monkeypatch.setattr(fba, "_get", lambda url, retries=3: None)
    assert fba.fetch_one("fundingRate", "monthly", "2019-01", tmp_path) == "404"
