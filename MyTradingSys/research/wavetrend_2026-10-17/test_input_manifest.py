import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import input_manifest as im  # noqa: E402


def _write(d, name, times, extra="1,2,3,4,5"):
    p = Path(d) / name
    with open(p, "w", newline="\n") as fh:
        fh.write("open_time,o,h,l,c,v\n")
        for t in times:
            fh.write(f"{t},{extra}\n")
    return p


def _jan(n, skip=(), dup=()):
    lo, _ = im._month_bounds_ms("2022-01")
    ts = [lo + i * im.MS for i in range(n) if i not in skip]
    return ts + [lo + i * im.MS for i in dup]


def test_digest_and_size(tmp_path):
    p = _write(tmp_path, "BTCUSDT-1m-2022-01.csv", _jan(5))
    e, _ = im.scan_file(p)
    assert e["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()
    assert e["size"] == p.stat().st_size and e["rows"] == 5


def test_duplicates_and_missing(tmp_path):
    p = _write(tmp_path, "BTCUSDT-1m-2022-01.csv", _jan(10, skip=(3, 4), dup=(0, 1, 1)))
    e, idx = im.scan_file(p)
    assert e["duplicate_rows"] == 3
    assert e["unique_minutes"] == 8
    assert e["expected_minutes"] == 31 * 1440
    assert e["missing_minutes"] == 31 * 1440 - 8
    assert idx == {0, 1, 2, 5, 6, 7, 8, 9}


def test_cutoff_refused_by_name_before_read(tmp_path):
    p = tmp_path / "BTCUSDT-1m-2024-07.csv"      # never created: must refuse without opening
    with pytest.raises(im.CutoffRefusal):
        im.build_manifest([p])


def test_cutoff_refused_by_timestamp(tmp_path):
    p = _write(tmp_path, "BTCUSDT-1m-2024-06.csv", [im.CUTOFF_MS])
    with pytest.raises(im.CutoffRefusal):
        im.scan_file(p)


def test_usable_bars_hand_count():
    # grid of 10 minutes, minute 7 missing: 5m bucket [0-4] complete, [5-9] lost
    out = im.usable_bars(set(range(10)) - {7}, 10)
    assert out["5m"] == 1 and out["15m"] == 0
    assert im.usable_bars(set(range(1440)), 1440) == {"5m": 288, "15m": 96, "1h": 24, "4h": 6, "1d": 1}


def test_non_time_columns_not_parsed(tmp_path):
    p = _write(tmp_path, "BTCUSDT-1m-2022-01.csv", _jan(3), extra="x,y,z,w,v")
    e, _ = im.scan_file(p)
    assert e["rows"] == 3
