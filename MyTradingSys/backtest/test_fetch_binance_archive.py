"""Spot-history extension of fetch_binance_archive: offline fixtures only (no network). Expectations are hand arithmetic."""
import hashlib
import io
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest import fetch_binance_archive as F  # noqa: E402

H = 3600000
T0 = 1502928000000  # 2017-08-17 00:00 UTC = 1502928000 s


def csv_rows(n, t0=T0, step=H, micro=False):
    # open,high,low,close,vol,close_time,quote,trades,tbv,tbq,ignore ; row k open = t0 + k*step
    rows = []
    for k in range(n):
        t = t0 + k * step
        t = t * 1000 if micro else t
        rows.append(f"{t},1.0,2.0,0.5,1.5,10,{t + step - 1},15,3,5,6,0")
    return "\n".join(rows) + "\n"


def make_zip(name, text):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, text)
    return b.getvalue()


class FakeNet:
    def __init__(self, files, bad_checksum=()):
        self.files, self.bad, self.calls = files, set(bad_checksum), []

    def __call__(self, url):
        self.calls.append(url)
        if url.endswith(".CHECKSUM"):
            z = self.files.get(url[:-9])
            if z is None:
                return None
            h = "0" * 64 if url[:-9] in self.bad else hashlib.sha256(z).hexdigest()
            return f"{h}  {url.rsplit('/', 1)[1][:-9]}\n".encode()
        return self.files.get(url)


def url_of(sym, tf, stamp, period="monthly"):
    return f"{F.SPOT_BASE}/{period}/klines/{sym}/{tf}/{sym}-{tf}-{stamp}.zip"


def test_parse_kline_csv_counts_and_gaps():
    # 4 rows 1h apart, then a jump of 3h: 5 rows, 1 gap; first/last open as written
    text = csv_rows(4) + csv_rows(1, t0=T0 + 7 * H)
    p = F.parse_kline_csv(text, H)
    assert p["rows"] == 5 and p["first_t"] == T0 and p["last_t"] == T0 + 7 * H
    assert p["gaps"] == [(T0 + 3 * H, T0 + 7 * H)]


def test_parse_kline_csv_microseconds_and_header():
    p = F.parse_kline_csv("open_time,o,h,l,c,v\n" + csv_rows(2, micro=True), H)
    assert p["rows"] == 2 and p["first_t"] == T0 and p["gaps"] == []


def test_parse_rejects_out_of_order_and_bad_rows():
    with pytest.raises(ValueError):
        F.parse_kline_csv(csv_rows(2) + csv_rows(1), H)  # third row repeats the first open time
    with pytest.raises(ValueError):
        F.parse_kline_csv("1,2,3\n", H)


def test_two_day_slice_download_and_manifest(tmp_path):
    # 2 days of 1h bars = 48 rows, daily archive files
    files = {url_of("BTCUSDT", "1h", d, "daily"): make_zip(f"BTCUSDT-1h-{d}.csv", csv_rows(24, T0 + i * 24 * H))
             for i, d in enumerate(["2017-08-17", "2017-08-18"])}
    net = FakeNet(files)
    res = F.fetch_spot_history(["BTCUSDT"], ["1h"], date(2017, 8, 17), date(2017, 8, 18), tmp_path, get=net, sleep_s=0, daily=True)
    assert res == {"ok": 2}
    out = tmp_path / "BTCUSDT" / "1h" / "klines"
    assert sorted(p.name for p in out.glob("*.csv")) == ["BTCUSDT-1h-2017-08-17.csv", "BTCUSDT-1h-2017-08-18.csv"]
    man = json.loads((tmp_path / "manifest.json").read_text())
    ent = man["BTCUSDT/1h/2017-08-17"]
    assert ent["rows"] == 24 and ent["sha256"] == hashlib.sha256(files[url_of("BTCUSDT", "1h", "2017-08-17", "daily")]).hexdigest()
    assert sum(v["rows"] for v in man.values()) == 48


def test_resume_skips_existing(tmp_path):
    u = url_of("ETHUSDT", "4h", "2017-08")
    net = FakeNet({u: make_zip("ETHUSDT-4h-2017-08.csv", csv_rows(6, step=4 * H))})
    args = (["ETHUSDT"], ["4h"], date(2017, 8, 1), date(2017, 8, 31), tmp_path)
    assert F.fetch_spot_history(*args, get=net, sleep_s=0) == {"ok": 1}
    n = len(net.calls)
    assert F.fetch_spot_history(*args, get=net, sleep_s=0) == {"skip": 1}
    assert len(net.calls) == n  # nothing fetched the second time


def test_checksum_mismatch_rejected_nothing_written(tmp_path):
    u = url_of("BTCUSDT", "1d", "2017-08")
    net = FakeNet({u: make_zip("BTCUSDT-1d-2017-08.csv", csv_rows(3, step=24 * H))}, bad_checksum=[u])
    with pytest.raises(F.ChecksumMismatch):
        F.fetch_spot_month("BTCUSDT", "1d", "2017-08", tmp_path, net)
    assert not list(tmp_path.rglob("*.csv"))
    assert not (tmp_path / "manifest.json").exists() or json.loads((tmp_path / "manifest.json").read_text()) == {}


def test_404_recorded_not_fatal(tmp_path):
    res = F.fetch_spot_history(["ETHUSDT"], ["1h"], date(2017, 1, 1), date(2017, 2, 28), tmp_path, get=FakeNet({}), sleep_s=0)
    assert res == {"404": 2}


def test_spot_months_inclusive():
    assert F.spot_months(date(2017, 8, 1), date(2017, 10, 20)) == ["2017-08", "2017-09", "2017-10"]


def test_estimate_gb_small_and_guard():
    assert F.estimate_gb(["BTCUSDT", "ETHUSDT"], ["15m", "1d"], date(2017, 8, 1), date(2026, 10, 31)) < 15
