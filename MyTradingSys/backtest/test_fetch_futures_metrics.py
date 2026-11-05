import hashlib, io, sys, zipfile
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_futures_metrics as ffm  # noqa: E402

HEADER = "create_time,symbol,sum_open_interest,sum_open_interest_value\n"


def _zip(name, rows):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, HEADER + "".join(f"2024-01-01 00:00:00,BTCUSDT,{i},{i}\n" for i in range(rows)))
    return buf.getvalue()


class FakeArchive:
    """Serves 2024-01-01..03 (03 short: 10 rows); 2024-01-04 and 2024-02-01 are 404."""

    def __init__(self):
        self.files, self.calls = {}, 0
        for d, rows in (("2024-01-01", 288), ("2024-01-02", 288), ("2024-01-03", 10), ("2024-01-05", 288)):
            url = f"{ffm.BASE}/BTCUSDT/BTCUSDT-metrics-{d}.zip"
            blob = _zip(f"BTCUSDT-metrics-{d}.csv", rows)
            self.files[url] = blob
            self.files[url + ".CHECKSUM"] = f"{hashlib.sha256(blob).hexdigest()}  x.zip".encode()

    def __call__(self, url):
        self.calls += 1
        return self.files.get(url)


def test_gap_listing_per_month(tmp_path):
    fake = FakeArchive()
    counts = ffm.run(["BTCUSDT"], date(2024, 1, 1), date(2024, 2, 1), tmp_path, get=fake)
    assert counts["BTCUSDT"] == {"ok": 4, "404": 28}
    gaps = ffm.list_gaps("BTCUSDT", tmp_path, date(2024, 1, 1), date(2024, 2, 1))
    assert gaps["2024-01"]["expected"] == 31 and gaps["2024-01"]["present"] == 4
    assert gaps["2024-01"]["missing"][0] == "2024-01-04"
    assert gaps["2024-01"]["short"] == {"2024-01-03": 10}
    assert gaps["2024-02"] == {"expected": 1, "present": 0, "missing": ["2024-02-01"], "short": {}}
    assert "TOTAL days=32 missing=28 short=1" in ffm.format_gaps("BTCUSDT", gaps)


def test_rerun_is_idempotent(tmp_path):
    fake = FakeArchive()
    ffm.run(["BTCUSDT"], date(2024, 1, 1), date(2024, 1, 3), tmp_path, get=fake)
    before = {p.name: p.read_bytes() for p in (tmp_path / "BTCUSDT").iterdir()}
    calls = fake.calls
    counts = ffm.run(["BTCUSDT"], date(2024, 1, 1), date(2024, 1, 3), tmp_path, get=fake)
    assert counts["BTCUSDT"] == {"skip": 3}
    assert fake.calls == calls
    assert {p.name: p.read_bytes() for p in (tmp_path / "BTCUSDT").iterdir()} == before


def test_checksum_mismatch_fails_closed(tmp_path):
    fake = FakeArchive()
    url = f"{ffm.BASE}/BTCUSDT/BTCUSDT-metrics-2024-01-01.zip"
    fake.files[url + ".CHECKSUM"] = b"0" * 64
    with pytest.raises(RuntimeError):
        ffm.fetch_day("BTCUSDT", date(2024, 1, 1), tmp_path, get=fake)
    assert not (tmp_path / "BTCUSDT" / "BTCUSDT-metrics-2024-01-01.csv").exists()


def test_root_from_env_never_hardcoded():
    assert ffm.resolve_root(env={"MTS_METRICS_ROOT": "X:/m"}) == Path("X:/m")
    assert ffm.resolve_root(env={"MTS_DATA_ROOT": "X:/d"}) == Path("X:/d") / "metrics"
    with pytest.raises(SystemExit):
        ffm.resolve_root(env={})
